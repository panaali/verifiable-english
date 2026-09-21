import random

from ve_experiments.stats import bootstrap_rate, paired_contrast, rate, summarize, to_markdown


def rows_from(p_approve, n_groups=120, judges=("j1", "j2"), seed=0, fail_every=0):
    """p_approve[(condition, label)] -> approval probability, with a shared per-group difficulty."""
    rng = random.Random(seed)
    rows = []
    k = 0
    for g in range(n_groups):
        shift = rng.uniform(-0.15, 0.15)
        for label in ("good", "bad"):
            for (cond, lab), p in p_approve.items():
                if lab != label:
                    continue
                for j in judges:
                    k += 1
                    approved = rng.random() < min(1, max(0, p + shift))
                    if fail_every and k % fail_every == 0:
                        approved = None
                    rows.append({"item_id": f"{g}-{label}", "group": f"g{g}", "label": label, "condition": cond,
                                 "judge": j, "seed": 0, "approved": approved})  # fmt: skip
    return rows


P = {("fol", "bad"): 0.5, ("ve", "bad"): 0.2, ("fol", "good"): 0.9, ("ve", "good"): 0.9}


def test_rates_and_denominators():
    rows = [
        {"item_id": "a", "group": "a", "label": "bad", "condition": "c", "judge": "j", "approved": True},
        {"item_id": "b", "group": "b", "label": "bad", "condition": "c", "judge": "j", "approved": False},
        {"item_id": "c", "group": "c", "label": "bad", "condition": "c", "judge": "j", "approved": None},
        {"item_id": "d", "group": "d", "label": "good", "condition": "c", "judge": "j", "approved": None},
        {"item_id": "e", "group": "e", "label": "good", "condition": "c", "judge": "j", "approved": True},
    ]
    fa = rate(rows, "false_approval", "c")
    assert (fa.numerator, fa.denominator) == (2, 3)  # the failed bad trial counts as approved
    ha = rate(rows, "honest_acceptance", "c")
    assert (ha.numerator, ha.denominator) == (1, 2)  # the failed good trial counts as rejected
    assert abs(fa.failure_rate - 1 / 3) < 1e-9
    assert rate(rows, "false_approval", "missing").value is None


def test_bootstrap_detects_a_real_difference_and_not_a_null():
    rows = rows_from(P)
    c = paired_contrast(rows, "false_approval", "ve", "fol", n_boot=2000)
    assert c.diff < -0.2 and c.ci_high < 0 and c.n_clusters == 120
    null = paired_contrast(rows, "honest_acceptance", "ve", "fol", n_boot=2000)
    assert null.ci_low < 0 < null.ci_high


def test_bootstrap_ci_contains_point_estimate_and_is_reproducible():
    rows = rows_from(P)
    r1 = bootstrap_rate(rows, "false_approval", "fol", n_boot=1000, seed=3)
    r2 = bootstrap_rate(rows, "false_approval", "fol", n_boot=1000, seed=3)
    assert r1 == r2 and r1.ci_low <= r1.value <= r1.ci_high and 0.02 < r1.ci_high - r1.ci_low < 0.25


def test_bootstrap_coverage_is_roughly_nominal():
    # 95% CI for a true difference of -0.3 should cover it in most of 60 replications
    hits = 0
    for s in range(60):
        c = paired_contrast(rows_from(P, n_groups=60, judges=("j",), seed=s), "false_approval", "ve", "fol", n_boot=400, seed=s)
        hits += c.ci_low <= -0.3 <= c.ci_high
    assert hits >= 50


def test_per_judge_breakdown_and_markdown():
    rows = rows_from(P, fail_every=17)
    assert {r["judge"] for r in summarize(rows, n_boot=50)["rates"]} == {"j1", "j2"}  # no pooled row by default
    s = summarize(rows, contrasts=[("ve", "fol")], n_boot=300, pooled=True)
    judges = {r["judge"] for r in s["rates"]}
    assert judges == {"*", "j1", "j2"}
    assert len(s["rates"]) == 2 * 3 * 2 and len(s["contrasts"]) == 2 * 3
    pooled = next(r for r in s["rates"] if r["judge"] == "*" and r["condition"] == "fol" and r["metric"] == "false_approval")
    per = [r for r in s["rates"] if r["judge"] != "*" and r["condition"] == "fol" and r["metric"] == "false_approval"]
    assert pooled["denominator"] == sum(r["denominator"] for r in per)
    assert pooled["failure_rate"] > 0
    md = to_markdown(s)
    assert "false_approval" in md and "ve - fol" in md


def test_variants_of_one_template_are_one_cluster_and_give_no_p_value():
    # Reviewer's reproduction: ten discordant variants of ONE template must not look like strong evidence.
    rows = []
    for k in range(10):
        for cond, approved in (("fol", True), ("ve", False)):
            rows.append({"item_id": f"v{k}", "group": f"v{k}", "template": "t1", "label": "bad", "condition": cond,
                         "judge": "j", "seed": 0, "approved": approved})  # fmt: skip
    c = paired_contrast(rows, "false_approval", "ve", "fol", "j", n_boot=200, cluster="template")
    assert c.n_clusters == 1 and not hasattr(c, "sign_test_p")
    assert (c.discordant_a_only, c.discordant_b_only) == (0, 10)
    assert c.ci_low == c.ci_high == c.diff == -1.0  # one cluster: the bootstrap cannot express uncertainty, and n_clusters says so


def _rows(cells):
    out = []
    for (item, template, cond), approved in cells.items():
        out.append({"item_id": item, "group": item, "template": template, "label": "bad", "condition": cond,
                    "judge": "j", "approved": approved, "sample": 0})  # fmt: skip
    return out


def test_cluster_t_uses_per_template_differences():
    import pytest as _pytest

    from ve_experiments.stats import cluster_t_contrast

    cells = {}
    for t, (fa_a, fa_b) in {"t1": (1, 3), "t2": (2, 4), "t3": (0, 4)}.items():
        for i in range(4):
            cells[(f"{t}-{i}", t, "a")] = i < fa_a
            cells[(f"{t}-{i}", t, "b")] = i < fa_b
    c = cluster_t_contrast(_rows(cells), "false_approval", "a", "b", "j")
    assert c.n_clusters == 3 and c.per_cluster == {"t1": -0.5, "t2": -0.5, "t3": -1.0}
    assert c.diff == _pytest.approx(-2 / 3)
    half = 4.303 * c.sd / 3**0.5
    assert c.ci_low == _pytest.approx(c.diff - half) and c.ci_high == _pytest.approx(c.diff + half)


def test_incomplete_pairing_is_rejected():
    import pytest as _pytest

    from ve_experiments.stats import PairingError, cluster_t_contrast, paired_contrast

    cells = {("x1", "t1", "a"): True, ("x1", "t1", "b"): False, ("x2", "t2", "a"): True, ("x3", "t2", "b"): True}
    for fn in (cluster_t_contrast, lambda *a: paired_contrast(*a, n_boot=10, cluster="template")):
        with _pytest.raises(PairingError):
            fn(_rows(cells), "false_approval", "a", "b", "j")
