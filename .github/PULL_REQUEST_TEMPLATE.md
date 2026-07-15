**What**

<!-- One or two sentences. What changed and where. -->

**Why**

<!-- The problem or gap it addresses. Link the issue if one exists. -->

**Tested**

<!-- What you ran and what you saw. Paste the relevant output — a claim without
     evidence is not a verification. Example:
     `claude plugin validate --strict ./craftsman-plugin` → "All components valid (12 agents, 8 skills, 2 commands, 2 hooks)"
     CI green on the linked commit. -->

**Checklist**

- [ ] `claude plugin validate --strict ./craftsman-plugin` passes locally
- [ ] CI (`validate.yml`) is green
- [ ] Agent/skill/command counts updated in README(s) if a component was added or removed
