"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions (Codex writer).

Encoder: dri-statute-corpus-gitlab-us-benefits-cw-1125 (Opus 5.5), after the translation was frozen (f8309cf469; no rule,
reading or unit changed here). Each in-scope question is one sub-case: the team member p and the items the question
needs, with the case's stated facts for them, transcribed by hand (encode.Sub; conventions E1-E3 there). The form names
the atom or value that answers it; a question that asks several things at once uses run.py's answer-layer "all"/"any"
forms (marked combined); a part on a unit the translation does not write is ("none", why); a question the translation
cannot answer at all is ("refuse", why). "judgement": anything the encoder decided beyond copying a stated fact (listed
as "encoder judgement" on RESULT.md).
PROBES: out-of-scope cases (scope "out": every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import bridge as B
from encode import Sub

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "e56e87c27598dfe0349ed9b84150fb2abfc081e3a837064de1a06cd3c35bbad1"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

CASES = []
_by = {}
DEP_FLAGS = ("sp", "dpn", "ch", "oth", "gl", "ownc", "dis")


def add(qid, sub, form):
    cid = qid.split("-")[0]
    if cid not in _by:
        _by[cid] = {"id": cid, "subs": [], "judgement": []}
        CASES.append(_by[cid])
    _by[cid]["subs"].append({"spec": sub, "questions": [{"qid": qid, "form": form}]})
    for j in sub.judgement:
        if j not in _by[cid]["judgement"]:
            _by[cid]["judgement"].append(j)


def yn(pred, x, want=True):
    return ("yn", pred, x, want)


def none(why):
    return ("none", why)


def ALL(*parts):
    return ("all", list(parts))


def ANY(*parts):
    return ("any", list(parts))


def REF(why):
    return ("refuse", why)


def tm(sd="2026-01-01", hrs="30", judgement=()):
    """The team member: start date and weekly hours (every case states both)."""
    return Sub(judgement).val("sd", "p", sd).val("hrs", "p", hrs)


def dep(s, d, age=None, **flags):
    s.item(d, "dep")
    for f in DEP_FLAGS:
        s.fact(f, d, flags.get(f, False))
    for f, v in flags.items():
        if f not in DEP_FLAGS:
            s.fact(f, d, v)
    if age is not None:
        s.val("dage", d, age)
    return s


def day(s, y, d):
    return s.item(y, "day").val("qd", y, d)


# --- G001 Maya: 29 hours ------------------------------------------------------------------------------------------------
add("G001-1", tm(hrs="29"), ("yn", "elig", "p"))
add("G001-2", tm(hrs="29"), REF("unit 3 not written (cross-reference: PlanSource Video Library, Accounting and Reporting)"))

# --- G002 Noah: 30 hours, PPO chosen 2026-01-31, salary $200,000 --------------------------------------------------------
add("G002-1", tm().item("e", "enr").val("dt", "e", "2026-01-31"), ALL(yn("elig", "p"), yn("suok", "e")))
add("G002-2", tm(), ("date", "sul", "p"))
add("G002-3", day(tm(), "y", "2026-01-01"), ALL(yn("blcov", "y"), yn("surv", "p"), ("veq", "blcost", "p", "0.00")))
add("G002-4", tm().val("sal", "p", "200000.00"), ("amt", "bl", "p"))

# --- G003 Liam: no plan, no active waiver, no group coverage; tries 2026-02-01; salary $250,000 ------------------------
def liam():
    return tm(hrs="31").fact("plan", val=False).fact("aw", val=False).fact("grp", val=False)


add("G003-1", liam().item("e", "enr").val("dt", "e", "2026-02-01"), ("yn", "suok", "e"))
add("G003-2", liam(), ("amt", "wamt", "p"))
add("G003-3", liam(), ("yn", "optc", "p"))
add("G003-4", liam().val("sal", "p", "250000.00"), ("amt", "bl", "p"))

# --- G004 Ava: group coverage, active waiver 2026-01-30, no GitLab medical plan ------------------------------------------
def ava():
    return tm().fact("grp").fact("aw").fact("plan", val=False)


add("G004-1", ava(), ("amt", "wamt", "p"))
add("G004-2", ava(), ALL(yn("dvok", "p"), none("units 25, 26 not written (dental levels, EyeMed: cross-reference)")))
add("G004-3", ava(), REF("unit 16 not written (other:norm: Flimp PlanSelect, Cigna One Guide)"))

# --- G005 Ethan: group coverage, no plan, no active waiver; salary $300,000 -------------------------------------------
def ethan():
    return tm().fact("grp").fact("aw", val=False).fact("plan", val=False)


add("G005-1", ethan(), ("amt", "wamt", "p"))
add("G005-2", ethan().val("sal", "p", "300000.00"), ("amt", "bl", "p"))

# --- G006 Mia: no group coverage, active waiver, no plan ---------------------------------------------------------------
def mia():
    return tm().fact("grp", val=False).fact("aw").fact("plan", val=False)


add("G006-1", mia(), ("amt", "wamt", "p"))
add("G006-2", mia().item("e", "enr").fact("nh", "e").fact("oe", "e", False),
    ALL(yn("volok", "e"), yn("volat", "p"), none("unit 29 not written (cross-reference: US Benefits Guide)")))
add("G006-3", mia(), ALL(yn("vlife", "p"), none("line 107 not written ('may need to complete an EOI', D12)")))

# --- G007 Oliver: children and a spouse covered as a GitLab team member ------------------------------------------------
add("G007-1", dep(tm(), "d", "25", ch=True), ("yn", "covd", "d"))
add("G007-2", dep(tm(), "d", "26", ch=True), ("yn", "covd", "d"))
s = dep(tm(), "d1", "27", ch=True)
dep(s, "d2", "29", ch=True, dis=False)
add("G007-3", s, ANY(yn("covd", "d1"), yn("covd", "d2")))
add("G007-4", dep(tm(), "d", "28", ch=True, dis=True), ("yn", "covd", "d"))
add("G007-5", dep(tm(), "d", sp=True, gl=True, ownc=True), ("yn", "covd", "d"))

# --- G008 Sophia: HDHP covering herself and her domestic partner (not married), new hire --------------------------------
def sophia(j=()):
    s = tm(judgement=j).fact("ca").fact("hi", val=False).fact("hdhp").fact("tmo", val=False).fact("hsa")
    return dep(s, "d", dpn=True, nh=True, oe=False, married=False, inh=True)


add("G008-1", sophia(), ("yn", "aff", "d"))
add("G008-2", sophia(), ("amt", "hsac", "p"))
add("G008-3", sophia(), ("yn", "dpexp", "d"))
add("G008-4", sophia(("G008-4: the partner on her HDHP (team member + partner) entered as 'covered under your family HDHP' "
                      "(inh)",)), ALL(yn("dphsa", "d"), yn("dpfull", "d")))

# --- G009 James: domestic partner added during open enrollment ---------------------------------------------------------
add("G009-1", dep(tm("2025-01-01", "31"), "d", dpn=True, nh=False, oe=True), ("yn", "aff", "d"))
add("G009-2", tm("2025-01-01", "31").item("e", "enr").fact("nh", "e", False).fact("oe", "e"),
    ALL(yn("volok", "e"), none("unit 10's 'may be taxable / may not be pre-tax eligible' not written (other:norm, D12)")))

# --- G010 Amelia: birth 2026-05-01, change submitted 2026-05-31 -------------------------------------------------------
def birth():
    return tm().item("v", "ev").fact("birth", "v").fact("oe", "v", False).val("evd", "v", "2026-05-01") \
        .val("sbd", "v", "2026-05-31")


add("G010-1", birth(), ("yn", "chgok", "v"))
add("G010-2", dep(tm(), "d", dpn=True, nh=False, oe=False), ("yn", "aff", "d"))
add("G010-3", birth(), ("date", "evl", "v"))

# --- G011 Lucas: five events outside open enrollment ------------------------------------------------------------------
def ev(s, v, kind, evd, sbd):
    s.item(v, "ev").fact("oe", v, False).val("evd", v, evd).val("sbd", v, sbd)
    for f in ("mar", "div", "birth", "adopt", "spemp"):
        s.fact(f, v, f == kind)
    return s


s = ev(tm("2025-01-01"), "v1", "mar", "2026-01-01", "2026-01-31")
ev(s, "v2", "spemp", "2026-03-01", "2026-03-31")
add("G011-1", s, ALL(yn("chgok", "v1"), yn("chgok", "v2")))
s = ev(tm("2025-01-01"), "v1", "adopt", "2026-05-01", "2026-06-01")
ev(s, "v2", "div", "2026-07-01", "2026-08-01")
add("G011-2", s, ANY(yn("chgok", "v1"), yn("chgok", "v2")))
add("G011-3", ev(tm("2025-01-01"), "v", None, "2026-09-01", "2026-09-10"), ("yn", "chgok", "v"))

# --- G012 Charlotte: Hawaii --------------------------------------------------------------------------------------------
add("G012-1", tm().fact("hi").fact("ca", val=False), ("yn", "cigok", "p"))
add("G012-2", tm().fact("hi").fact("ca", val=False), ("yn", "kaiok", "p"))

# --- G013 Henry: California, HDHP team member only ---------------------------------------------------------------------
def henry(j=()):
    return tm(judgement=j).fact("ca").fact("hi", val=False).fact("al", val=False).fact("nj", val=False).fact("hdhp") \
        .fact("tmo").fact("hsa")


add("G013-1", henry(), ("amt", "hsac", "p"))
add("G013-2", henry(), ALL(yn("hstax", "p"), yn("kaiok", "p")))
add("G013-3", henry(), REF("line 106's description ('limited out-of-network benefits') not written (other:norm)"))
add("G013-4", henry(("G013-4: 'the smaller of the two out-of-network deductible figures' entered as the individual tier "
                     "(fam false; the slash read as individual/family, R16)",)).fact("fam", val=False), ("amt", "epod", "p"))

# --- G014 Evelyn: Utah, PPO, no HSA; Medical FSA $4.00 left at the end of 2026 --------------------------------------
def evelyn():
    return tm().fact("ut").fact("hi", val=False).fact("ca", val=False).fact("hdhp", val=False).fact("hsa", val=False)


add("G014-1", evelyn(), ("yn", "hsael", "p"))
add("G014-2", evelyn(), ("yn", "imh", "p"))
add("G014-3", evelyn(), ("yn", "kaiok", "p"))
add("G014-4", evelyn().item("f", "fsa").fact("y26", "f").val("left", "f", "4.00"), ("amt", "ro", "f"))

# --- G015 Benjamin: aged 65, nonmedical withdrawal ---------------------------------------------------------------------
def ben():
    return tm().fact("hdhp").fact("tmo").fact("hsa").val("age", "p", "65").fact("medx", val=False)


add("G015-1", ben(), ("yn", "wnp", "p"))
add("G015-2", ben(), ALL(yn("taxadv", "p"), yn("hroll", "p")))
add("G015-3", ben(), REF("unit 69 not written (cross-reference: the investment minimum is not in the text)"))

# --- G016-G018: the 401(k) ---------------------------------------------------------------------------------------------
def k401(sal, rate, vb):
    return tm().val("sal", "p", sal).val("earn", "p", sal).val("rate", "p", rate).val("vb", "p", vb)


add("G016-1", k401("40000.00", "3", "60000.00"), ("amt", "match", "p"))
add("G016-2", k401("40000.00", "3", "60000.00"), ("amt", "loan", "p"))
add("G016-3", day(k401("40000.00", "3", "60000.00"), "y", "2026-01-01"), ALL(yn("k401el", "y"), yn("vest", "p")))
add("G016-4", k401("40000.00", "3", "60000.00"), REF("units 49, 51, 52 not written (cross-reference, no outcome, "
                                                     "other:norm)"))
add("G017-1", k401("50000.00", "6", "100000.00"), ("amt", "match", "p"))
add("G017-2", k401("50000.00", "6", "100000.00"), ("amt", "loan", "p"))
add("G017-3", k401("50000.00", "6", "100000.00"),
    ALL(none("unit 60 not written (other:norm: request online or call Fidelity)"), yn("ach", "p"), yn("loanat", "p")))
add("G018-1", k401("60000.00", "10", "150000.00"), ("amt", "match", "p"))
add("G018-2", k401("60000.00", "10", "150000.00"), ("amt", "loan", "p"))
add("G018-3", k401("60000.00", "10", "150000.00").fact("conv"),
    ALL(yn("callfid", "p"), yn("prio", "p"), none("unit 54 not written (cross-reference: Fidelity FAQ, webinar)")))
add("G018-4", k401("60000.00", "10", "150000.00").val("cyr", "p", "2026"),
    ALL(yn("convtax", "p"), ("veq", "tyr", "p", "2026"), none("units 57, 58 not written (other:norm: contact Fidelity)")))

# --- G019 Elijah: HSA contribution changes (bridged first of next month) ---------------------------------------------
add("G019-1", tm().fact("hdhp").item("h", "hc").bridge("nm1", "h", date="2026-02-01"), ("date", "eff", "h"))
add("G019-2", tm().fact("hdhp").item("h", "hc").bridge("nm1", "h", date="2026-02-28"), ("date", "eff", "h"))
add("G019-3", tm().fact("hdhp"), REF("units 71, 72 not written (no outcome; other:norm)"))
add("G019-4", tm().fact("hdhp"), REF("units 76-78 and unit 79's 'track your own limits' not written (other:norm)"))

# --- G020 Abigail: HSA; Limited Purpose FSA $5.00 left (2026 limit by the stated reading) ----------------------------
def abigail():
    return tm("2025-01-01").fact("hdhp").fact("hsa")


add("G020-1", abigail(), ("yn", "mfsaok", "p"))
add("G020-2", abigail(), ("yn", "lpfok", "p"))
add("G020-3", abigail().item("f", "fsa").fact("y26", "f").val("left", "f", "5.00"), ("amt", "ro", "f"))

# --- G021 Daniel: Medical FSA $6.00 left ------------------------------------------------------------------------------
def daniel():
    return tm("2025-01-01").fact("hsa", val=False).item("f", "fsa").fact("y26", "f").val("left", "f", "6.00")


add("G021-1", daniel(), ("amt", "ro", "f"))
add("G021-2", daniel(), ("yn", "rouse", "f"))
add("G021-3", daniel(), REF("unit 88's $3,400 is written only as a test of a stated election (elok), not as a value"))
add("G021-4", daniel(), REF("unit 86's April 22 is a bridged comparison date (roav), not a derived value"))

# --- G022 Emily: $680 left; runout claims (plan year ends 2025-12-31) --------------------------------------------------
def emily():
    return tm("2025-01-01").fact("hsa", val=False).val("pye", "p", "2025-12-31")


add("G022-1", emily().item("f", "fsa").fact("y26", "f").val("left", "f", "680.00"), ("amt", "ro", "f"))
for qid, xd, sbd in (("G022-2", "2025-12-01", "2026-03-31"), ("G022-3", "2025-12-02", "2026-04-01")):
    s = emily().item("x", "x").fact("mf", "x").fact("dc", "x", False).fact("trm", "x", False).val("xd", "x", xd)
    add(qid, s.val("sbd", "x", sbd), ("yn", "clmok", "x"))

# --- G023 Michael: Medical FSA $700 left; Dependent Care FSA claims ---------------------------------------------------
add("G023-1", tm("2025-01-01").fact("hsa", val=False).item("f", "fsa").fact("y26", "f").val("left", "f", "700.00"),
    ("amt", "ro", "f"))


def michael(xd, sbd):
    s = dep(tm("2025-01-01").fact("hsa", val=False).val("pye", "p", "2025-12-31"), "d", "12", ch=True, sp=False)
    s.fact("par", "d", False)
    s.item("x", "x").fact("dc", "x").fact("mf", "x", False).fact("trm", "x", False).val("xd", "x", xd).val("sbd", "x", sbd)
    return s.bridge("m15", "x", pye="2025-12-31").bridge("m31", "x", pye="2025-12-31")


add("G023-2", michael("2026-03-15", "2026-03-31"), ALL(yn("dcq", "d"), yn("clmok", "x")))
add("G023-3", michael("2026-03-16", "2026-04-01"), ("yn", "clmok", "x"))

# --- G024 Elizabeth: Dependent Care FSA; last day 2026-06-30 --------------------------------------------------------
TRD = "the termination date entered as the stated last day of work"
s = dep(tm("2025-01-01"), "d", "13", ch=True)
s.fact("par", "d", False)
add("G024-1", s, ("yn", "dcq", "d"))


def eliz(qid, flags, xd, sbd):
    s = tm("2025-01-01", judgement=(f"{qid}: {TRD} (2026-06-30)",)).val("ld", "p", "2026-06-30").val("trd", "p", "2026-06-30")
    dep(s, "d", **flags)
    s.item("x", "x").fact("dc", "x").fact("mf", "x", False).fact("trm", "x").val("xd", "x", xd).val("sbd", "x", sbd)
    return s


add("G024-2", eliz("G024-2", dict(sp=True, disd=True, par=False), "2026-06-29", "2026-09-28"),
    ALL(yn("dcq", "d"), yn("clmok", "x"), yn("xok", "x")))
add("G024-3", eliz("G024-3", dict(par=True, care=True), "2026-06-30", "2026-09-29"), ("yn", "clmok", "x"))

# --- G025 Alexander: Medical FSA $500; marriage 2026-06-01, requests 2026-06-15 -------------------------------------
def alex(j=()):
    return tm("2025-01-01", judgement=j).fact("hsa", val=False)


def chg(s, g, inc, oe=False, marriage=True, orig=None, nw=None):
    s.item(g, "chg").fact("inc", g, inc).fact("dec", g, not inc).fact("oe", g, oe)
    if marriage:
        ev(s, "v" + g, "mar", "2026-06-01", "2026-06-15")
        s.parent["v" + g] = g
    if orig is not None:
        s.val("orig", g, orig).val("nw", g, nw)
    return s


add("G025-1", chg(alex(), "g", True), ("yn", "fok", "g"))
s = chg(alex(), "g1", False)
chg(s, "g2", False, marriage=False)
add("G025-2", s, ANY(yn("fok", "g1"), yn("fok", "g2")))
add("G025-3", chg(alex(), "g", True, marriage=False), ("yn", "fok", "g"))
s = chg(alex(("G025-4: the most of the $700.00 pre-event expense = the original election (pre); the expense exceeds it "
              "(no minimum is a rule of the translation)",)), "g", True, orig="500.00", nw="2000.00")
add("G025-4", s.item("x", "x", "g").val("xd", "x", "2026-05-31"), ("amt", "pre", "g"))
s = chg(alex(("G025-5: the amount of the $1,500.00 post-event expense paid from the additional funds = the additional "
              "funds (addl); the expense equals them (no minimum is a rule of the translation)",)), "g", True,
        orig="500.00", nw="2000.00")
add("G025-5", s.item("x", "x", "g").val("xd", "x", "2026-06-02"), ("amt", "addl", "g"))

# --- G026 Sofia: last day 2026-06-30; supplemental life; Medical FSA --------------------------------------------------
def sofia(j=()):
    return tm("2025-01-01", judgement=j).val("ld", "p", "2026-06-30").fact("sl").fact("cont", val=False) \
        .fact("cobra", val=False).fact("hsa", val=False)


add("G026-1", day(sofia(), "y", "2026-07-01"), ("yn", "slcov", "y"))
add("G026-2", sofia(), REF("no amount rule for a Medical FSA claim (the translation writes only xok / clmok yes/no)"))
add("G026-3", sofia().val("contr", "p", "1000.00").val("spent", "p", "200.00"), ALL(yn("cobraok", "p"), yn("cobpost", "p")))


def sofia_x(qid, sbd):
    s = sofia((f"{qid}: {TRD} (2026-06-30)",)).val("trd", "p", "2026-06-30")
    return s.item("x", "x").fact("trm", "x").fact("mf", "x").fact("dc", "x", False).val("xd", "x", "2026-06-30") \
        .val("sbd", "x", sbd)


add("G026-4", sofia_x("G026-4", "2026-09-28"), ("date", "ctl", "x"))
add("G026-5", sofia_x("G026-5", "2026-09-29"), ("yn", "clmok", "x"))

# --- G027-G029: disability -------------------------------------------------------------------------------------------
def disab(j=()):
    return tm("2025-01-01", judgement=j).fact("qdis")


def rtw(s, ret, snt):
    return s.item("r", "rtw").val("ret", "r", ret).val("snt", "r", snt).fact("phys", "r")


add("G027-1", disab().val("sal", "p", "60000.00"), ("amt", "dmax", "p"))
add("G027-2", rtw(disab(), "2026-07-02", "2026-06-27"),
    ALL(none("line 109's 'you'll need to determine if you can return' not written (other:norm)"), yn("rtok", "r")))
add("G027-3", rtw(disab(), "2026-07-02", "2026-06-27"), ("date", "rtl", "r"))
add("G027-4", disab().item("x", "x").fact("need", "x").bridge("b3", "x", date="2026-01-02", calendar=B.MON_FRI),
    ("date", "nyl", "x"))
add("G028-1", rtw(disab(), "2026-07-09", "2026-07-05"), ("yn", "rtok", "r"))
add("G028-2", disab().item("s", "dsb").weeks("s", 27, 0), ALL(yn("unpaid", "s"), yn("cobop", "s"), yn("ltdap", "s")))
add("G028-3", disab(), ALL(yn("contam", "p"), ("veq", "discost", "p", "0.00"),
                           none("units 43, 44 and line 108's 'as soon as possible' not written")))
add("G029-1", rtw(disab(), "2026-06-15", "2026-06-09"), ("yn", "rtok", "r"))
add("G029-2", tm("2025-01-01"), REF("no amount for a consultation charge (unit 30 is written as the yes/no 'at no cost')"))
add("G029-3", tm("2025-01-01"), ALL(("veq", "bhs", "p", "3"), ("veq", "ldisc", "p", "25"), ("veq", "tdisc", "p", "25"),
                                    none("units 34, 35 not written (no outcome)")))

# --- G030-G035: the Travel HRA ---------------------------------------------------------------------------------------
def trip(mi, amt, cig=True):
    return tm().fact("cig", val=cig).item("t", "trip").val("mi", "t", mi).val("amt", "t", amt)


add("G030-1", trip("99", "2100.00"), ("yn", "hraok", "t"))
add("G030-2", trip("99", "2100.00"), ("amt", "hpre", "t"))
add("G031-1", trip("100", "2500.00"), ("yn", "hraok", "t"))
add("G031-2", trip("100", "2500.00"), ("amt", "hpre", "t"))
add("G032-1", trip("101", "2100.00"), ("amt", "hpre", "t"))
add("G032-2", trip("101", "2100.00"), ("amt", "hpost", "t"))
add("G033-1", trip("101", "2500.00"), ("amt", "hpre", "t"))
add("G033-2", trip("101", "2500.00"), ("amt", "hpost", "t"))
add("G034-1", trip("101", "3500.00"), ("amt", "hpre", "t"))
add("G034-2", trip("101", "3500.00"), ("amt", "hpost", "t"))
add("G034-3", trip("101", "3500.00"), REF("unit 102's 'Navia administers' describes (no outcome)"))
add("G035-1", trip("101", "3500.00", cig=False), ("yn", "hraok", "t"))
add("G035-2", trip("101", "3500.00", cig=False), ("amt", "hpre", "t"))
add("G035-3", day(tm("2025-01-01").val("ld", "p", "2026-06-30"), "y", "2026-07-01"),
    ALL(yn("hkeep", "p"), yn("fee", "y"), none("unit 81 not written ('Fidelity may charge', D12)")))
add("G035-4", tm("2025-01-01").fact("sl").fact("cont", val=False), ANY(yn("slcobra", "p"), yn("dccob", "p")))
add("G035-5", tm("2025-01-01"), REF("no amount rule for a Dependent Care FSA claim (the translation writes only xok / clmok)"))

# --- probes ----------------------------------------------------------------------------------------------------------
PROBES = {cid: "scope 'out' in questions-enc.jsonl (D15)" for cid in
          ("G036", "G037", "G038", "G039", "G040", "G041", "G042", "G043", "G044", "G045")}
PROBE_QIDS = {"G036": ["G036-1", "G036-2"], "G037": ["G037-1", "G037-2"], "G038": ["G038-1"],
              "G039": ["G039-1", "G039-2"], "G040": ["G040-1", "G040-2"], "G041": ["G041-1", "G041-2"],
              "G042": ["G042-1", "G042-2"], "G043": ["G043-1", "G043-2"], "G044": ["G044-1", "G044-2"],
              "G045": ["G045-1"]}
UNSUPPORTED = {}
