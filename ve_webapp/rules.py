"""Small W1 teaching example with checked, plain-English conflict results."""
from dataclasses import asdict

from ve.environment import Environment
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.norm_english import parse_english, render_english
from ve.norms import check_conflict, check_witness

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


def check_rules(text):
    env = Environment(RULES_ENV)
    document = parse_english(env, text)
    canonical, manifest = render_english(document)
    base = document.base_environment()
    world = {'complete': True, 'domains': {'act': ['urgent_action']}, 'constants': {},
             'relations': {'urgent': [['urgent_action']]}}
    witness = check_conflict(document, model=world)
    if witness.status == 'CONFLICT':
        if not check_witness(document, witness.target, world, witness.tuple):
            raise ValueError('Conflict situation failed independent validation.')
        explanation = ('For an urgent act, these selected rules give incompatible decisions. '
                       + witness.situation.replace('act urgent_action', 'the urgent act') + '.')
        status = 'conflict'
    else:
        proof = check_conflict(document, prove=True)
        status = 'clear' if proof.status == 'CONFLICT-FREE' else 'unknown'
        explanation = ('The checked rules have no conflict across all cases.' if status == 'clear'
                       else 'The check ran out of budget; no conclusion about conflict was established.')
    return {'status': status, 'explanation': explanation, 'canonical': canonical,
            'rules': len(document.rules), 'identity': manifest['document_hash']}
