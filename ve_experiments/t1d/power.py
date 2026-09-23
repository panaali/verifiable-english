"""T1d Part 1: paired item-level power analysis, v4 (offline; no model calls).

The item is the unit of analysis; k = 1 (a 30-item second sample is used only to report the ICC).
Fixed design (v2 recommendation, unchanged): 100 binding items = 40 CHARACTER (char_principal,
char_resource) + 60 RELATED-ENTITY (alias, group_member, role_user; called "semantic" before v4),
10 leak, 160 honest; five arms.

v3 primary Holm family (alpha .05, SIX p-values, all two-sided scale), for m in {opus, haiku}:
  (a) char binding false approval, m-ve vs m-raw: exact two-sided McNemar on the 40 char items;
  (b) related-entity binding false approval, m-ve vs m-raw: exact two-sided McNemar on the 60
      related-entity items;
  (c) honest completion NI at a 10 pp margin, Tango score test, one-sided p doubled onto the Holm scale.
      v4 correction: a doubled one-sided p tested at Holm level alpha_j rejects iff the one-sided p is
      <= alpha_j / 2, i.e. iff the lower limit of the two-sided (1 - alpha_j) Tango interval exceeds
      -0.10. That (1 - alpha_j) bound is what is reported (`ni_bound`); v3 wrote (1 - 2 alpha_j), which
      is looser than the test.
v4: the raw prompt does not depend on the sabotage kind (`materials.generate` never reads it), so raw
false approval is ONE rate per model shared by both strata; every scenario below respects that.
Claims (redefined): "the protocol helps model m on stratum s" iff (s) rejected with FEWER VE false
approvals AND (c) rejected. A rejection of (a) or (b) with MORE VE false approvals is the declared
HARM outcome ("the certificate protocol increased false approval"), never discarded. VE-arm false
approval per stratum is also reported with an exact Clopper-Pearson 95% CI.
Power is reported per model and for both models jointly, per stratum claim, over ICC and the latent
paired-arm correlation. Secondary (outside the family): opus-ve vs opus-raw-high, McNemar on all 100
binding items, with VE false approval 0, 5% or 10%.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'experiments/T1d/power.json'
ARMS = ('opus-raw', 'opus-raw-high', 'opus-ve', 'haiku-raw', 'haiku-ve')
BUDGET = 1500
ALPHA = 0.05
SEED = 20260923

# T1c anchors (experiments/T1c/RESULTS.md; 20,000 facts unless stated).
T1C_ANCHORS = {
    'opus-raw binding false approval': '7/10 (20k), 0/5 (5k); gate 8/30 samples, 6/10 items (27%)',
    'haiku-raw binding false approval': '7/10 (20k), 4/5 (5k)',
    'certificate arms binding/leak false approval': '0/60 claims pooled over arms and sizes',
    'honest completion': 'opus-raw 30/30, opus-ve 30/30, haiku-raw 29/30, haiku-ve 30/30',
}


# ----------------------------------------------------------------------------- tests

def mcnemar_exact(b, c):
    """Two-sided exact McNemar p (vectorised). b, c: discordant counts."""
    b, c = np.asarray(b), np.asarray(c)
    n = b + c
    p = 2 * stats.binom.cdf(np.minimum(b, c), np.maximum(n, 1), 0.5)
    return np.where(n == 0, 1.0, np.minimum(1.0, p))


def tango_z(n12, n21, n, delta0):
    """Tango (1998) score statistic for delta = p1 - p2 = (n12 - n21)/n under H0 delta = delta0.

    n12: items where arm 1 succeeds and arm 2 fails; n21 the reverse (vectorised).
    """
    n12, n21, n = (np.asarray(x, dtype=float) for x in (n12, n21, n))
    a = 2 * n
    b = -n12 - n21 + (2 * n - n12 + n21) * delta0
    c = -n21 * delta0 * (1 - delta0)
    p21 = (-b + np.sqrt(np.maximum(b * b - 4 * a * c, 0))) / (2 * a)
    var = n * (2 * p21 + delta0 * (1 - delta0))  # Var(n12 - n21) under p12 = p21 + delta0
    num = n12 - n21 - n * delta0
    with np.errstate(divide='ignore', invalid='ignore'):
        z = num / np.sqrt(np.maximum(var, 0))
    return np.where(var > 1e-12, z, np.where(num > 0, np.inf, np.where(num < 0, -np.inf, 0.0)))


def tango_ni_p(n12, n21, n, margin):
    """One-sided p for H0: delta <= -margin (arm 1 = ve, arm 2 = raw)."""
    return stats.norm.sf(tango_z(n12, n21, n, -margin))


def tango_interval(n12, n21, n, level=0.95):
    """Scalar Tango score interval by bisection on the (monotone) statistic."""
    zc = stats.norm.ppf(0.5 + level / 2)
    d = (n12 - n21) / n

    def root(target, lo, hi):
        for _ in range(80):
            mid = (lo + hi) / 2
            if (tango_z(n12, n21, n, mid) - target) > 0:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = -1.0 if tango_z(n12, n21, n, -1 + 1e-12) <= zc else root(zc, -1 + 1e-12, d)
    upper = 1.0 if tango_z(n12, n21, n, 1 - 1e-12) >= -zc else root(-zc, d, 1 - 1e-12)
    return float(lower), float(upper)


def ni_bound(n12, n21, n, alpha_j):
    """The reported NI bound: lower limit of the two-sided (1 - alpha_j) Tango interval, alpha_j the Holm
    level at which the doubled one-sided NI p-value was tested. Rejection of (c) at alpha_j holds iff
    this bound exceeds -margin (tested in tests/test_t1d_power.py)."""
    return tango_interval(n12, n21, n, level=1 - alpha_j)[0]


def ni_doubled_p(n12, n21, n, margin=0.10):
    return float(min(1.0, 2 * tango_ni_p(n12, n21, n, margin)))


def wilson(x, n, level=0.95):
    z = stats.norm.ppf(0.5 + level / 2)
    p = x / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def newcombe_interval(n11, n12, n21, n22, level=0.95):
    """Newcombe (1998) method 10: hybrid score interval for a paired difference p1 - p2."""
    n = n11 + n12 + n21 + n22
    p1, p2 = (n11 + n12) / n, (n11 + n21) / n
    l1, u1 = wilson(n11 + n12, n, level)
    l2, u2 = wilson(n11 + n21, n, level)
    den = (n11 + n12) * (n21 + n22) * (n11 + n21) * (n12 + n22)
    phi = 0.0 if den == 0 else (n11 * n22 - n12 * n21) / np.sqrt(den)
    d = p1 - p2
    lower = d - np.sqrt(max((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2, 0))
    upper = d + np.sqrt(max((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2, 0))
    return float(lower), float(upper)


def cluster_bootstrap_lower(item_diffs, level=0.95, reps=4000, rng=None):
    """Percentile lower bound (two-sided level) of the mean per-item difference."""
    rng = rng or np.random.default_rng(SEED)
    x = np.asarray(item_diffs, dtype=float)
    means = x[rng.integers(0, len(x), size=(reps, len(x)))].mean(axis=1)
    return float(np.quantile(means, (1 - level) / 2))


def signflip_p(item_diffs, k):
    """Exact two-sided sign-flip permutation p on per-item mean differences.

    Differences are multiples of 1/k, so the null distribution of the sum of +-|d_i| is an exact
    integer convolution (no enumeration of 2^n sign patterns).
    """
    units = np.rint(np.abs(np.asarray(item_diffs, dtype=float)) * k).astype(int)
    units = units[units > 0]
    if not len(units):
        return 1.0
    total = int(units.sum())
    dist = np.zeros(2 * total + 1)
    dist[total] = 1.0
    for u in units:
        shifted = np.zeros_like(dist)
        shifted[u:] += dist[:-u] * 0.5
        shifted[:-u] += dist[u:] * 0.5
        dist = shifted
    observed = abs(int(np.rint(np.sum(np.asarray(item_diffs) * k))))
    support = np.arange(-total, total + 1)
    return float(min(1.0, dist[np.abs(support) >= observed - 1e-9].sum()))


def icc_oneway(samples):
    """ICC(1) from an items x k matrix of 0/1 samples (one-way random-effects ANOVA)."""
    y = np.asarray(samples, dtype=float)
    n, k = y.shape
    if k < 2 or n < 2:
        return float('nan')
    grand = y.mean()
    msb = k * ((y.mean(axis=1) - grand) ** 2).sum() / (n - 1)
    msw = ((y - y.mean(axis=1, keepdims=True)) ** 2).sum() / (n * (k - 1))
    den = msb + (k - 1) * msw
    return float((msb - msw) / den) if den > 0 else float('nan')


def holm_reject(pvalues, alpha=ALPHA):
    """Holm step-down on the last axis; returns a boolean array of rejections."""
    p = np.asarray(pvalues, dtype=float)
    m = p.shape[-1]
    order = np.argsort(p, axis=-1)
    sorted_p = np.take_along_axis(p, order, axis=-1)
    ok = sorted_p <= alpha / (m - np.arange(m))
    ok = np.cumprod(ok, axis=-1).astype(bool)
    reject = np.zeros_like(ok)
    np.put_along_axis(reject, order, ok, axis=-1)
    return reject


# ----------------------------------------------------------------------------- simulation

def item_propensities(rng, reps, n, means, icc, cross_r=0.5):
    """Per-item success propensities for paired arms (Gaussian copula, beta marginals).

    Each arm's per-item propensity is Beta with the arm's mean and within-item ICC `icc`
    (beta-binomial across the k samples); arms share an item effect with latent correlation
    cross_r (items that fool one arm tend to fool the other).
    """
    shared = rng.standard_normal((reps, n, 1))
    own = rng.standard_normal((reps, n, len(means)))
    u = stats.norm.cdf(np.sqrt(cross_r) * shared + np.sqrt(1 - cross_r) * own)
    out = np.empty_like(u)
    for j, mu in enumerate(means):
        if mu <= 0 or mu >= 1:
            out[..., j] = float(mu >= 1)
            continue
        s = (1 - icc) / icc
        out[..., j] = stats.beta.ppf(u[..., j], mu * s, (1 - mu) * s)
    return out


def simulate_items(rng, reps, n, k, means, icc, cross_r=0.5):
    """reps x n x arms counts of successes over k samples."""
    p = item_propensities(rng, reps, n, means, icc, cross_r)
    return rng.binomial(k, p)


def clopper_pearson(x, n, level=0.95):
    a = (1 - level) / 2
    lo = 0.0 if x == 0 else float(stats.beta.ppf(a, x, n - x + 1))
    hi = 1.0 if x == n else float(stats.beta.ppf(1 - a, x + 1, n - x))
    return lo, hi


def binding_pvalues(rng, reps, n, raw_fa, ve_fa, icc, cross_r):
    """Two-sided exact McNemar p and the direction (+1: VE approves fewer false claims)."""
    counts = simulate_items(rng, reps, n, 1, (ve_fa, raw_fa), icc, cross_r)
    ve, raw = counts[..., 0] > 0, counts[..., 1] > 0
    b = (ve & ~raw).sum(axis=1)   # VE approves, raw does not
    c = (~ve & raw).sum(axis=1)   # raw approves, VE does not
    return mcnemar_exact(b, c), np.sign(c - b), ve.sum(axis=1)


def binding_power(rng, reps, n, k, raw_fa, ve_fa, icc, cross_r=0.5):
    """p-values usable for a REDUCTION claim (wrong direction -> 1). Kept for the v2 tests."""
    counts = simulate_items(rng, reps, n, k, (ve_fa, raw_fa), icc, cross_r)
    any_ve, any_raw = counts[..., 0] > 0, counts[..., 1] > 0
    b = (any_ve & ~any_raw).sum(axis=1)
    c = (~any_ve & any_raw).sum(axis=1)
    p = mcnemar_exact(b, c)
    return np.where(c > b, p, 1.0)


def ni_pvalues(rng, reps, n, k, ve_fail, raw_fail, icc, margin, cross_r=0.5):
    counts = simulate_items(rng, reps, n, k, (1 - ve_fail, 1 - raw_fail), icc, cross_r)
    all_ve, all_raw = counts[..., 0] == k, counts[..., 1] == k
    n12 = (all_ve & ~all_raw).sum(axis=1)
    n21 = (~all_ve & all_raw).sum(axis=1)
    return np.minimum(1.0, 2 * tango_ni_p(n12, n21, n, margin))


N_CHAR, N_RELATED, N_LEAK, N_HONEST, K = 40, 60, 10, 160, 1
ICC_ITEMS = 30
MARGIN = 0.10
ICCS = (0.3, 0.6, 0.9)
CROSS_R = (0.2, 0.5, 0.8)
RAW_FA = (0.15, 0.2, 0.3, 0.5, 0.7)
VE_FA = (0.0, 0.05, 0.10, 0.20)
HONEST = {'none': (0.0, 0.0), 'both 2%': (0.02, 0.02), 'both 5%': (0.05, 0.05), 've 5%, raw 0%': (0.05, 0.0)}
SCENARIOS = {  # (raw, char VE, related-entity VE, honest failures): ONE raw rate per model for both strata
    'plausible': (0.30, 0.05, 0.05, 'both 2%'),
    'related_entity_fools_ve': (0.30, 0.05, 0.25, 'both 2%'),
    'related_entity_fools_ve_fully': (0.30, 0.05, 0.30, 'both 2%'),
    'pessimistic': (0.15, 0.10, 0.10, 'both 5%'),
    't1c_like': (0.70, 0.0, 0.0, 'none'),
    'related_entity_harm': (0.10, 0.05, 0.25, 'both 2%'),
    'related_entity_harm_strong': (0.10, 0.05, 0.35, 'both 2%'),
    'char_harm': (0.10, 0.25, 0.05, 'both 2%'),
}


def run(reps=4000, seed=SEED):
    rng = np.random.default_rng(seed)
    decisions = (N_CHAR + N_RELATED + N_LEAK + N_HONEST) * len(ARMS) * K
    icc_decisions = ICC_ITEMS * len(ARMS)

    def family(sc, icc, r):
        """One model: (char p, char dir, related p, related dir, NI p). Independent draws per model."""
        raw, cv, sv, honest = SCENARIOS[sc]
        cr = sr = raw  # one shared raw false-approval rate per model
        pc, dc, _ = binding_pvalues(rng, reps, N_CHAR, cr, cv, icc, r)
        ps, ds, _ = binding_pvalues(rng, reps, N_RELATED, sr, sv, icc, r)
        vf, rf = HONEST[honest]
        pn = ni_pvalues(rng, reps, N_HONEST, K, vf, rf, icc, MARGIN, r)
        return pc, dc, ps, ds, pn

    scenario_power = []
    for sc in SCENARIOS:
        for icc in ICCS:
            for r in CROSS_R:
                opus, haiku = family(sc, icc, r), family(sc, icc, r)
                ps = np.stack([opus[0], opus[2], opus[4], haiku[0], haiku[2], haiku[4]], axis=-1)
                rej = holm_reject(ps)
                out = {'scenario': sc, 'icc': icc, 'cross_r': r}
                for m, (base, draws) in (('opus', (0, opus)), ('haiku', (3, haiku))):
                    char = rej[:, base] & (draws[1] > 0)
                    sem = rej[:, base + 1] & (draws[3] > 0)
                    ni = rej[:, base + 2]
                    out[m] = {'char_reduction': float(char.mean()), 'related_reduction': float(sem.mean()),
                              'ni': float(ni.mean()), 'claim_char': float((char & ni).mean()),
                              'claim_related': float((sem & ni).mean()), 'claim_both_strata': float((char & sem & ni).mean()),
                              'harm_char': float((rej[:, base] & (draws[1] < 0)).mean()),
                              'harm_related': float((rej[:, base + 1] & (draws[3] < 0)).mean())}
                    out[m]['_char'], out[m]['_sem'], out[m]['_ni'] = char, sem, ni
                for claim, key in (('claim_char', ('_char',)), ('claim_related', ('_sem',)),
                                   ('claim_both_strata', ('_char', '_sem'))):
                    ok = np.ones(reps, dtype=bool)
                    for m in ('opus', 'haiku'):
                        ok &= out[m]['_ni']
                        for k_ in key:
                            ok &= out[m][k_]
                    out[f'both_models_{claim}'] = float(ok.mean())
                for m in ('opus', 'haiku'):
                    for k_ in ('_char', '_sem', '_ni'):
                        del out[m][k_]
                scenario_power.append(out)

    # Unadjusted and first-step (alpha/6) McNemar power per stratum size over the rate grid.
    stratum_grid = []
    for name, n in (('char', N_CHAR), ('related', N_RELATED)):
        for raw in RAW_FA:
            for ve in VE_FA:
                for r in CROSS_R:
                    p, d, _ = binding_pvalues(rng, reps, n, raw, ve, 0.6, r)
                    stratum_grid.append({'stratum': name, 'n': n, 'raw_fa': raw, 've_fa': ve, 'icc': 0.6, 'cross_r': r,
                                         'reduction_unadjusted': float(((p <= ALPHA) & (d > 0)).mean()),
                                         'reduction_alpha_over_6': float(((p <= ALPHA / 6) & (d > 0)).mean()),
                                         'harm_unadjusted': float(((p <= ALPHA) & (d < 0)).mean())})
    # Harm detection: VE false approval above raw.
    harm = []
    for name, n in (('char', N_CHAR), ('related', N_RELATED)):
        for raw, ve in ((0.05, 0.20), (0.05, 0.30), (0.10, 0.25), (0.10, 0.35), (0.0, 0.15)):
            p, d, _ = binding_pvalues(rng, reps, n, raw, ve, 0.6, 0.5)
            harm.append({'stratum': name, 'n': n, 'raw_fa': raw, 've_fa': ve,
                         'harm_power_unadjusted': float(((p <= ALPHA) & (d < 0)).mean()),
                         'harm_power_alpha_over_6': float(((p <= ALPHA / 6) & (d < 0)).mean())})
    # Clopper-Pearson half-widths of the VE-arm false approval estimate at the stratum sizes.
    cp = {f'{name} n={n}, {x} approvals': [round(v, 4) for v in clopper_pearson(x, n)]
          for name, n in (('char', N_CHAR), ('related', N_RELATED)) for x in (0, 2, 6)}
    # NI type I error at the margin and NI power.
    type1 = {}
    for base in (0.0, 0.02):
        p = ni_pvalues(rng, reps, N_HONEST, K, base + MARGIN, base, 0.6, MARGIN)
        type1[f'raw_fail={base}'] = {'one_sided_.025': float(np.mean(p <= ALPHA)),
                                     'holm_first_.05/6': float(np.mean(p <= ALPHA / 6))}
    ni_detail = [{'honest_failures': name, 'icc': icc, 'cross_r': r,
                  'ni_power_unadjusted': float((ni_pvalues(rng, reps, N_HONEST, K, *HONEST[name], icc, MARGIN, r) <= ALPHA).mean())}
                 for name in HONEST for icc in ICCS for r in CROSS_R]
    # Secondary: opus-ve vs opus-raw-high, all 100 binding items, VE false approval 0 / 5 / 10%.
    secondary = {f'raw_high_fa={raw}, ve_fa={ve}': float(((lambda pd: (pd[0] <= ALPHA) & (pd[1] > 0))(
        binding_pvalues(rng, reps, N_CHAR + N_RELATED, raw, ve, 0.6, 0.5))).mean())
        for raw in RAW_FA for ve in (0.0, 0.05, 0.10)}
    headline = {sc: next(o for o in scenario_power if o['scenario'] == sc and o['icc'] == 0.6 and o['cross_r'] == 0.5)
                for sc in SCENARIOS}
    return {'model_calls': 0, 'seed': seed, 'reps': reps, 'arms': list(ARMS), 'alpha': ALPHA,
            'design': {'n_char': N_CHAR, 'n_related': N_RELATED, 'n_leak': N_LEAK, 'n_honest': N_HONEST, 'k': K,
                       'decisions': decisions, 'icc_subsample_items': ICC_ITEMS, 'icc_decisions': icc_decisions,
                       'total_decisions': decisions + icc_decisions},
            'holm_family': ['opus char McNemar', 'opus related-entity McNemar', 'opus honest NI (Tango)',
                            'haiku char McNemar', 'haiku related-entity McNemar', 'haiku honest NI (Tango)'],
            'claims': {'stratum s, model m': 'McNemar_s rejected with fewer VE false approvals AND NI rejected',
                       'harm': 'McNemar_s rejected with MORE VE false approvals (declared outcome)'},
            'scenarios': {k: dict(zip(('raw_shared', 'char_ve', 'related_ve', 'honest'), v))
                          for k, v in SCENARIOS.items()},
            'simulation': 'beta-binomial per item, Gaussian-copula item effect shared by paired arms with latent '
                          'correlation cross_r; the two models are simulated independently',
            't1c_anchors': T1C_ANCHORS, 'headline_icc0.6_r0.5': headline, 'scenario_power': scenario_power,
            'stratum_grid': stratum_grid, 'harm_detection': harm, 'clopper_pearson_ve_false_approval': cp,
            'ni_type1_at_margin': type1, 'ni_detail': ni_detail, 'secondary_opus_ve_vs_opus_raw_high': secondary,
            'ni_bound_examples': [{'n': N_HONEST, 'n12_ve_only_success': a, 'n21_raw_only_success': b, 'alpha_j': aj,
                                   'doubled_p': ni_doubled_p(a, b, N_HONEST), 'rejects': ni_doubled_p(a, b, N_HONEST) <= aj,
                                   'reported_bound_1_minus_alpha_j': ni_bound(a, b, N_HONEST, aj)}
                                  for a, b in ((0, 0), (0, 5), (0, 6), (1, 7)) for aj in (ALPHA / 6, ALPHA)]}


def main():
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    for sc, o in result['headline_icc0.6_r0.5'].items():
        print(sc, json.dumps({m: o[m] for m in ('opus', 'haiku')}),
              {k: o[k] for k in o if k.startswith('both_models')})
    print('type I:', result['ni_type1_at_margin'])
    print('harm:', json.dumps(result['harm_detection']))
    print('secondary:', json.dumps(result['secondary_opus_ve_vs_opus_raw_high']))


if __name__ == '__main__':
    main()
