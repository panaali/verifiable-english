"""Version 1 proposal acceptance, ambiguity boundaries, and adoption isolation."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from lark import Lark

from ve import Environment, parse
from ve.__main__ import main
from ve.english import EnglishVocabulary, english_lark_grammar, parse_english_with_metadata
from ve.environment import RESERVED, valid_identifier
from ve.errors import VEError
from ve.propose import adopt, propose, write_proposal

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'usecases/birthright-citizenship-debate'
ENV = Environment.from_json((CASE / 'environment.json').read_bytes())
OVERLAY = json.loads((CASE / 'environment.english.json').read_text())
SENTENCE = 'Every person who is born in the United States and is subject to US jurisdiction is a UK citizen.'


def proposal():
    return propose(ENV, SENTENCE, OVERLAY, acknowledge=['us_citizen'])


def test_closed_diagnostic_names_phrase_span_and_nearest_wording():
    with pytest.raises(VEError) as caught:
        parse_english_with_metadata(ENV, SENTENCE, vocabulary=OVERLAY)
    error = caught.value
    assert 'is a UK citizen' in str(error) and 'is a US citizen' in str(error)
    assert SENTENCE[error.span.start:error.span.end] == 'is a UK citizen'
    assert error.span.line == 1 and error.span.column == error.span.start + 1


def test_preview_requires_named_acknowledgement_and_never_writes_when_blocked(tmp_path):
    preview = propose(ENV, SENTENCE, OVERLAY)
    assert preview['status'] == 'blocked'
    assert preview['requires_acknowledgement'] == ['us_citizen']
    row, = preview['introduced']
    assert row['symbol'] == 'uk_citizen' and row['signature'] == ['person']
    assert row['review_status'] == 'unreviewed'
    assert 'machine-proposed; lexicon oewn-2025; tokens:' in row['description']
    assert row['nearest_existing'][0]['edit_distance'] == 1
    assert row['nearest_existing'][0]['shared_stem']
    with pytest.raises(VEError, match='acknowledge'):
        write_proposal(preview, tmp_path / 'blocked')
    with pytest.raises(VEError, match='acknowledgements'):
        adopt(preview, tmp_path / 'adopted')
    with pytest.raises(VEError, match='flagged'):
        propose(ENV, SENTENCE, OVERLAY, acknowledge=['anything'])
    assert not list(tmp_path.iterdir())


def test_proposal_uses_shared_whitespace_without_changing_source_spans():
    source = SENTENCE.replace('Every person', 'Every\t person').replace('a UK citizen', 'a  UK citizen')
    preview = propose(ENV, source, OVERLAY, acknowledge=['us_citizen'])
    row, = preview['introduced']
    start, end = row['source_span']['start'], row['source_span']['end']
    assert row['source_text'] == source[start:end] == 'is a  UK citizen'
    assert preview['source'] == source


def test_adoption_roundtrip_provenance_and_all_derivations(tmp_path):
    preview = proposal()
    write_proposal(preview, tmp_path / 'candidate')
    record = adopt(preview, tmp_path / 'adopted', acknowledge=['us_citizen'])
    env = Environment.from_json((tmp_path / 'adopted/environment.json').read_bytes())
    overlay = json.loads((tmp_path / 'adopted/environment.english.json').read_text())
    assert record['environment_id'] == env.environment_id != ENV.environment_id
    assert record['review_status'] == 'unreviewed'
    assert all(e['suggested'] for category in ('sorts', 'predicates') for e in overlay[category].values())
    options = dict(vocabulary=overlay, accept_suggested_vocabulary=True)
    result = parse_english_with_metadata(env, SENTENCE, **options)
    assert result.review_status == 'unreviewed'
    assert result.overlay_digest == preview['paraphrase']['overlay_digest'] == record['overlay_digest']
    assert parse(env, result.canonical_text) == result.document
    assert parse_english_with_metadata(env, result.english_text, **options).document == result.document
    with pytest.raises(VEError, match='accept-suggested'):
        parse_english_with_metadata(env, SENTENCE, vocabulary=overlay)
    # Independent all-derivations audit ONLY for the finite adopted lexicon.
    earley = Lark(english_lark_grammar(env, **options), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    from conformance.english_surface import directed_formulas
    from ve import ast, render
    for formula in directed_formulas(env, EnglishVocabulary(env, **options)):
        text = render(ast.Document((formula,)), env, 've_english', **options)
        assert parse_english_with_metadata(env, text, **options).document == ast.Document((formula,))
        assert not list(earley.parse(text[0].lower() + text[1:]).find_data('_ambig'))


def test_candidates_cannot_load_for_any_trusted_operation(tmp_path, capsys):
    preview = proposal()
    write_proposal(preview, tmp_path / 'candidate')
    source = tmp_path / 'source.ve'
    source.write_text('for every person x0, (x0 is uk_citizen).')
    for file in ('proposal.json', 'environment.proposed.json', 'environment.english.proposed.json'):
        candidate = tmp_path / 'candidate' / file
        # All API proof/certificate paths require this same Environment loader.
        with pytest.raises(VEError):
            Environment.from_json(candidate.read_bytes())
        for command in ('check', 'countermodel'):
            args = ['--conclusion', str(source)] if command == 'countermodel' else [str(source)]
            assert main([command, '--env', str(candidate), *args]) == 2
            assert json.loads(capsys.readouterr().out)['status'] == 'InvalidInput'


def test_adoption_revalidates_and_never_overwrites(tmp_path):
    preview = proposal()
    altered = deepcopy(preview)
    altered['acknowledged'] = []
    with pytest.raises(VEError): adopt(altered, tmp_path / 'bad')
    altered = deepcopy(preview)
    altered['candidate_environment']['candidate']['vocabulary']['predicates']['uk_citizen']['arguments'] = ['missing']
    with pytest.raises(VEError): adopt(altered, tmp_path / 'bad')
    adopt(preview, tmp_path / 'good', acknowledge=['us_citizen'])
    with pytest.raises(FileExistsError): adopt(preview, tmp_path / 'good', acknowledge=['us_citizen'])


@pytest.fixture
def ordinary():
    data = ENV.to_dict()
    data['vocabulary'] = {
        'sorts': {'person': {'description': 'Person.'}, 'organization': {'description': 'Organization.'}},
        'predicates': {
            'owns': {'arguments': ['person', 'person'], 'description': 'Owns.', 'verbalisation': '{0} owns {1}'},
            'citizen_of': {'arguments': ['person', 'organization'], 'description': 'Citizenship.', 'verbalisation': '{0} is a citizen of {1}'},
        },
        'constants': {name: {'sort': 'person', 'description': name} for name in ['alice', 'bob', 'acme', 'legacy']}}
    return Environment(data)


@pytest.mark.parametrize('text,reason', [
    ('Alice likes New York.', 'No binary or constant inference.'),
    ('Bob is owned by Alice.', 'No passive inference, and subject has no binder noun.'),
    ('Alice is a member of Acme.', 'No constant-subject proposal or capitalization-based references.'),
    ('Alice is a research and development manager.', 'and is a phrase boundary; no coordinated noun inference.'),
    ('Alice does not own Bob.', 'No negative verb morphology inference.'),
    ('Some people own cars.', 'No some form, sorts, plurals, or constants inferred.'),
    ('Every person is a research and development manager.', 'and terminates the phrase; remaining text is invalid.'),
    ('Every person is owned by alice.', 'Passive by is excluded.'),
    ('Every person believes that state laws apply.', 'No binary inference or complementizer extension.'),
    ('Every person owns legcy.', 'A constant typo is not a unary predicate.'),
    ('Every person ownns legacy.', 'A binary wording typo is not a unary predicate.'),
    ('Every person is a member of bbo.', 'A transposed short constant is not absorbed.'),
    ('Every person is a member of bo.', 'A truncated short constant is not absorbed.'),
    ('Every person is a member of acmme.', 'A typo of a known constant is not absorbed.'),
    ('Every person is a membber of acme.', 'A binary wording typo cannot absorb a known reference.'),
    ('Every person is a citzen of nowhere.', 'A binary frame typo with an unknown object stays an error.'),
    ('Every person is a citizen of.', 'A binary frame missing its object stays an error.'),
    ('Every person is a.', 'An article alone is not a nominal phrase.'),
    ('Every person who owns stock votes.', 'No new object constants or binary predicates.'),
])
def test_review_ambiguities_are_rejected(ordinary, text, reason):
    with pytest.raises(VEError):
        propose(ordinary, text)


@pytest.mark.parametrize('complement,identifier', [('a UK citizen', 'uk_citizen'), ('an honorary fellow', 'honorary_fellow'),
                                                   ('sparkling', 'sparkling'), ('not a UK citizen', 'uk_citizen'),
                                                   ('must', 'predicate_must'), ('x12', 'predicate_x12')])
def test_positive_negative_and_identifier_rules(complement, identifier):
    preview = propose(ENV, 'Every person is ' + complement + '.', OVERLAY)
    row, = preview['introduced']
    assert row['symbol'] == identifier
    assert valid_identifier(identifier) and identifier not in RESERVED
    if complement.startswith('not '):
        assert 'not (' in preview['paraphrase']['canonical_text']


def test_nominal_prepositions_are_atomic_without_reference_or_morphology(ordinary):
    # The maximal phrase rule permits this as ONE unary, not membership(Y).
    preview = propose(ordinary, 'Every person is a member of the guild.')
    assert preview['introduced'][0]['signature'] == ['person']
    assert preview['introduced'][0]['symbol'] == 'member_of_the_guild'


def test_cli_lead_workflow(tmp_path, capsys):
    common = ['--env', str(CASE / 'environment.json'), '--english-vocabulary', str(CASE / 'environment.english.json')]
    assert main(['propose', *common, SENTENCE]) == 2
    assert json.loads(capsys.readouterr().out)['requires_acknowledgement'] == ['us_citizen']
    assert main(['propose', *common, '--acknowledge', 'us_citizen', '--output', str(tmp_path / 'candidate'), SENTENCE]) == 0
    capsys.readouterr()
    assert main(['adopt', str(tmp_path / 'candidate/proposal.json'), '--output', str(tmp_path / 'adopted'), '--acknowledge', 'us_citizen']) == 0
    assert json.loads(capsys.readouterr().out)['review_status'] == 'unreviewed'
    sentence = tmp_path / 'sentence.txt'
    sentence.write_text(SENTENCE)
    assert main(['parse', '--env', str(tmp_path / 'adopted/environment.json'), '--english-vocabulary',
                 str(tmp_path / 'adopted/environment.english.json'), '--accept-suggested-vocabulary',
                 '--surface', 'english', str(sentence)]) == 0
    record = json.loads(capsys.readouterr().out)
    assert record['review_status'] == record['paraphrase']['review_status'] == 'unreviewed'


def test_scope_conflicts_and_no_sort_inference(ordinary):
    with pytest.raises(VEError):
        propose(ordinary, 'Every person is sparkling. Every organization is sparkling.')
    with pytest.raises(VEError):
        propose(ordinary, 'Every dragon is sparkling.')
    preview = propose(ordinary, 'For every person, that person is sparkling.')
    assert preview['introduced'][0]['signature'] == ['person']


def test_normalization_collision_and_length(ordinary):
    data = ordinary.to_dict()
    data['vocabulary']['predicates']['uk_citizen'] = {'arguments': ['person'], 'description': 'Existing symbol.'}
    env = Environment(data)
    preview = propose(env, 'Every person is a UK citizen.')
    assert preview['introduced'][0]['symbol'] == 'uk_citizen_2'
    assert preview['requires_acknowledgement'] == ['citizen_of', 'uk_citizen']
    preview = propose(ordinary, 'Every person is ' + 'z' * 70 + '.')
    assert len(preview['introduced'][0]['symbol']) == 64


def test_adopted_audit_report():
    report = json.loads((ROOT / 'conformance/proposed-vocabulary-report.json').read_text())
    assert report['roundtrips'] == 5000
    assert report['earley_texts'] == 500
    assert report['random_earley_texts'] == 250
    assert report['multi_statement_documents'] == 50
    assert report['ambiguous_texts'] == 0
    row, = report['vocabularies']
    assert row['vocabulary'] == 'adopted-unary' and row['review_status'] == 'unreviewed'


def test_near_duplicate_checks_include_sort_symbols(ordinary):
    preview = propose(ordinary, 'Every person is persom.')
    assert preview['requires_acknowledgement'] == ['person']
    nearest = preview['introduced'][0]['nearest_existing'][0]
    assert nearest['symbol'] == 'person' and nearest['kind'] == 'sort'
    assert nearest['edit_distance'] == 1
    assert propose(ordinary, 'Every person is persom.', acknowledge=['person'])['status'] == 'proposed'


@pytest.mark.parametrize('spelling', ['uk citizen', 'Uk Citizen', 'UK CITIZEN', 'uK   CiTiZeN'])
def test_content_case_roundtrip_and_no_second_predicate(spelling):
    preview = proposal()
    env = Environment(preview['candidate_environment']['candidate'])
    overlay = preview['candidate_overlay']['candidate']
    options = dict(vocabulary=overlay, accept_suggested_vocabulary=True)
    source = SENTENCE.replace('UK citizen', spelling)
    result = parse_english_with_metadata(env, source, **options)
    assert 'is a UK citizen.' in result.english_text
    assert 'uk_citizen_2' not in result.canonical_text
    assert parse_english_with_metadata(env, result.english_text, **options).document == result.document
    grammar = Lark(english_lark_grammar(env, **options), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    assert not list(grammar.parse(source[0].lower() + source[1:]).find_data('_ambig'))
    with pytest.raises(VEError, match='uk_citizen'):
        propose(env, source, overlay, acknowledge=['us_citizen', 'uk_citizen'])


def test_proposed_hyphen_equivalence_names_existing_symbol():
    preview = proposal()
    env = Environment(preview['candidate_environment']['candidate'])
    with pytest.raises(VEError, match='existing wording.*uk_citizen'):
        propose(env, 'Every person is a uk-citizen.', preview['candidate_overlay']['candidate'])


@pytest.mark.parametrize('wording', ['{0} is a uk citizen', '{0} is a UK-citizen', '{0} is a  UK citizen'])
@pytest.mark.parametrize('suggested', [False, True])
def test_handwritten_overlay_duplicate_wording_rejected(wording, suggested):
    preview = proposal()
    data = preview['candidate_environment']['candidate']
    data['vocabulary']['predicates']['other_citizen'] = {'arguments': ['person'], 'description': 'Other citizen.'}
    env = Environment(data)
    overlay = preview['candidate_overlay']['candidate']
    overlay['environment_id'] = env.environment_id
    overlay['predicates']['other_citizen'] = {'verbalisation': wording, 'suggested': suggested}
    with pytest.raises(VEError, match='Duplicate English wording.*(other_citizen|uk_citizen)'):
        EnglishVocabulary(env, vocabulary=overlay, accept_suggested_vocabulary=True)


def test_adopt_requires_own_flags_even_for_previously_acknowledged_preview(tmp_path):
    preview = proposal()
    with pytest.raises(VEError, match='own explicit --acknowledge.*us_citizen'):
        adopt(preview, tmp_path / 'rejected')
    assert not (tmp_path / 'rejected').exists()
    assert adopt(preview, tmp_path / 'ok', acknowledge=['us_citizen'])['acknowledged'] == ['us_citizen']


@pytest.mark.parametrize('field', ['source', 'base_environment', 'base_overlay', 'acknowledged', 'status', 'introduced'])
def test_adopt_rejects_tampered_or_stale_proposal(tmp_path, field):
    preview = proposal()
    if field == 'source':
        preview[field] += ' '
    elif field == 'base_environment':
        preview[field]['vocabulary']['sorts']['person']['description'] += ' changed'
    elif field == 'base_overlay':
        preview[field]['predicates']['us_citizen']['verbalisation'] = '{0} is a citizen'
    elif field == 'acknowledged':
        preview[field] = []
    elif field == 'status':
        preview[field] = 'adopted'
    else:
        preview[field][0]['near_duplicates'] = []
    with pytest.raises(VEError, match='digest changed'):
        adopt(preview, tmp_path / 'bad', acknowledge=['us_citizen'])
    assert not list(tmp_path.iterdir())


def test_linter_collision_diagnostic_attributes_both_phrases():
    with pytest.raises(VEError) as caught:
        propose(ENV, 'Every person who is born in the United States is a citizen.', OVERLAY)
    message = str(caught.value)
    assert 'Proposed phrase' in message and '{0} is a citizen' in message
    assert 'has_noncitizen_domiciled_parent' in message
    assert 'has a noncitizen parent domiciled in the United States' in message


@pytest.mark.parametrize('phrase', ['a citizen of the US', 'a citizen of the us'])
def test_reordered_content_overlap_is_flagged_and_explained(phrase):
    preview = propose(ENV, 'Every person is ' + phrase + '.', OVERLAY)
    assert 'us_citizen' in preview['requires_acknowledgement']
    row = next(r for r in preview['introduced'][0]['nearest_existing'] if r['symbol'] == 'us_citizen')
    assert row['content_overlap'] == ['citizen', 'us']


@pytest.mark.parametrize('phrase', ['taller than Bob', 'a citizen of France', 'owned by someone',
    'no longer employed', 'never employed', 'neither employed', 'nor employed', 'without work',
    'true', 'false', 'equal', 'equals', 'a member of alice', 'alice friendly',
    'a person', 'a person enthusiast', 'an organization', 'a non-employed worker', 'un-employed', 'no-longer employed', 'NEVER employed', 'taller-than Bob', 'a citizen of-France'])
def test_relational_negative_and_sort_content_rejected(ordinary, phrase):
    with pytest.raises(VEError, match='declared by hand'):
        propose(ordinary, 'Every person is ' + phrase + '.')


@pytest.mark.parametrize('prefix', ['un', 'non', 'un-', 'non-', 'UN', 'NON'])
def test_declared_negative_heads_cannot_override_closed_lint(ordinary, prefix):
    data = ordinary.to_dict()
    data['vocabulary']['predicates']['employed'] = {'arguments': ['person'], 'description': 'Employed.',
                                                   'verbalisation': '{0} is employed'}
    with pytest.raises(VEError):
        propose(Environment(data), 'Every person is ' + prefix + 'employed.')


def test_prefix_collision_names_existing_wording():
    for parse_text in (lambda text: propose(ENV, text, OVERLAY),
                       lambda text: parse_english_with_metadata(ENV, text, vocabulary=OVERLAY)):
        with pytest.raises(VEError, match="extends existing wording.*us_citizen.*is a US citizen"):
            parse_text('Every person is a US citizen of record.')


def test_cli_adopt_to_keeps_all_gates(tmp_path, capsys):
    common = ['--env', str(CASE / 'environment.json'), '--english-vocabulary', str(CASE / 'environment.english.json')]
    output = tmp_path / 'adopted'
    assert main(['propose', *common, '--adopt-to', str(output), SENTENCE]) == 2
    assert json.loads(capsys.readouterr().out)['requires_acknowledgement'] == ['us_citizen']
    assert not output.exists()
    assert main(['propose', *common, '--adopt-to', str(output), '--acknowledge', 'us_citizen', SENTENCE]) == 0
    assert json.loads(capsys.readouterr().out)['acknowledged'] == ['us_citizen']
    assert (output / 'environment.json').is_file()
    assert main(['propose', *common, '--adopt-to', str(tmp_path / 'clean'), 'Every person is sparkling.']) == 0
    assert json.loads(capsys.readouterr().out)['acknowledged'] == []


def test_cli_adopt_rejects_recorded_acknowledgements(tmp_path, capsys):
    write_proposal(proposal(), tmp_path / 'proposal')
    assert main(['adopt', str(tmp_path / 'proposal/proposal.json'), '--output', str(tmp_path / 'bad')]) == 2
    assert 'own explicit --acknowledge' in json.loads(capsys.readouterr().out)['error']['message']
    assert not (tmp_path / 'bad').exists()


def test_no_overlay_proposal_can_be_adopted(ordinary, tmp_path):
    preview = propose(ordinary, 'Every person is sparkling.')
    assert adopt(preview, tmp_path / 'adopted')['status'] == 'adopted'


def test_content_overlap_ignores_order_function_words_and_plural_s():
    from ve.english_phrases import nearest
    words = EnglishVocabulary(ENV, vocabulary=OVERLAY)
    for phrase in ('US citizens', 'citizens of the US', 'citizen of the US'):
        row = next(r for r in nearest(phrase, words) if r['symbol'] == 'us_citizen')
        assert row['near_duplicate'] and row['content_overlap'] == ['citizen', 'us']


def test_cli_adopts_proposal_without_base_overlay(tmp_path, capsys, ordinary):
    env_path = tmp_path / 'base.json'
    env_path.write_text(json.dumps(ordinary.to_dict()))
    assert main(['propose', '--env', str(env_path), '--output', str(tmp_path / 'candidate'),
                 'Every person is sparkling.']) == 0
    capsys.readouterr()
    assert main(['adopt', str(tmp_path / 'candidate/proposal.json'), '--output', str(tmp_path / 'adopted')]) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'adopted'


def test_content_casing_in_declared_nouns_and_bound_references(ordinary):
    preview = propose(ordinary, 'For every PERSON, that PeRsOn is Sparkling.')
    env = Environment(preview['candidate_environment']['candidate'])
    options = dict(vocabulary=preview['candidate_overlay']['candidate'], accept_suggested_vocabulary=True)
    result = parse_english_with_metadata(env, 'For every PERSON, THAT PERSON is SPARKLING.', **options)
    assert 'Every person is Sparkling.' in result.english_text
    grammar = Lark(english_lark_grammar(env, **options), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    assert not list(grammar.parse('for every PERSON, THAT PERSON is SPARKLING.').find_data('_ambig'))


def test_case_sensitive_quoted_identifiers_are_not_content_aliases(ordinary):
    data = ordinary.to_dict()
    for name in ('code_a', 'code_b'):
        data['vocabulary']['predicates'][name] = {'arguments': ['person'], 'description': name}
    env = Environment(data)
    with pytest.raises(VEError):
        parse_english_with_metadata(env, 'Every person is classified as "CODE_A".')
    assert 'code_a' in parse_english_with_metadata(env, 'Every person IS CLASSIFIED AS "code_a".').canonical_text


def test_forged_recorded_acknowledgements_never_authorize_adoption(tmp_path):
    from ve.wire import digest
    preview = propose(ENV, SENTENCE, OVERLAY)
    preview.update(status='proposed', acknowledged=['us_citizen'], requires_acknowledgement=[])
    preview['proposal_digest'] = digest('ve-vocabulary-proposal-v1\n',
                                       {k: v for k, v in preview.items() if k != 'proposal_digest'})
    with pytest.raises(VEError, match='own explicit --acknowledge'):
        adopt(preview, tmp_path / 'bad')
    assert not list(tmp_path.iterdir())


def test_adopt_recomputes_near_duplicates_even_with_updated_envelope_digest(tmp_path):
    from ve.wire import digest
    preview = proposal()
    preview['introduced'][0]['near_duplicates'] = []
    preview['proposal_digest'] = digest('ve-vocabulary-proposal-v1\n',
                                       {k: v for k, v in preview.items() if k != 'proposal_digest'})
    with pytest.raises(VEError, match='Proposal changed'):
        adopt(preview, tmp_path / 'bad', acknowledge=['us_citizen'])
    assert not list(tmp_path.iterdir())


def test_overlay_duplicate_of_implicit_wording_rejected(ordinary):
    data = ordinary.to_dict()
    for name in ('active', 'other'):
        data['vocabulary']['predicates'][name] = {'arguments': ['person'], 'description': name}
    env = Environment(data)
    overlay = {'format': 've.english-vocabulary@1', 'environment_id': env.environment_id, 'sorts': {},
               'predicates': {'other': {'verbalisation': '{0} is ACTIVE', 'suggested': True}}}
    with pytest.raises(VEError, match='Duplicate English wording.*active'):
        EnglishVocabulary(env, vocabulary=overlay, accept_suggested_vocabulary=True)
