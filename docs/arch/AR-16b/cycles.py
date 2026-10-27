"""AR-16b evidence (not a test): the import cycles among the `ve/` modules, from an `ast` walk.

    python docs/arch/AR-16b/cycles.py [--root DIR] [--out FILE]

Every `import` and `from ... import` statement of every `ve/**/*.py` file counts, at any depth (an indented, lazy
import too, since it closes a cycle at run time). A relative import is resolved against its file's package; `from P
import n` is an edge to the module `P.n` when that is a `ve` module, else to `P`. Only edges between `ve` modules are
kept, and no edge is added for the parent packages an import runs. The strongly connected components with more than
one module are the cycles. The output gives, for three readings of the same graph, the cycle sizes and the cycle
holding `ve.readings_verdicts` (the readings/document cycle):

- `raw`: each module a node.
- `readings_verdicts_as_one_module`: `ve.readings_verdicts.*` read as one module (the old `ve/readings_verdicts.py`),
  so a split that adds no cycle shows the same members before and after.
- `imports_by_owner`: an import of a name from a package's `__init__` that only re-exports it (`ve.document`,
  `ve.readings_verdicts`) is an edge to the submodule that defines the name, as if the importer named that
  submodule. A module of the package that is on the raw cycle but not on this one is on it only because callers
  import through the package's `__init__`, which imports every submodule.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

PACKAGES = ("ve.document", "ve.readings_verdicts")
SPLIT = "ve.readings_verdicts"


def module_of(path: Path, root: Path) -> str:
    parts = list(path.relative_to(root).with_suffix("").parts)
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def files_of(root: Path) -> dict[str, Path]:
    return {module_of(p, root): p for p in sorted((root / "ve").rglob("*.py")) if "__pycache__" not in p.parts}


def imports(root: Path) -> dict[str, list[tuple[str, str | None]]]:
    """Each module's imports of `ve` modules: (target module, the name imported from it, or None)."""
    files = files_of(root)
    out: dict[str, list[tuple[str, str | None]]] = {name: [] for name in files}
    for name, path in files.items():
        package = name.split(".") if path.name == "__init__.py" else name.split(".")[:-1]
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split(".")
                    while parts and ".".join(parts) not in files:
                        parts.pop()
                    if parts:
                        out[name].append((".".join(parts), None))
            elif isinstance(node, ast.ImportFrom):
                base = package[:len(package) - node.level + 1] if node.level else []
                base = ".".join([*base, *(node.module.split(".") if node.module else [])])
                for alias in node.names:
                    target = f"{base}.{alias.name}"
                    if target in files:
                        out[name].append((target, None))
                    elif base in files:
                        out[name].append((base, alias.name))
    return out


def reexports(root: Path, package: str) -> dict[str, str]:
    """The names a package's `__init__` imports from its own submodules: name → defining submodule."""
    files = files_of(root)
    path = files.get(package)
    if path is None or path.name != "__init__.py":
        return {}
    out = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            target = f"{package}.{node.module}"
            if target in files:
                for alias in node.names:
                    out[alias.asname or alias.name] = target
    return out


def graph(found: dict[str, list[tuple[str, str | None]]], owners: dict[str, dict[str, str]] | None = None
          ) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = {name: set() for name in found}
    for name, targets in found.items():
        for target, imported in targets:
            owner = (owners or {}).get(target, {}).get(imported) if imported is not None else None
            # A package's own `__init__` keeps its edges to its submodules.
            edges[name].add(owner if owner is not None and name != target else target)
    for name in edges:
        edges[name].discard(name)
    return edges


def components(edges: dict[str, set[str]]) -> list[list[str]]:
    """Tarjan's strongly connected components, iteratively."""
    index, low, on, stack, out, counter = {}, {}, set(), [], [], [0]
    for start in sorted(edges):
        if start in index:
            continue
        work = [(start, iter(sorted(edges[start])))]
        index[start] = low[start] = counter[0]
        counter[0] += 1
        stack.append(start)
        on.add(start)
        while work:
            node, children = work[-1]
            for child in children:
                if child not in index:
                    index[child] = low[child] = counter[0]
                    counter[0] += 1
                    stack.append(child)
                    on.add(child)
                    work.append((child, iter(sorted(edges[child]))))
                    break
                if child in on:
                    low[node] = min(low[node], index[child])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[node])
                if low[node] == index[node]:
                    component = []
                    while True:
                        member = stack.pop()
                        on.discard(member)
                        component.append(member)
                        if member == node:
                            break
                    out.append(sorted(component))
    return out


def collapsed(edges: dict[str, set[str]], package: str = SPLIT) -> dict[str, set[str]]:
    def one(name):
        return package if name == package or name.startswith(package + ".") else name
    out: dict[str, set[str]] = {}
    for name, targets in edges.items():
        out.setdefault(one(name), set()).update(one(t) for t in targets)
    for name in out:
        out[name].discard(name)
    return out


def summary(edges: dict[str, set[str]]) -> dict:
    cycles = sorted((c for c in components(edges) if len(c) > 1), key=lambda c: (-len(c), c))
    holding = next((c for c in cycles if SPLIT in c), [])
    return {"modules": len(edges), "edges": sum(map(len, edges.values())),
            "cycle_sizes": [len(c) for c in cycles], "readings_document_cycle": holding,
            "readings_document_cycle_size": len(holding)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    found = imports(root)
    raw = graph(found)
    owners = {package: reexports(root, package) for package in PACKAGES}
    by_owner = graph(found, owners)
    raw_summary, owner_summary = summary(raw), summary(by_owner)
    cycle, direct = set(raw_summary["readings_document_cycle"]), set(owner_summary["readings_document_cycle"])
    result = {"package_modules": {package: sorted(n for n in raw if n == package or n.startswith(package + "."))
                                  for package in PACKAGES},
              "raw": raw_summary, "readings_verdicts_as_one_module": summary(collapsed(raw)),
              "imports_by_owner": owner_summary,
              "on_the_cycle_only_through_a_package_init": sorted(
                  n for n in cycle - direct if any(n.startswith(p + ".") for p in PACKAGES))}
    text = json.dumps(result, indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
