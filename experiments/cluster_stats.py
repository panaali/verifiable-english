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


def planning_power(clusters=24, *, dev_template_sd=None, dev_clusters=None):
    """No assumed reviewer SD: measured dev template means are required."""
    if clusters < 2:
        raise ValueError("At least two planned template clusters are required")
    if dev_template_sd is None:
        return {"status": "PLACEHOLDER_REQUIRES_DEV_PILOT_VARIANCE", "ready_to_freeze": False,
                "clusters": clusters, "dev_clusters": None, "dev_template_sd": None,
                "standard_error": None, "half_width_95": None, "approximate_mde_80": None,
                "required_action": "Run experiments.E5.calibrate_power on complete paired dev trials for the selected judge/difficulty/style before freezing; never reuse the reviewer's assumed SD."}
    if dev_clusters is None or dev_clusters < 2 or not 0 <= dev_template_sd < float("inf"):
        raise ValueError("Finite nonnegative SD from at least two dev templates is required")
    se = dev_template_sd / sqrt(clusters)
    critical = float(t.ppf(.975, clusters-1))
    return {"status": "DEV_VARIANCE_ESTIMATE_REQUIRES_FREEZE_REVIEW", "ready_to_freeze": False,
            "clusters": clusters, "dev_clusters": dev_clusters, "dev_template_sd": dev_template_sd,
            "standard_error": se, "half_width_95": critical*se,
            "approximate_mde_80": (critical + float(norm.ppf(.80))) * se,
            "method": "Observed SD of paired dev template means / sqrt(planned K); t critical + normal 80% quantile; planning approximation, not simulated power",
            "limitations": "Only dev templates estimate variance; floor/ceiling or zero pilot variance does not establish sensitivity. Review the capability gate and variance uncertainty before committing a freeze amendment."}


if __name__ == "__main__":
    import json
    from pathlib import Path
    result = planning_power()
    (Path(__file__).parent / "E5/power.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
