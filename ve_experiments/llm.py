"""Shared model client over the `claude` and `codex` CLIs.

There are no API keys, so every model call is a subprocess. This module is the only place that
spawns one. It provides:

* a disk cache keyed by (model, system prompt, prompt, seed);
* retries with backoff, and a result object (never an exception) when all attempts fail, so that
  failed calls stay in experiment denominators;
* a process-wide concurrency limit (default 6);
* a JSONL call log with tokens and latency;
* strict parsing of a final JSON verdict (`parse_verdict`).

The CLIs take no sampling seed. `seed` only distinguishes cache entries, so seed 0 and seed 1 are
two independent samples of the same prompt, and repeating a seed replays the stored sample.

Calls run from an empty temporary directory, with tools and MCP servers disabled where the CLI
allows it, so that a judge never sees this repository (which contains ground truth).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

CACHE_VERSION = 1
DEFAULT_SYSTEM = "You are a careful reviewer. Follow the instructions in the user message exactly."
REPO_ROOT = Path(__file__).resolve().parent.parent


class BackendError(RuntimeError):
    """A model call failed in a way that may succeed on retry."""


@dataclass(frozen=True)
class RawReply:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None


@dataclass(frozen=True)
class LLMResult:
    model: str
    seed: int
    key: str
    text: str | None
    ok: bool
    error: str | None = None
    from_cache: bool = False
    latency_s: float = 0.0
    attempts: int = 0
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None


@dataclass(frozen=True)
class Request:
    model: str
    prompt: str
    seed: int = 0
    system: str | None = None
    tag: str = ""  # free-form label copied to the log (experiment id, trial id)


Backend = Callable[[str, str, str, float, Path], RawReply]
"""(model, system, prompt, timeout_s, cwd) -> RawReply; raises BackendError on failure."""


# --------------------------------------------------------------------------- CLI backends


def _run(cmd: Sequence[str], stdin: str, timeout_s: float, cwd: Path) -> str:
    try:
        proc = subprocess.run(
            list(cmd), input=stdin, capture_output=True, text=True, timeout=timeout_s, cwd=cwd
        )
    except subprocess.TimeoutExpired as exc:
        raise BackendError(f"timeout after {timeout_s}s") from exc
    except OSError as exc:
        raise BackendError(f"cannot start {cmd[0]}: {exc}") from exc
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-500:]
        raise BackendError(f"{cmd[0]} exited {proc.returncode}: {tail}")
    return proc.stdout


def claude_backend(model: str, system: str, prompt: str, timeout_s: float, cwd: Path) -> RawReply:
    cmd = [
        "claude", "-p", "--model", model, "--output-format", "json",
        "--tools", "", "--strict-mcp-config", "--system-prompt", system,
    ]  # fmt: skip
    out = _run(cmd, prompt, timeout_s, cwd)
    try:
        data = json.loads(out)
    except json.JSONDecodeError as exc:
        raise BackendError(f"claude returned non-JSON output: {out[-300:]!r}") from exc
    if data.get("is_error") or not isinstance(data.get("result"), str):
        raise BackendError(f"claude reported an error: {str(data.get('result'))[-300:]}")
    usage = data.get("usage") or {}
    cached = (usage.get("cache_read_input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0)
    return RawReply(
        text=data["result"],
        input_tokens=(usage.get("input_tokens") or 0) + cached,
        output_tokens=usage.get("output_tokens"),
        cached_input_tokens=usage.get("cache_read_input_tokens"),
    )


def codex_backend(model: str, system: str, prompt: str, timeout_s: float, cwd: Path) -> RawReply:
    # codex exec has no system-prompt flag; the system text is prepended to the prompt.
    cmd = [
        "codex", "exec", "-m", model, "-s", "read-only", "--skip-git-repo-check",
        "--json", "--ephemeral", "-",
    ]  # fmt: skip
    full = f"{system}\n\n{prompt}" if system else prompt
    out = _run(cmd, full, timeout_s, cwd)
    text: str | None = None
    usage: dict = {}
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message":
            text = event["item"].get("text")
        elif event.get("type") == "turn.completed":
            usage = event.get("usage") or {}
        elif event.get("type") in ("error", "turn.failed"):
            raise BackendError(f"codex reported: {json.dumps(event)[-300:]}")
    if text is None:
        raise BackendError(f"codex produced no agent message: {out[-300:]!r}")
    return RawReply(
        text=text,
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        cached_input_tokens=usage.get("cached_input_tokens"),
    )


def default_backend_for(model: str) -> Backend:
    if model.startswith("claude"):
        return claude_backend
    if model.startswith(("gpt", "o1", "o3", "o4", "codex")):
        return codex_backend
    raise ValueError(f"no CLI backend known for model {model!r}")


# --------------------------------------------------------------------------- client


def cache_key(model: str, system: str, prompt: str, seed: int) -> str:
    payload = json.dumps([CACHE_VERSION, model, system, prompt, seed], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class LLMClient:
    cache_dir: Path = REPO_ROOT / ".llm_cache"
    log_path: Path | None = None  # default: <cache_dir>/calls.jsonl
    max_concurrency: int = 6
    retries: int = 3  # total attempts
    timeout_s: float = 300.0
    backoff_s: float = 2.0
    backend: Backend | None = None  # override for tests; default routes by model name
    default_system: str = DEFAULT_SYSTEM
    _sem: threading.BoundedSemaphore = field(init=False, repr=False)
    _log_lock: threading.Lock = field(init=False, repr=False)
    _key_locks: dict[str, threading.Lock] = field(init=False, repr=False)
    _cwd: Path | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = Path(self.log_path) if self.log_path else self.cache_dir / "calls.jsonl"
        self._sem = threading.BoundedSemaphore(self.max_concurrency)
        self._log_lock = threading.Lock()
        self._key_locks = {}
        self._meta_lock = threading.Lock()

    # -- public API

    def call(self, model: str, prompt: str, seed: int = 0, system: str | None = None, tag: str = "") -> LLMResult:
        system = self.default_system if system is None else system
        key = cache_key(model, system, prompt, seed)
        with self._lock_for(key):  # identical concurrent requests make one model call
            hit = self._cache_read(key)
            if hit is not None:
                result = LLMResult(**{**hit, "from_cache": True})
                self._log(result, tag)
                return result
            result = self._call_uncached(model, system, prompt, seed, key)
            if result.ok:
                self._cache_write(key, result, system, prompt)
        self._log(result, tag)
        return result

    def map(self, requests: Iterable[Request], progress: Callable[[int, int], None] | None = None) -> list[LLMResult]:
        """Run requests concurrently (bounded by max_concurrency); results keep request order."""
        reqs = list(requests)
        done = 0
        lock = threading.Lock()

        def one(r: Request) -> LLMResult:
            nonlocal done
            res = self.call(r.model, r.prompt, r.seed, r.system, r.tag)
            with lock:
                done += 1
                if progress:
                    progress(done, len(reqs))
            return res

        with ThreadPoolExecutor(max_workers=max(1, self.max_concurrency)) as pool:
            return list(pool.map(one, reqs))

    # -- internals

    def _lock_for(self, key: str) -> threading.Lock:
        with self._meta_lock:
            return self._key_locks.setdefault(key, threading.Lock())

    def _neutral_cwd(self) -> Path:
        with self._meta_lock:
            if self._cwd is None or not self._cwd.exists():
                self._cwd = Path(tempfile.mkdtemp(prefix="ve-llm-neutral-"))
            return self._cwd

    def _call_uncached(self, model: str, system: str, prompt: str, seed: int, key: str) -> LLMResult:
        backend = self.backend or default_backend_for(model)
        error = "no attempt made"
        start = time.monotonic()
        for attempt in range(1, self.retries + 1):
            with self._sem:
                t0 = time.monotonic()
                try:
                    reply = backend(model, system, prompt, self.timeout_s, self._neutral_cwd())
                except BackendError as exc:
                    error = str(exc)
                else:
                    if reply.text.strip():
                        return LLMResult(
                            model=model, seed=seed, key=key, text=reply.text, ok=True,
                            latency_s=round(time.monotonic() - t0, 3), attempts=attempt,
                            input_tokens=reply.input_tokens, output_tokens=reply.output_tokens,
                            cached_input_tokens=reply.cached_input_tokens,
                        )  # fmt: skip
                    error = "empty reply"
            if attempt < self.retries:
                time.sleep(self.backoff_s * 2 ** (attempt - 1))
        return LLMResult(
            model=model, seed=seed, key=key, text=None, ok=False, error=error,
            latency_s=round(time.monotonic() - start, 3), attempts=self.retries,
        )  # fmt: skip

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / key[:2] / f"{key}.json"

    def _cache_read(self, key: str) -> dict | None:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))["result"]
        except (json.JSONDecodeError, KeyError, OSError):
            return None  # a corrupt entry is treated as a miss and overwritten

    def _cache_write(self, key: str, result: LLMResult, system: str, prompt: str) -> None:
        path = self._cache_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"result": asdict(result), "system": system, "prompt": prompt}
        tmp = path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
        tmp.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)

    def _log(self, result: LLMResult, tag: str) -> None:
        row = {k: v for k, v in asdict(result).items() if k != "text"}
        row.update(ts=round(time.time(), 3), tag=tag, chars_out=len(result.text or ""))
        with self._log_lock, open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")


def summarize_log(log_path: Path) -> dict:
    """Totals per model from a call log: calls, cache hits, failures, tokens, mean latency."""
    out: dict[str, dict] = {}
    for line in Path(log_path).read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        m = out.setdefault(
            row["model"],
            {"calls": 0, "cache_hits": 0, "failures": 0, "input_tokens": 0, "output_tokens": 0, "latency_s": 0.0},
        )
        m["calls"] += 1
        if row["from_cache"]:
            m["cache_hits"] += 1
            continue
        m["failures"] += 0 if row["ok"] else 1
        m["input_tokens"] += row.get("input_tokens") or 0
        m["output_tokens"] += row.get("output_tokens") or 0
        m["latency_s"] += row.get("latency_s") or 0.0
    for m in out.values():
        fresh = m["calls"] - m["cache_hits"]
        m["mean_latency_s"] = round(m.pop("latency_s") / fresh, 3) if fresh else None
    return out


# --------------------------------------------------------------------------- verdict parsing


class VerdictParseError(ValueError):
    pass


@dataclass(frozen=True)
class Verdict:
    value: str
    data: dict


def parse_verdict(text: str | None, allowed: Sequence[str] = ("approve", "reject"), key: str = "verdict") -> Verdict:
    """Parse the final JSON object of a reply, strictly.

    The reply may contain reasoning first, but it must END with one JSON object (optionally inside
    a closing ``` fence) whose `key` is exactly one of `allowed`. Anything else raises
    VerdictParseError: no keyword search, no case folding, no guessing. The caller scores a parse
    failure as a failed trial rather than dropping it.
    """
    if text is None:
        raise VerdictParseError("no reply")
    body = text.strip()
    if body.endswith("```"):
        body = body[:-3].rstrip()
    if not body.endswith("}"):
        raise VerdictParseError("reply does not end with a JSON object")
    obj = None
    pos = len(body)
    while True:
        pos = body.rfind("{", 0, pos)
        if pos < 0:
            break
        try:
            obj = json.loads(body[pos:])
            break
        except json.JSONDecodeError:
            continue
    if not isinstance(obj, dict):
        raise VerdictParseError("no JSON object at the end of the reply")
    if key not in obj:
        raise VerdictParseError(f"final JSON object has no {key!r} field")
    value = obj[key]
    if not isinstance(value, str) or value not in allowed:
        raise VerdictParseError(f"{key!r} is {value!r}, expected one of {list(allowed)}")
    return Verdict(value=value, data=obj)
