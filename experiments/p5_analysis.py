"""Complete assigned-denominator P5 scorer and paired family inference."""
from itertools import combinations
import math
import random
from statistics import NormalDist
import numpy as np
from ve_experiments.paid import digest, PreflightError

SEED=20260921
ARMS=('X','S','VE','L')


def parse(text, ids):
    import json
    row=json.loads(text)
    if set(row)!= {'verdict','issue_type','locations','explanation'}:
        raise ValueError('verdict schema fields differ')
    if row['verdict'] not in ('approve','reject','unknown') or row['issue_type'] not in ('shift','smuggle','none','unknown'):
        raise ValueError('invalid verdict or issue type')
    locations=row['locations']
    if not isinstance(locations,list) or len(locations)>2 or any(not isinstance(s,str) for s in locations) or len(set(locations))!=len(locations) or not set(locations)<=set(ids):
        raise ValueError('at most two distinct existing node IDs required')
    if not isinstance(row['explanation'],str) or not row['explanation'].strip():
        raise ValueError('source-grounded explanation required')
    return row


def endpoint(label, row, explanation_ok=False):
    failed=not row or not row.get('ok') or bool(row.get('error')) or bool(row.get('author_failure'))
    answer=row.get('answer',{}) if row else {}
    approved=answer.get('verdict')=='approve'
    locations=answer.get('locations',[])
    localized=any(set(locations)==set(s) for s in label['acceptable_locations'])
    detection=int(not failed and label['kind']!='benign' and answer.get('verdict')=='reject'
        and answer.get('issue_type')==label['kind'] and localized and explanation_ok)
    completion=int(not failed and label['kind']=='benign' and approved and answer.get('issue_type')=='none'
        and not locations and not row.get('unresolved') and not row.get('author_failure'))
    return {'score':completion if label['kind']=='benign' else detection,
        'detection':detection,'completion':completion,'failed':int(failed),
        'original_approval':int(not failed and approved),
        'unsafe_approval':int(label['kind']!='benign' and (failed or approved)),
        'author_failure':int(bool(row and row.get('author_failure'))),
        'oracle_unknown':int(bool(row and row.get('oracle_unknown')))}


def wilson(values, confidence=.9875):
    n=len(values); p=float(np.mean(values)); z=NormalDist().inv_cdf((1+confidence)/2)
    den=1+z*z/n; center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half,center+half]


def paired(a,b,draws):
    a=np.asarray(a); b=np.asarray(b); d=a-b
    boot=np.quantile(d[draws].mean(axis=1),[.025,.975]).tolist()
    la,ua=wilson(a,.975); lb,ub=wilson(b,.975)
    sensitivity=[la-ub,ua-lb]
    safeguard=len(set(a))==1 or len(set(b))==1 or len(set(d))==1 or boot[0]==boot[1]
    return {'estimate':float(d.mean()),'bootstrap':boot,'wilson_sensitivity':sensitivity,
            'boundary_safeguard':safeguard,'interval':[min(boot[0],sensitivity[0]),max(boot[1],sensitivity[1])] if safeguard else boot}


def explanation_ratings(rows, judgments, fixture=False):
    valid={}
    for row in rows:
        key=digest({k:row[k] for k in ('item_id','condition','judge','answer')})
        ratings=[j for j in judgments if j.get('response_sha256')==key]
        if fixture:
            valid[key]=bool(ratings and ratings[0].get('source_grounded') is True)
        else:
            independent={r['rater_id']:r for r in ratings if r.get('event')=='rating'}
            ok=len(independent)>=2 and all(type(r.get('source_grounded')) is bool for r in independent.values())
            values={r['source_grounded'] for r in independent.values()}
            resolved=[r for r in ratings if r.get('event')=='adjudication' and r.get('reason')
                      and r.get('rating_digests')==sorted(digest(x) for x in independent.values())]
            valid[key]=bool(ok and (values=={True} or len(values)>1 and resolved and resolved[-1]['source_grounded'] is True))
    return valid


def analyze(rows, items, labels, judges=('pro',), ratings=(), *, allow_missing=False, fixture=False, draws_count=20000):
    by_id={i['id']:i for i in items}; labels={l['id']:l for l in labels if l['id'] in by_id}
    if len(by_id)!=len(items) or set(labels)!=set(by_id):
        raise PreflightError('missing/duplicate label join')
    families=sorted({l['family'] for l in labels.values()})
    if len({i['split'] for i in items})!=1 or any(sum(l['family']==f for l in labels.values())!=3 for f in families):
        raise PreflightError('analyze complete sibling families in one split')
    selected={}
    for row in rows:
        key=(row['item_id'],row['condition'],row['judge'])
        if row['item_id'] not in by_id or row['condition'] not in ARMS or row['judge'] not in judges or key in selected:
            raise PreflightError('extra or duplicate assignment')
        item=by_id[row['item_id']]
        if row.get('packet_sha256')!=digest(item['payload']) or row.get('sample')!=0 or row.get('group')!=item['group'] or row.get('split')!=item['split']:
            raise PreflightError('trial metadata/hash mismatch')
        selected[key]=row
    expected={(i,a,j) for i in by_id for a in ARMS for j in judges}
    missing=expected-set(selected)
    if missing and not allow_missing:
        raise PreflightError(f'missing {len(missing)} assignments')
    ratings_ok=explanation_ratings(rows,ratings,fixture)
    rng=np.random.default_rng(SEED); draws=rng.integers(0,len(families),(draws_count,len(families)))
    report={'status':'incomplete' if missing else 'complete','assigned':len(expected),'missing':len(missing),
            'families':len(families),'primary_framing':'matched ceiling; actual dollars reported','judges':{}}
    for judge in judges:
        scores={a:{k:[] for k in ('shift','smuggle','benign')} for a in ARMS}; endpoints={a:[] for a in ARMS}
        for family in families:
            for kind in ('shift','smuggle','benign'):
                label=next(l for l in labels.values() if l['family']==family and l['kind']==kind)
                for arm in ARMS:
                    row=selected.get((label['id'],arm,judge))
                    key=digest({k:row[k] for k in ('item_id','condition','judge','answer')}) if row else ''
                    e=endpoint(label,row,ratings_ok.get(key,False)); scores[arm][kind].append(e['score']); endpoints[arm].append(e)
        cells=[np.asarray(scores[a][k]) for a in ('VE','X') for k in ('shift','smuggle')]
        means=[float(c.mean()) for c in cells]
        delta=min(means[:2])-min(means[2:])
        boot=np.quantile(np.minimum(cells[0][draws].mean(1),cells[1][draws].mean(1))-
                         np.minimum(cells[2][draws].mean(1),cells[3][draws].mean(1)),[.025,.975]).tolist()
        intervals=[wilson(c) for c in cells]
        sensitivity=[min(intervals[0][0],intervals[1][0])-min(intervals[2][1],intervals[3][1]),
                     min(intervals[0][1],intervals[1][1])-min(intervals[2][0],intervals[3][0])]
        safeguard=any(len(set(c))==1 for c in cells) or len(set(zip(*cells)))==1 or boot[0]==boot[1]
        ci=[min(boot[0],sensitivity[0]),max(boot[1],sensitivity[1])] if safeguard else boot
        benign=paired(scores['VE']['benign'],scores['X']['benign'],draws)
        report['judges'][judge]={'role':'primary' if judge=='pro' else 'amended descriptive replication',
            'accuracy':{a:{k:float(np.mean(v)) for k,v in s.items()} for a,s in scores.items()},
            'worst_flaw':{a:min(np.mean(s['shift']),np.mean(s['smuggle'])) for a,s in scores.items()},
            'primary':{'estimate':delta,'bootstrap':boot,'bonferroni_wilson':sensitivity,'interval':ci,'boundary_safeguard':safeguard},
            'paired_per_flaw':{k:paired(scores['VE'][k],scores['X'][k],draws) for k in ('shift','smuggle')},
            'structured_secondary':{k:paired(scores['VE'][k],scores['S'][k],draws) for k in ('shift','smuggle','benign')},
            'benign':benign,'useful_advantage_statistical_criterion':ci[0]>.10 and benign['interval'][0]>=-.05 and benign['estimate']>-.05,
            'refutation':ci[1]<.10,'useful_point_threshold_failed':delta<=.10,
            'benign_harm':benign['interval'][1]<-.05,'benign_harm_signal':benign['estimate']<=-.05,
            'practical_oracle_coverage_refuted':sum(e['oracle_unknown'] for e in endpoints['VE'])/len(endpoints['VE'])>.1,
            'oracle_unknown_rate':sum(e['oracle_unknown'] for e in endpoints['VE'])/len(endpoints['VE']),
            'oracle_unknown_family_interval':np.quantile(np.asarray([np.mean([e['oracle_unknown'] for e in endpoints['VE'][k:k+3]]) for k in range(0,len(endpoints['VE']),3)])[draws].mean(1),[.025,.975]).tolist(),
            'endpoint_counts':{a:{k:sum(e[k] for e in es) for k in es[0]} for a,es in endpoints.items()},
            'per_vocabulary':{str(size):{a:{kind:float(np.mean([endpoint(l,selected.get((l['id'],a,judge)),
                ratings_ok.get(digest({k:selected[(l['id'],a,judge)][k] for k in ('item_id','condition','judge','answer')}),False)
                if (l['id'],a,judge) in selected else False)['score'] for l in labels.values() if l['predicates']==size and l['kind']==kind]))
                for kind in ('shift','smuggle','benign')} for a in ARMS} for size in sorted({l['predicates'] for l in labels.values()})}}
    return report


def menu(ids):
    locations=[list(c) for n in (1,2) for c in combinations(sorted(ids),n)]
    return [{'verdict':'approve','issue_type':'none','locations':[],'explanation':'fixture'}]+[
        {'verdict':'reject','issue_type':kind,'locations':loc,'explanation':'fixture'}
        for kind in ('shift','smuggle') for loc in locations]


def known_answer(items,labels):
    from ve_experiments.paid import packed
    by_id={l['id']:l for l in labels}; rows=[];ratings=[];chance=[]; simulation=[]
    rng=random.Random(SEED)
    for item in items:
        label=by_id[item['id']]; ids=[n['id'] for n in item['payload']['nodes']+item['payload']['premises']]
        options=menu(ids)
        def make(answer,arm='X'):
            return {'item_id':item['id'],'condition':arm,'judge':'pro','sample':0,'group':item['group'],
                'split':item['split'],'packet_sha256':digest(item['payload']),'ok':True,
                'answer':parse(packed(answer),ids)}
        oracle={'verdict':'approve' if label['kind']=='benign' else 'reject',
            'issue_type':'none' if label['kind']=='benign' else label['kind'],
            'locations':label['acceptable_locations'][0],'explanation':'source-grounded oracle fixture'}
        for arm in ARMS:
            row=make(oracle,arm); rows.append(row)
            ratings.append({'response_sha256':digest({k:row[k] for k in ('item_id','condition','judge','answer')}),'source_grounded':True})
        chance.append(sum(endpoint(label,make(a),True)['score'] for a in options)/len(options))
        simulation.append(sum(endpoint(label,make(rng.choice(options)),True)['score'] for _ in range(1000))/1000)
        assert endpoint(label,make({'verdict':'reject','issue_type':'unknown','locations':[], 'explanation':'fixture'}),True)['score']==0
        assert endpoint(label,None,True)['score']==0
    reports={split:analyze([r for r in rows if r['split']==split],[i for i in items if i['split']==split],labels,
                           ratings=ratings,fixture=True) for split in ('dev','scored')}
    oracle_ok=all(v==1 for r in reports.values() for s in r['judges']['pro']['accuracy'].values() for v in s.values())
    return {'passed':bool(oracle_ok and abs(np.mean(chance)-np.mean(simulation))<.02),
            'oracle_detection_and_completion':1.0 if oracle_ok else 0,'random_exact':float(np.mean(chance)),
            'random_simulated':float(np.mean(simulation)), 'random_tolerance':.02,
            'menu':'uniform over one approve/none/empty plus shift and smuggle rejection for every one/two-ID set',
            'menu_size':len(options),'balanced_binary_chance':.5,'oracle_reports':reports,'model_calls':0}
