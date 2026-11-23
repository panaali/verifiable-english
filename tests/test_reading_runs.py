"""Ambiguous text answered under each named reading (usecases/reading_runs.py, feature C).

A toy use case under tmp_path (the shape of the statute-corpus laws: a rule table with a MUTANTS hook, rules(), cases,
and a run.py main() that writes a run file) stands in for a law, so the tests are hermetic and need no Lean. The
read-back test uses a small real VE environment. Each test names the property it pins: both readings answered and named,
the guards (hash, diff, differ-when, read-back, verbatim words) and the refusals (a dropped reading, one block per question).
"""
import importlib.util
import json
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("reading_runs", REPO / "usecases" / "reading_runs.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)

TRANSLATION = '''
MUTANTS = {}
TABLE = {1: ("RULE", ["if", "late", "Q1", "NO"], "a late application defeats it"),
         2: ("RULE", ["if", "always", "Q1", "YES"], "entitled"),
         3: ("RULE", ["if", "always", "Q2", "GBP 10"], "amount"),
         4: ("RULE", ["if", "unknown", "Q3", "YES"], "never fires")}
def rules(ctx, mutant=None):
    t = dict(TABLE)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return [{"id": f"r{n}", "row": n, "formula": e[1]} for n, e in sorted(t.items())]
'''
CASES = '''
CASES = [{"id": "C1", "facts": ["late"], "questions": ["Q1", "Q2", "Q3"]},
         {"id": "C2", "facts": [], "questions": ["Q1", "Q2", "Q3"]}]
'''
RUN = '''
import argparse, json
from pathlib import Path
import {tr} as T
import {ca} as K

class Environment:
    def __init__(self, raw):
        self.raw = raw

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases"); ap.add_argument("--out"); ap.add_argument("--no-lean", action="store_true")
    args = ap.parse_args(argv)
    recs = []
    for c in K.CASES:
        if args.cases and c["id"] not in args.cases.split(","):
            continue
        Environment({{"case": c["id"]}})
        ans = {{}}
        for r in T.rules(c):
            _, cond, q, v = r["formula"]
            if cond == "always" or cond in c["facts"]:
                ans.setdefault(q, v)
        recs.append({{"id": c["id"], "answers": {{q: ans.get(q, "OPEN") for q in c["questions"]}}}})
    Path(args.out).write_text(json.dumps({{"records": recs}}))
'''
SOURCE = "An application must be made on or before 31 March. An individual is entitled if the conditions are met."
NAME_A = "a late application means the individual is not entitled"
NAME_B = "a late application does not change entitlement"
DROP_ROW_1 = [{"op": "replace", "row": 1, "old": ["if", "late", "?q", "?v"], "new": ["if", "never", "?q", "?v"]}]


def toy_law(tmp_path):
    """A fresh toy use case with module names of its own (pytest runs many in one process)."""
    tag = uuid.uuid4().hex[:8]
    names = {"translation": f"toy_tr_{tag}", "cases": f"toy_ca_{tag}", "run": f"toy_run_{tag}"}
    law = tmp_path / "usecases" / "toy"
    law.mkdir(parents=True)
    (law / f"{names['translation']}.py").write_text(TRANSLATION)
    (law / f"{names['cases']}.py").write_text(CASES)
    (law / f"{names['run']}.py").write_text(RUN.format(tr=names["translation"], ca=names["cases"]))
    return law, {**names, "slot": 1, "readback": False}


def row(reading, name, edits, expect, questions="C1/Q1,C2/Q1", block="B1", words="on or before 31 March",
        differ=None, dq="Q1"):
    differ = differ or {"id": "DW-1", "from": "C2", "patch": [["append", ["facts"], "late"]]}
    return "\t".join([block, "reg. 16B(2)", words, reading, name, "-", json.dumps(edits), questions,
                      json.dumps(differ), json.dumps({"q": dq, "answer": expect})])


def table(tmp_path, cfg, rows):
    p = tmp_path / f"t-{uuid.uuid4().hex[:6]}.tsv"
    p.write_text("\n".join([f"# law\t{json.dumps(cfg)}", "# writer: test", "\t".join(R.COLUMNS), *rows]) + "\n")
    return p


def good_rows():
    return [row("A", NAME_A, [], "NO"), row("B", NAME_B, DROP_ROW_1, "YES")]


def run(tmp_path, rows):
    law_dir, cfg = toy_law(tmp_path)
    src = tmp_path / "source.txt"
    src.write_text(SOURCE)
    out = tmp_path / "out.json"
    return R.main(["--law-dir", str(law_dir), "--table", str(table(tmp_path, cfg, rows)), "--source", str(src),
                   "--out", str(out)])["blocks"]["B1"]


def test_each_reading_answers_under_its_name(tmp_path):
    q = run(tmp_path, good_rows())["questions"]["C1/Q1"]
    assert q["status"] == "per-reading" and q["answers"] == {"A": "NO", "B": "YES"}
    text = "\n".join(q["report"])
    assert text.startswith('The text allows two readings of reg. 16B(2): "on or before 31 March".')
    assert f'means "{NAME_A}"' in text and f'means "{NAME_B}"' in text
    assert ": NO." in text and ": YES." in text and "Both readings" not in text
    assert "VE gives none without naming the reading" in text


def test_agreeing_readings_say_both_readings_written(tmp_path):
    q = run(tmp_path, good_rows())["questions"]["C2/Q1"]
    assert q["status"] == "per-reading" and q["answers"] == {"A": "YES", "B": "YES"}
    assert q["report"][-1] == "YES. Both readings written for reg. 16B(2) give this answer."
    assert f'means "{NAME_A}"' in q["report"][1] and f'means "{NAME_B}"' in q["report"][2]


def test_hash_guard_same_rules_under_both_readings(tmp_path):
    same = [{"op": "replace", "row": 1, "old": ["if", "late", "?q", "?v"], "new": ["if", "late", "?q", "?v"]}]
    b = run(tmp_path, [row("A", NAME_A, [], "NO"), row("B", NAME_B, same, "YES")])
    for q in b["questions"].values():
        assert q["status"] == "writer-ambiguous" and q["answers"] == {}
        assert any(g.startswith("hash:") for g in q["guards"])


def test_differ_when_results_must_differ(tmp_path):
    no_late = {"id": "DW-1", "from": "C2", "patch": []}
    b = run(tmp_path, [row("A", NAME_A, [], "NO", differ=no_late), row("B", NAME_B, DROP_ROW_1, "YES", differ=no_late)])
    assert any("Lean-checked answers that differ" in g for g in b["guards"])
    assert all(q["status"] == "writer-ambiguous" for q in b["questions"].values())


def test_differ_when_catches_swapped_names(tmp_path):
    b = run(tmp_path, [row("A", NAME_A, [], "YES"), row("B", NAME_B, DROP_ROW_1, "NO")])
    assert any(g.startswith("differ: reading A gives") for g in b["guards"])
    assert all(q["status"] == "writer-ambiguous" for q in b["questions"].values())


def test_undecided_reading_gives_no_single_answer(tmp_path):
    open_b = [{"op": "set", "row": 2, "formula": ["if", "unknown", "Q1", "YES"]},
              {"op": "replace", "row": 1, "old": ["if", "late", "?q", "?v"], "new": ["if", "never", "?q", "?v"]},
              {"op": "set", "row": 3, "formula": ["if", "always", "Q2", "GBP 20"]}]
    b = run(tmp_path, [row("A", NAME_A, [], "GBP 10", questions="C1/Q1", dq="Q2"),
                       row("B", NAME_B, open_b, "GBP 20", questions="C1/Q1", dq="Q2")])
    q = b["questions"]["C1/Q1"]
    assert q["status"] == "per-reading" and q["answers"] == {"A": "NO", "B": "OPEN"}
    assert q["report"][2].endswith(": VE could not decide this.") and "Both readings" not in "\n".join(q["report"])


def test_words_must_be_verbatim(tmp_path):
    b = run(tmp_path, [row("A", NAME_A, [], "NO", words="by 31 March"), row("B", NAME_B, DROP_ROW_1, "YES",
                                                                         words="by 31 March")])
    assert b["guards"] == ["words: the quoted words are not in the source verbatim"]
    assert all(q["status"] == "writer-ambiguous" and "report" not in q for q in b["questions"].values())
    assert R.words_in_source("on or before\n 31  March", SOURCE)


def test_a_dropped_reading_is_refused(tmp_path):
    """The real-text test's plant: one reading presented as the answer. A table cannot express it."""
    law_dir, cfg = toy_law(tmp_path)
    with pytest.raises(R.TableError, match="exactly two readings"):
        R.load_table(table(tmp_path, cfg, [row("A", NAME_A, [], "NO")]))
    with pytest.raises(R.TableError, match="exactly two readings"):
        R.load_table(table(tmp_path, cfg, good_rows() + [row("C", "a third", DROP_ROW_1, "YES")]))
    with pytest.raises(R.TableError, match="own name"):
        R.load_table(table(tmp_path, cfg, [row("A", NAME_A, [], "NO"), row("B", NAME_A, DROP_ROW_1, "YES")]))
    with pytest.raises(R.TableError, match="different result"):
        R.load_table(table(tmp_path, cfg, [row("A", NAME_A, [], "NO"), row("B", NAME_B, DROP_ROW_1, "NO")]))


def test_one_block_per_question(tmp_path):
    law_dir, cfg = toy_law(tmp_path)
    rows = good_rows() + [row("A", NAME_A, [], "NO", block="B2"), row("B", NAME_B, DROP_ROW_1, "YES", block="B2")]
    with pytest.raises(R.TableError, match="one block per question"):
        R.load_table(table(tmp_path, cfg, rows))


def test_diff_guard_rules_outside_declared_rows():
    block = {"A": {"edits": []}, "B": {"edits": [{"op": "replace", "row": 1}]}}
    base = [[{"id": "r1", "row": 1, "formula": ["a"]}, {"id": "r3", "row": 3, "formula": ["c"]}]]
    a = [[{"id": "r1", "row": 1, "formula": ["a"]}, {"id": "r3", "row": 3, "formula": ["c"]}]]
    b = [[{"id": "r1", "row": 1, "formula": ["b"]}, {"id": "r3", "row": 3, "formula": ["CHANGED"]}]]
    fails, own = R.compare(block, base, {"A": ({}, a, None), "B": ({}, b, None)}, check_readback=False)
    assert fails == ["diff: reading B changes rules outside rows ['1']"]
    assert own["A"] == ['["a"]', '["c"]'] and own["B"] == ['["b"]', '["CHANGED"]']


def test_edit_that_matches_nothing_is_refused():
    t = {1: ("RULE", ["if", "late", "Q1", "NO"], "")}
    with pytest.raises(R.TableError, match="matches nothing"):
        R.transform([{"op": "replace", "row": 1, "old": ["if", "early", "?q", "?v"], "new": ["x"]}], 1)(t)
    assert R.transform(DROP_ROW_1, 1)(t)[1][1] == ["if", "never", "Q1", "NO"]


ENV = {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
       "spec_revision": "ve-v0.2-expand2-2026-09-25",
       "vocabulary": {"sorts": {"item": {"description": "An application."}},
                      "predicates": {"late": {"arguments": ["item"], "description": "Is made late."},
                                     "entitled": {"arguments": ["item"], "description": "Gives entitlement."}},
                      "constants": {"x": {"sort": "item", "description": "The application x.",
                                          "verbalisation": "application x"}}},
       "unit_schema": "ve-units@1", "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}}}


def test_readback_is_checked_english():
    rule = {"formula": ["implies", ["unary", "late", ["const", "x"]], ["not", ["unary", "entitled", ["const", "x"]]]]}
    s = R.readback(ENV, rule)
    assert s == "If x is late, then it is not the case that x is entitled."
    assert R.readback(ENV, {"formula": ["unary", "no_such_predicate", ["const", "x"]]}) is None
