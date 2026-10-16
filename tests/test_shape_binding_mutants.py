"""The generic binding checker on genuine Lean answers: one mutation test per mode (test-architecture rank 10,
the first, additive step; ADR 0001).

The recorded genuine answers (`tests/data/binding-answers.jsonl.gz`, `tools/binding_census.py --record`) are
mutated leaf by leaf, array by array and several fields at once (`tests/binding_mutants.py`). Every mutant whose
verdict the Lean shapes decide must get that verdict from the generic checker (`ve.backends.shape_binding.check`,
which is `service_schema.check_row`): a mutant of a bound or closed leaf, or one that breaks a format, a bound
length or a counter, is refused; a mutant that changes only leaves of no class is accepted, so the census
(`docs/test-architecture/binding-census.json`), which is generated from the same classification, says what the
shapes really bind. Nothing here replaces a route's own consumer tests (tests/test_discourse_answer.py and the
others stay): those check the hand binders this one cannot see.
"""
from __future__ import annotations

from collections import Counter
import sys
from pathlib import Path

import pytest

from tests import binding_mutants
from tests.binding_mutants import ACCEPT, EITHER, REFUSE
from ve.backends import shape_binding
from ve.backends.service_schema import MODES

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from binding_census import load_answers  # noqa: E402

ANSWERS = load_answers()
COORDINATED = ("drop+count", "duplicate+count", "rename", "replace")


def _answers(mode):
    return [(case, row, index) for name, case, row, index in ANSWERS if name == mode]


@pytest.mark.parametrize("mode", MODES)
def test_the_generic_checker_gives_every_mutant_the_verdict_its_shape_decides(mode):
    """Every genuine answer passes; every mutant the shapes decide gets that verdict, and some are refused."""
    answers = _answers(mode)
    assert answers, f"no recorded genuine answer of {mode}: run tools/binding_census.py --record"
    wrong, verdicts = [], Counter()
    for case, row, index in answers:
        shape_binding.check(mode, case, row, index)  # a genuine answer is accepted
        for mutant in binding_mutants.mutants(mode, case, row, index):
            verdict = binding_mutants.verdict(mode, case, mutant.row, index)
            verdicts[(mutant.expect, verdict)] += 1
            if mutant.expect != EITHER and verdict != mutant.expect:
                wrong.append(f"{mutant.kind} {mutant.path}: expected {mutant.expect} ({mutant.why}), got {verdict}")
    assert not wrong, wrong[:20]
    assert verdicts[(REFUSE, REFUSE)], f"no mutant of {mode} is refused: {dict(verdicts)}"


def test_coordinated_mutants_are_generated_and_decided():
    """The multi-field mutants (an array with its counter, one request name renamed everywhere, an element
    written over another) occur on the recorded answers, and the shapes decide some of each kind."""
    decided = Counter()
    for mode, case, row, index in ANSWERS:
        for mutant in binding_mutants.mutants(mode, case, row, index):
            if mutant.kind in COORDINATED and mutant.expect != EITHER:
                decided[(mutant.kind, mutant.expect)] += 1
    for kind in COORDINATED:
        assert decided[(kind, REFUSE)] + decided[(kind, ACCEPT)], (kind, dict(decided))
    assert decided[("rename", REFUSE)] and decided[("rename", ACCEPT)], dict(decided)


@pytest.mark.parametrize("mode", MODES)
def test_every_leaf_of_an_answer_is_a_leaf_of_the_census(mode):
    """The static census (`shape_binding.leaves`) holds every leaf the generic checker places in a genuine
    answer, with the class it places it in."""
    census: dict = {}
    for leaf in shape_binding.leaves(mode):
        census.setdefault((leaf.path, leaf.kind), set()).add(leaf.binding.cls)
    missing = set()
    for case, row, index in _answers(mode):
        placed, _ = shape_binding.classify(mode, case, row, index)
        for _, _, leaf in placed:
            if leaf.binding.cls not in census.get((leaf.path, leaf.kind), set()) | census.get((leaf.path, "any"), set()):
                missing.add((leaf.path, leaf.kind, leaf.binding.cls))
    assert not missing, sorted(missing)[:20]


def test_a_bound_leaf_and_a_free_leaf_of_one_answer():
    """One answer, both ways: an `x-equals` id is refused when renamed, a Lean-derived identity of no class is
    accepted (the shape leaves it to Lean, ADR 0001), and an `x-index` position is refused when moved."""
    mode, case, row, index = next(a for a in ANSWERS if a[0] == "discourse" and a[2].get("status") == "ok"
                                  and "report_id" in a[2] and a[2]["report_id"])
    assert binding_mutants.verdict(mode, case, {**row, "id": row["id"] + "x"}, index) == REFUSE
    flipped = row["report_id"][:-1] + ("0" if row["report_id"][-1] != "0" else "1")
    assert binding_mutants.verdict(mode, case, {**row, "report_id": flipped}, index) == ACCEPT
    error = next(a for a in ANSWERS if "case_index" in a[2])
    assert binding_mutants.verdict(error[0], error[1], {**error[2], "case_index": error[3] + 1}, error[3]) == REFUSE


def test_a_name_renamed_everywhere_is_refused_where_one_occurrence_is_bound():
    """A coordinated rename keeps every internal agreement, so only a binding to the request can refuse it: one
    occurrence bound by `x-equals` or `x-references` among free ones is enough (a `target` equal to a request
    layer, renamed with the `targets` entry that repeats it)."""
    mixed = 0
    for mode, case, row, index in ANSWERS:
        placed, _ = shape_binding.classify(mode, case, row, index)
        for mutant in binding_mutants.mutants(mode, case, row, index):
            if mutant.kind != "rename":
                continue
            leaves = [leaf for _, _, leaf in placed if leaf.path in mutant.path.split(",")]
            bound = any(leaf.binding.cls == "bound" and leaf.binding.at is None and
                        leaf.binding.relation in binding_mutants.EXACT | {"references"} for leaf in leaves)
            if bound and any(leaf.binding.cls == "none" for leaf in leaves):
                mixed += 1
                assert mutant.expect == REFUSE, (mode, mutant.path, mutant.why)
                assert binding_mutants.verdict(mode, case, mutant.row, index) == REFUSE, (mode, mutant.path)
    assert mixed, "no recorded answer repeats a bound request name in a free leaf"
