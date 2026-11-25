"""Made-up smoke cases for the OPM FEGLI premium translation, each answer worked by hand from the readings (not from any
writer's case). EXPECT: qid -> the hand answer ("yes"/"no"/an amount/"OPEN")."""
from encode import Sub

CASES, EXPECT = [], {}
PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}


def case(cid, subs):
    CASES.append({"id": cid, "subs": subs})


def q(qid, form, exp):
    EXPECT[qid] = exp
    return {"qid": qid, "form": form}


def emp(start, age, bw, basic=True):
    s = Sub().fact("emp").fact("ann", val=False).fact("basic", val=basic).period(start, age, bw)
    return s


def ann(start, age, nrb=False, nrc=False):
    return Sub().fact("ann").fact("emp", val=False).fact("nrb", val=nrb).fact("nrc", val=nrc).period(start, age)


def all4(s, basic, b, mult):
    return s.cov("basic", basic).cov("opta").cov("optb", b).cov("optc", multiples=mult)


def abasic(start, bd, col, amount="100000.00", s75=None, canc=False):
    s = Sub().fact("ann").fact("emp", val=False).fact("basic").period(start).val("bd", "p", bd)
    for r in ("r75", "r50", "rno"):
        s.fact(r, val=(r == col))
    s.fact("s75", val=s75 is not None).fact("canc", val=canc)
    if s75 is not None:
        s.val("sd", "p", s75)
    return s.cov("basic", amount)


# S01 employee 47, biweekly: 0.16 x 60 = 9.60; A 0.60; B 0.06 x 20 = 1.20; C 2 x 0.53 = 1.06 -> 12.46
case("S01", [{"spec": all4(emp("2025-06-02", 47, True), "60000.00", "20000.00", 2),
              "questions": [q("S01-1", ("amt", "tot", "t"), "12.46"), q("S01-2", ("amt", "pr", "b"), "9.60")]}])
# S02 employee 47, monthly: 0.3467 x 200 = 69.34; A 1.30; B 0.130 x 20 = 2.60; C 2 x 1.15 = 2.30 -> 75.54; 0.3467 x 60 inexact
case("S02", [{"spec": all4(emp("2025-06-01", 47, False), "200000.00", "20000.00", 2),
              "questions": [q("S02-1", ("amt", "tot", "t"), "75.54")]},
             {"spec": emp("2025-06-01", 47, False).cov("basic", "60000.00"),
              "questions": [q("S02-2", ("amt", "pr", "b"), "OPEN")]}])
# S03 annuitant 67, No Reduction B only: A free; B 1.040 x 40 = 41.60; C free -> 41.60
s3 = ann("2025-03-01", 67, nrb=True, nrc=False).cov("opta").cov("optb", "40000.00").cov("optc", multiples=3)
case("S03", [{"spec": s3, "questions": [q("S03-1", ("amt", "tot", "t"), "41.60"), q("S03-2", ("yn", "free", "oa"), "yes"),
                                        q("S03-3", ("yn", "free", "oc"), "yes"), q("S03-4", ("yn", "free", "ob"), "no")]}])
# S04 annuitant 62: A 13.00; B 0.867 x 10 = 8.67; C 2 x 5.27 = 10.54 -> 32.21
s4 = ann("2025-03-01", 62).cov("opta").cov("optb", "10000.00").cov("optc", multiples=2)
case("S04", [{"spec": s4, "questions": [q("S04-1", ("amt", "tot", "t"), "32.21")]}])
# S05 annuitant Basic 50%, 65th birthday 2025-05-15: May 1.0967 x 100 = 109.67; June 0.75 x 100 = 75.00; life yes
case("S05", [{"spec": abasic("2025-05-01", "2025-05-15", "r50"), "questions": [q("S05-1", ("amt", "pr", "b"), "109.67"),
                                                                              q("S05-3", ("yn", "life", "p"), "yes")]},
             {"spec": abasic("2025-06-01", "2025-05-15", "r50"), "questions": [q("S05-2", ("amt", "pr", "b"), "75.00")]}])
# S06 75%, birthday 2025-05-31: May 34.67, June 0.00
case("S06", [{"spec": abasic("2025-05-01", "2025-05-31", "r75"), "questions": [q("S06-1", ("amt", "pr", "b"), "34.67")]},
             {"spec": abasic("2025-06-01", "2025-05-31", "r75"), "questions": [q("S06-2", ("amt", "pr", "b"), "0.00")]}])
# S07 No Reduction, later 75% from 2025-08-01, birthday 2024-01-10: July 225.00; August 0.00; life no
case("S07", [{"spec": abasic("2025-07-01", "2024-01-10", "rno", s75="2025-08-01"),
              "questions": [q("S07-1", ("amt", "pr", "b"), "225.00"), q("S07-3", ("yn", "life", "p"), "no")]},
             {"spec": abasic("2025-08-01", "2024-01-10", "rno", s75="2025-08-01"),
              "questions": [q("S07-2", ("amt", "pr", "b"), "0.00")]}])
# S08 employee rates from the first pay period starting on or after 2021-10-01
case("S08", [{"spec": emp("2021-09-27", 40, True).cov("opta"), "questions": [q("S08-1", ("yn", "rap", "t"), "no"),
                                                                             q("S08-3", ("amt", "pr", "oa"), "OPEN")]},
             {"spec": emp("2021-10-04", 40, True).cov("opta"), "questions": [q("S08-2", ("yn", "rap", "t"), "yes"),
                                                                             q("S08-4", ("amt", "pr", "oa"), "0.30")]}])
# S09 Extra Benefit: 44 yes, 45 no, 30 yes, no extra cost
case("S09", [{"spec": emp("2025-06-01", 44, False), "questions": [q("S09-1", ("yn", "xb", "t"), "yes"),
                                                                 q("S09-4", ("yn", "xbcost", "p"), "no")]},
             {"spec": emp("2025-06-01", 45, False), "questions": [q("S09-2", ("yn", "xb", "t"), "no")]},
             {"spec": emp("2025-06-01", 30, False), "questions": [q("S09-3", ("yn", "xb", "t"), "yes")]}])
# S10 descriptions (R12)
case("S10", [{"spec": emp("2025-06-01", 50, False), "questions": [
    q("S10-1", ("yn", "agechg", "p"), "no"), q("S10-2", ("yn", "avgc", "p"), "yes"), q("S10-3", ("yn", "hlth", "p"), "no"),
    q("S10-4", ("yn", "post65", "p"), "yes")]}])
# S11 employee 82 monthly: A 13.00; B 6.240 x 10 = 62.40; C 16.90 -> 92.30
s11 = emp("2025-06-01", 82, False).cov("opta").cov("optb", "10000.00").cov("optc", multiples=1)
case("S11", [{"spec": s11, "questions": [q("S11-1", ("amt", "tot", "t"), "92.30")]}])
# S12 annuitant month before the rates: no rule
case("S12", [{"spec": ann("2021-09-01", 34).cov("opta"), "questions": [q("S12-1", ("yn", "rap", "t"), "no"),
                                                                      q("S12-2", ("amt", "pr", "oa"), "OPEN")]}])
# S13 cancelled 50%: not for life
case("S13", [{"spec": abasic("2025-06-01", "2024-01-10", "r50", canc=True), "questions": [q("S13-1", ("yn", "life", "p"), "no")]}])
