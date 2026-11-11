#!/usr/bin/env python3
"""GitHub repo discovery: trending (day/week/month), top-starred, task search, verification.

Stdlib only. Usage:
  scout.py trending --since daily|weekly|monthly [--language python] [--limit 10] [--verify]
  scout.py top      [--query "topic:llm"] [--language rust] [--limit 10] [--verify]
  scout.py find     "pdf table extraction" [--language python] [--min-stars 100] [--limit 10] [--verify]
  scout.py verify   owner/repo [owner/repo ...]
Common flags: --json (machine output), --no-auth (ignore tokens; 10 search / 60 core calls per hour).

Auth: uses $GITHUB_TOKEN or $GH_TOKEN if set, else `gh auth token` if gh is logged in,
unless --no-auth. All calls are read-only GETs against public data.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
UA = "github-repo-scout"
TOKEN = None
NOW = dt.datetime.now(dt.timezone.utc)


def _token(no_auth):
    if no_auth:
        return None
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    if TOKEN and url.startswith(API):
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            return json.loads(body) if accept.endswith("json") else body
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code in (403, 429):
            reset = e.headers.get("x-ratelimit-reset")
            when = dt.datetime.fromtimestamp(int(reset)).strftime("%H:%M") if reset else "later"
            sys.exit(f"GitHub rate limit hit ({e.code}). Retry after {when}, or set GITHUB_TOKEN / log in with gh.")
        raise


# ---------- sources ----------

def trending(since, language, limit):
    """Scrape github.com/trending — GitHub's own day/week/month ranking (no API exists for it)."""
    path = f"/trending/{urllib.parse.quote(language.lower())}" if language else "/trending"
    page = get(f"https://github.com{path}?since={since}", accept="text/html")
    repos = []
    for art in re.findall(r'<article class="Box-row">(.*?)</article>', page, re.S):
        m = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^/"]+/[^/"]+)"', art, re.S)
        if not m:
            continue
        name = m.group(1)
        desc = re.search(r'<p class="[^"]*color-fg-muted[^"]*">\s*(.*?)\s*</p>', art, re.S)
        lang = re.search(r'itemprop="programmingLanguage">([^<]+)<', art)
        stars = re.search(rf'href="/{re.escape(name)}/stargazers"[^>]*>.*?</svg>\s*([\d,]+)', art, re.S)
        gained = re.search(r'([\d,]+)\s+stars\s+(today|this week|this month)', art)
        repos.append({
            "full_name": name,
            "url": f"https://github.com/{name}",
            "description": html.unescape(re.sub(r"<[^>]+>", "", desc.group(1))).strip() if desc else "",
            "language": lang.group(1).strip() if lang else None,
            "stars": _int(stars.group(1)) if stars else None,
            "stars_gained": _int(gained.group(1)) if gained else None,
            "period": gained.group(2) if gained else since,
        })
    return repos[:limit]


def search(q, limit, sort="stars"):
    """sort="stars" for popularity lists; sort=None uses GitHub's best-match relevance ranking."""
    params = {"q": q, "per_page": min(limit, 100)}
    if sort:
        params.update({"sort": sort, "order": "desc"})
    url = f"{API}/search/repositories?" + urllib.parse.urlencode(params)
    data = get(url) or {}
    return [_from_api(r) for r in data.get("items", [])][:limit], data.get("total_count", 0)


def _from_api(r):
    return {
        "full_name": r["full_name"],
        "url": r["html_url"],
        "description": r.get("description") or "",
        "language": r.get("language"),
        "stars": r.get("stargazers_count"),
        "forks": r.get("forks_count"),
        "license": (r.get("license") or {}).get("spdx_id"),
        "pushed_at": r.get("pushed_at"),
        "created_at": r.get("created_at"),
        "archived": r.get("archived"),
        "topics": r.get("topics", []),
    }


def _int(s):
    return int(s.replace(",", ""))


def _days_ago(iso):
    return (NOW - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days if iso else None


# ---------- verification ----------

def verify(full_name, min_stars=50, stale_days=365):
    r = get(f"{API}/repos/{full_name}")
    if r is None:
        return {"full_name": full_name, "verdict": "not-found", "checks": {}, "flags": ["repo not found"]}
    owner = r["owner"]
    org_verified = None
    if owner.get("type") == "Organization":
        org = get(f"{API}/orgs/{owner['login']}") or {}
        org_verified = bool(org.get("is_verified"))

    pushed = _days_ago(r.get("pushed_at"))
    age = max(_days_ago(r.get("created_at")) or 1, 1)
    stars = r.get("stargazers_count", 0)
    lic = (r.get("license") or {}).get("spdx_id")
    checks = {
        "not_archived": not r.get("archived") and not r.get("disabled"),
        "not_fork": not r.get("fork"),
        "has_license": bool(lic) and lic != "NOASSERTION",
        "recently_active": pushed is not None and pushed <= stale_days,
        "enough_stars": stars >= min_stars,
        "has_description": bool(r.get("description")),
    }
    flags = []
    if org_verified:
        flags.append("owner is a GitHub-verified organization")
    if age < 30 and stars / age > 1000:
        flags.append(f"very young ({age}d) with {stars:,} stars: star spike, check it's not botted or hype-only")
    if r.get("forks_count", 0) == 0 and stars > 1000:
        flags.append("many stars but zero forks: unusual, inspect before trusting")
    hard_fail = not (checks["not_archived"] and checks["not_fork"])
    passed = sum(checks.values())
    verdict = "fail" if hard_fail else ("verified" if passed == len(checks) else
                                        "caution" if passed >= len(checks) - 2 else "fail")
    out = _from_api(r)
    out.update({
        "owner_type": owner.get("type"),
        "org_verified": org_verified,
        "open_issues": r.get("open_issues_count"),
        "last_push_days": pushed,
        "age_days": age,
        "verdict": verdict,
        "checks": checks,
        "flags": flags,
    })
    return out


# ---------- output ----------

def table(rows, extra=None):
    cols = ["#", "Repo", "Stars"] + ([extra] if extra else []) + ["Lang", "Verdict", "Description"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for i, r in enumerate(rows, 1):
        desc = (r.get("description") or "").replace("|", "/")
        desc = desc[:90] + ("…" if len(desc) > 90 else "")
        cells = [str(i), f"[{r['full_name']}]({r['url']})",
                 f"{r['stars']:,}" if r.get("stars") is not None else "?"]
        if extra:
            cells.append(f"+{r['stars_gained']:,}" if r.get("stars_gained") else "")
        cells += [r.get("language") or "", r.get("verdict", "—"), desc]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def attach_verification(rows, args):
    for r in rows:
        v = verify(r["full_name"], args.min_stars, args.stale_days)
        stars_gained, period = r.get("stars_gained"), r.get("period")
        r.update(v)
        if stars_gained is not None:
            r["stars_gained"], r["period"] = stars_gained, period
    return rows


def main():
    global TOKEN
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-auth", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, limit=10):
        sp.add_argument("--limit", type=int, default=limit)
        sp.add_argument("--verify", action="store_true", help="run quality checks on each result")
        sp.add_argument("--min-stars", type=int, default=50)
        sp.add_argument("--stale-days", type=int, default=365)

    t = sub.add_parser("trending"); common(t)
    t.add_argument("--since", choices=["daily", "weekly", "monthly"], default="daily")
    t.add_argument("--language")

    tp = sub.add_parser("top"); common(tp)
    tp.add_argument("--query", default="", help='extra qualifiers, e.g. "topic:llm" or "created:>2026-01-01"')
    tp.add_argument("--language")
    tp.add_argument("--floor", type=int, default=1000, help="stars floor for the search")

    f = sub.add_parser("find"); common(f)
    f.add_argument("task", help="keywords for what the repo should do")
    f.add_argument("--language")
    f.add_argument("--by-stars", action="store_true", help="rank by stars instead of relevance")
    f.add_argument("--pushed-within", type=int, default=365, help="days since last push")

    v = sub.add_parser("verify")
    v.add_argument("repos", nargs="+")
    v.add_argument("--min-stars", type=int, default=50)
    v.add_argument("--stale-days", type=int, default=365)

    # allow --json / --no-auth anywhere on the line
    argv = sys.argv[1:]
    flags = [a for a in argv if a in ("--json", "--no-auth")]
    args = p.parse_args(flags + [a for a in argv if a not in ("--json", "--no-auth")])
    TOKEN = _token(args.no_auth)

    if args.cmd == "verify":
        rows = [verify(r.strip().removeprefix("https://github.com/").strip("/"), args.min_stars, args.stale_days)
                for r in args.repos]
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for r in rows:
                print(f"## {r['full_name']} — {r['verdict'].upper()}")
                if r.get("url"):
                    print(f"{r['url']} · {r['stars']:,}★ · {r['forks']:,} forks · license {r['license']} · "
                          f"last push {r['last_push_days']}d ago · {r['open_issues']} open issues · "
                          f"owner {r['owner_type']}{' (verified org)' if r['org_verified'] else ''}")
                for k, ok in r["checks"].items():
                    print(f"- {'✅' if ok else '❌'} {k}")
                for fl in r["flags"]:
                    print(f"- ⚠️ {fl}" if "verified" not in fl else f"- 🏅 {fl}")
                print()
        return

    extra = None
    header = ""
    if args.cmd == "trending":
        rows = trending(args.since, args.language, args.limit)
        label = {"daily": "of the day", "weekly": "of the week", "monthly": "of the month"}[args.since]
        header = f"GitHub trending repos {label}" + (f" ({args.language})" if args.language else "") + \
                 f" — source: github.com/trending, {NOW:%Y-%m-%d}"
        extra = "Gained"
    elif args.cmd == "top":
        q = " ".join(x for x in [args.query, f"language:{args.language}" if args.language else "",
                                 f"stars:>={args.floor}", "archived:false"] if x)
        rows, total = search(q, args.limit)
        header = f"Top-starred repos for `{q}` ({total:,} matches)"
    else:
        since = (NOW - dt.timedelta(days=args.pushed_within)).strftime("%Y-%m-%d")
        q = " ".join(x for x in [args.task, "in:name,description,topics",
                                 f"language:{args.language}" if args.language else "",
                                 f"stars:>={args.min_stars}", f"pushed:>={since}", "archived:false", "fork:false"] if x)
        rows, total = search(q, args.limit, sort="stars" if args.by_stars else None)
        header = f"Repos for “{args.task}” (`{q}`, {total:,} matches, ranked by {'stars' if args.by_stars else 'relevance'})"

    if args.verify:
        rows = attach_verification(rows, args)
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(header + "\n")
        print(table(rows, extra) if rows else "No results.")


if __name__ == "__main__":
    main()
