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
from ve.surface.dates import DateRuleError, lower_date_item, written_exclusive
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
    assert lowered["concluded"][0][0] == "the start of the relevant period"
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
