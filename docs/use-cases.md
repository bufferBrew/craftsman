---
title: Use cases
---

# Use cases

Five worked scenarios showing when each part of craftsman earns its keep. Component details are
in the [plugin reference](https://github.com/bufferbrewlabs/craftsman/blob/main/craftsman-plugin/README.md).

## 1. "Every fix comes back with a bonus refactor"

**Symptom:** you ask for a one-line fix and get the fix plus renamed variables, extracted
helpers, and a reformatted file. Reviewing the diff takes longer than writing it yourself.

**With craftsman:** the `smallest-change-first` skill runs before any new code is written — a
seven-step ladder (does it need to exist? → already in the codebase? → stdlib? → platform
feature? → existing dependency? → one line? → only then write the minimum). Anything beyond the
literal request requires asking you first. For genuinely tiny edits, skip the pipeline entirely:

```
/craftsman:quick fix the off-by-one in Paginator.pageCount
```

`quick` skips the planner/tester/reviewer overhead but keeps the discipline: it still reads
before editing, still runs the project's build command, and still ends with a Caveats & status
block. If the change turns out bigger than it looked, it says so and stops.

## 2. "The same bug keeps getting filed as a new one"

**Symptom:** a null-handling bug was fixed in `OrderService` in March. In May the same root
cause resurfaces in `InvoiceService` and burns another afternoon because nobody connected the
two.

**With craftsman:** in a project with a [graphify](https://pypi.org/project/graphifyy/) graph,
the `debugger` agent queries the graph before grepping (`graphify query "<symptom>"`), which
surfaces the other call sites of an implicated shared function as suspects. Before filing a new
`KNOWN_ISSUES.md` entry it runs `graphify path` against existing entries — a short path means
the "new" bug is likely the same root cause resurfacing. If the match lands on a **resolved**
entry, its recorded one-line fix is recalled for reuse instead of being re-derived.

```
/craftsman:orchestrate fix the crash in InvoiceService when the line-item list is empty
```

Nothing is auto-merged or auto-fixed — matches are surfaced for you to judge.

## 3. "New project setup is a pile of guessed defaults"

**Symptom:** generic scaffolding writes a `CLAUDE.md` with `npm test` as the verify command when
the repo actually uses `pnpm turbo test`, plus files you never asked for.

**With craftsman:**

```
/craftsman:init
```

detects the stack from ~25 marker patterns, then resolves the **real** build/verify command in
priority order: CI config → README/CONTRIBUTING → `package.json` scripts (or Makefile /
`pyproject.toml`) → table default. It checks whether an issue log already exists under another
name (`TODO.md`, `ISSUES.md`, `BACKLOG.md`) before proposing `KNOWN_ISSUES.md`, shows you the
exact file content, and writes only on explicit yes. It never overwrites an existing `CLAUDE.md`
— it offers to append, and asks first.

## 4. "'Done!' — but nothing was actually verified"

**Symptom:** the report says done, the demo crashes. You find out the build was never run and the
edge case was silently skipped.

**With craftsman:** two mechanisms. First, orchestrator gates require **fresh evidence**, not
claims — `coder` must show actual build output before the pipeline advances, `tester` must show
the suite run. Second, the `caveats-and-status` skill ends every nontrivial task with a fixed
closing block:

```
Caveats & status
  Verified     build + unit suite pass; original repro no longer crashes
  Assumed      empty-state copy is a placeholder pending design
  Not covered  instrumented UI tests (no emulator in this run)
```

so "done" always comes with its boundaries attached — what was proven, what was assumed, and
what you still need to check yourself.

## 5. "It works, except when it gets stuck"

**Symptom:** a sync stops running and nothing says why. A job sits at `running` for days. A
"converted" item quietly turns back into "kept". Each one is a lifecycle the code never wrote
down: a `status` column, an enum or a `_busy` flag, with transitions scattered across whoever
happens to write it.

**With craftsman:** `/craftsman:state-machines` runs the `implicit-state-machines` skill. It reads
the states from the schema, the types, on-device storage and leftover files, then finds every line
that **writes** each state. The transitions it can prove from code are the real machine. It reports:

```
Findings
  1. [Stuck] connections.status: the scheduled sync only selects `active`, failures set `error`,
     and only a manual sync sets it back. One failure stops background sync for good.
     sync-worker/index.ts:121, :184, :390
  2. [Dead] sync_jobs.status = queued: only the column default; jobs are inserted as `running`.
  3. [Unguarded] "Keep" writes `kept` without checking the current status, undoing `converted`.
```

It is read-only: fixes go to `debugger` or `coder`. For a client with dozens of busy flags, its
`busy_flags.py` helper lists where each flag is set and reset, and whether anything guards it.

