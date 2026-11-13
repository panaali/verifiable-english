"""tools/fidmech/textchecks.py: L1 m/n/u/c/e on header quotes, one hit per quote by the precedence m > n > u > c > e.

The fixture tests/data/fidmech/doc holds a clean block for every shape (no hit) and the plants of the plan's section
10 table: L1m (no quote; `""`; only a translator's note), L1n ("within 3 days" for "within 30 days"; "permit 2" for
"permit 1"), L1u (one word changed), L1c (cut mid-sentence without an ellipsis; quoted up to a page join; a bullet
without its lead-in; a quote starting at the clause number "(2)" inside a sentence), L1e (an ellipsis).
"""
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from tools.fidmech import segment as S
from tools.fidmech import textchecks as T
from tools.fidmech.__main__ import main

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "tests/data/fidmech/doc"
TEXT = DOC / "source.txt"
PLANTS = {"m-none": "L1m", "m-empty": "L1m", "m-note-only": "L1m", "n-days": "L1n", "n-permit": "L1n",
          "u-word": "L1u", "c-cut": "L1c", "c-join": "L1c", "c-bullet": "L1c", "c-clause-two": "L1c",
          "c-abbrev": "L1c", "e-ellipsis": "L1e"}


def segmented(b=None):
    source = S.Source(TEXT.read_bytes())
    return S.Segmentation(source, b or S.load_boundaries(DOC / "fidmech/boundaries.json"))


def blocks():
    return T.read_blocks(DOC)


def block(source_field, id_="probe"):
    return {"id": id_, "file": "rules.d1.ve", "sets": (), "source": source_field, "text": "Rule 1. A probe."}


def classes(seg, source_field):
    hits, _ = T.check_block(seg, block(source_field))
    return [h.cls for h in hits]


def test_the_fixture_has_a_clean_block_and_a_plant_per_class():
    ids = [b["id"] for b in blocks()]
    assert set(PLANTS) <= set(ids)
    assert {T.CLASSES.index(c) for c in PLANTS.values()} == set(range(len(T.CLASSES)))
    assert sum(i.startswith("clean-") for i in ids) >= 10


@pytest.mark.parametrize("b", [b for b in T.read_blocks(DOC) if b["id"].startswith("clean-")], ids=lambda b: b["id"])
def test_a_clean_block_has_no_hit(b):
    hits, info = T.check_block(segmented(), b)
    assert hits == [] and info["checked"] >= 1


@pytest.mark.parametrize("id_, cls", PLANTS.items())
def test_each_plant_gives_exactly_its_class_once(id_, cls):
    b = next(b for b in blocks() if b["id"] == id_)
    hits, _ = T.check_block(segmented(), b)
    assert [h.cls for h in hits] == [cls]


def test_the_whole_fixture_report_counts_each_plant_once():
    hits, info = T.l1(segmented(), blocks())
    assert sorted((h.block, h.cls) for h in hits) == sorted(PLANTS.items())
    assert info == {"note": 2, "empty": 1, "checked": 26}  # 27 blocks: 3 are L1m, 2 quote twice


def test_l1m_covers_no_quote_empty_and_punctuation_quotes_and_note_only_headers():
    seg = segmented()
    for field in ("F1", 'F1 ""', 'F1 "  "', 'F1 "…"', 'F1 "--"', 'F1 ("every" is OT1)', 'F1 [the "only" note]',
                  'F1 "unclosed quote'):
        assert classes(seg, field) == ["L1m"], field
    assert classes(seg, 'F1 "We will keep records of every review." ""') == []  # an empty one beside a real one


def test_a_translators_note_quote_is_counted_as_info_and_not_checked():
    seg = segmented()
    hits, info = T.check_block(seg, block('F1 "We will keep records of every review." ("whatever" is OT1)'))
    assert hits == [] and info == {"note": 1, "empty": 0, "checked": 1}
    hits, info = T.check_block(seg, block('F1 "We will keep records of every review." "whatever" is OT1'))
    assert [h.cls for h in hits] == ["L1u"] and info["note"] == 0  # the same quote outside brackets is checked


def test_precedence_gives_one_hit_per_quote_the_first_that_applies():
    seg = segmented()
    assert classes(seg, 'F2 "We will answer each request within 3 days"') == ["L1n"]  # n over c
    assert classes(seg, 'F2 "We will answer each request within 3 … receipt."') == ["L1n"]  # n over e
    assert classes(seg, 'F1 "We will keep records of each"') == ["L1u"]  # u over c
    assert classes(seg, 'F1 "We will keep records … each review."') == ["L1u"]  # u over e
    assert classes(seg, 'F1 "We will keep … of every"') == ["L1c"]  # c over e: cut and elided
    assert classes(seg, 'F1 "We will keep … of every review"') == ["L1e"]  # only the final "." left out
    assert classes(seg, 'F1 "We will keep records" "of every review." "each review"') == ["L1c", "L1c", "L1u"]


def test_elided_fragments_must_lie_in_order_in_one_run_of_contiguous_sentences():
    seg = segmented()
    assert classes(seg, 'F1 "We will keep records … review. We will answer each request within 30 days of '
                        'receipt."') == ["L1e"]
    assert classes(seg, 'F1 "review. … We will keep records of every"') == ["L1u"]  # out of order
    assert classes(seg, 'F1 "We will keep records of every review. … That is, harm at a large scale."') == ["L1u"]


def test_digit_runs_are_compared_and_a_footnote_marker_inside_a_quote_is_no_hit():
    seg = segmented()
    assert classes(seg, 'F2 "We will answer each request within 30 days of receipt."') == []
    assert classes(seg, 'F2 "We will answer each request within 300 days of receipt."') == ["L1n"]
    assert classes(seg, 'F3 "We track the rate of progress 8 in AI research every quarter."') == []
    assert classes(seg, 'F3 "We track the rate of progress 9 in AI research every quarter."') == ["L1n"]
    assert classes(seg, 'F4 "Staff may permit 1 attempt per day and may permit 2 attempts per week."') == []


def test_a_quote_of_a_footnote_body_is_located_in_the_footnote_stream():
    hits, _ = T.check_block(segmented(), block('F3 "Progress means research output." "Progress means research"'))
    assert [(h.cls, h.at[0].split("@")[0]) for h in hits] == [("L1c", "fn8")]
    off = S.Segmentation(S.Source(TEXT.read_bytes()), segmented().boundaries.without("footnotes"))
    assert classes(off, 'F3 "Progress means research output."') == ["L1c"]  # in the main text it is no sentence


def test_a_bullet_needs_its_lead_in_among_the_same_blocks_quotes():
    seg = segmented()
    assert classes(seg, 'F6 "the training data."') == ["L1c"]
    assert classes(seg, 'F6 "Each review covers the following items:" and "the training data."') == []
    assert classes(seg, 'F6 "Each review covers the following items: ● the model weights;"') == []
    assert classes(seg, 'F8 "(1) know the field; and (2) have no conflict."') == ["L1c"]


def test_norm_makes_whitespace_and_quote_styles_in_a_quote_irrelevant():
    seg = segmented()
    for field in ('F1 "We will keep records of\tevery  review."', 'F1 “We will keep records of every review.”',
                  'F1 "We will keep records of every\r\nreview."', 'F1 "We will keep records of every review ."'):
        assert classes(seg, field) == [], field


def test_the_header_quote_scanner_pairs_marks_as_the_accounting_tool_does():
    quotes, problem = T.header_quotes('A "one" (“two” and "three") “four “nested” end” [x "five"]')
    assert [(q.text, q.note) for q in quotes] == [("one", False), ("two", True), ("three", True),
                                                  ("four “nested” end", False), ("five", True)]
    assert problem is None
    assert T.header_quotes('a ” b')[1] == "unpaired closing quote mark at character 2"
    assert T.header_quotes('a “b')[1] == "unclosed quote mark at character 2"


# --- levers and the report ---------------------------------------------------------------------------------------

def test_the_report_prints_each_lever_off_and_the_hits_it_clears_or_adds(tmp_path):
    result = T.report(DOC, TEXT.read_bytes(), DOC / "fidmech/boundaries.json")
    assert result["counts"] == {"L1m": 3, "L1n": 2, "L1u": 1, "L1c": 5, "L1e": 1}
    levers = result["levers"]
    assert set(levers) == set(S.LEVERS)
    assert levers["abbrev"]["added"] == [["L1c", "c-abbrev", "Each request uses form No."]]
    assert levers["hand-footnotes"]["cleared"] == [["L1c", "clean-hand-footnote", "This column summarizes plans."]]
    assert ["L1u", "clean-marker-removed", "The policy addresses catastrophic harm. That is, harm at a large "
            "scale."] in levers["footnotes"]["cleared"]
    assert ["L1u", "clean-across-join", "Our reports will be published once a review ends and will include a "
            "public summary."] in levers["furniture"]["cleared"]
    assert result["footnote_pairs"] == {"generator": 2, "hand": 1}
    assert result["unpaired_digit_runs"] == len(segmented().unpaired_runs) > 0
    assert result["also_gated"] == {}


def test_an_extra_boundary_lever_can_clear_a_cut_and_the_rerun_shows_it(tmp_path):
    case = tmp_path / "doc"
    shutil.copytree(DOC, case)
    data = json.loads((case / "fidmech/boundaries.json").read_text(encoding="utf-8"))
    source = S.Source(TEXT.read_bytes())
    data["extra"] = [{"at": source.byte[source.text.index("review. We will answer")], "reason": "test: a cut quote's end"}]
    (case / "fidmech/boundaries.json").write_text(json.dumps(data), encoding="utf-8")
    result = T.report(case, TEXT.read_bytes(), case / "fidmech/boundaries.json")
    assert ["L1c", "c-cut", "We will keep records of every"] in result["levers"]["extra"]["cleared"]
    assert result["counts"]["L1c"] == 4


def test_on_the_preparedness_case_the_classes_today_s_gate_enforces_are_marked(tmp_path):
    case = tmp_path / "openai-preparedness"
    shutil.copytree(DOC, case)
    result = T.report(case, TEXT.read_bytes(), case / "fidmech/boundaries.json")
    assert {c: row["hits"] for c, row in result["also_gated"].items()} == {"L1m": 3, "L1u": 1, "L1e": 1}
    assert "quote_evidence.py:39" in result["also_gated"]["L1m"]["by"]


def test_the_textcheck_command_writes_the_report_and_refuses_checks_of_later_batches(tmp_path, capsys):
    out = tmp_path / "l1.json"
    args = ["textcheck", "--doc", str(DOC), "--source", str(TEXT)]
    assert main(args + ["--checks", "L1", "--json", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "L1 hits: L1m 3, L1n 2, L1u 1, L1c 5, L1e 1" in printed
    assert json.loads(out.read_text(encoding="utf-8"))["counts"]["L1c"] == 5
    for checks in (["L2"], ["L1,L1a"], ["L4"]):
        assert main(args + ["--checks", *checks]) == 2
    assert "not built in this batch" in capsys.readouterr().err
    assert main(["textcheck", "--doc", str(tmp_path / "absent"), "--source", str(TEXT)]) == 2


def test_a_source_that_is_not_the_boundaries_source_is_refused(tmp_path, capsys):
    other = tmp_path / "source.txt"
    other.write_bytes(TEXT.read_bytes().replace(b"every review", b"every audit"))
    assert main(["textcheck", "--doc", str(DOC), "--source", str(other)]) == 2
    assert "boundaries are for source" in capsys.readouterr().err
    with pytest.raises(S.BoundariesError):
        S.Segmentation(S.Source(other.read_bytes()), replace(segmented().boundaries))


def test_the_occurrence_cap_fails_closed_a_capped_search_reports_a_hit_never_a_pass(monkeypatch):
    seg = segmented()
    assert classes(seg, 'F1 "We will keep records of every review."') == []
    monkeypatch.setattr(T, "MAX_OCCURRENCES", 0)
    assert classes(seg, 'F1 "We will keep records of every review."') == ["L1u"]
