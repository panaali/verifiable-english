"""Release B, F1 and F2 (relb-f1f2-grammar; reviews/dri-decision-relb-english-rules-20261121.md items 1, 2, 5).

F1 is the splice in ve/surface/time.py: date and money comparisons, each read by the quantity grammar, inside
if/and/or/not read by the core English grammar, with every reading admitted by Lean's existing quantity
admission. F2 is the money subtraction wording "A equals B minus C". The fixtures in tests/fixtures/relb_f1f2 are
copies of the eligibility environment and rule formulas (make_fixtures.py there), so these tests do not move when
usecases/eligibility does. The ten-sentence test reads sentences a fresh model wrote from the source clauses alone
(tests/fixtures/relb_f1f2/ten_sentences: prompt, input, unedited output); refusals are recorded results.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

import ve.surface.time as surface_time
from ve.environment import Environment
from ve.errors import AmbiguousDerivation, ResourceLimit, VEError
from ve.surface.time import (_Derivations, _quantity_spans, _splice_readings, parse_quantity_sentence,
                             parse_w6_sentence, render_quantity_sentence, render_w6_sentence)
from ve.units import elaborate_quantity, erased_data

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "relb_f1f2"
RAW = json.loads((FIXTURES / "environment.json").read_text(encoding="utf-8"))
RULES = {r["id"]: r for r in json.loads((FIXTURES / "rules.json").read_text(encoding="utf-8"))}
WORDINGS = json.loads((FIXTURES / "wordings.json").read_text(encoding="utf-8"))
TEN = FIXTURES / "ten_sentences"

# The 36 rules that need F1 (a date or money comparison under if/and/or/not; reviews/relb-f1-sizing-20261121.md),
# R16c that also needs F2, and the 19 that read today without either.
F1_RULES = [f"{base}.{role}" for role in ("applicant", "housemate")
            for base in ("R2", "R80", "R3", "R5a", "R5b", "R7a", "R7b", "R8a", "R8b", "R8c", "R9", "R11", "R12")] + [
    "R14a", "R14.2", "R14.3", "R14.1", "R15.6", "R15.5", "R15.4", "R16a", "R16b", "G7"]
F2_RULE = "R16c"
TODAY_RULES = [rid for rid in RULES if rid not in F1_RULES and rid != F2_RULE]
KEPT_EQUALS_AMOUNT = "The applicant's amount kept equals the applicant's winter fuel payment amount."


@pytest.fixture(scope="module")
def env():
    return Environment(RAW)


def statement(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def canonical(env, rid):
    return elaborate_quantity(env, statement(RULES[rid]["formula"]))[0]


def gbp(name):
    return ["const", "gbp_penny", name]


def test_rule_partition():
    assert len(F1_RULES) == 36 and len(TODAY_RULES) == 19 and len(RULES) == 56


@pytest.mark.parametrize("rid", F1_RULES)
def test_f1_rule_has_exactly_one_reading_and_it_is_the_rule(env, rid):
    expected = canonical(env, rid)
    assert render_w6_sentence(env, expected) == WORDINGS[rid]
    assert parse_w6_sentence(env, WORDINGS[rid]) == expected
    # Every reading the splice finds over every span choice is the rule (none is a rival).
    assert all(r == expected for r in _splice_readings(env, WORDINGS[rid]))


@pytest.mark.parametrize("rid", TODAY_RULES)
def test_rules_read_today_keep_their_one_reading(env, rid):
    expected = canonical(env, rid)
    assert render_w6_sentence(env, expected) == WORDINGS[rid]
    assert parse_w6_sentence(env, WORDINGS[rid]) == expected


def test_r16c_reads_back_to_its_rule(env):
    expected = canonical(env, F2_RULE)
    wording = WORDINGS[F2_RULE]
    assert wording == ("If applicant is entitled, then the applicant's amount kept equals the applicant's winter fuel "
                       "payment amount minus the applicant's recovered amount.")
    assert render_w6_sentence(env, expected) == wording
    assert parse_w6_sentence(env, wording) == expected


def test_r16c_sub_span_alone_does_not_win_a_reading_in_the_full_sentence(env):
    wording = WORDINGS[F2_RULE]
    alone = parse_quantity_sentence(env, KEPT_EQUALS_AMOUNT)["formula"]
    assert alone == ["eq", gbp("kept"), gbp("amount")]  # a different rule, read alone today
    text = " ".join(wording.split())[:-1]
    spans = {text[i:j]: [r["formula"] for r in readings]
             for i, j, readings in _quantity_spans(env, text, _Derivations(env))}
    sub = KEPT_EQUALS_AMOUNT[:-1].replace("The", "the", 1)
    assert spans[sub] == [alone]  # the splice does find the sub-span ...
    readings = _splice_readings(env, wording)
    assert readings and all(r == canonical(env, F2_RULE) for r in readings)  # ... and it wins no reading
    assert all(json.dumps(alone) not in json.dumps(r["formula"]) for r in readings)


def test_two_span_choices_that_read_differently_are_refused(env):
    sentence = "If it is not the case that the applicant's amount kept equals GBP 5.00, then applicant is recovered."
    first = ["implies", ["not", ["eq", gbp("kept"), ["num", "gbp_penny", "500"]]],
             ["unary", "recovered", ["const", "applicant"]]]
    # Control: one choice of spans reads, so one reading.
    assert parse_w6_sentence(env, sentence)["formula"] == first
    # A money constant whose name starts "it is not the case that ..." gives a second span choice: the longer span
    # reads eq(odd, 5.00) and its frame "If <span>, then ..." reads too.
    raw = copy.deepcopy(RAW)
    raw["vocabulary"]["constants"]["odd"] = {
        "sort": "$int", "unit": "gbp_penny", "description": "A constructed rival span.",
        "verbalisation": "it is not the case that the applicant's amount kept"}
    rival = Environment(raw)
    readings = _splice_readings(rival, sentence)
    second = ["implies", ["eq", gbp("odd"), ["num", "gbp_penny", "500"]], ["unary", "recovered", ["const", "applicant"]]]
    assert sorted(json.dumps(r["formula"]) for r in readings) == sorted(json.dumps(f) for f in [first, second])
    with pytest.raises(AmbiguousDerivation, match="2 derivations"):
        parse_w6_sentence(rival, sentence)


def test_span_readings_that_differ_are_refused(env):
    # One span, two quantity readings (a constant named like a comparison): the splice counts both.
    raw = copy.deepcopy(RAW)
    raw["vocabulary"]["constants"]["odd"] = {
        "sort": "$int", "unit": "gbp_penny", "description": "A constructed rival reading.",
        "verbalisation": "the applicant's amount kept equals the applicant's winter fuel payment amount"}
    raw["vocabulary"]["constants"]["odd2"] = {
        "sort": "$int", "unit": "gbp_penny", "description": "A constructed rival reading.",
        "verbalisation": "the applicant's winter fuel payment amount equals the applicant's recovered amount"}
    rival = Environment(raw)
    sentence = ("If applicant is entitled, then the applicant's amount kept equals the applicant's winter fuel payment "
                "amount equals the applicant's recovered amount.")
    then = ["unary", "entitled", ["const", "applicant"]]
    assert sorted(json.dumps(r["formula"]) for r in _splice_readings(rival, sentence)) == sorted(json.dumps(f) for f in [
        ["implies", then, ["eq", gbp("odd"), gbp("recovered_amount")]],
        ["implies", then, ["eq", gbp("kept"), gbp("odd2")]]])
    with pytest.raises(AmbiguousDerivation, match="2 derivations"):
        parse_w6_sentence(rival, sentence)


def test_the_splice_is_charged_to_the_derivation_budget(env, monkeypatch):
    rid = "R11.applicant"  # six spans, 63 choices
    assert parse_w6_sentence(env, WORDINGS[rid]) == canonical(env, rid)
    monkeypatch.setattr(surface_time, "MAX_DERIVATIONS", 40)
    with pytest.raises(ResourceLimit, match="MAX_DERIVATIONS=40"):
        parse_w6_sentence(env, WORDINGS[rid])


def test_many_comparisons_exhaust_the_budget(env, monkeypatch):
    # 2**k - 1 choices for k separate spans: charging each choice stops a sentence with many comparisons.
    monkeypatch.setattr(surface_time, "MAX_DERIVATIONS", 300)
    conjuncts = [["date_no_later", ["const", "day", "applicant_claim_date"], ["date", f"2026-10-{d:02d}"]]
                 for d in range(1, 10)]
    formula = conjuncts[0]
    for c in conjuncts[1:]:
        formula = ["and", formula, c]
    with pytest.raises(ResourceLimit, match="MAX_DERIVATIONS"):
        parse_w6_sentence(env, render_w6_sentence(env, elaborate_quantity(env, statement(formula))[0]))


def test_f2_money_subtraction_round_trip(env):
    for sentence, formula in [
            ("The applicant's amount kept equals the applicant's winter fuel payment amount minus the applicant's "
             "recovered amount.",
             ["eq", gbp("kept"), ["add", "gbp_penny", gbp("amount"), ["scale", "gbp_penny", "-1", gbp("recovered_amount")]]]),
            ("The applicant's recovered amount equals GBP 300.00 minus the applicant's amount kept.",
             ["eq", gbp("recovered_amount"), ["add", "gbp_penny", ["num", "gbp_penny", "30000"],
                                              ["scale", "gbp_penny", "-1", gbp("kept")]]])]:
        got = parse_quantity_sentence(env, sentence)
        assert got["formula"] == formula
        assert parse_w6_sentence(env, sentence) == got
        assert render_quantity_sentence(env, got) == sentence


def test_f2_minus_is_not_read_as_a_comparison_alone(env):
    # The leftover " minus ..." stops "A equals B" from reading the whole sentence as eq(A, B).
    with pytest.raises(VEError):
        parse_quantity_sentence(env, "The applicant's amount kept equals the applicant's winter fuel payment amount "
                                     "minus.")


def test_a_date_subtraction_is_refused(env):
    sentence = ("The applicant's claim date equals the applicant's care end date minus the applicant's care start "
                "date.")
    with pytest.raises(VEError):
        parse_quantity_sentence(env, sentence)
    with pytest.raises(VEError):
        parse_w6_sentence(env, sentence)
    day = ["const", "day", "applicant_claim_date"]
    with pytest.raises(VEError):  # Lean types add/scale for no day tag either
        elaborate_quantity(env, statement(["eq", day, ["add", "day", ["const", "day", "applicant_care_until"],
                                                       ["scale", "day", "-1", ["const", "day", "applicant_care_from"]]]]))


def percent_env():
    raw = copy.deepcopy(RAW)
    raw["units"]["bp"] = {"scale": "100", "display": {"kind": "percent"}}
    raw["vocabulary"]["constants"]["rate"] = {"sort": "$int", "unit": "bp", "description": "A rate.",
                                              "verbalisation": "the rate"}
    raw["vocabulary"]["constants"]["old_rate"] = {"sort": "$int", "unit": "bp", "description": "An old rate.",
                                                  "verbalisation": "the old rate"}
    return Environment(raw)


def test_percentage_points_keeps_its_one_reading():
    env = percent_env()
    sentence = "The rate minus the old rate equals 2.50 percentage points."
    got = parse_w6_sentence(env, sentence)
    assert got["formula"] == ["eq", ["add", "bp", ["const", "bp", "rate"], ["scale", "bp", "-1", ["const", "bp", "old_rate"]]],
                              ["num", "bp", "250"]]
    assert render_quantity_sentence(env, got) == sentence
    assert got == parse_quantity_sentence(env, sentence)
    # The money pattern does not apply to a percent tag.
    with pytest.raises(VEError):
        parse_quantity_sentence(env, "The rate equals the old rate minus the old rate.")


def test_stand_ins_are_fresh_and_not_borrowed(env):
    target, slot, predicates, words = surface_time._splice_target(env, 3, "")
    data = erased_data(env.to_dict())["vocabulary"]
    assert slot not in data["constants"] and not set(predicates) & set(data["predicates"])
    assert len(predicates) % 8 == 0 and all(w.startswith(f'"{slot}"') for w in words)
    # A text that already names the stand-ins gets other names.
    _, slot2, predicates2, _ = surface_time._splice_target(env, 3, f'"{slot}" is classified as "{predicates[0]}"')
    assert slot2 != slot and predicates2[0] != predicates[0]


def ten_sentences():
    clauses = json.loads((TEN / "input.json").read_text(encoding="utf-8"))["clauses"]
    lines = [line for line in (TEN / "writer_output.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == len(clauses) == 10
    return [(c, re.sub(r"^\d+\. ", "", line)) for c, line in zip(clauses, lines)]


def outcome(env, clause, sentence):
    text = " ".join(sentence.split())
    spans = sorted({text[i:j] for i, j, _ in _quantity_spans(env, text.rstrip(".") if text.endswith(".") else text,
                                                              _Derivations(env))})
    try:
        got = parse_w6_sentence(env, sentence)
    except VEError as exc:
        return {"rule": clause["rule"], "outcome": "refused", "equals_rule": None,
                "reason": f"{type(exc).__name__}: {exc}", "spans_read_alone": spans}
    return {"rule": clause["rule"], "outcome": "one reading", "equals_rule": got == canonical(env, clause["rule"]),
            "reason": None, "spans_read_alone": spans}


def test_ten_sentences_written_from_the_sources(env):
    """Each sentence gets exactly one reading or is refused (parse_w6_sentence never returns two); the
    recorded table is the result, so a change in any outcome shows here."""
    recorded = json.loads((TEN / "results.json").read_text(encoding="utf-8"))
    got = {str(clause["n"]): outcome(env, clause, sentence) for clause, sentence in ten_sentences()}
    assert got == recorded
