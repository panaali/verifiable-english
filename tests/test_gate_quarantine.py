"""Test speed B5: the gate never stops early, and the tracked quarantine (tools/test-quarantine.json).

A quarantined test still runs in the gate. When it fails there it runs once more, alone and serially:
passing alone, it no longer fails the gate and the record keeps both outcomes; failing again, it fails
the gate. The nightly (`--no-quarantine`) retries nothing, so every failure blocks it. An entry lives at
most seven days and names saved load evidence; an expired entry no longer applies.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from test_gate_rerun import BASELINE, FakeGate
from tools import gate, gate_collection, nested_pytest, quarantine

ROOT = Path(__file__).resolve().parents[1]
HELD = "tests/b.py::test_b"
OTHER = "tests/c.py::test_c"
DAY = datetime.date(2026, 10, 12)


def entry(test=HELD, **fields):
    return {"test": test, "evidence": "evidence.json", "owner": "orchestrator", "added": "2026-10-10",
            "expires": "2026-10-17", "reason": "fails under load", **fields}


class QuarantineGate(FakeGate):
    """FakeGate whose quarantine retry runs the node IDs it names: each fails alone when in `failing_alone`."""

    def __init__(self, tmp_path, monkeypatch):
        super().__init__(tmp_path, monkeypatch)
        self.failing, self.failing_alone = {HELD}, set()
        self.file = tmp_path / "quarantine.json"
        (tmp_path / "evidence.json").write_text(json.dumps({"test": HELD}))
        self.write([entry()])
        monkeypatch.setattr(quarantine, "PATH", self.file)
        monkeypatch.setattr(quarantine, "ROOT", tmp_path)
        monkeypatch.setattr(quarantine, "today", lambda: self.day)
        self.day = DAY

    def write(self, entries, version=1):
        self.file.write_text(json.dumps({"version": version, "entries": entries}))

    def command(self, args, *, env, stage, cwd=None):
        if stage != "Quarantine retry":
            return super().command(args, env=env, stage=stage, cwd=cwd)
        self.seen.append((stage, [str(arg) for arg in args]))
        ids = [str(arg) for arg in args if "::" in str(arg)]
        Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps({"tests": {
            nodeid: {"outcome": "failed" if nodeid in self.failing_alone else "passed"} for nodeid in ids}}))
        if self.failing_alone & set(ids):
            raise RuntimeError(gate.exit_reason(stage, 1))
        return ""

    def retries(self):
        return [args for stage, args in self.seen if stage == "Quarantine retry"]


@pytest.fixture
def fake(tmp_path, monkeypatch):
    return QuarantineGate(tmp_path, monkeypatch)


def test_a_quarantined_failure_that_passes_alone_does_not_fail_the_gate(fake):
    code, record = fake.run()
    assert (code, record["status"], record["failures"]) == (0, "passed", [])
    assert record["counts"]["failed"] == 0 and record["counts"]["passed"] == len(BASELINE)
    assert record["quarantine"] == {
        "enabled": True, "day": "2026-10-12", "active": [HELD], "expired": [],
        "retried": {HELD: {"suite": "failed", "alone": "passed", "owner": "orchestrator",
                           "expires": "2026-10-17", "evidence": "evidence.json"}}}
    # Only the quarantined test, serially: no xdist, every other gate option kept.
    [retry] = fake.retries()
    assert retry[retry.index("not live") + 1:] == [HELD]
    assert "-n" not in retry and "xdist" not in retry and "tools.gate_pytest" in retry


def test_a_quarantined_failure_that_fails_alone_fails_the_gate(fake):
    fake.failing_alone = {HELD}
    code, record = fake.run()
    assert (code, record["status"]) == (1, "failed")
    assert [f["nodeid"] for f in record["failures"] if f["stage"] == "pytest"] == [HELD]
    assert {"stage": "pytest command", "reason": "Python suite: exit 1"} in record["failures"]
    assert record["quarantine"]["retried"][HELD]["alone"] == "failed" and record["counts"]["failed"] == 1


def test_a_retry_without_a_result_fails_the_gate(fake, monkeypatch):
    monkeypatch.setattr(fake, "command", lambda args, *, env, stage, cwd=None: "" if stage == "Quarantine retry"
                        else QuarantineGate.command(fake, args, env=env, stage=stage, cwd=cwd))
    monkeypatch.setattr(gate, "command", fake.command)
    code, record = fake.run()
    assert (code, record["status"], record["quarantine"]["retried"][HELD]["alone"]) == (1, "failed", "no result")


def test_another_failure_still_fails_the_gate_and_is_never_retried(fake):
    fake.failing = {HELD, OTHER}
    code, record = fake.run()
    assert (code, record["status"]) == (1, "failed")
    assert [f["nodeid"] for f in record["failures"] if f["stage"] == "pytest"] == [OTHER]
    assert {"stage": "pytest command", "reason": "Python suite: exit 1"} in record["failures"]
    [retry] = fake.retries()
    assert retry[retry.index("not live") + 1:] == [HELD]


def test_the_nightly_retries_nothing(fake):
    code, record = fake.run("--no-quarantine")
    assert (code, record["status"], fake.retries()) == (1, "failed", [])
    assert record["quarantine"] == {"enabled": False, "active": [], "expired": [], "retried": {}}
    assert [f["nodeid"] for f in record["failures"] if f["stage"] == "pytest"] == [HELD]


@pytest.mark.parametrize("day, applies", [(datetime.date(2026, 10, 9), False), (datetime.date(2026, 10, 10), True),
                                          (datetime.date(2026, 10, 17), True), (datetime.date(2026, 10, 18), False)],
                         ids=["before added", "added", "expires", "after expiry"])
def test_an_entry_applies_from_its_added_day_to_its_expiry(fake, day, applies):
    fake.day = day
    code, record = fake.run()
    assert (code, bool(fake.retries())) == ((0, True) if applies else (1, False))
    assert record["quarantine"]["expired"] == ([] if day <= datetime.date(2026, 10, 17) else [HELD])


def test_a_malformed_quarantine_fails_the_gate(fake):
    fake.write([entry(expires="2026-10-18")])
    code, record = fake.run()
    assert (code, record["status"], fake.retries()) == (1, "failed", [])
    assert any(f["stage"] == "gate" and "within 7 days" in f["reason"] for f in record["failures"])


def test_a_passing_suite_retries_nothing(fake):
    fake.failing = set()
    code, record = fake.run()
    assert (code, record["status"], fake.retries(), record["quarantine"]["retried"]) == (0, "passed", [], {})


# --- the quarantine file ---

def test_the_tracked_quarantine_is_valid_and_names_collected_tests():
    entries = quarantine.load()
    collected = set(gate_collection.collect(prebuilt=True))
    for item in entries:
        assert item["test"] in collected, item["test"]
        assert json.loads((ROOT / item["evidence"]).read_text())["test"] == item["test"]
        assert subprocess.run(["git", "ls-files", "--error-unmatch", item["evidence"]], cwd=ROOT,
                              capture_output=True).returncode == 0, f"{item['evidence']} is not tracked"


BROKEN = [
    ("missing field", lambda d: d["entries"][0].pop("owner"), "exactly the fields"),
    ("extra field", lambda d: d["entries"][0].update(note="x"), "exactly the fields"),
    ("empty owner", lambda d: d["entries"][0].update(owner=" "), "owner is not a non-empty string"),
    ("owner not a string", lambda d: d["entries"][0].update(owner=7), "owner is not a non-empty string"),
    ("not a node id", lambda d: d["entries"][0].update(test="tests/b.py"), "not a test node ID"),
    ("outside tests", lambda d: d["entries"][0].update(test="tools/x.py::t"), "not a test node ID"),
    ("bad day", lambda d: d["entries"][0].update(added="10/10/2026"), "not a YYYY-MM-DD day"),
    ("eight days", lambda d: d["entries"][0].update(expires="2026-10-18"), "within 7 days"),
    ("expires first", lambda d: d["entries"][0].update(expires="2026-10-09"), "within 7 days"),
    ("twice", lambda d: d["entries"].append(copy.deepcopy(d["entries"][0])), "quarantined twice"),
    ("absolute evidence", lambda d: d["entries"][0].update(evidence="/etc/passwd"), "not a path in the repository"),
    ("evidence outside", lambda d: d["entries"][0].update(evidence="../x.json"), "not a path in the repository"),
    ("missing evidence", lambda d: d["entries"][0].update(evidence="none.json"), "evidence none.json"),
    ("evidence of another test", lambda d: d["entries"][0].update(test=OTHER), "is not about"),
    ("version 2", lambda d: d.update(version=2), "version 2"),
    ("version true", lambda d: d.update(version=True), "version True"),
    ("entries not a list", lambda d: d.update(entries={}), "'entries' is not a list"),
    ("extra key", lambda d: d.update(note="x"), "exactly 'version' and 'entries'"),
]


@pytest.mark.parametrize("change, message", [(change, message) for _, change, message in BROKEN],
                         ids=[name for name, _, _ in BROKEN])
def test_a_malformed_entry_is_refused(tmp_path, change, message):
    (tmp_path / "evidence.json").write_text(json.dumps({"test": HELD}))
    data = {"version": 1, "entries": [entry()]}
    path = tmp_path / "quarantine.json"
    path.write_text(json.dumps(data))
    assert [item["test"] for item in quarantine.load(path, tmp_path)] == [HELD]
    change(data)
    path.write_text(json.dumps(data))
    with pytest.raises(quarantine.QuarantineError, match=message):
        quarantine.load(path, tmp_path)


def test_an_unreadable_quarantine_is_refused(tmp_path):
    with pytest.raises(quarantine.QuarantineError):
        quarantine.load(tmp_path / "missing.json", tmp_path)
    (tmp_path / "bad.json").write_text("{")
    with pytest.raises(quarantine.QuarantineError):
        quarantine.load(tmp_path / "bad.json", tmp_path)


# --- the gate's pytest never stops early ---

FAILING = {"tests/test_one.py": "def test_one():\n    assert False\n",
           "tests/test_two.py": "def test_two():\n    assert False\n",
           "pyproject.toml": "[tool.pytest.ini_options]\naddopts = \"--maxfail=1\"\n"}


def project(tmp_path):
    for name, text in FAILING.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    return tmp_path


def gate_pytest(root, arguments, **settings):
    environment = nested_pytest.environment({**os.environ, "PYTEST_ADDOPTS": "-x"}, PYTHONPATH=str(ROOT),
                                            VE_GATE_PYTEST_RESULT=str(root / "events.json"), **settings)
    return subprocess.run(nested_pytest.command(arguments, python=[sys.executable]), cwd=root, env=environment,
                          text=True, capture_output=True, timeout=HANG_TIMEOUT)


def test_the_gates_pytest_runs_every_test_whatever_the_project_or_shell_asks(tmp_path):
    """The project's addopts ask for --maxfail=1 and the shell for -x: the gate's options replace the first
    and its environment drops the second, so both failing tests have a result."""
    root = project(tmp_path)
    done = gate_pytest(root, gate.pytest_args())
    assert done.returncode == 1, done.stdout
    tests = json.loads((root / "events.json").read_text())["tests"]
    assert {nodeid: row["outcome"] for nodeid, row in tests.items()} == {
        "tests/test_one.py::test_one": "failed", "tests/test_two.py::test_two": "failed"}


@pytest.mark.parametrize("option", ["--maxfail=1", "-x", "--exitfirst", "--sw", "--stepwise-skip"])
def test_the_gates_plugin_refuses_to_stop_early(tmp_path, option):
    root = project(tmp_path)
    done = gate_pytest(root, [*gate.PYTEST_ARGS[:-1], option, "tests"])
    assert done.returncode == 4, done.stdout + done.stderr
    assert "the gate runs every test" in done.stdout + done.stderr


def test_the_retry_command_is_the_gates_pytest_over_the_node_ids():
    command = gate.retry_command(["python"], [HELD, OTHER])
    assert command == nested_pytest.command([*gate.PYTEST_ARGS[:-1], HELD, OTHER], python=["python"])
    assert [argument for argument in command if "::" in argument] == [HELD, OTHER]
