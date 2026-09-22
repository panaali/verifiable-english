"""Regenerate reviewed examples and use-case English documents, without changing environments."""
import json

from ve import ast, Environment, parse, render
from ve.english import english_legend, parse_english
from .english_surface import ROOT


def examples():
    data = json.loads((ROOT / 'examples/fluent/environment.json').read_text())
    data.pop('profile')
    data.update(language='ve.core@0.1', profiles=['closure@0', 'relational-fol@0'],
                spec_revision='ve-v0.1-closure-2026-09-21')
    data['vocabulary']['predicates'].update({
        'audits': {'arguments': ['person', 'service'], 'description': 'Person audits service, in that order.',
                   'verbalisation': '{0} audits {1}'},
        'links': {'arguments': ['service', 'service'], 'description': 'Directed dependency.',
                  'verbalisation': '{0} depends on {1}'}})
    env = Environment(data)
    p = ast.Unary('deployed', ast.Const('legacy'))
    q = ast.Unary('reviewed', ast.Const('legacy'))
    px, qx = ast.Unary('deployed', ast.Var(0)), ast.Unary('reviewed', ast.Var(0))
    owns = ast.Binary('owns', ast.Var(0), ast.Var(1))
    cases = [
        ('Simple universal', ast.Forall('service', qx)),
        ('Relative guard', ast.Forall('service', ast.Implies(px, qx))),
        ('A potentially different owner per service', ast.Forall('service', ast.Implies(px, ast.Exists('person', owns)))),
        ('One owner before the service quantifier', ast.Exists('person', ast.Forall('service', ast.Implies(px, ast.Binary('owns', ast.Var(1), ast.Var(0)))))),
        ('Guard versus consequence', ast.Forall('person', ast.Forall('service', ast.Implies(ast.Binary('owns', ast.Var(1), ast.Var(0)), ast.Binary('audits', ast.Var(1), ast.Var(0)))))),
        ('Existential relative', ast.Exists('service', px)),
        ('Named constants', ast.Binary('owns', ast.Const('alice'), ast.Const('legacy'))),
        ('Validated negative', ast.Not(q)),
        ('Negative consequence', ast.Forall('service', ast.Implies(px, ast.Not(qx)))),
        ('Negated existential', ast.Not(ast.Exists('service', ast.And(px, ast.Not(qx))))),
        ('Two entities of the same sort', ast.Forall('person', ast.Exists('person', ast.Eq(ast.Var(1), ast.Var(0))))),
        ('Ordered relation arguments', ast.Forall('service', ast.Exists('service', ast.Binary('links', ast.Var(1), ast.Var(0))))),
        ('Reversed relation arguments', ast.Forall('service', ast.Exists('service', ast.Binary('links', ast.Var(0), ast.Var(1))))),
        ('Simple conjunction', ast.And(p, q)),
        ('Inclusive disjunction', ast.Or(p, q)),
        ('Simple conditional', ast.Implies(p, q)),
        ('Negation moved outside a conjunction', ast.Not(ast.And(p, q))),
        ('Left-associated conjunction', ast.And(ast.And(p, q), p)),
        ('Right-associated conjunction', ast.And(p, ast.And(q, p))),
        ('Mixed conjunction and disjunction', ast.Or(ast.And(p, q), ast.Not(p))),
        ('Exception remains inside the guard', ast.Forall('service', ast.Implies(ast.And(px, ast.Not(ast.Eq(ast.Var(0), ast.Const('legacy')))), qx))),
        ('Negated universal', ast.Not(ast.Forall('service', ast.Implies(px, qx)))),
        ('Deeply nested provisions', ast.Implies(ast.Or(ast.And(p, ast.Not(q)), ast.Forall('service', ast.Implies(px, qx))), ast.And(ast.Exists('person', ast.Forall('service', ast.Binary('owns', ast.Var(1), ast.Var(0)))), ast.Not(ast.Or(p, q))))),
        ('One or more named steps', ast.Forall('service', ast.Reach('plus', ast.Named('links'), ast.Var(0), ast.Const('legacy')))),
        ('Scoped step definition and a third entity', ast.Forall('service', ast.Reach('star', ast.Body('service', ast.And(ast.Binary('links', ast.Var(1), ast.Var(0)), ast.Not(ast.Eq(ast.Var(0), ast.Var(2))))), ast.Var(0), ast.Const('legacy')))),
    ]
    return env, cases


def generated_documentation():
    report = json.loads((ROOT / 'conformance/english-surface-report.json').read_text())
    lines = [
        '', f"**{report['roundtrips']:,} distinct well-typed environment/AST pairs** round-tripped through",
        '`render` and `parse_english`, across sixteen configurations (the original ten,',
        'four reviewed overlays, accepted suggestions, and an adopted unary vocabulary). Each configuration',
        'contributed 5,000 distinct ASTs: directed boundary cases followed by seeded random',
        'draws. Directed cases cover every template, validated negatives, subject and object relatives, two-atom guards,',
        'both three-atom associations, deeper/mixed guards, nested implications, and the',
        'actual use-case claims. Duplicate draws are recorded, not counted twice.',
        f"**{report['earley_texts']:,} environment/text pairs** (500 per configuration) had exactly one",
        'Earley dynamic-complete derivation, with zero ambiguity nodes. Every directed',
        'case is in that directed-heavy prefix of each configuration; it is **not a random sample**.',
        f"A separate seeded random sample adds **{report['random_earley_texts']:,} texts**",
        '(250 per configuration), all at measured AST depths 6–9, each with exactly one',
        'all-derivations parse and an exact AST round trip. It excludes the original corpus.',
        f"Another **{report['multi_statement_documents']:,} five-statement documents** round-trip",
        'and have exactly one all-derivations parse using the document grammar.',
        'This is finite evidence, not a universal unambiguity proof.',
        'The report records seeds, corpus/grammar hashes, overlay digests, constructor',
        'counts, and all original environment IDs. Counts are configuration-indexed;',
        'the same text may appear under different vocabularies.',
        '', f"All **{report['identity_fixtures']} original identity fixtures** retain English transport checks.",
        'Original environment JSON, strict claims, identities, and historical views remain unchanged.',
        '', '| Use case | Predicates | Original declared wording | Accepted original wording | Reviewed overlay wording | Overlay lint issues |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for row in report['linter']:
        lines.append(f"| {row['usecase']} | {row['predicates']} | {row['declared_templates']} | {row['accepted_after']} | {row['reviewed_templates']} | {len(row['reviewed_lint'])} |")
    lines += ['', 'The overlays supply reviewed wording for **all 53 predicates**, including the',
              '40 originally missing templates. Finite lexical idioms also cover the four',
              'previously rejected constitutional templates. The original declarations are',
              'still visible alongside the selected wording in each artifact legend.',
              '', '### Ten actual use-case sentences: before and after', '',
              'The baseline text and commit are stored in `conformance/english-before-after.json`.',
              'Each after-text is generated from the same strict claim and parsed back unchanged.', '']
    baseline = json.loads((ROOT / 'conformance/english-before-after.json').read_text())
    for item in baseline['sentences']:
        path = ROOT / 'usecases' / item['usecase'] / 'environment.json'
        env = Environment.from_json(path.read_bytes())
        overlay = json.loads(path.with_name('environment.english.json').read_text())
        formula = parse(env, path.with_name('claims.ve').read_bytes()).formulas[item['statement'] - 1]
        doc = ast.Document((formula,))
        after = render(doc, env, 've_english', vocabulary=overlay)
        assert parse_english(env, after, vocabulary=overlay) == doc
        lines += [f"#### {item['usecase']}, statement {item['statement']}", '',
                  'Before:', '', '```text', item['before'], '```', '',
                  'After:', '', '```text', after.rstrip(), '```', '']
    env, cases = examples()
    lines += ['', '### Twenty-five worked examples', '',
              'The example vocabulary is reproducible through `conformance.english_artifacts.examples()`.',
              'It extends the existing fluent vocabulary with active `audits` and `depends on`',
              'templates and enables closure. Each block is generated from the **same AST**;',
              'all 25 English blocks are parsed back during generation.', '']
    for i, (title, formula) in enumerate(cases, 1):
        lines += [f'#### {i}. {title}', '']
        for view, title in [('ve_strict', 'Strict'), ('ve_fluent', 'Fluent'), ('ve_english', 'English')]:
            text = render(ast.Document((formula,)), env, view)
            if view == 've_english': assert parse_english(env, text) == ast.Document((formula,))
            lines += [title + ':', '', '```text', text.rstrip(), '```', '']
    return '\n'.join(lines)


def artifacts():
    generated = generated_documentation()
    doc_path = ROOT / 'docs/english-surface.md'
    marker = '<!-- BEGIN GENERATED ENGLISH EVIDENCE -->'
    doc_path.write_text(doc_path.read_text().split(marker)[0] + marker + '\n' + generated)
    for path in sorted(p.with_name('environment.json') for p in (ROOT / 'usecases').glob('*/claims.ve')):
        env = Environment.from_json(path.read_bytes())
        source = path.with_name('claims.ve')
        document = parse(env, source.read_bytes())
        overlay = json.loads(path.with_name('environment.english.json').read_text())
        english = render(document, env, 've_english', vocabulary=overlay)
        assert parse_english(env, english, vocabulary=overlay) == document
        command = (f'UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \\\n'
                   f'  --env {path.relative_to(ROOT)} --view ve_english \\\n'
                   f'  --english-vocabulary {path.with_name("environment.english.json").relative_to(ROOT)} \\\n'
                   f'  {source.relative_to(ROOT)}')
        text = ('# English rendering\n\nGenerated from the unchanged environment and strict claims. '
                'The reviewed display-only overlay has its own digest in the legend; it does not change environment or meaning identity.\n\n'
                '```sh\n' + command + '\n```\n\n## Statements\n\n```text\n' + english
                + '```\n\n## Vocabulary and scope legend\n\n```text\n' + english_legend(env, 'compact', vocabulary=overlay) + '```\n')
        path.with_name('rendered-english.md').write_text(text)


if __name__ == '__main__':
    artifacts()
    print('Regenerated 25 worked examples and four English use-case documents; all parsed back unchanged.')
