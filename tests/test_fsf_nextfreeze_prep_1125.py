"""fsf-nextfreeze-prep-1125 (rows relc-qr-record-midsentence, relc-qr-footnote5-section): three record-header quotes of
the Framework end at a sentence end of the pinned source.

The headers of facts activities-internal-external, activities-high-risk (facts.d1.ve) and rule f10-dm-diff
(rules.d1.ve) quoted Glossary entries and footnote 5 up to a point inside a sentence. Each now quotes whole sentences
(DRI decision manage-agents reviews/dri-decisions-20261125-fsf-disposition.md item 5, text of
reviews/fsf-disposition-proposal-20261125.md section 2). Two of them stay cut at a sentence boundary by design (the
External Deployments entry and footnote 5 go on with a sentence about something else). Only the third header field
changes: rule and fact bodies are untouched, and no answer reads the quote's ending (translation.py:131, run.py:319-329).
"""
import re
from pathlib import Path

from tests.pinned_source import pinned_source

HERE = Path(__file__).resolve().parents[1] / "usecases" / "safety-framework"
# block id -> (file, the header's quotes that must end at a sentence end, quote-normalised copies of the pinned text,
# fsf-3.1.txt line 19 (Glossary) and line 7 (footnote 5)); the copies keep the check running where the source is absent.
HEADERS = {
    "activities-internal-external": ("facts.d1.ve", (
        "External Deployments: represent model releases to entities outside of Google.",
        "Internal Deployments: represent model releases restricted to Google employees for internal use.")),
    "activities-high-risk": ("facts.d1.ve", (
        "High-Risk Internal Deployments: represent model releases restricted to Google employees for use cases with "
        "the potential to enable severe threat scenarios (e.g. building internal security infrastructure or "
        "automating ML R&D).",)),
    "f10-dm-diff": ("rules.d1.ve", (
        "Note that deployment mitigations for the ML R&D CCLs are different than those for the misuse CCLs because of "
        "differences in which deployment could lead to severe harm for those respective categories.",)),
}
# What each quote must be followed by in the source: a space and the next sentence of the same entry, or the next entry.
NEXT = {
    "External Deployments: represent model releases to entities outside of Google.": " They can include ",
    "Note that deployment mitigations for the ML R&D CCLs are different than those for the misuse CCLs because of "
    "differences in which deployment could lead to severe harm for those respective categories.": " In contrast, ",
}


def _quote_normal(text):
    """The quote normalisation of the pinned-source tests: whitespace runs collapse to one space, curly quotes become
    straight ones."""
    return " ".join(text.split()).translate(str.maketrans("‘’“”", "''\"\""))


def _header(block_id):
    name, _ = HEADERS[block_id]
    [line] = [x for x in (HERE / name).read_text(encoding="utf-8").split("\n") if x.startswith(f"## {block_id} |")]
    return line


def test_the_three_record_headers_quote_whole_sentences():
    """Each listed quote stands in its block's header in straight quotes and ends with the sentence's full stop."""
    for block_id, (_name, quotes) in HEADERS.items():
        header = _header(block_id)
        found = re.findall(r'"([^"]*)"', header.split(" | ", 2)[2])
        for quote in quotes:
            assert quote in found, (block_id, quote)
            assert quote.endswith("."), (block_id, quote)


def test_the_quotes_end_at_a_sentence_end_of_the_pinned_source():
    """Against the pinned fsf-3.1.txt (when stored): each quote occurs exactly once, the copy above is the source's
    text, and what follows it is a space and a new sentence, or the next bullet entry; the footnote 5 quote starts at
    the footnote's first word."""
    path = pinned_source("safety-framework", skip=False)
    if path is None:
        return
    text = _quote_normal(path.read_text(encoding="utf-8"))
    for _block_id, (_name, quotes) in HEADERS.items():
        for quote in quotes:
            assert text.count(quote) == 1, quote
            at = text.index(quote) + len(quote)
            follow = text[at:at + 40]
            assert re.match(r" (\d{1,2} |● )?[A-Z(]", follow), (quote, follow)
            if quote in NEXT:
                assert follow.startswith(NEXT[quote]), (quote, follow)
    assert text.count("5 Note that deployment mitigations for the ML R&D CCLs") == 1
