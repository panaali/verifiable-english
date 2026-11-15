"""Safety-framework use case: case alternatives and item-scoped facts (row safety-framework-case-alternatives).

(A) A PLAN 5 row that names a branch "or" another, or a class of levels, is one case whose `alternatives` give one
situation per level of the class each branch names; the item holds at a choice where it holds in every alternative
(G3, G7, G9). (B) measures-sl2plus is a fact block of rules.d1.ve headed with the items whose proofs read it (the F16
items); run.py loads it for those items only and names it in their records.
Ruling: reviews/dri-decisions-20261114-safety-framework-fidelity-fix-3.md items 3 and 5.
"""
import pytest

from tests.test_safety_framework import RESULTS, _own_modules, run, translation  # noqa: F401 (fixture)

SL2PLUS_ITEMS = ("B-L2/RECSEC", "B-L3/RECSEC", "B-L4/RECSEC", "B-L6/RECSEC", "B-L7/RECSEC", "C1", "C4")


def _levels(predicate):
    return sorted(atom[1] for atom in run.document_atoms() if atom[0] == predicate)


def _situations(case_id):
    return sorted((tuple(a["levels"]), a["activity"], tuple(map(tuple, a["findings"])))
                  for a in run.CASES[case_id]["alternatives"])


def test_g7_states_a_tcl_and_a_mitigated_ccl_risk():
    """PLAN.md:353 G7 "disclosure for a TCL or for a mitigated CCL risk": every TCL with no finding, and every CCL with
    its risk mitigated (OT2) and the OT11 findings unset."""
    tcl = [((level,), None, ()) for level in _levels("tracked")]
    ccl = [((level,), None, (("mitigates", "p", level),)) for level in _levels("critical")]
    assert len(tcl) == 2 and len(ccl) == 5
    assert _situations("G7") == sorted(tcl + ccl)


def test_g3_states_approaching_and_reaching_a_tcl():
    """PLAN.md:349 G3 "approaching or reaching a TCL (alert)"."""
    approaching = [((), None, (("approaches", "p", level),)) for level in _levels("tracked")]
    reaching = [((level,), None, ()) for level in _levels("tracked")]
    assert _situations("G3") == sorted(approaching + reaching)


def test_g9_states_every_tcl_and_ccl_model():
    """PLAN.md:355 G9 "covered (must not deploy) for T/CCL models": the TCL half beside the CCL half."""
    levels = _levels("tracked") + _levels("critical")
    assert _situations("G9-TCCL") == sorted(((level,), "EXT-NOGOV", ()) for level in levels)


@pytest.mark.parametrize("item_id,record", [("G3", None), ("G7", None), ("G9", "FORBIDS")])
def test_each_alternative_is_answered_and_the_answer_holds_in_every_one(item_id, record):
    """The saved results answer every alternative of the case, and the item's answer is the per-choice conjunction."""
    result = RESULTS["items"][item_id] if record is None else RESULTS["items"][item_id]["parts"][record]
    case = run.CASES[next(k["case"] for k in run.json.loads((run.HERE / "answer-key.json").read_text())["items"]
                          if k["id"] == item_id)]
    assert sorted(result["alternatives"]) == sorted(a["id"] for a in case["alternatives"])
    assert all(run.describe(r) == "ALL" for r in result["alternatives"].values())
    assert run.describe(result) == "ALL"
    assert next(r for r in RESULTS["comparison"] if r["id"] == item_id)["agree"]


def test_an_alternative_that_fails_makes_the_item_fail():
    """The item holds where it holds in every alternative: a second alternative where F19 asks for disclosure (a CCL
    with both OT11 findings, as K9-L2) leaves exactly that alternative's choices."""
    k9 = run.CASES["K9-L2"]
    disclosing = {"id": "X-K9", "levels": k9["levels"], "activity": k9["activity"], "findings": k9["findings"]}
    silent = dict(run.CASES["G7"]["alternatives"][0])
    alone = run.item_result("SILENT:DISC", disclosing)
    both = run.item_result("SILENT:DISC", {"id": "X", "alternatives": [silent, disclosing]})
    assert run.describe(run.item_result("SILENT:DISC", silent)) == "ALL" and run.describe(alone) != "ALL"
    assert run.result_set(both, alone["cone"]) == run.result_set(alone, alone["cone"])
    with pytest.raises(SystemExit, match="alternatives"):
        run.case_atoms(run.CASES["G7"])


def test_measures_sl2plus_is_scoped_to_the_items_that_read_it():
    """Not a premise of every item: a fact block of rules.d1.ve headed with the F16 items, named in exactly their
    records. N3 also names the F16 rules: its witness search does not load the block (each witness comes from a
    level that recommends the measure itself)."""
    assert "measures-sl2plus" not in {b.id for b in translation.read_blocks("facts.d1.ve")}
    block = next(b for b in translation.rule_fact_blocks() if b.id == "measures-sl2plus")
    assert block.when == tuple(("item", i) for i in SL2PLUS_ITEMS)
    named = {i for i, r in RESULTS["items"].items() if "measures-sl2plus" in r.get("own_premises", ())}
    assert named == set(SL2PLUS_ITEMS)
    on_f16 = {i for i, r in RESULTS["items"].items() if {"f16-ds", "f16-ds-strict"} & set(run.json.dumps(r).split('"'))}
    assert on_f16 - {"N3"} == set(SL2PLUS_ITEMS)
    assert "measures-sl2plus" not in RESULTS["items"]["N3"].get("own_premises", ())
    assert len(run.PREMISES("C1")) == len(run.PREMISES()) + 4 == RESULTS["cost"]["premises"] + 4


def test_the_f16_items_load_the_block_and_their_proofs_use_it():
    """At RS3 = Ds the F16 rule selects SL2+'s baseline and additional measures for B-L2 (2.1.1) only through the
    block; the same case without the item's premises selects SL2+ alone."""
    choice = run.full_choice((("RS3", "Ds"), ("RS3force", "default")))
    with_block, without = {}, {}
    run.answer("RECSEC", run.item_case("B-L2/RECSEC", run.CASES["B-L2"]), choice, detail=with_block)
    run.answer("RECSEC", run.CASES["B-L2"], choice, detail=without)
    assert with_block["measures"] == ["rand_security_level_2", "security_level_2_plus", "sl2_plus_additional_measures"]
    assert without["measures"] == ["security_level_2_plus"]
    saved = RESULTS["items"]["B-L2/RECSEC"]["details"]["RS3=Ds,RS3force=default"]["measures"]
    assert saved == with_block["measures"]
    assert RESULTS["invention_audit"]["untraced"] == [] and RESULTS["invention_audit"]["bridges"] == ["bridge-one-domain"]
