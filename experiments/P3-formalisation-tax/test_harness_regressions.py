"""Regressions from the cross-family review of 94274a9 (VE encoding + reference together).

  * IAM context-key names are case-insensitive: re-casing w02's condition key
    (aws:RequestedRegion -> AWS:REQUESTEDREGION) or the request's context keys must not
    change either the reference or the VE answer.
  * Cedar record equality needs equal key sets: an extra key in a c21 assigned_orgs
    record makes Rule 1a false (the first-pass formalisation missed this).
  * c20: a tag that is not a set makes .contains/.containsAll a type error (policy skipped).
  * The structured-review answer keys still equal the (fixed) reference's answers, and VE
    gives the same 75 answers on those packets.

Run: uv run python test_harness_regressions.py
"""
from __future__ import annotations

import copy
import json

import harness as H


def answers(item, world, request, subdir=""):
    H.FORMAL_SUBDIR = subdir
    try:
        env, doc, bindings = H.load_formalisation(item)
        ve = H.ve_answer(item, env, doc, bindings, {}, world, request)["answer"]
    finally:
        H.FORMAL_SUBDIR = ""
    return ve, H.ref_answer(item, {}, world, request)


def test_iam_key_case():
    item = H.load_item("w02_deny_requested_region")
    upper = json.loads(json.dumps(item["world"]).replace('"aws:RequestedRegion"', '"AWS:REQUESTEDREGION"'))
    assert upper != item["world"]
    seen = set()
    for q in item["questions"]:
        base = answers(item, item["world"], q["request"])
        assert base[0] == base[1], q["description"]
        for world in (item["world"], upper):
            for fold in (str, str.upper, str.lower):
                req = dict(q["request"], context={fold(k): v for k, v in q["request"]["context"].items()})
                assert answers(item, world, req) == base, (q["description"], fold)
        seen.add(base[1])
    assert seen == {True, False}
    # policy variables: w03's ${aws:username} with a re-cased context key
    item = H.load_item("w03_mfa_selfmanage")
    for q in item["questions"]:
        if "aws:username" in q["request"]["context"]:
            req = copy.deepcopy(q["request"])
            req["context"]["AWS:UserName"] = req["context"].pop("aws:username")
            assert answers(item, item["world"], req) == answers(item, item["world"], q["request"]), q["description"]
            for sub in ("", "agent"):
                ve, ref = answers(item, item["world"], req, sub)
                assert ve == ref, (sub, q["description"])


def c21_extra_key_world():
    item = H.load_item("c21_tax_preparer")
    q = next(q for q in item["questions"] if q["recorded_decision"] == "allow"
             and q["request"]["resource"].endswith('"ABC"'))
    world = copy.deepcopy(item["world"])
    alice = next(e for e in world["entities"] if e["uid"] == q["request"]["principal"])
    alice["attrs"]["assigned_orgs"][0]["extra"] = "x"
    return item, q, world


def test_c21_record_extra_key():
    item, q, world = c21_extra_key_world()
    assert answers(item, item["world"], q["request"]) == (True, True)
    assert answers(item, world, q["request"]) == (False, False)
    # the frozen first pass is the defect the review found
    assert answers(item, world, q["request"], "first_pass") == (True, False)


def test_c20_non_set_tag():
    item = H.load_item("c20_tags_n_roles")
    q = next(q for q in item["questions"] if q["recorded_decision"] == "allow")
    world = copy.deepcopy(item["world"])
    ws = next(e for e in world["entities"] if e["uid"] == q["request"]["resource"])
    ws["attrs"]["tags"]["stage"] = "ALL"  # a String where the policy calls .contains/.containsAll
    assert answers(item, item["world"], q["request"]) == (True, True)
    assert answers(item, world, q["request"]) == (False, False)
    assert answers(item, world, q["request"], "first_pass")[0] is True  # first pass ignored the type error


def test_targeted_generators_hit_the_cases():
    for iid, op in (("w02_deny_requested_region", "key_case"), ("c21_tax_preparer", "record_extra_key")):
        ps = H.targeted_perturbations(H.load_item(iid))
        assert ps and all(p["ops"][-1] == op for p in ps), iid
    assert not H.targeted_perturbations(H.load_item("k01_pod_reader"))


def test_review_keys_match_reference():
    keys = json.loads((H.HERE / "review_packets" / "keys.json").read_text())
    for iid, key in keys.items():
        item = H.load_item(iid)
        packet = json.loads((H.HERE / "review_packets" / f"{iid}.json").read_text())
        env, doc, bindings = H.load_formalisation(item)
        for q, want in zip(packet["questions"], key):
            if "request" in q:
                got = H.ref_answer(item, {}, item["world"], q["request"])
                ve = H.ve_answer(item, env, doc, bindings, {}, item["world"], q["request"])["answer"]
            else:
                aq = {"target": q["target"], "instance": q["instance"]}
                got = H.ref_answer(item, aq, q["instance"], None)
                ve = H.ve_answer(item, env, doc, bindings, aq, q["instance"], None)["answer"]
            assert got == want == ve, (iid, q["n"])


if __name__ == "__main__":
    test_iam_key_case()
    test_c21_record_extra_key()
    test_c20_non_set_tag()
    test_targeted_generators_hit_the_cases()
    test_review_keys_match_reference()
    print("harness regressions: OK")
