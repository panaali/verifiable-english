"""Regenerate the isolated Lean CPU comparison for the eligibility harness.

The four runs alternate base/head then head/base.  Each Python process loads
``cpu_trace/sitecustomize.py`` through PYTHONPATH; that hook records the CPU
counter of each Lean service immediately before its owning process stops it.
The harness runs with ``--no-write``.  The raw service rows and stdout with
``/usr/bin/time``'s last line are kept in ``evidence/``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
RUNS = (("base", "first"), ("head", "second"),
        ("head", "first"), ("base", "second"))


def render() -> dict:
    runs = []
    for side, order in RUNS:
        source = EVIDENCE / f"lean-cpu-{side}-{order}.jsonl"
        services = [json.loads(line) for line in source.read_text().splitlines()]
        assert services and all(row["cpu_s"] >= 0 for row in services)
        output = (EVIDENCE / f"eligibility-{side}-{order}.log").read_bytes()
        payload, timing = output.rsplit(b"wall=", 1)
        timing = timing.decode().strip().split()
        wall = float(timing[0])
        runs.append({"side": side, "order": order, "services": len(services),
                     "lean_cpu_s": sum(row["cpu_s"] for row in services),
                     "wall_s": wall, "stdout_sha256": hashlib.sha256(payload).hexdigest()})
    assert len({row["stdout_sha256"] for row in runs}) == 1
    median = {side: {key: statistics.median(row[key] for row in runs if row["side"] == side)
                     for key in ("lean_cpu_s", "wall_s")} for side in ("base", "head")}
    cpu_ratio = median["head"]["lean_cpu_s"] / median["base"]["lean_cpu_s"]
    wall_ratio = median["head"]["wall_s"] / median["base"]["wall_s"]
    return {"runs": runs, "median": median,
            "lean_cpu_ratio": cpu_ratio, "wall_ratio": wall_ratio,
            "same_output": True, "within_budget": cpu_ratio <= 1.20 and wall_ratio <= 1.25}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = render()
    if args.write:
        (EVIDENCE / "lean-cpu.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
