"""Regressions for shared native artifacts during parallel pytest runs."""

import fcntl
from pathlib import Path
import subprocess
import sys
import time

import pytest

import conftest


def _wait_for(path, timeout=10):
    deadline = time.monotonic() + timeout
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert path.exists()


def test_orphaned_builder_keeps_exclusive_lock(tmp_path):
    """A killed pytest owner must not expose artifacts while its builder writes."""
    lock_path = tmp_path / "build.lock"
    started = tmp_path / "started"
    child_code = f"from pathlib import Path; import time; Path({str(started)!r}).touch(); time.sleep(1.5)"
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
        owner.kill()
        owner.wait(timeout=5)
        with lock_path.open("a+") as contender:
            with pytest.raises(BlockingIOError):
                fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                try:
                    fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    time.sleep(0.01)
            else:
                pytest.fail("orphaned builder did not release the lock")
    finally:
        if owner.poll() is None:
            owner.kill()
            owner.wait(timeout=5)


def test_timeout_stops_compiler_descendants(tmp_path):
    """A timed out build cannot leave a grandchild writing after retry."""
    spawned = tmp_path / "spawned"
    ready = tmp_path / "grandchild-ready"
    late = tmp_path / "late"
    release = tmp_path / "release"
    grandchild = ("from pathlib import Path; import time; "
                  f"release = Path({str(release)!r}); "
                  f"Path({str(ready)!r}).touch(); "
                  "\nwhile not release.exists(): time.sleep(0.01)\n"
                  f"Path({str(late)!r}).touch()")
    driver = "\n".join((
        "import subprocess, sys, time",
        f"from pathlib import Path; Path({str(spawned)!r}).touch()",
        f"subprocess.Popen([sys.executable, '-c', {grandchild!r}])",
        "time.sleep(5)",
    ))
    with (tmp_path / "build.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with pytest.raises(TimeoutError):
            conftest._run_build([sys.executable, "-c", driver], None, None, lock,
                timeout=3)
    assert spawned.exists()
    assert ready.exists()
    release.touch()
    time.sleep(0.2)
    assert not late.exists()


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
    result = subprocess.run([sys.executable, "-c", contender_code], timeout=5)
    assert result.returncode == 0


def test_lock_path_ignores_tmpdir(tmp_path, monkeypatch):
    """Sandbox-specific TMPDIR values cannot split the checkout lock."""
    expected = conftest.native_lock_path()
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    assert conftest.native_lock_path() == expected
    assert expected == conftest.ROOT / "rust/target/.ve-native-build.lock"
