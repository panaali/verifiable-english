"""Ambiguous text answered under each named reading (usecases/reading_runs.py, feature C).

A toy use case under tmp_path (the shape of the statute-corpus laws: a rule table with a MUTANTS hook, rules(), cases,
and a run.py main() that writes a run file) stands in for a law, so the tests are hermetic and need no Lean. Its rules
are real VE formulas over a small real VE environment, so the checked-English read-back guard runs in every end-to-end
test. Each test names the property it pins: both readings answered and named, the guards (words, hash, diff, edits,
read-back, differ-when) and the refusals (a dropped reading, one block per question, no guard switch in a table).
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

ENV = {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
       "spec_revision": "ve-v0.2-expand2-2026-09-25",
       "vocabulary": {"sorts": {"item": {"description": "An application."}},
                      "predicates": {p: {"arguments": ["item"], "description": d} for p, d in {
                          "late": "Is made late.", "always": "Is made.", "never": "Is never made.",
                          "unknown": "Is of an unknown kind.", "entitled": "Gives entitlement.",
                          "pays_ten": "Pays ten pounds.", "pays_twenty": "Pays twenty pounds.",
                          "refunded": "Is refunded."}.items()},
                      "constants": {"x": {"sort": "item", "description": "The application x.",
                                          "verbalisation": "application x"}}},
       "unit_schema": "ve-units@1", "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}}}


def U(p):
    return ["unary", p, ["const", "x"]]


def IMP(a, b):
    return ["implies", U(a), b]


TRANSLATION = '''
MUTANTS = {}
TABLE = {1: ("RULE", %r, "a late application defeats it"),
         2: ("RULE", %r, "entitled"),
         3: ("RULE", lambda ctx: [%r], "the amount (a builder row)"),
         4: ("RULE", %r, "never fires")}
def rules(ctx, mutant=None):
    t = dict(TABLE)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    out = []
    for n, e in sorted(t.items()):
        for i, f in enumerate(e[1](ctx) if callable(e[1]) else [e[1]]):
            out.append({"id": f"r{n}.{i}", "row": n, "formula": f})
    return out
''' % (IMP("late", ["not", U("entitled")]), IMP("always", U("entitled")), IMP("always", U("pays_ten")),
       IMP("unknown", U("refunded")))
CASES = '''
CASES = [{"id": "C1", "facts": ["late"], "questions": ["Q1", "Q2", "Q3", "Q4"]},
         {"id": "C2", "facts": [], "questions": ["Q1", "Q2", "Q3", "Q4"]},
         {"id": "C3", "case": "CC", "facts": [], "questions": ["Q1"]},
         {"id": "C4", "case": "CC", "facts": ["late"], "questions": ["Q4"]},
         {"id": "BOOM", "facts": ["boom"], "questions": ["Q1"]}]
'''
RUN = '''
import argparse, json
from pathlib import Path
import {tr} as T
import {ca} as K
ENV = {env}
OUT = {{"entitled": ("Q1", "YES", "NO"), "pays_ten": ("Q2", "GBP 10", None), "pays_twenty": ("Q2", "GBP 20", None),
        "refunded": ("Q3", "YES", None)}}

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
        if "boom" in c["facts"]:
            raise RuntimeError("boom")
        Environment(ENV)
        ans, facts = {{}}, set(c["facts"]) | {{"always"}}
        for r in T.rules(c):
            f = r["formula"]
            if f[1][1] in facts:
                neg = f[2][0] == "not"
                q, yes, no = OUT[(f[2][1] if neg else f[2])[1]]
                ans.setdefault(q, no if neg else yes)
        ans["Q4"] = "N/A" if ans.get("Q1") == "NO" else ans.get("Q2", "OPEN")
        recs.append({{"id": c["id"], "case": c.get("case", c["id"]),
                      "answers": {{q: ans.get(q, "OPEN") for q in c["questions"]}}}})
    Path(args.out).write_text(json.dumps({{"records": recs}}))
'''
SOURCE = "An application must be made on or before 31 March. An individual is entitled if the conditions are met."
NAME_A = "a late application means the individual is not entitled"
NAME_B = "a late application does not change entitlement"
NEVER_LATE = [{"op": "replace", "row": 1, "old": ["implies", ["unary", "late", "?x"], "?c"],
               "new": ["implies", ["unary", "never", "?x"], "?c"]}]


def toy_law(tmp_path, **cfg):
    """A fresh toy use case with module names of its own (pytest runs many in one process)."""
    tag = uuid.uuid4().hex[:8]
    names = {"translation": f"toy_tr_{tag}", "cases": f"toy_ca_{tag}", "run": f"toy_run_{tag}"}
    law = tmp_path / "usecases" / "toy"
    law.mkdir(parents=True)
    (law / f"{names['translation']}.py").write_text(TRANSLATION)
    (law / f"{names['cases']}.py").write_text(CASES)
    (law / f"{names['run']}.py").write_text(RUN.format(tr=names["translation"], ca=names["cases"], env=repr(ENV)))
    return law, {**names, "slot": 1, **cfg}


def row(reading, name, edits, expect, questions="C1/Q1,C2/Q1", block="B1", words="on or before 31 March",
        differ=None, dq="Q1"):
    differ = differ or {"id": "DW-1", "from": "C2", "patch": [["append", ["facts"], "late"]]}
    return "\t".join([block, "reg. 16B(2)", words, reading, name, "-", json.dumps(edits), questions,
                      json.dumps(differ), json.dumps({"q": dq, "answer": expect})])


def table(tmp_path, cfg, rows):
    p = tmp_path / f"t-{uuid.uuid4().hex[:6]}.tsv"
    p.write_text("\n".join([f"# law\t{json.dumps(cfg)}", "# writer: test", "\t".join(R.COLUMNS), *rows]) + "\n")
    return p


def good_rows(**kw):
    return [row("A", NAME_A, [], "NO", **kw), row("B", NAME_B, NEVER_LATE, "YES", **kw)]


def run(tmp_path, rows, **cfg):
    tmp_path.mkdir(parents=True, exist_ok=True)
    law_dir, cfg = toy_law(tmp_path, **cfg)
    src = tmp_path / "source.txt"
    src.write_text(SOURCE)
    out = tmp_path / "out.json"
    res = R.main(["--law-dir", str(law_dir), "--table", str(table(tmp_path, cfg, rows)), "--source", str(src),
                  "--out", str(out)])
    assert json.loads(out.read_text()) == json.loads(json.dumps(res))
    return res["blocks"]["B1"]


def test_each_reading_answers_under_its_name_beside_its_checked_rules(tmp_path):
    b = run(tmp_path, good_rows())
    assert b["guards"] == [] and b["readback"] is True
    q = b["questions"]["C1/Q1"]
    assert q["status"] == "per-reading" and q["answers"] == {"A": "NO", "B": "YES"}
    text = "\n".join(q["report"])
    assert text.startswith('The text allows two readings of reg. 16B(2): "on or before 31 March".')
    assert f'means "{NAME_A}" (If x is late, then it is not the case that x is entitled): NO.' in text
    assert f'means "{NAME_B}" (If x is classified as "never", then it is not the case that x is entitled): YES.' in text
    assert "Both readings" not in text and "VE gives none without naming the reading" in text


def test_agreeing_readings_say_both_readings_written(tmp_path):
    q = run(tmp_path, good_rows())["questions"]["C2/Q1"]
    assert q["status"] == "per-reading" and q["answers"] == {"A": "YES", "B": "YES"}
    assert q["report"][-1] == "YES. Both readings written for reg. 16B(2) give this answer."
    assert f'means "{NAME_A}"' in q["report"][1] and f'means "{NAME_B}"' in q["report"][2]


def test_readback_guard_refuses_a_rule_with_no_checked_wording(tmp_path):
    undeclared = [{"op": "replace", "row": 1, "old": ["implies", ["unary", "late", "?x"], "?c"],
                   "new": ["implies", ["unary", "late_by_post", "?x"], "?c"]}]
    b = run(tmp_path, [row("A", NAME_A, [], "NO"), row("B", NAME_B, undeclared, "YES")])
    for q in b["questions"].values():
        assert q["status"] == "writer-ambiguous" and q["answers"] == {}
        assert any(g.startswith("readback:") for g in q["guards"])


def test_a_table_cannot_switch_a_guard_off(tmp_path):
    law_dir, cfg = toy_law(tmp_path)
    with pytest.raises(R.TableError, match="no guard can be switched off"):
        R.load_table(table(tmp_path, {**cfg, "readback": False}, good_rows()))


def test_hash_guard_same_rules_under_both_readings(tmp_path):
    same = [{"op": "replace", "row": 1, "old": ["implies", ["unary", "late", "?x"], "?c"],
             "new": ["implies", ["unary", "late", "?x"], "?c"]}]
    b = run(tmp_path, [row("A", NAME_A, [], "NO"), row("B", NAME_B, same, "YES")])
    for q in b["questions"].values():
        assert q["status"] == "writer-ambiguous" and q["answers"] == {}
        assert any(g.startswith("hash:") for g in q["guards"])


def test_differ_when_results_must_differ(tmp_path):
    as_is = {"id": "DW-1", "from": "C2", "patch": []}
    b = run(tmp_path, [row("A", NAME_A, [], "NO", differ=as_is), row("B", NAME_B, NEVER_LATE, "YES", differ=as_is)])
    assert any("Lean-checked answers that differ" in g for g in b["guards"])
    assert all(q["status"] == "writer-ambiguous" for q in b["questions"].values())


def test_differ_when_catches_swapped_names(tmp_path):
    b = run(tmp_path, [row("A", NAME_A, [], "YES"), row("B", NAME_B, NEVER_LATE, "NO")])
    assert any(g.startswith("differ: reading A gives") for g in b["guards"])
    assert all(q["status"] == "writer-ambiguous" for q in b["questions"].values())


def test_undecided_reading_gives_no_single_answer(tmp_path):
    open_b = NEVER_LATE + [{"op": "set", "row": 2, "formula": IMP("unknown", U("entitled"))},
                           {"op": "replace", "row": 3, "old": U("pays_ten"), "new": U("pays_twenty")}]
    b = run(tmp_path, [row("A", NAME_A, [], "GBP 10", questions="C1/Q1", dq="Q2"),
                       row("B", NAME_B, open_b, "GBP 20", questions="C1/Q1", dq="Q2")])
    q = b["questions"]["C1/Q1"]
    assert q["status"] == "per-reading" and q["answers"] == {"A": "NO", "B": "OPEN"}
    assert q["report"][2].endswith(": VE could not decide this.") and "Both readings" not in "\n".join(q["report"])


def test_not_asked_needs_its_certified_condition(tmp_path):
    with_cond = run(tmp_path / "a", good_rows(questions="C1/Q4"), conditions={"Q4": ["Q1", "the person is entitled"]})
    q = with_cond["questions"]["C1/Q4"]
    assert q["status"] == "per-reading" and q["answers"] == {"A": "N/A", "B": "GBP 10"}
    assert q["report"][1].endswith(": not asked under this reading (the person is entitled is certified false).")
    bare = run(tmp_path / "b", good_rows(questions="C1/Q4"))["questions"]["C1/Q4"]
    assert bare["report"][1].endswith(": VE could not decide this.")


def test_words_must_be_verbatim_at_word_boundaries(tmp_path):
    b = run(tmp_path, good_rows(words="by 31 March"))
    assert b["guards"] == ["words: the quoted words are not in the source verbatim"]
    assert all(q["status"] == "writer-ambiguous" and q["answers"] == {} for q in b["questions"].values())
    assert R.words_in_source("on or before\n 31  March", SOURCE)
    assert not R.words_in_source("or before 31 Mar", SOURCE) and not R.words_in_source("n or before", SOURCE)


def test_a_dropped_reading_is_refused(tmp_path):
    """The real-text test's plant: one reading presented as the answer. A table cannot express it."""
    law_dir, cfg = toy_law(tmp_path)
    with pytest.raises(R.TableError, match="exactly two readings"):
        R.load_table(table(tmp_path, cfg, [row("A", NAME_A, [], "NO")]))
    with pytest.raises(R.TableError, match="exactly two readings"):
        R.load_table(table(tmp_path, cfg, good_rows() + [row("C", "a third", NEVER_LATE, "YES")]))
    with pytest.raises(R.TableError, match="own name"):
        R.load_table(table(tmp_path, cfg, [row("A", NAME_A, [], "NO"), row("B", " " + NAME_A.upper(), NEVER_LATE, "YES")]))
    with pytest.raises(R.TableError, match="different result"):
        R.load_table(table(tmp_path, cfg, [row("A", NAME_A, [], "NO"), row("B", NAME_B, NEVER_LATE, "NO")]))


def test_one_block_per_question(tmp_path):
    law_dir, cfg = toy_law(tmp_path)
    with pytest.raises(R.TableError, match="one block per question"):
        R.load_table(table(tmp_path, cfg, good_rows() + good_rows(block="B2")))


def test_builder_edit_that_never_takes_effect_fails_the_block(tmp_path):
    dead = NEVER_LATE + [{"op": "replace", "row": 3, "old": U("refunded"), "new": U("pays_twenty")}]
    b = run(tmp_path, [row("A", NAME_A, [], "NO"), row("B", NAME_B, dead, "YES")])
    assert any(g.startswith("edits: reading B edit 1") for g in b["guards"])
    assert all(q["status"] == "writer-ambiguous" for q in b["questions"].values())


def test_a_case_of_several_records_is_found_by_its_question(tmp_path):
    b = run(tmp_path, good_rows(questions="CC/Q4", differ={"id": "DW-1", "from": "CC", "patch": []}, dq="Q4"))
    assert "differ: reading A gives 'N/A', the table states 'NO'" in b["guards"]  # C4's Q4, not C3's
    assert "differ: reading B gives 'GBP 10', the table states 'YES'" in b["guards"]


def test_the_law_module_is_restored_when_its_run_fails(tmp_path):
    law_dir, cfg = toy_law(tmp_path)
    law = R.Law(law_dir, cfg)
    cases = list(law.K.CASES)
    with pytest.raises(RuntimeError, match="boom"):
        law.answers("BOOM", NEVER_LATE, extra_case={"id": "BOOM", "facts": ["boom"], "questions": ["Q1"]}, label="~t")
    assert "~t" not in law.T.MUTANTS and law.key is None and law.K.CASES == cases
    assert law.answers("C1", None)[0]["Q1"] == "NO"


def test_diff_guard_each_reading_against_the_translation():
    r = lambda i, row, f: {"id": f"r{i}.0", "row": row, "formula": [f]}  # noqa: E731
    block = {"A": {"edits": []}, "B": {"edits": [{"op": "replace", "row": 1}]}}
    base = [[r(1, 1, "a"), r(3, 3, "c")]]
    fails, own = R.compare(block, base, {"A": ({}, [[r(1, 1, "a"), r(3, 3, "c")]], None),
                                         "B": ({}, [[r(1, 1, "b"), r(3, 3, "CHANGED")]], None)})
    assert "diff: reading B differs from the translation outside its rows ['1']" in fails
    fails, _ = R.compare(block, base, {"A": ({}, [[r(1, 1, "z"), r(3, 3, "c")]], None),
                                       "B": ({}, [[r(1, 1, "b"), r(3, 3, "c")]], None)})
    assert fails[0] == "diff: reading A differs from the translation outside its rows []"
    fails, _ = R.compare(block, base, {"A": ({}, [[r(1, 1, "a"), r(3, 3, "c")]], None),
                                       "B": ({}, [[r(3, 3, "c"), r(1, 1, "a")]], None)})
    assert "hash: both readings consumed the same rules" in fails and "diff: reading B has no rules of its own" in fails
    fails, _ = R.compare(block, [[{"id": "s1", "formula": ["a"]}]], {"A": ({}, [[{"id": "s1", "formula": ["a"]}]], None),
                                                                    "B": ({}, [[{"id": "s1", "formula": ["b"]}]], None)})
    assert "diff: a consumed rule names no row" in fails


def test_row_of_and_decided():
    assert R.row_of({"row": 4}) == "4" and R.row_of({"unit": "u7"}) == "u7" and R.row_of({"id": "c2+.3"}) == "c2+"
    assert R.row_of({"id": "s1"}) is None and R.row_of({"id": "a.b"}) is None
    assert R.decided("YES") and R.decided(["Zack"]) and R.decided([]) and R.decided({"answer": "AMOUNT", "gbp": "1.00"})
    assert not R.decided("OPEN") and not R.decided("open") and not R.decided(None) and not R.decided("N/A")
    assert not R.decided({"answer": "YES", "lean_rejected": True}) and not R.decided({"answer": "INCONSISTENT"})


def test_edit_ops():
    t = {1: ("RULE", ["if", "late", "Q1", "NO"], ""), 2: ("RULE", ["a"], "")}
    with pytest.raises(R.TableError, match="matches nothing"):
        R.transform([{"op": "replace", "row": 1, "old": ["if", "early", "?q", "?v"], "new": ["x"]}], 1)(t)
    hits = [0, 0, 0, 0]
    t2 = R.transform([{"op": "replace", "row": 1, "old": ["if", "late", "?q", "?v"], "new": ["if", "never", "?q", "?v"]},
                      {"op": "and", "row": 2, "formula": ["b"]}, {"op": "copy", "row": "3", "from": 2},
                      {"op": "drop", "row": 2}], 1, hits)(t)
    assert t2 == {1: ("RULE", ["if", "never", "Q1", "NO"], ""), 3: ("RULE", ["and", ["a"], ["b"]], "")} and hits == [1] * 4
    with pytest.raises(R.TableError, match="already exists"):
        R.transform([{"op": "copy", "row": 2, "from": 1}], 1)(t)
    lst = [("p", "c", ["a"]), ("q", "c", ["b"])]
    assert R.transform([{"op": "copy", "row": "r", "from": "p"}], 2)(lst)[2] == ("r", "c", ["a"])
    with pytest.raises(R.TableError, match="two entries of one key"):
        R.transform([], 2)(lst + [("p", "c", ["z"])])
    hits = [0]
    build = R.transform([{"op": "replace", "row": 1, "old": ["x", "?a"], "new": ["y", "?a"]}], 1, hits)(
        {1: ("RULE", lambda ctx: [["x", ctx], ["z"]], "")})[1][1]
    assert hits == [0] and build("k") == [["y", "k"], ["z"]] and hits == [1]


def test_one_run_per_case_and_reading_in_a_block(tmp_path):
    """A block's questions on one case, and an unpatched differ case, share one run per reading (a law's Lean replay
    can take minutes per run)."""
    law_dir, cfg = toy_law(tmp_path)
    cfg2, blocks = R.load_table(table(tmp_path, cfg, good_rows(questions="C1/Q1,C1/Q2,C1/Q3",
                                                                differ={"id": "DW-1", "from": "C1", "patch": []})))
    law, calls = R.Law(law_dir, cfg2), []
    main = law.run.main
    law.run.main = lambda argv: (calls.append(argv), main(argv))[1]
    out = R.run_block(law, "B1", blocks["B1"], SOURCE)
    assert [q["status"] for q in out["questions"].values()] == ["per-reading"] * 3
    assert len(calls) == 3 and sum("--no-lean" in c for c in calls) == 1
