"""ET-E1's pre-registration and scorer (docs/events-time-causation/et-e1): hermetic, no model calls.

The pre-registration must be well formed (every expected answer an option, every wording of 2.7 asked), and the
scorer must apply the pre-registered bar and refuse answers that are not bound to a pre-registered item and sample.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parents[1] / "docs" / "events-time-causation" / "et-e1"
_spec = importlib.util.spec_from_file_location("et_e1_run", DIR / "run.py")
run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run)
SPEC = run.load_items(DIR / "items.json")
N = SPEC["samples_per_item"]


def _reply(letter):
    return f"Some reasoning.\nANSWER: {letter}"


def _answers(override=None):
    out = {(i["id"], k): _reply(i["expected"]) for i in SPEC["items"] for k in range(N)}
    out.update(override or {})
    return out


def _wrong(item_id):
    item = next(i for i in SPEC["items"] if i["id"] == item_id)
    return next(k for k, _ in run.options_of(SPEC, item) if k != item["expected"])


def test_preregistration_is_well_formed():
    items = SPEC["items"]
    assert len(items) == 30 and len({i["id"] for i in items}) == 30
    groups = {w["group"] for w in SPEC["wordings"]}
    assert sum(w["source"].startswith("2.7 row") for w in SPEC["wordings"]) == 13
    assert {i["group"] for i in items} == groups
    for item in items:
        assert item["expected"] in [k for k, _ in run.options_of(SPEC, item)], item["id"]
    by_id = {i["id"]: i for i in items}
    for u1, u2 in SPEC["until_pairs"]:
        assert (by_id[u1]["group"], by_id[u2]["group"]) == ("until-U1", "until-U2")


def test_parse_answer_takes_the_last_answer_line():
    assert run.parse_answer("ANSWER: A\nOn reflection.\nANSWER: C", "ABC") == "C"
    assert run.parse_answer("**ANSWER: B**", "ABC") == "B"
    assert run.parse_answer("ANSWER: E", "ABC") is None
    assert run.parse_answer("I think C.", "ABC") is None
    assert run.parse_answer(None, "ABC") is None


def test_all_correct_passes_every_bar():
    result = run.score(SPEC, _answers())
    assert {w["verdict"] for w in result["wordings"]} == {"PASS"}
    assert result["until"] == {"told_apart": 4 * N, "total": 4 * N, "verdict": "PASS"}


def test_one_miss_in_five_is_below_the_bar_and_one_in_ten_is_not():
    result = run.score(SPEC, _answers({("happens-on-other-day", 0): _reply(_wrong("happens-on-other-day")),
                                       ("before-same-day", 0): "no answer line"}))
    verdicts = {w["group"]: (w["correct"], w["total"], w["verdict"]) for w in result["wordings"]}
    assert verdicts["happens-on"] == (4, 5, "BELOW BAR")
    assert verdicts["is-before"] == (9, 10, "PASS")


def test_told_apart_needs_both_readings_of_the_same_sample():
    u1, u2 = SPEC["until_pairs"][0]
    result = run.score(SPEC, _answers({(u1, 0): _reply(_wrong(u1)), (u2, 1): _reply(_wrong(u2))}))
    assert result["until_pairs"][0]["told_apart"] == N - 2
    assert result["until"]["told_apart"] == 4 * N - 2
    assert result["until"]["verdict"] == "PASS"
    many = {(a, k): _reply(_wrong(a)) for a, _ in SPEC["until_pairs"][:1] for k in range(3)}
    assert run.score(SPEC, _answers(many))["until"]["verdict"] == "BELOW BAR"


def _write_raw(tmp_path, records):
    for name, rec in records.items():
        (tmp_path / name).write_text(json.dumps(rec))


def _all_records():
    return {f"{i['id']}__s{k}.json": {"item": i["id"], "sample": k, "reply": _reply(i["expected"])}
            for i in SPEC["items"] for k in range(N)}


def test_load_raw_accepts_the_complete_set(tmp_path):
    _write_raw(tmp_path, _all_records())
    assert run.load_raw(SPEC, tmp_path) == _answers()


@pytest.mark.parametrize("change", ["unknown_item", "sample_out_of_range", "sample_bool", "misnamed", "missing"])
def test_load_raw_refuses_unbound_answers(tmp_path, change):
    records = _all_records()
    first = f"{SPEC['items'][0]['id']}__s0.json"
    if change == "unknown_item":
        records["absent__s0.json"] = {"item": "absent", "sample": 0, "reply": "ANSWER: A"}
    elif change == "sample_out_of_range":
        records[f"{SPEC['items'][0]['id']}__s{N}.json"] = {"item": SPEC["items"][0]["id"], "sample": N, "reply": ""}
    elif change == "sample_bool":
        records[first]["sample"] = False
    elif change == "misnamed":
        records["copy.json"] = records[first]
    else:
        del records[first]
    _write_raw(tmp_path, records)
    with pytest.raises(ValueError):
        run.load_raw(SPEC, tmp_path)
