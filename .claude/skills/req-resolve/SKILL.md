---
name: req-resolve
description: Resolve requirement pending_refs into canonical depends_on IDs. Invoke explicitly with /req-resolve, optionally naming the modules.
disable-model-invocation: true
---

# Resolving pending_refs

For each `pending_refs` entry in the given modules (all files under `requirements/` if unspecified):

1. Find the target REQ by matching the phrase against `aliases`, `id` and requirement descriptions.
2. Unique match → move the resolved ID into `depends_on`, remove the entry from `pending_refs`, note the resolution in the REQ changelog.
3. Ambiguous or missing match → list the candidates found and ask the human which one was meant (or whether a new REQ should be created with `/req-new`). Never guess.
4. When done, run `python tools/lint_requirements.py` and report a summary: resolved / needs clarification.
