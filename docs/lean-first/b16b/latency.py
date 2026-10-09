"""Gate item 4 for 16b: `check_document` on the owned seed documents, in one checkout (run at the base and at the
head on the same host, one after the other).

    python docs/lean-first/b16b/latency.py OUT.json [--repeat N]

Imports `ve` from the current directory's checkout. Each owned seed of `conformance/document_wrapper.py` is
written once and checked `--repeat` times after one warm-up call (the service started, its build hashed). Per
document: the median and the largest wall time, the Python process's CPU, and the CPU of its child processes
(the Lean service and any Rust search), read from /proc at the clock tick and so given as the whole loop's total
divided by the number of calls.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import statistics
import sys
import tempfile
import time

TICK = os.sysconf("SC_CLK_TCK")
OWNED = ["plain", "mixed", "open-terms", "reading-sets", "graph-bridge", "graph-readings", "definitions",
         "p0-envelope", "alternatives-cells", "alternatives-graph", "risk"]


def children_cpu() -> float:
    total = 0
    for task in Path(f"/proc/{os.getpid()}/task").iterdir():
        for pid in (task / "children").read_text().split():
            try:
                fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            except FileNotFoundError:
                continue
            total += int(fields[11]) + int(fields[12])
    return total / TICK


def main(argv=None) -> int:
    args = argv or sys.argv[1:]
    out, repeat = Path(args[0]), int(args[args.index("--repeat") + 1]) if "--repeat" in args else 50
    sys.path.insert(0, os.getcwd())
    from conformance import document_wrapper as dw
    from ve.document import check_document
    generated = dict(dw._generated())
    rows = {}
    with tempfile.TemporaryDirectory() as directory:
        for name in OWNED:
            path = Path(directory) / f"{name}.ve.md"
            path.write_text(dw.text_of(generated[name]))
            check_document(path)
            walls, cpus = [], []
            child = children_cpu()
            for _ in range(repeat):
                own, start = time.process_time(), time.perf_counter()
                check_document(path)
                walls.append(time.perf_counter() - start)
                cpus.append(time.process_time() - own)
            rows[name] = {"wall_median": statistics.median(walls), "wall_max": max(walls),
                          "python_cpu_median": statistics.median(cpus),
                          "child_cpu_per_call": (children_cpu() - child) / repeat}
    out.write_text(json.dumps({"repeat": repeat, "load": os.getloadavg(), "documents": rows}, indent=1,
                              sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
