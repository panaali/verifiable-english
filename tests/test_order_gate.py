"""Order foundations must not open either existing certificate trust boundary."""
import copy

import pytest

from conformance.certificates import environment, envelope, invoke
from test_lean_conformance import lean_executable
from ve.ast import Top
from ve.entailment import prove_entailment


@pytest.mark.parametrize("profiles", [
    ["order@0", "relational-fol@0"],
    ["closure@0", "order@0", "relational-fol@0"],
])
def test_order_certificates_rejected_at_profile_gate(lean_executable, profiles):
    env = environment()
    certificate = prove_entailment(env, [Top()], Top()).certificate
    baseline = envelope("accepted-v0-control", env, [Top()], Top(), certificate)
    assert invoke(lean_executable, [baseline])[0]["valid"]
    cases = []
    for revision in ("ve-v0.1-order-2026-09-21", "ve-v0.1-closure-2026-09-21"):
        for version in (certificate["checker_version"], "ve-tableau-closure-checker@0",
                        "ve-tableau-order-checker@0"):
            case = copy.deepcopy(baseline)
            case["id"] = f"rejected-{len(cases)}"
            case["environment"].pop("profile")
            case["environment"].update(language="ve.core@0.1", profiles=profiles,
                                       spec_revision=revision)
            case["certificate"]["checker_version"] = version
            cases.append(case)
    results = invoke(lean_executable, cases)
    assert len(results) == len(cases)
    for result in results:
        assert result["status"] == "error" and result["valid"] is False
        assert result["error"] == "unsupported closure environment version/profiles"
