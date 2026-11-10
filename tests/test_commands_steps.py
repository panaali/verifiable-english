"""CI-3 (commands-imperatives section 7) through `english.command`: steps, `Then` steps and conditions written first,
and the saved A/B's b1 rows pinned to their Lean fixtures (DRI 2026-10-28 item 2(b))."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import lean_routes
from tests.lean_service_corpus import command_cases
from test_speech_source_lean import lean  # noqa: F401  (the speech-source route fixture)

ROOT = Path(__file__).resolve().parents[1]
AB = json.loads((ROOT / "docs/commands-imperatives/ci-3/AB.json").read_text())


@pytest.mark.parametrize("row", [r for r in AB["changed"] if r["class"] == "b1"], ids=lambda r: r["wording"])
def test_each_b1_row_is_a_route_fixture_that_reads(row):
    fixtures = (ROOT / "lean/VE/Commands/RunExamples.lean").read_text()
    assert f'"{row["wording"]}"' in fixtures
    assert row["base"].startswith("VE.Commands.StepOutcome.refused")
    assert row["head"].split()[0].rsplit(".", 1)[1] in ("one", "steps", "many")


def test_saved_ab_has_no_stop_row_and_no_surface_kind_flip():
    assert [r["wording"] for r in AB["changed"] if r["class"] not in ("b1", "b2", "rr")] == []
    assert AB["surface_kind_flips"] == [] and AB["corpus_if_then_literals"] == 0


def ask(wording):
    [case] = [c for c in command_cases() if c["id"] == "click"]
    [row] = lean_routes.rows("english.command", [{**case, "wording": wording}])
    return row["result"]


@pytest.mark.parametrize("wording", ["  Click Check, then do not share the token.",
                                     "  Click Check, then  click Check."])
def test_a_sequence_reads_one_reading_per_step_with_spans_into_the_wording(wording):
    answer = ask(wording)
    assert answer["outcome"] == "steps"
    assert len(answer["readings"]) == 2
    for reading in answer["readings"]:
        [fill] = reading["fills"]
        start, end = fill["span"]
        assert wording[start:end].lower() == fill["words"].lower()
    assert answer["paraphrase"].startswith("In this task, you are required to do these in order: first click check, then ")


def test_then_and_preposed_condition_read_one_with_their_flag():
    then, preposed = ask("Then click Check."), ask("If atlas is reviewed, click Check.")
    assert (then["outcome"], then["after_previous"], preposed["after_previous"]) == ("one", True, False)
    assert preposed["reading"]["command"]["guard"] == ["unary", "reviewed", ["const", "atlas"]]
    assert ask("Click Check.")["after_previous"] is False


def test_a_then_instruction_unit_is_refused_by_the_speech_source_route(lean):
    """The document check (finding (c), O3) is wired after the core check, by each unit's effective kind."""
    from test_speech_acts_conformance import reading_set
    from test_speech_acts_lean import U, command, unit
    from test_speech_source_lean import base_env, placed, run_source

    click = command("require", "click_required", ["check"])

    def check(line, u, sets=()):
        return run_source({"format": "ve-document@2", "environment": base_env(), "units": placed([line], [u]),
                           "reading_sets": list(sets)}, line)

    refused = "ThenWithoutStep: a Then step names no earlier instruction step as its antecedent"
    assert refused in check("Then click check.\n", unit("x", 0, "instruction", click))["error"]
    assert check("Click check.\n", unit("x", 0, "instruction", click))["status"] == "ok"
    signed = check("Then click check.\n", unit("c", 0, "asserted", {"ast": U("reviewed", "atlas")}),
                   [reading_set("c", 1, "authored", "instruction", click)])
    assert refused in signed["error"]
