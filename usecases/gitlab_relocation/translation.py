"""GitLab handbook 'Relocation / Address Change' (statute corpus batch 5, NON-STATUTE (a) company staff policy: where staff may
live and work): the VE translation, ONE pass with today's language. CROSS-FAMILY questions (Codex writer), Opus translator.

Row statute-corpus-gitlab-relocation-1125 (dri-statute-corpus-gitlab-relocation-tr-1125, Opus 5.5). Written from the pinned
source ONLY (manage-agents reviews/spare/statute-corpus/batch5/gitlab-relocation/source.txt, sha256 303fe44c...481f, CC BY-SA
4.0, page commit 03f49b80) and its 34 units (units.jsonl, sha256 b12c5f4f...228a2c). WRITTEN AND FROZEN BEFORE ANY QUESTION
EXISTS (orchestrator order 2026-11-25T10:25Z): no question, key or answer of any writer was read; the Codex writer runs later on
source.txt alone, so its questions stay independent of this file. Scope and the scope decisions D1-D17 are ISOLATION.md's,
fixed before any writer; the readings R1-R16 below are fixed here. Evidence branch: nothing here is a Lean kernel line, a
profile, a refuses pair or a lint change; nothing merges.

UNITS maps each unit n of units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one sub-case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
A builder returns (formula, target) pairs: target is the atom key or constant the formula defines (None = a check).

ONE SUB-CASE = the items one question needs: the team member p, the calendar year y asked about, the places (countries or
regions) the case names, the stays away from the primary location in that year (each a child of its place), a planned stay
(child of its place) for a last-date question, and a relocation request (child of its destination place). Every value is a
stated fact (dates; yes/no facts) or computed in Lean from them. The ONE bridged value is the first anniversary of the start
date (bridge/bridge.py; units of the tenure rule are ledgered "bridged"): the language has day steps (shift_days,
elapsed_days) and no year step.

READINGS (fixed here; refuse when in doubt; D-numbers are ISOLATION.md's):
R1  Days (D9; the brief's counting convention): a stay's days = elapsed days from its first to its last day + 1 (both days
    count); the days outside the primary location in the year = the sum over every stay of the year; the year's days =
    elapsed days from 1 January of the year to 1 January of the next (365 or 366, Lean's calendar); the days in the primary
    location = the year's days minus the days outside (every day not in a stated stay is in the primary location). Every stay
    must lie inside the year (a check: a stay outside it makes the facts contradict a rule, refused).
R2  The residence rule (units 6, 8; D3): condition A = days in the primary location >= 183; condition B = days outside <= 183.
    The rule is met when A and B both hold, not met when both fail; where exactly one holds (a 365-day year with 183 days
    outside) two outcomes at once: no answer. "at least half of the time worked" adds no other outcome (D3).
R3  Largest number of days outside (Q2; D3): by A it is the year's days - 183, by B it is 183; answered only when the two
    agree (a leap year: 183); a 365-day year: no answer. The last day a planned stay can end without going over the limit =
    its first day + (that largest number - the days already outside - 1), answered only when the largest number is
    answered, at least one day remains and the last day falls in the year.
R4  Working outside the primary location (units 7, 13, 16, 18, 8, 10): working from a stay's place is NOT permitted when the
    place is US-embargoed (16), when the manager has not approved that stay (7: "required to obtain manager approval ...
    regardless of the length of time"; a stated judgment, D11), when the place requires prior GitLab notice (or approval)
    and it was not given (18), or when the team member was hired in a role requiring time zone alignment and cannot fulfil
    it from the stay (13). It IS permitted only when none of these holds AND the year's residence rule is met (R2) AND the
    role is not stated to require presence in the hired location (7: "certain roles require", no outcome of its own) AND the
    stay is not under a digital nomad visa in a country where GitLab has an established entity (10: "may be prohibited", no
    outcome: blocks the yes only). The stays of a year are permitted when the residence rule is met and every stay is
    permitted; not permitted when the residence rule is not met or some stay is not permitted.
R5  Company-owned devices (16): not permitted to a US-embargoed place; permitted to any other place whose prior notice or
    approval requirement (18) is met ("allows its team members to work from most places globally"; the embargo is the only
    device restriction the text states). A requirement not met: no answer on the device.
R6  US-embargoed (16, 24; D6): a place is US-embargoed when it is one the text names (Cuba, Iran, North Korea, Syria, Russia,
    Belarus, the Crimea, Donetsk and Luhansk regions of Ukraine) or the case states it is on the U.S. embargoed country list
    ("includes but not limited to"); not embargoed when it is none of the named and the case states it is not on the list.
    The Federal list (25) is closed ("the following countries"); "Nicaragu,Somalia" is read as Nicaragua and Somalia (D1(d)).
R7  The long-term relocation (units 7, 11, 15, 19; D4): the days in one place in the year = the sum of that place's stays.
    The stay qualifies as a long-term relocation, and the long-term relocation process must be completed, when those days
    are >= 185 or the team member is changing their permanent location to that place (19: "establish yourself in a new
    location"); neither when the days are <= 181, the permanent location is not changing and the mail will not go to an
    address in the new place. 182-184 days: two outcomes at once (6 months vs 183 days): no answer. Mail to a new address
    alone (19: "please follow the steps") gives no answer.
R8  Short-term stay (units 11-14; D4, D13): a stay is short-term when the long-term NO conditions of R7 hold and not
    short-term when the long-term YES conditions hold. A short-term stay that is the team member's own decision and not
    required by GitLab: NOT eligible for the Business Accident Travel Policy and expenses related to the travel may NOT be
    submitted (13); otherwise the text gives no outcome.
R9  The digital nomad compensation rule (11; D4 days only): working in the place more than 183 days -> the compensation and
    employment agreement are updated (yes); 183 days or less in a temporary location (the permanent location not changing)
    -> no change (no).
R10 The relocation request (units 3, 20-26, 29, 31, 33; D5, D7): the request fails each condition below when the condition
    is not met; it is accepted (YES) only when no condition fails AND the case states GitLab's business approval (3, 20, 28;
    stated judgment); not accepted (NO) when some condition fails or the case states GitLab does not give business approval.
    Conditions (the Q3 labels): (a) "a formed entity open for hiring with no hiring restrictions or headcount cap" (22, 29);
    (b) "a possible new entity must be formally established, open for hiring and its business objectives fully understood"
    (23; fails only where a new entity is stated to be only a possibility); (c) "not a US-embargoed location" (24, R6);
    (d) "Trade Compliance Counsel approval for a GitLab Federal team member to a listed country" (25); (e) "eligibility to
    work without visa sponsorship provided by GitLab" (26); (f) "the appropriate right to work documentation/visa" (31);
    (g) "the one year tenure" (33, R12); (h) "business approval" (3).
R11 The Netherlands (26, 31, 32, 34; D5): (e) fails for a destination other than the Netherlands when the team member cannot
    establish eligibility without GitLab's sponsorship; for the Netherlands without it, two outcomes at once: no answer
    (no "the specific beats the general" reading); likewise (f) for the Netherlands without the documentation (the
    sponsorship could supply it). GitLab provides no sponsorship or immigration aid for a relocation outside the
    Netherlands (32, 34); for the Netherlands the text gives two outcomes ("only sponsors relocations to the Netherlands"
    vs "cannot assist ... if you do not already have that eligibility"): no answer. GitLab does not cover the relocation
    costs of the team member's family members (32), for every destination.
R12 Tenure (33; D8): met on a date when the date is on or after the first anniversary of the start date (same day and month
    one year later; bridge/bridge.py; a 29 February start date has no anniversary: refused). Eligible for relocation (29-33,
    "Considerations and Eligibility"): yes when conditions (a)-(g) all hold, no when one fails (business approval is the
    acceptance's, not eligibility's).
R13 Relocating without requesting approval first (5): "required to request an approval to relocate prior to moving": a move
    made without the request first is not permitted (no); the consequences ("could result in") have no outcome.
R14 Norms and descriptions (D10): "must", "please", "should", "consider", "are responsible for", "are encouraged" sentences
    with no classification the questions turn on are not written (ledger other:norm); "could", "may", "typically", "can
    impact", "may affect", "there should be no need" give no answer (ledger other:no outcome).
R15 Stated judgments (D11): the manager's approval of a stay, GitLab's business approval, "business objectives are fully
    understood"; facts the case states, never decided here (STATED_JUDGMENT).
R16 No number from a case's facts is ever a coefficient: every number is a literal of the pinned text (183, 6 months read as
    181/185 by D4, one year by the bridge) or the counting convention's +1.
"""
from __future__ import annotations

import hashlib
import json

DAY, NDAYS = ("day", "elapsed_day")

# base -> (unit, wording); a constant is f"{base}_{item}"; bases carry no "_"
BASES = {
    # year
    "ya": (DAY, "1 January of the year (stated by the year's name)"),
    "yb": (DAY, "1 January of the next year (stated by the year's name)"),
    "yl": (NDAYS, "the days of the year"),
    "out": (NDAYS, "the days outside the primary location in the year"),
    "inn": (NDAYS, "the days in the primary location in the year"),
    "mxa": (NDAYS, "the year's days minus 183"),
    "mx": (NDAYS, "the largest number of days outside the primary location in the year"),
    "rem": (NDAYS, "the days outside the primary location still allowed in the year"),
    # stay
    "sf": (DAY, "the stay's first day (stated)"),
    "sl": (DAY, "the stay's last day (stated)"),
    "sg": (NDAYS, "the elapsed days from the stay's first to its last day"),
    "sn": (NDAYS, "the stay's days (both the first and the last day counted)"),
    # place
    "pd": (NDAYS, "the days in the place in the year"),
    # planned stay
    "ps": (DAY, "the planned stay's first day (stated)"),
    "pg": (NDAYS, "the elapsed days from the planned stay's first day to its last allowed day"),
    "py": (NDAYS, "the elapsed days from the planned stay's first day to 1 January of the next year"),
    "pl": (DAY, "the last day on which the planned stay can end without going over the limit"),
    # person
    "sd": (DAY, "the team member's start date (stated)"),
    "an": (DAY, "the first anniversary of the start date (bridged: bridge/bridge.py)"),
    "tn": (DAY, "the first day the one year tenure is met"),
    # request
    "rd": (DAY, "the date of the relocation request or the date asked about (stated)"),
}
STATED_BASES = ("ya", "yb", "sf", "sl", "ps", "sd", "an", "rd")
STEP_BASES = tuple(b for b in BASES if b not in STATED_BASES)

EMB_NAMES = {"cuba": "Cuba", "iran": "Iran", "nkorea": "North Korea", "syria": "Syria", "russia": "Russia",
             "belarus": "Belarus", "crimea": "the Crimea region of Ukraine", "donetsk": "the Donetsk region of Ukraine",
             "luhansk": "the Luhansk region of Ukraine"}
FED_NAMES = {"afghanistan": "Afghanistan", "belarus": "Belarus", "burma": "Burma (Myanmar)",
             "car": "Central African Republic", "china": "China (PRC)", "drc": "Democratic Republic of Congo (DRC)",
             "eritrea": "Eritrea", "ethiopia": "Ethiopia", "haiti": "Haiti", "iraq": "Iraq", "lebanon": "Lebanon",
             "libya": "Libya", "nicaragua": "Nicaragua", "somalia": "Somalia", "ssudan": "South Sudan", "sudan": "Sudan",
             "venezuela": "Venezuela", "yemen": "Yemen", "zimbabwe": "Zimbabwe"}
NAMES = {**EMB_NAMES, **FED_NAMES, "netherlands": "the Netherlands"}


def is_name(n):
    return "is" + n


FACTS = {
    # place
    **{is_name(n): f"the place is {w}" for n, w in NAMES.items()},
    "onlist": "the place is on the U.S. embargoed country list (stated for a place the text does not name)",
    "ent": "GitLab already has a formed entity in the place",
    "open": "the entity is open for hiring",
    "restr": "the entity has hiring restrictions",
    "cap": "the entity has a headcount cap",
    "newposs": "a new entity in the place is only a possibility, not yet formally established",
    "objund": "the stated judgment: the business objectives of the new entity are fully understood",
    "reqnot": "the place requires prior GitLab notice before traveling to or working from it",
    "reqapp": "the place requires prior GitLab approval before traveling to or working from it",
    "chg": "the team member is changing their permanent location to the place",
    "mail": "the team member will have their mail delivered to an address in the place",
    # person
    "fed": "the team member is a GitLab Federal team member",
    "tzrole": "the team member was hired in a role requiring a time zone alignment",
    "rolereq": "the team member's role requires them to be present in the location for which they were hired",
    # stay
    "mgr": "the stated judgment: the manager approved working outside the primary location for the stay",
    "gnot": "prior GitLab notice was given for the stay",
    "gapp": "prior GitLab approval was given for the stay",
    "canfz": "the team member can fulfil the time zone requirement from the stay",
    "nv": "the stay is under a digital nomad visa",
    "own": "the stay is the team member's own decision",
    "reqg": "the stay is required by GitLab as part of the team member's role",
    # request
    "biz": "the stated judgment: GitLab gives business approval to the relocation",
    "elig": "the team member can establish eligibility to work in the destination without visa sponsorship provided by GitLab",
    "rtw": "the team member has the appropriate right to work documentation/visa for the destination",
    "tcc": "GitLab's Trade Compliance Counsel approved the request",
    "preq": "the team member requested an approval to relocate before moving",
}
STATED_JUDGMENT = ("mgr", "biz", "objund")   # D11
DERIVED = {
    # year
    "resa": "the team member resides in the primary location for at least 183 days in the year",
    "resb": "the days outside the primary location in the year are at most 183",
    "resok": "the team member meets the requirement to reside in the primary location in the year",
    "outok": "the team member may live and work outside the primary location for the stays of the year",
    # place
    "emb": "the place is US-embargoed",
    "fedl": "the place is on the Federal list of unit 25",
    "ltr": "the stay in the place qualifies as a long term relocation",
    "mustltr": "the team member must complete the long-term relocation process for the stay in the place",
    "st": "the stay in the place is a short-term stay",
    "comp": "the stay in the place results in a change to compensation or the employment agreement (digital nomad rule)",
    # stay
    "workok": "the team member may work from the stay's place during the stay",
    "devok": "the team member may take a company-owned device to the stay's place",
    "expok": "the team member may submit expenses related to the travel of the stay",
    "batp": "the team member is eligible to use the Business Accident Travel Policy for the stay",
    # request
    "fent": "the request fails: a formed entity open for hiring with no hiring restrictions or headcount cap",
    "fnew": "the request fails: a possible new entity must be formally established, open for hiring and its business "
            "objectives fully understood",
    "femb": "the request fails: not a US-embargoed location",
    "ffed": "the request fails: Trade Compliance Counsel approval for a GitLab Federal team member to a listed country",
    "felig": "the request fails: eligibility to work without visa sponsorship provided by GitLab",
    "frtw": "the request fails: the appropriate right to work documentation/visa",
    "ften": "the request fails: the one year tenure",
    "fbiz": "the request fails: business approval",
    "ten": "the team member has satisfied the one year tenure on the request date",
    "eligrel": "the team member is eligible for relocation on the request date",
    "acc": "GitLab can accept the relocation request",
    "spons": "GitLab provides visa sponsorship or immigration aid for the relocation",
    "famcost": "GitLab covers the relocation costs of the team member's family members",
    "mvok": "the team member may relocate as they did",
}
CONDITIONS = (("fent", "a formed entity open for hiring with no hiring restrictions or headcount cap"),
              ("fnew", "a possible new entity formally established, open for hiring, business objectives fully understood"),
              ("femb", "not a US-embargoed location"),
              ("ffed", "Trade Compliance Counsel approval for a GitLab Federal team member"),
              ("felig", "eligibility to work without visa sponsorship provided by GitLab"),
              ("frtw", "the appropriate right to work documentation/visa"),
              ("ften", "the one year tenure"),
              ("fbiz", "business approval"))


# --- formula helpers (ve-quantity@1 wire shapes) --------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def nd(v): return ["decimal", NDAYS, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def elapsed(a, b, n): return ["elapsed_days", a, b, n]       # the elapsed days from a to b equal n
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


def Add(unit, terms):
    terms = list(terms)
    if not terms:
        return ["decimal", unit, "0"]
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


# --- the case context -------------------------------------------------------------------------------------------------

class Ctx:
    """items: [(id, kind)]; parent: {child id: parent id}. Kinds: person (p), year (y), place, stay (child of a place),
    plan (a planned stay, child of a place), req (a relocation request, child of its destination place)."""

    def __init__(self, items, parent=None):
        self.items = list(items)
        self.parent = dict(parent or {})
        self.person = "p"

    def of(self, kind):
        return [x for x, kd in self.items if kd == kind]

    def children(self, x, kind=None):
        kinds = dict(self.items)
        return [y for y, p in self.parent.items() if p == x and (kind is None or kinds[y] == kind)]

    def year(self):
        ys = self.of("year")
        return ys[0] if ys else None


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


def _merge(*builders):
    def b(ctx):
        out = []
        for f in builders:
            out += f(ctx)
        return out
    return b


def _nothing(ctx):
    return []


# --- the rules, unit by unit ------------------------------------------------------------------------------------------

def _days(ctx, plus=1):
    """R1: stay days, the year's days, the days outside and in the primary location, the days per place, and the check
    that every stay lies in the year."""
    out = []
    y = ctx.year()
    stays = ctx.of("stay")
    for s in stays:
        out.append((elapsed(k("sf", s), k("sl", s), k("sg", s)), f"sg_{s}"))
        out.append((Eq(k("sn", s), add(NDAYS, k("sg", s), nd(plus))), f"sn_{s}"))
        if y is not None:
            out.append((And(no_later(k("ya", y), k("sf", s)), no_later(k("sf", s), k("sl", s)), before(k("sl", s), k("yb", y))),
                        None))
    if y is not None:
        out.append((elapsed(k("ya", y), k("yb", y), k("yl", y)), f"yl_{y}"))
        out.append((Eq(k("out", y), Add(NDAYS, [k("sn", s) for s in stays])), f"out_{y}"))
        out.append((Eq(add(NDAYS, k("inn", y), k("out", y)), k("yl", y)), f"inn_{y}"))
    for pl in ctx.of("place"):
        ss = ctx.children(pl, "stay")
        if ss or ctx.children(pl, "plan"):
            out.append((Eq(k("pd", pl), Add(NDAYS, [k("sn", s) for s in ss])), f"pd_{pl}"))
    return out


def _residence(ctx, a=183, b_strict=False):
    """R2 (units 6, 8): conditions A and B; the rule met when both hold, not met when both fail."""
    y = ctx.year()
    if y is None:
        return []
    out = both(Le(nd(a), k("inn", y)), Lt(k("inn", y), nd(a)), "resa", y)
    if b_strict:
        out += both(Lt(k("out", y), nd(183)), Le(nd(183), k("out", y)), "resb", y)
    else:
        out += both(Le(k("out", y), nd(183)), Lt(nd(183), k("out", y)), "resb", y)
    out += both(And(U("resa", y), U("resb", y)), And(Not(U("resa", y)), Not(U("resb", y))), "resok", y)
    return out


def _largest(ctx):
    """R3: the largest number of days outside (A and B agree) and a planned stay's last allowed day."""
    y = ctx.year()
    if y is None:
        return []
    out = [(Eq(add(NDAYS, k("mxa", y), nd(183)), k("yl", y)), f"mxa_{y}"),
           (Implies(Eq(k("mxa", y), nd(183)), Eq(k("mx", y), nd(183))), f"mx_{y}"),
           (Eq(add(NDAYS, k("rem", y), k("out", y)), k("mx", y)), f"rem_{y}")]
    for x in ctx.of("plan"):
        out.append((elapsed(k("ps", x), k("yb", y), k("py", x)), f"py_{x}"))
        out.append((Eq(add(NDAYS, k("pg", x), nd(1)), k("rem", y)), f"pg_{x}"))
        out.append((Implies(And(Le(nd(0), k("pg", x)), Lt(k("pg", x), k("py", x))), elapsed(k("ps", x), k("pl", x), k("pg", x))),
                    f"pl_{x}"))
    return out


def _embargo(ctx):
    """R6: US-embargoed places (16, 24) and the Federal list (25)."""
    out = []
    for pl in ctx.of("place"):
        named = [U(is_name(n), pl) for n in EMB_NAMES]
        out += both(Or(*named, U("onlist", pl)), And(*[Not(f) for f in named], Not(U("onlist", pl))), "emb", pl)
        fl = [U(is_name(n), pl) for n in FED_NAMES]
        out += both(Or(*fl), And(*[Not(f) for f in fl]), "fedl", pl)
    return out


def _stay_place(ctx, s):
    pl = ctx.parent.get(s)
    return pl if pl is not None and dict(ctx.items).get(pl) == "place" else None


def _met(req, given):
    """A prior notice / approval requirement met; and not met."""
    return Or(Not(req), given), And(req, Not(given))


def _work(ctx):
    """R4 (units 7, 8, 10, 13, 16, 18): working from a stay's place; the stays of the year."""
    out = []
    y = ctx.year()
    stays = ctx.of("stay")
    for s in stays:
        pl = _stay_place(ctx, s)
        if pl is None:
            continue
        nok, nbad = _met(U("reqnot", pl), U("gnot", s))
        aok, abad = _met(U("reqapp", pl), U("gapp", s))
        tzok, tzbad = Or(Not(pf("tzrole")), U("canfz", s)), And(pf("tzrole"), Not(U("canfz", s)))
        pos = And(Not(U("emb", pl)), U("mgr", s), nok, aok, tzok, Not(pf("rolereq")), Or(Not(U("nv", s)), Not(U("ent", pl))),
                  U("resok", y) if y is not None else FALSE)
        neg = Or(U("emb", pl), Not(U("mgr", s)), nbad, abad, tzbad)
        out += both(pos, neg, "workok", s)
    if y is not None:
        out += both(And(U("resok", y), *[U("workok", s) for s in stays]),
                    Or(Not(U("resok", y)), *[Not(U("workok", s)) for s in stays]), "outok", y)
    return out


def _device(ctx):
    """R5 (unit 16): company-owned devices."""
    out = []
    for s in ctx.of("stay"):
        pl = _stay_place(ctx, s)
        if pl is None:
            continue
        nok, _ = _met(U("reqnot", pl), U("gnot", s))
        aok, _ = _met(U("reqapp", pl), U("gapp", s))
        out += both(And(Not(U("emb", pl)), nok, aok), U("emb", pl), "devok", s)
    return out


def _ltr_conditions(pl, lo=181, hi=185):
    yes = Or(Le(nd(hi), k("pd", pl)), U("chg", pl))
    no = And(Le(k("pd", pl), nd(lo)), Not(U("chg", pl)), Not(U("mail", pl)))
    return yes, no


def _longterm(ctx, lo=181, hi=185):
    """R7 (units 7, 15, 19): the long-term relocation and its process."""
    out = []
    for pl in ctx.of("place"):
        if not (ctx.children(pl, "stay") or ctx.children(pl, "plan")):
            continue
        yes, no = _ltr_conditions(pl, lo, hi)
        out += both(yes, no, "ltr", pl)
        out += both(yes, no, "mustltr", pl)
    return out


def _shortterm(ctx, lo=181, hi=185):
    """R8 (units 11-14): short-term; R8 unit 13's expenses and the Business Accident Travel Policy."""
    out = []
    for pl in ctx.of("place"):
        if not (ctx.children(pl, "stay") or ctx.children(pl, "plan")):
            continue
        yes, no = _ltr_conditions(pl, lo, hi)
        out += both(no, yes, "st", pl)
    for s in ctx.of("stay"):
        pl = _stay_place(ctx, s)
        if pl is None:
            continue
        cond = And(U("st", pl), U("own", s), Not(U("reqg", s)))
        out += both(None, cond, "expok", s)
        out += both(None, cond, "batp", s)
    return out


def _comp(ctx, strict=True):
    """R9 (unit 11): the digital nomad compensation rule, days only."""
    out = []
    for pl in ctx.of("place"):
        if not (ctx.children(pl, "stay") or ctx.children(pl, "plan")):
            continue
        if strict:
            out += both(Lt(nd(183), k("pd", pl)), And(Le(k("pd", pl), nd(183)), Not(U("chg", pl))), "comp", pl)
        else:
            out += both(Le(nd(183), k("pd", pl)), And(Lt(k("pd", pl), nd(183)), Not(U("chg", pl))), "comp", pl)
    return out


def _req_place(ctx, r):
    pl = ctx.parent.get(r)
    return pl if pl is not None and dict(ctx.items).get(pl) == "place" else None


def _cond(ctx, which):
    """R10/R11/R12: the conditions of a relocation request, each as 'fails' (yes) / 'does not fail' (no)."""
    out = []
    for r in ctx.of("req"):
        pl = _req_place(ctx, r)
        if pl is None:
            continue
        nl = U(is_name("netherlands"), pl)
        if which == "fent":
            ok = And(U("ent", pl), U("open", pl), Not(U("restr", pl)), Not(U("cap", pl)))
            bad = Or(Not(U("ent", pl)), Not(U("open", pl)), U("restr", pl), U("cap", pl))
        elif which == "fnew":
            ok = Or(Not(U("newposs", pl)), And(U("ent", pl), U("open", pl), U("objund", pl)))
            bad = And(U("newposs", pl), Or(Not(U("ent", pl)), Not(U("open", pl)), Not(U("objund", pl))))
        elif which == "femb":
            ok, bad = Not(U("emb", pl)), U("emb", pl)
        elif which == "ffed":
            ok = Or(Not(pf("fed")), Not(U("fedl", pl)), U("tcc", r))
            bad = And(pf("fed"), U("fedl", pl), Not(U("tcc", r)))
        elif which == "felig":
            ok, bad = U("elig", r), And(Not(U("elig", r)), Not(nl))
        elif which == "frtw":
            ok, bad = U("rtw", r), And(Not(U("rtw", r)), Not(nl))
        elif which == "ften":
            ok, bad = U("ten", r), Not(U("ten", r))
        elif which == "fbiz":
            ok, bad = U("biz", r), Not(U("biz", r))
        else:
            raise ValueError(which)
        out += both(bad, ok, which, r)
    return out


def _tenure(ctx, on_day=True):
    """R12 (unit 33): the first day the tenure is met (the bridged anniversary) and the tenure on the request date."""
    out = [(Eq(pk("tn"), pk("an")), "tn_p")]
    for r in ctx.of("req"):
        if on_day:
            out += both(no_later(pk("tn"), k("rd", r)), before(k("rd", r), pk("tn")), "ten", r)
        else:
            out += both(before(pk("tn"), k("rd", r)), no_later(k("rd", r), pk("tn")), "ten", r)
    return out


def _acc(ctx):
    """R10: acceptance; R12: eligibility."""
    out = []
    names = [n for n, _ in CONDITIONS]
    for r in ctx.of("req"):
        out += both(And(*[Not(U(n, r)) for n in names]), Or(*[U(n, r) for n in names]), "acc", r)
        el = [n for n in names if n != "fbiz"]
        out += both(And(*[Not(U(n, r)) for n in el]), Or(*[U(n, r) for n in el]), "eligrel", r)
    return out


def _u32(ctx):
    """R11 (units 32, 34): sponsorship only for the Netherlands (no answer there); family costs never covered."""
    out = []
    for r in ctx.of("req"):
        pl = _req_place(ctx, r)
        if pl is None:
            continue
        out += both(None, Not(U(is_name("netherlands"), pl)), "spons", r)
        out += both(None, TRUE, "famcost", r)
    return out


def _u5(ctx):
    """R13 (unit 5): a move without requesting approval first is not permitted."""
    return [rr for r in ctx.of("req") for rr in both(None, Not(U("preq", r)), "mvok", r)]


def _c(which):
    return lambda ctx: _cond(ctx, which)


UNITS = {
    1: ("NOT", None, "other:norm", "unit 1: People Operations manages the process (a description); 'please submit a request "
        "via Compass' is a request with no outcome"),
    2: ("NOT", None, "other:no outcome", "unit 2: 'we want to encourage' and the aspects to consider describe (D1(e))"),
    3: ("PART", _c("fbiz"), "other:norm", "unit 3: 'require business approval' written (condition (h), a stated judgment, "
        "R10); 'Discuss ... and seek business approval before submitting' is a duty with no outcome; what the review "
        "considers is the discretion (stated judgment)"),
    4: ("NOT", None, "other:norm", "unit 4: 'discuss and obtain pre-approval in writing' a process duty; the text gives no "
        "outcome for a request without it"),
    5: ("PART", _u5, "other:norm", "unit 5: 'required to request an approval to relocate prior to moving' written (R13); "
        "'could result in disciplinary action' (no outcome), 'it is important to communicate' (a duty), the repeated "
        "encouragement (a description)"),
    6: ("PART", _merge(_days, _residence), "other:norm", "unit 6: the 183 days in and the maximum 183 days outside written "
        "(R1, R2); GitLab's tax reporting (a description), 'are encouraged to consult', 'contact the People Operations Team "
        "immediately', 'Managers are responsible for ensuring' are duties with no outcome"),
    7: ("PART", _work, "other:norm", "unit 7: manager approval regardless of length written (R4), 'Long-term relocations "
        "... must follow the application' written (R7); 'Managers can deny ... or ask ... to change' is carried only as the "
        "stated decision; 'certain roles require' blocks a yes only (R4); 'could also result in' has no outcome"),
    8: ("PART", _largest, "other:no outcome", "unit 8: the digital nomad permission for a maximum of 183 days and 'must still "
        "reside ... at least 183 days' written (R2-R4); 'Balancing flexibility ... is key' describes"),
    9: ("NOT", None, "other:no outcome", "unit 9: 'could risk' a permanent establishment, 'may be required' (D10)"),
    10: ("NOT", None, "other:norm", "unit 10: 'responsible for understanding' a duty; 'typically granted', 'may be "
         "prohibited', 'may also require' (D10: blocks a yes only, R4)"),
    11: ("PART", _comp, "other:no outcome", "unit 11: more than 183 days -> compensation and agreement updated, 183 days or "
         "less -> no change written (R9); 'qualify as a long term relocation' written with the D4 band (R7); 'can impact "
         "your ability to maintain the ... visa' has no outcome"),
    12: ("NOT", None, "other:norm", "unit 12: 'you are responsible for maintaining your health insurance, visas ...' and "
         "'Consider discussing' are duties with no outcome"),
    13: ("RULE", _shortterm, "unit 13: a short-term stay of the team member's own decision: no Business Accident Travel "
         "Policy, no travel expenses (R8); the time zone requirement in R4"),
    14: ("NOT", None, "other:no outcome", "unit 14: 'there should be no need to update your address' (D10)"),
    15: ("PART", _longterm, "other:no outcome", "unit 15: more than 6 months in one or in aggregate -> residence, must "
         "complete the long-term process written (R7, D4 band); how tax residency is determined in most countries describes "
         "outside law (no GitLab outcome)"),
    16: ("RULE", _merge(_embargo, _device), "unit 16: no company-owned devices to, no work from, US-embargoed places (R4-R6)"),
    17: ("NOT", None, "other:no outcome", "unit 17: the information is subject to change; 'Additional information can be "
         "found on the Trade Compliance page' (a signpost, not pinned)"),
    18: ("PART", _nothing, "other:norm", "unit 18: prior notice and/or approval written (in R4, R5's rules); 'do not hesitate "
         "to contact the People Team' a request with no outcome"),
    19: ("PART", _nothing, "other:norm", "unit 19: the definition ('establish yourself in a new location') and more than six "
         "months written (R7, in unit 15's rule); 'and/or will have your mail delivered ... please follow the steps' is a "
         "request: mail alone gives no answer"),
    20: ("PART", _nothing, "other:judgment standard", "unit 20: the company's discretion carried only as the stated business "
         "decision (R10, R15)"),
    21: ("NOT", None, "other:judgment standard", "unit 21: roles tied to places are a consideration under the discretion; "
         "no outcome of its own (D7): only the stated business decision answers"),
    22: ("PART", _c("fent"), "cross-reference", "unit 22: a formed entity with no hiring restrictions written (condition (a), "
         "R10); 'Review our Country hiring guidelines to see if the country is eligible' points outside the pinned source "
         "(the entity facts are stated, D12)"),
    23: ("PART", _c("fnew"), "other:judgment standard", "unit 23: a possible new entity must be formally established and open "
         "for hiring written (condition (b)); 'business objectives are fully understood' a stated judgment"),
    24: ("RULE", _c("femb"), "unit 24: no relocation requests to a US-embargoed location (condition (c), R6)"),
    25: ("RULE", _c("ffed"), "unit 25: Federal team members to the listed countries need Trade Compliance Counsel approval "
         "(condition (d))"),
    26: ("RULE", _c("felig"), "unit 26: eligibility to work without GitLab's visa sponsorship (condition (e); the Netherlands "
         "without it: two outcomes, R11)"),
    27: ("NOT", None, "other:judgment standard", "unit 27: the compensation adjustment (increase or decrease) and 'retains "
         "discretion ... due to the required adjustment': only the stated business decision answers (D7)"),
    28: ("NOT", None, "other:norm", "unit 28: 'will need to go through an approval process', the People Group's review after "
         "pre-approval (process duties); the discretion and 'may not be able to support' (stated judgment, no outcome)"),
    29: ("RULE", _c("fent"), "unit 29: only entities open for hiring with no hiring restrictions or headcount caps (condition "
         "(a))"),
    30: ("NOT", None, "other:norm", "unit 30: 'Consider any changes to benefits' a recommendation with no outcome"),
    31: ("RULE", _c("frtw"), "unit 31: the appropriate right to work documentation/visa (condition (f), R11)"),
    32: ("RULE", _u32, "unit 32: sponsorship only to the Netherlands; family members' relocation costs not covered (R11)"),
    33: ("RULE", _merge(_tenure, _c("ften"), _acc), "unit 33: the one year tenure (condition (g), R12; the anniversary is "
         "bridged)"),
    34: ("PART", _nothing, "other:norm", "unit 34: no sponsorship or immigration aid outside the Netherlands written (in unit "
         "32's rule, R11); 'you need to confirm', 'you will need to provide proof ... by uploading' are duties; 'cannot "
         "assist ... if you do not already have that eligibility' against the Netherlands exception (two outcomes, R11); "
         "'free to apply' a permission with no outcome; 'may affect your ability' (no outcome); 'refer to our Visa page' "
         "(a signpost)"),
}
BRIDGED_UNITS = (33,)        # the anniversary of the start date (bridge/bridge.py)
STATED_UNITS = (3, 7, 20, 21, 23, 27)   # carried only through a stated judgment (D11)


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
            "vocabulary": {"sorts": {"item": {"description": "A team member, year, place, stay, planned stay or request."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}}}}


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


def _drop_atom(name, value):
    """Replace every occurrence of the atom 'name' (any item) by TRUE / FALSE in a builder's formulas."""
    rep = json.dumps(TRUE if value else FALSE)

    def wrap(builder):
        def b(ctx):
            out = []
            for f, tg in builder(ctx):
                s = json.dumps(f)
                for x, _ in ctx.items:
                    s = s.replace(json.dumps(U(name, x)), rep)
                out.append((json.loads(s), tg))
            return out
        return b
    return wrap


def _p(fn, **kw):
    return lambda ctx: fn(ctx, **kw)


MUTANTS = {
    "M1": ("THRESHOLD: 'at least 183 days' in the primary location read as at least 182",
           lambda t: {**t, 6: (t[6][0], _merge(_days, _p(_residence, a=182)), *t[6][2:])}),
    "M2": ("THRESHOLD: 'a maximum total of 183 days' outside read as under 183",
           lambda t: {**t, 6: (t[6][0], _merge(_days, _p(_residence, b_strict=True)), *t[6][2:])}),
    "M3": ("COUNT: the stay's days counted without the last day (no +1)",
           lambda t: {**t, 6: (t[6][0], _merge(_p(_days, plus=0), _residence), *t[6][2:])}),
    "M4": ("THRESHOLD: 6 months read as at most 182 days (D4 band's lower edge 181 -> 182)",
           lambda t: {**t, 13: (t[13][0], _p(_shortterm, lo=182), *t[13][2:]),
                      15: (t[15][0], _p(_longterm, lo=182), *t[15][2:])}),
    "M5": ("THRESHOLD: 6 months read as at least 184 days (D4 band's upper edge 185 -> 184)",
           lambda t: {**t, 13: (t[13][0], _p(_shortterm, hi=184), *t[13][2:]),
                      15: (t[15][0], _p(_longterm, hi=184), *t[15][2:])}),
    "M6": ("THRESHOLD: unit 11's 'more than 183 days' read as at least 183",
           lambda t: {**t, 11: (t[11][0], _p(_comp, strict=False), *t[11][2:])}),
    "M7": ("DATE: the tenure met only after the anniversary (not on it)",
           lambda t: {**t, 33: (t[33][0], _merge(_p(_tenure, on_day=False), _c("ften"), _acc), *t[33][2:])}),
    "M8": ("LIST: Russia dropped from the US-embargoed list", _swap(16, _drop_atom("isrussia", False))),
    "M9": ("CONDITION: unit 25's Trade Compliance Counsel approval ignored (Federal list always fails)",
           _swap(25, _drop_atom("tcc", False))),
    "M10": ("CONDITION: the Netherlands exception dropped (eligibility without sponsorship fails there too)",
            _swap(26, _drop_atom("isnetherlands", False))),
    "M11": ("CONDITION: manager approval not required (unit 7)", _swap(7, _drop_atom("mgr", True))),
    "M12": ("CONDITION: unit 18's prior notice requirement dropped", _swap(7, _drop_atom("reqnot", False))),
    "M13": ("CONDITION: the headcount cap dropped from the entity condition", lambda t: _swap(29, _drop_atom("cap", False))(
        _swap(22, _drop_atom("cap", False))(t))),
    "M14": ("CONDITION: business approval not required for acceptance", _swap(3, _drop_atom("biz", True))),
    "M15": ("CONDITION: unit 13's 'your decision and not required by GitLab' dropped", _swap(13, _drop_atom("own", True))),
    "M16": ("CONDITION: the time zone requirement of unit 13 dropped", _swap(7, _drop_atom("tzrole", False))),
}


def tg_item(tg):
    """The item of an atom target key."""
    return json.loads(tg)[2][1]


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
