"""List every in-module layer declaration, Lean and Python, with its layer and reason; refuse a malformed one.

A Lean module declares its layer on its first line, `-- ve-layer: <1-5> (<reason>)`; a Python module or package
(its `__init__.py`) on its first line, `# ve-layer: <1-5> (<reason>)`. tools/layer_policy.py reads them before its
name rules (docs/ARCHITECTURE-LAYERS.md). One line per declaration: language, module, layer, reason and file.
Exits 1, naming each file, when a declaration is refused; tools/check_lean_imports.py and
tools/check_python_layers.py refuse the same ones.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from layer_policy import NAMES, ROOT, lean_declarations, lean_path, python_declarations


def rows(root: Path) -> tuple[list[str], list[str]]:
    """The listing's lines and the refusals, both sorted."""
    lean, lean_problems = lean_declarations(root)
    python, python_problems = python_declarations(root)
    lines = [f"lean {module} {layer} ({NAMES[layer]}) {lean_path(module)}: {reason}"
             for module, (layer, reason) in sorted(lean.items())]
    lines += [f"python {row} {layer} ({NAMES[layer]}) {path}: {reason}"
              for row, (layer, reason, path) in sorted(python.items())]
    return lines, sorted([*lean_problems, *python_problems])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="the checkout to read (default: this one)")
    args = parser.parse_args(argv)
    lines, problems = rows(args.root.resolve())
    for line in lines:
        print(line)
    print(f"{len(lines)} in-module layer declarations", file=sys.stderr)
    for problem in problems:
        print(f"layer declaration refused: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
