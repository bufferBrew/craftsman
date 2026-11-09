---
name: craftsman-workflow
description: Run the Craftsman pipeline when asked to orchestrate engineering work end to end. Routes specialists, verifies outcomes, and resumes interrupted runs.
---

# Craftsman workflow

Run the workflow in the main session so it can coordinate specialists and resolve user decisions.
Respect the host's current tool availability, permissions, and delegation rules.

- In Claude Code, use `Agent` with the installed `craftsman:<role>` agent when available.
- In Codex, use native subagent dispatch with the installed `craftsman_<role>` custom agent
  when available. Convert hyphens in the role name to underscores.
- On other hosts, map roles to their available agents. If dispatch or the specialist is
  unavailable, the main session can apply the role sequentially using its existing permissions.
  If running as a coordinator subagent without dispatch, hand the plan back to the caller.
  Record which checks lacked an independent reviewer. Release and security gates still apply.

## Define the work

Read the applicable project instructions and locate declared build, test, and preview commands.
Restate the requested outcome, the scope, and how to observe success. For an underspecified feature
or greenfield refactor, use `ideation-first` in the main session and carry its scope brief into
planning. Use an existing requirements spec when supplied. Follow `smallest-change-first` for
scope and dependency decisions. Pass the project's shell syntax and documented commands to the
specialist that will run them.

Choose the smallest pipeline that covers the task. Use `ui-designer` for interface implementation.
For mixed UI and logic, complete shared logic with `coder` before interface work. Run independent
phases in parallel only when at most one writes to the shared checkout. Give each writer explicit
file ownership. When a host uses separate worktrees, verify the integrated diff in the checkout
that will be delivered.

| Work | Default sequence |
|---|---|
| Small, well-understood change | One implementer and a focused check. In Claude Code, `/craftsman:quick` is the shortcut. |
| Feature | `planner` → implementer → `tester` → `reviewer`. Add `researcher` for unknown APIs or `docs-writer` for public API changes. |
| Bug | `debugger` → implementer → `tester` → `reviewer`. Start with a reproduction and root cause. Consult known issues, environment quirks, and the graphify skill when applicable. |
| Refactor | `planner` → `refactor-agent` → `reviewer` → `tester`. Capture the behavior baseline before editing. |
| Test, docs, or research | `tester`, `docs-writer`, or `researcher`, respectively. |
| Security audit | `security`, followed by `docs-writer` when documentation is needed. |
| Release | `security` → `release-prep`. Require the security result before starting release prep. |
| Dependency upgrade | `dependency-auditor` → `coder` → `tester` → `security`. |
| CI failure | `cicd-debugger` → `reviewer` for diagnosis and review. Route an authorized fix through the bug workflow. |

## Dispatch and verify

Give each specialist the immediate outcome, relevant paths and constraints, prior decisions or
evidence it needs, permitted writes, and the check that will determine whether the phase passes.
Link to relevant artifacts instead of forwarding full transcripts. Use the returned handoff as
input to the gate. Require it to include:

- **Status** as PASS, FAIL, or BLOCKED, with the changed files.
- **Check and result** with the exact command, exit status, and relevant output, or the steps
  taken and observed result for a runtime check. For a read-only phase, include the source, file,
  or finding.
- **Evidence location** when available, such as a test log, trace, screenshot, or diff. Identify
  the checkout or candidate state when it matters to later phases.
- **Gaps** covering assumptions, unavailable checks, and blockers.

Check actual tool results and artifacts when accessible. A status label cannot substitute for
evidence. Apply the gate appropriate to the phase:

- **Plan and diagnosis.** A plan names ordered, verifiable steps and the files or surfaces involved.
  A bug diagnosis includes a reproduction, root cause, and a targeted check for the fix.
- **Implementation and tests.** Verify the affected behavior in the current checkout. For bugs,
  show the regression check fail before the fix and pass after. If the baseline cannot be
  reproduced, record the reason and leave that comparison unverified. For UI, use the runtime
  checks in `ui-craft` where available.
- **Review.** Review the candidate diff against the agreed criteria. Provide the reviewer the
  diff, expected behavior, and reproduction instructions. Resolve high and critical findings
  before passing the gate unless an authorized exception is documented.
- **Security and release.** Require a passing security result. A conditional pass must name the
  conditions and show they are met or accepted by the appropriate owner before release prep.
  Release prep must report readiness. A blocked or skipped required check prevents a pass.
- **Read-only specialists.** Check the conclusion against the sources, project versions, and
  original question. Read-only work can pass without a build.

## Repair and resume

Repair a failed gate at most twice. First target the specific failure with fresh context.
For a second attempt, change the approach using the evidence. Escalate to diagnosis for a
build or test failure, or to planning when review exposes a design problem. Stop sooner if the
required permission, input, or tool is unavailable. After the second failed repair, report the
failed check, actual result, and what would unblock it. Rerun any affected gates after edits,
including review when the reviewed diff has changed.

For work that spans sessions or context compaction, update an existing task tracker or designated
handoff artifact at phase boundaries. Record scope, checkout and changed paths, last passing gate
with its evidence, repair counts, and the next pending step. Use the session's plan or handoff
summary when there is no designated artifact. On resume, confirm the checkout and working tree
before trusting a checkpoint. Keep credentials and raw sensitive output out of handoffs.

## Close the run

Summarize the outcome, phases run, changed files, verification evidence, and remaining gaps.
Use `caveats-and-status` to distinguish observed results from assumptions. Follow `commit-craft`
for requested Git actions. Report unavailable tools and fallbacks only where they affected
verification or independence.
