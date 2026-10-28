"""Pinned Git reads in history-dependent tests must name content, not a VM commit."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])")
VM_ONLY_TAGS = frozenset({
    "lean-first/oracle-python", "ve-green-0315", "ve-green-0350", "ve-green-0510",
    "ve-green-0545", "ve-green-0725", "ve-green-1245", "ve-green-assist",
    "ve-green-english", "ve-green-lexicon", "ve-green-numbers", "ve-green-propose",
    "ve-green-v4", "ve-paper-v1", "ve-paper-v2", "archive/open-judges-fcd378c",
    "p1-results-v1",
})
ALLOWED = {
    # The oracle checks this optional tag only when it exists, and always verifies its frozen tree and file digests.
    ("tools/lean_first_oracle.py", "lean-first/oracle-python"), ("tools/lean_first_oracle.py", "saved:tag"),
    # VM measurement writers: their tests replace `git` and `MERGES` (test_test_speed_b2.py) or call only `table`
    # (test_select_tests.py), so no test hands these revisions to Git.
    *(("docs/test-speed-b2/shadow.py", short) for short in (
        "167eb8ff", "19c5bbe6", "29773091", "71088e15", "7345e3ed", "87900bdf", "abc30811", "c7e2000d", "c9b8cba6",
        "cbbab2df", "f1b719c7")),
    ("tools/select_tests_evidence.py", "saved:commit"), ("tools/select_tests_evidence.py", "saved:changed"),
}
OPS = frozenset({"show", "ls-tree", "archive", "diff", "diff-tree", "rev-parse", "cat-file", "log", "merge-base",
                 "rev-list", "name-rev", "describe"})
# A revision read from saved data (a JSON file) is reported as `saved:<key>`; a key naming content passes.
SAVED = "saved:"
CONTENT_KEY = re.compile(r"tree|blob|path|file")


def module_constants(sources: list[str]) -> dict[str, set[str]]:
    """Module-level string constants by name, for revisions read as another module's attribute."""
    found: dict[str, set[str]] = {}
    for source in sources:
        for node in ast.parse(source).body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and \
                    isinstance(node.value.value, str):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        found.setdefault(target.id, set()).add(node.value.value)
    return found


STRING_CALLS = frozenset({"join", "format", "strip", "removeprefix", "removesuffix", "str"})


def revision_literals(source: str, constants: dict[str, set[str]] | None = None) -> set[str]:
    """Follow assignments, in each function's scope, into calls that ask Git (or trust_map) for a revision: literal
    ids and tags, another module's constants, and revisions read from saved JSON (`saved:<key>`)."""
    tree = ast.parse(source)
    constants = constants or {}
    bindings: dict[tuple[ast.AST | None, str], list[ast.AST]] = {}
    scope_of: dict[ast.AST, ast.AST | None] = {}  # each node's innermost enclosing function (None: the module)

    def visit(node, scope):
        scope_of[node] = scope
        inner = node if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) else scope
        pairs = []
        if isinstance(node, ast.Assign):
            pairs = [(target, node.value) for target in node.targets]
        elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)) and node.value is not None:
            pairs = [(node.target, node.value)]
        elif isinstance(node, (ast.For, ast.comprehension)):
            pairs = [(node.target, node.iter)]
        for target, value in pairs:
            for name in ast.walk(target):
                if isinstance(name, ast.Name):
                    bindings.setdefault((scope, name.id), []).append(value)
        for child in ast.iter_child_nodes(node):
            visit(child, inner)

    visit(tree, None)

    def bound(node: ast.Name) -> tuple[tuple, list[ast.AST]]:
        scope = scope_of[node]
        key = (scope, node.id) if (scope, node.id) in bindings else (None, node.id)
        return key, bindings.get(key, [])

    names: dict[tuple, set[str]] = {}  # each name's values, once (an entry in progress is empty: a cycle)
    loaded: dict[tuple, bool] = {}

    def saved(node) -> bool:
        """Read from a JSON file: `json.load(s)(...)`, or a name, item or attribute of one."""
        if isinstance(node, ast.Call):
            func = node.func
            return isinstance(func, ast.Attribute) and func.attr in {"load", "loads"} and \
                isinstance(func.value, ast.Name) and func.value.id == "json"
        if isinstance(node, ast.Name):
            key, values_ = bound(node)
            if key not in loaded:
                loaded[key] = False
                loaded[key] = any(saved(v) for v in values_)
            return loaded[key]
        if isinstance(node, (ast.Subscript, ast.Attribute)):
            return saved(node.value)
        return False

    def values(node):
        if isinstance(node, ast.Name):
            key, values_ = bound(node)
            if key not in names:
                names[key] = set()
                names[key] = set().union(*(values(v) for v in values_))
            return names[key]
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        if isinstance(node, ast.Subscript):  # an element of the container, never its index
            if saved(node.value):
                return {f"{SAVED}{node.slice.value if isinstance(node.slice, ast.Constant) else '?'}"}
            return values(node.value)
        if isinstance(node, ast.Attribute):
            return constants.get(node.attr, set()) | values(node.value)
        if isinstance(node, ast.Dict):
            return set().union(*(values(v) for v in node.values if v is not None))
        if isinstance(node, ast.Call):  # a string built from its parts; any other call's result is opaque
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
            return set().union(*(values(child) for child in ast.iter_child_nodes(node))) \
                if name in STRING_CALLS else set()
        return set().union(*(values(child) for child in ast.iter_child_nodes(node)))

    def command(node):
        """The argument list a call passes: its first argument or `args=`, followed through a variable."""
        first = next((kw.value for kw in node.keywords if kw.arg == "args"), node.args[0] if node.args else None)
        for value in [first, *(bound(first)[1] if isinstance(first, ast.Name) else ())]:
            if isinstance(value, (ast.List, ast.Tuple)):
                return value.elts
        return node.args

    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else \
            node.func.attr if isinstance(node.func, ast.Attribute) else ""
        args = command(node)
        direct = [arg.value for arg in args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
        git_call = ("git" in direct or name in {"git", "_git"}) and bool(OPS.intersection(direct))
        if name == "measure_rev":
            args = node.args[:1]
        elif not git_call:
            continue
        for arg in args:
            for value in values(arg):
                if value.startswith(SAVED):
                    found.add(value)
                    continue
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
    assert "9160d326" in revision_literals(
        'subprocess.run(["git", "-C", "checkout", "show", "9160d326:file"])\n')


@pytest.mark.parametrize("source", [
    # Review F3 (gha-lineage): each form returned no revision.
    'subprocess.run(["git", "show", f"{report.B12_HEAD}:lean/trust.txt"])\n',
    'subprocess.run(["git", "log", "c24aeab..HEAD"])\n',
    'subprocess.run(["git", "merge-base", "HEAD", "c24aeab2"])\n',
    'subprocess.run(["git", "rev-list", "c24aeab2"])\n',
    'command = ["git", "show", "c24aeab2:f"]\nsubprocess.run(command)\n',
    'subprocess.run(args=["git", "show", "c24aeab2:f"])\n',
    'REV = "c24aeab2" if old else "HEAD"\nsubprocess.run(["git", "show", f"{REV}:f"])\n',
])
def test_the_scanner_finds_each_way_a_revision_is_written(source):
    found = revision_literals(source, {"B12_HEAD": {"c24aeab2"}})
    assert found & {"c24aeab", "c24aeab2"}, found


@pytest.mark.parametrize("source, key", [
    # Review F1 (gha-lineage): commit ids read from saved evidence reached Git.
    ('EVIDENCE = json.loads(text)\ngit("log", "--reverse", f"{EVIDENCE[\'base\']}..HEAD")\n', "base"),
    ('E = json.loads(t)\nreport = E["report_commit"]\n'
     'subprocess.check_output(["git", "log", f"{E[\'base\']}..{report}"])\n', "report_commit"),
    ('for entry in m["items"]:\n    row = json.loads(t)\n    prov = row["provenance"]\n'
     '    key = (prov["git_revision"], prov["path"])\n'
     '    subprocess.check_output(["git", "show", ":".join(key)])\n', "git_revision"),
])
def test_a_revision_read_from_saved_data_is_found(source, key):
    assert f"saved:{key}" in revision_literals(source)


def test_saved_content_names_and_pinned_blobs_pass():
    assert revision_literals('E = json.loads(t)\nsubprocess.run(["git", "ls-tree", E["tree"]])\n') == {"saved:tree"}
    found = revision_literals(
        'BLOBS = {("46be9e1bafc85e37456cbf56e9dc92b6c8178666", "a.jsonl"): "cd12f275d64c4ae80606a75191c78601aff2a5e0"}\n'
        'row = json.loads(t)\nkey = (row["git_revision"], row["path"])\n'
        'subprocess.check_output(["git", "cat-file", "blob", BLOBS[key]])\n')
    assert "46be9e1bafc85e37456cbf56e9dc92b6c8178666" not in found, found
    assert "cd12f275d64c4ae80606a75191c78601aff2a5e0" in found and not any(f.startswith("saved:") for f in found)


def test_history_revisions_are_content_addressed():
    bad = []
    names = history_sources()
    sources = {name: (ROOT / name).read_text() for name in names}
    constants = module_constants(list(sources.values()))
    for name in names:
        for literal in revision_literals(sources[name], constants):
            if (name, literal) in ALLOWED:
                continue
            if literal.startswith(SAVED):
                if not CONTENT_KEY.search(literal):
                    bad.append(f"{name}: a revision read from saved data [{literal[len(SAVED):]}]; save the "
                               "commit's tree and subject and find it with tests/lineage.py, or pin a blob")
                continue
            if literal in VM_ONLY_TAGS:
                bad.append(f"{name}: VM-only tag {literal}")
                continue
            kind = subprocess.run(["git", "cat-file", "-t", literal], cwd=ROOT,
                                  capture_output=True, text=True).stdout.strip()
            if kind not in {"tree", "blob"}:
                bad.append(f"{name}: {literal} is {kind or 'absent'}; pin a tree or blob")
    assert bad == [], "\n".join(bad)
