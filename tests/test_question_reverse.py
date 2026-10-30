"""The reverse question corpus of Q1.3 (`conformance/question_reverse.py`, docs/spec/question-answering-PLAN.md Q1.3)
on a small fixed slice: the builder of each form, the mutants, the moved-word sentences, the measures' arithmetic,
and the group document's questions read by Lean, with the candidate limit on both sides."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from conformance import english_lean_e2_evidence as E
from conformance import question_reverse as R
from ve.english import EnglishVocabulary
from ve.environment import Environment

pytestmark = pytest.mark.filterwarnings("ignore::ve.english.UnreviewedVocabularyWarning")

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "docs/question-answering/q1-3"


def test_f1_frames_the_sentence():
    assert R.f1("Every member is registered.") == "Is it the case that every member is registered?"
    assert R.f1("For every member, the member is registered.") == \
        "Is it the case that for every member, the member is registered?"
    assert R.f1("Ann is verified.") == "Is it the case that Ann is verified?"


@pytest.mark.parametrize("sentence, question, put_back", [
    ("Every member is registered.", "Is every member registered?", "every member is registered."),
    ("Every member of the group is a person.", "Is every member of the group a person?",
     "every member of the group is a person."),
    ("Some member is registered and Ann is verified.", "Is some member registered and Ann is verified?",
     "some member is registered and Ann is verified."),
    ("Every person must be given equal access.", "Must every person be given equal access?",
     "every person must be given equal access."),
    ('"a27" may be performed.', 'May "a27" be performed?', '"a27" may be performed.'),
    ("Ann is verified.", "Is Ann verified?", "Ann is verified."),
])
def test_f2_fronts_the_word_after_the_subject(sentence, question, put_back):
    assert R.f2(sentence) == (question, put_back)
    assert put_back in R.candidates(question)


@pytest.mark.parametrize("sentence", [
    "Every member who is registered is eligible.",   # a clause in the subject: Lean's decision
    "Every member that is registered is eligible.",
    "Every member, is registered.",                   # a comma in the subject
    "It is not the case that Ann is verified.",       # an opener, not a name
    "This is impossible.",
    "Ann Bo is verified.",                            # a name of two words
    "ann is verified.",                               # not a name's spelling at the start
    "Is Ann verified.",                               # the word is first: no subject
    "Every member registers.",                        # no is, must or may
    "Every\nmember is registered.",                   # a subject across lines
])
def test_f2_is_not_built_for_other_subjects(sentence):
    assert R.f2(sentence) is None


def test_candidates_are_the_word_gaps_left_to_right():
    assert R.candidates("Is every member registered?") == ["every is member registered.",
                                                           "every member is registered."]
    assert R.candidates("Is Ann verified, then Bo?") == ["Ann is verified, then Bo.", "Ann verified, is then Bo.",
                                                         "Ann verified, then is Bo."]
    assert R.candidates("Must Ann?") == []


def test_every_mutant_differs_and_has_its_kind():
    f1 = R.mutants("Is it the case that every member is registered?", "f1")
    assert [kind for kind, _ in f1] == list(R.MUTANTS)
    assert dict(f1) == {
        "double-space": "Is  it  the  case  that  every  member  is  registered?",
        "space-before-mark": "Is it the case that every member is registered ?",
        "leading-space": " Is it the case that every member is registered?",
        "lower-initial": "is it the case that every member is registered?",
        "upper-auxiliary": "IS it the case that every member is registered?",
        "capital-body": "Is it the case that Every member is registered?"}
    f2 = dict(R.mutants("Must every person be given?", "f2"))
    assert f2["upper-auxiliary"] == "MUST every person be given?" and f2["capital-body"] == "Must Every person be given?"
    # A name already capitalised has no capital-body mutant, and no mutant is the question itself.
    named = R.mutants("Is Ann verified?", "f2")
    assert [kind for kind, _ in named] == list(R.MUTANTS[:-1])
    assert all(text != "Is Ann verified?" for _, text in named)


def test_the_long_question_has_the_asked_word_count():
    question = R.long_question(["Every member who is registered is eligible.", "Ann is verified."], 65)
    assert question.startswith("Is member who is ") and len(question[3:-1].split(" ")) == 65
    assert R.long_question(["Ann Bo."], 65) is None


def test_p95_and_share():
    assert R.p95(list(range(1, 101))) == 95 and R.p95(list(range(1, 21))) == 19 and R.p95([7.0]) == 7.0
    assert R.p95([]) is None and R.share(0, 0) is None and R.share(2, 3) == 0.666667


def _question(kind, same, status="one", ms=1.0, **outcome):
    return {"config": "c", "kind": kind, "question": f"{kind}?", "expected": "s.", "same": same, "ms": ms,
            "outcome": {"status": status, **outcome}}


def test_each_share_has_its_forms_denominator():
    questions = [_question("f1", True), _question("f1", True), _question("f1", False, "none", code="NoDerivation"),
                 _question("f2", True, sentence="s."), _question("f2", True, sentence="t."),
                 _question("f2", False, "many", code="AmbiguousQuestion", rephrasings=["Is it the case that s?"]),
                 _question("f2", False, "moved", code="QuestionWordMoved"),
                 _question("double-space:f1", False, "rejected", code="BadSpacing"),
                 _question("capital-body:f1", True)]
    moved = [{"config": "c", "question": "Is a b?", "moved": "a b is.", "status": "one", "same": False},
             {"config": "c", "question": "Is a b?", "moved": "a is b.", "status": "none", "same": False}]
    m = R.measures(questions, moved, [])
    assert (m["f1"]["questions"], m["f1"]["same"], m["f1"]["share"]) == (3, 2, 0.666667)
    assert [x["code"] for x in m["f1"]["misses"]] == ["NoDerivation"]
    assert (m["f2"]["questions"], m["f2"]["same"], m["f2"]["many"], m["f2"]["share"]) == (4, 2, 1, 0.75)
    assert m["f2"]["many_causes"][0]["rephrasings"] == ["Is it the case that s?"]
    assert [x["sentence"] for x in m["f2"]["other_sentence"]] == ["t."]
    assert [x["code"] for x in m["f2"]["misses"]] == ["QuestionWordMoved"]
    assert (m["odd"]["moved_sentences"], m["odd"]["f2_questions"], m["odd"]["accepted"]) == (2, 1, 1)
    assert m["mutants"] == {"capital-body:f1": {"one": 1, "questions": 1, "same": 1},
                            "double-space:f1": {"questions": 1, "rejected:BadSpacing": 1, "same": 0}}


@pytest.mark.parametrize("ms, met", [(100.0, True), (100.001, False)])
def test_the_latency_budget_is_met_at_its_bound_only(ms, met):
    limits = [{"candidates": 64, "ms": ms * 10}, {"candidates": 65, "ms": 99999.0}]
    gates = R.measures([_question("f1", True, ms=1.0)] * 19 + [_question("f1", True, ms=ms)] * 2, [], limits)[
        "latency"]
    assert (gates["p95_ms"], gates["met"], gates["q64_met"], gates["q64_runs"]) == (ms, met, met, 1)
    assert gates["max_ms"] == ms and gates["q64_max_ms"] == ms * 10


def test_no_question_meets_no_budget():
    gates = R.measures([], [], [])["latency"]
    assert gates["met"] is False and gates["q64_met"] is False and gates["p95_ms"] is None


@pytest.fixture(scope="module")
def group():
    path, data, texts = next(d for d in R.documents() if d[0] == "usecases/question-answering/group.ve.md")
    env = Environment(data)
    return path, env, EnglishVocabulary(env), texts


def test_the_group_documents_questions_read_through_lean(group):
    path, env, words, texts = group
    assert texts == ["Every member is registered.", "Every member who is registered is eligible.", "Ann is verified."]
    result = R.run_config(path, env, words, {}, texts)
    assert result["one_formula"] == 3
    by = {(q["kind"], q["sentence"]): q for q in result["questions"]}
    assert all(by[("f1", s)]["same"] for s in texts)
    assert [s for s in texts if ("f2", s) in by] == ["Every member is registered.", "Ann is verified."]
    assert all(by[("f2", s)]["same"] for s in ("Every member is registered.", "Ann is verified."))
    assert by[("double-space:f1", texts[0])]["outcome"]["code"] == "BadSpacing"
    assert by[("capital-body:f1", texts[0])]["same"] and not by[("lower-initial:f2", texts[2])]["same"]
    assert [(m["moved"], m["status"]) for m in result["moved"]] == [("every is member registered.", "none")]
    m = R.measures(result["questions"], result["moved"], [])
    assert m["f1"]["share"] == 1.0 and m["f2"]["share"] == 1.0 and m["odd"]["accepted"] == 0
    json.dumps(m)


def test_a_reading_counts_only_with_the_sentences_formula(group):
    path, env, words, texts = group
    formulas = [r["ast"][0] for r in R.read_sentences(env, words, {}, texts)]
    answer, _ = R.ask(env, words, {}, R.f1(texts[0]))
    assert R.reads_with(answer, formulas[0])
    assert not R.reads_with(answer, formulas[2]) and not R.reads_with(answer, None)
    assert not R.reads_with({**answer, "status": "many"}, formulas[0])


def test_the_candidate_limit_is_leans_on_both_sides(group):
    path, env, words, texts = group
    records = R.limit_records(path, env, words, {}, texts, repeat=1)
    assert [(r["candidates"], r["status"] == "budget", r["code"]) for r in records][1] == (65, True, "QuestionTooLong")
    assert records[0]["candidates"] == 64 and records[0]["status"] != "budget"


def test_the_default_run_is_the_whole_sealed_corpus():
    seal = json.loads((ROOT / "conformance/english-lean/corpus-seal.json").read_text())
    sizes = {row["unique_asts_roundtripped"] for row in seal["generated"] if row["stream"] == "english-surface"}
    args = R.arguments([])
    assert sizes == {args.per_config} and args.per_config == E.PER_CONFIG
    assert args.per_usecase == E.PER_USECASE
    assert R.coverage({}, args.per_config, args.per_usecase)["whole"]


def _row(**changed):
    return {"asked": 5, "drawn": 5, "sentences": 5, "dropped": {"none": 1}, **changed}


@pytest.mark.parametrize("configs, sizes, left_out", [
    ({"a": _row()}, (300, 500), {}),                                       # a sample of the round-trip streams
    ({"a": _row()}, (5000, 100), {}),                                      # a sample of the use-case streams
    ({"a": _row(drawn=4)}, (5000, 500), {"short_streams": {"a": 4}}),      # a stream that stalled
    ({"a": _row(dropped={"unavailable": 2})}, (5000, 500), {"unavailable_reads": {"a": 2}}),  # no answer: not "none"
    ({"a": {"skipped": "ValueError: x"}}, (5000, 500), {"skipped": ["a"]}),
])
def test_coverage_is_whole_only_when_nothing_is_left_out(configs, sizes, left_out):
    result = R.coverage(configs, *sizes)
    assert result["whole"] is False
    assert {k: v for k, v in result.items() if k in ("short_streams", "unavailable_reads", "skipped") and v} == left_out


def test_coverage_is_whole_with_duplicates_and_plain_refusals():
    # A text drawn twice is one sentence, and a sentence Lean does not read has an answer: neither leaves anything out.
    assert R.coverage({"a": _row(sentences=3), "b": {**_row(), "dropped": {"none": 5}}}, 5000, 500)["whole"] is True


def test_every_sentence_is_kept_or_counted_as_dropped(group):
    path, env, words, texts = group
    sentences = [*texts, "Qqq rrr sss."]
    result = R.run_config(path, env, words, {}, sentences)
    assert (result["sentences"], result["one_formula"], result["dropped"]) == (4, 3, {"none": 1})
    assert "ast" not in result["questions"][0]["outcome"]


def test_a_failed_service_is_unavailable_not_a_crash(group, monkeypatch):
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    path, env, words, texts = group

    def failed(*_args, **_kwargs):
        raise CheckerUnavailable("CheckerUnavailable: gone")
    monkeypatch.setattr(relay, "rows", failed)
    assert R.ask(env, words, {}, R.f1(texts[0]))[0]["status"] == "unavailable"
    result = R.run_config(path, env, words, {}, texts)
    assert (result["one_formula"], result["dropped"]) == (0, {"unavailable": 3})


def test_a_run_merges_its_slices_and_accounts_for_every_sentence(group, monkeypatch):
    path, env, words, texts = group
    monkeypatch.setattr(R, "TARGETS", [(path, env, {}, words)])
    monkeypatch.setattr(R, "SLICE", 2)
    configs, questions, moved, limits = R.run({}, {0: [*texts, texts[0], "Qqq rrr sss."]})
    row = configs[path]
    assert (row["asked"], row["drawn"], row["sentences"], row["stalled"]) == (5, 5, 4, 0)
    assert row["one_formula"] + sum(row["dropped"].values()) == row["sentences"]
    assert (row["questions"], row["moved"]) == (len(questions), len(moved))
    assert sum(q["kind"] == "f1" for q in questions) == 3 and {r["candidates"] for r in limits} == {64, 65}
    assert R.coverage(configs, 5000, 500)["whole"] is True


def test_a_delivered_row_has_the_whole_corpus_behind_it():
    evidence = json.loads((BATCH / "evidence/question-reverse.json").read_text())
    rows = [line for line in (BATCH / "REPORT.md").read_text().splitlines() if line.startswith("| F1 question for every")]
    assert len(rows) == 1
    assert evidence["coverage"]["whole"] is True or "| delivered |" not in rows[0]
    assert (evidence["per_config"], evidence["per_usecase"]) == (E.PER_CONFIG, E.PER_USECASE) or \
        "| delivered |" not in rows[0]
