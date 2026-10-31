"""Q1.3: the reverse question corpus, read by Lean's question reader (docs/spec/question-answering-PLAN.md Q1.3).

    uv run python -m conformance.question_reverse [--per-config N] [--per-usecase N] [--workers N] [--output PATH]

The defaults are the whole corpus (`english_lean_e2_evidence.PER_CONFIG`, `PER_USECASE`); the saved `coverage` says
what a run left out, compares each round-trip stream with its digest in the seal, and names the seal's other streams,
which this script does not draw. For every corpus sentence Lean reads with one formula (the sealed stream of every corpus configuration of
`conformance.english_lean_e2_evidence`, and the units of every use-case `.ve.md` document under its own
environment), the script builds the F1 question, the F2 question where the sentence begins with a quantified or
named subject followed by *is*, *must* or *may* (plan 3.2), and spacing and capitalisation mutants of both. Each
question is sent alone to `english.question` and its answer is checked by the relay's `question_problem`; each
sentence with its fronted word put back at another word gap (the odd-English measure) is read by `english.read`.
Lean decides every outcome; this script only builds texts, compares formulas and counts. A worker takes one slice of
one configuration at a time, so the measured times carry the host's load and each other's (`workers`,
`load_average`). The result is
`docs/question-answering/q1-3/evidence/question-reverse.json`, cited by `docs/spec/question-answering-q1-report.md`.
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
                       {"status": row["result"]["status"], "ast": row["result"].get("ast")})
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

    def brief(q):
        text = q["question"].encode()
        return {k: q[k] for k in ("config", "expected") if q.get(k) is not None} | {
            "question": q["question"][:LISTED_HEAD], "bytes": len(text), "sha256": hashlib.sha256(text).hexdigest()} | {
            k: q["outcome"][k] for k in ("status", "code", "sentence", "rephrasings", "error") if k in q["outcome"]}
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

def documents() -> list[tuple[str, dict, list[str]]]:
    """(path, environment data, unit texts ending with `.`) of every use-case `.ve.md` document outside the
    pilot runs (`run-*`)."""
    out = []
    for path in sorted(ROOT.glob("usecases/**/*.ve.md")):
        if any(part.startswith("run-") for part in path.parts):
            continue
        _, front, body = path.read_text().split("---\n", 2)
        data, raw = json.loads(front), body.encode()
        texts = [raw[u["span"][0]:u["span"][1]].decode().strip() for u in data.get("units", []) if "span" in u]
        out.append((str(path.relative_to(ROOT)), data["environment"], [t for t in texts if t.endswith(".")]))
    return out


def arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--per-config", type=int, default=E.PER_CONFIG, help="texts per round-trip configuration")
    parser.add_argument("--per-usecase", type=int, default=E.PER_USECASE, help="texts per use-case environment")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = arguments(argv)
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
