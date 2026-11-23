"""Smoke test of the translation on eleven MADE-UP cases (not from the question file), run before the encoder read any
question. No Lean. Usage: .venv/bin/python -B usecases/eu_sea_passengers/smoke.py"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
import run as R
STD = ["commercial","pax_transport","by_sea","timetable","vessel","contract","doc","person","offers_public",
       "works_e","regular_e","works_d","regular_d","in_ms_e","in_ms_d","est_ms"]
def mk(cid, facts, ints, forms=("applies","right","pay")):
    return {"id": cid, "facts": facts, "ints": ints, "questions": [{"qid": f"{cid}-{i}", "form": f} for i, f in enumerate(forms, 1)]}
base = {"cap_p": 400, "crew_p": 12, "dist_p": 40000, "nights_p": 0, "sch_h_p": 3, "sch_m_p": 0, "del_h_p": 1, "del_m_p": 30, "price_p": "40.00"}
cases = [
 mk("X1", STD, base),                                   # 25% of 40 = 10.00
 mk("X2", STD, {**base, "del_h_p": 2, "del_m_p": 1}),   # 50% = 20.00
 mk("X3", STD + ["ret"], {**base, "rprice_p": "80.00", "del_h_p": 2, "del_m_p": 0}),  # 25% of 40 = 10.00 (exactly double, not exceeding)
 mk("X4", STD + ["has_thr"], {**base, "price_p": "20.00", "thr_p": "6.00"}),  # comp 5.00 < 6 -> pay 0, Q2 refused
 mk("X5", STD + ["has_thr"], {**base, "price_p": "20.00", "thr_p": "8.00"}),  # doubt -> Q3 refused
 mk("X6", [f for f in STD if f != "in_ms_e"], base),    # (b): Union carrier (est) -> applies
 mk("X7", STD + ["not_mech"], {**base, "cap_p": 50}),   # R3 differ -> Q1 refused
 mk("X8", STD + ["pleasure","accomm"], {**base, "nights_p": 3}),  # cruise: applies yes, right no, 0
 mk("X9", STD + ["fault"], base),
 mk("X10", STD, {**base, "del_h_p": 0, "del_m_p": 59}),  # below -> no, 0
 mk("X11", [f for f in STD if f not in ("est_ms","in_ms_e")], base),  # (b) own service -> Union carrier
]
for c in cases:
    a, *_ = R.run_case(c)
    print(c["id"], json.dumps(a))
