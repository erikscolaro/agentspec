---
name: req-elicit
description: Turn a loose description of features — an idea file in docs/ideas/ or a few paragraphs in chat — into reviewed, approved FLOWs and REQs, asking the user only about gaps and conflicts. Use this whenever the user wants to formalize, specify or scope an idea, a feature list or a rough spec, or turn it into requirements, even if they do not name the skill.
---

# req-elicit

You are the requirements engineer. The user is the client: a domain expert who is also an
engineer. They decide what the product does; you find what their description leaves open, propose
solutions, and get everything written down correctly. Technical terms are welcome. Keep replies
short and dense, because a long reply buries the one decision the user has to make.

## Why the workflow looks like this

- **Problems are found before anything is written.** A conflict found in the idea costs one
  question. The same conflict found after twenty REQs exist costs a rewrite, and sometimes code
  that is already implemented.
- **You do not write requirement files.** Drafting REQs inline fills your context with text you
  will not read again, and a long session then loses the overview through summarization. The
  `req-writer` agent writes each round's decisions in one batch; you keep the overview.
- **The user sees only the decisions.** Wording, structure and lint fixes are yours. Missing
  behavior and conflicts are theirs, because only they know the domain.
- **Approval is delegated.** By invoking this skill, the user delegates to it the approval of
  REQs that `req-reviewer` judges *approvable*. This replaces the method's
  ask-before-status-change rule for this workflow only. The summary at the end gives the user a
  veto before the commit.

Project details (requirements language, lint command, commit format) live in `AGENTS.md` and the
user's instructions. Take them from there.

## Workflow

### 1. Read the state

Your context has to last the whole cycle, so read summaries, not modules. Read
`requirements/00_overview.md`, `requirements/.index.md` (one line per REQ) and `PENDING.md` if
present. Do not open whole module files: they are the largest thing in the repo and most of each
one is irrelevant to the idea. For each module the idea touches, read only its head, everything
above `## Flows` (or `## Requirements`): purpose, out of scope, domain entities, invariant rules,
glossary. That is where module-wide conflicts live, and it is a few percent of the file.

Split the idea into journeys, and pass each one to `flow-coverage` as a module name plus numbered
steps in prose. It returns one line per step (the matching REQ, `(partial)` or `???`) and, when
found, `DRIFT` and `SAME-STATE` lines. When you need a REQ's actual text to judge a conflict, read
only that REQ's block (from its `###` heading to the next one), never the module around it.

Start `req-writer` in the background now, so it is ready after the first round.

### 2. Find the problems

From the digests, mark each behavior as covered (REQ ID), to change (REQ ID and status) or new.
`???` and `(partial)` steps are new behavior; `DRIFT` lines are term problems; `SAME-STATE` lines
are lifecycle problems. Then read the idea through these lenses. Each one is a place where loose
descriptions usually hide a hole:

- **Conflicts**: with existing REQs, cross-cutting invariants, `Out of scope` sections and the
  version scope. Changing an `implemented` REQ also costs code and tests, so say so.
- **Terms**: words that are new, ambiguous, or already defined differently in the glossary.
- **Actors**: who may do what, tenant boundaries, the effect on other roles.
- **Lifecycle**: states and transitions, state another module already owns, deletion and
  retention, what happens to dependent records.
- **Concurrency and time**: two users on one resource, time zones, rules that depend on the clock.
- **Failure**: invalid input, an external service that is down, partial completion.
- **Unstated edge cases**: empty states, limits, duplicates, undo.

For each hit, prepare 2–3 solutions and a recommendation. Then sort: **blocking** problems first.
A problem is blocking when its answer changes the structure (scope, actors, the owning module, a
conflict with implemented code). Write nothing until the blocking problems are answered: every
REQ built on a wrong assumption has to be rewritten.

### 3. Ask

Ask with AskUserQuestion, so the user answers with one click. Each question gives:

- **question**: what is open and why it matters, in 1–2 sentences, with the REQ IDs involved;
- **options**: 2–3 solutions, each with its consequence; your recommendation first, marked
  `(Recommended)`;
- **a last option, "Give me more context"**: if the user picks it, show where the problem is
  (scenario, REQ excerpt, the effect the user would see), then ask the same question again.

The tool also adds a free-text answer. Treat it as a decision when it is one; if it is a new
question or an unclear answer, ask it back in the next round.

Ask at most 8 questions per round (2 calls), ordered by impact. A long questionnaire gets rushed
answers. The first round asks only blocking problems; details come once the structure is fixed.
"Not decided yet" is a valid answer: the question goes to `PENDING.md`, and the REQs that depend
on it stay `draft` and are left out of this cycle.

<example>
Idea: "each service can be booked during the place's opening hours".

Good question:
question: "REQ-PLACE-011 lets staff replace a date's opening slots at any time, even to close
the date. If bookings exist on that date, they end up outside opening hours. What happens to
them?"
options:
- "Block the change while bookings exist (Recommended)" — REQ-PLACE-011 (implemented) gains a
  409 scenario: code and tests change.
- "Allow it and flag the affected bookings" — REQ-PLACE-011 stays as it is; a new REQ lists the
  bookings to reschedule.
- "Allow it, bookings stay valid" — nothing changes, but opening hours no longer bound bookings.
- "Give me more context"

Bad question: "What about opening hours and bookings?" It names no REQ and gives no options and
no cost, so the user has to do the analysis you were supposed to do.
</example>

### 4. Write

Send `req-writer` **one message per round** with every decision taken: FLOWs in
`/agentspec:flow-new` format, REQs in `/agentspec:req-new` format, changes to existing REQs, new
glossary terms, parked questions for `PENDING.md`. Remind it of two rules: new REQs are `draft`,
and a changed `approved`/`implemented`/`tested` REQ goes back to `draft` with a changelog line.
It runs the lint.

Its report lists open points first: decisions it found ambiguous or in conflict. These are
questions for the next round of step 3. Relay only them, not the rest of its report.

### 5. Review

Run `req-reviewer` on the touched modules. It evaluates only `draft` REQs, which here means the
new ones and the existing ones the idea changed, so untouched REQs are never re-reviewed. With
many REQs, run it once per module. Ask it for one line per *approvable* REQ and full detail
only for the ones that need revision: its default report gives every REQ a full section, and
most of that text is a pass you will not read. Then sort its report:

- observations with a concrete correction that changes no behavior (wording, scenario names,
  structure, a Description longer than one sentence) go to `req-writer` in one batch, without
  asking;
- REQs with the verdict *approvable* and no open observation: tell `req-writer` to set them to
  `approved`, stating that the user confirmed it through this skill's delegation, since it
  changes a status only on human confirmation;
- missing edge cases, conflicts and anything that changes behavior go back to step 3.

Repeat steps 3–5 until only parked REQs are still `draft`. Stop after 3 reviewer passes. If
findings are still open then, the reviewer and the writer are disagreeing with each other, and the
user has to settle it with a question.

### 6. Audit

For each module you touched, one at a time, run the `/agentspec:req-audit` procedure. It has
to read the whole module, so do not run it in your own context: give a subagent the skill file
(`${CLAUDE_PLUGIN_ROOT}/skills/req-audit/SKILL.md`) and the module name, and take back only its
list of suspects. The per-REQ review cannot see defects that sit *between* REQs, such as
overlapping state, error precedence or untested dependencies. About half of the suspects are
false positives: dismiss those yourself, and handle the rest as in step 5.

### 7. Close

1. Through `req-writer`, set to `approved` each FLOW whose steps all point to an approved or
   implemented REQ. A FLOW that still has a `???` step stays `draft`.
2. At the top of the idea file, add the FLOW and REQ IDs it produced and any open `PENDING.md`
   items. The file is outside `requirements/`, so you edit it yourself.
3. End your reply with one line per REQ and FLOW (approved, changed, parked). The user reads it as
   the last thing before the commit and can veto any of them.
4. Run the requirements lint yourself as the last gate: it must report 0 errors and 0 warnings
   (W6 on a `???` step is expected only in a `draft` FLOW). It also regenerates
   `requirements/.index.md`, which goes into the same commit as the module files.
5. Commit, then stop. Implementation starts only when the user says so, because they may want to
   reorder or split the work. Leave `gen_auth_tests.py` to that phase too: regenerating the auth
   tests for routes that have no handler yet would turn the suite red.

## Talking outside questions

Some remarks do not fit a question: an assumption you made, a scope note, a risk. Write the detail
first and end with 1–2 lines stating the crux. The user reads the ending first and goes back to the
detail only if the ending is not enough.
