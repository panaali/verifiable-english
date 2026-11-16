"""fid-mech-b4: the wording generator moved into VE (plan 9), its harness mode and the actors.json matcher (plan 5.2).

The golden file holds manage-agents tools-local/wording-mutants.py's plan() for seeds 1-5 (n = 10) on frozen copies
of the three documents' inputs, and the sha256 of each file apply() writes for each planned mutant. The two tests that
check a mutant's parse ask Lean and are marked `needs_lean` (as tests/test_fidmech_adapters.py marks its live test).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.fidmech import mutants as M
from tools.fidmech import wording as W

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data" / "fidmech"
LEAN_SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
needs_lean = pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
GOLDEN = json.loads((DATA / "wording-golden.json").read_text(encoding="utf-8"))
DOCUMENTS = sorted(GOLDEN["documents"])


def inputs(document):
    return {p.name[:-4] if p.name.endswith(".py.txt") else p.name: p.read_text(encoding="utf-8")
            for p in sorted((DATA / "wording-inputs" / document).iterdir())}


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.mark.parametrize("document", DOCUMENTS)
def test_plan_and_apply_give_the_bundles_output_on_the_frozen_inputs(document):
    files = inputs(document)
    row = GOLDEN["documents"][document]
    assert {n: sha(t) for n, t in files.items()} == row["input_sha256"]
    units = list(W._blocks(files["rules.d1.ve"])[0])
    for seed in GOLDEN["seeds"]:
        planned = W.plan(files, units, GOLDEN["n"], seed)
        assert planned == row["seeds"][str(seed)]["plan"], (document, seed)
        applied = [{n: sha(t) for n, t in sorted(W.apply(files, [m]).items())} for m in planned]
        assert applied == row["seeds"][str(seed)]["apply_sha256"], (document, seed)


def test_actors_is_unchanged():
    assert hashlib.sha256(json.dumps(W.ACTORS).encode()).hexdigest() == hashlib.sha256(json.dumps([
        'the Responsible Scaling Officer', 'the external reviewers', 'external reviewers', 'the Board', 'the LTBT',
        'the CEO', 'the RSO', 'the company', 'regular-clearance employees', 'full-time employees', 'employees',
        'the public', 'the government', 'reviewers', 'Anthropic']).encode()).hexdigest()


@pytest.mark.parametrize("document, unit, actor", [
    ("openai-preparedness", "f7-compile", "the SAG"),
    ("safety-framework", "f14", "governance function"),
])
def test_the_actors_json_matcher_finds_an_actor_the_legacy_list_cannot(document, unit, actor):
    files = inputs(document)
    actors = W.load_actors(ROOT / "usecases" / document / "fidmech" / "actors.json")
    assert actor in actors and actor not in W.ACTORS
    legacy = [c for c in W.candidates(files, unit, W.case_actor_list(files)) if c[0] == "actor"]
    harness = [c for c in W.harness_candidates(files, unit, actors) if c[0] == "actor"]
    assert legacy == [] and any(c[1] == "act" and c[3] == actor for c in harness), harness


def test_the_matcher_reads_a_first_letter_in_either_case_and_nothing_else():
    pattern = W.actor_pattern("the SAG")
    assert pattern.search("The SAG decides") and pattern.search("asks the SAG")
    assert not pattern.search("the sag") and not pattern.search("the SAGE")


def test_an_actors_json_whose_list_is_not_generated_less_removed_plus_added_is_refused(tmp_path):
    data = {"schema": "fidmech-actors/1", "document": "x", "generated": ["the Board", "AI"],
            "removed": [{"phrase": "AI", "reason": "not a party"}], "added": [{"phrase": "Google", "reason": "r"}],
            "actors": ["the Board", "Google"]}
    path = tmp_path / "actors.json"
    path.write_text(json.dumps(data))
    assert W.load_actors(path) == ["the Board", "Google"]
    path.write_text(json.dumps({**data, "actors": ["the Board", "Google", "AI"]}))
    with pytest.raises(ValueError, match="generated - removed"):
        W.load_actors(path)


@pytest.mark.parametrize("document", DOCUMENTS)
def test_the_committed_actors_json_is_consistent(document):
    assert W.load_actors(ROOT / "usecases" / document / "fidmech" / "actors.json")


def fixture_case():
    """The frozen RSP vocabulary and environment with the structural fixture's five rule blocks and the frozen rules'
    f13-redact-p block (an act whose actor replacement VE refuses)."""
    files = inputs("anthropic-rsp")
    lines = files["rules.d1.ve"].splitlines(keepends=True)
    at = next(i for i, text in enumerate(lines) if text.startswith("## f13-redact-p |"))
    files["rules.d1.ve"] = (DATA / "structural" / "anthropic-rsp" / "rules.d1.ve").read_text(encoding="utf-8") \
        + "".join(lines[at:at + 2])
    return files


@needs_lean
def test_wording_mutants_are_scored_never_equivalent_and_stillborn_ones_are_listed():
    """An actor-replaced act is a scored mutant with no equivalence; an act VE refuses is listed, never scored."""
    from ve.softnorms import SoftEnvironment
    files = fixture_case()
    actors = W.load_actors(ROOT / "usecases" / "anthropic-rsp" / "fidmech" / "actors.json")
    records, report = M.wording_mutants("anthropic-rsp", files, actors,
                                        parse_env=lambda text: SoftEnvironment(json.loads(text)))
    assert records and all(r["class"] == "wording" and r["equivalent"] is None for r in records)
    by_id = {r["id"]: r for r in records}
    swap = by_id["anthropic-rsp:rows-cond:actor:1"]
    assert swap["where"] == "act" and swap["parse"] == "ok" and swap in M.scorable(records)
    assert any("the plans of regular-clearance staff about each threshold" in e["replace"] for e in swap["edits"])
    dead = {s["id"]: s["reason"] for s in report["stillborn"]}
    assert list(dead) == ["anthropic-rsp:f13-redact-p:actor:1"] and "invalid act phrase" in next(iter(dead.values()))
    assert by_id["anthropic-rsp:f13-redact-p:actor:1"]["parse"] == "stillborn"
    assert by_id["anthropic-rsp:f13-redact-p:actor:1"] not in M.scorable(records)
    for rec in records:
        for edit in rec["edits"]:
            assert files[edit["file"]].count(edit["find"]) == 1
