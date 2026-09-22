"""Revision 6: regressions for substantive rewrites and localization shortcuts."""
from copy import deepcopy
import random
import pytest
from experiments import p5, p5_review
from experiments.p5_materials import HERE, read
from experiments.p5_paraphrase import inference_parts
from experiments.p5_semantics import acceptance_check, edit_distance, licensing
from experiments.p5_leakage import localization_probe


def rewritten(dossier):
    texts={}
    for index,n in enumerate(dossier['nodes']):
        ant,con,tail,_=inference_parts(n['text'])
        if index % 2:
            text=f'Our reasoning rests on the following premises: {ant}. Therefore, {con}.'
        else:
            text=f'We take as our starting points the following information: {ant}; hence {con}.'
        texts[n['id']]=text+(' '+tail if tail else '')
    return texts


def source_items():
    labels = {r['id']: r for r in p5.labels(False)}
    return [{'id': d['id'], 'group': labels[d['id']]['family'],
             'split': labels[d['id']]['split'], 'payload': d}
            for d in read(HERE/'materials/dossiers.jsonl.gz')]


def test_distance_matches_dynamic_programming():
    rng=random.Random(19)
    for _ in range(100):
        a=''.join(rng.choices('abc',k=rng.randrange(20)))
        b=''.join(rng.choices('abc',k=rng.randrange(20)))
        row=list(range(len(b)+1))
        for i,x in enumerate(a,1):
            new=[i]
            for j,y in enumerate(b,1):
                new.append(min(new[-1]+1,row[j]+1,row[j-1]+(x!=y)))
            row=new
        assert edit_distance(a,b)==row[-1]/max(1,len(a),len(b))


def test_all_source_kinds_and_localizations_recoverable_and_genuine_rewrites():
    labels={r['id']:r for r in read(HERE/'labels.jsonl.gz')}
    for d in read(HERE/'materials/dossiers.jsonl.gz'):
        result=acceptance_check(d,rewritten(d))
        assert result['passed'],result
        kind,locations=result['paraphrase']['diagnoses'][0]
        assert kind==labels[d['id']]['kind']
        if kind!='benign':
            assert set(locations)==set(labels[d['id']]['acceptable_locations'][1])
        assert not acceptance_check(d,{n['id']:n['text'] for n in d['nodes']})['passed']


def test_repairs_new_flaws_and_unparsed_assertions_rejected():
    d=read(HERE/'materials/dossiers.jsonl.gz')[0]
    texts=rewritten(d)
    key=d['nodes'][0]['id']
    for bad in [texts[key].replace('unit','unit99',1),
                texts[key].replace('hence','nevertheless'),
                texts[key].replace('information:','information: not'),
                texts[key]+' This step is questionable.']:
        changed={**texts,key:bad}
        assert not acceptance_check(d,changed)['passed']


def test_localization_detects_original_shortcut_and_accepts_independent_tails():
    labels={r['id']:r for r in read(HERE/'labels.jsonl.gz')}
    items=source_items()
    assert localization_probe(items,labels)['passed']
    leaky=deepcopy(items)
    for item in leaky:
        q=item['payload']; paragraphs=q['argument'].split('\n\n')
        source=next(i for i,t in enumerate(paragraphs) if ' The checks that ' in t)
        head,tail=paragraphs[source].split(' The checks that ',1)
        paragraphs[source]=head
        producer=labels[item['id']]['acceptable_locations'][1][0]
        target=next(i for i,n in enumerate(q['nodes']) if n['id']==producer)
        paragraphs[target]+=' The checks that '+tail
        q['argument']='\n\n'.join(paragraphs)
    result=localization_probe(leaky,labels)
    assert not result['passed'] and result['correct']==56


def test_model_family_aliases_not_independent():
    assert p5_review.model_family('Claude Opus 5')==p5_review.model_family('Anthropic')
    assert p5_review.model_family('Gemini 3.1 Pro')!=p5_review.model_family('Claude')
    assert p5_review.model_family('made-up') is None


def test_review_refuses_drafts_before_spending(monkeypatch):
    from experiments import p5_revision as r
    monkeypatch.setattr(r,'independent_prose',lambda:{'passed':False})
    monkeypatch.setattr(r,'revision_ledger',lambda *a,**k:pytest.fail('must not reserve'))
    with pytest.raises(p5.PreflightError,match='84 regenerated'):
        r.gemini_review('1')


def test_revision_cap_and_missing_key_before_spending(tmp_path,monkeypatch):
    from experiments import p5_revision as r
    monkeypatch.setattr(r,'HERE',tmp_path)
    for stage,cap in [('paraphrase','.41'),('gemini-review','1.01')]:
        with pytest.raises(p5.PreflightError,match='positive cap'):
            r.revision_ledger(stage,cap)
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    with pytest.raises(p5.PreflightError,match='orchestrator'):
        p5.paraphrase('.40',revision=True)


def test_two_model_families_open_review_gate_but_aliases_do_not(tmp_path,monkeypatch):
    from experiments.p5_materials import archive
    from ve_experiments.paid import digest
    import experiments.p5_leakage
    monkeypatch.setattr(experiments.p5_leakage,'audit',lambda base:{'passed':True})
    items=source_items(); labels=p5.labels(False)
    for split in ('dev','scored'):
        archive(tmp_path/f'materials/{split}.jsonl.gz',[r for r in items if r['split']==split])
    archive(tmp_path/'labels.jsonl.gz',labels)
    by_id={r['id']:r for r in labels}
    rows=[]
    for item in items:
        for reviewer,family in [('a','Anthropic Claude'),('b','Google Gemini')]:
            rows.append({'event':'review','item_id':item['id'],'reviewer_id':reviewer,
                         'reviewer_kind':'model','model_family':family,
                         'packet_sha256':digest(item['payload']),
                         'checks':{k:True for k in p5_review.CHECKS},
                         'annotation':{'kind':by_id[item['id']]['kind']}})
    archive(tmp_path/'materials/review-ledger.jsonl.gz',rows)
    assert p5_review.gate(tmp_path)['passed']
    for row in rows:
        row['model_family']='Claude Opus'
    archive(tmp_path/'materials/review-ledger.jsonl.gz',rows)
    assert not p5_review.gate(tmp_path)['passed']
    for row in rows:
        row['model_family']='Google Gemini' if row['reviewer_id']=='b' else 'Claude'
        if row['reviewer_id']=='a':
            row['packet_sha256']='stale'
    archive(tmp_path/'materials/review-ledger.jsonl.gz',rows)
    assert not p5_review.gate(tmp_path)['passed']
