"""P5 reference construction. Hidden formal artifacts never enter online packets."""
from __future__ import annotations
from collections import Counter
from dataclasses import replace
import gzip
import hashlib
import json
from pathlib import Path
import random

from ve import (Environment, Claim, Deduction, ArgumentGraph, FiniteModel, evaluate,
                check_countermodel, prove_entailment, check_argument, formula_to_data)
from ve.argument import deduction_identity
from ve.environment import LANGUAGE, PROFILE, SPEC_REVISION
from ve_experiments.paid import digest, packed, PreflightError
from experiments.prereg_inventory import p5

HERE = Path(__file__).resolve().parent / 'P5-shifting-definitions'
SEED = 20260921


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def archive(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = ''.join(packed(row) + '\n' for row in rows).encode()
    path.write_bytes(gzip.compress(data, mtime=0))


def read(path):
    from experiments.trial_analysis import read_jsonl
    return read_jsonl(path) if path.exists() else []


def topology(seed):
    """A fork and join followed by forward chaining with seeded extra parents.

    Distinct directed degree/depth invariants prove non-isomorphism (a collision
    is rejected, never taken as evidence of isomorphism). Six declared leaves
    are one fact conjunction and five packs of Horn clauses.
    """
    rng = random.Random(seed)
    parents = [[0, 1, 2], [3, 4, 5], [6, 7]]
    for n in range(9, 30):
        parents.append(sorted({n - 1, *rng.sample(range(6, n - 1), rng.randrange(0, min(3, n-7)+1))}))
    return parents


def structural_signature(parents):
    edges = []
    for n, ps in enumerate(parents, 6):
        # Six real graph leaves: facts=0; packed rule declarations=1..5.
        edges.append(([0 if p < 6 else p for p in ps] + [1 + (n-6) % 5], n))
    depth = {n: 0 for n in range(6)}
    outgoing = Counter(p for ps, _ in edges for p in set(ps))
    for ps, n in edges:
        depth[n] = 1 + max(depth[p] for p in ps)
    return digest(sorted((depth[n], len(set(edges[n-6][0])) if n >= 6 else 0,
                          outgoing[n]) for n in range(30)))


def conjunction(parts):
    result = parts[0]
    for part in parts[1:]:
        result = f'({result}) and ({part})'
    return result


def build(slot, parents):
    rng = random.Random(slot['topology_seed'])
    size = slot['predicates']
    names = [f'p{i:02d}' for i in range(size)]
    rng.shuffle(names)
    main, alternatives = names[:-3], names[-3:]
    atoms = [(main[n % len(main)], f'c{n // len(main)}') for n in range(30)]
    # A critical edge on the mandatory chain, never a location encoded in IDs.
    target = rng.randrange(10, 27)
    parent = target - 1
    old, entity = atoms[parent]
    alternate = alternatives[1] if slot['variant']=='smuggle' else alternatives[0]
    ids = [f'n{n:02d}' for n in range(30)]
    rng.shuffle(ids)
    terms = {name: f'status{i+1}' for i, name in enumerate(names)}
    terms[old] = terms[alternatives[0]] = 'cleared'
    decoys = [a for a in main if a != old][:2]
    for word, primary, rival in zip(('ready', 'active'), decoys, alternatives[1:]):
        terms[primary] = terms[rival] = word
    descriptions = {p: f'{terms[p]} (R{i+1})' for i, p in enumerate(names)}
    env = Environment.from_dict({'language': LANGUAGE, 'profile': PROFILE, 'spec_revision': SPEC_REVISION,
        'vocabulary': {'sorts': {'unit': {'description': 'A unit in the local dossier.'}},
            'predicates': {p: {'arguments': ['unit'], 'description': descriptions[p]} for p in names},
            'constants': {c: {'sort': 'unit', 'description': f'Unit {c}.'} for _, c in atoms}}})
    def atom(pair):
        p, c = pair
        return f'@{c} is {p}'
    def clause(ps, out):
        return f'if ({conjunction([atom(p) for p in ps])}), then ({atom(out)})'
    intended_rules, merged_rules, rule_prose, records = [], [], [], []
    record_uses = {}
    for n, ps in enumerate(parents, 6):
        inputs = [atoms[p] for p in ps]
        if n == target and slot['variant'] != 'benign':
            inputs[ps.index(parent)] = (alternate, entity)
        intended_rules.append(clause(inputs, atoms[n]))
        merged_rules.append(clause([atoms[p] for p in ps], atoms[n]))
        # Same number and shape of records for every sibling. Intended grounding
        # is evidence, never a verdict or a free missing bridge.
        rec = {'id': f'r{n-6:02d}', 'text': 'If ' + ' and '.join(
            f'{c} has R{names.index(p)+1}' for p, c in inputs) +
            f', {atoms[n][1]} has R{names.index(atoms[n][0])+1}.'}
        if len({c for _,c in inputs} | {atoms[n][1]}) == 1:
            rec['text'] = f'For {atoms[n][1]}, ' + ' and '.join(
                f'R{names.index(p)+1}' for p,_ in inputs) + f' imply R{names.index(atoms[n][0])+1}.'
        records.append(rec)
        rule_prose.append({'id': ids[n], 'parents': [ids[p] if p >= 6 else ids[0] for p in ps],
            'rule_record': rec['id'], 'text': f'{atoms[n][1]} is {terms[atoms[n][0]]}.'})
        record_uses[ids[n]] = {'conclusion': descriptions[atoms[n][0]],
                              'required_inputs': [descriptions[p] for p, _ in inputs]}
    # Shift silently identifies two cleared senses. Smuggle instead requires
    # a bridge from cleared to the independently defined ready sense. The full
    # glossary is identical across all three siblings; no variant-only word.
    fact = conjunction([atom(a) for a in atoms[:6]])
    def make_graph(rules, certify=False):
        leaves = [Claim.create(env, ids[0], fact + '.\n')]
        for group in range(5):
            leaves.append(Claim.create(env, ids[group+1], conjunction(rules[group::5]) + '.\n'))
        claims = leaves + [Claim.create(env, ids[n], atom(atoms[n]) + '.\n') for n in range(6, 30)]
        edges = []
        for n, ps in enumerate(parents, 6):
            premises = list(dict.fromkeys([ids[0] if p < 6 else ids[p] for p in ps] + [ids[1+(n-6)%5]]))
            edges.append(Deduction(f'e{ids[n][1:]}', tuple(premises), ids[n]))
        graph = ArgumentGraph(env, tuple(claims), tuple(edges), ids[29], target_scope='original dossier root')
        if certify:
            by_id = {c.name: c for c in claims}
            new = []
            for edge in edges:
                proof = prove_entailment(env, [by_id[n].ast for n in edge.premises], by_id[edge.conclusion].ast)
                if proof.status != 'Found':
                    raise ValueError(f'proof search: {proof.status}')
                new.append(replace(edge, certificates=({'edge_id': deduction_identity(graph, edge),
                    'direction': 'follows', 'proof': proof.certificate},)))
            graph = replace(graph, deductions=tuple(new))
        return graph
    proposed = make_graph(merged_rules, True)
    intended = make_graph(intended_rules, slot['variant'] == 'benign')
    # Least forward closure gives a finite model of ALL intended declared leaves.
    true = set(atoms[:6])
    for n, ps in enumerate(parents, 6):
        inputs = [atoms[p] for p in ps]
        if n == target and slot['variant'] != 'benign':
            inputs[ps.index(parent)] = (alternate, entity)
        if all(p in true for p in inputs):
            true.add(atoms[n])
    model = FiniteModel.from_dict(env, {'complete': True, 'domains': {'unit': sorted({c for _, c in atoms})},
        'constants': {c: c for _, c in atoms}, 'relations': {p: [[c] for q, c in sorted(true) if q == p] for p in names}})
    leaves = intended.claims[:6]
    root = next(c for c in intended.claims if c.name == intended.root)
    if not all(evaluate(env, c.ast, model) for c in leaves):
        raise ValueError('unsatisfied declared premises')
    negative = check_countermodel(env, [c.ast for c in leaves], root.ast, model).valid
    if negative != (slot['variant'] != 'benign'):
        raise ValueError('whole-premise root witness failure')
    # A bridge is a hidden diagnostic artifact, never an added declared leaf.
    bridge = Claim.create(env, 'bridge', clause([atoms[parent]], (alternate, entity)) + '.\n')
    augmented = intended
    if slot['variant'] != 'benign':
        augmented = replace(intended, claims=(*intended.claims, bridge), deductions=tuple(
            replace(e, premises=(*e.premises, 'bridge')) if e.conclusion == ids[target] else e
            for e in intended.deductions))
        by_id = {c.name:c for c in augmented.claims}
        certified = []
        for edge in augmented.deductions:
            proof = prove_entailment(env, [by_id[n].ast for n in edge.premises], by_id[edge.conclusion].ast)
            if proof.status != 'Found':
                raise ValueError('bridge-augmented edge proof failure')
            certified.append(replace(edge, certificates=({'edge_id':deduction_identity(augmented, edge),
                'direction':'follows','proof':proof.certificate},)))
        augmented = replace(augmented, deductions=tuple(certified))
    plain_leaves = [{'id': ids[0], 'text': '; '.join(f'{c} has R{names.index(p)+1}' for p, c in atoms[:6]) + '.'}]
    for group in range(5):
        plain_leaves.append({'id': ids[group+1], 'text': 'Rules ' + ', '.join(r['id'] for r in records[group::5]) + ' are declared.'})
    glossary = [{'term': terms[p], 'sense': descriptions[p]} for p in names]
    rng.shuffle(glossary)
    rng.shuffle(rule_prose)
    rng.shuffle(plain_leaves)
    rng.shuffle(records)
    public_id = 'i' + hashlib.sha256((slot['cluster'] + '/' + str(('shift','smuggle','benign').index(slot['variant']))).encode()).hexdigest()[:12]
    dossier = {'id': public_id, 'glossary': glossary, 'premises': plain_leaves,
        'records': records, 'nodes': rule_prose, 'root': ids[29],
        'argument': 'The declared facts and rules justify the listed steps and the final claim.'}
    return dossier, {'id': public_id, 'slot_id': slot['id'], 'family': slot['cluster'], 'split': slot['split'],
        'kind': slot['variant'], 'predicates': size, 'acceptable_locations': [[ids[parent], ids[target]]]
        if slot['variant']=='shift' else [[ids[target]]] if slot['variant']=='smuggle' else [[]],
        'sense_use_mapping': record_uses, 'root_meaning': descriptions[atoms[29][0]],
        'bridge': bridge.source, 'affected_uses': [ids[parent], ids[target]]}, {
        'id': public_id, 'slot': slot, 'topology': parents, 'structural_signature': structural_signature(parents),
        'intended': intended.to_dict(), 'merged': proposed.to_dict(), 'model': model.to_dict(),
        'negative': negative, 'bridge': bridge.to_dict(env), 'augmented': augmented.to_dict(),
        'predicate_identities': {p: digest({'environment_id': env.environment_id, 'symbol': p,
                                            'declaration': env.to_dict()['vocabulary']['predicates'][p]}) for p in names}}


def generate(base=HERE):
    if any(r.get('identity','').startswith('scored/') for r in read(base/'runs/study/costs.jsonl')):
        raise PreflightError('scored material change requires amendment and separately labeled run')
    if (base / 'freeze.json').exists() and json.loads((base/'freeze.json').read_text()).get('status') == 'READY_FOR_SCORED':
        raise PreflightError('frozen materials require an amendment')
    dossiers, labels, graphs, attempts, signatures, family_topologies = [], [], [], read(base/'materials/construction-ledger.jsonl.gz'), set(), {}
    for slot in p5()['slots']:
        family = slot['cluster']
        if family not in family_topologies:
            increment = 0
            while True:
                candidate = topology(slot['topology_seed'] + f'/{increment}')
                sig = structural_signature(candidate)
                if sig not in signatures:
                    signatures.add(sig)
                    family_topologies[family] = candidate
                    break
                attempts.append({'family': family, 'increment': increment, 'candidate': candidate,
                                 'reason': 'structural invariant collision; reject conservatively'})
                increment += 1
        try:
            dossier, label, graph = build(slot, family_topologies[family])
        except Exception as exc:
            attempts.append({'slot': slot, 'topology': family_topologies[family], 'reason': str(exc)})
            archive(base/'materials/construction-ledger.jsonl.gz', attempts)
            raise
        dossiers.append(dossier); labels.append(label); graphs.append(graph)
    archive(base/'materials/dossiers.jsonl.gz', dossiers)
    archive(base/'labels.jsonl.gz', labels)
    archive(base/'materials/graphs.jsonl.gz', graphs)
    archive(base/'materials/construction-ledger.jsonl.gz', attempts)
    # A reproducible process-isolated OFFLINE DRAFT pass is deliberately not
    # represented as the preregistered Qwen independent author.
    import subprocess, sys
    process = subprocess.run([sys.executable, '-m', 'experiments.p5_paraphrase'],
        input=packed(dossiers), text=True, capture_output=True, check=True)
    paraphrases = json.loads(process.stdout)
    archive(base/'materials/paraphrases.jsonl.gz', paraphrases)
    by_id = {p['id']: p for p in paraphrases}
    for split in ('dev','scored'):
        archive(base/f'materials/{split}.jsonl.gz', [dict(id=d['id'], group=l['family'], split=split,
            payload={**d, 'nodes': by_id[d['id']]['nodes'], 'argument': by_id[d['id']]['argument']},
            paraphrase_status='OFFLINE_DRAFT_NOT_QWEN') for d,l in zip(dossiers,labels) if l['split']==split])
    if not (base/'materials/review-ledger.jsonl.gz').exists():
        archive(base/'materials/review-ledger.jsonl.gz', [])
    report = {'passed': len(signatures)==28, 'slots': len(labels), 'families':28,
        'method':'pairwise distinct directed degree/depth invariants; sufficient non-isomorphism test',
        'failed_candidates': len(attempts), 'independent_prose_ready': False,
        'status':'BUILT_REFERENCE_AND_OFFLINE_DRAFT_REVIEW_BLOCKED', 'paid_calls':0}
    write_json(base/'checks/construction.json', report)
    return report
