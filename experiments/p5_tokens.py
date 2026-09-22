"""P5-only Vertex counting and config-bound billing calibration.

countTokens accepts generationConfig but still undercounts the retained smoke.
Never transfer its residual to another system instruction, schema, or tool set.
P1 continues to use the unmodified shared VertexBackend.
"""
from dataclasses import asdict
import json

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


def calibrate():
    """Free counts of already completed P5 requests only; never generate."""
    from experiments import p5 as p
    from experiments.p5_materials import read, write_json
    book = Ledger(p.HERE/'runs/study/costs.jsonl', p.CAP)
    backend = P5VertexBackend(calibration={})
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
              'configs': configs, 'generation_calls': 0}
    write_json(p.HERE/'checks/gemini-calibration.json', result)
    return result
