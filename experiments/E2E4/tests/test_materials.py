from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import json
from pathlib import Path
import re
import pytest
from ve import ArgumentGraph, FiniteModel, Environment
from ve.ast import And
from ve.parser import parse
from ve.search import check_countermodel
from ve.entailment import check_entailment_certificate
from experiments.E2E4.materials import E2_CELLS, E4_CELLS, construction_support, render_cell, replay, validate_e2, load_frozen
from experiments.E2E4 import e2, e4

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def rows():
    return [r for exp in ("E2", "E4") for split in ("dev", "scored") for r in load_frozen(split, exp)]


def test_counts_template_split_and_visibility(rows):
    es = [r for r in rows if r["payload"]["experiment"] == "E2"]
    assert len(es) == 432
    assert Counter(r["split"] for r in es) == {"dev": 144, "scored": 288}
    assert Counter(r["payload"]["_audit"]["error"] for r in es) == {"honest": 144, "invalid_step": 144, "false_leaf": 72, "wrong_specification": 72}
    assert len({r["payload"]["template"] for r in es if r["split"] == "scored"}) == 8
    for experiment in ("E2", "E4"):
        for field in ("template", "family"):
            sets = [{r["payload"][field] for r in rows if r["split"] == s and r["payload"]["experiment"] == experiment} for s in ("dev", "scored")]
            assert not sets[0] & sets[1]
    symbols = defaultdict(set)
    for r in es:
        p = r["payload"]
        symbols[p["family"]].update(p["environment"]["vocabulary"]["predicates"])
        assert len(p["leaves"]) == (p["size"] + 1 if p["workload"] == "growing" else 2)
    families = list(symbols)
    assert all(not symbols[a] & symbols[b] for i, a in enumerate(families) for b in families[i+1:])


def test_all_e2_certificates_links_and_record_labels(rows):
    for row in rows:
        p = row["payload"]
        if p["experiment"] != "E2":
            continue
        assert validate_e2(p) == p["checker_output"]
        kind = p["_audit"]["error"]
        assert len(p["checker_output"]["unresolved_steps"]) == int(kind == "invalid_step")
        assert construction_support(p) == (kind != "false_leaf")
        assert (p["submitted_root"]["source"] == p["intended_source"]) == (kind != "wrong_specification")
        assert (p["checker_output"]["all_local_edges_follow"] and construction_support(p) and p["submitted_root"]["source"] == p["intended_source"]) == (row["label"] == "good")


def inventory(source):
    return Counter(re.findall(r"\w+", source))


def test_invalid_step_same_vocabulary_and_connectives_as_honest(rows):
    honest = {}
    for row in rows:
        p = row["payload"]
        if p["experiment"] == "E2" and row["label"] == "good":
            honest[p["template"], p["family"], p["size"], p["workload"]] = p
    positions = set()
    for row in rows:
        p = row["payload"]
        if p["experiment"] == "E2" and p["_audit"]["error"] == "invalid_step":
            n = p["_audit"]["bad_at"]
            positions.add(n)
            match = honest[p["template"], p["family"], p["size"], p["workload"]]
            assert inventory(p["steps"][n-1]["source"]) == inventory(match["steps"][n-1]["source"])
            assert inventory(p["steps"][n-1]["source"]) <= inventory(" ".join(s["source"] for s in match["steps"]))
    assert len(positions) > 20


def test_checker_prompts_grow_and_all_fol_statements_are_fol(rows):
    groups = defaultdict(dict)
    for row in rows:
        p = row["payload"]
        if p["experiment"] != "E2":
            continue
        direct, fol, ve = [render_cell(row, c) for c in E2_CELLS]
        assert "@a is " not in fol and "@unit" not in fol
        assert direct.count(": from ") == p["size"]
        assert "Full submitted work" not in fol + ve
        assert p["intended_source"].split(" is ")[1].strip(".\n") in fol
        if row["label"] == "good" and p["workload"] == "growing":
            groups[p["template"], p["family"]][p["size"]] = len(ve)
    assert all(g[256] > g[32] > g[4] * 2 for g in groups.values())


def test_tampered_e2_links_certificates_and_sources_fail(rows):
    original = next(r["payload"] for r in rows if r["payload"]["experiment"] == "E2" and r["label"] == "good")
    p = deepcopy(original)
    p["steps"][1]["premises"] = ["fact"]
    with pytest.raises(ValueError, match="link"):
        validate_e2(p)
    p = deepcopy(original)
    p["steps"][1]["source"] = p["intended_source"]
    with pytest.raises(ValueError, match="Displayed step"):
        validate_e2(p)
    p = deepcopy(original)
    check = p["checks"][p["steps"][0]["check_ref"]]
    check["graph"]["deductions"][0]["certificates"][0]["edge_id"] = "forged"
    assert not validate_e2(p)["all_local_edges_follow"]


def test_e4_60_each_scored_quantified_relational_certified_and_dishonest(rows):
    items = [r for r in rows if r["payload"]["experiment"] == "E4"]
    assert Counter((r["split"], r["label"]) for r in items) == {("dev", "good"): 8, ("dev", "bad"): 8, ("scored", "good"): 60, ("scored", "bad"): 60}
    assert len({r["payload"]["template"] for r in items if r["split"] == "scored"}) == 12
    for row in items:
        p = row["payload"]
        assert replay(p["check"]) == p["check"]["result"]
        graph = ArgumentGraph.from_dict(p["check"]["graph"])
        env = graph.env
        premises = [parse(env, s + "\n").formulas[0] for s in p["premises"]]
        conclusion = parse(env, p["conclusion"] + "\n").formulas[0]
        antecedent = premises[0]
        for x in premises[1:]: antecedent = And(antecedent, x)
        oracle = p["oracle"]["a_implies_b"]
        assert "for every" in " ".join(p["premises"]) or "there exists" in " ".join(p["premises"])
        if row["label"] == "good":
            assert oracle["status"] == "ENTAILED"
            assert check_entailment_certificate(env, (antecedent,), conclusion, oracle["certificate"]).valid
        else:
            assert oracle["status"] == "COUNTERMODEL"
            assert check_countermodel(env, premises, conclusion, FiniteModel.from_dict(env, oracle["model"])).valid
        asserted = FiniteModel.from_dict(env, p["asserted_model"])
        assert check_countermodel(env, premises, conclusion, asserted).valid == (row["label"] == "bad")
        assert len({len(v.split()) for v in p["critiques"].values()}) == 1
        assert "unchecked" in render_cell(row, "dishonest_critic")
        assert p["_audit"]["critic_is_dishonest"] == (row["label"] == "good")


def test_no_hidden_labels_and_prompt_contract(rows):
    for row in rows:
        p = {k: v for k, v in row["payload"].items() if not k.startswith("_")}
        cells = E2_CELLS if p["experiment"] == "E2" else E4_CELLS
        for cell in cells:
            text = render_cell(p, cell)
            assert row["id"] not in text and '"_audit"' not in text
            assert text.endswith('{"verdict":"approve"} or {"verdict":"reject"}.')


def test_generation_reproduces_selected_frozen_items(rows):
    selected = {}
    for row in rows:
        p = row["payload"]
        if p["experiment"] == "E4":
            selected.setdefault(("E4", p["template"]), row)
        elif p["size"] == 4:
            selected.setdefault(("E2", p["template"], p["workload"], p["_audit"]["error"]), row)
    for row in selected.values():
        p = row["payload"]
        if p["experiment"] == "E2":
            assert e2.make_item(p["template"], p["family"], p["size"], p["_audit"]["error"], p["workload"]) == row
        else:
            assert row in e4.make_pair(p["template"], p["family"])
