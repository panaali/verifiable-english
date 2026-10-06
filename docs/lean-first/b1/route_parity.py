"""Gate-1 byte parity of lean-first batch 1: each route mode of the service against its one-shot executable.

    python docs/lean-first/b1/route_parity.py RECORDED BASE_BIN [--workers N] [--modes M,...] [--out FILE]

RECORDED is the directory `tests/route_case_recorder.py` wrote (every distinct case the suite sent to a
statement-layer route mode); BASE_BIN is the `lean/.lake/build/bin` of a build from before batch 1, which
still has the one-shot executables. Every case goes, in the same batches, through the base one-shot
executable and through this checkout's service mode, and the two rows are compared as JSON values (keys
sorted); a batch the one-shot refused (exit 2) must be refused by the service (a request error). The
output gives, per mode, the cases, the identical and differing rows (with examples) and the CPU seconds
each side spent: the one-shot processes' own CPU (`wait4`) and the service's CPU across its requests.

Exit 0 only for evidence of parity: every requested mode (default: all) has recorded cases, every case
sent is accounted for as identical or by design, and none differs. Exit 1 when a row differs or the
accounting fails (`problems` in the output); exit 2, before anything runs, when RECORDED is missing or
records nothing, a mode is unknown, a requested mode has no recorded case or BASE_BIN lacks its
one-shot executable.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import glob
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from ve.backends.lean_service import LeanService, _decode_json  # noqa: E402

EXECUTABLES = {
    "norms": "ve_norms_route", "soft-norms": "ve_soft_norms_route", "rights": "ve_rights_route",
    "speech-acts": "ve_speech_acts_route", "reports": "ve_reports_route", "alternatives": "ve_alternatives_route",
    "risk": "ve_risk_route", "risk-eval": "ve_risk_eval", "quantity": "ve_quantity",
    "norm-defaults": "ve_norm_defaults_route", "discourse": "ve_discourse_route",
    "readings-route": "ve_readings_route", "diagnose": "ve_diagnose",
}
BATCH_CASES, BATCH_BYTES = 64, 2 << 20
# The contracts `ve_diagnose` registered (lean/VE/WireContract/Diagnose.lean `units`).
DIAGNOSE_UNITS = ("inner@0", "demo@0", "defer@0", "mid@0", "forms@0", "soft-norms@0")


class NoEvidence(Exception):
    """The inputs cannot show parity: a missing or empty recording, a missing one-shot
    executable, an unknown mode or a requested mode without a recorded case."""


def load(directory):
    """Distinct (mode, case text) pairs, in first-seen order. A directory that does not exist,
    holds no `*.jsonl` recording or records no case is `NoEvidence`."""
    if not os.path.isdir(directory):
        raise NoEvidence(f"no recording directory {directory}")
    paths = sorted(glob.glob(os.path.join(glob.escape(directory), "*.jsonl")))
    if not paths:
        raise NoEvidence(f"no *.jsonl recording in {directory}")
    seen = {}
    for path in paths:
        with open(path) as f:
            for line in f:
                mode, text = json.loads(line)
                seen.setdefault((mode, text), None)
    if not seen:
        raise NoEvidence(f"the recordings in {directory} hold no case")
    return list(seen)


def batches(pairs):
    """(mode, unit, texts) batches: per mode (and per diagnose unit), at most BATCH_CASES and BATCH_BYTES."""
    groups = defaultdict(list)
    for mode, text in pairs:
        unit = json.loads(text).get("unit") if mode == "diagnose" else None
        unit = unit if type(unit) is str else repr(unit)
        groups[(mode, unit)].append(text)
    for (mode, unit), texts in groups.items():
        batch, size = [], 0
        for text in texts:
            if batch and (len(batch) == BATCH_CASES or size + len(text) > BATCH_BYTES):
                yield mode, unit, batch
                batch, size = [], 0
            batch.append(text)
            size += len(text)
        if batch:
            yield mode, unit, batch


def one_shot(base_bin, mode, unit, texts):
    """(rows or None when refused, CPU seconds, wall seconds) of the base one-shot executable."""
    if mode == "diagnose":
        # The one-shot runner takes the unit as an argument and reads the case without it.
        stripped = []
        for text in texts:
            case = json.loads(text)
            case.pop("unit", None)
            stripped.append(json.dumps(case, ensure_ascii=False, separators=(",", ":")))
        texts = stripped
    command = [str(base_bin / EXECUTABLES[mode]), *([unit] if mode == "diagnose" else []), "-"]
    if mode == "risk-eval":
        command = command[:-1]
    data = ("[" + ",".join(texts) + "]").encode()
    started = time.perf_counter()
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def feed():
        proc.stdin.write(data)
        proc.stdin.close()
    feeder = threading.Thread(target=feed)
    feeder.start()
    out = proc.stdout.read()
    feeder.join()
    # The child's own CPU time, reaped here rather than by Popen.
    _, status, usage = os.wait4(proc.pid, 0)
    proc.returncode = os.waitstatus_to_exitcode(status)
    wall = time.perf_counter() - started
    cpu = usage.ru_utime + usage.ru_stime
    if proc.returncode == 2:
        return None, cpu, wall
    return _decode_json(out), cpu, wall


class Worker(threading.local):
    service: LeanService | None = None


_local = Worker()


def service_rows(mode, texts):
    if _local.service is None:
        _local.service = LeanService()
    service = _local.service
    service.start()
    before = service.cpu_seconds() or 0.0
    started = time.perf_counter()
    _, response = service.exchange(mode, "[" + ",".join(texts) + "]", len(texts), timeout=3600, texts=texts)
    wall = time.perf_counter() - started
    cpu = (service.cpu_seconds() or 0.0) - before
    if response.get("status") == "error":
        return None, cpu, wall
    return [entry["result"] for entry in response["results"]], cpu, wall


def canonical(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)


# The one difference by design: `ve_diagnose <unit>` exited 2 for a unit with no contract (and could not
# be asked without one); the `diagnose` mode answers each such case with an error row of that text.
UNIT_ROWS = {"InvalidInput: a diagnose case names its unit"}


def unit_row(unit, row):
    return row.get("status") == "error" and (
        row.get("error") in UNIT_ROWS or row.get("error") == f"UnsupportedProfile: no wire contract {unit}")


def compare(base_bin, batch):
    mode, unit, texts = batch
    registered = mode != "diagnose" or unit in DIAGNOSE_UNITS
    old, old_cpu, old_wall = one_shot(base_bin, mode, unit, texts) if registered else (None, 0.0, 0.0)
    new, new_cpu, new_wall = service_rows(mode, texts)
    result = {"mode": mode, "cases": len(texts), "one_shot_cpu": old_cpu, "service_cpu": new_cpu,
              "one_shot_wall": old_wall, "service_wall": new_wall, "same": 0, "different": [], "by_design": 0,
              "different_cases": 0}

    def batch_differs(reason):
        # Every case of the batch counts as different: none of its rows was compared.
        result["different"].append({"batch": reason})
        result["different_cases"] = len(texts)
        return result
    if not registered:
        if new is not None and len(new) == len(texts) and all(unit_row(unit, row) for row in new):
            result["by_design"] = len(texts)
            return result
        return batch_differs(f"diagnose unit {unit!r} not answered by error rows")
    if old is None or new is None:
        if old is None and new is None:
            result["same"] = len(texts)
            return result
        return batch_differs("refused by " + ("one-shot" if old is None else "service"))
    if len(old) != len(texts) or len(new) != len(texts):
        return batch_differs(f"row counts {len(old)} and {len(new)} for {len(texts)} cases")
    for text, a, b in zip(texts, old, new):
        if canonical(a) == canonical(b):
            result["same"] += 1
        else:
            result["different_cases"] += 1
            result["different"].append({"case": text[:300], "one_shot": canonical(a)[:500],
                                        "service": canonical(b)[:500]})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("recorded")
    parser.add_argument("base_bin", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--modes", help="comma-separated modes to compare (default: all)")
    args = parser.parse_args(argv)
    try:
        work, modes = plan(args.recorded, args.base_bin, args.modes)
    except NoEvidence as exc:
        print(f"route_parity: {exc}", file=sys.stderr)
        return 2
    summary = defaultdict(lambda: {"cases": 0, "same": 0, "different": 0, "by_design": 0, "examples": [],
                                   "one_shot_cpu": 0.0, "service_cpu": 0.0, "one_shot_wall": 0.0,
                                   "service_wall": 0.0, "batches": 0})
    with ThreadPoolExecutor(args.workers) as pool:
        for result in pool.map(lambda b: compare(args.base_bin, b), work):
            entry = summary[result["mode"]]
            entry["batches"] += 1
            for key in ("cases", "same", "by_design", "one_shot_cpu", "service_cpu", "one_shot_wall",
                        "service_wall"):
                entry[key] += result[key]
            entry["different"] += result["different_cases"]
            entry["examples"].extend(result["different"][:3 - len(entry["examples"])])
    report = {mode: {**entry, **{k: round(entry[k], 2) for k in
                                ("one_shot_cpu", "service_cpu", "one_shot_wall", "service_wall")}}
              for mode, entry in sorted(summary.items())}
    total = {key: sum(entry[key] for entry in report.values())
             for key in ("cases", "same", "different", "by_design", "batches")}
    problems = verdict_problems(modes, sum(len(texts) for _, _, texts in work), report, total)
    text = json.dumps({"total": total, "modes": report, "requested_modes": sorted(modes),
                       "problems": problems}, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(text + "\n")
    print(text)
    return 0 if not problems else 1


def plan(recorded, base_bin, mode_list):
    """(batches, requested modes), or `NoEvidence`: every requested mode is known, has its one-shot
    executable under `base_bin` and at least one recorded case."""
    modes = set(mode_list.split(",")) if mode_list else set(EXECUTABLES)
    unknown = sorted(modes - set(EXECUTABLES))
    if unknown or not modes:
        raise NoEvidence(f"unknown modes {unknown}" if unknown else "no mode requested")
    missing = sorted(EXECUTABLES[m] for m in modes if not (Path(base_bin) / EXECUTABLES[m]).is_file())
    if missing:
        raise NoEvidence(f"{base_bin} has no one-shot executable {', '.join(missing)}")
    work = list(batches(pair for pair in load(recorded) if pair[0] in modes))
    uncovered = sorted(modes - {mode for mode, _, _ in work})
    if uncovered:
        raise NoEvidence(f"no recorded case for modes {', '.join(uncovered)}")
    return work, modes


def verdict_problems(modes, sent, report, total):
    """Why the run is no parity evidence (empty when it is): every requested mode answered, every
    case sent accounted for as identical, by design or different, and nothing different."""
    problems = []
    if set(report) != modes:
        problems.append(f"modes without results: {sorted(modes - set(report))}")
    if total["cases"] == 0 or total["cases"] != sent:
        problems.append(f"{total['cases']} cases compared of {sent} sent")
    for mode, entry in report.items():
        if entry["cases"] == 0 or entry["same"] + entry["by_design"] + entry["different"] != entry["cases"]:
            problems.append(f"{mode}: {entry['cases']} cases, {entry['same']} identical, "
                            f"{entry['by_design']} by design, {entry['different']} different")
    if total["different"]:
        problems.append(f"{total['different']} cases differ")
    return problems


if __name__ == "__main__":
    sys.exit(main())
