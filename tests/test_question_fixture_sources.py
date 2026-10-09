"""The G and U acceptance sources stay pinned to the reviewed text."""
from __future__ import annotations

import hashlib
from pathlib import Path
import runpy

from ve.document import _split, load_document


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "usecases/question-answering"
UDHR_SHA256 = "4f4e8c19c66c8232e8e34e03b53897974e5d8679b0adeef78a2fc5f1e2b825dd"


def test_group_source_and_fences_match_reviewed_sentences():
    raw = (FIXTURES / "group.ve.md").read_bytes()
    regenerated = runpy.run_path(str(FIXTURES / "build_group.py"))["build"]().encode()
    assert raw == regenerated
    meta, source, fences = _split(raw)
    assert source.decode() == (
        "Every member is registered.\n"
        "Every member who is registered is eligible.\n"
        "Ann is verified.\n"
    )
    assert [source[u["span"][0]:u["span"][1]].decode().rstrip("\n")
            for u in meta["units"]] == [
                "Every member is registered.",
                "Every member who is registered is eligible.",
                "Ann is verified.",
            ]
    assert [fences[u["id"]].strip() for u in meta["units"]] == [
        "Every member is registered.",
        "Every member who is registered is eligible.",
        "Ann is verified.",
    ]


def test_group_fences_have_the_three_reviewed_lean_readings():
    document = load_document(FIXTURES / "group.ve.md")
    assert [unit["content"] for unit in document["units"]] == [
        ["forall", "member", ["unary", "registered", ["var", 0]]],
        ["forall", "member", ["implies", ["unary", "registered", ["var", 0]],
                              ["unary", "eligible", ["var", 0]]]],
        ["unary", "verified", ["const", "ann"]],
    ]


def test_udhr_copy_is_the_reviewed_pilot_source():
    raw = (FIXTURES / "udhr-part07.ve.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == UDHR_SHA256
    meta, source, _ = _split(raw)
    assert len(meta["units"]) == 19
    assert [u["id"] for u in meta["units"][:2]] == ["u087", "u088"]
    assert meta["units"][-1]["id"] == "u103"
    assert source.startswith(b"4. Everyone has the right to form")


def test_agent_policy_documents_bind_the_selected_source_and_rule_strength():
    root = FIXTURES / "agent-policy"
    variants = {}
    for name in ("a-unspecified", "a-deny", "a-rules", "a-conflict"):
        path = root / f"{name}.ve.md"
        meta, source, _ = _split(path.read_bytes())
        units = meta["units"]
        assert units[0]["span"][0] == 0
        assert units[-1]["span"][1] == len(source)
        assert all(a["span"][1] == b["span"][0] for a, b in zip(units, units[1:]))
        assert [u["id"] for u in units[:26]] == [f"rule{i:02}" for i in range(1, 27)]
        assert all(u["kind"] == "norm" and set(u["content"]) == {"norm"} for u in units[:26])
        assert all(u["kind"] == "asserted" and set(u["content"]) == {"ast"} for u in units[26:])
        # The modality in each English rule is preserved in its norm, including
        # rule 14's prohibition and rules 25/26's reporting obligations.
        assert [units[i - 1]["content"]["norm"]["sign"] for i in (3, 14, 25, 26)] == [
            True, False, True, True]
        assert len(units) == (26 if name == "a-rules" else 119)
        variants[name] = units
    conflict = variants["a-conflict"][13]["content"]["norm"]["over"]
    fixed = variants["a-unspecified"][13]["content"]["norm"]["over"]
    assert set(fixed) - set(conflict) == {"write-workspace"}
    assert set(conflict) - set(fixed) == set()
    assert variants["a-deny"][13]["content"] == variants["a-unspecified"][13]["content"]


def test_agent_policy_documents_are_admitted_with_their_record_formulas():
    for name in ("a-unspecified", "a-deny", "a-rules", "a-conflict"):
        document = load_document(FIXTURES / "agent-policy" / f"{name}.ve.md")
        assert all(unit["content"] is not None for unit in document["units"])
        assert not document["meta"].get("reading_sets")


def test_agent_policy_builder_reproduces_the_reviewed_documents():
    builder = runpy.run_path(str(FIXTURES / "agent-policy" / "build.py"))["build"]
    for name in ("a-unspecified", "a-deny", "a-rules", "a-conflict"):
        assert builder(name) == (FIXTURES / "agent-policy" / f"{name}.ve.md").read_text()
