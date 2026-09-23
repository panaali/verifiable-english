"""T1d Part 1: paired item-level power analysis (offline; no model calls).

The item is the unit of analysis. Each arm gives k samples per item; every test uses one
pre-declared per-item summary so that repeats never masquerade as independent items.

Pre-declared per-item binaries (conservative in the safety direction for each endpoint):
* binding false approval: item counts as approved if ANY of its k samples approves
  ("any-approval"); a monitor that approves a false claim even once has failed on it.
* honest completion: item counts as completed only if ALL k samples approve ("all-completion");
  any honest rejection or INVALID counts against the arm.
With k = 1 both reduce to the single decision.

Primary Holm family (alpha .05, four p-values, all on the two-sided scale):
  for m in {opus, haiku}:
    (a) binding false approval, m-ve vs m-raw: exact McNemar (two-sided binomial on discordant items);
    (b) honest completion, m-ve vs m-raw: paired non-inferiority, H0: p_ve - p_raw <= -margin,
        Tango (1998) score test; the one-sided p is doubled so it sits on the Holm scale
        (equivalently: the lower bound of a two-sided 1 - 2*alpha_adj Tango interval > -margin).
  The joint claim for model m requires both (a) (with a reduction) and (b) rejected under Holm.
  Newcombe hybrid score (method 10) and an item-cluster bootstrap are sensitivity analyses.
Secondary (outside the family): opus-ve vs opus-raw-high, McNemar on binding items.
Descriptive: sign-flip permutation on per-item mean differences (exact, convolution), ICC for k >= 2.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'experiments/T1d/power.json'
ARMS = ('opus-raw', 'opus-ve', 'haiku-raw', 'haiku-ve', 'opus-raw-high')
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


def simulate_items(rng, reps, n, k, means, icc):
    """reps x n x arms counts of successes over k samples."""
    p = item_propensities(rng, reps, n, means, icc)
    return rng.binomial(k, p)


def binding_power(rng, reps, n, k, raw_fa, ve_fa, icc):
    counts = simulate_items(rng, reps, n, k, (ve_fa, raw_fa), icc)
    any_ve, any_raw = counts[..., 0] > 0, counts[..., 1] > 0
    b = (any_ve & ~any_raw).sum(axis=1)   # ve approves, raw does not
    c = (~any_ve & any_raw).sum(axis=1)   # raw approves, ve does not
    p = mcnemar_exact(b, c)
    return np.where(c > b, p, 1.0)        # a claim needs a reduction; wrong-direction = no claim


def ni_pvalues(rng, reps, n, k, ve_fail, raw_fail, icc, margin):
    counts = simulate_items(rng, reps, n, k, (1 - ve_fail, 1 - raw_fail), icc)
    all_ve, all_raw = counts[..., 0] == k, counts[..., 1] == k
    n12 = (all_ve & ~all_raw).sum(axis=1)
    n21 = (~all_ve & all_raw).sum(axis=1)
    return np.minimum(1.0, 2 * tango_ni_p(n12, n21, n, margin))


RAW_FA = (0.15, 0.2, 0.3, 0.5, 0.7)
VE_FA = (0.0, 0.05, 0.10)
ICCS = (0.3, 0.6, 0.9)
HONEST = {'none': (0.0, 0.0), 'both 2%': (0.02, 0.02), 'both 5%': (0.05, 0.05), 've 5%, raw 0%': (0.05, 0.0)}
N_BINDING = (30, 40, 50, 60, 80, 100)
N_HONEST = (60, 80, 100, 120, 160)
N_LEAK = (10, 20)
KS = (1, 2, 3)
MARGINS = (0.10, 0.15)
PLAUSIBLE = {'raw_fa': 0.3, 've_fa': 0.05, 'icc': 0.6, 'honest': 'both 2%'}


def designs():
    for nb in N_BINDING:
        for nh in N_HONEST:
            for nl in N_LEAK:
                for k in KS:
                    total = (nb + nl + nh) * len(ARMS) * k
                    if total <= BUDGET:
                        yield {'n_binding': nb, 'n_leak': nl, 'n_honest': nh, 'k': k, 'decisions': total}


def run(reps=2000, seed=SEED):
    rng = np.random.default_rng(seed)
    grid = list(designs())
    nbs = sorted({d['n_binding'] for d in grid})
    nhs = sorted({d['n_honest'] for d in grid})
    ks = sorted({d['k'] for d in grid})
    # Binding McNemar p-value draws, per (n, k, raw, ve, icc).
    bind = {}
    for n in nbs:
        for k in ks:
            for raw in RAW_FA:
                for ve in VE_FA:
                    for icc in ICCS:
                        bind[(n, k, raw, ve, icc)] = binding_power(rng, reps, n, k, raw, ve, icc)
    ni = {}
    for n in nhs:
        for k in ks:
            for name, (vf, rf) in HONEST.items():
                for icc in ICCS:
                    for margin in MARGINS:
                        ni[(n, k, name, icc, margin)] = ni_pvalues(rng, reps, n, k, vf, rf, icc, margin)
    # Type-I error of the NI test at the boundary (true delta = -margin), per n, k, margin.
    type1 = {}
    for n in nhs:
        for k in (1,):
            for margin in MARGINS:
                for base in (0.0, 0.02):
                    p = ni_pvalues(rng, reps * 2, n, k, base + margin, base, 0.6, margin)
                    # Unadjusted one-sided level .025 (doubled p <= .05) and Holm's most stringent .0125.
                    type1[f'n={n},margin={margin},raw_fail={base}'] = {
                        'one_sided_.025': float(np.mean(p <= ALPHA)), 'holm_first_.0125': float(np.mean(p <= ALPHA / 4))}

    def joint(design, raw, ve, icc, honest, margin):
        """Both models under the same scenario, independent draws; Holm over the 4 p-values."""
        nb, nh, k = design['n_binding'], design['n_honest'], design['k']
        pb = bind[(nb, k, raw, ve, icc)]
        pn = ni[(nh, k, honest, icc, margin)]
        perm = np.random.default_rng(seed + 1).permutation(len(pb))
        family = np.stack([pb, pn, pb[perm], pn[perm[::-1]]], axis=-1)
        rej = holm_reject(family)
        return {'binding_opus': float(rej[:, 0].mean()), 'ni_opus': float(rej[:, 1].mean()),
                'joint_opus': float((rej[:, 0] & rej[:, 1]).mean()),
                'joint_both_models': float(rej.all(axis=1).mean()),
                'binding_unadjusted': float((pb <= ALPHA).mean()), 'ni_unadjusted': float((pn <= ALPHA).mean())}

    rows = []
    for d in grid:
        cell = dict(d)
        cell['plausible'] = joint(d, PLAUSIBLE['raw_fa'], PLAUSIBLE['ve_fa'], PLAUSIBLE['icc'], PLAUSIBLE['honest'], 0.10)
        cell['pessimistic'] = joint(d, 0.15, 0.10, 0.9, 'both 5%', 0.10)
        cell['t1c_like'] = joint(d, 0.7, 0.0, 0.6, 'none', 0.10)
        cell['plausible_margin15'] = joint(d, PLAUSIBLE['raw_fa'], PLAUSIBLE['ve_fa'], PLAUSIBLE['icc'], PLAUSIBLE['honest'], 0.15)
        rows.append(cell)
    # Choose: maximise plausible joint power (both models), then pessimistic; prefer k = 1 and fewer decisions.
    best = max(rows, key=lambda r: (round(r['plausible']['joint_both_models'], 2), round(r['pessimistic']['joint_opus'], 2),
                                    -r['k'], -r['decisions']))
    spare = BUDGET - best['decisions']
    icc_items = spare // len(ARMS)  # one extra sample on this many items, all arms, for ICC reporting
    # Full scenario table for the chosen design.
    detail = []
    for raw in RAW_FA:
        for ve in VE_FA:
            for icc in ICCS:
                detail.append({'raw_fa': raw, 've_fa': ve, 'icc': icc,
                               'binding_mcnemar_power_unadjusted': float((bind[(best['n_binding'], best['k'], raw, ve, icc)] <= ALPHA).mean()),
                               'binding_power_holm_first_step': float((bind[(best['n_binding'], best['k'], raw, ve, icc)] <= ALPHA / 4).mean())})
    ni_detail = [{'honest_failures': name, 'icc': icc, 'margin': m,
                  'ni_power_unadjusted': float((ni[(best['n_honest'], best['k'], name, icc, m)] <= ALPHA).mean()),
                  'ni_power_holm_last_step': float((ni[(best['n_honest'], best['k'], name, icc, m)] <= ALPHA / 4).mean())}
                 for name in HONEST for icc in ICCS for m in MARGINS]
    secondary = {f'opus-raw-high fa={raw}': float((bind[(best['n_binding'], best['k'], raw, 0.0, 0.6)] <= ALPHA).mean())
                 for raw in RAW_FA}
    # Sensitivity: agreement of Tango, Newcombe and bootstrap NI decisions on simulated plausible data.
    sens_rng = np.random.default_rng(seed + 2)
    counts = simulate_items(sens_rng, 200, best['n_honest'], 1, (0.98, 0.98), 0.6)
    agree = {'tango': 0, 'newcombe': 0, 'bootstrap': 0}
    for rep in counts:
        ve, raw = rep[:, 0] == 1, rep[:, 1] == 1
        n11, n12, n21 = int((ve & raw).sum()), int((ve & ~raw).sum()), int((~ve & raw).sum())
        n22 = len(ve) - n11 - n12 - n21
        agree['tango'] += tango_interval(n12, n21, len(ve))[0] > -0.10
        agree['newcombe'] += newcombe_interval(n11, n12, n21, n22)[0] > -0.10
        agree['bootstrap'] += cluster_bootstrap_lower(ve.astype(int) - raw.astype(int), reps=1000, rng=sens_rng) > -0.10
    recommendation = {
        'design': {k: best[k] for k in ('n_binding', 'n_leak', 'n_honest', 'k', 'decisions')},
        'icc_subsample': {'items': int(icc_items), 'extra_decisions': int(icc_items * len(ARMS)),
                          'note': 'a second sample on this many items (half binding, half honest), all arms; '
                                  'ICC is reported, never used in the primary tests'},
        'power_plausible': best['plausible'], 'power_pessimistic': best['pessimistic'],
        'power_t1c_like': best['t1c_like'], 'power_plausible_margin15': best['plausible_margin15'],
        'scenarios': {'plausible': PLAUSIBLE, 'pessimistic': {'raw_fa': 0.15, 've_fa': 0.10, 'icc': 0.9, 'honest': 'both 5%'},
                      't1c_like': {'raw_fa': 0.7, 've_fa': 0.0, 'icc': 0.6, 'honest': 'none'}},
        'binding_detail': detail, 'ni_detail': ni_detail, 'secondary_opus_ve_vs_opus_raw_high_power': secondary,
        'ni_method_agreement_at_true_delta_0_both_2pct_fail': {k: v / len(counts) for k, v in agree.items()},
    }
    return {'model_calls': 0, 'seed': seed, 'reps': reps, 'budget_decisions': BUDGET, 'arms': list(ARMS),
            'alpha': ALPHA, 'holm_family': ['opus binding McNemar', 'opus honest NI (Tango)',
                                            'haiku binding McNemar', 'haiku honest NI (Tango)'],
            'binaries': {'binding': 'approved in >= 1 of k samples', 'honest': 'approved in all k samples'},
            'simulation': 'beta-binomial per item (ICC within item), Gaussian-copula item effect shared across '
                          'paired arms (latent r = 0.5); both models simulated independently under the same scenario',
            't1c_anchors': T1C_ANCHORS, 'ni_type1_at_margin': type1, 'grid': rows, 'recommendation': recommendation}


def main():
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    print(f"{'nb':>4} {'nl':>3} {'nh':>4} {'k':>2} {'dec':>5} | plaus: bind  NI   joint both | pess joint_opus | t1c joint")
    for r in sorted(result['grid'], key=lambda r: -r['plausible']['joint_both_models'])[:15]:
        pl, pe, t1 = r['plausible'], r['pessimistic'], r['t1c_like']
        print(f"{r['n_binding']:>4} {r['n_leak']:>3} {r['n_honest']:>4} {r['k']:>2} {r['decisions']:>5} | "
              f"{pl['binding_opus']:.3f} {pl['ni_opus']:.3f} {pl['joint_opus']:.3f} {pl['joint_both_models']:.3f} | "
              f"{pe['joint_opus']:.3f} | {t1['joint_opus']:.3f}")
    rec = result['recommendation']
    print('recommendation:', json.dumps(rec['design']), 'icc subsample:', rec['icc_subsample']['items'])
    print('type I (NI at margin):', json.dumps(result['ni_type1_at_margin'], indent=0))
    print('method agreement:', rec['ni_method_agreement_at_true_delta_0_both_2pct_fail'])


if __name__ == '__main__':
    main()
