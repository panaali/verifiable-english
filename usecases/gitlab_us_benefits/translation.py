"""GitLab handbook 'GitLab Inc (US) Benefits' (statute corpus batch 5, NON-STATUTE (f) benefit plan summary): the VE
translation, one pass with today's language. CROSS-FAMILY questions (Codex writer), Opus translator.

Row statute-corpus-gitlab-us-benefits-1125 (dri-statute-corpus-gitlab-us-benefits-tr-1125, Opus 5.5). Written from the
pinned source (manage-agents reviews/spare/statute-corpus/batch5/gitlab-us-benefits/source.txt, sha256
6e6e97e9fb04d1e5bdb448e730cd6fab0295a5a45ea1effb859cf74931c95050, CC BY-SA 4.0, page commit 747fa3f6) and its 104 units
(units.jsonl, sha256 a734ad0ab10c8b50809af8e16bc1ec0cf1f0db941e9ade87172ee25b53135282) plus the in-scope lines 105-109 that
are no unit (ISOLATION.md D3). FROZEN BEFORE THE CODEX QUESTIONS EXIST (orchestrator order 2026-11-25T10:25Z): no question,
key or answer of this text was written or read when this file was written; the readings below come from the source, the
units, ISOLATION.md D1-D16 and WRITER-BRIEF.md's fixed facts and answer forms only. Evidence branch: nothing here is a Lean
kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each unit n of units.jsonl (and the D3 lines 105-109) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one sub-case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
A builder returns (formula, target) pairs: target is the atom key or constant the formula defines (None = a check).

ONE SUB-CASE = the items one question needs: the team member p, and per question the family member (dep), the life event
(ev), the enrolment or addition (enr), the FSA account (fsa), the FSA election change (chg), the expense or claim (x), the
HSA change (hc), the return-to-work note (rtw), the disability (dsb), the Travel HRA trip (trip) or the asked day (day).
Items are linked to their parent in ctx.parent (a change to its event, an expense to its change). Every value a rule needs
is a stated fact of the case, a value computed in Lean from them, or (dates the language has no step for: a first day of a
month, a calendar date of a stated year, business days) one value of the ONE tested bridge script bridge.py, entered by the
encoder through encode.Sub.bridge and marked bridge (the unit is ledgered "bridged"). AMOUNTS ARE NEVER BRIDGED.

READINGS (fixed here; refuse when in doubt; D-numbers are ISOLATION.md's):
R1  Eligibility (unit 4, D5): eligible when the stated weekly hours are at least 30, not eligible under 30. Benefits start
    on the start date. A rule that grants something to "you" (a dependant's cover, basic life on a day, the 401(k)) does
    not itself test the hours; where the case's hours are under 30, the not-eligible rule denies it too and the two
    outcomes refuse the answer (never a yes for a person under 30 hours).
R2  Sign-up (units 1, 2; D7): the last day = the start date + 30 days (day 0 = the start date). A plan is chosen within 30
    days when the case states a choice dated on or before that day; no choice, or a later one, is not within 30 days.
R3  Waiver allowance (units 2, 15, 17; D4): $150 a month when the person actively waived medical coverage in PlanSource
    AND (already has group medical coverage OR chose no plan within 30 days); $0 when the person chose a GitLab medical
    plan within 30 days and did not actively waive. No plan within 30 days and NO active waiver: two outcomes (unit 2 /
    unit 17's last sentence vs "You must actively waive"): DERIVE NONE. Active waiver, no group coverage and a plan chosen
    in time: not decided (unit 15/17 grant the opt-out to a person who already has coverage): DERIVE NONE.
    "won't have other optional coverage" (unit 2): no plan within 30 days -> no other optional coverage from the new-hire
    enrolment. Unit 17: with group coverage and an active waiver, dental, vision and other benefits stay open.
R4  Family members (units 5-9; D6): a spouse or domestic partner can be covered; a child (own, adopted or step-child)
    aged under 26 can; aged 27 or more cannot, unless the stated fact is that the child has a disability and cannot
    support themselves (unit 8: then can); aged exactly 26: two outcomes ("up to age 26"), DERIVE NONE. Anyone else (a
    parent, a sibling) cannot: the list is the grant. Unit 9: a family member who works at GitLab and is covered under
    the plans as a team member is not covered again (covered only once).
R5  Domestic Partner Affidavit (unit 10): needed when a domestic partner is added outside new-hire and open enrolment; not
    needed when added during either. "may be taxable" / "may not be pre-tax eligible" decide nothing (D12).
R6  Qualifying life events (units 11-14, line 105; D7, D10): marriage, divorce, birth or adoption of a child, a spouse's
    employment change are qualifying events; an unlisted event is not decided (never "no"). The last day to submit the
    change = the event date + 30 days. A change submitted on or before it for a listed event can be made; after it (and
    not during open enrolment) cannot. A change during open enrolment can be made.
R7  Medical plans by state (units 15, 18, 24; D11): Cigna medical: every US state except Hawaii; Kaiser: residents of
    California and Hawaii only. Utah (unit 22): the extended network PPO includes Intermountain Healthcare. California,
    Alabama, New Jersey (unit 23): HSA contributions are taxable at state level (other states: not decided).
R8  HSA (units 19-21, 64; D8): GitLab's monthly contribution is $100 for team-member-only cover and $125 for team member +
    spouse/child/family cover when the person is enrolled in the HDHP; $0 and not eligible for HSA contributions when not.
R9  Voluntary plans (units 27, 28): enrolment is optional, the premium after tax; enrolment during new-hire enrolment, open
    enrolment or a qualifying life event whose change is in time (R6); none of the three -> no.
R10 Basic life (units 36-39; D8): min(2 x annual base salary, $500,000), AD&D equal; no cost; covered from the first day
    (a day on or after the start date: yes; before it: no). Supplemental life (unit 41): not in COBRA; ends on the last
    day (a day after the last day: not covered unless continued directly with Cigna; a day before it: covered); can be
    continued directly with Cigna. On the last day itself: not decided.
R11 Disability (units 42, 45, 46, lines 108, 109): the most replaced is 66.7% of base salary, 1000 x max = 667 x salary in
    cents (inexact -> no answer); no cost; for a qualifying disability (stated judgment). Return to work: the last day to
    send = planned return - 5 days; sent on or before it with a physician's authorisation -> in time; after it, or
    without the authorisation -> not. A disability of more than 26 weeks (182 days; weeks x 7 + days in Lean) -> unpaid
    leave, COBRA option, may apply for long-term disability; under 26 weeks -> not; exactly 26 weeks: not decided. The
    maximum benefit period is 26 weeks. NYLife contacts within 3 business days of the stated anchor when it needs more
    information (bridged business days; only a Monday-Friday calendar the case states).
R12 401(k) (units 48, 50, 59; D8): immediate eligibility and vesting. Match: rate of at least 6% -> 3 % of earnings
    (100 x m3 = 3 x earnings in cents), capped at $1,500; rate 0 -> $0; a rate between 0 and 6 % -> the match is rate/2
    x earnings, a product of two stated quantities the language cannot write: REFUSED (ledger). Loan: vested balance at
    most $100,000 -> half of it (2 x loan = balance in cents); over $100,000 -> $50,000.
R13 HSA rules (units 67-80, 74, 75): stated outcomes as yes/no (tax advantages, rollover, keep on leaving, the fee after
    leaving: a day after the last day -> responsible; on or before -> not). Age 65 (unit 70): age 65 or more -> any
    purpose without penalty; under 65 and not for medical expenses -> not. Domestic partner (unit 74): not legally married
    -> the partner's expenses are not HSA-eligible; covered under the family HDHP -> may open their own HSA and both may
    contribute up to the family maximum. A change (unit 75) takes effect on the first day of the month after the change
    date (bridged).
R14 FSA (units 82-100; D9, D13): Medical FSA: not with an HSA; Limited Purpose FSA: only with an HSA. Dependent Care FSA
    dependants: a child under 13 (13 or more: no), a disabled spouse (not disabled: no), a parent needing care (not: no),
    anyone else no. 2026 (stated plan year), a Medical or Limited Purpose FSA account (stated): election at most $3,400
    -> yes, over -> no; a Dependent Care FSA, an account whose type is not stated, or another year: not decided (the
    limits line sits under "Rollover Details for Medical and Limited Purpose FSA"; latent fix U88, 2026-11-25: the frozen
    rule tested every FSA account, a Dependent Care one included). Rollover: left under $5 -> forfeited, $0 (any year:
    "Important Notes" states no year); exactly $5: two outcomes, DERIVE NONE; over $5 -> min(left, $680) for a 2026 plan
    year only (the $680 cap is stated for 2026; another year or a year not stated: not decided; latent fix U90,
    2026-11-25: the frozen "ro = left" rule had no 2026 condition). Rollover funds usable the following year when rolled.
    Availability (unit 86): before the 5th business day after March 31 -> not available; on or after April 22 of that
    year -> available (both bridged dates); between: not decided. Changes: an increase with a qualifying event whose
    change is in time (R6), or during open enrolment -> yes; an increase with neither -> no; a decrease outside open
    enrolment -> no ("reductions aren't allowed"), during open enrolment -> yes. Additional funds: for expenses on or after
    the event date; before it the original election only (unit 100 agrees; the rule governs, D13); additional = new -
    original. Claims: after termination, within 90 days of the termination date (units 95, 97); otherwise within 90 days
    after the plan year end (unit 98); Dependent Care FSA: incurred through the March 15 and submitted by the March 31
    after the plan year end (unit 83; bridged dates); where unit 83 and unit 98 give two outcomes (a leap year), both
    rules fire and the answer is refused. Medical FSA expenses: up to and including the last day (after it: not, unless
    COBRA); Dependent Care FSA: through the last day only, never COBRA. COBRA option: contributed more than spent ->
    yes, otherwise no; COBRA payments post-tax.
R15 Travel HRA (units 101-104; D8): reimbursable when the nearest place where the care is available is MORE than 100
    miles from home ("not available within 100 miles": 100 miles is within) and the person (and dependants) are enrolled
    in a Cigna medical plan; not otherwise. Pre-tax: min(expenses, $2,100); post-tax: the excess over $2,100, at most
    $900; $0 each when not reimbursable.
R16 EPO (line 106): out-of-network deductible $10,000 individual / $20,000 family, out-of-pocket max $20,000 / $40,000,
    coinsurance 50 % (the slash read as individual/family, the stated tier; a question on another reading is writer's).
R17 NY Life services and the 401(k) facts (units 30-33, 53-62): stated constants (3 sessions, 30 minutes, 25 %), the
    plain duties and facts as the yes/no predicate the question asks (call Fidelity for automatic conversions, after-tax
    deductions before ESPP, conversion taxable in the year of conversion, ACH from the personal account, after-tax
    repayment). Prime + 1 % is no number (probe).
R18 Norms: a plain duty or permission of the text is written as the yes/no predicate the question asks, nothing more; a
    conditional permission is the only grant (its condition failing -> no) where R-lines above say so; "may need", "may
    charge", "may be taxable" decide nothing (D12).
No number from a case's facts is ever a coefficient: every coefficient is a literal of the pinned text (30, 26, 13, 65, 5,
90 days, 30 hours, $150, $100, $125, 2 x, $500,000, 66.7 %, 3 % = half of 6 %, $1,500, 50 %, $50,000, $3,400, $680, $5,
$2,100, $900, 100 miles, 26 weeks) or a unit conversion (7 days a week).
"""
from __future__ import annotations

import hashlib
import json

USD, DAY, NDAYS, HRS, AGE, PCT, MILE, WEEK, CNT, MIN, YEAR = (
    "usd_cent", "day", "elapsed_day", "hour_week", "age_year", "percent", "mile", "week", "count", "minute", "cal_year")

# base -> (unit, wording); a constant is f"{base}_{item}"; bases carry no "_"
BASES = {
    # person (stated)
    "sd": (DAY, "the start date (first day of work) (stated)"),
    "hrs": (HRS, "the hours per week the team member works (stated)"),
    "pcd": (DAY, "the date the team member chose a plan in PlanSource (stated)"),
    "sal": (USD, "the annual base salary (stated)"),
    "earn": (USD, "the earnings for the year (stated)"),
    "rate": (PCT, "the team member's own 401(k) contribution rate (stated)"),
    "vb": (USD, "the vested 401(k) balance (stated)"),
    "ld": (DAY, "the team member's last day (stated)"),
    "trd": (DAY, "the termination date (stated)"),
    "pye": (DAY, "the last day of the plan year (stated)"),
    "age": (AGE, "the age in whole years on the asked date (stated)"),
    "contr": (USD, "the amount contributed to the Medical FSA (stated)"),
    "spent": (USD, "the amount spent from the Medical FSA (stated)"),
    "cyr": (YEAR, "the year of the Roth conversion (stated)"),
    # person (computed)
    "bst": (DAY, "the date the benefits start"),
    "sul": (DAY, "the last day to sign up for benefits (start date + 30 days)"),
    "wamt": (USD, "the monthly Medical Waiver Allowance"),
    "hsac": (USD, "GitLab's monthly HSA contribution"),
    "bl": (USD, "the basic life insurance benefit"),
    "adnd": (USD, "the AD&D benefit"),
    "blcost": (USD, "the team member's cost of basic life insurance"),
    "dmax": (USD, "the most of the base salary the disability insurance replaces"),
    "discost": (USD, "the team member's cost of disability insurance"),
    "stdw": (WEEK, "the maximum disability benefit period in weeks"),
    "m3": (USD, "3% of the earnings (half of the first 6%)"),
    "match": (USD, "the company 401(k) match for the year"),
    "loan": (USD, "the most the team member can borrow from the 401(k)"),
    "bhs": (CNT, "the face-to-face Behavioral Health sessions with counselors"),
    "lcm": (MIN, "the length of the free legal or financial consultation in minutes"),
    "ldisc": (PCT, "the legal services fee discount"),
    "tdisc": (PCT, "the tax services discount"),
    "tyr": (YEAR, "the year in which the converted amount is taxable"),
    "epod": (USD, "the EPO plan's out-of-network deductible for the tier"),
    "epoo": (USD, "the EPO plan's out-of-network out-of-pocket maximum for the tier"),
    "epoc": (PCT, "the EPO plan's out-of-network coinsurance"),
    # dependant
    "dage": (AGE, "the family member's age in whole years on the asked date (stated)"),
    # life event
    "evd": (DAY, "the date of the event (stated)"),
    "sbd": (DAY, "the date the change or claim is submitted (stated)"),
    "evl": (DAY, "the last day to submit the change (event date + 30 days)"),
    # enrolment / addition / asked day / expense
    "dt": (DAY, "the date of the action (stated)"),
    "qd": (DAY, "the asked date (stated)"),
    "xd": (DAY, "the date the expense is incurred (stated)"),
    # FSA
    "el": (USD, "the FSA election for the year (stated)"),
    "left": (USD, "the amount left in the FSA at the end of the plan year (stated)"),
    "ro": (USD, "the amount rolled over"),
    "orig": (USD, "the original FSA election (stated)"),
    "nw": (USD, "the increased FSA election (stated)"),
    "pre": (USD, "the most reimbursable for expenses before the event date"),
    "addl": (USD, "the additional funds"),
    "ctl": (DAY, "the last day to submit claims after termination (termination date + 90 days)"),
    "rol": (DAY, "the last day of the runout period (plan year end + 90 days)"),
    # HSA change, rollover availability, NYLife (bridged)
    "nm1": (DAY, "the first day of the month after the change date (bridge)"),
    "eff": (DAY, "the date the HSA change takes effect"),
    "m15": (DAY, "the March 15 after the plan year end (bridge)"),
    "m31": (DAY, "the March 31 after the plan year end (bridge)"),
    "rb5": (DAY, "the 5th business day after March 31 of the current tax year (bridge)"),
    "a22": (DAY, "April 22 of the current tax year (bridge)"),
    "anc": (DAY, "the date the claim reaches NYLife (stated)"),
    "b3": (DAY, "the 3rd business day after the date the claim reaches NYLife (bridge)"),
    "nyl": (DAY, "the last day by which NYLife contacts the team member"),
    # return to work
    "ret": (DAY, "the planned return date (stated)"),
    "snt": (DAY, "the date the authorization is e-mailed (stated)"),
    "rtl": (DAY, "the last day to e-mail the authorization (planned return - 5 days)"),
    # disability
    "dwk": (NDAYS, "the whole weeks of the disability (stated)"),
    "dxd": (NDAYS, "the days of the disability beyond the whole weeks (stated)"),
    "dur": (NDAYS, "the length of the disability in days"),
    # Travel HRA
    "mi": (MILE, "the distance from home to the nearest place where the care is available (stated)"),
    "amt": (USD, "the travel expenses (stated)"),
    "hpre": (USD, "the amount reimbursable from the pre-tax account"),
    "hpost": (USD, "the amount reimbursable from the post-tax account"),
}
STATED_BASES = ("sd", "hrs", "pcd", "sal", "earn", "rate", "vb", "ld", "trd", "pye", "age", "contr", "spent", "cyr",
                "dage", "evd", "sbd", "dt", "qd", "xd", "el", "left", "orig", "nw", "ret", "snt", "dwk", "dxd", "mi",
                "amt", "anc", "nm1", "m15", "m31", "rb5", "a22", "b3")
BRIDGED_BASES = ("nm1", "m15", "m31", "rb5", "a22", "b3")
STEP_BASES = tuple(b for b in BASES if b not in STATED_BASES)

FACTS = {
    # person
    "plan": "the team member chose a plan in PlanSource",
    "med": "the plan the team member chose is a GitLab medical plan",
    "aw": "the team member actively waived medical coverage in PlanSource",
    "grp": "the team member already has group medical coverage elsewhere",
    "hi": "the team member lives in Hawaii",
    "ca": "the team member lives in California",
    "ut": "the team member lives in Utah",
    "al": "the team member lives in Alabama",
    "nj": "the team member lives in New Jersey",
    "hdhp": "the team member is enrolled in the High Deductible Health Plan",
    "tmo": "the team member's coverage is team member only",
    "hsa": "the team member has an HSA",
    "sl": "the team member has supplemental life insurance",
    "cont": "the team member continued the supplemental life coverage directly with Cigna",
    "qdis": "the stated judgment: the team member's disability is a qualifying disability",
    "cobra": "the team member continues the Medical FSA through COBRA",
    "medx": "the withdrawal is for medical expenses",
    "cig": "the team member and the dependants are enrolled in a Cigna Medical Plan",
    "fam": "the coverage tier is family (not individual)",
    "y26": "the plan year is 2026",
    "need": "NYLife needs additional information",
    "conv": "the team member wants automatic Roth in-plan conversions",
    # dependant
    "sp": "the family member is the team member's spouse",
    "dpn": "the family member is the team member's domestic partner",
    "ch": "the family member is the team member's child (own, adopted or step-child)",
    "dis": "the family member has a disability and cannot support themselves",
    "par": "the family member is the team member's parent",
    "oth": "the family member is neither spouse, domestic partner nor child",
    "gl": "the family member works at GitLab",
    "ownc": "the family member is covered under GitLab's plans as a team member",
    "nh": "the action is taken during new hire enrollment",
    "oe": "the action is taken during open enrollment",
    "disd": "the family member is disabled",
    "care": "the family member is a parent needing care",
    "married": "the team member is legally married to the family member",
    "inh": "the family member is covered under the team member's family HDHP",
    # life event
    "mar": "the event is a marriage",
    "div": "the event is a divorce",
    "birth": "the event is the birth of a child",
    "adopt": "the event is the adoption of a child",
    "spemp": "the event is a change in the spouse's employment",
    # enrolment item
    "noev": "no life event is linked to the enrolment",
    # FSA change
    "inc": "the change increases the FSA contribution",
    "dec": "the change reduces the FSA contribution",
    # expense / claim
    "trm": "the claim is submitted after the team member's termination",
    "dc": "the account is a Dependent Care FSA",
    "mf": "the account is a Medical FSA",
    "lpf": "the account is a Limited Purpose FSA",
    # return to work
    "phys": "the stated judgment: the note is a physician's Return to Work authorization",
}
STATED_JUDGMENT = ("qdis", "phys")
DERIVED = {
    "elig": "the team member is eligible for GitLab's benefits",
    "p30": "the team member chose a plan within 30 days of the start date",
    "suok": "the sign-up on the action's date is within the 30 days",
    "wal": "the team member receives the Medical Waiver Allowance",
    "optc": "the team member has other optional coverage from the new-hire enrollment",
    "dvok": "the team member can still enroll in dental, vision and other benefits",
    "covd": "the family member can be covered under the plans",
    "twice": "the family member can be covered twice under GitLab's plans",
    "aff": "the team member must complete a Domestic Partner Affidavit",
    "qle": "the event is a qualifying life event",
    "chgok": "the change can be made on the submission date",
    "cigok": "the team member can enroll in a Cigna medical plan",
    "kaiok": "the team member can enroll in a Kaiser plan",
    "imh": "the team member's extended network PPO includes Intermountain Healthcare System",
    "hstax": "HSA contributions are taxable at state level for the team member",
    "hsael": "the team member is eligible for HSA contributions and enrollment",
    "volopt": "enrollment in the voluntary plans is optional",
    "volat": "the voluntary plans' premium is after tax",
    "volok": "the team member can enroll in the voluntary plans by this enrollment",
    "nyfree": "the New York Life support services are at no cost",
    "blcov": "the team member is covered by basic life insurance on the asked date",
    "surv": "survivor assurance and support services are included",
    "vlife": "additional voluntary life insurance is available through Cigna",
    "slcobra": "supplemental life insurance is included in COBRA",
    "slcont": "the team member can continue supplemental life coverage directly with Cigna",
    "slcov": "the team member is covered by GitLab's supplemental life insurance on the asked date",
    "disben": "the disability insurance replaces salary for the team member's disability",
    "contam": "the team member should contact the Absence Management team",
    "rtok": "the return-to-work authorization is sent in time",
    "unpaid": "the team member moves to unpaid leave",
    "cobop": "the team member has the option to continue benefits through COBRA",
    "ltdap": "the team member can apply for long-term disability at this time",
    "k401el": "the team member is eligible for the 401(k) on the asked date",
    "vest": "the team member's 401(k) company match is vested",
    "callfid": "the team member needs to call Fidelity",
    "prio": "after-tax deductions take priority over ESPP contributions",
    "convtax": "converted amounts are taxable",
    "ach": "the 401(k) loan is repaid via ACH from the personal bank account",
    "loanat": "the 401(k) loan is repaid with after-tax dollars",
    "taxadv": "HSA contributions reduce taxable income, earnings grow tax-free and medical withdrawals are tax-free",
    "hroll": "HSA money rolls over annually and never expires",
    "wnp": "the team member can withdraw from the HSA for this purpose without penalty",
    "wtf": "the HSA withdrawal is tax-free",
    "hkeep": "the HSA and its funds stay with the team member after leaving GitLab",
    "fee": "the team member is responsible for the HSA monthly administration fee on the asked date",
    "dpexp": "the domestic partner's expenses are HSA-eligible",
    "dphsa": "the domestic partner can open their own HSA",
    "dpfull": "both can contribute up to the full family maximum to their HSAs",
    "hchg": "the team member can adjust HSA contributions at this time",
    "glmon": "GitLab can monitor HSA contributions made outside payroll",
    "mfsaok": "the team member can participate in a Medical FSA",
    "lpfok": "the team member can participate in a Limited Purpose FSA",
    "dcq": "the family member is a qualifying dependant for the Dependent Care FSA",
    "elok": "the FSA election is within the year's maximum contribution",
    "forf": "the amount left in the FSA is forfeited",
    "rouse": "the team member can use rollover funds the following year",
    "roav": "the rollover funds are available on the asked date",
    "fok": "the FSA contribution change is allowed",
    "addok": "the additional FSA funds can be used for the expense",
    "clmok": "the claim can be submitted on the submission date",
    "xok": "the FSA can be used for the expense",
    "cobraok": "the Medical FSA COBRA option is available",
    "cobpost": "Medical FSA COBRA payments are on a post-tax basis",
    "dccob": "the Dependent Care FSA can be continued through COBRA",
    "hraok": "the travel is reimbursable under the Travel HRA",
}


# --- formula helpers (ve-quantity@1 wire shapes) --------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def usd(v): return ["decimal", USD, v]
def nd(v): return ["decimal", NDAYS, str(v)]
def hrs(v): return ["decimal", HRS, str(v)]
def yrs(v): return ["decimal", AGE, str(v)]
def pct(v): return ["decimal", PCT, str(v)]
def mil(v): return ["decimal", MILE, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
def add(tag, a, b): return ["add", tag, a, b]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]       # a is n days after b
TRUE, FALSE = ["top"], ["bottom"]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return TRUE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return FALSE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


UNIT_OF = {b: u for b, (u, _) in BASES.items()}


def k(base, x):
    return ["const", UNIT_OF[base], f"{base}_{x}"]


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def A(p, x):
    return key(U(p, x))


# --- the case context -------------------------------------------------------------------------------------------------

class Ctx:
    """items: [(id, kind)]; parent: {child id: parent id}. Kinds: person, dep, ev, enr, fsa, chg, x, hc, rtw, dsb, trip,
    day."""

    def __init__(self, items, parent=None):
        self.items = list(items)
        self.parent = dict(parent or {})
        self.person = "p"

    def of(self, kind):
        return [x for x, kd in self.items if kd == kind]

    def children(self, x, kind=None):
        kinds = dict(self.items)
        return [y for y, p in self.parent.items() if p == x and (kind is None or kinds[y] == kind)]


P = "p"


def pk(base):
    return k(base, P)


def pf(name):
    return U(name, P)


def both(pos, neg, atom, x):
    """atom(x) <- pos; not atom(x) <- neg (either may be None)."""
    out = []
    if pos is not None:
        out.append((Implies(pos, U(atom, x)), A(atom, x)))
    if neg is not None:
        out.append((Implies(neg, Not(U(atom, x))), A(atom, x)))
    return out


def fact_true(atom, x):
    """A plain outcome the text states for everyone (R17/R18)."""
    return [(U(atom, x), A(atom, x))]


def fact_false(atom, x):
    return [(Not(U(atom, x)), A(atom, x))]


def setv(base, x, term):
    return (Eq(k(base, x), term), f"{base}_{x}")


def cond_val(cond, base, x, term):
    return (Implies(cond, Eq(k(base, x), term)), f"{base}_{x}")


NOT_ELIG = Lt(pk("hrs"), hrs(30))


# --- the rules, unit by unit ------------------------------------------------------------------------------------------

def _u1(ctx):
    """Unit 1 (R2): 30 days from the start date; a sign-up on the action's date is in time when on or before it."""
    out = [(shift(pk("sul"), pk("sd"), 30), "sul_p")]
    for e in ctx.of("enr"):
        out += both(no_later(k("dt", e), pk("sul")), before(pk("sul"), k("dt", e)), "suok", e)
    return out


def _p30():
    return both(And(pf("plan"), no_later(pk("pcd"), pk("sul"))), Or(Not(pf("plan")), before(pk("sul"), pk("pcd"))),
                "p30", P)


def _u2(ctx):
    """Unit 2 (R3): no plan within 30 days -> the allowance (with an active waiver, D4) and no other optional coverage."""
    out = [(shift(pk("sul"), pk("sd"), 30), "sul_p")] + _p30()
    out += both(And(pf("aw"), Not(pf("p30"))), None, "wal", P)
    out += both(None, Not(pf("p30")), "optc", P)
    return out + _wamt()


def _wamt():
    return [cond_val(pf("wal"), "wamt", P, usd("150.00")), cond_val(Not(pf("wal")), "wamt", P, usd("0.00"))]


def _u4(ctx):
    """Unit 4 (R1): at least 30 hours a week; benefits start on the first day."""
    out = both(Le(hrs(30), pk("hrs")), NOT_ELIG, "elig", P)
    out.append(setv("bst", P, pk("sd")))
    return out


def _notdup(d):
    return Or(Not(U("gl", d)), Not(U("ownc", d)))


def _u6(ctx):
    """Unit 6 (R4): a spouse or domestic partner."""
    out = []
    for d in ctx.of("dep"):
        out += both(And(Or(U("sp", d), U("dpn", d)), _notdup(d)), None, "covd", d)
        out += both(None, NOT_ELIG, "covd", d)
    return out


def _u7(ctx):
    """Unit 7 (R4, D6): children under 26 (27 or more: not, unless unit 8)."""
    out = []
    for d in ctx.of("dep"):
        out += both(And(U("ch", d), Lt(k("dage", d), yrs(26)), _notdup(d)),
                    And(U("ch", d), Lt(yrs(26), k("dage", d)), Not(U("dis", d))), "covd", d)
        out += both(None, U("oth", d), "covd", d)
    return out


def _u8(ctx):
    """Unit 8 (R4): adult children with disabilities who cannot support themselves."""
    out = []
    for d in ctx.of("dep"):
        out += both(And(U("ch", d), U("dis", d), _notdup(d)), None, "covd", d)
    return out


def _u9(ctx):
    """Unit 9 (R4): covered only once."""
    out = []
    for d in ctx.of("dep"):
        out += both(None, U("gl", d), "twice", d)
        out += both(None, And(U("gl", d), U("ownc", d)), "covd", d)
    return out


def _u10(ctx):
    """Unit 10 (R5): the Domestic Partner Affidavit outside new hire and open enrollment."""
    out = []
    for d in ctx.of("dep"):
        out += both(And(U("dpn", d), Not(U("nh", d)), Not(U("oe", d))), And(U("dpn", d), Or(U("nh", d), U("oe", d))),
                    "aff", d)
    return out


def _qle(ctx):
    """Units 11-14 (R6, D10): the listed qualifying life events (no negative: the list is 'such as')."""
    out = []
    for e in ctx.of("ev"):
        out += both(Or(U("mar", e), U("div", e), U("birth", e), U("adopt", e), U("spemp", e)), None, "qle", e)
    return out


def _u105(ctx):
    """Line 105 (R6): within 30 days of the qualifying event; open enrollment changes."""
    out = []
    for e in ctx.of("ev"):
        out.append((Implies(U("qle", e), shift(k("evl", e), k("evd", e), 30)), f"evl_{e}"))
        out += both(Or(And(U("qle", e), no_later(k("sbd", e), k("evl", e))), U("oe", e)),
                    And(U("qle", e), before(k("evl", e), k("sbd", e)), Not(U("oe", e))), "chgok", e)
    return out


def _u15(ctx):
    """Units 15, 18, 24 (R7, D11): Cigna except Hawaii; Kaiser for California and Hawaii residents."""
    out = both(Not(pf("hi")), pf("hi"), "cigok", P)
    out += both(Or(pf("hi"), pf("ca")), And(Not(pf("hi")), Not(pf("ca"))), "kaiok", P)
    return out


def _u17(ctx):
    """Unit 17 (R3, D4): $150 with group coverage and an active waiver; dental, vision, other benefits stay open."""
    out = [(shift(pk("sul"), pk("sd"), 30), "sul_p")] + _p30()
    out += both(And(pf("aw"), pf("grp")), And(pf("med"), pf("p30"), Not(pf("aw"))), "wal", P)
    out += both(And(pf("aw"), pf("grp")), None, "dvok", P)
    return out + _wamt()


def _u20(ctx):
    """Units 20, 21, 64 (R8): $100 / $125 a month with the HDHP; not eligible without it."""
    out = both(pf("hdhp"), Not(pf("hdhp")), "hsael", P)
    out.append(cond_val(And(pf("hdhp"), pf("tmo")), "hsac", P, usd("100.00")))
    out.append(cond_val(And(pf("hdhp"), Not(pf("tmo"))), "hsac", P, usd("125.00")))
    out.append(cond_val(Not(pf("hdhp")), "hsac", P, usd("0.00")))
    return out


def _u22(ctx):
    return both(pf("ut"), None, "imh", P)


def _u23(ctx):
    return both(Or(pf("ca"), pf("al"), pf("nj")), None, "hstax", P)


def _u27(ctx):
    return fact_true("volopt", P) + fact_true("volat", P)


def _u28(ctx):
    """Unit 28 (R9): new hire, open enrollment or a qualifying life event in time."""
    out = []
    for e in ctx.of("enr"):
        evs = ctx.children(e, "ev")
        ok_ev = [U("chgok", v) for v in evs]
        bad_ev = And(*[Not(U("chgok", v)) for v in evs]) if evs else U("noev", e)
        out += both(Or(U("nh", e), U("oe", e), *ok_ev), And(Not(U("nh", e)), Not(U("oe", e)), bad_ev), "volok", e)
    return out


def _u30(ctx):
    return fact_true("nyfree", P)


def _u31(ctx):
    return [setv("bhs", P, ["decimal", CNT, "3"])]


def _u32(ctx):
    return [setv("lcm", P, ["decimal", MIN, "30"]), setv("ldisc", P, pct(25))]


def _u33(ctx):
    return [setv("lcm", P, ["decimal", MIN, "30"]), setv("tdisc", P, pct(25))]


def _u36(ctx):
    """Unit 36 (R10): min(2 x salary, $500,000); AD&D equal."""
    two = scale(USD, 2, pk("sal"))
    return [cond_val(Le(two, usd("500000.00")), "bl", P, two),
            cond_val(Lt(usd("500000.00"), two), "bl", P, usd("500000.00")),
            setv("adnd", P, pk("bl"))]


def _u37(ctx):
    """Unit 37 (R10): from day one."""
    out = []
    for y in ctx.of("day"):
        out += both(no_later(pk("sd"), k("qd", y)), Or(before(k("qd", y), pk("sd")), NOT_ELIG), "blcov", y)
    return out


def _u38(ctx):
    return fact_true("surv", P)


def _u39(ctx):
    return [setv("blcost", P, usd("0.00"))]


def _u40(ctx):
    return fact_true("vlife", P)


def _u41(ctx):
    """Unit 41 (R10): not in COBRA, ends on the last day, can continue with Cigna."""
    out = fact_false("slcobra", P) + both(pf("sl"), None, "slcont", P)
    for y in ctx.of("day"):
        out += both(And(pf("sl"), before(k("qd", y), pk("ld"))), And(before(pk("ld"), k("qd", y)), Not(pf("cont"))),
                    "slcov", y)
    return out


def _u42(ctx):
    """Unit 42 (R11): up to 66.7% of base salary, no cost, qualifying disabilities."""
    return [(Eq(scale(USD, 1000, pk("dmax")), scale(USD, 667, pk("sal"))), "dmax_p"), setv("discost", P, usd("0.00"))] \
        + both(pf("qdis"), Not(pf("qdis")), "disben", P)


def _u45(ctx):
    """Unit 45 (R11): at least 5 calendar days before the planned return, a physician's authorization."""
    out = []
    for r in ctx.of("rtw"):
        out.append((shift(k("ret", r), k("rtl", r), 5), f"rtl_{r}"))
        out += both(And(U("phys", r), no_later(k("snt", r), k("rtl", r))),
                    Or(before(k("rtl", r), k("snt", r)), Not(U("phys", r))), "rtok", r)
    return out


def _u46(ctx):
    """Unit 46 (R11): more than 26 weeks -> unpaid leave, COBRA option, long-term disability."""
    out = []
    for s in ctx.of("dsb"):
        out.append((Eq(k("dur", s), add(NDAYS, scale(NDAYS, 7, k("dwk", s)), k("dxd", s))), f"dur_{s}"))
        for atom in ("unpaid", "cobop", "ltdap"):
            out += both(Lt(nd(182), k("dur", s)), Lt(k("dur", s), nd(182)), atom, s)
    return out


def _u47(ctx):
    """Unit 47 (R11): within 3 business days (bridged), when NYLife needs more information."""
    out = []
    for x in ctx.of("x"):
        out.append((Implies(U("need", x), Eq(k("nyl", x), k("b3", x))), f"nyl_{x}"))
    return out


def _u48(ctx):
    """Unit 48 (R12): immediate eligibility and vesting."""
    out = fact_true("vest", P)
    for y in ctx.of("day"):
        out += both(no_later(pk("sd"), k("qd", y)), NOT_ELIG, "k401el", y)
    return out


def _u50(ctx):
    """Unit 50 (R12): 50% of contributions on the first 6% of earnings, up to $1,500."""
    r, m3 = pk("rate"), pk("m3")
    return [(Eq(scale(USD, 100, m3), scale(USD, 3, pk("earn"))), "m3_p"),
            cond_val(And(Le(pct(6), r), Le(m3, usd("1500.00"))), "match", P, m3),
            cond_val(And(Le(pct(6), r), Lt(usd("1500.00"), m3)), "match", P, usd("1500.00")),
            cond_val(Eq(r, pct(0)), "match", P, usd("0.00"))]


def _u53(ctx):
    return both(pf("conv"), None, "callfid", P)


def _u55(ctx):
    return fact_true("prio", P)


def _u56(ctx):
    return fact_true("convtax", P) + [setv("tyr", P, pk("cyr"))]


def _u59(ctx):
    """Unit 59 (R12): 50% of the vested balance or $50,000, whichever is less."""
    vb = pk("vb")
    return [(Implies(Le(vb, usd("100000.00")), Eq(scale(USD, 2, pk("loan")), vb)), "loan_p"),
            cond_val(Lt(usd("100000.00"), vb), "loan", P, usd("50000.00"))]


def _u61(ctx):
    return fact_true("ach", P)


def _u62(ctx):
    return fact_true("loanat", P)


def _u67(ctx):
    return fact_true("taxadv", P) + both(pf("medx"), None, "wtf", P)


def _u68(ctx):
    return fact_true("hroll", P)


def _u70(ctx):
    """Unit 70 (R13): at age 65, any purpose without penalty."""
    return both(Le(yrs(65), pk("age")), And(Lt(pk("age"), yrs(65)), Not(pf("medx"))), "wnp", P)


def _u73(ctx):
    """Unit 73 (R13): stays with you; the fee once GitLab is no longer the employer."""
    out = fact_true("hkeep", P)
    for y in ctx.of("day"):
        out += both(before(pk("ld"), k("qd", y)), no_later(k("qd", y), pk("ld")), "fee", y)
    return out


def _u74(ctx):
    """Unit 74 (R13): domestic partner HSA rules."""
    out = []
    for d in ctx.of("dep"):
        out += both(None, And(U("dpn", d), Not(U("married", d))), "dpexp", d)
        out += both(And(U("dpn", d), U("inh", d)), None, "dphsa", d)
        out += both(And(U("dpn", d), U("inh", d)), None, "dpfull", d)
    return out


def _u75(ctx):
    """Unit 75 (R13): anytime; effective on the 1st of the following month (bridged)."""
    out = fact_true("hchg", P)
    for h in ctx.of("hc"):
        out.append(setv("eff", h, k("nm1", h)))
    return out


def _u79(ctx):
    return fact_false("glmon", P)


def _u80(ctx):
    return fact_true("hkeep", P)


def _u82(ctx):
    """Units 82, 99 (R14): changes only in open enrollment or a qualifying life event; increases only; no reductions."""
    out = []
    for g in ctx.of("chg"):
        evs = ctx.children(g, "ev")
        ok_ev = [U("chgok", v) for v in evs]
        no_ev = And(*[Not(U("chgok", v)) for v in evs]) if evs else TRUE
        out += both(Or(U("oe", g), And(U("inc", g), Or(*ok_ev))) if ok_ev else U("oe", g),
                    Or(And(U("dec", g), Not(U("oe", g))), And(U("inc", g), Not(U("oe", g)), no_ev)), "fok", g)
    return out


def _u83(ctx):
    """Unit 83 (R14): qualifying dependants; incurred through March 15, submitted by March 31 (bridged dates)."""
    out = []
    for d in ctx.of("dep"):
        out += both(Or(And(U("ch", d), Lt(k("dage", d), yrs(13))), And(U("sp", d), U("disd", d)),
                       And(U("par", d), U("care", d))),
                    Or(And(U("ch", d), Le(yrs(13), k("dage", d))), And(U("sp", d), Not(U("disd", d))),
                       And(U("par", d), Not(U("care", d))), And(Not(U("ch", d)), Not(U("sp", d)), Not(U("par", d)))),
                    "dcq", d)
    for x in ctx.of("x"):
        out += both(And(U("dc", x), Not(U("trm", x)), no_later(k("xd", x), k("m15", x)), no_later(k("sbd", x), k("m31", x))),
                    And(U("dc", x), Not(U("trm", x)), Or(before(k("m15", x), k("xd", x)), before(k("m31", x), k("sbd", x)))),
                    "clmok", x)
    return out


def _u84(ctx):
    return both(Not(pf("hsa")), pf("hsa"), "mfsaok", P)


def _u85(ctx):
    return both(pf("hsa"), Not(pf("hsa")), "lpfok", P)


def _u86(ctx):
    """Unit 86 (R14): not before the 5th business day after March 31; no later than April 22 (bridged)."""
    out = []
    for y in ctx.of("day"):
        out += both(no_later(k("a22", y), k("qd", y)), before(k("qd", y), k("rb5", y)), "roav", y)
    return out


def _health_fsa(f):
    """A Medical or Limited Purpose FSA account (stated): the accounts the 'Rollover Details for Medical and Limited
    Purpose FSA' heading, and so unit 88's limits, are about (latent fix U88)."""
    return Or(U("mf", f), U("lpf", f))


def _u88(ctx):
    """Unit 88 (R14): 2026: $3,400 max contribution, $680 max rollover; the contribution test only for a stated Medical
    or Limited Purpose FSA (a Dependent Care FSA, or a type not stated: OPEN; latent fix U88)."""
    out = []
    for f in ctx.of("fsa"):
        hf = _health_fsa(f)
        out += both(And(U("y26", f), hf, Le(k("el", f), usd("3400.00"))),
                    And(U("y26", f), hf, Lt(usd("3400.00"), k("el", f))), "elok", f)
        out.append(cond_val(And(U("y26", f), Lt(usd("680.00"), k("left", f))), "ro", f, usd("680.00")))
    return out


def _u90(ctx):
    """Unit 90 (R14, D9): $5 minimum; $5 or less forfeited (exactly $5: two outcomes, derive none); the whole amount left
    over $5 (up to $680) rolls over only in a 2026 plan year, the one year the $680 cap is stated for (latent fix U90)."""
    out = []
    for f in ctx.of("fsa"):
        lf = k("left", f)
        out += both(Lt(lf, usd("5.00")), Lt(usd("5.00"), lf), "forf", f)
        out.append(cond_val(Lt(lf, usd("5.00")), "ro", f, usd("0.00")))
        out.append(cond_val(And(U("y26", f), Lt(usd("5.00"), lf), Le(lf, usd("680.00"))), "ro", f, lf))
    return out


def _u88_frozen(ctx):
    """The frozen _u88 (f8309cf469), kept only for the planted error M27: the $3,400 test on every FSA account."""
    out = []
    for f in ctx.of("fsa"):
        out += both(And(U("y26", f), Le(k("el", f), usd("3400.00"))), And(U("y26", f), Lt(usd("3400.00"), k("el", f))),
                    "elok", f)
        out.append(cond_val(And(U("y26", f), Lt(usd("680.00"), k("left", f))), "ro", f, usd("680.00")))
    return out


def _u90_frozen(ctx):
    """The frozen _u90 (f8309cf469), kept only for the planted error M28: 'ro = left' in any plan year."""
    out = []
    for f in ctx.of("fsa"):
        lf = k("left", f)
        out += both(Lt(lf, usd("5.00")), Lt(usd("5.00"), lf), "forf", f)
        out.append(cond_val(Lt(lf, usd("5.00")), "ro", f, usd("0.00")))
        out.append(cond_val(And(Lt(usd("5.00"), lf), Le(lf, usd("680.00"))), "ro", f, lf))
    return out


def _u91(ctx):
    out = []
    for f in ctx.of("fsa"):
        out += both(Lt(usd("5.00"), k("left", f)), Lt(k("left", f), usd("5.00")), "rouse", f)
    return out


def _u92(ctx):
    """Units 92, 96 (R14): expenses up to and including the last day; after it only through COBRA (Medical FSA)."""
    out = []
    for x in ctx.of("x"):
        out += both(And(Or(U("mf", x), U("dc", x)), no_later(k("xd", x), pk("ld"))),
                    Or(And(U("mf", x), before(pk("ld"), k("xd", x)), Not(pf("cobra"))),
                       And(U("dc", x), before(pk("ld"), k("xd", x)))), "xok", x)
    return out


def _u93(ctx):
    return both(Lt(pk("spent"), pk("contr")), Le(pk("contr"), pk("spent")), "cobraok", P)


def _u94(ctx):
    return fact_true("cobpost", P)


def _u95(ctx):
    """Units 95, 97 (R14): claims within 90 days of termination."""
    out = []
    for x in ctx.of("x"):
        out.append((Implies(U("trm", x), shift(k("ctl", x), pk("trd"), 90)), f"ctl_{x}"))
        out += both(And(U("trm", x), no_later(k("sbd", x), k("ctl", x))), And(U("trm", x), before(k("ctl", x), k("sbd", x))),
                    "clmok", x)
    return out


def _u96(ctx):
    return fact_false("dccob", P) + _u92(ctx)


def _u98(ctx):
    """Unit 98 (R14): 90 days after the plan year ends (the runout period)."""
    out = []
    for x in ctx.of("x"):
        out.append((Implies(Not(U("trm", x)), shift(k("rol", x), pk("pye"), 90)), f"rol_{x}"))
        out += both(And(Not(U("trm", x)), Not(U("dc", x)), no_later(k("sbd", x), k("rol", x))),
                    And(Not(U("trm", x)), before(k("rol", x), k("sbd", x))), "clmok", x)
    return out


def _u99(ctx):
    """Units 99, 100 (R14, D13): additional funds only for expenses on or after the event date."""
    out = _u82(ctx)
    for g in ctx.of("chg"):
        evs = ctx.children(g, "ev")
        out.append(setv("pre", g, k("orig", g)))
        out.append(setv("addl", g, add(USD, k("nw", g), scale(USD, -1, k("orig", g)))))
        for x in ctx.children(g, "x"):
            for e in evs:
                out += both(no_later(k("evd", e), k("xd", x)), before(k("xd", x), k("evd", e)), "addok", x)
    return out


def _u101(ctx):
    """Units 101, 102 (R15): care not available within 100 miles; enrolled in a Cigna Medical Plan."""
    out = []
    for t in ctx.of("trip"):
        out += both(And(Lt(mil(100), k("mi", t)), pf("cig")), Or(Le(k("mi", t), mil(100)), Not(pf("cig"))), "hraok", t)
    return out


def _u103(ctx):
    """Unit 103 (R15): pre-tax up to $2,100."""
    out = []
    for t in ctx.of("trip"):
        a, ok = k("amt", t), U("hraok", t)
        out.append(cond_val(And(ok, Le(a, usd("2100.00"))), "hpre", t, a))
        out.append(cond_val(And(ok, Lt(usd("2100.00"), a)), "hpre", t, usd("2100.00")))
        out.append(cond_val(Not(ok), "hpre", t, usd("0.00")))
    return out


def _u104(ctx):
    """Unit 104 (R15): post-tax $900 for expenses exceeding the pre-tax limit."""
    out = []
    for t in ctx.of("trip"):
        a, ok = k("amt", t), U("hraok", t)
        out.append(cond_val(And(ok, Le(a, usd("2100.00"))), "hpost", t, usd("0.00")))
        out.append(cond_val(And(ok, Lt(usd("2100.00"), a), Le(a, usd("3000.00"))), "hpost", t,
                            add(USD, a, usd("-2100.00"))))
        out.append(cond_val(And(ok, Lt(usd("3000.00"), a)), "hpost", t, usd("900.00")))
        out.append(cond_val(Not(ok), "hpost", t, usd("0.00")))
    return out


def _u106(ctx):
    """Line 106 (R16): EPO out-of-network figures by tier."""
    return [cond_val(Not(pf("fam")), "epod", P, usd("10000.00")), cond_val(pf("fam"), "epod", P, usd("20000.00")),
            cond_val(Not(pf("fam")), "epoo", P, usd("20000.00")), cond_val(pf("fam"), "epoo", P, usd("40000.00")),
            setv("epoc", P, pct(50))]


def _u108(ctx):
    return both(pf("qdis"), None, "contam", P)


def _u109(ctx):
    return [setv("stdw", P, ["decimal", WEEK, "26"])]


def _merge(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


def _nothing(ctx):
    return []


NO = "other:no outcome"
UNITS = {
    1: ("RULE", _u1, "unit 1: 30 days from the start date (R2; date steps in Lean)"),
    2: ("RULE", _u2, "unit 2: no plan in 30 days -> no other optional coverage, and the allowance with an active waiver "
        "(R3); with no active waiver unit 17 gives the opposite: the text's two outcomes, derive none (D4; not a cause)"),
    3: ("NOT", None, "cross-reference", "unit 3: points to the PlanSource Video Library and the Accounting and Reporting "
        "page (not pinned); no outcome"),
    4: ("RULE", _u4, "unit 4: at least 30 hours a week; benefits start on the first day (R1)"),
    5: ("RULE", _nothing, "unit 5: 'You can also cover:' (the ':' parent of units 6-8; their rules)"),
    6: ("RULE", _u6, "unit 6: spouse or domestic partner (R4)"),
    7: ("RULE", _u7, "unit 7: under 26 covered, 27+ not (R4); exactly 26: 'up to age 26' gives the text's two outcomes, "
        "derive none (D6; not a cause)"),
    8: ("RULE", _u8, "unit 8: adult children with disabilities who can't support themselves (R4)"),
    9: ("RULE", _u9, "unit 9: covered only once (R4)"),
    10: ("PART", _u10, "other:norm", "unit 10: the affidavit outside new hire / open enrollment (R5); 'may be taxable "
         "income' and 'may not be pre-tax eligible' decide nothing (D12)"),
    11: ("RULE", _qle, "unit 11: qualifying life events 'such as' (R6; an unlisted event is not decided, D10)"),
    12: ("RULE", _qle, "unit 12: marriage or divorce (R6)"),
    13: ("RULE", _qle, "unit 13: birth or adoption of a child (R6)"),
    14: ("RULE", _qle, "unit 14: spouse's employment changes (R6)"),
    15: ("RULE", _merge(_u15, _u17), "unit 15: Cigna nationwide, Kaiser for California and Hawaii (R7, D11); the opt-out "
         "allowance (R3)"),
    16: ("NOT", None, "other:norm", "unit 16: 'Use the Flimp PlanSelect tool ... or contact Cigna One Guide' (a request "
         "with no outcome)"),
    17: ("RULE", _u17, "unit 17: $150 with group coverage and an active waiver; dental, vision and other benefits (R3); "
         "the last sentence against 'must actively waive' with no waiver: the text's two outcomes, derive none (D4)"),
    18: ("PART", _u15, "cross-reference", "unit 18: all US states except Hawaii (R7); 'three coverage options' and the "
         "plan details and costs are in the US Benefits Guide (not pinned)"),
    19: ("RULE", _nothing, "unit 19: 'GitLab HSA Contributions:' (the ':' parent of units 20-21)"),
    20: ("RULE", _u20, "unit 20: $100 a month, team member only (R8)"),
    21: ("RULE", _u20, "unit 21: $125, team member + spouse/child/family (R8)"),
    22: ("RULE", _u22, "unit 22: Utah: Intermountain Healthcare (R7)"),
    23: ("RULE", _u23, "unit 23: taxable at state level in California, Alabama, New Jersey (R7); other states: the text "
         "is silent (not a cause)"),
    24: ("PART", _u15, "cross-reference", "unit 24: Hawaii and California (R7); each state's Kaiser plan options and "
         "costs are in the US Benefits Guide"),
    25: ("NOT", None, "cross-reference", "unit 25: dental plan details and costs in the US Benefits Guide (not pinned); "
         "'two coverage levels' decides nothing"),
    26: ("NOT", None, "cross-reference", "unit 26: vision plan details and costs in the US Benefits Guide (not pinned)"),
    27: ("RULE", _u27, "unit 27: voluntary, optional, after-tax premium (R9)"),
    28: ("RULE", _merge(_u28, _qle, _u105), "unit 28: new hire, open enrollment or a qualifying life event (R9)"),
    29: ("NOT", None, "cross-reference", "unit 29: 'See the US Benefits Guide' (not pinned)"),
    30: ("RULE", _u30, "unit 30: at no cost (R17)"),
    31: ("RULE", _u31, "unit 31: 3 face-to-face sessions (R17)"),
    32: ("RULE", _u32, "unit 32: 30-minute consultations, 25% fee discounts (R17)"),
    33: ("RULE", _u33, "unit 33: 30-minute consultation, 25% tax services discount (R17)"),
    34: ("NOT", None, NO, "unit 34: 'Healthcare navigation support' describes; no outcome"),
    35: ("NOT", None, NO, "unit 35: 'Additional coverage beyond business travel policy' describes; no amount or condition"),
    36: ("PART", _u36, "cross-reference", "unit 36: min(2 x salary, $500,000), AD&D equal (R10); 'See the US Benefits "
         "Guide' points outside"),
    37: ("RULE", _u37, "unit 37: covered from day one (R10)"),
    38: ("RULE", _u38, "unit 38: survivor assurance included (R10)"),
    39: ("RULE", _u39, "unit 39: no cost (R10)"),
    40: ("PART", _u40, "cross-reference", "unit 40: voluntary life through Cigna (R10); details and costs in the US "
         "Benefits Guide"),
    41: ("PART", _u41, "cross-reference", "unit 41: not in COBRA, ends on the last day, continue with Cigna (R10); "
         "'contact them for premium information' points outside; on the last day itself the text is silent"),
    42: ("PART", _u42, "other:judgment standard", "unit 42: up to 66.7% of base salary at no cost (R11); 'qualifying "
         "disabilities' is a stated judgment; 'See the US Benefits Guide' points outside; an inexact 66.7% product has no "
         "answer (no rounding rule in the text)"),
    43: ("NOT", None, NO, "unit 43: 'The process:' introduces the steps (no outcome)"),
    44: ("NOT", None, NO, "unit 44: the Absence Management team will guide you (a description; its items a-c are context)"),
    45: ("PART", _u45, "other:norm", "unit 45: at least 5 calendar days before the planned return (R11); 'Include any needed "
         "accommodations' is a duty with no outcome; the physician's authorization is a stated judgment"),
    46: ("RULE", _merge(_u46, _u109), "unit 46: more than 26 weeks -> unpaid leave, COBRA option, long-term disability "
         "(R11); exactly 26 weeks: the text is silent (not a cause)"),
    47: ("PART", _u47, "deadline/time limit", "unit 47: within 3 business days (R11): BRIDGED (bridge.business_days_after, "
         "a Monday-Friday calendar the case states)"),
    48: ("PART", _u48, "cross-reference", "unit 48: immediate eligibility and vesting (R12); plan details in the US "
         "Benefits Guide"),
    49: ("NOT", None, "cross-reference", "unit 49: 'Please see the 401(k) Administration and Enrollment Guide' (not pinned)"),
    50: ("PART", _u50, "amount arithmetic", "unit 50: rate of 6% or more -> 3% of earnings capped at $1,500; rate 0 -> $0 "
         "(R12); a rate between 0 and 6% needs rate x earnings, a product of two stated quantities the language cannot "
         "write (secondary: the Match Guide pointer)"),
    51: ("NOT", None, NO, "unit 51: investment choices through Fidelity NetBenefits (describes)"),
    52: ("NOT", None, "other:norm", "unit 52: 'Join our live financial workshops' (an invitation with no outcome)"),
    53: ("PART", _u53, "other:norm", "unit 53: call Fidelity for automatic conversions (R17); 'Follow these instructions' "
         "is a duty pointing to instructions not pinned (secondary cross-reference)"),
    54: ("NOT", None, "cross-reference", "unit 54: the Fidelity FAQ and the webinar (not pinned)"),
    55: ("PART", _u55, "other:norm", "unit 55: after-tax deductions take priority over ESPP (R17); 'Calculate carefully "
         "...' is advice with no outcome"),
    56: ("PART", _u56, "other:norm", "unit 56: converted amounts taxable in the year of conversion (R17); 'Consult your "
         "tax advisor' is advice"),
    57: ("NOT", None, "other:norm", "unit 57: 'Complete this form or call Fidelity' (a procedure with no outcome)"),
    58: ("NOT", None, "other:norm", "unit 58: 'Contact Fidelity directly ...' (a procedure with no outcome)"),
    59: ("PART", _u59, "cross-reference", "unit 59: 50% of the vested balance or $50,000, whichever is less (R12); 'Prime + "
         "1%' turns on the prime rate, outside the text"),
    60: ("NOT", None, "other:norm", "unit 60: 'Request online or call Fidelity' (a procedure with no outcome)"),
    61: ("RULE", _u61, "unit 61: repaid via ACH from the personal bank account (R17)"),
    62: ("RULE", _u62, "unit 62: repaid with after-tax dollars (R17)"),
    63: ("NOT", None, NO, "unit 63: 'Tax-advantaged accounts to help ...' introduces the part (no outcome)"),
    64: ("PART", _u20, "cross-reference", "unit 64: $100 / $125 a month; HDHP required (R8); the contribution limits are in "
         "the US Benefits Guide"),
    65: ("NOT", None, NO, "unit 65: what an HSA lets you do (describes)"),
    66: ("RULE", _nothing, "unit 66: 'Key benefits:' (the ':' parent of units 67-70)"),
    67: ("RULE", _u67, "unit 67: tax advantages (R13)"),
    68: ("RULE", _u68, "unit 68: rolls over annually, never expires (R13)"),
    69: ("NOT", None, "cross-reference", "unit 69: 'Once your balance reaches the minimum': the minimum is not in the text"),
    70: ("RULE", _u70, "unit 70: at age 65 any purpose without penalty (R13)"),
    71: ("NOT", None, NO, "unit 71: Fidelity administers; PlanSource will guide you (describes)"),
    72: ("NOT", None, "other:norm", "unit 72: 'Contact Fidelity ... Complete with your old provider's account information' "
         "(a procedure with no outcome)"),
    73: ("RULE", _u73, "unit 73: the HSA stays; the fee once GitLab is no longer the employer (R13)"),
    74: ("RULE", _u74, "unit 74: domestic partner HSA rules (R13)"),
    75: ("PART", _u75, "date/age arithmetic", "unit 75: anytime (R13); effective the 1st of the following month: BRIDGED "
         "(bridge.first_of_next_month); 'Use the Qualifying Life Event Process' is a procedure"),
    76: ("NOT", None, "other:norm", "unit 76: 'Contact Fidelity directly to front-load' ('Remember to:' parent); no "
         "outcome of its own"),
    77: ("NOT", None, "other:norm", "unit 77: 'Remember to include GitLab's contribution in your calculation' (advice)"),
    78: ("NOT", None, "other:norm", "unit 78: 'Remember to update your payroll deductions' (advice)"),
    79: ("PART", _u79, "other:norm", "unit 79: GitLab can't monitor contributions made outside payroll (R17); 'Track your "
         "own maximum contribution limits' is advice"),
    80: ("RULE", _u80, "unit 80: yours to keep when you leave (R13)"),
    81: ("NOT", None, "other:norm", "unit 81: 'Fidelity may charge management fees' decides nothing (D12)"),
    82: ("PART", _u82, "cross-reference", "unit 82: changes only in open enrollment or a qualifying life event (R14); the "
         "contribution limits are in the US Benefits Guide"),
    83: ("PART", _u83, "deadline/time limit", "unit 83: qualifying dependants written (R14); incurred through March 15, "
         "submitted by March 31: BRIDGED (bridge.month_day_after); 'Covers childcare and eldercare expenses' decides nothing"),
    84: ("RULE", _u84, "unit 84: no Medical FSA with an HSA (R14)"),
    85: ("RULE", _u85, "unit 85: Limited Purpose FSA with an HSA (R14)"),
    86: ("PART", _u86, "deadline/time limit", "unit 86: not before 5 business days after March 31, no later than April 22 "
         "(R14): BRIDGED (bridge.business_days_after, month_day_of_year); between them the text is silent"),
    87: ("RULE", _nothing, "unit 87: 'Contribution and Rollover Limits:' (the ':' parent of unit 88)"),
    88: ("RULE", _u88, "unit 88: 2026: $3,400 max contribution (a stated Medical or Limited Purpose FSA), $680 max "
         "rollover (R14; latent fix U88)"),
    89: ("RULE", _nothing, "unit 89: 'Important Notes:' (the ':' parent of units 90-91)"),
    90: ("RULE", _u90, "unit 90: under $5 forfeited, over $5 rolls over (R14; the whole amount up to $680 only in a 2026 "
         "plan year: latent fix U90); exactly $5: 'Minimum $5 required' vs '$5 or less are forfeited': the text's two "
         "outcomes, derive none (D9; not a cause)"),
    91: ("RULE", _u91, "unit 91: rollover funds usable the following year (R14)"),
    92: ("RULE", _u92, "unit 92: up to and including the last day unless COBRA (R14)"),
    93: ("RULE", _u93, "unit 93: COBRA if contributed more than spent (R14)"),
    94: ("RULE", _u94, "unit 94: COBRA payments post-tax (R14)"),
    95: ("RULE", _u95, "unit 95: claims within 90 days of termination (R14)"),
    96: ("RULE", _u96, "unit 96: Dependent Care FSA: no COBRA, expenses through the last day (R14)"),
    97: ("RULE", _u95, "unit 97: claims within 90 days of termination (R14)"),
    98: ("RULE", _u98, "unit 98: 90 days after the plan year ends (R14)"),
    99: ("RULE", _u99, "unit 99: increases only with a qualifying event, no reductions, additional funds from the event "
         "date (R14)"),
    100: ("RULE", _u99, "unit 100: the example: original election before the event, the additional amount after (R14, "
          "D13)"),
    101: ("RULE", _u101, "unit 101: care not available within 100 miles (R15)"),
    102: ("RULE", _u101, "unit 102: enrolled in a Cigna Medical Plan (R15); 'Navia administers' describes"),
    103: ("RULE", _u103, "unit 103: pre-tax up to $2,100 (R15)"),
    104: ("RULE", _u104, "unit 104: post-tax $900 for the excess (R15)"),
    # in-scope lines that are no unit (ISOLATION.md D3): own rows beside the unit rows
    105: ("RULE", _merge(_qle, _u105), "line 105 (not a unit, D3): within 30 days of the qualifying event (R6)"),
    106: ("PART", _u106, "other:norm", "line 106 (not a unit, D3): EPO figures (R16; the slash read as "
          "individual/family); 'Consider PPO 500 or HSA plans' is advice with no outcome"),
    107: ("NOT", None, "other:norm", "line 107 (not a unit, D3): 'may need to complete an EOI' decides nothing (D12)"),
    108: ("PART", _u108, "cross-reference", "line 108 (not a unit, D3): contact Absence Management (R18); 'See Sick Time "
          "reporting procedures' points outside (secondary: 'as soon as possible', a judgment standard)"),
    109: ("PART", _u109, "other:norm", "line 109 (not a unit, D3): the 26-week maximum benefit period (R11); 'you'll need "
          "to determine if you can return' is a duty with no outcome"),
}


# the ledger's mark column for the units not fully written: bridged (reads a bridge.py value) | stated (a stated judgment
# carries the rest) | not written (default)
LEDGER_MARK = {47: "bridged", 75: "bridged", 83: "bridged", 86: "bridged", 42: "stated", 45: "stated"}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a sub-case: [{"id", "unit", "formula", "defines"}]; a formula grounded by two units is kept once."""
    out, seen = [], set()
    for n, e in sorted(units_table(mutant).items()):
        if e[1] is None:
            continue
        for i, (f, target) in enumerate(e[1](ctx)):
            kk = key([f, target])
            if kk in seen:
                continue
            seen.add(kk)
            out.append({"id": f"u{n}.{i}", "unit": n, "formula": f, "defines": [] if target is None else [target]})
    return out


# --- structure helpers --------------------------------------------------------------------------------------------

def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def atoms_in(f, atoms, constants):
    if type(f) is not list or not f:
        return
    if f[0] in ("unary", "binary"):
        atoms.add(key(f))
        return
    if f[0] == "const" and len(f) == 3:
        constants.add(f[2])
        return
    for part in f[1:]:
        atoms_in(part, atoms, constants)


UNIT_RECORDS = {
    DAY: {"scale": "1", "display": {"kind": "iso_date"}},
    NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
    HRS: {"scale": "100", "display": {"kind": "decimal", "label": "hours per week"}},
    AGE: {"scale": "1", "display": {"kind": "decimal", "label": "years of age"}},
    PCT: {"scale": "100", "display": {"kind": "decimal", "label": "%"}},
    MILE: {"scale": "100", "display": {"kind": "decimal", "label": "miles"}},
    WEEK: {"scale": "1", "display": {"kind": "decimal", "label": "weeks"}},
    CNT: {"scale": "1", "display": {"kind": "decimal", "label": "count"}},
    MIN: {"scale": "1", "display": {"kind": "decimal", "label": "minutes"}},
    YEAR: {"scale": "1", "display": {"kind": "decimal", "label": "year"}},
    USD: {"scale": "100", "display": {"kind": "money", "currency": "USD", "input_symbol": "$"}},
}


def environment(ctx, used=None):
    consts = {}
    for x, kind in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's {kind} {x}.", "verbalisation": f"{kind} {x}"}
    for name in sorted(used or ()):
        base, x = name.split("_", 1)
        u, w = BASES[base]
        consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                        "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."} for n, d in {**FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A team member, family member, event, enrollment, account, "
                                                            "change, expense, note, disability, trip or day."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1", "units": dict(UNIT_RECORDS)}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _swaps(ns, fn):
    def apply(t):
        for n in ns:
            t = _swap(n, fn)(t)
        return t
    return apply


def _json_sub(a, b):
    return lambda builder: (lambda ctx: [(json.loads(json.dumps(f).replace(a, b)), tg) for f, tg in builder(ctx)])


def _reshift(f, n):
    """A date step 'a is N days after b' (bare or as an implication's conclusion) with N replaced."""
    if f[0] == "shift_days":
        return shift(f[1], f[2], n)
    if f[0] == "implies" and f[2][0] == "shift_days":
        return Implies(f[1], shift(f[2][1], f[2][2], n))
    return f


def _shift_n(prefix, n):
    return lambda b: (lambda ctx: [(f if tg is None or not tg.startswith(prefix) else _reshift(f, n), tg)
                                   for f, tg in b(ctx)])


def _drop(builder):
    return _nothing


MUTANTS = {
    "M1": ("THRESHOLD: eligibility 'at least 30 hours' read as more than 30", _swap(4, _json_sub(
        '["le", ["decimal", "hour_week", "30"]', '["lt", ["decimal", "hour_week", "30"]'))),
    "M2": ("DATE: the 30-day sign-up period read as 31 days", _swaps((1, 2, 17, 15), _shift_n("sul_", 31))),
    "M3": ("CONDITION: the waiver allowance without the active waiver (D4 dropped)", _swaps((2, 15, 17), _json_sub(
        '["unary", "aw", ["const", "p"]]', '["top"]'))),
    "M4": ("AMOUNT: the waiver allowance $150 read as $125", _swaps((2, 15, 17), _json_sub(
        '"usd_cent", "150.00"', '"usd_cent", "125.00"'))),
    "M5": ("AGE: children 'up to age 26' read as under 27 (26 covered)", _swap(7, _json_sub(
        '"age_year", "26"]]', '"age_year", "27"]]'))),
    "M6": ("CONDITION: unit 9 dropped (a family member covered twice)", _swap(9, _drop)),
    "M7": ("DATE: the 30 days after a qualifying event read as 31", _swaps((28, 105), _shift_n("evl_", 31))),
    "M8": ("CONDITION: Hawaii read as a Cigna state", _swaps((15, 18, 24), _json_sub(
        '["implies", ["unary", "hi", ["const", "p"]], ["not", ["unary", "cigok"', '["implies", ["bottom"], ["not", ["unary", "cigok"'))),
    "M9": ("AMOUNT: HSA family contribution $125 read as $100", _swaps((20, 21, 64), _json_sub(
        '"usd_cent", "125.00"', '"usd_cent", "100.00"'))),
    "M10": ("CONDITION: the HDHP requirement dropped (HSA contribution without the HDHP)", _swaps((20, 21, 64), _json_sub(
        '["implies", ["not", ["unary", "hdhp", ["const", "p"]]], ["eq", ["const", "usd_cent", "hsac_p"], ["decimal", "usd_cent", "0.00"]]]',
        '["implies", ["bottom"], ["eq", ["const", "usd_cent", "hsac_p"], ["decimal", "usd_cent", "0.00"]]]'))),
    "M11": ("AMOUNT: basic life cap $500,000 read as $400,000", _swap(36, _json_sub(
        '"usd_cent", "500000.00"', '"usd_cent", "400000.00"'))),
    "M12": ("AMOUNT: 401(k) match cap $1,500 read as $2,000", _swap(50, _json_sub(
        '"usd_cent", "1500.00"', '"usd_cent", "2000.00"'))),
    "M13": ("AMOUNT: 401(k) match 50% of the first 6% read as 100% (6% of earnings)", _swap(50, _json_sub(
        '["scale", "usd_cent", "3", ["const", "usd_cent", "earn_p"]]', '["scale", "usd_cent", "6", ["const", "usd_cent", "earn_p"]]'))),
    "M14": ("AMOUNT: the loan cap $50,000 read as $40,000 (the $100,000 switch point unchanged)", _swap(59, _json_sub(
        '"usd_cent", "50000.00"', '"usd_cent", "40000.00"'))),
    "M15": ("DATE: return-to-work 'at least 5 calendar days' read as 4", _swap(45, _shift_n("rtl_", 4))),
    "M16": ("THRESHOLD: FSA rollover $5 minimum read as at least $1", _swaps((90, 91), _json_sub(
        '"usd_cent", "5.00"', '"usd_cent", "1.00"'))),
    "M17": ("AMOUNT: FSA max rollover $680 read as $640", _swaps((88, 90), _json_sub(
        '"usd_cent", "680.00"', '"usd_cent", "640.00"'))),
    "M18": ("DATE: FSA claims 90 days after termination read as 60", _swaps((95, 97), _shift_n("ctl_", 60))),
    "M19": ("DATE: the runout 90 days after the plan year read as 89", _swap(98, _shift_n("rol_", 89))),
    "M20": ("THRESHOLD: Dependent Care FSA children 'under 13' read as 13 or under", _swap(83, _json_sub(
        '"age_year", "13"', '"age_year", "14"'))),
    "M21": ("CONDITION: Medical FSA with an HSA allowed (unit 84 reversed)", _swap(84, lambda b: (lambda ctx: [
        (U("mfsaok", P), tg) for f, tg in b(ctx)][:1]))),
    "M22": ("THRESHOLD: Travel HRA 'not within 100 miles' read as at least 100 miles", _swaps((101, 102), _json_sub(
        '["lt", ["decimal", "mile", "100"]', '["le", ["decimal", "mile", "100"]'))),
    "M23": ("AMOUNT: Travel HRA pre-tax $2,100 read as $2,000", _swap(103, _json_sub(
        '"usd_cent", "2100.00"', '"usd_cent", "2000.00"'))),
    "M24": ("CONDITION: 'reductions aren't allowed' dropped (a decrease outside open enrollment not refused)", _swaps(
        (82, 99, 100), _json_sub('["and", ["unary", "dec", ', '["and", ["unary", "inc", '))),
    "M25": ("DURATION: 'after 26 weeks' read as after 25 weeks (175 days)", _swap(46, _json_sub(
        '["decimal", "elapsed_day", "182"]', '["decimal", "elapsed_day", "175"]'))),
    # latent fixes 2026-11-25 (LATENT-DEPARTURES.md 10, 11): each restores the frozen rule; the question set asks neither
    # case (killed on the smoke set S22d/S22y and by tests/test_gitlab_us_benefits_latent.py)
    "M27": ("CONDITION: unit 88's $3,400 test on every FSA account, Dependent Care included (the frozen _u88)",
            _swap(88, lambda b: _u88_frozen)),
    "M28": ("CONDITION: the whole amount left (over $5, up to $680) rolls over in any plan year (the frozen _u90)",
            _swap(90, lambda b: _u90_frozen)),
    "M26": ("CONDITION: the Cigna Medical Plan requirement of the Travel HRA dropped", _swaps((101, 102), _json_sub(
        '["unary", "cig", ["const", "p"]]', '["top"]'))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
