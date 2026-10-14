"""arch-AR-4 review F2: AR-4 moves the per-file trust tables out of the tree and into the gate record
(`tools/trust_map.py --files`), but no gate wrote them. Every gate, full or a rerun, now records them, checked
by their writer's schema (`trust_map.files_problems`); missing or malformed counts fail the gate."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from test_gate_integrity import trust_counts
from test_gate_rerun import fake  # noqa: F401  (the fixture)
from tools import batch_evidence, gate


def test_every_gate_records_the_per_file_trust_counts(fake):
    """A full gate and a rerun both record what `tools/trust_map.py --files` measured."""
    code, record = fake.run()
    assert code == 1 and record["trust"] == trust_counts() and gate.TRUST_STAGE in fake.stages()
    fake.failing = set()
    code, record = fake.run("--rerun-failed")
    assert (code, record["status"], record["trust"]) == (0, "rerun-passed", trust_counts())
    code, record = fake.run()
    assert (code, record["status"], record["trust"]) == (0, "passed", trust_counts())


def _counts(change):
    counts = trust_counts()
    change(counts)
    return counts


@pytest.mark.parametrize("counts", [
    False, {}, [], 0, {**trust_counts(), "files": {}}, {**trust_counts(), "extra": 1},
    _counts(lambda c: c["files"]["VE/Demo.lean"].update(C=True)),
    _counts(lambda c: c["files"]["VE/Demo.lean"].update(C=-1)),
    _counts(lambda c: c["files"]["VE/Demo.lean"].pop("trusted")),
    _counts(lambda c: c["files"]["VE/Demo.lean"].update(trusted=4)),
    _counts(lambda c: c["budget"].update(V=1)),
    _counts(lambda c: c["budget"].update(K=0.0)),  # PROBE F6: numeric equality is not type validation
    _counts(lambda c: c["budget"].update(S=False)),
    _counts(lambda c: c["totals"].update(C=3.0)),
    _counts(lambda c: c["totals"].update(o=True)),
    _counts(lambda c: c["totals"].pop("lines")),
    _counts(lambda c: c["budget"].update(extra=0)),
    _counts(lambda c: c["files"].update({"VE/Demo.py": dict(c["files"]["VE/Demo.lean"])})),
], ids=["not-written", "empty", "list", "zero", "no-files", "extra-key", "bool-count", "negative-count",
        "missing-count", "totals-disagree", "budget-disagrees", "review-f6-float-budget", "bool-budget",
        "float-total", "bool-total", "missing-total", "extra-budget", "not-a-lean-file"])
def test_a_gate_without_valid_trust_counts_fails(fake, counts):
    fake.failing, fake.trust = set(), counts
    code, record = fake.run()
    assert (code, record["status"]) == (1, "failed") and "trust" not in record
    assert any(failure["reason"].startswith(gate.TRUST_STAGE) for failure in record["failures"])


# arch-AR-4 recheck F7: a reader of a gate record (`docs/arch/AR-4/report.py --check --gate`) crashed on a malformed
# one. Every reader checks it with the shared checks of `tools/batch_evidence.py`, which refuse any value.

SHA = "a" * 40
DEEP: list = []
for _ in range(10_000):
    DEEP = [DEEP]


def _sha(value):
    """`value` with the fake gate's commit id replaced by a full one."""
    return json.loads(json.dumps(value).replace('"commit-1"', f'"{SHA}"'))


def _records(fake) -> tuple[dict, dict, dict]:
    """A failed full gate, its R13 rerun and a passed full gate, as `tools/gate.py` writes them."""
    assert fake.run()[0] == 1
    failed = _sha(json.loads(fake.output.read_text()))
    fake.failing = set()
    rerun = _sha(fake.run("--rerun-failed")[1])
    passed = _sha(fake.run()[1])
    return failed, rerun, passed


def _checks(failed, rerun, passed) -> dict[str, list[str]]:
    budget = trust_counts()["budget"]
    return {"passed": batch_evidence.gate_record_problems(SHA, passed)
            + batch_evidence.gate_trust_problems(passed, budget),
            "pair": batch_evidence.rerun_pair_problems(failed, rerun)
            + batch_evidence.gate_trust_problems(failed, budget) + batch_evidence.gate_trust_problems(rerun, budget)}


def _nodes(value, path=()):
    yield path
    items = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, item in items:
        yield from _nodes(item, (*path, key))


def _replace(record, path, new):
    record = copy.deepcopy(record)
    if not path:
        return new
    node = record
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = new
    return record


def test_genuine_gate_records_pass_the_shared_checks(fake):
    failed, rerun, passed = _records(fake)
    assert _checks(failed, rerun, passed) == {"passed": [], "pair": []}
    budget = trust_counts()["budget"]
    assert batch_evidence.gate_trust_problems(passed, {**budget, "V": budget["V"] + 1})  # counts of another tree


def test_review_f8_bare_mutants_array_reaches_report_check(monkeypatch):
    """PROBE F8: the shared mutant validator accepts a bare array; rendering must read the same rows."""
    path = Path(__file__).resolve().parents[1] / "docs/arch/AR-4/report.py"
    spec = importlib.util.spec_from_file_location("ar4_report_f8", path)
    assert spec and spec.loader
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    original = report.load
    expected = report.main(["--check"])
    monkeypatch.setattr(report, "load", lambda p: original(p)["mutants"] if p.name == "mutants.json" else original(p))
    assert report.main(["--check"]) == expected


def test_review_f9_r13_requires_complete_full_and_nonempty_rerun_counts(fake):
    """PROBE F9, with genuine gate records: missing, retyped and inconsistent counts cannot invoke R13."""
    failed, rerun, passed = _records(fake)
    assert batch_evidence.rerun_pair_problems(failed, rerun) == []
    for record, field in ((failed, "full"), (rerun, "rerun")):
        for key in ("passed", "skipped", "failed", "selected", "deselected", "collected"):
            mutant = copy.deepcopy(record)
            mutant["counts"].pop(key)
            pair = (mutant, rerun) if field == "full" else (failed, mutant)
            assert batch_evidence.rerun_pair_problems(*pair), (field, key)
            mutant = copy.deepcopy(record)
            mutant["counts"][key] = False
            pair = (mutant, rerun) if field == "full" else (failed, mutant)
            assert batch_evidence.rerun_pair_problems(*pair), (field, key)
        mutant = copy.deepcopy(record)
        mutant["counts"]["collected"] += 1
        pair = (mutant, rerun) if field == "full" else (failed, mutant)
        assert batch_evidence.rerun_pair_problems(*pair), field
    empty = copy.deepcopy(rerun)
    empty["counts"].update(passed=0, selected=0, collected=0)
    assert batch_evidence.rerun_pair_problems(failed, empty)
    incomplete = copy.deepcopy(failed)
    incomplete["counts"] = {"failed": 1}
    assert batch_evidence.rerun_pair_problems(incomplete, empty)


@pytest.mark.parametrize("record", [{}, [], None, 7, True, "gate", DEEP])
def test_review_f7_probe_a_malformed_gate_record_is_refused(fake, record):
    """PROBE F7: `{}` as the full gate record; every check refuses it with a message naming the gate."""
    failed, rerun, passed = _records(fake)
    for problems in (*_checks(record, rerun, record).values(), _checks(failed, record, passed)["pair"]):
        assert problems and all("gate" in problem or "rerun" in problem for problem in problems)


# The fields each check reads: a value of another type there is refused (the rest, such as `environment`, is not
# read).
READ = {"passed": ("commit_sha", "status", "dirty", "stages", "failures", "trust", *(
    ("counts", key) for key in ("passed", "skipped", "failed", "selected", "deselected", "collected", "rust_passed"))),
    "full": ("commit_sha", "tree_sha", "status", "dirty", "stages", ("failures", None, "stage"),
             ("failures", None, "nodeid"), ("counts", "failed"), "trust"),
    "rerun": ("commit_sha", "tree_sha", "status", "dirty", "failures", "trust", ("rerun_failed", "tests"),
              ("rerun_failed", "outcomes"), ("rerun_failed", "previous", "commit_sha"),
              ("rerun_failed", "previous", "tree_sha"), ("counts", "passed"), ("counts", "selected"))}
# Containers a check reads only to reach the fields above: replacing the container itself is refused.
CONTAINERS = {"passed": {("counts",)}, "full": {("failures",), ("failures", None), ("counts",)},
              "rerun": {("rerun_failed",), ("rerun_failed", "previous"), ("counts",)}}


def _read(path, which) -> bool:
    """Whether a check reads the node at `path`: a field of `READ` or below it, or a container of `CONTAINERS`
    (None stands for any list index)."""
    def at(field, exact):
        return (len(path) == len(field) if exact else len(path) >= len(field)) and all(
            f is None or f == p for f, p in zip(field, path))
    return any(at(field if isinstance(field, tuple) else (field,), False) for field in READ[which]) or any(
        at(field, True) for field in CONTAINERS[which])


def test_every_retyped_node_of_a_gate_record_is_a_problem_never_a_crash(fake):
    """Type confusion over genuine records: each node becomes 7, true, null, [], {}, a string or a list nested
    10,000 deep. No check raises, and a field a check reads is refused with a value of another type."""
    failed, rerun, passed = _records(fake)
    for which, record in (("passed", passed), ("full", failed), ("rerun", rerun)):
        for path in list(_nodes(record)):
            for new in (7, True, None, [], {}, "x", DEEP):
                old = _replace(record, path, new)
                if json.dumps(old, default=str) == json.dumps(record):
                    continue
                sides = {"passed": (failed, rerun, old), "full": (old, rerun, passed), "rerun": (failed, old, passed)}
                checked = _checks(*sides[which])
                value = record
                for key in path:
                    value = value[key]
                if _read(path, which) and type(new) is not type(value) or not path:
                    assert checked["passed" if which == "passed" else "pair"], (which, path, new)
