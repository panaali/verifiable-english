"""The Python prover searches; the independently proved Lean checker decides."""
import copy
import json
from subprocesses import HANG_TIMEOUT
import subprocess

import pytest

from test_lean_conformance import lean_executable
from conformance.certificates import environment, envelope, run
from ve.ast import And, Bottom, Const, Exists, Forall, Implies, Not, Or, Top, Unary, Var
from ve.entailment import _binding, check_entailment_certificate, prove_entailment
from ve.limits import MAX_TABLEAU_DEPTH


def test_python_certificates_and_forged_mutations(lean_executable):
    report = run(lean_executable)
    assert report["constructive_random_queries"] >= 300
    assert report["python_accepted"] == report["lean_accepted"]
    assert report["forged"] >= 100
    assert report["forged"] == report["lean_rejected_forged"]
    assert set(report["trace_rule_counts"]) >= {
        "alpha:And:True", "alpha:Or:False", "alpha:Implies:False",
        "beta:And:False", "beta:Or:True", "beta:Implies:True",
        "gamma:Forall:True", "gamma:Exists:False",
        "delta:Forall:False", "delta:Exists:True", "not:Not:True", "not:Not:False"}


def test_certificate_json_rejects_duplicate_keys_null_and_invalid_index(lean_executable):
    env = environment()
    p = Unary("p", Const("a"))
    ps = [And(p, Top())]
    certificate = prove_entailment(env, ps, p).certificate
    case = envelope("malformed", env, ps, p, certificate)
    raw = json.dumps(case)
    malformed = [raw.replace('"rule": "expand"', '"rule": "close", "rule": "expand"', 1),
                 raw.replace('"at": 0', '"at": -1', 1),
                 raw.replace('"at": 0', '"at": 0.0', 1),
                 raw.replace('"at": 0', '"at": null', 1)]
    for text in malformed:
        proc = subprocess.run([str(lean_executable), "check-certificate"], input=text,
                              capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert proc.returncode == 2, proc.stdout + proc.stderr


def test_wrong_order_and_duplicate_premises_are_bound(lean_executable):
    env = environment()
    p = Unary("p", Const("a"))
    ps = [Top(), p, p]
    cert = prove_entailment(env, ps, p).certificate
    base = envelope("ordered", env, ps, p, cert)
    cases = [base]
    for index, premises in enumerate(([p, Top(), p], [Top(), p], [p, p, Top()])):
        cases.append(envelope(f"changed_{index}", env, premises, p, cert))
    proc = subprocess.run([str(lean_executable), "check-certificate"], input=json.dumps(cases),
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert proc.returncode == 1
    assert [r["valid"] for r in json.loads(proc.stdout)] == [True, False, False, False]


def test_compound_closure_versions_and_parameter_bindings(lean_executable):
    env = environment(False)
    p = Unary("p", Var(0))
    quantified = Exists("item", p)
    cases = []
    for f in (Not(quantified), And(quantified, Top()), Or(quantified, Top()),
              Implies(quantified, Top()), Forall("item", p), quantified):
        cert = prove_entailment(env, [f], f).certificate
        assert cert["trace"] == {"rule": "close"}
        cases.append(envelope(str(len(cases)), env, [f], f, cert))
        old = {**cert, "checker_version": "ve-tableau-checker@1"}
        cases.append(envelope(str(len(cases)), env, [f], f, old))
    # Same open compound AST, different parameters: existence is not universality.
    body = Or(p, p)
    ps, goal = [Exists("item", body)], Forall("item", body)
    forged = {**_binding(env, tuple(ps), goal), "trace": {
        "rule": "expand", "at": 0, "children": [{
            "rule": "expand", "at": 1, "children": [{"rule": "close"}]}]}}
    assert not check_entailment_certificate(env, ps, goal, forged).valid
    cases.append(envelope("different_bindings", env, ps, goal, forged))
    proc = subprocess.run([str(lean_executable), "check-certificate"], input=json.dumps(cases),
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert proc.returncode == 0, proc.stderr
    assert [r["valid"] for r in json.loads(proc.stdout)] == [True, False] * 6 + [False]


@pytest.mark.parametrize("depth", [MAX_TABLEAU_DEPTH, MAX_TABLEAU_DEPTH + 1, 126, 300])
def test_depth_limit_is_per_case_and_matches_python(lean_executable, depth):
    env = environment(False)
    ps, goal = [Not(Bottom())] * depth, Top()
    trace = {"rule": "close"}
    for index in reversed(range(depth)):
        trace = {"rule": "expand", "at": index, "children": [trace]}
    cert = {**_binding(env, tuple(ps), goal), "trace": trace}
    checked = check_entailment_certificate(env, ps, goal, cert)
    assert checked.valid == (depth <= MAX_TABLEAU_DEPTH)
    if not checked.valid:
        assert checked.status == "ResourceLimit"
    deep = envelope("deep", env, ps, goal, cert)
    good = envelope("good", env, [], Top(), prove_entailment(env, [], Top()).certificate)
    # The good case on BOTH sides must survive a certificate/JSON depth error.
    proc = subprocess.run([str(lean_executable), "check-certificate"],
                          input=json.dumps([good, deep, good]),
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert proc.returncode == int(depth > MAX_TABLEAU_DEPTH), proc.stderr + proc.stdout
    rows = json.loads(proc.stdout)
    assert len(rows) == 3
    assert [r["valid"] for r in rows] == [True, depth <= MAX_TABLEAU_DEPTH, True]
    if depth > MAX_TABLEAU_DEPTH:
        assert rows[1]["error"].startswith("ResourceLimit:")
        assert rows[1].get("id") == "deep" or rows[1]["case_index"] == 1


@pytest.mark.parametrize("raw", ['[,]', '[{} ,]', '[, {}]', '[{}] []', '[[}]]',
                                  '["unterminated]', '[{"a":1,"a":2},{}]'])
def test_batch_splitting_preserves_strict_json_rejection(lean_executable, raw):
    proc = subprocess.run([str(lean_executable), "check-certificate"], input=raw,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert proc.returncode == 2
