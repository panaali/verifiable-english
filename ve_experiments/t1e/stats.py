"""T1e analysis statistics (declared in PREREG-T1e.md) and an offline power simulation.

* exact McNemar: two-sided binomial test on the discordant pairs (unit = item);
* Newcombe (1998, method 10) hybrid-score interval for a paired difference of proportions,
  used for the gain in false approval (refutation: upper bound < 10pp) and for honest-completion
  non-inferiority (NI holds if the lower bound of HC_ve - HC_script > -10pp);
* Holm over the co-primary family.
Standard library + scipy.
"""
from __future__ import annotations

import math
import random

from scipy.stats import binom


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value; b = pairs (A yes, B no), c = pairs (A no, B yes)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * binom.cdf(k, n, .5))


def wilson(x, n, z=1.959963984540054):
    if n == 0:
        return 0.0, 1.0
    p = x / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centre - half, centre + half


def newcombe_paired(a, b, c, d, z=1.959963984540054):
    """CI for p1 - p2 with paired counts: a = both yes, b = 1 yes 2 no, c = 1 no 2 yes, d = both no."""
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    denom = math.sqrt(max(0.0, (a + b) * (c + d) * (a + c) * (b + d)))
    num = a * d - b * c
    if denom == 0:
        phi = 0.0
    else:
        adj = num - n / 2 if num > n / 2 else (0.0 if num >= 0 else num)
        phi = adj / denom
    diff = p1 - p2
    dl = math.sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    du = math.sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return diff - dl, diff + du


def holm(pvalues):
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adj, running = [0.0] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adj[i] = running
    return adj


def _pairs(rng, n, p_hi, p_lo, nested):
    """Paired binaries (arm hi, arm lo) with marginals p_hi >= p_lo; nested: lo implies hi."""
    a = b = c = d = 0
    for _ in range(n):
        if nested:
            u = rng.random()
            x, y = u < p_hi, u < p_lo
        else:
            x, y = rng.random() < p_hi, rng.random() < p_lo
        if x and y:
            a += 1
        elif x:
            b += 1
        elif y:
            c += 1
        else:
            d += 1
    return a, b, c, d


def power(n_sab=60, n_hon=60, sims=2000, alpha=.025, seed=0):
    """Power of the FA McNemar test (two-sided, at the worst-case Holm level alpha) and of the HC
    NI test (lower Newcombe bound > -0.10) under independent and nested pairings."""
    rng = random.Random(seed)
    rows = []
    for p_script in (.3, .5):
        for gain in (.10, .15, .20, .25):
            p_ve = p_script - gain
            for nested in (False, True):
                hits = refuted = 0
                for _ in range(sims):
                    a, b, c, d = _pairs(rng, n_sab, p_script, p_ve, nested)
                    if mcnemar_exact(b, c) < alpha and b > c:
                        hits += 1
                    lo, hi = newcombe_paired(a, b, c, d)
                    refuted += hi < .10
                rows.append({'fa_script': p_script, 'fa_ve': round(p_ve, 2), 'nested': nested, 'n_sab': n_sab,
                             'power_fa': hits / sims, 'p_refuted_ci_excludes_10pp': refuted / sims})
    for hc in (.85, .95):
        for delta in (0.0, -.05):
            for nested in (False, True):
                ni = 0
                for _ in range(sims):
                    a, b, c, d = _pairs(rng, n_hon, hc, hc + delta, nested)
                    lo, _ = newcombe_paired(a + 0, c, b, d)  # HC_ve - HC_script
                    ni += lo > -.10
                rows.append({'hc_script': hc, 'hc_ve': round(hc + delta, 2), 'nested': nested, 'n_hon': n_hon,
                             'power_ni': ni / sims})
    return rows
