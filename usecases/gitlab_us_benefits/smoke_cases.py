"""Made-up smoke cases for the GitLab US benefits translation, each answer worked by hand from the readings (not from any
writer's case: none existed when this file was written). EXPECT: qid -> the hand answer ("yes"/"no"/an amount/a
date/a number/"OPEN")."""
from encode import Sub
import bridge as B

CASES, EXPECT = [], {}
PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}
DEP_FLAGS = ("sp", "dpn", "ch", "oth", "gl", "ownc", "dis")


def case(cid, subs):
    CASES.append({"id": cid, "subs": subs})


def q(qid, form, exp):
    EXPECT[qid] = exp
    return {"qid": qid, "form": form}


def one(cid, s, *qs):
    case(cid, [{"spec": s, "questions": list(qs)}])


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


# S1: 30 hours, start 2027-01-04 -> eligible; sign-up last day 2027-02-03; sign-ups on 02-03 (yes) and 02-04 (no)
s = Sub().val("hrs", "p", "30").val("sd", "p", "2027-01-04").item("e1", "enr").val("dt", "e1", "2027-02-03")
s.item("e2", "enr").val("dt", "e2", "2027-02-04")
one("S1", s, q("S1-1", ("yn", "elig", "p"), "yes"), q("S1-2", ("date", "sul", "p"), "2027-02-03"),
    q("S1-3", ("date", "bst", "p"), "2027-01-04"), q("S1-4", ("yn", "suok", "e1"), "yes"), q("S1-5", ("yn", "suok", "e2"), "no"))
one("S2", Sub().val("hrs", "p", "29"), q("S2-1", ("yn", "elig", "p"), "no"))
# S3-S6: the waiver allowance (R3)
s = Sub().val("sd", "p", "2027-01-04").fact("plan", val=False).fact("aw").fact("grp", val=False)
one("S3", s, q("S3-1", ("amt", "wamt", "p"), "150.00"), q("S3-2", ("yn", "optc", "p"), "no"))
s = Sub().val("sd", "p", "2027-01-04").fact("plan", val=False).fact("aw", val=False).fact("grp")
one("S4", s, q("S4-1", ("amt", "wamt", "p"), "OPEN"), q("S4-2", ("yn", "wal", "p"), "OPEN"))
s = Sub().val("sd", "p", "2027-01-04").fact("plan").val("pcd", "p", "2027-01-20").fact("med").fact("aw", val=False)
s.fact("grp", val=False)
one("S5", s, q("S5-1", ("amt", "wamt", "p"), "0.00"))
s = Sub().val("sd", "p", "2027-01-04").fact("plan").val("pcd", "p", "2027-01-10").fact("med", val=False).fact("aw")
s.fact("grp")
one("S6", s, q("S6-1", ("amt", "wamt", "p"), "150.00"), q("S6-2", ("yn", "dvok", "p"), "yes"))
# S7-S11: family members (R4)
one("S7", dep(Sub().val("hrs", "p", "40"), "d", sp=True), q("S7-1", ("yn", "covd", "d"), "yes"))
s = Sub().val("hrs", "p", "40")
dep(s, "d1", "25", ch=True)
dep(s, "d2", "26", ch=True)
dep(s, "d3", "27", ch=True)
dep(s, "d4", "30", ch=True, dis=True)
one("S8", s, q("S8-1", ("yn", "covd", "d1"), "yes"), q("S8-2", ("yn", "covd", "d2"), "OPEN"),
    q("S8-3", ("yn", "covd", "d3"), "no"), q("S8-4", ("yn", "covd", "d4"), "yes"))
one("S9", dep(Sub().val("hrs", "p", "40"), "d", "60", oth=True), q("S9-1", ("yn", "covd", "d"), "no"))
one("S10", dep(Sub().val("hrs", "p", "40"), "d", sp=True, gl=True, ownc=True), q("S10-1", ("yn", "covd", "d"), "no"),
    q("S10-2", ("yn", "twice", "d"), "no"))
one("S11", dep(Sub().val("hrs", "p", "25"), "d", sp=True), q("S11-1", ("yn", "covd", "d"), "OPEN"))
# S12: the Domestic Partner Affidavit (R5)
s = Sub()
dep(s, "d1", dpn=True, nh=False, oe=False)
dep(s, "d2", dpn=True, nh=True, oe=False)
one("S12", s, q("S12-1", ("yn", "aff", "d1"), "yes"), q("S12-2", ("yn", "aff", "d2"), "no"))
# S13: qualifying life events (R6): marriage 2027-05-10 -> last day 2027-06-09
s = Sub()
for e, sbd in (("v1", "2027-06-09"), ("v2", "2027-06-10")):
    s.item(e, "ev").fact("mar", e).fact("oe", e, False).val("evd", e, "2027-05-10").val("sbd", e, sbd)
s.item("v3", "ev").fact("oe", "v3", False).val("evd", "v3", "2027-05-10").val("sbd", "v3", "2027-05-12")
for f in ("mar", "div", "birth", "adopt", "spemp"):
    s.fact(f, "v3", False)
one("S13", s, q("S13-1", ("yn", "chgok", "v1"), "yes"), q("S13-2", ("yn", "chgok", "v2"), "no"),
    q("S13-3", ("date", "evl", "v1"), "2027-06-09"), q("S13-4", ("yn", "chgok", "v3"), "OPEN"),
    q("S13-5", ("yn", "qle", "v3"), "OPEN"))
# S14: states (R7)
one("S14a", Sub().fact("hi").fact("ca", val=False), q("S14a-1", ("yn", "cigok", "p"), "no"),
    q("S14a-2", ("yn", "kaiok", "p"), "yes"))
one("S14b", Sub().fact("hi", val=False).fact("ca"), q("S14b-1", ("yn", "cigok", "p"), "yes"),
    q("S14b-2", ("yn", "kaiok", "p"), "yes"))
one("S14c", Sub().fact("hi", val=False).fact("ca", val=False).fact("ut"), q("S14c-1", ("yn", "kaiok", "p"), "no"),
    q("S14c-2", ("yn", "imh", "p"), "yes"))
# S15: HSA (R8)
one("S15a", Sub().fact("hdhp").fact("tmo"), q("S15a-1", ("amt", "hsac", "p"), "100.00"))
one("S15b", Sub().fact("hdhp").fact("tmo", val=False), q("S15b-1", ("amt", "hsac", "p"), "125.00"))
one("S15c", Sub().fact("hdhp", val=False), q("S15c-1", ("amt", "hsac", "p"), "0.00"), q("S15c-2", ("yn", "hsael", "p"), "no"))
# S16: basic life (R10)
for i, (sal, exp) in enumerate((("200000.00", "400000.00"), ("250000.00", "500000.00"), ("300000.00", "500000.00"))):
    one(f"S16{i}", Sub().val("sal", "p", sal), q(f"S16{i}-1", ("amt", "bl", "p"), exp), q(f"S16{i}-2", ("amt", "adnd", "p"), exp))
# S17: the 401(k) match (R12)
for i, (rate, earn, exp) in enumerate((("10", "40000.00", "1200.00"), ("6", "60000.00", "1500.00"),
                                       ("3", "40000.00", "OPEN"), ("6", "50000.00", "1500.00"), ("0", "80000.00", "0.00"))):
    one(f"S17{i}", Sub().val("rate", "p", rate).val("earn", "p", earn), q(f"S17{i}-1", ("amt", "match", "p"), exp))
# S18: the loan (R12)
for i, (vb, exp) in enumerate((("60000.00", "30000.00"), ("100000.00", "50000.00"), ("150000.00", "50000.00"))):
    one(f"S18{i}", Sub().val("vb", "p", vb), q(f"S18{i}-1", ("amt", "loan", "p"), exp))
# S19: return to work 2027-08-20 -> last day 2027-08-15 (R11)
s = Sub()
for r, snt in (("r1", "2027-08-15"), ("r2", "2027-08-16")):
    s.item(r, "rtw").val("ret", r, "2027-08-20").val("snt", r, snt).fact("phys", r)
one("S19", s, q("S19-1", ("yn", "rtok", "r1"), "yes"), q("S19-2", ("yn", "rtok", "r2"), "no"),
    q("S19-3", ("date", "rtl", "r1"), "2027-08-15"))
# S20: the 26 weeks (R11)
s = Sub().item("s1", "dsb").weeks("s1", 26, 1).item("s2", "dsb").weeks("s2", 20).item("s3", "dsb").weeks("s3", 26)
one("S20", s, q("S20-1", ("yn", "unpaid", "s1"), "yes"), q("S20-2", ("yn", "ltdap", "s2"), "no"),
    q("S20-3", ("yn", "cobop", "s3"), "OPEN"))
# S21: 66.7% (R11)
one("S21a", Sub().val("sal", "p", "100000.00"), q("S21a-1", ("amt", "dmax", "p"), "66700.00"))
one("S21b", Sub().val("sal", "p", "100001.00"), q("S21b-1", ("amt", "dmax", "p"), "OPEN"))
# S22: FSA rollover and election (R14, D9)
for i, (left, ro, forf) in enumerate((("4.00", "0.00", "yes"), ("5.00", "OPEN", "OPEN"), ("6.00", "6.00", "no"),
                                      ("680.00", "680.00", "no"), ("700.00", "680.00", "no"))):
    s = Sub().item("f", "fsa").fact("y26", "f").val("left", "f", left)
    one(f"S22{i}", s, q(f"S22{i}-1", ("amt", "ro", "f"), ro), q(f"S22{i}-2", ("yn", "forf", "f"), forf))
# (latent fix U88, 2026-11-25: the $3,400 test needs a stated Medical or Limited Purpose FSA; the frozen S22e stated no
# type and asked yes/no, now f1 is a Medical FSA and f2 a Limited Purpose FSA)
s = Sub().item("f1", "fsa").fact("y26", "f1").fact("mf", "f1").val("el", "f1", "3400.00").item("f2", "fsa")
s.fact("y26", "f2").fact("lpf", "f2").val("el", "f2", "3500.00")
one("S22e", s, q("S22e-1", ("yn", "elok", "f1"), "yes"), q("S22e-2", ("yn", "elok", "f2"), "no"))
# S22d (latent fix U88): a 2026 Dependent Care FSA election of $5,000, and an FSA of no stated type: not decided
s = Sub().item("f1", "fsa").fact("y26", "f1").fact("dc", "f1").val("el", "f1", "5000.00").item("f2", "fsa")
s.fact("y26", "f2").val("el", "f2", "5000.00")
one("S22d", s, q("S22d-1", ("yn", "elok", "f1"), "OPEN"), q("S22d-2", ("yn", "elok", "f2"), "OPEN"))
# S22y (latent fix U90): a Medical FSA, $600 left in a plan year that is not 2026: not decided; $4 left: $0 (any year)
s = Sub().item("f1", "fsa").fact("y26", "f1", False).fact("mf", "f1").val("left", "f1", "600.00").item("f2", "fsa")
s.fact("y26", "f2", False).fact("mf", "f2").val("left", "f2", "4.00")
one("S22y", s, q("S22y-1", ("amt", "ro", "f1"), "OPEN"), q("S22y-2", ("amt", "ro", "f2"), "0.00"))
one("S23", Sub().fact("hsa"), q("S23-1", ("yn", "mfsaok", "p"), "no"), q("S23-2", ("yn", "lpfok", "p"), "yes"))
# S24: Dependent Care FSA (R14): plan year ends 2026-12-31 -> March 15 / 31 2027; runout 2027-03-31
s = Sub()
dep(s, "d1", "12", ch=True)
dep(s, "d2", "13", ch=True)
one("S24a", s, q("S24a-1", ("yn", "dcq", "d1"), "yes"), q("S24a-2", ("yn", "dcq", "d2"), "no"))
s = Sub().val("pye", "p", "2026-12-31")
for x, xd, sbd in (("c1", "2027-03-15", "2027-03-31"), ("c2", "2027-03-16", "2027-03-31"), ("c3", "2027-03-15", "2027-04-01")):
    s.item(x, "x").fact("dc", x).fact("mf", x, False).fact("trm", x, False).val("xd", x, xd).val("sbd", x, sbd)
    s.bridge("m15", x, pye="2026-12-31").bridge("m31", x, pye="2026-12-31")
one("S24b", s, q("S24b-1", ("yn", "clmok", "c1"), "yes"), q("S24b-2", ("yn", "clmok", "c2"), "no"),
    q("S24b-3", ("yn", "clmok", "c3"), "no"))
# S25: claims after termination 2027-05-01 -> 2027-07-30 (R14)
s = Sub().val("trd", "p", "2027-05-01")
for x, sbd in (("c1", "2027-07-30"), ("c2", "2027-07-31")):
    s.item(x, "x").fact("trm", x).fact("mf", x).fact("dc", x, False).val("sbd", x, sbd)
one("S25", s, q("S25-1", ("yn", "clmok", "c1"), "yes"), q("S25-2", ("yn", "clmok", "c2"), "no"),
    q("S25-3", ("date", "ctl", "c1"), "2027-07-30"))
# S26: runout after 2027-12-31 (leap 2028) -> 2028-03-30; the Dependent Care FSA's March 31 then conflicts -> refused
s = Sub().val("pye", "p", "2027-12-31")
for x, sbd in (("c1", "2028-03-30"), ("c2", "2028-03-31")):
    s.item(x, "x").fact("mf", x).fact("dc", x, False).fact("trm", x, False).val("sbd", x, sbd)
s.item("c3", "x").fact("dc", "c3").fact("mf", "c3", False).fact("trm", "c3", False).val("xd", "c3", "2028-03-01")
s.val("sbd", "c3", "2028-03-31").bridge("m15", "c3", pye="2027-12-31").bridge("m31", "c3", pye="2027-12-31")
one("S26", s, q("S26-1", ("yn", "clmok", "c1"), "yes"), q("S26-2", ("yn", "clmok", "c2"), "no"),
    q("S26-3", ("yn", "clmok", "c3"), "OPEN"))
# S27: FSA changes (R14): marriage 2027-05-10 reported 05-20; increase 500 -> 2000
s = Sub().item("g", "chg").fact("inc", "g").fact("dec", "g", False).fact("oe", "g", False)
s.item("v", "ev", "g").fact("mar", "v").fact("oe", "v", False).val("evd", "v", "2027-05-10").val("sbd", "v", "2027-05-20")
s.val("orig", "g", "500.00").val("nw", "g", "2000.00")
s.item("c1", "x", "g").val("xd", "c1", "2027-05-09").item("c2", "x", "g").val("xd", "c2", "2027-05-10")
one("S27a", s, q("S27a-1", ("yn", "fok", "g"), "yes"), q("S27a-2", ("yn", "addok", "c1"), "no"),
    q("S27a-3", ("yn", "addok", "c2"), "yes"), q("S27a-4", ("amt", "pre", "g"), "500.00"),
    q("S27a-5", ("amt", "addl", "g"), "1500.00"))
s = Sub().item("g1", "chg").fact("dec", "g1").fact("inc", "g1", False).fact("oe", "g1", False)
s.item("g2", "chg").fact("inc", "g2").fact("dec", "g2", False).fact("oe", "g2", False)
s.item("g3", "chg").fact("dec", "g3").fact("inc", "g3", False).fact("oe", "g3")
one("S27b", s, q("S27b-1", ("yn", "fok", "g1"), "no"), q("S27b-2", ("yn", "fok", "g2"), "no"),
    q("S27b-3", ("yn", "fok", "g3"), "yes"))
# S28: Travel HRA (R15)
s = Sub().fact("cig")
for t, mi, amt in (("t1", "101", "2500.00"), ("t2", "100", "2500.00"), ("t3", "150", "3500.00"), ("t4", "150", "2100.00")):
    s.item(t, "trip").val("mi", t, mi).val("amt", t, amt)
one("S28a", s, q("S28a-1", ("yn", "hraok", "t1"), "yes"), q("S28a-2", ("yn", "hraok", "t2"), "no"),
    q("S28a-3", ("amt", "hpre", "t1"), "2100.00"), q("S28a-4", ("amt", "hpost", "t1"), "400.00"),
    q("S28a-5", ("amt", "hpost", "t3"), "900.00"), q("S28a-6", ("amt", "hpost", "t4"), "0.00"),
    q("S28a-7", ("amt", "hpre", "t2"), "0.00"))
one("S28b", Sub().fact("cig", val=False).item("t", "trip").val("mi", "t", "300"), q("S28b-1", ("yn", "hraok", "t"), "no"))
# S29-S31: bridged dates
one("S29", Sub().item("h", "hc").bridge("nm1", "h", date="2027-03-31"), q("S29-1", ("date", "eff", "h"), "2027-04-01"))
s = Sub()
for y, d in (("y1", "2027-04-06"), ("y2", "2027-04-22"), ("y3", "2027-04-10")):
    s.item(y, "day").val("qd", y, d).bridge("rb5", y, year=2027, calendar=B.MON_FRI).bridge("a22", y, year=2027)
one("S30", s, q("S30-1", ("yn", "roav", "y1"), "no"), q("S30-2", ("yn", "roav", "y2"), "yes"),
    q("S30-3", ("yn", "roav", "y3"), "OPEN"))
s = Sub().item("c", "x").fact("need", "c").bridge("b3", "c", date="2027-04-02", calendar=B.MON_FRI)
one("S31", s, q("S31-1", ("date", "nyl", "c"), "2027-04-07"))
# S32-S34: coverage on a day (R10, R13)
s = Sub().val("sd", "p", "2027-01-04").val("hrs", "p", "40").item("y1", "day").val("qd", "y1", "2027-01-04")
s.item("y2", "day").val("qd", "y2", "2027-01-03")
one("S32", s, q("S32-1", ("yn", "blcov", "y1"), "yes"), q("S32-2", ("yn", "blcov", "y2"), "no"),
    q("S32-3", ("yn", "k401el", "y1"), "yes"))
s = Sub().fact("sl").fact("cont", val=False).val("ld", "p", "2027-06-30").item("y1", "day").val("qd", "y1", "2027-07-01")
s.item("y2", "day").val("qd", "y2", "2027-06-30")
one("S33", s, q("S33-1", ("yn", "slcov", "y1"), "no"), q("S33-2", ("yn", "slcov", "y2"), "OPEN"),
    q("S33-3", ("yn", "slcobra", "p"), "no"), q("S33-4", ("yn", "fee", "y1"), "yes"), q("S33-5", ("yn", "fee", "y2"), "no"))
one("S35a", Sub().val("age", "p", "66").fact("medx", val=False), q("S35a-1", ("yn", "wnp", "p"), "yes"))
one("S35b", Sub().val("age", "p", "60").fact("medx", val=False), q("S35b-1", ("yn", "wnp", "p"), "no"))
one("S36", dep(Sub(), "d", dpn=True, married=False, inh=True), q("S36-1", ("yn", "dpexp", "d"), "no"),
    q("S36-2", ("yn", "dphsa", "d"), "yes"))
one("S37a", Sub().fact("fam", val=False), q("S37a-1", ("amt", "epod", "p"), "10000.00"),
    q("S37a-2", ("num", "epoc", "p"), "50.00"))
one("S37b", Sub().fact("fam"), q("S37b-1", ("amt", "epoo", "p"), "40000.00"))
one("S38", Sub(), q("S38-1", ("num", "bhs", "p"), "3"), q("S38-2", ("num", "stdw", "p"), "26"),
    q("S38-3", ("num", "lcm", "p"), "30"), q("S38-4", ("yn", "vest", "p"), "yes"))
# S39: voluntary plans (R9): birth 2027-03-01 submitted 2027-03-31 (last day 03-31)
s = Sub().item("e1", "enr").fact("nh", "e1").item("e2", "enr").fact("nh", "e2", False).fact("oe", "e2", False)
s.fact("noev", "e2").item("e3", "enr").fact("nh", "e3", False).fact("oe", "e3", False)
s.item("v", "ev", "e3").fact("birth", "v").fact("oe", "v", False).val("evd", "v", "2027-03-01").val("sbd", "v", "2027-03-31")
one("S39", s, q("S39-1", ("yn", "volok", "e1"), "yes"), q("S39-2", ("yn", "volok", "e2"), "no"),
    q("S39-3", ("yn", "volok", "e3"), "yes"))
one("S40a", Sub().val("contr", "p", "1000.00").val("spent", "p", "400.00"), q("S40a-1", ("yn", "cobraok", "p"), "yes"))
one("S40b", Sub().val("contr", "p", "400.00").val("spent", "p", "400.00"), q("S40b-1", ("yn", "cobraok", "p"), "no"))
s = Sub().val("ld", "p", "2027-06-30").fact("cobra", val=False)
for x, xd, mf in (("c1", "2027-06-30", True), ("c2", "2027-07-01", True), ("c3", "2027-07-01", False)):
    s.item(x, "x").fact("mf", x, mf).fact("dc", x, not mf).val("xd", x, xd)
one("S41", s, q("S41-1", ("yn", "xok", "c1"), "yes"), q("S41-2", ("yn", "xok", "c2"), "no"),
    q("S41-3", ("yn", "xok", "c3"), "no"))
