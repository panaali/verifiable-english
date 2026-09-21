"""One shared corpus: Python/Rust, and the existing Lean bridge where applicable."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from ve import Environment, FiniteModel, evaluate, parse, print_document
from ve.ast import document_from_data
from ve.errors import VEError
from ve.identity import meaning_id
from ve.wire import canonical_json, loads_json

ROOT = Path(__file__).resolve().parents[1]


def fixture(name):
    return json.loads((ROOT / f'conformance/{name}.json').read_text())


@pytest.fixture(scope='session')
def rust_executable():
    cargo = shutil.which('cargo')
    if not cargo: pytest.skip('cargo is not available')
    env = {**os.environ, 'CARGO_HOME': str(ROOT/'.cargo-home'), 'CARGO_TARGET_DIR': str(ROOT/'rust/target')}
    run = subprocess.run([cargo, 'build', '--locked', '--release', '--manifest-path', str(ROOT/'rust/Cargo.toml')],
                         cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    return ROOT/'rust/target/release/ve'


def invoke(executable, cases, errors=False):
    run = subprocess.run([str(executable),'conformance'], input=json.dumps(cases), text=True,
                         capture_output=True, timeout=60)
    assert run.returncode == int(errors), run.stdout + run.stderr
    return json.loads(run.stdout)


def test_rust_shared_evaluation(rust_executable):
    cases = fixture('evaluation'); results = invoke(rust_executable, cases)
    assert len(cases) == len(results) == 177
    assert sum(len(c['ast']) for c in cases) == 776
    for c, r in zip(cases, results, strict=True):
        env = Environment.from_dict(c['environment']); model = FiniteModel.from_dict(env,c['model'])
        doc = document_from_data(env,c['ast'])
        assert r['values'] == c['expected'] == [evaluate(env,f,model).value for f in doc.formulas], c['id']
        assert r['value'] == all(c['expected'])
        assert r['canonical'] == c['source'] == print_document(env,doc)
        assert r['ast'] == c['ast']


def test_rust_shared_parser(rust_executable):
    cases = fixture('parser'); results = invoke(rust_executable,cases,errors=True)
    for c,r in zip(cases,results,strict=True):
        env = Environment.from_dict(c['environment']); expected = c['expected_parser']
        if 'error_code' in expected:
            with pytest.raises(VEError) as exc: parse(env,c['source'])
            assert exc.value.code == expected['error_code'] == r['error']['code'], c['id']
            assert 'span' in r['error'], c['id']
        else:
            doc = parse(env,c['source'])
            assert r['canonical'] == expected['canonical'] == print_document(env,doc), c['id']
            assert r['ast'] == expected['ast']


def test_rust_shared_identities(rust_executable):
    cases = fixture('identity'); results = invoke(rust_executable,cases)
    for c,r in zip(cases,results,strict=True):
        env = Environment.from_dict(c['environment']); doc = document_from_data(env,c['ast'])
        model = FiniteModel.from_dict(env,c['model'])
        expected = c['expected_identity']
        assert r['environment_id'] == env.environment_id
        assert r['meaning_id'] == meaning_id(env,doc)
        assert r['formula_meaning_ids'] == [meaning_id(env,f) for f in doc.formulas]
        assert r['model_id'] == model.model_id
        assert {k:r[k] for k in expected} == expected, c['id']


def test_rust_shared_wire(rust_executable):
    for c in fixture('wire'):
        run = subprocess.run([str(rust_executable),'canonical-json'],input=c['raw'],text=True,capture_output=True,timeout=10)
        if c.get('reject'):
            with pytest.raises(VEError): loads_json(c['raw'])
            assert run.returncode == 2, c['id']
        else:
            assert run.returncode == 0, c['id']
            assert run.stdout.encode() == c['expected'].encode() == canonical_json(loads_json(c['raw'])), c['id']


def test_rust_shared_validation(rust_executable):
    cases = fixture('validation'); results = invoke(rust_executable,cases,errors=True)
    for c,r in zip(cases,results,strict=True):
        with pytest.raises(VEError) as exc:
            env = Environment.from_dict(c['environment'])
            FiniteModel.from_dict(env,c['model']); document_from_data(env,c['ast'])
        assert r['error']['code'] == c['expected_error'] == exc.value.code, c['id']


def test_rust_shared_search(rust_executable):
    from dataclasses import asdict
    from ve.ast import formula_from_data
    from ve.search import find_countermodel, check_countermodel
    cases = fixture('search'); results = invoke(rust_executable,cases)
    for c,r in zip(cases,results,strict=True):
        env = Environment.from_dict(c['environment'])
        premises = [formula_from_data(env,f) for f in c['premises']]
        conclusion = formula_from_data(env,c['conclusion'])
        if 'expected_check' in c:
            model = FiniteModel.from_dict(env,c['model'])
            expected = json.loads(json.dumps(asdict(check_countermodel(env,premises,conclusion,model))))
            assert {k:r[k] for k in expected} == c['expected_check'] == expected
        else:
            py = find_countermodel(env,premises,conclusion,**{k:c[k] for k in ('max_domain_size','max_models','max_evaluations')})
            assert {k:v for k,v in py.to_dict().items() if v is not None} == c['expected_search']
            assert r['status'] == py.status, c['id']
            if c['compare_counts']:
                assert r['models_checked'] == py.models_checked, c['id']
                assert r['evaluations'] == py.evaluations, c['id']
            if r['status'] == 'Found':
                assert check_countermodel(env,premises,conclusion,FiniteModel.from_dict(env,r['model'])).valid


def test_seeded_5000_case_fuzz(rust_executable):
    run = subprocess.run([sys.executable,str(ROOT/'conformance/fuzz.py'),'--rust',str(rust_executable),
                          '--count','5000'],cwd=ROOT,text=True,capture_output=True,timeout=240)
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(run.stdout)
    assert result['agreements'] == 5000


@pytest.fixture(scope='session')
def lean_shared_executable():
    lake = shutil.which('lake')
    if not lake: pytest.skip('lake is not available')
    run = subprocess.run([lake,'build'],cwd=ROOT/'lean',text=True,capture_output=True,timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    return ROOT/'lean/.lake/build/bin/ve_conformance'


@pytest.mark.parametrize('name',['evaluation','parser','identity','validation'])
def test_lean_same_extended_files(lean_shared_executable,name):
    cases = fixture(name)
    run = subprocess.run([str(lean_shared_executable),str(ROOT/f'conformance/{name}.json')],
                         cwd=ROOT,text=True,capture_output=True,timeout=90)
    assert run.returncode == int(name in ('parser','validation')), run.stdout + run.stderr
    for c,r in zip(cases,json.loads(run.stdout),strict=True):
        expected_error = ('expected_error' in c or 'error_code' in c.get('expected_parser',{}))
        assert (r['status']=='error') == expected_error, c['id']
        if not expected_error:
            assert r['canonical'] == c.get('expected_parser',{}).get('canonical',c['source']), c['id']
            if name in ('evaluation','identity'): assert r['values'] == c['expected'],c['id']
