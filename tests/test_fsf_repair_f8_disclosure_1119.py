"""fsf-repair-f8-disclosure-1119 (repair row F8): the legends that carry FSF 3.1's 5.2 disclosure passage and its 5.1
review sentence, byte for byte after this project's quote normalisation.

The sentences are read from the pinned source (tests/pinned_source.py). The gate runner may not store that text
(tools/gate-optional.json), so each sentence is also frozen here by the SHA-256 of its normalised bytes: with the source
present the test reads the sentence from it and checks the hash; without it, the hash alone pins the legend's quote.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

from tests.pinned_source import pinned_source

HERE = Path(__file__).resolve().parents[1] / "usecases" / "safety-framework"


def _vocabulary():
    """usecases/safety-framework/vocabulary.py under its own module name (usecases/eligibility has modules with the
    same bare names, so it is never put in sys.modules as `vocabulary`)."""
    spec = importlib.util.spec_from_file_location("fsf_f8_vocabulary", HERE / "vocabulary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _quote_normal(text):
    """The project's quote normalisation: whitespace runs collapse to one space, curly quotes become straight ones."""
    return " ".join(text.split()).translate(str.maketrans("‘’“”", "''\"\""))


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Each source sentence: the pattern that finds it in the normalised pinned text (page 17, sections 5.1 and 5.2), the
# SHA-256 of its normalised bytes, the section the legend cites, and the predicates (with the block that uses each)
# whose legend carries it.
SENTENCES = {
    "S:17": (r"Where appropriate, and subject to adequate .*? how they are expected to reduce the risk\.",
             "83ac002b81786652af24d32f1b0b023f5224aa375b7269cc99e69dab3694c590", "5.2",
             {"shared": "f19-default"}),
    "5.1": (r"The process will involve \(i\) .*? \(ii\) an assessment of our adherence to the Framework\.",
            "93f6c9ba79bb69800642d92dff2fba22bb751deb272c03d54a8a555f0aa50d86", "5.1",
            {"yearly_review": "f18-yearly", "frequent_review": "f18-frequent"}),
}


def _blocks():
    """rules.d1.ve's blocks: id -> the block's body (its lines after the `## id | ...` header)."""
    blocks, current = {}, None
    for line in (HERE / "rules.d1.ve").read_text().splitlines():
        if line.startswith("## "):
            current = line[3:].split(" | ")[0].strip()
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)
    return {block: "\n".join(lines) for block, lines in blocks.items()}


@pytest.mark.parametrize("name", sorted(SENTENCES))
def test_each_new_legend_quotes_the_source_sentence_byte_for_byte(name):
    """Row F8: the sentence is in quotes, whole, in each carrier legend, in the vocabulary and in the committed
    environment.d1.json; the carrier is the legend of a predicate the target block uses (the CARRIER GUARD), a
    regulated predicate whose act that block's Rule line states."""
    pattern, digest, section, carriers = SENTENCES[name]
    source = pinned_source("safety-framework", skip=False)
    if source is not None:
        found = re.findall(pattern, _quote_normal(source.read_text(encoding="utf-8")))
        assert len(found) == 1 and _sha(found[0]) == digest
    vocabulary = _vocabulary()
    committed = json.loads((HERE / "environment.d1.json").read_text(encoding="utf-8"))["vocabulary"]["predicates"]
    blocks = _blocks()
    for predicate, block in carriers.items():
        for entry in (vocabulary.environment()["vocabulary"]["predicates"][predicate], committed[predicate]):
            quoted = re.findall(rf"\({re.escape(section)}: \"(.*)\"\)$", _quote_normal(entry["description"]))
            assert len(quoted) == 1 and _sha(quoted[0]) == digest, (predicate, quoted)
            assert entry["regulated"]["role"] == "obligation"
            assert f"Every proposal must {entry['regulated']['act'].removeprefix('{0} ')}" in blocks[block] or \
                f"Every proposal should {entry['regulated']['act'].removeprefix('{0} ')}" in blocks[block]
