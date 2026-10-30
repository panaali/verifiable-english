"""The anthropic-rsp and openai-preparedness use cases (usecases/<case>): the frozen answer keys and their
transcription.

Each PLAN's section 6 is the answer key, frozen before any VE run (KEY-FREEZE.md records its SHA-256). The
transcription in answer-key.json and cases.json is pinned here by hash, and its counts are checked against the
PLAN's own section 5 table and section 6 totals, so that neither the key nor its transcription can change unnoticed.
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
USECASES = REPO / "usecases"

# case -> (section-6 SHA-256 recorded at the freeze, total items of section 5)
FROZEN = {
    "anthropic-rsp": ("1a684c7276c98e80b6a2db2718b5af7ba702b933be846498f895ec28744af5a3", 126),
    "openai-preparedness": ("6d1dd2a7729f789ea26212783fd49355ff3256110dc879c18e9f794b955ac522", 239),
}
# The section-6 subsection of each family, in the PLANs' order.
FAMILY_SECTION = {"A": "6.1", "B": "6.2", "K": "6.3", "T": "6.4", "C": "6.5", "G": "6.6", "N": "6.7", "S": "6.8",
                  "D": "6.9"}
CASES = sorted(FROZEN)


def section(case, number):
    """PLAN.md section `number` as KEY-FREEZE.md defines it: from the line starting `## <n>. ` up to the next one,
    joined with newlines plus a final newline."""
    lines = (USECASES / case / "PLAN.md").read_text(encoding="utf-8").split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith(f"## {number}. "))
    stop = next(i for i, line in enumerate(lines) if line.startswith(f"## {number + 1}. "))
    return "\n".join(lines[start:stop]) + "\n"


def items(case):
    return json.loads((USECASES / case / "answer-key.json").read_text())["items"]


def family_totals(case):
    """The section 5 table: family letter -> scored items (the number ending the row), and the bold total."""
    totals, total = {}, None
    for line in section(case, 5).split("\n"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and re.fullmatch(r"[A-Z]: .+", cells[0]):
            totals[cells[0][0]] = int(re.search(r"(\d+)$", cells[2]).group(1))
        elif cells[0] == "**Total**":
            total = int(cells[2].strip("*"))
    return totals, total


@pytest.mark.parametrize("case", CASES)
def test_section_6_is_the_frozen_key(case):
    """(a) The answer key is section 6 as frozen: the SHA-256 KEY-FREEZE.md records, recomputed."""
    recorded = re.search(r"Section 6 SHA-256 \| `([0-9a-f]{64})` \((\d+) bytes\)",
                         (USECASES / case / "KEY-FREEZE.md").read_text()).groups()
    text = section(case, 6).encode()
    assert (hashlib.sha256(text).hexdigest(), str(len(text))) == recorded
    assert recorded[0] == FROZEN[case][0]


@pytest.mark.parametrize("case", CASES)
def test_answer_key_has_every_item_of_section_5(case):
    """(b) and (c): the transcription has the section 5 total and each family's count, and one item per id."""
    totals, total = family_totals(case)
    rows = items(case)
    assert total == FROZEN[case][1] == len(rows) == sum(totals.values())
    assert len({r["id"] for r in rows}) == len(rows)
    assert Counter(r["plan"] for r in rows) == {FAMILY_SECTION[f]: n for f, n in totals.items()}
    assert {r["id"][0] for r in rows if r["plan"] == FAMILY_SECTION[r["id"][0]]} == set(totals)
    assert all(r["plan"] == FAMILY_SECTION[r["id"][0]] for r in rows)


@pytest.mark.parametrize("case", CASES)
def test_verdict_totals_are_those_section_6_states(case):
    """Section 6 states the ALL/SOME/NONE totals of its tabulated families; the transcription has them."""
    stated = {}
    for subsection, text in re.findall(r"### (6\.\d) [^\n]*\n(.*?)(?=\n### |\Z)", section(case, 6), re.S):
        found = re.search(r"Totals: ((?:(?:ALL|SOME|NONE) \d+(?:, )?)+)\.", text)
        if found:
            stated[subsection] = {k: int(n) for k, n in re.findall(r"(ALL|SOME|NONE) (\d+)", found.group(1))}
    assert stated, case
    for subsection, expected in stated.items():
        got = Counter(r["key"].split("(")[0] for r in items(case) if r["plan"] == subsection)
        assert got == expected, subsection


@pytest.mark.parametrize("case", CASES)
def test_every_item_names_a_case_of_cases_json_or_none(case):
    cases = {c["id"]: c for c in json.loads((USECASES / case / "cases.json").read_text())["cases"]}
    named = {r["case"] for r in items(case)}
    assert named - {None} == set(cases)
    for r in items(case):
        if r["case"] is not None:
            assert cases[r["case"]]["family"] == r["id"][0], r["id"]
        else:
            assert r["plan"] in {"6.5", "6.7", "6.8", "6.9"}, r["id"]


TRANSCRIPTION_SHA256 = {
    "anthropic-rsp": {"answer-key.json": "fd00575d348f0917cc6aebd08ea21cb67c5f2f7f1540a2d970666a127f1d4a50",
                      "cases.json": "b9f912ac56eb8cea4d9075b8936c640ec8f52d0e1e7a9bf80390264f8edeb554"},
    "openai-preparedness": {"answer-key.json": "2c8b27504eebd57bdb4953f5527fdc6373ce5e456fc5050bc8a840877b160ac2",
                            "cases.json": "a5b0d0c6a3bade39bd046e9434656231547237d06233651da909c34bd0704397"},
}


@pytest.mark.parametrize("case", CASES)
def test_transcription_is_pinned(case):
    """No key cell or case fact of the transcription changes without this pin changing in the same commit."""
    for name, digest in TRANSCRIPTION_SHA256[case].items():
        assert hashlib.sha256((USECASES / case / name).read_bytes()).hexdigest() == digest, name


# --- anthropic-rsp baseline (PLAN 7 to 10): the translation, the span accounting, stage 0 and the gaps -------------

RSP = USECASES / "anthropic-rsp"
RSP_EVIDENCE = REPO / "docs" / "usecases" / "safetyfw" / "anthropic-rsp"
# The case's modules import their siblings by bare names, two of which safety-framework's modules also use; they are
# loaded apart and stand in sys.modules only while these tests run (as tests/test_safety_framework.py does).
RSP_NAMES = ("rsp_vocabulary", "rsp_translation", "build_document", "stage0", "measure", "run", "reference")


def _load_rsp():
    import importlib
    import sys
    saved = {name: sys.modules.pop(name) for name in RSP_NAMES if name in sys.modules}
    sys.path.insert(0, str(RSP))
    try:
        return {name: importlib.import_module(name) for name in RSP_NAMES}
    finally:
        sys.path.remove(str(RSP))
        for name in RSP_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


RSP_MODULES = _load_rsp()
rsp_build, rsp_stage0, rsp_measure = RSP_MODULES["build_document"], RSP_MODULES["stage0"], RSP_MODULES["measure"]
rsp_translation, rsp_vocabulary = RSP_MODULES["rsp_translation"], RSP_MODULES["rsp_vocabulary"]
rsp_run, rsp_reference = RSP_MODULES["run"], RSP_MODULES["reference"]
LEAN_SERVICE = REPO / "lean/.lake/build/bin/ve_service"


@pytest.fixture
def rsp_modules(monkeypatch):
    import sys
    for name, module in RSP_MODULES.items():
        monkeypatch.setitem(sys.modules, name, module)


def test_rsp_environment_file_is_generated():
    assert (RSP / "environment.d1.json").read_text() == rsp_vocabulary.text()


@pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
def test_rsp_every_rule_and_premise_parses_with_one_reading(rsp_modules):
    for block in rsp_translation.rule_blocks():
        assert json.loads(rsp_translation.parsed_rule(block.id))["name"] == block.id
    assert sum(len(f) for _, f in rsp_translation.facts()) == 15


def test_rsp_n1_filters_all_rs0_definition_premises(rsp_modules):
    """F6: the T4 will/would-consider definitions must use the rule path's N1 switch."""
    facts = rsp_translation.facts()
    assert {block.id for block, _ in facts if block.narrowing == "RS0"} == {
        "t4-suff", "t4-only-if", "s2-suff-result", "s2-suff-third",
        "s2-only-if-result", "s2-only-if-third"}
    assert all(block.narrowing == "independent" for block, _ in facts
               if block.id.startswith("threshold-") or block.id == "highly-capable-t4")
    choice = rsp_run.BASE
    expected = {block.id for block, _ in facts if rsp_run.applies(block, choice)}
    assert {block.id for block, _ in rsp_run.selected_facts(choice)} == expected
    try:
        rsp_run.WITHOUT_NARROWING = "N1"
        assert {block.id for block, _ in rsp_run.selected_facts(choice)} == {
            block.id for block, _ in facts if rsp_run.applies(block, choice)
            and block.narrowing == "independent"}
    finally:
        rsp_run.WITHOUT_NARROWING = None


@pytest.mark.parametrize("item_id,case_id", [
    ("T1", "T1"), ("T2b", "T2"), ("T3", "T3"), ("T4b", "T4"), ("T7", "T7")])
def test_rsp_n1_counterfactual_removes_t_family_definition(item_id, case_id, rsp_modules):
    """F6 probe and adjacent proof/negative-goal cases, with baseline certificates retained."""
    case = rsp_run.CASES[case_id]
    baseline = rsp_run.threshold_answer(item_id, case)
    verdict = rsp_run.verdict(baseline)
    assert verdict == "ALL" if item_id in ("T1", "T3") else verdict.startswith("SOME(")
    assert all(row["reason"] != "UNKNOWN" for row in baseline["choices"])
    try:
        rsp_run.WITHOUT_NARROWING = "N1"
        without = rsp_run.threshold_answer(item_id, case)
        assert rsp_run.verdict(without) == "NONE"
        assert all(row["reason"] == "validated countermodel" for row in without["choices"])
    finally:
        rsp_run.WITHOUT_NARROWING = None


def test_rsp_n1_saved_comparison_includes_t_family(rsp_modules):
    changed = json.loads((RSP / "results.json").read_text())["without_narrowings"]["N1"]["changed"]
    assert len(changed) == 54
    assert {item: changed[item]["without"] for item in ("T1", "T2b", "T3", "T4b", "T7")} == {
        item: "NONE" for item in ("T1", "T2b", "T3", "T4b", "T7")}
    assert "Removing N1 changes 54 answer cells" in (RSP / "README.md").read_text()


def test_rsp_every_byte_is_in_exactly_one_unit(rsp_modules):
    """M3: the saved spans partition the 59,410 bytes; the D1 and master maps each total them; with the pinned source,
    the build reproduces spans.json and coverage.json byte for byte."""
    coverage = json.loads((RSP / "coverage.json").read_text())
    spans = json.loads((RSP / "spans.json").read_text())["units"]
    assert coverage["source_bytes"] == coverage["accounted_bytes"] == rsp_build.TEXT_BYTES == 59410
    assert sum(coverage["bytes_by_status"].values()) == sum(coverage["master_bytes_by_status"].values()) == 59410
    assert spans[0]["span"][0] == 0 and spans[-1]["span"][1] == 59410
    assert all(a["span"][1] == b["span"][0] for a, b in zip(spans, spans[1:]))
    assert [u["id"] for u in spans] == [uid for _, uid, _ in rsp_build.UNITS]
    if rsp_build.DEFAULT_SOURCE.exists():
        assert rsp_build.main(["--check"]) == 0


def test_rsp_reviewer_prohibitions_are_separate_coverage_units():
    """Each prohibition in 3.6.1 has its own span; only the organization clause has a D1 rule."""
    units = json.loads((RSP / "spans.json").read_text())["units"]
    ids = ("s361-financial-interest", "s361-individual-financial-interest", "s361-personal-relationships")
    assert [uid for _, uid, _ in rsp_build.UNITS if uid in ids] == list(ids)
    clauses = [next(u for u in units if u["id"] == uid) for uid in ids]
    assert [u["status"] for u in clauses] == ["CHECKED", "UNFORMALISED", "UNFORMALISED"]
    assert clauses[0]["rule"] == "f15-financial-interest"
    assert all(u["reason"] == "addressed_to_others" for u in clauses[1:])
    assert [u["span"][0] for u in clauses] == sorted(u["span"][0] for u in clauses)
    assert all(a["span"][1] == b["span"][0] for a, b in zip(clauses, clauses[1:]))
    assert (clauses[0]["span"][0], clauses[-1]["span"][1]) == (37680, 38099)
    if rsp_build.DEFAULT_SOURCE.exists():
        source = rsp_build.DEFAULT_SOURCE.read_bytes()
        for unit, phrase in zip(clauses, (b"a reviewing organization itself may not",
                                              b"individuals involved in conducting the review",
                                              b"close personal relationships with anyone at Anthropic")):
            assert phrase in source[slice(*unit["span"])]


def test_rsp_reported_coverage_matches_saved_measurement():
    """The use-case README and build report cannot keep a stale CHECKED claim after a span changes."""
    spans = json.loads((RSP / "spans.json").read_text())["units"]
    gaps = json.loads((RSP_EVIDENCE / "gaps.json").read_text())
    totals = gaps["master_bytes_by_status"]
    counts = Counter(u["status"] for u in spans)
    readme = (RSP / "README.md").read_text()
    report = (RSP_EVIDENCE.parent / "REPORT.md").read_text()
    for status in ("CHECKED", "OPEN", "LABELLED", "UNFORMALISED"):
        share = f"{totals[status] / gaps['source_bytes']:.1%}"
        cells = f"{counts[status]} | {totals[status]:,} | {share}"
        assert f"| {status} | {cells} |" in readme
        assert f"{totals[status]:,} ({share})" in next(
            line for line in report.splitlines() if line.startswith("| Anthropic RSP 3.4 |"))
    sc = gaps["features"]["SC"]
    assert f"| SC scope | {sc['units']} | {sc['bytes']:,} | {sc['sole_units']}, {sc['sole_bytes']:,} |" in readme


def test_rsp_every_reading_set_rule_and_open_term_is_placed(rsp_modules):
    """Each set of READINGS sits on exactly one unit and names only blocks of rules.d1.ve or facts.d1.ve (or a case
    premise); each open term a unit lists is declared; every declared open term is used."""
    spans = json.loads((RSP / "spans.json").read_text())["units"]
    placed = [u["reading_set"] for u in spans if "reading_set" in u]
    assert sorted(placed) == sorted(rsp_build.READINGS)
    blocks = {b.id for b in rsp_translation.read_blocks("rules.d1.ve")} | {
        b.id for b in rsp_translation.read_blocks("facts.d1.ve")}
    for set_id, (harness, choices) in rsp_build.READINGS.items():
        assert harness in rsp_build.SET_FAMILIES and set(harness.split(" and ")) <= set(rsp_translation.READING_SETS)
        for item in (i for items in choices.values() for i in items):
            assert item.startswith("case: ") or set(item.split(" or ")) <= blocks, (set_id, item)
    used = {t for u in spans for t in u.get("open_terms", [])}
    assert used == set(rsp_build.OPEN_TERMS)


def test_rsp_every_byte_not_checked_waits_for_a_named_family(rsp_modules):
    """gaps.json and units.json are measure.py's reading of the saved spans: a unit is CHECKED exactly when it has no
    blocker, every blocker is a family of the feature map, and an OPEN unit with an open term waits for JT."""
    units, gaps = rsp_measure.measure()
    for name, data in (("units.json", units), ("gaps.json", gaps)):
        assert json.loads((RSP_EVIDENCE / name).read_text()) == json.loads(json.dumps(data)), name
    for u in units["units"]:
        assert (u["status"] == "CHECKED") is (u["blockers"] == []), u["id"]
        assert set(u["blockers"]) <= set(rsp_measure.FAMILIES), u["id"]
    spans = {u["id"]: u for u in json.loads((RSP / "spans.json").read_text())["units"]}
    assert all("JT" in u["blockers"] for u in units["units"]
               if u["status"] == "OPEN" and spans[u["id"]].get("open_terms"))
    assert gaps["status_bytes_recomputed"] == gaps["master_bytes_by_status"]


def test_rsp_identifiers_and_inventions(rsp_modules):
    """P7 (M5) and M6, recomputed: no identifier packs a threshold, number or condition into its name, and every rule,
    premise, default and permission is traced to a span; stage0.json saved the same."""
    lint, audit = rsp_stage0.identifier_lint(), rsp_stage0.invention_audit()
    assert lint["violations"] == []
    assert audit["untraced"] == audit["defaults_untraced"] == audit["permissions_untraced"] == []
    assert audit["thresholds_without_premise"] == audit["order_or_causal_predicates"] == []
    saved = json.loads((RSP_EVIDENCE / "stage0.json").read_text())
    assert saved["P7"] == json.loads(json.dumps(lint)) and saved["M6"] == json.loads(json.dumps(audit))


def test_rsp_stage0_saved_answers(rsp_modules):
    """The saved stage 0: P1 OPEN, P2 pending, D2 admitted only without T4's unclassified harm, D3's certificates,
    P5 and P6 total, and judgments@0 refused beside soft-norms@0 (P8)."""
    saved = json.loads((RSP_EVIDENCE / "stage0.json").read_text())
    assert saved["P1"]["units"] == {"s36-full-review": "OPEN"}
    assert (saved["P2"]["units"], saved["P2"]["premises"]) == ({"t1-plan": "OPEN"}, "UNKNOWN")
    assert saved["P3"]["admitted"]
    assert saved["P3"]["with_unclassified_t4_harm"] == "HarmUnclassified: harm_of_automated_rd"
    assert all(c["might"] and not c["leads"] for c in saved["P3"]["stated_cells"])
    assert saved["P4"]["admitted"] and all(saved["P4"]["certificates"].values())
    assert saved["P5"]["total"] == saved["P6"]["master_total"] == 59410 and saved["P6"]["contiguous"]
    assert saved["P8"]["diagnostic"] == ("CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean "
                                         "route")


@pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
def test_rsp_stage0_rerun_equals_saved(rsp_modules):
    """Stage 0 recomputed by VE; the source probes need the pinned source, which the gate runner does not store
    (tools/gate-optional.json), and are left out without it."""
    assert rsp_stage0.main(["--check"]) == 0


@pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
def test_rsp_run_recomputes_every_key_item_and_records_causes(rsp_modules, monkeypatch):
    """Every saved answer comes from a fresh VE route, with no key read during answer()."""
    saved = json.loads((RSP / "results.json").read_text())
    fresh = rsp_run.run()
    assert fresh == {k: saved[k] for k in ("items", "comparison", "cost")}
    assert [r["id"] for r in saved["comparison"]] == [k["id"] for k in items("anthropic-rsp")]
    assert all(r["status"] in ("agree", "UNDECIDED-faithful") for r in saved["comparison"])
    assert all(r["cause"] and r["cause"]["feature_family"] for r in saved["comparison"] if not r["agree"])
    assert all(r["route"] for r in saved["comparison"])
    assert saved["metrics"]["M1"] == rsp_run.metrics(saved)["M1"]
    assert saved["metrics"]["M8"]["unknown_items"] == [r["id"] for r in saved["comparison"] if not r["agree"]]
    assert rsp_run.without_narrowings(fresh) == saved["without_narrowings"]
    # The case audit corrected the 6x factor and the scenario's explicit strong evidence.
    cases = rsp_run.CASES
    assert cases["T2"]["findings"]["OT15"] is False
    assert cases["K21"]["findings"]["OT8"] is True
    assert "significant_lead" not in json.dumps(json.loads(rsp_translation.parsed_rule("f24-delay"))["guard"])
    assert rsp_run.verdict(rsp_run.answer({"id": "K19b", "case": "K19b", "item": "REQUIRED:DELAY"})) == "ALL"
    # A model missing the source-stated T4 -> highly-capable premise is refused.
    original_atoms = rsp_run.atoms
    monkeypatch.setattr(rsp_run, "atoms", lambda case: original_atoms(case) - {("highly_capable", "s")})
    rsp_run._MODELS.clear()
    rsp_run._PREMISES_CHECKED.clear()
    choice = rsp_run.BASE
    doc = rsp_run.document(tuple(sorted(choice.items())), "deny")
    with pytest.raises(AssertionError, match="highly-capable-t4"):
        rsp_run.check_premises(doc, rsp_run.CASES["A-T4"], choice)


def test_rsp_independent_reference_and_comparator_catch_wrong_answers(rsp_modules):
    rows = rsp_reference.compare()
    assert len(rows) == 68 and all(row["agrees"] for row in rows)
    assert not rsp_reference.matches("ALL", ("RS1",), lambda c: c["RS1"] == "cond")
    assert not rsp_reference.matches("NONE", (), lambda c: True)
    assert not rsp_run.same_set("ALL", {"route": "test", "cone": [],
                                         "choices": [{"choice": {}, "holds": False}]})
    assert not rsp_run.same_set("ALL", {"route": "test", "cone": [], "choices": []})
    assert not rsp_run.same_set("SOME(cond)", {"route": "test", "cone": [],
                                                "choices": [{"choice": {}, "holds": True}]})


@pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
def test_rsp_six_mutants_change_exactly_the_named_results(rsp_modules):
    saved = json.loads((RSP / "results.json").read_text())
    fresh = rsp_run.mutants({"comparison": saved["comparison"]})
    assert fresh == saved["mutants"]
    assert all(value["exact"] for value in fresh.values())
    assert all(fresh[name]["invention_audit_flags"] for name in ("m2", "m4"))


@pytest.mark.parametrize("id_", ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C-doc"))
def test_rsp_unknown_w1_is_neither_false_nor_a_scored_answer(rsp_modules, monkeypatch, id_):
    saved = json.loads((RSP / "results.json").read_text())
    result = saved["items"][id_]
    assert all(row["holds"] is not False for row in result["choices"] if "UNKNOWN" in row["w1"])
    assert all("UNKNOWN" not in row["w1"] for row in result["choices"])
    from types import SimpleNamespace
    monkeypatch.setattr(rsp_run, "check_conflict", lambda *args, **kwargs: SimpleNamespace(status="UNKNOWN"))
    rsp_run._conflict.cache_clear()
    unresolved = rsp_run.conflict(id_)
    assert unresolved["undecided"] and all(row["holds"] is None for row in unresolved["choices"])
    assert rsp_run.verdict(unresolved) == "UNDECIDED"
    assert not rsp_run.same_set("NONE", unresolved)
    rsp_run._conflict.cache_clear()


@pytest.mark.parametrize("id_", ("D1", "D2", "D3b", "D4", "D5"))
def test_rsp_missing_quantity_certificate_is_undecided(rsp_modules, monkeypatch, id_):
    monkeypatch.setattr(rsp_run, "dates", lambda: {"certificates": {id_: False}})
    assert rsp_run.date_answer(id_)["undecided"]
    unknown = {"choices": [{"choice": {}, "holds": None}], "cone": [], "route": "test"}
    assert rsp_run.verdict(unknown) == "UNDECIDED"
    assert not rsp_run.same_set("NONE", unknown)


@pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
@pytest.mark.parametrize("mutant,field", [("m2", "untraced"), ("m4", "thresholds_without_premise")])
def test_rsp_invention_audit_checks_the_actual_mutation(rsp_modules, mutant, field):
    try:
        rsp_run.MUTANT = mutant
        result = rsp_run.run()
        audit = rsp_run.metrics({**result, "mutants": {}})["M6"]
        assert audit[field]
        assert audit == rsp_run.invention_audit_for(result)
    finally:
        rsp_run.MUTANT = None
        rsp_run.document.cache_clear()
        rsp_run._conflict.cache_clear()


@pytest.mark.parametrize("mutant,item_id,field", [("m2", "G1", "untraced"),
                                                  ("m4", "G3", "thresholds_without_premise")])
def test_rsp_audit_uses_the_mutated_query_input(rsp_modules, mutant, item_id, field):
    try:
        rsp_run.MUTANT = mutant
        item = rsp_run.gap_probe(item_id)
        audit = rsp_run.invention_audit_for({"items": {item_id: item}})
        assert audit[field]
    finally:
        rsp_run.MUTANT = None


def test_rsp_each_narrowing_has_an_unscored_counterfactual(rsp_modules):
    saved = json.loads((RSP / "results.json").read_text())["without_narrowings"]
    assert set(saved) == {"N1", "N2", "N3"}
    assert all(row["unscored"] and row["changed"] for row in saved.values())
    assert all(saved["N1"]["changed"][id_]["without"] == "NONE"
               for id_ in ("A-T0/PROT1", "A-T1/PROT1", "A-T4/PROT4",
                           "B-INTD/INSCOPE", "K2", "K4", "K22a", "D3b", "D4", "D5"))
    assert saved["N2"]["changed"]["G1"]["without"] == "NONE"
    assert saved["N3"]["changed"]["K13"]["without"] == "NONE"


def test_rsp_n1_classification_is_explicit_for_every_rule(rsp_modules):
    """RS0 is a source reading, including clauses that inherit 'will' from an earlier sentence."""
    blocks = rsp_translation.rule_blocks()
    assert len({block.id for block in blocks}) == len(blocks)
    assert all(block.narrowing in {"RS0", "independent"} for block in blocks)
    assert all(json.loads(rsp_translation.parsed_rule(block.id)).get("mode", "strict") == "strict"
               for block in blocks if block.narrowing == "RS0")
    assert {block.id for block in blocks if block.narrowing == "RS0"} >= {
        "f8-internal", "f9-public", "f9-internal", "f11-goal-missed"}
    assert {block.id for block in blocks if block.narrowing == "independent"} >= {
        "f5-strict", "f15-financial-interest", "f26-need-not-delay"}


@pytest.mark.parametrize("case_id,predicate", [
    ("B-INTD", "in_scope"),
    ("K2", "off_cycle_published"),
    ("K4", "off_cycle_published"),
    ("K22", "goal_miss_addressed"),
])
def test_rsp_n1_prediction_removes_inherited_commitments(rsp_modules, case_id, predicate):
    """F4: the selected Lean rules disappear when N1 is removed, even without a local 'will'."""
    try:
        rsp_run.WITHOUT_NARROWING = "N1"
        rsp_run.document.cache_clear()
        assert rsp_run.verdict(rsp_run.query(rsp_run.CASES[case_id], predicate)) == "NONE"
    finally:
        rsp_run.WITHOUT_NARROWING = None
        rsp_run.document.cache_clear()


def test_rsp_date_obligations_follow_their_source_rules(rsp_modules):
    """N1 changes the obligation, while D3's arithmetic certificate remains available."""
    rules = {b.id: b for b in rsp_translation.rule_blocks()}
    date_cases = rsp_stage0.DATE_QUESTIONS
    assert set(date_cases) == {"D3a", "D3b", "D4", "D5"}
    assert all(case[4] in rules and rules[case[4]].narrowing == "RS0" for case in date_cases.values())
    assert {id_: rsp_run.verdict(rsp_run.date_answer(id_)) for id_ in date_cases} == {
        "D3a": "NONE", "D3b": "ALL", "D4": "ALL", "D5": "ALL"}
    try:
        rsp_run.WITHOUT_NARROWING = "N1"
        assert {id_: rsp_run.verdict(rsp_run.date_answer(id_)) for id_ in date_cases} == {
            id_: "NONE" for id_ in date_cases}
    finally:
        rsp_run.WITHOUT_NARROWING = None


@pytest.mark.parametrize("narrowing,item_id", [("N1", "A-T1/PROT1"), ("N2", "G1"), ("N3", "K13")])
def test_rsp_each_narrowing_reruns_a_ve_answer(rsp_modules, narrowing, item_id):
    key = next(item for item in items("anthropic-rsp") if item["id"] == item_id)
    try:
        rsp_run.WITHOUT_NARROWING = narrowing
        rsp_run.document.cache_clear()
        assert rsp_run.verdict(rsp_run.answer(key)) == "NONE"
    finally:
        rsp_run.WITHOUT_NARROWING = None
        rsp_run.document.cache_clear()


# --- openai-preparedness baseline (PLAN 7 to 10) ---------------------------------------------------------------

PF = USECASES / "openai-preparedness"
PF_EVIDENCE = REPO / "docs/usecases/safetyfw/openai-preparedness"
PF_NAMES = ("pf_vocabulary", "pf_translation", "build_document", "stage0", "measure")


def _load_pf():
    import importlib
    import sys
    saved = {name: sys.modules.pop(name) for name in PF_NAMES if name in sys.modules}
    sys.path.insert(0, str(PF))
    try:
        return {name: importlib.import_module(name) for name in PF_NAMES}
    finally:
        sys.path.remove(str(PF))
        for name in PF_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


PF_MODULES = _load_pf()
pf_vocab, pf_translation, pf_build = (PF_MODULES[n] for n in ("pf_vocabulary", "pf_translation", "build_document"))
pf_stage0, pf_measure = (PF_MODULES[n] for n in ("stage0", "measure"))


@pytest.fixture
def pf_modules(monkeypatch):
    import sys
    for name, module in PF_MODULES.items():
        monkeypatch.setitem(sys.modules, name, module)


def test_pf_translation_lint_and_invention_audit(pf_modules):
    assert (PF / "environment.d1.json").read_text() == pf_vocab.text()
    assert len(pf_vocab.LEVELS) == 6
    assert pf_stage0.identifier_lint()["violations"] == []
    audit = pf_stage0.invention_audit()
    assert audit["untraced"] == audit["defaults_untraced"] == audit["permissions_untraced"] == []
    assert audit["choice_mismatches"] == []
    assert audit["thresholds_without_premise"] == audit["order_or_causal_predicates"] == []
    for block in pf_translation.rule_blocks():
        assert json.loads(pf_translation.parsed_rule(block.id))["name"] == block.id
    assert all(len(fs) == 2 for _, fs in pf_translation.facts())


def test_pf_all_planned_d1_families_have_source_bound_drafts(pf_modules):
    blocks = {b.id: b for b in pf_translation.rule_blocks()}
    assert {int(m.group(1)) for name in blocks if (m := re.match(r"f(\d+)-", name))} == set(range(1, 18))
    placements = {value[1] for value in pf_build.PLACEMENTS.values()
                  if value[0] in ("rule", "blocked_rule")}
    choices = {name for _, readings in pf_build.READINGS.values()
               for names in readings.values() for name in names}
    assert set(blocks) <= placements | choices
    assert all(block.source.strip() for block in blocks.values())

    for set_id, (harness, readings) in pf_build.READINGS.items():
        assert set(readings) == set(pf_translation.READING_SETS[harness])
        for choice, names in readings.items():
            for name in names:
                assert name in blocks
                assert not blocks[name].when or (harness, choice) in blocks[name].when

    assert [name for name in pf_build.READINGS["rs8-distilled"][1]["rel"]] == ["f6-rel"]
    assert pf_build.READINGS["rs8-distilled"][1]["pred"] == []
    f6 = json.loads(pf_translation.parsed_rule("f6-rel"))
    assert f6["sign"] is False and f6["predicate"] == "additional_safety_measures"
    assert f6["mode"] == "default"
    assert "significant_increase" in json.dumps(f6["unless"])

    f11 = pf_build.READINGS["rs5-adjustment"][1]
    assert {"f11-acknowledge", "f11-protect", "f11-share"} <= set(f11["within"]) & set(f11["exception"])
    assert json.loads(pf_translation.parsed_rule("f11-within"))["predicate"] == "adjustment_permission"
    exception = json.loads(pf_translation.parsed_rule("f11-exception"))
    assert exception["predicate"] == "safeguards_before_deployment" and exception["sign"] is False
    assert {"adjustment_confirmed", "adjustment_conditions"} <= set(re.findall(
        r'"([a-z_]+)"', json.dumps(exception["guard"])))

    rows = {"lra": "lra_found", "sandbagging": "sandbagging_found", "ara": "ara_found",
            "undermining": "undermining_found", "nuclear": "nuclear_found"}
    for row, predicate in rows.items():
        assert pf_build.READINGS[f"rs4-{row}"][1] == {"N": [f"f12-{row}"], "P": []}
        guard = json.dumps(json.loads(pf_translation.parsed_rule(f"f12-{row}"))["guard"])
        assert predicate in guard
        if row in ("lra", "undermining"):
            assert "high_capability" in guard and "critical_capability" in guard

    f17 = pf_build.READINGS["rs12-category"][1]
    assert f17 == {"suff": ["f17-suff"], "iff": ["f17-iff", "f17-iff-only"]}
    negative = json.loads(pf_translation.parsed_rule("f17-iff-only"))
    assert negative["sign"] is False and negative["guard"][0] == "not"
    for criterion in ("plausible", "measurable", "severe", "net_new", "irremediable"):
        assert criterion in json.dumps(negative["guard"])

    units = {unit["id"]: unit for unit in json.loads((PF / "spans.json").read_text())["units"]}
    assert {units[key]["blocked_rule"] for key in ("p10-u147", "p10-u148", "p8-u104", "p8-u105")} == {
        "f5-checkpoint", "f5-ambiguous", "f13-review", "f13-results"}
    assert all(units[key]["status"] == "UNFORMALISED" for key in ("p10-u147", "p10-u148"))
    for row, unit_id in {"lra": "p8-u106", "sandbagging": "p8-u109", "ara": "p8-u110",
                         "undermining": "p8-u111", "nuclear": "p8-u112"}.items():
        assert units[unit_id]["status"] == "OPEN"
        assert units[unit_id]["reading_set"] == f"rs4-{row}"
    assert units["p8-u109"]["waits"][-1] == "AP"
    assert units["p8-u112"]["waits"][-1] == "AP"


def test_pf_reading_blocks_match_the_choice_that_selects_them(pf_modules, monkeypatch):
    assert pf_stage0.invention_audit()["choice_mismatches"] == []
    original = pf_build.READINGS["rs1-misuse-bio"]
    monkeypatch.setitem(pf_build.READINGS, "rs1-misuse-bio",
                        ("RS1", {"strict": original[1]["default"], "default": original[1]["strict"]}))
    assert {tuple(row) for row in pf_stage0.invention_audit()["choice_mismatches"]} == {
        ("rs1-misuse-bio", "strict", "f1-misuse-bio-default"),
        ("rs1-misuse-bio", "default", "f1-misuse-bio-strict")}


def test_pf_checked_norms_keep_their_source_scope(pf_modules):
    units = {unit["id"]: unit for unit in json.loads((PF / "spans.json").read_text())["units"]}
    assert units["p16-u271"]["status"] == "UNFORMALISED"
    assert units["p16-u271"]["reason"] == "unmapped_clause"
    guard = json.loads(pf_translation.parsed_rule("f16-sag-recommend"))["guard"]
    assert "framework_deployment" in json.dumps(guard)
    assert "covered" in json.dumps(guard)


def test_pf_appendix_c2_should_is_a_pending_norm_reading(pf_modules):
    units = {unit["id"]: unit for unit in json.loads((PF / "spans.json").read_text())["units"]}
    unit = units["p19-u328"]
    assert unit["status"] == "OPEN" and unit["reading_set"] == "rs9-c2-misalignment"
    _, choices = pf_build.READINGS[unit["reading_set"]]
    assert set(choices) == {"strict", "default"}
    assert {json.loads(pf_translation.parsed_rule(ids[0])).get("mode", "strict") for ids in choices.values()} == {
        "strict", "default"}
    if pf_build.DEFAULT_SOURCE.exists():
        _, rebuilt = pf_build.build(pf_build.DEFAULT_SOURCE.read_bytes())
        assert next(r for r in rebuilt if r["id"] == unit["id"])["reading_set"] == unit["reading_set"]
    for page in (18, 19, 20):
        spec, wait = pf_build._fallback(page, 0, b"Safeguards should minimize risk.")
        assert spec["kind"] == ["unformalised", "unmapped_duty"] and wait == "AP"


def test_pf_p3_p4_are_recomputed_without_source_text(pf_modules):
    result = pf_stage0.run(None)
    saved = json.loads((PF_EVIDENCE / "stage0.json").read_text())
    assert result["P3"] == saved["P3"] and result["P4"] == saved["P4"]
    assert result["P3"]["admitted"] and result["P3"]["stated_might"]
    assert result["P3"]["bio_h_might"]
    assert result["P3"]["table1_might"] == {name: True for name in ("BIO-H", "BIO-C", "CYB-H", "CYB-C")}
    assert set(result["P3"]["table1_unformalised"]) == {"AIS-H", "AIS-C"}
    severity = pf_stage0.risk_environment()["risk"]["severity"]
    assert severity["more_severe"] == []
    assert len(severity["unranked"]) == len(severity["classes"]) * (len(severity["classes"]) - 1) // 2
    assert not result["P3"]["invented_leads"]
    assert result["P4"]["date_certificate_replayed"]
    assert result["P4"]["ratio"] == ["le", ["scale", "elapsed_day", "5",
        ["const", "elapsed_day", "current_progress_time"]],
        ["const", "elapsed_day", "baseline_progress_time"]]
    assert all(result["P4"]["conditional_date_bridges"].values())


def test_pf_one_fifth_time_bound_distinguishes_the_two_frozen_cases(pf_modules):
    from ve.environment import Environment
    from ve.units import prove_quantity, check_quantity_certificate
    env = Environment(pf_stage0.quantity_environment())
    def assertion(current_days):
        return {"format": "ve-quantity@1", "formula": ["le",
            ["scale", "elapsed_day", "5", ["num", "elapsed_day", str(current_days)]],
            ["num", "elapsed_day", "140"]]}
    certificate = prove_quantity(env, [], assertion(28))
    assert certificate and check_quantity_certificate(env, [], assertion(28), certificate)
    assert prove_quantity(env, [], assertion(35)) is None


def test_pf_temporal_and_per_item_rules_are_not_weakened_into_checked_claims(pf_modules):
    units = json.loads((PF / "spans.json").read_text())["units"]
    blocked = {"p10-u149": ("event_order", "ET"),
               "p11-u162": ("quantifier_scope", "SC"),
               "p11-u164": ("quantifier_scope", "SC"),
               "p11-u165": ("quantifier_scope", "SC")}
    by_id = {unit["id"]: unit for unit in units}
    assert {k: pf_build.BLOCKED_RULE_REASONS[k] for k in (
        "f7-evaluations", "f9-specific", "f9-efficacy", "f9-threshold")} == {
        "f7-evaluations": "event_order", "f9-specific": "quantifier_scope",
        "f9-efficacy": "quantifier_scope", "f9-threshold": "quantifier_scope"}
    if pf_build.DEFAULT_SOURCE.exists():
        _, rebuilt = pf_build.build(pf_build.DEFAULT_SOURCE.read_bytes())
        assert {unit["id"]: unit["reason"] for unit in rebuilt if unit["id"] in blocked} == {
            unit_id: reason for unit_id, (reason, _) in blocked.items()}
    for unit_id, (reason, feature) in blocked.items():
        unit = by_id[unit_id]
        assert unit["status"] == "UNFORMALISED"
        assert unit["reason"] == reason and feature in unit["waits"]
        assert "rule" not in unit and "blocked_rule" in unit
    for block_id, predicate in {
        "f7-evaluations": "evaluations_before_deployment",
        "f9-specific": "specific_safeguards_per_path",
        "f9-efficacy": "efficacy_methods_per_safeguard",
        "f9-threshold": "efficacy_threshold_per_safeguard",
    }.items():
        assert json.loads(pf_translation.parsed_rule(block_id))["predicate"] == predicate


def test_pf_exposition_fallback_preserves_claims_and_rs15_readings(pf_modules):
    units = {unit["id"]: unit for unit in json.loads((PF / "spans.json").read_text())["units"]}
    assert {units[unit_id]["reading_set"] for unit_id in ("p15-u249", "p15-u252")} == {
        "rs15-persuasion", "rs15-threat-models"}
    assert pf_build.PLACEMENTS["Going forward we will handle risks related to persuasion"][0] == "readings"
    assert pf_build.PLACEMENTS["For these areas, in collaboration with external experts, we commit"][0] == "readings"
    assert pf_build.PLACEMENTS["As a reminder, covered systems that reach High capability must have"][0] == "rule"
    assert pf_build.PLACEMENTS["Systems that reach Critical capability also require sufficient safeguards"][0] == "rule"
    for unit_id in ("p15-u249", "p15-u252", "p17-u296", "p17-u297"):
        assert units[unit_id]["status"] == "OPEN"
    for page in (15, 17):
        spec, _ = pf_build._fallback(page, 0, b"A substantive claim about safeguards.")
        assert spec["kind"] == ["unformalised", "unmapped_claim"]


def test_pf_rs13_and_untranslated_claims_have_named_residuals(pf_modules):
    records = json.loads((PF / "spans.json").read_text())["units"]
    summary = next(r for r in records if r.get("reading_set") == "rs13-employee-summary")
    assert summary["status"] == "OPEN"
    assert summary["waits"] == ["AT", "AP"]
    assert pf_build.READINGS["rs13-employee-summary"] == ("RS13", {"permission": [], "might": []})
    assert pf_translation.READING_SETS["RS13"] == ("permission", "might")
    exposition, _ = pf_build._fallback(1, 0, b"Contents")
    claim, _ = pf_build._fallback(1, 0, b"Employees may request a summary")
    assert exposition["kind"] == "exposition"
    assert claim["kind"] == ["unformalised", "hedged_claim"]
    pending = [r for r in records if r.get("reason") in {"unmapped_claim", "unmapped_duty"}]
    assert pending and all(r["status"] == "UNFORMALISED" and r.get("residual") for r in pending)
    assert len({r["residual"] for r in pending}) == len(pending)
    if pf_build.DEFAULT_SOURCE.exists():
        source = pf_build.DEFAULT_SOURCE.read_bytes()
        _, rebuilt = pf_build.build(source)
        assert rebuilt == [{k: v for k, v in r.items() if k != "status"} for r in records]
        for r in pending:
            a, b = r["span"]
            assert r["residual"] == (f"{r['reason']}-{r['id']}-"
                                     f"{hashlib.sha256(source[a:b]).hexdigest()[:12]}")


def test_pf_checked_has_no_wait_or_unmapped_source_clause(pf_modules):
    units = {r["id"]: r for r in json.loads((PF / "spans.json").read_text())["units"]}
    assert not [r["id"] for r in units.values() if r["status"] == "CHECKED" and r["waits"]]
    assert all(r["rule"] in pf_build.CHECKED_CLAUSES for r in units.values()
               if r["status"] == "CHECKED" and "rule" in r)
    for uid, rule_id in {"p10-u152": "f7-report", "p13-u218": "f14-document",
                         "p16-u271": "f16-sag-recommend"}.items():
        assert units[uid]["status"] == "UNFORMALISED"
        assert units[uid]["blocked_rule"] == rule_id
        assert rule_id not in pf_build.CHECKED_CLAUSES
    assert json.loads(pf_translation.parsed_rule("f14-document"))["predicate"] == "decision_documented"
    assert "applicable_risks" not in pf_translation.parsed_rule("f16-sag-recommend")
    assert units["p16-u283"]["status"] == "CHECKED"
    assert not pf_build._complete_clause_map("f16-ssc-visibility", b"The SSC will be given visibility into processes and reports")
    if pf_build.DEFAULT_SOURCE.exists():
        source = pf_build.DEFAULT_SOURCE.read_bytes()[slice(*units["p16-u283"]["span"])]
        assert pf_build._complete_clause_map("f16-ssc-visibility", source)
        assert pf_build.main(["--check"]) == 0


def test_pf_label_requires_positive_exposition_without_claim_marker(pf_modules):
    units = {r["id"]: r for r in json.loads((PF / "spans.json").read_text())["units"]}
    for uid in ("p11-u169", "p19-u327", "p19-u335", "p19-u336"):
        assert units[uid]["status"] != "LABELLED"
    if pf_build.DEFAULT_SOURCE.exists():
        source = pf_build.DEFAULT_SOURCE.read_bytes()
        for unit in units.values():
            if unit["status"] == "LABELLED":
                assert not pf_build.CLAIM_MARKER.search(source[slice(*unit["span"])])
        _, rebuilt = pf_build.build(source)
        assert [(r["id"], r["kind"]) for r in rebuilt] == [
            (r["id"], r["kind"]) for r in units.values()]


def test_pf_no_source_unit_is_left_in_translation_backlog():
    coverage = json.loads((PF / "coverage.json").read_text())
    assert coverage["unformalised_reasons"].get("not_translated", 0) == 0
    units = json.loads((PF / "spans.json").read_text())["units"]
    for unit in units:
        if unit["status"] == "UNFORMALISED":
            family, _ = pf_build.BLOCKER_DETAIL[unit["reason"]]
            assert unit["detail"].startswith(f"{family}: ")
            assert pf_build.SOURCE_SUBJECT[int(unit["id"].split("-")[0][1:])] in unit["detail"]


def test_pf_every_byte_has_ve_status_and_one_unit(pf_modules):
    coverage = json.loads((PF / "coverage.json").read_text())
    units = json.loads((PF / "spans.json").read_text())["units"]
    assert coverage["source_bytes"] == coverage["accounted_bytes"] == pf_build.TEXT_BYTES == 67418
    assert units[0]["span"][0] == 0 and units[-1]["span"][1] == 67418
    assert all(a["span"][1] == b["span"][0] for a, b in zip(units, units[1:]))
    assert sum(coverage["bytes_by_status"].values()) == 67418
    assert coverage["bytes_by_status"] == coverage["master_bytes_by_status"]
    assert {u["status"] for u in units} == {"CHECKED", "OPEN", "LABELLED", "UNFORMALISED"}
    assert all("reason" in u for u in units if u["status"] == "UNFORMALISED")
    assert all(u["status"] != "LABELLED" for u in units if u["id"].startswith("p2-"))
    readme = (PF / "README.md").read_text()
    gaps = json.loads((PF_EVIDENCE / "gaps.json").read_text())
    for family, data in gaps["features"].items():
        assert (f"| {family} | {data['units']} | {data['bytes']:,} | "
                f"{data['sole_units']}, {data['sole_bytes']:,} |") in readme
    assert f"{coverage['residual']['unresolved_reading_sets']} unresolved reading sets" in readme
    for status, amount in coverage["master_bytes_by_status"].items():
        count = sum(u["status"] == status for u in units)
        assert f"| {status} | {count} | {amount:,} | {amount / 67418:.1%} |" in readme
        report_row = next(line for line in (PF_EVIDENCE.parent / "REPORT.md").read_text().splitlines()
                          if line.startswith("| OpenAI PF v2 |"))
        assert f"{amount:,} ({amount / 67418:.1%})" in report_row
    if pf_build.DEFAULT_SOURCE.exists():
        assert pf_build.main(["--check"]) == 0


def test_pf_stage0_and_gaps(pf_modules):
    saved = json.loads((PF_EVIDENCE / "stage0.json").read_text())
    assert json.loads((PF / "environment.d2.json").read_text()) == pf_stage0.risk_environment()
    assert json.loads((PF / "environment.d3.json").read_text()) == pf_stage0.quantity_environment()
    assert saved["P1"]["admitted"] and set(saved["P1"]["units"].values()) == {"OPEN"}
    assert saved["P2"]["admitted"] and saved["P2"]["unresolved_reading_sets"] == 1
    assert saved["P3"]["admitted"] and saved["P3"]["stated_might"] and not saved["P3"]["invented_leads"]
    assert saved["P4"]["date_certificate_replayed"]
    assert saved["P5"]["total"] == saved["P6"]["master_total"] == 67418 and saved["P6"]["contiguous"]
    assert saved["P7"]["violations"] == saved["M6"]["untraced"] == []
    assert not saved["P8"]["admitted"]
    units, gaps = pf_measure.measure()
    assert json.loads((PF_EVIDENCE / "units.json").read_text()) == units
    assert json.loads((PF_EVIDENCE / "gaps.json").read_text()) == gaps
    assert gaps["status_bytes_recomputed"] == gaps["master_bytes_by_status"]
    for unit in units["units"]:
        assert (unit["status"] == "CHECKED") == (unit["blockers"] == [])
        assert set(unit["blockers"]) <= set(pf_measure.FAMILIES)
    if pf_build.DEFAULT_SOURCE.exists():
        assert pf_stage0.main(["--check"]) == 0
