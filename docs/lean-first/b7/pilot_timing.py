"""Lean-first batch 7 review B1: `ve document check` of one pilot document on the base and the head, side by side.

    uv run --frozen python docs/lean-first/b7/pilot_timing.py DOCUMENT --base ROOT --head ROOT [--rounds N] [--out F]

Each round starts both checkouts' `python -m ve document check DOCUMENT` at the same moment, so both see the same
host load, and records per side the wall time, the CPU (user + system) of the process and every descendant it
waited for (the Lean service included: `os.wait4`), the exit and the stdout's SHA-256, with the one-minute load
average before and after. The answers must be byte-identical. Nothing is written inside either checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def round_once(document: Path, roots: dict[str, Path]) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        procs, sinks = {}, {}
        load = os.getloadavg()[0]
        for side, root in roots.items():
            sinks[side] = open(Path(tmp) / side, "wb")
            env = {**os.environ, "PYTHONPATH": str(root)}
            env.pop("VE_LEAN_SERVICE", None)
            procs[side] = (subprocess.Popen([sys.executable, "-m", "ve", "document", "check", str(document)],
                                            cwd=root, env=env, stdout=sinks[side], stderr=subprocess.DEVNULL),
                           time.perf_counter())
        pending = {p.pid: side for side, (p, _) in procs.items()}
        result = {}
        while pending:
            pid, status, usage = os.wait4(-1, 0)
            side = pending.pop(pid, None)
            if side is None:
                continue
            result[side] = {"wall": round(time.perf_counter() - procs[side][1], 1),
                            "cpu": round(usage.ru_utime + usage.ru_stime, 1),
                            "exit": os.waitstatus_to_exitcode(status)}
        for side, sink in sinks.items():
            sink.close()
            result[side]["stdout_sha256"] = hashlib.sha256((Path(tmp) / side).read_bytes()).hexdigest()
    result["identical"] = len({result[side]["stdout_sha256"] for side in roots}) == 1
    result["load_before"], result["load_after"] = round(load, 1), round(os.getloadavg()[0], 1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--head", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    roots = {"base": args.base.resolve(), "head": args.head.resolve()}
    rounds = [round_once(args.document.resolve(), roots) for _ in range(args.rounds)]
    report = {"document_sha256": hashlib.sha256(args.document.read_bytes()).hexdigest(), "rounds": rounds}
    text = json.dumps(report, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0 if all(r["identical"] for r in rounds) else 1


if __name__ == "__main__":
    raise SystemExit(main())
