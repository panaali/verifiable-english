"""Smoke test of the translation on MADE-UP cases (not from the question file), run before the encoder read any question.
No Lean. Usage: .venv/bin/python -B usecases/app_levy/smoke.py"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402


def mk(cid, persons, earnings, groups, facts, ints, asks):
    qs = [{"qid": f"{cid}-{i}", "form": f, "item": x} for i, (f, x) in enumerate(asks, 1)]
    return {"id": cid, "persons": persons, "earnings": earnings, "groups": groups, "facts": facts, "ints": ints,
            "questions": qs}


ALL3 = lambda x: [("charged", x), ("amount", x), ("allowance", x)]
cases = [
    # X1 single employer, pay bill 4,000,000: 0.5 % = 20,000 > 15,000 -> charged 5,000.00
    mk("X1", ["a"], {"j1": "a", "j2": "a"}, {}, ["company:a", "sec:j1", "liab:j1", "sec:j2", "butfor:j2"],
       {"earn_j1": "3990000.00", "earn_j2": "10000.00"}, ALL3("a")),
    # X2 pay bill 3,000,000 exactly: 15,000 = 15,000 -> not charged, 0.00
    mk("X2", ["a"], {"j1": "a", "j2": "a"}, {}, ["company:a", "sec:j1", "liab:j1", "sec:j2"],
       {"earn_j1": "3000000.00", "earn_j2": "500000.00"}, ALL3("a")),
    # X3 odd pay bill without half-up -> refused amount; with half-up -> 5,000.01 (3,000,001.00 x 0.005 = 15000.005)
    mk("X3", ["a", "b"], {"j1": "a", "j2": "b"}, {}, ["company:a", "sec:j1", "liab:j1", "sec:j2", "liab:j2", "halfup:b"],
       {"earn_j1": "4000001.00", "earn_j2": "4000001.00"}, ALL3("a") + ALL3("b")),
    # X4 unit of two with a determination 10,000 / 5,000
    mk("X4", ["a", "b"], {"j1": "a", "j2": "b"}, {"g": ["a", "b"]},
       ["company:a", "company:b", "sec:j1", "liab:j1", "sec:j2", "liab:j2", "conn:a:g", "conn:b:g", "detmade:g"],
       {"earn_j1": "4000000.00", "earn_j2": "1000000.00", "det_a": "10000.00", "det_b": "5000.00"},
       ALL3("a") + ALL3("b")),
    # X5 (13) applies, three members: 5,000 each
    mk("X5", ["a", "b", "c"], {"j1": "a", "j2": "b", "j3": "c"}, {"g": ["a", "b", "c"]},
       ["company:a", "company:b", "llp:c", "sec:j1", "liab:j1", "sec:j2", "liab:j2", "sec:j3", "liab:j3",
        "conn:a:g", "conn:b:g", "conn:c:g", "noreturns:g", "notified13:a", "notified13:b", "notified13:c",
        "not_taken13:g", "dues_stated:g"],
       {"earn_j1": "4000000.00", "earn_j2": "2000000.00", "earn_j3": "1000000.00", "paid_a": "0.00", "paid_b": "0.00",
        "paid_c": "0.00", "due_a": "5000.00", "due_b": "0.00", "due_c": "0.00"}, ALL3("a") + [("allowance", "c")]),
    # X6 (8) applies: a and b relevant (returns 15,000 + 15,000), c not relevant -> c 0.00, a/b refused
    mk("X6", ["a", "b", "c"], {"j1": "a", "j2": "b", "j3": "c"}, {"g": ["a", "b", "c"]},
       ["company:a", "company:b", "company:c", "sec:j1", "liab:j1", "sec:j2", "liab:j2", "sec:j3", "liab:j3",
        "conn:a:g", "conn:b:g", "conn:c:g", "ret9:a", "ret9:b", "aware:a", "aware:b", "notified8:a", "notified8:b",
        "not_taken8:g"],
       {"earn_j1": "4000000.00", "earn_j2": "2000000.00", "earn_j3": "5000000.00", "ret_a": "15000.00",
        "ret_b": "15000.00"}, [("allowance", "c"), ("amount", "c"), ("allowance", "a")]),
    # X7 (13) with three members, 15,000 / 7? use 7 members? -> two members of a group of 3 (c no pay bill):
    # 7,500 each; c none -> 0.00, not charged
    mk("X7", ["a", "b", "c"], {"j1": "a", "j2": "b", "j3": "c"}, {"g": ["a", "b", "c"]},
       ["company:a", "company:b", "company:c", "sec:j1", "liab:j1", "sec:j2", "liab:j2", "sec:j3",
        "conn:a:g", "conn:b:g", "conn:c:g", "insufficient:g", "notified13:a", "notified13:b",
        "not_taken13:g"],
       {"earn_j1": "4000000.00", "earn_j2": "2000000.00", "earn_j3": "100.00", "paid_a": "1000.00",
        "paid_b": "0.00"}, ALL3("a") + ALL3("c")),
    # X8 (13) with rounding: three members, 15,000 / 3 exact; use pool with stated rounding up on an exact share
    # X8 determination fails (4) (total 14,000), corrected to 9,000 / 6,000 -> corrected used
    mk("X8", ["a", "b"], {"j1": "a", "j2": "b"}, {"g": ["a", "b"]},
       ["company:a", "company:b", "sec:j1", "liab:j1", "sec:j2", "liab:j2", "conn:a:g", "conn:b:g", "detmade:g",
        "altmade:g"],
       {"earn_j1": "4000000.00", "earn_j2": "1000000.00", "det_a": "10000.00", "det_b": "4000.00",
        "alt_a": "9000.00", "alt_b": "6000.00"}, ALL3("a")),
    # X9 seven-member (13) rounding: use 4 members of 15,000/4 = 3,750 exact; and a 7-way share needs rounding.
    mk("X9", list("abcdefg"), {f"j{x}": x for x in "abcdefg"}, {"g": list("abcdefg")},
       [f"company:{x}" for x in "abcdefg"] + [f"sec:j{x}" for x in "abcdefg"] + [f"liab:j{x}" for x in "abcdefg"]
       + [f"conn:{x}:g" for x in "abcdefg"] + [f"notified13:{x}" for x in "abcdefg"]
       + ["noreturns:g", "not_taken13:g", "rnd_up:a", "rnd_down:b"],
       {**{f"earn_j{x}": "1000000.00" for x in "abcdefg"}, **{f"paid_{x}": "0.00" for x in "abcdefg"}},
       [("allowance", "a"), ("allowance", "b"), ("allowance", "c")]),
]
for c in cases:
    a, *_ = R.run_case(c)
    print(c["id"], json.dumps(a))
