"""Write bridge/dates.jsonl: each case's stated dates (cases.py) with its facts text (questions-enc.jsonl) for bridges.py,
which refuses any date the facts do not state. usage: python3 -I bridge/make_dates.py (from usecases/faa-medical)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cases as K  # noqa: E402

enc = {d["id"]: d for d in (json.loads(x) for x in open(os.path.join(HERE, "..", "questions-enc.jsonl")) if x.strip())}
with open(os.path.join(HERE, "dates.jsonl"), "w") as f:
    for c in K.CASES:
        q = enc[c["id"]]
        assert q["date"] == c["dates"]["flight_day"], c["id"]
        f.write(json.dumps({"id": c["id"], "facts": q["facts"] + " " + q["date"], **c["dates"]}, sort_keys=True) + "\n")
