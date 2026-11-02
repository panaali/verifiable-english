"""SC-6: the UDHR's rights reach (docs/spec/scope.md 5.8, 7.8). Lean decides (`Pinned.rightNames`,
`Pinned.withReach`, `Pinned.withBarReach`, `lean/VE/Scope/Reach.lean`); the fixtures F14, F14′ and F14″ and u0218.s18's
regression (DRI DEC 16) are `#guard`s in `lean/VE/Scope/ReachExamples.lean`, checked by every `lake build`.

No route reads the reach yet (docs/scope/sc-6/DRI-QUESTION.md, sc-6b), so a document without a rights reach answers
byte for byte as main: a rights@0 part document of the UDHR under scope@0, whose answer main's service recorded
(`docs/scope/sc-6/record_absent.py`, `tests/data/scope/rights-reach-absent-main.json`)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from tests.test_rights import rights_env
from tests.test_scope_5_4_statements import statement
from tests.test_scope_document import _text
from ve.backends.relay import answer

ROOT = Path(__file__).resolve().parents[1]
ABSENT = ROOT / "tests/data/scope/rights-reach-absent-main.json"
REACH = ROOT / "lean/VE/Scope/Reach.lean"
EXAMPLES = ROOT / "lean/VE/Scope/ReachExamples.lean"


def spec_5_8() -> str:
    spec = (ROOT / "docs/spec/scope.md").read_text()
    start = spec.index("### 5.8 SC-6")
    return spec[start:spec.index("### 6.", start)]


def test_limitation_scope_of_reach_is_spec_5_8s_text():
    assert statement(spec_5_8(), "limitation_scope_of_reach") is not None
    assert statement(REACH.read_text(), "limitation_scope_of_reach") == statement(spec_5_8(),
                                                                                "limitation_scope_of_reach")


def test_the_statement_gate_compares_the_conjunct_after_the_record_update():
    """Review F1: the `:=` of `{ L' with scope := L.scope }` is inside the statement, so a changed second conjunct
    (the limitation otherwise unchanged) differs from the spec's text."""
    text = REACH.read_text()
    assert "scope := L.scope } = L :=" in text
    changed = text.replace("scope := L.scope } = L :=", "scope := none } = L :=", 1)
    assert statement(changed, "limitation_scope_of_reach") != statement(spec_5_8(), "limitation_scope_of_reach")


def _claim(name: str) -> dict:
    return {"kind": "claim", "norm": {"name": name, "predicate": "protect_required", "sign": True,
                                      "guard": ["top"], "unless": [], "over": []}}


def udhr_text() -> str:
    """Articles 3, 29 and 30 as rights@0 units under scope@0, Article 29's heading a title over its paragraphs; the
    limitation's scope is written (no reach)."""
    env = rights_env()
    env["profiles"] = sorted(env["profiles"] + ["scope@0"])
    limitation = {"name": "l29", "scope": ["life"], "kinds": "all", "decided_by": "unstated",
                  "conditions": [{"name": "law", "role": "necessary", "verbalisation": "determined by law"}],
                  "factors": []}
    lines = [("u001", "# Universal Declaration of Human Rights\n\n", None),
             ("u022a", "Everyone has the right to life\n\n",
              {"right": {"name": "life", "holder": "person", "lines": [_claim("protect")]}}),
             ("u109", "## Article 29\n\n", None),
             ("u111", "2. In the exercise of his rights and freedoms, everyone shall be subject only to such "
                      "limitations as are determined by law.\n\n", {"limitation": limitation}),
             ("u113", "## Article 30\n\n", None),
             ("u114", "Nothing in this Declaration may be interpreted as implying for any State, group or person any "
                      "right to destroy them.\n", {"bar": {"name": "art30", "reading": "rule"}})]
    units, start = [], 0
    for uid, line, content in lines:
        end = start + len(line.encode())
        units.append({"id": uid, "span": [start, end], "support": "none",
                      **({"kind": next(iter(content)), "meaning": "specified", "content": content} if content else
                         {"kind": ["unformalised", "other.discourse"],
                          "meaning": {"unformalised": "other.discourse"}})})
        start = end
    art29 = [u["span"] for u in units if u["id"] in ("u109", "u111")]
    scope = {"version": "scope@0",
             "anchors": [{"id": "doc", "kind": "document", "label": "UDHR", "span": [0, start]},
                         {"id": "art29", "kind": "section", "parent": "doc", "label": "Article 29",
                          "span": [art29[0][0], art29[1][1]]}],
             "governors": [{"id": "g109", "unit": "u109", "effect": "title", "reach": {"anchor": "art29"},
                            "units": ["u111"]}]}
    meta = {"format": "ve-document@1", "environment": env, "units": units, "scope": scope}
    return _text(meta, "".join(line for _, line, _ in lines))


def _answer(text: str):
    row, error = answer("document", {"id": "d", "document": text, "admit": True})
    return row if error is None else str(error)


def test_a_document_without_a_rights_reach_answers_byte_for_byte_as_main():
    saved = json.loads(ABSENT.read_text())
    row = _answer(udhr_text())
    assert isinstance(row, dict), row
    assert json.dumps(row, sort_keys=True) == json.dumps(saved["answers"]["udhr"], sort_keys=True)


def test_the_part_documents_name_no_stand_in_term():
    """What this item's UDHR documents say in place of `rights_and_freedoms_set_forth`: a reach."""
    assert "rights_and_freedoms_set_forth" not in udhr_text()
    examples = EXAMPLES.read_text()
    assert '#guard ((udhrDoc).compress.splitOn "rights_and_freedoms_set_forth").length == 1' in examples


def test_each_fixture_of_7_8_is_a_lean_section_with_guards():
    examples = EXAMPLES.read_text()
    sections = re.split(r"\n/-! ## ", examples)
    heads = {s.split(":", 1)[0]: s for s in sections[1:]}
    for fixture in ("F14", "F14′", "F14″"):
        assert fixture in heads and "#guard " in heads[fixture], fixture


def test_u0218_s18_records_its_blocker_and_two_by_one_choices():
    """DRI DEC 16: the lead-in guard over one unsplit act phrase, 2 × 1 choices, until modality MD-6."""
    examples = EXAMPLES.read_text()
    assert 'def u0218Blocker : String := "embedded act frame: modality MD-6"' in examples
    assert '#guard (do setChoices (← oc)).toOption == some [[("scope-u0218-s18", 1, 0)], [("scope-u0218-s18", 1, 1)]]' \
        in examples


def test_list_names_are_discourses_content_names():
    """syn2code-scope-4: scope keeps no second table of named unit sets; a list name is discourse's `ContentName`."""
    wire = (ROOT / "lean/VE/Scope/Wire.lean").read_text()
    govern = (ROOT / "lean/VE/Scope/Govern.lean").read_text()
    assert "let cn ← VE.Discourse.Wire.decodeContentName" in wire
    assert "listNames : List (VE.Discourse.ContentName × String × String)" in govern
    assert "if cn.units == us then pure us" in govern
