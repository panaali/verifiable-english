"""Regressions for verification-gate accounting, isolation, and run identity."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from tools import gate


def empty_result():
    return {"counts": {}, "failures": [], "skips": []}


def events():
    return {"collected": ["tests/a.py::test_a", "tests/b.py::test_b"],
            "selected": ["tests/a.py::test_a", "tests/b.py::test_b"],
            "deselected": [], "collection_reports": [],
            "tests": {"tests/a.py::test_a": {"outcome": "passed"},
                      "tests/b.py::test_b": {"outcome": "passed"}}}


@pytest.mark.parametrize("change,reason", [
    (lambda e: e["collected"].pop(), "baseline"),
    (lambda e: e["selected"].pop(), "without a deselection report"),
    (lambda e: e["collection_reports"].append(
        {"nodeid": "tests/c.py", "outcome": "skipped", "reason": "importorskip"}), "collection"),
])
def test_gate_rejects_missing_tests_and_module_skips(change, reason):
    result = empty_result()
    observed = events()
    change(observed)
    gate.interpret_pytest(result, observed, {"optional_tests": [], "deselected_tests": []},
                          events()["collected"])
    assert reason in str(result["failures"])


@pytest.mark.parametrize("body,conftest", [
    ("import pytest\npytest.skip('module unavailable', allow_module_level=True)\n", ""),
    ("import pytest\npytest.importorskip('ve_gate_absent_test_backend')\n", ""),
    ("def test_first(): pass\ndef test_second(): pass\n",
     "def pytest_collection_modifyitems(items):\n    items[:] = items[:1]\n"),
])
def test_pytest_plugin_observes_collection_bypasses(tmp_path, body, conftest):
    (tmp_path / "test_sample.py").write_text(body)
    if conftest:
        (tmp_path / "conftest.py").write_text(conftest)
    output = tmp_path / "events.json"
    env = {**os.environ, "VE_GATE_PYTEST_RESULT": str(output),
           "PYTHONPATH": str(gate.ROOT)}
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p",
                          "tools.gate_pytest", "-o", "addopts=", str(tmp_path)],
                         cwd=gate.ROOT, env=env, capture_output=True, text=True)
    assert run.returncode in (0, 5), run.stdout + run.stderr
    observed = json.loads(output.read_text())
    if conftest:
        assert len(observed["collected"]) == 2
        assert len(observed["selected"]) == 1
        assert not observed["deselected"]
    else:
        assert observed["collection_reports"][0]["outcome"] == "skipped"


def test_gate_environment_discards_test_and_cargo_overrides(monkeypatch):
    for name, value in {"PYTEST_ADDOPTS": "--ignore=tests/test_lean_conformance.py",
                        "PYTEST_PLUGINS": "drop_tests", "CARGO_TARGET_DIR": "/tmp/stale",
                        "CARGO_BUILD_TARGET": "other-target", "RUSTFLAGS": "--cfg fake",
                        "RUSTC": "/tmp/fake-rustc", "RUSTC_WRAPPER": "/tmp/wrapper",
                        "RUSTC_WORKSPACE_WRAPPER": "/tmp/wrapper", "RUSTDOC": "/tmp/fake-rustdoc",
                        "GIT_DIR": "/tmp/fake-git", "GIT_WORK_TREE": "/tmp/fake-worktree",
                        "GIT_INDEX_FILE": "/tmp/fake-index", "GIT_CONFIG_GLOBAL": "/tmp/fake-config",
                        "PYTHONPATH": "/tmp/fake-tools", "PYTHONHOME": "/tmp/fake-python",
                        "UV_PYTHON": "/tmp/fake-python"}.items():
        monkeypatch.setenv(name, value)
    env = gate.gate_environment()
    for name in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "CARGO_TARGET_DIR", "CARGO_BUILD_TARGET",
                 "RUSTFLAGS", "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "RUSTDOC",
                 "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG_GLOBAL",
                 "PYTHONPATH", "PYTHONHOME", "UV_PYTHON"):
        assert name not in env
    assert env["CARGO_HOME"] == str(gate.ROOT / ".cargo-home")
    assert env["PYTHONNOUSERSITE"] == "1"


def test_gate_environment_uses_real_repository_and_recorder(tmp_path, monkeypatch):
    fake_tools = tmp_path / "tools"
    fake_tools.mkdir()
    (fake_tools / "__init__.py").write_text("")
    (fake_tools / "gate_pytest.py").write_text("raise RuntimeError('fake recorder loaded')\n")
    marker = tmp_path / "sitecustomize-loaded"
    (tmp_path / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "absent-git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "fake-index"))
    env = gate.gate_environment()
    sha, _ = gate.source_identity(env)
    assert sha == subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=gate.ROOT,
                                           env=env, text=True).strip()
    run = subprocess.run([sys.executable, "-c", "from tools import gate_pytest; "
                          "print(gate_pytest.__file__)"], cwd=gate.ROOT, env=env,
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == str(gate.ROOT / "tools/gate_pytest.py")
    assert not marker.exists()


def test_gate_rejects_untracked_source_before_build(tmp_path, monkeypatch):
    output = tmp_path / "record.json"
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])
    seen = []

    def fake_command(args, *, env, stage, cwd=None):
        seen.append(stage)
        if stage == "commit":
            return "old"
        assert stage == "worktree status"
        assert "--untracked-files=all" in args
        return "?? tests/conftest.py"

    monkeypatch.setattr(gate, "command", fake_command)
    assert gate.main() == 1
    assert seen == ["commit", "worktree status"]
    assert json.loads(output.read_text())["dirty"] is True


def test_terminated_gate_cannot_leave_old_pass_record(tmp_path):
    output = tmp_path / "record.json"
    output.write_text('{"status":"passed"}')
    script = ("import sys, time\nfrom tools import gate\n"
              "gate.command = lambda *args, **kwargs: time.sleep(30)\n"
              "sys.argv = ['gate.py', '--output', sys.argv[1]]\n"
              "gate.main()\n")
    process = subprocess.Popen([sys.executable, "-c", script, str(output)],
                               cwd=gate.ROOT, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if json.loads(output.read_text()).get("status") == "failed":
                break
            time.sleep(0.02)
        else:
            pytest.fail("gate did not reset the record before work")
    finally:
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=5)
    assert json.loads(output.read_text())["status"] == "failed"


@pytest.mark.parametrize("interruption", [KeyboardInterrupt, TypeError, AttributeError])
def test_interrupted_gate_cannot_record_pass(tmp_path, monkeypatch, interruption):
    output = tmp_path / "record.json"
    output.write_text('{"status":"passed"}')
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"version": 1}))
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(["tests/a.py::test_a"]))
    monkeypatch.setattr(gate, "POLICY", policy)
    monkeypatch.setattr(gate, "COLLECTION", collection)
    monkeypatch.setattr(gate, "check_toolchains", lambda result, env: None)
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])

    def fake_command(args, *, env, stage, cwd=None):
        if stage == "commit":
            return "unchanged"
        if stage == "worktree status":
            return ""
        if stage == "Lean build":
            raise interruption("interrupted")
        return ""

    monkeypatch.setattr(gate, "command", fake_command)
    with pytest.raises(interruption):
        gate.main()
    record = json.loads(output.read_text())
    assert record["status"] == "failed"
    assert record["stages"] == ["toolchains"]


@pytest.mark.parametrize("change_head,change_worktree", [(False, False), (True, False),
                                                         (False, True)])
def test_gate_resets_record_uses_own_binary_and_checks_source_at_end(
        tmp_path, monkeypatch, change_head, change_worktree):
    target = "x86_64-unknown-linux-gnu"
    rust_binary = tmp_path / "rust/target" / target / "release/ve"
    rust_binary.parent.mkdir(parents=True)
    rust_binary.write_text("binary")
    for name in gate.LEAN_BINARIES:
        binary = tmp_path / "lean/.lake/build/bin" / name
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_text("binary")
        binary.chmod(0o755)
    rust_binary.chmod(0o755)
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"version": 1, "optional_tests": [], "deselected_tests": []}))
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(events()["collected"]))
    output = tmp_path / "record.json"
    output.write_text('{"status":"passed"}')
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "POLICY", policy)
    monkeypatch.setattr(gate, "COLLECTION", collection)
    monkeypatch.setattr(gate, "REQUIRED_FAMILIES", ())
    monkeypatch.setattr(gate, "check_toolchains", lambda result, env: None)
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])
    sha_calls = 0
    seen = []

    def fake_command(args, *, env, stage, cwd=None):
        nonlocal sha_calls
        seen.append((args, dict(env), stage))
        if stage == "commit":
            sha_calls += 1
            assert json.loads(output.read_text())["status"] == "failed"
            return "new" if change_head and sha_calls == 2 else "old"
        if stage == "worktree status":
            assert "--untracked-files=all" in args
            return "?? tests/conftest.py" if change_worktree and sha_calls == 2 else ""
        if stage == "Rust host":
            return f"host: {target}"
        if stage == "native Rust tests":
            return "test result: ok. 2 passed; 0 failed; 0 ignored;"
        if stage == "Python suite":
            Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps(events()))
        return ""

    monkeypatch.setattr(gate, "command", fake_command)
    code = gate.main()
    record = json.loads(output.read_text())
    assert code == int(change_head or change_worktree)
    assert record["status"] == ("failed" if code else "passed")
    assert "lean_audit" in record["stages"]
    cargo = [row for row in seen if row[2] in ("Rust build", "native Rust tests")]
    assert len(cargo) == 2
    assert all("--target-dir" in row[0] and target in row[0] for row in cargo)
    pytest_env = next(row[1] for row in seen if row[2] == "Python suite")
    assert pytest_env["VE_RUST_BINARY"] == str(rust_binary)
    assert [row[2] for row in seen].count("commit") == 2
