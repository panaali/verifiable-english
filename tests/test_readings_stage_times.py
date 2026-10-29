"""The readings admission profiler is opt-in and writes only stage JSON to stderr."""
import json
import os
import subprocess

import pytest

from tests.lean_routes import SERVICE
from tests.subprocesses import HANG_TIMEOUT


CASE = {"id": "profile", "kind": "readings-validate", "environment": {},
        "document": {"units": [], "reading_sets": []}}
REQUEST = json.dumps({"id": "profile", "mode": "readings-route", "cases": [CASE]}) + "\n"


def run(value):
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    env = os.environ.copy()
    env.pop("VE_READINGS_STAGE_TIMES", None)
    if value is not None:
        env["VE_READINGS_STAGE_TIMES"] = value
    return subprocess.run([str(SERVICE)], input=REQUEST, text=True, capture_output=True,
                          timeout=HANG_TIMEOUT, env=env, check=True)


def test_readings_stage_times_are_silent_by_default():
    assert run(None).stderr == ""
    assert run("0").stderr == ""


def test_readings_stage_times_are_json_lines_for_each_stage():
    rows = [json.loads(line) for line in run("1").stderr.splitlines()]
    assert [row["stage"] for row in rows] == ["splitCase", "admitS2", "runCase"]
    assert all(row["case"] == "profile" and type(row["nanos"]) is int and row["nanos"] >= 0
               and type(row["cpu_ticks"]) is int and row["status"] in ("ok", "error") for row in rows)


def test_readings_stage_times_do_not_change_the_answer():
    off = run(None).stdout
    on = run("1").stdout
    assert on == off
    response = json.loads(off.splitlines()[-1])
    assert response["status"] == "ok" and response["results"][0]["result"]["id"] == "profile"
