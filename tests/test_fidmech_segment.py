"""tools/fidmech/segment.py: furniture, footnote pairs, the two streams, sentence ends and boundaries.json validation.

Every test but the last runs on the fixture tests/data/fidmech/doc (three pages, one per line, RSP-shaped: an inline
footer, a repeated table header holding footnote 3's marker, footnotes 4 and 8 with their bodies later on the page in
the order 8, 4). The last test is the one real-source test (plan point 9).
"""
import ast
import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from tools.fidmech import segment as S
from tools.fidmech.__main__ import main

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "tests/data/fidmech/doc"
TEXT = DOC / "source.txt"


def fixture():
    return S.Source(TEXT.read_bytes()), S.load_boundaries(DOC / "fidmech/boundaries.json")


def segmented(b=None):
    source, frozen = fixture()
    return S.Segmentation(source, b or frozen)


def sentence_texts(seg, stream=0):
    return [s.text for s in seg.streams[stream].sentences]


def at(source, text, k=0):
    """The byte offset of the k-th occurrence of text in the fixture source."""
    i = -1
    for _ in range(k + 1):
        i = source.text.index(text, i + 1)
    return source.byte[i]


# --- furniture ---------------------------------------------------------------------------------------------------

def test_the_inline_footer_and_the_repeated_header_are_cut_from_the_main_stream():
    main_text = segmented().streams[0].canon.text
    assert "Example Policy, Page" not in main_text and "Capability or usage threshold" not in main_text
    source, b = fixture()
    pages = [page for _, page, _, _ in S.furniture_matches(source, b.furniture)]
    assert pages == [1, 2, 1, 2]  # the footer on pages 2 and 3, the header on pages 2 and 3 (0-based)
    off = S.Segmentation(source, b.without("furniture")).streams[0].canon.text
    assert "Example Policy, Page 2" in off and "Capability or usage threshold" in off


def test_the_furniture_command_lists_every_match_with_its_page_and_offset(capsys):
    assert main(["furniture", "--doc", str(DOC), "--source", str(TEXT)]) == 0
    rows = capsys.readouterr().out.splitlines()
    source, _ = fixture()
    assert len(rows) == 4
    for row in rows:
        k, page, byte, text = row.split("\t")
        start = int(byte.removeprefix("byte "))
        assert source.data[start:].decode().startswith(ast.literal_eval(text))  # the match is at its offset


@pytest.mark.parametrize("pattern, where", [
    ("Example Policy, Page \\d+", "page-end"),  # no $
    ("Example Policy, Page \\d+\\$", "page-end"),  # an escaped $ anchors nothing
    ("Capability or usage threshold", "page-start"),  # no ^
    ("^Capability or usage threshold", "page-end"),  # anchored to the other end
    ("^Capability or usage threshold", "inline"),
    ("^Nowhere in the text", "page-start"),  # matches no page
    ("^(?=Capability)", "page-start"),  # an empty match
])
def test_a_furniture_pattern_not_anchored_to_its_page_position_is_refused(pattern, where):
    source, b = fixture()
    bad = replace(b, furniture=({"pattern": pattern, "where": where, "reason": "test"},))
    with pytest.raises(S.BoundariesError):
        S.Segmentation(source, bad)


def test_an_anchored_page_end_pattern_is_accepted_as_the_counterpart():
    source, b = fixture()
    good = replace(b, furniture=({"pattern": "Page \\d+$", "where": "page-end", "reason": "test"},))
    assert [p for _, p, _, _ in S.furniture_matches(source, good.furniture)] == [1, 2]


# --- footnote pairs ----------------------------------------------------------------------------------------------

def test_the_generator_pairs_bodies_that_come_later_on_the_page_in_the_order_8_4():
    source, b = fixture()
    pairs, unresolved = S.propose(source, b.furniture, [f["body"][0] for f in b.footnotes if f["by"] == "hand"])
    assert [(p["n"], p["marker_at"]) for p in pairs] == [(8, at(source, "8 in AI")), (4, at(source, "4 That is"))]
    assert pairs[0]["body"][0] < pairs[1]["body"][0]  # body 8 comes first on the page
    assert source.data[slice(*pairs[1]["body"])].decode() == "4 In particular, harm to many people."
    assert [u["n"] for u in unresolved] == [3]  # its marker is in the repeated header: a hand decision
    assert [f for f in b.footnotes if f["by"] == "generator"] == pairs


def test_paired_markers_are_removed_and_digits_without_a_body_are_kept():
    seg = segmented()
    text = seg.streams[0].canon.text
    assert "catastrophic harm. That is, harm at a large scale." in text
    assert "the rate of progress in AI research" in text
    assert "progress 8 in AI" in seg.streams[0].marked.text
    assert "permit 1 attempt per day and may permit 2 attempts per week" in text
    source = seg.source
    assert {at(source, "1 attempt"), at(source, "2 attempts")} <= set(seg.unpaired_runs)
    off = S.Segmentation(source, seg.boundaries.without("footnotes")).streams[0].canon.text
    assert "harm. 4 That is" in off and "8 Progress means research output." in off


def test_each_footnote_body_is_a_stream_of_its_own_and_left_out_of_the_main_stream():
    seg = segmented()
    bodies = {s.name.split("@")[0]: s.canon.text for s in seg.streams[1:]}
    assert bodies == {"fn8": "Progress means research output.", "fn4": "In particular, harm to many people.",
                      "fn3": "This column summarizes plans."}
    assert not any(t in seg.streams[0].canon.text for t in bodies.values())


def test_the_hand_footnote_lever_is_the_generators_raw_proposal():
    seg = segmented()
    off = S.Segmentation(seg.source, seg.boundaries.without("hand-footnotes", seg.source))
    assert [f["by"] for f in off.boundaries.footnotes] == ["generator", "generator"]
    assert {s.canon.text for s in off.streams[1:]} == {"Progress means research output.",
                                                      "In particular, harm to many people. 3 This column summarizes "
                                                      "plans."}


# --- sentences ---------------------------------------------------------------------------------------------------

def test_clause_numbers_inside_a_sentence_do_not_split_it_and_split_only_after_a_lead_in():
    texts = sentence_texts(segmented())
    assert "If a report is (1) substantiated and (2) involves a material risk, we will notify the Board." in texts
    assert "We will select reviewers that:" in texts
    assert "(1) know the field; and (2) have no conflict." in texts  # one item: "(2)" splits nothing


def test_each_list_item_records_its_lead_in():
    seg = segmented()
    sentences = seg.streams[0].sentences
    by_text = {s.text: s for s in sentences}
    lead = by_text["Each review covers the following items:"]
    assert lead.is_lead_in
    for item in ("● the model weights;", "● the training data."):
        assert by_text[item].item == "●" and sentences[by_text[item].lead_in] == lead
    assert sentences[by_text["(1) know the field; and (2) have no conflict."].lead_in].text == \
        "We will select reviewers that:"
    assert by_text["We will keep records of every review."].lead_in is None


def test_a_sentence_runs_on_across_a_page_join_and_furniture():
    assert "Our reports will be published once a review ends and will include a public summary." in \
        sentence_texts(segmented())


def test_abbreviations_end_no_sentence_and_the_document_abbreviation_is_a_lever():
    seg = segmented()
    texts = sentence_texts(seg)
    assert "The audit names two checks, e.g. Code review, and a data check." in texts
    assert "Each request uses form No. A1 for its record." in texts
    off = sentence_texts(S.Segmentation(seg.source, seg.boundaries.without("abbrev")))
    assert "Each request uses form No." in off and "A1 for its record." in off


def test_extra_and_suppress_entries_move_sentence_starts():
    source, b = fixture()
    extra = replace(b, extra=({"at": at(source, "records of every"), "reason": "test"},))
    assert "records of every review." in sentence_texts(S.Segmentation(source, extra))
    suppress = replace(b, suppress=({"at": at(source, "We will answer"), "reason": "test"},))
    assert ("We will keep records of every review. We will answer each request within 30 days of receipt."
            in sentence_texts(S.Segmentation(source, suppress)))


def test_sentence_offsets_are_raw_byte_offsets_into_the_source():
    seg = segmented()
    for s in seg.streams[0].sentences:
        assert S.norm(seg.source.data[s.start:s.end].decode()).startswith(s.text[:12])
    one = next(s for s in seg.streams[0].sentences if s.text.startswith("Staff may permit"))
    assert seg.source.data[one.start:one.end].decode() == one.text


def test_norm_folds_whitespace_quote_styles_dashes_and_ligatures_and_keeps_digits():
    assert S.norm("a b\tc\r\nd  e") == "a b c d e"
    assert S.norm("“the ‘ﬁrst’ one” – it’s") == S.norm('"the \'first\' one" - it\'s') == '"the "first" one" - it"s'
    assert S.norm("Section 1 . ( see it )") == "Section 1. (see it)"
    assert S.norm("within 30 days") != S.norm("within 3 days")
    assert S.masked("within 30 days") == S.masked("within 3 days") == "within # days"


# --- boundaries.json validation ----------------------------------------------------------------------------------

def _raw():
    return json.loads((DOC / "fidmech/boundaries.json").read_text(encoding="utf-8"))


def _mutate(data, key, k, field, value):
    data[key][k][field] = value
    return data


@pytest.mark.parametrize("change", [
    lambda d: _mutate(d, "footnotes", 0, "reason", ""),  # no reason
    lambda d: _mutate(d, "furniture", 0, "reason", "  "),
    lambda d: _mutate(d, "footnotes", 0, "marker_at", 10 ** 6),  # outside the source
    lambda d: _mutate(d, "footnotes", 0, "body", [d["footnotes"][0]["body"][0], 10 ** 6]),
    lambda d: _mutate(d, "footnotes", 0, "marker_at", d["footnotes"][0]["marker_at"] + 1),  # not the digit run
    lambda d: _mutate(d, "footnotes", 0, "n", 9),  # marker digits differ from n
    lambda d: _mutate(d, "footnotes", 0, "body", [d["footnotes"][0]["body"][0] + 1, d["footnotes"][0]["body"][1]]),
    lambda d: _mutate(d, "footnotes", 1, "marker_at", d["footnotes"][0]["marker_at"]),  # a marker with two bodies
    lambda d: _mutate(d, "footnotes", 1, "body", d["footnotes"][0]["body"]),  # a body with two markers
    lambda d: _mutate(d, "footnotes", 0, "by", "guess"),
    lambda d: _mutate(d, "footnotes", 0, "marker_at", True),  # bool for int
    lambda d: _mutate(d, "furniture", 0, "pattern", "("),
    lambda d: _mutate(d, "abbrev", 0, "text", "two words."),
    lambda d: {**d, "unknown": []},
    lambda d: {**d, "source_sha256": "0" * 64},
    lambda d: {**d, "schema": "fidmech-boundaries/0"},
    lambda d: {**d, "extra": [{"at": 5, "reason": "test", "by": "x"}]},
    lambda d: {**d, "extra": [{"at": -1, "reason": "test"}]},
    lambda d: {**d, "extra": [{"at": 70, "reason": "inside the repeated header, which is cut"}]},
    lambda d: {**d, "suppress": [{"at": 0, "reason": "matches no boundary"}]},
    lambda d: {**d, "unpaired": [{"at": d["footnotes"][0]["marker_at"], "n": 8, "reason": "a frozen marker"}]},
])
def test_a_boundaries_entry_without_a_reason_or_outside_its_source_is_refused(change):
    source, _ = fixture()
    assert S.Segmentation(source, S.parse_boundaries(_raw()))  # the frozen file is accepted
    with pytest.raises(S.BoundariesError):
        S.Segmentation(source, S.parse_boundaries(change(_raw())))


def test_a_body_before_its_marker_or_two_pages_later_is_refused():
    source, b = fixture()
    four = next(f for f in b.footnotes if f["n"] == 4)
    early = {**four, "marker_at": at(source, "4 In particular"), "body": [at(source, "4 That is"),
                                                                         at(source, "4 That is") + 9]}
    with pytest.raises(S.BoundariesError):
        S.Segmentation(source, replace(b, footnotes=tuple(f for f in b.footnotes if f["n"] != 4) + (early,)))


def test_the_boundaries_check_fails_on_a_stale_pair_or_an_undecided_candidate(tmp_path, capsys):
    args = ["boundaries", "--doc", str(tmp_path), "--source", str(TEXT), "--check"]
    (tmp_path / "fidmech").mkdir()
    target = tmp_path / "fidmech/boundaries.json"
    target.write_text(json.dumps(_raw()), encoding="utf-8")
    assert main(args) == 0
    stale = _raw()
    stale["footnotes"][0]["reason"] = "edited"
    target.write_text(json.dumps(stale), encoding="utf-8")
    assert main(args) == 1
    undecided = _raw()
    undecided["footnotes"] = [f for f in undecided["footnotes"] if f["by"] == "generator"]
    target.write_text(json.dumps(undecided), encoding="utf-8")
    assert main(args) == 1
    rejected = _raw()  # a proposal rejected with a reason is decided
    rejected["unpaired"] = [{"at": rejected["footnotes"][0]["body"][0], "n": 8, "reason": "test"}]
    rejected["footnotes"] = rejected["footnotes"][1:]
    target.write_text(json.dumps(rejected), encoding="utf-8")
    assert main(args) == 0
    capsys.readouterr()


# --- the real sources (plan point 9) -----------------------------------------------------------------------------

@pytest.mark.parametrize("doc", ["anthropic-rsp", "safety-framework", "openai-preparedness"])
def test_the_frozen_boundaries_fit_the_pinned_source(doc, capsys):
    """Opens each case's build_document.DEFAULT_SOURCE (read from its assignment), so the merge train's quote step
    enforces it; it skips only where the pinned source is not stored (tools/gate-optional.json). The file's sha,
    every entry, the footnote pairs and the hand decisions are checked; the frozen generator pairs are the
    generator's proposal and no candidate is undecided."""
    case = ROOT / "usecases" / doc
    path = S.doc_source(case)
    if not path.exists():
        pytest.skip("the pinned source is not stored on this machine")
    data = path.read_bytes()
    b = S.load_boundaries(case / "fidmech/boundaries.json")
    assert hashlib.sha256(data).hexdigest() == b.source_sha256
    seg = S.Segmentation(S.Source(data), b)
    assert len(seg.streams[0].sentences) > 100
    assert main(["boundaries", "--doc", doc, "--check"]) == 0
    capsys.readouterr()
