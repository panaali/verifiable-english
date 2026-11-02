"""Python relay of judgment terms' authoring rows (docs/spec/judgment-terms.md 9.1 and 9.5; plan JT-3).

Lean owns the line, the record and the refusal (`VE.EnglishGrammar.JudgmentLines`). `declare` sends a declaration line to
the `judgment-line` mode; `read_authored` sends the bound names with an authored source to `english.read`. The service
checks each answer against its schema; this module binds a declaration's names to the line asked about (R8) and shows
Lean's text verbatim. It holds no word list and no wording. The lines are identifier wording: JT-E1r and JT-E1s failed,
and what they say a reader understands stays unmeasured.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .errors import CheckerUnavailable, ResourceLimit, VEError

MODE = "judgment-line"
_WORDS = re.compile(r'[^ "();,.]+')


def answer_problem(row: dict, case: dict) -> str | None:
    """Why a typed answer is not bound to its request, or None: the record and the predicate name one predicate, whose
    name, sorts (in order) and decider's words are words of the request's line. That a line means this record is
    Lean's theorem `parseLine_renders`, not a check here."""
    record, predicate = row["record"], row["predicate"]
    words = _WORDS.findall(case["line"])
    if record["name"] != predicate["name"] or record["arguments"] != predicate["arguments"]:
        return "the record and the predicate differ"
    remaining = iter(words)
    if record["name"] not in words or not all(sort in remaining for sort in record["arguments"]):
        return "a name is not in the line, in its order"
    decider = record["decided_by"]
    if decider != "unstated" and not all(word in words for word in decider.split("_")):
        return "the decider is not in the line"
    return None


def declare(line: str, jurisdiction: str) -> dict:
    """Lean's W2 record and predicate for a declaration line, bound to it; Lean's refusal raises its diagnostic."""
    from .backends.relay import decide
    case = {"id": MODE, "line": line, "jurisdiction": jurisdiction}
    row = decide(MODE, [case])[0]
    problem = answer_problem(row, case)
    if problem is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean's judgment line is not bound to its request: {problem}")
    return row


def read_authored(env, source: str, judgments: list):
    """Lean's authoring reading of `source` with its bound names (spec 9.5): an undeclared evaluative word raises
    Lean's refusal, text verbatim."""
    from .backends import english_lean
    from .english import EnglishVocabulary
    reading = english_lean.read(env, source, EnglishVocabulary(env, _defer_overlay_refusals=True), {},
                                judgments=judgments)
    if reading.status != "one":
        raise reading.rejection()
    return reading


def main(argv: list[str]) -> int:
    """`ve judgments declare LINE --jurisdiction J`, `ve judgments read --env FILE [--bound NAME]... SOURCE`. Exit 0 when
    Lean answers, 2 when it refused (its diagnostic), 4 at a resource limit."""
    import argparse
    from .environment import Environment
    parser = argparse.ArgumentParser(prog="python -m ve judgments")
    commands = parser.add_subparsers(dest="command", required=True)
    declaring = commands.add_parser("declare", help="a declaration line's W2 record and predicate")
    declaring.add_argument("line")
    declaring.add_argument("--jurisdiction", required=True)
    reading = commands.add_parser("read", help="read an authored source; an undeclared evaluative word is refused")
    reading.add_argument("source")
    reading.add_argument("--env", required=True)
    reading.add_argument("--bound", action="append", default=[], help="a bound judgment's predicate name")
    options = parser.parse_args(argv)
    try:
        if options.command == "declare":
            row = declare(options.line, options.jurisdiction)
            print(json.dumps({"record": row["record"], "predicate": row["predicate"]}, ensure_ascii=False, indent=2))
        else:
            env = Environment.from_dict(json.loads(Path(options.env).read_text(encoding="utf-8")))
            print(read_authored(env, options.source, options.bound).canonical())
    except CheckerUnavailable:
        raise
    except (VEError, OSError) as exc:
        error = exc.to_dict() if isinstance(exc, VEError) else {"code": "InvalidInput", "message": str(exc)}
        print(json.dumps({"status": error["code"], "error": error}, ensure_ascii=False, indent=2))
        return 4 if isinstance(exc, ResourceLimit) else 2
    return 0
