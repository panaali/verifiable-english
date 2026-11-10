"""Writes the fixture of lean/ResponseShape/Schemas/SoftPairsChecks.lean (rights-cfr-2-budget-1): four default rules on
`x_required` whose pairs (a,b) and (c,d) have disjoint guards, with a DISJOINT certificate package for each, as
tests/test_soft_review_regressions.py::test_disjoint_pair_is_removed_from_conditional_report builds one.
Run from the checkout: uv run python docs/rights/rights-cfr-2-budget-1/evidence/soft_pairs_fixture.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from tests.test_soft_norms_lean import base_prime, env, should  # noqa: E402
from ve.ast import formula_from_data  # noqa: E402
from ve.entailment import prove_entailment  # noqa: E402
from ve.soft_route import _run, classify_soft_pairs  # noqa: E402
from ve.softnorms import SoftEnvironment, SoftNormDocument  # noqa: E402

q, r = ["unary", "q", ["var", 0]], ["unary", "r", ["var", 0]]
raw = env(extra={"q": {"arguments": ["assistant"], "description": "q"},
                 "r": {"arguments": ["assistant"], "description": "r"}})
rules = [should("a", "x_required", True, guard=q), should("b", "x_required", False, guard=["not", q]),
         should("c", "x_required", True, guard=r), should("d", "x_required", False, guard=["not", r])]
soft = SoftNormDocument(SoftEnvironment(raw), rules)
row = _run({"id": "e", "kind": "soft-elaborate", "environment": raw, "norms": rules})
base = base_prime(row)
premises = [formula_from_data(base, item["ast"]) for item in row["background"]
            if item.get("label", "").startswith("soft:exception:")]
pairs = {}
for pair in row["colliding_pairs"]:
    if pair["label"] in ("soft:coherence:a,b", "soft:coherence:c,d"):
        proof = prove_entailment(base, premises, formula_from_data(base, pair["ast"]))
        assert proof.status == "Found", pair["label"]
        pairs[pair["label"]] = {"environment_id": soft.env.environment_id, "document_hash": soft.document_hash,
                                "target": pair["label"], "certificate": proof.certificate}
classified = classify_soft_pairs(soft, pairs=pairs)
print(json.dumps({"labels": [p["label"] for p in row["colliding_pairs"]], "discharged": classified["discharged"],
                  "weighing_points": classified["weighing_points"]}))
for name, value in (("env", raw), ("norms", rules), ("pairs", pairs)):
    print(name, json.dumps(json.dumps(value, separators=(",", ":"), sort_keys=True)))
