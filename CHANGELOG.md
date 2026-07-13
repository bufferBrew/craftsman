# Changelog

All notable changes to the craftsman plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Version numbers track `.claude-plugin/plugin.json` (kept in sync with the root
`marketplace.json`).

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
