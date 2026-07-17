---
description: Check the local craftsman install for known silent-failure conditions — Git Bash availability, graphify graph status, and the Windows python3 Store-stub trap. Prints OK or MISSING for each. Pass --fix to remediate detected issues, each one confirmed before it runs.
argument-hint: "[--fix]  (no args = diagnostic only)"
---

Check the local install for the three conditions that cause craftsman features to silently do
nothing. Print **OK** or **MISSING** for each, with a one-line fix if missing. Then a summary line.

## Mode

Arguments: $ARGUMENTS

- **Default (no `--fix`):** diagnostic only. Run all three checks, print OK/MISSING, change nothing.
- **`--fix`:** after a check reports MISSING, propose its exact remediation command, ask **y/n**, and
  run it **only on `y`**. Skip any the user declines. After running a fix, re-run that one check and
  report OK / still-MISSING. Never run an install or write to the project without the per-item `y` —
  the `--fix` flag is consent to *offer* repairs, not to run them silently.

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

**`--fix` remediation (Windows):** propose `winget install --id Git.Git -e`, ask y/n, run on y. This
installs to `C:\Program Files\Git\bin\bash.exe` — the first path `run-hook.cmd` probes — so **no PATH
edit is needed**. If `winget` is not available (`Get-Command winget` fails), don't try to install;
print the https://gitforwindows.org link for a manual install instead. On macOS/Linux `which bash`
practically always passes; if it genuinely fails, suggest `brew install bash` / the distro package
but do not auto-run it. After a successful install, re-run the check above and report the result.

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

**`--fix` remediation:** propose `graphify .`, ask y/n, run on y. Note this **writes `graphify-out/`
into the current project** — that project-level side effect is exactly why it needs the per-item
confirmation. If the `graphify` CLI itself is missing (`Get-Command graphify` fails), offer
`pip install graphifyy` first (separate y/n), then `graphify .`. After it runs, re-check for
`graphify-out\graph.json` and report the result.

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

**`--fix` remediation (Windows):** propose `winget install --id Python.Python.3.12 -e`, ask y/n, run
on y (fall back to the python.org link if `winget` is unavailable). **State clearly that this is a
partial fix:** the Microsoft Store app-execution alias can still shadow the real Python on PATH
order, so also tell the user to disable it in **Settings → Apps → Advanced app settings → App
execution aliases** (turn off the `python3.exe` / `python.exe` entries). Do **not** report OK until
`python3 --version` prints a real `Python 3.x.y` in a fresh terminal — an install alone does not
guarantee the stub is out of the way.

## Summary

After all three checks, print one of:
- **All OK** — craftsman is fully operational in this environment.
- **N item(s) need attention** — list each missing item with its one-line fix.

By default `/craftsman:doctor` is diagnostic only — it does not install or modify anything. With
`--fix` it can remediate the detected issues, but every repair is shown and confirmed (y/n) before
it runs; declined items are left untouched.
