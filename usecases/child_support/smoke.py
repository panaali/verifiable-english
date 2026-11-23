"""Smoke test on MADE-UP cases (written before questions-enc.jsonl was opened; not the writer's cases). SAME-FAMILY.

Usage (repository root): .venv/bin/python -B usecases/child_support/smoke.py [--lean]
Each case's expected answers were worked by hand from the pinned text; the test fails on any difference.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402


def case(cid, qs, children, persons=("pat",), benefits=(), facts=None, pairs=None, ints=None):
    return {"id": cid, "parent": "sam", "children": list(children), "persons": list(persons), "benefits": list(benefits),
            "facts": facts or {}, "pairs": pairs or {}, "ints": ints or {},
            "questions": [{"qid": f"{cid}-{i}", "item": it, "form": fm} for i, (it, fm, _) in enumerate(qs, 1)],
            "expect": {f"{cid}-{i}": e for i, (_, _, e) in enumerate(qs, 1)}}


QC = ["qcalc", "childof"]
CASES = [
    case("S01", [("sam", "rate", "basic"), ("pat", "amount", "76.80"), ("amy", "share", "none")], ["amy"],
         facts={"amy": QC}, pairs={"amy@pat": ["pwc"]}, ints={"inc_sam": "640.00"}),
    case("S02", [("pat", "amount", "120.00"), ("amy", "share", "Two-sevenths"), ("bob", "share", "none")], ["amy", "bob"],
         facts={"amy": QC, "bob": QC}, pairs={"amy@pat": ["pwc"], "bob@pat": ["pwc"]},
         ints={"inc_sam": "900.00", "nights_amy": "104"}),
    case("S03", [("pat", "amount", "13.00"), ("kim", "amount", "40.00"), ("amy", "share", "One-half")], ["amy", "bob"],
         persons=("pat", "kim"), facts={"amy": QC, "bob": QC}, pairs={"amy@pat": ["pwc"], "bob@kim": ["pwc"]},
         ints={"inc_sam": "500.00", "nights_amy": "175"}),
    case("S04", [("sam", "rate", "flat"), ("pat", "amount", "0.00"), ("amy", "share", "OPEN")], ["amy"],
         benefits=("jsa",), facts={"amy": QC, "jsa": ["b41b"]}, pairs={"amy@pat": ["pwc"], "sam@jsa": ["paid"]},
         ints={"inc_sam": "300.00", "nights_amy": "60"}),
    case("S05", [("sam", "rate", "nil"), ("pat", "amount", "0.00"), ("amy", "share", "none")], ["amy"],
         facts={"sam": ["presc5a"], "amy": QC}, pairs={"amy@pat": ["pwc"]}, ints={"inc_sam": "400.00", "nights_amy": "80"}),
    case("S06", [("sam", "rate", "OPEN"), ("pat", "amount", "32.00")], ["amy", "dan"],
         facts={"amy": QC, "dan": ["childof", "morder", "habuk"]}, pairs={"amy@pat": ["pwc"]},
         ints={"inc_sam": "400.00"}),
    case("S07", [("sam", "rate", "reduced"), ("pat", "amount", "18.00")], ["amy"],
         facts={"amy": QC}, pairs={"amy@pat": ["pwc"]}, ints={"inc_sam": "150.00", "redrate_sam": "18.00"}),
    case("S08", [("sam", "rate", "reduced"), ("pat", "amount", "7.00"), ("amy", "share", "One-half")], ["amy"],
         facts={"amy": QC}, pairs={"amy@pat": ["pwc"]},
         ints={"inc_sam": "150.00", "redrate_sam": "10.00", "nights_amy": "200"}),
    case("S09", [("sam", "rate", "basic"), ("pat", "amount", "264.30")], ["amy", "cal"], persons=("pat", "lee"),
         facts={"amy": QC}, pairs={"amy@pat": ["pwc"], "lee@cal": ["cbpaid"], "sam@lee": ["married", "samehh"]},
         ints={"inc_sam": "3500.00"}),
    case("S10", [("sam", "rate", "flat"), ("pat", "amount", "7.50")], ["amy"], persons=("pat", "lee"), benefits=("esa",),
         facts={"amy": QC, "lee": ["alsonrp", "calcinforce"], "esa": ["b41c"]},
         pairs={"amy@pat": ["pwc"], "sam@lee": ["livetog"], "lee@esa": ["paid"]},
         ints={"inc_sam": "90.00", "flatamt_sam": "7.50"}),
    case("S11", [("sam", "rate", "flat"), ("pat", "amount", "7.00"), ("amy", "share", "none")], ["amy"],
         facts={"amy": QC}, pairs={"amy@pat": ["pwc"]}, ints={"inc_sam": "100.00", "nights_amy": "120"}),
]


class K:
    CASES, PROBES, PROBE_QIDS, UNSUPPORTED = CASES, {}, {}, {}


def main():
    bad = 0
    if "--lean" in sys.argv:
        out = R.main(["--out", "/tmp/child-support-smoke-run.json"], K=K)
        got = {q: a for r in out["records"] for q, a in r["answers"].items()}
    else:
        got = {}
        for c in CASES:
            got.update(R.run_case(c)[0])
    for c in CASES:
        for qid, exp in c["expect"].items():
            a = got[qid]
            val = a.get("gbp", a["answer"])
            ok = val == exp
            bad += not ok
            print(("ok  " if ok else "BAD ") + qid, exp, "<-", a)
    print("smoke:", "PASS" if bad == 0 else f"FAIL {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
