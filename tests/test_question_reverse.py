"""The reverse question corpus of Q1.3 (`conformance/question_reverse.py`, docs/spec/question-answering-PLAN.md Q1.3)
on a small fixed slice: the builder of each form, the mutants, the moved-word sentences, the measures' arithmetic,
and the group document's questions read by Lean, with the candidate limit on both sides."""
from __future__ import annotations

import hashlib
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


def test_the_default_run_is_the_corpus_size():
    seal = json.loads(R.SEAL.read_text())
    sizes = {row["unique_asts_roundtripped"] for row in seal["generated"] if row["stream"] == "english-surface"}
    args = R.arguments([])
    assert sizes == {args.per_config} and args.per_config == E.PER_CONFIG
    assert args.per_usecase == E.PER_USECASE


def _configs(**changed):
    """Rows of a run that left nothing out: every stream of the seal with its digest, and one use-case stream."""
    seal = json.loads(R.SEAL.read_text())["generated"]
    row = {"asked": 5, "drawn": 5, "sentences": 5, "dropped": {"none": 1}}
    rows = {r["vocabulary"]: {**row, "stream_sha256": r["corpus_sha256"]} for r in seal if "vocabulary" in r}
    return rows | {"ordinary": {**rows["ordinary"], **changed}, "use-case": row}


def test_the_seal_names_the_streams_the_run_does_not_draw():
    assert R.coverage(_configs(), 5000, 500)["other_sealed_streams"] == {"english-mixed": 6757, "natural-view": 1220}
    assert R.coverage(_configs(), 5000, 500)["sealed_streams"] == 17


def test_a_stream_draws_its_use_cases_claims_as_the_sealed_one_does(monkeypatch):
    # The whole stream is compared with the seal's digest by `coverage` on a full run; here, that the claims come in.
    name = "claude-constitution-excerpt"
    env = Environment(json.loads((ROOT / f"usecases/{name}/environment.json").read_text()))
    claims = E.use_case_claims(f"{name}-reviewed", env)
    assert claims and E.use_case_claims("ordinary", env) == []
    monkeypatch.setattr(E, "CONFIGS", [(name, env, {}, EnglishVocabulary(env))])
    plain = [text for _, text, _ in E.streams(0, 300, 0, [])]
    sealed = [text for _, text, _ in E.streams(0, 300, 0, [], claims=True)]
    assert len(sealed) == 300 and set(sealed) != set(plain)


@pytest.mark.parametrize("changed, sizes, left_out", [
    ({}, (300, 500), {}),                                                  # a sample of the round-trip streams
    ({}, (5000, 100), {}),                                                 # a sample of the use-case streams
    ({"drawn": 4}, (5000, 500), {"short_streams": {"ordinary": 4}}),       # a stream that stalled
    ({"dropped": {"unavailable": 2}}, (5000, 500), {"unavailable_reads": {"ordinary": 2}}),  # no answer: not "none"
    ({"skipped": "ValueError: x"}, (5000, 500), {"skipped": ["ordinary"], "short_streams": None}),
    ({"stream_sha256": "0" * 64}, (5000, 500), {"unsealed_streams": ["ordinary"]}),  # not the sealed stream
])
def test_coverage_is_whole_only_when_nothing_is_left_out(changed, sizes, left_out):
    result = R.coverage(_configs(**changed), *sizes)
    assert result["whole_streams"] is False
    names = ("short_streams", "unavailable_reads", "skipped", "unsealed_streams")
    assert {k: v for k, v in result.items() if k in names and v} == {k: v for k, v in left_out.items() if v}


def test_coverage_needs_every_stream_of_the_seal():
    configs = _configs()
    del configs["order"]
    result = R.coverage(configs, 5000, 500)
    assert result["whole_streams"] is False and result["unsealed_streams"] == ["order"]


def test_coverage_is_whole_with_duplicates_and_plain_refusals():
    # A text drawn twice is one sentence, and a sentence Lean does not read has an answer: neither leaves anything out.
    configs = _configs(sentences=3, dropped={"none": 5})
    assert R.coverage(configs, 5000, 500)["whole_streams"] is True


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
    assert R.coverage(configs, 5000, 500)["short_streams"] == {}


def test_a_listed_question_keeps_its_head_length_and_hash():
    text = "Is it the case that " + "a " * 1000 + "b?"
    miss = {"config": "c", "kind": "f1", "question": text, "expected": None, "same": False, "ms": 1.0,
            "outcome": {"status": "budget", "code": "QuestionTooLong"}}
    listed = R.measures([miss], [], [])["f1"]["misses"][0]
    assert listed["question"] == text[:R.LISTED_HEAD] and listed["bytes"] == len(text)
    assert listed["sha256"] == hashlib.sha256(text.encode()).hexdigest() and listed["status"] == "budget"


def test_a_delivered_row_has_the_whole_corpus_behind_it():
    evidence = json.loads((BATCH / "evidence/question-reverse.json").read_text())
    rows = [line for line in (BATCH / "REPORT.md").read_text().splitlines() if line.startswith("| F1 question for every")]
    assert len(rows) == 1
    assert evidence["coverage"]["whole_streams"] is True or "| delivered |" not in rows[0]
    assert (evidence["per_config"], evidence["per_usecase"]) == (E.PER_CONFIG, E.PER_USECASE)
    assert evidence["coverage"]["unsealed_streams"] == [] and evidence["coverage"]["sealed_streams"] == 17
    assert not evidence["coverage"]["other_sealed_streams"] or "| delivered |" not in rows[0]


def test_the_saved_evidence_stays_in_the_tree():
    assert (BATCH / "evidence/question-reverse.json").stat().st_size < 1_000_000  # DRI decision D4


# ------------------------------------------------------------------ q1-3b

BATCH_B = ROOT / "docs/question-answering/q1-3b"


def test_frontings_front_every_is_must_or_may_in_turn():
    assert R.frontings("Every member who is registered is eligible.") == [
        (3, "Is every member who registered is eligible?"), (5, "Is every member who is registered eligible?")]
    assert R.frontings("It is not the case that Ann must be verified.") == [
        (1, "Is it not the case that Ann must be verified?"), (7, "Must it is not the case that Ann be verified?")]
    assert R.frontings("Is Ann verified.") == [] and R.frontings("Ann registers.") == []
    assert R.put_back("Every member is registered.") == "every member is registered."


@pytest.mark.parametrize("sentence", ["Every member is registered.", "Every person must be given equal access.",
                                      "Ann is verified.", "Some member is registered and Ann is verified."])
def test_frontings_hold_q1_3s_question_and_its_put_back(sentence):
    question, back = R.f2(sentence)
    assert question in [q for _, q in R.frontings(sentence)] and back == R.put_back(sentence)
    assert all(R.put_back(sentence) in R.candidates(q) for _, q in R.frontings(sentence))


def _none(text):
    return {"status": "none", "span": [text.index("X"), len(text)]}


def test_closeness_names_leans_closest_its_ties_and_the_readers_sentence():
    cands = ["a is X b.", "a b is X.", "a X is b."]
    reads = [_none(cands[0]), _none(cands[1]), {"status": "rejected", "span": [0, 1]}]
    text = 'No reading. Closest sentence tried: "a is X b.". Unknown.'
    got = R.closeness(cands, reads, text, "a X is b.")
    assert got == {"candidates": 3, "named": True, "closest": 0, "ties": 1, "consistent": False, "reader": 2}
    reads[1] = _none("a is X b.")  # the same diagnosis start: a tie, and Lean's choice is its leftmost
    assert R.closeness(cands, reads, text, None) | {"reader": None} == {
        "candidates": 3, "named": True, "closest": 0, "ties": 2, "consistent": True, "reader": None}
    assert R.closeness(cands, reads, "No reading.", None)["closest"] is None
    assert R.closeness(["é is X."], [_none("é is X.")], "", None)["ties"] == 1  # bytes, not code points


def _asked(kind, status, closest=None, stream_config="c", **extra):
    q = {"config": stream_config, "sentence": "S.", "read": True, "kind": kind, "question": "Is a b c?",
         "expected": "a is b c.", "ms": 1.0, "same": status == "one", "other": False, "outcome": {"status": status}}
    if closest is not None:
        q["outcome"]["text"] = ""
        q["closest"] = {"candidates": 3, "named": True, "consistent": True, "reader": 1, **closest}
    return q | extra


def test_the_closest_shares_count_only_named_f2_questions_with_no_reading():
    questions = [_asked("f2", "one"), _asked("f2", "moved"), _asked("f1", "none", {"closest": 0, "ties": 1,
                                                                                   "candidates": 1}),
                 _asked("f2", "none", {"closest": 0, "ties": 2}), _asked("f2", "none", {"closest": 1, "ties": 1}),
                 _asked("f2", "none", {"closest": None, "ties": 0, "named": False})]
    m = R.closest_measure(questions)
    assert (m["no_reading"], m["named"], m["not_named"], m["one_candidate"], m["measured"]) == (4, 3, 1, 1, 2)
    assert (m["tied"], m["leftmost_tie"], m["moved_second"], m["not_the_readers"]) == (1, 1, 1, 1)
    assert (m["share_tied"], m["share_moved_second"], m["share_not_the_readers"]) == (0.5, 0.5, 0.5)
    assert len(m["examples"]) == 1 and m["examples"][0]["closest"] == "a is b c."


def test_every_stream_is_counted_and_a_missing_one_leaves_the_run_partial():
    configs = {f"{s}:x": {"stream": s, "sentences": 2, "one_formula": 1, "questions": 1} for s in R.STREAMS}
    questions = [_asked("f2", "one", stream_config=f"{s}:x") for s in R.STREAMS]
    counts = R.per_stream(configs, questions)
    assert list(counts) == list(R.STREAMS)
    assert all(row == {"configs": 1, "f2": 1, "f2_many": 0, "f2_other": 0, "f2_same": 1, "one_formula": 1,
                       "questions": 1, "sentences": 2} for row in counts.values())
    seal = json.loads(R.SEAL.read_text())["generated"]
    mixed = {r["vocabulary"]: (r["corpus_sha256"], r["texts"], 0)
             for r in json.loads((ROOT / "conformance/english-mixed-report.json").read_text())["vocabularies"]}
    whole = {}
    for row in seal:
        if row["stream"] == "english-surface":
            whole[row["vocabulary"]] = {"stream": "english-surface", "stream_sha256": row["corpus_sha256"],
                                        "asked": 5000, "drawn": 5000}
            whole[f"random-earley:{row['vocabulary']}"] = {
                "stream": "random-earley", "random_earley_sha256": row["random_earley_corpus_sha256"],
                "document_sha256": row["document_corpus_sha256"], "documents_not_their_sentences": 0}
    assert R.coverage_b(whole, mixed, 1220, 5000, 500)["whole_streams"] is True
    assert R.coverage_b(whole, mixed, 1219, 5000, 500)["whole_streams"] is False          # a statement left out
    assert R.coverage_b(whole, dict(list(mixed.items())[1:]), 1220, 5000, 500)["mixed_unmatched"] == [next(iter(mixed))]
    del whole["random-earley:ordinary"]
    result = R.coverage_b(whole, mixed, 1220, 5000, 500)
    assert result["whole_streams"] is False and result["unsealed_random_earley"] == ["ordinary"]


def test_every_fronting_of_the_group_document_is_read_by_lean(group):
    path, env, words, texts = group
    result = R.run_config_b(path, env, words, {}, texts, False, False)
    by = {(q["sentence"], q["at"]): q for q in result["questions"]}
    assert sorted(by) == [("Ann is verified.", 1), ("Every member is registered.", 2),
                          ("Every member who is registered is eligible.", 3),
                          ("Every member who is registered is eligible.", 5)]
    clause = texts[1]
    assert by[(clause, 3)]["outcome"]["code"] == "QuestionWordMoved" and not by[(clause, 3)]["same"]
    assert by[(clause, 5)]["same"] and all(by[(s, k)]["same"] for s, k in by if s != clause)
    m = R.fronting_measure(result["questions"])
    assert (m["frontings"], m["sentences"], m["reached"], m["share"], m["limited"]) == (4, 3, 3, 1.0, 0)
    assert m["by_subject"]["other subject"] == {"limited": 0, "reached": 1, "sentences": 1, "several_same": 0}
    assert m["outcomes"] == {"moved:QuestionWordMoved": 1, "one": 3} and m["other_formula"] == []
    budget = {**by[(clause, 3)], "outcome": {"status": "budget", "code": "QuestionTooLong"}}
    m = R.fronting_measure([budget, {**budget, "at": 5}, by[("Ann is verified.", 1)]])
    assert (m["sentences"], m["reached"], m["limited"], m["share"], m["share_within_limits"]) == (2, 1, 1, 0.5, 1.0)


def test_a_question_with_no_reading_has_leans_closest_among_its_candidates(group):
    path, env, words, _ = group
    sentence = "Every member who registered is eligible."
    result = R.run_config_b(path, env, words, {}, [sentence], True, True)
    assert result["reads"][sentence]["one"] is False
    q = next(q for q in result["questions"] if q["kind"] == "f2")
    assert q["question"] == "Is every member who registered eligible?" and q["outcome"]["status"] == "none"
    cands = R.candidates(q["question"])
    assert q["closest"]["named"] and cands[q["closest"]["closest"]] in q["outcome"]["text"]
    assert q["closest"]["consistent"] and q["closest"]["reader"] == cands.index(R.put_back(sentence))
    f1 = next(q for q in result["questions"] if q["kind"] == "f1")
    assert f1["outcome"]["status"] == "none" and f1["closest"]["candidates"] == 1


def test_a_norm_documents_units_say_why_no_question_reaches_them():
    own = ROOT / "usecases/question-answering/udhr-part07.ve.md"
    data, units = R.norm_units(own.read_text())
    env = Environment(data)
    sentences = [t for _, _, t in units if R.one_sentence(t)]
    reads = R.run_config_b("udhr-part07", env, EnglishVocabulary(env), {}, sentences, False, False)["reads"]
    counts, examples = R.unit_reach(units, reads)
    assert sum(counts.values()) == len(units) and not any(why == "reached" for _, _, why in counts)
    assert all(kind == "meta" or why.startswith("english.read:") for kind, _, why in counts if why != "not one sentence")
    assert all(1 <= len(texts) <= 2 for texts in examples.values()) and set(examples) == {"/".join(k) for k in counts}
    assert R.why("A b.", {"A b.": {"one": True}}) == "reached" and R.why("A\nb.", {}) == "not one sentence"


def test_the_mixed_stream_is_its_generators_draw():
    texts, checks = R.mixed_texts(only={0})
    report = json.loads((ROOT / "conformance/english-mixed-report.json").read_text())["vocabularies"][0]
    (name, (_, _, sentences)), = texts.items()
    assert name == report["vocabulary"] and checks[name] == (report["corpus_sha256"], report["texts"], 0)
    assert sentences and all(s.endswith(".") for s in sentences)  # one formula each; a long one wraps


def test_the_natural_stream_is_each_rendered_statement():
    from conformance import natural_surface as N
    from ve import ast
    env = Environment(json.loads((ROOT / "examples/fluent/environment.json").read_text()))
    formula = ast.Unary("reviewed", ast.Const("legacy"))

    def audit():
        N._measure("x", [formula, formula], env)
        N.parse_english_argument(env, "")
        raise AssertionError("the audit goes on past its statements")
    texts, statements = R.natural_texts(audit)
    assert statements == 2 and texts["x"][2] == [N.render_natural_sentence(formula, env).text + "."] * 2


def test_the_random_earley_stream_skips_the_sealed_texts(monkeypatch):
    from conformance.english_surface import vocabularies
    name, env = next(iter(vocabularies()))
    monkeypatch.setattr(R, "TARGETS", [(name, env, {}, EnglishVocabulary(env))])
    texts, info = R.earley_stream(0, [], count=10)
    assert len(set(texts)) == 10 and info["documents"] == 2 and info["documents_not_their_sentences"] == 0
    again, _ = R.earley_stream(0, texts[:3], count=10)
    assert again[:7] == texts[3:] and not set(again) & set(texts[:3])


def test_the_q1_3b_evidence_stays_in_the_tree():
    evidence = json.loads((BATCH_B / "evidence/question-reverse-b.json").read_text())
    assert (BATCH_B / "evidence/question-reverse-b.json").stat().st_size < 1_000_000  # DRI decision D4
    assert list(evidence["streams"]) == list(R.STREAMS) and evidence["coverage"]["whole_streams"] is True
