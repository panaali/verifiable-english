"""Measure the readings report of one already loaded document, without model calls.

Usage: uv run python docs/scale-choice-batch/measure.py DOC OUTPUT
"""
import json
import os
import resource
import sys
import time
from pathlib import Path

from ve.backends.lean_service import LeanService, _cpu_seconds
from ve.document import load_document
from ve.readings_components import report


requests = []
original = LeanService._roundtrip


def timed(self, mode, cases_text, count, timeout, nonce, line, texts, expanded=None, stored=None):
    before = _cpu_seconds(self.pid) if self.pid else None
    started = time.monotonic()
    try:
        return original(self, mode, cases_text, count, timeout, nonce, line, texts, expanded, stored)
    finally:
        after = _cpu_seconds(self.pid) if self.pid else None
        requests.append({"mode": mode, "cases": count,
                         "wall": round(time.monotonic() - started, 3),
                         "cpu": round(after - before, 3) if before is not None and after is not None else None})


LeanService._roundtrip = timed
doc = load_document(Path(sys.argv[1]))
requests.clear()
load_start = os.getloadavg()[0]
cpu_start = resource.getrusage(resource.RUSAGE_SELF)
wall_start = time.monotonic()
result = report(doc)
wall = time.monotonic() - wall_start
cpu_end = resource.getrusage(resource.RUSAGE_SELF)
data = {"document": str(Path(sys.argv[1]).resolve()), "wall_seconds": round(wall, 3),
        "python_cpu_seconds": round(cpu_end.ru_utime + cpu_end.ru_stime - cpu_start.ru_utime - cpu_start.ru_stime, 3),
        "lean_cpu_seconds": round(sum(r["cpu"] or 0 for r in requests), 3),
        "load_1min_start": round(load_start, 2), "load_1min_end": round(os.getloadavg()[0], 2),
        "readings_status": result["status"], "request_count": len(requests),
        "readings_choice_requests": sum(r["mode"] == "readings-route" and r["cases"] == 1 for r in requests),
        "requests": requests}
Path(sys.argv[2]).write_text(json.dumps(data, indent=2) + "\n")
print(json.dumps({key: value for key, value in data.items() if key != "requests"}))
