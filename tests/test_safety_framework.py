"""Safety-framework use case (usecases/safety-framework): fails on any mismatch with the answer key
or any change in what VE computes.

The answer key is PLAN.md section 6, transcribed into answer-key.json before VE
was run, and pinned here by hash. The six recorded disagreements are findings
documented in README.md and PLAN section 12; the key is never edited to match VE.
`test_rerun_equals_committed_results` recomputes every result with VE.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "safety-framework"
sys.path.insert(0, str(HERE))

import build_document  # noqa: E402
import reference  # noqa: E402
import run  # noqa: E402
import translation  # noqa: E402
import vocabulary  # noqa: E402

KEY_SHA256 = "8fbb04753730ca894789b6c2a90e6fd1916c0a90ba0e609cecca2c5398e0ce0e"
RESULTS = json.loads((HERE / "results.json").read_text())
RECORDED_DISAGREEMENTS = {
    # The key notes a "need not" (REL) for internal deployment at L5 to L7; bullets 3 and 4
    # release only further development, so no rule releases DM there (reference.py agrees).
    "A-L5-INT/DM", "A-L6-INT/DM", "A-L7-INT/DM",
    # The closure "For CCLs, we define alert thresholds" and the TCL/CCL split make an alert
    # threshold for a TCL impossible: VE certifies these cases inconsistent, so they are not scored.
    "K2-L1/PROXIMITY", "K2-L5/PROXIMITY", "G3",
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
    assert sum(r["agree"] for r in rows) == 256
    # The comparison is recomputed from the committed results and the key.
    recomputed = run.compare(RESULTS)
    assert [r for r in rows if r["id"] in {x["id"] for x in recomputed}] == recomputed


def test_reference_reading_agrees_with_the_key_and_with_ve():
    out = reference.main()
    assert out["compared"] == 208 and out["items_differ"] == []
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
    assert [c for c, d in variants["without_N2"]["C1"]["details"].items()
            if d["status"] == "CONFLICT"] == ["RS3=Ds,RS6=same"]


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


@pytest.mark.skipif(not run.severity_and_dates_available(), reason="ve_risk_route is not built")
def test_rerun_equals_committed_results():
    assert run.main(["--check"]) == 0
