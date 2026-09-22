import json
from pathlib import Path
from types import SimpleNamespace
from decimal import Decimal

import pytest

from experiments import p1
from experiments import p1_preflight as gates


def test_full_inventory_joint_replay_and_pushback():
    rows = list(gates.token_requests())
    initial = [(r, n) for r, n in rows if r.metadata['role'] == 'initial']
    assert len(initial) == 1336
    assert len({r.metadata['item_id'] for r, _ in initial}) == 200
    replay = [(r, n) for r, n in rows if r.metadata['role'] == 'replay']
    assert len(replay) == 200
    assert all(n == 1024 and any(m['role'] == 'tool' for m in r.messages) for r, n in replay)
    pushes = [(r, n) for r, n in rows if r.metadata['role'] == 'attacker']
    assert len(pushes) == 140
    assert all(n == (5888 if r.metadata['arm'] == 'R' else 4864) for r, n in pushes)
    assert all(len(r.messages) >= 10 for r, _ in pushes)
    assert len(list(gates.token_requests('weak'))) == 1536


def test_amended_bounds_and_inventory_agree():
    from experiments.prereg_inventory import P1_PUSHBACK_INPUT_BOUNDS
    for request, _ in gates.token_requests():
        arm, phase = request.metadata['arm'], request.metadata['role']
        original = {'initial': 3072, 'replay': 4096, 'attacker': 4096, 'pushback': 6144}[phase]
        expected = (P1_PUSHBACK_INPUT_BOUNDS[arm][phase == 'pushback'] if phase in ('attacker', 'pushback')
                    else 6800 if arm in ('A', 'R') else original)
        assert request.max_input_tokens == expected
    for name, plan in p1.inventory()['budget_scenarios'].items():
        actual = p1.split_ceiling(name, 'dev') + p1.split_ceiling(name, 'scored') + Decimal(1)
        assert abs(actual - Decimal(str(plan['max_scheduled_api_usd']))) <= Decimal('.00000001')
    assert p1.inventory()['budget_scenarios']['full_256']['within_study_cap'] is False
    item = p1.materials('dev')[0]
    assert p1.request(item, 'A', 'pro', 4096, phase='probe').max_input_tokens == 3072


def test_overbudget_schedule_blocks_before_provider_calls(monkeypatch):
    monkeypatch.setattr(p1, 'STUDY_CAP_USD', 30)
    monkeypatch.setattr(p1, 'VertexBackend', lambda: pytest.fail('generation forbidden'))
    with pytest.raises(p1.BudgetExceeded, match='selected schedule ceiling exceeds'):
        p1.run_split('dev', 30)


def test_tokenizer_counts_every_fixture_and_fails_on_overflow(monkeypatch):
    req = next(gates.token_requests())[0]
    monkeypatch.setattr(gates, 'token_requests', lambda judge: iter([(req, 0), (req, 256)]))
    calls = []
    backend = SimpleNamespace(count=lambda r: calls.append(r) or 3000)
    report = gates.tokenize(backend)
    assert len(calls) == 2 and not report['passed']
    assert [r['passed'] for r in report['counts']] == [True, False]


def test_failed_receipt_replaces_old_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    p1.write_json(tmp_path / 'checks/example.json', {'passed': True, 'freeze_sha256': 'old'})
    def fail():
        raise RuntimeError('real failure')
    result = gates.receipt('example', 'new', fail)
    assert result['passed'] is False and result['freeze_sha256'] == 'new'
    assert json.loads((tmp_path / 'checks/example.json').read_text()) == result


def test_timestamp_binds_proof_to_current_hash_file(tmp_path, monkeypatch):
    root = tmp_path
    here = root / 'experiments/P1-deference'
    here.mkdir(parents=True)
    (here / 'PREREG.md').write_text('prereg')
    hashes = root / 'experiments/PREREG-HASHES.txt'
    hashes.write_text(p1.sha(here / 'PREREG.md') + '  experiments/P1-deference/PREREG.md\n')
    hashes.with_suffix('.txt.ots').write_bytes(b'proof')
    monkeypatch.setattr(p1, 'ROOT', root)
    monkeypatch.setattr(p1, 'HERE', here)
    output = f"File sha256 hash: {p1.sha(hashes)}\nverify PendingAttestation('calendar')"
    monkeypatch.setattr(gates.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout=output, stderr=''))
    assert gates.timestamp()['passed']
    assert not gates.timestamp()['bitcoin_confirmed']
    hashes.write_text(hashes.read_text() + '\n')
    assert not gates.timestamp()['passed']


def test_semantic_gate_real_pairs():
    result = gates.semantic_pairs()
    assert result['passed'] and len(result['pairs']) == 200
