"""Made-up smoke cases for the GitHub Sponsors (Sponsored Developer) translation, each answer worked by hand from the
readings R1-R13 (not from any writer's case: none exists yet). EXPECT: qid -> the hand answer ("yes"/"no"/an amount/a
day/"OPEN")."""
from encode import Sub

CASES, EXPECT = [], {}
PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}


def case(cid, subs):
    CASES.append({"id": cid, "subs": subs})


def q(qid, form, exp):
    EXPECT[qid] = exp
    return {"qid": qid, "form": form}


def sub(spec, *qs):
    return {"spec": spec, "questions": list(qs)}


def matcher(ad, *extra, **stated):
    """An individual accepted on ad, eligible for matching on every stated judgment, paid through Stripe Connect."""
    st = dict(oss=True, mission=True, appr=True, rescind=False)
    st.update(stated)
    s = Sub().dev("acc", "regd", "ind", "ghacct", "agreed", "us", *extra, **st).val("ad", "p", ad)
    return s


def org(*extra):
    return Sub().dev("acc", "regd", "org", "ghacct", "agreed", "us", *extra).val("ad", "p", "2026-01-05")


# A: matching and the $5,000 total; organization and profile sponsorships; the net; the payout day (R1, R4, R5, R7)
a = (matcher("2027-03-10", "sc").val("fd", "p", "2027-03-15").month("m1", "2027-04-01")
     .pay("y1", "m1", "2027-04-05", "3000.00", "ksp").pay("y2", "m1", "2027-04-10", "500.00", "ksp", "forg")
     .pay("y3", "m1", "2027-04-12", "200.00", "ksp", "fprof").pay("y4", "m1", "2027-04-20", "2500.00", "ksub")
     .pay("y5", "m1", "2027-04-25", "100.00", "ksp"))
case("A", [sub(a, q("A-1", ("amt", "mt", "y1"), "3000.00"), q("A-2", ("amt", "mt", "y2"), "0.00"),
               q("A-3", ("amt", "mt", "y3"), "0.00"), q("A-4", ("amt", "mt", "y4"), "2000.00"),
               q("A-5", ("amt", "mt", "y5"), "0.00"), q("A-6", ("amt", "mm", "m1"), "5000.00"),
               q("A-7", ("amt", "sdp", "m1"), "6300.00"), q("A-8", ("date", "pdy", "m1"), "2027-05-22"),
               q("A-9", ("date", "wl", "m1"), "2027-05-30"), q("A-10", ("date", "fp", "p"), "2027-05-14"),
               q("A-11", ("date", "fpd", "p"), "OPEN"), q("A-12", ("yn", "mok", "y2"), "no"),
               q("A-13", ("yn", "mok", "y1"), "yes"), q("A-14", ("date", "mpe", "p"), "2028-03-09"),
               q("A-15", ("amt", "tm", "p"), "5000.00"), q("A-16", ("yn", "sponsor", "y4"), "yes"),
               q("A-17", ("yn", "subs", "y1"), "no"))])

# B: ACH threshold with accrual; exactly $100.00 after an accrual is OPEN (R6, D6(b))
b = (org("ach").val("fd", "p", "2026-01-10").month("m1", "2027-06-01", "chs")
     .pay("y1", "m1", "2027-06-03", "60.00", "ksp").pay("y2", "m1", "2027-06-10", "39.99", "ksub")
     .month("m2", "2027-07-01").pay("y3", "m2", "2027-07-08", "0.01", "ksp"))
case("B", [sub(b, q("B-1", ("yn", "paid", "m1"), "no"), q("B-2", ("amt", "bal", "m1"), "99.99"),
               q("B-3", ("yn", "paid", "m2"), "OPEN"), q("B-4", ("amt", "bal", "m2"), "100.00"))])

# C: wire: exactly $100 with no accrual is paid; matching money left out of the threshold; leaving pays a small balance
c = (org("wire").val("fd", "p", "2026-01-10").month("m1", "2027-09-01", "chs")
     .pay("y1", "m1", "2027-09-15", "100.00", "ksp")
     .month("m2", "2027-10-01").pay("y2", "m2", "2027-10-04", "40.00", "ksp").pay("y3", "m2", "2027-10-06", "70.00", "kmf")
     .month("m3", "2027-11-01", "left").pay("y4", "m3", "2027-11-02", "10.00", "ksp"))
case("C", [sub(c, q("C-1", ("yn", "paid", "m1"), "yes"), q("C-2", ("date", "pdy", "m1"), "2027-10-21"),
               q("C-3", ("amt", "sdp", "m2"), "110.00"), q("C-4", ("amt", "bal", "m2"), "40.00"),
               q("C-5", ("yn", "paid", "m2"), "no"), q("C-6", ("yn", "paid", "m3"), "yes"),
               q("C-7", ("date", "pdy", "m3"), "2027-12-16"))])

# D: deductions outside the first 12 months are subtracted; a donation is not included (R1); D2: a refund inside them OPEN
d1 = (matcher("2025-01-10", "sc").month("m1", "2027-02-01").pay("y1", "m1", "2027-02-03", "300.00", "ksp")
      .pay("y2", "m1", "2027-02-05", "50.00", "kdon").pay("y3", "m1", "2027-02-07", "20.00", "kmon")
      .ded("d1", "m1", "2027-02-10", "15.00").ded("d2", "m1", "2027-02-11", "5.00", "gfee"))
d2 = (matcher("2027-01-20", "sc").month("m1", "2027-02-01").pay("y1", "m1", "2027-02-03", "300.00", "ksp")
      .pay("y2", "m1", "2027-02-05", "50.00", "kdon").ded("d1", "m1", "2027-02-10", "15.00"))
case("D", [sub(d1, q("D-1", ("amt", "sdp", "m1"), "300.00"), q("D-2", ("yn", "inc", "y2"), "no"),
               q("D-3", ("amt", "mt", "y1"), "0.00"), q("D-4", ("yn", "inmp", "y1"), "no")),
           sub(d2, q("D-5", ("amt", "sdp", "m1"), "OPEN"), q("D-6", ("amt", "mt", "y1"), "300.00"),
               q("D-7", ("amt", "mt", "y2"), "OPEN"))])

# E: a chargeback before the month's payout day is not matched; one after it is (R4)
e = (matcher("2027-01-05", "sc").val("fd", "p", "2027-01-06").month("m1", "2027-04-01")
     .pay("y1", "m1", "2027-04-02", "100.00", "ksp", cbd="2027-05-01")
     .pay("y2", "m1", "2027-04-03", "100.00", "ksp", cbd="2027-05-25"))
case("E", [sub(e, q("E-1", ("yn", "mok", "y1"), "no"), q("E-2", ("amt", "mt", "y2"), "100.00"),
               q("E-3", ("yn", "cbb", "y1"), "yes"))])

# F: first payments: the 60th day is a 22nd (one day); F2: it is not (OPEN) (R7, D6(a))
f1 = (org("sc").val("fd", "p", "2027-01-21").month("m1", "2027-01-01").pay("y1", "m1", "2027-01-21", "10.00", "ksp")
      .month("m2", "2027-02-01").pay("y2", "m2", "2027-02-10", "10.00", "ksp")
      .month("m3", "2027-03-01").pay("y3", "m3", "2027-03-10", "10.00", "ksp"))
f2 = (org("sc").val("fd", "p", "2027-01-22").month("m1", "2027-01-01").pay("y1", "m1", "2027-01-22", "10.00", "ksp"))
case("F", [sub(f1, q("F-1", ("date", "fpd", "p"), "2027-03-22"), q("F-2", ("date", "pdy", "m1"), "2027-03-22"),
               q("F-3", ("date", "pdy", "m3"), "2027-04-22"), q("F-4", ("date", "fp", "p"), "2027-03-22"),
               q("F-5", ("date", "pdy", "m2"), "2027-03-22")),
           sub(f2, q("F-6", ("date", "fpd", "p"), "OPEN"), q("F-7", ("date", "pdy", "m1"), "OPEN"))])

# G: a moved initiation day inside the 30 days; one outside them is OPEN; 90 days after the recognition month (R7, R8)
g = (org("sc", "term").val("fd", "p", "2026-01-01").val("rc", "p", "2027-06-30")
     .month("m1", "2027-05-01", mvd="2027-06-21").pay("y1", "m1", "2027-05-03", "10.00", "ksp")
     .month("m2", "2027-06-01", mvd="2027-08-02").pay("y2", "m2", "2027-06-03", "10.00", "ksp"))
case("G", [sub(g, q("G-1", ("date", "pdy", "m1"), "2027-06-21"), q("G-2", ("date", "pdy", "m2"), "OPEN"),
               q("G-3", ("date", "tr", "p"), "2027-09-28"), q("G-4", ("date", "wl", "m1"), "2027-06-30"))])

# H: ages (R9, D6(c))
def kid(age=None, ver=None, us=True, mna=None, born=None):
    st = {} if ver is None else {"ver": ver}
    s = Sub().dev("ghacct", "agreed", *(("us",) if us else ()), **st)
    if age is not None:
        s.val("ag", "p", age)
    if mna is not None:
        s.val("mna", "p", mna)
    if born is not None:
        s.born(*born)
    return s


case("H", [sub(kid(born=("2014-05-10", "2027-05-09")), q("H-1", ("yn", "part", "p"), "no"), q("H-2", ("yn", "gr", "p"), "no")),
           sub(kid(13), q("H-3", ("yn", "part", "p"), "yes"), q("H-4", ("yn", "gr", "p"), "OPEN")),
           sub(kid(13, True), q("H-5", ("yn", "gr", "p"), "yes")),
           sub(kid(17, False), q("H-6", ("yn", "gr", "p"), "no")),
           sub(kid(17, True), q("H-7", ("yn", "gr", "p"), "yes")),
           sub(kid(18), q("H-8", ("yn", "gr", "p"), "yes")),
           sub(kid(15, us=False, mna=16), q("H-9", ("yn", "part", "p"), "no"))])

# I: prohibited purposes and advertising (R10)
i = (Sub().act("a1", "crypto").act("a2").act("a3", "reasons", misrep=True).act("a4", "reasons")
     .act("a5", "adagr", "adproh").act("a6", "adprim").act("a7", "sanct").act("a8", "adagr"))
case("I", [sub(i, q("I-1", ("yn", "forb", "a1"), "yes"), q("I-2", ("yn", "forb", "a2"), "no"),
               q("I-3", ("yn", "forb", "a3"), "yes"), q("I-4", ("yn", "forb", "a4"), "OPEN"),
               q("I-5", ("yn", "forb", "a5"), "yes"), q("I-6", ("yn", "forb", "a6"), "OPEN"),
               q("I-7", ("yn", "forb", "a7"), "yes"), q("I-8", ("yn", "forb", "a8"), "no"))])

# J: duties and GitHub's acts (R11, R12)
j = (Sub().dev("fail", "us", breach=True).duty("u1", "dexp").duty("u2", None).gh("g1", "greimb").gh("g2", "grefund")
     .gh("g3", "gbank").gh("g4", "gwith").gh("g5", "gconv").gh("g6", "gfeemp").gh("g7", "gxmit").gh("g8", "gperm"))
case("J", [sub(j, q("J-1", ("yn", "req", "u1"), "yes"), q("J-2", ("yn", "req", "u2"), "no"),
               q("J-3", ("yn", "ghwill", "g1"), "no"), q("J-4", ("yn", "ghwill", "g2"), "no"),
               q("J-5", ("yn", "ghmay", "g3"), "yes"), q("J-6", ("yn", "ghmay", "g4"), "yes"),
               q("J-7", ("yn", "ghmay", "g5"), "OPEN"), q("J-8", ("yn", "ghwill", "g6"), "no"),
               q("J-9", ("yn", "ghwill", "g7"), "no"), q("J-10", ("yn", "ghmay", "g8"), "OPEN"))])

# K: leaving and rejoining (R2)
def rejoin(**st):
    return (matcher("2027-01-10", "sc", "rejn", **st).val("rj", "p", "2027-06-01").month("m1", "2027-07-01")
            .pay("y1", "m1", "2027-07-05", "100.00", "ksp"))


case("K", [sub(rejoin(expd=True), q("K-1", ("amt", "mt", "y1"), "0.00")),
           sub(rejoin(gapc=True), q("K-2", ("amt", "mt", "y1"), "100.00")),
           sub(rejoin(), q("K-3", ("amt", "mt", "y1"), "OPEN"))])

# L: review before 1 January 2020 (R13)
case("L", [sub(Sub().dev("applied", "ind").val("ap", "p", "2019-12-31"), q("L-1", ("yn", "review", "p"), "yes")),
           sub(Sub().dev("applied", "ind").val("ap", "p", "2020-01-01"), q("L-2", ("yn", "review", "p"), "OPEN"))])

# M: accepted on 29 February: the two-reading day is OPEN (R2)
mm = (matcher("2028-02-29", "sc").month("m1", "2029-02-01").pay("y1", "m1", "2029-02-27", "1.00", "ksp")
      .pay("y2", "m1", "2029-02-28", "1.00", "ksp").month("m2", "2029-03-01").pay("y3", "m2", "2029-03-01", "1.00", "ksp"))
case("M", [sub(mm, q("M-1", ("yn", "inmp", "y1"), "yes"), q("M-2", ("yn", "inmp", "y2"), "OPEN"),
               q("M-3", ("yn", "inmp", "y3"), "no"), q("M-4", ("date", "mpe", "p"), "OPEN"))])

# N: a cross-border minimum above the month's payment: not paid (R6)
n = org("sc").val("fd", "p", "2026-01-10").month("m1", "2027-08-01", mn="25.00").pay("y1", "m1", "2027-08-02", "20.00", "ksp")
case("N", [sub(n, q("N-1", ("yn", "paid", "m1"), "no"))])

# O: Sponsored Developer and entry into the Program (R13)
case("O", [sub(Sub().dev("acc", "regd", "devc", "rcv"), q("O-1", ("yn", "sdev", "p"), "yes"),
               q("O-2", ("yn", "entered", "p"), "yes")),
           sub(Sub().dev("regd"), q("O-3", ("yn", "entered", "p"), "no"))])
