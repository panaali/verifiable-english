"""The encoder's cases, from questions-enc.jsonl ONLY (template: fill CASES, PROBES, PROBE_QIDS; UNSUPPORTED only for an
in-scope question the record format cannot state).
One RECORD per pay reference period asked about (a case with two periods gives two records, "<case>.1", "<case>.2"). Each
record: "items" (the worker w, every payment, deduction, worker payment, benefit and provision of living accommodation the
facts name, and each stated run of accommodation days), "facts" (the unary facts true of each item; every other FACTS
entry is false, encode.py C1, except "unknown"), "links" (run_of), "ints" (stated amounts, days and day counts; the
period's first and last day; the following period's from the calendar, C5), "bridge" (the dates the bridge script reads:
date of birth, commencement, earlier commencement), "questions" (qid -> form: rate = Q1, rem = Q2, paid = Q3),
"judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder judgement"), "calendar" (C5
readings). PROBES: out-of-scope cases (all answered UNSUPPORTED): case id -> one line; PROBE_QIDS: case id -> its qids.
UNSUPPORTED: key -> (why, [qids]).
The helpers below (rec, qs, the period constants) are the build's; rec(...) builds one record.
"""
from __future__ import annotations

NOAPP = []                                   # not a contract of apprenticeship, no arrangements (all false, C1)
PAY = ["emp_payment", "as_prp"]              # a payment by the employer as respects the period asked about


def rec(rid, first, last, nfirst, nlast, dob, w, items, q, *, start=None, prior_start=None, runs=(), unknown=None,
        judgement=(), calendar=(), ints=None):
    """items: {name: (facts, amount or None, day or None)}; runs: (name, acc, days, whole)."""
    facts = {"w": ["worker"] + list(w)}
    vals = {"first": first, "last": last}
    if nfirst:
        vals["nfirst"], vals["nlast"] = nfirst, nlast
    for name, (fs, amt, day) in items.items():
        facts[name] = list(fs)
        if amt is not None:
            vals[f"amt_{name}"] = amt
        if day is not None:
            vals[f"paid_{name}"] = day
    links = []
    for (r, acc, n, whole) in runs:
        facts[r] = ["acc_run"] + (["whole"] if whole else [])
        vals[f"ndays_{r}"] = n
        links.append(("run_of", r, acc))
    vals.update(ints or {})
    qs = [{"qid": qid, "form": form} for qid, form in zip(q, ("rate", "rem", "paid"))]
    return {"id": rid, "items": ["w", *items, *[r[0] for r in runs]], "facts": facts, "links": links, "ints": vals,
            "unknown": unknown or {}, "questions": qs, "judgement": list(judgement), "calendar": list(calendar),
            "bridge": {"case": rid, "first": first, "dob": dob, "start": start, "prior_start": prior_start}}


def qs(case, *ns):
    return [f"{case}-{n}" for n in ns]


JUNE, JULY = ("2026-06-01", "2026-06-30", "2026-07-01", "2026-07-31"), ("2026-07-01", "2026-07-31", "2026-08-01", "2026-08-31")
AUG = ("2026-08-01", "2026-08-31", "2026-09-01", "2026-09-30")
MAY = ("2026-05-01", "2026-05-31", "2026-06-01", "2026-06-30")
CAL_MONTH = "the following pay reference period is the next calendar month (monthly pay by calendar month)"
CAL_WEEK = "the following pay reference period is the next week Monday to Sunday (weekly pay)"

# --- encoder's helpers (data only) ---------------------------------------------------------------------------
D30 = "2026-06-30"
APPR = ["contract_appr"]
NLW = ["nlw"]


def basic(amt, day=D30):
    """Basic pay for work done in the period asked about, paid on day."""
    return (PAY, amt, day)


def june(cid, dob, w, items, *, runs=(), unknown=None, judgement=(), calendar=(), ints=None, start=None,
         prior_start=None, q=(1, 2, 3)):
    return rec(cid, *JUNE, dob, w, items, qs(cid, *q), start=start, prior_start=prior_start, runs=runs,
               unknown=unknown, judgement=judgement, calendar=[CAL_MONTH, *calendar], ints=ints)


ACC_RUN30 = [("run1", "acc", 30, True)]

CASES = [
    # ---- rates (Q1) ----
    june("N001", "2008-06-15", [], {"p1": basic("800.00")}),
    june("N002", "2005-06-15", [], {"p1": basic("1084.99")}),
    june("N003", "2005-06-01", NLW, {"p1": basic("1271.01")}),
    june("N004", "2007-06-15", APPR, {"p1": basic("800.00")}, start="2025-05-01"),
    june("N005", "2007-06-01", APPR, {"p1": basic("1085.00")}, start="2025-06-01",
         judgement=["an apprenticeship agreement within ASCLA 2009 s. 32 stated as contract_appr"]),
    june("N006", "1990-01-01", NLW + APPR, {"p1": basic("800.00")}, start="2025-06-15"),
    june("N007", "1990-01-01", NLW + APPR + ["prior_continuity"], {"p1": basic("1271.00")},
         start="2026-05-01", prior_start="2025-05-01",
         judgement=["start = the move to Bob Ltd (1 May 2026); prior_start = the Green Farm commencement (1 May 2025)"]),
    june("N008", "1990-01-01", NLW + ["eng_england", "known_england", "made_eng", "made_wal", "made_sco"],
         {"p1": basic("800.00")}, start="2026-05-01",
         judgement=["SoS arrangements under ETA 1973 s. 2: every made_* fact whose words cover that maker is stated"]),
    june("N009", "1990-01-01", NLW + ["eng_england", "tb_agreement", "tb_standard"], {"p1": basic("800.00")},
         start="2026-05-01",
         judgement=["'engaged under that agreement in England' stated as eng_england"]),
    june("N010", "1990-01-01", NLW + ["eng_scotland", "known_scotland", "made_eng", "made_wal", "made_sco"],
         {"p1": basic("800.00")}, start="2026-05-01",
         judgement=["SoS arrangements under ETA 1973 s. 2: every made_* fact whose words cover that maker is stated"]),
    june("N011", "1990-01-01", NLW + ["eng_ni", "known_ni", "made_ni"], {"p1": basic("800.00")}, start="2026-05-01"),
    june("N012", "1990-01-01", NLW + ["eng_wales", "known_wales", "made_eng", "made_wal", "made_sco"],
         {"p1": basic("800.00")}, start="2026-05-01",
         judgement=["SoS arrangements under ETA 1973 s. 2: every made_* fact whose words cover that maker is stated"]),
    # ---- reg. 9 timing ----
    rec("N013.1", *JUNE, "1990-01-01", NLW,
        {"p1": basic("1200.00"), "p2": basic("71.00", "2026-07-07"), "p3": (["emp_payment"], "1271.00", "2026-07-31")},
        qs("N013", 1, 2, 3), calendar=[CAL_MONTH],
        judgement=["p3 (July work) is as respects a later period: no as_* fact"]),
    rec("N013.2", *JULY, "1990-01-01", NLW,
        {"p1": (["emp_payment", "as_prev"], "1200.00", D30), "p2": (["emp_payment", "as_prev"], "71.00", "2026-07-07"),
         "p3": basic("1271.00", "2026-07-31")},
        qs("N013", 4, 5, 6), calendar=[CAL_MONTH],
        judgement=["p1, p2 (June work) are as respects June, the period immediately before July: as_prev"]),
    june("N014", "1990-01-01", NLW,
         {"p1": basic("1200.00"),
          "p2": (PAY + ["rec_obligation", "rec_condition", "rec_given", "rec_paid_window"], "71.00", "2026-08-10")},
         ints={"recday_p2": "2026-07-27", "fourthwd": "2026-07-27"},
         calendar=["record given 27 July 2026 (July period), p2 paid 10 August 2026 (the period after): rec_paid_window"]),
    june("N015", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "p2": (PAY + ["rec_obligation", "rec_condition", "rec_given", "rec_paid_window"], "50.00", "2026-08-10")},
         ints={"recday_p2": "2026-07-26", "fourthwd": "2026-07-27"},
         calendar=["record given 26 July 2026 (July period), p2 paid 10 August 2026 (the period after): rec_paid_window"]),
    rec("N016", "2026-06-08", "2026-06-14", "2026-06-15", "2026-06-21", "1990-01-01", NLW + ["terminated"],
        {"p1": basic("400.00", "2026-06-14"), "p2": basic("108.40", "2026-07-14"), "p3": basic("100.00", "2026-07-15")},
        qs("N016", 1, 2, 3), ints={"termday": "2026-06-14", "monthend": "2026-07-14"},
        calendar=[CAL_WEEK + " (15-21 June 2026, read from the weekly pattern though the contract terminated 14 June)"]),
    # ---- reg. 10 exclusions ----
    june("N017", "1990-01-01", NLW + ["terminated"],
         {"p1": basic("1000.00"),
          "loan": (PAY + ["x_loan_advance"], "100.00", D30),
          "wadv": (["emp_payment", "x_loan_advance"], "80.00", D30),
          "lossoff": (PAY + ["x_retirement"], "200.00", D30),
          "settlek": (PAY + ["x_court", "due_contract"], "271.00", D30),
          "settlen": (PAY + ["x_court"], "29.00", D30),
          "redund": (PAY + ["x_redundancy"], "150.00", D30),
          "sugg": (PAY + ["x_suggestion"], "40.00", D30)},
         ints={"termday": "2026-06-30"},
         judgement=["the £300.00 settlement is split into its two stated parts (£271.00 contractual, £29.00 not)",
                    "the advance of wages for July work is not as respects June (no as_prp); the other June items are",
                    "monthend not stated: all payments are on the termination day"]),
    june("N018", "1990-01-01", NLW + ["absent"],
         {"p1": basic("1200.00"),
          "absh": (PAY + ["x_hours_not_work"], "90.00", D30),
          "salr": (PAY + ["x_salaried_reduced"], "80.00", D30),
          "bike": (PAY + ["benefit_kind"], "200.00", "2026-06-20"),
          "vouch": (PAY + ["x_voucher"], "50.00", "2026-06-20")},
         judgement=["the bicycle and the voucher are items provided by the employer (emp_payment, value as amt), as "
                    "reg. 10(f), (g) list them among payments"]),
    june("N019", "1990-01-01", NLW,
         {"ord": basic("1080.00"),
          "night": (PAY + ["part_excluded"], "180.00", D30),
          "prod": (PAY + ["performance"], "20.00", D30),
          "resp": (PAY + ["consolidated"], "51.00", D30),
          "inconv": (PAY + ["arrangement_pay"], "25.00", D30)},
         judgement=["night pay: the excess over the £12.00 lowest rate is not stated as its own amount (hours x "
                    "rates): part_excluded"]),
    june("N020", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "tools": (PAY + ["expenditure"], "40.00", D30),
          "tips": (PAY + ["x_tips"], "30.00", D30),
          "travel": (PAY + ["x_travel338", "expenditure"], "20.00", D30),
          "prem": (PAY + ["x_salary_premium"], "50.00", D30),
          "wptool": (["wpay_other", "expenditure", "met_by_emp"], "40.00", "2026-06-12"),
          "wprail": (["wpay_other", "expenditure", "met_by_emp"], "20.00", "2026-06-15")},
         judgement=["the s. 338 travel payment also meets Ann's employment travel expenditure: expenditure"]),
    # ---- regs. 12-13 reductions ----
    june("N021", "1990-01-01", NLW,
         {"p1": basic("20.00"), "charge": (["wpay_emp", "own_use"], "25.00", D30)},
         judgement=["the unpaid charge due 30 June is a payment due from the worker (wpay_emp), day = due day"]),
    june("N022", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "dconduct": (["deduction", "own_use", "conduct_liable"], "30.00", D30),
          "dloan": (["deduction", "own_use", "loan_repay"], "40.00", D30),
          "dwadv": (["deduction", "own_use", "loan_repay"], "20.00", D30),
          "dover": (["deduction", "own_use", "overpayment"], "25.00", D30),
          "dshares": (["deduction", "own_use", "shares"], "15.00", D30)}),
    june("N023", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "wpbook": (["wpay_emp", "own_use", "purchase_emp"], "10.00", "2026-06-20"),
          "wpgloves": (["wpay_emp", "own_use", "purchase_emp", "purchase_required", "expenditure"], "20.00",
                       "2026-06-20"),
          "wpapron": (["wpay_emp", "own_use", "purchase_emp", "purchase_required", "expenditure", "met_by_emp"],
                      "30.00", "2026-06-20"),
          "papron": (PAY + ["expenditure"], "30.00", D30)},
         judgement=["gloves and apron bought from Bob Ltd as required for the employment: purchase_emp and expenditure"]),
    june("N024", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "dlaundry": (["deduction", "expenditure", "met_by_emp"], "30.00", D30),
          "wptools": (["wpay_emp", "own_use", "expenditure", "purchase_emp", "purchase_required", "met_by_emp"],
                      "40.00", "2026-06-20"),
          "wptrain": (["wpay_other", "expenditure", "met_by_emp"], "50.00", "2026-06-21"),
          "wprepair": (["wpay_other", "expenditure"], "60.00", "2026-06-22"),
          "plaundry": (PAY + ["expenditure"], "30.00", D30),
          "ptools": (PAY + ["expenditure"], "40.00", D30),
          "ptrain": (PAY + ["expenditure"], "50.00", "2026-07-05")},
         judgement=["the £40.00 tools paid to Bob Ltd as required: purchase_emp, purchase_required",
                    "training expenditure intended on 21 June to be met: met_by_emp"]),
    # ---- regs. 14-16 accommodation ----
    june("N025", "1990-01-01", NLW,
         {"p1": basic("949.10"), "acc": (["accommodation"], None, None)},
         runs=[("run1", "acc", 13, True), ("run2", "acc", 16, True), ("run3", "acc", 1, False)],
         judgement=["14 June 2026 (provided only from 2 pm) is a run of 1 day, not whole"]),
    june("N026", "1990-01-01", NLW,
         {"p1": basic("1271.00"), "acc": (["accommodation", "acc_entitled", "deduction", "as_prp"], "300.00", D30)},
         runs=ACC_RUN30),
    june("N027", "1990-01-01", NLW,
         {"p1": basic("1271.00"), "acc": (["accommodation", "acc_entitled", "wpay_emp", "as_prp"], "333.00", D30)},
         runs=ACC_RUN30),
    june("N028", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "acc": (["accommodation", "acc_entitled", "deduction", "as_prp", "payee_lha", "employed_by_payee"],
                  "400.00", D30)},
         runs=ACC_RUN30, judgement=["a county council in England is a local housing authority (reg. 14(3) words)"]),
    june("N029", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "acc": (["accommodation", "acc_entitled", "deduction", "as_prp", "payee_hei", "enrolled_there"],
                  "500.00", D30)},
         runs=ACC_RUN30),
    june("N030", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "acc": (["accommodation", "acc_entitled", "deduction", "as_prp", "payee_hei", "enrolled_there"],
                  "500.00", D30)},
         runs=ACC_RUN30),
    june("N031", "2008-01-01", [],
         {"p1": basic("1085.00"),
          "acc": (["accommodation", "acc_entitled", "deduction", "as_prp", "payee_hei", "enrolled_there"],
                  "500.00", D30)},
         runs=ACC_RUN30),
    june("N032", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "rent1": (["wpay_other", "payee_lha"], "300.00", "2026-06-15"),
          "rent2": (["wpay_other", "payee_lha"], "300.00", D30)},
         judgement=["the private tenancies are not accommodation provided by the employer: no acc item, no runs",
                    "Green County Council (county council in England) and River Housing (private registered "
                    "provider) read as payee_lha (reg. 14(3) words)"]),
    june("N033", "1990-01-01", NLW,
         {"p1": basic("1271.00"),
          "acc": (["accommodation", "acc_entitled", "wpay_emp", "as_prp", "payee_lha", "employed_by_payee"],
                  "500.00", D30)},
         runs=ACC_RUN30,
         judgement=["River Housing (private registered provider of social housing) is a registered social landlord"]),
    june("N034", "1990-01-01", NLW + ["absent"],
         {"p1": basic("1525.20"),
          "absp": (PAY + ["x_hours_not_work"], "508.40", D30),
          "acc": (["accommodation", "acc_entitled", "deduction", "as_prp", "c15a", "c15c", "c15d"], "480.00", D30)},
         runs=ACC_RUN30, unknown={"acc": ["c15b"]},
         judgement=["c15b left unknown: whether the absence pay is not less than the entitlement needs arithmetic",
                    "c15c from the stated 120 against 160 hours, the difference entirely due to the absence"]),
    june("N035", "1990-01-01", NLW + ["absent"],
         {"p1": basic("1525.20"),
          "absp": (PAY + ["x_hours_not_work"], "400.00", D30),
          "acc": (["accommodation", "acc_entitled", "deduction", "as_prp", "c15a", "c15c", "c15d"], "480.00", D30)},
         runs=ACC_RUN30, unknown={"acc": ["c15b"]},
         judgement=["c15b left unknown: whether the absence pay is not less than the entitlement needs arithmetic",
                    "c15c from the stated 120 against 160 hours, the difference entirely due to the absence"]),
]

PROBES = {
    "N036": "a period beginning 1 March 2026, before the window (1 April - 1 October 2026) for which the text is in force",
    "N037": "the hours of work H under Part 5 (not supplied; Part 5 out of scope)",
    "N038": "whether a volunteer is a worker entitled to the national minimum wage (worker status, not stated)",
    "N039": "a penalty for underpayment (enforcement, outside regs. 4-16)",
    "N040": "the worker's age and national living wage status (not supplied)",
    "N041": "statutory arrears in November 2026 (Act s. 17, outside regs. 4-16)",
}
PROBE_QIDS = {
    "N036": ["N036-1", "N036-2", "N036-3"],
    "N037": ["N037-1"],
    "N038": ["N038-1"],
    "N039": ["N039-1"],
    "N040": ["N040-1"],
    "N041": ["N041-1"],
}
UNSUPPORTED = {
}
