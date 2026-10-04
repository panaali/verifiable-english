"""Merge gates for the two English correspondence harnesses."""
import dataclasses
import json
from pathlib import Path
import shutil
import warnings

import pytest

from ve import ast
from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning, parse_english
from ve.errors import SyntaxError
from conformance import english_lean, english_mixed
from conformance.english_surface import configurations
from ve.surface.registry import SurfaceRecord

ROOT = Path(__file__).resolve().parents[1]


def require_lean_build():
    assert shutil.which('lake'), 'lake must be on PATH'
    assert (ROOT / 'lean/.lake/build/lib/lean/VE/English/Run.olean').exists(), \
        'Run lake build before the English evidence tests'


# A harness's `pairs` and `texts` count the documents it generated, not the round trips it
# completed; a run that skips its comparisons still reports them. Each gate below checks the
# completed round trips against the corpus instead.

# The constructors of Lean's core `Formula` and `Term` (`VE.Bridge.decodeFormula`, the
# decoder of the runner's cases). The harness's own classifier (`english_lean.v0_only`)
# decides which ASTs it renders and compares; the gates count the core ASTs with this
# separate walk, so a classifier that drops a constructor cannot lower the bar it is held to.
LEAN_CORE = (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq, ast.Not, ast.And, ast.Or,
             ast.Implies, ast.Forall, ast.Exists, ast.Var, ast.Const)


def nodes(value):
    """Every AST node in `value`, by walking dataclass fields (no per-constructor cases)."""
    if dataclasses.is_dataclass(value):
        yield value
        for field in dataclasses.fields(value):
            yield from nodes(getattr(value, field.name))
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from nodes(item)


def lean_core(formula):
    return all(type(node) in LEAN_CORE for node in nodes(formula))


def lean_corpus(per_vocabulary, only=None):
    """Each configuration's `english_lean` corpus, by name (or only the one named)."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
        return {name: english_lean.corpus(env, EnglishVocabulary(env, **options), name,
                                          per_vocabulary, offset)
                for offset, (name, env, options) in enumerate(configurations())
                if only in (None, name)}


def expected_core(per_vocabulary, only=None):
    """The core ASTs of each configuration's corpus, counted independently of the harness."""
    return {name: sum(map(lean_core, formulas))
            for name, formulas in lean_corpus(per_vocabulary, only).items()}


def lean_incomplete(report, expected):
    """The vocabularies of an `english_lean` report whose core ASTs, `expected` per
    configuration, did not all complete the round trip (Lean core render, then Python parse
    back to the AST; for an admitted lexicon, Lean's own round trip too), or whose
    comparisons did not run."""
    rows = report['vocabularies']
    problems = [] if sum(row.get('asts', 0) for row in rows) == report['pairs'] else ['pairs not compared']
    if not sum(row.get('python reads lean core text', 0) for row in rows):
        problems.append('no round trip')
    if [row['vocabulary'] for row in rows] != list(expected):
        problems.append('vocabularies')
    for row in rows:
        core = expected.get(row['vocabulary'])
        if row.get('status') != 'compared' or row.get('python reads lean core text', 0) != core or \
                (row['lean_admissible'] and row.get('lean core round trip', 0) != core):
            problems.append(row['vocabulary'])
    return problems


def mixed_round_trips(row):
    """The documents of an `english_mixed` row that rendered, parsed with one derivation and
    came back as the same AST."""
    return row.get('sentences', 0) + row.get('paragraphs', 0)


def test_core_classifier_and_missing_parse_mutation(monkeypatch):
    require_lean_build()
    name, env, options = next(configurations())
    words = EnglishVocabulary(env, **options)
    lex = english_lean.lexicon(env, words)
    assert english_lean.core_tokens(ast.Top(), lex) == \
        ['this', 'holds', 'in', 'all', 'cases', '.']
    monkeypatch.setattr(english_lean, 'configurations', lambda: iter([(name, env, options)]))
    monkeypatch.setattr(english_lean, 'corpus', lambda *_: [ast.Top()])
    real_runner = english_lean.run_lean

    def null_core_parse(payload):
        admitted, covers, results = real_runner(payload)
        results[0]['parsed'] = None
        return admitted, covers, results

    monkeypatch.setattr(english_lean, 'run_lean', null_core_parse)
    report = english_lean.differential(1)
    assert report['failure_count'] == 1
    assert report['failures'][0]['kind'] == 'missing core parse'


def test_shadowed_binder_rejected_by_both_parsers():
    require_lean_build()
    _, env, options = next(configurations())
    lex = english_lean.lexicon(env, EnglishVocabulary(env, **options))
    fixed = english_lean.fixtures(lex)
    cases = [{'tokens': tokens, 'formulas': [['top']]}
             for _, tokens, _ in fixed]
    admitted, covers, results = english_lean.run_lean({
        'environment': english_lean.environment(env), 'lexicon': lex, 'cases': cases})
    assert admitted and covers
    for (name, tokens, expected), result in zip(fixed, results, strict=True):
        assert result['parsed'] == expected, name
        if expected is None:
            with pytest.raises(SyntaxError):
                parse_english(env, english_lean.detokenize(tokens), **options)
        else:
            parsed = parse_english(env, english_lean.detokenize(tokens), **options)
            assert [english_lean.wire(f) for f in parsed.formulas] == expected
            assert english_lean.core_reading(parsed.formulas[0], tokens, lex)


def test_english_differential_merge_smoke():
    require_lean_build()
    report = english_lean.differential(5)
    assert report['failure_count'] == 0
    assert report['pairs'] == 85
    assert len(report['vocabularies']) == 17
    assert lean_incomplete(report, expected_core(5)) == []


def test_a_differential_that_skips_its_comparisons_is_incomplete(monkeypatch):
    """Review: a harness that generates its corpus but compares nothing reported the same
    counts. Every AST classified outside the core (so never rendered or compared) leaves
    the pairs and no failure, and `lean_incomplete` names it."""
    require_lean_build()
    name, env, options = next(configurations())
    monkeypatch.setattr(english_lean, 'configurations', lambda: iter([(name, env, options)]))
    monkeypatch.setattr(english_lean, 'corpus', lambda *_: [ast.Top()])
    assert lean_incomplete(english_lean.differential(1), {name: 1}) == []
    monkeypatch.setattr(english_lean, 'v0_only', lambda formula: False)
    report = english_lean.differential(1)
    assert report['pairs'] == 1 and report['failure_count'] == 0
    assert lean_incomplete(report, {name: 1}) == ['no round trip', name]


def dropping(kind):
    """`english_lean.v0_only` with one core constructor left out: the ASTs containing it are
    classified outside the core, so they are neither rendered nor compared."""
    real = english_lean.v0_only
    return lambda formula: real(formula) and not any(type(node) is kind for node in nodes(formula))


def test_a_classifier_that_drops_negation_fails_the_smoke(monkeypatch):
    """Review: a classifier rejecting `ast.Not` cut the smoke's completed round trips from
    80 to 48 with no failure, and the gate passed, since it subtracted that classifier's own
    count of ASTs outside the core. The expected count is now the corpus's own."""
    require_lean_build()
    name, env, options = next(configurations())
    monkeypatch.setattr(english_lean, 'configurations', lambda: iter([(name, env, options)]))
    monkeypatch.setattr(english_lean, 'v0_only', dropping(ast.Not))
    report = english_lean.differential(5)
    [row] = report['vocabularies']
    assert report['failure_count'] == 0 and row['outside core AST'] == 2
    assert expected_core(5, name) == {name: 5}
    assert lean_incomplete(report, expected_core(5, name)) == [name]


def covering_corpus():
    """For the first configuration, the first core AST of its corpus containing each Lean
    core constructor. The smoke's corpus (the directed formulas first) has no `Top`,
    `Bottom`, `Binary`, `Or`, `Exists` or constant, so it cannot see a classifier drop one."""
    configuration = next(configurations())
    [formulas] = lean_corpus(100, configuration[0]).values()
    picked = []
    for kind in LEAN_CORE:
        formula = next((f for f in formulas if lean_core(f) and kind in map(type, nodes(f))), None)
        assert formula is not None, f'no core AST with {kind.__name__} in the first 100'
        picked += [formula] if formula not in picked else []
    return configuration, picked


@pytest.mark.parametrize('dropped', [None, *LEAN_CORE],
                         ids=lambda kind: 'none' if kind is None else kind.__name__)
def test_every_core_constructor_completes_its_round_trip(monkeypatch, dropped):
    """Every Lean core constructor is compared, and a classifier that drops any one of them
    fails the gate (with no failure in the report, since nothing it skips is compared)."""
    require_lean_build()
    configuration, formulas = covering_corpus()
    name = configuration[0]
    monkeypatch.setattr(english_lean, 'configurations', lambda: iter([configuration]))
    monkeypatch.setattr(english_lean, 'corpus', lambda *_: formulas)
    if dropped is not None:
        monkeypatch.setattr(english_lean, 'v0_only', dropping(dropped))
    report = english_lean.differential(len(formulas))
    assert report['failure_count'] == 0 and report['pairs'] == len(formulas)
    incomplete = lean_incomplete(report, {name: len(formulas)})
    assert incomplete == [] if dropped is None else name in incomplete


# One test per configuration, or per part of a slow one, so that they render and parse
# in parallel (the slowest took 511 s alone under load 40).
MIXED = [name for name, _, _ in english_mixed.all_configurations()]
MIXED_PARTS = {'news-article-reviewed': 4, 'claude-constitution-excerpt-reviewed': 3, 'news-article': 2}


@pytest.mark.parametrize('offset, part, parts',
                         [(offset, part, MIXED_PARTS.get(name, 1)) for offset, name in enumerate(MIXED)
                          for part in range(MIXED_PARTS.get(name, 1))],
                         ids=[f'{name}-{part}' if name in MIXED_PARTS else name for name in MIXED
                              for part in range(MIXED_PARTS.get(name, 1))])
def test_english_mixed_merge_smoke(offset, part, parts):
    report = english_mixed.mixed(1, only={offset}, part=part, parts=parts)
    assert [row['vocabulary'] for row in report['vocabularies']] == [MIXED[offset]]
    assert report['failure_count'] == 0, report['failures'][:3]
    # The intended corpus: this part's share of the configuration's generated documents
    # (generating them alone renders and parses nothing). Each must complete a round trip.
    corpus = english_mixed.mixed(1, only={offset}, check=False)['texts']
    [row] = report['vocabularies']
    assert row['texts'] == len(range(part, corpus, parts)) > 0
    assert mixed_round_trips(row) == row['texts']


def test_an_unchecked_mixed_run_completes_no_round_trip():
    """Review: with `check=False` as the default, every smoke part passed, because `texts`
    counts the generated documents. The smoke now requires a round trip per document,
    which an unchecked run never completes."""
    report = english_mixed.mixed(1, only={MIXED.index('order')}, check=False)
    [row] = report['vocabularies']
    assert row['texts'] > 0 and mixed_round_trips(row) == 0


def test_the_mixed_parts_are_configurations():
    assert set(MIXED_PARTS) <= set(MIXED)


def test_english_mixed_merge_generates_every_registered_construct():
    """The coverage half of the smoke run: the generated formulas alone decide it."""
    report = english_mixed.mixed(1, check=False)
    assert len(report['vocabularies']) == len(MIXED) and report['texts'] > 0
    assert report['failure_count'] == 0
    assert not report['missing_constructs']
    assert not report['unexercised_profiles']


def test_new_profile_cannot_hide_registered_construct(monkeypatch):
    class NewConstruct:
        pass

    actual = english_mixed.registry.records
    extra = SurfaceRecord('future-test', '', (), '', '', node_type=NewConstruct,
                          profiles=('future@0',))
    monkeypatch.setattr(english_mixed.registry, 'records', lambda: actual() + (extra,))
    monkeypatch.setattr(english_mixed, 'configurations', lambda: iter(()))
    report = english_mixed.mixed(1)
    assert 'NewConstruct' in report['unexercised_profiles']
    assert report['failure_count'] > 0


# The core ASTs of each configuration's 5,000-formula corpus (`expected_core(5000)`, which
# the parametrized test below recomputes in parallel, one configuration each).
FULL_CORE = {
    'ordinary': 5000, 'closure': 2036, 'colliding_aliases': 5000, 'function_words': 5000,
    'function_identifiers': 5000, 'precision_templates': 5000, 'birthright-citizenship-debate': 5000,
    'claude-constitution-excerpt': 2223, 'news-article': 5000, 'us-constitution-14th-s1': 5000,
    'birthright-citizenship-debate-reviewed': 5000, 'claude-constitution-excerpt-reviewed': 2387,
    'news-article-reviewed': 5000, 'us-constitution-14th-s1-reviewed': 5000,
    'accepted-suggestions': 5000, 'adopted-unary': 5000, 'order': 634}


@pytest.mark.parametrize('name', list(FULL_CORE))
def test_full_core_counts_are_the_corpus_counts(name):
    assert expected_core(5000, name) == {name: FULL_CORE[name]}


def test_full_core_counts_name_every_configuration():
    assert list(expected_core(0)) == list(FULL_CORE)


def test_full_english_report_gate():
    report = json.loads((ROOT / 'conformance/english-lean-report.json').read_text())
    assert report['full_gate'] and report['pairs'] == 85000
    assert report['per_vocabulary'] == 5000 and len(report['vocabularies']) == 17
    assert report['failure_count'] == 0
    assert lean_incomplete(report, FULL_CORE) == []
    assert report['seed'] == 2026092107
    assert report['corpus_sha256'] == \
        '12d5984396f2b5e2869195deaae419b6e8a5b73e8eb3bb4515f72d04bbc168ed'


def test_full_mixed_report_gate():
    report = json.loads((ROOT / 'conformance/english-mixed-report.json').read_text())
    assert report['seed'] == 2026792107
    assert report['texts'] == 6757 and len(report['vocabularies']) == 18
    assert report['failure_count'] == 0
    assert all(mixed_round_trips(row) == row['texts'] > 0 for row in report['vocabularies'])
    assert sum(row['texts'] for row in report['vocabularies']) == report['texts']
    assert report['missing_constructs'] == report['unexercised_profiles'] == []
    assert report['vocabularies'][0]['corpus_sha256'] == \
        '90b67e0b66f9f1a996de021b71c13935a6d144327451ca7cfb31ac0bc41631a7'
    assert report['vocabularies'][-1]['vocabulary'] == 'nary'
    assert 'Atom' in report['vocabularies'][-1]['node_types']
    assert report['vocabularies'][-1]['corpus_sha256'] == \
        '4c7fa73cd61a54d3dcdecd8b7aa5ab28020392ad4d96c241f59a321a2abe54b6'
    assert all(len(row['corpus_sha256']) == 64 for row in report['vocabularies'])
