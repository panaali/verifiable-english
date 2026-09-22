"""Offline, ledger-bound audit of retained P5 dev decisions. No dispatch path.

Run: UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python -m experiments.p5_diagnosis
"""
from hashlib import sha256
import json

from experiments import p5 as p
from experiments.p5_analysis import endpoint, explanation_ratings
from experiments.p5_oracle import author_graph
from ve_experiments.paid import digest

KINDS=('shift','smuggle','benign')
CAUSES=('wrong_verdict','right_verdict_wrong_locations','right_verdict_wrong_issue_type',
        've_author_failure','harness_json_delivery','scorer_author_failure_veto')


def audit(rows, items, labels, ledger, ratings=()):
    """Keep behavioral errors, protocol defects and unreviewed ratings distinct.

    Causes overlap. The scorer-veto count is limited to decisions that meet
    every deterministic detection criterion; actual credit still needs ratings.
    """
    by_id={i['id']:i for i in items}; labels={l['id']:l for l in labels}
    selected={(r['item_id'],r['condition'],r['judge']):r for r in rows}
    reviews=explanation_ratings(rows,ratings)
    reserves={}; completions={}; failures={}
    for event in ledger:
        identity=event.get('identity','')
        if event['event']=='reserve': reserves[identity]=event
        if event['event']=='complete': completions[identity]=event
        if event['event']=='infrastructure_failure':
            failures.setdefault(identity,[]).append(event)
    details=[]; protocols=[]
    for item in items:
        label=labels[item['id']]
        for arm in p.ARMS:
            pro=selected.get((item['id'],arm,'pro'))
            wrapper_failure=False
            if arm in ('VE','X') and pro:
                stages=[]
                for history in pro['history']:
                    stage=history['stage']
                    if stage not in ('author','repair','critic','defender','followup'): continue
                    identity=f"study-v9/dev/{item['id']}/{arm}/pro/{stage}/0"
                    complete=completions[identity]
                    assert complete['text']==history['text'],identity
                    text=history['text']; record={'stage':stage,'identity':identity,
                        'response_sha256':digest(text),'finish_reason':complete['finish_reason']}
                    try: json.loads(text); strict=True
                    except ValueError: strict=False
                    try:
                        artifact=p.protocol_json(text)
                        record.update(strict_json=strict,unwrapped_json=True)
                        wrapper_failure |= not strict
                        if arm=='VE' and stage in ('author','repair','defender'):
                            record['environment_type']=type(artifact.get('environment')).__name__
                            try:
                                result=author_graph(artifact,item['payload'])
                                record['offline_checker']={k:result[k] for k in ('ok','findings','obligations')}
                            except Exception as exc:
                                record['offline_checker']={'ok':False,'error':f'{type(exc).__name__}: {exc}'}
                        if arm=='X' and stage=='critic':
                            record['question_count']=len(artifact['questions'])
                            record['question_item_types']=[type(q).__name__ for q in artifact['questions']]
                    except (ValueError,KeyError,TypeError) as exc:
                        record.update(strict_json=strict,unwrapped_json=False,error=str(exc))
                    stages.append(record)
                answer_calls=[identity for identity in reserves if identity.startswith(
                    f"study-v9/dev/{item['id']}/{arm}/pro/") and identity.split('/')[-2] in ('answer','followup_answer')]
                protocols.append({'item_id':item['id'],'family':label['family'],'kind':label['kind'],
                    'arm':arm,'stages':stages,'isolated_answer_requests':answer_calls,
                    'isolated_answers_in_judge_history':sum(h['stage'] in ('isolated_answer','isolated_followup_answer') for h in pro['history']),
                    'diagnostics_received_by_judge':[h for h in pro['history'] if h['stage'] in ('diagnostics','recertification')],
                    'tool_events':pro['tool_events'],'unresolved':pro['unresolved']})
            for judge in ('pro','replication'):
                row=selected.get((item['id'],arm,judge))
                kind=label['kind']; flawed=kind!='benign'
                stage='lone' if arm=='L' else 'judge'
                identity=f"study-v9/dev/{item['id']}/{arm}/{judge}/{stage}/0"
                required={'verdict':'reject' if flawed else 'approve',
                    'issue_type':kind if flawed else 'none',
                    'exact_location_sets':label['acceptable_locations'] if flawed else [[]],
                    'explanation':'two independent source-grounded ratings with bound adjudication on disagreement' if flawed else 'nonempty contract field',
                    'benign_requires_no_author_failure_or_unresolved':not flawed}
                entry={'item_id':item['id'],'family':label['family'],'arm':arm,'kind':kind,
                    'judge':judge,'identity':identity,'required':required,'observed':bool(row)}
                if not row:
                    assert identity not in completions, 'completed judgment missing from trials'
                    entry.update(causes=[],score=0,deterministic_eligible=0,
                        infrastructure_failures=[{'status':e.get('status'),'error':e.get('error')} for e in failures.get(identity,[])])
                else:
                    complete=completions[identity]; reserve=reserves[identity]
                    assert digest(complete['text'])==row['response_sha256'],identity
                    assert digest(reserve['messages'])==row['prompt_sha256'],identity
                    assert json.loads(complete['text'])==row['answer'],identity
                    content=reserve['messages'][-1]['content']
                    if row['history']:
                        assert json.loads(content.split('\nProtocol record:\n',1)[1])==row['history'],identity
                    answer=row['answer']; right=answer['verdict']==required['verdict']
                    localized=any(set(answer['locations'])==set(s) for s in required['exact_location_sets'])
                    issue=answer['issue_type']==required['issue_type']
                    key=digest({k:row[k] for k in ('item_id','condition','judge','answer')})
                    eligible=endpoint(label,row,True)['score']
                    flags=(not right,right and not localized,right and not issue,
                        bool(row['author_failure']),wrapper_failure,
                        flawed and bool(row['author_failure']) and bool(eligible))
                    entry.update(raw_text=complete['text'],answer=answer,
                        prompt_sha256=row['prompt_sha256'],response_sha256=row['response_sha256'],
                        ledger_and_history_verified=True,author_failure=row['author_failure'],
                        unresolved=row['unresolved'],protocol_error=row['protocol_error'],
                        causes=[c for c,flag in zip(CAUSES,flags) if flag],
                        source_grounded_approved=reviews.get(key,False),
                        rating_records=sum(r.get('response_sha256')==key for r in ratings),
                        score=endpoint(label,row,reviews.get(key,False))['score'],
                        deterministic_eligible=eligible)
                details.append(entry)
    cells=[]
    for judge in ('pro','replication'):
        for arm in p.ARMS:
            for kind in KINDS:
                cell=[d for d in details if (d['judge'],d['arm'],d['kind'])==(judge,arm,kind)]
                cells.append({'judge':judge,'arm':arm,'kind':kind,'assigned':len(cell),
                    'observed':sum(d['observed'] for d in cell),'credited':sum(d['score'] for d in cell),
                    'deterministic_eligible':sum(d['deterministic_eligible'] for d in cell),
                    'eligible_without_rating_records':sum(d['deterministic_eligible'] and d.get('rating_records')==0 for d in cell) if kind!='benign' else 0,
                    'causes':{c:sum(c in d['causes'] for d in cell) for c in CAUSES}})
    return {'assigned':len(details),'observed':len(rows),'missing':len(details)-len(rows),
        'cause_counts_overlap':{c:{j:sum(c in d['causes'] and d['judge']==j for d in details)
            for j in ('pro','replication')} for c in CAUSES},
        'cells':cells,'decisions':details,'protocols':protocols,
        'model_calls':0,'rating_records':len(ratings)}


def markdown(report):
    lines=['# P5 dev diagnosis — 2026-09-22','',
        'Scenario (a), four families, 94/96 observed. This is an offline audit of the retained v9 run; no model calls, ratings, verdicts, or transcripts were generated or replaced.',
        '', '## Failure causes (overlapping observed judgments)', '',
        '| Cause | Gemini | Qwen | Total |','| --- | ---: | ---: | ---: |']
    names=['(i) Wrong verdict (including unknown)','(ii) Right verdict, wrong/missing exact localization',
        '(iii) Right verdict, wrong issue type','(iv) VE authoring failed',
        '(v) Nonjudge JSON wrapper delivery defect','(vi) Author-failure scorer veto on otherwise eligible flaw decisions']
    for cause,name in zip(CAUSES,names):
        counts=report['cause_counts_overlap'][cause]
        lines.append(f"| {name} | {counts['pro']} | {counts['replication']} | {sum(counts.values())} |")
    pending=sum(c['eligible_without_rating_records'] for c in report['cells'])
    lines += ['',f'Counts overlap: judge mistakes can coexist with protocol/author failures. The old veto applies to all 15 observed flawed VE decisions; it affects four deterministic candidates, but changes **zero credited scores** because all {pending} deterministic flaw candidates lack the preregistered independent explanation ratings. Missing ratings are an unfinished review requirement, not incorrect verdicts or a reason to waive the endpoint.',
        '', 'The two missing Qwen decisions are VE/shift (`i0e03b71…`) and X/smuggle (`ib301f2a…`), each with four ledger-recorded HTTP 429 failures and no accepted completion. These provider failures are separate from the harness defect above.',
        '', '## Corrected offline assigned-denominator scores', '',
        'Each entry is credited/assigned; brackets show deterministic candidates before explanation review for flaws. Candidates are **not** accuracy or credited detections. Benign credit retains author-failure and unresolved-protocol vetoes.', '',
        '| Judge | Arm | Shift | Smuggle | Benign |','| --- | --- | --- | --- | --- |']
    for judge in ('pro','replication'):
        for arm in p.ARMS:
            values=[]
            for kind in KINDS:
                c=next(c for c in report['cells'] if (c['judge'],c['arm'],c['kind'])==(judge,arm,kind))
                values.append(f"{c['credited']}/{c['assigned']}"+(f" [{c['deterministic_eligible']}]" if kind!='benign' else ''))
            lines.append('| '+('Gemini' if judge=='pro' else 'Qwen')+' | '+arm+' | '+' | '.join(values)+' |')
    lines += ['', '## Per-arm × kind cause counts', '',
        '| Judge | Arm | Kind | Observed | i | ii | iii | iv | v | vi |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for c in report['cells']:
        lines.append('| '+' | '.join(map(str,[c['judge'],c['arm'],c['kind'],c['observed'],*[c['causes'][k] for k in CAUSES]]))+' |')
    lines += ['', '## What reached each protocol', '',
        '**X:** 12/12 author outputs and 12/12 critic outputs were complete fenced JSON (STOP). The old parser failed on the author fence before reading the commitment or dispatching a single isolated answer. Ten critics contain 16 questions as single-field objects; two contain empty lists. There were zero initial-answer, follow-up, or follow-up-answer calls. All 23 observed judges received the author, critic, and failure record, with no isolated answers. The repair unwraps only a complete enclosing fence and accepts a question string or an exact single `question` field; token limits and copy isolation remain unchanged. Existing histories are not repaired retroactively.',
        '', '**VE:** 12/12 author, 12/12 repair, and 12/12 defender artifacts decode after presentation-fence removal, but all 36 have a string `environment`, not a VE environment object. Offline checker replay rejects all 36 with `VEError: Expected a JSON object`; no checkable graph, edge certificates, or substantive entailment findings exist. Strict online JSON parsing let four repairs and two defenders reach the local checker (six calls across five protocols), all UNKNOWN with that same error. The other eight repair diagnostics report JSON parsing failure. All 23 observed VE judges received their raw artifacts and the recorded failure diagnostics; only two protocols have recertification records. Wrapping repair exposes the underlying authoring error; it does not repair the environment or ordinary-prose claim sources.',
        '', '**Scorer:** PREREG §7 permits source-grounded detection from common prose after tool/author failure. The old shared `failed` flag incorrectly vetoed that detection and treated a valid rejection as a failed final decision in safety counts. The amendment separates final-decision failure from author failure. Benign completion, exact localization, issue type, verdict, ratings, and assignment denominators are unchanged. No independent ratings are present; the reported all-zero flaw scores are therefore unreviewed lower bounds, not evidence that every judge missed every flaw.',
        '', 'All 94 raw judge responses and prompt hashes match the retained ledger. For each nonempty history, the exact serialized protocol record in the ledger request matches the trial history. No accepted final response was dropped. Full raw verdicts, explanations, required sets, per-stage checker replay, and infrastructure evidence are in [checks/dev-diagnosis.json](checks/dev-diagnosis.json).',
        '', '## Gate decision', '',
        '**FAIL / incomplete.** Gemini contract compliance is 48/48 and Qwen is 46/46 on observed judgments (both 100%), but assigned coverage is only 94/96. Independent explanation/source-fidelity review is absent. X cross-examination was not delivered, VE authoring produced no checkable graphs, and source changes invalidate the old executable freeze. No scored execution is authorized. The amendment does not waive budgets or any gate; this session spends $0.',
        '', '## Individual raw decisions and required exact location sets', '',
        'Location order is irrelevant, but membership must equal one complete acceptable set: a correct ID plus an extra record ID fails. Benign requires an empty set. `OR` separates alternative acceptable sets.', '',
        '| Family | Judge | Arm | Kind | Raw verdict | Raw issue | Raw locations | Required verdict / issue / locations |',
        '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for d in report['decisions']:
        a=d.get('answer',{}); req=d['required']
        loc=lambda ids: ','.join(ids) or '∅'
        lines.append('| '+' | '.join([d['family'],d['judge'],d['arm'],d['kind'],a.get('verdict','MISSING'),
            a.get('issue_type','—'),loc(a.get('locations',[])),req['verdict']+' / '+req['issue_type']+' / '+
            ' OR '.join(loc(s) for s in req['exact_location_sets'])])+' |')
    return '\n'.join(lines)+'\n'


def main():
    paths={'trials':p.run_path('dev','trials.jsonl'),'ledger':p.HERE/'runs/study/costs.jsonl',
        'local_events':p.run_path('dev','local-events.jsonl'),'labels':p.HERE/'materials/anchored-labels.jsonl.gz',
        'materials':p.HERE/'materials/dev.jsonl.gz'}
    rows=p.read(paths['trials']); items=p.materials('dev'); labels=p.labels()
    ratings=p.read(p.run_path('dev','ratings.jsonl'))
    report=audit(rows,items,labels,p.read(paths['ledger']),ratings)
    report['input_sha256']={k:sha256(v.read_bytes()).hexdigest() for k,v in paths.items()}
    corrected=p.analyze(rows,items,labels,('pro','replication'),ratings,allow_missing=True)
    corrected.update(passed=False,source_fidelity_review_required=True,
        **p.contract_report(rows,len(items)*4,('pro','replication')),
        correction='2026-09-22 author-failure veto removed from flaw detection only; no ratings fabricated',
        deterministic_candidates_not_credited={j:{a:{k:next(c['deterministic_eligible'] for c in report['cells']
            if (c['judge'],c['arm'],c['kind'])==(j,a,k)) for k in KINDS} for a in p.ARMS} for j in ('pro','replication')})
    for cell in report['cells']:
        assert corrected['judges'][cell['judge']]['accuracy'][cell['arm']][cell['kind']]==cell['credited']/cell['assigned']
    p.write_json(p.HERE/'checks/dev-diagnosis.json',report)
    p.write_json(p.run_path('dev','analysis-corrected.json'),corrected)
    (p.HERE/'DEV-DIAGNOSIS.md').write_text(markdown(report))
    print(json.dumps({k:report[k] for k in ('assigned','observed','missing','cause_counts_overlap','cells','model_calls')},indent=2))


if __name__=='__main__':
    main()
