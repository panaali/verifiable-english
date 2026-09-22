"""Trusted checks: syntactic coverage is deliberately NOT semantic fidelity."""
from collections import Counter
import json
from ve import Environment, FiniteModel, parse, evaluate
from ve.ast import Binary, Const, Named, Not, Reach
from ve.errors import VEError
from .materials import bfs, source_rows


def environment(item):
    nodes = sorted({x for e in item['edges'] for x in e} | {item['user'], item['target']})
    return Environment({'language': 've.core@0.1', 'profiles': ['closure@0', 'relational-fol@0'],
                        'spec_revision': 've-v0.1-closure-2026-09-21',
                        'vocabulary': {'sorts': {'node': {'description': 'RBAC identifier'}},
                                       'predicates': {'edge': {'arguments': ['node','node'], 'description': 'One RBAC permission-flow edge'}},
                                       'constants': {n: {'sort': 'node', 'description': n} for n in nodes}}})


def coverage(item, rows):
    expected = Counter(r['id'] for r in source_rows(item['raw']))
    actual = Counter(r.get('source') for r in rows if isinstance(r, dict))
    return {'passed': actual == expected and len(rows) == len(expected),
            'missing': sorted((expected-actual).elements()),
            'extra_or_duplicate': sorted((actual-expected).elements(), key=str),
            'scope': 'one semantic source line per clause; headers excluded; no semantic comparison'}


def check_json(item, submission):
    try:
        edges = submission['edges']
        if not isinstance(edges, list) or len(edges) > 2*item['grants'] or any(not isinstance(e, list) or len(e) != 2 or any(not isinstance(x,str) for x in e) for e in edges):
            raise ValueError('expected JSON list of string pairs')
        result = bfs(edges, item['user'], item['target'])
        return {'valid': True, 'claim_supported': result['reachable'] == item['positive'],
                'reachable': result['reachable'], 'scope': 'BFS on untrusted transcription only'}
    except (KeyError, TypeError, ValueError) as exc:
        return {'valid': False, 'claim_supported': False, 'error': str(exc)}


def check_ve(item, submission):
    try:
        rows, certificate = submission['rows'], submission['certificate']
        cover = coverage(item, rows)
        env = environment(item)
        edges = []
        for row in rows:
            doc = parse(env, row['clause'].rstrip()+'\n')
            if len(doc.formulas) != 1 or type(doc.formulas[0]) is not Binary:
                raise ValueError('each source must map to exactly one edge clause')
            f = doc.formulas[0]
            if f.predicate != 'edge' or type(f.left) is not Const or type(f.right) is not Const:
                raise ValueError('only ground edge clauses allowed')
            edges.append((f.left.name, f.right.name))
        nodes = sorted(env.constants)
        model = FiniteModel.from_dict(env, {'complete': True, 'domains': {'node': nodes},
            'constants': {n:n for n in nodes}, 'relations': {'edge': [list(e) for e in sorted(set(edges))]}})
        claim = Reach('plus', Named('edge'), Const(item['user']), Const(item['target']))
        if not item['positive']:
            claim = Not(claim)
        evaluated = evaluate(env, claim, model, trace=False)
        witness = certificate.get('nodes')
        if not isinstance(witness, list) or any(n not in env.constants for n in witness):
            raise ValueError('certificate nodes must be declared identifiers')
        if item['positive']:
            certificate_ok = (certificate.get('kind') == 'path' and len(witness)>1 and witness[0] == item['user'] and witness[-1] == item['target'] and all(e in set(edges) for e in zip(witness,witness[1:])))
        else:
            cut = set(witness)
            certificate_ok = (certificate.get('kind') == 'cut' and item['user'] in cut and item['target'] not in cut and all(b in cut for a,b in edges if a in cut))
        return {'valid': True, 'coverage': cover, 'certificate_valid': certificate_ok,
                'evaluation': evaluated.to_dict(), 'claim_supported': bool(cover['passed'] and certificate_ok and evaluated.value is True),
                'model_id': model.model_id, 'profile': 'closure@0', 'lean_checked': False,
                'scope': 'closed-world finite model of submitted translation; source fidelity requires audit'}
    except (KeyError, TypeError, ValueError, VEError) as exc:
        return {'valid': False, 'claim_supported': False, 'error': str(exc)}


def trusted_system(report):
    return 'TRUSTED HARNESS REPORT (scope is limited as stated):\n' + json.dumps(report, sort_keys=True)
