"""et-5b review F1: every `ve document` subcommand admits an `events@0` document Lean's `document` mode checked.

Python builds the document from Lean's answer: the environment Lean's chain read (the row's `events_view`, bound to the
environment as written by `ve.events.view`), with the identities of the environment as written. The check's premise
set holds Lean's events pack (`ve.events.elaborated`); no conclusion route reads it yet (et-5c, DRI 2026-11-10 et-5b
item 2), so a conclusion is `CheckerUnavailable`, never an answer without it. Each test below fails on f1fe61819."""
from __future__ import annotations

import copy
import io
import json
from contextlib import redirect_stdout

import pytest

import ve.backends.relay as relay
from test_events_document import ENVIRONMENT, front, reading_set
from ve.document.cli import main as document_cli
from ve.document.report import EVENTS_CONCLUSION, EVENTS_READINGS_PENDING, check_document
from ve.errors import CheckerUnavailable, VEError

ANCHOR = ["const", "date_of_this_document"]
NAMED = ["const", "date__2030_01_01"]


def _before(a, b):
    return ["binary", "before", a, b]


def _asserted(document, *claims):
    """`document` with one asserted unit per claim after the norm unit, one source byte each."""
    units = document["units"] + [{"id": f"a{i}", "span": [i + 1, i + 2], "kind": "asserted",
                                  "meaning": "specified", "support": "assumption", "content": {"ast": c}}
                                 for i, c in enumerate(claims)]
    return {**document, "units": units}


def _dated(e):
    e["events"]["dates"] = ["2030-01-01"]


def _iso(e):
    del e["vocabulary"]["constants"]["date_of_this_document"]
    e["events"].update(dates=["2026-10-12"], anchor="2026-10-13")


def _environment(*changes):
    e = copy.deepcopy(ENVIRONMENT)
    for change in changes:
        change(e)
    return e


# Every soft-chain document the review's sweep named (open anchor, ISO anchor, an open reading set) and T15's shapes:
# asserted claims over the open anchor and over a named date's constant, which only Lean's view declares.
DOCUMENTS = {
    "open-anchor": front(),
    "iso-anchor": front(_environment(_iso)),
    "reading-set": front(reading_sets=[reading_set("A1")]),
    "t15-open": _asserted(front(), ["exists", "day", ["not", _before(ANCHOR, ["var", 0])]]),
    "t15-dated": _asserted(front(_environment(_dated)), _before(ANCHOR, NAMED)),
}
SUBCOMMANDS = (["check"], ["coverage"], ["readings"], ["render"])


def _text(document) -> str:
    return "---\n" + json.dumps(document) + "\n---\n" + "x" * len(document["units"])


def _run(tmp_path, document, *args, name="d.md"):
    path = tmp_path / name
    path.write_text(_text(document), encoding="utf-8")
    out = io.StringIO()
    with redirect_stdout(out):
        assert document_cli([args[0], str(path), *args[1:]]) == 0
    return out.getvalue()


def _twin(document):
    """The same document over the environment Lean's chain read (its `events_view`): no block, no `events@0`."""
    row, error = _answer(document)
    assert error is None
    return {**document, "environment": row["events_view"]}


def _answer(document):
    """Lean's `document` row and error for `document`, as `ve document check` asks for it."""
    return relay.answer("document", {"id": "d", "document": _text(document), "admit": True})


def test_probe_f1_check_document_counts_the_checked_byte(tmp_path):
    """PROBE F1 (et-5b review): `check_document` of the open-anchor document; at f1fe61819 it was CheckerUnavailable
    (`invalid environment envelope`, Python's soft environment refusing the block)."""
    path = tmp_path / "d.md"
    path.write_text("---\n" + json.dumps(front()) + "\n---\nx", encoding="utf-8")
    assert check_document(path)["coverage"]["bytes_by_status"] == {"CHECKED": 1}


@pytest.mark.parametrize("args", SUBCOMMANDS, ids=lambda a: a[0])
@pytest.mark.parametrize("name", DOCUMENTS)
def test_every_subcommand_admits_a_soft_chain_events_document(tmp_path, name, args):
    """Each subcommand answers for each document. Metamorphic: what it shows is what it shows for the twin over Lean's
    view, but the identities (the written environment's, block and profile included) and the premise status (the
    pack's, below)."""
    document = DOCUMENTS[name]
    shown, twin = _run(tmp_path, document, *args), _run(tmp_path, _twin(document), *args, name="twin.md")
    if args[0] != "check":
        assert shown == twin
        return
    shown, twin = json.loads(shown), json.loads(twin)
    assert shown["source_id"] != twin["source_id"] and shown["document_id"] != twin["document_id"]
    for key in ("source_id", "document_id", "premises"):
        shown.pop(key), twin.pop(key)
    assert shown == twin


def test_the_identities_bind_the_written_environment(tmp_path):
    """`source_id` is Lean's, over the written profiles (`events@0` among them); each unit's meaning id is Lean's."""
    row, _ = _answer(DOCUMENTS["t15-dated"])
    shown = json.loads(_run(tmp_path, DOCUMENTS["t15-dated"], "check"))
    assert (shown["source_id"], shown["document_id"]) == (row["source_id"], row["document_id"])


def test_the_check_premise_set_holds_the_events_pack(tmp_path):
    """"the anchor is before itself": a model without the pack, INCONSISTENT with Lean's irreflexivity premise. At
    f1fe61819 the document was unavailable; built over the view alone it would have been reported as having a model."""
    document = _asserted(front(), _before(ANCHOR, ANCHOR))
    assert json.loads(_run(tmp_path, document, "check"))["premises"]["status"] == "INCONSISTENT"
    assert json.loads(_run(tmp_path, _twin(document), "check", name="twin.md"))["premises"]["status"] == "model"


@pytest.mark.parametrize("extra", [[], ["--assume-no-exception"], ["--under", "rs:0"]],
                         ids=["plain", "assume-no-exception", "under"])
@pytest.mark.parametrize("name", DOCUMENTS)
def test_a_conclusion_over_an_events_document_is_unavailable(tmp_path, name, extra):
    """No conclusion route reads the pack (et-5c): every conclusion path is UNKNOWN, never a verdict without it."""
    conclusion = tmp_path / "c.json"
    conclusion.write_text(json.dumps(["top"]), encoding="utf-8")
    with pytest.raises(CheckerUnavailable) as raised:
        _run(tmp_path, DOCUMENTS[name], "readings", "--conclusion", str(conclusion), *extra)
    assert str(raised.value) == EVENTS_CONCLUSION


def test_the_twin_without_the_block_still_answers_a_conclusion(tmp_path):
    """The other direction: the refusal is the block's, not the soft chain's."""
    conclusion = tmp_path / "c.json"
    conclusion.write_text(json.dumps(["top"]), encoding="utf-8")
    shown = json.loads(_run(tmp_path, _twin(DOCUMENTS["open-anchor"]), "readings", "--conclusion", str(conclusion)))
    assert shown["verdict"] == "ALL"


def test_content_bearing_readings_premises_are_unknown_under_events(tmp_path, monkeypatch):
    """A content-bearing reading set's premises come from the readings route, which reads no pack: UNKNOWN, and the
    route is never asked. Forced on a genuine events document (a content-bearing set needs distinguishing models)."""
    import ve.document.report as report
    import ve.readings_verdicts as verdicts

    def asked(doc):
        raise AssertionError("the readings route answered an events document without its pack")
    import ve.readings_route as readings_route
    monkeypatch.setattr(report, "_content_bearing", lambda doc: True)
    monkeypatch.setattr(verdicts, "context", asked)
    # Coverage's readings lines (composition-s1.md 6) read no premise; they are stubbed with empty lines.
    monkeypatch.setattr(readings_route, "report", lambda doc: {"separations": {}, "findings": {},
                                                                "pending_candidates": 0, "couplings": 0})
    shown = json.loads(_run(tmp_path, DOCUMENTS["t15-dated"], "check"))
    assert shown["premises"] == {"status": "UNKNOWN", "reason": EVENTS_READINGS_PENDING}


def test_a_judgments_events_document_gets_its_twins_refusal(tmp_path):
    """Pre-existing, not et-5b's: Python builds no soft-chain `judgments@0` document, with or without `events@0`
    (`Unsupported profile judgments@0`); the events document gets exactly its twin's refusal."""
    def judged(e):
        e["profiles"] = sorted([*e["profiles"], "documents@1", "judgments@0"])
    document = front(_environment(judged))
    errors = []
    for doc, name in ((document, "d.md"), (_twin(document), "twin.md")):
        with pytest.raises(CheckerUnavailable) as raised:
            _run(tmp_path, doc, "check", name=name)
        errors.append(str(raised.value))
    assert errors[0] == errors[1] and errors[0].endswith("Unsupported profile judgments@0")


def test_ask_over_an_events_document_is_refused_before_any_answer(tmp_path):
    """`ve ask` reads the front matter itself (`ve.ask.environment`) and refuses the block, at base as now: its
    question is an entailment, et-5c's with the conclusion routes."""
    from ve.ask import environment
    with pytest.raises(VEError) as raised:
        environment(_text(front()).encode("utf-8"))
    assert str(raised.value) == "InvalidInput: invalid environment envelope"


# The binding of `events_view` (R8): every member dropped, added, retyped or rebound is CheckerUnavailable.
def _drop(*path):
    def change(v):
        target = v
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
    return change


def _put(value, *path):
    def change(v):
        target = v
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return change


TAMPERED = {
    "dropped": None,
    "null": "null",
    "list": [],
    "language": _put("ve.core@0.1", "language"),
    "language-retyped": _put(True, "language"),
    "spec-revision": _put("x", "spec_revision"),
    "block-kept": _put({"day": "day"}, "events"),
    "extra-member": _put([], "units"),
    "member-dropped": _drop("spec_revision"),
    "events-profile-kept": _put(["events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"],
                                "profiles"),
    "profiles-reordered": _put(["soft-norms@0", "norm-defaults@0", "norms@0", "relational-fol@0"], "profiles"),
    "profile-dropped": _put(["norms@0", "relational-fol@0", "soft-norms@0"], "profiles"),
    "vocabulary-member": _put({}, "vocabulary", "acts"),
    "sort-added": _put({"description": "s"}, "vocabulary", "sorts", "extra"),
    "sort-rebound": _put({"description": "another"}, "vocabulary", "sorts", "day"),
    "predicate-retyped": _put({"arguments": ["day", 1], "description": "before"}, "vocabulary", "predicates", "before"),
    "predicate-dropped": _drop("vocabulary", "predicates", "x_permitted"),
    "constant-added": _put({"sort": "day", "description": "d"}, "vocabulary", "constants", "date__2030_01_02"),
    "constant-dropped": _drop("vocabulary", "constants", "date__2030_01_01"),
    "anchor-dropped": _drop("vocabulary", "constants", "date_of_this_document"),
    "anchor-rebound": _put({"sort": "claude_instance", "description": "the date of this document"},
                           "vocabulary", "constants", "date_of_this_document"),
    "date-sort": _put({"sort": "claude_instance", "description": "2030-01-01"},
                      "vocabulary", "constants", "date__2030_01_01"),
    "date-description": _put({"sort": "day", "description": "2030-01-02"},
                             "vocabulary", "constants", "date__2030_01_01"),
    "date-member": _put({"sort": "day", "description": "2030-01-01", "extra": "x"},
                        "vocabulary", "constants", "date__2030_01_01"),
    "date-retyped": _put({"sort": "day", "description": 20300101}, "vocabulary", "constants", "date__2030_01_01"),
}


def _tampered(monkeypatch, change):
    genuine = relay.answer

    def answer(mode, case, *args, **kwargs):
        row, error = genuine(mode, case, *args, **kwargs)
        if mode == "document" and error is None:
            row = copy.deepcopy(row)
            if change is None:
                row.pop("events_view")
            elif type(change) is str:
                row["events_view"] = None
            elif type(change) is list:
                row["events_view"] = change
            else:
                change(row["events_view"])
        return row, error
    monkeypatch.setattr(relay, "answer", answer)


@pytest.mark.parametrize("name", TAMPERED)
def test_a_tampered_events_view_is_unavailable(tmp_path, monkeypatch, name):
    """Each mutant reaches the hand binding after the shape check (the member's shape is `copied`: bound whole)."""
    document = DOCUMENTS["t15-dated"]
    _run(tmp_path, document, "coverage")  # the genuine answer is built
    _tampered(monkeypatch, TAMPERED[name])
    with pytest.raises(CheckerUnavailable) as raised:
        _run(tmp_path, document, "coverage", name="tampered.md")
    # The view's own binding refuses it (`ve.events.view`), not only a later check its change happens to reach.
    assert "events@0 answer is not bound to its request: the document's events view" in str(raised.value) or (
        "events@0 answer is not bound to its request: " in str(raised.value) and "constant" in str(raised.value))


def test_an_events_view_on_a_document_without_events_is_unavailable(tmp_path, monkeypatch):
    """No row is extra: a view beside an environment that lists no `events@0` is refused."""
    twin = _twin(DOCUMENTS["open-anchor"])
    genuine = relay.answer

    def answer(mode, case, *args, **kwargs):
        row, error = genuine(mode, case, *args, **kwargs)
        return ({**row, "events_view": twin["environment"]} if mode == "document" and error is None else row), error
    monkeypatch.setattr(relay, "answer", answer)
    with pytest.raises(CheckerUnavailable):
        _run(tmp_path, twin, "coverage")
