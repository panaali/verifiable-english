"""AP-7: the draw, the sample's binding, and the score recomputed from the saved records. No model call."""
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parents[1] / "docs/act-phrases/ap-7"


def load(name):
    spec = importlib.util.spec_from_file_location(f"ap7_{name}", HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


draw, runner = load("draw"), load("runner")
CAVEAT = ("Codex was at its credit cap (resets 2026-11-04), so both listing seats are Claude Opus 5.5 in separate "
          "sessions (DRI ruling reviews/dri-decisions-20261031-ap-7.md item 1); the 'both auditors list' readings "
          "therefore come from one model family, which can share blind spots; cross-family review is optional (lead "
          "2026-10-10).")


def ok(text):
    return {"answer": text, "charged_cw": 15_000}


FAILED = {"answer": "", "error": "CLI exit 1 or unsuccessful result", "charged_cw": 25_000}


def phrase(pid, readings):
    return {"id": pid, "readings": readings, "status": "ok" if readings else "none", "raw": 1,
            "meanings": len(readings)}


def test_draw_is_reproducible_and_feeds_the_sample():
    units = json.loads((HERE / "population.json").read_text())
    result = draw.draw(units)
    assert result == json.loads((HERE / "draw.json").read_text())
    assert (result["population"], result["eligible"], len(result["drawn"])) == (669, 195, 30)
    ids = [p["id"] for p in json.loads((HERE / "sample.json").read_text())]
    assert ids[16:] == result["drawn"] and len(ids) == len(set(ids)) == 46
    assert draw.eligible("Claude should seek and enjoy it") and draw.eligible("We want Claude to explore or ask")
    assert not draw.eligible("Claude and Anthropic should seek it") and not draw.eligible("Seek and enjoy it")


def test_sample_is_bound_to_its_sources_and_lean():
    ps = runner.phrases()
    lean = json.loads((HERE / "lean-readings.json").read_text())
    assert [p["id"] for p in ps] == [r["id"] for r in lean]
    for p in ps:
        assert p["focus"] in p["source"] and p["op"] in {"must", "mustNot", "may", "right"}
        assert p["status"] in {"ok", "none", "limit", "refused"} and (p["status"] == "ok") == bool(p["readings"])
    assert sum(bool(p["readings"]) for p in ps) == 20


def test_seats_are_blind_and_within_the_call_limit():
    ps = runner.phrases()
    keys = runner.keys(ps)
    assert len(keys) == len(set(keys)) == 92 + 2 * len(runner.batches(ps)) + 46 <= runner.CALL_CAP
    for p in ps:
        a, b = (runner.prompt(f"list-{s}-{p['id']}", ps, {}) for s in "AB")
        assert a == b and p["source"] in a and not any(r in a for r in p["readings"])
    assert all(len(batch) <= runner.JUDGE_BATCH and all(p["readings"] for p in batch) for batch in runner.batches(ps))


def test_preregistration_names_three_sessions_and_the_caveat():
    text = (HERE / "PRE-REGISTRATION.md").read_text()
    assert " ".join(CAVEAT.split()) in " ".join(text.split())
    assert "**Three distinct sessions:** seat A and seat B (the two blind listing auditors) and seat M (the matcher)" \
        in text
    assert "recall ≥ 90% of the readings both auditors list;" in text and "no skipped-middle reading." in text


def test_failed_calls_score_as_no_reading():
    ps = [phrase("p", ["L one", "L two"]), phrase("q", [])]
    full = {"list-A-p": ok("1. a\n2. b"), "list-B-p": ok("1. a\n2. b"), "list-A-q": ok("1. c"),
            "list-B-q": ok("1. c"), "judge-A-1": ok("p L1: YES\np L2: NO"), "judge-B-1": ok("p L1: NO\np L2: NO"),
            "match-p": ok("PAIR A1 B1 L1\nPAIR A2 B2 L2\nSKIPPED: NONE"), "match-q": ok("PAIR A1 B1 NONE\nSKIPPED: NONE")}
    s = runner.score(ps, full)
    assert (s["recall"], s["not_a_reading"], s["rejected"], s["with_reading"]) == ([2, 3], [1, 2], ["p L2"], [1, 2])
    assert s["bar_recall"] is False and s["bar_not_a_reading"] is False and s["bar_skipped"] is True
    # a failed listing lists none; a failed matching counts min(|A|, |B|) agreed and none matched
    assert runner.score(ps, full | {"list-B-p": FAILED})["recall"] == [0, 1]
    assert runner.score(ps, full | {"match-p": FAILED})["recall"] == [0, 3]
    assert runner.score(ps, {k: v for k, v in full.items() if k != "match-p"})["recall"] == [0, 3]
    # a failed judgement says NO to every reading of its batch
    assert runner.score(ps, full | {"judge-A-1": FAILED})["rejected"] == ["p L1", "p L2"]
    # a phrase with no Lean reading matches nothing: naming L1 unbinds the answer
    assert runner.score(ps, full | {"match-q": ok("PAIR A1 B1 L1\nSKIPPED: NONE")})["recall"] == [2, 3]
    assert runner.score(ps, full | {"match-p": ok("PAIR A1 B1 L1\nSKIPPED: L2")})["skipped_middle"] == ["p L2"]


def test_answers_are_typed_and_bound():
    good = "PAIR A1 B2 L1\nPAIR A2 B1 NONE\nSKIPPED: NONE"
    assert runner.matched(ok(good), 2, 2, 1) == {"pairs": [(1, 2, 1), (2, 1, None)], "skipped": []}
    for bad in ("PAIR A3 B1 L1\nSKIPPED: NONE", "PAIR A1 B3 L1\nSKIPPED: NONE", "PAIR A1 B1 L2\nSKIPPED: NONE",
                "PAIR A1 B1 L1\nPAIR A1 B2 NONE\nSKIPPED: NONE", "PAIR A1 B1 NONE\nPAIR A2 B1 NONE\nSKIPPED: NONE",
                "PAIR A1 B1 L1\nPAIR A2 B2 L1\nSKIPPED: NONE", "PAIR A1 B1 L1", "PAIR A1 B1 L1\nSKIPPED: L2",
                "PAIR A1 B1 L1\nSKIPPED: NONE\nSKIPPED: NONE", "PAIR A1 B1 L1 (same)\nSKIPPED: NONE",
                "PAIR A0 B1 NONE\nSKIPPED: NONE", "PAIR A1 B1 L1\nSKIPPED: L1, L1"):
        assert runner.matched(ok(bad), 2, 2, 1) is None, bad
    batch = [phrase("p", ["x", "y"])]
    assert runner.judged(ok("p L1: yes\np L2: NO"), batch) == {("p", 1): True, ("p", 2): False}
    for bad in ("p L1: YES", "p L1: YES\np L2: NO\np L3: NO", "p L1: YES\np L1: YES\np L2: YES",
                "q L1: YES\np L2: YES", "p L1: MAYBE\np L2: YES"):
        assert runner.judged(ok(bad), batch) == {("p", 1): False, ("p", 2): False}, bad
    assert runner.listed(ok("1. a\n   detail\n2. b")) == ["a", "b"]
    assert runner.listed(ok("1. a\n3. b")) == [] and runner.listed(ok("Readings: a, b")) == []
    assert runner.listed(FAILED) == [] and runner.listed(None) == []


def test_score_recomputes_from_the_saved_records():
    records = runner.records()
    assert set(records) <= set(runner.keys(runner.phrases())) and len(records) <= runner.CALL_CAP
    for key, record in records.items():
        assert record["prompt"] == runner.prompt(key, runner.phrases(), records), key
    result = runner.score(runner.phrases(), records)
    assert result == json.loads((HERE / "results.json").read_text())
    assert result["cw"] <= runner.CW_CAP
    gate = re.search(r"^GATE: (.+)$", (HERE / "RESULTS.md").read_text(), re.M).group(1)
    verdicts = [result[k] for k in ("bar_recall", "bar_not_a_reading", "bar_skipped")]
    assert gate == ("PASS" if all(verdicts) else "FAIL") + " (" + ", ".join(
        f"{name} {'PASS' if v else 'FAIL'}" for name, v in zip(("recall", "not a reading", "skipped middle"),
                                                                verdicts, strict=True)) + ")"
