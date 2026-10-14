"""Test speed B5: how much sooner a selected run shows a failure when the failing test file runs first.

A replay, not a timing: each test file's duration is from a coverage map recorded by the nightly
(`tools/test_map.py record`, every file in its own process). `tools/test_map.record_units` starts files
on `JOBS` workers in a given order, and a failure shows when its file ends. For each file F, assumed to
be the one that fails (as in a fix round, where the test that failed last time is the likely one to fail
again), the replay computes when F ends with the files in name order (before B5) and with F first (B5).

usage: uv run python docs/test-speed-b5/measure.py MAP.json.gz   (writes evidence/durations.json and
evidence/first-failure.json beside this script; `--check` recomputes from the saved durations instead)
"""
from __future__ import annotations

import gzip
import heapq
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
JOBS = 8  # tools/select_tests.py --jobs default


def finish(order: list[str], seconds: dict[str, float], jobs: int = JOBS) -> dict[str, float]:
    """When each file ends, its files started in `order` on `jobs` workers as each worker frees up."""
    free = [0.0] * jobs
    ends = {}
    for unit in order:
        start = heapq.heappop(free)
        ends[unit] = start + seconds[unit]
        heapq.heappush(free, ends[unit])
    return ends


def replay(seconds: dict[str, float]) -> dict:
    names = sorted(seconds)
    before = finish(names, seconds)
    rows = {unit: {"seconds": seconds[unit], "name_order": round(before[unit], 1),
                   "first": round(seconds[unit], 1)} for unit in names}
    saved = sorted(round((before[unit] - seconds[unit]) / 60, 2) for unit in names)
    return {
        "jobs": JOBS, "files": len(names), "suite_seconds": round(sum(seconds.values()), 1),
        "makespan_name_order": round(max(before.values()), 1),
        "saved_minutes": {"median": round(statistics.median(saved), 1), "mean": round(statistics.fmean(saved), 1),
                          "p90": round(saved[int(0.9 * (len(saved) - 1))], 1), "max": round(saved[-1], 1)},
        "files_saving_10_min_or_more": sum(minutes >= 10 for minutes in saved),
        "rows": rows,
    }


def main() -> int:
    if sys.argv[1:] == ["--check"]:
        durations = json.loads((EVIDENCE / "durations.json").read_text())
        saved = json.loads((EVIDENCE / "first-failure.json").read_text())
        fresh = {**replay(durations["seconds"]), "map": durations["map"]}
        if fresh != saved:
            print("evidence/first-failure.json is not the replay of evidence/durations.json")
            return 1
        print("first-failure.json matches the replay of durations.json")
        return 0
    path = Path(sys.argv[1])
    data = json.load(gzip.open(path, "rt"))
    seconds = {unit: status["seconds"] for unit, status in data["status"].items()}
    source = {"file": path.name, "commit": data["commit"], "created": data["created"], "tree": data.get("tree", "")}
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "durations.json").write_text(json.dumps({"map": source, "seconds": dict(sorted(seconds.items()))},
                                                        indent=1, sort_keys=True) + "\n")
    (EVIDENCE / "first-failure.json").write_text(json.dumps({**replay(seconds), "map": source},
                                                            indent=1, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in replay(seconds).items() if key != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
