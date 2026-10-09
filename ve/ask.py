"""`ve ask DOCUMENT QUESTION --reading` (docs/spec/question-answering-PLAN.md 4.8, Q1.2).

A question is one of the document's own sentences, asked. Lean reads it (`english.question`) in the document's
vocabulary: the environment its front matter declares, as the document loader builds it, with the lexicon of the
English reader's producer. `read` is the one entry point; the CLI calls it. This module relays: it prints Lean's
`text` (the A0 line, or the refusal with its advice) and Lean's rephrasings, and writes no English of its own.

The answer to the question (`ve ask` without `--reading`, plan Q2) is not built: it exits 5.

Exit codes: 0 the question has one reading; 2 it is not read (Lean's code, class and text); 4 `ResourceLimit`;
5 `CheckerUnavailable`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .errors import CheckerUnavailable, ResourceLimit, VEError
from .limits import MAX_SOURCE_BYTES

OPERATION = "question.read"
EXIT_READ, EXIT_NOT_READ, EXIT_LIMIT, EXIT_UNAVAILABLE = 0, 2, 4, 5


def environment(raw: bytes):
    """The environment a document's sentences are read in: its front matter's, built as the loader builds it."""
    from .document import _environment, base_environment, stored_identities
    meta, _, _ = stored_identities(raw)
    return _environment(base_environment(meta))


def read(raw: bytes, question: str) -> dict:
    """Lean's checked `english.question` answer for `question` over the document `raw`, or the refusal raised as
    the class Lean names (its answer as `lean_question`)."""
    from .backends.english_lean import read_question
    from .english import EnglishVocabulary
    env = environment(raw)
    return read_question(env, question, EnglishVocabulary(env, _defer_overlay_refusals=True), {})


def _answer(exc: Exception) -> dict | None:
    return getattr(exc, "lean_question", None)


def _lines(answer: dict) -> list[str]:
    """Lean's text, its advice, then its rephrasings, one per line."""
    text = answer["text"] if "advice" not in answer else f'{answer["text"]} {answer["advice"]["text"]}'
    return [text, *answer.get("rephrasings", ())]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ve ask",
        description="Read a yes-or-no question as one of the document's sentences. Only --reading is built: "
                    "the answer itself is not (exit 5).")
    parser.add_argument("document", help="ve-document file")
    parser.add_argument("question", help="the question, ending with its only question mark")
    parser.add_argument("--reading", action="store_true", help="print the sentence the question is read as")
    parser.add_argument("--json", action="store_true", help="print Lean's whole result with the honesty fields")
    options = parser.parse_args(argv)
    from .assurance import operation
    honesty = {"operation": OPERATION, "assurance": operation(OPERATION)["assurance"]["current"],
               "intent": "unconfirmed", "proof": "not_checked", "answer": "not_built"}

    def emit(answer: dict | None, error: dict | None = None) -> None:
        if options.json:
            print(json.dumps({**honesty, **({"result": answer} if answer is not None else {}),
                              **({"error": error} if error is not None else {})}, ensure_ascii=False, indent=2))
        elif answer is not None:
            print("\n".join(_lines(answer)))
        else:
            print(error["message"], file=sys.stderr)

    if not options.reading:
        emit(None, {"class": "CheckerUnavailable", "message": "CheckerUnavailable: VE does not answer questions "
                    "yet (plan Q2); ask with --reading for the sentence the question is read as"})
        return EXIT_UNAVAILABLE
    try:
        path = Path(options.document)
        with path.open("rb") as stream:
            raw = stream.read(MAX_SOURCE_BYTES + 1)
        if len(raw) > MAX_SOURCE_BYTES:
            raise ResourceLimit(f"ResourceLimit: {options.document!r} exceeds {MAX_SOURCE_BYTES} bytes")  # relay-lint: file I/O
        answer = read(raw, options.question)
    except CheckerUnavailable as exc:
        emit(_answer(exc), {"class": "CheckerUnavailable", "message": str(exc)})
        return EXIT_UNAVAILABLE
    except ResourceLimit as exc:
        emit(_answer(exc), {"class": "ResourceLimit", "message": str(exc)})
        return EXIT_LIMIT
    except (VEError, OSError, UnicodeError) as exc:
        emit(_answer(exc), {"class": type(exc).__name__, "message": str(exc)})
        return EXIT_NOT_READ
    emit(answer)
    return EXIT_READ
