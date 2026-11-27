"""The skip rule on every gate (tools/skip_policy.py, tools/gate-optional.json): a skipped test passes a gate only
while a row of the one allowed list names it, its skip message and an expiry day not yet past. The full gate
(tools/gate.py) and every selected run (tools/select_tests.py --run: the runner's shards, the Mac's and the VM's
selected runs, the after-release light gate) refuse any other skip, and the skip of an expired row, as they refuse
a failed test."""
from __future__ import annotations

import datetime
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import select_tests  # noqa: E402
from tools import gate  # noqa: E402
from tools.gate import REQUIRED_FAMILIES  # noqa: E402

LISTED = "tests/test_sample_skips.py::test_listed"
UNLISTED = "tests/test_sample_skips.py::test_unlisted"
EXPIRED = "tests/test_sample_skips.py::test_expired"
ROWS = [
    {"nodeid": LISTED, "reason": "optional corpus is not downloaded", "owner": "someone", "expires": "2999-12-31"},
    {"nodeid": EXPIRED, "reason": "optional corpus is not downloaded", "owner": "someone", "expires": "2000-01-01"},
]
MESSAGE = "optional corpus is not downloaded"


def junit(path: Path, skipped: list[str], passed: tuple[str, ...] = ("tests/test_sample_skips.py::test_runs",)) -> None:
    """A pytest xunit1 report: one passed case per `passed` ID, one skipped case (MESSAGE) per `skipped` ID."""
    cases = []
    for nodeid, skip in [*((node, False) for node in passed), *((node, True) for node in skipped)]:
        file, name = nodeid.split("::")
        classname = file.removesuffix(".py").replace("/", ".")
        body = (f'<skipped type="pytest.skip" message="{MESSAGE}">{file}:3: {MESSAGE}</skipped>' if skip else "")
        cases.append(f'<testcase classname="{classname}" name="{name}" file="{file}" line="3" time="0.01">'
                     f'{body}</testcase>')
    path.write_text('<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" errors="0" '
                    f'failures="0" skipped="{len(skipped)}" tests="{len(cases)}">{"".join(cases)}'
                    '</testsuite></testsuites>')


def use_rows(monkeypatch) -> None:
    """The selected runs read ROWS as the list (a run without the shared checker reads none and passes every skip)."""
    if hasattr(select_tests, "skip_policy"):
        monkeypatch.setattr(select_tests.skip_policy, "load", lambda: ROWS)


@pytest.fixture
def plain_run(monkeypatch, tmp_path):
    """run_plain with pytest replaced: the fake writes a report whose skipped IDs the test sets, and exits 0."""
    use_rows(monkeypatch)
    monkeypatch.setattr(select_tests.run_order, "state_path", lambda: tmp_path / "state.json")
    skipped: list[str] = []

    def fake_run(command, **kwargs):
        report = next(Path(arg.split("=", 1)[1]) for arg in command if arg.startswith("--junitxml="))
        junit(report, skipped)
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(select_tests.subprocess, "run", fake_run)

    def run(*ids: str) -> int:
        skipped[:] = ids
        return select_tests.run_plain([*select_tests.PYTEST, "tests/test_sample_skips.py"], {"changed": []}, 0, {},
                                      held=set())
    return run


def test_a_selected_run_fails_on_an_unlisted_skip_and_passes_a_listed_one(plain_run, capsys):
    assert plain_run(LISTED) == 0
    assert plain_run(UNLISTED) == 1
    out = capsys.readouterr().out
    assert f"REFUSED SKIP (unlisted): {UNLISTED}" in out
    assert f"FAILED tests/test_sample_skips.py (exit skip policy): {UNLISTED}; log " in out
    assert plain_run() == 0


def test_a_selected_run_fails_on_the_skip_of_an_expired_row(plain_run, capsys):
    assert plain_run(EXPIRED) == 1
    assert f"REFUSED SKIP (expired): {EXPIRED}" in capsys.readouterr().out


def test_a_recorded_selected_run_fails_on_an_unlisted_skip(monkeypatch, tmp_path, capsys):
    """The path the runner's shards, the Mac and the VM take (select_tests.run_recorded): one report per unit."""
    unit = "tests/test_sample_skips.py"
    use_rows(monkeypatch)
    monkeypatch.setattr(select_tests.run_order, "state_path", lambda: tmp_path / "state.json")
    monkeypatch.setattr(select_tests.test_map, "working_tree_id", lambda: "f" * 40)
    monkeypatch.setattr(select_tests.test_map, "build_natives", lambda: None)
    monkeypatch.setattr(select_tests.test_map, "build_map", lambda results, commit: {})
    monkeypatch.setattr(select_tests.test_map, "write_map", lambda data, path: None)
    monkeypatch.setattr(select_tests.test_map, "tree_map_path", lambda tree: tmp_path / "map.json")
    monkeypatch.setattr(select_tests, "chunk_counts", lambda *args: {})
    monkeypatch.setattr(select_tests, "chunk_decisions", lambda *args: {})
    skipped: list[str] = []

    def record(ordered, work, jobs, maxfail, held):
        junit(work / (unit.replace("/", "__") + ".xml"), skipped)
        return {unit: {"exit": 0, "seconds": 0.1}}, {unit: []}
    monkeypatch.setattr(select_tests, "record_ordered", record)
    plan = {"selected": [unit], "map": None, "changed": []}
    skipped[:] = [LISTED]
    assert select_tests.run_recorded(plan, 1, held=set()) == 0
    skipped[:] = [UNLISTED]
    assert select_tests.run_recorded(plan, 1, held=set()) == 1
    assert f"FAILED {unit} (exit skip policy): {UNLISTED}; log " in capsys.readouterr().out
    skipped[:] = [EXPIRED]
    assert select_tests.run_recorded(plan, 1, held=set()) == 1


def gate_events(skipped: str) -> dict:
    selected = [f"tests/{name}::test_covered" for name in REQUIRED_FAMILIES] + [skipped]
    return {"collected": selected, "selected": selected, "deselected": [], "collection_reports": [],
            "tests": {node: {"outcome": "passed"} for node in selected[:-1]}
            | {skipped: {"outcome": "skipped", "reason": f"('{skipped}', 3, 'Skipped: {MESSAGE}')"}}}


@pytest.mark.parametrize("node, allowed", [(LISTED, True), (UNLISTED, False), (EXPIRED, False)],
                         ids=["listed", "unlisted", "expired row"])
def test_the_full_gate_refuses_an_unlisted_skip_and_an_expired_row(node, allowed):
    events = gate_events(node)
    result = {"counts": {}, "skips": [], "failures": []}
    gate.interpret_pytest(result, events, {"optional_tests": ROWS, "deselected_tests": []}, events["collected"])
    assert [skip["allowed"] for skip in result["skips"]] == [allowed]
    assert [failure["nodeid"] for failure in result["failures"] if failure["stage"] == "skip policy"] == \
        ([] if allowed else [node])
    if node == EXPIRED:
        assert "row for this skip expired" in result["failures"][0]["reason"]


def test_the_one_list_gives_every_row_a_reason_an_owner_and_an_expiry_day():
    from tools import skip_policy
    rows = skip_policy.load()
    assert rows == json.loads((ROOT / "tools/gate-optional.json").read_text())["optional_tests"]
    for row in rows:
        assert row["reason"].strip() and row["owner"].strip()
        datetime.date.fromisoformat(row["expires"])
    with pytest.raises(skip_policy.SkipPolicyError):
        skip_policy.validate({"optional_tests": [{"nodeid": LISTED, "reason": MESSAGE, "owner": "x"}]})
    with pytest.raises(skip_policy.SkipPolicyError):
        skip_policy.validate({"optional_tests": [{**ROWS[0], "expires": "next week"}]})


def test_a_row_applies_through_its_expiry_day():
    from tools import skip_policy
    row = {**ROWS[0], "expires": "2026-12-04"}
    assert skip_policy.verdict(LISTED, MESSAGE, [row], datetime.date(2026, 12, 4)) == "allowed"
    assert skip_policy.verdict(LISTED, MESSAGE, [row], datetime.date(2026, 12, 5)) == "expired"
    assert skip_policy.verdict(LISTED, "another reason", [row], datetime.date(2026, 12, 4)) == "unlisted"


def test_the_command_line_check_reads_junit_reports(tmp_path):
    """The checker a gate outside this repository can call on its own JUnit reports (exit 1: a refused skip)."""
    report = tmp_path / "report.xml"
    junit(report, ["tests/test_sample_skips.py::test_not_on_the_real_list"])
    done = subprocess.run([sys.executable, str(ROOT / "tools/skip_policy.py"), "junit", str(report)],
                          capture_output=True, text=True, check=False)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "REFUSED SKIP (unlisted): tests/test_sample_skips.py::test_not_on_the_real_list" in done.stdout
    junit(report, [])
    assert subprocess.run([sys.executable, str(ROOT / "tools/skip_policy.py"), "junit", str(report)],
                          capture_output=True, text=True, check=False).returncode == 0
