"""Time Python's regeneration of a captured `readings-validate` case (the copy `ve/readings_route.py` compares
with Lean's answer byte for byte), with its rights-route calls and Rust replays.

    VE_LEANFIRST_LOG=/tmp/lf.jsonl PYTHONPATH=docs/lean-first/hook \
        uv run --frozen python docs/lean-first/regenerate_case.py CASE.json OUT.json [--no-rust]

Prints wall and CPU seconds; OUT.json holds the answer in the route's row shape (without `id`), so it can be
compared with `ve_readings_route`'s output for the same case.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import resource
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def _children_cpu() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--no-rust", action="store_true")
    args = parser.parse_args()
    from ve.errors import VEError
    from ve.readings_route import rights_findings, rust_check
    from ve.readings_s1 import answer
    case = json.loads(args.case.read_text())[0]
    cpu, children = time.process_time(), _children_cpu()
    started = time.perf_counter()
    try:
        row = {"status": "ok", **answer(case["environment"], case["document"], chain_findings=rights_findings,
                                         rust=None if args.no_rust else rust_check)}
    except VEError as exc:
        row = {"status": "error", "error": exc.message if hasattr(exc, "message") else str(exc)}
    wall = time.perf_counter() - started
    args.out.write_text(json.dumps(row, ensure_ascii=False))
    print(json.dumps({"case": str(args.case), "wall_s": round(wall, 1),
                      "python_cpu_s": round(time.process_time() - cpu, 1),
                      "children_cpu_s": round(_children_cpu() - children, 1), "status": row["status"]}))


if __name__ == "__main__":
    main()
