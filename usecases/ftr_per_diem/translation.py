"""Federal Travel Regulation 41 CFR 301-11.1 to 301-11.23 (per diem and subsistence; statute corpus batch 4, US regulation):
the VE translation, one pass with today's language. CROSS-FAMILY questions (Codex writer), Opus translator.

Row statute-corpus-ftr-per-diem (dri-statute-corpus-ftr-per-diem-w-1124, Opus 5.5). Written from the pinned source
(manage-agents reviews/spare/statute-corpus/batch4/ftr-per-diem/source.txt, sha256 ea4135cf...f245fe, US federal work) and its
68 units (units.jsonl, sha256 765b00d9...3f7199). The encoder's question file (questions only, no answers, no tags) was read
BEFORE this file was written (ISOLATION.md says so). Scope and the decisions D1-D16 are ISOLATION.md's, fixed before the
writer ran; the readings below are fixed here, before cases.py exists. Evidence branch: nothing here is a Lean kernel line,
a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each unit n of units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one sub-case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
A builder returns (formula, target) pairs: target is the atom key or constant the formula defines (None = a check).

ONE SUB-CASE = the items one question needs: the employee p, the trip t (its travel status), the locations whose rates the
case states (loc), the calendar days (day) and nights (night) asked about or summed, their meals and expense items, and the
other things a question is about (rest period, long-term lodging, deposits, returns). Every value a rule needs is a stated
fact (dates, clock times, offsets, durations of single periods, amounts in USD) or a value computed in Lean from them; there
is NO bridge script: clock moments, the 12 and 24 hours, calendar days, flight time and the rest length are steps in Lean.

READINGS (fixed here; refuse when in doubt; D-numbers are ISOLATION.md's):
R1  Travel status (units 4, 10, 33; D5): a moment is (day, minute of the day). Departure and return are the stated moments
    at the residence, office or other authorized point. Clock times of one time zone are compared as given; a trip whose
    clock times carry UTC offsets (the dateline case) is converted to UTC in Lean (minute - offset, the day moved by one when
    the minute leaves 0..1439). "more than 12 hours": the return is strictly after departure + 12 h (exactly 12:00 is not
    more); "24 hours or more": the return is at or after departure + 24 h; "more than 12 but less than 24" = more than 12
    and not 24 or more.
R2  Eligibility (units 1-4): eligible when on official travel away from the official station or other agency-defined areas
    (stated), incurring subsistence expenses while performing it, and in travel status more than 12 hours; not eligible
    when not on official travel or not more than 12 hours. "Incurring subsistence expenses": a stated payment for lodging
    or a meal during the official travel (the per diem the text pays is lodging plus M&IE: units 8, 54, 55).
R3  Must pay (units 5-7): the agency must pay an eligible employee's subsistence expenses unless (a) the travel is to a
    training event under the Government Employees Training Act and the employee agreed not to be paid, or (b) it is for a
    pre-employment interview and the interviewing agency does not authorize payment; either exception -> not required.
R4  M&IE share of a calendar day (unit 55; D6): ineligible trip or a day outside travel status -> none; more than 12 but
    less than 24 hours -> 75 percent for each calendar day in travel status; 24 hours or more -> 75 percent on the day of
    departure and the day of return, 100 percent on each day between. 75 percent of a rate r is the m with 4 m = 3 r (Lean;
    no rounding is ever applied: an m with no whole-cent value has no model: refused). Calendar days are the local days of
    the stated departure and return. Travel that crosses the international dateline (unit 33: actual elapsed travel time,
    not calendar days) gets no calendar-day share and no per-calendar-day ship rate (refused); an ineligible trip still
    gets none.
R5  Applicable rate (units 9, 39, 50; D9): the per diem rate of a day or night is the TDY location's, except (i) a day or
    night in an authorized rest stop: the rest stop location's (39); (ii) where the agency authorized the alternate location
    and the case states it advantageous to the Government: the alternate location's (9, 50). "Generally" in unit 9 is read
    as this default with the text's own two exceptions; nothing else displaces it. A reduced per diem validly prescribed
    (R12) replaces the location's lodging and M&IE amounts on the days it covers.
R6  Meals provided (units 57-59; D6): a meal provided by the Government or included in a registration fee is deducted at its
    amount in the stated breakdown, on every day (the first and last day: the entire allocated amount from the 75 percent
    amount); a meal from a common carrier or a complimentary hotel/motel meal is not deducted. The day's M&IE = the share
    amount minus the deductions, but never below the breakdown's incidental expenses amount (58 second sentence, on every
    day). A day with no provided meal: the share amount. Full M&IE (60-62; R13): the share amount, no deduction.
R7  Lodging of a night (units 15-23, 54; D7): conventional: the single occupancy rate; Government quarters: the fee or service
    charge; friends or relatives: the host's additional costs the case states substantiated and deemed reasonable (never a
    token amount or comparable lodging); nonconventional: the amount paid, only when no conventional lodging is available or
    it is in short supply (else nothing); recreational vehicle: the expenses of the kinds unit 20 lists ("such as": an expense
    of another kind is neither counted nor excluded: refused; for a personally-owned vehicle never purchase, sale or payment
    for the vehicle, unit 23; such a payment for a vehicle not stated personally owned: refused); a personally-owned residence: nothing outside an authorized relocation (during
    one these sections decide nothing). Reimbursed: the cost when at most the applicable lodging rate, else the rate, for an
    expense the case states actual and necessary (54).
R8  Arrival after midnight (unit 9): a night with a stated arrival counts when the arrival is on or before its day, or on the
    next day strictly after 00:00 (the employee may claim the lodging for the preceding calendar day); 00:00 exactly: no
    answer (D5).
R9  Long-term lodging (units 24-31; D7): the total lodging cost = the costs on unit 25-31's list (rental of a furnished
    dwelling; for an unfurnished one the rent and the furniture and appliances the case states necessary; utilities; maid
    fees and cleaning charges the case states reasonable; monthly telephone and internet use fees; other costs the case
    states typically included in a hotel/motel price in the area); installation charges are excluded from the telephone
    and internet fees and long-distance charges from the telephone fee (units 29, 30), and a separate installation or
    long-distance charge of none of the listed kinds is not on the list; such a charge also stated to be of another listed
    kind (rent, furniture, a utility connection, maid or cleaning, a typical cost) is neither: refused. The daily
    lodging rate d is the amount with d added once for each of the stated days of occupancy for which the employee is
    entitled to lodging (each such day is one item: an enumeration of the stated count, no coefficient from a case) equal
    to the total; it is capped at "the daily per diem rate for the TDY location": its lodging rate plus its M&IE rate (the
    per diem is lodging plus M&IE, units 8, 54, 55; R11). A night of the long-term lodging costs the daily rate (then
    capped at the lodging rate as R7), and counts only when the case states it is one of the occupancy days for which the
    employee is entitled to lodging (not stated: refused).
R10 Lodging taxes (units 47, 48; D8): in CONUS and non-foreign OCONUS, the taxes paid are reimbursable when the night's whole
    lodging cost is reimbursable (cost at most the rate); when the cost exceeds the rate the tax on the capped cost needs a
    tax rate times an amount: no answer (refused, ledger amount arithmetic). Foreign areas: no separate claim (0).
R11 Actual expense (unit 49; D12): the ceiling of a day = 3 x (lodging rate + M&IE rate) of the applicable location when the
    agency authorized the maximum, else the stated lesser ceiling (at most that). All claimed amounts of a day may be
    reimbursed when their sum is at most the ceiling (and stated actual and necessary); not when it exceeds it.
R12 Reduced per diem (units 63-65): validly prescribed when the agency prescribed it, the case states the agency could
    determine in advance that costs would be lower, the reduced amounts are lower than the location's, and the rate was
    stated in a travel authorization issued before travel or (stated judgment) sufficient notice was given once travel had
    begun.
R13 Full M&IE (units 60-62): the agency allowed it (stated) and either the employee was unable to take part due to official
    business (stated), or medical requirements or religious beliefs prevented consuming the meal and a substitute was bought,
    and, where the employee had advance knowledge, approval was requested before the trip's departure day and a reasonable
    effort (stated) was made.
R14 Rest periods (units 34-39; D10, D11): may be authorized when the origin or destination is outside CONUS (a place stated as
    a foreign area or a non-foreign OCONUS area), the scheduled flight time including stopovers (the sum of the stated legs
    and stopovers, Lean) exceeds 14 hours, the route is stated direct or usually traveled, the agency determined business
    class not advantageous, and the travel is coach or premium economy; and the rest period is at most 24 hours, or exceeds
    it with no scheduled departure within 24 hours of arrival at the intermediate point, the employee booked on the first
    available departure and the agency's stated reasonable length. Not when any of these fails.
R15 Non-workdays (unit 40; D9): a scheduled non-workday counts as a travel day when the travel status requires staying at the
    TDY location (or traveling) and the case states the agency's decision that remaining is the cost-effective approach;
    otherwise no answer. The days and nights of unit 46's hypothetical stay ("had the employee remained") are days of
    remaining by that hypothesis.
R16 Voluntary return (unit 46; D12): the reimbursement = the smaller of the return's stated round-trip transportation and
    subsistence costs and what would have been allowed at the TDY location for the days and nights away (lodging per R7 and
    M&IE per R4, from the stated rates).
R17 Ship travel (unit 56): the agency's stated rate for each calendar day, when within the applicable M&IE rate, replaces
    unit 55's shares (55(a) "Except as provided in paragraph (b)").
R18 Duties, permissions, pointers (units 11-14, 32, 41-45, 52, 53, 66-68; D9): a plain duty or permission of the text is
    written as the yes/no predicate the question asks (must / should / may / is required), nothing more; a pointer to an
    outside provision is written only as the pointer itself (its content is out of scope: ledger cross-reference).
R19 Receipts (units 66-68): under the actual expense method every expense is itemized; a receipt is required for lodging
    whatever its amount and for a meal costing more than $75 (exactly $75.00: none).
No number from a case's facts is ever a coefficient: every coefficient is a literal of the pinned text (75 and 300 percent,
12, 14 and 24 hours, $75) or a unit conversion (60 minutes an hour, 1440 a day).
"""
from __future__ import annotations

import hashlib
import json

USD, DAY, MIN = "usd_cent", "day", "minute"

# base -> (unit, wording); a constant is f"{base}_{item}"; bases carry no "_"
BASES = {
    # trip (travel status)
    "dd": (DAY, "the day of departure from the residence, office or other authorized point (stated)"),
    "dm": (MIN, "the minute of the day of the departure (stated)"),
    "rd": (DAY, "the day of return to the residence, office or other authorized point (stated)"),
    "rm": (MIN, "the minute of the day of the return (stated)"),
    "doff": (MIN, "the departure clock's offset from UTC in minutes (stated)"),
    "roff": (MIN, "the return clock's offset from UTC in minutes (stated)"),
    "ud": (DAY, "the departure day on the comparison clock"),
    "um": (MIN, "the departure minute on the comparison clock"),
    "vd": (DAY, "the return day on the comparison clock"),
    "vm": (MIN, "the return minute on the comparison clock"),
    "ta": (DAY, "the day 12 hours after departure falls on"),
    "tb": (MIN, "the minute 12 hours after departure"),
    "tc": (DAY, "the day 24 hours after departure falls on"),
    "tad": (DAY, "the day the travel authorization stating the reduced rate was issued (stated)"),
    "rmr": (USD, "the reduced M&IE amount for a full day (stated)"),
    "rlr": (USD, "the reduced lodging amount (stated)"),
    "shr": (USD, "the agency's M&IE rate for travel by ship for each calendar day (stated)"),
    "pdt": (USD, "the per diem for the whole trip (lodging plus M&IE)"),
    # location
    "lr": (USD, "the location's maximum lodging rate (stated)"),
    "mr": (USD, "the location's M&IE rate (stated)"),
    "bb": (USD, "the breakdown's breakfast amount for the M&IE rate (stated)"),
    "bl": (USD, "the breakdown's lunch amount (stated)"),
    "bn": (USD, "the breakdown's dinner amount (stated)"),
    "bi": (USD, "the breakdown's incidental expenses amount (stated)"),
    # day or night
    "dy": (DAY, "the calendar day (stated)"),
    "lrx": (USD, "the applicable lodging rate"),
    "mrx": (USD, "the applicable M&IE rate"),
    "inc": (USD, "the applicable incidental expenses amount"),
    "mb": (USD, "the day's M&IE share amount"),
    "dsum": (USD, "the day's meal deductions"),
    "raw": (USD, "the share amount less the deductions"),
    "mie": (USD, "the day's M&IE"),
    "lcl": (USD, "the lesser actual-expense ceiling under agency policy (stated)"),
    "cl": (USD, "the day's actual-expense ceiling"),
    "cs": (USD, "the day's claimed actual expenses"),
    "rqd": (DAY, "the day the employee requested approval to claim the full M&IE (stated)"),
    # night
    "ny": (DAY, "the calendar day of the night (stated)"),
    "ad": (DAY, "the day of arrival at the lodging facility (stated)"),
    "am": (MIN, "the minute of the day of arrival at the lodging facility (stated)"),
    "sor": (USD, "the single occupancy rate for the night (stated)"),
    "fee": (USD, "the Government quarters fee or service charge for the night (stated)"),
    "pay": (USD, "the amount paid for the night (stated)"),
    "tx": (USD, "the lodging taxes paid for the night (stated)"),
    "lc": (USD, "the night's lodging cost"),
    "lo": (USD, "the night's reimbursable lodging"),
    "txr": (USD, "the night's reimbursable lodging taxes"),
    # expense items, meals
    "amt": (USD, "the item's amount (stated)"),
    "ia": (USD, "the item's amount counted"),
    "ded": (USD, "the meal's deduction"),
    # long-term lodging
    "ltc": (USD, "the long-term lodging's total cost"),
    "dly": (USD, "the long-term lodging's daily lodging rate before the cap"),
    "dlr": (USD, "the long-term lodging's daily lodging rate"),
    "pdr": (USD, "the TDY location's daily per diem rate (lodging plus M&IE) for the long-term lodging"),
    # rest period
    "lh": (MIN, "the leg's whole hours (stated)"),
    "lm": (MIN, "the leg's minutes beyond the hours (stated)"),
    "lmin": (MIN, "the leg's minutes"),
    "ft": (MIN, "the scheduled flight time including stopovers in minutes"),
    "rh": (MIN, "the rest period's whole hours (stated)"),
    "rn": (MIN, "the rest period's minutes beyond the hours (stated)"),
    "rlen": (MIN, "the rest period's length in minutes"),
    # voluntary return
    "rc": (USD, "the return's stated transportation and subsistence costs"),
    "wh": (USD, "what would have been allowed at the TDY location"),
    "vr": (USD, "the voluntary return's reimbursement"),
}
STATED_BASES = ("dd", "dm", "rd", "rm", "doff", "roff", "tad", "rmr", "rlr", "shr", "lr", "mr", "bb", "bl", "bn", "bi", "dy",
                "lcl", "rqd", "ny", "ad", "am", "sor", "fee", "pay", "tx", "amt", "lh", "lm", "rh", "rn")
STEP_BASES = tuple(b for b in BASES if b not in STATED_BASES)

FACTS = {
    # trip
    "offtr": "the employee performed official travel away from the official station or other areas defined by the agency",
    "paidsub": "the employee paid for lodging or a meal during the official travel",
    "geta": "the travel is to a training event under the Government Employees Training Act",
    "agree": "the employee agreed not to be paid subsistence expenses",
    "intv": "the travel is for a pre-employment interview",
    "intauth": "the interviewing agency authorized subsistence expense payment",
    "idl": "the travel crosses the international dateline",
    "altauth": "the agency authorized the per diem rate of the alternate location where lodging was obtained",
    "adv": "the stated judgment: the alternate location (its lodging and rate) is advantageous to the Government",
    "ship": "the travel is by ship",
    "redp": "the agency prescribed a reduced per diem rate",
    "redadv": "the stated judgment: the agency could determine in advance that lodging and/or meal costs would be lower",
    "redta": "the reduced rate is stated in the travel authorization",
    "suff": "the stated judgment: the notice given once travel had begun was sufficient to adjust spending",
    "aem": "the expenses are reimbursed under the actual expense method",
    "selcom": "the employee is selecting a commercial lodging facility",
    # location
    "tdyl": "the location is the TDY location",
    "altl": "the location is the alternate location where lodging was obtained",
    "conus": "the location is stated to be in CONUS",
    "nfo": "the location is stated to be a non-foreign area outside CONUS",
    "frgn": "the location is stated to be a foreign area",
    # day
    "nwd": "the day is a scheduled non-workday",
    "stayreq": "the travel status requires staying at the TDY location or traveling on the day",
    "remain": "the stated judgment: the agency determined remaining in travel status the most cost-effective approach",
    "redx": "the reduced per diem covers the day or night",
    "rs": "the day or night falls in a rest stop the agency authorized, at the location stated for it",
    "aed": "the agency authorized actual expense for the day",
    "aemax": "the agency authorized actual expense up to the maximum the text permits for the day",
    "lesser": "the agency authorized a lesser actual-expense ceiling for the day",
    "allowfull": "the agency allowed a full M&IE claim for the day",
    "offbiz": "the stated judgment: the employee was unable to take part in the Government-furnished meal due to the conduct "
              "of official business",
    "medrel": "the stated judgment: medical requirements or religious beliefs prevented consuming the furnished meal",
    "subst": "the employee purchased substitute meals instead",
    "advk": "the employee had advance knowledge of the meal to be furnished",
    "reqb": "the employee requested specific approval to claim the full M&IE allowance",
    "effort": "the stated judgment: the employee made a reasonable effort to make alternative meal arrangements but was "
              "unable to",
    "an": "the stated judgment: the expenses are actual and necessary",
    # meal
    "gov": "the meal was provided by the Government",
    "regfee": "the meal was included in a registration fee",
    "carrier": "the meal was provided by a common carrier",
    "comp": "the meal was a complimentary meal provided by a hotel or motel",
    "brk": "the meal is breakfast",
    "lun": "the meal is lunch",
    "din": "the meal is dinner",
    # night
    "conv": "the lodging is conventional lodging",
    "govq": "the lodging is Government quarters",
    "friends": "the lodging is with friends or relatives",
    "noncon": "the lodging is nonconventional lodging",
    "rv": "the lodging is a recreational vehicle",
    "rvown": "the lodging is a personally-owned recreational vehicle",
    "por": "the lodging is a personally-owned residence",
    "noconv": "no conventional lodging is available in the area, or conventional lodging is in short supply",
    "reloc": "the expense is incurred during an authorized relocation",
    "ltent": "the night is one of the occupancy days for which the employee is entitled to subsistence expense "
             "reimbursement for lodging",
    # expense items
    "host": "the item is an additional cost incurred by the host to accommodate the employee",
    "substr": "the stated judgment: the agency substantiated the host's cost and deemed it reasonable",
    "token": "the item is a flat token amount or the cost of comparable conventional lodging",
    "rvl": "the item is a recreational-vehicle expense of a kind unit 20 lists (parking, utilities, electricity, fuel, "
           "water, sewage, bath or shower, dumping fees)",
    "rvbuy": "the item is for purchasing, selling or paying for the recreational vehicle or camper",
    "frent": "the item is the rental cost of a furnished dwelling",
    "urent": "the item is the rental cost of an unfurnished dwelling",
    "furn": "the item is furniture or appliances for an unfurnished dwelling",
    "necf": "the stated judgment: the furniture or appliances are necessary",
    "util": "the item is a cost of connecting, disconnecting or using utilities",
    "maid": "the item is a maid fee or cleaning charge",
    "reasm": "the stated judgment: the maid fees and cleaning charges are reasonable",
    "phone": "the item is a monthly telephone use fee",
    "net": "the item is a monthly internet/wifi use fee",
    "typ": "the stated judgment: the item is a cost typically included in a hotel/motel room price in the area",
    "inst": "the item is an installation charge",
    "ldist": "the item is a long-distance call charge",
    "lodg": "the claimed item is lodging",
    "meal": "the claimed item is a meal",
    # rest period
    "ocon": "the travel's origin is stated to be in CONUS",
    "dcon": "the travel's destination is stated to be in CONUS",
    "direct": "the stated judgment: the travel is by a direct or usually traveled route",
    "bna": "the stated judgment: the agency determined that travel by business class is not advantageous",
    "coach": "the travel is by coach class",
    "pe": "the travel is by premium economy class",
    "nodep": "no scheduled transportation departs within 24 hours of arrival at the intermediate point",
    "firstb": "the employee is scheduled to board the first available scheduled departure",
    "reas": "the stated judgment: the agency determined the additional length of the rest period reasonable",
    # deposits, returns
    "curt": "the stated judgment: the assignment was curtailed, canceled or interrupted for official purposes or reasons "
            "beyond the employee's control and acceptable to the agency",
    "nonref": "the pre-paid expense is not refundable",
    "tried": "the stated judgment: the employee sought to obtain a refund or took steps to minimize costs",
    "failed": "the employee failed to perform the scheduled travel",
    "unacc": "the stated judgment: the employee's reasons for not performing the travel were unacceptable to the agency",
    "forf": "the employee forfeited the advance room deposit",
    "reqoff": "the agency requires the employee to return to the official station to perform official business",
    "savings": "the stated judgment: the agency will realize substantial cost savings by the employee's return home",
    "justx": "the stated judgment: periodic return travel home is justified as part of an extended TDY assignment",
}
STATED_JUDGMENT = ("adv", "redadv", "suff", "remain", "offbiz", "medrel", "effort", "an", "substr", "necf", "reasm", "typ",
                   "direct", "bna", "reas", "curt", "tried", "unacc", "savings", "justx")
DERIVED = {
    "incur": "the employee incurred subsistence expenses while performing official travel",
    "more12": "the travel status lasted more than 12 hours",
    "ge24": "the travel status lasted 24 hours or more",
    "short": "the travel status lasted more than 12 but less than 24 hours",
    "elig": "the employee is eligible for reimbursement of per diem or actual subsistence expenses",
    "excp": "one of unit 5's exceptions applies",
    "mustpay": "the agency must pay the employee's subsistence expenses",
    "indays": "the day is a calendar day in travel status",
    "outd": "the day is outside the travel status",
    "first": "the day is the day of departure",
    "last": "the day is the day of return",
    "mid": "the day is a full day between the first and the last",
    "dayok": "the day counts as a day of travel for subsistence",
    "s75": "the employee receives 75 percent of the applicable M&IE rate for the day",
    "s100": "the employee receives 100 percent of the applicable M&IE rate for the day",
    "s0": "the employee receives no M&IE for the day",
    "full": "the employee may claim the full M&IE amount for the day",
    "dedok": "the provided meal must be deducted",
    "mealy": "the day has a provided meal entered",
    "redok": "the reduced per diem rate may be prescribed",
    "nightok": "the night counts for lodging",
    "claimprev": "the employee may claim the lodging cost for the preceding calendar day",
    "ncok": "the nonconventional lodging is reimbursable",
    "tokok": "the token amount or comparable conventional lodging may be claimed as lodging reimbursement",
    "bar": "the personally-owned residence exclusion bars the expense",
    "barany": "the personally-owned residence exclusion bars one of the expenses asked about",
    "allow": "the item may be considered part of the long-term lodging cost",
    "anyinc": "one of the items asked about may be included in the long-term lodging cost",
    "sepx": "the lodging taxes may be claimed separately",
    "allok": "all the claimed actual expenses of the day may be reimbursed",
    "itemize": "the employee must itemize all expenses, each meal separately",
    "rcpt": "a receipt is required for the claimed item",
    "cond4": "the four conditions for a rest period hold",
    "mayrest": "the agency may authorize the rest period",
    "ppok": "the employee may be reimbursed for the non-refundable pre-paid expense",
    "repay": "the employee must repay the forfeited deposit",
    "mayret": "the agency may authorize per diem and round-trip transportation for the periodic return",
    "mayalt": "the agency may authorize the alternate location's rate in advance and a different method each calendar day",
    "daymeth": "the agency may allow a different method to be used each calendar day",
    "useel": "actual elapsed travel time is used to compute the subsistence entitlement rather than calendar days",
    "resv": "the employee must make the lodging reservation through the agency's travel management service",
    "fsfr": "the employee should stay in a fire safe facility and give first consideration to Government lodging programs",
    "dc5707": "section 5707a of title 5 applies to the government of the District of Columbia",
    "emg30": "these sections direct emergency travel due to incapacitating illness or injury to part 301-30",
    "n70": "the note to 301-11.17 refers to 301-70.201 for a blanket actual expense authorization exceeding the per diem rate",
}
BINARY = {"ap": "the per diem rate of the location (second) applies to the day or night (first)"}


# --- formula helpers (ve-quantity@1 wire shapes) --------------------------------------------------------------------

def U(p, x): return ["unary", p, ["const", x]]
def B(p, x, y): return ["binary", p, ["const", x], ["const", y]]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def usd(v): return ["decimal", USD, v]
def mn(v): return ["decimal", MIN, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
def add(tag, a, b): return ["add", tag, a, b]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]       # a is n days after b
TRUE, FALSE = ["top"], ["bottom"]
ZERO = usd("0.00")


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


def Add(unit, terms):
    terms = list(terms)
    if not terms:
        return ["decimal", unit, "0"] if unit != USD else ZERO
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = ["add", unit, t, r]
    return r


UNIT_OF = {b: u for b, (u, _) in BASES.items()}


def k(base, x):
    return ["const", UNIT_OF[base], f"{base}_{x}"]


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def A(p, x):
    return key(U(p, x))


def A2(p, x, y):
    return key(B(p, x, y))


def sameday(a, b):
    return And(no_later(a, b), no_later(b, a))


def minus(tag, a, b):
    return add(tag, a, scale(tag, -1, b))


# --- the case context -------------------------------------------------------------------------------------------------

class Ctx:
    """items: [(id, kind)]; parent: {child: parent}; link: {(item, role): item} (structural links the encoder transcribes:
    "at" the location of a rest-stop day or night, "lt" the long-term lodging of a night, "vr" the voluntary return of a
    hypothetical day or night); n: {long-term lodging: the stated count of entitled days}; arr: nights with a stated arrival;
    zoned: trips whose clock times carry UTC offsets. Kinds: person, trip, loc, day, hday, night, hnight, meal, hx (host
    cost), rvx, porx, lt, lx (long-term cost), cx (claimed item), rp (rest period), leg, pp, dep, ret, vret, rx, misc."""

    def __init__(self, items, parent=None, link=None, n=None, arr=(), zoned=()):
        self.items = list(items)
        self.parent = dict(parent or {})
        self.link = dict(link or {})
        self.n = dict(n or {})
        self.arr = set(arr)
        self.zoned = set(zoned)

    def of(self, *kinds):
        return [x for x, kd in self.items if kd in kinds]

    def kind(self, x):
        return dict(self.items)[x]

    def children(self, x, *kinds):
        kd = dict(self.items)
        return [y for y, _ in self.items if self.parent.get(y) == x and (not kinds or kd[y] in kinds)]

    def trip(self, x):
        while x is not None and self.kind(x) != "trip":
            x = self.parent.get(x)
        return x


P = "p"


def both(pos, neg, atom, x):
    """atom(x) <- pos; not atom(x) <- neg (either may be None)."""
    out = []
    if pos is not None:
        out.append((Implies(pos, U(atom, x)), A(atom, x)))
    if neg is not None:
        out.append((Implies(neg, Not(U(atom, x))), A(atom, x)))
    return out


def both2(pos, neg, atom, x, y):
    out = []
    if pos is not None:
        out.append((Implies(pos, B(atom, x, y)), A2(atom, x, y)))
    if neg is not None:
        out.append((Implies(neg, Not(B(atom, x, y))), A2(atom, x, y)))
    return out


def lt_moment(ad, am, bd, bm):
    """(ad, am) strictly before (bd, bm)."""
    return Or(before(ad, bd), And(sameday(ad, bd), Lt(am, bm)))


def le_moment(ad, am, bd, bm):
    return Or(before(ad, bd), And(sameday(ad, bd), Le(am, bm)))


# --- R1: travel status ------------------------------------------------------------------------------------------------

def _utc(t, d, m, off, D, M):
    """The comparison clock: local (d, m) for one time zone; minus the offset for a zoned trip (R1)."""
    if t not in _CTX.zoned:
        return [(shift(k(D, t), k(d, t), 0), f"{D}_{t}"), (Eq(k(M, t), k(m, t)), f"{M}_{t}")]
    x = minus(MIN, k(m, t), k(off, t))
    lo, hi = Le(mn(0), x), Lt(x, mn(1440))
    return [(Implies(And(lo, hi), shift(k(D, t), k(d, t), 0)), f"{D}_{t}"),
            (Implies(And(lo, hi), Eq(k(M, t), x)), f"{M}_{t}"),
            (Implies(Lt(x, mn(0)), shift(k(d, t), k(D, t), 1)), f"{D}_{t}"),
            (Implies(Lt(x, mn(0)), Eq(k(M, t), add(MIN, x, mn(1440)))), f"{M}_{t}"),
            (Implies(Le(mn(1440), x), shift(k(D, t), k(d, t), 1)), f"{D}_{t}"),
            (Implies(Le(mn(1440), x), Eq(k(M, t), add(MIN, x, mn(-1440)))), f"{M}_{t}")]


_CTX = None
_MUT = None


def _status(ctx, h12=720):
    out = []
    for t in ctx.of("trip"):
        out += _utc(t, "dd", "dm", "doff", "ud", "um") + _utc(t, "rd", "rm", "roff", "vd", "vm")
        um, ud, vd, vm = k("um", t), k("ud", t), k("vd", t), k("vm", t)
        out += [(Implies(Lt(um, mn(1440 - h12)), shift(k("ta", t), ud, 0)), f"ta_{t}"),
                (Implies(Le(mn(1440 - h12), um), shift(k("ta", t), ud, 1)), f"ta_{t}"),
                (Implies(Lt(um, mn(1440 - h12)), Eq(k("tb", t), add(MIN, um, mn(h12)))), f"tb_{t}"),
                (Implies(Le(mn(1440 - h12), um), Eq(k("tb", t), add(MIN, um, mn(h12 - 1440)))), f"tb_{t}"),
                (shift(k("tc", t), ud, 1), f"tc_{t}")]
        ta, tb, tc = k("ta", t), k("tb", t), k("tc", t)
        out += both(lt_moment(ta, tb, vd, vm), le_moment(vd, vm, ta, tb), "more12", t)
        out += both(le_moment(tc, um, vd, vm), lt_moment(vd, vm, tc, um), "ge24", t)
        out += both(And(U("more12", t), Not(U("ge24", t))), Or(Not(U("more12", t)), U("ge24", t)), "short", t)
    return out


def _elig(ctx):
    """Units 1-4 (R2)."""
    out = []
    for t in ctx.of("trip"):
        out += both(U("paidsub", t), None, "incur", t)
        out += both(And(U("offtr", t), U("incur", t), U("more12", t)), Or(Not(U("offtr", t)), Not(U("more12", t))),
                    "elig", t)
    return out


def _mustpay(ctx):
    """Units 5-7 (R3)."""
    out = []
    for t in ctx.of("trip"):
        exc = Or(And(U("geta", t), U("agree", t)), And(U("intv", t), Not(U("intauth", t))))
        noexc = And(Or(Not(U("geta", t)), Not(U("agree", t))), Or(Not(U("intv", t)), U("intauth", t)))
        out += both(exc, noexc, "excp", t)
        out += both(And(U("elig", t), Not(U("excp", t))), U("excp", t), "mustpay", t)
    return out


# --- R5: applicable rate ----------------------------------------------------------------------------------------------

def _xs(ctx):
    return ctx.of("day", "hday", "night", "hnight")


def _rates(ctx):
    """Units 9, 39, 50 (R5) and the rates of a day or night; R12's reduced amounts."""
    out = []
    for x in _xs(ctx):
        t = ctx.trip(x)
        locs = ctx.children(t, "loc")
        at = ctx.link.get((x, "at"))
        alt = FALSE if _MUT == "M15" else And(U("altauth", t), U("adv", t))
        if _MUT == "M16":
            at = None
        for L in locs:
            if at is not None:
                out += both2(U("rs", x) if L == at else None, U("rs", x) if L != at else None, "ap", x, L)
            nrs = TRUE if _MUT == "M16" else Not(U("rs", x))
            nalt = TRUE if _MUT == "M15" else Not(U("altauth", t))
            out += both2(And(nrs, alt, U("altl", L)), And(nrs, alt, Not(U("altl", L))), "ap", x, L)
            out += both2(And(nrs, nalt, U("tdyl", L)), And(nrs, nalt, Not(U("tdyl", L))), "ap", x, L)
            red = Not(U("redx", x))
            out.append((Implies(And(B("ap", x, L), red), Eq(k("lrx", x), k("lr", L))), f"lrx_{x}"))
            out.append((Implies(And(B("ap", x, L), red), Eq(k("mrx", x), k("mr", L))), f"mrx_{x}"))
            out.append((Implies(B("ap", x, L), Eq(k("inc", x), k("bi", L))), f"inc_{x}"))
        out.append((Implies(And(U("redok", t), U("redx", x)), Eq(k("lrx", x), k("rlr", t))), f"lrx_{x}"))
        out.append((Implies(And(U("redok", t), U("redx", x)), Eq(k("mrx", x), k("rmr", t))), f"mrx_{x}"))
    return out


# --- R4, R6, R13, R15, R17: M&IE of a day -----------------------------------------------------------------------------

def _days(ctx, q=(3, 4)):
    out = []
    for x in ctx.of("day", "hday"):
        t = ctx.trip(x)
        dy, dd, rd = k("dy", x), k("dd", t), k("rd", t)
        out += both(And(no_later(dd, dy), no_later(dy, rd)), Or(before(dy, dd), before(rd, dy)), "indays", x)
        out += both(Or(before(dy, dd), before(rd, dy)), And(no_later(dd, dy), no_later(dy, rd)), "outd", x)
        out += both(sameday(dy, dd), Or(before(dy, dd), before(dd, dy)), "first", x)
        out += both(sameday(dy, rd), Or(before(dy, rd), before(rd, dy)), "last", x)
        out += both(And(before(dd, dy), before(dy, rd)), Or(no_later(dy, dd), no_later(rd, dy)), "mid", x)
        if ctx.kind(x) == "hday":
            out += both(TRUE, None, "dayok", x)          # R15: unit 46's hypothetical stay
        else:
            out += both(Or(Not(U("nwd", x)), And(U("stayreq", x), U("remain", x))), And(U("nwd", x), Not(U("stayreq", x))),
                        "dayok", x)
        nship = TRUE if _MUT == "M22" else Not(U("ship", t))
        if _MUT == "M31":                                                 # M31: calendar-day shares across the dateline
            base = And(U("elig", t), U("dayok", x), nship)
            out += both(And(base, Or(And(U("short", t), U("indays", x)), And(U("ge24", t), Or(U("first", x), U("last", x))))),
                        Or(Not(U("elig", t)), U("outd", x), U("ship", t), U("mid", x),
                           And(U("ge24", t), Not(U("first", x)), Not(U("last", x)))), "s75", x)
            out += both(And(base, U("ge24", t), U("mid", x)),
                        Or(Not(U("elig", t)), U("outd", x), U("ship", t), U("short", t), U("first", x), U("last", x)),
                        "s100", x)
            out += both(Or(Not(U("elig", t)), U("outd", x)), And(U("elig", t), U("indays", x)), "s0", x)
        else:
            cal = Not(U("idl", t))                                        # unit 33: no calendar-day share across the IDL
            base = And(U("elig", t), U("dayok", x), nship, cal)
            out += both(And(base, Or(And(U("short", t), U("indays", x)), And(U("ge24", t), Or(U("first", x), U("last", x))))),
                        Or(Not(U("elig", t)), U("ship", t), And(cal, Or(U("outd", x), U("mid", x),
                           And(U("ge24", t), Not(U("first", x)), Not(U("last", x)))))), "s75", x)
            out += both(And(base, U("ge24", t), U("mid", x)),
                        Or(Not(U("elig", t)), U("ship", t),
                           And(cal, Or(U("outd", x), U("short", t), U("first", x), U("last", x)))), "s100", x)
            out += both(Or(Not(U("elig", t)), And(cal, U("outd", x))), And(U("elig", t), U("indays", x), cal), "s0", x)
        mb, mrx = k("mb", x), k("mrx", x)
        out.append((Implies(U("s75", x), Eq(scale(USD, q[1], mb), scale(USD, q[0], mrx))), f"mb_{x}"))
        out.append((Implies(U("s100", x), Eq(mb, mrx)), f"mb_{x}"))
        out.append((Implies(U("s0", x), Eq(mb, ZERO)), f"mb_{x}"))
    return out


def _full(ctx):
    """Units 60-62 (R13)."""
    out = []
    for x in ctx.of("day"):
        t = ctx.trip(x)
        adv_ok = Or(Not(U("advk", x)), And(U("reqb", x), before(k("rqd", x), k("dd", t)), U("effort", x)))
        if _MUT == "M21":                                                 # M21: (2) required without advance knowledge
            adv_ok = And(U("reqb", x), before(k("rqd", x), k("dd", t)), U("effort", x))
        cond = Or(U("offbiz", x), And(U("medrel", x), U("subst", x), adv_ok))
        out += both(And(U("allowfull", x), cond), Not(U("allowfull", x)), "full", x)
    return out


def _meals(ctx):
    """Units 57-59 (R6)."""
    out = []
    for m in ctx.of("meal"):
        x = ctx.parent[m]
        if _MUT == "M5":                                                  # M5: carrier meals deducted
            out += both(And(Or(U("gov", m), U("regfee", m), U("carrier", m)), Not(U("comp", m))),
                        Or(U("comp", m), And(Not(U("gov", m)), Not(U("regfee", m)), Not(U("carrier", m)))), "dedok", m)
        else:
            out += both(And(Or(U("gov", m), U("regfee", m)), Not(U("carrier", m)), Not(U("comp", m))),
                        Or(U("carrier", m), U("comp", m), And(Not(U("gov", m)), Not(U("regfee", m)))), "dedok", m)
        for L in ctx.children(ctx.trip(x), "loc"):
            for f, b in (("brk", "bb"), ("lun", "bl"), ("din", "bn")):
                out.append((Implies(And(B("ap", x, L), U(f, m), U("dedok", m)), Eq(k("ded", m), k(b, L))), f"ded_{m}"))
        out.append((Implies(Not(U("dedok", m)), Eq(k("ded", m), ZERO)), f"ded_{m}"))
    return out


def _mie(ctx):
    """The day's M&IE (R6, R13, R17)."""
    out = []
    for x in ctx.of("day", "hday"):
        t = ctx.trip(x)
        meals = ctx.children(x, "meal")
        mb, mie = k("mb", x), k("mie", x)
        ns = TRUE if _MUT == "M22" else Not(U("ship", t))
        if not meals:
            out.append((Implies(ns, Eq(mie, mb)), f"mie_{x}"))
        else:
            out.append((Eq(k("dsum", x), Add(USD, [k("ded", m) for m in meals])), f"dsum_{x}"))
            out.append((Eq(add(USD, k("raw", x), k("dsum", x)), mb), f"raw_{x}"))
            nf = Not(U("full", x)) if ctx.kind(x) == "day" else TRUE
            out.append((Implies(And(ns, nf, Le(k("inc", x), k("raw", x))), Eq(mie, k("raw", x))), f"mie_{x}"))
            out.append((Implies(And(ns, nf, Lt(k("raw", x), k("inc", x))), Eq(mie, k("inc", x))), f"mie_{x}"))
            if ctx.kind(x) == "day":
                out.append((Implies(And(ns, U("full", x)), Eq(mie, mb)), f"mie_{x}"))
        if _MUT != "M22":
            cal = None if _MUT == "M31" else Not(U("idl", t))             # unit 33: no per-calendar-day rate across the IDL
            out.append((Implies(And(U("ship", t), U("elig", t), U("indays", x), cal, Le(k("shr", t), k("mrx", x))),
                                Eq(mie, k("shr", t))), f"mie_{x}"))
    return out


# --- R7-R10: lodging --------------------------------------------------------------------------------------------------

def _nights(ctx):
    out = []
    for n in ctx.of("night", "hnight"):
        lc, lo = k("lc", n), k("lo", n)
        ent = U("ltent", n) if (n, "lt") in ctx.link and _MUT != "M32" else TRUE   # unit 24: entitled occupancy days
        if n in ctx.arr:
            ad, ny = k("ad", n), k("ny", n)
            if _MUT == "M14":                                             # M14: the preceding-day claim dropped
                out += both(None, TRUE, "claimprev", n)
                out += both(And(ent, no_later(ad, ny)), None, "nightok", n)
            else:
                out += both(And(shift(ad, ny, 1), Lt(mn(0), k("am", n))), no_later(ad, ny), "claimprev", n)
                out += both(And(ent, Or(no_later(ad, ny), U("claimprev", n))), None, "nightok", n)
        else:
            out += both(ent, None, "nightok", n)
        ok = And(U("an", n), U("nightok", n))
        out.append((Implies(And(ok, Le(lc, k("lrx", n))), Eq(lo, lc)), f"lo_{n}"))
        out.append((Implies(And(ok, Lt(k("lrx", n), lc)), Eq(lo, k("lrx", n))), f"lo_{n}"))
    return out


def _conv(ctx):
    return [(Implies(U("conv", n), Eq(k("lc", n), k("sor", n))), f"lc_{n}") for n in ctx.of("night", "hnight")
            if (n, "lt") not in ctx.link]


def _govq(ctx):
    return [(Implies(U("govq", n), Eq(k("lc", n), k("fee", n))), f"lc_{n}") for n in ctx.of("night", "hnight")]


def _items_sum(ctx, n, kind, pos, neg):
    out = []
    xs = ctx.children(n, kind)
    for i in xs:
        out.append((Implies(pos(i), Eq(k("ia", i), k("amt", i))), f"ia_{i}"))
        out.append((Implies(neg(i), Eq(k("ia", i), ZERO)), f"ia_{i}"))
    return out, Add(USD, [k("ia", i) for i in xs])


def _friends(ctx):
    out = []
    for n in ctx.of("night"):
        r, s = _items_sum(ctx, n, "hx", lambda i: And(U("host", i), U("substr", i), Not(U("token", i))),
                          lambda i: Or(U("token", i), Not(U("host", i))))
        out += r + [(Implies(U("friends", n), Eq(k("lc", n), s)), f"lc_{n}")]
        out += both(None, U("friends", n), "tokok", n)
    return out


def _noncon(ctx):
    out = []
    for n in ctx.of("night"):
        if _MUT == "M23":                                                 # M23: unit 19 dropped
            out += both(None, U("noncon", n), "ncok", n)
        else:
            out += both(And(U("noncon", n), U("noconv", n)), And(U("noncon", n), Not(U("noconv", n))), "ncok", n)
        if (n, "lt") not in ctx.link:
            out.append((Implies(U("ncok", n), Eq(k("lc", n), k("pay", n))), f"lc_{n}"))
        out.append((Implies(And(U("noncon", n), Not(U("noconv", n))), Eq(k("lo", n), ZERO)), f"lo_{n}"))
    return out


def _rv(ctx):
    out = []
    for n in ctx.of("night"):
        if _MUT == "M28":                                                 # M28: unit 20's list read as exhaustive
            zero = lambda i: Or(U("rvbuy", i), Not(U("rvl", i)))  # noqa: E731
        elif _MUT == "M33":                                               # M33: unit 23 without "personally-owned"
            zero = lambda i: U("rvbuy", i)  # noqa: E731
        else:
            zero = lambda i, n=n: And(U("rvbuy", i), U("rvown", n))  # noqa: E731
        r, s = _items_sum(ctx, n, "rvx", lambda i: And(U("rvl", i), Not(U("rvbuy", i))), zero)
        out += r + [(Implies(U("rv", n), Eq(k("lc", n), s)), f"lc_{n}")]
    return out


def _por(ctx):
    """Unit 22: a personally-owned residence: nothing outside an authorized relocation."""
    out = []
    for n in ctx.of("night"):
        out.append((Implies(And(U("por", n), Not(U("reloc", n))), Eq(k("lo", n), ZERO)), f"lo_{n}"))
    xs = ctx.of("porx")
    for i in xs:
        out += both(And(U("por", i), Not(U("reloc", i))), U("reloc", i), "bar", i)
    if xs:
        out += both(Or(*[U("bar", i) for i in xs]), And(*[Not(U("bar", i)) for i in xs]), "barany", P)
    return out


def _rvbuy(ctx):
    """Unit 23: no expense for purchasing, selling or paying for a personally-owned RV (an item of _rv's sum: 0)."""
    return []


def _longterm(ctx):
    """Units 24-31 (R9)."""
    out = []
    for lt in ctx.of("lt"):
        t = ctx.trip(lt)
        allow = lambda i: Or(U("frent", i), U("urent", i), And(U("furn", i), U("necf", i)), U("util", i),  # noqa: E731
                             And(U("maid", i), U("reasm", i)), U("phone", i), U("net", i), U("typ", i))
        xs = ctx.children(lt, "lx")
        for i in xs:
            inst, ldist = U("inst", i), U("ldist", i)
            other = Or(*[U(f, i) for f in ("frent", "urent", "furn", "util", "maid", "typ")])
            ph, nt = U("phone", i), U("net", i)
            excl = And(Not(other), Or(And(inst, Or(ph, nt)), And(ldist, ph), And(Or(inst, ldist), Not(ph), Not(nt))))
            if _MUT == "M13":
                out += both(Or(allow(i), U("inst", i), U("ldist", i)), None, "allow", i)
            elif _MUT == "M30":                                           # M30: the exclusion on every kind of item
                out += both(And(allow(i), Not(inst), Not(ldist)), Or(inst, ldist), "allow", i)
            else:
                out += both(And(allow(i), Not(inst), Not(ldist)), excl, "allow", i)
            out.append((Implies(U("allow", i), Eq(k("ia", i), k("amt", i))), f"ia_{i}"))
            out.append((Implies(Not(U("allow", i)), Eq(k("ia", i), ZERO)), f"ia_{i}"))
        out.append((Eq(k("ltc", lt), Add(USD, [k("ia", i) for i in xs])), f"ltc_{lt}"))
        nd = ctx.n.get(lt)
        if nd:
            out.append((Eq(Add(USD, [k("dly", lt)] * nd), k("ltc", lt)), f"dly_{lt}"))
        for L in ctx.children(t, "loc"):
            if _MUT == "M29":                                             # M29: capped at the lodging rate only
                cap = k("lr", L)
            else:
                out.append((Implies(U("tdyl", L), Eq(k("pdr", lt), add(USD, k("lr", L), k("mr", L)))), f"pdr_{lt}"))
                cap = k("pdr", lt)
            out.append((Implies(And(U("tdyl", L), Le(k("dly", lt), cap)), Eq(k("dlr", lt), k("dly", lt))), f"dlr_{lt}"))
            out.append((Implies(And(U("tdyl", L), Lt(cap, k("dly", lt))), Eq(k("dlr", lt), cap)), f"dlr_{lt}"))
        ex = ctx.of("lx")
        ask = [i for i in ex if ctx.link.get((i, "asked"))]
        if ask:
            out += both(Or(*[U("allow", i) for i in ask]), And(*[Not(U("allow", i)) for i in ask]), "anyinc", P)
    for n in ctx.of("night"):
        lt = ctx.link.get((n, "lt"))
        if lt is not None:
            out.append((Eq(k("lc", n), k("dly", lt)), f"lc_{n}"))
    return out


def _tax(ctx):
    """Units 47, 48 (R10)."""
    out = []
    for n in ctx.of("night"):
        t = ctx.trip(n)
        for L in ctx.children(t, "loc"):
            dom = Or(U("conus", L), U("nfo", L))
            out.append((Implies(And(B("ap", n, L), dom, U("an", n), U("nightok", n), Le(k("lc", n), k("lrx", n))),
                                Eq(k("txr", n), k("tx", n))), f"txr_{n}"))
            out.append((Implies(And(B("ap", n, L), U("frgn", L)), Eq(k("txr", n), ZERO)), f"txr_{n}"))
            out += both(And(B("ap", n, L), dom), And(B("ap", n, L), U("frgn", L)), "sepx", n)
    return out


def _pdt(ctx):
    """The per diem for the whole trip: its nights' lodging and its days' M&IE."""
    out = []
    for t in ctx.of("trip"):
        ns, ds = ctx.children(t, "night"), ctx.children(t, "day")
        if ns or ds:
            out.append((Eq(k("pdt", t), Add(USD, [k("lo", n) for n in ns] + [k("mie", d) for d in ds])), f"pdt_{t}"))
    return out


# --- R11: actual expense ----------------------------------------------------------------------------------------------

def _actual(ctx, mult=3):
    out = []
    for x in ctx.of("day"):
        cl = k("cl", x)
        out.append((Implies(And(U("aed", x), U("aemax", x)), Eq(cl, scale(USD, mult, add(USD, k("lrx", x), k("mrx", x))))),
                    f"cl_{x}"))
        out.append((Implies(And(U("aed", x), U("lesser", x),
                                Le(k("lcl", x), scale(USD, mult, add(USD, k("lrx", x), k("mrx", x))))),
                            Eq(cl, k("lcl", x))), f"cl_{x}"))
        cx = ctx.children(x, "cx")
        if cx:
            out.append((Eq(k("cs", x), Add(USD, [k("amt", i) for i in cx])), f"cs_{x}"))
            out += both(And(U("aed", x), U("an", x), Le(k("cs", x), cl)), Lt(cl, k("cs", x)), "allok", x)
    return out


def _receipts(ctx, lim="75.00"):
    """Units 66-68 (R19)."""
    out = []
    for t in ctx.of("trip"):
        out += both(U("aem", t), None, "itemize", t)
    for i in ctx.of("cx"):
        t = ctx.trip(i)
        out += both(And(U("aem", t), Or(U("lodg", i), And(U("meal", i), Lt(usd(lim), k("amt", i))))),
                    And(Not(U("lodg", i)), U("meal", i), Le(k("amt", i), usd(lim))), "rcpt", i)
    return out


# --- R12: reduced per diem --------------------------------------------------------------------------------------------

def _reduced(ctx):
    out = []
    for t in ctx.of("trip"):
        locs = [L for L in ctx.children(t, "loc")]
        lower = And(*[Implies(U("tdyl", L), And(Lt(k("rlr", t), k("lr", L)), Lt(k("rmr", t), k("mr", L)))) for L in locs])
        notice = Or(And(U("redta", t), before(k("tad", t), k("dd", t))), U("suff", t))
        out += both(And(U("redp", t), U("redadv", t), lower, notice), Not(U("redadv", t)), "redok", t)
    return out


# --- R14: rest periods ------------------------------------------------------------------------------------------------

def _rest(ctx, h14=840, h24=1440):
    out = []
    for r in ctx.of("rp"):
        legs = ctx.children(r, "leg")
        for g in legs:
            out.append((Eq(k("lmin", g), add(MIN, scale(MIN, 60, k("lh", g)), k("lm", g))), f"lmin_{g}"))
        out.append((Eq(k("ft", r), Add(MIN, [k("lmin", g) for g in legs])), f"ft_{r}"))
        out.append((Eq(k("rlen", r), add(MIN, scale(MIN, 60, k("rh", r)), k("rn", r))), f"rlen_{r}"))
        cls = Or(U("coach", r), U("pe", r))
        if _MUT == "M25":                                                 # M25: premium economy dropped
            cls = U("coach", r)
        out += both(And(Or(Not(U("ocon", r)), Not(U("dcon", r))), Lt(mn(h14), k("ft", r)), U("direct", r), U("bna", r), cls),
                    Or(And(U("ocon", r), U("dcon", r)), Le(k("ft", r), mn(h14)), Not(U("direct", r)), Not(U("bna", r)),
                       Not(U("coach", r)) if _MUT == "M25" else And(Not(U("coach", r)), Not(U("pe", r)))), "cond4", r)
        rl = k("rlen", r)
        out += both(Or(And(U("cond4", r), Le(rl, mn(h24))),
                       And(U("cond4", r), Lt(mn(h24), rl), U("nodep", r), U("firstb", r), U("reas", r))),
                    Or(Not(U("cond4", r)), And(Lt(mn(h24), rl), Or(Not(U("nodep", r)), Not(U("firstb", r))))), "mayrest", r)
    return out


# --- R16: voluntary return --------------------------------------------------------------------------------------------

def _vret(ctx):
    out = []
    for v in ctx.of("vret"):
        rx = ctx.children(v, "rx")
        hn = [n for n in ctx.of("hnight") if ctx.link.get((n, "vr")) == v]
        hd = [d for d in ctx.of("hday") if ctx.link.get((d, "vr")) == v]
        out.append((Eq(k("rc", v), Add(USD, [k("amt", i) for i in rx])), f"rc_{v}"))
        out.append((Eq(k("wh", v), Add(USD, [k("lo", n) for n in hn] + [k("mie", d) for d in hd])), f"wh_{v}"))
        out.append((Implies(Le(k("rc", v), k("wh", v)), Eq(k("vr", v), k("rc", v))), f"vr_{v}"))
        out.append((Implies(Lt(k("wh", v), k("rc", v)), Eq(k("vr", v), k("wh", v))), f"vr_{v}"))
    return out


# --- R18: duties, permissions, pointers -------------------------------------------------------------------------------

def _u11(ctx):
    return both(TRUE, None, "resv", P) if ctx.of("misc") else []


def _u1213(ctx):
    return both(U("selcom", P), None, "fsfr", P) if ctx.of("misc") else []


def _u14(ctx):
    return both(None, TRUE, "dc5707", P) if ctx.of("misc") else []


def _u41(ctx):
    return both(TRUE, None, "emg30", P) if ctx.of("misc") else []


def _u52(ctx):
    return both(TRUE, None, "n70", P) if ctx.of("misc") else []


def _u32(ctx):
    out = []
    for i in ctx.of("pp"):
        out += both(And(U("curt", i), U("nonref", i), U("tried", i)), Or(Not(U("curt", i)), Not(U("tried", i))), "ppok", i)
    return out


def _u53(ctx):
    out = []
    for i in ctx.of("dep"):
        out += both(And(U("failed", i), U("unacc", i), U("forf", i)), Or(Not(U("failed", i)), Not(U("unacc", i))), "repay", i)
    return out


def _u33(ctx):
    out = []
    for t in ctx.of("trip"):
        out += both(U("idl", t), None, "useel", t)
    return out


def _periodic(ctx):
    out = []
    for r in ctx.of("ret"):
        out += both(Or(U("reqoff", r), U("savings", r), U("justx", r)),
                    And(Not(U("reqoff", r)), Not(U("savings", r)), Not(U("justx", r))), "mayret", r)
    return out


def _u8(ctx):
    """Unit 8's last sentence: a permission without condition."""
    out = []
    for t in ctx.of("trip"):
        if _MUT == "M27":                                                 # M27: tied to the alternate location's advantage
            out += both(U("adv", t), Not(U("adv", t)), "daymeth", t)
        else:
            out += both(TRUE, None, "daymeth", t)
    return out


def _u50(ctx):
    out = []
    for t in ctx.of("trip"):
        out += both(And(U("adv", t), U("daymeth", t)), Not(U("adv", t)), "mayalt", t)
    return out


def _merge(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


def _nothing(ctx):
    return []


_STATUS = _merge(_status, _elig)
_DAY = _merge(_status, _elig, _rates, _days, _mie, _reduced)

UNITS = {
    1: ("RULE", _STATUS, "unit 1: the eligibility lead-in (frames units 2-4; R2)"),
    2: ("RULE", _STATUS, "unit 2: performing official travel away from the official station (R2)"),
    3: ("RULE", _STATUS, "unit 3: incurring subsistence expenses (R2)"),
    4: ("RULE", _STATUS, "unit 4: more than 12 hours in travel status (R1, R2)"),
    5: ("RULE", _merge(_STATUS, _mustpay), "unit 5: the agency must pay unless (R3)"),
    6: ("RULE", _mustpay, "unit 6: Government Employees Training Act training and the employee's agreement (R3)"),
    7: ("RULE", _mustpay, "unit 7: a pre-employment interview without authorization (R3)"),
    8: ("PART", _merge(_u8, _u50), "other:no outcome", "unit 8: a different method each calendar day (written as a "
        "permission, R18); "
        "'primarily' and the appendix A pointer decide nothing (D1(c), D9)"),
    9: ("RULE", _merge(_rates, _nights), "unit 9: the TDY location's rate, the alternate location, arrival after midnight "
        "(R5, R8)"),
    10: ("RULE", _STATUS, "unit 10: the period starts and ends at the residence, office or other authorized point (R1)"),
    11: ("RULE", _u11, "unit 11: reservations through the travel management service (R18)"),
    12: ("RULE", _u1213, "unit 12: should stay in a fire safe facility (R18)"),
    13: ("RULE", _u1213, "unit 13: first consideration to Government lodging programs (R18)"),
    14: ("PART", _u14, "cross-reference", "unit 14: the pointer 'does not apply to the government of the District of "
         "Columbia' written; 5 U.S.C. 5707a itself is outside the pinned text"),
    15: ("RULE", _nothing, "unit 15: the lead-in of units 16-20 (D1(b))"),
    16: ("RULE", _merge(_conv, _nights), "unit 16: conventional lodging at the single occupancy rate (R7)"),
    17: ("RULE", _merge(_govq, _nights), "unit 17: Government quarters, the fee or service charge (R7)"),
    18: ("RULE", _merge(_friends, _nights), "unit 18: friends or relatives: the host's additional costs; no token or "
         "comparable lodging (R7)"),
    19: ("RULE", _merge(_noncon, _nights), "unit 19: nonconventional lodging when none conventional or short supply (R7)"),
    20: ("RULE", _merge(_rv, _nights), "unit 20: recreational vehicle expenses (R7)"),
    21: ("RULE", _nothing, "unit 21: the lead-in of units 22-23 (D1(b))"),
    22: ("RULE", _por, "unit 22: a personally-owned residence, except during an authorized relocation (R7)"),
    23: ("RULE", _merge(_rv, _rvbuy), "unit 23: no purchase, sale or payment for a personally-owned RV (R7)"),
    24: ("RULE", _longterm, "unit 24: the daily lodging rate = total / entitled days, capped (R9)"),
    25: ("RULE", _longterm, "unit 25: the lead-in of units 26-31 (R9)"),
    26: ("RULE", _longterm, "unit 26: furnished dwelling rent; unfurnished: rent and necessary furniture (R9)"),
    27: ("RULE", _longterm, "unit 27: utilities (R9)"),
    28: ("RULE", _longterm, "unit 28: reasonable maid fees and cleaning (R9; stated judgment)"),
    29: ("RULE", _longterm, "unit 29: monthly telephone use fee, not installation or long-distance (R9)"),
    30: ("RULE", _longterm, "unit 30: monthly internet use fee, not installation (R9)"),
    31: ("RULE", _longterm, "unit 31: other costs typically included (R9; stated judgment)"),
    32: ("RULE", _u32, "unit 32: pre-paid non-refundable expenses on a curtailment (R18; stated judgments)"),
    33: ("RULE", _merge(_status, _u33), "unit 33: crossing the dateline: actual elapsed time (R1)"),
    34: ("RULE", _rest, "unit 34: the rest-period lead-in (R14)"),
    35: ("RULE", _rest, "unit 35: origin or destination outside CONUS (R14)"),
    36: ("RULE", _rest, "unit 36: scheduled flight time over 14 hours (R14)"),
    37: ("RULE", _rest, "unit 37: direct or usually traveled route (R14; stated judgment)"),
    38: ("RULE", _rest, "unit 38: business class not advantageous; coach or premium economy (R14)"),
    39: ("RULE", _merge(_rest, _rates), "unit 39: the rest stop location's rate; over 24 hours (R5, R14)"),
    40: ("PART", _DAY, "other:norm", "unit 40: non-workdays at the TDY location (R15); 'the agency should determine the "
         "most cost-effective approach' is a duty of the agency (only as a stated decision)"),
    41: ("PART", _u41, "cross-reference", "unit 41: the pointer to part 301-30 written; its rules are outside the pinned text"),
    42: ("RULE", _periodic, "unit 42: the periodic-return lead-in (R18)"),
    43: ("RULE", _periodic, "unit 43: return to perform official business (R18)"),
    44: ("RULE", _periodic, "unit 44: substantial cost savings (R18; stated judgment)"),
    45: ("RULE", _periodic, "unit 45: justified as part of an extended TDY (R18; stated judgment)"),
    46: ("RULE", _merge(_vret, _DAY, _nights, _conv), "unit 46: voluntary return limited to what staying would allow (R16)"),
    47: ("PART", _tax, "amount arithmetic", "unit 47: lodging taxes in CONUS and non-foreign OCONUS when the whole cost is "
         "reimbursable (R10); the tax on a capped cost needs a tax rate times an amount"),
    48: ("RULE", _tax, "unit 48: no separate lodging-tax claim in foreign areas (R10)"),
    49: ("RULE", _actual, "unit 49: actual expense up to 300 percent; a lesser ceiling (R11)"),
    50: ("RULE", _merge(_u50, _rates), "unit 50: the alternative location's rate when advantageous (R5)"),
    51: ("PART", _u50, "other:judgment standard", "unit 51: approval 'typically provided in advance and at the agency's "
         "discretion': only the permission is written (D9)"),
    52: ("PART", _u52, "cross-reference", "unit 52: the note's pointer written; 301-70.201 is outside the pinned text"),
    53: ("RULE", _u53, "unit 53: advance room deposit; repay when forfeited for unacceptable reasons (R18)"),
    54: ("RULE", _merge(_nights, _rates, _pdt), "unit 54: actual and necessary, not over the lodging rate (R7); the per diem "
         "of a trip = its lodging plus its M&IE"),
    55: ("RULE", _merge(_DAY, _pdt), "unit 55: 75 percent and 100 percent of the M&IE rate (R4)"),
    56: ("RULE", _merge(_DAY, _mie), "unit 56: travel by ship: the agency's rate within the M&IE rate (R17)"),
    57: ("PART", _merge(_meals, _mie), "definition by reference", "unit 57: deducting provided meals (R6); the amounts "
         "'shown at https://www.gsa.gov/mie' are outside the text (stated per case)"),
    58: ("RULE", _merge(_meals, _mie), "unit 58: the entire allocated meal cost on the first and last day; the incidental "
         "expenses floor (R6)"),
    59: ("RULE", _meals, "unit 59: common carrier and complimentary hotel meals not deducted (R6)"),
    60: ("RULE", _merge(_full, _mie), "unit 60: full M&IE when unable to take part due to official business (R13)"),
    61: ("RULE", _full, "unit 61: medical requirements or religious beliefs and substitute meals (R13)"),
    62: ("RULE", _full, "unit 62: advance knowledge: approval before travel and a reasonable effort (R13)"),
    63: ("RULE", _reduced, "unit 63: the reduced per diem lead-in (R12)"),
    64: ("RULE", _reduced, "unit 64: determined in advance that costs will be lower (R12; stated judgment)"),
    65: ("RULE", _reduced, "unit 65: stated in the travel authorization before travel, or sufficient notice (R12)"),
    66: ("RULE", _receipts, "unit 66: itemize under the actual expense method (R19)"),
    67: ("RULE", _receipts, "unit 67: a receipt for lodging regardless of amount (R19)"),
    68: ("RULE", _receipts, "unit 68: a receipt for a meal over $75 (R19)"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None and MUTANTS[mutant][1] is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a sub-case: [{"id", "unit", "formula", "defines"}]; a formula grounded by two units is kept once."""
    global _CTX, _MUT
    _CTX, _MUT = ctx, mutant
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
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."} for n, d in BINARY.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "An employee, trip, location, day, night, meal, expense item, "
                                                             "rest period, deposit or return."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      MIN: {"scale": "1", "display": {"kind": "decimal", "label": "minutes"}},
                      USD: {"scale": "100", "display": {"kind": "money", "currency": "USD", "input_symbol": "$"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _json_sub(a, b):
    return lambda builder: (lambda ctx: [(json.loads(json.dumps(f).replace(a, b)), tg) for f, tg in builder(ctx)])


def _drop(builder):
    return _nothing


def _all(units, fn):
    """Apply fn to every unit whose builder is not None."""
    def apply(t):
        t = dict(t)
        for n in units:
            e = t[n]
            if e[1] is not None:
                t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


_ALLU = tuple(UNITS)


def _filter(fn):
    """A builder transform that rewrites each (formula, target) pair with fn."""
    return lambda builder: (lambda ctx: [fn(f, tg) for f, tg in builder(ctx)])


def _concl(prefix, old_base, new_base):
    """Rewrite a rule defining <prefix>_x whose conclusion is Eq(<prefix>_x, <old_base>_y) to Eq(<prefix>_x, <new_base>_x')."""
    def fn(f, tg):
        if tg and tg.startswith(prefix + "_") and f[0] == "implies" and f[2][0] == "eq" and f[2][2][0] == "const" \
                and f[2][2][2].startswith(old_base + "_"):
            x = tg.split("_", 1)[1]
            return Implies(f[1], Eq(f[2][1], k(new_base, x))), tg
        return f, tg
    return _filter(fn)


def _dly_less_one(f, tg):
    if tg and tg.startswith("dly_") and f[0] == "eq" and f[1][0] == "add":
        return Eq(f[1][3], f[2]), tg
    return f, tg


# A mutant is (description, table transform or None); FLAG mutants (transform None) are read by the builders through _MUT.
MUTANTS = {
    "M1": ("THRESHOLD: 'more than 12 hours' read as at least 12 hours", _all(_ALLU, _json_sub(
        '["lt", ["const", "minute", "tb_', '["le", ["const", "minute", "tb_'))),
    "M2": ("THRESHOLD: '24 hours or more' read as more than 24 hours", _all(_ALLU, _json_sub(
        '["le", ["const", "minute", "um_', '["lt", ["const", "minute", "um_'))),
    "M3": ("AMOUNT: 75 percent read as 80 percent", _all(_ALLU, _json_sub(
        '["scale", "usd_cent", "4", ["const", "usd_cent", "mb_', '["scale", "usd_cent", "5", ["const", "usd_cent", "mb_'))),
    "M4": ("CONDITION: the incidental-expenses floor dropped (the share less deductions, however low)",
           _all(_ALLU, _concl("mie", "inc", "raw"))),
    "M5": ("CONDITION: common-carrier meals deducted", None),
    "M6": ("AMOUNT: actual expense 300 percent read as 200 percent", _all(_ALLU, _json_sub(
        '["scale", "usd_cent", "3", ["add"', '["scale", "usd_cent", "2", ["add"'))),
    "M7": ("THRESHOLD: meal receipt over $75 read as $75 or more", _all(_ALLU, _json_sub(
        '["lt", ["decimal", "usd_cent", "75.00"]', '["le", ["decimal", "usd_cent", "75.00"]'))),
    "M8": ("THRESHOLD: flight time 'exceeds 14 hours' read as at least 14", _all(_ALLU, _json_sub(
        '["lt", ["decimal", "minute", "840"]', '["le", ["decimal", "minute", "840"]'))),
    "M9": ("CONDITION: the rest period over 24 hours without 'first available departure'", _all(_ALLU, _json_sub(
        '"firstb"', '"nodep"'))),
    "M10": ("CONDITION: the lodging cap at the lodging rate dropped (the cost however high)", _all(_ALLU, _concl("lo", "lrx", "lc"))),
    "M11": ("CONDITION: the long-term daily rate cap dropped", _all(_ALLU, _concl("dlr", "pdr", "dly"))),
    "M12": ("DIVISOR: the long-term total divided by one entitled day fewer", _all(_ALLU, _filter(_dly_less_one))),
    "M13": ("CONDITION: installation and long-distance charges allowed in long-term lodging", None),
    "M14": ("CONDITION: arrival after 12 midnight never claims the preceding calendar day (unit 9's last sentence dropped)",
            None),
    "M15": ("CONDITION: the alternate location ignored (the TDY rate always)", None),
    "M16": ("CONDITION: the rest stop location ignored", None),
    "M17": ("CONDITION: unit 5's training exception without the employee's agreement", _all(_ALLU, _json_sub(
        '["unary", "agree"', '["unary", "geta"'))),
    "M18": ("CONDITION: unit 32 without the refund attempt", _all(_ALLU, _json_sub('"tried"', '"nonref"'))),
    "M19": ("CONDITION: unit 53's repayment without unacceptable reasons", _all(_ALLU, _json_sub('"unacc"', '"failed"'))),
    "M20": ("AMOUNT: the voluntary return's limit dropped (the return costs always)", _all(_ALLU, _concl("vr", "wh", "rc"))),
    "M21": ("CONDITION: full M&IE needs the approval request and effort even without advance knowledge", None),
    "M22": ("CONDITION: ship travel paid by unit 55's shares (unit 56 dropped)", None),
    "M23": ("CONDITION: nonconventional lodging never reimbursable (unit 19 dropped)", None),
    "M24": ("CONDITION: lodging taxes reimbursable in foreign areas", _all(_ALLU, _json_sub('"frgn"', '"nfo"'))),
    "M25": ("CLASS: a rest period only for coach (premium economy dropped)", None),
    "M26": ("CONDITION: the reduced rate's sufficient notice read as the travel authorization", _all(_ALLU, _json_sub(
        '["unary", "suff"', '["unary", "redta"'))),
    "M27": ("CONDITION: unit 8's different method each calendar day only when the alternate location is advantageous",
            None),
    "M28": ("CONDITION: unit 20's list read as exhaustive (an RV expense of another kind counted at 0)", None),
    "M29": ("CAP: the long-term daily rate capped at the lodging rate, not the daily per diem rate", None),
    "M30": ("CONDITION: the installation and long-distance exclusion on every kind of long-term item", None),
    "M31": ("CONDITION: calendar-day M&IE shares for travel crossing the international dateline", None),
    "M32": ("CONDITION: a long-term night counted without its stated lodging entitlement", None),
    "M33": ("CONDITION: unit 23's bar on paying for the vehicle without 'personally-owned'", None),
}


def tg_item(tg):
    return json.loads(tg)[2][1]


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
