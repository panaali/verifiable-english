"""Asimov extended: authored tie-breaking rules added to the unchanged Asimov v2 rules.

The static tests check that v2 stays unchanged and separate, that every rule
has one reading in plain English, and that the committed `results.json`
agrees with the answer key written before any VE run, except for the findings
the README lists. `test_rerun_equals_the_committed_results` reruns VE on
every case (about seven minutes on 12 workers), so any change in the rules,
the records or VE's behaviour fails.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "asimov-extended"
V2 = REPO / "usecases" / "asimov-laws"
sys.path.insert(0, str(HERE))

import cases  # noqa: E402
import check  # noqa: E402
import reading  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norm_english import render_english  # noqa: E402

KEY = json.loads((HERE / "answer-key.json").read_text())
RESULTS = json.loads((HERE / "results.json").read_text())

# PLAN.md section 1.1: v2 is pinned at commit 2205be39.
V2_PINS = {
    "rules.ve": "6517be81f0133438cac436ee713445fcd7aeb1e685604d866b9eb324dbc2a828",
    "rules.manifest.json": "acfed21b63f063b9d3e1061de8d209ac221ed58d619dbd6009ee68540756d163",
    "environment.json": "9deb0549202d105142cbf3da0b28dd6583bfab144f0a1e344842c1ec7220eeb3",
    "source.md": "751f2c331eff6cdade0a3f9cd2feb22f032c6be7d1d61df3783b9b67e8510330",
}

SCAFFOLDING = ("first clause", "second clause", "end first clause", "end second clause",
               "of the following hold", "the following holds", "(a)", "(b)", "(i)", "(ii)")

# The findings of README "Disagreements and findings": every other comparison agrees with the key.
FINDINGS = {
    "record_disagreements": [],
    "sampled": {"Q1": True, "Q2": True, "Q3": False, "lean_vs_reading": True},
    "Q3_failures": ["Q051", "Q067"],
    "conflict_targets": {"ext": [18, 14], "base": [18, 8]},
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v2_files_are_unchanged():
    assert {name: sha256(V2 / name) for name in V2_PINS} == V2_PINS


def test_base_is_v2_with_the_two_forced_substitutions():
    """B1: `prevents` is rejected in a risk environment (risk.md 2.2), so rules 9 and 13 say `might prevent`."""
    v2 = (V2 / "rules.ve").read_text()
    base = (HERE / "base.ve").read_text()
    substituted = (v2.replace("that action prevents that harm", "that action might prevent that harm", 1)
                   .replace("must be performed prevents that harm", "must be performed might prevent that harm", 1))
    assert base == substituted and base != v2
    assert v2.count(" prevents ") == 2 and " prevents " not in base


def test_base_rules_keep_v2_formulas_and_precedence():
    """B2: rules 1-13 of the extended document have v2's names, guards, carve-outs, consequences and precedence."""
    v2 = [rule.to_dict() for rule in cases.v2_document().rules]
    extended = [rule.to_dict() for rule in cases.document(True).rules]
    assert len(v2) == 13 and extended[:13] == v2
    assert [rule.to_dict() for rule in cases.document(False).rules] == v2


def test_every_rule_has_one_reading_in_plain_english():
    doc = cases.document(True)
    text = cases.source_text()
    manifest = json.loads((HERE / "rules.manifest.json").read_text())
    assert render_english(doc) == (text, manifest)
    assert len(doc.rules) == 29
    assert [marker for marker in SCAFFOLDING if marker in text.lower()] == []
    # The additions are separate from v2, labelled, and come after it.
    assert [rule.name for rule in doc.rules[13:]] == cases.ADDITION_NAMES
    assert all(name.startswith("tie-") for name in cases.ADDITION_NAMES)
    additions = (HERE / "additions.ve").read_text().splitlines()
    assert [line.split(".")[0].split(" (")[0] for line in additions] == [f"Rule {n}" for n in range(14, 30)]


def test_the_environment_extends_v2_without_changing_it():
    v2 = json.loads((V2 / "environment.json").read_text())
    extended = cases.environment()
    for name, predicate in v2["vocabulary"]["predicates"].items():
        assert extended["vocabulary"]["predicates"][name] == predicate, name
    assert extended["alternatives"] == v2["alternatives"]
    assert extended["profiles"] == v2["profiles"] + ["risk@0"]
    new = set(extended["vocabulary"]["predicates"]) - set(v2["vocabulary"]["predicates"])
    derived = {n for n in new if "regulated" in extended["vocabulary"]["predicates"][n]}
    assert new - derived == {"ordered_before", "outranks"}
    for name in derived:
        assert extended["vocabulary"]["predicates"][name]["description"].endswith("(authored, not Asimov's)")
    assert extended["risk"]["severity"]["decided_by"] == "the Asimov extension author"
    assert [h for h, _ in extended["risk"]["harm_classes"]] == list(cases.HARMS)
    Environment(extended)


def test_the_independent_reading_gives_the_answer_key():
    """The reading of `reading.py` was written from the plan's English, before and apart from VE's results."""
    for name, spec in cases.all_records().items():
        expected = KEY["records"][name]
        assert sorted(reading.read(spec, False)["clear"]) == sorted(expected["base"]), name
        assert sorted(reading.read(spec, True)["clear"]) == sorted(expected["ext"]), name


def test_the_committed_results_agree_with_the_answer_key_except_the_listed_findings():
    comparison = check.compare(RESULTS, KEY)
    assert comparison == RESULTS["comparison"]
    assert (comparison["base_agree"], comparison["ext_agree"], comparison["records"]) == (51, 51, 51)
    assert comparison["disagreements"] == FINDINGS["record_disagreements"]
    totals = KEY["totals"]
    assert comparison["categories"] == {k: totals[k] for k in ("UNCHANGED", "RESOLVED", "TIE", "SHARPENED",
                                                               "CHANGED", "DILEMMA")}
    assert all(comparison["document"][k] is True for k in ("ext_conflict", "base_conflict", "ext_followable"))
    assert [comparison["document"]["ext_conflict_targets"],
            comparison["document"]["base_conflict_targets"]] == list(FINDINGS["conflict_targets"].values())
    assert comparison["mutants"] == {f"M{i}": True for i in range(1, 6)}
    assert comparison["sampled"] == FINDINGS["sampled"]
    assert RESULTS["sampled"]["Q3_failures"] == FINDINGS["Q3_failures"]
    records = RESULTS["records"].values()
    assert sum(bool(r["base"]["clear"]) for r in records) == totals["base_clear"]
    assert sum(bool(r["ext"]["clear"]) for r in records) == totals["ext_clear"]
    assert all(all(r["independent_agrees"].values()) for r in records)


def test_each_q3_failure_is_an_order_excused_by_rule_19():
    """Finding: rule 20 counts only a lawful order as valid, so a prevailing order that rule 19 permits
    in a dilemma does not override the other one (PLAN.md section 9, "Order data validity")."""
    specs = check.sampled()
    for name in FINDINGS["Q3_failures"]:
        spec = specs[name]
        ext = reading.read(spec, True)
        assert ext["dilemma"] == "OVER-REQUIRED" and len(ext["required"]) == 2
        # Every action breaks the First Law, so only rule 19 permits the two orders ...
        assert reading.read(spec, False)["permitted"] == []
        # ... and one of them prevails over the other by rules 21-22, but is not a valid order (rule 20).
        assert not check.no_prevailing(spec, ext)


@pytest.mark.skipif(not check.BINARY.exists(), reason="ve_risk_route is not built")
def test_rerun_equals_the_committed_results():
    results = check.compute()
    results["comparison"] = check.compare(results, KEY)
    results.pop("timing")
    committed = {k: v for k, v in RESULTS.items() if k != "timing"}
    assert json.loads(json.dumps(results, sort_keys=True)) == committed
