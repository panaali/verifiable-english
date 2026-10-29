"""RD-5 behavior tests: copy declarations, reproduce the migrated UDHR, and replay witnesses through Lean."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests import lean_routes

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "usecases/udhr-pilot/run-20261010T1400Z"
sys.path.insert(0, str(RUN))

import migrate  # noqa: E402


METRICS = json.loads((RUN / "metrics.json").read_text())
UNMIGRATED = json.loads((RUN / "unmigrated.json").read_text())
META, _SOURCE = migrate.split_document((RUN / "translation.ve.md").read_bytes())


def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")





def test_copied_environment_holds_only_what_the_assertion_mentions():
    """The copied companion of `rs_u052`'s asserted reading: the main frame's declarations of the predicates it
    mentions and their sorts, without the verbalisation the norm companion gives them (so Lean's split refuses the
    set, E1)."""
    formula = ["forall", "prosecution", ["implies", ["or", ["unary", "arises_from_non_political_crime", ["var", 0]],
                                                           ["unary", "arises_from_acts_contrary_to_un", ["var", 0]]],
                                         ["not", ["unary", "asylum_right_covers_case", ["var", 0]]]]]
    main = {"vocabulary": {"constants": {}, "sorts": {"prosecution": {"description": "p"}, "person": {}},
                           "predicates": {name: {"arguments": ["prosecution"], "description": name}
                                          for name in ("arises_from_non_political_crime",
                                                       "arises_from_acts_contrary_to_un",
                                                       "asylum_right_covers_case", "unused")}}}
    like = {"language": "L", "profiles": ["p"], "spec_revision": "r"}
    env, lines = migrate.copied_environment(main, formula, like)
    assert sorted(env["vocabulary"]["predicates"]) == ["arises_from_acts_contrary_to_un",
                                                       "arises_from_non_political_crime", "asylum_right_covers_case"]
    assert list(env["vocabulary"]["sorts"]) == ["prosecution"] and env["profiles"] == ["p"]
    assert lines == ["sort prosecution", "predicate arises_from_acts_contrary_to_un",
                     "predicate arises_from_non_political_crime", "predicate asylum_right_covers_case"]


def test_the_migration_reproduces_the_committed_document(tmp_path):
    """Rerun through Lean from run 20261006T1800Z at bd6c7ab2: the same document and record, byte for byte."""
    lean()
    migrate.migrate(out=tmp_path)
    assert (tmp_path / "translation.ve.md").read_bytes() == (RUN / "translation.ve.md").read_bytes()
    assert json.loads((tmp_path / "unmigrated.json").read_text()) == UNMIGRATED


def test_one_sets_witnesses_replay_equal_in_its_component_and_alone(tmp_path):
    """`rs_u025`'s companions (witnesses SETTLED yes, SETTLED no and UNDECIDED): each witness Lean replays, in the
    component and alone, is the recorded one."""
    lean()
    import witnesses
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import wire
    env, doc = wire(META["environment"]), wire(document_wire(META["units"], META["reading_sets"]))
    [row] = run_lean([{"id": "split", "kind": "readings-elaborate", "environment": env, "document": doc}])
    parts = {c["component"]: c for c in row["components"]}
    (tmp_path / "specs").mkdir()
    (tmp_path / "companions").mkdir()
    got = witnesses.in_components(env, doc, {"rs_u025": parts["rs_u025"]}, folder=tmp_path / "specs",
                                  only={"rs_u025"})
    assert got == {k: v for k, v in METRICS["witnesses"]["in_components"].items() if k.startswith("u025.")}
    assert {w["recorded"] for v in got.values() for w in v["witnesses"]} == {"SETTLED yes", "SETTLED no", "UNDECIDED"}
    keys = {"u025.practice_prohibited", "u025.state_prohibits"}
    assert witnesses.alone(folder=tmp_path / "companions", only=keys) == \
        {k: METRICS["witnesses"]["alone"][k] for k in keys}
