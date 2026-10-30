"""The saved scale admission evidence holds whole-request CPU only; the stage profiler was withdrawn
(reviews/dri-decisions-20261029-scale-admission-profile.md item 1). Reads saved files, never the live tree."""
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
SAVED = {name: json.loads((FOLDER / name).read_text()) for name in FILES}
RUNS = {case: data["runs"] for saved in SAVED.values() for case, data in saved["cases"].items()}


def stage_values(value):
    children = value.values() if isinstance(value, dict) else value if isinstance(value, list) else ()
    if isinstance(value, dict):
        yield from (child for key, child in value.items() if "stage" in key.lower() or key in ("cpu_ticks", "nanos"))
    for child in children:
        yield from stage_values(child)


def test_every_case_has_three_runs_with_numeric_cpu():
    assert set(RUNS) == CASES
    for case, runs in RUNS.items():
        assert len(runs) == 3 and all(type(run["cpu_seconds"]) in (int, float) for run in runs), case


def test_no_numeric_stage_count_or_total():
    for name, saved in SAVED.items():
        assert all(value == "UNKNOWN" for value in stage_values(saved)), name


def test_measurement_scripts_do_not_set_the_withdrawn_stage_variable():
    for script in ("measure_admission.py", "admission_cases.py"):
        nodes = list(ast.walk(ast.parse((FOLDER / script).read_text())))
        assert not any(isinstance(node, ast.Constant) and node.value == "VE_READINGS_STAGE_TIMES" for node in nodes)
        assert not any(isinstance(node, ast.keyword) and node.arg == "env" for node in nodes), script


def test_profile_medians_are_the_saved_medians():
    lines = (FOLDER / "admission-profile-20261029.md").read_text().splitlines()
    for case, runs in RUNS.items():
        median = statistics.median(run["cpu_seconds"] for run in runs)
        row = [line for line in lines if line.startswith("|") and f"`{case}`" in line]
        assert len(row) == 1 and f"| {median:.2f} |" in row[0], (case, median, row)
