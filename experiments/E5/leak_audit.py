"""Frozen lexical leak audit, not a semantic ground-truth classifier.

Fits unigram logistic regression on dev and evaluates scored. Also computes the
maximum possible accuracy for ANY deterministic function of the unigram vector,
and for length/keyword features. Pairwise feature collisions give a stronger
bound than one fitted baseline. Citation-aware semantic matching is deliberately
not a lexical heuristic: it is the task being measured.
"""
from collections import Counter, defaultdict
import json
import math
import re

from .materials import HERE, build_items, render_cell


def tokens(text):
    return Counter(re.findall(r"\w+|[^\w\s]", text.lower()))


def feature_bound(examples, feature):
    groups = defaultdict(Counter)
    for text, label in examples:
        groups[feature(text)][label] += 1
    return sum(max(c.values()) for c in groups.values()) / len(examples)


def audit():
    datasets = {}
    for split in ("dev", "scored"):
        rows = [r for r in build_items(split) if r["payload"]["_audit"]["stratum"] == "primary"]
        datasets[split] = [(render_cell(r, "a"), int(r["label"] == "bad")) for r in rows]
    vocabulary = sorted({t for text, _ in datasets["dev"] for t in tokens(text)})
    # Sparse normalized counts, no external machine-learning dependency.
    vocab = set(vocabulary)
    vectors = {}
    for split, examples in datasets.items():
        vectors[split] = []
        for text, y in examples:
            counts = {t: n for t, n in tokens(text).items() if t in vocab}
            norm = math.sqrt(sum(n*n for n in counts.values()))
            vectors[split].append(({t: n/norm for t, n in counts.items()}, y))
    weights = dict.fromkeys(vocabulary, 0.0)
    bias = 0.0
    for _ in range(100):
        gradient = dict.fromkeys(vocabulary, 0.0)
        intercept = 0.0
        for x, y in vectors["dev"]:
            z = max(-30, min(30, bias + sum(weights[t] * n for t, n in x.items())))
            error = 1 / (1 + math.exp(-z)) - y
            intercept += error
            for t, n in x.items():
                gradient[t] += error * n
        n = len(vectors["dev"])
        bias -= intercept / n
        for t in weights:
            weights[t] -= gradient[t] / n + 0.01 * weights[t]
    report = {"training_split": "dev", "evaluation_split": "scored", "threshold": 0.60,
              "scope": "valid-deduction primary stratum; overall approval label", "splits": {}}
    keywords = ("security", "operational", "stale", "unsupported", "good", "bad", "checked", "not", "2031")
    for split, examples in datasets.items():
        accuracy = sum((bias + sum(weights[t]*n for t, n in x.items()) >= 0) == bool(y)
                       for x, y in vectors[split]) / len(examples)
        report["splits"][split] = {
            "n": len(examples), "bow_logistic_accuracy": accuracy,
            "any_unigram_classifier_upper_bound": feature_bound(examples, lambda t: tuple(sorted(tokens(t).items()))),
            "length_keyword_classifier_upper_bound": feature_bound(examples,
                lambda t: (len(t), len(t.split()), *(tokens(t)[w] for w in keywords))),
        }
    return report


if __name__ == "__main__":
    result = audit()
    (HERE / "leak-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
