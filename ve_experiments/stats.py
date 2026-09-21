"""Metrics and paired bootstrap for approve/reject experiments. Standard library only.

Input rows are the dicts written by runner.run (`trials.jsonl`): at least
`group`, `label` ("good"|"bad"), `condition`, `judge`, `approved` (True | False | None).

Failures stay in the denominator. A trial with `approved is None` (failed call, timeout, or
unparseable verdict) is scored as the WORST case for its label: approved if the item is bad,
rejected if the item is good. `failure_rate` is reported next to every metric so that a reader can
see how much of a number comes from this rule.

    false approval    = approved bad  / assigned bad
    honest acceptance = approved good / assigned good

The bootstrap resamples `group`s (base items) with replacement, keeping all of a group's trials
together across conditions, judges, and samples. This is what makes the contrast paired, and it
treats the item, not the model call, as the unit of replication. Judges are a fixed factor: with
two to four judges there is nothing to resample, so conclusions hold for these judges only.
"""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from math import comb

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
    n_groups: int
    n_boot: int
    discordant_a_only: int  # paired cells approved under a and not under b
    discordant_b_only: int
    sign_test_p: float | None  # exact two-sided McNemar/sign test on discordant cells


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


def _group_counts(rows: Sequence[dict]) -> dict[str, tuple[int, int]]:
    """group -> (approved, total) under the worst-case rule."""
    acc: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        acc[r["group"]][0] += worst_case_approved(r)
        acc[r["group"]][1] += 1
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
    rows: Sequence[dict], metric: str, condition: str, judge: str = "*", n_boot: int = 10_000, seed: int = 0, alpha: float = 0.05
) -> Rate:
    base = rate(rows, metric, condition, judge)
    counts = _group_counts(_select(rows, metric, condition, judge))
    groups = sorted(counts)
    if not groups:
        return base
    rng = random.Random(f"{seed}:{metric}:{condition}:{judge}")
    vals = sorted(v for _ in range(n_boot) if (v := _ratio(rng.choices(groups, k=len(groups)), counts)) is not None)
    return Rate(**{**asdict(base), "ci_low": _percentile(vals, alpha / 2), "ci_high": _percentile(vals, 1 - alpha / 2)})


def paired_contrast(
    rows: Sequence[dict], metric: str, a: str, b: str, judge: str = "*", n_boot: int = 10_000, seed: int = 0, alpha: float = 0.05
) -> Contrast:
    """rate(a) - rate(b) with a percentile bootstrap over groups.

    Only groups that have trials in BOTH conditions enter the contrast, so that a and b are compared
    on the same items. With crossed assignment that is every group.
    """
    ca = _group_counts(_select(rows, metric, a, judge))
    cb = _group_counts(_select(rows, metric, b, judge))
    groups = sorted(set(ca) & set(cb))
    if not groups:
        return Contrast(metric, a, b, judge, None, None, None, 0, n_boot, 0, 0, None)
    diff = _ratio(groups, ca) - _ratio(groups, cb)  # type: ignore[operator]
    rng = random.Random(f"{seed}:{metric}:{a}:{b}:{judge}")
    diffs = []
    for _ in range(n_boot):
        sample = rng.choices(groups, k=len(groups))
        diffs.append(_ratio(sample, ca) - _ratio(sample, cb))  # type: ignore[operator]
    diffs.sort()

    # exact sign test on paired cells (same item, judge, seed)
    def cells(cond: str) -> dict[tuple, bool]:
        return {(r["item_id"], r["judge"], r.get("seed", 0)): worst_case_approved(r) for r in _select(rows, metric, cond, judge)}

    xa, xb = cells(a), cells(b)
    shared = set(xa) & set(xb)
    a_only = sum(xa[k] and not xb[k] for k in shared)
    b_only = sum(xb[k] and not xa[k] for k in shared)
    return Contrast(
        metric, a, b, judge, diff, _percentile(diffs, alpha / 2), _percentile(diffs, 1 - alpha / 2),
        len(groups), n_boot, a_only, b_only, sign_test_p(a_only, b_only),
    )  # fmt: skip


def sign_test_p(k1: int, k2: int) -> float | None:
    """Two-sided exact binomial test that discordant pairs split 50/50. Treats cells as independent,
    which is optimistic when one group contributes many cells; the bootstrap CI is primary."""
    n = k1 + k2
    if n == 0:
        return None
    tail = sum(comb(n, i) for i in range(0, min(k1, k2) + 1)) / 2**n
    return min(1.0, 2 * tail)


def summarize(
    rows: Sequence[dict], contrasts: Sequence[tuple[str, str]] = (), n_boot: int = 10_000, seed: int = 0
) -> dict:
    """All rates and the requested contrasts, pooled ("*") and per judge."""
    conditions = sorted({r["condition"] for r in rows})
    judges = ["*", *sorted({r["judge"] for r in rows})]
    out: dict = {"n_rows": len(rows), "rates": [], "contrasts": []}
    for metric in METRICS:
        for j in judges:
            for c in conditions:
                out["rates"].append(asdict(bootstrap_rate(rows, metric, c, j, n_boot, seed)))
            for a, b in contrasts:
                out["contrasts"].append(asdict(paired_contrast(rows, metric, a, b, j, n_boot, seed)))
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
        lines += ["", "| metric | judge | a - b | diff | 95% CI | groups | a-only/b-only | sign p |", "|---|---|---|---|---|---|---|---|"]
        for c in summary["contrasts"]:
            lines.append(
                f"| {c['metric']} | {c['judge']} | {c['a']} - {c['b']} | {f(c['diff'])} | "
                f"[{f(c['ci_low'])}, {f(c['ci_high'])}] | {c['n_groups']} | "
                f"{c['discordant_a_only']}/{c['discordant_b_only']} | {f(c['sign_test_p'])} |"
            )
    return "\n".join(lines) + "\n"
