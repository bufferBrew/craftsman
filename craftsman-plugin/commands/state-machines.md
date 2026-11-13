---
description: Find and audit the implicit state machines in this project — status columns, lifecycle enums, busy flags — with their real transitions and stuck, dead, unguarded, stale or racy states.
argument-hint: "[optional area, feature or table to focus on]"
---

The user wants the implicit state machines in this codebase mapped and audited.

Focus: $ARGUMENTS (if empty, cover the whole project).

Apply the `implicit-state-machines` skill (load it with the Skill tool) and follow it end to end:

1. Find candidates across all four layers — database, domain types, server/back end, client/UI.
   If `graphify-out/graph.json` exists, use `graphify query` to locate writers before raw grep.
2. Classify each as persisted, derived or in-memory.
3. Trace every writer of every state to `file:line`; check initial and terminal states, error
   recovery on every path, monotonicity, unguarded writes, crash mid-transition, concurrency and
   lifetime.
4. Report in the skill's output format: the catalogue, then the findings, each traced to code.

Read-only: do not edit code, migrations or data. If a finding needs fixing, say so and offer to
hand it to the `debugger` or `coder` agent. Close with Status and Caveats (`caveats-and-status`),
naming any layer you could not inspect.
