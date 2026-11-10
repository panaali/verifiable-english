"""The saved pc-1g trust mutation record has a verdict for every planned mutant."""

from collections import Counter
import json
from pathlib import Path


RECORD = Path(__file__).resolve().parents[1] / "docs/profile-composition/pc-1g/trust-mutants.json"
PLAN_MUTANTS = 331  # The final Lean tree's generated full mutation plan.


def test_pc1g_trust_mutation_record_has_no_unresolved_mutants():
    """Review F2: an allow file alone cannot turn an incomplete saved run into passing evidence."""
    record = json.loads(RECORD.read_text())
    statuses = Counter(row["status"] for row in record["mutants"])
    assert len(record["mutants"]) == PLAN_MUTANTS
    assert set(statuses) <= set(record["counts"])
    assert statuses and record["counts"] == {key: statuses[key] for key in record["counts"]}
    assert "partial" not in record
    assert not any(statuses[key] for key in ("SURVIVOR", "UNKNOWN", "NOT RUN"))
    assert record.get("rescore", {}).get("mode") == "identical"
    assert record["rescore"]["reused"] + record["rescore"]["rerun"] == PLAN_MUTANTS
