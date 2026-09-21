import json

import pytest

from test_runner import PREREG, backend, git, make_items, repo  # noqa: F401

from ve_experiments.colab import FakeJobRunner, experiment_requests, export_job, import_outputs
from ve_experiments.llm import DEFAULT_SYSTEM, LLMClient
from ve_experiments.runner import Condition, DesignError, Experiment, PreregistrationError, assign_splits, load_trials, run
from ve_experiments.stats import rate

A, B = "vllm:org/model-a", "vllm:org/model-b"
SPECS = [{"id": "org/model-a"}, {"id": "org/model-b", "max_model_len": 1536}]


def make_exp(root, judges=(A, B, "judge-a")):
    conds = [Condition("fol", lambda p: f"FOL view: {p['text']}"), Condition("ve", lambda p: f"VE view: {p['text']}")]
    split_file = root / "experiments" / "EX" / "splits.json"
    return Experiment("EX", assign_splits(make_items(), 0.25, seed=1, split_file=split_file), conds, list(judges), root=root,
                      split_file=split_file)


def fake_reply(model, row):
    system, user = (m["content"] for m in row["messages"])
    assert system == DEFAULT_SYSTEM and [m["role"] for m in row["messages"]] == ["system", "user"]
    assert row["max_new_tokens"] == 400
    if model == "org/model-b" and "formula 3 " in user:
        return "Let me think about this for a very long", "length"  # truncated: unparseable, worst case
    if model == "org/model-b" and "formula 5 " in user:
        return "", "stop"  # empty reply: a failed call
    verdict = "reject" if ("VE view" in user and "weak" in user) else "approve"
    return f'fine\n{{"verdict": "{verdict}"}}', "stop"


def test_batch_judges_go_through_the_same_trial_records(repo, tmp_path):  # noqa: F811
    exp = make_exp(repo)
    client = LLMClient(cache_dir=tmp_path / "cache", backend=None)
    reqs = experiment_requests(exp, "dev", client)
    info = export_job(tmp_path / "job", "job-1", reqs, SPECS, max_new_tokens=400)
    n_dev = sum(i.split == "dev" for i in exp.items)
    assert info["n_prompts"] == n_dev * 2 and len(reqs) == n_dev * 2 * 2  # one prompt row serves both batch judges
    rows = [json.loads(x) for x in (tmp_path / "job" / "prompts.jsonl").read_text().splitlines()]
    assert all("vllm" not in r["key"] and "good" not in json.dumps(r["messages"]) for r in rows)  # no judge, no label
    results = FakeJobRunner(fake_reply)(tmp_path / "job", tmp_path / "results")
    counts = import_outputs(client, reqs, results)
    assert counts[A]["truncated"] == 0 and counts[A]["empty"] == 0 and counts[A]["missing"] == 0

    exp_batch = make_exp(repo, judges=(A, B))
    trials = load_trials(run(exp_batch, LLMClient(cache_dir=tmp_path / "cache"), "dev"))
    assert len(trials) == len(reqs) and all(t["from_cache"] for t in trials)
    a_ve = rate(trials, "false_approval", "ve", A)
    a_fol = rate(trials, "false_approval", "fol", A)
    assert a_ve.value == 0.0 and a_fol.value == 1.0
    dev_groups = sorted({i.group for i in exp.items if i.split == "dev"})
    cut = [t for t in trials if t["judge"] == B and t["truncated"]]
    assert ("g003" in dev_groups) == bool(cut)
    for t in cut:
        assert t["approved"] is None and t["parse_error"] and t["finish_reason"] == "length"
    empty = [t for t in trials if t["judge"] == B and not t["ok"]]
    assert ("g005" in dev_groups) == bool(empty) and all(t["error"] == "empty reply" for t in empty)
    # worst case: a truncated or empty reply on a bad item counts as approved, even in the VE view
    n_lost_bad = sum(t["label"] == "bad" and t["condition"] == "ve" for t in cut + empty)
    assert rate(trials, "false_approval", "ve", B).numerator == n_lost_bad


def test_a_trial_that_was_not_imported_fails_and_is_never_called(repo, tmp_path):  # noqa: F811
    exp = make_exp(repo, judges=(A,))
    trials = load_trials(run(exp, LLMClient(cache_dir=tmp_path / "cache", backoff_s=0), "dev"))
    assert trials and all(not t["ok"] and t["approved"] is None and "not imported" in t["error"] for t in trials)
    assert rate(trials, "false_approval", "ve", A).value == 1.0


def test_incomplete_or_foreign_outputs_are_refused(repo, tmp_path):  # noqa: F811
    exp = make_exp(repo, judges=(A, B))
    client = LLMClient(cache_dir=tmp_path / "cache")
    reqs = experiment_requests(exp, "dev", client)
    export_job(tmp_path / "job", "job-2", reqs, SPECS, max_new_tokens=400)
    results = FakeJobRunner(fake_reply)(tmp_path / "job", tmp_path / "results")
    out = results / "out" / "org--model-a" / "outputs.jsonl"
    lines = out.read_text().splitlines()
    out.write_text("\n".join(lines[1:]) + "\n")
    with pytest.raises(DesignError, match="have no output"):
        import_outputs(client, reqs, results)
    assert import_outputs(client, reqs, results, allow_missing=True)[A]["missing"] == 1
    out.write_text("\n".join(lines + [json.dumps({"key": "EX|dev|other|fol|0", "text": "x", "finish_reason": "stop"})]) + "\n")
    with pytest.raises(DesignError, match="never exported"):
        import_outputs(client, reqs, results)
    with pytest.raises(DesignError, match="do not match"):
        export_job(tmp_path / "job3", "job-3", reqs, SPECS[:1], max_new_tokens=400)


def test_exporting_the_scored_split_needs_the_committed_prereg(repo, tmp_path):  # noqa: F811
    exp = make_exp(repo, judges=(A,))
    client = LLMClient(cache_dir=tmp_path / "cache")
    with pytest.raises(PreregistrationError):
        experiment_requests(exp, "scored", client)
    (repo / "experiments" / "EX").mkdir(parents=True, exist_ok=True)
    (repo / "experiments" / "EX" / "PREREG.md").write_text(PREREG)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "prereg")
    assert experiment_requests(exp, "scored", client)


def test_a_rerun_exports_only_trials_that_are_not_cached(repo, tmp_path):  # noqa: F811
    from ve_experiments.colab import uncached

    exp = make_exp(repo, judges=(A, B))
    client = LLMClient(cache_dir=tmp_path / "cache")
    reqs = experiment_requests(exp, "dev", client)
    fol = [kr for kr in reqs if "|fol|" in kr.key]
    export_job(tmp_path / "job", "job-4", fol, SPECS, max_new_tokens=400)
    import_outputs(client, fol, FakeJobRunner(fake_reply)(tmp_path / "job", tmp_path / "results"))
    left = uncached(client, reqs)
    assert left and all("|ve|" in kr.key for kr in left) and len(left) == len(reqs) - len(fol)
