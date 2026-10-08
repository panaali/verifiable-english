"""English E2.6: Lean's authority over English admission rests on saved evidence, checked from the files alone
(no live checkout, no git): the readability replay of the frozen evaluation against E2.5's saved base."""
import copy
import json
from pathlib import Path

from conformance import english_lean_e2_readability_report as R

ROOT = Path(__file__).resolve().parents[1]


def saved():
    return (R.read(R.EVIDENCE / "readability-base.jsonl"), R.read(R.HEAD / "readability-writing.jsonl"),
            R.read(R.EVIDENCE / "readability-reading-base.jsonl"), R.read(R.HEAD / "readability-reading.jsonl"))


def test_readability_comparison_is_regenerated_from_the_saved_records():
    summary, text = R.render()
    assert json.loads((R.HEAD / "readability-comparison.json").read_text()) == summary
    assert (R.HEAD / "readability-changes.md").read_text() == text


def test_readability_replay_has_no_regression():
    summary, changed, reading = R.compare(*saved())
    assert summary["writing_attempts"] == 36 and summary["reading_items"] == 30
    assert summary["writing_outcome_changes"] == 0
    assert summary["writing_message_changes"] == summary["writing_preserved_changes"] == 6
    assert summary["writing_regressions"] == [] and summary["regression"] is False
    assert summary["reading_unavailable"] == [] and summary["reading_differences"] == [] and reading == []
    assert summary["lean_reading_items"] == ["R23", "R24", "R25", "R29", "R30"]
    # Every changed message is Lean's diagnosis after Lean's code text, and Python's hand parser at this checkout
    # reproduces the saved base message, so its span is the base location.
    for c in changed:
        assert c["head"]["ve_message"].startswith("Sentence 1 has no reading with the current vocabulary. ")
        assert c["check"]["base_reproduced"] and c["check"]["location_kept"]


def test_the_five_items_e25_lost_have_lean_answers_equal_to_the_base():
    base = {r["item"]: r for r in saved()[2]}
    for row in saved()[3]:
        if row["item"] in ("R23", "R24", "R25", "R29", "R30"):
            assert row["route"] == "lean"
            assert (row["verdict"], row["message"]) == (base[row["item"]]["verdict"], base[row["item"]]["message"] or "")


def _damaged(change):
    """The saved records with the first changed attempt's head record edited by `change`."""
    base_w, head_w, base_r, head_r = saved()
    head_w = copy.deepcopy(head_w)
    target = next(i for i, (b, h) in enumerate(zip(base_w, head_w)) if b["ve_message"] != h["ve_message"]
                  and change(head_w[i]) is not False)
    return R.compare(base_w, head_w, base_r, head_r)[0], head_w[target]


def test_a_lost_name_location_suggestion_or_outcome_is_a_regression():
    """Each preservation condition can fail: the check is not a constant pass."""
    def drop_name(row):
        if "', then '" not in row["ve_message"]:
            return False
        row["ve_message"] = row["ve_message"].replace("', then '", "a comma")

    def move_span(row):
        row["span"] = [row["span"][1], row["span"][1] + 1]

    def drop_suggestion(row):
        if "Use the English paraphrase" not in row["ve_message"]:
            return False
        row["ve_message"] = row["ve_message"].replace(" Use the English paraphrase as a writing example.", "")

    def change_outcome(row):
        row["outcome"] = "wrong_meaning"

    def fragment_elsewhere(row):
        if "'that'" not in row["ve_message"]:
            return False
        row["ve_message"] = row["ve_message"].replace("'that'", "'reviewed'")

    for change in (drop_name, move_span, drop_suggestion, change_outcome, fragment_elsewhere):
        summary, row = _damaged(change)
        assert summary["regression"] is True, change.__name__
        assert summary["writing_regressions"] or summary["writing_outcome_changes"], change.__name__


def test_the_bare_code_text_and_a_lost_reading_item_are_regressions():
    base_w, head_w, base_r, head_r = saved()
    bare = [{**h, "ve_message": "Sentence 1 has no reading with the current vocabulary."}
            if h["ve_message"] != b["ve_message"] else h for b, h in zip(base_w, head_w)]
    assert len(R.compare(base_w, bare, base_r, head_r)[0]["writing_regressions"]) == 6
    lost = [{**r, "verdict": "unavailable", "message": "ImportError"} if r["item"] == "R23" else r for r in head_r]
    summary = R.compare(base_w, head_w, base_r, lost)[0]
    assert summary["reading_unavailable"] == ["R23"] and summary["regression"] is True
    wrong = [{**r, "verdict": "GAP"} if r["item"] == "R23" else r for r in head_r]
    assert R.compare(base_w, head_w, base_r, wrong)[0]["reading_differences"] == ["R23"]
