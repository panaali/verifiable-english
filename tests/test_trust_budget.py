"""The trust budget ratchet on the live tree (architecture decision D3): trusted Lean lines (K, S and
untied [V]) rise only by an allowance the DRI signs, recorded in `docs/trust-baseline.json` by
`tools/trust_map.py --allow --reason ... --signed ...` (the AR-4 format: `budget` and `allowances`).

This is a check of the repository as it stands, not batch evidence (D4), so it always measures the
working tree and never a saved commit. Review F1 of QS-1: the only live comparison sat in a batch
report test, a branch re-pointed it at a saved commit, and S +17 went through the gate unsigned."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from tools import trust_map
from tools.lean_statements import inventory_path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def live():
    current, problems = trust_map.measure(ROOT, ROOT / "tools/trust-classes.json", inventory_path("lean/statements.txt"))
    assert problems == []
    baseline, bad = trust_map.parse_baseline(json.loads((ROOT / "docs/trust-baseline.json").read_text()))
    assert bad == []
    return current, baseline


def test_trust_map_check_passes_on_the_live_tree():
    """Probe F1 of the QS-1 review: the command the gate's owner runs."""
    run = subprocess.run([sys.executable, "tools/trust_map.py", "--check"], cwd=ROOT, capture_output=True,
                         text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PASS: K, S and untied [V] within " in run.stdout


def test_arith_lookup_and_fixture_helpers_are_classified(live):
    """me-12nc F2: the table implementation and all fixture helpers have their intended classes.

    Checking every declaration in the fixture module also catches a newly added helper that was
    omitted from the trust table, instead of relying on today's list of fixture names.
    """
    files, _ = live
    table = files["VE/Arith/TableExamples.lean"]
    assert table["unclassified"] == 0
    assert table["trusted"] == 0
    assert table["T"] > 0
    assert files["VE/Arith/Bounded.lean"]["unclassified"] == 0
    classes = trust_map.load_table(ROOT / "tools/trust-classes.json")
    lookup = {name: cls for name, cls in classes["VE/Arith/Bounded.lean"].items()
              if name == "VE.Arith.Defs.opEnvList" or name.startswith("VE.Arith.OpTable")}
    assert lookup and set(lookup.values()) == {"C"}


def test_every_allowance_is_signed_or_inherited_from_before_ar4(live):
    """An allowance carries the DRI's signature (a standing ruling's included) or the migration's
    marker, which grants nothing new (`tests/test_trust_ratchet.py`)."""
    _, baseline = live
    for entry in baseline["allowances"]:
        assert entry["signature"] == trust_map.UNSIGNED or trust_map.signature_problems(entry["signature"]) == [], entry


@pytest.mark.parametrize("key", trust_map.BUDGET)
def test_one_unsigned_trusted_line_fails_the_live_check(live, key):
    """The check above can fail: against a cap one line below the live tree, one budget key fails
    until a signed allowance grants exactly that line; an allowance of another class grants nothing,
    and the migration's marker is no signature."""
    current, _ = live
    cap = dict(trust_map.budget(trust_map.totals(current)))
    cap[key] -= 1
    failures = trust_map.check(current, cap, [])
    assert len(failures) == 1 and failures[0].startswith(f"{key} grew from ")
    entry = {"class": key, "lines": 1, "reason": "t", "signature": "DRI", "commit": "a" * 40}
    assert trust_map.check(current, cap, [entry]) == []
    other = next(k for k in trust_map.BUDGET if k != key)
    assert trust_map.check(current, cap, [{**entry, "class": other}])
    assert trust_map.signature_problems("") and trust_map.signature_problems(trust_map.UNSIGNED)
