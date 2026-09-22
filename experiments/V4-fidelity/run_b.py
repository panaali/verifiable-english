"""Frozen full-size B run, serial k=3; resume successes without resampling errors."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import subprocess

from fidelity import HERE, SYSTEM, dump, prompt, score
from ve_experiments.claude_cli import ClaudeCLI, Controls, EndpointError

CATEGORIES = ('negation scope', 'xor/or', 'quantifier', 'predicate conflation', 'other')


def endpoint_failure(message, raw):
    """Model/control drift is always fatal; an allowed quota event is not an error."""
    fatal=any(s in message.lower() for s in ('drift','model mismatch','date expired','previously started'))
    errors=[message]
    for line in raw.splitlines():
        try: record=json.loads(line)
        except json.JSONDecodeError: continue
        if record.get('type')=='result' and record.get('is_error'):
            errors.append(str(record.get('result','')))
        if record.get('error'):
            errors.append(str(record['error']))
        info=record.get('rate_limit_info',{})
        if record.get('type')=='rate_limit_event' and info.get('status') in ('rejected','rate_limited'):
            errors.append('rate_limit')
    error_text=' '.join(errors).lower()
    rate=any(s in error_text for s in ('rate_limit','rate limit','usage limit','hit your limit','quota','overloaded'))
    return fatal, rate


def taxonomy(gold, candidate):
    """Multi-label structural diagnostics, not a semantic or human adjudication."""
    from fidelity import features
    g, c = features(gold), features(candidate)
    out = []
    # Predicate/argument diagnostics independent of connective path.
    select = lambda rows, key: [r[key] for r in rows if key in r]
    if select(g, 'predicate') != select(c, 'predicate'):
        out.append('predicate conflation')
    if ([r for r in g if 'quantifier' in r] != [r for r in c if 'quantifier' in r]
            or select(g, 'arguments') != select(c, 'arguments')):
        out.append('quantifier')
    def paths(rows, op):
        return [r['path'] for r in rows if r.get('operator') == op]
    if paths(g, 'or') != paths(c, 'or') or (paths(g, 'and') != paths(c, 'and') and paths(g, 'or')):
        out.append('xor/or')
    if paths(g, 'not') != paths(c, 'not'):
        out.append('negation scope')
    return out or ['other']


def scored_sample(item, text):
    result = score(item, text)
    diags = result.get('translations', {})
    result['faithful_exact'] = (len(diags) == len(item['premises'])+1
                                and all(d['exact_structure'] for d in diags.values()))
    gold = {p['id']: p['gold_ast'] for p in item['premises']}
    gold['query'] = item['query']['gold_ast']
    failures = []
    for pid, diag in diags.items():
        if not diag['exact_structure']:
            failures.append({'row': pid, 'categories': taxonomy(gold[pid], diag['submitted_ast']),
                             'relation': diag['relation']})
    if not result['faithful_exact'] and not failures:
        failures.append({'row': None, 'categories': ['other'], 'reason': result.get('error', 'missing rows')})
    result['translation_failures'] = failures
    return result


def summarize(items, results):
    groups = defaultdict(list)
    counts = Counter({c: 0 for c in CATEGORIES})
    sample_counts = Counter({c: 0 for c in CATEGORIES})
    for item in items:
        for k in range(3):
            r = results.get((item['id'], k), {})
            groups['all'].append(r)
            groups['label:'+item['label']].append(r)
            groups['depth:'+str(item['depth'])].append(r)
            groups['query:'+item['query']['gold_ast'][0]].append(r)
            seen = set()
            for failure in r.get('translation_failures', []):
                counts.update(failure['categories']); seen.update(failure['categories'])
            sample_counts.update(seen)
    metrics = ('faithful_exact', 'faithful_mechanical', 'certified_answer', 'answer_correct', 'grounded_certificate')
    def group_summary(rs):
        taxonomy_counts=Counter({c:0 for c in CATEGORIES})
        for r in rs:
            taxonomy_counts.update({c for f in r.get('translation_failures',[]) for c in f['categories']})
        return {'n':len(rs),**{m:sum(bool(r.get(m)) for r in rs) for m in metrics},
                'failure_taxonomy_samples_multilabel':dict(taxonomy_counts)}
    return {'scheduled_items': len(items), 'scheduled_samples': len(items)*3,
            'scored_samples': len(results),
            'by_type': {g:group_summary(rs) for g,rs in groups.items()},
            'all_three_exact_items': sum(all(results.get((i['id'],k),{}).get('faithful_exact') for k in range(3)) for i in items),
            'taxonomy_diagnostics_multilabel_including_unparsed_placeholders': dict(counts),
            'taxonomy_samples_multilabel': dict(sample_counts),
            'errors': dict(Counter(r.get('error') for r in results.values() if r.get('error')))}


def main():
    if (HERE/'results/b/STOP.json').exists():
        raise EndpointError('Study permanently stopped; new endpoint audit and preregistration required')
    # Freeze check is local and occurs before spending; timestamp proof must exist.
    for line in (HERE/'HASHES').read_text().splitlines():
        expected, name = line.split('  ', 1)
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == expected, name
        subprocess.run(['git','diff','--exit-code','HEAD','--',str(HERE/name)], check=True, capture_output=True)
    assert (HERE/'HASHES.ots').is_file()
    items = [json.loads(x) for x in (HERE/'items-b.jsonl').read_text().splitlines()]
    out = HERE/'results/b'; out.mkdir(parents=True, exist_ok=True)
    client = ClaudeCLI(out/'ledger.jsonl', Controls(output_tokens=14000, timeout_s=300), max_calls=180)
    results = {}
    for p in out.glob('*-score.json'):
        r=json.loads(p.read_text()); results[r['id'],r['sample_index']]=r
    limits = 0
    for item in items:
        for k in range(3):
            if (item['id'],k) in results: continue
            try:
                row=client.sample(item['id'],SYSTEM,prompt(item),k)
                r=scored_sample(item,row['text'])
            except Exception as exc:
                # No same-sample retries. Model/context drift stops immediately;
                # a second quota/rate-limit failure stops the entire study.
                last=json.loads(client.ledger.read_text().splitlines()[-1]) if client.ledger.exists() else {}
                message=str(exc)
                fatal,rate=endpoint_failure(message,last.get('raw_stream',''))
                limits += int(rate)
                r={'id':item['id'],'error':message,'endpoint_failure':True,
                   'rate_limit':rate,'translation_failures':[{'row':None,'categories':['other']}]}
                fatal=fatal or limits>=2
                if fatal:
                    r['sample_index']=k; results[item['id'],k]=r
                    dump(out/f"{item['id']}-{k}-score.json",r)
                    dump(out/'summary.json',summarize(items,results))
                    raise EndpointError(f'STUDY STOP: {message}; rate failures={limits}') from exc
            r['sample_index']=k; results[item['id'],k]=r
            dump(out/f"{item['id']}-{k}-score.json",r)
            dump(out/'summary.json',summarize(items,results))
            print(json.dumps({'completed':len(results),'id':item['id'],'k':k,
                              **{m:r.get(m) for m in ('faithful_exact','certified_answer','answer_correct','error')}}),flush=True)


if __name__=='__main__': main()
