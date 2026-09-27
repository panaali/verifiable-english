"""closure@0 semantics, profile boundaries, views, identities and evidence."""
import copy
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess

import pytest

from ve import *
from ve.closure import unfold
from ve.entailment import CLOSURE_CHECKER_VERSION
from ve.environment import CLOSURE_LANGUAGE, CLOSURE_PROFILES, CLOSURE_REVISION
from ve.errors import VEError
from ve.grammar import export_grammar
from ve.wire import canonical_json
from explicit_inverse import parse_explicit
from fluent_inverse import parse_fluent

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / 'conformance/closure.json').read_text())


def load(case=CASES[3]):
    env = Environment(case['environment'])
    return env, document_from_data(env, case['ast']), FiniteModel.from_dict(env, case['model'])


def test_closure_corpus_python_and_inverse_views():
    for case in CASES:
        env, doc, model = load(case)
        assert parse(env, case['source']) == doc
        assert print_document(env, doc) == case['source']
        assert [evaluate(env, f, model, trace=False).value for f in doc.formulas] == case['expected']
        assert document_from_named_fol(env, document_to_named_fol(env, doc)) == doc
        for f in doc.formulas:
            for view in ('fol_symbols', 'fol_keywords', 've_strict', 've_explicit'):
                text = render(f, env, view)
                assert parse_explicit(env, text, view) == f, (case['id'], view, text)
            text = render(f, env, 've_fluent')
            assert parse_fluent(env, text) == f, text


def test_all_existing_v0_identity_preimages_and_hashes_unchanged():
    cases = json.loads((ROOT / 'conformance/identity.json').read_text())
    assert len(cases) >= 706
    for case in cases:
        env, doc, model = load(case)
        got = {'environment_id': env.environment_id, 'meaning_id': meaning_id(env, doc),
               'formula_meaning_ids': [meaning_id(env, f) for f in doc.formulas],
               'model_id': model.model_id,
               'canonical_environment': canonical_json(env.to_dict()).decode(),
               'canonical_ast': canonical_json(document_to_data(env, doc)).decode(),
               'canonical_model': canonical_json(model.to_dict()).decode()}
        assert got == case['expected_identity'], case['id']
        assert source_id(case['source']) == source_id(case['source'], env)
        assert print_document(env, doc) == case['source']


def test_closure_identity_domains_and_distinct_edge_forms():
    env, _, model = load()
    assert env.to_dict() == CASES[3]['environment']
    assert env.environment_id == hashlib.sha256(b've-environment-v0.1\n' + canonical_json(env.to_dict())).hexdigest()
    a = Reach('plus', Named('edge'), Const('start'), Const('end'))
    b = Reach('plus', Body('node', Binary('edge', Var(1), Var(0))), Const('start'), Const('end'))
    assert meaning_id(env, a) != meaning_id(env, b)
    assert meaning_id(env, a) == hashlib.sha256(b've-meaning-v0.1\n' + canonical_json(
        {'environment_id': env.environment_id, 'ast': formula_to_data(env, a)})).hexdigest()
    assert model.model_id == hashlib.sha256(b've-model-v0.1\n' + canonical_json(
        {'environment_id': env.environment_id, 'model': model.to_dict()})).hexdigest()
    assert source_id('true.\n', env) == hashlib.sha256(b've-source-v0.1\ntrue.\n').hexdigest()


@pytest.mark.parametrize('change', [
    lambda e: e.update(profiles=['relational-fol@0', 'closure@0']),
    lambda e: e.update(profiles=['closure@0', 'closure@0', 'relational-fol@0']),
    lambda e: e.update(profiles=['closure@0']),
    lambda e: e.update(profiles=['closure@0', 'order@0', 'relational-fol@0']),
    lambda e: e.update(profile='closure@0'),
    lambda e: e.update(spec_revision='unknown'),
])
def test_profile_envelope_rejections(change):
    raw = copy.deepcopy(CASES[3]['environment'])
    change(raw)
    with pytest.raises(VEError): Environment(raw)


def test_v0_profile_rejects_reach_and_contextual_tokens_remain_available():
    env, _, _ = load()
    raw = env.to_dict()
    del raw['profiles']
    raw.update(language='ve.core@0', profile='relational-fol@0', spec_revision='ve-v0-draft-2026-09-20')
    old = Environment(raw)
    with pytest.raises(VEError): parse(old, 'tc[edge](@start, @end).\n')
    raw['vocabulary']['predicates']['tc'] = {'description': 'Ordinary relation.', 'arguments': ['node', 'node']}
    raw['vocabulary']['predicates']['rtc'] = {'description': 'Ordinary predicate.', 'arguments': ['node']}
    old = Environment(raw)
    doc = parse(old, 'for every node a, ((a tc a) and (a is rtc)).\n')
    assert parse(old, print_document(old, doc)) == doc


@pytest.mark.parametrize('source', [
    'tc[marked](@start, @end).\n',
    'tc[node a, a | (true)](@start, @end).\n',
    'for every node a, (tc[node a, b | (true)](@start, @end)).\n',
    'tc[node a, b | (true)](a, @end).\n',
    'tc[node a,b | (true)](@start, @end).\n',
    'tc[node a, b|(true)](@start, @end).\n',
    'tc[node a, b | true](@start, @end).\n',
    'tc[edge](@start,@end).\n',
    'tc [edge](@start, @end).\n',
])
def test_strict_scope_and_syntax_rejection(source):
    env, _, _ = load()
    with pytest.raises(VEError): parse(env, source)


def test_wrong_sort_and_malformed_wire_rejected():
    env, _, _ = load()
    raw = env.to_dict()
    raw['vocabulary']['predicates']['hetero'] = {'description': 'cross sort', 'arguments': ['node', 'other']}
    env = Environment(raw)
    for f in [Reach('plus', Named('hetero'), Const('start'), Const('end')),
              Reach('star', Body('other', Top()), Const('start'), Const('end')),
              Reach('plus', Body('node', Eq(Var(0), Var(2))), Const('start'), Const('end')),
              Reach('bad', Named('edge'), Const('start'), Const('end'))]:
        with pytest.raises(VEError): check_formula(env, f)
    for edge in [[], ['named'], ['named', 'edge', 'extra'], ['body', 'node'], ['unknown', 'edge']]:
        with pytest.raises(VEError): formula_from_data(env, ['reach', 'plus', edge, ['const','start'], ['const','end']])


def test_bfs_independent_expected_cycles_direction_and_identity():
    for case in CASES:
        env, _, model = load(case)
        domain = model.domains['node']
        for a in domain:
            reached, pending = set(), [v for u,v in model.relations['edge'] if u == a]
            while pending:
                b = pending.pop()
                if b in reached: continue
                reached.add(b)
                pending.extend(v for u,v in model.relations['edge'] if u == b)
            for b in domain:
                raw = model.to_dict(); raw['constants'] = {'start': a, 'end': b}
                changed = FiniteModel.from_dict(env, raw)
                for kind in ('plus', 'star'):
                    f = Reach(kind, Named('edge'), Const('start'), Const('end'))
                    assert evaluate(env, f, changed).value == (b in reached or kind == 'star' and a == b)


def test_outer_parameter_capture_nested_closure_and_unfolding():
    env, _, model = load()
    sources = [
        'for every node z, (tc[node a, b | ((a edge b) and (not (b equals z)))](@start, @end)).\n',
        'for every node z, (rtc[node a, b | (there exists node w, ((a edge w) and ((w edge b) and (not (b equals z)))))](@start, @end)).\n',
        'for every node z, (tc[node a, b | (rtc[node c, d | ((c edge d) and (not (d equals z)))](a, b))](@start, @end)).\n',
    ]
    for source in sources:
        f = parse(env, source).formulas[0]
        expanded = Forall('node', unfold(f.body, 'node'))
        check_formula(env, expanded)
        for case in CASES[1:]:
            e, _, m = load(case)
            assert evaluate(e, f, m, trace=False).value == evaluate(e, expanded, m, trace=False).value
        for view in ('fol_symbols', 'fol_keywords', 've_strict', 've_explicit'):
            assert parse_explicit(env, render(f,env,view),view) == f
        assert parse_fluent(env, render(f,env,'ve_fluent')) == f
    assert evaluate(env, parse(env, sources[0]), model).value is False
    assert evaluate(env, parse(env, sources[0]), model, max_evaluations=1).status == 'ResourceLimit'


def test_fluent_locals_retained_no_relative_closure_guard_and_collisions():
    env, _, _ = load()
    f = Forall('node', Implies(Reach('star', Body('node', Top()), Var(0), Var(0)), Top()))
    text = render(f, env, 've_fluent')
    assert 'steps satisfying [vertex' in text and ' | (true)]' in text
    assert 'such that' not in text  # closure guards never enter the relative-guard contraction
    assert parse_fluent(env, text) == f
    legends = {render_vocabulary(env, view) for view in ('fol_symbols','fol_keywords','ve_strict','ve_explicit','ve_fluent')}
    assert len(legends) == 1
    assert json.loads(legends.pop())['closure']['relations'] == ['edge']
    raw = env.to_dict(); raw['vocabulary']['predicates']['edge']['verbalisation'] = '{1} is reachable from {0}'
    rejected = Environment(raw)
    assert lint_vocabulary(rejected)
    assert render(Reach('plus', Named('edge'), Const('start'),Const('end')),rejected,'ve_explicit') == '@end is reachable from @start by one or more edge steps'


def test_grammar_two_local_transition_and_outer_endpoint_scope():
    lark = pytest.importorskip('lark')
    env, _, _ = load()
    parser = lark.Lark(export_grammar(env, max_binder_depth=3, max_binders=3), start='start')
    for source in ['tc[edge](@start, @end).\n',
                   'rtc[node x0, x1 | (x0 edge x1)](@start, @end).\n',
                   'for every node x0, (tc[node x1, x2 | (x1 edge x0)](x0, @end)).\n']:
        parser.parse(source)
        parse(env, source)
    for source in ['tc[node x0, x1 | (true)](x0, @end).\n',
                   'tc[node x0, x1 | (true)](@start, x1).\n',
                   'for every other x0, (tc[edge](x0, @end)).\n']:
        with pytest.raises(lark.exceptions.LarkError): parser.parse(source)
    for dialect in ('gbnf', 'ebnf'):
        assert 'rtc[' in export_grammar(env, dialect=dialect, max_binder_depth=2)


def test_search_enumerates_base_edges_and_oracle_never_guesses():
    env, _, _ = load()
    plus = Reach('plus', Named('edge'), Const('start'), Const('end'))
    star = Reach('star', Named('edge'), Const('start'), Const('end'))
    found = find_countermodel(env, (star,), plus, max_domain_size=1, max_models=100)
    assert found.status == 'Found' and check_countermodel(env, (star,), plus, found.model).valid
    from ve.search import _used_predicates
    assert _used_predicates(plus) == {'edge'}
    assert _used_predicates(Reach('plus', Body('node', Binary('edge',Var(1),Var(0))),Const('start'),Const('end'))) == {'edge'}
    assert compare(env, plus, star, {'max_proof_steps':0,'max_domain_size':0,'max_models':0,'max_evaluations':0}).status == 'UNKNOWN'
    assert not in_two_variable_fragment(plus)


def test_closure_certificates_versioned_replay_and_no_induction():
    env, _, _ = load()
    a,b = Const('start'),Const('end')
    plus = Reach('plus',Named('edge'),a,b)
    star = Reach('star',Named('edge'),a,a)
    for premises, conclusion in [((),star), ((Binary('edge',a,b),),plus),
                                 ((Not(unfold(plus,'node')),),Not(plus))]:
        result = prove_entailment(env,premises,conclusion,max_steps=300)
        assert result.status == 'Found',result
        assert result.certificate['checker_version'] == CLOSURE_CHECKER_VERSION
        assert check_entailment_certificate(env,premises,conclusion,result.certificate).valid
        forged=copy.deepcopy(result.certificate); forged['trace']['rule']='induction'
        assert not check_entailment_certificate(env,premises,conclusion,forged).valid
    # Positive self reach is not licensed by reflexivity; an isolated vertex refutes it.
    result = prove_entailment(env,(),Reach('plus',Named('edge'),a,a),max_steps=50)
    assert result.status != 'Found'


def lean_bin():
    if not shutil.which('lake'): pytest.skip('lake unavailable')
    executable = ROOT/'lean/.lake/build/bin/ve_conformance'
    assert executable.exists(), 'Run lake build before pytest (sequentially)'
    return executable


def test_lean_all_closure_cases_and_countermodels():
    cases = CASES + [{**{k:c[k] for k in ('id','environment','model')}, 'kind':'countermodel',
                     'premises':c['ast'][:1], 'conclusion':c['ast'][1],
                     'expected_refutes': c['expected'][0] and not c['expected'][1]} for c in CASES]
    proc = subprocess.run([str(lean_bin())], input=json.dumps(cases),text=True,capture_output=True,timeout=120)
    assert proc.returncode == 0,proc.stdout+proc.stderr
    for case,result in zip(cases,json.loads(proc.stdout),strict=True):
        assert result['status']=='ok',result
        if case.get('kind'):
            assert result['refutes'] == case['expected_refutes']
        else:
            assert result['values']==case['expected']
            assert result['canonical']==case['source']


@pytest.mark.parametrize('with_reach', [False, True])
@pytest.mark.parametrize('version', [CLOSURE_CHECKER_VERSION, 've-tableau-checker@1', 've-tableau-checker@2'])
def test_lean_profile_gate_accepts_only_closure_checker_version(with_reach, version):
    env, _, _ = load()
    f=Reach('star',Named('edge'),Const('start'),Const('start')) if with_reach else Top()
    proof=prove_entailment(env,(),f,max_steps=100)
    assert proof.status=='Found'
    certificate = {**proof.certificate, 'checker_version': version}
    request={'id':'closure_certificate_gate','environment':env.to_dict(),'premises':[],
             'conclusion':formula_to_data(env,f),'certificate':certificate}
    proc=subprocess.run([str(lean_bin()),'check-certificate'],input=json.dumps(request),text=True,capture_output=True,timeout=30)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    response=json.loads(proc.stdout)[0]
    assert response['status'] == 'ok'
    assert response['valid'] is (version == CLOSURE_CHECKER_VERSION)


@pytest.mark.parametrize('kind', ['plus', 'star'])
@pytest.mark.parametrize('positive', [False, True])
@pytest.mark.parametrize('body', [False, True])
def test_closure_unfolding_replay_both_signs_and_rule_binding(kind, positive, body):
    from ve.entailment import _binding
    env, _, _ = load()
    edge = Body('node', Binary('edge', Var(1), Var(0))) if body else Named('edge')
    reach = Reach(kind, edge, Const('start'), Const('end'))
    expanded = unfold(reach, 'node')
    premises, goal = ((reach,), expanded) if positive else ((expanded,), reach)
    at = 0 if positive else 1
    certificate = {**_binding(env, premises, goal), 'trace': {
        'rule': f'closure-{kind}@0', 'at': at, 'children': [{'rule': 'close'}]}}
    assert check_entailment_certificate(env, premises, goal, certificate).valid
    for rule in ('expand', 'closure-star@0' if kind == 'plus' else 'closure-plus@0', 'induction'):
        forged = copy.deepcopy(certificate)
        forged['trace']['rule'] = rule
        assert not check_entailment_certificate(env, premises, goal, forged).valid
    forged = copy.deepcopy(certificate)
    forged['trace']['parameter'] = 'c:start'
    assert not check_entailment_certificate(env, premises, goal, forged).valid
    # A closure rule may not target the Reach-free, already valid v0 query.
    from conformance.certificates import environment
    old = environment(False)
    forged = {**_binding(old, (Not(Bottom()),), Top()), 'trace': {
        'rule': f'closure-{kind}@0', 'at': 0, 'children': [{'rule': 'close'}]}}
    assert not check_entailment_certificate(old, (Not(Bottom()),), Top(), forged).valid


def test_closure_equality_congruence_captured_parameters_and_edge_identity():
    env, _, _ = load()
    a,b=Const('start'),Const('end')
    # Body parameters include constants as well as enclosing quantifier bindings.
    f=Reach('plus',Body('node',And(Binary('edge',Var(1),Var(0)),Not(Eq(Var(0),a)))),a,b)
    g=Reach('plus',Body('node',And(Binary('edge',Var(1),Var(0)),Not(Eq(Var(0),b)))),b,a)
    result=prove_entailment(env,(Eq(a,b),f),g,max_steps=100)
    assert result.status=='Found'
    assert check_entailment_certificate(env,(Eq(a,b),f),g,result.certificate).valid
    changed=Reach('plus',Body('node',Not(Binary('edge',Var(1),Var(0)))),b,a)
    assert prove_entailment(env,(Eq(a,b),f),changed,max_steps=40).status!='Found'


def test_seeded_extended_formulas_all_view_inverses_and_lean():
    env, _, model=load(CASES[7])
    rng=random.Random(173)
    def term_(depth):
        return Var(rng.randrange(depth)) if depth and rng.randrange(2) else Const(rng.choice(('start','end')))
    def formula(depth,scope):
        tag=rng.randrange(10) if depth else rng.randrange(4)
        if tag==0:return Top()
        if tag==1:return Eq(term_(scope),term_(scope))
        if tag==2:return Binary('edge',term_(scope),term_(scope))
        if tag==3:return Reach(rng.choice(('plus','star')),Named('edge'),term_(scope),term_(scope))
        if tag==4:return Not(formula(depth-1,scope))
        if tag in (5,6):return (Forall if tag==5 else Exists)('node',formula(depth-1,scope+1))
        if tag==7:return Reach(rng.choice(('plus','star')),Body('node',formula(depth-1,scope+2)),term_(scope),term_(scope))
        return (And if tag==8 else Or)(formula(depth-1,scope),formula(depth-1,scope))
    cases=[]
    for i in range(100):
        f=formula(4,0); check_formula(env,f)
        source=print_document(env,Document((f,)))
        assert parse(env,source).formulas==(f,)
        for view in ('fol_symbols','fol_keywords','ve_strict','ve_explicit'):
            assert parse_explicit(env,render(f,env,view),view)==f
        assert parse_fluent(env,render(f,env,'ve_fluent'))==f
        value=evaluate(env,f,model,trace=False).value
        assert type(value) is bool
        cases.append({'id':f'fuzz_{i}','environment':env.to_dict(),'model':model.to_dict(),
                      'ast':[formula_to_data(env,f)],'source':source,'expected':[value]})
    proc=subprocess.run([str(lean_bin())],input=json.dumps(cases),text=True,capture_output=True,timeout=60)
    assert proc.returncode==0,proc.stdout+proc.stderr
    for case,result in zip(cases,json.loads(proc.stdout),strict=True):
        assert result['values']==case['expected'] and result['canonical']==case['source']
