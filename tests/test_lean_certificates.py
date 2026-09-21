"""The Python prover searches; the independently proved Lean checker decides."""
import copy
import json
import subprocess

from test_lean_conformance import lean_executable
from conformance.certificates import environment, envelope, run
from ve.ast import And, Const, Forall, Top, Unary, Var
from ve.entailment import prove_entailment


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
                              capture_output=True, text=True, timeout=10)
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
                          capture_output=True, text=True, timeout=10)
    assert proc.returncode == 1
    assert [r["valid"] for r in json.loads(proc.stdout)] == [True, False, False, False]
