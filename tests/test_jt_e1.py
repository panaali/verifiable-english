"""Local JT-E1 protocol checks; never makes a model call."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "docs/judgment-terms/jt-e1/runner.py"
SPEC = importlib.util.spec_from_file_location("jt_e1_runner", MODULE)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def test_frozen_frame_and_two_arm_rendering():
    rows = runner.items()
    assert len(rows) == 40
    assert sum(r["template"] == "no" for r in rows) == 20
    for row in rows:
        old, new = runner.render(row, "identifier"), runner.render(row, "english")
        assert row["source"] in old and row["source"] in new
        assert row["conclusion"] in old and row["conclusion"] in new
        assert row["predicate"] in old and row["atom"] in new
        assert "Open reading:" in old and "classified as" in old
        assert "is a judgment" in new
        assert old != new
        assert f"KEY: {row['answer']}" not in old + new


def test_scoring_requires_class_and_decider_and_flags_critical_misreading():
    row = runner.items()[0]  # turns, unstated
    assert runner.score(row, "CLASS: TURNS; DECIDER: NONE; WHY: judgment matters")["correct"]
    assert not runner.score(row, "CLASS: TURNS; DECIDER: court; WHY: judgment matters")["correct"]
    wrong = runner.score(row, "CLASS: SETTLED; DECIDER: NONE; WHY: checked")
    assert not wrong["correct"] and wrong["critical"]
    assert runner.score(row, "No structured answer; it is checked")["critical"]
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
