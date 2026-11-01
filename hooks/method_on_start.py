#!/usr/bin/env python3
"""SessionStart hook for Claude Code.

Injects the agentspec method rules (method/AGENTS-METHOD.md) as additional context, only in
projects that use agentspec, i.e. that have requirements/00_overview.md. Elsewhere prints nothing.
"""

import json
import os
import sys
from pathlib import Path


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}

    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
    if not (project / "requirements" / "00_overview.md").is_file():
        return 0

    method = Path(__file__).resolve().parent.parent / "method" / "AGENTS-METHOD.md"
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": method.read_text(encoding="utf-8"),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
