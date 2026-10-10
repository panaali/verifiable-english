"""Measure the AR-9 split of the assist modules and write the evidence JSON.

    uv run python docs/arch/AR-9/measure.py BASE > docs/arch/AR-9/evidence/split.json

BASE is read from git; the head side is the working tree, which must be clean so the
recorded head commit is the code measured. For every definition of the base
`ve/assist/recovery.py` and `ve/assist/session.py` (module level, and the members of
their classes) the tool finds the head definition and compares the two syntax trees
(`ast.dump`, which ignores positions and comments), as written and again after mapping
each call through a service seam (`self._evaluate(...)`) back to the module name it reads
(`evaluate(...)`). It also checks that every name the
base modules defined is still an attribute of the same module, and counts lines and
function-level imports per file of `ve/assist/`.
"""
from __future__ import annotations

import ast
import copy
import importlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SPLIT = {"ve/assist/recovery.py": ("ve.assist.recovery", "RecoveryService"),
         "ve/assist/session.py": ("ve.assist.session", "AssistSession")}
MISSING = {"identical": False, "identical_up_to_seams": False}


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True,
                          text=True).stdout


def function_imports(tree: ast.AST) -> int:
    """Import statements nested inside a function body."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            count += sum(isinstance(inner, (ast.Import, ast.ImportFrom)) for inner in ast.walk(node))
    return count


def file_rows(sources: dict[str, str]) -> dict[str, dict]:
    return {path: {"lines": len(text.splitlines()), "function_imports": function_imports(ast.parse(text))}
            for path, text in sorted(sources.items())}


def named(statements) -> dict[str, ast.stmt]:
    """Definitions and assignments by the name they bind."""
    out = {}
    for stmt in statements:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[stmt.name] = stmt
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    out[target.id] = stmt
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            out[stmt.target.id] = stmt
    return out


class _Unseam(ast.NodeTransformer):
    """Map a call through a service seam back to the module name it reads."""
    def visit_Call(self, node):
        self.generic_visit(node)
        func = node.func
        if (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
                and func.value.id in ("self", "cls") and func.attr in SEAMS):
            if func.attr == "_operation_seconds" and not node.args and not node.keywords:
                return ast.Name(id=SEAMS[func.attr], ctx=ast.Load())
            node.func = ast.Name(id=SEAMS[func.attr], ctx=ast.Load())
        return node


SEAMS = {"_operation_seconds": "OPERATION_SECONDS", "_checked_wording": "checked_wording",
         "_evaluate": "evaluate", "_formula_to_data": "formula_to_data", "_formula_from_data": "formula_from_data"}


def same(head: ast.AST, base: ast.AST) -> dict:
    return {"identical": ast.dump(head) == ast.dump(base),
            "identical_up_to_seams": ast.dump(_Unseam().visit(copy.deepcopy(head))) == ast.dump(base)}


def compare(base_path: str, base_text: str, head_sources: dict[str, str]) -> tuple[list[dict], list[str]]:
    module_name, class_name = SPLIT[base_path]
    module = importlib.import_module(module_name)
    head_trees = {path: ast.parse(text) for path, text in head_sources.items()}
    head_modules = {path: named(tree.body) for path, tree in head_trees.items()}
    head_classes = {}
    for path, tree in head_trees.items():
        for stmt in tree.body:
            if isinstance(stmt, ast.ClassDef):
                head_classes[stmt.name] = (path, named(stmt.body))
    owners = [klass.__name__ for klass in getattr(module, class_name).__mro__[:-1]]
    rows, missing = [], []
    for name, node in named(ast.parse(base_text).body).items():
        if not hasattr(module, name):
            missing.append(name)
        if name == class_name:
            for member, member_node in named(node.body).items():
                found = next(((owner, *head_classes[owner]) for owner in owners
                              if owner in head_classes and member in head_classes[owner][1]), None)
                rows.append({"name": f"{class_name}.{member}", "base_file": base_path,
                             "head_file": found and found[1], "head_owner": found and found[0],
                             **(same(found[2][member], member_node) if found else MISSING)})
            continue
        found = next(((path, defs[name]) for path, defs in head_modules.items() if name in defs), None)
        rows.append({"name": name, "base_file": base_path, "head_file": found and found[0], "head_owner": None,
                     **(same(found[1], node) if found else MISSING)})
    return rows, missing


def main() -> int:
    base = git("rev-parse", sys.argv[1]).strip()
    head = git("rev-parse", "HEAD").strip()
    dirty = bool(git("status", "--porcelain", "--", "ve").strip())
    base_paths = [p for p in git("ls-tree", "--name-only", base, "ve/assist/").split() if p.endswith(".py")]
    base_sources = {p: git("show", f"{base}:{p}") for p in base_paths}
    head_sources = {p.relative_to(ROOT).as_posix(): p.read_text() for p in sorted((ROOT / "ve/assist").glob("*.py"))}
    sys.path.insert(0, str(ROOT))
    functions, missing = [], {}
    for base_path in SPLIT:
        family = {p: t for p, t in head_sources.items() if Path(p).stem.split("_")[0] == Path(base_path).stem}
        rows, absent = compare(base_path, base_sources[base_path], family)
        functions += rows
        missing[SPLIT[base_path][0]] = absent
    print(json.dumps({"base": base, "head": head, "dirty": dirty,
                      "files": {"base": file_rows(base_sources), "head": file_rows(head_sources)},
                      "definitions": functions, "missing_names": missing}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
