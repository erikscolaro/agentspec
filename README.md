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
2. Check `AGENTS.md`: `init` fills in the commands and the requirements language from your project and a short questionnaire
3. Adapt `tools/gen_auth_tests.py`: its three constants at the top produce a Rust/rstest test as an example. Rewrite them for your test framework (the docstring has a pytest version) before the first REQ declares a protected route.
4. Create one module per file from `_template_module.md` — [`docs/example-auth.md`](docs/example-auth.md) is a worked example

The full workflow is in [`docs/GUIDE.md`](docs/GUIDE.md).

## Available tools

| Tool | Type | What it does | When to use it |
|---|---|---|---|
| `/agentspec:init` | skill | copies the templates and scripts, then fills `AGENTS.md` from your project and a short questionnaire | once, in a new project |
| `/agentspec:req-new` | skill | turns an informal description into a compliant `draft` REQ | whenever you need a new requirement |
| `/agentspec:req-audit` | skill | lists defects between the REQs of one module (report only) | before approving a module, or when it feels inconsistent |
| `/agentspec:req-resolve` | skill | resolves `pending_refs` into `depends_on` IDs (explicit only) | when the session start protocol flags `pending_refs` |
| `/agentspec:flow-new` | skill | turns a user journey into a `### FLOW-…` block pointing to REQs | when you describe a journey across several REQs |
| `req-reviewer` | agent | reviews `draft` REQs, read-only | before promoting `draft → approved` |
| `req-writer` | agent | writes decisions already taken with you into the REQs, never decides | during a design session, one message per decision batch |
| `flow-coverage` | agent | matches flow steps against existing REQs, read-only | called by `flow-new`, or to ask which REQs a journey covers |
| lint on edit | hook (PostToolUse) | runs the requirements lint after every edit to `requirements/*.md` | automatic |
| method at start | hook (SessionStart) | injects `method/AGENTS-METHOD.md` in projects with `requirements/00_overview.md` | automatic |
| `tools/lint_requirements.py` | script | structural lint of the requirements, regenerates `.index.md` | locally and in CI |
| `lint_requirements.py --emit-testmap` | script option | prints the scenario → REQ → test map | when you want to see test coverage (human only) |
| `lint_requirements.py --emit-routes` | script option | prints the route → REQ table | when you want the API surface at a glance (human only, never commit) |
| `tools/gen_auth_tests.py` | script | writes the auth-rejection test from the index | after a REQ changes `route` or `auth_required` |

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
