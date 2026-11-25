"""GitHub Sponsors Additional Terms, 'Terms For Sponsored Developer' 1.1-3.7 less 3.2.2, with the five definitions of
CHALLENGE.md B8 (statute corpus batch 5, NON-STATUTE (e) developer programme terms): the VE translation, one pass with
today's language. CROSS-FAMILY questions (Codex writer), Opus translator.

Row statute-corpus-github-sponsors-developer-1125 (dri-statute-corpus-github-sponsors-developer-tr-1125, Opus 5.5).
Written from the pinned source only (manage-agents reviews/spare/statute-corpus/batch5/github-sponsors-developer/
source.txt, sha256 83025de4...e730; units.jsonl 833af075...0fcb4, 45 units, 0 table rows) and the decisions D1-D14 of that
folder's ISOLATION.md. Written BEFORE any question exists (orchestrator 2026-11-25T10:25Z: the translation is frozen ahead
of the Codex questions; the Codex writer reads only source.txt). Evidence branch: nothing here is a Lean kernel line, a
profile, a refuses pair or a lint change; nothing merges.

UNITS maps each unit n of units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas;
  ("PART", builder, cause, note) written except the part named in the note (the ledger row's cause);
  ("NOT", None, cause, note)     not written.
A builder returns (formula, target) pairs: target is the atom key or constant the formula defines (None = a check).

WHAT IS CARRIED, AND HOW. Yes/no classifications of the items a case names (ve-quantity@1 formulas over one sort, item);
amounts in USD cents (sums and the $5,000 cap in Lean, never bridged); days as Lean dates: the 30, 60 and 90 days are
shift_days in Lean. The calendar steps the language has no form for (a month's last day, a month's 22nd, a month's third
Thursday, the same date 12 months later, whole years of age) come from ONE tested bridge (bridge/bridge.py); the units
that rest on them are ledgered "bridged".

ITEMS (x<digits> is reserved by VE). p the developer; m<k> a calendar month (first day stated, its months in order; the chain of months since the last
payout); y<k> an amount that reached the developer (its day, its amount, its kind; under its month, in day order);
d<k> a stated deduction (discount, tax, fee, refund, chargeback, amount not collected, amount owed to a third party, bank
fee; under its month); a<k> an act of the developer (raising funds, allowing payments, an advertising agreement); u<k> a
duty item (something the developer might have to do); g<k> an act of GitHub or Stripe.

READINGS fixed here, before any question exists (refuse when in doubt: where two readings give two answers no rule fires
and the question is OPEN; D-numbers are ISOLATION.md's):
R1  SPONSORED DEVELOPER PAYMENT (unit 5, D3, D6(d)). For a month: the amounts of the month that are sponsorships paid
    through the Program and Stripe, subscription payments, pooled-fund allocations (unit 40: "the payment timing and
    process remains as described above"), other monetization proceeds the developer elected, and matching money the case
    states, LESS every stated deduction of the month. A donation paid to the developer's own merchant account is not
    included (unit 30). "Other Exclusions as outlined in Section 4" (out of scope) applies none (D3). Two outcomes, OPEN:
    a stated deduction that falls in the first 12 months of an individual account (unit 22: "100% of sponsorships will go
    to the sponsored developer" and no GitHub fee, against unit 5's "less ..."; D6(d)); a deduction whose event and
    payment lie in different months (which month's net it reduces; the encoder enters it under both months, marked).
R2  MATCHING PERIOD (unit 22, 24; D5). It exists for an individual account GitHub accepted; it runs from the acceptance
    day (convention (c)) through the bridged last day (29 February: the two-reading days OPEN). A developer who left and
    rejoined: days from the rejoining on are in the period only if GitHub counted the gap (stated), and out if GitHub let
    the period expire (stated); otherwise OPEN. "Cannot be extended": nothing extends it.
R3  ELIGIBILITY FOR MATCHING (units 16-21, D7, D4). The account is eligible when it is an individual's account GitHub
    accepted, the developer has a GitHub account, is actively contributing to OSS (stated), GitHub's determination of the
    mission is favourable (stated), GitHub approved it for matching (stated: "case-by-case", "not all eligible ... will
    receive") and GitHub has not withheld, rescinded or blocked it (stated). Not eligible when any fails or it is an
    organization's account.
R4  A MATCHED PAYMENT (units 16, 18, 20, 22, 23). A sponsorship or subscription payment through the Program is matched
    when the account is eligible, the payment is in the matching period, it is not from an organization, not from an
    account with a published GitHub Sponsors profile, not to a second account of the developer (18: no matching across
    several accounts), its sponsorship had not stopped (23), and it was not charged back before its month's Sponsored
    Developer Payment date (23; read as the month's payout day, R7: if that day is OPEN, so is this). A pooled-fund
    allocation or a donation to the developer's merchant account: whether it is "community sponsorship" the text does not
    say (OPEN). Matching money, other proceeds: not matched.
R5  THE MATCH AND THE CAP (unit 22; the brief's stated reading of "match"). A matched payment gets an equal amount, as far
    as the $5,000 total allows: the payments in day order; matched so far + this payment <= $5,000: the payment's amount;
    above: the rest up to $5,000 (0 once it is reached). Two payments on one day across the cap: the encoder asks no
    single payment's amount (order unknown); the month total is the same in either order.
R6  ACH / WIRE THRESHOLD (unit 39, D6(b), unit 42). The month's balance for the threshold = the unpaid balance carried
    from the months before it in the chain + the month's Sponsored Developer Payment without matching money (39:
    "Contributions from the ... Matching Fund do not count"). Paid for the month: balance > $100, or = $100 when no
    earlier month of the chain accrued, or the developer leaves GitHub Sponsors in that month (39's last sentence). Not
    paid: balance < $100 and the developer does not leave. Exactly $100 after an accrual: "reaches $100" against "above
    the threshold": OPEN. A different threshold for the country (unit 42, stated): OPEN (39 says $100).
    Stripe Connect (38): paid "regardless of the amount"; with a stated cross-border minimum: paid when "the balance
    accrued since the last payout" is at least the minimum, not paid below it. That balance (sbal) = the month's
    Sponsored Developer Payment (with matching money: 38 excludes nothing) + the balance of the month before when that
    month was not paid; a payout (or the start of the chain) resets it. A month whose carried balance the facts leave
    unknown (not the chain's start, no earlier month in the case) has no balance, so no answer (OPEN). Row
    statute-corpus-github-sponsors-wrong-s028 (fix of the frozen 5336e71bbc, which compared the month's own payment).
R7  PAYOUT DAY OF A MONTH (units 36-39, D6(a)). Unit 36 puts a month's payments in the 30 days after its close; 38 / 39
    put payouts on a 22nd / a third Thursday. Their one common day is the 22nd / third Thursday of the NEXT month (bridged),
    or the stated moved initiation day (38: "can change from month to month"; it must still lie in 36's window, else
    OPEN). FIRST PAYMENTS (37): a month whose scheduled day is on or before the day 60 days after the first sponsorship
    was initiated is paid with the first payments: "60 days after" (reading A) against "subject to the variables below"
    (reading B: the first 22nd / third Thursday on or after it, bridged); a day only when the two coincide. A month that
    is not paid (R6) has no payout day here.
R8  WINDOW (36): the latest day for a month's payments = its last day + 30 (Lean). FIRST PAYMENT (37): the first
    sponsorship's initiation day + 60 (Lean); the first payout day (Stripe Connect, initiation not moved) when it is
    also a 22nd. AFTER TERMINATION (41): the last day of the month in which GitHub recognized the termination + 90 (the
    brief's reading of "approximately 90 days").
R9  AGE (units 6, 7, D6(c)). Participation: in the United States at least 13 (the text's example); elsewhere the stated
    minimum age of the country's law; a valid GitHub account; agreement to the Acceptable Use section, the GitHub Policies
    and these terms (stated outside outcomes). Giving and receiving Sponsor funds: 18 or over: as participation; 14 to 17:
    only with Stripe able to collect verification from a legal guardian (stated); exactly 13: with verification yes in
    both readings of "over the age of 13", without it OPEN.
R10 PROHIBITED PURPOSES (units 8-15, 31). An act that allows payments or raises funds involving a listed purpose is
    forbidden; legality, IP violation, processing personal data unlawfully, sanctions and an advertising agreement the
    Agreement or Community Guidelines prohibit are outside outcomes the case states (plain); "misrepresentation or
    deception" is a stated judgment read only on an act that makes representations about the reasons for raising funds
    (guard). An act no listed purpose classifies is not forbidden ("may": yes), unless its content's primary focus is
    advertising (31 "should not": OPEN).
R11 DUTIES (26, 27, 30, 31, 34, 44, 45): a duty item one of these clauses names is required; any other is not.
R12 GITHUB AND STRIPE (21, 22, 25, 27, 30, 32, 34-36, 42-45). "May" yes where the text grants it on facts the case states
    (otherwise OPEN: the text does not close GitHub's acts); "will / is responsible / is liable": the text's no.
R13 DESCRIPTIONS (1-4, 16, 27): a payer of a sponsorship or subscription through the Program is a Sponsor; a payment
    through the Program and Stripe is a Sponsorship; a subscription payment is a Subscription; an applicant before
    1 January 2020 (an individual) will be reviewed for matching; entry into the Program needs registration and
    acceptance.
No number from a case's facts is ever a coefficient: every coefficient is a literal of the pinned text ($5,000, $100,
30, 60, 90, 13, 18, 1 January 2020).
"""
from __future__ import annotations

import hashlib
import json

USD, DAY, AGE = ("usd_cent", "day", "age_year")

# base -> (unit, wording); a constant is f"{base}_{item}"; bases carry no "_"
BASES = {
    # stated
    "ad": (DAY, "the day GitHub accepted the developer's account into the Program (stated)"),
    "ap": (DAY, "the day the developer applied to the Program (stated)"),
    "fd": (DAY, "the day the developer's first sponsorship was initiated (stated)"),
    "rj": (DAY, "the day the developer rejoined GitHub Sponsors after leaving (stated)"),
    "rc": (DAY, "the day GitHub recognized that the Additional Terms had been terminated (stated)"),
    "ag": (AGE, "the developer's age in whole years (stated or bridged)"),
    "mna": (AGE, "the minimum age under the law of the developer's country (stated outside outcome)"),
    "mf": (DAY, "the first day of the calendar month (stated)"),
    "mvd": (DAY, "the moved payout initiation day for the month's payout (stated)"),
    "mn": (USD, "the cross-border minimum payout amount (stated)"),
    "dy": (DAY, "the day of the payment or deduction (stated)"),
    "am": (USD, "the amount of the payment or deduction (stated)"),
    "cbd": (DAY, "the day the payment was charged back to the Sponsor (stated)"),
    # bridged (bridge/bridge.py)
    "ml": (DAY, "the last day of the calendar month (bridged)"),
    "ps": (DAY, "the 22nd (Stripe Connect) or third Thursday (ACH or wire) of the month after the month (bridged)"),
    "mlo": (DAY, "the last day of the first 12 months in the Program on the first reading (bridged)"),
    "mhi": (DAY, "the last day of the first 12 months in the Program on the second reading (bridged)"),
    "nx": (DAY, "the first 22nd or third Thursday on or after the day 60 days after the first sponsorship (bridged)"),
    "rl": (DAY, "the last day of the month in which GitHub recognized the termination (bridged)"),
    # derived (Lean steps)
    "wl": (DAY, "the last day of the 30 days after the close of the month"),
    "fp": (DAY, "the day 60 days after the first sponsorship was initiated"),
    "tr": (DAY, "the day 90 days after the end of the month in which GitHub recognized the termination"),
    "mpe": (DAY, "the last day of the developer's first 12 months in the Program"),
    "fpd": (DAY, "the day of the developer's first payout"),
    "sd": (DAY, "the month's scheduled payout day after any stated move"),
    "pdy": (DAY, "the day the month's Sponsored Developer Payment is paid out"),
    "sdp": (USD, "the month's Sponsored Developer Payment"),
    "tb": (USD, "the month's Sponsored Developer Payment without matching money"),
    "ia": (USD, "the amount's part in the Sponsored Developer Payment (0 when it is not included)"),
    "nm": (USD, "the amount's part in the payout threshold balance (0 for matching money or an amount not included)"),
    "bal": (USD, "the balance at the end of the month for the payout threshold"),
    "sbal": (USD, "the Stripe Connect balance accrued since the last payout (unit 38)"),
    "mt": (USD, "the matching amount for the payment"),
    "cm": (USD, "the matching amount for the payments up to and including this one"),
    "mm": (USD, "the matching amount for the month's payments"),
    "tm": (USD, "the total matching amount for all the case's payments"),
}
BRIDGED = ("ml", "ps", "mlo", "mhi", "nx", "rl")
STATED_BASES = ("ad", "ap", "fd", "rj", "rc", "ag", "mna", "mf", "mvd", "mn", "dy", "am", "cbd") + BRIDGED
STEP_BASES = tuple(b for b in BASES if b not in STATED_BASES)
UNIT_OF = {b: u for b, (u, _) in BASES.items()}

# kind -> {fact: wording}. PLAIN facts are closed by the encoder (what the case does not say is false); STATED facts
# (judgments the case states) are never closed: unknown unless the case states them.
PLAIN = {
    "dev": {
        "acc": "GitHub accepted the developer's account into the Program",
        "regd": "the developer completed the Program's registration process",
        "ind": "the developer's account was accepted as an individual's account",
        "org": "the developer's account is an organization's account",
        "ghacct": "the developer has a valid GitHub account",
        "agreed": "the developer has agreed to the Acceptable Use section of the Agreement, the applicable GitHub Policies "
                  "and the GitHub Sponsors Additional Terms (stated outside outcome)",
        "us": "the developer lives in the United States",
        "applied": "the developer applied to the Program (on the stated day)",
        "devc": "the developer develops content under the Program",
        "rcv": "the developer receives Sponsored Developer Payments while participating in the Program",
        "sc": "the developer is paid through Stripe Connect",
        "ach": "the developer is paid through ACH transfer",
        "wire": "the developer is paid through wire transfer",
        "othr": "GitHub's payment policy sets another payout threshold for the developer's country (stated outside outcome)",
        "fmv": "the initiation day of the developer's first payout is moved (country, holiday, weekend or other factor)",
        "rejn": "the developer left GitHub Sponsors and rejoined later (on the stated day)",
        "term": "the Additional Terms were terminated and GitHub recognized it (on the stated day)",
        "pviol": "GitHub discovered a potential policy violation before payment of matching funds granted in the matching "
                 "period",
        "fail": "the developer failed to accurately provide or maintain the financial, tax and banking information "
                "GitHub requested",
        "hasfd": "the case states the day the developer's first sponsorship was initiated",
    },
    "mon": {
        "chs": "no unpaid balance is carried into this month from an earlier month (the chain of months starts here)",
        "mv": "the payout initiation day of this month's payout is moved (country, holiday, weekend or other factor)",
        "xbm": "this month's payout is a cross-border payout to which a stated minimum payout amount applies",
        "left": "the developer leaves GitHub Sponsors in this month",
    },
    "pay": {
        "ksp": "the amount is a sponsorship paid through the Program and Stripe (not a subscription offer)",
        "ksub": "the amount is a payment for a Subscription the developer offers through the Program",
        "kpool": "the amount is a sponsorship allocated from a pooled fund (a SOSS Fund or a Fund Profile)",
        "kdon": "the amount is a donation or direct sponsorship paid to the developer's own merchant account",
        "kmon": "the amount is proceeds from another monetization option the developer elected",
        "kmf": "the amount is matching money from the GitHub Sponsors Matching Fund",
        "forg": "the payment comes from an organization",
        "fprof": "the payment comes from a user or organization account with a published GitHub Sponsors profile",
        "oacct": "the payment is to an account of the developer other than the one account matching is approved for",
        "stopd": "the payment's sponsorship or subscription had stopped before the payment",
        "cbk": "the payment was charged back to the Sponsor (on the stated day)",
    },
    "ded": {
        "gfee": "the deduction is a fee charged by GitHub",
        "xmon": "the deduction's event and the payment it concerns fall in different months",
    },
    "act": {
        "fraud": "the act involves fraud or ransom",
        "illegal": "the act involves a violation of intellectual property or another illegal purpose (stated outside "
                   "outcome)",
        "reasons": "the act makes representations about the reasons for raising funds or requesting sponsorship",
        "crypto": "the act involves the purchase or sale of ICOs, utility tokens or other cryptocurrency",
        "secur": "the act involves the purchase or sale of securities, equity or other investment offers",
        "sellpi": "the act involves the sale of personal information",
        "pilaw": "the act involves processing personal information in violation of a law (stated outside outcome)",
        "gamble": "the act involves a lottery, raffle, gambling, pyramid scheme, self-dealing, get-rich-quick scheme, "
                  "deceptive marketing scheme, donation-for-donation scheme or an attempt to game GitHub's or third "
                  "parties' systems or services",
        "sanct": "the act involves a country, region, government, person or entity not permitted under the applicable "
                 "economic sanctions (stated outside outcome)",
        "adagr": "the act is entering into an advertising agreement to promote a product or brand",
        "adproh": "that advertising agreement would be prohibited by the Agreement or GitHub's Community Guidelines "
                  "(stated outside outcome)",
        "adprim": "the act makes advertising or promotional marketing the primary focus of the Sponsored Developer Content",
    },
    "duty": {
        "dcreate": "the item is creating a Sponsored Developer Account",
        "dcontent": "the item is making Sponsored Developer Content available via the Program and Service",
        "dpol": "the item is complying with all GitHub Policies",
        "dsupport": "the item is support, development and maintenance of the account and content, and complaints about them",
        "dtrue": "the item is registering with the developer's true identity and keeping the registration information "
                 "true, accurate, current and complete",
        "dmerch": "the item is establishing a merchant account with a third-party payment provider to accept donations",
        "dadlaw": "the item is complying with the laws on advertising hosted in the Sponsored Developer Content",
        "dexp": "the item is bearing the expenses the developer incurs in performing the Additional Terms",
        "drefund": "the item is specifying the terms and conditions of refunds to the developer's Sponsors",
        "dfin": "the item is providing complete and accurate financial, tax and banking information GitHub requests, to "
                "receive Sponsored Developer Payments",
    },
    "gh": {
        "gwmf": "the act is GitHub withholding or rescinding Matching Fund money or blocking the developer from matching",
        "gfeemp": "the act is GitHub charging a fee on a sponsorship paid in the developer's matching period",
        "gdis": "the act is GitHub disabling payouts until its investigation is completed",
        "grev": "the act is GitHub revoking matched funds contributed to the developer",
        "grefuse": "the act is GitHub refusing the developer's acceptance into the Program",
        "gdonl": "the act is GitHub answering a claim or remedy of the developer relating to donations",
        "gdonr": "the act is GitHub providing information or a report on the donations made to the developer",
        "gxmit": "the act is GitHub transmitting or transferring funds to the developer",
        "greimb": "the act is GitHub reimbursing or advancing the developer's expenses",
        "gwith": "the act is GitHub withholding payment pending its reasonable investigation",
        "gperm": "the act is GitHub permanently withholding amounts due to the developer",
        "sreall": "the act is the Sponsor reallocating withheld funds to another Sponsored Developer",
        "gdelay": "the act is GitHub or Stripe being responsible for delay or misapplication caused by incorrect or "
                  "incomplete information from the developer or a bank, a bank's failure to credit, or Stripe's errors",
        "scomb": "the act is Stripe combining the Sponsored Developer Payment with others owed to the developer",
        "gconv": "the act is GitHub converting USD to the local currency of the developer's address",
        "grefund": "the act is GitHub providing support for refunds or paying a refund",
        "gbank": "the act is GitHub deducting related bank fees from the Sponsored Developer Payment",
        "gterm": "the act is GitHub terminating the Additional Terms",
        "gforf": "the act is the forfeiture of Sponsored Developer Payments owed to the developer",
    },
}
STATED = {
    "dev": {
        "oss": "the developer is actively contributing to OSS (stated judgment)",
        "mission": "GitHub determined that the developer's use of GitHub and of the account is in accordance with the "
                   "GitHub Sponsors mission (stated judgment)",
        "appr": "GitHub approved the developer's account for matching (stated judgment: case-by-case)",
        "rescind": "GitHub withheld or rescinded the developer's Matching Fund money or blocked the developer from it "
                   "(stated)",
        "gapc": "GitHub counted the gap between the participation periods toward the matching period (stated)",
        "expd": "GitHub let the developer's matching period expire on leaving (stated)",
        "ver": "Stripe can collect verification information from the developer's legal guardian (stated)",
        "breach": "the developer is in breach, or suspected breach, of the Additional Terms or the Agreement (stated)",
        "detb": "GitHub determined, in its sole discretion, that the developer is in breach (stated)",
        "fviol": "the matched funds were found to be in violation of the Matching Fund policy (stated)",
    },
    "act": {"misrep": "the representations are misrepresentation or deception (stated judgment)"},
}
DERIVED = {
    "elig": "the developer's account is eligible for GitHub Sponsors matching",
    "part": "the developer meets the conditions to participate in the Program",
    "gr": "the developer can give and receive Sponsor funds",
    "review": "the developer will be reviewed for eligibility for the Matching Fund",
    "entered": "the developer has entered the Program",
    "sdev": "the developer is a Sponsored Developer",
    "inmp": "the item's day is in the developer's matching period",
    "mok": "the payment is matched",
    "cbb": "the payment was charged back before its Sponsored Developer Payment date",
    "inc": "the amount is included in the Sponsored Developer Payment",
    "spship": "the payment is a Sponsorship",
    "subs": "the payment is a Subscription",
    "sponsor": "the payer is a Sponsor",
    "amb": "the month's Sponsored Developer Payment has two readings",
    "fst": "the month's payments are paid with the first payments",
    "accr": "a balance accrued from an earlier month of the chain",
    "paid": "a payout is issued for the month",
    "forb": "the act is forbidden",
    "req": "the item is required of the developer",
    "ghmay": "GitHub (or Stripe, or the Sponsor) may do the act",
    "ghwill": "GitHub (or Stripe) will do, owes or is responsible for the act",
}
FACTS = {kd: {**PLAIN.get(kd, {}), **STATED.get(kd, {})} for kd in PLAIN}
ALL_FACTS = {n: w for d in FACTS.values() for n, w in d.items()}
STATED_JUDGMENT = ("oss", "mission", "appr", "rescind", "gapc", "expd", "ver", "breach", "detb", "fviol", "misrep")
assert not set(ALL_FACTS) & set(DERIVED)

# parameters a planted error may change (MUTANTS); the literals of the pinned text
PARAM = {"cap": "5000.00", "thr": "100.00", "win": 30, "prob": 60, "post": 90, "usmin": 13, "adult": 18,
         "jan2020": "2020-01-01", "don_inc": False, "mf_thr": False, "deduct": True, "org_no": True, "prof_no": True,
         "cb_before": True, "expire": True, "crypto": True, "accr_open": True, "first_open": True,
         "xb_carry": True}
_P = dict(PARAM)


# --- formula helpers (ve-quantity@1 wire shapes) --------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def usd(v): return ["decimal", USD, v]
def age(v): return ["decimal", AGE, str(v)]
def date(v): return ["date", v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]      # a is n days after b
TRUE, FALSE = ["top"], ["bottom"]


def And(*fs):
    fs = [f for f in fs if f is not None and f != TRUE]
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
        return ["decimal", unit, "0"] if unit != USD else usd("0.00")
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = ["add", unit, t, r]
    return r


def k(base, x):
    return ["const", UNIT_OF[base], f"{base}_{x}"]


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def A(p, x):
    return key(U(p, x))


# --- the case context -------------------------------------------------------------------------------------------------

class Ctx:
    """items: [(id, kind)] in the case's order; parent: {child: month}. Kinds: dev (p), mon, pay, ded, act, duty, gh."""

    def __init__(self, items, parent=None):
        self.items = list(items)
        self.parent = dict(parent or {})

    def of(self, kind):
        return [x for x, kd in self.items if kd == kind]

    def children(self, m, kind):
        kinds = dict(self.items)
        return [y for y, _ in self.items if self.parent.get(y) == m and kinds[y] == kind]

    def prev(self, m):
        ms = self.of("mon")
        i = ms.index(m)
        return ms[i - 1] if i > 0 else None

    def kind(self, x):
        return dict(self.items)[x]


P = "p"


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


def pos(atom, x, *conds):
    return both(And(*conds), None, atom, x)


def neg(atom, x, *conds):
    return both(None, And(*conds), atom, x)


def same_day(a, b):
    return And(no_later(a, b), no_later(b, a))


AW = Or(pf("ach"), pf("wire"))
INCL = ("ksp", "ksub", "kpool", "kmon", "kmf")


# --- the rules, unit by unit ------------------------------------------------------------------------------------------

def _u1(ctx):
    """Unit 1 (R13): the payer of a sponsorship or subscription payment through the Program is a Sponsor."""
    out = []
    for x in ctx.of("pay"):
        out += pos("sponsor", x, Or(U("ksp", x), U("ksub", x), U("kpool", x)))
    return out


def _u2(ctx):
    """Unit 2 (R13): a Sponsored Developer develops content under the Program and receives Sponsored Developer Payments."""
    return pos("sdev", P, pf("devc"), pf("rcv"), pf("acc")) + neg("sdev", P, Not(pf("devc"))) + \
        neg("sdev", P, Not(pf("rcv")))


def _u3(ctx):
    """Unit 3 (R13): a payment paid through the Program and Stripe is a Sponsorship."""
    out = []
    for x in ctx.of("pay"):
        out += pos("spship", x, Or(U("ksp", x), U("ksub", x), U("kpool", x)))
        out += neg("spship", x, Or(U("kmf", x), U("kmon", x)))
    return out


def _u4(ctx):
    """Unit 4 (R13): a payment for a Subscription offer is a Subscription; a sponsorship without one is not."""
    out = []
    for x in ctx.of("pay"):
        out += pos("subs", x, U("ksub", x))
        out += neg("subs", x, Or(U("ksp", x), U("kpool", x), U("kdon", x), U("kmf", x), U("kmon", x)))
    return out


def _u5(ctx):
    """Unit 5 (R1): the month's Sponsored Developer Payment = included amounts less stated deductions (Lean sums); the
    same without matching money for the ACH/wire threshold (unit 39, R6)."""
    out = []
    for x in ctx.of("pay"):
        out += pos("inc", x, Or(*[U(kd, x) for kd in INCL + (("kdon",) if _P["don_inc"] else ())]))
        if not _P["don_inc"]:
            out += neg("inc", x, U("kdon", x))
        out.append((Implies(U("inc", x), Eq(k("ia", x), k("am", x))), f"ia_{x}"))
        out.append((Implies(Not(U("inc", x)), Eq(k("ia", x), usd("0.00"))), f"ia_{x}"))
        nmf = TRUE if _P["mf_thr"] else Not(U("kmf", x))
        out.append((Implies(And(U("inc", x), nmf), Eq(k("nm", x), k("am", x))), f"nm_{x}"))
        out.append((Implies(Or(Not(U("inc", x)), FALSE if _P["mf_thr"] else U("kmf", x)), Eq(k("nm", x), usd("0.00"))),
                    f"nm_{x}"))
    for m in ctx.of("mon"):
        pays, deds = ctx.children(m, "pay"), ctx.children(m, "ded")
        out += both(Or(*[Or(U("xmon", d), U("inmp", d)) for d in deds]),
                    And(*[And(Not(U("xmon", d)), Not(U("inmp", d))) for d in deds]), "amb", m)
        dsum = [k("am", d) for d in deds] if _P["deduct"] else []
        out.append((Implies(Not(U("amb", m)), Eq(Add(USD, [k("sdp", m)] + dsum), Add(USD, [k("ia", x) for x in pays]))),
                    f"sdp_{m}"))
        out.append((Implies(Not(U("amb", m)), Eq(Add(USD, [k("tb", m)] + dsum), Add(USD, [k("nm", x) for x in pays]))),
                    f"tb_{m}"))
    return out


def _u6(ctx):
    """Unit 6 (R9): who may participate (US: at least 13; elsewhere the stated minimum age)."""
    ag = k("ag", P)
    return (pos("part", P, pf("us"), Le(age(_P["usmin"]), ag), pf("ghacct"), pf("agreed"))
            + pos("part", P, Not(pf("us")), Le(k("mna", P), ag), pf("ghacct"), pf("agreed"))
            + neg("part", P, pf("us"), Lt(ag, age(_P["usmin"])))
            + neg("part", P, Not(pf("us")), Lt(ag, k("mna", P)))
            + neg("part", P, Not(pf("ghacct"))) + neg("part", P, Not(pf("agreed"))))


def _u7(ctx):
    """Unit 7 (R9, D6(c)): 13 to 17 give and receive Sponsor funds only with a guardian's verification."""
    ag = k("ag", P)
    teen = And(Le(age(14), ag), Lt(ag, age(_P["adult"])))
    return (pos("gr", P, U("part", P), Le(age(_P["adult"]), ag))
            + pos("gr", P, U("part", P), teen, pf("ver"))
            + pos("gr", P, U("part", P), Le(age(13), ag), Lt(ag, age(14)), pf("ver"))
            + neg("gr", P, Not(U("part", P)))
            + neg("gr", P, teen, Not(pf("ver"))))


def _ban(*conds):
    def b(ctx):
        out = []
        for a in ctx.of("act"):
            out += pos("forb", a, *[U(cd, a) if isinstance(cd, str) else cd(a) for cd in conds])
        return out
    return b


def _u8(ctx):
    """Unit 8 (R10): the lead-in; an act no listed purpose classifies is not forbidden (closure)."""
    out = []
    for a in ctx.of("act"):
        out += neg("forb", a, *[Not(U(f, a)) for f in ("fraud", "illegal", "crypto" if _P["crypto"] else "fraud", "secur", "sellpi", "pilaw",
                                                         "gamble", "sanct", "adprim")],
                   Or(Not(U("reasons", a)), Not(U("misrep", a))), Or(Not(U("adagr", a)), Not(U("adproh", a))))
    return out


def _u16(ctx):
    """Unit 16 (R3, R4, R13): review of applicants before 1 January 2020; no organization in the Matching Fund; an
    organization's sponsorship is not matched."""
    out = pos("review", P, pf("applied"), pf("ind"), before(k("ap", P), date(_P["jan2020"])))
    out += neg("elig", P, pf("org"))
    for x in ctx.of("pay"):
        if _P["org_no"]:
            out += neg("mok", x, U("forg", x))
    return out


def _u18(ctx):
    """Unit 18 (R3, R4): a GitHub account, accepted as an individual, actively contributing to OSS; one account only."""
    out = neg("elig", P, Not(pf("ind"))) + neg("elig", P, Not(pf("ghacct"))) + neg("elig", P, Not(pf("oss")))
    for x in ctx.of("pay"):
        out += neg("mok", x, U("oacct", x))
    return out


def _u19(ctx):
    """Unit 19 (R3): GitHub's determination on the mission (stated)."""
    return neg("elig", P, Not(pf("mission")))


def _u20(ctx):
    """Unit 20 (R4): no matching for a sponsorship from an account with a published GitHub Sponsors profile."""
    out = []
    for x in ctx.of("pay"):
        if _P["prof_no"]:
            out += neg("mok", x, U("fprof", x))
    return out


def _u21(ctx):
    """Unit 21 (R3, R12): GitHub may withhold or rescind Matching Fund money and block a user for any reason."""
    out = neg("elig", P, pf("rescind"))
    for g in ctx.of("gh"):
        out += pos("ghmay", g, U("gwmf", g))
    return out


def _u17(ctx):
    """Unit 17 (R3): case-by-case: eligibility needs GitHub's approval (stated); the whole of R3's positive rule."""
    return (pos("elig", P, pf("ind"), Not(pf("org")), pf("acc"), pf("ghacct"), pf("oss"), pf("mission"), pf("appr"),
                Not(pf("rescind")))
            + neg("elig", P, Not(pf("appr"))) + neg("elig", P, Not(pf("acc"))))


def _inmp(ctx):
    """Unit 22 / 24 (R2): the day of a payment or deduction in the matching period."""
    out = []
    for y in ctx.of("pay") + ctx.of("ded"):
        d = k("dy", y)
        out += pos("inmp", y, pf("ind"), pf("acc"), no_later(k("ad", P), d), no_later(d, k("mlo", P)),
                   Or(Not(pf("rejn")), before(d, k("rj", P)), pf("gapc")))
        out += neg("inmp", y, Not(pf("ind")))
        out += neg("inmp", y, Not(pf("acc")))
        out += neg("inmp", y, before(d, k("ad", P)))
        out += neg("inmp", y, before(k("mhi", P), d))
    return out


def _u22(ctx):
    """Unit 22 (R2, R5, R8, R12): the matching period, the equal match up to $5,000 in total, no GitHub fee in it."""
    out = _inmp(ctx)
    cap = usd(_P["cap"])
    prev = usd("0.00")
    for x in ctx.of("pay"):
        out += neg("mok", x, Not(U("inmp", x)))
        out += neg("mok", x, Not(U("elig", P)))
        out += neg("mok", x, Or(U("kmf", x), U("kmon", x)))
        out.append((Implies(Not(U("mok", x)), Eq(k("mt", x), usd("0.00"))), f"mt_{x}"))
        out.append((Implies(And(U("mok", x), Le(add(USD, prev, k("am", x)), cap)), Eq(k("mt", x), k("am", x))),
                    f"mt_{x}"))
        out.append((Implies(And(U("mok", x), Lt(cap, add(USD, prev, k("am", x)))), Eq(add(USD, k("mt", x), prev), cap)),
                    f"mt_{x}"))
        out.append((Eq(k("cm", x), add(USD, prev, k("mt", x))), f"cm_{x}"))
        prev = k("cm", x)
    pays = ctx.of("pay")
    if pays:
        out.append((Eq(k("tm", P), k("cm", pays[-1])), f"tm_{P}"))
    for m in ctx.of("mon"):
        out.append((Eq(k("mm", m), Add(USD, [k("mt", x) for x in ctx.children(m, "pay")])), f"mm_{m}"))
    out.append((Implies(And(pf("ind"), pf("acc"), Not(pf("rejn")), no_later(k("mhi", P), k("mlo", P))),
                        Eq(k("mpe", P), k("mlo", P))), f"mpe_{P}"))
    for g in ctx.of("gh"):
        out += neg("ghwill", g, U("gfeemp", g))
    return out


def _u23(ctx):
    """Unit 23 (R4): a stopped sponsorship stops its matching; a chargeback before the payment date is not matched."""
    out = []
    for x in ctx.of("pay"):
        m = ctx.parent[x]
        out += neg("mok", x, U("stopd", x))
        out += neg("mok", x, U("cbb", x))
        early, late = ((before(k("cbd", x), k("pdy", m)), no_later(k("pdy", m), k("cbd", x))) if _P["cb_before"] else
                       (before(k("pdy", m), k("cbd", x)), no_later(k("cbd", x), k("pdy", m))))
        out += pos("cbb", x, U("cbk", x), early)
        out += neg("cbb", x, Not(U("cbk", x)))
        out += neg("cbb", x, U("cbk", x), late)
        out += pos("mok", x, U("elig", P), Or(U("ksp", x), U("ksub", x)),
                   Not(U("forg", x)) if _P["org_no"] else None, Not(U("fprof", x)) if _P["prof_no"] else None,
                   Not(U("oacct", x)), U("inmp", x), Not(U("stopd", x)), Not(U("cbb", x)))
    return out


def _u24(ctx):
    """Unit 24 (R2): leaving and rejoining: GitHub's choice (stated) counts the gap or lets the period expire."""
    out = []
    for y in ctx.of("pay") + ctx.of("ded"):
        if _P["expire"]:
            out += neg("inmp", y, pf("rejn"), no_later(k("rj", P), k("dy", y)), pf("expd"))
        else:
            out += pos("inmp", y, pf("ind"), pf("acc"), no_later(k("ad", P), k("dy", y)), no_later(k("dy", y), k("mlo", P)),
                       pf("expd"))
    return out


def _u25(ctx):
    """Unit 25 (R12): GitHub may disable payouts until its investigation is done; may revoke funds found in violation."""
    out = []
    for g in ctx.of("gh"):
        out += pos("ghmay", g, U("gdis", g), pf("pviol"))
        out += pos("ghmay", g, U("grev", g), pf("fviol"))
    return out


def _duty(*facts):
    def b(ctx):
        out = []
        for u in ctx.of("duty"):
            for f in facts:
                out += pos("req", u, U(f, u))
        return out
    return b


def _duty_closure(ctx):
    out = []
    for u in ctx.of("duty"):
        out += neg("req", u, *[Not(U(f, u)) for f in PLAIN["duty"]])
    return out


def _u26(ctx):
    """Unit 26 (R11, R12): create the account, make content available, comply with GitHub Policies; the developer alone
    is responsible for support, development, maintenance and complaints (closure of duties here)."""
    return _duty("dcreate", "dcontent", "dpol", "dsupport")(ctx) + _duty_closure(ctx)


def _u27(ctx):
    """Unit 27 (R11, R12, R13): entry needs registration and acceptance; true identity; GitHub may refuse acceptance."""
    out = pos("entered", P, pf("regd"), pf("acc")) + neg("entered", P, Not(pf("regd"))) + \
        neg("entered", P, Not(pf("acc")))
    out += _duty("dtrue")(ctx)
    for g in ctx.of("gh"):
        out += pos("ghmay", g, U("grefuse", g))
    return out


def _u30(ctx):
    """Unit 30 (R1, R11, R12): donations go to the merchant account, are not in Sponsored Developer Payments, give no
    claim against GitHub; GitHub may report them; a merchant account is required for them."""
    out = _duty("dmerch")(ctx)
    for g in ctx.of("gh"):
        out += neg("ghwill", g, U("gdonl", g))
        out += pos("ghmay", g, U("gdonr", g))
    return out


def _u31(ctx):
    """Unit 31 (R10, R11): no advertising agreement the Agreement or Community Guidelines prohibit; advertising laws."""
    return _ban("adagr", "adproh")(ctx) + _duty("dadlaw")(ctx)


def _u32(ctx):
    """Unit 32 (R12): GitHub does not transmit or transfer funds to Sponsored Developers."""
    out = []
    for g in ctx.of("gh"):
        out += neg("ghwill", g, U("gxmit", g))
    return out


def _u34(ctx):
    """Unit 34 (R11, R12): the developer bears its expenses; GitHub will not reimburse or advance them."""
    out = _duty("dexp")(ctx)
    for g in ctx.of("gh"):
        out += neg("ghwill", g, U("greimb", g))
    return out


def _u35(ctx):
    """Unit 35 (R12): withholding on breach or suspected breach pending investigation; permanent withholding after
    GitHub's determination; the Sponsor can then reallocate."""
    out = []
    for g in ctx.of("gh"):
        out += pos("ghmay", g, U("gwith", g), pf("breach"))
        out += pos("ghmay", g, U("gperm", g), pf("detb"))
        out += pos("ghmay", g, U("sreall", g), pf("detb"))
    return out


def _u36(ctx):
    """Unit 36 (R7, R8, R12): a month's payments within 30 days after its close (Lean); the payout day of a month that is
    not paid with the first payments; GitHub/Stripe not responsible for delays from wrong information or Stripe."""
    out = []
    for m in ctx.of("mon"):
        out.append((shift(k("wl", m), k("ml", m), _P["win"]), f"wl_{m}"))
        out.append((Implies(And(U("paid", m), Not(U("fst", m)), before(k("ml", m), k("sd", m)),
                                no_later(k("sd", m), k("wl", m))), Eq(k("pdy", m), k("sd", m))), f"pdy_{m}"))
    for g in ctx.of("gh"):
        out += neg("ghwill", g, U("gdelay", g))
    return out


def _u37(ctx):
    """Unit 37 (R7, R8): first payments 60 days after the first sponsorship (Lean); a day only where the two readings of
    'subject to the variables below' coincide."""
    out = [(Implies(pf("hasfd"), shift(k("fp", P), k("fd", P), _P["prob"])), f"fp_{P}")]
    for m in ctx.of("mon"):
        out += pos("fst", m, no_later(k("ps", m), k("fp", P)))
        out += neg("fst", m, before(k("fp", P), k("ps", m)))
        out.append((Implies(And(U("paid", m), U("fst", m), same_day(k("nx", P), k("fp", P)) if _P["first_open"] else None),
                            Eq(k("pdy", m), k("fp", P))),
                    f"pdy_{m}"))
    out.append((Implies(And(pf("sc"), Not(pf("fmv")), same_day(k("nx", P), k("fp", P))), Eq(k("fpd", P), k("fp", P))),
                f"fpd_{P}"))
    return out


def _sched(ctx):
    out = []
    for m in ctx.of("mon"):
        out.append((Implies(Not(U("mv", m)), Eq(k("sd", m), k("ps", m))), f"sd_{m}"))
        out.append((Implies(U("mv", m), Eq(k("sd", m), k("mvd", m))), f"sd_{m}"))
    return out


def _u38(ctx):
    """Unit 38 (R6, R7): Stripe Connect: the 22nd (bridged), regardless of the amount; a stated move; a stated
    cross-border minimum compared with "the balance accrued since the last payout" (sbal: carried while unpaid, reset
    at each payout; unknown carry -> no balance -> OPEN)."""
    out = _sched(ctx)
    for m in ctx.of("mon"):
        pm = ctx.prev(m)
        out.append((Implies(U("chs", m), Eq(k("sbal", m), k("sdp", m))), f"sbal_{m}"))
        if pm is not None:
            out.append((Implies(And(Not(U("chs", m)), U("paid", pm)), Eq(k("sbal", m), k("sdp", m))), f"sbal_{m}"))
            out.append((Implies(And(Not(U("chs", m)), Not(U("paid", pm))),
                                Eq(k("sbal", m), add(USD, k("sbal", pm), k("sdp", m)))), f"sbal_{m}"))
        cmp = "sbal" if _P["xb_carry"] else "sdp"
        out += pos("paid", m, pf("sc"), Not(U("xbm", m)))
        out += pos("paid", m, pf("sc"), U("xbm", m), Le(k("mn", m), k(cmp, m)))
        out += neg("paid", m, pf("sc"), U("xbm", m), Lt(k(cmp, m), k("mn", m)))
    return out


def _u39(ctx):
    """Unit 39 (R6): ACH / wire: the third Thursday (bridged); $100 without matching money, accrual, leaving."""
    out = []
    thr = usd(_P["thr"])
    for m in ctx.of("mon"):
        pm = ctx.prev(m)
        out += both(None, U("chs", m), "accr", m)
        if pm is not None:
            out += pos("accr", m, Not(U("chs", m)), Not(U("paid", pm)))
            out += neg("accr", m, Not(U("chs", m)), U("paid", pm))
            out.append((Implies(And(Not(U("chs", m)), U("paid", pm)), Eq(k("bal", m), k("tb", m))), f"bal_{m}"))
            out.append((Implies(And(Not(U("chs", m)), Not(U("paid", pm))), Eq(k("bal", m), add(USD, k("bal", pm), k("tb", m)))),
                        f"bal_{m}"))
        out.append((Implies(U("chs", m), Eq(k("bal", m), k("tb", m))), f"bal_{m}"))
        out += pos("paid", m, AW, Not(pf("othr")), Lt(thr, k("bal", m)))
        out += pos("paid", m, AW, Not(pf("othr")), Le(thr, k("bal", m)), Not(U("accr", m)) if _P["accr_open"] else None)
        out += pos("paid", m, AW, U("left", m))
        out += neg("paid", m, AW, Not(pf("othr")), Lt(k("bal", m), thr), Not(U("left", m)))
    return out


def _u41(ctx):
    """Unit 41 (R8): after termination: the last day of the recognition month (bridged) + 90 days (Lean)."""
    return [(Implies(pf("term"), shift(k("tr", P), k("rl", P), _P["post"])), f"tr_{P}")]


def _u42(ctx):
    """Unit 42 (R12): Stripe may combine Sponsored Developer Payments owed to the developer."""
    out = []
    for g in ctx.of("gh"):
        out += pos("ghmay", g, U("scomb", g))
    return out


def _u43(ctx):
    """Unit 43 (R12): outside the United States GitHub may convert USD to the local currency."""
    out = []
    for g in ctx.of("gh"):
        out += pos("ghmay", g, U("gconv", g), Not(pf("us")))
    return out


def _u44(ctx):
    """Unit 44 (R11, R12): the developer specifies refund terms; GitHub never supports or pays refunds."""
    out = _duty("drefund")(ctx)
    for g in ctx.of("gh"):
        out += neg("ghwill", g, U("grefund", g))
    return out


def _u45(ctx):
    """Unit 45 (R11, R12): financial, tax and banking information required; on failure GitHub can deduct bank fees,
    can terminate, and payments may be forfeited."""
    out = _duty("dfin")(ctx)
    for g in ctx.of("gh"):
        for f in ("gbank", "gterm", "gforf"):
            out += pos("ghmay", g, U(f, g), pf("fail"))
    return out


def _checks(ctx):
    """Entry 0 (encoder checks, no unit): each payment or deduction lies in its month; payments in day order."""
    out = []
    for y in ctx.of("pay") + ctx.of("ded"):
        m = ctx.parent[y]
        out.append((And(no_later(k("mf", m), k("dy", y)), no_later(k("dy", y), k("ml", m))), None))
    pays = ctx.of("pay")
    for a, b in zip(pays, pays[1:]):
        out.append((no_later(k("dy", a), k("dy", b)), None))
    return out


def _nothing(ctx):
    return []


UNITS = {
    0: ("RULE", _checks, "entry 0: the encoder's month and order checks"),
    1: ("RULE", _u1, "unit 1: a payer of a sponsorship or subscription through the Program is a Sponsor (R13)"),
    2: ("RULE", _u2, "unit 2: a Sponsored Developer (R13)"),
    3: ("RULE", _u3, "unit 3: a payment through the Program and Stripe is a Sponsorship (R13)"),
    4: ("PART", _u4, "other:judgment standard", "unit 4: a payment for a Subscription offer; 'in exchange for goods, "
        "services, or other offers' is the stated kind of the payment (R13)"),
    5: ("PART", _u5, "cross-reference", "unit 5: the month's net in Lean (R1); 'other Exclusions as outlined in Section 4' "
        "applies none (D3); 'Matching Funds' read as the Matching Fund money (D2(d)); two outcomes with unit 22 OPEN "
        "(D6(d))"),
    6: ("PART", _u6, "cross-reference", "unit 6: the US minimum 13 written; another country's minimum age law, the "
        "Acceptable Use section and the GitHub Policies are stated outside outcomes (R9)"),
    7: ("PART", _u7, "other:judgment standard", "unit 7: 'can collect verification information' stated; age 13 without "
        "it OPEN (D6(c), R9)"),
    8: ("RULE", _u8, "unit 8: the lead-in of units 9-15; closure (R10)"),
    9: ("PART", _ban("fraud"), "cross-reference", "unit 9: fraud and ransom written; violations of intellectual property "
        "and 'other illegal purposes' are stated outside outcomes (R10)"),
    10: ("PART", _ban("reasons", "misrep"), "other:judgment standard", "unit 10: 'misrepresentation or deception' stated, "
         "guarded by representations about the reasons (R10)"),
    11: ("RULE", lambda ctx: _ban("crypto")(ctx) if _P["crypto"] else [], "unit 11: cryptocurrency (R10)"),
    12: ("RULE", _ban("secur"), "unit 12: securities, equity, investment offers (R10)"),
    13: ("PART", lambda ctx: _ban("sellpi")(ctx) + _ban("pilaw")(ctx), "cross-reference",
         "unit 13: sale of personal information written; 'in violation of any laws' a stated outside outcome (R10)"),
    14: ("PART", _ban("gamble"), "other:judgment standard", "unit 14: the listed schemes are the act's stated kind; "
         "'deceptive', 'attempts to game' read from the case's description (R10)"),
    15: ("PART", _ban("sanct"), "cross-reference", "unit 15: 'not permitted under U.S. and other economic sanctions under "
         "applicable law' a stated outside outcome (R10)"),
    16: ("PART", _u16, "other:judgment standard", "unit 16: review before 1 January 2020 (an individual), organizations "
         "out, organization sponsorship not matched; 'not all eligible ... will receive matching' stated (R3, R13)"),
    17: ("PART", _u17, "other:judgment standard", "unit 17: 'case-by-case' a stated approval (R3)"),
    18: ("PART", _u18, "other:judgment standard", "unit 18: 'actively contributing to OSS' stated; one account (R3, R4)"),
    19: ("PART", _u19, "other:judgment standard", "unit 19: GitHub's determination 'in our sole discretion' stated (R3)"),
    20: ("RULE", _u20, "unit 20: no matching from an account with a published Sponsors profile (R4)"),
    21: ("PART", _u21, "other:judgment standard", "unit 21: GitHub's right written; its use 'for any reason' stated (R3, R12)"),
    22: ("PART", _u22, "date/age arithmetic", "unit 22: the period's last day bridged (the same date 12 months later; "
         "29 February OPEN); the equal match (the brief's stated reading) and the $5,000 total in Lean; no GitHub fee in "
         "the period; 'may charge a nominal processing fee' in the future not carried (R2, R5)"),
    23: ("PART", _u23, "deadline/time limit", "unit 23: a stopped sponsorship and a chargeback before the Sponsored "
         "Developer Payment date (read as the month's payout day, R7: OPEN when that day is) (R4)"),
    24: ("PART", _u24, "other:judgment standard", "unit 24: GitHub's choice to count the gap or let the period expire "
         "stated (R2)"),
    25: ("PART", _u25, "other:judgment standard", "unit 25: 'potential policy violation' and 'found to be in violation' "
         "stated (R12)"),
    26: ("PART", _u26, "other:norm", "unit 26: the three duties and responsibility carried as required items (R11); 'You "
         "will' carried as a classification, not a norm"),
    27: ("PART", _u27, "other:norm", "unit 27: entry needs registration and acceptance; true identity required; 'may be "
         "required to register with the payment service provider(s)' and the Privacy Statement not carried (R11, R13)"),
    28: ("NOT", None, "other:norm", "unit 28: GitHub 'may provide' options and the developer 'agree[s] to the terms that "
         "apply to that option': permissions and agreement to outside terms, no outcome a case can ask"),
    29: ("NOT", None, "cross-reference", "unit 29: 'GitHub will pay you the Subscription Sponsorship as provided in "
         "Section 4' (out of scope, D3); the developer's responsibility for the offer's nature is description"),
    30: ("PART", _u30, "other:norm", "unit 30: donations not in Sponsored Developer Payments (R1), no claim against GitHub, "
         "merchant account required for them; 'You are responsible for compliance with any third-party ... agreements' "
         "not carried"),
    31: ("PART", _u31, "other:norm", "unit 31: 'should not be advertising or promotional marketing' not carried (OPEN, "
         "R10); a prohibited advertising agreement forbidden (stated outside outcome); advertising laws required"),
    32: ("PART", _u32, "other:norm", "unit 32: GitHub does not transmit funds (R12); Stripe's control of timing and "
         "method is description"),
    33: ("NOT", None, "other:norm", "unit 33: lead-in 'The following amounts are not included ... or may be withheld': "
         "its items (34-35) are written on their own; no outcome of its own (D11)"),
    34: ("RULE", _u34, "unit 34: expenses borne by the developer; no reimbursement or advance (R11, R12)"),
    35: ("PART", _u35, "other:judgment standard", "unit 35: 'suspected breach', 'reasonable investigation' and 'sole "
         "discretion' stated (R12)"),
    36: ("PART", _u36, "date/age arithmetic", "unit 36: the month's last day bridged; + 30 days in Lean; the payout day "
         "with units 38/39 (D6(a), R7); 'Payouts are sent ... to the bank account you provided' not carried"),
    37: ("PART", _u37, "date/age arithmetic", "unit 37: + 60 days in Lean; the coinciding 22nd / third Thursday bridged; "
         "'subject to the variables below' two readings (D6(a), R7)"),
    38: ("PART", _u38, "date/age arithmetic", "unit 38: the 22nd of the next month bridged; moved days and the cross-border "
         "minimum stated (D10, R6, R7); the minimum compared with the balance accrued since the last payout (Lean)"),
    39: ("PART", _u39, "date/age arithmetic", "unit 39: the third Thursday bridged; $100 without matching money, accrual "
         "and leaving in Lean; exactly $100 after an accrual OPEN (D6(b), R6)"),
    40: ("NOT", None, "other:no outcome", "unit 40: pooled funds keep the same schedule (carried by R1's inclusion); the "
         "immediate transfer 'subject to standard Stripe Connect settlement timing as determined by Stripe' gives no day; "
         "'GitHub does not control' is description"),
    41: ("PART", _u41, "date/age arithmetic", "unit 41: the recognition month's last day bridged; + 90 days in Lean "
         "('approximately 90 days' read as 90, the brief's stated reading)"),
    42: ("PART", _u42, "cross-reference", "unit 42: thresholds, methods and timeframes of 'GitHub's then-current payment "
         "policies' are stated outside outcomes (another threshold: OPEN, R6); Stripe may combine (R12)"),
    43: ("PART", _u43, "other:norm", "unit 43: GitHub may convert outside the US (R12); 'our then-current conversion "
         "rates' outside: no converted amount"),
    44: ("RULE", _u44, "unit 44: refund terms the developer's; GitHub neither supports nor pays refunds (R11, R12)"),
    45: ("PART", _u45, "other:norm", "unit 45: information required (R11); on failure GitHub can deduct bank fees, can "
         "terminate, payments may be forfeited (R12); 'We will notify you ... of changes' not carried"),
}
assert sorted(UNITS) == list(range(46)), sorted(set(range(46)) - set(UNITS))


def units_table(mutant=None):
    return dict(UNITS)


def rules(ctx, mutant=None):
    """Ground rules for a sub-case: [{"id", "unit", "formula", "defines"}]; a formula grounded by two units is kept once."""
    global _P
    _P = dict(PARAM)
    if mutant is not None:
        _P.update(MUTANTS[mutant][1])
    out, seen = [], set()
    try:
        for n, e in sorted(units_table(mutant).items()):
            if e[1] is None:
                continue
            for i, (f, target) in enumerate(e[1](ctx)):
                kk = key([f, target])
                if kk in seen:
                    continue
                seen.add(kk)
                out.append({"id": f"u{n}.{i}", "unit": n, "formula": f, "defines": [] if target is None else [target]})
    finally:
        _P = dict(PARAM)
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
        consts[x] = {"sort": "item", "description": f"The case's {kind} item {x}.", "verbalisation": f"{kind} {x}"}
    for name in sorted(used or ()):
        base, x = name.split("_", 1)
        u, w = BASES[base]
        consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                        "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**ALL_FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The developer, a month, a payment, a deduction, an act, a "
                                                             "duty item or a GitHub act of the case."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      AGE: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
                      USD: {"scale": "100", "display": {"kind": "money", "currency": "USD", "input_symbol": "$"}}}}


# --- planted errors (run.py --mutants, smoke_test.py): each must change at least one answer ------------------------

MUTANTS = {
    "M1": ("CAP: the $5,000 matching total read as $4,000", {"cap": "4000.00"}),
    "M2": ("WINDOW: 'within 30 days after the close' read as 31 days", {"win": 31}),
    "M3": ("PROBATION: '60 days after the first sponsorship' read as 59", {"prob": 59}),
    "M4": ("AFTER TERMINATION: 'approximately 90 days' read as 89", {"post": 89}),
    "M5": ("THRESHOLD: the ACH/wire $100 read as $10", {"thr": "10.00"}),
    "M6": ("AGE: the US minimum age 13 read as 12", {"usmin": 12}),
    "M7": ("AGE: 'under 18' read as under 19", {"adult": 19}),
    "M8": ("REVIEW: 'before January 1, 2020' read as before 1 January 2021", {"jan2020": "2021-01-01"}),
    "M9": ("DONATION: a donation to the developer's merchant account read as part of the payment", {"don_inc": True}),
    "M10": ("THRESHOLD: matching money counted toward the $100", {"mf_thr": True}),
    "M11": ("NET: deductions not subtracted from the month's payment", {"deduct": False}),
    "M12": ("ORGANIZATION: a sponsorship from an organization read as matched", {"org_no": False}),
    "M13": ("PROFILE: a sponsorship from an account with a Sponsors profile read as matched", {"prof_no": False}),
    "M14": ("CHARGEBACK: 'before the Sponsored Developer Payment date' read as after it", {"cb_before": False}),
    "M15": ("REJOIN: an expired matching period read as continuing after rejoining", {"expire": False}),
    "M16": ("CRYPTO: the cryptocurrency ban dropped", {"crypto": False}),
    "M17": ("ACCRUAL: exactly $100 after an accrual read as paid (D6(b) dropped)", {"accr_open": False}),
    "M18": ("FIRST PAYMENTS: 'subject to the variables below' dropped (the 60th day always the payout day)",
            {"first_open": False}),
    "M19": ("CARRY: the cross-border minimum compared with the month's own payment, not the balance accrued since the "
            "last payout (the frozen 5336e71bbc reading)", {"xb_carry": False}),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
