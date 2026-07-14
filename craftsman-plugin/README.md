<p align="center">
  <img src="https://raw.githubusercontent.com/bufferBrew/craftsman/main/craftsman-logo.png" alt="craftsman" width="240">
</p>

# craftsman

<p align="center">
  <a href="https://github.com/bufferBrew/craftsman/actions/workflows/validate.yml"><img src="https://github.com/bufferBrew/craftsman/actions/workflows/validate.yml/badge.svg" alt="validate"></a>
  <a href="https://github.com/bufferBrew/craftsman/blob/main/craftsman-plugin/.claude-plugin/plugin.json"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FbufferBrew%2Fcraftsman%2Fmain%2Fcraftsman-plugin%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=blue" alt="version"></a>
  <a href="https://code.claude.com/docs/en/plugin-marketplaces"><img src="https://img.shields.io/badge/Claude%20Code-plugin-d97757" alt="Claude Code plugin"></a>
  <a href="https://github.com/bufferBrew/craftsman/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

A Claude Code plugin that makes engineering discipline the default: the smallest correct change,
no fix without a root cause, and an honest report of what was actually verified. Ten agents, seven
skills, two slash commands, and a cross-platform hook system.

## Why craftsman

| Without | With craftsman |
|---|---|
| "Fixed it" — plus an uninvited refactor of three other files | **Minimal-diff coding** — the smallest change that solves the problem; anything beyond the request needs your OK first |
| Symptom patched; the same bug returns next month under a new name | **Root-cause debugging** — no fix without an established root cause, and a [graphify](https://pypi.org/project/graphifyy/) knowledge graph catches *recurring* bugs before they're filed as new ones |
| The same OS/shell quirk rediscovered by trial and error every session | **Environment-quirk memory** — discovered once, recorded in a stable file, never re-derived |
| Scaffolding that writes files you didn't ask for | **Ask-before-writing setup** — `/craftsman:init` proposes exact file content and waits for confirmation, every run |
| "Done!" (the build never actually ran) | **Honest completion** — every nontrivial task ends with a Caveats & status block: Verified / Assumed / Not covered |
| Guessing which agent to chain next | **`@orchestrator`** — classifies the task, picks the minimal pipeline, and gates each stage on fresh evidence, not claims |

## 30-second start

```
claude plugin marketplace add bufferBrew/craftsman
claude plugin install craftsman@craftsman
```

Restart Claude Code (or start a new session), then in any project:

1. **`/craftsman:init`** — detects your stack, proposes a project `CLAUDE.md` (with the real
   build/verify command) and a `KNOWN_ISSUES.md` template, and asks before writing anything.
2. **`@orchestrator <task>`** for multi-step work; **`/craftsman:quick <change>`** for one-line
   fixes.
3. When a bug comes in and the project has a graphify graph, the investigation automatically runs
   through the graph first and checks whether the bug duplicates a `KNOWN_ISSUES.md` entry.

More install options (session-only trial, local checkout) under [Installation](#installation).
Worked examples in [docs/use-cases.md](../docs/use-cases.md); contributions welcome — see
[CONTRIBUTING.md](../CONTRIBUTING.md).

## Contents

```
craftsman-plugin/
├── .claude-plugin/plugin.json    Plugin manifest
├── agents/                       Ten agents (see Agents reference)
├── skills/                       Seven skills (see Skills reference)
├── commands/
│   ├── init.md                   /craftsman:init — project scaffolder
│   └── quick.md                  /craftsman:quick — small-change fast path
└── hooks/
    ├── hooks.json                Hook wiring (SessionStart + PreToolUse)
    ├── run-hook.cmd              Polyglot dispatcher (Windows CMD + Unix bash)
    ├── session-start             Injects the plugin reminder into new sessions
    ├── pretooluse-graphify-bash  "Use graphify first" hint on grep/find Bash calls
    └── pretooluse-graphify-read  Same hint on Read/Glob of source files
```

## Requirements

- **Claude Code** with plugin support (`claude plugin --help` works).
- **Windows**: Git for Windows (the hook dispatcher looks for
  `C:\Program Files\Git\bin\bash.exe`, then `C:\Program Files (x86)\...`, then `bash` on PATH).
  If no bash is found, hooks skip silently — the rest of the plugin still works.
- **Optional**: a working `python` or `python3` on PATH. The graphify hooks use it to parse tool
  input; without it they fall back to a regex heuristic (Bash hook) or skip (Read hook).
- **Recommended**: the `graphify` CLI/skill — it powers recurring-bug detection *and* query-first
  codebase navigation. `/craftsman:init` detects whether it's installed and offers to install the
  `graphifyy` package (on explicit confirmation) if it's missing. Everything else still works
  without it.

## Installation

### Option A — session-only (try it out)

Load the plugin for a single session without installing anything, from a local checkout:

```
claude --plugin-dir ./craftsman-plugin
```

Repeatable per session; nothing is written to `~/.claude`.

### Option B — install from GitHub (recommended)

This repository is itself a marketplace (`.claude-plugin/marketplace.json` at the repo root lists
the plugin with `"source": "./craftsman-plugin"`). Install directly:

```
claude plugin marketplace add bufferBrew/craftsman
claude plugin install craftsman@craftsman
```

Or from inside a session: `/plugin marketplace add bufferBrew/craftsman` then
`/plugin install craftsman@craftsman`.

Restart Claude Code (or start a new session) after installing. Verify with `claude plugin list`
and inspect the loaded components with `claude plugin details craftsman` — it should report
10 agents, 9 skills (the 7 skills plus the 2 commands), and 2 hook events (SessionStart,
PreToolUse), with an always-on cost of roughly 1.2k tokens per session.

### Option C — install from a local marketplace checkout

A marketplace is any directory (or git repo) containing `.claude-plugin/marketplace.json`. From a
local clone of this repo, add the marketplace by path and install:

```
claude plugin marketplace add ./craftsman
claude plugin install craftsman@craftsman
```

The plugin `source` in `marketplace.json` must be a **relative** path (`./...`) — an absolute path
string fails marketplace validation.

### Validate after any change

```
claude plugin validate --strict ./craftsman-plugin
```

This checks the manifest and the YAML frontmatter of every agent, skill, and command. Run it
before committing — broken frontmatter does not error at runtime, it **silently drops all
metadata** (tools, model, description), which disables the component in ways that are hard to
notice.

## Commands reference

### `/craftsman:init`

Project-level setup. Explicit and user-triggered — never runs on session start, never writes
without confirmation.

**Existing project (marker files found):**
1. Detects the stack from ~25 marker patterns (Gradle/Android, Maven/Spring, npm/yarn/pnpm,
   Poetry/pip/Django, Cargo, Go, Flutter, .NET, Ruby, PHP, Swift, CMake/Make, Deno, Elixir,
   Docker-only, monorepo).
2. Resolves the **real** build/verify command, not the generic default — priority order:
   CI config (`.github/workflows/*.yml` etc.) → `README.md`/`CONTRIBUTING.md` →
   `package.json` scripts (or Makefile targets / `pyproject.toml` tool config) → table default.
3. Checks for an existing issue log under another name (`TODO.md`, `ISSUES.md`, `BACKLOG.md`)
   and offers to adopt it instead of creating a duplicate `KNOWN_ISSUES.md`.

**New/empty project (no markers):** asks which stack you intend to use — it does not guess and
does not invent a `package.json` for you.

**Both paths:** shows the exact proposed file content, asks, and writes only on explicit yes.
Never overwrites an existing `CLAUDE.md` (offers to append instead, still asking). It also detects
graphify's status: if a graph exists it notes graphify is active; if graphify is installed but
unbuilt, the proposed `CLAUDE.md` notes that running `graphify .` would enable graph-aware
debugging (nothing runs it automatically); if graphify is missing entirely, it recommends it and
offers to install the `graphifyy` package — running the install only on explicit confirmation.

### `/craftsman:quick <description of the small change>`

Fast path for genuinely small, well-understood edits — typo fixes, one-line logic changes, small
obvious bugs. Skips the orchestrator pipeline (no separate planner/tester/reviewer pass) but keeps
the discipline:

- Still reads before editing, still follows `smallest-change-first`.
- Bug-shaped requests still get root-cause investigation (and the graphify check, if a graph
  exists) — "quick" skips pipeline overhead, not rigor.
- Still runs the project's declared build/verify command.
- Still ends with the Caveats & status section.
- If the change turns out bigger than it looked, it says so and stops instead of forcing it.

You don't have to remember the command: `@orchestrator` also recognizes small-change wording
("quick fix", "just", "trivial", "one-liner") and routes to the same path itself.

## Agents reference

Invoke any agent with `@<name> <task>` or let `@orchestrator` route for you.

| Agent | Model | Writes files? | Use for |
|---|---|---|---|
| `orchestrator` | Opus | No (delegates) | Any multi-step task; picks the smallest pipeline, enforces gates, max 2 repairs per gate, structured report |
| `planner` | Haiku | No | Decomposing a feature/bug into ordered steps before coding |
| `coder` | Opus | Yes | The implementation itself — minimal diff, runs the build, asks before adding anything extra |
| `debugger` | Opus | No (+ Bash to reproduce) | Bug diagnosis — reproduces, traces to root cause (superpowers 4-phase method), hands off a fix location + reproduction recipe + failing-test spec to `coder`; graphify/quirks/KNOWN_ISSUES aware |
| `reviewer` | Haiku | No | CRITICAL/HIGH/MEDIUM/LOW review; also flags hand-rolled logic that duplicates stdlib/dependencies, and cross-checks `KNOWN_ISSUES.md` |
| `tester` | Sonnet | Test files only | Coverage gaps, regression tests, runs the suite |
| `security` | Opus | No | Secrets grep, git-history scan, OWASP, Android/Spring/CI-CD/agent checks; PASS/FAIL verdict |
| `release-prep` | Sonnet | No | Pre-release checklist; "Ready to ship: YES/NO" |
| `researcher` | Haiku | No | Doc/API/version lookups — codebase first, then installed MCP servers, then the web |
| `docs-writer` | Sonnet | Doc files only | README/changelog/architecture notes grounded in current code |

**Orchestrator pipelines** (chosen automatically by task type):

- `quick` → `coder` alone
- `feature` → *ideation gate* (if underspecified, main-thread `ideation-first` skill produces a
  scope brief first) → `researcher?` → `planner` → `coder` → `tester` → `reviewer` → `docs-writer?`
- `bugfix` → `debugger` (read-only root-cause 4-phase method + quirks/KNOWN_ISSUES/graphify; hands
  off fix location + repro recipe) → `coder` → `tester` → `reviewer`
- `refactor` → `planner` → `coder` → `reviewer` → `tester`
- `release` → `security` → `release-prep` (security is never skipped before release)
- plus `testing`, `documentation`, `security`, `dependency`, `cicd`, `research` single/short chains

Gates between stages require **fresh evidence**, not claims — e.g. coder must show actual build
output, not say "build passes."

## Skills reference

Skills load on demand (Skill tool) and are referenced by the agents; you can also invoke them
directly.

| Skill | When it applies |
|---|---|
| `ideation-first` | Before planning a new feature or greenfield refactor whose requirements aren't pinned down. Asks 3–5 clarifying questions one at a time, then emits a **Scope brief** (Goal / In scope / Out of scope / Key decisions / Open questions) the planner builds on. Skipped for well-specified requests, `quick`, and `bugfix`. Runs in the main thread (interactive); `@orchestrator` gates on the brief's presence rather than running it itself. |
| `smallest-change-first` | Before writing any new code/file/dependency. Seven-step ladder: needs to exist? → already in codebase? → stdlib? → platform feature? → existing dependency? → one line? → only then write the minimum. Source of the "ask before anything extra" rule. |
| `logging-tradeoffs` | When taking a deliberate shortcut, investigating a possibly-logged bug, or resolving an entry. Defines the `KNOWN_ISSUES.md` format: what changed / ceiling / upgrade trigger / status. |
| `environment-memory` | Before retrying anything that failed once; after discovering an OS/shell/tool quirk. Reads/appends `~/.claude/craftsman-memory/environment-quirks.md`. |
| `caveats-and-status` | When reporting any nontrivial task complete. Fixed closing block: Verified / Assumed / Not covered. |
| `graphify-recurring-bugs` | During bug investigation **only when** `graphify-out/graph.json` exists; complete no-op otherwise. See next section. |
| `commit-craft` | Before any git commit, branch, or PR. Atomic commits; imperative ~50-char subject + why-focused body + `Co-Authored-By` trailer; branch naming; history hygiene (squash fixups, `--force-with-lease`); PR conventions (small, what/why/testing, `Closes #`, Claude Code trailer, green CI). Only commits/pushes/PRs when asked; branches first off `main`. |

## Graphify integration (recurring bugs)

If a project has a built graph (`graphify-out/graph.json`):

1. **Investigation**: `graphify query "<symptom>"` runs before raw grep — cheaper in tokens and
   surfaces related callers/dependents a stack trace misses. Other call sites of an implicated
   shared function are treated as suspects too.
2. **Dedup before filing / recall a past fix**: before adding a new `KNOWN_ISSUES.md` entry,
   `graphify path "<new bug symbol>" "<existing entry symbol>"` is run against existing entries. A
   short path means the "new" bug is likely the same root cause resurfacing elsewhere — that gets
   surfaced for you to judge, never auto-merged. When the match lands on a **resolved** entry, its
   recorded one-line fix is a known-good fix to reuse rather than re-derive — graphify is the
   linker that recalls it; `KNOWN_ISSUES.md` is where the fix itself lives.
3. **After the fix**: `graphify update .` (incremental, AST-only, no LLM cost) keeps the graph
   current.
4. **Hooks**: any grep/find Bash call or Read/Glob of a source file in a graphed project gets an
   injected reminder to query the graph first. The hooks are project-agnostic (they check for
   `graphify-out/graph.json` relative to the working directory) and fire correctly on Windows via
   the `run-hook.cmd` dispatcher.

Building a graph is never triggered automatically — run `graphify .` yourself when you want one.
`/craftsman:init` will surface graphify (and offer to install the `graphifyy` package if it's
missing, on confirmation), but graph *builds* always remain user-triggered.

## Persistent memory, Obsidian, Notion

- **`~/.claude/craftsman-memory/environment-quirks.md`** — flat, append-only, one line per quirk:
  `<symptom> → <fix> (discovered: <date>, context: <where>)`. Lives outside the plugin install
  directory so plugin updates never wipe it. Read in full when relevant; kept short by design.
- **Obsidian**: the whole `~/.claude/craftsman-memory/` folder *is* an Obsidian vault as-is — plain
  markdown, no export, sync, or config step. In Obsidian, **Open folder as vault** and point it at
  `~/.claude/craftsman-memory/`. You then get full-text search, backlinks, and the graph view over
  your accumulated quirks — plus a real editor instead of scrolling one flat file — while Claude Code
  keeps writing the same files live underneath. (Unrelated to graphify's own `--obsidian`
  codebase-graph export, which is a separate feature.)
- **Notion**: mirroring is **opt-in only** — an entry goes to Notion only when you explicitly ask,
  or when closing out an entry you flagged as important. Nothing syncs automatically.

## Troubleshooting

**An agent/skill/command behaves as if its config is missing.** Its YAML frontmatter probably
failed to parse — most commonly an unquoted `description:` containing a bare colon later in the
line. All metadata is silently dropped in that case. Run
`claude plugin validate --strict <plugin path>` to catch it.

**Hooks do nothing on Windows.** The dispatcher exits silently if it can't find bash — install
Git for Windows at the standard path or put `bash` on PATH. Also confirm the hook script names in
`hooks.json` are **extensionless** (a `.sh` suffix triggers Claude Code's Windows auto-prepend and
breaks dispatch).

**Graphify Read-hook never fires.** It needs a working Python. Note the Windows trap: `python3`
may be on PATH as a non-functional Microsoft Store stub — the hooks handle this by test-running
each candidate, but if neither `python3` nor `python` actually works, the Read hook skips
(by design, rather than guessing).

**Testing hooks manually from Git Bash:** use `cmd.exe //c '...'` (double slash) — a single `/c`
gets mangled by MSYS path conversion and cmd.exe opens interactively instead.

Known machine-specific quirks are collected in
`~/.claude/craftsman-memory/environment-quirks.md` — check there first when something
environment-shaped fails.

## Development

- Edit → `claude plugin validate --strict .` → test against a testbed fixture → commit.
- Hook scripts are bash with a `bash -n` syntax check; `run-hook.cmd` is polyglot (CMD batch block
  wrapped in a bash no-op heredoc) — edit it only with both interpreters in mind, and re-test via
  actual `cmd.exe` invocation, not just bash.
- Bump `version` in `.claude-plugin/plugin.json` on changes; `claude plugin update craftsman`
  picks up new versions for marketplace installs.

## License

MIT
