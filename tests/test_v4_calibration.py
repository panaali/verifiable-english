"""Gold semantics, no gold leakage, and repeated-error selection semantics."""
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest
import ve
from ve_experiments.claude_cli import Controls, EndpointError, check_context_date, isolated_env

HERE=Path(__file__).resolve().parents[1]/'experiments/V4-calibration'
sys.path.insert(0,str(HERE))
import generate as cg
import calibrate as cr
sys.path.remove(str(HERE))


def test_fixed_environment_overrides_inherited_values():
    env=isolated_env({'LANG':'random','LC_ALL':'random','TZ':'random','SHELL':'random'},'/c','/h','test',Controls())
    assert (env['LANG'],env['LC_ALL'],env['TZ'],env['SHELL'])==('en_US.UTF-8','en_US.UTF-8','UTC','/bin/sh')
    with pytest.raises(EndpointError,match='date would drift'):
        check_context_date(Controls(context_date='1900-01-01'))


def test_corpus_gold_replay_and_both_polarities():
    for split in ('smoke','dev','heldout'):
        rows=cr.load_items(split)
        for item in rows:
            env=ve.Environment.from_dict(item['environment'])
            fs=[ve.formula_from_data(env,p['gold_ast']) for p in item['premises']]
            q=ve.formula_from_data(env,item['query']['gold_ast'])
            evidence=item['gold_evidence']
            if item['label']=='Uncertain':
                assert set(item['gold_witnesses'])=={'True','False'}
            else:
                goal=q if item['label']=='True' else ve.Not(q)
                assert ve.check_entailment_certificate(env,fs,goal,evidence['certificate'],max_steps=10000).valid
            for polarity,raw in item['gold_witnesses'].items():
                model=ve.FiniteModel.from_dict(env,raw)
                assert all(ve.evaluate(env,f,model).value for f in fs)
                assert ve.evaluate(env,q,model).value is (polarity=='True')
            assert 300<=item['content_words']<=310


def test_public_prompt_and_disjoint_instances():
    ids=set()
    for split in ('smoke','dev','heldout'):
        for item in cr.load_items(split):
            assert item['id'] not in ids;ids.add(item['id'])
            text=cr.prompt(item)
            for forbidden in ('gold_ast','gold_witnesses','gold_evidence',item['id']):
                assert forbidden not in text
    assert cr.load_items('smoke')[0]==cg.generate_item('smoke','uncertain',0)


def test_recurring_error_is_same_wrong_label_not_two_different_errors():
    item={'id':'x','type':'xor','label':'True'}
    rows={('x',0):{'answer':'False'},('x',1):{'answer':'Uncertain'},('x',2):{'answer':'True','correct':True}}
    summary=cr.summarize([item],rows)['by_type']['xor']
    assert summary['recurring_same_wrong_answer_items']==0
    rows['x',2]={'answer':'False'}
    assert cr.summarize([item],rows)['by_type']['xor']['recurring_same_wrong_answer_items']==1


def test_model_split_gates_precede_spend():
    with patch.object(cr.ClaudeCLI,'sample',side_effect=AssertionError('must not spend')):
        with pytest.raises(ValueError,match='Haiku only'): cr.run('smoke','opus')
        with pytest.raises(ValueError,match='Never expose'): cr.run('dev','opus')
        with pytest.raises(ValueError,match='requires frozen'): cr.run('heldout','opus')
