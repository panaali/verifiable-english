"""CROSS-FAMILY: write xfam/dates.jsonl from xfam/cases_xfam.py and xfam/questions-enc.jsonl, exactly as the frozen
bridge/make_dates.py does for cases.py. Then: python3 -I ../bridge/bridges.py --cases dates.jsonl > bridges.jsonl
usage (from usecases/faa-medical/xfam): python3 -I make_dates.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cases_xfam as K  # noqa: E402

enc = {d["id"]: d for d in (json.loads(x) for x in open(os.path.join(HERE, "questions-enc.jsonl")) if x.strip())}
with open(os.path.join(HERE, "dates.jsonl"), "w") as f:
    for c in K.CASES:
        q = enc[c["id"]]
        assert q["date"] == c["dates"]["flight_day"], c["id"]
        f.write(json.dumps({"id": c["id"], "facts": q["facts"] + " " + q["date"], **c["dates"]}, sort_keys=True) + "\n")
