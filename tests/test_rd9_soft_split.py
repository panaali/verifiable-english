"""F32: a document under the soft completion beside a companion set is refused by every kind of the split.

rd-9 narrowed S1's abstention to the rights chain, so a soft-chain document under `norm-defaults@0` with a
content-bearing set is read under the soft completion (`underSoftCompletion`) when it is one case. Its split
(readings-defaults 3) is not built for that completion: rd-9-soft-chain.md 5 row 7 refuses a companion on the soft
chain with RD-4a's text. Every admission of the split goes through one check (`splitAdmissible`,
`ComponentsWire.lean`): `admitComponent`, `admitChecked` and the product's `requireCompletion`. Before the fix
validate answered F-SD1's own situation with `InvalidInput: invalid situation <id>` and elaborate answered `main`
without its completion.

The kinds are the generated response schema's (`$defs/kind`, rendered from Lean's shape), so a new readings kind is
covered here without editing this file.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import lean_routes
from tests.test_readings_companions_lean import set_a
from tests.test_readings_sd_lean import fsd1
from ve import readings_route
from ve.errors import VEError
from ve.readings_s1 import wire

ROW_7 = "UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented"
SCHEMA = Path(__file__).resolve().parents[1] / "ve/backends/lean_service_schema/readings-route.json"
KINDS = sorted(json.loads(SCHEMA.read_text())["$defs"]["kind"])
QUESTIONS = ("conflict", "premises", "query")


@pytest.fixture(scope="module", autouse=True)
def service():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def split_document():
    """F-SD1 (the soft completion) and F-ND1's set over its own vocabulary as a companion set (`rs_a` on `u_a`)."""
    raw, document, sid = fsd1()
    a, _, _ = set_a()
    both = readings_route.document_wire(document["units"] + [{"id": "u_a"}], document["reading_sets"] + [a])
    return wire(raw), document, wire(both), sid


def requests():
    """Every kind, each verdicts question (the product reads its question before any case), and each component."""
    for kind in KINDS:
        for question in (QUESTIONS if kind == "readings-verdicts" else (None,)):
            for component in (None, "main", "rs_a"):
                yield pytest.param(kind, question, component, id=f"{kind}-{question}-{component}")


def test_kinds_come_from_the_generated_schema():
    assert "readings-validate" in KINDS and "readings-verdicts" in KINDS and len(KINDS) >= 9


def test_fsd1_alone_stays_under_the_soft_completion():
    raw, document, _, _ = split_document()
    alone = wire(readings_route.document_wire(document["units"], document["reading_sets"]))
    for kind in ("readings-validate", "readings-elaborate"):
        [row] = readings_route.run_lean([{"id": kind, "kind": kind, "environment": raw, "document": alone}])
        assert row["status"] == "ok" and row["filled"]["chain"] == "soft", row


@pytest.mark.parametrize("kind,question,component", list(requests()))
def test_f32_every_kind_of_a_soft_split_is_refused_with_row_7(kind, question, component):
    raw, _, both, _ = split_document()
    case = {"id": kind, "kind": kind, "environment": raw, "document": both,
            **({"question": question} if question else {}), **({"component": component} if component else {})}
    [row] = readings_route.run_lean([case])
    assert row == {"id": kind, "status": "error", "error": ROW_7}, row


def test_f32_probe_validate_and_elaborate_through_the_relay():
    """The probe's cases (reviews/rd-9-probe-f32.py): refused with row 7, never InvalidInput nor an answer without
    its completion; the Python relay raises Lean's text."""
    raw, document, both, _ = split_document()
    for kind in ("readings-validate", "readings-elaborate"):
        [row] = readings_route.run_lean([{"id": kind, "kind": kind, "environment": raw, "document": both}])
        assert row["status"] == "error" and row["error"] == ROW_7, row
    a, _, _ = set_a()
    with pytest.raises(VEError) as caught:
        readings_route.validate(raw, document["units"] + [{"id": "u_a"}], document["reading_sets"] + [a])
    assert str(caught.value).endswith(ROW_7)
