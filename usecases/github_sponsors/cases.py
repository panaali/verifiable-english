"""The encoder's cases for the GitHub Sponsors (Sponsored Developer) translation, from questions-enc.jsonl ONLY (sha256
checked at import). CROSS-FAMILY questions (Codex writer), Opus encoder.

Encoder: dri-statute-corpus-github-sponsors-developer-cw-1125 (Opus 5.5), a session that neither wrote the questions nor
the translation (frozen at 5336e71bbc before the questions existed, ISOLATION.md D15). Each in-scope case is transcribed
by hand into encode.Sub items (p, months, payments, deductions, acts, duty items, GitHub acts) with their plain facts
(closed world, E2), the stated judgments the case states, the stated days and amounts. The question's form is read from
its text:
  "How much matching money ... on <payment>" -> ("amt", "mt", y); "What amount of <month>'s payments counts in ...
  Sponsored Developer Payments" -> ("amt", "sdp", m); "Is <sponsor>'s sponsorship matched" -> ("yn", "mok", y);
  "On which day does ... matching period end" -> ("date", "mpe", "p"); "May <developer> take part" -> ("yn", "part");
  "... take part to receive Sponsor funds" -> ("yn", "gr"); "May <developer> raise funds for <purpose>" ->
  ("nyn", "forb", a); "Will / Must GitHub <act>" -> ("yn", "ghwill", g); "Does <amount> count in ... Sponsored Developer
  Payments" -> ("yn", "inc", y); "... in gross Subscription payments" -> ("yn", "subs", y); "first payout ... day" ->
  ("date", "fpd", "p"); "paid out for <month>" (a day) -> ("date", "pdy", m); "Is <developer>'s balance paid out in
  <month M+1>" -> ("yn", "paid", m) for month M; "How much is paid out on D" -> ("payout", m, D) for the month m whose
  payout D is (run.py answer layer); "latest day of the 30-day window" -> ("date", "wl", m); "latest day of the
  approximately-90-day window" -> ("date", "tr", "p").
"judgement" (Sub(judgement=...)): what the encoder decided beyond copying a stated fact (listed as encoder judgement; such
a question leaves the "without anything computed outside Lean" denominator).
REFUSED (form "refuse"): questions the encoder could not transcribe into the translation's vocabulary (OPEN, listed,
not correct). PROBES: out-of-scope cases (every answer UNSUPPORTED, D12). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from encode import Sub

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "b690d65b9c5b507051a1326d1898f520eb3b9eeeef7d3ef48e6b0981ec5f464c"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

CASES = []
PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}

J_GH = ("ghacct entered: a developer GitHub accepted into the Program is read as having a GitHub account (the case does "
        "not say so; matching eligibility needs it, unit 18)")
J_TAKEPART = ("'take part in the Program' read as unit 6 participation (part), not unit 7's giving and receiving of "
              "Sponsor funds")
J_FD = ("fd = 2026-10-23: the case states the first payout on 22 December 2026 but no initiation day; the day 60 days "
        "before it is entered (encoder arithmetic; any earlier day gives the same answers here: every month asked has "
        "its scheduled payout day after the first payout)")
J_PAYMONTH = ("'balance paid out in <month>' read as the payout for the month before it (units 38/39: a month's balance "
              "is paid out in the next month)")
J_PAYOUT = ("'how much is paid out on D' read as the payout of the month whose scheduled day D is (the bridge's 22nd / "
            "third Thursday of the next month, or the stated moved day); its amount asked as that month's balance "
            "(bal, Lean): the case has no matching money, so the balance is what is paid out (run.py 'payout' form)")
J_FIRSTAMT = ("the first payout's amount asked as the first month's Sponsored Developer Payment (the case's only "
              "payment; no other payment or deduction before the first payout)")
J_BALLEFT = ("'remaining / unpaid payments paid after termination' asked as the balance of the month she leaves in (bal, "
             "Lean; no matching money in the case, so the balance is the unpaid payments)")


def case(cid, subs):
    CASES.append({"id": cid, "subs": subs})


def sub(spec, *qs):
    return {"spec": spec, "questions": [{"qid": q, "form": f} for q, f in qs]}


def refuse(why, *qids):
    return sub(Sub(), *[(q, ("refuse", why)) for q in qids])


def nomf(spec):
    """The 'payout' form is used only where no payment of the sub-case is matching money (run.py)."""
    assert not any("kmf" in spec.true[x] for x, kd in spec.items if kd == "pay")
    return spec


STD = ("acc", "regd", "ind", "ghacct", "agreed", "us", "devc")


def matcher(ad, *extra, judgement=(J_GH,), **stated):
    """An individual accepted on ad, approved for matching on the stated judgments the case states."""
    st = dict(oss=True, mission=True, appr=True, rescind=False)
    st.update(stated)
    return Sub(judgement=list(judgement)).dev("acc", "ind", "ghacct", *extra, **st).val("ad", "p", ad)


# --- ages and taking part (units 6, 7) ---------------------------------------------------------------------------------
case("S001", [sub(Sub(judgement=[J_TAKEPART]).dev(*STD, ver=True).born("2014-02-02", "2027-02-01").gh("g1", "greimb"),
                  ("S001-1", ("yn", "part", "p")), ("S001-2", ("yn", "ghwill", "g1")))])
case("S002", [sub(Sub(judgement=[J_TAKEPART]).dev(*STD, ver=False).born("2014-02-01", "2027-02-01"),
                  ("S002-1", ("yn", "part", "p"))),
              sub(Sub(judgement=[J_TAKEPART]).dev(*STD, ver=True).born("2014-02-01", "2027-02-02"),
                  ("S002-2", ("yn", "part", "p")))])
case("S003", [sub(Sub().dev(*STD, ver=False).born("2010-02-01", "2027-02-01"), ("S003-1", ("yn", "gr", "p"))),
              sub(Sub().dev(*STD, ver=True).born("2010-02-01", "2027-02-02"), ("S003-2", ("yn", "gr", "p")))])
case("S004", [sub(Sub(judgement=[J_TAKEPART]).dev(*STD, ver=False).born("2009-02-01", "2027-02-01"),
                  ("S004-1", ("yn", "part", "p"))),
              sub(Sub(judgement=[J_TAKEPART]).dev(*[f for f in STD if f != "ghacct"], ver=False)
                  .born("2009-02-01", "2027-02-03"),
                  ("S004-2", ("yn", "part", "p")))])

# --- prohibited purposes (units 8-15, 31) --------------------------------------------------------------------------------
case("S005", [sub(Sub().dev("acc", "ind").act("a1", "fraud").act("a2", "illegal").act("a3", "reasons", misrep=True),
                  ("S005-1", ("nyn", "forb", "a1")), ("S005-2", ("nyn", "forb", "a2")),
                  ("S005-3", ("nyn", "forb", "a3")))])
case("S006", [sub(Sub().dev("acc", "org").act("a1", "crypto").act("a2", "secur").act("a3", "sellpi"),
                  ("S006-1", ("nyn", "forb", "a1")), ("S006-2", ("nyn", "forb", "a2")),
                  ("S006-3", ("nyn", "forb", "a3")))])
case("S007", [sub(Sub().dev("acc", "ind").act("a1", "pilaw").act("a2", "gamble").act("a3", "gamble").act("a4", "gamble"),
                  ("S007-1", ("nyn", "forb", "a1")), ("S007-2", ("nyn", "forb", "a2")),
                  ("S007-3", ("nyn", "forb", "a3")), ("S007-4", ("nyn", "forb", "a4")))])
case("S008", [sub(Sub().dev("acc", "ind").act("a1", "sanct").act("a2", "adagr", "adproh"),
                  ("S008-1", ("nyn", "forb", "a1")), ("S008-2", ("nyn", "forb", "a2")))])

# --- matching: the period and the $5,000 total (units 16-22) ----------------------------------------------------------
case("S009", [sub(matcher("2027-01-29", "applied").val("ap", "p", "2019-12-31")
                  .month("m1", "2027-01-01", "chs").pay("y1", "m1", "2027-01-29", "20.00", "ksp")
                  .month("m2", "2028-01-01").pay("y2", "m2", "2028-01-28", "30.00", "ksp")
                  .pay("y3", "m2", "2028-01-29", "40.00", "ksp"),
                  ("S009-1", ("amt", "mt", "y1")), ("S009-2", ("amt", "mt", "y2")), ("S009-3", ("amt", "mt", "y3")),
                  ("S009-4", ("date", "mpe", "p")))])
case("S010", [sub(matcher("2027-04-30").month("m1", "2027-05-01", "chs").pay("y1", "m1", "2027-05-01", "4990.00", "ksp")
                  .month("m2", "2028-04-01").pay("y2", "m2", "2028-04-29", "10.00", "ksp")
                  .pay("y3", "m2", "2028-04-30", "1.00", "ksp"),
                  ("S010-1", ("amt", "mt", "y1")), ("S010-2", ("amt", "mt", "y2")), ("S010-3", ("amt", "mt", "y3")))])
case("S011", [sub(matcher("2027-05-31").month("m1", "2027-06-01", "chs").pay("y1", "m1", "2027-06-01", "4900.00", "ksp")
                  .pay("y2", "m1", "2027-06-02", "200.00", "ksp").pay("y3", "m1", "2027-06-03", "50.00", "ksp"),
                  ("S011-1", ("amt", "mt", "y2")), ("S011-2", ("amt", "mt", "y3")), ("S011-3", ("date", "mpe", "p")))])
case("S012", [sub(matcher("2028-02-29").month("m1", "2029-02-01", "chs").pay("y1", "m1", "2029-02-28", "12.00", "ksp")
                  .month("m2", "2029-03-01").pay("y2", "m2", "2029-03-01", "13.00", "ksp"),
                  ("S012-1", ("date", "mpe", "p")), ("S012-2", ("amt", "mt", "y1")), ("S012-3", ("amt", "mt", "y2")))])
case("S013", [sub(matcher("2027-12-31").month("m1", "2027-12-01", "chs").pay("y1", "m1", "2027-12-31", "11.00", "ksp")
                  .month("m2", "2028-12-01").pay("y2", "m2", "2028-12-30", "22.00", "ksp")
                  .pay("y3", "m2", "2028-12-31", "33.00", "ksp"),
                  ("S013-1", ("amt", "mt", "y1")), ("S013-2", ("amt", "mt", "y2")), ("S013-3", ("amt", "mt", "y3")))])
case("S014", [sub(matcher("2027-03-10").month("m1", "2027-03-01", "chs").pay("y1", "m1", "2027-03-11", "40.00", "ksp")
                  .pay("y2", "m1", "2027-03-12", "50.00", "ksp", "forg").pay("y3", "m1", "2027-03-13", "60.00", "ksp", "fprof")
                  .pay("y4", "m1", "2027-03-14", "70.00", "ksp", "forg", "fprof"),
                  ("S014-1", ("yn", "mok", "y1")), ("S014-2", ("yn", "mok", "y2")), ("S014-3", ("yn", "mok", "y3")),
                  ("S014-4", ("yn", "mok", "y4")))])
case("S015", [sub(Sub().dev("acc", "regd", "org", "devc", "rcv", appr=False).val("ad", "p", "2027-03-10")
                  .month("m1", "2027-03-01", "chs").pay("y1", "m1", "2027-03-11", "75.00", "ksp"),
                  ("S015-1", ("yn", "mok", "y1")), ("S015-2", ("amt", "sdp", "m1")))])
case("S016", [sub(matcher("2027-06-01", "applied", judgement=(
    J_GH, "p is Luca's first account (matching approved for it only); Ned's payment to the second account entered as "
          "a payment to an account other than the one matching is approved for (oacct)"))
                  .val("ap", "p", "2020-01-02").month("m1", "2027-06-01", "chs")
                  .pay("y1", "m1", "2027-06-03", "25.00", "ksp").pay("y2", "m1", "2027-06-03", "35.00", "ksp", "oacct"),
                  ("S016-1", ("yn", "mok", "y1")), ("S016-2", ("yn", "mok", "y2")))])
case("S017", [
    sub(matcher("2027-02-01", "applied", mission=False, appr=False,
                judgement=(J_GH, "the state on 2 February 2027: GitHub's adverse mission finding and declined matching "
                                 "stand; the approval of 3 February is only for later payments"))
        .val("ap", "p", "2019-12-31").month("m1", "2027-02-01", "chs").pay("y1", "m1", "2027-02-02", "20.00", "ksp"),
        ("S017-1", ("yn", "mok", "y1"))),
    sub(matcher("2027-02-01", rescind=True,
                judgement=(J_GH, "the rescission of this one payment's matching (5 February) entered as rescind on a "
                                 "sub-case holding only this payment"))
        .month("m1", "2027-02-01", "chs").pay("y1", "m1", "2027-02-04", "30.00", "ksp"),
        ("S017-2", ("amt", "mt", "y1"))),
    sub(matcher("2027-02-01", rescind=True,
                judgement=(J_GH, "the revocation (9 February) of this payment's matching funds before they were paid "
                                 "entered as GitHub withholding or rescinding Matching Fund money (rescind), on a sub-case "
                                 "holding only this payment"))
        .month("m1", "2027-02-01", "chs").pay("y1", "m1", "2027-02-06", "40.00", "ksp"),
        ("S017-3", ("amt", "mt", "y1")))])
case("S018", [sub(matcher("2027-01-01", "sc", "us", judgement=(
    J_GH, "E5: fd = 1 March 2027, the first stated sponsorship payment (no initiation day and no earlier payment stated)",
    "the stated 'Sponsored Developer Payment date 22 April 2027' is a derived day: not entered",
    "S018-1: Sam makes no April payment (his subscription stopped on 5 March): asked as April's matching (mm of a "
    "month with no payment)"))
                  .val("fd", "p", "2027-03-01").month("m1", "2027-03-01", "chs")
                  .pay("y1", "m1", "2027-03-01", "15.00", "ksub")
                  .pay("y2", "m1", "2027-03-02", "40.00", "ksp", cbd="2027-04-21")
                  .pay("y3", "m1", "2027-03-03", "50.00", "ksp", cbd="2027-04-23")
                  .month("m2", "2027-04-01"),
                  ("S018-1", ("amt", "mm", "m2")), ("S018-2", ("yn", "mok", "y2")), ("S018-3", ("yn", "mok", "y3")))])
case("S019", [
    sub(matcher("2027-09-30", "rejn", gapc=True, expd=False,
                judgement=(J_GH, "the state on 1 January 2028: the first leaving (1 December 2027) and rejoining "
                                 "(31 December 2027), gap counted"))
        .val("rj", "p", "2027-12-31").month("m1", "2028-01-01", "chs").pay("y1", "m1", "2028-01-01", "25.00", "ksp"),
        ("S019-1", ("date", "mpe", "p")), ("S019-2", ("yn", "mok", "y1"))),
    sub(matcher("2027-09-30", "rejn", expd=True,
                judgement=(J_GH, "the second rejoining (11 March 2028, period expired) entered alone; the first gap's "
                                 "counting is not entered in this sub-case"))
        .val("rj", "p", "2028-03-11").month("m1", "2028-03-01", "chs").pay("y1", "m1", "2028-03-12", "35.00", "ksp"),
        ("S019-3", ("yn", "mok", "y1")))])

# --- the Sponsored Developer Payment (units 1-5, 28-30, 40) ------------------------------------------------------------
s20 = (Sub(judgement=["the seven March deductions have no stated day: entered on 31 March 2027 (any March day gives the "
                      "same answers: all after the matching period)"])
       .dev("acc", "ind", "devc", "rcv").val("ad", "p", "2026-01-01").month("m1", "2027-03-01", "chs")
       .pay("y1", "m1", "2027-03-02", "300.00", "ksp").pay("y2", "m1", "2027-03-03", "120.00", "ksub")
       .pay("y3", "m1", "2027-03-04", "80.00", "ksub").pay("y4", "m1", "2027-03-05", "70.00", "kpool", "forg", "fprof")
       .pay("y5", "m1", "2027-03-06", "60.00", "kdon").pay("y6", "m1", "2027-03-07", "40.00", "kmf"))
for i, a in enumerate(("5.00", "7.00", "9.00", "20.00", "30.00", "11.00", "13.00"), 1):
    s20.ded(f"d{i}", "m1", "2027-03-31", a)
case("S020", [sub(s20, ("S020-1", ("amt", "sdp", "m1")), ("S020-2", ("yn", "subs", "y2")),
                  ("S020-3", ("yn", "inc", "y5")), ("S020-4", ("yn", "inc", "y4")))])
case("S021", [sub(Sub().dev("acc", "ind").val("ad", "p", "2026-01-01").month("m1", "2027-03-01", "chs")
                  .pay("y1", "m1", "2027-03-03", "45.00", "kmon").gh("g1", "greimb").gh("g2", "grefund"),
                  ("S021-1", ("amt", "sdp", "m1")), ("S021-2", ("yn", "ghwill", "g1")), ("S021-3", ("yn", "ghwill", "g2")))])
case("S022", [refuse("withholding pending investigation and permanent withholding (unit 35) are carried only as GitHub's "
                     "permission; the translation has no amount withheld from a payout", "S022-1", "S022-2")])


# --- payouts (units 32, 36-39, 41-43, 45) ------------------------------------------------------------------------------
def payee(*extra, fd="2026-10-23", judgement=(J_FD,)):
    s = Sub(judgement=list(judgement)).dev("acc", "ind", *extra).val("ad", "p", "2026-01-01")
    return s.val("fd", "p", fd) if fd else s


def first(ad, fd, day, amount, mf):
    return (Sub(judgement=[J_FIRSTAMT]).dev("acc", "ind", "sc", "us").val("ad", "p", ad).val("fd", "p", fd)
            .month("m1", mf, "chs").pay("y1", "m1", day, amount, "ksp"))


case("S023", [sub(first("2027-01-30", "2027-01-31", "2027-01-31", "40.00", "2027-01-01"),
                  ("S023-1", ("date", "fpd", "p")), ("S023-2", ("amt", "sdp", "m1")))])
case("S024", [sub(first("2027-12-29", "2027-12-30", "2027-12-30", "55.00", "2027-12-01"),
                  ("S024-1", ("date", "fpd", "p")), ("S024-2", ("amt", "sdp", "m1")))])
case("S025", [sub(first("2027-11-29", "2027-11-30", "2027-11-30", "65.00", "2027-11-01"),
                  ("S025-1", ("date", "fpd", "p")), ("S025-2", ("amt", "sdp", "m1")))])
case("S026", [sub(payee("sc", "us", fd=None, judgement=())
                  .month("m1", "2027-02-01", "chs").pay("y1", "m1", "2027-02-28", "10.00", "ksp")
                  .month("m2", "2027-04-01").pay("y2", "m2", "2027-04-30", "20.00", "ksp")
                  .month("m3", "2027-05-01").pay("y3", "m3", "2027-05-31", "30.00", "ksp")
                  .month("m4", "2028-02-01").pay("y4", "m4", "2028-02-29", "40.00", "ksp"),
                  ("S026-1", ("date", "wl", "m1")), ("S026-2", ("date", "wl", "m4")),
                  ("S026-3", ("date", "wl", "m2")), ("S026-4", ("date", "wl", "m3")))])
case("S027", [sub(nomf(payee("sc", "us", judgement=(J_FD, J_PAYOUT, "July's moved initiation day (25 July 2027) entered "
                                                                     "on June's month, whose payout falls in July"))
                       .month("m1", "2027-05-01", "chs").pay("y1", "m1", "2027-05-31", "1.00", "ksp")
                       .month("m2", "2027-06-01", mvd="2027-07-25").pay("y2", "m2", "2027-06-30", "1.00", "ksp")),
                  ("S027-1", ("date", "pdy", "m1")), ("S027-2", ("payout", "m1", "2027-06-22")),
                  ("S027-3", ("date", "pdy", "m2")), ("S027-4", ("payout", "m2", "2027-07-25")))])
case("S028", [sub(nomf(payee("sc", judgement=(J_FD, J_PAYMONTH, J_PAYOUT))
                       .month("m1", "2027-03-01", "chs", mn="50.00").pay("y1", "m1", "2027-03-31", "49.00", "ksp")
                       .month("m2", "2027-04-01", mn="50.00")
                       .month("m3", "2027-05-01", mn="50.00").pay("y2", "m3", "2027-05-31", "2.00", "ksp")),
                  ("S028-1", ("yn", "paid", "m1")), ("S028-2", ("yn", "paid", "m3")),
                  ("S028-3", ("payout", "m3", "2027-06-22")))])
case("S029", [sub(nomf(payee("ach", "us", judgement=(J_FD, J_PAYMONTH, J_PAYOUT))
                       .month("m1", "2027-03-01", "chs").pay("y1", "m1", "2027-03-31", "99.99", "ksp")
                       .month("m2", "2027-04-01").pay("y2", "m2", "2027-04-30", "0.01", "ksp")),
                  ("S029-1", ("yn", "paid", "m1")), ("S029-2", ("yn", "paid", "m2")),
                  ("S029-3", ("payout", "m2", "2027-05-20")))])
case("S030", [sub(nomf(payee("wire", "us", judgement=(J_FD, J_PAYOUT))
                       .month("m1", "2027-09-01", "chs").pay("y1", "m1", "2027-09-30", "100.01", "ksp")),
                  ("S030-1", ("date", "pdy", "m1")), ("S030-2", ("payout", "m1", "2027-10-21")))])
case("S031", [sub(payee("ach", "us", judgement=(J_FD, J_PAYMONTH))
                  .month("m1", "2027-03-01", "chs").pay("y1", "m1", "2027-03-31", "99.00", "ksp")
                  .pay("y2", "m1", "2027-03-31", "20.00", "kmf")
                  .month("m2", "2027-04-01").pay("y3", "m2", "2027-04-30", "1.01", "ksp"),
                  ("S031-1", ("yn", "paid", "m1")), ("S031-3", ("yn", "inc", "y2"))),
              refuse("the payout of 20 May 2027 carries matching money from an unpaid earlier month: the amount paid out "
                     "is not a value of the translation (the balance leaves matching money out; no carried paid-out "
                     "sum)", "S031-2")])
case("S032", [sub(nomf(payee("ach", "us", "term", judgement=(
    J_FD, J_PAYMONTH, J_PAYOUT, J_BALLEFT, "paid 'by ACH transfer from her Stripe Connect account': the payout method "
                                           "entered as ACH only (units 39, 42)"))
                       .val("rc", "p", "2027-05-01")
                       .month("m1", "2027-01-01", "chs").pay("y1", "m1", "2027-01-31", "30.00", "ksp")
                       .month("m2", "2027-02-01").pay("y2", "m2", "2027-02-28", "40.00", "ksp")
                       .month("m3", "2027-03-01").pay("y3", "m3", "2027-03-31", "30.01", "ksp")
                       .month("m4", "2027-04-01").pay("y4", "m4", "2027-04-30", "20.00", "ksp")
                       .month("m5", "2027-05-01", "left")),
                  ("S032-1", ("yn", "paid", "m2")), ("S032-2", ("date", "pdy", "m3")),
                  ("S032-3", ("payout", "m3", "2027-04-15")), ("S032-4", ("amt", "bal", "m5")),
                  ("S032-5", ("date", "tr", "p")))])
case("S033", [sub(payee("sc", "us", "term", judgement=(J_FD, J_BALLEFT)).val("rc", "p", "2027-06-30")
                  .month("m1", "2027-06-01", "chs", "left").pay("y1", "m1", "2027-06-29", "35.00", "ksp"),
                  ("S033-1", ("date", "tr", "p")), ("S033-2", ("amt", "bal", "m1")))])
case("S034", [sub(nomf(payee("sc", "us", "fail", judgement=(J_FD, J_PAYOUT))
                       .month("m1", "2027-03-01", "chs").pay("y1", "m1", "2027-03-31", "150.00", "ksp")
                       .ded("d1", "m1", "2027-03-31", "7.50").month("m2", "2027-04-01")),
                  ("S034-1", ("amt", "sdp", "m1")), ("S034-2", ("payout", "m1", "2027-04-22"))),
              refuse("forfeiture of payments (unit 45) is carried only as GitHub's permission; the translation has no "
                     "forfeited amount", "S034-3")])

# --- duties and entry (units 26-28) ------------------------------------------------------------------------------------
case("S035", [sub(Sub(judgement=["'may take part on her terms of providing no content' read as: is making content "
                                 "available required of her (unit 26); required -> she may not"])
                  .dev("acc", "regd", "ind", "ghacct", "agreed").duty("u1", "dcontent"),
                  ("S035-1", ("nyn", "req", "u1"))),
              sub(Sub(judgement=["'may she take part through the refused replacement registration' read as entry into "
                                 "the Program on that registration (unit 27): registered, not accepted"])
                  .dev("regd", "ind", "ghacct", "agreed"),
                  ("S035-2", ("yn", "entered", "p"))),
              refuse("unit 28 (optional monetization features and their additional terms) is not written (ledger "
                     "other:norm)", "S035-3")])

# --- probes (D12): out-of-scope cases, answered UNSUPPORTED from the encoder file's scope field ----------------------
for cid, qids, why in (
        ("S036", ("S036-1", "S036-2"), "sponsor service and card fees: Terms for Sponsors (out of scope, D1)"),
        ("S037", ("S037-1", "S037-2"), "sponsor invoices and dashboards: Terms for Sponsors (out of scope, D1)"),
        ("S038", ("S038-1", "S038-2"), "sponsor agreement notice and renewal: Terms for Sponsors (out of scope, D1)"),
        ("S039", ("S039-1", "S039-2"), "s.3.2.2 Taxes and foreign tax law (out of scope, D1, D2(c))"),
        ("S040", ("S040-1", "S040-2"), "s.3.8 Stripe Connect agreements (out of scope, D1)"),
        ("S041", ("S041-1",), "limitation of liability (out of scope, D1)"),
        ("S042", ("S042-1", "S042-2"), "s.5 suspension and effect of termination (out of scope, D1, D2(b))"),
        ("S043", ("S043-1", "S043-2"), "General Program Terms: confidentiality, publicity (out of scope, D1)"),
        ("S044", ("S044-1", "S044-2", "S044-3"), "General Program Terms: notice, assignment, governing law (out of scope)"),
        ("S045", ("S045-1", "S045-2"), "General Program Terms: changes to the terms (out of scope, D1)")):
    PROBES[cid] = why
    PROBE_QIDS[cid] = list(qids)
