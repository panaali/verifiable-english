"""ap-2's raw cap and step budget stay provisional while the plan's condition for dropping the word fails (review F2).

The act-phrases plan (`docs/spec/act-phrases-PLAN.md` 11, deferred item 5) drops "provisional" from N and the step
budget only after a re-measurement with vocabularies written by someone other than the person measuring. ap-2's
measurement (`docs/act-phrases/ap-2/evidence/n-measurement.json`, saved evidence) does not meet it: R rests on AP-0's
registered rows alone, since every M1 row has raw 0, and S on an M1 row whose frame the measurer's rule wrote. So
`rawCap` and `stepBudget` must say "provisional", and nothing of ap-2 may say they no longer are.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/act-phrases/ap-2/evidence/n-measurement.json"
READ = ROOT / "lean/VE/Acts/Read.lean"
PLAN = ROOT / "docs/spec/act-phrases-PLAN.md"


def _docstring(source: str, name: str) -> str:
    match = re.search(r"/--((?:(?!-/).)*)-/\s*def " + name + r" ", source, re.S)
    assert match, f"{name} has no docstring"
    return match.group(1)


def _independent(data: dict) -> bool:
    """Whether R and S rest on rows whose vocabulary the measurer did not write: the registered rows only."""
    rows = {row["id"]: row for row in data["rows"]}
    return all(rows[i]["source"].endswith("(registered)") and not rows[i]["kind"].startswith("m1-")
               for i in data["R_rows"] + data["S_rows"]) and any(
        row["raw"] > 0 for row in rows.values() if row["kind"].startswith("m1-"))


def test_the_saved_measurement_does_not_meet_the_plans_condition():
    data = json.loads(EVIDENCE.read_text())
    rows = {row["id"]: row for row in data["rows"]}
    m1 = [row for row in rows.values() if row["kind"].startswith("m1-")]
    assert m1 and all(row["raw"] == 0 for row in m1)
    assert all(rows[i]["source"].endswith("(registered)") for i in data["R_rows"])
    assert any(rows[i]["kind"].startswith("m1-") for i in data["S_rows"])
    assert not _independent(data)


def test_the_plan_still_lists_the_condition():
    row = next(line for line in PLAN.read_text().splitlines() if line.startswith("| 5 | Re-measuring R and S"))
    assert "written by someone other than the person measuring" in row and 'dropping "provisional"' in row


def test_the_limits_say_provisional_while_the_condition_fails():
    data = json.loads(EVIDENCE.read_text())
    source = READ.read_text()
    if not _independent(data):
        for name in ("rawCap", "stepBudget"):
            assert "provisional" in _docstring(source, name), name
        for path in [*(ROOT / "docs/act-phrases/ap-2").glob("*.*"), *(ROOT / "lean/VE/Acts").glob("*.lean")]:
            assert "no longer provisional" not in path.read_text(), path
