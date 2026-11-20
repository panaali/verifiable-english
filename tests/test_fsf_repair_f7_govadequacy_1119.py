"""fsf-repair-f7-govadequacy-1119 (row F7): three FSF legends carry the pinned source's sentences, byte for byte after the
quote normalisation below. The governance finding's legend (OT3, the GOV atom) carries 2.1.2 step 2's adequacy sentence
(S:10). The `mitigates` legend (OT2, the "We assess" finding of the risk acceptance determination) carries the three
1.3.5 "We assess that the deployment mitigations have brought ..." sentences. The `acceptable` legend (the determination)
carries the first sentence of the 1.3.5 "To summarize" list. Each legend also stays inside the lines a line reader of its
vocabulary.py entry sees (the carrier guard: a legend counts only where such a reader finds it)."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "safety-framework"


def _load_vocabulary():
    spec = importlib.util.spec_from_file_location("fsf_f7_vocabulary", HERE / "vocabulary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vocabulary = _load_vocabulary()
GOV = "governance_found_acceptable_with_safety_case_where_ccl_reached"

# (predicate, the sentence's first words, its last words): each pair bounds exactly one sentence of the pinned source.
SENTENCES = (
    (GOV, "In particular, we will deem deployment mitigations adequate",
     "from the proposed external deployment has been reduced to an acceptable level."),
    ("mitigates", "We assess that the deployment mitigations have brought the residual risk of harm",
     "and the historical incidence and severity of related events."),
    ("mitigates", "We assess that the deployment mitigations have brought the residual risk of severe harm",
     "information pertaining to model propensities and the severity of related events."),
    ("mitigates", "We assess that the deployment mitigations have brought the residual risk of significant harm",
     "material risk of significant harm through misalignment risk."),
    ("acceptable", "A model for which inherent risk assessment indicates no T/CCL is reached",
     "substantially contribute to significant or severe risk scenarios."),
)


def _quote_normal(text):
    """The quote normalisation: whitespace runs collapse to one space, curly quotes become straight ones."""
    return " ".join(text.split()).translate(str.maketrans("‘’“”", "''\"\""))


def _legends():
    """Each predicate's legend twice: as vocabulary.py states it and as the committed environment.d1.json holds it."""
    committed = json.loads((HERE / "environment.d1.json").read_text())["vocabulary"]["predicates"]
    stated = vocabulary.environment()["vocabulary"]["predicates"]
    return {p: (_quote_normal(stated[p]["description"]), _quote_normal(committed[p]["description"]))
            for p, _, _ in SENTENCES}


def _source_sentence(text, first, last):
    found = re.findall(re.escape(first) + r"[^\n]*?" + re.escape(last), text)
    assert len(found) == 1, (first, found)
    assert not re.search(r"\. [A-Z]", found[0][len(first):-len(last)].replace("e.g. ", "")), found[0]
    return found[0]


def test_each_f7_legend_quotes_its_source_sentence_byte_for_byte():
    """The condition test of row F7: each sentence is read from the pinned source (not from a reader or a flag) and
    stands whole, in double quotes, in its predicate's legend, in the vocabulary and in environment.d1.json."""
    text = _quote_normal(pinned_source("safety-framework").read_text())
    legends = _legends()
    for predicate, first, last in SENTENCES:
        sentence = _source_sentence(text, first, last)
        for legend in legends[predicate]:
            assert f'"{sentence}"' in legend, (predicate, sentence)


def _entry_lines(key, lines):
    """The vocabulary.py lines a line reader takes for an entry: the key line, then lines while a parenthesis stays open
    or the next line continues a string (starts with a quote and is not another "name": key)."""
    start = next(i for i, line in enumerate(lines) if re.match(r'\s*"' + re.escape(key) + r'"\s*:', line))
    out, depth = [lines[start]], lines[start].count("(") - lines[start].count(")")
    for line in lines[start + 1:]:
        if depth <= 0 and not (line.lstrip().startswith('"') and not re.match(r'\s*"[a-z0-9_]+"\s*:', line)):
            break
        out.append(line)
        depth += line.count("(") - line.count(")")
    return out


def _strings(lines):
    """The string literals of some lines, adjacent ones joined, escaped quotes read as quotes."""
    joined = re.findall(r'"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*', "\n".join(lines))
    return [_quote_normal("".join(re.findall(r'"((?:[^"\\]|\\.)*)"', run)).replace('\\"', '"')) for run in joined]


@pytest.mark.parametrize("predicate", sorted({p for p, _, _ in SENTENCES}))
def test_each_f7_sentence_sits_in_the_lines_of_its_vocabulary_entry(predicate):
    """The carrier guard, without the source: each appended quote (found in the legend by its first words) is in one
    string of the lines a line reader takes for the predicate's vocabulary.py entry, so it is the predicate's legend
    there too, not text a reader of the entry misses (as the `acceptable` description was when it followed the
    "verbalisation" key on its own "description": line)."""
    legend = _quote_normal(vocabulary.environment()["vocabulary"]["predicates"][predicate]["description"])
    strings = _strings(_entry_lines(predicate, (HERE / "vocabulary.py").read_text().splitlines()))
    for p, first, last in SENTENCES:
        if p == predicate:
            quoted = re.findall('"(' + re.escape(first) + '[^"]*?' + re.escape(last) + ')"', legend)
            assert len(quoted) == 1, (predicate, first)
            assert any(f'"{quoted[0]}"' in s for s in strings), (predicate, first)
