# Module: <Name>

<!-- Copy this file as requirements/<module_name>.md and fill it in.
     Files prefixed with "_" are ignored by the lint. -->

```yaml
module: module_name            # lowercase, consistent with the REQ ID prefix
status: draft                  # aggregate: draft | in_progress | implemented | stable
owner_dir: src/module_name/    # directory of this module's code (scanned by the lint for Implements: refs)
test_dirs: [tests/]            # dirs scanned for `Covers: REQ-XXX-NNN` comments (E15, W9, --emit-testmap)
depends_on_modules: []         # e.g. [auth]
flow_coverage: optional        # optional | required — 'required' turns on W5 for this module
```

## Purpose

<!-- 2-4 sentences: what this module manages. Explicitly name what it does NOT
     manage, pointing to other modules (→ see Out of scope). -->

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

## Flows

<!-- User-goal level journeys: how several REQs of this module compose into
     something an actor actually sets out to do. NAVIGATIONAL, NEVER NORMATIVE:
     every step must reference a REQ, and no step may introduce behavior that is
     not specified in a REQ. If deleting a flow would leave any behavior
     unspecified, that behavior was in the wrong place — move it into a REQ.
     Use /flow-new. Each flow is a level-3 heading (###) nested here. -->

### FLOW-XXX-NAME — Short goal statement

```yaml
id: FLOW-XXX-NAME              # FLOW-<MODULE>-<NAME>, uppercase
module: module_name
actor: <role>                  # a human role, not a component
trigger: <what starts it>
outcome: <state of the world when it succeeds>
status: draft                  # draft | approved | implemented | tested | deprecated
```

**Narrative**

<!-- 2-4 sentences: why this journey exists and what the actor is trying to
     achieve. No behavior specification — that lives in the REQs. -->

**Steps**

1. <!-- what the actor does --> → REQ-XXX-001
2. <!-- ... --> → ???            <!-- ??? = no REQ yet; W5/W6 will keep reminding you -->

**Notes**

<!-- Ordering, cardinality, interruption semantics — as OBSERVATIONS, with a
     pointer to the REQ that enforces them. "Step 3 requires step 1 (enforced by
     REQ-XXX-004)" is fine. "Step 3 must reject if step 1 is missing" is not:
     that is a requirement, write it in REQ-XXX-004. -->

- <!-- e.g. Steps 1-2 interleave freely; no ordering is enforced. -->

---

## Requirements

<!-- One block per REQ, copied from _template_req.md. Progressive IDs, never reused.
     Each REQ is a level-3 heading (###) nested under this level-2 (##) section. -->
