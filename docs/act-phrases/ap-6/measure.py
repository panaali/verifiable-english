"""AP-6 bar row 2: check the three fixtures on the binary route and on route (a), and compare their cost.

Each fixture (docs/act-phrases/ap-6/fixtures/) has two documents: `<f>.binary.ve.md`, the binary route as today's
language states it (the act's last bound slot dropped), and `<f>.reified.ve.md`, route (a) (the act reified as an event
sort with one role predicate per bound non-subject slot). Both are checked with today's `ve document check`, the
product's own path: Lean admission, the norm layers regenerated and validated, and the premise set's model. Neither
route's Lean is needed: route (a)'s reified document is an ordinary binary norms document.

The cost is CPU seconds (user + system) of the check and its children, as tools/bench measures (`ChildCPU` of
tests/subprocesses.py; machine load stretches CPU time far less than elapsed time), with the elapsed time beside it.
The runs alternate binary and reified so that drift in the machine's load falls on both. Speed is measured here, never
in the suite (CLAUDE.md). Run from the repository root, after `python3 tools/rust_build.py` and the Lean build:

    uv run python docs/act-phrases/ap-6/measure.py --runs 9 --out docs/act-phrases/ap-6/timing.json

`--verify <timing.json>` reruns nothing: it recomputes the verdict from the saved raw rows and fails unless it equals
the saved one (REPORT.md cites the saved file, not a live run).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
from subprocesses import HANG_TIMEOUT, ChildCPU  # noqa: E402

FIXTURES = ("u019", "u057", "mu")
VARIANTS = ("binary", "reified")
BAR = 1.25  # the plan's pre-registered ratio (act-phrases-PLAN.md, AP-6)
FLOOR = ROOT / "tests/data/rd9-docroute.ve.md"  # a one-rule document: the CLI's fixed cost


def check_once(path: Path) -> dict:
    """One `ve document check`; the check must succeed with an admitted graph and a model of the premises."""
    start = time.monotonic()
    with ChildCPU() as cpu:
        done = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(path)], cwd=ROOT,
                              capture_output=True, text=True, timeout=HANG_TIMEOUT)
    wall = time.monotonic() - start
    if done.returncode != 0:
        raise RuntimeError(f"{path.name}: exit {done.returncode}\n{done.stderr[-2000:]}")
    answer = json.loads(done.stdout)
    if answer["admission"]["admitted"] is not True or answer["premises"]["status"] != "model":
        raise RuntimeError(f"{path.name}: not admitted with a model: {answer['admission']} {answer['premises']}")
    return {"cpu_s": round(cpu.seconds, 4), "wall_s": round(wall, 4)}


def verdict(rows: dict) -> dict:
    """Per fixture, the ratio of the medians (reified over binary, CPU) and whether it is within the bar."""
    out = {}
    for name in FIXTURES:
        binary = statistics.median(r["cpu_s"] for r in rows[name]["binary"])
        reified = statistics.median(r["cpu_s"] for r in rows[name]["reified"])
        ratio = reified / binary
        out[name] = {"binary_cpu_median_s": round(binary, 4), "reified_cpu_median_s": round(reified, 4),
                     "ratio": round(ratio, 4), "within_bar": ratio <= BAR}
    out["all_within_bar"] = all(out[name]["within_bar"] for name in FIXTURES)
    return out


def machine() -> dict:
    model = next((line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                  if line.startswith("model name")), platform.processor()) if Path("/proc/cpuinfo").exists() else \
        platform.processor()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"node": platform.node(), "system": platform.platform(), "cpu": model, "cpus": os.cpu_count(),
            "python": platform.python_version(), "commit": commit}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--runs", type=int, default=9)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        saved = json.loads(args.verify.read_text())
        again = verdict(saved["rows"])
        if again != saved["verdict"] or saved["bar"] != BAR:
            print(f"verdict differs from the saved one:\n{json.dumps(again, indent=1)}", file=sys.stderr)
            return 1
        print("saved verdict reproduced:", json.dumps(again))
        return 0
    paths = {(f, v): HERE / "fixtures" / f"{f}.{v}.ve.md" for f in FIXTURES for v in VARIANTS}
    load_before = os.getloadavg()
    for path in [FLOOR, *paths.values()]:  # warm the files and the checker binaries once
        check_once(path)
    rows = {f: {v: [] for v in VARIANTS} for f in FIXTURES}
    floor = []
    for _ in range(args.runs):
        floor.append(check_once(FLOOR))
        for f in FIXTURES:
            for v in VARIANTS:
                rows[f][v].append(check_once(paths[(f, v)]))
    result = {"machine": machine(), "load_before": [round(x, 2) for x in load_before],
              "load_after": [round(x, 2) for x in os.getloadavg()], "runs": args.runs, "bar": BAR,
              "floor": {"document": str(FLOOR.relative_to(ROOT)), "runs": floor,
                        "cpu_median_s": round(statistics.median(r["cpu_s"] for r in floor), 4)},
              "rows": rows, "verdict": verdict(rows)}
    text = json.dumps(result, indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    print(json.dumps(result["verdict"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
