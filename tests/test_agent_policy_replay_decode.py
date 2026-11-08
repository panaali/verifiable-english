"""Agent-policy use case: a replay's raw output that is not UTF-8, or JSON nested too
deeply to parse, is refused with `CheckerUnavailable`, never a traceback.

Fake binaries in `tmp_path` stand in for the Rust `ve` and Lean `ve_conformance`.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "agent-policy"
sys.path.insert(0, str(HERE))

import check  # noqa: E402
from ve.errors import CheckerUnavailable  # noqa: E402

DEEP = 500_000
BAD_OUTPUT = {
    "not UTF-8": (b'[{"id": "0", "status": "Satisfied\xff"}]', "output is not UTF-8"),
    "too deep": (b"[" * DEEP + b"]" * DEEP, "output nested too deeply to read"),
}
ENVIRONMENT = {"language": "ve.core@0.2", "profiles": ["relational-fol@0"],
               "spec_revision": "ve-v0.2-expand2-2026-09-25",
               "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}}
MODEL_CASE = {"environment": ENVIRONMENT, "ast": [["top"]], "value": True,
              "model": {"complete": True, "domains": {}, "relations": {}, "constants": {}}}


def _fake_binary(tmp_path, output):
    """An executable that reads its request and writes `output` as raw bytes."""
    (tmp_path / "output.bin").write_bytes(output)
    binary = tmp_path / "fake"
    binary.write_text(f"#!{sys.executable}\nimport sys\nsys.stdin.buffer.read()\n"
                      f"sys.stdout.buffer.write(open({str(tmp_path / 'output.bin')!r}, 'rb').read())\n")
    binary.chmod(0o755)
    return binary


@pytest.mark.parametrize("kind", sorted(BAD_OUTPUT))
def test_rust_values_refuses_bad_output(kind):
    output, message = BAD_OUTPUT[kind]
    with pytest.raises(CheckerUnavailable, match=f"^Rust replay: {message}"):
        check.rust_values(output, ["0"])


@pytest.mark.parametrize("kind", sorted(BAD_OUTPUT))
def test_rust_replay_refuses_bad_output_of_the_binary(tmp_path, monkeypatch, kind):
    output, message = BAD_OUTPUT[kind]
    monkeypatch.setattr(check, "RUST", _fake_binary(tmp_path, output))
    with pytest.raises(CheckerUnavailable, match=f"^Rust replay: {message}"):
        check.replay_rust({"rust": [MODEL_CASE]})


@pytest.mark.parametrize("kind", sorted(BAD_OUTPUT))
def test_lean_replay_refuses_bad_output_of_the_route(tmp_path, monkeypatch, kind):
    output, message = BAD_OUTPUT[kind]
    monkeypatch.setattr(check, "LEAN_ROUTE", _fake_binary(tmp_path, output))
    with pytest.raises(CheckerUnavailable, match=f"^Lean replay: {message}"):
        check.replay_lean({"lean": [{"kind": "certificate", "norm": False}]})


@pytest.mark.parametrize("kind", sorted(BAD_OUTPUT))
def test_the_harness_reports_the_refusal_and_exits_1_without_a_traceback(tmp_path, kind):
    output, message = BAD_OUTPUT[kind]
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"lean": [], "rust": [MODEL_CASE]}))
    driver = ("import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); import check; "
              "check.RUST, check.LEAN_ROUTE, check.EVIDENCE = map(Path, sys.argv[2:5]); check.cli(['replay'])")
    done = subprocess.run([sys.executable, "-c", driver, str(HERE), str(_fake_binary(tmp_path, output)),
                           str(tmp_path / "no-lean-route"), str(evidence)],
                          capture_output=True, text=True, timeout=HANG_TIMEOUT, cwd=tmp_path,
                          env={**os.environ, "AGENT_POLICY_WORKERS": "1"})
    assert done.returncode == 1
    assert done.stderr.startswith(f"CheckerUnavailable: Rust replay: {message}")
    assert "Traceback" not in done.stderr
