import pytest

from ve.ast import And, Binary, Bottom, Const, Forall, Not, Top, check_formula
from ve.background import background
from ve.environment import Environment
from ve.errors import InvalidModel, UnknownSymbol, UnsupportedProfile, VEError
from ve.evaluate import evaluate
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.model import FiniteModel
from ve.search import find_countermodel


def environment(*, functional=True, total=True):
    return Environment({"language": "ve.core@0.2",
        "profiles": ["data@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"person": {"description": "Person"}},
            "predicates": {"department": {"arguments": ["person", "$string"],
                "description": "Department of a person", "functional": functional, "total": total}},
            "constants": {"alice": {"sort": "person", "description": "Alice"},
                "finance": {"sort": "$string"}, "sales": {"sort": "$string"}}}})


def model(env, rows):
    return FiniteModel.from_dict(env, {"complete": True,
        "domains": {"person": ["a"], "$string": ["f", "s"]},
        "constants": {"alice": "a", "finance": "f", "sales": "s"},
        "relations": {"department": rows}})


def test_flags_generate_premises_and_reject_invalid_tables():
    env = environment()
    assert env.to_dict()["vocabulary"]["predicates"]["department"]["total"] is True
    assert [p.generator for p in background(env)] == ["flags", "flags", "literals"]
    assert evaluate(env, Binary("department", Const("alice"), Const("finance")),
                    model(env, [["a", "f"]])).value is True
    for rows in ([], [["a", "f"], ["a", "s"]]):
        with pytest.raises(InvalidModel) as exc:
            model(env, rows)
        assert exc.value.generator == "flags"


def test_flags_are_identity_bound_and_restricted_to_data_profile():
    assert environment(functional=False).environment_id != environment().environment_id
    assert environment(total=False).environment_id != environment().environment_id
    data = environment().to_dict()
    data["profiles"] = ["relational-fol@0"]
    with pytest.raises(UnsupportedProfile, match="data@0"):
        Environment(data)
    data = environment().to_dict()
    data["vocabulary"]["predicates"]["department"]["total"] = 1
    with pytest.raises(VEError, match="Boolean"):
        Environment(data)
    with pytest.raises(UnknownSymbol):
        check_formula(environment(), Binary("department", Const("alice"), Const("undeclared")))


def test_flag_background_is_bound_into_proof_and_search():
    env = environment()
    both = And(Binary("department", Const("alice"), Const("finance")),
               Binary("department", Const("alice"), Const("sales")))
    conclusion = Not(both)
    proof = prove_entailment(env, (), conclusion)
    assert proof.status == "Found"
    assert check_entailment_certificate(env, (), conclusion, proof.certificate).valid
    witness = find_countermodel(env, (), Bottom(),
                                max_domain_size=2, max_models=40)
    assert witness.status == "Found" and witness.model.relations["department"]
    with pytest.raises(UnsupportedProfile, match="stage 2"):
        check_formula(env, Forall("$string", Top()))
