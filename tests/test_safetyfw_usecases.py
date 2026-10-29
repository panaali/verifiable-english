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
                           "B-INTD/INSCOPE", "K2", "K4", "K22a"))
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
