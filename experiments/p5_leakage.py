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


def audit(base=HERE):
    import numpy as np
    from scipy.sparse import csr_matrix, hstack
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
    from sklearn.model_selection import LeaveOneGroupOut
    from sklearn.preprocessing import StandardScaler

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
    folds = list(LeaveOneGroupOut().split(X, y, groups))
    predictions = {key: np.empty(len(items), dtype=int) for key in ('tokens', 'structure', 'combined')}
    convergence = []
    for train, test in folds:
        # Fit every transformation inside the held-family-out fold.
        vectorizer = CountVectorizer(token_pattern=r'(?u)\b\w+\b')
        a = vectorizer.fit_transform([texts[k] for k in train])
        b = vectorizer.transform([texts[k] for k in test])
        scaler = StandardScaler()
        c = csr_matrix(scaler.fit_transform(X[train])); d = csr_matrix(scaler.transform(X[test]))
        for key, training, testing in [('tokens', a, b), ('structure', c, d),
                                       ('combined', hstack([a, c]), hstack([b, d]))]:
            clf = LogisticRegression(C=1.0, solver='lbfgs', max_iter=15000, random_state=SEED)
            clf.fit(training, y[train])
            convergence.append({'held_out_family':str(groups[test[0]]), 'probe':key,
                'iterations':int(max(clf.n_iter_)), 'converged':int(max(clf.n_iter_)) < clf.max_iter})
            predictions[key][test] = clf.predict(testing)
    probes = {}
    for key, pred in predictions.items():
        accuracy = float(accuracy_score(y, pred))
        probes[key] = {'accuracy': accuracy, 'balanced_accuracy': float(balanced_accuracy_score(y, pred)),
                       'correct': int(sum(pred == y)), 'confusion_matrix': confusion_matrix(y, pred, labels=range(3)).tolist(),
                       'passed': accuracy <= 1/3,
                       'predictions': [{'item_id': i['id'], 'truth': classes[int(t)], 'predicted': classes[int(v)]}
                                       for i, t, v in zip(items, y, pred)]}
    probes.update(relational_probes(items, y, groups))
    return {'passed': all(r['passed'] for r in probes.values()) and all(r['converged'] for r in convergence),
            'estimator':{'model':'LogisticRegression', 'C':1.0, 'solver':'lbfgs', 'max_iter':15000, 'seed':SEED},
            'convergence':convergence, 'chance_accuracy': 1/3,
            'threshold': 1/3, 'accuracy': max(r['accuracy'] for r in probes.values()),
            'policy': 'Every fixed probe must score at or below three-class chance; no seed/hyperparameter selection.',
            'fit_scope': 'All 84 slots. Logistic: 28 leave-family-out folds. Node trees: stratified and stratified-grouped 6-fold CV (reported separately).',
            'classes': classes, 'features': list(FEATURE_NAMES), 'probes': probes,
            'packet_sha256': digest([i['payload'] for i in items]),
            'label_sha256': digest([labels[i['id']]['kind'] for i in items]),
            'export_order_sha256': digest([i['id'] for i in items]),
            'order_mod3_counts': {str(k): dict(Counter(labels[i['id']]['kind'] for n, i in enumerate(items) if n%3==k)) for k in range(3)},
            'generation_calls': 0, 'limitation': 'Shortcut screen, not proof of semantic difficulty or source fidelity.'}

ATOM = re.compile(r'(unit\d+) is ([a-z-]+)(?: \(([a-z -]+)\))?')
MARKERS = ('Given', 'From', 'Using', 'would establish', 'would imply', 'would yield')


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
        head, _, tail = node['text'].partition('. ')
        m = re.fullmatch(r'(?:Given|From|Using) (.*), (unit\d+ is .+?)\.?', head)
        if not m:
            raise ValueError('unparsed inference node')
        ants, con = ATOM.findall(m[1]), ATOM.findall(m[2])[0]
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


def relational_probes(items, y, groups):
    import numpy as np
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.metrics import accuracy_score, confusion_matrix
    features = [node_features(i['payload']) for i in items]
    vectorizer = DictVectorizer(sparse=False)
    X = vectorizer.fit_transform(features)  # names only; no learned statistics
    result = {}
    # Fix seeds/hyperparameters before inspecting construction results.
    for key, splitter in [('node_relations', StratifiedKFold(6, shuffle=True, random_state=1)),
                          ('node_relations_grouped', StratifiedGroupKFold(6, shuffle=True, random_state=1))]:
        pred = np.empty(len(y), dtype=int)
        folds = []
        for train, test in splitter.split(X, y, groups if 'grouped' in key else None):
            clf = DecisionTreeClassifier(max_depth=3, random_state=1)
            clf.fit(X[train], y[train]); pred[test] = clf.predict(X[test])
            folds.append({'test_ids':[items[k]['id'] for k in test],
                          'split_features':[vectorizer.feature_names_[v] for v in clf.tree_.feature if v >= 0]})
        accuracy = float(accuracy_score(y, pred))
        result[key] = {'accuracy':accuracy, 'balanced_accuracy':accuracy,
                       'correct':int(sum(pred == y)), 'passed':accuracy <= 1/3,
                       'confusion_matrix':confusion_matrix(y, pred, labels=range(3)).tolist(),
                       'estimator':{'model':'DecisionTreeClassifier', 'max_depth':3, 'random_state':1},
                       'cv':type(splitter).__name__, 'n_splits':6,
                       'features':vectorizer.feature_names_, 'folds':folds,
                       'predictions':[{'item_id':i['id'], 'truth':int(t), 'predicted':int(v)}
                                      for i,t,v in zip(items,y,pred)]}
    # Adapt the reviewer's closed-form unit/rank rule to every current phrase.
    # In the four-way construction, tied senses have ranks 0 or 2, never 1.
    pred = np.asarray([2 if f['branch_con_unit_is_sample'] else
                       0 if f['branch_con_sense_rank'] == 1 else 1 for f in features])
    accuracy = float(accuracy_score(y, pred))
    result['reviewer_unit_rank_rule'] = {
        'accuracy':accuracy, 'balanced_accuracy':accuracy, 'correct':int(sum(pred == y)),
        'passed':accuracy <= 1/3, 'coverage':len(items),
        'rule':'branch conclusion is sample -> smuggle; else sense rank 1 -> benign; else shift',
        'confusion_matrix':confusion_matrix(y, pred, labels=range(3)).tolist()}
    return result
