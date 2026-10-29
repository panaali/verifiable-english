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
                      "cases.json": "0ed79956454c30e12b7808bec6d0db7b94324a97a14daabf7e8272d5ec8a5405"},
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
RSP_NAMES = ("rsp_vocabulary", "rsp_translation", "build_document", "stage0", "measure")


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
