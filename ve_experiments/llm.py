"""Shared model client over the `claude` and `codex` CLIs.

There are no API keys, so every model call is a subprocess. This module is the only place that
spawns one. It provides:

* a disk cache keyed by (model, system prompt, prompt, seed);
* retries with backoff, and a result object (never an exception) when all attempts fail, so that
  failed calls stay in experiment denominators;
* a concurrency limit per provider CLI (default 6 each for `claude` and `codex`);
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

CACHE_VERSION = 2  # 2: hardened CLI flags, trial identity in the key, tool-use detection
DEFAULT_SYSTEM = "You are a careful reviewer. Follow the instructions in the user message exactly."
REPO_ROOT = Path(__file__).resolve().parent.parent


class BackendError(RuntimeError):
    """A model call failed in a way that may succeed on retry. `tool_events` lists anything the model did
    besides writing text before it failed; the client carries them over to the retry, so a judge that ran a
    tool in a failed attempt stays invalid even if a later attempt answers cleanly."""

    def __init__(self, message: str, tool_events: Sequence[str] = ()):
        super().__init__(message)
        self.tool_events = tuple(tool_events)


@dataclass(frozen=True)
class RawReply:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    tool_events: tuple[str, ...] = ()  # anything the model did besides writing text (commands, tools, searches)
    finish_reason: str | None = None  # "length" = the reply hit the token limit (known for vLLM judges only)


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
    tool_events: tuple[str, ...] = ()
    identity: str = ""
    finish_reason: str | None = None  # "length" when the reply was cut at the token limit; None when unknown

    @property
    def truncated(self) -> bool:
        return self.finish_reason == "length"

    @property
    def used_tools(self) -> bool:
        return bool(self.tool_events)


@dataclass(frozen=True)
class Request:
    model: str
    prompt: str
    seed: int = 0
    system: str | None = None
    tag: str = ""  # free-form label copied to the log
    identity: str = ""  # stable trial identity; part of the cache key, never shown to the model


Backend = Callable[[str, str, str, float, Path], RawReply]
"""(model, system, prompt, timeout_s, cwd) -> RawReply; raises BackendError on failure."""


# --------------------------------------------------------------------------- CLI backends


def split_model(model: str) -> tuple[str, dict[str, str]]:
    """"gpt-5.6-luna@effort=none" -> ("gpt-5.6-luna", {"effort": "none"}). Settings are part of the
    judge's name everywhere (cache key, trials, reports), so a judge with reasoning disabled can never
    be confused with the default one. Supported: `effort=<level>` (codex model_reasoning_effort) and
    `thinking=<max tokens>` (claude MAX_THINKING_TOKENS)."""
    base, _, rest = model.partition("@")
    settings = dict(kv.split("=", 1) for kv in rest.split(",") if kv)
    unknown = set(settings) - {"effort", "thinking"}
    if unknown:
        raise ValueError(f"unknown model settings {sorted(unknown)} in {model!r}")
    return base, settings


def _run(cmd: Sequence[str], stdin: str, timeout_s: float, cwd: Path, env: dict | None = None,
         events_from: Callable[[str], list[str]] | None = None) -> str:
    try:
        proc = subprocess.run(
            list(cmd), input=stdin, capture_output=True, text=True, timeout=timeout_s, cwd=cwd,
            env={**os.environ, **env} if env else None,
        )
    except subprocess.TimeoutExpired as exc:
        raise BackendError(f"timeout after {timeout_s}s") from exc
    except OSError as exc:
        raise BackendError(f"cannot start {cmd[0]}: {exc}") from exc
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-500:]
        raise BackendError(f"{cmd[0]} exited {proc.returncode}: {tail}", events_from(proc.stdout or "") if events_from else ())
    return proc.stdout


CLAUDE_ISOLATION = ("--safe-mode", "--setting-sources", "", "--disable-slash-commands")
"""No ambient context for Claude judges: --safe-mode disables CLAUDE.md, skills, plugins, hooks, MCP servers,
custom commands and agents, output styles; --setting-sources "" loads no user, project or local settings;
--system-prompt replaces the default prompt; the cwd is an empty temporary directory. Checked live on
2026-09-21: the model reports no context besides the message. NOT disabled, because no flag exists: admin-managed
(policy) settings, and about 450 input tokens that the CLI adds to every call."""


def claude_backend(model: str, system: str, prompt: str, timeout_s: float, cwd: Path) -> RawReply:
    base, settings = split_model(model)
    cmd = [
        "claude", "-p", "--model", base, "--output-format", "json",
        "--tools", "", "--strict-mcp-config", *CLAUDE_ISOLATION, "--system-prompt", system,
    ]  # fmt: skip
    env = {"MAX_THINKING_TOKENS": settings["thinking"]} if "thinking" in settings else None
    out = _run(cmd, prompt, timeout_s, cwd, env)
    try:
        data = json.loads(out)
    except json.JSONDecodeError as exc:
        raise BackendError(f"claude returned non-JSON output: {out[-300:]!r}") from exc
    if data.get("is_error") or not isinstance(data.get("result"), str):
        raise BackendError(f"claude reported an error: {str(data.get('result'))[-300:]}")
    tool_events = []
    if (data.get("num_turns") or 1) > 1:
        tool_events.append(f"claude:num_turns={data.get('num_turns')}")
    tool_events += [f"claude:permission_denial:{json.dumps(d)[:120]}" for d in data.get("permission_denials") or []]
    usage = data.get("usage") or {}
    cached = (usage.get("cache_read_input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0)
    return RawReply(
        text=data["result"],
        input_tokens=(usage.get("input_tokens") or 0) + cached,
        output_tokens=usage.get("output_tokens"),
        cached_input_tokens=usage.get("cache_read_input_tokens"),
        tool_events=tuple(tool_events),
    )


CODEX_FLAGS = (
    "-s", "read-only", "--skip-git-repo-check", "--json", "--ephemeral", "--ignore-user-config", "--ignore-rules",
    "--disable", "shell_tool", "--disable", "apps", "--disable", "browser_use", "--disable", "computer_use",
    "--disable", "plugins", "-c", 'web_search="disabled"',
)  # fmt: skip
"""`-s read-only` alone still lets the model READ the whole filesystem, including ground truth in this
repository. Disabling the shell tool and the other tool features removes that ability (verified live:
asked to run `ls`, the model answers that it cannot). As a second line of defence every event that is
not plain text is recorded, and the runner scores such a trial as invalid."""

_CODEX_TEXT_ITEMS = ("agent_message", "reasoning")


def codex_tool_events(out: str) -> list[str]:
    """Every non-text item in a codex event stream, also when the run failed afterwards."""
    found: list[str] = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") or {}
        if event.get("type", "").startswith("item.") and item.get("type") not in _CODEX_TEXT_ITEMS:
            if event.get("type") == "item.completed" or item.get("type") == "command_execution":
                found.append(f"codex:{item.get('type')}:{str(item.get('command') or item.get('name') or '')[:120]}")
    return list(dict.fromkeys(found))


def parse_codex_events(out: str) -> RawReply:
    text: str | None = None
    usage: dict = {}
    tool_events: list[str] = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") or {}
        if event.get("type", "").startswith("item.") and item.get("type") not in _CODEX_TEXT_ITEMS:
            if event.get("type") == "item.completed" or item.get("type") == "command_execution":
                tool_events.append(f"codex:{item.get('type')}:{str(item.get('command') or item.get('name') or '')[:120]}")
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            text = item.get("text")
        elif event.get("type") == "turn.completed":
            usage = event.get("usage") or {}
        elif event.get("type") in ("error", "turn.failed"):
            raise BackendError(f"codex reported: {json.dumps(event)[-300:]}", tool_events)
    if text is None:
        raise BackendError(f"codex produced no agent message: {out[-300:]!r}", tool_events)
    return RawReply(
        text=text,
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        cached_input_tokens=usage.get("cached_input_tokens"),
        tool_events=tuple(dict.fromkeys(tool_events)),
    )


def codex_backend(model: str, system: str, prompt: str, timeout_s: float, cwd: Path) -> RawReply:
    # codex exec has no system-prompt flag; the system text is prepended to the prompt.
    base, settings = split_model(model)
    extra = ["-c", f'model_reasoning_effort="{settings["effort"]}"'] if "effort" in settings else []
    cmd = ["codex", "exec", "-m", base, *CODEX_FLAGS, *extra, "-"]
    full = f"{system}\n\n{prompt}" if system else prompt
    return parse_codex_events(_run(cmd, full, timeout_s, cwd, events_from=codex_tool_events))


OFFLINE_PREFIX = "vllm:"
"""Judges named `vllm:<hugging face id>` are open-weight models run as a batch job on a GPU runtime
(ve_experiments/colab.py). Their replies are imported into the cache under the same key a live call would
use; a cache miss is therefore a missing import, never a reason to call anything."""


def offline_backend(model: str, system: str, prompt: str, timeout_s: float, cwd: Path) -> RawReply:
    raise BackendError(f"{model} is a batch judge and this trial was not imported (see ve_experiments/colab.py)")


def default_backend_for(model: str) -> Backend:
    if model.startswith(OFFLINE_PREFIX):
        return offline_backend
    if model.startswith("claude"):
        return claude_backend
    if model.startswith(("gpt", "o1", "o3", "o4", "codex")):
        return codex_backend
    raise ValueError(f"no CLI backend known for model {model!r}")


# --------------------------------------------------------------------------- client


def cache_key(model: str, system: str, prompt: str, seed: int, identity: str = "") -> str:
    """`identity` names the trial (experiment, item, cell, judge, sample). It keeps two trials that
    happen to share a prompt from collapsing into one model call, and is never sent to the model."""
    payload = json.dumps([CACHE_VERSION, model, system, prompt, seed, identity], ensure_ascii=False)
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
    _sems: dict = field(init=False, repr=False)
    _log_lock: threading.Lock = field(init=False, repr=False)
    _key_locks: dict[str, threading.Lock] = field(init=False, repr=False)
    _cwd: Path | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = Path(self.log_path) if self.log_path else self.cache_dir / "calls.jsonl"
        self._sems = {}
        self._log_lock = threading.Lock()
        self._key_locks = {}
        self._meta_lock = threading.Lock()

    # -- public API

    def call(
        self, model: str, prompt: str, seed: int = 0, system: str | None = None, tag: str = "", identity: str = ""
    ) -> LLMResult:
        system = self.default_system if system is None else system
        key = cache_key(model, system, prompt, seed, identity)
        with self._lock_for(key):  # identical concurrent requests make one model call
            hit = self._cache_read(key)
            if hit is not None:
                hit["tool_events"] = tuple(hit.get("tool_events") or ())
                result = LLMResult(**{**hit, "from_cache": True})
                self._log(result, tag)
                return result
            result = self._call_uncached(model, system, prompt, seed, key, identity)
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
            res = self.call(r.model, r.prompt, r.seed, r.system, r.tag, r.identity)
            with lock:
                done += 1
                if progress:
                    progress(done, len(reqs))
            return res

        with ThreadPoolExecutor(max_workers=max(1, 2 * self.max_concurrency)) as pool:
            return list(pool.map(one, reqs))

    # -- internals

    def _sem_for(self, model: str) -> threading.BoundedSemaphore:
        """One limit per provider CLI (`claude*` vs everything else), since their rate limits are separate."""
        family = "claude" if model.startswith("claude") else "codex"
        with self._meta_lock:
            return self._sems.setdefault(family, threading.BoundedSemaphore(self.max_concurrency))

    def _lock_for(self, key: str) -> threading.Lock:
        with self._meta_lock:
            return self._key_locks.setdefault(key, threading.Lock())

    def _neutral_cwd(self) -> Path:
        with self._meta_lock:
            if self._cwd is None or not self._cwd.exists():
                self._cwd = Path(tempfile.mkdtemp(prefix="ve-llm-neutral-"))
            return self._cwd

    def _call_uncached(self, model: str, system: str, prompt: str, seed: int, key: str, identity: str = "") -> LLMResult:
        backend = self.backend or default_backend_for(model)
        error = "no attempt made"
        carried: list[str] = []  # tool events of failed attempts; they invalidate the trial whatever comes later
        start = time.monotonic()
        for attempt in range(1, self.retries + 1):
            with self._sem_for(model):
                t0 = time.monotonic()
                try:
                    reply = backend(model, system, prompt, self.timeout_s, self._neutral_cwd())
                except BackendError as exc:
                    error = str(exc)
                    carried += [f"attempt{attempt}:{e}" for e in exc.tool_events]
                else:
                    if reply.text.strip():
                        return LLMResult(
                            model=model, seed=seed, key=key, text=reply.text, ok=True,
                            latency_s=round(time.monotonic() - t0, 3), attempts=attempt,
                            input_tokens=reply.input_tokens, output_tokens=reply.output_tokens,
                            cached_input_tokens=reply.cached_input_tokens,
                            tool_events=(*carried, *reply.tool_events), identity=identity,
                            finish_reason=reply.finish_reason,
                        )  # fmt: skip
                    error = "empty reply"
            if backend is offline_backend:
                break  # nothing to retry
            if attempt < self.retries:
                time.sleep(self.backoff_s * 2 ** (attempt - 1))
        return LLMResult(
            model=model, seed=seed, key=key, text=None, ok=False, error=error,
            latency_s=round(time.monotonic() - start, 3), attempts=self.retries, identity=identity,
            tool_events=tuple(carried),
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

    def store(self, result: LLMResult, system: str, prompt: str) -> None:
        """Put an externally produced reply (a batch judge) into the cache. `result.key` must be the key of
        the call it stands for. Failed results are stored too, so a replay reports the same failure."""
        if result.key != cache_key(result.model, system, prompt, result.seed, result.identity):
            raise ValueError("result.key does not match (model, system, prompt, seed, identity)")
        self._cache_write(result.key, result, system, prompt)

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


def parse_final_json(text: str | None) -> dict:
    """The JSON object that ENDS the reply (optionally inside a closing ``` fence), or VerdictParseError."""
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
    return obj


def parse_verdict(text: str | None, allowed: Sequence[str] = ("approve", "reject"), key: str = "verdict") -> Verdict:
    """Parse the final JSON object of a reply, strictly.

    The reply may contain reasoning first, but it must END with one JSON object (optionally inside
    a closing ``` fence) whose `key` is exactly one of `allowed`. Anything else raises
    VerdictParseError: no keyword search, no case folding, no guessing. The caller scores a parse
    failure as a failed trial rather than dropping it.
    """
    obj = parse_final_json(text)
    if key not in obj:
        raise VerdictParseError(f"final JSON object has no {key!r} field")
    value = obj[key]
    if not isinstance(value, str) or value not in allowed:
        raise VerdictParseError(f"{key!r} is {value!r}, expected one of {list(allowed)}")
    return Verdict(value=value, data=obj)
