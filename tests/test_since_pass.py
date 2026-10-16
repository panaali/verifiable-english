"""Selection against the branch's last passing tree (tools/since_pass.py, test-speed batch B3): the rule's
choice of base, its step and age bounds, the shadow rows written beside each gate, the evidence check that
recomputes every row, and the activation that keeps today's merge base until the evidence holds.

Every repository is a synthetic one under tmp_path; the planner is a stand-in that returns fixed plans, so
no test runs the selector on this checkout except `test_plan_between_is_the_select_tests_base_plan`."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import since_pass  # noqa: E402
from since_pass import Pass, RecordError  # noqa: E402

NOW = datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc)
STAGES = ["toolchains", "lean_build", "lean_audit", "rust_build", "cargo_test", "pytest"]
# The stand-in plans: the rule's selection is one file, today's two of the three units.
SINCE = {"selected": ["tests/test_a.py"], "full": False, "full_reasons": [], "map": None, "full_count": 3}
TODAY = {"selected": ["tests/test_a.py", "tests/test_b.py"], "full": False, "full_reasons": [], "map": None,
         "full_count": 3}


def git(repository, *args):
    return subprocess.run(["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid",
                           "-c", "commit.gpgsign=false", *args], cwd=repository, check=True, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT).stdout.strip()


class Repository:
    """A git repository whose `main` has one commit, the merge base of every branch made here."""

    def __init__(self, path: Path):
        self.path = path
        path.mkdir()
        git(path, "init", "-q", "-b", "main")
        self.counter = 0
        self.base = self.commit("base")

    def commit(self, message="change") -> str:
        self.counter += 1
        (self.path / f"file{self.counter}.txt").write_text(f"{self.counter}\n")
        git(self.path, "add", "-A")
        git(self.path, "commit", "-q", "-m", message)
        return self.head()

    def head(self) -> str:
        return git(self.path, "rev-parse", "HEAD")

    def tree(self, commit="HEAD") -> str:
        return git(self.path, "rev-parse", f"{commit}^{{tree}}")

    def branch(self, name, start="main"):
        git(self.path, "checkout", "-q", "-b", name, start)

    def checkout(self, name):
        git(self.path, "checkout", "-q", name)


@pytest.fixture
def repo(tmp_path):
    return Repository(tmp_path / "repository")


def a_pass(repo, commit, *, at=NOW - timedelta(hours=1), item="item", status="passed", mode="full") -> Pass:
    return Pass(item, "b", commit, repo.tree(commit), status, mode, at, "0" * 64)


def records(tmp_path, *passes, extra=()) -> Path:
    path = tmp_path / "gate-records.jsonl"
    with path.open("a") as handle:
        for line in extra:
            handle.write(line + "\n")
        for found in passes:
            handle.write(json.dumps(found.row()) + "\n")
    return path


def result(repo, status="passed", failures=(), mode="full", **changes) -> dict:
    record = {"commit_sha": repo.head(), "tree_sha": repo.tree(), "dirty": False, "mode": mode,
              "stages": list(STAGES), "status": status, "failures": [dict(failure) for failure in failures],
              "counts": {}}
    record.update(changes)
    return record


def planner(repo, calls=None, since=SINCE, today=TODAY):
    """A stand-in for `plan_between`: the rule's plan for a pass base, today's for the merge base."""
    def plan(base, head):
        if calls is not None:
            calls.append((base, head))
        return dict(today if base == git(repo.path, "merge-base", head, "main") else since)
    return plan


def shadow(repo, tmp_path, *, item, records_path, status="passed", failures=(), calls=None, now=NOW,
           since=SINCE, today=TODAY):
    return since_pass.after_gate(repo.path, result(repo, status, failures), records=records_path,
                                 shadow=tmp_path / "shadow.jsonl", item=item, now=now,
                                 planner=planner(repo, calls, since, today))


# --- the rule ---------------------------------------------------------------------------------------------

def test_without_a_pass_the_base_is_todays_merge_base(repo):
    repo.branch("b")
    repo.commit()
    decision = since_pass.choose(repo.path, [], now=NOW)
    assert decision["rule"] == "merge-base" and decision["base"] == repo.base == decision["merge_base"]


def test_the_pass_closest_to_head_is_the_base(repo):
    repo.branch("b")
    first = repo.commit()
    second = repo.commit()
    repo.commit()
    decision = since_pass.choose(repo.path, [a_pass(repo, second, at=NOW - timedelta(hours=3)),
                                             a_pass(repo, first, at=NOW - timedelta(hours=1))], now=NOW)
    assert decision["rule"] == "since-pass" and decision["base"] == second and decision["steps"] == 1


def test_a_pass_outside_the_branchs_history_since_the_merge_base_is_not_a_base(repo):
    # A sibling branch from the same main commit, and a commit of this branch after HEAD (HEAD reset back):
    # both descend from the merge base, neither is an ancestor of HEAD.
    repo.branch("other")
    sibling = repo.commit()
    repo.branch("b", "main")
    repo.commit()
    ahead = repo.commit()
    git(repo.path, "reset", "-q", "--hard", "HEAD~1")
    decision = since_pass.choose(repo.path, [a_pass(repo, sibling), a_pass(repo, ahead)], now=NOW)
    assert decision["rule"] == "merge-base" and decision["base"] == repo.base


def test_a_pass_of_main_before_the_merge_base_is_not_a_base(repo):
    # The merge base itself is where the branch starts (allowed); an older main commit is not.
    older = repo.base
    git(repo.path, "checkout", "-q", "main")
    newer_main = repo.commit()
    repo.branch("c", newer_main)
    repo.commit()
    decision = since_pass.choose(repo.path, [a_pass(repo, older)], now=NOW)
    assert decision["rule"] == "merge-base" and decision["base"] == newer_main
    decision = since_pass.choose(repo.path, [a_pass(repo, older), a_pass(repo, newer_main)], now=NOW)
    assert decision["rule"] == "since-pass" and decision["base"] == newer_main


def test_a_row_whose_tree_is_not_its_commits_or_whose_commit_is_absent_is_not_a_base(repo):
    repo.branch("b")
    passed = repo.commit()
    repo.commit()
    wrong_tree = Pass("item", "b", passed, repo.tree("main"), "passed", "full", NOW, "0" * 64)
    absent = Pass("item", "b", "f" * 40, repo.tree(), "passed", "full", NOW, "0" * 64)
    assert since_pass.choose(repo.path, [wrong_tree, absent], now=NOW)["rule"] == "merge-base"


@pytest.mark.parametrize("commits, rule", [(since_pass.MAX_STEPS, "since-pass"),
                                           (since_pass.MAX_STEPS + 1, "merge-base")])
def test_more_than_max_steps_since_the_pass_forces_todays_base(repo, commits, rule):
    repo.branch("b")
    passed = repo.commit()
    for _ in range(commits):
        repo.commit()
    decision = since_pass.choose(repo.path, [a_pass(repo, passed)], now=NOW)
    assert decision["rule"] == rule and decision["steps"] == commits
    assert decision["forced"] == (None if rule == "since-pass" else "steps")
    assert decision["base"] == (passed if rule == "since-pass" else repo.base)


def test_a_sync_merge_is_one_step_and_moves_the_merge_base_past_the_pass(repo):
    repo.branch("b")
    passed = repo.commit()
    repo.commit()
    git(repo.path, "checkout", "-q", "main")
    for _ in range(since_pass.MAX_STEPS + 2):
        repo.commit()
    repo.checkout("b")
    git(repo.path, "merge", "-q", "--no-edit", "main")
    assert since_pass.first_parent_steps(repo.path, passed, repo.head()) == 2
    # After the sync the pass precedes the new merge base: today's base, not the pass.
    decision = since_pass.choose(repo.path, [a_pass(repo, passed)], now=NOW)
    assert decision["rule"] == "merge-base" and decision["base"] == git(repo.path, "rev-parse", "main")


@pytest.mark.parametrize("age, rule", [(timedelta(hours=24), "since-pass"),
                                       (timedelta(hours=24, seconds=1), "merge-base"),
                                       (timedelta(seconds=-1), "merge-base")])
def test_a_pass_older_than_a_day_or_in_the_future_forces_todays_base(repo, age, rule):
    repo.branch("b")
    passed = repo.commit()
    repo.commit()
    decision = since_pass.choose(repo.path, [a_pass(repo, passed, at=NOW - age)], now=NOW)
    assert decision["rule"] == rule and decision["forced"] == (None if rule == "since-pass" else "age")


# --- the records ------------------------------------------------------------------------------------------

def test_a_rerun_that_passed_is_a_pass_and_a_failed_gate_is_not(repo, tmp_path):
    repo.branch("b")
    passed = repo.commit()
    rerun = a_pass(repo, passed, status="rerun-passed", mode="rerun-failed")
    failed = {**rerun.row(), "status": "failed", "mode": "full"}
    path = records(tmp_path, rerun, extra=[json.dumps(failed), '{"loop": "x", "round": 1}', "not json"])
    passes, malformed = since_pass.read_passes(path)
    assert passes == [rerun] and len(malformed) == 1 and "not a pass" in malformed[0]


def test_a_merge_train_row_with_a_gate_key_is_another_writers_row(repo, tmp_path):
    # merge-train.sh writes {"train": ..., "gate": "R2", ...}: neither a pass nor a malformed gate row.
    repo.branch("b")
    passed = a_pass(repo, repo.commit())
    train = {"train": "t1", "branch": "b", "candidate": passed.commit, "integration": passed.commit,
             "verify": "PASS", "gate": "R2", "legs": "a,b"}
    passes, malformed = since_pass.read_passes(records(tmp_path, passed, extra=[json.dumps(train)]))
    assert passes == [passed] and malformed == []


@pytest.mark.parametrize("key, value", [
    ("gate", 7), ("gate", ""), ("branch", True), ("commit", "f" * 39), ("commit", "F" * 40), ("tree", None),
    ("status", "passed "), ("mode", []), ("t", "2026-10-14 12:00:00"), ("t", 1760000000),
    ("result_sha256", "0" * 63), ("extra", 1), ("t", None)])
def test_a_gate_row_with_a_wrong_field_is_refused(repo, key, value):
    row = a_pass(repo, repo.base).row()
    row[key] = value
    with pytest.raises(RecordError):
        since_pass.pass_row(row)


def test_a_gate_row_missing_a_field_is_refused(repo):
    for key in since_pass.PASS_KEYS:
        row = a_pass(repo, repo.base).row()
        del row[key]
        with pytest.raises(RecordError):
            since_pass.pass_row(row)


# --- after a gate -----------------------------------------------------------------------------------------

def test_after_gate_writes_the_shadow_row_against_earlier_passes_then_records_its_pass(repo, tmp_path):
    repo.branch("b")
    first = repo.commit()
    path = tmp_path / "gate-records.jsonl"
    calls = []
    done = shadow(repo, tmp_path, item="x", records_path=path, calls=calls)
    # The first gate has no earlier pass: today's base, no plans; its own pass is recorded after its row.
    rows = since_pass.read_jsonl(tmp_path / "shadow.jsonl")
    assert rows[0]["decision"]["rule"] == "merge-base" and calls == [] and rows[0]["counted"] is False
    assert [found.commit for found in since_pass.read_passes(path)[0]] == [first]
    assert any("recorded the pass" in line for line in done)
    second = repo.commit()
    failures = [{"stage": "pytest", "nodeid": "tests/test_b.py::test_x", "reason": "boom"},
                {"stage": "pytest command", "reason": "Python suite: exit 1"}]
    shadow(repo, tmp_path, item="x", records_path=path, status="failed", failures=failures, calls=calls)
    row = since_pass.read_jsonl(tmp_path / "shadow.jsonl")[1]
    assert calls == [(first, second), (repo.base, second)]
    assert row["decision"]["rule"] == "since-pass" and row["decision"]["base"] == first
    assert row["outside"]["since_pass"] == [{"stage": "pytest", "nodeid": "tests/test_b.py::test_x"}]
    assert row["outside"]["merge_base"] == [] and row["counted"] is True and row["units"] == 3
    # A failed gate is not a pass.
    assert [found.commit for found in since_pass.read_passes(path)[0]] == [first]


def test_after_gate_twice_on_one_commit_writes_nothing_new(repo, tmp_path):
    repo.branch("b")
    repo.commit()
    path = tmp_path / "gate-records.jsonl"
    shadow(repo, tmp_path, item="x", records_path=path)
    done = shadow(repo, tmp_path, item="x", records_path=path)
    assert len(since_pass.read_jsonl(tmp_path / "shadow.jsonl")) == 1 and len(since_pass.read_jsonl(path)) == 1
    assert any("already" in line for line in done)


@pytest.mark.parametrize("changes", [{"commit_sha": "0" * 40}, {"tree_sha": "0" * 40}, {"dirty": True},
                                     {"dirty": None}, {"stages": "pytest"}])
def test_after_gate_refuses_a_record_not_of_this_clean_head(repo, tmp_path, changes):
    repo.branch("b")
    repo.commit()
    path = tmp_path / "gate-records.jsonl"
    with pytest.raises(RecordError):
        since_pass.after_gate(repo.path, result(repo, **changes), records=path, shadow=tmp_path / "shadow.jsonl",
                              item="x", now=NOW, planner=planner(repo))
    assert not path.exists() and not (tmp_path / "shadow.jsonl").exists()


def test_a_rerun_records_a_pass_but_no_shadow_row(repo, tmp_path):
    repo.branch("b")
    repo.commit()
    path = tmp_path / "gate-records.jsonl"
    record = result(repo, "rerun-passed", mode="rerun-failed")
    since_pass.after_gate(repo.path, record, records=path, shadow=tmp_path / "shadow.jsonl", item="x", now=NOW,
                          planner=planner(repo))
    assert not (tmp_path / "shadow.jsonl").exists()
    assert [(found.status, found.mode) for found in since_pass.read_passes(path)[0]] == [("rerun-passed",
                                                                                           "rerun-failed")]


@pytest.mark.parametrize("failures, plan, expected", [
    ([{"stage": "pytest", "nodeid": "tests/test_a.py::t"}], SINCE, []),
    ([{"stage": "pytest", "nodeid": "tests/test_b.py::t"}], SINCE, [{"stage": "pytest", "nodeid": "tests/test_b.py::t"}]),
    ([{"stage": "skip policy", "nodeid": "tests/test_c.py::t"}], SINCE,
     [{"stage": "skip policy", "nodeid": "tests/test_c.py::t"}]),
    ([{"stage": "pytest", "nodeid": "tests/test_a.py::t"}, {"stage": "pytest command"}], SINCE, []),
    ([{"stage": "pytest command"}], SINCE, [{"stage": "pytest command"}]),
    ([{"stage": "coverage"}], SINCE, []),
    ([{"stage": "gate"}], SINCE, [{"stage": "gate"}]),
    ([{"stage": "gate"}, {"stage": "pytest", "nodeid": "tests/test_c.py::t"}],
     {**SINCE, "full": True, "full_reasons": ["uv.lock"]}, []),
])
def test_a_failure_is_outside_a_selection_unless_its_file_is_selected(failures, plan, expected):
    assert since_pass.outside(failures, plan) == expected


def test_coverage_failures_are_listed_as_gate_only():
    failures = [{"stage": "coverage"}, {"stage": "source identity"}, {"stage": "pytest", "nodeid": "tests/x.py::t"}]
    assert since_pass.gate_only(failures) == failures[:2]


# --- evidence and activation ------------------------------------------------------------------------------

def evidence(repo, tmp_path, items: int, *, miss: bool = False, since=SINCE) -> Path:
    """Shadow rows of `items` items, each a passing gate then a second gate on its own branch."""
    path = tmp_path / "gate-records.jsonl"
    for number in range(items):
        repo.branch(f"item{number}", "main")
        repo.commit()
        shadow(repo, tmp_path, item=f"item{number}", records_path=path, now=NOW - timedelta(hours=2))
        repo.commit()
        failures = [{"stage": "pytest", "nodeid": "tests/test_c.py::t"}] if miss and number == 0 else []
        shadow(repo, tmp_path, item=f"item{number}", records_path=path, failures=failures,
               status="failed" if failures else "passed", since=since)
    return tmp_path / "shadow.jsonl"


def test_ten_items_without_a_miss_activate_the_rule_and_base_prints_the_pass(repo, tmp_path, capsys):
    rows = evidence(repo, tmp_path, since_pass.ACTIVATION_ITEMS)
    verdict = since_pass.check(repo.path, rows)
    assert verdict["active"] and len(verdict["items"]) == since_pass.ACTIVATION_ITEMS and verdict["rows"] == 20
    head = repo.head()
    repo.commit()
    path = tmp_path / "gate-records.jsonl"
    code = since_pass.main(["base", "--records", str(path), "--evidence", str(rows)], root=repo.path, now=NOW)
    assert code == 0 and capsys.readouterr().out.strip() == head


@pytest.mark.parametrize("items, miss", [(since_pass.ACTIVATION_ITEMS - 1, False), (since_pass.ACTIVATION_ITEMS, True),
                                         (0, False)])
def test_fewer_items_or_a_miss_keeps_todays_base(repo, tmp_path, capsys, items, miss):
    rows = evidence(repo, tmp_path, items, miss=miss)
    assert not since_pass.check(repo.path, rows)["active"]
    if not items:
        repo.branch("solo")
    repo.commit()
    code = since_pass.main(["base", "--records", str(tmp_path / "gate-records.jsonl"), "--evidence", str(rows)],
                           root=repo.path, now=NOW)
    assert code == 0 and capsys.readouterr().out.strip() == repo.base
    assert since_pass.main(["check", "--evidence", str(rows)], root=repo.path) == (1 if miss else 0)


def test_rows_whose_rule_selected_everything_do_not_count(repo, tmp_path):
    rows = evidence(repo, tmp_path, since_pass.ACTIVATION_ITEMS,
                    since={**SINCE, "selected": ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"],
                           "full": True, "full_reasons": ["missing coverage map"]})
    verdict = since_pass.check(repo.path, rows)
    assert verdict["items"] == [] and not verdict["active"]


def test_one_branch_under_ten_labels_is_one_item(repo, tmp_path):
    path = tmp_path / "gate-records.jsonl"
    repo.branch("one")
    repo.commit()
    shadow(repo, tmp_path, item="one", records_path=path, now=NOW - timedelta(hours=2))
    for number in range(since_pass.ACTIVATION_ITEMS):
        repo.commit()
        shadow(repo, tmp_path, item=f"one-c{number}", records_path=path)
    verdict = since_pass.check(repo.path, tmp_path / "shadow.jsonl")
    assert verdict["items"] == ["one"] and verdict["rows"] == since_pass.ACTIVATION_ITEMS + 1
    assert not verdict["active"]


def test_a_detached_head_row_is_not_evidence(repo, tmp_path):
    path = tmp_path / "gate-records.jsonl"
    repo.branch("one")
    repo.commit()
    shadow(repo, tmp_path, item="one", records_path=path, now=NOW - timedelta(hours=2))
    repo.commit()
    git(repo.path, "checkout", "-q", "--detach")
    shadow(repo, tmp_path, item="one", records_path=path)
    row = since_pass.read_jsonl(tmp_path / "shadow.jsonl")[1]
    assert row["branch"] == "HEAD" and row["decision"]["rule"] == "since-pass" and row["counted"] is False


def test_a_long_row_and_a_short_one_are_each_appended_as_one_whole_line(tmp_path):
    path = tmp_path / "rows.jsonl"
    big = {"selected": [f"tests/test_{number:04d}.py" for number in range(2000)]}
    for _ in range(3):
        since_pass.append(path, big)
        since_pass.append(path, {"gate": "x"})
    assert [json.loads(line) for line in path.read_text().splitlines()] == [big, {"gate": "x"}] * 3


def mutate(row: dict, path: str, value) -> dict:
    row = json.loads(json.dumps(row))
    *parents, last = path.split(".")
    target = row
    for key in parents:
        target = target[key]
    if value is DELETE:
        del target[last]
    else:
        target[last] = value
    return row


DELETE = object()
MUTATIONS = [
    ("format", "ve-since-pass-shadow@2"), ("item", 7), ("item", ""), ("commit", "f" * 40), ("tree", "f" * 40),
    ("t", "yesterday"), ("units", True), ("units", 0), ("gate.status", "passed"), ("gate.mode", "rerun-failed"),
    ("gate.stages", ["toolchains"]), ("gate.result_sha256", None), ("gate.failures", []),
    ("gate.failures", [{"stage": 7}]), ("gate.failures", [{"stage": "pytest", "nodeid": "tests/test_a.py::t"}]), ("decision.rule", "since"), ("decision.steps", 2),
    ("decision.steps", True), ("decision.base", "f" * 40), ("decision.forced", "age"), ("decision.pass", None),
    ("decision.pass.t", "2026-10-12T00:00:00Z"), ("decision.pass.status", "failed"),
    ("decision.merge_base", "f" * 40), ("since_pass", None), ("since_pass.full", 0),
    ("since_pass.selected", ["tests/test_b.py", "tests/test_a.py"]), ("since_pass.selected", [7]),
    ("since_pass.full_reasons", ["requested"]), ("since_pass.map", "main"), ("merge_base_plan", {}),
    ("outside.since_pass", []), ("outside.gate_only", [{"stage": "coverage"}]), ("counted", False),
    ("counted", 1), ("extra", True)]
DELETIONS = ["item", "gate", "decision.pass", "since_pass.map", "outside", "counted", "gate.failures"]


@pytest.mark.parametrize("path, value", MUTATIONS + [(path, DELETE) for path in DELETIONS],
                         ids=[f"{path}={value!r}" for path, value in MUTATIONS] + [f"del {path}" for path in DELETIONS])
def test_check_refuses_every_retyped_rebound_or_dropped_field(repo, tmp_path, path, value):
    rows = evidence(repo, tmp_path, 1, miss=True)
    lines = rows.read_text().splitlines()
    since_pass.check(repo.path, rows)  # the genuine rows pass
    row = json.loads(lines[1])
    assert row["decision"]["rule"] == "since-pass" and row["gate"]["failures"]
    lines[1] = json.dumps(mutate(row, path, value))
    rows.write_text("\n".join(lines) + "\n")
    with pytest.raises(RecordError):
        since_pass.check(repo.path, rows)
    assert not since_pass.activation(repo.path, rows)[0]


def test_check_refuses_a_duplicated_row_and_a_line_that_is_not_json(repo, tmp_path):
    rows = evidence(repo, tmp_path, 1)
    lines = rows.read_text().splitlines()
    for broken in ([*lines, lines[1]], [*lines, "{"]):
        rows.write_text("\n".join(broken) + "\n")
        with pytest.raises(RecordError):
            since_pass.check(repo.path, rows)


# --- the real planner -------------------------------------------------------------------------------------

def test_plan_between_is_the_select_tests_base_plan(monkeypatch):
    import select_tests
    calls = []
    monkeypatch.setattr(select_tests, "select", lambda paths, **options: calls.append((paths, options)) or {})
    base = git(ROOT, "rev-parse", "HEAD~1")
    head = git(ROOT, "rev-parse", "HEAD")
    since_pass.plan_between(base, head)
    expected = git(ROOT, "diff", "--no-renames", "--name-only", f"{base}...{head}").splitlines()
    assert calls == [(expected, {"base": base, "after": head, "coverage": "auto"})]
