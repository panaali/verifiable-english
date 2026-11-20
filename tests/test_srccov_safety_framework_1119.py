"""srccov-safety-framework-1119: the FSF source sentences the source-coverage map found ABSENT, carried word for word.

Each kept unit of the map (manage-agents reviews/source-coverage-1119/rows-safety-framework.tsv, rows 5, 13, 14, 16,
17, 20, 24-27 and 30-33) is read from the pinned FSF 3.1 text (tests/pinned_source.py) at its UTF-8 byte span, after the
project's quote normalisation (usecases/safetyfw_accounting.py `norm`). Its section heading or Glossary label, a list
bullet and the one PDF running head inside a span are cut by their exact strings; the rest must stand in quotes, byte
for byte, in the committed legend of the named predicate (environment.d1.json, what a reader is shown), after the same
normalisation. The quoted passage may be the sentence alone or a longer one holding it whole (bounded by the passage's
ends or spaces): a definition quoted whole with its label or footnote mark (defs-repair-safety-framework-1119) carries it.
Inner quotes are curly (that branch's escape guard), so the legend's straight quotes open and close its passages.

A legend carries only when a reader is shown it: the predicate is used by a block of rules.d1.ve or facts.d1.ve (the
counter's `used_predicates`, tests/omission_rule.py), it is not an open term (METHOD amendment 4: an open term carries
nothing), the quote is outside any parenthesised citation, and its words are in the counter's raw read of the
vocabulary.py entry (`legend_raw`), not behind a variable.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from tests import omission_rule as O
from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "usecases" / "safety-framework"


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A = _module("safetyfw_accounting", REPO / "usecases" / "safetyfw_accounting.py")

RUNNING_HEAD = "Frontier Safety Framework | 18 Frontier Safety Framework "

# unit -> (predicate, UTF-8 byte span in the pinned text, the heading or label cut before the sentence, the last words).
CARRIES = {
    "S0022": ("misuse", (3027, 3168), "2 ", "models to cause harm."),
    "S0159": ("misuse", (31869, 31973), "8 ", "baseline without generative AI."),
    "S0203": ("ml_rd_and_misalignment", (40534, 40693), "3.2.2 ML R&D Critical Capability Levels ",
              "may reach a severe scale."),
    "S0009": ("critical", (1063, 1378), "", "approaches to address such risks."),
    "S0249": ("critical", (48178, 48308), "Thresholds Critical Capability Levels (CCLs): ",
              "built the Framework process."),
    "S0012": ("assessed", (1613, 1758), "", "reasoning, and scientific understanding."),
    "S0060": ("assessed", (10862, 11130), "", "proximity of the model to a T/CCL."),
    "S0259": ("assessed", (49489, 49588), "● Early Warning Evaluations: ", "dangerous capabilities of a model."),
    "S0260": ("assessed", (49589, 49882), "", "these thresholds have been reached."),
    "S0056": ("change_assessed", (9892, 10205), "", "completion of a post-training run."),
    "S0261": ("change_assessed", (49883, 49985), "Material Capability Change Assessments: ",
              "capability assessment is required."),
    "S0262": ("change_assessed", (49986, 50299), "", "to a critical capability assessment."),
    "S0044": ("proximity_assessed", (7521, 7701), "", "and external experts as needed."),
    "S0078": ("secured", (14548, 14844), "", "critical capabilities in deployments."),
    "S0105": ("secured", (21699, 22028), "2.1 Mitigation Approach ", "capabilities in external deployments."),
    "S0276": ("secured", (52382, 52525), "", "parameters, among other measures."),
    "S0103": ("holistic", (21159, 21347), "", "balancing safety with innovation."),
    "S0149": ("recommends", (29853, 30038), "", "to models reaching each CCL."),
    "S0201": ("periodic_covers_internal", (40151, 40325), "", "internal deployments for such models."),
    "S0271": ("external", (51632, 51742), "", "releases to the broader public."),
    "S0281": ("residual_assessed", (53214, 53332), "", "and the effect of mitigations."),
    "S0284": ("safety_case", (53579, 53726), "", "model's risk acceptance determination."),
    "S0020": ("yearly_review", (2630, 2788), "", "of frontier models improves."),
}


# The quoted passages: one unit, or consecutive sentences of one Glossary entry quoted together.
PASSAGES = [(unit,) for unit in sorted(CARRIES) if unit not in {"S0259", "S0260", "S0261", "S0262"}] + [
    ("S0259", "S0260"), ("S0261", "S0262")]


def _environment() -> dict:
    return json.loads((CASE / "environment.d1.json").read_text(encoding="utf-8"))


def _legend(predicate: str) -> str:
    return _environment()["vocabulary"]["predicates"][predicate]["description"]


def quoted_passages(legend: str) -> list[tuple[int, str]]:
    """(offset of the opening quote, text) of each quoted passage of a legend: the runs between its straight quotes."""
    passages, offset = [], 0
    for k, part in enumerate(legend.split('"')):
        if k % 2:
            passages.append((offset - 1, part))
        offset += len(part) + 1
    return passages


def holds_whole(passage: str, words: str, *, at_start: bool = True) -> bool:
    """`words` stand in the normalised passage, ending at its end or before a space, and (at_start) starting at its
    start or after a space: whole sentences, never a piece of a longer word."""
    start = r"(?:^|(?<= ))" if at_start else ""
    return re.search(start + re.escape(words) + r"(?:$|(?= ))", A.norm(passage)) is not None


def source_sentence(text: bytes, unit: str) -> str:
    """The unit's sentence from the pinned text: its byte span, normalised, its heading or label cut (it must stand
    there), the running head inside the span cut."""
    _, (start, end), cut, _ = CARRIES[unit]
    sentence = A.norm(text[start:end].decode("utf-8")).strip().replace(RUNNING_HEAD, "")
    assert sentence.startswith(cut), (unit, sentence)
    return sentence[len(cut):]


@pytest.mark.parametrize("passage", PASSAGES, ids="+".join)
def test_the_legend_quotes_the_pinned_source_sentence(passage):
    """The condition test: the source sentences, read from the pinned text, stand in quotes in the committed legend
    of a predicate a block uses (fails at d5f402140f, where these legends lacked them)."""
    text = pinned_source("safety-framework").read_bytes()
    sentences = []
    for unit in passage:
        sentence = source_sentence(text, unit)
        assert sentence.endswith(CARRIES[unit][3]), (unit, sentence)
        sentences.append(sentence)
    predicate = CARRIES[passage[0]][0]
    assert {CARRIES[unit][0] for unit in passage} == {predicate}
    assert any(holds_whole(quoted, " ".join(sentences)) for _, quoted in quoted_passages(_legend(predicate))), (
        passage, predicate)


def test_every_kept_unit_is_in_one_passage():
    assert sorted(unit for passage in PASSAGES for unit in passage) == sorted(CARRIES)


@pytest.mark.parametrize("passage", PASSAGES, ids="+".join)
def test_the_carrier_is_a_legend_a_reader_is_shown(passage):
    """Needs no source. The predicate is used by a rule or fact block, is no open term, the sentence's quote (found
    by its last words) is outside any parenthesised citation, and the counter's raw read of the vocabulary.py entry
    holds those words, so no variable hides them."""
    unit = passage[-1]
    predicate, _, _, last = CARRIES[unit]
    environment = _environment()
    blocks = {**O.rule_blocks((CASE / "rules.d1.ve").read_text(encoding="utf-8")),
              **O.rule_blocks((CASE / "facts.d1.ve").read_text(encoding="utf-8"))}
    used = {p for _, body in blocks.values() for p in O.used_predicates(body, environment)}
    assert predicate in used, predicate
    vocabulary = _module("fsf_vocabulary_srccov", CASE / "vocabulary.py")
    assert predicate not in vocabulary.OPEN_PREDICATES, predicate
    legend = _legend(predicate)
    assert "Open term" not in legend
    opening = [start for start, quoted in quoted_passages(legend) if holds_whole(quoted, last, at_start=False)]
    assert opening, (unit, last)
    end = opening[0]
    assert legend[:end].count("(") - legend[:end].count(")") == 0, (unit, "inside a parenthesised citation")
    raw = "\n".join(O.strip_comments(O.legend_raw(predicate, (CASE / "vocabulary.py").read_text().splitlines())))
    assert set(O.content_words(last)) <= set(re.findall(r"[a-z0-9_]+", O.omit_norm(raw))), (unit, predicate)


def test_a_passage_carries_only_whole_sentences_inside_one_quote():
    """The merged reading can fail: a sentence split across two quotes, cut short, or run into a longer word is not
    carried; one alone or inside a longer quote, with curly inner quotes, is."""
    sentence = 'We call it "Tracked." It holds.'
    for legend in ('a "We call it “Tracked.” It holds."', 'a "2 We call it “Tracked.” It holds. More." b'):
        assert any(holds_whole(q, sentence) for _, q in quoted_passages(legend)), legend
    for legend in ('a "We call it “Tracked.”" b "It holds."', 'a "We call it “Tracked.” It hold"',
                   'a "XWe call it “Tracked.” It holds."', 'a We call it “Tracked.” It holds. "b"'):
        assert not any(holds_whole(q, sentence) for _, q in quoted_passages(legend)), legend
    assert quoted_passages('a "b" c "d"') == [(2, "b"), (8, "d")]


def test_the_cut_strings_are_headings_labels_and_the_running_head_only():
    """The reader of the source cuts nothing else: every cut is a section heading, a Glossary label, a footnote mark
    or a list bullet, and the running head is the page-18 one."""
    assert {cut for _, _, cut, _ in CARRIES.values()} == {
        "", "2 ", "8 ", "3.2.2 ML R&D Critical Capability Levels ", "Thresholds Critical Capability Levels (CCLs): ",
        "● Early Warning Evaluations: ", "Material Capability Change Assessments: ", "2.1 Mitigation Approach "}
    assert RUNNING_HEAD.startswith("Frontier Safety Framework | 18 ")
