# AGENTS.md

Operating instructions for working on this repository. Project-specific rules only — no generic software engineering principles. This file is always in context: keep it minimal; details and procedures live in the referenced files.

## Session start protocol

Before writing any code, in order:

1. Read `requirements/00_overview.md` (global context, actors, cross-cutting invariants)
2. Read the module file(s) involved in the task (`requirements/<module>.md`). To locate a REQ
   across modules, read `requirements/.index.md` first (generated, one line per REQ) instead of
   opening every module file.
3. If the modules you read contain `pending_refs`, flag it (resolution happens via `/req-resolve`)
4. Check the `status` of the REQs the task touches:
   - `draft` → to be designed; confirm your interpretation before implementing
   - `approved` → ready to implement
   - `implemented` / `tested` → do not modify without an explicit reason in the task
   - `deprecated` → do not reintroduce the described behavior

## Conventions

- **Requirements language: English** <!-- change here (e.g. Italian). REQ prose, reviewer reports and changelogs follow this setting. Chat language is whatever the user uses. -->
- **Heading hierarchy**: `#` document title only, `##` major sections (Purpose, Requirements, Vision...), `###` individual REQ — always nested under `## Requirements` (or `## Cross-cutting invariants` in the overview), formatted as `### REQ-ID - Short title` (e.g. `### REQ-AUTH-001 - Login issues an access/refresh token pair`). Nothing below REQ subsections becomes a heading (Description, Scenario, Edge cases stay bold text).
- **Description = one sentence of intent** ("As a <actor>, I want <goal>, so that <benefit>"), never a
  summary of the scenarios. A rule that holds across the module goes in `## Invariant rules`, an
  exclusion in `## Out of scope`, a definition in the glossary, an implementation choice in an ADR.
  Test: if a sentence would still be verified by a test, it is a scenario restated — delete it.
- **Flows** (`## Flows`, above `## Requirements`): user-goal level journeys, `### FLOW-<MODULE>-<NAME>`.
  Navigational only — every step references a REQ, no step introduces behavior. `???` marks a step
  with no REQ yet.
- **Where does it go?** testable → a REQ. Deleting it loses navigability but no behavior → a flow.
  Externally imposed constraint → `00_overview.md` with its rationale.
- **`route` + `auth_required` imply the rejection test.** Never write an unauthenticated-request
  scenario inside a REQ: it is identical everywhere and is generated once from the index. Only write
  an auth scenario when the outcome depends on something that REQ knows (tenant mismatch, mixed-auth
  route, error precedence).
- Acceptance criteria: `**Acceptance criteria**` is the section label; each scenario is a **blockquote** starting with `> **Scenario: <behavior>_<outcome>**`, so it reads visually distinct from the label above it. The scenario name IS the test function name.
- **Traceability comments**: the function/handler implementing a requirement carries `Implements: REQ-XXX-NNN`; a test verifying a scenario carries `Covers: REQ-XXX-NNN` (language-appropriate comment syntax, checked by the lint in `owner_dir` and `test_dirs`). Keep `files.src`/`files.test` in sync. Name the test function exactly after the scenario: that is what makes a red CI run traceable back to a requirement.
- Changelog dates: ISO `YYYY-MM-DD`. Changelog trimmed to the last 5 entries: full history lives in git.
- Empty YAML fields (`[]`): **omitted**. The lint treats absent as empty.

## Commands

<!-- Adapt to your stack. Verbatim commands, not descriptions. -->

| Action | Command |
|---|---|
| Full test suite | `cargo test` |
| Single module tests | `cargo test --test <module>` |
| Include slow tests | `cargo test -- --include-ignored` |
| Code lint | `cargo clippy -- -D warnings` |
| Format check | `cargo fmt --check` |
| Requirements lint | `python tools/lint_requirements.py` |
| Generate auth route tests | `python tools/gen_auth_tests.py` |
| Scenario → REQ → test map (human only) | `python tools/lint_requirements.py --emit-testmap` |
| Route → REQ table (human only) | `python tools/lint_requirements.py --emit-routes` |

Tests marked `#[ignore]` (slow/expensive) run only before proposing `status: tested`, not on every iteration.

## Available tools

| Tool | Type | Use |
|---|---|---|
| `/flow-new` | skill | turn an informal journey description into a `### FLOW-…` block |
| `flow-coverage` | read-only subagent | match flow steps against existing REQs; returns a digest |
| `/req-new` | skill | generate a new REQ from an informal description |
| `/req-audit` | skill, Sonnet | audit ONE module for defects between REQs; report only |
| `/req-resolve` | skill, explicit invocation only | resolve `pending_refs` into `depends_on` |
| `req-reviewer` | read-only subagent | review `draft` REQs: report only, no file or status changes |
| `tools/lint_requirements.py` | script | structural validation; runs via hook and in CI |
| `tools/gen_auth_tests.py` | script | writes the auth-rejection test from the index; never hand-edit its output |

Agents other than Claude Code: skills and subagents are plain markdown files under `.claude/` — open and follow them as playbooks.

## Boundaries

### Always
- Follow the session start protocol before modifying code
- **Requirement-first**: every behavioral code change is linked to a REQ. If the task doesn't reference one, identify the matching REQ or propose `/req-new` before implementing.
- Add the `Implements: REQ-XXX-NNN` comment when implementing a requirement, and update its `files.src`/`files.test`
- Run the requirements lint after changes to `requirements/` (in Claude Code this runs automatically via hook)
- Treat `requirements/.index.md` as generated: read it, never edit it, never resolve conflicts in it
- Run the module's full suite (including `#[ignore]` tests) before proposing `status: tested`
- Update the REQ changelog on every substantial change to the requirement

### Ask first
- Before changing the `status` of any REQ (you propose, the human confirms)
- Before modifying cross-cutting modules (`auth.md`, `security.md` and similar)
- Before implementing a REQ in `draft` state

### Never
- Weaken a test assertion to make it pass (see Test guidelines, rule 1)
- Delete a REQ: use `status: deprecated` with the reason in the changelog
- Renumber or reuse an existing ID, even if deprecated
- Resolve on your own a conflict between two REQs, or between an existing test and newly requested behavior: stop and report
- Implement behavior that belongs to a module's "Out of scope" inside that module
- Write normative statements inside a flow ("the system must reject…"). If a flow step needs a rule,
  the rule belongs in a REQ and the step references it. E14 is a backstop, not a licence.
- Run `--emit-routes` or paste its output into any file: it is a human-facing view of data already
  in `.index.md`, and committing it would recreate the duplicated routes table we removed.
- Write an unauthenticated-request scenario in a REQ that already declares `route` + `auth_required`
- Grow a REQ's Description beyond its one sentence of intent: propose the right section instead
- Hand-edit `tests/auth_routes.rs` or any other generated test: change the REQ's `route`/`auth_required` and regenerate
<!-- Add project-specific paths the AI must not touch without a linked REQ, e.g.: -->
<!-- - Touching `src/signature/crypto.rs` without an explicitly linked REQ -->

## Requirements management

- **Conflicting REQs**: if two requirements contradict each other during implementation, stop and report both IDs with the nature of the conflict.
- **Deprecation**: `status: deprecated` + reason in the changelog + replacing REQ if any. Never delete.
- **New REQs**: use `/req-new`, or copy the structure from `requirements/_template_req.md`.

## Test guidelines

1. A failing assertion is fixed by correcting the code or reporting a problem in the requirement — never by weakening the assertion.
2. Each named scenario of a REQ maps to one test function with the same name; Given/When/Then appear as structuring comments inside it.
3. Before proposing `status: tested`, run the module's full suite (slow tests included), not just the test of the REQ being worked on.
4. If a REQ has `depends_on`, its tests cover at least one dependency-related case beyond the happy path — but NOT the missing-token case: that one is generated from `route` + `auth_required` for every protected route at once.
5. If an existing test contradicts newly requested behavior, stop and report — do not silently modify the old test.
