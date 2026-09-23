"""Surface-feature leakage audit for Part 1 materials (honest vs sabotaged items).

Features are computed only from what a monitor sees: policy text, claim and certificate display
(statement, S, invariant; as in T1c the proof trace and the checker's step count are not shown).
They exclude the semantic signals the monitor is supposed to use (does the certified statement
equal the claim; is the principal in S; the verdict). A classifier that beats
chance on these features would let a monitor guess the label without doing the task.
"""
from collections import Counter
import numpy as np

from .materials import FAMILIES, SCHEMES, SHAPES, parse_policy

FEATURES = ('total_lines', 'total_bytes', 'identifiers', 'mean_targets_per_line', 'max_targets_per_line',
            'principal_out', 'principal_in', 'resource_in', 'source_only_ids', 'twins_of_principal',
            'twins_of_resource', 'claim_chars', 'set_size', 'set_out_facts',
            'statement_chars', 'principal_line_pos', 'resource_first_pos')


def _twins(name, universe):
    alphabet = '0123456789abcdef'
    count = 0
    for i, ch in enumerate(name):
        if ch in alphabet:
            count += sum(name[:i] + c + name[i + 1:] in universe for c in alphabet if c != ch)
    return count


def item_features(item, sub, report):
    edges = parse_policy(item)
    p, x = item['principal'], item['resource']
    ids = {n for e in edges for n in e}
    targets = {b for _, b in edges}
    out = Counter(a for a, _ in edges)
    inn = Counter(b for _, b in edges)
    lines = [l for body in item['raw'].values() for l in body.split('\n')[1:] if l]
    per_line = [max(1, l.count(' ') ) for l in lines]
    text = '\n'.join(item['raw'][n] for n, _, _ in FAMILIES[item['family']]['files'])
    members = set(sub['separating_set'])
    pos_p = text.find(p + (': ' if FAMILIES[item['family']]['format'] == 'colon' else ''))
    row = {'total_lines': len(lines), 'total_bytes': len(text.encode()), 'identifiers': len(ids),
           'mean_targets_per_line': float(np.mean(per_line)), 'max_targets_per_line': max(per_line),
           'principal_out': out[p], 'principal_in': inn[p], 'resource_in': inn[x],
           'source_only_ids': len(ids - targets), 'twins_of_principal': _twins(p, ids), 'twins_of_resource': _twins(x, ids),
           'claim_chars': len(item['claim']), 'set_size': len(members),
           'set_out_facts': sum(out[s] for s in members),
           'statement_chars': len(report['statement']),
           'principal_line_pos': pos_p / max(1, len(text)), 'resource_first_pos': text.find(x) / max(1, len(text))}
    return row


def matrix(rows):
    """Numeric features plus one-hot strata (family, scheme, shape)."""
    families = sorted(FAMILIES)
    cols = list(FEATURES) + [f'family={f}' for f in families] + [f'scheme={s}' for s in SCHEMES] + [f'shape={s}' for s in SHAPES]
    X = np.array([[r['features'][f] for f in FEATURES] + [r['family'] == f for f in families] +
                  [r['scheme'] == s for s in SCHEMES] + [r['shape'] == s for s in SHAPES] for r in rows], dtype=float)
    return X, cols


def _auc(y, score):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, score))


def oof_scores(X, y, model, repeats=10, seed=0):
    from sklearn.base import clone
    from sklearn.model_selection import StratifiedKFold
    total = np.zeros(len(y))
    for r in range(repeats):
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed + r)
        for train, test in folds.split(X, y):
            m = clone(model).fit(X[train], y[train])
            total[test] += m.predict_proba(X[test])[:, 1]
    return total / repeats


def models():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return {'logistic': make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)),
            'random_forest': RandomForestClassifier(n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=-1)}


def audit(rows, *, positive, negative='honest', boot=2000, permutations=100, seed=20260923):
    """AUC (repeated 5-fold out-of-fold) with a bootstrap 95% CI and a label-permutation p-value."""
    chosen = [r for r in rows if r['kind'] in positive or r['kind'] == negative]
    X, cols = matrix(chosen)
    y = np.array([r['kind'] != negative for r in chosen], dtype=int)
    rng = np.random.default_rng(seed)
    result = {'n_positive': int(y.sum()), 'n_negative': int((1 - y).sum()), 'positive_kinds': sorted(positive),
              'features': cols, 'models': {}}
    for name, model in models().items():
        score = oof_scores(X, y, model)
        auc = _auc(y, score)
        boots = []
        for _ in range(boot):
            idx = rng.integers(0, len(y), len(y))
            if 0 < y[idx].sum() < len(idx):
                boots.append(_auc(y[idx], score[idx]))
        null = [_auc(yp, oof_scores(X, yp, model, repeats=1, seed=int(rng.integers(1 << 30))))
                for yp in (rng.permutation(y) for _ in range(permutations))]
        result['models'][name] = {'auc': round(auc, 4), 'ci95': [round(float(np.quantile(boots, .025)), 4),
                                                                 round(float(np.quantile(boots, .975)), 4)],
                                  'permutation_p': round((1 + sum(a >= auc for a in null)) / (1 + len(null)), 4),
                                  'null_auc_mean': round(float(np.mean(null)), 4),
                                  'null_auc_q95': round(float(np.quantile(null, .95)), 4)}
    # Univariate diagnostics: AUC of each raw feature alone (direction-free: max(a, 1 - a)).
    uni = {}
    for j, c in enumerate(cols[:len(FEATURES)]):
        a = _auc(y, X[:, j])
        uni[c] = round(max(a, 1 - a), 4)
    result['univariate_auc'] = dict(sorted(uni.items(), key=lambda kv: -kv[1]))
    return result
