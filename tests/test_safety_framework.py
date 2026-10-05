"""Safety-framework use case (usecases/safety-framework): fails on any mismatch with the answer key
or any change in what VE computes.

The answer key is PLAN.md section 6, transcribed into answer-key.json before VE
was run, and pinned here by hash. The five recorded disagreements are findings
documented in README.md and PLAN section 12; the key is never edited to match VE.
`test_rerun_equals_committed_results` recomputes every result with VE.
"""
import hashlib
import importlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "safety-framework"
# usecases/eligibility has modules with the same bare names (run, reference, translation), and
# both use cases import their siblings lazily by those names. This use case's modules are loaded
# apart and stand in sys.modules only while its own tests run.
OWN_NAMES = ("vocabulary", "translation", "run", "reference", "severity_and_dates", "build_document")


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
translation, vocabulary = OWN["translation"], OWN["vocabulary"]


@pytest.fixture(autouse=True)
def _own_modules(monkeypatch):
    for name, module in OWN.items():
        monkeypatch.setitem(sys.modules, name, module)

KEY_SHA256 = "8fbb04753730ca894789b6c2a90e6fd1916c0a90ba0e609cecca2c5398e0ce0e"
RESULTS = json.loads((HERE / "results.json").read_text())
RECORDED_DISAGREEMENTS = {
    # The key notes a "need not" (REL) for internal deployment at L5 to L7; bullets 3 and 4
    # release only further development, so no rule releases DM there (reference.py agrees).
    "A-L5-INT/DM", "A-L6-INT/DM", "A-L7-INT/DM",
    # The key wrote C1 and C-doc under narrowing N2 (F16 only a default rule), which the results
    # review withdrew: under RS3 = Ds with strict force and RS6 = same, F16 and F15 conflict.
    "C1", "C-doc",
}


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
    assert sum(r["agree"] for r in rows) == 257
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
    # With the withdrawn N2, F16 is a default rule at both forces and C1 is conflict-free.
    assert all(d["status"] == "CONFLICT-FREE" for d in variants["with_N2"]["C1"]["details"].values())
    # M7: a completed outcome depends on the default exactly at the silent or conflicted cells.
    assert {k for k, v in RESULTS["default_sensitive"].items() if v["conflicted_choices"]} == {
        "B-L2/RECSEC", "B-L3/RECSEC", "B-L4/RECSEC"}


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
    # The strict reading conflicts with F15 exactly when both name one act (RS6 same).
    details = RESULTS["items"]["C1"]["details"]
    assert [c for c, d in details.items() if d["status"] == "CONFLICT"] == ["RS3=Ds,RS3force=strict,RS6=same"]
    kind, true = reference.family_c_g()["C1"]
    assert kind == "SOME" and len(true) == 2 ** (len(reference.ALL_SETS) - 3)
    assert all((c["RS3"], c["RS3force"], c["RS6"]) == ("Ds", "strict", "same") for c in true)


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
