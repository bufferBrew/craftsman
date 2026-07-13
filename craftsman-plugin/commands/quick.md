---
description: Route a small, explicitly-scoped change straight to the coder agent, skipping the full plan/test/review pipeline.
argument-hint: <description of the small change>
---

The user wants a small, explicitly-scoped change made quickly, without the overhead of the full
orchestrator pipeline (no separate planner/tester/reviewer pass). This is for changes genuinely
scoped to one small, well-understood edit — typo fixes, one-line logic changes, small obvious bug
fixes — not a substitute for proper process on anything bigger.

Request: $ARGUMENTS

Do this directly, following the `coder` agent's principles even though you are not dispatching to
it as a separate subagent call:

1. Read the relevant file(s) before editing.
2. Follow the `smallest-change-first` skill: don't add anything beyond the literal request; if
   satisfying it turns out to need more than a small, well-understood edit, say so and stop rather
   than forcing it — this command is for genuinely small changes, not a shortcut around planning
   a bigger one.
3. If this reads as a bug fix rather than a small feature tweak, still establish root cause
   before changing anything — "quick" means skipping
   pipeline overhead, not skipping root-cause investigation. Check
   `~/.claude/craftsman-memory/environment-quirks.md` for a known fix before retrying anything that
   might have failed before. If the project has `graphify-out/graph.json`, use the
   `graphify-recurring-bugs` skill during investigation.
4. Make the change.
5. Run the project's declared build/verify command (from its `CLAUDE.md`; ask if none is declared
   — do not guess).
6. If you take a deliberate shortcut, log it via the `logging-tradeoffs` skill rather than leaving
   a silent TODO.
7. Close with the `caveats-and-status` skill's Caveats & status section.

Never add a file, dependency, or scope beyond the literal request without asking first.
