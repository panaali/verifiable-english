"""defs-repair-udhr-pilot-1119: the saved record of the three P1 'definitions carried' rows of the UDHR pilot.

Each row's definition is read from the source (the translation's body) byte for byte; a row recorded CARRIED has the
whole definition in one legend run of its carrier, and a row recorded NOT CARRIED does not, so the record cannot go
stale silently. The rows stay NOT CARRIED because the only carrier, the translation's front matter, belongs to a
sealed, measured run: `migrate.py` reproduces it byte for byte from a SHA-256-pinned snapshot and `metrics.json`
measured exactly its bytes. Reads saved files only; no Git, no Lean.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "docs/usecases/udhr-pilot/defs-repair-udhr-pilot-1119/rows.json"
RUN = ROOT / "usecases/udhr-pilot/run-20261010T1400Z"
DOCUMENT = RUN / "translation.ve.md"
AUDIT_P1_ROWS = ("defs-udhr-pilot-1-1119", "defs-udhr-pilot-2-1119", "defs-udhr-pilot-3-1119")
SEALED = "the only carrier is the front matter of a sealed, measured run's translation"


def record():
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def document():
    """(front matter, body bytes) of the translation: line 2 is the JSON front matter, the body is the source."""
    raw = DOCUMENT.read_bytes()
    assert raw.startswith(b"---\n")
    head, body = raw[4:].split(b"\n---\n", 1)
    return json.loads(head), body


def quote_norm(text):
    """The counter's quote normalisation (defs-carried METHOD step 3): NFKC, curly quotes and dashes, case, spaces,
    line-break hyphens."""
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("—", "-"),
                 ("–", "-"), ("‑", "-"), ("‐", "-"), ("…", "..."), ("‚", ",")):
        text = text.replace(a, b)
    text = re.sub(r"\s+", " ", text.lower()).strip()
    return re.sub(r"(?<=[a-z])- (?=[a-z])", "", text)


def carrier_runs(meta, carrier):
    """The legend runs a reader is shown for the row's term: a predicate's description, or an open term's factors."""
    if carrier["kind"] == "predicate-description":
        return [meta["environment"]["vocabulary"]["predicates"][carrier["key"]]["description"]]
    assert carrier["kind"] == "open-term-factors", carrier
    (term,) = [entry for entry in meta["open_terms"] if entry["name"] == carrier["key"]]
    return list(term["factors"]) + ([term["description"]] if "description" in term else [])


def test_the_record_holds_exactly_the_audits_p1_rows():
    rows = record()["rows"]
    assert tuple(row["id"] for row in rows) == AUDIT_P1_ROWS
    for row in rows:
        assert row["verify"] in ("KEPT", "DROPPED") and row["carry"] in ("CARRIED", "NOT CARRIED"), row
        assert row["quote"].strip() and row["rules"], row
        assert row["carry"] == "CARRIED" or row["reason"].strip(), row


@pytest.mark.parametrize("row_id", AUDIT_P1_ROWS)
def test_a_kept_rows_definition_is_the_source_sentence_byte_for_byte(row_id):
    (row,) = [row for row in record()["rows"] if row["id"] == row_id]
    assert row["verify"] == "KEPT"
    _, body = document()
    quote = row["quote"].encode("utf-8")
    assert body.count(quote) == 1, row_id
    line = DOCUMENT.read_bytes().split(b"\n")[row["source_line"] - 1]
    assert quote in line, (row_id, line[:80])
    # a sentence boundary on each side: the full span, never a clause of it
    start = line.index(quote)
    assert re.fullmatch(rb"(\d+\. )?", line[:start]) or line[:start].endswith(b". "), row_id
    assert quote.endswith(b".")


@pytest.mark.parametrize("row_id", AUDIT_P1_ROWS)
def test_a_rows_rules_use_its_term(row_id):
    (row,) = [row for row in record()["rows"] if row["id"] == row_id]
    meta, _ = document()
    units = {unit["id"]: unit for unit in meta["units"]}
    carrier = row["carrier"]
    for rule in row["rules"]:
        unit = units[rule]
        assert unit["kind"] == "norm", rule
        if carrier["kind"] == "open-term-factors":
            assert carrier["key"] in unit["meaning"]["open"], rule
        else:  # the predicate is reached through the unit's reading set (the audit's tie of predicate to rule)
            (reading_set,) = [rs for rs in meta["reading_sets"] if rs["unit"] == rule]
            assert carrier["key"] in json.dumps(reading_set), rule


@pytest.mark.parametrize("row_id", AUDIT_P1_ROWS)
def test_a_rows_carry_verdict_matches_its_carrier(row_id):
    """CARRIED: the whole normalised definition is in one legend run; NOT CARRIED: it is in none."""
    (row,) = [row for row in record()["rows"] if row["id"] == row_id]
    meta, _ = document()
    quote = quote_norm(row["quote"])
    carried = any(quote in quote_norm(run) for run in carrier_runs(meta, row["carrier"]))
    assert carried == (row["carry"] == "CARRIED"), (row_id, row["carry"])


def test_a_row_left_not_carried_for_the_seal_names_a_sealed_measured_run():
    """The seal the NOT CARRIED rows rest on: the migration's input is pinned and the measured run read these bytes."""
    rows = [row for row in record()["rows"] if row["carry"] == "NOT CARRIED"]
    assert all(row["reason"].startswith(SEALED) for row in rows)
    if not rows:
        return
    pin = re.search(r'^FROZEN_SHA256 = "([0-9a-f]{64})"$', (RUN / "migrate.py").read_text(), re.M).group(1)
    assert hashlib.sha256((RUN / "frozen-run.json").read_bytes()).hexdigest() == pin
    metrics = json.loads((RUN / "metrics.json").read_text())
    assert metrics["after"]["document_bytes"] == len(DOCUMENT.read_bytes())
    test, name = record()["sealed_by"]["reproduction_test"].split("::")
    assert f"def {name}(" in (ROOT / test).read_text()
