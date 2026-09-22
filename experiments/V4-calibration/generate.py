"""Fresh VE-checkable calibration families with seven crossed difficulty levers."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys

import ve

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'V4-fidelity'))
from fidelity import environment, english, to_ast
from generator import sat

LEVERS=('uncertain','cases','xor','modus_tollens','near_miss','nested_quantifiers','belief_inconsistent')
SEEDS={'smoke':2026092220,'dev':2026092221,'heldout':2026092222}


def write(path, obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')


def model(env, relations):
    return {'complete':True,'domains':{'person':['a','b']},'constants':{'ada':'a','ben':'b'},
            'relations':{p:relations.get(p,[]) for p in env['vocabulary']['predicates']}}


def validate(item, witnesses):
    env=ve.Environment.from_dict(item['environment'])
    fs=[ve.formula_from_data(env,p['gold_ast']) for p in item['premises']]
    q=ve.formula_from_data(env,item['query']['gold_ast'])
    for f in fs+[q]:
        assert ve.parse(env,ve.print_formula(env,f)+'.\n').formulas==(f,)
    checked={}
    for polarity,m in witnesses.items():
        finite=ve.FiniteModel.from_dict(env,m)
        assert all(ve.evaluate(env,f,finite).value is True for f in fs)
        assert ve.evaluate(env,q,finite).value is (polarity=='True')
        checked[polarity]=m
    if item['label']=='Uncertain':
        assert set(checked)=={'True','False'}
        evidence={'kind':'two_checked_countermodels'}
    else:
        assert item['label'] in checked # consistency, no vacuous entailment
        goal=q if item['label']=='True' else ve.Not(q)
        result=ve.prove_entailment(env,fs,goal,max_steps=10000)
        assert result.status=='Found', (item['id'],result)
        assert ve.check_entailment_certificate(env,fs,goal,result.certificate,max_steps=10000).valid
        evidence={'kind':'replayed_tableau','certificate':result.certificate,'steps':result.steps}
    item.update(gold_witnesses=checked,gold_evidence=evidence)


def generate_item(split,lever,index,target_words=300):
    rng=random.Random(f'{SEEDS[split]}:{lever}:{index}')
    belief=lever=='belief_inconsistent' or index%3==2
    near=lever=='near_miss' or index%3==1
    active=[lever]
    if belief and 'belief_inconsistent' not in active: active.append('belief_inconsistent')
    if near and 'near_miss' not in active: active.append('near_miss')
    label=('True','False','Uncertain')[index%3]
    preds={}; mapping={}; texts={}
    ids=list(range(6)); rng.shuffle(ids)
    neutral=['is marked amber','is marked cobalt','is marked silver','is marked violet','is marked teal','is marked copper']
    beliefs=['is a robin','is a fish','breathes underwater','is a mammal','is a mineral','is alive']
    for i,name in enumerate('abcdef'):
        pred=f'p{ids[i]}'; phrase=(beliefs if belief else neutral)[i]
        preds[pred]={'arguments':['person'],'description':phrase}
        mapping[name]=['unary',pred,['const','ada']]; texts[name]='Ada '+phrase
    n=lambda x:('¬',x)
    imp=lambda a,b:('→',a,b)
    if lever in ('uncertain','near_miss'):
        # The near-miss bridge targets e, not b; no closed-world assumption.
        sk=['a',imp('a','b'),imp('e','c'),imp('c','d')]
        if lever=='near_miss' and label!='Uncertain': sk.append(imp('b','c'))
        else: label='Uncertain'
        query=n('d') if label=='False' else 'd'
    elif lever=='cases':
        sk=[('∨','a','b'),imp('a','c'),imp('b','c'),imp('c','d')]
        query='e' if label=='Uncertain' else n('d') if label=='False' else 'd'
    elif lever=='xor':
        sk=[('⊕','a','b'),imp('b','c'),imp('c','d')]
        if label!='Uncertain': sk.append('a')
        query=n('b') if label=='True' else 'b'
    elif lever=='modus_tollens':
        sk=[imp('a','b'),imp('b','c'),imp('c','d')]
        if label!='Uncertain': sk.append(n('d'))
        query=n('a') if label=='True' else 'a'
    else:
        sk=['a',imp('a','b'),imp('b','c'),imp('c','d')]
        query='e' if label=='Uncertain' else n('d') if label=='False' else 'd'
    if near: sk.extend([imp('e','b'),imp('f','e')])
    premises=[{'english':english(f,texts)+'.','gold_ast':to_ast(f,mapping)} for f in sk]
    q={'english':english(query,texts)+'.','gold_ast':to_ast(query,mapping)}
    raw_witnesses={}
    for polarity in (True,False):
        assignment=sat(sk+[query if polarity else n(query)])
        if assignment is not None:
            raw_witnesses[str(polarity)]={mapping[a][1]:[['a']] if assignment.get(a,False) else [] for a in mapping}
    if lever=='nested_quantifiers':
        # Quantifiers interact through shared predicates; these are not opaque atoms.
        preds={'r':{'arguments':['person','person'],'description':'admires (first person to second person)'},
               's':{'arguments':['person','person'],'description':'follows (first person to second person)'}}
        if belief:
            preds['r']['description']='is the parent of (first person to second person)'
            preds['s']['description']='is younger than (first person to second person)'
        rphrase='is the parent of' if belief else 'admires'
        sphrase='is younger than' if belief else 'follows'
        r=['binary','r',['var',1],['var',0]]
        s=['binary','s',['var',0],['var',1]]
        premises=[{'english':f'For every person x, there is a person y such that x {rphrase} y (y may depend on x).',
                   'gold_ast':['forall','person',['exists','person',r]]},
                  {'english':f'For every person x and every person y, if x {rphrase} y, then y {sphrase} x.',
                   'gold_ast':['forall','person',['forall','person',['implies',r,s]]]}]
        target=['forall','person',['exists','person',s]]
        if label=='Uncertain':
            target=['exists','person',['forall','person',['binary','s',['var',1],['var',0]]]]
            qe=f'There is a person y such that for every person x, y {sphrase} x.'
        else: qe=f'For every person x, there is a person y such that y {sphrase} x (y may depend on x).'
        q={'english':('It is not the case that ('+qe+').' if label=='False' else qe),
           'gold_ast':['not',target] if label=='False' else target}
        diagonal=[['a','a'],['b','b']]; full=[[a,b] for a in 'ab' for b in 'ab']
        raw_witnesses=({'True':{'r':diagonal,'s':full},'False':{'r':diagonal,'s':diagonal}}
                       if label=='Uncertain' else {label:{'r':diagonal,'s':diagonal}})
        if near:
            # Converse near-miss over a separate relation, never a hidden axiom.
            preds['t']={'arguments':['person','person'],'description':'almost follows (first person to second person)'}
            premises.append({'english':'Ada almost follows Ben.','gold_ast':['binary','t',['const','ada'],['const','ben']]})
            for rels in raw_witnesses.values(): rels['t']=[['a','b']]
    # Match content word length with independent, satisfiable unary distractors.
    # Simple facts avoid exponential proof branching. Their irrelevance is disclosed.
    colors=['amber','cobalt','silver','violet','teal','copper','ivory','scarlet']
    j=0
    while sum(len(p['english'].split()) for p in premises)+len(q['english'].split())<target_words:
        pred=f'd{j}'
        phrase=f'wears the {colors[j%8]} badge from numbered club {j}'
        preds[pred]={'arguments':['person'],'description':phrase}
        premises.append({'english':'Ben '+phrase+'.','gold_ast':['unary',pred,['const','ben']]})
        for rels in raw_witnesses.values(): rels[pred]=[['b']]
        j+=1
    rng.shuffle(premises)
    for j,p in enumerate(premises): p['id']=f'p{j}'
    item={'id':f'c-{split}-{lever}-{index:03d}','split':split,'seed':SEEDS[split],
          'type':lever,'active_levers':active,'label':label,'environment':environment(preds),
          'premises':premises,'query':q,'content_words':sum(len(p['english'].split()) for p in premises)+len(q['english'].split())}
    validate(item,{p:model(item['environment'],rels) for p,rels in raw_witnesses.items()})
    return item


def generate(n=12):
    manifest={'seeds':SEEDS,'items_per_type_per_split':{'smoke':2,'dev':n,'heldout':n},'splits':{}}
    for split,count in [('smoke',2),('dev',n),('heldout',n)]:
        rows=[generate_item(split,lever,i) for lever in LEVERS for i in range(count)]
        path=HERE/f'{split}.jsonl'
        path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
        manifest['splits'][split]={'items':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'labels':dict(Counter(r['label'] for r in rows)),
            'words_min':min(r['content_words'] for r in rows),'words_max':max(r['content_words'] for r in rows)}
        print(split,manifest['splits'][split],flush=True)
    write(HERE/'manifest.json',manifest)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--per-type',type=int,default=12)
    generate(p.parse_args().per_type)
