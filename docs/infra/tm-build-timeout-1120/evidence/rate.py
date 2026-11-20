import json,glob,os,collections,datetime
root='/home/seyran/code/manage-agents/test-skip/nightly'
rows=[]
for run in sorted(glob.glob(root+'/parts-2026111[6-9]*')):
    tsv={}
    for l in open(run+'/parts.tsv'):
        f=l.split('\t'); tsv[f[0]]=(int(f[3]),int(f[4]))
    for p in glob.glob(run+'/part-*.json'):
        d=json.load(open(p)); k=p.split('-')[-1][:-5]
        if not d.get('mutants') or k not in tsv: continue
        ms=d['mutants']; to=sum('did not finish' in (m.get('detail') or '') for m in ms)
        tlim=3600 if '1620Z' in run else 1800
        lk=d['steps']['lake']; rn=d['steps']['runs']
        judged=sum(m['status'] in ('KILLED','SURVIVOR','INVALID') or (m['status']=='UNKNOWN' and 'did not finish' not in (m.get('detail') or '')) for m in ms)
        okn=rn['mutant_checks']+rn['mutant_builds']-to; oks=lk['mutant_checks']+lk['mutant_builds']-to*tlim
        rows.append((os.path.basename(run)[6:],int(k),d.get('where','actions?'),d['jobs'],tsv[k][0],tsv[k][1],judged,to,rn['mutant_checks'],int(lk['mutant_checks']),rn['mutant_builds'],int(lk['mutant_builds']),oks/max(okn,1)))
# concurrency on the same host: overlapping nightly parts on ve-cloud-2
for r in sorted(rows,key=lambda r:r[4]):
    conc=sum(1 for o in rows if o is not r and o[2]==r[2] and o[4]<r[5] and o[5]>r[4])
    print(f"{r[0]} p{r[1]:>2} {r[2]:<10} j{r[3]} conc{conc} judged{r[6]:>3} TO{r[7]:>3} checkruns{r[8]:>3} {r[9]:>6}s buildruns{r[10]:>3} {r[11]:>5}s avg_nonTO_run {r[12]:.0f}s")
