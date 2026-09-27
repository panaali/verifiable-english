"""Recheck the authored BlueDot use case without changing the source draft."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path

from ve.ast import Document, formula_from_data
from ve.document import check_document, load_document
from ve.english import parse_english
from ve.natural import render_natural_sentence


ROOT = Path(__file__).resolve().parents[1] / "usecases/bluedot-grant"
SOURCE_HASH = "a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22"


def test_source_partition_and_authored_readings():
    source = (ROOT / "source.md").read_bytes()
    assert sha256(source).hexdigest() == SOURCE_HASH
    doc = load_document(ROOT / "document.ve.md")
    assert doc["source"] == source
    assert len(source) == 7619
    assert Counter(u["status"] for u in doc["units"]) == {
        "CHECKED": 12, "LABELLED": 50, "OPEN": 22, "UNFORMALISED": 9}
    cursor = 0
    for unit in doc["units"]:
        assert unit["span"][0] == cursor
        cursor = unit["span"][1]
        assert unit["source"].encode() == source[slice(*unit["span"])]
    assert cursor == len(source)

    checked = {u["id"]: u for u in doc["units"] if u["status"] == "CHECKED"}
    sets = doc["meta"]["reading_sets"]
    assert {s["unit"] for s in sets} == set(checked)
    for reading_set in sets:
        assert reading_set["status"] == "authored"
        assert reading_set["signature"] == "grant-author"
        assert len(reading_set["readings"]) == 1
        assert reading_set["readings"][0]["content"] == checked[reading_set["unit"]]["content"]


def test_admission_coverage_and_natural_roundtrip():
    path = ROOT / "document.ve.md"
    doc = load_document(path)
    result = check_document(path)
    coverage = result["coverage"]
    assert coverage["source_bytes"] == coverage["accounted_bytes"] == 7619
    assert coverage["coverage_percent"] == 100
    assert coverage["bytes_by_status"] == {
        "CHECKED": 780, "LABELLED": 3513, "OPEN": 2081, "UNFORMALISED": 1245}
    assert coverage["unformalised_reasons"] == {"causal_evidence": 8, "vague_comparison": 1}
    assert result["admission"]["admitted"] is True
    reported = {a["label"] for a in result["admission"]["report"]["assumptions"]}
    assert reported == {f"readings:{r['id']}@1:0" for r in doc["meta"]["reading_sets"]}

    natural_count = 0
    view = (ROOT / "natural-view.md").read_text()
    for unit in doc["units"]:
        assert f"### {unit['id']} · {unit['status']}" in view
        if unit["status"] != "CHECKED":
            continue
        formula = formula_from_data(doc["environment"], unit["content"])
        natural = render_natural_sentence(formula, doc["environment"],
                                          accept_suggested_vocabulary=True)
        natural_count += natural.natural
        assert natural.text + "." in view
        assert parse_english(doc["environment"], natural.text + ".",
                             accept_suggested_vocabulary=True) == Document((formula,))
    assert natural_count == 1
