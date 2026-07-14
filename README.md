<p align="center">
  <img src="./craftsman-logo.png" alt="craftsman" width="240">
</p>

# craftsman — Claude Code plugin marketplace

<p align="center">
  <a href="https://github.com/bufferBrew/craftsman/actions/workflows/validate.yml"><img src="https://github.com/bufferBrew/craftsman/actions/workflows/validate.yml/badge.svg" alt="validate"></a>
  <a href="./craftsman-plugin/.claude-plugin/plugin.json"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FbufferBrew%2Fcraftsman%2Fmain%2Fcraftsman-plugin%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=blue" alt="version"></a>
  <a href="https://code.claude.com/docs/en/plugin-marketplaces"><img src="https://img.shields.io/badge/Claude%20Code-plugin-d97757" alt="Claude Code plugin"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

**craftsman** makes engineering discipline the default in [Claude Code](https://code.claude.com):
the smallest correct change, no fix without a root cause, and an honest report of what was
actually verified. It bundles ten agents, seven skills, two slash commands, and a cross-platform
hook system — installable in two commands.

<p align="center">
  <img src="./craftsman-demo.svg" alt="Terminal demo: @orchestrator runs the bugfix pipeline — debugger finds the root cause via graphify, coder ships a +4 −1 diff with a passing build, tester adds a regression test, and the run ends with a Verified / Assumed / Not covered status block" width="780">
</p>

## Install

```
claude plugin marketplace add bufferBrew/craftsman
claude plugin install craftsman@craftsman
```

Or from inside a Claude Code session:

```
/plugin marketplace add bufferBrew/craftsman
/plugin install craftsman@craftsman
```

Restart Claude Code (or start a new session) after installing, then run `/craftsman:init` in any
project to get started.

## What you get

| Problem | Before | With craftsman |
|---|---|---|
| Choosing the right agent pipeline | Trial-and-error chaining of agents | `@orchestrator` classifies the task, picks the minimal pipeline, and gates each stage on fresh evidence |
| Diffs grow beyond the request | "Fixed it" — plus an uninvited refactor of three other files | **Minimal-diff coding** — the smallest change that solves the problem; anything extra needs your OK first |
| The same bug returns under a new name | Symptom patched, root cause untouched | **Root-cause debugging** — no fix without an established root cause; a [graphify](https://pypi.org/project/graphifyy/) knowledge graph catches recurring bugs before they're filed as new ones |
| Finding relevant code takes forever | Raw grep through files | Query the graphify graph first — hooks nudge every grep/find toward it in graphed projects |
| Environment quirks rediscovered every session | Same OS/shell/tool failure re-derived by trial and error | **Environment-quirk memory** — discovered once, recorded, never re-derived |
| Scaffolding writes files you didn't ask for | Surprise `CLAUDE.md` and config files | **Ask-before-writing** — `/craftsman:init` proposes exact file content and waits for confirmation |
| "Done!" but nothing was actually run | Claims without evidence | **Honest completion** — every nontrivial task ends with a Verified / Assumed / Not covered status block |

## Documentation

- [Full plugin reference](./craftsman-plugin/README.md) — agents, skills, commands, hooks,
  installation options, troubleshooting.
- [Use cases](./docs/use-cases.md) — worked scenarios showing when each piece earns its keep.
- [Contributing](./CONTRIBUTING.md) — how to add agents/skills, validate, and test hooks.
- [Changelog](./CHANGELOG.md)

## License

[MIT](./LICENSE)
