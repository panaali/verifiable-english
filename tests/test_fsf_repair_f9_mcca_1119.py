"""fsf-repair-f9-mcca-1119 (row F9): two 1.3.2 sentences of the pinned FSF 3.1 text, verbatim, in the legends of the
predicates the target answers' blocks use.

- G6 (SILENT:CCA, a model not on the frontier) reads block f3, whose act is `assessed` ("be preceded by a critical
  capability assessment"): its legend carries "We may also apply material capability change assessments to models not
  on the frontier, to understand whether a critical capability assessment is required."
- K4/CHECKPOINT_MCCA reads block f5, whose act is `change_assessed`: its legend carries the MCCA content, "These
  assessments draw on model characteristics, such as its provenance, size, modality, and performance on general
  capability benchmarks."

Each sentence is read from the pinned source (tests/pinned_source.py), never written here; the check is on the legend
vocabulary.py computes and on the committed environment.d1.json, after the project's quote normalisation (whitespace
runs collapse to one space, curly quotes become straight ones).
"""
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

import pytest

from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "safety-framework"

# predicate -> (the rule block of the target answer that uses it, the start of the 1.3.2 sentence its legend carries)
CARRIED = {
    "assessed": ("f3", "We may also apply material capability change assessments to models not on the frontier"),
    "change_assessed": ("f5", "These assessments draw on model characteristics"),
}


def _quote_normal(text):
    return " ".join(text.split()).translate(str.maketrans("‘’“”", "''\"\""))


def _own(name):
    """`name` from usecases/safety-framework, loaded apart (usecases/eligibility has modules with the same names)."""
    saved = {n: sys.modules.pop(n) for n in ("vocabulary", "translation") if n in sys.modules}
    sys.path.insert(0, str(HERE))
    try:
        return importlib.import_module(name)
    finally:
        sys.path.remove(str(HERE))
        for n in ("vocabulary", "translation"):
            sys.modules.pop(n, None)
        sys.modules.update(saved)


VOCABULARY = _own("vocabulary")
TRANSLATION = _own("translation")


def _source_sentence(text, start):
    found = re.findall(re.escape(start) + r"[^.]*\.", text)
    assert len(found) == 1, (start, found)
    return found[0]


def _legends(predicate):
    computed = VOCABULARY.environment()["vocabulary"]["predicates"][predicate]
    committed = json.loads((HERE / "environment.d1.json").read_text())["vocabulary"]["predicates"][predicate]
    return computed, committed


@pytest.mark.parametrize("predicate", sorted(CARRIED))
def test_the_legend_quotes_the_pinned_1_3_2_sentence_byte_for_byte(predicate):
    """Row F9: the sentence, read whole from the pinned source, stands quoted in the legend (computed and committed)."""
    text = _quote_normal(pinned_source("safety-framework").read_text(encoding="utf-8"))
    sentence = _source_sentence(text, CARRIED[predicate][1])
    for entry in _legends(predicate):
        assert f'"{sentence}"' in _quote_normal(entry["description"])


@pytest.mark.parametrize("predicate", sorted(CARRIED))
def test_the_legend_is_a_counted_carrier_of_the_target_block(predicate):
    """CARRIER GUARD: the legend counts only as the legend of a predicate the block uses, i.e. the block's rule body
    holds the predicate's act template (the counter's used_predicates match). The legend keeps its act and role."""
    block_id = CARRIED[predicate][0]
    body = next(b.text for b in TRANSLATION.rule_blocks() if b.id == block_id)
    for entry in _legends(predicate):
        act = re.sub(r"^\{0\}\s*", "", entry["regulated"]["act"])
        pattern = re.sub(r"\\\{\d\\\}", ".+?", re.escape(act))
        assert re.search(r"(?<![A-Za-z])" + pattern + r"(?![A-Za-z])", body), (block_id, act)
        assert entry["regulated"]["role"] == "obligation"
