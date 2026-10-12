"""Citation replay and transitive provenance checks."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ve.ast import Top, Bottom, Not, And, Or, Const, Unary, formula_to_data
from ve.bundle import check_bundle
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.profiles import SPEC_REVISION


# Lean decides bundles since lean-first batch 13b: its one reading-binding text replaces Python's three
# (superseded set, unregistered set, unresolved citation); docs/lean-first/b13b/DELTA.md lists the change.
LEAN_BINDING = "^Reading label is not bound to its registered reading formula or citation is unresolved$"

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
    data["document"] = {"reading_sets": [{"id": "u", "version": 0,
        "readings": [formula_to_data(Environment(data["environment"]), Top()),
                     formula_to_data(Environment(data["environment"]), Not(Top()))]}]}
    assert check_bundle(data)["status"] == "Checked"
    for forged in ({}, {"u": "1:0"}, {"u": "0:1"}):
        changed = deepcopy(data)
        changed["lemmas"][0]["reading_choices"] = forged
        with pytest.raises(VEError, match="reading"):
            check_bundle(changed)
        if LEAN.exists():
            verdict = lean_bundle_verdict(LEAN, changed["environment"], changed["lemmas"], changed["document"])
            assert verdict["status"] == "error" and "reading" in verdict["error"]
    conflict = deepcopy(data)
    conflict["lemmas"][1]["premises"][0]["label"] = "readings:u@0:1"
    conflict["lemmas"][1]["premises"][0]["ast"] = formula_to_data(Environment(data["environment"]), Not(Top()))
    conflict["lemmas"][1]["premises"].append(deepcopy(data["lemmas"][0]["premises"][0]))
    conflict["lemmas"][1]["transitive_leaves"] = [
        conflict["lemmas"][1]["premises"][0], data["lemmas"][0]["premises"][0]]
    with pytest.raises(VEError, match="incompatible"):
        check_bundle(conflict)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, conflict["environment"], conflict["lemmas"], conflict["document"])
        assert verdict["status"] == "error" and "incompatible" in verdict["error"]
    compatible = deepcopy(data)
    compatible["document"]["reading_sets"][0]["readings"] = [formula_to_data(Environment(data["environment"]), Top())]
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
        assert lean_bundle_verdict(LEAN, compatible["environment"], compatible["lemmas"], compatible["document"])["status"] == "ok"


def test_superseded_reading_set_rejects_cited_dependants():
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    data["environment"]["vocabulary"] = {
        "sorts": {"thing": {"description": "A thing."}},
        "predicates": {"p": {"arguments": ["thing"], "description": "P."}},
        "constants": {"a": {"sort": "thing", "description": "A."}},
    }
    env = Environment(data["environment"])
    p = Unary("p", Const("a"))
    result = And(p, Top())
    leaf = {"label": "readings:u@0:all", "ast": formula_to_data(env, p)}
    first, second = data["lemmas"]
    first.update(environment_id=env.environment_id, premises=[deepcopy(leaf)],
                 conclusion=formula_to_data(env, p), meaning_id=meaning_id(env, p),
                 reading_choices={"u": "0:all"}, transitive_leaves=[deepcopy(leaf)],
                 certificate=prove_entailment(env, (p,), p).certificate)
    second.update(environment_id=env.environment_id, premises=[deepcopy(leaf)],
                  cites=[first["meaning_id"]], conclusion=formula_to_data(env, result),
                  meaning_id=meaning_id(env, result), reading_choices={"u": "0:all"},
                  transitive_leaves=[deepcopy(leaf)],
                  certificate=prove_entailment(env, (p, p), result).certificate)
    data["document"] = {"reading_sets": [
        {"id": "u", "version": 0, "readings": [formula_to_data(env, p)]}]}
    assert check_bundle(data)["status"] == "Checked"
    if LEAN.exists():
        assert lean_bundle_verdict(LEAN, data["environment"], data["lemmas"], data["document"])["status"] == "ok"

    data["document"]["reading_sets"].append(
        {"id": "u", "version": 1,
         "readings": [formula_to_data(env, p), formula_to_data(env, Not(p))]})
    with pytest.raises(VEError, match=LEAN_BINDING):
        check_bundle(data)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"], data["document"])
        assert verdict["status"] == "error" and "Reading label is not bound" in verdict["error"]


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
    data["document"] = {"reading_sets": [{"id": "u", "version": 0,
        "readings": [formula_to_data(env, top), formula_to_data(env, neg)]}]}
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
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"], data["document"])
        assert verdict["status"] == "error" and "reading" in verdict["error"]


@pytest.mark.parametrize("second_label", ["readings:u@0:0", "readings:u@0:all"])
def test_reading_label_cannot_name_opposite_formula_or_forged_all(second_label):
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    env = Environment(data["environment"])
    p, opposite = Top(), Not(Top())
    data["document"] = {"reading_sets": [{"id": "u", "version": 0,
        "readings": [formula_to_data(env, p), formula_to_data(env, opposite)]}]}
    first, second = data["lemmas"]
    first["premises"][0]["label"] = "readings:u@0:0"
    first["transitive_leaves"] = deepcopy(first["premises"])
    first["reading_choices"] = {"u": "0:0"}
    second.update(name="opposite", premises=[{"label": second_label,
        "ast": formula_to_data(env, opposite)}], cites=[], conclusion=formula_to_data(env, opposite),
        meaning_id=meaning_id(env, opposite),
        reading_choices={"u": "0:all" if second_label.endswith("all") else "0:0"},
        transitive_leaves=[{"label": second_label, "ast": formula_to_data(env, opposite)}],
        certificate=prove_entailment(env, (opposite,), opposite).certificate)
    false = Bottom()
    both = deepcopy(first["premises"] + second["premises"])
    data["lemmas"].append({"name": "false", "environment_id": env.environment_id,
        "premises": deepcopy(both), "cites": [first["meaning_id"], second["meaning_id"]],
        "conclusion": formula_to_data(env, false), "meaning_id": meaning_id(env, false),
        "reading_choices": {"u": "0:0"}, "transitive_leaves": deepcopy(both),
        "certificate": prove_entailment(env, (p, opposite, p, opposite), false).certificate})
    with pytest.raises(VEError, match="Reading label is not bound"):
        check_bundle(data)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"], data["document"])
        assert verdict["status"] == "error" and "Reading label is not bound" in verdict["error"]


def test_all_label_names_the_registered_disjunction_and_requires_document():
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    env = Environment(data["environment"])
    either = Or(Top(), Not(Top()))
    data["lemmas"] = data["lemmas"][:1]
    first = data["lemmas"][0]
    first["premises"] = [{"label": "readings:u@0:all", "ast": formula_to_data(env, either)}]
    first["transitive_leaves"] = deepcopy(first["premises"])
    first["reading_choices"] = {"u": "0:all"}
    first["certificate"] = prove_entailment(env, (either,), Top()).certificate
    data["document"] = {"reading_sets": [{"id": "u", "version": 0,
        "readings": [formula_to_data(env, Top()), formula_to_data(env, Not(Top()))]}]}
    assert check_bundle(data, lean_executable=LEAN if LEAN.exists() else None)["status"] == "Checked"
    del data["document"]
    with pytest.raises(VEError, match=LEAN_BINDING):
        check_bundle(data)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"])
        assert verdict["status"] == "error" and "Reading label is not bound" in verdict["error"]


def test_duplicate_reading_set_identity_cannot_rebind_a_label():
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    env = Environment(data["environment"])
    leaf = data["lemmas"][0]["premises"][0]
    leaf["label"] = "readings:u@0:0"
    data["lemmas"][0]["transitive_leaves"] = deepcopy(data["lemmas"][0]["premises"])
    data["lemmas"][0]["reading_choices"] = {"u": "0:0"}
    data["lemmas"] = data["lemmas"][:1]
    data["document"] = {"reading_sets": [
        {"id": "u", "version": 0, "readings": [formula_to_data(env, Top())]},
        {"id": "u", "version": 0, "readings": [formula_to_data(env, Not(Top()))]}]}
    with pytest.raises(VEError, match="duplicate reading set"):
        check_bundle(data)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"], data["document"])
        assert verdict["status"] == "error" and "duplicate reading set" in verdict["error"]


def test_unresolved_citation_labels_cannot_hide_opposite_leaves():
    from ve.bundle import lean_bundle_verdict
    data = bundle()
    env = Environment(data["environment"])
    p, opposite, false = Top(), Not(Top()), Bottom()
    first, second = data["lemmas"]
    second.update(name="B", premises=[{"label": "open:B", "ast": formula_to_data(env, opposite)}],
        cites=[], conclusion=formula_to_data(env, opposite), meaning_id=meaning_id(env, opposite),
        reading_choices={}, transitive_leaves=[{"label": "open:B", "ast": formula_to_data(env, opposite)}],
        certificate=prove_entailment(env, (opposite,), opposite).certificate)
    third_leaves = [{"label": "cite:local/A", "ast": formula_to_data(env, p)},
                    {"label": "cite:local/B", "ast": formula_to_data(env, opposite)}]
    data["lemmas"].append({"name": "false", "environment_id": env.environment_id,
        "premises": deepcopy(third_leaves), "cites": [], "conclusion": formula_to_data(env, false),
        "meaning_id": meaning_id(env, false), "reading_choices": {},
        "transitive_leaves": deepcopy(third_leaves),
        "certificate": prove_entailment(env, (p, opposite), false).certificate})
    with pytest.raises(VEError, match=LEAN_BINDING):
        check_bundle(data)
    if LEAN.exists():
        verdict = lean_bundle_verdict(LEAN, data["environment"], data["lemmas"])
        assert verdict["status"] == "error" and "citation is unresolved" in verdict["error"]


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
