"""Revision 7: constrained rewrites, masked distance and localization shortcuts."""
from copy import deepcopy
import random
import re
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


def test_v7_masking_measures_surrounding_prose_and_threshold():
    from experiments.p5_semantics import mask_claims, MIN_DISTANCE
    assert MIN_DISTANCE == .20
    assert mask_claims('unit1 is ready and unit22 is pre-approved.') == '# and #.'
    assert mask_claims('unit1 is ready.') == mask_claims('unit999 is active.')
    d = read(HERE/'materials/dossiers.jsonl.gz')[0]
    source = {n['id']: n['text'] for n in d['nodes']}
    all_rewritten = rewritten(d)
    outcomes = []
    for count in range(len(d['nodes']) + 1):
        texts = dict(source)
        texts.update({n['id']: all_rewritten[n['id']] for n in d['nodes'][:count]})
        result = acceptance_check(d, texts)
        expected = edit_distance(mask_claims('\n\n'.join(source.values())),
                                 mask_claims('\n\n'.join(texts.values())))
        assert result['normalized_levenshtein'] == expected
        assert result['passed'] == (expected >= .20)
        outcomes.append(result['passed'])
    assert not outcomes[0] and outcomes[-1]


def test_v7_discourse_frames_preserve_every_kind_and_localization():
    from experiments.p5_semantics import parts
    for d in read(HERE/'materials/dossiers.jsonl.gz'):
        texts = {}
        for index, n in enumerate(d['nodes']):
            ant, con, tail, _ = inference_parts(n['text'])
            variants = [f'From the fact that {ant}, it follows that {con}.',
                        f'{con} is inferred from the fact that {ant}.',
                        f'These facts are taken together: {ant.replace(" and ", ". Also, ")}. Therefore, {con}.']
            text = variants[index % len(variants)]
            if tail:
                checks, outcomes = re.split(r' would (?:yield|imply|establish) that ', tail.removeprefix('The checks that ').removesuffix(', respectively.'))
                text = f'If {checks}, then {outcomes} would follow, respectively. ' + text
            texts[n['id']] = text
            assert parts(text)[1] == con
        result = acceptance_check(d, texts)
        assert result['passed'], result
        assert result['source'] == result['paraphrase']


def test_v7_conditional_reframing_cannot_assert_or_repair_alternatives():
    d = read(HERE/'materials/dossiers.jsonl.gz')[0]
    texts = rewritten(d)
    node = next(n for n in d['nodes'] if 'The checks that ' in n['text'])
    key = node['id']
    original = texts[key]
    head, tail = original.split(' The checks that ')
    checks, outcomes = re.split(r' would (?:yield|imply|establish) that ', tail.removesuffix(', respectively.'))
    reordered = ' and '.join(reversed(outcomes.split(' and ')))
    bad = [f'{head} If {checks}, then {reordered} would follow, respectively.',
           original.replace(' would ', ' do '),
           f'{head} If not {checks}, then {outcomes} would follow, respectively.']
    for candidate in bad:
        assert not acceptance_check(d, {**texts, key: candidate})['passed']


def test_v7_rejects_synonyms_units_lost_duplicates_order_ids_and_glosses():
    d = read(HERE/'materials/dossiers.jsonl.gz')[0]
    texts = rewritten(d)
    key = d['nodes'][0]['id']
    from experiments.p5_semantics import CLAIM
    atom = CLAIM.search(texts[key])[0]
    for bad in [texts[key].replace(atom, atom + '-synonym', 1),
                texts[key].replace(atom, atom.replace('unit', 'unit99'), 1),
                texts[key] + ' n03.', texts[key] + ' (some gloss).']:
        assert not acceptance_check(d, {**texts, key: bad})['passed']
    assert not acceptance_check(d, {k: v for k, v in texts.items() if k != key})['passed']
    keys = list(texts)
    swapped = {**texts, keys[0]: texts[keys[1]], keys[1]: texts[keys[0]]}
    assert not acceptance_check(d, swapped)['passed']
    for n in d['nodes']:
        ant, con, tail, _ = inference_parts(n['text'])
        if ' and ' in ant and len(set(ant.split(' and '))) < len(ant.split(' and ')):
            changed = f'From the fact that {ant.split(" and ")[0]}, it follows that {con}.'
            assert not acceptance_check(d, {**texts, n['id']: changed})['passed']
            break
    else:
        pytest.fail('fixture requires a repeated premise')


def test_v7_prompt_and_ledger_isolate_failed_v6_rebuy(tmp_path, monkeypatch):
    from experiments import p5_revision as r
    from ve_experiments.paid import Ledger
    monkeypatch.setattr(r, 'HERE', tmp_path)
    old = Ledger(tmp_path/'runs/revision-v6/paraphrase-costs.jsonl', '.40')
    old.allowance('retained-v6-cost-fixture', '.16')
    evidence = old.path.read_bytes()
    book = r.revision_ledger('paraphrase', '.40')
    assert book.path == tmp_path/'runs/revision-v7/paraphrase-costs.jsonl'
    assert r.revision_ledger('paraphrase', '.40').path == book.path
    assert old.path.read_bytes() == evidence
    envelopes = read(tmp_path/'runs/study/costs.jsonl')
    assert len(envelopes) == 1 and envelopes[0]['identity'] == 'v7-paraphrase-envelope'
    d = read(HERE/'materials/dossiers.jsonl.gz')[0]
    req = p5.request({'id': d['id'], 'split': 'materials', 'payload': d}, 'shared', 'paraphrase')
    assert req.identity.startswith('rewrite-v7/')
    prompt = req.messages[0]['content']
    assert 'CONSTRAINED' in prompt and 'verbatim' in prompt
    assert '0.20' in prompt and 'single character #' in prompt
