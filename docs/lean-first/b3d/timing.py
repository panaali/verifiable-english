"""Lean-first batch 3d timing: the readings corpus and a pilot document, base and head side by side.

    uv run --frozen python docs/lean-first/b3d/timing.py corpus CASES.json --base ROOT --head ROOT [--repeat N]
    uv run --frozen python docs/lean-first/b3d/timing.py pilot DOCUMENT --base ROOT --head ROOT [--repeat N]
    uv run --frozen python docs/lean-first/b3d/timing.py cases CASES.json OUT.json

`corpus` runs `ve.readings_route.validate` over every case of CASES.json (the readings corpus that
`tools/lean_first_diff.py record --corpus readings` writes next to its output), in one Python process per side,
each importing the `ve` package of its checkout, both started at the same moment so that both see the same host
load. Per run and side it prints the wall time, the Python process's own CPU, its children's CPU (the one-shot
`ve_readings_route` processes) and the outcomes (ok, rejected, unavailable). `pilot` runs `ve document check
DOCUMENT` from each checkout at the same moment and prints per side the wall time, the CPU of the process and its
children (`os.wait4`), the exit status, the report's `status` (or the error code) and whether the two reports are
byte-identical. The one-minute load average is printed before and after each run. `cases` writes the
`ve_readings_route` case each document of CASES.json sends, captured before Lean is called, so that the corpus can
be run in one route process (`docs/lean-first/b3b/udhr_timing.py time OUT.json`) without start-up costs. Nothing
is written inside either checkout.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time


def side(cases: Path) -> dict:
    """In the child: every case through `validate`, timed (the `ve` imported is the checkout's)."""
    from ve.readings_route import validate
    counts = {"ok": 0, "rejected": 0, "unavailable": 0}
    rows = json.loads(cases.read_text())
    start = time.perf_counter()
    for case in rows:
        document = case["document"]
        units = [{"id": u["id"], "kind": u.get("kind"), **({"content": u["content"]} if "content" in u else {})}
                 for u in document["units"]]
        try:
            validate(case["environment"], units, document["reading_sets"])
            counts["ok"] += 1
        except Exception as exc:  # noqa: BLE001  (each outcome is counted)
            code = getattr(exc, "code", None) or type(exc).__name__
            counts["unavailable" if code == "CheckerUnavailable" else "rejected"] += 1
    wall = time.perf_counter() - start
    me, kids = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"wall": round(wall, 2), "python_cpu": round(me.ru_utime + me.ru_stime, 2),
            "children_cpu": round(kids.ru_utime + kids.ru_stime, 2), **counts}


class _Captured(Exception):
    pass


def capture(cases: Path, out: Path) -> dict:
    """The route case of each corpus document, in order (this checkout's `ve`)."""
    import ve.readings_route as route

    def run_lean(sent, **_):
        raise _Captured(sent)

    route.run_lean = run_lean
    captured = []
    for case in json.loads(cases.read_text()):
        document = case["document"]
        units = [{"id": u["id"], "kind": u.get("kind"), **({"content": u["content"]} if "content" in u else {})}
                 for u in document["units"]]
        try:
            route.validate(case["environment"], units, document["reading_sets"])
        except _Captured as sent:
            captured += sent.args[0]
        except Exception:  # noqa: BLE001  (refused before Lean: no route case)
            pass
    out.write_text(json.dumps(captured, ensure_ascii=False))
    return {"documents": len(json.loads(cases.read_text())), "route_cases": len(captured)}


def _env(root: Path) -> dict:
    env = {**os.environ, "PYTHONPATH": str(root)}
    env.pop("VE_AUTHORITY", None)
    return env


def corpus_run(cases: Path, base: Path, head: Path) -> dict:
    load = os.getloadavg()[0]
    procs = {name: subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_side", str(cases)],
                                    cwd=root, env=_env(root), stdout=subprocess.PIPE)
             for name, root in (("base", base), ("head", head))}
    result = {name: json.loads(p.communicate()[0]) for name, p in procs.items()}
    return {**result, "load_before": round(load, 1), "load_after": round(os.getloadavg()[0], 1)}


def pilot_run(document: Path, base: Path, head: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        outputs = {name: open(Path(tmp) / name, "wb") for name in ("base", "head")}
        load = os.getloadavg()[0]
        procs = {}
        for name, root in (("base", base), ("head", head)):
            p = subprocess.Popen([sys.executable, "-m", "ve", "document", "check", str(document)], cwd=root,
                                 env=_env(root), stdout=outputs[name], stderr=subprocess.DEVNULL)
            procs[p.pid] = (name, time.perf_counter())
        result = {}
        while procs:
            pid, status, usage = os.wait4(-1, 0)
            if pid not in procs:
                continue
            name, started = procs.pop(pid)
            result[name] = {"wall": round(time.perf_counter() - started, 2),
                            "cpu": round(usage.ru_utime + usage.ru_stime, 2),
                            "exit": os.waitstatus_to_exitcode(status)}
        for f in outputs.values():
            f.close()
        texts = {name: (Path(tmp) / name).read_bytes() for name in ("base", "head")}
    for name, text in texts.items():
        try:
            report = json.loads(text)
            result[name]["status"] = report.get("status") or (report.get("error") or {}).get("code") or "answered"
        except ValueError:
            result[name]["status"] = "unreadable"
        result[name]["report_bytes"] = len(text)
    return {**result, "identical": texts["base"] == texts["head"], "load_before": round(load, 1),
            "load_after": round(os.getloadavg()[0], 1)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("corpus", "pilot"):
        p = sub.add_parser(name)
        p.add_argument("input", type=Path)
        p.add_argument("--base", type=Path, required=True)
        p.add_argument("--head", type=Path, required=True)
        p.add_argument("--repeat", type=int, default=1)
    p = sub.add_parser("cases")
    p.add_argument("input", type=Path)
    p.add_argument("out", type=Path)
    p = sub.add_parser("_side")
    p.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    if args.command == "cases":
        print(json.dumps(capture(args.input, args.out)))
        return 0
    if args.command == "_side":
        print(json.dumps(side(args.input)))
        return 0
    run = corpus_run if args.command == "corpus" else pilot_run
    runs = [run(args.input.resolve(), args.base.resolve(), args.head.resolve()) for _ in range(args.repeat)]
    print(json.dumps({"input": args.input.name, "runs": runs}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
