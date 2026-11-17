"""fid-mech-b5: kill tables and denominators (plan 2e), units passing the stated checks (plan 8), the plant and defect
loader with rebase by unit text (plan 5.3), adjudication matching and CR (plan 8). No Lean: fixture cases and lines.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tools.fidmech import manifests as MF
from tools.fidmech import report as REP
from tools.fidmech import runner as RUN

ROOT = Path(__file__).resolve().parents[1]
B2 = ROOT / "tests/data/fidmech/b2"
B5 = ROOT / "tests/data/fidmech/b5"
DOC = "anthropic-rsp"


def line(mid, unit="u1", op="drop-conjunct", cls="structural", parse="ok", equivalent=None, K="survived", CR="not-read",
         new_hits=(), sentinel_ok=None, **text):
    """A results line; its sentinel confirmed the run unless it is not-run or `sentinel_ok` says otherwise."""
    v = {"K": K, **{c: text.get(c, "survived") for c in REP.TEXT}, "CR": CR}
    ok = K != "not-run" if sentinel_ok is None else sentinel_ok
    return {"record": {"id": mid, "verdict": v, "sentinel_ok": ok},
            "mutant": {"id": mid, "unit": unit, "op": op, "class": cls, "parse": parse, "equivalent": equivalent},
            "text": {"new_hits": list(new_hits), "error": None}}


def text(units, hits=(), users=None, sidecar=True):
    return {"units": list(units), "hits": [{"class": c, "block": b, "quote": q} for c, b, q in hits],
            "users": users or {}, "sidecar": sidecar}


# ---- kill tables and denominators -------------------------------------------------------------------------------

def test_each_instruments_denominator_leaves_out_what_did_not_run_and_none_is_split():
    lines = [line("a", K="killed"), line("b", K="inconclusive", D="killed"), line("c", K="error"),
             line("d", K="not-run"), line("e", K="survived", CR="missed"), line("f", K="survived"),
             line("g", K="not-run", L2="error")]
    row = REP.kill_table(lines)["drop-conjunct"]
    assert (row["K"]["killed"], row["K"]["decided"]) == (1, 3)
    assert row["K"]["left_out"] == {"inconclusive": 1, "error": 1, "not-run": 2}
    assert (row["D"]["killed"], row["D"]["decided"]) == (1, 7) and row["L2"]["decided"] == 6
    assert (row["CR"]["decided"], row["CR"]["left_out"]) == (1, {"not-read": 6})
    assert row["any"] == 2 and row["scored"] == 7
    assert row["none"] == {"every instrument ran": 1, "CR not read": 1, "some instrument did not run": 3}


def test_a_stillborn_mutant_is_listed_and_never_scored(tmp_path):
    lines = [line("ok", K="killed")]
    mutants = [{"id": "ok", "op": "drop-conjunct", "parse": "ok", "equivalent": None},
               {"id": "dead", "op": "flip-force", "parse": "stillborn", "equivalent": None}]
    batch = {"document": DOC, "status": "ok", "mutants": 2, "ran": 1, "not_run": 0, "selection": {}, "rows": {}}
    d, _ = REP.document_report({"batch": batch, "lines": lines, "mutants": mutants, "text": None})
    assert d["stillborn"] == {"count": 1, "by_op": {"flip-force": 1}}
    assert set(d["kill_table"]) == {"drop-conjunct", "all"} and d["kill_table"]["all"]["scored"] == 1
    # a stillborn line, should one reach the table, is not scored either
    assert REP.kill_table([line("x", parse="stillborn", K="killed")])["all"]["scored"] == 0


def test_syntactic_and_declared_equivalents_are_unscored_and_declared_ones_count_as_survivors_when_asked():
    lines = [line("a", K="killed"), line("s", equivalent="syntactic", K="killed"),
             line("d", equivalent="declared:reorder", K="killed", L1="killed")]
    assert REP.kill_table(lines)["all"]["scored"] == 1
    row = REP.kill_table(lines, declared_as_survivor=True)["all"]
    assert (row["scored"], row["K"]["killed"], row["K"]["decided"], row["any"]) == (2, 1, 2, 1)


# ---- units passing the stated checks ----------------------------------------------------------------------------

def test_an_incomplete_unit_is_never_passing_and_an_untested_one_never_passes_vacuously():
    lines = [line("a1", unit="u1", K="killed"), line("a2", unit="u1", K="inconclusive"),
             line("b1", unit="u2", K="killed"), line("b2", unit="u2", K="killed"),
             line("c1", unit="u3", K="killed"), line("c2", unit="u3", K="not-run"),
             line("d1", unit="u4", K="killed", op="flip-force"), line("d2", unit="u4", K="survived", op="flip-force"),
             line("w1", unit="u5", cls="wording", op="actor", K="killed"),
             line("e1", unit="u6", K="survived"), line("e2", unit="u6", K="error")]
    t = text(["u1", "u2", "u3", "u4", "u5", "u6"])
    u = REP.unit_status(lines, t)
    assert u["lists"]["status"] == {"u1": "incomplete", "u2": "passing", "u3": "incomplete", "u4": "failing",
                                    "u5": "untested", "u6": "failing"}
    assert (u["passing"], u["incomplete"], u["untested"], u["with_survivor"]) == (1, 2, 1, 2)
    assert REP.unit_status(lines, t, flip_force=False)["lists"]["status"]["u4"] == "untested"


def test_a_unit_with_a_baseline_text_hit_fails_and_l2_reaches_it_through_the_predicates_users():
    lines = [line("a", unit="u1", K="killed"), line("b", unit="u2", K="killed"), line("c", unit="u3", K="killed")]
    t = text(["u1", "u2", "u3"], hits=[("L1c", "u1", "q"), ("L2b", "pred", None), ("L4u", "main@0", "s")],
             users={"pred": ["u2"]})
    assert REP.unit_status(lines, t)["lists"]["status"] == {"u1": "failing", "u2": "failing", "u3": "passing"}
    assert set(REP.unit_status(lines, t, text_checks=False)["lists"]["status"].values()) == {"passing"}


def test_d_hits_are_every_uncovered_word_and_every_loss_entry_and_a_sidecarless_document_has_a_headline_without_d(
        tmp_path):
    case = tmp_path / DOC
    shutil.copytree(B2, case)
    sidecar = (case / "accounting.d1.txt").read_text()
    (case / "accounting.d1.txt").write_text(sidecar.replace("r-share | omits: nothing",
                                                            'r-share | omits: "final report" loss 1'))
    env = json.loads((case / "environment.d1.json").read_text())
    env["vocabulary"]["predicates"]["records_kept"]["regulated"]["act"] = "{0} keep records"
    env["vocabulary"]["predicates"]["records_kept"]["description"] = (
        'records are kept at {0}; section 1: "We will keep records of every review."')
    (case / "environment.d1.json").write_text(json.dumps(env))
    (case / "rules.d1.ve").write_text((case / "rules.d1.ve").read_text().replace(
        "must keep records of every review.", "must keep records."))
    tc = RUN.TextChecks(case, (case / "source.txt").read_bytes(), case / "fidmech/boundaries.json")
    d = sorted((h.block, h.quote) for h in tc.hits if h.cls == "D")
    assert ("r-share", "loss 1: final report") in d and ("r-records", "review") in d
    t = {"units": tc.units, "users": tc.users, "sidecar": tc.sidecar,
         "hits": [h.to_dict() for h in tc.hits]}
    lines = [line(u, unit=u, K="killed") for u in tc.units]
    assert REP.unit_status(lines, t)["lists"]["status"]["r-share"] == "failing"
    assert REP.unit_status(lines, t, with_d=False)["lists"]["status"]["r-share"] == "passing"
    batch = {"document": DOC, "status": "ok", "mutants": 0, "ran": 0, "not_run": 0, "selection": {}, "rows": {}}
    t.update({"counts": {}, "levers": {}})
    with_sidecar, _ = REP.document_report({"batch": batch, "lines": lines, "mutants": [], "text": t})
    without, _ = REP.document_report({"batch": batch, "lines": lines, "mutants": [], "text": {**t, "sidecar": False}})
    assert "without D (no sidecar)" not in with_sidecar["units"]
    assert without["units"]["without D (no sidecar)"]["passing"] > without["units"]["all ops"]["passing"]


def test_the_report_says_units_passing_the_stated_checks_and_never_calls_them_faithful():
    batch = {"document": DOC, "status": "ok", "mutants": 1, "ran": 1, "not_run": 0,
             "selection": {"rule_blocks": 2, "in_no_item": ["u2"]}, "rows": {}}
    t = {**text(["u1", "u2"]), "counts": {}, "levers": {"sidecar": {"cleared": [], "added": []}}}
    d, _ = REP.document_report({"batch": batch, "lines": [line("a", K="killed")], "mutants": [], "text": t})
    md = REP.render({"documents": [d], "inputs_sha256": None})
    assert "Units passing the stated checks (L1, L2, L3, D, K-structural), all ops: 1 of 2" in md
    assert md.replace('Never "faithful"', "").lower().count("faithful") == 0
    assert "1 of 2 rule blocks are selected by no item (the adapter's rule ids); every K mutant of such a rule is " \
           "expected to survive K" in md and "measured K verdicts of their scored mutants: {}" in md


# ---- plants and real defects (plan 5.3) -------------------------------------------------------------------------

@pytest.fixture
def case(tmp_path):
    c = tmp_path / DOC
    shutil.copytree(B2, c)
    return c


def test_plants_rebase_by_unit_text_and_a_gone_unit_is_not_applicable_with_its_reason(case):
    plants = json.loads((B5 / "plants.json").read_text())
    records, rows = MF.plant_records(plants, DOC, case)
    status = {r["id"]: (r["status"], r.get("how") or r.get("reason")) for r in rows}
    assert status["PL:whole"] == ("applied", "applied whole")
    assert status["PL:lines"] == ("applied", "rebased by line")
    assert status["PL:gone"][0] == "not applicable" and "is gone from the file under test" in status["PL:gone"][1]
    assert status["CTL:reorder"][0] == "excluded"
    by = {r["id"]: r for r in records}
    assert set(by) == {f"{DOC}:plant:PL:whole", f"{DOC}:plant:PL:lines"}
    assert all(r["class"] == "plant" and r["equivalent"] is None for r in records)
    [edit] = by[f"{DOC}:plant:PL:lines"]["edits"]
    assert "keep records." in edit["replace"] and "of every review" in edit["find"]


def test_a_defect_without_a_repair_is_unscored_and_a_later_change_is_never_read_as_its_repair(case):
    defects = json.loads((B5 / "defects.json").read_text())
    records, rows = MF.defect_records(defects, DOC, case)
    status = {r["id"]: (r["status"], r.get("how") or r.get("reason")) for r in rows}
    assert status["D:norepair"][0] == "no repair yet"
    assert status["D:later"][0] == "not applicable" and "never read as the repair" in status["D:later"][1]
    assert status["D:deleted"][0] == "not applicable" and "the repair deleted legend of old_pred" in status["D:deleted"][1]
    assert status["D:applied"] == ("applied", "applied whole")
    [rec] = records
    assert rec["class"] == "real-defect" and '"We will keep records ..."' in rec["edits"][0]["replace"]
    counts = REP.plant_counts(REP.plant_rows([line(rec["id"], K="killed")], {"defects": rows}))["defects"]
    assert (counts["entries"], counts["applied"], counts["no repair yet"], counts["not applicable"]) == (4, 1, 1, 2)
    # VE gets the class of each reason, never the reason, which names the unit
    assert counts["not_applicable_by"] == {"the repaired text changed later": 1,
                                           "the repair deleted text the defect needs": 1}
    assert "r-publish" not in json.dumps(counts) and "old_pred" not in json.dumps(counts)
    assert (counts["K_killed"], counts["K_decided"], counts["any_killed"]) == (1, 1, 1)


def test_a_vocabulary_edit_regenerates_the_environment_from_the_edited_module():
    vocab = 'import json\nP = {"a": 1}\ndef text():\n    return json.dumps(P) + "\\n"\n'
    assert MF.environment_text(vocab) == '{"a": 1}\n'
    assert MF.environment_text(vocab.replace('"a": 1', '"a": 2')) == '{"a": 2}\n'


# ---- adjudication and CR (plan 8) -------------------------------------------------------------------------------

def finding(**kw):
    base = {"id": "F#1", "case": DOC, "unit": "u1", "fp1_key": "u1", "fp1": "fp1:aaaa", "allegation_class": "word dropped",
            "word": "final", "cited_text": "the final report", "verdict": "REAL-by-both"}
    return {**base, **kw}


@pytest.mark.parametrize("hit, findings, fp_now, outcome", [
    ({"class": "D", "block": "u1", "quote": "final"}, [finding()], {"u1": "fp1:aaaa"}, "confirmed"),
    ({"class": "D", "block": "u1", "quote": "final"}, [finding(verdict="NOT-by-both")], {"u1": "fp1:aaaa"},
     "contradicted"),
    ({"class": "D", "block": "u1", "quote": "final"}, [finding()], {"u1": "fp1:bbbb"}, "unadjudicated"),
    ({"class": "D", "block": "u1", "quote": "board"}, [finding()], {"u1": "fp1:aaaa"}, "unadjudicated"),
    ({"class": "L3w", "block": "u1", "quote": "final"}, [finding()], {"u1": "fp1:aaaa"}, "unadjudicated"),
    ({"class": "L1u", "block": "u1", "quote": "the final report"}, [finding(allegation_class="cut or short quote")],
     {"u1": "fp1:aaaa"}, "unadjudicated"),
    ({"class": "L1c", "block": "u1", "quote": "We will share the final report"},
     [finding(allegation_class="cut or short quote", cited_text="share the final report")], {"u1": "fp1:aaaa"},
     "confirmed"),
    ({"class": "D", "block": "u1", "quote": "loss 1: final report"}, [finding(verdict="split")], {"u1": "fp1:aaaa"},
     "unadjudicated"),
])
def test_a_hit_is_confirmed_or_contradicted_only_by_its_own_class_word_and_unchanged_unit(hit, findings, fp_now,
                                                                                           outcome):
    assert REP.adjudicate(hit, DOC, findings, {}, fp_now)[0] == outcome


def test_the_six_classes_without_an_allegation_are_always_unadjudicated():
    assert set(REP.NO_ALLEGATION) == {"L1m", "L1u", "L1a", "L2q", "L2a", "L4l"}
    assert not set(REP.NO_ALLEGATION) & set(REP.ALLEGATION)


def test_cr_fills_a_wording_mutant_only_on_its_unit_kind_text_and_fp1():
    lines = [line("w", unit="u1", cls="wording", op="qualifier"), line("w2", unit="u2", cls="wording", op="qualifier")]
    mutants = [{"id": "w", "edits": [{"find": "must keep all records", "replace": "must keep records"}]},
               {"id": "w2", "edits": [{"find": "must keep all records", "replace": "must keep records"}]}]
    entry = {"unit": "u1", "kind": "qualifier", "old": "all records", "new": "records", "found": True,
             "fp1": "fp1:aaaa"}
    fp_rows = [{"case": DOC, "role": "measured", "unit": "u1", "fp1": "fp1:aaaa"},
               {"case": DOC, "role": "measured", "unit": "u2", "fp1": "fp1:cccc"}]
    perunit = {"u1": {"recall_gate": {"mutants": [entry]}}, "u2": {"recall_gate": {"mutants": [
        {**entry, "unit": "u2", "fp1": "fp1:dddd"}]}}}
    n = REP.fill_cr(lines, mutants, REP._cr_entries(perunit), fp_rows, {"u1": "fp1:aaaa", "u2": "fp1:cccc"}, DOC)
    assert n == 1 and lines[0]["record"]["verdict"]["CR"] == "found" and lines[1]["record"]["verdict"]["CR"] == "not-read"
    lines[0]["record"]["verdict"]["CR"] = "not-read"
    assert REP.fill_cr(lines, mutants, [entry], fp_rows, {"u1": "fp1:eeee"}, DOC) == 0


def test_a_changed_line_that_stands_twice_is_not_rebased():
    text = "## a | x\nRule 1. Every situation must act.\n## b | y\nRule 1. Every situation must act.\n"
    assert MF.rebase(text, "## a | old\nRule 1. Every situation must act.", "## a | old\nRule 1. Every situation may act.") \
        == (None, "the changed text 'Rule 1. Every situation must act.' stands 2 times in the file under test")
    new, how = MF.rebase(text, "## a | x\nRule 1. Every situation must act.", "## a | x\nRule 1. Every situation may act.")
    assert how == "whole" and new.count("may act") == 1


# ---- a result no good sentinel confirmed (fid-mech-b5 review F1) ------------------------------------------------

INVALID_KILLED = dict(K="killed", sentinel_ok=False)


def test_an_invalid_k_is_left_out_of_every_k_denominator_and_counted_beside():
    """F1: a line whose sentinel failed (sentinel_ok false) reads INVALID, never its measured K: out of K decided,
    counted in the left-out K, no kill for any instrument, the unit incomplete, not a decided survivor."""
    lines = [line("a", K="killed"), line("b", **INVALID_KILLED), line("c", K="survived", sentinel_ok=False),
             line("d", K="error", sentinel_ok=False)]
    row = REP.kill_table(lines)["all"]
    assert (row["K"]["killed"], row["K"]["decided"]) == (1, 1)
    assert row["K"]["left_out"] == {"INVALID": 3}
    assert row["any"] == 1 and row["none"] == {"some instrument did not run": 3}
    # a missing or non-bool sentinel_ok is unconfirmed too (fail closed)
    odd = [line("e", K="killed"), line("f", K="killed")]
    del odd[0]["record"]["sentinel_ok"]
    odd[1]["record"]["sentinel_ok"] = 1
    assert REP.kill_table(odd)["all"]["K"]["left_out"] == {"INVALID": 2}


def test_a_unit_whose_mutant_is_invalid_is_incomplete_never_passing_or_failing_on_it():
    t = text(["u1", "u2"])
    lines = [line("a1", unit="u1", K="killed"), line("a2", unit="u1", **INVALID_KILLED),
             line("b1", unit="u2", K="killed"), line("b2", unit="u2", K="survived", sentinel_ok=False)]
    for kw in ({}, {"text_checks": False}, {"declared_as_survivor": True}):
        u = REP.unit_status(lines, t, **kw)
        assert u["lists"]["status"] == {"u1": "incomplete", "u2": "incomplete"} and u["with_survivor"] == 0


def test_a_declared_equivalent_counted_as_a_survivor_keeps_an_invalid_or_not_run_k():
    lines = [line("d1", equivalent="declared:x", **INVALID_KILLED), line("d2", equivalent="declared:x", K="not-run"),
             line("d3", equivalent="declared:x", K="killed")]
    row = REP.kill_table(lines, declared_as_survivor=True)["all"]
    assert (row["K"]["killed"], row["K"]["decided"], row["K"]["left_out"]) == (0, 1, {"INVALID": 1, "not-run": 1})


def test_the_document_report_reads_an_invalid_k_in_plants_blind_spot_unprobed_and_errors():
    batch = {"document": DOC, "status": "ok", "mutants": 4, "ran": 4, "not_run": 0,
             "selection": {"rule_blocks": 2, "in_no_item": ["u2"]},
             "rows": {"plants": [{"id": "P1", "status": "applied", "mutant": "p", "reason": ""}], "defects": []}}
    lines = [line("p", cls="plant", **INVALID_KILLED), line("k", unit="u2", **INVALID_KILLED),
             line("e", K="error", sentinel_ok=False), line("ok", K="killed")]
    lines[2]["record"]["kernel"] = {"error": "RuntimeError: boom"}
    d, rows = REP.document_report({"batch": batch, "lines": lines, "mutants": [], "text": None})
    assert d["K_invalid"] == 3
    assert rows["plants_and_defects"]["plants"][0]["K"] == "INVALID"
    assert rows["plants_and_defects"]["plants"][0]["any"] is False
    p = d["plants_and_defects"]["plants"]
    assert (p["K_killed"], p["K_decided"], p["K_invalid"], p["any_killed"]) == (0, 0, 1, 0)
    assert d["blind_spot"] == {"drop-conjunct": 2}  # k and e: no instrument killed them; ok was killed
    assert d["unprobed_rules"]["K"] == {"INVALID": 1}
    assert d["K_errors"] == {}
    md = REP.render({"documents": [d], "inputs_sha256": None})
    assert "4 run, 3 with an INVALID K (no good sentinel confirmed the run: left out of every K denominator)" in md


def test_only_records_k_reading_and_report_verdicts_read_a_records_verdicts():
    """The class of F1: a reader that takes verdict["K"] off a record skips the sentinel. In tools/fidmech only
    records.k_reading and report.verdicts read a record's verdict dict (report.fill_cr writes CR into it)."""
    import ast
    allowed = {("records.py", "k_reading"), ("report.py", "verdicts"), ("report.py", "fill_cr")}
    found = set()
    for path in sorted((ROOT / "tools/fidmech").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.Lambda)):
                continue
            for node in ast.walk(fn):
                if (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                        and node.slice.value == "verdict" and not (isinstance(node.value, ast.Name)
                                                                  and node.value.id == "f")):
                    found.add((path.name, getattr(fn, "name", "<lambda>")))
    assert found - allowed == set(), found - allowed
    assert ("records.py", "k_reading") in found and ("report.py", "verdicts") in found
