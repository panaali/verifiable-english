"""AR-16b evidence (not a test): every top-level definition of `ve/readings_verdicts.py` at the base is in exactly one
module of the package `ve/readings_verdicts/` at the head, with the same source text but for its indented relative
imports, which gain one leading dot (`from .x` becomes `from ..x`: the module is one package deeper). The two files' import
headers are compared separately: the union of names the package's modules import from outside it is the base's.
A comment line of the base outside every top-level statement is in the package as a whole line, and the package
has as many indented (lazy) imports as the base.

    python docs/arch/AR-16b/verbatim.py --base SHA [--head SHA] [--out FILE]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = "ve/readings_verdicts.py"


def show(rev: str, path: str) -> str:
    return subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, check=True, capture_output=True,
                          text=True).stdout


def package_files(rev: str) -> list[str]:
    out = subprocess.run(["git", "ls-tree", "--name-only", f"{rev}:ve/readings_verdicts/"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout.split()
    return [f"ve/readings_verdicts/{name}" for name in out if name.endswith(".py")]


def definitions(text: str) -> tuple[dict[str, str], dict[str, set[str]]]:
    """(each top-level definition's source text, from its first decorator or line, the imported names by module)."""
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    found, imported = {}, {}
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = ("." * node.level + (node.module or "")) if isinstance(node, ast.ImportFrom) else ""
            imported.setdefault(module, set()).update(a.asname or a.name for a in node.names)
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and node is tree.body[0]:
            continue  # the module docstring
        name = (node.targets[0].id if isinstance(node, ast.Assign) else
                "<if __name__>" if isinstance(node, ast.If) else node.name)
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        found[name] = "".join(lines[start - 1:node.end_lineno])
    return found, imported


def indented_imports(text: str) -> int:
    """The import statements below the top level (the lazy imports that break a cycle at run time)."""
    tree = ast.parse(text)
    top = {id(node) for node in tree.body}
    return sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) and id(node) not in top)


def top_level_comments(text: str) -> list[str]:
    """The comment lines outside every top-level statement (a comment above a definition, say): each must be in the
    package as a whole line."""
    tree = ast.parse(text)
    covered = {line for node in tree.body
               for line in range(min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])]),
                                 node.end_lineno + 1)}
    return [line for number, line in enumerate(text.splitlines(), 1)
            if number not in covered and line.lstrip().startswith("#")]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    base, base_imports = definitions(show(args.base, OLD))
    owners: dict[str, list[str]] = {}
    head: dict[str, str] = {}
    head_imports: dict[str, set[str]] = {}
    modules = {}
    for path in package_files(args.head):
        text = show(args.head, path)
        modules[path] = text.count("\n")
        found, imported = definitions(text)
        for name, source in found.items():
            owners.setdefault(name, []).append(path)
            head[name] = source
        for module, names in imported.items():
            if module.startswith(".."):  # outside the package: compare with the base's `.x` imports
                head_imports.setdefault(module[1:], set()).update(names)
            elif not module.startswith(".") and module != "__future__":
                head_imports.setdefault(module, set()).update(names)
    moved = {name: re.sub(r"(?m)^(\s+)from \.(?=[A-Za-z_.])", r"\1from ..", source) for name, source in base.items()}
    comments = top_level_comments(show(args.base, OLD))
    package_text = "".join(show(args.head, path) for path in package_files(args.head))
    errors = [f"{name}: in {owners.get(name, [])}" for name in base if len(owners.get(name, [])) != 1]
    errors += [f"top-level comment lost: {line}" for line in comments if line + "\n" not in package_text]
    errors += [f"{name}: its text changed" for name in base if name in head and head[name] != moved[name]]
    lazy = {"base": indented_imports(show(args.base, OLD)),
            "head": sum(indented_imports(show(args.head, path)) for path in package_files(args.head))}
    if lazy["base"] != lazy["head"]:
        errors.append(f"indented imports: base {lazy['base']}, head {lazy['head']}")
    added = sorted(set(head) - set(base))
    base_external = {module: names for module, names in base_imports.items() if module != "__future__"}
    if head_imports != base_external:
        errors.append(f"imports from outside the package differ: base {sorted((m, sorted(n)) for m, n in base_external.items())}"
                      f", head {sorted((m, sorted(n)) for m, n in head_imports.items())}")
    result = {"base": args.base, "head": subprocess.run(["git", "rev-parse", args.head], cwd=ROOT, check=True,
                                                         capture_output=True, text=True).stdout.strip(),
              "definitions": len(base), "moved_verbatim": sum(1 for n in base if n in head and head[n] == moved[n]),
              "top_level_comments": len(comments), "indented_imports": lazy,
              "added": added, "module_lines": modules,
              "errors": errors}
    text = json.dumps(result, indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    sys.stdout.write(text)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
