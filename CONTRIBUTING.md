# Contributing to craftsman

Thanks for your interest. Small, focused PRs are the house style — the plugin itself enforces
minimal diffs, and so does its repo.

## Repo layout

```
.claude-plugin/marketplace.json   Marketplace manifest (this repo is its own marketplace)
craftsman-plugin/                 The plugin itself
├── .claude-plugin/plugin.json    Plugin manifest (version lives here)
├── agents/                       One .md per agent (YAML frontmatter + system prompt)
├── skills/<name>/SKILL.md        One directory per skill
├── commands/                     /craftsman:init and /craftsman:quick
└── hooks/                        hooks.json + bash scripts + run-hook.cmd dispatcher
craftsman-testbed/                Fixture project for manual testing
.github/workflows/validate.yml    CI: manifest, frontmatter, and hook-syntax checks
```

## Try your changes locally

Load your working copy into a single session without installing anything:

```
claude --plugin-dir ./craftsman-plugin
```

Then exercise the piece you changed (invoke the agent, run the command, trigger the hook) against
`craftsman-testbed/` or any scratch project.

## Validate before committing

```
claude plugin validate --strict ./craftsman-plugin
```

This is non-negotiable: broken YAML frontmatter does **not** error at runtime — it silently drops
all metadata (tools, model, description), disabling the component in ways that are hard to notice.
The most common cause is an unquoted `description:` containing a bare colon later in the line.

CI (`validate.yml`) additionally checks that:

- all JSON manifests parse and `plugin.json` / `marketplace.json` versions match,
- every agent has `name`, `description`, `tools`, and `model` in its frontmatter,
- every skill has `name` and `description`; every command has `description`,
- hook scripts pass `bash -n`.

## Adding a component

- **Agent** — new file in `agents/` with frontmatter (`name`, `description`, `tools`, `model`).
  Use model aliases (`opus` / `sonnet` / `haiku`), never pinned dated model IDs. Keep tool grants
  minimal (read-only agents get no Edit/Write). Add a row to the plugin README's Agents reference
  and, if the orchestrator should route to it, update the orchestrator's pipeline table.
- **Skill** — new directory `skills/<name>/SKILL.md`. The `description` must state *when* the
  skill applies, not just what it does. Add a row to the Skills reference.
- **Hook** — hook scripts are bash, wired through `hooks/hooks.json` and dispatched by
  `run-hook.cmd`. Script names must be **extensionless** (a `.sh` suffix triggers Claude Code's
  Windows auto-prepend and breaks dispatch). Hooks must degrade silently when their dependencies
  (bash, python) are missing.

### Editing `run-hook.cmd`

It's a polyglot file — a CMD batch block wrapped in a bash no-op heredoc — so it must stay valid
under **both** interpreters. Test it via actual `cmd.exe` invocation, not just bash. From Git
Bash, use `cmd.exe //c '...'` (double slash — a single `/c` gets mangled by MSYS path conversion).

## Versioning and changelog

- Bump `version` in `craftsman-plugin/.claude-plugin/plugin.json` **and** the matching entry in
  `.claude-plugin/marketplace.json` — CI fails if they drift.
- Add a [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) entry to `CHANGELOG.md` under the
  new version.

The `KNOWN_ISSUES.md` and `environment-quirks.md` file formats are considered stable as of v0.5.x.
If a future version changes either format in a breaking way, that change will be called out
explicitly in `CHANGELOG.md`. No migration tooling exists yet because no breaking change has
occurred — existing files in the current format continue to work with the current skills and agents
without modification.

## Commits and PRs

The repo follows its own `commit-craft` skill: atomic commits, imperative ~50-character subject,
a body that explains *why*, one logical change per commit. For PRs: keep them small, describe
what/why/how it was tested, and make sure `validate.yml` is green.
