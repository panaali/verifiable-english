"""JT-E1r pre-call checks. These tests never invoke a reader model."""
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1] / "docs/judgment-terms/jt-e1r"
sys.path.insert(0, str(ROOT))
import render  # noqa: E402

spec = importlib.util.spec_from_file_location("jt_e1r_runner", ROOT / "runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_frozen_frame_and_real_capture_bytes():
    rows = render.rows()
    assert len(rows) == 40
    assert {r["answer"] for r in rows if r["id"].startswith("U")} == {"settled", "turns", "conditional"}
    assert {r["answer"] for r in rows if r["id"].startswith("C")} == {"settled", "turns", "conditional"}
    assert render.audit() == ["U17", "U18", "U19", "U20", "C17", "C18", "C19", "C20"]
    for row in rows:
        meta = __import__("json").loads((render.CAPTURES / f"{row['id']}.command.json").read_text())
        assert meta["commit"] == render.PIN
        assert meta["command"][1:4] == ["-m", "ve", "render"]
        assert meta["command"][-1].endswith(meta["document"])
        assert meta["command"][meta["command"].index("--env") + 1].endswith(meta["environment"])


def test_display_information_and_fallback():
    for row in render.rows():
        old, new = render.displays(row)
        common = render.common_text(row)
        for arm in ("identifier", "english"):
            body = runner.prompt(row, arm)
            assert body.startswith(runner.PROMPT)
            assert row["source"] in body and row["conclusion"] in body
            assert row["predicate"] in body and row["atom"] in body
            assert row["decider"] in body
            assert common in body
            assert "KEY:" not in body
        if row["lint"] == "accepted":
            assert old != new
            assert render.english(row, old) == new
            ending = ("; the text does not say who makes it."
                      if row["decider"] == "unstated" else f" for {row['decider']}.")
            assert new.decode() == f"Whether {row['atom']} is a judgment{ending}\n"
        else:
            assert old == new
            assert render.english(row, old) == old


def test_scoring_requires_class_and_decider_and_flags_critical():
    row = render.rows()[0]
    assert runner.score(row, "CLASS: TURNS; DECIDER: workplace board; WHY: dependent")["correct"]
    assert not runner.score(row, "CLASS: TURNS; DECIDER: NONE; WHY: dependent")["correct"]
    assert runner.score(row, "CLASS: SETTLED; DECIDER: NONE; WHY: checked")["critical"]
    assert not runner.score(row, "CLASS: TURNS; DECIDER: workplace board; WHY: not settled")["critical"]
    settled = render.rows()[1]
    assert runner.score(settled, "CLASS: SETTLED; DECIDER: NONE; WHY: independent")["correct"]
    assert not runner.score(settled, "CLASS: TURNS; DECIDER: NONE; WHY: maybe")["correct"]


def test_usage_is_fully_reported_and_no_credit_fallback():
    usage = {"usage": {"input_tokens": 1, "output_tokens": 2,
                       "cache_creation_input_tokens": 3, "cache_read_input_tokens": 4,
                       "fallback_credit": None}}
    assert runner.usage_cw(usage) == 10
    assert runner.within_caps(0, 0)
    assert runner.within_caps(99, runner.CW_CAP - runner.RESERVE_CW)
    assert not runner.within_caps(100, 0)
    assert not runner.within_caps(0, runner.CW_CAP - runner.RESERVE_CW + 1)
    assert runner.record_cw({"error": "CLI failed", "charged_cw": runner.RESERVE_CW}) == runner.RESERVE_CW
    with pytest.raises(RuntimeError):
        runner.record_cw({"error": "CLI failed", "charged_cw": 0})
    for bad in ({"usage": {**usage["usage"], "fallback_credit": True}},
                {"usage": {**usage["usage"], "output_tokens": True}},
                {"usage": {k: v for k, v in usage["usage"].items() if k != "output_tokens"}}):
        with pytest.raises(RuntimeError):
            runner.usage_cw(bad)


def test_original_items_are_not_reused():
    with (ROOT.parent / "jt-e1/items.tsv").open() as stream:
        old = stream.read()
    for row in render.rows():
        assert row["source"] not in old
        assert row["predicate"] not in old
