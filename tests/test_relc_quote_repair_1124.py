"""relc-quote-repair-1124: five FSF legend quotes end where their source entry ends.

A mechanical check of every stored quote of the Framework against the source entry it quotes (manage-agents
reviews/pathf-q3/relc-quote-repair-1124/check_quotes.py and SCOPE.md) found five legend quotes that stop at a sentence
end inside their entry: the Glossary entry "Safety Cases" without its last sentence ("For ML R&D and misalignment risk,
...") in material_safety_case_update, governance_found_acceptable_with_safety_case_where_ccl_reached and safety_case;
footnote 6 without its last sentence ("As the authors point out, ...") in recommends; and the Glossary entry Residual
Risk Assessments without its last two sentences in within_levels. Each quote is completed, verbatim, to its entry's
end. The condition test: each completed quote stands unbroken in the legend a reader is shown (environment.d1.json and
vocabulary.py's output) and in the text the definitions counter counts, and the legend's quote closes right after it
(fails on main at 80d609609d for all five). With the pinned FSF text stored at its pin, each completed quote also
occurs once in it and is followed by its entry's end; the test never downloads and never skips.
"""
from __future__ import annotations

import pytest

from omission_rule import omit_norm
from tests.pinned_source import pinned_source
from tests.test_defs_repair_safety_framework_1119 import GOV, _as_counted, _committed, _counted, _shown

ML_RD_SENTENCE = (
    "For ML R&D and misalignment risk, such an argument may be based, for example, on considerations such as the "
    "effectiveness of mitigations relative to model capabilities, and information pertaining to model propensities "
    "and the severity of related events.")
FOOTNOTE_6_LAST = (
    "As the authors point out, the “security level benchmarks represent neither a complete standard nor a compliance "
    "regime—they are provided for informational purposes only and should inform security teams’ decisions rather "
    "than supersede them.”")
# The whole entries, in the source's bytes, written out here (not shared with the defs repair's constants, so the test
# fails on a tree whose stored quotes are the cut ones).
SAFETY_CASES_REST = (
    "Residual risk assessments will be supplemented with a safety case when a model reaches a CCL, and inform a "
    "model’s risk acceptance determination. 15 For misuse risk, such an argument may be based, for example, on "
    "considerations such as the effectiveness of mitigations, the scope of the deployment, what capabilities and "
    "mitigations are available on other publicly available models, and the historical incidence and severity of "
    "related events. " + ML_RD_SENTENCE)
SAFETY_CASES = (
    "Safety Cases: are an assessable argument showing how severe risks associated with a model's CCLs have been "
    "reduced to an acceptable level. " + SAFETY_CASES_REST)
FOOTNOTE_6 = (
    "6 In other words, “security level N ” indicates security controls and detections at a level generally aligned "
    "with RAND SL N . See https://www.rand.org/pubs/research_reports/RRA2849-1.html , pp 21-22. In aligning our "
    "security levels with RAND’s, we are referring to the security goals and principles in the RAND framework, "
    "rather than the benchmarks (i.e. concrete measures) also described in the RAND report. " + FOOTNOTE_6_LAST)
RRA_LAST_TWO = (
    "This is part of the risk management process, following a critical capability assessment and the effect of "
    "mitigations. The residual risk should be brought within the acceptable levels, as determined by the T/CCLs as "
    "relevant.")
RRA_WITHOUT_HEADING = (
    "the process of evaluating the level of risk that remains after all planned mitigation strategies have been "
    "implemented. " + RRA_LAST_TWO)

# legend -> (the completed quote, the last sentence it had lacked, what the source prints right after the entry ends)
CASES = {
    "material_safety_case_update": (SAFETY_CASES, ML_RD_SENTENCE, " 15 See also, for reference"),
    GOV: (SAFETY_CASES, ML_RD_SENTENCE, " 15 See also, for reference"),
    "safety_case": (SAFETY_CASES_REST, ML_RD_SENTENCE, " 15 See also, for reference"),
    "recommends": (FOOTNOTE_6, FOOTNOTE_6_LAST, " Frontier Safety Framework | 9"),
    "within_levels": (RRA_WITHOUT_HEADING, RRA_LAST_TWO, " Safety Cases: are"),
}


def test_the_completed_quotes_end_with_the_missing_sentences():
    """The constants are the completed quotes, and the defs repair's audit-row constants agree with them."""
    from tests import test_defs_repair_safety_framework_1119 as defs
    assert (defs.SAFETY_CASES, defs.SAFETY_CASES_REST, defs.FOOTNOTE_6) == (SAFETY_CASES, SAFETY_CASES_REST, FOOTNOTE_6)
    for key, (quote, last, _after) in CASES.items():
        assert quote.endswith(last), key


@pytest.mark.parametrize("key", sorted(CASES))
def test_each_completed_quote_is_carried_whole_and_closes_there(key):
    """The condition test: the completed quote stands unbroken, shown and counted, and the legend's quotation closes
    right after it (so the quote ends where its entry ends, not one sentence short)."""
    quote, _last, _after = CASES[key]
    assert all(omit_norm(quote) in omit_norm(legend) for legend in _shown(key)), key
    assert _as_counted(quote) in _counted(key), key
    description = _committed()["vocabulary"]["predicates"][key]["description"]
    assert description.count(quote + '"') == 1, key


@pytest.mark.parametrize("key", sorted(CASES))
def test_each_completed_quote_ends_where_its_entry_ends_in_the_pinned_source(key):
    """With the pinned FSF text stored at its pin: the completed quote occurs once and the source goes on with the
    entry's end (the footnote text, the page footer or the next Glossary entry). Absent and not required, nothing is
    checked here (the condition test above needs no source)."""
    quote, _last, after = CASES[key]
    path = pinned_source("safety-framework", skip=False)
    if path is None:
        return
    text = path.read_text(encoding="utf-8")
    assert text.count(quote) == 1, key
    end = text.index(quote) + len(quote)
    assert text[end:end + len(after)] == after, (key, text[end:end + 40])
