import copy

import pytest

from ve.ast import (And, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Not, Or, Top, Unary, Var)
from ve.entailment import (ENTAILMENT_CHECKER_VERSION,
                           check_entailment_certificate, prove_entailment)
from ve.environment import Environment


def environment(*, constants=True):
    return Environment.from_dict({
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"person": {"description": "A person."},
                      "place": {"description": "A place."}},
            "predicates": {
                "kind": {"arguments": ["person"], "description": "Is kind."},
                "visits": {"arguments": ["person", "place"], "description": "Visits."},
            },
            "constants": ({"ada": {"sort": "person", "description": "Ada."},
                           "bea": {"sort": "person", "description": "Bea."}}
                          if constants else {}),
        },
    })


def certify(env, premises, conclusion):
    result = prove_entailment(env, premises, conclusion)
    assert result.status == "Found", result.to_dict()
    assert result.certificate["checker_version"] == ENTAILMENT_CHECKER_VERSION
    checked = check_entailment_certificate(env, premises, conclusion, result.certificate)
    assert checked.valid and checked.status == "Valid"
    return result.certificate


def test_propositional_and_quantified_entailments_certify():
    env = environment()
    universal = Forall("person", Implies(Unary("kind", Var(0)),
                                         Eq(Var(0), Const("ada"))))
    certify(env, [universal, Unary("kind", Const("bea"))],
            Eq(Const("bea"), Const("ada")))
    certify(env, [Or(Unary("kind", Const("ada")), Unary("kind", Const("bea"))),
                  Not(Unary("kind", Const("ada")))], Unary("kind", Const("bea")))


def test_equality_substitution_and_aliasing_are_checked():
    env = environment()
    certify(env, [Eq(Const("ada"), Const("bea")), Unary("kind", Const("ada"))],
            Unary("kind", Const("bea")))
    # Unique names are not assumed; reflexivity is nevertheless logical equality.
    certify(env, [], Eq(Const("ada"), Const("ada")))
    assert prove_entailment(env, [], Not(Eq(Const("ada"), Const("bea")))).status == "NotFound"


def test_many_sorts_and_quantifier_alternation():
    env = environment()
    premise = Forall("person", Exists("place", Binary("visits", Var(1), Var(0))))
    conclusion = Exists("place", Binary("visits", Const("ada"), Var(0)))
    certify(env, [premise], conclusion)
    # Reordering the relation arguments is rejected by the AST type checker, not hidden in a proof.
    with pytest.raises(Exception):
        prove_entailment(env, [premise], Exists("place", Binary("visits", Var(0), Const("ada"))))


def test_empty_sorts_have_vacuous_quantifier_semantics():
    env = environment(constants=False)
    assert prove_entailment(env, [], Forall("person", Unary("kind", Var(0)))).status == "NotFound"
    certify(env, [], Not(Exists("person", Bottom())))
    # Excluded middle remains valid even though the sort can be empty.
    exists = Exists("person", Unary("kind", Var(0)))
    certify(env, [], Or(exists, Not(exists)))


def test_not_found_and_resource_limit_are_distinct_from_found():
    env = environment()
    assert prove_entailment(env, [], Unary("kind", Const("ada"))).status == "NotFound"
    limited = prove_entailment(env, [Top()], Top(), max_steps=0)
    assert limited.status == "ResourceLimit" and limited.certificate is None


def test_certificate_is_bound_to_exact_order_environment_and_conclusion():
    env = environment()
    p = Unary("kind", Const("ada"))
    certificate = certify(env, [Top(), p], p)
    assert not check_entailment_certificate(env, [p, Top()], p, certificate).valid
    assert not check_entailment_certificate(env, [Top(), p], Top(), certificate).valid
    changed = environment(constants=False)
    # A stale environment binding is rejected even when the trace shape is plausible.
    assert not check_entailment_certificate(changed, [], Top(), certificate).valid


@pytest.mark.parametrize("mutation", [
    lambda c: c.update(checker_version="future"),
    lambda c: c.update(extra=True),
    lambda c: c.update(trace={"rule": "close"}),
    lambda c: c.update(trace={"rule": "expand", "at": True, "children": []}),
    lambda c: c.update(trace={"rule": "expand", "at": 999, "children": []}),
    lambda c: c.update(trace={"rule": "execute", "code": "raise SystemExit"}),
])
def test_malformed_and_fabricated_certificates_never_certify_or_crash(mutation):
    env = environment()
    p = Unary("kind", Const("ada"))
    certificate = certify(env, [And(p, Top())], p)
    forged = copy.deepcopy(certificate)
    mutation(forged)
    checked = check_entailment_certificate(env, [And(p, Top())], p, forged)
    assert not checked.valid and checked.status == "InvalidCertificate"


def test_replay_budget_is_explicit():
    env = environment()
    p = Unary("kind", Const("ada"))
    certificate = certify(env, [p], p)
    checked = check_entailment_certificate(env, [p], p, certificate, max_steps=0)
    assert not checked.valid and checked.status == "ResourceLimit"


def test_deep_tableau_roundtrips_within_json_envelope():
    from ve.argument_fixtures import merged_vocabulary_example
    from ve.ast import Top, Bottom, Not
    from ve.limits import MAX_TABLEAU_DEPTH
    from ve.wire import canonical_json, loads_json

    env = merged_vocabulary_example().env
    # Shallow independent ASTs require a long linear tableau before the final
    # negated tautology closes. This used to exceed the JSON nesting limit.
    premises = (Not(Bottom()),) * 120 + (Not(Top()),)
    result = prove_entailment(env, premises, Bottom())
    assert result.status == 'Found' and result.steps > 100
    replay = loads_json(canonical_json(result.certificate))
    assert check_entailment_certificate(env, premises, Bottom(), replay).valid
    # Oversized traces must stop during search rather than emit unreplayable data.
    too_deep = (Not(Bottom()),) * (MAX_TABLEAU_DEPTH + 5) + (Not(Top()),)
    result = prove_entailment(env, too_deep, Bottom())
    assert result.status == 'ResourceLimit' and result.certificate is None
    assert 'nesting' in result.detail
