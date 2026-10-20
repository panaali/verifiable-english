"""AR-16a evidence (not a test): the import cycles among the `ve/` modules, from an `ast` walk.

    python docs/arch/AR-16a/cycles.py [--root DIR] [--out FILE]

Every `import` and `from ... import` statement of every `ve/**/*.py` file counts, at any depth (an indented, lazy
import too, since it closes a cycle at run time). A relative import is resolved against its file's package; `from P
import n` is an edge to the module `P.n` when that is a `ve` module, else to `P`. Only edges between `ve` modules are
kept, and no edge is added for the parent packages an import runs. The strongly connected components with more than
one module are the cycles: the output lists their sizes, the component holding `ve.document`, and the same component
with `ve.document.*` read as one module (the old `ve/document.py`), so a split that adds no cycle shows the same
modules before and after.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def module_of(path: Path, root: Path) -> str:
    parts = list(path.relative_to(root).with_suffix("").parts)
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def graph(root: Path) -> dict[str, set[str]]:
    files = {module_of(p, root): p for p in sorted((root / "ve").rglob("*.py")) if "__pycache__" not in p.parts}
    edges: dict[str, set[str]] = {name: set() for name in files}
    for name, path in files.items():
        package = name.split(".") if path.name == "__init__.py" else name.split(".")[:-1]
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split(".")
                    while parts and ".".join(parts) not in files:
                        parts.pop()
                    if parts:
                        edges[name].add(".".join(parts))
            elif isinstance(node, ast.ImportFrom):
                base = package[:len(package) - node.level + 1] if node.level else []
                base = ".".join([*base, *(node.module.split(".") if node.module else [])])
                for alias in node.names:
                    target = f"{base}.{alias.name}"
                    if target in files:
                        edges[name].add(target)
                    elif base in files:
                        edges[name].add(base)
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


def collapsed(edges: dict[str, set[str]], package: str = "ve.document") -> dict[str, set[str]]:
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
    holding = next((c for c in cycles if "ve.document" in c), [])
    return {"modules": len(edges), "edges": sum(map(len, edges.values())),
            "cycle_sizes": [len(c) for c in cycles], "document_cycle": holding,
            "document_cycle_size": len(holding)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    edges = graph(args.root.resolve())
    result = {"package_modules": sorted(n for n in edges if n == "ve.document" or n.startswith("ve.document.")),
              "raw": summary(edges), "document_as_one_module": summary(collapsed(edges))}
    text = json.dumps(result, indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
