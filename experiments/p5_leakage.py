"""Blinded-surface shortcut probes, grouped by the independent family unit.

Fixed features/hyperparameters, no seed search or classifier-driven selection.
All 84 construction slots are audited; this is not an efficacy evaluation.
"""
from collections import Counter
import random
import re

from experiments.p5_materials import HERE, SEED, read
from ve_experiments.paid import digest, packed


FEATURE_NAMES = ('bytes', 'words', 'glossary', 'records', 'nodes', 'premises',
                 'argument_bytes', 'node_bytes', 'record_bytes', 'root_index',
                 'edges', 'unique_parents', 'max_indegree', 'min_indegree',
                 'mean_indegree',
                 'sense_indices', 'unique_sense_indices', 'record_pointers')


def feature_row(item, index):
    q = item['payload']; text = packed(q)
    degrees = [len(n['parents']) for n in q['nodes']]
    sense_indices = re.findall(r'\bR\d+\b', text)
    return [len(text), len(text.split()), len(q['glossary']), len(q['records']),
            len(q['nodes']), len(q['premises']), len(q.get('argument', '')),
            sum(len(n['text']) for n in q['nodes']), sum(len(r['text']) for r in q['records']),
            int(q['root'][1:]), sum(degrees), len({p for n in q['nodes'] for p in n['parents']}),
            max(degrees), min(degrees), sum(degrees)/len(degrees),
            len(sense_indices),
            len(set(sense_indices)), sum('rule_record' in n for n in q['nodes'])]


PERMUTATIONS = 199


def prose_surface(item):
    """The exact shared argument judged by all arms, never draft node texts."""
    prose = item['payload']['argument']
    paragraphs = prose.split('\n\n')
    return prose, [len(prose), len(prose.split()), len(paragraphs),
                   *[len(paragraph) for paragraph in paragraphs]]


def permutation_summary(observed, null):
    """One-sided max statistic: repeat the entire best-of-k search under null."""
    import numpy as np
    null = np.asarray(null)
    maximum = np.max(null, axis=1)
    pvalues = (1 + (maximum[:, None] >= np.asarray(observed)[None, :] - 1e-12).sum(0)) / (len(null) + 1)
    return {'p_values':pvalues.tolist(), 'p_value':float(min(pvalues)),
            'passed':bool(min(pvalues) >= .05),
            'null_max_mean':float(maximum.mean()), 'null_max_p95':float(np.quantile(maximum, .95)),
            'null_maxima':maximum.tolist()}


def audit(base=HERE, *, workers=8):
    import numpy as np
    from joblib import Parallel, delayed, parallel_config
    from scipy.sparse import csr_matrix, hstack
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import LeaveOneGroupOut, StratifiedKFold, StratifiedGroupKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier
    from threadpoolctl import threadpool_limits

    items = read(base/'materials/dev.jsonl.gz') + read(base/'materials/scored.jsonl.gz')
    labels = {l['id']: l for l in read(base/'labels.jsonl.gz')}
    items.sort(key=lambda item: item['id'])
    random.Random(f'{SEED}/packet-order-v3').shuffle(items)
    if len(items) != 84 or len(labels) != 84:
        return {'passed': False, 'reason': 'requires all 84 packets'}
    classes = ['benign', 'shift', 'smuggle']
    y = np.asarray([classes.index(labels[i['id']]['kind']) for i in items])
    groups = np.asarray([i['group'] for i in items])
    X = np.asarray([feature_row(i, n) for n, i in enumerate(items)], dtype=float)
    texts = [packed(i['payload']) for i in items]
    prose_texts, prose_rows = zip(*(prose_surface(i) for i in items))
    prose_X = np.asarray(prose_rows, dtype=float)
    folds = list(LeaveOneGroupOut().split(X, y, groups))
    prepared = []
    for train, test in folds:
        vectorizer = CountVectorizer(token_pattern=r'(?u)\b\w+\b')
        a = vectorizer.fit_transform([texts[k] for k in train])
        b = vectorizer.transform([texts[k] for k in test])
        scaler = StandardScaler()
        c = csr_matrix(scaler.fit_transform(X[train])); d = csr_matrix(scaler.transform(X[test]))
        prose_vectorizer = CountVectorizer(token_pattern=r'(?u)\b\w+\b')
        pa = prose_vectorizer.fit_transform([prose_texts[k] for k in train])
        pb = prose_vectorizer.transform([prose_texts[k] for k in test])
        prose_scaler = StandardScaler()
        pc = csr_matrix(prose_scaler.fit_transform(prose_X[train]))
        pd = csr_matrix(prose_scaler.transform(prose_X[test]))
        prepared.append((train, test, [(a,b), (c,d), (hstack([a,c]).tocsr(),hstack([b,d]).tocsr()),
            (pa,pb), (pc,pd), (hstack([pa,pc]).tocsr(),hstack([pb,pd]).tocsr())]))
    features = [node_features(i['payload']) for i in items]
    vectorizer = DictVectorizer(sparse=False)
    Z = vectorizer.fit_transform(features)
    all_features = np.column_stack([X, Z])
    names = [*FEATURE_NAMES, *vectorizer.feature_names_]
    # Fixed label-independent seven-fold family assignment. Value->majority
    # lookup is refitted for every feature, fold, and permuted label vector.
    family_names = sorted(set(groups)); random.Random(1).shuffle(family_names)
    assignment = {g:n % 7 for n,g in enumerate(family_names)}
    lookup_folds = []
    for f in range(7):
        test = np.flatnonzero([assignment[g] == f for g in groups])
        train = np.flatnonzero([assignment[g] != f for g in groups])
        equal = (all_features[test].T[:,:,None] == all_features[train].T[:,None,:]).astype(float)
        lookup_folds.append((train,test,equal))
    rule = np.asarray([2 if f['branch_con_unit_is_sample'] else
                       0 if f['branch_con_sense_rank'] == 1 else 1 for f in features])
    convergence = []
    def scores(yy, retain=False):
        pred = np.empty((9+len(names), len(yy)), dtype=int)
        for train,test,matrices in prepared:
            for k,(a,b) in enumerate(matrices):
                clf = LogisticRegression(C=1.0, solver='lbfgs', max_iter=15000, random_state=SEED)
                clf.fit(a, yy[train]); pred[k,test] = clf.predict(b)
                if max(clf.n_iter_) >= clf.max_iter:
                    raise ValueError('nonconverged permutation probe')
                if retain:
                    convergence.append({'probe':k,'held_out_family':str(groups[test[0]]),
                                        'iterations':int(max(clf.n_iter_)), 'converged':True})
        for k,splitter in enumerate((StratifiedKFold(6,shuffle=True,random_state=1),
                                    StratifiedGroupKFold(6,shuffle=True,random_state=1)),6):
            for train,test in splitter.split(Z,yy,groups if k == 7 else None):
                clf = DecisionTreeClassifier(max_depth=3,random_state=1)
                clf.fit(Z[train],yy[train]); pred[k,test] = clf.predict(Z[test])
        pred[8] = rule
        for train,test,equal in lookup_folds:
            counts = equal @ np.eye(3)[yy[train]]
            votes = counts.argmax(2)
            votes[counts.sum(2) == 0] = np.bincount(yy[train],minlength=3).argmax()
            pred[9:,test] = votes
        return (pred == yy).mean(1), pred
    def null_score(yy):
        return scores(yy)[0]
    # Exchange labels within families, preserving one of each label in every
    # family. Refit every estimator, including label-dependent stratification.
    # The ID nonce is never regenerated based on these results.
    with threadpool_limits(limits=1):
        observed, predictions = scores(y, True)
        rng = np.random.default_rng(SEED)
        members = [np.flatnonzero(groups == g) for g in sorted(set(groups))]
        permuted_labels = []
        for _ in range(PERMUTATIONS):
            yy = y.copy()
            for members_in_family in members:
                yy[members_in_family] = rng.permutation(yy[members_in_family])
            permuted_labels.append(yy)
        # Independent refits, in the original RNG/output order. Process-local
        # numerical thread limits avoid oversubscription; no estimator or null
        # statistic changes with worker count.
        with parallel_config(backend='loky', inner_max_num_threads=1):
            null = Parallel(n_jobs=workers, verbose=5)(delayed(null_score)(yy) for yy in permuted_labels)
    comparison = permutation_summary(observed, null)
    probe_names = ['tokens','structure','combined','prose_tokens','prose_structure','prose_combined','node_relations','node_relations_grouped',
                   'reviewer_unit_rank_rule', *['single/'+n for n in names]]
    probes = {name:{'accuracy':float(a),'correct':int(round(a*len(items))),
                   'adjusted_p_value':pv,'passed':pv >= .05}
              for name,a,pv in zip(probe_names,observed,comparison['p_values'])}
    localization = localization_probe(items, labels)
    return {'passed':comparison['passed'] and localization['passed'], 'localization':localization, 'probes':probes, 'accuracy':float(max(observed)),
            'best_probe':probe_names[int(observed.argmax())], 'convergence':convergence,
            'chance_accuracy':1/3, 'minimum_p_value':.05,
            'permutation_null':{k:v for k,v in comparison.items() if k != 'p_values'},
            'permutations':PERMUTATIONS, 'k':len(probes), 'seed':SEED,
            'policy':'Within-family label permutations; refit all probes and compare best-of-k to each permuted best-of-k. Pass p >= 0.05; no seed or nonce search.',
            'features':names, 'classes':classes,
            'packet_sha256':digest([i['payload'] for i in items]),
            'prose_sha256':digest(list(prose_texts)),
            'prose_scope':'Exact shared argument text; three prose-only probes included in every best-of-k null refit. Original node probes cover the additional VE node block.',
            'label_sha256':digest([labels[i['id']]['kind'] for i in items]),
            'export_order_sha256':digest([i['id'] for i in items]),
            'order_mod3_counts':{str(k):dict(Counter(labels[i['id']]['kind'] for n,i in enumerate(items) if n%3==k)) for k in range(3)},
            'generation_calls':0, 'limitation':'Shortcut screen, not proof of semantic difficulty or source fidelity.'}

ATOM = re.compile(r'(unit\d+) is ([a-z-]+)(?: \(([a-z -]+)\))?')
MARKERS = ('Because', 'Since', 'Given that', 'It follows that', 'would establish', 'would imply', 'would yield')


def node_features(packet):
    """Public-text relations only; no labels, reference locations or chaining.

    Retain a row for EVERY node, then flatten by public list position and
    collect extrema/means plus the alternative-bearing node. This catches a
    marker-targeted shortcut without assuming a single wording of that marker.
    """
    import numpy as np
    senses, orders = {}, {}
    for pos, gloss in enumerate(packet['glossary']):
        m = re.fullmatch(r'([a-z-]+): ([a-z -]+) \(R(\d+)\)', gloss['sense'])
        if not m:
            raise ValueError('unparsed glossary entry')
        senses[m[1], m[2]] = int(m[3]); orders[m[1], m[2]] = pos
    samples = set()
    for record in packet['records']:
        t = record['text']
        for pattern, group in [(r'(unit\d+) is a sample of lot (unit\d+)', 1),
                               (r'Lot (unit\d+) supplied sample (unit\d+)', 2),
                               (r'The sample from lot (unit\d+) is (unit\d+)', 2),
                               (r'Here (unit\d+) names a sample taken from lot (unit\d+)', 1)]:
            samples.update(m[group] for m in re.finditer(pattern, t))
    rows = []
    for pos, node in enumerate(packet['nodes']):
        from experiments.p5_paraphrase import inference_parts
        premises, conclusion, tail, _ = inference_parts(node['text'])
        ants, con = ATOM.findall(premises), ATOM.findall(conclusion)[0]
        alt_tail = re.split(r'would (?:establish|imply|yield) that ', tail)
        alts = ATOM.findall(alt_tail[-1]) if len(alt_tail) > 1 else []
        key = con[1:]; sid = senses.get(key, -1); order = orders.get(key, -1)
        altids = [senses.get(a[1:], -1) for a in alts]
        altorders = [orders.get(a[1:], -1) for a in alts]
        row = dict(con_unit_is_sample=int(con[0] in samples),
                   con_unit_in_ants=int(con[0] in {a[0] for a in ants}),
                   con_unit_num=int(con[0][4:]), con_sense_id=sid,
                   con_sense_order=order,
                   con_sense_rank=sum(v < sid for v in altids),
                   con_order_rank=sum(v < order for v in altorders),
                   n_alts=len(alts), n_ants=len(ants), position=pos,
                   indegree=len(node['parents']),
                   outdegree=sum(node['id'] in n['parents'] for n in packet['nodes']),
                   is_root=int(node['id'] == packet['root']),
                   sample_ants=sum(a[0] in samples for a in ants),
                   sample_alts=sum(a[0] in samples for a in alts))
        for j in range(3):
            row[f'alt{j}_is_sample'] = int(alts[j][0] in samples) if j < len(alts) else -1
            row[f'con_sense_lt_alt{j}'] = int(sid < altids[j]) if j < len(alts) else -1
        row.update({f'marker_{phrase}':int(phrase in node['text']) for phrase in MARKERS})
        rows.append(row)
    features = {f'node_{i}_{k}':v for i, r in enumerate(rows) for k, v in r.items()}
    for k in rows[0]:
        values = [r[k] for r in rows]
        features.update({f'{op}_{k}':float(fn(values)) for op, fn in
                         [('min', min), ('max', max), ('mean', np.mean)]})
    candidates = [r for r in rows if r['n_alts']]
    if len(candidates) != 1:
        raise ValueError('expected one four-way branch node')
    features.update({f'branch_{k}':v for k, v in candidates[0].items()})
    return features


def localization_probe(items, labels):
    """Fixed reviewer shortcut; target permutations retain sibling dependence.

    The attacker gets only the tail position and the four reference positions.
    Permute the critical reference block within each family, never packet IDs
    or semantic contents. A tail outside these blocks makes the rule abstain.
    """
    from scipy.stats import binom
    families = {}
    rows = []
    for item in items:
        q = item['payload']
        paragraphs = q['argument'].split('\n\n')
        tails = [i for i, t in enumerate(paragraphs) if 'The checks that ' in t]
        refs = [i for i, t in enumerate(paragraphs) if 'the immediately preceding ' in t.lower()]
        if len(tails) != 1 or len(refs) != 4:
            return {'passed': False, 'reason': 'expected one tail and four references per packet'}
        if labels[item['id']]['kind'] == 'benign':
            continue
        index = tails[0]
        candidate = index+1 if index+1 in refs else None
        prediction = {q['nodes'][index]['id'], q['nodes'][candidate]['id']} if candidate is not None else set()
        hit = prediction in [set(v) for v in labels[item['id']]['acceptable_locations']]
        next_ref = next((r for r in refs if r > index), None)
        block_hit = next_ref is not None and [q['nodes'][next_ref]['id']] in labels[item['id']]['acceptable_locations']
        row = {'item_id': item['id'], 'tail_index': index, 'eligible': candidate is not None, 'hit': hit,
               'block_hit': block_hit}
        rows.append(row)
        families.setdefault(item['group'], []).append(row)
    if any(len(v) != 2 or len({(r['tail_index'], r['eligible'], r['hit'], r['block_hit']) for r in v}) != 1 for v in families.values()):
        return {'passed': False, 'reason': 'localization null requires matched siblings'}
    eligible = sum(v[0]['eligible'] for v in families.values())
    hits = sum(v[0]['hit'] for v in families.values())
    pvalue = float(binom.sf(hits-1, eligible, .25))
    block_hits = sum(v[0]['block_hit'] for v in families.values())
    block_p = float(binom.sf(block_hits-1, len(families), .25))
    adjusted_p = min(1., 2*min(pvalue, block_p))
    return {'passed': bool(rows) and adjusted_p >= .05, 'adjusted_p_value':adjusted_p,
            'multiplicity':'Bonferroni over two fixed localization rules',
            'next_reference_block':{'correct':2*block_hits,'n':len(rows),
                'accuracy':block_hits/max(1,len(families)), 'chance_accuracy':.25, 'p_value':block_p},
            'correct': sum(r['hit'] for r in rows),
            'n': len(rows), 'accuracy': sum(r['hit'] for r in rows)/max(1,len(rows)),
            'chance_accuracy': eligible*.25/max(1,len(families)), 'p_value': pvalue,
            'eligible_families': eligible, 'hit_families': hits,
            'null': 'Exact within-family permutation of the four reference blocks; sibling pairs move together. Noncandidate tail abstains.',
            'rule': 'tail producer plus unique immediately following back-reference consumer',
            'rows': rows}
