#!/usr/bin/env python3
"""PostToolUse hook for Claude Code.

Runs the requirements lint when the agent modifies a file under requirements/.
Exit 0 if the file is unrelated or the lint passes.
Exit 2 if the lint fails: output goes to stderr and returns to the agent as feedback.
"""

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    file_path = str((data.get("tool_input") or {}).get("file_path", ""))
    if "requirements/" not in file_path.replace("\\", "/"):
        return 0

    repo_root = Path(__file__).resolve().parent.parent.parent
    result = subprocess.run(
        [sys.executable, str(repo_root / "tools" / "lint_requirements.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout + result.stderr, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
