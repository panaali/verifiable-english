"""kb-2a-b: the document mode on the core document (the architect seat's design for kb-2a, section 3; DRI item 6).

The acceptance document tests/data/kb2a/rsp-mixed.ve.md (RSP units, docs/kernel/kb-2a-b/build_rsp_mixed.py) is
lowered by Lean to one core document per choice of its reading set, admitted by the soft route's kernel row
(`slot-admission`) one row per choice, and its unit statuses are the fold of those rows (`VE.Service.CoreCheck`).
Each refusal test runs a one-edit variation of the same document. Python binds and renders; it decides nothing."""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from ve.backends import relay
from ve.backends.lean_service import CheckerUnavailable
from ve.backends.service_schema import Invalid, check_row
from ve.document import load as load_module
from ve.document.cli import main as document_main
from ve.document.core import bind_core_answer
from ve.document.report import check_document
from ve.document.source import _parts, _split
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "tests/data/kb2a/rsp-mixed.ve.md"
GOLDEN = ROOT / "tests/data/kb2a/rsp-mixed.answer.json"
EVIDENCE = ROOT / "docs/kernel/kb-2a-b"
TEXT = DOC.read_text(encoding="utf-8")
META = json.loads(TEXT[4:TEXT.index("\n---\n")])
BODY = TEXT[TEXT.index("\n---\n") + 5:]
STATUSES = {"intro-aspire-source": "LABELLED", "intro-aspire": "UNFORMALISED", "t1-plan-source": "LABELLED",
            "t1-plan": "OPEN", "t4-name-source": "LABELLED", "t4-name": "CHECKED", "s35-aim-source": "LABELLED",
            "s35-aim": "CHECKED", "s35-disclose-source": "LABELLED", "s35-disclose": "CHECKED",
            "s36-full-review-source": "LABELLED", "s36-full-review": "OPEN"}


def variation(tmp_path, edit) -> Path:
    """The acceptance document with one edit of its front matter, its body unchanged."""
    meta = copy.deepcopy(META)
    edit(meta)
    path = tmp_path / "variation.ve.md"
    path.write_text("---\n" + json.dumps(meta, indent=1, ensure_ascii=False) + "\n---\n" + BODY, encoding="utf-8")
    return path


def unit(meta, uid):
    return next(u for u in meta["units"] if u["id"] == uid)


@pytest.fixture
def lean_only(monkeypatch):
    """Fail if Python's own document path runs; record each answer `_lean_answer` returns."""
    answers = []
    original = load_module._lean_answer

    def spied(*args, **kwargs):
        row = original(*args, **kwargs)
        answers.append(row)
        return row

    def python_path(*args, **kwargs):
        raise AssertionError("Python's own document path decided a document of the core path")

    monkeypatch.setattr(load_module, "_lean_answer", spied)
    monkeypatch.setattr(load_module, "_load_document", python_path)
    return answers


def test_document_check_is_answered_by_lean(lean_only, capsys):
    """Section 3 item 1: `ve document check` exits 0 and is Lean's document mode's answer: `_lean_answer` returned an
    answer and no Python path decided. Each unit's status is the fold's."""
    assert document_main(["check", str(DOC)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert len(lean_only) == 1 and lean_only[0] is not None and set(lean_only[0]) == {"id", "status", "view", "rows"}
    assert report["answered_by"] == "lean core document path"
    assert {u["id"]: u["status"] for u in report["units"]} == STATUSES
    done = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(DOC)], cwd=ROOT, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout) == report


def test_document_answer_is_the_golden_file(lean_only, capsys):
    """Section 3 item 2: the answer carries each unit's status, its core statements per choice with their origins,
    and one admission row per choice; `--json` prints it verbatim, byte for byte the committed golden file."""
    assert document_main(["check", "--json", str(DOC)]) == 0
    out = capsys.readouterr().out
    assert out == GOLDEN.read_text(encoding="utf-8")
    row = json.loads(out)
    view = row["view"]
    assert {u["id"]: u["status"] for u in view["units"]} == STATUSES
    assert view["choices"] == [[{"reading": i, "set": "rs1-t1"}] for i in range(3)]
    assert len(row["rows"]) == len(view["choices"]) == 3
    assert [r["case"]["id"] for r in row["rows"]] == ["choice-0", "choice-1", "choice-2"]
    assert all(r["answer"] == {"id": r["case"]["id"], "status": "ok", "rules": len(r["case"]["norms"]),
                               "facts": len(r["case"]["facts"])} for r in row["rows"])
    statements = {e["id"]: e["choices"] for e in view["statements"]}
    assert set(statements) == {"t1-plan", "t4-name", "s35-aim", "s35-disclose", "s36-full-review"}
    # t1-plan: its judgment term in every choice, then the reading's rule (cond, uncond) or nothing (ov, pending).
    plan = statements["t1-plan"]
    assert [[(s["feature"], s.get("reading")) for s in c] for c in plan] == [
        [("judgments@0", None), ("norms@0", {"index": 0, "set": "rs1-t1"})],
        [("judgments@0", None), ("norms@0", {"index": 1, "set": "rs1-t1"})],
        [("judgments@0", None)]]
    assert all(c == [{"feature": "facts", "premise": ["unary", "listed", ["const", "automated_rd"]]}]
               for c in statements["t4-name"])
    assert all(c[-1]["feature"] == "soft-norms@0" and c[-1]["rule"] == unit(META, "s36-full-review")["content"]
               for c in statements["s36-full-review"])
    load_module._core_document(DOC.read_bytes(), row)


def test_document_lowering_keeps_reading_sets_distinct(tmp_path, lean_only):
    """Section 3 item 5: two readings that lower to the same statements (here `uncond` made pending, like `ov`) are
    refused `ReadingsCollapsed`, by Lean. The answer has no success flag of the lowering at all: the view and its
    statements carry no `admitted`, `success`, `valid` or `verdict` member."""
    def collapse(meta):
        meta["reading_sets"][0]["readings"][1].update(content=None, meaning_id="pending")
    with pytest.raises(VEError) as caught:
        check_document(variation(tmp_path, collapse))
    assert str(caught.value) == "ReadingsCollapsed: reading set rs1-t1 readings 1 and 2 lower to the same statements"
    assert caught.value.lowering is True
    view = json.loads(GOLDEN.read_text())["view"]
    keys = set()

    def walk(value):
        if type(value) is dict:
            keys.update(value)
            for item in value.values():
                walk(item)
        elif type(value) is list:
            for item in value:
                walk(item)
    walk({k: view[k] for k in ("choices", "statements", "units")})
    assert not keys & {"admitted", "success", "valid", "verdict", "lowered", "ok"}


def test_document_lowering_refuses_unknown_part(tmp_path, lean_only):
    """Section 3 item 5: a reading set (an origin's set) naming a unit the document does not have is `UnknownPart`."""
    def missing(meta):
        meta["reading_sets"][0]["unit"] = "no-such-unit"
    with pytest.raises(VEError) as caught:
        check_document(variation(tmp_path, missing))
    assert str(caught.value) == ("UnknownPart: reading set rs1-t1 names unit no-such-unit, which the document does "
                                 "not have")
    assert caught.value.lowering is True


def test_document_lowered_facts_inconsistent_no_verdict(tmp_path, lean_only, capsys):
    """Section 3 item 5: facts p(a) and not p(a) lowered from the document (intro-aspire asserting not listed(T4)
    beside t4-name's listed(T4)) are admitted with no verdict: the answer has neither CONFLICT-FREE nor `valid`; the
    carried case sent to `slot-conflict` and to `slot-certificate` gets kb-3a's refusal of facts with no model."""
    def contradict(meta):
        unit(meta, "intro-aspire").update(kind="asserted", meaning="specified", support="testimony",
                                          content={"ast": ["not", ["unary", "listed", ["const", "automated_rd"]]]})
    path = variation(tmp_path, contradict)
    assert document_main(["check", "--json", str(path)]) == 0
    out = capsys.readouterr().out
    assert "CONFLICT-FREE" not in out and not re.search(r'"valid"', out)
    row = json.loads(out)
    assert [u["status"] for u in row["view"]["units"] if u["id"] in ("intro-aspire", "t4-name")] == ["CHECKED"] * 2
    case = row["rows"][0]["case"]
    negated = ["not", ["unary", "listed", ["const", "automated_rd"]]]
    assert case["facts"] == [negated, ["unary", "listed", ["const", "automated_rd"]]]
    refusal = "InvalidInput: facts need a facts_model: a base model of the background and the facts"
    conflict = {**case, "id": "conflict", "kind": "slot-conflict", "packages": {}}
    certificate = {**case, "id": "certificate", "kind": "slot-certificate", "premises": [], "conclusion": ["top"],
                   "certificate": {}}
    answered = relay.rows("soft-norms", [conflict, certificate])
    assert [r.get("error") for r in answered] == [refusal, refusal]


def test_document_lowering_never_falls_back_to_python(tmp_path, lean_only):
    """Section 3 item 5 and 2.5: a document of the core path that Lean refuses with a `CheckerUnavailable` code (a soft
    rule the soft route rejects: an unknown rank) keeps Lean's refusal as its answer; before kb-2a-b Python's own path
    took any such document."""
    def unknown_rank(meta):
        unit(meta, "s35-aim")["content"]["norm"]["rank"] = "no-such-rank"
    with pytest.raises(CheckerUnavailable) as caught:
        check_document(variation(tmp_path, unknown_rank))
    assert str(caught.value) == ("CheckerUnavailable: a soft source the soft route rejects keeps its loader's "
                                 "diagnostic: UnknownRank: rule f13-minimize-default, no-such-rank")
    assert caught.value.lowering is True


def test_kb2a_python_before_recorded():
    """DRI item 6: what Python decided for the acceptance document before the fallback was removed is recorded, and
    every listed difference from Lean's answer names its cause (a file:line or a rule)."""
    before = json.loads((EVIDENCE / "python-before.json").read_text())
    assert before["exit"] == 5 and before["stdout"]["status"] == "CheckerUnavailable"
    table = (EVIDENCE / "python-vs-lean.md").read_text()
    rows = [line for line in table.splitlines() if line.startswith("| D")]
    assert rows
    for line in rows:
        cells = [c.strip() for c in line.strip("|").split("|")]
        assert len(cells) == 5 and cells[4], line
        assert re.search(r"[\w/.-]+\.(?:lean|py):\d+|rule ", cells[4]), line


# --- R8: the core answer is typed and bound --------------------------------------------------------------------------

def _paths(value, path=()):
    """Each node's path, the environment's vocabulary entered only at its root."""
    yield path
    if path[-1:] == ("vocabulary",):
        return
    if type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, (*path, key))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _paths(item, (*path, index))


def _get(value, path):
    for key in path:
        value = value[key]
    return value


def _set(value, path, new):
    out = copy.deepcopy(value)
    target = out
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = new
    return out


def _refused(row) -> bool:
    try:
        check_row("document", row, {"id": "document", "document": TEXT, "admit": True}, 0)
    except Invalid:
        return True
    raw = DOC.read_bytes()
    _, body, _ = _split(raw)
    try:
        bind_core_answer(META, body, list(_parts(META["units"])), row)
    except CheckerUnavailable:
        return True
    return False


GOLDEN_ROW = json.loads(GOLDEN.read_text())
# Lean's decisions, typed but not bound: each unit's status (its schema enum), the identities and the coverage
# counts, which the bound fields of `_bind_document_answer` and the schema check as the plain answer's.
DECIDED = re.compile(r"^\('view', '(units', \d+, 'status|source_id|document_id|coverage|judgment_lines|judgments)")


def test_core_answer_retyped_fields_are_unavailable():
    """Every member of the core answer retyped (to a value of another JSON type) is refused by the schema or by the
    binding."""
    assert not _refused(GOLDEN_ROW)
    for path in list(_paths(GOLDEN_ROW))[1:]:
        old = _get(GOLDEN_ROW, path)
        new = 7 if type(old) is not int else "7"
        assert _refused(_set(GOLDEN_ROW, path, new)), path


def test_core_answer_rebound_fields_are_unavailable():
    """Every member that names the request (an id, a choice, a reading, a statement, a case's environment, rules and
    facts, an answer's counts) shifted to another value of its type is refused: the answer is about the document
    sent. Statuses and identities are Lean's and only typed."""
    checked = 0
    for path in list(_paths(GOLDEN_ROW))[1:]:
        old = _get(GOLDEN_ROW, path)
        if DECIDED.match(repr(path)) or type(old) not in (str, int, bool):
            continue
        new = (old + 1) if type(old) is int else (not old) if type(old) is bool else old + "x"
        assert _refused(_set(GOLDEN_ROW, path, new)), path
        checked += 1
    assert checked > 100
    rows = GOLDEN_ROW["rows"]
    for changed in ({**GOLDEN_ROW, "rows": rows[:-1]}, {**GOLDEN_ROW, "rows": rows + rows[:1]},
                    {**GOLDEN_ROW, "rows": rows[::-1]}, {**GOLDEN_ROW, "rows": [{**rows[0], "refused": "x"}] + rows[1:]}):
        assert _refused(changed)
