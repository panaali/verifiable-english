"""Shared test setup for serial and xdist runs."""

import fcntl
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

import pytest

from subprocesses import HANG_TIMEOUT
from tools import rust_build
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
    # Path-independent, so the release binary matches lean/checkers.lock.
    cargo_env = rust_build.cargo_env()
    commands = (
        ([lake, "build"], ROOT / "lean", None),
        ([cargo, "build", "-j", "2", "--locked", "--release",
          "--manifest-path", str(ROOT / "rust/Cargo.toml")], ROOT, cargo_env),
        ([cargo, "build", "-j", "2", "--locked", "-p", "ve"], ROOT / "rust", cargo_env),
    )
    for command, cwd, env in commands:
        _run_build(command, cwd, env, lock)


# The checker clients' wall-clock defaults (5 s per Rust call or Lean service
# request, 30 s for a service to start, 60-300 s per one-shot Lean runner call,
# 10-600 s in the conformance harness, 30 s for the pre-commit wire check) are
# hang guards, not work limits; under load a correct call can outlast them.
# Every test, and every process a test starts, waits HANG_TIMEOUT instead; the
# work limits are the backends' budgets. Set for the whole process, so module
# fixtures and collection see it too.
CHECKER_TIMEOUTS = ("VE_RUST_TIMEOUT", "VE_LEAN_SERVICE_TIMEOUT", "VE_LEAN_SERVICE_STARTUP_TIMEOUT",
                    "VE_LEAN_TIMEOUT", "VE_CONFORMANCE_HANG_TIMEOUT", "VE_PRECOMMIT_TIMEOUT")


class CheckerSettingRemoved(BaseException):
    """A child started without a checker setting (a BaseException, so no product handler hides it)."""


# The refused starts of the running test (a worker thread may swallow the exception).
REFUSED = []


def removed_checker_settings(env):
    """The checker settings a child started with `env` (None: this process's environment)
    lacks, when `env` derives from a running test's environment (it holds the
    PYTEST_CURRENT_TEST pytest sets). Such a child would wait a production default: a
    test checks a default by instrumentation, never by a real child running against it.
    A fresh environment (the gate's) is the child's own to configure."""
    env = os.environ if env is None else env
    if "PYTEST_CURRENT_TEST" not in env:
        return []
    return [variable for variable in CHECKER_TIMEOUTS if variable not in env]


# The real checkers: the Lean executables and the Rust builds.
CHECKERS = (ROOT / "lean/.lake/build/bin", ROOT / "rust/target")


def real_checker(program) -> bool:
    if program is None:
        return False
    path = os.path.realpath(os.fsdecode(program))
    return any(path.startswith(f"{directory}{os.sep}") for directory in CHECKERS)


def lowered_checker_settings(program, env):
    """The checker settings a real checker started with `env` (None: this process's
    environment) would wait less than HANG_TIMEOUT under, when `env` derives from a
    running test's environment. A test of a deadline injects its expiry against a fake
    (tests/subprocesses.py: expired_waits); a real checker under load always gets the
    hang guard."""
    env = os.environ if env is None else env
    if "PYTEST_CURRENT_TEST" not in env or not real_checker(program):
        return []
    lowered = []
    for variable in CHECKER_TIMEOUTS:
        try:
            if float(env.get(variable, HANG_TIMEOUT)) < HANG_TIMEOUT:
                lowered.append(variable)
        except ValueError:
            lowered.append(variable)
    return lowered


# Audit events that start a process: the positions of their program and environment arguments.
PROCESS_EVENTS = {"subprocess.Popen": (0, 3), "os.posix_spawn": (0, 2), "os.system": (None, None)}


def refuse_child_without_checker_settings(event, args):
    if event in PROCESS_EVENTS:
        program_at, env_at = PROCESS_EVENTS[event]
        env = None if env_at is None else args[env_at]
        missing = removed_checker_settings(env)
        if missing:
            message = f"{event} started a child without {', '.join(missing)}"
            REFUSED.append(message)
            raise CheckerSettingRemoved(message)
        program = None
        if program_at is not None:
            program = args[program_at]
            if program is None and event == "subprocess.Popen":
                argv = args[1]
                program = argv if isinstance(argv, (str, bytes, os.PathLike)) else next(iter(argv), None)
        lowered = lowered_checker_settings(program, env)
        if lowered:
            message = f"{event} started the real checker {program} with {', '.join(lowered)} below HANG_TIMEOUT"
            REFUSED.append(message)
            raise CheckerSettingRemoved(message)


def pytest_configure(config):
    for variable in CHECKER_TIMEOUTS:
        os.environ[variable] = str(HANG_TIMEOUT)
    sys.addaudithook(refuse_child_without_checker_settings)


def pytest_sessionstart(session):
    """Build once, then hold a read lock until all this process's tests end."""
    lock_path = native_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = lock_path.open("a+")
    try:
        if hasattr(session.config, "workerinput") or os.environ.get("VE_NATIVE_PREBUILT") == "1":
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
    monkeypatch.setattr(unambiguity, "EARLEY_SECONDS", HANG_TIMEOUT)
    for variable in CHECKER_TIMEOUTS:
        monkeypatch.setenv(variable, str(HANG_TIMEOUT))
    REFUSED.clear()
    yield
    refused, REFUSED[:] = list(REFUSED), []
    assert refused == [], "a test removed or lowered a checker setting and started a real child"
