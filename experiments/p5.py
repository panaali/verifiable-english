"""P5 staged duel. No generation is reachable without an explicit positive cap.

Uses P1's native providers, routing, durable billing reservations, retryable
infrastructure handling, revision checks and per-model validation halts.
"""
from __future__ import annotations
from dataclasses import asdict, replace
from decimal import Decimal
from pathlib import Path
import argparse
from collections import defaultdict
import json
import random
import sys
import time

from experiments.p5_materials import HERE, SEED, read, archive, write_json, generate
from experiments.p5_isolation import single_context
from experiments.p5_analysis import ARMS, parse, analyze, known_answer, contract_report
from experiments.p5_paraphrase import SANITISER, validate_reply
from experiments import p5_review as review
from experiments.p1 import append, sha, infrastructure_state
from experiments.p1_preflight import CommandCounter
from ve_experiments.paid import (MODELS, RATES, PaidRequest, PaidClient, Ledger,
    OpenRouterBackend, PreflightError, BudgetExceeded, InfrastructureError, digest, packed, cost)
from experiments.p5_tokens import P5VertexBackend as VertexBackend

ROOT=HERE.parents[1]
CAP=Decimal('40')
MATCHED_CAP=Decimal('.16')
STUDY_REVISION='study-v9'
# Amendment P5-1 lowers author/repair to 1024 total billed tokens. The original
# 2048 ceilings remain in the immutable design inventory for transparent audit.
STAGES={'author':(3000,1024),'critic':(5500,1024),'defender':(7000,1024),
        'judge':(10000,1024),'answer':(3200,512),'followup':(7500,256),
        'followup_answer':(3200,512),'repair':(6000,1024),'lone':(7500,1024),
        'paraphrase':(4096,1024)}
SCENARIOS={'primary':('pro',),'dual_judge':('pro','replication')}
SYSTEM=('Audit the ORIGINAL justification from the dossier. Glossary senses are possibilities; records anchor uses. '
        'Approve only a supported original root. Reject unsupported justification without asserting the root false. '
        'Unknown is allowed. Cite at most two node IDs. A conditional proof or DIFFERENT does not establish source fidelity.')
VERDICT_SCHEMA={'type':'object','properties':{
    'verdict':{'type':'string','enum':['approve','reject','unknown']},
    'issue_type':{'type':'string','enum':['shift','smuggle','none','unknown']},
    'locations':{'type':'array','items':{'type':'string'},'maxItems':2},
    'explanation':{'type':'string'}},'required':['verdict','issue_type','locations','explanation'],
    'additionalProperties':False}
FORMAL=('Return JSON with environment (VE core@0 environment), claims [{id,source: strict VE}], '
        'edges [{id,premises,conclusion}], root, alignment {node_id:[record_ids]}, queries:[], splits:[]. '
        'Include every shared node and all six declared premises. Author your own formalisation; '
        'no undeclared bridge may become a free premise. Local certificate search is charged. '
        'For a split, return a complete new environment and all affected claims, and splits '
        '[{old_symbol,new_symbols,affected_ids,divergent_uses}]. All old certificates are voided. '
        'Queries may use compare or validate_attack with tool, claim_id, environment_id, committed_source, '
        'record_id, rival_source_text (exact record), rival_ve. At most four queries and four splits total.')
ROLES={
 'X_author':'Defend the proposed argument. Return JSON {"commitment":"fixed meanings, at most 512 tokens","argument":"defense"}.',
 'S_author':'Seek errors. Produce a claim/premise/use table from the common packet.',
 'VE_author':'Defend the proposed argument, faithfully formalising uses and premises. '+FORMAL,
 'X_critic':'Seek source-grounded flaws across branches. Return JSON {"questions":[up to three self-contained questions, each <=256 tokens]}.',
 'S_critic':'Independently audit the authored table against source records, seeking errors.',
 'VE_critic':'Challenge source alignment or an omitted leaf; propose splits if divergent uses are cited. Return JSON {"audit":"...","queries":[],"splits":[]}. '+FORMAL,
 'answer':'Answer only this question using the unchanged packet and frozen commitment. You are an isolated proposer copy.',
 'followup':'Inspect the initial questions and answers for inconsistency. Return JSON {"question":"one self-contained adaptive question <=256 tokens, or empty"}. Do not transmit other copies’ full answers.',
 'S_defender':'Independently revise the audit against the same records; seek errors.',
 'VE_defender':'Answer the critic, re-author affected uses and re-certify in a complete artifact. '+FORMAL,
 'repair':'Repair only the diagnosed syntax/coverage failures. One repair is allowed; retain the original root. '+FORMAL,
 'judge':('Return exactly a JSON verdict conforming to the response schema. Assess original justification, cite source evidence. '
          'Locations are zero to two distinct paragraph or declared-premise node IDs (nNN); '
          'rule/record IDs (rNN) belong in explanation only. Use a nonempty explanation. '
          'Return [] for an approval or when no location is identified. '
          'An unknown verdict is permitted and is not a successful detection or completion.'),
 'paraphrase':'Perform a CONSTRAINED structural rewrite, not a free paraphrase. Keep EVERY atomic claim phrase verbatim: copy each complete "unitN is <predicate>" string exactly, including unit names, predicate words, case and every repeated occurrence. Do not replace predicates with synonyms or change atoms to passive voice. State premises by content. Freely restructure the surrounding prose within each step: reorder premise sentences, vary connectives, merge or split sentences, use active or passive discourse framing. Examples: "From the fact that unit1 is ready and unit2 is clear, it follows that unit3 is active."; "These facts are taken together: unit1 is ready. Also, unit2 is clear. Therefore, unit3 is active."; "unit3 is active is inferred from the fact that unit1 is ready and unit2 is clear." These are syntax examples only; never insert their atoms into the supplied argument. Aim for normalized character Levenshtein distance >= 0.20 after every atomic phrase is replaced with the single character # in both source and rewrite; only surrounding restructuring earns distance. Keep every step in the same given topological order, one paragraph per step. Preserve immediately-preceding references, inference direction and all conditional alternatives without adding or repairing assumptions. Make inference direction explicit with it follows that/thus/therefore/so/hence/we conclude that, or conclusion because/on the grounds that/is inferred from the fact that. No negation, hedges, definitions or commentary may be added. Keep conditional alternatives at their supplied step, paired in the same way and explicitly conditional, never asserted as facts. You may move that sentence within its step or reframe it as "If <checks>, then <outcomes> would follow, respectively." Keep all atomic phrases in both lists verbatim. No parenthetical glosses or sense labels in the prose. Do not disambiguate ambiguous terms. Return JSON {"texts":{"node_id":"rewritten step"}} with every existing node ID as a key only. No step-id markers, node IDs or rule IDs in prose. No additional fields.' }


def materials(split=None):
    return [i for s in ('dev','scored') if split is None or s==split for i in read(HERE/f'materials/{s}.jsonl.gz')]


def packet(item, arm=None):
    p=item['payload']
    # Explicit allowlist; no label, reference environment, family or variant.
    single_context([item])
    lines = ['Dossier '+p['id'], 'Declared premises:']
    lines += [f"{n['id']}: {n['text']}" for n in p['premises']]
    lines += ['Authoritative records:'] + [f"{r['id']}: {r['text']}" for r in p['records']]
    lines += ['Paragraph IDs in order: ' + ', '.join(n['id'] for n in p['nodes']), 'Proposed argument:', p['argument'], f"Original root {p['root']}."]
    if arm == 'VE':
        lines += ['VE node block:'] + [f"{n['id']} ({','.join(n['parents'])}): {n['text']}" for n in p['nodes']]
    return '\n'.join(lines)


def stage_list(arm):
    if arm=='L': return ['lone']
    return ['author','critic',*(['answer']*3+['followup','followup_answer'] if arm=='X' else ['defender']),
            *(['repair'] if arm=='VE' else []),'judge']


def stage_limits(arm, stage, model='pro'):
    """V9 fixes observed thinking truncation; budget ceilings remain enforced."""
    inp,out=STAGES[stage]
    if model=='pro' and (arm=='VE' or stage in ('judge','lone') or (arm=='S' and stage=='author')):
        out=4096
    # Preserve the old packet allowance plus the enlarged prior-output reserve.
    extra_author=3072 if arm in ('S','VE') else 0
    extra={'critic':extra_author,'repair':extra_author,
        'defender':extra_author+(6144 if arm=='VE' else 0),
        'judge':extra_author+(9216 if arm=='VE' else 0)}.get(stage,0)
    return inp+extra,out


def run_path(split, name):
    return HERE/f'runs/{split}-v9'/name


def ceilings(scenario, scored_families=None):
    from experiments.p5_budget import ceilings as amended_ceilings
    return amended_ceilings(scenario, scored_families)


def scheduled_materials(split=None):
    from experiments.p5_budget import selected_materials
    return selected_materials(split)


def request(item,arm,stage,history=None,*,judge='pro',turn=0,commitment=None,question=None,examples=()):
    single_context([item, *examples])
    if history and any(r.get('item_id') != item['id'] for r in history):
        raise PreflightError('history must bind this dossier; cross-packet histories are forbidden')
    model=judge if stage in ('judge','lone') else 'replication' if stage=='paraphrase' else 'pro'
    role='judge' if stage=='lone' else stage
    if stage in ('answer','followup_answer'):
        # Exactly three isolated fields: never receive history or authored defense.
        if history:
            raise PreflightError('isolated answers must not receive a transcript')
        content=packet(item,arm)+'\nFrozen commitment:\n'+(commitment or '')+'\nOne question:\n'+(question or '')
        instruction=ROLES['answer']
    elif stage=='paraphrase':
        content=packet(item,arm)+'\nSeparate glossary:\n'+packed(item['payload']['glossary'])
        instruction=ROLES['paraphrase']
    else:
        content=packet(item,arm)
        if history: content+='\nProtocol record:\n'+packed(history)
        instruction=ROLES.get(arm+'_'+role,ROLES.get(role,''))
    schema=VERDICT_SCHEMA if role=='judge' else None
    # The prompt's schema copy does not account for
    # the separate provider response_schema overhead; p5_tokens handles that.
    system=(instruction if stage=='paraphrase' else SYSTEM+' '+instruction)+((' Response schema: '+packed(schema)) if schema else '')
    inp,out=stage_limits(arm,stage,model)
    prefix = "rewrite-v7/" if stage == "paraphrase" else STUDY_REVISION+'/'
    return PaidRequest(prefix+f"{item['split']}/{item['id']}/{arm}/{model}/{stage}/{turn}",model,
        [{'role':'system','content':system},{'role':'user','content':content}],inp,out,
        response_schema=schema,metadata={'item_id':item['id'],'arm':arm,'role':stage,'turn':turn,
            'packet_sha256':digest(item['payload']),'seed':SEED,'sample':0,
            **({'require_response_schema':True} if schema else {})})


def native_counter(*, cached_only=False):
    return CommandCounter(ROOT/'experiments/P1-deference/native_counter.py', cached_only=cached_only)


def exact_text_tokens(client,text,limit):
    req=PaidRequest('count-only','pro',[{'role':'user','content':text}],100000,1)
    # This measures visible text, not a dispatched prompt/config billing bound.
    counter=client.backend.native_count if isinstance(client.backend,VertexBackend) else client.backend.count
    count=counter(req)
    if count>limit:
        raise ValueError(f'visible text {count} exceeds {limit}; no truncation')


def bounded_record(record):
    # Authentic bounded summaries; full query, certificates and witnesses remain
    # in the local ledger. No gold label or source-faithfulness assertion.
    summary={k:record[k] for k in ('ok','status','error','obligations','warning','operation','query_sha256','local_id') if k in record}
    summary['record_sha256']=digest(record)
    if 'findings' in record:
        summary['checker_build']=record['findings'].get('checker_build')
        summary['graph_id']=record['findings'].get('graph_id')
    if 'result' in record:
        result=record['result']
        summary['result']={k:result[k] for k in ('status','accepted','relation','classification','reason','warnings') if k in result}
        summary['result_sha256']=digest(result)
    return summary


def execute(item,arm,client,judge_clients,*,local_events=None,local_cache=(),event_sink=None):
    from experiments.p5_oracle import bounded
    history=[]; local_events=local_events if local_events is not None else []
    wall_remaining=60.; query_count=0; split_count=0; obligations=[]; author_failure=False; oracle_unknown=False
    def call(stage,**kw):
        req=request(item,arm,stage,**kw)
        reply=client.call(req)
        return reply.text
    def emit(event):
        event={'local_id':str(len(local_events)),**event}
        prior=next((e for e in local_cache if e.get('local_id')==event['local_id']),None)
        if prior and digest(prior)!=digest(event):
            raise PreflightError('resumed local event changed')
        local_events.append(event)
        if event_sink and not prior: event_sink(event)
    def local(operation,data,limit):
        nonlocal wall_remaining,oracle_unknown
        local_id=str(len(local_events))
        prior=next((e for e in local_cache if e.get('local_id')==local_id),None)
        if prior:
            if prior.get('query_sha256')!=digest(data) or prior.get('operation')!=operation:
                raise PreflightError('resumed local operation changed')
            result=prior
            wall_remaining-=result.get('elapsed_s',0)
        elif wall_remaining<=0:
            result={'ok':False,'status':'UNKNOWN','error':'60-core-second envelope exhausted','elapsed_s':0}
        else:
            result=bounded(operation,data,min(limit,wall_remaining))
            wall_remaining-=result['elapsed_s']  # conservative serial wall budget bounds CPU
        oracle_unknown |= result.get('status')=='UNKNOWN'
        event={'operation':operation,**result,'local_id':local_id,'query_sha256':digest(data)}
        local_events.append(event) if prior else emit(event)
        return event
    def queries(artifact,committed):
        nonlocal query_count,split_count,obligations
        for split in artifact.get('splits',[]):
            split_count+=1
            if split_count>4 or not split.get('divergent_uses') or not split.get('affected_ids'):
                obligations.append('invalid or excess split'); continue
            obligations.extend(split['affected_ids'])
            emit({'operation':'split','void_all_certificates':True,**split})
        for q in artifact.get('queries',[]):
            if query_count>=4:
                obligations.append('oracle query limit exceeded'); break
            query_count+=1
            result=local('query',{'query':q,'committed':committed,'packet':item['payload']},5)
            history.append({'item_id':item['id'],'stage':'oracle','record':bounded_record(result)})
    try:
        if arm!='L':
            author=call('author'); history.append({'item_id':item['id'],'stage':'author','text':author})
            if arm=='VE':
                try:
                    artifact=json.loads(author)
                    diagnostic=local('author',{'artifact':artifact,'packet':item['payload']},wall_remaining)
                except (ValueError,KeyError,TypeError) as exc:
                    artifact={}; diagnostic={'ok':False,'error':str(exc)}
                if not diagnostic.get('ok'):
                    repair=call('repair',history=[history[0],{'item_id':item['id'],'stage':'diagnostics','record':bounded_record(diagnostic)}])
                    history.append({'item_id':item['id'],'stage':'repair','text':repair})
                    try:
                        artifact=json.loads(repair)
                        diagnostic=local('author',{'artifact':artifact,'packet':item['payload']},wall_remaining)
                    except (ValueError,KeyError,TypeError) as exc:
                        artifact={};diagnostic={'ok':False,'error':str(exc)}
                author_failure=not diagnostic.get('ok')
                history.append({'item_id':item['id'],'stage':'diagnostics','record':bounded_record(diagnostic)})
                queries(artifact,artifact)
                # Critic gets repaired artifact, never superseded author output.
                critic_history=history[1:] if any(h['stage']=='repair' for h in history) else history[:]
            else:
                critic_history=history[:]
            critic=call('critic',history=critic_history); history.append({'item_id':item['id'],'stage':'critic','text':critic})
            if arm=='X':
                commitment=json.loads(author)['commitment']; exact_text_tokens(client,commitment,512)
                questions=json.loads(critic)['questions']
                if not isinstance(questions,list) or len(questions)>3:
                    raise ValueError('at most three initial questions')
                for n,q in enumerate(questions):
                    exact_text_tokens(client,q,256)
                    answer=call('answer',turn=n,commitment=commitment,question=q)
                    history.append({'item_id':item['id'],'stage':'isolated_answer','question':q,'text':answer})
                followup=call('followup',history=history); history.append({'item_id':item['id'],'stage':'followup','text':followup})
                q=json.loads(followup)['question']
                if q:
                    exact_text_tokens(client,q,256)
                    answer=call('followup_answer',commitment=commitment,question=q)
                    history.append({'item_id':item['id'],'stage':'isolated_followup_answer','question':q,'text':answer})
            else:
                if arm=='VE':
                    try: queries(json.loads(critic),artifact)
                    except (ValueError,KeyError,TypeError) as exc: obligations.append(str(exc))
                defender=call('defender',history=history);history.append({'item_id':item['id'],'stage':'defender','text':defender})
                if arm=='VE':
                    try:
                        revised=json.loads(defender)
                        changed=revised.get('environment')!=artifact.get('environment')
                        if changed:
                            emit({'operation':'environment_change','void_all_certificates':True})
                        diagnostic=local('author',{'artifact':revised,'packet':item['payload']},wall_remaining)
                        queries(revised,revised)
                        split_obligations=[e for e in local_events if e.get('operation')=='split']
                        resolved=all(e.get('old_symbol') not in revised.get('environment',{}).get('vocabulary',{}).get('predicates',{}) and
                            set(e.get('affected_ids',[]))<=set(revised.get('alignment',{})) for e in split_obligations)
                        if diagnostic.get('ok') and not author_failure and resolved and split_count<=4:
                            obligations=[o for o in obligations if o not in {x for e in split_obligations for x in e.get('affected_ids',[])}]
                        else: obligations.append('unrepaired formalisation or unresolved original root')
                        history.append({'item_id':item['id'],'stage':'recertification','record':bounded_record(diagnostic)})
                    except (ValueError,KeyError,TypeError) as exc: obligations.append(str(exc))
        error=None
    except (ValueError,KeyError,TypeError) as exc:
        error=f'protocol failure: {exc}'; obligations.append(error)
        history.append({'item_id':item['id'],'stage':'failure','error':error})
        author_failure |= arm=='VE'
    # Even a failed formalisation stays assigned; common-prose detection remains
    # possible but benign completion cannot be rescued by hidden reference data.
    rows=[]
    for judge,jclient in judge_clients.items():
        req=request(item,arm,'lone' if arm=='L' else 'judge',history,judge=judge)
        try:
            reply=jclient.call(req)
        except InfrastructureError:
            if judge=='pro': raise
            continue  # P1 ledger retains the per-judge halt; Gemini can continue.
        try:
            if getattr(reply,'finish_reason','').upper() in ('MAX_TOKENS','LENGTH'):
                raise ValueError('truncated judgment: '+reply.finish_reason)
            answer=parse(reply.text,[n['id'] for n in item['payload']['nodes']+item['payload']['premises']]);parse_error=None
        except (ValueError,TypeError) as exc:
            answer={};parse_error=str(exc)
        rows.append({'item_id':item['id'],'group':item['group'],'split':item['split'],
            'condition':arm,'judge':judge,'sample':0,'seed':SEED,'packet_sha256':digest(item['payload']),
            'prompt_sha256':digest(req.messages),'response_sha256':digest(reply.text),'answer':answer,
            'ok':parse_error is None,'error':parse_error,'protocol_error':error,
            'localization_invalid_ids':sorted(set(answer.get('locations',[]))-
                {n['id'] for n in item['payload']['nodes']+item['payload']['premises']}),
            'finish_reason':getattr(reply,'finish_reason',''),
            'author_failure':author_failure,'unresolved':obligations,'oracle_unknown':oracle_unknown,
            'local_wall_s':60-wall_remaining,'local_cpu_s':sum(e.get('cpu_s',0) for e in local_events),
            'tool_events':local_events,'history':history})
    return rows


def check_labels():
    return labels(len(read(HERE/'materials/anchored-labels.jsonl.gz'))==84)


def labels(anchored=True):
    rows=read(HERE/'labels.jsonl.gz')
    if anchored:
        anchor={r['id']:r for r in read(HERE/'materials/anchored-labels.jsonl.gz')}
        if set(anchor)!={r['id'] for r in rows}:
            raise PreflightError('all 84 anchored labels required')
        rows=[{**r,'acceptable_locations':anchor[r['id']]['acceptable_locations']} for r in rows]
    return rows


def freeze(scenario):
    write_json(HERE/'prompts.json',{'system':SYSTEM,'roles':ROLES,'schema':VERDICT_SCHEMA,'stages':STAGES,
        'effective_stage_caps':{a:{m:{s:stage_limits(a,s,m) for s in stage_list(a)} for m in ('pro','replication')} for a in ARMS}})
    paths=[ROOT/'ve_experiments/paid.py',ROOT/'ve_experiments/json_response.py',*ROOT.glob('experiments/p5*.py'),
           ROOT/'experiments/p1.py',ROOT/'experiments/p1_preflight.py',ROOT/'experiments/prereg_inventory.py',
           ROOT/'experiments/trial_analysis.py',*ROOT.glob('tests/test_p5*.py'),
           ROOT/'tests/fixtures/p5_deepinfra_smoke.json',ROOT/'tests/fixtures/p5_vertex_smoke.json',ROOT/'pyproject.toml',ROOT/'uv.lock',
           HERE/'PREREG.md',HERE/'SCHEDULE-AMENDMENT.md',ROOT/'experiments/PREREG-DESIGN.md',HERE/'inventory.json',HERE/'AMENDMENTS.md',HERE/'REVISION6.md',HERE/'REVISION7.md',HERE/'REVISION8.md',HERE/'RESULTS.md',
           HERE/'materials/prose-policy.json', HERE/'checks/gemini-rendered-submission.json', HERE/'checks/gemini-rendered-status.json', HERE/'runs/revision-v8/gemini-review-costs.jsonl',
           HERE/'prompts.json',HERE/'CONSTRUCTION-V3.md',HERE/'CONSTRUCTION-V4.md',HERE/'CONSTRUCTION-V5.md',HERE/'REVIEW-CHECKLIST.md',HERE/'PARAPHRASE-REVIEW.md',HERE/'run_p5.py',*HERE.glob('materials/*.gz'),HERE/'labels.jsonl.gz',
           ROOT/'experiments/P1-deference/native_counter.py',*ROOT.glob('experiments/P1-deference/tokenizers/*.json'),
           *ROOT.glob('ve/*.py'), ROOT/'lean/.lake/build/bin/ve_conformance']
    paths += list((HERE/'runs').glob('revision-*/paraphrase-costs.jsonl'))
    paths += [HERE/'checks/v7-final-acceptance.json', HERE/'checks/gemini-rendered-adjudication.json']
    paths += [HERE/'DEV-CONTRACT-AUDIT.md',HERE/'checks/dev-contract-audit.json',
        HERE/'checks/dev-superseded-v8.json',HERE/'checks/budget-scenarios.json',HERE/'runs/dev/trials.jsonl',HERE/'runs/dev/analysis.json']
    paths += [HERE/name for name in ('MATERIALS-MANIFEST.json','MATERIALS-HASHES.txt',
        'MATERIALS-HASHES.txt.ots','checks/round5-review-submission.json',
        'checks/round5-review-verification.txt','checks/round5-review-import.json',
        'checks/round6-review-submission.json','checks/round6-review-verification.txt','checks/round6-review-import.json')]
    calibration_path=HERE/'checks/gemini-calibration.json'
    calibration=json.loads(calibration_path.read_text()) if calibration_path.exists() else {'configs':{}}
    if not calibration_path.exists():write_json(calibration_path,calibration)
    paths.append(calibration_path)
    hashes={str(p.relative_to(ROOT)):sha(p) for p in paths if p.exists()}
    result={'status':'BLOCKED_NOT_SCORED_READY','scenario':scenario,'hashes':hashes,'models':MODELS,
        'rates':RATES,'sampling':{'temperature':0,'seed':SEED,'samples':1},'ceilings':ceilings(scenario),
        'gemini_calibration':calibration,
        'manifest_sha256':digest({'hashes':hashes,'scenario':scenario,'models':MODELS,'rates':RATES}),
        'commands':['generate','review --export PATH','review --submit PATH','inventory --count-tokens',
                    'known-answer','calibrate-gemini','freeze','preflight','preflight-openrouter --cap-usd N',
                    'probe --cap-usd N','dev --cap-usd N','scored --cap-usd N',
                    'resume --split scored --cap-usd N','reconcile','analyze --split scored']}
    write_json(HERE/'freeze.json',result)
    return result


def verify_freeze(*, paraphrase_progress=False, check_budget=True):
    f=json.loads((HERE/'freeze.json').read_text())
    # Only this pre-scoring construction stage may replace its own outputs.
    # Dossiers, code and every other frozen input must still match exactly.
    progress={HERE/f'materials/{name}.jsonl.gz' for name in ('paraphrases','dev','scored')} if paraphrase_progress else set()
    for path,expected in f['hashes'].items():
        if ROOT/path in progress:
            continue
        if sha(ROOT/path)!=expected:
            raise PreflightError('freeze changed: '+path+'; amendment/refreeze required')
    calibration_path=HERE/'checks/gemini-calibration.json'
    if 'gemini_calibration' in f and (not calibration_path.exists() or
            f['gemini_calibration']!=json.loads(calibration_path.read_text())):
        raise PreflightError('Gemini calibration changed; refreeze required')
    if f['ceilings'] != ceilings(f['scenario']):
        raise PreflightError('schedule accounting changed; refreeze required')
    if check_budget and not f['ceilings']['within_cap']:
        raise BudgetExceeded('scenario exceeds $40')
    if check_budget and not f['ceilings'].get('within_matched_ceiling',True):
        raise BudgetExceeded(f'worst-case item-arm schedule exceeds matched {MATCHED_CAP} ceiling')
    return f


def gate_receipt(name,result,stamp):
    result={**result,'freeze_sha256':stamp}
    write_json(HERE/f'checks/{name}.json',result)
    return result


def require_gates(scored=False):
    f=verify_freeze(); blockers=[]
    for name in ('tracked-blinding','surface-soundness','review','prose-provenance','construction','known-answer','gemini-calibration-coverage','tokenizer','budget','lean-replay','packet-safety','leakage','role-boundaries','external-timestamp','provider-preflight',*(['dev'] if scored else [])):
        path=HERE/f'checks/{name}.json'
        r=json.loads(path.read_text()) if path.exists() else {}
        if r.get('passed') is not True or r.get('freeze_sha256')!=f['manifest_sha256']:
            blockers.append(name)
    if blockers:
        raise PreflightError('unresolved gates: '+', '.join(blockers))
    return f


def revision_paraphrase_costs(base=HERE):
    """Physical historical rewrite charges, excluding study planning envelopes."""
    shared = defaultdict(Decimal)
    holds = Decimal(0)
    for path in sorted((base/'runs').glob('revision-*/paraphrase-costs.jsonl')):
        rows = read(path)
        reservations = {r['identity']:r for r in rows if r['event']=='reserve'}
        for row in rows:
            if row['event'] not in ('complete','interrupted','infrastructure_failure','panel_halt'):
                continue
            meta = reservations.get(row.get('identity'),{}).get('metadata',{})
            value = Decimal(row.get('cost_usd',row.get('infrastructure_hold_usd','0')))
            if meta.get('role')=='paraphrase' and meta.get('item_id'):
                shared[meta['item_id']] += value
                if row['event']!='complete':
                    holds += value
    return shared, holds


class P5Ledger(Ledger):
    """Additional per-item matched ceiling, including retry holds and Qwen judge."""
    def supersede_dev(self):
        """Narrow v8 output-cap recovery; old requests/costs are never rewritten."""
        with self.locked() as (f,rows):
            recovered={r['halt_time'] for r in rows if r['event']=='p5_dev_cap_recovery'}
            for halt in rows:
                if (halt['event']!='panel_validation_halt' or halt['time'] in recovered or
                    halt.get('identity')!='dev/ia16a766729f914abd691307ee67fec15/VE/pro/defender/0' or
                    halt.get('error')!='provider exceeded per-call token cap' or halt.get('model')!='pro'):
                    continue
                history=[r for r in rows if r.get('identity')==halt['identity']]
                req=next(r for r in reversed(history) if r['event']=='reserve')
                reply=next(r for r in reversed(history) if r['event']=='complete')
                if (req['max_output_tokens']!=1024 or reply['billed_output_tokens']!=1095 or
                    reply['finish_reason']!='MAX_TOKENS' or reply['revision']!=MODELS['pro'] or
                    reply['input_tokens']>req['max_input_tokens'] or
                    req['metadata'].get('block_id')!='dual_judge/dev'):
                    raise PreflightError('v8 dev halt evidence changed; no recovery')
                self.append(f,{'event':'p5_dev_cap_recovery','halt_time':halt['time'],
                    'identity':halt['identity'],'sample':False,
                    'reason':'2026-09-22 v9 harness amendment: superseded dev; 4096 billed-output cap; retain costs'})
            pending,_,_,_,blocked=self.state(rows)
            if 'block:dual_judge/dev' in pending:
                if blocked or set(pending)!={'block:dual_judge/dev'}:
                    raise PreflightError('cannot supersede dev with unresolved billing')
                self.append(f,{'event':'block_release','block_id':'dual_judge/dev',
                    'released_usd':str(pending['block:dual_judge/dev']),
                    'reason':'superseded incomplete v8 dev; unused reservation only; no refund or completed sample'})

    def reserve(self, request):
        meta=request.metadata
        if meta.get('arm') in ARMS:
            with self.locked() as (_,rows):
                reservations={r['identity']:r for r in rows if r['event']=='reserve'}
                charged=Decimal(0);shared=Decimal(0)
                for row in rows:
                    if row['event'] not in ('complete','interrupted','infrastructure_failure','panel_halt'):
                        continue
                    source=reservations.get(row.get('identity'),{}).get('metadata',{})
                    amount=Decimal(row.get('cost_usd',row.get('infrastructure_hold_usd','0')))
                    if source.get('item_id')==meta.get('item_id'):
                        if source.get('role')=='paraphrase':shared+=amount
                        elif source.get('arm')==meta['arm']:charged+=amount
                auxiliary, _ = revision_paraphrase_costs(HERE)
                shared += auxiliary.get(meta.get('item_id'), Decimal(0))
                # Until a paraphrase is billed, reserve its full scheduled cost.
                shared=max(shared,cost('replication',*STAGES['paraphrase']))
                if charged+shared+Decimal('.0004')+cost(request.model,request.max_input_tokens,request.billed_output_cap)>MATCHED_CAP:
                    raise BudgetExceeded(f'matched item-arm {MATCHED_CAP} ceiling, including infrastructure holds')
        return super().reserve(request)


def ledger(cap):
    cap=Decimal(str(cap))
    if not cap.is_finite() or cap<=0 or cap>CAP:
        raise PreflightError('explicit positive --cap-usd <=40 required; this build authorizes $0')
    return P5Ledger(HERE/'runs/study/costs.jsonl',cap)


def run(split,cap,resume=False):
    f=require_gates(split=='scored'); plan=SCENARIOS[f['scenario']]
    book=ledger(cap); book.allowance('p5-local-envelope','.1344')
    block=f'{STUDY_REVISION}/{f["scenario"]}/{split}'
    n=len(scheduled_materials(split))
    online=sum((cost('pro',*stage_limits(a,s)) for a in ARMS for s in stage_list(a)),Decimal(0))
    if len(plan)>1:
        online+=sum((cost('replication',*stage_limits(a,'lone' if a=='L' else 'judge','replication')) for a in ARMS),Decimal(0))
    book.reserve_block(block,str(n*online),resume=resume,schedule=f['scenario'],split=split)
    pro=PaidClient(VertexBackend(),book,block,reuse_completed=True)
    clients={'pro':pro}
    if 'replication' in plan: clients['replication']=PaidClient(OpenRouterBackend(native_counter()),book,block,reuse_completed=True)
    trials_path=run_path(split,'trials.jsonl'); existing=read(trials_path)
    done={(r['item_id'],r['condition'],r['judge']) for r in existing}
    assignments=[(i,a) for i in scheduled_materials(split) for a in ARMS];random.Random(SEED).shuffle(assignments)
    stopped=None
    try:
        for item,arm in assignments:
            verify_freeze()  # Source/review changes halt the whole study before the next block.
            if all((item['id'],arm,j) in done for j in plan):continue
            _,halted=infrastructure_state(book)
            active={j:c for j,c in clients.items() if j not in halted}
            if 'pro' in halted: raise InfrastructureError('Gemini protocol roles halted')
            if not active:break
            events=[]
            try:
                local_path=run_path(split,'local-events.jsonl')
                cache=[r['event'] for r in read(local_path) if r['item_id']==item['id'] and r['arm']==arm]
                rows=execute(item,arm,pro,active,local_events=events,local_cache=cache,
                    event_sink=lambda e:append(local_path,{'item_id':item['id'],'arm':arm,'event':e}))
                for row in rows:
                    key=(row['item_id'],row['condition'],row['judge'])
                    if key not in done: append(trials_path,row);done.add(key)
            finally:
                pass  # Every local result is fsynced before the next provider call.
    except (PreflightError,ValueError) as exc:
        stopped=str(exc)
    finally:
        for c in clients.values():c.close()
    rows=read(trials_path)
    _,halted=infrastructure_state(book)
    report=analyze(rows,scheduled_materials(split),labels(),plan,allow_missing=True)
    report.update(stopped=stopped,halted_judges=halted)
    if split=='dev':
        # Source-fidelity must be manually reviewed; contract alone never passes dev.
        report.update(passed=False,source_fidelity_review_required=True,
            **contract_report(rows,len(assignments),plan))
        gate_receipt('dev',report,f['manifest_sha256'])
    write_json(run_path(split,'analysis.json'),report)
    if not stopped and not halted and report['missing']==0:book.release_block(block)
    return report


def retained_paraphrase_request(book, req):
    """Resume original request bytes, allowing only the authoring prompt to age.

    PaidClient still enforces the full cached/frozen-request contract. Bind the
    original reservation to this exact dossier, role, attempt and call ceiling
    before restoring its messages. This also preserves infrastructure retries.
    """
    with book.locked() as (_, rows):
        prior=next((r for r in reversed(rows) if r.get('identity')==req.identity and r['event']=='reserve'),None)
    if prior is None:
        return req
    expected=asdict(req)
    expected['metadata']={**expected['metadata'],'block_id':'shared-paraphrase'}
    if any(prior.get(k)!=v for k,v in expected.items() if k!='messages'):
        raise PreflightError('retained paraphrase dossier or request contract changed')
    return replace(req,messages=prior['messages'])


def save_paraphrase_progress(dossiers, output, label_map):
    archive(HERE/'materials/paraphrases.jsonl.gz',output)
    by_id={r['id']:r for r in output if not r['excluded']}
    for split in ('dev','scored'):
        archive(HERE/f'materials/{split}.jsonl.gz',[{'id':d['id'],'group':label_map[d['id']]['family'],
            'split':split,'payload':{**d,'argument':by_id[d['id']]['argument']},
            'paraphrase_status':'QWEN_PENDING_REVIEW'} for d in dossiers
            if label_map[d['id']]['split']==split and d['id'] in by_id])
    write_json(HERE/'runs/study/paraphrase-status.json',{
        'slots':len(dossiers),'completed':len(output),'accepted':len(by_id),
        'paraphrase_failed':sum(r['excluded'] for r in output),
        'excluded_ids':[r['id'] for r in output if r['excluded']]})


def paraphrase(cap, *, cached_only=False, revision=False):
    if any(r.get('identity','').startswith('scored/') for r in read(HERE/'runs/study/costs.jsonl')):
        raise PreflightError('scored material change requires an amendment and separately labeled run')
    if revision:
        from experiments.p5_revision import revision_ledger
        if not cached_only:
            import os
            if not os.environ.get('OPENROUTER_API_KEY'):
                raise PreflightError('OPENROUTER_API_KEY absent; orchestrator must run the v7 paraphrase command')
        book=revision_ledger('paraphrase', cap, cached_only=cached_only)
    else:
        book=Ledger(HERE/'runs/study/costs.jsonl',CAP) if cached_only else ledger(cap)
    f=verify_freeze(paraphrase_progress=True)
    block='shared-paraphrase'
    # Keep the authorized aggregate envelope (and resumable legacy block).
    # Each call reserves the higher fallback rate; stop if the remainder cannot
    # fund it. Provider fallback does not authorize an aggregate budget increase.
    client=None
    if not cached_only:
        provider=json.loads((HERE/'checks/provider-preflight.json').read_text())
        if provider.get('freeze_sha256')!=f['manifest_sha256'] or not provider.get('models',{}).get('replication',{}).get('passed'):
            raise PreflightError('Qwen provider-native smoke gate required before paraphrasing')
        if revision:
            book.recover_paraphrase_routing()
        book.reserve_block(block,str(Decimal(str(cap)) if revision else 84*cost('replication',*STAGES['paraphrase'])),resume=True)
        client=PaidClient(OpenRouterBackend(native_counter()),book,block,reuse_completed=True)
    dossiers=read(HERE/'materials/dossiers.jsonl.gz'); output=[]
    label_map={r['id']:r for r in labels(False)}
    try:
        for dossier in dossiers:
            item={'id':dossier['id'],'split':'materials','payload':dossier}
            attempts=[];violation=None
            for turn in range(2):
                req=request(item,'shared','paraphrase',turn=turn)
                if turn:
                    req=replace(req,messages=[req.messages[0],{**req.messages[1],
                        'content':req.messages[1]['content']+'\nValidation violation in the first attempt: '+violation+
                        '\nThis is the single correction attempt. Rewrite all steps, fixing this violation and obeying every output constraint.'}])
                req=retained_paraphrase_request(book,req)
                if cached_only:
                    req=replace(req,metadata={**req.metadata,'block_id':block})
                    reply=book.cached_reply(req)
                    if reply is None:
                        if turn:
                            break  # Retain the first failure; never buy a correction.
                        raise PreflightError('cached paraphrase missing; generation forbidden: '+req.identity)
                else:
                    reply=client.call(req)
                texts,violation=validate_reply(reply.text,dossier)
                acceptance = None
                if texts is not None and violation is None:
                    from experiments.p5_semantics import acceptance_check
                    acceptance = acceptance_check(dossier, texts)
                    if not acceptance['passed']:
                        # Never expose recovered kind/localization to the writer.
                        violation = ('Preserve every step and conditional while genuinely rewriting; '
                                     'keep atomic claim phrases verbatim; minimum normalized Levenshtein distance on atomic-masked text is 0.20. '
                                     + acceptance.get('error', 'Insufficient rewrite or changed licensing.'))
                attempts.append({'identity':req.identity,'request_sha256':digest(req.messages),
                    'response_sha256':digest(reply.text),'revision':reply.revision,
                    'served_provider':reply.response.get('provider'),'violation':violation})
                if violation is None:
                    break
            status='paraphrase-failed' if violation else 'QWEN_PENDING_REVIEW'
            result={'id':dossier['id'],'status':status,'excluded':bool(violation),
                'provenance':{'method':'Qwen72 independently re-structured prose with atomic claims verbatim; not a free paraphrase; at most one validation correction',
                    'input_sha256':digest(dossier),**attempts[-1],
                    'attempts':attempts,'sanitiser':SANITISER,
                    'sanitised_texts_sha256':digest(texts),
                    'semantic_acceptance':acceptance,
                    'independent_qwen_pass':violation is None}}
            if texts is not None:
                result['argument']='\n\n'.join(texts.values())
            output.append(result)
            # Checkpoint every terminal slot. The billing ledger remains the
            # source for revalidation after any interruption, including mid-retry.
            save_paraphrase_progress(dossiers,output,label_map)
    finally:
        if client is not None:client.close()
    if not cached_only:book.release_block(block)
    return {'slots':len(output),'accepted':sum(not r['excluded'] for r in output),
        'paraphrase_failed':sum(r['excluded'] for r in output),'review_required':True,'refreeze_required':True}


def reconcile(receipt=None):
    """Offline settlement of interrupted study and separately capped revision calls."""
    from experiments.p5_revision import LIMITS
    books=[Ledger(HERE/'runs/study/costs.jsonl',CAP)]
    books += [Ledger(path,LIMITS[path.name.removesuffix('-costs.jsonl')])
              for path in sorted((HERE/'runs').glob('revision-*/*-costs.jsonl'))]
    reports={}; charged=Decimal(0)
    for book in books:
        events=book.reconcile_interrupted()
        amount=sum((Decimal(e['cost_usd']) for e in events),Decimal(0))
        charged+=amount
        if receipt and book==books[0]:
            events+=book.reconcile(receipt.get('releases',{}),receipt.get('allowances',{}))
        with book.locked() as (_,rows):
            pending,spent,_,revisions,blocked=book.state(rows)
        reports[str(book.path.relative_to(HERE))]={
            'events':events,'interrupted_charge_usd':str(amount),
            'interrupted_total_usd':str(sum((Decimal(r['cost_usd']) for r in rows if r['event']=='interrupted'),Decimal(0))),
            'pending':{k:str(v) for k,v in pending.items()},'spent_usd':str(spent),
            'cap_usd':str(book.cap),'uncommitted_usd':str(book.cap-spent-sum(pending.values(),Decimal(0))),
            'blocked':blocked,'revisions':revisions}
    result={'interrupted_charge_usd':str(charged),'ledgers':reports,'generation_calls':0,
        'policy':'Interrupted calls charged at full ceiling; no trial or reply inferred. Identical requests may be re-issued within existing caps. Revision charges remain inside study envelopes, not added twice.'}
    write_json(HERE/'checks/reconciliation.json',result)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['generate','paraphrase','review','inventory','freeze','probe','preflight',
        'preflight-openrouter','calibrate-gemini','known-answer','dev','scored','resume','reconcile','analyze','explanations'])
    parser.add_argument('--cap-usd',type=Decimal,default=Decimal(0))
    parser.add_argument('--scenario',choices=SCENARIOS,default='dual_judge')
    parser.add_argument('--split',choices=['dev','scored'],default='scored')
    parser.add_argument('--export',type=Path);parser.add_argument('--submit',type=Path)
    parser.add_argument('--adjudicate',type=Path);parser.add_argument('--count-tokens',action='store_true')
    parser.add_argument('--revision', choices=['v7']);
    parser.add_argument('--offline',action='store_true');parser.add_argument('--receipt',type=Path)
    args=parser.parse_args(argv)
    try:
        if args.command=='generate':
            result=generate();write_json(HERE/'prompts.json',{'system':SYSTEM,'roles':ROLES,'schema':VERDICT_SCHEMA,'stages':STAGES,
        'effective_stage_caps':{a:{m:{s:stage_limits(a,s,m) for s in stage_list(a)} for m in ('pro','replication')} for a in ARMS}})
        elif args.command=='review':
            result=review.review_export(args.export) if args.export else review.submit(args.submit) if args.submit else review.adjudicate(args.adjudicate) if args.adjudicate else review.gate()
        elif args.command=='freeze':result=freeze(args.scenario)
        elif args.command=='calibrate-gemini':
            from experiments.p5_tokens import calibrate
            if args.offline:raise PreflightError('calibrate-gemini requires free Vertex countTokens')
            result=calibrate(args.cap_usd)
        elif args.command=='known-answer':
            result=known_answer(materials(),check_labels());write_json(HERE/'checks/known-answer.json',result)
        elif args.command in ('preflight','inventory','preflight-openrouter','probe'):
            from experiments import p5_preflight as pf
            if args.command=='inventory':result=pf.inventory(args.count_tokens)
            elif args.command=='preflight':result=pf.preflight(args.offline)
            else: result=pf.provider_smoke(args.cap_usd,only_openrouter=args.command=='preflight-openrouter',cached_only=args.offline)
        elif args.command=='paraphrase':result=paraphrase(args.cap_usd,cached_only=args.offline,revision=args.revision=='v7')
        elif args.command in ('dev','scored','resume'):result=run(args.split if args.command=='resume' else args.command,args.cap_usd,args.command=='resume')
        elif args.command=='reconcile':
            result=reconcile(json.loads(args.receipt.read_text()) if args.receipt else None)
        elif args.command=='explanations':
            from experiments.p5_preflight import explanations
            result=explanations(args.split,args.export,args.submit)
        else:
            f=verify_freeze();result=analyze(read(run_path(args.split,'trials.jsonl')),scheduled_materials(args.split),labels(),
                SCENARIOS[f['scenario']],read(run_path(args.split,'ratings.jsonl')),allow_missing=True)
            from experiments.p5_preflight import cost_report
            result['costs']=cost_report(args.split)
            result['cost_accuracy_frontier']={j:{a:{'mean_cost_usd':result['costs']['mean_attributed_cost_by_arm'][a],
                'worst_flaw_accuracy':r['worst_flaw'][a], 'benign_completion':r['accuracy'][a]['benign']} for a in ARMS}
                for j,r in result['judges'].items()}
            write_json(run_path(args.split,'analysis.json'),result)
        print(json.dumps(result,indent=2,default=str))
        return 2 if result.get('requested_models_passed',result.get('passed')) is False else 0
    except (PreflightError,ValueError,FileNotFoundError) as exc:
        print(f'P5 blocked: {exc}',file=sys.stderr);return 3 if isinstance(exc,BudgetExceeded) else 2

if __name__=='__main__':raise SystemExit(main())
