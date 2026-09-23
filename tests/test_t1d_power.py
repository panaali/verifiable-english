"""T1d paired-power helpers: exact tests, intervals, ICC, Holm (fast, offline)."""
from itertools import product

import numpy as np
import pytest
from scipy import stats

from ve_experiments.t1d import power as P


def test_mcnemar_exact_matches_binomial():
    assert P.mcnemar_exact(0, 0) == 1.0
    assert P.mcnemar_exact(0, 7) == pytest.approx(2 * 0.5 ** 7)  # T1c: 7 discordant, p = .016
    assert P.mcnemar_exact(3, 9) == pytest.approx(stats.binomtest(3, 12).pvalue)


def test_signflip_exact_equals_enumeration():
    rng = np.random.default_rng(1)
    for _ in range(20):
        k = int(rng.integers(1, 4))
        d = rng.integers(-k, k + 1, size=int(rng.integers(1, 11))) / k
        obs = abs(d.sum())
        sums = [abs(np.dot(s, np.abs(d))) for s in product((-1, 1), repeat=len(d))]
        brute = np.mean([s >= obs - 1e-9 for s in sums])
        assert P.signflip_p(d, k) == pytest.approx(brute)


def test_tango_interval_contains_estimate_and_ni_p_consistent():
    lo, hi = P.tango_interval(3, 5, 80)
    assert lo < (3 - 5) / 80 < hi
    # All concordant: lower bound is about -(z^2 / (n + z^2)) and passes a 10pp margin at n = 80.
    lo0, hi0 = P.tango_interval(0, 0, 80)
    z2 = stats.norm.ppf(0.975) ** 2
    assert lo0 == pytest.approx(-z2 / (80 + z2), abs=1e-6) and hi0 == pytest.approx(z2 / (80 + z2), abs=1e-6)
    # NI test at level alpha rejects iff the 1 - 2*alpha interval's lower bound exceeds -margin.
    for n12, n21 in ((0, 0), (1, 4), (0, 6), (2, 9)):
        lower = P.tango_interval(n12, n21, 80, level=0.95)[0]
        assert (P.tango_ni_p(n12, n21, 80, 0.10) <= 0.025) == (lower > -0.10)


def test_newcombe_method10_worked_example():
    # Newcombe (1998) example a=36, b=12, c=2, d=0: difference .2, method 10 gives [.0569, .3404].
    lo, hi = P.newcombe_interval(36, 12, 2, 0)
    assert lo == pytest.approx(0.0569, abs=5e-4) and hi == pytest.approx(0.3404, abs=5e-4)


def test_icc_and_holm():
    assert P.icc_oneway(np.array([[1, 1], [0, 0], [1, 1], [0, 0]])) == pytest.approx(1.0)
    rej = P.holm_reject(np.array([[0.01, 0.04, 0.03, 0.2], [0.001, 0.02, 0.0126, 0.5]]))
    assert rej.tolist() == [[True, False, False, False], [True, True, True, False]]


def test_small_simulation_power_is_monotone_in_effect():
    rng = np.random.default_rng(0)
    weak = (P.binding_power(rng, 400, 40, 1, 0.15, 0.10, 0.6) <= 0.05).mean()
    strong = (P.binding_power(rng, 400, 40, 1, 0.70, 0.0, 0.6) <= 0.05).mean()
    assert strong > 0.99 and weak < 0.3


def test_clopper_pearson_and_two_sided_harm_direction():
    lo, hi = P.clopper_pearson(0, 40)
    assert lo == 0 and hi == pytest.approx(1 - 0.025 ** (1 / 40))
    lo, hi = P.clopper_pearson(6, 60)
    assert lo == pytest.approx(stats.beta.ppf(.025, 6, 55)) and hi == pytest.approx(stats.beta.ppf(.975, 7, 54))
    rng = np.random.default_rng(3)
    p, d, _ = P.binding_pvalues(rng, 300, 60, 0.05, 0.40, 0.6, 0.5)  # VE approves far more: harm
    assert ((p <= .05) & (d < 0)).mean() > .9


def test_ni_reported_bound_matches_the_doubled_p_test_at_every_holm_level():
    """v4 regression (second-round review): the bound reported for the doubled one-sided NI p tested
    at Holm level alpha_j is the two-sided (1 - alpha_j) Tango interval, and the two always agree."""
    n, margin = 160, 0.10
    for alpha_j in [P.ALPHA / m for m in range(1, 7)]:
        for n12 in range(0, 4):
            for n21 in range(0, 16):
                rejects = P.ni_doubled_p(n12, n21, n, margin) <= alpha_j
                assert rejects == (P.ni_bound(n12, n21, n, alpha_j) > -margin), (alpha_j, n12, n21)
    # The reviewer's case: n = 160, n12 = 0, n21 = 6. Doubled p = .008408 > .05/6, so (c) is not rejected at
    # the first Holm step, and the reported (1 - .05/6) bound does not pass -10%. The v3 (1 - 2 alpha_j)
    # interval did pass it, contradicting the test.
    assert P.ni_doubled_p(0, 6, n) == pytest.approx(0.008408, abs=5e-6)
    assert P.ni_bound(0, 6, n, P.ALPHA / 6) <= -margin
    assert P.tango_interval(0, 6, n, level=1 - 2 * P.ALPHA / 6)[0] > -margin


def test_power_scenarios_share_one_raw_rate_across_strata():
    for raw, char_ve, related_ve, honest in P.SCENARIOS.values():
        assert 0 <= raw <= 1 and honest in P.HONEST
    harm = {k: v for k, v in P.SCENARIOS.items() if 'harm' in k}
    assert harm and all(max(v[1], v[2]) > v[0] for v in harm.values())  # harm needs VE above the shared raw rate
