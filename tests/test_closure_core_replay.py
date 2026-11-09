"""Closure certificates replay through Core behind closure's own gates (consolidation step 3b).

Both closure runners, the conformance executable's `check-certificate` (`CertificateWire.runClosureCase`)
and the `route` mode (`Route.Wire.runClosure`), call `Closure.Tableau.checkCertificate`: closure's
version gate (`@0` and `@1`, the induction rule only at `@1`), then Core's `replay` of the embedded
certificate. Closure's decoder is the atom-free gate in front of Core: an n-ary `atom`, which Core's
decoder reads, is refused with closure's own message.
"""
import copy
import json
from pathlib import Path

import pytest

from conformance.certificates import invoke, replay_python
from conformance.closure_certificates import positive_cases as original_cases
from conformance.induction import positive_cases
from lean_routes import rows

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / 'lean/.lake/build/bin/ve_conformance'
V0, V1 = 've-tableau-closure-checker@0', 've-tableau-closure-checker@1'
ATOM = ['atom', 'p', [['const', 'a']] * 3]  # Core's n-ary atom; not a closure formula


def _induct(node):
    """The first `closure-induct@1` node of a trace, depth first."""
    if node['rule'] == 'closure-induct@1':
        return node
    return next(filter(None, map(_induct, node.get('children', []))), None)


def _variants(case, mutations):
    out = []
    for name, mutate in mutations.items():
        variant = copy.deepcopy(case)
        variant.pop('expected', None)
        variant['id'] = name
        mutate(variant)
        out.append(variant)
    return out


def _version(version):
    return lambda c: c['certificate'].update(checker_version=version)


def _answer(row):
    return {key: row[key] for key in ('status', 'valid', 'error') if key in row}


def test_certificate_runner_keeps_closures_version_gate_and_refusal_texts():
    good = positive_cases()[0]
    assert good['certificate']['checker_version'] == V1 and _induct(good['certificate']['trace'])
    assert replay_python(good)
    cases = _variants(good, {
        'v1': lambda c: None,
        'v0': _version(V0),  # an induction node under @0: the rule is off, a verdict and no error
        'v2': _version('ve-tableau-closure-checker@2'),
        'core-version': _version('ve-tableau-core-checker@1'),
        'atom-invariant': lambda c: _induct(c['certificate']['trace']).update(invariant=ATOM),
        'atom-conclusion': lambda c: c.update(conclusion=ATOM),
        'stale': lambda c: c['certificate'].update(environment_id='0' * 64),
        'rule': lambda c: c['certificate']['trace'].update(rule='closure-bogus@0'),
    })
    answers = {row['id']: _answer(row) for row in invoke(LEAN, cases)}
    assert answers == {
        'v1': {'status': 'ok', 'valid': True},
        'v0': {'status': 'ok', 'valid': False},
        'v2': {'status': 'ok', 'valid': False},
        'core-version': {'status': 'ok', 'valid': False},
        'atom-invariant': {'status': 'error', 'valid': False, 'error': 'invalid indexed formula'},
        'atom-conclusion': {'status': 'error', 'valid': False, 'error': 'invalid indexed formula'},
        'stale': {'status': 'error', 'valid': False, 'error': 'certificate is stale or bound to different inputs'},
        'rule': {'status': 'error', 'valid': False, 'error': 'unknown tableau rule'},
    }


def test_certificates_without_induction_keep_their_verdict_at_both_versions():
    cases, _ = original_cases()
    assert cases and not any(_induct(c['certificate']['trace']) for c in cases)
    # Each certificate as written, and with its first expansion's branches dropped (a replay
    # that cannot close: a verdict, not a refusal), labelled @0 and labelled @1.
    cut = [c for c in cases if c['certificate']['trace']['rule'] != 'close']
    assert cut
    both = [variant for case in cases for variant in _variants(case, {
        case['id'] + '@0': _version(V0), case['id'] + '@1': _version(V1)})]
    both += [variant for case in cut for variant in _variants(case, {
        case['id'] + '-cut@0': lambda c: (_version(V0)(c), c['certificate']['trace'].update(children=[])),
        case['id'] + '-cut@1': lambda c: (_version(V1)(c), c['certificate']['trace'].update(children=[]))})]
    answers = invoke(LEAN, both)
    assert all(row['status'] == 'ok' for row in answers), [r for r in answers if r['status'] != 'ok']
    assert [row['valid'] for row in answers] == [True] * (2 * len(cases)) + [False] * (2 * len(cut))


@pytest.fixture(scope='module')
def route_case():
    cases = json.loads((ROOT / 'lean/VE/Route/examples/route-cases.json').read_text())
    case = next(c for c in cases if c['id'] == 'closure-certificate-uses-background')
    assert case['certificate']['checker_version'] == V1 and case['expected']['valid'] is True
    return case


def test_route_runner_keeps_closures_version_gate_and_refusal_texts(route_case):
    induct = {'rule': 'closure-induct@1', 'at': 0, 'sort': 'person', 'invariant': ['top'], 'children': []}
    cases = _variants(route_case, {
        'v1': lambda c: None,
        'v0': _version(V0),
        'v2': _version('ve-tableau-closure-checker@2'),
        'atom-invariant': lambda c: c['certificate'].update(trace={**induct, 'invariant': ATOM}),
        'induct-v0': lambda c: c['certificate'].update(checker_version=V0, trace=induct),
        'rule': lambda c: c['certificate']['trace'].update(rule='closure-bogus@0'),
    })
    answers = {row['id']: {**_answer(row), **({'steps': row['steps']} if 'steps' in row else {})}
               for row in rows('route', cases)}
    assert answers == {
        'v1': {'status': 'ok', 'valid': True, 'steps': 4},
        'v0': {'status': 'ok', 'valid': True, 'steps': 4},
        'v2': {'status': 'ok', 'valid': False, 'steps': 4},
        'atom-invariant': {'status': 'error', 'valid': False, 'error': 'invalid indexed formula'},
        'induct-v0': {'status': 'ok', 'valid': False, 'steps': 1},
        'rule': {'status': 'error', 'valid': False, 'error': 'unknown tableau rule'},
    }

