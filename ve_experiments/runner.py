"""Generic runner for "items x conditions x judges" experiments.

Concepts
--------
Item        one thing a judge approves or rejects. `label` is the ground truth ("good" should be
            approved, "bad" should be rejected); it comes from the checker or from construction.
            `group` ties variants of one base item together (a faithful and a weakened version of
            the same requirement): a group never straddles the dev/scored split, and the bootstrap
            in stats.py resamples groups.
Condition   a named function from the judge-visible payload to a prompt. It never receives the
            label, the item id, or payload keys starting with "_" (hidden metadata).
Judge       a model id.

Assignment is paired: by default every item is shown in every condition to every judge ("crossed";
model judges are stateless, so there is no carry-over). With a tight budget, "rotated" gives each
(group, judge) exactly one condition, balanced by a seeded Latin rotation; contrasts are then
between groups and need more items.

Scoring the `scored` split requires a committed, unmodified experiments/<id>/PREREG.md.
"""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .llm import LLMClient, Request, VerdictParseError, parse_verdict

LABELS = ("good", "bad")
SPLITS = ("dev", "scored")
PREREG_REQUIRED_HEADINGS = ("primary metric", "primary contrast", "refutation condition", "sample size")


class PreregistrationError(RuntimeError):
    pass


class DesignError(ValueError):
    pass


@dataclass(frozen=True)
class Item:
    id: str
    label: str  # "good" | "bad"
    payload: Mapping[str, Any]
    group: str = ""  # defaults to id
    split: str = ""  # "dev" | "scored"; filled by assign_splits

    def __post_init__(self) -> None:
        if self.label not in LABELS:
            raise DesignError(f"item {self.id}: label must be one of {LABELS}")
        if not self.group:
            object.__setattr__(self, "group", self.id)

    def visible(self) -> dict[str, Any]:
        return {k: v for k, v in self.payload.items() if not k.startswith("_")}


@dataclass(frozen=True)
class Condition:
    name: str
    build_prompt: Callable[[Mapping[str, Any]], str]


@dataclass(frozen=True)
class Trial:
    item_id: str
    group: str
    label: str
    split: str
    condition: str
    judge: str
    seed: int


@dataclass
class Experiment:
    id: str
    items: Sequence[Item]
    conditions: Sequence[Condition]
    judges: Sequence[str]
    assignment: str = "crossed"  # or "rotated"
    samples: int = 1  # independent samples (seeds) per trial cell
    seed: int = 0
    allowed_verdicts: tuple[str, str] = ("approve", "reject")  # (approve word, reject word)
    system: str | None = None
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @property
    def dir(self) -> Path:
        return self.root / "experiments" / self.id


# --------------------------------------------------------------------------- splits


def assign_splits(items: Sequence[Item], dev_fraction: float, seed: int) -> list[Item]:
    """Deterministic split by group. Sorting groups by a seeded hash makes the split independent of
    item order and stable when items are added."""
    groups = sorted({it.group for it in items}, key=lambda g: hashlib.sha256(f"{seed}:{g}".encode()).hexdigest())
    n_dev = round(len(groups) * dev_fraction)
    dev = set(groups[:n_dev])
    return [_with_split(it, "dev" if it.group in dev else "scored") for it in items]


def _with_split(item: Item, split: str) -> Item:
    return Item(id=item.id, label=item.label, payload=item.payload, group=item.group, split=split)


def check_design(exp: Experiment) -> None:
    ids = [it.id for it in exp.items]
    if len(set(ids)) != len(ids):
        raise DesignError("duplicate item ids")
    if len({c.name for c in exp.conditions}) != len(exp.conditions):
        raise DesignError("duplicate condition names")
    if len(set(exp.judges)) != len(exp.judges):
        raise DesignError("duplicate judges")
    split_of_group: dict[str, str] = {}
    for it in exp.items:
        if it.split not in SPLITS:
            raise DesignError(f"item {it.id} has no split; call assign_splits first")
        if split_of_group.setdefault(it.group, it.split) != it.split:
            raise DesignError(f"group {it.group} appears in both dev and scored splits")
    if exp.assignment not in ("crossed", "rotated"):
        raise DesignError(f"unknown assignment {exp.assignment!r}")


# --------------------------------------------------------------------------- assignment


def plan_trials(exp: Experiment, split: str) -> list[Trial]:
    check_design(exp)
    items = [it for it in exp.items if it.split == split]
    names = [c.name for c in exp.conditions]
    trials: list[Trial] = []
    if exp.assignment == "crossed":
        cells = [(it, c, j) for it in items for c in names for j in exp.judges]
    else:
        groups = sorted({it.group for it in items})
        random.Random(f"{exp.seed}:{split}:rotate").shuffle(groups)
        offset = {g: i for i, g in enumerate(groups)}
        cells = [
            (it, names[(offset[it.group] + ji) % len(names)], j)
            for it in items
            for ji, j in enumerate(exp.judges)
        ]
    for it, cond, judge in cells:
        for s in range(exp.samples):
            trials.append(Trial(it.id, it.group, it.label, it.split, cond, judge, exp.seed * 1000 + s))
    return trials


# --------------------------------------------------------------------------- preregistration


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def require_prereg(exp_dir: Path, root: Path) -> dict[str, str]:
    """Refuse to score unless experiments/<id>/PREREG.md is committed and unmodified.

    Returns the commit and blob hash, which the run manifest records, so that a reader can verify
    the preregistration predates the scored run.
    """
    path = exp_dir / "PREREG.md"
    if not path.is_file():
        raise PreregistrationError(f"{path} does not exist; write and commit it before scoring")
    rel = str(path.resolve().relative_to(root.resolve()))
    if _git(root, "ls-files", "--error-unmatch", rel).returncode != 0:
        raise PreregistrationError(f"{rel} is not tracked by git; commit it before scoring")
    if _git(root, "status", "--porcelain", "--", rel).stdout.strip():
        raise PreregistrationError(f"{rel} has uncommitted changes; commit them before scoring")
    text = path.read_text(encoding="utf-8").lower()
    missing = [h for h in PREREG_REQUIRED_HEADINGS if h not in text]
    if missing:
        raise PreregistrationError(f"{rel} lacks required sections: {missing}")
    commit = _git(root, "log", "-1", "--format=%H %cI", "--", rel).stdout.strip()
    blob = _git(root, "rev-parse", f"HEAD:{rel}").stdout.strip()
    return {"prereg_commit": commit, "prereg_blob": blob}


# --------------------------------------------------------------------------- running


def build_prompts(exp: Experiment, trials: Sequence[Trial]) -> list[str]:
    items = {it.id: it for it in exp.items}
    conds = {c.name: c for c in exp.conditions}
    prompts = []
    for t in trials:
        item = items[t.item_id]
        prompt = conds[t.condition].build_prompt(item.visible())
        if len(item.id) >= 4 and item.id in prompt:
            raise DesignError(f"prompt for {item.id}/{t.condition} contains the item id (possible label leak)")
        prompts.append(prompt)
    return prompts


def run(exp: Experiment, client: LLMClient, split: str, out_dir: Path | None = None, limit: int | None = None) -> Path:
    """Run one split and write trials.jsonl and manifest.json. Returns the run directory."""
    if split not in SPLITS:
        raise DesignError(f"split must be one of {SPLITS}")
    manifest: dict[str, Any] = {"experiment": exp.id, "split": split, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    if split == "scored":
        if limit is not None:
            raise PreregistrationError("a scored run cannot be truncated with `limit`")
        manifest.update(require_prereg(exp.dir, exp.root))
    trials = plan_trials(exp, split)
    if limit is not None:
        trials = trials[:limit]
    prompts = build_prompts(exp, trials)
    approve, reject = exp.allowed_verdicts
    requests = [
        Request(model=t.judge, prompt=p, seed=t.seed, system=exp.system, tag=f"{exp.id}/{split}/{t.item_id}/{t.condition}")
        for t, p in zip(trials, prompts)
    ]
    results = client.map(requests)

    run_dir = out_dir or exp.dir / "runs" / f"{split}-{time.strftime('%Y%m%d-%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "trials.jsonl", "w", encoding="utf-8") as fh:
        for t, p, r in zip(trials, prompts, results):
            row = asdict(t)
            row.update(
                prompt_sha=hashlib.sha256(p.encode()).hexdigest()[:16], llm_key=r.key, ok=r.ok, error=r.error,
                latency_s=r.latency_s, input_tokens=r.input_tokens, output_tokens=r.output_tokens,
                from_cache=r.from_cache, reply=r.text,
            )  # fmt: skip
            try:
                verdict = parse_verdict(r.text, allowed=exp.allowed_verdicts)
                row.update(verdict=verdict.value, approved=verdict.value == approve, parse_error=None)
            except VerdictParseError as exc:
                row.update(verdict=None, approved=None, parse_error=str(exc))
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    manifest.update(
        finished=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        n_trials=len(trials),
        n_items=len({t.item_id for t in trials}),
        conditions=[c.name for c in exp.conditions],
        judges=list(exp.judges),
        assignment=exp.assignment,
        samples=exp.samples,
        seed=exp.seed,
        n_failed_calls=sum(not r.ok for r in results),
        git_head=_git(exp.root, "rev-parse", "HEAD").stdout.strip(),
        git_dirty=bool(_git(exp.root, "status", "--porcelain", "--untracked-files=no").stdout.strip()),
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return run_dir


def load_trials(run_dir: Path) -> list[dict]:
    return [json.loads(line) for line in (Path(run_dir) / "trials.jsonl").read_text(encoding="utf-8").splitlines()]
