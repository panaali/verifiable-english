"""The readings admission profiler is opt-in and writes only stage JSON to stderr."""
import json
import os
from pathlib import Path
import subprocess

import pytest

from tests.lean_routes import SERVICE
from tests.subprocesses import HANG_TIMEOUT


ROOT = Path(__file__).resolve().parents[1]


CASE = {"id": "profile", "kind": "readings-validate", "environment": {},
        "document": {"units": [], "reading_sets": []}}
REQUEST = json.dumps({"id": "profile", "mode": "readings-route", "cases": [CASE]}) + "\n"


def run(value, request=REQUEST):
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    env = os.environ.copy()
    env.pop("VE_READINGS_STAGE_TIMES", None)
    if value is not None:
        env["VE_READINGS_STAGE_TIMES"] = value
    return subprocess.run([str(SERVICE)], input=request, text=True, capture_output=True,
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


@pytest.mark.parametrize("kind", ["readings-elaborate", "readings-choice", "readings-verdicts"])
def test_split_w2_fixed_part_completion_is_timed(kind):
    from tests.test_readings_companions_lean import env_main, fc1

    document, _, _ = fc1()
    case = {"id": kind, "kind": kind, "environment": env_main(), "document": document}
    if kind == "readings-verdicts":
        case.update(question="premises", assumed=[])
    request = json.dumps({"id": "profile", "mode": "readings-route", "cases": [case]}) + "\n"
    observed = run("1", request)
    if kind == "readings-verdicts":
        result = json.loads(observed.stdout.splitlines()[-1])["results"][0]["result"]
        assert result["status"] == "ok"
    rows = [json.loads(line) for line in observed.stderr.splitlines()]
    main_rows = [row for row in rows if row["part"] == "main"]
    main = [row["stage"] for row in main_rows]
    assert main.count("admitS2") >= 2
    assert any(row["stage"] == "admitNDFull" and row["status"] == "ok" for row in main_rows)


def test_normal_client_profiles_registered_and_reused_handle(monkeypatch):
    from ve.backends.lean_service import LeanService

    monkeypatch.setenv("VE_READINGS_STAGE_TIMES", "1")
    with LeanService(timeout=HANG_TIMEOUT, allow_unlisted_build=True) as service:
        for repeat in range(2):
            start, _ = service.stderr()
            answer = service.run("readings-route", [CASE], timeout=HANG_TIMEOUT)
            assert answer[0]["id"] == "profile"
            _, stderr = service.stderr(start)
            rows = [json.loads(line) for line in stderr.splitlines()]
            assert any(row["stage"] == "splitCase" and row["case"] == "profile" for row in rows), repeat


def test_saved_twofold_profile_records_fixed_part_completion():
    evidence = json.loads((ROOT / "docs/perf/admission-profile-evidence.json").read_text())
    runs = evidence["cases"]["admission-prefix-100-2x"]["runs"]
    assert len(runs) == 3
    for run in runs:
        main_rows = [row for row in run["stages"] if row["part"] == "main"]
        main = [row["stage"] for row in main_rows]
        assert main.count("admitS2") >= 2
        assert any(row["stage"] == "admitNDFull" and row["status"] == "ok" for row in main_rows)
