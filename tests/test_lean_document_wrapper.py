"""The new Lean W2 wrapper projection. The Python switch is batch 16b."""
import json

import pytest

from conformance.p0 import environment
from ve.backends.lean_service import LeanService


def document(source, units, **extra):
    front = {"format": "ve-document@1", "environment": environment(), "units": units, **extra}
    return "---\n" + json.dumps(front) + "\n---\n" + source


def unit(uid, span, *, kind="exposition", meaning="specified", support="none", **extra):
    return {"id": uid, "span": span, "kind": kind, "meaning": meaning,
            "support": support, **extra}


@pytest.fixture(scope="module")
def service():
    with LeanService(allow_unlisted_build=True) as instance:
        yield instance


def row(service, source, units, **extra):
    return service.run("document", [{"id": "d", "document": document(source, units, **extra)}])[0]


def test_utf8_partition_status_and_counts(service):
    source = "Café. Next.\n"
    cut = len("Café. ".encode())
    result = row(service, source, [
        unit("a", [0, cut], kind="asserted", support="assumption", content={"ast": ["top"]}),
        unit("b", [cut, len(source.encode())], kind=["unformalised", "future_profile"],
             meaning={"unformalised": "future_profile"}, status="UNFORMALISED")])
    assert result["status"] == "ok"
    assert result["coverage"] == {
        "source_bytes": len(source.encode()), "accounted_bytes": len(source.encode()),
        "coverage_percent": 100, "bytes_by_kind": {"asserted": cut,
                                                       "unformalised": len(source.encode()) - cut},
        "bytes_by_status": {"CHECKED": cut, "UNFORMALISED": len(source.encode()) - cut},
        "unformalised_reasons": {"future_profile": 1},
        "residual": {"open_terms": 0, "assumptions": 1, "bridge_leaves": 0,
                     "unresolved_reading_sets": 0}, "residual_total": 1}


def test_mixed_parent_counts_parts_once(service):
    parts = [unit("a", [0, 1], kind="asserted", content={"ast": ["top"]}, status="CHECKED"),
             unit("b", [1, 3], kind=["unformalised", "opaque"],
                  meaning={"unformalised": "opaque"}, status="UNFORMALISED")]
    result = row(service, "A B", [{"id": "parent", "span": [0, 3],
                                     "status": "MIXED", "parts": parts}])
    assert result["status"] == "ok"
    assert [u["parent_id"] for u in result["units"]] == ["parent", "parent"]
    assert result["coverage"]["accounted_bytes"] == 3
    assert sum(result["coverage"]["bytes_by_status"].values()) == 3


def test_gap_and_wrong_status_are_rejected(service):
    gap = row(service, "AB", [unit("a", [0, 1])])
    assert gap["status"] == "error"
    assert gap["error"] == "unit spans do not partition all source bytes"
    wrong = row(service, "AB", [unit("a", [0, 2], status="CHECKED")])
    assert wrong["status"] == "error"
    assert wrong["error"] == "unit status contradicts content, meaning, or active reading set"


def test_missing_semantic_composition_fails_closed(service):
    result = row(service, "AB", [unit("a", [0, 2])],
                 reading_sets=[{"id": "r", "unit": "a", "version": 1,
                                "status": "open", "readings": []}])
    assert result["status"] == "error"
    assert result["error"].startswith("CheckerUnavailable: document reading sets")
