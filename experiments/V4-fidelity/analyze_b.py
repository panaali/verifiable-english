"""Offline row-level AST audit. No model calls; frozen primary scores stay intact."""
from collections import Counter
import json
from pathlib import Path
import ve
from fidelity import HERE
from ve_experiments.llm import parse_final_json
from run_b import CATEGORIES, taxonomy


def main():
    items={i['id']:i for i in map(json.loads,(HERE/'items-b.jsonl').read_text().splitlines())}
    rows=[json.loads(x) for x in (HERE/'results/b/ledger.jsonl').read_text().splitlines()]
    stop_path=HERE/'results/b/STOP.json'
    excluded={tuple(k) for k in json.loads(stop_path.read_text())['post_stop_identities']} if stop_path.exists() else set()
    details=[]; counts=Counter({c:0 for c in CATEGORIES}); exact=total=0
    for row in rows:
        if row['status']!='ok' or (row['item_id'],row['sample_index']) in excluded: continue
        item=items[row['item_id']];env=ve.Environment.from_dict(item['environment'])
        expected={p['id']:p for p in item['premises']}
        expected['query']={'gold_ast':item['query']['gold_ast']}
        total+=len(expected)
        try:
            obj=parse_final_json(row['text']); ts=obj['translations']
            submitted={t['premise_id']:t for t in ts}
            if len(submitted)!=len(ts): raise ValueError('duplicate rows')
            submitted['query']={'ve':obj['query_ve']}
        except Exception as exc:
            details.append({'id':item['id'],'sample_index':row['sample_index'],'row':None,'categories':['other'],'error':str(exc)})
            counts['other']+=1;continue
        for pid,gold in expected.items():
            detail={'id':item['id'],'sample_index':row['sample_index'],'row':pid}
            try:
                t=submitted[pid]
                if pid!='query' and t['english']!=gold['english']:raise ValueError('English substituted')
                parsed=ve.parse(env,t['ve'].rstrip()+'\n').formulas
                if len(parsed)!=1:raise ValueError('Expected exactly one formula')
                ast=ve.formula_to_data(env,parsed[0])
                if ast==gold['gold_ast']:exact+=1;continue
                detail.update(categories=taxonomy(gold['gold_ast'],ast),gold_ast=gold['gold_ast'],submitted_ast=ast)
            except Exception as exc:detail.update(categories=['other'],error=str(exc))
            details.append(detail);counts.update(detail['categories'])
    result={'scope':'independent per-row audit of successful endpoint responses; no scientific-score mutation',
            'expected_translation_rows_in_successful_responses':total,'exact_translation_rows':exact,
            'taxonomy_multilabel':dict(counts),'failures':details}
    (HERE/'results/b/row-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='failures'},indent=2))

if __name__=='__main__':main()
