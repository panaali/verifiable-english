"""docs/testing-profile.md states the numbers of its measurement artifacts (testperf review C).

The tables and the per-executable figures are read again from `docs/testing-profile/before.json` and
`after.json`, which `tools/test_profile_report.py --json` wrote from the raw per-worker records.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/testing-profile.md").read_text()
RUNS = {name: json.loads((ROOT / f"docs/testing-profile/{name}.json").read_text()) for name in ("before", "after")}
# The category table's row labels, by the report's category names.
CATEGORIES = {
    "Python in the test process": "python in the test process (remainder)",
    "Lean routes and runners (one process per call)": "lean route / runner",
    "child Python processes (nested pytest, CLIs)": "child python",
    "other tools (pre-commit, fake checkers)": "other",
    "Rust checker": "rust checker",
    "builds inside tests (lake, cargo)": "build (lake/cargo)",
    "Lean service (CPU)": "lean service (CPU)",
    "git": "git",
}


def number(value):
    return f"{round(value):,}"


def row(label):
    lines = [line for line in DOC.splitlines() if line.startswith(f"| {label} |")]
    assert len(lines) == 1, label
    return [cell.strip() for cell in lines[0].strip("|").split("|")][1:]


def table_after(heading):
    """The rows of the first table after the line starting with `heading`, without its header."""
    lines = DOC.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
        elif rows:
            break
    return rows[2:]


def test_result_table():
    before, after = RUNS["before"], RUNS["after"]
    assert row("sum of test wall times") == [f"{number(before['total_test_seconds'])} s",
                                             f"{number(after['total_test_seconds'])} s"]
    assert row("suite CPU (workers and every descendant)") == [f"{number(before['suite_cpu'])} s",
                                                               f"{number(after['suite_cpu'])} s"]
    run = row("tests run by default")
    for cell, data in zip(run, (before, after), strict=True):
        passed, skipped = (int(value.replace(",", "")) for value in
                           re.match(r"([\d,]+) passed, (\d+) skipped", cell).groups())
        assert passed + skipped == data["tests"]


def test_category_table():
    assert [cells[0] for cells in table_after("Test wall time by category")] == list(CATEGORIES)
    for label, category in CATEGORIES.items():
        for cell, data in zip(row(label), (RUNS["before"], RUNS["after"]), strict=True):
            seconds = data["categories"][category]
            value, _, share = cell.partition(" (")
            assert value == number(seconds), (label, cell)
            if share:
                assert share == f"{round(100 * seconds / data['total_test_seconds'])}%)", (label, cell)


def test_slowest_tests_tables():
    for heading, name in (("Before (`-n 8`", "before"), ("After (`-n 8`", "after")):
        rows = table_after(heading)
        assert rows == [[number(seconds), nodeid.removeprefix("tests/")]
                        for seconds, nodeid in RUNS[name]["slowest_tests"][:len(rows)]]
        assert len(rows) == 20


def executables(name, category):
    return [row for row in RUNS[name]["executables"] if row["category"] == category]


def test_per_executable_figures():
    lean = executables("after", "lean route / runner")
    assert (f"After: {sum(row['count'] for row in lean):,} route calls, {number(sum(row['wall'] for row in lean))} s "
            f"of process time, {number(sum(row['cpu'] for row in lean))} CPU s") in DOC
    (service,) = executables("after", "lean service (CPU)")
    assert f"The {service['count']} service starts per" in DOC
    assert f"they cost {number(service['cpu'])} CPU s in total" in DOC
    (rust,) = executables("after", "rust checker")
    assert (f"**Rust.** {rust['count']:,} calls, {number(rust['wall'])} s, median "
            f"{round(1000 * rust['median_wall'])} ms") in DOC
