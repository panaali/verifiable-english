"""fsf-repair-f6-sl2plus-1119 (row F6): the `recommends` legend carries the source's Security Level 2+, 3 and 4 text.

The FSF's own words for the recommended security levels are 2.1.1's Security Level 2+ sentence (source line 9) and,
on table 3.2.2.a (source line 15), the Security level 3 and 4 recommendations with their footnote marks 12 and 13 and
the two footnotes. Each sits, quoted byte for byte, in the legend of `recommends`: a predicate the FACTS unit uses
(every level's "recommends" fact). No passage sits inside a parenthesis that the audit counter cuts as a citation
(one holding a digit or "section", "appendix", "table"), so each passage is counted text of a carrier for every answer
that reads FACTS; only the source's own "(SL2)" inside the S:9 sentence is cut, as it is everywhere the counter reads
it. The sentences are read from the pinned source here, never from this file.
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


# The audit counter's citation cut (uc-audit `_omit_legend_segments`, legend-carrier ruling s1). The counter reads a
# legend with these spans removed, so a quoted run inside one is classed a citation, never a carrier. The counter lives
# outside this repository; these patterns mirror its rule so a legend here can be checked without it.
CITATION_PARENTHESIS = re.compile(r"\([^()]*(?:\d|section|appendix|table)[^()]*\)", re.I)
LEADING_CITATION = re.compile(r"^\s*[A-Z]?\d+(?:\.\d+)*[a-z]?\s*:")
AT_CITATION = re.compile(r"\b[A-Z]?\d+(?:\.\d+)*[a-z]?\s+at\s+\{\d\}")
PROVENANCE = re.compile(r"\s*(?:[A-Z]?\d+(?:\.\d+)*[a-z]?\s*(?::|at\s+\{\d\})|\(?section\b)", re.I)

# The legends that already held a quoted run inside a citation parenthesis on main f5553bc894 (review note C4: their
# own items; not this one's), with how many such parentheses each holds. The guard lets no legend gain one.
CITED_QUOTES_ON_MAIN = {
    ("anthropic-rsp", "crossed"): 1,
    ("anthropic-rsp", "determined_by_publication"): 1,
    ("anthropic-rsp", "off_cycle_public_deployment"): 1,
    ("anthropic-rsp", "off_cycle_internal_deployment"): 1,
    ("anthropic-rsp", "ai_evidence_risk"): 1,
    ("anthropic-rsp", "external_review_process"): 1,
    ("anthropic-rsp", "revised_because_unable"): 1,
    ("anthropic-rsp", "lead_delay_needed"): 1,
    ("anthropic-rsp", "posture_delay_needed"): 1,
    ("anthropic-rsp", "lead_no_longer_believed"): 1,
    ("anthropic-rsp", "posture_attainable"): 1,
    ("anthropic-rsp", "advance_recommendations"): 1,
    ("anthropic-rsp", "goals_kept"): 1,
    ("anthropic-rsp", "candid_reports"): 1,
    ("anthropic-rsp", "governance_notified"): 1,
    ("anthropic-rsp", "ltbt_briefed"): 1,
    ("anthropic-rsp", "investigated"): 1,
    ("anthropic-rsp", "board_notified"): 1,
    ("anthropic-rsp", "internal_review"): 1,
    ("safety-framework", "reached"): 1,
    ("safety-framework", "approaches"): 1,
    ("safety-framework", "at_least_as_strong"): 1,
    ("safety-framework", "mitigates"): 1,
    ("safety-framework", "unmitigated_public_safety_risk"): 1,
    ("safety-framework", "adherence_undermined"): 1,
    ("safety-framework", "proximity_assessed"): 1,
    ("safety-framework", "residual_assessed"): 1,
    ("safety-framework", "holistic"): 1,
    ("safety-framework", "within_levels"): 1,
}


def _counted(legend):
    """A legend as the counter counts it: its citations cut out; a provenance string (a leading section citation that
    copies a quoted sentence) counts as nothing."""
    if PROVENANCE.match(legend) and re.search(r'"[^"]*(?:\s+\S+){2,}[^"]*"', legend):
        return ""
    return LEADING_CITATION.sub(" ", _cut_inside(legend))


def _cut_inside(text):
    """The cuts that apply anywhere in a string: citation parentheses and "<n> at {k}"."""
    return AT_CITATION.sub(" ", CITATION_PARENTHESIS.sub(" ", text))


def _source_sentences():
    """Each SOURCE_PATTERNS passage, found exactly once in the normalised pinned source."""
    text = _quote_normal(pinned_source("safety-framework").read_text())
    sentences = {}
    for name, pattern in SOURCE_PATTERNS.items():
        found = re.findall(pattern, text)
        assert len(found) == 1, (name, found)
        sentences[name] = found[0]
    return sentences


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
    sentences = _source_sentences()
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


def test_every_passage_is_counted_text_of_the_recommends_legend():
    """Review F1: each passage survives the counter's citation cut. The cut legend holds the passage cut the same way
    (only the source's own "(SL2)" goes, review note C1), so no citation parenthesis reaches into a passage. The
    passages once sat inside "(table 3.2.2.a, ...; footnote 12: ...)", which the counter cut whole."""
    sentences = _source_sentences()
    for entry in _legends():
        counted = _quote_normal(_counted(entry["description"]))
        assert [name for name, sentence in sentences.items()
                if _quote_normal(_cut_inside(sentence)) not in counted] == []
        assert [m.group(0) for m in CITATION_PARENTHESIS.finditer(entry["description"]) if '"' in m.group(0)] == []


def _cited_quotes(environment):
    """{predicate: how many citation parentheses of its legend strings hold a quote mark} for one environment."""
    out = {}
    for key, entry in environment["vocabulary"]["predicates"].items():
        n = sum(1 for value in entry.values() if isinstance(value, str)
                for m in CITATION_PARENTHESIS.finditer(value) if '"' in m.group(0))
        if n:
            out[key] = n
    return out


def test_no_legend_gains_a_quote_inside_a_citation_parenthesis():
    """The class guard of review F1, over every audited use case (each environment.d1.json with legends): no legend
    holds more quoted runs inside a citation parenthesis than it did on main (CITED_QUOTES_ON_MAIN). A quote added
    inside "(table ...)" or "(3.2: ...)" is read by the counter as a citation and never counted as a carrier."""
    paths = sorted((REPO / "usecases").glob("*/environment.d1.json"))
    assert {p.parent.name for p in paths} >= {"anthropic-rsp", "safety-framework", "openai-preparedness"}
    gained = {}
    for path in paths:
        for key, n in _cited_quotes(json.loads(path.read_text())).items():
            if n > CITED_QUOTES_ON_MAIN.get((path.parent.name, key), 0):
                gained[(path.parent.name, key)] = n
    assert gained == {}


def test_the_guard_finds_a_quote_inside_a_citation_parenthesis():
    """The guard and the cut can fail: the legend's shape before F1 was fixed (two quotes inside one citation
    parenthesis) is found, and its counted text loses the Security level 3 cell; without the parentheses it keeps it."""
    before = ('the framework recommends {1} (tables 2.2.1.a to 3.2.2.a). Security level 3 (table 3.2.2.a, ML R&D '
              'acceleration level 1: "Security level 3 12"; footnote 12: "12 This level may include mitigations.").')
    assert _cited_quotes({"vocabulary": {"predicates": {"recommends": {"description": before}}}}) == {"recommends": 1}
    assert "Security level 3 12" not in _counted(before)
    assert "Security level 3 12" in _counted(before.replace("level 3 (table", "level 3, table").replace(".\").", '."'))
