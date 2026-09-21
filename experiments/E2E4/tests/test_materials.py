from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ve import ArgumentGraph, FiniteModel
from ve.search import check_countermodel
from experiments.E2E4.materials import (
    E2_CELLS, E4_CELLS, REQUIREMENT, build_items, construction_support,
    render_cell, replay, validate_e2,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def rows():
    return build_items("all")


def test_counts_balance_and_fixed_e2_requirement(rows):
    items = [r for r in rows if r["payload"]["experiment"] == "E2"]
    assert len(items) == 36
    assert Counter(r["payload"]["size"] for r in items) == {4: 12, 32: 12, 256: 12}
    assert Counter(r["label"] for r in items) == {"bad": 24, "good": 12}
    assert {r["payload"]["requirement"] for r in items} == {REQUIREMENT}
    assert Counter(r["payload"]["_audit"]["error"] for r in items) == {
        "honest": 12, "invalid_step": 12, "false_leaf": 6, "wrong_specification": 6}
    assert all(len(r["payload"]["leaves"]) == 2 for r in items)


def test_every_persisted_check_replays_and_invalid_has_exactly_one_gap(rows):
    seen = {}
    for row in rows:
        p = row["payload"]
        checks = p["checks"].values() if p["experiment"] == "E2" else (p["check"],)
        for chk in checks:
            key = json.dumps(chk["graph"], sort_keys=True)
            if key not in seen:
                seen[key] = replay(chk)
            assert seen[key] == chk["result"]
            for artifact in chk["result"]["edges"][0]["artifacts"]:
                if artifact["kind"] == "gap":
                    assert artifact["check"]["valid"] is True
        if p["experiment"] == "E2":
            assert validate_e2(p) == p["checker_output"]
            gaps = p["checker_output"]["unresolved_steps"]
            assert len(gaps) == (1 if p["_audit"]["error"] == "invalid_step" else 0)
            assert len(p["steps"]) == p["size"]
            for n, step in enumerate(p["steps"], 1):
                assert step["premises"][0] == ("fact" if n == 1 else f"s{n-1}")


def test_mutated_gap_witness_rejected(rows):
    bad = next(r for r in rows if r["payload"].get("_audit", {}).get("error") == "invalid_step")
    check = next(c for c in bad["payload"]["checks"].values() if not c["result"]["composed"])
    graph = ArgumentGraph.from_dict(check["graph"])
    artifact = next(a for a in check["result"]["edges"][0]["artifacts"] if a["kind"] == "gap")
    model_data = deepcopy(artifact["model"])
    entity = model_data["constants"]["a"]
    model_data["relations"]["r"] = [[entity]]
    model = FiniteModel.from_dict(graph.env, model_data)
    claims = {c.name: c for c in graph.claims}
    cm = check_countermodel(graph.env, [claims[n].ast for n in graph.deductions[0].premises], claims["root"].ast, model)
    assert not cm.valid and cm.conclusion_value


def test_link_and_display_substitutions_rejected(rows):
    p = deepcopy(next(r["payload"] for r in rows if r["payload"]["experiment"] == "E2" and r["label"] == "good"))
    p["steps"][1]["premises"] = ["fact"]
    with pytest.raises(ValueError, match="link"):
        validate_e2(p)
    p["steps"][1]["premises"] = ["s1"]
    p["steps"][1]["source"] = "@a is r.\n"
    with pytest.raises(ValueError, match="Displayed step"):
        validate_e2(p)


def test_construction_labels_from_records_requirement_and_check(rows):
    for row in rows:
        p = row["payload"]
        if p["experiment"] != "E2":
            continue
        kind = p["_audit"]["error"]
        assert construction_support(p) is (kind != "false_leaf")
        matches = p["submitted_root"]["source"] == "@a is q.\n"
        assert matches is (kind != "wrong_specification")
        assert (construction_support(p) and matches and p["checker_output"]["all_local_edges_follow"]) == (row["label"] == "good")


def test_renderers_have_identical_checker_reports_and_no_audit_labels(rows):
    for row in rows:
        p = {k: v for k, v in row["payload"].items() if not k.startswith("_")}
        cells = E2_CELLS if p["experiment"] == "E2" else E4_CELLS
        prompts = [render_cell(p, c) for c in cells]
        assert all('"_audit"' not in x and row["id"] not in x for x in prompts)
        assert all(x.endswith('{"verdict":"approve"} or {"verdict":"reject"}.') for x in prompts)
        if p["experiment"] == "E2":
            marker = "Checker output (identical information in both checked views):\n"
            assert marker not in prompts[0]
            assert prompts[1].split(marker)[1] == prompts[2].split(marker)[1]
            assert prompts[0].count(": from ") == p["size"]
            assert "Full submitted work" not in prompts[1] + prompts[2]
            assert "p(a)" in prompts[1] and "@a is p" in prompts[2]
            assert json.dumps(p["records"], sort_keys=True) in prompts[0]
            assert json.dumps(p["records"], sort_keys=True) in prompts[1]


def test_e4_true_gaps_and_dishonest_model_fails_valid_premise(rows):
    items = [r for r in rows if r["payload"]["experiment"] == "E4"]
    assert len(items) == 8 and Counter(r["label"] for r in items) == {"good": 4, "bad": 4}
    for row in items:
        p = row["payload"]
        graph = ArgumentGraph.from_dict(p["check"]["graph"])
        claims = {c.name: c for c in graph.claims}
        assert [claims[n].source.strip() for n in graph.deductions[0].premises] == p["premises"]
        assert claims["root"].source.strip() == p["conclusion"]
        model = FiniteModel.from_dict(graph.env, p["asserted_model"])
        cm = check_countermodel(graph.env, [claims[n].ast for n in graph.deductions[0].premises], claims["root"].ast, model)
        if row["label"] == "good":
            assert p["check"]["result"]["composed"]
            assert not cm.valid and cm.premise_values[-1] is False
        else:
            assert cm.valid
        assert "unchecked" in render_cell(row, "dishonest_critic")
        for pred in model.relations:
            assert pred in render_cell(row, "prose_critique")


def test_splits_and_generated_jsonl(rows):
    dev = [r for r in rows if r["split"] == "dev"]
    scored = [r for r in rows if r["split"] == "scored"]
    assert {r["group"] for r in dev}.isdisjoint({r["group"] for r in scored})
    for exp in ("E2", "E4"):
        for split in ("dev", "scored"):
            got = [json.loads(x) for x in (ROOT / f"{exp.lower()}-{split}.jsonl").read_text().splitlines()]
            assert got == build_items(split, exp)
    dev_prompts = {render_cell(r, "prose_critique") for r in dev if r["payload"]["experiment"] == "E4"}
    scored_prompts = {render_cell(r, "prose_critique") for r in scored if r["payload"]["experiment"] == "E4"}
    assert not dev_prompts & scored_prompts


@pytest.mark.parametrize("split", ["nope", "DEV", ""])
def test_invalid_split(split):
    with pytest.raises(ValueError):
        build_items(split)
