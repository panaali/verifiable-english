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
    run = subprocess.run([cargo, 'build', '-j', '1', '--locked', '--release', '--manifest-path', str(ROOT/'rust/Cargo.toml')],
                         cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
    assert run.returncode == 0, run.stdout + run.stderr
    return ROOT/'rust/target/release/ve'


def invoke(executable, cases, errors=False):
    run = subprocess.run([str(executable),'conformance'], input=json.dumps(cases), text=True,
                         capture_output=True, timeout=60)
    assert run.returncode == int(errors), run.stdout + run.stderr
    return json.loads(run.stdout)


@pytest.mark.skip(reason="Rust supports relational-fol@0 only; conformance/closure.json requires closure@0 (see conformance/README.md)")
def test_rust_closure_evaluation(rust_executable):
    cases = fixture('closure')
    results = invoke(rust_executable, cases)
    for case, result in zip(cases, results, strict=True):
        assert result['values'] == case['expected'], case['id']
        assert result['canonical'] == case['source'], case['id']


def test_rust_shared_evaluation(rust_executable):
    cases = fixture('evaluation'); results = invoke(rust_executable, cases)
    assert len(cases) == len(results) == 701
    assert sum(len(c['ast']) for c in cases) == 4912
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
            with pytest.raises(VEError) as exc: loads_json(c['raw'])
            assert run.returncode == 2, c['id']
            assert exc.value.code == c['expected_error'] == json.loads(run.stderr)['error']['code'], c['id']
        else:
            assert run.returncode == 0, c['id']
            assert run.stdout.encode() == c['expected'].encode() == canonical_json(loads_json(c['raw'])), c['id']


def test_rust_shared_countermodels(rust_executable):
    from dataclasses import asdict
    from ve.search import check_countermodel
    cases = fixture('countermodels'); results = invoke(rust_executable, cases)
    assert len(cases) == len(results) == 708
    for c, r in zip(cases, results, strict=True):
        env = Environment.from_dict(c['environment'])
        model = FiniteModel.from_dict(env, c['model'])
        doc = document_from_data(env, c['premises'] + [c['conclusion']])
        expected = json.loads(json.dumps(asdict(check_countermodel(env, doc.formulas[:-1], doc.formulas[-1], model))))
        assert r['id'] == c['id']
        assert r['valid'] == c['expected_refutes']
        assert {k: r[k] for k in expected} == expected, c['id']


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
    if not os.environ.get('VE_LEAN_PREBUILT'):
        run = subprocess.run([lake,'build'],cwd=ROOT/'lean',text=True,capture_output=True,timeout=180)
        assert run.returncode == 0, run.stdout + run.stderr
    assert (ROOT/'lean/.lake/build/bin/ve_conformance').exists()
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


def test_rust_source_binding_and_cli_outcomes(rust_executable,tmp_path):
    case = fixture('evaluation')[0]
    mismatched = {**case,'source':'true.\n'}
    rejected = invoke(rust_executable,mismatched,errors=True)[0]
    assert rejected['error']['code'] == 'TypeMismatch'
    assert rejected['error']['message'] == 'source/AST mismatch'
    env = tmp_path/'environment.json'; env.write_text(json.dumps(case['environment']))
    model = tmp_path/'model.json'; model.write_text(json.dumps(case['model']))
    source = tmp_path/'source.ve'
    for text,code,status in [('true.\n',0,'Satisfied'),('false.\n',1,'Violated'),('true.\r\n',2,'error')]:
        source.write_bytes(text.encode())
        run = subprocess.run([str(rust_executable),'evaluate','--env',str(env),'--model',str(model),
                              '--source',str(source)],text=True,capture_output=True,timeout=10)
        assert run.returncode == code
        assert json.loads(run.stdout or run.stderr)['status'] == status
    premises = tmp_path/'premises.ve'; premises.write_text('')
    conclusion = tmp_path/'conclusion.ve'; conclusion.write_text('false.\n')
    command = [str(rust_executable),'countermodel','--env',str(env),'--premises',str(premises),
               '--conclusion',str(conclusion)]
    for check in (False, True):
        args = ([str(rust_executable), 'check-countermodel', *command[2:], '--model', str(model)]
                if check else command)
        run = subprocess.run(args,text=True,capture_output=True,timeout=10)
        assert run.returncode == 2
        assert json.loads(run.stderr)['error']['code'] == 'SyntaxError'
    premises.write_text('true.\n')
    run = subprocess.run(command,text=True,capture_output=True,timeout=10)
    assert run.returncode == 0, run.stderr
    found = json.loads(run.stdout); assert found['status'] == 'Found'
    model.write_text(json.dumps(found['model']))
    run = subprocess.run([str(rust_executable),'check-countermodel',*command[2:],'--model',str(model)],
                         text=True,capture_output=True,timeout=10)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['valid']
    run = subprocess.run([*command,'--max-models','0'],text=True,capture_output=True,timeout=10)
    assert run.returncode == 2
    assert json.loads(run.stdout)['status'] == 'ResourceLimit'


@pytest.mark.parametrize('oversized_bytes,terminated', [
    (16 * 1024 * 1024, True),  # newline is the byte over the cap
    (16 * 1024 * 1024 + 100_000, True),
    (16 * 1024 * 1024 + 100_000, False),
])
def test_jsonl_continues_after_oversized_record(rust_executable, tmp_path, oversized_bytes, terminated):
    case = fixture('evaluation')[0]
    valid = json.dumps(case).encode() + b'\n'
    stream = tmp_path / 'oversized.jsonl'
    stream.write_bytes(valid + b'x' * oversized_bytes + (b'\n' + valid + valid if terminated else b''))
    run = subprocess.run([str(rust_executable), 'jsonl', str(stream)], capture_output=True, text=True, timeout=30)
    assert run.returncode == 1, run.stderr
    records = [json.loads(line) for line in run.stdout.splitlines()]
    assert len(records) == (4 if terminated else 2)
    assert records[0]['id'] == case['id']
    assert records[1]['error']['code'] == 'ResourceLimit'
    for record in records[2:]:
        assert record['status'] == 'ok'
        assert record['id'] == case['id']
        assert record['values'] == case['expected']


def test_rust_printer_resource_limit(rust_executable):
    case = fixture('evaluation')[0]
    case.pop('source')
    # 9,000 AST nodes is valid, but printing these statements exceeds 64 KiB.
    case['ast'] = [['implies',['top'],['top']]] * 3000
    env = Environment.from_dict(case['environment'])
    doc = document_from_data(env,case['ast'])
    with pytest.raises(VEError) as exc: print_document(env,doc)
    assert exc.value.code == 'ResourceLimit'
    result = invoke(rust_executable,case,errors=True)[0]
    assert result['error']['code'] == 'ResourceLimit'
