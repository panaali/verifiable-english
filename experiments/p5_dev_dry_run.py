"""Offline delivery smoke; synthetic replies are never trials or ratings."""
from copy import deepcopy
from types import SimpleNamespace
from experiments import p5 as p
from experiments.p5_dev_revision import ENVIRONMENT_EXAMPLE
from experiments.p5_oracle import author_graph
from ve_experiments.paid import packed, digest


def artifact(item):
    packet = item['payload']
    nodes = packet['premises'] + packet['nodes']
    return {'environment': deepcopy(ENVIRONMENT_EXAMPLE),
        'claims': [{'id': n['id'], 'source': '@sample is marked.\n'} for n in nodes],
        'edges': [{'id': 'edge'+str(k), 'premises': n['parents'], 'conclusion': n['id']}
                  for k, n in enumerate(packet['nodes'])],
        'root': packet['root'],
        'alignment': {n['id']: [packet['records'][0]['id']] for n in nodes},
        'queries': [], 'splits': []}


def dry_run():
    results = []
    for item in p.materials('dev'):
        for arm in ('X', 'VE'):
            requests = []
            authored = artifact(item)
            def call(req):
                requests.append(req)
                stage = req.metadata['role']
                answer = {'verdict': 'unknown', 'issue_type': 'unknown', 'locations': [],
                          'explanation': 'Synthetic delivery test; no source-fidelity judgment.'}
                if stage == 'judge': return SimpleNamespace(text=packed(answer))
                if arm == 'VE': value = authored if stage != 'critic' else {'queries': [], 'splits': []}
                else:
                    value = {'author': {'commitment': 'FIXED', 'argument': 'PRIVATE_DEFENSE'},
                        'critic': {'questions': ['Q1', {'question': 'Q2'}, 'Q3']},
                        'followup': {'question': 'Q4'}}.get(stage)
                return SimpleNamespace(text='```json\n'+packed(value)+'\n```' if value is not None else 'ISOLATED_REPLY')
            client = SimpleNamespace(call=call, backend=SimpleNamespace(count=lambda r: len(r.messages[-1]['content'].split())))
            events = []
            rows = p.execute(item, arm, client, {'pro': client, 'replication': client}, local_events=events)
            assert all(not r['protocol_error'] and not r['author_failure'] and not r['unresolved'] for r in rows)
            assert all(req.identity.startswith('study-v10/dev/') for req in requests)
            entry = {'item_id': item['id'], 'arm': arm, 'judgments': len(rows), 'passed': True}
            if arm == 'X':
                answers = [req for req in requests if req.metadata['role'] in ('answer', 'followup_answer')]
                assert len(answers) == 4
                for req, q in zip(answers, ('Q1', 'Q2', 'Q3', 'Q4')):
                    assert req.messages[-1]['content'] == p.packet(item, arm)+'\nFrozen commitment:\nFIXED\nOne question:\n'+q
                entry.update(isolated_answers=3, adaptive_answers=1)
            else:
                assert len(events) == 2 and all(e['ok'] and e['graph'] for e in events)
                # A valid repair reply traverses the same real checker; normal
                # success does not buy an unnecessary repair call.
                repair = author_graph(p.protocol_json('```json\n'+packed(authored)+'\n```'), item['payload'])
                assert repair['ok']
                entry.update(artifact_sha256=digest(authored), author_replay=True,
                             repair_replay=repair['ok'], defender_replay=True)
            results.append(entry)
    return {'passed': True, 'generation_calls': 0, 'paid_calls': 0,
        'synthetic_only': True, 'source_fidelity_asserted': False,
        'scope': '12 X protocols with 48 isolated answers; 36 synthetic VE author/repair/defender checker replays. No efficacy evidence.',
        'results': results}


if __name__ == '__main__':
    from experiments.p5_materials import write_json
    result = dry_run()
    write_json(p.HERE/'checks/dev-rerun-dry-run.json', result)
    print(packed({k:v for k,v in result.items() if k!='results'}))
