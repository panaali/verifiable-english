"""Equal-weight paired cluster-t intervals; never resample trials as clusters."""
from collections import defaultdict
from math import sqrt
from statistics import mean, stdev
from scipy.stats import t, norm


def cluster_t(effects, *, confidence=.95):
    """effects is iterable of (structural template, paired contrast).

    Aggregate vocabularies/items/samples inside each template, then use a t
    interval on complete template means. Callers must retain assigned failures
    with worst-case outcomes and form paired contrasts BEFORE this function.
    """
    groups = defaultdict(list)
    for cluster, effect in effects:
        groups[cluster].append(effect)
    if len(groups) < 2:
        raise ValueError("At least two independent template clusters are required")
    averages = [mean(values) for values in groups.values()]
    estimate, n = mean(averages), len(averages)
    se = stdev(averages) / sqrt(n)
    half = float(t.ppf((1 + confidence) / 2, n-1)) * se
    return {"estimate": estimate, "clusters": n, "df": n-1, "standard_error": se,
            "interval": [estimate-half, estimate+half], "method": "equal-weight paired template-cluster t"}


def planning_power(clusters=24):
    se = .06 * sqrt(8/clusters)
    critical = float(t.ppf(.975, clusters-1))
    return {"clusters": clusters, "bad_items_per_template_per_difficulty": 8,
            "assumed_false_approval": .40, "assumed_discordant_pairs": .20,
            "reviewer_reference_clusters": 8, "reviewer_reference_standard_error": .06,
            "standard_error": se, "half_width_95": critical*se,
            "approximate_mde_80": (critical + float(norm.ppf(.80))) * se,
            "method": "reviewer SE scaled by sqrt(8/K); t critical + normal 80% quantile; planning approximation, not simulated power"}


if __name__ == "__main__":
    import json
    from pathlib import Path
    result = planning_power()
    (Path(__file__).parent / "E5/power.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
