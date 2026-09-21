"""Post-unblinding alternative DIRECT witnesses; never rewrites blind ratings."""
import json
from pathlib import Path
import sys

sys.path.insert(0, '/private/tmp/ve-e0-integration')
import ve

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(line) for line in (ROOT / 'second_rater.jsonl').read_text().splitlines()]
records = []


def direct(ident, fixed_action, effect, predicates, constants, condition):
    """Specialize a policy's fixed action into a binary effect relation."""
    e = {'language': 've.core@0', 'profile': 'relational-fol@0',
         'spec_revision': 've-v0-draft-2026-09-20', 'vocabulary': {
             'sorts': {s: {'description': f'A Cedar {s} entity.'} for s in ('principal', 'resource')},
             'predicates': {
                 **{name: {'arguments': sorts, 'description': description}
                    for name, (sorts, description) in predicates.items()},
                 'contributes': {'arguments': ['principal', 'resource'],
                                 'description': f'This policy contributes {effect} for the fixed action {fixed_action}.'}},
             'constants': {name: {'sort': sort, 'description': literal}
                           for name, (sort, literal) in constants.items()}}}
    source = (f'for every principal p, (for every resource r, (if (p contributes r), then ({condition}))).\n'
              f'for every principal p, (for every resource r, (if ({condition}), then (p contributes r))).\n')
    records.append({'dataset': 'cedar', 'id': ident, 'label': 'DIRECT',
                    'phase': 'post-unblinding alternative for proposed adjudication',
                    'formalization': source, 'environment': e,
                    'fixed_action': fixed_action,
                    'reconstruction': 'The full policy effect is false for other actions; at the fixed action it is exactly contributes(principal,resource).',
                    'parse_result': ve.check(ve.Environment(e), source)})


direct('cedar-examples/cedar-example-use-cases/document_cloud/policies.cedar#5',
       'Action::"ModifyDocument"', 'permit',
       {'owned_by': (['resource', 'principal'], 'resource.owner equals the principal; absent owner yields no tuple.')},
       {}, 'r owned_by p')
direct('cedar-examples/cedar-example-use-cases/document_cloud/policies.cedar#7',
       'Action::"ViewDocument"', 'permit',
       {'access_edit': (['resource'], 'The publicAccess field is present and equals the single literal "edit".'),
        'private_present': (['resource'], 'The Boolean isPrivate field is present.'),
        'private_true': (['resource'], 'The present Boolean isPrivate field equals true.')},
       {'public_principal': ('principal', 'Public::"public"')},
       '((p equals @public_principal) and (r is access_edit)) and ((r is private_present) and (not (r is private_true)))')
direct('cedar-examples/cedar-java-partial-evaluation/app/src/main/resources/policies.cedar#3',
       'Action::"Read"', 'permit', {},
       {'alice': ('principal', 'User::"Alice_admin"'), 'document': ('resource', 'Document::"confidential_doc1"')},
       '(p equals @alice) and (r equals @document)')
direct('cedar-examples/cedar-java-partial-evaluation/app/src/main/resources/policies.cedar#2',
       'Action::"Read"', 'forbid', {},
       {'bob': ('principal', 'User::"Bob_admin"'), 'document': ('resource', 'Document::"protected_doc1"')},
       '(p equals @bob) and (r equals @document)')
direct('cedar-examples/cedar-example-use-cases/streaming_service/policies.cedar#1',
       'Action::"watch"', 'permit',
       {'subscriber': (['principal'], 'The principal has Cedar entity type Subscriber.'),
        'movie': (['resource'], 'The resource has Cedar entity type Movie.'),
        'rent_present': (['resource'], 'The Boolean needsRentOrBuy field is present.'),
        'rent_true': (['resource'], 'The present Boolean needsRentOrBuy field equals true.')}, {},
       '((p is subscriber) and (r is movie)) and ((r is rent_present) and (not (r is rent_true)))')

host = next(r for r in rows if r['id'].endswith('pod-security-policy/host-namespaces/src.rego'))
records.append({'dataset': 'gatekeeper', 'id': host['id'], 'label': 'DIRECT',
                'phase': 'post-unblinding reclassification of unchanged checked witness',
                'formalization': host['formalization'], 'environment': host['environment'],
                'rationale': 'The vocabulary has only the existing request and three primitive unary scalar-field tests; there is no tuple or collection reification.',
                'parse_result': ve.check(ve.Environment(host['environment']), host['formalization'])})

(ROOT / 'second_rater_adjudication_witnesses.jsonl').write_text(
    ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in records))
print(f'{len(records)} post-unblinding DIRECT witnesses accepted.')
