"""Tests for the week-set earnings item (row statute-ei-canada-weekset): a stated set of weeks at one amount
("weeks 1, 3, 5, ..., 25: $300.00 each") is ONE item of the record (make_cases.py, encode.py, encoding E3) and s. 14(4)
ranks over items (translation._rank_rules), so a two-amount interleaved year is 2 items, not one run per week.

SYNTHETIC cases only (written here; no question or answer of any sealed set). Each derived fact is proved by the
checker's own prover and every certificate and answer document is replayed in Lean (ve.backends.relay), so a pass of
the Lean tests means the Lean kernel admitted the rate document (no Lean limit is changed: lean/VE/Time/Document.lean
caps a quantity document at 1,000 graph nodes).

Run (repository root, with lean/.lake/build/bin/ve_service): .venv/bin/python -m pytest -q usecases/ei_canada/test_weekset.py
Fails on ecc971dbc4 (the frozen 141/141 build): no week-set form, so the parse stops. MEASURED there (not a test: one
run): the same 26-week year stated as 26 single-week runs gives a rate document of more than 1,000 graph nodes.
"""
from __future__ import annotations

import sys
import time
from fractions import Fraction
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import encode as E  # noqa: E402
import make_cases as MC  # noqa: E402
import run as RUN  # noqa: E402
import translation as T  # noqa: E402

NODE_LIMIT = 1000  # lean/VE/Time/Document.lean (quantity documents); read here, never changed


def synthetic(cid, weeks_text, n, rate="7.5", hours="1,200", myie="65,520.00", year=2026):
    """A synthetic encoder record in the writer's fixed fact form (make_cases.parse reads it)."""
    facts = " ".join([
        "Ana is an insured person who has made an initial claim for regular benefits.",
        f"If a benefit period is established for Ana, it would begin on 4 January {year}.",
        f"The regional rate of unemployment that applies to Ana is {rate}%.",
        f"Ana had {hours} hours of insurable employment in the qualifying period.",
        "Ana has had an interruption of earnings from employment.",
        f"Ana's insurable earnings in each week of the {n}-week qualifying period, not including any amount paid or "
        f"payable by reason of lay-off or separation from employment: {weeks_text}.",
        "No insurable earnings were paid or payable to Ana during the qualifying period by reason of lay-off or "
        "separation from employment.",
        f"The maximum yearly insurable earnings for {year} are ${myie}.",
    ])
    return MC.parse({"id": cid, "scope": "in", "facts": facts, "questions": [
        {"qid": f"{cid}-1", "kind": "Q1", "text": "Does Ana qualify under s. 7(2)?"},
        {"qid": f"{cid}-3", "kind": "Q3", "text": "What is Ana's rate of weekly benefits? (no rounding rule applies)"}]})


# --- the parse (make_cases.week_set) -------------------------------------------------------------------------------

def test_week_set_forms():
    assert MC.week_set("T", "1, 3, 5, ..., 25") == list(range(1, 26, 2))
    assert MC.week_set("T", "2, 4, …, 26") == list(range(2, 27, 2))
    assert MC.week_set("T", "1, 4 and 9") == [1, 4, 9]
    assert MC.week_set("T", "1, 4, 9") == [1, 4, 9]
    assert MC.week_set("T", "3, 6, ..., 12 and 15") == [3, 6, 9, 12, 15]
    assert MC.week_set("T", "1, 3, ..., 9, 11") == [1, 3, 5, 7, 9, 11]


@pytest.mark.parametrize("text", ["1, 3, ..., 50", "1, ..., 51", "3, 1", "1, 3, 3", "5", "1, 3, 4, ..., 9",
                                  "1, 3, ..., 9, 12", "1, 3, ..., 3", "0, 2", "1, 3, ... 9", "1,3", "1, two",
                                  "1, 3, ...", "1, 3, ..., 10", "1, 3, ..., 9 and 10", "..., 3, 5", "1, 3, ..., 7, ..., 11",
                                  "1, 3, ..., 5", "1, 3, 5, ..., 7"])
def test_week_set_refuses(text):
    with pytest.raises(ValueError):
        MC.week_set("T", text)


@pytest.mark.parametrize("weeks_text,why", [
    ("weeks 1, 3, 5: $300.00 each; weeks 2, 4: $500.00 each", "weeks not all given"),
    ("weeks 1, 3, 5: $300.00 each; weeks 2, 4, 5, 6: $500.00 each", "week 5 given twice"),
    ("weeks 1, 3, 5, 7: $300.00 each; weeks 2, 4, 6: $500.00 each", "week 7 outside"),
    ("weeks 4 to 2: $300.00 each; weeks 1, 5, 6: $500.00 each", "ends before it starts"),
    ("week 0: $1.00; weeks 1 to 6: $500.00 each", "week 0 outside"),
    ("weeks 0 to 3: $1.00 each; weeks 4 to 6: $500.00 each", "week 0 outside"),
    ("weeks 1 to 3: $1.00 each; weeks 3 to 6: $500.00 each", "week 3 given twice"),
])
def test_record_refuses_incomplete_or_overlapping_weeks(weeks_text, why):
    with pytest.raises(ValueError, match=why):
        synthetic("TBAD", weeks_text, 6)


def test_two_amount_interleaved_year_is_two_items():
    case = synthetic("T26", "weeks 1, 3, 5, ..., 25: $300.00 each; weeks 2, 4, ..., 26: $500.00 each", 26)
    assert case["runs"] == [{"set": list(range(1, 26, 2))}, {"set": list(range(2, 27, 2))}]
    assert case["weeks"] == ["300.00", "500.00"] * 13
    ctx = E.context(case)
    assert [g for g, _ in ctx.runs] == ["g01", "g02"] and ctx.sets == {"g01", "g02"}
    fids = {f["id"] for f in E.facts(case)}
    assert not any(x.startswith(("gfirst_", "glast_")) for x in fids)
    # rules grow with the weeks, not with the square of the weeks: the same year as 26 single-week runs (the only form
    # the frozen record read) is about 3x the rules at 26 weeks; doubling the weeks of a two-set year adds < 30%
    sets26 = len(T.rules(ctx))
    runs26 = len(T.rules(E.context(synthetic(
        "T26R", "; ".join(f"week {i}: ${'300.00' if i % 2 else '500.00'}" for i in range(1, 27)), 26))))
    sets52 = len(T.rules(E.context(synthetic(
        "T52", "weeks 1, 3, 5, ..., 51: $612.40 each; weeks 2, 4, ..., 52: $455.10 each", 52))))
    assert runs26 > 2.5 * sets26 and sets52 < 1.3 * sets26, (sets26, runs26, sets52)


# --- s. 14(4) ranking exactness (forward evaluation of the ground rules; fast) ----------------------------------------

def _expected(case, n_weeks):
    """Brute force: items rank by earnings (higher first), then stated order; weeks inside an item by week order."""
    order = []
    for j, it in enumerate(case["runs"]):
        listed = it["set"] if isinstance(it, dict) else list(range(it[0], it[1] + 1))
        order += [(-Fraction(case["weeks"][w - 1]), j, w) for w in listed]
    order.sort()
    rank = {w: i for i, (_, _, w) in enumerate(order)}
    total = sum(-a for a, _, _ in order[:n_weeks])
    return rank, total


@pytest.mark.parametrize("weeks_text,n", [
    ("weeks 1, 3, 5, ..., 25: $300.00 each; weeks 2, 4, ..., 26: $500.00 each", 26),
    ("weeks 1 to 4: $400.00 each; weeks 5, 7, 9: $400.00 each; weeks 6, 8, 10: $250.00 each", 10),  # tie run/set
    ("weeks 2, 4, ..., 20: $410.10 each; week 1: $999.99; weeks 3, 5, ..., 21: $410.10 each; weeks 22 to 24: $0.00 each", 24),
    ("weeks 1, 2 and 9: $100.00 each; weeks 3 to 8: $700.00 each; weeks 10, 11, ..., 14: $700.00 each", 14),
])
@pytest.mark.parametrize("mutant", [None, "M6"])
def test_rank_is_exact_over_items(weeks_text, n, mutant):
    case = synthetic("TR", weeks_text, n)
    fw = RUN.Forward(T.rules(E.context(case), mutant), E.facts(case))
    nweeks = int(fw.vals["nweeks"])
    rank, _ = _expected(case, nweeks)
    ranks = {int(w[1:]): int(fw.vals[f"rank_{w}"]) for w in E.context(case).weeks}
    assert ranks == rank
    assert sorted(ranks.values()) == list(range(n))  # a permutation: no gap, no double count
    calc = {int(w[1:]) for w in E.context(case).weeks if fw.truths[T.key(T.U("calc", w))]}
    cut = nweeks + (1 if mutant == "M6" else 0)
    assert calc == {w for w, r in rank.items() if r < cut}
    assert fw.vals["calcsum"] == sum(Fraction(case["weeks"][w - 1]) for w in calc) * 100


# --- proved and replayed in Lean ------------------------------------------------------------------------------------

def run_with_lean(case):
    """(staged answers, Lean rows by id, doc id -> target, prove seconds, documents) for one synthetic case."""
    rec, lean_cases, _ = RUN._case_task(case)
    target = {lc["id"]: lc.pop("_target") for lc in lean_cases if "_target" in lc}
    docs = {lc["id"]: lc["document"] for lc in lean_cases if lc["kind"] == "document"}
    rows = {r["id"]: r for r in RUN.lean(lean_cases)}
    return rec, rows, target, docs


def _check_admitted(case, benefit):
    t0 = time.time()
    rec, rows, target, docs = run_with_lean(case)
    seconds = time.time() - t0
    qid = case["questions"][1]["qid"]
    assert rec["staged"][qid] == {"answer": "CAD", "cad": benefit}, rec["staged"]
    assert rec["staged"][case["questions"][0]["qid"]] == {"answer": "YES"}
    certs = [r for k, r in rows.items() if "/cert/" in k]
    assert certs and all(r.get("status") == "ok" and r.get("valid") is True for r in certs)
    rate_doc = [k for k, t in target.items() if t == "benefit"]
    assert len(rate_doc) == 1
    nodes = len(docs[rate_doc[0]]["graph"]["nodes"])
    assert nodes < NODE_LIMIT, nodes
    for k in target:
        assert rows[k].get("status") == "ok" and rows[k].get("assurance") == "lean-admitted", (k, rows[k])
    print(f"\n{case['id']}: rules {rec['rules']}, rate document {nodes} graph nodes, prove {rec['prove_seconds']} s, "
          f"prove + Lean {seconds:.1f} s")
    return seconds


@pytest.mark.heavy
def test_26_alternating_weeks_rate_document_admitted():
    # 13 weeks at $500 + 7 of 13 at $300 (s. 14(2) at 7.5%: 20 weeks; the cut falls inside the $300 set)
    # = $8,600.00 / 20 = $430.00; 55% = $236.50
    case = synthetic("T26", "weeks 1, 3, 5, ..., 25: $300.00 each; weeks 2, 4, ..., 26: $500.00 each", 26)
    _check_admitted(case, "236.50")


@pytest.mark.heavy
def test_52_alternating_weeks_rate_document_admitted():
    # 20 of the 26 weeks at $612.40 (the cut falls inside the higher set) = $12,248.00 / 20 = $612.40; 55% = $336.82.
    # Its run time (prove + Lean) is printed and reported, not asserted (CLAUDE.md: no elapsed-time assertions in tests;
    # MEASURED 240 s on the VM at load ~15, 2026-11-24, against the row's 10-minute bar).
    case = synthetic("T52", "weeks 1, 3, 5, ..., 51: $612.40 each; weeks 2, 4, ..., 52: $455.10 each", 52)
    _check_admitted(case, "336.82")
