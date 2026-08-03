# Project overview

<!-- Fill in every section. This is the first file the AI reads each session:
     it contains only what is cross-cutting to ALL modules. Module-specific
     context belongs in the module file. -->

## Vision

<!-- 2-4 sentences: what the system does, for whom, the scope of the current version. -->

## Actors

<!-- One actor per row: canonical name + short description. REQs use ONLY canonical names. -->

| Actor | Description |
|---|---|
| <!-- e.g. Tenant Admin --> | <!-- e.g. Owner of the client organization, manages documents and signers --> |

## Global constraints

<!-- Constraints that apply everywhere: regulatory (GDPR, eIDAS...), infrastructure
     (EU hosting, self-hosting...), technology (mandated stack). -->

## Cross-cutting invariants

<!-- Rules valid in every module, written ONCE here and never repeated in individual REQs.
     If an invariant must be referenceable via depends_on, give it an ID as in the example. -->

### REQ-GLOBAL-001 - Entity identifiers are UUID v4

```yaml
id: REQ-GLOBAL-001
module: global
type: invariant
status: approved
aliases: [uuid-v4, id-format]
```

**Description**
Every entity identifier exposed via API is a UUID v4. No sequential ID is ever exposed externally.

**Changelog**
- YYYY-MM-DD: created

<!-- Other typical examples: input sanitization, timestamp format (ISO 8601 UTC),
     multi-tenant isolation, access logging. -->

## Global glossary

<!-- Only terms used across multiple modules. Local terms belong in the module glossary. -->

| Term | Definition |
|---|---|
| | |

## Module index

<!-- Update when you create a new module. -->

| Module | File | Status |
|---|---|---|
| auth | [auth.md](auth.md) | draft |

## Working on this repo

The full operating protocol (session start, commands, boundaries, test guidelines, tools) is in [`AGENTS.md`](../AGENTS.md) (symlinked as `CLAUDE.md`, so Claude Code loads it automatically). The human developer guide is in [`docs/GUIDE.md`](../docs/GUIDE.md).
