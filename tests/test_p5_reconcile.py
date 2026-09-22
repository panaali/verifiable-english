"""Interrupted revision calls stay charged inside both existing budget caps."""
from decimal import Decimal
import json

from experiments import p5
from ve_experiments.paid import Ledger, PaidRequest, PaidReply, cost


def test_cli_reconciles_study_and_revision_calls_without_dispatch(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(p5, 'HERE', tmp_path)
    study = Ledger(tmp_path/'runs/study/costs.jsonl', 40)
    study.allowance('v7-paraphrase-envelope', '.40')
    smoke = PaidRequest('provider-preflight/p5/replication', 'replication', [], 100, 100)
    study.reserve(smoke)
    book = Ledger(tmp_path/'runs/revision-v7/paraphrase-costs.jsonl', '.40')
    book.reserve_block('shared-paraphrase', '.40')
    req = PaidRequest('rewrite-v7/materials/x', 'replication', [], 4096, 3072,
                      metadata={'block_id': 'shared-paraphrase', 'role': 'paraphrase'})
    complete = PaidRequest('rewrite-v7/materials/complete', 'replication', [], 4096, 3072,
                           metadata=req.metadata)
    book.reserve(complete)
    book.complete(complete, PaidReply('original', 1, 1, 0, 0, 'rev', {}, {}))
    book.reserve(req)
    original = book.path.read_bytes()
    assert p5.main(['reconcile']) == 0
    result = json.loads(capsys.readouterr().out)
    ceiling = cost('replication', 4096, 3072, role='paraphrase')
    assert Decimal(result['interrupted_charge_usd']) == ceiling + cost('replication', 100, 100)
    assert result['generation_calls'] == 0
    assert book.path.read_bytes().startswith(original)
    assert book.cached_reply(complete).text == 'original'
    assert book.cached_reply(req) is None
    with study.locked() as (_, rows):
        assert Ledger.state(rows)[1] == Decimal('.40') + cost('replication', 100, 100)
        assert sum(r['event'] == 'allowance' for r in rows) == 1
    with book.locked() as (_, rows):
        pending, spent, _, _, blocked = Ledger.state(rows)
    assert not blocked and set(pending) == {'block:shared-paraphrase'}
    assert spent + sum(pending.values()) == Decimal('.40')
    settled = book.path.read_bytes()
    assert p5.main(['reconcile']) == 0
    result = json.loads(capsys.readouterr().out)
    assert Decimal(result['interrupted_charge_usd']) == 0
    assert book.path.read_bytes() == settled
    book.reserve_block('shared-paraphrase', '.40', resume=True)
    book.reserve(req)
