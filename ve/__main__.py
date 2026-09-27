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
    argv = sys.argv[1:] if argv is None else list(argv)
    if argv[:1] == ["assist"]:
        from .assist.cli import main as assist_main
        return assist_main(argv[1:])
    if argv[:2] == ["adapter", "run"]:
        from .adapters.cli import main as adapter_main
        return adapter_main(argv[2:])
    if argv[:1] == ["bundle"]:
        if argv[:2] != ["bundle", "check"]:
            print("usage: python -m ve bundle check BUNDLE [--lean EXECUTABLE]", file=sys.stderr)
            return 2
        bundle_parser = argparse.ArgumentParser(prog="python -m ve bundle check")
        bundle_parser.add_argument("bundle", help="ve-bundle@0 JSON file")
        bundle_parser.add_argument("--lean", help="optional Lean ve_conformance executable")
        options = bundle_parser.parse_args(argv[2:])
        try:
            from .bundle import check_bundle
            _emit(check_bundle(loads_json(_read(options.bundle)), lean_executable=options.lean))
            return 0
        except VEError as exc:
            _emit({"status": "InvalidInput", "error": exc.to_dict()})
            return 2
    if argv[:1] == ["definitions"]:
        definition_parser = argparse.ArgumentParser(prog="python -m ve definitions")
        definition_parser.add_argument("--env", required=True)
        definition_parser.add_argument(
            "--adopt", help="English definition and glossary sentences; prints the new environment version")
        options = definition_parser.parse_args(argv[1:])
        try:
            from .surface.definitions import adopt, wordings
            if options.adopt:
                raw = adopt(loads_json(_read(options.env)), _read(options.adopt).decode("utf-8"))
                env = Environment(raw)
                _emit({"environment_id": env.environment_id, "environment": raw,
                       "definitions": wordings(env)})
                return 0
            env = Environment.from_json(_read(options.env))
            _emit({"environment_id": env.environment_id, "definitions": wordings(env)})
            return 0
        except VEError as exc:
            _emit({"status": "InvalidInput", "error": exc.to_dict()})
            return 2
    if argv[:1] == ["document"]:
        from .document import main as document_main
        return document_main(argv[1:])
    parser = argparse.ArgumentParser(prog="python -m ve", description="Experimental VE v0 language checking")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("assist", help="interactive assisted formalisation (python -m ve assist --help)")
    commands.add_parser("bundle", help="check a lemma bundle (python -m ve bundle check --help)")
    commands.add_parser("definitions", help="preview definition wordings; --adopt English definitions and glossaries")
    commands.add_parser("document", help="document check, render, coverage and readings")
    proposal = commands.add_parser("propose", help="preview new unary English vocabulary; never adopt implicitly")
    proposal.add_argument("--env", required=True)
    proposal.add_argument("--english-vocabulary")
    proposal.add_argument("--acknowledge", action="append", default=[], metavar="SYMBOL",
                          help="acknowledge a flagged existing near-duplicate; repeat for each symbol")
    proposal.add_argument("--adopt-to", help="explicitly adopt into a new directory after all acknowledgements")
    proposal.add_argument("--output", help="new directory for wrapped candidate files")
    proposal.add_argument("text", help="English sentence text, or '-' to read stdin")
    adoption = commands.add_parser("adopt", help="explicitly adopt a vocabulary proposal")
    adoption.add_argument("proposal", help="proposal.json from ve propose")
    adoption.add_argument("--output", required=True, help="new directory for adopted files")
    adoption.add_argument("--acknowledge", action="append", default=[], metavar="SYMBOL")
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
                         help="input language; render defaults to the canonical strict view")
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
            sub.add_argument("--view", choices=("fol_symbols", "fol_keywords", "ve_strict", "ve_explicit", "ve_natural", "ve_fluent", "ve_english",
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
        if args.command == "adopt":
            from .propose import adopt
            _emit(adopt(loads_json(_read(args.proposal)), args.output, acknowledge=args.acknowledge))
            return 0
        env = Environment.from_json(_read(args.env))
        if args.command == "propose":
            from .propose import adopt, propose, write_proposal
            vocabulary = loads_json(_read(args.english_vocabulary)) if args.english_vocabulary else None
            source = _read("-", MAX_SOURCE_BYTES) if args.text == "-" else args.text
            preview = propose(env, source, vocabulary, acknowledge=args.acknowledge)
            if preview['requires_acknowledgement']:
                _emit(preview)
                return 2
            if args.output:
                write_proposal(preview, args.output)
            if args.adopt_to:
                _emit(adopt(preview, args.adopt_to, acknowledge=args.acknowledge))
            else:
                _emit(preview)
            return 0
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
        from . import suggest_vocabulary
        from .english_vocabulary import overlay_provenance
        surface = args.surface or "strict"
        display_view = "ve_strict" if args.surface == "strict" else "ve_english"
        if hasattr(args, "view") and args.view is None:
            args.view = "ve_english" if args.command == "render" and args.surface == "english" else "ve_strict"

        def load_english_options():
            vocabulary = loads_json(_read(args.english_vocabulary)) if args.english_vocabulary else None
            if vocabulary is None and args.accept_suggested_vocabulary:
                vocabulary = suggest_vocabulary(env)
            return (dict(vocabulary=vocabulary, accept_suggested_vocabulary=args.accept_suggested_vocabulary),
                    overlay_provenance(vocabulary))

        defer_display_options = surface == "strict" and args.command in ("check", "evaluate", "parse", "countermodel")
        english_options, provenance = ({}, {}) if defer_display_options else load_english_options()
        if (surface == "english" or getattr(args, "view", None) == "ve_english") and provenance.get("overlay_digest"):
            print(json.dumps(provenance), file=sys.stderr)
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
            try:
                if defer_display_options:
                    english_options, provenance = load_english_options()
                record["conclusion_text"] = render(conclusion, env, display_view, **english_options)
                record.update(provenance)
            except Exception as exc:
                record["display_omitted"] = type(exc).__name__
            if paraphrases:
                record["paraphrases"] = paraphrases
                record.update(provenance)
            _emit(record)
            return 0 if result.status == "Found" else (3 if result.status == "NotFound" else 4)
        if args.command == "import-fol":
            document = document_from_named_fol(env, loads_json(_read(args.source)))
            if args.view == "natural" and not args.with_legend:
                _emit(natural_document(env, document, naming=args.naming, **english_options).to_dict())
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
            # Display is outside the trusted verdict path, including vocabulary
            # validation and unexpected renderer failures.
            try:
                if defer_display_options:
                    english_options, provenance = load_english_options()
                conclusions = record.get("conclusions", ())
                view = "ve_natural" if conclusions else display_view
                display = render(document_from_data(env, record["ast"]), env, view,
                                 conclusions=conclusions, **english_options)
                record.update(display_text=display, **provenance)
            except Exception as exc:
                record["display_omitted"] = type(exc).__name__
            _emit(record)
            if model is None:
                return 0
            return {"Satisfied": 0, "Violated": 1, "ResourceLimit": 4}[record["evaluation"]["status"]]
        if surface == "english":
            from .english import parse_english_with_metadata
            parsed = parse_english_with_metadata(env, source, **english_options)
            document = parsed.document
            conclusions = parsed.conclusions
            if parsed.paraphrase()["changed"]:
                print(json.dumps({"paraphrase": parsed.paraphrase()}, ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            document = parse(env, source)
            conclusions = ()
        if args.command == "render":
            if args.view == "natural" and not args.with_legend:
                _emit(natural_document(env, document, naming=args.naming,
                                       conclusions=conclusions, **english_options).to_dict())
                return 0
            view = {"canonical": "ve_strict", "natural": "ve_natural"}.get(args.view, args.view)
            renderer = render_cell if args.with_legend else render
            options = dict(english_options, conclusions=conclusions,
                           **({"style": args.legend_style} if args.with_legend else {}))
            print(renderer(document, env, view, args.naming, **options), end="")
        else:
            if conclusions:
                raise ValueError('Format cannot export English conclusion roles to strict VE')
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
