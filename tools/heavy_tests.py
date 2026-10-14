"""Generate the heavy pytest inventory from a complete duration report.

The committed report is the measured Mac run. A nightly can pass its own
``--durations=0`` output or JSON report with ``--report`` and use ``--write``.
``--check`` refuses an unmarked test over 20 seconds as well as a stale list.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "tests/heavy-durations.json"
INVENTORY = ROOT / "tests/heavy.json"
THRESHOLD = 10.0
BUDGET = 20.0
DURATION = re.compile(r"^\s*([\d.]+)s\s+(?:call|setup|teardown)\s+(tests/\S+::\S+)")


def read_report(path: Path) -> tuple[str, dict[str, float]]:
    raw = path.read_text()
    if path.suffix == ".json":
        data = json.loads(raw)
        if "tests" in data:
            rows = data["tests"]
            if isinstance(rows, list):  # runA.json
                times = {row["t"]: row["dur"] for row in rows
                         if row["t"].startswith("tests/") and "::" in row["t"]}
            else:
                times = rows
            run = data.get("run", data.get("mode", path.name))
        else:
            raise ValueError("duration report has no tests")
    else:
        times = {}
        for line in raw.splitlines():
            match = DURATION.match(line)
            if match:
                seconds, nodeid = match.groups()
                times[nodeid] = times.get(nodeid, 0.0) + float(seconds)
        run = path.name
    if not times or any(not isinstance(t, (int, float)) or isinstance(t, bool) or t < 0
                        for t in times.values()):
        raise ValueError("duration report has no valid nonnegative test times")
    return str(run), {str(nodeid): float(seconds) for nodeid, seconds in times.items()}


def inventory(run: str, times: dict[str, float]) -> dict:
    return {"run": run, "threshold_seconds": THRESHOLD,
            "collected_count": len(times),
            "heavy": [{"nodeid": nodeid, "seconds": seconds, "run": run}
                      for nodeid, seconds in sorted(times.items()) if seconds >= THRESHOLD]}


def check_budget(times: dict[str, float], marked: set[str]) -> list[str]:
    return [nodeid for nodeid, seconds in sorted(times.items())
            if seconds > BUDGET and nodeid not in marked]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=REPORT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    run, times = read_report(args.report)
    expected = inventory(run, times)
    if args.write:
        if args.report.resolve() != REPORT.resolve():
            REPORT.write_text(json.dumps({"run": run, "tests": times}, sort_keys=True,
                                         separators=(",", ":")) + "\n")
        INVENTORY.write_text(json.dumps(expected, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {len(expected['heavy'])} heavy of {len(times)} tests from {run}")
        return 0
    actual = json.loads(INVENTORY.read_text())
    unmarked = check_budget(times, {row["nodeid"] for row in actual["heavy"]})
    if unmarked:
        print("unmarked tests over 20 s: " + ", ".join(unmarked))
    if actual != expected:
        print("tests/heavy.json is stale; regenerate from the duration report")
    return int(bool(unmarked or actual != expected))


if __name__ == "__main__":
    raise SystemExit(main())
