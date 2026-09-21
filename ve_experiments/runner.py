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

Scoring the `scored` split requires a committed experiments/<id>/PREREG.md whose bytes equal HEAD,
the real `ve` backend, and (if used) a committed split file. Run directories are never reused.
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
from .ve_iface import backend_name

LABELS = ("good", "bad")
SPLITS = ("dev", "scored")
# Plan v2 item 6. Each entry is a tuple of acceptable spellings; one must occur in a markdown heading
# that is followed by a non-empty body.
PREREG_REQUIRED_SECTIONS = (
    ("primary contrast",),
    ("refutation condition",),
    ("honest-acceptance constraint", "honest acceptance constraint"),
    ("smallest useful effect",),
    ("capability gate", "calibration gate", "capability and calibration gate"),
    ("sample size",),
)


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
    sample: int = 0

    def identity(self, experiment_id: str) -> str:
        return f"{experiment_id}|{self.split}|{self.item_id}|{self.condition}|{self.judge}|{self.sample}"


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
    split_file: Path | None = None  # if set, a scored run requires it to be committed and unmodified
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @property
    def dir(self) -> Path:
        return self.root / "experiments" / self.id


# --------------------------------------------------------------------------- splits


def _hash_split(group: str, dev_fraction: float, seed: int) -> str:
    """Each group is assigned on its own (hash below a threshold), so adding or removing other
    groups can never move it. The dev share is therefore approximate, not exact."""
    x = int(hashlib.sha256(f"{seed}:{group}".encode()).hexdigest()[:12], 16) / 16**12
    return "dev" if x < dev_fraction else "scored"


def assign_splits(items: Sequence[Item], dev_fraction: float, seed: int, split_file: Path | None = None) -> list[Item]:
    """Split by group and persist the assignment.

    With `split_file` (commit it), a group that already has an assignment keeps it for ever; new
    groups are appended; an item that arrives with a different explicit split is refused. Items may
    carry an explicit `split` (for designs that split by template or vocabulary family).
    """
    recorded: dict[str, str] = {}
    if split_file is not None and Path(split_file).exists():
        recorded = json.loads(Path(split_file).read_text(encoding="utf-8"))["groups"]
    assigned = dict(recorded)
    for it in items:
        want = it.split or assigned.get(it.group) or _hash_split(it.group, dev_fraction, seed)
        if assigned.setdefault(it.group, want) != want:
            raise DesignError(f"group {it.group} is recorded as {assigned[it.group]!r} and cannot move to {want!r}")
    if split_file is not None and assigned != recorded:
        Path(split_file).parent.mkdir(parents=True, exist_ok=True)
        body = {"seed": seed, "dev_fraction": dev_fraction, "groups": dict(sorted(assigned.items()))}
        Path(split_file).write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    return [_with_split(it, assigned[it.group]) for it in items]


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
            trials.append(Trial(it.id, it.group, it.label, it.split, cond, judge, exp.seed * 1000 + s, s))
    return trials


# --------------------------------------------------------------------------- preregistration


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def require_committed(path: Path, root: Path) -> dict[str, str]:
    """The file's working bytes must equal the blob committed at HEAD. Comparing bytes (not
    `git status`) means `git update-index --assume-unchanged` or skip-worktree cannot hide an edit."""
    path = Path(path)
    if not path.is_file():
        raise PreregistrationError(f"{path} does not exist; write and commit it before scoring")
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    blob = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"], capture_output=True)
    if blob.returncode != 0:
        raise PreregistrationError(f"{rel} is not committed at HEAD; commit it before scoring")
    if blob.stdout != path.read_bytes():
        raise PreregistrationError(f"{rel} differs from the committed version; commit it before scoring")
    commit = _git(root, "log", "-1", "--format=%H %cI", "--", rel).stdout.strip()
    return {"path": rel, "commit": commit, "blob": _git(root, "rev-parse", f"HEAD:{rel}").stdout.strip()}


def missing_prereg_sections(text: str) -> list[str]:
    sections: list[tuple[str, str]] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            sections.append((line.lstrip("# ").strip().lower(), ""))
        elif sections:
            sections[-1] = (sections[-1][0], sections[-1][1] + line.strip())
    missing = []
    for spellings in PREREG_REQUIRED_SECTIONS:
        if not any(any(sp in head for sp in spellings) and body for head, body in sections):
            missing.append(spellings[0])
    return missing


def require_prereg(exp_dir: Path, root: Path) -> dict[str, str]:
    """Refuse to score unless experiments/<id>/PREREG.md is committed, byte-identical to HEAD, and has
    a non-empty section for every Plan v2 field. The manifest records commit and blob."""
    info = require_committed(exp_dir / "PREREG.md", root)
    missing = missing_prereg_sections((exp_dir / "PREREG.md").read_text(encoding="utf-8"))
    if missing:
        raise PreregistrationError(f"{info['path']} lacks required non-empty sections: {missing}")
    return {"prereg_commit": info["commit"], "prereg_blob": info["blob"]}


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
        if exp.split_file is not None:
            manifest["split_file"] = require_committed(exp.split_file, exp.root)
        if backend_name() != "ve":
            raise PreregistrationError("scored runs require the real `ve` package, not the stub backend")
    manifest["ve_backend"] = backend_name()
    trials = plan_trials(exp, split)
    if limit is not None:
        trials = trials[:limit]
    prompts = build_prompts(exp, trials)
    approve, reject = exp.allowed_verdicts
    requests = [
        Request(model=t.judge, prompt=p, seed=t.seed, system=exp.system, tag=f"{exp.id}/{split}/{t.item_id}/{t.condition}",
                identity=t.identity(exp.id))
        for t, p in zip(trials, prompts)
    ]
    run_dir = allocate_run_dir(out_dir, exp.dir / "runs", split)  # before any call, so a clash costs nothing
    results = client.map(requests)
    with open(run_dir / "trials.jsonl", "x", encoding="utf-8") as fh:
        for t, p, r in zip(trials, prompts, results):
            row = asdict(t)
            row.update(
                prompt_sha=hashlib.sha256(p.encode()).hexdigest()[:16], llm_key=r.key, ok=r.ok, error=r.error,
                latency_s=r.latency_s, input_tokens=r.input_tokens, output_tokens=r.output_tokens,
                from_cache=r.from_cache, reply=r.text, tool_events=list(r.tool_events),
            )  # fmt: skip
            if r.tool_events:
                # The judge ran a command or tool: it may have read ground truth. Invalid, scored worst case.
                row.update(verdict=None, approved=None, parse_error="invalid: judge used tools")
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                continue
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
        n_tool_use_trials=sum(bool(r.tool_events) for r in results),
        git_head=_git(exp.root, "rev-parse", "HEAD").stdout.strip(),
        git_dirty=bool(_git(exp.root, "status", "--porcelain", "--untracked-files=no").stdout.strip()),
    )
    with open(run_dir / "manifest.json", "x", encoding="utf-8") as fh:
        fh.write(json.dumps(manifest, indent=2) + "\n")
    return run_dir


def allocate_run_dir(out_dir: Path | None, runs: Path, split: str) -> Path:
    """Create a fresh run directory atomically. Never reuses or overwrites an existing one."""
    if out_dir is not None:
        try:
            Path(out_dir).mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise DesignError(f"run directory {out_dir} already exists; results are never overwritten") from exc
        return Path(out_dir)
    runs.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for n in range(1, 10_000):
        candidate = runs / f"{split}-{stamp}-{n:03d}"
        try:
            candidate.mkdir(exist_ok=False)
            return candidate
        except FileExistsError:
            continue
    raise DesignError("could not allocate a run directory")


def load_trials(run_dir: Path) -> list[dict]:
    return [json.loads(line) for line in (Path(run_dir) / "trials.jsonl").read_text(encoding="utf-8").splitlines()]
