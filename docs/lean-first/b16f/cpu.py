"""CPU of `ve document check` and `ve document render` on batch 16f's pilots, the base checkout against the head.

    python docs/lean-first/b16f/cpu.py BASE_ROOT HEAD_ROOT [--repeat N]

Each document is checked and rendered in a fresh process of each checkout (the Lean service started by that
process included), `--repeat` times, and the median user+system CPU of the process tree is saved with the machine's
load average, in `evidence/cpu.json`. The time of the head's Lean `document` request alone (warm service, wall clock,
the service is single-threaded) is saved beside it: R4's absolute budget is at most 1 s Lean CPU and 2 s wall per
document check.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from tools.lean_first_diff import pilot_documents  # noqa: E402

PILOTS = (  # a soft-norms document with 15 norms, one with one; a norms@0 one with a fence; a small norms@0 one
    "pilot/cc-20260929T1800Z:usecases/claude-constitution-pilot/run-20260929T1800Z/readings/all-default.ve.md",
    "pilot/udhr-20261003T0600Z:usecases/udhr-pilot/run-20261003T0600Z/readings/u111.default_both_aims_state.ve.md",
    "pilot/cc-20260928T0600Z:usecases/claude-constitution-pilot/run-20260928T0600Z/translation.ve.md",
    "pilot/udhr-20261008T1800Z:usecases/udhr-pilot/run-20261008T1800Z/translation.ve.md",
)

LEAN_REQUEST = """
import json, sys, time
from pathlib import Path
from ve import document as D
from ve.backends.relay import answer
raw = Path(sys.argv[1]).read_bytes()
D._lean_answer(raw, True)  # starts the service and builds the lexicon proposal
captured = {}
real = answer
def timed(mode, case):
    start = time.perf_counter()
    out = real(mode, case)
    captured["seconds"] = time.perf_counter() - start
    return out
import ve.backends.relay as relay
relay.answer = timed
D._lean_answer(raw, True)
print(json.dumps(captured))
"""


def cpu(root: Path, args: list[str]) -> float:
    env = {**os.environ, "PYTHONPATH": str(root), "VE_NATIVE_PREBUILT": "1"}
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    subprocess.run([sys.executable, *args], cwd=root, env=env, capture_output=True, check=False)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("head", type=Path)
    parser.add_argument("--repeat", type=int, default=3)
    args = parser.parse_args()
    documents = {name: raw for name, _, raw in pilot_documents(ROOT)}
    rows = []
    with tempfile.TemporaryDirectory(prefix="b16f-cpu-") as directory:
        for name in PILOTS:
            path = Path(directory) / "document.ve.md"
            path.write_bytes(documents[name])
            row = {"pilot": name}
            for op in ("check", "render"):
                for side, root in (("base", args.base), ("head", args.head)):
                    row[f"{op}_{side}_cpu_s"] = round(statistics.median(
                        cpu(root, ["-m", "ve", "document", op, str(path)]) for _ in range(args.repeat)), 2)
                row[f"{op}_ratio"] = round(row[f"{op}_head_cpu_s"] / row[f"{op}_base_cpu_s"], 2)
            env = {**os.environ, "PYTHONPATH": str(args.head), "VE_NATIVE_PREBUILT": "1"}
            done = subprocess.run([sys.executable, "-c", LEAN_REQUEST, str(path)], cwd=args.head, env=env,
                                  capture_output=True, text=True, check=True)
            row["head_lean_document_request_s"] = round(json.loads(done.stdout.splitlines()[-1])["seconds"], 3)
            rows.append(row)
            print(json.dumps(row), flush=True)
    out = {"load_average": os.getloadavg(), "repeat": args.repeat, "rows": rows}
    (HERE / "evidence").mkdir(exist_ok=True)
    (HERE / "evidence/cpu.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
