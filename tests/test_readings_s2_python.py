"""S2a's choice algebra and closed English, independent of proof search."""

from dataclasses import dataclass

from ve.readings_sup import (bits_of, choice_atom, choice_contents, choice_core, choice_vocabulary,
                             choices, copies, pattern, sup_ready, superposed_contents,
                             uniform_precedence, unsatisfiable_ids)
from ve.readings_s1 import Candidate as S1Candidate, Content, Document, ReadingSet
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


def _norm(name, *, over=(), mode="strict", sufficient=()):
    body = {"name": name, "predicate": "required", "sign": True,
            "guard": ["top"], "over": list(over), "mode": mode}
    if mode == "default":
        body["exception"] = {"decided_by": "unstated", "sufficient": list(sufficient),
                             "necessary": [], "factors": []}
    return Content("norm", body, {"norm": body})


def _doc(candidates, fixed=()):
    doc = Document.__new__(Document)
    reading_set = ReadingSet({"id": "rs1", "unit": "u1", "version": 1},
                             [S1Candidate(f"a{i}", c, {}) for i, c in enumerate(candidates)])
    doc.items = [("fixed", f"f{i}", c) for i, c in enumerate(fixed)] + [("set", "u1", reading_set)]
    return doc


def test_superposition_gates_and_qualifies_without_mutating_sources():
    first = _norm("rule-x")
    second = _norm("rule-x", mode="default", sufficient=(["top"],))
    fixed = _norm("stop-x", over=("rule-x",))
    doc = _doc([first, second], [fixed])
    assert sup_ready(doc.sets)
    assert uniform_precedence(doc)
    assert copies(doc, "rule-x") == ["rd-1-rule-x", "rd-2-rule-x"]
    result = superposed_contents(doc)
    assert result[0].body["over"] == ["rd-1-rule-x", "rd-2-rule-x"]
    assert result[1].body["name"] == "rd-1-rule-x"
    assert result[2].body["name"] == "rd-2-rule-x"
    assert result[2].body["guard"] == ["and", ["top"], ["unary", "ve__bit__1__0", ["const", "ve__here"]]]
    assert result[2].body["exception"]["sufficient"] == [
        ["and", ["top"], ["unary", "ve__bit__1__0", ["const", "ve__here"]]]]
    assert fixed.body["over"] == ["rule-x"]
    assert second.body["name"] == "rule-x"
    assert [c.body["name"] for c in choice_contents(doc, {"rs1": 1})] == ["stop-x", "rule-x"]


def test_uniform_precedence_catches_m8_leak_and_shape_rejects_m17():
    fixed = _norm("stop-x", over=("waive-x",))
    doc = _doc([_norm("waive-x"), _norm("waive-x", over=("base-x",))], [fixed])
    assert not uniform_precedence(doc)
    doc.sets[0].candidates[1].content = None
    assert not sup_ready(doc.sets)
    doc.sets[0].candidates[1].content = _norm("waive-x", over=("base-x",))
    coupling = {"id": "c1", "axis": "force", "sets": [
        {"set": "rs1", "version": 1}, {"set": "rs2", "version": 1}]}
    assert not sup_ready(doc.sets, [coupling])


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
