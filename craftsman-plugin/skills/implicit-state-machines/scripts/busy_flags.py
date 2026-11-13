#!/usr/bin/env python3
"""List busy/in-flight flags and how each one is set, reset and guarded.

Read-only, Python stdlib only. Part of the implicit-state-machines skill.

    python3 -I busy_flags.py <dir> [--ext .dart] [--names busy,saving,...] [--all]

For every boolean flag whose name matches --names (declared like `bool _saving = false`,
`let saving = false`, `var isBusy = false`, `const [saving, setSaving] = useState(false)`), it
prints the lines that set it true and false, whether a reset sits inside a `finally` or `catch`
block, whether the reset is gated on `mounted`, and whether anything guards against re-entry
(`if (flag) return`, `flag ? null :`, `disabled={flag}`, `saving: flag`).

A flag is marked CHECK when it is set true but has no reset in `finally`/`catch` (it can stay
set if the awaited call throws), or when nothing guards it (double submit). These are leads,
not findings: read the code before reporting either.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

DEFAULT_NAMES = (
    "busy,saving,loading,syncing,pending,running,inflight,submitting,"
    "generating,refreshing,sending,deleting,uploading,importing,exporting,testing,working"
)
SKIP_DIRS = {
    ".git", "node_modules", "build", "dist", ".dart_tool", "graphify-out",
    "coverage", ".next", "Pods", ".gradle", "test", "tests", "__tests__",
}
REACH = 6  # lines above a reset to search for an enclosing finally/catch or mounted check


def declarations(line: str, names: list[str]) -> list[tuple[str, str]]:
    """Return (flag, setter) pairs declared on this line; setter is '' unless React state."""
    found = []
    word = "|".join(names)
    flag = rf"(_?(?:is)?(?:{word})\w*)"
    if re.search(r"\bbool\s+\w+\s*=", line):  # Dart: `bool _a = false, _busy = false;`
        for m in re.finditer(rf"(?:\bbool\s+|,\s*){flag}\s*=", line, re.IGNORECASE):
            found.append((m.group(1), ""))
    for pattern in (
        rf"\b(?:let|var)\s+{flag}\s*(?::\s*\w+)?\s*=\s*(?:false|true)\b",  # TS, Swift, Kotlin var
        rf"\b(?:private\s+)?var\s+{flag}\s*(?::\s*Boolean)?\s*=\s*(?:false|true)\b",
    ):
        for m in re.finditer(pattern, line, re.IGNORECASE):
            found.append((m.group(1), ""))
    react = re.search(
        rf"const\s*\[\s*{flag}\s*,\s*(set\w+)\s*\]\s*=\s*useState\(\s*(?:false|true)", line, re.IGNORECASE
    )
    if react:
        found.append((react.group(1), react.group(2)))
    return found


def scan_file(path: str, names: list[str]) -> list[dict]:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return []
    results = []
    seen = set()
    for i, line in enumerate(lines, 1):
        for flag, setter in declarations(line, names):
            if flag in seen:
                continue
            seen.add(flag)
            results.append(analyse(path, lines, i, flag, setter))
    return results


def analyse(path: str, lines: list[str], decl: int, flag: str, setter: str) -> dict:
    f = re.escape(flag)
    if setter:
        s = re.escape(setter)
        true_re = re.compile(rf"\b{s}\(\s*true\s*\)")
        false_re = re.compile(rf"\b{s}\(\s*false\s*\)")
    else:
        true_re = re.compile(rf"(?<![\w.]){f}\s*=\s*true\b|\bthis\.{f}\s*=\s*true\b")
        false_re = re.compile(rf"(?<![\w.]){f}\s*=\s*false\b|\bthis\.{f}\s*=\s*false\b")
    guard_re = re.compile(
        rf"if\s*\([^)]*\b{f}\b[^)]*\)\s*(?:\{{\s*)?return"  # if (a || flag) return
        rf"|\b{f}\b[^?;]*\?\s*null\b"  # onPressed: flag ? null : (also split over two lines)
        rf"|disabled\s*=\s*\{{[^}}]*\b{f}\b"  # disabled={flag}
        rf"|\b\w+\s*:\s*(?:this\.)?{f}\s*[,)]"  # saving: flag,
        rf"|\bif\s*\([^)]*\b{f}\b[^)]*\)\s*\{{?\s*$"  # if (flag) { on its own line
    )

    sets_true, sets_false, resets_safe, mounted, guards = [], [], [], [], []
    for n, text in enumerate(lines, 1):
        if n == decl:
            continue
        if true_re.search(text):
            sets_true.append(n)
        if false_re.search(text):
            sets_false.append(n)
            window = " ".join(lines[max(0, n - 1 - REACH):n])
            if re.search(r"\bfinally\b|\bcatch\b|\.catch\(|\bonError\b|\.whenComplete\(", window):
                resets_safe.append(n)
            if re.search(r"\bmounted\b|isMounted|!disposed|\bisActive\b", window):
                mounted.append(n)
        # Join with the next line so `flag\n    ? null` and `if (\n flag) return` still match.
        joined = text + " " + (lines[n].strip() if n < len(lines) else "")
        if n != decl and guard_re.search(joined) and not true_re.search(text):
            guards.append(n)

    notes = []
    if sets_true and not resets_safe:
        notes.append("no reset in finally/catch")
    if sets_true and not guards:
        notes.append("no guard found")
    if sets_true and not sets_false:
        notes.append("never reset")
    return {
        "file": path, "line": decl, "flag": flag,
        "true": sets_true, "false": sets_false, "safe_reset": resets_safe,
        "mounted": mounted, "guard": guards, "notes": notes,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="directory to scan, e.g. lib or src")
    ap.add_argument("--ext", default=".dart", help="comma-separated extensions (default .dart)")
    ap.add_argument("--names", default=DEFAULT_NAMES, help="comma-separated flag name stems")
    ap.add_argument("--all", action="store_true", help="also print flags with nothing to check")
    args = ap.parse_args()

    exts = tuple(e.strip() if e.strip().startswith(".") else "." + e.strip() for e in args.ext.split(","))
    names = [n.strip() for n in args.names.split(",") if n.strip()]
    if not os.path.isdir(args.root):
        print(f"not a directory: {args.root}", file=sys.stderr)
        return 2

    rows = []
    for dirpath, dirnames, filenames in os.walk(args.root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(exts) and not re.search(r"(_test|\.test|\.spec)\.", name):
                rows.extend(scan_file(os.path.join(dirpath, name), names))

    flagged = [r for r in rows if r["notes"]]
    shown = rows if args.all else flagged
    for r in shown:
        status = "CHECK " + "; ".join(r["notes"]) if r["notes"] else "ok"
        print(f"{r['file']}:{r['line']} {r['flag']}  [{status}]")
        print(f"    true@{r['true']} false@{r['false']} finally/catch@{r['safe_reset']} "
              f"mounted@{r['mounted']} guard@{r['guard']}")
    print(f"\n{len(rows)} flags, {len(flagged)} to check"
          + ("" if args.all or not rows else " (--all lists the rest)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
