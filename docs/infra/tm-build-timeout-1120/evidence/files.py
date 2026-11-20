import json,glob,os,collections
root='/home/seyran/code/manage-agents/test-skip/nightly'
to_files=collections.Counter(); to_ids=set(); judged_where=collections.defaultdict(list)
for run in sorted(glob.glob(root+'/parts-2026111*')):
    for p in glob.glob(run+'/part-*.json'):
        d=json.load(open(p)); w=d.get('where','actions?')+'/j'+str(d.get('jobs'))
        for m in d.get('mutants',[]):
            det=m.get('detail') or ''
            if 'did not finish' in det:
                if run>=root+'/parts-20261116': to_files[m['file']]+=1; to_ids.add(m['id'])
            elif m['status'] in ('KILLED','SURVIVOR','INVALID','UNKNOWN') :
                judged_where[m['id']].append((os.path.basename(run)[6:15],w,m['status']))
print('timeouts by file 11-16..19 (part rows):')
for f,n in to_files.most_common(15): print(' ',n,f)
print('distinct timed-out ids',len(to_ids))
ever=[i for i in to_ids if judged_where.get(i)]
print('of them ever judged in any part since 11-09:',len(ever))
c=collections.Counter(w for i in ever for (_,w,_) in judged_where[i]); print(c.most_common())
