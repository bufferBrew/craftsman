---
description: Check the local craftsman install for known silent-failure conditions — Git Bash availability, graphify graph status, and the Windows python3 Store-stub trap. Prints OK or MISSING for each.
argument-hint: (no arguments — checks the current environment)
---

Check the local install for the three conditions that cause craftsman features to silently do
nothing. Print **OK** or **MISSING** for each, with a one-line fix if missing. Then a summary line.

## Check 1 — Git Bash (Windows hook dispatcher)

The hook dispatcher (`craftsman-plugin/hooks/run-hook.cmd`) looks for bash in this order:
1. `C:\Program Files\Git\bin\bash.exe`
2. `C:\Program Files (x86)\Git\bin\bash.exe`
3. `bash` anywhere on PATH

If none is found, hooks skip silently — the session-start reminder and the graphify PreToolUse
hints never fire. The rest of the plugin still works.

Check each path in order and report the first one found. On macOS/Linux, check `which bash`.

```powershell
# Windows check
if     (Test-Path 'C:\Program Files\Git\bin\bash.exe')      { "OK: Git Bash at standard path" }
elseif (Test-Path 'C:\Program Files (x86)\Git\bin\bash.exe') { "OK: Git Bash at x86 path" }
elseif (Get-Command bash -ErrorAction SilentlyContinue)       { "OK: bash found on PATH" }
else { "MISSING: no bash found — hooks skip silently.`nFix: install Git for Windows from https://gitforwindows.org" }
```

## Check 2 — graphify graph (`graphify-out/graph.json`)

Without a built graph, all graphify features are complete no-ops: recurring-bug dedup, query-first
codebase navigation, and the PreToolUse hints do nothing.

The graph is never built automatically — you trigger it yourself (`graphify .` or `/graphify`).

```powershell
if (Test-Path 'graphify-out\graph.json') {
    "OK: graphify-out/graph.json exists — graphify features active"
} else {
    "MISSING: no graph found — graphify features are inactive.`nFix: run 'graphify .' (CLI) or '/graphify' (skill) to build one.`n      If graphify is not installed: pip install graphifyy"
}
```

## Check 3 — Python 3 (graphify PreToolUse hooks)

The graphify PreToolUse hooks parse tool input with `python3`. On Windows, `python3` may be a
non-functional Microsoft Store stub — it is on PATH but opens the Store instead of running Python.
The hooks test each candidate before using it; if neither works, the Read hook silently skips.

Run this in a terminal to check:

```
python3 --version
```

- If the output is `Python 3.x.y` → **OK**.
- If the command hangs, opens the Microsoft Store, or returns without printing a version → **MISSING** (stub trap active).

Fix: install Python from https://python.org (check "Add to PATH" during install) and restart the
terminal. Verify with `python3 --version` in the new terminal.

## Summary

After all three checks, print one of:
- **All OK** — craftsman is fully operational in this environment.
- **N item(s) need attention** — list each missing item with its one-line fix.

`/craftsman:doctor` is diagnostic only — it does not install or modify anything.
