"""Property-based checks of the probability statements in design/evidence-layer-design.md.

Desk mathematics only: every test builds finite probability spaces (random or explicit) and checks
the bounds the design states, plus explicit counterexamples to the statements it retracts.
No model or API calls.

Run: uv run pytest tests/test_evidence_bounds.py -q
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.optimize import linprog

EPS = 1e-9
SEEDS = st.integers(min_value=0, max_value=2**32 - 1)


# ---------------------------------------------------------------- helpers


def rand_space(rng: np.random.Generator, m: int) -> np.ndarray:
    """Random probability weights on m outcomes (some outcomes may get zero mass)."""
    w = rng.random(m) * (rng.random(m) > 0.15)
    if w.sum() == 0:
        w[0] = 1.0
    return w / w.sum()


def rand_event(rng: np.random.Generator, m: int, density: float | None = None) -> np.ndarray:
    d = rng.uniform(0.3, 0.98) if density is None else density
    return rng.random(m) < d


def P(w: np.ndarray, ev: np.ndarray) -> float:
    return float(w[ev].sum())


def frechet_lb(ps) -> float:
    """Boole/Frechet lower bound on P(AND L_i) from marginals (or their lower ends)."""
    ps = list(ps)
    return max(0.0, 1.0 - sum(1.0 - p for p in ps))


def entailed_root(rng, conj: np.ndarray) -> np.ndarray:
    """An arbitrary event R with conj ⊆ R: the semantics of a certified Entails(E, {L_i}, R)."""
    return conj | (rng.random(conj.shape[0]) < rng.uniform(0, 0.7))


# ---------------------------------------------------------------- §2.4 single derivation


@settings(max_examples=400, deadline=None)
@given(SEEDS, st.integers(1, 7), st.integers(2, 40))
def test_root_lower_bound_boole_frechet(seed, n, m):
    rng = np.random.default_rng(seed)
    w = rand_space(rng, m)
    leaves = [rand_event(rng, m) for _ in range(n)]
    conj = np.logical_and.reduce(leaves)
    R = entailed_root(rng, conj)
    ps = [P(w, L) for L in leaves]
    # P(R) >= P(AND L) >= 1 - sum doubt
    assert P(w, R) + EPS >= P(w, conj) >= frechet_lb(ps) - EPS
    # the conjunction (not R) is bounded above by the smallest leaf
    assert P(w, conj) <= min(ps) + EPS
    # interval leaves: the bound computed from the lower ends is still valid
    lows = [p * rng.uniform(0, 1) for p in ps]
    assert P(w, R) + EPS >= frechet_lb(lows)


def test_min_leaf_is_not_an_upper_bound_on_the_root():
    # Retracted statement: P(R) <= min_i P(L_i). Counterexample: R is certain, the leaf is not.
    w = np.array([0.5, 0.5])
    L = np.array([True, False])
    R = np.array([True, True])  # L ⊆ R, so Entails({L}, R) holds
    assert P(w, R) == 1.0 > P(w, L) == 0.5


@settings(max_examples=200, deadline=None)
@given(SEEDS, st.integers(1, 7))
def test_frechet_bound_is_attained(seed, n):
    """Given only the marginals and one entailment, 1 - sum doubt is the best possible bound.
    Case sum doubt <= 1: attained by pairwise disjoint failure events."""
    rng = np.random.default_rng(seed)
    doubts = rng.dirichlet(np.ones(n + 1))[:n] * rng.uniform(0, 1)  # sum of doubts <= 1
    # outcomes: one failure region per leaf (pairwise disjoint), plus "all leaves hold"
    w = np.append(doubts, 1 - doubts.sum())
    leaves = [np.array([j != i for j in range(n + 1)]) for i in range(n)]
    R = np.logical_and.reduce(leaves)  # R = AND L, the least root the entailment permits
    ps = [P(w, L) for L in leaves]
    assert abs(P(w, R) - frechet_lb(ps)) < 1e-9


@settings(max_examples=200, deadline=None)
@given(SEEDS, st.integers(2, 7))
def test_frechet_bound_is_attained_when_doubt_exceeds_one(seed, n):
    """Case sum doubt > 1: the bound is 0; disjoint failures cannot exist (they would need mass > 1),
    so zero is attained by failure arcs laid end to end around [0, 1), which cover the space."""
    rng = np.random.default_rng(seed)
    doubts = rng.uniform(0, 1, n)
    if doubts.sum() <= 1:
        doubts = doubts / doubts.sum() * rng.uniform(1.0001, n)
        doubts = np.minimum(doubts, 1.0)
    if doubts.sum() <= 1:
        doubts[0] = 1.0
    starts = np.concatenate([[0.0], np.cumsum(doubts)[:-1]]) % 1.0
    ends = (starts + doubts) % 1.0
    cuts = np.unique(np.concatenate([[0.0, 1.0], starts, ends]))
    w = np.diff(cuts)
    mids = (cuts[:-1] + cuts[1:]) / 2

    def fails(i):
        a, d = starts[i], doubts[i]
        return ((mids - a) % 1.0) < d

    leaves = [~fails(i) for i in range(n)]
    R = np.logical_and.reduce(leaves)  # R = AND L
    ps = [P(w, L) for L in leaves]
    assert all(abs(p - (1 - d)) < 1e-9 for p, d in zip(ps, doubts))
    assert frechet_lb(ps) == 0.0
    assert P(w, R) < 1e-9  # attained: the failure events cover the space


# ---------------------------------------------------------------- §2.6 calibration of the bound


def test_marginal_leaf_calibration_does_not_validate_selected_bounds():
    """Reviewer's counterexample. Three equally likely strata; forecasts per stratum and true leaf
    frequencies. Each leaf is marginally calibrated, yet among roots with LB >= 0.8 the root holds
    only 60% of the time."""
    forecasts = [(0.9, 0.9), (0.9, 0.1), (0.1, 0.9)]
    freqs = [(0.8, 0.8), (1.0, 0.1), (0.1, 1.0)]
    # marginal calibration of each leaf: P(L_i | f_i = v) = v
    for i in range(2):
        for v in {f[i] for f in forecasts}:
            cells = [k for k, f in enumerate(forecasts) if f[i] == v]
            assert math.isclose(sum(freqs[k][i] for k in cells) / len(cells), v)
    selected = [k for k, f in enumerate(forecasts) if frechet_lb(f) >= 0.8 - EPS]
    assert selected == [0]
    # stratum 0 as a finite space with disjoint failures: fail L1 .2, fail L2 .2, both hold .6
    w = np.array([0.2, 0.2, 0.6])
    L1 = np.array([False, True, True])
    L2 = np.array([True, False, True])
    assert math.isclose(P(w, L1), freqs[0][0]) and math.isclose(P(w, L2), freqs[0][1])
    R = L1 & L2
    assert math.isclose(P(w, R), 0.6) and P(w, R) < frechet_lb(forecasts[0]) - 0.1


@settings(max_examples=200, deadline=None)
@given(SEEDS, st.integers(1, 5), st.integers(2, 8), st.sampled_from([0.6, 0.7, 0.8, 0.9]))
def test_conditionally_valid_leaves_validate_selected_bounds(seed, n, strata, t):
    """If in every forecast cell each leaf's true probability is >= its forecast low, then among
    roots selected by LB >= t the root holds with frequency >= t (in expectation)."""
    rng = np.random.default_rng(seed)
    weight = rng.dirichlet(np.ones(strata))
    num = den = 0.0
    for k in range(strata):
        m = int(rng.integers(2, 20))
        w = rand_space(rng, m)
        leaves = [rand_event(rng, m, rng.uniform(0.7, 1.0)) for _ in range(n)]
        R = entailed_root(rng, np.logical_and.reduce(leaves))
        lows = [P(w, L) * rng.uniform(0.9, 1.0) for L in leaves]  # conditionally valid in cell k
        if frechet_lb(lows) >= t:
            num += weight[k] * P(w, R)
            den += weight[k]
    if den > 0:
        assert num / den + EPS >= t


# ---------------------------------------------------------------- §2.4 graphs, shared leaves


@settings(max_examples=400, deadline=None)
@given(SEEDS, st.integers(2, 40))
def test_dag_with_shared_leaf_flattened_and_recursive_bounds(seed, m):
    """C1 <= {L1,L2}, C2 <= {L2,L3}, R <= {C1,C2}; alternative derivation R <= {L2,L4}."""
    rng = np.random.default_rng(seed)
    w = rand_space(rng, m)
    L1, L2, L3, L4 = (rand_event(rng, m, rng.uniform(0.6, 1.0)) for _ in range(4))
    C1 = entailed_root(rng, L1 & L2)
    C2 = entailed_root(rng, L2 & L3)
    R = (C1 & C2) | (L2 & L4) | (rng.random(m) < 0.1)
    p = {k: P(w, v) for k, v in dict(L1=L1, L2=L2, L3=L3, L4=L4).items()}
    flat = frechet_lb([p["L1"], p["L2"], p["L3"]])  # each distinct leaf counted once
    rec = frechet_lb([frechet_lb([p["L1"], p["L2"]]), frechet_lb([p["L2"], p["L3"]])])
    alt = frechet_lb([p["L2"], p["L4"]])
    assert rec <= flat + EPS  # recursion double-counts L2's doubt: sound but looser
    assert P(w, R) + EPS >= flat
    assert P(w, R) + EPS >= rec
    assert P(w, R) + EPS >= max(flat, alt)  # max over certified derivations


def test_noisy_or_over_derivations_unsound_with_shared_leaf():
    # Two derivations {L1, L2} and {L2, L3} with L1 = L3 = certain; both hinge on L2.
    w = np.array([0.5, 0.5])
    L2 = np.array([True, False])
    top = np.array([True, True])
    R = (top & L2) | (L2 & top)  # least root: R = L2
    p1 = p2 = frechet_lb([1.0, P(w, L2)])  # 0.5 each
    noisy_or = 1 - (1 - p1) * (1 - p2)  # 0.75
    assert P(w, R) == 0.5 < noisy_or
    assert P(w, R) >= max(p1, p2)  # the sound combination


@settings(max_examples=300, deadline=None)
@given(SEEDS, st.integers(2, 12), st.integers(2, 12))
def test_noisy_or_sound_when_derivation_events_independent(seed, m1, m2):
    rng = np.random.default_rng(seed)
    w1, w2 = rand_space(rng, m1), rand_space(rng, m2)
    w = np.outer(w1, w2).ravel()  # product space: coordinate 1 independent of coordinate 2
    A = [rand_event(rng, m1) for _ in range(2)]
    B = [rand_event(rng, m2) for _ in range(2)]
    lift1 = lambda e: np.repeat(e, m2)  # noqa: E731
    lift2 = lambda e: np.tile(e, m1)  # noqa: E731
    D1 = lift1(A[0] & A[1])
    D2 = lift2(B[0] & B[1])
    R = D1 | D2 | (rng.random(m1 * m2) < 0.05)
    lb1 = frechet_lb([P(w1, a) for a in A])
    lb2 = frechet_lb([P(w2, b) for b in B])
    assert P(w, R) + EPS >= 1 - (1 - lb1) * (1 - lb2)


# ---------------------------------------------------------------- independence of leaves


def independent_block_space(rng, s: int, m: int):
    """Omega = {0,1}^s x [m]. The s block leaves are mutually independent; the extra coordinate
    has an arbitrary conditional law given the block, so other leaves may depend on the block."""
    ps = rng.uniform(0.3, 1.0, s)
    rows = []
    for bits in itertools.product([0, 1], repeat=s):
        pb = math.prod(ps[i] if b else 1 - ps[i] for i, b in enumerate(bits))
        rows.append(pb * rng.dirichlet(np.ones(m)))
    w = np.concatenate(rows)
    bits = np.array(list(itertools.product([0, 1], repeat=s))).repeat(m, axis=0).astype(bool)
    block = [bits[:, i] for i in range(s)]
    return w, ps, block


@settings(max_examples=300, deadline=None)
@given(SEEDS, st.integers(1, 5), st.integers(0, 3), st.integers(1, 6))
def test_partial_independence_bound(seed, s, extra, m):
    rng = np.random.default_rng(seed)
    w, ps, block = independent_block_space(rng, s, m)
    n_out = w.shape[0]
    others = [rand_event(rng, n_out, rng.uniform(0.6, 1.0)) for _ in range(extra)]
    for i, L in enumerate(block):
        assert abs(P(w, L) - ps[i]) < 1e-9
    conj = np.logical_and.reduce(block + others)
    R = entailed_root(rng, conj)
    lb = max(0.0, math.prod(ps) + sum(P(w, o) for o in others) - len(others))
    assert P(w, R) + EPS >= lb


def test_independence_product_fails_for_dependent_leaves():
    w = np.full(4, 0.25)
    L1 = np.array([1, 1, 1, 0], bool)
    L2 = np.array([1, 1, 0, 1], bool)
    R = L1 & L2
    assert P(w, R) == 0.5 < P(w, L1) * P(w, L2)  # 0.5625


@settings(max_examples=300, deadline=None)
@given(SEEDS, st.integers(2, 30))
def test_certified_entailment_refutes_independence(seed, m):
    """If A ⊆ B and 0 < P(A), P(B) < 1 then A, B are not independent: a mechanical necessary check."""
    rng = np.random.default_rng(seed)
    w = rand_space(rng, m)
    B = rand_event(rng, m)
    A = B & rand_event(rng, m)
    pa, pb = P(w, A), P(w, B)
    if 1e-6 < pa and pb < 1 - 1e-6:
        assert abs(P(w, A & B) - pa * pb) > 1e-12


# ---------------------------------------------------------------- §2.2 likelihood ratios


def posterior_odds(joint: dict) -> float:
    """joint[(h, e1, e2)] = probability; odds of h=1 given e1=e2=1."""
    return joint[(1, 1, 1)] / joint[(0, 1, 1)]


@settings(max_examples=300, deadline=None)
@given(SEEDS)
def test_lr_product_exact_under_conditional_independence(seed):
    rng = np.random.default_rng(seed)
    prior = rng.uniform(0.05, 0.95)
    q = rng.uniform(0.05, 0.95, size=(2, 2))  # q[h, i] = P(E_i = 1 | H = h)
    joint = {}
    for h, e1, e2 in itertools.product([0, 1], repeat=3):
        ph = prior if h else 1 - prior
        f = lambda i, e: q[h, i] if e else 1 - q[h, i]  # noqa: E731
        joint[(h, e1, e2)] = ph * f(0, e1) * f(1, e2)
    lr = [q[1, i] / q[0, i] for i in range(2)]
    assert math.isclose(posterior_odds(joint), prior / (1 - prior) * lr[0] * lr[1], rel_tol=1e-9)


def test_lr_product_wrong_for_distinct_originators_with_common_cause():
    """Two originators each report independently given (H, Z); Z (say, a shared rumour) is
    independent of H. The originators differ, yet E1, E2 are not independent given H."""
    prior, pz = 0.5, 0.5
    rate = {(0, 0): 0.05, (0, 1): 0.9, (1, 0): 0.6, (1, 1): 0.95}  # P(report | H, Z)
    joint = {k: 0.0 for k in itertools.product([0, 1], repeat=3)}
    for h, z, e1, e2 in itertools.product([0, 1], repeat=4):
        p = (prior if h else 1 - prior) * (pz if z else 1 - pz)
        r = rate[(h, z)]
        p *= (r if e1 else 1 - r) * (r if e2 else 1 - r)
        joint[(h, e1, e2)] += p

    def lik(h, i):
        num = sum(v for (hh, e1, e2), v in joint.items() if hh == h and (e1, e2)[i] == 1)
        return num / sum(v for (hh, _, _), v in joint.items() if hh == h)

    lrs = [lik(1, i) / lik(0, i) for i in range(2)]
    naive = prior / (1 - prior) * lrs[0] * lrs[1]
    true = posterior_odds(joint)
    assert naive > 1.2 * true  # product overcounts the shared cause


# ---------------------------------------------------------------- §2.3 coherence with UNKNOWN


def lp_feasible(atoms: list[tuple[int, ...]], lo, hi) -> bool:
    if not atoms:
        return False
    k = len(lo)
    M = np.array([[a[i] for a in atoms] for i in range(k)], float)
    res = linprog(
        np.zeros(len(atoms)),
        A_ub=np.vstack([M, -M]),
        b_ub=np.concatenate([hi, -np.asarray(lo)]),
        A_eq=np.ones((1, len(atoms))),
        b_eq=[1.0],
        bounds=[(0, None)] * len(atoms),
        method="highs",
    )
    return res.status == 0


def lp_range(atoms, lo, hi, i) -> tuple[float, float]:
    k = len(lo)
    M = np.array([[a[j] for a in atoms] for j in range(k)], float)
    kw = dict(
        A_ub=np.vstack([M, -M]),
        b_ub=np.concatenate([hi, -np.asarray(lo)]),
        A_eq=np.ones((1, len(atoms))),
        b_eq=[1.0],
        bounds=[(0, None)] * len(atoms),
        method="highs",
    )
    mn = linprog(M[i], **kw).fun
    mx = -linprog(-M[i], **kw).fun
    return mn, mx


@settings(max_examples=250, deadline=None)
@given(SEEDS, st.integers(1, 4))
def test_unknown_atoms_kept_possible_is_sound(seed, k):
    rng = np.random.default_rng(seed)
    all_atoms = list(itertools.product([0, 1], repeat=k))
    possible = [a for a in all_atoms if rng.random() < 0.7] or [all_atoms[0]]
    impossible = [a for a in all_atoms if a not in possible]
    # the oracle's view: some possible and some impossible atoms come back UNKNOWN
    unknown = [a for a in all_atoms if rng.random() < 0.3]
    certified_impossible = [a for a in impossible if a not in unknown]
    relaxed = [a for a in all_atoms if a not in certified_impossible]  # the sound rule
    # (1) a truly coherent interval assessment is never reported as violated
    mass = rng.dirichlet(np.ones(len(possible)))
    true_p = np.array([sum(m for a, m in zip(possible, mass) if a[i]) for i in range(k)])
    lo = np.clip(true_p - rng.uniform(0, 0.2, k), 0, 1)
    hi = np.clip(true_p + rng.uniform(0, 0.2, k), 0, 1)
    assert lp_feasible(relaxed, lo, hi)
    # narrowed intervals are outer approximations: they still contain the true values
    for i in range(k):
        mn, mx = lp_range(relaxed, lo, hi, i)
        assert mn - 1e-7 <= true_p[i] <= mx + 1e-7
    # (2) any violation reported by the relaxation is a genuine incoherence
    lo2 = rng.uniform(0, 1, k)
    hi2 = np.minimum(1, lo2 + rng.uniform(0, 0.3, k))
    if not lp_feasible(relaxed, lo2, hi2):
        assert not lp_feasible(possible, lo2, hi2)
    # (3) with no UNKNOWN atoms the relaxation is exact
    if not unknown:
        assert lp_feasible(relaxed, lo2, hi2) == lp_feasible(possible, lo2, hi2)


def test_feasible_with_no_unknown_is_not_necessarily_tight():
    """Zero UNKNOWN atoms makes feasibility exact, but 'coherent (tight)' also needs every endpoint
    unchanged by narrowing. Claims A, B with A ⊆ B certified: atom (A, not B) is impossible."""
    atoms = [(1, 1), (0, 1), (0, 0)]
    lo, hi = np.array([0.5, 0.4]), np.array([0.6, 0.9])
    assert lp_feasible(atoms, lo, hi)  # avoids sure loss, exactly
    mn_b, _ = lp_range(atoms, lo, hi, 1)
    assert mn_b > lo[1] + 0.05  # lo_B narrows from 0.4 to 0.5: not tight


def test_treating_unknown_as_impossible_is_unsound():
    # One claim A; both atoms really possible; oracle returns UNKNOWN on the not-A atom.
    lo = hi = np.array([0.5])
    assert lp_feasible([(1,), (0,)], lo, hi)  # truly coherent
    assert not lp_feasible([(1,)], lo, hi)  # dropping the UNKNOWN atom reports a false violation


# ---------------------------------------------------------------- the design's printed numbers


def test_design_document_numbers():
    # §3 checker report: seven leaves
    p = [0.97, 0.98, 0.88, 0.99, 0.91, 0.97, 0.98]
    doubt = sum(1 - x for x in p)
    assert math.isclose(doubt, 0.32) and math.isclose(frechet_lb(p), 0.68)
    assert math.isclose((1 - p[2]) + (1 - p[4]), 0.21) and 0.21 <= doubt
    S = [0, 1, 3, 5, 6]
    part = math.prod(p[i] for i in S) + p[2] + p[4] - 2
    assert math.isclose(part, 0.6846039564, abs_tol=1e-10)
    # printed lower bounds must be rounded DOWN: 0.684, never 0.685
    assert math.floor(part * 1000) / 1000 == 0.684 and 0.684 <= part < 0.685
    full = math.prod(p)
    assert math.isclose(full, 0.716398848, abs_tol=1e-9) and math.floor(full * 1000) / 1000 == 0.716
    assert part - frechet_lb(p) < 0.005
    # §3 worked example: credit dispute
    q = [0.98, 0.98, 0.85, 0.90, 0.95]
    assert math.isclose(frechet_lb(q), 0.66)
    assert math.isclose(frechet_lb([0.98, 0.98, 0.95, 0.90, 0.95]), 0.76)  # L3 -> 0.95
    # §2.4: seven leaves at 0.95 and at 0.85
    assert math.isclose(frechet_lb([0.95] * 7), 0.65) and frechet_lb([0.85] * 7) == 0.0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
