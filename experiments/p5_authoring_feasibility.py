"""DEV-only, one author + at most one repair; never executes judges or scored items."""
from collections import Counter
from dataclasses import asdict, replace
from datetime import datetime, timezone
from decimal import Decimal
import argparse
import json
from pathlib import Path

from experiments import p5 as p
from experiments.p5_oracle import bounded
from experiments.p5_tokens import config_key, frozen_calibration
from ve import Environment, Claim
from ve_experiments.paid import Ledger, PaidClient, PreflightError, cost, digest, packed

REVISION = 've-author-feasibility-v11'
OUT = p.HERE / 'runs' / REVISION
CATEGORIES = ('syntax/parse error', 'undeclared or misspelled predicate', 'sort/type error',
              'wrong graph shape', 'missing premise so the step does not entail',
              'certificate/format', 'prover ResourceLimit', 'other')
TOY_ENV = {
    'language': 've.core@0', 'profile': 'relational-fol@0',
    'spec_revision': 've-v0-draft-2026-09-20',
    'vocabulary': {
        'sorts': {'toy': {'description': 'An unrelated demonstration object.'}},
        'predicates': {name: {'arguments': ['toy'], 'description': desc} for name, desc in
                       [('marked', 'Carries a mark.'), ('round', 'Has a round shape.'),
                        ('inspected', 'Has been inspected.')]},
        'constants': {'pebble': {'sort': 'toy', 'description': 'The example object.'}}}}
TOY = {
    'environment': TOY_ENV,
    'claims': [
        {'id': 'given', 'source': '(@pebble is marked) and (@pebble is round).\n'},
        {'id': 'rule', 'source': 'if ((@pebble is marked) and (@pebble is round)), then (@pebble is inspected).\n'},
        {'id': 'result', 'source': '@pebble is inspected.\n'}],
    'edges': [{'id': 'edge', 'premises': ['given', 'rule'], 'conclusion': 'result'}],
    'root': 'result', 'alignment': {'given': ['toy_fact'], 'rule': ['toy_rule'], 'result': ['toy_rule']},
    'queries': [], 'splits': []}
TOY_PACKET = {'premises': [{'id': 'given'}, {'id': 'rule'}], 'nodes': [{'id': 'result'}],
              'root': 'result', 'records': [{'id': 'toy_fact'}, {'id': 'toy_rule'}]}
GUIDE = r'''VE authoring contract (syntax documentation, not a dossier solution):
The environment is a JSON OBJECT with exactly language="ve.core@0", profile="relational-fol@0", spec_revision="ve-v0-draft-2026-09-20", vocabulary.
Vocabulary contains sorts, predicates, constants objects. EVERY sort has description; EVERY predicate has arguments (list of declared sorts) AND description; EVERY constant has sort AND description. Descriptions may be short. Choose your own vocabulary from the supplied text. Use ASCII identifiers [a-z][a-z0-9_]*, replacing spaces/hyphens in identifiers. Declare every used symbol, with appropriate arity and sort. Constants require @; bare names are bound variables only. No undeclared symbols, free variables or parenthetical English glosses in VE sources.
Every claim source is EXACTLY ONE closed formula, ending in a period and an actual newline. In JSON write that newline as \n. Never put several period-terminated statements in one claim. A group of declared facts or rules must be ONE nested conjunction; never drop group members. Do not add quantifiers to ground facts/rules: a named entity stays a constant, not an arbitrary variable.
Exact grammar for this relational fragment (F,G,H are metavariables, not literal VE):
term := @constant | bound_variable
F := term is unary_predicate | term binary_predicate term | term equals term | true | false | not (F) | (F) and (G) | (F) or (G) | if (F), then (G) | for every sort x, (F) | there exists sort x, (F)
source := F followed by . and newline
Spaces, commas, lower case and parentheses are exact. There is NO general parenthesized-formula production. Do not wrap a whole formula in extra parentheses. A three-member conjunction is ((F) and (G)) and (H), not (F) and (G) and (H). To conjoin rules use (if (F), then (G)) and (if (H), then (F)). A grouped premise can contain both facts and conditionals, nested with the same binary rule.
Graph contract: one claim for EACH supplied paragraph and EACH of the six declared-premise IDs, no extra or missing claims. Keep the original root. One edge per paragraph, no edge concluding a declared premise. Unique edge IDs, existing claim IDs only, acyclic dependencies. An edge lists ALL claim IDs needed to prove its conclusion, including declared rule-group premises; the node block's parent hints alone do not supply the rules to the prover. Source records are evidence, not implicit logical axioms. Keep declared-premise content and all its conditional alternatives; unassumed checks must not become facts. Do not invent a bridge, change an entity, merge distinct meanings, replace claims by true, or weaken the original root to make a proof pass. A failed proof is allowed and retained.
Alignment must have every claim ID as a key and a nonempty list of exact supplied record IDs as value, including premise entries. It records source associations, not a certificate of factual support.
Certificate contract: emit edges with id,premises,conclusion only. DO NOT author a proof/certificate, hash, AST, graph ID or environment ID. The local harness creates Claim identities, runs prove_entailment(max_steps=10000) for each edge, attaches a follows certificate when found, then runs check_argument(search=False). All edges must replay for mechanical success; this alone does not establish source fidelity. Emit queries:[] and splits:[] for this authoring-only probe.
Complete unrelated toy example, showing wire format and rule-premise wiring only. None of its symbols, claims or record IDs belongs in your answer:
''' + packed(TOY) + '\nReturn only the complete artifact JSON; no explanation or markdown. Keep descriptions concise.'


def category(result):
    error = result.get('error', '')
    if 'SyntaxError:' in error or 'exactly one closed statement' in error:
        return CATEGORIES[0]
    if 'UnknownSymbol:' in error:
        return CATEGORIES[1] if 'predicate' in error else CATEGORIES[2]
    if any(s in error for s in ('UnboundVariable:', 'TypeMismatch:', 'ShadowedVariable:')):
        return CATEGORIES[2]
    if 'Incorrect fields' in error or 'JSON object' in error:
        return CATEGORIES[5]
    if 'ResourceLimit' in error:
        return CATEGORIES[6]
    if any(s in error for s in ('coverage', 'root missing', 'cycle', 'reference', 'alignment')):
        return CATEGORIES[3]
    return CATEGORIES[7]


def replay(text, item):
    try:
        artifact = p.protocol_json(text)
    except (ValueError, TypeError) as exc:
        return {'ok': False, 'delivery_error': str(exc)}
    result = bounded('author', {'artifact': artifact, 'packet': item['payload']}, 5)
    # Add location of the actual first schema/parser failure, never a repaired source.
    if result.get('error'):
        try:
            env = Environment.from_dict(artifact['environment'])
            for claim in artifact['claims']:
                try:
                    Claim.create(env, claim['id'], claim['source'])
                except Exception as exc:
                    result['claim_id'] = claim.get('id')
                    if getattr(exc, 'span', None):
                        result['span'] = asdict(exc.span)
                    break
        except Exception:
            pass
    return result


def retained_inputs():
    paths = [p.HERE / f'runs/dev-v10/{n}' for n in ('trials.jsonl', 'local-events.jsonl', 'ratings.jsonl')]
    paths += [p.HERE / 'runs/study/costs.jsonl', p.HERE / 'materials/dev.jsonl.gz',
              p.HERE / 'materials/scored.jsonl.gz', p.HERE / 'labels.jsonl.gz']
    return {str(path.relative_to(p.ROOT)): p.sha(path) for path in paths}


def offline_audit():
    before = retained_inputs()
    items = {i['id']: i for i in p.materials('dev')}
    rows = [r for r in p.read(p.HERE / 'runs/dev-v10/trials.jsonl') if r['judge'] == 'pro']
    details, xrows = [], []
    for row in rows:
        item = items[row['item_id']]
        if row['condition'] == 'VE':
            for h in row['history']:
                if h['stage'] not in ('author', 'repair', 'defender'):
                    continue
                result = replay(h['text'], item)
                details.append({'item_id': item['id'], 'stage': h['stage'],
                    'response_sha256': digest(h['text']), 'replay': result,
                    'category': 'JSON delivery' if 'delivery_error' in result else category(result)})
        elif row['condition'] == 'X':
            author = next(h['text'] for h in row['history'] if h['stage'] == 'author')
            critic = next(h['text'] for h in row['history'] if h['stage'] == 'critic')
            questions = p.protocol_json(critic)['questions']
            texts = [p.question_text(q) for q in questions]
            commitment = p.protocol_json(author)['commitment']
            isolated = [p.request(item, 'X', 'answer', commitment=commitment, question=q, turn=n)
                        for n, q in enumerate(texts)]
            assert all(req.messages[-1]['content'] == p.packet(item, 'X') +
                       '\nFrozen commitment:\n' + commitment + '\nOne question:\n' + q
                       for req, q in zip(isolated, texts))
            followups = [h for h in row['history'] if h['stage'] == 'followup']
            followup_error = None
            for h in followups:
                try: p.question_text(p.protocol_json(h['text'])['question'])
                except ValueError as exc: followup_error = str(exc)
            xrows.append({'item_id': item['id'], 'questions': len(texts),
                          'critic_sha256': digest(critic), 'texts_unchanged': all(
                              q == (raw if isinstance(raw, str) else raw.get('question', raw.get('text')))
                              for raw, q in zip(questions, texts)),
                          'isolated_context_exact': True, 'followup_error': followup_error,
                          'historical_completed': not row['unresolved'],
                          'previous_wrapper_failure': 'single question field' in (row['protocol_error'] or '')})
    counts = Counter(d['category'] for d in details)
    assert len(details) == 36 and counts['JSON delivery'] == 6
    assert before == retained_inputs()
    result = {'time_utc': datetime.now(timezone.utc).isoformat(), 'first_failure_only': True,
              'categories': {c: counts[c] for c in CATEGORIES}, 'delivery_failures': counts['JSON delivery'],
              'artifacts': details, 'x_decoder': xrows, 'retained_hashes': before, 'paid_calls': 0}
    p.write_json(OUT / 'offline-audit.json', result)
    return result


def request(item, stage, history=None):
    if item['split'] != 'dev' or stage not in ('author', 'repair'):
        raise PreflightError('only DEV author/repair are authorized')
    req = p.request(item, 'VE', stage, history)
    messages = [dict(m) for m in req.messages]
    messages[-1]['content'] = messages[-1]['content'].replace(p.dev_revision.WIRE_GUIDE, GUIDE, 1)
    return replace(req, identity=f'{REVISION}/dev/{item["id"]}/VE/pro/{stage}/0',
                   messages=messages, max_input_tokens=8192 if stage == 'author' else 12288,
                   metadata={**req.metadata, 'feasibility_only': True, 'prompt_revision': REVISION})


def freeze():
    audit = json.loads((OUT / 'offline-audit.json').read_text())
    assert audit['retained_hashes'] == retained_inputs()
    toy = bounded('author', {'artifact': TOY, 'packet': TOY_PACKET}, 5)
    if not toy['ok']:
        raise PreflightError('toy example does not replay')
    reqs = [request(i, s) for i in p.materials('dev') for s in ('author', 'repair')]
    calibration = frozen_calibration()
    assert all(config_key(req) in calibration['configs'] for req in reqs)
    ceiling = sum((cost(r.model, r.max_input_tokens, r.billed_output_cap) for r in reqs), Decimal(0))
    assert ceiling <= 3
    paths = [Path(__file__), p.ROOT/'tests/test_p5_authoring_feasibility.py',
             p.HERE/'AUTHORING-FEASIBILITY-AMENDMENT.md', OUT/'offline-audit.json',
             p.HERE/'freeze.json', p.ROOT/'ve_experiments/paid.py', p.ROOT/'uv.lock']
    paths += list((p.ROOT/'experiments').glob('p5*.py')) + list((p.ROOT/'ve').glob('*.py'))
    manifest = {'time_utc': datetime.now(timezone.utc).isoformat(), 'revision': REVISION,
                'cap_usd': '3', 'worst_case_usd': str(ceiling), 'max_calls': 24,
                'item_ids': [i['id'] for i in p.materials('dev')], 'guide': GUIDE,
                'guide_sha256': digest(GUIDE), 'toy_replay': toy,
                'models': p.MODELS, 'rates': p.RATES,
                'calibrated_configs': sorted({config_key(r) for r in reqs}),
                'author_requests': [asdict(r) for r in reqs if r.metadata['role'] == 'author'],
                'hashes': {str(path.relative_to(p.ROOT)): p.sha(path) for path in paths},
                'retained_hashes': audit['retained_hashes']}
    p.write_json(OUT/'freeze.json', manifest)
    return {'worst_case_usd': str(ceiling), 'max_calls': 24, 'toy_replay': toy['ok']}


def run(cap):
    if not Decimal(0) < cap <= Decimal(3):
        raise PreflightError('explicit cap must be in (0,3]')
    manifest = json.loads((OUT/'freeze.json').read_text())
    for path, sha in manifest['hashes'].items():
        if p.sha(p.ROOT/path) != sha: raise PreflightError('probe freeze changed: '+path)
    if retained_inputs() != manifest['retained_hashes']:
        raise PreflightError('retained inputs changed')
    if cap < Decimal(manifest['worst_case_usd']):
        raise PreflightError('cap cannot cover complete worst-case probe')
    book = Ledger(OUT/'costs.jsonl', cap)
    client = PaidClient(p.VertexBackend(), book)
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
                if stage == 'author':
                    history = [{'item_id': item['id'], 'stage': 'author', 'text': reply.text},
                               {'item_id': item['id'], 'stage': 'diagnostics',
                                'record': {**p.bounded_record(result), **{k: result[k] for k in ('claim_id', 'span', 'delivery_error') if k in result}}}]
                if result.get('ok'): break
            row = {'item_id': item['id'], 'stages': stages, 'ok': stages[-1]['replay']['ok']}
            results.append(row)
            p.write_json(OUT/'results.json', results)
            print(f'[{len(results)}/12] replay={row["ok"]}; stages={len(stages)}', flush=True)
    finally:
        client.close()
    assert retained_inputs() == manifest['retained_hashes']
    paid = p.read(book.path)
    pending, spent, *_ = Ledger.state(paid)
    summary = {'revision': REVISION, 'n': len(results), 'successes': sum(r['ok'] for r in results),
               'initial_successes': sum(r['stages'][0]['replay']['ok'] for r in results),
               'rate': sum(r['ok'] for r in results)/len(results),
               'calls': sum(r['event']=='complete' for r in paid), 'spend_usd': str(spent),
               'pending_usd': str(sum(pending.values(), Decimal(0))), 'cap_usd': str(cap),
               'judges': 0, 'scored_items': 0, 'retained_inputs_unchanged': True,
               'source_fidelity_assessed': False}
    p.write_json(OUT/'summary.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['audit', 'freeze', 'run'])
    parser.add_argument('--cap-usd', type=Decimal, default=Decimal(0))
    args = parser.parse_args()
    result = offline_audit() if args.action == 'audit' else freeze() if args.action == 'freeze' else run(args.cap_usd)
    print(packed({k: v for k, v in result.items() if k not in ('artifacts', 'x_decoder', 'retained_hashes')}))

if __name__ == '__main__': main()
