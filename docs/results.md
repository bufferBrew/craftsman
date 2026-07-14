---
title: Results
---

# Results

craftsman shipped its first public release ([v0.1.0](https://github.com/bufferBrew/craftsman/releases))
this week, so there isn't yet a corpus of external before/after sessions to report on. Rather than
invent numbers, this page tracks two things: real, verifiable examples of the discipline from
craftsman's own commit history (a plugin repo maintained under its own rules), and it will grow
with genuine field examples as the plugin gets used elsewhere. If you have a before/after from
your own project, see [CONTRIBUTING.md](https://github.com/bufferBrew/craftsman/blob/main/CONTRIBUTING.md)
for how to submit one.

## Minimal diff, verified in this repo's own history

**[`7c9b7b0`](https://github.com/bufferBrew/craftsman/commit/7c9b7b07d00b096723724fcd896124c365899f98)
— "Fix stale agent count in root README (9 -> 10)"**

```
README.md | 2 +-
1 file changed, 1 insertion(+), 1 deletion(-)
```

The request was exactly what the commit did: one wrong number, one file, one line changed. No
surrounding prose touched, no reformatting.

## Root cause over symptom patch, verified in this repo's own history

**[`42cabb2`](https://github.com/bufferBrew/craftsman/commit/42cabb210b83a5e05a92ce6d133f25b472845c78)
— the bash graphify hook's non-empty check**

The `pretooluse-graphify-bash` hook was silently misbehaving because of a one-character-class bash
mistake:

```diff
-      ... && [ -n "${out+x}" ] && { printf '%s' "$out"; return; }
+      ... && [ -n "$out" ] && { printf '%s' "$out"; return; }
```

`${out+x}` tests whether the variable is *set* — even to an empty string — not whether it's
*non-empty*. The symptom (the hook occasionally firing on empty command output) could have been
patched by adding a fallback check somewhere downstream; the actual root cause was this single
line, and the fix is a single line too.

## What this page doesn't claim (yet)

No graphify-recall dedup event, no orchestrator pipeline run, and no minimal-diff coding session
from an external project has been logged here — that data doesn't exist yet for a plugin this new.
Claims about recurring-bug recall or pipeline gating are described in
[the use cases](./use-cases.html) as intended behavior, not as measured results, until there's a
real example to point to.
