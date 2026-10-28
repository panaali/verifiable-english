"""Pinned Git reads in history-dependent tests must name content, not a VM commit."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{8,40}(?![0-9a-f])")
VM_ONLY_TAGS = frozenset({
    "lean-first/oracle-python", "ve-green-0315", "ve-green-0350", "ve-green-0510",
    "ve-green-0545", "ve-green-0725", "ve-green-1245", "ve-green-assist",
    "ve-green-english", "ve-green-lexicon", "ve-green-numbers", "ve-green-propose",
    "ve-green-v4", "ve-paper-v1", "ve-paper-v2", "archive/open-judges-fcd378c",
    "p1-results-v1",
})
# The oracle checks this optional tag only when it exists, and always verifies its frozen tree and file digests.
ALLOWED = {("tools/lean_first_oracle.py", "lean-first/oracle-python")}
OPS = frozenset({"show", "ls-tree", "archive", "diff", "rev-parse", "cat-file"})


def revision_literals(source: str) -> set[str]:
    """Follow literal assignments into calls that ask Git (or trust_map) for a revision."""
    tree = ast.parse(source)
    bindings = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if not isinstance(value, (ast.Constant, ast.Name, ast.JoinedStr)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    bindings.setdefault(target.id, []).append(value)

    def values(node, seen=frozenset()):
        if isinstance(node, ast.Name):
            return set().union(*(values(v, seen | {node.id}) for v in bindings.get(node.id, ()))) \
                if node.id not in seen else set()
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        return set().union(*(values(child, seen) for child in ast.iter_child_nodes(node)))

    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else \
            node.func.attr if isinstance(node.func, ast.Attribute) else ""
        args = node.args[0].elts if isinstance(node.args[0], (ast.List, ast.Tuple)) else node.args
        direct = [arg.value for arg in args[:3] if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
        git_call = ("git" in direct and bool(OPS.intersection(direct)) or
                    name in {"git", "_git"} and bool(OPS.intersection(direct)))
        if name == "measure_rev":
            args = node.args[:1]
        elif not git_call:
            continue
        for arg in args:
            for value in values(arg):
                found.update(HEX.findall(value))
                found.update(tag for tag in VM_ONLY_TAGS if tag in value)
    return found


def history_sources() -> list[str]:
    rows = json.loads((ROOT / "tests/history-dependent.json").read_text())["tests"]
    names = {row["test"] for row in rows}
    names.update(via.split(":", 1)[0] for row in rows for via in row["via"])
    return sorted(name for name in names if name.endswith(".py") and (ROOT / name).is_file())


def test_literal_revision_scanner_follows_a_frozen_loader():
    assert "9160d326" in revision_literals(
        'import subprocess\nREV = "9160d326"\n'
        'subprocess.check_output(["git", "show", f"{REV}:ve/norm_defaults.py"])\n')
    assert "9160d326" not in revision_literals('REV = "9160d326"\nrecord = {"commit": REV}\n')


def test_history_revisions_are_content_addressed():
    bad = []
    for name in history_sources():
        source = (ROOT / name).read_text()
        if not (HEX.search(source) or any(tag in source for tag in VM_ONLY_TAGS)):
            continue
        for literal in revision_literals(source):
            if (name, literal) in ALLOWED:
                continue
            if literal in VM_ONLY_TAGS:
                bad.append(f"{name}: VM-only tag {literal}")
                continue
            kind = subprocess.run(["git", "cat-file", "-t", literal], cwd=ROOT,
                                  capture_output=True, text=True).stdout.strip()
            if kind not in {"tree", "blob"}:
                bad.append(f"{name}: {literal} is {kind or 'absent'}; pin a tree or blob")
    assert bad == [], "\n".join(bad)
