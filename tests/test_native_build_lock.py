"""Regressions for shared native artifacts during parallel pytest runs."""

import fcntl
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

    def communicate_once_spawned(process, *args, **kwargs):
        # Start the build's timeout only when the driver's descendants exist.
        _wait_for(spawned)
        return communicate(process, *args, **kwargs)

    monkeypatch.setattr(subprocess.Popen, "communicate", communicate_once_spawned)
    try:
        with (tmp_path / "build.lock").open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            with pytest.raises(TimeoutError):
                conftest._run_build([sys.executable, "-c", driver], None, None, lock,
                    timeout=1)
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
