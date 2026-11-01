# AGENTS.md

Method rules: injected by the agentspec plugin at session start; for other agents see `method/AGENTS-METHOD.md` in the agentspec repository.

Project-specific rules only. This file is always in context: keep it minimal.

## Conventions

- **Requirements language: {{REQUIREMENTS_LANGUAGE}}** <!-- REQ prose, reviewer reports and changelogs follow this setting. Chat language is whatever the user uses. -->
- **Tests live in**: `{{TEST_DIR}}`

## Commands

<!-- Verbatim commands, not descriptions. /agentspec:init fills these in. -->

| Action | Command |
|---|---|
| Full test suite | `{{TEST_COMMAND}}` |
| Single module tests | `{{TEST_MODULE_COMMAND}}` |
| Include slow tests | `{{TEST_SLOW_COMMAND}}` |
| Code lint | `{{LINT_COMMAND}}` |
| Format check | `{{FORMAT_COMMAND}}` |
| Requirements lint | `python3 tools/lint_requirements.py` |
| Generate auth route tests | `python3 tools/gen_auth_tests.py` |
| Scenario → REQ → test map (human only) | `python3 tools/lint_requirements.py --emit-testmap` |
| Route → REQ table (human only) | `python3 tools/lint_requirements.py --emit-routes` |

Slow/expensive tests run only before proposing `status: tested`, not on every iteration.

## Boundaries

### Never
- {{PROTECTED_PATHS}} <!-- generated or protected files the AI must not touch without a linked REQ, one bullet each; delete the line if none -->

## Project rules

- {{PROJECT_RULES}} <!-- extra project-specific rules, one bullet each; delete the section if none -->
