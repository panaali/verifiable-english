"""DF-E1's preregistered blind reader transport and scoring, without model calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "docs/defeasible/df-e1/runner.py"
spec = importlib.util.spec_from_file_location("df_e1_runner", source)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "HERE", tmp_path)
    rows = []
    for i in range(24):
        kind = "needs" if i < 12 else "strict"
        forms = {"long": [f"Rendered answer {i}"]}
        if i < 6:
            forms["short"] = [f"Short answer {i}"]
        rows.append({"id": f"I{i:02d}", "expected": "yes" if i < 12 else "no",
                     "class": kind, "rule_text": f"Rule {i}", "rendered": forms})
    (tmp_path / "items.json").write_text(json.dumps(rows))
    raw = tmp_path / "raw"
    raw.mkdir()
    for row, form in runner.jobs(rows):
        body = runner.prompt(row, form)
        key = (row["id"], form)
        reply = "ANSWER: YES" if row["expected"] == "yes" else "ANSWER: NO"
        (raw / f"{key[0]}__{form}.json").write_text(json.dumps({
            "id": key[0], "form": form, "reply": reply, "charged_cw": 10,
            "prompt_sha256": hashlib.sha256(body.encode()).hexdigest()}))
    return rows, raw


def test_prompt_contains_only_rule_answer_and_question(tmp_path, monkeypatch):
    rows, _ = fixture(tmp_path, monkeypatch)
    body = runner.prompt(rows[0], "short")
    assert body == ("Rule text:\nRule 0\n\nRendered answer:\nShort answer 0\n\n" +
                    runner.QUESTION + "\n\nANSWER: YES or NO")


def test_ambiguous_answer_is_not_scored():
    assert runner.parse("ANSWER: YES\nANSWER: NO") is None
    assert runner.parse("ANSWER: MAYBE") is None
    assert runner.parse("ANSWER: YES") == "yes"


def test_score_bar_and_short_comparison(tmp_path, monkeypatch):
    rows, raw = fixture(tmp_path, monkeypatch)
    assert runner.score()["outcome"] == "short form DROPPED"
    path = raw / "I00__long.json"
    rec = json.loads(path.read_text())
    rec["reply"] = "ANSWER: NO"
    path.write_text(json.dumps(rec))
    scored = runner.score()
    assert scored["long"]["needs_read_strict"] == 1
    assert scored["outcome"] == "short form KEPT"
    for name in ("I01", "I02"):
        path = raw / f"{name}__long.json"
        rec = json.loads(path.read_text())
        rec["reply"] = "ANSWER: NO"
        path.write_text(json.dumps(rec))
    assert runner.score()["outcome"] == "DF-3 waits for a redesign of the wording"


def test_strict_controls_count_for_both_forms(tmp_path, monkeypatch):
    _, raw = fixture(tmp_path, monkeypatch)
    for name in ("I12", "I13"):
        path = raw / f"{name}__long.json"
        rec = json.loads(path.read_text())
        rec["reply"] = "ANSWER: YES"
        path.write_text(json.dumps(rec))
    scored = runner.score()
    assert scored["long"]["strict_read_needs"] == 2
    assert scored["short"]["strict_read_needs"] == 2
    assert not scored["short"]["pass"]


def test_cw_uses_subscription_plan_weights():
    usage = {"input_tokens": 100, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 100,
             "output_tokens": 100}
    assert runner.cw(usage) == int(0.68 * (100 + 120 + 2.5 + 500))
    assert runner.cw(None) == runner.RESERVE_CW
