---
name: flow-new
description: Turn an informal description of a user journey into a FLOW block in a module's ## Flows section, with every step pointing to an existing REQ or marked ???. Use when the user asks to add, write or draft a flow, journey or workflow.
---

# New flow

A flow is navigational, never normative: every step points to a REQ, and no step introduces
behavior. The REQs own the rules; the flow owns why the journey exists, which steps repeat and
the typical order.

1. Read `requirements/_template_module.md` (the `## Flows` block is the reference structure) and
   the target module file. If the module is unclear, ask.
2. Split the description into numbered steps at the level of "what the actor does".
3. Delegate matching to the `flow-coverage` subagent: pass the module and the steps. Do not read
   `.index.md` or other modules yourself beyond what its digest cites.
4. From the digest, without asking:
   - **vocabulary drift**: use the REQ's wording in the step;
   - **same state**: two steps writing the same entity/field → keep both, add a Note naming it.
5. Ask the user ONE batch of questions, only about what cannot be derived: ordering (can steps
   interleave?), cardinality (which steps repeat?), interruption (what if the actor stops
   halfway?), retention. Skip the batch if nothing is open.
6. Write the block under `## Flows` (above `## Requirements`):
   - heading `### FLOW-<MODULE>-<NAME> — <goal>`, id uppercase `FLOW-<MODULE>-<NAME>` (letters,
     digits, hyphens); the yaml `id` equals the heading id, `module` equals the file header;
   - `actor` (a human role), `trigger`, `outcome`, `status: draft`;
   - **Narrative**: 2-4 sentences of why, no behavior;
   - **Steps**: numbered, each ending in `→ REQ-XXX-NNN`, or `→ ???` when the digest found none;
   - **Notes**: bullets, observations only, with a pointer to the REQ that enforces any ordering
     ("step 3 requires step 1 (enforced by REQ-XXX-004)"). If an answer from step 5 is a rule
     ("must reject when…") it belongs in a REQ: write `???` in the note and tell the user.
7. Do not create the missing REQs. List the `???` steps and suggest `/agentspec:req-new` for each,
   one at a time in a clean context.
8. Run `python3 "${CLAUDE_PLUGIN_ROOT}/tools/lint_requirements.py"`. W6 on `???` is expected
   while the flow is `draft`; anything else is yours to fix.
