"""HICBC: turn the encoder's records (cases.py) and the bridge (bridge/bridges.jsonl) into a case's domains and VE facts.
Mechanical; every reading of a question is in cases.py, every calendar or arithmetic step in the bridge. Closed facts: every
fact predicate gets a literal (true or false) for every tuple of the case's constants, so negative steps can be proved.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import rules as R

HERE = Path(__file__).resolve().parent


def load_bridges(expected_sha=None):
    raw = (HERE / "bridge" / "bridges.jsonl").read_bytes()
    if expected_sha and hashlib.sha256(raw).hexdigest() != expected_sha:
        raise SystemExit("bridge/bridges.jsonl differs from the pinned bridge output")
    return {json.loads(l)["id"]: json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()}


def pc(name):
    return "p_" + name.lower()


def gbp(s):
    v = s if "." in s else s + ".00"
    return ["decimal", "gbp_penny", v]


def case_model(case, br):
    people = [pc(p) for p in case["people"]]
    items = [i["item"] for i in br["items"]]
    pairs = sorted({R.pair_name(a, b) for k, a in enumerate(people) for b in people[k + 1:]})
    dts = sorted(br["daytypes"])
    dom = {"person": people, "item": items, "pair": pairs, "daytype": dts}
    ani_people = [pc(p) for p in case["ani"]]
    facts = []

    def lit(f, val):
        facts.append({"id": f"f{len(facts)}", "formula": f if val else ["not", f]})

    for p, a in sorted(case["ani"].items()):
        facts.append({"id": f"f{len(facts)}", "formula": ["eq", ["const", "gbp_penny", "ani_" + pc(p)], gbp(a)]})
    for it in br["items"]:
        i = it["item"]
        lit(R.U("basis_b", i), it["basis"] == "b")
        lit(R.U("election_13a", i), it["election_13a"])
        lit(R.U("by_145a", i), it["basis"] == "145a")
        lit(R.U("is_child", i), True)
        lit(R.U("d4_short", i), it["d4_short"])
        lit(R.U("d4_a_before", i), it["d4_a_before"])
        lit(R.U("d4_a_after", i), it["d4_a_after"])
        for p in case["people"]:
            lit(R.B("entitled", pc(p), i), p == it["claimant"])
            lit(R.B("child_lives_with", pc(p), i), p in it["lives_with"])
        for d in dts:
            lit(R.B("in_week", d, i), d in it["daytypes"])
    for d in dts:
        for key, flags in br["daytypes"][d]["pairs"].items():
            a, b = key.split("|")
            pr = R.pair_name(pc(a), pc(b))
            for k in R.FACTS:
                if k in ("married_or_cp", "sep_court", "sep_permanent", "as_if_married"):
                    lit(R.B(k, pr, d), flags[k])
    consts = {**dom, "ani": ani_people, "charge": [pc(case["subject"])] if case["subject"] in case["ani"] else []}
    return dom, ani_people, facts, consts
