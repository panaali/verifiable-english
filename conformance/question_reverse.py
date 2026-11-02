"""Q1.3: the reverse question corpus, read by Lean's question reader (docs/spec/question-answering-PLAN.md Q1.3).

    uv run python -m conformance.question_reverse [--per-config N] [--per-usecase N] [--workers N] [--output PATH]

The defaults are the whole corpus (`english_lean_e2_evidence.PER_CONFIG`, `PER_USECASE`); the saved `coverage` says
what a run left out, compares each round-trip stream with its digest in the seal, and (`--part a`) names the seal's
other streams, which only `--part b` draws (q1-3b, below). For every corpus sentence Lean reads with one formula (the sealed stream of every corpus configuration of
`conformance.english_lean_e2_evidence`, and the units of every use-case `.ve.md` document under its own
environment), the script builds the F1 question, the F2 question where the sentence begins with a quantified or
named subject followed by *is*, *must* or *may* (plan 3.2), and spacing and capitalisation mutants of both. Each
question is sent alone to `english.question` and its answer is checked by the relay's `question_problem`; each
sentence with its fronted word put back at another word gap (the odd-English measure) is read by `english.read`.
Lean decides every outcome; this script only builds texts, compares formulas and counts. A worker takes one slice of
one configuration at a time, so the measured times carry the host's load and each other's (`workers`,
`load_average`). The result is
`docs/question-answering/q1-3/evidence/question-reverse.json`, cited by `docs/spec/question-answering-q1-report.md`.

`--part b` is q1-3b: every fronting of each sentence, the seal's other streams, the norm part documents and open
point 10.2, written to `docs/question-answering/q1-3b/evidence/question-reverse-b.json`.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import time
import warnings

from conformance import english_lean_e2_evidence as E

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/question-answering/q1-3/evidence/question-reverse.json"
SEAL = ROOT / "conformance/english-lean/corpus-seal.json"
FORMAT = "ve.question-reverse@1"
FRAME = "Is it the case that "
AUXILIARIES = ("is", "must", "may")
QUANTIFIERS = ("every", "some", "no", "all", "at")
# First words written in lower case inside a question; any other first word (a name) keeps its case.
OPENERS = QUANTIFIERS + ("for", "if", "it", "there", "both", "either", "neither", "the", "this", "each")
CLAUSE_WORDS = ("who", "that", "which", "whose")
PLAIN = re.compile(r'[A-Za-z][A-Za-z_-]*|"[^"\s]+"')
NAME = re.compile(r'[A-Z][A-Za-z_-]*|"[^"\s]+"')
MUTANTS = ("double-space", "space-before-mark", "leading-space", "lower-initial", "upper-auxiliary",
           "capital-body")
BUDGET_MS, BUDGET_64_MS = 100.0, 1000.0  # plan 3.6: p95 of a corpus question; a 64-candidate question
SLICE = 200  # sentences a worker takes at a time, so that the slow configurations share the workers
LISTED_HEAD = 120  # characters kept of a listed question; DRI decision D4 keeps evidence in the tree under 1 MB

# Filled before the workers fork: (name, env, options, words) per configuration, then per use-case document.
TARGETS: list = []


# ------------------------------------------------------------------ the questions (texts only)

def lower_initial(text: str) -> str:
    """`text` with its first letter in lower case when its first word is a sentence opener, else unchanged."""
    first = text.split(" ", 1)[0]
    return text[0].lower() + text[1:] if first.lower() in OPENERS else text


def f1(sentence: str) -> str:
    """The F1 question of a sentence ending with `.`."""
    return FRAME + lower_initial(sentence[:-1]) + "?"


def f2(sentence: str) -> tuple[str, str] | None:
    """(the F2 question, the sentence Lean should put back) when the sentence begins with a quantified subject
    without a clause or comma, or a one-word name, followed by is, must or may; else None. A subject with a
    clause is not built: which word is the main sentence's is Lean's decision (`VE.Question.Moved`)."""
    words = sentence[:-1].split(" ")
    k = next((i for i, word in enumerate(words) if word in AUXILIARIES), None)
    if not k or any("\n" in word for word in words[:k]):
        return None
    subject = words[:k]
    if subject[0].lower() in QUANTIFIERS:
        if not all(PLAIN.fullmatch(w) and w.lower() not in CLAUSE_WORDS + AUXILIARIES for w in subject[1:]):
            return None
    elif k != 1 or not NAME.fullmatch(subject[0]) or subject[0].lower() in OPENERS:
        return None
    head = lower_initial(" ".join(subject))
    return f"{words[k].capitalize()} {' '.join([head] + words[k + 1:])}?", " ".join([head] + words[k:]) + "."


def frontings(sentence: str) -> list[tuple[int, str]]:
    """(word index, F2 question) for each occurrence of is, must or may after the first word, in turn, whatever the
    subject (q1-3b): Lean decides which, if any, fronts the main sentence's word (`VE.Question.Moved`). Each
    question's put-back sentence is `put_back(sentence)`."""
    words = sentence[:-1].split(" ")
    return [(k, f"{word.capitalize()} {lower_initial(' '.join(words[:k] + words[k + 1:]))}?")
            for k, word in enumerate(words) if k and word in AUXILIARIES]


def put_back(sentence: str) -> str:
    """The sentence as a candidate of its own F2 questions: the word put back where it was."""
    return lower_initial(sentence[:-1]) + "."


def candidates(question: str) -> list[str]:
    """The F2 question's fronted word put back before every word of its rest after the first (plan 3.2's gaps,
    with a word separated by spaces), left to right: the moved-word sentences of the odd-English measure."""
    aux, _, rest = question[:-1].partition(" ")
    gaps = [word.start() for word in re.finditer(r"\S+", rest) if word.start() > 0]
    return [rest[:g] + aux.lower() + " " + rest[g:] + "." for g in gaps]


def mutants(question: str, form: str) -> list[tuple[str, str]]:
    """(kind, text) spacing and capitalisation mutants of a question; each differs from it."""
    body = len(FRAME) if form == "f1" else question.index(" ") + 1
    aux = question.split(" ", 1)[0]
    out = [("double-space", question.replace(" ", "  ")),
           ("space-before-mark", question[:-1] + " ?"),
           ("leading-space", " " + question),
           ("lower-initial", question[0].lower() + question[1:]),
           ("upper-auxiliary", aux.upper() + question[len(aux):]),
           ("capital-body", question[:body] + question[body].upper() + question[body + 1:])]
    return [(kind, text) for kind, text in out if text != question]


def long_question(sentences: list[str], words: int) -> str | None:
    """An F2 question with exactly `words` words after `Is` (so `words - 1` candidates), cycling the plain
    lower-case words of the corpus sentences; None when they have none."""
    pool = [w for s in sentences for w in s[:-1].split(" ") if w.isalpha() and w.islower()]
    if not pool:
        return None
    return "Is " + " ".join(pool[i % len(pool)] for i in range(words)) + "?"


# ------------------------------------------------------------------ Lean's answers

def read_sentences(env, words, options, texts: list[str]) -> list[dict]:
    """`english.read`'s checked outcome for each text: `{"status", "ast"}` (one formula list) or unavailable."""
    from ve.backends import english_lean as L
    from ve.backends import relay
    from ve.english_grammar import lexicon_id
    from ve.errors import CheckerUnavailable
    out = []
    for start in range(0, len(texts), 400):
        cases = [{**L.request(env, text, words, options), "id": f"t{start + k}"}
                 for k, text in enumerate(texts[start:start + 400])]
        try:
            rows = relay.rows("english.read", cases)
        except CheckerUnavailable as failure:
            rows = [{"status": "error", "error": str(failure)}] * len(cases)
        for case, row in zip(cases, rows, strict=True):
            text = case["source"]
            expected = {**L.identities(env, text, words, case["lexicon"]), "lexicon_id": lexicon_id(case["lexicon"])}
            problem = row.get("error", row) if row.get("status") != "ok" else \
                L.response_problem(row["result"], expected, env, text)
            out.append({"status": "unavailable", "error": str(problem)[:300]} if problem else
                       {"status": row["result"]["status"], "ast": row["result"].get("ast"),
                        **{k: row["result"][k] for k in ("code", "span") if k in row["result"]}})
    return out


def ask(env, words, options, question: str) -> tuple[dict, float]:
    """`english.question`'s checked answer to one question, as the relay sends it, and its milliseconds."""
    from ve.backends import english_lean as L
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    case = {**L.request(env, question, words, options), "id": L.QUESTION_MODE, "question": question}
    started = time.perf_counter()
    try:
        row = relay.rows(L.QUESTION_MODE, [case])[0]
    except CheckerUnavailable as failure:
        row = {"status": "error", "error": str(failure)}
    ms = (time.perf_counter() - started) * 1000
    if row.get("status") != "ok":
        return {"status": "unavailable", "error": str(row.get("error", row))[:300]}, ms
    answer = row["result"]
    problem = L.question_problem(answer, L.identities(env, question, words, case["lexicon"]), env, question)
    if problem:
        return {"status": "unavailable", "error": problem}, ms
    return {k: answer[k] for k in ("status", "code", "sentence", "form", "ast", "rephrasings", "text")
            if k in answer}, ms


def reads_with(outcome: dict, formula) -> bool:
    """Whether a question's checked answer is `one` with exactly the sentence's formula."""
    return outcome["status"] == "one" and outcome.get("ast") == formula


def run_config(name: str, env, words, options, sentences: list[str]) -> dict:
    """Every record of one configuration: the sentences Lean reads with one formula, their questions and
    mutants, the moved-word sentences of each F2 question, and how many sentences each other outcome dropped."""
    readings = read_sentences(env, words, options, sentences)
    kept = [(s, r["ast"][0]) for s, r in zip(sentences, readings) if r["status"] == "one" and len(r["ast"]) == 1]
    dropped = Counter(r["status"] for r in readings if r["status"] != "one" or len(r["ast"]) != 1)
    questions, odd = [], []
    for sentence, formula in kept:
        built = [("f1", f1(sentence), None)]
        if (fronted := f2(sentence)) is not None:
            built.append(("f2", *fronted))
            odd += [(sentence, fronted[0], c, formula) for c in candidates(fronted[0]) if c != fronted[1]]
        for form, question, expected in built:
            for kind, text in [(form, question)] + [(f"{k}:{form}", t) for k, t in mutants(question, form)]:
                outcome, ms = ask(env, words, options, text)
                questions.append({"config": name, "sentence": sentence, "kind": kind, "question": text,
                                  "expected": expected, "ms": round(ms, 3), "same": reads_with(outcome, formula),
                                  "outcome": {k: v for k, v in outcome.items() if k != "ast"}})
    odd_read = read_sentences(env, words, options, [c for _, _, c, _ in odd])
    moved = [{"config": name, "sentence": s, "question": q, "moved": c, "status": r["status"],
              "same": r["status"] == "one" and r["ast"] == [formula]}
             for (s, q, c, formula), r in zip(odd, odd_read, strict=True)]
    return {"sentences": len(sentences), "one_formula": len(kept), "dropped": dict(dropped), "questions": questions,
            "moved": moved}


def transport_ms(env, words, options, repeat: int = 5) -> float:
    """The median milliseconds of a request Lean refuses before reading (`NotOneQuestion`): the relay and the
    environment and lexicon it carries, without a candidate."""
    return sorted(ask(env, words, options, "No question.")[1] for _ in range(repeat))[repeat // 2]


def limit_records(name: str, env, words, options, sentences: list[str], repeat: int = 3) -> list[dict]:
    """The 64-candidate question (timed `repeat` times) and the 65-candidate one beside it (Lean's limit)."""
    out = []
    for count, times in ((65, repeat), (66, 1)):
        question = long_question(sentences, count)
        if question is None:
            return []
        for _ in range(times):
            outcome, ms = ask(env, words, options, question)
            out.append({"config": name, "candidates": count - 1, "question": question, "status": outcome["status"],
                        "code": outcome.get("code"), "ms": round(ms, 3)})
    return out


def stream_of(task: tuple[int, int]) -> tuple[int, list[str], int]:
    """(target, its stream's texts, the stalls that cut it): a worker's task, the generator's stall alarm being
    per process."""
    index, count = task
    texts = [text for _, text, _ in E.streams(index, count, 0, [], claims=True)]
    return index, texts, E.STALLED.get(TARGETS[index][0], 0)


def slice_of(task: tuple[int, list[str]]) -> tuple[int, dict]:
    """A worker's task: `run_config` on some of a target's sentences."""
    index, sentences = task
    name, env, options, words = TARGETS[index]
    return index, run_config(name, env, words, options, sentences)


def limits_of(task: tuple[int, list[str]]) -> tuple[int, list[dict], float]:
    """A worker's task: a target's limit records and transport time."""
    index, sentences = task
    name, env, options, words = TARGETS[index]
    return index, limit_records(name, env, words, options, sentences), transport_ms(env, words, options)


def run(asked: dict[int, int], given: dict[int, list[str]], mapper=map) -> tuple[dict, list, list, list]:
    """(configs, questions, moved, limits) of the targets: `asked` maps a target to the stream size to draw,
    `given` to its sentences (a document's units). `mapper` runs the workers' tasks, in any order."""
    drawn, stalled, digests = dict(given), {}, {}
    for index, texts, stalls in mapper(stream_of, list(asked.items())):
        drawn[index], stalled[index] = texts, stalls
        digests[index] = hashlib.sha256("".join(f"{text}\n" for text in texts).encode()).hexdigest()
    unique = {index: list(dict.fromkeys(texts)) for index, texts in drawn.items()}
    slices = [(index, texts[k:k + SLICE]) for index, texts in sorted(unique.items())
              for k in range(0, len(texts), SLICE)]
    results = {index: [] for index in drawn}
    for count, (index, result) in enumerate(mapper(slice_of, slices), 1):
        results[index].append(result)
        print(f"slice {count} of {len(slices)}", file=sys.stderr, flush=True)
    limited = {index: rest for index, *rest in mapper(limits_of, sorted(drawn.items()))}
    configs, questions, moved, limits = {}, [], [], []
    for index in sorted(drawn):
        times = [q["ms"] for r in results[index] for q in r["questions"]]
        dropped = sum((Counter(r["dropped"]) for r in results[index]), Counter())
        configs[TARGETS[index][0]] = {
            "asked": asked.get(index, len(given.get(index, ()))), "drawn": len(drawn[index]),
            "stalled": stalled.get(index, 0), "stream_sha256": digests.get(index), "sentences": len(unique[index]),
            "one_formula": sum(r["one_formula"] for r in results[index]), "dropped": dict(sorted(dropped.items())),
            "questions": len(times), "moved": sum(len(r["moved"]) for r in results[index]), "p95_ms": p95(times),
            "max_ms": max(times, default=None), "transport_ms": limited[index][1]}
        questions += [q for r in results[index] for q in r["questions"]]
        moved += [m for r in results[index] for m in r["moved"]]
        limits += limited[index][0]
    return configs, questions, moved, limits


def coverage(configs: dict, per_config: int, per_usecase: int) -> dict:
    """What the run left out. `whole_streams` holds only when it left out nothing of the streams it draws: both sizes
    are the corpus's, every configuration ran, every stream was drawn to its size, each stream in the seal has the
    seal's digest, and every sentence has an answer. `other_sealed_streams` are the seal's streams it never draws."""
    generated = json.loads(SEAL.read_text())["generated"]
    sealed = {row["vocabulary"]: row["corpus_sha256"] for row in generated if row["stream"] == "english-surface"}
    short = {name: row["drawn"] for name, row in configs.items() if "skipped" not in row and row["drawn"] < row["asked"]}
    unavailable = {name: row["dropped"]["unavailable"] for name, row in configs.items()
                   if row.get("dropped", {}).get("unavailable")}
    skipped = sorted(name for name, row in configs.items() if "skipped" in row)
    unsealed = sorted(name for name, digest in sealed.items() if configs.get(name, {}).get("stream_sha256") != digest)
    return {"per_config": E.PER_CONFIG, "per_usecase": E.PER_USECASE, "short_streams": short,
            "unavailable_reads": unavailable, "skipped": skipped, "unsealed_streams": unsealed,
            "sealed_streams": len(sealed) - len(unsealed),
            "other_sealed_streams": {row["stream"]: row.get("texts", row.get("statements")) for row in generated
                                     if row["stream"] != "english-surface"},
            "whole_streams": (per_config, per_usecase) == (E.PER_CONFIG, E.PER_USECASE)
            and not (short or unavailable or skipped or unsealed)}


# ------------------------------------------------------------------ the measures (arithmetic only)

def p95(values: list[float]) -> float | None:
    """The nearest-rank 95th percentile."""
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1] if ordered else None


def share(part: int, whole: int) -> float | None:
    return round(part / whole, 6) if whole else None


def brief(q: dict) -> dict:
    """A listed question: its configuration, put-back sentence, head, length, hash and Lean's answer."""
    text = q["question"].encode()
    return {k: q[k] for k in ("config", "expected") if q.get(k) is not None} | {
        "question": q["question"][:LISTED_HEAD], "bytes": len(text), "sha256": hashlib.sha256(text).hexdigest()} | {
        k: q["outcome"][k] for k in ("status", "code", "sentence", "rephrasings", "error") if k in q["outcome"]}


def measures(questions: list[dict], moved: list[dict], limits: list[dict]) -> dict:
    f1s = [q for q in questions if q["kind"] == "f1"]
    f2s = [q for q in questions if q["kind"] == "f2"]
    f2_same = [q for q in f2s if q["same"]]
    many = [q for q in f2s if q["outcome"]["status"] == "many"]
    by_kind = {}
    for q in questions:
        if ":" in q["kind"]:
            row = by_kind.setdefault(q["kind"], Counter())
            row["questions"] += 1
            row["same"] += q["same"]
            row[":".join(filter(None, (q["outcome"]["status"], q["outcome"].get("code"))))] += 1
    corpus_ms = [q["ms"] for q in questions]
    by_form = {kind: p95([q["ms"] for q in questions if (q["kind"] if ":" not in q["kind"] else "mutant") == kind])
               for kind in ("f1", "f2", "mutant")}
    limit_ms = [r["ms"] for r in limits if r["candidates"] == 64]
    return {
        "f1": {"questions": len(f1s), "same": sum(q["same"] for q in f1s),
               "share": share(sum(q["same"] for q in f1s), len(f1s)), "misses": [brief(q) for q in f1s if not q["same"]]},
        "f2": {"questions": len(f2s), "same": len(f2_same), "many": len(many),
               "share": share(len(f2_same) + len(many), len(f2s)),
               "other_sentence": [brief(q) for q in f2_same if q["outcome"]["sentence"] != q["expected"]],
               "many_causes": [brief(q) for q in many],
               "misses": [brief(q) for q in f2s if not q["same"] and q["outcome"]["status"] != "many"]},
        "odd": {"moved_sentences": len(moved), "f2_questions": len({(m["config"], m["question"]) for m in moved}),
                "accepted": sum(m["status"] == "one" for m in moved),
                "accepted_same": sum(m["same"] for m in moved),
                "acceptances": [m for m in moved if m["status"] == "one"]},
        "mutants": {kind: dict(sorted(row.items())) for kind, row in sorted(by_kind.items())},
        "latency": {"questions": len(corpus_ms), "p95_ms": p95(corpus_ms), "max_ms": max(corpus_ms, default=None),
                    "p95_ms_by_kind": by_form, "budget_ms": BUDGET_MS, "met": p95(corpus_ms) is not None and p95(corpus_ms) <= BUDGET_MS,
                    "q64_runs": len(limit_ms), "q64_max_ms": max(limit_ms, default=None), "q64_budget_ms": BUDGET_64_MS,
                    "q64_met": bool(limit_ms) and max(limit_ms) <= BUDGET_64_MS},
        "limits": limits,
    }


# ------------------------------------------------------------------ the corpus

def document_units(raw: bytes) -> tuple[dict, list[tuple[dict, str, bool]]]:
    """(front matter, (unit, text, whether the text is a fence) per unit with a span) of a `.ve.md` document, read as
    the document loader reads it: `_parts`' units, spans over the source without its fences, and as a unit's text the
    English `ve` fence it names (`_english_fences`), the sentence Lean reads, else its span, which is source prose."""
    from ve.document.source import _english_fences, _parts, _split
    meta, source, fences = _split(raw)
    english = dict(_english_fences(meta.get("units", []), fences))
    return meta, [(u, english[u["id"]].strip(), True) if u.get("id") in english else
                  (u, source[u["span"][0]:u["span"][1]].decode().strip(), False)
                  for u, _ in _parts(meta.get("units", [])) if "span" in u]


def documents() -> list[tuple[str, dict, list[str]]]:
    """(path, environment data, unit texts ending with `.`) of every use-case `.ve.md` document outside the
    pilot runs (`run-*`)."""
    out = []
    for path in sorted(ROOT.glob("usecases/**/*.ve.md")):
        if any(part.startswith("run-") for part in path.parts):
            continue
        data, units = document_units(path.read_bytes())
        out.append((str(path.relative_to(ROOT)), data["environment"], [t for _, t, _ in units if t.endswith(".")]))
    return out


# ------------------------------------------------------------------ q1-3b: every fronting, the other streams, norms

OUTPUT_B = ROOT / "docs/question-answering/q1-3b/evidence/question-reverse-b.json"
FORMAT_B = "ve.question-reverse-b@1"
# The streams of a q1-3b run, each with whether its F1 questions are asked (q1-3 asked them for the first three).
STREAMS = {"english-surface": False, "usecase-surface": False, "usecase-documents": False, "random-earley": True,
           "english-mixed": True, "natural-view": True, "norm-documents": True}
PLANS: dict = {}  # target index -> its stream; filled with TARGETS before the workers fork
EXAMPLES = 10


def closeness(cands: list[str], reads: list[dict], text: str, put: str | None) -> dict:
    """Open point 10.2's record of a question with no reading: which candidate Lean's text names as the closest
    sentence tried, how many candidates share the right-most diagnosis start (each candidate's own `english.read`
    span, in bytes), whether Lean's choice is the leftmost of them (`consistent`; Python checks, Lean chose), and
    where the moved word and the reader's sentence (`put`, the source order) are."""
    named = [i for i, c in enumerate(cands) if f'Closest sentence tried: "{c}". ' in text]
    starts = [len(c[:r["span"][0]].encode()) if r["status"] == "none" and "span" in r else None
              for c, r in zip(cands, reads, strict=True)]
    best = max((s for s in starts if s is not None), default=None)
    ties = [i for i, s in enumerate(starts) if s is not None and s == best]
    at = named[0] if named else None
    return {"candidates": len(cands), "named": "Closest sentence tried: " in text, "closest": at, "ties": len(ties),
            "consistent": at is None or (bool(ties) and at == ties[0]), "reader": cands.index(put) if put in cands else None}


def run_config_b(name: str, env, words, options, sentences: list[str], asks_f1: bool, every: bool) -> dict:
    """q1-3b's records of one configuration: for each sentence Lean reads with one formula (with `every`, each
    sentence), its F1 question when `asks_f1`, every fronting of `frontings`, each answer and, for an answer with no
    reading, its `closeness` over Lean's reads of its candidates; and each sentence's own `english.read` outcome."""
    readings = read_sentences(env, words, options, sentences)
    questions = []
    for sentence, r in zip(sentences, readings, strict=True):
        formula = r["ast"][0] if r["status"] == "one" and len(r["ast"]) == 1 else None
        if formula is None and not every:
            continue
        built = [("f1", None, f1(sentence))] if asks_f1 else []
        for form, at, question in built + [("f2", k, q) for k, q in frontings(sentence)]:
            outcome, ms = ask(env, words, options, question)
            record = {"config": name, "sentence": sentence, "read": formula is not None, "kind": form, "at": at,
                      "question": question, "expected": put_back(sentence) if form == "f2" else None,
                      "ms": round(ms, 3), "same": formula is not None and reads_with(outcome, formula),
                      "other": formula is not None and outcome["status"] == "one" and outcome["ast"] != formula,
                      "outcome": {k: v for k, v in outcome.items() if k != "ast"}}
            if outcome["status"] == "none":
                cands = [question[len(FRAME):-1] + "."] if form == "f1" else candidates(question)
                record["closest"] = closeness(cands, read_sentences(env, words, options, cands),
                                              outcome["text"], record["expected"])
            questions.append(record)
    return {"sentences": len(sentences), "one_formula": sum(r["status"] == "one" and len(r["ast"]) == 1 for r in readings),
            "unavailable": sum(r["status"] == "unavailable" for r in readings),
            "reads": {s: {"status": r["status"], "code": r.get("code"), "one": r["status"] == "one" and len(r["ast"]) == 1}
                      for s, r in zip(sentences, readings, strict=True)},
            "questions": questions}


def earley_stream(index: int, sealed: list[str], count: int = 250) -> tuple[list[str], dict]:
    """The random Earley texts of round-trip configuration `index` and its documents of five, drawn as
    `english_surface.audit` draws them (its seed, depths 6 to 9, no formula twice, no text of the sealed stream),
    with the digests the seal records; a document whose text is not its five sentences is counted."""
    from conformance.english_surface import SEED, formula_depth, random_formula
    from ve import ast
    from ve.printer import render
    _, env, options, _ = TARGETS[index]
    rng, seen, texts, formulas, known = random.Random(SEED + 100_000 + index), set(), [], [], {f"{t}\n" for t in sealed}
    while len(texts) < count:
        formula = random_formula(rng, env, rng.randrange(6, 10))
        if not 6 <= formula_depth(formula) <= 9 or formula in seen:
            continue
        text = render(ast.Document((formula,)), env, "ve_english", **options)
        if text in known:
            continue
        seen.add(formula)
        texts.append(text)
        formulas.append(formula)
    documents = [render(ast.Document(tuple(formulas[k:k + 5])), env, "ve_english", **options)
                 for k in range(0, len(formulas) - 1, 5)]
    digest = lambda xs: hashlib.sha256("".join(xs).encode()).hexdigest()  # noqa: E731
    return [t.rstrip("\n") for t in texts], {
        "random_earley_sha256": digest(texts), "documents": len(documents), "document_sha256": digest(documents),
        "documents_not_their_sentences": sum(d != "".join(texts[5 * k:5 * k + 5]) for k, d in enumerate(documents))}


def stream_b(task: tuple[int, int]) -> tuple[int, list[str], int, tuple | None]:
    """A worker's task: `stream_of`, and for a round-trip configuration its `earley_stream`."""
    index, texts, stalls = stream_of(task)
    return index, texts, stalls, earley_stream(index, texts) if E.round_trip(TARGETS[index][0]) else None


def mixed_texts(only=None) -> tuple[dict, dict]:
    """({configuration: (env, options, its one-sentence texts)}, {configuration: (digest, texts, paragraphs whose
    text is not their sentences)}): `english_mixed.mixed`'s own draw, its texts kept and its parsing left out (each
    text's parse is its rendered document; `mixed` digests the texts it renders)."""
    from unittest import mock
    from conformance import english_mixed as M
    configs, seen, last = M.all_configurations(), {}, []

    def render(document, env, *args, **kwargs):
        text = M_render(document, env, *args, **kwargs)
        seen.setdefault(id(env), []).append((document, text))
        last[:] = [document]
        return text
    M_render = M.render
    with mock.patch.object(M, "all_configurations", lambda: configs), mock.patch.object(M, "render", render), \
            mock.patch.object(M, "parse_english", lambda *_a, **_k: last[0]):
        report = M.mixed(only=only)
    out, checks = {}, {}
    for (name, env, options), row in zip([c for k, c in enumerate(configs) if only is None or k in only],
                                         report["vocabularies"], strict=True):
        drawn = seen.get(id(env), [])
        single = {d.formulas[0]: t for d, t in drawn if len(d.formulas) == 1}
        out[name] = (env, options, [t.rstrip("\n") for t in single.values()])
        checks[name] = (row["corpus_sha256"], len(drawn),
                        sum(t != "".join(single.get(f, "") for f in d.formulas) for d, t in drawn if len(d.formulas) > 1))
    return out, checks


def natural_texts(audit=None) -> tuple[dict, int]:
    """({corpus: (env, options, statement sentences)}, statements): `natural_surface.audit`'s own statements, each
    `render_natural_sentence`'s text with its period, recorded where `_measure` renders them (its checks refused),
    the audit stopped at its prose example (`parse_english_argument`), after the last statement."""
    from unittest import mock
    from conformance import natural_surface as N
    out, current = {}, {}
    measure0, render0 = N._measure, N.render_natural_sentence

    def measure(name, formulas, env, *, options=None, **kwargs):
        current.update(name=name, env=env, options=options or {})
        out.setdefault(name, (env, options or {}, []))
        return measure0(name, formulas, env, options=options, **kwargs)

    def render(formula, env, **options):
        result = render0(formula, env, **options)
        out[current["name"]][2].append(result.text + ".")
        return result

    class Done(Exception):
        """The audit's statements are all rendered: its prose example, which needs no statement, is not run."""

    def unchecked(*_args, **_kwargs):
        raise ValueError("not checked here")

    def done(*_args, **_kwargs):
        raise Done
    with mock.patch.object(N, "_measure", measure), mock.patch.object(N, "render_natural_sentence", render), \
            mock.patch.object(N, "require_unique_derivation", unchecked), \
            mock.patch.object(N, "parse_english_argument", done):
        try:
            (audit or N.audit)()
        except Done:
            pass
    return out, sum(len(texts) for _, _, texts in out.values())


def norm_documents() -> list[tuple[str, str, str]]:
    """(name, sha256, text) of the latest version of each norm part document: the UDHR pilot's
    `translation-part<n>` and the constitution pilot's readings parts, as AR-17's `pilot_parts.selected` picks them
    (not whole documents, L70), without the evidence variants; then `udhr-part07` of the question-answering use case."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("pilot_parts", ROOT / "docs/arch/AR-17/pilot_parts.py")
    parts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parts)
    latest = {}
    for name, blob, text in sorted(parts.documents()):
        branch, _, path = name.partition(":")
        if "/evidence/" not in path and not path.rsplit("/", 1)[-1].startswith("udhr-part"):  # main's copy is added
            latest[(branch.split("-")[0], path.rsplit("/", 1)[-1])] = (name, blob, bytes(text).decode())
    own = ROOT / "usecases/question-answering/udhr-part07.ve.md"
    raw = own.read_bytes()
    return sorted(latest.values()) + [(str(own.relative_to(ROOT)), hashlib.sha256(raw).hexdigest(), raw.decode())]


def one_sentence(text: str) -> bool:
    return text.endswith(".") and "\n" not in text


def norm_units(text: str) -> tuple[dict, list[tuple[str, str, str | None, bool]]]:
    """(environment data, (kind, content kind, text, whether Lean is asked to read it) per unit with a span) of a
    `.ve.md` document: its `document_units`, a fence whatever its lines (a list is one sentence) and a span when it
    is `one_sentence`."""
    data, units = document_units(text.encode())
    return data["environment"], [
        (u.get("kind", "-") if isinstance(u.get("kind", "-"), str) else json.dumps(u["kind"], separators=(",", ":")),
         next(iter(u["content"])) if isinstance(u.get("content"), dict) else None,
         t, t.endswith(".") if fenced else one_sentence(t)) for u, t, fenced in units]


def why(text: str, reads: dict[str, dict]) -> str:
    """Whether a unit's text can be a question's source: `reached` only for a sentence that `english.read` (its
    outcome in `reads`, which holds every text Lean was asked to read) reads with one formula; else why not (not
    one sentence, or Lean's outcome and code)."""
    r = reads.get(text)
    if r is None:
        return "not one sentence"
    return "reached" if r["one"] else ":".join(filter(None, ("english.read", r["status"], r["code"])))


def unit_reach(units: list[tuple[str, str, str | None, bool]], reads: dict[str, dict]) -> tuple[Counter, dict]:
    """(units per (kind, content, `why`), two example texts of each key)."""
    counts, examples = Counter(), {}
    for kind, content, text, _ in units:
        key = (kind, content or "-", why(text, reads))
        counts[key] += 1
        if len(examples.setdefault("/".join(key), [])) < 2:
            examples["/".join(key)].append(text[:LISTED_HEAD])
    return counts, examples


def slice_b(task: tuple[int, list[str]]) -> tuple[int, dict]:
    """A worker's task: `run_config_b` on some of a target's sentences."""
    index, sentences = task
    name, env, options, words = TARGETS[index]
    stream = PLANS[index]
    return index, run_config_b(name, env, words, options, sentences, STREAMS[stream], stream == "norm-documents")


def run_b(asked: dict[int, int], given: dict[int, list[str]], earley: dict[int, int],
          mapper=map) -> tuple[dict, list, dict]:
    """(configs, questions, each norm document's reads by sentence) of a q1-3b run: `asked` maps a target to the
    stream size to draw, `given` to its sentences, and `earley` a round-trip target to the target of its random
    Earley texts."""
    drawn, extra = dict(given), {}
    for index, texts, stalls, more in mapper(stream_b, list(asked.items())):
        drawn[index] = texts
        extra[index] = {"stalled": stalls,
                        "stream_sha256": hashlib.sha256("".join(f"{t}\n" for t in texts).encode()).hexdigest()}
        if more is not None:
            drawn[earley[index]], extra[earley[index]] = more[0], more[1]
    unique = {index: list(dict.fromkeys(texts)) for index, texts in drawn.items()}
    slices = [(index, texts[k:k + SLICE]) for index, texts in sorted(unique.items())
              for k in range(0, len(texts), SLICE)]
    results = {index: [] for index in drawn}
    for count, (index, result) in enumerate(mapper(slice_b, slices), 1):
        results[index].append(result)
        print(f"slice {count} of {len(slices)}", file=sys.stderr, flush=True)
    configs, questions, reads = {}, [], {}
    for index in sorted(drawn):
        mine = [q for r in results[index] for q in r["questions"]]
        configs[TARGETS[index][0]] = {
            "stream": PLANS[index], "asked": asked.get(index, len(given.get(index, ()))), "drawn": len(drawn[index]),
            "sentences": len(unique[index]), "one_formula": sum(r["one_formula"] for r in results[index]),
            "unavailable": sum(r["unavailable"] for r in results[index]),
            "questions": len(mine), "p95_ms": p95([q["ms"] for q in mine]),
            "max_ms": max((q["ms"] for q in mine), default=None), **extra.get(index, {})}
        if PLANS[index] == "norm-documents":
            reads[TARGETS[index][0]] = {s: x for r in results[index] for s, x in r["reads"].items()}
        questions += mine
    return configs, questions, reads


def per_stream(configs: dict, questions: list[dict]) -> dict:
    """Per stream of `STREAMS`, every one listed: its configurations, sentences, one-formula sentences, and its
    questions of each form with how many read with the sentence's formula, are `many`, read another formula or
    have no answer."""
    out = {stream: Counter() for stream in STREAMS}
    for row in configs.values():
        if "stream" in row:
            for key in ("sentences", "one_formula", "questions"):
                out[row["stream"]][key] += row[key]
            out[row["stream"]]["configs"] += 1
    for q in questions:
        row = out[configs[q["config"]]["stream"]]
        for key, counted in (("", True), ("_same", q["same"]), ("_many", q["outcome"]["status"] == "many"),
                             ("_other", q["other"]), ("_unavailable", q["outcome"]["status"] == "unavailable")):
            row[q["kind"] + key] += counted
    return {stream: dict(sorted(row.items())) for stream, row in out.items()}


def f1_measure(questions: list[dict]) -> dict:
    """The F1 questions of the sentences with one formula: how many read with it, and the rest (200 listed)."""
    f1s = [q for q in questions if q["kind"] == "f1" and q["read"]]
    return {"questions": len(f1s), "same": sum(q["same"] for q in f1s),
            "misses": [brief(q) for q in f1s if not q["same"]][:200]}


def fronting_measure(questions: list[dict]) -> dict:
    """Plan 4.9's measure on every fronting of a sentence with one formula: each answer's outcome; per sentence,
    whether one of its frontings reads with the formula or is `many` (the share), split by whether q1-3's `f2`
    builds the sentence's question (no clause in the subject), and again without the sentences whose every fronting
    Lean refuses at its limits (`budget`); each `many` and each other formula, listed."""
    f2s = [q for q in questions if q["kind"] == "f2" and q["read"]]
    groups = {}
    for q in f2s:
        groups.setdefault((q["config"], q["sentence"]), []).append(q)
    split = {"q1-3 subject": Counter(), "other subject": Counter()}
    for (_, sentence), qs in groups.items():
        row = split["q1-3 subject" if f2(sentence) is not None else "other subject"]
        row["sentences"] += 1
        row["reached"] += any(q["same"] or q["outcome"]["status"] == "many" for q in qs)
        row["several_same"] += sum(q["same"] for q in qs) > 1
        row["limited"] += all(q["outcome"]["status"] == "budget" for q in qs)
        if f2(sentence) is not None:
            row["q1_3_question_same"] += any(q["same"] for q in qs if q["question"] == f2(sentence)[0])
    sentences = sum(row["sentences"] for row in split.values())
    reached = sum(row["reached"] for row in split.values())
    limited = sum(row["limited"] for row in split.values())
    return {"frontings": len(f2s), "sentences": sentences, "reached": reached, "share": share(reached, sentences),
            "limited": limited, "share_within_limits": share(reached, sentences - limited),
            "outcomes": dict(sorted(Counter(":".join(filter(None, (q["outcome"]["status"], q["outcome"].get("code"))))
                                            for q in f2s).items())),
            "by_subject": {k: dict(sorted(v.items())) for k, v in split.items()},
            "many_causes": [brief(q) for q in f2s if q["outcome"]["status"] == "many"],
            "other_formula": [brief(q) | {"lean_sentence": q["outcome"]["sentence"]} for q in f2s if q["other"]]}


def closest_measure(questions: list[dict]) -> dict:
    """Open point 10.2 over every question with no reading: how often Lean names a closest sentence, how often it
    is a candidate, the leftmost of tied candidates or the only one, where its moved word sits (second: the first
    gap) and whether it is the reader's sentence (the put-back); each share over the F2 questions whose closest is
    named among more than one candidate, with `EXAMPLES` of the moved-word-second ties, and how many of the questions
    are distinct texts (a text repeated in several documents is a question of each)."""
    nones = [q for q in questions if q["outcome"]["status"] == "none"]
    named = [q for q in nones if q["closest"]["named"]]
    found = [q for q in named if q["closest"]["closest"] is not None]
    pool = [q for q in found if q["kind"] == "f2" and q["closest"]["candidates"] > 1]
    c = lambda q: q["closest"]  # noqa: E731
    tied = [q for q in pool if c(q)["ties"] > 1]
    second = [q for q in pool if c(q)["closest"] == 0]
    known = [q for q in pool if c(q)["reader"] is not None]
    other = [q for q in known if c(q)["closest"] != c(q)["reader"]]
    examples = [brief(q) | {"closest": candidates(q["question"])[0], "ties": c(q)["ties"]} for q in tied
                if c(q)["closest"] == 0 and c(q)["reader"] not in (None, 0)][:EXAMPLES]
    return {"no_reading": len(nones), "distinct_no_reading": len({q["question"] for q in nones}),
            "distinct_measured": len({q["question"] for q in pool}),
            "by_form": dict(Counter(q["kind"] for q in nones)), "named": len(named),
            "not_named": len(nones) - len(named), "named_unmatched": [brief(q) for q in named if q not in found][:20],
            "one_candidate": sum(c(q)["candidates"] == 1 for q in found), "measured": len(pool),
            "tied": len(tied), "leftmost_tie": sum(c(q)["consistent"] for q in tied),
            "unique": sum(c(q)["ties"] == 1 for q in pool), "moved_second": len(second),
            "moved_second_tied": sum(q in tied for q in second), "reader_known": len(known),
            "not_the_readers": len(other), "share_tied": share(len(tied), len(pool)),
            "share_moved_second": share(len(second), len(pool)), "share_not_the_readers": share(len(other), len(known)),
            "inconsistent": [brief(q) | {"ties": c(q)["ties"]} for q in found if not c(q)["consistent"]][:20],
            "examples": examples}


def norm_measure(norms: dict, configs: dict, questions: list[dict]) -> dict:
    """The norm part documents: each one's reach, the units per `why` over all of them, the units it reached, the
    stream's question counts, and how many of its sentences and frontings with an answer are distinct texts (the
    constitution parts repeat one source)."""
    mine = [q for q in questions if configs[q["config"]]["stream"] == "norm-documents"
            and q["outcome"]["status"] != "unavailable"]
    by_why = Counter()
    for row in norms.values():
        for *key, count in row["reach"]:
            by_why[key[2]] += count
    return {"documents": norms, "by_why": dict(sorted(by_why.items())), "reached": by_why["reached"],
            "questions": per_stream(configs, questions)["norm-documents"],
            "distinct_answered_sentences": len({q["sentence"] for q in mine}),
            "distinct_answered_frontings": len({q["question"] for q in mine if q["kind"] == "f2"}),
            "answered_frontings": sum(q["kind"] == "f2" for q in mine)}


# The `coverage_b` keys that each leave a run partial when they are not empty or zero.
LEFT_OUT = ("unsealed_streams", "unsealed_random_earley", "unsealed_documents", "mixed_unmatched",
            "documents_not_their_sentences", "mixed_paragraphs_not_their_sentences", "short_streams", "skipped",
            "unavailable_reads")


def coverage_b(configs: dict, mixed_checks: dict, natural_statements: int, per_config: int, per_usecase: int) -> dict:
    """What a q1-3b run left out: each drawn stream against the seal's digest (the sealed streams, the random
    Earley texts and documents), `english-mixed` against its report's digest per configuration and the seal's
    size, `natural-view` against the seal's statement count, and the sentences with no answer; `whole_streams` holds
    only when every one matches and every sentence has an answer."""
    seal = json.loads(SEAL.read_text())["generated"]
    surface = {row["vocabulary"]: row for row in seal if row["stream"] == "english-surface"}
    sizes = {row["stream"]: row.get("texts", row.get("statements")) for row in seal if row["stream"] != "english-surface"}
    mixed = {row["vocabulary"]: row["corpus_sha256"]
             for row in json.loads((ROOT / "conformance/english-mixed-report.json").read_text())["vocabularies"]}
    rows = {(row["stream"], name.split(":", 1)[-1]): row for name, row in configs.items() if "stream" in row}
    diff = lambda stream, key, want: sorted(  # noqa: E731
        v for v, r in surface.items() if rows.get((stream, v), {}).get(key) != r[want])
    out = {"unsealed_streams": diff("english-surface", "stream_sha256", "corpus_sha256"),
           "unsealed_random_earley": diff("random-earley", "random_earley_sha256", "random_earley_corpus_sha256"),
           "unsealed_documents": diff("random-earley", "document_sha256", "document_corpus_sha256"),
           "documents_not_their_sentences": sum(r.get("documents_not_their_sentences", 0) for r in rows.values()),
           "mixed_unmatched": sorted(v for v, d in mixed.items() if mixed_checks.get(v, (None,))[0] != d),
           "mixed_texts": sum(c[1] for c in mixed_checks.values()),
           "mixed_paragraphs_not_their_sentences": sum(c[2] for c in mixed_checks.values()),
           "natural_statements": natural_statements, "seal_sizes": sizes,
           "short_streams": {n: r["drawn"] for n, r in configs.items() if "asked" in r and r["drawn"] < r["asked"]},
           "skipped": sorted(n for n, r in configs.items() if "skipped" in r),
           "unavailable_reads": {n: r["unavailable"] for n, r in configs.items() if r.get("unavailable")}}
    out["whole_streams"] = (per_config, per_usecase) == (E.PER_CONFIG, E.PER_USECASE) and not any(
        out[k] for k in LEFT_OUT) and (out["mixed_texts"], natural_statements) == \
        (sizes.get("english-mixed"), sizes.get("natural-view"))
    return out


def main_b(args) -> int:
    """The q1-3b run: every target's sentences, questions and measures, written to `args.output`."""
    from ve.english import EnglishVocabulary
    from ve.environment import Environment
    E._setup()
    warnings.simplefilter("ignore")
    E.CONFIGS.extend(E.configurations())
    load = [round(x, 1) for x in os.getloadavg()]
    TARGETS.extend(E.CONFIGS)
    configs, asked, given, earley, units = {}, {}, {}, {}, {}

    def add(name, env, options, stream, texts=None, words=None):
        try:
            words = words or EnglishVocabulary(env, _defer_overlay_refusals=True, **options)
        except Exception as exc:  # noqa: BLE001 - a refused vocabulary is recorded, as q1-3 records it
            configs[name] = {"stream": stream, "skipped": f"{type(exc).__name__}: {exc}"[:200], "sentences": 0,
                             "one_formula": 0, "questions": 0}
            return None
        TARGETS.append((name, env, options, words))
        PLANS[len(TARGETS) - 1] = stream
        if texts is not None:
            given[len(TARGETS) - 1] = texts
        return len(TARGETS) - 1
    for index, (name, env, options, words) in enumerate(E.CONFIGS):
        stream = "english-surface" if E.round_trip(name) else "usecase-surface"
        if isinstance(words, Exception):
            configs[name] = {"stream": stream, "skipped": f"{type(words).__name__}: {words}"[:200], "sentences": 0,
                             "one_formula": 0, "questions": 0}
            continue
        PLANS[index], asked[index] = stream, args.per_config if E.round_trip(name) else args.per_usecase
        if E.round_trip(name):
            earley[index] = add(f"random-earley:{name}", env, options, "random-earley", words=words)
    for path, data, texts in documents():
        add(path, Environment(data), {}, "usecase-documents", texts)
    mixed, mixed_checks = mixed_texts()
    for name, (env, options, texts) in mixed.items():
        add(f"english-mixed:{name}", env, options, "english-mixed", texts)
    natural, statements = natural_texts()
    for name, (env, options, texts) in natural.items():
        add(f"natural-view:{name}", env, options, "natural-view", texts)
    for name, blob, text in norm_documents():
        data, found = norm_units(text)
        if add(f"norm-documents:{name}", Environment(data), {}, "norm-documents",
               [t for _, _, t, asked_to_read in found if asked_to_read]) is not None:
            units[f"norm-documents:{name}"] = (blob, found)
    started = time.time()
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        ran, questions, reads = run_b(asked, given, earley, pool.imap_unordered)
    configs.update(ran)
    norms = {}
    for name, (blob, found) in units.items():
        reach, examples = unit_reach(found, reads.get(name, {}))
        norms[name] = {"sha256": blob, "units": len(found), "reach": [[*k, n] for k, n in sorted(reach.items())],
                       "examples": examples}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    by_kind = {kind: p95([q["ms"] for q in questions if q["kind"] == kind]) for kind in ("f1", "f2")}
    report = {"format": FORMAT_B, "commit": commit, "per_config": args.per_config, "per_usecase": args.per_usecase,
              "workers": args.workers, "seconds": round(time.time() - started, 1),
              "load_average": {"start": load, "end": [round(x, 1) for x in os.getloadavg()], "cpus": os.cpu_count()},
              "coverage": coverage_b(configs, mixed_checks, statements, args.per_config, args.per_usecase),
              "streams": per_stream(configs, questions), "configs": configs,
              "f1": f1_measure(questions), "f2": fronting_measure(questions), "closest": closest_measure(questions),
              "norm": norm_measure(norms, configs, questions),
              "latency": {"recorded_only": "q1-3c", "questions": len(questions), "p95_ms": p95([q["ms"] for q in questions]),
                          "max_ms": max((q["ms"] for q in questions), default=None), "p95_ms_by_kind": by_kind}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({k: report[k] for k in ("coverage", "streams")}, indent=1)[:4000])
    return 0


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--per-config", type=int, default=E.PER_CONFIG, help="texts per round-trip configuration")
    parser.add_argument("--per-usecase", type=int, default=E.PER_USECASE, help="texts per use-case environment")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--part", choices=("a", "b"), default="a", help="q1-3's run (a) or q1-3b's (b)")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    args.output = args.output or (OUTPUT if args.part == "a" else OUTPUT_B)
    return args


def main(argv=None) -> int:
    args = arguments(argv)
    if args.part == "b":
        return main_b(args)
    from ve.english import EnglishVocabulary
    from ve.environment import Environment
    E._setup()
    warnings.simplefilter("ignore")
    E.CONFIGS.extend(E.configurations())
    load = [round(x, 1) for x in os.getloadavg()]
    TARGETS.extend(E.CONFIGS)
    configs = {name: {"skipped": f"{type(words).__name__}: {words}"[:200]}
               for name, _, _, words in TARGETS if isinstance(words, Exception)}
    asked = {index: args.per_config if E.round_trip(target[0]) else args.per_usecase
             for index, target in enumerate(TARGETS) if not isinstance(target[3], Exception)}
    given = {}
    for path, data, texts in documents():
        env = Environment(data)
        given[len(TARGETS)] = texts
        TARGETS.append((path, env, {}, EnglishVocabulary(env, _defer_overlay_refusals=True)))
    started = time.time()
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        ran, questions, moved, limits = run(asked, given, pool.imap_unordered)
    configs.update(ran)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    report = {"format": FORMAT, "commit": commit, "per_config": args.per_config, "per_usecase": args.per_usecase,
              "workers": args.workers, "seconds": round(time.time() - started, 1),
              "coverage": coverage(configs, args.per_config, args.per_usecase),
              "load_average": {"start": load, "end": [round(x, 1) for x in os.getloadavg()], "cpus": os.cpu_count()},
              "configs": configs, **measures(questions, moved, limits)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({k: {x: y for x, y in v.items() if not isinstance(y, (list, dict))}
                      for k, v in report.items() if isinstance(v, dict) and k not in ("configs", "mutants")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
