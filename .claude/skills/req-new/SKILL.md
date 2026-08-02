---
name: req-new
description: Create a new requirement compliant with the repo methodology from an informal description. Use when the user asks to add, create or draft a new requirement.
---

# New requirement

1. Read `requirements/_template_req.md` (reference structure, not duplicated here) and the target module file.
2. If the target module is unclear from the request, ask before proceeding.
3. ID: module prefix + first free number. Never reuse numbers, not even from deprecated REQs.
4. Fill in the block:
   - Atomic description: if the Then would verify more than 2-3 unrelated outcomes, propose two separate REQs.
   - Each scenario = one Given/When/Then block, with a single When.
   - Edge cases always present: if not deducible from the request, ask instead of inventing.
5. Vague references to other requirements → entry in `pending_refs`, in natural language. Do not invent IDs in `depends_on`.
6. `status: draft`. Omit empty fields. Changelog: today's date, `created (draft)`.
7. Write the REQ prose in the requirements language set in AGENTS.md (Conventions).
8. Append the block to the module's Requirements section; if the REQ introduces or changes a route, update the "Exposed routes" table in the same file.
9. Run `python tools/lint_requirements.py`.
