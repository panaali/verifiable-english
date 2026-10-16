#!/usr/bin/env python3
"""Replay test selection on the 17 first-parent merges of Oct 11-14 (test-architecture draft 2, section 2.3).

Each row is the plan `tools/select_tests.py --commit M --json` makes for a merge M, against its first parent,
run by the selector of a given checkout (`--selector`, default this one) in a private cache:

* `as_it_was`: no map given; the selector looks in the shared cache (`$VE_TESTMAP_CACHE`) for a map of an
  ancestor of the parent, as it did then. Not reproducible (the cache changes); measured once.
* `fresh`: the map `evidence/map-recorded.json.gz` (main's map at 91858c03, recorded by main's recorder) taken
  as recorded at the parent (`--assume-fresh`), the "map after every merge" of rank 4.
* `fresh_complete`: the same map with the nine units the plan found unrecorded taken from
  `evidence/nine-units.json.gz`, recorded by this branch's recorder (`tools/test_map.py record`).
* `fresh_cutoff`: `fresh_complete` with the Lean build records of `evidence/lean-builds/` (one per distinct
  `lean/` tree of the window, built and hashed on the VM, linux-x86_64), so the binary cutoff applies.

A plan's share is the recorded seconds of the units it selects over the recorded seconds of every unit of
the complete map (the same weights for every column); `mac_share` is the same over the Mac test seconds of
each test file in run A of the plan (`evidence/mac-durations.json`; files run A did not have count 0).

    python3 docs/test-architecture/select/replay.py --write fresh fresh_complete fresh_cutoff
    python3 docs/test-architecture/select/replay.py --selector /tmp/main --label main --write as_it_was fresh
    python3 docs/test-architecture/select/replay.py --check   # this checkout's saved rows, recomputed

`--check` recomputes this checkout's saved columns and fails on any difference in a selected set: the
regression test of the plans that batch evidence gets at the batch gate and merge train (architecture
decision D4). It reads the build records only on linux-x86_64, where they were measured.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import test_map  # noqa: E402

EVIDENCE = HERE / "evidence"
REPLAY = EVIDENCE / "replay.json"
RECORDED = EVIDENCE / "map-recorded.json.gz"
NINE = EVIDENCE / "nine-units.json.gz"
BUILDS = EVIDENCE / "lean-builds"
MAC = EVIDENCE / "mac-durations.json"
BUILD_PLATFORM = "linux-x86_64"
# The 17 first-parent merges of Oct 11 00:00Z - Oct 14 18:00Z, oldest first (draft 2, 2.3).
MERGES = ("cd546c0d9", "8cec935af", "f1b719c7a", "c9b8cba63", "615e89d7f", "49de179e7", "11676c2c0",
          "da0c04bd9", "09a807d7e", "406736a47", "d006b1f48", "2d964d5dc", "f98183bf5", "dccd9cf5a",
          "4667e8de6", "8594f1d05", "9f40783b8")
COLUMNS = ("as_it_was", "fresh", "fresh_complete", "fresh_cutoff")


def complete_map(directory: Path) -> Path:
    """The recorded map with the nine units replaced by their recordings on this branch."""
    recorded, nine = test_map.load(RECORDED), test_map.load(NINE)
    results = {}
    for source in (recorded, nine):
        edges = test_map.unit_edges(source)
        for unit in source["tests"]:
            results[unit] = {**edges[unit], **source["status"][unit]}
    data = test_map.build_map(results, recorded["commit"])
    path = directory / "map-complete.json.gz"
    test_map.write_map(data, path)
    return path


def plan(selector: Path, merge: str, column: str, work: Path, complete: Path) -> dict:
    env = {**os.environ, "XDG_CACHE_HOME": str(work / "xdg"), "VE_LEAN_BUILDS": str(work / "no-builds")}
    env.pop("VE_TESTMAP", None)
    command = ["python3", "tools/select_tests.py", "--commit", merge, "--json"]
    if column != "as_it_was":
        env["VE_TESTMAP_CACHE"] = str(work / "no-maps")
        command += ["--assume-fresh", "--map", str(RECORDED if column == "fresh" else complete)]
    if column == "fresh_cutoff":
        builds = work / "builds"
        if not builds.exists():
            builds.mkdir()
            for record in BUILDS.glob("*.json"):
                shutil.copy(record, builds / record.name)
        env["VE_LEAN_BUILDS"] = str(builds)
    result = subprocess.run(command, cwd=selector, env=env, capture_output=True, text=True, check=True)
    return json.loads(result.stdout[result.stdout.index("{"):])


def row(data: dict, weights: dict[str, float], total: float) -> dict:
    selected = sorted(data["selected"])
    cutoff = data.get("lean_cutoff") or {}
    mac = json.loads(MAC.read_text())
    return {"selected": selected, "units": len(selected), "full_count": data["full_count"],
            "share": round(100 * sum(weights.get(unit, 0.0) for unit in selected) / total, 1),
            "mac_share": round(100 * sum(mac["files"].get(unit, 0.0) for unit in selected) / mac["total"], 1),
            "full": data["full"], "full_reasons": data["full_reasons"], "plan_seconds": data["seconds"],
            "map": (data["map"] or {}).get("commit"), "lean_cutoff": cutoff.get("state"),
            "rebuilt": cutoff.get("rebuilt"), "same": cutoff.get("same")}


def replay(selector: Path, columns: list[str]) -> dict[str, dict[str, dict]]:
    if "fresh_cutoff" in columns and f"{sys.platform}-{platform.machine()}" != BUILD_PLATFORM:
        raise SystemExit(f"the build records are {BUILD_PLATFORM}'s; replay fresh_cutoff there")
    with tempfile.TemporaryDirectory(prefix="ve-select-replay-") as directory:
        work = Path(directory)
        complete = complete_map(work)
        weights = {unit: float(status["seconds"]) for unit, status in test_map.load(complete)["status"].items()}
        total = sum(weights.values())
        found: dict[str, dict[str, dict]] = {}
        for column in columns:
            for merge in MERGES:
                found.setdefault(column, {})[merge] = row(plan(selector, merge, column, work, complete),
                                                           weights, total)
                print(f"{column} {merge}: {found[column][merge]['units']} units, "
                      f"{found[column][merge]['share']}%", flush=True)
        return found


def summary(rows: dict[str, dict]) -> dict:
    shares = [entry["share"] for entry in rows.values()]
    return {"average_share": round(sum(shares) / len(shares), 1),
            "average_mac_share": round(sum(entry["mac_share"] for entry in rows.values()) / len(rows), 1),
            "average_units": round(sum(entry["units"] for entry in rows.values()) / len(rows), 1),
            "full_plans": sum(entry["full"] for entry in rows.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("columns", nargs="*", help=f"some of {', '.join(COLUMNS)} (default: all but as_it_was)")
    parser.add_argument("--selector", type=Path, default=ROOT, help="the checkout whose selector runs")
    parser.add_argument("--label", default="branch", help="the name the rows are saved under")
    parser.add_argument("--write", action="store_true", help="save the rows in evidence/replay.json")
    parser.add_argument("--check", action="store_true", help="recompute this checkout's saved rows")
    args = parser.parse_args()
    if set(args.columns) - set(COLUMNS):
        parser.error(f"unknown columns {sorted(set(args.columns) - set(COLUMNS))}")
    saved = json.loads(REPLAY.read_text()) if REPLAY.exists() else {}
    if args.check:
        columns = [column for column in saved.get(args.label, {}) if column != "as_it_was"]
        found = replay(args.selector, columns)
        differ = [f"{column} {merge}" for column in columns for merge in MERGES
                  if found[column][merge]["selected"] != saved[args.label][column]["rows"][merge]["selected"]]
        print(f"replayed {len(columns)} columns x {len(MERGES)} merges: "
              + (f"{len(differ)} plans differ from the saved ones: {differ}" if differ else "every plan as saved"))
        return 1 if differ else 0
    found = replay(args.selector, args.columns or list(COLUMNS[1:]))
    for column, rows in found.items():
        print(f"{column}: {summary(rows)}")
    if args.write:
        entry = saved.setdefault(args.label, {})
        for column, rows in found.items():
            entry[column] = {"summary": summary(rows), "rows": rows}
        REPLAY.write_text(json.dumps(saved, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
