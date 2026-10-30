"""The saved mutation run must not waive CSV character regressions."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/math-evidence/me-4"


def test_csv_equality_mutants_are_killed_without_an_allowance() -> None:
    allowances = json.loads((EVIDENCE / "trust-mutants-allow.json").read_text())["allow"]
    assert not any(row["definition"] == "VE.Calc.csvRecords" and row["operator"] == "eq-le"
                   for row in allowances)

    mutants = json.loads((EVIDENCE / "trust-mutants.json").read_text())["mutants"]
    csv_equality = [row for row in mutants if row["definition"] == "VE.Calc.csvRecords"
                    and row["operator"] == "eq-le"]
    assert len(csv_equality) >= 2
    assert all(row["raw_status"] == "KILLED" and row["status"] == "KILLED" for row in csv_equality)
