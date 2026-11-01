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

2. Report the created files and, separately, every `EXISTS, skipped` line. For a skipped
   `AGENTS.md` or `CLAUDE.md`, tell the user to merge `${CLAUDE_PLUGIN_ROOT}/template/<file>` by
   hand — do not merge it yourself. If the lint fails with `PyYAML missing`, say `pip install pyyaml`.

3. Remind the user of the three things to adapt, nothing else:
   - `requirements/00_overview.md`: vision, actors, constraints, invariants
   - `AGENTS.md`: the Commands table (test runner, code lint) and the requirements language
   - `tools/gen_auth_tests.py`: the three constants at the top emit a Rust/rstest example; rewrite
     them for the project's test framework before the first REQ declares a protected route
