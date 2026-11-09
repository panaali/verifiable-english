"""The path a Python expression builds, as far as its own file says: the one evaluator of path expressions.

`path_of` evaluates an expression (`Path(__file__).resolve().parents[1] / "tools" / "gate.py"`, `os.path.join(root,
"lean", "VE")`, `ROOT.joinpath("a", "b")`, `"lean/VE/" + "A.lean"`) with the values a file assigns to its names
(`assignments`, looked up where the expression stands). tools/history_tests.py finds the scripts a test runs with
it; tools/select_tests.py (`built_paths`) finds the paths a test's source names in pieces.
"""
from __future__ import annotations

import ast
from collections.abc import Callable
import os

Values = Callable[[str], list[ast.AST]]


def callee(call: ast.Call) -> str:
    """The name a call calls: `f` in `f(x)` and in `m.f(x)`; "" for any other callee."""
    return call.func.attr if isinstance(call.func, ast.Attribute) else (
        call.func.id if isinstance(call.func, ast.Name) else "")


def assignments(tree: ast.AST) -> dict[tuple[str, str], list[ast.AST]]:
    """The values assigned to each name in each code object, by (qualified name of the code object, name): a
    module's own names under "<module>", a function's under its qualified name (`f`, `C.m`, `f.<locals>.g`)."""
    assigned: dict[tuple[str, str], list[ast.AST]] = {}

    def visit(node, scope: str, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                visit(child, prefix + child.name, prefix + child.name + ".<locals>.")
            elif isinstance(child, ast.ClassDef):
                visit(child, prefix + child.name, prefix + child.name + ".")
            else:
                if isinstance(child, (ast.Assign, ast.AnnAssign, ast.NamedExpr)) and child.value is not None:
                    for target in child.targets if isinstance(child, ast.Assign) else [child.target]:
                        if isinstance(target, ast.Name):
                            assigned.setdefault((scope, target.id), []).append(child.value)
                visit(child, scope, prefix)

    visit(tree, "<module>", "")
    return assigned


def path_of(node, values: Values, file: str, depth: int = 0) -> tuple[str | None, bool]:
    """The path an expression makes, as far as this file says: `(text, True)` relative to the root when it is
    built from `__file__` (`Path(__file__).resolve().parents[1] / "tools" / "gate.py"`), `(text, False)` for
    literal parts after an unknown base, `(None, False)` when the source does not say. `values(name)` gives the
    values the file assigns to a name where the expression stands."""
    if depth > 8:
        return None, False
    recurse = lambda inner: path_of(inner, values, file, depth + 1)  # noqa: E731
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, False
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return file, True
        found = values(node.id)
        return recurse(found[0]) if len(found) == 1 else (None, False)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        (left, anchored), (right, _) = recurse(node.left), recurse(node.right)
        if right is None:
            return None, False
        if left is None:
            return right, False
        return os.path.normpath(os.path.join(left, right)), anchored
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):  # "lean/VE/" + "A.lean": both known
        (left, anchored), (right, _) = recurse(node.left), recurse(node.right)
        return (left + right, anchored) if left is not None and right is not None else (None, False)
    if isinstance(node, ast.Call):
        if callee(node) in ("Path", "PurePath", "str", "fspath", "resolve", "absolute", "realpath", "abspath") \
                and len(node.args) <= 1:
            inner = node.args[0] if node.args else (node.func.value if isinstance(node.func, ast.Attribute)
                                                    else None)
            return recurse(inner) if inner is not None else (None, False)
        if callee(node) in ("join", "Path", "PurePath", "joinpath") and node.args:
            base = [node.func.value] if callee(node) == "joinpath" and isinstance(node.func, ast.Attribute) else []
            parts = [recurse(argument) for argument in [*base, *node.args]]
            if all(text is not None for text, _ in parts):
                return os.path.normpath(os.path.join(*(text for text, _ in parts))), parts[0][1]
            known = parts[max(index for index, (text, _) in enumerate(parts) if text is None) + 1:]
            if known:  # as `/`: the literal parts after an unknown base (`os.path.join(root, "lean", "VE")`)
                return os.path.normpath(os.path.join(*(text for text, _ in known))), False
        return None, False
    if isinstance(node, ast.Attribute) and node.attr == "parent":
        text, anchored = recurse(node.value)
        return (os.path.dirname(text) or ".", anchored) if text is not None else (None, False)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == "parents" \
            and isinstance(node.slice, ast.Constant) and type(node.slice.value) is int:
        text, anchored = recurse(node.value.value)
        if text is None:
            return None, False
        for _ in range(node.slice.value + 1):
            text = os.path.dirname(text) or "."
        return text, anchored
    return None, False


def builds(node) -> bool:
    """Whether an expression builds a path from parts: a `/` or `+` of two, or a join call."""
    return isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.Add)) \
        or isinstance(node, ast.Call) and (callee(node) in ("join", "joinpath")
                                           or callee(node) in ("Path", "PurePath") and len(node.args) > 1)


def built_paths(source: str, file: str) -> frozenset[str]:
    """Every path a Python source (of `file`, root-relative) builds by a join of parts it gives: the path of
    each outermost path-building expression (`builds`), `ROOT / "lean" / "VE" / "Time" / "Calendar.lean"` is
    lean/VE/Time/Calendar.lean. A part of a bigger join is no path of its own (`ROOT / "lean" / "VE" / "A.lean"`
    names lean/VE/A.lean, not lean/VE; nor does a `joinpath` receiver). None when the source does not parse."""
    try:
        tree = ast.parse(source, file)
    except (SyntaxError, ValueError):
        return frozenset()
    assigned = assignments(tree)
    found: set[str] = set()

    def visit(node, parent, scopes: list[str], prefix: str) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            inner = ".<locals>." if not isinstance(node, ast.ClassDef) else "."
            for child in ast.iter_child_nodes(node):  # decorators, defaults and bases run outside
                if child not in node.body:
                    visit(child, node, scopes, prefix)
            for statement in node.body:
                visit(statement, node, [*scopes, prefix + node.name], prefix + node.name + inner)
            return
        part = builds(parent) or isinstance(parent, ast.Attribute) and parent.attr == "joinpath"
        if builds(node) and not part:
            values = lambda name: next((assigned[(scope, name)] for scope in reversed(scopes)  # noqa: E731
                                        if (scope, name) in assigned), [])
            text, _ = path_of(node, values, file)
            if text is not None:
                found.add(text)
        for child in ast.iter_child_nodes(node):
            visit(child, node, scopes, prefix)

    visit(tree, None, ["<module>"], "")
    return frozenset(found)
