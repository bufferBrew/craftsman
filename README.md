# craftsman — Claude Code plugin marketplace

This repository is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
hosting **craftsman**, an agent-discipline toolkit: a portable agent set plus skills enforcing
minimal-diff coding, root-cause debugging, recurring-bug detection via graphify, environment-quirk
memory, and an ask-before-writing project scaffolder.

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

Restart Claude Code (or start a new session) after installing.

## What's inside

The plugin lives in [`craftsman-plugin/`](./craftsman-plugin) — see its
[README](./craftsman-plugin/README.md) for the full reference (9 agents, 5 skills, 2 slash
commands, and a cross-platform hook system).

## License

[MIT](./LICENSE)
