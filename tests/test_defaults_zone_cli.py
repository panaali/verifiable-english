"""`ve document readings PATH --conclusion Q --assume-no-exception` at one situation (batch df-5b; defeasible plan
DF-1b and DF-5, spec 8.6): a question file that names a `situation`, with its `record`, `observations` and `query`,
sends df-5's `defaults-zone` request through `ve.defaults` and prints Lean's bound answer with the DE10, DE10f, DE11
and DE13 English Lean chose, each sentence through W7's all-derivations gate (`ve.defaults_english.Gate`).

The fixtures (tests/data/defaults_zone_cli/) are spec 8.6's cases as documents and question files, each one df-5's
own request (tests/test_defaults_zone.py `CASES`); the CLI's answer is the service mode's for that request. Every
other `--assume-no-exception` call prints what it printed before (`unchanged.json`, recorded with main's Python).
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import functools
import io
import json
from pathlib import Path

import pytest

from tests import test_defaults_zone
from tests.test_defaults_zone import genuine
from ve import defaults, defaults_english
from ve.backends import relay
from ve.document import cli
from ve.document.load import load_document
from ve.errors import UnsupportedProfile, VEError

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests/data/defaults_zone_cli"
# fixture: df-5's case (spec 8.6: DF-μ, DF-μ′, DF-μ″, DF-δz, DF-ξ, DF-ξ′, DF-π′; then a record and X's labels)
FIXTURES = {"df-mu": "mu", "df-mu1": "mu1", "df-mu2": "mu2", "df-delta-z": "delta_z", "df-xi": "xi",
            "df-xi1": "xi1", "df-pi1": "pi1", "record-off": "epsilon_off", "no-completion-labels": "beta_none"}
P1 = "docs/research/evidence/defeasible/baseline/p1-force-u0036-s05.ve.md"
CE4 = "docs/research/evidence/defeasible/baseline/p2-ce4.ve.md"


@functools.lru_cache(maxsize=None)
def _loaded(path):
    return load_document(path)


def _cli(monkeypatch, path, question):
    """What `ve document readings PATH --conclusion QUESTION --assume-no-exception` prints, and the `defaults-zone`
    requests it sent (each document loaded once per session: the document route is not under test here)."""
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(cli, "load_document", lambda p: _loaded(str(p)))
    sent, decide = [], relay.decide
    monkeypatch.setattr(relay, "decide", lambda mode, cases, *a, **k: (
        sent.extend(c for c in cases if c.get("kind") == "defaults-zone") or decide(mode, cases, *a, **k)))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert cli.main(["readings", str(path), "--conclusion", str(question), "--assume-no-exception"]) == 0
    return json.loads(out.getvalue()), sent


def _documents(case):
    """df-5's request as the CLI sends it: the document's environment adds the `documents@1` profile."""
    environment = case["environment"]
    return {**case, "id": "zone",
            "environment": {**environment, "profiles": sorted({*environment["profiles"], "documents@1"})}}


def test_each_fixture_is_df_5s_request():
    """Each fixture's document carries df-5's environment and norms, and its question df-5's situation, record,
    observations and query, unchanged."""
    for name, key in FIXTURES.items():
        case = CASES_OF(key)
        front = json.loads((DATA / f"{name}.ve.md").read_text().split("---\n")[1])
        assert front["environment"] == _documents(case)["environment"]
        assert [unit["content"] for unit in front["units"]] == case["norms"]
        assert json.loads((DATA / f"{name}.json").read_text()) == {
            "situation": case["model"], "record": case["record"], "observations": case["observations"],
            "query": case["query"]}


def CASES_OF(key):
    return test_defaults_zone.CASES[key][0]()


def test_every_cli_fixture_answers_as_the_service_mode(monkeypatch):
    """Condition (ii): each spec 8.6 fixture through the command line sends df-5's request (the observations and the
    record included) and prints the service mode's answer to it, with the English of the rows Lean chose."""
    for name, key in FIXTURES.items():
        case, row, *_ = genuine(key)
        out, sent = _cli(monkeypatch, DATA / f"{name}.ve.md", DATA / f"{name}.json")
        assert sent == [_documents(case)], name
        assert out == {"question": "default", "kind": "defaults-zone",
                       "answer": {k: v for k, v in row.items() if k not in ("id", "status")},
                       "english": defaults_english.sentences(case, row)}, name
        expected, english = test_defaults_zone.CASES[key][1:]
        assert expected is None or out["answer"] == expected, name
        assert english is None or len(out["english"]) == len(english), name


def test_situated_routing_and_refusals(monkeypatch):
    """Only a JSON object naming `situation` is asked at a situation: a formula (a list, even one that holds the
    string "situation"), any other JSON value and an object without `situation` go to DF-1b's two questions as
    before. A situated question has exactly the four members, on a soft-norms@0 document without content-bearing or
    open reading sets that asserts no fact, and takes no --under, --sentence or --narrowing."""
    asked = []
    monkeypatch.setattr(defaults, "ask", lambda *arguments: asked.append(arguments[3]) or {"asked": "strict"})
    monkeypatch.setattr(defaults, "ask_zone", lambda *arguments: {"asked": "zone"})
    monkeypatch.setattr(cli, "_readings_without_exception", lambda *arguments: {"asked": "readings"})
    doc = load_document(ROOT / "tests/data/defaults_zone_cli/df-xi.ve.md")
    args = argparse.Namespace(under=None, sentence=None, narrowing=None)
    question = json.loads((DATA / "df-xi.json").read_text())
    for conclusion in (["unary", "situation", ["var", 0]], 5, "situation", {"record": []}, [question]):
        assert cli._assume_no_exception(doc, conclusion, args) == {"asked": "strict"}
    assert asked == [["unary", "situation", ["var", 0]], 5, "situation", {"record": []}, [question]]
    assert cli._assume_no_exception(doc, question, args) == {"asked": "zone"}
    for wrong in ({**question, "premises": []}, {k: v for k, v in question.items() if k != "record"}):
        with pytest.raises(VEError, match="^InvalidInput: a question at a situation has the members situation, "
                                          "record, observations, query$"):
            cli._assume_no_exception(doc, wrong, args)
    fact = {"kind": "asserted", "content": ["exists", "assistant", ["unary", "x_required", ["var", 0]]]}
    with pytest.raises(VEError, match="takes its facts from the situation; the document asserts some"):
        cli._assume_no_exception({**doc, "units": [*doc["units"], fact]}, question, args)
    for flags in ({"under": ["s:0"]}, {"sentence": "u0"}, {"narrowing": "n"}):
        with pytest.raises(VEError, match="takes no --under, --sentence or --narrowing"):
            cli._assume_no_exception(doc, question, argparse.Namespace(**{**vars(args), **flags}))
    ce4 = load_document(ROOT / CE4)
    assert cli._assume_no_exception(ce4, ["top"], args) == {"asked": "readings"}
    with pytest.raises(VEError, match="applies to a soft-norms@0 document without open reading sets"):
        cli._assume_no_exception(ce4, question, args)


BOTH_SIDES = (test_every_cli_fixture_answers_as_the_service_mode, test_situated_routing_and_refusals)


def test_every_other_call_prints_what_it_printed_before(monkeypatch):
    """Condition (i): DF-1b's CLI fixtures with no situation (P-1, P-3 and CE4 with P-1's question) print, byte for
    byte, what main's Python printed (`unchanged.json`)."""
    monkeypatch.chdir(ROOT)
    recorded = json.loads((DATA / "unchanged.json").read_text())
    assert len(recorded) == 6 and all(entry["exit"] == 0 for entry in recorded)
    for entry in recorded:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert cli.main(entry["argv"]) == 0
        assert out.getvalue() == entry["stdout"], entry["argv"]


def test_weighing_documents_are_refused_by_lean_on_the_cli_path(monkeypatch):
    """Condition (iii): a `weighing@0` document asked at a situation is refused, and nothing is answered, with the
    text the service mode gives df-5's request for it (Lean's own, unchanged). On main that text is the layered
    decoder's, which refuses the profile before diagnostic 1 (df-5's DF-θ guards in
    `lean/VE/Defaults/ZoneWireExamples.lean`); spec 5 row 1's text is `weighingText`, which Lean's `viewRest` gives
    on a decoded document (df-5's guard, condition (iv)). The DRI was asked to confirm this reading (df-5b REPORT)."""
    monkeypatch.chdir(ROOT)
    front = json.loads((DATA / "weighing.ve.md").read_text().split("---\n")[1])
    norms, question = [unit["content"] for unit in front["units"]], json.loads((DATA / "df-xi.json").read_text())
    assert "weighing@0" in front["environment"]["profiles"]
    request = _documents({**CASES_OF("xi"), "environment": front["environment"], "norms": norms})
    with pytest.raises(UnsupportedProfile) as service:
        defaults.run(request)
    for ask in (lambda: cli.main(["readings", str(DATA / "weighing.ve.md"), "--conclusion", str(DATA / "df-xi.json"),
                                  "--assume-no-exception"]),
                lambda: defaults.ask_zone(front["environment"], norms, question)):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), pytest.raises(UnsupportedProfile) as raised:
            ask()
        assert (str(raised.value), out.getvalue()) == (str(service.value), "")
    assert str(service.value) == "UnsupportedProfile: Unsupported profile weighing@0"


# -- W7's all-derivations gate for DE10, DE10f, DE11 and DE13

def test_w7_every_zone_sentence_has_one_derivation_its_own(monkeypatch):
    """Every sentence each df-5 fixture shows, and every row inside DE10″, is read by exactly one registered wording
    (S2's and every zone row's, `templates`), the one it was built from; all three DE10 forms and every row after
    DE10 are registered."""
    checked = []
    check = defaults_english.Gate.check
    monkeypatch.setattr(defaults_english.Gate, "check", lambda gate, shown: checked.append(gate) or check(gate, shown))
    names = set(defaults_english.templates())
    assert {"DE10:byDefault:short", "DE10′:byDefault:long", "DE10″:leftTo:short", "DE10″:leftTo:long",
            "DE10f:", "DE11:", "DE13:excepted", "DE13:off", "DE13:outweighs", "DE13:excepted:inline", "E12"} <= names
    for name in test_defaults_zone.CASES:
        case, row, *_ = genuine(name)
        defaults_english.sentences(case, row)
    built = [(name, text) for gate in checked for name, text in gate.built]
    assert {name.split(":")[0] for name, _ in built} == {"DE10", "DE10′", "DE10″", "DE10f", "DE11", "DE13"}
    assert any(name.endswith(":inline") for name, _ in built)
    for gate in checked:
        for name, text in gate.built:
            assert gate.derivations(text) == [name], text


def _ambiguous(monkeypatch, row, kind, words):
    """Lean's words with one row's words replaced, as a reworded table would give them."""
    table = copy.deepcopy(defaults_english._words())
    [line] = [w for w in table["lines"] if (w["row"], w["kind"]) == (row, kind)]
    line.update(words)
    monkeypatch.setattr(defaults_english, "_words", lambda: table)


def test_w7_refuses_a_sentence_two_wordings_read(monkeypatch):
    """A shown sentence two wordings derive is refused, never shown: DE13's words made DE10f's (DF-μ's DE10f line),
    and inside DE10″, DE13's inline words made DE10f's (DF-μ′'s two completions)."""
    force = [w for w in defaults_english._words()["lines"] if w["row"] == "DE10f"][0]
    _ambiguous(monkeypatch, "DE13", "excepted", {"sentence": force["sentence"]})
    case, row, *_ = genuine("mu")
    with pytest.raises(VEError, match="^InvalidInput: zone wording DE10f: has 2 derivations: The facts here force"):
        defaults_english.sentences(case, row)
    monkeypatch.undo()
    _ambiguous(monkeypatch, "DE13", "excepted", {"inline": force["inline"]})
    case, row, *_ = genuine("mu1")
    with pytest.raises(VEError, match="^InvalidInput: zone wording DE13:excepted:inline has 2 derivations"):
        defaults_english.sentences(case, row)
