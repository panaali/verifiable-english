"""Tests of the one bridge script (run: python3 -I usecases/gitlab_relocation/bridge/test_bridge.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge as B  # noqa: E402

assert B.anniversary("2026-03-15") == "2027-03-15"
assert B.anniversary("2027-02-28") == "2028-02-28"          # into a leap year: the same day
assert B.anniversary("2028-03-01") == "2029-03-01"
assert B.anniversary("2027-12-31") == "2028-12-31"
assert B.anniversary("2028-02-28") == "2029-02-28"
try:
    B.anniversary("2028-02-29")
    raise SystemExit("FAIL: 29 February must be refused")
except ValueError:
    pass
print("bridge tests: 6 passed")
