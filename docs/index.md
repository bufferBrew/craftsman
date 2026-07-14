---
title: craftsman
---

# craftsman

Engineering discipline as the default in [Claude Code](https://code.claude.com): the smallest
correct change, no fix without a root cause, and an honest report of what was actually verified.
Ten agents, seven skills, two slash commands, and a cross-platform hook system — installable in
two commands.

## Install

```
claude plugin marketplace add bufferBrew/craftsman
claude plugin install craftsman@craftsman
```

Restart Claude Code (or start a new session), then run `/craftsman:init` in any project.

## Common problems this solves

- **Claude Code minimal diff** — a fix comes back with an uninvited refactor. `smallest-change-first`
  and minimal-diff coding stop that: anything beyond the request needs your OK first.
- **Claude Code keeps refactoring** — a one-line ask turns into three files touched. The `coder`
  agent runs a seven-step ladder before writing anything new, and stops at the minimum.
- **Claude Code says done but didn't test** — "Done!" with no build ever run. Every nontrivial task
  ends with a Verified / Assumed / Not covered status block, backed by fresh build/test evidence at
  each pipeline gate.
- **Claude Code re-fixes the same bug under a new name** — a [graphify](https://pypi.org/project/graphifyy/)
  knowledge graph lets the `debugger` agent recognize a recurring bug and recall its resolved fix
  instead of re-deriving it.

## Documentation

- [Use cases](./use-cases.html) — four worked scenarios showing when each piece earns its keep.
- [Results](./results.html) — real, verifiable before/after evidence, honestly scoped to what exists so far.
- [Full plugin reference](https://github.com/bufferBrew/craftsman/blob/main/craftsman-plugin/README.md) —
  agents, skills, commands, hooks, installation options, troubleshooting.
- [Changelog](https://github.com/bufferBrew/craftsman/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/bufferBrew/craftsman/blob/main/CONTRIBUTING.md)
- [Source on GitHub](https://github.com/bufferBrew/craftsman)

## License

[MIT](https://github.com/bufferBrew/craftsman/blob/main/LICENSE)
