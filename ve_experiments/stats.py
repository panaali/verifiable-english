"""Metrics and paired bootstrap for approve/reject experiments. Standard library only.

Input rows are the dicts written by runner.run (`trials.jsonl`): at least
`group`, `label` ("good"|"bad"), `condition`, `judge`, `approved` (True | False | None).

Failures stay in the denominator. A trial with `approved is None` (failed call, timeout, or
unparseable verdict) is scored as the WORST case for its label: approved if the item is bad,
rejected if the item is good. `failure_rate` is reported next to every metric so that a reader can
see how much of a number comes from this rule.

    false approval    = approved bad  / assigned bad
    honest acceptance = approved good / assigned good

The bootstrap resamples CLUSTERS with replacement, keeping all of a cluster's trials together
across conditions and samples. `cluster` names the row field that identifies the independent unit:
"group" (base item) by default; experiments whose items are variants of a few semantic templates
must pass the template field, since variants of one template are not independent. This is what
makes the contrast paired. Judges are a fixed factor and are never pooled in a primary result:
`summarize` reports each judge separately, and a pooled row only on request, labelled exploratory.

No p-value is reported. An earlier exact sign test over trial cells treated dependent variants as
independent (ten variants of one template gave p = 0.002 with one cluster); the cluster bootstrap
interval is the only inferential statement. Discordant counts are given as descriptive numbers.
"""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass

METRICS = {"false_approval": "bad", "honest_acceptance": "good"}


def worst_case_approved(row: dict) -> bool:
    if row["approved"] is None:
        return row["label"] == "bad"
    return bool(row["approved"])


@dataclass(frozen=True)
class Rate:
    metric: str
    condition: str
    judge: str  # "*" = pooled over judges
    value: float | None
    numerator: int
    denominator: int
    failure_rate: float | None
    ci_low: float | None = None
    ci_high: float | None = None


@dataclass(frozen=True)
class Contrast:
    metric: str
    a: str
    b: str
    judge: str
    diff: float | None  # rate(a) - rate(b)
    ci_low: float | None
    ci_high: float | None
    n_clusters: int
    n_boot: int
    discordant_a_only: int  # paired cells approved under a and not under b (descriptive only)
    discordant_b_only: int


def _select(rows: Iterable[dict], metric: str, condition: str | None = None, judge: str | None = None) -> list[dict]:
    label = METRICS[metric]
    return [
        r
        for r in rows
        if r["label"] == label
        and (condition is None or r["condition"] == condition)
        and (judge in (None, "*") or r["judge"] == judge)
    ]


def rate(rows: Sequence[dict], metric: str, condition: str, judge: str = "*") -> Rate:
    sel = _select(rows, metric, condition, judge)
    num = sum(worst_case_approved(r) for r in sel)
    fails = sum(r["approved"] is None for r in sel)
    n = len(sel)
    return Rate(metric, condition, judge, num / n if n else None, num, n, fails / n if n else None)


def _group_counts(rows: Sequence[dict], cluster: str = "group") -> dict[str, tuple[int, int]]:
    """cluster -> (approved, total) under the worst-case rule."""
    acc: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        acc[r[cluster]][0] += worst_case_approved(r)
        acc[r[cluster]][1] += 1
    return {g: (a, n) for g, (a, n) in acc.items()}


def _ratio(groups: Sequence[str], counts: dict[str, tuple[int, int]]) -> float | None:
    num = den = 0
    for g in groups:
        a, n = counts.get(g, (0, 0))
        num += a
        den += n
    return num / den if den else None


def _percentile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        raise ValueError("no values")
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def bootstrap_rate(
    rows: Sequence[dict], metric: str, condition: str, judge: str = "*", n_boot: int = 10_000, seed: int = 0,
    alpha: float = 0.05, cluster: str = "group",
) -> Rate:  # fmt: skip
    base = rate(rows, metric, condition, judge)
    counts = _group_counts(_select(rows, metric, condition, judge), cluster)
    groups = sorted(counts)
    if not groups:
        return base
    rng = random.Random(f"{seed}:{metric}:{condition}:{judge}")
    vals = sorted(v for _ in range(n_boot) if (v := _ratio(rng.choices(groups, k=len(groups)), counts)) is not None)
    return Rate(**{**asdict(base), "ci_low": _percentile(vals, alpha / 2), "ci_high": _percentile(vals, 1 - alpha / 2)})


def paired_contrast(
    rows: Sequence[dict], metric: str, a: str, b: str, judge: str = "*", n_boot: int = 10_000, seed: int = 0,
    alpha: float = 0.05, cluster: str = "group",
) -> Contrast:  # fmt: skip
    """rate(a) - rate(b) with a percentile bootstrap over groups.

    Only groups that have trials in BOTH conditions enter the contrast, so that a and b are compared
    on the same items. With crossed assignment that is every group.
    """
    if judge != "*":
        _require_paired(rows, metric, a, b, judge)
    ca = _group_counts(_select(rows, metric, a, judge), cluster)
    cb = _group_counts(_select(rows, metric, b, judge), cluster)
    groups = sorted(set(ca) & set(cb))
    if not groups:
        return Contrast(metric, a, b, judge, None, None, None, 0, n_boot, 0, 0)
    diff = _ratio(groups, ca) - _ratio(groups, cb)  # type: ignore[operator]
    rng = random.Random(f"{seed}:{metric}:{a}:{b}:{judge}")
    diffs = []
    for _ in range(n_boot):
        sample = rng.choices(groups, k=len(groups))
        diffs.append(_ratio(sample, ca) - _ratio(sample, cb))  # type: ignore[operator]
    diffs.sort()

    # descriptive discordant counts on paired cells (same item, judge, seed)
    def cells(cond: str) -> dict[tuple, bool]:
        return {(r["item_id"], r["judge"], r.get("seed", 0)): worst_case_approved(r) for r in _select(rows, metric, cond, judge)}

    xa, xb = cells(a), cells(b)
    shared = set(xa) & set(xb)
    a_only = sum(xa[k] and not xb[k] for k in shared)
    b_only = sum(xb[k] and not xa[k] for k in shared)
    return Contrast(
        metric, a, b, judge, diff, _percentile(diffs, alpha / 2), _percentile(diffs, 1 - alpha / 2),
        len(groups), n_boot, a_only, b_only,
    )  # fmt: skip


class PairingError(ValueError):
    pass


def _require_paired(rows: Sequence[dict], metric: str, a: str, b: str, judge: str) -> None:
    """A paired contrast is only defined when both cells hold exactly the same (item, sample) trials."""
    ka = sorted((r["item_id"], r.get("sample", 0)) for r in _select(rows, metric, a, judge))
    kb = sorted((r["item_id"], r.get("sample", 0)) for r in _select(rows, metric, b, judge))
    if ka != kb or len(set(ka)) != len(ka):
        raise PairingError(f"{judge}: cells {a!r} and {b!r} do not contain the same trials "
                           f"({len(ka)} vs {len(kb)}, {len(set(ka) ^ set(kb))} unmatched)")  # fmt: skip


T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
        21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}  # fmt: skip


@dataclass(frozen=True)
class ClusterT:
    metric: str
    a: str
    b: str
    judge: str
    diff: float  # unweighted mean over clusters of (rate in a - rate in b) within the cluster
    ci_low: float
    ci_high: float
    sd: float  # between-cluster standard deviation of the per-cluster differences
    n_clusters: int
    per_cluster: dict


def cluster_t_contrast(rows: Sequence[dict], metric: str, a: str, b: str, judge: str, cluster: str = "template") -> ClusterT:
    """The per-cluster differences d_c = rate_a(c) - rate_b(c) are the data; the estimate is their mean, the 95%
    interval is mean +/- t(0.975, G-1) * sd / sqrt(G). Clusters weigh equally whatever their number of items.
    Requires complete pairing and at least two clusters (at most 31)."""
    _require_paired(rows, metric, a, b, judge)
    ca = _group_counts(_select(rows, metric, a, judge), cluster)
    cb = _group_counts(_select(rows, metric, b, judge), cluster)
    d = {c: ca[c][0] / ca[c][1] - cb[c][0] / cb[c][1] for c in sorted(ca)}
    g = len(d)
    if g < 2 or g - 1 not in T975:
        raise ValueError(f"cluster-t needs between 2 and 31 clusters, got {g}")
    mean = sum(d.values()) / g
    sd = (sum((x - mean) ** 2 for x in d.values()) / (g - 1)) ** 0.5
    half = T975[g - 1] * sd / g**0.5
    return ClusterT(metric, a, b, judge, mean, mean - half, mean + half, sd, g, d)


def summarize(
    rows: Sequence[dict], contrasts: Sequence[tuple[str, str]] = (), n_boot: int = 10_000, seed: int = 0,
    cluster: str = "group", pooled: bool = False,
) -> dict:  # fmt: skip
    """All rates and the requested contrasts per judge. `pooled=True` adds a "*" row across judges,
    which is exploratory: judges differ in family and in CLI context and are not exchangeable."""
    conditions = sorted({r["condition"] for r in rows})
    judges = [*(["*"] if pooled else []), *sorted({r["judge"] for r in rows})]
    out: dict = {"n_rows": len(rows), "rates": [], "contrasts": []}
    for metric in METRICS:
        for j in judges:
            for c in conditions:
                out["rates"].append(asdict(bootstrap_rate(rows, metric, c, j, n_boot, seed, cluster=cluster)))
            for a, b in contrasts:
                out["contrasts"].append(asdict(paired_contrast(rows, metric, a, b, j, n_boot, seed, cluster=cluster)))
    return out


def to_markdown(summary: dict) -> str:
    def f(x: float | None) -> str:
        return "n/a" if x is None else f"{x:.3f}"

    lines = ["| metric | judge | condition | rate | 95% CI | k/n | failures |", "|---|---|---|---|---|---|---|"]
    for r in summary["rates"]:
        lines.append(
            f"| {r['metric']} | {r['judge']} | {r['condition']} | {f(r['value'])} | "
            f"[{f(r['ci_low'])}, {f(r['ci_high'])}] | {r['numerator']}/{r['denominator']} | {f(r['failure_rate'])} |"
        )
    if summary["contrasts"]:
        lines += ["", "| metric | judge | a - b | diff | 95% CI | clusters | a-only/b-only |", "|---|---|---|---|---|---|---|"]
        for c in summary["contrasts"]:
            lines.append(
                f"| {c['metric']} | {c['judge']} | {c['a']} - {c['b']} | {f(c['diff'])} | "
                f"[{f(c['ci_low'])}, {f(c['ci_high'])}] | {c['n_clusters']} | "
                f"{c['discordant_a_only']}/{c['discordant_b_only']} |"
            )
    return "\n".join(lines) + "\n"
