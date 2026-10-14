"""Norms operations on the Lean authority: elaboration, certificates, conflicts, admission.

Each public entry point dispatches its own adapter on FOL-family norm documents,
with `data@0` flags and definitions (`lean/VE/Norms/Flagged.lean`), and on
norm documents over the closure, core and order families
(`lean/VE/Service/FamilyNorms.lean`).
"""
from __future__ import annotations

from pathlib import Path
from copy import deepcopy
from itertools import product

import pytest

from ve.ast import (And, Atom, Binary, Body, Const, Exists, Forall, Implies, Le, Named, Not, Num, Reach,
                    Top, Unary, Var, _to_data)
from ve.backends import dispatch, relay
from ve.backends.lean_service import CheckerUnavailable
from ve.background import background
from ve.environment import Environment
from ve.errors import InvalidModel, VEError
from ve.model import FiniteModel
from ve.norms import (NormDocument, check_conflict, check_norm_entailment_certificate,
                      prove_norm_entailment)
from ve.profiles import LANGUAGE, SPEC_REVISION
from tests.test_norms import obligation, permission, rule

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def flagged(*, total=False, definitions=False, family=(), data=True, relation=False):
    """Norms over a FOL environment (or a `family` one) with a flagged table
    (unless `data` is false) and, optionally, a definition and a homogeneous
    binary relation."""
    predicates = {
        "required": obligation(),
        "permitted": permission(),
        "owner": {"arguments": ["act", "party"], "description": "owner",
                  **({"functional": True, **({"total": True} if total else {})} if data else {})},
        "urgent": {"arguments": ["act"], "description": "urgent"},
        **({"before": {"arguments": ["act", "act"], "description": "before"}} if relation else {}),
    }
    profiles = {"norms@0", "relational-fol@0", *family, *(("data@0",) if data else ())}
    if definitions:
        profiles.add("definitions@0")
        predicates["pressing"] = {"arguments": ["act"], "description": "pressing",
                                  "defined": {"arguments": ["act"], "body": ["unary", "urgent", ["var", 0]]}}
    return Environment({"language": LANGUAGE, "profiles": sorted(profiles), "spec_revision": SPEC_REVISION,
                        "vocabulary": {"sorts": {"act": {"description": "act"}, "party": {"description": "party"}},
                                       "predicates": predicates, "constants": {}}})


def document(env):
    guard = Unary("pressing" if "pressing" in env.predicates else "urgent", Var(0))
    return NormDocument(env, [rule("must", "required", True, guard),
                              rule("may", "permitted", True, guard)])


def routed(monkeypatch, authority):
    ops = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, auth: ops.append((op, auth))])
    monkeypatch.setenv("VE_AUTHORITY", authority)
    return ops


def outcomes(doc):
    layers = doc.premises()
    proof = prove_norm_entailment(doc, (), Top(), max_steps=200)
    return {"elaborate": [(label, _to_data(f)) for label, f in layers],
            "certificate": check_norm_entailment_certificate(doc, (), Top(), proof.certificate),
            "stale": check_norm_entailment_certificate(doc, (Top(),), Top(), proof.certificate),
            "schema": check_norm_entailment_certificate(doc, (), Top(), {}),
            "conflict": check_conflict(doc, prove=True, tableau_steps=500),
            "missing": check_conflict(doc, certificates={}),
            "no evidence": check_conflict(doc)}


@pytest.mark.parametrize("total", [False, True])
@pytest.mark.parametrize("definitions", [False, True])
def test_norms_operations_with_flags_and_definitions_match_python(monkeypatch, total, definitions):
    env = flagged(total=total, definitions=definitions)
    routed(monkeypatch, "python")
    expected = outcomes(document(env))
    assert expected["certificate"].valid and expected["conflict"].status == "CONFLICT-FREE"
    ops = routed(monkeypatch, "lean")
    assert outcomes(document(env)) == expected
    assert {"norms_elaborate", "norms_certificate", "norms_conflict"} <= {op for op, _ in ops}


def test_lean_norms_background_puts_flag_premises_first():
    from ve.backends.relay import decide as run
    env = flagged(total=True, definitions=True)
    doc = document(env)
    row = run("norms", [{"id": "e", "kind": "norms-elaborate", "environment": env.to_dict(),
                         "norms": [r.to_dict() for r in doc.rules]}])[0]
    python = [(p.generator, _to_data(p.formula)) for p in background(env)]
    assert [(b["generator"], b["ast"]) for b in row["background"]] == python
    assert [g for g, _ in python][:2] == ["flags", "flags"]
    # A total flag is a ∀∃ premise the small-model restriction does not keep.
    assert row["fragment"] is False
    functional = flagged(definitions=True)
    row = run("norms", [{"id": "e", "kind": "norms-elaborate", "environment": functional.to_dict(),
                         "norms": [r.to_dict() for r in document(functional).rules]}])[0]
    assert row["fragment"] is True


def witness_model(doc, owner):
    env = doc.base_environment()
    return FiniteModel.from_dict(env, {"complete": True, "domains": {"act": ["a"], "party": ["p", "q"]},
                                       "constants": {},
                                       "relations": {"owner": owner, "urgent": [["a"]]}})


def test_conflict_witness_over_flags_is_lean_checked(monkeypatch):
    env = flagged()
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [["a", "p"]])
    routed(monkeypatch, "python")
    expected = check_conflict(doc, model=model)
    assert expected.status == "CONFLICT" and expected.target == "required->permitted"
    ops = routed(monkeypatch, "lean")
    assert check_conflict(doc, model=model) == expected
    assert ("norms_conflict", "lean") in ops


def test_lean_rejects_a_witness_model_that_violates_a_flag():
    from ve.backends.relay import decide as run
    env = flagged()
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [])
    wire = {**model.to_dict(), "relations": {**model.to_dict()["relations"], "owner": [["a", "p"], ["a", "q"]]}}
    case = {"id": "w", "kind": "norms-conflict", "environment": env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules],
            "witness": {"target": "required->permitted", "model": wire, "tuple": ["a"]}}
    with pytest.raises(InvalidModel) as caught:
        run("norms", [case])
    assert caught.value.generator == "flags"


def test_a_witness_lean_refuses_is_checker_unavailable(monkeypatch):
    from ve.backends import relay
    env = flagged()
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [["a", "p"]])
    real = relay.decide

    def refuse(mode, cases, **kw):
        rows = real(mode, cases, **kw)
        return [{**row, "verdict": "UNKNOWN"} if "witness" in case else row
                for case, row in zip(cases, rows)]

    monkeypatch.setattr(relay, "decide", refuse)
    routed(monkeypatch, "lean")
    with pytest.raises(CheckerUnavailable, match="does not confirm"):
        check_conflict(doc, model=model)


FAMILIES = [(("closure@0",), False), (("closure@0",), True), (("closure@0", "nary@0"), False),
            (("closure@0", "nary@0"), True), (("order@0",), False)]


@pytest.mark.parametrize("family,definitions", FAMILIES)
def test_norms_on_the_closure_core_and_order_families_are_leans(monkeypatch, family, definitions):
    """First-order norm documents over the other families: Lean regenerates the
    layers over the FOL view and checks the family's certificates."""
    from ve.backends import relay
    env = flagged(definitions=definitions, family=family, data="order@0" not in family)
    routed(monkeypatch, "python")
    expected = outcomes(document(env))
    assert expected["certificate"].valid and expected["conflict"].status == "CONFLICT-FREE"
    ops = routed(monkeypatch, "lean")
    modes = []
    real = relay.decide

    def spy(mode, cases, **kw):
        modes.append(mode)
        return real(mode, cases, **kw)

    monkeypatch.setattr(relay, "decide", spy)
    assert outcomes(document(env)) == expected
    assert {"norms_elaborate", "norms_certificate", "norms_conflict"} <= {op for op, _ in ops}
    assert "family-norms" in modes


def test_a_family_certificate_bound_to_other_premises_is_invalid_in_lean():
    from ve.backends.relay import decide as run
    env = flagged(family=("closure@0",))
    doc = document(env)
    proof = prove_norm_entailment(doc, (), Top(), max_steps=200)
    case = {"id": "c", "kind": "norms-certificate", "environment": env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules], "premises": [], "conclusion": ["top"],
            "certificate": proof.certificate}
    assert run("family-norms", [case])[0]["valid"] is True
    with pytest.raises(VEError, match="stale"):
        run("family-norms", [{**case, "premises": [["top"]]}])


def test_family_conflict_witness_is_lean_checked(monkeypatch):
    env = flagged(family=("closure@0",))
    doc = NormDocument(env, [rule("must", "required", True, Unary("urgent", Var(0)))])
    model = witness_model(doc, [["a", "p"]])
    routed(monkeypatch, "python")
    expected = check_conflict(doc, model=model)
    assert expected.status == "CONFLICT"
    ops = routed(monkeypatch, "lean")
    assert check_conflict(doc, model=model) == expected
    assert ("norms_conflict", "lean") in ops


@pytest.mark.parametrize("family,guard", [
    (("closure@0",), lambda: Reach("star", Named("before"), Var(0), Var(0))),
    (("closure@0", "nary@0"), lambda: Exists("party", Atom("tri", (Var(1), Var(1), Var(0))))),
    (("order@0",), lambda: Le(Num(1), Num(2))),
])
def test_non_first_order_norms_are_dispatched_and_match_python(monkeypatch, family, guard):
    env = flagged(family=family, relation="order@0" not in family,
                  data="order@0" not in family)
    if "nary@0" in family:
        raw = env.to_dict()
        raw["vocabulary"]["predicates"]["tri"] = {
            "arguments": ["act", "act", "party"], "description": "tri"}
        env = Environment(raw)
    doc = NormDocument(env, [rule("may", "permitted", True, guard())])
    expected_layers = [(label, _to_data(f)) for label, f in doc._premises_python()]
    ops = routed(monkeypatch, "lean")
    actual = outcomes(doc)
    assert actual["elaborate"] == expected_layers
    assert actual["certificate"].valid
    assert {"norms_elaborate", "norms_certificate", "norms_conflict"} <= {op for op, _ in ops}


@pytest.mark.parametrize("field", ["order", "label", "target", "sorts"])
def test_non_first_order_elaboration_refuses_unbound_rows(monkeypatch, field):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    real = relay.decide

    def corrupt(mode, cases, **kwargs):
        row = deepcopy(real(mode, cases, **kwargs)[0])
        if cases[0]["kind"] == "norms-elaborate":
            if field == "order":
                row["order"] = []
            elif field == "label":
                row["premises"][0]["label"] = "layer:norms:absent"
            elif field == "target":
                row["conflict_targets"][0]["target"] = "absent"
            else:
                row["conflict_targets"][0]["sorts"] = ["party"]
        return [row]

    monkeypatch.setattr(relay, "decide", corrupt)
    with pytest.raises(CheckerUnavailable, match="bound to the request"):
        doc.premises()


def test_non_first_order_conflict_refuses_extra_target(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    real = relay.decide

    def corrupt(mode, cases, **kwargs):
        row = deepcopy(real(mode, cases, **kwargs)[0])
        if mode == "family-norms" and cases[0].get("kind") == "norms-conflict":
            row["targets"].append("absent")
        return [row]

    monkeypatch.setattr(relay, "decide", corrupt)
    with pytest.raises(CheckerUnavailable, match="bound to the request"):
        check_conflict(doc, certificates={})


def test_non_first_order_certificate_refuses_unbound_layer_count(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    proof = prove_norm_entailment(doc, (), Top(), max_steps=200)
    real = relay.decide

    def corrupt(mode, cases, **kwargs):
        row = deepcopy(real(mode, cases, **kwargs)[0])
        if mode == "family-norms" and cases[0].get("kind") == "norms-certificate":
            row["layers"] += 1
        return [row]

    monkeypatch.setattr(relay, "decide", corrupt)
    with pytest.raises(CheckerUnavailable, match="bound to the request"):
        check_norm_entailment_certificate(doc, (), Top(), proof.certificate)


def test_non_first_order_certificate_propagates_checker_unavailable(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])

    def unavailable(*_args, **_kwargs):
        raise CheckerUnavailable("CheckerUnavailable: service stopped")

    monkeypatch.setattr(relay, "decide", unavailable)
    with pytest.raises(CheckerUnavailable, match="service stopped"):
        check_norm_entailment_certificate(doc, (), Top(), {})


def test_non_first_order_conflict_witness_is_checked_by_lean(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("must", "required", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    model = {"complete": True, "domains": {"act": ["a"], "party": ["p"]},
             "constants": {}, "relations": {"owner": [["a", "p"]], "urgent": [], "before": []}}
    ops = routed(monkeypatch, "lean")
    report = check_conflict(doc, model=model)
    assert report.status == "CONFLICT" and report.target == "required->permitted"
    assert ("norms_conflict", "lean") in ops


def nary_lower_outcome(*, unused_nary_definition):
    """A core-family document whose lower regulated outcome holds an n-ary atom
    under a binder (corpus document 13's shape). An unused n-ary core definition
    keeps it on the retained Python route (`family_in_scope`, batch 14c)."""
    raw = flagged(family=("closure@0", "nary@0"), relation=True).to_dict()
    raw["vocabulary"]["predicates"]["tri"] = {
        "arguments": ["act", "act", "party"], "description": "tri"}
    if unused_nary_definition:
        raw["profiles"] = sorted(set(raw["profiles"]) | {"definitions@0"})
        raw["vocabulary"]["predicates"]["tri_defined"] = {
            "arguments": ["act", "act", "party"], "description": "tri_defined",
            "defined": {"arguments": ["act", "act", "party"], "body": ["top"]}}
    doc = NormDocument(Environment(raw), [
        rule("may", "permitted", True, Exists("party", Atom("tri", (Var(1), Var(1), Var(0))))),
        rule("must", "required", True, Forall("party", Implies(Binary("owner", Var(1), Var(0)),
                                                               Not(Unary("permitted", Var(1))))))])
    model = {"complete": True, "domains": {"act": ["a"], "party": ["p"]}, "constants": {},
             "relations": {"owner": [["a", "p"]], "urgent": [], "before": [], "tri": []}}
    return doc, model


def answer(run):
    """An operation's answer or its raised diagnostic, for route comparisons."""
    try:
        return ("ok", run())
    except VEError as error:
        return ("error", type(error).__name__, str(error))


def conflict_answers(doc, model):
    from ve.norms import check_witness
    return {"model": answer(lambda: check_conflict(doc, model=model)),
            "prove": answer(lambda: check_conflict(doc, prove=True, tableau_steps=300)),
            "missing": answer(lambda: check_conflict(doc, certificates={})),
            "witness": answer(lambda: check_witness(doc, "required->permitted", model, ["a"]))}


ROUTE_CASES = (
    ("closure-urgent", ("closure@0",), Unary("urgent", Var(0))),
    ("closure-reach", ("closure@0",), Reach("star", Named("before"), Var(0), Var(0))),
    ("core-reach", ("closure@0", "nary@0"), Reach("star", Named("before"), Var(0), Var(0))),
    ("order-urgent", ("order@0",), Unary("urgent", Var(0))),
    ("order-le", ("order@0",), Le(Num(1), Num(2))),
)
ROUTE_NAMES = tuple(sorted((name for name, _, _ in ROUTE_CASES))) + ("nary-lower-outcome",)


def route_documents():
    """Family documents with a conflict target on the Lean family route, first
    order or not, including corpus document 13's n-ary lower outcome."""
    model = {"complete": True, "domains": {"act": ["a"], "party": ["p"]}, "constants": {},
             "relations": {"owner": [["a", "p"]], "urgent": [["a"]], "before": [["a", "a"]]}}
    docs = {}
    for name, family, guard in ROUTE_CASES:
        env = flagged(family=family, relation="order@0" not in family, data="order@0" not in family)
        relations = {k: v for k, v in model["relations"].items() if k in env.predicates}
        docs[name] = (NormDocument(env, [rule("must", "required", True, guard)]),
                      {**model, "relations": relations})
    nary, nary_model = nary_lower_outcome(unused_nary_definition=False)
    docs["nary-lower-outcome"] = (nary, nary_model)
    assert set(docs) == set(ROUTE_NAMES)
    return docs


@pytest.mark.parametrize("name", sorted(ROUTE_NAMES))
def test_lean_family_route_answers_as_the_retained_python_route(monkeypatch, name):
    """lf-14b review F2/F3, the class: a batch-14b change to a shared Python
    helper must not change an answer on either route. Every conflict operation
    answers on the Lean family route exactly as the retained Python route (the
    base's) answers, including the base's `TypeMismatch` for an unsubstituted
    n-ary lower outcome, until batch 14c signs that change."""
    import ve.norms
    doc, model = route_documents()[name]
    assert ve.norms._lean_route(doc)
    ops = routed(monkeypatch, "lean")
    lean = conflict_answers(doc, model)
    assert ("norms_conflict", "lean") in ops
    monkeypatch.setattr(ve.norms, "_lean_route", lambda document: False)
    assert conflict_answers(doc, model) == lean


def test_retained_python_route_keeps_the_base_nary_expansion(monkeypatch):
    """lf-14b review F2/F3: the n-ary lower outcome answers as the base did
    (`TypeMismatch` from the unsubstituted atom) on the retained route and on
    the Lean family route alike."""
    from ve.norms import _lean_route, check_witness
    mismatch = "TypeMismatch: Predicate 'tri'"
    for unused_nary_definition in (True, False):
        doc, model = nary_lower_outcome(unused_nary_definition=unused_nary_definition)
        assert _lean_route(doc) is not unused_nary_definition
        routed(monkeypatch, "lean")
        with pytest.raises(VEError, match=mismatch):
            check_conflict(doc, model=model)
        with pytest.raises(VEError, match=mismatch):
            check_conflict(doc, prove=True, tableau_steps=300)
        with pytest.raises(VEError, match=mismatch):
            check_witness(doc, "required->permitted", model, ["a"])


def capture_environment(third):
    """A core-family environment with `tri(act, act, third)`."""
    raw = flagged(family=("closure@0", "nary@0"), relation=True, data=False).to_dict()
    raw["vocabulary"]["predicates"]["tri"] = {"arguments": ["act", "act", third], "description": "tri"}
    return Environment(raw)


def capture_permits(third):
    permits = {
        "exists": Exists(third, Atom("tri", (Var(1), Var(1), Var(0)))),
        "nested": Exists(third, Not(Forall("act", Atom("tri", (Var(2), Var(0), Var(1)))))),
    }
    if third == "act":
        permits["open"] = Atom("tri", (Var(0), Var(0), Var(0)))
        permits["reach-body"] = Reach("star", Body("act", Atom("tri", (Var(0), Var(1), Var(2)))),
                                      Var(0), Var(0))
    return permits


CAPTURE_PERMITS = {"same": capture_permits("act"), "mixed": capture_permits("party")}
CAPTURE_CITES = {
    "depth0": Not(Unary("permitted", Var(0))),
    "depth1": Forall("act", Implies(Binary("before", Var(1), Var(0)), Unary("permitted", Var(1)))),
    "depth2": Exists("act", Forall("party", Implies(Binary("owner", Var(1), Var(0)),
                                             Unary("permitted", Var(2))))),
}
CAPTURE_NAMES = tuple(sorted(
    [f"{kind}-{permit}-{cite}"
     for kind, permits in CAPTURE_PERMITS.items()
     for permit in permits for cite in CAPTURE_CITES]
    + ["same-exists-proved", "same-exists-situation"]
))


def capture_documents():
    """lf-14b review F5's class: Lean-family-route documents whose lower
    regulated outcome holds an n-ary atom over its tuple variable, cited under
    zero to two binders of a higher rule. The base expansion leaves the atom's
    variables unsubstituted, so they are captured by the citing binders: a
    mixed-sort atom no longer types (the base `TypeMismatch`), a same-sort atom
    silently means something else."""
    docs = {}
    for kind, third in (("same", "act"), ("mixed", "party")):
        env = capture_environment(third)
        permits = CAPTURE_PERMITS[kind]
        for (p, permit), (c, cite) in product(permits.items(), CAPTURE_CITES.items()):
            docs[f"{kind}-{p}-{c}"] = NormDocument(env, [rule("may", "permitted", True, permit),
                                                         rule("must", "required", True, cite)])
    env = capture_environment("act")
    permit = rule("may", "permitted", True, Exists("act", Atom("tri", (Var(1), Var(1), Var(0)))))
    # Lean's `required->permitted` is unsatisfiable; the captured base expansion is not.
    docs["same-exists-proved"] = NormDocument(env, [permit, rule("must", "required", True, Exists(
        "act", And(Binary("before", Var(1), Var(0)), Unary("permitted", Var(1)))))])
    # `cited` releases `required` only under the captured base expansion.
    docs["same-exists-situation"] = NormDocument(env, [
        permit, rule("must", "required", True, Unary("urgent", Var(0))),
        rule("release", "required", False, Unary("urgent", Var(0))),
        rule("cited", "required", False, Forall("act", Implies(Binary("before", Var(1), Var(0)),
                                                               Unary("permitted", Var(1)))))])
    assert set(docs) == set(CAPTURE_NAMES)
    return docs


def capture_models(third):
    last = {"act": ["a", "b"], "party": ["p"]}[third]
    return [{"complete": True, "domains": {"act": ["a", "b"], "party": ["p"]}, "constants": {},
             "relations": {"before": before, "owner": owner, "urgent": urgent, "tri": tri}}
            for before, owner, urgent, tri in [
                ([["a", "b"]], [["a", "p"]], [], [["b", "b", last[-1]]]),
                ([["a", "b"], ["b", "b"]], [], [], [["a", "a", last[0]], ["a", "b", last[0]]]),
                ([], [["b", "p"]], [], []),
                ([["a", "b"]], [], [["a"]], [["b", "b", last[-1]]])]]


def lean_targets(doc):
    from ve.ast import _Decoder
    return {t["target"]: (t["sorts"], _Decoder().decode(t["ast"]))
            for t in doc._lean_regenerated()["conflict_targets"]}


@pytest.mark.parametrize("name", CAPTURE_NAMES)
def test_lean_route_generators_search_the_targets_lean_regenerates(monkeypatch, name):
    """lf-14b review F5, the class: on the Lean family route Python's untrusted
    witness search and prover work on exactly the conflict targets Lean's
    `norms-elaborate` regenerates (and `norms-conflict` checks), whatever the
    base expansion captured; the base expansion stays the admission check."""
    import ve.norms
    doc = capture_documents()[name]
    assert ve.norms._lean_route(doc)
    routed(monkeypatch, "lean")
    searched = {n: (list(s), f) for n, s, _, f in ve.norms._generator_targets(doc, lean=True)}
    assert searched == lean_targets(doc)
    assert [t[:3] for t in ve.norms._generator_targets(doc, lean=False)] == list(doc.conflict_targets())


@pytest.mark.parametrize("name", CAPTURE_NAMES)
def test_lean_route_model_check_answers_as_lean_checks_each_candidate(monkeypatch, name):
    """lf-14b review F5: a finite-model conflict check on the Lean family route
    never proposes a witness Lean refutes (which was `CheckerUnavailable`). Its
    answer is the first target, in Python's order, whose base expansion is
    admitted and which has a tuple Lean confirms, or the base `TypeMismatch` at
    the first target the base expansion does not type, or UNKNOWN."""
    from ve.backends.relay import decide
    from ve.norms import _Checker, _lean_case
    doc = capture_documents()[name]
    routed(monkeypatch, "lean")
    env = doc.base_environment()
    third = doc.env.predicates["tri"].arguments[2]
    for model in capture_models(third):
        expected = ("ok", "UNKNOWN", None, ())
        for target, sorts, admitted in doc.conflict_targets():
            try:
                _Checker(env).formula(admitted, tuple(reversed(sorts)))
            except VEError as error:
                expected = ("error", str(error))
                break
            confirmed = [values for values in product(*(model["domains"][s] for s in sorts))
                         if decide("family-norms", [_lean_case(doc, "norms-conflict", witness={
                             "target": target, "model": model, "tuple": list(values)})])[0]["verdict"] == "CONFLICT"]
            if confirmed:
                expected = ("ok", "CONFLICT", target, tuple(confirmed[0]))
                break
        try:
            report = check_conflict(doc, model=model)
            got = ("ok", report.status, report.target, report.tuple)
        except VEError as error:
            got = ("error", str(error))
        assert got == expected, model


def test_lean_route_f5_witness_is_unknown_not_checker_unavailable(monkeypatch):
    """lf-14b review F5's probe: same-sort n-ary arguments; the base expansion
    proposes `required->permitted` at `a`, which Lean refutes at both tuples."""
    doc = capture_documents()["same-exists-depth1"]
    routed(monkeypatch, "lean")
    model = {"complete": True, "domains": {"act": ["a", "b"], "party": ["p"]}, "constants": {},
             "relations": {"before": [["a", "b"]], "urgent": [], "owner": [], "tri": [["b", "b", "b"]]}}
    assert check_conflict(doc, model=model).status == "UNKNOWN"
    model["relations"]["tri"] = [["a", "a", "b"]]
    report = check_conflict(doc, model=model)
    assert (report.status, report.target, report.tuple) == ("CONFLICT", "required->permitted", ("b",))


def test_lean_route_situation_names_the_rules_selected_by_leans_targets(monkeypatch):
    """lf-14b review F5's class in the CONFLICT record: the situation names the
    rules selected under the substituted outcome Lean checks, not a rule the
    captured base expansion would select."""
    doc, model = capture_documents()["same-exists-situation"], capture_models("act")[3]
    routed(monkeypatch, "lean")
    report = check_conflict(doc, model=model)
    assert (report.status, report.target, report.tuple) == ("CONFLICT", "required", ("a",))
    assert report.situation == "act a: rule must requires; rule release releases"


def test_lean_route_proof_search_proves_the_targets_lean_replays(monkeypatch):
    """lf-14b review F5's class in proof search: Python's prover proves the
    substituted targets, so Lean replays its certificates. The captured base
    expansion of `required->permitted` is satisfiable; Lean's target is not."""
    doc = capture_documents()["same-exists-proved"]
    ops = routed(monkeypatch, "lean")
    assert check_conflict(doc, prove=True, tableau_steps=2000).status == "CONFLICT-FREE"
    assert ("norms_conflict", "lean") in ops


def test_non_first_order_conflict_zero_model_budget_is_unknown():
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("must", "required", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    model = {"complete": True, "domains": {"act": ["a"], "party": ["p"]},
             "constants": {}, "relations": {"owner": [["a", "p"]], "urgent": [], "before": []}}
    assert check_conflict(doc, model=model, max_evaluations=0).status == "UNKNOWN"
    assert check_conflict(doc, model=model, max_evaluations=50).status == "CONFLICT"


def test_non_first_order_conflict_refused_witness_is_unavailable(monkeypatch):
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("must", "required", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    model = {"complete": True, "domains": {"act": ["a"], "party": ["p"]},
             "constants": {}, "relations": {"owner": [["a", "p"]], "urgent": [], "before": []}}
    real = relay.decide

    def refuse(mode, cases, **kwargs):
        row = deepcopy(real(mode, cases, **kwargs)[0])
        if cases[0].get("kind") == "norms-conflict":
            row["verdict"] = "UNKNOWN"
        return [row]

    monkeypatch.setattr(relay, "decide", refuse)
    with pytest.raises(CheckerUnavailable, match="does not confirm"):
        check_conflict(doc, model=model)


def test_non_first_order_wire_faults_raise_content_errors():
    env = flagged(family=("closure@0",), relation=True)
    doc = NormDocument(env, [rule("may", "permitted", True,
                                  Reach("star", Named("before"), Var(0), Var(0)))])
    case = {"id": "fault", "kind": "norms-elaborate", "environment": env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules]}
    from ve.backends.relay import decide

    deep = ["top"]
    for _ in range(10_000):
        deep = ["not", deep]
    for bad in (7, True, None, [], {}, deep):
        mutant = deepcopy(case)
        mutant["norms"][0]["norm"]["guard"] = bad
        with pytest.raises(VEError) as caught:
            decide("family-norms", [mutant])
        assert not isinstance(caught.value, CheckerUnavailable)
    two_faults = deepcopy(case)
    two_faults["norms"][0]["norm"].update({"guard": 7, "over": None})
    with pytest.raises(VEError) as caught:
        decide("family-norms", [two_faults])
    assert not isinstance(caught.value, CheckerUnavailable)


def test_unknown_regulated_predicate_is_python_wording(monkeypatch):
    doc = document(flagged())
    for authority in ("python", "lean"):
        routed(monkeypatch, authority)
        with pytest.raises(VEError, match="^UnknownSymbol: regulated predicate urgent$"):
            doc.elaborate("urgent")


def test_norm_admission_is_dispatched_to_lean(monkeypatch):
    from ve.norm_admission import admit_norm_document
    env = flagged()
    doc = document(env)
    units = [{"id": f"u{i}", "span": [i, i + 1], "kind": "norm", "content": r.to_dict()}
             for i, r in enumerate(doc.rules)]
    layer = dict(doc.premises())["layer:norms:permitted"]
    source = {"units": units, "graph": {"root": "l", "nodes": [
        {"name": "l", "ast": _to_data(layer), "label": "layer:norms:permitted"}]}}
    routed(monkeypatch, "python")
    expected = admit_norm_document(env, source)
    ops = routed(monkeypatch, "lean")
    assert admit_norm_document(env, source) == expected
    assert ("norms_admission", "lean") in ops
