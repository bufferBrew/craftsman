---
name: github-repo-scout
description: Find and vet GitHub repositories. Lists trending repos of the day, week or month, top-starred repos (overall, by language or topic), and searches GitHub for repos that solve a specific task ("a library for PDF table extraction", "best open-source Flutter charting package"), then verifies each candidate (not archived, licensed, recently active, real adoption, verified org). Use this whenever the user asks for GitHub repo of the day/week/month, trending repos, most-starred or popular repos, "is there a repo/library/tool for X", "find me an open-source alternative to Y", or wants to check whether a repo is legit or maintained, even if they don't say "GitHub" explicitly.
---

# GitHub Repo Scout

One script, `scripts/scout.py` (Python stdlib only), does the data gathering. Your job is to pick the right mode, run it, and add judgment on top: the script returns facts, you decide which repo actually fits the user's task.

Run it as `python3 <skill base directory>/scripts/scout.py <mode> ...` (the base directory is shown when this skill loads). Everything is a read-only GET on public data.

## Modes

| User wants | Command |
|---|---|
| Repo of the day / week / month | `trending --since daily\|weekly\|monthly [--language python] --verify` |
| Highest-starred repos | `top [--query "topic:llm"] [--language rust] [--floor 1000]` |
| Repos for a task | `find "task keywords" [--language dart] [--min-stars 100] --verify` |
| Is this repo legit / maintained? | `verify owner/repo [owner/repo ...]` |

Common flags: `--limit N` (default 10), `--verify` (adds a verdict column), `--json` (for your own post-processing), `--no-auth`.

**"Repo of the day/week/month"** means the #1 entry of GitHub's own Trending page for that window, ranked by stars gained in the window. The Trending page is the only source for this; the REST API has no equivalent, so the script reads the page's HTML. If it returns zero rows, GitHub changed the markup: say so and fall back to `find` with `created:>` or `pushed:>` date qualifiers via `top --query`, labeling it as an approximation. Present the winner first with a sentence on why it's trending, then the rest of the list.

**Task search** is where judgment matters:
1. Turn the request into 2-3 keyword variants (synonyms, the common library names, the language's ecosystem term) and run `find` for each; a single phrasing misses a lot. Add `--language` when the user's stack is known (this workspace is mostly Flutter/Dart, Kotlin, TypeScript, Python).
   Results are ranked by GitHub's relevance, not stars, because star-sorting surfaces famous but off-topic repos (a "pdf table extraction" search sorted by stars returns `public-apis` first). Use `--by-stars` only when the user wants the most popular option. Matching covers name, description and topics, so if a search returns too few hits, loosen the keywords or lower `--min-stars`.
2. Merge, dedupe, then run `--verify` on the shortlist.
3. Recommend 1-3 repos, not the whole list: say why each fits the task, what it costs (license, language, maintenance), and which one you'd pick. Read the README (`gh repo view owner/repo` or fetch the page) before recommending if the description alone doesn't settle fit.

## What "verified" means here

GitHub has no blanket "verified repo" badge, so the script checks evidence, and reports exactly which checks failed rather than a bare score:

- not archived/disabled and not a fork (hard failures)
- has an SPDX license (no license = you legally can't use it)
- pushed within the last 365 days (`--stale-days` to change)
- at least 50 stars (`--min-stars`)
- has a description
- bonus signals: owner is a GitHub-verified organization; flags for suspicious star spikes (young repo with a huge star rate) or many stars and zero forks

Verdicts: `verified` (all pass), `caution` (one or two soft checks fail), `fail`. Always tell the user this is a heuristic: a `verified` repo is maintained and licensed, not security-audited. If they plan to run its code or add it as a dependency, suggest skimming the code and its open issues first, and never run an unfamiliar repo's install scripts on their behalf without asking.

## Output

Show the script's markdown table (repo links are already clickable), then your recommendation underneath. Include the date for trending results, since they change daily. Don't pad: the table plus a short pick-and-why is the answer.

## Limits and gotchas

- Unauthenticated, the search API allows ~10 requests/minute and core ~60/hour. `--verify` costs 1-2 calls per repo, so verify a shortlist of ~10, not 100. The script uses `$GITHUB_TOKEN`/`$GH_TOKEN` or `gh auth token` when available (higher limits); pass `--no-auth` to force anonymous calls. On a rate-limit error it exits with the reset time: report it rather than retrying in a loop.
- Star counts measure attention, not quality. For old, famous repos, check `last_push_days` before recommending.
- The trending `Gained` column is stars gained during the window, taken from the page as-is.
