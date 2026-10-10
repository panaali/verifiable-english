"""Summarize one timed suite run for docs/eff-tests/REPORT.md: summarize_suite.py LABEL JUNIT RUN OUT.

RUN is the wrapper's record (`{"commit", "command", "started", "ended", "loads"}`: epoch seconds and the
1-minute load average sampled each minute); JUNIT is the run's pytest JUnit XML. OUT gets the counts, the
wall time, the load range, the sum of the test times, the slowest tests and the tests this branch changed.
"""
import json
import statistics
import sys
import xml.etree.ElementTree as ET

WATCHED = ("tests.test_enum_domains", "tests.test_wire_gate_corpus", "tests.test_difffuzz")


def nodeid(case):
    module = case.get("classname", "")
    return f"{module.replace('.', '/')}.py::{case.get('name')}" if module.startswith("tests.") else \
        f"{module}::{case.get('name')}"


def main(label, junit, run, out):
    record = json.load(open(run))
    cases = list(ET.parse(junit).getroot().iter("testcase"))
    outcomes = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
    failed, times = [], []
    for case in cases:
        kind = next((child.tag for child in case if child.tag in ("failure", "error", "skipped")), "passed")
        outcomes["failed" if kind == "failure" else kind] += 1
        if kind in ("failure", "error"):
            failed.append(nodeid(case))
        times.append((float(case.get("time", 0)), nodeid(case)))
    watched = {nodeid(c): round(float(c.get("time", 0)), 1) for c in cases
               if c.get("classname", "").startswith(WATCHED) and float(c.get("time", 0)) >= 5}
    properties = {nodeid(c): {p.get("name"): p.get("value") for p in c.iter("property")}
                  for c in cases if any(True for _ in c.iter("property"))}
    loads = record["loads"]
    summary = {"label": label, "commit": record["commit"], "command": record["command"],
               "wall_seconds": round(record["ended"] - record["started"]),
               "load": {"min": min(loads), "median": statistics.median(loads), "max": max(loads),
                        "samples": len(loads)},
               "tests": len(cases), "outcomes": outcomes, "failed": sorted(failed),
               "sum_test_seconds": round(sum(t for t, _ in times)),
               "slowest": [[round(t, 1), name] for t, name in sorted(times, reverse=True)[:15]],
               "watched": dict(sorted(watched.items())), "properties": properties}
    with open(out, "w") as handle:
        json.dump(summary, handle, indent=1)
        handle.write("\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
