"""PS-E1 pre-call audit, scorer boundaries, runner caps and saved evidence. These tests never call a reader model."""
from collections import Counter
import copy
import json
from pathlib import Path
import shutil
import sys
import threading

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import lean_build

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "docs/presupposition/ps-e1"))
import e1_items  # noqa: E402
import e1_runner  # noqa: E402
import e1_score  # noqa: E402
import e1_stub  # noqa: E402

CFG, ITEMS, STUB = e1_score.config(), e1_items.load(), e1_stub.saved_table()
one_at_a_time = CFG | {"concurrency": 1}


def need_lean():
    if shutil.which("lake") is None:
        pytest.skip("lake is not available")
    lean_build("VE")


def first(rows, **want):
    return next(r for r in rows if all(r.get(k) == v for k, v in want.items()))


def test_audit_accepts_the_frozen_items_and_prompts_are_blind():
    e1_items.audit(ITEMS, CFG, STUB)
    assert e1_items.dumps(e1_items.build()) == e1_items.ITEMS.read_text()
    for item in ITEMS:
        body = e1_items.prompt(item)
        assert item["sentence"] in body and item["situation"] in body and item["question"] in body
        assert all(f"({k}) {v}" in body for k, v in item["options"].items()) and (item["heading"] or "") in body
        assert not any(w in body for w in (item["id"], "presupposition", "carrier", "proxy", "assumed", "conditioned"))


AUDIT_BREAKS = {
    "drop_item": lambda items, rows, cfg: items.pop(),
    "row_missing": lambda items, rows, cfg: rows.pop(),
    "a_kept_at_rule_act": lambda items, rows, cfg: first(items, cell="rule_act")["options"].update(a=e1_items.FALSE),
    "a_dropped_at_top": lambda items, rows, cfg: first(items, cell="top")["options"].pop("a"),
    "plain_b_at_rule": lambda items, rows, cfg: first(items, cell="rule_act")["options"].update(b=e1_items.SILENT),
    "plain_b_at_guard": lambda items, rows, cfg: first(items, cell="rule_guard")["options"].update(b=e1_items.SILENT),
    "e_at_top": lambda items, rows, cfg: first(items, cell="top")["options"].update(e=e1_items.TRUE),
    "e_missing_at_negated": lambda items, rows, cfg: first(items, cell="negated")["options"].pop("e"),
    "question": lambda items, rows, cfg: items[0].update(question="What does it say?"),
    "pre_not_in_c": lambda items, rows, cfg: items[0].update(pre="something else"),
    "key_swapped": lambda items, rows, cfg: items[0]["key"].update(a="assumed"),
    "same_stimulus": lambda items, rows, cfg: items[1].update(sentence=items[0]["sentence"], situation=items[0]["situation"]),
    "three_in_a_cell": lambda items, rows, cfg: first(items, **{"class": "factive", "cell": "negated"}).update(cell="top"),
    "class_on_other_row": lambda items, rows, cfg: cfg["mapping"].update(factive="plural"),
    "not_shallow": lambda items, rows, cfg: first(rows, cell="negated").update(shallow=False),
    "goal_holds_in_target": lambda items, rows, cfg: rows[0].update(goal=True),
    "control_goal_fails": lambda items, rows, cfg: first(rows, id="C01").update(goal=False),
    "control_key_flipped": lambda items, rows, cfg: first(items, id="C01").update(expected="a"),
    "filter_moved": lambda items, rows, cfg: first(items, id="C01").update(filter="or"),
    "proviso_close_holds": lambda items, rows, cfg: first(rows, id="V01").update(close=True),
    "no_whether": lambda items, rows, cfg: first(items, id="S01").update(sentence="Elm School is fine."),
    "negated_without_not": lambda items, rows, cfg: first(items, cell="negated").update(sentence="All is well."),
    "guard_without_if": lambda items, rows, cfg: first(items, cell="rule_guard").update(sentence="Sam must go."),
    "act_with_guard": lambda items, rows, cfg: first(items, cell="rule_act").update(sentence="If so, Sam must go."),
    "heading_lost": lambda items, rows, cfg: first(items, **{"class": "heading_noun_phrase"}).update(heading=None),
}


@pytest.mark.parametrize("name", sorted(AUDIT_BREAKS))
def test_audit_refuses(name):
    items, rows, cfg = copy.deepcopy(ITEMS), copy.deepcopy(STUB), copy.deepcopy(CFG)
    AUDIT_BREAKS[name](items, rows, cfg)
    with pytest.raises(ValueError):
        e1_items.audit(items, cfg, rows)


def test_saved_stub_table_is_leans_output_and_a_failing_guard_stops_the_generator():
    need_lean()
    assert e1_stub.compute(ITEMS) == STUB
    items = copy.deepcopy(ITEMS[:1])
    items[0]["lean"]["model"] = 'model [("entity", ["x"])] [("owner_of", [["x", "c"]])] [("c", "c")]'
    with pytest.raises(RuntimeError, match="lean refused"):
        e1_stub.compute(items)
    assert all(r["be_one_class"] is (r["cell"] in ("negated", "antecedent")) for r in STUB)


def cell(a, b, cls="factive", where="top", **row):
    pair = [i for i in ITEMS if i["class"] == cls and i["cell"] == where]
    base = {"a": 0, "b": 0, "c": 0, "d": 0}
    return e1_score.class_cell(CFG, pair, {pair[0]["id"]: base | a, pair[1]["id"]: base | b},
                               {r["id"]: r | row for r in STUB})


@pytest.mark.parametrize("x,y,listed", [(5, 40, False), (6, 40, True), (40, 5, False), (6, 6, True)])
def test_candidate_bar_is_6_of_40_on_each_item(x, y, listed):
    assert ("assumed" in cell({"c": x}, {"c": y})["candidates"]) is listed


@pytest.mark.parametrize("x,y,one", [(35, 40, None), (36, 40, "assumed"), (40, 35, None), (36, 36, "assumed")])
def test_one_reading_bar_is_36_of_40_on_both(x, y, one):
    assert cell({"c": x}, {"c": y})["one_reading"] == one


@pytest.mark.parametrize("x,y,empty", [(10, 10, False), (11, 0, True), (0, 11, True)])
def test_cannot_tell_above_10_of_40_on_either_item_admits_no_carrier(x, y, empty):
    got = cell({"c": 29, "d": x}, {"c": 29, "d": y})
    assert got["no_carrier"] is empty and (got["candidates"] == []) is empty


def test_b_and_e_are_one_class_only_where_the_stub_row_says_so():
    neg = {"where": "negated"}
    assert cell({"b": 3, "e": 3}, {"b": 3, "e": 3}, **neg)["candidates"] == ["conditioned"]
    alias = cell({"b": 30, "e": 6}, {"b": 30, "e": 6}, **neg)
    assert alias["candidates"] == ["conditioned", "in_place"] and alias["one_reading"] == "conditioned"
    assert cell({"b": 3, "e": 3}, {"b": 3, "e": 3}, be_one_class=False, **neg)["candidates"] == []
    apart = cell({"b": 3, "e": 36}, {"b": 3, "e": 36}, be_one_class=False, **neg)
    assert apart["candidates"] == ["in_place"] and apart["one_reading"] == "in_place"


def cc(cands, one=None, no=False, **share):
    return {"candidates": cands, "one_reading": one, "no_carrier": no, "shares": [share]}


def row_cell(*classes):
    return e1_score.row_cell(CFG, dict(enumerate(classes)))


def test_row_cell_union_order_ties_and_disagreement():
    got = row_cell(cc(["assumed"], conditioned=10, assumed=20), cc(["conditioned"], conditioned=30, assumed=5))
    assert got["cell"] == ["conditioned", "assumed"] and got["status"] == "open" and "disagree" in got["notes"][0]
    assert row_cell(cc(["assumed"], assumed=9), cc(["conditioned"], conditioned=9))["cell"] == ["assumed", "conditioned"]
    assert row_cell(cc(["asserted", "conditioned"], conditioned=9, asserted=9))["cell"] == ["conditioned", "asserted"]


def test_row_cell_one_reading_needs_every_class_and_a_no_carrier_class_empties_it():
    assumed = cc(["assumed"], "assumed", assumed=80)
    same = row_cell(assumed, assumed)
    assert same["cell"] == ["assumed"] and same["status"] == "one_reading"
    assert row_cell(assumed, cc(["conditioned"], "conditioned", conditioned=80))["status"] == "open"
    assert row_cell(assumed, cc(["assumed"], assumed=60))["status"] == "open"
    alias = row_cell(cc(["conditioned", "in_place"], "conditioned", conditioned=80, in_place=20))
    assert alias["cell"] == ["conditioned", "in_place"] and alias["status"] == "one_reading"
    empty = row_cell(cc([], None, True), assumed)
    assert empty["cell"] == [] and empty["status"] == "no_carrier"


def test_row_cell_obeys_cell_ok():
    both = row_cell(cc(["assumed", "asserted"], asserted=50, assumed=20))
    assert both["cell"] == ["assumed"] and "C3" in both["notes"][0]
    assert row_cell(cc(["in_place"], in_place=20))["cell"] == ["in_place", "conditioned"]


def counts():
    return {i["id"]: {**{k: 0 for k in i["options"]}, "b": 40} for i in ITEMS}


def analyse(c):
    return e1_score.analyse(CFG, ITEMS, c, STUB)


def test_controls_bar_is_36_of_40_on_11_of_12():
    c = counts()
    controls = [i for i in ITEMS if i["family"] == "control"]
    for i in controls:
        c[i["id"]] = {**c[i["id"]], "b": 0, i["expected"]: 36}
    for wrong, passing, ok in ((0, 12, True), (1, 11, True), (2, 10, False)):
        for i in controls[:wrong]:
            c[i["id"]][i["expected"]] = 35
        out = analyse(c)
        assert (out["controls_passing"], out["controls_ok"]) == (passing, ok)


@pytest.mark.parametrize("n,ok", [(6, True), (7, False)])
def test_suspension_bar_is_at_most_6_of_40_on_each(n, ok):
    c = counts()
    c["S04"].update(c=n)
    assert analyse(c)["suspension_ok"] is ok


def generic_cells(c):
    return first(analyse(c)["table"], row="generic")["cells"]


@pytest.mark.parametrize("x,y,gains", [(5, 6, False), (6, 5, False), (6, 6, True)])
def test_proviso_adds_unconditional_only_at_6_of_40_on_both(x, y, gains):
    c = counts()
    c[first(ITEMS, **{"class": "factive", "cell": "consequent"})["id"]].update(b=35, c=5)  # open, not one-reading
    c["V05"].update(c=x)
    c["V06"].update(c=y)
    assert ("unconditional" in generic_cells(c)["consequent"]) is gains
    assert "unconditional" not in first(analyse(c)["table"], row="plural")["cells"]["consequent"]


@pytest.mark.parametrize("target_status", ["one_reading", "no_carrier"])
def test_proviso_adds_an_independent_candidate_even_when_target_is_decided(target_status):
    c = counts()
    c["V05"].update(c=40)
    c["V06"].update(c=40)
    if target_status == "no_carrier":
        c[first(ITEMS, **{"class": "factive", "cell": "consequent"})["id"]].update(b=29, d=11)
    out = analyse(c)
    assert "unconditional" in generic_cells(c)["consequent"]
    assert out["cells"]["generic", "consequent"]["status"] == "open"
    assert target_status in out["cells"]["generic", "consequent"]["notes"][0]
    table = out["table"]
    assert [t["row"] for t in table] == ["definite", "plural", "generic"]
    assert all(list(t["cells"]) == list(e1_score.ALL_CELLS) and t["cells"]["disjunct"] == [] for t in table)


def test_proviso_is_applied_to_every_row_from_its_own_pair():
    c = counts()
    for i in ITEMS:
        if i["family"] == "proviso":
            c[i["id"]].update(c=6)
    assert all("unconditional" in row["cells"]["consequent"] for row in analyse(c)["table"])


def record(item, t, answer="(b)", **over):
    return {"id": item["id"], "trial": t, "state": "final", "answer": answer, "charged_cw": 100, "prior_cw": 0,
            "model_calls": 1, "attempts": 1, "prompt_sha256": e1_items.sha(e1_items.prompt(item)),
            "system_sha256": e1_items.sha(CFG["reader_instruction"]), **over}


def test_tally_counts_errors_and_malformed_as_d_and_refuses_a_missing_trial():
    item = first(ITEMS, id="T-SD-ACT-a")
    records = {(item["id"], t): record(item, t) for t in range(1, 41)}
    assert e1_score.tally([item], records, 40)[0][item["id"]] == {"b": 40, "c": 0, "d": 0}
    for t, row in {2: record(item, 2, "", error="x"), 3: record(item, 3, "(a)"), 4: record(item, 4, "I think (b)"),
                   5: record(item, 5, " b. ")}.items():
        records[item["id"], t] = row
    got, errors, malformed = e1_score.tally([item], records, 40)
    assert got[item["id"]] == {"b": 37, "c": 0, "d": 3}
    assert errors == [f"{item['id']}#02"] and malformed == [f"{item['id']}#03", f"{item['id']}#04"]
    for broken in ({k: v for k, v in records.items() if k[1] != 40}, records | {(item["id"], 1): record(item, 1, state="outage")}):
        with pytest.raises(ValueError, match="no final record"):
            e1_score.tally([item], broken, 40)


def test_bound_accepts_a_true_record_and_refuses_a_rebound_or_outside_one():
    item = ITEMS[0]
    e1_score.bound(ITEMS, CFG, {(item["id"], 1): record(item, 1)})
    for key, row in {(item["id"], 41): record(item, 41), ("absent", 1): record(item, 1),
                     (item["id"], 2): record(item, 2, prompt_sha256="0"), (item["id"], 3): record(item, 3, system_sha256="0")}.items():
        with pytest.raises(ValueError):
            e1_score.bound(ITEMS, CFG, {key: row})


def test_table_ok_is_leans_answer_both_ways():
    need_lean()
    def table(where, cands):
        return [{"row": "x", "cells": {c: cands if c == where else [] for c in e1_score.ALL_CELLS}}]
    assert e1_score.table_ok(table("negated", ["conditioned", "in_place"]))
    assert e1_score.table_ok(table("consequent", ["assumed", "unconditional"]))
    for where, cands in (("negated", ["assumed", "asserted"]), ("negated", ["in_place"]), ("rule_act", ["asserted"]),
                         ("top", ["in_place", "conditioned"]), ("top", ["unconditional"])):
        assert not e1_score.table_ok(table(where, cands))


def ok(cw=100, model="claude-sonnet-5-5"):
    usage = {"input_tokens": cw - 3, "output_tokens": 3, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
             "fallback_credit": None}
    return 0, {"subtype": "success", "is_error": False, "result": "(b)", "usage": usage, "modelUsage": {model: {}}}, ""


DOWN = (1, {"raw_stdout": "limit"}, "")


class Fake:
    def __init__(self, *results, together=0):
        self.results, self.calls, self.threads, self.lock = iter(results), [], set(), threading.Lock()
        self.together = threading.Barrier(together, timeout=HANG_TIMEOUT) if together else None

    def __call__(self, cfg, item, account):
        with self.lock:
            self.calls.append(item["id"])
            self.threads.add(threading.get_ident())
            early = len(self.calls) <= 4
        if self.together and early:
            self.together.wait()
        with self.lock:
            return next(self.results, None) or ok()


def run(tmp_path, fake, items=ITEMS[:1], cfg=CFG):
    return e1_runner.run(items, cfg, tmp_path, call=fake, pick=lambda: "/acct/claude-x", head="h", frame=ITEMS)


def test_runner_runs_every_trial_at_most_four_at_once_and_resumes(tmp_path):
    fake = Fake(together=4)  # four calls overlap; one call at a time per thread, so four threads mean at most four
    assert run(tmp_path, fake, ITEMS[:2]) == "done"
    assert Counter(fake.calls) == {ITEMS[0]["id"]: 40, ITEMS[1]["id"]: 40} and len(fake.threads) == 4
    records = e1_score.load_records(tmp_path)
    assert len(records) == 80 and all(r["state"] == "final" and r["answer"] == "(b)" for r in records.values())
    (tmp_path / ITEMS[0]["id"] / "07.json").unlink()
    again = Fake()
    assert run(tmp_path, again) == "done" and again.calls == [ITEMS[0]["id"]]
    path = tmp_path / ITEMS[0]["id"] / "08.json"
    path.write_text(json.dumps(json.loads(path.read_text()) | {"prompt_sha256": "0"}))
    with pytest.raises(ValueError, match="rebound"):
        run(tmp_path, Fake())


def test_runner_redispatches_a_crashed_trial_and_keeps_its_reserve(tmp_path):
    item = ITEMS[0]
    row = record(item, 1, state="dispatched", charged_cw=None)
    e1_runner.save(tmp_path / item["id"] / "01.json", row)
    assert e1_runner.spent({(item["id"], 1): row}) == (1, e1_runner.RESERVE_CW)
    assert run(tmp_path, Fake()) == "done"
    got = e1_score.load_records(tmp_path)[item["id"], 1]
    assert (got["prior_cw"], got["attempts"], got["model_calls"]) == (e1_runner.RESERVE_CW, 2, 2)


@pytest.mark.parametrize("cap,n,status", [(40, 40, "done"), (39, 39, "cap")])
def test_runner_call_cap(tmp_path, cap, n, status):
    fake = Fake()
    assert run(tmp_path, fake, cfg=CFG | {"call_cap": cap}) == status and len(fake.calls) == n


def test_runner_cw_cap_stops_before_the_reserve_can_pass_it(tmp_path):
    fake = Fake()
    cap = 1000 + e1_runner.DISPATCH_CW
    assert run(tmp_path, fake, cfg=one_at_a_time | {"cw_cap": cap}) == "cap"
    assert len(fake.calls) == 11  # at 1,000 the 11th still fits with its reserve; at 1,100 the 12th does not
    assert e1_runner.spent(e1_score.load_records(tmp_path))[1] == 1100
    assert run(tmp_path / "wide", Fake(), cfg=one_at_a_time | {"cw_cap": 10 ** 7}) == "done"


def test_runner_refuses_a_call_without_its_full_dispatch_allowance(tmp_path):
    fake = Fake(ok(e1_runner.RESERVE_CW + 1))
    assert run(tmp_path, fake, cfg=one_at_a_time | {"cw_cap": e1_runner.RESERVE_CW,
                                                    "trials_per_item": 1}) == "cap"
    assert fake.calls == [] and e1_runner.spent(e1_score.load_records(tmp_path)) == (0, 0)


def test_runner_refuses_a_prompt_outside_the_dispatch_envelope(tmp_path):
    fake = Fake()
    cfg = one_at_a_time | {"reader_instruction": "x" * e1_runner.MAX_PROMPT_BYTES}
    assert run(tmp_path, fake, cfg=cfg) == "cap"
    assert fake.calls == []


def test_runner_stops_on_reported_per_call_exhaustion_and_preserves_the_usage(tmp_path):
    fake = Fake(ok(e1_runner.DISPATCH_CW + 1))
    assert run(tmp_path, fake, cfg=one_at_a_time | {"cw_cap": e1_runner.DISPATCH_CW}) == "cap"
    assert len(fake.calls) == 1
    assert e1_runner.spent(e1_score.load_records(tmp_path)) == (1, e1_runner.DISPATCH_CW + 1)


def test_runner_applies_dispatch_allowance_to_a_resumed_run(tmp_path):
    item = ITEMS[0]
    e1_runner.save(tmp_path / item["id"] / "01.json", record(item, 1, charged_cw=100))
    fake = Fake()
    assert run(tmp_path, fake, cfg=one_at_a_time | {"trials_per_item": 2,
                                                    "cw_cap": e1_runner.DISPATCH_CW}) == "cap"
    assert fake.calls == []


def test_pilot_projection_against_the_cap():
    item = ITEMS[0]
    def measured(cw):
        return e1_runner.project(item, CFG, {(item["id"], t): record(item, t, charged_cw=cw) for t in range(1, 41)})
    at = measured(3472)
    assert at["cw_per_call"] == 3472 and at["projection"] == 14_999_040 and at["within_cap"]
    assert not measured(3473)["within_cap"]


def test_main_runs_the_audit_first_and_refuses_a_run_without_a_pilot_within_the_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(e1_runner, "committed", lambda: "h")
    monkeypatch.setattr(e1_runner, "run", lambda *a, **k: pytest.fail("called"))
    monkeypatch.setattr(e1_runner, "PILOT", tmp_path / "pilot.json")
    assert "no pilot" in e1_runner.main(["--run"])
    (tmp_path / "pilot.json").write_text(json.dumps({"within_cap": False}))
    assert "no pilot" in e1_runner.main(["--run"])
    monkeypatch.setattr(e1_items, "load", lambda: ITEMS[:-1])
    with pytest.raises(ValueError):
        e1_runner.main(["--pilot"])


def test_committed_refuses_a_dirty_frozen_file(monkeypatch):
    monkeypatch.setattr(e1_runner.subprocess, "run", lambda *a, **k: type("Done", (), {"stdout": b"other"}))
    with pytest.raises(RuntimeError, match="before reader calls"):
        e1_runner.committed()


def test_outage_is_retried_and_three_failures_in_a_row_stop(tmp_path):
    never_started = (-1, e1_runner.NeverStarted(), "")
    fake = Fake(never_started)
    assert run(tmp_path, fake, cfg=one_at_a_time) == "done" and len(fake.calls) == 41
    got = e1_score.load_records(tmp_path)[ITEMS[0]["id"], 1]
    assert (got["attempts"], got["state"], got["answer"], got["model_calls"]) == (2, "final", "(b)", 1)
    fake = Fake(never_started, never_started, never_started)
    assert run(tmp_path / "s", fake, cfg=one_at_a_time).startswith("stopped") and len(fake.calls) == 3
    records = e1_score.load_records(tmp_path / "s")
    assert all(r["state"] == "outage" and r["model_calls"] == 0 for r in records.values())
    assert e1_runner.spent(records)[1] == 3 * e1_runner.RESERVE_CW


@pytest.mark.parametrize("wrapper", [DOWN[1], {"_never_started": True},
                                     {**ok()[1], "usage": None}, {**ok()[1], "modelUsage": None},
                                     {**ok()[1], "modelUsage": [{"bad": "shape"}]},
                                     {**ok()[1], "modelUsage": {1: {}}},
                                     {**ok()[1], "usage": {k: 0 for k in e1_runner.USAGE_KEYS}},
                                     {**ok()[1], "usage": {**ok()[1]["usage"], "output_tokens": 0},
                                      "subtype": "error_during_execution", "is_error": True, "result": ""}])
def test_ambiguous_cli_failure_is_a_final_call_error_without_retry(tmp_path, wrapper):
    fake = Fake((1, wrapper, ""))
    assert run(tmp_path, fake, cfg=one_at_a_time | {"call_cap": 1, "trials_per_item": 1}) == "done"
    assert len(fake.calls) == 1
    got = e1_score.load_records(tmp_path)[ITEMS[0]["id"], 1]
    assert got["state"] == "final" and got["model_calls"] == 1
    assert e1_score.letter(ITEMS[0], got) == ("d", "error")
    if e1_runner.usage_cw(wrapper) == 0:
        assert got["charged_cw"] == e1_runner.RESERVE_CW


def test_third_attempt_of_an_outage_is_a_final_call_error(tmp_path):
    fake = Fake(*[(-1, e1_runner.NeverStarted(), "")] * 3)
    assert run(tmp_path, fake, cfg=one_at_a_time | {"trials_per_item": 1}).startswith("stopped") and len(fake.calls) == 3
    got = e1_score.load_records(tmp_path)[ITEMS[0]["id"], 1]
    assert got["state"] == "final" and got["prior_cw"] == 2 * e1_runner.RESERVE_CW
    assert e1_score.letter(ITEMS[0], got) == ("d", "error")


@pytest.mark.parametrize("result,why", [(ok(model="claude-haiku-5-5"), "exclusively"), ((1, ok()[1], ""), "exit 1"),
                                        ((0, {**ok()[1], "is_error": True}, ""), "unsuccessful"),
                                        ((0, {**ok()[1], "result": 7}, ""), "not text")])
def test_a_call_that_reached_the_model_but_failed_is_an_error_at_once(result, why):
    answer, error, outage = e1_runner.classify(result[0], result[1], CFG["model"])
    assert answer == "" and why in error and outage is False
    assert e1_runner.classify(*ok()[:2], CFG["model"]) == ("(b)", None, False)


def test_zero_output_success_is_an_error_not_an_outage():
    wrapper = copy.deepcopy(ok()[1])
    wrapper["usage"]["output_tokens"] = 0
    assert e1_runner.classify(0, wrapper, CFG["model"]) == ("", "success with zero output tokens", False)


@pytest.mark.parametrize("key,value", [("input_tokens", True), ("output_tokens", None), ("input_tokens", -1),
                                       ("cache_read_input_tokens", "7")])
def test_malformed_usage_is_no_reported_usage(key, value):
    assert e1_runner.usage_cw(ok(100)[1]) == 100
    wrapper = copy.deepcopy(ok()[1])
    wrapper["usage"][key] = value
    assert e1_runner.usage_cw(wrapper) is None and e1_runner.classify(0, wrapper, CFG["model"])[2] is False


def test_paid_credit_fallback_and_picker_failure_stop_the_run(tmp_path):
    credit = copy.deepcopy(ok())
    credit[1]["usage"]["fallback_credit"] = {"amount": 1}
    fake = Fake(credit)
    assert run(tmp_path, fake, cfg=one_at_a_time).startswith("stopped: paid-credit") and len(fake.calls) == 1
    assert e1_score.letter(ITEMS[0], e1_score.load_records(tmp_path)[ITEMS[0]["id"], 1]) == ("d", "error")
    def broken():
        raise RuntimeError("account picker unavailable")
    fake = Fake()
    status = e1_runner.run(ITEMS[:1], CFG, tmp_path / "p", call=fake, pick=broken, frame=ITEMS)
    assert status.startswith("stopped: account picker") and fake.calls == []


def test_reader_command_is_the_smallest_context_and_strips_api_keys(monkeypatch):
    command = e1_runner.reader_command(CFG, "body")
    assert command[:2] == ["claude", "-p"] and command[-1] == "body" and "--bare" not in command
    for flag, value in (("--model", "claude-sonnet-5-5"), ("--system-prompt", CFG["reader_instruction"]), ("--tools", ""),
                        ("--setting-sources", ""), ("--max-turns", "1")):
        assert command[command.index(flag) + 1] == value
    assert "--strict-mcp-config" in command and "--no-session-persistence" in command
    seen = {}
    def fake_run(cmd, **kw):
        seen.update(kw)
        assert not list(Path(kw["cwd"]).iterdir())
        return type("Done", (), {"stdout": json.dumps(ok()[1]), "stderr": "", "returncode": 0})
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("CLAUDE_EFFORT", "low")
    monkeypatch.setattr(e1_runner.subprocess, "run", fake_run)
    assert e1_runner.cli_call(CFG, ITEMS[0], "/acct/claude-x")[0] == 0
    assert "ANTHROPIC_API_KEY" not in seen["env"] and "CLAUDE_EFFORT" not in seen["env"] and seen["env"]["CLAUDE_CONFIG_DIR"] == "/acct/claude-x"
    assert seen["env"]["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] == str(e1_runner.MAX_OUTPUT_TOKENS)


@pytest.mark.parametrize("failure", ["timeout", "invalid_json", "spawn_error"])
def test_cli_failure_is_an_outage_only_when_the_process_never_started(monkeypatch, failure):
    def fake_run(cmd, **kw):
        if failure == "timeout":
            raise e1_runner.subprocess.TimeoutExpired(cmd, 1)
        if failure == "spawn_error":
            raise OSError("executable not found")
        return type("Done", (), {"stdout": "not json", "stderr": "", "returncode": 1})
    monkeypatch.setattr(e1_runner.subprocess, "run", fake_run)
    code, wrapper, _ = e1_runner.cli_call(CFG, ITEMS[0], "/acct/claude-x")
    assert e1_runner.classify(code, wrapper, CFG["model"])[2] is (failure == "spawn_error")


def test_saved_table_and_results_are_the_generators_output():
    if sum(1 for _ in e1_score.RAW.glob("*/*.json")) < CFG["call_cap"]:
        pytest.skip("the 4,320 raw answers are not saved yet")
    need_lean()
    table, results = e1_score.generate()
    assert e1_score.TABLE.read_text() == table and e1_score.RESULTS.read_text() == results
    assert e1_score.table_ok(json.loads(table)) and e1_score.LABEL in results


def test_generate_refuses_an_incomplete_raw_directory(tmp_path):
    e1_runner.save(tmp_path / ITEMS[0]["id"] / "01.json", record(ITEMS[0], 1))
    with pytest.raises(ValueError, match="no final record"):
        e1_score.generate(tmp_path)
