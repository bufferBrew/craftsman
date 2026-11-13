---
name: implicit-state-machines
description: Use when asked to find, list or audit the state machines in a codebase ("what are the states of X", "find implicit state machines", "map the lifecycles"), and when a review or bug touches a status/state/stage column, a lifecycle enum, or a busy/in-flight flag. Finds lifecycles encoded as strings, enums, nullable timestamps and booleans, traces every writer to recover the real transitions, and flags stuck, dead, unguarded and stale states. Read-only.
---

# Implicit State Machines

## Overview

Most apps never declare a state machine. The lifecycle of a connection, a job, an order or a
form lives in a `status` text column, an enum, a pair of booleans or a nullable `*_at` column, and
the transitions are scattered across whatever code happens to write it. Nobody owns the whole
picture, so the bugs hide in the gaps: a state you can enter but never leave, a state nothing
ever sets, a write that skips the guard every other path respects.

**Core principle:** the states are declared in one place, but the machine is defined by its
**writers**. List the states from the schema or type, then find every line that assigns them —
the transitions you can prove from code are the real machine, whatever the docs say.

This skill is read-only. It reports; it never edits code or data.

## 1. Find candidates

Sweep all four layers; each hides a different kind of machine.

| Layer | Look for |
|---|---|
| Database | `CHECK (col IN (...))` / `= ANY (ARRAY[...])` constraints, Postgres enum types, columns named `status`, `state`, `stage`, `phase`, `step`; nullable `*_at` columns that mark a transition (`completed_at`, `revoked_at`, `claimed_at`, `lease_expires_at`) |
| Domain types | `enum`s, sealed classes / tagged unions, string-literal unions (`'queued' \| 'running'`), constants lists like `['ordered', 'shipped', ...]` |
| Server/back end | Job tables and workers (queued → running → done), retry/attempt counters, leases and heartbeats, webhooks, cron paths |
| Client/UI | Busy flags (`_saving`, `_busy`, `_syncing`, `inFlight`), static or module-level guards, optimistic-update layers (pending → confirmed / rolled back), debounced autosave, permission flows, async-value loading/data/error |

Useful starting greps (adapt to the language):

```
grep -rnE "^\s*(export )?enum |sealed class|type \w+ = '[a-z_]+' \|" src lib
grep -rnE "status|state|stage|phase" --include=*.sql migrations
grep -rnE "(bool|let|var) _?(busy|saving|loading|syncing|pending|running|inFlight|submitting)" .
grep -rnE "status: *['\"][a-z_]+['\"]|\.update\(\{ *['\"]?status" .
```

With database access, read constraints and column defaults straight from the catalog
(`pg_constraint`, `information_schema.columns`) — migrations can drift from the live schema.

Skip pure display enums (button sizes, colours, sort columns, categories). A candidate is a
machine only if the value **changes over the life of one entity**.

## 2. Classify each machine

- **Persisted** — stored; survives restarts; several writers (server, client, cron) can race.
- **Derived** — computed from other fields every time (status from dates, from counts). Cannot get
  stuck, but can disagree with a persisted copy.
- **In-memory** — a process or widget lifetime: busy flags, optimistic layers, autosave. Lost on
  restart; the classic bugs are double-submit and leaks from a lifetime ending mid-flight.

Note when one row carries **two orthogonal machines** (an order's shipping stage and its refund
status) — they must not be merged into one diagram.

## 3. Trace the transitions

For every state value, grep for each place that **writes** it — not reads. For each writer
record: `from → to`, the trigger (user action, sync, cron, webhook, error handler), any guard
(`where status = 'x'`, rank comparison, `if (busy) return`), and `file:line`.

Then check, per machine:

- **Initial state** — what the default is and whether any code actually creates rows in it.
- **Terminal states** — which ones have no way out, and whether that is intended.
- **Error recovery** — every path that enters an error/failed state: which path leaves it? Do all
  entry paths (manual, cron, retry) also have a matching exit? Asymmetry here is the most common
  real bug.
- **Monotonicity** — should it only move forward (shipping stages, refunds)? Is that enforced on
  *every* writer, or only some?
- **Unguarded writes** — a setter that ignores the current state can overwrite a state that should
  stick (e.g. "keep" clobbering "converted").
- **Crash mid-transition** — a job set to `running` by a process that dies: is there a lease,
  timeout or sweeper, and does the UI offer a way out?
- **Concurrency** — two writers (two taps, two workers, client vs server) racing on one entity;
  single "pending" slots that a second action overwrites or a first completion clears.
- **Lifetime** — in-memory machines whose owner (widget, auto-disposed provider, request scope)
  can be torn down while an `await` is pending.

## 4. Flag findings

| Finding | Meaning |
|---|---|
| **Stuck** | Reachable state with no exit on some path (error set by cron but only cleared by a manual action; `running` with no sweeper) |
| **Dead** | Declared state nothing ever writes (`queued` that is only a column default; enum values only rendered) |
| **Unguarded** | A writer that can move an entity backwards or out of a state other paths protect |
| **Stale** | A persisted copy of a derived state that is only refreshed on some writes |
| **Racy** | Two writers or overlapping in-flight operations that can lose an update |

Only report a finding you traced to `file:line`. If a transition depends on runtime behaviour you
could not confirm from code, say "possible" and what would confirm it.

## Output format

```
## Persisted
| # | Machine | States | Transitions (trigger) | Where |

## Derived
- **Name** (`file:line`): states — what it is computed from.

## In-memory
- **Name**: states and guard — `file:line`.

## Findings
1. [Stuck|Dead|Unguarded|Stale|Racy] Machine — what happens, concrete scenario, `file:line`.
```

Lead with the findings if the user asked about bugs; lead with the catalogue if they asked for a
map. Mermaid `stateDiagram-v2` blocks are welcome for the two or three machines that matter most —
not for every enum.

## Hand-offs

- A finding that needs a fix goes to `debugger` (root cause) or `coder` (the fix) — this skill does
  not patch.
- A deliberate, accepted gap (e.g. "we never sweep stale jobs, volume is tiny") is a
  `logging-tradeoffs` entry, not a recurring finding.
- Close with `caveats-and-status`: which layers were searched, and which were not (e.g. no
  database access, so constraints came from migrations only).
