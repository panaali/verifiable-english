"""Batch backend for open-weight judges (vLLM on a Colab GPU), producing the same trial records as hosted judges.

A judge named `vllm:<hugging face id>` is never called live. Instead:

  1. `export_job`     writes a job directory: prompts.jsonl (one row per DISTINCT judge-free trial key, with the
                      same system and user text a hosted judge receives, as chat messages), models.json, job.json.
                      One job serves every vllm judge of the split, because they all see identical prompts.
  2. a `JobRunner`    submits the job, waits, fetches `out/<model slug>/outputs.jsonl` (`ColabJobRunner`), or
                      fabricates outputs in tests (`FakeJobRunner`).
  3. `import_outputs` stores every reply in the LLM cache under the key a live call of that trial would have
                      (model, system, prompt, seed, trial identity), with `finish_reason`.
  4. `runner.run`     then replays the trials from the cache, so verdict parsing, worst-case scoring, tool checks,
                      run directories and manifests are the code path of the hosted judges. A trial that was not
                      imported fails (approved = null, worst case); `import_outputs` refuses incomplete outputs
                      unless told otherwise, so this cannot happen silently.

Exporting the scored split requires the committed PREREG, exactly like running it.
The Hugging Face token is read from the environment or the token file by the child process only; it is never
printed, logged, or written to a job directory.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .llm import OFFLINE_PREFIX, LLMClient, LLMResult, Request, cache_key
from .runner import DesignError, Experiment, build_prompts, check_design, plan_trials, require_scored_ready

COLAB_DIR = Path("/Users/seyran/code/manage-agents/colab")
TOKEN_FILE = Path("/Users/seyran/Downloads/hugginface-access-token.txt")
VLLM_CMD = (
    "test -f /content/ve_work/venvs/vllm/.ok || (uv venv -q /content/ve_work/venvs/vllm && uv pip install -q -p "
    "/content/ve_work/venvs/vllm vllm && touch /content/ve_work/venvs/vllm/.ok) && uv pip install -q -p "
    "/content/ve_work/venvs/vllm ninja && export PATH=/content/ve_work/venvs/vllm/bin:$PATH && "  # vLLM JIT kernels need ninja
    "/content/ve_work/venvs/vllm/bin/python "
    "-u vllm_judge.py --prompts prompts.jsonl --out-dir out --models models.json --max-new-tokens {max_new_tokens} "
    "--temperature 0 --seed 0 --model-timeout-min {model_timeout_min}"
)


def is_batch_judge(judge: str) -> bool:
    return judge.startswith(OFFLINE_PREFIX)


def model_id(judge: str) -> str:
    if not is_batch_judge(judge):
        raise DesignError(f"{judge!r} is not a batch judge (expected the prefix {OFFLINE_PREFIX!r})")
    return judge[len(OFFLINE_PREFIX):]


def slug(name: str) -> str:
    """Output directory name used by jobs_lib/vllm_judge.py."""
    return re.sub(r"[^A-Za-z0-9.=_-]+", "--", name)


@dataclass(frozen=True)
class KeyedRequest:
    key: str  # judge-free trial key; the same for every judge that sees this prompt
    request: Request  # for one judge: model = judge name, with the identity and seed of a live call


def experiment_requests(exp: Experiment, split: str, client: LLMClient) -> list[KeyedRequest]:
    """The requests `runner.run` will make for the batch judges of `exp`, with judge-free keys."""
    judges = [j for j in exp.judges if is_batch_judge(j)]
    if not judges:
        raise DesignError("the experiment has no batch judge")
    if split == "scored":
        check_design(exp)
        require_scored_ready(exp, [it for it in exp.items if it.split == split])
    trials = [t for t in plan_trials(exp, split) if t.judge in judges]
    prompts = build_prompts(exp, trials)
    system = client.default_system if exp.system is None else exp.system
    return [
        KeyedRequest(f"{exp.id}|{t.split}|{t.item_id}|{t.condition}|{t.sample}",
                     Request(t.judge, p, t.seed, system, identity=t.identity(exp.id)))
        for t, p in zip(trials, prompts)
    ]  # fmt: skip


def uncached(client: LLMClient, requests: Sequence[KeyedRequest]) -> list[KeyedRequest]:
    """Requests whose key is missing from the cache for at least one judge (then the key is exported for every
    judge, so that one prompts file still serves them all). Lets a rerun submit only the cells that changed."""
    def hit(kr: KeyedRequest) -> bool:
        r = kr.request
        system = client.default_system if r.system is None else r.system
        return client._cache_read(cache_key(r.model, system, r.prompt, r.seed, r.identity)) is not None

    need = {kr.key for kr in requests if not hit(kr)}
    return [kr for kr in requests if kr.key in need]


def exported_keys(job_dir: Path) -> set[str]:
    return {json.loads(x)["key"] for x in (Path(job_dir) / "prompts.jsonl").read_text(encoding="utf-8").splitlines()}


def export_job(job_dir: Path, job_id: str, requests: Sequence[KeyedRequest], model_specs: Sequence[dict],
               max_new_tokens: int, model_timeout_min: int = 420, max_minutes: int = 780) -> dict:
    """Write prompts.jsonl, models.json and job.json. Every judge that shares a key must share the exact text."""
    judges = sorted({kr.request.model for kr in requests})
    spec_ids = [s["id"] for s in model_specs]
    if sorted(model_id(j) for j in judges) != sorted(spec_ids):
        raise DesignError(f"model specs {spec_ids} do not match the batch judges {judges}")
    by_key: dict[str, tuple[str, str]] = {}
    seen: dict[str, set[str]] = {}
    for kr in requests:
        text = (kr.request.system or "", kr.request.prompt)
        if by_key.setdefault(kr.key, text) != text:
            raise DesignError(f"key {kr.key} has different prompts for different judges")
        if kr.request.model in seen.setdefault(kr.key, set()):
            raise DesignError(f"key {kr.key} occurs twice for {kr.request.model}")
        seen[kr.key].add(kr.request.model)
    if any(s != set(judges) for s in seen.values()):
        raise DesignError("not every batch judge has every key; export one job per identical trial set")
    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=False)
    with open(job_dir / "prompts.jsonl", "x", encoding="utf-8") as fh:
        for key, (system, prompt) in by_key.items():
            msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
            fh.write(json.dumps({"key": key, "messages": msgs, "max_new_tokens": max_new_tokens}, ensure_ascii=False) + "\n")
    (job_dir / "models.json").write_text(json.dumps(list(model_specs), indent=1) + "\n", encoding="utf-8")
    job = {"id": job_id, "cmd": VLLM_CMD.format(max_new_tokens=max_new_tokens, model_timeout_min=model_timeout_min),
           "inputs": ["jobs_lib/vllm_judge.py"], "max_minutes": max_minutes}  # fmt: skip
    (job_dir / "job.json").write_text(json.dumps(job, indent=1) + "\n", encoding="utf-8")
    return {"job_id": job_id, "n_prompts": len(by_key), "judges": judges, "max_new_tokens": max_new_tokens}


class JobRunner(Protocol):
    def __call__(self, job_dir: Path, results_dir: Path) -> Path:
        """Run the job and return the directory that contains out/<slug>/outputs.jsonl."""


def _colab(*args: str, timeout_s: float) -> str:
    env = dict(os.environ)
    if not env.get("HF_TOKEN"):
        env["HF_TOKEN"] = TOKEN_FILE.read_text(encoding="utf-8").strip()
    proc = subprocess.run(["uv", "run", "-q", "--with", "huggingface_hub", "python", "colab_client.py", *args],
                          cwd=COLAB_DIR, env=env, capture_output=True, text=True, timeout=timeout_s)  # fmt: skip
    if proc.returncode != 0:
        raise RuntimeError(f"colab_client {args[0]} failed: {(proc.stderr or proc.stdout)[-400:]}")
    return proc.stdout


class ColabJobRunner:
    def __init__(self, wait_timeout_s: float = 8 * 3600):
        self.wait_timeout_s = wait_timeout_s

    def submit(self, job_dir: Path) -> str:
        return _colab("submit", str(Path(job_dir).resolve()), timeout_s=600)

    def wait_fetch(self, job_id: str, results_dir: Path) -> Path:
        _colab("wait", job_id, timeout_s=self.wait_timeout_s)
        _colab("fetch", job_id, str(Path(results_dir).resolve()), timeout_s=1800)
        return Path(results_dir)

    def __call__(self, job_dir: Path, results_dir: Path) -> Path:
        self.submit(job_dir)
        return self.wait_fetch(json.loads((Path(job_dir) / "job.json").read_text())["id"], results_dir)


class FakeJobRunner:
    """Test double: answers every prompt with `reply(model id, row) -> (text, finish_reason)`."""

    def __init__(self, reply: Callable[[str, dict], tuple[str, str]]):
        self.reply = reply

    def __call__(self, job_dir: Path, results_dir: Path) -> Path:
        rows = [json.loads(x) for x in (Path(job_dir) / "prompts.jsonl").read_text(encoding="utf-8").splitlines()]
        for spec in json.loads((Path(job_dir) / "models.json").read_text(encoding="utf-8")):
            out = Path(results_dir) / "out" / slug(spec.get("name") or spec["id"])
            out.mkdir(parents=True)
            with open(out / "outputs.jsonl", "w", encoding="utf-8") as fh:
                for row in rows:
                    text, finish = self.reply(spec["id"], row)
                    fh.write(json.dumps({"key": row["key"], "text": text, "n_input_tokens": 1, "n_output_tokens": 1,
                                         "latency_share_s": 0.0, "finish_reason": finish}) + "\n")  # fmt: skip
            (out / "manifest.json").write_text(json.dumps({"model": spec["id"], "revision": "fake"}), encoding="utf-8")
        return Path(results_dir)


def import_outputs(client: LLMClient, requests: Sequence[KeyedRequest], results_dir: Path,
                   allow_missing: bool = False) -> dict[str, dict]:
    """Store each judge's replies in the cache under the live-call key. Returns counts per judge.

    An empty reply is stored as a failed call, as the live client would record it. A key that is absent from a
    model's outputs is an error unless `allow_missing`; then it is stored as a failed call (scored worst case).
    """
    report: dict[str, dict] = {}
    for judge in sorted({kr.request.model for kr in requests}):
        out = Path(results_dir) / "out" / slug(model_id(judge))
        if not (out / "outputs.jsonl").exists():
            raise FileNotFoundError(f"no outputs for {judge} under {out}")
        rows = {}
        for line in (out / "outputs.jsonl").read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["key"] in rows:
                raise DesignError(f"{judge}: key {row['key']} occurs twice in the outputs")
            rows[row["key"]] = row
        mine = [kr for kr in requests if kr.request.model == judge]
        missing = [kr.key for kr in mine if kr.key not in rows]
        extra = set(rows) - {kr.key for kr in mine}
        if extra:
            raise DesignError(f"{judge}: {len(extra)} output keys were never exported, e.g. {sorted(extra)[:2]}")
        if missing and not allow_missing:
            raise DesignError(f"{judge}: {len(missing)} of {len(mine)} trials have no output, e.g. {missing[:2]}")
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8")) if (out / "manifest.json").exists() else {}
        counts = {"trials": len(mine), "missing": len(missing), "empty": 0, "truncated": 0,
                  "revision": manifest.get("revision"), "vllm": manifest.get("vllm")}  # fmt: skip
        for kr in mine:
            r, row = kr.request, rows.get(kr.key)
            system = client.default_system if r.system is None else r.system
            key = cache_key(r.model, system, r.prompt, r.seed, r.identity)
            text = (row or {}).get("text")
            ok = bool(text and text.strip())
            counts["empty"] += row is not None and not ok
            counts["truncated"] += (row or {}).get("finish_reason") == "length"
            client.store(LLMResult(
                model=r.model, seed=r.seed, key=key, text=text if ok else None, ok=ok,
                error=None if ok else ("missing from batch output" if row is None else "empty reply"),
                latency_s=(row or {}).get("latency_share_s") or 0.0, attempts=1,
                input_tokens=(row or {}).get("n_input_tokens"), output_tokens=(row or {}).get("n_output_tokens"),
                identity=r.identity, finish_reason=(row or {}).get("finish_reason"),
            ), system, r.prompt)  # fmt: skip
        report[judge] = counts
    return report
