"""Stage 3 runs: the completeness of a run (docs/spec/mig3.md 2.8), fixtures L8, L15, L16,
and one run through tools/shadow_run.py."""
from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import signal
import subprocess
import sys

import pytest

from tools import shadow_run

ROOT = Path(__file__).resolve().parents[1]
ENTRY = {"id": "baseline", "expected_exit": 0, "min_cases": 5, "min_compared": 2}
LOCK = {"ve_service": ["svc"], "rust_jsonl": ["rst"]}


def make_run(directory: Path, *, corpus="baseline", tallies=None, records=None, stderr="", **meta):
    directory.mkdir()
    data = {"run": "r", "corpus": corpus, "commit": "c" * 40, "trigger": "nightly",
            "started": "2026-10-07T00:05:00Z", "finished": "2026-10-07T03:00:00Z", "exit": 0, "cases": 10,
            "builds": {"ve_service": "svc", "rust_jsonl": "rst"},
            "seed": 20261007 if corpus == "fuzz-nightly" else None, "webapp_commit": None,
            "stderr_faults": stderr.count("ve shadow:"), "clean": {"started": True, "finished": True}, **meta}
    (directory / "run.json").write_text(json.dumps(data))
    (directory / "stderr.txt").write_text(stderr)
    for worker, data in (tallies if tallies is not None else {"1-n": tally()}).items():
        (directory / f"tally-{worker}.json").write_text(json.dumps(data))
    for worker, text in (records or {}).items():
        (directory / f"records-{worker}.jsonl").write_text(text)
    return directory


def tally(final=True, **counts):
    cell = {name: 0 for name in shadow_run.OP_COUNTS}
    cell.update({"compared": 3, "agree": 3})
    cell.update(counts)
    cell["uncompared"] = {}
    return {"run": "r", "pid": 1, "nonce": "n", "started": "2026-10-07T00:05:00Z", "final": final, "calls": 3,
            "ops": {"evaluate": cell}}


def divergence():
    return json.dumps({"kind": "divergence", "op": "evaluate", "input_digest": None, "python": 1, "lean": 2,
                       "rust": None, "class": ["verdict"], "python_ms": 1, "backend_ms": 1, "run": None,
                       "test": None, "input": None}) + "\n"


def problems(directory, entry=ENTRY, **options):
    return shadow_run.run_problems(directory, entry, LOCK, **options)


def test_a_complete_run(tmp_path):
    assert problems(make_run(tmp_path / "run")) == []


@pytest.mark.parametrize("change,named", [
    ({"exit": 1}, "the exit status is 1, not 0"),
    ({"builds": {"ve_service": "other", "rust_jsonl": "rst"}}, "the ve_service binary is not pinned in lean/checkers.lock"),
    ({"records": {"1-n": divergence()[:-20]}, "tallies": {"1-n": tally(zero_tolerance=1, agree=2)}},
     "the file records-1-n.jsonl is malformed"),
    ({"tallies": {"1-n": tally(final=False)}}, "the worker 1-n did not finalize its tally"),
    ({"records": {"1-n": divergence()}, "tallies": {"1-n": tally(zero_tolerance=1, recorded_only=1, agree=1)}},
     "the tally of 1-n does not match its records"),
    ({"records": {"2-m": divergence()}}, "the tally of 2-m does not match its records"),
    ({"tallies": {"1-n": tally(recorder_faults=1)}}, "1 recorder faults (0 on standard error)"),
    ({"stderr": "ve shadow: cannot write tally: no space\n"}, "1 recorder faults (1 on standard error)"),
    ({"cases": 4}, "4 cases, below the floor of 5"),
    ({"tallies": {"1-n": tally(compared=1, agree=1)}}, "1 compared calls, below the floor of 2"),
    ({"corpus": "fuzz-nightly", "seed": 20261006}, "the seed is 20261006, not the seed of 2026-10-07"),
    ({"finished": None}, "the run has not finished"),
    ({"clean": {"started": True, "finished": False}}, f"the checkout was not clean at {'c' * 40}"),
])
def test_l8_each_condition_is_named(tmp_path, change, named):
    directory = make_run(tmp_path / "run", **change)
    found = problems(directory)
    assert named in found, found


def test_a_calibration_run_is_not_held_to_the_floors(tmp_path):
    directory = make_run(tmp_path / "run", cases=1)
    assert problems(directory) == ["1 cases, below the floor of 5"]
    assert problems(directory, calibration=True) == []
    assert problems(directory, entry={**ENTRY, "min_cases": None, "min_compared": None}) == [
        "the corpus baseline has no floors: it is not calibrated"]


WORKER = """
import os, sys
sys.path.insert(0, {root!r})
from ve.backends.dispatch import execute
mode = {mode!r}
if mode == "failing":
    import pathlib
    def refuse(*args, **kwargs):
        raise OSError("no space left on device")
    pathlib.Path.write_text = refuse
    pathlib.Path.open = refuse
for index in range({calls}):
    agree = mode == "agree"
    result = execute("evaluate", {{"i": index}}, lambda: {{"value": True}}, lean=lambda: {{"value": agree}})
    assert result == {{"value": True}}
if mode == "agree":
    import signal
    os.kill(os.getpid(), signal.SIGKILL)
"""


def _worker(directory: Path, mode: str, calls: int) -> subprocess.CompletedProcess:
    environment = {**os.environ, "VE_AUTHORITY": "shadow", "VE_SHADOW_DIR": str(directory), "VE_SHADOW_RUN": "r"}
    for name in ("VE_SHADOW_LOG", "VE_AUTHORITY_OVERRIDES"):
        environment.pop(name, None)
    code = WORKER.format(root=str(ROOT), mode=mode, calls=calls)
    return subprocess.run([sys.executable, "-c", code], env=environment, capture_output=True, text=True, timeout=600)


def _three_workers(tmp_path, third: str):
    directory = tmp_path / "run"
    directory.mkdir()
    stderr = ""
    for mode, calls in (("differ", 3), ("differ", 3), (third, 2)):
        completed = _worker(directory, mode, calls)
        stderr += completed.stderr
        if mode != "agree":
            assert completed.returncode == 0, completed.stderr
    meta = {"run": "r", "corpus": "baseline", "commit": "c" * 40, "trigger": "nightly",
            "started": "2026-10-07T00:05:00Z", "finished": "2026-10-07T03:00:00Z", "exit": 0, "cases": 10,
            "builds": {"ve_service": "svc", "rust_jsonl": "rst"}, "seed": None, "webapp_commit": None,
            "stderr_faults": sum(line.startswith("ve shadow:") for line in stderr.splitlines()),
            "clean": {"started": True, "finished": True}}
    (directory / "run.json").write_text(json.dumps(meta))
    (directory / "stderr.txt").write_text(stderr)
    return directory, stderr


def test_l15_a_worker_that_did_not_finalize_fails_the_run(tmp_path):
    directory, _ = _three_workers(tmp_path, "agree")
    tallies = shadow_run.read_run(directory)["tallies"]
    unfinished = [worker for worker, data in tallies.items() if not data["final"]]
    assert len(tallies) == 3 and len(unfinished) == 1
    assert len(list(directory.glob("records-*.jsonl"))) == 2
    found = problems(directory)
    assert found == [f"the worker {unfinished[0]} did not finalize its tally"]


def test_l16_a_worker_whose_writes_all_fail_fails_the_run(tmp_path):
    directory, stderr = _three_workers(tmp_path, "failing")
    lines = [line for line in stderr.splitlines() if line.startswith("ve shadow:")]
    assert any(line.startswith("ve shadow: cannot write tally: ") for line in lines)
    assert any(line.startswith("ve shadow: cannot write records: ") for line in lines)
    assert len(shadow_run.read_run(directory)["tallies"]) == 2
    found = problems(directory)
    assert any(problem.endswith(" on standard error)") for problem in found), found


TOY = """
import json, os, sys
sys.path.insert(0, {root!r})
from ve.backends.dispatch import execute
for index in range(3):
    execute("evaluate", {{"i": index}}, lambda: {{"value": True}}, lean=lambda: {{"value": True}})
print("toy corpus ran", file=sys.stderr)
open(os.environ["VE_SHADOW_CASES"], "w").write(json.dumps({{"cases": 3}}))
sys.exit(int(sys.argv[1]))
"""


@pytest.mark.parametrize("status", [0, 3])
def test_a_run_through_the_tool(tmp_path, status):
    script = tmp_path / "toy.py"
    script.write_text(TOY.format(root=str(ROOT)))
    registry = tmp_path / "corpora.json"
    registry.write_text(json.dumps([{"id": "toy", "plan": "toy", "command": ["{python}", str(script), str(status)],
                                     "expected_exit": 0, "min_cases": 3, "min_compared": 3,
                                     "calibration": "cal", "merge": False}]))
    out = io.StringIO()
    with redirect_stdout(out):
        returned = shadow_run.main(["--corpus", "toy", "--out", str(tmp_path / "run"), "--registry", str(registry)])
    assert returned == status
    directory = tmp_path / "run"
    meta = json.loads((directory / "run.json").read_text())
    assert meta["exit"] == status and meta["cases"] == 3 and meta["finished"] and meta["trigger"] == "manual"
    assert meta["run"].startswith(f"toy-{meta['commit'][:12]}-") and meta["stderr_faults"] == 0
    assert "toy corpus ran" in (directory / "stderr.txt").read_text()
    assert sorted(path.name.split("-")[0] for path in directory.iterdir()) == ["run.json", "stderr.txt", "tally"]
    [tally_path] = directory.glob("tally-*.json")
    data = json.loads(tally_path.read_text())
    assert data["final"] and data["run"] == meta["run"] and data["ops"]["evaluate"]["compared"] == 3
    printed = out.getvalue()
    assert (f"run {meta['run']} is not complete: the exit status is 3, not 0" in printed) is (status == 3)
