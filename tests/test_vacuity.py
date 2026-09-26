from conformance.p0 import environment
from ve.argument import ArgumentGraph, Claim, Deduction, check_argument
from ve.ast import Bottom, Top
from ve.check import check
from ve.environment import Environment
from ve.vacuity import premise_status


def test_three_valued_premise_report():
    env = Environment(environment())
    assert premise_status(env, (Top(),))["status"] == "model"
    contradiction = premise_status(env, (Bottom(),))
    assert contradiction["status"] == "INCONSISTENT"
    assert contradiction["certificate"]
    assert premise_status(env, (Top(),), max_proof_steps=0, max_models=0)["status"] == "UNKNOWN"
    assert check(env, "false.\n")["premises"]["status"] == "INCONSISTENT"


def test_argument_marks_dependent_certificate_vacuous():
    env = Environment(environment())
    premise = Claim.create(env, "premise", "false.\n")
    root = Claim.create(env, "root", "true.\n")
    graph = ArgumentGraph(env, (premise, root), (Deduction("edge", ("premise",), "root"),), "root")
    result = check_argument(graph)
    assert result.premises["status"] == "INCONSISTENT"
    assert result.edges[0]["premise_status"]["status"] == "INCONSISTENT"
    assert any(a.get("vacuous") for a in result.edges[0]["artifacts"])
