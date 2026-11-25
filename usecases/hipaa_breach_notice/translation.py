"""HIPAA breach notification, 45 CFR 164.402-164.414 (eCFR 2026-11-20; statute corpus batch 4, regulation, US data security): the
VE translation, one pass with today's language. CROSS-FAMILY questions (Codex writer), Opus translator/encoder.

Row statute-corpus-hipaa-breach-notice (dri-statute-corpus-hipaa-breach-notice-w-1124, Opus 5.5). Written from the pinned source
only (manage-agents reviews/spare/statute-corpus/batch4/hipaa-breach-notice/source.txt, sha256 c49a158d...1bd5), the decisions
D1-D14 of ISOLATION.md and the fixed facts of WRITER-BRIEF.md, BEFORE the encoder's question file (questions-enc.jsonl) was
opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of batch4/hipaa-breach-notice/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Duties and permissions are carried as CLASSIFICATIONS of the stated facts (a yes/no predicate whose definition is the text's
condition: "the covered entity must notify the Secretary of this incident"); a norm that cannot be carried so is other:norm.

ONE CASE = one incident i (the acquisition, access, use or disclosure the case describes). Items (one sort "item"):
  i   the incident (breach, discovery by the covered entity, the covered entity's notices and their latest days);
  s   a State or jurisdiction with residents affected by i (count res_s, stated);
  b   the business associate's side of i (its discovery, its notice to the covered entity);
  k   a person who learned of i on a stated day (role facts; knowers of the covered entity or of the business associate);
  o   a law enforcement official's statement about delaying a notice;
  g   an affected individual (or several alike) whose contact facts a method question asks about;
  e   an element of a notice's content a question asks about.
Days are integers of the unit "day"; counts (residents, individuals with insufficient contact information, days of a posting
or a toll-free number) integers of the unit "count". Every literal below (500, 10, 60, 30, 90, the calendar years) is a
literal of the pinned text or of the calendar; no number from a case is ever a coefficient.

NO BRIDGE: every day step is in Lean: N days after a day (shift_days); the latest of the earliest-known days (unit 7, 22) as
a choice among stated days, each candidate proved with its order conditions; 31 December of the year of discovery from a fixed
calendar table (a calendar year Y runs from 1 January Y to 31 December Y, Y = 2020..2040); the total individuals as the sum of
the stated per-State residents (D8).

READINGS (fixed here, on the text and the brief's fixed facts; refuse when in doubt):
R1  Breach (units 2-4): breach <-> protected health information (stated) AND acquired, accessed, used or disclosed in a manner
    not permitted under subpart E (stated) AND no exclusion of (1) applies AND the risk assessment does NOT demonstrate a low
    probability of compromise (unit 4: "presumed to be a breach unless ... demonstrates"; a case that states no demonstration
    leaves the presumption standing). Exclusion (i): an acquisition, access or use, by a workforce member or a person acting
    under the authority of the covered entity or business associate, unintentional, in good faith and within the scope of
    authority, and no further impermissible use or disclosure. (ii): an inadvertent disclosure by a person authorized to
    access PHI at the covered entity or business associate to another person authorized at the same one or at an organized
    health care arrangement in which the covered entity participates, and no further impermissible use or disclosure.
    (iii): a disclosure where the covered entity or business associate has a good faith belief the unauthorized recipient
    would not reasonably have been able to retain the information. Good faith, inadvertence, retention, low probability:
    stated judgments.
R2  Unsecured (unit 5): PHI not rendered unusable, unreadable or indecipherable by a method of the Secretary's guidance
    (stated as a fact, D2). A breach of unsecured PHI ("bun") is what triggers every notice.
R3  Discovery (units 7, 22): the first day on which the breach is known to (a) the covered entity through a person, other than
    the person committing the breach, who is a workforce member or agent (agency a stated judgment) / (b) the business
    associate through an employee, officer or other agent, not the person committing it; or the stated reasonable-diligence
    day, whichever is earlier. A case may state the discovery day itself instead (D4): then that day.
R4  Latest days (units 8, 16, 23; D6): discovery + 60 (the outer limit; "without unreasonable delay" never moves a date). The
    Secretary (unit 19): 500 or more individuals: contemporaneously with the individual notice = the stated day the
    individual notices were given, if stated and not after their own latest day, else the individuals' latest day; (unit 20)
    fewer than 500: 31 December of the year of discovery + 60.
R5  Who (units 6, 15, 18, 21): bun -> individuals, the Secretary, and media for each State with MORE than 500 residents
    affected; individuals = the sum of the stated per-State residents (D8). The business associate: the covered entity, when
    bun and the business associate discovered the breach. Not bun -> none.
R6  Law enforcement (units 26-28): a statement applies when it says the notice would impede a criminal investigation or cause
    damage to national security. Written AND specifying the time: delay to the stated last day of that time. Oral: document it
    (with the official's identity) and delay to the statement day + 30, unless a written statement specifying the time is
    submitted within that time (on or before the statement day + 30): then to its stated last day. A written statement with
    no time specified and no oral statement: no delay rule applies (no date; refused, D7). An oral statement followed by a
    written one AFTER the 30 days: (a) and (b) give two dates: refused (D11). The latest day of a notice that a qualifying
    statement delays is never answered (D7): refused. A statement covers the notices the case says it concerns.
R7  Methods (units 11-13): written notice by first-class mail to the last known address; by e-mail if the individual agreed
    to electronic notice and has not withdrawn the agreement; a deceased individual known to the covered entity whose next of
    kin's or personal representative's address it has: first-class mail to them. Substitute notice: required where
    insufficient or out-of-date contact information precludes written notice to the (living) individual; not required where
    it is the next of kin's or personal representative's contact information that is insufficient. Fewer than 10 such
    individuals: may be by an alternative form of written notice, telephone or other means; 10 or more: must be a conspicuous
    posting for 90 days on the home page or conspicuous notice in major print or broadcast media, AND include a toll-free
    number active at least 90 days (a stated posting or number period is compared with 90 in Lean).
R8  Content (units 9, 10, 17, 24): an element listed in (c)(1)(A)-(E) must be included when it is possible to include it
    (stated judgment); an element not listed is not required; plain language is required of every notice to individuals and
    (unit 17) the media notice. The business associate's notice: the identification of each individual, to the extent
    possible (stated); other available information the covered entity needs (unit 25): required.
R9  Urgent (unit 14): telephone or other means MAY be used in addition to the written notice when the covered entity deems the
    case urgent (stated judgment); not deemed urgent: no answer.
R10 Log (unit 20): fewer than 500 individuals -> the covered entity must keep a log or other documentation; 500 or more, or no
    bun: not required by these sections.
R11 Administrative requirements (unit 29): the covered entity must comply (the content of 164.530 is not pinned). Burden of
    proof (unit 30): on the covered entity or business associate, as applicable, in the event of a use or disclosure in
    violation of subpart E (stated); not otherwise.
"""
from __future__ import annotations

import hashlib
import json

DAY = "day"
CNT = "count"
YEARS = range(2020, 2041)

INT_UNITS = {  # base -> (unit, words)
    "disc": (DAY, "the day the breach is treated as discovered by the covered entity"),
    "dd": (DAY, "the first day the breach would have been known to the covered entity by exercising reasonable diligence"),
    "li": (DAY, "the latest day for the notice to individuals"),
    "lm": (DAY, "the latest day for the notice to the media"),
    "ls": (DAY, "the latest day for the notice to the Secretary"),
    "ye": (DAY, "31 December of the calendar year in which the breach was discovered"),
    "isd": (DAY, "the day the covered entity gave the notice to individuals (stated)"),
    "tot": (CNT, "the number of individuals involved in the breach"),
    "nins": (CNT, "the number of individuals with insufficient or out-of-date contact information"),
    "pdays": (CNT, "the number of days of the substitute notice's posting"),
    "tdays": (CNT, "the number of days the toll-free number remains active"),
    "res": (CNT, "the number of residents of the State or jurisdiction involved"),
    "bdisc": (DAY, "the day the breach is treated as discovered by the business associate"),
    "bdd": (DAY, "the first day the breach would have been known to the business associate by exercising reasonable "
                 "diligence"),
    "lb": (DAY, "the latest day for the business associate's notice to the covered entity"),
    "kd": (DAY, "the day the person learned of the breach"),
    "od": (DAY, "the day the official made the statement"),
    "pend": (DAY, "the last day of the time specified in the written statement"),
    "fwd": (DAY, "the day a written statement followed the oral one"),
    "fwend": (DAY, "the last day of the time specified in the following written statement"),
    "l30": (DAY, "the day 30 days from the date of the oral statement"),
    "dly": (DAY, "the latest day to which the notice may be delayed"),
}
BASES_OF = {"incs": ("disc", "dd", "li", "lm", "ls", "ye", "isd", "tot", "nins", "pdays", "tdays"),
            "states": ("res",), "bas": ("bdisc", "bdd", "lb"), "knows": ("kd",),
            "stmts": ("od", "pend", "fwd", "fwend", "l30", "dly")}
FACTS = {
    # incident
    "phi": "the information is protected health information",
    "notperm": "the acquisition, access, use or disclosure was in a manner not permitted under subpart E",
    "guid": "the information was rendered unusable, unreadable or indecipherable to unauthorized persons through a technology "
            "or methodology specified by the Secretary in the guidance",
    "acq": "the incident is an acquisition, access or use of the information",
    "dsc": "the incident is a disclosure of the information",
    "wf": "the person is a workforce member or a person acting under the authority of the covered entity or business associate",
    "unint": "the acquisition, access or use was unintentional",
    "gfs": "it was made in good faith and within the scope of authority (stated judgment)",
    "further": "it resulted in further use or disclosure in a manner not permitted under subpart E",
    "inadv": "the disclosure was inadvertent (stated judgment)",
    "authfrom": "the person disclosing is authorized to access protected health information at the covered entity or business "
                "associate",
    "authto": "the recipient is authorized to access protected health information at the same covered entity or business "
              "associate, or organized health care arrangement in which the covered entity participates",
    "gfret": "the covered entity or business associate has a good faith belief that the unauthorized recipient would not "
             "reasonably have been able to retain the information (stated judgment)",
    "lowprob": "the risk assessment of at least the four factors demonstrates a low probability that the information has been "
               "compromised (stated judgment)",
    "hasdd": "a reasonable-diligence day is stated for the covered entity (stated judgment)",
    "hasisd": "the day the covered entity gave the notice to individuals is stated",
    "urg": "the covered entity deems the case to require urgency because of possible imminent misuse (stated judgment)",
    "hasnins": "the number of individuals with insufficient or out-of-date contact information is stated",
    "post": "a substitute notice posting period is stated",
    "tfree": "a toll-free number period is stated",
    # business associate
    "bknow": "the business associate discovered (learned of) the breach",
    "hasbdd": "a reasonable-diligence day is stated for the business associate (stated judgment)",
    "bidpos": "identifying each affected individual was possible for the business associate (stated judgment)",
    # knower
    "kce": "the person is a workforce member or agent of the covered entity (agency: stated judgment)",
    "kba": "the person is an employee, officer or other agent of the business associate",
    "kcom": "the person committed the breach",
    # statement
    "purp": "the official stated the notice would impede a criminal investigation or cause damage to national security",
    "wr": "the statement was in writing",
    "per": "the written statement specifies the time for which a delay is required (to the day pend)",
    "oral": "the statement was made orally",
    "fw": "a written statement followed the oral statement (on the day fwd)",
    "fwper": "the following written statement specifies the time for which a delay is required (to the day fwend)",
    "ab_ind": "the statement concerns the notice to individuals",
    "ab_med": "the statement concerns the notice to the media",
    "ab_sec": "the statement concerns the notice to the Secretary",
    "ab_ba": "the statement concerns the business associate's notice to the covered entity",
    # individual (group)
    "dec": "the covered entity knows the individual is deceased",
    "nokad": "the covered entity has the address of the next of kin or personal representative",
    "agr": "the individual agreed to electronic notice",
    "wdr": "the individual withdrew that agreement",
    "ins": "insufficient or out-of-date contact information precludes written notification to the individual",
    "nokins": "insufficient or out-of-date contact information precludes written notification to the next of kin or "
              "personal representative",
    # element
    "lst": "the element is one the notice to individuals must include under (c)(1)(A)-(E)",
    "pos": "it is possible to include the element (stated judgment)",
    "emed": "the element is asked of the notice to the media",
    "ecnt": "the contact procedures include a toll-free number, an e-mail address, Web site or postal address",
    "ectq": "the question is whether the contact procedures meet (c)(1)(E)'s list",
}
STATED = ("gfs", "inadv", "gfret", "lowprob", "hasdd", "hasbdd", "urg", "kce", "bidpos", "pos")
DERIVED_UNARY = {
    "ex1": "exclusion (1)(i) applies", "ex2": "exclusion (1)(ii) applies", "ex3": "exclusion (1)(iii) applies",
    "excl": "the incident is excluded from breach",
    "breach": "the incident is a breach",
    "uns": "the information is unsecured protected health information",
    "bun": "the incident is a breach of unsecured protected health information the covered entity must notify",
    "ind": "the covered entity must notify the affected individuals",
    "sec": "the covered entity must notify the Secretary",
    "media": "the covered entity must notify prominent media outlets serving the State",
    "anym": "the covered entity must notify the media of some State",
    "big": "the breach involves 500 or more individuals",
    "ndi": "no applicable law enforcement statement delays the notice to individuals",
    "ndm": "no applicable law enforcement statement delays the notice to the media",
    "nds": "no applicable law enforcement statement delays the notice to the Secretary or to individuals",
    "ndb": "no applicable law enforcement statement delays the business associate's notice",
    "baduty": "the business associate must notify the covered entity",
    "dlyapp": "the statement requires the notice to be delayed",
    "docreq": "the covered entity or business associate must document the oral statement, including the official's identity",
    "plain": "the notice must be written in plain language",
    "logreq": "the covered entity must maintain a log or other documentation of the breach",
    "urgok": "the covered entity may provide information by telephone or other means in addition to the written notice",
    "burden": "the covered entity or business associate has the burden of demonstrating the notifications were made or there "
              "was no breach",
    "admin": "the covered entity must comply with the administrative requirements of 164.530 for this subpart",
    "mailok": "written notification by first-class mail to the individual at the last known address is a form the text gives",
    "emailok": "notification by electronic mail is a form the text allows",
    "nokreq": "written notification by first-class mail to the next of kin or personal representative is the form required",
    "substreq": "a substitute form of notice must be provided to the individual",
    "altok": "the substitute notice may be by an alternative form of written notice, telephone or other means",
    "wmreq": "the substitute notice must be a conspicuous web posting for 90 days or conspicuous notice in major media",
    "tfreq": "the substitute notice must include a toll-free number active at least 90 days",
    "postok": "the stated posting period meets the 90 days",
    "tfok": "the stated toll-free number period meets the 90 days",
    "inclreq": "the notice must include the element",
    "contactok": "the stated contact procedures meet (c)(1)(E)",
    "bidreq": "the business associate's notice must include the identification of each affected individual",
    "binforeq": "the business associate must provide the covered entity with the other available information",
}


# --- formula helpers (ve-quantity@1 wire shapes; fmla_eligibility / wmf conventions) ---------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]       # a is n days after b
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def Eq(a, b): return ["eq", a, b]
def cnt(v): return ["decimal", CNT, str(v)]
def date(v): return ["date", v]
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


def iff_u(p, x, body): return Iff(U(p, x), body)
def yes(cond, p, x): return Implies(cond, U(p, x))
def no(cond, p, x): return Implies(cond, Not(U(p, x)))


def add_all(terms):
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = ["add", CNT, t, r]
    return r


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """incs: [i]; the other kinds map an item to its incident (or, for knowers, to ("ce"|"ba", incident))."""
    KINDS = ("states", "bas", "knows", "stmts", "groups", "elems")

    def __init__(self, incs=("i",), states=None, bas=None, knows=None, stmts=None, groups=None, elems=None):
        self.incs = list(incs)
        self.states, self.bas, self.knows = dict(states or {}), dict(bas or {}), dict(knows or {})
        self.stmts, self.groups, self.elems = dict(stmts or {}), dict(groups or {}), dict(elems or {})

    @property
    def items(self):
        return self.incs + [x for kd in self.KINDS for x in getattr(self, kd)]

    def of(self, kind, i):
        return [x for x, j in getattr(self, kind).items() if j == i]

    def ba_of(self, i):
        bs = self.of("bas", i)
        return bs[0] if bs else None


def per_inc(fn):
    return lambda ctx: [f for i in ctx.incs for f in fn(i, ctx)]


def per(kind, fn):
    return lambda ctx: [f for x, i in getattr(ctx, kind).items() for f in fn(x, i, ctx)]


# --- the units ----------------------------------------------------------------------------------------------------

def _breach(i, ctx):
    """Units 2, 4 (R1): breach <-> PHI, not permitted under subpart E, not excluded, no low probability demonstrated."""
    return [iff_u("breach", i, And(U("phi", i), U("notperm", i), Not(U("excl", i)), Not(U("lowprob", i))))]


def _excl(i, ctx):
    """Unit 3 (R1): the three exclusions."""
    return [iff_u("ex1", i, And(U("acq", i), U("wf", i), U("unint", i), U("gfs", i), Not(U("further", i)))),
            iff_u("ex2", i, And(U("dsc", i), U("inadv", i), U("authfrom", i), U("authto", i), Not(U("further", i)))),
            iff_u("ex3", i, And(U("dsc", i), U("gfret", i))),
            iff_u("excl", i, Or(U("ex1", i), U("ex2", i), U("ex3", i)))]


def _uns(i, ctx):
    """Unit 5 (R2): unsecured PHI; a breach of unsecured PHI."""
    return [iff_u("uns", i, And(U("phi", i), Not(U("guid", i)))),
            iff_u("bun", i, And(U("breach", i), U("uns", i)))]


def _ind(i, ctx):
    """Unit 6 (R5): the covered entity notifies each affected individual."""
    return [iff_u("ind", i, U("bun", i))]


def _earliest(target, cands):
    """cands: [(condition, day term)]: target = the earliest day among those whose condition holds (each candidate with its
    order conditions; ties give the same day)."""
    out = []
    for n, (cond, d) in enumerate(cands):
        others = [Implies(c2, no_later(d, d2)) for m, (c2, d2) in enumerate(cands) if m != n]
        out.append(Implies(And(cond, *others), Eq(target, d)))
    return out


def _disc(i, ctx):
    """Unit 7 (R3): treated as discovered by the covered entity: the first day known to a workforce member or agent (not the
    person committing the breach), or the reasonable-diligence day if earlier."""
    cands = [(And(U("kce", kk), Not(U("kcom", kk))), k("kd", kk)) for kk, (side, j) in ctx.knows.items()
             if j == i and side == "ce"]
    cands.append((U("hasdd", i), k("dd", i)))
    return _earliest(k("disc", i), cands)


def _li(i, ctx):
    """Unit 8 (R4, D6): no later than 60 calendar days after discovery (the outer limit)."""
    return [shift(k("li", i), k("disc", i), 60)]


def _content(e, i, ctx):
    """Unit 9 (R8): an element of (c)(1)(A)-(E) must be included to the extent possible; (E)'s four contact means."""
    ok = And(U("bun", i), Not(U("emed", e)))
    return [yes(And(ok, U("lst", e), U("pos", e)), "inclreq", e),
            no(Not(U("lst", e)), "inclreq", e),
            no(And(U("lst", e), Not(U("pos", e))), "inclreq", e),
            yes(And(U("ectq", e), U("ecnt", e)), "contactok", e),
            no(And(U("ectq", e), Not(U("ecnt", e))), "contactok", e)]


def _plain(i, ctx):
    """Unit 10 (R8): plain language."""
    return [yes(U("bun", i), "plain", i)]


def _methods(g, i, ctx):
    """Unit 12 (R7): first-class mail; e-mail on an agreement not withdrawn; next of kin of a deceased individual."""
    dec = U("dec", g)
    return [yes(And(Not(dec), Not(U("ins", g))), "mailok", g),
            no(And(Not(dec), U("ins", g)), "mailok", g),
            yes(And(Not(dec), U("agr", g), Not(U("wdr", g))), "emailok", g),
            no(Not(U("agr", g)), "emailok", g),
            no(And(U("agr", g), U("wdr", g)), "emailok", g),
            yes(And(dec, U("nokad", g)), "nokreq", g),
            no(Not(dec), "nokreq", g)]


def _subst_g(g, i, ctx):
    """Unit 13 first two sentences (R7): substitute notice required for the individual; not for the next of kin."""
    dec = U("dec", g)
    return [yes(And(U("bun", i), Not(dec), U("ins", g)), "substreq", g),
            no(And(Not(dec), Not(U("ins", g))), "substreq", g),
            no(And(dec, U("nokins", g)), "substreq", g)]


def _subst_i(i, ctx):
    """Unit 13 (i)-(ii) (R7): fewer than 10 / 10 or more; posting for 90 days; toll-free number at least 90 days."""
    n, has = k("nins", i), U("hasnins", i)
    ten, ninety = cnt(10), cnt(90)
    few, many = And(has, Lt(cnt(0), n), Lt(n, ten)), And(has, Le(ten, n))
    return [yes(few, "altok", i), no(many, "altok", i),
            yes(many, "wmreq", i), no(few, "wmreq", i),
            yes(many, "tfreq", i), no(few, "tfreq", i),
            yes(And(many, U("post", i), Le(ninety, k("pdays", i))), "postok", i),
            no(And(many, U("post", i), Lt(k("pdays", i), ninety)), "postok", i),
            yes(And(many, U("tfree", i), Le(ninety, k("tdays", i))), "tfok", i),
            no(And(many, U("tfree", i), Lt(k("tdays", i), ninety)), "tfok", i)]


def _urgent(i, ctx):
    """Unit 14 (R9): telephone or other means in addition, when deemed urgent."""
    return [yes(And(U("bun", i), U("urg", i)), "urgok", i)]


def _total(i, ctx):
    """D8: the individuals involved = the sum of the stated per-State residents (Lean arithmetic)."""
    ss = ctx.of("states", i)
    if not ss:
        return []
    return [Eq(k("tot", i), add_all([k("res", s) for s in ss]))]


def _media(s, i, ctx):
    """Unit 15 (R5): more than 500 residents of a State or jurisdiction -> prominent media outlets serving it."""
    return [iff_u("media", s, And(U("bun", i), Lt(cnt(500), k("res", s))))]


def _anym(i, ctx):
    return [iff_u("anym", i, Or(*[U("media", s) for s in ctx.of("states", i)]))]


def _lm(i, ctx):
    """Unit 16 (R4): the media notice: 60 calendar days after discovery."""
    return [shift(k("lm", i), k("disc", i), 60)]


def _media_content(e, i, ctx):
    """Unit 17 (R8): the media notice meets 164.404(c)."""
    return [yes(And(U("anym", i), U("emed", e), U("lst", e), U("pos", e)), "inclreq", e)]


def _media_plain(i, ctx):
    return []   # plain language of the media notice: the same predicate "plain" (unit 10 via 17); nothing more to ground


def _sec(i, ctx):
    """Unit 18 (R5): the Secretary."""
    return [iff_u("sec", i, U("bun", i))]


def _big(i, ctx):
    """Units 19-20 (R4): 500 or more individuals against less than 500."""
    return [iff_u("big", i, Le(cnt(500), k("tot", i)))]


def _ls_big(i, ctx):
    """Unit 19 (R4, D6): contemporaneously with the notice to individuals."""
    big, has = U("big", i), U("hasisd", i)
    return [Implies(And(big, has, no_later(k("isd", i), k("li", i))), Eq(k("ls", i), k("isd", i))),
            Implies(And(big, Not(has)), Eq(k("ls", i), k("li", i)))]


def _ls_small(i, ctx):
    """Unit 20 (R4, R10): fewer than 500: the log, and 60 days after the end of the calendar year of discovery."""
    out = [Implies(And(no_later(date(f"{y}-01-01"), k("disc", i)), no_later(k("disc", i), date(f"{y}-12-31"))),
                   Eq(k("ye", i), date(f"{y}-12-31"))) for y in YEARS]
    out.append(Implies(Not(U("big", i)), shift(k("ls", i), k("ye", i), 60)))
    out += [yes(And(U("bun", i), Not(U("big", i))), "logreq", i), no(U("big", i), "logreq", i),
            no(Not(U("bun", i)), "logreq", i)]
    return out


def _baduty(b, i, ctx):
    """Unit 21 (R5): the business associate notifies the covered entity."""
    return [iff_u("baduty", b, And(U("bun", i), U("bknow", b)))]


def _bdisc(b, i, ctx):
    """Unit 22 (R3): treated as discovered by the business associate."""
    cands = [(And(U("kba", kk), Not(U("kcom", kk))), k("kd", kk)) for kk, (side, j) in ctx.knows.items()
             if j == i and side == "ba"]
    cands.append((U("hasbdd", b), k("bdd", b)))
    return _earliest(k("bdisc", b), cands)


def _lb(b, i, ctx):
    """Unit 23 (R4): 60 calendar days after the business associate's discovery."""
    return [shift(k("lb", b), k("bdisc", b), 60)]


def _bid(b, i, ctx):
    """Unit 24 (R8): identification of each individual, to the extent possible."""
    return [yes(And(U("baduty", b), U("bidpos", b)), "bidreq", b),
            no(And(U("baduty", b), Not(U("bidpos", b))), "bidreq", b)]


def _binfo(b, i, ctx):
    """Unit 25 (R8): other available information."""
    return [yes(U("baduty", b), "binforeq", b)]


def _le_lead(o, i, ctx):
    """Unit 26 (R6): a statement applies when it names a criminal investigation or national security."""
    p = U("purp", o)
    return [iff_u("dlyapp", o, And(p, Or(And(U("wr", o), U("per", o)), U("oral", o))))]


def _le_written(o, i, ctx):
    """Unit 27 (R6): written, with the time specified: delay to its stated last day."""
    return [Implies(And(U("purp", o), U("wr", o), U("per", o), Not(U("oral", o))), Eq(k("dly", o), k("pend", o)))]


def _le_oral(o, i, ctx):
    """Unit 28 (R6): oral: document it; delay no longer than 30 days from the statement, unless a written statement as in (a)
    is submitted during that time."""
    p, oral, fw, fwp = U("purp", o), U("oral", o), U("fw", o), U("fwper", o)
    within = And(fw, fwp, no_later(k("fwd", o), k("l30", o)))
    return [yes(And(p, oral), "docreq", o), no(Not(oral), "docreq", o), no(Not(p), "docreq", o),
            shift(k("l30", o), k("od", o), 30),
            Implies(And(p, oral, Not(fw)), Eq(k("dly", o), k("l30", o))),
            Implies(And(p, oral, fw, Not(fwp)), Eq(k("dly", o), k("l30", o))),
            Implies(And(p, oral, within), Eq(k("dly", o), k("fwend", o)))]


def _nodelay(i, ctx):
    """R6: whether a qualifying statement delays a notice (its own latest day is then not answered)."""
    os_ = ctx.of("stmts", i)
    hit = lambda ab: Or(*[And(U("dlyapp", o), U(ab, o)) for o in os_])  # noqa: E731
    out = [iff_u("ndi", i, Not(hit("ab_ind"))), iff_u("ndm", i, Not(hit("ab_med"))),
           iff_u("nds", i, Not(Or(hit("ab_sec"), hit("ab_ind"))))]
    b = ctx.ba_of(i)
    if b:
        out.append(iff_u("ndb", b, Not(hit("ab_ba"))))
    return out


def _admin(i, ctx):
    """Unit 29 (R11): the covered entity complies with 164.530's listed administrative requirements."""
    return [U("admin", i)]


def _burden(i, ctx):
    """Unit 30 (R11): the burden of proof, in the event of a use or disclosure in violation of subpart E."""
    return [iff_u("burden", i, U("notperm", i))]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


def per_ba(fn):
    return lambda ctx: [f for b, i in ctx.bas.items() for f in fn(b, i, ctx)]


NONE = lambda ctx: []  # noqa: E731
UNITS = {
    1: ("RULE", NONE, "lead-in of the definitions (units 2, 5): 'As used in this subpart'"),
    2: ("PART", per_inc(_breach), "cross-reference",
        "R1: breach written; 'not permitted under subpart E' and 'protected health information' are stated facts (subpart E "
        "and the definition of PHI not pinned, D2)"),
    3: ("PART", per_inc(_excl), "cross-reference",
        "R1: the three exclusions written; 'workforce member', 'organized health care arrangement', 'subpart E' stated facts; "
        "good faith, inadvertence and retention are stated judgments"),
    4: ("RULE", None, "R1: the presumption written inside unit 2's rule (the low-probability demonstration a stated "
                      "judgment); the four factors are what the stated assessment covers"),
    5: ("PART", per_inc(_uns), "cross-reference",
        "R2: unsecured written; the Secretary's guidance (its methods) not pinned: the case states whether a method of it was "
        "applied (D2)"),
    6: ("RULE", per_inc(_ind), "R5: each affected individual"),
    7: ("RULE", per_inc(_disc), "R3: the earliest qualifying day in Lean (agency and reasonable diligence stated judgments)"),
    8: ("PART", per_inc(_li), "other:judgment standard",
        "R4, D6: 60 calendar days in Lean; 'without unreasonable delay' (an evaluative standard) not carried"),
    9: ("RULE", per("elems", _content), "R8: elements (A)-(E) to the extent possible (stated judgment); (E)'s four means"),
    10: ("RULE", per_inc(_plain), "R8: plain language"),
    11: ("RULE", NONE, "lead-in of (d): the methods of units 12-14"),
    12: ("PART", per("groups", _methods), "other:norm",
         "R7: first-class mail, e-mail on an agreement not withdrawn, the next of kin of a deceased individual written; 'may "
         "be provided in one or more mailings as information is available' (a permission with no outcome a case decides) not "
         "carried; 164.502(g)(4) (who is a personal representative) a stated fact"),
    13: ("PART", _cat(per("groups", _subst_g), per_inc(_subst_i)), "other:judgment standard",
         "R7: required / not required, fewer than 10 / 10 or more, 90 days in Lean written; 'reasonably calculated to reach' "
         "and 'conspicuous', 'major print or broadcast media', 'where the individuals ... likely reside' not carried"),
    14: ("RULE", per_inc(_urgent), "R9: telephone in addition when deemed urgent (stated judgment)"),
    15: ("RULE", _cat(per_inc(_total), per("states", _media), per_inc(_anym)),
         "R5: more than 500 residents of a State, the per-State count in Lean"),
    16: ("PART", per_inc(_lm), "other:judgment standard",
         "R4: 60 calendar days in Lean; 'without unreasonable delay' not carried"),
    17: ("RULE", per("elems", _media_content), "R8: the media notice meets 164.404(c) (in scope: units 9-10)"),
    18: ("RULE", per_inc(_sec), "R5: the Secretary"),
    19: ("PART", _cat(per_inc(_big), per_inc(_ls_big)), "cross-reference",
         "R4: 500 or more individuals (the sum in Lean), contemporaneously = the same day; 'in the manner specified on the HHS "
         "Web site' not pinned"),
    20: ("PART", per_inc(_ls_small), "cross-reference",
         "R4, R10: the log and 60 days after the end of the calendar year of discovery (calendar table in Lean) written; 'in "
         "the manner specified on the HHS web site' not pinned"),
    21: ("RULE", per_ba(_baduty), "R5: the business associate notifies the covered entity"),
    22: ("RULE", per_ba(_bdisc), "R3: the business associate's earliest qualifying day in Lean"),
    23: ("PART", per_ba(_lb), "other:judgment standard",
         "R4: 60 calendar days in Lean; 'without unreasonable delay' not carried"),
    24: ("RULE", per_ba(_bid), "R8: identification of each individual, to the extent possible (stated judgment)"),
    25: ("PART", per_ba(_binfo), "other:judgment standard",
         "R8: the duty written; 'at the time of the notification ... or promptly thereafter as information becomes "
         "available' (no day) not carried"),
    26: ("RULE", _cat(per("stmts", _le_lead), per_inc(_nodelay)), "R6: the statement's purpose and whom it delays"),
    27: ("RULE", per("stmts", _le_written), "R6: written with the time specified"),
    28: ("RULE", per("stmts", _le_oral), "R6: oral: document; 30 days in Lean; a written statement within that time"),
    29: ("PART", per_inc(_admin), "cross-reference",
         "R11: the duty to comply written; the administrative requirements of 164.530 not pinned"),
    30: ("RULE", per_inc(_burden), "R11: the burden of proof"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]."""
    out = []
    table = units_table(mutant)
    for n, e in sorted(table.items()):
        if e[1] is None:
            continue
        for i, f in enumerate(e[1](ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (fmla_eligibility translation.py conventions) ----------------------------------------------

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
    """The atoms / day or count constants a ground rule fixes."""
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
    if f[0] == "shift_days" and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

def int_constants(ctx):
    """name -> (unit, words) for every day / count constant of the case."""
    out = {}
    for kind, bases in BASES_OF.items():
        xs = ctx.incs if kind == "incs" else list(getattr(ctx, kind))
        for x in xs:
            for base in bases:
                out[f"{base}_{x}"] = INT_UNITS[base]
    return out


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
    for name, (unit, w) in int_constants(ctx).items():
        consts[name] = {"sort": "$int", "unit": unit, "description": f"{w[0].upper() + w[1:]} ({name}).",
                        "verbalisation": f"{w} ({name})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The incident, or a State, the business associate's side, a "
                                                             "person who learned of it, a law enforcement statement, an "
                                                             "affected individual or a notice element the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      CNT: {"scale": "1", "display": {"kind": "decimal", "label": "count"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _m_media(s, i, ctx):
    return [iff_u("media", s, And(U("bun", i), Le(cnt(500), k("res", s))))]


def _m_big(i, ctx):
    return [iff_u("big", i, Lt(cnt(500), k("tot", i)))]


def _m_li(i, ctx):
    return [shift(k("li", i), k("disc", i), 61)]


def _m_excl(i, ctx):
    out = _excl(i, ctx)
    out[0] = iff_u("ex1", i, And(U("acq", i), U("wf", i), U("unint", i), U("gfs", i)))
    return out


def _m_breach(i, ctx):
    return [iff_u("breach", i, And(U("phi", i), U("notperm", i), Not(U("excl", i))))]


def _m_uns(i, ctx):
    return [iff_u("uns", i, U("phi", i)), iff_u("bun", i, And(U("breach", i), U("uns", i)))]


def _m_disc(i, ctx):
    cands = [(U("kce", kk), k("kd", kk)) for kk, (side, j) in ctx.knows.items() if j == i and side == "ce"]
    cands.append((U("hasdd", i), k("dd", i)))
    return _earliest(k("disc", i), cands)


def _m_disc_dd(i, ctx):
    cands = [(And(U("kce", kk), Not(U("kcom", kk))), k("kd", kk)) for kk, (side, j) in ctx.knows.items()
             if j == i and side == "ce"]
    return _earliest(k("disc", i), cands)


def _m_subst(i, ctx):
    n, has = k("nins", i), U("hasnins", i)
    few, many = And(has, Lt(cnt(0), n), Le(n, cnt(10))), And(has, Lt(cnt(10), n))
    out = _subst_i(i, ctx)
    out[0:6] = [yes(few, "altok", i), no(many, "altok", i), yes(many, "wmreq", i), no(few, "wmreq", i),
                yes(many, "tfreq", i), no(few, "tfreq", i)]
    return out


def _m_oral(o, i, ctx):
    out = _le_oral(o, i, ctx)
    out[3] = shift(k("l30", o), k("od", o), 31)
    return out


def _m_oral_fw(o, i, ctx):
    out = _le_oral(o, i, ctx)
    out[6] = Implies(And(U("purp", o), U("oral", o), U("fw", o), U("fwper", o)), Eq(k("dly", o), k("fwend", o)))
    return out


def _m_ls_small(i, ctx):
    out = _ls_small(i, ctx)
    out[len(YEARS)] = Implies(Not(U("big", i)), shift(k("ls", i), k("disc", i), 60))
    return out


def _m_methods(g, i, ctx):
    out = _methods(g, i, ctx)
    out[2] = yes(And(Not(U("dec", g)), U("agr", g)), "emailok", g)
    out[4] = no(FALSE, "emailok", g)
    return out


def _m_le_lead(o, i, ctx):
    return [iff_u("dlyapp", o, Or(And(U("wr", o), U("per", o)), U("oral", o)))]


MUTANTS = {
    "M1": ("THRESHOLD: media for 500 or more residents of a State (not more than 500)",
           _swap(15, lambda b: _cat(per_inc(_total), per("states", _m_media), per_inc(_anym)))),
    "M2": ("THRESHOLD: the Secretary's 500 or more read as more than 500",
           _swap(19, lambda b: _cat(per_inc(_m_big), per_inc(_ls_big)))),
    "M3": ("PERIOD: 60 calendar days read as 61 (individuals)", _swap(8, lambda b: per_inc(_m_li))),
    "M4": ("EXCLUSION: further impermissible use ignored in exclusion (i)", _swap(3, lambda b: per_inc(_m_excl))),
    "M5": ("PRESUMPTION: the low-probability demonstration ignored", _swap(2, lambda b: per_inc(_m_breach))),
    "M6": ("SECURED: the Secretary's-guidance method ignored (all PHI unsecured)", _swap(5, lambda b: per_inc(_m_uns))),
    "M7": ("DISCOVERY: the person committing the breach counted as knowledge", _swap(7, lambda b: per_inc(_m_disc))),
    "M8": ("DISCOVERY: the reasonable-diligence day ignored", _swap(7, lambda b: per_inc(_m_disc_dd))),
    "M9": ("THRESHOLD: substitute notice 10 or more read as more than 10",
           _swap(13, lambda b: _cat(per("groups", _subst_g), per_inc(_m_subst)))),
    "M10": ("PERIOD: the oral statement's 30 days read as 31", _swap(28, lambda b: per("stmts", _m_oral))),
    "M11": ("UNLESS: a written statement after the 30 days still governs", _swap(28, lambda b: per("stmts", _m_oral_fw))),
    "M12": ("YEAR END: the small-breach Secretary notice counted from discovery, not the year end",
            _swap(20, lambda b: per_inc(_m_ls_small))),
    "M13": ("E-MAIL: a withdrawn agreement to electronic notice ignored", _swap(12, lambda b: per("groups", _m_methods))),
    "M14": ("PURPOSE: a statement naming neither a criminal investigation nor national security delays too",
            _swap(26, lambda b: _cat(per("stmts", _m_le_lead), per_inc(_nodelay)))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
