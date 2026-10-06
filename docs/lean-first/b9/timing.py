"""Per-operation wall and CPU of the W6 public operations, for the latency item of the batch-9 gate.

    PYTHONPATH=CHECKOUT python docs/lean-first/b9/timing.py CORPUS.json.gz OUT.json [--limit N]

Replays the quantity corpus (`docs/lean-first/quantity-corpus.json.gz`) in one process with the
checkout on PYTHONPATH (the base or the head), under the default authority, and writes for each
operation the call count and the p50, p95 and total of its wall time, plus the process CPU and the
CPU of its children (the Lean service, counted when the pool is closed at the end). The first call of
each operation is not timed separately: the service start is in the totals. Run base and head back to
back on the same host; compare CPU where the host is loaded.
"""
from __future__ import annotations

import gzip
import json
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))


def main(corpus_path: str, out: str, limit: int | None = None) -> int:
    from lean_first_diff import _quantity_call  # imports `ve` only when called: the PYTHONPATH checkout's
    corpus = json.loads(gzip.decompress(Path(corpus_path).read_bytes()))
    seen: dict[str, int] = {}
    walls: dict[str, list[float]] = {}
    cpu0 = time.process_time()
    start = time.perf_counter()
    for entry in corpus:
        op = entry["op"]
        if limit is not None and seen.get(op, 0) >= limit:
            continue
        seen[op] = seen.get(op, 0) + 1
        t0 = time.perf_counter()
        try:
            _quantity_call(entry)
        except Exception:  # noqa: BLE001  (a rejection is an answer; its time counts)
            pass
        walls.setdefault(op, []).append(time.perf_counter() - t0)
    wall = time.perf_counter() - start
    cpu = time.process_time() - cpu0
    try:
        from ve.backends import relay
        relay._close()
    except Exception:  # noqa: BLE001  (the base has no relay pool to close for these operations)
        pass
    children = resource.getrusage(resource.RUSAGE_CHILDREN)

    def pct(values, q):
        ordered = sorted(values)
        return ordered[min(len(ordered) - 1, int(q * len(ordered)))]
    report = {"wall_s": round(wall, 2), "python_cpu_s": round(cpu, 2),
              "children_cpu_s": round(children.ru_utime + children.ru_stime, 2),
              "ops": {op: {"calls": len(v), "p50_ms": round(1000 * pct(v, 0.5), 3),
                           "p95_ms": round(1000 * pct(v, 0.95), 3), "total_s": round(sum(v), 2)}
                      for op, v in sorted(walls.items())}}
    Path(out).write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    limit = None
    if "--limit" in args:
        index = args.index("--limit")
        limit = int(args[index + 1])
        del args[index:index + 2]
    raise SystemExit(main(*args, limit=limit))
