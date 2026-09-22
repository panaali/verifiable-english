"""Serial native-role API calls with durable, fail-closed dollar reservations.

No credential files are inspected. Vertex uses ADC; OpenRouter uses only the
process environment. Unknown billing is never interpreted as a free request.
"""
from __future__ import annotations

import asyncio
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, replace
from decimal import Decimal
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time

MODELS = {"pro": "gemini-3.1-pro-preview",
          "replication": "qwen/qwen-2.5-72b-instruct",
          "weak": "meta-llama/llama-3.1-8b-instruct"}
RATES = {"pro": ("2", "12", "1"), "replication": (".36", ".40", "1.055"),
         "weak": (".02", ".04", "1.055")}


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(packed(value).encode()).hexdigest()


def cost(model, inp, output):
    if any(type(v) is not int or v < 0 for v in (inp, output)):
        raise ValueError("token counts must be nonnegative integers")
    ri, ro, fee = map(Decimal, RATES[model])
    return (Decimal(inp) * ri + Decimal(output) * ro) * fee / Decimal(1000000)


class PreflightError(RuntimeError):
    pass


class InfrastructureError(PreflightError):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class ToolEndpointUnavailable(InfrastructureError):
    """Dispatch rejected before generation; not a scientific observation."""


def no_tool_endpoint(error):
    return "No endpoints found that support tool use" in str(error)


def infrastructure_status(exc):
    import httpx
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if isinstance(exc, (TimeoutError, httpx.TimeoutException)):
        return "timeout"
    if status == 429 or isinstance(status, int) and 500 <= status <= 599:
        return status
    return None


def smoke(request):
    return request.identity.startswith("provider-preflight/") or request.metadata.get("role") == "probe"


def revision_key(model, response):
    return model + "/" + str(response.get("provider")) if model == "weak" else model


class BudgetExceeded(PreflightError):
    """CLI maps this to exit status 3."""


@dataclass(frozen=True)
class PaidRequest:
    identity: str
    model: str
    messages: list[dict]
    max_input_tokens: int
    max_output_tokens: int
    tools: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    timeout_s: float = 120


@dataclass
class PaidReply:
    text: str
    input_tokens: int
    output_tokens: int  # visible candidates; excludes thinking
    thinking_tokens: int
    cached_tokens: int
    revision: str
    response: dict
    assistant: dict
    tool_calls: list[dict] = field(default_factory=list)
    finish_reason: str = ""
    provider_cost_usd: float | None = None
    latency_s: float = 0

    @property
    def billed_output_tokens(self):
        return self.output_tokens + self.thinking_tokens


class Ledger:
    def __init__(self, path, cap_usd):
        self.path = Path(path)
        self.cap = Decimal(str(cap_usd))
        if not self.cap.is_finite() or self.cap <= 0:
            raise ValueError("cap must be finite and positive")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def locked(self):
        with self.path.open("a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                rows = [json.loads(line) for line in f]
                yield f, rows
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    @staticmethod
    def append(f, row):
        f.seek(0, 2)
        f.write(packed({"time": time.time(), **row}) + "\n")
        f.flush()
        os.fsync(f.fileno())

    @staticmethod
    def state(rows):
        pending, committed, seen, revisions = {}, Decimal(0), set(), {}
        reservations = {}
        blocked = False
        recovered = {r["halt_time"] for r in rows if r["event"] in ("smoke_recovery", "routing_recovery")}
        for row in rows:
            if row["event"] == "reserve":
                pending[row["identity"]] = Decimal(row["ceiling_usd"])
                seen.add(row["identity"])
                reservations[row["identity"]] = row
                block = row.get("metadata", {}).get("block_id")
                if block:
                    pending["block:" + block] -= Decimal(row["ceiling_usd"])
            elif row["event"] == "complete":
                ceiling = pending.pop(row["identity"])
                committed += Decimal(row["cost_usd"])
                revisions.setdefault(revision_key(row["model"], row.get("response", {})), row["revision"])
                block = reservations[row["identity"]].get("metadata", {}).get("block_id")
                if block:
                    pending["block:" + block] += ceiling - Decimal(row["cost_usd"])
            elif row["event"] in ("infrastructure_failure", "smoke_recovery", "routing_recovery", "panel_halt", "arm_unavailable"):
                ceiling = pending.pop(row["identity"])
                held = Decimal(row["infrastructure_hold_usd"])
                committed += held
                block = reservations[row["identity"]].get("metadata", {}).get("block_id")
                if block:
                    pending["block:" + block] += ceiling - held
            elif row["event"] == "halt":
                if row["time"] not in recovered:
                    blocked = True
            elif row["event"] == "block_reserve":
                pending["block:" + row["block_id"]] = Decimal(row["ceiling_usd"])
            elif row["event"] == "block_release":
                pending.pop("block:" + row["block_id"])
            elif row["event"] == "allowance":
                committed += Decimal(row["cost_usd"])
        return pending, committed, seen, revisions, blocked

    def allowance(self, identity, amount):
        """Persist reserved envelopes that cannot fund additional samples."""
        with self.locked() as (f, rows):
            if any(r.get("event") == "allowance" and r["identity"] == identity for r in rows):
                return
            pending, spent, _, _, blocked = self.state(rows)
            if blocked or pending:
                raise PreflightError("ledger not available for allowance")
            if spent + Decimal(str(amount)) > self.cap:
                raise BudgetExceeded("envelope exceeds --cap-usd")
            self.append(f, {"event": "allowance", "identity": identity, "cost_usd": str(amount)})

    def reserve_block(self, block_id, ceiling, *, resume=False):
        with self.locked() as (f, rows):
            pending, spent, _, _, blocked = self.state(rows)
            prior = next((r for r in rows if r['event'] == 'block_reserve' and r['block_id'] == block_id), None)
            if resume and prior:
                if Decimal(prior['ceiling_usd']) != Decimal(str(ceiling)):
                    raise PreflightError('resumed block ceiling changed')
                if blocked or any(k != 'block:' + block_id for k in pending):
                    raise PreflightError('ledger halted or has unreconciled billing')
                if spent + sum(pending.values()) > self.cap:
                    raise BudgetExceeded('resumed commitments exceed --cap-usd')
                return  # A released block may only replay its already completed calls.
            if pending or blocked:
                raise PreflightError("ledger halted or another block/billing reservation exists")
            if any(r.get("event") == "block_reserve" and r["block_id"] == block_id for r in rows):
                raise PreflightError("block already assigned; no replacement samples")
            if spent + Decimal(str(ceiling)) > self.cap:
                raise BudgetExceeded("complete block ceiling would exceed --cap-usd")
            self.append(f, {"event": "block_reserve", "block_id": block_id, "ceiling_usd": str(ceiling)})

    def release_block(self, block_id):
        with self.locked() as (f, rows):
            pending, _, _, _, blocked = self.state(rows)
            if blocked or any(not k.startswith("block:") for k in pending):
                raise PreflightError("cannot release block while billing unresolved")
            if 'block:' + block_id not in pending:
                return
            self.append(f, {"event": "block_release", "block_id": block_id})

    def require_block(self, ceiling):
        with self.locked() as (_, rows):
            pending, spent, _, _, blocked = self.state(rows)
            if pending or blocked:
                raise PreflightError("ledger halted or has unreconciled billing; dispatch forbidden")
            if spent + Decimal(str(ceiling)) > self.cap:
                raise BudgetExceeded("complete block ceiling would exceed --cap-usd")

    def reserve(self, request):
        if request.max_input_tokens <= 0 or request.max_output_tokens <= 0:
            raise ValueError("request token ceilings must be positive")
        ceiling = cost(request.model, request.max_input_tokens, request.max_output_tokens)
        with self.locked() as (f, rows):
            pending, spent, seen, revisions, blocked = self.state(rows)
            history = [r for r in rows if r.get("identity") == request.identity]
            for row in rows:
                if row['event'] in ('panel_halt', 'panel_validation_halt') and row['model'] == request.model:
                    raise InfrastructureError(row['error'])
                if row['event'] == 'arm_unavailable' and row['model'] == request.model and request.metadata.get('arm') == row['arm']:
                    raise ToolEndpointUnavailable(row['error'])
            failures = sum(r["event"] == "infrastructure_failure" for r in history)
            retry = history and (history[-1]['event'] == 'routing_recovery' or
                                history[-1]["event"] == "infrastructure_failure" and failures <= 3)
            if failures > 3 and history[-1]["event"] == "infrastructure_failure":
                raise InfrastructureError("infrastructure retry limit exhausted")
            if request.identity in seen and not (smoke(request) or retry):
                raise PreflightError("assignment already dispatched; paid retries are forbidden")
            if retry:
                prior = next(r for r in reversed(history) if r["event"] == "reserve")
                if any(prior[k] != asdict(request)[k] for k in asdict(request)):
                    raise PreflightError("infrastructure retry changed frozen request")
            block = request.metadata.get("block_id")
            block_key = "block:" + block if block else None
            if blocked or any(k != block_key for k in pending):
                raise PreflightError("ledger halted or has unreconciled billing; dispatch forbidden")
            if block and (block_key not in pending or pending[block_key] < ceiling):
                raise BudgetExceeded("call ceiling exceeds reserved block remainder")
            if spent + sum(pending.values()) + (Decimal(0) if block else ceiling) > self.cap:
                raise BudgetExceeded("committed cost plus call ceiling exceeds --cap-usd")
            self.append(f, {"event": "reserve", **asdict(request), "ceiling_usd": str(ceiling),
                            "remaining_usd": str(self.cap - spent - ceiling),
                            "prompt_sha256": digest(request.messages), "planned_model": MODELS[request.model]})
            return revisions

    def complete(self, request, reply, error=None, *, panel_only=False):
        actual = cost(request.model, reply.input_tokens, reply.billed_output_tokens)
        if reply.provider_cost_usd is not None:
            actual = max(actual, Decimal(str(reply.provider_cost_usd)) * Decimal(RATES[request.model][2]))
        # Design-table accounting charges cached input at full rate; provider billing
        # is a separate reconciliation field, never an assumed cache discount.
        with self.locked() as (f, rows):
            _, spent, _, _, _ = self.state(rows)
            self.append(f, {"event": "complete", "identity": request.identity,
                            "model": request.model, **asdict(reply),
                            "served_provider": reply.response.get("provider"),
                            "billed_output_tokens": reply.billed_output_tokens,
                            "cost_usd": str(actual), "remaining_usd": str(self.cap - spent - actual),
                            "billing_basis": "maximum of design table (cached input at full rate) and provider billing with fee"})
            if error:
                self.append(f, {"event": "panel_validation_halt" if panel_only else "halt",
                                "identity": request.identity, "model": request.model, "error": error,
                                "sample": False})

    def halt(self, request, error, response=None, latency_s=None):
        with self.locked() as (f, _):
            self.append(f, {"event": "halt", "identity": request.identity, "error": error,
                            "response": response, "latency_s": latency_s,
                            "billing": "unknown; ceiling remains reserved"})

    def cached_reply(self, request):
        """Reuse the original matching output, including malformed trial outputs."""
        with self.locked() as (_, rows):
            reservation = reply = None
            halted = False
            for row in rows:
                if row.get("identity") != request.identity:
                    continue
                if row["event"] == "reserve":
                    reservation, reply, halted = row, None, False
                elif row["event"] == "complete":
                    reply = row
                elif row["event"] in ("halt", "panel_validation_halt"):
                    halted = True
            if reply is not None and not halted:
                for key in ("model", "messages", "tools", "max_input_tokens", "max_output_tokens"):
                    if reservation[key] != getattr(request, key):
                        raise PreflightError("cached smoke request changed" if smoke(request) else "cached trial request changed")
                if not smoke(request) and any(reservation[k] != getattr(request, k) for k in ('metadata', 'timeout_s')):
                    raise PreflightError('cached trial request changed')
                return PaidReply(**{k: reply[k] for k in PaidReply.__dataclass_fields__})
        return None

    def recover_tool_routing(self):
        """Amendment 7: retry only the legacy weak R routing rejection once."""
        with self.locked() as (f, rows):
            recovered = {r['halt_time'] for r in rows if r['event'] == 'routing_recovery'}
            for row in list(rows):
                if row['event'] != 'halt' or row['time'] in recovered or not no_tool_endpoint(row.get('error')):
                    continue
                reservation = next(r for r in reversed(rows) if r['event'] == 'reserve' and r['identity'] == row['identity'])
                if reservation['model'] != 'weak' or reservation['metadata'].get('arm') != 'R' or row.get('response'):
                    continue
                if 'HTTP 404:' not in row['error']:
                    continue
                recovery = {'event': 'routing_recovery', 'identity': row['identity'], 'halt_time': row['time'],
                            'infrastructure_hold_usd': '0', 'sample': False, 'reason': 'Amendment 7 unrestricted weak R routing'}
                self.append(f, recovery)
                rows.append(recovery)

    def stop_panel(self, request, error, *, unavailable=False):
        with self.locked() as (f, rows):
            pending, _, _, _, _ = self.state(rows)
            self.append(f, {'event': 'arm_unavailable' if unavailable else 'panel_halt',
                'identity': request.identity, 'model': request.model, 'arm': request.metadata.get('arm'),
                'error': error, 'sample': False,
                'infrastructure_hold_usd': '0' if unavailable else str(pending[request.identity])})

    def recover_smoke(self, request):
        if not smoke(request):
            return
        with self.locked() as (f, rows):
            recovered = {r["halt_time"] for r in rows if r["event"] == "smoke_recovery"}
            for row in rows:
                if row.get("identity") != request.identity or row["event"] != "halt" or row["time"] in recovered:
                    continue
                pending, _, _, _, _ = self.state(rows)
                if request.identity not in pending:
                    continue  # A completed response that failed validation stays halted.
                free = any(f"HTTP {code}:" in row.get("error", "") for code in (404, 429)) and not row.get("response")
                recovery = {"event": "smoke_recovery", "identity": request.identity,
                    "halt_time": row["time"], "infrastructure_hold_usd": "0" if free else str(pending[request.identity]),
                    "sample": False, "reason": "Amendment 5 smoke exception; original evidence retained"}
                self.append(f, recovery)
                rows.append(recovery)

    def infrastructure_failure(self, request, error, status, latency_s):
        with self.locked() as (f, rows):
            pending, _, _, _, _ = self.state(rows)
            attempt = 1 + sum(r["event"] == "infrastructure_failure" and r["identity"] == request.identity for r in rows)
            self.append(f, {"event": "infrastructure_failure", "identity": request.identity,
                "error": error, "status": status, "attempt": attempt, "sample": False,
                "latency_s": latency_s, "backoff_s": 2 ** (attempt-1) if attempt <= 3 else None,
                "served_provider": None,
                "infrastructure_hold_usd": "0" if status == 429 else str(pending[request.identity]),
                "billing": "no trial charge; 429 rejected" if status == 429 else "unknown; ceiling held as infrastructure overhead"})
            return attempt


def integer(value, name):
    if type(value) is not int or value < 0:
        raise PreflightError(f"missing/invalid API usage: {name}")
    return value


class VertexBackend:
    def __init__(self, client=None):
        from google import genai
        from google.genai import types
        self.client = client or genai.Client(vertexai=True,
            project="project-5ee49d39-f814-4ff7-861", location="global",
            http_options=types.HttpOptions(timeout=120000,
                retry_options=types.HttpRetryOptions(attempts=1)))

    def wire(self, request):
        from google.genai import types
        system, contents = [], []
        for m in request.messages:
            if m["role"] == "system":
                if contents:
                    raise PreflightError("system messages must precede conversation")
                system.append(types.Part(text=m["content"]))
            elif "vertex_content" in m:
                contents.append(types.Content.model_validate(m["vertex_content"]))
            elif m["role"] == "tool":
                contents.append(types.Content(role="user", parts=[types.Part(
                    function_response=types.FunctionResponse(name="replay", id=m["tool_call_id"],
                        response=json.loads(m["content"])))]))
            elif m["role"] in ("user", "assistant"):
                contents.append(types.Content(role="model" if m["role"] == "assistant" else "user",
                                             parts=[types.Part(text=m["content"])]))
            else:
                raise PreflightError("unsupported role")
        cfg = types.GenerateContentConfig(system_instruction=types.Content(parts=system),
            temperature=0, seed=20260921, max_output_tokens=request.max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            tools=[types.Tool(function_declarations=[types.FunctionDeclaration(**t) for t in request.tools])]
                  if request.tools else None)
        return contents, cfg

    def count(self, request):
        from google.genai import types
        contents, cfg = self.wire(request)
        result = self.client.models.count_tokens(model=MODELS[request.model], contents=contents,
            config=types.CountTokensConfig(system_instruction=cfg.system_instruction,
                                          tools=cfg.tools))
        return integer(result.total_tokens, "countTokens.total_tokens")

    async def generate(self, request):
        contents, cfg = self.wire(request)
        response = await self.client.aio.models.generate_content(model=MODELS[request.model],
                                                                 contents=contents, config=cfg)
        data = response.model_dump(mode="json", exclude_none=True)
        self.last_response = data
        u = response.usage_metadata
        if u is None:
            raise PreflightError("missing usage_metadata")
        inp = integer(u.prompt_token_count, "prompt_token_count")
        # Protobuf omits zero scalar fields. Total reconciliation prevents missing
        # candidate/thought fields from silently hiding billed tokens.
        out = integer(u.candidates_token_count or 0, "candidates_token_count")
        thinking = integer(u.thoughts_token_count or 0, "thoughts_token_count")
        if integer(u.total_token_count, "total_token_count") != inp + out + thinking:
            raise PreflightError("Vertex usage does not reconcile prompt + candidates + thoughts")
        if not response.model_version:
            raise PreflightError("Vertex omitted served model revision")
        candidates = response.candidates or []
        content = candidates[0].content if candidates else None
        parts = content.parts or [] if content else []
        calls = [{"id": p.function_call.id or f"replay-{i}", "name": p.function_call.name,
                  "arguments": p.function_call.args} for i, p in enumerate(parts) if p.function_call]
        return PaidReply("".join(p.text for p in parts if p.text and not p.thought), inp, out,
            thinking, integer(u.cached_content_token_count or 0, "cached_content_token_count"),
            response.model_version, data,
            {"role": "assistant", "vertex_content": content.model_dump(mode="json", exclude_none=True)}
            if content else {"role": "assistant", "content": ""}, calls,
            str(candidates[0].finish_reason.value) if candidates else "NO_CANDIDATE")


class OpenRouterBackend:
    """No approximate tokenizer fallback: require a verified native wire counter.

    OpenRouter has no joint countTokens endpoint. The execution freeze must
    supply a validated provider chat-template counter (including tools).
    """
    def __init__(self, counter=None):
        self.counter = counter

    def wire(self, request):
        if request.model not in ("replication", "weak"):
            raise PreflightError("invalid OpenRouter model")
        if any("vertex_content" in m for m in request.messages):
            raise PreflightError("cannot flatten Vertex thought signatures into OpenRouter messages")
        providers = ["deepinfra"] if request.model == "replication" else ["deepinfra", "novita", "groq"]
        provider = {"order": providers, "only": providers, "allow_fallbacks": False,
                    "require_parameters": True, "quantizations": ["fp8"]}
        if request.model == 'weak' and request.metadata.get('arm') == 'R':
            provider = {'require_parameters': True}
        return {"model": MODELS[request.model], "messages": request.messages,
                "temperature": 0, "seed": 20260921, "max_tokens": request.max_output_tokens,
                "provider": provider,
                **({"tools": [{"type": "function", "function": t} for t in request.tools]}
                   if request.tools else {})}

    def count(self, request):
        if self.counter is None:
            raise PreflightError("OpenRouter native joint tokenizer/template gate unresolved")
        return integer(self.counter(self.wire(request)), "native joint input count")

    async def generate(self, request):
        import httpx
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise PreflightError("OPENROUTER_API_KEY is absent from process environment")
        async with httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=0),
                                    timeout=request.timeout_s) as client:
            r = await client.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + key}, json=self.wire(request))
            if r.status_code != 200:
                raise InfrastructureError(f"OpenRouter HTTP {r.status_code}: {r.text.replace(key, '[REDACTED]')}", r.status_code)
            data = r.json()
        self.last_response = data
        u = data.get("usage", {})
        inp = integer(u.get("prompt_tokens"), "prompt_tokens")
        total = integer(u.get("completion_tokens"), "completion_tokens")
        thinking = integer(u.get("completion_tokens_details", {}).get("reasoning_tokens"), "reasoning_tokens")
        cached = integer(u.get("prompt_tokens_details", {}).get("cached_tokens"), "cached_tokens")
        if thinking > total or u.get("total_tokens") != inp + total:
            raise PreflightError("OpenRouter usage does not reconcile")
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {"role": "assistant", "content": ""}
        calls = [{"id": c["id"], "name": c["function"]["name"],
                  "arguments": decode_arguments(c["function"]["arguments"])} for c in msg.get("tool_calls", [])]
        if not data.get("provider") or not data.get("model") or u.get("cost") is None:
            raise PreflightError("OpenRouter omitted provider/model/billing")
        revision = packed({k: data.get(k) for k in ("model", "provider", "system_fingerprint")})
        return PaidReply(msg.get("content") or "", inp, total-thinking, thinking, cached, revision,
                         data, msg, calls, choice.get("finish_reason", ""), u["cost"])


def decode_arguments(value):
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value  # Invalid model tool output is scored, never retried.


class OfflineBackend:
    """Inject synthetic replies through the same request/parser path; no network."""
    def __init__(self, respond):
        self.respond = respond

    def count(self, request):
        return 0  # deliberately not offered as a real tokenizer

    async def generate(self, request):
        response = self.respond(request)
        if isinstance(response, PaidReply):
            return response
        return PaidReply(response, 0, 0, 0, 0, "offline", {},
                         {"role": "assistant", "content": response})


class PaidClient:
    def __init__(self, backend, ledger, block_id=None, *, reuse_completed=False):
        self.backend, self.ledger = backend, ledger
        self.block_id = block_id
        self.reuse_completed = reuse_completed
        # SDK transports own async connection pools bound to their first loop.
        # Keep one loop for the entire serial client, never asyncio.run per call.
        self._runner = asyncio.Runner()

    async def _generate(self, request):
        return await asyncio.wait_for(self.backend.generate(request), request.timeout_s)

    def close(self):
        self._runner.close()

    def call(self, request):
        if self.block_id:
            request = replace(request, metadata={**request.metadata, "block_id": self.block_id})
        if self.reuse_completed:
            cached = self.ledger.cached_reply(request)
            if cached is not None:
                return cached
        if not 0 < request.timeout_s <= 120:
            raise PreflightError("wall timeout must be in (0,120]")
        count = self.backend.count(request)
        if count > request.max_input_tokens:
            raise PreflightError(f"joint input {count} exceeds {request.max_input_tokens}; no truncation")
        self.ledger.recover_smoke(request)
        while True:
            revisions = self.ledger.reserve(request)
            start = time.monotonic()
            self.backend.last_response = None
            try:
                reply = self._runner.run(self._generate(request))
                break
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                key = os.environ.get("OPENROUTER_API_KEY")
                if key:
                    error = error.replace(key, "[REDACTED]")
                status = infrastructure_status(exc)
                if (isinstance(exc, InfrastructureError) and exc.status_code == 404
                        and request.model == 'weak' and request.metadata.get('arm') == 'R'
                        and no_tool_endpoint(exc)):
                    self.ledger.stop_panel(request, error, unavailable=True)
                    raise ToolEndpointUnavailable(error) from None
                if status is not None:
                    attempt = self.ledger.infrastructure_failure(request, error, status, time.monotonic()-start)
                    if attempt <= 3:
                        time.sleep(2 ** (attempt-1))
                        continue
                    raise InfrastructureError(error + "; infrastructure retry limit exhausted") from None
                if isinstance(exc, InfrastructureError) and self.reuse_completed:
                    self.ledger.stop_panel(request, error)
                    raise InfrastructureError(error) from None
                self.ledger.halt(request, error, self.backend.last_response, time.monotonic()-start)
                raise PreflightError(error) from None
        revision = revisions.get(revision_key(request.model, reply.response))
        reply.latency_s = time.monotonic() - start
        error = None
        if reply.input_tokens > request.max_input_tokens or reply.billed_output_tokens > request.max_output_tokens:
            error = "provider exceeded per-call token cap"
        elif revision and revision != reply.revision:
            error = "served model revision changed; amendment required"
        elif reply.provider_cost_usd is not None and Decimal(str(reply.provider_cost_usd)) * Decimal(RATES[request.model][2]) > cost(request.model, reply.input_tokens, reply.billed_output_tokens) + Decimal(".00000001"):
            error = "provider billing exceeds design price table; amendment required"
        self.ledger.complete(request, reply, error, panel_only=self.reuse_completed)
        if error:
            if self.reuse_completed:
                raise InfrastructureError(error)
            raise PreflightError(error)
        return reply
