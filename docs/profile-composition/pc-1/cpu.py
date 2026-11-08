"""R4's saved evidence for row 16 (pc-1 review F2 and F6): the Lean CPU and wall time of the document mode on PROBE F2
(256 readings, 1.46 MB, plain) and on the 64-reading fixture (63 distinct dangling references per reading, plain and
with `judgments@0`), answered by the merge base's service and by PC-1's, run by run in turn. Each figure is the least
of `RUNS` runs on one warm service; the load average is recorded with them. Writes cpu.json beside this file.

    uv run python docs/profile-composition/pc-1/cpu.py BASE_SERVICE HEAD_SERVICE
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

from test_judgments_chain import DATA, LAYER, PLAIN, front, reading, reading_set, text  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402

RUNS = 7


def case(n, profiles, models):
    ids = [f"r{i}" for i in range(n)]
    fm = front("u0052.s01", profiles, sets=reading_set([reading(r, {o: f"m-{r}-{o}" for o in ids if o != r})
                                                        for r in ids], models))
    return {"id": "c", "document": text("u0052.s01", fm)}


CASES = {"probe-f2-256-plain": case(256, PLAIN, {}), "f6-64-plain": case(64, PLAIN, {"d": DATA["model"]}),
         "f6-64-layer": case(64, LAYER, {"d": DATA["model"]})}


def measure(base, head):
    """Each case on both services, base and head alternating run by run, so both see the same machine load."""
    out = {"base": {}, "head": {}}
    with LeanService(base, allow_unlisted_build=True) as b, LeanService(head, allow_unlisted_build=True) as h:
        for name, c in CASES.items():
            best = {}
            for _ in range(RUNS):
                for side, service in (("base", b), ("head", h)):
                    before, start = service.cpu_seconds(), time.perf_counter()
                    row = service.run("document", [c])[0]
                    used, spent = service.cpu_seconds() - before, time.perf_counter() - start
                    cpu, wall, _ = best.get(side, (used, spent, None))
                    best[side] = (min(cpu, used), min(wall, spent), row.get("error") or row["status"])
            for side, (cpu, wall, answer) in best.items():
                out[side][name] = {"bytes": len(c["document"]), "cpu_seconds": round(cpu, 3),
                                   "wall_seconds": round(wall, 3), "answer": answer}
    return out


def main(base, head):
    figures = measure(base, head)
    out = {"runs": RUNS, "load_average": [round(x, 1) for x in os.getloadavg()],
           "budget": {"cpu_seconds": 1.0, "wall_seconds": 2.0}, **figures,
           "within_budget": all(f["cpu_seconds"] <= 1.0 and f["wall_seconds"] <= 2.0
                                for f in figures["head"].values()),
           "services": {k: hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in (("base", base), ("head", head))}}
    (Path(__file__).parent / "cpu.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0 if out["within_budget"] else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
