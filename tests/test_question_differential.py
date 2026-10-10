"""Q1 three ways (review C of Astra, a B item of the DRI ruling of 2026-10-09): Lean's question reader against an
independent Python reader, and each reading's meaning evaluated by Python, Lean and Rust.

Lean is the only question reader VE runs, so the earlier conformance (spec rows, Lean `#guard`s, the live mode) ran
one reader three times. Here:

* **Two readers.** `tests/question_reference.py` reads questions from the spec's definitions over Python's own
  English reader (the Lark all-derivations parse and the hand parser), sharing no code with `VE.Question`. Every
  fixture question and its seeded 1-fault and 2-fault mutants (`one_faults`: a word deleted, doubled or swapped with
  the next, a determiner or the auxiliary replaced, an inner auxiliary fronted, F1 and F2 converted into each other,
  a clause word inserted, the question mark dropped, doubled, spaced or preceded by a bad character, a wh-word or a
  conclusion marker) is read by both, and the status, the code the outcome fixes, the asked form, sentence and
  formula, and the rephrasings must agree. An outcome the reference cannot decide as Lean does is excluded with its
  reason (a candidate's work budget, a lexical refusal other than spacing or a bad character); the exclusions are
  counted and bounded.
* **Three evaluators.** Every formula Lean reads a question as is checked by Rust's kernel (`check`) and evaluated on
  seeded models of its vocabulary by Python's evaluator, by Lean's metered evaluator (`ve_metered`, called directly:
  the public `ve.evaluate` keeps Python's authority) and by Rust (`evaluate-budgeted`); the three values must agree.

The comparison can fail: a reference reader without the moved-word rule, or with the outcome order changed, gives
disagreements on the fixtures (`test_the_comparison_can_fail`).

* **Every part.** A word put back inside a part (a `formula` or `atom` read by a rule with words of its own) is a
  moved word (looprecheck of the ruling, B). `test_every_part_of_every_rule_is_a_clause` writes one sentence for
  every such rule of the grammar sources (`ve/english_grammar/*.json`, so a new rule is covered when it is added),
  fronts each `is` of it, and requires `moved` for a word of a part or a guard and `one` for the rule's own word,
  from Lean and from the reference alike.
* **Every joined verb phrase.** So is a word put back inside one of the verb phrases a rule joins with `and` or
  `or` (looprecheck 2, B). `test_every_joined_verb_phrase_is_a_part` writes every such rule of the grammar sources
  (two or more verb phrases, the nonterminals of type `relative` in the specs' 2.4 tables) inside a sentence of a
  vocabulary that reads it, fronts each `is`, and requires `moved`, with the word fronted from every phrase at once
  offered when that reads with the same meaning (`Is some member registered and eligible?`).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import re

import pytest

import question_fixtures as F
import question_reference as R
from ve.backends import relay
from ve.english import EnglishVocabulary

pytestmark = pytest.mark.filterwarnings("ignore::ve.english.UnreviewedVocabularyWarning")

MODE = "english.question"
SEED = 20261009
# F-LFv3's vocabulary is refused before any question is read (G23); every other frame is compared.
FRAMES = [frame for frame in dict.fromkeys(row[1] for row in F.FIXTURES) if frame != "F-LFv3"]
DETERMINERS = ("every", "some", "no", "a", "an")
# The CI sample: every 1-fault mutant on the frames whose questions are short (G, FD), a seeded sample on A and U,
# whose questions have many candidates; Ar, Ac and Ad have A's vocabulary (spec 7.4), so only their fixtures run.
# `VE_QUESTION_DIFF_DEEP=1` runs every mutant of every frame (about 2,100 inputs, a few minutes).
DEEP = os.environ.get("VE_QUESTION_DIFF_DEEP") == "1"
ONE_FAULTS = {"G": None, "FD": None, "A": 12, "U": 12, "Ar": 0, "Ac": 0, "Ad": 0}
TWO_FAULTS = {"G": 3, "FD": 3, "A": 1, "U": 1, "Ar": 0, "Ac": 0, "Ad": 0}
MAX_EXCLUDED = 0.05     # the share of inputs the reference may exclude
MODELS = 6              # seeded models per reading


def one_faults(question: str) -> list[str]:
    """The 1-fault mutants of a question (the module docstring lists the kinds)."""
    out = []
    core = question[:-1] if question.endswith("?") else question
    words = core.split(" ")
    join = lambda ws: " ".join(ws) + "?"
    for i in range(1, len(words)):
        out.append(join(words[:i] + words[i + 1:]))
        out.append(join(words[:i + 1] + words[i:]))
        if i + 1 < len(words):
            out.append(join(words[:i] + [words[i + 1], words[i]] + words[i + 2:]))
        for clause in R.CLAUSE_WORDS[:2]:
            out.append(join(words[:i] + [clause] + words[i:]))
    for i, word in enumerate(words):
        if word.lower() in DETERMINERS:
            for other in DETERMINERS:
                if other != word.lower():
                    out.append(join(words[:i] + [R.capitalise(other) if i == 0 else other] + words[i + 1:]))
    if words[0].lower() in R.AUXILIARIES:
        for aux in R.AUXILIARIES:
            if aux != words[0].lower():
                out.append(join([R.capitalise(aux)] + words[1:]))
    sh = R.shape(question)
    if sh[0] == "caseThat":
        body = sh[1].split(" ")
        out.extend(join([R.capitalise(w)] + body[:i] + body[i + 1:]) for i, w in enumerate(body) if w in R.AUXILIARIES)
    for c in R.candidates(question):
        if c.form == "fronted":
            out.append(f"{R.CASE_FRAME}{c.sentence[:-1]}?")
            # the auxiliary fronted again from every other place of the sentence it is put back into
            ws = c.sentence[:-1].split(" ")
            out.extend(join([R.capitalise(w)] + ws[:i] + ws[i + 1:]) for i, w in enumerate(ws) if w == c.aux and i)
    out += [core, core + "??", core + " ?", core + "!?", core + ".", core[:1].lower() + core[1:] + "?",
            join(["Who"] + words[1:]), join(words[:1] + ["therefore"] + words[1:])]
    return [q for q in dict.fromkeys(out) if q != question and q.strip()]


def corpus() -> list[tuple[str, str, str]]:
    """(frame, kind, question): every fixture question, its 1-fault mutants and seeded 2-fault mutants."""
    rng = random.Random(SEED)
    rows = []
    for fixture, frame, question, _ in F.FIXTURES:
        if frame not in FRAMES or len(question) > 200:
            continue
        rows.append((frame, "zero-fault", question))
        ones = one_faults(question)
        cap = None if DEEP else ONE_FAULTS.get(frame)
        rows += [(frame, "one-fault", q) for q in (ones if cap is None else rng.sample(ones, min(cap, len(ones))))]
        for q in rng.sample(ones, min(3 if DEEP else TWO_FAULTS.get(frame, 1), len(ones))):
            twos = one_faults(q)
            if twos:
                rows.append((frame, "two-fault", rng.choice(twos)))
    return list(dict.fromkeys(rows))


@pytest.fixture(scope="module")
def readers():
    out = {}
    for frame in FRAMES:
        env = F.environment(frame)
        out[frame] = R.Reader(env, EnglishVocabulary(env, _defer_overlay_refusals=True))
    return out


def lean_results(rows) -> list[dict]:
    cases = []
    for frame, _, question in rows:
        case = F.request(frame, question)
        cases.append(case)
    answered = relay.rows(MODE, cases)
    assert len(answered) == len(cases)
    out = []
    for row in answered:
        assert row.get("status") == "ok", row
        out.append(row["result"])
    return out


def compare(rows, readers, reference=None):
    """(agreements, disagreements, exclusions) of Lean and the reference reader over `rows`."""
    results = lean_results(rows)
    agree, differ, excluded = [], [], []
    for (frame, kind, question), result in zip(rows, results, strict=True):
        ours = (readers[frame] if reference is None else reference(frame)).ask(question)
        if ours["status"] == "excluded":
            excluded.append((frame, question, ours["reason"], result["status"]))
            continue
        theirs = R.lean_view(result)
        (agree if ours == theirs else differ).append((frame, kind, question, theirs, ours, result))
    return agree, differ, excluded


@pytest.fixture(scope="module")
def compared(readers):
    rows = corpus()
    return rows, compare(rows, readers)


def test_lean_and_the_reference_reader_agree(compared):
    rows, (agree, differ, excluded) = compared
    shown = [{"frame": f, "kind": k, "question": q, "lean": t, "python": o} for f, k, q, t, o, _ in differ[:8]]
    assert not differ, json.dumps(shown, indent=1, ensure_ascii=False)
    assert len(excluded) <= MAX_EXCLUDED * len(rows), excluded[:10]
    # Not vacuous: every kind of mutant ran on every frame, and the comparison saw every outcome the mode has.
    for frame in FRAMES:
        kinds = ("zero-fault", "one-fault", "two-fault") if DEEP or ONE_FAULTS.get(frame) != 0 else ("zero-fault",)
        for kind in kinds:
            assert any(r[0] == frame and r[1] == kind for r in rows), (frame, kind)
    statuses = {t["status"] for _, _, _, t, _, _ in agree}
    assert statuses >= {"one", "moved", "none", "rejected", "notQuestion", "indefinite", "many"}, statuses
    assert sum(1 for *_, t, _, _ in agree if t["status"] == "moved") >= 3


def test_the_comparison_can_fail(readers, monkeypatch):
    """Seeded faults in the reference reader each give a disagreement: the moved-word rule dropped, the rephrasing
    filter dropped, `that` left out of the clause words, parts not counted as clauses, joined verb phrases not
    counted as parts, the indefinite rephrasings dropped, and the lexical refusals checked out of position order. (Spec 7.8's order fault, a refused candidate put before one that reads,
    has no input here: 195,759 random questions over G's vocabulary gave no question with both, and no vocabulary
    the lexicon policy admits was found to give one; the proof of `readQuestion_complete` catches it, seeded bug 3
    of the integration report.)"""
    rows = [(frame, "zero-fault", question) for _, frame, question, _ in F.FIXTURES if frame in FRAMES]
    rows.append(("G", "one-fault", "Is every member eligible! ?"))
    original_read, original_fault = R.Reader.read_question, R.lexical_fault

    def no_indefinite(self, question):
        o = R.Reader.classify(self, question)
        return o

    def spacing_first(outside):
        return "BadSpacing" if outside != outside.rstrip() else original_fault(outside)
    faults = {
        "no moved-word rule": (R.Reader, "moved_out", lambda self, c: False),
        "no rephrasing filter": (R.Reader, "askable", lambda self, q: True),
        "no indefinite rephrasings": (R.Reader, "read_question", no_indefinite),
        "that is not a clause word": (R, "CLAUSE_WORDS", ("who", "which")),
        "no parts": (R.Reader, "sentence_kinds", lambda self: set()),
        "no joined verb phrases": (R.Reader, "joined", lambda self, sentence, node: []),
        "spacing before bad characters": (R, "lexical_fault", spacing_first),
    }
    for name, (owner, attribute, replacement) in faults.items():
        with monkeypatch.context() as m:
            m.setattr(owner, attribute, replacement)
            fresh = {frame: R.Reader(r.env, r.words) for frame, r in readers.items()}
            _, differ, _ = compare(rows, fresh, reference=lambda frame: fresh[frame])
            assert differ, name
    assert R.Reader.read_question is original_read


# ------------------------------------------------------------------ every part of every rule

GRAMMARS = Path(__file__).resolve().parents[1] / "ve/english_grammar"
PARTS = ("formula", "atom")
# What each other nonterminal of a part-bearing rule is written as, on G's vocabulary.
FILLS = {"declaration": "member", "relative_pronoun": "who", "guard": "is registered", "article": "a",
         "term": "ann", "count": "one", "list_marker": ("(a)", "(b)")}
SENTENCES = ("ann is eligible", "bo is verified")
# Part-bearing rules whose sentence G's vocabulary does not read (F1's question is not `one`), with the reason.
UNREAD = {"reach.body": "reach needs a relation of two members; G has none",
          "reach.body.listed": "reach needs a relation of two members; G has none"}


def part_rules() -> list[dict]:
    """Every rule of the grammar sources that reads a part: a `formula` or `atom` beside a word of its own."""
    out = []
    for path in sorted(GRAMMARS.glob("*@*.json")):
        for row in json.loads(path.read_text()):
            rhs = row["rhs"]
            if row.get("status") == "proposed" or not any(isinstance(x, dict) and x.get("n") in PARTS for x in rhs):
                continue
            if any(isinstance(x, str) or "p" in x for x in rhs):
                out.append(row)
    return out


def write_rule(row) -> tuple[str, list[tuple[int, bool]]]:
    """The rule written out: its words, each nonterminal filled; and for each `is` its character offset and whether
    it is inside a nonterminal (a part or a guard) rather than one of the rule's own words."""
    pieces, parts, markers = [], iter(SENTENCES * 4), iter(FILLS["list_marker"])
    for x in row["rhs"]:
        if isinstance(x, str):
            pieces.append((x, False, False))
        elif "p" in x:
            pieces.append((x["p"], x.get("before", False), False))
        elif x["n"] in PARTS:
            pieces.append((next(parts), False, True))
        elif x["n"] == "list_marker":
            pieces.append((next(markers), False, False))
        else:
            pieces.append((FILLS[x["n"]], False, True))  # a nonterminal this test cannot write fails here
    text, offsets = "", []
    for piece, attached, inner in pieces:
        if text and not attached:
            text += " "
        start = len(text)
        text += piece
        for m in re.finditer(r"\bis\b", piece):
            offsets.append((start + m.start(), inner))
    return text, offsets


def test_every_part_of_every_rule_is_a_clause(readers):
    rules = part_rules()
    assert {r["tag"] for r in rules} >= {"compact.if", "compact.and", "compact.or", "universal.global", "negation",
                                         "existential.global", "listing.all.words"}
    cases = []
    for row in rules:
        sentence, offsets = write_rule(row)
        case_that = f"{R.CASE_FRAME}{sentence}?"
        cases.append((row["tag"], "F1", case_that, None))
        for at, inner in offsets:
            cases.append((row["tag"], "inner" if inner else "own",
                          f"Is {sentence[:at]}{sentence[at + 3:]}?", case_that))
    results = lean_results([("G", "part", q) for _, _, q, _ in cases])
    read = {tag for (tag, kind, _, _), result in zip(cases, results) if kind == "F1" and result["status"] == "one"}
    assert {r["tag"] for r in rules} - read == set(UNREAD), sorted({r["tag"] for r in rules} - read)
    # A rule with an `is` of its own offers that word fronted, which means what F1's question means.
    own = {}
    for tag, kind, question, _ in cases:
        if kind == "own":
            own.setdefault(tag, []).append(question)
    moved = set()
    for (tag, kind, question, case_that), result in zip(cases, results, strict=True):
        theirs = R.lean_view(result)
        assert readers["G"].ask(question) == theirs, (tag, question, theirs)
        if tag in UNREAD or kind == "F1":
            continue
        if kind == "inner":
            # Refused, with the questions VE reads in its place: the main sentence's word fronted where it has
            # one, else F1's question (each meaning is offered once).
            rephrasings = theirs.get("rephrasings", ())
            assert theirs["status"] == "moved" and rephrasings, (tag, question, theirs)
            assert all(readers["G"].askable(r) for r in rephrasings), (tag, question, theirs)
            assert rephrasings == own.get(tag, [case_that]), (tag, question, theirs)
            moved.add(tag)
        else:
            assert theirs["status"] == "one", (tag, question, theirs)
    assert moved == read, sorted(read - moved)


# ------------------------------------------------------------------ every joined verb phrase

JOIN_WORDS = ("and", "or")
# Where each nonterminal that joins verb phrases is written: the frame whose vocabulary reads it, and the sentence
# around it. A new joining nonterminal fails `test_every_joined_verb_phrase_is_a_part` until it is placed here.
JOIN_CONTEXTS = {"some_tail": ("G", "some member {}"),
                 "natural_tail": ("FD", "every deployed service {}"),
                 "guard": ("G", "every member who {} is eligible"),
                 "alt_verb_phrase": ("Alt", "every action available to rob {}")}
# What each verb phrase is written as in each frame, in turn.
PHRASE_FILLS = {"G": {"relative": ("is registered", "is eligible", "is verified"),
                      "guard_atom": ("is registered", "is eligible", "is verified"),
                      "guard_relative": ("is verified", "is eligible")},
                "FD": {"relative": ("is reviewed",), "owner_clause": ("has an owner",)},
                "Alt": {"alt_verb_atom": ("is taken", "is inaction")}}


def join_rules() -> list[dict]:
    """Every rule of the grammar sources that joins verb phrases: it reads `and` or `or`, and two or more of its
    nonterminals are verb phrases (type `relative` in the specs' 2.4 tables)."""
    out = []
    for path in sorted(GRAMMARS.glob("*@*.json")):
        for row in json.loads(path.read_text()):
            rhs = row["rhs"]
            phrases = [x for x in rhs if isinstance(x, dict) and x.get("n") in R.phrase_kinds()]
            if row.get("status") != "proposed" and len(phrases) >= 2 and any(x in JOIN_WORDS for x in rhs):
                out.append(row)
    return out


def write_join(row) -> tuple[str, str, list[int], list[int]]:
    """The frame, the rule written inside its context sentence, the offset of each `is` inside a joined phrase, and
    the offset of each `is` of the context (the main sentence's word)."""
    frame, context = JOIN_CONTEXTS[row["lhs"]]
    fills = {n: iter(ws * 4) for n, ws in PHRASE_FILLS[frame].items()}
    text = ""
    phrases = []
    for x in row["rhs"]:
        piece, attached = (x, False) if isinstance(x, str) else (x["p"], x.get("before", False)) if "p" in x else (
            next(fills[x["n"]]), False)
        if text and not attached:
            text += " "
        if isinstance(x, dict) and "n" in x:
            phrases.append((len(text), len(text) + len(piece)))
        text += piece
    at = context.index("{}")
    sentence = context.format(text)
    words = [m.start() for m in re.finditer(r"\bis\b", sentence)]
    inner = [w for w in words if any(at + a <= w < at + b for a, b in phrases)]
    return frame, sentence, inner, [w for w in words if w not in inner]


def test_every_joined_verb_phrase_is_a_part(readers):
    rules = join_rules()
    assert {r["tag"] for r in rules} >= {"some-tail.two", "natural-tail.both", "guard.two", "verb-phrase.either",
                                         "verb-phrase.either-both", "verb-phrase.both"}, sorted(r["tag"] for r in rules)
    assert not {r["tag"] for r in rules} & {"some-tail.copula", "compact.and", "coordination.predicate-and"}
    readers = {**readers, "Alt": R.Reader(F.environment("Alt"), EnglishVocabulary(F.environment("Alt"),
                                                                                  _defer_overlay_refusals=True))}
    cases = []
    for row in rules:
        frame, sentence, inner, own = write_join(row)
        assert inner, (row["tag"], sentence)
        case_that = f"{R.CASE_FRAME}{sentence}?"
        fronted = lambda ws: f"Is {''.join(sentence[i] for i in range(len(sentence)) if not any(w <= i < w + 3 for w in ws))}?"
        cases.append((row["tag"], frame, "F1", case_that, None))
        cases += [(row["tag"], frame, "own", fronted([w]), None) for w in own]
        cases += [(row["tag"], frame, "inner", fronted([w]), fronted(inner)) for w in inner]
    results = lean_results([(frame, "join", q) for _, frame, _, q, _ in cases])
    own, case_that, moved = {}, {t: q for t, _, k, q, _ in cases if k == "F1"}, set()
    for (tag, frame, kind, question, _), result in zip(cases, results, strict=True):
        theirs = R.lean_view(result)
        assert readers[frame].ask(question) == theirs, (tag, question, theirs)
        assert theirs["status"] == "one" if kind in ("F1", "own") else theirs["status"] == "moved", (tag, question, theirs)
        if kind == "own":
            own.setdefault(tag, []).append(question)
    across = 0
    for (tag, frame, kind, question, both), result in zip(cases, results, strict=True):
        if kind != "inner":
            continue
        rephrasings = R.lean_view(result).get("rephrasings", [])
        assert rephrasings and all(readers[frame].askable(r) for r in rephrasings), (tag, question, rephrasings)
        meaning = next(r["ast"] for (t, _, k, _, _), r in zip(cases, results) if t == tag and k == "F1")
        reads = readers[frame].ask(both)
        # The main sentence's word where it has one; else the word fronted from every phrase at once, when that
        # reads with the same meaning; else F1's question.
        if tag in own:
            assert rephrasings == own[tag], (tag, question, rephrasings)
        elif reads.get("status") == "one" and reads["ast"] == meaning:
            assert rephrasings == [both], (tag, question, rephrasings)
            across += 1
        else:
            assert rephrasings == [case_that[tag]], (tag, question, rephrasings)
        moved.add(tag)
    assert moved == {r["tag"] for r in rules} and across >= 2, (sorted(moved), across)


# ------------------------------------------------------------------ the meaning, three ways

def _models(env, rng, count):
    """Seeded models of `env`'s vocabulary: each sort its constants and two more elements (a value sort such as
    `$string` its constants only), each predicate a random table, a functional and total one a random function."""
    from ve import FiniteModel
    data = env.to_dict()["vocabulary"]
    values = {e["sort"] for e in data["constants"].values() if e["sort"].startswith("$")} | {
        s for e in data["predicates"].values() for s in e["arguments"] if s.startswith("$")}
    out = []
    for _ in range(count):
        domains = {sort: [*(c for c, e in data["constants"].items() if e["sort"] == sort),
                          *(() if sort in values else (f"{sort}_x", f"{sort}_y"))]
                   for sort in [*data["sorts"], *sorted(values)]}
        relations = {}
        for name, entry in data["predicates"].items():
            *keys, last = entry["arguments"]
            tuples = [[]]
            for sort in keys:
                tuples = [t + [e] for t in tuples for e in domains.get(sort, [])]
            if entry.get("functional") and entry.get("total"):
                relations[name] = [t + [rng.choice(domains[last])] for t in tuples if domains.get(last)]
            else:
                relations[name] = [t + [e] for t in tuples for e in domains.get(last, []) if rng.random() < 0.5]
        wire = {"complete": True, "domains": domains, "constants": {c: c for c in data["constants"]},
                "relations": relations}
        out.append((wire, FiniteModel.from_dict(env, wire)))
    return out


def test_python_lean_and_rust_evaluate_each_reading_alike(compared, readers):
    from ve.ast import formula_from_data
    from ve.backends import rust_jsonl
    from ve.evaluate import _evaluate_lean, _evaluate_validated
    from ve.limits import MAX_EVALUATIONS
    _, (agree, _, _) = compared
    readings = {}
    for frame, _, _, theirs, _, result in agree:
        if theirs["status"] == "one":
            readings.setdefault((frame, json.dumps(result["ast"])), result["ast"])
    rng = random.Random(SEED)
    evaluated = {frame: 0 for frame in FRAMES}
    for (frame, _), ast in sorted(readings.items()):
        env = readers[frame].env
        formula = formula_from_data(env, ast)
        rust_env = rust_jsonl.rust_environment(env)
        assert rust_jsonl.run({"id": "q", "kind": "check", "environment": rust_env, "ast": ast})["well_typed"] is True
        for wire, model in _models(env, rng, MODELS):
            python = _evaluate_validated((formula,), model, max_evaluations=MAX_EVALUATIONS).value
            lean = _evaluate_lean(env, {"id": "q", "kind": "evaluate-budgeted", "model": model.to_dict(), "ast": [ast],
                                        "max_evaluations": MAX_EVALUATIONS, "max_trace_nodes": 0,
                                        "trace": False}).value
            rust = rust_jsonl.run({"id": "q", "kind": "evaluate-budgeted", "environment": rust_env,
                                   "model": wire, "ast": [ast]})
            assert python == lean == rust["value"], (frame, ast, wire, python, lean, rust)
            evaluated[frame] += 1
    assert all(n >= MODELS for n in evaluated.values()) and sum(evaluated.values()) >= 100, evaluated


def test_the_models_tell_readings_apart(readers):
    """The value comparison can fail: on the seeded models, G1's and G3's readings (every member is eligible, every
    member is verified) differ somewhere for each of the three evaluators."""
    from ve.ast import formula_from_data
    from ve.backends import rust_jsonl
    from ve.evaluate import _evaluate_lean, _evaluate_validated
    from ve.limits import MAX_EVALUATIONS
    env = readers["G"].env
    asts = [row[3]["ast"] for row in F.FIXTURES if row[0] in ("G1", "G3")]
    rust_env = rust_jsonl.rust_environment(env)
    differs = {"python": False, "lean": False, "rust": False}
    for wire, model in _models(env, random.Random(SEED), MODELS):
        values = {"python": [], "lean": [], "rust": []}
        for ast in asts:
            values["python"].append(_evaluate_validated((formula_from_data(env, ast),), model,
                                                        max_evaluations=MAX_EVALUATIONS).value)
            values["lean"].append(_evaluate_lean(env, {"id": "q", "kind": "evaluate-budgeted", "model": model.to_dict(),
                                                       "ast": [ast], "max_evaluations": MAX_EVALUATIONS,
                                                       "max_trace_nodes": 0, "trace": False}).value)
            values["rust"].append(rust_jsonl.run({"id": "q", "kind": "evaluate-budgeted", "environment": rust_env,
                                                  "model": wire, "ast": [ast]})["value"])
        for name, (a, b) in values.items():
            differs[name] |= a != b
    assert all(differs.values()), differs
