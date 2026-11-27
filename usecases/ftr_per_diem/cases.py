"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions (Codex writer).

Encoder: dri-statute-corpus-ftr-per-diem-w-1124 (Opus 5.5), after the translation was committed (ce0c9ba0ff). Each in-scope
question is one sub-case: the items it needs and the case's stated facts for them, transcribed by hand (encode.Sub and
kit.py; conventions E1-E5 in encode.py). The question's form names the atom or value that answers it. "judgement": anything
the encoder decided beyond copying a stated fact (listed as "encoder judgement" on RESULT.md).
PROBES: out-of-scope cases (scope "out": every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from encode import Sub
from kit import day, items, loc, night, trip

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "a599666614d420bd1d7d9af515fa627e1d124179025687561c79db7cb0bab6a6"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

CASES = []
_by = {}


def add(qid, sub, form):
    cid = qid.split("-")[0]
    if cid not in _by:
        _by[cid] = {"id": cid, "subs": [], "judgement": []}
        CASES.append(_by[cid])
    _by[cid]["subs"].append({"spec": sub, "questions": [{"qid": qid, "form": form}]})
    for j in sub.judgement:
        if j not in _by[cid]["judgement"]:
            _by[cid]["judgement"].append(j)


FEB = "2027-02-"


def d(n):
    return f"{FEB}{n:02d}"


def spring(dep, ret, lr="140.00", mr="68.00", brk=None, judgement=(), **kw):
    """The common frame: Boston / Cambridge / Springfield, all CONUS; Springfield's stated rates."""
    s = trip(Sub(judgement), dep=dep, ret=ret, **kw)
    return loc(s, "ls", lr=lr, mr=mr, brk=brk)


def misc(s):
    return s.item("mx", "misc")


BRK68 = ("16.00", "19.00", "28.00", "5.00")

# T001-T003: one day, 08:00 to 20:00 / 19:59 / 20:01
for cid, ret in (("T001", "20:00"), ("T002", "19:59"), ("T003", "20:01")):
    add(f"{cid}-1", spring((d(1), "08:00"), (d(1), ret)), ("yn", "elig", "t"))
add("T001-2", day(spring((d(1), "08:00"), (d(1), "20:00")), "d1", d(1)), ("share", "d1"))
add("T003-2", day(spring((d(1), "08:00"), (d(1), "20:01")), "d1", d(1)), ("amt", "mie", "d1"))

# T004: 08:00 1 Feb to 07:59 2 Feb; conventional $100 (single occupancy $100), tax $10, arrival 23:59 1 Feb
T4 = ((d(1), "08:00"), (d(2), "07:59"))
add("T004-1", spring(*T4), ("yn", "elig", "t"))
s = spring(*T4)
night(s, "n1", d(1), sor="100.00", tax="10.00", arrive=(d(1), "23:59"))
day(s, "d1", d(1))
day(s, "d2", d(2))
add("T004-2", s, ("amt", "pdt", "t"))
s = spring(*T4)
night(s, "n1", d(1), sor="100.00", tax="10.00", arrive=(d(1), "23:59"))
add("T004-3", s, ("amt", "txr", "n1"))
add("T004-4", misc(spring(*T4)), ("yn", "resv", "p"))

# T005: 08:00 1 Feb to 08:00 2 Feb; Albany (alternate, advantageous, authorized) $160 / $80; arrival 00:01 2 Feb


def t5(an=True):
    s = spring((d(1), "08:00"), (d(2), "08:00"), altauth=True, adv=True)
    loc(s, "la", lr="160.00", mr="80.00", tdy=False, alt=True)
    return night(s, "n1", d(1), sor="160.00", tax="16.00", arrive=(d(2), "00:01"), an=an)


add("T005-1", spring((d(1), "08:00"), (d(2), "08:00")), ("yn", "elig", "t"))
add("T005-2", t5(None), ("yn", "claimprev", "n1"))
add("T005-3", t5(None), ("loc", "n1", {"ls": "Springfield", "la": "Albany"}))
s = t5()
day(s, "d1", d(1))
day(s, "d2", d(2))
add("T005-4", s, ("amt", "pdt", "t"))

# T006: 08:00 1 Feb to 18:00 3 Feb; breakdown 16 / 19 / 28 / 5; meals by day; conventional $180, tax $18
T6 = ((d(1), "08:00"), (d(3), "18:00"))
add("T006-1", spring(*T6), ("yn", "elig", "t"))
add("T006-2", day(spring(*T6, brk=BRK68), "d1", d(1), meals=[("ma", "brk", "gov"), ("mb", "lun", "gov"),
                                                               ("mc", "din", "gov")]), ("amt", "mie", "d1"))
add("T006-3", day(spring(*T6, brk=BRK68), "d2", d(2), meals=[("ma", "brk", "comp"), ("mb", "lun", "carrier"),
                                                               ("mc", "din", "regfee")]), ("amt", "mie", "d2"))
add("T006-4", day(spring(*T6, brk=BRK68), "d3", d(3), meals=[("ma", "lun", "gov")]), ("amt", "mie", "d3"))
add("T006-5", night(spring(*T6), "n1", d(1), sor="180.00", tax="18.00", arrive=(d(1), "16:00")), ("amt", "txr", "n1"))
add("T006-6", misc(spring(*T6)).fact("selcom"), ("yn", "fsfr", "p"))
add("T006-7", misc(spring(*T6)), ("yn", "dc5707", "p"))

# T007: Alaska (non-foreign OCONUS); Government quarters $40 fee, $4 tax


def t7():
    s = trip(Sub(), dep=(d(1), "08:00"), ret=(d(2), "18:00"))
    return loc(s, "lk", lr="140.00", mr="68.00", area="nfo")


add("T007-1", t7(), ("yn", "elig", "t"))
add("T007-2", night(t7(), "n1", d(1), ltype="govq", fee="40.00", tax="4.00", arrive=(d(1), "16:00")), ("amt", "lo", "n1"))
add("T007-3", night(t7(), "n1", d(1), ltype="govq", fee="40.00", tax="4.00", arrive=(d(1), "16:00")), ("amt", "txr", "n1"))

# T008: friends; the host's $20 (substantiated, reasonable) and a $10 token
T8 = ((d(1), "08:00"), (d(3), "18:00"))
add("T008-1", spring(*T8), ("yn", "elig", "t"))


def t8():
    s = night(spring(*T8), "n1", d(1), ltype="friends", tax="0.00", arrive=(d(1), "16:00"))
    return items(s, "n1", "hx", [("ha", "20.00", dict(host=True, substr=True, token=False)),
                                 ("hb", "10.00", dict(host=False, token=True))])


add("T008-2", t8(), ("amt", "lo", "n1"))
add("T008-3", t8(), ("yn", "tokok", "n1"))

# T009: nonconventional, no conventional lodging available
add("T009-1", spring(*T8), ("yn", "elig", "t"))
add("T009-2", night(spring(*T8), "n1", d(1), ltype="noncon", pay="110.00", tax="0.00", arrive=(d(1), "16:00"),
                    noconv=True, an=None), ("yn", "ncok", "n1"))

# T010: a personally-owned recreational vehicle; the listed fees and a purchase / sale payment
add("T010-1", spring(*T8), ("yn", "elig", "t"))
s = night(spring(*T8), "n1", d(1), ltype="rv", tax="0.00", arrive=(d(1), "16:00"))
s.fact("rvown", "n1", True)   # stated ("a personally-owned recreational vehicle"); field added by fidfix-ftr-per-diem-1126,
#                               encoded by a fresh Opus encoder seat that saw only this case and question (fix/encoder2/)
RVL = dict(rvl=True, rvbuy=False)
items(s, "n1", "rvx", [("va", "20.00", RVL), ("vb", "4.00", RVL), ("vc", "4.00", RVL), ("vd", "3.00", RVL),
                       ("ve", "5.00", RVL), ("vf", "6.00", RVL), ("vg", "2.00", RVL), ("vh", "2.00", RVL),
                       ("vi", "2.00", RVL), ("vj", "2.00", RVL),
                       ("vk", "90.00", dict(rvl=False, rvbuy=True)), ("vl", "30.00", dict(rvl=False, rvbuy=True))])
add("T010-2", s, ("amt", "lo", "n1"))

# T011: a personally-owned residence outside any relocation; the January costs during an authorized relocation
add("T011-1", spring(*T8), ("yn", "elig", "t"))
add("T011-2", night(spring(*T8), "n1", d(1), ltype="por", tax="0.00", arrive=(d(1), "16:00"), reloc=False),
    ("amt", "lo", "n1"))
s = spring(*T8, judgement=["T011-3: the $600 real estate purchase expense is entered as an expense of unit 22's kinds "
                           "(the question names it under the personally-owned-residence exclusion)"])
items(s, "p", "porx", [("pa", "800.00", dict(por=True, reloc=True)), ("pb", "600.00", dict(por=True, reloc=True))])
add("T011-3", s, ("yn", "barany", "p"))

# T012-T014: long-term lodging
LX0 = dict(frent=False, urent=False, furn=False, necf=False, util=False, maid=False, reasm=False, phone=False, net=False,
           typ=False, inst=False, ldist=False)


def lx(**kw):
    f = dict(LX0)
    f.update(kw)
    return f


def longterm(s, n, rows, asked=()):
    s.item("lt", "lt", "t")
    s.n["lt"] = n
    items(s, "lt", "lx", rows)
    for x in asked:
        s.link[(x, "asked")] = True
    return s


T12 = ((d(1), "08:00"), (d(11), "18:00"))
add("T012-1", spring(*T12), ("yn", "elig", "t"))
ROWS12 = [("ka", "800.00", lx(urent=True)), ("kb", "100.00", lx(furn=True, necf=True)),
          ("kc", "80.00", lx(furn=True, necf=True)), ("kd", "20.00", lx(util=True)), ("ke", "20.00", lx(util=True)),
          ("kf", "40.00", lx(util=True)), ("kg", "30.00", lx(maid=True, reasm=True)),
          ("kh", "30.00", lx(maid=True, reasm=True)), ("ki", "20.00", lx(phone=True)), ("kj", "20.00", lx(net=True)),
          ("kk", "40.00", lx(typ=True)), ("kl", "25.00", lx(inst=True)), ("km", "15.00", lx(ldist=True)),
          ("kn", "35.00", lx(inst=True))]
add("T012-2", longterm(spring(*T12), 10, ROWS12), ("amt", "dlr", "lt"))
add("T012-3", longterm(spring(*T12), 10, ROWS12, asked=("kl", "km", "kn")), ("yn", "anyinc", "p"))

T13 = ((d(1), "08:00"), (d(15), "18:00"))
add("T013-1", spring(*T13, lr="120.00", mr="80.00"), ("yn", "elig", "t"))
add("T013-2", longterm(spring(*T13, lr="120.00", mr="80.00"), 10, [("ka", "2000.00", lx(frent=True))]), ("amt", "dlr", "lt"))
s = longterm(spring(*T13, lr="120.00", mr="80.00"), 10, [("ka", "2000.00", lx(frent=True))])
night(s, "n2", d(2), ltype="noncon", tax="0.00", noconv=True)
s.link[("n2", "lt")] = "lt"
add("T013-3", s, ("amt", "lo", "n2"))

T14 = ((d(1), "08:00"), (d(11), "18:00"))
add("T014-1", spring(*T14, lr="120.00", mr="80.00"), ("yn", "elig", "t"))
add("T014-2", longterm(spring(*T14, lr="120.00", mr="80.00"), 10, [("ka", "2400.00", lx(frent=True))]), ("amt", "dlr", "lt"))

# T015: curtailed for official purposes; two non-refundable deposits, a refund sought for one
T15 = ((d(1), "08:00"), (d(2), "18:00"))
add("T015-1", spring(*T15), ("yn", "elig", "t"))
add("T015-2", items(spring(*T15), "t", "pp", [("pa", "100.00", dict(curt=True, nonref=True, tried=True))]),
    ("yn", "ppok", "pa"))
add("T015-3", items(spring(*T15), "t", "pp", [("pb", "100.00", dict(curt=True, nonref=True, tried=False))]),
    ("yn", "ppok", "pb"))

# T016: no travel performed; two forfeited advance room deposits
add("T016-1", spring((d(1), "08:00"), (d(2), "18:00"), offtr=False, paid=None), ("yn", "elig", "t"))
add("T016-2", spring((d(8), "08:00"), (d(9), "18:00"), offtr=False, paid=None), ("yn", "elig", "t"))
add("T016-3", items(spring((d(1), "08:00"), (d(2), "18:00"), offtr=False, paid=None), "t", "dep",
                    [("da", "50.00", dict(failed=True, unacc=False, forf=True))]), ("yn", "repay", "da"))
add("T016-4", items(spring((d(8), "08:00"), (d(9), "18:00"), offtr=False, paid=None), "t", "dep",
                    [("db", "50.00", dict(failed=True, unacc=True, forf=True))]), ("yn", "repay", "db"))

# T017-T021: rest periods (Paris / Versailles / Rome, foreign; T021 CONUS)


def foreign(tdy_name="lr"):
    s = trip(Sub(), dep=(d(1), "06:00"), ret=(d(6), "22:00"))
    return loc(s, tdy_name, lr="140.00", mr="68.00", area="frgn")


def rest(s, legs, hours, minutes=0, **facts):
    s.item("r", "rp", "t").facts_("r", **facts)
    s.val("rh", "r", hours).val("rn", "r", minutes)
    for i, (h, m) in enumerate(legs):
        g = f"g{chr(97 + i)}"
        s.item(g, "leg", "r").val("lh", g, h).val("lm", g, m)
    return s


LEGS14 = ((2, 0), (10, 0), (2, 0))
LEGS1401 = ((2, 0), (10, 0), (2, 1))
FRG = dict(ocon=False, dcon=False, direct=True, bna=True)
add("T017-1", foreign(), ("yn", "elig", "t"))
add("T017-2", rest(foreign(), LEGS14, 24, coach=True, pe=False, **FRG), ("yn", "mayrest", "r"))
add("T018-1", foreign(), ("yn", "elig", "t"))
add("T018-2", rest(foreign(), LEGS1401, 24, coach=False, pe=True, **FRG), ("yn", "mayrest", "r"))
s = night(foreign(), "n1", d(1), sor="100.00", tax="0.00", arrive=(d(1), "22:01"), rs=True, an=None)
s.link[("n1", "at")] = "lr"
add("T018-3", s, ("loc", "n1", {"lr": "Rome"}))
add("T019-1", foreign(), ("yn", "elig", "t"))
add("T019-2", rest(foreign(), LEGS1401, 26, coach=True, pe=False, nodep=True, firstb=True, reas=True, **FRG),
    ("yn", "mayrest", "r"))
s = foreign()
loc(s, "lm", lr="160.00", mr="80.00", tdy=False, area="frgn")
night(s, "n2", d(2), sor="100.00", tax="0.00", rs=True, an=None)
s.link[("n2", "at")] = "lm"
add("T019-3", s, ("loc", "n2", {"lr": "Rome", "lm": "Milan"}))
add("T020-1", foreign(), ("yn", "elig", "t"))
add("T020-2", rest(foreign(), LEGS1401, 28, coach=True, pe=False, nodep=True, firstb=False, **FRG), ("yn", "mayrest", "r"))
T21 = ((d(1), "06:00"), (d(6), "22:00"))
add("T021-1", spring(*T21), ("yn", "elig", "t"))
add("T021-2", rest(spring(*T21), LEGS1401, 24, coach=False, pe=False, ocon=True, dcon=True, direct=True, bna=True),
    ("yn", "mayrest", "r"))

# T022: non-workdays at the TDY location; a required periodic return
T22 = ((d(1), "08:00"), (d(8), "18:00"))
add("T022-1", spring(*T22), ("yn", "elig", "t"))
add("T022-2", day(spring(*T22), "d6", d(6), nwd=True, stayreq=True, remain=True), ("amt", "mie", "d6"))
add("T022-3", items(spring(*T22), "t", "ret", [("ra", None, dict(reqoff=True))]), ("yn", "mayret", "ra"))
add("T022-4", misc(spring(*T22)), ("yn", "emg30", "p"))

# T023: periodic returns authorized on cost savings / an extended-TDY justification
T23 = ((d(1), "08:00"), (d(28), "18:00"))
add("T023-1", spring(*T23), ("yn", "elig", "t"))
add("T023-2", items(spring(*T23), "t", "ret", [("ra", None, dict(reqoff=False, savings=True, justx=False))]),
    ("yn", "mayret", "ra"))
add("T023-3", items(spring(*T23), "t", "ret", [("rb", None, dict(reqoff=False, savings=False, justx=True))]),
    ("yn", "mayret", "rb"))

# T024: voluntary returns on non-workdays (6-7 and 13-14 February)
T24 = ((d(1), "08:00"), (d(16), "18:00"))
add("T024-1", spring(*T24), ("yn", "elig", "t"))


def vret(costs, days):
    s = spring(*T24)
    s.item("v", "vret", "t")
    items(s, "v", "rx", [(f"x{chr(97 + i)}", c, {}) for i, c in enumerate(costs)])
    for n in days:
        h, e = f"h{chr(96 + n)}", f"e{chr(96 + n)}"
        night(s, h, d(n), kind="hnight", sor="100.00", tax="0.00")
        day(s, e, d(n), kind="hday")
        s.link[(h, "vr")] = "v"
        s.link[(e, "vr")] = "v"
    return s


add("T024-2", vret(["100.00", "10.00", "10.00", "20.00", "10.00", "10.00", "20.00"], (6, 7)), ("amt", "vr", "v"))
add("T024-3", vret(["300.00", "30.00", "30.00", "40.00", "30.00", "30.00", "40.00"], (13, 14)), ("amt", "vr", "v"))

# T025: Paris (TDY) and Versailles (alternate, advantageous, authorized), foreign; actual expense on 2-4 February


def t25(**kw):
    s = trip(Sub(), dep=(d(1), "08:00"), ret=(d(5), "18:00"), altauth=True, adv=True, **kw)
    loc(s, "lp", lr="100.00", mr="60.00", area="frgn")
    return loc(s, "lv", lr="100.00", mr="60.00", tdy=False, alt=True, area="frgn")


add("T025-1", t25(), ("yn", "elig", "t"))
add("T025-2", night(t25(), "n1", d(1), sor="100.00", tax="10.00", arrive=(d(1), "16:00"), an=None), ("yn", "sepx", "n1"))
add("T025-3", day(t25(), "d2", d(2), aed=True, aemax=True, lesser=False, an=True), ("amt", "cl", "d2"))
CL = lambda **kw: dict(lodg=False, meal=False, **kw)  # noqa: E731
s = day(t25(), "d2", d(2), aed=True, aemax=True, lesser=False, an=True)
items(s, "d2", "cx", [("ca", "100.00", dict(lodg=True, meal=False)), ("cb", "125.00", dict(lodg=False, meal=True)),
                      ("cc", "125.00", dict(lodg=False, meal=True)), ("cd", "125.00", dict(lodg=False, meal=True)),
                      ("ce", "5.00", CL())])
add("T025-4", s, ("yn", "allok", "d2"))
s = day(t25(), "d3", d(3), aed=True, aemax=True, lesser=False, an=True)
items(s, "d3", "cx", [("ca", "100.00", dict(lodg=True, meal=False)), ("cb", "125.00", dict(lodg=False, meal=True)),
                      ("cc", "125.00", dict(lodg=False, meal=True)), ("cd", "126.00", dict(lodg=False, meal=True)),
                      ("ce", "5.00", CL())])
add("T025-5", s, ("yn", "allok", "d3"))
s = day(t25(), "d4", d(4), aed=True, aemax=False, lesser=True, an=True)
s.val("lcl", "d4", "250.00")
add("T025-6", s, ("amt", "cl", "d4"))
add("T025-7", t25(), ("yn", "mayalt", "t"))
add("T025-8", misc(t25()), ("yn", "n70", "p"))

# T026: actual expense; receipts
T26 = ((d(1), "08:00"), (d(3), "18:00"))
add("T026-1", spring(*T26, aem=True), ("yn", "elig", "t"))
add("T026-2", spring(*T26, aem=True), ("yn", "itemize", "t"))
add("T026-3", items(spring(*T26, aem=True), "t", "cx", [("ca", "5.00", dict(lodg=True, meal=False))]), ("yn", "rcpt", "ca"))
add("T026-4", items(spring(*T26, aem=True), "t", "cx", [("cb", "75.00", dict(lodg=False, meal=True))]), ("yn", "rcpt", "cb"))
add("T026-5", items(spring(*T26, aem=True), "t", "cx", [("cc", "75.01", dict(lodg=False, meal=True))]), ("yn", "rcpt", "cc"))

# T027: full M&IE claims
T27 = ((d(1), "08:00"), (d(5), "18:00"))
add("T027-1", spring(*T27), ("yn", "elig", "t"))
add("T027-2", day(spring(*T27, brk=BRK68), "d2", d(2), meals=[("ma", "lun", "gov")], allowfull=True, offbiz=True),
    ("yn", "full", "d2"))
s = day(spring(*T27, brk=BRK68), "d3", d(3), meals=[("ma", "din", "gov")], allowfull=True, offbiz=False, medrel=True,
        subst=True, advk=True, reqb=True, effort=True)
s.val("rqd", "d3", "2027-01-29")
add("T027-3", s, ("amt", "mie", "d3"))
add("T027-4", day(spring(*T27, brk=BRK68), "d4", d(4), meals=[("ma", "lun", "gov")], allowfull=True, offbiz=False,
                  medrel=True, subst=True, advk=False), ("amt", "mie", "d4"))

# T028, T029: reduced per diem


def red(dep, ret, ta, **kw):
    s = spring(dep, ret, redp=True, redadv=True, **kw)
    s.val("rlr", "t", "80.00").val("rmr", "t", "40.00")
    if ta is not None:
        s.val("tad", "t", ta)
    return s


T28 = ((d(1), "08:00"), (d(3), "18:00"))
add("T028-1", spring(*T28), ("yn", "elig", "t"))
add("T028-2", red(*T28, "2027-01-30", redta=True), ("yn", "redok", "t"))
add("T028-3", day(red(*T28, "2027-01-30", redta=True), "d2", d(2), redx=True), ("amt", "mie", "d2"))
T29 = ((d(1), "08:00"), (d(5), "18:00"))
add("T029-1", spring(*T29), ("yn", "elig", "t"))
add("T029-2", red(*T29, None, redta=False, suff=True), ("yn", "redok", "t"))

# T030: Tokyo to Honolulu and back across the dateline; offsets UTC+09 / UTC+09 at the residence
T30 = dict(dep=("2027-02-03", "10:00"), ret=("2027-02-04", "10:00"), zoned=(540, 540), idl=True)
add("T030-1", trip(Sub(), **T30), ("yn", "elig", "t"))
add("T030-2", trip(Sub(), **T30), ("yn", "useel", "t"))
add("T030-3", trip(Sub(), **T30), ("yn", "ge24", "t"))

# T031-T034: must the agency pay (training; pre-employment interview)
TT = ((d(1), "08:00"), (d(3), "18:00"))
add("T031-1", spring(*TT, geta=True, agree=True), ("yn", "mustpay", "t"))
add("T032-1", spring(*TT, geta=True, agree=False), ("yn", "mustpay", "t"))
add("T033-1", spring(*TT, intv=True, intauth=False), ("yn", "mustpay", "t"))
add("T034-1", spring(*TT, intv=True, intauth=True), ("yn", "mustpay", "t"))

# T035: Government ship; the agency's $40 for each calendar day
s = trip(Sub(), dep=(d(1), "08:00"), ret=(d(2), "08:01"), ship=True)
loc(s, "lv", lr="140.00", mr="68.00")
s.val("shr", "t", "40.00")
add("T035-1", trip(Sub(), dep=(d(1), "08:00"), ret=(d(2), "08:01"), ship=True), ("yn", "elig", "t"))
add("T035-2", day(s, "d1", d(1)), ("amt", "mie", "d1"))

PROBES = {
    "T036": "out of scope: the per diem rate table of a named location (not pinned; the brief's probe list)",
    "T037": "out of scope: the income tax treatment of an extended TDY (301-11.601-.604 out; WTA, ETTRA)",
    "T038": "out of scope: airfare and class of travel",
    "T039": "out of scope: mileage rates",
    "T040": "out of scope: emergency travel under part 301-30",
    "T041": "out of scope: a private company's travel rules",
    "T042": "out of scope: a State government's travel rules",
    "T043": "out of scope: relocation allowances",
}
PROBE_QIDS = {"T036": ["T036-1"], "T037": ["T037-1", "T037-2"], "T038": ["T038-1", "T038-2"], "T039": ["T039-1"],
              "T040": ["T040-1"], "T041": ["T041-1"], "T042": ["T042-1"], "T043": ["T043-1"]}
UNSUPPORTED = {}
