"""Citation replay and transitive provenance checks."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ve.ast import Top, Bottom, Not, And, formula_to_data
from ve.bundle import check_bundle
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.profiles import SPEC_REVISION


def bundle():
    env = Environment({"language": "ve.core@0.2", "profiles": ["definitions@0", "relational-fol@0"],
                       "spec_revision": SPEC_REVISION,
                       "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}}})
    top, both = Top(), And(Top(), Top())
    first = {"name": "first", "environment_id": env.environment_id,
             "premises": [{"label": "open:assumption", "ast": formula_to_data(env, top)}], "cites": [],
             "conclusion": formula_to_data(env, top), "meaning_id": meaning_id(env, top),
             "reading_choices": {},
             "transitive_leaves": [{"label": "open:assumption", "ast": formula_to_data(env, top)}],
             "certificate": prove_entailment(env, (top,), top).certificate}
    second = {"name": "second", "environment_id": env.environment_id,
              "premises": deepcopy(first["premises"]), "cites": [first["meaning_id"]],
              "conclusion": formula_to_data(env, both), "meaning_id": meaning_id(env, both),
              "reading_choices": {},
              "transitive_leaves": deepcopy(first["transitive_leaves"]),
              "certificate": prove_entailment(env, (top, top), both).certificate}
    return {"version": "ve-bundle@0", "environment": env.to_dict(), "lemmas": [first, second]}


def test_checked_citation_and_labels():
    report = check_bundle(bundle())
    assert report["status"] == "Checked"
    assert report["lemmas"][1]["transitive_leaves"] == report["lemmas"][0]["transitive_leaves"]


LEAN = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_conformance"


def _cyclic(b):
    """The first lemma cites the second, which is later in the bundle."""
    b["lemmas"][0]["cites"] = [b["lemmas"][1]["meaning_id"]]


def _self_citation(b):
    b["lemmas"][1]["cites"] = [b["lemmas"][1]["meaning_id"]]


def _other_version(b):
    b["lemmas"][1]["environment_id"] = "0" * 64


def _stripped_label(b):
    b["lemmas"][1]["transitive_leaves"][0]["label"] = "asserted"


FORGERIES = [
    (lambda b: b["lemmas"][1]["cites"].__setitem__(0, "absent"), "absent"),
    (lambda b: b["lemmas"][1]["transitive_leaves"].clear(), "labels"),
    (_stripped_label, "labels"),
    (lambda b: b["lemmas"][1]["reading_choices"].__setitem__("u", "0:1"), "reading"),
    (lambda b: b["lemmas"][1]["premises"].clear(), "hypothesis"),
    (_cyclic, "absent, cyclic"),
    (_self_citation, "absent, cyclic"),
    (_other_version, "another environment"),
]


@pytest.mark.parametrize("mutation, diagnostic", FORGERIES)
def test_reject_forged_citation(mutation, diagnostic):
    data = bundle()
    mutation(data)
    with pytest.raises(VEError, match=diagnostic):
        check_bundle(data)


@pytest.mark.parametrize("mutation, diagnostic", FORGERIES)
def test_lean_rejects_the_same_forged_citations(mutation, diagnostic):
    """Both checkers reject every forgery (PLAN-EXPAND2 W3 acceptance (3))."""
    from ve.bundle import lean_bundle_verdict
    if not LEAN.exists():
        pytest.skip("lean route runner is not built (lake build)")
    data = bundle()
    assert lean_bundle_verdict(LEAN, data["environment"], data["lemmas"])["status"] == "ok"
    mutation(data)
    verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"])
    assert verdict["status"] == "error", verdict
    if diagnostic != "certificate":
        assert diagnostic.split(",")[0] in verdict["error"] or "label" in verdict["error"], verdict


def test_lean_replays_bundles_in_one_run():
    if not LEAN.exists():
        pytest.skip("lean route runner is not built (lake build)")
    assert check_bundle(bundle(), lean_executable=LEAN)["lean_checked"] is True
    path = Path(__file__).resolve().parents[1] / "usecases/math-mini-paper/t7-definitions-bundle.json"
    assert check_bundle(json.loads(path.read_text()), lean_executable=LEAN)["lean_checked"] is True


def test_reading_choices_are_derived_from_label_and_version():
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    leaf = data["lemmas"][0]["premises"][0]
    leaf["label"] = "readings:u@0:0"
    data["lemmas"][0]["transitive_leaves"][0]["label"] = leaf["label"]
    data["lemmas"][1]["premises"][0]["label"] = leaf["label"]
    data["lemmas"][1]["transitive_leaves"][0]["label"] = leaf["label"]
    for lemma in data["lemmas"]:
        lemma["reading_choices"] = {"u": "0:0"}
    assert check_bundle(data)["status"] == "Checked"
    for forged in ({}, {"u": "1:0"}, {"u": "0:1"}):
        changed = deepcopy(data)
        changed["lemmas"][0]["reading_choices"] = forged
        with pytest.raises(VEError, match="reading"):
            check_bundle(changed)
        if LEAN.exists():
            verdict = lean_bundle_verdict(LEAN, changed["environment"], changed["lemmas"])
            assert verdict["status"] == "error" and "reading" in verdict["error"]
    conflict = deepcopy(data)
    conflict["lemmas"][1]["premises"][0]["label"] = "readings:u@0:1"
    conflict["lemmas"][1]["premises"].append(deepcopy(data["lemmas"][0]["premises"][0]))
    conflict["lemmas"][1]["transitive_leaves"] = [
        conflict["lemmas"][1]["premises"][0], data["lemmas"][0]["premises"][0]]
    with pytest.raises(VEError, match="incompatible"):
        check_bundle(conflict)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, conflict["environment"], conflict["lemmas"])
        assert verdict["status"] == "error" and "incompatible" in verdict["error"]
    compatible = deepcopy(data)
    compatible["lemmas"][0]["premises"][0]["label"] = "readings:u@0:all"
    compatible["lemmas"][0]["transitive_leaves"][0]["label"] = "readings:u@0:all"
    compatible["lemmas"][0]["reading_choices"] = {"u": "0:all"}
    compatible["lemmas"][1]["premises"].append(deepcopy(compatible["lemmas"][0]["premises"][0]))
    compatible["lemmas"][1]["transitive_leaves"].append(deepcopy(compatible["lemmas"][0]["premises"][0]))
    env = Environment(compatible["environment"])
    compatible["lemmas"][1]["certificate"] = prove_entailment(
        env, (Top(), Top(), Top()), And(Top(), Top())).certificate
    assert check_bundle(compatible)["status"] == "Checked"
    if LEAN.exists():
        assert lean_bundle_verdict(LEAN, compatible["environment"], compatible["lemmas"])["status"] == "ok"


def test_cited_hypothesis_must_be_on_branch_even_with_fresh_certificate():
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    second = data["lemmas"][1]
    second["premises"] = []
    env = Environment(data["environment"])
    second["certificate"] = prove_entailment(env, (Top(),), And(Top(), Top())).certificate
    with pytest.raises(VEError, match="hypothesis.*branch"):
        check_bundle(data)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"])
        assert verdict["status"] == "error" and "hypothesis" in verdict["error"]


def test_incompatible_readings_cannot_certify_false_with_empty_maps():
    """The former empty-choice-map exploit: opposite readings prove false."""
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    env = Environment(data["environment"])
    top, neg, bottom = Top(), Not(Top()), Bottom()
    first, second = data["lemmas"]
    first["premises"][0]["label"] = "readings:u@0:0"
    first["transitive_leaves"] = deepcopy(first["premises"])
    second.update(name="opposite", premises=[{"label": "readings:u@0:1",
        "ast": formula_to_data(env, neg)}], cites=[], conclusion=formula_to_data(env, neg),
        meaning_id=meaning_id(env, neg), reading_choices={},
        transitive_leaves=[{"label": "readings:u@0:1", "ast": formula_to_data(env, neg)}],
        certificate=prove_entailment(env, (neg,), neg).certificate)
    third = {"name": "false", "environment_id": env.environment_id,
             "premises": deepcopy(first["premises"] + second["premises"]),
             "cites": [first["meaning_id"], second["meaning_id"]],
             "conclusion": formula_to_data(env, bottom), "meaning_id": meaning_id(env, bottom),
             "reading_choices": {}, "transitive_leaves": deepcopy(first["premises"] + second["premises"]),
             "certificate": prove_entailment(env, (top, neg, top, neg), bottom).certificate}
    data["lemmas"].append(third)
    with pytest.raises(VEError, match="reading"):
        check_bundle(data)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"])
        assert verdict["status"] == "error" and "reading" in verdict["error"]


def test_math_bundle_preserves_background_and_rejects_version_tampering():
    path = Path(__file__).resolve().parents[1] / "usecases/math-mini-paper/t7-definitions-bundle.json"
    data = json.loads(path.read_text())
    assert [leaf["label"] for leaf in check_bundle(data)["lemmas"][-1]["transitive_leaves"]] == [
        "background:definitions", "open:transitivity"]
    forged = deepcopy(data)
    forged["lemmas"][-1]["transitive_leaves"] = forged["lemmas"][-1]["transitive_leaves"][1:]
    with pytest.raises(VEError, match="labels"):
        check_bundle(forged)
    forged = deepcopy(data)
    forged["lemmas"][-1]["environment_id"] = "0" * 64
    with pytest.raises(VEError, match="another environment"):
        check_bundle(forged)
