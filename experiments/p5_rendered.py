"""2026-09-22 orchestrator amendment: reviewed generator-rendered prose.

Historical reviews remain historical. Only the explicitly authorized report-level
policy may combine the round-5 report with a fresh, hash-bound Gemini review.
"""
import argparse
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import json
import hashlib
import re
import subprocess

from experiments.p5_materials import HERE, read, archive, write_json
from experiments.p5_isolation import blind_packet
from ve_experiments.json_response import strip_json_fence
from ve_experiments.paid import (Ledger, PaidClient, PaidRequest, VertexBackend,
                                 PreflightError, digest, packed)

POLICY = 'generator-rendered-2026-09-22'
HISTORICAL_ARCHIVE_SHA256 = '621f3e6a56c5fc1196724da01de4e0f63f722875bf2367aeee1e2f4f5e019842'
HISTORICAL_REPORT_SHA256 = 'a36d6e2c0c84b94bbd3148f3de4dbed66b11092daa4ba4bd63754aebffbdbb0a'
HISTORICAL_COMMIT = 'e4114957a70985934a9dd85ba0b0a2f703827fed'
PROMPT = '''Review this ONE proposed argument as experimental material. You see only its public packet, no gold labels or sibling packets. It may deliberately contain a meaning shift or a missing sample-to-lot assumption; that is NOT a material defect. Determine whether the authoritative records and premises unambiguously support a benign reading, a meaning shift, or a missing assumption, and whether the original root and intended flaw remain intelligible. Check for extra unintended flaws, answer hints, or ambiguous/unrecoverable interpretation. The conditional-alternative sentence states unassumed possibilities, not facts. For a flawed argument locate the producer/consumer pair of steps and identify the record-based discrepancy. For benign use an empty locations list. Return compact JSON only: {"ready":boolean,"kind":"shift|smuggle|benign|uncertain","locations":[step IDs],"evidence":"brief record-grounded reason","issues":[material defects or uncertainties]}. Ready means suitable as material, not that the argument is valid. Do not approve on faith. Keep the whole answer under 120 words.'''


def normalize_tail(packet):
    result = deepcopy(packet)
    result['argument'] = re.sub(r' The checks that [^\n]+', '', result['argument'])
    for n in result['nodes']:
        n['text'] = re.sub(r' The checks that .*', '', n['text'])
    return result


def tails(packet):
    return sorted(re.findall(r' The checks that [^\n]+', packet['argument']))


def provenance(base=HERE):
    policy_path = base/'materials/prose-policy.json'
    if not policy_path.exists():
        return {'passed':False, 'reason':'dated generator-rendered policy absent'}
    policy = json.loads(policy_path.read_text())
    dossiers = {r['id']:r for r in read(base/'materials/dossiers.jsonl.gz')}
    historical = {r['id']:r for r in read(base/'materials/round5-reviewed-packets.jsonl.gz')}
    items = read(base/'materials/dev.jsonl.gz') + read(base/'materials/scored.jsonl.gz')
    expected = {r['id']:digest(r['payload']) for r in items}
    failures = []
    for item in items:
        i = item['id']; current = item['payload']; old = historical.get(i)
        if (current != dossiers.get(i) or old is None or
                normalize_tail(current) != normalize_tail(old) or tails(current) != tails(old)):
            failures.append(i)
    return {'passed':hashlib.sha256((base/'materials/round5-reviewed-packets.jsonl.gz').read_bytes()).hexdigest()==HISTORICAL_ARCHIVE_SHA256 and policy.get('policy')==POLICY and len(items)==84 and
            len(expected)==84 and set(expected)==set(dossiers)==set(historical) and
            policy.get('packet_hashes')==expected and not failures,
            'policy':POLICY, 'independent_paraphrase_required':False,
            'prose':'generator-rendered from the same VE graphs',
            'historical_transfer':'all public fields identical except conditional-tail placement',
            'packets':len(items), 'failures':failures, 'generation_calls':0}


def prepare(base=HERE):
    from experiments import p5
    if any(r.get('identity','').startswith(('dev/','scored/')) for r in read(base/'runs/study/costs.jsonl')):
        raise PreflightError('cannot adopt material after study inference')
    # Preserve the completed v7 material acceptance evidence before restoring all slots.
    destination = base/'materials/rejected-v7-paraphrases.jsonl.gz'
    if not destination.exists():
        destination.write_bytes((base/'materials/paraphrases.jsonl.gz').read_bytes())
    rows = read(destination)
    violations = Counter(a['violation'] for r in rows for a in r['provenance']['attempts'] if a['violation'])
    stats = {'accepted':sum(not r['excluded'] for r in rows), 'slots':len(rows),
             'violations':sum(violations.values()), 'violation_counts':dict(violations)}
    write_json(base/'checks/v7-final-acceptance.json',stats)
    historical = base/'materials/round5-reviewed-packets.jsonl.gz'
    if not historical.exists():
        historical.write_bytes(subprocess.check_output(['git','show',HISTORICAL_COMMIT+
            ':experiments/P5-shifting-definitions/materials/dossiers.jsonl.gz'],cwd=p5.ROOT))
    dossiers = read(base/'materials/dossiers.jsonl.gz')
    labels = {r['id']:r for r in read(base/'labels.jsonl.gz')}
    for split in ('dev','scored'):
        archive(base/f'materials/{split}.jsonl.gz',[
            {'id':d['id'],'group':labels[d['id']]['family'],'split':split,
             'payload':d,'prose_status':POLICY} for d in dossiers if labels[d['id']]['split']==split])
    archive(base/'materials/paraphrases.jsonl.gz',[
        {'id':d['id'],'argument':d['argument'],'excluded':False,'status':POLICY,
         'provenance':{'method':'generator-rendered from same VE graphs',
                       'independent_qwen_pass':False,'input_sha256':digest(d),
                       'amendment':'2026-09-22 orchestrator; v6/v7 evidence and costs retained'}} for d in dossiers])
    write_json(base/'materials/prose-policy.json',{'policy':POLICY,
        'authority':'Explicit orchestrator instruction, 2026-09-22',
        'historical_commit':HISTORICAL_COMMIT,
        'packet_hashes':{d['id']:digest(d) for d in dossiers},
        'review_policy':'Accept the historical round-5 Claude materials report plus current isolated Gemini packet reviews. Round 6 is unblinded supporting fidelity/leakage evidence.',
        'source_limit':'Generator-rendered from the same VE graphs: VE formalisation is easier than on independently authored prose. VE repair remains charged.'})
    result = provenance(base)
    if not result['passed']:
        raise PreflightError('historical transfer differs by more than tail placement')
    return result


class ReviewBackend(VertexBackend):
    """Free full-wire native count; material review has its own bounded ledger.

    Its billed prompt is checked against the reserved input cap after dispatch;
    no study-config calibration is invented for this separate review prompt.
    """
    def count(self, request):
        from experiments.p5_tokens import count_wire
        contents, cfg = count_wire(request)
        return self.client.models.count_tokens(model='gemini-3.1-pro-preview',
            contents=contents,config=cfg).total_tokens


def review_request(item, version=2):
    from experiments import p5
    if version == 2:
        # Exact judge-visible English packet: records contain all sense definitions.
        content = p5.packet(item, "L")
    elif version == 1:
        content = packed(blind_packet(item["payload"]))
    else:
        raise ValueError("unknown review request version")
    return PaidRequest(('review-rendered-v8/' if version == 1 else 'review-rendered-v8-1024/')+item['id'],'pro',[
        {'role':'system','content':PROMPT},
        {'role':'user','content':content}],3500,768 if version == 1 else 1024,
        metadata={'role':'material-review','packet_sha256':digest(item['payload']),
                  'item_id':item['id'],'policy':POLICY})


def validate_review(row, item):
    if not isinstance(row,dict) or set(row) != {'ready','kind','locations','evidence','issues'}:
        raise ValueError('review schema mismatch')
    ids = {n['id'] for n in item['payload']['nodes']}
    if (type(row['ready']) is not bool or row['kind'] not in ('shift','smuggle','benign','uncertain') or
        not isinstance(row['locations'],list) or any(n not in ids for n in row['locations']) or
        len(set(row['locations']))!=len(row['locations']) or
        not isinstance(row['evidence'],str) or not row['evidence'].strip() or
        not isinstance(row['issues'],list) or any(not isinstance(s,str) for s in row['issues'])):
        raise ValueError('invalid review fields')
    return row


def recover_review_cap(book):
    """Retain and acknowledge only the initial 768-token review overrun <=1024."""
    with book.locked() as (f, rows):
        recovered = {r['halt_time'] for r in rows if r['event']=='material_review_cap_recovery'}
        for halt in rows:
            if (halt['event']!='panel_validation_halt' or halt['time'] in recovered or
                halt.get('model')!='pro' or not halt['identity'].startswith('review-rendered-v8/') or
                halt['error']!='provider exceeded per-call token cap'):
                continue
            history = [r for r in rows if r.get('identity')==halt['identity']]
            req = next(r for r in history if r['event']=='reserve')
            reply = next(r for r in history if r['event']=='complete')
            if (req['max_output_tokens']==768 and req['metadata'].get('policy')==POLICY and
                reply['input_tokens']<=req['max_input_tokens'] and
                768 < reply['billed_output_tokens'] <= 1024 and reply['revision']=='gemini-3.1-pro-preview'):
                book.append(f,{'event':'material_review_cap_recovery','halt_time':halt['time'],
                    'identity':halt['identity'],'sample':False,
                    'reason':'P5 revision 8 review feasibility correction; paid cost retained; incomplete reply remains invalid; subsequent calls cap 1024 within cumulative $1'})


def gemini_review(cap):
    from experiments import p5
    cap = Decimal(str(cap))
    if not cap.is_finite() or not 0 < cap <= 1:
        raise PreflightError('Gemini material review requires positive cumulative cap <= $1')
    if not provenance()['passed']:
        raise PreflightError('all 84 generator-rendered packets and historical transfer required')
    p5.verify_freeze()
    Ledger(HERE/'runs/study/costs.jsonl',p5.CAP).allowance('v8-gemini-review-envelope',str(cap))
    book = Ledger(HERE/'runs/revision-v8/gemini-review-costs.jsonl',cap)
    recover_review_cap(book)
    client = PaidClient(ReviewBackend(),book,reuse_completed=True)
    path = HERE/'checks/gemini-rendered-submission.json'
    prior = {r['item_id']:r for r in json.loads(path.read_text())} if path.exists() else {}
    results = dict(prior); error = None
    # Every call is one fresh context, even across siblings. No export annotations
    # or reference labels enter this function or its provider requests.
    try:
        for item in sorted(p5.materials(),key=lambda i:i['id']):
            old = prior.get(item['id'],{})
            # Keep valid reviews even when negative; never retry a substantive judgment.
            if 'review' in old:
                continue
            req = review_request(item)
            reply = client.call(req)
            row = {'item_id':item['id'],'packet_sha256':digest(item['payload']),
                   'request_sha256':digest(req.messages),'response_sha256':digest(reply.text),
                   'reviewer_id':'gemini-3.1-pro-v8/'+item['id'],
                   'model_family':'Google Gemini','revision':reply.revision,
                   'minutes':reply.latency_s/60,'fresh_context':True,'request_version':2}
            try:
                row['review'] = validate_review(json.loads(strip_json_fence(reply.text)),item)
            except (ValueError,TypeError) as exc:
                row['error'] = str(exc)
            results[item['id']] = row
            write_json(HERE/'checks/gemini-rendered-submission.json',list(results.values()))
            print(json.dumps({'completed':len(results),'valid':sum('review' in r for r in results.values())}),flush=True)
    except PreflightError as exc:
        error = str(exc)
    finally:
        client.close()
    with book.locked() as (_,ledger_rows):
        pending,spent,*_ = book.state(ledger_rows)
    rows = list(results.values())
    status = {'completed_calls':sum(r['event']=='complete' for r in ledger_rows),
              'completed_call_cost_usd':str(sum((Decimal(r['cost_usd']) for r in ledger_rows if r['event']=='complete'),Decimal(0))),
              'infrastructure_holds_usd':str(sum((Decimal(r.get('infrastructure_hold_usd','0')) for r in ledger_rows if r['event'] in ('infrastructure_failure','panel_halt')),Decimal(0))),
              'completed':len(rows),'valid':sum('review' in r for r in rows),
              'cap_usd':str(cap),'spent_usd':str(spent),
              'pending_usd':str(sum(pending.values(),Decimal(0))),'error':error,
              'model':'gemini-3.1-pro-preview','provider':'Vertex ADC',
              'passed':len(rows)==84 and all('review' in r and r['review']['ready'] and not r['review']['issues'] for r in rows)}
    write_json(HERE/'checks/gemini-rendered-status.json',status)
    return status


def review_gate(base=HERE):
    from experiments import p5
    from experiments.p5_leakage import audit
    prov = provenance(base)
    report = base/'checks/round5-review-verification.txt'
    historical = report.read_text()
    historical_ok = (p5.sha(report)==HISTORICAL_REPORT_SHA256 and 'VERDICT: READY (materials)' in historical and
                     'All 84: kind 84/84, localisation 84/84.' in historical)
    rows = (
        json.loads((base/'checks/gemini-rendered-submission.json').read_text())
        if (base/'checks/gemini-rendered-submission.json').exists() else [])
    by_id = {r['item_id']:r for r in rows}
    labels = {r['id']:r for r in read(base/'labels.jsonl.gz')}
    unresolved = []; anchored = []
    ledger = read(base/'runs/revision-v8/gemini-review-costs.jsonl')
    completed = {r['identity']:r for r in ledger if r['event']=='complete'}
    reservations = {r['identity']:r for r in ledger if r['event']=='reserve'}
    for item in read(base/'materials/dev.jsonl.gz') + read(base/'materials/scored.jsonl.gz'):
        row = by_id.get(item['id'],{}); review = row.get('review',{}); label = labels[item['id']]
        req = review_request(item,row.get('request_version',1)); billed = completed.get(req.identity,{})
        try:
            validate_review(review,item)
            reservation = reservations.get(req.identity,{})
            authentic = (reservation.get('messages')==req.messages and
                         reservation.get('metadata')==req.metadata and
                         billed.get('input_tokens',10**9)<=req.max_input_tokens and
                         billed.get('billed_output_tokens',10**9)<=req.max_output_tokens and
                         billed.get('revision')=='gemini-3.1-pro-preview' and
                         digest(billed['text'])==row.get('response_sha256') and
                         json.loads(strip_json_fence(billed['text']))==review)
        except (ValueError,KeyError,TypeError):
            authentic = False
        passed = (authentic and row.get('packet_sha256')==digest(item['payload']) and
            row.get('request_sha256')==digest(req.messages) and review.get('ready') is True and
            not review.get('issues') and review.get('kind')==label['kind'] and
            (review.get('locations')==[] if label['kind']=='benign' else
             set(review.get('locations',[]))==set(label['acceptable_locations'][1])))
        if not passed:
            unresolved.append(item['id'])
        else:
            anchored.append({'id':item['id'],'packet_sha256':digest(item['payload']),
                **{k:label[k] for k in ('kind','acceptable_locations','sense_use_mapping','root_meaning')},
                'anchor_provenance':'reference mappings; round-5 report accepted by amendment; current Gemini diagnosis agrees',
                'gemini_evidence':review['evidence']})
    leakage = audit(base)
    write_json(base/'checks/leakage.json',leakage)
    passed = prov['passed'] and historical_ok and len(anchored)==84 and not unresolved and leakage['passed']
    # Do not freeze partial reference labels as independent annotations.
    archive(base/'materials/anchored-labels.jsonl.gz',anchored if passed else [])
    result = {'passed':passed,'policy':POLICY,'reviewed_slots':len(anchored),'unresolved':unresolved,
        'leakage_passed':leakage['passed'],'provenance_passed':prov['passed'],
        'claude_round5':{'accepted':historical_ok and prov['passed'], 'verdict':'READY (materials)',
            'report_sha256':p5.sha(report),'scope':'historical report-level approval; tail relocation audited separately',
            'limitation':'partial original submission failed old importer; not 84 complete hash-bound blind annotations'},
        'round6':'supporting fidelity/no-kind-leak evidence; explicitly unblinded; tail localisation defect fixed',
        'gemini_current':{'accepted':len(anchored)==84 and not unresolved,'completed':len(rows),
                          'matching_current_diagnoses':len(anchored),'provider':'Vertex ADC'},
        'lead_hand_check':'deferred by orchestrator amendment; no new human review asserted'}
    write_json(base/'checks/review.json',result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','check','gemini-review'])
    parser.add_argument('--cap-usd',type=Decimal,default=Decimal(0))
    args = parser.parse_args()
    result = prepare() if args.command=='prepare' else provenance() if args.command=='check' else gemini_review(args.cap_usd)
    print(json.dumps(result,indent=2))
    if not result['passed']:
        raise SystemExit(2)

if __name__=='__main__':
    main()
