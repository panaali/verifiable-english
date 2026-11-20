"""defs-repair-bluedot-grant-1119: the source's definitions are carried in the legends a reader is shown.

Each carried row of the 'definitions carried' audit (defs-bluedot-grant-1..7-1119) names a constant whose
legend (its vocabulary ``description`` in the front matter of ``document.ve.md`` or ``causal.ve.md``) must
contain one sentence of ``source.md`` byte for byte. The sentence is read from ``source.md`` here, by its line
and its opening words, never copied into this file, so a legend that drifts from the source fails.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pytest

from ve.document import front_matter

ROOT = Path(__file__).resolve().parents[1] / "usecases/bluedot-grant"
SOURCE_LINES = (ROOT / "source.md").read_text(encoding="utf-8").splitlines()

# (row, source line, the sentence's opening words): the audit's source_loc and quote.
G1 = (42, "VEX is presented as")  # note 4
G3 = (27, "The contribution here is an implementation and tests of mandatory proof:")  # NEW contribution
G5 = (39, "OLD text is copied from")  # note 1

# (row, carrier file, constant, source sentence)
ROWS = [
    ("defs-bluedot-grant-1-1119", "document.ve.md", "vex", G1),
    ("defs-bluedot-grant-2-1119", "document.ve.md", "mandatory_checked_proofs", G3),
    ("defs-bluedot-grant-3-1119", "document.ve.md", "guarantee", G3),
    ("defs-bluedot-grant-4-1119", "document.ve.md", "prevention", G3),
    ("defs-bluedot-grant-5-1119", "causal.ve.md", "mandatory_proof", G3),
    ("defs-bluedot-grant-6-1119", "document.ve.md", "old_text", G5),
]


def source_sentence(line: int, opening: str) -> str:
    """The sentence of source.md line ``line`` that begins with ``opening``, to its full stop."""
    text = SOURCE_LINES[line - 1]
    start = text.index(opening)
    end = re.compile(r"\.(\s|$)").search(text, start)
    assert end is not None, (line, opening)
    return text[start:end.start() + 1]


def norm(text: str) -> str:
    """Quote normalisation: NFKC, straight quotes and hyphens, collapsed whitespace, case folded."""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                                         "‐": "-", "‑": "-", "–": "-", "—": "-"}))
    return " ".join(text.split()).casefold()


def constants(name: str) -> dict:
    meta, _ = front_matter((ROOT / name).read_bytes())
    return meta["environment"]["vocabulary"]["constants"]


def test_source_sentences_are_the_audit_spans():
    # The full definitional spans, from sentence boundary to sentence boundary.
    assert source_sentence(*G1) == ("VEX is presented as proposed mandatory evidence for statistical and "
                                    "approximate claims.")
    g3 = source_sentence(*G3)
    assert g3.endswith("by excluding assumed false sub-claims.") and g3 == SOURCE_LINES[58]  # :27 = :59
    assert source_sentence(*G5) == "OLD text is copied from FORM-EDITS-2026-09-21.md, the current form text."


@pytest.mark.parametrize("row, carrier, constant, sentence", ROWS, ids=[r[0] for r in ROWS])
def test_legend_carries_the_source_definition(row, carrier, constant, sentence):
    quote = source_sentence(*sentence)
    description = constants(carrier)[constant]["description"]
    assert quote in description, (row, description)
    assert norm(quote) in norm(description), row


def test_old_text_speaker_names_the_constant_whose_legend_carries_g5():
    # Row 7: the attribution speaker `old_text` of u003, u030 and u032 is the token of the declared
    # constant `old_text`, so the legend a reader looks up for the speaker is row 6's.
    meta, _ = front_matter((ROOT / "document.ve.md").read_bytes())
    units = {u["id"]: u for u in meta["units"]}
    for uid in ("u003", "u030", "u032"):
        assert units[uid]["kind"][:2] == ["attributed", "old_text"], uid
    assert source_sentence(*G5) in meta["environment"]["vocabulary"]["constants"]["old_text"]["description"]
