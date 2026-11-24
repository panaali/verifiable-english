"""Date arithmetic in the checked core (date-arith): the `cal` and `cal_cmp` nodes Lean works out while
decoding, the input dates bound into a statement's meaning id, and the shell's lowering of the written form
(ve/surface/dates.py) with its two rules from the design challenge (C2: overlapping rules that conclude one
date are refused; C3: a date the case may lack stays an ordinary day constant).

Boundary tests (each would catch an off-by-one error at its boundary): a day
(`test_week_window_and_birthday_on_the_boundary`, the week's last day), a month end
(`test_last_day_of_the_nth_month_after`), a leap day (`test_29_february_age_is_refused_and_readings_settle_it`) and a
birthday (`test_week_window_and_birthday_on_the_boundary`)."""
from datetime import date

import pytest

from ve.environment import Environment
from ve.errors import VEError
from ve.surface.dates import DateRuleBound, DateRuleError, lower_date_item, written_exclusive
from ve.units import elaborate_quantity, quantity_meaning_id

EPOCH = date(1970, 1, 1)


def day(iso):
    return str((date.fromisoformat(iso) - EPOCH).days)


def environment(*more_days):
    constants = {"p": {"sort": "person", "description": "the person"}}
    for name, phrase in (("pa_person", "the pensionable-age date of the person"),
                         ("pa_partner", "the pensionable-age date of the partner"),
                         ("tenancy", "the date of the tenancy agreement"),
                         ("payment", "the payment date"), *more_days):
        constants[name] = {"sort": "$int", "unit": "day", "description": phrase, "verbalisation": phrase}
    return Environment({
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"person": {"description": "a person"}},
                       "predicates": {name: {"arguments": ["person"], "description": name}
                                      for name in ("man", "eligible", "higher_rate", "in_force", "exempt")},
                       "constants": constants},
        "unit_schema": "ve-units@1", "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}}})


FACTS = {f"the {role} is {word}": ["unary", pred, ["const", "p"]]
         for role in ("person", "partner")
         for word, pred in (("a man", "man"), ("eligible", "eligible"), ("paid the higher rate", "higher_rate"),
                            ("exempt", "exempt"))}
FACTS["the licence is in force"] = ["unary", "in_force", ["const", "p"]]


def closed_truth(q):
    """The truth value of a closed formula over day numbers (the `cal_cmp` results and constants-free nodes)."""
    op = q[0]
    if op in ("top", "bottom"):
        return op == "top"
    if op == "not":
        return not closed_truth(q[1])
    if op in ("and", "or", "implies"):
        a, b = closed_truth(q[1]), closed_truth(q[2])
        return {"and": a and b, "or": a or b, "implies": (not a) or b}[op]
    x, y = int(q[1][2]), int(q[2][2])
    return {"date_before": x < y, "date_after": x > y, "date_on": x == y, "date_no_later": x <= y}[op]


def condition_of(env, text, case, **kw):
    """The Lean-elaborated condition of the item's one rule."""
    lowered = lower_date_item(env, text, case, facts=FACTS, **kw)
    [premise] = [p for p in lowered["premises"] if p["formula"][0] == "implies"]
    canonical, _ = elaborate_quantity(env, premise)
    return canonical["formula"][1], lowered


# --- the nodes, through the Lean service -------------------------------------------------------------------

def test_cal_nodes_are_worked_out_in_lean_and_bind_their_input_dates():
    env = environment()
    q = {"format": "ve-quantity@1"}
    canonical, _ = elaborate_quantity(env, dict(q, formula=["date_on", ["const", "day", "pa_person"],
                                                            ["cal", ["plus_months", ["date", "1960-06-27"], "792", "none"]]]))
    assert canonical["formula"] == ["date_on", ["const", "day", "pa_person"], ["num", "day", day("2026-06-27")]]
    early = dict(q, formula=["cal_cmp", "before", ["date", "1960-01-01"], ["date", "1960-06-27"]])
    earlier = dict(q, formula=["cal_cmp", "before", ["date", "1959-01-01"], ["date", "1960-06-27"]])
    assert elaborate_quantity(env, early)[0] == elaborate_quantity(env, earlier)[0]
    assert elaborate_quantity(env, early)[0]["formula"] == ["top"]
    assert quantity_meaning_id(env, early) != quantity_meaning_id(env, earlier)
    assert quantity_meaning_id(env, dict(q, formula=["top"])) != quantity_meaning_id(env, early)
    shown, _ = elaborate_quantity(env, dict(q, formula=["cal_cmp", "on_or_after", ["date", "2026-06-27"],
                                                        ["date", "2026-06-26"]]))
    assert shown["formula"] == ["date_no_later", ["num", "day", day("2026-06-26")], ["num", "day", day("2026-06-27")]]
    for formula, message in (
            (["cal_cmp", "on", ["plus_months", ["date", "1960-02-29"], "792", "none"], ["date", "2026-02-28"]],
             r"MissingDay\(plus 792 months\)"),
            (["date_on", ["const", "day", "pa_person"], ["cal", ["date", "1969-12-31"]]], "DateRange"),
            (["cal_cmp", "on", ["date", "1899-12-31"], ["date", "1960-01-01"]], r"DateRange\(1899-12-31\)"),
            (["cal_cmp", "on", ["nth_weekday", 5, 0, 2, 2026], ["date", "2026-02-28"]], "Invalid nth weekday"),
            (["cal_cmp", "later", ["date", "2026-01-01"], ["date", "2026-01-02"]], "Invalid date comparison"),
            (["date_on", ["const", "day", "pa_person"], ["cal", ["plus_days", ["date", "2026-01-02"], "-1"]]],
             r"DateRange\(day offset\)")):
        with pytest.raises(VEError, match=message):
            elaborate_quantity(env, dict(q, formula=formula))


# --- the written form, lowered (PROPOSAL section 3's four kinds) -------------------------------------------

def test_comparison_with_a_date_before_1970_is_decided_and_bound():
    env = environment()
    text = "If the birth date of the person is on or before 2 March 1952, then the person is eligible."
    yes, _ = condition_of(env, text, {"dates": {"the birth date of the person": "1952-03-02"}})
    no, _ = condition_of(env, text, {"dates": {"the birth date of the person": "1952-03-03"}})
    assert (yes, no) == (["top"], ["bottom"])


def test_week_window_and_birthday_on_the_boundary():
    """The birthday boundary (an age is attained at the start of the birthday) and the day boundary (the
    week's last day is its start plus 6 days): born 18 May 1951, 75 on 18 May 2026, the last day of the week
    beginning the second Tuesday in May 2026 (12 May)."""
    env = environment()
    text = ("Let the start of the reference week be the second Tuesday in May of the scheme year. "
            "If the person has attained the age of 75 years on the last day of the week beginning the start of the "
            "reference week, then the person is paid the higher rate.")
    case = {"years": {"the scheme year": 2026}}
    on_birthday, _ = condition_of(env, text, dict(case, dates={"the birth date of the person": "1951-05-18"}))
    assert on_birthday == ["date_no_later", ["num", "day", day("2026-05-18")], ["num", "day", day("2026-05-18")]]
    assert closed_truth(on_birthday)
    day_after, _ = condition_of(env, text, dict(case, dates={"the birth date of the person": "1951-05-19"}))
    assert not closed_truth(day_after)
    week_start, _ = condition_of(env, text, dict(case, dates={"the birth date of the person": "1951-05-12"}))
    assert closed_truth(week_start)
    under = "If the person is under the age of 75 on 18 May 2026, then the person is eligible."
    cond, _ = condition_of(env, under, {"dates": {"the birth date of the person": "1951-05-18"}})
    assert cond[0] == "not" and not closed_truth(cond)
    cond, _ = condition_of(env, under, {"dates": {"the birth date of the person": "1951-05-19"}})
    assert closed_truth(cond)


def test_last_day_of_the_nth_month_after():
    """The month-end boundary: the last day of the 18th month after the month of 31 January 2025 is
    31 July 2026, whatever day of January."""
    env = environment(("operation", "the operation date"))
    text = ("If the operation date is on or before the last day of the 18th month after the month of the issue date, "
            "then the licence is in force.")
    for issue in ("2025-01-31", "2025-01-01"):
        last, _ = condition_of(env, text, {"dates": {"the issue date": issue}})
        assert last == ["date_no_later", ["const", "day", "operation"], ["num", "day", day("2026-07-31")]]


def test_29_february_age_is_refused_and_readings_settle_it():
    """The leap-day boundary: 29 February plus whole years lands on a missing day in a common year; with no
    reading the age is refused (C11), never guessed."""
    env = environment()
    case = {"dates": {"the birth date of the person": "1960-02-29"}}
    with pytest.raises(VEError, match="MissingDay"):
        condition_of(env, "If the person has attained the age of 66 years on 23 November 2026, then the person is "
                          "eligible.", case)
    leap, _ = condition_of(env, "If the person has attained the age of 64 years on 29 February 2024, then the person "
                                "is eligible.", case)
    assert closed_truth(leap)
    for reading, iso in (("last", "2026-02-28"), ("next", "2026-03-01")):
        cond, _ = condition_of(env, f"If the birth date of the person plus 66 years, reading: {reading} day is on "
                                    "28 February 2026, then the person is eligible.", case)
        assert closed_truth(cond) == (reading == "last"), (reading, cond)
        cond, _ = condition_of(env, f"If the birth date of the person plus 66 years, reading: {reading} day is on "
                                    f"{int(iso[8:])} {('February', 'March')[iso[6] == '3']} 2026, then the person is "
                                    "eligible.", case)
        assert closed_truth(cond)


def test_concluded_dates_and_per_role_copies():
    env = environment()
    text = ("If the birth date of the person is on or after 6 April 1950, then the pensionable-age date of the person "
            "is the birth date of the person plus 66 years.")
    case = {"dates": {"the birth date of the person": "1955-07-01", "the birth date of the partner": "1949-01-01"}}
    lowered = lower_date_item(env, text, case, facts=FACTS, roles=["the person", "the partner"])
    assert [r[1][2] for r in lowered["rules"]] == [
        ["date_on", ["const", "day", "pa_person"], ["cal", ["plus_months", ["date", "1955-07-01"], "792", "none"]]],
        ["date_on", ["const", "day", "pa_partner"], ["cal", ["plus_months", ["date", "1949-01-01"], "792", "none"]]]]
    person, partner = (elaborate_quantity(env, p)[0]["formula"] for p in lowered["premises"])
    assert person == ["implies", ["top"], ["date_on", ["const", "day", "pa_person"], ["num", "day", day("2021-07-01")]]]
    assert partner[1] == ["bottom"]


# --- C2: overlapping rules that conclude one date -------------------------------------------------------------

def test_overlapping_rules_concluding_one_date_are_refused_unless_written_exclusive():
    env = environment()
    case = {"dates": {"the birth date of the person": "1955-07-01"}}
    first = ("If the person is a man, then the pensionable-age date of the person is the birth date of the person "
             "plus 65 years. ")
    overlapping = ("If the birth date of the person is on or after 6 April 1950, then the pensionable-age date of the "
                   "person is the birth date of the person plus 66 years.")
    with pytest.raises(DateRuleError, match=r"DateRuleOverlap.*\(C2\)"):
        lower_date_item(env, first + overlapping, case, facts=FACTS)
    exclusive = ("If not the person is a man and the birth date of the person is on or after 6 April 1950, then the "
                 "pensionable-age date of the person is the birth date of the person plus 66 years.")
    lowered = lower_date_item(env, first + exclusive, case, facts=FACTS)
    assert len(lowered["rules"]) == 2
    ages = ("If the person has attained the age of 60 on 1 January 2015, then the pensionable-age date of the person "
            "is 1 January 2015. If the person is under the age of 60 on 1 January 2015, then the pensionable-age date "
            "of the person is the birth date of the person plus 60 years.")
    assert len(lower_date_item(env, ages, case, facts=FACTS)["rules"]) == 2
    assert written_exclusive(["and", ["unary", "man", ["const", "p"]], ["top"]],
                             ["not", ["unary", "man", ["const", "p"]]])
    assert not written_exclusive(["unary", "man", ["const", "p"]], ["unary", "eligible", ["const", "p"]])


# --- C3: a date the case may lack ------------------------------------------------------------------------------

def test_a_date_the_case_may_lack_is_a_day_constant_with_todays_nodes():
    env = environment()
    text = "If the date of the tenancy agreement is before 1 June 2019, then the person is exempt."
    lack = ["the date of the tenancy agreement"]
    absent = lower_date_item(env, text, {"dates": {"the date of the tenancy agreement": None}}, may_lack=lack,
                             facts=FACTS)
    assert absent["rules"][0][1][1] == ["date_before", ["const", "day", "tenancy"], ["cal", ["date", "2019-06-01"]]]
    assert absent["case_facts"] == []
    given = lower_date_item(env, text, {"dates": {"the date of the tenancy agreement": "2019-05-01"}},
                            may_lack=lack, facts=FACTS)
    assert given["rules"] == absent["rules"]
    assert given["case_facts"] == [["date_on", ["const", "day", "tenancy"], ["date", "2019-05-01"]]]
    for premise in given["premises"]:
        elaborate_quantity(env, premise)
    window = lower_date_item(env, "If the payment date is in the period of 14 days beginning with the date of the "
                                  "tenancy agreement, then the person is exempt.", {}, may_lack=lack, facts=FACTS)
    assert window["rules"][0][1][1] == ["within_days", ["const", "day", "payment"], ["const", "day", "tenancy"], "13"]
    for refused in ("Let the start be the date of the tenancy agreement.",
                    "If the payment date is before the date of the tenancy agreement plus 1 month, then the person "
                    "is exempt.",
                    "If the payment date is before the last day of the month of the date of the tenancy agreement, "
                    "then the person is exempt."):
        with pytest.raises(DateRuleError, match="C3|no reading"):
            lower_date_item(env, refused, {}, may_lack=lack, facts=FACTS)
    with pytest.raises(DateRuleError, match=r"name it in may_lack \(C3\)"):
        lower_date_item(env, text.replace("the date of the tenancy agreement", "the birth date of the person"),
                        {"dates": {"the birth date of the person": None}}, facts=FACTS)


def test_let_sentences_have_one_value_and_come_first():
    env = environment()
    with pytest.raises(DateRuleError, match="has one value"):
        lower_date_item(env, "Let the scheme year be 2026. Let the scheme year be 2027.", {})
    with pytest.raises(DateRuleError):
        lower_date_item(env, "If the payment date is before the start of the reference week, then the person is "
                             "exempt. Let the start of the reference week be 1 June 2026.", {}, facts=FACTS)


# --- the Opus build review's findings (manage-agents reviews/spare/date-arith/BUILD-REVIEW-OPUS.md) -------

def test_review_b1_a_conclusion_about_a_day_constant_always_meets_c2():
    env = environment(("relevant", "the start of the relevant period"))
    case = {"dates": {"the birth date of the person": "1955-07-01", "the date of the tenancy agreement": "2020-01-01"}}
    two = ("If the person is a man, then the start of the relevant period is on 1 June 2026. "
           "If the person is eligible, then the start of the relevant period is on 2 June 2026.")
    with pytest.raises(DateRuleError, match=r"DateRuleOverlap.*the start of the relevant period.*\(C2\)"):
        lower_date_item(env, two, case, facts=FACTS)
    lowered = lower_date_item(env, two.split(". ")[0] + ".", case, facts=FACTS)
    assert lowered["concluded"][0][0] == "relevant"
    assert lowered["rules"][0][1][2] == ["date_on", ["const", "day", "relevant"], ["cal", ["date", "2026-06-01"]]]
    with pytest.raises(DateRuleError, match=r"is a case date; a rule does not conclude it \(C2\)"):
        lower_date_item(env, "If the person is a man, then the date of the tenancy agreement is on 1 June 2026.", case,
                        facts=FACTS)
    with pytest.raises(DateRuleError, match=r"is a case date; a rule does not conclude it \(C2\)"):
        lower_date_item(env, "If the person is a man, then the date of the tenancy agreement is 1 June 2026.", {},
                        may_lack=["the date of the tenancy agreement"], facts=FACTS)


def test_review_b2_c2_compares_the_rules_of_every_item_of_a_case():
    from ve.surface.dates import lower_date_items
    env = environment()
    case = {"dates": {"the birth date of the person": "1955-07-01"}}
    first = ("If the person is a man, then the pensionable-age date of the person is the birth date of the person plus "
             "65 years.")
    second = ("If the birth date of the person is on or after 6 April 1950, then the pensionable-age date of the person "
              "is the birth date of the person plus 66 years.")
    assert len(lower_date_item(env, first, case, facts=FACTS)["rules"]) == 1
    assert len(lower_date_item(env, second, case, facts=FACTS)["rules"]) == 1
    with pytest.raises(DateRuleError, match=r"DateRuleOverlap.*\(C2\)"):
        lower_date_items(env, [first, second], case, facts=FACTS)
    exclusive = "If not the person is a man and " + second[3:]
    assert len(lower_date_items(env, [first, exclusive], case, facts=FACTS)) == 2


def test_review_b9_b10_a_date_the_case_may_lack_stays_a_constant():
    env = environment(("tenancy_partner", "the tenancy date of the partner"), ("tenancy_person", "the tenancy date of the person"))
    with pytest.raises(DateRuleError, match="never set by a Let sentence"):
        lower_date_item(env, "Let the date of the tenancy agreement be 1 June 2019.", {},
                        may_lack=["the date of the tenancy agreement"])
    text = "If the tenancy date of the person is before 1 June 2019, then the person is exempt."
    lowered = lower_date_item(env, text, {"dates": {"the tenancy date of the partner": "2019-05-01"}},
                              may_lack=["the tenancy date of the person"], facts=FACTS,
                              roles=["the person", "the partner"])
    assert [r[1][1] for r in lowered["rules"]] == [
        ["date_before", ["const", "day", "tenancy_person"], ["cal", ["date", "2019-06-01"]]],
        ["date_before", ["const", "day", "tenancy_partner"], ["cal", ["date", "2019-06-01"]]]]
    assert lowered["case_facts"] == [["date_on", ["const", "day", "tenancy_partner"], ["date", "2019-05-01"]]]


# --- the Codex review's findings and the Opus review's at 17775b3795 (manage-agents reviews/spare/date-arith/
# CODEX-REVIEW.final.md, OPUS-MISROUTED-REVIEW.final.md) ------------------------------------------------------

def _deadline_env():
    return environment(("deadline", "the deadline"), ("relevant", "the start of the relevant period"),
                       ("claim", "the day the claim is made"))


ALWAYS = "If 1 June 2026 is on 1 June 2026, then "


@pytest.mark.parametrize("second", [
    "2 June 2026 is on the deadline",            # Codex W6: reversed operands, through the W6 date_on wording
    "the deadline equals 2 June 2026",           # "equals"
    "The deadline is on 2 June 2026",            # capitalised
    "the deadline is before 1 June 2026",        # a comparison, not an equality
    "the deadline is on 2 June 2026",            # the direct wording, for reference
])
def test_codex_h1_c2_keys_on_the_lowered_conclusion_not_its_text(second):
    """H1: every rule whose conclusion lowers to a date node over a day constant concludes that constant, so
    two overlapping rules about the deadline are refused whatever the second conclusion's wording."""
    env = _deadline_env()
    text = ALWAYS + "the deadline is 1 June 2026. " + ALWAYS + second + "."
    with pytest.raises(DateRuleError, match=r"DateRuleOverlap.*deadline.*\(C2\)"):
        lower_date_item(env, text, {}, facts=FACTS)
    from ve.surface.dates import lower_date_items
    with pytest.raises(DateRuleError, match=r"DateRuleOverlap.*deadline.*\(C2\)"):
        lower_date_items(env, [ALWAYS + "the deadline is 1 June 2026.", ALWAYS + second + "."], {}, facts=FACTS)
    lowered = lower_date_item(env, ALWAYS + second + ".", {}, facts=FACTS)
    assert [c[0] for c in lowered["concluded"]] == ["deadline"]


def test_codex_h1_a_name_with_is_in_it_and_reversed_case_dates():
    env = _deadline_env()
    two = ("If the person is a man, then the day the claim is made is 1 June 2026. "
           "If the person is eligible, then the day the claim is made is 2 June 2026.")
    with pytest.raises(DateRuleError, match=r"DateRuleOverlap.*claim.*\(C2\)"):
        lower_date_item(env, two, {}, facts=FACTS)
    one = lower_date_item(env, two.split(". ")[0] + ".", {}, facts=FACTS)
    assert one["rules"][0][1][2] == ["date_on", ["const", "day", "claim"], ["cal", ["date", "2026-06-01"]]]
    case = {"dates": {"the date of the tenancy agreement": "2020-01-01"}}
    for conclusion in ("1 June 2026 is on the date of the tenancy agreement",
                       "The date of the tenancy agreement is on 1 June 2026",
                       "the deadline is on the date of the tenancy agreement"):
        if not conclusion.startswith("the deadline"):  # a given case date is substituted there: a ground date
            with pytest.raises(DateRuleError, match=r"is a case date; a rule does not conclude it \(C2\)"):
                lower_date_item(env, f"If the person is a man, then {conclusion}.", case, facts=FACTS)
        with pytest.raises(DateRuleError, match=r"is a case date; a rule does not conclude it \(C2\)"):
            lower_date_item(env, f"If the person is a man, then {conclusion}.", {},
                            may_lack=["the date of the tenancy agreement"], facts=FACTS)
    with pytest.raises(DateRuleError, match=r"compares fixed dates only"):
        lower_date_item(env, "If the person is a man, then 2 June 2026 is before 1 June 2026.", {}, facts=FACTS)


def test_codex_h2_a_let_never_names_a_date_a_rule_concludes():
    env = _deadline_env()
    codex = ("Let the deadline be 1 June 2026. If 1 June 2026 is on 1 June 2026, then the deadline is 2 June 2026. "
             "If the deadline is on 1 June 2026, then the person is eligible.")
    opus = ("Let the start of the relevant period be 1 March 2026. If the person is a man, then the start of the "
            "relevant period is 1 April 2026. If the start of the relevant period is before 15 March 2026, then the "
            "person is eligible.")
    for text in (codex, opus):
        with pytest.raises(DateRuleError, match=r"DateRuleLet.*a Let sentence does not set it"):
            lower_date_item(env, text, {}, facts=FACTS)
    from ve.surface.dates import lower_date_items
    with pytest.raises(DateRuleError, match=r"DateRuleLet"):
        lower_date_items(env, ["Let the start of the relevant period be 1 March 2026. If the start of the relevant "
                               "period is before 15 March 2026, then the person is eligible.",
                               "If the person is a man, then the start of the relevant period is 1 April 2026."],
                         {}, facts=FACTS)


def test_opus_h3_a_let_is_lowered_per_role():
    """H3: the partner (56 on the payment date) is not answered eligible from the person's (76) pension day."""
    env = environment()
    text = ("Let the pension day be the day the person attains the age of 66 years. If the payment date is on or after "
            "the pension day, then the person is eligible.")
    case = {"dates": {"the birth date of the person": "1950-01-01", "the birth date of the partner": "1970-01-01",
                      "the payment date": "2026-06-01"}}
    lowered = lower_date_item(env, text, case, facts=FACTS, roles=["the person", "the partner"])
    person, partner = (elaborate_quantity(env, p)[0]["formula"][1] for p in lowered["premises"])
    assert closed_truth(person)
    assert not closed_truth(partner)
    assert lowered["rules"][1][1][1][3] == ["plus_months", ["date", "1970-01-01"], "792", "none"]


@pytest.mark.parametrize("text", [
    # rtt2 S4 (pawhp H15 reg. 2): a fact on every day of a span
    "If the person lived in a care home throughout the qualifying week and for the 12 weeks immediately preceding "
    "the qualifying week, then the person is eligible.",
    "If the person lived in a care home throughout the qualifying week, then the deadline is 1 June 2026.",
    # rtt2 S10 (SI 2025/969 reg. 2(b)): a fact on some day of a span
    "If in respect of any day falling within the qualifying week the person is ordinarily resident in England, then "
    "the person is eligible.",
    "If the person is ordinarily resident on any day in the qualifying week, then the person is eligible.",
    "If the person is a man and the person is resident on every day of the qualifying week, then the person is "
    "eligible.",
])
def test_codex_m1_span_facts_are_refused_cannot(text):
    """M1: a fact over a span of days is refused (CANNOT), even when the caller's facts map reads it."""
    env = _deadline_env()
    condition = text[3:text.index(", then ")]
    facts = dict(FACTS)
    for part in [condition, *condition.split(" and ")]:
        facts[part] = ["unary", "eligible", ["const", "p"]]
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(env, text, {}, facts=facts)


# --- the Codex re-check's two MEDIUMs (reviews/spare/date-arith/CODEX-RECHECK.final.md) --------------------------

RECHECK_SPAN = ("If the person lived in a care home for the week immediately preceding the qualifying week, then the "
                "deadline is 1 June 2026.")
RECHECK_SPAN_FACTS = {"the person lived in a care home for the week immediately preceding the qualifying week":
                      ["unary", "resident", ["const", "p"]]}


@pytest.mark.parametrize("text, facts", [
    # the re-check's exact item and facts map: a singular unit
    (RECHECK_SPAN, RECHECK_SPAN_FACTS),
    # a written count
    ("If the person lived in a care home for twelve weeks immediately preceding the qualifying week, then the "
     "deadline is 1 June 2026.",
     {"the person lived in a care home for twelve weeks immediately preceding the qualifying week":
      ["unary", "resident", ["const", "p"]]}),
    # "a"/"an", a compound written count, a period of N units
    ("If the person lived in a care home for a month before the qualifying week, then the deadline is 1 June 2026.",
     {"the person lived in a care home for a month before the qualifying week": ["unary", "resident", ["const", "p"]]}),
    ("If the person lived in a care home for the twenty-six weeks ending with the qualifying week, then the deadline "
     "is 1 June 2026.",
     {"the person lived in a care home for the twenty-six weeks ending with the qualifying week":
      ["unary", "resident", ["const", "p"]]}),
    ("If the person lived in a care home for a period of 52 weeks prior to the qualifying week, then the deadline is "
     "1 June 2026.",
     {"the person lived in a care home for a period of 52 weeks prior to the qualifying week":
      ["unary", "resident", ["const", "p"]]}),
])
def test_codex_recheck_med1_singular_and_written_count_spans_are_refused_cannot(text, facts):
    """Re-check MEDIUM 1: a duration span with a singular unit or a written count is refused with the span's own
    reason, before the facts map is read."""
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(_deadline_env(), text, {}, roles=["the person"], may_lack=[], facts=facts)


def test_codex_recheck_med1_control_a_non_span_sentence_still_lowers():
    """The span check does not touch a sentence without a span: the same item without the span phrase lowers."""
    text = "If the person lived in a care home, then the deadline is 1 June 2026."
    lowered = lower_date_item(_deadline_env(), text, {}, roles=["the person"], may_lack=[],
                              facts={"the person lived in a care home": ["unary", "resident", ["const", "p"]]})
    assert [p["formula"] for p in lowered["premises"]] == [
        ["implies", ["unary", "resident", ["const", "p"]],
         ["date_on", ["const", "day", "deadline"], ["cal", ["date", "2026-06-01"]]]]]


# --- the Codex re-check 2's MEDIUM (reviews/spare/date-arith/CODEX-RECHECK2.final.md) ------------------------------

def _hyphen_span_item(dash, space=" "):
    clause = f"the person lived in a care home for twenty{dash}six{space}weeks before the qualifying week"
    return (f"If {clause}, then the deadline is 1 June 2026.", {clause: ["unary", "resident", ["const", "p"]]})


@pytest.mark.parametrize("dash, space", [
    ("\u2011", " "),       # the re-check's exact item and facts map: a non-breaking hyphen
    ("\u2010", " "),       # a hyphen
    ("\u2013", " "),       # an en dash
    ("\u2212", " "),       # a minus sign
    ("\u2011", "\u00a0"),  # a non-breaking hyphen and a no-break space
])
def test_codex_recheck2_unicode_hyphen_written_count_span_is_refused_cannot(dash, space):
    """Re-check 2 MEDIUM: a written count with a Unicode hyphen ("for twenty\u2011six weeks before") is refused
    CANNOT (DateRuleSpan) exactly as its ASCII form is, before the facts map is read; the control (no span) still
    lowers with the same characters elsewhere in the item."""
    text, facts = _hyphen_span_item(dash, space)
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(_deadline_env(), text, {}, roles=["the person"], may_lack=[], facts=facts)
    ascii_text, ascii_facts = _hyphen_span_item("-")
    with pytest.raises(DateRuleError, match=r"CANNOT \(DateRuleSpan\)"):
        lower_date_item(_deadline_env(), ascii_text, {}, roles=["the person"], may_lack=[], facts=ascii_facts)
    control = f"the person lived in a care{space}home twenty{dash}six years ago"
    lowered = lower_date_item(_deadline_env(), f"If {control}, then the deadline is 1 June 2026.", {},
                              roles=["the person"], may_lack=[],
                              facts={" ".join(control.split()): ["unary", "resident", ["const", "p"]]})
    assert [p["formula"] for p in lowered["premises"]] == [
        ["implies", ["unary", "resident", ["const", "p"]],
         ["date_on", ["const", "day", "deadline"], ["cal", ["date", "2026-06-01"]]]]]


def test_codex_recheck_med2_a_raw_date_term_counts_as_a_fixed_day():
    """Re-check MEDIUM 2: a conclusion that compares raw ["date", iso] terms only (here from the facts map) is
    refused as comparing fixed dates only."""
    text = "If 1 June 2026 is on 1 June 2026, then 2 June 2026 is before 1 June 2026."
    facts = {"2 June 2026 is before 1 June 2026": ["date_before", ["date", "2026-06-02"], ["date", "2026-06-01"]]}
    with pytest.raises(DateRuleError, match=r"compares fixed dates only"):
        lower_date_item(_deadline_env(), text, {}, roles=["the person"], may_lack=[], facts=facts)


# --- the Opus review's MEDIUM: one boundary test per form real items use ----------------------------------------

def _payment(text, iso, **case):
    cond, _ = condition_of(environment(), text, {"dates": {"the payment date": iso, **case}})
    return closed_truth(cond)


def test_opus_m2_period_x_to_y_includes_both_ends():
    text = "If the payment date is in the period 1 April 2026 to 30 April 2026, then the person is exempt."
    assert [_payment(text, d) for d in ("2026-03-31", "2026-04-01", "2026-04-30", "2026-05-01")] == [
        False, True, True, False]


def test_opus_m2_last_day_of_an_n_day_period():
    text = ("If the payment date is on or before the last day of the period of 14 days beginning with 1 June 2026, "
            "then the person is exempt.")
    assert [_payment(text, d) for d in ("2026-06-14", "2026-06-15")] == [True, False]


def test_opus_m2_nth_day_of_a_period():
    text = "If the payment date is on the 3rd day of the period beginning with 1 June 2026, then the person is exempt."
    assert [_payment(text, d) for d in ("2026-06-02", "2026-06-03", "2026-06-04")] == [False, True, False]


def test_opus_m2_week_forms():
    inside = "If the payment date is in the week beginning 1 June 2026, then the person is exempt."
    assert [_payment(inside, d) for d in ("2026-05-31", "2026-06-01", "2026-06-07", "2026-06-08")] == [
        False, True, True, False]
    by = "If the payment date is in or before the week beginning 1 June 2026, then the person is exempt."
    assert [_payment(by, d) for d in ("2026-06-07", "2026-06-08")] == [True, False]


def test_opus_m2_birthday_and_aged_forms():
    birthday = "If the person has reached their 18th birthday on 1 June 2026, then the person is eligible."
    assert [_payment(birthday, "2026-06-01", **{"the birth date of the person": b})
            for b in ("2008-06-01", "2008-06-02")] == [True, False]
    aged = "If the person is aged at least 65 years and 6 months on 1 June 2026, then the person is eligible."
    assert [_payment(aged, "2026-06-01", **{"the birth date of the person": b})
            for b in ("1960-12-01", "1960-12-02")] == [True, False]
    minus = "If the payment date is on or after 1 June 2026 minus 3 months, then the person is exempt."
    assert [_payment(minus, d) for d in ("2026-02-28", "2026-03-01")] == [False, True]


# --- full-gate fix round (manage-agents reviews/dri-decisions-20261124-date-arith-fullgate-fix.md item 1) ---------

@pytest.mark.parametrize("text", [
    "If the licence is valid, then the person is exempt.",  # the condition reaches the W6 grammar
    "If the person is exempt, then the payment date is before 1 June 2026.",  # the conclusion reaches it
])
def test_fullgate_checker_unavailable_in_the_w6_reading_reaches_the_caller(text, monkeypatch):
    """A CheckerUnavailable raised while reading a condition or conclusion propagates: no handler in the
    lowering turns it into a refusal or a reading (test_broad_exception_handlers_are_reviewed)."""
    from ve.errors import CheckerUnavailable
    from ve.surface import time

    def unavailable(*_a, **_k):
        raise CheckerUnavailable("backend down", operation="english.admission")

    monkeypatch.setattr(time, "parse_w6_sentence", unavailable)
    facts = {"the person is exempt": FACTS["the person is exempt"]}
    with pytest.raises(CheckerUnavailable, match="backend down"):
        lower_date_item(environment(), text, {}, facts=facts)


BOUND_FORMS = (
    "If the payment date is on or before 1 June 2026 plus {n} days, then the person is exempt.",
    "If the payment date is on or before 1 June 2026 plus 1 year and {n} months, then the person is exempt.",
    "If the person has attained the age of {n} on 1 June 2026, then the person is eligible.",
    "If the person is aged at least 65 years and {n} months on 1 June 2026, then the person is eligible.",
    "If the person is under the age of {n} on 1 June 2026, then the person is eligible.",
    "If the person has reached their {n}th birthday on 1 June 2026, then the person is eligible.",
    "If the payment date is in the period of {n} days beginning with 1 June 2026, then the person is exempt.",
    "If the payment date is on the {n}th day of the period beginning with 1 June 2026, then the person is exempt.",
    "If the payment date is on the last day of the period of {n} days beginning with 1 June 2026, "
    "then the person is exempt.",
    "If the payment date is on or before the last day of the {n}th month after the month of 1 June 2026, "
    "then the person is exempt.",
    "If the person is exempt, then the payment date is 1 June 2026 plus {n} days.",
)


@pytest.mark.parametrize("digits", (7, 41, 641, 4301))
@pytest.mark.parametrize("form", BOUND_FORMS)
def test_fullgate_a_huge_count_in_a_date_rule_is_refused_not_converted(form, digits):
    """Every count, ordinal and year a date rule reads is at most 6 digits; a longer one is CANNOT, never
    converted (test_every_int_conversion_in_ve_is_bounded_or_reviewed), at Python's lowest digit limit too."""
    import sys
    case = {"dates": {"the birth date of the person": "1960-06-27"}}
    before = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(640)
    try:
        with pytest.raises(DateRuleBound, match=r"CANNOT \(DateRuleBound\)"):
            lower_date_item(environment(), form.format(n="9" * digits), case, facts=FACTS)
    finally:
        sys.set_int_max_str_digits(before)
    # Control: at the bound (6 digits) the same form lowers or refuses for another reason, never DateRuleBound.
    try:
        lower_date_item(environment(), form.format(n="9" * 6), case, facts=FACTS)
    except DateRuleBound:
        raise AssertionError("6 digits is within the bound")
    except DateRuleError:
        pass


@pytest.mark.parametrize("year", ("9" * 41, "9" * 4301, 10 ** 50, -1), ids=("41-digits", "4301-digits", "10e50", "minus-1"))
def test_fullgate_a_huge_case_year_is_refused_not_converted(year):
    text = "If the payment date is on the first Monday in June of the scheme year, then the person is exempt."
    with pytest.raises(DateRuleBound, match=r"CANNOT \(DateRuleBound\)"):
        lower_date_item(environment(), text, {"years": {"the scheme year": year}}, facts=FACTS)
    assert lower_date_item(environment(), text, {"years": {"the scheme year": "2026"}}, facts=FACTS)["rules"]


# --- date-arith-day-after: "the day after D" and "D plus N days|weeks" for a date the case supplies ------------
# (manage-agents row date-arith-day-after-case-date). A date the case may lack is a day constant c; c + k lowers to
# today's nodes (shift_days, within_days, date_after, date_no_later), never to a ground expression.

def _value(t, consts):
    return int(t[2]) if t[0] == "num" else consts[t[2]]


def truth(q, consts):
    """The truth value of an elaborated formula with the day constants valued (day numbers): the meaning of each
    node (VE.Time.Semantics: CalShift, CalWithin over valid days)."""
    op = q[0]
    if op in ("top", "bottom"):
        return op == "top"
    if op == "not":
        return not truth(q[1], consts)
    if op in ("and", "or", "implies"):
        a, b = truth(q[1], consts), truth(q[2], consts)
        return {"and": a and b, "or": a or b, "implies": (not a) or b}[op]
    x, y = _value(q[1], consts), _value(q[2], consts)
    if op == "within_days":
        return y <= x <= y + int(q[3])
    if op == "shift_days":
        return x == y + int(q[3])
    return {"date_before": x < y, "date_after": x > y, "date_on": x == y, "date_no_later": x <= y}[op]


ENTRY = ("entry", "the date of entry")
QWEEK = "the first day of the qualifying week"


def _decide(text, dates, lack=(), env=None):
    """The rule's condition, elaborated by Lean, decided on the case's dates (constants from its case facts)."""
    env = env or environment(ENTRY, ("claim", "the date of claim"))
    lowered = lower_date_item(env, text, {"dates": dates}, may_lack=list(lack), facts=FACTS)
    consts = {}
    for fact in lowered["case_facts"]:
        consts[fact[1][2]] = int(day(fact[2][1]))
    [premise] = [p for p in lowered["premises"] if p["formula"][0] == "implies"]
    canonical, _ = elaborate_quantity(env, premise)
    return truth(canonical["formula"][1], consts)


@pytest.mark.parametrize("lack", [(), ("the date of entry",)], ids=["case-date", "may-lack"])
def test_dayafter_entry_52_weeks_plus_one_day_against_exactly_52_weeks(lack):
    """The boundary of SI 2005/3360 reg. 2(5)-style counting: an entry exactly 52 weeks (364 days) before the first
    day of the qualifying week against one 52 weeks and 1 day before, and one 52 weeks less a day before."""
    qweek = date(2021, 3, 1)  # the year before it holds 29 February 2020
    forms = {"on or after the date of entry plus 52 weeks": lambda gap: gap >= 364,
             "after the date of entry plus 52 weeks": lambda gap: gap > 364,
             "on or after the day after the date of entry plus 52 weeks": lambda gap: gap >= 365,
             "on the day after the date of entry plus 52 weeks": lambda gap: gap == 365,
             "before the date of entry plus 52 weeks": lambda gap: gap < 364,
             "on or before the day after the date of entry": lambda gap: gap <= 1}
    for form, expected in forms.items():
        text = f"If {QWEEK} is {form}, then the person is eligible."
        for gap in (363, 364, 365, 366, 1, 0):
            entry = qweek.fromordinal(qweek.toordinal() - gap)
            dates = {QWEEK: qweek.isoformat(), "the date of entry": entry.isoformat()}
            assert _decide(text, dates, lack) is expected(gap), (form, gap, lack)


@pytest.mark.parametrize("lack", [(), ("the date of entry",)], ids=["case-date", "may-lack"])
@pytest.mark.parametrize("entry,after", [("2021-01-31", "2021-02-01"), ("2021-04-30", "2021-05-01"),
                                         ("2020-12-31", "2021-01-01"), ("2021-02-28", "2021-03-01"),
                                         ("2020-02-28", "2020-02-29"), ("2020-02-29", "2020-03-01")],
                         ids=["month-end", "30-day-month-end", "year-end", "28-feb-common", "28-feb-leap", "29-feb"])
def test_dayafter_month_end_year_end_and_february(entry, after, lack):
    nxt = date.fromisoformat(after)
    for probe, expected in ((nxt, True), (date.fromordinal(nxt.toordinal() - 1), False),
                            (date.fromordinal(nxt.toordinal() + 1), False)):
        text = f"If the day after the date of entry is on {probe.day} {probe.strftime('%B')} {probe.year}, then the person is eligible."
        assert _decide(text, {"the date of entry": entry}, lack) is expected, (entry, probe, lack)


@pytest.mark.parametrize("entry,text,expected", [
    ("2021-01-31", "the day after the date of entry", "2021-02-01"),
    ("2020-12-31", "the day after the date of entry", "2021-01-01"),
    ("2020-02-28", "the day after the date of entry", "2020-02-29"),
    ("2021-02-28", "the day after the date of entry", "2021-03-01"),
    ("2020-02-20", "the date of entry plus 2 weeks", "2020-03-05"),
    ("2021-02-20", "the date of entry plus 2 weeks", "2021-03-06"),
    ("2024-02-25", "the date of entry plus 1 week", "2024-03-03"),
    ("2019-03-01", "the date of entry plus 52 weeks", "2020-02-28"),
    ("2019-03-01", "the day after the date of entry plus 52 weeks", "2020-02-29"),
    ("2020-02-29", "the date of entry plus 3 days", "2020-03-03")])
def test_dayafter_a_concluded_date_is_worked_out_in_lean(entry, text, expected):
    """A case date (every case gives it) plus days or weeks, or the day after it, concluded: Lean works it out."""
    env = environment(ENTRY)
    lowered = lower_date_item(env, f"If the person is eligible, then the payment date is {text}.",
                              {"dates": {"the date of entry": entry}}, facts=FACTS)
    [premise] = lowered["premises"]
    canonical, _ = elaborate_quantity(env, premise)
    assert canonical["formula"][2] == ["date_on", ["const", "day", "payment"], ["num", "day", day(expected)]]


@pytest.mark.parametrize("lack", [(), ("the date of entry",)], ids=["case-date", "may-lack"])
def test_dayafter_plus_weeks_across_a_leap_day_in_a_comparison(lack):
    for entry, weeks in (("2020-02-20", 2), ("2021-02-20", 2), ("2023-03-01", 52), ("2019-12-31", 9)):
        start = date.fromisoformat(entry)
        target = date.fromordinal(start.toordinal() + 7 * weeks)
        text = f"If the date of claim is on the date of entry plus {weeks} weeks, then the person is eligible."
        for probe, expected in ((target, True), (date.fromordinal(target.toordinal() - 1), False),
                                (date.fromordinal(target.toordinal() + 1), False)):
            dates = {"the date of entry": entry, "the date of claim": probe.isoformat()}
            assert _decide(text, dates, lack) is expected, (entry, weeks, probe, lack)


def test_dayafter_two_dates_the_case_may_lack_each_offset():
    text = ("If the date of claim plus 1 day is before the date of entry plus 3 days, then the person is eligible.")
    lack = ("the date of entry", "the date of claim")
    for gap in range(-1, 5):  # claim = entry + gap: claim + 1 < entry + 3 iff gap < 2
        claim = date.fromordinal(date(2020, 2, 27).toordinal() + gap)
        assert _decide(text, {"the date of entry": "2020-02-27", "the date of claim": claim.isoformat()},
                       lack) is (gap < 2), gap


def test_dayafter_a_period_beginning_with_the_day_after_a_date_the_case_may_lack():
    text = ("If the date of claim is in the period of 7 days beginning with the day after the date of entry, then "
            "the person is eligible.")
    for gap in range(-1, 10):
        claim = date.fromordinal(date(2020, 2, 25).toordinal() + gap)
        dates = {"the date of entry": "2020-02-25", "the date of claim": claim.isoformat()}
        assert _decide(text, dates, ("the date of entry",)) is (1 <= gap <= 7), gap
        assert _decide(text, dates) is (1 <= gap <= 7), gap


@pytest.mark.parametrize("form", ["the date of entry plus 1000000 days", "the date of entry plus 1234567 weeks",
                                  "the day after the date of entry plus 9999999 days"])
@pytest.mark.parametrize("lack", [(), ("the date of entry",)], ids=["case-date", "may-lack"])
def test_dayafter_a_huge_count_is_cannot(form, lack):
    text = f"If the date of claim is before {form}, then the person is eligible."
    with pytest.raises(DateRuleBound, match="CANNOT"):
        lower_date_item(environment(ENTRY, ("claim", "the date of claim")), text,
                        {"dates": {"the date of entry": "2020-01-01", "the date of claim": "2020-01-02"}},
                        may_lack=list(lack), facts=FACTS)


@pytest.mark.parametrize("form", ["the date of entry plus 999999 weeks", "the day after the date of entry plus 999999 days"])
def test_dayafter_a_total_offset_of_a_day_constant_past_999999_days_is_cannot(form):
    with pytest.raises(DateRuleBound, match="CANNOT"):
        lower_date_item(environment(ENTRY, ("claim", "the date of claim")),
                        f"If the date of claim is before {form}, then the person is eligible.",
                        {"dates": {"the date of claim": "2020-01-02"}}, may_lack=["the date of entry"], facts=FACTS)


@pytest.mark.parametrize("lack", [(), ("the date of entry",)], ids=["case-date", "may-lack"])
@pytest.mark.parametrize("text,match", [
    ("If the date of claim is before the date of entry minus 1 day, then the person is eligible.", "minus|C3"),
    ("If the date of claim is before the date of entry minus 52 weeks, then the person is eligible.", "minus|C3"),
    ("If the date of claim is before the day before the date of entry, then the person is eligible.",
     "no (?:date )?reading|No W6"),
    ("If the date of claim is 52 weeks before the date of entry, then the person is eligible.", "no (?:date )?reading|No W6"),
    ("If the person is eligible for 52 weeks before the date of entry, then the person is exempt.", "DateRuleSpan"),
    ("If the person is eligible for the week immediately preceding the day after the date of entry, then the person "
     "is exempt.", "DateRuleSpan")])
def test_dayafter_minus_and_span_wordings_stay_refused(text, match, lack):
    with pytest.raises(VEError, match=match):
        lower_date_item(environment(ENTRY, ("claim", "the date of claim")), text,
                        {"dates": {"the date of entry": "2020-01-01", "the date of claim": "2020-01-02"}},
                        may_lack=list(lack), facts=FACTS)


@pytest.mark.parametrize("text", [
    "Let the start be the day after the date of entry. If the date of claim is on the start, then the person is "
    "eligible.",
    "If the person is eligible, then the date of claim is the day after the date of entry.",
    "If the person is eligible, then the date of claim is the date of entry plus 2 weeks.",
    "If the date of claim is before the date of entry plus 1 month, then the person is eligible.",
    "If the date of claim is before the date of entry plus 2 weeks, reading: last day, then the person is eligible.",
    "If the date of claim is before the last day of the month of the day after the date of entry, then the person "
    "is eligible.",
    "If the date of claim is in or before the week beginning the day after the date of entry, then the person is "
    "eligible.",
    "If the date of claim is on the last day of the week beginning the date of entry plus 1 day, then the person is "
    "eligible."])
def test_dayafter_a_day_after_a_date_the_case_may_lack_is_compared_only(text):
    """c + k (c a date the case may lack) is never a Let value, a conclusion, a month base or a period's ground."""
    with pytest.raises(DateRuleError, match="C3|no (?:date )?reading|reading follows"):
        lower_date_item(environment(ENTRY, ("claim", "the date of claim")), text,
                        {"dates": {"the date of entry": None, "the date of claim": "2020-01-02"}},
                        may_lack=["the date of entry", "the date of claim"], facts=FACTS)


def test_dayafter_a_name_that_starts_with_the_day_after_keeps_its_reading():
    env = environment(("hearing", "the day after the hearing"))
    lowered = lower_date_item(env, "If the day after the hearing is before 1 June 2020, then the person is eligible.",
                              {"dates": {"the day after the hearing": "2020-05-01", "the hearing": "2020-05-31"}},
                              facts=FACTS)
    assert lowered["rules"][0][1][1] == ["cal_cmp", "before", ["date", "2020-05-01"], ["date", "2020-06-01"]]
