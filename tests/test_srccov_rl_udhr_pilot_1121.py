"""srccov-rl-udhr-pilot-1121: the saved record of the UDHR pilot's 'none: translation omission' units.

The source-coverage map (pin e53db4e8fc) tags 37 UDHR units 'none: translation omission'. The record keeps each unit
that still holds and drops the rest, with a reason the test can check against the files. A kept unit stays NOT
CARRIED. Its only carrier is the front matter of the sealed, measured run `run-20261010T1400Z`, and a sealed run is
never rewritten in place. The test keeps the record honest in both directions. A kept unit's quote is its source
sentence, byte for byte. Its front-matter units still have no VE body: an in-place carry fails this test, and so does
the seal check. Reads saved files only; no Git, no Lean.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "docs/infra/srccov-rl-udhr-pilot-1121/units.json"
RUN = ROOT / "usecases/udhr-pilot/run-20261010T1400Z"
DOCUMENT = RUN / "translation.ve.md"
EVIDENCE = ROOT / "docs/premise-scale/evidence/ab-documents.json"
SEALED = "the only carrier is the front matter of a sealed, measured run's translation (run-20261010T1400Z)"

# The map's units tagged 'none: translation omission' (part-udhr-pilot-s4.tsv) and the candidate row of each.
MAP_UNITS = {
    "S0014": 3, "S0015": 4, "S0016": 5, "S0017": 5, "S0018": 6, "S0019": 7, "S0021": 8, "S0022": 9, "S0023": 10,
    "S0028": 13, "S0029": 13, "S0030": 14, "S0031": 14, "S0032": 15, "S0033": 15, "S0034": 16, "S0035": 16,
    "S0038": 17, "S0040": 18, "S0041": 18, "S0042": 19, "S0044": 20, "S0046": 21, "S0047": 21, "S0048": 22,
    "S0049": 22, "S0053": 24, "S0056": 24, "S0061": 27, "S0063": 27, "S0064": 27, "S0065": 27, "S0068": 28,
    "S0071": 30, "S0072": 30, "S0073": 30, "S0074": 31,
}
DROPPED = {"S0047": "already-carried", "S0048": "needs-feature", "S0071": "needs-feature", "S0072": "needs-feature"}


def record():
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def entry(unit_id):
    (row,) = [row for row in record()["units"] if row["unit"] == unit_id]
    return row


def document():
    """(front matter, body bytes) of the translation: line 2 is the JSON front matter, the body is the source."""
    raw = DOCUMENT.read_bytes()
    assert raw.startswith(b"---\n")
    head, body = raw[4:].split(b"\n---\n", 1)
    return json.loads(head), body


def quote_norm(text):
    """The counter's quote normalisation (defs-carried METHOD step 3): NFKC, curly quotes and dashes, case, spaces."""
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("—", "-"), ("–", "-")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text.lower()).strip()


def front_matter_units():
    meta, _ = document()
    return {unit["id"]: unit for unit in meta["units"]}


def test_the_record_holds_exactly_the_maps_omission_units_and_their_rows():
    rows = record()["units"]
    assert [row["unit"] for row in rows] == sorted(MAP_UNITS)
    for row in rows:
        assert row["row"] == f"srccov-udhr-pilot-s4-{MAP_UNITS[row['unit']]}-1119", row["unit"]
        assert row["verify"] == ("DROPPED" if row["unit"] in DROPPED else "KEPT"), row["unit"]
        assert row["reason"].strip(), row["unit"]


@pytest.mark.parametrize("unit_id", sorted(MAP_UNITS))
def test_a_units_quote_is_its_source_sentence_byte_for_byte(unit_id):
    row = entry(unit_id)
    _, body = document()
    start, end = row["body_bytes"]
    quote = row["quote"].encode("utf-8")
    assert body[start:end] == quote, unit_id
    line = DOCUMENT.read_bytes().split(b"\n")[row["source_line"] - 1]
    assert quote in line, unit_id
    # the recorded front-matter units are exactly the ones whose span meets the sentence
    meta, _ = document()
    meets = [u["id"] for u in meta["units"] if u["span"][0] < end and u["span"][1] > start]
    assert row["front_matter_units"] == meets, unit_id


@pytest.mark.parametrize("unit_id", sorted(set(MAP_UNITS) - set(DROPPED)))
def test_a_kept_unit_is_still_an_omission_at_main(unit_id):
    """Kept: every covering unit is a norm with no VE body; the formal content sits only in its reading set."""
    row = entry(unit_id)
    assert row["carry"] == "NOT CARRIED" and row["reason"].startswith(SEALED), unit_id
    units = front_matter_units()
    meta, _ = document()
    sets = {rs["unit"]: rs["id"] for rs in meta["reading_sets"]}
    assert row["front_matter_units"], unit_id
    for uid in row["front_matter_units"]:
        assert units[uid]["kind"] == "norm" and "content" not in units[uid], (unit_id, uid)
    assert row["reading_sets"] == [sets[uid] for uid in row["front_matter_units"]], unit_id


@pytest.mark.parametrize("unit_id", sorted(DROPPED))
def test_a_dropped_units_reason_holds_in_the_files(unit_id):
    row = entry(unit_id)
    assert row["drop_class"] == DROPPED[unit_id] and "carry" not in row, unit_id
    assert row["blocking_text"] in row["quote"], unit_id
    units = front_matter_units()
    if row["drop_class"] == "already-carried":
        (uid,) = row["front_matter_units"]
        unit = units[uid]
        assert unit.get("status") == "CHECKED", uid
        norm = unit["content"]["norm"]
        assert norm["sign"] is False and norm["guard"] == ["top"] and norm["unless"] == [], uid
        meta, _ = document()
        legend = meta["environment"]["vocabulary"]["predicates"][norm["predicate"]]
        assert legend["regulated"]["default"] == "allow", uid
        act = legend["regulated"]["act"].replace("{0} ", "").replace("{1} ", "")  # "compel to belong to ..."
        assert quote_norm(row["blocking_text"]) in quote_norm(act), uid
        assert quote_norm(row["blocking_text"]) in quote_norm(legend["description"]), uid
    elif unit_id == "S0048":
        (uid,) = row["front_matter_units"]
        assert units[uid]["kind"][0] == "unformalised", uid
    else:  # a feature no declared profile has: possibility (S0071) or a purpose clause (S0072)
        meta, _ = document()
        assert not {"modality@0", "events@0"} & set(meta["environment"]["profiles"])
        assert re.search(r"\b(is possible|for the purpose of)\b", row["blocking_text"]), unit_id


def test_the_seal_the_not_carried_units_rest_on_still_holds():
    """The migration's input is pinned, the measured run read these bytes, and the evidence pins their hash."""
    rec = record()
    raw = DOCUMENT.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert rec["carrier_sha256"] == digest
    assert digest in EVIDENCE.read_text(encoding="utf-8")
    pin = re.search(r'^FROZEN_SHA256 = "([0-9a-f]{64})"$', (RUN / "migrate.py").read_text(), re.M).group(1)
    assert hashlib.sha256((RUN / "frozen-run.json").read_bytes()).hexdigest() == pin
    metrics = json.loads((RUN / "metrics.json").read_text())
    assert metrics["after"]["document_bytes"] == len(raw)
    test, name = rec["sealed_by"]["reproduction_test"].split("::")
    assert f"def {name}(" in (ROOT / test).read_text()
