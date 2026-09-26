"""Differential check of the documented dependency-order algorithm against Lean.

Usage (repo root, after `lake build`): python3 lean/VE/Route/examples/dag_differential.py
The reference below is written from docs/P0-Lean-NOTES.md ("Dependency order"),
not from the Lean source, so agreement checks that the documentation is exact.
P0-Py's `ve/background.py:dependency_order` should produce the same results.
"""
import json
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BINARY = ROOT / "lean/.lake/build/bin/ve_conformance"
ENV = {"language": "ve.core@0.2", "profiles": ["definitions@0", "norms@0", "relational-fol@0"],
       "spec_revision": "ve-v0.2-expand2-2026-09-25",
       "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}}


def dependency_order(nodes):
    names = [n["name"] for n in nodes]
    for name in names:
        if names.count(name) > 1:
            return {"status": "error", "error": f"DuplicateDeclaration: dependency node {name}"}
    node_set = set(names)
    deps = {n["name"]: [m for m in n["mentions"] if m in node_set] for n in nodes}
    placed = []
    while len(placed) < len(names):
        ready = [n for n in names if n not in placed and all(d in placed for d in deps[n])]
        if not ready:
            unplaced = sorted(n for n in names if n not in placed)
            return {"status": "error", "error": "DependencyCycle: " + ", ".join(unplaced)}
        placed.append(min(ready))
    return {"status": "ok", "order": placed}


def graph(rng):
    pool = [f"s{i}" for i in range(rng.randint(0, 9))] + ["base", "done"]
    names = rng.sample(pool, k=rng.randint(0, min(8, len(pool))))
    if names and rng.random() < 0.1:
        names.append(rng.choice(names))
    return [{"name": n, "mentions": rng.sample(pool, k=rng.randint(0, min(3, len(pool))))} for n in names]


def main():
    rng = random.Random(20260925)
    cases = [{"id": f"g{i}", "kind": "dependency-order", "environment": ENV, "nodes": graph(rng)}
             for i in range(200)]
    run = subprocess.run([str(BINARY), "route"], input=json.dumps(cases), capture_output=True, text=True)
    results = json.loads(run.stdout)
    bad = 0
    for case, result in zip(cases, results, strict=True):
        expected = {"id": case["id"], **dependency_order(case["nodes"])}
        if result != expected:
            bad += 1
            print("MISMATCH", case["nodes"], result, expected)
    kinds = [r["status"] for r in results]
    print(f"{200 - bad}/200 agree ({kinds.count('ok')} accepted, {kinds.count('error')} rejected)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
