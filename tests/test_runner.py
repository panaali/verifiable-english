import json
import subprocess

import pytest

from ve_experiments.llm import LLMClient, RawReply
from ve_experiments.runner import (
    Condition, DesignError, Experiment, Item, PreregistrationError, assign_splits, check_design, load_trials,
    plan_trials, require_prereg, run,
)  # fmt: skip

PREREG = "# E\n## Primary metric\nx\n## Primary contrast\nx\n## Refutation condition\nx\n## Sample size\nx\n"


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
    return Experiment("EX", assign_splits(make_items(), 0.25, seed=1), conds, ["judge-a", "judge-b"],
                      assignment=assignment, samples=samples, root=root)  # fmt: skip


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
    assert len(dev) == 5 and len(scored) == 15 and not dev & scored
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
    assert len(trials) == 15 * 2 * 2 * 2 * 2
    assert all(t.split == "scored" for t in trials)
    cells = {(t.item_id, t.condition, t.judge, t.seed) for t in trials}
    assert len(cells) == len(trials)
    assert not {t.item_id for t in trials} & {t.item_id for t in plan_trials(exp, "dev")}


def test_rotated_assignment_is_balanced_and_keeps_groups_together(tmp_path):
    exp = make_exp(tmp_path, assignment="rotated")
    trials = plan_trials(exp, "scored")
    assert len(trials) == 15 * 2 * 2
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
    exp.dir.mkdir(parents=True)
    (exp.dir / "PREREG.md").write_text(PREREG)
    with pytest.raises(PreregistrationError, match="not tracked"):
        run(exp, client, "scored")
    git(repo, "add", "experiments")
    git(repo, "commit", "-qm", "prereg")
    (exp.dir / "PREREG.md").write_text(PREREG + "edited after the fact\n")
    with pytest.raises(PreregistrationError, match="uncommitted"):
        run(exp, client, "scored")
    (exp.dir / "PREREG.md").write_text("# nothing\n")
    git(repo, "commit", "-qam", "gut prereg")
    with pytest.raises(PreregistrationError, match="lacks required"):
        require_prereg(exp.dir, repo)


def test_dev_run_needs_no_prereg_and_scored_run_records_it(repo):
    exp = make_exp(repo)
    client = LLMClient(cache_dir=repo / ".c", backend=backend)
    dev_dir = run(exp, client, "dev", out_dir=repo / "out-dev")
    assert len(load_trials(dev_dir)) == 5 * 2 * 2 * 2
    exp.dir.mkdir(parents=True, exist_ok=True)
    (exp.dir / "PREREG.md").write_text(PREREG)
    git(repo, "add", "experiments")
    git(repo, "commit", "-qm", "prereg")
    with pytest.raises(PreregistrationError, match="truncated"):
        run(exp, client, "scored", limit=3)
    out = run(exp, client, "scored", out_dir=repo / "out")
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["prereg_commit"] and manifest["prereg_blob"] and manifest["n_trials"] == 120
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
