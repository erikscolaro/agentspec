---
name: init
description: Set up agentspec in the current project - copies the requirements templates, AGENTS.md, CLAUDE.md, the lint scripts and the CI workflow. Never overwrites existing files. Invoke explicitly with /agentspec:init.
disable-model-invocation: true
---

# Initialize agentspec

1. From the project root, run exactly this (it copies the template and never overwrites):

   ```bash
   P="${CLAUDE_PLUGIN_ROOT}"
   copy() { if [ -e "$2" ]; then echo "EXISTS, skipped: $2"; else mkdir -p "$(dirname "$2")" && cp "$1" "$2" && echo "created: $2"; fi; }
   (cd "$P/template" && find . -type f) | while read -r f; do copy "$P/template/$f" "${f#./}"; done
   for s in lint_requirements.py gen_auth_tests.py; do copy "$P/tools/$s" "tools/$s"; done
   python3 tools/lint_requirements.py
   ```

2. Report the created files and every `EXISTS, skipped` line. If the lint fails with
   `PyYAML missing`, say `pip install pyyaml`. For a skipped `CLAUDE.md`, tell the user to merge
   `${CLAUDE_PLUGIN_ROOT}/template/CLAUDE.md` by hand.

3. **Analyze the project.** Read the configuration files present at the root (`Cargo.toml`,
   `package.json`, `pyproject.toml`, `go.mod`, `Makefile`, `pom.xml`, `build.gradle` and similar)
   and deduce: full test command, single-module test command, slow-tests command, code lint,
   format check, and the test directory.

4. **Short questionnaire.** One `AskUserQuestion` call, at most 4 questions, each with proposed
   options (the free "Other" answer is always available). Skip any question already answered with
   certainty by step 3.
   - Requirements language (English, Italian, ...).
   - Confirm or correct the deduced commands (propose the deduced set as the first option).
   - Generated or protected files the AI must not touch (propose the generated paths you found).
   - Extra project rules, if any ("none" as an option).

5. **Fill in `AGENTS.md`.** Replace every `{{...}}` placeholder of
   `${CLAUDE_PLUGIN_ROOT}/template/AGENTS.md` with the answers; drop the Never bullet or the
   Project rules section when the answer is "none". Show the result to the user and save it only
   after confirmation. If `AGENTS.md` already existed (skipped in step 1), do not overwrite it:
   show the differences with the filled-in template and let the user choose what to merge.

6. Remind the user of what is left to adapt, nothing else:
   - `requirements/00_overview.md`: vision, actors, constraints, invariants
   - `tools/gen_auth_tests.py`: the three constants at the top emit a Rust/rstest example; rewrite
     them for the project's test framework before the first REQ declares a protected route
