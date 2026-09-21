"""Offline dev-trained feature probes across every E5 cell and difficulty.

No model calls; labels are used only outside prompts. This probes superficial
prediction, NOT general absence of semantic or adversarial information leakage.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from .materials import HERE, CELLS, INSTRUCTIONS, DIFFICULTIES, render_cell, packed, parse_memo


def tokens(text):
    return Counter(re.findall(r"\w+|[^\w\s]", text.lower()))


def feature_bound(examples, feature):
    groups = defaultdict(Counter)
    for text, label in examples:
        groups[feature(text)][label] += 1
    return sum(max(c.values()) for c in groups.values()) / len(examples)


def load_rows(split):
    with gzip.open(HERE / f"{split}.jsonl.gz", "rt") as f:
        return [r for line in f if (r := json.loads(line))["payload"]["_audit"]["stratum"] == "primary"]


def dossier_features(text):
    """Equality/duplication graph from PROMPT text, without resolving selectors.

    Retain IDs, displayed ordinals, citation incidence and the entire equivalence
    relation (not just duplicate counts). Compare both ordered and unordered
    profiles, and also near-duplicates with profile names erased. No content
    values, labels, construction data, tags or selector resolutions are features.
    """
    prefix, body = text.split("Evidence records:\n", 1)
    body = body.split("\nBadge:", 1)[0].strip()
    citations = [set(re.findall(r"\br\d+\b", line.split("Cites:", 1)[1]))
                 for line in prefix.splitlines() if "Cites:" in line]
    records = ([parse_memo(chunk) for chunk in re.split(r"\n(?=Memo r\d+\.)", body)]
               if body.startswith("Memo ") else [json.loads(line) for line in body.splitlines()])
    nodes, keys = [], {kind: [] for kind in ("ordered", "unordered", "names_erased")}
    for ordinal, record in enumerate(records):
        if "profiles" not in record:
            continue
        nodes.append((record["record_id"], ordinal,
                      tuple(record["record_id"] in ids for ids in citations)))
        profiles = record["profiles"]
        keys["ordered"].append(packed(profiles))
        keys["unordered"].append(packed(sorted(packed(p) for p in profiles)))
        keys["names_erased"].append(packed(sorted(packed({k: v for k, v in p.items() if k != "profile"})
                                                for p in profiles)))
    partitions = {}
    for kind, values in keys.items():
        first = {}
        partitions[kind] = [first.setdefault(value, i) for i, value in enumerate(values)]
    cited = [any(node[2]) for node in nodes]
    exact = keys["unordered"]
    unmatched = any(not is_cited and not any(other == value and cited[j] for j, other in enumerate(exact))
                    for value, is_cited in zip(exact, cited))
    return {"uncited_unmatched": unmatched,
            "signature": packed({"nodes": nodes, "equality_partitions": partitions})}


def structural_report(rows, texts):
    features = [dossier_features(text) for text in texts]
    result = {}
    for difficulty in DIFFICULTIES:
        selected = [(row, feature) for row, feature in zip(rows, features)
                    if row["payload"]["_audit"]["difficulty"] == difficulty]
        pairs = defaultdict(list)
        for row, feature in selected:
            pairs[row["payload"]["_audit"]["pair"]].append(feature["signature"])
        correct = sum(feature["uncited_unmatched"] == (row["label"] == "bad") for row, feature in selected)
        result[difficulty] = {"n": len(selected), "uncited_unmatched_correct": correct,
            "uncited_unmatched_accuracy": correct / len(selected),
            "any_equality_rule_empirical_bound": feature_bound(
                [(feature["signature"], row["label"]) for row, feature in selected], lambda x: x),
            "pairs": len(pairs),
            "identical_pair_structures": sum(len(pair) == 2 and pair[0] == pair[1] for pair in pairs.values())}
    return result


def numeric_features(text):
    # All inputs come from the PROMPT. No hidden bad_at/leaf index or label.
    markers = ("security assurance", "operational readiness", "savelo", "torami", "2031-03-",
               "2031-04-19", "talven", "velora")
    features = [len(text), len(text.split()), len(text.splitlines()), text.count("Cites:"),
                len(re.findall(r'"record_id"|Memo r\d+', text)),
                len(set(re.findall(r"\br\d{3}\b", text))), len(re.findall(r"\d{4}-\d{2}-\d{2}", text))]
    for marker in markers:
        positions = [m.start() / len(text) for m in re.finditer(re.escape(marker), text)]
        features += [len(positions), min(positions, default=-1), max(positions, default=-1),
                     sum(positions)/len(positions) if positions else -1]
    # Per displayed record ordinal: position, length, citations, date/marker counts.
    # Fixed 40 slots covers frozen maximum 6 leaves*4 + 8 distractors.
    records = text.split("Evidence records:\n", 1)[1].split("\nBadge:", 1)[0]
    chunks = re.split(r'(?=\{"kind":|Memo r\d+\.)', records)
    chunks = [c for c in chunks if c.strip()]
    for i in range(40):
        chunk = chunks[i] if i < len(chunks) else ""
        ids = re.findall(r'"record_id":"(r\d+)"|Memo (r\d+)', chunk)
        rid = next((a or b for a, b in ids), "")
        cited = sum(rid in line for line in text.splitlines() if "Cites:" in line) if rid else 0
        features += [len(chunk), cited, *(chunk.count(m) for m in markers)]
    return features


def audit():
    rows = {s: load_rows(s) for s in ("dev", "scored")}
    report = {"input_sha256": {s: hashlib.sha256((HERE / f"{s}.jsonl.gz").read_bytes()).hexdigest() for s in rows}, "renderer_sha256": hashlib.sha256((HERE / "materials.py").read_bytes()).hexdigest(), "audit_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "seed": 5301, "training_split": "dev", "evaluation_split": "scored", "model_calls": 0,
        "scope": "primary, balanced overall approval labels only; controls excluded and counted separately",
        "instruction_styles": list(INSTRUCTIONS),
        "preprocessing": "Drop only the randomized instruction-style first line, whose text is constant within style. Assert all remaining bytes identical across styles. Full record bodies, panels and dates are retained.",
        "classifier": "L2 logistic regression C=1, liblinear, max_iter=1000; numeric inputs standardized on dev; text L2-normalized hashed counts, 2^17 features, no alternate signs",
        "feature_sets": {"char_1_5": [1, 5], "char_6_12": [6, 12], "word_1_3": [1, 3],
                         "counts_positions_dates_lengths": "record/citation counts; date counts; anomaly-marker absolute ordinal/relative positions and record lengths"},
        "interpretation": "Held-out predictive accuracy, not an upper bound for these feature classes. Chance .50. Results >.60 trigger review before model scoring, not removal of inconvenient families.",
        "structural_probes": "Uncited dossier matches no cited dossier => BAD; plus empirical majority-label bound for ANY function of the complete dossier-equality signature, including IDs/positions/citation incidence, ordered/unordered profiles and name-erased near-duplicates. This bound applies only to these features on this finite inventory, not arbitrary semantic classifiers or future items.",
        "cells": {}}
    for cell in CELLS:
        texts, labels = {}, {}
        for split, items in rows.items():
            texts[split] = []
            for row in items:
                variants = [render_cell(row, cell, style).split("\n", 1)[1] for style in INSTRUCTIONS]
                assert variants[0] == variants[1]
                assert all(flag not in variants[0] for flag in ("scope_matches_target", "binding_mismatch", "differing_evidence_senses"))
                texts[split].append(variants[0])
            labels[split] = np.array([r["label"] == "bad" for r in items])
        result = {"train_n": len(rows["dev"]), "test_n": len(rows["scored"]), "scored_accuracy": {},
                  "by_difficulty": {d: {} for d in DIFFICULTIES},
                  "by_family": {f: {} for f in ("merged_vocabulary", "scope_mismatch", "unsupported_leaf", "stale_evidence")},
                  "by_grounding_variant": {v: {} for v in ("profile", "authorization_chain")},
                  "merged_tag_condition": {tag: {} for tag in ("honest", "forged")}, "pair_balance": {}}
        result["dossier_structure"] = {split: structural_report(rows[split], texts[split]) for split in rows}
        for name, analyzer, sizes in (("char_1_5", "char", (1, 5)), ("char_6_12", "char", (6, 12)), ("word_1_3", "word", (1, 3)),
                                      ("counts_positions_dates_lengths", None, None)):
            if analyzer:
                vectorizer = HashingVectorizer(analyzer=analyzer, ngram_range=sizes, n_features=2**17,
                                              alternate_sign=False, norm="l2", lowercase=True)
                xdev = vectorizer.transform(texts["dev"])
                xscore = vectorizer.transform(texts["scored"])
            else:
                scaler = StandardScaler()
                xdev = scaler.fit_transform([numeric_features(t) for t in texts["dev"]])
                xscore = scaler.transform([numeric_features(t) for t in texts["scored"]])
            classifier = LogisticRegression(C=1, solver="liblinear", random_state=5301, max_iter=1000)
            classifier.fit(xdev, labels["dev"])
            prediction = classifier.predict(xscore)
            result["scored_accuracy"][name] = float(np.mean(prediction == labels["scored"]))
            for difficulty in DIFFICULTIES:
                mask = np.array([r["payload"]["_audit"]["difficulty"] == difficulty for r in rows["scored"]])
                result["by_difficulty"][difficulty][name] = float(np.mean(prediction[mask] == labels["scored"][mask]))
            for family in result["by_family"]:
                mask = np.array([r["payload"]["_audit"]["family"] == family for r in rows["scored"]])
                result["by_family"][family][name] = float(np.mean(prediction[mask] == labels["scored"][mask]))
            for variant in result["by_grounding_variant"]:
                mask = np.array([r["payload"]["_audit"]["grounding_variant"] == variant for r in rows["scored"]])
                result["by_grounding_variant"][variant][name] = float(np.mean(prediction[mask] == labels["scored"][mask]))
            for tag in ("honest", "forged"):
                mask = np.array([r["payload"]["_audit"]["family"] == "merged_vocabulary" and r["payload"]["_audit"]["tag_condition"] == tag for r in rows["scored"]])
                result["merged_tag_condition"][tag][name] = float(np.mean(prediction[mask] == labels["scored"][mask]))
            del xdev, xscore
        for split, items in rows.items():
            pairs = defaultdict(list)
            for row, text in zip(items, texts[split]):
                pairs[row["payload"]["_audit"]["pair"]].append((row, text))
            metrics = Counter()
            for pair in pairs.values():
                assert len(pair) == 2
                (a, ta), (b, tb) = pair
                metrics["pairs"] += 1
                metrics["equal_character_length"] += len(ta) == len(tb)
                metrics["equal_unigram_multiset"] += tokens(ta) == tokens(tb)
                metrics["equal_record_count"] += len(a["payload"]["records"]) == len(b["payload"]["records"])
                metrics["equal_citation_positions"] += [l["evidence_ids"] for l in a["payload"]["leaves"]] == [l["evidence_ids"] for l in b["payload"]["leaves"]]
                metrics["equal_date_multiset"] += Counter(re.findall(r"\d{4}-\d{2}-\d{2}", ta)) == Counter(re.findall(r"\d{4}-\d{2}-\d{2}", tb))
            result["pair_balance"][split] = dict(metrics)
        report["cells"][cell] = result
        print(cell, result["scored_accuracy"], flush=True)
    return report


if __name__ == "__main__":
    result = audit()
    (HERE / "leak-report.json").write_text(json.dumps(result, indent=2) + "\n")
