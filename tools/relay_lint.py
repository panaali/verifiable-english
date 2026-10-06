"""Fail if a relayed module raises a content diagnostic of its own (docs/LEAN-FIRST-PLAN.md,
rule 2 and gate item 3).

A relayed module returns Lean's answer or raises Lean's diagnostic verbatim. It may build a
`VEError` only from text it received (a name, an attribute, a call result); it may not write
one: a `VEError` subclass called with a literal, an f-string, or an expression built from
them as its message is the module's own diagnostic. Operational failures
(`CheckerUnavailable` and its subclasses) are Python's own by rule 2 and are allowed, and so is a
file I/O failure (input bytes that cannot reach Lean, such as a file that is no UTF-8 text) when
the call carries the marker `# relay-lint: file I/O` on one of its lines; marked calls are counted
in the report.

Which classes are content diagnostics is read from Python itself: every subclass of
`ve.errors.VEError` reachable from the `ve` package, by the name a module calls it with
(imported name or attribute). The list of relayed modules is `RELAYED`; each batch that
relays a surface adds its modules (its row of section 5.2).

Usage: ``python tools/relay_lint.py [PATH ...]`` (default: `RELAYED`). Exit 1 on a finding.
"""
from __future__ import annotations

import ast
import importlib
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# The modules whose diagnostics are Lean's (batch 0: the relay itself; batch 3: the readings route;
# batch 4: discourse).
RELAYED = ("ve/backends/relay.py", "ve/readings_route.py", "ve/discourse.py",
           "ve/rights_route.py")
FILE_IO = "# relay-lint: file I/O"


def content_classes() -> frozenset[str]:
    """The names of every content diagnostic class: `VEError` subclasses that are not
    operational. Every `ve` module is imported so that each subclass is defined."""
    import ve
    from ve.errors import CheckerUnavailable, VEError
    for info in pkgutil.walk_packages(ve.__path__, "ve."):
        try:
            importlib.import_module(info.name)
        except Exception:  # noqa: BLE001  (optional dependencies; their classes are unreachable)
            continue
    names, todo = set(), [VEError]
    while todo:
        cls = todo.pop()
        if not issubclass(cls, CheckerUnavailable):
            names.add(cls.__name__)
        todo.extend(cls.__subclasses__())
    return frozenset(names)


def _own_text(node: ast.expr) -> bool:
    """Whether a message expression contains text written in the module."""
    if isinstance(node, ast.Constant):
        return isinstance(node.value, str)
    if isinstance(node, ast.JoinedStr):
        return True
    if isinstance(node, ast.BinOp):
        return _own_text(node.left) or _own_text(node.right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("format", "join"):
        return _own_text(node.func.value)
    return False


def _called_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def file_io(path: Path, node: ast.Call) -> bool:
    """Whether a call carries the file I/O marker on one of its source lines."""
    lines = path.read_text().splitlines()[node.lineno - 1:node.end_lineno]
    return any(line.rstrip().endswith(FILE_IO) for line in lines)


def findings(path: Path, classes: frozenset[str], marked: list | None = None) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _called_name(node.func) not in classes:
            continue
        if file_io(path, node):
            if marked is not None:
                marked.append(f"{path.name}:{node.lineno}")
            continue
        message = node.args[0] if node.args else next(
            (k.value for k in node.keywords if k.arg == "message"), None)
        if message is not None and _own_text(message):
            out.append(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}:{node.lineno}: "
                       f"{_called_name(node.func)} raised with the module's own text")
    return out


def main(argv: list[str] | None = None) -> int:
    paths = [Path(p).resolve() for p in (argv if argv else [str(ROOT / r) for r in RELAYED])]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        print("\n".join(f"relayed module not found: {p}" for p in missing))
        return 1
    classes = content_classes()
    marked: list[str] = []
    found = [f for p in paths for f in findings(p, classes, marked)]
    io = f"; {len(marked)} file I/O diagnostic(s): {', '.join(marked)}" if marked else ""
    print("\n".join(found) if found else f"PASS: {len(paths)} relayed module(s), no own content diagnostic{io}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
