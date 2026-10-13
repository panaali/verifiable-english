"""Measure the Rust search's wall-clock time against the size of its case (DRI decision ME1).

Each case runs alone in a fresh `ve jsonl -` process, with no timeout, and the row records the
case's size in bytes, its constants, the answer's status and models checked, and the wall time.
The cases are the countermodel searches the premise-scale pilots sent (recorded by
`--record`), and a synthetic series of ground-fact documents (H's shape: N integer constants each
stated equal to a numeral) searched to the model budget, the most a premise-check search does.

    uv run python docs/premise-scale/measure_rust_timeout.py --binary rust/target/release/ve \
        --out docs/premise-scale/evidence/rust-timeout.json CASES.jsonl...
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

SPEC = "ve-v0.2-expand2-2026-09-25"


def synthetic(n: int, copies: int = 1) -> dict:
    """A ground-fact order case with `n` integer constants, as the quantity route sends it: 20
    facts per premise (H's tables), the premises stated `copies` times (a larger case of the
    same vocabulary)."""
    constants = {f"c{i:04d}": {"sort": "$int", "description": f"quantity {i}"} for i in range(n)}
    premises = []
    for start in range(0, n, 20):
        facts = [["eq", ["const", f"c{i:04d}"], ["num", str(1000 + 7 * i)]] for i in range(start, min(n, start + 20))]
        premise = facts[-1]
        for fact in reversed(facts[:-1]):
            premise = ["and", fact, premise]
        premises.append(premise)
    return {"id": f"synthetic-{n}x{copies}", "environment": {
        "language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
        "spec_revision": SPEC, "vocabulary": {"sorts": {}, "predicates": {}, "constants": constants}},
        "premises": premises * copies, "conclusion": ["bottom"], "max_domain_size": 2, "min_domain_size": 0,
        "nonempty_domains": False, "max_models": 10_000, "max_evaluations": 100_000}


def run(binary: str, case: dict) -> dict:
    line = json.dumps(case, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"
    start = time.monotonic()
    proc = subprocess.run([binary, "jsonl", "-"], input=line, capture_output=True, check=False)
    wall = time.monotonic() - start
    try:
        row = json.loads(proc.stdout.decode().splitlines()[0])
    except (IndexError, ValueError):
        row = {"status": "no record", "error": proc.stderr[-200:].decode("utf-8", "replace")}
    return {"case": case["id"], "bytes": len(line),
            "constants": len(case["environment"]["vocabulary"].get("constants", {})),
            "status": row.get("status"), "models_checked": row.get("models_checked"),
            "wall_seconds": round(wall, 3)}


def fit(rows: list[dict]) -> dict:
    """Least squares seconds = a + b * N + c * N^2 (N the case's constants) over the rows that
    spent the model budget, the longest a premise-check search runs: each of its 10,000 candidate
    models assigns every constant, and the time grows faster than N (the synthetic series). The
    worst ratio of a measured time to the fit is reported with it."""
    points = [(r["constants"], r["wall_seconds"]) for r in rows if r["status"] == "ResourceLimit"]
    if len(points) < 3:
        return {"points": len(points)}
    # Normal equations of the three-parameter fit, by Gauss-Jordan elimination.
    basis = [lambda n: 1.0, lambda n: float(n), lambda n: float(n * n)]
    m = [[sum(f(n) * g(n) for n, _ in points) for g in basis] + [sum(f(n) * t for n, t in points)]
         for f in basis]
    for i in range(3):
        pivot = max(range(i, 3), key=lambda r: abs(m[r][i]))
        m[i], m[pivot] = m[pivot], m[i]
        for r in range(3):
            if r != i and m[i][i]:
                factor = m[r][i] / m[i][i]
                m[r] = [a - factor * b for a, b in zip(m[r], m[i])]
    a, b, c = (m[i][3] / m[i][i] for i in range(3))
    worst = max(t / max(a + b * n + c * n * n, 1e-9) for n, t in points)
    return {"points": len(points), "seconds": round(a, 4), "seconds_per_constant": round(b, 6),
            "seconds_per_constant_squared": round(c, 9), "worst_ratio_to_fit": round(worst, 3)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sizes", default="25,50,100,200,400,800")
    parser.add_argument("cases", nargs="*", type=Path)
    args = parser.parse_args()
    rows = []
    for path in args.cases:
        for number, line in enumerate(path.read_text().splitlines()):
            case = json.loads(line)["case"]
            case["id"] = f"{path.stem}#{number}"
            rows.append(run(args.binary, case))
            print(json.dumps(rows[-1]), flush=True)
    for n in map(int, args.sizes.split(",")):
        rows.append(run(args.binary, synthetic(n)))
        print(json.dumps(rows[-1]), flush=True)
    for copies in (2, 4, 8, 16):
        rows.append(run(args.binary, synthetic(25, copies)))
        print(json.dumps(rows[-1]), flush=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"binary": args.binary, "rows": rows, "fit": fit(rows)}, indent=1) + "\n")
    print(json.dumps(fit(rows)))


if __name__ == "__main__":
    main()
