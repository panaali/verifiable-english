"""tools/fidmech/sentchecks.py: L1a, L2, L3, L4 and D on the fixture case tests/data/fidmech/b2.

The fixture is clean in every check (no hit). Each plant of the plan's section 10 table is one edit of a copy of it
under tmp_path and gives exactly its class: L1a (a quote of a sentence in another block's linked span; the wrong
sentence of the right linked span; an unlinked block's quote that occurs twice), L2b ("section 3 at {0}"), L2q (a
legend quoting half a sentence), L2a (a legend quoting a sentence of an unrelated span), L3w ("after" added to an act
phrase; "within one week" added where the source says "In selecting"), L4u (a rule deleted whose sentence carries
"will"), L4l (a "We conduct ..." sentence of an exposition unit left uncovered), L4g (a sentence a legend quote alone
covers) and D (the full quote holds "final", the act does not, the legend quotes the sentence: "final" is listed).
"""
import json
import shutil
from pathlib import Path

import pytest

from tools.fidmech import segment as S
from tools.fidmech import sentchecks as C
from tools.fidmech import textchecks as T
from tools.fidmech.__main__ import main

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/data/fidmech/b2"
B2 = ("L1a", "L2", "L3", "L4", "D")


def copy(tmp_path) -> Path:
    case = tmp_path / "b2"
    shutil.copytree(FIX, case)
    return case


def edit(case: Path, name: str, old: str, new: str):
    path = case / name
    text = path.read_text(encoding="utf-8")
    assert old in text, (name, old)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def drop_block(case: Path, name: str, block_id: str):
    lines = (case / name).read_text(encoding="utf-8").splitlines(keepends=True)
    k = next(i for i, line in enumerate(lines) if line.startswith(f"## {block_id} |"))
    (case / name).write_text("".join(lines[:k] + lines[k + 2:]), encoding="utf-8")


def legend(case: Path, name: str, description: str | None = None, act: str | None = None):
    env = json.loads((case / "environment.d1.json").read_text(encoding="utf-8"))
    entry = env["vocabulary"]["predicates"][name]
    if description is not None:
        entry["description"] = description
    if act is not None:
        entry["regulated"]["act"] = act
    (case / "environment.d1.json").write_text(json.dumps(env), encoding="utf-8")


def run(case: Path, checks) -> dict:
    return C.report(case, (case / "source.txt").read_bytes(), case / "fidmech/boundaries.json", checks)


def hits(result, cls):
    return [h for h in result["hits"] if h["class"] == cls]


# Each plant: (edit of the copy, the checks run, the class it gives, its count, a fragment of the hit's quote).
def p_l1a_other_span(c):
    edit(c, "rules.d1.ve", 'section 1 "We will answer each request within 30 days of receipt."',
         'section 1 "We will answer each request within 30 days of receipt." "We will keep records of every review."')


def p_l1a_wrong_sentence(c):
    edit(c, "rules.d1.ve", 'section 1 "We will keep records of every review."', 'section 1 "Staff check records."')


def p_l1a_unlinked_twice(c):
    with (c / "facts.d1.ve").open("a", encoding="utf-8") as f:
        f.write('## f-ends | always | section 1 "Each review ends with a summary."\n"review_summary" is listed.\n')


def p_l2b(c):
    legend(c, "report_shared", description="section 3 at {0}")


def p_l2q(c):
    legend(c, "records_kept", description='records are kept at {0}; section 1: "We will keep records"')


def p_l2a(c):
    legend(c, "records_kept", description='records are kept at {0}; section 1: "We will share the final report with '
                                          'the Board."')


def p_l3_after(c):
    legend(c, "records_kept", act="{0} keep records of every review after the audit")
    edit(c, "rules.d1.ve", "must keep records of every review.", "must keep records of every review after the audit.")


def p_l3_within(c):
    legend(c, "independence_weighed", act="{0} weigh the independence of reviewers in selecting within one week")
    edit(c, "rules.d1.ve", "reviewers in selecting,", "reviewers in selecting within one week,")


def p_l4u(c):
    drop_block(c, "rules.d1.ve", "r-publish")


def p_l4l(c):
    drop_block(c, "facts.d1.ve", "f-conduct")


def p_l4g(c):
    drop_block(c, "rules.d1.ve", "r-publish")
    legend(c, "report_shared", description='the report goes to the Board at {0}; section 1: "We will share the final '
                                           'report with the Board."; and "We will publish a summary after each review."')


def p_d_final(c):
    legend(c, "report_shared", act="{0} share the report with the Board")
    edit(c, "rules.d1.ve", "must share the final report", "must share the report")


PLANTS = {
    "L1a-other-span": (p_l1a_other_span, ("L1", "L1a"), "L1a", 1, "We will keep records of every review."),
    "L1a-wrong-sentence": (p_l1a_wrong_sentence, ("L1", "L1a"), "L1a", 1, None),
    "L1a-unlinked-twice": (p_l1a_unlinked_twice, ("L1", "L1a"), "L1a", 1, "Each review ends with a summary."),
    "L2b": (p_l2b, ("L2",), "L2b", 1, None),
    "L2q": (p_l2q, ("L2",), "L2q", 1, "We will keep records"),
    "L2a": (p_l2a, ("L2",), "L2a", 1, "We will share the final report"),
    "L3w-after": (p_l3_after, ("L3",), "L3w", 1, "after"),
    "L3w-within": (p_l3_within, ("L3",), "L3w", 1, "within"),
    "L4u": (p_l4u, ("L4",), "L4u", 1, "We will publish a summary after each review."),
    "L4l": (p_l4l, ("L4",), "L4l", 1, "We conduct a safety review before each release."),
    "L4g": (p_l4g, ("L4",), "L4g", 1, "We will publish a summary after each review."),
    "D-final": (p_d_final, ("D",), "D", 1, "final"),
}


def test_the_clean_fixture_has_no_hit_in_any_check():
    result = run(FIX, C.CHECKS)
    assert result["hits"] == []
    assert set(result["counts"]) == {c for cs in C.CLASSES.values() for c in cs} | {"L4g"}
    info = result["info"]
    assert info["L1a"] == {"linked_blocks": 5, "unlinked_blocks": 1}
    assert info["L4"]["obligation_bearing"] == 7 and info["D"]["sidecar"] is True
    for check in B2:
        assert run(FIX, (check,))["hits"] == []


@pytest.mark.parametrize("plant", PLANTS)
def test_each_plant_gives_exactly_its_class(plant, tmp_path):
    change, checks, cls, n, quote = PLANTS[plant]
    case = copy(tmp_path)
    change(case)
    result = run(case, checks)
    assert {c: k for c, k in result["counts"].items() if k} == {cls: n}, result["hits"]
    if quote is not None:
        assert quote in hits(result, cls)[0]["quote"]


def test_l1a_is_the_last_class_a_quote_with_an_earlier_class_gets_no_l1a(tmp_path):
    case = copy(tmp_path)
    edit(case, "rules.d1.ve", 'section 1 "We will answer each request within 30 days of receipt."',
         'section 1 "We will answer each request within 30 days of receipt." "We will keep records of every"')
    result = run(case, ("L1", "L1a"))
    assert {c: k for c, k in result["counts"].items() if k} == {"L1c": 1}


def test_the_wrong_sentence_plant_names_the_unquoted_cue_sentence(tmp_path):
    case = copy(tmp_path)
    p_l1a_wrong_sentence(case)
    [hit] = hits(run(case, ("L1", "L1a")), "L1a")
    assert hit["block"] == "r-records" and hit["quote"] is None
    assert "'will'" in hit["detail"] and "We will keep records of every review." in hit["detail"]


def test_l2_counts_the_legends_it_does_not_check():
    info = run(FIX, ("L2",))["info"]["L2"]
    assert info == {"regulated": 5, "passages_unlinked": 0,
                    "not_checked": {"base_predicates": 1, "base_bare": 1, "open_terms": 0}}


def test_a_legend_passage_inside_brackets_is_a_note_and_the_l2b_detail_says_so(tmp_path):
    case = copy(tmp_path)
    legend(case, "report_shared", description='the report goes to the Board at {0} (section 1: "We will share the '
                                              'final report with the Board.")')
    [hit] = hits(run(case, ("L2",)), "L2b")
    assert "1 inside, read as translator's notes" in hit["detail"]


def test_l2q_includes_an_elided_legend_passage(tmp_path):
    case = copy(tmp_path)
    legend(case, "records_kept", description='records are kept at {0}; section 1: "We will keep records ... review."')
    [hit] = hits(run(case, ("L2",)), "L2q")
    assert "L1e" in hit["detail"]


def test_the_rule_line_less_the_ve_template_keeps_no_guard_if():
    blocks = {b["id"]: b for b in T.read_blocks(FIX)}
    seg = S.Segmentation(S.Source((FIX / "source.txt").read_bytes()), S.load_boundaries(FIX / "fidmech/boundaries.json"))
    data = C.load_case(FIX, seg)
    b = blocks["r-select"]
    own = dict(C.own_words(b, data, S.accounting.used_names(b["text"], data.legend)))
    assert " if " in b["text"] and " if " not in own["rule line"] and "selection" not in own["rule line"]
    assert "act of independence_weighed" in own and "legend of selection" in own


def test_l3_uses_the_header_quote_when_l1_locates_no_sentence_and_says_so(tmp_path):
    case = copy(tmp_path)
    edit(case, "rules.d1.ve", '"We will publish a summary after each review."',
         '"We will publish a summary following each review."')
    [hit] = hits(run(case, ("L3",)), "L3w")
    assert hit["block"] == "r-publish" and hit["quote"] == "after" and "header quote" in hit["detail"]


def test_l4_coverage_by_unformalised_units_and_ruled_out_entries_are_levers(tmp_path):
    result = run(FIX, ("L4",))
    at = (FIX / "source.txt").read_bytes().index(b"We will train")
    assert result["levers"]["unformalised"]["cleared"] == [
        ["L4u", f"main@{at}", "We will train new staff each year."]]
    case = copy(tmp_path)
    p_l4u(case)
    seg = S.Segmentation(S.Source((case / "source.txt").read_bytes()),
                         S.load_boundaries(case / "fidmech/boundaries.json"))
    s = next(s for s in seg.streams[0].sentences if s.text.startswith("We will publish"))
    (case / "fidmech/ruled_out.json").write_text(json.dumps(
        [{"at": s.start, "sentence": s.text[:60], "reason": "test: ruled out by a translator", "by": "test"}]))
    result = run(case, ("L4",))
    assert {c: k for c, k in result["counts"].items() if k} == {}
    assert result["levers"]["ruled_out"]["cleared"] == [["L4u", f"main@{s.start}", s.text]]


def test_d_lists_the_word_a_legend_quote_alone_carries_and_the_sidecar_can_cover_it(tmp_path):
    case = copy(tmp_path)
    p_d_final(case)
    [hit] = hits(run(case, ("D",)), "D")
    assert hit["block"] == "r-share" and hit["quote"] == "final" and "outside" not in hit["detail"]
    edit(case, "accounting.d1.txt", "r-share | omits: nothing", 'r-share | omits: "final" exposition')
    result = run(case, ("D",))
    assert result["hits"] == []
    assert result["levers"]["sidecar"]["cleared"] == [["D", "r-share", "final"]]


def test_every_loss_entry_is_a_d_hit(tmp_path):
    case = copy(tmp_path)
    edit(case, "accounting.d1.txt", "r-share | omits: nothing", 'r-share | omits: "final report" loss 1')
    [hit] = hits(run(case, ("D",)), "D")
    assert hit["quote"] == "loss 1: final report"


def test_d_counts_what_lies_outside_the_header_quote(tmp_path):
    case = copy(tmp_path)
    edit(case, "rules.d1.ve", '"We will share the final report with the Board."', '"We will share the final report"')
    edit(case, "rules.d1.ve", "must share the final report with the Board.", "must share the final report.")
    legend(case, "report_shared", act="{0} share the final report",
           description='the report is shared at {0}; section 1: "We will share the final report with the Board."')
    result = run(case, ("D",))
    [hit] = hits(result, "D")
    assert hit["quote"] == "board" and "outside the header quote" in hit["detail"]
    assert result["info"]["D"]["outside_quote"] == 1


def test_a_case_without_a_sidecar_lists_every_unaccounted_word(tmp_path):
    case = copy(tmp_path)
    p_d_final(case)
    (case / "accounting.d1.txt").unlink()
    result = run(case, ("D",))
    assert result["info"]["D"]["sidecar"] is False
    assert [h["quote"] for h in hits(result, "D")] == ["final"]


@pytest.mark.parametrize("text, cue", [
    ("We will keep records.", "will"),
    ("Each record is required for audit.", "required"),
    ("Staff may not delete records.", "may not"),
    ("We conduct a safety review before each release.", "We conduct"),
    ("We also conduct a review.", "We also conduct"),
    ("Anthropic conducts a review.", "Anthropic conducts"),
    ("We believe reviews help.", None),
    ("We conduct reviews when we can.", None),
    ("We conducted a review last year.", None),
    ("We currently.", None),
    ("Our staff check records.", None),
])
def test_the_obligation_cues(text, cue):
    assert C.load_cues("anthropic-rsp").cue(text) == cue


def test_the_company_cue_is_per_document():
    assert C.load_cues("openai-preparedness").cue("OpenAI conducts a review.") == "OpenAI conducts"
    assert C.load_cues("anthropic-rsp").cue("OpenAI conducts a review.") is None


@pytest.mark.parametrize("change, message", [
    (lambda s: {"at": s.start}, "needs exactly"),
    (lambda s: [], "needs exactly"),
    (lambda s: {"at": s.start, "sentence": s.text[:60], "reason": "x", "by": "t", "extra": 1}, "needs exactly"),
    (lambda s: {"at": s.start, "sentence": s.text[:60], "reason": " ", "by": "t"}, "without a reason"),
    (lambda s: {"at": s.start, "sentence": s.text[:60], "reason": "x", "by": ""}, "without a by"),
    (lambda s: {"at": str(s.start), "sentence": s.text[:60], "reason": "x", "by": "t"}, "no sentence start"),
    (lambda s: {"at": True, "sentence": s.text[:60], "reason": "x", "by": "t"}, "no sentence start"),
    (lambda s: {"at": s.start + 3, "sentence": s.text[:60], "reason": "x", "by": "t"}, "no sentence start"),
    (lambda s: {"at": 10 ** 6, "sentence": s.text[:60], "reason": "x", "by": "t"}, "no sentence start"),
    (lambda s: {"at": s.start, "sentence": "We will publish nothing.", "reason": "x", "by": "t"}, "not 'We will"),
])
def test_a_ruled_out_entry_without_a_reason_or_outside_the_source_is_refused(change, message, tmp_path):
    case = copy(tmp_path)
    seg = S.Segmentation(S.Source((case / "source.txt").read_bytes()),
                         S.load_boundaries(case / "fidmech/boundaries.json"))
    s = next(s for s in seg.streams[0].sentences if s.text.startswith("We will publish"))
    path = case / "fidmech/ruled_out.json"
    path.write_text(json.dumps([change(s)]))
    with pytest.raises(C.DataError, match=message):
        C.load_ruled_out(path, seg)
    good = {"at": s.start, "sentence": s.text[:60], "reason": "x", "by": "t"}
    path.write_text(json.dumps([good, good]))
    with pytest.raises(C.DataError, match="two entries"):
        C.load_ruled_out(path, seg)
    path.write_text(json.dumps({"entries": [good]}))
    with pytest.raises(C.DataError, match="must be a list"):
        C.load_ruled_out(path, seg)
    path.write_text(json.dumps([good]))
    assert C.load_ruled_out(path, seg) == (good,)


def test_the_textcheck_command_runs_the_b2_checks_with_the_sentence_span(tmp_path, capsys):
    out = tmp_path / "b2.json"
    args = ["textcheck", "--doc", str(FIX), "--source", str(FIX / "source.txt")]
    assert main(args + ["--checks", "L1a,L2,L3,L4,D", "--span", "sentence", "--json", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "L1a+L2+L3+L4+D hits: L1a 0, L2b 0, L2q 0, L2a 0, L3w 0, L4u 0, L4l 0, D 0, L4g 0" in printed
    assert "ruled_out off:" in printed and "sidecar off:" in printed and "unformalised off:" in printed
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["checks"] == list(B2) and result["data_sha256"]["cues.json"]
    assert main(args + ["--checks", "all"]) == 0
    assert "L1+L1a+L2+L3+L4+D hits:" in capsys.readouterr().out
    assert main(args + ["--checks", "L5"]) == 2
    assert "unknown checks ['L5']" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        main(args + ["--checks", "D", "--span", "quote"])
