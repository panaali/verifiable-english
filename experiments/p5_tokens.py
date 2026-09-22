"""P5-only Vertex counting and config-bound billing calibration.

countTokens accepts generationConfig but still undercounts the retained smoke.
Never transfer its residual to another system instruction, schema, or tool set.
P1 continues to use the unmodified shared VertexBackend.
"""
from dataclasses import asdict, replace
from decimal import Decimal
import asyncio
import json
import time

from ve_experiments.paid import (MODELS, Ledger, PaidRequest, PreflightError,
                                 VertexBackend, digest, integer)


def count_wire(request):
    from google.genai import types
    contents, cfg = VertexBackend.__new__(VertexBackend).wire(request)
    # GenerateContentConfig also contains transport/client-only fields. Project
    # all shared generation fields, including MIME, schema and thinking config.
    generation = types.GenerationConfig.model_validate({
        k: v for k, v in cfg.model_dump(exclude_none=True).items()
        if k in types.GenerationConfig.model_fields})
    config = types.CountTokensConfig(system_instruction=cfg.system_instruction,
                                    tools=cfg.tools, generation_config=generation)
    return contents, config


def config_key(request):
    _, config = count_wire(request)
    return digest([MODELS[request.model], config.model_dump(mode='json', exclude_none=True)])


def wire_key(request):
    contents, config = count_wire(request)
    return digest([MODELS[request.model],
                   [c.model_dump(mode='json', exclude_none=True) for c in contents],
                   config.model_dump(mode='json', exclude_none=True)])


def frozen_calibration():
    from experiments import p5 as p
    return json.loads((p.HERE/'freeze.json').read_text()).get('gemini_calibration', {})


def coverage():
    from experiments.p5_preflight import fixtures
    calibration = frozen_calibration()
    configs = {}
    for request, _ in fixtures():
        if request.model == 'pro':
            key = config_key(request)
            configs.setdefault(key, {'example': request.identity,
                'calibrated': key in calibration.get('configs', {})})
    return {'passed': all(c['calibrated'] for c in configs.values()),
            'configs': configs, 'generation_calls': 0,
            'policy': 'Exact config calibration required; no smoke residual extrapolation.'}


def correction(request, calibration):
    entry = calibration.get('configs', {}).get(config_key(request))
    if entry is None:
        raise PreflightError('Gemini config has no frozen billing calibration: '+config_key(request))
    overhead = integer(entry['overhead_tokens'], 'Gemini overhead')
    if overhead < 0:
        raise PreflightError('negative Gemini overhead')
    return overhead


class P5VertexBackend(VertexBackend):
    def __init__(self, client=None, *, calibration=None):
        super().__init__(client)
        self.calibration = frozen_calibration() if calibration is None else calibration

    def native_count(self, request):
        contents, config = count_wire(request)
        return integer(self.client.models.count_tokens(model=MODELS[request.model],
            contents=contents, config=config).total_tokens, 'countTokens.total_tokens')

    def count(self, request):
        overhead = correction(request, self.calibration)  # Fail before dispatch/count.
        return self.native_count(request) + overhead


def cached_count(request, reply, calibration):
    """Recheck exact retained wire and response; never call Vertex offline."""
    overhead = correction(request, calibration)
    samples = calibration['configs'][config_key(request)]['samples']
    sample = next((s for s in samples if s['wire_sha256'] == wire_key(request)
                   and s['response_sha256'] == digest(reply.response)
                   and s['revision'] == reply.revision), None)
    if sample is None:
        raise PreflightError('cached Gemini count missing for exact smoke wire/response')
    native = integer(sample['native_tokens'], 'retained countTokens.total_tokens')
    if sample['billed_input'] != reply.input_tokens or native + overhead != reply.input_tokens:
        raise PreflightError('cached Gemini calibration disagrees with billing')
    return native + overhead, native, overhead


def calibration_smokes(book, backend, cap):
    """Renew missing configs in one durable <=$0.30 amendment block.

    Keep every config field exact, including the stage output cap. Only the
    user content is replaced. Unknown billing halts without any paid retry.
    """
    from experiments.p5_preflight import fixtures
    from experiments.p5_materials import read
    if not cap.is_finite() or not Decimal(0) < cap <= Decimal('.30'):
        raise PreflightError('Gemini calibration cap must be positive and <= $0.30')
    block = 'gemini-config-calibration-v9'
    retained = set()
    for row in read(book.path):
        if row['event'] != 'reserve' or row['model'] != 'pro':
            continue
        old = PaidRequest(**{k: row[k] for k in PaidRequest.__dataclass_fields__ if k in row})
        if book.cached_reply(old) is not None:
            retained.add(config_key(old))
    requests = {}
    for req, _ in fixtures():
        if req.model != 'pro':
            continue
        key = config_key(req)
        if key in retained:
            continue
        requests.setdefault(key, replace(req,
            identity='calibration/p5/gemini/v9/'+key,
            messages=[m for m in req.messages if m['role']=='system'] +
                [{'role':'user','content':'Calibration only. No dossier is supplied. Return the shortest possible unknown or empty response permitted by the system and schema. Do not invent an argument.'}],
            max_input_tokens=2048,
            metadata={'role':'calibration','config_sha256':key,'block_id':block}))
    if len(requests) > 12:
        raise PreflightError('Gemini calibration exceeds twelve distinct configs')
    if not requests:
        return 0
    # Count all requests before reserving or dispatching; configuration must
    # survive the prompt replacement exactly. Billing residual is measured later.
    for key, req in requests.items():
        if config_key(req) != key or backend.native_count(req) + 512 > req.max_input_tokens:
            raise PreflightError('calibration request/config exceeds conservative input bound')
    book.reserve_block(block, str(cap), resume=True,
                       schedule=[asdict(r) for r in requests.values()], split='calibration')
    calls = 0
    with asyncio.Runner() as runner:
        for req in requests.values():
            if book.cached_reply(req) is not None:
                continue
            rows = read(book.path)
            prior = [r for r in rows if r['event']=='reserve'
                     and r.get('metadata',{}).get('block_id')==block]
            if len(prior) >= 12 or any(r['identity']==req.identity for r in prior):
                raise PreflightError('calibration dispatch cap reached; no retries')
            book.reserve(req)
            start = time.monotonic()
            backend.last_response = None
            try:
                reply = runner.run(asyncio.wait_for(backend.generate(req), req.timeout_s))
            except Exception as exc:
                book.halt(req, type(exc).__name__+': '+str(exc), backend.last_response,
                          time.monotonic()-start)
                raise PreflightError('calibration failed; billing held, no retry') from exc
            reply.latency_s = time.monotonic()-start
            error = ('calibration revision/token cap mismatch'
                     if reply.revision != MODELS['pro'] or reply.input_tokens > req.max_input_tokens
                     or reply.billed_output_tokens > req.billed_output_cap else None)
            book.complete(req, reply, error)
            calls += 1
            if error:
                raise PreflightError(error)
            print(f'Gemini calibration {calls}/{len(requests)} complete', flush=True)
    book.release_block(block)
    return calls


def calibrate(cap=Decimal(0)):
    """Free retained counts by default; explicit <=$0.30 renews missing configs."""
    from experiments import p5 as p
    from experiments.p5_materials import read, write_json
    book = Ledger(p.HERE/'runs/study/costs.jsonl', p.CAP)
    backend = P5VertexBackend(calibration={})
    cap = Decimal(str(cap))
    if not cap.is_finite() or cap < 0 or cap > Decimal('.30'):
        raise PreflightError('Gemini calibration cap must be between $0 and $0.30')
    calls = calibration_smokes(book, backend, cap) if cap else 0
    configs = {}
    reservations = {r['identity']: r for r in read(book.path)
                    if r['event'] == 'reserve' and r['model'] == 'pro'}
    for row in reservations.values():
        req = PaidRequest(**{k: row[k] for k in PaidRequest.__dataclass_fields__ if k in row})
        reply = book.cached_reply(req)
        if reply is None:
            continue
        if reply.revision != MODELS['pro']:
            raise PreflightError('Gemini calibration model revision changed')
        native = backend.native_count(req)
        overhead = reply.input_tokens - native
        if overhead < 0:
            raise PreflightError('negative Gemini calibration residual')
        key = config_key(req)
        entry = configs.setdefault(key, {'overhead_tokens': overhead, 'samples': []})
        if entry['overhead_tokens'] != overhead:
            raise PreflightError('Gemini overhead is not constant for config '+key)
        entry['samples'].append({'request': asdict(req), 'wire_sha256': wire_key(req),
            'native_tokens': native, 'billed_input': reply.input_tokens,
            'response_sha256': digest(reply.response), 'revision': reply.revision})
    result = {'method': 'full GenerateContentConfig countTokens + per-config billed residual',
              'configs': configs, 'generation_calls': calls}
    write_json(p.HERE/'checks/gemini-calibration.json', result)
    return result
