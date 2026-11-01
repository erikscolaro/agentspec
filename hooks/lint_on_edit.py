#!/usr/bin/env python3
"""PostToolUse hook for Claude Code.

Runs the requirements lint when the agent modifies a .md file under the project's requirements/.
Exit 0 if the file is unrelated or the lint passes.
Exit 2 if the lint fails: output goes to stderr and returns to the agent as feedback.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    file_path = Path(str((data.get("tool_input") or {}).get("file_path", "")))
    if file_path.suffix != ".md" or (project / "requirements") not in file_path.resolve().parents:
        return 0

    lint = Path(__file__).resolve().parent.parent / "tools" / "lint_requirements.py"
    result = subprocess.run(
        [sys.executable, str(lint)], cwd=project, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout + result.stderr, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
