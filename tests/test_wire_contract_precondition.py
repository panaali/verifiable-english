"""Ground the S3-pre inherited-profile discrepancy with a reachable case."""

import json
import subprocess

from tests.test_soft_norms_lean import LEAN, env, should
from ve.errors import VEError
from ve.softnorms import load_soft_document


def test_norm_defaults_profile_rejects_on_both_soft_routes():
    environment = env(profiles=("norms@0", "norm-defaults@0", "soft-norms@0"))
    cases = []
    for index, norms in enumerate(([], [should("a", "x_required", True)])):
        try:
            load_soft_document(environment, norms)
        except VEError as error:
            assert error.code == "SOFT_UNSUPPORTED_PROFILE"
            assert "norm-defaults@0" in str(error)
        else:
            raise AssertionError("Python accepted the probe")
        cases.append({"id": f"norm-defaults-reach-{index}", "kind": "soft-elaborate",
                      "environment": environment, "norms": norms})
    result = subprocess.run([str(LEAN), "-"], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=180, check=False)
    assert result.returncode == 1, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    for row in rows:
        assert row["status"] == "error"
        assert row["code"] == "SOFT_UNSUPPORTED_PROFILE"
        assert "norm-defaults@0" in row["error"]
