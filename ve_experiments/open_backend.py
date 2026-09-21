"""Local open-weight judges for `LLMClient` (Apple MLX through `mlx-lm`, 4-bit community quantizations).

A judge name is `open:<hf repo>[@key=value,...]`, e.g.

    open:mlx-community/Qwen2.5-3B-Instruct-4bit
    open:mlx-community/Qwen2.5-3B-Instruct-4bit@verdict=forced
    open:mlx-community/Qwen2.5-3B-Instruct-4bit@temp=0.7,max_new=400

Settings (all part of the judge name, hence of the cache key, the trial rows and every report):
  max_new   cap on generated tokens (default 400)
  temp      0 = deterministic greedy decoding (default); > 0 = sampling, seeded with the request's seed,
            so that (prompt, seed) replays exactly. Unlike the CLI backends the seed is real here.
  verdict   free (default) | forced | reason_forced, see `open_worker.py`. In every mode the reply goes
            through the same strict `parse_verdict`, and an unparseable reply is scored as the worst case.

The models run in ONE worker subprocess (`open_worker.py`) that holds one model at a time. The worker may
use another interpreter: set VE_OPEN_PYTHON to a Python that has `mlx-lm` (default: this interpreter).
The worker runs with HF_HUB_OFFLINE=1 from a neutral directory: weights must be downloaded beforehand
(`huggingface_hub.snapshot_download`), and a judge never triggers network access.

Caching, retries and the call log are the client's, exactly as for hosted judges. In addition every
fresh generation is logged to <cache_dir>/open_calls.jsonl with batch size, wall time and token counts.
Greedy requests that arrive together are generated as one batch (VE_OPEN_BATCH, default 8); the logged
`gen_s` is the wall time of the batch, so throughput is batch_size / gen_s.
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from .llm import REPO_ROOT, BackendError, RawReply

PREFIX = "open:"
DEFAULTS = {"max_new": "400", "temp": "0", "verdict": "free"}
VERDICT_MODES = ("free", "forced", "reason_forced")
WORKER = Path(__file__).with_name("open_worker.py")
ALLOWED = ("approve", "reject")


def max_batch() -> int:
    return int(os.environ.get("VE_OPEN_BATCH", "8"))


def parse_open_model(model: str) -> tuple[str, dict[str, str]]:
    if not model.startswith(PREFIX):
        raise ValueError(f"not an open-weight judge name: {model!r}")
    repo, _, rest = model[len(PREFIX) :].partition("@")
    given = dict(kv.split("=", 1) for kv in rest.split(",") if kv)
    unknown = set(given) - set(DEFAULTS)
    if unknown or not repo:
        raise ValueError(f"bad open-weight judge name {model!r} (unknown settings {sorted(unknown)})")
    settings = {**DEFAULTS, **given}
    if settings["verdict"] not in VERDICT_MODES:
        raise ValueError(f"verdict must be one of {VERDICT_MODES}")
    if int(settings["max_new"]) <= 0 or float(settings["temp"]) < 0:
        raise ValueError(f"bad max_new or temp in {model!r}")
    return repo, settings


class Worker:
    """One subprocess, many waiting threads. Replies are matched to requests by id."""

    def __init__(self, cmd: list[str] | None = None, log_path: Path | None = None) -> None:
        self.cmd = cmd
        self.log_path = Path(log_path) if log_path else REPO_ROOT / ".llm_cache" / "open_calls.jsonl"
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._waiting: dict[int, dict] = {}
        self._ids = itertools.count(1)

    def _start(self, cwd: Path) -> None:
        cmd = self.cmd or [os.environ.get("VE_OPEN_PYTHON", sys.executable), str(WORKER), str(max_batch())]
        env = {**os.environ, "HF_HUB_OFFLINE": "1", "TOKENIZERS_PARALLELISM": "false"}
        env.pop("HF_TOKEN", None)
        try:
            self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                          text=True, cwd=cwd, env=env)  # fmt: skip
        except OSError as exc:
            raise BackendError(f"cannot start open-weight worker: {exc}") from exc
        threading.Thread(target=self._read, args=(self._proc,), daemon=True).start()

    def _read(self, proc: subprocess.Popen) -> None:
        for line in proc.stdout:
            try:
                rep = json.loads(line)
            except json.JSONDecodeError:
                continue
            with self._lock:
                slot = self._waiting.pop(rep.get("id"), None)
            if slot:
                slot["reply"] = rep
                slot["event"].set()
        with self._lock:  # the worker died: fail everyone who is still waiting
            slots, self._waiting = list(self._waiting.values()), {}
            if self._proc is proc:
                self._proc = None
        for slot in slots:
            slot["reply"] = {"error": "open-weight worker exited"}
            slot["event"].set()

    def request(self, payload: dict, timeout_s: float, cwd: Path) -> dict:
        slot = {"event": threading.Event(), "reply": None}
        with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._start(cwd)
            rid = next(self._ids)
            self._waiting[rid] = slot
            try:
                self._proc.stdin.write(json.dumps({**payload, "id": rid}, ensure_ascii=False) + "\n")
                self._proc.stdin.flush()
            except OSError as exc:
                self._waiting.pop(rid, None)
                raise BackendError(f"open-weight worker is not accepting requests: {exc}") from exc
        if not slot["event"].wait(timeout_s):
            with self._lock:
                self._waiting.pop(rid, None)
            self.close()  # a stuck generation cannot be cancelled; restart the worker
            raise BackendError(f"timeout after {timeout_s}s")
        rep = slot["reply"]
        if "error" in rep:
            raise BackendError(rep["error"])
        return rep

    def log(self, row: dict) -> None:
        with self._lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")

    def close(self) -> None:
        with self._lock:
            proc, self._proc = self._proc, None
        if proc and proc.poll() is None:
            proc.kill()


_worker = Worker()


def open_backend(model: str, system: str, prompt: str, timeout_s: float, cwd: Path, seed: int = 0,
                 worker: Worker | None = None) -> RawReply:  # fmt: skip
    repo, s = parse_open_model(model)
    w = worker or _worker
    payload = {"model": repo, "system": system, "prompt": prompt, "max_new": int(s["max_new"]), "temp": float(s["temp"]),
               "seed": seed, "verdict": s["verdict"], "allowed": list(ALLOWED)}  # fmt: skip
    t0 = time.monotonic()
    rep = w.request(payload, timeout_s, cwd)
    w.log({"ts": round(time.time(), 3), "model": model, "seed": seed, "input_tokens": rep.get("input_tokens"),
           "output_tokens": rep.get("output_tokens"), "gen_s": rep.get("gen_s"), "batch_size": rep.get("batch_size"),
           "wait_s": round(time.monotonic() - t0, 3), "hit_max_new": rep.get("output_tokens", 0) >= int(s["max_new"]),
           "extra": rep.get("extra") or {}})  # fmt: skip
    return RawReply(text=rep.get("text") or "", input_tokens=rep.get("input_tokens"), output_tokens=rep.get("output_tokens"))


open_backend.takes_seed = True  # LLMClient passes the request's seed to backends that declare this
