"""Asimov extended: authored tie-breaking rules added to the unchanged Asimov v2 rules.

The static tests check that v2 stays unchanged and separate, that every rule
has one reading in plain English, and that the committed `results.json`
agrees with the answer key written before any VE run, except for the findings
the README lists. `test_rerun_equals_the_committed_results` reruns VE on
every case (about sixteen minutes on 12 workers), so any change in the rules,
the records or VE's behaviour fails.
"""
import hashlib
import json
import sys
from pathlib import Path

from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "asimov-extended"
V2 = REPO / "usecases" / "asimov-laws"
sys.path.insert(0, str(HERE))

import asimov_extended_cases as cases  # noqa: E402
import asimov_extended_check as check  # noqa: E402
import asimov_extended_reading as reading  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norm_english import render_english  # noqa: E402

KEY = json.loads((HERE / "answer-key.json").read_text())
RESULTS = json.loads((HERE / "results.json").read_text())

# PLAN.md section 1.1: v2 formulas and precedence stay pinned; X2 refreshed two wordings.
V2_PINS = {
    "rules.ve": "9d00b09cc9f7fc26aa481244df57e6b96a23abc337c84fd42beb1ec920bde4a5",
    "rules.manifest.json": "67ea9542f9358a1cd3f0844f34fc95d7ecd87eeefd1b4545ba727d7edd881385",
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

# README "The permission default": the records whose statuses change when `permitted` defaults to deny. A record
# can keep its clear set and still lose a permission, so each status is listed on its own (review finding B).
DENY_BASE_CHANGES = [
    "S:a", "S:c-7", "S:o-7", "S:l5", "R:rescue-destroys-robot", "R:self-preservation-without-conflict",
    "R:ordered-unnecessary-injury", "R:unnecessary-injury", "R:unnecessary-allowed-human-harm",
    "R:unrelated-work-while-human-harmed", "R:unrelated-work-while-humanity-harmed", "R:ordered-unrelated-work",
    "R:unavoidable-harm", "R:two-rescues-destroy-robot-differently", "R:two-rescues-destroy-robot-alike",
    "R:two-threats-without-higher-law", "R:two-threats-one-safe-rescue", "R:forced-threat-and-avoidable-threat",
    "R:dominated-action-when-threats-conflict", "P:P1 risky-rescues", "P:P2 certain-injury-vs-possible-death",
    "P:P7 injury-vs-property", "P:P9 unordered-possible-robot-loss", "P:P10 risky-rescue-only",
]
# The v2 records that keep their clear set but lose a permission.
DENY_BASE_PERMISSION_ONLY = [
    "S:d-full", "S:j", "R:obedience-destroys-robot", "R:obedience-destroys-robot-retreat-available",
    "R:ordered-action-preserves-robot", "R:two-orders-destroy-robot-differently", "O:O1 j-earlier",
    "O:O2 j-later-more-authority", "O:O3 j-earlier-more-authority", "O:O4 j-simultaneous-more-authority",
    "O:O5 j-later-authority-risky", "O:O6 j-later-authority-unlawful", "P:P3 ordered-possible-injury",
    "P:P4 ordered-possible-robot-loss",
]
DENY_RECORDS = {
    "clear": {"base": DENY_BASE_CHANGES, "ext": []},
    "permitted": {"base": [n for n in cases.all_records() if n in DENY_BASE_CHANGES + DENY_BASE_PERMISSION_ONLY],
                  "ext": []},
    "required": {"base": [], "ext": []},
    "dilemma": {"base": DENY_BASE_CHANGES, "ext": []},
}
# The sampled records: v2's counts, and the extended records by name with the actions only the default permits.
DENY_SAMPLED = {
    "base": {"clear": 129, "permitted": 208, "required": 0, "dilemma": 118},
    "ext": {"clear": ["Q039", "Q225", "Q290"],
            "permitted": ["Q019", "Q039", "Q117", "Q177", "Q190", "Q225", "Q233", "Q290", "Q292"],
            "required": [], "dilemma": []},
    "ext_permitted_only_by_default": {"Q019": ["nothing"], "Q039": ["a2"], "Q117": ["a1"], "Q177": ["nothing"],
                                      "Q190": ["a3"], "Q225": ["a1"], "Q233": ["a1"], "Q290": ["a2"],
                                      "Q292": ["a1"]},
    "base_clear": 138, "ext_clear": 295,
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v2_artifact_pins():
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
    base = (HERE / "base.ve").read_text()
    assert text.startswith(base + "\n")
    additions = text[len(base) + 1:].splitlines()
    assert [line.split(".")[0].split(" (")[0] for line in additions] == [f"Rule {n}" for n in range(14, 30)]
    assert render_english(cases.document(False)) == (base, json.loads((HERE / "base.manifest.json").read_text()))


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
    """The reading of `asimov_extended_reading.py` was written from the plan's English, before and apart from VE's results."""
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


def test_every_completion_default_is_stated_and_only_permission_allows():
    """Review finding B: a completion default the source does not state must be surfaced. Only `permitted`
    completes to allow; README and source.md name it, and README OPEN lists it."""
    env = cases.environment()
    defaults = {name: p["regulated"]["default"] for name, p in env["vocabulary"]["predicates"].items()
                if "regulated" in p}
    assert {name for name, d in defaults.items() if d == "allow"} == {"permitted"}
    assert set(defaults.values()) == {"allow", "deny"}
    readme = (HERE / "README.md").read_text()
    open_section = readme.split("\n## OPEN\n")[1].split("\n## ")[0]
    assert "**The permission default.**" in open_section
    assert "## The permission default" in readme
    assert "modeling choices" in (HERE / "source.md").read_text()


def test_p9_base_verdict_rests_on_the_permission_default():
    """Review finding B's example: no v2 rule grants P9's actions, so only the default permits them."""
    spec = cases.all_records()["P:P9 unordered-possible-robot-loss"]
    assert reading.read(spec, False)["clear"] == ["nothing", "act"]
    denied = reading.read(spec, False, permission_default="deny")
    assert (denied["permitted"], denied["dilemma"]) == ([], "NONE-PERMITTED")
    assert reading.read(spec, True, permission_default="deny")["clear"] == ["nothing"]


def _sides(read):
    return {side: {name: decisions[side] for name, decisions in read.items()} for side in ("base", "ext")}


def test_the_reading_with_permission_denied_by_default_gives_the_committed_counts():
    """Every status is compared, not only the clear set: in six sampled records the extended rules keep the
    clear action but an unrequired action is permitted only by the default (review finding B)."""
    records, specs = cases.all_records(), check.sampled()
    changes = check.status_changes(_sides(check.read_all(records)),
                                   _sides(check.read_all(records, permission_default="deny")), records)
    assert changes == DENY_RECORDS
    allow, deny = _sides(check.read_all(specs)), _sides(check.read_all(specs, permission_default="deny"))
    changes = check.status_changes(allow, deny, specs)
    assert {status: len(changes[status]["base"]) for status in check.STATUSES} == DENY_SAMPLED["base"]
    assert {status: changes[status]["ext"] for status in check.STATUSES} == DENY_SAMPLED["ext"]
    assert {n: [a for a in allow["ext"][n]["permitted"] if a not in deny["ext"][n]["permitted"]]
            for n in changes["permitted"]["ext"]} == DENY_SAMPLED["ext_permitted_only_by_default"]
    assert sum(bool(deny["base"][k]["clear"]) for k in specs) == DENY_SAMPLED["base_clear"]
    assert sum(bool(deny["ext"][k]["clear"]) for k in specs) == DENY_SAMPLED["ext_clear"]


def test_a_lost_permission_counts_even_when_the_clear_set_stays():
    """Review finding B's example: in Q019 only the default permits `nothing`, which might harm humanity and is
    beaten by the order `a1`; rule 18 does not forbid it, so the clear set stays `a1` either way."""
    spec = check.sampled()["Q019"]
    allowed, denied = reading.read(spec, True), reading.read(spec, True, permission_default="deny")
    assert allowed["clear"] == denied["clear"] == ["a1"]
    assert (allowed["permitted"], denied["permitted"]) == (["nothing", "a1"], ["a1"])
    sides = lambda decision: {side: {"Q019": decision} for side in ("base", "ext")}  # noqa: E731
    changes = check.status_changes(sides(allowed), sides(denied), {"Q019": spec})
    assert changes["clear"]["ext"] == [] and changes["permitted"]["ext"] == ["Q019"]


def test_the_committed_permission_default_results_agree_with_the_reading():
    deny = RESULTS["permission_default_deny"]
    assert deny["records"]["changed"] == DENY_RECORDS
    assert (deny["records"]["records"], deny["records"]["base_clear"], deny["records"]["ext_clear"]) == (51, 13, 49)
    assert deny["records"]["ext_permitted_only_by_default"] == {}
    sampled = deny["sampled"]["changed"]
    assert {status: len(sampled[status]["base"]) for status in check.STATUSES} == DENY_SAMPLED["base"]
    assert {status: sampled[status]["ext"] for status in check.STATUSES} == DENY_SAMPLED["ext"]
    assert deny["sampled"]["ext_permitted_only_by_default"] == DENY_SAMPLED["ext_permitted_only_by_default"]
    assert (deny["sampled"]["base_clear"], deny["sampled"]["ext_clear"]) == (138, 295)
    assert all(deny["sampled"]["ext_clear_when_changed"].values())
    assert deny["records"]["lean_vs_reading_disagreements"] == deny["sampled"]["lean_vs_reading_disagreements"] == []


# The rerun, one section per test so that the sections (and each mutant) run in parallel.
# Corpus scale (8,070 CPU seconds of Lean, 42% of the suite's, docs/testing-profile.md): the
# document checks, the mutants and the 300 sampled records run with `-m nightly` and in
# tools/gate.py; the records section, the 51 records under both rules, runs by default.
needs_lean = pytest.mark.skipif(not check.SERVICE.exists(), reason="the Lean service is not built")


def _plain(value):
    return json.loads(json.dumps(value, sort_keys=True))


@pytest.mark.nightly
@needs_lean
def test_rerun_document_equals_the_committed_results():
    document = check.document_section(cases.environment(), cases.norms(True), cases.norms(False), {})
    assert _plain(document) == RESULTS["document"]


@pytest.mark.nightly
@needs_lean
@pytest.mark.parametrize("name", check.MUTANTS)
def test_rerun_mutant_equals_the_committed_results(name):
    result = check.mutant(name, cases.environment(), cases.norms(True))
    result.pop("seconds")
    assert _plain(result) == RESULTS["mutants"][name]


@needs_lean
def test_rerun_records_equal_the_committed_results():
    env, ext_rules, base_rules, records = cases.environment(), cases.norms(True), cases.norms(False), \
        cases.all_records()
    per_record, lean = check.records_section(env, base_rules, ext_rules, records, {})
    assert _plain(per_record) == RESULTS["records"]
    deny = check.permission_default(env, base_rules, ext_rules, records, lean)
    assert _plain(deny) == RESULTS["permission_default_deny"]["records"]


@pytest.mark.nightly
@needs_lean
def test_rerun_sample_equals_the_committed_results():
    env, ext_rules, base_rules = cases.environment(), cases.norms(True), cases.norms(False)
    specs, sample_lean, result = check.sampled_section(env, base_rules, ext_rules, check.SAMPLE, {})
    assert _plain(result) == RESULTS["sampled"]
    deny = check.permission_default(env, base_rules, ext_rules, specs, sample_lean)
    assert _plain(deny) == RESULTS["permission_default_deny"]["sampled"]


def test_the_committed_comparison_is_the_answer_key_comparison_of_the_committed_sections():
    """With every section equal to the committed one (above), the rerun's comparison is this."""
    assert _plain(check.compare(RESULTS, KEY)) == RESULTS["comparison"]
    assert set(RESULTS) == {"document", "records", "mutants", "sampled", "permission_default_deny",
                            "comparison", "timing"}


def test_the_whole_run_joins_the_sections(monkeypatch):
    """compute(), which writes results.json, is the sections the tests above check."""
    class Pool:
        def __init__(self, *_):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def starmap_async(self, function, jobs):
            return type("Done", (), {"get": lambda _: [function(*job) for job in jobs]})()

        close = join = lambda self: None
    monkeypatch.setattr(check, "multiprocessing", SimpleNamespace(get_context=lambda _: SimpleNamespace(Pool=Pool)))
    monkeypatch.setattr(check, "document_section", lambda *args: {"doc": True})
    monkeypatch.setattr(check, "mutant", lambda name, *_: {"verdict": name, "seconds": 1.0})
    monkeypatch.setattr(check, "records_section", lambda *args: ({"R": 1}, "lean"))
    monkeypatch.setattr(check, "sampled_section", lambda env, b, e, sample, timing: ({"S": sample}, "sample-lean",
                                                                                      {"sampled": sample}))
    monkeypatch.setattr(check, "permission_default", lambda env, b, e, specs, lean: [sorted(specs), lean])
    results = check.compute(sample=7)
    results.pop("timing")
    assert results == {"document": {"doc": True}, "records": {"R": 1},
                       "mutants": {name: {"verdict": name} for name in check.MUTANTS}, "sampled": {"sampled": 7},
                       "permission_default_deny": {"records": [sorted(cases.all_records()), "lean"],
                                                   "sampled": [["S"], "sample-lean"]}}


def test_permission_default_stays_allow_until_norm_defaults_combines_with_risk_and_alternatives():
    """Review finding B's class under norm-defaults@0: the source does not state `allow`, but the case
    needs alternatives@0 and risk@0, which norm-defaults@0 does not combine with yet
    (docs/spec/norm-defaults.md 3.3, integration gap). Python and Lean's risk route both reject the
    switched environment, so the case keeps v2's default and README says why. When this test fails,
    the combination exists: switch `permitted` to `unspecified` and re-run."""
    from tests import lean_routes
    from ve.errors import UnsupportedProfile
    env = cases.environment()
    assert {"alternatives@0", "risk@0"} <= set(env["profiles"])
    switched = json.loads(json.dumps(env))
    switched["profiles"] = sorted({*switched["profiles"], "norm-defaults@0"})
    switched["vocabulary"]["predicates"]["permitted"]["regulated"]["default"] = "unspecified"
    with pytest.raises(UnsupportedProfile, match="Unsupported profile norm-defaults@0"):
        Environment(switched)
    without_risk = {k: v for k, v in switched.items() if k != "risk"}
    without_risk["profiles"] = [p for p in switched["profiles"] if p != "risk@0"]
    with pytest.raises(UnsupportedProfile, match="Unsupported profile norm-defaults@0"):
        Environment(without_risk)
    (row,) = lean_routes.rows("risk", [{"id": "switched", "kind": "risk-elaborate", "environment": switched,
                                        "norms": []}])
    assert (row["status"], row["error"]) == ("error", "UnsupportedProfile: Unsupported profile norm-defaults@0")
    readme = (HERE / "README.md").read_text()
    assert "### Why the default is not `unspecified`" in readme
