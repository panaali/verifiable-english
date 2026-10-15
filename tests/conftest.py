"""Shared test setup for serial and xdist runs."""

import fcntl
import hashlib
import json
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
HEAVY_IDS = frozenset(row["nodeid"] for row in json.loads((ROOT / "tests/heavy.json").read_text())["heavy"])


def pytest_collection_modifyitems(items):
    for item in items:
        if item.nodeid in HEAVY_IDS:
            item.add_marker(pytest.mark.heavy)
        elif item.get_closest_marker("heavy"):
            raise pytest.UsageError(f"{item.nodeid} is marked heavy but absent from tests/heavy.json; "
                                    "regenerate the measured inventory")

# A virtualenv copied from another checkout keeps that checkout's interpreter in its entry-point
# shebangs (`.venv/bin/pytest`), and with it that checkout's editable install: `ve` would then be
# the other checkout's, and so would the Lean service and Rust binaries it starts.
_VE_CHECKOUT = Path(unambiguity.__file__).resolve().parents[2]
if _VE_CHECKOUT != ROOT:
    raise pytest.UsageError(f"ve is imported from {_VE_CHECKOUT}, not from this checkout {ROOT}; "
                            "recreate .venv (rm -rf .venv && uv sync --locked --group dev)")


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
    english_comparator(config)


def english_comparator(config):
    """The suite runs English admission with the comparator on (docs/spec/english-lean-e2.md 2.8, D15): every
    Lean-decided admission also runs Python's reader and writes one comparison record, which never changes the
    result. `VE_ENGLISH_COMPARATOR=0` turns it off for a run; a test of the switch sets it itself. The records
    go to one directory per run (each xdist worker its own file), and the session's end writes their summary
    (`english_comparator_summary`) beside them and prints it."""
    if os.environ.get("VE_ENGLISH_COMPARATOR") is None:
        os.environ["VE_ENGLISH_COMPARATOR"] = "1"
    if os.environ["VE_ENGLISH_COMPARATOR"] != "1":
        return
    directory = os.environ.get("VE_ENGLISH_COMPARATOR_DIR")
    if directory is None:
        import tempfile
        directory = tempfile.mkdtemp(prefix="ve-english-comparator-")
        os.environ["VE_ENGLISH_COMPARATOR_DIR"] = directory
    name = getattr(config, "workerinput", {}).get("workerid", "controller")
    os.environ.setdefault("VE_SHADOW_LOG", str(Path(directory) / f"{name}.jsonl"))


def english_comparator_summary(directory: Path) -> dict:
    """The comparison records of a run, counted: the English admissions compared, those excluded (Python's
    wall-clock limit), and the difference classes of the rest (S2 4.5 under S3 2.11's correspondence)."""
    from collections import Counter
    records = []
    for path in sorted(directory.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            if record.get("op") in (None, "english.admission") and "classes" in record:
                records.append(record)
    compared = [record for record in records if "excluded" not in record and "planted" not in record]
    classes = Counter(",".join(record["classes"]) or "agree" for record in compared)
    return {"records": len(records), "excluded": sum("excluded" in record for record in records),
            "planted": sum("planted" in record for record in records), "classes": dict(sorted(classes.items()))}


def _setting(variable, default):
    text = os.environ.get(variable, "")
    return int(text) if text.isdecimal() and int(text) > 0 else default


def worker_count(cpus=None, load=None):
    """`-n auto`: the CPUs this process may use less the machine's 1-minute load, at most
    VE_TEST_WORKERS (default: every usable CPU). A busy machine then gets fewer workers
    instead of an oversubscribed run; never fewer than one. More is opt-in: the floor
    VE_TEST_MIN_WORKERS (default 1, at most VE_TEST_WORKERS) lets a machine whose load
    never falls below its CPU count (a shared VM) run the ~20,000 CPU-second suite on
    more than one worker; test outcomes do not depend on load either way."""
    cpus = len(os.sched_getaffinity(0)) if cpus is None else cpus
    load = os.getloadavg()[0] if load is None else load
    configured = _setting("VE_TEST_WORKERS", cpus)
    floor = min(_setting("VE_TEST_MIN_WORKERS", 1), configured)
    return max(floor, min(configured, cpus - round(load)))


@pytest.hookimpl(optionalhook=True)  # the gate loads pytest without plugin autoload
def pytest_xdist_auto_num_workers(config):
    count = worker_count()
    print(f"ve: -n auto: {count} workers (load {os.getloadavg()[0]:.1f}, "
          f"{len(os.sched_getaffinity(0))} CPUs)", file=sys.stderr)
    return count


# What the native builds read, and what they produce.
NATIVE_INPUTS = ("lean", "rust", "rust-toolchain.toml")
NATIVE_BUILD_DIRS = ("lean/.lake", "rust/target")


def native_outputs(root=ROOT):
    binaries = root / "lean/.lake/build/bin"
    return sorted((*(binaries.iterdir() if binaries.is_dir() else ()),
                   root / "rust/target/release/ve", root / "rust/target/debug/ve"))


def native_fingerprint(root=ROOT):
    """The native builds' inputs (the content of every tracked or unignored file under
    lean/ and rust/, build directories excepted, and the Rust toolchain pin) and the
    identity of their outputs (size, modification time and inode of each executable);
    None when an output is missing. Equal to the stamp the last build in this checkout
    wrote exactly when its inputs and outputs are unchanged."""
    listed = subprocess.run(["git", "ls-files", "-z", "-c", "-o", "--exclude-standard", "--", *NATIVE_INPUTS],
                            cwd=root, capture_output=True, check=True, timeout=HANG_TIMEOUT).stdout
    digest = hashlib.sha256()
    for name in sorted(set(filter(None, listed.decode().split("\0")))):
        if name.startswith(tuple(f"{directory}/" for directory in NATIVE_BUILD_DIRS)):
            continue
        path = root / name
        if path.is_file():
            digest.update(name.encode() + b"\0" + path.read_bytes() + b"\0")
    outputs = {}
    for path in native_outputs(root):
        try:
            status = path.stat()
        except FileNotFoundError:
            return None
        outputs[path.relative_to(root).as_posix()] = [status.st_size, status.st_mtime_ns, status.st_ino]
    return {"inputs": digest.hexdigest(), "outputs": outputs}


def native_stamp_path(root=ROOT):
    return native_lock_path(root).with_name(".ve-native-stamp.json")


def native_fresh(root=ROOT) -> bool:
    """Whether the last build in this checkout already produced the current binaries."""
    stamp = native_stamp_path(root)
    fingerprint = native_fingerprint(root)
    try:
        return fingerprint is not None and json.loads(stamp.read_text()) == fingerprint
    except (FileNotFoundError, ValueError):
        return False


def pytest_sessionstart(session):
    """Build once, then hold a read lock until all this process's tests end.

    VE_NATIVE_PREBUILT=1 uses the binaries as they are; =0 always builds. Unset (local
    runs), the binaries are reused when the stamp of the last build in this checkout
    still matches their inputs and outputs, else built and stamped."""
    lock_path = native_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = lock_path.open("a+")
    prebuilt = os.environ.get("VE_NATIVE_PREBUILT")
    try:
        if hasattr(session.config, "workerinput") or prebuilt == "1":
            fcntl.flock(lock, fcntl.LOCK_SH)
            return
        if prebuilt != "0" and native_fresh():
            fcntl.flock(lock, fcntl.LOCK_SH)  # waits for a build in progress
            if native_fresh():
                return
        fcntl.flock(lock, fcntl.LOCK_EX)
        if prebuilt == "0" or not native_fresh():
            _build_backends(lock)
            native_stamp_path().write_text(json.dumps(native_fingerprint()) + "\n")
        fcntl.flock(lock, fcntl.LOCK_SH)
    except BaseException:
        lock.close()
        raise
    finally:
        if not lock.closed:
            session.config._ve_native_lock = lock


def pytest_sessionfinish(session, exitstatus):
    lock = getattr(session.config, "_ve_native_lock", None)
    if lock is not None:
        lock.close()
    directory = os.environ.get("VE_ENGLISH_COMPARATOR_DIR")
    if directory and not hasattr(session.config, "workerinput") and Path(directory).is_dir():
        summary = english_comparator_summary(Path(directory))
        (Path(directory) / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
        print(f"\nve: English comparator: {json.dumps(summary)} ({directory})", file=sys.stderr)


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


@pytest.fixture(autouse=True)
def interrupted_gate_reaches_its_injected_build(request, monkeypatch):
    """The interruption test mocks toolchain setup, so it must also bypass trace lookup.

    The real gate checks Lake's traces with its validated Lean binary before the build.
    With setup mocked, the isolated test PATH has no Lean binary; the trace preflight
    would stop before the test's injected interruption at the Lean build.
    """
    if request.node.originalname == "test_interrupted_gate_cannot_record_pass":
        monkeypatch.setattr(request.module.gate.lake_outputs, "drop_stale", lambda *args, **kwargs: None)
