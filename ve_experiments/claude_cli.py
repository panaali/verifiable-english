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

from ve import stream_audit

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


# Credential-like substrings for error messages (same patterns as ve/assist/proposer.py).
_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{6,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}(?:\.[A-Za-z0-9_\-]*)?"),
    re.compile(r"(?i)\bbearer\s+[^\s'\",;\]]+"),
    re.compile(r"(?i)\b([a-z_]*(?:token|secret|password|api_?key|credential)[a-z_]*)\s*[:=]\s*[^\s'\",;\]]{8,}"),
    re.compile(r"(?<![A-Za-z0-9_\-])(?=[A-Za-z0-9_\-]*[0-9])(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{32,}"),
)


def redact(text, token=None):
    """Remove the live token (and its encodings) and anything else that looks like a credential."""
    text = str(text)
    if token:
        text = text.replace(token, "[REDACTED]")
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return sanitize(text, token)


def sanitize(value, token):
    """The canonical sanitizer (``ve.stream_audit.sanitize``) with this token's needles: every string,
    recursively (dict keys included), decoded to a fixpoint under every supported encoding."""
    return stream_audit.sanitize(value, stream_audit.needles_for(token))


def stream_digest(raw):
    """SHA-256 of the raw stream bytes (the stream itself is never persisted) and its size."""
    data = raw if isinstance(raw, bytes) else str(raw).encode("utf-8", errors="surrogateescape")
    return {"raw_stream_sha256": hashlib.sha256(data).hexdigest(), "raw_stream_bytes": len(data)}


def stream_records(raw, token):
    """The stream's JSON records, decoded then sanitized; undecodable lines are counted, not kept."""
    lines = [line for line in str(raw).splitlines() if line.strip()]
    records = stream_audit.records_from_raw(raw)
    return {"stream_records": sanitize(records, token), "unparsed_lines": len(lines) - len(records)}


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


class RetryRefused(EndpointError):
    """The caller's ``before_retry`` gate (e.g. a per-item budget) refused another backend attempt."""


RETRY_BACKOFF = (30, 60, 120, 240, 480)


def _dicts(value):
    """The dict elements of ``value`` if it is a list, else none (total over arbitrary JSON)."""
    return [v for v in value if type(v) is dict] if type(value) is list else []


def _as_dict(value):
    return value if type(value) is dict else {}


def _stream_identity(raw):
    """``(records, assistants, results, real_models, init_models, synthetic)`` of a raw stream.

    TOTAL over arbitrary JSON: non-dict records (null, arrays, scalars) are skipped, a non-dict
    ``message`` or ``modelUsage`` contributes nothing, and only string model names count (a list- or
    dict-valued model is ignored, never hashed). Usage is extracted separately
    (``stream_audit.stream_usage``), so no malformed record can make classification lose it."""
    records = [r for r in stream_audit.records_from_raw(raw) if type(r) is dict]
    assistants = [_as_dict(r.get("message")) for r in records if r.get("type") == "assistant"]
    results = [r for r in records if r.get("type") == "result"]
    real = {m.get("model") for m in assistants
            if type(m.get("model")) is str and m.get("model") != "<synthetic>"}
    real.update(k for r in results for k in _as_dict(r.get("modelUsage"))
                if type(k) is str and k != "<synthetic>")
    init_models = {r.get("model") if type(r.get("model")) is str else repr(r.get("model"))
                   for r in records if r.get("subtype") == "init" and r.get("model") is not None}
    synthetic = any(m.get("model") == "<synthetic>" for m in assistants)
    return records, assistants, results, real, init_models, synthetic


def infrastructure_failure(raw, expected_model, diagnostic=""):
    """Classify protocol errors without mistaking model prose for network errors.

    A real alternate model always wins over a simultaneous transport failure.
    Init is requested identity, not evidence that a model served a response.
    Total over arbitrary stream content: it never raises on malformed records.
    """
    raw = raw if isinstance(raw, str) else str(raw or "")
    if not raw.strip():
        return "empty stream"
    records, assistants, results, real, init_models, synthetic = _stream_identity(raw)
    if (real | init_models) - {expected_model}:
        return None
    if synthetic and not real:
        return "synthetic placeholder without a served model"
    errors = [str(diagnostic)]
    errors.extend(str(r.get("result", "")) for r in results if r.get("is_error"))
    errors.extend(str(b.get("text", "")) for m in assistants if m.get("model") == "<synthetic>"
                  for b in _dicts(m.get("content")))
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


USAGE_KEYS = stream_audit.USAGE_KEYS


def reported_usage(raw):
    """Usage the stream reports, extracted leniently BEFORE any validation (so a truncated or otherwise
    rejected response still accounts for the tokens it spent).

    Counted usage is ``ve.stream_audit.stream_usage``: the field-wise MAX over EVERY usage-bearing record
    (each result record and each assistant message), for well-formed and malformed streams alike, so no
    later record can erase what an earlier one reported. ``ve.assist.verify`` recomputes it from the
    stored ``stream_records``."""
    raw = raw if isinstance(raw, str) else str(raw or "")
    # Usage FIRST and independently of identity: a malformed record can never cost the spend.
    usage = stream_audit.stream_usage(stream_audit.records_from_raw(raw))
    try:
        models = sorted(_stream_identity(raw)[3])
    except Exception:  # identity is best effort; usage is not
        models = []
    out = {"served_model": models[0] if len(models) == 1 else None, "reported_models": models}
    if usage:
        counted_input, counted_output = stream_audit.usage_totals(usage)
        if counted_input is not None:
            out["input_tokens"] = counted_input
        if counted_output is not None:
            out["output_tokens"] = counted_output
        out["usage"] = usage
    return out


def parse_stream(raw, expected_model):
    """Validate a complete stream. Any malformation surfaces as an EndpointError (never another type)."""
    try:
        return _parse_stream(raw, expected_model)
    except EndpointError:
        raise
    except Exception as exc:
        raise EndpointError(f"Malformed stream ({type(exc).__name__})") from None


def _parse_stream(raw, expected_model):
    reason = infrastructure_failure(raw, expected_model)
    if reason:
        raise InfrastructureError(reason)
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if any(type(r) is not dict for r in records):
        raise EndpointError("Malformed stream record (not a JSON object)")
    if any(r.get("type") == "assistant" and (type(r.get("message")) is not dict
                                             or type(r["message"].get("content", [])) is not list
                                             or type(r["message"].get("model")) is not str)
           for r in records):
        raise EndpointError("Malformed assistant record")
    if any(r.get("type") == "result" and type(r.get("modelUsage", {})) is not dict for r in records):
        raise EndpointError("Malformed result record")
    if any(r.get("subtype") == "init" and type(r.get("model")) is not str for r in records):
        raise EndpointError("Malformed init record")
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
    if any(type(b) is not dict or b.get("type") not in ("text", "thinking", "redacted_thinking")
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
    # Counted usage: field-wise max over every usage-bearing record (see reported_usage).
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
        # Needles of every token this client handed to a child (in memory only, never persisted), so
        # the canonical sanitizer can be applied by the caller too (``secret_needles``).
        self._needles = stream_audit.needles_for(None)

    def secret_needles(self):
        return self._needles

    def _ledger_rows(self):
        if not self.ledger.exists():
            return []
        with self.ledger.open(encoding="utf-8") as log:
            fcntl.flock(log, fcntl.LOCK_SH)
            rows = []
            for line in log:
                try:
                    rows.append(json.loads(line)) if line.strip() else None
                except ValueError:
                    continue
        return [r for r in rows if type(r) is dict]

    def _final_rows(self, key):
        """Every attempt under ``key`` that logged an outcome, in ledger order (the ledger is the truth)."""
        if key is None:
            return []
        return [r for r in self._ledger_rows() if r.get("key") == key and r.get("status") in FINAL]

    def _key_for(self, request):
        """The key of the latest logged attempt of this exact request (item, sample, system, prompt,
        content tokens, account), found WITHOUT the binary: identity survives a missing or broken CLI."""
        item_id, sample_index, system, prompt, content_tokens = request
        rows = [r for r in self._ledger_rows()
                if (r.get("item_id"), r.get("sample_index"), r.get("system"), r.get("prompt"),
                    r.get("content_tokens"), r.get("account_label")) ==
                (item_id, sample_index, system, prompt, content_tokens, self.account_label) and r.get("key")]
        return rows[-1]["key"] if rows else None

    def _row_usage(self, row):
        return {**_attempt_usage(row), "model": row.get("served_model"),
                "account_label": row.get("account_label", self.account_label), "call_key": row.get("key")}

    def _account(self, exc, request):
        """Attach to a failure the usage of EVERY backend attempt under its key, read from the ledger.

        The key is the failing attempt's, else the key computed earlier in this ``sample`` call, else
        the key of the latest logged attempt of the same request (so a preflight failure -- no ``claude``
        binary, a failing ``claude --version`` -- before the key could be recomputed still keeps it).
        A failure after a call started carries that attempt's usage; its earlier attempts are the
        ``prior_attempts``. A rejection BEFORE any call started spent nothing itself: the latest logged
        attempt under the key becomes the reported call and the rest its ``prior_attempts``, so spent
        tokens and the key are never dropped. With no logged attempt at all the call is ``not_started``."""
        spent = getattr(exc, "usage", None)
        if type(spent) is dict and spent.get("call_key"):
            key = spent["call_key"]
        else:  # the first identity with logged attempts (a changed binary changes the recomputed key)
            keys = [k for k in (self._last_key, self._key_for(request)) if k]
            key = next((k for k in keys if self._final_rows(k)), keys[0] if keys else None)
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
        exc.usage = stream_audit.sanitize(exc.usage, self._needles)
        return exc

    def sample(self, item_id, system, prompt, sample_index=0, *, content_tokens=None):
        """One sample. Every earlier attempt under the same key logged in the ledger (infrastructure
        retries, in this call or in an earlier, paused one) is returned as ``prior_attempts`` -- on the
        reply, or in the final error's ``usage`` -- so the caller can account for every token spent.

        EVERY exit path goes through ``_account``: endpoint errors, infrastructure errors, and any other
        exception (a failing ``claude --version``, unreadable credentials) as a sanitized EndpointError."""
        request = (item_id, sample_index, system, prompt, content_tokens)
        self._last_key = None  # once per sample: a retry keeps the key its earlier attempts computed
        failure = None
        for attempt in range(1 + (len(RETRY_BACKOFF) if self.infrastructure_retries else 0)):
            gate = getattr(self, "before_retry", None)
            if attempt and gate is not None and not gate([_attempt_usage(r) for r in self._final_rows(self._last_key)]):
                # the caller's budget cannot cover another backend attempt: stop, accounted like any failure
                failure = RetryRefused("the caller's budget gate refused an infrastructure retry")
                break
            try:
                row = self._sample_once(item_id, system, prompt, sample_index,
                                        content_tokens=content_tokens, retry_number=attempt)
            except InfrastructureError as exc:
                if self.infrastructure_retries and attempt < len(RETRY_BACKOFF):
                    continue
                if self.infrastructure_retries:
                    failure = InfrastructurePaused("Infrastructure retries exhausted; resume the same request")
                    failure.usage = getattr(exc, "usage", None)
                else:
                    failure = exc
            except EndpointError as exc:
                failure = exc
            except Exception as exc:  # never escapes unaccounted, never with its original context
                failure = sanitized_error(exc)
                failure = EndpointError(stream_audit.sanitize(str(failure), self._needles))
            else:
                finals = self._final_rows(row.get("key"))
                return {**row, "prior_attempts": [_attempt_usage(r) for r in finals[:-1]]}
            break
        # Raised outside the except blocks: no __context__ chain back to an unsanitized original.
        raise self._account(failure, request)

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
            self._needles = self._needles | stream_audit.needles_for(token)
            base = {"key": key, "item_id": item_id, "sample_index": sample_index,
                    "prompt_group": group, "system": system, "prompt": prompt,
                    "controls": control, "content_tokens": content_tokens,
                    "account_label": self.account_label}
            def append(row):
                # Every persisted row passes through the canonical sanitizer, whatever its status.
                row = sanitize(row, token)
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
                # Usage is taken from the stream even when validation rejected it (e.g. truncation), and
                # FIRST: nothing below (classification, identity, records) may cost the usage already seen.
                if not parsed:
                    try:
                        parsed = reported_usage(raw)
                    except Exception:
                        parsed = {}
                is_infra = isinstance(exc, InfrastructureError)
                try:
                    reason = infrastructure_failure(raw, self.controls.model, str(exc))
                except Exception:
                    reason = None
                try:
                    records = stream_records(raw, token)
                except Exception:
                    records = {"stream_records": [], "unparsed_lines": None}
                identity = {}
                if parsed.get("served_model") is not None:
                    identity["served_model"] = redact(parsed["served_model"], token)
                if type(parsed.get("reported_models")) is list:
                    identity["reported_models"] = [redact(m, token) for m in parsed["reported_models"]]
                failed = {**base, **parsed, **identity,
                          "status": "infrastructure_error" if is_infra else "error",
                          "classification": "INFRASTRUCTURE" if is_infra else "ENDPOINT",
                          "counts_as_sample": False, "retry_number": retry_number,
                          "timestamp": now(), "error": redact(exc, token),
                          "infrastructure_reason": reason,
                          "elapsed_s": time.monotonic()-start,
                          **stream_digest(raw_bytes), **records}
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
