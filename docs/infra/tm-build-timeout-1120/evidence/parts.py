import json,glob,os,sys,collections,datetime
root='/home/seyran/code/manage-agents/test-skip/nightly'
for run in sorted(glob.glob(root+'/parts-2026111[6-9]*')):
    tsv={}
    if os.path.exists(run+'/parts.tsv'):
        for l in open(run+'/parts.tsv'):
            f=l.split('\t'); tsv[f[0]]=(int(f[3]),int(f[4]))
    print('==',os.path.basename(run))
    for p in sorted(glob.glob(run+'/part-*.json'),key=lambda x:int(x.split('-')[-1][:-5])):
        d=json.load(open(p)); k=p.split('-')[-1][:-5]
        ms=d.get('mutants',[])
        st=collections.Counter(m['status'] for m in ms)
        to=[m for m in ms if 'did not finish' in (m.get('detail') or '')]
        tov=collections.Counter(m['detail'].split(' did not')[0].split(': ')[-1]+' '+m['detail'].split('in ')[1].split(' s')[0] for m in to)
        lk=d.get('steps',{}).get('lake',{})
        t=tsv.get(k); when=datetime.datetime.utcfromtimestamp(t[0]).strftime('%m-%dT%H:%M') if t else '?'
        print(f"p{k:>3} {when} {d.get('where','?'):<10} j{d.get('jobs')} s{d.get('seconds')} K{st['KILLED']} S{st['SURVIVOR']} U{st['UNKNOWN']} I{st['INVALID']} NR{st['NOT RUN']} TO{len(to)} {dict(tov)} mb{int(lk.get('mutant_builds',0))} mc{int(lk.get('mutant_checks',0))} sc{int(lk.get('stage_controls',0))}")
