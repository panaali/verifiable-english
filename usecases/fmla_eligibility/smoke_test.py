"""Smoke test on MADE-UP cases (not from the question file), written with the translation: the staged route (Python
prover, no Lean) must give the hand-worked answers below and refuse where reading R1 refuses. SAME-FAMILY.
usage (repository root): .venv/bin/python -B usecases/fmla_eligibility/smoke_test.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))
import encode as E  # noqa: E402
import fmla_bridge as FB  # noqa: E402
import run as R  # noqa: E402


def br(case, rows):
    return {(case, item): FB.row(r) for item, r in rows.items()}


def mk(cid, leaves, periods, breaks, blocks, facts, ints, rows, qs, period_for=None, precedes=()):
    c = {"id": cid, "leaves": leaves, "periods": periods, "breaks": breaks, "blocks": blocks, "facts": facts,
         "ints": ints, "precedes": list(precedes),
         "questions": [{"qid": f"{cid}-{i}", "item": "l1", "form": f} for i, f in enumerate(qs, 1)]}
    if period_for is not None:
        c["period_for"] = period_for
    return c, br(cid, rows)


ALL = ["eligible", "twelve", "hours", "site"]
CASES = [
    # S1 regular, continuous 8 Jan 2024 -> leave 2 Jun 2025; blocks: one before the window, two inside; 60 employees
    (mk("S1", ["l1"], ["s1"], [], ["h1", "h2", "h3"],
        {"l1": ["acct", "acc_record"], "s1": ["payroll"], "h1": ["h_worked"], "h2": ["h_worked"], "h3": ["h_worked"]},
        {"start_l1": "2025-06-02", "count_l1": 60, "weeks_s1": 73, "hours_h1": "500", "hfrom_h1": "2024-01-08",
         "hto_h1": "2024-06-01", "hours_h2": "700", "hfrom_h2": "2024-06-02", "hto_h2": "2024-12-31", "hours_h3": "600",
         "hfrom_h3": "2025-01-01", "hto_h3": "2025-06-01"},
        {"l1": {"kind": "window", "start": "2025-06-02"}, "s1": {"kind": "duration", "from": "2024-01-08", "to": "2025-06-01"}},
        ALL), ["yes", "yes", "yes", "yes"]),
    # S2 casual: 26 + 26 payroll weeks around a 3-month break; 49 employees on the notice day
    (mk("S2", ["l1"], ["s1", "s2"], ["b1"], ["h1"],
        {"l1": ["acct", "acc_record", "casual"], "s1": ["payroll"], "s2": ["payroll"], "h1": ["h_worked"]},
        {"start_l1": "2026-07-06", "count_l1": 49, "weeks_s1": 26, "weeks_s2": 26, "hours_h1": "1250.00",
         "hfrom_h1": "2025-07-06", "hto_h1": "2026-07-05"},
        {"l1": {"kind": "window", "start": "2026-07-06"}, "s1": {"kind": "duration", "from": "2025-03-31", "to": "2025-09-28"},
         "s2": {"kind": "duration", "from": "2026-01-05", "to": "2026-07-05"},
         "b1": {"kind": "duration", "from": "2025-09-29", "to": "2026-01-04"}},
        ALL, precedes=[("s1", "b1")]), ["no", "yes", "yes", "no"]),
    # S3 regular: 5 years' employment, an 8-year break (not USERRA, no agreement, practice: not counted), 20 weeks since
    (mk("S3", ["l1"], ["s1", "s2"], ["b1"], [],
        {"l1": ["acct", "acc_record"], "s1": ["payroll"], "s2": ["payroll"]},
        {"start_l1": "2026-06-01", "count_l1": 80, "weeks_s1": 261, "weeks_s2": 20},
        {"l1": {"kind": "window", "start": "2026-06-01"}, "s1": {"kind": "duration", "from": "2008-01-07", "to": "2012-12-30"},
         "s2": {"kind": "duration", "from": "2026-01-12", "to": "2026-05-31"},
         "b1": {"kind": "duration", "from": "2012-12-31", "to": "2026-01-11"}},
        ["twelve"], precedes=[("s1", "b1")]), ["no"]),
    # S4 the same with a written rehire agreement: the earlier periods count again
    (mk("S4", ["l1"], ["s1", "s2"], ["b1"], [],
        {"l1": ["acct", "acc_record"], "s1": ["payroll"], "s2": ["payroll"], "b1": ["b_rehire"]},
        {"start_l1": "2026-06-01", "count_l1": 80, "weeks_s1": 261, "weeks_s2": 20},
        {"l1": {"kind": "window", "start": "2026-06-01"}, "s1": {"kind": "duration", "from": "2008-01-07", "to": "2012-12-30"},
         "s2": {"kind": "duration", "from": "2026-01-12", "to": "2026-05-31"},
         "b1": {"kind": "duration", "from": "2012-12-31", "to": "2026-01-11"}},
        ["twelve"], precedes=[("s1", "b1")]), ["yes"]),
    # S5 regular, 52 payroll weeks but 11 months 23 days: R1 refuses; no accurate record, nothing shown: hours met
    (mk("S5", ["l1"], ["s1"], [], [],
        {"l1": [], "s1": ["payroll"]},
        {"start_l1": "2025-12-29", "count_l1": 50, "weeks_s1": 52},
        {"l1": {"kind": "window", "start": "2025-12-29"}, "s1": {"kind": "duration", "from": "2025-01-06", "to": "2025-12-28"}},
        ["twelve", "hours", "site"]), ["OPEN", "yes", "yes"]),
    # S6 a block across the window's first day: no share, hours refused; employer shows (but accounting given: unused)
    (mk("S6", ["l1"], ["s1"], [], ["h1"],
        {"l1": ["acct", "acc_record"], "s1": ["payroll"], "h1": ["h_worked"]},
        {"start_l1": "2026-03-02", "count_l1": 120, "weeks_s1": 60, "hours_h1": "1600", "hfrom_h1": "2025-01-06",
         "hto_h1": "2026-03-01"},
        {"l1": {"kind": "window", "start": "2026-03-02"}, "s1": {"kind": "duration", "from": "2025-01-06", "to": "2026-03-01"}},
        ["hours", "twelve"]), ["OPEN", "yes"]),
]

bad = 0
for (case, rows), want in CASES:
    E.bridges = lambda rows=rows: rows
    got = R.run_case(case)[0]
    vals = [got[q["qid"]]["answer"] for q in case["questions"]]
    ok = vals == want
    bad += not ok
    print(case["id"], "ok" if ok else "FAIL", vals, want)
print(f"{len(CASES) - bad}/{len(CASES)} smoke cases as hand-worked")
sys.exit(1 if bad else 0)
