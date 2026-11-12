"""Safety-framework use case (usecases/safety-framework): fails on any mismatch with the answer key
or any change in what VE computes.

The answer key is PLAN.md section 6, transcribed into answer-key.json before VE
was run, and pinned here by hash. The recorded disagreements (RECORDED_DISAGREEMENTS) are findings
documented in README.md and PLAN section 12; the key is never edited to match VE.
`test_rerun_equals_committed_results` recomputes every result with VE.
"""
import hashlib
import importlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "safety-framework"
# usecases/eligibility has modules with the same bare names (run, reference, translation), and
# both use cases import their siblings lazily by those names. This use case's modules are loaded
# apart and stand in sys.modules only while its own tests run.
OWN_NAMES = ("vocabulary", "translation", "run", "reference", "severity_and_dates", "build_document",
             "readings_r1", "measure_r1", "measure_r2")


def _load_own_modules():
    saved = {name: sys.modules.pop(name) for name in OWN_NAMES if name in sys.modules}
    sys.path.insert(0, str(HERE))
    try:
        return {name: importlib.import_module(name) for name in OWN_NAMES}
    finally:
        for name in OWN_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


OWN = _load_own_modules()
build_document, reference, run = OWN["build_document"], OWN["reference"], OWN["run"]
readings_r1, measure_r1, measure_r2 = OWN["readings_r1"], OWN["measure_r1"], OWN["measure_r2"]
translation, vocabulary = OWN["translation"], OWN["vocabulary"]


@pytest.fixture(autouse=True)
def _own_modules(monkeypatch):
    for name, module in OWN.items():
        monkeypatch.setitem(sys.modules, name, module)

KEY_SHA256 = "8fbb04753730ca894789b6c2a90e6fd1916c0a90ba0e609cecca2c5398e0ce0e"
RESULTS = json.loads((HERE / "results.json").read_text())
RECORDED_DISAGREEMENTS = {
    # Key cells both uc-auditors found wrong (PLAN 12 item 23, fsf-fidelity-fix): they name RS9 = same, a reading
    # the text excludes (footnote 5), so they describe no admissible choice; the section-12 answer is NONE.
    "C3", "C-doc",
}
# The rules only an excluded reading selected (PLAN 12 "Excluded readings").
EXCLUDED_RULES = {"f10-dm-same", "f10-rel-same", "f15-same"}


def test_answer_key_is_the_transcription():
    data = (HERE / "answer-key.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() == KEY_SHA256
    items = json.loads(data)["items"]
    assert len(items) == 262
    assert Counter(i["id"][0] for i in items) == {"A": 160, "B": 40, "K": 18, "S": 12, "R": 11, "G": 9,
                                                  "C": 6, "N": 3, "D": 3}
    a = Counter(i["key"].split("(")[0] for i in items if i["id"].startswith("A-"))
    assert a == {"ALL": 25, "SOME": 67, "NONE": 68}
    b = Counter(i["key"].split("(")[0] for i in items if i["id"].startswith("B-"))
    assert b == {"ALL": 13, "SOME": 5, "NONE": 22}


def test_environment_file_is_generated():
    assert (HERE / "environment.d1.json").read_text() == vocabulary.text()


def test_every_rule_and_premise_parses_with_one_reading():
    for block in translation.rule_blocks():
        assert json.loads(translation.parsed_rule(block.id))["name"] == block.id
    assert sum(len(f) for _, _, f in translation.facts()) == RESULTS["cost"]["premises"]


def test_results_agree_with_the_key_except_the_recorded_findings():
    rows = RESULTS["comparison"]
    assert len(rows) == 262
    assert {r["id"] for r in rows if not r["agree"]} == RECORDED_DISAGREEMENTS
    assert sum(r["agree"] for r in rows) == 260
    # The section-12 deviation entries (key untouched): C1, C3 and C-doc are NONE, and the run agrees with each.
    deviations = {r["id"]: r["deviation"] for r in rows if "deviation" in r}
    assert deviations == {i: {"plan_12": 23, "answer": "NONE", "agree": True} for i in ("C1", "C3", "C-doc")}
    assert all(r["ve"] == "NONE" for r in rows if r["id"] in deviations)
    # The comparison is recomputed from the committed results and the key.
    recomputed = run.compare(RESULTS)
    assert [r for r in rows if r["id"] in {x["id"] for x in recomputed}] == recomputed


def test_reference_reading_agrees_with_the_key_and_with_ve():
    out = reference.main()
    assert out["compared"] == 208
    assert sorted(out["items_differ"]) == sorted(i for i in RECORDED_DISAGREEMENTS if i.startswith("C"))
    assert out["rel_notes_differ"] == sorted(f"{i} (REL)" for i in RECORDED_DISAGREEMENTS if "INT/DM" in i)


def test_metrics():
    assert RESULTS["lint"]["violations"] == []
    assert RESULTS["invention_audit"]["untraced"] == []
    assert all(not v["mismatch"] for v in RESULTS["default_sensitive"].values())
    assert RESULTS["items"]["N3"]["without_witness"] == []
    variants = RESULTS["variants"]
    assert [c for c, d in variants["m1"]["C2"]["details"].items() if d["status"] == "CONFLICT"] == ["RS7=E"]
    assert variants["m2"]["N2_entailed"] and not variants["m2"]["traced_to_source"]
    assert RESULTS["d2_d3"]["m3"]["S4"] == "ALL"
    assert variants["m4"]["premises_inconsistent"]
    assert [c for c, d in variants["m5"]["C5"]["details"].items() if d["status"] == "CONFLICT"] == ["RS2=U"]
    assert all(v == "SOME(RS1=G)" for k, v in variants["m6"].items() if k != "C3")
    # PLAN 11's m6: C3 disappears once DM-h and DM-s are two acts (footnote 5; RS9 = same excluded).
    assert variants["m6"]["C3"] == "NONE"
    # With the withdrawn N2, F16 is a default rule at both forces and C1 is conflict-free.
    assert all(d["status"] == "CONFLICT-FREE" for d in variants["with_N2"]["C1"]["details"].values())
    # M7: a completed outcome depends on the default exactly at the silent or conflicted cells; the only
    # conflicted cells came from RS6 = same (F15 against a strict F16), which the text excludes.
    assert {k for k, v in RESULTS["default_sensitive"].items() if v["conflicted_choices"]} == set()
    # PLAN 6.1: under the RS0 prediction reading (without N1) nothing is required, so every item is NONE
    # (fsf-fidelity-fix review F1: B-L5/PRA was ALL while f17-hri was missing from the "will" rules).
    without_n1 = {v["item"]: v["without_N1"] for v in variants["without_N1"]}
    assert len(without_n1) == 8 and set(without_n1.values()) == {"NONE"}, without_n1


def test_span_accounting_is_complete():
    coverage = json.loads((HERE / "coverage.json").read_text())
    assert coverage["source_bytes"] == coverage["accounted_bytes"] == build_document.TEXT_BYTES
    assert sum(coverage["bytes_by_status"].values()) == build_document.TEXT_BYTES
    assert sum(coverage["master_bytes_by_status"].values()) == build_document.TEXT_BYTES
    spans = json.loads((HERE / "spans.json").read_text())["units"]
    assert spans[0]["span"][0] == 0 and spans[-1]["span"][1] == build_document.TEXT_BYTES
    assert all(a["span"][1] == b["span"][0] for a, b in zip(spans, spans[1:]))
    if build_document.DEFAULT_SOURCE.exists():
        assert build_document.main(["--check"]) == 0


@pytest.mark.skipif(not OWN["severity_and_dates"].RISK_ROUTE.exists(), reason="the Lean service is not built")
def test_rerun_equals_committed_results():
    assert run.main(["--check"]) == 0


# --- regressions from the results review (manage-agents/safety-framework-review.final.md) -----

def test_premises_leave_every_level_open_to_its_decider():
    """Finding A: "For CCLs, we define alert thresholds" became a premise that only CCLs have
    them. Whether a model has reached a level or its alert threshold is open term OT1: no premise
    may settle it for any level, so each such finding alone is consistent with the premises."""
    open_level_terms = {"reached", "approaches"}
    for _, _, formulas in translation.facts():
        for formula in formulas:
            assert not run.predicates_of(formula) & open_level_terms, formula
    for level in vocabulary.LEVELS:
        for predicate in open_level_terms:
            assert run.premise_status(frozenset({(predicate, "p", level)}))[0] == "model", (predicate, level)
    for case_id in ("K2-L1", "K2-L5", "G3"):
        assert RESULTS["premises"][case_id]["status"] == "model"
    rows = {r["id"]: r for r in RESULTS["comparison"]}
    assert rows["K2-L1/PROXIMITY"]["agree"] and rows["K2-L5/PROXIMITY"]["agree"] and rows["G3"]["agree"]


def test_every_should_keeps_its_strict_reading():
    """Finding B: the field's "should" (F16, RS3 = Ds) was narrowed to a default rule. Stated
    exceptions fit a strict rule too, so every "should" or "must" of RS3 and RS4 keeps both forces:
    each default rule has a strict sibling on the same act whose choice differs only in force."""
    blocks = translation.rule_blocks()
    for block in blocks:
        if " should " not in block.text or dict(block.when).get("RS4aim"):
            continue  # "we aim to" is a default norm or an intent (RS4aim), not a force word
        force_sets = [s for s, v in block.when if v == "default"]
        assert force_sets, block.id
        sibling_when = {(s, "strict" if s in force_sets else v) for s, v in block.when}
        siblings = [b for b in blocks if set(b.when) == sibling_when
                    and run.rule_predicate(b.id) == run.rule_predicate(block.id)]
        assert len(siblings) == 1 and " must " in siblings[0].text, block.id
    assert translation.READING_SETS["RS3force"] == ("strict", "default")
    # F15 (insider misuse) and F16 (security measures) name two acts, so neither force conflicts with F15 (C1).
    details = RESULTS["items"]["C1"]["details"]
    assert {d["status"] for d in details.values()} == {"CONFLICT-FREE"} and len(details) == 4
    assert reference.family_c_g()["C1"] == ("NONE", [])


def test_build_check_writes_nothing_beside_the_source(tmp_path):
    """`build_document.py --check` must run against a read-only copy of the pinned source."""
    if not build_document.DEFAULT_SOURCE.exists():
        pytest.skip("the pinned source is not stored on this machine")
    source = tmp_path / "fsf-3.1.txt"
    source.write_bytes(build_document.DEFAULT_SOURCE.read_bytes())
    tmp_path.chmod(0o555)
    try:
        assert build_document.main(["--source", str(source), "--check"]) == 0
        assert sorted(p.name for p in tmp_path.iterdir()) == ["fsf-3.1.txt"]
    finally:
        tmp_path.chmod(0o755)


# --- fsf-r1: reading sets with content (docs/usecases/safety-framework/fsf-r1/REPORT.md) -----------

def test_a_set_carries_content_exactly_when_each_reading_is_one_rule_and_that_rule_is_its_content():
    """Each content-bearing set's candidates are the translation's own rules, nothing else: one per reading, with
    the reading's rule of rules.d1.ve as its content under one shared rule name; every other set stays pending."""
    from ve.softnorms import SoftEnvironment
    env = SoftEnvironment(build_document.environment())
    content = set()
    for set_id, (_, choices) in build_document.READINGS.items():
        single = all(len(rules) == 1 and " or " not in rules[0] for rules in choices.values())
        assert build_document.content_bearing(set_id) is single
        if not single:
            continue
        content.add(set_id)
        word = build_document.FORCE_WORDS.get(set_id, "x")
        source = f"Text {word} here.".encode()
        reading_set = build_document.content_set(env, set_id, "u", [0, len(source)], source)
        assert [r["id"] for r in reading_set["readings"]] == list(choices)
        for reading in reading_set["readings"]:
            norm = dict(reading["content"]["norm"])
            assert norm.pop("name") == set_id.replace("_", "-")
            expected = json.loads(translation.parsed_rule(choices[reading["id"]][0]))
            expected.pop("name")
            assert norm == expected
        if set_id in build_document.FORCE_WORDS:
            start, stop = reading_set["source_word"]
            assert source[start:stop].decode() == word
    assert content == {"rs2_misuse", "rs2_ml_rd", "rs4_holistic", "rs4_within", "rs4_elicitation"}
    saved = json.loads((HERE / "readings" / "results.json").read_text())["sets"]
    assert {s for s, v in saved.items() if v["content"]} == content


def test_ve_decides_every_content_bearing_set_and_keeps_its_unit_open():
    """readings/results.json as `readings_r1.py` wrote it: VE (Lean) admitted each part document, found its readings
    CONFLICT-FREE with a checked model of its premises, and showed a separation; the unit stays OPEN. The whole
    document's verdict stays UNKNOWN while any set has a pending reading."""
    saved = json.loads((HERE / "readings" / "results.json").read_text())
    for set_id, entry in saved["sets"].items():
        if not entry["content"]:
            assert entry["pending"] and "refused" not in entry, set_id
            continue
        assert (entry["status"], entry["premises"], entry["route"], entry["conflict"]) == (
            "OPEN", "model", "superposed", "CONFLICT-FREE"), set_id
        assert [sorted(p["readings"]) for p in entry["pairs"]] == [sorted(entry["rules"])], set_id
    whole = saved["whole_document"]
    assert (whole["route"], whole["premises"]) == ("pending", "UNKNOWN")
    assert whole["residual"]["separations"] == sum(v["content"] for v in saved["sets"].values())


@pytest.mark.skipif(not OWN["severity_and_dates"].RISK_ROUTE.exists(), reason="the Lean service is not built")
def test_readings_rerun_equals_committed_readings():
    """The part documents are cut from the pinned source, which the gate runner does not store (tools/gate-optional.json)."""
    if not build_document.DEFAULT_SOURCE.exists():
        pytest.skip("the pinned source is not stored on this machine")
    assert readings_r1.main(["--check"]) == 0


def test_every_unit_and_item_is_measured_once():
    """measure_r1: every byte is in one unit, every answer-key item is attributed to the units whose rules decide
    it or to none, a CHECKED unit has no blocker and every other unit at least one known feature."""
    units, rest = measure_r1.measure()
    assert sum(u["bytes"] for u in units) == build_document.TEXT_BYTES
    rows = {r["id"]: r for r in RESULTS["comparison"]}
    assert rest["answer_key"] == {"items": len(rows), "agree": sum(r["agree"] for r in rows.values())}
    disagree = set(rest["items_disagree"]).union(*(u["items_disagree"] for u in units))
    assert disagree == {i for i, r in rows.items() if not r["agree"]}
    for u in units:
        assert (u["status"] == "CHECKED") is (u["blockers"] == []), u["id"]
        assert "unknown" not in u["blockers"], u["id"]
        assert u["items_agree"] + len(u["items_disagree"]) == u["items"], u["id"]
    open_terms = {u["id"] for u in json.loads((HERE / "spans.json").read_text())["units"] if u.get("open_terms")}
    assert {u["id"] for u in units if "judgment terms" in u["blockers"] and u["status"] == "OPEN"} == open_terms


# --- fsf-r2 (2026-10-28): re-measured after jt-2/jt-2b, df-1b/df-1bb and sc-5r/sc-5rb ----------------------------

FSF_R2 = REPO / "docs" / "usecases" / "safety-framework" / "fsf-r2"


def test_fsf_r2_measures_every_unit_as_saved_and_none_moved_since_oct18():
    """fsf-r2's saved units.json and gaps.json (measure_r2's measurement of the Oct 28 translation): every unit has
    its Oct 18 status and every feature a family. They are batch evidence, read as saved (D4): fsf-fidelity-fix
    changed the translation since, so a live measurement no longer equals them."""
    units = json.loads((FSF_R2 / "units.json").read_text())
    gaps = json.loads((FSF_R2 / "gaps.json").read_text())
    r1 = {u["id"]: u for u in json.loads((measure_r1.EVIDENCE / "units.json").read_text())["units"]}
    assert [u["id"] for u in units["units"]] == list(r1)
    assert all(u["status"] == u["status_oct18"] == r1[u["id"]]["status"] for u in units["units"])
    assert gaps["units_changed_status_since_oct18"] == []
    assert gaps["master_bytes_by_status"]["today"] == gaps["master_bytes_by_status"]["oct18"]
    families = {"JT", "DF", "SC", "QT", "ET", "AP", "WG", "AT", "external reference", "readings", "no claim to check"}
    assert set(gaps["features"]) == set(measure_r2.FAMILIES)
    assert all(f["family"] in families for f in gaps["features"].values())


def test_fsf_r2_probes_record_lean_s_answer_on_each_merged_item():
    """The saved probes: judgments@0 beside soft-norms@0 refused by the soft chain's own composition check (PC-1 composes
    the layer; D1's environment waits for PC-2a/2b) and a judged unit OPEN where admitted; the defaults flag refused
    on an open reading set; RS8's set refused on its governor's own unit."""
    probes = json.loads((FSF_R2 / "probes.json").read_text())
    assert probes["JT-a"]["diagnostic"] == ("CheckerUnavailable: soft-norms with readings, alternatives or risk needs "
                                            "its composed Lean route")
    assert probes["JT-b"]["diagnostic"] == "JudgmentUnbound: ot1_level_reached"
    for probe in ("JT-c", "JT-d", "SC-b", "SC-d"):
        assert probes[probe]["admitted"] and set(probes[probe]["units"].values()) == {"OPEN"}, probe
    assert len(probes["JT-d"]["units"]) == 8
    assert {u for row in probes["JT-d"]["judgments"]["used"] for u in row["units"]} == set(probes["JT-d"]["units"])
    assert not probes["DF-a"]["admitted"] and probes["DF-a"]["status"]["units"] == {"s135-holistic": "OPEN"}
    assert probes["DF-c"]["answer"]["verdict"] == "UNKNOWN"
    assert probes["DF-c"]["status"] == {"admitted": True, "units": {"s135-holistic": "CHECKED"}}
    assert probes["SC-c"]["diagnostic"] == "ScopeReadings: s135-bullet2-only"



# --- fsf-fidelity-fix (2026-11-12): readings the source excludes (DRI decision 2026-10-29 uc-audit2 item 1) -------

def test_excluded_readings_and_their_rules_are_never_offered_again(tmp_path, monkeypatch):
    """RS9 = same (footnote 5) and RS6 = same (R14) are excluded: no reading set of the harness, the D1 document or
    the independent reference offers them, no rule only they selected exists, a block that names one is refused,
    the committed run selects no rule under either, and its C1, C3 and C-doc agree with the PLAN 12 NONE entries."""
    excluded = {("RS6", "same"), ("RS9", "same")}
    assert set(translation.EXCLUDED_READINGS) == excluded
    for set_id, value in excluded:
        assert value not in translation.READING_SETS[set_id] and value not in reference.SETS[set_id]
        assert run.SETS[set_id] == ("different",)
    assert all(reading != "same" for _, (_, readings) in build_document.READINGS.items() for reading in readings)
    named = {r for _, (_, readings) in build_document.READINGS.items() for rules in readings.values() for r in rules}
    assert not named & EXCLUDED_RULES
    assert not {b.id for b in translation.rule_blocks()} & EXCLUDED_RULES
    assert not {(s, v) for b in translation.rule_blocks() for s, v in b.when} & excluded
    # A rule block that names an excluded reading is refused when the translation is read.
    (tmp_path / "rules.d1.ve").write_text("## f10-dm-same | RS1=G & RS9=same | F10\nRule 1. Every proposal is acceptable.\n")
    monkeypatch.setattr(translation, "HERE", tmp_path)
    with pytest.raises(SystemExit, match="excluded reading RS9=same"):
        translation.read_blocks("rules.d1.ve")
    # The committed run: no choice, detail or rule list anywhere names an excluded reading or its rules.
    text = json.dumps({k: v for k, v in RESULTS.items() if k != "comparison"})
    assert "same" not in {v for s, v in re.findall(r'"(RS[69])": "(\w+)"', text)}
    assert not re.search(r"RS[69]=same", text) and not any(r in text for r in EXCLUDED_RULES)
    rows = {r["id"]: r for r in RESULTS["comparison"]}
    assert {i: (rows[i]["ve"], rows[i]["deviation"]["answer"]) for i in ("C1", "C3", "C-doc")} == {
        i: ("NONE", "NONE") for i in ("C1", "C3", "C-doc")}


@pytest.mark.parametrize("levels, activity, adequate", [
    (("cbrn_uplift_level_1", "cyber_uplift_level_1"), "EXT", ["applies", "p", "security_level_2_plus"]),
    (("ml_rd_acceleration_level_1", "ml_rd_automation_level_1"), "HRI", ["security_assessed_adequate", "p"])])
def test_one_mitigated_level_does_not_discharge_another_reached_level(levels, activity, adequate):
    """f9-acc, f10-acc: "for the T/CCLs the model has reached" (2.1.2, 3.1.2 step 2). A model at two levels of one
    bullet, with security adequate for both, is deemed acceptable when the deployment mitigations cover both levels,
    and not when they cover only one (the existential reading let one mitigated level discharge the other)."""
    def acceptable(mitigated):
        case = {"id": "fsf-fix:" + "+".join(mitigated), "family": "R", "levels": list(levels), "activity": activity,
                "findings": [["mitigates", "p", level] for level in mitigated] + [adequate]}
        assert run.premise_status(run.case_atoms(case))[0] == "model"
        return run.describe(run.item_result("ACCEPTABLE", case))
    assert acceptable(levels) == "ALL"
    assert acceptable(levels[:1]) == "NONE"


def test_a_possible_adjustment_is_no_exception_to_the_recommended_level():
    """f16-ds, f16-ds-strict: 2.2's "may be adjusted if ... This may occur if, for example, a model does not possess
    capabilities meaningfully different from other publicly available models" gives a reason, not a sufficient
    condition. With that finding (OT16) at L2 the recommended level is still required under RS3 = Ds, as without it;
    1.3.5's "we otherwise assess that the level of security applied is adequate" (OT4) remains the excepted case."""
    def recsec(*findings):
        case = {"id": "fsf-fix:recsec", "family": "B", "levels": ["cbrn_uplift_level_1"], "activity": None,
                "findings": [[f, "p"] for f in findings]}
        return run.describe(run.item_result("RECSEC", case))
    assert recsec() == recsec("like_public_models") == "SOME(RS3=Ds)"
    assert recsec("security_assessed_adequate") == "NONE"


# --- fsf-fidelity-fix review: F1 (the "will" rules of RS0), F2 (a CHECKED unit that uses an open predicate) ---------

def _quoted(text):
    return " ".join(re.findall(r'"([^"]*)"', text))


def test_every_rule_takes_its_rs0_status_from_its_source_feature():
    """F1: the "will" rules (RS0) are derived from the feature each rule header names, with one table entry per
    feature, so a rule added later cannot be left out (f17-hri was). A header quoting a "will" is a "will" rule, and
    each "will" feature's entry quotes its "will"."""
    blocks = translation.rule_blocks()
    features = {translation.rule_feature(b) for b in blocks}
    assert set(translation.WILL_FEATURES).isdisjoint(translation.NOT_WILL_FEATURES)
    assert set(translation.WILL_FEATURES) | set(translation.NOT_WILL_FEATURES) == features
    will = translation.will_rules()
    assert will == {b.id for b in blocks if translation.rule_feature(b) in translation.WILL_FEATURES}
    assert {"f6", "f8", "f14", "f17-pra", "f17-hri", "f17-add", "f18-yearly"} <= will
    assert not will & {"f2", "f4-check-d", "f4-need-d", "f4-check-r", "f4-need-r", "f12-u", "f15-diff", "f19-default"}
    assert all(re.search(r"\bwill\b", quote) for quote in translation.WILL_FEATURES.values())
    assert {b.id for b in blocks if re.search(r"\bwill\b", _quoted(b.source))} <= will


def test_a_rule_added_under_a_will_feature_is_a_will_rule_and_an_unclassified_feature_is_refused(monkeypatch):
    blocks = translation.rule_blocks()
    hri = next(b for b in blocks if b.id == "f17-hri")
    monkeypatch.setattr(translation, "rule_blocks",
                        lambda: blocks + [translation.Block("f17-later", hri.when, hri.source, hri.text)])
    assert "f17-later" in translation.will_rules()
    monkeypatch.setattr(translation, "rule_blocks",
                        lambda: blocks + [translation.Block("f99-later", (), "F99, no feature", hri.text)])
    with pytest.raises(SystemExit, match="F99"):
        translation.will_rules()


def test_every_will_quote_is_the_pinned_source_text():
    """The quotes are the pinned source's own words, which the gate runner does not store (tools/gate-optional.json)."""
    if not build_document.DEFAULT_SOURCE.exists():
        pytest.skip("the pinned source is not stored on this machine")
    text = build_document.DEFAULT_SOURCE.read_text()
    assert [f for f, quote in translation.WILL_FEATURES.items() if quote not in text] == []


def test_the_open_predicates_are_the_environment_legend_s_open_terms():
    """vocabulary.OPEN_PREDICATES, which the builder derives open terms from, says what the committed environment's
    legend says: "Open term OT<n>, decided by ..." or, with no term, "Decided by ..."."""
    predicates = json.loads((HERE / "environment.d1.json").read_text())["vocabulary"]["predicates"]
    legend = {}
    for name, entry in predicates.items():
        m = re.search(r"\. Open term (OT[0-9]+), decided by |\. Decided by ", entry["description"])
        if m:
            legend[name] = m[1]
    assert legend == vocabulary.OPEN_PREDICATES
    assert {t for t in legend.values() if t} <= set(build_document.OPEN_TERM_NAMES)


def test_a_unit_whose_rule_or_premise_uses_an_open_predicate_is_open_with_its_term():
    """F2: f15-diff's condition uses `reached` (OT1), and the Glossary premises of g-external and g-high-risk are about
    `low_risk` (OT8) and `high_risk` (OT7); each was CHECKED. The meanings the builder writes (derived from the
    content) are the open terms spans.json records, and no unit with an open term is CHECKED."""
    meanings = build_document.unit_meanings()
    spans = {u["id"]: u for u in json.loads((HERE / "spans.json").read_text())["units"]}
    assert set(meanings) == set(spans)
    for uid, meaning in meanings.items():
        terms = meaning["open"] if type(meaning) is dict and "open" in meaning else None
        assert spans[uid].get("open_terms") == terms, uid
        assert terms is None or spans[uid]["status"] == "OPEN", uid
    assert spans["s22-insider-not-required"]["open_terms"] == ["ot1_level_reached"]
    assert spans["g-external"]["open_terms"] == ["ot8_low_risk_external"]
    assert spans["g-high-risk"]["open_terms"] == ["ot7_high_risk_internal"]
    coverage = json.loads((HERE / "coverage.json").read_text())
    assert coverage["master_bytes_by_status"]["CHECKED"] == 4043 and coverage["bytes_by_status"]["CHECKED"] == 2935


def test_the_builder_refuses_a_checked_unit_whose_content_uses_an_open_predicate():
    rule = json.loads(translation.parsed_rule("f15-diff"))
    front = {"units": [{"id": "u", "content": {"norm": rule}}, {"id": "v"}, {"id": "w"}],
             "reading_sets": [{"unit": "w", "readings": [{"content": None}, {"content": {"norm": rule}}]}]}
    document = b"---\n" + json.dumps(front).encode() + b"\n---\nprose"
    checked = {"u": "CHECKED", "v": "CHECKED", "w": "CHECKED"}
    assert build_document.checked_but_open(document, checked) == {"u": ["reached"], "w": ["reached"]}
    assert build_document.checked_but_open(document, {"u": "OPEN", "v": "CHECKED", "w": "OPEN"}) == {}
    # Listed terms come first, then the derived ones; an open predicate with no term and nothing listed is refused.
    derived = build_document.derived_meaning
    assert derived("u", {"meaning": "specified"}, {"norm": rule}) == {"open": ["ot1_level_reached"]}
    assert derived("u", {"meaning": {"open": ["ot12_periodic"]}}, {"norm": rule}) == {
        "open": ["ot12_periodic", "ot1_level_reached"]}
    assert derived("u", {"meaning": "specified"}, {"ast": ["unary", "external", ["var", 0]]}) == "specified"
    termless = {"ast": ["unary", "internal_risk_unacceptable_without_safeguards", ["var", 0]]}
    with pytest.raises(SystemExit, match="internal_risk_unacceptable_without_safeguards"):
        derived("u", {"meaning": "specified"}, termless)
