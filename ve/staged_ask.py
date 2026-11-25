# ve-layer: 4 (the CLI's `ve ask` on a staged-route translation directory; it runs the directory's own runner)
"""`ve ask DIRECTORY QUESTION [--case ID] [--json]`: a question about one case, asked of a staged-route translation.

A staged-route translation (the statute corpus's policy texts, for example `usecases/posthog_leave`) is a directory, not
a ve-document: it holds no English vocabulary in which Lean could read a question, only
- `translation.py`: the text's rules, grounded per case;
- `run.py`: its runner. `run.py --cases ID --out FILE` grounds the rules over the case's items, proves each derived fact
  as one step, sends every step certificate to Lean and one quantity document per answer target, and writes a run file
  whose record for the case maps each question id to its answer; an answer counts only when Lean admitted every
  document it rests on (else the runner writes OPEN);
- `questions-enc.jsonl`: the encoder's question file, one case per line (`id`, `facts`, `questions` with `qid` and
  `text`); the runner's case table (`cases.py`) holds the encoder's form of each question.

So the question asked here is one of a case's own questions, found by its exact text (with `--case`, among that case's
questions; without, it must be the question of exactly one case), and its reading is the encoder's, not Lean's: Lean's
`ask` mode (`ve.ask`, for a ve-document file) is not used. This module proves nothing and decides nothing: it runs the
directory's runner on that one case in this process and prints the runner's answer for the question, or the reason it
has none, as the runner recorded it. `--json` prints the record's answer, the case's Lean counts and these honesty
fields: `route` "staged", `question` "encoded" (matched to the encoder's question by its text), `answer`
"staged_route" (the runner's wording), `proof` "lean_checked" for an answer (every document it rests on admitted by
Lean, the runner's rule), else "not_checked".

Exit codes, as `ve ask`: 0 an answer; 3 no answer (OPEN or UNSUPPORTED in the run file, with its reason); 2 not read
(not a staged-route directory, no such case, the question is not one of the case's, `--reading` or `--evidence`);
5 `CheckerUnavailable` (Lean could not be reached).
"""
from __future__ import annotations

import argparse
from concurrent.futures import BrokenExecutor
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile

from .errors import CheckerUnavailable

# The files of a staged-route translation, inside the directory the caller names. Spelled from parts on purpose: the
# repository's static analysers (tools/source_graph.py, tools/history_tests.py) read a bare file name such as "run.py"
# in a product module as every file of that name in the repository, but these are names under the caller's path.
SUFFIX = ".py"
RUNNER, RULES, QUESTIONS = "run" + SUFFIX, "translation" + SUFFIX, "questions-enc.jsonl"
FILES = (RULES, RUNNER, QUESTIONS)
EXIT_ANSWERED, EXIT_NO_ANSWER, EXIT_NOT_READ, EXIT_UNAVAILABLE = 0, 3, 2, 5
NO_ANSWER = ("OPEN", "UNSUPPORTED")
TYPED = ("DATE", "DATETIME", "AMOUNT", "NUMBER")  # answers whose text is their `value`
# What a runner that fails on a case raises (its asserts, a malformed case, a pool worker killed, its argparse): an
# operational failure of this route, exit 5, never a verdict. CheckerUnavailable passes through as itself.
RUNNER_FAILURES = (AssertionError, ArithmeticError, AttributeError, ImportError, LookupError, OSError, TypeError,
                   ValueError, RecursionError, BrokenExecutor, SystemExit)
_OPTIONS_WITH_VALUES = ("--case", "--evidence")


def document_argument(argv: list[str]) -> str | None:
    """The DOCUMENT argument of a `ve ask` command line (its first positional argument), or None."""
    skip = False
    for arg in argv:
        if skip:
            skip = False
        elif arg in _OPTIONS_WITH_VALUES:
            skip = True
        elif arg == "--":
            continue
        elif not arg.startswith("-"):
            return arg
    return None


def is_staged(argv: list[str]) -> bool:
    """True when the `ve ask` command line asks a directory (a staged-route translation is a directory; a ve-document
    is a file and keeps Lean's `ask` route)."""
    document = document_argument(argv)
    return document is not None and Path(document).is_dir()


class NotRead(Exception):
    """A question this route does not read, with the reason (exit 2)."""


def cases(directory: Path) -> list[dict]:
    """The encoder's cases of `directory/questions-enc.jsonl`; NotRead names the first line that is not a case (an
    object with an `id` and a list of questions, each an object with a `qid` and a `text`)."""
    path = directory / QUESTIONS
    table = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except ValueError as exc:
            raise NotRead(f"{path}:{number} is not JSON: {exc}") from exc
        questions = case.get("questions") if type(case) is dict else None
        if type(case) is not dict or "id" not in case or type(questions) is not list or not all(
                type(q) is dict and "qid" in q and "text" in q for q in questions):
            raise NotRead(f"{path}:{number} is not a case (an object with an id and questions with a qid and a text)")
        table.append(case)
    return table


def find(directory: Path, question: str, case: str | None) -> tuple[str, str]:
    """(case id, question id) of the encoder's question whose text is `question` (outer white space aside), in case
    `case` when given; NotRead names why there is none or more than one."""
    missing = [name for name in FILES if not (directory / name).is_file()]
    if missing:
        raise NotRead(f"{directory} is a directory but not a staged-route translation: it has no "
                      f"{', '.join(missing)} (a ve-document is asked as a file)")
    table = cases(directory)
    if case is not None and not any(c.get("id") == case for c in table):
        raise NotRead(f"{directory} has no case {case!r} (its cases: {', '.join(str(c.get('id')) for c in table)})")
    wanted = question.strip()
    found = [(c["id"], q["qid"]) for c in table if case is None or c.get("id") == case
             for q in c.get("questions", ()) if str(q.get("text", "")).strip() == wanted]
    if not found:
        where = f"case {case}" if case is not None else "any case"
        raise NotRead(f"the question is not one of the questions of {where} in {directory / 'questions-enc.jsonl'}: "
                      "a staged-route translation answers a case's own questions, asked by their exact text (it has "
                      "no vocabulary in which a new question could be read)")
    if len({cid for cid, _ in found}) > 1:
        raise NotRead(f"the question is asked of more than one case ({', '.join(sorted({c for c, _ in found}))}); "
                      "name one with --case")
    if len(found) > 1:
        raise NotRead(f"case {found[0][0]} asks this question more than once ({', '.join(q for _, q in found)}): "
                      "the text does not say which is meant")
    return found[0]


def run_case(directory: Path, case: str) -> list[dict]:
    """The directory's runner on one case: its run file's records for `case`. The runner is loaded in this process from
    its own file under its own module name (`run`), with its directory first on `sys.path`, so the workers of a process
    pool it starts import its functions as it does; it is called as `main(["--cases", case, "--out", FILE])` and what
    it prints is not shown (pool workers' output and stderr are not captured). Afterwards `sys.path` and the recursion
    limit are as before, the modules loaded from the directory are dropped, and any module that had the name of one of
    the directory's modules is put back (so a second directory's runner reads its own `translation`, and nobody else's
    `run` is replaced); modules the run loaded from outside the directory (`ve`'s among them) stay. A runner that fails
    (RUNNER_FAILURES) is CheckerUnavailable naming the failure."""
    path = (directory / RUNNER).resolve()
    own = {p.stem for p in path.parent.glob("*.py")} | {p.name for p in path.parent.iterdir()
                                                       if (p / ("__init__" + SUFFIX)).is_file()}
    saved_path, shadowed = list(sys.path), {n: sys.modules.pop(n) for n in list(sys.modules)
                                            if n.split(".")[0] in own}
    saved_modules, saved_limit = set(sys.modules), sys.getrecursionlimit()
    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        with tempfile.TemporaryDirectory(prefix="ve-staged-ask-") as scratch, \
                contextlib.redirect_stdout(io.StringIO()):
            sys.path.insert(0, str(path.parent))
            sys.modules[path.stem] = module
            spec.loader.exec_module(module)
            out = Path(scratch) / "run.json"
            module.main(["--cases", case, "--out", str(out)])
            run = json.loads(out.read_text(encoding="utf-8"))
    except RUNNER_FAILURES as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: the runner {path} failed on case {case!r}: "
                                 f"{type(exc).__name__}: {exc}") from exc
    finally:
        sys.path[:] = saved_path
        sys.setrecursionlimit(saved_limit)
        for added in set(sys.modules) - saved_modules:
            if added.split(".")[0] in own or _under(sys.modules[added], directory):
                del sys.modules[added]
        sys.modules.update(shadowed)
    records = run.get("records") if type(run) is dict else None
    if type(records) is not list or not all(type(r) is dict for r in records):
        raise CheckerUnavailable(f"CheckerUnavailable: the runner {path} wrote no list of records")
    return [r for r in records if r.get("id") == case]


def record_of(records: list[dict], qid: str, path: Path) -> dict | None:
    """The one record of the case that holds `qid` (a runner may write a case's encoder refusals as a second record
    of the same case id); None when none does (the runner's case table does not carry the question); several is a
    run file this route cannot read."""
    holding = [r for r in records if type(r.get("answers")) is dict and qid in r["answers"]]
    if len(holding) > 1:
        raise CheckerUnavailable(f"CheckerUnavailable: {len(holding)} records hold {qid} in the run file of "
                                 f"{path} ({len(records)} records of its case)")
    return holding[0] if holding else None


def _under(module, directory: Path) -> bool:
    """True when `module` was loaded from a file inside `directory` (the runner's own modules: its translation, case
    table, encoder, bridge)."""
    file = getattr(module, "__file__", None)
    return file is not None and Path(file).resolve().is_relative_to(directory.resolve())


def _inconsistent(record: dict) -> list[str]:
    """The targets the case's step log marks inconsistent (two values proved, or a proved sentinel: premises with no
    model), from the record's `steps` and its sub-cases' `steps`."""
    steps = [*(record.get("steps") or ()), *(s for sub in (record.get("subs") or ()) if type(sub) is dict
                                             for s in (sub.get("steps") or ()))]
    return [str(s.get("target")) for s in steps if type(s) is dict and s.get("inconsistent")]


def reason(answer: dict, record: dict) -> str:
    """Why the run file's answer is no answer, from the answer's and its record's own fields."""
    if answer.get("answer") == "UNSUPPORTED":
        scope = "outside the translation's scope" if record.get("scope") == "out" else "not supported in scope"
        why = record.get("unsupported")
        return f"UNSUPPORTED: the case is {scope}" + (f": {why}" if why else "")
    if answer.get("lean_rejected"):
        return "OPEN: Lean did not admit every document the staged answer rests on"
    for key in ("why", "refused"):
        if answer.get(key):
            return f"OPEN: {answer[key]}"
    if answer.get("no_form"):
        return "OPEN: no form of the translation carries this question"
    text = "OPEN: the runner established no answer for this question and recorded no reason"
    marked = _inconsistent(record)
    if marked:
        text += f" (the case's step log marks {len(marked)} step(s) inconsistent: {', '.join(marked)})"
    return text


def shown(answer: dict) -> str | None:
    """The answer's text: the value of a typed answer (TYPED), else the answer itself; None for an answer that is not
    text or a typed answer without a value (a malformed record)."""
    text, value = answer.get("answer"), answer.get("value")
    if type(text) is not str or not text:
        return None
    if text in TYPED:
        return str(value) if type(value) in (str, int) and str(value) else None
    return text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ve ask",
        description="Answer one of a case's questions from a staged-route translation directory, by the "
                    "directory's own runner (Lean replays its certificates); a ve-document file is asked by Lean.")
    parser.add_argument("document", help="a staged-route translation directory (translation.py, run.py, "
                                         "questions-enc.jsonl)")
    parser.add_argument("question", help="the case's question, by its exact text in questions-enc.jsonl")
    parser.add_argument("--case", help="the case id in questions-enc.jsonl (needed when several cases ask it)")
    parser.add_argument("--json", action="store_true", help="print the answer with its record and honesty fields")
    parser.add_argument("--reading", action="store_true", help="refused here: there is no vocabulary to read in")
    parser.add_argument("--evidence", help="refused here: the runner makes and Lean checks its own pieces")
    options = parser.parse_args(argv)
    directory = Path(options.document)
    honesty = {"operation": "question.answer", "route": "staged", "question": "encoded", "answer": "staged_route",
               "proof": "not_checked", "intent": "unconfirmed"}

    def emit(code: int, text: str, extra: dict | None = None) -> int:
        if options.json:
            print(json.dumps({**honesty, **(extra or {}), "text": text}, ensure_ascii=False, indent=2))
        else:
            print(text, file=sys.stdout if code == EXIT_ANSWERED else sys.stderr)
        return code

    try:
        if options.reading or options.evidence:
            raise NotRead("--reading and --evidence read a question in a ve-document's vocabulary; a staged-route "
                          "translation has none")
        case, qid = find(directory, options.question, options.case)
        record = record_of(run_case(directory, case), qid, directory / RUNNER)
    except NotRead as exc:
        return emit(EXIT_NOT_READ, str(exc), {"answer": "no_answer"})
    except CheckerUnavailable as exc:
        return emit(EXIT_UNAVAILABLE, str(exc), {"answer": "no_answer"})
    if record is None:
        return emit(EXIT_NO_ANSWER, f"OPEN: the runner's case table does not carry {qid} (no record of case {case} "
                                    "holds it)", {"answer": "no_answer", "case": case, "qid": qid})
    answer = record["answers"][qid]
    extra = {"case": case, "qid": qid, "record": {"answer": answer, "lean": record.get("lean")}}
    if type(answer) is not dict or answer.get("answer") in NO_ANSWER:
        why = reason(answer, record) if type(answer) is dict else f"OPEN: the runner wrote no answer for {qid}"
        return emit(EXIT_NO_ANSWER, why, {**extra, "answer": "no_answer"})
    text = shown(answer)
    if text is None:
        return emit(EXIT_UNAVAILABLE, f"CheckerUnavailable: the runner's answer for {qid} is malformed: {answer!r}",
                    {**extra, "answer": "no_answer"})
    honesty["proof"] = "lean_checked"
    return emit(EXIT_ANSWERED, text, extra)
