"""The 11b report's measured numbers are generated from its gate artifacts."""
from __future__ import annotations

import subprocess
import sys

from subprocesses import HANG_TIMEOUT
from test_speech_acts_lean import ROOT


def test_batch_report_metrics_match_evidence():
    check = subprocess.run([sys.executable, "docs/lean-first/b11b/report.py"], cwd=ROOT,
                           capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert check.returncode == 0, check.stdout + check.stderr
