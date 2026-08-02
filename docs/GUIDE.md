# Developer guide

This guide is for you, not for the AI: it is not referenced by `AGENTS.md`, so it never consumes context tokens. Here you find the *why* and the *how* of using the template day to day.

## Who reads what

| File | Reader | When |
|---|---|---|
| `AGENTS.md` (= `CLAUDE.md`) | the AI | always in context, every session |
| `requirements/00_overview.md` | AI + human | session start (protocol) |
| `requirements/<module>.md` | AI + human | on demand, only modules touched by the task |
| `.claude/skills/`, `.claude/agents/` | Claude Code | auto-discovery; other agents open them as markdown |
| `docs/GUIDE.md` (this file) | you only | never loaded by the AI |

Underlying principle: whatever is always in context (`AGENTS.md`) stays minimal; everything else loads only when needed.

## Initial setup (once)

1. **Use this template** on GitHub → new repo
2. Fill in `requirements/00_overview.md`: vision, actors, constraints, cross-cutting invariants
3. In `AGENTS.md`, adapt: the **Commands** table to your stack (examples are Rust/cargo) and the **Conventions** — including the **requirements language** (English by default; set e.g. Italian there and every REQ, report and changelog will follow)
4. Adapt or delete `requirements/auth.md` (a working example)
5. Create one file per module from `requirements/_template_module.md`
6. Check the lint locally: `pip install pyyaml && python tools/lint_requirements.py`

On Windows: `CLAUDE.md` is a symlink to `AGENTS.md`. If git doesn't preserve it (`git config core.symlinks true` before cloning), recreate it or copy the file — what matters is that they don't diverge.

## Daily workflow

### 1. Writing a requirement

Two equivalent paths:

- Tell the AI what you want in natural language → the `/req-new` skill generates the compliant block (correct ID, `status: draft`, vague references into `pending_refs`)
- Write it by hand copying `requirements/_template_req.md`

Either way: don't stop to look up other requirements' exact IDs while writing. Drop the phrase into `pending_refs` ("when the token is expired") and move on — resolution is a separate step.

### 2. Review

Before approving a draft, invoke the `req-reviewer` subagent ("review the drafts of the upload module"). It runs in an isolated, read-only context and returns a per-REQ report (approvable / needs revision) with pointed proposals, without touching anything. Promoting `draft → approved` is your call.

### 3. Resolving pending_refs

Periodically (or at session start if the protocol flags them): `/req-resolve`. The AI matches against existing REQs' `aliases`; on ambiguous cases it asks instead of guessing.

### 4. Implementation

Give the AI the task by ID ("implement REQ-UPLOAD-002"). The protocol in `AGENTS.md` is **requirement-first**: if you ask for a behavior change without citing a REQ, the AI must find the matching one or propose `/req-new` before coding. It must also read the module and dependencies first, write one test per Given/When/Then scenario, add an `Implements: REQ-XXX-NNN` comment on the implementing function (cross-language traceability, checked by the lint), and stop on conflicts instead of resolving them on its own.

### 5. Promoting to tested

The AI may *propose* `implemented → tested` only after running the module's full suite (slow tests included). Confirmation is yours: it's the checkpoint against flaky tests or softened assertions.

## The lint

It validates structure, not content (content is the review's job): unique well-formed IDs, `depends_on` pointing to existing REQs, allowed statuses, `tested` with linked tests, paths in `files.*` actually existing, forgotten `pending_refs`, and code under the modules' `owner_dir` referencing non-existent REQs (typos in `Implements:` comments).

It runs in three places, ordered by distance from you:

1. **Hook** (`.claude/settings.json`): automatically after every AI edit to `requirements/` — on failure the errors return as feedback to the agent, which fixes them immediately
2. **Local**: `python tools/lint_requirements.py` whenever you want
3. **CI** (GitHub Action): on every push/PR touching requirements — the final safety net

Exit code 1 = errors (blocking), 0 = clean or warnings only.

## Maintenance

- **Deprecate, never delete**: `status: deprecated` + reason in the changelog. Prevents the AI from reintroducing discarded behavior, and gives you decision traceability (useful for documentation/thesis writing too).
- **Module growing too large** (~15-20 REQs or an unwieldy file): don't switch to one-file-per-REQ — split the module into two coherent modules. Often it's a sign the code should be split too.
- **Routes table**: derived; the REQ is the source of truth. If they diverge, fix the table.
- **REQ changelogs**: keep the last ~5 entries; full history is in git.

## Why it's built this way (in short)

Every choice minimizes the tokens the AI re-processes each cycle: one file per module (no monolith, no fragments), empty YAML fields omitted, skills referencing templates instead of duplicating them, deterministic lint instead of asking the AI to check, subagents for read-heavy/small-output tasks so the material read doesn't pollute the main session. If you extend the template, keep this criterion: AI judgment only where judgment is needed, everything else goes to scripts.
