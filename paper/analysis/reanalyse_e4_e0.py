#!/usr/bin/env python3
"""POST HOC E4 lenient results/reply inspection and E0 dispute ledger. No calls."""
import argparse, hashlib, json, random, re, unicodedata
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
from math import sqrt
from e4_sensitivity import verdict, read_rows, T975_11
PAPER=Path(__file__).resolve().parents[1];OUT=PAPER/'generated'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers),*['| '+' | '.join(map(str,r))+' |' for r in rows]])+'\n'
def ascii_text(s):
    for a,b in {'\u2014':' -- ','\u2013':'-','\u2019':"'",'\u2018':"'",'\u201c':'"','\u201d':'"','\u2265':'>=','\u2264':'<=','\u03ba':'kappa'}.items():s=s.replace(a,b)
    return unicodedata.normalize('NFKD',s).encode('ascii','replace').decode().replace('|',' / ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--outputs',type=Path,default=Path('/Users/seyran/code/manage-agents/colab/results/e4-scored-a/out'));p.add_argument('--labels',type=Path,default=Path('/Users/seyran/code/ve-codex/experiments/E2E4/colab/out/scored/E4/labels.jsonl'));p.add_argument('--prompts',type=Path,default=Path('/Users/seyran/code/manage-agents/colab/jobs/e4-scored-a/prompts.jsonl'));a=p.parse_args()
 labels=read_rows(a.labels);prompts=read_rows(a.prompts);assert labels.keys()==prompts.keys();assert all(r['prompts_sha256']==hashlib.sha256(a.prompts.read_bytes()).hexdigest() for r in labels.values());rows=[];contrasts=[];hashes=[a.labels,a.prompts];samples=[];frozen=[]
 for path in sorted(a.outputs.glob('*/outputs.jsonl')):
  hashes.extend([path,path.parent/'manifest.json']);outputs=read_rows(path);assert outputs.keys()==labels.keys();judge='14B' if '14B' in str(path) else '7B';scores={}
  for k,out in outputs.items():
   assert out.get('ok') is not False and not out.get('error') and not out.get('tool_events')
   v=verdict(out['text'],True);assert v is not None;scores[k]=int(v=='approve')
  for arm in ['prose_critique','checked_countermodel','dishonest_critic']:
   ks=[k for k,r in labels.items() if r['cell']==arm];counts=[]
   for lab in ['bad','good']:
    kk=[k for k in ks if labels[k]['label']==lab];assert len(kk)==60;counts.append(f'{sum(scores[k] for k in kk)}/60')
   failures=sum(verdict(outputs[k]['text']) is None for k in ks)
   rows.append([judge,arm.replace('_',' '),*counts,f'{failures}/120','0/120'])
  for lab in ['bad','good']:
   d=defaultdict(list)
   for k,r in labels.items():
    if r['cell']=='checked_countermodel' and r['label']==lab:
     other=f"{r['item_id']}|prose_critique|{r['instruction']}";d[r['template']].append(scores[k]-scores[other])
   ds=list(map(mean,d.values()));h=T975_11*stdev(ds)/sqrt(12)
   contrasts.append([judge,'FA' if lab=='bad' else 'HA',f'{mean(ds):+.3f}',f'[{mean(ds)-h:+.3f}, {mean(ds)+h:+.3f}]'])
  strict={k:(int(labels[k]['label']=='bad') if verdict(o['text']) is None else int(verdict(o['text'])=='approve')) for k,o in outputs.items()}
  fs={}
  for lab in ['bad','good']:
   ds=defaultdict(list)
   for k,r in labels.items():
    if r['cell']=='checked_countermodel' and r['label']==lab:
     other=f"{r['item_id']}|prose_critique|{r['instruction']}";ds[r['template']].append(strict[k]-strict[other])
   vals=list(map(mean,ds.values()));h=T975_11*stdev(vals)/sqrt(12);fs[lab]=(mean(vals),mean(vals)-h,mean(vals)+h)
  m,lo,hi=fs['bad'];decision='supports protection (pilot)' if hi<0 and fs['good'][1]>=-.05 else 'FA floor; no protection identified'
  frozen.append([f'E4 {judge}',f'{m:+.3f}',f'[{lo:+.3f}, {hi:+.3f}] (95%)',decision,f'HA {fs["good"][0]:+.3f} [{fs["good"][1]:+.3f}, {fs["good"][2]:+.3f}]'])
  if judge=='7B':
   pool=sorted(k for k,r in labels.items() if r['cell']=='prose_critique');chosen=random.Random(20260921).sample(pool,10)
   for k in chosen:
    messages=prompts[k]['messages'];text=messages[-1]['content'];final=text.splitlines()[-1]
    samples.append({'key':k,'label':labels[k]['label'],'prompt_final_question':final,'task_opening':text.splitlines()[0],'reply':outputs[k]['text'],'messages':messages})
   assert all(o['n_output_tokens']==7 for o in outputs.values())
 (OUT/'preregistered-decisions.md').write_text((OUT/'preregistered-e1.md').read_text().replace('97.5% cluster-t interval','Cluster-t interval (E1 97.5%)') + '\n'.join('| '+' | '.join(r)+' |' for r in frozen)+'\n')
 (OUT/'posthoc-e4-primary.md').write_text('POST HOC lenient parsing (presented analysis); original protocol failures kept separately.\n\n'+table(['Judge','Arm','FA','HA','Protocol failures','Unrecovered'],rows))
 (OUT/'posthoc-e4-contrasts.md').write_text('POST HOC checked minus prose; equal-weight template means and descriptive 95% cluster-t intervals.\n\n'+table(['Judge','Endpoint','Difference','95% interval'],contrasts))
 (OUT/'posthoc-e4-replies.json').write_text(json.dumps(samples,indent=2)+'\n')
 text=['POST HOC inspection. Simple random sample of 10 of the 120 7B prose replies,', 'seed 20260921, sampling sorted assignment keys without replacement.', 'Full messages and exact replies are in `posthoc-e4-replies.json`.', 'The final prompt instruction (there is no separate final interrogative) and raw reply follow.', '']
 for i,s in enumerate(samples,1):
  text += [f'**{i}. `{s["key"]}`; oracle label: {s["label"]}.**','', 'Task opening:', '', '> '+s['task_opening'], '', 'Final prompt instruction:', '', '> '+s['prompt_final_question'],'','Raw reply:','','```json',s['reply'],'```','']
 (OUT/'posthoc-e4-replies.md').write_text('\n'.join(text))
 # The frozen source already records each item and both raters; post hoc presentation only.
 source=PAPER/'sources/e0-second-rater.md';hashes.append(source);raw=source.read_text().split('## Every disagreement\n',1)[1];ledgers=[];summary=[]
 for section in re.split(r'\n(?=### )',raw.strip()):
  match=re.match(r'### (.+?) \((\d+)\)',section);assert match;dataset,n=match.groups();entries=[]
  for item,body in re.findall(r'\*\*`([^`]+)`\*\*\n(.*?)(?=\n\*\*`|\Z)',section,re.S):
   first=re.search(r'- First: \*\*(\w+)\*\*',body).group(1);second=re.search(r'- Second: \*\*(\w+)\*\*',body).group(1);proposed=re.search(r'- Proposed: \*\*(\w+)\*\* (.*)',body).groups();entries.append([ascii_text(item).replace('_','\\_'),first+' / '+second,proposed[0],ascii_text(proposed[1]).lstrip(' -')])
  assert len(entries)==int(n),(dataset,len(entries),n)
  ledgers += [f'## {dataset}: disputed items (post hoc presentation)','',table(['Item','First / second','Proposed','Adapter assumption or omitted meaning'],entries),'']
  summary.append([dataset,n])
 (OUT/'posthoc-e0-disputes.md').write_text('POST HOC presentation of all frozen inter-rater disagreements. Proposed labels are adjudication suggestions, not new frozen ratings. Item paths identify the original dataset records.\n\n'+'\n'.join(ledgers))
 (OUT/'posthoc-e4-e0-provenance.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in hashes},indent=2)+'\n')
 print(table(['Dataset','Disputed items'],summary));print(table(['Judge','Arm','FA','HA','Protocol failures','Unrecovered'],rows));print('\n'.join(s['reply'] for s in samples));print(samples[0]['prompt_final_question'])
if __name__=='__main__':main()
