"""defs-repair-eligibility-1119: each source definition the rules depend on is carried word for word.

For each kept row of the definitions-carried audit (reviews/defs-carried-1119/rows-eligibility.tsv),
the source sentence is read from usecases/eligibility/source/*.txt by its line span and must occur, after
the counter's quote normalisation (`omit_norm`), in the legend of every predicate the row names in the
shown environment.json, or in the gloss of bridge fact B1 in rules.json. Row 1 (pensionable age) was
dropped: its quote stops inside table 4 of Sch. 4 para. 1 (docs/usecases/eligibility/defs-repair-eligibility-1119/REPORT.md).
"""
from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from omission_rule import omit_norm

HERE = Path(__file__).resolve().parents[1] / "usecases" / "eligibility"
S1, S2, S3 = "uksi-2025-969-made.txt", "wfp-print.txt", "uksi-2005-3360-reg2.txt"
PARTNER = ("partner_of", "partners_throughout", "partner_at_home", "excluded_partner_benefit")
B1 = "rule B1"
# row -> (defined term, source pieces (file, first line, last line, the piece starts at this text or None),
#         carriers: predicate names, or B1 for the gloss of bridge fact B1)
ROWS = {
    "defs-eligibility-2-1119": ("qualifying week", [(S1, 40, 40, None), (S2, 38, 38, None)], (B1,)),
    "defs-eligibility-3-1119": ("partner", [(S1, 33, 33, None)], PARTNER),
    "defs-eligibility-4-1119": ("couple", [(S1, 22, 26, None)], PARTNER),
    "defs-eligibility-5-1119": ("polygamous marriage", [(S1, 35, 39, None)], PARTNER),
    "defs-eligibility-6-1119": ("residential care", [(S1, 52, 57, None)], ("in_residential_care",)),
    "defs-eligibility-7-1119": ("lives with", [(S1, 58, 58, None)], ("lives_with",)),
    "defs-eligibility-8-1119": ("care home", [(S1, 17, 21, None)], ("in_care_setting",)),
    "defs-eligibility-9-1119": ("independent hospital", [(S1, 28, 32, None)], ("in_care_setting",)),
    "defs-eligibility-10-1119": ("free in-patient treatment", [(S1, 27, 27, None), (S3, 9, 12, None)], ("inpatient",)),
    "defs-eligibility-11-1119": ("total income", [(S2, 140, 140, None), (S2, 141, 141, "You’ll need")], ("recovered",)),
    "defs-eligibility-12-1119": ("HMRC", [(S2, 139, 139, None)], ("recovered",)),
}


def source_piece(name, first, last, start):
    lines = (HERE / "source" / name).read_text(encoding="utf-8").split("\n")
    text = " ".join(lines[first - 1:last])
    if start is not None:
        assert start in text, (name, first, start)
        text = text[text.index(start):]
    return text


def carriers():
    env = json.loads((HERE / "environment.json").read_text(encoding="utf-8"))
    rules = json.loads((HERE / "rules.json").read_text(encoding="utf-8"))["rules"]
    shown = {name: entry["description"] for name, entry in env["vocabulary"]["predicates"].items()}
    [b1] = [r for r in rules if r["id"] == "B1"]
    shown[B1] = b1["gloss"]
    return shown, rules


@pytest.mark.parametrize("row", sorted(ROWS))
def test_each_carrier_holds_the_source_definition_word_for_word(row):
    term, pieces, names = ROWS[row]
    shown, _ = carriers()
    sentence = " ".join(source_piece(*piece) for piece in pieces)
    assert omit_norm(term) in omit_norm(sentence), (row, term)
    for name in names:
        assert omit_norm(sentence) in omit_norm(shown[name]), (row, name)


DELTA = (Path(__file__).resolve().parents[1] / "docs/usecases/eligibility/defs-repair-eligibility-1119"
         / "evidence/results-delta.json")


def test_saved_results_delta_keeps_verdicts_and_the_base_messages_names():
    """R1 evidence over the saved delta of results.json (DELTA.md): the answers, the summary and the
    mutant kills are equal, and every changed message keeps each name the base quoted and the base's
    position, if it had one."""
    delta = json.loads(DELTA.read_text(encoding="utf-8"))
    assert delta["summary_equal"] and delta["answers_equal"] and delta["mutants_equal"]
    assert set(delta["identity"]) == {"/environment_id", "/seconds"}
    assert delta["message_changes"]
    for change in delta["message_changes"]:
        base, head = change["base"], change["head"]
        assert base.split(":")[0] == head.split(":")[0], change  # the outcome word (rejected, no wording)
        for name in re.findall(r"'[^']+'|\"[^\"]+\"|\b[A-Z][A-Za-z]+\(", base):
            assert name in head, (change, name)
        if re.search(r"position \d+", base):
            assert re.search(r"position \d+", head), change


@pytest.mark.parametrize("row", sorted(ROWS))
def test_each_carrier_is_used_by_a_rule(row):
    """A legend counts only on a predicate some rule uses (the audit's carrier guard)."""
    _, rules = carriers()
    text = json.dumps([r["formula"] for r in rules if r["id"] != "B1"])
    for name in ROWS[row][2]:
        assert name == B1 or f'"{name}"' in text, (row, name)
