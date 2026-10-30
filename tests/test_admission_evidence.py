"""The scale admission evidence holds whole-request CPU only (SAVED evidence, never the live tree).

The stage profiler was withdrawn (reviews/dri-decisions-20261029-scale-admission-profile.md item 1),
so every saved case has three runs with numeric process CPU and no numeric stage figure, the runner
does not set the withdrawn variable, and the report's medians are those of the saved runs.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import statistics

FOLDER = Path(__file__).resolve().parents[1] / "docs/perf"
FILES = ("admission-profile-evidence.json", "admission-profile-controlled.json",
         "admission-profile-constitution.json")
CASES = {"admission-prefix-50", "admission-prefix-75", "admission-prefix-100-main3", "admission-prefix-100",
         "admission-prefix-100-2x", "admission-prefix-100-4x", "admission-constitution-185kb"}


def cases() -> dict:
    found = {}
    for name in FILES:
        found.update(json.loads((FOLDER / name).read_text())["cases"])
    return found


def stage_values(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if "stage" in key.lower() or key in ("cpu_ticks", "nanos"):
                yield key, child
            yield from stage_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from stage_values(child)


def test_every_case_has_three_runs_with_numeric_cpu():
    saved = cases()
    assert set(saved) == CASES
    for name, case in saved.items():
        assert len(case["runs"]) == 3, name
        for run in case["runs"]:
            cpu = run["cpu_seconds"]
            assert type(cpu) in (int, float) and cpu > 0, (name, cpu)


def test_no_numeric_stage_count_or_total():
    for name in FILES:
        rows = list(stage_values(json.loads((FOLDER / name).read_text())))
        assert all(value == "UNKNOWN" for _, value in rows), (name, rows[:3])


def test_measurement_scripts_do_not_set_the_withdrawn_stage_variable():
    for script in ("measure_admission.py", "admission_cases.py"):
        tree = ast.parse((FOLDER / script).read_text())
        constants = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}
        assert "VE_READINGS_STAGE_TIMES" not in constants, script
        assert not any(isinstance(node, ast.keyword) and node.arg == "env" for node in ast.walk(tree)), script


def test_profile_medians_are_the_saved_medians():
    lines = (FOLDER / "admission-profile-20261029.md").read_text().splitlines()
    for name, case in cases().items():
        median = statistics.median(run["cpu_seconds"] for run in case["runs"])
        row = [line for line in lines if line.startswith("|") and f"`{name}`" in line]
        assert len(row) == 1 and f"| {median:.2f} |" in row[0], (name, median, row)
