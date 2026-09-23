"""Audited subscription endpoint. One fresh process per attempt; infrastructure retries are opt-in.

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
import re
from pathlib import Path
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
    if re.search(r"(?:http(?:/\d(?:\.\d)?)?\s*|status(?:_code)?[\s:=]+|api error[\s:]+)(5\d\d)\b", message):
        return "HTTP 5xx"
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
            "--permission-mode", "dontAsk", "--effort", controls.effort,
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
               CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK="1")
    if controls.thinking_tokens is not None:
        env.update(MAX_THINKING_TOKENS=str(controls.thinking_tokens),
                   CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING="1")
    return env


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
    usage = result.get("usage", {})
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in keys):
        raise EndpointError("Missing or invalid input usage")
    return {"init": initial, "usage": usage, "model_usage": result.get("modelUsage"),
            "served_model": expected_model, "input_tokens": sum(usage[k] for k in keys),
            "output_tokens": usage.get("output_tokens"),
            "thinking_tokens_reported": usage.get("output_tokens_details", {}).get("thinking_tokens"),
            "stop_reason": result.get("stop_reason"), "text": result["result"]}


class ClaudeCLI:
    def __init__(self, ledger: Path, controls=Controls(), max_calls=None, *, account_config_dir=None, infrastructure_retries=False):
        self.ledger, self.controls, self.max_calls = Path(ledger), controls, max_calls
        self.infrastructure_retries = infrastructure_retries
        self.account_config = account_config(account_config_dir)
        self.account_label = account_label(self.account_config)

    def sample(self, item_id, system, prompt, sample_index=0, *, content_tokens=None):
        prior = [json.loads(line) for line in self.ledger.read_text().splitlines()] if self.ledger.exists() else []
        matching = [r for r in prior if r.get('item_id') == item_id and r.get('sample_index') == sample_index and r.get('status') != 'retry_scheduled']
        resumed = self.infrastructure_retries and (getattr(self, 'resume_pending', False) or bool(matching and matching[-1]['status'] in ('error', 'infrastructure_error')))
        self.resume_pending = False
        for attempt in range(1 if resumed else 0, 1 + (len(RETRY_BACKOFF) if self.infrastructure_retries else 0)):
            try:
                return self._sample_once(item_id, system, prompt, sample_index,
                                         content_tokens=content_tokens, retry_number=attempt)
            except InfrastructureError as exc:
                if not self.infrastructure_retries:
                    raise
                if attempt == len(RETRY_BACKOFF):
                    raise InfrastructurePaused("Infrastructure retries exhausted; resume the same request") from exc

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
            matching = [r for r in history if r.get("key") == key and r["status"] != "retry_scheduled"]
            if matching:
                if matching[-1]["status"] == "ok":
                    return matching[-1]
                last = matching[-1]
                retryable = last["status"] == "infrastructure_error" or (
                    last["status"] == "error" and infrastructure_failure(
                        last.get("raw_stream", ""), self.controls.model, last.get("error", "")))
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
            if matching or retry_number:
                delay = RETRY_BACKOFF[retry_number - 1] if retry_number else RETRY_BACKOFF[0]
                append({**base, "status": "retry_scheduled", "timestamp": now(),
                        "retry_number": retry_number, "backoff_s": delay,
                        "resumed": retry_number == 0, "previous_status": matching[-1]["status"] if matching else "prior_date_infrastructure_error",
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
                       "raw_stream": raw}
            except Exception as exc:
                # Never include environment/credentials; stdout is model protocol data only.
                raw = raw.replace(token, "[REDACTED]")
                if isinstance(exc, (ConnectionError, subprocess.TimeoutExpired)):
                    if isinstance(exc, subprocess.TimeoutExpired) and exc.stdout:
                        raw = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout
                        raw = raw.replace(token, "[REDACTED]")
                    if infrastructure_failure(raw, self.controls.model, str(exc)) or isinstance(exc, ConnectionError):
                        exc = InfrastructureError("connection error or empty timed-out stream")
                append({**base, **parsed, "status": "infrastructure_error" if isinstance(exc, InfrastructureError) else "error",
                        "classification": "INFRASTRUCTURE" if isinstance(exc, InfrastructureError) else "ENDPOINT",
                        "counts_as_sample": False, "retry_number": retry_number,
                        "timestamp": now(), "error": str(exc).replace(token, "[REDACTED]"),
                        "raw_stream": raw, "elapsed_s": time.monotonic()-start})
                raise exc
            # Defence in depth against accidental credential echo in model protocol data.
            row = json.loads(json.dumps(row).replace(token, "[REDACTED]"))
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
