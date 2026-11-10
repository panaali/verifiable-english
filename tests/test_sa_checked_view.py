"""sa-checked-view (docs/spec/purpose-explanation.md 5.1): the typed checked view changes no answer.

On the document-mode fixtures (a plain document, `scope@0` with a reading set governed per choice, a refused request),
`docs/document-model/sa-checked-view/view_bytes.lean` runs `checkDocSets` and `checkDocSetsView` on each request with
`lake env lean`; the view's first component is `checkDocSets`'s answer byte for byte, and both are the answer the
service gives the same request. Lean computes every value; Python only compares them. The statement gate
(`spec_text_check.py`) keeps the eight 5.1 declarations equal to the spec's text.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, ROOT, lean_build
from tests.test_scope_document import F1, _split, _text, _written_in_full
from tests.test_scope_readings_document import _doc, _on_lead
from ve.backends.relay import answer

EVIDENCE = ROOT / "docs/document-model/sa-checked-view"
NORM = "VE.Route.Admission.Kind.norm"


def _cases() -> dict[str, dict]:
    meta, body = _split(F1.read_text())
    return {name: {"id": "d", "document": text, "admit": True} for name, text in {
        "plain": _text(_written_in_full(meta), body),
        "governed": _doc(),
        "refused": _doc(_on_lead),
    }.items()}


@pytest.fixture(scope="module")
def lean_lines(tmp_path_factory):
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    cases = _cases()
    path = tmp_path_factory.mktemp("view") / "cases.jsonl"
    path.write_text("".join(json.dumps(c) + "\n" for c in cases.values()))
    done = subprocess.run([lake, "env", "lean", str(EVIDENCE / "view_bytes.lean")], cwd=LEAN, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT, env={**os.environ, "VE_VIEW_CASES": str(path)})
    assert done.returncode == 0, done.stdout + done.stderr
    lines = [json.loads(line) for line in done.stdout.splitlines() if line.startswith("{")]
    assert len(lines) == len(cases), done.stdout
    return dict(zip(cases, lines)), cases


@pytest.mark.parametrize("name", ["plain", "governed", "refused"])
def test_the_view_first_component_is_check_doc_sets_byte_for_byte_and_the_services(lean_lines, name):
    lines, cases = lean_lines
    line = lines[name]
    assert line["view"] == line["answer"]
    row, error = answer("document", cases[name])
    if name == "refused":
        assert line["answer"] == {"error": "ScopeReadings: u0164.s02"} and "rows_render" not in line
        assert row == {"id": "d", "status": "error", "error": line["answer"]["error"]}
        assert str(error) == line["answer"]["error"]
        return
    assert error is None
    ours = json.loads(line["answer"]["ok"])
    # The service answers `checkDocSetsAnswered`: the same answer, with a governed set's composed rules beside it.
    assert {k: v for k, v in row.items() if k != "composed_readings"} == ours
    assert ("composed_readings" in row) == (name == "governed")
    assert line["rows_render"] is True and line["source_is"] is True
    assert line["pack_sources"] == []


def test_the_governed_rows_are_after_scope_fold(lean_lines):
    """The fixture exercises the governor fold: a row the checked document carries changes under it, and the view's
    rows are the folded ones (the lead-in takes its items' status)."""
    lines, _ = lean_lines
    governed = lines["governed"]
    assert governed["fold_changed"] is True and governed["rows_render"] is True
    units = {u["id"]: u for u in json.loads(governed["answer"]["ok"])["units"]}
    assert units["u0164.s02"]["status"] == "OPEN"
    assert lines["plain"]["fold_changed"] is False


def test_candidates_and_readings_name_the_active_set_in_order(lean_lines):
    lines, _ = lean_lines
    governed = lines["governed"]
    assert governed["readings"] == [["u0165.s03", ["wide", "narrow"]]]
    assert governed["candidates"] == [["u0165.s03", [NORM, NORM]]]
    assert governed["active_kinds"] == governed["candidates"]
    assert lines["plain"]["candidates"] == lines["plain"]["readings"] == lines["plain"]["active_kinds"] == []


def _spec_check(*source: str) -> int:
    return subprocess.run([sys.executable, "-B", str(EVIDENCE / "spec_text_check.py"), *source], cwd=ROOT,
                          capture_output=True, text=True, timeout=HANG_TIMEOUT).returncode


def test_the_eight_statements_equal_the_spec_and_a_changed_one_fails(tmp_path):
    assert _spec_check() == 0
    text = (LEAN / "VE/Service/DocumentView.lean").read_text()
    for old, new in [("ns.length = ks.length", "ns.length ≤ ks.length"),
                     ("V.packSources = [] :=", "V.packSources = [] ∨ True :="),
                     ("activeKinds j = .ok V.candidates", "(activeKinds j).isOk")]:
        assert old in text
        path = tmp_path / f"{len(new)}.lean"
        path.write_text(text.replace(old, new))
        assert _spec_check(str(path)) == 1, new
