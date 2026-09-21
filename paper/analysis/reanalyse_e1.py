#!/usr/bin/env python3
"""POST HOC offline reanalysis. See README.md for estimands and assumptions."""
import hashlib, itertools, json, os
from collections import Counter, defaultdict
from pathlib import Path
from statistics import NormalDist
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
from scipy.stats import t
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt']='ve-posthoc-20260921'
import matplotlib.pyplot as plt

PAPER=Path(__file__).resolve().parents[1]; ROOT=PAPER.parent; OUT=PAPER/'generated'
VIEWS=['fol_symbols','fol_keywords','ve_strict','ve_natural','ve_fluent']
SHORT=dict(zip(VIEWS,['S','K','V','N','F']))
PATHS=[ROOT/'experiments/E1/runs/e1-scored-0921/trials.jsonl',ROOT/'experiments/E1/runs/e1-scored-0921-e1b/trials.jsonl',ROOT/'experiments/E1/items/scored.jsonl']
def read(p): return [json.loads(l) for l in p.read_text().splitlines()]
def table(head,rows): return '\n'.join(['| '+' | '.join(head)+' |','|'+'---|'*len(head),*['| '+' | '.join(map(str,r))+' |' for r in rows]])+'\n'
def write(name,head,rows): (OUT/name).write_text('POST HOC analysis; not preregistered.\n\n'+table(head,rows))
def interval_text(x): return f'[{x[0]:+.3f}, {x[1]:+.3f}]'
def signs(n): return np.array(list(itertools.product([-1.,1.],repeat=n)))
def pvalue(d,delta=0):
    d=np.asarray(d)-delta
    return float(np.mean(np.abs(signs(len(d))@d/len(d))>=abs(np.mean(d))-1e-12))
def inversion(d,alpha=.05,bounds=(-1,1)):
    # Exhaustive flips; invert constant-location tests on a fixed 0.0005 grid.
    # Hull of acceptance set, expanded one grid step, including boundary nulls.
    grid=np.linspace(*bounds,round((bounds[1]-bounds[0])/.0005)+1)
    d=np.asarray(d); base=signs(len(d))@d/len(d); slope=signs(len(d)).mean(axis=1)
    ps=[]
    for g in np.array_split(grid,40):
        ps.extend(np.mean(np.abs(base[:,None]-slope[:,None]*g)>=np.abs(d.mean()-g)-1e-12,axis=0))
    accepted=grid[np.array(ps)>alpha]
    assert len(accepted)
    return [max(bounds[0],float(accepted[0]-.0005)),min(bounds[1],float(accepted[-1]+.0005))]
def per_template(rs):
    a=defaultdict(list)
    for r in rs: a[r['template']].append(r['score'])
    assert set(a)<=set(TEMPLATES) and len(a)>1
    return np.array([np.mean(a[k]) for k in sorted(a)])
rows=read(PATHS[0]); items={r['id']:r for r in read(PATHS[2])}; b=read(PATHS[1])
assert len(items)==874 and len(rows)==17480 and len(b)==8740
assert len({(r['judge'],r['item_id'],r['condition']) for r in rows})==len(rows)
for r in rows:
    assert r['template']==items[r['item_id']]['template'] and r['group']==items[r['item_id']]['group']
    r['view'],r['explanation']=r['condition'].split('|');r['judge_short']='32B' if '32B' in r['judge'] else '14B'
    r['score']=int(r['label']=='bad') if r['approved'] is None else int(r['approved'])
    r['weakening']=items[r['item_id']].get('direction')=='weaker'
assert not any(r['approved'] is None for r in rows)
TEMPLATES=sorted({r['template'] for r in rows}); assert len(TEMPLATES)==12
# direction is the oracle relation, not the attack family. Generator calls compare(faithful, candidate).
assert all(r['label']=='bad' and r['oracle']=='VALID' for r in items.values() if r.get('direction')=='weaker')
def cell(j,v,e,label='bad',weak=False): return [r for r in rows if r['judge_short']==j and r['view']==v and r['explanation']==e and r['label']==label and (not weak or r['weakening'])]
metrics=[]; contrasts=[]; weakrates=[]; weakcontrasts=[]; sensitivity=[]; prereg=[]; results={}
for j in ['14B','32B']:
 for e in ['none','attacker']:
  for v in VIEWS:
    bad=cell(j,v,e);good=cell(j,v,e,'good');fa=np.mean([r['score'] for r in bad]);ha=np.mean([r['score'] for r in good]);
    zf=NormalDist().inv_cdf((sum(r['score'] for r in bad)+.5)/(len(bad)+1));zh=NormalDist().inv_cdf((sum(r['score'] for r in good)+.5)/(len(good)+1))
    metrics.append([j,SHORT[v],e,f'{sum(r["score"] for r in bad)}/{len(bad)}',f'{sum(r["score"] for r in good)}/{len(good)}',f'{(ha+1-fa)/2:.3f}',f'{zh-zf:.3f}',f'{-(zh+zf)/2:.3f}'])
    wr=cell(j,v,e,weak=True);d=per_template(wr);ci=inversion(d,bounds=(0,1))
    weakrates.append([j,SHORT[v],e,f'{sum(r["score"] for r in wr)}/{len(wr)}',f'{np.mean([r["score"] for r in wr]):.3f}',f'{d.mean():.3f}',interval_text(ci)])
  for v in ['ve_strict','ve_fluent']:
    a=cell(j,v,e);s=cell(j,'fol_symbols',e)
    assert {r['item_id'] for r in a}=={r['item_id'] for r in s}
    d=per_template(a)-per_template(s);alpha=.025 if j=='32B' and v=='ve_strict' else .05
    ci=inversion(d,alpha);p=pvalue(d);loo=[np.delete(d,i).mean() for i in range(12)]
    key=f'{j}/{v}/{e}';results[key]={'mean':float(d.mean()),'p_two_sided':p,'interval':ci,'level':1-alpha,'loto':[min(loo),max(loo)],'per_template':dict(zip(TEMPLATES,map(float,d)))}
    contrasts.append([j,SHORT[v]+' - S',e,f'{d.mean():+.3f}',f'{p:.6f}',interval_text(ci),interval_text([min(loo),max(loo)])])
    if j=='32B' and v=='ve_strict':
      tc=t.ppf(1-alpha/2,11)*d.std(ddof=1)/np.sqrt(12);tci=[d.mean()-tc,d.mean()+tc]
      hd=per_template(cell(j,v,e,'good'))-per_template(cell(j,'fol_symbols',e,'good'));hh=t.ppf(.9875,11)*hd.std(ddof=1)/np.sqrt(12)
      holds=hd.mean()-hh>=-.10 and hd.mean()>=-.05 and np.mean([r['score'] for r in cell(j,v,e,'good')])>=.70
      def decision(ci,threshold):
        if ci[0]>0: return 'refuted (harmful)'
        if ci[1]<=-threshold and holds: return 'supported'
        if ci[0]>-threshold: return 'refuted'
        return 'inconclusive'
      prereg.append(['E1 P1' if e=='attacker' else 'E1 P2',f'{d.mean():+.3f}',interval_text(tci),decision(tci,.05),'holds'])
      for method,bounds in [('frozen t interval',tci),('post hoc sign flip',ci)]:
       sensitivity.append(['P1' if e=='attacker' else 'P2',method,*[decision(bounds,h) for h in [.03,.05,.08]]])
    wa=cell(j,v,e,weak=True);ws=cell(j,'fol_symbols',e,weak=True);wd=per_template(wa)-per_template(ws);wci=inversion(wd)
    weakcontrasts.append([j,SHORT[v]+' - S',e,f'{wd.mean():+.3f}',interval_text(wci),f'{pvalue(wd):.6f}'])
    results['weakening/'+key]={'mean':float(wd.mean()),'p_two_sided':pvalue(wd),'interval':wci,'pooled_a':float(np.mean([r['score'] for r in wa])),'pooled_s':float(np.mean([r['score'] for r in ws])),'n':len(wa)}
write('posthoc-e1-metrics.md',['Judge','View','Explanation','FA','HA','Balanced accuracy',"d-prime",'c'],metrics)
write('posthoc-e1-contrasts.md',['Judge','Contrast','Explanation','Template mean','Two-sided p','Inverted interval','Leave-one-out range'],contrasts)
write('posthoc-weakening-rates.md',['Judge','View','Explanation','Approved / weakening','Pooled FA','Template FA','95% interval'],weakrates)
write('posthoc-weakening-contrasts.md',['Judge','Contrast','Explanation','Template difference','95% interval','Two-sided p'],weakcontrasts)
write('posthoc-thresholds.md',['Contrast','Interval method','0.03','0.05','0.08'],sensitivity)
(OUT/'preregistered-e1.md').write_text(table(['Frozen contrast','FA difference','97.5% cluster-t interval','Original decision','HA constraint'],sorted(prereg)))
# Binomial GLM with working independence; sandwich clustered on all 12 templates.
# Base items are nested in template, so clustering at template permits their dependence.
modelrows=[];modelinfo={}
for label in ['bad','good']:
 rr=[r for r in rows if r['label']==label]; names=['Intercept',*[v for v in VIEWS[1:]],'explanation=attacker','judge=32B',*[v+':32B' for v in VIEWS[1:]]]
 X=np.array([[1,*[int(r['view']==v) for v in VIEWS[1:]],int(r['explanation']=='attacker'),int(r['judge_short']=='32B'),*[int(r['view']==v and r['judge_short']=='32B') for v in VIEWS[1:]]] for r in rr],float);y=np.array([r['score'] for r in rr])
 def fun(beta):
    eta=X@beta;p=expit(eta)
    return np.sum(np.logaddexp(0,eta)-y*eta),X.T@(p-y)
 fit=minimize(fun,np.zeros(X.shape[1]),jac=True,method='BFGS',options={'gtol':1e-7,'maxiter':2000})
 beta=fit.x;p=expit(X@beta);grad=np.max(np.abs(fun(beta)[1]));assert grad<1e-4
 bread=np.linalg.inv(X.T@((p*(1-p))[:,None]*X));scores=X*(y-p)[:,None]
 cluster=np.array([scores[np.array([r['template']==k for r in rr])].sum(axis=0) for k in TEMPLATES]);cov=bread@(cluster.T@cluster)@bread*12/11*(len(rr)-1)/(len(rr)-X.shape[1]);se=np.sqrt(np.diag(cov));crit=t.ppf(.975,11)
 for name,coef,s in zip(names,beta,se): modelrows.append([label,name,f'{coef:+.3f}',f'{s:.3f}',interval_text([coef-crit*s,coef+crit*s]),('<.0001' if 2*t.sf(abs(coef/s),11)<.0001 else f'{2*t.sf(abs(coef/s),11):.4f}')])
 modelinfo[label]={'n':len(rr),'max_abs_score':float(grad),'optimizer_message':str(fit.message),'coefficients':dict(zip(names,map(float,beta)))}
write('posthoc-logistic.md',['Label stratum','Term','Log odds','Cluster SE','95% t(11) interval','p (exploratory)'],modelrows)
# Paired E1b control directly from trial truth scores.
e1b=[]
for j in ['14B','32B']:
 for v in VIEWS:
  rr=[r for r in b if j in r['judge'] and r['condition']==v];g=defaultdict(list)
  for r in rr:g[r['template']].append(r['correct_of_2']/2)
  e1b.append([j,SHORT[v],f'{sum(r["correct_of_2"] for r in rr)}/{2*len(rr)}',f'{np.mean([np.mean(x) for x in g.values()]):.3f}',sum(r['answer'] is None for r in rr)])
write('posthoc-e1b.md',['Judge','View','Correct / assigned truth questions','Template accuracy','Failed replies'],e1b)
fig,axes=plt.subplots(2,2,figsize=(9,6),sharex=True,sharey=True)
for row,j in enumerate(['14B','32B']):
 for col,e in enumerate(['none','attacker']):
  ax=axes[row,col]
  for v,offset,color in [('ve_strict',-.13,'#2466a3'),('ve_fluent',.13,'#b24723')]:
   vals=results[f'{j}/{v}/{e}']['per_template'];ax.scatter(list(vals.values()),np.arange(12)+offset,label=SHORT[v]+' - S',s=20,color=color)
  ax.axvline(0,color='gray',lw=.7);ax.set_title(j+', '+e);ax.set_yticks(range(12),[k.split('_')[0] for k in TEMPLATES]);ax.grid(axis='x',alpha=.2)
axes[0,0].legend(fontsize=8);fig.supxlabel('POST HOC: paired false-approval difference within each template');fig.tight_layout();fig.savefig(OUT/'posthoc-template-differences.pdf',metadata={'CreationDate':None,'ModDate':None});fig.savefig(OUT/'posthoc-template-differences.svg',metadata={'Date':None});plt.close(fig)
results['model']=modelinfo;results['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in PATHS};results['weakening_candidates']=sum(r.get('direction')=='weaker' for r in items.values());results['weakening_template_counts']=dict(Counter(r['template'] for r in items.values() if r.get('direction')=='weaker'))
(OUT/'posthoc-e1.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({k:v for k,v in results.items() if k.startswith('32B') or k.startswith('weakening/32B') or k.startswith('14B/ve_fluent')},indent=2))
