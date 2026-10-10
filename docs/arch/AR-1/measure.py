#!/usr/bin/env python3
"""AR-1's measured outcome, written to docs/arch/AR-1/evidence/manifests.json.

    python3 docs/arch/AR-1/measure.py BASE [HEAD]

Reads both audit manifests and lean/audit.py at BASE (the batch's merge base with main) and HEAD from git, and
the declaration list at HEAD: the manifest lines, theorems and imports before and after, every theorem added
(with its declaring module and what kind of theorem it is), every one removed (none: the new manifests list a
superset), the Prop-class instances Lean compiles as theorems, and the lines of the deleted theorem-name scan.
"""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import lean_statements  # noqa: E402

MANIFESTS = ("lean/VE/Audit.lean", "lean/ResponseShape/Audit.lean")
OUTPUT = Path(__file__).resolve().parent / "evidence/manifests.json"


def show(rev: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{path}"], capture_output=True, text=True,
                          check=True).stdout


def scan_lines(text: str) -> list[str]:
    """The theorem-name scan of the base's `scan_sources`: its `actual` set and the namespace and `theorem`
    regular expressions that filled it (lean/audit.py:80-112 in the plan, the word scans excepted)."""
    body = text.split("def scan_sources(root):", 1)[1].split("\n\n\n", 1)[0].splitlines()
    start = next(i for i, line in enumerate(body) if line.strip() == "scopes = []")
    end = body.index("    return actual, sources")
    return [line for line in body[:start] if "actual" in line] + body[start:end + 1]


def main(base: str, head: str = "HEAD") -> dict:
    declared, _ = lean_statements.declaration_list(ROOT / "lean/declarations.txt")
    kinds = {d.name: d.kind for constants in declared.values() for d in constants}
    module_of = {d.name: m for m, constants in declared.items() for d in constants}
    out = {"base": subprocess.run(["git", "-C", str(ROOT), "rev-parse", base], capture_output=True, text=True,
                                  check=True).stdout.strip(), "manifests": {}}
    before, after = set(), set()
    for manifest in MANIFESTS:
        old, new = show(base, manifest), show(head, manifest)
        b, a = (re.findall(r"^#print axioms (\S+)", t, re.M) for t in (old, new))
        out["manifests"][manifest] = {
            "lines_before": len(old.splitlines()), "lines_after": len(new.splitlines()),
            "theorems_before": len(b), "theorems_after": len(a),
            "imports_before": len(re.findall(r"^import ", old, re.M)),
            "imports_after": len(re.findall(r"^import ", new, re.M)),
            "hand_lines_before": [line for line in old.splitlines()
                                  if line and not line.startswith(("#print axioms ", "import "))]}
        before |= set(b)
        after |= set(a)

    def category(name: str) -> str:
        if re.search(r"(^|\.)inst[A-Z]", name):
            return "Prop-class instance"
        if kinds.get(name.rsplit(".", 1)[0]) in ("structure", "class"):
            return "Prop field of a structure"
        return "other"

    added = sorted(after - before)
    by = {}
    for name in added:
        by.setdefault(category(name), []).append(name)
    out["removed"] = sorted(before - after)
    out["added_count"] = len(added)
    out["added_by_category"] = {k: {"count": len(v), "roots": sorted({module_of[n].split(".")[0] for n in v})}
                                for k, v in sorted(by.items())}
    out["prop_class_instances"] = [{"name": n, "module": module_of[n]} for n in by.get("Prop-class instance", [])]
    deleted = scan_lines(show(base, "lean/audit.py"))
    out["theorem_regex_scan_deleted"] = {"lines": len(deleted), "text": deleted,
                                         "left_in_head": sum(line in show(head, "lean/audit.py").splitlines()
                                                             for line in deleted if "re.match" in line)}
    out["added"] = [{"name": n, "module": module_of[n], "category": category(n)} for n in added]
    return out


if __name__ == "__main__":
    result = main(*sys.argv[1:])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=1) + "\n")
    print({k: v for k, v in result.items() if k not in ("added", "manifests")})
