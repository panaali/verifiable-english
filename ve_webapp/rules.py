"""Small W1 teaching examples with checked, plain-English conflict results and questions."""
from itertools import product

from ve import ast
from ve.environment import Environment
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.english import parse_english_with_metadata, render_english as render_formula
from ve.norm_english import parse_english, render_english, default_sentence
from ve.norms import check_conflict, check_witness, prove_norm_entailment, check_norm_entailment_certificate

RULES_TEXT = ('Rule 1. Every act must not be done.\n'
              'Rule 2 (exception to rule 1). Every act may be done, if that act is urgent.\n'
              'Rule 3. Every act must be done, if that act is urgent.')
RULES_ENV = {'language': LANGUAGE, 'profiles': ['norms@0', 'relational-fol@0'],
             'spec_revision': SPEC_REVISION,
             'vocabulary': {'sorts': {'act': {'description': 'act'}},
                            'predicates': {
                                'permitted': {'arguments': ['act'], 'description': 'permission',
                                              'regulated': {'role': 'permission', 'default': 'deny',
                                                            'act': '{0} be done'}},
                                'required': {'arguments': ['act'], 'description': 'obligation',
                                             'regulated': {'role': 'obligation', 'default': 'deny',
                                                           'permission': 'permitted', 'act': '{0} be done'}},
                                'urgent': {'arguments': ['act'], 'description': 'urgent',
                                           'verbalisation': '{0} is urgent'}}, 'constants': {}}}

# The tour's policy. Rule 4 has no precedence over rule 1, so a suspended
# employee is both permitted and forbidden to read: the checker finds it.
HANDBOOK_TEXT = ('Rule 1. Every employee may read the handbook.\n'
                 'Rule 2. Every employee must sign the handbook.\n'
                 'Rule 3 (exception to rule 2). Every employee need not sign the handbook, if that employee is new.\n'
                 'Rule 4. Every employee must not read the handbook, if that employee is suspended.')
HANDBOOK_ENV = {'language': LANGUAGE, 'profiles': ['norms@0', 'relational-fol@0'],
                'spec_revision': SPEC_REVISION,
                'vocabulary': {'sorts': {'employee': {'description': 'A person who works for the company.'}},
                               'predicates': {
                                   'may_read': {'arguments': ['employee'], 'description': 'Permission to read the staff handbook.',
                                                'regulated': {'role': 'permission', 'default': 'deny',
                                                              'act': '{0} read the handbook'}},
                                   'may_sign': {'arguments': ['employee'], 'description': 'Permission to sign the staff handbook.',
                                                'regulated': {'role': 'permission', 'default': 'allow',
                                                              'act': '{0} sign the handbook'}},
                                   'must_sign': {'arguments': ['employee'], 'description': 'Duty to sign the staff handbook.',
                                                 'regulated': {'role': 'obligation', 'default': 'deny',
                                                               'permission': 'may_sign', 'act': '{0} sign the handbook'}},
                                   'new': {'arguments': ['employee'], 'description': 'Joined the company this month.',
                                           'verbalisation': '{0} is new'},
                                   'suspended': {'arguments': ['employee'], 'description': 'Currently suspended from work.',
                                                 'verbalisation': '{0} is suspended'}},
                               'constants': {}}}
VOCABULARIES = {'acts': (RULES_ENV, RULES_TEXT), 'handbook': (HANDBOOK_ENV, HANDBOOK_TEXT)}
MAX_CASE_FACTS = 4


def _vocabulary(name):
    if name not in VOCABULARIES:
        raise ValueError('Choose a listed rule vocabulary.')
    env_json, text = VOCABULARIES[name]
    return Environment(env_json), text


def _plain(env):
    return [p for p, d in env.predicates.items() if d.regulated is None and len(d.arguments) == 1]


def _reading(document):
    """VE's own English for each rule and for each default."""
    env = document.env
    canonical, manifest = render_english(document)
    rules = [canonical[a:b] for a, b in (entry['span'] for entry in manifest['blocks'])]
    defaults = [default_sentence(env, p) for p, d in env.predicates.items() if d.regulated is not None]
    return canonical, manifest, rules, defaults


def _conflict_search(document):
    """Every fact combination for one thing of each kind; a found witness is re-checked."""
    env = document.env
    plain = _plain(env)
    names = {sort: [sort + '_1'] for sort in env.sorts}
    for values in product((False, True), repeat=len(plain)):
        world = {'complete': True, 'domains': names, 'constants': {},
                 'relations': {p: ([[names[env.predicates[p].arguments[0]][0]]] if v else [])
                               for p, v in zip(plain, values)}}
        witness = check_conflict(document, model=world)
        if witness.status == 'CONFLICT':
            if not check_witness(document, witness.target, world, witness.tuple):
                raise ValueError('Conflict situation failed independent validation.')
            return witness, dict(zip(plain, values)), world
    return None, None, None


def _situation(env, facts, sort):
    words = [('is ' if value else 'is not ') + env.predicates[p].verbalisation.removeprefix('{0} is ')
             for p, value in facts.items()]
    noun = sort.replace('_', ' ')
    article = 'an' if noun[0] in 'aeiou' else 'a'
    if not words:
        return f'For {article} {noun}'
    return f'For {article} {noun} who ' + ' and '.join(words)


def _decisions(document, witness, world):
    from ve.model import FiniteModel
    env = document.env
    if witness.target in document.order:
        model = FiniteModel.from_dict(document.base_environment(), world)
        selected = document.selected_rules(witness.target, model, witness.tuple)
        role = env.predicates[witness.target].regulated.role
        numbers = {r.name: i for i, r in enumerate(document.rules, 1)}
        words = {('permission', True): 'permits it', ('permission', False): 'forbids it',
                 ('obligation', True): 'requires it', ('obligation', False): 'releases it'}
        modal = 'may' if role == 'permission' else 'must'
        act = env.predicates[witness.target].regulated.act.replace('{0} ', '{0} ' + modal + ' ', 1).format(
            'the ' + env.predicates[witness.target].arguments[0])
        parts = [f'rule {numbers[r.name]} {words[role, r.sign]}' for r in selected]
        return f'whether {act}: ' + ' but '.join(parts) + ', and neither rule is an exception to the other'
    required = witness.target.split('->', 1)[0]
    act = env.predicates[required].regulated.act.replace('{0} ', '{0} must ', 1).format(
        'the ' + env.predicates[required].arguments[0])
    return f'whether {act}: the rules require it but do not permit it'


def check_rules(text, vocabulary='acts'):
    env, _ = _vocabulary(vocabulary)
    document = parse_english(env, text)
    canonical, manifest, rules, defaults = _reading(document)
    common = {'canonical': canonical, 'rules': len(document.rules), 'identity': manifest['document_hash'],
              'readings': rules, 'defaults': defaults, 'vocabulary': vocabulary}
    if vocabulary == 'acts':
        world = {'complete': True, 'domains': {'act': ['urgent_action']}, 'constants': {},
                 'relations': {'urgent': [['urgent_action']]}}
        witness = check_conflict(document, model=world)
        if witness.status == 'CONFLICT':
            if not check_witness(document, witness.target, world, witness.tuple):
                raise ValueError('Conflict situation failed independent validation.')
            explanation = ('For an urgent act, these selected rules give incompatible decisions. '
                           + witness.situation.replace('act urgent_action', 'the urgent act') + '.')
            return {'status': 'conflict', 'explanation': explanation, **common}
    else:
        witness, facts, world = _conflict_search(document)
        if witness is not None:
            sort = env.predicates[witness.target.split('->', 1)[0]].arguments[0]
            explanation = (_situation(env, facts, sort) + ', the rules disagree about '
                           + _decisions(document, witness, world) + '.')
            return {'status': 'conflict', 'explanation': explanation, **common}
    proof = check_conflict(document, prove=True)
    status = 'clear' if proof.status == 'CONFLICT-FREE' else 'unknown'
    explanation = ('The checked rules have no conflict across all cases.' if status == 'clear'
                   else 'The check ran out of budget; no conclusion about conflict was established.')
    return {'status': status, 'explanation': explanation, **common}


def _predicates(formula):
    found = set()
    def visit(node):
        if isinstance(node, ast.Unary):
            found.add(node.predicate)
        for value in getattr(node, '__dataclass_fields__', {}):
            child = getattr(node, value)
            if hasattr(child, '__dataclass_fields__'):
                visit(child)
    visit(formula)
    return found


def _follows(document, formula):
    proof = prove_norm_entailment(document, (), formula, max_steps=4000)
    if proof.status != 'Found' or not proof.certificate:
        return False
    return check_norm_entailment_certificate(document, (), formula, proof.certificate).valid


def ask_rules(text, question, vocabulary='acts'):
    """Yes, no, or not settled; each answer and each listed case is a replayed proof."""
    env, _ = _vocabulary(vocabulary)
    document = parse_english(env, text)
    if type(question) is not str or not question.strip():
        raise ValueError('Write the question as one statement, such as: Every employee who is new may read the handbook.')
    parsed = parse_english_with_metadata(env, question.strip() + '\n')
    if len(parsed.document.formulas) != 1:
        raise ValueError('Ask about one statement at a time.')
    formula = parsed.document.formulas[0]
    guard, body, sort = None, None, None
    if isinstance(formula, ast.Forall):
        sort = formula.sort
        if isinstance(formula.body, ast.Implies):
            guard, body = formula.body.left, formula.body.right
        else:
            guard, body = ast.Top(), formula.body
        opposite = ast.Forall(sort, ast.Implies(guard, ast.Not(body)))
    else:
        opposite = ast.Not(formula)
    reading = render_formula(formula, env).strip()
    if _follows(document, formula):
        return {'answer': 'yes', 'reading': reading, 'cases': [],
                'explanation': 'Yes. The rules imply this statement in every situation.'}
    if _follows(document, opposite):
        return {'answer': 'no', 'reading': reading, 'cases': [],
                'explanation': 'No. The rules imply the opposite in every situation.'}
    cases = []
    mentioned = _predicates(guard) if guard is not None else set()
    plain = [p for p in _plain(env) if sort is not None and env.predicates[p].arguments[0] == sort
             and p not in mentioned]
    if guard is not None and len(plain) <= MAX_CASE_FACTS:
        noun = sort.replace('_', ' ')
        for values in product((True, False), repeat=len(plain)):
            condition = guard
            for p, value in zip(plain, values):
                atom = ast.Unary(p, ast.Var(0))
                literal = atom if value else ast.Not(atom)
                condition = literal if isinstance(condition, ast.Top) else ast.And(condition, literal)
            yes = ast.Forall(sort, ast.Implies(condition, body))
            no = ast.Forall(sort, ast.Implies(condition, ast.Not(body)))
            holds, fails = _follows(document, yes), _follows(document, no)
            if holds and fails:
                continue  # The condition cannot happen.
            if holds or fails:
                when = _situation(env, dict(zip(plain, values)), sort).removeprefix('For ')
                cases.append({'answer': 'yes' if holds else 'no',
                              'when': when[0].upper() + when[1:] if plain else 'Every ' + noun})
    return {'answer': 'not settled', 'reading': reading, 'cases': cases,
            'explanation': 'The rules do not settle this. The answer depends on facts the statement leaves open.'}
