import json

import pytest

from conformance.p0 import environment
from ve.document import check_document, coverage, load_document, render_document
from ve.errors import VEError
from ve.readings import plan_choices


def write_doc(tmp_path, text, units, **extra):
    front = {"format": "ve-document@1", "environment": environment(), "units": units, **extra}
    path = tmp_path / "sample.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + text)
    return path


def unit(uid, start, stop, kind="asserted", meaning="specified", content=None):
    return {"id": uid, "span": [start, stop], "kind": kind, "meaning": meaning,
            "support": "assumption", "content": content}


def test_byte_partition_and_vacuity(tmp_path):
    source = "Café. Next.\n".encode()
    cut = len("Café. ".encode())
    path = write_doc(tmp_path, source, [unit("a", 0, cut, content={"ast": ["top"]}),
                                        unit("b", cut, len(source), ["unformalised", "future_profile"],
                                             {"unformalised": "future_profile"})])
    doc = load_document(path)
    report = coverage(doc)
    assert report["source_bytes"] == report["accounted_bytes"] == len(source)
    assert report["unformalised_reasons"] == {"future_profile": 1}
    assert check_document(path)["premises"]["status"] == "model"
    assert "Café" in render_document(path)


@pytest.mark.parametrize("spans", [[[0, 2], [3, 6]], [[0, 4], [3, 6]], [[3, 6], [0, 3]],
                                   [[0, 3], [3, 5]]])
def test_partition_rejects_gaps_overlap_order_and_tail(tmp_path, spans):
    path = write_doc(tmp_path, b"abcdef", [unit("a", *spans[0]), unit("b", *spans[1])])
    with pytest.raises(VEError, match="partition"):
        load_document(path)


def test_utf8_cut_and_nested_kind(tmp_path):
    source = "é".encode()
    nested = ["attributed", "alice", "believes", ["hedged", "likely",
              ["causal", "because", "asserted", "asserted"]]]
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), nested, content={"ast": ["top"]})])
    assert load_document(path)["units"][0]["kind"] == nested
    path = write_doc(tmp_path, source, [unit("a", 0, 1), unit("b", 1, 2)])
    with pytest.raises(VEError, match="UTF-8"):
        load_document(path)


def test_reading_route_never_disjoins_mixed_kinds():
    assertions = [{"id": str(i), "readings": [{"kind": "asserted", "content": ["top"]}] * 2}
                  for i in range(12)]
    assert plan_choices(assertions)["route"] == "assertion-disjunction"
    mixed = [{"id": str(i), "readings": [{"kind": "norm", "content": None},
                                            {"kind": ["unformalised", "open_term"], "content": None}]}
             for i in range(7)]
    assert plan_choices(mixed[:1])["route"] == "enumerate"
    assert len(plan_choices(mixed[:1])["choices"]) == 2
    assert plan_choices(mixed)["route"] == "UNKNOWN"


def test_unbound_fence_rejected(tmp_path):
    path = write_doc(tmp_path, b"text\n```ve a\ntrue.\n```\n", [unit("a", 0, 5)])
    with pytest.raises(VEError, match="unbound VE fence"):
        load_document(path)
