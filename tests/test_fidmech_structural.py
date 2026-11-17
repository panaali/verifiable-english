"""fid-mech-b4: structural mutants on the parsed rule (plan 5.1) and their equivalence (plan 2d; Opus round 2 point 9).

Every test here parses VE English, which asks Lean: each is marked `needs_lean` as tests/test_fidmech_adapters.py
marks its live test. The fixtures are 5 RSP-vocabulary blocks and 3 FSF-vocabulary rule blocks plus a premise block
(tests/data/fidmech/structural/), parsed in the frozen environments of tests/data/fidmech/wording-inputs/.
"""
from __future__ import annotations

import json
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

import pytest

from tools.fidmech import mutants as M
from tools.fidmech import structural as S

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data" / "fidmech"
LEAN_SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
needs_lean = pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
pytestmark = needs_lean
RSP, FSF = "anthropic-rsp", "safety-framework"
SELECTED = {RSP: {"Q1": ("f16-only-legal",)},
            FSF: {"A1": ("f4-check-r",), "A2": ("f4-check-r", "f2")}}
# A2's model holds only f4-check-r's own guard; "subsequent" holds in more items than "frontier", so a choice that
# did not skip the rule's own predicates would write "if both that proposal is subsequent and that proposal is
# subsequent" (Astra round 2, FSF f4-check-r).
ATOMS = {RSP: {"Q1": (("external_review_process", "s"), ("highly_capable", "s"), ("listed", "T1"))},
         FSF: {"A1": (("frontier", "p"), ("subsequent", "p")), "A2": (("subsequent", "p"),)}}


def files_of(document):
    return {p.name[:-4] if p.name.endswith(".py.txt") else p.name: p.read_text(encoding="utf-8")
            for p in sorted((DATA / "structural" / document).iterdir())}


@lru_cache(maxsize=None)
def env_of(document):
    from ve.softnorms import SoftEnvironment
    return SoftEnvironment(json.loads((DATA / "wording-inputs" / document / S.ENVIRONMENT).read_text()))


@lru_cache(maxsize=None)
def generated(document):
    return M.structural_mutants(document, files_of(document), env_of(document), SELECTED[document], ATOMS[document])


def by_id(document):
    return {r["id"]: r for r in generated(document)[0]}


def line(rec):
    """The mutant's rule line (the last line of its one edit)."""
    (edit,) = rec["edits"]
    return edit["replace"].splitlines()[-1]


EXPECTED = {
    "drop-conjunct": (f"{RSP}:rows-cond:drop-conjunct:1", "Rule 1. Every situation must have the plans of the "
                      "company about each threshold in place, if that threshold is listed."),
    "drop-unless": (f"{RSP}:f16-only-legal:drop-unless:1", "Rule 1. Every situation must not have material redacted "
                    "from the version given to external reviewers, if that situation is classified as "
                    "\"external_review_process\"."),
    "drop-disjunct": (f"{RSP}:f18-either:drop-disjunct:1", "Rule 1. Every situation must have the position of RSO "
                      "maintained, if that situation is noteworthy."),
    "drop-exception": (f"{RSP}:f12-board-approval:drop-exception:1", "{}"),
    "flip-force": (f"{RSP}:f12-board-approval:flip-force:1", "Rule 1. Every situation should have its Risk Report "
                   "approved by the Board as well as the LTBT, if that situation is classified as "
                   "\"marginal_major_role\"."),
    "add-guard-true": (f"{RSP}:f16-only-legal:add-guard-true:1", "Rule 1. Every situation must not have material "
                       "redacted from the version given to external reviewers, if both that situation is classified "
                       "as \"external_review_process\" and that situation is classified as \"highly_capable\", unless "
                       "either that situation is classified as \"legal_prohibition_redaction\" or that situation is "
                       "classified as \"legal_rights_redaction\", or both."),
    "rule-drop": (f"{RSP}:f12-final:rule-drop:1", "Rule 1. Every situation need not have its Risk Report approved by "
                  "the Board as well as the LTBT, if this is impossible."),
    "widen-quantifier": (f"{RSP}:rows-cond:widen-quantifier:1", "Rule 1. Every situation must have the plans of the "
                         "company about each threshold in place, if that situation has crossed that threshold."),
}


@pytest.mark.parametrize("op", S.OPS)
def test_each_op_writes_its_expected_mutant_back_as_ve_english(op):
    id_, expected = EXPECTED[op]
    rec = by_id(RSP)[id_]
    assert (rec["op"], rec["class"], rec["parse"], line(rec)) == (op, "structural", "ok", expected)


def test_the_fixtures_counts_per_op():
    counts = {op: row["mutants"] for op, row in M.counts(*generated(RSP)).items()}
    assert counts == {"drop-conjunct": 4, "drop-unless": 1, "drop-disjunct": 4, "drop-exception": 1, "flip-force": 5,
                      "add-guard-true": 1, "rule-drop": 5, "widen-quantifier": 1}
    report = generated(RSP)[1]
    assert report["duplicates"] == {"drop-conjunct": 1}  # rows-cond's one restricting conjunct is the widen
    assert report["no-item"] == ["rows-cond", "f12-final", "f12-board-approval", "f18-either"]
    assert not report["stillborn"] and not report["unrenderable"]


def test_every_find_occurs_once_and_every_mutant_parses_to_its_edit():
    for document in (RSP, FSF):
        files = files_of(document)
        for rec in generated(document)[0]:
            for edit in rec["edits"]:
                assert files[edit["file"]].count(edit["find"]) == 1
                assert edit["file_sha256"] == M.sha256_text(files[edit["file"]])
            assert rec["parse"] == "ok"


def test_the_guard_template_names_the_bound_variables_sort():
    """FSF rules are over proposals: the added guard says "that proposal", never "that situation"."""
    rec = by_id(FSF)[f"{FSF}:f4-check-r:add-guard-true:1"]
    assert line(rec) == ("Rule 1. Every proposal must be preceded by a determination of any substantial "
                         "modification, if both that proposal is subsequent and that proposal is frontier.")
    assert all("situation" not in line(r) for r in generated(FSF)[0] if r["where"] != "precedence")


def test_add_guard_true_never_picks_a_predicate_the_rule_uses():
    rule = S.parse(env_of(FSF), next(b.text for b in S.rule_blocks(files_of(FSF)[S.RULES]) if b.id == "f4-check-r"))
    ops = S.ops_of(rule, env_of(FSF), true_atoms=["subsequent"])
    assert [op for op, _, _ in ops if op == "add-guard-true"] == []
    for rec in generated(FSF)[0]:
        assert "subsequent and that proposal is subsequent" not in line(rec)
    assert S.guard_candidates(env_of(FSF), "f4-check-r", "proposal", SELECTED[FSF], ATOMS[FSF]) == [
        "subsequent", "frontier"]


def test_a_header_declared_exception_and_its_precedence_pair_are_each_dropped():
    recs = {r["id"]: r for r in generated(FSF)[0] if r["op"] == "drop-exception"}
    assert sorted(recs) == [f"{FSF}:f3:drop-exception:1", f"{FSF}:f3:drop-exception:2"]
    pair, header = recs[f"{FSF}:f3:drop-exception:1"], recs[f"{FSF}:f3:drop-exception:2"]
    assert (pair["where"], pair["edits"][0]["file"], pair["edits"][0]["replace"]) == ("precedence", "translation.py",
                                                                                     "{}")
    assert line(header).endswith("if this is impossible.") and header["where"] == "rule"
    assert generated(FSF)[1]["duplicates"] == {"rule-drop": 1}  # f3's rule-drop is the header exception's drop


def test_two_conjuncts_reordered_are_syntactic():
    files = files_of(FSF)
    block = next(b for b in S.rule_blocks(files[S.RULES]) if b.id == "f2")
    swapped = ('if both that proposal is frontier and that proposal is classified as "first_deployment".')
    edits = M.rule_edit(files, block, block.text.split(", if ")[0] + ", " + swapped)
    assert M.rule_equivalence(files, env_of(FSF), edits) == "syntactic"
    other = M.rule_edit(files, block, block.text.split(", if ")[0] + ", if that proposal is frontier.")
    assert M.rule_equivalence(files, env_of(FSF), other) is None


def test_flip_force_is_never_syntactic():
    """Opus round 2 point 9: SoftRule.to_dict keeps the mode; Norm.to_dict, which drops it, would call it equal."""
    for document in (RSP, FSF):
        flips = [r for r in generated(document)[0] if r["op"] == "flip-force"]
        assert flips and all(r["equivalent"] is None for r in flips)
    rule = S.parse(env_of(RSP), next(b.text for b in S.rule_blocks(files_of(RSP)[S.RULES]) if b.id == "rows-cond"))
    flipped = replace(rule, mode="default")
    assert rule.core.to_dict() == flipped.core.to_dict()
    assert not S.syntactic(rule, flipped)
    files = files_of(RSP)
    block = next(b for b in S.rule_blocks(files[S.RULES]) if b.id == "rows-cond")
    edits = M.rule_edit(files, block, block.text.replace(" must ", " should ", 1))
    assert M.rule_equivalence(files, env_of(RSP), edits) is None


def test_canonicalisation_sorts_nested_and_or_operands_and_keeps_over():
    rule = S.parse(env_of(RSP), next(b.text for b in S.rule_blocks(files_of(RSP)[S.RULES]) if b.id == "f16-only-legal"))
    core = rule.core
    swapped = replace(rule, core=replace(core, unless=(S.ast.Or(core.unless[0].right, core.unless[0].left),)))
    assert S.syntactic(rule, swapped)
    assert not S.syntactic(rule, replace(rule, core=replace(core, over=("f12-final",))))
