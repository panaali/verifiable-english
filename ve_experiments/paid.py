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
WEAK_PROVIDER_RATES = {  # Amendment 8: cached provider-preflight endpoint listing, USD/million.
    "DeepInfra": (".02", ".04", "1.055"), "Novita": (".02", ".05", "1.055"),
    "Groq": (".05", ".08", "1.055"), "CoreWeave": (".22", ".22", "1.055"),
    "Cloudflare": (".152", ".287", "1.055"),
}
VERDICT_SCHEMA = {"type": "object", "properties": {
    "verdict": {"type": "string", "enum": ["approve", "reject", "unknown"]}},
    "required": ["verdict"], "additionalProperties": False}
JUDGE_OUTPUT_CAP = 1024


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(packed(value).encode()).hexdigest()


def cost(model, inp, output, *, provider=None, arm=None):
    if any(type(v) is not int or v < 0 for v in (inp, output)):
        raise ValueError("token counts must be nonnegative integers")
    rates = RATES[model]
    if model == "weak":
        if provider is not None:
            if provider not in WEAK_PROVIDER_RATES:
                raise PreflightError(f"provider absent from design price table: {provider}")
            rates = WEAK_PROVIDER_RATES[provider]
        elif arm is not None:
            # R is unrestricted; reserve the most expensive advertised tool endpoint.
            # Other arms retain fp8 routing (DeepInfra/Novita).
            rates = WEAK_PROVIDER_RATES["CoreWeave" if arm == "R" else "Novita"]
    ri, ro, fee = map(Decimal, rates)
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
    response_schema: dict | None = None

    @property
    def billed_output_cap(self):
        # Amendment 14 changes accounting only; the provider wire and cache
        # identity retain the attacker's 256-token visible-message request.
        return JUDGE_OUTPUT_CAP if self.model == 'pro' and self.metadata.get('role') == 'attacker' else self.max_output_tokens


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
        recovered = {r["halt_time"] for r in rows if r["event"] in ("smoke_recovery", "routing_recovery", "amendment8_halt_recovery", "amendment14_halt_recovery")}
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
            elif row["event"] == "amendment14_block":
                pending["block:" + row["block_id"]] = Decimal(row["remaining_usd"])
            elif row["event"] == "block_release":
                pending.pop("block:" + row["block_id"])
            elif row["event"] == "allowance":
                committed += Decimal(row["cost_usd"])
            elif row["event"] == "allowance_adjustment":
                committed += Decimal(row["cost_usd"]) - Decimal(row["prior_usd"])
        return pending, committed, seen, revisions, blocked

    def reconcile(self, releases, allowances):
        """Append audited releases; never erase calls or forgive unknown billing.

        Callers supply block reasons and replacement allowance amounts/evidence.
        A live call in a block prevents its release, even if the schedule changed.
        """
        with self.locked() as (f, rows):
            pending, _, _, _, blocked = self.state(rows)
            if blocked or any(not k.startswith('block:') for k in pending):
                raise PreflightError('cannot reconcile study holds while billing unresolved')
            events = []
            for block, reason in releases.items():
                if 'block:' + block in pending:
                    events.append({'event': 'block_release', 'block_id': block,
                                   'released_usd': str(pending['block:' + block]), 'reason': reason})
            current = {r['identity']: Decimal(r['cost_usd']) for r in rows
                       if r['event'] in ('allowance', 'allowance_adjustment')}
            for identity, details in allowances.items():
                amount = Decimal(details['cost_usd'])
                if not amount.is_finite() or amount < 0:
                    raise ValueError('reconciled allowance must be finite and nonnegative')
                prior = current.get(identity, Decimal(0))
                if prior != amount:
                    events.append({'event': 'allowance_adjustment', 'identity': identity,
                                   'prior_usd': str(prior), 'released_usd': str(prior - amount), **details})
            for event in events:
                self.append(f, {**event, 'sample': False})
            return events

    def allowance(self, identity, amount):
        """Persist reserved envelopes that cannot fund additional samples."""
        with self.locked() as (f, rows):
            if any(r.get("event") in ("allowance", "allowance_adjustment") and r["identity"] == identity for r in rows):
                return
            pending, spent, _, _, blocked = self.state(rows)
            if blocked or pending:
                raise PreflightError("ledger not available for allowance")
            if spent + Decimal(str(amount)) > self.cap:
                raise BudgetExceeded("envelope exceeds --cap-usd")
            self.append(f, {"event": "allowance", "identity": identity, "cost_usd": str(amount)})

    def reserve_block(self, block_id, ceiling, *, resume=False, schedule=None, split=None):
        with self.locked() as (f, rows):
            pending, spent, _, _, blocked = self.state(rows)
            prior = next((r for r in reversed(rows) if r['event'] in ('block_reserve', 'amendment14_block') and r['block_id'] == block_id), None)
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
            self.append(f, {"event": "block_reserve", "block_id": block_id, "ceiling_usd": str(ceiling),
                            "schedule": schedule, "split": split})

    def release_block(self, block_id):
        with self.locked() as (f, rows):
            pending, _, _, _, blocked = self.state(rows)
            if blocked or any(not k.startswith("block:") for k in pending):
                raise PreflightError("cannot release block while billing unresolved")
            if 'block:' + block_id not in pending:
                return
            self.append(f, {"event": "block_complete", "block_id": block_id, "sample": False})
            self.append(f, {"event": "block_release", "block_id": block_id,
                            "released_usd": str(pending['block:' + block_id]), "reason": "completed block"})

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
        ceiling = cost(request.model, request.max_input_tokens, request.billed_output_cap, arm=request.metadata.get('arm'))
        with self.locked() as (f, rows):
            pending, spent, seen, revisions, blocked = self.state(rows)
            history = [r for r in rows if r.get("identity") == request.identity]
            recovered = {r['halt_time'] for r in rows if r['event'] in ('amendment8_halt_recovery', 'amendment14_halt_recovery')}
            for row in rows:
                if row['event'] in ('panel_halt', 'panel_validation_halt') and row['model'] == request.model and row['time'] not in recovered:
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
                if any(prior.get(k) != asdict(request)[k] for k in asdict(request)):
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
        try:
            actual = cost(request.model, reply.input_tokens, reply.billed_output_tokens,
                          provider=reply.response.get('provider'))
        except PreflightError:
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
            recovered = {r['halt_time'] for r in rows if r['event'] in
                         ('amendment8_halt_recovery', 'amendment14_halt_recovery')}
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
                    halted |= row['time'] not in recovered
            if reply is not None and not halted:
                for key in ("model", "messages", "tools", "max_input_tokens", "max_output_tokens", "response_schema"):
                    if reservation.get(key) != getattr(request, key):
                        raise PreflightError("cached smoke request changed" if smoke(request) else "cached trial request changed")
                if not smoke(request) and any(reservation[k] != getattr(request, k) for k in ('metadata', 'timeout_s')):
                    raise PreflightError('cached trial request changed')
                return PaidReply(**{k: reply[k] for k in PaidReply.__dataclass_fields__})
        return None

    def amend_attacker_billing(self, block_id, ceiling):
        """Amendment 14: append recovery and reopen the same scored envelope.

        Only a reconciled Gemini attacker output overrun within 1,024 is
        recoverable. Keep request IDs, responses, receipts and costs untouched.
        """
        with self.locked() as (f, rows):
            pending, spent, _, _, blocked = self.state(rows)
            if blocked or any(not k.startswith('block:') for k in pending):
                raise PreflightError('Amendment 14 requires reconciled billing')
            recovered = {r['halt_time'] for r in rows if r['event'] == 'amendment14_halt_recovery'}
            events = []
            for halt in rows:
                if (halt['event'] != 'panel_validation_halt' or halt['time'] in recovered
                        or halt.get('model') != 'pro' or not halt['identity'].startswith('scored/')
                        or halt['error'] != 'provider exceeded per-call token cap'):
                    continue
                history = [r for r in rows if r.get('identity') == halt['identity']]
                req = next(r for r in history if r['event'] == 'reserve')
                reply = next(r for r in history if r['event'] == 'complete')
                if (req['metadata'].get('role') != 'attacker' or req['max_output_tokens'] != 256
                        or req['metadata'].get('block_id') != block_id
                        or reply['input_tokens'] > req['max_input_tokens']
                        or not 256 < reply['billed_output_tokens'] <= JUDGE_OUTPUT_CAP
                        or reply['output_tokens'] > 256):
                    continue
                prior_revisions = {r['revision'] for r in rows if r['event'] == 'complete'
                                   and r.get('model') == 'pro' and r['time'] < halt['time']}
                listed = cost('pro', reply['input_tokens'], reply['billed_output_tokens'])
                if prior_revisions != {reply['revision']} or Decimal(reply['cost_usd']) > listed:
                    raise PreflightError('Amendment 14 cannot recover revision or price mismatch')
                events.append({'event': 'amendment14_halt_recovery', 'halt_time': halt['time'],
                               'identity': halt['identity'], 'sample': False,
                               'reason': 'attacker visible cap 256; billed-output cap 1024; reuse completed reply'})
            prior = next((r for r in rows if r['event'] == 'block_reserve' and r['block_id'] == block_id), None)
            amended = next((r for r in rows if r['event'] == 'amendment14_block' and r['block_id'] == block_id), None)
            if prior and not amended:
                identities = {r['identity'] for r in rows if r['event'] == 'reserve'
                              and r['metadata'].get('block_id') == block_id}
                consumed = sum((Decimal(r.get('cost_usd', '0')) + Decimal(r.get('infrastructure_hold_usd', '0'))
                                for r in rows if r.get('identity') in identities
                                and r['event'] in ('complete', 'infrastructure_failure', 'panel_halt')), Decimal(0))
                remaining = Decimal(str(ceiling)) - consumed
                other = sum((v for k, v in pending.items() if k != 'block:' + block_id), Decimal(0))
                if remaining < 0 or spent + other + remaining > self.cap:
                    raise BudgetExceeded('Amendment 14 commitments exceed --cap-usd')
                events.append({'event': 'amendment14_block', 'block_id': block_id,
                               'ceiling_usd': str(ceiling), 'consumed_usd': str(consumed),
                               'remaining_usd': str(remaining), 'sample': False,
                               'reason': 'resume same assignments; subtract all completed costs and retain holds'})
            elif amended and Decimal(amended['ceiling_usd']) != Decimal(str(ceiling)):
                raise PreflightError('Amendment 14 ceiling changed')
            for event in events:
                self.append(f, event)
            return events

    def amended_dev_request(self, request):
        """Only the approved dev exception may replace a changed request.

        Identical attacker requests retain their original identity. Changed histories,
        caps or schemas receive a deterministic new identity; old charges stay intact.
        """
        if request.metadata.get('split') != 'dev':
            return request
        with self.locked() as (_, rows):
            if not any(r['event'] == 'amendment8' for r in rows):
                return request
            candidates = [r for r in rows if r['event'] == 'reserve' and
                          (r['identity'] == request.identity or r['identity'].startswith(request.identity + '/amendment8/'))]
            values = asdict(request)
            for prior in reversed(candidates):
                same = all(prior.get(k) == v for k, v in values.items() if k not in ('metadata', 'identity'))
                same &= {k: v for k, v in prior['metadata'].items() if k != 'block_id'} == {
                    k: v for k, v in request.metadata.items() if k != 'block_id'}
                if same:
                    return replace(request, identity=prior['identity'], metadata=prior['metadata'])
            prior = next((r for r in candidates if r['identity'] == request.identity), None)
            if prior:
                values['metadata'].pop('block_id', None)
                return replace(request, identity=request.identity + '/amendment8/' + digest(values))
        return request

    def gemini_schedule(self):
        with self.locked() as (f, rows):
            calls = [r for r in rows if r['event'] == 'complete' and r['model'] == 'pro'][-50:]
            mean = sum(r['billed_output_tokens'] for r in calls) / len(calls) if calls else 0
            prior = any(r['event'] == 'schedule_fallback' for r in rows)
            if mean > 512 and not prior:
                self.append(f, {'event': 'schedule_fallback', 'schedule': 'primary_1024',
                    'window': len(calls), 'mean_billed_output_tokens': mean, 'sample': False})
            return 'primary_1024' if prior or mean > 512 else 'full_256'

    def amend_dev(self, ceiling):
        """Append-only Amendment 8 recovery; no generation or accounting erasure."""
        with self.locked() as (f, rows):
            if any(r['event'] == 'amendment8' for r in rows):
                return
            pending, spent, _, _, blocked = self.state(rows)
            if blocked or pending:
                raise PreflightError('Amendment 8 requires reconciled, released dev billing')
            if any(r['event'] == 'reserve' and r.get('metadata', {}).get('split') == 'scored' for r in rows):
                raise PreflightError('Amendment 8 is dev-only and must precede scored dispatch')
            self.append(f, {'event': 'amendment8', 'split': 'dev', 'sample': False,
                'prior_spend_usd': str(spent), 'planning_ceiling_usd': str(ceiling)})
            for row in rows:
                if row['event'] != 'panel_validation_halt' or not row['identity'].startswith('dev/'):
                    continue
                completion = next(r for r in reversed(rows) if r['event'] == 'complete' and r['identity'] == row['identity'])
                if row['error'] == 'provider exceeded per-call token cap':
                    reservation = next(r for r in reversed(rows) if r['event'] == 'reserve' and r['identity'] == row['identity'])
                    safe = (completion['input_tokens'] <= reservation['max_input_tokens']
                            and completion['billed_output_tokens'] <= JUDGE_OUTPUT_CAP)
                elif row['error'] == 'provider billing exceeds design price table; amendment required':
                    try:
                        safe = Decimal(str(completion['provider_cost_usd'])) * Decimal('1.055') <= cost(
                            completion['model'], completion['input_tokens'], completion['billed_output_tokens'],
                            provider=completion['response'].get('provider')) + Decimal('.00000001')
                    except (PreflightError, TypeError):
                        safe = False
                else:
                    safe = False
                if safe:
                    self.append(f, {'event': 'amendment8_halt_recovery', 'halt_time': row['time'],
                        'identity': row['identity'], 'model': row['model'], 'sample': False})

    def format_fallback(self, request, status, error):
        with self.locked() as (f, _):
            self.append(f, {'event': 'structured_output_fallback', 'identity': request.identity,
                'model': request.model, 'from': 'json_schema', 'to': 'json_object',
                'status': status, 'error': error, 'sample': False, 'rejected_request_cost_usd': '0'})

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
            elif m.get("tool_calls"):
                # Amendment 12: Gemini attacker observes Qwen's native replay
                # transcript without dropping function calls or their bindings.
                parts = [types.Part(text=m['content'])] if m.get('content') else []
                parts += [types.Part(function_call=types.FunctionCall(
                    name=c['function']['name'], id=c['id'],
                    args=json.loads(c['function']['arguments'])
                    if isinstance(c['function']['arguments'], str) else c['function']['arguments']))
                    for c in m['tool_calls']]
                contents.append(types.Content(role='model', parts=parts))
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
            response_mime_type='application/json' if request.response_schema else None,
            response_schema=request.response_schema,
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

    def wire(self, request, response_mode='json_schema'):
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
                **({'response_format': {'type': response_mode, **({'json_schema': {
                    'name': 'verdict', 'strict': True, 'schema': request.response_schema}}
                    if response_mode == 'json_schema' else {})}} if request.response_schema else {}),
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
            mode = 'json_schema'
            r = await client.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + key}, json=self.wire(request))
            error = r.text.replace(key, '[REDACTED]') if r.status_code != 200 else ''
            if (request.response_schema and r.status_code in (400, 422)
                    and any(s in error.lower() for s in ('json_schema', 'structured output', 'response_format'))
                    and any(s in error.lower() for s in ('not support', 'unsupported', 'not available'))):
                # Only an explicit parameter rejection is free to retry in JSON mode.
                self.record_fallback(request, r.status_code, error)
                mode = 'json_object'
                r = await client.post('https://openrouter.ai/api/v1/chat/completions',
                    headers={'Authorization': 'Bearer ' + key}, json=self.wire(request, mode))
            if r.status_code != 200:
                raise InfrastructureError(f"OpenRouter HTTP {r.status_code}: {r.text.replace(key, '[REDACTED]')}", r.status_code)
            data = r.json()
            if request.response_schema:
                data['_p1_response_format'] = mode
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
            request = self.ledger.amended_dev_request(request)
            cached = self.ledger.cached_reply(request)
            if cached is not None:
                return cached
        if not 0 < request.timeout_s <= 120:
            raise PreflightError("wall timeout must be in (0,120]")
        count = self.backend.count(request)
        if count > request.max_input_tokens:
            raise PreflightError(f"joint input {count} exceeds {request.max_input_tokens}; no truncation")
        self.ledger.recover_smoke(request)
        self.backend.record_fallback = self.ledger.format_fallback
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
        if reply.input_tokens > request.max_input_tokens or reply.billed_output_tokens > request.billed_output_cap:
            error = "provider exceeded per-call token cap"
        elif revision and revision != reply.revision:
            error = "served model revision changed; amendment required"
        else:
            try:
                listed = cost(request.model, reply.input_tokens, reply.billed_output_tokens,
                              provider=reply.response.get('provider'))
                if reply.provider_cost_usd is not None and Decimal(str(reply.provider_cost_usd)) * Decimal(RATES[request.model][2]) > listed + Decimal('.00000001'):
                    error = 'provider billing exceeds design price table; amendment required'
            except PreflightError as exc:
                error = str(exc)
        self.ledger.complete(request, reply, error, panel_only=self.reuse_completed)
        if error:
            if self.reuse_completed:
                raise InfrastructureError(error)
            raise PreflightError(error)
        return reply
