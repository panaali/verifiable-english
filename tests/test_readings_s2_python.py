"""S2a's choice algebra and closed English, independent of proof search."""

from dataclasses import dataclass

from ve.readings_sup import (bits_of, choice_atom, choice_core, choice_vocabulary,
                             choices, pattern, unsatisfiable_ids)
from ve.readings_s2_english import (OVER_BUDGET, QUIET, dead_reading, every_result,
                                    named_result, none_result, not_superposed,
                                    result_sentence)


@dataclass
class Candidate:
    id: str
    labels: dict


@dataclass
class Set:
    id: str
    version: int
    candidates: list


def _set(name, labels=("A", "B"), version=1):
    return Set(name, version, [Candidate(f"{name}-{i}", {"force": label})
                               for i, label in enumerate(labels)])


def test_binary_patterns_and_unused_code_match_m7():
    sets = [_set("rs1", ("A", "B", "C"))]
    bit0 = ["unary", "ve__bit__1__0", ["const", "ve__here"]]
    bit1 = ["unary", "ve__bit__1__1", ["const", "ve__here"]]
    assert bits_of(1) == 0 and bits_of(3) == 2 and bits_of(64) == 6
    assert pattern(1, 3, 0) == ["and", ["not", bit0], ["not", bit1]]
    assert pattern(1, 3, 1) == ["and", bit0, ["not", bit1]]
    assert pattern(1, 3, 2) == ["and", ["not", bit0], bit1]
    assert choice_atom(sets, "missing", 0) == ["bottom"]
    assert choice_core(sets) == [("readings:rs1@1:one", ["not", ["and", bit0, bit1]])]
    assert choice_vocabulary(sets) == {"sorts": ["ve__reading"],
                                        "constants": {"ve__here": "ve__reading"},
                                        "predicates": {"ve__bit__1__0": ["ve__reading"],
                                                       "ve__bit__1__1": ["ve__reading"]}}


def test_coupling_narrowing_and_stale_narrowing_match_m6_m17():
    sets = [_set("rs1"), _set("rs2")]
    coupling = {"id": "c1", "axis": "force", "sets": [
        {"set": "rs1", "version": 1}, {"set": "rs2", "version": 1}]}
    assert choices(sets, [coupling]) == ([{"rs1": 0, "rs2": 0}, {"rs1": 1, "rs2": 1}], False)
    narrowing = {"id": "n1", "set": "rs1", "version": 1, "keeps": ["rs1-0"]}
    assert choices(sets, [coupling], [narrowing]) == ([{"rs1": 0, "rs2": 0}], False)
    core = choice_core(sets, [coupling], [narrowing])
    assert [label for label, _ in core] == ["coupling:c1", "narrowing:n1"]
    assert core[-1][1] == ["not", ["unary", "ve__bit__1__0", ["const", "ve__here"]]]
    stale = {**narrowing, "version": 2}
    assert choices(sets, [coupling], [stale]) == choices(sets, [coupling])
    assert choice_core(sets, [coupling], [stale]) == choice_core(sets, [coupling])
    assert unsatisfiable_ids(sets, [coupling], [stale]) == "c1"


def test_unsatisfiable_and_65_choice_boundary():
    sets = [_set("rs1"), _set("rs2")]
    drops = [{"id": "n1", "set": "rs1", "version": 1, "keeps": ["rs1-0"]},
             {"id": "n2", "set": "rs1", "version": 1, "keeps": ["rs1-1"]}]
    assert choices(sets, narrowings=drops) == ([], False)
    assert unsatisfiable_ids(sets, narrowings=drops) == "n1, n2"
    many = [_set(f"rs{i}") for i in range(7)]
    found, over = choices(many)
    assert len(found) == 65 and over
    assert found[0] == {f"rs{i}": 0 for i in range(7)}


def test_closed_s2_english_instances():
    follows = result_sentence("follows", conclusion="*Every agent must help each user.*")
    assert every_result(1, "follows", conclusion="*Every agent must help each user.*") == (
        "Under every reading of the open sentence, the conclusion follows: *Every agent must help each user.*")
    assert named_result([(1, "*must*"), (2, "*should*")],
                        result_sentence("conflict_free")) == (
        "Read sentence 1 as *must* and sentence 2 as *should*: "
        "no two rules on the same act contradict each other.")
    assert none_result(3) == "Under no reading of the 3 open sentences does the conclusion follow."
    assert not_superposed("sentences 1 and 2") == (
        "The readings of sentences 1 and 2 were checked one way at a time, not together.")
    assert dead_reading(2, "*should*").endswith("sentence 2 as *should*.")
    assert "may not" not in " ".join((follows, QUIET, OVER_BUDGET))
