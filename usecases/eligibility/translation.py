"""VE translation of the Winter Fuel Payment rules (PLAN.md sections 4 and 6).

This module builds the `ve-units@1` environment, the rules as annotated
`ve-quantity@1` trees, and each profile's facts. It reads the profile fields of
cases.json and the bridge tables of PLAN.md section 4.3. It never reads a `key`
field, and it imports nothing from reference.py.

Every rule is instantiated for the two roles, `applicant` and `housemate`, because
W6a has no integer binders (PLAN section 6). A rule's `other` is the other role.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
QW0, QW1 = "2026-09-21", "2026-09-27"  # bridge B1: the week from the third Monday of September 2026
CLAIM_DEADLINE = "2027-03-31"  # reg. 4(5): 31 March following the qualifying week
ROLES = ("applicant", "housemate")
OTHER = {"applicant": "housemate", "housemate": "applicant"}
BENEFITS = {  # constant name: English name
    "state_pension": "the State Pension",
    "attendance_allowance": "Attendance Allowance",
    "income_support": "income support",
    "income_based_jsa": "income-based jobseeker's allowance",
    "pension_credit": "state pension credit",
    "income_related_esa": "income-related employment and support allowance",
    "universal_credit": "universal credit",
}
# S1 reg. 1(3) "relevant benefit", (a) to (e), in the order of the regulation.
RELEVANT = ("income_support", "income_based_jsa", "pension_credit", "income_related_esa",
            "universal_credit")

# Bridge B2 (PLAN 4.3): birth date -> ("on", date) or ("no_later", bound) for the
# pensionable-age date, from Pensions Act 1995 Sch. 4 para. 1.
PENSIONABLE_AGE = {
    "1942-01-15": ("no_later", "2018-12-05"), "1944-05-02": ("no_later", "2018-12-05"),
    "1946-09-26": ("no_later", "2018-12-05"), "1946-09-27": ("no_later", "2018-12-05"),
    "1946-09-28": ("no_later", "2018-12-05"),
    "1955-03-14": ("on", "2021-03-14"), "1957-11-02": ("on", "2023-11-02"),
    "1960-02-29": ("no_later", "2026-03-01"), "1960-06-27": ("on", "2026-09-27"),
    "1960-06-28": ("on", "2026-09-28"), "1970-08-19": ("on", "2037-08-19"),
}
# Bridge B3: birth date -> 80th birthday.
EIGHTIETH = {
    "1942-01-15": "2022-01-15", "1944-05-02": "2024-05-02", "1946-09-27": "2026-09-27",
    "1946-09-28": "2026-09-28", "1955-03-14": "2035-03-14", "1957-11-02": "2037-11-02",
    "1960-02-29": "2040-02-29", "1960-06-27": "2040-06-27", "1960-06-28": "2040-06-28",
    "1970-08-19": "2050-08-19",
}

# Integer constants per role: name suffix -> (unit, English words after "the <role>'s").
ROLE_INTEGERS = {
    "pa_date": ("day", "pensionable-age date"),
    "eightieth": ("day", "80th birthday"),
    "ew_from": ("day", "first day of ordinary residence in England and Wales"),
    "ew_last_day": ("day", "last day of ordinary residence in England and Wales"),
    "scot_ni_from": ("day", "first day of ordinary residence in Scotland or Northern Ireland"),
    "care_from": ("day", "care start date"),
    "care_until": ("day", "care end date"),
    "admitted": ("day", "hospital admission date"),
    "treatment_start": ("day", "treatment start date"),
    "discharged": ("day", "hospital discharge date"),
    "custody_from": ("day", "custody start date"),
    "release": ("day", "release date"),
    "claim_date": ("day", "claim date"),
    "care_before_week": ("elapsed_day", "care days before the week"),
    "treatment_before_week": ("elapsed_day", "treatment days before the week"),
    "income": ("gbp_penny", "total income"),
}
# Integer constants of the household (AR5): name -> (unit, English words after "the
# household's"). They date the shared home and the partnership recorded on the housemate.
HOUSEHOLD_INTEGERS = {
    "home_from": ("day", "home start date"),
    "home_until": ("day", "home end date"),
    "partner_from": ("day", "partnership start date"),
    "partner_until": ("day", "partnership end date"),
}
APPLICANT_MONEY = {
    "amount": "winter fuel payment amount",
    "recovered_amount": "recovered amount",
    "kept": "amount kept",
}

# Base (fact) predicates and derived predicates: name -> (arguments, description).
FACT_PREDICATES = {
    "partner_of": (["person", "person"], "The first person is a partner of the second (S1 reg. 1(3), taken as a fact, O3)."),
    "shares_home": (["person", "person"], "The two persons share accommodation as their mutual home in the qualifying week (S1 reg. 1(4)(b), taken as a fact)."),
    "home_start_dated": (["person", "person"], "The two persons' mutual home began on the household's home start date; otherwise it began before the qualifying week (AR5)."),
    "home_ended": (["person", "person"], "The two persons' mutual home has a last day, the household's home end date; otherwise it continues after the qualifying week (AR5)."),
    "partnership_start_dated": (["person", "person"], "The two persons became partners on the household's partnership start date; otherwise before the qualifying week (AR5)."),
    "partnership_ended": (["person", "person"], "The two persons' partnership has a last day, the household's partnership end date; otherwise it continues after the qualifying week (AR5)."),
    "paid_for_week": (["person", "benefit"], "The benefit has been, or falls to be, paid to the person for the qualifying week."),
    "ever_resident_ew": (["person"], "The person has a first day of ordinary residence in England and Wales."),
    "remains_resident_ew": (["person"], "The person's ordinary residence in England and Wales has not ended."),
    "moved_to_scotland_or_ni": (["person"], "The person has become ordinarily resident in Scotland or Northern Ireland."),
    "in_care_setting": (["person"], "The person resides in a care home, independent hospital or Polish resettlement accommodation from the care start date, and to the care end date if the stay has one."),
    "care_ended": (["person"], "The person's care stay has a last day, the care end date."),
    "inpatient": (["person"], "The person is a hospital in-patient receiving free treatment, from the admission date to the discharge date."),
    "detained_in_custody": (["person"], "The person is detained in custody from the custody start date to the release date."),
    "under_sentence": (["person"], "The person's custody is under a sentence imposed by a court."),
    "claimed": (["person"], "The person made a claim for the winter fuel payment on the claim date."),
    "paid_without_claim": (["person"], "The person is paid without a claim (S1 reg. 5(1))."),
}
DERIVED_PREDICATES = {
    "reached_pa": (["person"], "R2: the person reached pensionable age in or before the qualifying week."),
    "reached_80": (["person"], "The person reached the age of 80 in or before the qualifying week."),
    "resident_in_week": (["person"], "R3: the person is ordinarily resident in England or Wales on a day of the qualifying week."),
    "has_rb": (["person"], "R4: a relevant benefit has been, or falls to be, paid to the person for the qualifying week."),
    "in_residential_care": (["person"], "R5: the person is in residential care (S1 reg. 1(4)(a))."),
    "lives_with": (["person", "person"], "R6: the first person lives with the second (S1 reg. 1(4)(b))."),
    "home_throughout": (["person", "person"], "R7a: the two persons share their mutual home on every day of the qualifying week (AR7)."),
    "partners_throughout": (["person", "person"], "R7b: the first person is a partner of the second on every day of the qualifying week (AR7)."),
    "excluded_partner_benefit": (["person"], "R7: S1 reg. 4(2)(a) applies to the person."),
    "excluded_hospital": (["person"], "R8: S1 reg. 4(2)(b) applies to the person."),
    "excluded_custody": (["person"], "R9: S1 reg. 4(2)(c) applies to the person."),
    "excluded_care_benefit": (["person"], "R10: S1 reg. 4(3) applies to the person."),
    "excluded_moved": (["person"], "R11: S1 reg. 4(4) applies to the person."),
    "excluded_no_claim": (["person"], "R12: S1 reg. 4(5) applies to the person."),
    "excluded": (["person"], "R13: some exclusion in S1 reg. 4(2) to (5) applies to the person."),
    "entitled": (["person"], "R13: the person is entitled to a winter fuel payment for winter 2026 to 2027."),
    "recovered": (["person"], "R16: HMRC takes the payment back from the person (S2)."),
}

UNITS = {
    "day": {"scale": "1", "display": {"kind": "iso_date"}},
    "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
    "gbp_penny": {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}},
}


def environment():
    constants = {
        "applicant": {"sort": "person", "description": "The applicant P.", "verbalisation": "the applicant"},
        "housemate": {"sort": "person", "description": "The one other person H in P's household, if any.",
                      "verbalisation": "the housemate"},
    }
    for name, words in BENEFITS.items():
        constants[name] = {"sort": "benefit", "description": f"The benefit {words}.", "verbalisation": words}
    for role in ROLES:
        for suffix, (unit, words) in ROLE_INTEGERS.items():
            constants[f"{role}_{suffix}"] = {"sort": "$int", "unit": unit,
                                             "description": f"The {role}'s {words}.",
                                             "verbalisation": f"the {role}'s {words}"}
    for name, (unit, words) in HOUSEHOLD_INTEGERS.items():
        constants[name] = {"sort": "$int", "unit": unit, "description": f"The household's {words}.",
                           "verbalisation": f"the household's {words}"}
    for name, words in APPLICANT_MONEY.items():
        constants[name] = {"sort": "$int", "unit": "gbp_penny", "description": f"The applicant's {words}.",
                           "verbalisation": f"the applicant's {words}"}
    predicates = {name: {"arguments": args, "description": text}
                  for name, (args, text) in {**FACT_PREDICATES, **DERIVED_PREDICATES}.items()}
    return {"language": "ve.core@0.2",
            "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"person": {"description": "A person in the applicant's household."},
                                     "benefit": {"description": "A social security benefit."}},
                           "predicates": predicates, "constants": constants},
            "unit_schema": "ve-units@1", "units": UNITS}


# --- formula builders -------------------------------------------------------

def obj(name):
    return ["const", name]


def num(role, suffix):
    return ["const", ROLE_INTEGERS[suffix][0], f"{role}_{suffix}"]


def household(name):
    return ["const", HOUSEHOLD_INTEGERS[name][0], name]


def money_const(name):
    return ["const", "gbp_penny", name]


def day(iso):
    return ["date", iso]


def gbp(text):
    return ["decimal", "gbp_penny", text]


def days(n):
    return ["decimal", "elapsed_day", str(n)]


def U(pred, x):
    return ["unary", pred, obj(x)]


def B(pred, x, y):
    return ["binary", pred, obj(x), obj(y)]


def Not(f):
    return ["not", f]


def And(*fs):
    result = fs[-1]
    for f in reversed(fs[:-1]):
        result = ["and", f, result]
    return result


def Or(*fs):
    result = fs[-1]
    for f in reversed(fs[:-1]):
        result = ["or", f, result]
    return result


def Implies(a, b):
    return ["implies", a, b]


def Iff(a, b):
    return ["and", ["implies", a, b], ["implies", b, a]]


def key(formula):
    return json.dumps(formula, separators=(",", ":"))


def rule(rid, source, gloss, formula, role=None, defines=None):
    """A rule premise. `defines` lists what the rule determines: an atom (by its
    key) for a biconditional, or the names of integer constants it fixes."""
    if defines is None:
        defines = [key(formula[1][1])] if formula[0] == "and" and formula[1][0] == "implies" else []
    return {"id": rid if role is None else f"{rid}.{role}", "rule": rid, "role": role,
            "source": source, "gloss": gloss, "formula": formula, "defines": defines}


# --- rules (PLAN 4.1), with the mutants of PLAN section 8 -------------------

MUTANTS = {
    "M1": "R8 '> 364' as '>= 364'", "M2": "R8 counting the admission day",
    "M3": "R5 '>= 84' as '> 84'", "M4": "R16 '> 35,000' as '>= 35,000'",
    "M5": "R2 'no later than' as 'before'", "M6": "R15 age 80 strict",
    "M7": "R7 without 'partner'", "M8": "R7 without the partner's pensionable age",
    "M9": "R9 without 'under a sentence'", "M10": "R11 'before' for 'on or before'",
    "M11": "R12 'before' 31 March", "M12": "R3 'every day' for 'any day'",
    "M13": "R16 counting the partner's income", "M14": "R14 without 3(3)",
    "M15": "R4 without income support", "M16": "R4 without income-based JSA",
    "M17": "R4 without state pension credit", "M18": "R4 without income-related ESA",
    "M19": "R4 without universal credit",
    "M20": "R11 without the order of AR6", "M21": "R11 without the QW0 bound of AR6",
    "M22": "R11 without the E&W-start bound of AR6", "M23": "R6 with the other person also out of residential care",
    "M24": "R5 without the care end date", "M25": "R5 with the care end date strictly after the week",
    "M26": "R7 without the whole-week shared home", "M27": "R7 without the whole-week partnership",
    "M28": "R7 with the first days strictly before the week", "M29": "R7 with the last days strictly after the week",
    "M30": "R14 with 'throughout' read into 3(3)",
}
_DELETED_BENEFIT = {"M15": "income_support", "M16": "income_based_jsa", "M17": "pension_credit",
                    "M18": "income_related_esa", "M19": "universal_credit"}


def role_rules(r, mutant=None):
    o = OTHER[r]
    no_later = "date_before" if mutant == "M5" else "date_no_later"
    rules = [
        rule("R2", "S1 reg. 2(a)", f"The {r} has reached pensionable age in or before the week exactly when the {r}'s pensionable-age date is no later than {QW1}.",
             Iff(U("reached_pa", r), [no_later, num(r, "pa_date"), day(QW1)]), r),
        rule("R80", "S1 reg. 3(3) to (6)", f"The {r} has reached the age of 80 in or before the week exactly when the {r}'s 80th birthday is no later than {QW1}.",
             Iff(U("reached_80", r), ["date_before" if mutant == "M6" else "date_no_later", num(r, "eightieth"), day(QW1)]), r),
    ]
    if mutant == "M12":
        resident = And(U("ever_resident_ew", r), ["date_no_later", num(r, "ew_from"), day(QW0)],
                       Or(U("remains_resident_ew", r), ["date_no_later", day(QW1), num(r, "ew_last_day")]))
    else:
        resident = And(U("ever_resident_ew", r), ["date_no_later", num(r, "ew_from"), day(QW1)],
                       Or(U("remains_resident_ew", r), ["date_no_later", day(QW0), num(r, "ew_last_day")]))
    rules.append(rule("R3", "S1 reg. 2(b)", f"The {r} is ordinarily resident in England or Wales on a day of the week exactly when that residence began no later than {QW1} and either continues or has a last day no earlier than {QW0}.",
                      Iff(U("resident_in_week", r), resident), r))
    listed = [b for b in RELEVANT if b != _DELETED_BENEFIT.get(mutant)]
    rules.append(rule("R4", "S1 reg. 1(3) 'relevant benefit'", f"A relevant benefit is paid to the {r} for the week exactly when income support, income-based jobseeker's allowance, state pension credit, income-related employment and support allowance or universal credit is paid to the {r} for the week.",
                      Iff(U("has_rb", r), Or(*(B("paid_for_week", r, b) for b in listed))), r))
    rules.append(rule("R5a", "S1 reg. 1(4)(a)", f"If the {r} is in a care setting, the elapsed duration from the {r}'s care start date to {QW0} equals the {r}'s care days before the week.",
                      Implies(U("in_care_setting", r), ["elapsed_days", num(r, "care_from"), day(QW0), num(r, "care_before_week")]), r,
                      [f"{r}_care_before_week"]))
    care_days = (["lt", days(84), num(r, "care_before_week")] if mutant == "M3"
                 else ["le", days(84), num(r, "care_before_week")])
    care = [U("in_care_setting", r), care_days]
    if mutant != "M24":  # "throughout the qualifying week": a stay with a last day lasts to QW1
        care.append(Or(Not(U("care_ended", r)),
                       ["date_before" if mutant == "M25" else "date_no_later", day(QW1), num(r, "care_until")]))
    rules.append(rule("R5b", "S1 reg. 1(4)(a)", f"The {r} is in residential care exactly when the {r} is in a care setting, the {r}'s care days before the week are at least 84 days (12 weeks), and the {r}'s care stay either has no end date or ends no earlier than {QW1}.",
                      Iff(U("in_residential_care", r), And(*care)), r))
    lives = [B("shares_home", r, o), Not(U("in_residential_care", r))]  # the condition is on r only
    if mutant == "M23":
        lives.append(Not(U("in_residential_care", o)))
    rules.append(rule("R6", "S1 reg. 1(4)(b)", f"The {r} lives with the {o} exactly when they share a mutual home and the {r} is not in residential care.",
                      Iff(B("lives_with", r, o), And(*lives)), r))
    # AR7: "throughout the qualifying week" holds for a period whose first day is no later
    # than QW0 and whose last day is no earlier than QW1; an undated end lies outside QW (AR5).
    first = "date_before" if mutant == "M28" else "date_no_later"
    last = "date_before" if mutant == "M29" else "date_no_later"
    for rid, derived, base, name, gloss in (
            ("R7a", "home_throughout", "shares_home", "shared_home",
             f"The {r} and the {o} share a mutual home throughout the week exactly when they share a mutual home, and the home"),
            ("R7b", "partners_throughout", "partner_of", "partnership",
             f"The {r} is a partner of the {o} throughout the week exactly when the {r} is a partner of the {o}, and the partnership")):
        started, ended, start, end = PERIODS[name]
        rules.append(rule(rid, "S1 reg. 4(2)(a) 'throughout the qualifying week', reading AR7",
                          f"{gloss} either began before the week or has a start date no later than {QW0}, and either continues or has an end date no earlier than {QW1}.",
                          Iff(B(derived, r, o), And(B(base, r, o), Or(Not(B(started, r, o)), [first, household(start), day(QW0)]),
                                                    Or(Not(B(ended, r, o)), [last, day(QW1), household(end)]))), r))
    partner_body = [B("partner_of" if mutant == "M27" else "partners_throughout", r, o), B("lives_with", r, o),
                    B("home_throughout", r, o), U("reached_pa", o), U("has_rb", o)]
    if mutant == "M7":
        partner_body.pop(0)
    if mutant == "M8":
        partner_body.remove(U("reached_pa", o))
    if mutant == "M26":
        partner_body.remove(B("home_throughout", r, o))
    rules.append(rule("R7", "S1 reg. 4(2)(a)", f"Regulation 4(2)(a) applies to the {r} exactly when, throughout the week, the {r} is a partner of the {o} and shares a mutual home with the {o}, the {r} lives with the {o}, and the {o} has reached pensionable age and is paid a relevant benefit for the week.",
                      Iff(U("excluded_partner_benefit", r), And(*partner_body)), r))
    rules.append(rule("R8a", "S3 reg. 2(5)", f"If the {r} is an in-patient, the {r}'s treatment start date is {0 if mutant == 'M2' else 1} day after the {r}'s hospital admission date.",
                      Implies(U("inpatient", r), ["shift_days", num(r, "treatment_start"), num(r, "admitted"), "0" if mutant == "M2" else "1"]), r,
                      [f"{r}_treatment_start"]))
    rules.append(rule("R8b", "S1 reg. 4(2)(b)", f"If the {r} is an in-patient, the elapsed duration from the {r}'s treatment start date to {QW0} equals the {r}'s treatment days before the week.",
                      Implies(U("inpatient", r), ["elapsed_days", num(r, "treatment_start"), day(QW0), num(r, "treatment_before_week")]), r,
                      [f"{r}_treatment_before_week"]))
    more = (["le", days(364), num(r, "treatment_before_week")] if mutant == "M1"
            else ["lt", days(364), num(r, "treatment_before_week")])
    rules.append(rule("R8c", "S1 reg. 4(2)(b)", f"Regulation 4(2)(b) applies to the {r} exactly when the {r} is an in-patient whose treatment began no later than {QW0}, whose discharge is no earlier than {QW1}, and whose treatment days before the week are more than 364 days (52 weeks).",
                      Iff(U("excluded_hospital", r), And(U("inpatient", r), ["date_no_later", num(r, "treatment_start"), day(QW0)],
                                                         ["date_no_later", day(QW1), num(r, "discharged")], more)), r))
    custody = [U("detained_in_custody", r), U("under_sentence", r),
               ["date_before", num(r, "custody_from"), day(QW0)], ["date_after", num(r, "release"), day(QW1)]]
    if mutant == "M9":
        custody.pop(1)
    rules.append(rule("R9", "S1 reg. 4(2)(c), reading AR1", f"Regulation 4(2)(c) applies to the {r} exactly when the {r} is detained in custody under a sentence, the custody began before {QW0}, and the release is after {QW1}.",
                      Iff(U("excluded_custody", r), And(*custody)), r))
    rules.append(rule("R10", "S1 reg. 4(3)", f"Regulation 4(3) applies to the {r} exactly when the {r} is in residential care and is paid a relevant benefit for the week.",
                      Iff(U("excluded_care_benefit", r), And(U("in_residential_care", r), U("has_rb", r))), r))
    # AR6: the move comes on or after the first day of the week of E&W residence,
    # which is the later of the residence start and QW0.
    moved = [U("resident_in_week", r), U("moved_to_scotland_or_ni", r)]
    if mutant not in ("M20", "M22"):
        moved.append(["date_no_later", num(r, "ew_from"), num(r, "scot_ni_from")])
    if mutant not in ("M20", "M21"):
        moved.append(["date_no_later", day(QW0), num(r, "scot_ni_from")])
    moved.append(["date_before" if mutant == "M10" else "date_no_later", num(r, "scot_ni_from"), day(QW1)])
    rules.append(rule("R11", "S1 reg. 4(4), reading AR6", f"Regulation 4(4) applies to the {r} exactly when the {r} is resident in England or Wales on a day of the week and, no earlier than the {r}'s first day of that residence and no earlier than {QW0}, became ordinarily resident in Scotland or Northern Ireland no later than {QW1}.",
                      Iff(U("excluded_moved", r), And(*moved)), r))
    rules.append(rule("R12", "S1 reg. 4(5), (6) and 5(1)", f"Regulation 4(5) applies to the {r} exactly when the {r} is not paid without a claim and made no claim on or before {CLAIM_DEADLINE}.",
                      Iff(U("excluded_no_claim", r), And(Not(U("paid_without_claim", r)),
                                                         Not(And(U("claimed", r), ["date_before" if mutant == "M11" else "date_no_later",
                                                                                   num(r, "claim_date"), day(CLAIM_DEADLINE)])))), r))
    rules.append(rule("R13a", "S1 reg. 4(1) to (5)", f"The {r} is excluded exactly when one of regulations 4(2)(a), 4(2)(b), 4(2)(c), 4(3), 4(4) and 4(5) applies to the {r}.",
                      Iff(U("excluded", r), Or(*(U(p, r) for p in ("excluded_partner_benefit", "excluded_hospital", "excluded_custody",
                                                                    "excluded_care_benefit", "excluded_moved", "excluded_no_claim")))), r))
    rules.append(rule("R13b", "S1 regs. 2 and 4(1)", f"The {r} is entitled exactly when the {r} has reached pensionable age, is resident in England or Wales on a day of the week, and is not excluded.",
                      Iff(U("entitled", r), And(U("reached_pa", r), U("resident_in_week", r), Not(U("excluded", r)))), r))
    return rules


def amount_rules(mutant=None):
    a, h = "applicant", "housemate"
    entitled, rb, e80, care = U("entitled", a), U("has_rb", a), U("reached_80", a), U("in_residential_care", a)
    with_entitled = And(B("lives_with", a, h), U("entitled", h))
    partner_80 = And(B("partner_of", a, h), B("lives_with", a, h), U("reached_80", h))  # 3(3): "in that week"
    if mutant == "M30":
        partner_80 = And(B("partners_throughout", a, h), B("lives_with", a, h), B("home_throughout", a, h), U("reached_80", h))
    cond_2 = And(Not(rb), Or(with_entitled, care))
    cond_3 = And(rb, partner_80)
    cond_6 = And(Not(rb), Or(And(with_entitled, U("reached_80", h)), care))
    cond_5 = And(Not(rb), with_entitled, Not(U("reached_80", h)), Not(cond_6))
    rules = [
        rule("R14.2", "S1 reg. 3(2)", "If the applicant is entitled, has not reached 80, is paid no relevant benefit, and either lives with an entitled person or is in residential care, the amount is GBP 100.00.",
             Implies(And(entitled, Not(e80), cond_2), ["eq", money_const("amount"), gbp("100.00")])),
    ]
    if mutant != "M14":
        rules.append(rule("R14.3", "S1 reg. 3(3)", "If the applicant is entitled, has not reached 80, is paid a relevant benefit, and is the partner of and lives with a person who has reached 80, the amount is GBP 300.00.",
                          Implies(And(entitled, Not(e80), cond_3), ["eq", money_const("amount"), gbp("300.00")])))
    guard_1 = [Not(cond_2)] + ([] if mutant == "M14" else [Not(cond_3)])
    rules += [
        rule("R14.1", "S1 reg. 3(1)", "If the applicant is entitled, has not reached 80, and neither regulation 3(2) nor 3(3) applies, the amount is GBP 200.00.",
             Implies(And(entitled, Not(e80), *guard_1), ["eq", money_const("amount"), gbp("200.00")])),
        rule("R15.6", "S1 reg. 3(6)", "If the applicant is entitled, has reached 80, is paid no relevant benefit, and either lives with an entitled person who has reached 80 or is in residential care, the amount is GBP 150.00.",
             Implies(And(entitled, e80, cond_6), ["eq", money_const("amount"), gbp("150.00")])),
        rule("R15.5", "S1 reg. 3(5), subject to 3(6)", "If the applicant is entitled, has reached 80, is paid no relevant benefit, lives with an entitled person who has not reached 80, and regulation 3(6) does not apply, the amount is GBP 200.00.",
             Implies(And(entitled, e80, cond_5), ["eq", money_const("amount"), gbp("200.00")])),
        rule("R15.4", "S1 reg. 3(4)", "If the applicant is entitled, has reached 80, and neither regulation 3(6) nor 3(5) applies, the amount is GBP 300.00.",
             Implies(And(entitled, e80, Not(cond_6), Not(cond_5)), ["eq", money_const("amount"), gbp("300.00")])),
    ]
    income = money_const("applicant_income")
    if mutant == "M13":
        income = ["add", "gbp_penny", income, money_const("housemate_income")]
    over = (["le", gbp("35000.00"), income] if mutant == "M4" else ["lt", gbp("35000.00"), income])
    rules += [
        rule("R16a", "S2 'If your income is over £35,000'", "If the applicant is entitled and the applicant's total income is more than GBP 35000.00, HMRC takes the payment back and the recovered amount equals the amount.",
             Implies(And(entitled, over), And(U("recovered", a), ["eq", money_const("recovered_amount"), money_const("amount")]))),
        rule("R16b", "S2 'If your income is over £35,000'", "If the applicant is entitled and the applicant's total income is at most GBP 35000.00, HMRC does not take the payment back and the recovered amount equals GBP 0.00.",
             Implies(And(entitled, Not(over)), And(Not(U("recovered", a)), ["eq", money_const("recovered_amount"), gbp("0.00")]))),
        rule("R16c", "S2", "If the applicant is entitled, the amount kept equals the amount minus the recovered amount.",
             Implies(entitled, ["eq", money_const("kept"), ["add", "gbp_penny", money_const("amount"),
                                                            ["scale", "gbp_penny", "-1", money_const("recovered_amount")]]])),
    ]
    for item in rules:
        item["defines"] = {"R16a": [key(U("recovered", a)), "recovered_amount"],
                           "R16b": [key(U("recovered", a)), "recovered_amount"],
                           "R16c": ["kept"]}.get(item["rule"], ["amount"])
    return rules


B1 = rule("B1", "S1 reg. 1(3), bridge B1", f"{QW1} is 6 days after {QW0}.", ["shift_days", day(QW1), day(QW0), "6"])


def rules(mutant=None):
    """The rule premises in dependency order: each role's rules, then the amounts."""
    return [*role_rules("applicant", mutant), *role_rules("housemate", mutant), *amount_rules(mutant), B1]


# --- facts of a profile ------------------------------------------------------

# Every profile field role_facts reads: person fields, then per record the required
# and the optional fields. A field outside these would be dropped without a fact, so
# check_fields rejects it (the eligibility recheck found `care.until` dropped).
PERSON_FIELDS = {"birth", "ew_from", "ew_last_day", "scot_ni_from", "benefits", "care", "hospital",
                 "custody", "claim", "income"}
# Fields read by no rule, each with the reason. `home` names where a person without
# E&W residence lives (B08, B09); S1 depends on that only through `ew_from`, and the
# Scotland and Northern Ireland schemes are out of scope (PLAN O7).
UNREAD_FIELDS = {"home": "S1 reads E&W residence only (O7)"}
# The couple and its periods are recorded once, on the housemate (AR5): record name ->
# (start-dated fact, ended fact, start constant, end constant).
PERIODS = {"shared_home": ("home_start_dated", "home_ended", "home_from", "home_until"),
           "partnership": ("partnership_start_dated", "partnership_ended", "partner_from", "partner_until")}
HOUSEMATE_FIELDS = {"partner", *PERIODS}
RECORD_FIELDS = {"care": ({"from"}, {"until"}), "hospital": ({"admitted", "discharged"}, set()),
                 "custody": ({"from", "release", "sentenced"}, set()),
                 "claim": ({"automatic"}, {"claimed_on"}),
                 **{name: (set(), {"from", "until"}) for name in PERIODS}}


def check_fields(r, p):
    """Raise ValueError on a field or benefit of person p that no fact would carry."""
    allowed = PERSON_FIELDS | set(UNREAD_FIELDS) | (HOUSEMATE_FIELDS if r == "housemate" else set())
    if set(p) - allowed:
        raise ValueError(f"{r}: unread profile fields {sorted(set(p) - allowed)}")
    if set(p["benefits"]) - set(BENEFITS):
        raise ValueError(f"{r}: unknown benefits {sorted(set(p['benefits']) - set(BENEFITS))}")
    for name, (required, optional) in RECORD_FIELDS.items():
        record = p.get(name)
        if record is not None and not required <= set(record) <= required | optional:
            raise ValueError(f"{r}.{name}: fields {sorted(record)}, expected {sorted(required)}"
                             f" and optionally {sorted(optional)}")
    if p.get("partnership") is not None and not p.get("partner"):
        raise ValueError(f"{r}: partnership dates without a partner")
    for name in PERIODS:  # AR5: a listed period includes a day of the week
        period = p.get(name) or {}
        start, end = (date.fromisoformat(period.get(k, v)) for k, v in (("from", QW0), ("until", QW1)))
        if not start <= end or start > date.fromisoformat(QW1) or end < date.fromisoformat(QW0):
            raise ValueError(f"{r}.{name}: {period} includes no day of the qualifying week")


def _person(raw, defaults):
    return {**defaults, **raw} if raw is not None else None


def fact(fid, formula, kind="fact"):
    return {"id": fid, "kind": kind, "formula": formula}


def lit(cond, f):
    return f if cond else Not(f)


def household_facts(r, housemate):
    """Role r's facts on whether the shared home, and a partnership, recorded on the
    housemate began or ended near the week (AR5). None without a housemate, and no
    partnership facts without a partner."""
    o = OTHER[r]
    facts = []
    for name, (started, ended, _, _) in PERIODS.items():
        if housemate is None or name == "partnership" and not housemate.get("partner"):
            continue
        period = housemate.get(name) or {}
        facts.append(fact(f"{r}.{started}", lit(period.get("from") is not None, B(started, r, o))))
        facts.append(fact(f"{r}.{ended}", lit(period.get("until") is not None, B(ended, r, o))))
    return facts


def household_dates(housemate):
    """The dates of the recorded periods, once for the household."""
    facts = []
    for name, (_, _, start, end) in PERIODS.items():
        period = (housemate or {}).get(name) or {}
        for field, constant in (("from", start), ("until", end)):
            if period.get(field) is not None:
                facts.append(fact(f"household.{constant}", ["date_on", household(constant), day(period[field])]))
    return facts


def role_facts(r, p, other_present, housemate=None):
    """Facts for role r from profile person p (None when the housemate is absent)."""
    o = OTHER[r]
    facts = []
    partner = bool(p and p.get("partner")) if r == "housemate" else None
    facts.append(fact(f"{r}.shares_home", lit(other_present, B("shares_home", r, o))))
    if r == "housemate":
        facts.append(fact("housemate.partner_of", lit(partner, B("partner_of", r, o))))
    facts += household_facts(r, housemate)
    if p is None:
        return facts
    check_fields(r, p)
    for b in BENEFITS:
        facts.append(fact(f"{r}.paid.{b}", lit(b in p["benefits"], B("paid_for_week", r, b))))
    rule_pa = PENSIONABLE_AGE[p["birth"]]
    op = "date_on" if rule_pa[0] == "on" else "date_no_later"
    facts.append(fact(f"{r}.pa_date", [op, num(r, "pa_date"), day(rule_pa[1])], "bridge B2"))
    facts.append(fact(f"{r}.eightieth", ["date_on", num(r, "eightieth"), day(EIGHTIETH[p["birth"]])], "bridge B3"))
    facts.append(fact(f"{r}.ever_resident_ew", lit(p["ew_from"] is not None, U("ever_resident_ew", r))))
    if p["ew_from"] is not None:
        facts.append(fact(f"{r}.ew_from", ["date_on", num(r, "ew_from"), day(p["ew_from"])]))
        facts.append(fact(f"{r}.remains_resident_ew", lit(p["ew_last_day"] is None, U("remains_resident_ew", r))))
        if p["ew_last_day"] is not None:
            facts.append(fact(f"{r}.ew_last_day", ["date_on", num(r, "ew_last_day"), day(p["ew_last_day"])]))
    facts.append(fact(f"{r}.moved", lit(p["scot_ni_from"] is not None, U("moved_to_scotland_or_ni", r))))
    if p["scot_ni_from"] is not None:
        facts.append(fact(f"{r}.scot_ni_from", ["date_on", num(r, "scot_ni_from"), day(p["scot_ni_from"])]))
    care = p["care"]
    facts.append(fact(f"{r}.in_care_setting", lit(care is not None, U("in_care_setting", r))))
    if care is not None:
        facts.append(fact(f"{r}.care_from", ["date_on", num(r, "care_from"), day(care["from"])]))
        facts.append(fact(f"{r}.care_ended", lit(care.get("until") is not None, U("care_ended", r))))
        if care.get("until") is not None:
            facts.append(fact(f"{r}.care_until", ["date_on", num(r, "care_until"), day(care["until"])]))
    hospital = p["hospital"]
    facts.append(fact(f"{r}.inpatient", lit(hospital is not None, U("inpatient", r))))
    if hospital is not None:
        facts.append(fact(f"{r}.admitted", ["date_on", num(r, "admitted"), day(hospital["admitted"])]))
        facts.append(fact(f"{r}.discharged", ["date_on", num(r, "discharged"), day(hospital["discharged"])]))
    custody = p["custody"]
    facts.append(fact(f"{r}.detained", lit(custody is not None, U("detained_in_custody", r))))
    if custody is not None:
        facts.append(fact(f"{r}.under_sentence", lit(custody["sentenced"], U("under_sentence", r))))
        facts.append(fact(f"{r}.custody_from", ["date_on", num(r, "custody_from"), day(custody["from"])]))
        facts.append(fact(f"{r}.release", ["date_on", num(r, "release"), day(custody["release"])]))
    claim = p["claim"]
    facts.append(fact(f"{r}.paid_without_claim", lit(claim["automatic"], U("paid_without_claim", r))))
    facts.append(fact(f"{r}.claimed", lit(claim.get("claimed_on") is not None, U("claimed", r))))
    if claim.get("claimed_on") is not None:
        facts.append(fact(f"{r}.claim_date", ["date_on", num(r, "claim_date"), day(claim["claimed_on"])]))
    facts.append(fact(f"{r}.income", ["eq", num(r, "income"), gbp(p["income"])]))
    return facts


def profile_facts(case, defaults):
    """The facts of one profile. Reads the profile fields only, never `key`."""
    applicant = _person(case["applicant"], defaults)
    housemate = _person(case["housemate"], defaults)
    present = housemate is not None
    facts = role_facts("applicant", applicant, present, housemate)
    # The partner relation and the household's periods are recorded on the housemate;
    # they hold both ways.
    partner = bool(housemate and housemate.get("partner"))
    facts.insert(1, fact("applicant.partner_of", B("partner_of", "applicant", "housemate") if partner
                         else Not(B("partner_of", "applicant", "housemate"))))
    facts += role_facts("housemate", housemate, present, housemate)
    facts += household_dates(housemate)
    return facts


# --- questions ----------------------------------------------------------------

AMOUNTS = ("100.00", "150.00", "200.00", "300.00")


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def entitled_goal(positive=True):
    f = U("entitled", "applicant")
    return f if positive else Not(f)


def recovered_goal(positive=True):
    f = U("recovered", "applicant")
    return f if positive else Not(f)


def amount_goal(value):
    return ["eq", money_const("amount"), gbp(value)]


def kept_goal(value):
    return ["eq", money_const("kept"), gbp(value)]


def load_cases(path=HERE / "cases.json", *, strip_keys=True):
    """Profiles with every `key` field removed, so no builder can read one."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if strip_keys:
        data["cases"] = [{k: v for k, v in case.items() if k != "key"} for case in data["cases"]]
    return data


def elapsed(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days
