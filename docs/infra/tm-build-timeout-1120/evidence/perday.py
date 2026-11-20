"""Judged vs build-timeout rows per day (the day a part ended, parts.tsv) and per host, every part record since 11-10;
H = a file whose tries end in a build timeout >= 20% of the time (heavy20.json), L = the others. Read-only."""
import json, glob, collections, datetime
root = '/home/seyran/code/manage-agents/test-skip/nightly'
heavy = set(json.load(open('/home/seyran/code/manage-agents/reviews/tm-build-timeout-1120/evidence/heavy20.json')))
byday = collections.defaultdict(collections.Counter)
for run in sorted(glob.glob(root + '/parts-2026111*')):
    tsv = {l.split('\t')[0]: int(l.split('\t')[4]) for l in open(run + '/parts.tsv')}
    for p in glob.glob(run + '/part-*.json'):
        k = p.split('-')[-1][:-5]
        if k not in tsv:
            continue
        d = json.load(open(p)); day = datetime.datetime.fromtimestamp(tsv[k], datetime.UTC).strftime('%m-%d')
        for m in d.get('mutants', []):
            if m['status'] == 'NOT RUN':
                continue
            to = 'did not finish' in (m.get('detail') or '')
            byday[day][('TO ' if to else 'judged ') + d.get('where', 'actions') + (' H' if m['file'] in heavy else ' L')] += 1
for day, c in sorted(byday.items()):
    j = sum(v for k, v in c.items() if k.startswith('judged')); t = sum(v for k, v in c.items() if k.startswith('TO'))
    print(day, f'judged {j} build-timeout {t}', dict(sorted(c.items())))
