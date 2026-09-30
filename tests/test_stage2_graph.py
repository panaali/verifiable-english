"""Argument composition on the Lean authority: Lean's `graph` mode (VE/Service/Graph.lean)."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ve import ArgumentGraph, Claim, Deduction, check_argument, deduction_identity
from ve.ast import Const, Top, Unary, formula_to_data
from ve.backends import dispatch, lean_runner
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.errors import VEError
from ve.printer import print_formula
from tests import probe_matrix as pm

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")


def claim(env, name, formula=Top()):
    return Claim.create(env, name, print_formula(env, formula) + ".\n")


def with_certs(graph):
    by_name = {c.name: c for c in graph.claims}
    edges = []
    for edge in graph.deductions:
        proof = prove_entailment(graph.env, tuple(by_name[n].ast for n in edge.premises),
                                 by_name[edge.conclusion].ast, max_steps=1000)
        if proof.status == "Found":
            edge = replace(edge, certificates=({"edge_id": deduction_identity(graph, edge),
                                                "direction": "follows", "proof": proof.certificate},))
        edges.append(edge)
    return replace(graph, deductions=tuple(edges))


def packages():
    env = Environment(pm.raw_environment(()))
    shared = with_certs(ArgumentGraph(env, (claim(env, "root"), claim(env, "b"), claim(env, "a"), claim(env, "c")),
        (Deduction("er", ("b", "c"), "root"), Deduction("eb", ("a",), "b"),
         Deduction("ec", ("a",), "c")), "root"))
    raw = pm.raw_environment(("definitions@0",))
    raw["vocabulary"]["predicates"]["derived"]["defined"]["body"] = ["top"]
    defined = Environment(raw)
    background = with_certs(ArgumentGraph(defined, (claim(defined, "root", Unary("derived", Const("x"))),),
                                          (Deduction("er", (), "root"),), "root"))
    from ve.argument_fixtures import worked_examples
    return {"shared": shared, "background": background, **{
        f"worked_{name}": graph for name, graph in worked_examples().items()}}


def routed(monkeypatch, authority):
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, auth: seen.append((op, auth))])
    monkeypatch.setenv("VE_AUTHORITY", authority)
    return seen


def graph_calls(monkeypatch):
    calls = []
    real = lean_runner.run

    def spy(mode, cases, **kw):
        rows = real(mode, cases, **kw)
        if mode == "graph":
            calls.append((cases, rows))
        return rows

    monkeypatch.setattr(lean_runner, "run", spy)
    return calls


@pytest.mark.parametrize("name", list(packages()))
def test_argument_records_match_python_and_compose_through_lean(monkeypatch, name):
    graph = packages()[name]
    routed(monkeypatch, "python")
    expected = check_argument(graph, search=False).to_dict()
    seen = routed(monkeypatch, "lean")
    calls = graph_calls(monkeypatch)
    assert check_argument(graph, search=False).to_dict() == expected
    assert ("graph", "lean") in seen
    assert bool(calls) == expected["composed"]


def test_background_leaves_are_assumptions_of_the_lean_report(monkeypatch):
    graph = packages()["background"]
    routed(monkeypatch, "lean")
    calls = graph_calls(monkeypatch)
    record = check_argument(graph, search=False)
    assert record.composed
    [(_, [row])] = calls
    assert row["report"]["root"] == "root"
    assert any(name.startswith("background:") for name in row["report"]["assumptions"])
    assert [b["label"] for b in row["background"]] == ["background:definitions"]


def lean_case(graph):
    env = graph.env
    record = check_argument(graph, search=False)
    edges = [{"name": r["name"], "premises": r["premises"], "conclusion": r["conclusion"],
              "edge_id": r["edge_id"], "certificate": next(a["certificate"]["proof"] for a in r["artifacts"]
                                                            if a["kind"] == "follows")}
             for r in record.edges]
    nodes = [{"name": c.name, "source": c.source, "ast": formula_to_data(env, c.ast), "claim_id": c.claim_id}
             for c in graph.claims]
    return {"id": "graph", "environment": env.to_dict(), "nodes": nodes, "edges": edges, "root": graph.root}


@pytest.mark.parametrize("change,message", [
    (lambda case: case["nodes"][1].update(claim_id="0" * 64), "claim_id"),
    (lambda case: case["edges"][0].update(edge_id="0" * 64), "edge_id"),
    (lambda case: case["edges"][0].update(certificate=case["edges"][1]["certificate"]), "stale"),
    (lambda case: case["nodes"][1].update(source="false.\n"), "claim_id"),
])
def test_lean_graph_mode_rechecks_identities_and_bindings(monkeypatch, change, message):
    monkeypatch.setenv("VE_AUTHORITY", "python")
    case = lean_case(packages()["shared"])
    assert lean_runner.run("graph", [case])[0]["assumptions"] == ["a"]
    change(case)
    with pytest.raises(VEError, match=message):
        lean_runner.run("graph", [case])


def test_a_lean_refusal_or_different_projection_is_unavailable(monkeypatch):
    from ve.backends.diagnostics import checker_error
    graph = packages()["shared"]
    routed(monkeypatch, "lean")
    real = lean_runner.run

    def refuse(mode, cases, **kw):
        if mode == "graph":
            raise checker_error("graph rejected: a certificate in the root's cone does not check")
        return real(mode, cases, **kw)

    monkeypatch.setattr(lean_runner, "run", refuse)
    assert check_argument(graph, search=False).status == "CheckerUnavailable"

    def reorder(mode, cases, **kw):
        rows = real(mode, cases, **kw)
        return [{**row, "supporting_edges": row["supporting_edges"][::-1]} for row in rows] \
            if mode == "graph" else rows

    monkeypatch.setattr(lean_runner, "run", reorder)
    result = check_argument(graph, search=False)
    assert result.status == "CheckerUnavailable" and "projection" in result.errors[0]["message"]


FAMILIES = [("closure@0",), ("closure@0", "nary@0"), ("order@0",), ("closure@0", "definitions@0"),
            ("closure@0", "nary@0", "data@0"), ("closure@0", "norms@0"), ("order@0", "norms@0")]


@pytest.mark.parametrize("family", FAMILIES)
def test_closure_core_and_order_packages_compose_through_lean(monkeypatch, family):
    """A package over the closure, core or order family composes through
    Lean's graph mode (VE/Service/Family.lean): each deduction's certificate is
    the family's, and the report's leaves are Python's composition."""
    env = Environment(pm.raw_environment(family))
    formula = pm.semantic_formula(env)
    graph = with_certs(ArgumentGraph(env, (claim(env, "root", formula), claim(env, "a", formula),
                                           claim(env, "b")),
                                     (Deduction("er", ("a", "b"), "root"),), "root"))
    routed(monkeypatch, "python")
    expected = check_argument(graph, search=False).to_dict()
    assert expected["composed"], family
    seen = routed(monkeypatch, "lean")
    calls = graph_calls(monkeypatch)
    assert check_argument(graph, search=False).to_dict() == expected
    assert ("graph", "lean") in seen
    [(_, [row])] = calls
    assert row["assumptions"] == ["a", "b"] and row["supporting_edges"] == ["er"]


def test_a_family_certificate_bound_elsewhere_is_rejected_by_lean(monkeypatch):
    env = Environment(pm.raw_environment(("closure@0",)))
    formula = pm.semantic_formula(env)
    graph = with_certs(ArgumentGraph(env, (claim(env, "root", formula), claim(env, "a", formula)),
                                     (Deduction("er", ("a",), "root"),), "root"))
    routed(monkeypatch, "lean")
    calls = graph_calls(monkeypatch)
    check_argument(graph, search=False)
    [([case], _)] = calls
    case["edges"][0]["certificate"]["premise_meaning_ids"] = ["0" * 64]
    with pytest.raises(VEError, match="stale"):
        lean_runner.run("graph", [case])


def legacy_environment(kind):
    """The frozen pre-route envelopes of the Stage 0 probes (ve.core@0, and
    ve.core@0.1 closure or order)."""
    from ve.environment import (LANGUAGE, PROFILE, SPEC_REVISION as V0_REV, CLOSURE_LANGUAGE,
                                CLOSURE_PROFILES, CLOSURE_REVISION, ORDER_PROFILES, ORDER_REVISION)
    raw = pm.raw_environment(())
    raw.pop("profiles")
    if kind == "v0":
        raw.update(language=LANGUAGE, spec_revision=V0_REV, profile=PROFILE)
    else:
        raw.update(language=CLOSURE_LANGUAGE,
                   spec_revision=CLOSURE_REVISION if kind == "closure" else ORDER_REVISION,
                   profiles=list(CLOSURE_PROFILES if kind == "closure" else ORDER_PROFILES))
    return Environment(raw)


@pytest.mark.parametrize("kind", ["closure", "order"])
def test_legacy_packages_compose_through_lean(monkeypatch, kind):
    env = legacy_environment(kind)
    formula = Unary("base", Const("x"))
    graph = with_certs(ArgumentGraph(env, (claim(env, "root", formula), claim(env, "a", formula)),
                                     (Deduction("er", ("a",), "root"),), "root"))
    routed(monkeypatch, "python")
    expected = check_argument(graph, search=False).to_dict()
    assert expected["composed"]
    seen = routed(monkeypatch, "lean")
    calls = graph_calls(monkeypatch)
    assert check_argument(graph, search=False).to_dict() == expected
    assert ("graph", "lean") in seen and len(calls) == 1


def test_norms_profile_premises_are_background_leaves(monkeypatch):
    """A norms environment's Background ends with its profile premises; a
    certificate over them composes through Lean like any Background leaf."""
    from tests.test_norms import environment, obligation, permission
    env = environment({"required": obligation(), "permitted": permission()})
    graph = with_certs(ArgumentGraph(env, (Claim.create(env, "root", "true.\n"),),
                                     (Deduction("er", (), "root"),), "root"))
    routed(monkeypatch, "python")
    expected = check_argument(graph, search=False).to_dict()
    assert expected["composed"]
    routed(monkeypatch, "lean")
    calls = graph_calls(monkeypatch)
    assert check_argument(graph, search=False).to_dict() == expected
    [(_, [row])] = calls
    assert [b["label"] for b in row["background"]] == ["background:profile"]
