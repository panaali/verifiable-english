"""Which tests of one test file a chunk runs: the one rule that splits a file's collected tests into k parts.

A selected run (the selector's `--run`) can run a heavy test file as k pytest processes ("chunks") instead of one,
so one file no longer sets the floor of the whole run. Chunk i of k is named by the label `<file>::chunk(<i>/<k>)`
(`label`, `parse_label`) and runs as an ordinary pytest process of the file with VARIABLE set to `<i>/<k>`; the
suite's collection hook keeps the items `partition` puts in part i and deselects the rest, in pytest's own way.
The selector checks the outcome against this same rule: every collected test ran in exactly one chunk.

`partition` is pure and deterministic: it depends only on the set of node IDs, the count and the seconds given.
The nodes whose seconds are known go first, longest first (ties by node ID), each to the part with the least
seconds so far (ties to the lowest part); the others follow in node ID order, round-robin. With no seconds at all
that is plain round-robin over the sorted node IDs. Every node is in exactly one part. Which tests a chunk keeps
never depends on collection order, the process or the machine, so the selector's own listing of the file gives
the same parts as the chunk processes do.

Strings here name no file: the suite's collection hook imports this module, and every test's import closure
holds what that hook imports.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping
import os
import re

# The environment variable a chunk process reads: `<i>/<k>`, 1 <= i <= k. Unset: the whole file, as always.
VARIABLE = "VE_TEST_CHUNK"
LABEL = re.compile(r"(?P<file>[^:]+)::chunk\((?P<index>[1-9][0-9]*)/(?P<count>[1-9][0-9]*)\)")
SETTING = re.compile(r"(?P<index>[1-9][0-9]*)/(?P<count>[1-9][0-9]*)")


def label(file: str, index: int, count: int) -> str:
    """The name of chunk `index` of `count` of `file` in a plan and a run's output."""
    check(index, count)
    return f"{file}::chunk({index}/{count})"


def parse_label(text: str) -> tuple[str, int, int] | None:
    """(file, index, count) of a chunk label; None for anything else (a plain unit)."""
    found = LABEL.fullmatch(text)
    if found is None or int(found["index"]) > int(found["count"]):
        return None
    return found["file"], int(found["index"]), int(found["count"])


def setting(text: str) -> tuple[int, int]:
    """(index, count) of a VARIABLE value; ValueError for a malformed one."""
    found = SETTING.fullmatch(text.strip())
    if found is None or int(found["index"]) > int(found["count"]):
        raise ValueError(f"{VARIABLE}={text!r}: expected <i>/<k> with 1 <= i <= k")
    return int(found["index"]), int(found["count"])


def check(index: int, count: int) -> None:
    if not (type(index) is int and type(count) is int and 1 <= index <= count):
        raise ValueError(f"chunk {index!r}/{count!r}: expected 1 <= i <= k")


def partition(nodeids: Iterable[str], count: int, seconds: Mapping[str, float] | None = None) -> list[list[str]]:
    """The `count` parts of `nodeids`, each sorted by node ID (module docstring: the rule)."""
    check(1, count)
    seconds = seconds or {}
    nodes = sorted(set(nodeids))
    known = sorted((nodeid for nodeid in nodes if nodeid in seconds), key=lambda nodeid: (-seconds[nodeid], nodeid))
    parts: list[list[str]] = [[] for _ in range(count)]
    load = [0.0] * count
    for nodeid in known:
        part = min(range(count), key=lambda i: (load[i], i))
        parts[part].append(nodeid)
        load[part] += seconds[nodeid]
    for position, nodeid in enumerate(nodeid for nodeid in nodes if nodeid not in seconds):
        parts[position % count].append(nodeid)
    return [sorted(part) for part in parts]


def chunk(nodeids: Iterable[str], index: int, count: int, seconds: Mapping[str, float] | None = None) -> list[str]:
    """The node IDs chunk `index` of `count` keeps: part `index` of `partition`."""
    check(index, count)
    return partition(nodeids, count, seconds)[index - 1]


def register(config, seconds: Callable[[], Mapping[str, float]], environ: MutableMapping[str, str] = os.environ) -> None:
    """The suite's hook (from its `pytest_configure`): with VARIABLE set, keep only that chunk's tests.

    The variable is taken out of `environ` here, before any test runs, so no process a test starts inherits it.
    Unset, nothing is registered and the run is what it always was. The chunk is chosen last among the
    collection hooks (`trylast`), after `-m`, `-k` and every other deselection, over the tests still collected,
    balanced by `seconds()` (the recorded per-test durations); the rest is deselected through pytest's own
    `pytest_deselected`, so the summary counts it as deselected. A chunk runs in one process: under xdist the
    workers would not see the variable, so that is a usage error."""
    value = environ.pop(VARIABLE, None)
    if value is None:
        return
    import pytest

    try:
        index, count = setting(value)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from None
    if getattr(config.option, "numprocesses", None) or hasattr(config, "workerinput"):
        raise pytest.UsageError(f"{VARIABLE}={value}: a chunk runs in one pytest process, not under xdist")

    class Chunk:
        @pytest.hookimpl(trylast=True)
        def pytest_collection_modifyitems(self, config, items):
            keep = set(chunk((item.nodeid for item in items), index, count, seconds()))
            deselected = [item for item in items if item.nodeid not in keep]
            if deselected:
                config.hook.pytest_deselected(items=deselected)
                items[:] = [item for item in items if item.nodeid in keep]

    config.pluginmanager.register(Chunk(), "ve-test-chunk")
