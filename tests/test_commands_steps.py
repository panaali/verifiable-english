"""CI-3 (commands-imperatives section 7) through `english.command`: steps, `Then` steps and conditions written first,
and the saved A/B's b1 rows pinned to their Lean fixtures (DRI 2026-10-28 item 2(b))."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import lean_routes
from tests.lean_service_corpus import command_cases

ROOT = Path(__file__).resolve().parents[1]
AB = json.loads((ROOT / "docs/commands-imperatives/ci-3/AB.json").read_text())


@pytest.mark.parametrize("row", [r for r in AB["changed"] if r["class"] == "b1"], ids=lambda r: r["wording"])
def test_each_b1_row_is_a_route_fixture_that_reads(row):
    fixtures = (ROOT / "lean/VE/Commands/RunExamples.lean").read_text()
    assert f'"{row["wording"]}"' in fixtures
    assert row["base"].startswith("VE.Commands.StepOutcome.refused")
    assert row["head"].split()[0].rsplit(".", 1)[1] in ("one", "steps", "many")


def test_saved_ab_has_no_stop_row_and_no_surface_kind_flip():
    assert [r["wording"] for r in AB["changed"] if r["class"] not in ("b1", "b2")] == []
    assert AB["surface_kind_flips"] == [] and AB["corpus_if_then_literals"] == 0


def ask(wording):
    [case] = [c for c in command_cases() if c["id"] == "click"]
    [row] = lean_routes.rows("english.command", [{**case, "wording": wording}])
    return row["result"]


def test_a_sequence_reads_one_reading_per_step_with_spans_into_the_wording():
    wording = "  Click Check, then do not share the token."
    answer = ask(wording)
    assert answer["outcome"] == "steps"
    assert [r["command"]["force"] for r in answer["readings"]] == ["require", "forbid"]
    for reading in answer["readings"]:
        [fill] = reading["fills"]
        start, end = fill["span"]
        assert wording[start:end].lower() == fill["words"].lower()
    assert answer["paraphrase"] == ("In this task, you are required to do these in order: first click check, then do "
                                    "not share the token. The order is stated; VE does not reason about it.")


def test_then_and_preposed_condition_read_one_with_their_flag():
    then, preposed = ask("Then click Check."), ask("If atlas is reviewed, click Check.")
    assert (then["outcome"], then["after_previous"], preposed["after_previous"]) == ("one", True, False)
    assert preposed["reading"]["command"]["guard"] == ["unary", "reviewed", ["const", "atlas"]]
    assert ask("Click Check.")["after_previous"] is False
