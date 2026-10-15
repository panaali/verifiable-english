"""The A/B of Q2.4 (docs/spec/question-answering-PLAN.md, Q2.4): Lean's situation and point wording (`VE.Words`,
through `ve/words.py`) against the Python producers it replaced, byte for byte, on the readings, norm-defaults and
pilot corpora.

    uv run python tools/words_ab.py corpus --out DIR [--trees N]     # the norm-defaults and pilot corpora
    VE_WORDS_AB=DIR uv run python -m pytest -p tools.words_ab ...    # every call a test makes
    uv run python tools/words_ab.py summary DIR... [--write]          # the saved evidence

`install()` wraps every call site whose English Q2.4 moved (the readings routes' shown situations, filled gaps and
pair premises; the norm-defaults status, gap, conflict and completion sentences and the legend): each call returns
the current (Lean-worded) text and, beside it, computes the text the pre-Q2.4 producer gives for the same inputs
(`conformance/frozen_words.py`, the producers at `REVISION` from Git history) and records whether the two are the
same. A difference is a wording delta of DELTA.md (plan Q2.4: the target is byte-identical English); the saved
evidence (`docs/spec/question-answering-q2/evidence/words-ab.json`) lists each one. The records are JSON lines,
one per call, appended to `<pid>.jsonl` in the directory `VE_WORDS_AB` (or the corpus run's `--out`).

The corpora:
* readings: every call the readings suites make (`tests/test_readings_*.py`, `tests/test_stage2_readings.py`) and
  every readings document of the pilot corpus;
* norm-defaults: every call the norm-defaults suites make (`tests/test_norm_defaults*.py`) and the generated corpus
  of `conformance/norm_defaults_differential.py` (seeds 0 to `--trees` - 1, each tree's situation: the status
  sentence of every point Lean decides, the latent conflict sentence of Lean's CONFLICT witness, the gap sentence of
  every reachable report line, the completion question, the legend);
* pilots: every `.ve.md` document of every `pilot/*` branch, once per content (`tools/lean_first_diff.py`), through
  `check_document`, which words the readings report of a document with open reading sets.
"""
from __future__ import annotations

import argparse
import functools
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
EVIDENCE = ROOT / "docs/spec/question-answering-q2/evidence/words-ab.json"
_sink: list = []


def _text(value):
    try:
        return json.loads(json.dumps(value, default=str))
    except (TypeError, ValueError):
        return repr(value)


def _record(site, new, old, case):
    row = {"site": site, "same": new == old}
    if new != old:
        row.update(new=_text(new), old=_text(old), case=_text(case))
    directory = os.environ.get("VE_WORDS_AB")
    if directory:
        with open(Path(directory) / f"{os.getpid()}.jsonl", "a", encoding="utf-8") as out:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    _sink.append(row)


def _compare(site, current, frozen, shape=lambda value: value, case=lambda *args: args[1:]):
    """`current` wrapped: its result is returned; `frozen` on the same arguments is recorded beside it."""
    @functools.wraps(current)
    def wrapped(*args, **kwargs):
        new = current(*args, **kwargs)
        try:
            old = frozen(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - the old producer's failure is a recorded difference
            old = {"raised": f"{type(exc).__name__}: {exc}"}
        _record(site, shape(new, "new"), shape(old, "old"), case(*args, **kwargs))
        return new
    wrapped.__words_ab__ = True
    return wrapped


def _gap_text(value, side):
    """A list of filled gaps as its clauses and its shown sentences: the current `(clause, sentence)` pairs
    (Lean's), the old `(clause, value)` pairs worded by the old `gap_sentences`."""
    from conformance import frozen_words
    if side == "new":
        from ve.readings_s2_english import shown_gaps
        return {"clauses": [c for c, _ in value], "text": shown_gaps(value)}
    old = frozen_words.module("readings_s2_english")
    return {"clauses": [c for c, _ in value], "text": old.gap_sentences(value)}


def install():
    """Wrap every call site Q2.4 moved (idempotent)."""
    from conformance import frozen_words
    from ve import norm_defaults_english, readings_route, readings_s2_wording
    if getattr(readings_s2_wording.S2Wording.shown_situation, "__words_ab__", False):
        return
    old_s2 = frozen_words.module("readings_s2_wording").S2Wording
    old_s1 = frozen_words.module("readings_route").Wording
    old_nd = frozen_words.module("norm_defaults_english")
    same = lambda value, side: value  # noqa: E731
    S2 = readings_s2_wording.S2Wording
    S2.shown_situation = _compare("readings.situation", S2.shown_situation, old_s2.situation, same,
                                  lambda self, data, choice: {"data": data, "choice": choice})
    S2.gaps = _compare("readings.gaps", S2.gaps, old_s2.gaps, _gap_text, lambda self, data: {"data": data})
    S2.plan_gaps = _compare("readings.plan_gaps", S2.plan_gaps, old_s2.plan_gaps, _gap_text,
                            lambda self, model, gaps: {"model": model, "gaps": gaps})
    S2.pair_premise = _compare("readings.pair", S2.pair_premise, old_s2.pair_premise, same,
                               lambda self, label: {"label": label})
    W = readings_route.Wording
    W.situation_text = _compare("readings.s1_situation", W.situation_text, old_s1.situation_text, same,
                                lambda self, set_id, witness, entry: {"set": set_id, "entry": entry})
    W.gap_text = _compare("readings.s1_gaps", W.gap_text, old_s1.gap_text, same, lambda self, base: {"base": base})
    for name in ("status_sentence", "gap_sentence", "latent_conflict_sentence", "completion_question"):
        setattr(norm_defaults_english, name,
                _compare(f"norm_defaults.{name}", getattr(norm_defaults_english, name), getattr(old_nd, name), same,
                         lambda document, situation, row: {"environment": document.env.to_dict(), "row": row}))
    norm_defaults_english.legend = _compare("norm_defaults.legend", norm_defaults_english.legend, old_nd.legend,
                                            same, lambda env: {"environment": env.to_dict()})


# pytest plugin (`-p tools.words_ab`): the comparisons of every call a test makes.

def pytest_configure(config):
    install()


# The corpora.

def norm_defaults_corpus(trees: int) -> None:
    from conformance import norm_defaults_differential as generator
    from conformance import frozen_norm_defaults as oracle
    from ve import norm_defaults_english as english
    from ve.model import FiniteModel
    from ve.norm_defaults import UnspecifiedDocument, report, search_reached
    from ve.norm_defaults_route import run_case
    for seed in range(trees):
        env, rules, raw = generator.case(seed, profiled=True)
        frozen = oracle.UnspecifiedDocument(env, rules)
        document = UnspecifiedDocument(env, rules)
        situation = FiniteModel.from_dict(document.situation_environment(), raw)
        english.legend(env)
        for case, _, kind in generator.point_cases(frozen, raw):
            row = run_case(case)
            if row.get("status") != "ok":
                continue
            if kind.startswith("conflict:"):
                if row.get("verdict") == "CONFLICT" and row.get("kind") == "latent":
                    english.latent_conflict_sentence(document, situation, row)
            elif kind != "table3" and "point_status" in row:
                english.status_sentence(document, situation, row)
        for line in report(document, model=raw)["report"]:
            if line.get("reached") == "reachable" and "witness" in line:
                english.gap_sentence(document, situation, line)
        for predicate in document.unspec:
            english.completion_question(document, predicate, search_reached(document, predicate))


def _pilot(item):
    """`check_document` of one pilot document, its moved sites compared (in a pool worker)."""
    scratch, name, sha, text = item
    from ve.document import check_document
    from ve.errors import CheckerUnavailable, VEError
    install()
    path = Path(scratch) / f"{sha[:16]}.ve.md"
    path.write_bytes(text)
    try:
        check_document(path)
        return name, sha, None
    except (VEError, CheckerUnavailable) as exc:
        # a document VE refuses (or a checker that is unavailable) shows no readings English to compare
        return name, sha, type(exc).__name__


def pilot_corpus(workers: int = 1) -> None:
    import multiprocessing
    from tools.lean_first_diff import pilot_documents
    documents = pilot_documents(ROOT)
    checked, refused = 0, []
    with tempfile.TemporaryDirectory(prefix="words-ab-pilots-") as scratch, \
            multiprocessing.get_context("fork").Pool(workers) as pool:
        for done, (name, sha, error) in enumerate(pool.imap_unordered(
                _pilot, [(scratch, name, sha, text) for name, sha, text in documents]), 1):
            if error is None:
                checked += 1
            else:
                refused.append(f"{name} ({sha[:12]}): {error}")
            print(f"pilot {done}/{len(documents)}: {name} {error or 'checked'}", flush=True)
    print(json.dumps({"pilots": len(documents), "pilots_checked": checked, "pilots_refused": refused}, indent=1))


def summary(paths, write=False):
    counts, differences = {}, []
    files = [f for path in paths for f in (sorted(Path(path).glob("*.jsonl")) if Path(path).is_dir() else [Path(path)])]
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            site = counts.setdefault(row["site"], {"calls": 0, "same": 0})
            site["calls"] += 1
            site["same"] += row["same"]
            if not row["same"]:
                differences.append(row)
    result = {"method": "every call of each moved site against the pre-Q2.4 producer on the same inputs "
                        "(conformance/frozen_words.py at its REVISION)",
              "sites": dict(sorted(counts.items())), "calls": sum(c["calls"] for c in counts.values()),
              "differences": differences}
    if write:
        EVIDENCE.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    corpus = sub.add_parser("corpus")
    corpus.add_argument("--out", required=True)
    corpus.add_argument("--trees", type=int, default=1000)
    corpus.add_argument("--skip-pilots", action="store_true")
    corpus.add_argument("--workers", type=int, default=1)
    show = sub.add_parser("summary")
    show.add_argument("paths", nargs="+")
    show.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "corpus":
        Path(args.out).mkdir(parents=True, exist_ok=True)
        os.environ["VE_WORDS_AB"] = args.out
        install()
        if args.trees:
            norm_defaults_corpus(args.trees)
        if not args.skip_pilots:
            pilot_corpus(args.workers)
        print(json.dumps(summary([args.out])["sites"], indent=1))
        return 0
    result = summary(args.paths, write=args.write)
    print(json.dumps({k: v for k, v in result.items() if k != "differences"}, indent=1))
    print(f"{len(result['differences'])} differences")
    return 1 if result["differences"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
