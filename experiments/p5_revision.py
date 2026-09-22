"""Bounded v6 material regeneration/review; no dev/scored generation."""
import argparse
from decimal import Decimal
import json
import time

from experiments import p5, p5_review
from experiments.p5_materials import HERE, read, write_json
from ve_experiments.json_response import strip_json_fence
from ve_experiments.paid import Ledger, PaidClient, PaidRequest, PreflightError, VertexBackend, digest, packed

LIMITS = {'paraphrase': Decimal('.40'), 'gemini-review': Decimal('1')}


def revision_ledger(stage, cap, *, cached_only=False):
    limit = LIMITS[stage]
    cap = Decimal(str(cap))
    if not cached_only and (not cap.is_finite() or not 0 < cap <= limit):
        raise PreflightError(f'{stage} requires positive cap <= {limit}')
    if not cached_only:
        # Conservative authorization envelope in the unchanged study-wide $40
        # ledger; actual bills live in the separately capped revision ledger.
        Ledger(HERE/'runs/study/costs.jsonl', p5.CAP).allowance('v6-'+stage+'-envelope', str(cap))
    return Ledger(HERE/f'runs/revision-v6/{stage}-costs.jsonl', limit if cached_only else cap)


def independent_prose(base=HERE):
    from experiments.p5_semantics import acceptance_check
    dossiers = {d['id']:d for d in read(base/'materials/dossiers.jsonl.gz')}
    rows = read(base/'materials/paraphrases.jsonl.gz')
    checks = []
    for row in rows:
        dossier = dossiers[row['id']]
        paragraphs = row.get('argument','').split('\n\n')
        if len(paragraphs) != len(dossier['nodes']):
            checks.append({'id':row['id'],'passed':False}); continue
        result = acceptance_check(dossier, dict(zip([n['id'] for n in dossier['nodes']], paragraphs)))
        result.update(id=row['id'], passed=result['passed'] and row['provenance'].get('independent_qwen_pass',False))
        checks.append(result)
    return {'passed':len(rows)==84 and {r['id'] for r in rows}==set(dossiers) and all(r['passed'] for r in checks),
            'packets':len(rows),'checks':checks,'generation_calls':0}


REVIEW_PROMPT = '''Independently review ONE proposed English argument against its authoritative records, declared premises and glossary. You have no hidden labels, formal graph, other review or sibling packet. Compare source and rewritten prose for every step, original root, added assumptions, repaired flaws, sense preservation and answer leakage. Run a zero-then-one-relaxation licensing analysis mentally: can every inference be licensed? If not, is there a meaning shift or an unsupported sample/lot transfer? Localize it using the supplied ordered step_ids. Return one JSON object with keys checks, annotation, corrections, notes. Checks: source_fidelity, root_preserved, no_added_assumption, no_repaired_flaw, complete_sense_mapping, localization_anchored, no_answer_leakage (all explicit booleans). Annotation: kind (shift/smuggle/benign), sense_use_mapping (every step ID to the record and meaning it uses), required_assumptions (array), root_meaning (string), acceptable_locations (one singleton consumer ID and one producer/consumer pair; for benign identify the corresponding branch edge), source_evidence (nonempty array). Corrections is an array of substantive problems. Notes must disclose uncertainty; do not approve on faith. Keep sense mappings compact (record ID and sense phrase), evidence to one short sentence and notes brief. Output compact JSON; do not reproduce the packet.'''


def gemini_review(cap):
    # Never buy a review of drafts, partial generation, or the superseded no-op.
    if not independent_prose()['passed']:
        raise PreflightError('all 84 regenerated semantic/distance-accepted Qwen paraphrases required before Gemini review')
    p5.verify_freeze()
    destination = HERE/'runs/revision-v6/review-packets.json'
    p5_review.review_export(destination)
    manifest = json.loads(destination.read_text())
    book = revision_ledger('gemini-review',cap)
    client = PaidClient(VertexBackend(),book,reuse_completed=True)
    submitted = []; failures = []
    try:
        for assignment, paths in enumerate(manifest['assignments'],1):
            for path in paths:
                source = json.loads((destination.parent/path).read_text())[0]
                payload = {k:source[k] for k in ('packet','source_argument')}
                # Single packet per fresh request. No source-label, previous
                # annotation, previous reply or sibling context is included.
                req = PaidRequest('review-v6/'+source['item_id'],'pro',
                    [{'role':'system','content':REVIEW_PROMPT},{'role':'user','content':packed(payload)}],
                    7000,1024,metadata={'role':'material-review','packet_sha256':source['packet_sha256']})
                started = time.monotonic()
                reply = client.call(req)
                try:
                    annotation = json.loads(strip_json_fence(reply.text))
                    if set(annotation) != {'checks','annotation','corrections','notes'}:
                        raise ValueError('review schema mismatch')
                    row = {**annotation,'item_id':source['item_id'],'packet_sha256':source['packet_sha256'],
                           'reviewer_id':f'gemini-3.1-pro-v6-assignment-{assignment}',
                           'reviewer_kind':'model','model_family':'Google Gemini',
                           'minutes':max(reply.latency_s,time.monotonic()-started)/60,
                           'response_sha256':digest(reply.text),'blinding':'fresh context; public packet and source only',
                           'lead_hand_check':'deferred'}
                    submitted.append(row)
                except (ValueError, TypeError) as exc:
                    failures.append({'item_id':source['item_id'],'error':str(exc),'response_sha256':digest(reply.text)})
                write_json(HERE/'runs/revision-v6/gemini-submission.json',submitted)
                write_json(HERE/'checks/gemini-review-v6-status.json',{'completed':len(submitted)+len(failures),'valid':len(submitted),'failures':failures,'cap_usd':str(cap)})
    finally:
        client.close()
    # Submit only once, preserving authentic model answers (never fill labels).
    prior = {(r.get('item_id'),r.get('reviewer_id'),r.get('packet_sha256')) for r in read(HERE/'materials/review-ledger.jsonl.gz')}
    fresh = [r for r in submitted if (r['item_id'],r['reviewer_id'],r['packet_sha256']) not in prior]
    path = HERE/'runs/revision-v6/gemini-new-submission.json'
    write_json(path,fresh)
    if fresh:
        p5_review.submit(path,run_gate=False)
    return {'completed':len(submitted)+len(failures),'valid':len(submitted),'failures':failures,'review_gate':p5_review.gate()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['gemini-review','check'])
    parser.add_argument('--cap-usd',type=Decimal,default=Decimal(0))
    args=parser.parse_args()
    result=gemini_review(args.cap_usd) if args.command=='gemini-review' else independent_prose()
    print(json.dumps(result,indent=2))
    if args.command == 'check' and not result['passed']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
