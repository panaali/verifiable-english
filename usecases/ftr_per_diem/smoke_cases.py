"""Made-up smoke cases for the FTR per diem translation, each answer worked by hand from the readings (not from any writer's
case). EXPECT: qid -> the hand answer ("yes"/"no"/an amount/a share value/a location/"OPEN")."""
from encode import Sub
from kit import day, items, loc, night, trip

CASES, EXPECT = [], {}
PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}


def case(cid, subs):
    CASES.append({"id": cid, "subs": subs})


def q(qid, form, exp):
    EXPECT[qid] = exp
    return {"qid": qid, "form": form}


# S1: 07:00 to 20:00 the same day (13 h): eligible, 75 percent of $64 = $48.00
s = trip(Sub(), dep=("2027-03-01", "07:00"), ret=("2027-03-01", "20:00"))
loc(s, "la", lr="150.00", mr="64.00")
day(s, "d1", "2027-03-01")
case("S1", [{"spec": s, "questions": [q("S1-1", ("yn", "elig", "t"), "yes"), q("S1-2", ("share", "d1"), "75"),
                                      q("S1-3", ("amt", "mie", "d1"), "48.00")]}])

# S2: 1 Mar 07:00 to 3 Mar 19:00; $150 / $76 (18, 20, 33, 5)
s = trip(Sub(), dep=("2027-03-01", "07:00"), ret=("2027-03-03", "19:00"))
loc(s, "la", lr="150.00", mr="76.00", brk=("18.00", "20.00", "33.00", "5.00"))
day(s, "d1", "2027-03-01", meals=[("m1", "din", "gov")])                                  # 57 - 33 = 24
day(s, "d2", "2027-03-02", meals=[("m2", "lun", "gov"), ("m3", "brk", "carrier")])       # 76 - 20 = 56
day(s, "d3", "2027-03-03", meals=[("m4", "brk", "regfee"), ("m5", "lun", "regfee"), ("m6", "din", "gov")])  # floor 5
night(s, "n1", "2027-03-01", sor="170.00", tax="17.00", arrive=("2027-03-01", "18:00"))  # 150; tax refused
night(s, "n2", "2027-03-02", sor="120.00", tax="12.00")                                  # 120; tax 12
case("S2", [{"spec": s, "questions": [q("S2-1", ("amt", "mie", "d1"), "24.00"), q("S2-2", ("amt", "mie", "d2"), "56.00"),
                                      q("S2-3", ("amt", "mie", "d3"), "5.00"), q("S2-4", ("amt", "lo", "n1"), "150.00"),
                                      q("S2-5", ("amt", "txr", "n1"), "OPEN"), q("S2-6", ("amt", "txr", "n2"), "12.00"),
                                      q("S2-7", ("amt", "pdt", "t"), "355.00"), q("S2-8", ("share", "d2"), "100")]}])

# S3: exactly 12 hours: not eligible, no M&IE
s = trip(Sub(), dep=("2027-03-01", "06:30"), ret=("2027-03-01", "18:30"))
loc(s, "la", lr="150.00", mr="64.00")
day(s, "d1", "2027-03-01")
case("S3", [{"spec": s, "questions": [q("S3-1", ("yn", "elig", "t"), "no"), q("S3-2", ("share", "d1"), "0")]}])

# S4: rest period: legs 6h + 3h stopover + 5h01 = 14h01; origin CONUS, destination outside; coach; 24 h -> may
s = trip(Sub(), dep=("2027-03-01", "06:00"), ret=("2027-03-09", "20:00"))
s.item("r", "rp", "t").facts_("r", ocon=True, dcon=False, direct=True, bna=True, coach=True, pe=False)
s.val("rh", "r", 24).val("rn", "r", 0)
for g, (h, m) in (("g1", (6, 0)), ("g2", (3, 0)), ("g3", (5, 1))):
    s.item(g, "leg", "r").val("lh", g, h).val("lm", g, m)
case("S4", [{"spec": s, "questions": [q("S4-1", ("yn", "mayrest", "r"), "yes")]}])

# S5: long-term: 900 furnished + 60 utilities + 40 installation; 6 entitled days -> 960 / 6 = 160 -> capped at 140
s = trip(Sub(), dep=("2027-03-01", "06:00"), ret=("2027-03-07", "20:00"))
loc(s, "la", lr="140.00", mr="64.00")
s.item("lt", "lt", "t")
s.n["lt"] = 6
items(s, "lt", "lx", [("ka", "900.00", dict(frent=True)), ("kb", "60.00", dict(util=True)),
                      ("kc", "40.00", dict(inst=True))])
s.link[("kc", "asked")] = True
for f in ("urent", "furn", "maid", "phone", "net", "typ", "ldist", "inst", "util", "frent"):
    for x in ("ka", "kb", "kc"):
        if not (x, f) in (("ka", "frent"), ("kb", "util"), ("kc", "inst")):
            s.fact(f, x, False)
case("S5", [{"spec": s, "questions": [q("S5-1", ("amt", "dlr", "lt"), "140.00"), q("S5-2", ("yn", "anyinc", "p"), "no")]}])

# S6: actual expense: $100 + $50 -> ceiling 450; claims 300 + 151 = 451 -> not all; receipts at 75.00 / 75.01
s = trip(Sub(), dep=("2027-03-01", "06:00"), ret=("2027-03-03", "20:00"), aem=True)
loc(s, "la", lr="100.00", mr="50.00")
day(s, "d2", "2027-03-02", aed=True, aemax=True, lesser=False, an=True)
items(s, "d2", "cx", [("c1", "300.00", dict(lodg=True, meal=False)), ("c2", "75.00", dict(lodg=False, meal=True)),
                      ("c3", "76.00", dict(lodg=False, meal=True))])
case("S6", [{"spec": s, "questions": [q("S6-1", ("amt", "cl", "d2"), "450.00"), q("S6-2", ("yn", "allok", "d2"), "no"),
                                      q("S6-3", ("yn", "rcpt", "c2"), "no"), q("S6-4", ("yn", "rcpt", "c3"), "yes"),
                                      q("S6-5", ("yn", "rcpt", "c1"), "yes"), q("S6-6", ("yn", "itemize", "t"), "yes")]}])

# S7: zoned: 23:00 UTC-05 on 1 Mar (04:00 UTC 2 Mar) to 10:00 UTC+00 on 2 Mar: 6 hours -> not eligible
s = trip(Sub(), dep=("2027-03-01", "23:00"), ret=("2027-03-02", "10:00"), zoned=(-300, 0), idl=False)
case("S7", [{"spec": s, "questions": [q("S7-1", ("yn", "elig", "t"), "no"), q("S7-2", ("yn", "ge24", "t"), "no")]}])

# S8: alternate location authorized and advantageous; arrival 00:05 the next day; 2 days 24h+ -> 75 + 75
s = trip(Sub(), dep=("2027-03-01", "09:00"), ret=("2027-03-02", "10:00"), altauth=True, adv=True)
loc(s, "la", lr="150.00", mr="64.00")
loc(s, "lb", lr="120.00", mr="80.00", tdy=False, alt=True)
day(s, "d1", "2027-03-01")
day(s, "d2", "2027-03-02")
night(s, "n1", "2027-03-01", sor="130.00", arrive=("2027-03-02", "00:05"))
case("S8", [{"spec": s, "questions": [q("S8-1", ("loc", "n1", {"la": "Alpha", "lb": "Beta"}), "Beta"),
                                      q("S8-2", ("yn", "claimprev", "n1"), "yes"),
                                      q("S8-3", ("amt", "pdt", "t"), "240.00")]}])   # 120 + 60 + 60
