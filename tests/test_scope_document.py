"""SC-1b: the Lean document mode admits `scope@0` (docs/spec/scope.md 5.2, 7.2) on the F1 part document, the pinned
constitution's hard-constraint block (u0164.s01-u0166.s01) rewritten with the lead-in's part and seven item parts.
Lean governs and folds the statuses; Python relays the case and builds the document from the bound answer (R8)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ve import document as D
from ve.backends.relay import answer

F1 = Path(__file__).parent / "data/scope/hard-constraints.ve.md"
ITEMS = [f"u0165.s0{i}" for i in range(1, 8)]


def _split(text: str):
    front, body = text[4:].split("\n---\n", 1)
    return json.loads(front), body


def _text(meta: dict, body: str) -> str:
    return "---\n" + json.dumps(meta, ensure_ascii=False) + "\n---\n" + body


def _rows(text: str):
    row, error = answer("document", {"id": "d", "document": text, "admit": True})
    return ({u["id"]: u for u in row["units"]}, row) if error is None else (None, str(error))


def _written_in_full(meta: dict) -> dict:
    """The block as the translation writes it today: each rule in full, no lead-in part, no scope@0."""
    meta = json.loads(json.dumps(meta))
    lead = meta.pop("scope")["governors"][0]["effect"]["frame"]
    meta["environment"]["profiles"].remove("scope@0")
    for unit in meta["units"]:
        if "part" in unit.get("content", {}):
            unit["content"] = {"norm": {**unit["content"]["part"], **lead}}
        if unit["id"] == "u0164.s02":
            unit.update(kind=["unformalised", "norms"], meaning={"unformalised": "norms"})
    return meta


def test_f1_doc_the_lead_in_takes_its_items_status_and_each_item_is_its_rule_in_full():
    meta, body = _split(F1.read_text())
    rows, _ = _rows(F1.read_text())
    today, _ = _rows(_text(_written_in_full(meta), body))
    assert rows["u0164.s02"]["status"] == "OPEN" and today["u0164.s02"]["status"] == "UNFORMALISED"
    assert all(rows[u] == today[u] for u in ITEMS)  # the seven rows byte for byte, statuses OPEN
    assert {rows[u]["status"] for u in ITEMS} == {"OPEN"}


def test_f1_bad_an_item_not_admitted_leaves_the_lead_in_unformalised():
    meta, body = _split(F1.read_text())
    unit = next(u for u in meta["units"] if u["id"] == "u0165.s02")
    unit.pop("content")
    unit.update(kind=["unformalised", "norms"], meaning={"unformalised": "norms"})
    rows, row = _rows(_text(meta, body))
    assert rows["u0164.s02"]["status"] == "UNFORMALISED"
    assert row["coverage"]["bytes_by_status"] == {"OPEN": 896 - 139 - 22, "UNFORMALISED": 472 + 139 + 22}


def test_f1_off_without_scope_the_document_is_answered_as_before():
    meta, body = _split(F1.read_text())
    meta["environment"]["profiles"].remove("scope@0")
    assert _rows(_text(meta, body))[1] == "unknown document metadata"
    del meta["scope"]
    assert _rows(_text(meta, body))[1] == "unit fence must match its id"


@pytest.mark.parametrize("profiles, text", [
    (["alternatives@0", "norms@0", "relational-fol@0", "scope@0"], "UnsupportedProfile: scope@0 with alternatives@0"),
    (["relational-fol@0", "scope@0"], "UnsupportedProfile: scope@0 requires norms@0")])
def test_the_profile_tables_scope_row_refuses_first(profiles, text):
    meta, body = _split(F1.read_text())
    meta["environment"]["profiles"] = profiles
    assert _rows(_text(meta, body))[1] == text


def test_ve_document_check_builds_the_governed_document_from_the_bound_answer(tmp_path):
    path = tmp_path / "f1.ve.md"
    path.write_text(F1.read_text())
    units = {u["id"]: u for u in D.load_document(path)["units"]}
    assert units["u0164.s02"]["status"] == "OPEN"
    assert [units[u]["content"]["norm"]["name"] for u in ITEMS[:2]] == ["hc-cbrn-uplift", "hc-infrastructure-uplift"]
    assert D.check_document(path)["coverage"]["bytes_by_status"] == {"OPEN": 896, "UNFORMALISED": 472}
