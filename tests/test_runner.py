import json
import subprocess

import pytest

from ve_experiments.llm import LLMClient, RawReply
from ve_experiments.runner import (
    Condition, DesignError, Experiment, Item, PreregistrationError, assign_splits, check_design, load_trials,
    plan_trials, require_prereg, run,
)  # fmt: skip

PREREG = ("Status: FROZEN\n# E\n## Primary contrast\nx\n## Refutation condition\nx\n## Honest-acceptance constraint\nx\n"
          "## Smallest useful effect\nx\n## Capability gate and calibration gate\nx\n## Sample size\nx\n")


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README").write_text("x")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "init")
    return tmp_path


def make_items(n=20):
    items = []
    for g in range(n):
        for label in ("good", "bad"):
            items.append(Item(id=f"item{g:03d}-{label}", label=label, group=f"g{g:03d}",
                              payload={"text": f"formula {g} {'ok' if label == 'good' else 'weak'}", "_attack": "swap"}))  # fmt: skip
    return items


def make_exp(root, assignment="crossed", samples=1):
    conds = [Condition("fol", lambda p: f"FOL view: {p['text']}"), Condition("ve", lambda p: f"VE view: {p['text']}")]
    split_file = root / "experiments" / "EX" / "splits.json"
    return Experiment("EX", assign_splits(make_items(), 0.25, seed=1, split_file=split_file), conds, ["judge-a", "judge-b"],
                      assignment=assignment, samples=samples, root=root, split_file=split_file)  # fmt: skip


def backend(model, system, prompt, timeout_s, cwd):
    # approves everything in the FOL view; in the VE view rejects weakened items
    v = "reject" if ("VE view" in prompt and "weak" in prompt) else "approve"
    if "formula 7 " in prompt and model == "judge-b":
        return RawReply("I cannot decide.")
    return RawReply(f'ok\n{{"verdict": "{v}"}}')


def test_splits_are_disjoint_by_group_and_deterministic():
    items = assign_splits(make_items(), 0.25, seed=1)
    dev = {i.group for i in items if i.split == "dev"}
    scored = {i.group for i in items if i.split == "scored"}
    assert dev and scored and len(dev) + len(scored) == 20 and not dev & scored
    again = assign_splits(list(reversed(make_items())), 0.25, seed=1)
    assert {i.id: i.split for i in items} == {i.id: i.split for i in again}
    assert {i.id: i.split for i in items} != {i.id: i.split for i in assign_splits(make_items(), 0.25, seed=2)}


def test_design_rejects_group_in_both_splits(tmp_path):
    exp = make_exp(tmp_path)
    first = exp.items[0]
    exp.items = [Item(first.id, first.label, first.payload, first.group, "dev" if first.split == "scored" else "scored"), *exp.items[1:]]
    with pytest.raises(DesignError, match="both dev and scored"):
        check_design(exp)


def test_crossed_assignment_is_fully_paired(tmp_path):
    exp = make_exp(tmp_path, samples=2)
    trials = plan_trials(exp, "scored")
    n = len({i.group for i in exp.items if i.split == 'scored'})
    assert len(trials) == n * 2 * 2 * 2 * 2
    assert all(t.split == "scored" for t in trials)
    cells = {(t.item_id, t.condition, t.judge, t.seed) for t in trials}
    assert len(cells) == len(trials)
    assert not {t.item_id for t in trials} & {t.item_id for t in plan_trials(exp, "dev")}


def test_rotated_assignment_is_balanced_and_keeps_groups_together(tmp_path):
    exp = make_exp(tmp_path, assignment="rotated")
    trials = plan_trials(exp, "scored")
    n = len({i.group for i in exp.items if i.split == 'scored'})
    assert len(trials) == n * 2 * 2
    by = {}
    for t in trials:
        by.setdefault((t.group, t.judge), set()).add(t.condition)
    assert all(len(v) == 1 for v in by.values())  # good and bad variant share a condition per judge
    counts = [sum(1 for t in trials if t.condition == c and t.judge == "judge-a") for c in ("fol", "ve")]
    assert abs(counts[0] - counts[1]) <= 2


def test_scored_run_refused_without_committed_prereg(repo):
    exp = make_exp(repo)
    client = LLMClient(cache_dir=repo / ".c", backend=backend)
    with pytest.raises(PreregistrationError, match="does not exist"):
        run(exp, client, "scored")
    exp.dir.mkdir(parents=True, exist_ok=True)
    (exp.dir / "PREREG.md").write_text(PREREG)
    with pytest.raises(PreregistrationError, match="not committed"):
        run(exp, client, "scored")
    git(repo, "add", "experiments")
    git(repo, "commit", "-qm", "prereg")
    (exp.dir / "PREREG.md").write_text(PREREG + "edited after the fact\n")
    with pytest.raises(PreregistrationError, match="differs from the committed"):
        run(exp, client, "scored")
    (exp.dir / "PREREG.md").write_text("Status: FROZEN\n# nothing\n")
    git(repo, "commit", "-qam", "gut prereg")
    with pytest.raises(PreregistrationError, match="lacks required"):
        require_prereg(exp.dir, repo)
    (exp.dir / "PREREG.md").write_text(PREREG.replace("Status: FROZEN", "Status: DRAFT for review"))
    git(repo, "commit", "-qam", "draft prereg")
    with pytest.raises(PreregistrationError, match="not frozen"):
        run(exp, client, "scored")


def test_scored_run_refuses_an_item_the_committed_split_file_records_as_dev(repo):
    exp = make_exp(repo)
    (exp.dir / "PREREG.md").write_text(PREREG)
    git(repo, "add", "experiments")
    git(repo, "commit", "-qm", "prereg and splits")
    client = LLMClient(cache_dir=repo / ".c", backend=backend)
    dev_item = next(i for i in exp.items if i.split == "dev")
    smuggled = [Item(i.id, i.label, i.payload, i.group, "scored") if i.group == dev_item.group else i for i in exp.items]
    exp.items = smuggled
    with pytest.raises(PreregistrationError, match="not recorded as scored"):
        run(exp, client, "scored")
    exp.split_file = None
    with pytest.raises(PreregistrationError, match="requires a committed split file"):
        run(exp, client, "scored")


def test_row_fields_and_scorer_reach_the_trial_rows(repo):
    exp = make_exp(repo)
    exp.row_fields = ("attack",)
    exp.score = lambda item, verdict: {"n_chars": len(item.payload["text"]), "said": verdict}
    rows = load_trials(run(exp, LLMClient(cache_dir=repo / ".c", backend=backend), "dev"))
    assert all(r["attack"] == "swap" and r["n_chars"] > 0 for r in rows)
    assert {r["said"] for r in rows} <= {"approve", "reject", None}


def test_dev_run_needs_no_prereg_and_scored_run_records_it(repo):
    exp = make_exp(repo)
    client = LLMClient(cache_dir=repo / ".c", backend=backend)
    dev_dir = run(exp, client, "dev", out_dir=repo / "out-dev")
    n_dev = len({i.group for i in exp.items if i.split == 'dev'})
    assert len(load_trials(dev_dir)) == n_dev * 2 * 2 * 2
    exp.dir.mkdir(parents=True, exist_ok=True)
    (exp.dir / "PREREG.md").write_text(PREREG)
    git(repo, "add", "experiments")
    git(repo, "commit", "-qm", "prereg")
    with pytest.raises(PreregistrationError, match="truncated"):
        run(exp, client, "scored", limit=3)
    out = run(exp, client, "scored", out_dir=repo / "out")
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["prereg_commit"] and manifest["prereg_blob"] and manifest["n_trials"] == (20 - n_dev) * 8
    assert manifest["ve_backend"] == "ve"
    rows = load_trials(out)
    assert {r["split"] for r in rows} == {"scored"}
    bad_ve = [r for r in rows if r["label"] == "bad" and r["condition"] == "ve" and r["parse_error"] is None]
    assert bad_ve and all(r["approved"] is False for r in bad_ve)
    # unparseable replies are kept, with approved=None
    failed = [r for r in rows if r["parse_error"]]
    assert all(r["approved"] is None and r["judge"] == "judge-b" for r in failed)


def test_prompt_never_sees_label_id_or_hidden_fields(tmp_path):
    seen = []
    exp = make_exp(tmp_path)
    exp.conditions = [Condition("spy", lambda p: seen.append(dict(p)) or "prompt")]
    from ve_experiments.runner import build_prompts

    build_prompts(exp, plan_trials(exp, "dev"))
    assert seen and all(set(p) == {"text"} for p in seen)
    exp.conditions = [Condition("leak", lambda p: "about item000-good")]
    leaky = [t for s in ("dev", "scored") for t in plan_trials(exp, s) if t.item_id == "item000-good"]
    with pytest.raises(DesignError, match="item id"):
        build_prompts(exp, leaky)


def test_prereg_edit_hidden_by_assume_unchanged_is_caught(repo):
    exp = make_exp(repo)
    exp.dir.mkdir(parents=True, exist_ok=True)
    (exp.dir / "PREREG.md").write_text(PREREG)
    git(repo, "add", "experiments")
    git(repo, "commit", "-qm", "prereg")
    git(repo, "update-index", "--assume-unchanged", "experiments/EX/PREREG.md")
    (exp.dir / "PREREG.md").write_text(PREREG.replace("x", "y"))
    with pytest.raises(PreregistrationError, match="differs from the committed"):
        require_prereg(exp.dir, repo)


def test_prereg_needs_every_plan_v2_section_with_a_body(repo):
    from ve_experiments.runner import missing_prereg_sections

    assert missing_prereg_sections(PREREG) == []
    old = "# E\n## Primary metric\nx\n## Primary contrast\nx\n## Refutation condition\nx\n## Sample size\nx\n"
    assert missing_prereg_sections(old) == ["honest-acceptance constraint", "smallest useful effect", "capability gate"]
    assert "smallest useful effect" in missing_prereg_sections(PREREG.replace("## Smallest useful effect\nx\n", "## Smallest useful effect\n"))


def test_identical_prompts_in_distinct_trials_are_distinct_calls(tmp_path):
    # Reviewer's reproduction: 2 items x 2 conditions x 2 samples with one shared prompt must make 8 calls, not 2.
    calls = []

    def be(model, system, prompt, timeout_s, cwd):
        calls.append(prompt)
        return RawReply('{"verdict": "approve"}')

    items = [Item(f"same{i}-good", "good", {"text": "identical"}, split="dev") for i in range(2)]
    conds = [Condition("a", lambda p: "the same prompt"), Condition("b", lambda p: "the same prompt")]
    exp = Experiment("EX", items, conds, ["judge-a"], samples=2, root=tmp_path)
    client = LLMClient(cache_dir=tmp_path / ".c", backend=be)
    rows = load_trials(run(exp, client, "dev", out_dir=tmp_path / "o1"))
    assert len(rows) == 8 and len(calls) == 8 and len({r["llm_key"] for r in rows}) == 8
    assert all("same0" not in c for c in calls)  # the identity is in the key, never in the prompt
    run(exp, client, "dev", out_dir=tmp_path / "o2")
    assert len(calls) == 8  # a rerun replays every trial from the cache


def test_persisted_split_never_moves_a_group(tmp_path):
    # Reviewer's reproduction: g0..g3, then append g16.
    f = tmp_path / "splits.json"
    mk = lambda names: [Item(f"{g}-good", "good", {}, group=g) for g in names]  # noqa: E731
    first = {i.group: i.split for i in assign_splits(mk(["g0", "g1", "g2", "g3"]), 0.5, 0, f)}
    second = {i.group: i.split for i in assign_splits(mk(["g0", "g1", "g2", "g3", "g16"]), 0.5, 0, f)}
    assert all(second[g] == s for g, s in first.items())
    # without the file the hash split is still independent per group
    third = {i.group: i.split for i in assign_splits(mk(["g16", "g3", "g0"]), 0.5, 0)}
    assert all(second[g] == s for g, s in third.items())
    moved = [Item("g0-good", "good", {}, group="g0", split="dev" if first["g0"] == "scored" else "scored")]
    with pytest.raises(DesignError, match="cannot move"):
        assign_splits(moved, 0.5, 0, f)


def test_run_directories_are_never_reused(tmp_path, monkeypatch):
    import time as _time

    exp = make_exp(tmp_path)
    client = LLMClient(cache_dir=tmp_path / ".c", backend=backend)
    monkeypatch.setattr(_time, "strftime", lambda *a: "20260921-000000")
    d1, d2 = run(exp, client, "dev"), run(exp, client, "dev")
    assert d1 != d2 and (d1 / "trials.jsonl").exists() and (d2 / "trials.jsonl").exists()
    with pytest.raises(DesignError, match="never overwritten"):
        run(exp, client, "dev", out_dir=d1)


def test_trial_in_which_the_judge_used_a_tool_is_invalid(tmp_path):
    def be(model, system, prompt, timeout_s, cwd):
        events = ("codex:command_execution:cat items.jsonl",) if "formula 3 " in prompt else ()
        return RawReply('{"verdict": "reject"}', tool_events=events)

    exp = make_exp(tmp_path)
    exp.items = [Item(i.id, i.label, i.payload, i.group, "dev") for i in exp.items]
    rows = load_trials(run(exp, LLMClient(cache_dir=tmp_path / ".c", backend=be), "dev", out_dir=tmp_path / "o"))
    tainted = [r for r in rows if r["tool_events"]]
    assert tainted and all(r["approved"] is None and "tools" in r["parse_error"] for r in tainted)
    from ve_experiments.stats import rate

    bad = [r for r in tainted if r["label"] == "bad"]
    assert rate(bad, "false_approval", bad[0]["condition"]).value == 1.0  # worst case, although the reply said reject


def test_scored_run_refuses_the_stub_backend(repo, monkeypatch):
    import ve_experiments.runner as R

    exp = make_exp(repo)
    exp.dir.mkdir(parents=True, exist_ok=True)
    (exp.dir / "PREREG.md").write_text(PREREG)
    git(repo, "add", "experiments")
    git(repo, "commit", "-qm", "prereg")
    monkeypatch.setattr(R, "backend_name", lambda: "stub")
    with pytest.raises(PreregistrationError, match="stub"):
        run(exp, LLMClient(cache_dir=repo / ".c", backend=backend), "scored")


def test_truncated_or_failed_replies_are_never_parsed(repo):
    from ve_experiments.llm import RawReply as RR

    def cut(model, system, prompt, timeout_s, cwd):
        # a reply that was cut at the token limit but happens to end in a valid verdict
        return RR('...{"verdict": "reject"}', finish_reason="length")

    exp = make_exp(repo)
    exp.score = lambda item, verdict: {"said": verdict}
    rows = load_trials(run(exp, LLMClient(cache_dir=repo / ".c", backend=cut), "dev"))
    assert rows and all(r["truncated"] and r["verdict"] is None and r["approved"] is None and r["said"] is None for r in rows)
    assert all("truncated" in r["parse_error"] for r in rows)
    from ve_experiments.stats import rate

    assert rate(rows, "false_approval", "ve", "judge-a").value == 1.0  # worst case, although the text says reject
