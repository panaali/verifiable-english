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
import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
# pensionable_age.py beside this file, loaded by path (this module is also loaded by path, without its
# directory on sys.path: tests/test_srccov_rl_eligibility_1121.py).
_PA_SPEC = importlib.util.spec_from_file_location("_eligibility_pensionable_age", HERE / "pensionable_age.py")
PA = sys.modules.get(_PA_SPEC.name) or importlib.util.module_from_spec(_PA_SPEC)
if _PA_SPEC.name not in sys.modules:
    sys.modules[_PA_SPEC.name] = PA
    _PA_SPEC.loader.exec_module(PA)
# Bridge B1: the qualifying week of 2026, worked out from its definition in S1 reg. 1(3) ("the week beginning on
# the third Monday in the September of that year") by pensionable_age.qualifying_week; 2026 is the year of the
# payment (S2:5 "winter 2026 to 2027"). Lean checks that QW1 is 6 days after QW0 (rule B1).
QW_YEAR = 2026
QW0, QW1 = (d.isoformat() for d in PA.qualifying_week(QW_YEAR))
GUIDE_WEEK_END = "2026-09-27"  # S2:38 "between 21 to 27 September 2026": the week the guide's cut-offs are for
W6A_FIRST_DAY = date(1970, 1, 1)  # W6a dates start here (ve/units.py day_number; probe P1)
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

# Bridges B2 and B3 (spare-ages-cutoffs): the guide's birth-date cut-offs for this qualifying week,
# read from the guide's own sentences by `guide_cutoffs`. A birth date cannot be a W6a term (every
# one is before 1970-01-01; probe P1), so `age_facts` compares it with the cut-offs in Python and
# states a bound on the person's pensionable-age date and 80th birthday against the last day of
# the week. This replaced two hand-filled tables keyed by 10 birth dates (any other birth date
# stopped the run); tests/test_spare_ages_cutoffs.py checks the cut-offs against Sch. 4 (reference.py).
# Source-coverage unit -> S2 line (wfp-print.txt) of each guide sentence the reader reads: W1-W7 of
# reviews/relb/FAULTS.md section 4 (S2:46, :55, :61, :66 and :70 are the lead-ins of the amount rows).
GUIDE_CUTOFF_LINES = {
    "S0372": 5, "S0391": 23, "S0411": 46, "S0412": 47, "S0413": 48, "S0416": 55, "S0417": 56, "S0418": 57,
    "S0419": 58, "S0420": 59, "S0421": 61, "S0422": 62, "S0423": 63, "S0426": 66, "S0427": 67, "S0428": 68,
    "S0429": 70, "S0430": 71, "S0431": 72,
}
GUIDE_LEAD_INS = {46: "You’ll get either:", 55: "You’ll get a payment of:", 61: "One of you will get a payment of either:",
                  66: "You’ll get a payment of either:", 70: "If you’re eligible you’ll get either:"}
_MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December")
_GUIDE_DATE = rf"([1-9]|[12][0-9]|3[01]) ({'|'.join(_MONTH_NAMES)}) ([0-9]{{4}})"


def _guide_date(match, first):
    return date(int(match[first + 2]), _MONTH_NAMES.index(match[first + 1]) + 1, int(match[first]))


def guide_cutoffs(lines=None):
    """(pensionable-age cut-off, 80th-birthday cut-off), read from the guide's W1-W7 sentences.

    "born on or before D" gives the first (S2:5, :23: born on or before D, pensionable age reached by
    the end of the week); "born before E" gives the second (80 by the end of the week); "born between
    E and D" is the span between them. Every amount row starts "£<n> if " and every other line is its
    lead-in, word for word. Any other wording, a date left over, or two lines that disagree raise
    ValueError: no cut-off is taken from a sentence the reader does not read whole."""
    import re
    if lines is None:
        lines = (HERE / "source" / "wfp-print.txt").read_text(encoding="utf-8").split("\n")
    pa, age80 = set(), set()
    patterns = ((rf"born between {_GUIDE_DATE} and {_GUIDE_DATE}", (age80, pa)),
                (rf"born on or before {_GUIDE_DATE}", (pa,)), (rf"born before {_GUIDE_DATE}", (age80,)))
    for unit, number in GUIDE_CUTOFF_LINES.items():
        text = lines[number - 1]
        if number in GUIDE_LEAD_INS:
            if text != GUIDE_LEAD_INS[number]:
                raise ValueError(f"{unit} (S2:{number}): not the lead-in {GUIDE_LEAD_INS[number]!r}: {text!r}")
            continue
        if number > 23 and not re.match(r"£[0-9]+ if ", text):
            raise ValueError(f"{unit} (S2:{number}): not an amount row: {text!r}")
        rest, found = text, 0
        for pattern, targets in patterns:
            for match in re.finditer(pattern, rest):
                for k, target in enumerate(targets):
                    target.add(_guide_date(match, 1 + 3 * k))
                found += 1
            rest = re.sub(pattern, "", rest)
        if not found or re.search(rf"{'|'.join(_MONTH_NAMES)}|born", rest):
            raise ValueError(f"{unit} (S2:{number}): a birth-date condition the reader does not read: {text!r}")
    if len(pa) != 1 or len(age80) != 1:
        raise ValueError(f"the guide's cut-offs disagree: pensionable age {sorted(pa)}, age 80 {sorted(age80)}")
    (pa_cutoff,), (age80_cutoff,) = pa, age80
    if not age80_cutoff < pa_cutoff:
        raise ValueError(f"the age-80 cut-off {age80_cutoff} is not before the pensionable-age cut-off {pa_cutoff}")
    return pa_cutoff, age80_cutoff


def _bound_facts(r, suffix, bounds, kind):
    """Facts for an (earliest, latest) day: one `date_on` when they are equal, else `date_after` the day before
    the earliest and `date_no_later` than the latest. A bound before 1970-01-01 (outside W6a) is dropped or
    raised to that day, which only weakens it."""
    earliest, latest = bounds
    if earliest == latest and earliest >= W6A_FIRST_DAY:
        return [fact(f"{r}.{suffix}", ["date_on", num(r, suffix), day(earliest.isoformat())], kind)]
    facts = [fact(f"{r}.{suffix}", ["date_no_later", num(r, suffix), day(max(latest, W6A_FIRST_DAY).isoformat())], kind)]
    before = earliest - timedelta(days=1)
    if before >= W6A_FIRST_DAY:
        facts.append(fact(f"{r}.{suffix}_from", ["date_after", num(r, suffix), day(before.isoformat())], kind))
    return facts


def _guide_agrees(what, bounds, by_guide):
    """Refuse (ValueError) where Sch. 4 decides "by the end of the week" one way and the guide's cut-off the other."""
    end = date.fromisoformat(QW1)
    if (bounds[1] <= end and not by_guide) or (bounds[0] > end and by_guide):
        raise ValueError(f"{what}: Sch. 4 gives {bounds[0]} to {bounds[1]}, the guide's cut-off the other side of {QW1}")


def age_facts(r, birth):
    """Bridges B2 and B3 for role r: the pensionable-age date by Pensions Act 1995 Sch. 4 para. 1 and the 80th
    birthday, worked out from the birth date by `pensionable_age` (which reads Sch. 4's own text), as days or
    bounds. For the guide's week (S2:38) the guide's cut-offs (born on or before the first; born before the
    second) must agree with them, else the profile is refused: two readings of the source, one answer."""
    born = date.fromisoformat(birth)
    if born > date.fromisoformat(QW1):
        raise ValueError(f"{r}: born {birth}, after the qualifying week")
    pa, age80 = PA.pensionable_age(born, schedule=_schedule4()), PA.eightieth_birthday(born)
    if QW1 == GUIDE_WEEK_END:
        pa_cutoff, age80_cutoff = guide_cutoffs()
        _guide_agrees(f"{r} pensionable age", pa, born <= pa_cutoff)
        _guide_agrees(f"{r} age 80", age80, born < age80_cutoff)
    return [*_bound_facts(r, "pa_date", pa, "bridge B2"), *_bound_facts(r, "eightieth", age80, "bridge B3")]


_SCHEDULE4 = []


def _schedule4():
    if not _SCHEDULE4:
        _SCHEDULE4.append(PA.read_schedule4())
    return _SCHEDULE4[0]

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

# Guide predicates (srccov-rl-eligibility-1121): base predicates of the guide rules G1 to G7
# (guide_rules). No profile fact fixes one, so each is open in every profile. Each legend quotes
# the S2 words it stands for, word for word (the line in the comment).
GUIDE_PREDICATES = {
    "affects_other_benefits": (["person"], "The money the person gets affects the person's other benefits (S2: “affect your other benefits”)."),  # S2:39
    "jointly_claims_benefits": (["person"], "The person and the person's partner jointly claim any of the benefits, which are Pension Credit, Universal Credit and income-related Employment and Support Allowance (S2: “If you and your partner jointly claim any of the benefits”; “Pension Credit”; “Universal Credit”; “income-related Employment and Support Allowance (ESA)”)."),  # S2:60; the benefits S2:51-53
    "paid_into_usual_account": (["person"], "The person is paid into the bank account the person's benefits are usually paid into (S2: “paid into the bank account your benefits are usually paid into”)."),  # S2:64
    "tax_code_changed": (["person"], "HMRC changes the person's tax code to pay back the person's winter fuel payment (S2: “If HMRC changes your tax code to pay back your Winter Fuel Payment”)."),  # S2:145
    "tax_deducted_increases": (["person"], "The tax deducted from the person's wages, salary or pension increases (S2: “the tax deducted from your wages, salary or pension will increase”)."),  # S2:145
    "two_payments_to_collect": (["person"], "HMRC needs to collect 2 payments from the person (S2: “If HMRC needs to collect 2 payments”)."),  # S2:147
    "two_payments_through_tax_code": (["person"], "HMRC collects 2 payments through the person's tax code at the same time (S2: “HMRC will collect 2 payments through your tax code at the same time”)."),  # S2:148
    "more_tax_each_month": (["person"], "The person pays more tax each month (S2: “you will pay more tax each month”)."),  # S2:148
    "completes_self_assessment": (["person"], "The person completes a Self Assessment tax return (S2: “If you complete a Self Assessment tax return”)."),  # S2:152
    "files_online": (["person"], "The person files tax returns online (S2: “If you file tax returns online”)."),  # S2:154
    "included_automatically": (["person"], "HMRC includes the amount of the person's winter fuel payment in the person's tax return automatically (S2: “HMRC will usually include the amount automatically”)."),  # S2:154
    "shown_as_wfp_charge": (["person"], "The amount shows on the person's tax return as the Winter Fuel Payment charge (S2: “It will show as the ‘Winter Fuel Payment charge’”)."),  # S2:154
    "in_tax_calculation": (["person"], "The amount is included in the person's tax calculation (S2: “will be included in your tax calculation”)."),  # S2:154
    "opted_out": (["person"], "The person has opted out of receiving the winter fuel payment (S2: “opt out of receiving Winter Fuel Payment”)."),  # S2:143
}
FACT_PREDICATES.update(GUIDE_PREDICATES)

# Source conditions the rules read with existing predicates (S2 words -> the formula, built by
# `source_condition`). The amount rules and the guide rules both read them from here, and the
# guide-context test (tests/test_srccov_rl_eligibility_1121.py) checks every S2 heading or
# lead-in condition a guide sentence sits under is either quoted by the legend of a guide
# predicate in the rule's antecedent or is one of these, conjoined in the antecedent.
LIVES_WITH_ELIGIBLE = "If you live with someone else who’s eligible for the Winter Fuel Payment"  # S2:49
SOURCE_CONDITIONS = {
    LIVES_WITH_ELIGIBLE:
        (("binary", "lives_with", "applicant", "housemate"), ("unary", "entitled", "housemate")),
}

# Guide sentences (srccov-rl-eligibility-1121): each S2 sentence a guide rule carries, word for
# word (rule -> (source-coverage unit, S2 line, sentence)). The rule's gloss ends with it.
GUIDE_SENTENCES = {
    "G1": ("S0406", 39, "Any money you get will not affect your other benefits."),
    "G2": ("S0424", 64, "You’ll be paid into the bank account your benefits are usually paid into."),
    "G3": ("S0465", 145, "This means the tax deducted from your wages, salary or pension will increase."),
    "G4": ("S0467", 148, "HMRC will collect 2 payments through your tax code at the same time."),
    "G5": ("S0468", 148, "This means you will pay more tax each month."),
    "G6": ("S0474", 154, "It will show as the ‘Winter Fuel Payment charge’ and will be included in your tax calculation."),
    "G7": ("S0483", 166, "If you do not opt out and your total income is over £35,000, you’ll receive the Winter Fuel Payment but HMRC will take it back."),
}

# Source definitions and wording, word for word from source/*.txt (one string per source line,
# the line breaks as single spaces): S1 = uksi-2025-969-made.txt, S2 = wfp-print.txt, S3 =
# uksi-2005-3360-reg2.txt. Each is appended to the legend of the predicates that use the term
# (LEGEND_DEFINITIONS) or, for the qualifying week, to the gloss of bridge B1.
DEFINITIONS = {
    "pensionable age": " ".join((  # S1:16, S1:34
        "(3) In these Regulations—",
        "“pensionable age” has the meaning given by the rules in paragraph 1 of Schedule 4 to the Pensions Act 1995(9);")),
    "regulation 2": "2. Subject to regulation 4, the Secretary of State must pay a winter fuel payment out of the social fund to a person (“P”) where—",  # S1:60
    "qualifying week": " ".join((  # S1:40; S2:38
        "“qualifying week” means in respect of any year the week beginning on the third Monday in the September of that year;",
        "The amount you get is based on when you were born and your circumstances between 21 to 27 September 2026. This is called the ‘qualifying week’.")),
    "partner": "“partner” means a member of a couple or a polygamous marriage;",  # S1:33
    "couple": " ".join((  # S1:22-26
        "“couple” means—", "(a)",
        "two people who are married to, or civil partners of, each other and are members of the same household, or", "(b)",
        "two people who are not married to, or civil partners of, each other but are living together as if they were a married couple or civil partners;")),
    "polygamous marriage": " ".join((  # S1:35-39
        "“polygamous marriage” means any marriage which took place under the laws of a country which permits polygamy where—", "(a)",
        "any member of the marriage is for the time being married to more than one person, and", "(b)",
        "all the members of the marriage are members of the same household;")),
    "residential care": " ".join((  # S1:52-57
        "(4) In these Regulations, a person—",
        "(a)is in residential care if, disregarding any period of temporary absence, they reside in—",
        "(i)a care home,", "(ii)an independent hospital, or",
        "(iii)accommodation provided under section 3(1) of the Polish Resettlement Act 1947(14),",
        "throughout the qualifying week and the period of at least 12 weeks ending immediately before the qualifying week;")),
    "lives with": "(b)lives with a person if, disregarding any period of temporary absence, they share accommodation with one or more persons as their mutual home and they are not in residential care.",  # S1:58
    "care home": " ".join((  # S1:17-21
        "“care home”—", "(a)", "in England, has the meaning assigned to it by section 3 of the Care Standards Act 2000(4);", "(b)",
        "in Wales, means accommodation the provision of which, together with nursing or care, is a care home service as defined in paragraph 1 of Schedule 1 to the Regulation and Inspection of Social Care (Wales) Act 2016(5) which is provided wholly or mainly to persons aged 18 or over;")),
    "independent hospital": " ".join((  # S1:28-32
        "“independent hospital”—", "(a)",
        "in England, means a hospital as defined by section 275(1) of the National Health Service Act 2006(7) that is not a health service hospital as defined by that section;", "(b)",
        "in Wales, means a hospital as defined by section 206(1) of the National Health Service (Wales) Act 2006(8) that is not a health service hospital as defined by that section;")),
    "free in-patient treatment": " ".join((  # S1:27; S3:9-12
        "“free in-patient treatment” is to be construed in accordance with regulation 2(4) and (5) of the Social Security (Hospital In-Patients) Regulations 2005(6);",
        "(4) For the purposes of this regulation, a person shall be regarded as receiving or having received free in-patient treatment for any period for which he is or has been maintained free of charge while undergoing medical or other treatment as an in-patient—",
        "(a)in a hospital or similar institution under the National Health Service Act 1977 M2, the National Health Service (Scotland) Act 1978 M3 or the National Health Service and Community Care Act 1990 M4, or",
        "(b)in a hospital or similar institution maintained or administered by the Defence Council,",
        "and such a person shall for the purposes of sub-paragraph (a) be regarded as being maintained free of charge in a hospital or similar institution unless his accommodation and services are provided under section 65 of the National Health Service Act 1977, section 57 of the National Health Service (Scotland) Act 1978 M5 or paragraph 14 of Schedule 2 to the National Health Service and Community Care Act 1990.")),
    "total income": " ".join((  # S2:140; S2:141, its second sentence
        "Your partner’s income does not count towards your total income.",
        "You’ll need to provide the total amount of income you expect to receive in the tax year before any deductions.")),
    "HMRC": "If your total income is over £35,000, HM Revenue and Customs (HMRC) will take your Winter Fuel Payment back.",  # S2:139
}
_PARTNER_TERMS = ("partner", "couple", "polygamous marriage")
# Predicate -> the DEFINITIONS its legend carries, after its own description.
LEGEND_DEFINITIONS = {
    "partner_of": _PARTNER_TERMS, "partners_throughout": _PARTNER_TERMS, "partner_at_home": _PARTNER_TERMS,
    "excluded_partner_benefit": _PARTNER_TERMS,
    "in_residential_care": ("residential care",),
    "lives_with": ("lives with",),
    "in_care_setting": ("care home", "independent hospital"),
    "inpatient": ("free in-patient treatment",),
    "recovered": ("total income", "HMRC"),
    "reached_pa": ("pensionable age",),
    "entitled": ("regulation 2",),
}

# Out of scope (srccov-eligibility-1119): source units that state no rule of the winter fuel
# payment, so no rule, fact or legend carries them. Each group names the content and its kind;
# each unit is given by its source-coverage unit id and the line where it starts (S1, S2 as
# above; Sch4 = ukpga-1995-26-sch4.txt).
# - metadata, out of scope: the enacting formula naming the powers the Regulations are made
#   under, the impact assessment statement, and the guide's alternative formats notice:
#   S0001 S1:11, S0092 S1:133, S0374 S2:6.
# - title, out of scope: the headings of Schedule 4 and of the sections it inserts, and the
#   chapter headings of the guide: S0114 Sch4:3, S0223 Sch4:252, S0243 Sch4:272,
#   S0268 Sch4:312, S0293 Sch4:357, S0401 S2:35, S0432 S2:73, S0441 S2:104, S0446 S2:110,
#   S0480 S2:163.
# - navigation or page furniture, out of scope: the Explanatory Note's pointer to regulation 3,
#   the header rows of the Schedule 4 tables, the guide's scam warning and its contact channel
#   lines: S0073 S1:114, S0164 Sch4:123, S0177 Sch4:152, S0195 Sch4:191, S0386 S2:16,
#   S0451 S2:121, S0487 S2:175.
# - bare citation or pointer, out of scope: footnotes that point to a definition in a cited Act,
#   and the guide's pointers to other pages: S0093 S1:135, S0096 S1:137, S0098 S1:137,
#   S0455 S2:137, S0459 S2:141, S0479 S2:162.
# - change log, out of scope: regulations 6 and 7 (a consequential amendment of the Social
#   Security (Claims and Payments) Regulations 1987, and the revocation of the 2024
#   Regulations) and the Explanatory Note's summary of them: S0067 S1:100, S0068 S1:102,
#   S0069 S1:103, S0070 S1:104, S0090 S1:131, S0091 S1:132.
# - history, out of scope: the footnotes giving the amendment history of the Acts and
#   instruments S1 cites: S0094 S1:135, S0095 S1:135, S0097 S1:137, S0099 S1:137,
#   S0100 S1:137, S0101 S1:137, S0102 S1:137, S0103 S1:139, S0104 S1:141, S0105 S1:142,
#   S0106 S1:147, S0107 S1:151, S0108 S1:161, S0109 S1:163, S0110 S1:164, S0111 S1:165,
#   S0112 S1:166, S0113 S1:168.
# - editorial annotation, out of scope: the opening of the Explanatory Note, which is not part
#   of the Regulations: S0071 S1:112.
# - rationale, out of scope: why a change of circumstances is reported: S0449 S2:114.


def legend(name, text):
    """A predicate's description: its own text, then the source definitions it carries."""
    return " ".join((text, *(DEFINITIONS[term] for term in LEGEND_DEFINITIONS.get(name, ()))))


DERIVED_PREDICATES = {
    "reached_pa": (["person"], "R2: the person reached pensionable age in or before the qualifying week."),
    "reached_80": (["person"], "The person reached the age of 80 in or before the qualifying week."),
    "resident_in_week": (["person"], "R3: the person is ordinarily resident in England or Wales on a day of the qualifying week."),
    "has_rb": (["person"], "R4: a relevant benefit has been, or falls to be, paid to the person for the qualifying week."),
    "in_residential_care": (["person"], "R5: the person is in residential care (S1 reg. 1(4)(a))."),
    "lives_with": (["person", "person"], "R6: the first person lives with the second (S1 reg. 1(4)(b))."),
    "home_throughout": (["person", "person"], "R7a: the two persons share their mutual home on every day of the qualifying week (AR7)."),
    "partners_throughout": (["person", "person"], "R7b: the first person is a partner of the second on every day of the qualifying week (AR7)."),
    "partner_at_home": (["person", "person"], "R14a: on one day of the qualifying week, the first person is a partner of the second and they share a mutual home (AR8)."),
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
    predicates = {name: {"arguments": args, "description": legend(name, text)}
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


def source_condition(words):
    """The formula a SOURCE_CONDITIONS entry reads its S2 words as: the conjunction of its atoms."""
    return And(*(U(pred, *args) if kind == "unary" else B(pred, *args)
                 for kind, pred, *args in SOURCE_CONDITIONS[words]))


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
    "M31": "R14 without the common day of AR8", "M32": "R14 with the bounds of AR8 strict",
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
    with_entitled = source_condition(LIVES_WITH_ELIGIBLE)
    # AR8: 3(3) "in that week, P is the partner of and living with" asks for one day of
    # QW in the partnership and in the shared home. Each includes a day of QW (AR5), so
    # they share one exactly when each begins no later than the other ends; an undated
    # start lies before QW and an undated end after it.
    bound = "date_before" if mutant == "M32" else "date_no_later"
    common_day = rule("R14a", "S1 reg. 3(3) 'in that week', reading AR8", "The applicant is a partner of the housemate and they share a mutual home on one day of the week exactly when the applicant is a partner of the housemate, they share a mutual home, the home either began before the week or began no later than the partnership's end date if the partnership has one, and the partnership either began before the week or began no later than the home's end date if the home has one.",
                      Iff(B("partner_at_home", a, h),
                          And(B("partner_of", a, h), B("shares_home", a, h),
                              Or(Not(B("home_start_dated", a, h)), Not(B("partnership_ended", a, h)),
                                 [bound, household("home_from"), household("partner_until")]),
                              Or(Not(B("partnership_start_dated", a, h)), Not(B("home_ended", a, h)),
                                 [bound, household("partner_from"), household("home_until")]))))
    partner_80 = And(B("partner_of" if mutant == "M31" else "partner_at_home", a, h), B("lives_with", a, h),
                     U("reached_80", h))  # 3(3): "in that week", on a common day (AR8)
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
        rules.append(rule("R14.3", "S1 reg. 3(3), reading AR8", "If the applicant is entitled, has not reached 80, is paid a relevant benefit, and, on one day of the week, is the partner of and lives with a person who has reached 80, the amount is GBP 300.00.",
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
    return [common_day, *rules]


def guide_rules():
    """The guide rules G1 to G7 (srccov-rl-eligibility-1121): S2 sentences a plain rule line
    carries, for the applicant. Each gloss reads the formula, then gives the sentence word for
    word (GUIDE_SENTENCES). Each rule defines nothing, so no staged step uses it, and each holds
    when its guide predicates are false, so it is true in every profile's keyed model."""
    a = "applicant"
    over = ["lt", gbp("35000.00"), money_const("applicant_income")]
    lines = {
        "G1": ("If the applicant is entitled, the money the applicant gets does not affect the applicant's other benefits.",
               Implies(U("entitled", a), Not(U("affects_other_benefits", a)))),
        "G2": ("If the applicant lives with the housemate, the housemate is entitled, the applicant and the applicant's partner jointly claim any of the benefits, and the applicant is entitled, the applicant is paid into the bank account the applicant's benefits are usually paid into.",
               Implies(And(source_condition(LIVES_WITH_ELIGIBLE), U("jointly_claims_benefits", a), U("entitled", a)),
                       U("paid_into_usual_account", a))),
        "G3": ("If HMRC changes the applicant's tax code to pay back the applicant's winter fuel payment, the tax deducted from the applicant's wages, salary or pension increases.",
               Implies(U("tax_code_changed", a), U("tax_deducted_increases", a))),
        "G4": ("If HMRC changes the applicant's tax code to pay back the applicant's winter fuel payment and needs to collect 2 payments from the applicant, HMRC collects 2 payments through the applicant's tax code at the same time.",
               Implies(And(U("tax_code_changed", a), U("two_payments_to_collect", a)), U("two_payments_through_tax_code", a))),
        "G5": ("If HMRC changes the applicant's tax code to pay back the applicant's winter fuel payment, needs to collect 2 payments from the applicant, and collects 2 payments through the applicant's tax code at the same time, the applicant pays more tax each month.",
               Implies(And(U("tax_code_changed", a), U("two_payments_to_collect", a), U("two_payments_through_tax_code", a)),
                       U("more_tax_each_month", a))),
        "G6": ("If the applicant completes a Self Assessment tax return, files tax returns online, and HMRC includes the amount of the applicant's winter fuel payment in the applicant's tax return automatically, the amount shows as the Winter Fuel Payment charge and is included in the applicant's tax calculation.",
               Implies(And(U("completes_self_assessment", a), U("files_online", a), U("included_automatically", a)),
                       And(U("shown_as_wfp_charge", a), U("in_tax_calculation", a)))),
        "G7": ("If the applicant is entitled, has not opted out, and the applicant's total income is more than GBP 35000.00, the amount is more than GBP 0.00 and HMRC takes the payment back.",
               Implies(And(U("entitled", a), Not(U("opted_out", a)), over),
                       And(["lt", gbp("0.00"), money_const("amount")], U("recovered", a)))),
    }
    return [rule(rid, f"S2:{GUIDE_SENTENCES[rid][1]}, srccov-rl-eligibility-1121", f"{gloss} {GUIDE_SENTENCES[rid][2]}",
                 formula, defines=[])
            for rid, (gloss, formula) in lines.items()]


B1 = rule("B1", "S1 reg. 1(3), bridge B1", f"{QW1} is 6 days after {QW0}. {DEFINITIONS['qualifying week']}", ["shift_days", day(QW1), day(QW0), "6"])


def rules(mutant=None):
    """The rule premises in dependency order: each role's rules, the amounts, then the guide rules."""
    return [*role_rules("applicant", mutant), *role_rules("housemate", mutant), *amount_rules(mutant),
            *guide_rules(), B1]


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
    facts += age_facts(r, p["birth"])
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
