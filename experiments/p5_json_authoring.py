"""DEV-only structured FOL authoring probe. No judges or scored dispatch."""
from collections import Counter
from dataclasses import asdict, replace
from datetime import datetime, timezone
from decimal import Decimal
import argparse
import json
import re

from experiments import p5 as p
from experiments import p5_authoring_feasibility as previous
from experiments.p5_oracle import bounded
from experiments.p5_tokens import count_wire
from ve import Environment
from ve.fol import document_from_named_fol
from ve.printer import print_document
from ve_experiments.paid import Ledger, PaidClient, PreflightError, VertexBackend, cost, digest, packed

REVISION = 've-json-author-feasibility-v13'
OUT = p.HERE / 'runs' / REVISION
# v12's first call was rejected (400 INVALID_ARGUMENT): its exact array
# length bounds make "a constraint that has too many states for serving".
# Its ledger is settled at the full reserved ceiling and, like both smoke
# ledgers and the flash-lite bisection allowance, stays charged against the
# task's $2.50 cap. The wire schema now omits array length bounds; the full
# schema, including exact coverage bounds, is still enforced locally.
RUNS = p.HERE / 'runs'
PRIOR_LEDGERS = [RUNS / 've-json-author-feasibility-v12' / 'costs.jsonl',
                 RUNS / 've-json-author-schema-smoke-v13' / 'costs.jsonl',
                 RUNS / 've-json-author-schema-smoke2-v13' / 'costs.jsonl']
BISECT_LOG = RUNS / 've-json-author-schema-bisect-v13.jsonl'
# 9 gemini-2.5-flash-lite calls, <=899 prompt + 16 output tokens each at
# $0.10/$0.40 per M (< $0.0009); failed 400s are unbilled. Rounded up.
BISECT_ALLOWANCE = Decimal('0.001')
TASK_CAP = Decimal('2.50')

GUIDE = '''Author the complete claim graph in the response JSON Schema. This changes the authoring INTERFACE only. Faithfully formalise all six declared premises and every paragraph, retaining the original root and all conditional alternatives. Do not assert unassumed checks, invent a bridge, change an entity, merge distinct meanings, replace claims by true, omit group members, or weaken the root to obtain a proof. A faithful unprovable graph is allowed.
The supplied vocabulary is a mechanical inventory of PUBLIC glossary senses and entity names, not a per-use interpretation. Choose the appropriate predicate separately at every use from the records. No hidden labels or reference formalisation is supplied.
expressions is a zero-indexed flat AST in dependency order. Every operand integer refers to an EARLIER expression, never a claim ID. Reuse expressions freely. unary has predicate and term:{const:entity}; binary has predicate,left:{const:entity},right:{const:entity}; eq has left/right constant terms; not has body:index; and/or/implies have left:index,right:index; top/bottom have only op. These are VE's named-FOL operators with references replacing nested formulas; all dossier formulas are ground. For a group of facts/rules make ONE nested conjunction referencing all members. A conditional is implies, never a fact. A paragraph claim states its conclusion and any conditional alternatives it asserts; inference antecedents are represented by its parent claims.
claims contains exactly one {id,formula:expression_index,records:[exact record IDs]} for EVERY dossier paragraph and declared-premise ID. Each records array must be nonempty, including declared premises. Alignment is an association, not a support certificate.
support maps EVERY paragraph ID to the declared-premise IDs additionally needed by its edge (facts and/or rule groups). The harness copies the paragraph's public parent edges verbatim and adds these selected declared premises, deduplicating identical IDs. Select every needed rule group; records are not implicit axioms. No added intermediate paragraphs, leaf premises, or non-dossier parents are permitted. The model selects all formulas and additional premise support. root is the supplied original root.
The harness expands AST references without semantic rewriting, imports via the SAME document_from_named_fol path as python -m ve import-fol, prints canonical VE, constructs claims, searches each edge with max_steps=10000, and replays certificates with check_argument(search=False). It does not author or repair content. No model-authored certificates, hashes, queries or splits are needed. One repair receives located diagnostics and the unchanged previous JSON; repair only diagnosed interface/coverage failures while preserving content. No judge is called.
Unrelated syntax example: expressions [{"op":"unary","predicate":"marked","term":{"const":"pebble"}},{"op":"unary","predicate":"round","term":{"const":"pebble"}},{"op":"and","left":0,"right":1}]. A claim formula:2 means both properties. These example symbols do not belong in your dossier output. Return only the complete JSON.'''


def prior_spend():
    total = BISECT_ALLOWANCE
    for path in PRIOR_LEDGERS:
        if path.exists():
            pending, committed, *_ = Ledger.state(p.read(path))
            total += committed + sum(pending.values(), Decimal(0))
    return total


def cap_remaining():
    return TASK_CAP - prior_spend()


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties),
            'additionalProperties': False}


def enum(values):
    return {'type': 'string', 'enum': list(values)}


def array(items, minimum=0, maximum=512):
    return {'type': 'array', 'items': items, 'minItems': minimum, 'maxItems': maximum}


def vocabulary(packet):
    """Public inventory only; no per-node sense assignment or logical content."""
    predicates = {}
    for entry in packet['glossary']:
        match = re.fullmatch(r'(.+): (.+) \(R(\d+)\)', entry['sense'])
        if not match or match[1] != entry['term']:
            raise PreflightError('unrecognised public glossary entry')
        predicates['p' + match[3]] = {'arguments': ['entity'], 'description': entry['sense']}
    text = packed({k: packet[k] for k in ('premises', 'records', 'nodes')})
    constants = sorted(set(re.findall(r'\bunit\d+\b', text)))
    # The only public binary relation in this dossier family. No relation facts
    # are generated: the model must decide whether/where they occur in claims.
    if re.search(r'Lot unit\d+ supplied sample unit\d+\.', text):
        predicates['supplied'] = {'arguments': ['entity', 'entity'], 'description': 'Lot supplied sample.'}
    return {'language': 've.core@0', 'profile': 'relational-fol@0',
            'spec_revision': 've-v0-draft-2026-09-20', 'vocabulary': {
                'sorts': {'entity': {'description': 'A named dossier entity.'}},
                'predicates': dict(sorted(predicates.items())),
                'constants': {c: {'sort': 'entity', 'description': c} for c in constants}}}


def schema(packet):
    vocab = vocabulary(packet)['vocabulary']
    term = obj({'const': enum(vocab['constants'])})
    ref = {'type': 'integer', 'minimum': 0, 'maximum': 511}
    variants = [obj({'op': enum(['unary']), 'predicate': enum(
        k for k,v in vocab['predicates'].items() if len(v['arguments']) == 1), 'term': term})]
    binaries = [k for k,v in vocab['predicates'].items() if len(v['arguments']) == 2]
    if binaries:
        variants.append(obj({'op': enum(['binary']), 'predicate': enum(binaries), 'left': term, 'right': term}))
    variants += [obj({'op': enum(['eq']), 'left': term, 'right': term}),
                 obj({'op': enum(['top', 'bottom'])}), obj({'op': enum(['not']), 'body': ref}),
                 obj({'op': enum(['and', 'or', 'implies']), 'left': ref, 'right': ref})]
    ids = [n['id'] for n in packet['premises'] + packet['nodes']]
    claim = obj({'id': enum(ids), 'formula': ref, 'records': array(enum(r['id'] for r in packet['records']), 1, len(packet['records']))})
    return obj({'expressions': array({'anyOf': variants}, 1),
                'claims': array(claim, len(ids), len(ids)),
                'support': obj({n['id']: array(enum(x['id'] for x in packet['premises']), 0, len(packet['premises']))
                                for n in packet['nodes']}), 'root': enum([packet['root']])})


def wire_schema(packet):
    """Provider copy of schema(): identical except array length bounds.

    Vertex rejects exact/large minItems/maxItems as too many serving states,
    so only minItems=1 survives on the wire. validate() enforces the full
    schema() locally; any length violation is a located interface failure.
    """
    def strip(s):
        if isinstance(s, dict):
            out = {k: strip(v) for k, v in s.items() if k not in ('minItems', 'maxItems')}
            if s.get('minItems') == 1:
                out['minItems'] = 1
            return out
        return [strip(v) for v in s] if isinstance(s, list) else s
    return strip(schema(packet))


class InterfaceError(ValueError):
    def __init__(self, message, path):
        super().__init__(message)
        self.path = path


def validate(value, spec, path=''):
    """Strict validator for precisely the JSON Schema subset emitted above."""
    def fail(message):
        raise InterfaceError(message, path)
    if 'anyOf' in spec:
        for option in spec['anyOf']:
            try:
                validate(value, option, path)
                return
            except InterfaceError:
                pass
        fail('value matches no AST constructor schema')
    kind = spec['type']
    if kind == 'object':
        if type(value) is not dict or set(value) != set(spec['properties']):
            fail('object fields do not match schema')
        for k, sub in spec['properties'].items():
            validate(value[k], sub, path + '/' + k)
    elif kind == 'array':
        if type(value) is not list or not spec['minItems'] <= len(value) <= spec['maxItems']:
            fail('array length/type does not match schema')
        for i, entry in enumerate(value):
            validate(entry, spec['items'], path + '/' + str(i))
    elif kind == 'integer':
        if type(value) is not int or not spec['minimum'] <= value <= spec['maximum']:
            fail('invalid expression reference')
    elif kind == 'string':
        if type(value) is not str or value not in spec['enum']:
            fail('value is outside the public enum')
    else:
        raise AssertionError('unsupported schema keyword/type')


def convert(raw, packet):
    validate(raw, schema(packet))
    env_data = vocabulary(packet)
    env = Environment.from_dict(env_data)
    expanded, sizes, depths = [], [], []
    names = [c['id'] for c in raw['claims']]
    expected = {n['id'] for n in packet['premises'] + packet['nodes']}
    if len(set(names)) != len(names) or set(names) != expected:
        raise InterfaceError('missing or duplicate claim coverage', '/claims')
    for i, expr in enumerate(raw['expressions']):
        node = dict(expr)
        fields = ('left', 'right') if node['op'] in ('and', 'or', 'implies') else ('body',) if node['op'] == 'not' else ()
        size, depth = 1, 1
        for field in fields:
            ref = node[field]
            if ref >= i:
                raise InterfaceError('AST references must point to earlier expressions', f'/expressions/{i}/{field}')
            size += sizes[ref]
            depth = max(depth, 1 + depths[ref])
            node[field] = expanded[ref]
        if size > 10000 or depth > 64:
            raise InterfaceError('expanded AST exceeds VE node/depth budget', f'/expressions/{i}')
        sizes.append(size)
        depths.append(depth)
        expanded.append(node)
    claims, documents = [], {}
    for ci, value in enumerate(raw['claims']):
        name = value['id']
        index = value['formula']
        if index >= len(expanded):
            raise InterfaceError('claim references nonexistent expression', f'/claims/{ci}/formula')
        fol = {'formulas': [expanded[index]]}
        try:
            doc = document_from_named_fol(env, fol)
            source = print_document(env, doc)
        except Exception as exc:
            raise InterfaceError(type(exc).__name__ + ': ' + str(exc),
                                 f'/claims/{ci}/formula' + (getattr(exc, 'path', None) or '')) from exc
        claims.append({'id': name, 'source': source})
        documents[name] = fol
    artifact = {'environment': env_data, 'claims': claims,
                'edges': [{'id': 'e_' + n['id'], 'conclusion': n['id'],
                           'premises': list(dict.fromkeys(n['parents'] + raw['support'][n['id']]))}
                          for n in packet['nodes']],
                'root': raw['root'], 'alignment': {c['id']: c['records'] for c in raw['claims']},
                'queries': [], 'splits': []}
    return artifact, documents


def replay(text, item):
    try:
        raw = p.protocol_json(text)
    except (ValueError, TypeError) as exc:
        return {'ok': False, 'category': 'JSON delivery/truncation', 'error': str(exc), 'path': ''}
    try:
        artifact, documents = convert(raw, item['payload'])
    except (InterfaceError, ValueError, TypeError) as exc:
        return {'ok': False, 'category': 'schema/AST reference or import error',
                'error': type(exc).__name__ + ': ' + str(exc), 'path': getattr(exc, 'path', '')}
    result = bounded('author', {'artifact': artifact, 'packet': item['payload']}, 5)
    diagnostics = []
    if 'findings' in result:
        for edge, status in result['findings']['findings'].items():
            if status != ['follows']:
                # Findings are keyed by deduction NAME, not a hidden gold edge.
                target = next((e for e in artifact['edges'] if e['id'] == edge), None)
                diagnostics.append({'edge_id': edge, 'claim_id': target['conclusion'] if target else None,
                                    'status': status, 'path': '/support/' + target['conclusion'] if target else '/support'})
        diagnostics += [{'error': error, 'path': '/support'} for error in result['findings']['errors']]
    category = ('success' if result['ok'] else 'graph/certificate rejection' if result.get('findings', {}).get('errors')
                else 'unproved edge (no certificate; not a refutation)' if 'findings' in result
                else 'local resource limit' if 'timeout' in result.get('error', '') or 'ResourceLimit' in result.get('error', '')
                else previous.category(result))
    return {**result, 'category': category, 'diagnostics': diagnostics,
            'canonical_artifact': artifact, 'fol_documents': documents}


def feedback(result):
    return {k: result[k] for k in ('ok', 'category', 'error', 'path', 'diagnostics', 'obligations') if k in result}


def request(item, stage, history=None):
    if item['split'] != 'dev' or stage not in ('author', 'repair'):
        raise PreflightError('only DEV author/repair are authorized')
    if history and any(r['item_id'] != item['id'] for r in history):
        raise PreflightError('cross-dossier history')
    packet = item['payload']
    # No labels, reference graph, family, variant, or per-use interpretation.
    public = {k: packet[k] for k in ('id', 'premises', 'records', 'nodes', 'root')}
    instruction = ('Defend the proposed argument, faithfully formalising uses and premises.' if stage == 'author'
                   else 'Repair only the diagnosed interface/coverage failures. One repair is allowed; retain the original root.')
    req = p.request(item, 'VE', stage)
    content = GUIDE + '\nPublic vocabulary:\n' + packed(vocabulary(packet)['vocabulary']) + '\nDossier:\n' + packed(public)
    if history:
        content += '\nProtocol record:\n' + packed(history)
    return replace(req, identity=f'{REVISION}/dev/{item["id"]}/VE/pro/{stage}/0',
                   messages=[{'role': 'system', 'content': p.SYSTEM + ' ' + instruction},
                             {'role': 'user', 'content': content}],
                   max_input_tokens=16384 if stage == 'author' else 20480, max_output_tokens=5000,
                   response_schema=wire_schema(packet), metadata={**req.metadata, 'feasibility_only': True,
                       'prompt_revision': REVISION, 'require_response_schema': True})


class SchemaBudgetBackend(VertexBackend):
    """No transfer of a residual calibrated on another schema/system config."""
    def count(self, req):
        contents, cfg = count_wire(req)
        native = self.client.models.count_tokens(model=p.MODELS[req.model], contents=contents, config=cfg).total_tokens
        # Deliberately double-cover schema, plus fixed framing margin. This is
        # a conservative admission guard, NOT a claim of exact billing count.
        # Full input/output ceilings are reserved and actual usage reconciled.
        return int(native) + len(packed(req.response_schema).encode()) + 512


def settle_v12():
    """Settle the halted v12 call at its full ceiling; never refund it."""
    return Ledger(PRIOR_LEDGERS[0], Decimal('2.50')).reconcile_interrupted()


def smoke():
    """One minimal paid call proving Vertex accepts the JSON-Schema wire.

    Uses DEV item 0's real author schema, a content-free instruction and a
    64-token output cap (the first smoke, sent with the
    rejected bounded wire schema, is retained and charged at its ceiling); the reply is not scored or used by the probe.
    """
    if PRIOR_LEDGERS[2].exists():
        raise PreflightError('schema smoke already dispatched')
    item = p.materials('dev')[0]
    base = request(item, 'author')
    req = replace(base, identity=f'{REVISION}/schema-smoke2/{item["id"]}',
                  max_input_tokens=8192, max_output_tokens=64,
                  messages=[{'role': 'system', 'content': 'Schema acceptance smoke test.'},
                            {'role': 'user', 'content': 'Return any short JSON value conforming to the response schema.'}],
                  metadata={**base.metadata, 'role': 'schema_smoke'})
    client = PaidClient(SchemaBudgetBackend(), Ledger(PRIOR_LEDGERS[2], Decimal('0.02')))
    try:
        reply = client.call(req)
    finally:
        client.close()
    return {'finish_reason': reply.finish_reason, 'input_tokens': reply.input_tokens,
            'billed_output_tokens': reply.billed_output_tokens, 'text_prefix': reply.text[:200]}


def retained_inputs():
    return {**previous.retained_inputs(), **{
        str(path.relative_to(p.ROOT)): p.sha(path)
        for path in [*previous.OUT.iterdir(), *PRIOR_LEDGERS[0].parent.iterdir(),
                     *[q for q in PRIOR_LEDGERS[1:] if q.exists()], BISECT_LOG]
        if path.is_file()}}


def freeze():
    items = p.materials('dev')
    assert len(items) == 12
    reqs = [request(i, s) for i in items for s in ('author', 'repair')]
    ceiling = sum((cost(r.model, r.max_input_tokens, r.billed_output_cap) for r in reqs), Decimal(0))
    assert ceiling <= cap_remaining()
    for req in reqs:
        count_wire(req)  # SDK must accept actual response_schema before dispatch.
    paths = [p.ROOT/'experiments/p5_json_authoring.py', p.ROOT/'tests/test_p5_json_authoring.py',
             p.HERE/'JSON-AUTHORING-AMENDMENT.md', p.ROOT/'ve_experiments/paid.py', p.ROOT/'uv.lock']
    paths += list((p.ROOT/'ve').glob('*.py')) + [p.ROOT/f'experiments/{name}.py' for name in
        ('p5', 'p5_oracle', 'p5_tokens', 'p5_authoring_feasibility', 'p5_dev_revision')]
    manifest = {'time_utc': datetime.now(timezone.utc).isoformat(), 'revision': REVISION,
                'cap_usd': str(cap_remaining()), 'prior_task_spend_usd': str(prior_spend()),
                'task_cap_usd': str(TASK_CAP), 'worst_case_usd': str(ceiling), 'max_calls': 24,
                'item_ids': [i['id'] for i in items], 'models': p.MODELS, 'rates': p.RATES,
                'guide': GUIDE, 'author_requests': [asdict(r) for r in reqs if r.metadata['role'] == 'author'],
                'hashes': {str(path.relative_to(p.ROOT)): p.sha(path) for path in paths},
                'retained_hashes': retained_inputs()}
    if (OUT/'freeze.json').exists():
        raise PreflightError('freeze already exists; never overwrite a dispatched identity')
    p.write_json(OUT/'freeze.json', manifest)
    return {'revision': REVISION, 'worst_case_usd': str(ceiling), 'max_calls': 24}


def run(cap):
    if not cap.is_finite() or not Decimal(0) < cap <= cap_remaining():
        raise PreflightError('explicit cap must be positive and within the task cap net of prior ledgers')
    manifest = json.loads((OUT/'freeze.json').read_text())
    for path, sha in manifest['hashes'].items():
        if p.sha(p.ROOT/path) != sha:
            raise PreflightError('probe freeze changed: ' + path)
    if retained_inputs() != manifest['retained_hashes']:
        raise PreflightError('retained evidence changed')
    if cap < Decimal(manifest['worst_case_usd']):
        raise PreflightError('cap cannot cover worst-case complete probe')
    book = Ledger(OUT/'costs.jsonl', cap)
    client = PaidClient(SchemaBudgetBackend(), book)
    results = []
    try:
        for item in p.materials('dev'):
            history, stages = [], []
            for stage in ('author', 'repair'):
                req = request(item, stage, history or None)
                cached = book.cached_reply(req)
                reply = cached if cached is not None else client.call(req)
                result = replay(reply.text, item)
                stages.append({'stage': stage, 'identity': req.identity, 'response_sha256': digest(reply.text),
                               'finish_reason': reply.finish_reason, 'replay': result})
                history = [{'item_id': item['id'], 'stage': 'author', 'text': reply.text},
                           {'item_id': item['id'], 'stage': 'diagnostics', 'record': feedback(result)}]
                if result['ok']:
                    break
            row = {'item_id': item['id'], 'stages': stages, 'ok': stages[-1]['replay']['ok']}
            results.append(row)
            p.write_json(OUT/'results.json', results)
            print(f'[{len(results)}/12] replay={row["ok"]}; stages={len(stages)}; {stages[-1]["replay"]["category"]}', flush=True)
    finally:
        client.close()
    assert retained_inputs() == manifest['retained_hashes']
    pending, spent, *_ = Ledger.state(p.read(book.path))
    summary = {'revision': REVISION, 'n': len(results), 'successes': sum(r['ok'] for r in results),
               'initial_successes': sum(r['stages'][0]['replay']['ok'] for r in results),
               'rate': sum(r['ok'] for r in results)/12, 'calls': sum(len(r['stages']) for r in results),
               'spend_usd': str(spent), 'pending_usd': str(sum(pending.values(), Decimal(0))),
               'cap_usd': str(cap), 'judges': 0, 'scored_items': 0, 'source_fidelity_assessed': False,
               'final_categories': dict(Counter(r['stages'][-1]['replay']['category'] for r in results)),
               'all_attempt_categories': dict(Counter(s['replay']['category'] for r in results for s in r['stages'])),
               'retained_inputs_unchanged': True}
    p.write_json(OUT/'summary.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['settle-v12', 'smoke', 'freeze', 'run'])
    parser.add_argument('--cap-usd', type=Decimal, default=Decimal(0))
    args = parser.parse_args()
    actions = {'settle-v12': settle_v12, 'smoke': smoke, 'freeze': freeze,
               'run': lambda: run(args.cap_usd)}
    print(packed(actions[args.action]()))


if __name__ == '__main__':
    main()
