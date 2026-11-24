"""Made-up smoke cases for the GitLab travel-expense translation, each answer worked by hand from the readings (not from any
writer's case). EXPECT: qid -> the hand answer ("yes"/"no"/an amount/a date/"OPEN")."""
from encode import Sub

CASES, EXPECT = [], {}
PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}


def case(cid, subs):
    CASES.append({"id": cid, "subs": subs})


def flight(s, f, *, intl, price, dp, ch, bu, bk, dep, sel, classes=4, bus=3, appr=False, navan=True, segs=((5, 1),)):
    s.item(f, "flight").fact("intl", f, intl).fact("navan", f, navan).fact("appr", f, appr).fact("biz", f)
    s.val("pr", f, price).val("dp", f, dp).val("ch", f, ch).val("bu", f, bu).val("bk", f, bk).val("dep", f, dep)
    s.val("rsel", f, sel).val("rstd", f, 1).val("rbus", f, bus)
    for i, (h, m) in enumerate(segs):
        s.seg(f"{f}s{i + 1}", f, h, m)
    return s


def q(qid, form, exp):
    EXPECT[qid] = exp
    return {"qid": qid, "form": form}


# S1: domestic, 5h30, premium, 190 cm, no approval; price 610 > 1.2 x 500; booked 10 days ahead
s = Sub().fact("incm").val("cm", "p", "190")
flight(s, "f", intl=False, price="610.00", dp="500.00", ch="600.00", bu="20.00", bk="2027-03-01", dep="2027-03-11", sel=2,
       segs=((5, 30),))
case("S1", [{"spec": s, "questions": [q("S1-1", ("yn", "clsok", "f"), "yes"), q("S1-2", ("yn", "flag", "f"), "yes"),
                                      q("S1-3", ("date", "lid", "f"), "2027-02-25"), q("S1-4", ("yn", "ph", "f"), "no")]}])
# S2: international 4h00 + 6h00, premium, 6 ft 7 in with approval -> height permits; booked 30 days ahead, in budget
s = Sub().fact("incm", val=False).val("ft", "p", "6").val("inch", "p", "7")
flight(s, "f", intl=True, price="500.00", dp="500.00", ch="480.00", bu="20.00", bk="2027-03-01", dep="2027-03-31", sel=2,
       appr=True, segs=((4, 0), (6, 0)))
case("S2", [{"spec": s, "questions": [q("S2-1", ("yn", "pdur", "f"), "no"), q("S2-2", ("yn", "clsok", "f"), "yes"),
                                      q("S2-3", ("yn", "flag", "f"), "no"), q("S2-4", ("date", "lid", "f"), "2027-03-10")]}])
# S3: acceptance: booked 2027-03-01 23:30, asked 2027-03-02 23:29 / 23:30
for i, (td, tm, exp) in enumerate((("2027-03-02", "23:29", "no"), ("2027-03-02", "23:30", "yes"))):
    s = Sub().fact("incm").val("cm", "p", "170")
    flight(s, "f", intl=False, price="700.00", dp="500.00", ch="600.00", bu="20.00", bk="2027-03-01", dep="2027-03-20", sel=1)
    s.item("c", "chk").clock("bd", "bm", "c", "2027-03-01", "23:30").clock("td", "tm", "c", td, tm).fact("noact", "c")
    s.fact("apv", "c", False).fact("den", "c", False)
    case(f"S3{i}", [{"spec": s, "questions": [q(f"S3{i}-1", ("yn", "acc", "c"), exp)]}])
s = Sub().item("c", "chk").clock("bd", "bm", "c", "2027-12-31", "08:15")
case("S4", [{"spec": s, "questions": [q("S4-1", ("dt", "c"), "2028-01-01T08:15")]}])
# S5: meals: breakfast 30, dinner 60 + tip 15 (cap 12) -> 102; second day 50 + 70 + tip 0 -> 120 cap
for i, (items, tips, exp) in enumerate(((["30.00", "60.00"], [("15.00", "60.00")], "102.00"),
                                        (["50.00", "70.00"], [("10.00", "70.00")], "120.00"))):
    s = Sub().item("d", "mday").fact("trav", "d")
    for j, a in enumerate(items):
        s.item(f"e{j}", "meal", "d").val("amt", f"e{j}", a)
    for j, (a, b) in enumerate(tips):
        s.item(f"tp{j}", "tip", "d").val("amt", f"tp{j}", a).val("bill", f"tp{j}", b).fact("tipd", f"tp{j}")
    case(f"S5{i}", [{"spec": s, "questions": [q(f"S5{i}-1", ("amt", "rmb", "d"), exp)]}])
# S6: hotel 6 nights at 310 (cap 300), refundable standard, Navan, no extras
s = Sub().item("h", "stay").fact("navan", "h").fact("std", "h").fact("extra", "h", False).fact("airbnb", "h", False)
s.val("ci", "h", "2027-05-01").val("co", "h", "2027-05-07").val("bk", "h", "2027-04-20").val("amt", "h", "310.00")
s.val("dp", "h", "260.00").fact("only", "h", False).fact("block", "h", False)
case("S6", [{"spec": s, "questions": [q("S6-1", ("yn", "dc", "h"), "yes"), q("S6-2", ("amt", "rmb", "h"), "300.00"),
                                      q("S6-3", ("yn", "rep", "h"), "no"), q("S6-4", ("yn", "h20", "h"), "no"), q("S6-6", ("yn", "stdok", "h"), "OPEN"),
                                      q("S6-5", ("yn", "nrok", "h"), "no")]}])
# S7: frequent traveller: 3 trips of 2 x 9h, business for customers
s = Sub().fact("incm").val("cm", "p", "170")
for t in ("t1", "t2", "t3"):
    s.item(t, "trip").fact("intl", t)
    for j in (1, 2):
        s.seg(f"{t}s{j}", t, 9, 0)
flight(s, "f", intl=True, price="900.00", dp="900.00", ch="900.00", bu="0.00", bk="2027-01-01", dep="2027-02-01", sel=3,
       segs=((9, 0),))
s.fact("rcus", "f").fact("rspk", "f", False).fact("rcnf", "f", False)
case("S7", [{"spec": s, "questions": [q("S7-1", ("yn", "clsok", "f"), "yes"), q("S7-2", ("yn", "pfreq", "f"), "yes")]}])
# S8: rental in Spain: buy liability and CDW; rental in Mexico: CDW two outcomes
s = Sub().fact("us").item("r", "car").fact("usca", "r", False).fact("mex", "r", False).fact("outus", "r")
case("S8", [{"spec": s, "questions": [q("S8-1", ("yn", "bboth", "r"), "yes"), q("S8-2", ("yn", "fchad", "r"), "no")]}])
s = Sub().fact("us").item("r", "car").fact("usca", "r", False).fact("mex", "r").fact("outus", "r")
case("S9", [{"spec": s, "questions": [q("S9-1", ("yn", "bcdw", "r"), "OPEN"), q("S9-2", ("yn", "bmxl", "r"), "yes")]}])
# S10: taxis: single 140 -> 140; round trip 320 without approval -> not in full
s = Sub().item("g1", "ground").fact("rt", "g1", False).val("amt", "g1", "140.00").fact("client", "g1").fact("desc", "g1")
s.fact("app73", "g1", False).item("g2", "ground").fact("rt", "g2").val("amt", "g2", "320.00").fact("client", "g2")
s.fact("desc", "g2").fact("app73", "g2", False)
case("S10", [{"spec": s, "questions": [q("S10-1", ("amt", "rmb", "g1"), "140.00"), q("S10-2", ("yn", "full", "g2"), "no")]}])
# S11: travel days: conference 4 days with day before/after -> 6
s = Sub().item("w", "work").val("ws", "w", "2027-06-10").val("we", "w", "2027-06-13").fact("inc", "w").fact("intev", "w", False)
case("S11", [{"spec": s, "questions": [q("S11-1", ("num", "cov", "w"), "6")]}])
# S12: trains: 4 trips of 2 x 5h10, first class, booked 15 days ahead
s = Sub()
for t in ("t1", "t2", "t3", "t4"):
    s.item(t, "ttrip")
    for j in (1, 2):
        s.seg(f"{t}s{j}", t, 5, 10)
s.item("r", "train").fact("navan", "r").val("pr", "r", "100.00").val("dp", "r", "90.00").val("bk", "r", "2027-01-01")
s.val("dep", "r", "2027-01-16").val("rsel", "r", 2).val("rstd", "r", 1).val("rbus", "r", 9)
case("S12", [{"spec": s, "questions": [q("S12-1", ("yn", "tup", "r"), "yes"), q("S12-2", ("yn", "t20", "r"), "no")]}])
