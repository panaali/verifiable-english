"""Pinned lexical data, advisory classification, and proposal provenance."""
from copy import deepcopy
import io
import json
from pathlib import Path
import zipfile

import pytest

from tools import build_lexicon
from ve import Environment
from ve.english import parse_english_with_metadata
from ve.errors import VEError
from ve.lexicon import classify, describe
from ve.propose import adopt, propose
from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def env():
    data = json.loads((ROOT / 'usecases/birthright-citizenship-debate/environment.json').read_text())
    data['vocabulary'] = {
        'sorts': {'person': {'description': 'Person.',
                              'verbalisation': {'singular': 'person', 'plural': 'people'}}},
        'predicates': {}, 'constants': {}}
    return Environment(data)


def test_shipped_data_is_sorted_compact_and_lossless():
    data = (ROOT / 've/lexicon/oewn-2025.json').read_bytes()
    lexicon = json.loads(data)
    assert len(data) < 5_000_000
    assert lexicon['source'] == {'url': build_lexicon.SOURCE_URL, 'sha256': build_lexicon.SOURCE_SHA256}
    rows = lexicon['entries']
    assert len(rows) == 72780
    assert rows == sorted(rows)
    assert len({(lemma, cls) for lemma, cls, _, _ in rows}) == len(rows)
    for lemma, cls, suffixes, forms in rows:
        assert build_lexicon.WORD.fullmatch(lemma)
        assert cls in {'noun', 'adjective', 'verb'}
        assert suffixes == sorted(set(suffixes))
        assert all(suffix[0] in {'noun': '1', 'verb': '2', 'adjective': '35'}[cls] for suffix in suffixes)
        for values in forms.values():
            assert values == sorted(set(values))
    assert build_lexicon.encode(lexicon) == data


def test_builder_rejects_unverified_source():
    with pytest.raises(ValueError, match='SHA-256 mismatch'):
        build_lexicon.build(b'not the pinned release')


def test_exception_third_person_variants_take_precedence_over_spelling_rules():
    rows = json.loads((ROOT / 've/lexicon/oewn-2025.json').read_bytes())['entries']
    verbs = {lemma: forms for lemma, cls, _, forms in rows if cls == 'verb'}
    assert verbs['quiz']['third_person'] == ['quizzes']
    assert verbs['chivy']['third_person'] == ['chevies', 'chivvies']
    assert verbs['be']['third_person'] == ['is']
    assert 'was' not in verbs['be']['past_participle']


def test_extraction_keeps_senses_and_exceptions_without_frequency_filter(monkeypatch):
    # A small format fixture exercises extraction without tests depending on a network.
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('oewn2025/index.sense', '\n'.join([
            'write%2:36:00:: 00000000 1 0', 'written%3:00:00:: 00000001 1 0',
            'citizen%1:18:00:: 00000002 1 0', 'write%2:32:00:: 00000003 1 0',
            'two_words%1:00:00:: 00000004 1 0', 'quickly%4:02:00:: 00000005 1 0']))
        z.writestr('oewn2025/verb.exc', 'written write\nwrote write\nwriting write\n')
    data = archive.getvalue()
    import hashlib
    monkeypatch.setattr(build_lexicon, 'SOURCE_SHA256', hashlib.sha256(data).hexdigest())
    result = build_lexicon.build(data)
    assert [r[:2] for r in result['entries']] == [['citizen', 'noun'], ['write', 'verb'], ['written', 'adjective']]
    row = result['entries'][1]
    assert row[2] == ['2:32:00::', '2:36:00::']
    assert row[3] == {'third_person': ['writes'], 'past_participle': ['written'],
                      'exceptions': ['writing', 'written', 'wrote']}
    assert build_lexicon.encode(result) == build_lexicon.encode(build_lexicon.build(data))


@pytest.mark.parametrize('token,expected,lemma', [
    ('citizen', 'noun', 'citizen'), ('helpful', 'adjective', 'helpful'),
    ('deployed', 'participle', 'deploy'), ('reviewed', 'participle', 'review'),
    ('written', 'participle', 'write'), ('gone', 'participle', 'go'),
    ('bought', 'participle', 'buy'), ('run', 'participle', 'run'),
])
def test_unary_classes_and_inflected_sense_keys(token, expected, lemma):
    evidence = classify(token)
    row, = evidence['tokens']
    assert expected in row['classes']
    analysis = next(a for a in row['analyses'] if a['class'] == expected)
    assert analysis['lemma'] == lemma
    assert all(key.startswith(lemma + '%') for key in analysis['sense_keys'])
    assert f'{token}/{expected}(' in describe(evidence) or f'|{expected}(' in describe(evidence)
    assert classify(token.upper())['tokens'][0]['analyses'] == row['analyses']


def test_homographs_preserve_all_classes_and_senses():
    row, = classify('light')['tokens']
    assert 'noun' in row['classes'] and 'adjective' in row['classes']
    assert all(len(a['sense_keys']) > 1 for a in row['analyses'])
    row, = classify('went')['tokens']
    assert row['classes'] == ['unknown']  # An untagged past form is not a participle.
    assert row['known_to_lexicon']
    assert not classify('went')['all_unknown_undeclared']


def test_unknown_warning_is_advisory_and_adoption_still_explicit(env, tmp_path):
    source = 'Every person is zzyqv blorptastic.'
    with pytest.raises(VEError):
        parse_english_with_metadata(env, source)
    preview = propose(env, source)
    row, = preview['introduced']
    evidence = row['lexicon']
    assert preview['status'] == 'proposed'
    assert evidence['unknown_tokens'] == ['zzyqv', 'blorptastic']
    assert evidence['all_unknown_undeclared']
    assert row['description'].startswith('machine-proposed; lexicon oewn-2025; tokens: zzyqv/unknown(no sense key)')
    assert propose(env, source) == preview
    with pytest.raises(VEError):
        Environment(preview['candidate_environment'])
    adopt(preview, tmp_path / 'adopted')
    adopted = Environment.from_json((tmp_path / 'adopted/environment.json').read_bytes())
    overlay = json.loads((tmp_path / 'adopted/environment.english.json').read_text())
    parse_english_with_metadata(adopted, source, vocabulary=overlay, accept_suggested_vocabulary=True)


def test_known_and_declared_tokens_suppress_all_unknown_flag(env):
    row, = propose(env, 'Every person is helpful zzyqv.')['introduced']
    assert row['lexicon']['unknown_tokens'] == ['zzyqv']
    assert not row['lexicon']['all_unknown_undeclared']
    data = env.to_dict()
    data['vocabulary']['predicates']['zzyqv'] = {'arguments': ['person'], 'description': 'Opaque declared word.'}
    row, = propose(Environment(data), 'Every person is blorptastic zzyqv.')['introduced']
    assert row['lexicon']['tokens'][1]['declared']
    assert not row['lexicon']['all_unknown_undeclared']
    assert 'zzyqv' in row['near_duplicates']  # Lexical evidence does not bypass this gate.


def test_token_boundaries_are_only_annotations(env):
    row, = propose(env, 'Every person is helpful-zzyqv.')['introduced']
    assert [r['token'] for r in row['lexicon']['tokens']] == ['helpful', 'zzyqv']
    assert row['symbol'] == 'helpful_zzyqv'
    assert row['verbalisation'] == '{0} is helpful-zzyqv'


@pytest.mark.parametrize('phrase', ['a citizen of France', 'a citizen of france',
                                  'a citizen OF FRANCE', 'a citizen of-france',
                                  'a member of PERSON', 'a PEOPLE enthusiast',
                                  'owned BY someone', 'NEVER employed'])
def test_case_independent_relational_and_sort_gates(env, phrase):
    # No binary predicate/constant exists here to mask the preposition regression.
    with pytest.raises(VEError, match='declared by hand'):
        propose(env, 'Every person is ' + phrase + '.')


@pytest.mark.parametrize('spelling', ['france', 'FRANCE', 'France'])
def test_declared_constants_are_blocked_case_insensitively(env, spelling):
    data = env.to_dict()
    data['vocabulary']['constants']['france'] = {'sort': 'person', 'description': 'Opaque constant.'}
    with pytest.raises(VEError, match='declared constant or sort noun'):
        propose(Environment(data), 'Every person is ' + spelling + ' friendly.')


@pytest.mark.parametrize('phrase', ['a member of the guild', 'a member OF THE guild'])
def test_article_led_opaque_phrase_remains_allowed(env, phrase):
    assert propose(env, 'Every person is ' + phrase + '.')['status'] == 'proposed'


def test_lexical_evidence_cannot_be_tampered_with_even_after_redigest(env, tmp_path):
    preview = deepcopy(propose(env, 'Every person is helpful.'))
    preview['introduced'][0]['lexicon']['tokens'][0]['analyses'][0]['sense_keys'] = ['fake%3:00:00::']
    preview['proposal_digest'] = digest('ve-vocabulary-proposal-v1\n',
                                        {k: v for k, v in preview.items() if k != 'proposal_digest'})
    with pytest.raises(VEError, match='Proposal changed'):
        adopt(preview, tmp_path / 'adopted')
    assert not (tmp_path / 'adopted').exists()
