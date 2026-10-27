"""The pool that elaborates a mutant module's selected sources at once (`tests/lean_pool.py`), with a fake elaborate
function: it elaborates exactly the sources of the module's items the session runs, starts no pool under xdist or at
width 1, and leaves each test the outcome its own call would give (a missing result is the serial call; a timeout is
the same timeout)."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

import lean_pool
from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import nested_pytest  # noqa: E402

# A module whose module-scoped fixture asks the pool for the sources of its `test_a` items; `test_b` has none.
POOLED = """
import json, threading
from pathlib import Path
import pytest
import lean_pool

@pytest.fixture(scope="module")
def pooled(request, tmp_path_factory):
    asked, lock = [], threading.Lock()
    def elaborate(directory, source):
        with lock:
            asked.append(source)
        return source.upper()
    results = lean_pool.elaborate_selected(request, {"test_a": lambda n: f"{MODULE}-{n}"}, elaborate,
                                           lambda: tmp_path_factory.mktemp("pool"), env={})
    Path(OUT).write_text(json.dumps({"items": [item.nodeid for item in lean_pool.selected(request.session,
                                                                                          request.module)],
                                     "asked": sorted(asked), "results": results}))

@pytest.mark.parametrize("n", ["keep1", "keep2", "dropped", "unselected"])
def test_a(pooled, n):
    pass

def test_b(pooled):
    pass
"""
# Deselects one item of the pooled module, as a plugin's `pytest_collection_modifyitems` does.
CONFTEST = """
def pytest_collection_modifyitems(config, items):
    gone = [item for item in items if item.name == "test_a[dropped]"]
    items[:] = [item for item in items if item not in gone]
    config.hook.pytest_deselected(items=gone)
"""
# Another module with a `test_a` of its own, which the first module's pool must not see.
OTHER = """
import pytest

@pytest.mark.parametrize("n", ["keep1", "other"])
def test_a(n):
    pass
"""


def test_the_pool_elaborates_exactly_the_modules_items_that_will_run(tmp_path):
    """After `-k` and a deselection, the pool builds and elaborates the sources of the module's remaining items, and
    no other module's items (`other_test.py` has a `test_a` of its own)."""
    out = tmp_path / "out.json"
    for module in ("pooled_test", "other_test"):
        text = POOLED.replace("{MODULE}", module).replace("OUT", repr(str(out))) if module == "pooled_test" else OTHER
        (tmp_path / f"{module}.py").write_text(text)
    (tmp_path / "conftest.py").write_text(CONFTEST)
    command = nested_pytest.command(["-q", "-p", "no:cacheprovider", "--rootdir", str(tmp_path), "-k",
                                     "not unselected", "pooled_test.py", "other_test.py"])
    done = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=HANG_TIMEOUT,
                          env=nested_pytest.environment({"PATH": "/usr/bin:/bin"}, PYTHONPATH=str(ROOT / "tests")))
    assert done.returncode == 0, done.stdout + done.stderr
    found = json.loads(out.read_text())
    assert found["items"] == ["pooled_test.py::test_a[keep1]", "pooled_test.py::test_a[keep2]",
                              "pooled_test.py::test_b"]
    assert found["asked"] == ["pooled_test-keep1", "pooled_test-keep2"]
    assert found["results"] == {"pooled_test-keep1": "POOLED_TEST-KEEP1", "pooled_test-keep2": "POOLED_TEST-KEEP2"}


class _NoPool:
    def __init__(self, *_):
        raise AssertionError("a pool was started")


def _request(*names: str):
    module = SimpleNamespace(__name__="fake_module")
    items = [SimpleNamespace(module=module, originalname="test_x", callspec=SimpleNamespace(params={"name": n}))
             for n in names]
    return SimpleNamespace(session=SimpleNamespace(items=items), module=module)


@pytest.mark.parametrize("env", [{"VE_TEST_LEAN_JOBS": "1"}, {"PYTEST_XDIST_WORKER": "gw0"},
                                 {"PYTEST_XDIST_WORKER": "gw3", "VE_TEST_LEAN_JOBS": "6"}],
                         ids=["width-1", "xdist-worker", "xdist-worker-with-a-width"])
def test_no_pool_starts_at_width_1_or_in_an_xdist_worker(monkeypatch, env):
    """Every test then elaborates its own source, as before: nothing is built, elaborated or given a directory."""
    calls = []
    monkeypatch.setattr(lean_pool, "ThreadPoolExecutor", _NoPool)
    results = lean_pool.elaborate_selected(_request("m1", "m2"), {"test_x": lambda name: calls.append(name) or name},
                                           lambda d, s: calls.append(s), lambda: calls.append("base"), env=env)
    assert results == {} and calls == []
    assert lean_pool.width(env) == 1


def test_the_width_is_the_setting_else_the_default(tmp_path):
    assert lean_pool.width({}) == lean_pool.JOBS > 1
    assert lean_pool.width({"VE_TEST_LEAN_JOBS": "3"}) == 3
    for bad in ("0", "-2", "x", "1.5"):
        with pytest.raises(ValueError, match="VE_TEST_LEAN_JOBS"):
            lean_pool.width({"VE_TEST_LEAN_JOBS": bad})
    # The same request with no setting starts the pool and elaborates each distinct source once.
    asked, lock = [], threading.Lock()

    def elaborate(directory, source):
        assert directory.parent == tmp_path and directory.is_dir()
        with lock:
            asked.append(source)
        return f"done {source}"
    results = lean_pool.elaborate_selected(_request("m1", "m2", "m1"), {"test_x": lambda name: name}, elaborate,
                                           lambda: tmp_path, env={})
    assert results == {"m1": "done m1", "m2": "done m2"} and sorted(asked) == ["m1", "m2"]


def test_a_result_missing_from_the_pool_is_the_tests_own_call(tmp_path):
    """A source whose build or elaboration raised something other than a timeout is not in the results, and its test
    calls the serial path; a source the pool has is not elaborated again."""
    def build(name):
        if name == "unbuilt":
            raise AssertionError("the mutation does not apply")
        return name

    def elaborate(directory, source):
        if source == "broken":
            raise OSError("no room to write the mutant")
        return f"pool {source}"
    results = lean_pool.elaborate_selected(_request("ok", "unbuilt", "broken"), {"test_x": build}, elaborate,
                                           lambda: tmp_path, env={"VE_TEST_LEAN_JOBS": "2"})
    assert results == {"ok": "pool ok"}
    serial = []
    for source in ("ok", "unbuilt", "broken"):
        done = lean_pool.result(results, source, lambda source=source: serial.append(source) or f"serial {source}")
        assert done == (f"pool {source}" if source == "ok" else f"serial {source}")
    assert serial == ["unbuilt", "broken"]


def _test_body(elaborate):
    """What a mutant test does with its elaboration (`test_every_seeded_mutant_fails_a_fixture`)."""
    done = elaborate()
    assert done.returncode != 0


def _outcome(body) -> tuple:
    try:
        body()
    except subprocess.TimeoutExpired as timeout:
        return "TimeoutExpired", timeout.cmd, timeout.timeout
    except AssertionError:
        return "AssertionError",
    return "passed",


def test_a_timeout_in_the_pool_is_the_outcome_of_the_serial_call(tmp_path):
    """An elaboration that times out raises the same `TimeoutExpired` in its test as the test's own call raises; the
    other sources keep their results."""
    def elaborate(directory, source):
        if source == "slow":
            raise subprocess.TimeoutExpired(["lake", "env", "lean", str(directory / "M.lean")], HANG_TIMEOUT)
        return subprocess.CompletedProcess(["lake"], 1 if source == "killed" else 0, "", "")
    results = lean_pool.elaborate_all(["slow", "killed", "survives"], elaborate, tmp_path, 3)
    assert set(results) == {"slow", "killed", "survives"}
    for source in results:
        serial = _outcome(lambda: _test_body(lambda: elaborate(tmp_path / "serial", source)))
        pooled = _outcome(lambda: _test_body(lambda: lean_pool.result(results, source, lambda: pytest.fail("serial"))))
        assert pooled[0] == serial[0] and pooled[2:] == serial[2:], source
    assert _outcome(lambda: _test_body(lambda: lean_pool.result(results, "slow", None)))[0] == "TimeoutExpired"
    assert [_outcome(lambda s=s: _test_body(lambda: lean_pool.result(results, s, None)))[0]
            for s in ("killed", "survives")] == ["passed", "AssertionError"]
