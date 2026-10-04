"""Regressions for shared native artifacts during parallel pytest runs."""

import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

import conftest
from subprocesses import HANG_TIMEOUT


# Every step below waits for an explicit event (a file or a lock), never for a
# fixed interval: under load any interval can pass before the other side acts.
# HANG_TIMEOUT only bounds a side that never acts at all.
def _wait_for(path, timeout=HANG_TIMEOUT):
    deadline = time.monotonic() + timeout
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert path.exists()


def _wait_code(path):
    """Child code that blocks until `path` exists (or HANG_TIMEOUT passes)."""
    return (f"deadline = time.monotonic() + {HANG_TIMEOUT}\n"
            f"while not Path({str(path)!r}).exists() and time.monotonic() < deadline:\n"
            "    time.sleep(0.01)\n")


def _acquire(lock, timeout=HANG_TIMEOUT):
    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.01)


# The delays reproduce review findings: a parent scheduled 2 s late once saw an
# orphaned builder that had already slept out its fixed 1.5 s and released.
@pytest.mark.parametrize("parent_delay", [0, 2])
def test_orphaned_builder_keeps_exclusive_lock(tmp_path, parent_delay):
    """A killed pytest owner must not expose artifacts while its builder writes."""
    lock_path = tmp_path / "build.lock"
    started = tmp_path / "started"
    release = tmp_path / "release"
    child_code = ("from pathlib import Path; import time\n"
                  f"Path({str(started)!r}).touch()\n" + _wait_code(release))
    owner_code = "\n".join((
        "import fcntl, sys",
        "from pathlib import Path",
        f"sys.path.insert(0, {str(Path(conftest.__file__).parent)!r})",
        "import conftest",
        f"with Path({str(lock_path)!r}).open('a+') as lock:",
        "    fcntl.flock(lock, fcntl.LOCK_EX)",
        f"    conftest._run_build([sys.executable, '-c', {child_code!r}], None, None, lock)",
    ))
    owner = subprocess.Popen([sys.executable, "-c", owner_code],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        _wait_for(started)
        time.sleep(parent_delay)
        owner.kill()
        owner.wait(timeout=HANG_TIMEOUT)
        with lock_path.open("a+") as contender:
            # The builder holds the lock until it is told to finish, however
            # late this check runs.
            with pytest.raises(BlockingIOError):
                fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            release.touch()
            _acquire(contender)
    finally:
        release.touch()
        if owner.poll() is None:
            owner.kill()
            owner.wait(timeout=HANG_TIMEOUT)


# A driver that starts 4 s late once outlived the old fixed 3 s timeout before
# spawning its grandchild. The timeout now starts once the grandchild is up.
@pytest.mark.parametrize("driver_delay", [0, 4])
def test_timeout_stops_compiler_descendants(tmp_path, monkeypatch, driver_delay):
    """A timed out build cannot leave a grandchild writing after retry."""
    spawned = tmp_path / "spawned"
    ready = tmp_path / "grandchild-ready"
    alive = tmp_path / "grandchild-alive"
    late = tmp_path / "late"
    release = tmp_path / "release"
    # The grandchild holds `alive` locked for as long as it runs.
    grandchild = ("import fcntl, time\nfrom pathlib import Path\n"
                  f"alive = Path({str(alive)!r}).open('a+')\n"
                  "fcntl.flock(alive, fcntl.LOCK_EX)\n"
                  f"Path({str(ready)!r}).touch()\n" + _wait_code(release) +
                  f"Path({str(late)!r}).touch()\n")
    driver = "\n".join((
        "import subprocess, sys, time",
        "from pathlib import Path",
        f"time.sleep({driver_delay})",
        f"subprocess.Popen([sys.executable, '-c', {grandchild!r}])",
        _wait_code(ready),
        f"Path({str(spawned)!r}).touch()",
        f"time.sleep({HANG_TIMEOUT})",
    ))
    communicate = subprocess.Popen.communicate

    waits = []

    def communicate_once_spawned(process, *args, **kwargs):
        # The build's deadline expires (an injected clock) only once the driver's
        # descendants exist: the driver never ends, so nothing waits it out.
        if kwargs.get("timeout") is None:  # reaping the stopped group
            return communicate(process, *args, **kwargs)
        _wait_for(spawned)
        waits.append(kwargs["timeout"])
        return communicate(process, *args, **{**kwargs, "timeout": 0})

    monkeypatch.setattr(subprocess.Popen, "communicate", communicate_once_spawned)
    try:
        with (tmp_path / "build.lock").open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            with pytest.raises(TimeoutError):
                conftest._run_build([sys.executable, "-c", driver], None, None, lock)
        assert waits == [HANG_TIMEOUT]
        assert ready.exists()
        # _run_build returns only after the whole group has stopped, so the
        # grandchild's lock is already free; no interval decides this.
        with alive.open("a+") as check:
            fcntl.flock(check, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert not late.exists()
    finally:
        release.touch()


def test_other_invocation_cannot_rebuild_while_tests_read(tmp_path):
    """Different pytest basetemps still use one artifact lock."""
    assert conftest.native_lock_path() == conftest.native_lock_path(conftest.ROOT)
    assert tmp_path not in conftest.native_lock_path().parents
    assert conftest.native_lock_path().parent == conftest.ROOT / "rust/target"
    # The controller holds a shared lock throughout this invocation. A second
    # invocation must wait for it before taking the exclusive build lock.
    contender_code = "\n".join((
        "import fcntl, sys",
        "from pathlib import Path",
        f"with Path({str(conftest.native_lock_path())!r}).open('a+') as lock:",
        "    try:",
        "        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)",
        "    except BlockingIOError:",
        "        sys.exit(0)",
        "    sys.exit(1)",
    ))
    result = subprocess.run([sys.executable, "-c", contender_code], timeout=HANG_TIMEOUT)
    assert result.returncode == 0


def test_lock_path_ignores_tmpdir(tmp_path, monkeypatch):
    """Sandbox-specific TMPDIR values cannot split the checkout lock."""
    expected = conftest.native_lock_path()
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    assert conftest.native_lock_path() == expected
    assert expected == conftest.ROOT / "rust/target/.ve-native-build.lock"


def _native_checkout(root):
    """A checkout with one Lean and one Rust source and every native output the build makes."""
    subprocess.run(["git", "init", "-q", str(root)], check=True, timeout=HANG_TIMEOUT)
    (root / ".gitignore").write_text("ignored.lean\n")
    for name, text in {"lean/VE/A.lean": "def a := 1\n", "rust/src/main.rs": "fn main() {}\n",
                       "rust-toolchain.toml": "[toolchain]\n", "lean/.lake/build/bin/ve_service": "lean",
                       "rust/target/release/ve": "release", "rust/target/debug/ve": "debug"}.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    subprocess.run(["git", "add", "lean/VE", "rust/src", "rust-toolchain.toml", ".gitignore"], cwd=root,
                   check=True, timeout=HANG_TIMEOUT)


def test_local_runs_reuse_binaries_only_while_their_stamp_matches(tmp_path):
    """The default local run skips the build exactly when the last build's stamp still matches
    the native inputs (tracked or new, ignored files apart) and the outputs it produced."""
    _native_checkout(tmp_path)
    assert not conftest.native_fresh(tmp_path)
    stamp = conftest.native_stamp_path(tmp_path)
    stamp.write_text(json.dumps(conftest.native_fingerprint(tmp_path)))
    assert conftest.native_fresh(tmp_path)
    (tmp_path / "ignored.lean").write_text("not an input\n")
    (tmp_path / "lean/.lake/build/trace").write_text("a build directory is not an input\n")
    assert conftest.native_fresh(tmp_path)
    changes = [
        lambda: (tmp_path / "lean/VE/A.lean").write_text("def a := 2\n"),  # an edited source
        lambda: (tmp_path / "rust/src/new.rs").write_text("\n"),  # a new, untracked source
        lambda: (tmp_path / "rust-toolchain.toml").write_text("[toolchain]\nchannel = '1.99'\n"),
        lambda: (tmp_path / "rust/target/release/ve").write_text("another build"),  # a replaced output
        lambda: (tmp_path / "lean/.lake/build/bin/ve_quantity").write_text("lean"),  # an added output
    ]
    for change in changes:
        stamp.write_text(json.dumps(conftest.native_fingerprint(tmp_path)))
        change()
        assert not conftest.native_fresh(tmp_path)
    (tmp_path / "rust/target/debug/ve").unlink()
    assert conftest.native_fingerprint(tmp_path) is None and not conftest.native_fresh(tmp_path)


@pytest.mark.parametrize("cpus, load, settings, workers", [
    (32, 0.0, {}, 32), (32, 20.4, {}, 12), (32, 31.0, {}, 1), (32, 51.2, {}, 1),
    (16, 2.6, {"VE_TEST_WORKERS": "8"}, 8), (16, 6.0, {"VE_TEST_WORKERS": "8"}, 8),
    (16, 13.0, {"VE_TEST_WORKERS": "8"}, 3), (32, 51.2, {"VE_TEST_MIN_WORKERS": "8"}, 8),
    (32, 20.4, {"VE_TEST_MIN_WORKERS": "8"}, 12), (32, 51.2, {"VE_TEST_MIN_WORKERS": "8", "VE_TEST_WORKERS": "2"}, 2),
    (32, 51.2, {"VE_TEST_MIN_WORKERS": "0"}, 1), (2, 9.0, {}, 1),
], ids=["idle", "busy", "one slot left (review)", "overloaded: one", "configured", "configured, room left",
        "configured and busy", "opt-in floor", "opt-in floor below capacity", "configured below the floor",
        "a floor of zero is one", "two CPUs"])
def test_auto_workers_leave_the_busy_part_of_the_machine_alone(monkeypatch, cpus, load, settings, workers):
    """`-n auto` takes min(CPUs - load, VE_TEST_WORKERS), at least one, so a busy machine is
    not oversubscribed; a larger floor is only taken when VE_TEST_MIN_WORKERS asks for it."""
    for variable in ("VE_TEST_WORKERS", "VE_TEST_MIN_WORKERS"):
        monkeypatch.delenv(variable, raising=False)
    for variable, value in settings.items():
        monkeypatch.setenv(variable, value)
    assert conftest.worker_count(cpus=cpus, load=load) == workers
