# Changelog

All notable changes to the craftsman plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Version numbers track `.claude-plugin/plugin.json` (kept in sync with the root
`marketplace.json`).

## [0.11.0] - 2026-08-12

### Added
- **Bundled MCP servers** (`craftsman-plugin/.mcp.json`): `figma` (the hosted remote server) and
  `chrome-devtools` (Google's official `chrome-devtools-mcp`). Both serve the UI surface —
  `ui-designer` and `ui-craft` — and both are opt-in, going through Claude Code's per-server
  approval like any project `.mcp.json`. Declining both leaves every agent, skill and command
  working; nothing hard-depends on them.

  `chrome-devtools` in particular closes the gap `ui-designer` has always had to declare under
  "Not covered": a build check proves a UI compiles, not that it renders, and hover/focus states
  only exist in a live browser. See the plugin README's *MCP servers* section for the security
  notes on each (Figma OAuth scope; Chrome profile isolation).

### Changed
- `ui-craft` gained four sections covering failure modes that pass visual review and still ship
  broken. All four came out of an interaction audit of a real Flutter app, where every one of
  them was live in production code:
  - **Every control is keyboard-operable.** The skill previously said only "keyboard/focus order
    follows visual order" — which assumes the control is focusable at all. A tap handler on a
    plain container (`GestureDetector`, `onClick` on a `<div>`) is invisible to Tab traversal, so
    a shared button component built that way makes an entire app unusable without a pointer. It
    is a WCAG 2.1.1 failure that looks perfect in a screenshot. The section names the four
    properties to verify — reachable, operable, visibly focused, correctly excluded when disabled
    — and asks for a behavioral test, since none of this is visible in a diff.
  - **The four interaction states are one set.** hover / focus / pressed / disabled: define one,
    owe all four. Notes that focus is not hover, and that transparent button variants have no
    fill to darken and so need their own hover treatment.
  - **Measure the slot, not the window.** Breakpoint logic must read the container's width, not
    the viewport's. Mixing them — sizing cells from the local constraint while counting columns
    from the viewport — is what produces overflow and dead columns.
  - **Fixed extents and scaled text do not mix.** Any hardcoded height wrapping text overflows at
    the 1.5–2x text scale users actually set.

  Also under *State-driven UI*: distinguish offline from server failure (an auth rejection
  arrived over a working connection, so "check your connection" sends the user to debug the wrong
  thing), and give skeletons the same extents as the content they stand in for.
- `ui-designer` now calls out those same four checks explicitly in its **Craft** section rather
  than deferring wholesale to the skill, and its "Not covered" contract widened: contrast ratios,
  real text-scale behavior, and hover/focus appearance are all outside what a build check proves
  and must be reported as unverified.

## [0.10.0] - 2026-07-26

### Added
- `/craftsman:discover <vague idea>`: a requirements-discovery interview that turns an
  underspecified request into a numbered, testable spec. It exists because the shallow end of
  `ideation-first` was the only option — 3–5 questions and a three-line brief, with no way to invoke
  it deliberately, so a substantially open request ("build a notifications system") got the same
  treatment as a merely fuzzy one.

  The work is split across two surfaces because of a hard constraint: **a subagent cannot conduct an
  interview.** It receives one cold prompt and returns one result, which is why `orchestrator` already
  has to bounce underspecified features back to its caller. So the interview runs in the main thread
  as a command, and only the half a subagent is genuinely good at — reading the codebase — is
  delegated.
- `requirements-analyst` agent (read-only: Read/Glob/Grep, Opus): drafts the clarifying questions a
  request leaves unanswered, grounded in prior art and existing abstractions rather than a generic
  checklist. Every question carries a `file:line` or an explicit "gap" label, plus an assumption
  default so the interview never stalls on a declined question; questions the code already settles
  come back as *constraints* instead. Capped at 10–20 questions — past that, it is asking things the
  codebase already answers. It never asks the user anything itself and never writes files.

### Changed
- `ideation-first`: now runs at two depths. **Quick** is unchanged and still the default (3–5
  questions, one per turn, Scope brief). **Deep** grounds 10–20 questions in the analyst's dossier and
  asks them in **3–4 sequenced rounds of 2–4 questions** via `AskUserQuestion` — a deliberate
  divergence from the one-question-per-turn rule, which is right for five questions and punishing for
  fifteen. What the rule actually protects is that later questions adapt to earlier answers, and
  sequenced *rounds* preserve that; batching all fifteen at once does not.

  Deep mode ends by writing a numbered requirements spec (`R1`, `R2`, … each with an acceptance
  criterion, so `tester` and `reviewer` can trace coverage back to a requirement) at
  `docs/requirements/<slug>.md` — proposed, shown in full, and written only on confirmation, per the
  same ask-before-writing rule `/craftsman:init` follows. The **Scope brief** is still emitted inline
  at both depths and remains the machine handoff the planner and the orchestrator's ideation gate
  consume; the spec file is additive, and the brief gained a `Spec:` line pointing at it.

  New explicit rule: **expand the questions, bound the scope.** Deep mode raises error states, empty
  states, migration, and offline behavior — then still recommends the smallest build that satisfies
  the request, with everything surfaced but unagreed recorded under Out of scope. A deep interview
  that ends with a *bigger* scope than a quick one has failed; it should end with the same scope, held
  with more confidence and a longer out-of-scope list. Without this, deep mode would have quietly
  contradicted `smallest-change-first`.
- `orchestrator`: the ideation gate now accepts either an inline Scope brief or a path to a
  requirements spec, and instructs the planner to read the spec when one is named. Availability table
  gains `requirements-analyst`.
- `/craftsman:orchestrate`: the ideation-gate step routes substantially open requests to deep mode
  rather than a three-line brief.
- `userpromptsubmit-task-router`: the feature-shaped nudge names `/craftsman:discover` for
  substantially open requests. Still one nudge per prompt; no new `case` branch.

### Fixed
- `session-start` announced "Seven skills" and "Five commands" — both already wrong before this
  release (8 and 6), and both invisible to CI: the count validator skips any line containing
  "commands" when checking skills, and only matches the literal phrase "N slash commands" for
  commands. The whole reminder is a single line, so both slipped through every check. The skill list
  was also missing `ui-craft` and the command list was missing `/craftsman:orchestrate` — a session
  therefore started without being told two components existed.

## [0.9.0] - 2026-07-25

### Added
- `/craftsman:orchestrate <task>`: a slash command for the full pipeline. The orchestrator was the
  only major entry point without one, so it never appeared in the `/` menu — every other command
  (`init`, `quick`, `doctor`, `review`, `security`) did. It runs the orchestrator's discipline in
  the **main thread** rather than dispatching the agent as a subagent, for two reasons:
  orchestration *is* subagent dispatch and nesting that is unreliable, and the ideation gate needs
  interactive Q&A that a subagent cannot hold (as a subagent, `orchestrator` must bounce
  underspecified features back to its caller). `@craftsman:orchestrator` still works for running
  the pipeline in its own context.

### Fixed
- Agent invocation is documented as `@craftsman:<name>` throughout. Plugin agents are namespaced,
  so the bare `@<name>` form the docs taught — `@orchestrator` in both READMEs, `docs/use-cases.md`,
  and the `ideation-first` skill — matches nothing in the agent picker, making the orchestrator look
  like it wasn't installed. Note: `craftsman-demo.svg` still shows `@orchestrator` in its rendered
  terminal text; correcting it requires regenerating the asset.

## [0.8.0] - 2026-07-23

### Added
- Automatic skill-routing hooks so craftsman skills surface from task shape instead of a manual
  check. Four new event-driven hooks, all self-contained (they reference only `craftsman:*` skills
  and this plugin's own agents, never another plugin) and quiet by default (a nudge fires only on a
  real signal): `userpromptsubmit-task-router` (routes the prompt to the matching agent/skill by
  task shape — bug, feature, refactor, security, release, CI, testing, docs, version-control),
  `pretooluse-git-guard` (commit-craft hint on `git commit`/`push`/`tag` & `gh pr`),
  `pretooluse-edit-guard` (file-pattern skill hints for `KNOWN_ISSUES.md`/test/workflow files, and
  drops the session marker the close-out hook reads), and `stop-closeout` (nudges
  caveats-and-status once after real edits, then self-deletes its marker — loop-safe via both the
  marker and `stop_hook_active`).
- New hook events wired in `hooks.json`: `UserPromptSubmit` and `Stop` (previously only
  `SessionStart` + `PreToolUse`).

### Changed
- `orchestrator`: gate and repair hardening. Adds a **handoff contract** — every dispatched agent
  must close with `STATUS`/`FILES CHANGED`/`VERIFIED BY`/`EVIDENCE`/`CAVEATS`, and gates are checked
  against that block rather than the agent's prose, so a missing evidence line now fails the gate
  instead of passing on confidence. The repair loop **escalates** rather than retrying: attempt 2
  routes to a different agent (`debugger` for build/test failures, `planner` for review findings)
  before re-implementing. The parallelism rule now forbids two file-writing agents running
  concurrently (the old "different output artifacts" wording permitted it) and states that parallel
  dispatch means multiple `Agent` calls in one message. Also: one-sentence scope restatement and a
  new-dependency stop before pipeline selection, a bugfix requirement that the regression test fail
  before the fix and pass after, `Files changed` / `Verification run` lines on the report, and an
  explicit "never commit, push, branch, or open a PR unless asked" constraint.
- `session-start`: added a proactive lead-in to check `environment-quirks.md` before retrying a
  failed command, and to prefer graphify for navigation when `graphify-out/graph.json` exists.
- `run-hook.cmd`: reworded to drop the superpowers-plugin attribution — the dispatcher and the
  whole plugin depend on no other plugin being installed.
- README: new "Automatic skill routing (hooks)" section documenting the six hooks, plus the four
  routing ideas (skill chaining, parallel analysis, negative filtering, contextual caching) that
  are intentionally model/orchestrator behaviors rather than hooks.

## [0.7.0] - 2026-07-17

### Added
- `/craftsman:doctor --fix`: opt-in remediation for the three detected silent-failure conditions.
  Default (no-arg) behavior is unchanged — diagnostic only. With `--fix`, each repair is shown and
  confirmed (y/n) before it runs, then the check is re-run to verify: Git Bash via
  `winget install Git.Git` (lands on the standard path the hook dispatcher already probes, so no
  PATH edit), graphify graph via `graphify .`, and the Windows python3 Store-stub via
  `winget install Python.Python.3.12` (flagged as a partial fix — the Store app-execution alias may
  still need disabling). Falls back to manual install links where `winget` is unavailable.

## [0.6.0] - 2026-07-15

### Added
- `ui-craft` skill: framework-adaptive modern-UI discipline — design-token priority
  (`design-system/MASTER.md` from design-intelligence skills like ui-ux-pro-max → framework theme
  → existing conventions), accessibility (contrast, touch targets, semantics, focus order),
  responsive layout, state-driven UI with explicit loading/empty/error states, motion restraint.
- `ui-designer` agent: UI implementation specialist that detects the project's UI framework
  (Compose, Flutter, React/Next.js, SwiftUI, Vue, web), applies the `ui-craft` skill, and carries
  coder's minimal-diff contract. The orchestrator routes UI-flavored feature/bugfix/quick tasks
  (screens, components, styling, layout, theming) to it in the `coder` slot.

### Removed
- Android/Spring project-type tiering from the orchestrator: the Android feature/bugfix pipeline
  branches, the environment-dependent `android-feature`/`android-tester`/`compose-reviewer`
  table, and the never-created `spring-api`/`spring-reviewer`/`spring-tester` planned-agents
  table (also removed from ROADMAP.md). One stack-adaptive pipeline remains — agents defer to
  the build/verify command the project's own `CLAUDE.md` declares.

### Changed
- Security agent's Android and Spring Boot sections reframed as platform-conditional checks that
  run only when the project matches, reporting N/A otherwise.
- Tester's Bash-scope examples broadened beyond Gradle/Maven (npm, pytest, cargo, flutter),
  deferring to the project's declared test command.

## [0.5.1] - 2026-07-14

### Added
- Terminal-style demo image (`craftsman-demo.svg`) on the root README showing an orchestrator
  bugfix run end to end.
- `CONTRIBUTING.md`: local testing via `--plugin-dir`, validation requirements, component
  conventions, `run-hook.cmd` polyglot editing rules, and versioning/changelog process.
- `docs/use-cases.md`: four worked scenarios (minimal diffs, recurring-bug recall via graphify,
  ask-first scaffolding, honest completion).
- GitHub issue templates (bug report, feature request) and a Discussions contact link.

### Changed
- Restructured both READMEs to lead with the value proposition: a "Why craftsman" problem/solution
  table, a 30-second start, and status badges (CI, version, license). Reference content unchanged;
  the plugin README's Quick start section merged into the new 30-second start.

## [0.5.0] - 2026-07-14

### Added
- `commit-craft` skill: git/commit/branch/PR conventions — atomic commits, imperative subject +
  why-focused body + `Co-Authored-By` trailer, branch naming, history hygiene (squash fixups,
  `--force-with-lease`), and PR hygiene. Enforces "only commit/push/PR when asked; branch first
  off `main`."

### Changed
- `orchestrator`, `coder`, `debugger`, and `security` agents now run on `opus` (previously
  `sonnet`) for higher-capability reasoning; other agents unchanged.
- `graphify-recurring-bugs` skill and the README graphify section now frame graphify as *recall*
  of a past working fix: a `graphify path` match to a **resolved** `KNOWN_ISSUES.md` entry surfaces
  that entry's recorded fix to reuse, not only recurring-bug dedup. graphify links; `KNOWN_ISSUES.md`
  stores the fix.

### Fixed
- Reconciled stale skill counts across the plugin README, the root README, and the session-start
  hook (now consistently seven skills). The session-start hook had also been silently omitting the
  `ideation-first` skill; it now lists all seven.

## [0.4.0] - 2026-07-14

### Changed
- `debugger` is now a read-only diagnostician: it establishes root cause and hands off a fix
  location, reproduction recipe, and failing-test spec to `coder` instead of editing code itself.
- Every agent's `model` field uses an alias (`sonnet` / `haiku`) instead of a pinned dated model
  ID, so agents survive model version turnover without a coordinated edit.
- `coder`'s Bash scope explicitly permits `graphify update .` after a fix, so the post-fix graph
  refresh the `graphify-recurring-bugs` skill prescribes is actually runnable.

### Added
- GitHub Actions workflow (`.github/workflows/validate.yml`) that validates JSON manifests, checks
  that `plugin.json` and `marketplace.json` versions match, parses the YAML frontmatter of every
  agent/skill/command, and syntax-checks the hook scripts.

### Fixed
- The graphify PreToolUse hint now also covers the `Grep` tool, and no longer fires when reading
  documentation files (`.md`/`.rst`/`.txt`/`.mdx`) such as `CLAUDE.md`, `KNOWN_ISSUES.md`, or
  `README.md`, which agents are required to read directly.
- Orchestrator no longer asserts the Android agents (`android-feature`, `android-tester`,
  `compose-reviewer`) are always available; they are now marked environment-dependent with
  `coder`/`tester`/`reviewer` fallbacks.
- README graphify link now points to the `graphifyy` package instead of the Claude Code repo, and
  the logo uses an absolute URL so it renders outside the repo root.
- Bash graphify hook now checks command output is non-empty (`[ -n "$out" ]`) rather than merely
  set.

## [0.3.0]

### Added
- `ideation-first` skill: turns an underspecified feature or greenfield-refactor request into a
  Scope brief (Goal / In scope / Out of scope / Key decisions / Open questions) before planning.
- Expanded Obsidian documentation for the `~/.claude/craftsman-memory/` vault.

### Fixed
- Corrected a stale agent count in the root README (9 → 10).

## [0.2.0]

### Added
- craftsman logo on the README landing pages.
- `.gitattributes` normalizing hook scripts to LF line endings.

### Changed
- Synced the plugin version across `plugin.json` and `marketplace.json`.

## [0.1.0]

### Added
- Initial public release: the full agent set, the discipline skills,
  `/craftsman:init` and `/craftsman:quick` commands, and the cross-platform graphify hook system.
