"""The trust budget ratchet on the live tree (architecture decision D3): trusted Lean lines (K, S and
untied [V]) rise only by an allowance the DRI signs in the same merge, recorded in
`docs/trust-baseline.json` by `tools/trust_map.py --write`.

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

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def live():
    current, problems = trust_map.measure(ROOT, ROOT / "tools/trust-classes.json", ROOT / "lean/statements.txt")
    assert problems == []
    return current, json.loads((ROOT / "docs/trust-baseline.json").read_text())


def test_trust_map_check_passes_on_the_live_tree():
    """Probe F1 of the QS-1 review: the command the gate's owner runs."""
    run = subprocess.run([sys.executable, "tools/trust_map.py", "--check"], cwd=ROOT, capture_output=True,
                         text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "PASS: K, S and untied [V] within the baseline" in run.stdout


def test_the_baseline_is_the_live_tree_with_every_signature_recorded(live):
    """A signed change runs `--write`, which moves its entry into `history` and records the tree, so a
    merged tree equals its baseline and leaves no entry pending."""
    current, baseline = live
    assert trust_map.check(current, baseline) == []
    assert baseline["files"] == current
    assert baseline["signed"] == []
    assert baseline["totals"] == trust_map.totals(current)


@pytest.mark.parametrize("key", ["K", "S", "V"])
def test_one_unsigned_trusted_line_fails_the_live_check(live, key):
    """The check above can fail: against a baseline one line below the live tree, one budget key
    fails until a signed entry allows exactly that line, and an entry without a signature allows nothing."""
    current, _ = live
    totals = dict(trust_map.totals(current))
    totals["trusted"] -= 1
    if key in ("K", "S"):
        totals[key] -= 1
    lower = {"totals": totals, "files": current, "signed": []}
    failures = trust_map.check(current, lower)
    assert len(failures) == 1 and failures[0].startswith(f"{key} grew from ")
    assert trust_map.check(current, {**lower, "signed": [{"change": "t", "signed": "DRI", "allow": {key: 1}}]}) == []
    assert trust_map.check(current, {**lower, "signed": [{"change": "t", "signed": "", "allow": {key: 1}}]})
    other = next(k for k in ("K", "S", "V") if k != key)
    assert trust_map.check(current, {**lower, "signed": [{"change": "t", "signed": "DRI", "allow": {other: 1}}]})
