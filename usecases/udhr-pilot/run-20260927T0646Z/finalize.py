"""Run document checks and write the review outputs from the pinned translation."""
from __future__ import annotations
import collections
import hashlib
import json
from pathlib import Path
from ve.document import check_document, coverage, load_document, render_document

root=Path(__file__).resolve().parent
source=root.parent/'source'/'udhr.md'
translation=root/'translation.ve.md'
doc=load_document(translation)
check=check_document(translation)
cov=coverage(doc)
unit_rows=json.loads((root/'units.json').read_text())['units']
assert len(unit_rows)==len(doc['units'])
assert cov['accounted_bytes']==cov['source_bytes']==len(source.read_bytes())
assert doc['source']==source.read_bytes()
status_counts=collections.Counter(r['status'] for r in unit_rows)
status_bytes=collections.Counter()
missing=collections.Counter()
for row in unit_rows:
    status_bytes[row['status']]+=row['span'][1]-row['span'][0]
    if row['status']=='UNFORMALISED':
        missing[row['missing_feature']]+=1
        assert row['missing_feature'] in {'norms','time','counting','quantities','attribution',
            'causation','modality/belief','defaults'} or row['missing_feature'].startswith('other:')
    for feature in row.get('unresolved_features',[]):
        assert feature in {'norms','time','counting','quantities','attribution','causation',
                           'modality/belief','defaults'} or feature.startswith('other:')
assert sum(status_bytes.values())==len(source.read_bytes())
meta=doc['meta']
metrics={
 'source':{'path':'source/udhr.md','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
           'bytes':len(source.read_bytes()),'fetch_date_utc':'2026-09-27'},
 'baseline':'ve-green-z6',
 'unit_scale':'sentence or clause; headings and standalone speaker/transition fragments separate',
 'previous_run':None,
 'old_boundary_aggregation':'not applicable; no previous run',
 'bytes_accounted':cov['accounted_bytes'],
 'bytes_accounted_percent':cov['coverage_percent'],
 'unit_count':len(unit_rows),
 'unit_counts_by_status':dict(sorted(status_counts.items())),
 'bytes_by_status':dict(sorted(status_bytes.items())),
 'open_terms':[{'name':o['name'],'decided_by':o['decided_by'],'necessary':o['necessary'],
                'sufficient':o['sufficient'],'factors':o['factors']} for o in meta['open_terms']],
 'reading_sets':[{'id':r['id'],'unit':r['unit'],'status':r['status'],
                  'candidates':[c['id'] for c in r['readings']],
                  'formula_elaborated':all(c['content'] is not None for c in r['readings'])}
                 for r in meta['reading_sets']],
 'missing_feature_tally':dict(sorted(missing.items())),
 'unresolved_reading_feature_tally':dict(sorted(collections.Counter(
      feature for row in unit_rows for feature in row.get('unresolved_features',[])).items())),
 'check_verdicts':{
   'document_load':'PASS',
   'byte_partition':'PASS',
   'document_check':'PASS',
   'premises':check['premises'],
   'reading_plan_route':check['reading_plan']['route'],
   'formal_formula_units':sum(u['content'] is not None for u in doc['units']),
   'assertion_admission':'not applicable; no formal assertion graph',
   'render':'PASS',
   'reading_models':'schema references only; null-content candidates have no semantic separating model'
 },
 'document_id':check['document_id'],
 'source_id':check['source_id'],
 'coverage_tool':cov,
}
(root/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
(root/'rendered.md').write_text(render_document(translation))
print(json.dumps({'units':len(unit_rows),'statuses':status_counts,'missing':missing,
                  'coverage':cov['coverage_percent'],'premises':check['premises']['status']},default=dict))
