"""Transcription helpers for cases.py and smoke_cases.py (FTR per diem). Each helper only copies stated facts into a Sub
(encode.py's conventions E1-E5); nothing is computed here."""
from __future__ import annotations

from encode import Sub

DAY_FALSE = dict(nwd=False, redx=False, rs=False, allowfull=False, aed=False)
NIGHT_FALSE = dict(redx=False, rs=False)
TRIP_FALSE = dict(geta=False, intv=False, idl=False, altauth=False, ship=False, redp=False, aem=False)


def trip(s, *, dep, ret, offtr=True, paid=True, zoned=None, **facts):
    """dep / ret: (YYYY-MM-DD, HH:MM) of departure from and return to the residence, office or other authorized point.
    zoned: (departure offset, return offset) in minutes east of UTC (E2) for a case whose clock times carry offsets."""
    s.item("t", "trip")
    s.clock("dd", "dm", "t", *dep).clock("rd", "rm", "t", *ret)
    if zoned is not None:
        s.zoned.add("t")
        s.val("doff", "t", zoned[0]).val("roff", "t", zoned[1])
    f = dict(TRIP_FALSE)
    f.update(facts)
    s.fact("offtr", "t", offtr)
    if paid is not None:
        s.fact("paidsub", "t", paid)
    s.facts_("t", **f)
    return s


def loc(s, x, *, lr, mr, tdy=True, alt=False, area="conus", brk=None):
    """A location whose rates the case states; brk = (breakfast, lunch, dinner, incidentals) of its M&IE breakdown."""
    s.item(x, "loc", "t").val("lr", x, lr).val("mr", x, mr)
    s.facts_(x, tdyl=tdy, altl=alt, conus=area == "conus", nfo=area == "nfo", frgn=area == "frgn")
    if brk is not None:
        for b, v in zip(("bb", "bl", "bn", "bi"), brk):
            s.val(b, x, v)
    return s


def day(s, x, date, kind="day", meals=(), **facts):
    """meals: [(id, 'brk'|'lun'|'din', provider 'gov'|'regfee'|'carrier'|'comp')]."""
    s.item(x, kind, "t").val("dy", x, date)
    f = dict(DAY_FALSE) if kind == "day" else dict(redx=False, rs=False)
    f.update(facts)
    s.facts_(x, **f)
    for m, which, prov in meals:
        s.item(m, "meal", x)
        s.facts_(m, brk=which == "brk", lun=which == "lun", din=which == "din", gov=prov == "gov",
                 regfee=prov == "regfee", carrier=prov == "carrier", comp=prov == "comp")
    return s


def night(s, x, date, *, kind="night", ltype="conv", sor=None, fee=None, pay=None, tax=None, arrive=None, an=True, **facts):
    """A night of lodging: ltype conv / govq / friends / noncon / rv / por; arrive = (YYYY-MM-DD, HH:MM)."""
    s.item(x, kind, "t").val("ny", x, date)
    s.fact(ltype, x)
    if sor is not None:
        s.val("sor", x, sor)
    if fee is not None:
        s.val("fee", x, fee)
    if pay is not None:
        s.val("pay", x, pay)
    if tax is not None:
        s.val("tx", x, tax)
    if arrive is not None:
        s.arr.add(x)
        s.clock("ad", "am", x, *arrive)
    s.fact("an", x, an)
    f = dict(NIGHT_FALSE)
    f.update(facts)
    s.facts_(x, **f)
    return s


def items(s, parent, kind, rows):
    """rows: [(id, amount, {fact: value})]."""
    for x, amount, facts in rows:
        s.item(x, kind, parent)
        if amount is not None:
            s.val("amt", x, amount)
        s.facts_(x, **facts)
    return s
