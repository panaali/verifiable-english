"""Citation replay and transitive provenance checks."""
from copy import deepcopy

import pytest

from ve.ast import Top, And, formula_to_data
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
             "reading_choices": {"u": "r1"},
             "transitive_leaves": [{"label": "open:assumption", "ast": formula_to_data(env, top)}],
             "certificate": prove_entailment(env, (top,), top).certificate}
    second = {"name": "second", "environment_id": env.environment_id,
              "premises": deepcopy(first["premises"]), "cites": [first["meaning_id"]],
              "conclusion": formula_to_data(env, both), "meaning_id": meaning_id(env, both),
              "reading_choices": {"u": "r1"},
              "transitive_leaves": deepcopy(first["transitive_leaves"]),
              "certificate": prove_entailment(env, (top, top), both).certificate}
    return {"version": "ve-bundle@0", "environment": env.to_dict(), "lemmas": [first, second]}


def test_checked_citation_and_labels():
    report = check_bundle(bundle())
    assert report["status"] == "Checked"
    assert report["lemmas"][1]["transitive_leaves"] == report["lemmas"][0]["transitive_leaves"]


@pytest.mark.parametrize("mutation, diagnostic", [
    (lambda b: b["lemmas"][1]["cites"].__setitem__(0, "absent"), "absent"),
    (lambda b: b["lemmas"][1]["transitive_leaves"].clear(), "labels"),
    (lambda b: b["lemmas"][1]["reading_choices"].__setitem__("u", "r2"), "reading"),
    (lambda b: b["lemmas"][1]["premises"].clear(), "certificate"),
])
def test_reject_forged_citation(mutation, diagnostic):
    data = bundle()
    mutation(data)
    with pytest.raises(VEError, match=diagnostic):
        check_bundle(data)
