---
name: caveats-and-status
description: Use when about to report any nontrivial task as complete — requires closing with separate Status and Caveats sections stating what was verified, what's unresolved, and what was assumed.
---

# Caveats & Status

## Overview

"Done" without a status check is a guess wearing a confident voice. This skill defines the closing
format every nontrivial completed task uses, so what wasn't verified is always visible rather than
buried in an upbeat summary.

**Core principle:** state what you checked, not just what you did.

## When this applies

Any response that reports a task as complete, fixed, or passing — code changes, file scaffolding,
investigations with a conclusion. Skip it for pure Q&A with no action taken, and for the `quick`
flow's trivial one-liners where the verification step itself already says everything needed (don't
pad a two-line change with a boilerplate section that adds nothing).

## The format

End the response with two separate sections — Status first, Caveats second:

```
**Status**
- Verified: <what you actually ran/observed, with the result>
- Not covered: <what's explicitly out of scope or unverified>

**Caveats**

| Caveat | Impact | How to resolve |
|---|---|---|
| <the assumption, gap, or thing taken on faith> | <what it actually means for the user> | <the specific check, command, or decision that settles it> |
```

Status stays a bullet list; **Caveats is always a table**, one row per caveat — never a bullet
list, and never merged into Status. Status is what you can back with evidence from this session;
Caveats is everything you couldn't. The table makes each gap scannable and forces the "so what" to
be stated: a caveat with no real impact is usually not worth a row.

Omit a Status line entirely if it's genuinely empty, and if there are no caveats at all, omit the
whole Caveats section rather than emitting a table with a placeholder row.

## Rules

- "Verified" requires a command actually run or a behavior actually observed in this session —
  not "should work," not a previous run, not extrapolation from a partial check.
- Before writing an "Assumed" line, try to validate it if a check is actually available in this
  session — grep for the symbol, read the file, run the command. Only fall back to "Assumed" once
  verification genuinely isn't possible here; don't default to assuming when checking was an
  option.
- If verification wasn't possible (no test environment, no way to run the app), say so explicitly
  in "Not covered" rather than silently omitting it — an honest gap beats an implied guarantee.
- Every Caveats row needs all three cells filled with something real. If "How to resolve" would be
  empty, the caveat is either not actionable — say why in that cell — or it belongs in Status under
  "Not covered" instead.
- Run the verification and read its actual output *before* writing the "Verified" line — the
  claim comes after the evidence, never before. Report failures honestly, with the actual error
  output, not a softened summary. This format stands alone; it does not depend on any other
  plugin being installed.
