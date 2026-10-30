"""JT-E1r pre-call checks. These tests never invoke a reader model."""
import importlib.util
import json
from pathlib import Path
import subprocess
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
    failed = {"error": "CLI failed", "cli": usage, "charged_cw": runner.RESERVE_CW, "answer": ""}
    assert runner.record_cw(failed) == runner.RESERVE_CW
    with pytest.raises(RuntimeError):
        runner.record_cw(failed | {"charged_cw": 0})
    with pytest.raises(RuntimeError):
        runner.record_cw({"error": "CLI failed", "charged_cw": runner.RESERVE_CW})
    for bad in ({"usage": {**usage["usage"], "fallback_credit": True}},
                {"usage": {**usage["usage"], "output_tokens": True}},
                {"usage": {k: v for k, v in usage["usage"].items() if k != "output_tokens"}}):
        with pytest.raises(RuntimeError):
            runner.usage_cw(bad)


def reader_wrapper(cw=50_000, **changes):
    wrapper = {"subtype": "success", "is_error": False, "result": "CLASS: TURNS; DECIDER: NONE; WHY: x",
               "modelUsage": {runner.MODEL: {}},
               "usage": {**dict.fromkeys(runner.USAGE_KEYS, 0),
                         "input_tokens": cw, "fallback_credit": None}}
    return wrapper | changes


@pytest.mark.parametrize("arm", ["identifier", "english"])
@pytest.mark.parametrize("row_index", [0, 1, 2], ids=["turns", "settled", "conditional"])
def test_failed_call_charges_reported_usage_above_reserve(monkeypatch, arm, row_index):
    row = render.rows()[row_index]
    wrapper = reader_wrapper()
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k:
                        subprocess.CompletedProcess([], 1, json.dumps(wrapper), ""))
    record = runner.call(row, arm, "subscription")
    assert record["charged_cw"] == 50_000
    assert runner.record_cw(record) == runner.usage_cw(record["cli"])


@pytest.mark.parametrize("outcome,known", [
    ("failed", True), ("timeout", False), ("timeout_usage", True),
    ("oversized", True), ("large_record", True),
    ("invalid_model", True), ("invalid_result", True), ("invalid_usage", False),
    ("invalid_wrapper", False), ("overflow", True), ("failed_overflow", True),
])
def test_every_dispatched_outcome_is_saved_and_restart_is_blocked(tmp_path, monkeypatch, outcome, known):
    row = render.rows()[0]
    monkeypatch.setattr(runner, "RAW", tmp_path)
    monkeypatch.setattr(runner, "committed", lambda: None)
    monkeypatch.setattr(runner.render, "audit", lambda: None)
    monkeypatch.setattr(runner.render, "rows", lambda: [row])
    monkeypatch.setattr(runner, "account", lambda: "subscription")
    wrapper = reader_wrapper(cw=runner.CW_CAP + 1 if "overflow" in outcome else 50_000)
    if outcome == "invalid_model":
        wrapper["modelUsage"] = {"another-model": {}}
    elif outcome == "invalid_result":
        wrapper["result"] = []
    elif outcome == "invalid_usage":
        wrapper["usage"]["output_tokens"] = True
    elif outcome == "oversized":
        wrapper["result"] = "x" * (runner.RAW_CAP + 1)
    elif outcome == "large_record":
        wrapper["result"] = "x" * (runner.RAW_CAP - 2000)
    output = "[]" if outcome == "invalid_wrapper" else json.dumps(wrapper)
    calls = []

    def fake_run(*args, **kwargs):
        calls.append(args)
        assert (tmp_path / f"{row['id']}-identifier.json").exists()
        if outcome == "timeout":
            raise subprocess.TimeoutExpired(args[0], 1200)
        if outcome == "timeout_usage":
            raise subprocess.TimeoutExpired(args[0], 1200, output=output.encode())
        return subprocess.CompletedProcess(args[0], 1 if outcome in {"failed", "failed_overflow"} else 0,
                                           output, "")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError):
        runner.run()
    assert len(calls) == 1
    saved = json.loads((tmp_path / f"{row['id']}-identifier.json").read_text())
    assert (tmp_path / f"{row['id']}-identifier.json").stat().st_size <= runner.RAW_CAP
    if outcome == "overflow":
        assert "error" not in saved
    else:
        assert saved["error"]
    if known:
        assert runner.record_cw(saved) == saved["charged_cw"]
        assert saved["charged_cw"] >= 50_000
    else:
        assert saved["charged_cw"] is None
        with pytest.raises(RuntimeError):
            runner.record_cw(saved)
    with pytest.raises(RuntimeError):
        runner.run()
    assert len(calls) == 1


def test_interrupted_call_keeps_durable_dispatch_record(tmp_path, monkeypatch):
    row = render.rows()[0]
    monkeypatch.setattr(runner, "RAW", tmp_path)
    monkeypatch.setattr(runner, "committed", lambda: None)
    monkeypatch.setattr(runner.render, "audit", lambda: None)
    monkeypatch.setattr(runner.render, "rows", lambda: [row])
    monkeypatch.setattr(runner, "account", lambda: "subscription")

    def interrupted(*args):
        assert (tmp_path / f"{row['id']}-identifier.json").exists()
        raise KeyboardInterrupt

    monkeypatch.setattr(runner, "call", interrupted)
    with pytest.raises(KeyboardInterrupt):
        runner.run()
    saved = json.loads((tmp_path / f"{row['id']}-identifier.json").read_text())
    assert saved["state"] == "dispatched" and saved["charged_cw"] is None
    with pytest.raises(RuntimeError, match="unaccounted raw call"):
        runner.run()


@pytest.mark.parametrize("mutation", [
    lambda record: record.update(answer="changed"),
    lambda record: record["cli"].update(modelUsage={"another-model": {}}),
    lambda record: record["cli"]["usage"].update(input_tokens=True),
    lambda record: record.update(charged_cw=0),
    lambda record: record.update(state="dispatched"),
])
def test_saved_result_rejects_accounting_and_result_tampering(mutation):
    record = json.loads((ROOT / "raw/C01-english.json").read_text())
    assert runner.record_cw(record) == record["charged_cw"]
    mutation(record)
    with pytest.raises(RuntimeError):
        runner.record_cw(record)


def fail_record(record):
    record.update(error="CLI failed", exit_code=1, answer="",
                  charged_cw=max(runner.RESERVE_CW, runner.usage_cw(record["cli"])))
    return record


def test_failed_accounted_call_scores_incorrect_and_not_critical(monkeypatch):
    """F2: PRE-REGISTRATION.md says call errors count incorrect; the frame still scores."""
    saved = runner.existing()
    baseline = runner.results()
    records = json.loads(json.dumps(saved))
    monkeypatch.setattr(runner, "existing", lambda: records)
    fail_record(records["U02-english.json"])
    probe = runner.results()
    assert probe["counts"] == {"identifier": baseline["counts"]["identifier"], "english": 19}
    assert probe["errors"] == ["U02-english"] and baseline["errors"] == []
    assert probe["cw"] == 1_201_615 == baseline["cw"] + runner.RESERVE_CW - runner.usage_cw(
        saved["U02-english.json"]["cli"])
    for name, record in saved.items():
        records = json.loads(json.dumps(saved))
        fail_record(records[name])
        arm = record["arm"]
        was = runner.score(next(r for r in render.rows() if r["id"] == record["id"]), record["answer"])
        scored = runner.results()
        assert scored["counts"][arm] == baseline["counts"][arm] - was["correct"], name
        assert scored["errors"] == [name.removesuffix(".json")]
        assert scored["calls"] == 80 and scored["cw"] == sum(r["charged_cw"] for r in records.values())


def test_failed_call_answer_is_never_scored_or_critical(monkeypatch):
    records = json.loads(json.dumps(runner.existing()))
    for name in ("U01-english.json", "C03-identifier.json"):
        fail_record(records[name])
    monkeypatch.setattr(runner, "existing", lambda: records)
    scored_answers = []

    def misread(row, answer):
        scored_answers.append(answer)
        return {"correct": True, "critical": True, "class": "SETTLED", "decider": "NONE"}

    monkeypatch.setattr(runner, "score", misread)
    result = runner.results()
    assert len(scored_answers) == 78 and "" not in scored_answers
    assert result["counts"] == {"identifier": 39, "english": 39}
    assert "U01" not in result["critical"] and len(result["critical"]) == 39
    assert result["errors"] == ["C03-identifier", "U01-english"]


@pytest.mark.parametrize("mutation", [
    lambda record: record.update(charged_cw=None),
    lambda record: record["cli"].pop("usage"),
    lambda record: record["cli"]["usage"].update(fallback_credit=True),
    lambda record: record.update(charged_cw=runner.RESERVE_CW - 1),
    lambda record: record.update(answer="CLASS: TURNS; DECIDER: NONE; WHY: x"),
    lambda record: record.update(state="dispatched"),
], ids=["unknown_charge", "no_usage", "credit_fallback", "undercharged", "answer_kept", "dispatched"])
def test_failed_call_with_unknown_usage_still_blocks_scoring(monkeypatch, mutation):
    records = json.loads(json.dumps(runner.existing()))
    mutation(fail_record(records["U02-english.json"]))
    monkeypatch.setattr(runner, "existing", lambda: records)
    with pytest.raises(RuntimeError):
        runner.results()


@pytest.mark.parametrize("drop", [1, 2, 80])
def test_scoring_requires_all_80_records(monkeypatch, drop):
    records = json.loads(json.dumps(runner.existing()))
    for name in sorted(records)[:drop]:
        del records[name]
    monkeypatch.setattr(runner, "existing", lambda: records)
    with pytest.raises(RuntimeError, match=f"only {80 - drop} of 80"):
        runner.results()


def test_original_items_are_not_reused():
    with (ROOT.parent / "jt-e1/items.tsv").open() as stream:
        old = stream.read()
    for row in render.rows():
        assert row["source"] not in old
        assert row["predicate"] not in old
