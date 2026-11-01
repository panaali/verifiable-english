"""SC-4: scope@0's forward declarations (docs/spec/scope.md 1.9, 3, 5.6, 7.6) through the document mode. Lean decides
(`forwardCheck`, `admitBlock`'s step 9, `lean/VE/Scope/Govern.lean`); Python relays the answer (R8).

The DRI's decision of 2026-11-01 (reviews/dri-decisions-20261101-sc-4.md): a document without `forward` answers byte
for byte as main (main's answers recorded by `docs/scope/sc-4/record_absent.py` from main's service in
`tests/data/scope/forward-absent-main.json`); F12-f's passing document answers as its twin without the member, only
the document's identity differing; 256 declarations over 64 later units are admitted and 257 are a ResourceLimit."""
from __future__ import annotations

import json
from pathlib import Path

from tests.test_rights import rights_env
from tests.test_scope_document import CHAINS, F1, FRAME, _text
from ve.backends.relay import answer

ABSENT = Path(__file__).parent / "data/scope/forward-absent-main.json"


def forward_text(forward: list | None = None, later: int = 1) -> str:
    """Rule a, then "Rule a has exceptions stated later in this section." (u2), then `later` rules, the last over a."""
    env = rights_env()
    env["profiles"] = sorted(CHAINS["norms"] + ["scope@0"])
    del env["vocabulary"]["rights"]
    names = ["b"] if later == 1 else [f"b{i}" for i in range(later)]
    lines = [("u1", "- **Rule a:** Unit a.\n", {"norm": {"name": "a", **FRAME, "guard": ["top"]}}),
             ("u2", "Rule a has exceptions stated later in this section.\n", None)] + [
        (f"u{i + 3}", f"- **Rule {n}:** Unit {n}.\n",
         {"norm": {"name": n, **FRAME, "over": ["a"] if i == len(names) - 1 else [], "guard": ["top"]}})
        for i, n in enumerate(names)]
    units, start = [], 0
    for uid, line, content in lines:
        end = start + len(line.encode())
        units.append({"id": uid, "span": [start, end], "support": "none",
                      **({"kind": "norm", "meaning": "specified", "content": content} if content else
                         {"kind": ["unformalised", "norms"], "meaning": {"unformalised": "norms"}})})
        start = end
    scope = {"version": "scope@0", "anchors": [{"id": "doc", "kind": "document", "label": "Doc", "span": [0, start]}]}
    if forward is not None:
        scope["forward"] = forward
    meta = {"format": "ve-document@1", "environment": env, "units": units, "scope": scope}
    return _text(meta, "".join(line for _, line, _ in lines))


def absent_documents() -> dict[str, str]:
    """The documents without `forward` whose answers main recorded: F1 (a frame governor) and F12-f's twin."""
    return {"f1": F1.read_text(), "twin": forward_text()}


def _answer(text: str):
    row, error = answer("document", {"id": "d", "document": text, "admit": True})
    return row if error is None else str(error)


def test_a_document_without_forward_answers_byte_for_byte_as_main():
    saved = json.loads(ABSENT.read_text())
    assert set(saved["answers"]) == set(absent_documents())
    for name, text in absent_documents().items():
        assert json.dumps(_answer(text), sort_keys=True) == json.dumps(saved["answers"][name], sort_keys=True), name


def test_f12_f_the_passing_declaration_answers_as_its_twin_without_it():
    twin, declared = _answer(forward_text()), _answer(forward_text([{"unit": "u2", "rule": "a", "anchor": "doc"}]))
    assert isinstance(twin, dict) and isinstance(declared, dict)
    assert {key for key in twin if twin[key] != declared[key]} == {"document_id"}


def test_f12_f_and_f0_a_declaration_with_no_later_exception_is_leans_scope_forward():
    # u3's `over` names a, not b; u1 names nothing; and the document has no governor (F12-f0)
    assert _answer(forward_text([{"unit": "u2", "rule": "b", "anchor": "doc"}])) == \
        "ScopeForward: u2: rule b has no later exception in doc"
    assert _answer(forward_text([{"unit": "u3", "rule": "a", "anchor": "doc"}])) == \
        "ScopeForward: u3: rule a has no later exception in doc"


def test_the_member_is_read_by_leans_decoder():
    assert _answer(forward_text([{"unit": "u2", "rule": "a"}])) == \
        "InvalidInput: scope@0 forward.u2.anchor must be present"
    assert _answer(forward_text({"unit": "u2"})) == "InvalidInput: scope@0 forward must be an array"


def test_256_declarations_over_64_later_units_are_admitted_and_257_are_a_resource_limit():
    declaration = {"unit": "u2", "rule": "a", "anchor": "doc"}
    admitted = _answer(forward_text([declaration] * 256, later=64))
    assert isinstance(admitted, dict) and admitted["status"] == "ok"
    assert _answer(forward_text([declaration] * 257, later=64)) == "ResourceLimit: scope forward declarations"
