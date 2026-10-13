"""Q2.6's agreement with the existing check (docs/spec/question-answering-PLAN.md, Q2.6), without model calls.

    uv run python tools/question_answering_agreement.py fixtures [IDS...] [--timeout S]   # every fixture question
    VE_QA_AGREEMENT=DIR uv run python -m pytest -p tools.question_answering_agreement tests/test_readings_*.py
                                                     # capture the readings suites' queries into DIR
    uv run python tools/question_answering_agreement.py norm-defaults --out DIR [--trees N] [--workers W]
                                                     # the norm-defaults corpus's queries into DIR
    uv run python tools/question_answering_agreement.py corpus DIR... [--write] [--workers W]
                                                     # ask each query and compare

For every fixture question, and for every query of the readings and norm-defaults conformance corpora asked as an
F1 question of its document, Lean's leads (`ve ask`) are compared with `ve document readings --conclusion` on the
same document and formula (RD-3's fold, or Python's W2 fold on a document without content-bearing sets).

The corpora: the readings corpus is every `readings --conclusion` query the readings suites ask of a document (the
pytest plugin records the document's text, the conclusion and the verdict the existing route printed, for queries
with no `--under`, `--sentence` or `--narrowing`); the norm-defaults corpus is the generated documents of
`conformance/norm_defaults_differential.py` (seeds 0 to `--trees` - 1, as `tools/lean_first_diff.py` writes them),
each asked, for every regulated predicate, whether it holds of every element and of the constant `k`.

A query is asked as F1, `Is it the case that <sentence>?`, where the sentence is the conclusion's canonical
sentence on the existing English surface (read back to the conclusion, `readings_s2_english.canonical_sentence`). A
query whose sentence Lean does not read as the conclusion is counted, not compared (`not asked`).

The comparison (`classify`), from the plan: *yes* must be ALL; ALL admits only *yes* and *unknown* rows (a row whose
conflict or premise status is unchecked is unknown, never a contradiction); NONE admits no *yes* row; SOME, NOT ALL
and UNKNOWN admit anything but every row *yes*. *No* from a checked negation certificate and *not settled* from a
checked split may coexist with the fold's UNKNOWN. Every other combination is `requires review`, which fails the run.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs/spec/question-answering-q2/evidence/agreement.json"
_spec = importlib.util.spec_from_file_location("ask_fixtures", ROOT / "tools/ask_fixtures.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)
FIXTURES_METHOD = "ve document readings --conclusion on each recorded question AST"
CORPUS_METHOD = ("each query of the readings suites and of the generated norm-defaults corpus asked as F1 "
                 "(`Is it the case that <canonical sentence>?`) with ve ask, against ve document readings "
                 "--conclusion on the same document and formula")


def classify(leads: list[str], older: str | None) -> str:
    """`agrees`, or `requires review` with the reason, for the rows' leads against the older route's verdict."""
    if older is None:
        return "older route gave no verdict"
    all_yes = bool(leads) and all(lead == "yes" for lead in leads)
    if all_yes and older != "ALL":
        return f"requires review: every row yes, older {older}"
    if older == "ALL" and any(lead not in ("yes", "unknown") for lead in leads):
        return "requires review: older ALL, a row neither yes nor unknown"
    if older == "NONE" and "yes" in leads:
        return "requires review: older NONE, a row yes"
    return "agrees"


def _older(path: Path, conclusion, timeout: float) -> tuple[str | None, str]:
    """The existing route's verdict for `conclusion` over the document at `path`, in a child process."""
    with tempfile.TemporaryDirectory(prefix="ve-q2-agreement-") as directory:
        question = Path(directory) / "conclusion.json"
        question.write_text(json.dumps(conclusion))
        try:
            done = subprocess.run([sys.executable, "-m", "ve", "document", "readings", str(path), "--conclusion",
                                   str(question)], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, f"older route exceeded {timeout:g} s wall"
    if done.returncode:
        return None, f"older route exit {done.returncode}: {done.stderr.strip()[:200]}"
    answer = json.loads(done.stdout)
    return answer.get("verdict") or answer.get("status"), "ok"


def _older_here(path: Path, conclusion) -> tuple[str | None, str]:
    """`_older` in this process (the generated corpus's many small documents)."""
    from ve.document import main as document_main
    from ve.errors import CheckerUnavailable, VEError
    with tempfile.TemporaryDirectory(prefix="ve-q2-agreement-") as directory:
        question = Path(directory) / "conclusion.json"
        question.write_text(json.dumps(conclusion))
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                code = document_main(["readings", str(path), "--conclusion", str(question)])
        except (VEError, CheckerUnavailable) as exc:
            return None, f"older route refused: {type(exc).__name__}: {str(exc)[:160]}"
    if code:
        return None, f"older route exit {code}"
    answer = json.loads(out.getvalue())
    return answer.get("verdict") or answer.get("status"), "ok"


def fixture_row(ident: str, timeout: float) -> dict:
    entry = AF.load(ident)
    if "error" in entry:
        return {"fixture": ident, "ask": "refused", "older": None, "status": "outside ask route"}
    older, note = _older(ROOT / entry["path"], entry["result"]["ast"], timeout)
    if older is None:
        return {"fixture": ident, "ask": entry["result"]["lead"], "older": None, "status": note}
    status = classify([row["lead"] for row in entry["result"]["rows"]], older)
    return {"fixture": ident, "ask": entry["result"]["lead"], "older": older,
            "status": "compared" if status == "agrees" else status}


def fixtures(requested, timeout):
    saved = json.loads(OUT.read_text()) if OUT.exists() else {}
    rows = {row["fixture"]: row for row in saved.get("rows", [])}
    for ident, _, _ in AF.FIXTURES:
        if not requested or ident in requested:
            rows[ident] = fixture_row(ident, timeout)
            print(f"{ident}: {rows[ident]['status']}", flush=True)
    saved.update(method=FIXTURES_METHOD, rows=[rows[i] for i, _, _ in AF.FIXTURES if i in rows])
    OUT.write_text(json.dumps(saved, indent=1, ensure_ascii=False) + "\n")
    return saved


# The readings suites' queries (pytest plugin `-p tools.question_answering_agreement`).

def _recording(original, directory):
    def recorded(argv=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = original(argv)
        sys.stdout.write(out.getvalue())
        args = list(argv or [])
        if (code == 0 and args[:1] == ["readings"] and "--conclusion" in args
                and not {"--under", "--sentence", "--narrowing"} & set(args)):
            conclusion = json.loads(Path(args[args.index("--conclusion") + 1]).read_text())
            record = {"corpus": "readings", "document": Path(args[1]).read_text(encoding="utf-8"),
                      "conclusion": conclusion, "older": json.loads(out.getvalue()).get("verdict")}
            with open(Path(directory) / f"{os.getpid()}.jsonl", "a", encoding="utf-8") as sink:
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
        return code
    recorded.__agreement__ = True
    return recorded


def pytest_configure(config):
    directory = os.environ.get("VE_QA_AGREEMENT")
    if not directory:
        return
    from ve import document
    if not getattr(document.main, "__agreement__", False):
        document.main = _recording(document.main, directory)


# The generated norm-defaults corpus's queries.

def _nd_queries(item):
    """The generated document's queries, each with the existing route's verdict (in a pool worker)."""
    scratch, row = item
    from conformance import norm_defaults_differential as generator
    path = Path(scratch) / f"{row['case']}.ve.md"
    path.write_text(row["text"])
    out = []
    for predicate in generator.REGULATED:
        for conclusion in (["forall", "act", ["unary", predicate, ["var", 0]]], ["unary", predicate, ["const", "k"]]):
            older, note = _older_here(path, conclusion)
            out.append({"corpus": "norm-defaults", "case": row["case"], "document": row["text"],
                        "conclusion": conclusion, "older": older, "note": note})
    return out


def norm_defaults(out: Path, trees: int, workers: int) -> None:
    import multiprocessing
    from tools.lean_first_diff import norm_defaults_corpus
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ve-q2-nd-") as scratch:
        corpus_file = Path(scratch) / "corpus.json"
        norm_defaults_corpus(corpus_file)
        rows = [row for row in json.loads(corpus_file.read_text()) if not row["case"].startswith("invalid/")][:trees]
        with open(out / "norm-defaults.jsonl", "w", encoding="utf-8") as sink, \
                multiprocessing.get_context("fork").Pool(workers) as pool:
            for found in pool.imap(_nd_queries, [(scratch, row) for row in rows]):
                for record in found:
                    sink.write(json.dumps(record) + "\n")


# Asking each query.

def _question(raw: bytes, conclusion) -> str | None:
    """The conclusion asked as F1, when its canonical sentence exists and Lean reads the question as it."""
    from ve.ask import environment, read
    from ve.ast import formula_from_data
    from ve.errors import CheckerUnavailable, VEError
    from ve.readings_s2_english import canonical_sentence
    env = environment(raw)
    try:
        sentence = canonical_sentence(env, formula_from_data(env, conclusion), "no canonical sentence")
    except (VEError, ValueError, KeyError):
        return None
    body = sentence.rstrip(".")
    for text in dict.fromkeys((body[:1].lower() + body[1:], body)):
        question = f"Is it the case that {text}?"
        try:
            if read(raw, question).get("ast") == conclusion:
                return question
        except (VEError, CheckerUnavailable):
            continue
    return None


def _compare(item):
    """One corpus record asked and compared (in a pool worker)."""
    scratch, index, record = item
    from ve.ask import answer
    from ve.errors import CheckerUnavailable, VEError
    raw = record["document"].encode("utf-8")
    path = Path(scratch) / f"d{index}.ve.md"
    path.write_bytes(raw)
    row = {"corpus": record["corpus"], "case": record.get("case"), "conclusion": record["conclusion"],
           "older": record["older"]}
    if record["older"] is None:
        row.update(status="older route gave no verdict", note=record.get("note"))
        return row
    question = _question(raw, record["conclusion"])
    if question is None:
        row["status"] = "not asked: no question VE reads as the conclusion"
        return row
    row["question"] = question
    try:
        result = answer(path, raw, question)
    except (VEError, CheckerUnavailable) as exc:
        row.update(status=f"ask refused: {type(exc).__name__}", note=str(exc)[:200])
        return row
    leads = [r["lead"] for r in result["rows"]]
    row.update(lead=result["lead"], leads=leads, status=classify(leads, record["older"]))
    return row


def corpus(paths, write=False, workers=1):
    import multiprocessing
    records, seen = [], set()
    for path in paths:
        for f in (sorted(Path(path).glob("*.jsonl")) if Path(path).is_dir() else [Path(path)]):
            for line in f.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                key = (record["document"], json.dumps(record["conclusion"]))
                if key not in seen:
                    seen.add(key)
                    records.append(record)
    results = []
    with tempfile.TemporaryDirectory(prefix="ve-q2-corpus-") as scratch, \
            multiprocessing.get_context("fork").Pool(workers) as pool:
        for row in pool.imap(_compare, [(scratch, i, r) for i, r in enumerate(records)]):
            results.append(row)
            print(f"{row['corpus']} {len(results)}/{len(records)}: {row['status']}", flush=True)
    counts = {}
    for row in results:
        bucket = counts.setdefault(row["corpus"], {})
        status = row["status"].split(":")[0]
        bucket[status] = bucket.get(status, 0) + 1
    summary = {"method": CORPUS_METHOD, "queries": len(results), "counts": counts,
               "requires_review": [r for r in results if r["status"].startswith("requires review")],
               "rows": results}
    if write:
        saved = json.loads(OUT.read_text()) if OUT.exists() else {"method": FIXTURES_METHOD, "rows": []}
        saved["corpus"] = summary
        OUT.write_text(json.dumps(saved, indent=1, ensure_ascii=False) + "\n")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    fx = sub.add_parser("fixtures")
    fx.add_argument("ids", nargs="*")
    fx.add_argument("--timeout", type=float, default=1800)
    nd = sub.add_parser("norm-defaults")
    nd.add_argument("--out", required=True)
    nd.add_argument("--trees", type=int, default=1000)
    nd.add_argument("--workers", type=int, default=1)
    cp = sub.add_parser("corpus")
    cp.add_argument("paths", nargs="+")
    cp.add_argument("--write", action="store_true")
    cp.add_argument("--workers", type=int, default=1)
    args = parser.parse_args(argv)
    if args.command == "fixtures":
        saved = fixtures(set(args.ids), args.timeout)
        return 1 if any(row["status"].startswith("requires review") for row in saved["rows"]) else 0
    if args.command == "norm-defaults":
        norm_defaults(Path(args.out), args.trees, args.workers)
        return 0
    summary = corpus(args.paths, write=args.write, workers=args.workers)
    print(json.dumps(summary["counts"], indent=1))
    return 1 if summary["requires_review"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
