# Roadmap

No dates, no version commitments. Items ship when they are well-scoped and tested.
Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Planned agents

The orchestrator's [agent availability reference](craftsman-plugin/agents/orchestrator.md) is the
canonical list of what exists, what is environment-dependent, and what is not yet created. Three
agents are documented in the "Not yet created" table:

| Agent | What it would do | Fallback today |
|---|---|---|
| `spring-api` | Spring-specific implementation: REST endpoints, Spring Boot annotations, bean wiring, and the Spring project's own build/verify command | `coder` |
| `spring-reviewer` | Spring-specific code review: Spring idioms, bean lifecycle, annotation misuse, and MVC/data layer conventions | `reviewer` |
| `spring-tester` | Spring-specific test writing: JUnit unit tests, `@SpringBootTest` integration tests, MockMvc slice tests | `tester` |

These three are sequenced together because the orchestrator already defines a Spring feature
pipeline (`researcher → planner → coder → tester → reviewer`). Right now that pipeline runs
entirely on generalist agents. Adding the Spring specialists would slot them into the same pipeline
positions without changing the pipeline shape — the same motivation that produced `android-feature`,
`android-tester`, and `compose-reviewer` for the Android tier.

**A note on the Android agents:** `android-feature`, `android-tester`, and `compose-reviewer` are
not missing and are not planned additions to this plugin's `agents/` directory. They are
environment-dependent agents that come from the host Agent SDK — see the "Environment-dependent"
table in orchestrator.md. The orchestrator falls back gracefully when they are absent.

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
