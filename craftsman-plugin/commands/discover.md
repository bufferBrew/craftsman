---
description: Turn a vague idea into concrete requirements — a codebase-grounded question interview ending in a numbered, testable spec.
argument-hint: <the vague feature idea or request to pin down>
---

The user has an idea that isn't specified well enough to plan yet. This runs the `ideation-first`
skill's **deep mode**: a read-only agent reads the codebase and drafts the questions the request
leaves unanswered, then you conduct the interview here and produce a numbered requirements spec.

Request: $ARGUMENTS

This runs in the **main thread**, not as a subagent, and that is the whole point — an interview needs
back-and-forth with the user, and a subagent gets one cold prompt and returns one result. Only the
question-drafting half is delegated.

1. **Check it's actually underspecified.** If the goal, boundaries, and done-condition are already
   clear, say so and stop — point the user at `/craftsman:orchestrate` instead. Interrogating a clear
   request wastes their time, and this command is easy to reach for by reflex.

2. **Dispatch `requirements-analyst`** (one `Agent` call, `subagent_type: requirements-analyst`) with
   the request and enough context to find the right code. It starts cold, so include the request
   verbatim and the project root. Read back its dossier: prior art, detected constraints, candidate
   questions with `file:line` evidence, and an assumption default per question.

   Note which questions it says the code *already* answers — those are constraints to state, not
   questions to ask.

3. **Read `${CLAUDE_PLUGIN_ROOT}/skills/ideation-first/SKILL.md`** and follow its deep process.

4. **Interview in 3–4 rounds of 2–4 related questions**, using `AskUserQuestion` so each is a click
   rather than an essay. Sequence the rounds — purpose and scope first, then behavior and
   integration, then non-functional and acceptance criteria — so later rounds adapt to earlier
   answers. Do not batch every question at once; that defeats the sequencing.

   When the user says "you decide" or "don't know": take the analyst's assumption default, record it
   under **Assumptions**, and move on. Never stall the interview on a declined question.

5. **Hold the scope while expanding the questions.** Ask about error states, empty states, migration,
   offline, concurrency — then still recommend the *smallest* build that satisfies the request.
   Everything surfaced but not agreed goes under **Out of scope**, recorded rather than built. A deep
   interview should end with the same small scope as a quick one, held with more confidence and a
   longer out-of-scope list.

6. **Propose the spec, then write it.** Show the full content and the path
   (`docs/requirements/<slug>.md` by default, redirectable) and wait for explicit confirmation before
   writing anything. Never create the file or its parent directory unprompted. Number every
   requirement `R1`, `R2`, … and give each an acceptance criterion — that numbering is what lets
   `tester` and `reviewer` trace coverage back to a requirement later.

7. **Emit the Scope brief block inline as well**, including its `Spec:` line. The spec file is for
   humans; the brief is the handoff `planner` and `orchestrator` consume, and the orchestrator's
   ideation gate checks for it.

8. **Hand off.** Close by telling the user they can now run `/craftsman:orchestrate` (or
   `@craftsman:orchestrator` with the brief pasted in, since a subagent can't see this conversation).

Constraints: never write code or implement anything here — this command settles the *what*, and the
planner and coder handle the *how* afterwards. Never write the spec, or any other file, without
showing the content and getting confirmation first.
