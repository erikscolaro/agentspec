# AGENTS.md

Method rules: injected by the agentspec plugin at session start; for other agents see `method/AGENTS-METHOD.md` in the agentspec repository.

Project-specific rules only. This file is always in context: keep it minimal.

## Conventions

- **Requirements language: English** <!-- change here (e.g. Italian). REQ prose, reviewer reports and changelogs follow this setting. Chat language is whatever the user uses. -->

## Commands

<!-- Adapt to your stack. Verbatim commands, not descriptions. -->

| Action | Command |
|---|---|
| Full test suite | `<e.g. cargo test, pytest, npm test>` |
| Single module tests | `<…>` |
| Include slow tests | `<…>` |
| Code lint | `<…>` |
| Format check | `<…>` |
| Requirements lint | `python3 tools/lint_requirements.py` |
| Generate auth route tests | `python3 tools/gen_auth_tests.py` |
| Scenario → REQ → test map (human only) | `python3 tools/lint_requirements.py --emit-testmap` |
| Route → REQ table (human only) | `python3 tools/lint_requirements.py --emit-routes` |

Slow/expensive tests run only before proposing `status: tested`, not on every iteration.

## Boundaries

### Never
<!-- Add project-specific paths the AI must not touch without a linked REQ, e.g.: -->
<!-- - Touching `src/signature/crypto.rs` without an explicitly linked REQ -->
