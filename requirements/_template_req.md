<!-- Skeleton of a single requirement: copy it into the "Requirements" section
     of the module file. The heading MUST match the id field. -->

## REQ-XXX-001

```yaml
id: REQ-XXX-001                # prefix = module (e.g. REQ-UPLOAD-001), number never reused
module: module_name
type: functional               # functional | non_functional | invariant
status: draft                  # draft | approved | implemented | tested | deprecated
priority: medium               # low | medium | high
auth_required: none            # none | <role> (e.g. tenant_admin) — a reference, not a repetition
aliases: []                    # keywords for resolving other REQs' pending_refs
files:
  src: []                      # real paths, e.g. [src/upload/handler.rs]
  test: []                     # required for status: tested, e.g. [tests/upload.rs::upload_valid]
depends_on: []                 # already-resolved canonical IDs, e.g. [REQ-AUTH-003]
pending_refs: []               # natural-language references; the AI resolves them into depends_on
```

<!-- Convention: in the real REQ, OMIT empty fields ([]): the lint treats absent as empty.
     They are all shown here only to document the full structure. -->

**Description**

<!-- One or two sentences: the atomic behavior. If the Then verifies more than 2-3
     unrelated outcomes, split into two REQs. Self-contained: no "as above". -->

**Acceptance criteria**

**Scenario: <behavior>_<outcome>**  <!-- the scenario name IS the test function name -->
- Given <!-- system state before the action -->
- When <!-- ONE action only -->
- Then <!-- observable, verifiable outcome -->

<!-- More scenarios = more named blocks. Each scenario → one test function with the same name.
     Dependency-coverage scenarios can note it inline: **Scenario: x** *(covers REQ-AUTH-003)* -->

**Edge cases**

<!-- Not optional: this is the section the AI "fills in randomly" if missing.
     Behavior on invalid input, errors, limits. Only validation SPECIFIC to this REQ;
     rules repeated everywhere belong in the invariants. -->

**Changelog**

- YYYY-MM-DD: created (draft)
