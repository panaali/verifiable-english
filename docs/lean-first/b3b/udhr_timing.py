"""Lean-first batch 3b timing: the UDHR pilot's readings call, base and head side by side.

    uv run --frozen python docs/lean-first/b3b/udhr_timing.py dump DOCUMENT OUT.json [--sets N]
    uv run --frozen python docs/lean-first/b3b/udhr_timing.py time CASE.json --base BIN --head BIN [--repeat N]
    uv run --frozen python docs/lean-first/b3b/udhr_timing.py alternate CASE.json --bin NAME=BIN ... [--rounds N]

`dump` writes the one `ve_readings_route` case that `document load` of DOCUMENT sends, and stops before Lean is
called (plan section 3.5's `dump_readings_case.py`); `--sets N` keeps the first N reading sets. `time` runs the
two route executables on the case at the same moment, so both see the same host load, `--repeat` times, and
prints one JSON object: per run and side the wall time and the child's user and system CPU (`os.wait4`), the
one-minute load average before and after, and whether the two answers are byte-identical. `alternate` runs the
named executables one after another, each once per round, `--rounds` times, and prints each run's CPU (user +
system) and exit and whether every executable's answer is byte-identical to the first's in every round: on a
shared host the minimum over rounds is the comparison least disturbed by other work, and running one executable
at a time keeps the two from competing with each other. Nothing is written inside the checkout.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]


class _Captured(Exception):
    pass


def dump(document: Path, out: Path, sets: int | None) -> dict:
    sys.path.insert(0, str(ROOT))
    import ve.readings_route as route
    from ve.document import load_document

    def capture(cases, **_):
        raise _Captured(cases)

    route.run_lean = capture
    try:
        load_document(document)
    except _Captured as captured:
        cases = captured.args[0]
    else:
        raise SystemExit("the document made no readings-validate call")
    if sets is not None:
        for case in cases:
            case["document"]["reading_sets"] = case["document"].get("reading_sets", [])[:sets]
    out.write_text(json.dumps(cases, ensure_ascii=False))
    return {"bytes": out.stat().st_size, "reading_sets": len(cases[0]["document"].get("reading_sets", []))}


def _start(binary: Path, case: Path, sink):
    return subprocess.Popen([str(binary), str(case)], stdout=sink, stderr=subprocess.DEVNULL), time.perf_counter()


def run_pair(case: Path, base: Path, head: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        outputs = {side: open(Path(tmp) / side, "wb") for side in ("base", "head")}
        load = os.getloadavg()[0]
        procs = {side: _start(binary, case, outputs[side]) for side, binary in (("base", base), ("head", head))}
        result = {}
        pending = {p.pid: side for side, (p, _) in procs.items()}
        while pending:
            pid, status, usage = os.wait4(-1, 0)
            side = pending.pop(pid, None)
            if side is None:
                continue
            result[side] = {"wall": round(time.perf_counter() - procs[side][1], 2), "user": round(usage.ru_utime, 2),
                            "sys": round(usage.ru_stime, 2), "exit": os.waitstatus_to_exitcode(status)}
        for f in outputs.values():
            f.close()
        same = (Path(tmp) / "base").read_bytes() == (Path(tmp) / "head").read_bytes()
        size = (Path(tmp) / "head").stat().st_size
    return {**result, "identical": same, "answer_bytes": size, "load_before": round(load, 1),
            "load_after": round(os.getloadavg()[0], 1)}


def alternate(case: Path, bins: list[tuple[str, Path]], rounds: int) -> dict:
    runs = {name: [] for name, _ in bins}
    identical = True
    load = os.getloadavg()[0]
    with tempfile.TemporaryDirectory() as tmp:
        for _ in range(rounds):
            answers = []
            for name, binary in bins:
                out = Path(tmp) / name
                with open(out, "wb") as sink:
                    process, _ = _start(binary, case, sink)
                    _, status, usage = os.wait4(process.pid, 0)
                runs[name].append({"cpu": round(usage.ru_utime + usage.ru_stime, 2),
                                   "exit": os.waitstatus_to_exitcode(status)})
                answers.append(out.read_bytes())
            identical = identical and all(a == answers[0] for a in answers)
    return {"case": case.name, "rounds": rounds, "runs": runs, "identical": identical,
            "load_before": round(load, 1), "load_after": round(os.getloadavg()[0], 1)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("dump")
    p.add_argument("document", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--sets", type=int)
    p = sub.add_parser("time")
    p.add_argument("case", type=Path)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--head", type=Path, required=True)
    p.add_argument("--repeat", type=int, default=1)
    p = sub.add_parser("alternate")
    p.add_argument("case", type=Path)
    p.add_argument("--bin", action="append", required=True, help="NAME=PATH, in run order")
    p.add_argument("--rounds", type=int, default=5)
    args = parser.parse_args(argv)
    if args.command == "dump":
        print(json.dumps(dump(args.document, args.out, args.sets)))
        return 0
    if args.command == "alternate":
        bins = [(spec.split("=", 1)[0], Path(spec.split("=", 1)[1])) for spec in args.bin]
        result = alternate(args.case, bins, args.rounds)
        print(json.dumps(result, indent=1))
        return 0 if result["identical"] else 1
    runs = [run_pair(args.case, args.base, args.head) for _ in range(args.repeat)]
    print(json.dumps({"case": args.case.name, "runs": runs}, indent=1))
    return 0 if all(r["identical"] and r["base"]["exit"] == r["head"]["exit"] for r in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
