---
description: Run the full craftsman pipeline on a task — classify it, select the minimal agent set, dispatch specialists, gate each stage on fresh evidence, and report.
argument-hint: <the multi-step task to run end to end>
---

Request: $ARGUMENTS

Run the `craftsman:craftsman-workflow` skill in the main session. If needed, read
`${CLAUDE_PLUGIN_ROOT}/skills/craftsman-workflow/SKILL.md`. Keep decisions and verification
in this session and dispatch the smallest applicable set of specialists.
