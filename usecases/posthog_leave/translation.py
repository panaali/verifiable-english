"""PostHog handbook "Time off" (statute corpus batch 4, text 2, NON-STATUTE (b) leave policy): the VE translation, one pass
with today's language.

Row statute-corpus-posthog-leave (dri-statute-corpus-posthog-leave-w-1124, Opus 5.5, translator and encoder). CROSS-FAMILY
questions (Codex writer, sealed in manage-agents reviews/spare/statute-corpus/batch4/posthog-leave/ISOLATION.md). Written from
the pinned source only (batch4/posthog-leave/source.txt, sha256 0f6cdd4f...0d9af; units.jsonl 46 units, 3 table rows) BEFORE
the encoder's question file was read. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint
change; nothing merges.

UNITS maps each in-scope unit n of batch4/posthog-leave/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2; other:no outcome = other:<named>, C4).
Items (one sort "item"): the team member m, absences a (one booked or taken time off, with its stated work days and first
day), years y (a calendar year a case asks about), parental leaves l, blocks b (a continuous block of a parental leave) and
quarters q (a calendar quarter with a stated quota attainment). Unary facts on items, binary facts in_year(a, y), of(a, m),
per-item integer constants. Every literal below (25, 4 types, 5 work days, 2 weeks, 3, 2, 3, 12, 24, 6 weeks, 6 and 12
months, 12 weeks, 100%, two quarters) is a literal of the pinned text; no number from a case is a coefficient.
Dates computed from dates (the day 4 months before a leave's first day; a quarter's first and last day; the prior two full
quarters) come ONLY from bridge/posthog_bridge.py (ledgered "bridged"); every comparison, sum, average and cap is written
here (AMOUNTS ARE NEVER BRIDGED).

Readings fixed here, on the text alone (refuse when in doubt; ISOLATION.md D1-D12 bind):
R1 NORMS. A duty, request or permission addressed to the team member ("you do not need to get approval", "please ...",
   "should", "you should avoid", "do not book", "make sure that", "just take them", "please speak to") is NOT written
   (other:norm): no question on what the member needs to, should or may do is answered from it. Written are the text's
   statements of fact about PostHog's arrangements: what is paid, offered or not offered, what happens automatically, how
   the types of time off are defined, the table, the deadline and the minimum as comparisons with the member's acts.
R2 TYPES (units 16-19): the four types are definitions; an absence fits Parental Leave when it is parental leave, Medical
   Leave when it is planned time off for the member personally on medical grounds, Out Sick when the member is sick and takes
   the time off unexpectedly, and PTO otherwise (vacation, any other time off, and time off to support a family member on
   medical grounds: "this is PTO"). A question "should <member> select <type>" is read as "does <type> fit this absence".
R3 MINIMUM (unit 1): "at least 25 days off a year, including national holidays": work days off in the calendar year the case
   names. PTO days and holidays taken off count; whether days off sick, on medical, parental or bereavement leave count is
   not settled by the text: the minimum is met when the PTO and holiday days alone reach 25, not met when all days off
   together stay under 25, otherwise no answer (refused).
R4 TABLE (units 37-39): time at PostHog is the stated whole months and days on the leave's first day; "under 6 months" =
   fewer than 6 whole months; "6 - 12 months" = from 6 months to 12 months and 0 days inclusive; "over 12 months" = more
   than 12 months (12 months and 1 day or more). The rows are exclusive under this reading (D4). A row gives (low, high)
   weeks: 3 weeks = (3, 3); "2 - 3 weeks" = (2, 3); "up to 24 weeks" = high 24 and no low ("up to"); answers render the
   range or the maximum, never a point inside (D3).
R5 MORE GENEROUS (unit 40): the member receives the local statutory paid parental leave instead of the policy when it is
   more generous: by a stated judgment, or when it is at full pay and longer than the row's high; the member receives the
   policy when a stated judgment says it is not more generous, when the case states no local statutory leave, or when the
   local weeks are no more than the row's low. Otherwise no answer. Never in addition; "top up" to full pay when the member
   receives any statutory leave.
R6 BLOCKS (unit 41): enhanced parental leave is paid in one continuous block: a leave's only block is paid; a block that is
   not the first of its leave is not; the first of several blocks: no answer. PostHog never pays it split.
R7 LOGGING (unit 43): "at least 4 months before it will begin": logged on or before the bridged day (the test's month
   convention); "as soon as you feel comfortable" is a stated judgment, not written.
R8 SICK PAY (unit 27): days of illness are paid while the member's days off sick in the same year, up to and including the
   absence, are no more than the contract's stated limit; over the limit they are not paid sick leave ("the upper limit
   for paid sick leave ... will be specified in your contract"; REVISION 11-25: was "no answer"); what the plan of unit 29
   then arranges is not written. Extended illness (unit 29): 5 or more work days, or a stated judgment.
R9 OTE (unit 45, under the "Maternity leave" heading, D2): applies to maternity leave of a quota-carrying Sales role taking 12
   weeks or longer, and not to maternity leave below 12 weeks or outside such a role; for paternity leave the text does not
   decide (refused). OTE = the average of the two calendar quarters' attainments in the prior two full quarters, capped at
   100%; exact only (D10: no rounding is written; an average that is not exact to the stated places is refused).
R10 UNPAID EXTENSION: maternity leave can be extended with unpaid time off (unit 44); paternity leave cannot (unit 46).
R11 BEREAVEMENT (units 31-32): the policy covers the loss of any person (closeness is not defined) and pregnancy and child
   loss for both parents; PostHog does not ask about the relationship; "at least 2 weeks of paid leave" is the amount asked
   for pregnancy and child loss (its reach to other losses is not settled: refused).
R12 BOOKING (units 11, 13, 14, 21, 22, 24): booked in the Time Off by Deel app in Slack -> automatically approved, added to
   the team time off calendar and the manager's personal calendar, Slack status set to out of office (except longer term
   leave, unit 13, which unit 23's "regardless of the holiday length" contradicts for approval and the calendars: longer term
   leave gets no answer there); the team calendar does not show it when the member has not authorised the app or not
   subscribed; booked directly on deel.com only -> the team will not know the member is out; PostHog does not book public
   holidays for the member; only admins can delete holidays; a message in #team-people-and-ops -> the team cancels it.
R13 STATED FACTS ABOUT THE POLICY AND THE MEMBER'S ACTS (REVISION 11-25, dri-b4-policy-translation-revise-1125, written from
   source.txt and the frozen run's refusal causes only; R1 narrowed, not dropped). R1 left unwritten some sentences that
   are not duties at all but statements of fact about the policy, and some acts the text names as the way to do a thing.
   Written now, each from its own sentence:
   - unit 2 "The 25 days is a minimum, not a guide": the policy does not describe the minimum as merely a guide;
   - unit 3 "taking significantly more vacation time than most - for example, 40 days": the text's example is 40 days a
     year; a year whose PTO and holiday days off reach 40 is, by the text's own example, significantly more than most
     (fewer than 40: no answer; "would be very surprised" stays no outcome, D9);
   - unit 4 "We care about your results, not how long you work": yes for every member;
   - unit 5 "You do not need to get approval for time off from your manager": no manager approval is needed (the
     expectation to coordinate and the request to avoid stay other:norm);
   - units 8-10 the two things to make sure of "before you start" (authorized the app; subscribed to the calendar): the
     member has done both exactly when both facts hold (the request itself stays other:norm);
   - unit 13 "Book it on the Time Off by Deel app in Slack": the member booked the way the text says exactly when they
     booked on the app; booked directly on deel.com only (unit 14) is not that way;
   - unit 22 "you can use the Bulk Add by Region feature": the member can use it;
   - unit 24 "drop a message in #team-people-and-ops": the member used the text's cancellation route exactly when they
     dropped that message;
   - unit 26 "you don't need to tell us" (an appointment, a school run, finishing early): the member does not need to;
   - unit 35 "we can often get an exception granted": an exception is not certain to be granted (no answer on whether one
     will be granted in a case).
   Not written still (R1): what the member must, should or may do as a duty or request.
R14 (revision 11-26) units 1, 27 and 29, read again from the source. Where the case leaves a condition unknown, no
   answer (refused).
   - unit 1 (R3): an absence whose days fall in more than one calendar year ("span", stated either way) counts in a year
     only its stated work days in that year (dy); an absence stated to lie in one year counts whole, as before; an absence
     whose spanning is not stated, or a spanning one without dy, leaves the year's sums unknown (no answer). "Not met"
     only for a calendar year the member is stated to be employed throughout (wholeyear): the text does not say how a
     part year counts. A booking the member asked to cancel (msgcancel, unit 24) is not counted.
   - unit 27 (R8): the text leaves the limit's period to the contract ("will be specified in your contract"). Paid while
     the days off sick of the absence's calendar year, up to and including it, are within the limit, when no earlier day
     off sick lies outside that year or the contract counts per calendar year (limcal): any other period counts no more
     days. Over the limit, and not paid when every day of the absence is over it, only when the contract counts per
     calendar year and the count is exact (every sick absence placed in a year and not spanning years). Crossing the
     limit partway: no answer on pay. The absence's own days always count.
   - unit 29: "extended periods of illness (5+ work days)" is measured on the period of illness: the absence's days plus
     those of every absence stated to be the same continuous period of illness (sameill, stated either way; unit 28 books
     a period in parts). Not extended only when that sum is known and under 5 and the case does not say the illness goes
     on beyond the booked days (ongoing).
"""
from __future__ import annotations

import hashlib
import json

DAY, WD, WK, MON, TDAY, PCT, QN, NT = ("day", "workday_count", "week_count", "month_count", "tenure_day", "percent",
                                        "quarter_count", "type_count")
INT_UNITS = {  # per-item integer constants: base -> (unit, words)
    # absences
    "days": (WD, "the stated number of work days of the absence"),
    "from": (DAY, "the first day of the absence"),
    "cum": (WD, "the member's work days off sick in the absence's year, up to and including the absence (sum)"),
    "bminwk": (WK, "the weeks of paid leave the policy asks the member to take at least after a pregnancy or child loss"),
    # years
    "mindays": (WD, "the days off a year the policy expects at least"),
    "vlo": (WD, "the year's work days off as PTO or holidays (sum)"),
    "vhi": (WD, "the year's work days off of every kind (sum)"),
    # members
    "limit": (WD, "the upper limit of paid sick leave a year in the member's contract (stated)"),
    "ntypes": (NT, "the number of types of time off the app offers"),
    # parental leaves
    "tm": (MON, "the member's whole months at PostHog on the leave's first day (stated)"),
    "td": (TDAY, "the days beyond those whole months (stated)"),
    "lo": (WK, "the table row's lowest weeks of paid parental leave"),
    "hi": (WK, "the table row's highest weeks of paid parental leave"),
    "lwk": (WK, "the weeks of paid parental leave the law of the member's country or state gives (stated)"),
    "wlo": (WK, "the lowest weeks of paid parental leave the member receives"),
    "whi": (WK, "the highest weeks of paid parental leave the member receives"),
    "start": (DAY, "the first day of the parental leave (stated)"),
    "logday": (DAY, "the day the member logged the parental leave in the Ops platform (stated)"),
    "dl": (DAY, "the day 4 months before the leave's first day (bridge)"),
    "latest": (DAY, "the latest day to log the leave at least 4 months before it begins"),
    "wtaken": (WK, "the weeks of maternity leave the member is taking (stated)"),
    "qwf": (DAY, "the first day of the prior two full quarters before the leave (bridge)"),
    "qwt": (DAY, "the last day of the prior two full quarters before the leave (bridge)"),
    "qsum": (PCT, "the sum of the quota attainments of the quarters inside that window"),
    "qcnt": (QN, "the number of stated quarters inside that window"),
    "avg": (PCT, "the average of those attainments"),
    "ote": (PCT, "the percentage of OTE at which the member's OTE is calculated"),
    # quarters
    "att": (PCT, "the member's sales quota attainment for the quarter (stated)"),
    "qfrom": (DAY, "the quarter's first day (bridge)"),
    "qto": (DAY, "the quarter's last day (bridge)"),
}
PAIR_UNITS = {  # per (item, item) constants: base -> (unit, words)
    "slo": (WD, "(absence, year) the absence's work days counted as PTO or holiday in the year"),
    "shi": (WD, "(absence, year) the absence's work days counted in the year"),
    "sc": (WD, "(absence b, absence a) b's work days off sick counted for a"),
    "qs": (PCT, "(quarter, leave) the quarter's attainment counted for the leave"),
    "qc": (QN, "(quarter, leave) the quarter counted (1) or not (0) for the leave"),
    # R14 (revision 11-26)
    "dy": (WD, "(absence, year) the absence's work days that fall in the year (stated)"),
    "sd": (WD, "(absence b, absence a) b's work days counted in a's period of illness"),
}
INT_UNITS["pd"] = (WD, "the work days of the absence's period of illness: its own days and those of every absence stated "
                       "to be the same continuous period of illness (sum)")  # R14
FACTS = {  # unary facts (the encoder states each true or false)
    "member": "the item is a PostHog team member (the fixed fact of the test)",
    "admin": "the member is an admin of the time off system",
    # absences
    "vac": "the absence is PTO (vacation or other time off of type PTO) or a national or public holiday taken off",
    "ill": "the member is sick on the absence's days",
    "unexpected": "the member takes the absence unexpectedly",
    "medself": "the absence is planned time off for the member personally, on medical grounds",
    "parental": "the absence is parental leave",
    "app": "the member booked the absence on the Time Off by Deel app in Slack",
    "deelonly": "the member booked the absence directly on deel.com and not on the Time Off by Deel app in Slack",
    "auth": "the member has authorized the Time Off by Deel app in Slack to connect to their Google Calendar",
    "subs": "the member has subscribed to the team time off calendar",
    "longterm": "the absence is longer term leave (encoder judgement where the case does not say)",
    "holiday": "the absence is a public or national holiday the member takes off",
    "msgcancel": "the member dropped a message in #team-people-and-ops to cancel the booked absence",
    "bereaved": "the absence follows the death of a person",
    "pcloss": "the absence follows a pregnancy loss or the loss of a child, for either parent",
    "healthneed": "the member needs extended time for physical or mental health reasons (stated judgment)",
    "extjudged": "the period of illness is extended (stated judgment other than by the 5 work days)",
    # parental leaves
    "maternity": "the leave is maternity leave (the stated kind)",
    "paternity": "the leave is paternity leave (the stated kind)",
    "haslocal": "the case states the paid parental leave the law of the member's country or state gives",
    "localfull": "that local statutory leave is at full pay",
    "judgedmore": "the local statutory parental leave is more generous than the PostHog policy (stated judgment)",
    "judgedless": "the local statutory parental leave is not more generous than the PostHog policy (stated judgment)",
    "statrecv": "the member receives statutory leave (pay) during the parental leave",
    "sales": "the member is in a quota-carrying Sales role",
    "decallow": "PostHog decided to allow the member's combination of parental leave and a long holiday (stated)",
    "decrefuse": "PostHog decided not to allow the member's combination of parental leave and a long holiday (stated)",
    # blocks
    "sole": "the block is the only block of its parental leave (one continuous block)",
    "later": "the block is not the first block of its parental leave",
    # members, R14 (revision 11-26)
    "limcal": "the member's contract states that its limit of paid sick leave counts per calendar year",
    # years, R14
    "wholeyear": "the member is employed by PostHog throughout the calendar year (stated)",
    # absences, R14
    "ongoing": "the case states that the illness goes on beyond the absence's booked days",
}
BINARY = {
    "in_year": "(absence, year) the absence's days fall in the calendar year (all of them, or some of them for an "
               "absence that spans years)",
    "of": "(absence, member) the absence is the member's",
}
# R14 (revision 11-26): facts NOT closed-world (C1 does not apply): stated true, stated false, or unknown (no fact).
OPEN_UNARY = {
    "span": "(absence) the absence's days fall in more than one calendar year (stated either way)",
}
OPEN_BINARY = {
    "sameill": "(absence, absence) the two absences are bookings of one continuous period of illness (stated either way)",
}
STATED = ("healthneed", "extjudged", "judgedmore", "judgedless", "decallow", "decrefuse")
BRIDGED_CONSTS = ("dl", "qwf", "qwt", "qfrom", "qto")
DERIVED_UNARY = {
    "met": "(year) the member has taken the minimum days off the policy expects for the year (unit 1)",
    "fitpto": "(absence) PTO is the type of time off that fits the absence (units 16, 19)",
    "fitsick": "(absence) Out Sick is the type that fits the absence (unit 17)",
    "fitparental": "(absence) Parental Leave is the type that fits the absence (unit 18)",
    "fitmedical": "(absence) Medical Leave is the type that fits the absence (unit 19)",
    "autook": "(absence) the absence is automatically approved (unit 13)",
    "incal": "(absence) the absence shows up in the team time off calendar (units 11, 13)",
    "mgrcal": "(absence) the absence is added to the manager's personal calendar (unit 13)",
    "teamknows": "(absence) the team will know the member is out (unit 14)",
    "slackooo": "(absence) the app sets the member's Slack status to out of office and autoresponds (unit 21)",
    "phbooks": "(absence) PostHog books the public holiday in on the member's behalf (unit 22)",
    "candelete": "(member) the member can delete a holiday (unit 24)",
    "cancelled": "(absence) a member of the People & Ops team will cancel the holiday for the member (unit 24)",
    "countshours": "(member) PostHog counts the member's hours or days worked (unit 25)",
    "paidsick": "(absence) the member is paid for the days of illness (unit 27)",
    "overlimit": "(absence) the member is going over the limit of paid sick leave (unit 29)",
    "extended": "(absence) the absence is an extended period of illness (unit 29)",
    "covered": "(absence) the bereavement policy covers the absence (units 31, 32)",
    "asksrel": "(absence) PostHog asks about the member's relationship to the person (unit 31)",
    "treatedext": "(absence) PostHog treats the time as extended sick leave (unit 33)",
    "canparental": "(member) the member is able to take parental leave (unit 36)",
    "rowu6": "(leave) the table row 'under 6 months' applies",
    "row612": "(leave) the table row '6 - 12 months' applies",
    "rowo12": "(leave) the table row 'over 12 months' applies",
    "upto": "(leave) the row gives only a maximum ('up to')",
    "genmore": "(leave) the local statutory parental leave is more generous (unit 40)",
    "gennot": "(leave) the local statutory parental leave is not more generous, or none is stated (unit 40)",
    "recvph": "(leave) the member receives the PostHog policy's parental leave (unit 40)",
    "recvlocal": "(leave) the member receives the local statutory parental leave instead (unit 40)",
    "wupto": "(leave) the weeks the member receives are given only as a maximum",
    "inaddition": "(leave) the PostHog policy is given in addition to the statutory policy (unit 40)",
    "topup": "(leave) PostHog tops the statutory leave pay up to the member's full pay (unit 40)",
    "paidblock": "(block) PostHog pays the enhanced parental leave for the block (unit 41)",
    "payssplit": "(leave) PostHog pays the enhanced parental leave split over more than one block (unit 41)",
    "allowed": "(leave) PostHog allows the combination of parental leave and a long holiday (unit 42)",
    "loggedok": "(leave) the member logged the leave in the Ops platform at least 4 months before it begins (unit 43)",
    "unpaidext": "(leave) the leave can be extended using unpaid time off (units 44, 46)",
    "oteapplies": "(leave) the member's OTE is calculated by averaging the prior two full quarters (unit 45)",
}
DERIVED_BINARY = {
    "inwin": "(quarter, leave) the quarter is one of the prior two full quarters before the leave",
}
DERIVED_UNARY.update({  # REVISION 11-25 (R13)
    "minguide": "(member) the policy describes its 25-day minimum as merely a guide (unit 2)",
    "sigmore": "(year) the member's PTO and holiday days off in the year reach the policy's own example of significantly "
               "more vacation time than most, 40 days (unit 3)",
    "results": "(member) PostHog cares about the member's results, not how long they work (unit 4)",
    "mgrappr": "(member) the member needs approval for time off from their manager (unit 5)",
    "setupdone": "(absence) the member has done both things the text lists before booking: authorized the Time Off by Deel "
                 "app to connect to their Google Calendar and subscribed to the team time off calendar (units 8-10)",
    "viaapp": "(absence) the member booked the absence the way the text says to book a day off: on the Time Off by Deel "
              "app in Slack (unit 13)",
    "bulkadd": "(member) the member can use the app's Bulk Add by Region feature to identify and add public holidays "
               "(unit 22)",
    "cancelroute": "(absence) the member asked to cancel the holiday by the route the text gives: a message in "
                   "#team-people-and-ops (unit 24)",
    "musttell": "(member) the member needs to tell PostHog about time away for an appointment, a school run or finishing "
                "early (unit 26)",
    "excsure": "(member) an exception from jury duty is certain to be granted (unit 35)",
})
INT_UNITS["exdays"] = (WD, "the days off a year the policy gives as its example of significantly more vacation time than "
                           "most (unit 3)")


# --- formula helpers (the ve-quantity@1 wire shapes; fmla_eligibility / oas_canada conventions) --------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def lit(tag, v): return ["decimal", tag, v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
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


def k(base, x):
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kp(base, x, y):
    return ["const", PAIR_UNITS[base][0], f"{base}_{x}_{y}"]


def total(tag, terms):
    if not terms:
        return lit(tag, "0")
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = add(tag, t, r)
    return r


def iff_u(p, x, body): return Iff(U(p, x), body)


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, members=(), absences=(), years=(), leaves=(), blocks=(), quarters=()):
        self.members, self.absences, self.years = list(members), list(absences), list(years)
        self.leaves, self.blocks, self.quarters = list(leaves), list(blocks), list(quarters)

    @property
    def items(self):
        return self.members + self.absences + self.years + self.leaves + self.blocks + self.quarters


def per(kind, fn):
    return lambda ctx: [f for x in getattr(ctx, kind) for f in fn(x, ctx)]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


# --- the units ----------------------------------------------------------------------------------------------------

def _u1_head(y, ctx):
    return [Eq(k("mindays", y), lit(WD, "25")),
            Eq(k("vlo", y), total(WD, [kp("slo", a, y) for a in ctx.absences])),
            Eq(k("vhi", y), total(WD, [kp("shi", a, y) for a in ctx.absences])),
            Implies(Le(k("mindays", y), k("vlo", y)), U("met", y)),
            Implies(Lt(k("vhi", y), k("mindays", y)), Not(U("met", y)))]


def _u1_head14(y, ctx):
    """R14: 'not met' only for a calendar year the member is employed throughout (the text does not say how a part year
    counts)."""
    return [Eq(k("mindays", y), lit(WD, "25")),
            Eq(k("vlo", y), total(WD, [kp("slo", a, y) for a in ctx.absences])),
            Eq(k("vhi", y), total(WD, [kp("shi", a, y) for a in ctx.absences])),
            Implies(Le(k("mindays", y), k("vlo", y)), U("met", y)),
            Implies(And(U("wholeyear", y), Lt(k("vhi", y), k("mindays", y))), Not(U("met", y)))]


def _u1_pre14(y, ctx):
    """Unit 1 as written before R14 (planted error M19): an absence counted whole in every year it is in."""
    out = _u1_head(y, ctx)
    for a in ctx.absences:
        iy = B("in_year", a, y)
        out += [Implies(And(iy, U("vac", a)), Eq(kp("slo", a, y), k("days", a))),
                Implies(Or(Not(iy), Not(U("vac", a))), Eq(kp("slo", a, y), lit(WD, "0"))),
                Implies(iy, Eq(kp("shi", a, y), k("days", a))),
                Implies(Not(iy), Eq(kp("shi", a, y), lit(WD, "0")))]
    return out


def _u1(y, ctx):
    """Unit 1 with R3 and R14: at least 25 days off a year, including national holidays. An absence counts whole in a
    year only when it is stated to lie in one calendar year; one that spans years counts its stated days in the year (dy);
    spanning unstated (or dy unstated) -> the year's sums are unknown. Not met only for a whole year of employment."""
    out = _u1_head14(y, ctx)
    for a in ctx.absences:
        sp, v = U("span", a), U("vac", a)
        iy = And(B("in_year", a, y), Not(U("msgcancel", a)))  # R14: a booking asked to be cancelled is not time off
        out += [Implies(And(iy, Not(sp), v), Eq(kp("slo", a, y), k("days", a))),
                Implies(And(iy, sp, v), Eq(kp("slo", a, y), kp("dy", a, y))),
                Implies(Or(Not(iy), Not(v)), Eq(kp("slo", a, y), lit(WD, "0"))),
                Implies(And(iy, Not(sp)), Eq(kp("shi", a, y), k("days", a))),
                Implies(And(iy, sp), Eq(kp("shi", a, y), kp("dy", a, y))),
                Implies(Not(iy), Eq(kp("shi", a, y), lit(WD, "0")))]
    return out


def _u11_13(a, ctx):
    """Units 11, 13 with R12: the app's automatic effects; the calendar not shown without the two prerequisites."""
    app, lt = U("app", a), U("longterm", a)
    return [Implies(And(app, Not(lt)), U("autook", a)),
            Implies(And(app, Not(lt), U("auth", a), U("subs", a)), U("incal", a)),
            Implies(Or(Not(U("auth", a)), Not(U("subs", a))), Not(U("incal", a))),
            Implies(And(app, Not(lt)), U("mgrcal", a))]


def _u14(a, ctx):
    """Unit 14: booked directly on deel.com: the team will not know you are out."""
    return [Implies(U("deelonly", a), Not(U("teamknows", a)))]


def _u15(m, ctx):
    """Unit 15: four types of time off you can select."""
    return [Implies(U("member", m), Eq(k("ntypes", m), lit(NT, "4")))]


def _u16_19(a, ctx):
    """Units 16-19 with R2: the four types as definitions."""
    par, med, sick = U("parental", a), U("medself", a), And(U("ill", a), U("unexpected", a))
    return [iff_u("fitparental", a, par),
            iff_u("fitmedical", a, And(med, Not(par))),
            iff_u("fitsick", a, And(sick, Not(med), Not(par))),
            iff_u("fitpto", a, And(Not(par), Not(med), Not(sick)))]


def _u21(a, ctx):
    """Unit 21: the app sets the Slack status to out of office and autoresponds."""
    return [Implies(U("app", a), U("slackooo", a))]


def _u22(a, ctx):
    """Unit 22: not practical for PostHog to book public holidays on the member's behalf."""
    return [Implies(U("holiday", a), Not(U("phbooks", a)))]


def _u24m(m, ctx):
    """Unit 24: only admins can delete holidays."""
    return [Implies(Not(U("admin", m)), Not(U("candelete", m)))]


def _u24a(a, ctx):
    """Unit 24: a message in #team-people-and-ops and a member of the team will cancel the holiday for you."""
    return [Implies(U("msgcancel", a), U("cancelled", a))]


def _u25(m, ctx):
    """Unit 25: we don't count hours or days worked."""
    return [Implies(U("member", m), Not(U("countshours", m)))]


def _same_year(b, a, ctx):
    return Or(*[And(B("in_year", b, y), B("in_year", a, y)) for y in ctx.years])


def _u27_cum(a, ctx):
    out = [Eq(k("cum", a), total(WD, [kp("sc", b, a) for b in ctx.absences]))]
    for b in ctx.absences:
        same = _same_year(b, a, ctx)
        cond = And(U("ill", b), same, no_later(k("from", b), k("from", a)))
        out += [Implies(cond, Eq(kp("sc", b, a), k("days", b))),
                Implies(Or(Not(U("ill", b)), Not(same), before(k("from", a), k("from", b))),
                        Eq(kp("sc", b, a), lit(WD, "0")))]
    return out


def _u27_pre14(a, ctx):
    """Unit 27 as written before R14 (planted error M20): the whole absence unpaid once cum passes the limit; the
    calendar year as the limit's period."""
    out = _u27_cum(a, ctx)
    for m in ctx.members:
        mine = And(B("of", a, m), U("ill", a))
        out += [Implies(And(mine, Le(k("cum", a), k("limit", m))), U("paidsick", a)),
                Implies(And(mine, Lt(k("limit", m), k("cum", a))), U("overlimit", a)),
                Implies(And(mine, Lt(k("limit", m), k("cum", a))), Not(U("paidsick", a))),  # R8 (revision 11-25)
                Implies(And(mine, Le(k("cum", a), k("limit", m))), Not(U("overlimit", a)))]
    return out


def _placed(x, ctx):
    return Or(*[B("in_year", x, y) for y in ctx.years])


def _u27_cum14(a, ctx):
    """R14: the absence's own days always count; an earlier absence's days count when it is in the same year item."""
    out = [Eq(k("cum", a), total(WD, [kp("sc", b, a) for b in ctx.absences])),
           Implies(U("ill", a), Eq(kp("sc", a, a), k("days", a))),
           Implies(Not(U("ill", a)), Eq(kp("sc", a, a), lit(WD, "0")))]
    for b in ctx.absences:
        if b == a:
            continue
        same = _same_year(b, a, ctx)
        cond = And(U("ill", b), same, no_later(k("from", b), k("from", a)))
        out += [Implies(cond, Eq(kp("sc", b, a), k("days", b))),
                Implies(Or(Not(U("ill", b)), Not(same), before(k("from", a), k("from", b))),
                        Eq(kp("sc", b, a), lit(WD, "0")))]
    return out


def _u27(a, ctx):
    """Unit 27 with R8 and R14. The text leaves the limit's period to the contract. cum counts the days off sick of the
    absence's calendar year up to and including it.
    PAID (and not over the limit) when cum is within the limit and either no earlier day off sick lies outside that
    calendar year, or the contract counts per calendar year (limcal) and every earlier sick absence is placed in a year:
    any other period counts no more days than cum.
    OVER THE LIMIT, and NOT PAID when every day of the absence is over it (cum >= limit + days), only when the contract
    counts per calendar year and cum is exact: the absence and every earlier sick absence placed in a year item and stated
    not to span years. Otherwise no answer; crossing the limit partway: no answer on pay."""
    out = _u27_cum14(a, ctx)
    others = [b for b in ctx.absences if b != a]
    early = {b: And(U("ill", b), no_later(k("from", b), k("from", a))) for b in others}
    cross = Or(*[And(early[b], Not(_same_year(b, a, ctx))) for b in others])
    placed = And(_placed(a, ctx), *[Or(Not(early[b]), _placed(b, ctx)) for b in others])
    exact = And(placed, Not(U("span", a)), *[Or(Not(early[b]), Not(U("span", b))) for b in others])
    for m in ctx.members:
        mine, cal = And(B("of", a, m), U("ill", a)), U("limcal", m)
        within = Le(k("cum", a), k("limit", m))
        okpaid = Or(Not(cross), And(cal, placed))
        out += [Implies(And(mine, okpaid, within), U("paidsick", a)),
                Implies(And(mine, cal, exact, Lt(k("limit", m), k("cum", a))), U("overlimit", a)),
                Implies(And(mine, cal, exact, Le(add(WD, k("limit", m), k("days", a)), k("cum", a))),
                        Not(U("paidsick", a))),  # R8 (revision 11-25), R14: every day over the limit
                Implies(And(mine, okpaid, within), Not(U("overlimit", a)))]
    return out


def _u29_pre14(a, ctx):
    """Unit 29 as written before R14 (planted error M21): measured on the one booked absence."""
    ill, d = U("ill", a), k("days", a)
    return [Implies(And(ill, Le(lit(WD, "5"), d)), U("extended", a)),
            Implies(U("extjudged", a), U("extended", a)),
            Implies(And(ill, Lt(d, lit(WD, "5")), Not(U("extjudged", a))), Not(U("extended", a)))]


def _u29(a, ctx):
    """Unit 29 with R14: extended periods of illness (5+ work days), measured on the period of illness (pd): the
    absence's days plus those of every absence stated to be the same continuous period of illness (sameill); a sick
    absence whose link to this one is not stated leaves pd unknown (not extended: no answer); an illness stated to go on
    beyond the booked days (ongoing): not extended gets no answer."""
    ill, d, pd = U("ill", a), k("days", a), k("pd", a)
    others = [b for b in ctx.absences if b != a]
    out = [Eq(pd, total(WD, [d] + [kp("sd", b, a) for b in others]))]
    for b in others:
        s = B("sameill", b, a)
        out += [Implies(And(U("ill", b), s), Eq(kp("sd", b, a), k("days", b))),
                Implies(Or(Not(U("ill", b)), Not(s)), Eq(kp("sd", b, a), lit(WD, "0")))]
    return out + [Implies(And(ill, Le(lit(WD, "5"), d)), U("extended", a)),
                  Implies(And(ill, Le(lit(WD, "5"), pd)), U("extended", a)),
                  Implies(U("extjudged", a), U("extended", a)),
                  Implies(And(ill, Lt(pd, lit(WD, "5")), Not(U("extjudged", a)), Not(U("ongoing", a))),
                          Not(U("extended", a)))]


def _u31_32(a, ctx):
    """Units 31, 32 with R11."""
    loss = Or(U("bereaved", a), U("pcloss", a))
    return [iff_u("covered", a, loss),
            Implies(loss, Not(U("asksrel", a))),
            Implies(U("pcloss", a), Eq(k("bminwk", a), lit(WK, "2")))]


def _u33(a, ctx):
    """Unit 33: extended time for physical or mental health reasons after a loss: treated as extended sick leave."""
    return [Implies(And(U("healthneed", a), Or(U("bereaved", a), U("pcloss", a))), U("treatedext", a))]


def _u36(m, ctx):
    """Unit 36: anyone at PostHog, regardless of gender, childbirth or adoption, is able to take parental leave."""
    return [Implies(U("member", m), U("canparental", m))]


def _rows(l, ctx):
    """Units 37-39 with R4: the row by time at PostHog (whole months and days)."""
    tm, td = k("tm", l), k("td", l)
    m6, m12, d0 = lit(MON, "6"), lit(MON, "12"), lit(TDAY, "0")
    return [iff_u("rowu6", l, Lt(tm, m6)),
            iff_u("row612", l, And(Le(m6, tm), Or(Lt(tm, m12), And(Eq(tm, m12), Eq(td, d0))))),
            iff_u("rowo12", l, Or(Lt(m12, tm), And(Eq(tm, m12), Lt(d0, td))))]


def _cell(l, row, kind, low, high):
    g = And(U(row, l), U(kind, l))
    out = [Implies(g, Eq(k("hi", l), lit(WK, high)))]
    if low is not None:
        out.append(Implies(g, Eq(k("lo", l), lit(WK, low))))
    return out


def _u37(l, ctx):
    return _cell(l, "rowu6", "maternity", "3", "3") + _cell(l, "rowu6", "paternity", "2", "3")


def _u38(l, ctx):
    return _cell(l, "row612", "maternity", "12", "12") + _cell(l, "row612", "paternity", "2", "3")


def _u39(l, ctx):
    return (_cell(l, "rowo12", "maternity", None, "24") + _cell(l, "rowo12", "paternity", "6", "6")
            + [iff_u("upto", l, And(U("rowo12", l), U("maternity", l)))])


def _u40(l, ctx):
    """Unit 40 with R5."""
    lw, hl = k("lwk", l), U("haslocal", l)
    return [Implies(U("judgedmore", l), U("genmore", l)),
            Implies(And(hl, U("localfull", l), Lt(k("hi", l), lw)), U("genmore", l)),
            Implies(U("judgedless", l), U("gennot", l)),
            Implies(Not(hl), U("gennot", l)),
            Implies(And(hl, Le(lw, k("lo", l))), U("gennot", l)),
            Implies(U("gennot", l), U("recvph", l)), Implies(U("genmore", l), Not(U("recvph", l))),
            Implies(U("genmore", l), U("recvlocal", l)), Implies(U("gennot", l), Not(U("recvlocal", l))),
            Implies(U("gennot", l), Eq(k("wlo", l), k("lo", l))), Implies(U("gennot", l), Eq(k("whi", l), k("hi", l))),
            Implies(U("genmore", l), Eq(k("wlo", l), lw)), Implies(U("genmore", l), Eq(k("whi", l), lw)),
            Implies(And(U("gennot", l), U("upto", l)), U("wupto", l)),
            Implies(Or(U("genmore", l), Not(U("upto", l))), Not(U("wupto", l))),
            Implies(hl, Not(U("inaddition", l))),
            Implies(U("statrecv", l), U("topup", l))]


def _u41b(b, ctx):
    """Unit 41 with R6 (blocks)."""
    return [Implies(U("sole", b), U("paidblock", b)), Implies(U("later", b), Not(U("paidblock", b)))]


def _u41l(l, ctx):
    return [Implies(Or(U("maternity", l), U("paternity", l)), Not(U("payssplit", l)))]


def _u42(l, ctx):
    """Unit 42: 'usually won't allow' (no definite outcome): only PostHog's stated decision."""
    return [Implies(U("decallow", l), U("allowed", l)), Implies(U("decrefuse", l), Not(U("allowed", l)))]


def _u43(l, ctx):
    """Unit 43 with R7: at least 4 months before it will begin (the day from the bridge)."""
    return [Eq(k("latest", l), k("dl", l)),
            iff_u("loggedok", l, no_later(k("logday", l), k("latest", l)))]


def _u44(l, ctx):
    return [Implies(U("maternity", l), U("unpaidext", l))]


def _u46(l, ctx):
    return [Implies(U("paternity", l), Not(U("unpaidext", l)))]


def _u45(l, ctx):
    """Unit 45 with R9: OTE by averaging the prior two full quarters, capped at 100%."""
    mat, sales, wk = U("maternity", l), U("sales", l), k("wtaken", l)
    w12 = lit(WK, "12")
    app_ = U("oteapplies", l)
    two = Eq(k("qcnt", l), lit(QN, "2"))
    hundred = lit(PCT, "100")
    out = [Implies(And(mat, sales, Le(w12, wk)), app_),
           Implies(And(mat, Or(Not(sales), Lt(wk, w12))), Not(app_)),
           Eq(k("qsum", l), total(PCT, [kp("qs", q, l) for q in ctx.quarters])),
           Eq(k("qcnt", l), total(QN, [kp("qc", q, l) for q in ctx.quarters])),
           Implies(And(app_, two), Eq(scale(PCT, 2, k("avg", l)), k("qsum", l))),
           Implies(And(app_, two, Le(k("avg", l), hundred)), Eq(k("ote", l), k("avg", l))),
           Implies(And(app_, two, Lt(hundred, k("avg", l))), Eq(k("ote", l), hundred))]
    for q in ctx.quarters:
        inw = B("inwin", q, l)
        out += [Iff(inw, And(no_later(k("qwf", l), k("qfrom", q)), no_later(k("qto", q), k("qwt", l)))),
                Implies(inw, Eq(kp("qs", q, l), k("att", q))), Implies(Not(inw), Eq(kp("qs", q, l), lit(PCT, "0"))),
                Implies(inw, Eq(kp("qc", q, l), lit(QN, "1"))), Implies(Not(inw), Eq(kp("qc", q, l), lit(QN, "0")))]
    return out


# --- REVISION 11-25 (R13): stated facts R1 had left unwritten -------------------------------------------------------

def _r13_member(m, ctx):
    """Units 2, 3, 4, 5, 22, 26, 35 (R13): statements of fact about the policy, one per member."""
    mem = U("member", m)
    return [Implies(mem, Not(U("minguide", m))),                 # unit 2 "a minimum, not a guide"
            Implies(mem, Eq(k("exdays", m), lit(WD, "40"))),     # unit 3 "for example, 40 days"
            Implies(mem, U("results", m)),                       # unit 4 "We care about your results"
            Implies(mem, Not(U("mgrappr", m))),                  # unit 5 "You do not need to get approval"
            Implies(mem, U("bulkadd", m)),                       # unit 22 "you can use the Bulk Add by Region feature"
            Implies(mem, Not(U("musttell", m))),                 # unit 26 "you don't need to tell us"
            Implies(mem, Not(U("excsure", m)))]                  # unit 35 "we can often get an exception granted"


def _r13_year(y, ctx):
    """Unit 3 (R13): a year at or above the text's 40-day example (PTO and holidays, unit 1's vlo)."""
    return [Implies(Le(lit(WD, "40"), k("vlo", y)), U("sigmore", y))]


def _r13_absence(a, ctx):
    """Units 8-10, 13-14, 24 (R13): the member's acts measured against the steps the text names."""
    return [iff_u("setupdone", a, And(U("auth", a), U("subs", a))),
            iff_u("viaapp", a, U("app", a)),
            Implies(U("deelonly", a), Not(U("viaapp", a))),
            iff_u("cancelroute", a, U("msgcancel", a))]


def _none(ctx):
    return []


NORM, NOOUT, JUDG = "other:norm", "other:no outcome", "other:judgment standard"
UNITS = {
    1: ("RULE", per("years", _u1), "R3: 25 work days a year; PTO and holidays count, other days off only bound the "
                                    "answer (two readings otherwise: refused); R14: an absence spanning years "
                                    "counts its stated days in the year"),
    2: ("PART", per("members", _r13_member), NOOUT, "R13 (rev 11-25): 'The 25 days is a minimum, not a guide' WRITTEN "
                                                   "(with units 3, 4, 5, 22, 26, 35 in one builder); purpose and 'will "
                                                   "look into holiday usage occasionally to encourage': no outcome"),
    3: ("PART", per("years", _r13_year), NOOUT, "R13 (rev 11-25): the 40-day example WRITTEN (a year at 40 or more PTO and "
                                               "holiday days is significantly more than most); 'we would be very "
                                               "surprised' no outcome (D9)"),
    4: ("RULE", _none, "R13 (rev 11-25): 'We care about your results, not how long you work.' (unit 2's builder)"),
    5: ("PART", _none, NORM, "R13 (rev 11-25): 'You do not need to get approval for time off from your manager' WRITTEN "
                             "(unit 2's builder); 'we expect everyone to coordinate ... You should avoid': an expectation "
                             "and a request (R1)"),
    6: ("NOT", None, NORM, "'You should avoid ... an entire Small Team off': a request (R1)"),
    7: ("NOT", None, NORM, "'should avoid ... the only X people ... try to make sure one of you can check in'; "
                           "'unavoidable' a judgment (R1)"),
    8: ("NOT", None, NORM, "'Before you start, make sure that:' (R1)"),
    9: ("PART", per("absences", _r13_absence), NORM, "R13 (rev 11-25): the two steps as a definition WRITTEN (setupdone; "
                                                    "with units 10, 13, 14, 24 in one builder); 'make sure that' (R1) "
                                                    "not; its consequence is unit 11"),
    10: ("PART", _none, NORM, "R13 (rev 11-25): unit 9's builder; 'make sure that you have subscribed' (R1) not"),
    11: ("RULE", per("absences", _u11_13), "not authorised or not subscribed -> not shown in the team calendar"),
    12: ("NOT", None, NORM, "'To book a day off:' (lead-in of a procedure)"),
    13: ("PART", _none, NORM, "'Book it on the app' (a request) NOT written; 'automatically approved and added to the team "
                              "time off calendar ... added to your manager's personal calendar' WRITTEN (unit 11's "
                              "builder, R12), except longer term leave, which unit 23 contradicts (no answer); 'longer "
                              "term leave' is not defined (an encoder judgement fact)"),
    14: ("PART", per("absences", _u14), NORM, "'Do not book directly on deel.com' (a prohibition) NOT written; 'the team "
                                              "will not know you are out' WRITTEN"),
    15: ("RULE", per("members", _u15), "four types of time off"),
    16: ("RULE", per("absences", _u16_19), "R2: PTO, the residual type (units 16-19 in one builder)"),
    17: ("RULE", _none, "R2: Out Sick (unit 16's builder)"),
    18: ("RULE", _none, "R2: Parental Leave (unit 16's builder)"),
    19: ("RULE", _none, "R2: Medical Leave; a family member's medical need is PTO (unit 16's builder)"),
    20: ("NOT", None, NORM, "'Block out your own personal GCal' (a request); 'might still get booked' no outcome"),
    21: ("PART", per("absences", _u21), NORM, "'Set an out of office message' (a request) NOT written; the app's Slack "
                                              "status and autoresponse WRITTEN"),
    22: ("PART", per("absences", _u22), NORM, "'Please manually book in public holidays' NOT written; PostHog does not "
                                              "book them on your behalf WRITTEN; 'you can use the Bulk Add by Region "
                                              "feature' WRITTEN (R13, rev 11-25, unit 2's builder)"),
    23: ("NOT", None, NORM, "'The same rules as above apply regardless of the holiday length and type ... should also be "
                            "booked in the same way': booking requests; its clash with unit 13's exception refuses "
                            "longer term leave there (R12)"),
    24: ("RULE", _cat(per("members", _u24m), per("absences", _u24a)), "only admins can delete; the team cancels on a "
                                                                      "message (the 'drop a message' request is the "
                                                                      "condition)"),
    25: ("RULE", per("members", _u25), "PostHog does not count hours or days worked"),
    26: ("PART", _none, NORM, "R13 (rev 11-25): 'you don't need to tell us' WRITTEN (unit 2's builder); 'Please just add "
                              "it to your calendar ... make sure you have cover': requests (R1)"),
    27: ("PART", per("absences", _u27), "cross-reference", "R8: paid within the contract's limit (the contract, outside "
                                                            "the text, a stated number; R14: crossing the limit partway "
                                                            "and an unstated limit period across years refused); 'you "
                                                            "don't need to work', 'just "
                                                            "take them' NOT written (R1)"),
    28: ("NOT", None, NORM, "'Please let your manager know ... add it to Time Off by Deel. You shouldn't pre-emptively book "
                            "...': requests; 'may trigger the need for a doctor's note' no outcome"),
    29: ("PART", per("absences", _u29), NORM, "extended illness (5+ work days, R14: on the period of "
                                              "illness) and going over the limit WRITTEN; 'please "
                                              "speak to [People & Ops]' NOT written; 'In most countries, we will need a "
                                              "doctor's note' no outcome"),
    30: ("NOT", None, NORM, "'please let [People & Ops] know': a request"),
    31: ("PART", per("absences", _u31_32), NORM, "R11: closeness not defined (any person's loss covered) and 'we won't "
                                                "ask about your relationship' WRITTEN; 'Please just let us know up front' "
                                                "NOT written"),
    32: ("PART", _none, NORM, "R11 (unit 31's builder): pregnancy and child loss covered for both parents; 2 weeks of "
                              "paid leave the amount asked; 'Please take' (a request) itself not written"),
    33: ("PART", per("absences", _u33), JUDG, "'for physical or mental health reasons' a stated judgment; 'just chat to' "
                                              "NOT written"),
    34: ("NOT", None, NORM, "'Please let it - just be communicative ... We trust you': requests"),
    35: ("PART", _none, NORM, "'please let [People & Ops] know right away' (a request) NOT written; 'we can often get an "
                              "exception': not certain WRITTEN (R13, rev 11-25, unit 2's builder); whether one is granted "
                              "in a case: no outcome (D9)"),
    36: ("RULE", per("members", _u36), "anyone able to take parental leave, regardless of gender, childbirth or adoption"),
    37: ("RULE", _cat(per("leaves", _rows), per("leaves", _u37)), "R4: row 'under 6 months': 3 weeks / 2 - 3 weeks"),
    38: ("RULE", per("leaves", _u38), "R4: row '6 - 12 months': 12 weeks / 2 - 3 weeks"),
    39: ("RULE", per("leaves", _u39), "R4: row 'over 12 months': up to 24 weeks / 6 weeks"),
    40: ("PART", per("leaves", _u40), JUDG, "R5: 'more generous' by the numbers or a stated judgment; 'in most cases' "
                                            "descriptive; local law (outside the text) stated"),
    41: ("RULE", _cat(per("blocks", _u41b), per("leaves", _u41l)), "R6: one continuous block"),
    42: ("PART", per("leaves", _u42), NOOUT, "'usually won't allow' (D9): only PostHog's stated decision; 'log it in the "
                                             "Ops platform or speak to your manager' a request, NOT written"),
    43: ("PART", per("leaves", _u43), "deadline/time limit", "R7: at least 4 months before it begins WRITTEN (the day "
                                                             "BRIDGED); 'as soon as you feel comfortable' a judgment; "
                                                             "the People & Ops follow-up descriptive"),
    44: ("PART", per("leaves", _u44), NORM, "R10: maternity leave can be extended with unpaid time off WRITTEN; 'please "
                                            "work with your team ... log the total' NOT written"),
    45: ("RULE", per("leaves", _u45), "R9: OTE averaged over the prior two full quarters (window BRIDGED), capped at 100%"),
    46: ("RULE", per("leaves", _u46), "R10: no unpaid leave for paternity leave"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    out = []
    for n, e in sorted(units_table(mutant).items()):
        if e[1] is None:
            continue
        for i, f in enumerate(e[1](ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (fmla_eligibility conventions) -------------------------------------------------------------

def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def conjuncts(f):
    if is_iff(f) or type(f) is not list or f[0] != "and":
        return [f]
    return conjuncts(f[1]) + conjuncts(f[2])


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


def defines(f):
    if is_iff(f):
        lhs = f[1][1]
        if lhs[0] in ("unary", "binary"):
            return [key(lhs)]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] == "implies":
        return defines(f[2])
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    if f[0] == "eq" and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    if f[0] == "eq" and f[1][0] == "scale" and f[1][3][0] == "const" and len(f[1][3]) == 3:
        return [f[1][3][2]]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

KIND_BASES = {"members": ("limit", "ntypes", "exdays"), "absences": ("days", "from", "cum", "bminwk", "pd"),
              "years": ("mindays", "vlo", "vhi"),
              "leaves": ("tm", "td", "lo", "hi", "lwk", "wlo", "whi", "start", "logday", "dl", "latest", "wtaken", "qwf",
                         "qwt", "qsum", "qcnt", "avg", "ote"),
              "blocks": (), "quarters": ("att", "qfrom", "qto")}


def int_constants(ctx):
    out = {}
    for kind, bases in KIND_BASES.items():
        for x in getattr(ctx, kind):
            for base in bases:
                out[f"{base}_{x}"] = INT_UNITS[base]
    for y in ctx.years:
        for a in ctx.absences:
            out[f"slo_{a}_{y}"], out[f"shi_{a}_{y}"] = PAIR_UNITS["slo"], PAIR_UNITS["shi"]
            out[f"dy_{a}_{y}"] = PAIR_UNITS["dy"]  # R14
    for a in ctx.absences:
        for b in ctx.absences:
            out[f"sc_{b}_{a}"] = PAIR_UNITS["sc"]
            if b != a:
                out[f"sd_{b}_{a}"] = PAIR_UNITS["sd"]  # R14
    for l in ctx.leaves:
        for qq in ctx.quarters:
            out[f"qs_{qq}_{l}"], out[f"qc_{qq}_{l}"] = PAIR_UNITS["qs"], PAIR_UNITS["qc"]
    return out


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
    for name, (u, w) in int_constants(ctx).items():
        consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({name}).",
                        "verbalisation": f"{w} ({name})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **OPEN_UNARY, **DERIVED_UNARY}.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in {**BINARY, **OPEN_BINARY, **DERIVED_BINARY}.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A team member, absence, year, parental leave, block or "
                                                             "quarter the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      WD: {"scale": "1", "display": {"kind": "decimal", "label": "workdays"}},
                      WK: {"scale": "1", "display": {"kind": "decimal", "label": "weeks"}},
                      MON: {"scale": "1", "display": {"kind": "decimal", "label": "months"}},
                      TDAY: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      PCT: {"scale": "10000", "display": {"kind": "decimal", "label": "percent"}},
                      QN: {"scale": "1", "display": {"kind": "decimal", "label": "quarters"}},
                      NT: {"scale": "1", "display": {"kind": "decimal", "label": "types"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _wrap(walker):
    return lambda builder: (lambda ctx: [walker(f) for f in builder(ctx)])


def _json_sub(a, b):
    return lambda f: json.loads(json.dumps(f).replace(a, b))


def _atom_to(pred, repl):
    """Replace every atom of predicate pred by repl (a planted error)."""
    def walk(f):
        if type(f) is not list or not f:
            return f
        if f[0] == "unary" and f[1] == pred:
            return repl(f) if callable(repl) else repl
        return [walk(x) for x in f]
    return walk


def _drop(pred):
    return lambda builder: (lambda ctx: [f for f in builder(ctx) if not pred(json.dumps(f))])


MUTANTS = {
    "M1": ("THRESHOLD: unit 1 minimum 25 days read as 24", _swap(1, _wrap(_json_sub('"workday_count", "25"',
                                                                                    '"workday_count", "24"')))),
    "M2": ("MIN-DAYS: unit 1 days off sick and other leave counted with PTO (R3 dropped)",
           _swap(1, _wrap(_atom_to("vac", TRUE)))),
    "M3": ("TABLE: unit 38 maternity 12 weeks read as 11", _swap(38, _wrap(_json_sub('"week_count", "12"',
                                                                                     '"week_count", "11"')))),
    "M4": ("TABLE: unit 39 paternity 6 weeks read as 5", _swap(39, _wrap(_json_sub('"week_count", "6"',
                                                                                   '"week_count", "5"')))),
    "M5": ("TENURE: exactly 6 months read as under 6 (unit 37 '<' as '<=')",
           _swap(37, _wrap(lambda f: json.loads(json.dumps(f).replace(
               '["lt", ["const", "month_count", "tm_', '["le", ["const", "month_count", "tm_')) if '"rowu6"' in json.dumps(f)
               else f))),
    "M6": ("TENURE: exactly 12 months read as over 12 (R4's 0 days dropped)",
           _swap(37, _wrap(lambda f: json.loads(json.dumps(f).replace('["lt", ["decimal", "tenure_day", "0"]',
                                                                      '["le", ["decimal", "tenure_day", "0"]'))))),
    "M7": ("DEADLINE: unit 43 logging on the day 4 months before read as too late",
           _swap(43, _wrap(_json_sub('"date_no_later"', '"date_before"')))),
    "M8": ("CAP: unit 45 the 100% cap dropped", _swap(45, _drop(lambda s: '["lt", ["decimal", "percent", "100"]' in s))),
    "M9": ("THRESHOLD: unit 45 12 weeks read as 13", _swap(45, _wrap(_json_sub('"week_count", "12"',
                                                                               '"week_count", "13"')))),
    "M10": ("THRESHOLD: unit 29 extended illness 5 work days read as 6",
            _swap(29, _wrap(_json_sub('"workday_count", "5"', '"workday_count", "6"')))),
    "M11": ("LIMIT: unit 27 the contract's limit read as exclusive", _swap(27, _wrap(_json_sub(
        '["le", ["const", "workday_count", "cum_', '["lt", ["const", "workday_count", "cum_')))),
    "M12": ("GENEROUS: unit 40 a more generous local leave ignored",
            _swap(40, _drop(lambda s: s.startswith('["implies", ["and", ["unary", "haslocal"') and '"localfull"' in s))),
    "M13": ("TYPES: units 17/19 any illness read as Medical Leave (planned, for the member personally, dropped)",
            _swap(16, _wrap(_atom_to("medself", lambda f: ["unary", "ill", f[2]])))),
    "M14": ("BLOCKS: unit 41 a later block paid", _swap(41, _drop(lambda s: '"later"' in s))),
    "M15": ("UNPAID: unit 46 dropped (paternity leave extended unpaid)", _swap(46, lambda b: _none)),
    # REVISION 11-25 (R13, R8)
    "M16": ("APPROVAL: unit 5 manager approval read as needed",
            _swap(2, _wrap(lambda f: ["implies", f[1], f[2][1]] if json.dumps(f).count('"mgrappr"') else f))),
    "M17": ("OVERLIMIT: unit 27 sick days over the contract's limit read as paid",
            _swap(27, _wrap(lambda f: ["implies", f[1], f[2][1]]
                            if f[0] == "implies" and f[2][:1] == ["not"] and f[2][1][1] == "paidsick" else f))),
    "M18": ("SETUP: units 9-10 one of the two steps read as enough",
            _swap(9, _wrap(lambda f: ["and", ["implies", f[1][1], ["or", f[1][2][1], f[1][2][2]]],
                                      ["implies", ["or", f[2][1][1], f[2][1][2]], f[2][2]]]
                           if '"setupdone"' in json.dumps(f) else f))),
    # R14 (revision 11-26): each restores the unit as written before R14
    "M19": ("YEARS: unit 1 an absence counted whole in every year it is in",
            _swap(1, lambda b: per("years", _u1_pre14))),
    "M20": ("LIMIT: unit 27 the whole absence unpaid once the limit is passed; the calendar year assumed as the limit's "
            "period", _swap(27, lambda b: per("absences", _u27_pre14))),
    "M21": ("PERIOD: unit 29 extended illness measured on the one booking",
            _swap(29, lambda b: per("absences", _u29_pre14))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
