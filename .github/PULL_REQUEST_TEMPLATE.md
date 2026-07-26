**What**

<!-- One or two sentences. What changed and where. -->

**Why**

<!-- The problem or gap it addresses. Link the issue if one exists. -->

**Tested**

<!-- What you ran and what you saw. Paste the relevant output — a claim without
     evidence is not a verification. Example:
     `claude plugin validate --strict ./craftsman-plugin` → "Validation passed" (15 agents, 8 skills, 7 commands, 4 hook events)
     CI green on the linked commit. -->

**Checklist**

- [ ] `claude plugin validate --strict ./craftsman-plugin` passes locally
- [ ] CI (`validate.yml`) is green
- [ ] Agent/skill/command counts updated in README(s) if a component was added or removed
