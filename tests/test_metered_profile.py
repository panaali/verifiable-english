"""The `metered` mode checks the norms profile of its model itself (kb-validators part 1, decision D13).

A model whose required relation holds a tuple its permission does not is refused by `metered` with the
`model` mode's own diagnostic (`InvalidModel(profile): …`, `VE.Norms.Plain.profileOkOn`), on every checker
family and both case kinds, also when it is sent straight to `metered` without the `model` mode. An
admissible model is answered as before, and an environment without a norm pair is not checked. What the
check guarantees is stated by `VE.Route.MeteredRun.runWith_sound` (`ProfileAdmits`)."""
import pytest

from ve.backends import relay
from ve.backends.lean_runner import metered_evaluation
from ve.errors import CheckerUnavailable
from ve.evaluate import read_evaluation
from ve.profiles import SPEC_REVISION

FAMILIES = {
    "fol": ["norms@0", "relational-fol@0"],
    "closure": ["closure@0", "norms@0", "relational-fol@0"],
    "nary": ["closure@0", "nary@0", "norms@0", "relational-fol@0"],
    "order": ["norms@0", "order@0", "relational-fol@0"],
}
KINDS = ("evaluate-budgeted", "non-vacuity")
DIAGNOSTIC = "InvalidModel(profile): required relation required exceeds permission permitted"
FORMULA = ["forall", "point", ["unary", "upper", ["var", 0]]]


def _environment(profiles, regulated=True):
    def declared(description):
        return {"arguments": ["point"], "description": description}
    predicates = {"upper": declared("upper"), "permitted": declared("permission"),
                  "required": declared("obligation")}
    if regulated:
        predicates["permitted"]["regulated"] = {"role": "permission", "default": "deny", "act": "{0} be done"}
        predicates["required"]["regulated"] = {"role": "obligation", "default": "deny", "act": "{0} be done",
                                               "permission": "permitted"}
    return {"language": "ve.core@0.2", "profiles": sorted(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {"point": {"description": "point"}}, "constants": {},
                           "predicates": predicates}}


def _model(required, permitted):
    return {"complete": True, "domains": {"point": ["a", "b"]}, "constants": {},
            "relations": {"upper": [["a"]], "required": [[x] for x in required],
                          "permitted": [[x] for x in permitted]}}


def _case(profiles, model, kind="evaluate-budgeted", regulated=True, case_id="e"):
    return {"id": case_id, "kind": kind, "environment": _environment(profiles, regulated), "model": model,
            "ast": [FORMULA], "formula": FORMULA, "max_evaluations": 1000}


# Required relations beyond their permission: one tuple of two, the only tuple, every tuple.
BEYOND = [(["a"], []), (["a", "b"], ["a"]), (["b"], ["a"])]
# Within: a proper part, equal, both empty, required empty.
WITHIN = [(["a"], ["a", "b"]), (["a", "b"], ["a", "b"]), ([], []), ([], ["b"])]


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("required,permitted", BEYOND)
def test_a_model_beyond_its_permission_is_refused_by_metered_with_the_model_modes_diagnostic(
        family, kind, required, permitted):
    model = _model(required, permitted)
    [row] = relay.rows("metered", [_case(FAMILIES[family], model, kind)])
    assert row == {"id": "e", "status": "error", "error": DIAGNOSTIC}
    # The `model` mode refuses it with the same text: one check, two callers.
    [checked] = relay.rows("model", [{"id": "model", "environment": _environment(FAMILIES[family]),
                                      "model": model}])
    assert checked == {"id": "model", "status": "error", "error": DIAGNOSTIC}


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("required,permitted", WITHIN)
def test_a_model_within_its_permission_is_still_answered(family, kind, required, permitted):
    model = _model(required, permitted)
    [row] = relay.rows("metered", [_case(FAMILIES[family], model, kind)])
    assert row["status"] == "ok", row
    if kind == "evaluate-budgeted":
        # `upper` holds of `a` only: the formula is false in the model.
        assert row["evaluation"]["value"] is False
    else:
        assert row["suitable"] is True
    [checked] = relay.rows("model", [{"id": "model", "environment": _environment(FAMILIES[family]),
                                      "model": model}])
    assert checked["status"] == "ok" and checked["valid"] is True


@pytest.mark.parametrize("family", FAMILIES)
def test_without_a_norm_pair_the_same_relations_are_answered(family):
    # The same tables with no `regulated` declaration: no pair, nothing to check.
    [row] = relay.rows("metered", [_case(FAMILIES[family], _model(["a"], []), regulated=False)])
    assert row["status"] == "ok", row
    assert row["evaluation"]["value"] is False


def test_the_handle_path_checks_the_profile_as_the_first_case_does():
    # The second case names the environment the first registered (`environment_handle`): the kept
    # `Prepared` carries the profile, and a handle never changes an answer.
    profiles = FAMILIES["fol"]
    cases = [_case(profiles, _model(["a"], ["a"]), case_id="first"),
             _case(profiles, _model(["a"], []), case_id="second"),
             _case(profiles, _model(["b"], ["b"]), case_id="third")]
    rows = relay.rows("metered", cases)
    assert [row["status"] for row in rows] == ["ok", "error", "ok"]
    assert rows[1] == {"id": "second", "status": "error", "error": DIAGNOSTIC}


def test_a_profile_refusal_reaches_python_as_checker_unavailable_never_as_an_answer():
    case = _case(FAMILIES["fol"], _model(["a"], []))
    with pytest.raises(CheckerUnavailable, match=r"InvalidModel\(profile\)"):
        read_evaluation(metered_evaluation(case), case)


def test_every_public_entry_refuses_the_same_model_before_metered_as_on_main():
    # DELTA row 1 (R7): through the Python API the record is unavailable with the same text on main and
    # here. The validated path asks the `model` mode (`FiniteModel.from_dict`), which refuses it.
    from ve import Environment, FiniteModel
    from ve.errors import InvalidModel
    env = Environment(_environment(FAMILIES["fol"]))
    with pytest.raises(InvalidModel, match=r"^InvalidModel\(profile\): required relation required exceeds "
                                           r"permission permitted$"):
        FiniteModel.from_dict(env, _model(["a"], []))
    # Its opposite: the admissible model is built.
    assert FiniteModel.from_dict(env, _model(["a"], ["a"])).model_id


def test_the_soft_path_refuses_the_same_model_in_python_before_metered():
    # A soft environment's model is not sent to the `model` mode (ve/model.py); Python's own decoder
    # refuses the profile violation there, so no public entry sends it to `metered` either.
    from tests.test_soft_selected import document
    from ve import FiniteModel
    from ve.errors import InvalidModel
    extended = document("deny").extended_env
    assert extended.soft_premises
    predicates = extended.to_dict()["vocabulary"]["predicates"]
    relations = {name: [] for name in predicates if name not in extended.definition_entries}

    def model(permitted):
        return {"complete": True, "constants": {},
                "domains": {sort: ["a"] if sort == "assistant" else [] for sort in extended.model_sorts},
                "relations": {**relations, "x_required": [["a"]], "x_permitted": permitted}}
    with pytest.raises(InvalidModel, match="required relation x_required exceeds permission x_permitted"):
        FiniteModel.from_dict(extended, model([]))
    assert FiniteModel.from_dict(extended, model([["a"]])).model_id
