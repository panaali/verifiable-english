"""AR-14 counts of one checkout: layer exceptions, layer rows, import cycles, indented imports, `import ve`.

    uv run python docs/arch/AR-14/measure.py ROOT --out FILE

ROOT is a checkout (the merge base's worktree or this one). The cycles are `scc.py` (the architecture pass's
script, copied unchanged); `import ve` runs in ROOT (its own `ve/`, first on the path) with `python -X importtime` RUNS times and keeps the median.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys

HERE = Path(__file__).resolve().parent
RUNS = 15


def layer_rows(root: Path) -> dict:
    """The names in `tools/layer_policy.py`'s `PYTHON` table, per layer (a package's name counts once)."""
    tree = ast.parse((root / "tools/layer_policy.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and [getattr(t, "id", None) for t in node.targets] == ["PYTHON"]:
            table = {}
            for key, value in zip(node.value.keys, node.value.values):
                names = value.elts if isinstance(value, ast.List) else None
                if names is None:  # "a b c".split() or ("a " "b").split()
                    names = [ast.Constant(n) for n in value.func.value.value.split()]
                table[key.value] = sorted(n.value for n in names)
            return {"per_layer": {str(k): len(v) for k, v in table.items()},
                    "total": sum(len(v) for v in table.values())}
    raise ValueError("no PYTHON table")


def indented_imports(root: Path) -> dict:
    """Import statements below column 0 in `ve/` (all, and relative ones: the plan's 646)."""
    every = relative = 0
    files = set()
    for path in sorted((root / "ve").rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.Import, ast.ImportFrom)) and node.col_offset > 0:
                every += 1
                if isinstance(node, ast.ImportFrom) and node.level:
                    relative += 1
                    files.add(path.relative_to(root).as_posix())
    return {"indented": every, "indented_relative": relative, "files_with_indented_relative": len(files)}


def cycles(root: Path) -> dict:
    out = subprocess.run([sys.executable, "-I", str(HERE / "scc.py"), str(root)], capture_output=True, text=True,
                         check=True).stdout
    sizes = json.loads(re.search(r"SCC sizes: (\[[^\]]*\])", out).group(1))
    groups = re.findall(r"^\d+ (\[.*\])$", out, re.M)
    return {"sizes": sizes, "output": out.splitlines()[0], "largest": [ast.literal_eval(g) for g in groups[:2]]}


def import_ve(root: Path) -> dict:
    probe = ("import sys, ve; m = sorted(n for n in sys.modules if n == 've' or n.startswith('ve.')); "
             "print(len(m)); print(' '.join(m)); print('ve.english' in sys.modules, 've.parser' in sys.modules)")
    lines = subprocess.run([sys.executable, "-c", probe], cwd=root, capture_output=True, text=True,
                           check=True).stdout.splitlines()
    times = []
    for _ in range(RUNS):
        err = subprocess.run([sys.executable, "-X", "importtime", "-c", "import ve"], cwd=root,
                             capture_output=True, text=True, check=True).stderr
        times.append(int(next(line.split("|")[1] for line in err.splitlines() if line.split("|")[-1].strip() == "ve")))
    english, parser = lines[2].split()
    return {"modules": int(lines[0]), "module_names": lines[1].split(), "loads_english": english == "True",
            "loads_parser": parser == "True", "cumulative_us_median": int(statistics.median(times)),
            "cumulative_us_runs": times}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True,
                          check=True).stdout.strip()
    exceptions = json.loads((root / "tools/layer-exceptions.json").read_text())
    record = {"commit": head, "python": sys.version.split()[0],
              "exceptions": {"count": len(exceptions), "edges": sorted(exceptions)},
              "layer_rows": layer_rows(root), "cycles": cycles(root), "indented_imports": indented_imports(root),
              "import_ve": import_ve(root)}
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k not in {"exceptions", "cycles", "import_ve"}}))
    print(record["exceptions"]["count"], record["cycles"]["sizes"], record["import_ve"]["modules"],
          record["import_ve"]["cumulative_us_median"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
