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

The comparison (`classify`), from the plan: *yes* must be ALL unless the older route's saved reason says its search
budget prevented a classification. ALL admits only *yes* and *unknown* rows; NONE admits no *yes* row. The report
distinguishes identical verdicts from compatible evidence differences, especially `ask` unknown with a checked X1
conflict. Every unexplained combination is `requires review`, which fails the run.
"""
from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
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
OUT = ROOT / "docs/spec/question-answering-q2/evidence/agreement.json.gz"
_spec = importlib.util.spec_from_file_location("ask_fixtures", ROOT / "tools/ask_fixtures.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)
FIXTURES_METHOD = "ve document readings --conclusion on each recorded question AST"
CORPUS_METHOD = ("each query of the readings suites and of the generated norm-defaults corpus asked as F1 "
                 "(`Is it the case that <canonical sentence>?`) with ve ask, against ve document readings "
                 "--conclusion on the same document and formula")


OLDER_BUDGET_REASON = "no complete checked classification within the search budget"


def saved_agreement() -> dict:
    """Read the compressed, committed agreement record."""
    return json.loads(gzip.decompress(OUT.read_bytes())) if OUT.exists() else {}


def save_agreement(data: dict) -> None:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    OUT.write_bytes(gzip.compress(payload, mtime=0))


def classify(leads: list[str], older: str | None, older_reason: str | None = None,
             ask_reasons: list[str | None] | None = None) -> str:
    """Compare evidence without calling a merely compatible verdict identical."""
    from ve.ask import LEADS  # The relay schema is the owner of the lead vocabulary.
    if older is None:
        return "older route gave no verdict"
    if older not in {"ALL", "SOME", "NONE", "UNKNOWN"}:
        return f"requires review: unrecognized older verdict {older}"
    if not leads or any(lead not in LEADS for lead in leads):
        return "requires review: missing or unrecognized ask lead"
    all_yes = bool(leads) and all(lead == "yes" for lead in leads)
    if all_yes and older != "ALL":
        if older == "UNKNOWN" and older_reason == OLDER_BUDGET_REASON:
            return "older budget exhausted"
        return f"requires review: every row yes, older {older}"
    if older == "ALL" and any(lead not in ("yes", "unknown") for lead in leads):
        return "requires review: older ALL, a row neither yes nor unknown"
    if older == "NONE" and "yes" in leads:
        return "requires review: older NONE, a row yes"
    if "unknown" in leads and ask_reasons and "X1" in ask_reasons:
        return "ask unknown (X1 conflict)"
    if ((older == "ALL" and all(lead == "yes" for lead in leads)) or
            (older == "NONE" and all(lead == "no" for lead in leads)) or
            (older == "UNKNOWN" and all(lead == "unknown" for lead in leads))):
        return "same verdict"
    if "unknown" in leads:
        return "ask unknown (other)"
    return "compatible difference"


def _older(path: Path, conclusion, timeout: float) -> tuple[str | None, str, str | None]:
    """The existing route's verdict for `conclusion` over the document at `path`, in a child process."""
    with tempfile.TemporaryDirectory(prefix="ve-q2-agreement-") as directory:
        question = Path(directory) / "conclusion.json"
        question.write_text(json.dumps(conclusion))
        try:
            done = subprocess.run([sys.executable, "-m", "ve", "document", "readings", str(path), "--conclusion",
                                   str(question)], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, f"older route exceeded {timeout:g} s wall", None
    if done.returncode:
        return None, f"older route exit {done.returncode}: {done.stderr.strip()[:200]}", None
    answer = json.loads(done.stdout)
    return answer.get("verdict") or answer.get("status"), "ok", answer.get("reason")


def _older_here(path: Path, conclusion) -> tuple[str | None, str, str | None]:
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
            return None, f"older route refused: {type(exc).__name__}: {str(exc)[:160]}", None
    if code:
        return None, f"older route exit {code}", None
    answer = json.loads(out.getvalue())
    return answer.get("verdict") or answer.get("status"), "ok", answer.get("reason")


def fixture_row(ident: str, timeout: float) -> dict:
    entry = AF.load(ident)
    if "error" in entry:
        return {"fixture": ident, "ask": "refused", "older": None, "status": "outside ask route"}
    older, note, older_reason = _older(ROOT / entry["path"], entry["result"]["ast"], timeout)
    if older is None:
        return {"fixture": ident, "ask": entry["result"]["lead"], "older": None, "status": note}
    status = classify([row["lead"] for row in entry["result"]["rows"]], older, older_reason,
                      [row["reason"] for row in entry["result"]["rows"]])
    return {"fixture": ident, "ask": entry["result"]["lead"], "older": older,
            "older_reason": older_reason, "status": "compared" if not status.startswith("requires review") else status}


def fixtures(requested, timeout):
    saved = saved_agreement()
    rows = {row["fixture"]: row for row in saved.get("rows", [])}
    for ident, _, _ in AF.FIXTURES:
        if not requested or ident in requested:
            rows[ident] = fixture_row(ident, timeout)
            print(f"{ident}: {rows[ident]['status']}", flush=True)
    saved.update(method=FIXTURES_METHOD, rows=[rows[i] for i, _, _ in AF.FIXTURES if i in rows])
    save_agreement(saved)
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
            older = json.loads(out.getvalue())
            record = {"corpus": "readings", "document": Path(args[1]).read_text(encoding="utf-8"),
                      "conclusion": conclusion, "older": older.get("verdict"),
                      "older_reason": older.get("reason")}
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
            older, note, older_reason = _older_here(path, conclusion)
            out.append({"corpus": "norm-defaults", "case": row["case"], "document": row["text"],
                        "conclusion": conclusion, "older": older, "older_reason": older_reason, "note": note})
    return out


def norm_defaults(out: Path, trees: int, workers: int, start: int = 0) -> None:
    import multiprocessing
    from tools.lean_first_diff import norm_defaults_corpus
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ve-q2-nd-") as scratch:
        corpus_file = Path(scratch) / "corpus.json"
        norm_defaults_corpus(corpus_file)
        rows = [row for row in json.loads(corpus_file.read_text()) if not row["case"].startswith("invalid/")][start:trees]
        with open(out / "norm-defaults.jsonl", "w", encoding="utf-8") as sink, \
                multiprocessing.get_context("fork").Pool(workers) as pool:
            for found in pool.imap_unordered(_nd_queries, [(scratch, row) for row in rows]):
                for record in found:
                    sink.write(json.dumps(record) + "\n")
                sink.flush()


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
    scratch, index, key, record = item
    from ve.ask import answer
    from ve.errors import CheckerUnavailable, VEError
    raw = record["document"].encode("utf-8")
    path = Path(scratch) / f"d{index}.ve.md"
    path.write_bytes(raw)
    row = {"corpus": record["corpus"], "case": record.get("case"), "conclusion": record["conclusion"],
           "older": record["older"], "older_reason": record.get("older_reason")}
    if record["older"] is None:
        row.update(status="older route gave no verdict", note=record.get("note"))
        return key, row
    question = _question(raw, record["conclusion"])
    if question is None:
        row["status"] = "not asked: no question VE reads as the conclusion"
        return key, row
    row["question"] = question
    try:
        result = answer(path, raw, question)
    except (VEError, CheckerUnavailable) as exc:
        row.update(status=f"ask refused: {type(exc).__name__}", note=str(exc)[:200])
        return key, row
    leads = [r["lead"] for r in result["rows"]]
    reasons = [r["reason"] for r in result["rows"]]
    row.update(lead=result["lead"], leads=leads, ask_reasons=reasons,
               status=classify(leads, record["older"], record.get("older_reason"), reasons))
    return key, row


def corpus(paths, write=False, workers=1, checkpoint: Path | None = None):
    import multiprocessing
    records, seen = [], set()
    input_counts = {}
    raw_cases = {}
    for path in paths:
        for f in (sorted(Path(path).glob("*.jsonl")) if Path(path).is_dir() else [Path(path)]):
            for line in f.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                input_counts[record["corpus"]] = input_counts.get(record["corpus"], 0) + 1
                if record["corpus"] == "norm-defaults":
                    raw_cases[record["case"]] = raw_cases.get(record["case"], 0) + 1
                key = hashlib.sha256((record["document"] + "\n" + json.dumps(record["conclusion"],
                                                                         sort_keys=True)).encode()).hexdigest()
                if key not in seen:
                    seen.add(key)
                    records.append((key, record))
    incomplete = {case: count for case, count in raw_cases.items() if count != 8}
    if incomplete:
        raise ValueError(f"norm-defaults raw corpus has incomplete or repeated trees: {incomplete}")
    done = {}
    if checkpoint is not None and checkpoint.exists():
        for line in checkpoint.read_text(encoding="utf-8").splitlines():
            saved = json.loads(line)
            if saved["key"] in seen:
                row = saved["row"]
                if "leads" in row:
                    row["status"] = classify(row["leads"], row["older"], row.get("older_reason"),
                                             row.get("ask_reasons"))
                done[saved["key"]] = row
    pending = [(i, key, record) for i, (key, record) in enumerate(records) if key not in done]
    with tempfile.TemporaryDirectory(prefix="ve-q2-corpus-") as scratch, \
            multiprocessing.get_context("fork").Pool(workers) as pool, \
            (checkpoint.open("a", encoding="utf-8") if checkpoint is not None else contextlib.nullcontext()) as sink:
        for key, row in pool.imap_unordered(_compare, [(scratch, i, key, record) for i, key, record in pending]):
            done[key] = row
            if checkpoint is not None:
                sink.write(json.dumps({"key": key, "row": row}, ensure_ascii=False) + "\n")
                sink.flush()
            print(f"{row['corpus']} {len(done)}/{len(records)}: {row['status']}", flush=True)
    results = [done[key] for key, _ in records]
    counts = {}
    for row in results:
        bucket = counts.setdefault(row["corpus"], {})
        status = row["status"].split(":")[0]
        bucket[status] = bucket.get(status, 0) + 1
    trees = len({row["case"] for row in results if row["corpus"] == "norm-defaults"})
    scope = (f"all captured readings-suite queries and {trees} generated norm-defaults trees, "
             "with one ground and one universal query per regulated predicate")
    summary = {"method": CORPUS_METHOD, "scope": scope, "input_counts": input_counts,
               "queries": len(results), "counts": counts,
               "requires_review": [r for r in results if r["status"].startswith("requires review")],
               "rows": results}
    if write:
        saved = saved_agreement() or {"method": FIXTURES_METHOD, "rows": []}
        saved["corpus"] = summary
        save_agreement(saved)
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
    nd.add_argument("--start", type=int, default=0, help="first seed to generate (for a resumed corpus run)")
    nd.add_argument("--workers", type=int, default=1)
    cp = sub.add_parser("corpus")
    cp.add_argument("paths", nargs="+")
    cp.add_argument("--write", action="store_true")
    cp.add_argument("--workers", type=int, default=1)
    cp.add_argument("--checkpoint", type=Path, help="append each compared query for a resumable corpus run")
    args = parser.parse_args(argv)
    if args.command == "fixtures":
        saved = fixtures(set(args.ids), args.timeout)
        return 1 if any(row["status"].startswith("requires review") for row in saved["rows"]) else 0
    if args.command == "norm-defaults":
        norm_defaults(Path(args.out), args.trees, args.workers, args.start)
        return 0
    summary = corpus(args.paths, write=args.write, workers=args.workers, checkpoint=args.checkpoint)
    print(json.dumps(summary["counts"], indent=1))
    return 1 if summary["requires_review"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
