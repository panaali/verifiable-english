"""S2a's choice algebra and closed English, independent of proof search."""

from dataclasses import dataclass

from ve.readings_sup import (bits_of, choice_atom, choice_contents, choice_core, choice_vocabulary,
                             choices, copies, pattern, sup_ready, superposed_contents,
                             uniform_precedence, unsatisfiable_ids)
from ve.readings_s1 import Candidate as S1Candidate, Content, Document, ReadingSet
import pytest

from ve.errors import VEError
from ve.readings_s2_english import (OVER_BUDGET, QUIET, S2A, TEMPLATES, Slots, dead_reading, derivations,
                                    every_result, gated, named_result, none_result, not_superposed)


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


SLOTS = Slots(numbers={"1", "2", "3"}, readings={"*must*", "*should*", "reading 1", "reading 2"},
              conclusions={"*For every agent, for every user, that agent must help that user.*"},
              situations={"a is an agent; u is a user"})


def test_closed_s2_english_instances_pass_the_gate():
    """Each S2a sentence is built from its registered template and admitted by the all-derivations gate (W7)."""
    conclusion = "*For every agent, for every user, that agent must help that user.*"
    assert every_result(1, "follows", SLOTS, conclusion=conclusion) == (
        "Under every reading of the open sentence, the conclusion follows: " + conclusion)
    assert named_result([(1, "*must*"), (2, "*should*")], "conflict_free", SLOTS) == (
        "Read sentence 1 as *must* and sentence 2 as *should*: "
        "no two rules on the same act contradict each other.")
    assert none_result(3, SLOTS) == "Under no reading of the 3 open sentences does the conclusion follow."
    assert not_superposed([1, 2], SLOTS) == (
        "The readings of sentences 1 and 2 were checked one way at a time, not together.")
    assert dead_reading(2, "*should*", SLOTS).endswith("sentence 2 as *should*.")
    assert "may not" not in " ".join((QUIET, OVER_BUDGET))
    for text, name in ((QUIET, "E8"), (OVER_BUDGET, "E28")):
        assert [d[0] for d in derivations(text, SLOTS)] == [name]


def test_every_s2a_instance_has_one_derivation():
    """Instances of every S2a template, over every result sentence where it takes one, each read by exactly one
    registered template, its own (W7's gate over S2a's registrations and S1's)."""
    from ve.readings_s2_english import (excludes, independent, narrowed, one_reading, over_budget, provided,
                                        quiet, requires, result_sentence)
    conclusion, situation = next(iter(SLOTS.conclusions)), next(iter(SLOTS.situations))
    kinds = ("conflict_free", "follows", "countermodel", "conflict", "premise_model", "inconsistent")
    built = [provided(SLOTS), one_reading(1, 2, SLOTS), quiet(SLOTS), over_budget(SLOTS),
             narrowed(1, "*should*", [2, 3], SLOTS), independent(2, SLOTS), dead_reading(1, "reading 2", SLOTS),
             none_result(2, SLOTS), not_superposed([1], SLOTS), requires((1, "*must*"), (2, "reading 1"), SLOTS),
             excludes((1, "*must*"), (2, "reading 1"), SLOTS)]
    for kind in kinds:
        built.append(named_result([(1, "*must*"), (3, "reading 2")], kind, SLOTS, conclusion=conclusion,
                                  situation=situation))
        if kind in ("conflict_free", "follows", "inconsistent"):
            built += [every_result(1, kind, SLOTS, conclusion=conclusion),
                      every_result(2, kind, SLOTS, conclusion=conclusion)]
    for text in built:
        assert len(derivations(text, SLOTS)) == 1, text
    assert result_sentence("follows", conclusion=conclusion).startswith("the conclusion follows: ")


def test_the_gate_refuses_a_second_derivation():
    """A reading name that could also be read as two named readings gives E12 two derivations: refused."""
    ambiguous = Slots(numbers={"1", "2"}, readings={"*must*", "*should*", "*must* and sentence 2 as *should*"})
    text = "Read sentence 1 as *must* and sentence 2 as *should*: no two rules on the same act contradict each other."
    assert len(derivations(text, ambiguous)) == 2
    with pytest.raises(VEError, match="has 2 derivations"):
        gated("E12", text, ambiguous)
    with pytest.raises(VEError, match="has 0 derivations"):
        gated("E12", "Read sentence 9 as *must*: no two rules on the same act contradict each other.", SLOTS)


def test_g5_e11_is_not_a_wording():
    """The lifting lemma holds (4.4), so E11 is never shown: it has no derivation (G5)."""
    text = "Under every reading with at least one individual, no two rules on the same act contradict each other."
    assert derivations(text, SLOTS) == []


def test_g6_g9_generated_names_and_may_not_refused():
    for text in ("Read sentence 1 as *must*: the conclusion follows: *ve__here*",
                 "This does not depend on how sentence 1 is read. may not"):
        with pytest.raises(VEError, match="generated name or `may not`"):
            gated("E12", text, SLOTS)


def test_s1_report_sentences_keep_their_own_lead():
    """The class of review B4: S1's report sentences go through the same registry, each read by its own lead only,
    so no S1 sentence can be read as one of S2a's (and none of S2a's as one of S1's)."""
    from ve.readings_english import E24, act_only_sentence, assertion_pair_sentence, outcome_pair_sentence
    from ve.readings_route import _s1_gated
    _s1_gated("E24", E24)
    _s1_gated("E16", act_only_sentence("avoid deceiving", "help"))
    _s1_gated("E19", assertion_pair_sentence("a is an agent", "*must*", "*should*"))
    _s1_gated("E19", outcome_pair_sentence("a is an agent", "*must*", "*should*", "obligation", "a", True,
                                           other_admissible=False))
    with pytest.raises(VEError, match="S1 wording E19 has 0 derivations"):
        _s1_gated("E19", "This does not depend on how sentence 1 is read.")
