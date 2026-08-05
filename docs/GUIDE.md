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

It validates structure, not content (content is the review's job): unique well-formed IDs, `depends_on` pointing to existing REQs, allowed statuses, `tested` with linked tests, paths in `files.*` actually existing, forgotten `pending_refs`, code under the modules' `owner_dir` referencing non-existent REQs (typos in `Implements:` comments), REQ headings at the wrong level, and REQ headings missing a descriptive title.

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


## Flows

A flow is the user-goal level above requirements. A REQ is one operation (an endpoint, a
job); a flow is what an actor actually sets out to do, which usually spans several REQs.
In Cockburn's terms the REQs sit at subfunction level and the flow at sea level.

Flows live in `## Flows` inside the module file, above `## Requirements`. There is no
separate file type.

**The rule that makes them cheap: flows are navigational, never normative.** Every step
references a REQ, and no step may introduce behavior that is not specified in a REQ. The
test: if deleting the flow leaves some behavior unspecified, that behavior was written in
the wrong place. What flows legitimately own — and no test can express — is *why* the
feature exists, which steps repeat, and in what order things typically happen.

Ordering is the trap. "Steps 1-2 interleave freely" is an observation and belongs in the
flow. "Closing the delivery requires at least one scan" is a rule and belongs in the REQ;
the flow may only point at it. Diagnostic: if skipping a step makes the system return an
error, that ordering is a requirement.

### Writing one

Use `/flow-new`. You give it a rough prose description; it reads the generated index,
delegates coverage matching to the `flow-coverage` subagent, runs the checks that need no
input (vocabulary drift, two steps writing the same state), then asks you one batch of
questions about what genuinely cannot be derived — ordering, cardinality, interruption
semantics, retention.

Steps with no matching REQ get `???`. That is deliberate: `/flow-new` does not create the
missing requirements. It records them where the lint will keep surfacing them (W6 while
the flow is `draft`, E14 once it is `approved`), and you resolve them one at a time with
`/req-new` in a clean context. Writing four requirements back to back in one session
produces a fourth that is measurably worse than the first.

Set `flow_coverage: required` in a module header to turn on W5, which flags functional
REQs that no flow references. Leave it `optional` on infrastructure-heavy modules, where
most requirements legitimately sit outside any user journey.

## The generated index

Every lint run rewrites `requirements/.index.md`: one line per REQ and per flow,
`id | module | status | auth | route | title | aliases | flows`. It is committed, and CI
fails if it is stale — regenerate by running the lint.

Do not edit it. It exists so that an agent can locate a requirement across forty modules
by reading one file instead of forty, and so the reverse question — *which flows use this
REQ?* — is answerable at all.

`python tools/lint_requirements.py --emit-routes` prints the route → REQ table to stdout.
It is a human-facing view of data already in the index: read it when you want the API
surface at a glance, never commit it. Committing it would recreate the hand-maintained
routes table this replaced.

## Auth rejection tests are generated, not written

A REQ that declares `route` and `auth_required` implies its own "reject the
unauthenticated request" test. Writing that scenario by hand duplicates the auth
requirement in every module and means a change from 401 to 403 touches every file.

So: never write it. Generate one parametrized test from the index over every row with a
route and a non-`none` auth. W7 flags the duplicates; W8 flags a REQ that declares auth
without a route, which would otherwise silently drop out of that generated coverage.

Auth scenarios that legitimately stay in a REQ are the ones whose outcome depends on
something only that REQ knows: an authenticated user outside the resource's tenant, a
route readable anonymously but writable only when authenticated, or precedence between
an auth failure and a validation failure.


## What the Description is for

One sentence: `As a <actor>, I want <goal>, so that <benefit>.` Nothing else.

The default failure mode is a Description that paraphrases the scenarios — "the system
compares declared against counted quantities and records the discrepancies". It reads
like an explanation, which is why it survives review, but every clause of it is already
verified by a test. That is a second source of truth, and it drifts the first time a
scenario changes.

Apply the test clause by clause: **would a test still verify this sentence?** If yes, it
is a scenario restated. What survives is only what no test can express — why the feature
exists at all, and for whom.

Everything you are tempted to add beyond that sentence already has a home, and putting it
in one REQ's Description means the next REQ either repeats it or contradicts it:

| Tempted to write | Where it goes |
|---|---|
| a rule that holds across the module | `## Invariant rules` |
| what this module deliberately does not do | `## Out of scope` |
| a term that needs defining | `## Local glossary`, or the global one |
| an externally imposed constraint | `00_overview.md`, with its rationale |
| an implementation choice | an ADR — never a requirement |

For invariants and non-functional requirements the actor may be the system or an
operator. Keep the *so that* clause and relax the rest rather than contorting a database
constraint into a user story.

Note how this interacts with flows. A flow carries the intent of a whole journey, so once
flows exist the REQ's Description has a narrower job, not a broader one: the reason this
single operation exists, in one line. If a REQ's intent can only be explained by
describing the steps around it, that is a signal the flow is missing, not that the
Description should get longer.


## Tracing a red test back to a requirement

`files.test` points from a REQ to its tests. The reverse — a test fails in CI, which
requirement was that? — needs two conventions:

- the test function is named exactly after the scenario, which `AGENTS.md` already requires
- the test carries a `Covers: REQ-XXX-NNN` comment, and the module header lists its
  `test_dirs` so the lint scans them

With both in place, `python tools/lint_requirements.py --emit-testmap` prints
`scenario | REQ | file::function`. E15 catches a `Covers:` naming a REQ that does not exist.

W9 flags a named scenario with no matching test — but only once the REQ is past `draft`,
because a draft with no tests is normal and a permanently red CI is a CI nobody reads.
Tighten it to an error only when enough of your REQs are `tested` to make that realistic.

## Generated auth tests

`python tools/gen_auth_tests.py` reads the index and writes one parametrized test over
every route with a non-`none` `auth_required`. Do not hand-edit the output: change the
REQ and regenerate. CI runs it with `--check` and fails if the file is stale.

While no REQ declares a protected route the correct state is **no file at all**, so a
fresh repo ships an empty `tests/` and CI stays green. The file appears the first time a
REQ declares one, and is removed again if the last one goes away — `--check` treats all
three states as equally valid, it only compares against what the index says.

The three constants at the top of the script are the only stack-specific part — swap them
for pytest, JUnit, or whatever you use. The docstring carries a pytest example.

## Auditing a module

`req-reviewer` looks inside one REQ at a time. `/req-audit` looks between them: two REQs
mutating the same field without knowing about each other, two failure conditions that can
hold at once with no `error_precedence`, a `depends_on` no scenario exercises, an edge case
that lives in prose and in no test, a REQ nothing references and no flow reaches.

These are the defects that never surface while writing a single requirement, because each
one is individually well-formed — the defect is in the space between them. Run it once per
module when the module stabilises, not per requirement.

It runs on Sonnet deliberately. The checks are semantic, not textual: recognising that
"increments quantity" and "applies a delta to stock" touch the same field, when the two
REQs share no vocabulary and never cite each other, is the whole job. A weaker model
returns REQ pairs that share a noun, and an audit you have to double-check is an audit you
stop running.
