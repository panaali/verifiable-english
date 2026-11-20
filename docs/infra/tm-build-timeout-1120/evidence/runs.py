import json,glob,os,collections
root='/home/seyran/code/manage-agents/test-skip/nightly'
for run in sorted(glob.glob(root+'/parts-2026111*')):
    by=collections.defaultdict(lambda:[0,0,0,0])
    tsv={}
    for l in open(run+'/parts.tsv'):
        f=l.split('\t'); tsv[f[0]]=(int(f[3]),int(f[4]))
    for p in glob.glob(run+'/part-*.json'):
        d=json.load(open(p)); w=d.get('where','actions?')
        k=p.split('-')[-1][:-5]
        ms=d.get('mutants',[])
        to=sum('did not finish' in (m.get('detail') or '') for m in ms)
        j=sum(m['status']!='NOT RUN' for m in ms)-to
        by[w][0]+=j; by[w][1]+=to; by[w][2]+=1
        if k in tsv: by[w][3]+=tsv[k][1]-tsv[k][0]
    print(os.path.basename(run)[6:], {w:f"judged {v[0]} TO {v[1]} parts {v[2]} part-h {v[3]/3600:.1f}" for w,v in by.items()})
