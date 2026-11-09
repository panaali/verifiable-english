"""A mutant renumbered by an inserted one is paired by its text, not refused; a mutant whose text is gone stays
refused (tools/gate_collection.py, `CASES_HOOK`)."""
from __future__ import annotations

import json

import pytest

from tests.test_gate_collection import commit, compare, gate_events, git
from tools import gate, gate_collection

# Each case is named by its definition and its position, as tests/test_packs_guard_mutants.py names them.
MODULE = """import json, pathlib, pytest
MUTANTS = json.loads(pathlib.Path(__file__).with_name("mutants.json").read_text())
IDS = [f"{name}-{i}" for i, (name, _, _) in enumerate(MUTANTS)]
HOOK
@pytest.mark.parametrize("name,find,replace", MUTANTS, ids=IDS)
def test_mutant(name, find, replace): pass
"""
HOOK = "def mutant_cases(): return {nodeid: json.dumps(mutant) for nodeid, mutant in zip(IDS, MUTANTS)}\n"
BASE = [["a", "x", "y"], ["b", "x", "y"], ["c", "x", "y"], ["d", "x", "y"]]
INSERTED = [BASE[0], ["new", "x", "y"], *BASE[1:]]
SAME = [["a", "x", "1"], ["a", "x", "2"], ["a", "x", "3"]]


def case(name):
    return f"tests/test_m.py::test_mutant[{name}]"


def files(mutants, hook=HOOK):
    return {"pytest.ini": "[pytest]\n", "tests/test_m.py": MODULE.replace("HOOK", hook),
            "tests/mutants.json": json.dumps(mutants)}


def history(tmp_path, before, after, hook=HOOK, trailer=None, worktree=False):
    git(tmp_path, "init", "-q", "-b", "main")
    base = commit(tmp_path, files(before, hook))
    if worktree:
        expected = gate_collection.collect(tmp_path)
        (tmp_path / "tests/mutants.json").write_text(json.dumps(after))
        return gate_collection.missing(expected, gate_collection.collect(tmp_path),
                                       gate_collection.changes(base, None, root=tmp_path))
    head = commit(tmp_path, files(after))
    if trailer:
        head = commit(tmp_path, {}, f"x\n\n{gate_collection.TRAILER}: {trailer}{gate_collection.SEPARATOR}why")
    return compare(tmp_path, base, head)


SHIFTED = "b-1:b-2 c-2:c-3 d-3:d-4"
# (base mutants, head mutants, the base's hook, a trailer's target, head in the worktree, the pairs, the refused)
CASES = {
    "inserted": (BASE, INSERTED, HOOK, "", False, SHIFTED, ""),
    "inserted-worktree": (BASE, INSERTED, HOOK, "", True, SHIFTED, ""),
    "trailer-first": (BASE, INSERTED, HOOK, "b-1", False, "c-2:c-3 d-3:d-4", ""),
    # Each head loses a base mutant's text (most also insert one), or the base has no hook: each lost ID is refused.
    "text-changed": (BASE, [*INSERTED[:3], ["c", "x", "z"], BASE[3]], HOOK, "", False, "", "b-1 c-2 d-3"),
    "case-deleted": (BASE, [*INSERTED[:3], BASE[3]], HOOK, "", False, "", "b-1 c-2"),
    # `a-0` keeps its ID with another text; the lost `a-2`'s text is at `a-1`, but `a-0`'s first text is gone.
    "kept-id-reused": (SAME, SAME[1:], HOOK, "", False, "", "a-2"),
    "no-hook-at-base": (BASE, INSERTED, "", "", False, "", "b-1 c-2 d-3"),
    "two-cases-one-text": ([BASE[0], BASE[0]], [["new", "x", "y"], BASE[0]], HOOK, "", False, "", "a-0"),
}


@pytest.mark.parametrize("before, after, hook, trailer, worktree, paired, refused", CASES.values(), ids=CASES)
def test_a_renumbered_mutant_is_paired_by_its_text_and_a_gone_one_refused(tmp_path, before, after, hook, trailer,
                                                                          worktree, paired, refused):
    verdict = history(tmp_path, before, after, hook, trailer and case(trailer), worktree)
    assert verdict.paired == {case(b): case(h) for b, h in (pair.split(":") for pair in paired.split())}
    assert set(verdict.refused) == {case(name) for name in refused.split()} and verdict.failed() == bool(refused)
    assert set(verdict.removed) == ({case(trailer)} if trailer else set())


def test_the_gate_logs_the_pairing_table_and_records_it(capsys):
    diff = gate_collection.Changes("b" * 40, "h" * 40, {})
    diff.renumbered = lambda expected, collected, lost: {case("b-1"): case("b-2")}
    result = {"counts": {}, "failures": [], "skips": []}
    gate.interpret_pytest(result, gate_events([case("b-2")]), {"optional_tests": [], "deselected_tests": []},
                          [case("b-1")], families=(), diff=diff, base="b" * 40)
    assert result["failures"] == [] and result["collection"]["paired"] == {case("b-1"): case("b-2")}
    assert f"[gate] renumbered: {case('b-1')} -> {case('b-2')}" in capsys.readouterr().out
