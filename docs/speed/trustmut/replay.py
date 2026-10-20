#!/usr/bin/env python3
"""speed-trustmut step 1: replay tools/trust_mutants.py on the HEADs where the six B findings were raised.

    uv run python docs/speed/trustmut/replay.py [--run] [--jobs 8]

With --run, each HEAD is checked out in a detached worktree under /tmp, its lean/.lake is linked from this
checkout's build (only read: nothing builds there; the tool builds in its own scratch copies), and the tool runs on
every mutant (no --max-mutants cut), writing docs/speed/trustmut/evidence/<head>.json with a profile (`profiled`:
the 5-minute load, the time in the probe and in builds, the tool's commit). Without --run, the table
is read from that saved evidence (D4). A finding counts as flagged when the tool lists a survivor on one of the
lines the review names; the default --max-mutants 60 column says whether one of them is among the first 60.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent / "evidence"
# (finding, the HEAD its review checked, the base, {file under lean/: the lines the review names})
FINDINGS = [
    ("pk-1 F1", "6b58a0ff7911008227fe14f9ea4bfd7b8d80ea37", "93131f967bb3ad87674c214b19347986f33c79b2",
     {"VE/NormDefaults/Packs.lean": [75, 421, 422, 423]}),
    ("qt-a1 F1", "b20a8e306c88e4f3d143e12ca08a1db56e1204f9", "c7fc6acace33d5c23616d99249672b666a5ae875",
     {"VE/Cardinality/Semantics.lean": [14, 16, 24, 26, 32, 33, 34, 52, 55, 56, 57, 58],
      "VE/Cardinality/Syntax.lean": [70, 86, 88, 91]}),
    ("ap-2 F1", "584ac3bb36a3909d1307239af5d07a7ca3323d71", "c2b1a7d442b492934580cc2db099fe6ac27eef92",
     {"VE/Acts/Syntax.lean": [66, 80, 86, 92, 101, 117, 119], "VE/Acts/Read.lean": [19]}),
    ("ap-2 F7", "e13a4e413574b68e88446043e873661114182ab2", "c2b1a7d442b492934580cc2db099fe6ac27eef92",
     {"VE/Acts/Syntax.lean": [83, 92, 96, 113, 114, 119]}),
    ("ap-2 F10", "3d1085285cb224c97333ac82bc255c469a060458", "c2b1a7d442b492934580cc2db099fe6ac27eef92",
     {"VE/Acts/Syntax.lean": [78, 79]}),
    ("ap-2 F11", "aa2fd56e3e335b5c8926a97d729d5da022754513", "c2b1a7d442b492934580cc2db099fe6ac27eef92",
     {"VE/Acts/Syntax.lean": [88, 89, 121, 122]}),
]
BUDGET = 1200  # step 1: each replay takes at most 20 minutes
FINAL = {"aa2fd56e"}  # the replays run with the final tool (the evidence does not name the tool's commit)


def replay(head: str, base: str, jobs: int) -> None:
    tree = Path(f"/tmp/trustmut-replay-{head[:8]}")
    subprocess.run(["git", "worktree", "add", "--detach", str(tree), head], cwd=ROOT, check=True, capture_output=True)
    try:
        (tree / "lean/.lake/build").mkdir(parents=True)
        for part in ("lib", "ir"):
            subprocess.run(["cp", "-al", str(ROOT / "lean/.lake/build" / part), str(tree / "lean/.lake/build")],
                           check=True)
        EVIDENCE.mkdir(exist_ok=True)
        started = time.monotonic()
        done = subprocess.run([sys.executable, __file__, "--profiled", "--root", str(tree), "--base",
                               base, "--jobs", str(jobs), "--max-mutants", "100000",
                               "--json", str(EVIDENCE / f"{head[:8]}.json")], cwd=ROOT, text=True)
        print(f"{head[:8]}: exit {done.returncode} in {time.monotonic() - started:.0f} s", flush=True)
    finally:
        shutil.rmtree(tree / "lean/.lake", ignore_errors=True)
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, check=False)


def profiled(argv: list[str]) -> int:
    """The tool's `main(argv)` in this process, unchanged, and its evidence JSON given a "profile": the 5-minute load
    sampled every 15 s (`os.getloadavg`), the seconds spent in `probe` (section 1e's elaborations, the control pass
    included) and in Lake's builds, each summed over the threads, and the commit and sha256 of the tool that ran.
    Timing wraps the two functions only, so no verdict can change (the DRI's note 2026-10-20: which part of a replay
    over the budget is the probe's)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import trust_mutants
    spent, lock, loads, done = Counter(), threading.Lock(), [os.getloadavg()[1]], threading.Event()

    def timed(name, f):
        def wrapper(*a, **k):
            started = time.monotonic()
            try:
                return f(*a, **k)
            finally:
                with lock:
                    spent[name(a) if callable(name) else name] += time.monotonic() - started
        return wrapper

    def sample() -> None:
        while not done.wait(15):
            loads.append(os.getloadavg()[1])
    trust_mutants.probe = timed("probe", trust_mutants.probe)
    trust_mutants.Scratch.lake = timed(lambda a: f"lake {a[2]}", trust_mutants.Scratch.lake)
    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    try:
        code = trust_mutants.main(argv)
    finally:
        done.set()
        sampler.join()
    out = Path(argv[argv.index("--json") + 1])
    data = json.loads(out.read_text())
    data["profile"] = {
        "tool": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "tool_sha256": hashlib.sha256((ROOT / "tools/trust_mutants.py").read_bytes()).hexdigest(),
        "load5": {"min": min(loads), "max": max(loads), "mean": round(sum(loads) / len(loads), 1),
                  "samples": len(loads)},
        "thread_seconds": {k: round(v) for k, v in sorted(spent.items())}}
    out.write_text(trust_mutants.evidence(data))
    return code


def profile() -> str:
    """The saved profiles (`profiled`): each replay's load and the probe's share of the time its threads spent."""
    said = []
    for finding, head, _, _ in FINDINGS:
        data = json.loads((EVIDENCE / f"{head[:8]}.json").read_text())
        if p := data.get("profile"):
            t, load = p["thread_seconds"], p["load5"]
            busy = t.get("probe", 0) + t.get("lake build", 0)
            said.append(f"{finding} {data['seconds']} s at {data['jobs']} jobs, tool {p['tool'][:9]}, 5-minute load "
                        f"{load['min']:.0f}-{load['max']:.0f} (mean {load['mean']}); thread seconds: probe "
                        f"{t.get('probe', 0)}, builds {t.get('lake build', 0)} (the probe "
                        f"{100 * t.get('probe', 0) / max(busy, 1):.0f}% of the two)")
    return "Profiled replays: " + ("; ".join(said) or "none") + "."


def table() -> list[str]:
    rows = ["| Finding | HEAD | Mutants (run / survivors / invalid / unknown) | Seconds at 8 jobs "
            "| Survivors on the named lines | Flagged | Within the default 60 |", "|---|---|---|---|---|---|---|"]
    for finding, head, _, sites in FINDINGS:
        data = json.loads((EVIDENCE / f"{head[:8]}.json").read_text())
        mutants = data["mutants"]
        hits = [m for m in mutants if m["status"] == "SURVIVOR" and m["line"] in sites.get(m["file"], [])]
        first = {m["id"] for m in mutants[:60]}
        c = data["counts"]
        sites = list(dict.fromkeys(f"`{m['file'].split('/')[-1]}:{m['line']}` {m['operator']}" for m in hits))
        listed = "; ".join(sites[:6]) + (" ..." if len(sites) > 6 else "")
        rows.append(f"| {finding} | `{head[:9]}` | {len(mutants)} / {c['SURVIVOR']} / {c['INVALID']} / {c['UNKNOWN']} "
                    f"| {data['seconds']} | {len(hits)}: {listed} "
                    f"| {'yes' if hits else 'NO'} | {'yes' if any(m['id'] in first for m in hits) else 'no'} |")
    return rows


def f9() -> str:
    """Review F9's rules on the saved replays: a mutant that changes its line count (`relined` decides it now) and a
    kill on a parse error (now UNKNOWN, `PARSE`); with neither, the F9 fix changes no replayed verdict."""
    sys.path.insert(0, str(ROOT / "tools"))
    from trust_mutants import PARSE
    moved = parsed = 0
    for head in dict.fromkeys(head for _, head, _, _ in FINDINGS):
        for m in json.loads((EVIDENCE / f"{head[:8]}.json").read_text())["mutants"]:
            moved += m["after"].count("\n") != m["before"].count("\n")
            parsed += m["status"] == "KILLED" and bool(PARSE.match(m["detail"].split(": ", 1)[1]))
    return f"Review F9 on the replays: {moved} mutants change their line count, {parsed} kills are parse errors."


def f10() -> str:
    """Review F10's rule on the saved replays: a kill or INVALID where Lean gave no answer (`NO_ANSWER`; now UNKNOWN).
    The evidence keeps each message's first line, where every form `NO_ANSWER` names but a `#guard_msgs` quote
    shows (no replayed tree has a `#guard_msgs`), and the kills' first lines by kind."""
    sys.path.insert(0, str(ROOT / "tools"))
    from trust_mutants import NO_ANSWER
    blank, kinds = 0, Counter()
    for head in dict.fromkeys(head for _, head, _, _ in FINDINGS):
        for m in json.loads((EVIDENCE / f"{head[:8]}.json").read_text())["mutants"]:
            blank += m["status"] in ("KILLED", "INVALID") and bool(NO_ANSWER.search(m["detail"]))
            if m["status"] == "KILLED":
                kinds[" ".join(m["detail"].split(": ", 1)[1].split()[:4])] += 1
    return (f"Review F10 on the replays: {blank} kills or INVALID gave no answer; the kills: "
            + ", ".join(f"{n} '{k}'" for k, n in kinds.most_common()) + ".")


def f11() -> str:
    """Review F11/F12's rule on the saved replays (run with it): the kills by message, and the UNKNOWN and INVALID by
    reason, the detail's text after its location."""
    kinds: dict[str, Counter] = {"KILLED": Counter(), "UNKNOWN": Counter(), "INVALID": Counter()}
    for head in dict.fromkeys(head for _, head, _, _ in FINDINGS):
        for m in json.loads((EVIDENCE / f"{head[:8]}.json").read_text())["mutants"]:
            if m["status"] in kinds:
                said = m["detail"].split(": ", 1)[1] if m["detail"].startswith("lean/") else m["detail"]
                reason = said[said.rfind(" ("):].strip() if said.endswith(")") and " (" in said else ""
                kinds[m["status"]][" ".join(said.split()[:3]) + (f" {reason}" if reason else "")] += 1
    return "Review F11/F12 on the replays: " + "; ".join(
        f"{status}: " + ", ".join(f"{n} '{k}'" for k, n in found.most_common()) for status, found in kinds.items())


def budget() -> str:
    """Step 1's time budget on the saved replays (review F14: the report quotes this line, never a claim of its own):
    each replay within `BUDGET` or over it, and which tool ran it."""
    rows = [(finding, head[:8], json.loads((EVIDENCE / f"{head[:8]}.json").read_text())["seconds"])
            for finding, head, _, _ in FINDINGS]
    def say(part: list) -> str:
        return ", ".join(f"{f} {s} s ({'final' if h in FINAL else 'F8'} tool)" for f, h, s in part) or "none"
    within = [r for r in rows if r[2] <= BUDGET]
    final = [r for r in rows if r[1] in FINAL]
    return (f"Step 1's budget ({BUDGET} s a replay): {len(within)} of {len(rows)} replays within it; over it: "
            f"{say([r for r in rows if r[2] > BUDGET])}. On the final tool {sum(r[2] <= BUDGET for r in final)} of "
            f"{len(final)} within it.")


def main() -> int:
    if sys.argv[1:2] == ["--profiled"]:  # `replay`'s run of the tool (the arguments are the tool's)
        return profiled(sys.argv[2:])
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--only", help="with --run, only the HEAD that starts with this")
    args = parser.parse_args()
    if args.run:
        for head, base in dict.fromkeys((head, base) for _, head, base, _ in FINDINGS):
            if not args.only or head.startswith(args.only):
                replay(head, base, args.jobs)
    if not args.only:
        print("\n".join([*table(), "", budget(), profile(), f9(), f10(), f11()]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
