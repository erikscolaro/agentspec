# agentspec

A Claude Code plugin for writing software requirements optimized for iteration with AI coding assistants, while keeping the human readability of a classic requirements document.

## Philosophy

The traditional waterfall document is written to be read once and "frozen". agentspec produces requirements the AI can **re-consult and update on every iteration cycle**, with no implicit context to fill in and no token waste:

- **Markdown + YAML frontmatter** per requirement: parsable metadata + readable prose
- **One file per module**: fits the context window, iterate on one part at a time
- **Atomic, self-contained requirements** with two-way requirement ↔ code ↔ test traceability (`files.*` + `Implements:` / `Covers:` comments)
- **Requirement-first rule**: every behavioral code change is linked to a REQ
- **Deterministic lint** (script + hook + CI) for structural rules; AI judgment only where judgment is needed
- **Skills and subagents** for the requirements lifecycle

## Requirements

Python 3 with PyYAML (`pip install pyyaml`). Nothing else.

## Install

```
/plugin marketplace add erikscolaro/agentspec
/plugin install agentspec@agentspec
```

You get:

| Component | Use |
|---|---|
| `/agentspec:init` | set up agentspec in the current project |
| `/agentspec:req-new` | generate a REQ from an informal description |
| `/agentspec:req-audit` | audit one module for defects between REQs (report only) |
| `/agentspec:req-resolve` | resolve `pending_refs` into `depends_on` (explicit only) |
| `/agentspec:flow-new` | turn a journey description into a `### FLOW-…` block |
| `req-reviewer` agent | review `draft` REQs, read-only |
| `req-writer` agent | write decisions already taken into the REQs |
| `flow-coverage` agent | match flow steps against existing REQs, read-only |
| SessionStart hook | injects the method rules (`method/AGENTS-METHOD.md`) in projects that have `requirements/00_overview.md` |
| PostToolUse hook | runs the lint after every edit to `requirements/*.md` |

## First use

In your project root run `/agentspec:init`. It copies, and never overwrites (existing files are listed as skipped):

```
AGENTS.md                              project-specific rules for the AI
CLAUDE.md                              contains only @AGENTS.md
requirements/00_overview.md            vision, actors, cross-cutting invariants
requirements/_template_module.md       module skeleton
requirements/_template_req.md          requirement skeleton
tools/lint_requirements.py             the lint
tools/gen_auth_tests.py                auth-rejection test generator
.github/workflows/lint-requirements.yml   CI
```

Then:

1. Fill in `requirements/00_overview.md`
2. Adapt the Commands table and the requirements language in `AGENTS.md`
3. Adapt `tools/gen_auth_tests.py`: its three constants at the top produce a Rust/rstest test as an example. Rewrite them for your test framework (the docstring has a pytest version) before the first REQ declares a protected route.
4. Create one module per file from `_template_module.md` — [`docs/example-auth.md`](docs/example-auth.md) is a worked example

The full workflow is in [`docs/GUIDE.md`](docs/GUIDE.md).

## Where the rules live

The general method rules are in the plugin, in [`method/AGENTS-METHOD.md`](method/AGENTS-METHOD.md): a SessionStart hook injects them only in projects with `requirements/00_overview.md`, so the plugin can stay installed at user level. The project's `AGENTS.md` keeps only what is specific to it: requirements language, commands, protected paths.

## Where the scripts live

The plugin's `tools/` is what the skills and the hook run (`${CLAUDE_PLUGIN_ROOT}/tools/…`, always from the project root). `init` also copies both scripts into the project's `tools/`, so CI and other agents work without the plugin. The two copies can drift after a plugin update: to refresh the lint, delete `tools/lint_requirements.py` and run `/agentspec:init` again. `tools/gen_auth_tests.py` holds your own constants, so update it by hand.

## Requirement lifecycle

`draft → approved → implemented → tested` (or `deprecated`)

The AI proposes status transitions, the human confirms. `tested` requires `files.test` populated and the module's full suite green. Abandoned requirements become `deprecated` with a reason — never deleted.

## Key rules (details in `method/AGENTS-METHOD.md`)

- A failing test assertion is fixed by correcting the code or reporting a problem in the requirement — **never by weakening the assertion**
- On conflict (between requirements, or between an existing test and new behavior) the AI **stops and reports**
- Cross references are written in natural language in `pending_refs` and resolved into canonical IDs with `/agentspec:req-resolve`
- Implementing code carries an `Implements: REQ-XXX-NNN` comment — cross-language traceability, verified by the lint

## Other agents

Only Claude Code is packaged for now. Other agents get no hook: point them at `method/AGENTS-METHOD.md` (copy it into the project or reference it from their instructions file) alongside the project's `AGENTS.md`. The skills (`skills/*/SKILL.md`) and agents (`agents/*.md`) are plain markdown and can be followed as playbooks by other agents.
