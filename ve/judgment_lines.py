"""Python relay of judgment terms' authoring refusal (docs/spec/judgment-terms.md 9.5; plan JT-3).

Lean owns the refusal (`VE.EnglishGrammar.JudgmentLines.refusal`). `read_authored` sends the bound names with an authored
source to `english.read` and shows Lean's text verbatim; it holds no word list and no wording (R8). The wording is not
measured: JT-E1r and JT-E1s failed.
"""
from __future__ import annotations

import json
from pathlib import Path

from .errors import CheckerUnavailable, ResourceLimit, VEError


def read_authored(env, source: str, judgments: list):
    """Lean's authoring reading of `source` with its bound names: an undeclared evaluative word raises Lean's refusal."""
    from .backends import english_lean
    from .english import EnglishVocabulary
    reading = english_lean.read(env, source, EnglishVocabulary(env, _defer_overlay_refusals=True), {},
                                judgments=judgments)
    if reading.status != "one":
        raise reading.rejection()
    return reading


def main(argv: list[str]) -> int:
    """`ve judgments read --env FILE [--bound NAME]... SOURCE`. Exit 0 when Lean reads it, 2 when it refused (its
    diagnostic), 4 at a resource limit."""
    import argparse
    from .environment import Environment
    parser = argparse.ArgumentParser(prog="python -m ve judgments")
    commands = parser.add_subparsers(dest="command", required=True)
    reading = commands.add_parser("read", help="read an authored source; an undeclared evaluative word is refused")
    reading.add_argument("source")
    reading.add_argument("--env", required=True)
    reading.add_argument("--bound", action="append", default=[], help="a bound judgment's predicate name")
    options = parser.parse_args(argv)
    try:
        env = Environment.from_dict(json.loads(Path(options.env).read_text(encoding="utf-8")))
        print(read_authored(env, options.source, options.bound).canonical())
    except CheckerUnavailable:
        raise
    except (VEError, OSError) as exc:
        error = exc.to_dict() if isinstance(exc, VEError) else {"code": "InvalidInput", "message": str(exc)}
        print(json.dumps({"status": error["code"], "error": error}, ensure_ascii=False, indent=2))
        return 4 if isinstance(exc, ResourceLimit) else 2
    return 0
