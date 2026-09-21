"""Run ``python -m ve --help`` for the small file-based checking interface."""
import argparse
import json
from pathlib import Path
import sys

from .ast import doc_from_json, document_to_data
from .check import check
from .environment import Environment
from .errors import ResourceLimit, VEError
from .fol import document_from_named_fol
from .limits import MAX_PACKAGE_BYTES, MAX_SOURCE_BYTES
from .model import FiniteModel
from .parser import parse
from .printer import natural_document, print_document, render
from .search import find_countermodel
from .wire import loads_json


def _read(path, limit=MAX_PACKAGE_BYTES):
    if path == "-":
        data = sys.stdin.buffer.read(limit + 1)
    else:
        with Path(path).open("rb") as stream:
            data = stream.read(limit + 1)
    if len(data) > limit:
        raise ResourceLimit(f"Input {path!r} exceeds {limit} bytes")
    return data


def _emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m ve", description="Experimental VE v0 language checking")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("parse", "format", "render", "evaluate", "check", "import-fol", "countermodel"):
        sub = commands.add_parser(command)
        sub.add_argument("--env", required=True, help="environment JSON file")
        if command == "countermodel":
            sub.add_argument("--premises", help="VE document; omit for no premises")
            sub.add_argument("--conclusion", required=True, help="exactly one VE statement")
            sub.add_argument("--max-domain-size", type=int, default=2)
            sub.add_argument("--min-domain-size", type=int, default=0)
            sub.add_argument("--nonempty-domains", action="store_true")
            sub.add_argument("--nonvacuous-for", help="VE formula whose quantifiers and implications must be non-vacuous")
            sub.add_argument("--max-models", type=int, default=10_000)
        else:
            sub.add_argument("source", help="VE source or, for import-fol, FOL JSON; '-' reads stdin")
        if command in ("render", "import-fol"):
            sub.add_argument("--view", choices=("fol_symbols", "fol_keywords", "ve_strict", "ve_natural",
                                                 "canonical", "natural"), default="ve_strict")
        if command in ("evaluate", "check"):
            sub.add_argument("--model", required=command == "evaluate", help="complete finite-model JSON")
            sub.add_argument("--candidate-ast", help="document AST JSON to check against source")
        if command in ("evaluate", "check", "countermodel"):
            sub.add_argument("--max-evaluations", type=int, default=1_000_000)
        if command in ("evaluate", "check"):
            sub.add_argument("--no-trace", action="store_true", help="omit explanations to use the full evaluation budget")
    args = parser.parse_args(argv)
    try:
        env = Environment.from_json(_read(args.env))
        if args.command == "countermodel":
            premises = parse(env, _read(args.premises, MAX_SOURCE_BYTES)).formulas if args.premises else ()
            conclusion = parse(env, _read(args.conclusion, MAX_SOURCE_BYTES))
            if len(conclusion.formulas) != 1:
                raise VEError("A claimed entailment requires exactly one conclusion statement")
            nonvacuous = None
            if args.nonvacuous_for:
                document = parse(env, _read(args.nonvacuous_for, MAX_SOURCE_BYTES))
                if len(document.formulas) != 1:
                    raise VEError("--nonvacuous-for requires exactly one statement")
                nonvacuous = document.formulas[0]
            result = find_countermodel(env, premises, conclusion.formulas[0], max_domain_size=args.max_domain_size,
                                       min_domain_size=args.min_domain_size,
                                       nonempty_domains=args.nonempty_domains, nonvacuous_for=nonvacuous,
                                       max_models=args.max_models, max_evaluations=args.max_evaluations)
            _emit(result.to_dict())
            return 0 if result.status == "Found" else (3 if result.status == "NotFound" else 2)
        if args.command == "import-fol":
            document = document_from_named_fol(env, loads_json(_read(args.source)))
            if args.view == "natural":
                _emit(natural_document(env, document).to_dict())
                return 0
            view = {"canonical": "ve_strict"}.get(args.view, args.view)
            print(render(document, env, view), end="")
            return 0
        source = _read(args.source, MAX_SOURCE_BYTES)
        if args.command in ("check", "evaluate", "parse"):
            model = FiniteModel.from_json(env, _read(args.model)) if getattr(args, "model", None) else None
            candidate = (doc_from_json(env, _read(args.candidate_ast))
                         if getattr(args, "candidate_ast", None) else None)
            record = check(env, source, model, candidate_ast=candidate,
                           max_evaluations=getattr(args, "max_evaluations", 1_000_000),
                           trace=not getattr(args, "no_trace", False))
            _emit(record)
            if model is None:
                return 0
            return {"Satisfied": 0, "Violated": 1, "ResourceLimit": 2}[record["evaluation"]["status"]]
        document = parse(env, source)
        if args.command == "render":
            if args.view == "natural":
                _emit(natural_document(env, document).to_dict())
                return 0
            view = {"canonical": "ve_strict"}.get(args.view, args.view)
            print(render(document, env, view), end="")
        else:
            print(print_document(env, document), end="")
        return 0
    except VEError as exc:
        _emit({"status": "ResourceLimit" if exc.code == "ResourceLimit" else "InvalidInput", "error": exc.to_dict()})
        return 2
    except (OSError, ValueError) as exc:
        _emit({"status": "InvalidInput", "error": {"code": "InvalidInput", "message": str(exc)}})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
