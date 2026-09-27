"""Rebuild the pilot from the pinned source; never modifies the source."""
from __future__ import annotations
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'source' / 'udhr.md'
PIN = 'd6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a'
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN, 'pinned source changed'
text = raw.decode('utf-8')

# The only invented words here are metadata labels, never a replacement for source words.
ENV = {
    'language': 've.core@0.2',
    'profiles': ['documents@1', 'relational-fol@0'],
    'spec_revision': 've-v0.2-expand2-2026-09-25',
    'vocabulary': {
        'sorts': {'person': {'description': 'a human person',
                             'verbalisation': {'singular': 'person', 'plural': 'people'}}},
        'predicates': {},
        'constants': {}
    }
}

OPEN_TERMS = {
    'equal_before_law': ('applicable_court', ['equal legal standing', 'equal legal protection', 'scope of comparators']),
    'inherent_dignity': ('human_rights_interpreter', ['meaning of dignity', 'scope of inherence']),
    'inalienable_rights': ('human_rights_interpreter', ['which rights', 'conditions on transfer or loss']),
    'essential': ('human_rights_interpreter', ['essential for which end', 'degree of necessity']),
    'greatest_importance': ('human_rights_interpreter', ['comparison class', 'measure of importance']),
    'natural_group_unit': ('human_rights_interpreter', ['meaning of natural', 'meaning of fundamental', 'what counts as family']),
    'arbitrary': ('applicable_court', ['legality', 'reasonableness', 'procedural safeguards']),
    'fair': ('applicable_court', ['procedural fairness', 'public access', 'independence']),
    'adequate': ('human_rights_interpreter', ['health needs', 'living conditions', 'resources']),
    'just': ('human_rights_interpreter', ['fairness criteria', 'comparison group']),
    'reasonable': ('human_rights_interpreter', ['hours', 'work setting', 'health and rest']),
    'genuine': ('human_rights_interpreter', ['authenticity of election or prosecution', 'procedural evidence']),
}
open_terms = [dict(name=name, arguments=['person'] if name == 'equal_before_law' else [],
                   decided_by=role, necessary=[], sufficient=[], factors=factors,
                   precedents=[], jurisdiction='universal', version=1)
              for name, (role, factors) in OPEN_TERMS.items()]

# Split only within each displayed block. The separator remains with the prior unit.
segments = []
char_cursor = 0
article = 'title'
for line in text.splitlines(keepends=True):
    start = char_cursor
    char_cursor += len(line)
    if not line.strip():
        # Blank lines belong to the preceding unit, preserving every source byte.
        if segments:
            segments[-1]['end'] = char_cursor
        continue
    if line.startswith('## '): article = line[3:].strip()
    if line.startswith('#'):
        segments.append({'start': start, 'end': char_cursor, 'article': article, 'heading': True})
        continue
    cuts = [0]
    for m in re.finditer(r';\s+|(?<=[.!?])\s+(?=[A-Z])', line):
        if m.start() == 2 and line[:2] in ('1.', '2.', '3.', '4.'): continue
        cuts.append(m.end())
    # Especially long Preamble paragraphs and linked legal clauses need clause units.
    for m in re.finditer(r',\s+and\s+|\s+and\s+should\s+|\s+and\s+(?:is|are)\s+entitled\s+', line):
        if len(line.strip()) > 220 or m.group().strip().startswith('and should') or 'entitled' in m.group():
            cuts.append(m.end() - len(m.group().lstrip().split()[-1]) - 1 if False else m.start() + (2 if m.group().startswith(',') else 0))
    cuts = sorted(set(c for c in cuts if 0 <= c < len(line)))
    for a, b in zip(cuts, cuts[1:] + [len(line)]):
        if a < b:
            segments.append({'start': start+a, 'end': start+b, 'article': article, 'heading': False})
assert ''.join(text[s['start']:s['end']] for s in segments) == text

# Whole-unit status is conservative: a clause with a missing norm is not counted as checked.
def classify(chunk, article, heading):
    stripped = chunk.strip()
    if heading: return 'LABELLED', 'meta', 'specified', None, []
    if stripped in ('Now, therefore,', 'The General Assembly,'):
        return 'LABELLED', 'meta', {'contextual': 'preamble_transition_or_speaker'}, None, []
    lower = stripped.lower()
    names = [n for n in OPEN_TERMS if n.replace('_',' ') in lower]
    if 'equal before the law' in lower: names.append('equal_before_law')
    if 'natural and fundamental group unit' in lower: names.append('natural_group_unit')
    if 'inherent dignity' in lower: names.append('inherent_dignity')
    if 'inalienable rights' in lower: names.append('inalienable_rights')
    names = list(dict.fromkeys(names))
    if article == 'Preamble':
        if lower.startswith('whereas'):
            if 'foundation of freedom' in lower or 'resulted in' in lower: feature = 'causation'
            elif 'reaffirmed' in lower or 'pledged' in lower or 'proclaimed' in lower: feature = 'attribution'
            elif 'essential' in lower or 'greatest importance' in lower:
                if 'greatest importance' in lower: return 'OPEN', 'exposition', {'open': ['greatest_importance']}, None, ['greatest_importance']
                feature = 'modality_belief'
            else: feature = 'other_preamble_dependency'
            return 'UNFORMALISED', ['unformalised', feature], {'unformalised': feature}, feature, names
        if lower.startswith('proclaims'):
            return 'UNFORMALISED', ['attributed','general_assembly','says','norm'], {'unformalised':'norms'}, 'norms', names
        feature = 'attribution' if 'proclaimed' in lower else 'other_preamble_dependency'
        return 'UNFORMALISED', ['unformalised',feature], {'unformalised':feature}, feature, names
    if ('may not be invoked' in lower or 'may be compelled' in lower
            or 'may in no case' in lower or 'may be interpreted' in lower
            or 'should act' in lower):
        return 'READINGS', 'norm', {'contextual': 'modal_scope_readings'}, None, names
    if stripped.startswith('All are equal before the law'):
        return 'OPEN', 'exposition', {'open':['equal_before_law']}, None, ['equal_before_law']
    if 'natural and fundamental group unit' in lower and 'is entitled' not in lower:
        return 'OPEN', 'exposition', {'open':['natural_group_unit']}, None, ['natural_group_unit']
    if 'born free' in lower: feature='time'
    elif 'endowed with reason' in lower: feature='other_metaphorical_endowment'
    elif re.search(r'\b(right|rights|entitled|shall|should|duties|may|compulsory|freedom)\b',lower) or lower.startswith('no one'):
        feature='norms'
    else: feature='other_legal_force'
    return 'UNFORMALISED', 'norm' if feature == 'norms' else ['unformalised',feature], {'unformalised':feature}, feature, names

# The source's legal equality is left open: this version's writable English
# vocabulary does not admit its wording as a checked predicate template.
units = []
analysis = []
reading_sets = []
for i, seg in enumerate(segments,1):
    piece = text[seg['start']:seg['end']]
    status, kind, meaning, missing, names = classify(piece,seg['article'],seg['heading'])
    uid = f'u{i:03d}'
    lo = len(text[:seg['start']].encode()); hi = len(text[:seg['end']].encode())
    unit = {'id':uid,'span':[lo,hi],'kind':kind,'meaning':meaning,'support':'none'}
    units.append(unit)
    entry = {'id':uid,'article':seg['article'],'span':[lo,hi],'status':status,
             'source':piece.strip()}
    if missing:
        entry['missing_feature'] = (missing.replace('_','/',1) if missing.startswith('modality_')
                                    else 'other:'+missing[6:] if missing.startswith('other_') else missing)
    if names:entry['open_terms']=names
    analysis.append(entry)
    if status == 'READINGS':
        # Both readings remain open. The schema needs model references even when
        # neither normative candidate has a formula; these refs do not decide them.
        rid=f'rs_{uid}'
        entry['reading_set']=rid
        should = 'should act' in piece.lower()
        entry['unresolved_features'] = ['norms','defaults'] if should else ['norms','modality/belief']
        first_id, second_id = ('strict','default') if should else ('permission','possibility')
        first_why = ('Should may state a strict obligation.' if should else
                     'May can deny legal permission in this legal context.')
        second_why = ('Should may state a defeasible recommendation or default.' if should else
                      'May can express possibility or ability; the text alone does not formally eliminate this scope.')
        reading_sets.append({'id':rid,'unit':uid,'version':1,'status':'open','readings':[
            {'id':first_id,'kind':'norm','meaning_id':f'{rid}.{first_id}','content':None,
             'admission':{'who':'translator','why':first_why+' No semantic separating model is available.',
                          'distinguishing_models':{second_id:'MODEL_ID'}}},
            {'id':second_id,'kind':['hedged','generally','norm'] if should else ['hedged','could','asserted'],
             'meaning_id':f'{rid}.{second_id}','content':None,
             'admission':{'who':'translator','why':second_why+' No semantic separating model is available.',
                          'distinguishing_models':{first_id:'MODEL_ID'}}}],
             'models':{'MODEL_ID':'MODEL_DATA'}})

# Real finite-model identity for the schema. It cannot separate non-formula readings.
from ve.environment import Environment
from ve.model import FiniteModel
model_data={'complete':True,'domains':{'person':['p']},'constants':{},'relations':{}}
model_id=FiniteModel.from_dict(Environment(ENV),model_data).model_id
for rs in reading_sets:
    rs['models']={model_id:model_data}
    for r in rs['readings']:
        r['admission']['distinguishing_models']={k:model_id for k in r['admission']['distinguishing_models']}

front={'format':'ve-document@1','environment':ENV,'units':units,'open_terms':open_terms,
       'reading_sets':reading_sets}
body=b'---\n'+json.dumps(front,ensure_ascii=False,sort_keys=True,indent=2).encode()+b'\n---\n'+raw
(ROOT/'translation.ve.md').write_bytes(body)
(ROOT/'units.json').write_text(json.dumps({'source_sha256':PIN,'units':analysis,
    'note':'A status describes the full source clause. OPEN formulas are checked fragments with undecided legal predicates; normative force is never treated as an assertion.'},ensure_ascii=False,indent=2)+'\n')
print(len(units),len(reading_sets),len(raw),model_id)
