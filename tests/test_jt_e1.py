"""Local JT-E1 protocol checks; never makes a model call."""
import importlib.util
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / "docs/judgment-terms/jt-e1/runner.py"
SPEC = importlib.util.spec_from_file_location("jt_e1_runner", MODULE)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def test_frozen_frame_and_two_arm_preview():
    rows = runner.items()
    assert len(rows) == 40
    assert sum(r["template"] == "no" for r in rows) == 20
    for row in rows:
        old, new = runner.render(row, "identifier"), runner.render(row, "english")
        assert row["source"] in old and row["source"] in new
        assert row["conclusion"] in old and row["conclusion"] in new
        assert "Open reading:" in old and "classified as" in old
        assert row["predicate"] in old
        if row["template"] == "yes":
            assert row["atom"] in new and "is a judgment" in new
            assert old != new
        else:
            assert "classified as" in new
            assert row["predicate"] in new
            assert old == new
        if row["decider"] != "unstated":
            assert row["decider"] in old and row["decider"] in new
        # These are declaration previews, not invented zone or criterion answers.
        assert "left_to(" not in old and "conflict_free_given(" not in old
        assert f"KEY: {row['answer']}" not in old + new


def test_conditional_control_decider_is_visible_for_every_named_row():
    rows = [row for row in runner.items() if row["answer"] == "conditional"
            and row["decider"] != "unstated"]
    assert {row["id"] for row in rows} == {"U17", "U18", "U19", "C13", "C14", "C15", "C16"}
    for row in rows:
        assert f"Judgment decider: {row['decider']}." in runner.render(row, "identifier")


def test_missing_or_inconsistent_live_display_cannot_launch_study():
    rows = runner.items()
    with pytest.raises(ValueError, match="missing live renderer display"):
        runner.validate_live_display(rows)
    assert not hasattr(runner, "call")
    with pytest.raises(ValueError, match="missing live renderer display"):
        runner.main()
    captured = [dict(row, identifier_display=f"control {row['decider']}",
                     english_display=f"English {row['decider']}") for row in rows]
    with pytest.raises(ValueError, match="identifier fallback"):
        runner.validate_live_display(captured)
    for row in captured:
        row["identifier_display"] = f"Judgment decider: {row['decider']}."
        row["english_display"] = (row["identifier_display"] if row["template"] == "no"
                                  else f"English for {row['decider']}")
    runner.validate_live_display(captured)
    captured[33]["identifier_display"] = "criterion without its named decider"
    captured[33]["english_display"] = captured[33]["identifier_display"]
    with pytest.raises(ValueError, match="named decider absent"):
        runner.validate_live_display(captured)


def test_scoring_requires_class_and_decider_and_flags_critical_misreading():
    row = runner.items()[0]  # turns, unstated
    assert runner.score(row, "CLASS: TURNS; DECIDER: NONE; WHY: judgment matters")["correct"]
    assert not runner.score(row, "CLASS: TURNS; DECIDER: court; WHY: judgment matters")["correct"]
    wrong = runner.score(row, "CLASS: SETTLED; DECIDER: NONE; WHY: checked")
    assert not wrong["correct"] and wrong["critical"]
    assert runner.score(row, "No structured answer; it is checked")["critical"]
    assert not runner.score(row, "CLASS: TURNS; DECIDER: NONE; WHY: it is not settled")["critical"]
    settled = runner.items()[2]
    assert runner.score(settled, "CLASS: SETTLED; DECIDER: NONE; WHY: independent rule")["correct"]
    assert not runner.score(settled, "CLASS: TURNS; DECIDER: NONE; WHY: maybe")["critical"]


def test_call_and_context_caps():
    assert runner.within_budget(0, 0)
    assert runner.within_budget(99, 2_975_000)
    assert not runner.within_budget(100, 0)
    assert not runner.within_budget(0, 2_975_001)
    assert runner.usage_cw({"usage": {"input_tokens": 1, "output_tokens": 2,
                                       "cache_creation_input_tokens": 3,
                                       "cache_read_input_tokens": 4}}) == 10
