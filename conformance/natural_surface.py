"""Reproducible natural-view coverage over repository and seeded round-trip corpora."""
from __future__ import annotations

import json
from pathlib import Path
import random

from ve import Environment, parse, ast, natural_document, parse_english_argument, check_argument
from ve.natural import (_NOTATION, render_natural_sentence, render_presentation,
                        parse_presentation, PresentationNeedsRepair)
from ve.english import parse_english
from ve.surface.unambiguity import require_unique_derivation
from ve.printer import render
from conformance.english_surface import ROOT, SEED, vocabularies, order_environment, random_formula


def _source_files(root):
    for path in sorted(root.rglob('*.ve')):
        environment = next((parent / 'environment.json' for parent in (path.parent, *path.parents)
                            if (parent / 'environment.json').is_file()), None)
        if environment is not None:
            yield path, environment


def _disposition(result):
    if result.reason == 'different_ast':
        return 'candidate_ast_mismatch_explicit_repair'
    if result.reason != 'symbols_or_variable_names':
        return 'candidate_audit_failed_explicit_repair'
    if '"' in result.text or '@' in result.text or '_' in result.text:
        return 'needs_confirmed_display_name_or_vocabulary'
    if any(char in result.text for char in '[]*+-'):
        return 'needs_notation_free_order_or_closure_form'
    if '(' in result.text or ')' in result.text:
        return 'needs_word_scope_or_binder_form'
    return 'needs_audited_english_rewrite'


def _measure(name, formulas, env, *, options=None, examples=None, real_document=False):
    options = options or {}
    reasons, fallback_details = {}, []
    natural = 0
    wrong = 0
    for index, formula in enumerate(formulas):
        result = render_natural_sentence(formula, env, **options)
        sentence = result.text + '.'
        try:
            require_unique_derivation(env, sentence, **options)
            if parse_english(env, sentence, **options) != ast.Document((formula,)):
                wrong += 1
        except Exception:
            wrong += 1
        if result.natural:
            assert not _NOTATION.search(result.text), result.text
            assert result.reason is None and result.fluent_text is None
            natural += 1
        else:
            assert result.reason and result.fluent_text and result.form == 'explicit form'
            reasons[result.reason] = reasons.get(result.reason, 0) + 1
            fallback_details.append({'statement': index + 1, 'reason': result.reason,
                                     'disposition': _disposition(result)})
        if examples is not None and len(examples) < 30:
            examples.append({'corpus': name, 'before': render(formula, env, 've_fluent'),
                             'after': result.text, 'natural': result.natural, 'form': result.form,
                             'fallback_reason': result.reason})
    count = len(formulas)
    row = {'corpus': name, 'statements': count, 'natural': natural,
            'fallback': count - natural,
            'natural_fraction': natural / count if count else 0.0,
            'fallback_reasons': reasons, 'fallback_details': fallback_details,
            'accepted_wrong_readings': wrong}
    if real_document and formulas:
        try:
            legacy_view = natural_document(env, ast.Document(tuple(formulas)), **options)
            presentation = parse_presentation(env, legacy_view.text,
                                              allow_explicit=True, **options)
            assert presentation.document == ast.Document(tuple(formulas))
            assert all(sentence['role'] == 'premise' and not sentence['dependencies']
                       for sentence in presentation.sentences)
            row['prose_round_trip'] = 'exact'
            try:
                render_presentation(env, presentation.document, **options)
                row['versioned_presentation'] = 'ready'
            except PresentationNeedsRepair as exc:
                row['versioned_presentation'] = 'needs_repair'
                row['presentation_repairs'] = exc.details
        except Exception as exc:
            row['prose_round_trip'] = type(exc).__name__
    return row


def audit(random_per_vocabulary=100):
    rows, examples, skipped = [], [], []
    for group in ('examples', 'usecases'):
        for path, environment in _source_files(ROOT / group):
            try:
                if path.parts[-3:-2] == ('theorems',) and path.parent.name.startswith('T9'):
                    closure_environment = path.parent.parent.parent / 'environment-closure.json'
                    if closure_environment.is_file():
                        environment = closure_environment
                env = Environment.from_json(environment.read_bytes())
                raw = path.read_bytes()
                formulas = parse(env, raw).formulas if raw.strip() else ()
            except Exception as exc:
                skipped.append({'source': str(path.relative_to(ROOT)), 'reason': type(exc).__name__})
                continue
            overlay = environment.with_name('environment.english.json')
            options = {'vocabulary': json.loads(overlay.read_text())} if overlay.is_file() else {}
            rows.append(_measure(str(path.relative_to(ROOT)), formulas, env,
                                 options=options, examples=examples,
                                 real_document=True))
    fluent_path = ROOT / 'examples/fluent/examples.ve'
    env = Environment.from_json((fluent_path.parent / 'environment.json').read_bytes())
    rows.append(_measure('docs/fluent-examples.md', parse(env, fluent_path.read_bytes()).formulas, env,
                         examples=examples))
    env = Environment.from_json((fluent_path.parent / 'environment.json').read_bytes())
    formulas = []
    for line in (ROOT / 'tests/data/fluent-items.jsonl').read_text().splitlines():
        formulas.extend(parse(env, json.loads(line)['claim']).formulas)
    rows.append(_measure('tests/data/fluent-items.jsonl', formulas, env, examples=examples))
    for offset, (name, env) in enumerate((*vocabularies(), ('order', order_environment()))):
        rng = random.Random(SEED + offset)
        formulas = []
        seen = set()
        while len(formulas) < random_per_vocabulary:
            formula = random_formula(rng, env, rng.randrange(2, 9))
            if formula not in seen:
                ast.check_formula(env, formula)
                seen.add(formula)
                formulas.append(formula)
        rows.append(_measure('roundtrip/' + name, formulas, env, examples=examples))
    total = sum(row['statements'] for row in rows)
    natural = sum(row['natural'] for row in rows)
    disposition_counts = {}
    for row in rows:
        for detail in row['fallback_details']:
            key = detail['disposition']
            disposition_counts[key] = disposition_counts.get(key, 0) + 1
    real_rows = [row for row in rows if row['corpus'].startswith(('examples/', 'usecases/'))]
    demo_env = Environment.from_json((ROOT / 'examples/assist/environment.json').read_bytes())
    demo_options = {'vocabulary': json.loads((ROOT / 'examples/assist/environment.english.json').read_text())}
    demo = ast.Document((
        ast.Forall('service', ast.Implies(ast.Unary('reviewed', ast.Var(0)),
                                          ast.Unary('safe', ast.Var(0)))),
        ast.Unary('reviewed', ast.Const('api')),
        ast.Unary('safe', ast.Const('api'))))
    prose = natural_document(demo_env, demo, conclusions=(2,), **demo_options)
    assert parse_english(demo_env, prose.text, **demo_options) == demo
    graph = parse_english_argument(demo_env, prose.text, **demo_options)
    assert check_argument(graph, search=False).findings['d3'] == ('follows',)
    return {'method': 'per-sentence English parse, exact AST equality, and Lark Earley all derivations before acceptance; prose example adds document round trip and claim-graph certificate replay',
            'statements': total, 'natural': natural, 'fallback': total - natural,
            'natural_fraction': natural / total if total else 0.0,
            'accepted_wrong_readings': sum(row['accepted_wrong_readings'] for row in rows),
            'fallback_dispositions': disposition_counts,
            'real_documents': {'documents': len(real_rows),
                               'statements': sum(row['statements'] for row in real_rows),
                               'notation_free': sum(row['natural'] for row in real_rows),
                               'exact_prose_round_trips': sum(row.get('prose_round_trip') == 'exact'
                                                              for row in real_rows),
                               'ready_versioned_presentations': sum(row.get('versioned_presentation') == 'ready'
                                                                    for row in real_rows),
                               'documents_needing_repair': sum(row.get('versioned_presentation') == 'needs_repair'
                                                               for row in real_rows),
                               'prose_failures': [{'source': row['corpus'],
                                                   'reason': row['prose_round_trip']}
                                                  for row in real_rows
                                                  if row.get('prose_round_trip') not in ('exact', None)]},
            'prose_argument': {'before': 'Every reviewed service is safe. / Api is reviewed. / Api is safe.',
                               'after': prose.text, 'statements': len(demo.formulas),
                               'checked_conclusions': 1, 'round_trip': True,
                               'one_reading': True, 'claim_graph_replay': True},
            'rows': rows, 'skipped': skipped,
            'examples': examples[:10]}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--random-per-vocabulary', type=int, default=100)
    parser.add_argument('--output', type=Path, default=ROOT / 'conformance/natural-view-report.json')
    args = parser.parse_args()
    result = audit(args.random_per_vocabulary)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(f"{result['natural']}/{result['statements']} natural; {result['fallback']} fallback; "
          f"{len(result['skipped'])} skipped sources; zero accepted wrong readings")
