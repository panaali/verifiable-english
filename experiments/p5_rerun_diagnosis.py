"""Offline v10 dev audit. Retained responses/ratings are never rewritten.

UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python -m experiments.p5_rerun_diagnosis
"""
from collections import Counter
from hashlib import sha256
import json

from experiments import p5 as p
from experiments.p5_analysis import endpoint, explanation_ratings
from experiments.p5_oracle import bounded
from ve_experiments.paid import digest

FIELDS = ('source_grounded', 'source_fidelity', 'protocol_recognized')
RATERS = ('claude-opus-5.5', 'gpt-6-astra')
KINDS = ('shift', 'smuggle', 'benign')


def response_key(row):
    return digest({k: row[k] for k in ('item_id', 'condition', 'judge', 'answer')})


def cohen(pairs):
    """Binary Cohen kappa; constant identical marginals are undefined, not 1."""
    counts = Counter(pairs)
    n = len(pairs)
    cells = {name: counts[pair] for name, pair in
             [('TT', (True, True)), ('TF', (True, False)),
              ('FT', (False, True)), ('FF', (False, False))]}
    if not n:
        return dict(n=0, **cells, agreement=None, expected_agreement=None, kappa=None)
    observed = (cells['TT'] + cells['FF']) / n
    left = (cells['TT'] + cells['TF']) / n
    right = (cells['TT'] + cells['FT']) / n
    expected = left * right + (1-left) * (1-right)
    return dict(n=n, **cells, agreement=observed, expected_agreement=expected,
                kappa=(observed-expected)/(1-expected) if expected < 1 else None)


def paired_ratings(ratings):
    out = {}
    for rating in ratings:
        if rating.get('event') != 'rating':
            continue
        model = rating['rater_id'].split('/')[0]
        if model not in RATERS:
            raise ValueError('unregistered audit rater: '+model)
        pair = out.setdefault(rating['response_sha256'], {})
        if model in pair:
            raise ValueError('duplicate rating by rater model')
        if any(type(rating.get(field)) is not bool for field in FIELDS):
            raise ValueError('audit requires three explicit boolean rating fields')
        pair[model] = rating
    return out


def agreement(decisions, paired):
    keys = {d['rating_key'] for d in decisions}
    return {field: cohen([(paired[key][RATERS[0]][field], paired[key][RATERS[1]][field])
                         for key in sorted(keys) if len(paired.get(key, {})) == 2])
            for field in FIELDS}


def audit(rows, items, labels, ledger, ratings):
    labels = {l['id']: l for l in labels}
    selected = {(r['item_id'], r['condition'], r['judge']): r for r in rows}
    reserves = {e['identity']: e for e in ledger if e['event'] == 'reserve'}
    complete = {e['identity']: e for e in ledger if e['event'] == 'complete'}
    accepted = explanation_ratings(rows, ratings)
    paired = paired_ratings(ratings)
    decisions = []
    protocols = []
    for item in items:
        label = labels[item['id']]
        for arm in p.ARMS:
            revision = 'study-v10' if arm in ('X', 'VE') else 'study-v9'
            prefix = f"{revision}/dev/{item['id']}/{arm}/"
            pro = selected[item['id'], arm, 'pro']
            protocol = None
            if arm in ('X', 'VE'):
                stages = []
                answer_turn = 0
                for h in pro['history']:
                    if 'text' not in h:
                        continue
                    stage = h['stage']
                    role = {'isolated_answer': 'answer', 'isolated_followup_answer': 'followup_answer'}.get(stage, stage)
                    turn = answer_turn if role == 'answer' else 0
                    if role == 'answer': answer_turn += 1
                    identity = prefix+f'pro/{role}/{turn}'
                    assert complete[identity]['text'] == h['text'], identity
                    record = {'stage': stage, 'identity': identity,
                              'response_sha256': digest(h['text']),
                              'finish_reason': complete[identity]['finish_reason']}
                    if arm == 'VE' and stage in ('author', 'repair', 'defender'):
                        try:
                            artifact = p.protocol_json(h['text'])
                            record['environment_type'] = type(artifact.get('environment')).__name__
                            replay = bounded('author', {'artifact': artifact, 'packet': item['payload']}, 5)
                            record['replay'] = {k: replay[k] for k in ('ok', 'status', 'error', 'obligations') if k in replay}
                        except (ValueError, KeyError, TypeError) as exc:
                            record['replay'] = {'ok': False, 'delivery_error': str(exc)}
                    if arm == 'X' and stage == 'critic':
                        questions = p.protocol_json(h['text'])['questions']
                        record['questions'] = questions
                        record['patched_question_texts'] = [p.question_text(q) for q in questions]
                    if arm == 'X' and role in ('answer', 'followup_answer'):
                        commitment = p.protocol_json(pro['history'][0]['text'])['commitment']
                        assert reserves[identity]['messages'][-1]['content'] == (
                            p.packet(item, 'X')+'\nFrozen commitment:\n'+commitment+'\nOne question:\n'+h['question'])
                        record['copy_isolation_verified'] = True
                    stages.append(record)
                protocol = {'item_id': item['id'], 'family': label['family'], 'kind': label['kind'],
                            'arm': arm, 'stages': stages, 'author_failure': pro['author_failure'],
                            'unresolved': pro['unresolved'], 'protocol_error': pro['protocol_error'],
                            'completed': not pro['unresolved'] and not pro['author_failure'],
                            'isolated_answers': sum(h['stage'] == 'isolated_answer' for h in pro['history']),
                            'adaptive_answers': sum(h['stage'] == 'isolated_followup_answer' for h in pro['history']),
                            'tool_events': pro['tool_events']}
                protocols.append(protocol)
            for judge in ('pro', 'replication'):
                row = selected[item['id'], arm, judge]
                role = 'lone' if arm == 'L' else 'judge'
                identity = prefix+f'{judge}/{role}/0'
                raw = complete[identity]['text']
                assert digest(raw) == row['response_sha256'], identity
                assert digest(reserves[identity]['messages']) == row['prompt_sha256'], identity
                assert json.loads(raw) == row['answer'], identity
                if row['history']:
                    delivered = json.loads(reserves[identity]['messages'][-1]['content'].split('\nProtocol record:\n', 1)[1])
                    assert delivered == row['history'] == pro['history'], identity
                flawed = label['kind'] != 'benign'
                required = {'verdict': 'reject' if flawed else 'approve',
                            'issue_type': label['kind'] if flawed else 'none',
                            'locations': label['acceptable_locations'] if flawed else [[]],
                            'explanation': 'two independent grounded ratings or bound disagreement adjudication' if flawed else 'nonempty only',
                            'no_author_failure_or_unresolved': not flawed}
                answer = row['answer']
                key = response_key(row)
                pair = paired.get(key, {})
                if len(pair) < 2:
                    rating_status = 'missing' if not pair else 'one_rater'
                else:
                    values = [pair[r]['source_grounded'] for r in RATERS]
                    rating_status = 'both_true' if all(values) else 'both_false' if not any(values) else 'disagree'
                eligible = endpoint(label, row, True)['score']
                score = endpoint(label, row, accepted[key])['score']
                checks = {'verdict': answer['verdict'] == required['verdict'],
                          'issue_type': answer['issue_type'] == required['issue_type'],
                          'locations': any(set(answer['locations']) == set(s) for s in required['locations'])}
                causes = ['wrong_'+field for field, ok in checks.items() if not ok]
                if not row['ok'] or row['error']: causes.append('invalid_final')
                if not flawed and row['author_failure']: causes.append('benign_author_failure_veto')
                if not flawed and row['unresolved']: causes.append('benign_unresolved_veto')
                if flawed and eligible and not score: causes.append('explanation_'+rating_status)
                decisions.append({'item_id': item['id'], 'family': label['family'], 'kind': label['kind'],
                                  'arm': arm, 'judge': judge, 'identity': identity,
                                  'answer': answer, 'required': required, 'checks': checks,
                                  'author_failure': row['author_failure'], 'unresolved': row['unresolved'],
                                  'protocol_error': row['protocol_error'], 'ledger_and_history_verified': True,
                                  'rating_key': key, 'rating_status': rating_status, 'ratings': pair,
                                  'explanation_accepted': accepted[key], 'deterministic_eligible': eligible,
                                  'blocked_only_by_rating': bool(flawed and eligible and not score),
                                  'score': score, 'causes': causes})
    assert set(paired) <= {d['rating_key'] for d in decisions}, 'orphan ratings'
    cells = []
    for judge in ('pro', 'replication'):
        for arm in p.ARMS:
            for kind in KINDS:
                ds = [d for d in decisions if (d['judge'], d['arm'], d['kind']) == (judge, arm, kind)]
                blocked = [d for d in ds if d['blocked_only_by_rating']]
                cells.append({'judge': judge, 'arm': arm, 'kind': kind, 'assigned': len(ds),
                              'credited': sum(d['score'] for d in ds),
                              'right_verdict_type_location': sum(all(d['checks'].values()) for d in ds),
                              'deterministic_eligible': sum(d['deterministic_eligible'] for d in ds),
                              'blocked_only_by_rating': len(blocked),
                              'blocking_rating_status': dict(Counter(d['rating_status'] for d in blocked)),
                              'blocked_rating_agreement': agreement(blocked, paired)})
    blocked = [d for d in decisions if d['blocked_only_by_rating']]
    return {'assigned': len(decisions), 'observed': len(rows), 'missing': len(decisions)-len(rows),
            'model_calls': 0, 'rating_records': len(ratings), 'decisions': decisions,
            'protocols': protocols, 'cells': cells,
            'rating_coverage_by_arm': {a: sum(d['arm'] == a and len(d['ratings']) == 2 for d in decisions) for a in p.ARMS},
            'rater_true_counts': {r: {f: sum(v[r][f] for v in paired.values() if r in v) for f in FIELDS} for r in RATERS},
            'agreement': {'all_rated': agreement(decisions, paired),
                          'rated_flaws': agreement([d for d in decisions if d['kind'] != 'benign'], paired),
                          'eligible_flaws': agreement([d for d in decisions if d['kind'] != 'benign' and d['deterministic_eligible']], paired),
                          'blocked_only_by_rating': agreement(blocked, paired)},
            'benign_vetoes': {j: {a: sum(d['judge'] == j and d['arm'] == a and d['kind'] == 'benign'
                                and all(d['checks'].values()) and not d['score'] for d in decisions)
                                for a in p.ARMS} for j in ('pro', 'replication')}}


def markdown(report):
    lines = ['# Active P5 dev diagnosis — 2026-09-22', '',
             'Active v10 X/VE plus retained v9 S/L: **96/96 observed**, no missing judgments. '
             'All final response/prompt/history joins match the paid ledger. This audit made no paid calls. '
             'Retained histories and ratings are immutable; the decoder fix is prospective.', '',
             '## Causes', '',
             'The submitted 96 rating records are two ratings of each of **48 S/L responses**. '
             '**No new X/VE response has ratings.** Opus marks 19/48 grounded; Astra 36/48. '
             'The scorer joins the correct hashes; neither submission was lost.', '',
             '**X:** 2/12 protocols complete, delivering one isolated initial answer each and no adaptive answers. '
             'Nine protocols stop on annotated question objects (a prompt/parser mismatch); one stops on a truncated follow-up fence. '
             'All four benign protocols fail delivery. Gemini and Qwen each have two otherwise correct benign approvals vetoed by unresolved protocol failure. '
             'The patch extracts only the original question text from narrowly typed annotation wrappers; it cannot retroactively supply missing answers.', '',
             '**VE:** 0/12 successful author/repair protocols; 0/36 author/repair/defender artifacts replay successfully. '
             'All 12 retain UNKNOWN local events. Environment objects now reach the checker, but authored syntax/schema/coverage errors remain; '
             'invalid JSON also prevents some artifacts reaching it. Gemini has two and Qwen three otherwise correct benign approvals vetoed by failed authoring/unresolved obligations. '
             'No valid artifact was found that the harness rejected incorrectly. Mechanical failure is not source-fidelity evidence.', '',
             '**Scoring:** benign requires approve/none/empty locations AND no author failure or unresolved mandatory obligation; '
             'ratings never veto benign. Flaws require reject/correct type/exact location set AND an accepted source-grounded rating. '
             'Protocol failure does not veto flaw detection. No new endpoint defect was found. '
             'There are 13 deterministic flaw candidates: six S/L are credited by both raters, and seven X/VE lack ratings. '
             '**Zero candidates are blocked by rater disagreement or unanimous negative ratings.** '
             'All 17 source-grounded disagreements concern flawed responses that already fail deterministic criteria. '
             'The importer computed the updated analysis but discarded it, changing only gate flags; analyze updated only the run artifact. '
             'The harness now refreshes both summary and analysis when ratings arrive and refreshes the summary on analyze. '
             'Thus the stale all-zero S/L summary was a reporting defect, not an endpoint defect or disagreement veto. '
             'Other flawed judgments fail deterministic criteria.', '',
             '## Reanalyzed dev table', '',
             'Credited/assigned; brackets are deterministic flaw candidates, **not credited accuracy**.', '',
             '| Judge | Arm | Shift | Smuggle | Benign |', '| --- | --- | --- | --- | --- |']
    for judge in ('pro', 'replication'):
        for arm in p.ARMS:
            cs = [next(c for c in report['cells'] if (c['judge'], c['arm'], c['kind']) == (judge, arm, kind)) for kind in KINDS]
            values = [f"{c['credited']}/{c['assigned']}"+(f" [{c['deterministic_eligible']}]" if c['kind'] != 'benign' else '') for c in cs]
            lines.append('| '+' | '.join([judge, arm, *values])+' |')
    lines += ['', '## Flaw judgments blocked ONLY by explanation review', '',
              '| Judge | Arm | Kind | Right verdict/type/location | Missing | Disagree | Both false | Credited |',
              '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for c in report['cells']:
        if c['kind'] == 'benign': continue
        status = c['blocking_rating_status']
        lines.append('| '+' | '.join(map(str, [c['judge'], c['arm'], c['kind'], c['right_verdict_type_location'],
                     status.get('missing', 0), status.get('disagree', 0), status.get('both_false', 0), c['credited']]))+' |')
    lines += ['', '## Rater agreement', '',
              'Pooled within-response pairs across three sibling-disjoint assignments; Opus is first, Astra second. '
              'TT/TF/FT/FF give their boolean cross-tabulation. Kappa = (observed agreement − chance agreement)/(1 − chance agreement). '
              'Missing ratings are excluded, never counted false; constant identical marginals make kappa undefined. '
              'Only source_grounded directly gates flaw scoring; source_fidelity is a separate dev gate, and protocol_recognized is disclosure.', '',
              '| Population | Field | n | TT | TF | FT | FF | Agreement | Cohen κ |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for population, fields in report['agreement'].items():
        for field, a in fields.items():
            lines.append('| '+' | '.join(map(str, [population, field, a['n'], a['TT'], a['TF'], a['FT'], a['FF'],
                         f"{a['agreement']:.4f}" if a['agreement'] is not None else 'undefined',
                         f"{a['kappa']:.4f}" if a['kappa'] is not None else 'undefined']))+' |')
    lines += ['', '## Per-response causes: NEW X/VE', '',
              'Family suffix identifies p5-dev-00…03; s=shift, m=smuggle, b=benign. '
              'Required sets separated by OR; order within a set is irrelevant. '
              'Every VE row has author failure and all three artifact replays fail; every X row lists actual delivery. '
              'All 48 X/VE rating statuses are missing. Full reasons, artifact ledger identities, rating hashes and local events are in checks/dev-v10-diagnosis.json.', '',
              '| Family | Kind | Arm | Judge | Verdict | Type | Locations | Required verdict/type/sets | Author/replay or X completion | Rating | Cause |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    loc = lambda ids: ','.join(ids) or '∅'
    for d in sorted(report['decisions'], key=lambda d: (d['family'], KINDS.index(d['kind']), d['arm'], d['judge'])):
        if d['arm'] not in ('X', 'VE'): continue
        protocol = next(pr for pr in report['protocols'] if (pr['item_id'], pr['arm']) == (d['item_id'], d['arm']))
        a = d['answer']; req = d['required']
        state = 'author fail; replay 0/3' if d['arm'] == 'VE' else ('complete' if protocol['completed'] else 'failed')+f"; answers {protocol['isolated_answers']}+{protocol['adaptive_answers']}"
        lines.append('| '+' | '.join([d['family'][-2:], d['kind'], d['arm'], d['judge'], a['verdict'], a['issue_type'], loc(a['locations']),
                     req['verdict']+'/'+req['issue_type']+'/'+' OR '.join(loc(s) for s in req['locations']), state,
                     d['rating_status'], ', '.join(d['causes']) or '—'])+' |')
    lines += ['', '## VE artifact replay detail', '',
              '| Family | Kind | Stage | Replay failure |', '| --- | --- | --- | --- |']
    for pr in report['protocols']:
        if pr['arm'] != 'VE': continue
        for s in pr['stages']:
            if 'replay' in s:
                reason = s['replay'].get('error', s['replay'].get('delivery_error', str(s['replay'].get('obligations'))))
                lines.append('| '+' | '.join([pr['family'], pr['kind'], s['stage'], reason.replace('|', '\\|').replace('\n', ' ')])+' |')
    lines += ['', '## Recommendation and proposed adjudication rule — NOT applied', '',
              '**Do not start the scored run.** Complete blind ratings of all 48 new X/VE responses and resolve review disagreements. '
              'The dev contract is 48/48 valid per judge, but source-fidelity review remains unpassed; '
              'X delivery is defective and VE practical oracle coverage is 0/12 (UNKNOWN in 12/12). '
              'The prospective parser patch requires a reviewed/refrozen/timestamped executable before any authorized new inference. '
              'No new identities, rerun schedule, paid authorization, gate waiver or outcome relabeling is applied here. '
              'Do not repeatedly re-buy VE failures until they pass; any authoring/prompt intervention must be separately preregistered and evaluated as a new feasibility revision.', '',
              '**Proposed rule to preregister before scored data:** retain the two independent blind ratings. '
              'Send every disagreement on source_grounded or source_fidelity (across all responses, without selecting on deterministic eligibility) '
              'to a third independent adjudicator using only the same one-dossier packet, original answer, and field-specific rubric, '
              'with no arm/model, gold labels, aggregate outcomes, or other raters’ judgments. '
              'Require the adjudicator to identify the claimed failing inference and cite exact source records, '
              'distinguishing a sense conversion from an unsupported entity transfer and allowing logically equivalent wording. '
              'Require source_grounded to agree with the answer’s verdict/type/locations as well as records; '
              'source_fidelity separately asks whether its factual source claims are accurate. '
              'Use the independent third judgment to resolve each disputed field; unresolved/insufficient-evidence cases remain uncredited. '
              'Unanimous original judgments stand. Bind every resolution to the response hash and sorted digests of both ratings, '
              'with adjudicator identity, record evidence and rationale, and publish it. '
              'Protocol recognition remains a disclosure (retain both reports; flag if either recognizes), never an efficacy veto. '
              'The current source-fidelity gate needs an explicit reviewed amendment/implementation to consume such adjudications; '
              'this proposal does not silently enable it. Apply the rule uniformly to dev and scored once approved, preserving all originals. '
              'Exact verdict/type/location checks and benign vetoes remain unchanged. '
              'Report each-rater and unanimous-rating sensitivities descriptively, never choose the rater that produces favorable scores.', '']
    return '\n'.join(lines)


def main():
    paths = {'v9_trials': p.run_path('dev', 'trials.jsonl'),
             'v10_trials': p.dev_revision.run_path('dev', 'trials.jsonl'),
             'ratings': p.dev_revision.run_path('dev', 'ratings.jsonl'),
             'ledger': p.HERE/'runs/study/costs.jsonl',
             'local_events': p.dev_revision.run_path('dev', 'local-events.jsonl'),
             'materials': p.HERE/'materials/dev.jsonl.gz',
             'labels': p.HERE/'materials/anchored-labels.jsonl.gz'}
    hashes = {k: sha256(path.read_bytes()).hexdigest() for k, path in paths.items()}
    rows = p.dev_revision.trials('dev'); items = p.materials('dev'); labels = p.labels()
    ratings = p.read(paths['ratings'])
    report = audit(rows, items, labels, p.read(paths['ledger']), ratings)
    report['input_sha256'] = hashes
    analysis = p.analyze(rows, items, labels, ('pro', 'replication'), ratings)
    current = json.loads(p.dev_revision.run_path('dev', 'analysis.json').read_text())
    for c in report['cells']:
        assert current['judges'][c['judge']]['accuracy'][c['arm']][c['kind']] == c['credited']/c['assigned']
    assert analysis['judges'] == current['judges']
    # Offline refresh under the recorded execution freeze, not a new execution
    # attestation. Changed source still fails verify_freeze before any dispatch.
    from experiments.p5_preflight import refresh_dev_summary
    refresh_dev_summary(current, rows, ratings)
    assert all(sha256(path.read_bytes()).hexdigest() == hashes[k] for k, path in paths.items())
    p.write_json(p.HERE/'checks/dev-v10-diagnosis.json', report)
    (p.HERE/'DEV-V10-DIAGNOSIS.md').write_text(markdown(report))
    print(json.dumps({k: report[k] for k in ('assigned', 'missing', 'rating_coverage_by_arm', 'agreement', 'cells')}, indent=2))


if __name__ == '__main__':
    main()
