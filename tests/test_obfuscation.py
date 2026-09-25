import json
import re

import pytest

from ve_experiments.obfuscation.materials import affine_root, dataset, evaluate, render, verify_item
from ve_experiments.obfuscation.mutations import FAMILIES, check_lean, plants
from ve_experiments.obfuscation.run import dry_run, leakage_audit, prepare


def test_grid_oracle_and_single_leaf_dependence():
    items = dataset()
    assert len(items) == 24
    assert {(x["depth"], x["truth"]) for x in items} == {
        (8, True), (8, False), (32, True), (32, False)}
    for item in items:
        verify_item(item)
        assert (evaluate(item) == item["target"]) is item["truth"]
        if not item["truth"]:
            assert affine_root(item)[0][item["false_leaf"]] != 0
    for depth in (8, 32):
        assert sum(x["depth"] == depth for x in items) == 12


def test_blinding_and_structural_audit():
    items = dataset()
    assert leakage_audit(items)["status"] == "PASS"
    for item in items:
        surface = render(item)
        assert item["id"] not in surface
        assert not re.search(r"false_leaf|dishonest|truth", surface, re.I)
    broken = [dict(x) for x in items]
    broken[0]["steps"] = broken[0]["steps"][:-1]
    assert leakage_audit(broken)["status"] == "FAIL"


def test_programmatic_plants_have_distinct_mismatches_and_lean_certificates():
    rows = plants()
    assert len(rows) == 20
    assert {p["family"] for p in rows} == set(FAMILIES)
    assert all(p["semantic_mismatch"] for p in rows)
    assert all(check_lean(plant) for plant in rows)
    with pytest.raises(ValueError):
        check_lean({"lean": "theorem x : True := by sorry"})


def test_prepare_and_dry_run_never_sample(monkeypatch, tmp_path):
    from ve_experiments.claude_cli import ClaudeCLI

    def forbidden(*args, **kwargs):
        raise AssertionError("model call attempted")

    monkeypatch.setattr(ClaudeCLI, "sample", forbidden)
    prepare(tmp_path, lean=False)
    requests = dry_run(tmp_path)
    assert len(requests) == 72
    assert len({r["request_id"] for r in requests}) == 72
    plan = json.loads((tmp_path / "g1-plan.json").read_text())
    assert plan["model_calls_executed"] == 0
    assert plan["paid_spend_usd"] == 0
    assert plan["paid_cap_usd"] <= 5
    assert not (tmp_path / "ledger.jsonl").exists()
    assert all("false_leaf" not in r["prompt"] for r in requests)
