"""Offline contracts: assignment, leakage boundary, freeze gate, scoring, context guard."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from experiments.colab_common import DEFAULT_SYSTEM, ROOT, read_budget, trial_rows
from experiments.colab_scoring import analyze, join_outputs, parse_verdict, discover_outputs, markdown
from experiments.E5.colab.preflight import check
from experiments.E5.colab import export_prompts as exporter
from experiments.E2E4.colab import export_prompts as other_exporter
from experiments.E5.materials import render_cell
from experiments.E2E4.materials import load_frozen, render_cell as render_other
from experiments.trial_analysis import read_jsonl


def fixture_labels():
    labels = []
    for template in range(3):
        # Unequal item counts ensure the interval averages TEMPLATE means.
        for vocab in range(template + 1):
            for label in ("bad", "good"):
                for control in (False, True):
                    for cell in "abcde":
                        item = f"{template}-{vocab}-{label}-{control}"
                        labels.append({"key": f"{item}|{cell}|neutral", "item_id": item, "cell": cell,
                            "instruction": "neutral", "experiment": "E5", "split": "dev",
                            "label": "bad" if control else label, "family": "merged_vocabulary",
                            "template": str(template), "vocabulary": str(vocab), "control": control,
                            "control_type": "converse" if control else "none", "forged_tag": label == "bad",
                            "tag_condition": "forged" if label == "bad" else "honest", "difficulty": "medium",
                            "valid_deduction": not control, "grounding_label": label, "grounding_variant": "profile",
                            "size": None, "workload": None, "checker_visibility": None, "max_new_tokens": 400,
                            "prompt_sha": "fixture"})
    return labels


def reply(label, approved=False, **extra):
    return {"key": label["key"], "text": json.dumps({"verdict": "approve" if approved else "reject"}),
            "finish_reason": "stop", **extra}


@pytest.mark.parametrize("text,expected", [
    ('reasoning\n```json\n{"verdict":"approve"}\n```', "approve"),
    ('{"verdict":"reject"}\n{"verdict":"approve"}', "approve"),
    ('{"verdict":"approve"} trailing', None), ('{"verdict":"APPROVE"}', None),
    ('I approve', None), ('{"verdict":["approve"]}', None), ('{"other":"approve"}', None),
    (None, None), ('{"verdict":"reject", "reason":{"foo":1}}', "reject"),
])
def test_final_json_only(text, expected):
    assert parse_verdict(text) == expected


def test_synthetic_primary_pairs_templates_controls_and_failures():
    labels = fixture_labels()
    outputs = [reply(r, r["cell"] == "b" and (r["template"] == "0" or r["control"])) for r in labels]
    # BAD parse failure counts approved, GOOD parse failure rejected; truncation recorded.
    victim = next(i for i, r in enumerate(labels) if not r["control"] and r["label"] == "bad" and r["cell"] == "c")
    outputs[victim].update(text='{"verdict":', finish_reason="length")
    good = next(i for i, r in enumerate(labels) if r["label"] == "good" and r["cell"] == "c")
    outputs[good].update(text="approve", finish_reason="length")
    result = analyze(labels, {"synthetic": outputs})
    primary = next(r for r in result["contrasts"] if r["role"] == "primary")
    assert primary["estimate"] == pytest.approx(1/3)  # not 1/6 item-weighted
    assert primary["clusters"] == 3 and primary["df"] == 2 and primary["pairs"] == 6
    assert primary["template_means"] == {"0": 1, "1": 0, "2": 0}
    assert primary["interval"][0] < 0 < primary["interval"][1]
    metric = next(r for r in result["metrics"] if r["subset"] == "primary" and r["family"] == "ALL" and r["cell"] == "c")
    assert metric["false_approval"]["count"] == 1
    assert metric["honest_acceptance"]["count"] == 0
    assert metric["parse_failure"]["count"] == metric["truncated"]["count"] == 2
    assert any(r["subset"] == "merged_vocabulary:forged_tags" for r in result["contrasts"])
    assert any(r["subset"] == "control:converse:good" for r in result["metrics"])
    assert {r["contrast"] for r in result["contrasts"]} >= {"b-a", "c-b", "d-c", "e-d"}
    assert "95%" in markdown(result)


def test_missing_whole_model_and_partial_outputs_stay_in_denominators():
    labels = fixture_labels()
    result = analyze(labels, {"missing-model": []})
    assert result["judges"][0]["missing"] == len(labels)
    for r in result["metrics"]:
        assert r["missing"]["count"] == r["n"]
        assert r["false_approval"]["rate"] in (None, 1)
        assert r["honest_acceptance"]["rate"] in (None, 0)
    rows = join_outputs(labels, [reply(labels[0], False, error="backend failed")])
    assert rows[0]["approved"] == 1 and rows[0]["backend_failure"]
    assert sum(r["missing"] for r in rows) == len(labels) - 1


def test_invalid_assignments_fail_instead_of_dropping_rows():
    labels = fixture_labels()
    with pytest.raises(ValueError, match="Duplicate output"):
        join_outputs(labels, [reply(labels[0]), reply(labels[0])])
    with pytest.raises(ValueError, match="Unexpected"):
        join_outputs(labels, [{"key": "unknown", "text": ""}])
    with pytest.raises(ValueError, match="Duplicate label"):
        analyze(labels + [labels[0]], {"judge": []})
    with pytest.raises(ValueError, match="Incomplete paired"):
        analyze(labels[1:], {"judge": []})
    changed = deepcopy(labels)
    changed[0]["template"] = "wrong"
    with pytest.raises(ValueError, match="Metadata differs"):
        analyze(changed, {"judge": []})


def test_frozen_means_first_line_and_exact_head_bytes(tmp_path):
    def git(*args):
        return subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    git("init", "-q")
    p = tmp_path / "PREREG.md"
    p.write_text("Draft\nmax_new_tokens: 400\n")
    assert read_budget(p, "dev", tmp_path) == 400
    with pytest.raises(ValueError, match="Status: FROZEN"):
        read_budget(p, "scored", tmp_path)
    p.write_text("Status: FROZEN\nmax_new_tokens: 400\n")
    with pytest.raises(ValueError, match="byte-identical"):
        read_budget(p, "scored", tmp_path)
    git("add", "PREREG.md")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "freeze")
    assert read_budget(p, "scored", tmp_path) == 400
    git("update-index", "--assume-unchanged", "PREREG.md")
    p.write_text(p.read_text() + "dirty\n")
    with pytest.raises(ValueError, match="byte-identical"):
        read_budget(p, "scored", tmp_path)


def test_draft_export_refuses_before_creating_directory(tmp_path):
    with pytest.raises(ValueError, match="Status: FROZEN"):
        exporter.export(split="scored", difficulty="medium", instruction="neutral", cells="a,b", out=tmp_path / "e5")
    for experiment in ("E2", "E4"):
        with pytest.raises(ValueError, match="Status: FROZEN"):
            other_exporter.export(experiment=experiment, split="scored", cells=None, out=tmp_path / experiment)
    assert not list(tmp_path.iterdir())


def test_exact_token_context_guard_includes_response_and_template():
    class FakeTokenizer:
        init_kwargs = {"_commit_hash": "test"}
        def apply_chat_template(self, messages, *, add_generation_prompt, tokenize):
            assert add_generation_prompt and not tokenize
            return "SYSTEM USER ASSISTANT " + messages[-1]["content"]
        def __call__(self, text, *, add_special_tokens):
            assert not add_special_tokens
            return SimpleNamespace(input_ids=text.split())
    row = {"key": "test|a|neutral", "messages": [{"role": "user", "content": "one two"}], "max_new_tokens": 400}
    specs = [{"id": "fake", "max_model_len": 405}]
    assert check([row], specs, lambda _: FakeTokenizer())[0]["prompts_over_context"] == 0
    specs[0]["max_model_len"] = 404
    assert check([row], specs, lambda _: FakeTokenizer())[0]["prompts_over_context"] == 1
    assert row["messages"][0]["content"] == "one two"


def test_export_matches_harness_and_labels_cannot_be_uploaded(tmp_path, monkeypatch):
    source = subprocess.check_output(["git", "show", "claude/harness:ve_experiments/llm.py"], cwd=ROOT, text=True)
    system = next(ast.literal_eval(n.value) for n in ast.parse(source).body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "DEFAULT_SYSTEM" for t in n.targets))
    assert system == DEFAULT_SYSTEM
    from experiments.E5.check_harness import load_harness
    runner = load_harness("claude/harness")
    items = [r for r in read_jsonl(ROOT / "experiments/E5/dev.jsonl.gz") if r["payload"]["_audit"]["difficulty"] == "medium"][:2]
    monkeypatch.setattr(exporter, "read_jsonl", lambda _: items)
    for style in ("neutral", "audit"):
        out = tmp_path / style
        exporter.export(split="dev", difficulty="medium", instruction=style, cells="a,b,c,d,e", out=out)
        prompts = read_jsonl(out / "gpu/prompts.jsonl")
        labels = read_jsonl(out / "labels.jsonl")
        exp = runner.Experiment(id="E5", items=[runner.Item(**r) for r in items], judges=["offline"],
            conditions=[runner.Condition(c, lambda p, c=c: render_cell(p, c, style)) for c in "abcde"])
        expected = runner.build_prompts(exp, runner.plan_trials(exp, "dev"))
        assert [r["messages"][1]["content"] for r in prompts] == expected
        assert all(r["messages"][0] == {"role": "system", "content": system} for r in prompts)
        assert all(set(r) == {"key", "messages", "max_new_tokens"} for r in prompts)
        assert all(r["max_new_tokens"] == 400 for r in prompts)
        assert [r["key"] for r in prompts] == [r["key"] for r in labels]
        assert not (out / "gpu/labels.jsonl").exists()
        assert set(p.name for p in (out / "gpu").iterdir()) == {"job.json", "prompts.jsonl", "models.json", "preflight.py"}
        models = json.loads((out / "gpu/models.json").read_text())
        assert len(models) == 3 and all(m["max_model_len"] == 8192 for m in models)
        # No runner importing/executing a judge occurred.
        assert json.loads((out / "manifest.json").read_text())["model_calls"] == 0
        with pytest.raises(FileExistsError):
            exporter.export(split="dev", difficulty="medium", instruction=style, cells="a", out=out)


@pytest.mark.parametrize("experiment", ["E2", "E4"])
def test_native_exports_match_renderers(experiment, tmp_path, monkeypatch):
    items = load_frozen("dev", experiment)[:2]
    monkeypatch.setattr(other_exporter, "load_frozen", lambda *_: items)
    out = tmp_path / experiment
    other_exporter.export(experiment=experiment, split="dev", cells=None, out=out)
    prompts = read_jsonl(out / "gpu/prompts.jsonl")
    lookup = {r["id"]: r for r in items}
    for row in prompts:
        item, cell, instruction = row["key"].split("|")
        assert instruction == "harness"
        assert row["messages"][1]["content"] == render_other(lookup[item], cell)
    assert len(prompts) == 6


def test_e4_primary_and_e2_size_interaction_from_synthetic_outputs():
    for ex, cells in (("E4", ("prose_critique", "checked_countermodel", "dishonest_critic")),
                      ("E2", ("direct", "structured_fol", "ve"))):
        labels, outputs = [], []
        for item in load_frozen("dev", ex):
            for cell in cells:
                _, label = trial_rows(item, cell, "harness", "synthetic prompt", 400, ex)
                labels.append(label)
                approved = (cell == "prose_critique" if ex == "E4" else cell == "direct" and label["size"] == 256)
                outputs.append(reply(label, approved))
        result = analyze(labels, {"synthetic": outputs})
        primary = [r for r in result["contrasts"] if r["role"].startswith("primary")]
        assert primary and all(r["clusters"] == 4 for r in primary)
        if ex == "E4":
            assert primary[0]["estimate"] == -1 and primary[0]["pairs"] == 8
        else:
            direct = [r for r in primary if "direct" in r["contrast"]]
            fol = [r for r in primary if "structured_fol" in r["contrast"]]
            assert all(r["estimate"] == -1 for r in direct)
            assert all(r["estimate"] == 0 for r in fol)
            assert {r["workload"] for r in primary} == {"fixed", "growing"}


def test_cli_synthetic_outputs_and_missing_model(tmp_path):
    from experiments.colab_common import write_jsonl, write_json
    labels = fixture_labels()
    export = tmp_path / "export"
    (export / "gpu").mkdir(parents=True)
    write_jsonl(export / "labels.jsonl", labels)
    write_json(export / "gpu/models.json", [{"id": "synthetic"}, {"id": "missing"}])
    outputs = tmp_path / "out"
    (outputs / "synthetic").mkdir(parents=True)
    write_jsonl(outputs / "synthetic/outputs.jsonl", [reply(r) for r in labels])
    write_json(outputs / "synthetic/manifest.json", {"model": "synthetic"})
    command = ["python", str(ROOT / "experiments/E5/colab/score.py"), "--outputs", str(outputs), "--labels", str(export / "labels.jsonl")]
    run = subprocess.run(command, text=True, capture_output=True)
    assert run.returncode == 0, run.stderr
    result = json.loads((outputs / "score-summary.json").read_text())
    assert len(result["judges"]) == 2
    assert (outputs / "score-table.md").exists()
    assert len(read_jsonl(outputs / "scored-trials.jsonl")) == 2 * len(labels)


def test_moved_labels_retain_entirely_missing_judge_assignment(tmp_path):
    from experiments.colab_common import write_jsonl
    labels = fixture_labels()
    for row in labels:
        row["assigned_models"] = ["absent"]
    path = tmp_path / "labels.jsonl"
    write_jsonl(path, labels)
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    actual, provenance = discover_outputs(outputs, path)
    assert actual == {"absent": []}
    assert "No model outputs" in provenance["absent"]["error"]


def test_stale_gpu_prompt_hash_cannot_be_scored_as_new_materials(tmp_path):
    from experiments.colab_scoring import verify_input_binding
    from experiments.colab_common import write_json
    labels = [{"prompts_sha256": "new"}]
    write_json(tmp_path / "preflight-inputs.json", {"prompts_sha256": "old", "prompts": 1})
    with pytest.raises(ValueError, match="input hash/count"):
        verify_input_binding(tmp_path, labels)
    write_json(tmp_path / "preflight-inputs.json", {"prompts_sha256": "new", "prompts": 1})
    assert verify_input_binding(tmp_path, labels)["status"] == "verified"
