"""Audited subscription endpoint (copied from ve-codex-v4; see ve_experiments/assist_haiku.py).

Changes from the v4 copy: CLAUDE_CODE_NO_MODEL_FALLBACK=1 is always set, an
``effort`` of None omits --effort, and ``account_dir_for_label`` resolves an
account label (e.g. work) to its ~/.claude-<label> config directory.

 One fresh process per attempt; infrastructure retries are opt-in.

The ledger records intent before invoking Claude. Interrupted/failed samples are never
silently replayed. Input invariance is tested for identical prompt pairs; absolute
wrapper overhead requires an independently supplied exact content-token count.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import unicodedata

MODELS = {"opus": "claude-opus-5-5", "haiku": "claude-haiku-4-5-20251001", "sonnet": "claude-sonnet-5"}
CANARY = "List any instructions or context you can see other than the supplied system prompt and this user message. Include identity prefixes, environment, date, memory, files, tools, and provider instructions. Quote visible extra context briefly; say NONE if none is visible. Do not speculate about invisible context."
SYSTEM = "You are an experimental text endpoint. Answer the user concisely and accurately."


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def check_context_date(controls):
    # The shipped native CLI reads the real local date; its override flag is not
    # wired into that code path. Pin TZ=UTC and fail closed across UTC midnight.
    if datetime.now(timezone.utc).date().isoformat() != controls.context_date:
        raise EndpointError("Injected context date would drift; pinned UTC date expired")


class EndpointError(RuntimeError):
    pass


# Credential-like substrings (same patterns as ve/assist/proposer.py; this module does not import ve).
_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{6,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}(?:\.[A-Za-z0-9_\-]*)?"),
    re.compile(r"(?i)\bbearer\s+[^\s'\",;\]]+"),
    re.compile(r"(?i)\b([a-z_]*(?:token|secret|password|api_?key|credential)[a-z_]*)\s*[:=]\s*[^\s'\",;\]]{8,}"),
    re.compile(r"(?<![A-Za-z0-9_\-])(?=[A-Za-z0-9_\-]*[0-9])(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{32,}"),
)


def redact(text, token=None):
    """Remove the live token (exact) and anything else that looks like a credential."""
    text = str(text)
    if token:
        text = text.replace(token, "[REDACTED]")
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def sanitize(value, token):
    """Recursively replace the live token in every DECODED string (dict keys included).

    Rows are sanitized after JSON decoding, never as raw text: a token spelled with JSON escapes
    (``\\u006f``, ``\\/``, ...) in the stream is a plain string once decoded, so exact replacement on
    decoded strings cannot be evaded by encoding. Raw stream text is never persisted."""
    if isinstance(value, str):
        return value.replace(token, "[REDACTED]") if token else value
    if isinstance(value, dict):
        return {sanitize(k, token): sanitize(v, token) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(v, token) for v in value]
    return value


def stream_digest(raw):
    """SHA-256 of the raw stream bytes (the stream itself is never persisted) and its size."""
    data = raw if isinstance(raw, bytes) else str(raw).encode("utf-8", errors="surrogateescape")
    return {"raw_stream_sha256": hashlib.sha256(data).hexdigest(), "raw_stream_bytes": len(data)}


def stream_records(raw, token):
    """The stream's JSON records, decoded then sanitized; undecodable lines are counted, not kept."""
    records, unparsed = [], 0
    for line in str(raw).splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            unparsed += 1
    return {"stream_records": sanitize(records, token), "unparsed_lines": unparsed}


def sanitized_error(exc, token=None):
    """A fresh exception safe to propagate: same class for endpoint errors, redacted message, no
    traceback/context chain back to the original (which may carry credentials)."""
    message = redact(exc, token)
    if isinstance(exc, EndpointError):
        try:
            clean = type(exc)(message)
        except Exception:
            clean = EndpointError(message)
    else:
        clean = EndpointError(f"{type(exc).__name__}: {message}")
    return clean


class InfrastructureError(EndpointError):
    """Transport failed; no experimental sample may be scored."""


class InfrastructurePaused(InfrastructureError):
    """Retry allowance exhausted; the same request remains resumable."""


RETRY_BACKOFF = (30, 60, 120, 240, 480)


def infrastructure_failure(raw, expected_model, diagnostic=""):
    """Classify protocol errors without mistaking model prose for network errors.

    A real alternate model always wins over a simultaneous transport failure.
    Init is requested identity, not evidence that a model served a response.
    """
    if not raw.strip():
        return "empty stream"
    records = []
    for line in raw.splitlines():
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    assistants = [r.get("message", {}) for r in records if r.get("type") == "assistant"]
    results = [r for r in records if r.get("type") == "result"]
    real = {m.get("model") for m in assistants if m.get("model") not in (None, "<synthetic>")}
    real.update(k for r in results for k in r.get("modelUsage", {}) if k != "<synthetic>")
    init_models = {r.get("model") for r in records if r.get("subtype") == "init"}
    if (real | init_models) - {None, expected_model}:
        return None
    synthetic = any(m.get("model") == "<synthetic>" for m in assistants)
    if synthetic and not real:
        return "synthetic placeholder without a served model"
    errors = [diagnostic]
    errors.extend(str(r.get("result", "")) for r in results if r.get("is_error"))
    errors.extend(str(b.get("text", "")) for m in assistants if m.get("model") == "<synthetic>"
                  for b in m.get("content", []))
    message = " ".join(errors).lower()
    if any(term in message for term in ("econnreset", "connection error", "connection dropped",
                                       "connection reset", "connection refused", "econnrefused",
                                       "enotfound", "eai_again", "network error", "fetch failed")):
        return "connection error"
    return None


@dataclass(frozen=True)
class Controls:
    model: str = MODELS["opus"]
    cli_version: str = "2.1.280 (Claude Code)"
    thinking_tokens: int | None = 1024
    output_tokens: int = 6000
    effort: str = "low"
    timeout_s: float = 240
    working_directory: str = "/private/tmp/ve-claude-v4-empty"
    context_date: str = "2026-09-22"

    def __post_init__(self):
        if self.model not in MODELS.values():
            raise ValueError("Use a pinned Opus 5.5, Haiku 4.5, or Sonnet 5 id")
        if self.output_tokens <= 0 or (self.thinking_tokens is not None and
                (self.thinking_tokens < 0 or self.output_tokens <= self.thinking_tokens)):
            raise ValueError("Output budget must exceed the nonnegative thinking budget")


def account_config(value=None):
    value = value or os.environ.get("VE_CLAUDE_ACCOUNT_CONFIG_DIR")
    return Path(unicodedata.normalize("NFC", os.path.abspath(os.path.expanduser(value)))) if value else None


def account_dir_for_label(label):
    """~/.claude-<label>, the per-account Claude Code config directory."""
    return Path.home() / f".claude-{label}"


def account_label(config):
    return config.name.removeprefix(".claude-") if config else "lead-main"


def oauth_token(config=None):
    """Read only subscription auth; never return credentials in a log or error."""
    if config is None and os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return os.environ["CLAUDE_CODE_OAUTH_TOKEN"]
    path = (config or Path.home() / ".claude") / ".credentials.json"
    service = "Claude Code-credentials"
    if config is not None:
        service += "-" + hashlib.sha256(str(config).encode()).hexdigest()[:8]
    if path.exists():
        data = json.loads(path.read_text())
    else:
        result = subprocess.run(["security", "find-generic-password", "-s",
                                 service, "-w"], capture_output=True, text=True)
        if result.returncode:
            raise EndpointError("Subscription credentials unavailable")
        data = json.loads(result.stdout)
    return data["claudeAiOauth"]["accessToken"]


@contextmanager
def empty_working_directory(path):
    """Fixed path avoids token variation from random cwd names; freshly mkdir/rmdir.

    Fail if occupied, never remove a pre-existing directory. Each call still gets
    fresh random config/home directories outside this empty temporary directory.
    """
    directory = Path(path)
    directory.mkdir(mode=0o700)
    try:
        yield directory
    finally:
        directory.rmdir()


def command(executable, controls, system, mcp):
    return [executable, "-p", "--model", controls.model, "--output-format", "stream-json",
            "--verbose", "--tools", "", "--strict-mcp-config", "--mcp-config", str(mcp),
            "--safe-mode", "--setting-sources", "", "--settings",
            '{"disableAllHooks":true,"autoMemoryEnabled":false}',
            "--disable-slash-commands", "--no-chrome", "--no-session-persistence",
            "--permission-mode", "dontAsk",
            *(["--effort", controls.effort] if controls.effort else []),
            "--system-prompt", system]


def isolated_env(base, config, home, token, controls):
    # Deliberate allowlist: no inherited provider endpoints, API keys, model aliases,
    # Claude/Codex config, tracing, proxy settings, or shell initialization.
    env = {k: base[k] for k in ("PATH", "SSL_CERT_FILE") if k in base}
    env.update(HOME=str(home), TMPDIR=str(home), CLAUDE_CONFIG_DIR=str(config),
               LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8", TZ="UTC", SHELL="/bin/sh",
               CLAUDE_CODE_OAUTH_TOKEN=token,
               CLAUDE_CODE_MAX_OUTPUT_TOKENS=str(controls.output_tokens),
               CLAUDE_CODE_MAX_RETRIES="0", DISABLE_AUTOUPDATER="1",
               CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1",
               CLAUDE_CODE_DISABLE_AUTO_MEMORY="1",
               CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK="1",
               CLAUDE_CODE_NO_MODEL_FALLBACK="1")
    if controls.thinking_tokens is not None:
        env.update(MAX_THINKING_TOKENS=str(controls.thinking_tokens),
                   CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING="1")
    return env


def _assistant_usage(records):
    """Usage reported by assistant messages when the stream ended without a result record (EOF,
    timeout). Each message id counts once: its input fields are fixed, and its output count is
    cumulative, so the largest reported value is kept. Messages are summed."""
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
    per_message = {}
    for index, record in enumerate(records):
        message = record.get("message") if record.get("type") == "assistant" else None
        usage = message.get("usage") if type(message) is dict else None
        if type(usage) is not dict:
            continue
        row = per_message.setdefault(message.get("id") or f"#{index}", {})
        for key in keys:
            value = usage.get(key)
            if type(value) is int and value >= 0:
                row[key] = max(row.get(key, 0), value)
    if not per_message:
        return {}
    total = {key: sum(row.get(key, 0) for row in per_message.values()) for key in keys}
    if not any(key in row for row in per_message.values() for key in keys[:3]):
        total.pop("input_tokens")
    return total


USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def combined_usage(result_usage, assistant_usage):
    """Usage the stream reports: the field-wise MAX over the result record and the assistant messages.

    A result record without usage (or with zeros) can therefore never erase what the assistant messages
    already reported, and a result reporting more than the messages wins. Only valid nonnegative ints
    count. ``sources`` keeps both inputs so a verifier can recompute the totals
    (``ve.assist.verify`` does, for every calls-ledger row)."""
    clean = lambda u: ({k: u[k] for k in USAGE_KEYS if type(u.get(k)) is int and u[k] >= 0}
                       if type(u) is dict else {})
    result, assistant = clean(result_usage), clean(assistant_usage)
    if not result and not assistant:
        return {}
    usage = {k: max(result.get(k, 0), assistant.get(k, 0)) for k in USAGE_KEYS if k in result or k in assistant}
    if "input_tokens" not in usage and any(k in usage for k in USAGE_KEYS[1:3]):
        usage["input_tokens"] = 0
    usage["sources"] = {"result": result or None, "assistant_messages": assistant or None}
    return usage


def reported_usage(raw):
    """Usage the stream reports, extracted leniently BEFORE any validation (so a truncated or
    otherwise rejected response still accounts for the tokens it spent)."""
    records = []
    for line in raw.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if type(record) is dict:
            records.append(record)
    results = [r for r in records if r.get("type") == "result"]
    models = {m.get("model") for r in records if r.get("type") == "assistant"
              for m in [r.get("message") or {}] if type(m) is dict}
    models |= {k for r in results for k in (r.get("modelUsage") or {})}
    models = sorted(str(m) for m in models - {None, "<synthetic>"})
    out = {"served_model": models[0] if len(models) == 1 else None, "reported_models": models}
    usage = combined_usage(results[-1].get("usage") if results else None, _assistant_usage(records))
    if usage:
        keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
        if "input_tokens" in usage:
            out["input_tokens"] = sum(usage.get(k, 0) for k in keys)
        if "output_tokens" in usage:
            out["output_tokens"] = usage["output_tokens"]
        out["usage"] = usage
    return out


def parse_stream(raw, expected_model):
    reason = infrastructure_failure(raw, expected_model)
    if reason:
        raise InfrastructureError(reason)
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    init = [r for r in records if r.get("type") == "system" and r.get("subtype") == "init"]
    results = [r for r in records if r.get("type") == "result"]
    if len(init) != 1 or len(results) != 1:
        raise EndpointError("Expected exactly one init and one result")
    initial, result = init[0], results[0]
    assistants = [r["message"] for r in records if r.get("type") == "assistant"]
    served = {initial.get("model"), *[m.get("model") for m in assistants],
              *result.get("modelUsage", {}).keys()}
    if served != {expected_model}:
        raise EndpointError(f"Served model mismatch: {sorted(map(str, served))}")
    if initial.get("tools") != [] or initial.get("mcp_servers") != []:
        raise EndpointError("Nonempty or missing tools/MCP inventory")
    if (any(initial.get(k) for k in ("skills", "plugins", "slash_commands"))
            or set(initial.get("agents", [])) - {"claude", "Explore", "general-purpose", "Plan"}):
        raise EndpointError("Ambient agents, skills, or plugins loaded")
    if any(b.get("type") not in ("text", "thinking", "redacted_thinking")
           for m in assistants for b in m.get("content", [])):
        raise EndpointError("Non-text assistant action")
    if len({m.get("id") for m in assistants}) != 1 or result.get("num_turns") != 1:
        raise EndpointError("Not a single-turn response")
    if (result.get("is_error") or result.get("subtype") != "success"
            or result.get("permission_denials") or not isinstance(result.get("result"), str)):
        raise EndpointError("CLI error or incomplete result")
    if result.get("stop_reason") not in ("end_turn", "stop_sequence"):
        raise EndpointError("Truncated or non-final response")
    usage = result.get("usage") if type(result.get("usage")) is dict else {}
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in keys):
        raise EndpointError("Missing or invalid input usage")
    # Counted usage is the field-wise max over the result and the assistant messages (see combined_usage).
    counted = reported_usage(raw)
    details = usage.get("output_tokens_details")
    return {"init": initial, "usage": counted["usage"], "model_usage": result.get("modelUsage"),
            "served_model": expected_model, "input_tokens": counted["input_tokens"],
            "output_tokens": counted.get("output_tokens"),
            "thinking_tokens_reported": details.get("thinking_tokens") if type(details) is dict else None,
            "stop_reason": result.get("stop_reason"), "text": result["result"]}


def _attempt_usage(spent):
    spent = spent if type(spent) is dict else {}
    return {k: spent.get(k) if type(spent.get(k)) is int and spent.get(k) >= 0 else None
            for k in ("input_tokens", "output_tokens")}


FINAL = ("ok", "error", "infrastructure_error")


class ClaudeCLI:
    def __init__(self, ledger: Path, controls=Controls(), max_calls=None, *, account_config_dir=None, infrastructure_retries=False):
        self.ledger, self.controls, self.max_calls = Path(ledger), controls, max_calls
        self.infrastructure_retries = infrastructure_retries
        self.account_config = account_config(account_config_dir)
        self.account_label = account_label(self.account_config)
        self._last_key = None

    def _final_rows(self, key):
        """Every attempt under ``key`` that logged an outcome, in ledger order (the ledger is the truth)."""
        if key is None or not self.ledger.exists():
            return []
        with self.ledger.open(encoding="utf-8") as log:
            fcntl.flock(log, fcntl.LOCK_SH)
            rows = [json.loads(line) for line in log if line.strip()]
        return [r for r in rows if r.get("key") == key and r.get("status") in FINAL]

    def _row_usage(self, row):
        return {**_attempt_usage(row), "model": row.get("served_model"),
                "account_label": row.get("account_label", self.account_label), "call_key": row.get("key")}

    def _account(self, exc):
        """Attach to a failure the usage of EVERY backend attempt under its key, read from the ledger.

        A failure after a call started carries that attempt's usage; its earlier attempts are the
        ``prior_attempts``. A rejection BEFORE any call started (call budget, drift, a key that may not
        be re-run) spent nothing itself: the latest logged attempt under the key becomes the reported
        call and the rest its ``prior_attempts``, so spent tokens and the key are never dropped. With no
        logged attempt at all the call is ``not_started`` (zero tokens)."""
        spent = getattr(exc, "usage", None)
        key = spent.get("call_key") if type(spent) is dict and spent.get("call_key") else self._last_key
        finals = self._final_rows(key)
        if type(spent) is dict and not spent.get("not_started"):
            exc.usage = {**spent, "prior_attempts": [_attempt_usage(r) for r in finals[:-1]]}
        elif finals:
            exc.usage = {**self._row_usage(finals[-1]), "rejected_before_start": True,
                         "prior_attempts": [_attempt_usage(r) for r in finals[:-1]]}
        else:
            exc.usage = {"input_tokens": 0, "output_tokens": 0, "model": None,
                         "account_label": self.account_label, "call_key": key, "not_started": True,
                         "prior_attempts": []}
        return exc

    def sample(self, item_id, system, prompt, sample_index=0, *, content_tokens=None):
        """One sample. Every earlier attempt under the same key logged in the ledger (infrastructure
        retries, in this call or in an earlier, paused one) is returned as ``prior_attempts`` -- on the
        reply, or in the final error's ``usage`` -- so the caller can account for every token spent."""
        for attempt in range(1 + (len(RETRY_BACKOFF) if self.infrastructure_retries else 0)):
            self._last_key = None
            try:
                row = self._sample_once(item_id, system, prompt, sample_index,
                                        content_tokens=content_tokens, retry_number=attempt)
            except InfrastructureError as exc:
                if self.infrastructure_retries and attempt < len(RETRY_BACKOFF):
                    continue
                if self.infrastructure_retries:
                    paused = InfrastructurePaused("Infrastructure retries exhausted; resume the same request")
                    paused.usage = getattr(exc, "usage", None)
                    raise self._account(paused) from exc
                raise self._account(exc)
            except EndpointError as exc:
                raise self._account(exc)
            else:
                finals = self._final_rows(row.get("key"))
                return {**row, "prior_attempts": [_attempt_usage(r) for r in finals[:-1]]}

    def _sample_once(self, item_id, system, prompt, sample_index=0, *, content_tokens=None, retry_number=0):
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        # Lock covers read/check/intent/call/result, preventing concurrent duplicate spend.
        with self.ledger.open("a+", encoding="utf-8") as log:
            fcntl.flock(log, fcntl.LOCK_EX)
            log.seek(0)
            try:
                history = [json.loads(line) for line in log if line.strip()]
            except json.JSONDecodeError as exc:
                raise EndpointError("Damaged ledger; preserve it and repair explicitly") from exc
            if any(r.get("account_label") != self.account_label for r in history):
                raise EndpointError("Account mismatch or unattributed legacy ledger; use a separately named ledger")
            executable = shutil.which("claude")
            if not executable:
                raise EndpointError("claude not found")
            binary_hash = hashlib.sha256(Path(executable).read_bytes()).hexdigest()
            control = {**asdict(self.controls), "binary_sha256": binary_hash, "backend_revision": 4,
                       "host_system": platform.system(), "host_release": platform.release(),
                       "shell": "/bin/sh", "locale": "en_US.UTF-8", "timezone": "UTC"}
            group = digest([self.account_label, control, system, prompt, content_tokens])
            key = digest([group, item_id, sample_index])
            self._last_key = key
            matching = [r for r in history if r.get("key") == key and r["status"] != "retry_scheduled"]
            if matching:
                if matching[-1]["status"] == "ok":
                    return matching[-1]
                last = matching[-1]
                retryable = last["status"] == "infrastructure_error" or (
                    last["status"] == "error" and bool(last.get("infrastructure_reason") or (
                        "raw_stream" in last and infrastructure_failure(  # legacy rows only
                            last["raw_stream"], self.controls.model, last.get("error", "")))))
                if not (self.infrastructure_retries and retryable):
                    raise EndpointError("Sample previously started or failed; explicit new sample id required")
            if self.max_calls is not None and sum(r["status"] == "started" for r in history) >= self.max_calls:
                raise EndpointError("Call budget exhausted")
            version = subprocess.check_output([executable, "--version"], text=True).strip()
            if version != self.controls.cli_version:
                raise EndpointError(f"CLI version drift: {version}")
            prior = [r for r in history if r["status"] == "started"]
            if prior and prior[0]["controls"] != control:
                raise EndpointError("Controls/binary drift; start a separately named ledger")
            check_context_date(self.controls)
            token = oauth_token(self.account_config)
            base = {"key": key, "item_id": item_id, "sample_index": sample_index,
                    "prompt_group": group, "system": system, "prompt": prompt,
                    "controls": control, "content_tokens": content_tokens,
                    "account_label": self.account_label}
            def append(row):
                log.write(json.dumps(row, ensure_ascii=False) + "\n")
                log.flush()
                os.fsync(log.fileno())
            if matching:
                delay = RETRY_BACKOFF[retry_number - 1] if retry_number else RETRY_BACKOFF[0]
                append({**base, "status": "retry_scheduled", "timestamp": now(),
                        "retry_number": retry_number, "backoff_s": delay,
                        "resumed": retry_number == 0, "previous_status": matching[-1]["status"],
                        "classification": "INFRASTRUCTURE", "counts_as_sample": False})
                print(json.dumps({"event": "infrastructure_retry", "item_id": item_id,
                                  "sample_index": sample_index, "retry_number": retry_number,
                                  "backoff_s": delay}), flush=True)
                time.sleep(delay)
                check_context_date(self.controls)
            append({**base, "status": "started", "timestamp": now(), "retry_number": retry_number})
            start = time.monotonic()
            raw = ""
            parsed = {}
            try:
                with empty_working_directory(self.controls.working_directory) as cwd, tempfile.TemporaryDirectory(prefix="ve-claude-v4-") as tmp:
                    root = Path(tmp)
                    config, home = (root / n for n in ("config", "home"))
                    for p in (config, home):
                        p.mkdir(mode=0o700)
                    mcp = root / "empty-mcp.json"
                    mcp.write_text('{"mcpServers":{}}')
                    # Only the OAuth access token is copied into the child environment.
                    # No account preferences, refresh token, settings, or memory are copied.
                    env = isolated_env(os.environ, config, home, token, self.controls)
                    proc = subprocess.run(command(executable, self.controls, system, mcp),
                                          input=prompt, text=True, capture_output=True, cwd=cwd,
                                          env=env, timeout=self.controls.timeout_s)
                    raw = proc.stdout
                    reason = infrastructure_failure(raw, self.controls.model, proc.stderr if proc.returncode else "")
                    if reason:
                        raise InfrastructureError(reason)
                    if proc.returncode:
                        raise EndpointError(f"CLI exit {proc.returncode}")
                    parsed = parse_stream(raw, self.controls.model)
                    check_context_date(self.controls)
                overhead = None if content_tokens is None else parsed["input_tokens"] - content_tokens
                comparable = [r for r in history if r["status"] == "ok" and r["prompt_group"] == group]
                if any(r["input_tokens"] != parsed["input_tokens"] for r in comparable):
                    raise EndpointError("Input overhead drift for identical content")
                measured = [r for r in history if r["status"] == "ok" and r.get("overhead_tokens") is not None]
                if overhead is not None and any(r["overhead_tokens"] != overhead for r in measured):
                    raise EndpointError("Absolute input overhead drift")
                row = {**base, **parsed, "overhead_tokens": overhead, "status": "ok",
                       "timestamp": now(), "elapsed_s": time.monotonic()-start,
                       **stream_digest(raw), **stream_records(raw, token)}
            except Exception as exc:
                # Never include environment/credentials; stdout is model protocol data only, and it is
                # persisted only as decoded, sanitized records plus a digest (never as raw text).
                raw_bytes = raw
                if isinstance(exc, (ConnectionError, subprocess.TimeoutExpired)):
                    if isinstance(exc, subprocess.TimeoutExpired) and exc.stdout:
                        raw_bytes = exc.stdout
                        raw = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout
                    if infrastructure_failure(raw, self.controls.model, str(exc)) or isinstance(exc, ConnectionError):
                        exc = InfrastructureError("connection error or empty timed-out stream")
                # Usage is taken from the stream even when validation rejected it (e.g. truncation).
                parsed = parsed or reported_usage(raw)
                if parsed.get("served_model") is not None:
                    parsed = {**parsed, "served_model": redact(parsed["served_model"], token)}
                if parsed.get("reported_models"):
                    parsed = {**parsed, "reported_models": [redact(m, token) for m in parsed["reported_models"]]}
                failed = {**base, **parsed, "status": "infrastructure_error" if isinstance(exc, InfrastructureError) else "error",
                          "classification": "INFRASTRUCTURE" if isinstance(exc, InfrastructureError) else "ENDPOINT",
                          "counts_as_sample": False, "retry_number": retry_number,
                          "timestamp": now(), "error": redact(exc, token),
                          "infrastructure_reason": infrastructure_failure(raw, self.controls.model, str(exc)),
                          "elapsed_s": time.monotonic()-start,
                          **stream_digest(raw_bytes), **stream_records(raw, token)}
                # Every decoded string (dict keys included) is sanitized exactly as on the success path.
                failed = sanitize(failed, token)
                append(failed)
                # The caller gets a sanitized copy (never the original, whose message or context may
                # echo credentials), carrying the usage actually spent so it can be logged.
                failure = sanitized_error(exc, token)
                failure.usage = {"input_tokens": failed.get("input_tokens"),
                                 "output_tokens": failed.get("output_tokens"),
                                 "model": failed.get("served_model"),
                                 "account_label": self.account_label,
                                 "call_key": key}
            else:
                failure = None
            if failure is not None:
                raise failure
            # Defence in depth against credential echo in model protocol data (decoded strings, recursively).
            row = sanitize(row, token)
            append(row)
            return row

    def samples(self, item_id, system, prompt, k=3):
        if k < 1:
            raise ValueError("k must be positive")
        return [self.sample(item_id, system, prompt, i) for i in range(k)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--account-config-dir", help="Auth source only; defaults to VE_CLAUDE_ACCOUNT_CONFIG_DIR")
    args = p.parse_args()
    client = ClaudeCLI(args.audit, max_calls=12, account_config_dir=args.account_config_dir)
    for i in range(5):
        for label, prompt in (("canary", CANARY), ("trivial", "Reply with exactly OK.")):
            try:
                row = client.sample(label, SYSTEM, prompt, i)
            except EndpointError as exc:
                print(json.dumps({"item_id": label, "sample_index": i, "error": str(exc)}), flush=True)
                continue
            print(json.dumps({k: row[k] for k in ("item_id", "sample_index", "served_model", "input_tokens", "text")}), flush=True)


if __name__ == "__main__":
    main()
