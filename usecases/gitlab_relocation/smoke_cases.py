"""Made-up smoke cases for the GitLab relocation translation, each answer worked by hand from the readings R1-R16 (written
before any writer's question existed). EXPECT: qid -> the hand answer ("yes"/"no"/a number/a date/conditions/"OPEN")."""
from encode import Sub
from translation import EMB_NAMES

CASES, EXPECT = [], {}
PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}


def case(cid, subs):
    CASES.append({"id": cid, "subs": subs})


def q(qid, form, exp):
    EXPECT[qid] = exp
    return {"qid": qid, "form": form}


def person(fed=False, tzrole=False, rolereq=False):
    return Sub().fact("fed", "p", fed).fact("tzrole", "p", tzrole).fact("rolereq", "p", rolereq)


def place(s, x, name=None, onlist=False, reqnot=False, reqapp=False, chg=False, mail=False):
    s.place(x, name, None if name in EMB_NAMES else onlist)
    return s.fact("reqnot", x, reqnot).fact("reqapp", x, reqapp).fact("chg", x, chg).fact("mail", x, mail)


def stay(s, x, pl, first, last, mgr=True, gnot=False, gapp=False, canfz=True, nv=False, own=True, reqg=False):
    s.stay(x, pl, first, last)
    return (s.fact("mgr", x, mgr).fact("gnot", x, gnot).fact("gapp", x, gapp).fact("canfz", x, canfz).fact("nv", x, nv)
            .fact("own", x, own).fact("reqg", x, reqg))


# S1: one stay in Spain from 1 January (R1-R3, R7, R9). 2027 has 365 days, 2028 366.
for i, (y, last, exp) in enumerate((
        ("2027", "2027-07-02", {"resok": "OPEN", "comp": "no", "ltr": "OPEN", "mx": "OPEN", "outok": "OPEN"}),  # 183 out, 182 in
        ("2027", "2027-07-01", {"resok": "yes", "comp": "no", "ltr": "OPEN", "st": "OPEN", "outok": "yes"}),    # 182 out, 183 in
        ("2028", "2028-07-01", {"resok": "yes", "comp": "no", "ltr": "OPEN", "mx": "183", "outok": "yes"}),     # 183 / 183
        ("2027", "2027-07-03", {"resok": "no", "comp": "yes", "ltr": "OPEN", "outok": "no"}),                   # 184 out
        ("2027", "2027-07-04", {"resok": "no", "comp": "yes", "ltr": "yes", "mustltr": "yes", "st": "no"}),     # 185 out
        ("2027", "2027-06-30", {"resok": "yes", "comp": "no", "ltr": "no", "mustltr": "no", "st": "yes"}))):    # 181 out
    s = person().year(y)
    place(s, "es")
    stay(s, "s1", "es", f"{y}-01-01", last)
    qs = []
    for pred, e in exp.items():
        form = ("num", "mx", "y") if pred == "mx" else ("yn", pred, "y" if pred in ("resok", "outok") else "es")
        qs.append(q(f"S1{i}-{pred}", form, e))
    case(f"S1{i}", [{"spec": s, "questions": qs}])

# S2: two places in 2027: Spain 1 Feb - 30 Apr (89 days), Italy 1 Jun - 30 Sep (122 days): 211 outside.
s = person().year("2027")
place(s, "es")
place(s, "it")
stay(s, "s1", "es", "2027-02-01", "2027-04-30")
stay(s, "s2", "it", "2027-06-01", "2027-09-30")
case("S2", [{"spec": s, "questions": [q("S2-1", ("yn", "resok", "y"), "no"), q("S2-2", ("yn", "outok", "y"), "no"),
                                      q("S2-3", ("yn", "st", "es"), "yes"), q("S2-4", ("yn", "ltr", "it"), "no"),
                                      q("S2-5", ("yn", "workok", "s1"), "OPEN")]}])

# S3: one 10-day trip in 2027 (R4, R5, R8).
TRIPS = [  # (cid, place kwargs, stay kwargs, person kwargs, expected)
    ("S30", {"name": "cuba"}, {}, {}, {"workok": "no", "devok": "no"}),
    ("S31", {}, {}, {}, {"workok": "yes", "devok": "yes", "expok": "no", "batp": "no", "outok": "yes"}),
    ("S32", {}, {"mgr": False}, {}, {"workok": "no", "devok": "yes", "outok": "no"}),
    ("S33", {"reqnot": True}, {"gnot": False}, {}, {"workok": "no", "devok": "OPEN"}),
    ("S34", {"reqnot": True}, {"gnot": True}, {}, {"workok": "yes", "devok": "yes"}),
    ("S35", {}, {"canfz": False}, {"tzrole": True}, {"workok": "no"}),
    ("S36", {}, {"own": False}, {}, {"expok": "OPEN", "workok": "yes"}),
    ("S37", {"name": "russia"}, {}, {}, {"workok": "no", "devok": "no"}),
    ("S38", {"onlist": True}, {}, {}, {"workok": "no"}),
    ("S39", {}, {}, {"rolereq": True}, {"workok": "OPEN"}),
]
for cid, pkw, skw, ekw, exp in TRIPS:
    s = person(**ekw).year("2027")
    place(s, "c", **pkw)
    stay(s, "s1", "c", "2027-05-01", "2027-05-10", **skw)
    case(cid, [{"spec": s, "questions": [q(f"{cid}-{pred}", ("yn", pred, "y" if pred == "outok" else "s1"), e)
                                         for pred, e in exp.items()]}])


# S4: relocation requests (R10-R12).
def request(cid, name=None, onlist=False, ent=True, opn=True, restr=False, cap=False, newposs=False, objund=False, fed=False,
            tcc=False, elig=True, rtw=True, biz=True, start="2025-03-15", rd="2026-03-15", preq=True, exp=None, wpre=True,
            nopred=()):
    s = person(fed=fed)
    s.place("d", name, None if name in EMB_NAMES else onlist)   # R6: a place the embargo list does not name: stated
    for f, v in (("ent", ent), ("open", opn), ("restr", restr), ("cap", cap), ("newposs", newposs), ("objund", objund)):
        s.fact(f, "d", v)
    s.item("r", "req", "d").fact("tcc", "r", tcc).fact("elig", "r", elig).fact("rtw", "r", rtw).fact("biz", "r", biz)
    s.fact("preq", "r", preq).val("rd", "r", rd).start(start)
    if wpre is not None:     # R17 (condition (i)); None: the case does not state it
        s.fact("wpre", "r", wpre)
    for unit, text in nopred:   # encoder rule E5
        s.nopred(unit, text)
    qs = []
    for pred, e in exp.items():
        form = ("which", "r") if pred == "which" else ("date", "tn", "p") if pred == "tn" else ("yn", pred, "r")
        qs.append(q(f"{cid}-{pred}", form, e))
    case(cid, [{"spec": s, "questions": qs}])


request("S40", exp={"acc": "yes", "which": "none", "eligrel": "yes", "ten": "yes", "tn": "2026-03-15", "famcost": "no",
                    "spons": "no"})
request("S41", rd="2026-03-14", exp={"acc": "no", "which": "the one year tenure", "ten": "no", "eligrel": "no"})
request("S42", biz=False, exp={"acc": "no", "which": "business approval", "eligrel": "yes"})
request("S43", cap=True, exp={"acc": "no", "which": "a formed entity open for hiring with no hiring restrictions or "
                                                    "headcount cap"})
request("S44", name="netherlands", elig=False, rtw=False, exp={"acc": "OPEN", "felig": "OPEN", "spons": "OPEN",
                                                                "famcost": "no"})
request("S45", name="china", fed=True, exp={"acc": "no", "ffed": "yes"})
request("S46", name="ethiopia", fed=True, tcc=True, exp={"acc": "yes", "ffed": "no"})
request("S47", name="russia", exp={"acc": "no", "femb": "yes"})
request("S48", elig=False, exp={"acc": "no", "felig": "yes", "frtw": "no"})
request("S49", ent=False, opn=False, newposs=True, exp={"acc": "no", "fnew": "yes", "fent": "yes"})
request("S4a", name="china", fed=False, exp={"acc": "yes", "ffed": "no"})
request("S4b", preq=False, exp={"mvok": "no"})
# Row statute-corpus-gitlab-relocation-wrong-r035 (R17, E5), added after the frozen run.
PRE = "written pre-approval from the functional Vice President and People Business Partner"
request("S4c", wpre=False, exp={"acc": "no", "which": PRE, "eligrel": "yes", "fpre": "yes"})
request("S4d", wpre=None, exp={"acc": "OPEN", "which": "OPEN", "eligrel": "yes", "fpre": "OPEN"})
request("S4e", wpre=None, cap=True, exp={"acc": "no", "eligrel": "no", "which": "OPEN"})
request("S4f", nopred=[(26, "the team member's work permit is under appeal")], exp={"acc": "OPEN", "eligrel": "OPEN",
                                                                                    "famcost": "no"})
request("S4h", cap=True, nopred=[(26, "the team member's work permit is under appeal")], exp={"acc": "no"})
request("S4g", nopred=[(30, "the team member has not yet reviewed benefit changes")], exp={"acc": "yes", "eligrel": "yes"})

# S5: a planned stay in the leap year 2028: Italy 10 Jan - 9 Mar (60 days); the Spain stay from 1 June can end on 1 Oct.
s = person().year("2028")
place(s, "it")
place(s, "es")
stay(s, "s1", "it", "2028-01-10", "2028-03-09")
s.item("x", "plan", "es").val("ps", "x", "2028-06-01")
case("S5", [{"spec": s, "questions": [q("S5-1", ("date", "pl", "x"), "2028-10-01"), q("S5-2", ("num", "mx", "y"), "183")]}])
s = person().year("2027")
place(s, "es")
s.item("x", "plan", "es").val("ps", "x", "2027-06-01")
case("S6", [{"spec": s, "questions": [q("S6-1", ("date", "pl", "x"), "OPEN")]}])

# S7 (R18, row statute-latent-tour-gitlab-relocation-U15, added after the frozen run): Spain whose only child is a planned
# stay from 1 January 2027 (length not stated), permanent location not changing, no mail there: no long-term NO, no
# short-term YES, no compensation NO (the frozen R7-R9 counted it as 0 days: M18-M20). S7b: the same plan beside a 32-day
# stay. S7c: the same plan with a change of permanent location: long-term YES, not short-term.
for cid, stays, chg, exp in (("S7", (), False, {"mustltr": "OPEN", "ltr": "OPEN", "st": "OPEN", "comp": "OPEN"}),
                             ("S7b", (("2027-01-01", "2027-02-01"),), False,
                              {"mustltr": "OPEN", "ltr": "OPEN", "st": "OPEN", "comp": "OPEN"}),
                             ("S7c", (), True, {"mustltr": "yes", "ltr": "yes", "st": "no", "comp": "OPEN"})):
    s = person().year("2027")
    place(s, "es", chg=chg)
    s.item("x", "plan", "es").val("ps", "x", "2027-01-01")
    for i, (a, b) in enumerate(stays):
        stay(s, f"s{i + 1}", "es", a, b)
    case(cid, [{"spec": s, "questions": [q(f"{cid}-{a}", ("yn", a, "es"), v) for a, v in exp.items()]}])

# S8 (R19, row statute-latent-tour-gitlab-relocation-U11-mail, added after the frozen run): Spain, 32 stated days, permanent
# location not changing, mail delivered to an address there: no compensation NO, as no long-term NO / short-term YES (the
# frozen R9 answered no: M21). S8b: the same with no mail there: the frozen answers. S8c: 200 days with mail: yes.
for cid, last, mail, exp in (("S8", "2027-02-01", True, {"ltr": "OPEN", "st": "OPEN", "comp": "OPEN"}),
                             ("S8b", "2027-02-01", False, {"ltr": "no", "st": "yes", "comp": "no"}),
                             ("S8c", "2027-07-19", True, {"ltr": "yes", "st": "no", "comp": "yes"})):
    s = person().year("2027")
    place(s, "es", mail=mail)
    stay(s, "s1", "es", "2027-01-01", last)
    case(cid, [{"spec": s, "questions": [q(f"{cid}-{a}", ("yn", a, "es"), v) for a, v in exp.items()]}])
