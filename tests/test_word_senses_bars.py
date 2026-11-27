"""Word senses, version 1: the measured bars stay checked (bars and scoring frozen before the build:
docs/word-senses-v1/SCORING.md, pinned below by its sha256).

The fixtures in tests/data/word_senses_v1/ were recorded at the build: the 94 measured texts (seeded sets 1 and 2, the
ten word-on-two-kinds texts, the 20 friction texts, and today's tiers B, B-fix and C), the reader's two recorded runs
on each (its prompt kept as a sha256), VE's answers in both modes (with the reader; the word list alone), and the keys.
No test here calls a model or a reader program.

- test_the_recorded_answers_meet_the_bars scores the recorded answers with SCORING.md's rule, as written, and asserts
  the bars.
- test_the_branch_reads_each_text_as_recorded reads every text again with the recorded reader runs and asserts the same
  answers, so the bars hold for the code as it is, not only for the answers once recorded.

Five per-use branch keys (texts l03, l07, t13, t04, c02) were made after the results were seen, by two fresh keyers
that saw only the text, the question and the branch: they are NOT blind (keys.json "branch_not_blind"). The bars are
met only with them: test_with_the_blind_keys_alone_exactly_the_recorded_clause_cases_fail shows which answers need them.
If an answer changes on purpose, re-record the fixtures and re-score; never edit a key to make a test pass."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from ve import word_senses as ws

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data" / "word_senses_v1"
PROMPT_SHA256 = "e80bd349b03e2ceed840a3e3af15cc1d071022b5db8df05ddc7ab7da62b945ec"  # the reader prompt the runs were recorded with
SCORING_SHA256 = "4a9617c7af29bacc248dddd5700eedd298b6b626b138fdf22ecb6e7059bda5af"  # SCORING.md as hashed before the build
TEXTS, READER, ANSWERS, KEYS = (json.loads((DATA / f"{n}.json").read_text()) for n in
                                ("texts", "reader", "answers", "keys"))
NORM = {"Yes": "yes", "No": "no", "not determined": "not decided"}
SAFE = ("not determined", "cannot check")   # SCORING.md: "not determined" or "VE cannot check that reading yet"
WRONG = ("WRONG", "BRANCH-WRONG")
NO_ONE_KEY = ("layer1", "B", "Bfix", "C")   # SCORING.md: these have no ONE key; key A stands for it
BARRED = ("set1", "set2", "layer1", "B", "Bfix", "C")


def score_question(a: dict, key: str | None, branch: list | None, tier: str) -> str:
    """One question under SCORING.md (a branch with a Yes/No and no agreed key counts as branch wrong)."""
    bw = a.get("both_ways")
    if not bw:
        ans = a["answer"]
        if ans in ("Yes", "No"):
            return "UNKEYED" if key is None else ("RIGHT" if NORM[ans] == key else "WRONG")
        return "RIGHT" if ans == "not determined" and key == "not decided" else "MISS"
    one = branch[0] if branch else (key if tier in NO_ONE_KEY else None)
    ok = one is not None and NORM.get(bw.get("same"), bw.get("same")) == one
    for u in bw.get("uses", []):
        if u["answer"] not in SAFE:
            k = branch[1].get(str(u["sentence"])) if branch else None
            ok = ok and k is not None and NORM.get(u["answer"], u["answer"]) == k
    if "different" in bw and bw["different"] not in SAFE:
        ok = False
    if "meanings" in bw:   # no measured text gives two meanings; an unkeyed branch is wrong
        ok = False
    return "BRANCH-SAFE" if ok else "BRANCH-WRONG"


def scored(mode: str, not_blind: bool = True) -> dict:
    """{text id: [(question, verdict, raised words)]} for one mode; a text not read has no rows."""
    branch = {**KEYS["branch"], **(KEYS["branch_not_blind"] if not_blind else {})}
    out = {}
    for name, r in ANSWERS[mode].items():
        tier = name.split("-", 1)[0]
        out[name] = [(a["question"], score_question(a, KEYS["a"].get(f"{name}|{a['question']}"),
                                                    branch.get(f"{name}|{a['question']}"), tier),
                      (a.get("both_ways") or {}).get("words", [])) for a in r["answers"]]
    return out


def wrong_texts(rows: dict, prefix: str, ids=None) -> tuple[list, list]:
    names = sorted(n for n in rows if n.startswith(prefix + "-") and (ids is None or n in ids))
    return names, [n for n in names if any(v in WRONG for _, v, _ in rows[n])]


def upper95(wrong: int, n: int) -> float:
    """One-sided 95% exact (Clopper-Pearson) upper bound on the wrong rate."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        p = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(wrong + 1))
        lo, hi = (p, hi) if cdf > 0.05 else (lo, p)
    return hi


def test_the_fixtures_are_the_measured_set():
    counts = {}
    for name in TEXTS:
        counts[name.split("-", 1)[0]] = counts.get(name.split("-", 1)[0], 0) + 1
    assert counts == {"set1": 10, "set2": 20, "layer1": 10, "c2": 20, "B": 14, "Bfix": 5, "C": 15}
    assert set(TEXTS) == set(READER) == set(ANSWERS["reader"]) == set(ANSWERS["list"])
    assert {k.split("|")[0] for k in KEYS["a"]} <= set(TEXTS) and len(KEYS["branch_not_blind"]) == 5
    assert KEYS["no_giveaway"] == [f"set2-g{i:02d}" for i in range(1, 11)]
    # The reader runs were recorded with this prompt; a new prompt needs new recordings (and a new measurement).
    assert hashlib.sha256((ROOT / "ve" / "word_senses_prompt.txt").read_bytes()).hexdigest() == PROMPT_SHA256
    assert hashlib.sha256((ROOT / "docs" / "word-senses-v1" / "SCORING.md").read_bytes()).hexdigest() == SCORING_SHA256
    assert round(upper95(0, 10), 3) == 0.259 and round(upper95(0, 20), 3) == 0.139 and round(upper95(1, 20), 3) == 0.216


def test_every_barred_question_has_its_key():
    for mode in ("reader", "list"):
        unkeyed = [(n, q) for n, qs in scored(mode).items() if n.split("-", 1)[0] in BARRED
                   for q, v, _ in qs if v == "UNKEYED"]
        assert unkeyed == [], (mode, unkeyed)


def test_the_recorded_answers_meet_the_bars():
    reader, listed = scored("reader"), scored("list")
    # (a) with the reader: set 1 at most 1 of 10 texts wrong; set 2 at most 2 of 20, at most 1 of the 10 no-giveaway.
    # Recorded: set 1 0 of 10; set 2 1 of 20 (g15: a per-use branch "no answer" where the key is "not decided").
    assert len(wrong_texts(reader, "set1")[1]) <= 1
    assert wrong_texts(reader, "set2")[1] == ["set2-g15"]
    assert len(wrong_texts(reader, "set2", set(KEYS["no_giveaway"]))[1]) <= 1
    # (b) friction with the reader: fewer than 4 needless both-ways answers in the 20 texts.
    needless = [(n, q) for n, qs in reader.items() if n.startswith("c2-") for q, v, words in qs
                if v.startswith("BRANCH") and (not words or all(KEYS["c2"].get(f"{n}|{w}") == "same" for w in words))]
    assert len(needless) < 4, needless
    # (c) layer 1: all 10 read and 0 wrong (both modes); (d) tiers B, B-fix and C: 0 wrong, both modes.
    for rows, mode in ((reader, "reader"), (listed, "list")):
        names, bad = wrong_texts(rows, "layer1")
        assert len(names) == 10 and all(ANSWERS[mode][n]["status"] == "read" for n in names)
        assert bad == [], (mode, bad)
        for tier in ("B", "Bfix", "C"):
            assert wrong_texts(rows, tier)[1] == [], (mode, tier)


def test_with_the_blind_keys_alone_exactly_the_recorded_clause_cases_fail():
    """The five NOT-blind keys decide bars (c) and (d): without them these texts count wrong."""
    def bad(mode):
        rows = scored(mode, not_blind=False)
        return sorted(n for t in ("layer1", "B", "Bfix", "C") for n in wrong_texts(rows, t)[1])
    assert bad("reader") == ["layer1-l03"]
    assert bad("list") == ["B-t13", "Bfix-t04", "C-c02", "layer1-l03", "layer1-l07"]


def test_a_wrong_answer_would_break_a_bar():
    """The scorer is not vacuous: a flipped answer, an unkeyed branch and a "no answer" branch are wrong."""
    assert score_question({"question": "q", "answer": "Yes"}, "no", None, "layer1") == "WRONG"
    b = {"question": "q", "answer": "depends on meaning", "both_ways": {"same": "No", "uses": [{"sentence": 9, "answer": "No"}]}}
    assert score_question(b, "no", None, "layer1") == "BRANCH-WRONG"
    assert score_question(b, "no", ["no", {"9": "no"}], "layer1") == "BRANCH-SAFE"
    assert score_question(b, "no", ["no", {"9": "yes"}], "layer1") == "BRANCH-WRONG"
    c = {"question": "q", "answer": "depends on meaning",
         "both_ways": {"same": "Yes", "uses": [{"sentence": 3, "answer": "no answer"}]}}
    assert score_question(c, "yes", ["yes", {"3": "not decided"}], "set2") == "BRANCH-WRONG"
    assert score_question(c, "yes", None, "set2") == "BRANCH-WRONG"   # sets 1 and 2 need their ONE key


def compact(result: dict) -> dict:
    return {"status": result["status"], "answers": [{k: a[k] for k in ("question", "answer", "both_ways") if k in a}
                                                    for a in result.get("answers", [])]}


@pytest.mark.parametrize("name", sorted(TEXTS))
def test_the_branch_reads_each_text_as_recorded(name, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rec, calls = READER[name], []

    def reader(prompt: str) -> str:
        assert hashlib.sha256(prompt.encode()).hexdigest() == rec["input_sha256"], "the reader's input changed"
        calls.append(prompt)
        assert len(calls) <= len(rec["outputs"]), "more reader runs than recorded"
        return rec["outputs"][len(calls) - 1]

    n = name.split("-", 1)[1]
    got = ws.read(f"{n}.txt", TEXTS[name], reader=reader, scratch=tmp_path)
    assert compact(got) == ANSWERS["reader"][name]
    assert len(calls) == len(rec["outputs"])
    assert compact(ws.read(f"{n}.txt", TEXTS[name], reader=None, scratch=tmp_path)) == ANSWERS["list"][name]
