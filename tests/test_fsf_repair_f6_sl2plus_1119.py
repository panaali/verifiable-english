"""fsf-repair-f6-sl2plus-1119 (row F6): the `recommends` legend carries the source's Security Level 2+, 3 and 4 text.

The FSF's own words for the recommended security levels are 2.1.1's Security Level 2+ sentence (source line 9) and,
on table 3.2.2.a (source line 15), the Security level 3 and 4 recommendations with their footnote marks 12 and 13 and
the two footnotes. Each sits, quoted byte for byte, in the legend of `recommends`: a predicate the FACTS unit uses
(every level's "recommends" fact), so the legend is a counted carrier for every answer that reads FACTS. The
sentences are read from the pinned source here, never from this file.
"""
import importlib.util
import json
import re
from pathlib import Path

from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "safety-framework"

# Each pattern finds one sentence (or the table cell with its footnote mark) in the normalised pinned source.
SOURCE_PATTERNS = {
    "S:9 Security Level 2+": r'We also define and recommend "Security Level 2\+," which uses RAND Security Level 2 '
                             r'\(SL2\) as a baseline, [^.]*\.',
    "S:15 Security level 3 cell": r"Security level 3 12",
    "S:15 footnote 12": r"12 This level may include [^.]*\.",
    "S:15 Security level 4 sentence": r"We recommend Security level 4 13 [^.]*\.",
    "S:15 footnote 13": r"13 This level may include [^.]*\.",
}


def _vocabulary():
    spec = importlib.util.spec_from_file_location("fsf_f6_vocabulary", HERE / "vocabulary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _quote_normal(text):
    """The project's quote normalisation: whitespace runs collapse to one space, curly quotes become straight ones."""
    return " ".join(text.split()).translate(str.maketrans("‘’“”", "''\"\""))


def _legends():
    """The `recommends` legend as the vocabulary writes it and as environment.d1.json commits it."""
    written = _vocabulary().environment()["vocabulary"]["predicates"]["recommends"]
    committed = json.loads((HERE / "environment.d1.json").read_text())["vocabulary"]["predicates"]["recommends"]
    return written, committed


def test_the_recommends_legend_quotes_the_security_level_sentences_whole():
    """Condition test of row F6: each source sentence occurs once in the pinned source and, quoted whole, in the
    `recommends` legend (written and committed); the base legend and its verbalisation stay."""
    text = _quote_normal(pinned_source("safety-framework").read_text())
    sentences = {}
    for name, pattern in SOURCE_PATTERNS.items():
        found = re.findall(pattern, text)
        assert len(found) == 1, (name, found)
        sentences[name] = found[0]
    assert sentences["S:9 Security Level 2+"].endswith("from insider threats and well-resourced non-state external "
                                                       "actors.")
    assert sentences["S:15 footnote 12"].endswith("prevent data exfiltration.")
    assert sentences["S:15 footnote 13"].endswith("minimizing potential attack surface.")
    for entry in _legends():
        legend = _quote_normal(entry["description"])
        assert [name for name, sentence in sentences.items() if f'"{sentence}"' not in legend] == []
        assert legend.startswith("the framework recommends {1} for models reaching {0} (tables 2.2.1.a to 3.2.2.a). ")
        assert entry["verbalisation"] == "{0} recommends {1}" and entry["arguments"] == ["level", "measure"]


def test_the_recommends_legend_is_a_carrier_of_the_facts_unit():
    """The carrier guard: the legend is that of a predicate the FACTS unit uses, for each of the three security
    levels the legend describes, and the committed environment is the vocabulary's own output."""
    facts = (HERE / "facts.d1.ve").read_text()
    for measure in ("security_level_2_plus", "security_level_3", "security_level_4"):
        assert re.search(rf'" recommends "{measure}"\.', facts), measure
    written, committed = _legends()
    assert written == committed
