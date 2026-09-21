"""Regenerate reviewed examples and use-case English documents, without changing environments."""
from copy import deepcopy
import json
from pathlib import Path

from ve import ast, Environment, parse, render
from ve.english import english_legend, parse_english
from .english_surface import ROOT, lint_report


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
        '', f"**{report['roundtrips']:,} random well-typed environment/AST pairs** round-tripped through the public",
        '`render` and `parse_english` APIs across ten vocabularies. Each vocabulary',
        'contributed 5,000 distinct ASTs; duplicate generator draws are counted separately',
        'in [the committed report](../conformance/english-surface-report.json).',
        f"**{report['earley_texts']:,} rendered environment/text pairs** (500 distinct texts per vocabulary) had exactly one",
        'Earley derivation, with zero ambiguity nodes. The sample includes closure,',
        'duplicate aliases, structural function words in nouns and verbs, structural',
        'identifiers/constants, expanded templates, and all four real vocabularies.',
        'Seeds, environment IDs, corpus hashes, grammar hashes, and constructor counts',
        'are recorded. Counts are environment-indexed; simple formulas can recur in',
        'different vocabularies. This sample is not a uniform distribution over all ASTs.',
        '',
        f"All **{report['identity_fixtures']} existing identity fixtures** have an additional English",
        'transport regression: English round trip preserves their strict bytes and',
        'stored environment/meaning IDs. The original fixture regression still checks',
        'all preimages, model IDs, and formula IDs. Minimal pairs test quantifier order,',
        'argument reversal, scope, and/or, implication reversal, dropped conjuncts,',
        'moved negation, and guard versus consequent.',
        '',
        '| Current use-case environment | Predicates | Declared templates | Accepted before | Accepted after | Missing metadata |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for row in report['linter']:
        lines.append(f"| {row['usecase']} | {row['predicates']} | {row['declared_templates']} | {row['accepted_before']} | {row['accepted_after']} | {len(row['missing_templates'])} |")
    before = sum(r['accepted_before'] for r in report['linter'])
    after = sum(r['accepted_after'] for r in report['linter'])
    lines += ['', f'In total: **{before}/13 before, {after}/13 after**. Forty of the 53 predicates',
              'have no declared template in the current integration files. Their absence',
              'is not a rejection and is not counted as an accepted template. The old',
              '`rendered.md` snapshots are not a substitute for current environment JSON.',
              'No environment was edited to improve these numbers or its identities.', '',
              'Still rejected:', '']
    reasons = {
        'citizen_of_state': 'Binary copula with a nominal complement; no validated active argument-order template is declared.',
        'within_jurisdiction_of': 'Binary copula with a prepositional complement; outside the active-relation grammar.',
        'abridges_priv_or_imm': 'Contains a lexical coordination using “or”; the linter does not decide whether this is an atomic idiom or a disjunction.',
        'deprives': 'Places extra coordinated, punctuated content after the second argument; unsupported placeholder shape.',
    }
    for row in report['linter']:
        for rejected in row['still_rejected']:
            n = rejected['predicate']
            lines.append(f"- `{n}` — `{rejected['template']}`. {reasons.get(n, 'Outside the finite lexical grammar.')} Codes: {', '.join(rejected['codes'])}.")
    lines += ['', 'Missing template identifiers (all retained explicitly in the report and legends):', '']
    for row in report['linter']:
        if row['missing_templates']:
            lines.append(f"- {row['usecase']}: " + ', '.join('`' + n + '`' for n in row['missing_templates']) + '.')
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
    for path in sorted((ROOT / 'usecases').glob('*/environment.json')):
        env = Environment.from_json(path.read_bytes())
        source = path.with_name('claims.ve')
        document = parse(env, source.read_bytes())
        english = render(document, env, 've_english')
        assert parse_english(env, english) == document
        command = (f'UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \\\n'
                   f'  --env {path.relative_to(ROOT)} --view ve_english \\\n'
                   f'  {source.relative_to(ROOT)}')
        text = ('# English rendering\n\nGenerated from the unchanged environment and strict claims. '
                'Quoted predicate names indicate missing or rejected lexical metadata.\n\n'
                '```sh\n' + command + '\n```\n\n## Statements\n\n```text\n' + english
                + '```\n\n## Vocabulary and scope legend\n\n```text\n' + english_legend(env, 'compact') + '```\n')
        path.with_name('rendered-english.md').write_text(text)


if __name__ == '__main__':
    artifacts()
    print('Regenerated 25 worked examples and four English use-case documents; all parsed back unchanged.')
