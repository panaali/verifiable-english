"""Shared test setup for serial and xdist runs."""

import fcntl
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

import pytest

from subprocesses import HANG_TIMEOUT
from ve import argument, bundle
from ve.surface import unambiguity

ROOT = Path(__file__).resolve().parents[1]


def native_lock_path(root=ROOT):
    """One lock for every pytest invocation using this checkout's build outputs."""
    return root.resolve() / "rust/target/.ve-native-build.lock"


def _stop_build_group(process):
    # The build driver may have spawned compilers that still write artifacts.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.communicate()
    # A dead group leader does not imply its grandchildren have stopped.
    # Reap is unavailable for grandchildren, so inspect the Linux process group.
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        living = False
        for proc in Path("/proc").iterdir():
            if not proc.name.isdecimal():
                continue
            try:
                fields = (proc / "stat").read_text().rsplit(")", 1)[1].split()
                if int(fields[2]) == process.pid and fields[0] not in ("Z", "X"):
                    living = True
                    break
            except (FileNotFoundError, ProcessLookupError, PermissionError, IndexError):
                continue
        if not living:
            return
        time.sleep(0.01)
    raise RuntimeError(f"build process group {process.pid} did not stop")


def _run_build(command, cwd, env, lock, timeout=HANG_TIMEOUT):
    # The child inherits the lock. If pytest is killed, the builder keeps the
    # exclusive lock until it and its descendants finish.
    process = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, start_new_session=True,
                               pass_fds=(lock.fileno(),))
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        _stop_build_group(process)
        raise TimeoutError(f"build timed out: {command}") from exc
    if process.returncode != 0:
        _stop_build_group(process)
        raise AssertionError(stdout + stderr)


def _build_backends(lock):
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
        _run_build(command, cwd, env, lock)


def pytest_sessionstart(session):
    """Build once, then hold a read lock until all this process's tests end."""
    lock_path = native_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = lock_path.open("a+")
    try:
        if hasattr(session.config, "workerinput"):
            fcntl.flock(lock, fcntl.LOCK_SH)
        else:
            fcntl.flock(lock, fcntl.LOCK_EX)
            _build_backends(lock)
            fcntl.flock(lock, fcntl.LOCK_SH)
    except BaseException:
        lock.close()
        raise
    session.config._ve_native_lock = lock


def pytest_sessionfinish(session, exitstatus):
    lock = getattr(session.config, "_ve_native_lock", None)
    if lock is not None:
        lock.close()


@pytest.fixture(autouse=True)
def generous_hang_guards(monkeypatch):
    # Deadline tests install their own deterministic clock and budget.
    # All production defaults and semantic work limits remain unchanged.
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", 1800)
    monkeypatch.setattr(argument, "LEAN_REPLAY_TIMEOUT", 1800)
    monkeypatch.setattr(bundle, "LEAN_REPLAY_TIMEOUT", 1800)
    monkeypatch.setenv("VE_CONFORMANCE_HANG_TIMEOUT", "1800")
