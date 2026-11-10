"""AR-23 evidence: closure's version gate, atom-free gate and refusal texts, row for row, on one checkout.

    cd <checkout> && uv run python <this file> --out ROWS.json      # once at the base, once at the head
    uv run python docs/arch/AR-23/closure_probe.py --compare BASE.json HEAD.json --json evidence/closure-probe.json

Runs the variants of `tests/test_closure_core_replay.py` (an induction certificate at `@1`, at `@0`, at an
unknown version `@2` and at Core's version; an n-ary `atom` invariant and conclusion, which closure refuses; a
stale certificate; an unknown rule; a route certificate's induction under `@0`) through the checkout's own
certificate runner (`ve_conformance check-certificate`) and route runner (`ve_service` mode `route`), and saves
every row whole. `--compare` requires the two checkouts' rows to be equal byte for byte.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

V0, V1 = 've-tableau-closure-checker@0', 've-tableau-closure-checker@1'
ATOM = ['atom', 'p', [['const', 'a']] * 3]


def induct(node):
    if node['rule'] == 'closure-induct@1':
        return node
    return next(filter(None, map(induct, node.get('children', []))), None)


def variants(case, mutations):
    out = []
    for name, mutate in mutations.items():
        variant = copy.deepcopy(case)
        variant.pop('expected', None)
        variant['id'] = name
        mutate(variant)
        out.append(variant)
    return out


def version(v):
    return lambda c: c['certificate'].update(checker_version=v)


def record(root: Path) -> dict:
    sys.path[:0] = [str(root), str(root / 'tests')]
    from conformance.certificates import invoke
    from conformance.closure_certificates import positive_cases as original_cases
    from conformance.induction import positive_cases
    from lean_routes import rows
    good = positive_cases()[0]
    certificate = variants(good, {
        'v1': lambda c: None, 'v0': version(V0), 'v2': version('ve-tableau-closure-checker@2'),
        'core-version': version('ve-tableau-core-checker@1'),
        'atom-invariant': lambda c: induct(c['certificate']['trace']).update(invariant=ATOM),
        'atom-conclusion': lambda c: c.update(conclusion=ATOM),
        'stale': lambda c: c['certificate'].update(environment_id='0' * 64),
        'rule': lambda c: c['certificate']['trace'].update(rule='closure-bogus@0')})
    for case in original_cases()[0]:
        certificate += variants(case, {case['id'] + '@0': version(V0), case['id'] + '@1': version(V1)})
    route_case = next(c for c in json.loads((root / 'lean/VE/Route/examples/route-cases.json').read_text())
                      if c['id'] == 'closure-certificate-uses-background')
    node = {'rule': 'closure-induct@1', 'at': 0, 'sort': 'person', 'invariant': ['top'], 'children': []}
    route = variants(route_case, {
        'v1': lambda c: None, 'v0': version(V0), 'v2': version('ve-tableau-closure-checker@2'),
        'atom-invariant': lambda c: c['certificate'].update(trace={**node, 'invariant': ATOM}),
        'induct-v0': lambda c: c['certificate'].update(checker_version=V0, trace=node),
        'rule': lambda c: c['certificate']['trace'].update(rule='closure-bogus@0')})
    return {'certificate': invoke(root / 'lean/.lake/build/bin/ve_conformance', certificate),
            'route': rows('route', route)}


def compare(base_path: Path, head_path: Path) -> dict:
    base, head = (json.loads(p.read_text()) for p in (base_path, head_path))
    out = {'tool': 'docs/arch/AR-23/closure_probe.py', 'runners': {}}
    for runner in ('certificate', 'route'):
        b, h = base[runner], head[runner]
        out['runners'][runner] = {
            'rows': len(h), 'equal': b == h,
            'differences': [r['id'] for r, s in zip(b, h) if r != s] + (['row count'] if len(b) != len(h) else []),
            'answers': {r['id']: {k: r[k] for k in ('status', 'valid', 'error', 'steps') if k in r} for r in h}}
    out['sha256'] = {name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for name, p in (('base', base_path), ('head', head_path))}
    out['equal'] = all(r['equal'] for r in out['runners'].values())
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--out')
    parser.add_argument('--compare', nargs=2, type=Path)
    parser.add_argument('--json')
    args = parser.parse_args(argv)
    if args.compare:
        result = compare(*args.compare)
        Path(args.json).write_text(json.dumps(result, indent=1) + '\n')
        print('closure probe', 'EQUAL' if result['equal'] else 'DIFFERENT',
              {k: v['rows'] for k, v in result['runners'].items()})
        return 0 if result['equal'] else 1
    Path(args.out).write_text(json.dumps(record(Path.cwd()), indent=1, sort_keys=True) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
