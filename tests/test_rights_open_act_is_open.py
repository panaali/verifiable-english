"""rights-cfr-4: a right whose act is a declared open term is OPEN (docs/spec/rights.md 7.2).

Spec 7.2: "one with an open standard in a guard, act, limitation or condition is OPEN". Lean's `nodeOpen`
(lean/VE/Rights/Run.lean) read the guard and carve-outs but not the act `N.pred`, so a specified strict right whose
act predicate is a declared open term was reported CHECKED. The status is Lean's (`Rights.Run.unitOpen`); these tests
read it through `ve document check` (Lean's document mode) and through the rights route's `rights-elaborate` answer
(`unit_open`), which the retained path relays."""
from __future__ import annotations

import json

from ve.__main__ import main as ve_main
from ve.document import load_document

ACTS = {"speak_permitted": "{0} speak", "marry_permitted": "{0} marry"}
# Unit texts of different lengths, so `bytes_by_status` tells which unit is OPEN.
TEXTS = ("Unit 1.\n", "Unit two of two.\n")


def _right(name, act):
    return {"right": {"name": name, "holder": "person", "guard": ["top"], "lines": [
        {"kind": "liberty", "norm": {"name": f"{name}-line", "predicate": act, "sign": True,
                                     "guard": ["unary", "adult", ["var", 0]], "unless": [], "over": []}}]}}


def _open_term(name):
    return {"name": name, "arguments": ["x"], "decided_by": "court", "necessary": [], "sufficient": [],
            "factors": [], "precedents": [], "jurisdiction": "document", "version": 1}


def _document(acts, open_terms):
    """A part document: one specified strict right per act (u1, u2, ...), an exposition unit when there is one right,
    and `open_terms` declared."""
    predicates = {act: {"arguments": ["person"], "description": "permission",
                        "regulated": {"role": "permission", "default": "allow", "act": ACTS[act]}} for act in ACTS}
    predicates["adult"] = {"arguments": ["person"], "description": "base"}
    environment = {"language": "ve.core@0.2", "profiles": ["norms@0", "relational-fol@0", "rights@0", "soft-norms@0"],
                   "spec_revision": "ve-v0.2-expand2-2026-09-25",
                   "vocabulary": {"sorts": {"person": {"description": "person"}}, "predicates": predicates,
                                  "constants": {},
                                  "rights": {"holders": ["person"], "bearers": ["person"], "protected": []},
                                  "soft": {"parties": [], "ranks": [], "outranks": [],
                                           "outranking": {"mode": "strict"}}}}
    units, start = [], 0
    for index, text in enumerate(TEXTS):
        unit = {"id": f"u{index + 1}", "span": [start, start + len(text)], "meaning": "specified", "support": "none"}
        start += len(text)
        if index < len(acts):
            unit.update(kind="right", content=_right(f"r{index + 1}", acts[index]))
        else:
            unit["kind"] = "exposition"
        units.append(unit)
    front = {"format": "ve-document@1", "environment": environment, "units": units,
             "open_terms": [_open_term(name) for name in open_terms]}
    return "---\n" + json.dumps(front) + "\n---\n" + "".join(TEXTS)


def _check(text, tmp_path, capsys):
    """`ve document check`'s exit code and bytes by status, and the per-unit statuses and the route's `unit_open`
    (per item of the rights source: its `source_units` header first) of the loaded document."""
    path = tmp_path / "part.ve.md"
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    code = ve_main(["document", "check", str(path)])
    report = json.loads(capsys.readouterr().out)
    loaded = load_document(path)
    statuses = {u["id"]: u["status"] for u in loaded["units"]}
    return code, report["coverage"]["bytes_by_status"], statuses, loaded["rights_document"].elaborated["unit_open"]


def test_rights_open_act_is_open(tmp_path, capsys):
    """The condition test: a specified strict right whose act is a declared open term is OPEN, on both paths."""
    code, by_status, statuses, unit_open = _check(_document(["speak_permitted"], ["speak_permitted"]), tmp_path,
                                                  capsys)
    assert code == 0
    assert by_status == {"OPEN": len(TEXTS[0]), "LABELLED": len(TEXTS[1])}
    assert statuses == {"u1": "OPEN", "u2": "LABELLED"}
    assert unit_open == [False, True]


def test_rights_closed_act_stays_checked(tmp_path, capsys):
    """The control: the same right with no open term (or an open term it does not read) stays CHECKED."""
    for open_terms in ([], ["marry_permitted"]):
        code, by_status, statuses, unit_open = _check(_document(["speak_permitted"], open_terms), tmp_path, capsys)
        assert code == 0
        assert by_status == {"CHECKED": len(TEXTS[0]), "LABELLED": len(TEXTS[1])}, open_terms
        assert statuses == {"u1": "CHECKED", "u2": "LABELLED"}, open_terms
        assert unit_open == [False, False], open_terms


def test_rights_open_act_reads_each_rights_own_act(tmp_path, capsys):
    """Two rights, one with an open act: only that right is OPEN, whichever of the two it is."""
    for acts, expected in ((["speak_permitted", "marry_permitted"], ("OPEN", "CHECKED")),
                           (["marry_permitted", "speak_permitted"], ("CHECKED", "OPEN"))):
        code, by_status, statuses, unit_open = _check(_document(acts, ["speak_permitted"]), tmp_path, capsys)
        assert code == 0
        assert statuses == {"u1": expected[0], "u2": expected[1]}, acts
        assert by_status == {expected[0]: len(TEXTS[0]), expected[1]: len(TEXTS[1])}, acts
        assert unit_open == [False] + [s == "OPEN" for s in expected], acts
