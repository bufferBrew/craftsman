---
description: Route a security audit directly to the security agent for the current project — no full orchestrator pipeline.
argument-hint: (no arguments — audits the current project)
---

Run a full security audit on the current project, following the `security` agent's discipline.

Work through every section below systematically. For each clean section say so explicitly.

## 1. Hardcoded secrets — grep first

Grep across all source files for:
- Credential keywords: `(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)\s*[=:]\s*["']?[A-Za-z0-9+/=._-]{16,}`
- Passwords: `(password|passwd|pwd)\s*[=:]\s*["'][^"']{4,}["']`
- Provider token shapes: `ghp_[A-Za-z0-9]{36}`, `AKIA[0-9A-Z]{16}`, `sk-[A-Za-z0-9]{48}`

## 2. Git history scan

```bash
git log --all --oneline --diff-filter=A -- "*.env" "local.properties" "*.keystore" "*.pem"
```

## 3. OWASP Top 10 (applicable to this project's stack)

Check for: injection (SQL/shell), broken access control, cryptographic failures, security misconfiguration, vulnerable components (use WebSearch on NVD for old-looking dependency versions), logging failures.

## 4. CI/CD (if `.github/workflows/` exists)

- `pull_request_target` + checkout at PR head SHA — **CRITICAL**
- Floating action versions (`@v3`, `@main`) vs pinned SHA
- `${{ secrets.X }}` echoed in run steps
- Over-broad `permissions: write-all`

## 5. AI agent-specific

- CLAUDE.md files with credentials
- Agent `.md` files — read-only agents must not have Edit/Write/Bash
- Prompt injection risks in skills/commands

## 6. .gitignore audit

Confirm sensitive files (`*.env`, `local.properties`, `*.keystore`, `*.pem`) are in `.gitignore` and not tracked by git (`git ls-files --error-unmatch <file>`).

---

**Output format** for each finding:
```
[SEVERITY] Category — Short title
Location: file:line
Detail: what is vulnerable and how it could be exploited.
Fix: concrete remediation step.
```

End with the severity count table and:
**Verdict**: PASS (zero CRITICAL or HIGH) | CONDITIONAL PASS (HIGH only) | FAIL (any CRITICAL)
