"""`tools/lean_decided_share.py` (readings-defaults 1.10 and 10; plan 3.9, RD-5): sums Lean's decided units' span
bytes and decides nothing; Lean's list is untrusted input, checked against the document."""
from __future__ import annotations

import json

import pytest

from tests.test_document import unit, write_doc
from tools import lean_decided_share as L
from ve.errors import VEError

SOURCE = "First rule. Second rule. A note.\n".encode()
A, B = len(b"First rule. "), len(b"First rule. Second rule. ")
UNITS = [{"id": "a", "span": [0, A]}, {"id": "b", "span": [A, B]}, {"id": "c", "span": [B, len(SOURCE)]}]


def test_the_share_sums_only_the_units_lean_lists():
    out = L.share(UNITS, len(SOURCE), {"decided_units": ["b"], "max_choice_rules": 2}, ["b", "c"])
    assert out["decided_bytes"] == B - A and out["decided_units"] == ["b"]
    assert out["decided_share_percent"] == str((100 * (B - A) / len(SOURCE)).__round__(2))
    assert out["max_choice_rules"] == 2 and out["decided_bytes_checked_outside"] == B - A
    assert out["one_rule"] == L.ONE_RULE and out["basis"] == "readings-verdicts decided_units"


def test_without_a_lean_answer_nothing_is_decided():
    """The UDHR run of 2026-10-06 has no readings block, so no Lean answer across readings: 0 (plan 3.9 'Before')."""
    out = L.share(UNITS, len(SOURCE))
    assert (out["decided_bytes"], out["decided_share_percent"], out["max_choice_rules"]) == (0, "0.00", None)
    assert out["basis"] == "no Lean answer across readings"
    # Astra's review C: no CONFLICT-FREE sentence stands without a Lean answer.
    assert out["one_rule"] is None and "CONFLICT-FREE" not in json.dumps(out)
    assert L.share(UNITS, len(SOURCE), {"decided_units": []})["decided_bytes"] == 0


def test_the_one_rule_sentence_is_about_the_isolated_rule():
    """Astra's review C: S2a's M8 has a one-rule reading whose choice is a CONFLICT with the document's other rules
    (tests/test_readings_s2_document.py), so the sentence claims CONFLICT-FREE only for a rule checked by itself."""
    assert L.ONE_RULE.startswith("A rule checked by itself is CONFLICT-FREE by construction")
    assert "reading checked with the document's other rules" in L.ONE_RULE
    assert not L.ONE_RULE.startswith("A reading")


@pytest.mark.parametrize("decided, total, percent", [(4257, 10916, "39.00"), (4792, 10916, "43.90"),
                                                     (2543, 10916, "23.30"), (1, 3, "33.33"), (2, 3, "66.67")])
def test_the_percentage_is_exact_decimal_arithmetic(decided, total, percent):
    """Plan 3.9's figures: the upper bound 4,257 of 10,916 bytes is 39.00%; the recorded claimed and audit-verified
    shares 43.90% and 23.30% come out of the same rule."""
    units = [{"id": "x", "span": [0, decided]}, {"id": "y", "span": [decided, total]}]
    assert L.share(units, total, {"decided_units": ["x"]})["decided_share_percent"] == percent


GENUINE = {"decided_units": ["a", "b"], "max_choice_rules": 1}


def _mutations():
    """Each field of a genuine answer dropped, emptied, duplicated and retyped (checklist line 4)."""
    yield "no decided_units", {"max_choice_rules": 1}
    yield "decided_units null", {**GENUINE, "decided_units": None}
    yield "decided_units a string", {**GENUINE, "decided_units": "a"}
    yield "decided_units an object", {**GENUINE, "decided_units": {"a": True}}
    yield "a unit twice", {**GENUINE, "decided_units": ["a", "a"]}
    yield "an int unit", {**GENUINE, "decided_units": ["a", 7]}
    yield "a bool unit", {**GENUINE, "decided_units": [True]}
    yield "an unknown unit", {**GENUINE, "decided_units": ["a", "zz"]}
    yield "max_choice_rules a bool", {**GENUINE, "max_choice_rules": True}
    yield "max_choice_rules a string", {**GENUINE, "max_choice_rules": "1"}
    yield "max_choice_rules negative", {**GENUINE, "max_choice_rules": -1}
    yield "max_choice_rules a float", {**GENUINE, "max_choice_rules": 1.0}
    yield "a list answer", [GENUINE]
    yield "a null answer field set", {"decided": ["a"]}


@pytest.mark.parametrize("name, answer", list(_mutations()), ids=[n for n, _ in _mutations()])
def test_a_malformed_answer_is_refused_never_summed(name, answer):
    with pytest.raises(VEError):
        L.share(UNITS, len(SOURCE), answer)


@pytest.mark.parametrize("outside", [["zz"], ["a", "a"], "a", [7], None])
def test_the_units_checked_outside_are_checked_too(outside):
    if outside is None:
        assert L.share(UNITS, len(SOURCE), GENUINE, outside)["decided_bytes_checked_outside"] == 0
        return
    with pytest.raises(VEError):
        L.share(UNITS, len(SOURCE), GENUINE, outside)


def test_the_cli_reads_the_document_spans(tmp_path, capsys):
    path = write_doc(tmp_path, SOURCE, [unit("a", 0, A, content={"ast": ["top"]}),
                                        unit("b", A, B, content={"ast": ["top"]}),
                                        unit("c", B, len(SOURCE), ["unformalised", "future_profile"],
                                             {"unformalised": "future_profile"})])
    answer = tmp_path / "answer.json"
    answer.write_text(json.dumps({"decided_units": ["a", "b"]}))
    assert L.main([str(path), "--answer", str(answer)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["decided_bytes"] == B and out["source_bytes"] == len(SOURCE)
    assert L.main([str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["decided_bytes"] == 0
    answer.write_text(json.dumps({"decided_units": ["zz"]}))
    assert L.main([str(path), "--answer", str(answer)]) == 1
    assert "zz is not a unit of the document" in capsys.readouterr().err
    answer.write_bytes(b"\xff")
    assert L.main([str(path), "--answer", str(answer)]) == 1


@pytest.mark.parametrize("text", ["7", "true", "null", "[]", "{}", "[" * 10_000 + "]" * 10_000,
                                  '{"decided_units": ' + "[" * 10_000 + "]" * 10_000 + "}"])
def test_every_malformed_answer_file_is_a_refusal(tmp_path, capsys, text):
    """Each JSON node replaced by 7, true, null, [], {} or a 10,000-deep nest: only a refusal, exit 1."""
    path = write_doc(tmp_path, SOURCE, [unit("a", 0, len(SOURCE), content={"ast": ["top"]})])
    answer = tmp_path / "answer.json"
    answer.write_text(text)
    assert L.main([str(path), "--answer", str(answer)]) == 1
    assert capsys.readouterr().err.startswith("InvalidInput: ")
    # As the units checked outside, `[]` is a genuine empty list; every other value is refused.
    expected = 0 if text == "[]" else 1
    assert L.main([str(path), "--answer", str(write_answer(tmp_path, [])), "--checked-outside", str(answer)]) \
        == expected
    assert capsys.readouterr().err.startswith("InvalidInput: ") is bool(expected)


def write_answer(tmp_path, decided):
    path = tmp_path / "genuine.json"
    path.write_text(json.dumps({"decided_units": decided}))
    return path
