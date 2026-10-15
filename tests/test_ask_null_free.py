"""Found by Q2.6's corpus agreement (qa-q2 review F4): `ve ask` sent an exposition unit's missing content as JSON null,
which the service's restricted JSON refuses, so every norm-defaults document with a unit without content was
refused (256 of the corpus's queries). The class, not the example: no request `ve ask` builds holds a null, on any
route; Lean reads an absent content as none, as the front matter has it."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _nulls(value, path=""):
    if value is None:
        yield path
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _nulls(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _nulls(item, f"{path}/{index}")


def _exposition_document(tmp_path):
    """A generated norm-defaults document whose only unit is exposition (no rule), as the corpus writes it."""
    from conformance import norm_defaults_differential as generator
    env, _, _ = generator.case(12, profiled=True)
    text = "No rule.\n"
    front = {"format": "ve-document@1", "environment": env.to_dict(),
             "units": [{"id": "u0", "span": [0, len(text.encode())], "kind": "exposition", "meaning": "specified",
                        "support": "none"}]}
    path = tmp_path / "exposition.ve.md"
    path.write_text("---\n" + json.dumps(front) + "\n---\n" + text)
    return path


def test_a_unit_without_content_is_answered(tmp_path):
    from ve.ask import answer, prepare
    path = _exposition_document(tmp_path)
    question = "Is it the case that every act may be audited?"
    prepared = prepare(path, path.read_bytes(), question)
    assert list(_nulls(prepared.request)) == []
    assert answer(path, path.read_bytes(), question)["lead"] in ("yes", "no", "notSettled", "notNecessarily",
                                                                "unknown")


def test_no_request_of_any_route_holds_a_null():
    """The readings, plain and norm-defaults routes, on recorded fixtures' documents (U3, G3, A1)."""
    from ve.ask import prepare
    for ident in ("U3", "G3", "A1"):
        entry = json.loads((ROOT / f"tests/fixtures/ask/{ident}.json").read_text())
        path = ROOT / entry["path"]
        prepared = prepare(path, path.read_bytes(), entry["question"], entry["case"]["evidence"], generate=False)
        assert list(_nulls(prepared.request)) == [], ident
