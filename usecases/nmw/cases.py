"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-nmw-1123 (Opus 5.5), after the translation was committed (eee2ae44b9, 14:49Z).
One RECORD per pay reference period asked about (a case with two periods gives two records, "N011.1", "N011.2"). Each
record: "items" (the worker w, every payment, deduction, worker payment, benefit and provision of living accommodation the
facts name, and each stated run of accommodation days), "facts" (the unary facts true of each item; every other FACTS
entry is false, encode.py C1, except "unknown"), "links" (run_of), "ints" (stated amounts, days and day counts; the
period's first and last day; the following period's from the calendar, C5), "bridge" (the dates the bridge script reads:
date of birth, commencement, earlier commencement), "questions" (qid -> form: rate = Q1, rem = Q2, paid = Q3),
"judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder judgement"), "calendar" (C5
readings). PROBES: out-of-scope cases (all answered UNSUPPORTED).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "399f5771d3396a074b395e1530c9e3c69c8e41ff8be762a55b9d02daeb1bc39d"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

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

CASES = [
    rec("N001", *JUNE, "1990-03-03", ["nlw"], {
        "p1": (PAY, "1652.30", "2026-06-30"),
        "p2": (PAY + ["x_court", "due_contract"], "254.20", "2026-06-26"),
        "p3": (["emp_payment", "x_court"], "750.00", "2026-06-26")}, qs("N001", 1, 2, 3),
        judgement=["N001: the £1,004.20 tribunal settlement taken as its two stated parts, £254.20 contract pay due "
                   "(reg. 10(c) 'other than ... an amount due under the worker's contract') and £750.00 compensation"],
        calendar=[CAL_MONTH]),
    rec("N002", "2026-07-06", "2026-07-12", "2026-07-13", "2026-07-19", "1985-08-14", ["nlw"], {
        "p1": (PAY, "444.50", "2026-07-10"),
        "p2": (PAY + ["part_excluded"], "95.25", "2026-07-10")}, qs("N002", 1, 2, 3),
        judgement=["N002: the £95.25 for 5 further hours at £19.05, the same work for which £12.70 is payable, read as a "
                   "payment within reg. 10(j) whose excess over the lowest rate is not stated as its own amount"],
        calendar=[CAL_WEEK]),
    rec("N003", *JUNE, "2005-06-15", [], {
        "p1": (PAY, "1686.00", "2026-06-30"),
        "p2": (PAY + ["arrangement_pay"], "120.00", "2026-06-30"),
        "p3": (PAY + ["performance"], "50.00", "2026-06-30")}, qs("N003", 1, 2, 3),
        judgement=["N003: the night-shift allowance read as attributable to a particular aspect of the working "
                   "arrangements (reg. 10(k)); the sales-target bonus as attributable to performance"],
        calendar=[CAL_MONTH]),
    rec("N004", *JULY, "2005-07-01", ["nlw"], {
        "p1": (PAY, "1850.10", "2026-07-31"),
        "p2": (PAY + ["arrangement_pay", "consolidated"], "56.50", "2026-07-31")}, qs("N004", 1, 2, 3),
        judgement=["N004: the London allowance read as attributable to working circumstances (reg. 10(k)), consolidated"],
        calendar=[CAL_MONTH]),
    rec("N005", "2026-09-14", "2026-09-20", "2026-09-21", "2026-09-27", "2008-09-16", [], {
        "p1": (PAY, "200.00", "2026-09-18"),
        "p2": (PAY + ["x_tips"], "30.00", "2026-09-18")}, qs("N005", 1, 2, 3), calendar=[CAL_WEEK]),
    rec("N006", *JUNE, "2008-02-10", ["contract_appr"], {"p1": (PAY, "1150.00", "2026-06-30")}, qs("N006", 1, 2, 3),
        start="2025-03-02", calendar=[CAL_MONTH]),
    rec("N007", *JUNE, "2006-05-05", ["contract_appr"], {"p1": (PAY, "1300.00", "2026-06-30")}, qs("N007", 1, 2, 3),
        start="2025-02-02", calendar=[CAL_MONTH]),
    rec("N008", *AUG, "1995-12-12", ["nlw", "eng_wales", "made_wal", "known_wales"],
        {"p1": (PAY, "1200.00", "2026-08-31")}, qs("N008", 1, 2, 3), start="2025-10-15", calendar=[CAL_MONTH]),
    rec("N009", *AUG, "2007-08-01", ["eng_scotland", "made_sco", "known_scotland"],
        {"p1": (PAY, "1250.00", "2026-08-31")}, qs("N009", 1, 2, 3), start="2025-07-04", calendar=[CAL_MONTH]),
    rec("N010", *MAY, "2007-05-18", ["eng_ni", "made_ni", "known_ni"],
        {"p1": (PAY, "1288.00", "2026-05-29")}, qs("N010", 1, 2, 3), start="2025-01-06", calendar=[CAL_MONTH]),
    rec("N011.1", "2026-08-31", "2026-09-06", "2026-09-07", "2026-09-13", "2004-03-01",
        ["nlw", "eng_england", "made_eng", "tb_agreement", "tb_standard"], {
            "p1": (PAY, "375.00", "2026-09-04"),
            "p2": (["emp_payment"], "375.00", "2026-09-11")}, qs("N011", 1, 2, 3), start="2025-09-07",
        calendar=[CAL_WEEK]),
    rec("N011.2", "2026-09-07", "2026-09-13", "2026-09-14", "2026-09-20", "2004-03-01",
        ["nlw", "eng_england", "made_eng", "tb_agreement", "tb_standard"], {
            "p1": (["emp_payment", "as_prev"], "375.00", "2026-09-04"),
            "p2": (PAY, "375.00", "2026-09-11")}, qs("N011", 4, 5, 6), start="2025-09-07", calendar=[CAL_WEEK]),
    rec("N012", *JUNE, "2004-11-09", ["nlw", "contract_appr", "prior_continuity"],
        {"p1": (PAY, "1800.00", "2026-06-30")}, qs("N012", 1, 2, 3), start="2026-02-01", prior_start="2025-03-03",
        calendar=[CAL_MONTH]),
    rec("N013", *JUNE, "2003-01-02", ["nlw", "eng_england", "known_england"], {
        "wp1": (["wpay_emp", "purchase_emp", "purchase_required", "own_use", "expenditure", "met_by_emp"], "60.00",
                "2026-06-03"),
        "wp2": (["wpay_other", "expenditure", "met_by_emp"], "45.00", "2026-06-04"),
        "p1": (["emp_payment", "expenditure"], "105.00", "2026-06-30"),
        "p2": (PAY, "1645.20", "2026-06-30"),
        "d1": (["deduction", "expenditure"], "120.00", "2026-06-30")}, qs("N013", 1, 2, 3),
        judgement=["N013: the required uniform, the safety boots and the required safety course fee read as the worker's "
                   "expenditure in connection with the employment; the £1,645.20 read as the pay before the £120.00 "
                   "deduction; the guild's scheme called Apprenticeships read as arrangements known by that name but "
                   "not made under ETA 1973 s. 2 / JSA 1995 s. 17B (stated)"],
        calendar=[CAL_MONTH]),
    rec("N014.1", *MAY, "1980-11-22", ["nlw"], {
        "p1": (PAY, "1800.00", "2026-05-29"),
        "p2": (PAY, "106.50", "2026-06-05"),
        "p3": (["emp_payment"], "1800.00", "2026-06-30")}, qs("N014", 1, 2, 3), calendar=[CAL_MONTH]),
    rec("N014.2", *JUNE, "1980-11-22", ["nlw"], {
        "p1": (["emp_payment", "as_prev"], "1800.00", "2026-05-29"),
        "p2": (["emp_payment", "as_prev"], "106.50", "2026-06-05"),
        "p3": (PAY, "1800.00", "2026-06-30")}, qs("N014", 4, 5, 6), calendar=[CAL_MONTH]),
    rec("N015", *JUNE, "1975-07-07", ["nlw"], {
        "p1": (PAY + ["rec_obligation", "rec_condition", "rec_given", "rec_paid_window"], "1300.00", "2026-08-28")},
        qs("N015", 1, 2, 3), ints={"fourthwd": "2026-07-27", "recday_p1": "2026-08-03"},
        calendar=[CAL_MONTH, "N015: 3 and 28 August 2026 fall in the August 2026 period (rec_paid_window)"]),
    rec("N016", *JUNE, "1983-04-21", ["nlw"], {
        "p1": (PAY, "400.00", "2026-06-30"),
        "p2": (PAY + ["rec_obligation", "rec_condition", "rec_given"], "1300.00", "2026-10-02")},
        qs("N016", 1, 2, 3), ints={"fourthwd": "2026-07-27", "recday_p2": "2026-08-03"},
        calendar=[CAL_MONTH, "N016: the record given 3 August 2026 (August period); 2 October 2026 is in neither the "
                             "August nor the September period (rec_paid_window false)"]),
    rec("N017", *JUNE, "1988-10-12", ["nlw"], {
        "p1": (PAY + ["rec_obligation", "rec_condition", "rec_given", "rec_paid_window"], "1300.00", "2026-08-10")},
        qs("N017", 1, 2, 3), ints={"fourthwd": "2026-07-27", "recday_p1": "2026-07-27"},
        calendar=[CAL_MONTH, "N017: the record given 27 July 2026 (July period); 10 August 2026 is in the period after "
                             "(rec_paid_window)"]),
    rec("N018", "2026-06-08", "2026-06-14", "2026-06-15", "2026-06-21", "1988-04-30", ["nlw", "terminated"], {
        "p1": (["emp_payment", "as_prev"], "390.00", "2026-06-12"),
        "p2": (PAY, "360.00", "2026-07-10"),
        "p3": (PAY, "21.30", "2026-07-20")}, qs("N018", 1, 2, 3),
        ints={"termday": "2026-06-14", "monthend": "2026-07-14"}, calendar=[CAL_WEEK]),
    rec("N019", *JUNE, "1999-01-11", ["nlw"], {
        "acc1": (["accommodation"], None, None),
        "p1": (PAY, "1573.50", "2026-06-30")}, qs("N019", 1, 2, 3), runs=[("run1", "acc1", 30, True)],
        calendar=[CAL_MONTH]),
    rec("N020", *JUNE, "1996-09-19", ["nlw"], {
        "acc1": (["accommodation", "acc_entitled"], "400.00", None),
        "p1": (PAY, "1984.00", "2026-06-30")}, qs("N020", 1, 2, 3),
        runs=[("run1", "acc1", 1, False), ("run2", "acc1", 29, True)],
        judgement=["N020: the £400.00 deducted for the room is the accommodation item's entitled amount (one item, reg. 14)"],
        calendar=[CAL_MONTH]),
    rec("N021", *JULY, "1992-02-02", ["nlw"], {
        "acc1": (["accommodation", "acc_entitled"], "300.00", None),
        "p1": (PAY, "1800.00", "2026-07-31")}, qs("N021", 1, 2, 3), runs=[("run1", "acc1", 31, True)],
        judgement=["N021: the £300.00 deducted for the room is the accommodation item's entitled amount"],
        calendar=[CAL_MONTH]),
    rec("N022", "2026-06-22", "2026-06-28", "2026-06-29", "2026-07-05", "2000-08-08", ["nlw"], {
        "acc1": (["accommodation", "acc_entitled"], "77.70", None),
        "p1": (PAY, "560.00", "2026-06-26"),
        "d1": (["deduction", "own_use", "loan_repay"], "50.00", "2026-06-26"),
        "wp1": (["wpay_emp", "own_use", "purchase_emp"], "35.00", "2026-06-23"),
        "wp2": (["wpay_other", "expenditure"], "45.00", "2026-06-24")}, qs("N022", 1, 2, 3),
        runs=[("run1", "acc1", 7, True)],
        judgement=["N022: the £77.70 paid for the room is the accommodation item's entitled amount; the non-slip shoes "
                   "read as expenditure in connection with the employment"],
        calendar=[CAL_WEEK]),
    rec("N023", *JUNE, "2007-03-04", [], {
        "acc1": (["accommodation", "acc_entitled", "payee_hei", "enrolled_there"], "600.00", None),
        "p1": (PAY, "1100.00", "2026-06-30")}, qs("N023", 1, 2, 3), runs=[("run1", "acc1", 30, True)],
        calendar=[CAL_MONTH]),
    rec("N024", *JUNE, "2008-10-05", [], {
        "acc1": (["accommodation", "acc_entitled", "payee_hei", "enrolled_there"], "450.00", None),
        "p1": (PAY, "480.00", "2026-06-30")}, qs("N024", 1, 2, 3), runs=[("run1", "acc1", 30, True)],
        calendar=[CAL_MONTH]),
    rec("N025", *JUNE, "2005-12-12", [], {
        "acc1": (["accommodation", "acc_entitled", "payee_hei"], "400.00", None),
        "p1": (PAY, "1152.00", "2026-06-30")}, qs("N025", 1, 2, 3), runs=[("run1", "acc1", 30, True)],
        calendar=[CAL_MONTH]),
    rec("N026", *JUNE, "1984-01-17", ["nlw"], {
        "acc1": (["accommodation", "acc_entitled", "payee_lha"], "520.00", None),
        "p1": (PAY, "1906.50", "2026-06-30")}, qs("N026", 1, 2, 3), runs=[("run1", "acc1", 30, True)],
        judgement=["N026: a council flat let from the general waiting list, 'nothing to do with his job', read as not "
                   "provided in connection with his employment with the authority"],
        calendar=[CAL_MONTH]),
    rec("N027", *JUNE, "1979-12-25", ["nlw"], {
        "acc1": (["accommodation", "acc_entitled", "payee_lha", "employed_by_payee"], "500.00", None),
        "p1": (PAY, "2070.00", "2026-06-30")}, qs("N027", 1, 2, 3), runs=[("run1", "acc1", 30, True)],
        judgement=["N027: the Northern Ireland Housing Executive read as a local housing authority (reg. 14(3)(c), "
                   "named in the definition); the flat provided because of the job read as in connection with it"],
        calendar=[CAL_MONTH]),
    rec("N028", *JULY, "1997-06-06", ["nlw"], {
        "acc1": (["accommodation", "acc_entitled", "payee_lha"], "600.00", None),
        "p1": (PAY, "1779.40", "2026-07-31")}, qs("N028", 1, 2, 3), runs=[("run1", "acc1", 31, True)],
        judgement=["N028: a flat let through the council register, 'nothing to do with his job', read as not provided "
                   "in connection with his employment with the registered social landlord"],
        calendar=[CAL_MONTH]),
    rec("N029.1", *JUNE, "1993-09-03", ["nlw", "absent"], {
        "acc1": (["accommodation", "acc_entitled", "c15a", "c15c", "c15d"], "600.00", None),
        "p1": (PAY, "1680.00", "2026-06-30"),
        "p2": (PAY + ["x_hours_not_work"], "560.00", "2026-06-30")}, qs("N029", 1, 2, 3),
        runs=[("run1", "acc1", 30, True)], unknown={"acc1": ["c15b"]},
        judgement=["N029: reg. 15(1)(b) (paid for the absent hours not less than the entitlement under the Regulations) "
                   "is left unstated: it needs an amount comparison the facts do not give as such"],
        calendar=[CAL_MONTH]),
    rec("N029.2", *JULY, "1993-09-03", ["nlw", "absent"], {
        "acc1": (["accommodation", "acc_entitled", "c15a", "c15c", "c15d"], "600.00", None),
        "p1": (PAY, "1820.00", "2026-07-31"),
        "p2": (PAY + ["x_hours_not_work"], "532.00", "2026-07-31")}, qs("N029", 4, 5, 6),
        runs=[("run1", "acc1", 31, True)], unknown={"acc1": ["c15b"]},
        judgement=["N029: as for June (reg. 15(1)(b) unstated)"], calendar=[CAL_MONTH]),
    rec("N030", *JUNE, "1987-02-14", ["nlw", "absent"], {
        "acc1": (["accommodation", "acc_entitled", "c15a", "c15c", "c15d"], "600.00", None),
        "p1": (PAY, "1680.00", "2026-06-30")}, qs("N030", 1, 2, 3), runs=[("run1", "acc1", 30, True)],
        judgement=["N030: paid nothing for the absent hours read as reg. 15(1)(b) not met"], calendar=[CAL_MONTH]),
    rec("N031", *JULY, "1991-10-09", ["nlw"], {
        "p1": (["emp_payment", "x_loan_advance"], "200.00", "2026-07-10"),
        "p2": (["emp_payment", "x_suggestion"], "100.00", "2026-07-15"),
        "p3": (["emp_payment", "x_voucher"], "150.00", "2026-07-20"),
        "b1": (["benefit_kind"], "40.00", None),
        "wp1": (["wpay_other", "expenditure", "met_by_emp"], "60.00", "2026-07-08"),
        "p4": (["emp_payment", "expenditure"], "60.00", "2026-07-31"),
        "p5": (["emp_payment", "x_travel338", "expenditure"], "45.00", "2026-07-31"),
        "p6": (PAY, "1779.40", "2026-07-31"),
        "d1": (["deduction", "own_use", "loan_repay"], "200.00", "2026-07-31")}, qs("N031", 1, 2, 3),
        judgement=["N031: work calls on her own phone at the employer's request read as expenditure in connection with "
                   "the employment; the gym membership as a benefit in kind (not a payment)"],
        calendar=[CAL_MONTH]),
    rec("N032", *AUG, "1970-04-28", ["nlw", "terminated"], {
        "p1": (PAY, "1700.00", "2026-08-31"),
        "p2": (["emp_payment", "x_redundancy"], "3000.00", "2026-08-31"),
        "p3": (["emp_payment", "x_retirement"], "2000.00", "2026-08-31"),
        "p4": (PAY, "80.00", "2026-09-11")}, qs("N032", 1, 2, 3),
        ints={"termday": "2026-08-31", "monthend": "2026-09-30"}, calendar=[CAL_MONTH]),
    rec("N033", *JUNE, "1982-05-30", ["nlw"], {
        "p1": (PAY + ["part_excluded"], "1992.95", "2026-06-30"),
        "p2": (["emp_payment", "x_salary_premium"], "300.00", "2026-06-30")}, qs("N033", 1, 2, 3),
        judgement=["N033: the salary instalment of which £150.00 is attributable to reg. 23 hours (reg. 10(i)) is "
                   "excluded in part; the part that counts is not stated as its own amount"],
        calendar=[CAL_MONTH]),
    rec("N034", *JUNE, "1995-03-15", ["nlw"], {
        "p1": (PAY, "1971.50", "2026-06-30"),
        "d1": (["deduction", "own_use"], "25.00", "2026-06-30"),
        "d2": (["deduction", "own_use"], "40.00", "2026-06-30"),
        "d3": (["deduction", "own_use", "conduct_liable"], "40.00", "2026-06-30"),
        "d4": (["deduction", "own_use", "overpayment"], "30.00", "2026-06-30"),
        "d5": (["deduction", "shares"], "50.00", "2026-06-30")}, qs("N034", 1, 2, 3),
        judgement=["N034: the till shortage for which the contract makes her liable read as reg. 12(2)(a)"],
        calendar=[CAL_MONTH]),
    rec("N035", *JUNE, "1998-04-07", ["nlw"], {
        "wp1": (["wpay_emp", "own_use", "purchase_emp", "purchase_required", "expenditure"], "60.00", "2026-06-03"),
        "d1": (["deduction", "own_use", "purchase_emp"], "30.00", "2026-06-30"),
        "p1": (PAY, "1996.50", "2026-06-30")}, qs("N035", 1, 2, 3),
        judgement=["N035: the required uniform used only for work read as expenditure in connection with the employment"],
        calendar=[CAL_MONTH]),
]

PROBES = {
    "N036": "a pay reference period beginning before 1 April 2026 (other rates in force)",
    "N037": "output work: the hours themselves (Part 5) are asked",
    "N038": "whether a volunteer is a worker entitled to the national minimum wage",
    "N039": "a family member living in the employer's household (outside the Act's entitlement)",
    "N040": "no date of birth and no statement about the national living wage rate",
    "N041": "salaried hours work: the hours themselves (Part 5) are asked",
}
PROBE_QIDS = {"N036": ["N036-1", "N036-2", "N036-3"], "N037": ["N037-1"], "N038": ["N038-1", "N038-2"],
              "N039": ["N039-1"], "N040": ["N040-1", "N040-2"], "N041": ["N041-1"]}
UNSUPPORTED = {}
