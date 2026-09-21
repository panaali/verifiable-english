"""Check all witnesses, adapter invariants, independent graph truth, and Lean agreement."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from ve import Environment, FiniteModel, document_from_data, evaluate, parse, print_document, meaning_id
from ve.identity import source_id

OUT = Path(__file__).resolve().parent


def reachable(edges,a,b,star=False):
    if star and a==b:return True
    seen=set(); todo=[y for x,y in edges if x==a]
    while todo:
        x=todo.pop()
        if x==b:return True
        if x not in seen:
            seen.add(x);todo.extend(y for u,y in edges if u==x)
    return False


def function(rows,domain,total):
    keys=[row[0] for row in rows]
    assert len(keys)==len(set(keys)), 'nonfunctional field'
    if total:assert set(keys)==set(domain), 'missing total field'


def adapter_check(row,raw):
    env=Environment(row['environment']);m=FiniteModel.from_dict(env,raw)
    a=row['adapter']; rs=m.relations;ds=m.domains
    if row['dataset']=='cedar':
        for p in a['request_fields']:function(rs[p],ds['request'],True)
        for p in a['entity_attributes']+a['set_attributes']:function(rs[p],ds['entity'],False)
        assert all(not reachable(rs['parent'],x,x) for x in ds['entity']), 'cyclic Cedar hierarchy'
        tags=[x[0] for p in a['type_tags'] for x in rs[p]]
        assert sorted(tags)==sorted(ds['entity']), 'entity type tags must partition the carrier'
        assert set(a['uid_map'])==set(ds['entity'])
        assert len(set(a['uid_map'].values()))==len(ds['entity']), 'distinct local entities must represent distinct UIDs'
        for p in a['type_tags']:
            for (x,) in rs[p]:
                assert p=='type_'+a['uid_map'][x].split('::"')[0].replace('::','_').lower()
    else:
        for p in a.get('total_functions',[]):function(rs[p],ds[env.predicates[p].arguments[0]],True)
        for p in a.get('partial_functions',[]):function(rs[p],ds[env.predicates[p].arguments[0]],False)
        if 'entry_state' in rs:
            # Every tuple has exactly one value in each coordinate, already checked above.
            st,nd,val=(dict(rs[p]) for p in ('entry_state','entry_node','entry_value'))
            keys=[(st[e],nd[e]) for e in ds['data_entry']]
            assert len(keys)==len(set(keys))
            assert set(keys)==set(rs['active'])
            assert len({i for n,i in rs['node_id']})==len(ds['node'])
    return m


def cedar_truth(row,m):
    rs=m.relations;cs=m.constants
    one=lambda p,x: next((y for a,y in rs[p] if a==x),None)
    rtc=lambda a,b: a is not None and b is not None and reachable(rs['parent'],a,b,True)
    item=row['id']
    for (q,) in [(x,) for x in m.domains['request']]:
        p,a,r=(one(field,q) for field in row['adapter']['request_fields'])
        if 'sales_orgs/templated/' in item:
            value=rtc(a,cs['action_group']) and one('owner',r)==p
        elif 'github_example/policies.cedar#5' in item:
            value=a==cs['action_target'] and rtc(p,one('writers',r))
        elif 'sales_orgs/static/' in item:
            collection=one('viewer_markets',r)
            value=rtc(a,cs['action_group']) and collection is not None and any(
                rtc(p,g) for c,g in rs['set_member'] if c==collection)
        elif 'github-templates/' in item:
            value=rtc(p,cs['principal_slot']) and a==cs['action_target'] and r==cs['resource_slot']
        elif 'PhotoApp/' in item:
            value=rtc(p,cs['family']) and a==cs['action_target'] and rtc(r,cs['album'])
        elif 'gdrive-templates/' in item:
            value=rtc(p,cs['principal_slot']) and a==cs['action_target'] and rtc(r,cs['resource_slot'])
        elif 'policies_3c.cedar' in item:
            value=p==cs['alice'] and rtc(r,cs['album'])
        elif 'policies_2a.cedar' in item:
            value=rtc(p,cs['friends']) and a==cs['action_target'] and r==cs['photo']
        elif 'cedar-java-partial-evaluation/' in item:
            value=rtc(p,cs['admin']) and rtc(a,cs['read_group']) and rtc(r,cs['protected'])
        elif 'policies_3a.cedar' in item:
            value=a==cs['action_target'] and rtc(r,cs['album'])
        else:raise AssertionError(item)
        if ((q,) in rs['permit_contribution']) != value:return False
    return True


def alloy_truth(row,m):
    rs=m.relations;ds=m.domains;cs=m.constants
    if '@81' in row['id'] or '@80' in row['id']:
        edges=[(a,b) for a,b in rs['next_id'] if b!=cs['origin']]
        return reachable(edges,cs['left_id'],cs['right_id'])
    if '@5190' in row['id']:
        edges=set(rs['parent'])|{(b,a) for a,b in rs['parent']}
        return all(reachable(edges,h,g,True) for g in ds['gsa'] for h in ds['gsa'])
    if '@282' in row['id']:
        return not any(reachable(rs['xtends'],t,t) for t in ds['jtype'])
    assert '@4943' in row['id']
    if len(ds['node'])!=1:return False
    if {n for s,n in rs['active']}!=set(ds['node']):return False
    node_id=dict(rs['node_id']);succ=dict(rs['successor'])
    st,nd,val=(dict(rs[p]) for p in ('entry_state','entry_node','entry_value'))
    data={(st[e],nd[e]):val[e] for e in ds['data_entry']}
    for s in ds['state']:
        active={n for t,n in rs['active'] if t==s}
        for n in active:
            nx=succ[data[s,n]]
            edges=[(a,b) for a,b in rs['next_id'] if b!=node_id[n]]
            if any(reachable(edges,node_id[k],node_id[nx]) for k in active-{n}):return False
            if nx==n and len(active)!=1:return False
    return True


def validate():
    manifest=json.loads((OUT/'manifest.json').read_text())
    allowed=set(re.findall(r'^\| `([^`]+)` \| (?:REIFIED|OPAQUE|NO) →', (ROOT/'docs/spec/v0.1-coverage.md').read_text(),re.M))
    assert len(manifest['items'])==15
    assert len({x['id'] for x in manifest['items']})==15
    assert sum(x['dataset']=='cedar' for x in manifest['items'])==10
    assert sum(x['dataset']=='alloy' for x in manifest['items'])==5
    samples={}
    cases=[];reports=[]
    for entry in manifest['items']:
        row=json.loads((OUT/entry['file']).read_text())
        assert row['id']==entry['id'] and row['id'] in allowed
        prov=row['provenance'];key=(prov['git_revision'],prov['path'])
        if key not in samples:
            raw=subprocess.check_output(['git','show',':'.join(key)],cwd=ROOT,text=True)
            samples[key]={r['id']:r for r in map(json.loads,raw.splitlines())}
        assert row['source']==samples[key][row['id']]['text']
        assert hashlib.sha256(row['source'].encode()).hexdigest()==prov['text_sha256']
        env=Environment(row['environment']);doc=document_from_data(env,row['ast'])
        assert parse(env,row['strict'])==doc
        assert (OUT/entry['file'].replace('.json','.ve')).read_text()==print_document(env,doc)==row['strict']
        result={'id':row['id'],'file':entry['file'],'meaning_id':meaning_id(env,doc),
                'source_id':source_id(row['strict'],env),'model_results':[]}
        for expected,key in ((True,'true_model'),(False,'false_model')):
            m=adapter_check(row,row[key])
            python=evaluate(env,doc,m,trace=False)
            independent=cedar_truth(row,m) if row['dataset']=='cedar' else alloy_truth(row,m)
            assert python.value is expected and independent is expected,(row['id'],key)
            label=row['id']+':'+key
            cases.append({'id':label,'environment':row['environment'],'model':row[key],
                          'ast':row['ast'],'source':row['strict']})
            result['model_results'].append({'model':key,'expected':expected,'python':python.value,
                                            'independent_graph_check':independent,'model_id':m.model_id})
        reports.append(result)
    executable=ROOT/'lean/.lake/build/bin/ve_conformance'
    assert executable.exists(),'Build Lean first, then run this checker sequentially.'
    proc=subprocess.run([str(executable)],input=json.dumps(cases),text=True,capture_output=True,timeout=120)
    assert proc.returncode==0,proc.stdout+proc.stderr
    results=json.loads(proc.stdout)
    assert len(results)==30
    for i,result in enumerate(results):
        expected=(i%2==0)
        assert result['id']==cases[i]['id']
        assert result['status']=='ok' and result['values']==[expected]
        assert result['canonical']==cases[i]['source']
        reports[i//2]['model_results'][i%2]['lean']=result['values'][0]
    return {'status':'PASS','profile':'closure@0','cedar_items':10,'alloy_items':5,
            'models':30,'python_lean_agree':30,'items':reports,
            'limits':['Finite tests do not prove source-to-VE translation equivalence.',
                      'Adapter validation checks the recorded relevant relational signatures; it is not full Cedar schema or Alloy module validation.',
                      'The independent graph checks are handwritten projections of the sampled claims, not runs of Cedar or Alloy engines.']}


if __name__=='__main__':
    report=validate()
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"PASS: {report['cedar_items']} Cedar + {report['alloy_items']} Alloy; {report['models']} models checked by Python, independent graph checks, and Lean.")
