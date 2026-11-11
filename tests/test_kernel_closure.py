"""The kernel boundary's measuring tool (docs/spec/kernel-boundary.md, sections 2 and 6).

These tests cover the Python half: the registry's shape, the line counting, the requests sent to
the Lean half and the saved baseline's consistency. The Lean half (`tools/kernel_closure.lean`)
reads the compiled environment and runs in the gate, not here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import kernel_closure  # noqa: E402

REGISTRY = json.loads((ROOT / "tools/kernel-paths.json").read_text())
BASELINE = json.loads((ROOT / "docs/kernel/closure-baseline.json").read_text())


def test_overlapping_ranges_are_counted_once():
    ranges = [("A", 1, 10), ("A", 5, 12), ("A", 20, 20), ("B", 1, 3), ("A", 2, 3)]
    assert kernel_closure.covered(ranges) == 12 + 1 + 3
    assert kernel_closure.covered([]) == 0
    assert kernel_closure.covered([("A", 7, 7), ("A", 7, 7)]) == 1


def test_every_path_names_its_entry_theorems_and_subject():
    names = [path["name"] for path in REGISTRY["paths"]]
    assert len(names) == len(set(names))
    for path in REGISTRY["paths"]:
        assert path["tier"] in {"kernel", "candidate"}, path["name"]
        assert path["entry"] and path["theorems"] and path["subject"], path["name"]
        assert len(path["theorems"]) == len(set(path["theorems"])), path["name"]
        for exit_ in path.get("nonverdict", []):
            assert exit_["name"] and len(exit_["why"]) > 20, path["name"]
    assert REGISTRY["verdict_tokens"] == sorted(set(REGISTRY["verdict_tokens"]), key=REGISTRY["verdict_tokens"].index)


def test_the_requests_leave_the_subject_unread_and_cut_the_wrap_at_it():
    path = {"name": "p", "entry": ["E"], "theorems": ["T"], "subject": ["S"], "delegates": ["D"],
            "nonverdict": [{"name": "N", "why": "a reviewed exit that carries no verdict"}]}
    spec, wrap = kernel_closure.requests({"paths": [path]})
    assert spec == {"name": "spec:p", "roots": ["T"], "opaque": ["S"]}
    assert wrap == {"name": "wrap:p", "roots": ["E"], "opaque": ["S", "D", "N"], "mode": "run"}
    *_, body = kernel_closure.requests({"paths": [dict(path, tier="kernel")]})
    assert body == {"name": "body:p", "roots": ["S"], "opaque": [], "mode": "run"}


def test_fixture_modules_are_not_verdict_writers():
    assert kernel_closure.is_fixture("VE.Service.DocumentChainChecks")
    assert kernel_closure.is_fixture("VE.Compose.Examples")
    assert kernel_closure.is_fixture("ResponseShape.Schemas.NormDefaults")
    assert not kernel_closure.is_fixture("VE.Service.Document")


def test_the_saved_baseline_is_of_this_registry():
    """The baseline was measured with this registry: same paths, same tiers, and the kernel total
    is at least its largest kernel path and at most the sum of them."""
    saved = {row["name"]: row for row in BASELINE["paths"]}
    assert set(saved) == {path["name"] for path in REGISTRY["paths"]}
    for path in REGISTRY["paths"]:
        assert saved[path["name"]]["tier"] == path["tier"]
        assert saved[path["name"]]["theorems"] == len(path["theorems"])
    kernel = [row["lines"] for row in saved.values() if row["tier"] == "kernel"]
    assert max(kernel) <= BASELINE["kernel_lines"] <= sum(kernel)
    assert BASELINE["problems"] == []


def test_the_kernel_is_within_the_signed_total():
    """Section 6: the kernel total rises only with the architect's signature (docs/kernel/ALLOWANCES.md)."""
    signed = int((ROOT / "docs/kernel/ALLOWANCES.md").read_text().split("signed total:")[1].split()[0].replace(",", ""))
    assert BASELINE["kernel_lines"] <= signed
