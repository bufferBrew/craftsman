---
description: Route a code-review request directly to the reviewer agent — no full orchestrator pipeline.
argument-hint: <file path, diff, or description of what to review>
---

The user wants a code review without the overhead of the full orchestrator pipeline. This routes
straight to the reviewer agent's discipline.

Request: $ARGUMENTS

Do this directly, following the `reviewer` agent's principles:

1. Read the relevant file(s) before reviewing — do not work from memory.
2. If `$ARGUMENTS` names a file, review that file. If it describes a recent change, use Glob/Grep
   to find the relevant files first.

**Severity definitions:**
- **CRITICAL**: data loss, security vulnerability, crash in the happy path, broken build, wrong behavior in a core invariant.
- **HIGH**: incorrect logic, race condition, resource leak, missing error handling on an external call, silent failure.
- **MEDIUM**: edge case not handled, misleading error message, inefficient but not broken, missing null check in a non-critical path.
- **LOW**: style inconsistency, dead code, overly verbose logic, minor naming issue, unnecessary reinvention of a stdlib/existing-dependency function.

**Output format for each finding:**
```
[SEVERITY] file.ext:line — Short title
Detail: what is wrong and why it matters.
Fix: concrete description of the correction (do not write the fixed code — describe it).
```

Group findings by severity (CRITICAL first). If a section is clean: `[PASS] No issues found in <area>.`

End with: **Summary**: `X CRITICAL, Y HIGH, Z MEDIUM, W LOW findings.`

Constraints: only report issues you are confident about. Do not praise code or pad with positives.
Do not flag issues already covered by an existing test.
