"""A mutant renumbered by an inserted one is paired by its text, not refused as a removed test; a mutant whose
text is gone stays refused (tools/gate_collection.py, `CASES_HOOK`; row gate-mutant-id-renumber)."""
from __future__ import annotations

import json

import pytest

from tests.test_gate_collection import commit, compare, gate_events, git
from tools import gate, gate_collection

# Each case is named by its definition and its position, as tests/test_packs_guard_mutants.py names them.
MODULE = """import json, pathlib, pytest
MUTANTS = json.loads(pathlib.Path(__file__).with_name("mutants.json").read_text())
IDS = [f"{name}-{i}" for i, (name, _, _) in enumerate(MUTANTS)]
{hook}
@pytest.mark.parametrize("name,find,replace", MUTANTS, ids=IDS)
def test_mutant(name, find, replace): pass
"""
HOOK = """def mutant_cases():
    return {nodeid: json.dumps(mutant) for nodeid, mutant in zip(IDS, MUTANTS)}
"""
BASE = [["a", "x", "y"], ["b", "x", "y"], ["c", "x", "y"], ["d", "x", "y"]]
INSERTED = [BASE[0], ["new", "x", "y"], *BASE[1:]]
CASE = "tests/test_m.py::test_mutant[{}]"


def files(mutants, hook=HOOK):
    return {"pytest.ini": "[pytest]\n", "tests/test_m.py": MODULE.replace("{hook}", hook),
            "tests/mutants.json": json.dumps(mutants)}


@pytest.fixture
def repository(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    git(repository, "init", "-q", "-b", "main")
    return repository


def test_an_inserted_mutant_shifts_three_ids_and_each_is_paired_by_its_text(repository):
    base = commit(repository, files(BASE))
    verdict = compare(repository, base, commit(repository, files(INSERTED)))
    assert verdict.paired == {CASE.format("b-1"): CASE.format("b-2"), CASE.format("c-2"): CASE.format("c-3"),
                              CASE.format("d-3"): CASE.format("d-4")}
    assert not verdict.failed() and verdict.refused == {} and verdict.removed == {}
    assert gate_collection.pairing_text(verdict).splitlines()[0] == \
        f"renumbered: {CASE.format('b-1')} -> {CASE.format('b-2')}"


def test_the_worktree_side_is_paired_from_its_files(repository):
    base = commit(repository, files(BASE))
    expected = gate_collection.collect(repository)
    commit(repository, files(INSERTED))
    verdict = gate_collection.missing(expected, gate_collection.collect(repository),
                                      gate_collection.changes(base, None, root=repository))
    assert len(verdict.paired) == 3 and not verdict.failed()


# Each head loses a base mutant's text (most also insert one): every lost ID of the function stays refused.
SAME = [["a", "x", "1"], ["a", "x", "2"], ["a", "x", "3"]]
GONE = {
    "text-changed": (BASE, [BASE[0], ["new", "x", "y"], BASE[1], ["c", "x", "z"], BASE[3]], ("b-1", "c-2", "d-3")),
    "case-deleted": (BASE, [BASE[0], ["new", "x", "y"], BASE[1], BASE[3]], ("b-1", "c-2")),
    # `a-0` keeps its ID with another text; the lost `a-2`'s text is at `a-1`, but `a-0`'s first text is gone.
    "kept-id-reused": (SAME, SAME[1:], ("a-2",)),
}


@pytest.mark.parametrize("before, after, refused", GONE.values(), ids=GONE)
def test_a_mutant_whose_text_is_gone_stays_refused(repository, before, after, refused):
    base = commit(repository, files(before))
    verdict = compare(repository, base, commit(repository, files(after)))
    assert verdict.paired == {} and set(verdict.refused) == {CASE.format(n) for n in refused}


def test_a_module_without_the_hook_on_a_side_pairs_nothing(repository):
    base = commit(repository, files(BASE, hook=""))
    verdict = compare(repository, base, commit(repository, files(INSERTED)))
    assert verdict.paired == {} and set(verdict.refused) == {CASE.format(n) for n in ("b-1", "c-2", "d-3")}


@pytest.mark.parametrize("base, head, pairs", [
    ({"b-1": "B", "c-2": "C"}, {"n-1": "N", "b-2": "B", "c-3": "C"}, {"b-1": "b-2", "c-2": "c-3"}),
    # A kept ID whose text changed still needs a head case with its old text.
    ({"x-0": "A", "x-1": "B", "x-2": "C"}, {"x-0": "B", "x-1": "C"}, {}),
    ({"x-0": "A", "x-1": "A"}, {"y-0": "A"}, {}),  # two base cases, one head case: one is removed
    ({"x-0": "A", "x-1": "A"}, {"y-0": "A", "y-1": "A"}, {"x-0": "y-0", "x-1": "y-1"}),
])
def test_pairing_is_by_text_one_head_case_each(base, head, pairs):
    assert gate_collection.pair_cases(base, head) == pairs


def test_a_trailer_still_records_a_lost_id_before_any_pairing(repository):
    base = commit(repository, files(BASE))
    commit(repository, files(INSERTED))
    git(repository, "commit", "-q", "--allow-empty", "-m",
        f"x\n\n{gate_collection.TRAILER}: {CASE.format('b-1')}{gate_collection.SEPARATOR}renumbered")
    verdict = compare(repository, base, git(repository, "rev-parse", "HEAD"))
    assert set(verdict.removed) == {CASE.format("b-1")} and set(verdict.paired) == {CASE.format(n) for n in
                                                                                   ("c-2", "d-3")}


def test_the_gate_logs_the_pairing_table_and_records_it(capsys):
    paired = {CASE.format("b-1"): CASE.format("b-2")}
    diff = gate_collection.Changes("b" * 40, "h" * 40, {})
    diff.renumbered = lambda expected, collected, lost: {k: v for k, v in paired.items() if k in lost}
    result = {"counts": {}, "failures": [], "skips": []}
    gate.interpret_pytest(result, gate_events([CASE.format("b-2")]), {"optional_tests": [], "deselected_tests": []},
                          [CASE.format("b-1")], families=(), diff=diff, base="b" * 40)
    assert result["failures"] == [] and result["collection"]["paired"] == paired
    assert f"[gate] renumbered: {CASE.format('b-1')} -> {CASE.format('b-2')}" in capsys.readouterr().out
