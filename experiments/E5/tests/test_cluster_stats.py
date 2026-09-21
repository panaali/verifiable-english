import pytest
from experiments.cluster_stats import cluster_t, planning_power


def test_cluster_interval_preserves_dependence_and_rejects_single_cluster():
    effects = [("a", -.1), ("b", .0), ("c", .2), ("d", .3)]
    base = cluster_t(effects)
    assert base == cluster_t(effects * 100)
    assert base["df"] == 3 and base["clusters"] == 4
    assert base["interval"][0] < base["estimate"] < base["interval"][1]
    with pytest.raises(ValueError):
        cluster_t([("a", .1), ("a", .2)])
    assert .10 < planning_power()["approximate_mde_80"] < .11
