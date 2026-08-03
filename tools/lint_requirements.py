#!/usr/bin/env python3
"""Lint for the files under requirements/.

Mechanically validates the methodology rules:
  E1  unparsable YAML block
  E2  heading and id field do not match
  E3  invalid id format (expected REQ-<PREFIX>-<number>)
  E4  duplicate id
  E5  status not allowed
  E6  priority not allowed
  E7  type not allowed
  E8  depends_on points to a non-existent id
  E9  status: tested but files.test empty
  E10 REQ module field differs from the file's module header
  E11 path in files.src/files.test does not exist in the repository
  E12 code (in modules' owner_dir) references a non-existent REQ
  E13 REQ heading at the wrong level (must be ### h3, nested under ## Requirements)
  W1  unresolved pending_refs
  W2  file with REQs but no module header
  W3  deprecated REQ referenced in depends_on of an active REQ
  W4  REQ heading has no descriptive title (### REQ-ID - Title)

Exit code 1 on errors, 0 on warnings only or clean.
Files prefixed with "_" are ignored. 00_overview.md does not require a module header.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML missing: pip install pyyaml")

REPO_ROOT = Path(__file__).resolve().parent.parent
REQ_DIR = REPO_ROOT / "requirements"

ID_RE = re.compile(r"^REQ-[A-Z0-9]+-\d+$")
HEADING_RE = re.compile(r"^(#{1,4})\s+(REQ-[A-Z0-9]+-\d+)(?:\s*[-–—]\s*(.+?))?\s*$", re.MULTILINE)
FENCE_RE = re.compile(r"^```yaml\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
REQ_REF_RE = re.compile(r"REQ-[A-Z0-9]+-\d+")

REQ_HEADING_LEVEL = 3  # ### — nested under ## Requirements

STATUS_OK = {"draft", "approved", "implemented", "tested", "deprecated"}
PRIORITY_OK = {"low", "medium", "high"}
TYPE_OK = {"functional", "non_functional", "invariant"}

CODE_EXT = {
    ".rs", ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".rb", ".php", ".swift", ".sql", ".sh",
}


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def parse_file(path: Path, problems: list) -> tuple[dict | None, list[dict]]:
    """Returns (module_header, [req]) for a .md file."""
    text = path.read_text(encoding="utf-8")
    headings = [
        (m.start(), len(m.group(1)), m.group(2), (m.group(3) or "").strip())
        for m in HEADING_RE.finditer(text)
    ]
    module_header = None
    reqs = []

    for m in FENCE_RE.finditer(text):
        line = line_of(text, m.start())
        loc = f"{path.name}:{line}"
        try:
            data = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            problems.append(("E1", loc, f"unparsable YAML: {e}"))
            continue
        if not isinstance(data, dict):
            continue

        if "id" in data:
            # REQ heading immediately preceding the block
            prev = [h for h in headings if h[0] < m.start()]
            if prev:
                _, heading_level, heading_id, heading_title = prev[-1]
            else:
                heading_level = heading_id = heading_title = None
            reqs.append({
                "data": data, "loc": loc,
                "heading_id": heading_id, "heading_level": heading_level, "heading_title": heading_title,
            })
        elif "module" in data and module_header is None:
            module_header = {"data": data, "loc": loc}

    return module_header, reqs


def main() -> int:
    problems: list[tuple[str, str, str]] = []  # (code, location, message)
    all_reqs: dict[str, dict] = {}  # id -> {status, loc, depends_on}
    owner_dirs: set[str] = set()

    files = sorted(
        p for p in REQ_DIR.glob("*.md") if not p.name.startswith("_")
    )
    if not files:
        print(f"No files in {REQ_DIR}")
        return 0

    # Pass 1: parsing and local validations
    for path in files:
        module_header, reqs = parse_file(path, problems)

        if reqs and module_header is None and not path.name.startswith("00_"):
            problems.append(("W2", path.name, "file with REQs but no module header"))

        header_data = (module_header or {}).get("data", {})
        file_module = header_data.get("module")
        if header_data.get("owner_dir"):
            owner_dirs.add(str(header_data["owner_dir"]))

        for r in reqs:
            d, loc = r["data"], r["loc"]
            rid = str(d.get("id", ""))

            if not ID_RE.match(rid):
                problems.append(("E3", loc, f"id '{rid}' does not match REQ-<PREFIX>-<number>"))
                continue
            if r["heading_id"] != rid:
                problems.append(("E2", loc, f"heading '{r['heading_id']}' ≠ id '{rid}'"))
            if r["heading_level"] is not None and r["heading_level"] != REQ_HEADING_LEVEL:
                problems.append(("E13", loc, f"{rid}: heading is h{r['heading_level']}, expected h{REQ_HEADING_LEVEL} (###)"))
            if not r["heading_title"]:
                problems.append(("W4", loc, f"{rid}: heading has no descriptive title (### {rid} - Title)"))
            if rid in all_reqs:
                problems.append(("E4", loc, f"duplicate id '{rid}' (already in {all_reqs[rid]['loc']})"))
                continue

            status = d.get("status")
            if status not in STATUS_OK:
                problems.append(("E5", loc, f"{rid}: status '{status}' not in {sorted(STATUS_OK)}"))
            if "priority" in d and d["priority"] not in PRIORITY_OK:
                problems.append(("E6", loc, f"{rid}: priority '{d['priority']}' not in {sorted(PRIORITY_OK)}"))
            if "type" in d and d["type"] not in TYPE_OK:
                problems.append(("E7", loc, f"{rid}: type '{d['type']}' not in {sorted(TYPE_OK)}"))

            if status == "tested":
                tests = (d.get("files") or {}).get("test") or []
                if not tests:
                    problems.append(("E9", loc, f"{rid}: status tested but files.test empty"))

            for kind in ("src", "test"):
                for entry in (d.get("files") or {}).get(kind) or []:
                    rel = str(entry).split("::")[0]  # tests/x.rs::function -> tests/x.rs
                    if not (REPO_ROOT / rel).exists():
                        problems.append(("E11", loc, f"{rid}: files.{kind} '{rel}' does not exist"))

            if file_module and d.get("module") != file_module:
                problems.append(("E10", loc, f"{rid}: module '{d.get('module')}' ≠ file header '{file_module}'"))

            pending = d.get("pending_refs") or []
            if pending:
                problems.append(("W1", loc, f"{rid}: {len(pending)} pending_refs to resolve"))

            all_reqs[rid] = {
                "status": status,
                "loc": loc,
                "depends_on": d.get("depends_on") or [],
            }

    # Pass 2: cross references
    for rid, info in all_reqs.items():
        for dep in info["depends_on"]:
            if dep not in all_reqs:
                problems.append(("E8", info["loc"], f"{rid}: depends_on '{dep}' does not exist"))
            elif all_reqs[dep]["status"] == "deprecated" and info["status"] != "deprecated":
                problems.append(("W3", info["loc"], f"{rid}: depends on '{dep}' which is deprecated"))

    # Pass 3: REQ references inside module code (owner_dir)
    seen_code_refs: set[tuple[str, str]] = set()
    for od in sorted(owner_dirs):
        base = REPO_ROOT / od
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if not (f.is_file() and f.suffix in CODE_EXT):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel_f = str(f.relative_to(REPO_ROOT))
            for m in REQ_REF_RE.finditer(content):
                ref = m.group(0)
                if ref not in all_reqs and (rel_f, ref) not in seen_code_refs:
                    seen_code_refs.add((rel_f, ref))
                    problems.append(("E12", f"{rel_f}:{line_of(content, m.start())}",
                                     f"code references unknown requirement '{ref}'"))

    # Report
    errors = [p for p in problems if p[0].startswith("E")]
    warnings = [p for p in problems if p[0].startswith("W")]

    for code, loc, msg in sorted(problems, key=lambda p: (p[0][0] != "E", p[1])):
        kind = "ERROR" if code.startswith("E") else "WARN "
        print(f"{kind} [{code}] {loc}  {msg}")

    print(
        f"\n{len(files)} files, {len(all_reqs)} requirements — "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
