"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions (Codex writer).

Encoder: dri-statute-corpus-gitlab-expenses-w-1124 (Opus 5.5), after the translation was committed (96eb3607a5). Each
in-scope question is one sub-case: the items it needs and the case's stated facts for them, transcribed by hand (encode.Sub;
conventions E1-E3 there). The question's form names the atom or value that answers it. "judgement": anything the encoder
decided beyond copying a stated fact (listed as "encoder judgement" on RESULT.md).
PROBES: out-of-scope cases (scope "out": every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from encode import Sub

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "ef1f69a16565669c1ffcb80b71f88c39aac0bdfbf64581e1d19dabd5ebd07f00"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

MILEAGE = "R14: miles x rate is a product of two stated quantities; the language writes no product of two constants"
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


def person(cm=None, ft=None, inch=None, us=None, judgement=()):
    s = Sub(judgement)
    if cm is not None:
        s.fact("incm").val("cm", "p", cm)
    elif ft is not None:
        s.fact("incm", val=False).val("ft", "p", ft).val("inch", "p", inch)
    if us is not None:
        s.fact("us", val=us)
    return s


def flight(s, f, *, intl, price, dp, ch, bu, bk, dep, sel, bus, appr, segs, navan=True, reason=None):
    """E1: the stated classes numbered from 1 (lowest); standard economy = 1."""
    s.item(f, "flight").fact("intl", f, intl).fact("navan", f, navan).fact("appr", f, appr).fact("biz", f)
    s.val("pr", f, price).val("dp", f, dp).val("ch", f, ch).val("bu", f, bu).val("bk", f, bk).val("dep", f, dep)
    s.val("rsel", f, sel).val("rstd", f, 1).val("rbus", f, bus)
    for i, (h, m) in enumerate(segs):
        s.seg(f"{f}s{i + 1}", f, h, m)
    if reason is not None:   # "other": a purpose none of the three (a partner visit)
        for r in ("rcus", "rspk", "rcnf"):
            s.fact(r, f, r == reason)
    return s


def trips(s, ts):
    """The quarter's trips: [(segments)], every listed flight international."""
    for i, segs in enumerate(ts):
        t = f"t{i + 1}"
        s.item(t, "trip").fact("intl", t)
        for j, (h, m) in enumerate(segs):
            s.seg(f"{t}s{j + 1}", t, h, m)
    return s


def chk(s, bd, bt, td, tt, noact, apv=None, den=None):
    s.item("c", "chk").clock("bd", "bm", "c", bd, bt).clock("td", "tm", "c", td, tt).fact("noact", "c", noact)
    if apv is None:
        s.fact("apv", "c", False)
    else:
        s.fact("apv", "c").clock("pd", "pm", "c", *apv)
    if den is None:
        s.fact("den", "c", False)
    else:
        s.fact("den", "c").clock("dd", "dm", "c", *den)
    return s


# --- G001-G007: class of service, flags, acceptance --------------------------------------------------------------------
STD4 = dict(bus=3)   # standard economy, premium economy, business, first


def g001():
    return flight(person(cm="195"), "f", intl=False, price="599.99", dp="500.00", ch="550.00", bu="50.00", bk="2028-02-16",
                  dep="2028-03-01", sel=2, appr=False, segs=[(5, 0)], **STD4)


add("G001-1", g001(), ("yn", "clsok", "f"))
add("G001-2", g001(), ("date", "lid", "f"))
add("G001-3", g001(), ("yn", "flag", "f"))


def g002():
    return flight(person(cm="196"), "f", intl=False, price="600.01", dp="500.00", ch="550.00", bu="50.00", bk="2028-02-17",
                  dep="2028-03-01", sel=2, appr=True, segs=[(5, 1)], **STD4)


add("G002-1", g002(), ("yn", "clsok", "f"))
add("G002-2", g002(), ("yn", "fm", "f"))
for qn, t in (("3", "09:59"), ("4", "10:00"), ("5", "10:01")):
    add(f"G002-{qn}", chk(g002(), "2028-02-17", "10:00", "2028-02-18", t, True), ("yn", "acc", "c"))
add("G002-6", g002(), ("yn", "ph", "f"))


def g003():
    return flight(person(cm="199"), "f", intl=False, price="600.00", dp="500.00", ch="550.00", bu="50.00", bk="2028-03-01",
                  dep="2028-03-15", sel=2, appr=True, segs=[(5, 1), (4, 59)], **STD4)


add("G003-1", g003(), ("yn", "hdur", "f"))
add("G003-2", g003(), ("yn", "flag", "f"))
add("G003-3", chk(g003(), "2028-03-01", "12:00", "2028-03-02", "12:01", False, den=("2028-03-02", "11:59")),
    ("yn", "acc", "c"))


def g004():
    return flight(person(cm="200"), "f", intl=True, price="500.00", dp="500.00", ch="500.00", bu="50.00", bk="2028-02-09",
                  dep="2028-02-29", sel=2, appr=True, segs=[(5, 0)], **STD4)


add("G004-1", g004(), ("yn", "clsok", "f"))
add("G004-2", g004(), ("date", "lid", "f"))
add("G004-3", Sub().item("c", "chk").clock("bd", "bm", "c", "2028-02-09", "08:00"), ("dt", "c"))


def g005():
    return flight(person(cm="201"), "f", intl=True, price="600.00", dp="500.00", ch="550.00", bu="50.00", bk="2028-02-07",
                  dep="2028-02-29", sel=2, appr=False, segs=[(5, 1)], **STD4)


add("G005-1", g005(), ("yn", "clsok", "f"))
add("G005-2", g005(), ("yn", "flag", "f"))
add("G005-3", g005(), ("yn", "ph", "f"))


def g006():
    return flight(person(ft="6", inch="5"), "f", intl=True, price="500.00", dp="500.00", ch="500.00", bu="50.00",
                  bk="2028-02-08", dep="2028-02-29", sel=2, appr=True, segs=[(5, 1), (4, 59)], **STD4)


add("G006-1", g006(), ("yn", "hdur", "f"))
add("G006-2", chk(g006(), "2028-02-08", "09:00", "2028-02-09", "08:59", False, apv=("2028-02-08", "10:00")),
    ("yn", "acc", "c"))


def g007(sel, price):
    # classes: standard economy, business, first
    return flight(person(ft="6", inch="6"), "f", intl=False, price=price, dp="600.00", ch="600.00", bu="50.00",
                  bk="2028-03-01", dep="2028-03-15", sel=sel, bus=2, appr=True, segs=[(4, 59)])


add("G007-1", g007(2, "600.00"), ("yn", "clsok", "f"))
add("G007-2", g007(2, "600.00"), ("yn", "outok", "f"))
add("G007-3", g007(3, "700.00"), ("yn", "clsok", "f"))

# --- G008-G010: frequent traveller --------------------------------------------------------------------------------------


def g008(sel, reason):
    s = trips(person(cm="180"), [[(8, 1), (8, 1), (8, 1)], [(8, 1), (8, 1)]])
    return flight(s, "f", intl=True, price="900.00", dp="900.00", ch="900.00", bu="100.00", bk="2028-03-01",
                  dep="2028-04-01", sel=sel, appr=False, segs=[(8, 1)], reason=reason, **STD4)


add("G008-1", g008(3, "rcus"), ("yn", "pfreq", "f"))
add("G008-2", g008(2, "rcus"), ("yn", "clsok", "f"))
add("G008-3", g008(3, "rspk"), ("yn", "clsok", "f"))
add("G008-4", g008(3, "rcnf"), ("yn", "clsok", "f"))
add("G008-5", g008(3, "other"), ("yn", "clsok", "f"))


def g009(bk, dep, reason):
    s = trips(person(cm="180"), [[(8, 0), (8, 0)]] * 3)
    return flight(s, "f", intl=True, price="900.00", dp="900.00", ch="900.00", bu="100.00", bk=bk, dep=dep, sel=3,
                  appr=False, segs=[(8, 0)], reason=reason, **STD4)


add("G009-1", g009("2028-02-10", "2028-03-10", "rcus"), ("yn", "clsok", "f"))
add("G009-2", g009("2028-03-01", "2028-04-01", "rspk"), ("yn", "clsok", "f"))
add("G009-3", g009("2028-03-01", "2028-04-01", "rcnf"), ("yn", "clsok", "f"))
add("G009-4", g009("2028-03-01", "2028-04-01", "other"), ("yn", "clsok", "f"))


def g010(bk, dep, reason):
    s = trips(person(cm="180"), [[(8, 1), (8, 1)], [(8, 1), (8, 1)], [(8, 1), (8, 1)], [(8, 1), (7, 59)]])
    return flight(s, "f", intl=True, price="900.00", dp="900.00", ch="900.00", bu="100.00", bk=bk, dep=dep, sel=3,
                  appr=False, segs=[(8, 1)], reason=reason, **STD4)


add("G010-1", g010("2028-03-01", "2028-04-01", "rcnf"), ("yn", "clsok", "f"))
add("G010-2", g010("2028-03-10", "2028-04-10", "other"), ("yn", "clsok", "f"))
add("G010-3", g010("2028-02-01", "2028-03-01", "rcus"), ("yn", "clsok", "f"))
add("G010-4", g010("2028-02-10", "2028-03-10", "rspk"), ("yn", "clsok", "f"))

# --- G011: cancellations, unused tickets, points ------------------------------------------------------------------------
add("G011-1", Sub().item("k", "ticket").fact("cant", "k"), ("yn", "lvok", "k"))
add("G011-2", Sub().item("k", "ticket").fact("unused", "k").fact("pers", "k"), ("yn", "persok", "k"))
add("G011-3", Sub().item("k", "ticket").fact("ptsup", "k").val("chg", "k", "30.00"), ("amt", "rmb", "k"))
add("G011-4", Sub().item("k", "ticket").fact("unused", "k").fact("usedwp", "k", False), ("yn", "buyok", "k"))

# --- G012-G015: car rental ----------------------------------------------------------------------------------------------


def car(s, *, navan, bk, pu, sel, rint, conf, rcpt, usca, mex, outus):
    s.item("r", "car").fact("navan", "r", navan).val("bk", "r", bk).val("dep", "r", pu).val("rsel", "r", sel)
    s.val("rint", "r", rint).fact("conf", "r", conf).fact("rcpt", "r", rcpt)
    return s.fact("usca", "r", usca).fact("mex", "r", mex).fact("outus", "r", outus)


def g012():
    return car(person(us=True), navan=True, bk="2028-02-23", pu="2028-03-01", sel=1, rint=1, conf=True, rcpt=True,
               usca=True, mex=False, outus=False)


add("G012-1", g012(), ("yn", "rreimb", "r"))
add("G012-2", Sub().item("u", "fuelx").fact("renting", "u").fact("fuel", "u").val("amt", "u", "300.01"), ("amt", "rmb", "u"))
add("G012-3", Sub().item("u", "fuelx").fact("renting", "u").fact("fuel", "u").fact("mile", "u"), ("yn", "bothok", "u"))
add("G012-4", g012(), ("yn", "bxl", "r"))
add("G012-5", g012(), ("yn", "bcdw", "r"))
add("G012-6", Sub().item("u", "fuelx").fact("renting", "u").fact("fuel", "u").val("amt", "u", "300.00"), ("amt", "rmb", "u"))

J13 = "full-size car class ranked above intermediate (the industry's class order; the text names no order)"


def g013(judgement=()):
    return car(person(us=False, judgement=judgement), navan=False, bk="2028-02-24", pu="2028-03-01", sel=2, rint=1,
               conf=False, rcpt=False, usca=True, mex=False, outus=False)


add("G013-1", g013((J13,)), ("yn", "rclsok", "r"))
add("G013-2", g013(), ("yn", "rflag", "r"))
add("G013-3", g013(), ("date", "lsv", "r"))
add("G013-4", g013(), ("yn", "bcl", "r"))

J14 = "a rental picked up and driven only in Mexico read as one where 'travel to Mexico is required' (unit 24)"


def g014():
    return car(person(us=True, judgement=(J14,)), navan=True, bk="2028-03-01", pu="2028-03-08", sel=1, rint=1, conf=True,
               rcpt=True, usca=False, mex=True, outus=True)


add("G014-1", g014(), ("yn", "bmxl", "r"))
add("G014-2", g014(), ("yn", "bcdw", "r"))


def g015():
    return car(person(us=False), navan=True, bk="2028-03-01", pu="2028-03-08", sel=1, rint=1, conf=True, rcpt=True,
               usca=False, mex=False, outus=True)


add("G015-1", g015(), ("yn", "bboth", "r"))
add("G015-2", g015(), ("yn", "fchad", "r"))

# --- G016-G021: hotels, Airbnb, self stay -------------------------------------------------------------------------------


def stay(s, h, *, navan, std, ci, co, bk, amt, dp=None, extra=False, only=False, block=False, refund=True):
    s.item(h, "stay").fact("navan", h, navan).fact("std", h, std).val("ci", h, ci).val("co", h, co).val("bk", h, bk)
    s.val("amt", h, amt).fact("extra", h, extra).fact("only", h, only).fact("block", h, block).fact("refund", h, refund)
    s.fact("airbnb", h, False)
    if dp is not None:
        s.val("dp", h, dp)
    return s


def g016():
    return stay(Sub(), "h", navan=True, std=True, ci="2028-03-01", co="2028-03-07", bk="2028-02-23", amt="299.99",
                dp="300.00")


add("G016-1", g016(), ("yn", "rep", "h"))
add("G016-2", g016(), ("yn", "dc", "h"))
add("G016-3", g016(), ("amt", "rmb", "h"))


def g017(judgement=()):
    s = stay(Sub(judgement), "h", navan=False, std=True, ci="2028-03-01", co="2028-03-06", bk="2028-02-24", amt="300.00")
    return s.fact("mgr", "h").fact("apadm", "h", False)


add("G017-1", g017(), ("yn", "houtok", "h"))
add("G017-2", g017(), ("date", "lsv", "h"))
add("G017-3", g017(), ("yn", "dc", "h"))
J17 = "hotel parking during the customer-visit stay read as parking 'pertaining to travel to/from ... clients' (unit 69)"
s = g017((J17,))
s.item("i1", "inc", "h").fact("rsv", "i1").fact("mtag", "i1").fact("report", "i1").val("amt", "i1", "40.00")
s.item("i2", "inc", "h").fact("park", "i2").fact("ptag", "i2").fact("client", "i2").fact("desc", "i2").fact("report", "i2")
s.val("amt", "i2", "20.00")
add("G017-4", s, ("yn", "incok", "h"))
add("G017-5", g017().item("i3", "inc", "h").fact("movie", "i3"), ("yn", "claimok", "i3"))


def g018(amt, std, refund, only):
    return stay(Sub(), "h", navan=True, std=std, ci="2028-03-08", co="2028-03-09", bk="2028-03-01", amt=amt, dp="250.00",
                refund=refund, only=only)


add("G018-1", g018("300.01", True, True, False), ("yn", "h20", "h"))
add("G018-2", g018("299.99", True, False, False), ("yn", "nrok", "h"))
add("G018-3", g018("300.00", False, True, False), ("yn", "stdok", "h"))
add("G018-4", g018("300.01", True, True, False), ("amt", "rmb", "h"))
add("G018-5", g018("299.99", True, False, True), ("yn", "nrok", "h"))

s = stay(Sub(), "h", navan=False, std=True, ci="2028-03-08", co="2028-03-09", bk="2028-03-01", amt="301.00", block=True,
         refund=False)
s.fact("corp", "h", False).val("alt", "h", "360.00").fact("excg", "h").val("exc", "h", "301.00").fact("mgr", "h")
s.fact("apadm", "h").fact("perscard", "h").fact("navexp", "h")
add("G019-1", s, ("yn", "blkok", "h"))
for qn, amt in (("2", "359.99"), ("3", "360.01"), ("4", "360.00")):
    add(f"G019-{qn}", stay(Sub(), "h", navan=True, std=True, ci="2028-03-08", co="2028-03-09", bk="2028-03-01", amt=amt,
                           dp="300.00"), ("yn", "h20", "h"))


def airbnb(cheaper):
    s = Sub().item("a", "stay").fact("airbnb", "a").fact("cheaper", "a", cheaper).fact("manual", "a").val("amt", "a", "300.00")
    return s.val("ci", "a", "2028-03-08").val("co", "a", "2028-03-09").val("bk", "a", "2028-03-01")


add("G020-1", airbnb(True), ("yn", "abok", "a"))
add("G020-2", airbnb(False), ("yn", "abperm", "a"))
for qn, amt in (("1", "50.00"), ("2", "50.01")):
    add(f"G021-{qn}", Sub().item("g", "gift").fact("self", "g").fact("approp", "g").val("amt", "g", amt), ("amt", "rmb", "g"))

# --- G022-G024: meals ---------------------------------------------------------------------------------------------------


def mday(food, tip, bill):
    s = Sub().item("d", "mday").fact("trav", "d")
    for j, a in enumerate(food):
        s.item(f"e{j + 1}", "meal", "d").val("amt", f"e{j + 1}", a)
    return s.item("tp", "tip", "d").val("amt", "tp", tip).val("bill", "tp", bill).fact("tipd", "tp")


add("G022-1", mday(["19.99", "40.00", "50.00"], "10.00", "50.00"), ("amt", "rmb", "d"))
add("G022-2", mday(["20.00", "40.00", "50.00"], "10.00", "50.00"), ("amt", "rmb", "d"))
add("G022-3", mday(["19.51", "40.00", "50.00"], "10.50", "50.00"), ("amt", "rmb", "d"))
add("G023-1", Sub().fact("us").item("b", "group").fact("prac", "b", False).fact("senior", "b"), ("yn", "grp", "b"))
add("G023-2", Sub().fact("us").item("b", "group").fact("prac", "b").fact("senior", "b"), ("yn", "grp", "b"))
add("G023-3", Sub().fact("us").item("tp", "tip").fact("cash", "tp").val("amt", "tp", "49.99"), ("yn", "nrc", "tp"))
add("G023-4", Sub().fact("us").item("tp", "tip").fact("cash", "tp").val("amt", "tp", "50.00"), ("yn", "nrc", "tp"))


def tmeal(food, tip):
    s = Sub().fact("us", val=False).item("m", "tmeal").item("e1", "meal", "m").val("amt", "e1", food)
    return s.item("tp", "tip", "m").val("amt", "tp", tip).val("bill", "tp", food).fact("tipd", "tp")


add("G024-1", tmeal("70.00", "10.00"), ("amt", "rmb", "m"))
add("G024-2", tmeal("80.00", "0.01"), ("amt", "rmb", "m"))
add("G024-3", Sub().fact("us", val=False).item("b", "group").fact("prac", "b", False).fact("senior", "b"), ("yn", "grp", "b"))
s = Sub().fact("us", val=False).item("ts", "tipset")
for j, a in enumerate(("49.99", "50.00")):
    s.item(f"tp{j + 1}", "tip", "ts").fact("cash", f"tp{j + 1}").val("amt", f"tp{j + 1}", a)
add("G024-4", s, ("yn", "nrcany", "ts"))

# --- G025-G027: mileage -------------------------------------------------------------------------------------------------
add("G025-1", Sub(), ("refuse", MILEAGE))
add("G025-2", Sub().item("mi", "mileage").val("ent", "mi", "0.60").val("ent2", "mi", "0.50"), ("yn", "ctl", "mi"))
add("G026-1", Sub(), ("refuse", MILEAGE))
add("G027-1", Sub(), ("refuse", MILEAGE))
add("G027-2", Sub().item("u", "fuelx").fact("ev", "u").fact("fuel", "u", False).fact("mile", "u"), ("yn", "bothok", "u"))

# --- G028-G029: trains --------------------------------------------------------------------------------------------------


def train(s, t, *, pr, bk, dep, sel=1):
    s.item(t, "train").fact("navan", t).val("pr", t, pr).val("dp", t, "100.00").val("bk", t, bk).val("dep", t, dep)
    return s.val("rsel", t, sel).val("rstd", t, 1)


def ttrips(s, ts):
    for i, segs in enumerate(ts):
        t = f"t{i + 1}"
        s.item(t, "ttrip")
        for j, (h, m) in enumerate(segs):
            s.seg(f"{t}s{j + 1}", t, h, m)
    return s


add("G028-1", train(Sub(), "tr", pr="119.99", bk="2028-02-16", dep="2028-03-01"), ("yn", "t20", "tr"))
add("G028-2", train(Sub(), "tr", pr="120.00", bk="2028-02-26", dep="2028-03-10"), ("yn", "t20", "tr"))
add("G028-3", train(Sub(), "tr", pr="120.01", bk="2028-03-18", dep="2028-04-01"), ("yn", "t20", "tr"))
add("G028-4", train(Sub(), "tr", pr="119.99", bk="2028-02-16", dep="2028-03-01"), ("date", "lth", "tr"))
add("G028-5", train(ttrips(Sub(), [[(5, 1), (5, 1)], [(5, 1), (5, 1)], [(5, 1), (4, 59)]]), "tr", pr="120.01",
                    bk="2028-03-18", dep="2028-04-01", sel=2), ("yn", "tup", "tr"))
add("G028-6", train(Sub(), "tr", pr="120.00", bk="2028-02-26", dep="2028-03-10"), ("yn", "tlead", "tr"))
add("G029-1", train(ttrips(Sub(), [[(5, 1), (5, 1)]] * 4), "tr", pr="100.00", bk="2028-03-27", dep="2028-04-10", sel=2),
    ("yn", "tup", "tr"))
add("G029-2", Sub().item("cd", "card").val("mo", "cd", 12), ("yn", "rcok", "cd"))
add("G029-3", Sub().item("cd", "card").val("mo", "cd", 1), ("yn", "rcok", "cd"))

# --- G030-G031: ground transport, parking and tolls ---------------------------------------------------------------------


def ground(rt, amt, app):
    return Sub().item("g", "ground").fact("rt", "g", rt).val("amt", "g", amt).fact("client", "g").fact("desc", "g") \
        .fact("app73", "g", app)


def pday(park, toll, app):
    s = Sub().item("pd", "pday").fact("client", "pd").fact("desc", "pd").fact("app73", "pd", app)
    return s.item("g1", "ground", "pd").val("amt", "g1", park).item("g2", "ground", "pd").val("amt", "g2", toll)


add("G030-1", ground(True, "300.00", False), ("amt", "rmb", "g"))
add("G030-2", ground(True, "300.01", True), ("yn", "full", "g"))
add("G030-3", pday("100.00", "50.00", False), ("amt", "rmb", "pd"))
add("G030-4", pday("100.00", "50.01", True), ("yn", "full", "pd"))
add("G031-1", ground(False, "150.00", False), ("amt", "rmb", "g"))
add("G031-2", ground(False, "150.01", False), ("yn", "full", "g"))
add("G031-3", ground(True, "300.01", False), ("yn", "full", "g"))
add("G031-4", pday("100.00", "50.01", False), ("yn", "full", "pd"))
add("G031-5", Sub().item("u", "fuelx").fact("fuel", "u").fact("mile", "u").fact("renting", "u", False), ("yn", "bothok", "u"))

# --- G032-G033: travel days, internet -----------------------------------------------------------------------------------


def work(inc):
    return Sub().item("w", "work").val("ws", "w", "2028-03-08").val("we", "w", "2028-03-10").fact("inc", "w", inc) \
        .fact("intev", "w", False)


add("G032-1", work(True), ("num", "cov", "w"))
for qn, amt in (("2", "50.00"), ("3", "50.01")):
    add(f"G032-{qn}", Sub().item("n", "net").fact("trav", "n").fact("desc", "n").val("amt", "n", amt), ("amt", "rmb", "n"))
add("G033-1", work(False), ("num", "cov", "w"))
add("G033-2", work(False).item("y", "day", "w").val("dy", "y", "2028-03-07"), ("yn", "covd", "y"))

# --- G034-G035: nursing travel, personal trips --------------------------------------------------------------------------


def milk(kind, svc):
    return Sub().fact("nurse").item("mk", "milk").fact(kind, "mk").fact("svc", "mk", svc)


add("G034-1", milk("svcfee", True), ("yn", "mok", "mk"))
add("G034-2", milk("bag", True), ("yn", "mok", "mk"))
add("G034-3", milk("bag", False), ("yn", "mok", "mk"))
s = Sub().fact("nurse").item("ms", "mset")
for x, kind in (("mk1", "cool"), ("mk2", "ship"), ("mk3", "ship")):
    s.item(x, "milk", "ms").fact(kind, x).fact("svc", x, False)
add("G034-4", s, ("yn", "mall", "ms"))
add("G034-5", flight(Sub(), "f", intl=True, price="200.00", dp="200.00", ch="200.00", bu="50.00", bk="2028-03-25",
                     dep="2028-04-08", sel=2, bus=3, appr=False, segs=[(4, 59)]), ("yn", "pdur", "f"))
add("G035-1", Sub().item("ps", "personal").fact("pers", "ps").fact("pbook", "ps").fact("perscard", "ps"), ("yn", "pbok", "ps"))
add("G035-2", Sub().item("ps", "personal").fact("pers", "ps").fact("pbook", "ps"), ("yn", "invok", "ps"))

# --- probes -------------------------------------------------------------------------------------------------------------
PROBES = {cid: "scope 'out' in questions-enc.jsonl (D14)" for cid in
          ("G036", "G037", "G038", "G039", "G040", "G041", "G042", "G043", "G044", "G045")}
PROBE_QIDS = {"G036": ["G036-1", "G036-2"], "G037": ["G037-1"], "G038": ["G038-1"], "G039": ["G039-1"], "G040": ["G040-1"],
              "G041": ["G041-1", "G041-2"], "G042": ["G042-1"], "G043": ["G043-1"], "G044": ["G044-1"],
              "G045": ["G045-1", "G045-2"]}
UNSUPPORTED = {}
