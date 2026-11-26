"""Sums of amounts (statute-feature-sums-build; manage-agents reviews/spare/statute-corpus/feature-sums/PROPOSAL.md v2,
tested on real text in feature-sums2/RESULT.md): the W6 wordings "A equals B plus C." and "A equals the sum of B, C
... and Z." (ve/surface/time.py) and the shell's lowering of a sum over named terms, the case's items, or the days or
weeks of a period (ve/surface/sums.py). No Lean node is added: every lowered statement is an add chain Lean admits
today, and the answers below are Lean certificates (prove_quantity).

The decision's conditions (manage-agents reviews/dri-decisions-20261124-feature-sums2-prod.md item 1), each its own
test: (1) the `sum of` wording renders and parses the add chain with exactly one reading; (2) the three plants P1-P3
of feature-sums2 are refused; (3) a sum of more than 60 terms is refused at run time; (4) a real day-sum case (council
tax, LGFA 1992 s. 10(1), the K007 run across two financial years); (5) a running total is refused."""
from __future__ import annotations

import pytest

from ve.environment import Environment
from ve.errors import AmbiguousDerivation, ResourceLimit, UnsupportedProfile, VEError
from ve.surface.sums import (SumRuleBound, SumRuleError, SumRuleRunning, lower_sum_item, lower_sum_items,
                             lower_written_item)
from ve.surface.time import (MAX_SUM_TERMS, _chain, parse_quantity_sentence, parse_w6_sentence,
                             render_quantity_sentence, render_w6_sentence)
from ve.units import elaborate_quantity, prove_quantity

GBP = "gbp_penny"
UNITS = {GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP"}},
         "day": {"scale": "1", "display": {"kind": "iso_date"}}}


def environment(amounts=(), individuals=(), predicates=(), units=UNITS):
    constants = {name: {"sort": "item", "description": name} for name in individuals}
    for name, phrase in amounts:
        constants[name] = {"sort": "$int", "unit": GBP, "description": phrase, "verbalisation": phrase}
    return Environment({
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"item": {"description": "an item of the case"}},
                       "predicates": {p: {"arguments": ["item"], "description": p} for p in predicates},
                       "constants": constants},
        "unit_schema": "ve-units@1", "units": units})


def g(name):
    return ["const", GBP, name]


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def proves(env, premises, formula):
    statements = [p if "format" in p else q(p) for p in premises]
    statements = [elaborate_quantity(env, s)[0] for s in statements]
    return prove_quantity(env, statements, elaborate_quantity(env, q(formula))[0]) is not None


def terms_env(n):
    return environment([("total", "the total")] + [(f"t{k}", f"the amount of part {k}") for k in range(1, n + 1)])


def sum_sentence(n):
    words = [f"the amount of part {k}" for k in range(1, n + 1)]
    if n == 2:
        return f"The total equals {words[0]} plus {words[1]}."
    return f"The total equals the sum of {', '.join(words[:-1])} and {words[-1]}."


# --- (1) the wording: one reading, round trip ------------------------------------------------------------------

@pytest.mark.parametrize("n", [2, 3, 4, 12])
def test_condition1_sum_wording_round_trip_with_exactly_one_reading(n):
    env = terms_env(n)
    sentence = sum_sentence(n)
    got = parse_quantity_sentence(env, sentence)
    assert got["formula"] == ["eq", g("total"), _chain(GBP, [g(f"t{k}") for k in range(1, n + 1)])]
    assert parse_w6_sentence(env, sentence) == got  # every grammar together: still one reading
    assert render_quantity_sentence(env, got) == sentence
    assert render_w6_sentence(env, got) == sentence


def test_condition1_sixty_terms_round_trip():
    env = terms_env(MAX_SUM_TERMS)
    sentence = sum_sentence(MAX_SUM_TERMS)
    got = parse_quantity_sentence(env, sentence)
    assert render_quantity_sentence(env, got) == sentence
    assert parse_w6_sentence(env, sentence) == got


def test_condition1_literals_and_constants_mix():
    env = terms_env(2)
    sentence = "The total equals the sum of the amount of part 1, GBP 5.00 and the amount of part 2."
    got = parse_quantity_sentence(env, sentence)
    assert got["formula"] == ["eq", g("total"), ["add", GBP, g("t1"), ["add", GBP, ["num", GBP, "500"], g("t2")]]]
    assert render_quantity_sentence(env, got) == sentence


def test_condition1_two_tilings_are_two_readings_never_one_picked():
    # A constant whose phrase is itself "part 1, part 2" gives a second tiling: rejected, the writer renames.
    env = environment([("total", "the total"), ("a", "part 1"), ("b", "part 2"), ("c", "part 3"),
                       ("ab", "part 1, part 2"), ("d", "part 4")])
    with pytest.raises(AmbiguousDerivation):
        parse_quantity_sentence(env, "The total equals the sum of part 1, part 2, part 3 and part 4.")
    with pytest.raises(AmbiguousDerivation):
        parse_w6_sentence(env, "The total equals the sum of part 1, part 2, part 3 and part 4.")


def test_condition1_one_wording_per_count():
    env = terms_env(3)
    for sentence in ("The total equals the sum of the amount of part 1 and the amount of part 2.",  # two: "plus"
                     "The total equals the amount of part 1 plus the amount of part 2 plus the amount of part 3.",
                     "The total equals the sum of the amount of part 1, the amount of part 2, and the amount of part 3.",
                     "The total equals the sum of the amount of part 1, the amount of part 2 and the amount of part 9."):
        with pytest.raises(VEError):
            parse_quantity_sentence(env, sentence)


def test_condition1_only_the_right_nested_chain_has_a_wording():
    env = terms_env(3)
    left = q(["eq", g("total"), ["add", GBP, ["add", GBP, g("t1"), g("t2")], g("t3")]])
    canonical, _ = elaborate_quantity(env, left)
    with pytest.raises(UnsupportedProfile):
        render_quantity_sentence(env, canonical)


def test_condition1_a_sum_inside_a_rule_reads_once():
    env = environment([("total", "the total"), ("a", "the first amount"), ("b", "the second amount"),
                       ("c", "the third amount"), ("cap", "the cap")])
    sentence = "If the first amount is less than the cap, then the total equals the first amount plus the second amount."
    got = parse_w6_sentence(env, sentence)
    assert got["formula"] == ["implies", ["lt", g("a"), g("cap")], ["eq", g("total"), ["add", GBP, g("a"), g("b")]]]
    assert render_w6_sentence(env, got) == sentence


def test_condition1_units_must_agree():
    env = environment([("total", "the total")], units=UNITS)
    data = env.to_dict()
    data["vocabulary"]["constants"]["when"] = {"sort": "$int", "unit": "day", "description": "w",
                                               "verbalisation": "the day paid"}
    env = Environment(data)
    with pytest.raises(VEError):
        parse_quantity_sentence(env, "The total equals GBP 1.00 plus the day paid.")


# --- (2) the plants of feature-sums2 (mkjudge.py) ----------------------------------------------------------------

SSP_DAYS = [f"{d} May 2026" for d in range(1, 32)] + [f"{d} June 2026" for d in range(1, 16)]


def ssp_env():
    return environment([("ssp_total", "the amount to which the employee has become entitled by way of statutory sick "
                                      "pay up to 15 June 2026"), ("limit", "the entitlement limit")] +
                       [(f"ssp_{k}", f"the amount of statutory sick pay to which the employee is entitled for {w}")
                        for k, w in enumerate(SSP_DAYS)])


P1 = ("The amount to which the employee has become entitled by way of statutory sick pay up to 15 June 2026 equals the sum, "
      "over each day of the period beginning with 1 May 2026 and ending with 14 June 2026, of the amount of statutory sick "
      "pay to which the employee is entitled for the day.\n"
      "If the amount to which the employee has become entitled by way of statutory sick pay up to 15 June 2026 is more "
      "than or equal to the entitlement limit, then the maximum entitlement as against the employer is reached on or "
      "before 15 June 2026.\n"
      "[OUTSIDE: other: the maximum entitlement is reached on the day on which the amount first reaches or passes the "
      "entitlement limit]")


def test_condition2_plant_p1_running_total_stopping_a_day_early_is_refused():
    env = ssp_env()
    with pytest.raises(SumRuleRunning):
        lower_written_item(env, P1)
    # Its OUTSIDE marker hides the "first day" test: refused on that alone too (F9).
    hidden = P1.replace("first reaches or passes", "is at least")
    with pytest.raises(SumRuleError, match="SumRuleOutside"):
        lower_written_item(env, hidden)
    # The sum line alone lowers, and the read-back shows the period ends on 14 June, not 15 June: the question's
    # total up to and including 15 June is not certified from it.
    [line] = [s for s in P1.split("\n") if "equals the sum" in s]
    lowered = lower_sum_item(env, line)
    assert lowered["readback"][-1].endswith("for 13 June 2026 and the amount of statutory sick pay to which the "
                                            "employee is entitled for 14 June 2026.")
    per_day = [["eq", g(f"ssp_{k}"), ["decimal", GBP, "16.00"]] for k in range(len(SSP_DAYS))]
    env2 = lowered["environment"]
    assert proves(env2, lowered["premises"] + per_day, ["eq", g("ssp_total"), ["decimal", GBP, "720.00"]])
    assert not proves(env2, lowered["premises"] + per_day, ["eq", g("ssp_total"), ["decimal", GBP, "736.00"]])


VED_ITEM = ("The price of the non-standard accessories of the vehicle equals the sum, over each accessory that is a "
            "non-standard accessory and that is attached to the vehicle when the vehicle is first registered under this "
            "Act, of the price of the accessory.")
P2 = VED_ITEM.replace(" and that is attached to the vehicle when the vehicle is first registered under this Act", "")


def ved_case():
    env = environment([("nsa", "the price of the non-standard accessories of the vehicle"),
                       ("a1p", "the price of the accessory (a1)"), ("a2p", "the price of the accessory (a2)")],
                      individuals=["a1", "a2"], predicates=["non_standard", "first_reg"])
    facts = {}
    for i in ("a1", "a2"):
        ns, fr = ["unary", "non_standard", ["const", i]], ["unary", "first_reg", ["const", i]]
        facts[f"the accessory ({i}) is a non-standard accessory"] = ns
        facts[f"the accessory ({i}) is a non-standard accessory and that is attached to the vehicle when the vehicle is "
              "first registered under this Act"] = ["and", ns, fr]
    a1, a2 = (["unary", p, ["const", i]] for i, p in (("a1", "first_reg"), ("a2", "first_reg")))
    stated = [["unary", "non_standard", ["const", "a1"]], ["unary", "non_standard", ["const", "a2"]], a1, ["not", a2]]
    case = {"items": {"accessory": ["a1", "a2"]}, "facts": stated}
    amounts = [["eq", g("a1p"), ["decimal", GBP, "800.00"]], ["eq", g("a2p"), ["decimal", GBP, "300.00"]]]
    return env, facts, case, stated + amounts


def test_condition2_plant_p2_dropped_item_condition_is_refused_the_source_answer():
    env, facts, case, premises = ved_case()
    good = lower_sum_item(env, VED_ITEM, case, facts=facts)
    plant = lower_sum_item(env, P2, case, facts=facts)
    source_answer = ["eq", g("nsa"), ["decimal", GBP, "800.00"]]  # a2 was attached after first registration
    assert proves(good["environment"], good["premises"] + premises, source_answer)
    # The plant does not certify the source's answer (VE does not give it), and its read-back shows the missing
    # guard: no line of it names the first registration.
    assert not proves(plant["environment"], plant["premises"] + premises, source_answer)
    assert any("first_reg" in str(p) for p in good["premises"])
    assert not any("first_reg" in str(p) for p in plant["premises"])
    assert plant["readback"] != good["readback"]


P3 = ("If the applicable fraction is one-half in relation to any qualifying child in the care of the person with care, then "
      "the total amount payable to the person with care is further decreased by GBP 7.00.")
CSA_SUM = ("The further decrease equals the sum, over each qualifying child that is a child for whom the applicable fraction "
           "is one-half, of the amount of GBP 7 for the qualifying child.")


def test_condition2_plant_p3_per_item_amount_as_one_total_is_refused():
    env = environment([("dec", "the further decrease"), ("c1x", "the amount of GBP 7 for the qualifying child (c1)"),
                       ("c2x", "the amount of GBP 7 for the qualifying child (c2)")],
                      individuals=["c1", "c2"], predicates=["half"])
    # The plant is no sum: the sum lowering refuses it (a per-item amount is written as a sum over the items).
    with pytest.raises(SumRuleError, match="not a written sum"):
        lower_sum_item(env, P3)
    assert lower_written_item(env, P3)["sums"] == []
    facts = {f"the qualifying child ({c}) is a child for whom the applicable fraction is one-half":
             ["unary", "half", ["const", c]] for c in ("c1", "c2")}
    stated = [["unary", "half", ["const", "c1"]], ["unary", "half", ["const", "c2"]]]
    lowered = lower_sum_item(env, CSA_SUM, {"items": {"qualifying child": ["c1", "c2"]}, "facts": stated}, facts=facts)
    premises = lowered["premises"] + stated + [["eq", g("c1x"), ["decimal", GBP, "7.00"]],
                                               ["eq", g("c2x"), ["decimal", GBP, "7.00"]]]
    assert proves(lowered["environment"], premises, ["eq", g("dec"), ["decimal", GBP, "14.00"]])
    assert not proves(lowered["environment"], premises, ["eq", g("dec"), ["decimal", GBP, "7.00"]])


# --- (3) more than 60 terms: refused at run time ---------------------------------------------------------------

def test_condition3_more_than_sixty_terms_refused_at_run_time():
    n = MAX_SUM_TERMS + 1
    env = terms_env(n)
    with pytest.raises(ResourceLimit, match="SumBound"):
        parse_quantity_sentence(env, sum_sentence(n))
    with pytest.raises(SumRuleBound):
        lower_sum_item(env, sum_sentence(n))
    chain = q(["eq", g("total"), _chain(GBP, [g(f"t{k}") for k in range(1, n + 1)])])
    canonical, _ = elaborate_quantity(env, chain)
    with pytest.raises(UnsupportedProfile, match="SumBound"):
        render_quantity_sentence(env, canonical)


def test_condition3_item_and_day_runs_over_sixty_are_refused_sixty_lowers():
    items = [f"p{k}" for k in range(1, 62)]
    env = environment([("dep", "the deposit")] + [(f"a{i}", f"the amount of the payment ({i})") for i in items])
    text = "The deposit equals the sum, over each payment, of the amount of the payment."
    with pytest.raises(SumRuleBound):
        lower_sum_item(env, text, {"items": {"payment": items}})
    assert len(lower_sum_item(env, text, {"items": {"payment": items[:60]}})["terms"]) == 60
    days = [f"{d} January 2026" for d in range(1, 32)] + [f"{d} February 2026" for d in range(1, 29)] + [
        "1 March 2026", "2 March 2026"]
    env = environment([("run", "the amount payable for the run")] +
                      [(f"pay{k}", f"the amount payable for {w}") for k, w in enumerate(days)])
    run = ("The amount payable for the run equals the sum, over each day of the period beginning with 1 January 2026 "
           "and ending with {}, of the amount payable for the day.")
    assert len(lower_sum_item(env, run.format("1 March 2026"))["terms"]) == 60
    with pytest.raises(SumRuleBound):
        lower_sum_item(env, run.format("2 March 2026"))


# --- (4) a real day-sum case: council tax, LGFA 1992 s. 10(1), the K007 run ------------------------------------

RUN = [("2026-03-30", "30 March 2026", "y2025"), ("2026-03-31", "31 March 2026", "y2025"),
       ("2026-04-01", "1 April 2026", "y2026"), ("2026-04-02", "2 April 2026", "y2026")]


def council_tax_env():
    amounts = [("run", "the amount payable for the run"), ("amtd_y2025", "the amount for band D for 2025-26"),
               ("amtd_y2026", "the amount for band D for 2026-27"), ("amt_y2025", "the amount for band H for 2025-26"),
               ("amt_y2026", "the amount for band H for 2026-27")]
    amounts += [(f"pay_{k}", f"the amount payable for {w}") for k, (_, w, _) in enumerate(RUN)]
    return environment(amounts)


def council_tax_rules():
    """s. 5(1) (band H is 18/9 of band D), s. 10(1) (a day's amount is A / D, written D x amount = A, D = 365 for
    both years as the case states) and the case's stated band D amounts; no discount applies (stated)."""
    rules = [["eq", ["scale", GBP, "9", g(f"amt_{y}")], ["scale", GBP, "18", g(f"amtd_{y}")]] for y in ("y2025", "y2026")]
    rules += [["eq", ["scale", GBP, "365", g(f"pay_{k}")], g(f"amt_{y}")] for k, (_, _, y) in enumerate(RUN)]
    rules += [["eq", g("amtd_y2025"), ["decimal", GBP, "1971.00"]], ["eq", g("amtd_y2026"), ["decimal", GBP, "2102.40"]]]
    return rules


COUNCIL_TAX_RUN = ("The amount payable for the run equals the sum, over each day of the period beginning with 30 March 2026 "
                   "and ending with 2 April 2026, of the amount payable for the day.")


def test_condition4_council_tax_day_run_across_two_financial_years():
    env = council_tax_env()
    lowered = lower_sum_item(env, COUNCIL_TAX_RUN)
    assert lowered["terms"] == ["pay_0", "pay_1", "pay_2", "pay_3"]
    assert lowered["readback"] == [
        "The amount payable for the run equals the sum of the amount payable for 30 March 2026, the amount payable for "
        "31 March 2026, the amount payable for 1 April 2026 and the amount payable for 2 April 2026."]
    assert parse_w6_sentence(env, lowered["readback"][0]) == lowered["premises"][0]
    premises = lowered["premises"] + council_tax_rules()
    # 2 x 1971.00 / 365 = 10.80 for each March day, 2 x 2102.40 / 365 = 11.52 for each April day: 44.64.
    assert proves(env, premises, ["eq", g("run"), ["decimal", GBP, "44.64"]])
    for wrong in ("44.63", "43.20", "46.08", "33.12"):  # off by a penny, all one year, a day short
        assert not proves(env, premises, ["eq", g("run"), ["decimal", GBP, wrong]])


def test_condition4_period_ends_from_case_dates_and_offsets_include_both_ends():
    env = council_tax_env()
    text = ("The amount payable for the run equals the sum, over each day of the period beginning with the day after "
            "the notice day and ending with the notice day plus 4 days, of the amount payable for the day.")
    lowered = lower_sum_item(env, text, {"dates": {"the notice day": "2026-03-29"}})
    assert lowered["terms"] == ["pay_0", "pay_1", "pay_2", "pay_3"]
    before = ("The amount payable for the run equals the sum, over each day of the period beginning with 30 March 2026 "
              "and ending with 3 April 2026 minus 1 day, of the amount payable for the day.")
    assert lower_sum_item(env, before)["terms"] == ["pay_0", "pay_1", "pay_2", "pay_3"]


def test_condition4_a_missing_day_amount_is_refused_never_zero():
    env = council_tax_env()
    with pytest.raises(SumRuleError, match="never read as 0"):
        lower_sum_item(env, COUNCIL_TAX_RUN.replace("2 April 2026", "3 April 2026"))
    # A day amount no rule fixes leaves the run unknown: nothing is certified.
    lowered = lower_sum_item(env, COUNCIL_TAX_RUN)
    rules = [r for r in council_tax_rules() if r[1] != ["scale", GBP, "365", g("pay_3")]]
    assert not proves(env, lowered["premises"] + rules, ["eq", g("run"), ["decimal", GBP, "44.64"]])
    assert not proves(env, lowered["premises"] + rules, ["eq", g("run"), ["decimal", GBP, "33.12"]])


def test_condition4_period_errors_are_refused():
    env = council_tax_env()
    with pytest.raises(SumRuleError, match="begins after it ends"):
        lower_sum_item(env, COUNCIL_TAX_RUN.replace("beginning with 30 March 2026", "beginning with 3 April 2026"))
    data = env.to_dict()
    data["vocabulary"]["constants"]["end"] = {"sort": "$int", "unit": "day", "description": "e",
                                              "verbalisation": "the end of the run"}
    concluded = Environment(data)
    with pytest.raises(SumRuleError, match="not a date every case gives"):
        lower_sum_item(concluded, COUNCIL_TAX_RUN.replace("2 April 2026", "the end of the run"))
    weeks = environment([("wk", "the total for the weeks"), ("w1", "the amount for the week beginning 6 April 2026")])
    text = ("The total for the weeks equals the sum, over each week of the period beginning with 6 April 2026 and "
            "ending with {}, of the amount for the week.")
    assert lower_sum_item(weeks, text.format("12 April 2026"))["terms"] == ["w1"]
    with pytest.raises(SumRuleError, match="partial week"):
        lower_sum_item(weeks, text.format("13 April 2026"))


# --- (5) running totals: CANNOT --------------------------------------------------------------------------------

def test_condition5_running_total_sentence_refused():
    env = ssp_env()
    for text in (
            "The amount to which the employee has become entitled by way of statutory sick pay up to 15 June 2026 equals "
            "the sum, over each day of the period beginning with 1 May 2026 and ending with the first day on which the "
            "total reaches the entitlement limit, of the amount of statutory sick pay to which the employee is entitled "
            "for the day.",
            "The amount to which the employee has become entitled by way of statutory sick pay up to 15 June 2026 equals "
            "the sum, over each day of the period beginning with 1 May 2026 and ending with 15 June 2026 on which the "
            "cumulative amount is less than the entitlement limit, of the amount of statutory sick pay to which the "
            "employee is entitled for the day."):
        with pytest.raises(SumRuleRunning):
            lower_sum_item(env, text)
    # A sum that reads its own amount in its condition is a running total, whatever its words.
    self_ref = ("The amount to which the employee has become entitled by way of statutory sick pay up to 15 June 2026 "
                "equals the sum, over each day of the period beginning with 1 May 2026 and ending with 15 June 2026 on "
                "which the amount to which the employee has become entitled by way of statutory sick pay up to 15 June "
                "2026 is less than the entitlement limit, of the amount of statutory sick pay to which the employee is "
                "entitled for the day.")
    with pytest.raises(SumRuleRunning):
        lower_sum_item(env, self_ref)
    with pytest.raises(SumRuleRunning):
        lower_sum_item(terms_env(2), "The total equals the total plus the amount of part 1.")


# --- items (2.2): completeness, open world, one item per summand -----------------------------------------------

TF_ITEM = ("The amount of the tenancy deposit equals the sum, over each payment that is held as security for the "
           "tenancy, of the amount of the payment.")


def tf():
    env = environment([("dep", "the amount of the tenancy deposit"), ("a4", "the amount of the payment (p4)"),
                       ("a5", "the amount of the payment (p5)"), ("a6", "the amount of the payment (p6)")],
                      individuals=["p4", "p5", "p6"], predicates=["held"])
    held = {i: ["unary", "held", ["const", i]] for i in ("p4", "p5", "p6")}
    facts = {f"the payment ({i}) is held as security for the tenancy": f for i, f in held.items()}
    amounts = [["eq", g("a4"), ["decimal", GBP, "5769.24"]], ["eq", g("a5"), ["decimal", GBP, "500.00"]],
               ["eq", g("a6"), ["decimal", GBP, "120.00"]]]
    return env, held, facts, amounts


def test_items_tenant_fees_deposit_over_the_payments_held_as_security():
    env, held, facts, amounts = tf()
    stated = [held["p4"], held["p5"], ["not", held["p6"]]]
    case = {"items": {"payment": ["p4", "p5", "p6"]}, "facts": stated}
    lowered = lower_sum_item(env, TF_ITEM, case, facts=facts)
    assert lowered["readback"][0] == "The payments of this case are exactly p4, p5 and p6."
    assert lowered["readback"][-1] == ("The amount of the tenancy deposit equals the sum of the amount counted for the "
                                       "payment (p4), the amount counted for the payment (p5) and the amount counted "
                                       "for the payment (p6).")
    env2 = lowered["environment"]
    for line in lowered["readback"][1:]:
        assert parse_w6_sentence(env2, line) in lowered["premises"]
    premises = lowered["premises"] + stated + amounts
    assert proves(env2, premises, ["eq", g("dep"), ["decimal", GBP, "6269.24"]])
    assert not proves(env2, premises, ["eq", g("dep"), ["decimal", GBP, "6389.24"]])


def test_items_without_the_completeness_premise_or_with_an_unknown_atom_are_refused():
    env, held, facts, _ = tf()
    with pytest.raises(SumRuleError, match="completeness premise"):
        lower_sum_item(env, TF_ITEM, {"facts": [held["p4"]]}, facts=facts)
    with pytest.raises(SumRuleError, match=r"open world.*|not stated or decided"):
        lower_sum_item(env, TF_ITEM, {"items": {"payment": ["p4", "p5"]}, "facts": [held["p4"]]}, facts=facts)
    # The caller may decide an atom the case does not state (e.g. by a Lean certificate).
    decided = lower_sum_item(env, TF_ITEM, {"items": {"payment": ["p4", "p5"]}, "facts": [held["p4"]]}, facts=facts,
                             decide=lambda atom: atom == held["p5"] or None)
    assert len(decided["terms"]) == 2
    with pytest.raises(SumRuleError, match="never read as 0"):
        lower_sum_item(env, TF_ITEM, {"items": {"payment": ["p4", "p7"]}, "facts": [held["p4"]]}, facts=facts)


def test_items_an_empty_listed_set_sums_to_zero():
    env, held, facts, _ = tf()
    lowered = lower_sum_item(env, TF_ITEM, {"items": {"payment": []}}, facts=facts)
    assert lowered["readback"][0] == "The payments of this case are exactly none."
    assert proves(env, lowered["premises"], ["eq", g("dep"), ["decimal", GBP, "0.00"]])


def test_two_sums_of_one_amount_are_refused():
    env = terms_env(3)
    with pytest.raises(SumRuleError, match="both define"):
        lower_sum_items(env, [sum_sentence(3), sum_sentence(2)])


# --- review round (Opus review of sums-build-1124: A1-A4, B1-B4) ---------------------------------------------------

def test_review_a1_a_tiling_over_sixty_refuses_the_sentence_not_a_shorter_tiling():
    n = MAX_SUM_TERMS + 1
    env = environment([("total", "the total"), ("ab", "part 1, part 2")] + [(f"t{k}", f"part {k}") for k in range(1, n + 1)])
    words = [f"part {k}" for k in range(1, n + 1)]
    sentence = f"The total equals the sum of {', '.join(words[:-1])} and {words[-1]}."
    with pytest.raises(ResourceLimit, match="SumBound"):
        parse_quantity_sentence(env, sentence)
    with pytest.raises(ResourceLimit, match="SumBound"):
        parse_w6_sentence(env, sentence)


def test_review_a2_two_sums_that_read_each_other_are_refused():
    env = environment([("x", "the first total"), ("y", "the second total"), ("a", "part a"), ("b", "part b"),
                       ("c", "part c")])
    with pytest.raises(SumRuleRunning, match="SumRuleCycle"):
        lower_sum_items(env, ["The first total equals part a plus the second total.",
                              "The second total equals part b plus the first total."])
    with pytest.raises(SumRuleRunning, match="SumRuleCycle"):
        lower_sum_items(env, ["The first total equals the sum of part a, part c and the second total.",
                              "The second total equals part b plus the first total."])
    # A chain without a cycle lowers.
    assert len(lower_sum_items(env, ["The first total equals part a plus the second total.",
                                     "The second total equals part b plus part c."])) == 2


def test_review_b1_a_sum_amount_is_defined_once_in_the_item():
    env = terms_env(3)
    with pytest.raises(SumRuleError, match="defined once"):
        lower_written_item(env, sum_sentence(3) + "\nThe total equals GBP 5.00.")
    with pytest.raises(SumRuleError, match="defined once"):
        lower_written_item(env, sum_sentence(3) + "\nIf the amount of part 1 is less than GBP 1.00, then the total "
                                                  "equals GBP 0.00.")
    assert len(lower_sum_items(env, [sum_sentence(3), sum_sentence(3)])) == 1  # the same formula twice
    # A rule with a sum in its conclusion is the W6 grammar's, not a sum definition.
    rule = "If the amount of part 3 is less than GBP 1.00, then the amount of part 3 equals the amount of part 1 plus the amount of part 2."
    assert lower_written_item(env, rule)["other"] == [rule]


def test_review_a3_outside_markers_that_may_hide_a_sum_or_condition_are_refused():
    env, held, facts, _ = tf()
    case = {"items": {"payment": ["p4"]}, "facts": [held["p4"]]}
    for marker in ("[OUTSIDE: other: a payment that has been refunded is not counted]",
                   "[OUTSIDE: other: the rent and the service charge]",
                   "[Outside: other: anything]", "[OUTSIDE : other : anything]",
                   "[OUTSIDE: multiple: five weeks' rent, unless refunded]",
                   "[OUTSIDE: product: the daily rate for each day]",
                   "[OUTSIDE - other: anything]"):
        with pytest.raises(SumRuleError, match="SumRuleOutside"):
            lower_written_item(env, TF_ITEM + "\n" + marker, case, facts=facts)
    kept = lower_written_item(env, TF_ITEM + "\n[OUTSIDE: multiple: five weeks' rent]", case, facts=facts)
    assert len(kept["sums"]) == 1 and kept["other"] == []


def detention_env():
    days = ["28 September 2025", "29 September 2025", "30 September 2025", "1 October 2025"]
    env = environment([("run", "the amount payable for the run"), ("lim", "the limit")] +
                      [(f"pay{k}", f"the amount payable for {w}") for k, w in enumerate(days)],
                      individuals=[f"d{k}" for k in range(4)], predicates=["detained"])
    facts = {f"Saul is detained on {w}": ["unary", "detained", ["const", f"d{k}"]] for k, w in enumerate(days)}
    return env, days, facts


def test_review_b4_guarded_day_sum_counts_only_the_days_that_meet_the_condition():
    env, days, facts = detention_env()
    text = ("The amount payable for the run equals the sum, over each day of the period beginning with 28 September 2025 "
            "and ending with 1 October 2025 on which Saul is detained, of the amount payable for the day.")
    stated = [facts[f"Saul is detained on {w}"] if k < 3 else ["not", facts[f"Saul is detained on {w}"]]
              for k, w in enumerate(days)]
    lowered = lower_sum_item(env, text, {"facts": stated}, facts=facts)
    assert lowered["readback"][0] == ("If \"d0\" is detained, then the amount counted for 28 September 2025 equals the "
                                      "amount payable for 28 September 2025.")
    assert lowered["readback_checks"] == ["w6"] * len(lowered["readback"])
    amounts = [["eq", g(f"pay{k}"), ["decimal", GBP, "4.08"]] for k in range(4)]
    premises = lowered["premises"] + stated + amounts
    assert proves(lowered["environment"], premises, ["eq", g("run"), ["decimal", GBP, "12.24"]])
    assert not proves(lowered["environment"], premises, ["eq", g("run"), ["decimal", GBP, "16.32"]])
    with pytest.raises(SumRuleError, match="1 October 2025"):  # open world: the last day's atom is not stated
        lower_sum_item(env, text, {"facts": stated[:3]}, facts=facts)


def test_review_a4_day_conditions_that_may_be_running_totals_are_refused():
    env, days, facts = detention_env()
    base = ("The amount payable for the run equals the sum, over each day of the period beginning with 28 September 2025 "
            "and ending with 1 October 2025 on which {}, of the amount payable for the day.")
    for cond in ("the entitlement limit has not yet been met", "the limit is not reached", "Saul is already detained"):
        with pytest.raises(SumRuleRunning):
            lower_sum_item(env, base.format(cond), {}, facts=facts)
    data = env.to_dict()
    data["vocabulary"]["constants"]["cap"] = {"sort": "$int", "unit": GBP, "description": "c",
                                              "verbalisation": "the cap amount"}
    env = Environment(data)
    compare = {f"the amount payable for the day is more than the cap amount on {w}": ["lt", g("cap"), g(f"pay{k}")]
               for k, w in enumerate(days)}
    with pytest.raises(SumRuleRunning, match="compares an amount"):
        lower_sum_item(env, base.format("the amount payable for the day is more than the cap amount"), {}, facts=compare)


def test_review_b3_a_multiple_written_as_a_sum_is_refused():
    env = environment([("cap", "the cap"), ("rent", "the weekly rent")])
    with pytest.raises(SumRuleError, match="multiple"):
        lower_sum_item(env, "The cap equals the sum of the weekly rent, the weekly rent, the weekly rent, the weekly rent "
                            "and the weekly rent.")
    with pytest.raises(SumRuleError, match="multiple"):
        lower_sum_item(env, "The cap equals the weekly rent plus the weekly rent.")


def test_review_b4_a_long_sum_inside_a_rule_reads_once():
    env = environment([("total", "the total"), ("a", "the first amount"), ("b", "the second amount"),
                       ("c", "the third amount"), ("cap", "the cap"), ("d", "the fourth amount")])
    sentence = ("If both the first amount is less than the cap and the second amount is less than the cap, then the total "
                "equals the sum of the first amount, the second amount, the third amount and the fourth amount.")
    got = parse_w6_sentence(env, sentence)
    assert got["formula"][2] == ["eq", g("total"), _chain(GBP, [g("a"), g("b"), g("c"), g("d")])]
    assert render_w6_sentence(env, got) == sentence


def test_review_b4_a_summand_in_another_unit_is_refused():
    units = dict(UNITS, hours={"scale": "1", "display": {"kind": "decimal", "label": "hours"}})
    env = environment([("dep", "the deposit")], units=units)
    data = env.to_dict()
    data["vocabulary"]["constants"]["h4"] = {"sort": "$int", "unit": "hours", "description": "h",
                                             "verbalisation": "the amount of the payment (p4)"}
    env = Environment(data)
    with pytest.raises(SumRuleError, match="unit"):
        lower_sum_item(env, "The deposit equals the sum, over each payment, of the amount of the payment.",
                       {"items": {"payment": ["p4"]}})


def test_review_b2_long_day_sum_read_back_is_checked_by_the_whole_grammar():
    days = [f"{d} January 2026" for d in range(1, 32)] + [f"{d} February 2026" for d in range(1, 30 - 1)] + ["1 March 2026"]
    env = environment([("run", "the amount payable for the run")] +
                      [(f"pay{k}", f"the amount payable for {w}") for k, w in enumerate(days)])
    lowered = lower_sum_item(env, "The amount payable for the run equals the sum, over each day of the period beginning "
                                  "with 1 January 2026 and ending with 1 March 2026, of the amount payable for the day.")
    assert len(lowered["terms"]) == 60 and lowered["readback_checks"] == ["w6"]
    assert parse_w6_sentence(env, lowered["readback"][0]) == lowered["premises"][0]
    # Terms with " is " in them can exhaust the splice: the line is then read by the quantity and core grammars.
    [line] = [s for s in P1.split("\n") if "equals the sum" in s]
    assert lower_sum_item(ssp_env(), line)["readback_checks"] == ["quantity+core"]


def test_review_b4_decide_adds_a_decided_guard_and_plurals():
    env, held, facts, amounts = tf()
    decided = lower_sum_item(env, TF_ITEM, {"items": {"payment": ["p4", "p5"]}, "facts": [held["p4"]]}, facts=facts,
                             decide=lambda atom: atom == held["p5"] or None)
    assert any(p["formula"][0] == "implies" and p["formula"][1] == held["p5"] for p in decided["premises"])
    env2, *_ = ved_case()
    _, vfacts, vcase, _ = ved_case()
    assert lower_sum_item(env2, VED_ITEM, vcase, facts=vfacts)["readback"][0] == (
        "The accessories of this case are exactly a1 and a2.")


# --- the promotion to main (Opus review of promote-sums-1126) --------------------------------------------------

@pytest.mark.parametrize("extra", [
    "GBP 1.00 equals the total.",
    "The deposit is held and the total equals GBP 1.00.",
    "If the amount of part 1 is less than GBP 1.00, then the fee is waived and the total equals GBP 1.00.",
    "The Total equals GBP 1.00."])
def test_promote_review_b1_any_other_wording_that_gives_the_sum_a_value_is_refused(extra):
    """Review B1: a value for the sum's amount in any wording (either side, inside an "and", in a rule's conclusion)
    makes the premises contradict the sum; refused, never passed on with it."""
    with pytest.raises(SumRuleError, match="defined once"):
        lower_written_item(terms_env(3), sum_sentence(3) + "\n" + extra)


def test_promote_review_b1_a_condition_on_the_sum_is_kept():
    """A rule whose condition reads the sum's amount gives it no value: kept for the caller's grammar."""
    rule = "If the total is more than GBP 5.00, then the amount of part 1 equals GBP 0.00."
    assert lower_written_item(terms_env(3), sum_sentence(3) + "\n" + rule)["other"] == [rule]


def test_promote_review_a1_a_constant_phrase_with_plus_is_a_second_reading():
    """Review A1 (an intended change of the W6 language, recorded in ve/surface/time.py): a constant whose phrase is
    itself "A plus B" over two term phrases gives the sentence a second reading, eq(total, A + B); both are kept, so the
    sentence is AmbiguousDerivation (refused, the writer renames), never one picked."""
    env = environment([("total", "the total"), ("rent", "the rent"), ("charges", "charges"),
                       ("both", "the rent plus charges")])
    for parse in (parse_quantity_sentence, parse_w6_sentence):
        with pytest.raises(AmbiguousDerivation):
            parse(env, "The total equals the rent plus charges.")
    renamed = environment([("total", "the total"), ("rent", "the rent"), ("charges", "charges"),
                           ("both", "the rent and charges together")])
    assert parse_w6_sentence(renamed, "The total equals the rent plus charges.") is not None
