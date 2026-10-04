"""Merge gates for the two English correspondence harnesses."""
import json
from pathlib import Path
import shutil

import pytest

from ve import ast
from ve.english import EnglishVocabulary, parse_english
from ve.errors import SyntaxError
from conformance import english_lean, english_mixed
from conformance.english_surface import configurations
from ve.surface.registry import SurfaceRecord

ROOT = Path(__file__).resolve().parents[1]


def require_lean_build():
    assert shutil.which('lake'), 'lake must be on PATH'
    assert (ROOT / 'lean/.lake/build/lib/lean/VE/English/Run.olean').exists(), \
        'Run lake build before the English evidence tests'


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
    assert report['texts'] > 0


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


def test_full_english_report_gate():
    report = json.loads((ROOT / 'conformance/english-lean-report.json').read_text())
    assert report['full_gate'] and report['pairs'] == 85000
    assert report['per_vocabulary'] == 5000 and len(report['vocabularies']) == 17
    assert report['failure_count'] == 0
    assert report['seed'] == 2026092107
    assert report['corpus_sha256'] == \
        '12d5984396f2b5e2869195deaae419b6e8a5b73e8eb3bb4515f72d04bbc168ed'


def test_full_mixed_report_gate():
    report = json.loads((ROOT / 'conformance/english-mixed-report.json').read_text())
    assert report['seed'] == 2026792107
    assert report['texts'] == 6757 and len(report['vocabularies']) == 18
    assert report['failure_count'] == 0
    assert report['missing_constructs'] == report['unexercised_profiles'] == []
    assert report['vocabularies'][0]['corpus_sha256'] == \
        '90b67e0b66f9f1a996de021b71c13935a6d144327451ca7cfb31ac0bc41631a7'
    assert report['vocabularies'][-1]['vocabulary'] == 'nary'
    assert 'Atom' in report['vocabularies'][-1]['node_types']
    assert report['vocabularies'][-1]['corpus_sha256'] == \
        '4c7fa73cd61a54d3dcdecd8b7aa5ab28020392ad4d96c241f59a321a2abe54b6'
    assert all(len(row['corpus_sha256']) == 64 for row in report['vocabularies'])
