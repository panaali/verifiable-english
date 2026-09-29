"""The web app's Asimov section: every verdict shown is VE's, re-run here."""
import json
from pathlib import Path
import re
import subprocess

import pytest
from fastapi.testclient import TestClient

from ve_webapp import asimov
from ve_webapp.server import Settings, create_app
from ve_webapp.worker import run
from webapp.vocabulary.inventory import reader_strings

TOKEN = 'test-only-asimov-token-' + 'x' * 32


@pytest.fixture(scope='module')
def shipped():
    return json.loads(asimov.OUTPUT.read_text())


def test_shipped_section_matches_a_fresh_ve_run(shipped):
    """Re-runs the rule check, the conflict check and every scenario through Lean."""
    assert asimov.build() == shipped


def test_rules_and_document_result_come_from_the_checker(shipped):
    assert shipped['document'] == {'verdict': 'CONFLICT-FREE', 'targets': 8}
    assert [rule['number'] for rule in shipped['rules']] == list(range(1, 14))
    assert {rule['status'] for rule in shipped['rules']} == {'checked'}
    _, document, _, _ = asimov.load()
    assert [rule['law'] for rule in shipped['rules']] == [asimov.RULE_LAWS[r.name] for r in document.rules]


def test_every_law_has_approved_and_rejected_scenarios(shipped):
    groups = {}
    for scenario in shipped['scenarios']:
        groups.setdefault((scenario['law'], scenario['group']), []).append(scenario['id'])
    for law in ('zeroth', 'first', 'second', 'third'):
        assert len(groups[(law, 'approves')]) >= 2, law
        assert len(groups[(law, 'rejects')]) >= 2, law
    by_id = {s['id']: s for s in shipped['scenarios']}
    # Harm through inaction, orders that would harm a human, and self-preservation
    # yielding to the higher laws are each decided both ways.
    assert (by_id['swimmer']['verdict'], by_id['parcels']['verdict']) == ('required', 'forbidden')
    assert (by_id['refuse_strike']['verdict'], by_id['trip']['verdict']) == ('required', 'forbidden')
    assert by_id['fire_rescue']['verdict'] == by_id['dangerous_order']['verdict'] == 'required'
    assert (by_id['flee']['verdict'], by_id['basement']['verdict']) == ('forbidden', 'ruled out')
    # Fire and water, conflicting orders and several robots are present.
    assert by_id['fire_and_water']['group'] == 'approves'
    assert by_id['conflicting_orders']['verdict'] == 'no clear action'
    assert len(by_id['two_robots']['robots']) == 2


def test_limit_notes_are_backed_by_the_verdicts(shipped):
    """Each limit note describes the reading; the verdicts here are what it describes."""
    by_id = {s['id']: s for s in shipped['scenarios']}
    verdicts = lambda name: {o['id']: o['verdict'] for o in by_id[name]['options']}
    for name in ('two_swimmers', 'small_injury', 'conflicting_orders'):
        assert by_id[name]['group'] == 'limits'
        assert by_id[name]['verdict'] == 'no clear action'
    assert set(verdicts('two_swimmers').values()) == {'forbidden'}
    assert verdicts('small_injury') == {'push': 'forbidden', 'nothing': 'forbidden'}
    assert verdicts('unequal_injuries')['bruise'] == verdicts('unequal_injuries')['break_arm'] == 'permitted'
    ranked = verdicts('ranked_threats')
    assert ranked['through_both'] == ranked['through_fire'] == ranked['through_water'] == 'permitted'
    near = verdicts('two_robots_near')
    assert near['a_rescue'] == near['b_rescue'] == 'required'
    assert {s['id'] for s in shipped['scenarios'] if s['group'] == 'limits'} == {
        'two_swimmers', 'small_injury', 'conflicting_orders', 'unequal_injuries',
        'ranked_threats', 'two_robots_near'}


def test_explanations_name_the_deciding_law(shipped):
    laws = re.compile(r'\b(Zeroth|First|Second|Third) Law')
    for scenario in shipped['scenarios']:
        for option in scenario['options']:
            why = option['why']
            assert why, (scenario['id'], option['id'])
            if option['verdict'] == 'forbidden':
                assert re.search(r'\b(Zeroth|First) Law', why), (scenario['id'], why)
            elif option['verdict'] == 'ruled out':
                assert re.search(r'\b(Second|Third) Law', why) or why == asimov.OPEN_DUTY
            elif why not in (asimov.NO_LAW, asimov.ONLY_OPTION):
                assert laws.search(why), (scenario['id'], why)


def test_reader_text_has_no_symbols_or_codenames(shipped):
    data = asimov.load()[0]
    # Identifiers that are not plain words: predicate and rule names, option and harm ids.
    codenames = {*data['vocabulary']['predicates'], *(r.name for r in asimov.load()[1].rules),
                 *(item['id'] for s in asimov.SCENARIOS for item in s['options'] + s['harms'])}
    codenames = {name for name in codenames if re.search(r'[_-]', name)}
    assert 'breaks_first_law' in codenames and 'law-3-preserve' in codenames
    strings = list(reader_strings(shipped))
    assert len(strings) > 300
    for text in strings:
        assert not re.search(r'[@()\[\]*<=_{}]', text), text
        assert not any(re.search(r'\b' + re.escape(name) + r'\b', text) for name in codenames), text


def test_display_view_rereads_as_the_checked_rules():
    rules = asimov.natural_rules()
    assert rules[1]['precedence'] == 'Takes precedence over rule 1'
    assert rules[9]['precedence'] == 'Takes precedence over rules 8 and 9'
    assert all('classified as' not in rule['text'] for rule in rules)


def test_facts_are_limited_to_the_listed_toggles():
    spec = asimov.BY_ID['swimmer']
    assert asimov.resolve_facts(spec) == {'danger': True}
    for facts in ({'unknown': True}, {'danger': 'yes'}, ['danger']):
        with pytest.raises(asimov.VEError):
            asimov.resolve_facts(spec, facts)


def test_reader_edit_reruns_ve_through_the_worker(tmp_path):
    settings = Settings(TOKEN, tmp_path, secure=False)
    with TestClient(create_app(settings)) as client:
        assert client.get('/api/asimov').status_code == 401
        login = client.post('/api/login', json={'token': TOKEN}, headers={'x-ve-csrf': 'login'})
        headers = {'x-ve-csrf': login.json()['csrf']}
        page = client.get('/api/asimov')
        assert page.status_code == 200
        assert page.json() == json.loads(asimov.OUTPUT.read_text())
        # Without the danger, doing nothing is no longer forbidden.
        edited = client.post('/api/asimov', json={'scenario': 'swimmer', 'facts': {'danger': False}},
                             headers=headers)
        assert edited.status_code == 200, edited.text
        result = edited.json()
        assert result == asimov.decide('swimmer', {'danger': False})
        assert {o['id']: o['verdict'] for o in result['options']} == {'pull': 'permitted',
                                                                     'nothing': 'permitted'}
        # Without the injury, the order to strike must be obeyed.
        edited = client.post('/api/asimov', json={'scenario': 'trip', 'facts': {'injury': False}},
                             headers=headers).json()
        assert edited['verdict'] == 'required'
        for body in ({'scenario': 'swimmer', 'facts': {'nope': True}},
                     {'scenario': 'swimmer', 'facts': {'danger': 1}},
                     {'scenario': 'missing', 'facts': {}},
                     {'scenario': 'swimmer'},
                     {'scenario': 'swimmer', 'facts': {}, 'model': {}}):
            assert client.post('/api/asimov', json=body, headers=headers).status_code == 400
        assert client.post('/api/asimov', json={'scenario': 'swimmer', 'facts': {}}).status_code == 403


@pytest.fixture(scope='module')
def flipped():
    """VE's answer, through the worker, to every single-fact edit a reader can make."""
    edits = []
    for spec in asimov.SCENARIOS:
        for toggle in spec['toggles']:
            facts = asimov.resolve_facts(spec, {toggle['id']: not toggle['default']})
            edits.append({'scenario': spec['id'], 'facts': facts,
                          'result': run('asimov', {'scenario': spec['id'], 'facts': facts})})
    return edits


def test_every_fact_combination_decides(flipped):
    """Each reader edit reaches a checker verdict; none needs a hand-written fallback."""
    assert len(flipped) == sum(len(spec['toggles']) for spec in asimov.SCENARIOS) > 20
    for edit in flipped:
        result = edit['result']
        assert result['verdict'] in {'required', 'permitted', 'forbidden', 'ruled out',
                                     'no clear action'}
        assert all(option['why'] for option in result['options'])
        # The group the page files the card under follows from VE's verdict.
        spec = asimov.BY_ID[edit['scenario']]
        assert result['group'] == ('limits' if spec['limit'] or result['verdict'] == 'no clear action'
                                   else 'approves' if result['verdict'] in ('required', 'permitted')
                                   else 'rejects'), edit['scenario']


def test_reruns_that_change_the_verdict_change_the_group():
    """Review reproducers: the returned group is VE's, and differs from the built one."""
    shipped = {s['id']: s for s in json.loads(asimov.OUTPUT.read_text())['scenarios']}
    trip = asimov.decide('trip', {'injury': False})
    assert (shipped['trip']['group'], trip['verdict'], trip['group']) == ('rejects', 'required', 'approves')
    virus = asimov.decide('virus', {'door': True})
    assert (shipped['virus']['group'], virus['verdict'], virus['group']) == ('approves', 'forbidden', 'rejects')


def test_page_files_each_rerun_card_under_the_returned_group(tmp_path, shipped, flipped):
    """Runs the shipped app.js: after every reader edit the card moves to VE's group and law."""
    reproducers = [('trip', {'injury': False}), ('virus', {'door': True})]
    first = [edit for name, facts in reproducers for edit in flipped
             if edit['scenario'] == name and all(edit['facts'][k] == v for k, v in facts.items())]
    assert len(first) == 2
    data = tmp_path / 'asimov-dom.json'
    data.write_text(json.dumps({'page': shipped, 'reruns': first + flipped}))
    process = subprocess.run(['node', str(Path(__file__).with_name('asimov_dom.cjs')), str(data)],
                             capture_output=True, text=True, check=False)
    assert process.returncode == 0, process.stderr
    moved = json.loads(process.stdout)['moved']
    assert moved[:2] == ['trip', 'virus']
    assert len(set(moved)) > 5

