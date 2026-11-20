"""defs-carried-oos-measure-1119: the out-of-sample fixture, the drawn-flag list and the measurement script.

The condition test: tests/data/defs_carried/oos_cases.json (the out-of-sample cases) and oos_flags.json (the flags drawn
for the independent false-alarm judgement) load, and neither holds a (document, rule, term) of the 61-case fixture
(known_cases.json, all 389 of its cases). The other tests pin the script's counting rules on small made-up inputs:
the Wilson interval, the recall hit rule (a case with no passage is a miss), the seeded draw and its exclusions, and
the judge-reply parser and tally. No test runs a model or reads a live git diff.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data" / "defs_carried"
SCRIPT = ROOT / "docs" / "infra" / "defs-carried-oos-measure-1119" / "measure.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("defs_carried_oos_measure", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = _load_script()
KNOWN = json.loads((DATA / "known_cases.json").read_text(encoding="utf-8"))
OOS = json.loads((DATA / "oos_cases.json").read_text(encoding="utf-8"))
FLAGS = json.loads((DATA / "oos_flags.json").read_text(encoding="utf-8"))
KNOWN_KEYS = {(c["doc"], c["rule"], c["term"]) for c in KNOWN["cases"]}


def test_oos_fixture_and_flags_load_and_are_disjoint_from_the_known_cases():
    """CONDITION TEST: both files load, their counts match their contents, and no case or flag has the matching key
    (document, rule, term) of a known case; every case the fixture excludes as in-sample is a known key."""
    assert OOS["matching_key"] == ["doc", "rule", "term"]
    cases = OOS["cases"]
    assert len(cases) == OOS["counts"]["cases"] > 0
    assert len({c["case"] for c in cases}) == len(cases)
    assert {c["doc"] for c in cases} == {"openai-preparedness", "safety-framework", "anthropic-rsp"}
    assert not [c["case"] for c in cases if (c["doc"], c["rule"], c["term"]) in KNOWN_KEYS]
    ex = OOS["excluded_in_sample"]
    assert len(ex) == OOS["counts"]["excluded_in_sample"]
    assert all((e["doc"], e["rule"], e["term"]) in KNOWN_KEYS for e in ex)
    assert OOS["counts"]["pairs"] == len(cases) + len(ex)

    flags = FLAGS["flags"]
    assert len(flags) == FLAGS["drawn"] >= 100
    assert len({f["id"] for f in flags}) == len(flags)
    assert len({f["population_index"] for f in flags}) == len(flags)
    assert not [f["id"] for f in flags if (f["doc"], f["rule"], f["term"]) in KNOWN_KEYS]
    assert all(f["verdict"] not in ("CARRIED", "CARRIED-ASSUMED") for f in flags)
    assert all(f["doc"] and f["rule"] and f["verdict"] and f["passage"] for f in flags)


def test_the_fixture_records_the_row_files_it_was_built_from():
    """The three audit row files are committed verbatim and their hashes are the ones the fixture names."""
    for name, rec in OOS["row_files"].items():
        got = hashlib.sha256((DATA / "oos_audit" / name).read_bytes()).hexdigest()
        assert got == rec["sha256"], name
    rows = set()
    for name in OOS["row_files"]:
        for line in (DATA / "oos_audit" / name).read_text(encoding="utf-8").splitlines()[1:]:
            rows.add(line.split("\t")[0])
    assert {c["row"] for c in OOS["cases"]} <= rows
    assert len(rows) == OOS["counts"]["rows"]


def test_wilson_interval():
    assert m.wilson(0, 0) == (None, None)
    lo, hi = m.wilson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.2775, abs=1e-4)
    lo, hi = m.wilson(5, 10)
    assert (lo, hi) == (pytest.approx(0.2366, abs=1e-4), pytest.approx(0.7634, abs=1e-4))
    lo, hi = m.wilson(10, 10)
    assert lo == pytest.approx(0.7225, abs=1e-4) and hi == pytest.approx(1.0)


def _case(cid, row, passages=({"text": "x"},)):
    return {"case": cid, "row": row, "doc": "d", "rule": cid.split(":")[1], "term": "t", "passages": list(passages)}


def _known(cid, hit, reach, verdict):
    return {"case": cid, "hit": hit, "reach": reach, "verdict": verdict, "best_run": [], "tokens": [], "where": []}


def test_recall_counts_a_hit_only_when_reached_with_a_verdict_below_carried():
    fx = {"cases": [_case("r1:a", "r1"), _case("r1:b", "r1"), _case("r2:a", "r2"), _case("r3:a", "r3"),
                    _case("r4:a", "r4", passages=())]}
    rep = {"tree": {"kind": "test"}, "seconds": 0.0, "documents": {"d": {"known": [
        _known("r1:a", True, "parsed", "NOT CARRIED"),
        _known("r1:b", False, "term-not-in-rule", "NOT CARRIED"),
        _known("r2:a", False, "parsed", "CARRIED"),
        _known("r3:a", False, "rule-missing", "NOT CARRIED"),
        _known("r4:a", True, "parsed", None),          # the tool's own hit test passes a case with no passage
    ]}}}
    t = m.tabulate_recall(fx, rep)
    per = {p["case"]: p for p in t["per_case"]}
    assert [c for c, p in per.items() if p["hit"]] == ["r1:a"]
    assert per["r4:a"]["reason"].startswith("no passage")
    assert per["r1:b"]["reason"] == "never reached: term-not-in-rule"
    assert per["r2:a"]["reason"] == "tool verdict CARRIED"
    assert (t["hits"], t["cases"], t["findings_detected"], t["findings"]) == (1, 5, 1, 4)
    assert t["missed_findings"] == ["r2", "r3", "r4"]
    assert t["verdict_only"]["pairs_below_carried"] == 3


def _report(pairs):
    entries = [{"id": "M1", "file": "s.md", "line": 1, "marker": "means", "passage": "p"}]
    return {"tree": {"kind": "test"}, "documents": {"d": {"marker_entries": entries, "pairs": pairs}}}


def _pair(rule, term, verdict):
    return {"entry": "M1", "rule": rule, "term": term, "verdict": verdict, "phrase": "p", "via": "name",
            "best_run": 1, "tokens": 3}


def test_draw_excludes_known_keys_and_passing_pairs_and_is_seeded():
    pairs = [_pair(f"R{i}", "t", "NOT CARRIED") for i in range(30)]
    pairs += [_pair("K", "t", "FRAGMENT"), _pair("C", "t", "CARRIED"), _pair("A", "t", "CARRIED-ASSUMED")]
    rep = _report(pairs)
    d1 = m.draw(rep, 10, 7, {("d", "K", "t")})
    d2 = m.draw(rep, 10, 7, {("d", "K", "t")})
    assert d1 == d2
    assert d1["population"] == 30 and d1["excluded_known_keys"] == 1
    assert {f["rule"] for f in d1["flags"]} <= {f"R{i}" for i in range(30)}
    assert len({f["rule"] for f in d1["flags"]}) == 10
    assert m.draw(rep, 10, 8, {("d", "K", "t")})["flags"] != d1["flags"]


def test_judge_replies_are_parsed_and_tallied_without_edits():
    text = ("F001 | CARRIED | legend says it\n"
            "noise line\n"
            "**F002 | NOT CARRIED | missing**\n"
            "F003 | UNSURE | cannot tell\n"
            "F001 | NOT CARRIED | a second line for F001 is ignored\n"
            "F004 | MAYBE | not a verdict\n")
    got = m.parse_judge(text)
    assert got == {"F001": ("CARRIED", "legend says it"), "F002": ("NOT CARRIED", "missing"),
                   "F003": ("UNSURE", "cannot tell")}
    flags = {"flags": [{"id": f"F00{i}", "doc": "d", "rule": "r", "term": "t", "verdict": "NOT CARRIED"}
                       for i in range(1, 5)]}
    t = m.tally(flags, got)
    assert (t["judged"], t["carried"], t["unsure"], t["not_carried"]) == (3, 1, 1, 1)
    assert t["unjudged"] == ["F004"]
    assert t["false_alarm_rate"]["unsure_not_false_alarm"][:2] == [1, 3]
    assert t["false_alarm_rate"]["unsure_as_false_alarm"][:2] == [2, 3]
    assert t["false_alarm_rate"]["unsure_dropped"][:2] == [1, 2]
    d = m.parse_judge("F001 | DEFINES | x\nF002 | DOES NOT DEFINE | y\nF003 | DEFINES | z\n", m.DEF_LINE)
    b = m.tally(flags, got, d)["supplementary_definition_pass"]
    assert b["broad_false_alarm"][:2] == [2, 3]          # F001 shown anyway, F002 defines nothing
    assert b["broad_false_alarm_unsure_as_false_alarm"][:2] == [3, 3]
