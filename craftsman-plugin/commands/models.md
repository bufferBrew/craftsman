---
description: Choose which models the craftsman agents run on — the shipped Claude tiers, opt-in Fable, another provider behind a gateway (OpenAI, Gemini, a local model), or an export of the agents and skills to Codex CLI.
argument-hint: "[list | show | set <preset> [--deep M --balanced M --fast M] | reset | env | export codex]"
---

Every craftsman agent belongs to one of three tiers, set by the comment on its `model:` line:

| Tier | Agents | Shipped model |
|---|---|---|
| deep | orchestrator, coder, debugger, refactor-agent, security, requirements-analyst, ui-designer | `opus` |
| balanced | tester, docs-writer, release-prep, dependency-auditor, cicd-debugger | `sonnet` |
| fast | planner, reviewer, researcher | `haiku` |

A profile maps the three tiers to models. The scripts live in `${CLAUDE_PLUGIN_ROOT}/scripts/`.

Arguments: $ARGUMENTS

## With no arguments

Run `"${CLAUDE_PLUGIN_ROOT}/scripts/craftsman-models" show` and `... list`, print both, and ask
which preset the user wants. Change nothing until they pick one.

## `list`, `show`, `env`

Run `craftsman-models <subcommand>` and print its output as-is.

## `set <preset> [--deep M] [--balanced M] [--fast M]`

1. Say what will change: the preset's tier → model mapping, and that it rewrites the agent files in
   the installed plugin and saves the choice to `~/.claude/craftsman/models.conf`.
2. For `claude-fable`, say it is opt-in: Fable costs more than Opus and needs Fable access on the
   account. For `openai`, `gemini`, or any non-Claude model, say that Claude Code can only reach
   those through an Anthropic-compatible gateway (LiteLLM, OpenRouter, a Codex router, Ollama),
   which the user has to run and point Claude Code at.
3. Ask **y/n**. On `y`, run `craftsman-models set ...` with the user's arguments.
4. For a gateway preset, run `craftsman-models env` and show the env block. Offer to add it to
   `~/.claude/settings.json` (a separate **y/n**): add only the `ANTHROPIC_*` model keys and, if the
   user gives one, `ANTHROPIC_BASE_URL`. Never write a token or key into settings — tell the user
   to export `ANTHROPIC_AUTH_TOKEN` in their shell profile instead.
5. Tell the user the agents switch at the start of the next session.

If the script refuses because the plugin is a git checkout (`--plugin-dir` development), explain
that and only pass `--allow-git` if the user asks for it.

## `reset`

Ask **y/n**, then run `craftsman-models reset`. If you added model keys to `settings.json` earlier,
offer to remove them too.

## `export codex [--deep M --balanced M --fast M]`

Installs craftsman for OpenAI's Codex CLI: each agent becomes a Codex custom agent
(`~/.codex/agents/craftsman_<name>.toml`, model and reasoning effort from its tier, a read-only
sandbox unless it can edit files) and each skill is copied to `~/.agents/skills/`. Defaults to
`gpt-6-astra` / `gpt-6.1-sol` / `gpt-6-luna`.

1. Run `"${CLAUDE_PLUGIN_ROOT}/scripts/craftsman-export" codex --dry-run` with the user's flags and
   show the file list.
2. Ask **y/n**. On `y`, run it without `--dry-run`.
3. Say what doesn't carry over: hooks and slash commands have no Codex equivalent, and the agent
   prompts still mention Claude Code tools such as Skill and Agent. `craftsman-export codex
   --uninstall` removes everything the export wrote.

The model names in the presets are a snapshot. If the user names newer models, pass them with
`--deep` / `--balanced` / `--fast` rather than arguing for the preset.
