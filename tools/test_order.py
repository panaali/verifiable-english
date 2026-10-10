"""The order an agent's run takes its test units in, and what it remembers of the last run.

`tools/select_tests.py --run` starts the units that failed last time first, then the test files the
change edits, then the rest in name order (`order`), so the first failure shows minutes sooner. The
order never changes which units run: it is a permutation of the selection. With `--maxfail N` the run
stops after N failed tests; a gate never stops early (tools/gate_pytest.py refuses `--maxfail`, `-x`
and `--stepwise`).

The last failures are this worktree's (`last_failed`): the failed tests of the last selected run, kept
in the worktree's git directory, and of the worktree's gate record (`gate-result.json`) when the gate
ran after that run. A unit leaves the list when it runs to the end without a failure. Failures come from each unit's JUnit
report (`junit_failures`), read with the XML library; a unit that fails without one counts as one
failed test named by the unit.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ElementTree

ROOT = Path(__file__).resolve().parents[1]
STATE = "ve-last-failed.json"
FORMAT = "ve-last-failed@1"
GATE_RECORD = "gate-result.json"
# The pytest options that make a unit write the JUnit report `junit_failures` reads (xunit1 names the file).
JUNIT_OPTIONS = ("-o", "junit_family=xunit1")


def order(units: Iterable[str], *, changed: Iterable[str] = (), failed: Iterable[str] = ()) -> list[str]:
    """`units`: those in `failed` first, then those in `changed`, then the rest, each group in name order."""
    units = sorted(set(units))
    failed, changed = set(failed), set(changed)
    return ([unit for unit in units if unit in failed]
            + [unit for unit in units if unit in changed and unit not in failed]
            + [unit for unit in units if unit not in failed and unit not in changed])


def unit_of(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def junit_options(report: Path) -> list[str]:
    return [*JUNIT_OPTIONS, f"--junitxml={report}"]


def read_junit(report: Path, unit: str | None = None) -> tuple[set[str], list[str]] | None:
    """The test files a JUnit (xunit1) report has cases of, and the node IDs of its failed and errored tests;
    None when there is no readable report. A case without a file (a collection error, named by its module)
    is that module's file, or `unit` when given."""
    try:
        tree = ElementTree.parse(report)
    except (OSError, ElementTree.ParseError):
        return None
    files, failed = set(), set()
    for case in tree.iter("testcase"):
        file, name, classname = case.get("file"), case.get("name") or "", case.get("classname") or ""
        broken = case.find("failure") is not None or case.find("error") is not None
        if not file:
            file = unit or name.replace(".", "/") + ".py"
            files.add(file)
            if broken:
                failed.add(file)
            continue
        files.add(file)
        if broken:
            module = file.removesuffix(".py").replace("/", ".")
            if not classname and name == module:  # the module itself: it failed to collect
                failed.add(file)
                continue
            classes = classname.removeprefix(module + ".").split(".") if classname.startswith(module + ".") else []
            failed.add("::".join([file, *classes, name]))
    return files, sorted(failed)


def git_dir(root: Path = ROOT) -> Path:
    found = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=root, text=True,
                           capture_output=True, check=True).stdout.strip()
    return Path(found)


def state_path(root: Path = ROOT) -> Path:
    """This worktree's own git directory: the last failures are the worktree's, never another's."""
    return git_dir(root) / STATE


def read_state(path: Path) -> dict[str, list[str]]:
    """The failed tests by unit in the state file, or nothing for a missing or malformed one (order only)."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    failed = data.get("failed") if isinstance(data, dict) and data.get("format") == FORMAT else None
    if not isinstance(failed, dict):
        return {}
    return {unit: sorted(ids) for unit, ids in failed.items() if isinstance(unit, str) and isinstance(ids, list)
            and all(isinstance(nodeid, str) for nodeid in ids)}


def gate_failures(path: Path) -> dict[str, list[str]]:
    """The failed tests of a gate record by unit (stage `pytest`, a test node ID), or nothing."""
    try:
        record = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    failures = record.get("failures") if isinstance(record, dict) else None
    found: dict[str, set[str]] = {}
    for failure in failures if isinstance(failures, list) else ():
        if not isinstance(failure, dict):
            continue
        nodeid = failure.get("nodeid")
        if failure.get("stage") == "pytest" and isinstance(nodeid, str) and nodeid.startswith("tests/"):
            found.setdefault(unit_of(nodeid), set()).add(nodeid)
    return {unit: sorted(ids) for unit, ids in found.items()}


def last_failed(root: Path = ROOT, state: Path | None = None) -> dict[str, list[str]]:
    """The failed tests by unit of this worktree's last selected run and of its gate record, when the gate
    ran after that run (a selected run since then has seen which of them still fail)."""
    state = state or state_path(root)
    sources = [read_state(state)]
    if newer(root / GATE_RECORD, state):
        sources.append(gate_failures(root / GATE_RECORD))
    merged: dict[str, set[str]] = {}
    for source in sources:
        for unit, ids in source.items():
            merged.setdefault(unit, set()).update(ids)
    return {unit: sorted(ids) for unit, ids in sorted(merged.items())}


def newer(path: Path, than: Path) -> bool:
    """Whether `path` exists and was written after `than` (or `than` does not exist)."""
    try:
        written = path.stat().st_mtime_ns
    except OSError:
        return False
    try:
        return written > than.stat().st_mtime_ns
    except OSError:
        return True


def updated(previous: Mapping[str, list[str]], *, completed: Iterable[str],
            failed: Mapping[str, list[str]]) -> dict[str, list[str]]:
    """The state after a run: a unit that ran to the end leaves it unless it failed; a failed unit's tests
    replace its old ones; a unit the run did not finish keeps what it had."""
    state = {unit: list(ids) for unit, ids in previous.items() if unit not in set(completed)}
    state.update({unit: sorted(ids) for unit, ids in failed.items() if ids})
    return dict(sorted(state.items()))


def write_state(path: Path, failed: Mapping[str, list[str]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps({"format": FORMAT, "failed": dict(sorted(failed.items()))},
                                    indent=1, sort_keys=True) + "\n")
    temporary.replace(path)
