from collections import Counter, defaultdict
from copy import deepcopy
import json

import pytest

from experiments.E5.materials import (
    HERE, CELLS, FAMILIES, TEMPLATES, build_items, graph_for_payload, grounding_audit,
    logical_bundle, render_cell, sense_panel, split_manifest,
)
from experiments.E5.leak_audit import audit, tokens
from ve.argument import ArgumentGraph, check_argument
from ve.search import check_countermodel


@pytest.fixture(scope="module")
def rows():
    return build_items("dev") + build_items("scored")


def test_frozen_export_and_splits(rows):
    manifest = split_manifest()
    assert len(rows) == 384
    assert len({r['id'] for r in rows}) == len(rows)
    for split in ("dev", "scored"):
        selected = [r for r in rows if r["split"] == split]
        assert [json.loads(s) for s in (HERE / f"{split}.jsonl").read_text().splitlines()] == selected
        for row in selected:
            a = row["payload"]["_audit"]
            assert manifest["groups"][row["group"]] == split
            assert manifest["templates"][a["template"]] == split
            assert manifest["vocabulary_families"][a["vocabulary_family"]] == split
            assert set(row) == {"id", "label", "group", "split", "payload"}
    for field in ("template", "vocabulary_family"):
        values = [{r["payload"]["_audit"][field] for r in rows if r["split"] == s} for s in ("dev", "scored")]
        assert not values[0] & values[1]


def test_balanced_grounding_and_real_approval_labels(rows):
    strata = defaultdict(Counter)
    for row in rows:
        a = row["payload"]["_audit"]
        strata[a["template"], a["family"], a["stratum"]][a["grounding_label"]] += 1
        assert row["label"] == ("good" if a["grounding_label"] == "good" and not a["invalid_deduction"] else "bad")
    assert len(strata) == len(TEMPLATES) * len(FAMILIES) * 2
    assert all(c["good"] == c["bad"] == 2 for c in strata.values())


def test_construction_labels_and_perturbations(rows):
    for row in rows:
        p = row["payload"]
        assert grounding_audit(p)["label"] == p["_audit"]["grounding_label"]
        if p["_audit"]["grounding_label"] == "bad":
            assert {v for _, v in grounding_audit(p)["issues"]} == {p["_audit"]["family"]}
    # A good item becomes unsupported if its citation is replaced by its distractor.
    p = deepcopy(next(r["payload"] for r in rows if r["payload"]["_audit"]["grounding_label"] == "good"
                      and r["payload"]["_audit"]["family"] == "unsupported_leaf"))
    used = {x for l in p["leaves"] for x in l["evidence_ids"]}
    decoy = next(r["record_id"] for r in p["records"] if r["record_id"] not in used)
    p["leaves"][0]["evidence_ids"] = [decoy]
    assert grounding_audit(p)["label"] == "bad"


def test_every_item_certified_by_real_checker_and_all_assumptions_retained(rows):
    for row in rows:
        p = row["payload"]
        graph = graph_for_payload(p)
        result = check_argument(graph, search=False)
        assert result.status == p["checker"]["status"]
        assert result.composed == p["checker"]["composed"]
        assert {k: list(v) for k, v in result.findings.items()} == p["checker"]["findings"]
        assert graph.graph_id == p["_audit"]["graph_id"]
        assert set(result.remaining_assumptions) == {l["claim"] for l in p["leaves"]}
        assert not result.errors
        if p["_audit"]["invalid_deduction"]:
            assert sum("gap" in f for f in result.findings.values()) == 1
            assert not result.composed
        else:
            assert all(f == ("follows",) for f in result.findings.values())
            assert set(a["name"] for a in result.composition["assumptions"]) == set(result.remaining_assumptions)


def test_persisted_certificates_replay_and_witness_corruption_fails():
    for line in (HERE / "certificates.jsonl").read_text().splitlines():
        row = json.loads(line)
        graph = ArgumentGraph.from_dict(row["graph"])
        result = check_argument(graph, search=False)
        assert result.composed is (not row["invalid_deduction"])
        if row["invalid_deduction"]:
            edge = graph.deductions[-1]
            claims = {c.name: c for c in graph.claims}
            model = edge.countermodels[0]
            # Using the same formula as both premise and conclusion cannot yield a gap.
            conclusion = claims[edge.conclusion].ast
            assert not check_countermodel(graph.env, (conclusion,), conclusion, model).valid


def test_badge_matches_checker_and_never_grounding_label(rows):
    for row in rows:
        p = row["payload"]
        assert "Badge:" not in render_cell(row, "a")
        expected = "Badge: proof checked (Checked)." if p["checker"]["composed"] else "Badge: proof not checked (Incomplete)."
        for cell in CELLS[1:]:
            assert expected in render_cell(row, cell)
        for cell in CELLS:
            text = render_cell(row, cell)
            assert row["id"] not in text
            assert p["_audit"]["template"] not in text
            assert "_audit" not in text and "grounding_label" not in text
            visible = {k: v for k, v in p.items() if not k.startswith("_")}
            assert render_cell(visible, cell) == text
        assert "Outstanding obligations" not in render_cell(row, "b")
        assert "Predicate-use panel" not in render_cell(row, "c")
        assert "urn:ve:e5" not in render_cell(row, "d")


def test_sense_panel_uses_only_cited_records(rows):
    for row in rows:
        p = row["payload"]
        flags = sense_panel(p)
        mixed = any(r["differing_evidence_senses"] for r in flags)
        assert mixed == (p["_audit"]["family"] == "merged_vocabulary" and p["_audit"]["grounding_label"] == "bad")
        for f in flags:
            used = {e for l in p["leaves"] for e in l["evidence_ids"]}
            assert set(f["evidence_senses"]) <= used


def test_exact_pairwise_lexical_matching_and_leak_gate(rows):
    pairs = defaultdict(list)
    for row in rows:
        pairs[row["payload"]["_audit"]["pair"]].append(render_cell(row, "a"))
    for texts in pairs.values():
        assert len(texts) == 2
        assert len(texts[0]) == len(texts[1])
        assert tokens(texts[0]) == tokens(texts[1])
        assert texts[0] != texts[1]  # a citation association really changed
    report = audit()
    for metrics in report["splits"].values():
        assert metrics["bow_logistic_accuracy"] <= .60
        assert metrics["any_unigram_classifier_upper_bound"] == .5
        assert metrics["length_keyword_classifier_upper_bound"] == .5


def test_reject_unknown_split_and_cell():
    with pytest.raises(ValueError):
        build_items("test")
    with pytest.raises(ValueError):
        render_cell({}, "z")


def test_displayed_derivation_cannot_reuse_a_different_certificate(rows):
    p = deepcopy(next(r["payload"] for r in rows if r["label"] == "good"))
    last = p["derivation"][-1]
    last["premises"] = [p["leaves"][0]["claim"]]
    result = check_argument(graph_for_payload(p), search=False)
    assert not result.composed
    assert result.errors
    p["root"]["source"] = "true."
    with pytest.raises(ValueError, match="Displayed root"):
        graph_for_payload(p)
