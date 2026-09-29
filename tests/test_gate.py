"""The full gate must reject missing coverage while honoring exact optional cases."""
import json

from tools.gate import REQUIRED_FAMILIES, ROOT, interpret_pytest, permitted


def test_exact_parameterized_skip_and_live_deselection_are_accounted_for():
    policy = json.loads((ROOT / "tools/gate-optional.json").read_text())
    admission = "tests/test_p0_three_way.py::test_rust_matches_expected[admission]"
    live = "tests/test_llm.py::test_live_smoke"
    assert permitted(admission, "Skipped: admission is outside Rust scope",
                     policy["optional_tests"])
    assert not permitted(admission.replace("admission", "labels"),
                         "Skipped: admission is outside Rust scope", policy["optional_tests"])
    selected = [f"tests/{name}::test_covered" for name in REQUIRED_FAMILIES] + [admission]
    events = {"collected": selected + [live], "selected": selected,
              "deselected": [live], "collection_reports": [],
              "tests": {node: {"outcome": "passed"} for node in selected[:-1]} |
                       {admission: {"outcome": "skipped", "reason": "Skipped: admission is outside Rust scope"}}}
    result = {"counts": {}, "skips": [], "failures": []}
    interpret_pytest(result, events, policy, events["collected"])
    assert not result["failures"]
    assert result["counts"]["selected"] == len(selected)
    assert result["counts"]["deselected"] == 1
    assert {row["nodeid"] for row in result["skips"]} == {admission, live}
