"""fsf-repair-f2-glossary-1119: the legends of the measures the case asks for carry their FSF Glossary definitions.

Each sentence is read from the pinned FSF 3.1 text (tests/pinned_source.py), after the project's quote
normalisation (usecases/safetyfw_accounting.py `norm`: curly quotes made plain, whitespace collapsed), at its
Glossary entry, and must stand in quotes, byte for byte, in the committed legend of the named predicate
(environment.d1.json, what a reader is shown; tests/test_safety_framework.py checks it is vocabulary.py's output).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("safetyfw_accounting", REPO / "usecases" / "safetyfw_accounting.py")
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

GLOSSARY_START = "Frontier Safety Framework Glossary"

# predicate -> (the Glossary entry's label as the pinned text prints it, the number of its sentences quoted).
GLOSSARY_ENTRIES = {
    "assessed": ("Critical Capability Assessments: ", 1),
    "secured": ("Security Mitigations: ", 1),
    "residual_assessed": ("Residual Risk Assessments: ", 1),
    "within_levels": ("Residual Risk Assessments: ", 1),
    "frontier": ("Frontier AI Models or Models : ", 2),
}


def _legend(predicate: str) -> str:
    environment = json.loads((REPO / "usecases" / "safety-framework" / "environment.d1.json").read_text())
    return environment["vocabulary"]["predicates"][predicate]["description"]


def glossary_sentence(text: str, label: str, sentences: int) -> str:
    """The first `sentences` sentences after `label` in the Glossary of the normalised text, without the final full
    stop. The label must occur exactly once in the Glossary."""
    glossary = A.norm(text)[A.norm(text).index(GLOSSARY_START):]
    assert glossary.count(label) == 1, label
    start = glossary.index(label) + len(label)
    end = start
    for _ in range(sentences):
        end = glossary.index(". ", end) + 2
    return glossary[start:end - 2]


@pytest.mark.parametrize("predicate", sorted(GLOSSARY_ENTRIES))
def test_the_legend_quotes_the_pinned_glossary_sentence(predicate):
    """The condition test: the source sentence, quote-normalised, stands in quotes in the legend, cited to the
    Glossary (fails at 7cbec4b340b8, where these legends lacked it)."""
    text = pinned_source("safety-framework").read_text(encoding="utf-8")
    sentence = glossary_sentence(text, *GLOSSARY_ENTRIES[predicate])
    legend = _legend(predicate)
    # The quote closes after the sentence, or goes on with the entry's next source sentence (defs-repair-safety-
    # framework-1119 quotes the frontier entry whole: its audit row x1 runs on to the version sentences).
    longer = glossary_sentence(text, GLOSSARY_ENTRIES[predicate][0], GLOSSARY_ENTRIES[predicate][1] + 1)
    assert f'"{sentence}"' in legend or f'"{longer}' in legend, (predicate, sentence)
    assert "Glossary" in legend


def test_the_extracted_sentences_are_whole_definitions():
    """The extraction stops at the definition's own end, so a legend cannot pass on a prefix: the sentences named in
    the task, read from the source, end where the Glossary entry's definition ends."""
    text = pinned_source("safety-framework").read_text(encoding="utf-8")
    ends = {predicate: glossary_sentence(text, *entry).split()[-3:] for predicate, entry in GLOSSARY_ENTRIES.items()}
    assert ends == {
        "assessed": ["sources", "of", "evidence"],
        "secured": ["by", "unauthorized", "actors"],
        "residual_assessed": ["have", "been", "implemented"],
        "within_levels": ["have", "been", "implemented"],
        "frontier": ["other", "Google", "models"],
    }


def test_the_frontier_legend_no_longer_stands_in_for_the_definition():
    """Needs no source: OT9's legend gives the definition in place of the bare "(Glossary definition)" marker, and stays
    the open term OT9."""
    legend = _legend("frontier")
    assert "(Glossary definition)" not in legend
    assert legend.startswith("the model of {0} is a frontier AI model. Glossary: Frontier AI Models \"are trained on")
    assert legend.endswith(". Open term OT9, decided by no one the text names (unstated)")
