---
name: req-audit
description: Audit one module for defects that live BETWEEN requirements - overlapping state, missing error precedence, untested dependencies, dead REQs. Read-only, returns a list of suspects. Use when the user asks to audit, review as a whole, or sanity-check a module's requirements.
model: sonnet
---

# Module audit

Defects inside a single REQ are `req-reviewer`'s job. This skill looks only at what happens
**between** REQs, which nobody checks by hand because it means holding the whole module in
mind at once.

Scope: **one module per invocation**. Never audit several modules together — the context
grows and the signal dilutes. If asked for more, do them one at a time and say so.

## Procedure

1. Read the module file in full, plus `00_overview.md` (invariants and glossary).
   Do NOT read other modules; cite their REQs by id if a check needs one.
2. Run each check below across all REQs of the module.
3. Report. Nothing else — no rewrites, no status changes, no file edits.

## Checks

1. **Overlapping state** — two REQs whose outcomes mutate the same entity or field, without
   either referencing the other. Say which field, and what the audit trail looks like after
   both have run. Beware the two REQs will describe it in different words and never name
   each other: that is exactly why this is worth checking.
2. **Missing error precedence** — two REQs (or two scenarios) whose failure conditions can
   hold simultaneously on the same request, where neither declares `error_precedence`. Name
   the request that triggers both.
3. **Untested dependency** — a `depends_on` that no scenario of the depending REQ exercises.
   Exception: the missing-token case, which is generated from `route` + `auth_required` and
   must NOT be flagged.
4. **Prose-only edge case** — a behavior stated in an **Edge cases** section with no scenario
   covering it. It is specified but untraceable and untested.
5. **Contradicted invariant** — a scenario whose Then violates a rule in the module's
   `## Invariant rules` or in `00_overview.md`'s cross-cutting invariants.
6. **Orphan** — a functional REQ that no other REQ references and no flow reaches. Usually
   either dead, or evidence that a flow is missing. Say which you think it is.
7. **Description drift** — a Description that describes behavior instead of intent. Only
   report it as a one-line aside per REQ; the deep version is `req-reviewer`'s job.

## Output

One line per suspect, grouped by check, nothing else:

```
OVERLAP   REQ-WAREHOUSE-001 + REQ-WAREHOUSE-002
          both change item.quantity; 001 via upsert, 002 via delta.
          after a receiving run the movement log is missing the 001 increment.
PRECEDENCE REQ-DOC-004
          a close on an empty delivery with a malformed id satisfies two failures; neither
          REQ says which wins.
```

Then a single closing line: how many suspects, and which one you would look at first.

No preamble, no summary of the module, no recommendations beyond naming the defect. Roughly
half of what you report will be dismissed on sight — that is expected, and it is why every
entry must be judgeable in one line. A long report is a failed report.

Say plainly when a check finds nothing. Do not manufacture findings to fill the shape.
