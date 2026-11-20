import json,glob,os,collections,datetime,calendar
root='/home/seyran/code/manage-agents/test-skip/nightly'
def ts(s): return calendar.timegm(datetime.datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ').timetuple())
jobs=[]
for l in open('/home/seyran/code/manage-agents/cloud2-runs.jsonl'):
    try: r=json.loads(l)
    except: continue
    if r.get('host')!='ve-cloud-2' or r.get('rc') in (86,3) : continue
    try: s=int(float(r['seconds']))
    except: continue
    if s<=60: continue
    e=ts(r['t']); jobs.append((r['kind'],r['label'],e-s,e))
def overlap(a,b,c,d): return max(0,min(b,d)-max(a,c))
rows=[]
for run in sorted(glob.glob(root+'/parts-2026111*')):
    tsv={}
    for l in open(run+'/parts.tsv'):
        f=l.split('\t'); tsv[f[0]]=(int(f[3]),int(f[4]))
    for p in glob.glob(run+'/part-*.json'):
        d=json.load(open(p)); k=p.split('-')[-1][:-5]
        if d.get('where')!='ve-cloud-2' or k not in tsv: continue
        a,b=tsv[k]; ms=d['mutants']
        to=sum('did not finish' in (m.get('detail') or '') for m in ms); jd=sum(m['status']!='NOT RUN' for m in ms)-to
        dur=b-a
        g=sum(overlap(a,b,x,y) for kd,lb,x,y in jobs if kd=='gate')/dur
        tm=sum(overlap(a,b,x,y) for kd,lb,x,y in jobs if kd=='tm')/dur   # includes itself
        sel=sum(overlap(a,b,x,y) for kd,lb,x,y in jobs if kd=='sel')/dur
        rows.append((os.path.basename(run)[6:],k,dur,jd,to,g,tm,sel))
print('run part dur judged TO TOratio gate_frac tm_conc sel_conc')
for r in rows: print(f"{r[0]} p{r[1]:>2} {r[2]:>5} {r[3]:>3} {r[4]:>3} {r[4]/max(1,r[3]+r[4]):.2f} g{r[5]:.2f} tm{r[6]:.1f} sel{r[7]:.1f}")
import statistics
def grp(f):
    b=collections.defaultdict(lambda:[0,0])
    for r in rows: b[f(r)][0]+=r[3]; b[f(r)][1]+=r[4]
    return {k:f"judged {v[0]} TO {v[1]} ratio {v[1]/max(1,v[0]+v[1]):.2f}" for k,v in sorted(b.items())}
print('by tm concurrency (rounded):',grp(lambda r: round(r[6])))
print('by gate overlap > 0.3:',grp(lambda r: r[5]>0.3))
print('by run date >= 11-16:',grp(lambda r: r[0]>='20261116'))
