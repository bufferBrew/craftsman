# Roadmap

No dates, no version commitments. Items ship when they are well-scoped and tested.
Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Usage evidence and telemetry

There is currently no way to see which craftsman skills, agents, or hooks actually fired in a
given session. [docs/results.md](docs/results.md) is explicit that no corpus of real before/after
sessions exists yet — the plugin is new and external field examples haven't accumulated.

Three approaches that could address this, each with real tradeoffs:

**(a) Opt-in session transcript scanning.** A local script that parses Claude's conversation
export and surfaces which craftsman tools were invoked. Advantage: post-hoc, no runtime friction.
Tradeoff: conversation exports may not be available in all Claude configurations, and parsing
them reliably requires knowing Claude's exact export format, which can change.

**(b) Append-on-fire hook log.** A hook that writes a timestamped line to a local log file
whenever it fires — e.g., `~/.claude/craftsman-memory/hook-log.md`. Advantage: lightweight,
always-on audit trail with no self-reporting involved. Tradeoff: only captures hook events, not
skill or agent invocations, and adds a write side effect to every hook run.

**(c) `/craftsman:session-summary` command.** A command that prompts Claude to reflect at the end
of a session on which craftsman disciplines were applied. Advantage: covers agents and skills
that leave no filesystem trace. Tradeoff: relies on Claude's self-report of its own behavior,
which is not the same as an objective log — the accuracy of that reflection is unverified.

**This item needs a scoping conversation before implementation.** The tradeoffs — privacy
implications of a persistent log, friction cost of an end-of-session prompt, and the correctness
risk of self-reported telemetry — must be settled before any code is written. Open an issue or
Discussion to start that conversation.
