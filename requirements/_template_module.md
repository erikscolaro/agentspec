# Module: <Name>

<!-- Copy this file as requirements/<module_name>.md and fill it in.
     Files prefixed with "_" are ignored by the lint. -->

```yaml
module: module_name            # lowercase, consistent with the REQ ID prefix
status: draft                  # aggregate: draft | in_progress | implemented | stable
owner_dir: src/module_name/    # directory of this module's code (also scanned by the lint for REQ references)
depends_on_modules: []         # e.g. [auth]
```

## Purpose

<!-- 2-4 sentences: what this module manages. Explicitly name what it does NOT
     manage, pointing to other modules (→ see Out of scope). -->

## Exposed routes

<!-- The module's API surface. The REQ remains the source of truth: if this table
     and a REQ diverge, the REQ wins and the table gets fixed.
     REQ↔route is N:M: one route may implement several REQs and vice versa. -->

| Method | Path | Handler | REQ | Auth |
|---|---|---|---|---|
| | | | | |

## Out of scope

<!-- What this module does NOT do, pointing to the module that does.
     Critical section: without it the AI tends to "invade" other modules' territory. -->

- <!-- e.g. Document signing → see signature.md -->

## Domain entities

<!-- Local conceptual schema: entities and main fields, not the exact code structs
     (the AI reads those from the code; this section must stay stable over time). -->

- `Entity`: field_a, field_b, field_c

## Invariant rules

<!-- Rules valid for ALL REQs of this module, written once here.
     E.g. allowed state transitions, tenant isolation, uniqueness. -->

- <!-- e.g. Document states: awaiting_signature → signed → archived (one-way) -->

## Module NFR constraints

<!-- Only module-specific NFRs. Global ones belong in 00_overview.md. -->

- <!-- e.g. Upload max 50MB per file -->

## Local glossary

<!-- Module-specific terms only. -->

| Term | Definition |
|---|---|
| | |

---

## Requirements

<!-- One block per REQ, copied from _template_req.md. Progressive IDs, never reused.
     Each REQ is a level-3 heading (###) nested under this level-2 (##) section. -->
