"""Reproduce 15 checked E0 closure translations from pinned sampled source text.

Run from the repository root after lake build. No source-language solver or
translation-equivalence theorem is claimed by the finite witness checks.
"""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from ve import Environment, FiniteModel, document_from_named_fol, document_to_data, evaluate, print_document, render
from ve.environment import CLOSURE_LANGUAGE, CLOSURE_PROFILES, CLOSURE_REVISION

REV = '46be9e1bafc85e37456cbf56e9dc92b6c8178666'
OUT = Path(__file__).resolve().parent


def sample(dataset):
    path = f'experiments/E0/survey_samples/{dataset}.jsonl'
    text = subprocess.check_output(['git', 'show', f'{REV}:{path}'], cwd=ROOT, text=True)
    return {r['id']: r for r in map(json.loads, text.splitlines())}


def term(s): return {'const': s[1:]} if s.startswith('@') else {'var': s}
def atom(p, *args):
    if len(args) == 1: return {'op': 'unary', 'predicate': p, 'term': term(args[0])}
    return {'op': 'binary', 'predicate': p, 'left': term(args[0]), 'right': term(args[1])}
def eq(a,b): return {'op':'eq', 'left':term(a), 'right':term(b)}
def neg(f): return {'op':'not','body':f}
def op(k,a,b): return {'op':k,'left':a,'right':b}
def both(*fs):
    if not fs: return {'op':'top'}
    result=fs[-1]
    for f in reversed(fs[:-1]): result=op('and',f,result)
    return result
def either(*fs):
    result=fs[-1]
    for f in reversed(fs[:-1]): result=op('or',f,result)
    return result
def implies(a,b): return op('implies',a,b)
def iff(a,b): return both(implies(a,b),implies(b,a))
def quant(k,s,v,b): return {'op':k,'sort':s,'variable':v,'body':b}
def all_(s,v,b): return quant('forall',s,v,b)
def ex(s,v,b): return quant('exists',s,v,b)
def reach(k,e,a,b): return {'op':'reach','kind':k,'edge':e,'left':term(a),'right':term(b)}
def named(r): return {'named':r}
def body(s,phi): return {'sort':s,'source':'x','destination':'y','body':phi}
def rtc(a,b): return reach('star',named('parent'),a,b)


def environment(sorts, relations, constants):
    return Environment({'language':CLOSURE_LANGUAGE,'profiles':list(CLOSURE_PROFILES),
        'spec_revision':CLOSURE_REVISION,'vocabulary':{
            'sorts':{s:{'description':desc} for s,desc in sorts.items()},
            'predicates':{p:{'arguments':args,'description':desc} for p,(args,desc) in relations.items()},
            'constants':{c:{'sort':s,'description':desc} for c,(s,desc) in constants.items()}}})


def model(env,domains,constants,relations):
    return {'complete':True,'domains':{s:sorted(domains[s]) for s in env.sorts},
            'constants':constants,'relations':{p:sorted([list(x) for x in set(map(tuple,relations.get(p,[])))]) for p in env.predicates}}


def save(slug,dataset,source,env,formula,yes,no,adapter,contrast):
    doc=document_from_named_fol(env,{'formulas':[formula]})
    for expected,raw in ((True,yes),(False,no)):
        checked=FiniteModel.from_dict(env,raw)
        result=evaluate(env,doc,checked,trace=False)
        assert result.value is expected,(slug,expected,result)
    text=print_document(env,doc)
    row={'id':source['id'],'dataset':dataset,'source':source['text'],
         'provenance':{'git_revision':REV,'path':f'experiments/E0/survey_samples/{dataset}.jsonl',
                       'text_sha256':hashlib.sha256(source['text'].encode()).hexdigest()},
         'environment':env.to_dict(),'ast':document_to_data(env,doc),'strict':text,
         'adapter':adapter,'contrast':contrast,'true_model':yes,'false_model':no}
    (OUT/(slug+'.json')).write_text(json.dumps(row,indent=2,ensure_ascii=False)+'\n')
    (OUT/(slug+'.ve')).write_text(text)
    return {'file':slug+'.json','id':source['id'],'dataset':dataset}


CEDAR_IDS = [
'cedar-examples/cedar-example-use-cases/sales_orgs/templated/policies.cedar#3',
'cedar-examples/cedar-example-use-cases/github_example/policies.cedar#5',
'cedar-examples/cedar-example-use-cases/sales_orgs/static/policies.cedar#5',
'cedar-examples/oopsla2024-benchmarks/benches/github-templates/cedar/policies.cedar#0',
'cedar-examples/cedar-policy-language-in-action/PhotoApp/photoapp.cedar#4',
'cedar-examples/oopsla2024-benchmarks/benches/gdrive-templates/cedar/policies.cedar#0',
'cedar-integration-tests/tests/example_use_cases/policies_3c.cedar#0',
'cedar-integration-tests/tests/example_use_cases/policies_2a.cedar#0',
'cedar-examples/cedar-java-partial-evaluation/app/src/main/resources/policies.cedar#0',
'cedar-integration-tests/tests/example_use_cases/policies_3a.cedar#0',
]


def cedar(index,source):
    sorts={'entity':'A Cedar entity UID, including action and referenced unloaded UIDs.',
           'request':'A request record; its principal, action and resource fields are single-valued and present.'}
    rels={
      'parent':(['entity','entity'],'Primitive immediate hierarchy edge, child to parent. Never a precomputed ancestor relation.'),
      'request_principal':(['request','entity'],'The principal entity UID in this request.'),
      'request_action':(['request','entity'],'The action entity UID in this request.'),
      'request_resource':(['request','entity'],'The resource entity UID in this request.'),
      'permit_contribution':(['request'],'Proposed match extension of THIS permit policy, fully defined by the formula; not the final authorization decision.')}
    consts={}; vals={}; entities={'user','action','resource'}
    tables={'parent':[], 'request_principal':[('request0','user')], 'request_action':[('request0','action')],
            'request_resource':[('request0','resource')], 'permit_contribution':[('request0',)]}
    terms=[]; chains=[]; source_names={}
    def const(name,value,uid):
        consts[name]=('entity',uid);vals[name]=value;entities.add(value);source_names[value]=uid
        return '@'+name
    def chain(child,parent,prefix):
        mid=prefix+'_middle';entities.update((child,mid,parent))
        tables['parent'].extend([(child,mid),(mid,parent)]);chains.append((mid,parent))
    if index==1:
        target=const('action_group','edit_actions','Action::"PrezEditActions"')
        terms=[rtc('a',target),atom('owner','r','p')]
        rels['owner']=(['entity','entity'],'Present owner entity-valued attribute; no row means absent.')
        tables['owner']=[('resource','user')];chain('action','edit_actions','action')
    elif index==2:
        act=const('action_target','action','Action::"push"')
        terms=[eq('a',act),ex('entity','g',both(atom('writers','r','g'),rtc('p','g')))]
        rels['writers']=(['entity','entity'],'Present writers attribute: ONE UserGroup entity, not ordinary set membership.')
        tables['writers']=[('resource','writer_group')];chain('user','writer_group','principal')
        source_names['writer_group']='UserGroup::"synthetic_writers"'
    elif index==3:
        target=const('action_group','view_actions','Action::"MarketTemplateViewActions"')
        sorts['collection']='A reified present entity-set attribute, including present empty sets.'
        rels['viewer_markets']=(['entity','collection'],'Present viewerMarkets attribute points to its set value; absent has no row.')
        rels['set_member']=(['collection','entity'],'An ordinary element of the reified set, without hierarchy expansion.')
        tables['viewer_markets']=[('resource','markets')];tables['set_member']=[('markets','market_group')]
        terms=[rtc('a',target),ex('collection','c',ex('entity','g',both(atom('viewer_markets','r','c'),atom('set_member','c','g'),rtc('p','g'))))]
        chain('action','view_actions','action');chain('user','market_group','principal')
        source_names['market_group']='Market::"synthetic_market"'
    elif index==4:
        pg=const('principal_slot','principal_group','Bound ?principal slot (arbitrary entity UID, not a new quantifier).')
        res=const('resource_slot','resource','Bound ?resource slot (arbitrary entity UID).')
        act=const('action_target','action','Action::"read"')
        terms=[rtc('p',pg),eq('a',act),eq('r',res)];chain('user','principal_group','principal')
    elif index==5:
        pg=const('family','doe_family','PhotoApp::UserGroup::"DoeFamily"')
        act=const('action_target','action','PhotoApp::Action::"viewPhoto"')
        album=const('album','doe_photos','PhotoApp::Album::"DoePhotos"')
        terms=[rtc('p',pg),eq('a',act),rtc('r',album)]
        chain('user','doe_family','principal');chain('resource','doe_photos','resource')
    elif index==6:
        pg=const('principal_slot','principal_group','Bound ?principal slot (arbitrary entity UID).')
        res=const('resource_slot','resource_group','Bound ?resource slot (arbitrary entity UID).')
        act=const('action_target','action','Action::"read"')
        terms=[rtc('p',pg),eq('a',act),rtc('r',res)]
        chain('user','principal_group','principal');chain('resource','resource_group','resource')
    elif index==7:
        user=const('alice','user','User::"alice"');album=const('album','vacation','Album::"jane_vacation"')
        terms=[eq('p',user),rtc('r',album)];chain('resource','vacation','resource')
    elif index==8:
        pg=const('friends','friends_group','UserGroup::"jane_friends"')
        act=const('action_target','action','Action::"view"')
        photo=const('photo','resource','Photo::"VacationPhoto94.jpg"')
        terms=[rtc('p',pg),eq('a',act),eq('r',photo)];chain('user','friends_group','principal')
    elif index==9:
        pg=const('admin','admin_group','UserGroup::"Admin"')
        ag=const('read_group','read_actions','Action::"Read"')
        rg=const('protected','protected_group','DocumentGroup::"Protected"')
        terms=[rtc('p',pg),rtc('a',ag),rtc('r',rg)]
        chain('user','admin_group','principal');chain('action','read_actions','action');chain('resource','protected_group','resource')
    elif index==10:
        act=const('action_target','action','Action::"view"');album=const('album','vacation','Album::"jane_vacation"')
        terms=[eq('a',act),rtc('r',album)];chain('resource','vacation','resource')
    # Core Cedar inputs can mix types; tags keep that distinction on one carrier.
    resource_types={1:'Presentation',2:'Repo',3:'Template',4:'Repo',5:'PhotoApp::Photo',
                    6:'Document',7:'Photo',8:'Photo',9:'Document',10:'Photo'}
    types={'user':'User','action':'Action','resource':resource_types[index]}
    for value,raw in source_names.items():
        if '::"' in raw: types[value]=raw.split('::"')[0]
    for value in sorted(entities - types.keys()):
        raw=source_names.get(value,'')
        if '::"' in raw:
            types[value]=raw.split('::"')[0]
        elif value.startswith('action') or value.endswith('actions'):
            types[value]='Action'
        elif value.startswith('resource') or value in ('vacation','doe_photos','protected_group'):
            types[value]='DocumentGroup' if index==9 else 'Album' if index in (5,7,10) else 'Folder'
        else:
            types[value]='Market' if index==3 else 'UserGroup'
    for value,kind in types.items():
        tag='type_'+kind.replace('::','_').lower()
        rels[tag]=(['entity'],'Cedar entity type tag '+kind+'; tags do not precompute policy truth or reachability.')
        tables.setdefault(tag,[]).append((value,))
        source_names[value]=kind+'::"'+value+'"' if '::"' not in source_names.get(value,'') else source_names[value]
    match=ex('entity','p',ex('entity','a',ex('entity','r',both(
        atom('request_principal','q','p'),atom('request_action','q','a'),atom('request_resource','q','r'),*terms))))
    formula=all_('request','q',iff(atom('permit_contribution','q'),match))
    env=environment(sorts,rels,consts)
    domains={'entity':entities,'request':['request0']}
    if 'collection' in sorts:domains['collection']=['markets']
    yes=model(env,domains,vals,tables);no=copy.deepcopy(yes)
    no['relations']['parent'].remove(list(chains[-1]))
    adapter={'kind':'cedar-request-projection@0','effect':'permit',
      'translation_unit':'Exact sampled single policy match, represented as a definition of its per-request permit contribution.',
      'request_fields':['request_principal','request_action','request_resource'],
      'entity_attributes':[p for p in ('owner','writers') if p in rels],
      'set_attributes':['viewer_markets'] if 'viewer_markets' in rels else [],
      'uid_map':source_names,'type_tags':sorted(p for p in rels if p.startswith('type_')),
      'conditions':[
        'All request fields are total functions. UIDs include referenced but unloaded entities, so equality and zero-step membership still work.',
        'parent contains primitive child-to-parent edges. The witness adapter checks acyclicity, matching Cedar hierarchy inputs.',
        'Present entity-valued fields are partial functions. Present set attributes have explicit collection objects; no field row is absence.',
        'All chosen conditions use positive attribute access, so absent fields give no permit contribution, as do Cedar evaluation errors here.',
        'Template slots, where present, are supplied constants. The formula remains parameterized by their denotations.',
        'No other policy, forbid override, full authorization decision or schema-inferred hierarchy is asserted.']}
    return save(f'cedar_{index:02}', 'cedar',source,env,formula,yes,no,adapter,
        'Both models propose the same permit contribution. Removing the last edge of a required two-step hierarchy path falsifies its defining equivalence; request fields and other conditions remain fixed.')


def alloy_less_than(slug,source):
    env=environment({'identifier':'An Alloy Id.'},
      {'next_id':(['identifier','identifier'],'The primitive Id-restricted next field, one successor for each Id.')},
      {n:('identifier',f'Supplied argument {n} of less_than; arguments are fixed for this predicate call.') for n in ('origin','left_id','right_id')})
    # Predicate arguments are constants, retaining every model/argument assignment.
    formula=reach('plus',body('identifier',both(atom('next_id','x','y'),neg(eq('y','@origin')))), '@left_id','@right_id')
    domains={'identifier':['i0','i1','i2']};tables={'next_id':[('i0','i1'),('i1','i2'),('i2','i0')]}
    yes=model(env,domains,{'origin':'i0','left_id':'i0','right_id':'i2'},tables)
    no=model(env,domains,{'origin':'i1','left_id':'i0','right_id':'i2'},tables)
    return save(slug,'alloy',source,env,formula,yes,no,
      {'kind':'alloy-predicate-call@0','total_functions':['next_id'],
       'conditions':['Id<:next restricts the source to Id; the carrier and next_id already enforce that signature.',
                     'Id->from is removed by excluding DESTINATION equal to origin inside the Body, fixed on every step.',
                     'No unfolding of a recursive helper or command scope is assumed. Constants supply arbitrary predicate arguments.',
                     'Both models retain the total successor cycle and the source fact that every Id is reachable from every Id.']},
      'Changing only the fixed origin from i0 to i1 removes the first edge of the i0-to-i2 path. Outgoing edges of origin are not removed.')


def alloy_connected(source):
    env=environment({'gsa':'An Alloy GSA.'}, {'parent':(['gsa','gsa'],'Primitive parent field, at most one parent per GSA.')}, {})
    formula=all_('gsa','g',all_('gsa','h',reach('star',body('gsa',either(atom('parent','x','y'),atom('parent','y','x'))),'h','g')))
    yes=model(env,{'gsa':['a','b','c']},{},{'parent':[('a','b'),('b','c')]})
    no=model(env,{'gsa':['a','b','c']},{},{'parent':[('a','b')]})
    return save('alloy_03_connected','alloy',source,env,formula,yes,no,
      {'kind':'alloy-assertion@0','partial_functions':['parent'],
       'conditions':['parent + ~parent is explicitly expanded as the disjunction of forward and reversed one-step edges.',
                     'The assertion quantifies all GSA pairs, from the second bound GSA to the first.',
                     'This translates the sampled assertion over its relevant signature; unrelated Iolus dynamics and source module facts are not premises.']},
      'A three-vertex parent chain is connected through forward/converse steps. Removing b-to-c isolates c and falsifies the assertion.')


def alloy_dag(source):
    env=environment({'jtype':'An Alloy Type.'},{'xtends':(['jtype','jtype'],'Primitive Type.xtends relation.')},{})
    formula=all_('jtype','t',neg(reach('plus',named('xtends'),'t','t')))
    yes=model(env,{'jtype':['a','b','c']},{},{'xtends':[('a','b'),('b','c')]})
    no=model(env,{'jtype':['a','b','c']},{},{'xtends':[('a','b'),('b','c'),('c','a')]})
    return save('alloy_04_dag','alloy',source,env,formula,yes,no,
      {'kind':'alloy-fact@0','conditions':['graph/dag[xtends] expands to no positive xtends cycle.',
        'Type is the relevant carrier. These instances can use Interface atoms, whose xtends field permits a set of interfaces.',
        'The fact itself is the checked claim, not a premise that would exclude its falsifying model. Other Java fields are outside the sampled fact.']},
      'Adding the edge c-to-a closes a positive cycle; no inequality test is substituted for positive length.')


def alloy_one_node(source):
    sorts={'node':'An Alloy Node.','identifier':'An Alloy Id.','state':'An Alloy State.',
           'node_data':'An Alloy NodeData.','data_entry':'A reified State.data(state,node,node_data) tuple.'}
    rels={
      'active':(['state','node'],'State.active membership.'),
      'node_id':(['node','identifier'],'The total Node.id field, injective as required by the source fact.'),
      'next_id':(['identifier','identifier'],'Primitive Id.next successor field.'),
      'entry_state':(['data_entry','state'],'State coordinate of a State.data tuple.'),
      'entry_node':(['data_entry','node'],'Node coordinate of a State.data tuple.'),
      'entry_value':(['data_entry','node_data'],'NodeData value coordinate of a State.data tuple.'),
      'successor':(['node_data','node'],'Primitive NodeData.next field; not transitive reachability.')}
    env=environment(sorts,rels,{})
    one=ex('node','n',all_('node','m',eq('m','n')))
    # For every active node n: resolve n.(s.data).next, then expand NextCorrect.
    less=reach('plus',body('identifier',both(atom('next_id','x','y'),neg(eq('y','f')))),'ii','jj')
    no_between=all_('node','m',implies(both(atom('active','st','m'),neg(eq('m','n'))),
        ex('identifier','ii',ex('identifier','jj',both(atom('node_id','m','ii'),atom('node_id','nx','jj'),neg(less))))))
    active_one=ex('node','unique',both(atom('active','st','unique'),all_('node','z',implies(atom('active','st','z'),eq('z','unique')))))
    resolved=ex('data_entry','entry',ex('node_data','nd',ex('node','nx',ex('identifier','f',both(
        atom('entry_state','entry','st'),atom('entry_node','entry','n'),atom('entry_value','entry','nd'),
        atom('successor','nd','nx'),atom('node_id','n','f'),no_between,either(neg(eq('nx','n')),active_one))))))
    correct=all_('state','st',all_('node','n',implies(atom('active','st','n'),resolved)))
    union_equals=all_('node','n',ex('state','st',atom('active','st','n')))
    formula=both(one,correct,union_equals)
    ds={'node':['n0'],'identifier':['i0','i1'],'state':['s0'],'node_data':['d0'],'data_entry':['e0']}
    rows={'active':[('s0','n0')],'node_id':[('n0','i0')],'next_id':[('i0','i1'),('i1','i0')],
          'entry_state':[('e0','s0')],'entry_node':[('e0','n0')],'entry_value':[('e0','d0')],'successor':[('d0','n0')]}
    yes=model(env,ds,{},rows)
    nds=copy.deepcopy(ds);nds['state']=[];nds['data_entry']=[]
    nrows=copy.deepcopy(rows)
    for key in ('active','entry_state','entry_node','entry_value'):nrows[key]=[]
    no=model(env,nds,{},nrows)
    return save('alloy_05_one_node','alloy',source,env,formula,yes,no,
      {'kind':'alloy-predicate@0','total_functions':['node_id','next_id','entry_state','entry_node','entry_value','successor'],
       'conditions':['#Node=1 is expanded by existence and universal equality; no numeric profile is assumed.',
        'NextCorrect expands both no-intervening-active-node and successor-not-self-or-exactly-one-active-node clauses.',
        'less_than is expanded by positive Body closure of next_id with edges INTO the fixed origin removed.',
        'State.data is represented by unique tuples: exactly one NodeData per active (state,node) pair and none for inactive pairs.',
        'State.active=Node denotes UNION across states, not every state containing every node.',
        'No arbitrary numeric command scope or opaque NextCorrect/less_than predicate is supplied. Unused NodeData fields can be expanded independently.']},
      'The true structure has one active node in one state. The false structure keeps one node and the same Id cycle but has an empty State carrier, so State.active=Node fails. In both, the relation multiplicities remain valid.')


def main():
    cedar_sources=sample('cedar');alloy_sources=sample('alloy')
    ledger=[cedar(i,cedar_sources[item]) for i,item in enumerate(CEDAR_IDS,1)]
    ledger.append(alloy_less_than('alloy_01_chord2',alloy_sources['alloy-models/algorithms/distributed-hashtable/chord2.als@81']))
    ledger.append(alloy_less_than('alloy_02_chord',alloy_sources['alloy-models/algorithms/distributed-hashtable/chord.als@80']))
    ledger.append(alloy_connected(alloy_sources['alloy-models/algorithms/multicasting/iolus.als@5190']))
    ledger.append(alloy_dag(alloy_sources['alloy-models/models/java/javatypes_soundness.als@282']))
    ledger.append(alloy_one_node(alloy_sources['alloy-models/algorithms/distributed-hashtable/chord2.als@4943']))
    (OUT/'manifest.json').write_text(json.dumps({'profile':'closure@0','items':ledger},indent=2)+'\n')
    print('Generated',len(ledger),'items, each with true and false models.')


if __name__=='__main__':main()
