"""Ground the S3-pre inherited-profile discrepancy with a reachable case."""

import json

from tests import lean_routes
from tests.test_soft_norms_lean import LEAN, env, should
from ve.errors import VEError
from ve.softnorms import load_soft_document


def probe_sources():
    """`env()` under `norm-defaults@0`, with no rule and with one."""
    environment = env(profiles=("norms@0", "norm-defaults@0", "soft-norms@0"))
    return [(environment, norms) for norms in ([], [should("a", "x_required", True)])]


def test_norm_defaults_profile_rejects_on_both_soft_routes():
    cases = []
    for index, (environment, norms) in enumerate(probe_sources()):
        try:
            load_soft_document(environment, norms)
        except VEError as error:
            assert error.code == "SOFT_UNSUPPORTED_PROFILE"
            assert "norm-defaults@0" in str(error)
        else:
            raise AssertionError("Python accepted the probe")
        cases.append({"id": f"norm-defaults-reach-{index}", "kind": "soft-elaborate",
                      "environment": environment, "norms": norms})
    result = lean_routes.completed(LEAN, cases)
    assert result.returncode == 1, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    for row in rows:
        assert row["status"] == "error"
        assert row["code"] == "SOFT_UNSUPPORTED_PROFILE"
        assert "norm-defaults@0" in row["error"]
