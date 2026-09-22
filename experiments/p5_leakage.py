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
            len(q['nodes']), len(q['premises']), len(q['argument']),
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
    random.Random(f'{SEED}/packet-order-v2').shuffle(items)
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
    return {'passed': all(r['passed'] for r in probes.values()) and all(r['converged'] for r in convergence),
            'estimator':{'model':'LogisticRegression', 'C':1.0, 'solver':'lbfgs', 'max_iter':15000, 'seed':SEED},
            'convergence':convergence, 'chance_accuracy': 1/3,
            'threshold': 1/3, 'accuracy': max(r['accuracy'] for r in probes.values()),
            'policy': 'Every fixed probe must score at or below three-class chance; no seed/hyperparameter selection.',
            'fit_scope': 'all 84 slots; 28 leave-family-out folds; no sibling crosses a fold',
            'classes': classes, 'features': list(FEATURE_NAMES), 'probes': probes,
            'packet_sha256': digest([i['payload'] for i in items]),
            'label_sha256': digest([labels[i['id']]['kind'] for i in items]),
            'export_order_sha256': digest([i['id'] for i in items]),
            'order_mod3_counts': {str(k): dict(Counter(labels[i['id']]['kind'] for n, i in enumerate(items) if n%3==k)) for k in range(3)},
            'generation_calls': 0, 'limitation': 'Shortcut screen, not proof of semantic difficulty or source fidelity.'}
