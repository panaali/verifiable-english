"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions (Codex writer).

Encoder: dri-statute-corpus-gitlab-relocation-cw-1125 (Opus 5.5), on top of the FROZEN translation 8b113741bd (ISOLATION.md
D18: translation.py, encode.py and bridge/ unchanged). Each in-scope question is one sub-case: the items it needs and the
case's stated facts for them, transcribed by hand (encode.Sub; conventions E1-E4 there; E4: a fact the case states only for
another question is not entered, so a question's sub-case carries the manager's approval (a stated judgment) only when its
answer needs it). The question's form names the atom or value that answers it. "judgement": anything the encoder decided
beyond copying a stated fact (listed as "encoder judgement" on RESULT.md). Stated facts with no predicate in the translation
(the unwritten units 1, 4, 12, 14, 30: Compass, written VP/PBP pre-approval, insurance, Workday address, benefit review) are
not entered; where a question's answer could turn on one, it is named in that question's judgement.
PROBES: out-of-scope cases (scope "out": every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from encode import Sub
from translation import EMB_NAMES

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "539ee4c55c080c6735b740da0a4b9be38364eb90afd9248e1c80d2df69af1d12"
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


def refuse(qid, why):
    add(qid, Sub(), ("refuse", why))


# --- stays (R001-R021) ----------------------------------------------------------------------------------------------------
# A stay spec: (stay id, place id, place name key or None, onlist, first, last, place facts, stay facts).
# place facts: reqnot, reqapp, ent, chg, mail; stay facts: mgr, gnot, gapp, canfz, nv, own, reqg.


def stays_sub(year, stays, person=None, need=frozenset(), judgement=()):
    """need: which facts to enter: 'days' always; 'work' (emb, mgr, notice/approval, time zone, role, visa+entity);
    'device' (emb, notice/approval); 'ltr' (chg, mail); 'comp' (chg); 'exp' (ltr + own, reqg)."""
    s = Sub(judgement).year(year)
    person = person or {}
    if "work" in need:
        s.fact("tzrole", "p", person.get("tzrole", False)).fact("rolereq", "p", person.get("rolereq", False))
    seen = set()
    for (x, pl, name, onlist, first, last, pf, sf) in stays:
        if pl not in seen:
            seen.add(pl)
            if need & {"work", "device"}:
                s.place(pl, name, None if name in EMB_NAMES else onlist)
                s.fact("reqnot", pl, pf.get("reqnot", False)).fact("reqapp", pl, pf.get("reqapp", False))
                if "work" in need:
                    s.fact("ent", pl, pf.get("ent", True))
            else:
                s.item(pl, "place")
            if need & {"ltr", "exp"}:
                s.fact("chg", pl, pf.get("chg", False)).fact("mail", pl, pf.get("mail", False))
            if "comp" in need:
                s.fact("chg", pl, pf.get("chg", False))
        s.stay(x, pl, first, last)
        if "work" in need:
            s.fact("mgr", x, sf.get("mgr", True)).fact("nv", x, sf.get("nv", False))
            if pf.get("reqnot"):
                s.fact("gnot", x, sf.get("gnot", False))
            if pf.get("reqapp"):
                s.fact("gapp", x, sf.get("gapp", False))
            if person.get("tzrole"):
                s.fact("canfz", x, sf.get("canfz", True))
        if "device" in need and "work" not in need:
            if pf.get("reqnot"):
                s.fact("gnot", x, sf.get("gnot", False))
            if pf.get("reqapp"):
                s.fact("gapp", x, sf.get("gapp", False))
        if "exp" in need:
            s.fact("own", x, sf.get("own", True)).fact("reqg", x, sf.get("reqg", False))
    return s


def st(x, pl, name, first, last, pf=None, sf=None, onlist=False):
    return (x, pl, name, onlist, first, last, pf or {}, sf or {})


ES = lambda x, a, b, **kw: st(x, "es", None, a, b, **kw)  # noqa: E731  Spain: not named by the text, not on the list
PT = lambda x, a, b, **kw: st(x, "pt", None, a, b, **kw)  # noqa: E731  Portugal: likewise


def residence(qid, year, stays):
    add(qid, stays_sub(year, stays, need=set()), ("yn", "resok", "y"))


def outside(qid, year, stays, person=None, judgement=()):
    add(qid, stays_sub(year, stays, person, need={"work"}, judgement=judgement), ("yn", "outok", "y"))


def largest(qid, year, stays):
    add(qid, stays_sub(year, stays, need=set()), ("num", "mx", "y"))


# R001-R004: one Spain stay in 2027 (365 days)
for cid, stays, mx in (("R001", [ES("s1", "2027-01-01", "2027-06-30")], True),
                       ("R002", [ES("s1", "2027-01-01", "2027-06-30"), PT("s2", "2027-08-01", "2027-08-01")], False),
                       ("R003", [ES("s1", "2027-01-01", "2027-07-02")], True),
                       ("R004", [ES("s1", "2027-07-01", "2027-12-31")], False)):
    residence(f"{cid}-1", "2027", stays)
    outside(f"{cid}-2", "2027", stays)
    if mx:
        largest(f"{cid}-3", "2027", stays)

# R005: two Spain stays in 2027
R005 = [ES("s1", "2027-02-01", "2027-04-30"), ES("s2", "2027-06-01", "2027-09-04")]
residence("R005-1", "2027", R005)
outside("R005-2", "2027", R005)
s = stays_sub("2027", R005[:1], need=set())
s.item("x", "plan", "es").val("ps", "x", "2027-06-01")
add("R005-3", s, ("date", "pl", "x"))
add("R005-4", stays_sub("2027", R005, need={"ltr"}), ("yn", "mustltr", "es"))

# R006-R009: 2028 (366 days)
for cid, stays, mx in (("R006", [ES("s1", "2028-01-01", "2028-06-29")], True),
                       ("R007", [ES("s1", "2028-01-01", "2028-06-30")], False),
                       ("R008", [ES("s1", "2028-01-01", "2028-06-30"), PT("s2", "2028-08-01", "2028-08-01")], True),
                       ("R009", [ES("s1", "2028-01-01", "2028-07-02")], False)):
    residence(f"{cid}-1", "2028", stays)
    outside(f"{cid}-2", "2028", stays)
    if mx:
        largest(f"{cid}-3", "2028", stays)

# R010: Spain + Portugal in 2028; the last day the Portugal stay from 1 June can end
R010 = [ES("s1", "2028-02-01", "2028-04-30"), PT("s2", "2028-06-01", "2028-09-03")]
residence("R010-1", "2028", R010)
outside("R010-2", "2028", R010)
s = stays_sub("2028", R010[:1], need=set())
s.item("pt", "place").item("x", "plan", "pt").val("ps", "x", "2028-06-01")
add("R010-3", s, ("date", "pl", "x"))

# R011: Kira, Portugal 1 Sep 2027 - 1 Mar 2028 as two stated stays; digital nomad visa; no entity in Portugal
NV = {"nv": True}
outside("R011-1", "2027", [PT("s1", "2027-09-01", "2027-12-31", pf={"ent": False}, sf=NV)])
outside("R011-2", "2028", [PT("s1", "2028-01-01", "2028-03-01", pf={"ent": False}, sf=NV)])
add("R011-3", stays_sub("2027", [PT("s1", "2027-09-01", "2027-12-31")], need={"ltr"}, judgement=[
    "R011-3: 'this stay' runs 1 Sep 2027 - 1 Mar 2028 (122 + 61 days); the translation counts days per calendar year (R7, "
    "D9: stays split at 31 December): encoded as the 2027 part (122 days); the 2028 part (61 days) gives the same answer"]),
    ("yn", "mustltr", "pt"))

# R012: Lena, Spain 183 days in 2028 with a digital nomad visa where GitLab has an entity
R012 = [ES("s1", "2028-01-01", "2028-07-01", sf=NV)]
add("R012-1", stays_sub("2028", R012, need={"work"}), ("yn", "workok", "s1"))
add("R012-2", stays_sub("2028", R012, need={"comp"}), ("yn", "comp", "es"))
add("R012-3", stays_sub("2028", R012, need={"ltr"}), ("yn", "mustltr", "es"))

# R013: Mina, Portugal 31 days, own decision
R013 = [PT("s1", "2027-03-01", "2027-03-31")]
add("R013-1", stays_sub("2027", R013, need={"exp"}), ("yn", "expok", "s1"))
add("R013-2", stays_sub("2027", R013, need={"ltr"}), ("yn", "mustltr", "pt"))

# R014: Nico, Spain 184 days
R014 = [ES("s1", "2027-07-01", "2027-12-31")]
add("R014-1", stays_sub("2027", R014, need={"ltr"}), ("yn", "ltr", "es"))
add("R014-2", stays_sub("2027", R014, need={"comp"}), ("yn", "comp", "es"))

# R015: Oona, Spain 10 days, mail to the Spain address
R015 = [ES("s1", "2027-05-01", "2027-05-10", pf={"mail": True})]
add("R015-1", stays_sub("2027", R015, need={"ltr"}), ("yn", "mustltr", "es"))
add("R015-2", stays_sub("2027", R015, need={"comp"}), ("yn", "comp", "es"))

# R016: Pia, six stays, Toronto time zone role; manager approved Spain and Italy only; Italy breaks the time zone
R016 = [st("s1", "es", None, "2027-02-01", "2027-02-01", sf={"mgr": True}),
        st("s2", "pt", None, "2027-03-01", "2027-03-01", sf={"mgr": False}),
        st("s3", "fr", None, "2027-04-01", "2027-04-01", sf={"mgr": False}),
        st("s4", "it", None, "2027-05-01", "2027-05-10", sf={"mgr": True, "canfz": False}),
        st("s5", "de", None, "2027-06-01", "2027-06-10", sf={"mgr": False}),
        st("s6", "be", None, "2027-07-01", "2027-07-10", sf={"mgr": False})]
J16 = ["R016: France and Belgium never discussed with the manager: entered as no manager approval (E3)"]
for i, s_ in enumerate(R016, 1):
    add(f"R016-{i}", stays_sub("2027", R016, person={"tzrole": True}, need={"work"},
                               judgement=J16 if i in (3, 6) else ()), ("yn", "workok", s_[0]))

# R017: Quinn, Spain 10 days required by GitLab
R017 = [ES("s1", "2027-04-01", "2027-04-10", sf={"own": False, "reqg": True})]
add("R017-1", stays_sub("2027", R017, need={"exp"}), ("yn", "expok", "s1"))
outside("R017-2", "2027", R017)

# R018: Ravi, Spain needs prior notice (none given), Portugal prior approval (none), France neither
R018 = [st("s1", "es", None, "2027-03-01", "2027-03-01", pf={"reqnot": True}, sf={"gnot": False}),
        st("s2", "pt", None, "2027-04-01", "2027-04-01", pf={"reqapp": True}, sf={"gapp": False}),
        st("s3", "fr", None, "2027-05-01", "2027-05-01")]
for i, s_ in enumerate(R018, 1):
    add(f"R018-{i}", stays_sub("2027", R018, need={"work"}), ("yn", "workok", s_[0]))

# R019: Sara, the five embargoed countries the text names
R019 = [st(f"s{i}", n, n, f"2027-{m:02d}-01", f"2027-{m:02d}-01")
        for i, (n, m) in enumerate((("cuba", 2), ("iran", 3), ("nkorea", 4), ("syria", 5), ("russia", 6)), 1)]
for i, s_ in enumerate(R019, 1):
    add(f"R019-{i}", stays_sub("2027", R019, need={"work"}), ("yn", "workok", s_[0]))
add("R019-6", stays_sub("2027", R019, need={"device"}), ("yn", "devok", "s1"))

# R020: Tari, Belarus and the three Ukrainian regions the text names; Kyiv region stated not on the list
R020 = [st(f"s{i}", n, n, f"2027-{m:02d}-01", f"2027-{m:02d}-01")
        for i, (n, m) in enumerate((("belarus", 2), ("crimea", 3), ("donetsk", 4), ("luhansk", 5)), 1)]
R020.append(st("s5", "kyiv", None, "2027-06-01", "2027-06-01", onlist=False))
for i, s_ in enumerate(R020, 1):
    add(f"R020-{i}", stays_sub("2027", R020, need={"work"}), ("yn", "workok", s_[0]))

# R021: Uma, Brazil stated on the list, Mexico stated not on it
R021 = [st("s1", "br", None, "2027-02-01", "2027-02-01", onlist=True),
        st("s2", "mx", None, "2027-03-01", "2027-03-01", onlist=False)]
add("R021-1", stays_sub("2027", R021, need={"device"}), ("yn", "devok", "s1"))
add("R021-2", stays_sub("2027", R021, need={"device"}), ("yn", "devok", "s2"))
add("R021-3", stays_sub("2027", R021, need={"work"}), ("yn", "workok", "s1"))


# --- relocation requests (R022-R035) ------------------------------------------------------------------------------------

def request(name=None, onlist=False, ent=True, opn=True, restr=False, cap=False, newposs=False, objund=None, fed=False,
            tcc=False, elig=True, rtw=True, biz=True, start="2025-01-01", rd="2027-01-02", judgement=()):
    s = Sub(judgement).fact("fed", "p", fed)
    s.place("d", name, None if name in EMB_NAMES else onlist)
    for f, v in (("ent", ent), ("open", opn), ("restr", restr), ("cap", cap), ("newposs", newposs)):
        s.fact(f, "d", v)
    if objund is not None:
        s.fact("objund", "d", objund)
    s.item("r", "req", "d").fact("tcc", "r", tcc).fact("elig", "r", elig).fact("rtw", "r", rtw).fact("biz", "r", biz)
    s.val("rd", "r", rd).start(start)
    return s


ACC, WHICH, ELIG = ("yn", "acc", "r"), ("which", "r"), ("yn", "eligrel", "r")

add("R022-1", request("china", fed=True), ACC)
add("R022-2", request("china", fed=True, tcc=True, rd="2027-01-03"), ACC)
add("R023-1", request("ethiopia", fed=True), ACC)
add("R023-2", request("ethiopia", fed=True, tcc=True, rd="2027-01-03"), ACC)
add("R024-1", request("belarus", fed=True), WHICH)
add("R024-2", request("belarus", fed=True, tcc=True, rd="2027-01-03"), ACC)
add("R025-1", request("china"), ACC)
add("R025-2", request("ethiopia"), ACC)
add("R025-3", request("belarus"), ACC)
add("R026-1", request("netherlands"), ACC)
add("R026-2", request("netherlands"), ("yn", "famcost", "r"))
add("R027-1", request("netherlands", elig=False, rtw=False), ACC)
add("R027-2", request("netherlands", elig=False, rtw=False), WHICH)
add("R028-1", request(elig=False, rtw=False), ACC)
add("R028-2", request(elig=False, rtw=False), WHICH)

# R029: Cleo, the Spain entity day by day (2-7 January 2027)
J29 = ("R029: the Spain location is unit 23's 'location where there might be the possibility of the formation of a new "
       "entity' on every date (a possibility on 2 January): newposs entered true on 2-7 January; translation R10 (b) reads it "
       "with ent/open/objund (the formula fnew's ok branch needs newposs together with a formed entity)")
for i, (day, kw) in enumerate((
        ("2027-01-02", dict(ent=False, opn=False, restr=False, cap=False, objund=False)),
        ("2027-01-03", dict(ent=True, opn=False, restr=False, cap=False, objund=False)),
        ("2027-01-04", dict(ent=True, opn=True, restr=True, cap=False, objund=False)),
        ("2027-01-05", dict(ent=True, opn=True, restr=False, cap=True, objund=False)),
        ("2027-01-06", dict(ent=True, opn=True, restr=False, cap=False, objund=False)),
        ("2027-01-07", dict(ent=True, opn=True, restr=False, cap=False, objund=True))), 1):
    add(f"R029-{i}", request(newposs=True, rd=day, judgement=[J29], **kw), WHICH)

add("R030-1", request(start="2026-02-02"), ELIG)
add("R030-2", request(start="2026-02-02"), ("date", "tn", "p"))
add("R031-1", request(start="2026-01-02"), ELIG)     # destination Canada (same country), not named, not on the list
add("R031-2", request(start="2026-01-02"), WHICH)
add("R032-1", request(start="2026-01-03"), ELIG)
add("R032-2", request(start="2026-01-03"), ("date", "tn", "p"))
add("R033-1", request(biz=False), ACC)
add("R033-2", request(biz=False), WHICH)

# R034: Hugo, start date 29 February 2028: the bridge fixes no anniversary (D8): refused
for q in ("R034-1", "R034-2", "R034-3"):
    refuse(q, "start date 29 February: the text fixes no anniversary (D8; bridge/bridge.py refuses)")

# R035: Ines, no written VP/PBP pre-approval (unit 4: not written, no outcome; no predicate)
J35 = ("R035: the stated lack of written VP and People Business Partner pre-approval (unit 4), the Compass question (unit 1) "
       "and the benefit review (unit 30) have no predicate (units not written, ledger other:norm): not entered")
add("R035-1", request(judgement=[J35]), WHICH)
add("R035-2", request(judgement=[J35]), ACC)

# --- probes ---------------------------------------------------------------------------------------------------------------
PROBES = {cid: "scope 'out' in questions-enc.jsonl (D14)" for cid in
          ("R036", "R037", "R038", "R039", "R040", "R041", "R042", "R043", "R044", "R045")}
PROBE_QIDS = {f"R0{n}": [f"R0{n}-1"] for n in range(36, 46)}
PROBE_QIDS["R043"] = ["R043-1", "R043-2"]
UNSUPPORTED = {}
