"""fsf-repair-f1-leveldefs-1119: every capability level of the safety-framework case carries its source definition.

The predicate `defined` has one legend (its description in environment.d1.json) that names each level `L` of
vocabulary.LEVELS and quotes, right after it, the level's defining sentence from its table or section; one fact
`"L" is defined.` of the level's `levels-*` block in facts.d1.ve uses the predicate, so that block shows the legend
(the carrier rule of reviews/pathf-q3/flag-analysis-1119/converge-AB.md section 0: a legend of a predicate the block
uses, never the LEVELS constant string or the block's "## " header). One predicate for all levels, because the
identifier lint P7 (run.identifier_lint) refuses a predicate name that packs a level. The sentence is read from the
pinned source, never from here.
"""
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

import pytest

from tests.pinned_source import pinned_source
from tools.fidmech.segment import norm

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "safety-framework"
OWN_NAMES = ("vocabulary", "translation")


def _load_own_modules():
    """The case's modules by their bare names, loaded apart (tests/test_safety_framework.py does the same)."""
    saved = {name: sys.modules.pop(name) for name in OWN_NAMES if name in sys.modules}
    sys.path.insert(0, str(HERE))
    try:
        return {name: importlib.import_module(name) for name in OWN_NAMES}
    finally:
        sys.path.remove(str(HERE))
        for name in OWN_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


OWN = _load_own_modules()
translation, vocabulary = OWN["translation"], OWN["vocabulary"]

# Where each level's definition starts in the extracted source: the label before it (the table row's or the
# section's "is defined as follows" line). Labels only: the sentence itself is read from the source.
SOURCE_LABELS = {
    "cbrn_uplift_tcl": "CBRN uplift TCL :",
    "cbrn_uplift_level_1": "CBRN uplift level 1:",
    "cyber_uplift_level_1": "Cyber uplift level 1:",
    "harmful_manipulation_level_1": "Harmful manipulation level 1 (exploratory):",
    "stealth_and_situational_awareness_tcl": "Stealth and Situational Awareness TCL :",
    "ml_rd_acceleration_level_1": "ML R&D acceleration level 1:",
    "ml_rd_automation_level_1": "ML R&D automation level 1:",
}


def _committed_legends():
    return json.loads((HERE / "environment.d1.json").read_text())["vocabulary"]["predicates"]


def level_entries(legend):
    """{level: its part of the `defined` legend}: from the level's name, where it starts an entry ("<level> is "), up to
    the next level's entry."""
    starts = sorted((m.start(), level) for level in vocabulary.LEVELS
                    for m in re.finditer(r"(?<![a-z_])" + re.escape(level) + r" is ", legend))
    assert [level for _, level in starts] == list(vocabulary.LEVELS), starts  # each once, in the LEVELS order
    ends = [at for at, _ in starts[1:]] + [len(legend)]
    return {level: legend[at:end] for (at, level), end in zip(starts, ends)}


def _block_of(level):
    """The one `levels-*` fact block that states the level's class facts."""
    blocks = [b for b in translation.read_blocks("facts.d1.ve")
              if b.id.startswith("levels-") and f'"{level}" is ' in b.text]
    assert len(blocks) == 1, (level, [b.id for b in blocks])
    return blocks[0]


def source_definitions(text):
    """{level: its defining sentence}: the words after the level's label up to the first full stop that ends a
    sentence. Each label occurs exactly once in the source."""
    out = {}
    for level, label in SOURCE_LABELS.items():
        assert text.count(label) == 1, (level, text.count(label))
        m = re.compile(re.escape(label) + r" (.+?\.)(?= |\n|$)").search(text)
        assert m is not None, level
        out[level] = m[1]
    return out


def test_every_level_has_its_definition_in_the_legend_of_a_predicate_its_block_uses():
    """Hermetic part: the `defined` legend has one entry per level that cites the level's own table or section and
    quotes one sentence, and each level's `levels-*` block has the fact that uses the predicate (so the legend is
    shown with that block)."""
    assert set(SOURCE_LABELS) == set(vocabulary.LEVELS)
    entry = _committed_legends()["defined"]
    assert entry == vocabulary.environment()["vocabulary"]["predicates"]["defined"]
    assert entry["arguments"] == ["level"] and entry["verbalisation"] == "{0} is defined" and "regulated" not in entry
    assert entry["description"].startswith("{0} is a capability level that the framework defines in its own words")
    for level, part in level_entries(entry["description"]).items():
        citation = re.search(r"\(((?:table )?\d+(?:\.\d+)+(?:\.[a-z])?)\)$", vocabulary.LEVELS[level])[1]
        assert f"({citation}), defined as \"" in part, level
        assert len(re.findall(r'"[A-Z][^"]+\."', part)) == 1, level
        block = _block_of(level)
        assert f'"{level}" is defined.' in block.text, (level, block.id)
        formulas = dict(translation.fact_formulas())[block.id]
        assert any(getattr(f, "predicate", None) == "defined" and f.term.name == level for f in formulas), level
    # The fact is in its level's own block only.
    for level in vocabulary.LEVELS:
        holders = [b.id for b in translation.read_blocks("facts.d1.ve") if f'"{level}" is defined.' in b.text]
        assert holders == [_block_of(level).id], level


def test_every_level_legend_quotes_the_pinned_source_definition_verbatim():
    """The condition test: each legend contains its level's source sentence byte for byte after the project's quote
    normalisation (tools/fidmech/segment.py norm: whitespace, quote styles, dashes and ligatures folded; digits kept,
    so the footnote mark 8 inside CBRN uplift level 1 must be there)."""
    text = pinned_source("safety-framework").read_text(encoding="utf-8")
    sentences = source_definitions(text)
    assert len(sentences) == 7
    assert " additional 8 expected harm at severe scale." in sentences["cbrn_uplift_level_1"]
    built = vocabulary.environment()["vocabulary"]["predicates"]["defined"]["description"]
    committed = _committed_legends()["defined"]["description"]
    missing = [level for legend in (built, committed) for level, part in level_entries(legend).items()
               if f'"{norm(sentences[level])}"' not in norm(part)]
    assert missing == []


def test_the_source_definitions_reader_takes_the_whole_sentence_and_one_label_only():
    """source_definitions on a small text: the sentence ends at its full stop (a mark inside stays), and a label that
    is missing or occurs twice is refused."""
    text = "x " + " ".join(f"{label} Has words {i} inside it. Next." for i, label in enumerate(SOURCE_LABELS.values()))
    got = source_definitions(text)
    assert got["cbrn_uplift_level_1"] == "Has words 1 inside it."
    with pytest.raises(AssertionError):
        source_definitions(text.replace("Cyber uplift level 1:", "Cyber uplift level one:"))
    with pytest.raises(AssertionError):
        source_definitions(text + " CBRN uplift TCL : again.")
