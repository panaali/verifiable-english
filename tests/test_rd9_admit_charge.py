"""sc-admit-cpu: admission's per-reading charge on the wire (DRI 2026-11-11 sc-admit-cpu item 3; spec rd-9 4.1 step 5,
14.11).

Lean's `admitSDOf` reads `sdAdmitWork N <= maxSdAdmitWork` before the per-choice texts. Over it, every soft-chain
readings kind that admits the document is refused with Lean's `ResourceLimit` text. On main, NSDheavy and heavyIn
were admitted in 1.3-2.0 s of Lean CPU (docs/rd-9/sc-admit-cpu/cpu.md). The requests are the evidence's own
(`docs/rd-9/sc-admit-cpu/admit_docs.py`, the one builder of these documents on the wire). Python decides nothing here:
each expected value is Lean's text or status, and the `#guard`s in lean/VE/Readings/SoftWireExamples.lean pin the
same values on the Lean documents.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from tests import lean_routes
from tests.test_readings_s1_lean import run

ROOT = Path(__file__).resolve().parents[1]
LEAN = "ve_readings_route"
REFUSAL = "ResourceLimit: the per-reading checks of 64 readings exceed 131072 units"


def _builder():
    spec = importlib.util.spec_from_file_location("sc_admit_docs", ROOT / "docs/rd-9/sc-admit-cpu/admit_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DOCS = _builder()


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    return LEAN


def _row(lean, kind, name):
    case = {"id": kind, "kind": kind, "environment": DOCS.environment(), "document": DOCS.CASES[name]()}
    return run(lean, [case])[0]


@pytest.mark.parametrize("kind", ["readings-validate", "readings-elaborate"])
@pytest.mark.parametrize("name", ["NSDheavy", "heavyIn", "overLimit"])
def test_over_the_charge_admission_is_refused_with_leans_resource_limit(lean, name, kind):
    """R5's regression rows: documents admitted on main over R4, and the next work over the limit, are refused."""
    row = _row(lean, kind, name)
    assert (row["status"], row["error"]) == ("error", REFUSAL), row


@pytest.mark.parametrize("name", ["atLimit", "NSDbig6", "wideGuard767"])
def test_within_the_charge_or_over_64_choices_admission_is_unchanged(lean, name):
    """At the limit and on the named NSDbig 6 the per-choice texts run and pass; over 64 choices no text runs and the
    charge is not read, although wideGuard767's work is over it. (`readings-elaborate`: these documents carry no
    distinguishing models, which `readings-validate` asks for after admission.)"""
    row = _row(lean, "readings-elaborate", name)
    assert (row["status"], row["route"]) == ("ok", "enumerated"), row
