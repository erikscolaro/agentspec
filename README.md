# AI Requirements Template

A template for writing software requirements optimized for iteration with AI coding assistants (Claude Code, Cursor, etc.), while keeping the human readability of a classic requirements document.

## Philosophy

The traditional waterfall document is written to be read once and "frozen". This template produces requirements the AI can **re-consult and update on every iteration cycle**, with no implicit context to fill in and no token waste:

- **Markdown + YAML frontmatter** per requirement: parsable metadata + readable prose
- **One file per module**: fits the context window, iterate on one part at a time
- **Atomic, self-contained requirements** with two-way requirement ↔ code ↔ test traceability (`files.*` + `Implements:` comments in code)
- **Requirement-first rule**: every behavioral code change is linked to a REQ
- **Deterministic lint** (script + hook + CI) for structural rules; AI judgment only where judgment is needed
- **Skills and subagents included** for the requirements lifecycle (drafting, review, reference resolution)

## Structure

```
AGENTS.md                 Operating protocol for the AI (always in context — minimal)
CLAUDE.md -> AGENTS.md    Symlink: Claude Code loads it automatically
docs/GUIDE.md             Human developer guide (never read by the AI)
requirements/
  00_overview.md          Vision, actors, cross-cutting invariants
  _template_module.md     New module skeleton (not linted)
  _template_req.md        New requirement skeleton (not linted)
  auth.md                 Example module — adapt or delete
.claude/
  skills/req-new/         /req-new — generate a REQ from an informal description
  skills/req-resolve/     /req-resolve — resolve pending_refs into depends_on
  agents/req-reviewer.md  Read-only subagent for draft review (Sonnet)
  settings.json           Hook: automatic lint after edits to requirements/
tools/
  lint_requirements.py    Structural validator (12 errors + 3 warnings)
  hooks/lint_on_edit.py   Hook script
.github/workflows/        CI running the lint on push/PR
```

## Quick start

1. **Use this template** on GitHub
2. Fill in `requirements/00_overview.md`
3. Adapt Commands and Conventions in `AGENTS.md` to your stack — the **requirements language** is English by default and can be changed there
4. Read `docs/GUIDE.md` for the full workflow

Local lint: `pip install pyyaml && python tools/lint_requirements.py`

## Requirement lifecycle

`draft → approved → implemented → tested` (or `deprecated`)

The AI proposes status transitions, the human confirms. `tested` requires `files.test` populated and the module's full suite green. Abandoned requirements become `deprecated` with a reason — never deleted.

## Key rules (details in AGENTS.md)

- A failing test assertion is fixed by correcting the code or reporting a problem in the requirement — **never by weakening the assertion**
- On conflict (between requirements, or between an existing test and new behavior) the AI **stops and reports**
- Cross references are written in natural language in `pending_refs` and resolved into canonical IDs with `/req-resolve`
- Implementing code carries an `Implements: REQ-XXX-NNN` comment — cross-language traceability, verified by the lint
