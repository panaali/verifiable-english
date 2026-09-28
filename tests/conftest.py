"""Shared test setup for serial and xdist runs."""

import fcntl
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from ve import argument, bundle
from ve.surface import unambiguity

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def built_backends(tmp_path_factory, request):
    """Build once per run before any worker reads a native binary or Lean olean.

    All xdist workers share the parent of their per-worker base temp directory.
    The lock also makes an interrupted build retryable: the stamp is written only
    after all three build commands succeed.
    """
    base = tmp_path_factory.getbasetemp()
    shared = base.parent if hasattr(request.config, "workerinput") else base
    lock_path = shared / "native-build.lock"
    stamp = shared / "native-build.done"
    with lock_path.open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not stamp.exists():
            lake = shutil.which("lake")
            cargo = shutil.which("cargo")
            assert lake is not None, "lake is required for the complete test suite"
            assert cargo is not None, "cargo is required for the complete test suite"
            cargo_env = {**os.environ, "CARGO_HOME": str(ROOT / ".cargo-home"),
                         "CARGO_TARGET_DIR": str(ROOT / "rust/target")}
            commands = (
                ([lake, "build"], ROOT / "lean", None),
                ([cargo, "build", "-j", "2", "--locked", "--release",
                  "--manifest-path", str(ROOT / "rust/Cargo.toml")], ROOT, cargo_env),
                ([cargo, "build", "-j", "2", "--locked", "-p", "ve"], ROOT / "rust", cargo_env),
            )
            for command, cwd, env in commands:
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                        text=True, timeout=HANG_TIMEOUT)
                assert result.returncode == 0, result.stdout + result.stderr
            stamp.touch()

@pytest.fixture(autouse=True)
def generous_hang_guards(monkeypatch):
    # Deadline tests install their own deterministic clock and budget.
    # All production defaults and semantic work limits remain unchanged.
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1800)
    monkeypatch.setattr(argument, "LEAN_REPLAY_TIMEOUT", 1800)
    monkeypatch.setattr(bundle, "LEAN_REPLAY_TIMEOUT", 1800)
    monkeypatch.setenv("VE_CONFORMANCE_HANG_TIMEOUT", "1800")
