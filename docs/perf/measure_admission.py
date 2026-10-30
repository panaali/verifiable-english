"""Run fresh Lean service admissions three times each, saving whole-request process CPU evidence.

Usage: python3 docs/perf/measure_admission.py OUTPUT INPUT.jsonl [INPUT.jsonl ...]
The isolated scope is tried first. A VM without a user systemd bus falls back to
the same command under nice, recording the isolation failure for every run.
Stage times are not measured: the stage profiler was withdrawn
(reviews/dri-decisions-20261029-scale-admission-profile.md item 1).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
ISO = Path("/home/seyran/code/manage-agents/iso.sh")


def cpu_usage():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def one(path: Path) -> dict:
    source = path.read_text()
    before = cpu_usage()
    load_before = os.getloadavg()[0]
    command = ["zsh", str(ISO), "exp-scale-admission", "24G", "--", str(SERVICE)]
    proc = subprocess.run(command, input=source, text=True, capture_output=True)
    iso_error = None
    transport = "iso.sh"
    if proc.returncode and "Failed to connect to bus" in proc.stderr:
        iso_error = proc.stderr.strip()
        transport = "nice fallback"
        proc = subprocess.run(["nice", "-n", "15", str(SERVICE)], input=source,
                              text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError(f"{path.name}: service exit {proc.returncode}: {proc.stderr[:300]}")
    answer = json.loads(proc.stdout.splitlines()[-1])
    result = answer["results"][0]["result"]
    return {"cpu_seconds": round(cpu_usage() - before, 4), "load_1min_before": round(load_before, 2),
            "load_1min_after": round(os.getloadavg()[0], 2), "transport": transport,
            "iso_error": iso_error, "answer_status": result["status"],
            "answer_error": result.get("error")}


def main():
    output = Path(sys.argv[1])
    inputs = [Path(name) for name in sys.argv[2:]]
    data = {"service_sha256": hashlib.sha256(SERVICE.read_bytes()).hexdigest(), "cases": {}}
    for path in inputs:
        print(path.name, flush=True)
        data["cases"][path.stem] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                     "bytes": path.stat().st_size, "runs": []}
        for repeat in range(3):
            row = one(path)
            data["cases"][path.stem]["runs"].append(row)
            print(f"  {repeat + 1}: {row['cpu_seconds']} CPU s, {row['answer_status']}, "
                  f"load {row['load_1min_before']}", flush=True)
    output.write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
