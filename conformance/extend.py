"""Additional portable fixtures; the original evaluation corpus is unchanged."""
from __future__ import annotations
import copy
from ve import Environment, FiniteModel, parse, print_document
from ve.ast import document_from_data, document_to_data
from ve.errors import VEError
from ve.identity import meaning_id
from ve.wire import canonical_json


def parser_cases(evaluation):
    result = []
    def add(case, name, source):
        case = copy.deepcopy(case)
        case.update(id=name, source=source)
        env = Environment.from_dict(case['environment'])
        try:
            doc = parse(env, source)
            case['ast'] = document_to_data(env, doc)
            case['expected_parser'] = {'canonical': print_document(env, doc), 'ast': case['ast']}
        except VEError as exc:
            case['ast'] = [['top']]
            case['expected_parser'] = {'error_code': exc.code}
        result.append(case)
    for case in evaluation:
        add(case, 'parser_' + case['id'], case['source'])
    base = evaluation[0]
    valid = [
        'true.\nfalse.\n',
        '(for every service s, (s is deployed)) and (for every service s, (s is reviewed)).\n',
        'for every service trueish, (there exists person falsehood, (falsehood owns trueish)).\n',
        'for every service x999, (x999 equals x999).\n',
        'for every service s, (true).\nfor every service s, (false).\n',
        'not (' * 63 + 'true' + ')' * 63 + '.\n',
    ]
    invalid = [
        '', 'true.', 'true.\r\n', 'true.\n\n', ' true.\n', 'true .\n', '(true).\n',
        'true and false.\n', 'True.\n', 'true.\n#comment\n', 'true.\t\n', 'true.\nfalse.',
        'true.\u2028', 'for every service s, (for every service s, (true)).\n',
        'for every service person, (true).\n', 'for every service not, (true).\n',
        'for every service deployed, (true).\n',
        'for every service s, (s is deployed).\nthere exists service t, (s is reviewed).\n',
        'for every absent s, (true).\n', 'for every service s, (s is owns).\n',
        'for every service s, (s owns s).\n', 'for every person p, (p is deployed).\n',
        'for every person p, (there exists service s, (p equals s)).\n',
        'for every service s, (s is absent).\n', 's is deployed.\n',
        '@missing equals @missing.\n', 'not (true.\n', 'if (true) then (false).\n',
        'there exists service s, (s is deployed)).\n',
        'for every service s, (s deployed s).\n', 'trueish.\n', 'must (true).\n',
        'not (' * 64 + 'true' + ')' * 64 + '.\n',
        'for every service ' + 'a' * 65 + ', (true).\n',
        'true.\n' * 10001,
    ]
    for i, source in enumerate(valid + invalid):
        add(base, f'parser_edge_{i:03}', source)
    return result


def identity_cases(evaluation):
    cases = copy.deepcopy(evaluation)
    for i, description in enumerate(['Person 😀 €', 'escape " \\ \b \f \n \r \t \u0000',
                                     'é', 'e\u0301', '\u2028\u2029\U00010000\ue000']):
        case = copy.deepcopy(evaluation[0])
        case['id'] = f'identity_unicode_{i}'
        case['environment']['vocabulary']['sorts']['person']['description'] = description
        cases.append(case)
    # Model normalization: reordered inventories have the same normalized identity.
    for case in cases:
        env = Environment.from_dict(case['environment'])
        doc = document_from_data(env, case['ast'])
        model = FiniteModel.from_dict(env, case['model'])
        case['expected_identity'] = {
            'environment_id': env.environment_id,
            'meaning_id': meaning_id(env, doc),
            'formula_meaning_ids': [meaning_id(env, f) for f in doc.formulas],
            'model_id': model.model_id,
            'canonical_environment': canonical_json(env.to_dict()).decode(),
            'canonical_ast': canonical_json(case['ast']).decode(),
            'canonical_model': canonical_json(model.to_dict()).decode(),
        }
        for values in case['model']['domains'].values(): values.reverse()
        for rows in case['model']['relations'].values(): rows.reverse()
    return cases


def wire_cases():
    import json
    values = [True, False, 0, 2**53-1, {}, [],
              {'\ue000': 0, '\U00010000': 1, '😀': 2, '\r': 3},
              {'controls': ''.join(chr(i) for i in range(32)), 'unicode': 'é e\u0301 € 😀 / \u2028\u2029'},
              {'b': [True, 3], 'a': {'z': '"\\'}},
              [[[[['depth']]]]]]
    cases = [{'id': f'wire_{i}', 'raw': json.dumps(v, ensure_ascii=True),
              'expected': canonical_json(v).decode()} for i, v in enumerate(values)]
    cases.append({'id': 'wire_negative_zero', 'raw': '-0', 'expected': '0'})
    for i, raw in enumerate(['{"a":1,"a":2}', '{"a":1,"\\u0061":2}',
                             '{"a":{"b":1,"b":2}}', 'null', '1.0', '1e0', '-1',
                             '9007199254740992', '"\\ud800"', '"\\udfff"', '[true,]',
                             '01', 'NaN', '[', 'true false', '['*257+'true'+']'*257]):
        cases.append({'id': f'wire_invalid_{i}', 'raw': raw, 'reject': True})
    return cases


def validation_cases(evaluation):
    from ve.ast import document_from_data
    mutations = [
        lambda c: c['environment'].update(language='unknown'),
        lambda c: c['environment'].update(extra='unknown'),
        lambda c: c['environment']['vocabulary']['sorts']['person'].update(description=''),
        lambda c: c['environment']['vocabulary']['predicates']['owns'].update(arguments=['unknown','service']),
        lambda c: c['environment']['vocabulary']['predicates']['owns'].update(arguments=[]),
        lambda c: c['environment']['vocabulary']['sorts'].update(x0={'description':'Reserved.'}),
        lambda c: c['environment']['vocabulary']['sorts'].update(owns={'description':'Duplicate.'}),
        lambda c: c['model'].update(complete=False),
        lambda c: c['model'].update(complete=1),
        lambda c: c['model'].update(extra=[]),
        lambda c: c['model']['relations'].pop('owns'),
        lambda c: c['model']['domains'].pop('person'),
        lambda c: c['model']['domains']['person'].append('alice'),
        lambda c: c['model']['domains']['person'].append('Bad'),
        lambda c: c['model']['relations']['owns'].append(['alice','api']),
        lambda c: c['model']['relations'].update(owns=[['missing','api']]),
        lambda c: c['model']['relations'].update(owns=[['api','alice']]),
        lambda c: c['model']['relations'].update(owns=[['alice']]),
        lambda c: c.update(ast=[]),
        lambda c: c.update(ast=[['top','extra']]),
        lambda c: c.update(ast=[['unknown']]),
        lambda c: c.update(ast=[['eq',['var',0],['var',0]]]),
        lambda c: c.update(ast=[['forall','missing',['top']]]),
        lambda c: c.update(ast=[['forall','person',['unary','deployed',['var',0]]]]),
        lambda c: c.update(ast=[['forall','person',['unary','owns',['var',0]]]]),
        lambda c: c.update(ast=[['forall','person',['eq',['var',True],['var',0]]]]),
        lambda c: c.update(ast=[['forall','person',['exists','service',['eq',['var',0],['var',1]]]]]),
    ]
    cases = []
    for i, mutate in enumerate(mutations):
        case = copy.deepcopy(evaluation[0]); case.pop('source'); case.pop('expected')
        case['id'] = f'validation_{i:03}'; mutate(case)
        try:
            env = Environment.from_dict(case['environment'])
            FiniteModel.from_dict(env, case['model'])
            document_from_data(env, case['ast'])
        except VEError as exc: case['expected_error'] = exc.code
        else: raise AssertionError('Mutation was accepted')
        cases.append(case)
    return cases


def search_cases():
    from dataclasses import asdict
    from ve.ast import formula_from_data
    from ve.search import find_countermodel, check_countermodel
    env = Environment.from_dict({'language':'ve.core@0','profile':'relational-fol@0',
        'spec_revision':'ve-v0-draft-2026-09-20','vocabulary':{
            'sorts':{'item':{'description':'An item.'}},
            'predicates':{'marked':{'arguments':['item'],'description':'Marked.'}},'constants':{}}})
    atom = ['unary','marked',['var',0]]
    every = ['forall','item',atom]
    some = ['exists','item',atom]
    problems = [([], ['top']), ([], ['bottom']), ([every], some), ([some], every),
                ([some], ['exists','item',['top']]), ([], ['or',every,['not',every]]),
                ([['bottom']], ['bottom']), ([['exists','item',['not',atom]]], every)]
    cases = []
    for i,(premises,conclusion) in enumerate(problems):
        for size in range(3):
            case = {'id':f'search_{i}_{size}', 'environment':env.to_dict(),
                    'premises':premises, 'conclusion':conclusion,
                    'max_domain_size':size, 'max_models':1000, 'max_evaluations':10000}
            result = find_countermodel(env,[formula_from_data(env,f) for f in premises],
                                       formula_from_data(env,conclusion),max_domain_size=size,
                                       max_models=1000,max_evaluations=10000)
            case['expected_search'] = {k: v for k, v in result.to_dict().items() if v is not None}
            # Counts agree only when the single declared predicate is used.
            case['compare_counts'] = i in (2,3,4,5,7)
            cases.append(case)
    for i, (models, work) in enumerate([(0,100), (100,0), (1,100), (100,1)]):
        case = {'id':f'search_budget_{i}', 'environment':env.to_dict(), 'premises':[],
                'conclusion':['or',every,['not',every]], 'max_domain_size':2,
                'max_models':models,'max_evaluations':work,'compare_counts':True}
        case['expected_search'] = {k: v for k, v in find_countermodel(env,[],formula_from_data(env,case['conclusion']),
            max_domain_size=2,max_models=models,max_evaluations=work).to_dict().items() if v is not None}
        cases.append(case)
    for i, value in enumerate([[], [['a']]]):
        model = FiniteModel.from_dict(env, {'complete':True,'domains':{'item':['a']},
                                           'constants':{},'relations':{'marked':value}})
        case = {'id':f'witness_{i}','environment':env.to_dict(),'premises':[],
                'conclusion':every,'model':model.to_dict()}
        case['expected_check'] = asdict(check_countermodel(env,[],formula_from_data(env,every),model))
        cases.append(case)
    return cases
