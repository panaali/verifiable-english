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
from .printer import (LEGEND_STYLES, NAMING_POLICIES, measure_jsonl_lengths, natural_document,
                      print_document, render, render_cell)
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
    suggestions = commands.add_parser("suggest-vocabulary", help="emit unreviewed English vocabulary candidates")
    suggestions.add_argument("--env", required=True)
    grammar = commands.add_parser("grammar", help="export an environment-specific decoding grammar")
    grammar.add_argument("--env", required=True, help="environment JSON file")
    grammar.add_argument("--dialect", choices=("lark", "gbnf", "ebnf"), default="lark")
    grammar.add_argument("--mode", choices=("full", "syntax"), default="full")
    grammar.add_argument("--max-binder-depth", type=int, default=3)
    grammar.add_argument("--max-binders", type=int)
    grammar.add_argument("--max-rules", type=int, default=20_000)
    output = grammar.add_mutually_exclusive_group()
    output.add_argument("--wrapper", action="store_true", help="constrain the whole VE/explanation JSON object")
    output.add_argument("--spec", action="store_true", help="emit the structured-output adapter spec as JSON")
    lengths = commands.add_parser("view-lengths", help="measure all five views of actual JSONL items")
    lengths.add_argument("--env", required=True)
    lengths.add_argument("source", help="JSONL item file")
    lengths.add_argument("--field", default="ast", help="top-level field containing each item")
    lengths.add_argument("--source-format", choices=("ast", "ve"), default="ast")
    lengths.add_argument("--naming", choices=NAMING_POLICIES, default="per_statement")
    lengths.add_argument("--without-legend", action="store_true", help="measure claim text alone")
    lengths.add_argument("--legend-style", choices=LEGEND_STYLES, default="json")
    for command in ("parse", "format", "render", "evaluate", "check", "import-fol", "countermodel"):
        sub = commands.add_parser(command)
        sub.add_argument("--env", required=True, help="environment JSON file")
        sub.add_argument("--english-vocabulary", help="display-only English vocabulary overlay JSON")
        sub.add_argument("--accept-suggested-vocabulary", action="store_true",
                         help="explicitly accept unreviewed suggested wording")
        sub.add_argument("--surface", choices=("strict", "english"),
                         help="input language; omitted means strict input and English display")
        if command == "countermodel":
            sub.add_argument("--premises", help="VE document; omit for no premises")
            sub.add_argument("--conclusion", required=True, help="exactly one VE statement")
            sub.add_argument("--max-domain-size", type=int, default=2)
            sub.add_argument("--min-domain-size", type=int, default=0)
            sub.add_argument("--nonempty-domains", action="store_true")
            sub.add_argument("--nonvacuous-for", help="VE formula whose quantifiers and implications must be non-vacuous")
            sub.add_argument("--semantic-nonvacuity", action="store_true",
                             help="also require jointly satisfiable clause guards under universals; requires --nonvacuous-for")
            sub.add_argument("--max-models", type=int, default=10_000)
        else:
            sub.add_argument("source", help="VE source or, for import-fol, FOL JSON; '-' reads stdin")
        if command in ("render", "import-fol"):
            sub.add_argument("--view", choices=("fol_symbols", "fol_keywords", "ve_strict", "ve_natural", "ve_fluent", "ve_english",
                                                 "canonical", "natural"), default=None)
            sub.add_argument("--with-legend", action="store_true", help="include the shared vocabulary legend")
            sub.add_argument("--legend-style", choices=LEGEND_STYLES, default="json",
                             help="vocabulary legend format (used with --with-legend)")
            sub.add_argument("--naming", choices=NAMING_POLICIES, default="per_statement")
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
        if args.command == "suggest-vocabulary":
            from . import suggest_vocabulary
            _emit(suggest_vocabulary(env))
            return 0
        if args.command == "view-lengths":
            _emit(measure_jsonl_lengths(args.source, env, field=args.field,
                                       source_format=args.source_format, naming=args.naming,
                                       include_vocabulary=not args.without_legend, style=args.legend_style))
            return 0
        if args.command == "grammar":
            from .grammar import export_grammar, structured_output_spec
            options = dict(dialect=args.dialect, mode=args.mode, max_binder_depth=args.max_binder_depth,
                           max_binders=args.max_binders, max_rules=args.max_rules)
            if args.spec:
                _emit(structured_output_spec(env, **options))
            else:
                print(export_grammar(env, wrapper=args.wrapper, **options), end="")
            return 0
        from .english import EnglishVocabulary
        from . import suggest_vocabulary
        vocabulary = loads_json(_read(args.english_vocabulary)) if args.english_vocabulary else None
        if vocabulary is None and args.accept_suggested_vocabulary:
            vocabulary = suggest_vocabulary(env)
        english_options = dict(vocabulary=vocabulary, accept_suggested_vocabulary=args.accept_suggested_vocabulary)
        EnglishVocabulary(env, **english_options)  # Validate even when the selected output is strict.
        surface = args.surface or "strict"
        display_view = "ve_strict" if args.surface == "strict" else "ve_english"
        if hasattr(args, "view") and args.view is None:
            args.view = "ve_strict" if args.command == "import-fol" else display_view
        paraphrases = {}

        def read_document(path):
            source = _read(path, MAX_SOURCE_BYTES)
            if surface == "english":
                from .english import parse_english_with_metadata
                parsed = parse_english_with_metadata(env, source, **english_options)
                paraphrases[path] = parsed.paraphrase()
                return parsed.document
            return parse(env, source)

        if args.command == "countermodel":
            premises = read_document(args.premises).formulas if args.premises else ()
            conclusion = read_document(args.conclusion)
            if len(conclusion.formulas) != 1:
                raise VEError("A claimed entailment requires exactly one conclusion statement")
            nonvacuous = None
            if args.nonvacuous_for:
                document = read_document(args.nonvacuous_for)
                if len(document.formulas) != 1:
                    raise VEError("--nonvacuous-for requires exactly one statement")
                nonvacuous = document.formulas[0]
            result = find_countermodel(env, premises, conclusion.formulas[0], max_domain_size=args.max_domain_size,
                                       min_domain_size=args.min_domain_size,
                                       nonempty_domains=args.nonempty_domains, nonvacuous_for=nonvacuous,
                                       semantic_nonvacuity=args.semantic_nonvacuity,
                                       max_models=args.max_models, max_evaluations=args.max_evaluations)
            record = result.to_dict()
            record["conclusion_text"] = render(conclusion, env, display_view, **english_options)
            if paraphrases:
                record["paraphrases"] = paraphrases
            _emit(record)
            return 0 if result.status == "Found" else (3 if result.status == "NotFound" else 4)
        if args.command == "import-fol":
            document = document_from_named_fol(env, loads_json(_read(args.source)))
            if args.view == "natural" and not args.with_legend:
                _emit(natural_document(env, document, naming=args.naming).to_dict())
                return 0
            view = {"canonical": "ve_strict", "natural": "ve_natural"}.get(args.view, args.view)
            renderer = render_cell if args.with_legend else render
            options = dict(english_options, **({"style": args.legend_style} if args.with_legend else {}))
            print(renderer(document, env, view, args.naming, **options), end="")
            return 0
        source = _read(args.source, MAX_SOURCE_BYTES)
        if args.command in ("check", "evaluate", "parse"):
            model = FiniteModel.from_json(env, _read(args.model)) if getattr(args, "model", None) else None
            candidate = (doc_from_json(env, _read(args.candidate_ast))
                         if getattr(args, "candidate_ast", None) else None)
            record = check(env, source, model, candidate_ast=candidate,
                           max_evaluations=getattr(args, "max_evaluations", 1_000_000),
                           trace=not getattr(args, "no_trace", False), surface=surface, **english_options)
            from .ast import document_from_data
            record["display_text"] = render(document_from_data(env, record["ast"]), env, display_view, **english_options)
            _emit(record)
            if model is None:
                return 0
            return {"Satisfied": 0, "Violated": 1, "ResourceLimit": 4}[record["evaluation"]["status"]]
        if surface == "english":
            from .english import parse_english_with_metadata
            parsed = parse_english_with_metadata(env, source, **english_options)
            document = parsed.document
            if parsed.paraphrase()["changed"]:
                print(json.dumps({"paraphrase": parsed.paraphrase()}, ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            document = parse(env, source)
        if args.command == "render":
            if args.view == "natural" and not args.with_legend:
                _emit(natural_document(env, document, naming=args.naming).to_dict())
                return 0
            view = {"canonical": "ve_strict", "natural": "ve_natural"}.get(args.view, args.view)
            renderer = render_cell if args.with_legend else render
            options = dict(english_options, **({"style": args.legend_style} if args.with_legend else {}))
            print(renderer(document, env, view, args.naming, **options), end="")
        else:
            print(print_document(env, document), end="")
        return 0
    except VEError as exc:
        _emit({"status": "ResourceLimit" if exc.code == "ResourceLimit" else "InvalidInput", "error": exc.to_dict()})
        return 4 if exc.code == "ResourceLimit" else 2
    except (OSError, ValueError) as exc:
        _emit({"status": "InvalidInput", "error": {"code": "InvalidInput", "message": str(exc)}})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
