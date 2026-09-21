"""Explanation-balance gate: `uv run python -m ve_experiments.e1.balance <split> [--write]`.

An explanation must not reveal the label through its STYLE. Checked on the explanation text alone, before scoring:

  B1  length in words:             |stratified SMD| < 0.20 (bad minus good)
  B2  hedging-marker count:        |stratified SMD| < 0.20; the marker list below was fixed before looking at labels
  B3  style-only classifier:       leave-one-template-out AUC within [0.40, 0.60]

Stratified SMD: strata are (template, explanation author); the numerator is the stratum-size-weighted mean of the
within-stratum differences of means, the denominator the pooled within-stratum standard deviation. Strata that lack a
label are skipped and counted. The classifier is a logistic regression (pure Python, fixed seed-free batch gradient
descent) on style features only: word count, sentence count, mean sentence length, mean word length, comma and
semicolon counts, type-token ratio, hedging count, first-person count. It never sees content words, so it measures
style, not the (legitimately different) content of explanations of different statements.

Content exclusion rule (label-blind): a hedging marker that occurs in any REQUIREMENT text of the split is dropped
for that split, because explanations echo the requirement ("different services may have different maintainers" is
permission, not doubt). Revision history, stated for the record: the first version of this check (2026-09-21) counted
"may", "unless", "as long as" etc. as hedges and gave the classifier the rates of 40 function words including
and/or/not/every/only; both measure the logical content of the statement being explained, which the judge sees
anyway. That version failed on dev and scored (hedging SMD -1.08 / -0.43, AUC 0.81 / 0.87) and was replaced by this
one; thresholds were not changed. Second revision, same day: conditional and deontic words (unless, as long as,
assuming, should, intended) were removed from the marker list because they state exceptions, not doubt; the list now
holds epistemic hedges and approximators only. `check(split)` raises BalanceError when a criterion fails; the
scored drivers call it.
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict

from .pilot import E1, load_candidates

HEDGES = ("may", "might", "could", "perhaps", "possibly", "probably", "likely", "seems", "seem", "appears", "appear",
          "arguably", "roughly", "approximately", "essentially", "generally", "typically", "usually", "somewhat",
          "in effect", "in practice", "more or less", "in most cases", "effectively", "in spirit", "broadly", "largely",
          "in essence", "sort of", "kind of", "presumably", "apparently", "supposedly", "in principle")  # fmt: skip
FIRST_PERSON = ("i", "my", "we", "our", "me")
SMD_LIMIT, AUC_LOW, AUC_HIGH = 0.20, 0.40, 0.60


class BalanceError(RuntimeError):
    pass


def words(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def hedge_count(text: str, markers=HEDGES) -> int:
    low = " " + " ".join(words(text)) + " "
    return sum(low.count(f" {h} ") for h in markers)


def usable_markers(rows: list[dict]) -> tuple[str, ...]:
    reqs = " " + " | ".join(" ".join(words(r["requirement"])) for r in rows) + " "
    return tuple(h for h in HEDGES if f" {h} " not in reqs)


def features(text: str, markers=HEDGES) -> list[float]:
    w = words(text)
    n = max(len(w), 1)
    sents = max(len(re.findall(r"[.!?]+", text)), 1)
    return [len(w) / 60, sents / 4, len(w) / sents / 20, sum(map(len, w)) / n / 5, text.count(",") / 5, float(text.count(";")),
            len(set(w)) / n, float(hedge_count(text, markers)), float(sum(w.count(f) for f in FIRST_PERSON))]  # fmt: skip


def stratified_smd(rows: list[dict], value) -> dict:
    strata = defaultdict(lambda: {"good": [], "bad": []})
    for r in rows:
        strata[(r["template"], r.get("explanation_author"))][r["label"]].append(value(r["explanation"]))
    num = den_w = ss = df = 0.0
    skipped = 0
    for s in strata.values():
        g, b = s["good"], s["bad"]
        if len(g) < 2 or len(b) < 2:
            skipped += 1
            continue
        mg, mb = sum(g) / len(g), sum(b) / len(b)
        w = len(g) + len(b)
        num, den_w = num + w * (mb - mg), den_w + w
        ss += sum((x - mg) ** 2 for x in g) + sum((x - mb) ** 2 for x in b)
        df += len(g) + len(b) - 2
    sd = math.sqrt(ss / df) if df and ss > 0 else 0.0
    diff = num / den_w if den_w else 0.0
    mean = {lab: sum(value(r["explanation"]) for r in rows if r["label"] == lab) / max(1, sum(r["label"] == lab for r in rows)) for lab in ("good", "bad")}
    return {"smd": diff / sd if sd else 0.0, "diff": diff, "sd": sd, "mean_good": mean["good"], "mean_bad": mean["bad"],
            "strata": len(strata), "strata_skipped": skipped}  # fmt: skip


def _fit(xs: list[list[float]], ys: list[int], steps: int = 300, lr: float = 0.5, l2: float = 0.01) -> list[float]:
    k = len(xs[0])
    w = [0.0] * (k + 1)
    for _ in range(steps):
        grad = [0.0] * (k + 1)
        for x, y in zip(xs, ys):
            z = w[0] + sum(a * b for a, b in zip(w[1:], x))
            e = 1 / (1 + math.exp(-max(-30.0, min(30.0, z)))) - y
            grad[0] += e
            for i, a in enumerate(x):
                grad[i + 1] += e * a
        w = [wi - lr * (g / len(xs) + (l2 * wi if i else 0.0)) for i, (wi, g) in enumerate(zip(w, grad))]
    return w


def auc(scores: list[float], ys: list[int]) -> float:
    pos, neg = [s for s, y in zip(scores, ys) if y], [s for s, y in zip(scores, ys) if not y]
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def loto_auc(rows: list[dict], markers=HEDGES) -> float:
    """Leave one template out: train on the others, score the held-out explanations; AUC over all held-out scores."""
    feats = [features(r["explanation"], markers) for r in rows]
    k = len(feats[0])
    ys = [int(r["label"] == "bad") for r in rows]
    scores = [0.0] * len(rows)
    for t in sorted({r["template"] for r in rows}):
        tr = [i for i, r in enumerate(rows) if r["template"] != t]
        mu = [sum(feats[i][j] for i in tr) / len(tr) for j in range(k)]
        sd = [math.sqrt(sum((feats[i][j] - mu[j]) ** 2 for i in tr) / len(tr)) or 1.0 for j in range(k)]
        z = lambda f: [(f[j] - mu[j]) / sd[j] for j in range(k)]  # noqa: E731
        w = _fit([z(feats[i]) for i in tr], [ys[i] for i in tr])
        for i, r in enumerate(rows):
            if r["template"] == t:
                scores[i] = w[0] + sum(a * b for a, b in zip(w[1:], z(feats[i])))
    return auc(scores, ys)


def measure(split: str, name: str | None = None) -> dict:
    rows = [c for c in load_candidates(name=name or split) if c["split"] == split and c.get("explanation")]
    markers = usable_markers(rows)
    out = {"split": split, "hedging_markers_dropped_as_requirement_words": sorted(set(HEDGES) - set(markers)), "n_good": sum(r["label"] == "good" for r in rows), "n_bad": sum(r["label"] == "bad" for r in rows),
           "authors": sorted({r.get("explanation_author") for r in rows}),
           "length": stratified_smd(rows, lambda t: len(t.split())), "hedging": stratified_smd(rows, lambda t: hedge_count(t, markers)),
           "loto_style_auc": loto_auc(rows, markers)}  # fmt: skip
    out["pass"] = {"B1_length": abs(out["length"]["smd"]) < SMD_LIMIT, "B2_hedging": abs(out["hedging"]["smd"]) < SMD_LIMIT,
                   "B3_style_classifier": AUC_LOW <= out["loto_style_auc"] <= AUC_HIGH}  # fmt: skip
    return out


def check(split: str) -> dict:
    m = measure(split)
    failed = [k for k, ok in m["pass"].items() if not ok]
    if failed:
        raise BalanceError(f"explanation balance failed on {split}: {failed}; regenerate or length-match before scoring")
    return m


def main() -> None:
    m = measure(sys.argv[1])
    text = json.dumps(m, indent=1)
    if "--write" in sys.argv:
        (E1 / f"BALANCE-{sys.argv[1]}.json").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
