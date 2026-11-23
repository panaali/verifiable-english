"""Smoke test of the 61.23 machinery on MADE-UP cases (written before the question file was opened; not part of the
number). usage: uv run python -B usecases/faa-medical/smoke.py [--lean]"""
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))
import bridges as BR  # noqa: E402

FACTS = ("Born 14 March 1971 (a smoke case). First-class examination 9 October 2024; third-class examination 2 October "
         "2022. Flight 3 May 2025; flight 1 May 2025; course 4 May 2024; comprehensive examination 2 June 2023.")
CASES = [
    # S1 ATP PIC, age 53 at the exam: first class, 6 months -> valid to 2025-04-30; D 2025-05-03 -> NO
    {"id": "S1", "dates": {"birth": "1971-03-14", "flight_day": "2025-05-03", "certs": {"cert1": "2024-10-09", "cert2": "2022-10-02"}},
     "true": ["atp", "acting_pic"], "certs": {"cert1": {"class": 1, "suspended": False}, "cert2": {"class": 3, "suspended": False}},
     "want": {"Q1": "FIRST CLASS", "Q2": "NO", "Q3": "N/A"}},
    # S2 same, D 2025-04-30 wait: use 1 May -> NO; private privileges: first class age 53 -> 24 months -> 2026-10-31
    {"id": "S2", "dates": {"birth": "1971-03-14", "flight_day": "2025-05-01", "certs": {"cert1": "2024-10-09"}},
     "true": ["private"], "certs": {"cert1": {"class": 1, "suspended": False}},
     "want": {"Q1": "THIRD CLASS", "Q2": "YES", "Q3": "2026-10-31"}},
    # S3 sport pilot under 61.113(i) at night with a driver's license and BasicMed: course 2024-05-04 -> 2026-05-31,
    #    exam 2023-06-02 -> 2027-06-30; D 2025-05-01 -> YES, last day 2026-05-31
    {"id": "S3", "dates": {"birth": "1971-03-14", "flight_day": "2025-05-01", "certs": {"cert1": "2022-10-02"},
                           "course_day": "2024-05-04", "basic_exam_day": "2023-06-02"},
     "true": ["sport", "night", "under_113i", "meets_316", "holds_dl", "dl_complied", "dl_med_complied", "course_done",
              "basic_exam_done"], "certs": {"cert1": {"class": 3, "suspended": False}},
     "want": {"Q1": "CERTIFICATE OR LICENSE", "Q2": "YES", "Q3": "2026-05-31"}},
    # S4 glider pilot in a glider: none
    {"id": "S4", "dates": {"flight_day": "2025-05-01"}, "true": ["private", "glider_rating", "in_glider"],
     "want": {"Q1": None, "Q2": None, "Q3": None}},
]
FAKE = types.ModuleType("cases")
FAKE.CASES = [{k: v for k, v in c.items() if k != "want"} for c in CASES]
FAKE.PROBES, FAKE.MUTANT_TARGETS, FAKE.BRIDGES_SHA256 = {}, {m: [] for m in ("M1", "M2", "M3", "M4", "M5", "M6")}, ""
sys.modules["cases"] = FAKE
import encode as E  # noqa: E402
for c in CASES:
    E._BRIDGES[c["id"]] = BR.bridge_case({"id": c["id"], "facts": FACTS, **c["dates"]})
import run  # noqa: E402

out = run.main(([] if "--lean" in sys.argv else ["--no-lean"]))
bad = 0
for rec, c in zip(out["records"], CASES):
    got = rec["answers"] if "--lean" in sys.argv else rec["staged"]
    print(rec["id"], got, "want", c["want"])
    bad += any(v is not None and got.get(k) != v for k, v in c["want"].items())
print("SMOKE", "FAIL" if bad else "OK")
