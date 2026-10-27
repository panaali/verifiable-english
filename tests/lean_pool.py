"""Elaborate the Lean mutants a test module will run at once, before its tests read them (speed-vocabpar).

A mutant test elaborates one source with `lake env lean` and asserts on the output. `tools/select_tests.py --run`
runs each test file as one process without xdist, so a module of 600 such tests ran them one after another and
set the selected run's wall time. `elaborate_selected` finds the module's items the session will run (after `-k`
and deselection), builds each one's source with the function its test calls, and elaborates them all through a
bounded pool of threads, each waiting on the module's own elaborate function. Each test then reads its result
(`result`) and asserts exactly what it asserted before.

Under xdist (the gate, the nightlies) and at width 1 there is no pool: every test elaborates its own source, as
before. A result the pool does not have, for whatever reason, is elaborated by the test itself.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
from typing import Callable, Mapping

# The `lake env lean` processes a module's pool runs at once: the 6 workers a Mac test-runner slot gives one pytest
# run (MAC_PYTEST_WORKERS), so a unit of a selected run takes no more of the runner than a plain run with `-n 6`
# would (measured in docs/infra/speed-vocabpar/REPORT.md). VE_TEST_LEAN_JOBS replaces it; 1 is the serial path.
JOBS = 6


def width(env: Mapping[str, str] = os.environ) -> int:
    """How many elaborations run at once: 1 in an xdist worker (its tests already run side by side with the
    other workers'), else VE_TEST_LEAN_JOBS, else `JOBS`."""
    if env.get("PYTEST_XDIST_WORKER"):
        return 1
    setting = env.get("VE_TEST_LEAN_JOBS", "").strip()
    if not setting:
        return JOBS
    if not setting.isdigit() or int(setting) < 1:
        raise ValueError(f"VE_TEST_LEAN_JOBS must be a positive integer, not {setting!r}")
    return int(setting)


def selected(session, module) -> list:
    """The items of `module` that `session` will run: `session.items` is the run's list after `-k`, `-m` and
    every deselection."""
    return [item for item in session.items if getattr(item, "module", None) is module]


def elaborate_all(sources: list[str], elaborate: Callable[[Path, str], subprocess.CompletedProcess], base: Path,
                  jobs: int) -> dict[str, object]:
    """Each distinct source elaborated by `elaborate(directory, source)`, `jobs` at a time, each in its own
    directory under `base`. A timeout is kept (the test raises it, as its own call would); any other exception
    leaves the source out, so its test elaborates it itself."""
    unique = list(dict.fromkeys(sources))

    def one(job: tuple[int, str]) -> tuple[str, object]:
        index, source = job
        directory = base / str(index)
        try:
            directory.mkdir()
            return source, elaborate(directory, source)
        except subprocess.TimeoutExpired as timeout:
            return source, timeout
        except Exception:
            return source, None

    pool = ThreadPoolExecutor(jobs)
    try:
        return {source: done for source, done in pool.map(one, enumerate(unique)) if done is not None}
    finally:
        pool.shutdown(cancel_futures=True)


def elaborate_selected(request, sources: Mapping[str, Callable[..., str]],
                       elaborate: Callable[[Path, str], subprocess.CompletedProcess], base: Callable[[], Path],
                       env: Mapping[str, str] = os.environ) -> dict[str, object]:
    """For a module-scoped fixture: the results of every source the module's selected tests will elaborate.
    `sources` maps a test function's name to the function its test calls for its source, given the item's
    parameters; `base()` makes the pool's directory. Empty at width 1, so every test takes the serial path."""
    jobs = width(env)
    if jobs == 1:
        return {}
    wanted = []
    for item in selected(request.session, request.module):
        build = sources.get(getattr(item, "originalname", None))
        if build is None:
            continue
        callspec = getattr(item, "callspec", None)
        try:
            wanted.append(build(**(callspec.params if callspec else {})))
        except Exception:
            continue  # the test builds it itself and fails there, as it did before
    return elaborate_all(wanted, elaborate, base(), jobs) if wanted else {}


def result(results: Mapping[str, object], source: str,
           serial: Callable[[], subprocess.CompletedProcess]) -> subprocess.CompletedProcess:
    """`source`'s elaboration: the pool's result, its timeout raised as the test's own call raises it, or, when the
    pool has none, `serial()`."""
    if source not in results:
        return serial()
    done = results[source]
    if isinstance(done, subprocess.TimeoutExpired):
        raise subprocess.TimeoutExpired(done.cmd, done.timeout, done.output, done.stderr)
    return done
