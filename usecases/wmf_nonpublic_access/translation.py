"""Wikimedia Foundation Access to Nonpublic Personal Data Policy (oldid 556416; statute corpus batch 4, NON-STATUTE (e)): the VE
translation, one pass with today's language. CROSS-FAMILY questions (Codex writer), Opus translator/encoder.

Row statute-corpus-wmf-nonpublic-access (dri-statute-corpus-wmf-nonpublic-access-w-1124, Opus 5.5). Written from the pinned source
only (manage-agents reviews/spare/statute-corpus/batch4/wmf-nonpublic-access/source.txt, sha256 023d5262...c2a) and the decisions
D1-D14 of ISOLATION.md, BEFORE the encoder's question file (questions-enc.jsonl) was opened. Evidence branch: nothing here is a
Lean kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of batch4/wmf-nonpublic-access/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Duties, permissions and "should" sentences are carried as CLASSIFICATIONS of the stated facts (a yes/no predicate whose
definition is the text's condition: "the member must obtain written approval for this disclosure"); a norm that cannot be
carried that way is ledgered other:norm.

ONE CASE = one community member m. Items (one sort "item"):
  m   the member (coverage, the 90-day compliance deadline of (e));
  a   a TEST of the minimum requirements (a)-(c) on a day: a grant of access rights for a role, a candidacy in a community-run
      selection process for such a role, or the compliance check of (e) on its deadline (at = the deadline, a Lean step);
  e   a change of the member's email address (day of the change; whether and when the Foundation was informed);
  d   a disclosure of Nonpublic Personal Data, planned or made, or a request for such data (recipient, circumstance, the
      explanation email and the written approval of the Foundation);
  t   a tool the member had access to (revoked or not, the day);  x  data the member has (from which tool);
  u   a use of a tool;  k  a complaint;  i  personal information the member submitted to the Foundation.
Days are integers of the unit "day" (the language's day domain begins on January 1, 1970: a day before it enters as January 1,
1970 only where every comparison it takes part in is with days from 1970 on, R12).

THE BRIDGE (one tested script, bridge/wmf_bridge.py; never the encoder): from a stated date of birth, the day the member attains
16 and 18 years of age (stated convention: at the beginning of the anniversary of the date of birth); from a stated disclosure
day and the case's named public holidays, the TENTH BUSINESS DAY COUNTING BACK from the disclosure day (the disclosure day
counted when it is a business day; business day = Monday to Friday not a named public holiday). Every comparison with these
days, every period of days (one week = 7 days, 90 calendar days) and every deadline is in the rules below (Lean checks them).
Why b10 decides "at least ten business days prior": the business days after a sending day s up to and including the disclosure
day t number ten or more exactly when s is before b10 (b10 and the nine business days after it up to t are all after s); so
the latest sending day is the day before b10.

READINGS (fixed here, on the text; refuse when in doubt):
R1  Coverage (units 1-4): the Policy applies to a member to whom the Foundation has granted access to Nonpublic Personal Data
    (the stated grant); the three "including" items are kinds of such access (written as the same grant with the kind). Not
    covered when no grant and none of the three kinds of access is stated. A member who gets data under an approved
    exception on terms outside the Policy (unit 5), or whose every access was revoked before the day asked: undetermined.
R2  The minimum requirements (unit 6 with (a)-(c)) are tested on the day asked (the grant, the candidacy, or the (e) deadline):
    each act counts only when done on or before that day. "Should also be considered requirements to be a candidate": the
    same test for a candidacy. Community-specified additional criteria that the member does not meet: the Policy's own
    requirements met -> undetermined (the Policy permits them; whether they bar is the community's), not met -> no.
R3  Age (unit 8): at least 18, or 16 when the role applied for is email response team member. Where an application day is
    stated as well as the day asked, both must meet it for "yes"; the limit reached between the two: undetermined (two
    readings: "any community member who applies ... must be" vs "must meet before being granted"). An individual exemption
    for age reviewed by the Legal department and approved removes the age bar; an exemption stated as granted without that
    review: undetermined.
R4  Domicile (unit 5): a member with known domicile in a jurisdiction that blocks access to Wikimedia projects "would otherwise
    be unable to be granted": barred unless an individual exemption reviewed by Legal is approved. LATENT FIX 11-26 (U6): the
    bar is not one of Sections (a)-(c): it stands in the way of a grant or a candidacy (ok), never of the (e) compliance
    check, and it is not part of "the minimum requirements of Sections (a)-(c) are met" (req).
R5  Email ((b)): a valid address submitted to the Foundation; the account linked to a valid address; verification completed
    when it was requested on or before the day asked; for each change of address on or before the day asked: met when the
    day asked is within the week (on or before the change day + 7) or the Foundation was informed by change day + 7; not met
    when the week ended before the day asked and the Foundation was not informed by the day asked; informed late but before
    the day asked: undetermined.
R6  Confidentiality ((c)): read and certified agreement to the Confidentiality Agreement on or before the day asked. The
    Agreement's own text is not pinned. REVISION 11-25 (dri-b4-policy-translation-revise-1125, written from source.txt and
    the frozen run's refusal causes only): this Policy itself states the six subjects the Agreement outlines (units 16-21:
    what to treat as confidential; when access is allowed; how data about other users may be used; when and to whom data
    may be disclosed and how to refrain otherwise; how to safeguard accounts; when to report disclosure or improper access,
    use or disclosure). Written: for the case's member and for each test of the requirements (a grant, a candidacy, the (e)
    compliance check), the Confidentiality Agreement the member is required to read and certify outlines each subject. What
    the Agreement says on a subject (its wording, its rules) stays unpinned: a question on that is not answered.
R7  (e): a member granted access rights on or before the effective day (stated, D3) must meet (a)-(c) by the effective day +
    90 (on or before, the stated convention), or by the stated day to which the Foundation extended the period. For a member
    granted later: no answer (the requirements are met before the grant; whether that is "a deadline": undetermined).
    "should anticipate having their access rights revoked" (unit 24): no definite outcome (D7).
R8  Use (unit 27): a use is allowed when it complies with the policy governing the tool (stated); for CheckUser, unless the check
    is cross-wiki, the applicable local policy must allow it too. Destroy (LATENT FIX 11-26, U27): Nonpublic Personal Data
    the member has as a result of a tool to which their access was revoked on or before the day asked must be destroyed;
    no other data. Only
    Nonpublic Personal Data ("must destroy all Nonpublic Personal Data that they have as a result of that tool"; unit 3
    separates "content" from "Nonpublic Personal Data"): the data's being such is a Privacy Policy conclusion, entered as a
    fact from the case's words (npd, with npdst: the case says either way; a reading of the words beyond them is listed as
    encoder judgement); stated not to be: no; not stated: undetermined (refused).
R9  Disclosure (units 28-35): limited to (i)-(vi) (each with its stated judgment, D9). Written approval of the Foundation is
    required for a disclosure in a situation covered by (ii) or (iv), or one the member is required by law to make to law
    enforcement, administrative bodies or other governmental agencies (except (iii): required by law AND (iii) gives two
    outcomes: undetermined). Secured = the explanation emailed before b10 (bridge) AND the Foundation's written approval given
    on or before the disclosure day. "May disclose": in the list and (no approval needed, or approval secured) -> yes; not in
    the list and not required by law -> no; approval needed and not secured, where the case states the approval facts -> no;
    approval facts not stated -> undetermined. Under no obligation by the Foundation: never obliged.
R10 Unit 36: a member who discloses to law enforcement in response to a request regarding an immediate and credible threat of
    bodily harm needs no pre-authorization and should immediately contact the Foundation; one who declines an emergency
    request should immediately email the Foundation. "Permitted without pre-authorization": yes for a listed disclosure that
    needs no approval, no for one that does.
R11 Unit 37: a request not covered by (i)-(vi), or not acted upon by the member, or a subpoena, should be directed to the
    Foundation's legal department; a covered request the member acts upon: not.
R12 Days before January 1, 1970 (a birthday of a member born before 1952): entered as January 1, 1970 by the bridge only where
    every comparison is with days from 1970 on (the case's days are all later).
R13 Complaints (units 38-40): a complaint about an infringement of this Policy may be submitted to the Ombuds Commission; one
    about an action under an exception should be evaluated by the appropriate community governance mechanisms, may be referred
    to the Foundation, and may be reviewed by the Ombuds Commission if it concerns the Privacy Policy's relevant section; one
    about obligations outside the Policy should be evaluated by community governance mechanisms. Nothing else is decided
    ("may result in", "will generally defer": no definite outcome, D7).
R14 Unit 22: personal information a member submits to the Foundation as part of the application process or otherwise under the
    Policy is subject to the Privacy Policy and the Data Retention Guidelines (their content not pinned).
No number from a case's facts is ever a coefficient: every literal below (16, 18 through the bridge; 7, 90; ten business days
through the bridge) is a literal of the pinned text.
"""
from __future__ import annotations

import hashlib
import json

DAY = "day"
INT_UNITS = {  # per-item day constants: base -> words
    # member
    "eff": "the day this Policy becomes effective (a stated fact of the case, D3)",
    "gd": "the day the Foundation granted the member access rights",
    "extd": "the day to which the Foundation extended the member's compliance period",
    "dl": "the day by which the member must meet the requirements of Sections (a)-(c) under (e)",
    # test of the requirements
    "at": "the day the requirements are tested (the grant, the candidacy, or the (e) deadline)",
    "app": "the day the member applied",
    "a16": "the day the member attains 16 years of age (bridge)",
    "a18": "the day the member attains 18 years of age (bridge)",
    "certd": "the day the member certified the minimum age to the Foundation",
    "subd": "the day the member submitted an email address to the Foundation",
    "linkd": "the day the member's account was linked to an email address",
    "vrqd": "the day verification of the address was requested",
    "verd": "the day the member completed the verification",
    "csd": "the day the member read and certified agreement to the Confidentiality Agreement",
    # change of address
    "chgd": "the day the member changed the email address",
    "infd": "the day the member informed the Foundation of the change",
    "lim": "the last day of the week within which the Foundation must be informed of the change",
    "askd": "the day asked about",
    # disclosure
    "dday": "the day of the disclosure (made or anticipated)",
    "sentd": "the day the member emailed the Foundation the explanation of the proposed disclosure",
    "apprd": "the day the Foundation gave written approval of the disclosure",
    "b10": "the tenth business day counting back from the disclosure day (bridge)",
    "lat": "the latest day on which the explanation may be emailed (the day before b10)",
    # tool, data
    "revd": "the day the member's access to the tool was revoked",
    "xask": "the day asked about the data",
}
FACTS = {
    # member
    "granted": "the Foundation has granted the member access to Nonpublic Personal Data covered by the Privacy Policy",
    "tool": "the member has access to a tool that permits them to view Nonpublic Personal Data about other users or members "
            "of the public",
    "supp": "the member has the ability to access content or Nonpublic Personal Data removed from administrator view",
    "dev": "the member is a volunteer developer with access to Nonpublic Personal Data",
    "excout": "the member receives the data under an approved exception on terms outside this Policy",
    "allrev": "every access of the member to Nonpublic Personal Data was revoked before the day asked",
    "ext": "the Foundation extended the member's compliance period (to the day extd)",
    # test of the requirements
    "hasapp": "an application day is stated besides the day asked",
    "ert": "the role applied for is email response team member",
    "cert": "the member certified to the Foundation that they meet the minimum age required for the rights applied for",
    "sub": "the member submitted an email address to the Foundation",
    "subvalid": "the submitted email address is valid",
    "link": "the account under which the member applies is linked to an email address",
    "linkvalid": "the linked email address is valid",
    "vrq": "the member was requested to verify the submitted or linked email address",
    "ver": "the member completed that verification",
    "cs": "the member read and certified agreement to the Confidentiality Agreement",
    "exm_age": "an individual exemption for user age, reviewed by the Legal department, was approved for the member",
    "exm_dom": "an individual exemption for domicile, reviewed by the Legal department, was approved for the member",
    "exm_unrev": "an individual exemption is stated as granted without review by the Legal department",
    "blocked": "the member's known domicile is in a jurisdiction that blocks access to Wikimedia projects",
    "exc": "an approved exception (reviewed by the Legal department) covers the member's group",
    "crit_unmet": "the community requires additional criteria for the role that the member does not meet",
    # change of address
    "inf": "the member informed the Foundation of the change (on the day infd)",
    # disclosure / request
    "r_dcm": "the recipient is another Designated Community Member with the same access rights, or otherwise permitted to "
             "access the same Nonpublic Personal Data",
    "duty": "the disclosure is made to fulfill the duties outlined in the applicable policy for the access tool used (stated "
            "judgment)",
    "r_vendor": "the recipient is a service provider, carrier or other third party vendor",
    "ipblk": "the disclosure is to assist in the targeting of IP blocks or the formulation of a complaint to relevant Internet "
             "Service Providers",
    "r_le": "the recipient is law enforcement",
    "threat": "there is an immediate and credible threat of serious bodily harm (stated judgment)",
    "r_auth": "the recipient is an authorized party",
    "uperm": "the user whose nonpublic information is disclosed gave express permission",
    "r_pub": "the recipient is the public",
    "blk": "the disclosure is a necessary and incidental consequence of the member blocking a sockpuppet or other abusive "
           "account (stated judgment)",
    "legexc": "the disclosure is authorized by the Foundation's Legal Department through an exception to this Policy",
    "lawreq": "the member is required by law to disclose to law enforcement, administrative bodies or other governmental "
              "agencies",
    "lereq": "the member received a request for the data from law enforcement",
    "emerg": "the request is an emergency request (stated judgment)",
    "subp": "the request is a subpoena",
    "disc": "the member discloses (or chooses to disclose) the data",
    "sent": "the member emailed the Foundation an explanation of the proposed disclosure (on the day sentd)",
    "appr": "the Foundation gave written approval of the disclosure (on the day apprd)",
    "apprst": "the case states the facts of the explanation email and the Foundation's written approval",
    # tool, use
    "rev": "the member's access to the tool was revoked (on the day revd)",
    # data (LATENT FIX 11-26, U27: unit 27's destroy duty is for Nonpublic Personal Data only)
    "npd": "the data is Nonpublic Personal Data covered by the Privacy Policy (a Privacy Policy conclusion, from the case's words)",
    "npdst": "the case states whether the data is Nonpublic Personal Data covered by the Privacy Policy",
    "pol": "the use complies with the policy that governs the tool (for CheckUser: the global CheckUser Policy)",
    "cu": "the tool is the CheckUser tool",
    "cross": "the check is a cross-wiki check",
    "locbad": "the local policy applicable to the relevant Site does not allow the use",
    # complaint
    "infr": "the complaint is about an infringement of this Policy",
    "excact": "the complaint is about an inappropriate action taken under an exception to this Policy",
    "ppsec": "the complaint concerns the Privacy Policy's relevant section",
    "outside": "the complaint is about confidentiality obligations or expectations that exist outside this Policy and its "
               "exceptions",
    # personal information
    "subapp": "the information was submitted by the member to the Foundation as part of the application process or otherwise "
              "under this Policy",
}
BINARY = {
    "chg": "(change, test) the change of address is one of the member's changes before the test",
    "from": "(data, tool) the member has the data as a result of the tool",
}
STATED = ("duty", "threat", "blk", "emerg")
BRIDGED_CONSTS = ("a16", "a18", "b10")
DERIVED_UNARY = {
    "covered": "this Policy applies to the member (a Designated Community Member)",
    "holder": "the member had been granted access rights at the time this Policy becomes effective",
    "ageok": "the member meets the minimum age for the role on the day tested",
    "certok": "the member certified the minimum age by the day tested",
    "subok": "the member submitted a valid email address by the day tested",
    "linkok": "the account was linked to a valid email address by the day tested",
    "verok": "the verification requirement is met on the day tested",
    "chgok": "every change of address was reported as (b) requires, on the day tested",
    "emailok": "the requirements of Section (b) are met on the day tested",
    "csok": "the member read and certified the Confidentiality Agreement by the day tested",
    "domok": "no known domicile bars the grant",
    "req": "the minimum requirements of Sections (a)-(c) are met on the day tested",
    "ok": "nothing in the Policy's requirements stands in the way (grant, candidacy, or compliance by the deadline)",
    "inok": "the member informed the Foundation of the change within one week of it",
    "s1": "the disclosure is covered by (i)", "s2": "the disclosure is covered by (ii)", "s3": "the disclosure is covered by (iii)",
    "s4": "the disclosure is covered by (iv)", "s5": "the disclosure is covered by (v)", "s6": "the disclosure is covered by (vi)",
    "listed": "the disclosure is one of those the Policy limits disclosures to ((i)-(vi))",
    "needappr": "the member must secure the Foundation's written approval before the disclosure",
    "early": "the explanation was emailed at least ten business days prior to the disclosure",
    "approk": "the Foundation's written approval was secured as the Policy requires",
    "maydisc": "the member may disclose the data in the circumstance",
    "nopre": "the member is permitted to disclose without pre-authorization",
    "emailnow": "the member should immediately email (contact) the Foundation",
    "obliged": "the member is under an obligation by the Foundation to disclose",
    "tolegal": "the request should be directed to the Foundation's legal department",
    "mayuse": "the member may use the tool for this use",
    "destroy": "the member must destroy the data",
    "ombuds": "the complaint may be submitted to (reviewed by) the Ombuds Commission",
    "commgov": "the complaint should be evaluated by the appropriate community governance mechanisms",
    "wmfref": "the complaint may be referred to the Foundation for review under the Office Actions Policy",
    "priv": "the information is subject to the Foundation's Privacy Policy and Data Retention Guidelines",
}
AGREEMENT_SUBJECTS = {  # REVISION 11-25 (R6): unit -> (predicate, the subject as this Policy states it)
    16: ("agconf", "what Designated Community Members should treat as confidential information"),
    17: ("agwhen", "when they are allowed to access Nonpublic Personal Data"),
    18: ("aguse", "how Designated Community Members may use Nonpublic Personal Data about other users"),
    19: ("agdisc", "when and to whom they may disclose the Nonpublic Personal Data and how they must otherwise refrain from "
                   "disclosing it to anyone, except as permitted under applicable policies"),
    20: ("agsafe", "how they must safeguard their accounts from unauthorized access"),
    21: ("agrep", "when they must report disclosure of Nonpublic Personal Data to third parties or improper access, use, or "
                  "disclosure of Nonpublic Personal Data"),
}
for _n, (_p, _w) in AGREEMENT_SUBJECTS.items():
    DERIVED_UNARY[_p] = ("(member, or a test of the requirements) the short Confidentiality Agreement the member is required "
                         f"to read and certify (Section (c)) outlines {_w} (unit {_n})")


# --- formula helpers (the ve-quantity@1 wire shapes; fmla_eligibility / oas_canada conventions) ----------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
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


def k(base, x):
    return ["const", DAY, f"{base}_{x}"]


def iff_u(p, x, body): return Iff(U(p, x), body)
def yes(cond, p, x): return Implies(cond, U(p, x))
def no(cond, p, x): return Implies(cond, Not(U(p, x)))


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """items by kind; atdl: tests whose day is the member's (e) deadline (a Lean step), the others' day is stated."""
    KINDS = ("tests", "changes", "discs", "tools", "datas", "uses", "comps", "infos")

    def __init__(self, tests=(), changes=(), discs=(), tools=(), datas=(), uses=(), comps=(), infos=(), atdl=()):
        self.member = "m"
        self.tests, self.changes, self.discs = list(tests), list(changes), list(discs)
        self.tools, self.datas, self.uses, self.comps, self.infos = list(tools), list(datas), list(uses), list(comps), list(infos)
        self.atdl = list(atdl)

    @property
    def items(self):
        return [self.member] + [x for kd in self.KINDS for x in getattr(self, kd)]


def per(kind, fn):
    return lambda ctx: [f for x in getattr(ctx, kind) for f in fn(x, ctx)]


def member(fn):
    return lambda ctx: fn(ctx.member, ctx)


# --- the units ----------------------------------------------------------------------------------------------------

def _cov_grant(m, ctx):
    """Unit 1 (R1): covered when the Foundation granted access; not covered when no grant and no kind of access is stated."""
    return [yes(And(U("granted", m), Not(U("excout", m)), Not(U("allrev", m))), "covered", m),
            no(And(Not(U("granted", m)), Not(U("tool", m)), Not(U("supp", m)), Not(U("dev", m))), "covered", m)]


def _cov_kind(p):
    """Units 2-4 (R1): the kind of access, granted, is covered (the 'including' items)."""
    return lambda m, ctx: [yes(And(U("granted", m), U(p, m), Not(U("excout", m)), Not(U("allrev", m))), "covered", m)]


def _exemptions(a, ctx):
    """Unit 5 (R3, R4): an individual exemption reviewed by Legal removes the age or domicile bar (in _age, _dom); an
    approved group exception keeps a 'no' from being given (in _ok)."""
    return [yes(Or(Not(U("blocked", a)), U("exm_dom", a)), "domok", a),
            no(And(U("blocked", a), Not(U("exm_dom", a)), Not(U("exm_unrev", a))), "domok", a)]


def _ok(a, ctx):
    """Unit 6 (R2): the minimum requirements before a grant, and as requirements to be a candidate; community criteria.
    LATENT FIX 11-26 (U6): req is Sections (a)-(c) only (age, certification, email, confidentiality); the domicile bar of
    unit 5 ("would otherwise be unable to be granted", R4) is a conjunct of ok for a grant or a candidacy test only, never
    of the (e) compliance check (ctx.atdl), which unit 23 limits to "the requirements of Sections (a) - (c)"."""
    req, crit, exc = U("req", a), U("crit_unmet", a), U("exc", a)
    parts = [U(p, a) for p in ("ageok", "certok", "emailok", "csok")]
    out = [yes(And(*parts), "req", a),
           no(Or(*[Not(p) for p in parts]), "req", a)]
    if a in ctx.atdl:
        return out + [yes(And(req, Not(crit)), "ok", a),
                      no(And(Not(req), Not(exc)), "ok", a)]
    dom = U("domok", a)
    return out + [yes(And(req, dom, Not(crit)), "ok", a),
                  no(And(Or(Not(req), Not(dom)), Not(exc)), "ok", a)]


def _age(a, ctx):
    """Unit 8 (R3): at least 18, or 16 for an email response team member; bridged birthdays; Legal-reviewed exemption."""
    at, app, a16, a18 = k("at", a), k("app", a), k("a16", a), k("a18", a)
    ert, ex, hasapp, unrev = U("ert", a), U("exm_age", a), U("hasapp", a), U("exm_unrev", a)
    return [yes(ex, "ageok", a),
            yes(And(ert, no_later(a16, at), Or(Not(hasapp), no_later(a16, app))), "ageok", a),
            yes(And(Not(ert), no_later(a18, at), Or(Not(hasapp), no_later(a18, app))), "ageok", a),
            no(And(Not(ex), Not(unrev), ert, before(at, a16)), "ageok", a),
            no(And(Not(ex), Not(unrev), Not(ert), before(at, a18)), "ageok", a)]


def _cert(a, ctx):
    """Unit 9: certified the minimum age to the Foundation, by the day tested."""
    at, d = k("at", a), k("certd", a)
    return [yes(And(U("cert", a), no_later(d, at)), "certok", a),
            no(Or(Not(U("cert", a)), before(at, d)), "certok", a)]


def _email_all(a, ctx):
    """Unit 10 (lead-in of (b)): the four requirements together."""
    parts = [U(p, a) for p in ("subok", "linkok", "verok", "chgok")]
    return [yes(And(*parts), "emailok", a), no(Or(*[Not(p) for p in parts]), "emailok", a)]


def _sub(a, ctx):
    """Unit 11: a valid email address submitted to the Foundation by the day tested."""
    at, d = k("at", a), k("subd", a)
    return [yes(And(U("sub", a), U("subvalid", a), no_later(d, at)), "subok", a),
            no(Or(Not(U("sub", a)), Not(U("subvalid", a)), before(at, d)), "subok", a)]


def _link(a, ctx):
    """Unit 12: the account linked to a valid email address by the day tested."""
    at, d = k("at", a), k("linkd", a)
    return [yes(And(U("link", a), U("linkvalid", a), no_later(d, at)), "linkok", a),
            no(Or(Not(U("link", a)), Not(U("linkvalid", a)), before(at, d)), "linkok", a)]


def _verify(a, ctx):
    """Unit 13: verification completed, if requested (on or before the day tested)."""
    at, rq, vd = k("at", a), k("vrqd", a), k("verd", a)
    asked = And(U("vrq", a), no_later(rq, at))
    return [yes(Not(U("vrq", a)), "verok", a),
            yes(And(U("vrq", a), before(at, rq)), "verok", a),
            yes(And(U("ver", a), no_later(vd, at)), "verok", a),
            no(And(asked, Not(U("ver", a))), "verok", a),
            no(And(asked, U("ver", a), before(at, vd)), "verok", a)]


def _week(e, ctx):
    """Unit 14: the week after a change ends on the change day + 7 (the stated convention); informed within it or not."""
    lim, inf_d, ask = k("lim", e), k("infd", e), k("askd", e)
    return [shift(lim, k("chgd", e), 7),
            yes(And(U("inf", e), no_later(inf_d, lim)), "inok", e),
            no(And(U("inf", e), before(lim, inf_d)), "inok", e),
            no(And(Not(U("inf", e)), before(lim, ask)), "inok", e)]


def _chgok(a, ctx):
    """Unit 14 in the test (R5): every change on or before the day tested reported in time, or its week still running."""
    at = k("at", a)
    good, bad = [], []
    for e in ctx.changes:
        lim, chd, ind = k("lim", e), k("chgd", e), k("infd", e)
        good.append(Or(Not(B("chg", e, a)), before(at, chd), no_later(at, lim), And(U("inf", e), no_later(ind, lim))))
        bad.append(And(B("chg", e, a), no_later(chd, at), before(lim, at), Or(Not(U("inf", e)), before(at, ind))))
    return [yes(And(*good), "chgok", a), no(Or(*bad), "chgok", a)]


def _cs(a, ctx):
    """Unit 15 (R6): read and certified agreement to the Confidentiality Agreement by the day tested."""
    at, d = k("at", a), k("csd", a)
    return [yes(And(U("cs", a), no_later(d, at)), "csok", a),
            no(Or(Not(U("cs", a)), before(at, d)), "csok", a)]


def _agreement(n):
    """Units 16-21 (R6, revision 11-25): the Confidentiality Agreement outlines the subject this Policy names."""
    p = AGREEMENT_SUBJECTS[n][0]
    return lambda ctx: [U(p, x) for x in [ctx.member] + ctx.tests]


def _priv(i, ctx):
    """Unit 22 (R14): submitted information is subject to the Privacy Policy and the Data Retention Guidelines."""
    return [yes(U("subapp", i), "priv", i)]


def _deadline(m, ctx):
    """Unit 23 (R7): granted at the effective day -> (a)-(c) within 90 calendar days of it, or by the extended day."""
    eff, gd, dl = k("eff", m), k("gd", m), k("dl", m)
    hold = U("holder", m)
    out = [iff_u("holder", m, no_later(gd, eff)),
           Implies(And(hold, Not(U("ext", m))), shift(dl, eff, 90)),
           Implies(And(hold, U("ext", m)), ["eq", dl, k("extd", m)])]
    for a in ctx.atdl:
        out.append(["eq", k("at", a), dl])
    return out


def _use(u, ctx):
    """Unit 27 first part (R8): only in accordance with the tool's policy; CheckUser: the local policy too unless cross-wiki."""
    return [iff_u("mayuse", u, And(U("pol", u), Or(Not(U("cu", u)), U("cross", u), Not(U("locbad", u)))))]


def _destroy(x, ctx):
    """Unit 27 last sentence (R8): "that member must destroy all Nonpublic Personal Data that they have as a result of that
    tool". LATENT FIX 11-26 (U27): the duty needs the data to be Nonpublic Personal Data (npd, stated); data stated not to
    be (npdst, not npd) or not from a revoked tool: no; from a revoked tool with npd not stated: no rule (refused)."""
    hits = Or(*[And(B("from", x, t), U("rev", t), no_later(k("revd", t), k("xask", x))) for t in ctx.tools])
    npd, st = U("npd", x), U("npdst", x)
    return [yes(And(npd, hits), "destroy", x),
            no(Not(hits), "destroy", x),
            no(And(st, Not(npd)), "destroy", x)]


def _list(d, ctx):
    """Unit 28 (R9): disclosures are limited to (i)-(vi)."""
    return [iff_u("listed", d, Or(*[U(f"s{n}", d) for n in range(1, 7)]))]


SIT = {1: ("r_dcm", "duty"), 2: ("r_vendor", "ipblk"), 3: ("r_le", "threat"), 4: ("r_auth", "uperm"), 5: ("r_pub", "blk")}


def _sit(n):
    def build(d, ctx):
        if n == 6:
            return [iff_u("s6", d, U("legexc", d))]
        p, q = SIT[n]
        return [iff_u(f"s{n}", d, And(U(p, d), U(q, d)))]
    return build


def _approval(d, ctx):
    """Unit 35 (R9): no obligation; written approval for (ii), (iv) and disclosures required by law; ten business days."""
    s2, s3, s4, law = U("s2", d), U("s3", d), U("s4", d), U("lawreq", d)
    need, b10, sent_d, dd = U("needappr", d), k("b10", d), k("sentd", d), k("dday", d)
    listed, ok, st = U("listed", d), U("approk", d), U("apprst", d)
    return [Not(U("obliged", d)),
            yes(Or(s2, s4), "needappr", d),
            yes(And(law, Not(s3)), "needappr", d),
            no(And(Not(s2), Not(s4), Not(law)), "needappr", d),
            shift(b10, k("lat", d), 1),
            iff_u("early", d, And(U("sent", d), before(sent_d, b10))),
            yes(And(U("early", d), U("appr", d), no_later(k("apprd", d), dd)), "approk", d),
            no(Or(Not(U("early", d)), Not(U("appr", d)), before(dd, k("apprd", d))), "approk", d),
            yes(And(listed, Not(need)), "maydisc", d),
            yes(And(listed, need, ok), "maydisc", d),
            no(And(Not(listed), Not(law)), "maydisc", d),
            no(And(need, Not(ok), st), "maydisc", d)]


def _emergency(d, ctx):
    """Unit 36 (R10): without pre-authorization; should immediately contact / email the Foundation."""
    lereq, thr, em, disc = U("lereq", d), U("threat", d), U("emerg", d), U("disc", d)
    listed, need, law = U("listed", d), U("needappr", d), U("lawreq", d)
    return [yes(And(listed, Not(need)), "nopre", d),
            no(need, "nopre", d),
            no(And(Not(listed), Not(law)), "nopre", d),
            yes(And(lereq, thr, disc), "emailnow", d),
            yes(And(lereq, em, Not(disc)), "emailnow", d),
            no(Not(lereq), "emailnow", d),
            no(And(lereq, Not(thr), Not(em)), "emailnow", d)]


def _legal(d, ctx):
    """Unit 37 (R11): all other requests should be directed to the Foundation's legal department."""
    listed, disc, law = U("listed", d), U("disc", d), U("lawreq", d)
    return [yes(Or(And(Not(listed), Not(law)), Not(disc), U("subp", d)), "tolegal", d),
            no(And(listed, disc), "tolegal", d)]


def _ombuds(kk, ctx):
    """Unit 38 (R13): complaints about infringements of this Policy may be submitted to the Ombuds Commission."""
    return [yes(U("infr", kk), "ombuds", kk)]


def _exc_complaint(kk, ctx):
    """Unit 39 (R13)."""
    return [yes(U("excact", kk), "commgov", kk), yes(U("excact", kk), "wmfref", kk),
            yes(And(U("excact", kk), U("ppsec", kk)), "ombuds", kk)]


def _outside(kk, ctx):
    """Unit 40 (R13)."""
    return [yes(U("outside", kk), "commgov", kk)]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


NONE = lambda ctx: []  # noqa: E731
UNITS = {
    1: ("PART", member(_cov_grant), "definition by reference",
        "R1: covered when the Foundation granted access (stated); 'Nonpublic Personal Data covered by the Privacy Policy' is "
        "defined by the Privacy Policy (not pinned): the grant is stated as access to such data"),
    2: ("RULE", member(_cov_kind("tool")), "R1: access to a tool permitting a view of Nonpublic Personal Data (granted)"),
    3: ("RULE", member(_cov_kind("supp")), "R1: the ability to access content removed from administrator view (granted)"),
    4: ("RULE", member(_cov_kind("dev")), "R1: volunteer developers with access (granted)"),
    5: ("PART", per("tests", _exemptions), "other:norm",
        "R3, R4: individual exemptions for age or domicile reviewed by Legal written (they remove the bar); group exceptions "
        "'at its sole discretion' (a permission of the Foundation) carried only as keeping a 'no' from being given; 'listed "
        "publicly' / 'not listed publicly' have no outcome a question can ask"),
    6: ("PART", per("tests", _ok), "other:norm",
        "R2: the minimum requirements before a grant and for a candidacy written; 'The community may require ... additional "
        "community-specified criteria' (a permission to the community) not carried: unmet criteria leave the answer "
        "undetermined when the Policy's requirements are met; LATENT FIX 11-26 (U6): req = (a)-(c) only, the domicile bar "
        "in ok for grant and candidacy tests, not for the (e) compliance check"),
    7: ("RULE", NONE, "lead-in of (a): the age requirements (units 8, 9) are conjuncts of unit 6's test"),
    8: ("RULE", per("tests", _age), "R3: 18, or 16 for email response team members; the birthdays BRIDGED"),
    9: ("RULE", per("tests", _cert), "certified the minimum age for the role, by the day tested"),
    10: ("RULE", per("tests", _email_all), "lead-in of (b): the four email requirements together"),
    11: ("RULE", per("tests", _sub), "a valid email address submitted (validity stated)"),
    12: ("RULE", per("tests", _link), "the account linked to a valid email address"),
    13: ("RULE", per("tests", _verify), "verification completed if requested"),
    14: ("RULE", _cat(per("changes", _week), per("tests", _chgok)), "one week = change day + 7, in Lean (R5)"),
    15: ("PART", per("tests", _cs), "cross-reference",
         "R6: read and certified agreement written; the Confidentiality Agreement itself is not pinned"),
    16: ("RULE", _agreement(16), "R6 (revision 11-25): this Policy states the Agreement outlines this subject; what "
         "the Agreement says on it is not pinned and not written"),
    17: ("RULE", _agreement(17), "R6 (revision 11-25): this Policy states the Agreement outlines this subject; what "
         "the Agreement says on it is not pinned and not written"),
    18: ("RULE", _agreement(18), "R6 (revision 11-25): this Policy states the Agreement outlines this subject; what "
         "the Agreement says on it is not pinned and not written"),
    19: ("RULE", _agreement(19), "R6 (revision 11-25): this Policy states the Agreement outlines this subject; what "
         "the Agreement says on it is not pinned and not written"),
    20: ("RULE", _agreement(20), "R6 (revision 11-25): this Policy states the Agreement outlines this subject; what "
         "the Agreement says on it is not pinned and not written"),
    21: ("RULE", _agreement(21), "R6 (revision 11-25): this Policy states the Agreement outlines this subject; what "
         "the Agreement says on it is not pinned and not written"),
    22: ("PART", per("infos", _priv), "cross-reference",
         "R14: 'is subject to' written as a classification; the Privacy Policy and Data Retention Guidelines not pinned"),
    23: ("PART", member(_deadline), "other:norm",
         "R7: the 90 calendar days (Lean) and a stated extension written; 'may, at its sole discretion, extend' (a power of "
         "the Foundation) carried only through the stated extension"),
    24: ("NOT", None, "other:no outcome",
         "'should anticipate having their access rights revoked': no definite outcome (D7)"),
    25: ("NOT", None, "other:no outcome", "introductory description of the section (no outcome)"),
    26: ("NOT", None, "other:no outcome", "a section title kept as a unit by sample5.py (D2(b)); answered on unit 27"),
    27: ("PART", _cat(per("uses", _use), per("datas", _destroy)), "cross-reference",
         "R8: use per the governing tool policy (CheckUser: global, and local unless cross-wiki) and the destroy duty written; "
         "the CheckUser, Suppression and local policies not pinned (their conclusions stated); LATENT FIX 11-26 (U27): the "
         "duty only for data stated to be Nonpublic Personal Data (npd), refused when that is not stated"),
    28: ("RULE", per("discs", _list), "R9: disclosures limited to (i)-(vi)"),
    29: ("RULE", per("discs", _sit(1)), "(i): the recipient's access and 'to fulfill the duties' (stated judgment, D9)"),
    30: ("RULE", per("discs", _sit(2)), "(ii)"),
    31: ("RULE", per("discs", _sit(3)), "(iii): 'immediate and credible threat' (stated judgment)"),
    32: ("RULE", per("discs", _sit(4)), "(iv)"),
    33: ("RULE", per("discs", _sit(5)), "(v): 'necessary and incidental', sockpuppet/abusive (stated judgments)"),
    34: ("RULE", per("discs", _sit(6)), "(vi): the Legal Department's authorization through an exception (stated)"),
    35: ("RULE", per("discs", _approval),
         "R9: no obligation; written approval for (ii), (iv) and disclosures required by law; ten business days BRIDGED (the "
         "tenth business day back, bridge); the approval day compared in Lean"),
    36: ("RULE", per("discs", _emergency), "R10: no pre-authorization for (iii) on request; immediately contact / email"),
    37: ("RULE", per("discs", _legal), "R11: all other requests to the legal department"),
    38: ("PART", per("comps", _ombuds), "other:no outcome",
         "R13: may be submitted to the Ombuds Commission written; 'may result in conduct warnings or removal', 'may take "
         "such actions', 'will generally defer' (no definite outcome, D7) not written"),
    39: ("PART", per("comps", _exc_complaint), "cross-reference",
         "R13: evaluated by community governance, referral to the Foundation, Ombuds review on the Privacy Policy section "
         "written; the Office Actions Policy and the Privacy Policy's 'relevant section' not pinned (stated)"),
    40: ("PART", per("comps", _outside), "other:no outcome",
         "R13: evaluated by community governance written; 'may result in loss of the Foundation's trust' (no definite "
         "outcome)"),
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
    """The atoms / day constants a ground rule fixes."""
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
        # shift(a, b, n): defines a, except b10 = lat + 1 which defines lat
        return [f[2][2]] if f[1][2].startswith("b10_") else [f[1][2]]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

BASES_OF = {"member": ("eff", "gd", "extd", "dl"),
            "tests": ("at", "app", "a16", "a18", "certd", "subd", "linkd", "vrqd", "verd", "csd"),
            "changes": ("chgd", "infd", "lim", "askd"),
            "discs": ("dday", "sentd", "apprd", "b10", "lat"),
            "tools": ("revd",), "datas": ("xask",)}


def int_constants(ctx):
    """name -> words for every day constant of the case."""
    out = {}
    for kind, bases in BASES_OF.items():
        xs = [ctx.member] if kind == "member" else getattr(ctx, kind)
        for x in xs:
            for base in bases:
                out[f"{base}_{x}"] = INT_UNITS[base]
    return out


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
    for name, w in int_constants(ctx).items():
        consts[name] = {"sort": "$int", "unit": DAY, "description": f"{w[0].upper() + w[1:]} ({name}).",
                        "verbalisation": f"{w} ({name})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in BINARY.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The member, or a test of the requirements, change of address, "
                                                             "disclosure or request, tool, data, use, complaint or piece of "
                                                             "information the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------
# (except M13, M14, LATENT FIX 11-26: their departures sit behind no question of the set, so run.py reports them
#  killed: False on the set; they are killed by tests/test_wmf_nonpublic_access_latent.py and smoke S19/S20)

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


def _age_m(a, ctx):
    """M2: the email response team exception dropped (16 never applies: 18 for every role)."""
    at, app, a18 = k("at", a), k("app", a), k("a18", a)
    ex, hasapp, unrev = U("exm_age", a), U("hasapp", a), U("exm_unrev", a)
    return [yes(ex, "ageok", a),
            yes(And(no_later(a18, at), Or(Not(hasapp), no_later(a18, app))), "ageok", a),
            no(And(Not(ex), Not(unrev), before(at, a18)), "ageok", a)]


def _age_m3(a, ctx):
    """M3: the Legal-reviewed age exemption ignored (the age limits bind everyone)."""
    at, a16, a18, app = k("at", a), k("a16", a), k("a18", a), k("app", a)
    ert, hasapp = U("ert", a), U("hasapp", a)
    return [yes(And(ert, no_later(a16, at), Or(Not(hasapp), no_later(a16, app))), "ageok", a),
            yes(And(Not(ert), no_later(a18, at), Or(Not(hasapp), no_later(a18, app))), "ageok", a),
            no(And(ert, before(at, a16)), "ageok", a),
            no(And(Not(ert), before(at, a18)), "ageok", a)]


def _m1_week(e, ctx):
    out = _week(e, ctx)
    out[0] = shift(k("lim", e), k("chgd", e), 8)
    return out


def _m5_approval(d, ctx):
    out = _approval(d, ctx)
    out[5] = iff_u("early", d, And(U("sent", d), no_later(k("sentd", d), k("b10", d))))
    return out


def _m7_approval(d, ctx):
    out = _approval(d, ctx)
    s2, law = U("s2", d), U("lawreq", d)
    out[1] = yes(s2, "needappr", d)
    out[3] = no(And(Not(s2), Not(law)), "needappr", d)
    return out


def _m9_use(u, ctx):
    return [iff_u("mayuse", u, And(U("pol", u), Or(Not(U("cu", u)), Not(U("locbad", u)))))]


def _m10_verify(a, ctx):
    at, vd = k("at", a), k("verd", a)
    return [yes(And(U("ver", a), no_later(vd, at)), "verok", a),
            no(Not(U("ver", a)), "verok", a),
            no(And(U("ver", a), before(at, vd)), "verok", a)]


def _m11_ok(a, ctx):
    """M11: (c) dropped from req (LATENT FIX 11-26: on the fixed unit 6, the domicile bar in ok of grants and candidacies)."""
    out = _ok(a, ctx)
    parts = [U(p, a) for p in ("ageok", "certok", "emailok")]
    out[0] = yes(And(*parts), "req", a)
    out[1] = no(Or(*[Not(p) for p in parts]), "req", a)
    return out


def _m13_ok_frozen(a, ctx):
    """M13: the frozen unit 6 (af4991e018): the domicile bar folded into req for every test, the (e) check included."""
    req = U("req", a)
    return [yes(And(U("ageok", a), U("certok", a), U("emailok", a), U("csok", a), U("domok", a)), "req", a),
            no(Or(Not(U("ageok", a)), Not(U("certok", a)), Not(U("emailok", a)), Not(U("csok", a)), Not(U("domok", a))),
               "req", a),
            yes(And(req, Not(U("crit_unmet", a))), "ok", a),
            no(And(Not(req), Not(U("exc", a))), "ok", a)]


def _m14_destroy_frozen(x, ctx):
    """M14: the frozen unit 27 destroy duty (af4991e018): any data from a revoked tool, Nonpublic Personal Data or not."""
    hits = [And(B("from", x, t), U("rev", t), no_later(k("revd", t), k("xask", x))) for t in ctx.tools]
    return [iff_u("destroy", x, Or(*hits))]


def _m12_deadline(m, ctx):
    out = _deadline(m, ctx)
    out[1] = Implies(And(U("holder", m), Not(U("ext", m))), shift(k("dl", m), k("eff", m), 91))
    return out


MUTANTS = {
    "M1": ("THRESHOLD: (b) one week read as eight days",
           _swap(14, lambda b: _cat(per("changes", _m1_week), per("tests", _chgok)))),
    "M2": ("EXCEPTION: (a) the email response team member's 16 dropped (18 for every role)",
           _swap(8, lambda b: per("tests", _age_m))),
    "M3": ("EXEMPTION: an individual age exemption reviewed by Legal ignored", _swap(8, lambda b: per("tests", _age_m3))),
    "M4": ("THRESHOLD: (e) ninety calendar days read as ninety-one", _swap(23, lambda b: member(_m12_deadline))),
    "M5": ("PERIOD: ten business days read as nine (an email on b10 itself accepted)",
           _swap(35, lambda b: per("discs", _m5_approval))),
    "M6": ("LIST: (iii) law enforcement dropped from the list", _swap(31, lambda b: per("discs", lambda d, ctx: [
        iff_u("s3", d, FALSE)]))),
    "M7": ("APPROVAL: (iv) needs no written approval", _swap(35, lambda b: per("discs", _m7_approval))),
    "M8": ("DUTY: the destroy duty on revocation dropped", _swap(27, lambda b: _cat(per("uses", _use), per("datas", lambda x, ctx: [
        iff_u("destroy", x, FALSE)])))),
    "M9": ("LOCAL: CheckUser's local policy applied to cross-wiki checks too",
           _swap(27, lambda b: _cat(per("uses", _m9_use), per("datas", _destroy)))),
    "M10": ("VERIFICATION: verification required whether or not requested", _swap(13, lambda b: per("tests", _m10_verify))),
    "M11": ("CONFIDENTIALITY: (c) dropped from the requirements", _swap(6, lambda b: per("tests", _m11_ok))),
    # REVISION 11-25 (R6)
    "M12": ("AGREEMENT: the account-safeguarding subject (unit 20) read as not outlined",
            _swap(20, lambda b: (lambda ctx: [Not(f) for f in b(ctx)]))),
    # LATENT FIX 11-26: each restores the frozen rule (af4991e018); killed by tests/test_wmf_nonpublic_access_latent.py and
    # smoke S19/S20 (the departures sit behind no question of the set)
    "M13": ("DOMICILE: the frozen unit 6 (the domicile bar inside req, so the (e) compliance check fails on it)",
            _swap(6, lambda b: per("tests", _m13_ok_frozen))),
    "M14": ("NPD: the frozen unit 27 destroy duty (any data from a revoked tool, not only Nonpublic Personal Data)",
            _swap(27, lambda b: _cat(per("uses", _use), per("datas", _m14_destroy_frozen)))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
