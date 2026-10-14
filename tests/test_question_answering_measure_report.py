"""F4: published numbers must agree with captured measurements and fixtures."""
from __future__ import annotations

import importlib.util
import gzip
import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("question_answering_report", ROOT / "tools/question_answering_report.py")
REPORT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REPORT)


def _agreement():
    return json.loads(gzip.decompress((REPORT.EVIDENCE / "agreement.json.gz").read_bytes()))


def test_q2_measurement_report_is_generated_from_saved_evidence():
    assert REPORT.DESTINATION.read_text() == REPORT.render()
    fixtures = json.loads((REPORT.EVIDENCE / "fixtures.json").read_text())["fixtures"]
    agreement = _agreement()["rows"]
    assert {row["fixture"] for row in agreement} == {row["id"] for row in fixtures}
    assert any(row["status"] == "compared" for row in agreement)


def test_the_budgets_are_met_and_the_corpus_agreement_is_recorded(tmp_path):
    """F4 (qa-q2 recheck): the report shows the plan's pass gates met (`ask` Lean CPU at most 2 s, U3 `ve ask` wall
    at most 60 s), and the agreement of the corpora's queries is recorded with no lead that contradicts the
    existing route (`tools/question_answering_agreement.py`)."""
    # The report states each budget as met (its renderer compares the saved figures with the plan's limits; the
    # measurement itself is the benchmark tools/bench/test_perf.py::test_ask_lean_cpu, never a suite assertion).
    text = REPORT.render()
    assert "`ask` CPU: U3 PASS, A1 PASS; U3 CLI wall: PASS." in text
    saved = _agreement()
    assert not any(row["status"].startswith("requires review") for row in saved["rows"])
    corpus = saved["corpus"]
    assert corpus["queries"] == len(corpus["rows"]) > 0
    # A comparison that needs review is reviewed in the evidence and is a row of DELTA.md (D15), never silent.
    delta = (ROOT / "docs/spec/question-answering-q2/DELTA.md").read_text()
    assert corpus["requires_review"] == [r for r in corpus["rows"] if r["status"].startswith("requires review")]
    for row in corpus["requires_review"]:
        assert row["review"].startswith("reviewed (DELTA D") and row["review"][16:19].rstrip(")") in delta, row
    assert {"readings", "norm-defaults"} <= set(corpus["counts"])
    # The DRI deferred seeds 450–999. The saved measurement covers exactly 450 complete trees.
    assert corpus["input_counts"]["norm-defaults"] == 450 * 8
    assert corpus["input_counts"]["readings"] >= 8
    assert sum(counts.get("same verdict", 0) for counts in corpus["counts"].values()) > 0
    from tools.lean_first_diff import norm_defaults_corpus
    from tools.question_answering_agreement import _nd_conclusions
    generated = tmp_path / "generated.json"
    norm_defaults_corpus(generated, trees=450, include_invalid=False)
    texts = {row["case"]: row["text"] for row in json.loads(generated.read_text())}
    assert set(texts) == {f"s{i}" for i in range(450)}
    def key(document, conclusion):
        return hashlib.sha256((document + "\n" + json.dumps(conclusion, sort_keys=True)).encode()).hexdigest()
    expected = {key(document, conclusion) for document in texts.values() for conclusion in _nd_conclusions()}
    compared = [row for row in corpus["rows"] if row["corpus"] == "norm-defaults"]
    assert len(compared) == len(expected)
    assert {key(texts[row["case"]], row["conclusion"]) for row in compared} == expected
    for row in corpus["rows"]:
        assert "older_reason" in row
        if "leads" in row:
            assert len(row["ask_reasons"]) == len(row["leads"])
        if row["status"] in {"same verdict", "ask unknown (X1 conflict)", "ask unknown (other)",
                             "compatible difference", "older budget exhausted"}:
            assert row["question"].startswith("Is it the case that ") and row["leads"]
        if row["status"] == "older budget exhausted":
            from tools.question_answering_agreement import OLDER_BUDGET_REASON
            assert row["older"] == "UNKNOWN" and row["older_reason"] == OLDER_BUDGET_REASON


def test_q2_f11_checked_conflicts_are_separate_from_identical_verdicts():
    corpus = _agreement()["corpus"]
    conflicts = [row for row in corpus["rows"] if row.get("older") in {"ALL", "NONE"}
                 and row.get("ask_reasons") and "X1" in row["ask_reasons"]]
    assert conflicts
    assert all(row["status"] == "ask unknown (X1 conflict)" for row in conflicts)
    assert sum(group.get("ask unknown (X1 conflict)", 0) for group in corpus["counts"].values()) >= len(conflicts)
    rendered = REPORT.render()
    assert "ask unknown (X1 conflict)" in rendered
    assert (f"Checked X1 conflicts where the older route answered ALL or NONE: {len(conflicts)} "
            f"(ALL {sum(row['older'] == 'ALL' for row in conflicts)}; "
            f"NONE {sum(row['older'] == 'NONE' for row in conflicts)}).") in rendered


def test_q2_f11_conflict_only_evidence_is_checked_by_lean(tmp_path):
    """The faster corpus refresh classifies X1 through the same Lean replay as a full answer."""
    from tools.lean_first_diff import norm_defaults_corpus
    from ve.ask import prepare
    generated = tmp_path / "generated.json"
    norm_defaults_corpus(generated, trees=450, include_invalid=False)
    document = next(row["text"] for row in json.loads(generated.read_text()) if row["case"] == "s0")
    saved = next(row for row in _agreement()["corpus"]["rows"]
                 if row["corpus"] == "norm-defaults" and row["case"] == "s0"
                 and row["status"] == "ask unknown (X1 conflict)")
    path = tmp_path / "s0.ve.md"
    path.write_text(document)
    prepared = prepare(path, document.encode(), saved["question"], generate=False)
    gen = prepared.builder.gen
    prepared.request["case"]["evidence"] = prepared.builder.conflict_evidence({"packages": gen._packages()})
    rows = prepared.ask()["rows"]
    assert [row["lead"] for row in rows] == saved["leads"]
    assert [row["reason"] for row in rows] == saved["ask_reasons"] == ["X1"]


def test_q2_d13_words_timing_covers_readings_norm_defaults_and_pilot():
    saved = json.loads((REPORT.EVIDENCE / "words-perf.json").read_text())
    by_case = {}
    for row in saved["rows"]:
        assert row["cpu_s"] > 0 and row["wall_s"] > 0
        by_case.setdefault(row["document"], {}).setdefault(row["revision"], set()).add(row["run"])
    assert set(by_case) == {"qa-q2-readings-bench.ve.md", "norm-defaults-seed-0",
                            "qa-q2-pilot-readings.ve.md"}
    assert all(revisions == {"before": {1, 2}, "after": {1, 2}} for revisions in by_case.values())
    delta = next(line for line in (ROOT / "docs/spec/question-answering-q2/DELTA.md").read_text().splitlines()
                 if line.startswith("| D13 |"))
    assert "evidence/words-perf.json" in delta
    for case in by_case:
        rows = [row for row in saved["rows"] if row["document"] == case]
        for field in ("cpu_s", "wall_s"):
            before = round(sum(row[field] for row in rows if row["revision"] == "before") / 2, 3)
            after = round(sum(row[field] for row in rows if row["revision"] == "after") / 2, 3)
            assert f"{before}→{after} s" in delta


def test_q2_f4_agreement_classifies_evidence_differences_by_saved_reasons():
    from tools.question_answering_agreement import OLDER_BUDGET_REASON, classify
    assert classify(["yes"], "UNKNOWN") == "requires review: every row yes, older UNKNOWN"
    assert classify(["yes"], "UNKNOWN", "some other limit") == "requires review: every row yes, older UNKNOWN"
    assert classify(["yes"], "UNKNOWN", OLDER_BUDGET_REASON) == "older budget exhausted"
    assert classify(["unknown"], "ALL", ask_reasons=["X1"]) == "ask unknown (X1 conflict)"
    assert classify(["unknown"], "UNKNOWN", ask_reasons=["X1"]) == "ask unknown (X1 conflict)"
    assert classify(["unknown"], "NONE", ask_reasons=["X4"]) == "ask unknown (other)"
    assert classify(["yes"], "ALL") == "same verdict"
    assert classify(["yes", "yes"], "ALL") == "same verdict"
    assert classify(["unknown", "unknown"], "UNKNOWN") == "same verdict"
    assert classify(["notSettled"], "UNKNOWN") == "compatible difference"
    assert classify(["notNecessarily"], "UNKNOWN") == "compatible difference"
    assert classify(["notSettled"], "SOME") == "compatible difference"
    assert classify([], "ALL").startswith("requires review")
    assert classify(["yes"], "DECIDED").startswith("requires review")
    assert classify(["true"], "ALL").startswith("requires review")


def test_q2_f5_d9_readings_generator_changes_no_decided_verdict():
    saved = json.loads((REPORT.EVIDENCE / "d9-readings-ab.json").read_text())
    assert saved["queries"] == len(saved["rows"]) == 8
    assert saved["changes"] == [row for row in saved["rows"]
                                if row["before"]["verdict"] != row["after"]["verdict"]]
    for row in saved["changes"]:
        assert row["before"]["verdict"] == "UNKNOWN"
        assert row["after"]["verdict"] in {"ALL", "SOME", "NONE"}


def test_q2_f4_corpus_rejects_an_incomplete_generated_tree(tmp_path):
    from tools.question_answering_agreement import corpus
    path = tmp_path / "incomplete.jsonl"
    path.write_text(json.dumps({"corpus": "norm-defaults", "case": "s0", "document": "",
                                "conclusion": ["unary", "p", ["const", "k"]], "older": "UNKNOWN"}) + "\n")
    with pytest.raises(ValueError, match="incomplete or repeated trees"):
        corpus([path])


def test_q2_f11_generated_scope_stops_at_the_requested_tree(tmp_path):
    from tools.lean_first_diff import norm_defaults_corpus
    path = tmp_path / "bounded.json"
    norm_defaults_corpus(path, trees=2, include_invalid=False)
    assert [row["case"] for row in json.loads(path.read_text())] == ["s0", "s1"]


@pytest.mark.parametrize("case,predicate", [
    ("s125", "x_required"), ("s234", "y_permitted"),
    ("s312", "x_required"), ("s361", "x_required"),
])
def test_q2_f5_d15_budget_unknown_does_not_contradict_checked_yes(case, predicate):
    from tools.question_answering_agreement import OLDER_BUDGET_REASON
    matches = [row for row in _agreement()["corpus"]["rows"]
               if row["corpus"] == "norm-defaults" and row["case"] == case and
               row["conclusion"] == ["forall", "act", ["unary", predicate, ["var", 0]]]]
    assert len(matches) == 1
    row = matches[0]
    assert row["older"] == "UNKNOWN"
    assert row["older_reason"] == OLDER_BUDGET_REASON
    assert row["leads"] == ["yes"]
    assert row["status"] == "older budget exhausted"
