"""`tools/gate.py --rerun-failed`: rerun only the failed tests' files of a gate that failed on this tree.

Builders reran the full gate on a commit already gated (six of 18 gates in seven hours, most for one
load-sensitive test). A rerun takes the failed gate's record: on the same tree and toolchains, when every
failure was a test, only the files of its failed tests run, and the lean audit and native Rust tests are
taken from that gate. The record says so (`mode`, `rerun_failed`), and its status is `rerun-passed`, never
`passed`: the final evidence is still a clean full gate. Anything else runs the full gate.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
import sys

import pytest

import test_gate_integrity

from test_gate_integrity import pin_rust_binary
from tools import gate

BASELINE = ["tests/a.py::test_a", "tests/a.py::test_a2", "tests/b.py::test_b", "tests/c.py::test_c"]
FAILED = "tests/a.py::test_a"


class FakeGate:
    """The gate in a scratch root, its commands answered here: the suite's events are those of the tests
    the command names (all of BASELINE for `tests`), each failing when it is in `failing`."""

    def __init__(self, tmp_path, monkeypatch):
        root = tmp_path / "root"
        for binary in [root / "rust/target/release/ve", *(root / "lean/.lake/build/bin" / name
                                                          for name in gate.LEAN_BINARIES)]:
            binary.parent.mkdir(parents=True, exist_ok=True)
            binary.write_text("binary")
            binary.chmod(0o755)
        pin_rust_binary(root)
        (root / "rust/Cargo.lock").write_text("version = 4\n")
        policy = tmp_path / "policy.json"
        policy.write_text(json.dumps({"version": 1, "optional_tests": [], "deselected_tests": []}))
        collection = tmp_path / "collection.json"
        collection.write_text(json.dumps(BASELINE))
        self.output = tmp_path / "record.json"
        self.root, self.tree, self.failing, self.seen = root, "tree-1", {FAILED}, []
        self.trust = None  # the counts `trust_map.py --files` writes (None: trust_counts())
        self.toolchains = {"lean": "Lean (version 4.24.0)", "rustc": "rustc 1.90.0"}
        scratches = itertools.count()
        monkeypatch.setattr(gate, "ROOT", root)
        monkeypatch.setattr(gate, "POLICY", policy)
        monkeypatch.setattr(gate, "COLLECTION", collection)
        monkeypatch.setattr(gate, "REQUIRED_FAMILIES", ())
        # uv is linked from each gate's own scratch directory: its path differs on every run.
        monkeypatch.setattr(gate, "check_toolchains", lambda result, env: result["toolchains"].update(
            self.toolchains, paths={"uv": f"/tmp/ve-gate-{next(scratches)}/bin/uv", "lake": "/elan/bin/lake"}))
        monkeypatch.setattr(gate, "command", self.command)
        self.monkeypatch = monkeypatch

    def command(self, args, *, env, stage, cwd=None):
        self.seen.append((stage, [str(arg) for arg in args]))
        if self.trust is not False:  # False: trust_map.py wrote nothing
            test_gate_integrity.fake_trust(args, stage, self.trust)
        if stage == "commit":
            return "commit-1"
        if stage == "tree":
            return self.tree
        if stage == "Python environment":
            return str(self.root / ".venv")
        if stage == "native Rust tests":
            return "test result: ok. 2 passed; 0 failed; 0 ignored;"
        if stage in ("Python collection", "Python suite"):
            files = [str(arg) for arg in args if str(arg).startswith("tests/")]
            ids = [nodeid for nodeid in BASELINE if not files or nodeid.split("::")[0] in files]
            outcomes = {nodeid: {"outcome": "failed", "reason": "AssertionError"} if nodeid in self.failing
                        else {"outcome": "passed"} for nodeid in ids}
            Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps(
                {"collected": ids, "selected": ids, "deselected": [], "collection_reports": [],
                 "tests": outcomes if stage == "Python suite" else {}, "workers": {"gw0": ids}}))
            if stage == "Python suite" and self.failing & set(ids):
                raise RuntimeError("Python suite: exit 1")
        return ""

    def run(self, *flags):
        self.seen.clear()
        self.monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(self.output), *flags])
        code = gate.main()
        return code, json.loads(self.output.read_text())

    def stages(self):
        return [stage for stage, _ in self.seen]

    def pytest_targets(self):
        return [[arg for arg in args[args.index("not live") + 1:]]
                for stage, args in self.seen if stage in ("Python collection", "Python suite")]


@pytest.fixture
def fake(tmp_path, monkeypatch):
    return FakeGate(tmp_path, monkeypatch)


def test_a_rerun_runs_only_the_failed_tests_files_and_is_not_a_full_gate(fake):
    code, first = fake.run()
    assert (code, first["status"], first["mode"], first["tree_sha"]) == (1, "failed", "full", "tree-1")
    assert [f["nodeid"] for f in first["failures"] if f["stage"] == "pytest"] == [FAILED]
    assert fake.pytest_targets() == [["tests"], ["tests"]]
    fake.failing = set()  # the test passes alone (it failed under load)
    code, record = fake.run("--rerun-failed")
    assert (code, record["status"], record["mode"]) == (0, "rerun-passed", "rerun-failed")
    assert record["rerun_failed"] == {
        "previous": {"commit_sha": "commit-1", "tree_sha": "tree-1", "mode": "full", "status": "failed"},
        "tests": [FAILED], "files": ["tests/a.py"], "reused_stages": ["lean_audit", "cargo_test"],
        "outcomes": {FAILED: "passed"}}
    # Only the failed test's file ran; the audit and the native Rust tests were the failed gate's.
    assert fake.pytest_targets() == [["tests/a.py"], ["tests/a.py"]]
    assert record["counts"]["selected"] == 2 and record["failures"] == []
    assert "Lean audit" not in fake.stages() and "native Rust tests" not in fake.stages()
    assert {"Lean build", "Rust build", "Wire contract check"} <= set(fake.stages())
    assert record["stages"] == ["toolchains", "lean_build", "rust_build", "pytest"]
    # Never a full gate's evidence: the full gate is still required.
    assert record["status"] != "passed"
    code, full = fake.run()
    assert (code, full["status"], full["mode"]) == (0, "passed", "full") and "Lean audit" in fake.stages()


def test_a_rerun_that_fails_again_fails_and_can_itself_be_rerun(fake):
    fake.run()
    code, again = fake.run("--rerun-failed")
    assert (code, again["status"], again["rerun_failed"]["outcomes"]) == (1, "failed", {FAILED: "failed"})
    assert [f["nodeid"] for f in again["failures"] if f["stage"] == "pytest"] == [FAILED]
    fake.failing = set()
    code, record = fake.run("--rerun-failed")
    assert (code, record["status"]) == (0, "rerun-passed")
    assert record["rerun_failed"]["previous"]["mode"] == "rerun-failed"


def test_a_rerun_reads_the_record_it_is_given(fake, tmp_path):
    fake.run()
    kept = tmp_path / "kept.json"
    kept.write_text(fake.output.read_text())
    fake.output.write_text('{"status": "passed"}')
    fake.failing = set()
    code, record = fake.run("--rerun-failed", str(kept))
    assert (code, record["status"], record["rerun_failed"]["tests"]) == (0, "rerun-passed", [FAILED])


def _edit(fake, change):
    record = json.loads(fake.output.read_text())
    change(record)
    fake.output.write_text(json.dumps(record))


@pytest.mark.parametrize("change, refusal", [
    (lambda fake: setattr(fake, "tree", "tree-2"), "ran on tree 'tree-1', not 'tree-2'"),
    (lambda fake: fake.toolchains.update(lean="Lean (version 4.25.0)"), "other toolchains"),
    (lambda fake: fake.output.unlink(), "no previous gate record"),
    (lambda fake: fake.output.write_text("{"), "no previous gate record"),
    (lambda fake: _edit(fake, lambda r: r.update(status="passed")), "status is 'passed'"),
    (lambda fake: _edit(fake, lambda r: r.update(status="rerun-passed")), "status is 'rerun-passed'"),
    (lambda fake: _edit(fake, lambda r: r.update(dirty=True)), "clean worktree"),
    (lambda fake: _edit(fake, lambda r: r["stages"].remove("pytest")), "suite did not complete"),
    (lambda fake: _edit(fake, lambda r: r["failures"].append({"stage": "coverage", "reason": "baseline"})),
     "failed outside its tests"),
    (lambda fake: _edit(fake, lambda r: r["failures"].append({"stage": "skip policy", "nodeid": "tests/b.py::test_b",
                                                              "reason": "skipped"})), "failed outside its tests"),
    (lambda fake: _edit(fake, lambda r: r["failures"].append({"stage": "pytest", "nodeid": "../x.py::t",
                                                              "reason": "x"})), "failed outside its tests"),
    (lambda fake: _edit(fake, lambda r: r.update(failures=[f for f in r["failures"] if f["stage"] != "pytest"])),
     "names no failed test"),
], ids=["another tree", "other toolchains", "no record", "unreadable record", "passed", "rerun passed",
        "dirty", "suite incomplete", "coverage failure", "skip policy failure", "foreign node id",
        "no failed test"])
def test_anything_but_test_failures_on_this_tree_runs_the_full_gate(fake, change, refusal):
    fake.run()
    change(fake)
    fake.failing = set()
    code, record = fake.run("--rerun-failed")
    assert refusal in record["rerun_failed"]["refused"], record["rerun_failed"]
    assert (code, record["status"], record["mode"]) == (0, "passed", "full")
    assert fake.pytest_targets() == [["tests"], ["tests"]]
    assert "Lean audit" in fake.stages() and "native Rust tests" in fake.stages()


def test_a_full_gate_records_its_tree_and_mode(fake):
    fake.failing = set()
    code, record = fake.run()
    assert (code, record["status"], record["mode"], record["tree_sha"]) == (0, "passed", "full", "tree-1")
    assert "rerun_failed" not in record

