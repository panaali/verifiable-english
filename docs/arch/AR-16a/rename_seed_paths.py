"""AR-16a, run once: the seeded-fault scripts of lean-first batches 16b to 16f name `ve/document.py` as the file of
each fault, beside the text the fault replaces. The split moved that text, verbatim, into one module of
`ve/document/`, so each such file name becomes the module that holds the text exactly once (the script fails if no
module or more than one does, or if the package holds the text more than once in all). A fault whose text the
base's `ve/document.py` no longer held is stale before the split: it keeps its file name and is listed. Only the
file names change: the faults, their texts and their tests are as written, and the batches' saved evidence (their
`mutants.json`) is a record of the runs at their own commits, kept as it is.

    python docs/arch/AR-16a/rename_seed_paths.py --base SHA [--check]
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = "ve/document.py"
SCRIPTS = ("docs/lean-first/b16b/mutants.py", "docs/lean-first/b16c/seed_faults.py",
           "docs/lean-first/b16d/seed_faults.py", "docs/lean-first/b16e/seed_faults.py",
           "docs/lean-first/b16f/seed_faults.py")


def holder(text: str, modules: dict[str, str]) -> str:
    counts = {path: source.count(text) for path, source in modules.items()}
    found = [path for path, n in counts.items() if n]
    if len(found) != 1 or counts[found[0]] != 1:
        raise SystemExit(f"{text!r}: held by {counts if found else 'no module'}, not once by one module")
    return found[0]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", required=True, help="the commit whose ve/document.py the scripts were written for")
    parser.add_argument("--check", action="store_true", help="report what would change; write nothing")
    args = parser.parse_args(argv)
    base = subprocess.run(["git", "show", f"{args.base}:{OLD}"], cwd=ROOT, check=True, capture_output=True,
                          text=True).stdout
    modules = {path.relative_to(ROOT).as_posix(): path.read_text()
               for path in sorted((ROOT / "ve/document").glob("*.py"))}
    report = {}
    for script in SCRIPTS:
        path = ROOT / script
        source = path.read_text()
        lines = source.splitlines(keepends=True)
        edits, stale = [], []  # (line, column, end column, new path); the stale faults' first lines
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.Tuple):
                continue
            items = node.elts
            for i, item in enumerate(items[:-1]):
                if isinstance(item, ast.Constant) and item.value == OLD:
                    old = items[i + 1]
                    if not (isinstance(old, ast.Constant) and isinstance(old.value, str)):
                        raise SystemExit(f"{script}:{item.lineno}: no fault text after {OLD!r}")
                    if item.lineno != item.end_lineno:
                        raise SystemExit(f"{script}:{item.lineno}: a file name over two lines")
                    if base.count(old.value) == 0:
                        stale.append(old.value.splitlines()[0].strip())
                        continue
                    edits.append((item.lineno, item.col_offset, item.end_col_offset, holder(old.value, modules)))
        for line, start, end, new in sorted(edits, reverse=True):
            text = lines[line - 1]
            assert text[start:end] == json.dumps(OLD), (script, line)
            lines[line - 1] = text[:start] + json.dumps(new) + text[end:]
        report[script] = {"renamed": len(edits), "modules": sorted({new for *_, new in edits}),
                          "stale_before_the_split": stale}
        if not args.check:
            path.write_text("".join(lines))
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
