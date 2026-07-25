---
description: Run the full craftsman pipeline on a task — classify it, select the minimal agent set, dispatch specialists, gate each stage on fresh evidence, and report.
argument-hint: <the multi-step task to run end to end>
---

The user wants a multi-step task handled end to end by the craftsman pipeline. This runs the
`orchestrator` agent's discipline **in the main thread** rather than dispatching to it as a
separate subagent call — orchestration means dispatching specialists via the `Agent` tool, and
nesting that inside a subagent is unreliable. Running here keeps dispatch on the one context where
it works, and lets you hold the interactive Q&A that the ideation gate needs.

Request: $ARGUMENTS

Read `${CLAUDE_PLUGIN_ROOT}/agents/orchestrator.md` for the full specification — classification
signals, per-type pipelines, per-agent gate criteria, and the report template. Follow it as written,
with the deviations noted above. The operational spine:

1. **Classify.** Read the project's `CLAUDE.md` (or `AGENTS.md`) once for the declared build/verify
   command and constraints. Restate the request in one sentence — the literal ask. If you catch
   yourself writing "and also…", that belongs under **Out of scope** on the report, not in the
   pipeline. Pick one task type: `quick`, `feature`, `bugfix`, `refactor`, `testing`,
   `documentation`, `security`, `release`, `dependency`, `cicd`, `research`. Mark the task
   UI-flavored if it centers on user-facing interface work, which swaps `coder` → `ui-designer`.

2. **New-dependency stop.** If the task appears to need a library, plugin, or file the project's
   `CLAUDE.md` doesn't already sanction, stop and ask before dispatching anyone.

3. **Ideation gate.** For a `feature` or greenfield `refactor` that is underspecified — goal,
   boundaries, or success criteria open to interpretation — run the `craftsman:ideation-first`
   skill *first* and carry its Scope brief verbatim into the planner's prompt. Unlike the
   orchestrator subagent, which must bounce this back to its caller, you can hold that conversation
   directly. Well-specified requests skip it.

4. **Select the minimal pipeline** for the task type. Do not add agents the task doesn't require —
   more agents means more latency and noise. Parallel dispatch means multiple `Agent` calls in a
   single message, and is allowed only when the agents are independent **and at most one writes
   files**. Never run two of `coder` / `ui-designer` / `refactor-agent` / `tester` concurrently.

5. **Dispatch each specialist** with a self-contained prompt — each starts cold, so include the
   exact task, relevant file paths, prior agents' output, the project's constraints, and the
   correct shell syntax for build commands. End every dispatch prompt with the handoff contract:

   > Close your response with exactly this block:
   > ```
   > STATUS: PASS | FAIL | BLOCKED
   > FILES CHANGED: <repo-relative paths, or "none">
   > VERIFIED BY: <exact command run, or "not run — read-only">
   > EVIDENCE: <verbatim result line, e.g. "BUILD SUCCESSFUL in 42s" / "47 tests, 0 failures">
   > CAVEATS: <what you did not do, assumed, or could not verify>
   > ```

6. **Gate against that block, not the agent's prose.** A missing, vague, or
   reconstructed-from-memory block is a gate failure — an agent that cannot show what it ran did
   not verify anything. Never infer a passing build from an agent's confidence. On a `bugfix`, the
   regression test must be shown to fail before the fix and pass after; one that passes both ways
   proves nothing.

7. **Repair at most twice per gate, escalating.** Attempt 1: same agent, more information (previous
   output verbatim, plus the suspected cause named explicitly). Attempt 2: change the agent —
   build/test failure routes to `debugger` for a root cause, review findings route to `planner` to
   re-plan, and *then* back to the implementer. If the gate fails twice, stop and report the
   blocker with the exact failing command and its output. Never quietly relax a gate.

8. **Report** using the `## Orchestrator Report` template, including the `Files changed` and
   `Verification run` lines and the closing Status / Caveats sections.

Constraints: never write or edit code yourself — delegate to `coder` / `ui-designer` /
`refactor-agent`. Never commit, push, branch, or open a PR unless the user explicitly asked;
finishing a pipeline is not permission to commit. Never let an agent create a new project file
without showing the proposed content and getting confirmation first. The security gate is mandatory
before `release-prep`.

If the request is genuinely one small, well-understood edit, say so and use `/craftsman:quick`
instead of paying full-pipeline cost.
