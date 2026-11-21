"""The shadow-corpus seal of English in Lean is self-consistent and current: it is a generated file
(`english-lean-seal` in tools/regen_generated.py), and its own check finds every kind of drift."""
import copy
import json

import pytest

from ve.wire import digest

from conformance import english_lean_seal as Z


def test_seal_identity_covers_its_content():
    seal = json.loads(Z.SEAL.read_text())
    body = {k: v for k, v in seal.items() if k != 'seal_id'}
    assert seal['seal_id'] == digest(Z.DOMAIN, body)
    assert {e['kind'] for e in seal['sources']} == {'entry-point caller', 'corpus source'}
    assert len({e['path'] for e in seal['sources']}) == len(seal['sources'])
    assert any(row['stream'] == 'english-surface' for row in seal['generated'])


def test_the_committed_seal_is_current():
    """srccov-rl-anthropic-rsp-1121 F1 (the review's probe): a rebase resolved the seal, a later commit edited a
    sealed test (tests/test_english_statement_blocks.py), and the seal kept main's hash. The committed seal is
    the writer's output on this tree: no source changed, missing or unsealed, and no derived part stale."""
    assert Z.check(json.loads(Z.SEAL.read_text())) == []
    assert json.loads(Z.SEAL.read_text()) == Z.build()


def _reseal(seal: dict) -> dict:
    body = {k: v for k, v in seal.items() if k != 'seal_id'}
    return {**body, 'seal_id': digest(Z.DOMAIN, body)}


def _mutants():
    """One seal per kind of drift, each otherwise current (its seal_id recomputed unless the id is the fault)."""
    seal = Z.build()
    changed = copy.deepcopy(seal)
    changed['sources'][0]['sha256'] = '0' * 64
    yield 'changed source', _reseal(changed), f"changed: {seal['sources'][0]['path']}"
    missing = copy.deepcopy(seal)
    missing['sources'].append({'path': 'tests/no_such_sealed_file.py', 'kind': 'corpus source', 'sha256': '0' * 64})
    yield 'missing source', _reseal(missing), 'missing: tests/no_such_sealed_file.py'
    unsealed = copy.deepcopy(seal)
    dropped = unsealed['sources'].pop()
    yield 'unsealed source', _reseal(unsealed), f"unsealed: {dropped['path']}"
    stream = copy.deepcopy(seal)
    stream['generated'][0] = {**stream['generated'][0], 'seed': stream['generated'][0]['seed'] + 1}
    yield 'stale stream', _reseal(stream), 'stale: generated'
    pilot = copy.deepcopy(seal)
    pilot['pilots'] = pilot['pilots'][1:]
    yield 'stale pilot', _reseal(pilot), 'stale: pilots'
    fmt = copy.deepcopy(seal)
    fmt['format'] = 've.english-lean-corpus-seal@0'
    yield 'stale format', _reseal(fmt), 'stale: format'
    yield 'forged id', {**seal, 'seal_id': '0' * 64}, 'stale: seal_id'
    yield 'extra key', _reseal({**seal, 'note': 'x'}), 'stale: seal_id'


@pytest.mark.parametrize('name, seal, line', list(_mutants()), ids=[m[0] for m in _mutants()])
def test_the_check_reports_each_kind_of_drift(name, seal, line):
    """Before F1's fix the check compared only the source hashes: a stale stream digest, pilot pin, format or
    seal_id passed it. Each drift is reported, and only its own line."""
    assert Z.check(seal) == [line], name
