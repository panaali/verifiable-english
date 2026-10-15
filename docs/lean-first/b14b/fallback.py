"""Check that batch 14b leaves the retained Python norms route as the base had it.

    uv run python docs/lean-first/b14b/fallback.py OUT.json

Every corpus document (`corpus.py`, seed 14, 150 documents) was on the retained
Python route at the base. This records the same operations at the head with the
Lean route switched off, so every operation runs the retained Python, and
compares each answer with the base recording `evidence/base-corpus.json.gz`
(lf-14b review F2: the n-ary atom substitution reached the fallback). This is
batch evidence, checked at the batch gate and merge; it is not a permanent test.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(f"b14b_{name}", HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    _, out = sys.argv
    corpus, compare = load("corpus"), load("compare")
    import ve.norms
    ve.norms._lean_route = lambda document: False
    head = {"seed": 14, "count": 150, "records": list(corpus.records(14, 150))}
    result = compare.compare(compare.read(str(HERE / "evidence" / "base-corpus.json.gz")), head)
    result["route"] = "retained Python (Lean route switched off at the head)"
    Path(out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{result['records']} records; {len(result['differences'])} differences")
    raise SystemExit(0 if result["identical"] else 1)


if __name__ == "__main__":
    main()
