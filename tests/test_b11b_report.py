"""The 11b report's measured numbers are generated from its gate artifacts."""
from __future__ import annotations

import json
import subprocess
import sys

from subprocesses import HANG_TIMEOUT
from test_speech_acts_lean import ROOT


def test_batch_report_metrics_match_evidence():
    check = subprocess.run([sys.executable, "docs/lean-first/b11b/report.py"], cwd=ROOT,
                           capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert check.returncode == 0, check.stdout + check.stderr
    here = ROOT / "docs/lean-first/b11b"
    availability = json.loads((here / "evidence/speech-availability.json").read_text())
    assert len(availability) == 3
    assert all(row["dri_signature"] == "DRI signoff: DELTA.md, commit 50b5a23b, 2026-10-07"
               for row in availability)
    assert "signed by the DRI 2026-10-07" in (here / "DELTA.md").read_text()
