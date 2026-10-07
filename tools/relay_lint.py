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
relays a surface adds its modules (its row of section 5.2). A `ve` module that only relayed
modules import is relayed with them (`helpers`), so a check cannot leave the lint by moving
into a module of its own.
An explicitly owned surface parser remains outside the relay even when only a
relayed file adapter imports it.

A second rule keeps the unspecified completion's `fill` in Lean (readings-defaults plan, RD-2b and D12): no
readings module (`ve/readings*.py`) holds a string literal containing a reserved completion name prefix
(`RESERVED`), so none builds a filled name. A literal that only keeps such names out of the English (a non-wording
guard) carries the marker `# relay-lint: non-wording` on its line; marked literals are counted in the report.

Usage: ``python tools/relay_lint.py [PATH ...]`` (default: `RELAYED`, and the readings modules for the second
rule; given paths, both rules read each path). Exit 1 on a finding.
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
# batch 4: discourse; batch 7: rights; batch 8: reports; batch 11b: speech source).
RELAYED = ("ve/backends/relay.py", "ve/readings_route.py", "ve/discourse.py",
           "ve/rights_route.py", "ve/reports.py", "ve/reports_route.py",
           "ve/backends/speech_source.py", "ve/speech_document.py")
# W2's English text-to-structure parser remains the experimental English E3
# owner. SpeechDocument only supplies its structured fence to Lean for checking.
OWNED_SURFACES = frozenset({"ve.speech_english"})
FILE_IO = "# relay-lint: file I/O"
# The modules that may not build the completion's names, and the reserved prefixes (norm-defaults 2.1).
READINGS_GLOB = "ve/readings*.py"
from ve.environment import RESERVED_PREFIXES as RESERVED  # noqa: E402  (one table with the checker's)
NON_WORDING = "# relay-lint: non-wording"


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


def _module_files() -> dict[str, Path]:
    """Every module of the `ve` package by dotted name."""
    files = {}
    for path in (ROOT / "ve").rglob("*.py"):
        parts = list(path.relative_to(ROOT).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        files[".".join(parts)] = path
    return files


def _imports(name: str, path: Path, files: dict[str, Path]) -> set[str]:
    """The `ve` modules `path` imports, at any depth of its code, by Python's own parser."""
    package = name.split(".") if path.name == "__init__.py" else name.split(".")[:-1]
    found = set()
    for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = package[:len(package) - node.level + 1] if node.level else []
            stem = ".".join(base + ([node.module] if node.module else []))
            found.add(stem)
            found.update(f"{stem}.{alias.name}" for alias in node.names)
    return {module for module in found if module in files and module != name}


def helpers(relayed: list[Path]) -> list[Path]:
    """The `ve` modules that only relayed modules import, found from the relayed ones: a check
    moved out of a relayed module into a module of its own is still the relayed surface's
    (lf-8 recheck B2: `ve/reports_preflight.py` held the reports relay's checks).
    Explicitly owned surface parsers are excluded from this import-closure rule."""
    files = _module_files()
    names = {path.resolve(): name for name, path in files.items()}
    graph = {name: _imports(name, path, files) for name, path in files.items()}
    importers: dict[str, set[str]] = {}
    for name, imported in graph.items():
        for module in imported:
            importers.setdefault(module, set()).add(name)
    covered = {names[p] for p in relayed if p in names}
    todo, found = list(covered), []
    while todo:
        for module in sorted(graph[todo.pop()]):
            if (module not in covered and module not in OWNED_SURFACES
                    and importers[module] <= covered and files[module].name != "__init__.py"):
                covered.add(module)
                todo.append(module)
                found.append(files[module])
    return found

def reserved_literals(path: Path, marked: list | None = None) -> list[str]:
    """Every string literal of the module (f-string parts and docstrings included) that contains a reserved
    completion prefix, read with Python's own parser; a literal whose line carries `NON_WORDING` is counted in
    `marked` instead."""
    lines = path.read_text().splitlines()
    tree = ast.parse("\n".join(lines), filename=str(path))
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and any(prefix in node.value for prefix in RESERVED)):
            continue
        if any(line.rstrip().endswith(NON_WORDING) for line in lines[node.lineno - 1:node.end_lineno]):
            if marked is not None:
                marked.append(f"{path.name}:{node.lineno}")
            continue
        out.append(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}:{node.lineno}: "
                   "a readings module holds a reserved completion name")
    return out


def main(argv: list[str] | None = None) -> int:
    paths = [Path(p).resolve() for p in (argv if argv else [str(ROOT / r) for r in RELAYED])]
    if not argv:
        paths += helpers(paths)
    readings = paths if argv else sorted(ROOT.glob(READINGS_GLOB))
    missing = [p for p in paths if not p.is_file()]
    if missing:
        print("\n".join(f"relayed module not found: {p}" for p in missing))
        return 1
    classes = content_classes()
    marked: list[str] = []
    guards: list[str] = []
    found = [f for p in paths for f in findings(p, classes, marked)]
    found += [f for p in readings for f in reserved_literals(p, guards)]
    io = f"; {len(marked)} file I/O diagnostic(s): {', '.join(marked)}" if marked else ""
    io += f"; {len(guards)} non-wording guard(s): {', '.join(guards)}" if guards else ""
    print("\n".join(found) if found else f"PASS: {len(paths)} relayed module(s), no own content diagnostic; "
          f"{len(readings)} readings module(s), no reserved completion name{io}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
