---
name: ideation-first
description: "Use before planning a new feature or greenfield refactor whose requirements aren't yet pinned down — clarifies intent through questions and ends with a scope brief the planner can build on. Runs at two depths: quick (3–5 questions, the default) and deep (a full requirements interview producing a numbered spec, used by /craftsman:discover or when asked for thorough requirements)."
---

# Ideation First

## Overview

Planning against guessed requirements wastes work. The planner turns a request into ordered steps —
but if the request itself is vague, every step is built on a guess, and the further the pipeline
runs, the more expensive that guess is to unwind. This skill settles the *what* before anyone plans
the *how*.

**Core principle:** clarify the what before planning the how.

## When this applies

A request for a **new capability, feature, or greenfield refactor whose requirements aren't pinned
down** — the goal, the boundaries, or the success criteria are open to interpretation. Signals:
"build a … screen", "add … support", "let users …", "we need something that …" with no spec.

## When to skip

- **Well-specified requests** — the goal, inputs, and done-condition are already unambiguous. Don't
  interrogate when the ask is clear; go straight to planning.
- **`quick` one-liners** — typo fixes, obvious small edits. Ideation is overhead here.
- **`bugfix`** — bugs get root-cause investigation first via the `debugger`, not requirements
  clarification. The "what" is already defined (make the broken thing work).

If you find yourself asking questions whose answers you already have, stop — you're past the point
this skill is for.

## Two depths

| | **Quick** (default) | **Deep** |
|---|---|---|
| When | Any underspecified feature; the model routes here on its own | `/craftsman:discover`, or the user asks for thorough/complete requirements |
| Questions | 3–5, one per turn | 10–20, batched into 3–4 rounds |
| Grounding | Whatever context you already have | A `requirements-analyst` dossier read from the codebase first |
| Output | **Scope brief** | Numbered requirements spec written to a file, **plus** the scope brief |

Quick is the default. Escalate to deep only when the request is substantially open — a whole new
surface, a feature with real integration and error-handling questions, something a three-line brief
would visibly under-serve. Deep mode on a small feature is ceremony, and ceremony is the failure mode
this skill is most likely to fall into.

## Expand the questions, bound the scope

These pull in opposite directions and both are required.

**Expand the questions.** Ask about the things the user hasn't thought about — error states, empty
states, concurrent access, migration of existing data, what happens offline. Surfacing a requirement
is free; discovering it after implementation is not.

**Bound the scope.** Surfacing a requirement is not the same as agreeing to build it. When the
request is open-ended, propose the *smallest* thing that satisfies it and confirm — don't quietly
scope in an ambitious version. Everything surfaced but not agreed goes in **Out of scope**, where it
is recorded rather than built.

This is `smallest-change-first` applied to requirements: ask broadly, build narrowly. A deep
interview that ends with a bigger scope than a quick one has failed, not succeeded — it should end
with the *same* small scope, held with more confidence and a longer out-of-scope list.

## The quick process

1. **Ask 3–5 clarifying questions, one at a time.** One question per turn — each answer informs the
   next. Cover **purpose** (what problem does this solve, for whom), **constraints** (what must it
   fit within — existing patterns, platforms, non-negotiables), and **success criteria** (how do we
   know it's done and right).
2. **Prefer the minimal interpretation** — see above.
3. **Propose 2–3 approaches** when there's a real design fork, each with its trade-off and your
   recommendation. Lead with the one you'd pick and say why.
4. **Confirm, then write the scope brief.**

## The deep process

1. **Ground the questions first.** Dispatch `@craftsman:requirements-analyst` with the request and
   read back its dossier: prior art, detected constraints, candidate questions with evidence, and an
   assumption default per question. Questions derived from code beat questions derived from a
   template — and the analyst also tells you which questions *not* to ask because the code already
   settles them.
2. **Ask in rounds, not one at a time.** Group the dossier's questions into **3–4 rounds of 2–4
   related questions**, and use `AskUserQuestion` so each is a choice rather than an essay. Sequence
   the rounds so later ones adapt to earlier answers: purpose and scope first, then behavior and
   integration, then non-functional and acceptance criteria last (they depend on everything above).

   > This is a deliberate divergence from quick mode's one-question-per-turn rule. One at a time is
   > right for 3–5 questions and punishing for fifteen. What matters is that the *rounds* are
   > sequenced — batching all fifteen at once means nothing adapts, which is the actual thing the
   > one-at-a-time rule exists to prevent.

3. **Never stall on an unknown.** "You decide", "don't know", "not sure yet" → take the analyst's
   assumption default, record it under **Assumptions** in the spec, and move on. Do not re-ask, and
   do not block the interview on a question the user has declined.
4. **Fill the categories that apply**: purpose & users, scope boundaries, data & state, error & edge
   behavior, integration & dependencies, non-functional (performance, accessibility, security,
   offline), acceptance criteria, rollout & migration. Skip a category rather than padding it.
5. **Propose the spec, confirm, then write it.** Show the full proposed content and the path, wait
   for explicit confirmation, then write. Never create the file or its directory unprompted — this is
   the same ask-before-writing rule `/craftsman:init` follows.
6. **Emit the scope brief too**, inline. The spec is the human artifact; the brief is the machine
   handoff, and the planner and orchestrator both consume it.

## The requirements spec (deep mode)

Default path: `docs/requirements/<slug>.md` in the target project. Offer it as a default the user can
redirect.

```
# <Feature> — requirements

**Context** — the problem, who's affected, what prompted this.
**Goals** — what this must achieve.
**Non-goals** — what it deliberately does not achieve.

**Requirements**
- R1 (MUST) — <one testable statement>
- R2 (SHOULD) — <one testable statement>

**Acceptance criteria**
- R1: Given <state>, when <action>, then <observable outcome>.

**Out of scope** — surfaced during the interview, deliberately not built.
**Assumptions** — questions the user declined, and the default taken for each.
**Key decisions** — choices made during the interview, and why.
```

Number every requirement (`R1`, `R2`, …) and keep each one independently testable. The numbering is
what lets `tester` and `reviewer` trace coverage back to a specific requirement — a spec written as
prose paragraphs can't be checked off.

## The scope brief

End by producing this block — at both depths. It is the hand-off to the planner; keep it compact.

```
**Scope brief**
- Goal: <one sentence>
- In scope: <bullets>
- Out of scope: <bullets — the explicit "not doing" list>
- Key decisions: <choices made during ideation + why>
- Open questions: <anything still unresolved, or "none">
- Spec: <path to the requirements spec, or "none — quick mode">
```

When routing through `@craftsman:orchestrator`, pass this brief in the invocation so the planner
receives it — a cold subagent can't see the conversation it wasn't part of. (`/craftsman:orchestrate`
and `/craftsman:discover` run in the main thread, so they already have the brief.)

## Red flags

| Thought | Reality |
|---|---|
| "I get the gist, I'll just start coding" | A gist is not an agreed scope. Confirm the what first. |
| "I'll ask all my questions at once" | Quick mode: one at a time. Deep mode: 3–4 sequenced rounds. Either way, later questions must be able to adapt to earlier answers. |
| "The request was vague, so I'll pick something ambitious" | Pick the *minimal* interpretation and confirm it. Scope creep starts here. |
| "This feature is obviously simple, skip the brief" | Simple-looking features are where unexamined assumptions cost the most. The brief can be three lines, but write it. |
| "The out-of-scope list is empty" | If nothing is out of scope, you haven't bounded anything. Name what you're deliberately not doing. |
| "Deep mode means fifteen questions, so I'll find fifteen" | Questions the code already answers are noise. Ten grounded questions beat twenty padded ones — and the analyst's dossier tells you which are which. |
| "I batched all the rounds to save time" | Then nothing adapted, and you asked round 3's questions without round 1's answers. Sequence the rounds. |
| "The user didn't know, so I'll come back to it" | Take the assumption default, record it under Assumptions, move on. A stalled interview ships nothing. |
| "The spec captures the requirements, criteria can come later" | A requirement with no acceptance criterion isn't testable, so nobody can tell whether it was met. They come from the same conversation — write them now. |
| "Deep mode surfaced more, so the scope grew" | Ask broadly, build narrowly. Extra findings belong in Out of scope, not in the build. |
