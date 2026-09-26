"""Generated data declarations and finite tables across Python and Lean."""
import json
import random
import subprocess
from pathlib import Path

import pytest

from ve.ast import And, Binary, Const, Not
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.errors import InvalidModel
from ve.model import FiniteModel


LEAN = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_conformance"


def _run(cases):
    completed = subprocess.run([str(LEAN), "route", "-"], input=json.dumps(cases),
                               text=True, capture_output=True, timeout=120)
    assert completed.returncode in (0, 1), completed.stderr
    return json.loads(completed.stdout)


@pytest.mark.skipif(not LEAN.exists(), reason="lake build has not produced the route runner")
def test_1000_generated_flag_and_literal_sets():
    rng = random.Random(5)
    cases, expected = [], []
    for index in range(1000):
        functional, total = rng.choice((False, True)), rng.choice((False, True))
        count = rng.randrange(1, 4)
        literals = {f"lit{j}": {"sort": "$string"} for j in range(count)}
        env = Environment({"language": "ve.core@0.2",
            "profiles": ["data@0", "relational-fol@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"person": {"description": "Person"}},
                "predicates": {"field": {"arguments": ["person", "$string"],
                    "description": "A field", "functional": functional, "total": total}},
                "constants": literals}})
        chosen = rng.randrange(0, 4)
        rows = ["e0", "e1"][:chosen]
        model = {"complete": True, "domains": {"person": ["p"], "$string": ["e0", "e1", "e2"]},
                 "constants": {name: f"e{rng.randrange(3)}" for name in literals},
                 "relations": {"field": [["p", value] for value in rows]}}
        try:
            FiniteModel.from_dict(env, model)
            expected.append(("ok", None))
        except InvalidModel as exc:
            expected.append(("error", exc.generator))
        cases.append({"id": f"data-{index}", "kind": "evaluate", "environment": env.to_dict(),
                      "model": model, "ast": [["top"]]})
    results = _run(cases)
    assert len(results) == 1000
    for case, want, got in zip(cases, expected, results, strict=True):
        assert (got["status"], got.get("generator")) == want, (case["id"], want, got)


@pytest.mark.skipif(not LEAN.exists(), reason="lake build has not produced the route runner")
def test_flag_certificate_bound_to_generated_background():
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
