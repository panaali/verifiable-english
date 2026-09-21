import pytest
from copy import deepcopy
import hashlib
import json
from math import sqrt
from statistics import stdev

from experiments.cluster_stats import cluster_t, planning_power
from experiments.E5.calibrate_power import calibrate, main
from experiments.E5.materials import HERE, render_cell
from experiments.trial_analysis import read_jsonl, paired_effects
from experiments.E2E4.analyze_e4 import analyze
from experiments.E2E4.materials import load_frozen


def test_cluster_interval_preserves_dependence_and_rejects_single_cluster():
    effects = [("a", -.1), ("b", .0), ("c", .2), ("d", .3)]
    base = cluster_t(effects)
    assert base == cluster_t(effects * 100)
    assert base["df"] == 3 and base["clusters"] == 4
    assert base["interval"][0] < base["estimate"] < base["interval"][1]
    with pytest.raises(ValueError):
        cluster_t([("a", .1), ("a", .2)])
    assert planning_power()["approximate_mde_80"] is None
    assert planning_power()["status"] == "PLACEHOLDER_REQUIRES_DEV_PILOT_VARIANCE"


def trial(item, condition, approved, **kwargs):
    return {"item_id": item["id"], "group": item["group"], "label": item["label"], "split": item["split"],
            "judge": "offline-fixture", "condition": condition, "sample": 0, "ok": True,
            "approved": approved, "parse_error": None, "tool_events": [], **kwargs}


@pytest.fixture
def pilot():
    items = read_jsonl(HERE / "dev.jsonl.gz")
    endpoint = [r for r in items if r["label"] == "bad" and r["payload"]["_audit"]["stratum"] == "primary"
                and r["payload"]["_audit"]["difficulty"] == "medium"]
    templates = sorted({r["payload"]["_audit"]["template"] for r in endpoint})
    trials = []
    for item in endpoint:
        effect = templates.index(item["payload"]["_audit"]["template"]) % 3 - 1
        for cell in ("a", "b"):
            approved = (effect == -1 if cell == "a" else effect == 1)
            trials.append(trial(item, cell + "_neutral", approved,
                prompt_sha=hashlib.sha256(render_cell(item, cell, "neutral").encode()).hexdigest()[:16]))
    return items, trials


def test_power_uses_observed_template_variance_and_records_provenance(pilot, tmp_path, monkeypatch):
    items, trials = pilot
    expected_sd = stdev(i % 3 - 1 for i in range(8))
    result = calibrate(trials, items, judge="offline-fixture", difficulty="medium", style="neutral")
    assert result["dev_clusters"] == 8 and result["clusters"] == 24
    assert result["dev_template_sd"] == pytest.approx(expected_sd)
    assert result["standard_error"] == pytest.approx(expected_sd / sqrt(24))
    assert result["assignment"]["assigned_trials"] == 128
    assert result["ready_to_freeze"] is False
    path, output = tmp_path / "trials.jsonl", tmp_path / "power.json"
    path.write_text("".join(json.dumps(row) + "\n" for row in trials))
    monkeypatch.setattr("sys.argv", ["calibrate_power", str(path), "--judge", "offline-fixture",
                                    "--difficulty", "medium", "--style", "neutral", "--output", str(output)])
    main()
    saved = json.loads(output.read_text())
    assert saved["inputs"][str(path)] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert saved["dev_template_sd"] == result["dev_template_sd"]


@pytest.mark.parametrize("fault,match", [("missing", "Incomplete"), ("duplicate", "Duplicate"),
    ("scored", "dev trials only"), ("stale", "prompt hash"), ("sample", "sample index")])
def test_power_refuses_incomplete_or_wrong_pilot(pilot, fault, match):
    items, original = pilot
    trials = deepcopy(original)
    if fault == "missing": trials.pop()
    if fault == "duplicate": trials.append(trials[0])
    if fault == "scored": trials[0]["split"] = "scored"
    if fault == "stale": trials[0]["prompt_sha"] = "old-materials"
    if fault == "sample": trials[0]["sample"] = 1
    with pytest.raises(ValueError, match=match):
        calibrate(trials, items, judge="offline-fixture", difficulty="medium", style="neutral")


def test_e4_analysis_treats_renamings_as_near_replicates_and_keeps_failures():
    items = load_frozen("scored", "E4")
    templates = sorted({r["payload"]["_audit"]["template"] for r in items})
    trials = [trial(item, condition, condition == "checked_countermodel" and
                    templates.index(item["payload"]["_audit"]["template"]) % 2 == 0)
              for item in items for condition in ("prose_critique", "checked_countermodel")]
    result = analyze(trials, items, judge="offline-fixture")
    for endpoint in result["endpoints"].values():
        assert endpoint["items"] == 60 and endpoint["clusters"] == 12 and endpoint["df"] == 11
        assert endpoint["estimate"] == .5
        assert endpoint["standard_error"] == pytest.approx(stdev([0, 1] * 6) / sqrt(12))
    item = next(r for r in items if r["label"] == "bad")
    broken = [trial(item, "a", False), trial(item, "b", False, ok=False)]
    effects, assignment = paired_effects(broken, [item], judge="offline-fixture", conditions=("a", "b"))
    assert effects[0][1] == 1 and assignment["failures"]["b"] == 1
    item = next(r for r in items if r["label"] == "good")
    broken = [trial(item, "a", True), trial(item, "b", True, tool_events=["invalid tool"])]
    effects, assignment = paired_effects(broken, [item], judge="offline-fixture", conditions=("a", "b"))
    assert effects[0][1] == -1 and assignment["failures"]["b"] == 1
