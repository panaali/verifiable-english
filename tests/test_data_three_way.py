"""Generated data declarations and finite tables across Python and Lean."""
import json
import os
import random
from subprocesses import HANG_TIMEOUT
import subprocess
from pathlib import Path

from ve.ast import And, Binary, Const, Not, formula_to_data
from ve.background import background
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.errors import InvalidModel
from ve.model import FiniteModel


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_conformance"
RUST = Path(os.environ.get("VE_RUST_BINARY", os.environ.get(
    "VE_W5_RUST_BIN", str(ROOT / "rust/target/release/ve"))))


def _run(cases):
    completed = subprocess.run([str(LEAN), "route", "-"], input=json.dumps(cases),
                               text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert completed.returncode in (0, 1), completed.stderr
    return json.loads(completed.stdout)


def test_1000_generated_flag_and_literal_sets():
    assert LEAN.exists(), "lake build must produce the route runner"
    assert RUST.exists(), "cargo build --release must produce the Rust runner"
    rng = random.Random(5)
    cases, expected, elaborated = [], [], []
    for index in range(1000):
        functional, total = rng.choice((False, True)), rng.choice((False, True))
        backup_functional, backup_total = rng.choice((False, True)), rng.choice((False, True))
        count = rng.randrange(1, 4)
        literals = {f"lit{j}": {"sort": "$string"} for j in range(count)}
        env = Environment({"language": "ve.core@0.2",
            "profiles": ["data@0", "relational-fol@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"person": {"description": "Person"}},
                "predicates": {"field": {"arguments": ["person", "$string"],
                    "description": "A field", "functional": functional, "total": total},
                    **({"backup": {"arguments": ["person", "$string"],
                        "description": "Backup field", "functional": backup_functional,
                        "total": backup_total}} if index % 2 == 0 else {})},
                "constants": literals}})
        chosen = rng.randrange(0, 4)
        rows = ["e0", "e1"][:chosen]
        backup_rows = ["e1", "e2"][:rng.randrange(0, 3)]
        model = {"complete": True, "domains": {"person": ["p"], "$string": ["e0", "e1", "e2"]},
                 "constants": {name: f"e{rng.randrange(3)}" for name in literals},
                 "relations": {"field": [["p", value] for value in rows],
                     **({"backup": [["p", value] for value in backup_rows]}
                        if index % 2 == 0 else {})}}
        try:
            FiniteModel.from_dict(env, model)
            expected.append(("ok", None))
        except InvalidModel as exc:
            expected.append(("error", exc.generator))
        cases.append({"id": f"data-{index}", "kind": "evaluate", "environment": env.to_dict(),
                      "model": model, "ast": [["top"]]})
        cases.append({"id": f"background-{index}", "kind": "background", "environment": env.to_dict()})
        items = background(env)
        elaborated.append({"premises": [formula_to_data(env, p.formula, _generated=True) for p in items],
                           "generators": [p.generator for p in items]})
    results = _run(cases)
    assert len(results) == 2000
    for case, want, generated, got, shown in zip(cases[::2], expected, elaborated,
                                                   results[::2], results[1::2], strict=True):
        assert (got["status"], got.get("generator")) == want, (case["id"], want, got)
        assert {key: shown[key] for key in generated} == generated, (case["id"], shown)
    completed = subprocess.run([str(RUST), "conformance"],
        input=json.dumps(cases[::2]), text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert completed.returncode in (0, 1), completed.stderr
    rust_results = json.loads(completed.stdout)
    assert len(rust_results) == 1000
    for case, want, got in zip(cases[::2], expected, rust_results, strict=True):
        assert got["status"] == want[0], (case["id"], want, got)
        if want[0] == "error":
            assert got["error"]["code"] == "InvalidModel"
            assert want[1] in got["error"]["message"], (case["id"], want, got)


def test_flag_certificate_bound_to_generated_background():
    assert LEAN.exists(), "lake build must produce the route runner"
    env = Environment({"language": "ve.core@0.2",
        "profiles": ["data@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"person": {"description": "Person"}},
            "predicates": {"department": {"arguments": ["person", "$string"],
                "description": "Department", "functional": True, "total": True}},
            "constants": {"alice": {"sort": "person", "description": "Alice"},
                          "finance": {"sort": "$string"}, "sales": {"sort": "$string"}}}})
    conclusion = Not(And(Binary("department", Const("alice"), Const("finance")),
                         Binary("department", Const("alice"), Const("sales"))))
    proof = prove_entailment(env, (), conclusion)
    assert proof.status == "Found"
    case = {"id": "data-certificate", "kind": "certificate", "environment": env.to_dict(),
            "premises": [], "conclusion": ["not", ["and",
                ["binary", "department", ["const", "alice"], ["const", "finance"]],
                ["binary", "department", ["const", "alice"], ["const", "sales"]]]],
            "certificate": proof.certificate}
    assert _run([case])[0]["valid"] is True
    changed = env.to_dict()
    del changed["vocabulary"]["predicates"]["department"]["functional"]
    case["environment"] = changed
    assert _run([case])[0].get("valid") is not True


def test_closure_family_replays_the_same_data_background():
    assert LEAN.exists(), "lake build must produce the route runner"
    from tests.test_data_flags import environment
    data = environment().to_dict()
    data["profiles"] = ["closure@0", "data@0", "relational-fol@0"]
    env = Environment(data)
    conclusion = Not(And(Binary("department", Const("alice"), Const("finance")),
                         Binary("department", Const("alice"), Const("sales"))))
    certificate = prove_entailment(env, (), conclusion).certificate
    assert certificate is not None
    case = {"id": "closure-data", "kind": "certificate", "environment": data,
            "premises": [], "conclusion": ["not", ["and",
                ["binary", "department", ["const", "alice"], ["const", "finance"]],
                ["binary", "department", ["const", "alice"], ["const", "sales"]]]],
            "certificate": certificate}
    assert _run([case])[0]["valid"] is True
