"""P5 reference construction. Hidden formal artifacts never enter online packets."""
from __future__ import annotations
from collections import Counter
from dataclasses import replace
import gzip
import os
import hashlib
import hmac
import json
from pathlib import Path
import random

from ve import (Environment, Claim, Deduction, ArgumentGraph, FiniteModel, evaluate,
                check_countermodel, prove_entailment)
from ve.argument import deduction_identity
from ve.environment import LANGUAGE, PROFILE, SPEC_REVISION
from ve_experiments.paid import digest, packed, PreflightError
from experiments.prereg_inventory import p5

HERE = Path(__file__).resolve().parent / 'P5-shifting-definitions'
SEED = 20260921
STEPS = 16
CLAIMS = STEPS + 6
NONCE_PATH = Path(os.environ.get('VE_P5_NONCE', str(Path.home() / 'code/manage-agents/p5-id-nonce')))


def private_nonce(path=NONCE_PATH):
    """Create once, outside the repository; never serialize the key in artifacts."""
    if path.resolve().is_relative_to(HERE.parents[1]):
        raise PreflightError('ID nonce must be outside the repository')
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(os.urandom(32))
    key = path.read_bytes()
    if len(key) != 32 or path.stat().st_mode & 0o077:
        raise PreflightError('ID nonce must be 32 private bytes (mode 0600)')
    return key


def packet_id(slot, nonce):
    message = ('P5-construction-v5/' + slot['id']).encode()
    return 'i' + hmac.new(nonce, message, hashlib.sha256).hexdigest()[:32]


def prose_argument(nodes):
    return '\n\n'.join(f"[{n['id']}] {n['text']}" for n in nodes)



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
    for n in range(9, CLAIMS):
        parents.append(sorted({n - 1, *rng.sample(range(6, n - 1), rng.randrange(0, min(1, n-7)+1))}))
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
                          outgoing[n]) for n in range(CLAIMS)))


def argument_signature(graph):
    """Sufficient non-isomorphism invariant of the actual certified graph."""
    incoming = {e.conclusion: e.premises for e in graph.deductions}
    outgoing = Counter(p for e in graph.deductions for p in e.premises)
    depths = {}
    def depth(n):
        if n not in depths:
            depths[n] = 0 if n not in incoming else 1 + max(depth(p) for p in incoming[n])
        return depths[n]
    return digest(sorted((depth(c.name), len(incoming.get(c.name, ())), outgoing[c.name])
                         for c in graph.claims))


def conjunction(parts):
    result = parts[0]
    for part in parts[1:]:
        result = f'({result}) and ({part})'
    return result


# Compact, concrete sense descriptions: records and prose share this English
# surface, but never a per-node record/sense pointer.
SURFACES = [
    ('sealed', 'packaging intact'), ('logged', 'entry recorded'),
    ('weighed', 'mass measured'), ('coded', 'identifier assigned'),
    ('counted', 'quantity tallied'), ('cooled', 'temperature reduced'),
    ('sorted', 'contents ordered'), ('stored', 'location assigned'),
    ('labelled', 'label attached'), ('booked', 'transport reserved'),
    ('wrapped', 'cover fitted'), ('scanned', 'barcode read'),
    ('rated', 'grade recorded'), ('tagged', 'tag attached'),
    ('listed', 'catalogue entry made'), ('dated', 'date recorded'),
    ('sized', 'dimensions measured'), ('dried', 'moisture removed'),
    ('cleaned', 'surface washed'), ('marked', 'mark applied'),
    ('packed', 'container filled'), ('queued', 'place assigned'),
    ('routed', 'route assigned'), ('checked', 'check completed'),
    ('stamped', 'stamp applied'), ('wrapped-up', 'handling completed'),
    ('tracked', 'tracking enabled'), ('tested', 'test completed'),
    ('filed', 'document stored'), ('signed', 'signature recorded'),
    ('weighed-in', 'arrival mass recorded'), ('shelved', 'shelf assigned'),
    ('clipped', 'clip attached'), ('tied', 'tie attached'),
    ('folded', 'fold completed'), ('mounted', 'mount fitted'),
    ('bundled', 'bundle formed'), ('stacked', 'stack formed'),
    ('bagged', 'bag fitted'), ('boxed', 'box fitted'),
    ('numbered', 'number assigned'), ('photographed', 'image recorded'),
    ('loaded', 'loading completed'), ('unloaded', 'unloading completed'),
    ('received', 'receipt recorded'), ('shipped', 'departure recorded'),
    ('staged', 'staging completed'), ('scheduled', 'time assigned'),
    ('balanced', 'balance checked'), ('calibrated', 'calibration recorded'),
    ('secured', 'fastener fitted'), ('inspected', 'inspection completed'),
    ('processed', 'processing completed'), ('registered', 'registration recorded'),
    ('documented', 'documentation stored'), ('measured', 'measurement recorded'),
    ('reviewed', 'review completed'), ('audited', 'audit completed'),
    ('retained', 'retention recorded'), ('released', 'release recorded'),
]
AMBIGUITIES = [
    ('cleared', 'inspection passed', 'payment settled'),
    ('ready', 'packing completed', 'staffing arranged'),
    ('active', 'power connected', 'registry current'),
    ('open', 'seal removed', 'account enabled'),
    ('sound', 'casing intact', 'signal audible'),
    ('free', 'fee waived', 'space available'),
]


def build(slot, parents, nonce=None):
    """Four source branches span the sense × unit Cartesian product.

    The downstream unit is independently balanced across families. The shift
    keeps that unit but changes sense; smuggle keeps sense but changes unit.
    Both sample-to-lot and lot-to-sample transport require an unstated bridge.
    """
    rng = random.Random(slot['topology_seed'] + '/content-v3')
    size = slot['predicates']
    names = [f'p{i:02d}' for i in range(size)]
    rng.shuffle(names)
    main, primary, rival, selectors, dormant = names[:-8], names[-8], names[-7], names[-6:-2], names[-2:]
    # Four matched reference blocks: two comparison senses, a producer on
    # another unit, and its consumer. Every reference has exactly 3 prior
    # same-term conclusions, 2 senses and 2 units, independent of the label.
    reference_steps = [9, 13, 17, 21]
    target = rng.choice(reference_steps)
    parent = target - 1
    ordinary = main[6:]
    atoms = [(ordinary[n % len(ordinary)], f'lot{n // len(ordinary)}') for n in range(CLAIMS)]
    entity_names = [f'unit{n}' for n in range(8)]
    rng.shuffle(entity_names)
    entity_map = dict(zip(sorted({c for _, c in atoms} | {'sample0', 'comparison0'}), entity_names))
    atoms = [(p, entity_map[c]) for p, c in atoms]
    lot, sample = entity_map['lot0'], entity_map['sample0']
    sample_required = int(slot['cluster'].rsplit('-', 1)[1]) % 2 == 0
    entity, other_unit = (sample, lot) if sample_required else (lot, sample)
    decoy_predicates = iter(zip(main[:6:2], main[1:6:2]))
    block_pairs = [(primary, rival) if t == target else next(decoy_predicates) for t in reference_steps]
    decoy_pairs = []
    unit_rng = random.Random(slot['topology_seed'] + '/decoy-units-v5')
    for t, (first, second) in zip(reference_steps, block_pairs):
        atoms[t-3] = (second, entity_map['comparison0'])
        atoms[t-2] = (first, entity_map['comparison0'])
        atoms[t-1] = (first, entity if t == target else unit_rng.choice([lot, sample]))
        if t != target:
            decoy_pairs.extend([t-3, t-2])
    options = [(primary, entity), (rival, entity), (primary, other_unit), (rival, other_unit)]
    kind_index = ('benign', 'shift', 'smuggle').index(slot['variant'])
    chosen = options[kind_index]
    proposed_atoms = list(atoms)
    proposed_atoms[parent] = chosen
    ids = [f'n{n:02d}' for n in range(CLAIMS)]
    rng.shuffle(ids)
    record_ids = [f'r{n:02d}' for n in range(STEPS)]
    rng.shuffle(record_ids)
    surface_bank = list(SURFACES)
    rng.shuffle(surface_bank)
    surfaces = dict(zip(names, surface_bank))
    # Either critical sense is a property plausibly generalized from a
    # physical sample to a lot. Account/staffing senses remain decoys only.
    critical_senses = [
        ('clear', 'optically transparent', 'contamination absent'),
        ('light', 'density low', 'colour pale'),
        ('stable', 'temperature constant', 'shape retained'),
        ('dry', 'surface moisture absent', 'internal moisture low'),
    ]
    ambiguities = [rng.choice(critical_senses), *rng.sample(AMBIGUITIES, 3)]
    for (a, b), (term, first, second) in zip(
            [(primary, rival), *[pair for pair in block_pairs if pair != (primary, rival)]], ambiguities):
        senses = [first, second]; rng.shuffle(senses)
        surfaces[a] = (term, senses[0]); surfaces[b] = (term, senses[1])
    # Sense codes and glossary positions use separate per-packet random streams.
    # Neither permutation sorts by the selected route or semantic role.
    codes = list(range(1, size + 1))
    random.Random(slot['seed'] + '/sense-ids').shuffle(codes)
    descriptions = {p: f'{surfaces[p][0]}: {surfaces[p][1]} (R{code:02d})'
                    for p, code in zip(names, codes)}
    constants = sorted({c for _, c in atoms} | {sample})
    env = Environment.from_dict({'language': LANGUAGE, 'profile': PROFILE, 'spec_revision': SPEC_REVISION,
        'vocabulary': {'sorts': {'unit': {'description': 'A lot or its physical sample.'}},
            'predicates': {p: {'arguments': ['unit'], 'description': descriptions[p]} for p in names},
            'constants': {c: {'sort': 'unit', 'description': f'Sample taken from lot {lot}.' if c == sample else f'Lot {c}.'} for c in constants}}})

    def atom(pair):
        p, c = pair
        return f'@{c} is {p}'

    def clause(inputs, out):
        return f'if ({conjunction([atom(p) for p in inputs])}), then ({atom(out)})'

    def english(pair, qualified=True):
        p, c = pair
        term, meaning = surfaces[p]
        return f'{c} is {term}' + (f' ({meaning})' if qualified and term in {a[0] for a in ambiguities} else '')

    # Ignore several redundant cited parents in all variants. The selected
    # critical predecessor is also just context in later shortcuts; only the
    # next chain step transports it. Hence there is one localized defect.
    inputs_by_node = {}
    redundant = []
    for n, ps in enumerate(parents, 6):
        needed = [p for p in ps if not (n > target and p == parent)]
        if n > 9:
            extras = [p for p in needed if p != n-1]
            if extras:
                removed = rng.choice(extras)
                needed.remove(removed)
                redundant.append((n, removed))
        inputs_by_node[n] = [atoms[p] for p in needed]
    if len(redundant) < 1:
        raise ValueError('insufficient harmless context edges')

    # Four source routes share all upstream conditions. Their ordering is
    # shuffled without consulting this slot's label.
    branch_order = list(range(4)); rng.shuffle(branch_order)
    selector_atoms = [(p, lot) for p in selectors]
    rule_sets, merged_sets, records = [], [], []
    for n in range(6, CLAIMS):
        inputs = inputs_by_node[n]
        if n == parent:
            pairs = [(inputs + [selector_atoms[j]], options[j]) for j in branch_order]
        else:
            pairs = [(inputs, atoms[n])]
        # Unused conditional antecedents are legitimate alternative support,
        # identically present in benign and flawed dossiers. They cannot fire.
        if n in (6, 7, target):
            pairs.append(([(dormant[0], entity), (dormant[1], entity)], atoms[n]))
        rule_sets.append([clause(ins, out) for ins, out in pairs])
        merged_sets.append([clause([chosen if a == atoms[parent] and n == target else a for a in ins], out)
                            for ins, out in pairs])
        records.append({'id': record_ids[n-6], 'text': ' '.join(
            'If ' + ' and '.join(english(a) for a in ins) + ', then ' + english(out) + '.'
            for ins, out in pairs)})
    # Relationship is context, not a representativeness or predicate-transfer
    # premise. It appears in the same record in every sibling.
    relation_forms = [f'{sample} is a sample of lot {lot}.',
                      f'Lot {lot} supplied sample {sample}.',
                      f'The sample from lot {lot} is {sample}.']
    records[0]['text'] += ' ' + rng.choice(relation_forms)
    fact_atoms = atoms[:6] + [selector_atoms[kind_index]]
    fact = conjunction([atom(a) for a in fact_atoms])

    def make_graph(rule_groups, certify=False, bridge=None):
        leaves = [Claim.create(env, ids[0], fact + '.\n')]
        for group in range(5):
            leaves.append(Claim.create(env, ids[group+1], conjunction(
                [r for rules in rule_groups[group::5] for r in rules]) + '.\n'))
        claims = leaves + [Claim.create(env, ids[n], atom(proposed_atoms[n]) + '.\n') for n in range(6, CLAIMS)]
        if bridge is not None:
            claims.append(bridge)
        edges = []
        for n, ps in enumerate(parents, 6):
            premises = list(dict.fromkeys([ids[0] if p < 6 else ids[p] for p in ps] + [ids[1+(n-6)%5]]))
            if n == parent and ids[0] not in premises:
                premises.append(ids[0])
            if n == target and bridge is not None:
                premises.append('bridge')
            edges.append(Deduction(f'e{ids[n][1:]}', tuple(premises), ids[n]))
        graph = ArgumentGraph(env, tuple(claims), tuple(edges), ids[CLAIMS-1], target_scope='original dossier root')
        if certify:
            by_id = {c.name: c for c in claims}
            new = []
            for edge in edges:
                proof = prove_entailment(env, [by_id[n].ast for n in edge.premises], by_id[edge.conclusion].ast)
                if proof.status != 'Found':
                    raise ValueError(f'proof search {edge.name}: {proof.status}')
                new.append(replace(edge, certificates=({'edge_id': deduction_identity(graph, edge),
                    'direction': 'follows', 'proof': proof.certificate},)))
            graph = replace(graph, deductions=tuple(new))
        return graph

    proposed = make_graph(merged_sets, True)
    intended = make_graph(rule_sets, slot['variant'] == 'benign')
    bridge = Claim.create(env, 'bridge', clause([chosen], atoms[parent]) + '.\n')
    augmented = intended if slot['variant'] == 'benign' else make_graph(rule_sets, True, bridge)
    # Least closure of every source rule, not just the cited proof path.
    horn_rules = []
    for n in range(6, CLAIMS):
        ins = inputs_by_node[n]
        if n == parent:
            horn_rules.extend((ins + [selector_atoms[j]], options[j]) for j in range(4))
        else:
            horn_rules.append((ins, atoms[n]))
        if n in (6, 7, target):
            horn_rules.append(([(dormant[0], entity), (dormant[1], entity)], atoms[n]))
    true = set(fact_atoms)
    while True:
        expanded = true | {out for ins, out in horn_rules if set(ins) <= true}
        if expanded == true:
            break
        true = expanded
    model = FiniteModel.from_dict(env, {'complete': True, 'domains': {'unit': constants},
        'constants': {c: c for c in constants}, 'relations': {p: [[c] for q, c in sorted(true) if q == p] for p in names}})
    leaves = intended.claims[:6]
    root = next(c for c in intended.claims if c.name == intended.root)
    if not all(evaluate(env, c.ast, model) for c in leaves):
        raise ValueError('unsatisfied declared premises')
    negative = check_countermodel(env, [c.ast for c in leaves], root.ast, model).valid
    if negative != (slot['variant'] != 'benign'):
        raise ValueError('whole-premise root witness failure')

    other_checks = [j for j in branch_order if j != kind_index]
    plain_leaves = [{'id': ids[0], 'text': '; '.join(english(a) for a in fact_atoms) +
        '. The checks that ' + ' and '.join(english(selector_atoms[j]) for j in other_checks) + ' remain unassumed.'}]
    for group in range(5):
        plain_leaves.append({'id': ids[group+1], 'text': 'Rules ' + ', '.join(r['id'] for r in records[group::5]) + ' are declared.'})
    nodes, record_uses = [], {}
    # Independent of the selected critical route, with the same count in all kinds.
    # All comparison positions are eligible, irrespective of which of the
    # four reference blocks is critical. No producer or consumer is eligible.
    tail_node = random.Random(slot['topology_seed'] + '/tail-position-v6').choice(
        [t-offset for t in reference_steps for offset in (3, 2)])
    for n, ps in enumerate(parents, 6):
        cited = [proposed_atoms[p] for p in ps]
        # At the target the term is reused without its qualifier. The record's
        # conditional fixes the relevant sense; the shift is in this claimed
        # inference, not a change to that authoritative conditional. A result
        # for the other unit is likewise offered directly as grounds, without
        # stating a property-transfer bridge.
        contents = []
        for q, a in zip(ps, cited):
            if atoms[q] not in inputs_by_node[n]:
                continue
            # Refer to the earlier result by content, without silently
            # restating a lot fact when only a sample fact was established.
            if q == parent and n > target:
                continue  # Redundant context is not needed to state this inference.
            if q == n - 1 and n in reference_steps:
                contents.append(f'the immediately preceding {surfaces[a[0]][0]} result holds')
            else:
                contents.append(english(a, False))
        if n == parent:
            contents.append(english(selector_atoms[kind_index], False))
        from experiments.p5_paraphrase import render_inference
        text = render_inference(' and '.join(contents), english(proposed_atoms[n], False), (n-6) % 4)
        if n == tail_node:
            # Record alternatives are genuine contextual comparisons, not
            # asserted premises. Permute which route is relied on while
            # preserving the complete lexical workload across siblings.
            text += ' The checks that ' + ' and '.join(english(selector_atoms[j]) for j in other_checks)
            text += rng.choice([' would establish that ', ' would imply that ', ' would yield that ']) + ' and '.join(english(options[j], False) for j in other_checks) + ', respectively.'
        nodes.append({'id': ids[n], 'parents': list(dict.fromkeys(ids[p] if p >= 6 else ids[0] for p in ps)), 'text': text})
        record_uses[ids[n]] = {'conclusion': descriptions[proposed_atoms[n][0]],
            'entity': proposed_atoms[n][1], 'required_inputs': [english(a) for a in inputs_by_node[n]],
            'source_record': record_ids[n-6]}
    glossary = [{'term': surfaces[p][0], 'sense': descriptions[p]} for p in names]
    random.Random(slot['seed'] + '/glossary-position').shuffle(glossary)
    rng.shuffle(plain_leaves); rng.shuffle(records)
    public_id = packet_id(slot, private_nonce() if nonce is None else nonce)
    dossier = {'id': public_id, 'glossary': glossary, 'premises': plain_leaves,
        'records': records, 'nodes': nodes, 'argument': prose_argument(nodes), 'root': ids[CLAIMS-1]}
    return dossier, {'id': public_id, 'slot_id': slot['id'], 'family': slot['cluster'], 'split': slot['split'],
        'kind': slot['variant'], 'predicates': size, 'acceptable_locations': [[ids[target]], [ids[parent], ids[target]]],
        'sense_use_mapping': record_uses, 'root_meaning': english(atoms[CLAIMS-1]),
        'bridge': bridge.source, 'affected_uses': [ids[parent], ids[target]]}, {
        'id': public_id, 'family': slot['cluster'], 'predicates': size, 'topology': parents, 'structural_signature': structural_signature(parents),
        'intended': intended.to_dict(), 'merged': proposed.to_dict(), 'model': model.to_dict(),
        'bridge': bridge.to_dict(env), 'augmented': augmented.to_dict(),
        'construction': {'version': 6, 'tail_node': ids[tail_node], 'target': ids[target], 'parent': ids[parent],
            'unqualified_reference_nodes': [ids[n] for n in reference_steps],
            'redundant_edges': [[ids[n], ids[q]] for n, q in redundant],
            'decoy_nodes': [ids[n] for n in decoy_pairs],
            'comparison_nodes': [ids[target-3], ids[target-2]],
            'dormant_predicates': dormant, 'selector_predicates': selectors},
        'predicate_identities': {p: digest({'environment_id': env.environment_id, 'symbol': p,
                                            'declaration': env.to_dict()['vocabulary']['predicates'][p]}) for p in names}}

def generate(base=HERE):
    if any(r.get('identity','').startswith('scored/') for r in read(base/'runs/study/costs.jsonl')):
        raise PreflightError('scored material change requires amendment and separately labeled run')
    if (base / 'freeze.json').exists() and json.loads((base/'freeze.json').read_text()).get('status') == 'READY_FOR_SCORED':
        raise PreflightError('frozen materials require an amendment')
    nonce = private_nonce()
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
            dossier, label, graph = build(slot, family_topologies[family], nonce)
        except Exception as exc:
            attempts.append({'slot': slot, 'topology': family_topologies[family], 'reason': str(exc)})
            archive(base/'materials/construction-ledger.jsonl.gz', attempts)
            raise
        dossiers.append(dossier); labels.append(label); graphs.append(graph)
    # Shuffle opaque IDs, not variant-ordered inventory positions. This exact
    # permutation is shared by archive/export/leakage checks.
    triples = list(zip(dossiers, labels, graphs))
    triples.sort(key=lambda row: row[0]['id'])
    random.Random(f'{SEED}/packet-order-v3').shuffle(triples)
    dossiers, labels, graphs = map(list, zip(*triples))
    actual_signatures = {}
    for row in graphs:
        graph = ArgumentGraph.from_dict(row['intended'])
        signature = argument_signature(graph)
        family = row['family']
        if actual_signatures.setdefault(family, signature) != signature:
            raise ValueError('sibling formal topologies differ')
        row['formal_structural_signature'] = signature
    if len(set(actual_signatures.values())) != 28:
        raise ValueError('actual formal graph invariant collision')
    archive(base/'materials/dossiers.jsonl.gz', dossiers)
    archive(base/'labels.jsonl.gz', labels)
    archive(base/'materials/graphs.jsonl.gz', graphs)
    archive(base/'materials/construction-ledger.jsonl.gz', attempts)
    # A reproducible process-isolated OFFLINE DRAFT pass is deliberately not
    # represented as the preregistered Qwen independent author.
    import subprocess, sys
    paraphrases = []
    for dossier in dossiers:
        # One packet per process: sibling content never enters the editor context.
        process = subprocess.run([sys.executable, '-m', 'experiments.p5_paraphrase'],
            input=packed([dossier]), text=True, capture_output=True, check=True)
        paraphrases.extend(json.loads(process.stdout))
    archive(base/'materials/paraphrases.jsonl.gz', paraphrases)
    by_id = {p['id']: p for p in paraphrases}
    for split in ('dev','scored'):
        archive(base/f'materials/{split}.jsonl.gz', [dict(id=d['id'], group=l['family'], split=split,
            payload={**d, 'argument': by_id[d['id']]['argument']},
            paraphrase_status='OFFLINE_DRAFT_NOT_QWEN') for d,l in zip(dossiers,labels) if l['split']==split])
    if not (base/'materials/review-ledger.jsonl.gz').exists():
        archive(base/'materials/review-ledger.jsonl.gz', [])
    report = {'passed': len(signatures)==28, 'slots': len(labels), 'families':28,
        'method':'pairwise distinct directed degree/depth invariants; sufficient non-isomorphism test',
        'failed_candidates': len(attempts), 'actual_formal_graph_families': len(set(actual_signatures.values())),
        'generator_version': 6, 'deduction_steps': STEPS, 'source_records_fixed_within_family': True, 'independent_prose_ready': False,
        'status':'BUILT_REFERENCE_AND_OFFLINE_DRAFT_REVIEW_BLOCKED', 'paid_calls':0}
    write_json(base/'checks/construction.json', report)
    return report
