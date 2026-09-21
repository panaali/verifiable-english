from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import itertools
import json
import pytest

from experiments.E5.materials import (HERE, CELLS, INSTRUCTIONS, FAMILIES, TEMPLATES, DIFFICULTIES,
    make_split_manifest, split_manifest, make_pair, graph_for_payload, grounding_audit, read_record,
    topology_for, render_cell, sense_panel, parse_memo, packed)
from experiments.E5.leak_audit import tokens
from ve.argument import ArgumentGraph, check_argument
from ve.search import check_countermodel


@pytest.fixture(scope="module")
def rows():
    return [json.loads(line) for split in ("dev", "scored") for line in gzip.decompress((HERE / f"{split}.jsonl.gz").read_bytes()).decode().splitlines()]


def canonical_topology(dag):
    n = len(dag)
    return min(tuple(sorted((m[i], tuple(sorted(m[p] for p in parents))) for i, parents in enumerate(dag, 1)))
               for perm in itertools.permutations(range(1, n)) for m in [{0: 0, n: n, **dict(zip(range(1, n), perm))}])


def test_inventory_splits_and_distinct_structures(rows):
    assert len(rows) == 3072
    assert len({r['id'] for r in rows}) == len(rows)
    assert split_manifest() == json.loads(json.dumps(make_split_manifest()))
    for split, n, templates in (("dev", 768, 8), ("scored", 2304, 24)):
        selected = [r for r in rows if r["split"] == split]
        assert len(selected) == n
        assert len({r["payload"]["_audit"]["template"] for r in selected}) == templates
        for d, cfg in DIFFICULTIES.items():
            topologies = {canonical_topology(topology_for(r["payload"]["_audit"]["template"], cfg.graph_size)) for r in selected if r["payload"]["_audit"]["difficulty"] == d}
            assert len(topologies) == templates
    for field in ("template", "vocabulary_family"):
        sets = [{r["payload"]["_audit"][field] for r in rows if r["split"] == s} for s in ("dev", "scored")]
        assert not sets[0] & sets[1]
    for r in rows:
        assert split_manifest()["groups"][r["group"]] == r["split"]


def test_seeded_generator_matches_frozen_materials(rows):
    # At least one primary/control and GOOD/BAD per family/level/split.
    sampled = {}
    for row in rows:
        a = row["payload"]["_audit"]
        sampled.setdefault((row["split"], a["difficulty"], a["family"], a["control"]), row)
    for row in sampled.values():
        a = row["payload"]["_audit"]
        pair = make_pair(a["template"], a["vocabulary_family"], a["family"], a["control"], a["difficulty"])
        generated = next(r for r in pair if r["id"] == row["id"])
        assert generated == row


def test_records_and_approval_labels_proved_from_visible_content(rows):
    strata = defaultdict(Counter)
    for row in rows:
        p, a = row["payload"], row["payload"]["_audit"]
        audit = grounding_audit(p)
        assert audit["label"] == a["grounding_label"]
        assert {reason for _, reason in audit["issues"]} == ({a["family"]} if a["grounding_label"] == "bad" else set())
        assert row["label"] == ("good" if a["grounding_label"] == "good" and a["control"] == "none" else "bad")
        cfg = DIFFICULTIES[a["difficulty"]]
        assert all(len(l["evidence_ids"]) == cfg.records_per_leaf for l in p["leaves"])
        cited = {eid for leaf in p["leaves"] for eid in leaf["evidence_ids"]}
        assert len(p["records"]) - len(cited) == cfg.distractors
        if p["record_format"] == "prose":
            assert all(parse_memo(r["memo"]) == r["data"] for r in p["records"])
        for r in p["records"]:
            if r["data"]["kind"] == "catalog":
                # Both interpretations are present; applicability requires the selector.
                assert {pr["profile"] for pr in r["data"]["profiles"]} == {"talven", "velora"}
        strata[row["split"], a["difficulty"], a["family"], a["stratum"]][a["grounding_label"]] += 1
    assert all(c["good"] == c["bad"] for c in strata.values())


def test_record_solver_uses_prose_not_hidden_fields(rows):
    p = deepcopy(next(r["payload"] for r in rows if r["label"] == "good" and r["payload"]["record_format"] == "prose"))
    selected = p["leaves"][0]["evidence_ids"][1]
    record = next(r for r in p["records"] if r["record_id"] == selected)
    record["memo"] = record["memo"].replace("snapshot 2031-04-18", "snapshot 2031-04-19")
    assert grounding_audit(p)["label"] == "bad"
    # Dates remain valid; a snapshot difference is an explicit version mismatch.
    assert {reason for _, reason in grounding_audit(p)["issues"]} == {"scope_mismatch"}


def test_all_logical_artifacts_replay_and_positions_vary(rows):
    raw = gzip.decompress((HERE / "certificates.jsonl.gz").read_bytes()).decode()
    positions = defaultdict(set)
    for line in raw.splitlines():
        row = json.loads(line)
        graph = ArgumentGraph.from_dict(row["graph"])
        result = check_argument(graph, search=False)
        assert not result.errors
        assert result.composed == (row["control"] == "none")
        if row["control"] != "none":
            gap = next(e for e in graph.deductions if e.countermodels)
            positions[row["control"]].add(gap.name)
            claims = {c.name: c for c in graph.claims}
            conclusion = claims[gap.conclusion].ast
            assert not check_countermodel(graph.env, (conclusion,), conclusion, gap.countermodels[0]).valid
    assert all(len(v) >= 5 for v in positions.values())
    for difficulty in ("medium", "hard"):
        selections = [r["data"]["profile"] for row in rows if row["payload"]["_audit"]["difficulty"] == difficulty
                      for r in row["payload"]["records"] if r["data"]["kind"] == "selection"]
        assert set(selections) == {"talven", "velora"}
        assert .4 < selections.count("talven") / len(selections) < .6
    for difficulty in DIFFICULTIES:
        items = [r for r in rows if r["payload"]["_audit"]["difficulty"] == difficulty]
        assert len({r["payload"]["_audit"]["flawed_leaf"] for r in items}) >= 5
        assert len({next(i for i, rec in enumerate(r["payload"]["records"]) if rec["record_id"] == r["payload"]["_audit"]["flawed_record"]) for r in items}) >= 5


def test_every_displayed_graph_bound_to_replayed_certificate(rows):
    for row in rows:
        p = row["payload"]
        graph = graph_for_payload(p)
        result = check_argument(graph, search=False)
        assert not result.errors
        assert result.composed == p["checker"]["composed"]
        assert result.status == p["checker"]["status"]
        assert graph.graph_id == p["_audit"]["graph_id"]
        assert 3 <= len(graph.claims) <= 12
        assert sum("gap" in f for f in result.findings.values()) == int(p["_audit"]["invalid_deduction"])


def test_forged_tags_and_raw_panels_no_answer_flags(rows):
    merged = Counter()
    for row in rows:
        p, a = row["payload"], row["payload"]["_audit"]
        if a["family"] == "merged_vocabulary" and a["grounding_label"] == "bad":
            merged[row["split"], a["difficulty"], a["stratum"], a["tag_condition"]] += 1
            victim = next(r for r in p["records"] if r["record_id"] == a["flawed_record"])
            leaf = next(l for l in p["leaves"] if l["claim"] == a["flawed_leaf"])
            selector = next(r for r in p["records"] if r["record_id"] == leaf["evidence_ids"][0])
            selected_profile = read_record(selector, p["record_format"]).get("profile", "talven")
            stated = next(pr for pr in read_record(victim, p["record_format"])["profiles"] if pr["profile"] == selected_profile)
            term = next(t for t, meaning in stated["meanings"].items() if "security assurance" in meaning)
            tag = victim["tags"][selected_profile][term]
            assert tag.endswith(":0" if a["tag_condition"] == "forged" else ":1")
        if a["grounding_label"] == "good":
            for record in p["records"]:
                for profile in read_record(record, p["record_format"]).get("profiles", []):
                    for term, meaning in profile["meanings"].items():
                        assert record["tags"][profile["profile"]][term].endswith(":1" if "security assurance" in meaning else ":0")
        for cell in CELLS:
            text = render_cell(row, cell)
            assert not any(flag in text for flag in ("scope_matches_target", "binding_mismatch", "differing_evidence_senses", "_audit", "grounding_label", row["id"]))
            expected = "Badge: proof checked (Checked)." if p["checker"]["composed"] else "Badge: proof not checked (Incomplete)."
            assert (expected in text) == (cell != "a")
            assert render_cell(row, cell, "neutral").split("\n", 1)[1] == text.split("\n", 1)[1]
        assert all(set(r) == {"record", "profile", "predicate", "declared_sense", "record_tag"} for r in sense_panel(p))
    for key, n in merged.items():
        assert merged[(*key[:-1], "forged" if key[-1] == "honest" else "honest")] == n


def test_matched_pairs_all_cells_and_audit_artifact(rows):
    pairs = defaultdict(list)
    for row in rows:
        pairs[row["payload"]["_audit"]["pair"]].append(row)
    for pair in pairs.values():
        for cell in CELLS:
            a, b = [render_cell(r, cell) for r in pair]
            assert a != b
            assert len(a) == len(b)
            assert tokens(a) == tokens(b)
    report = json.loads((HERE / "leak-report.json").read_text())
    assert report["input_sha256"] == {s: hashlib.sha256((HERE / f"{s}.jsonl.gz").read_bytes()).hexdigest() for s in ("dev", "scored")}
    assert report["renderer_sha256"] == hashlib.sha256((HERE / "materials.py").read_bytes()).hexdigest()
    assert set(report["cells"]) == set(CELLS)
    for metrics in report["cells"].values():
        assert set(metrics["scored_accuracy"]) == {"char_1_5", "char_6_12", "word_1_3", "counts_positions_dates_lengths"}
        assert metrics["train_n"] == 384 and metrics["test_n"] == 1152


def test_knob_ranges_and_odd_total_claim_counts():
    for n in range(3, 13):
        for k in (1, 2, 3, 4):
            pair = make_pair("chain3", "dev_cinder", "merged_vocabulary", "none", "easy",
                graph_size=n, records_per_leaf=k, distractors=(n+k)%9, flaw_spread=k > 1, record_format="prose")
            assert len(graph_for_payload(pair[0]["payload"]).claims) == n
            assert grounding_audit(pair[0]["payload"])["label"] == "good"
            assert grounding_audit(pair[1]["payload"])["label"] == "bad"
    with pytest.raises(ValueError):
        make_pair("chain3", "dev_cinder", "scope_mismatch", difficulty="hard", records_per_leaf=1)


def test_display_tampering_cannot_reuse_certificate(rows):
    p = deepcopy(next(r["payload"] for r in rows if r["label"] == "good"))
    p["derivation"][-1]["premises"] = []
    result = check_argument(graph_for_payload(p), search=False)
    assert not result.composed and result.errors
    p["root"]["source"] = "true."
    with pytest.raises(ValueError, match="Displayed root"):
        graph_for_payload(p)
