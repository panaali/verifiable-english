#!/usr/bin/env python3
"""Recompute Wilson intervals from pinned counts; retain frozen/adjudicated separation."""
from pathlib import Path
import json
from math import sqrt
from statistics import NormalDist

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'generated'
DATASETS = [('folio','FOLIO'),('proofwriter','ProofWriter'),('cedar','Cedar'),
            ('gatekeeper','Gatekeeper'),('alloy','Alloy'),('fret','FRET'),('clover','Clover')]
SRC = '<!-- src: paper/sources/e0-metrics.json; paper/sources/e0-second-rater.md; provenance in paper/sources/manifest.json. -->'

def write(name, text):
    path = OUT / name
    text = text.rstrip() + '\n'
    if not path.exists() or path.read_text() != text:
        path.write_text(text)

def wilson(k, n):
    z = NormalDist().inv_cdf(.975)
    p = k/n
    center = (p+z*z/(2*n))/(1+z*z/n)
    half = z*sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return max(0., center-half), min(1., center+half)

def cell(k,n):
    lo,hi = wilson(k,n)
    return f'{k}/{n}; {100*k/n:.1f}% [{100*lo:.1f}, {100*hi:.1f}]'

def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'---|'*len(headers),
                      *['| '+' | '.join(map(str,r))+' |' for r in rows]])+'\n'

def main():
    OUT.mkdir(exist_ok=True)
    m = json.loads((ROOT/'sources/e0-metrics.json').read_text())
    n = m['denominator_per_dataset']
    assert n == 30
    for key,_ in DATASETS:
        c = m['second_counts'][key]
        assert sum(c.values()) == n
        for name,k in [('strict',c['DIRECT']),('lenient',c['DIRECT']+c['REIFIED'])]:
            r = m['second_rates'][key][name]
            lo,hi = wilson(k,n)
            assert k == r['k'] and abs(lo-r['ci_low']) < 1e-12 and abs(hi-r['ci_high']) < 1e-12
    for filename,caption,get in [
        ('e0-first-table.md','First-rater frozen counts. Strict and lenient fit with nominal 95% Wilson intervals. Gatekeeper rows classify core rules, not all exemptions.',lambda k:m['agreement'][k]['first_counts']),
        ('e0-coverage-table.md','Second-rater frozen counts. Strict and lenient fit with nominal 95% Wilson intervals.',lambda k:m['second_counts'][k])]:
        rows=[]
        for key,name in DATASETS:
            c=get(key); rows.append([name,cell(c.get('DIRECT',0),n),cell(c.get('DIRECT',0)+c.get('REIFIED',0),n)])
        write(filename,caption+'\n\n'+table(['Dataset','Strict fit','Lenient fit'],rows)+'\n'+SRC)
    rows=[]
    for key,name in DATASETS:
        a=m['agreement'][key]; row=[name]
        for mode in ['four_way','collapsed']:
            v=a[mode]; row.extend([f"{v['matching']}/{v['n']} ({100*v['observed']:.1f}%)",'undefined' if v['kappa'] is None else f"{v['kappa']:.3f}"])
        rows.append(row)
    write('e0-agreement-table.md',table(['Dataset','Four-way agreement','Kappa','Fit/no-fit agreement','Kappa'],rows)+'\n'+SRC)
    rows=[]
    for key in ['cedar','gatekeeper']:
        c=m['proposed_adjudicated_counts'][key]
        rows.append([key.title(),cell(c['DIRECT'],n),cell(c['DIRECT']+c['REIFIED'],n)])
    rows.extend([['All frozen claimed-fit witnesses','114 parse/type checks','3 Cedar translations later found defective'],['Proposed corrected fit inventory','111/210','Not a pooled population estimate']])
    write('e0-corrections-table.md','Proposed adjudication only; unchanged datasets retain the frozen counts.\n\n'+table(['Dataset / inventory','Strict fit / checks','Lenient fit / qualification'],rows)+'\n'+SRC)
    rows=[]
    for e in m['roadmap_independent']:
        rows.append([e['construct'],e['total'],', '.join(f'{name} {e["per_dataset"][key]}' for key,name in DATASETS if e['per_dataset'][key])])
    write('e0-constructs-table.md',table(['Missing construct','Items','Dataset counts'],rows)+'\n'+SRC)
    # The per-dataset ledger is a committed design judgment, not an inferred measurement.
    ledger=(ROOT.parent/'docs/spec/v0.1-coverage.md').read_text()
    import re
    rows=[]
    for key,name in DATASETS:
        match=re.search(r'^\| '+key+r' \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$',ledger,re.M)
        assert match,key
        v=list(map(int,match.groups()))
        rows.append([name,*[f'{x}/{n}' for x in v[:4]]])
    write('coverage-projection-table.md','PROJECTION: lenient fits from the frozen baseline; A = closure, B = proposed linear integer arithmetic.\n\n'+table(['Dataset','Base','A','B','A+B'],rows)+'\nFrozen inventory totals: 114/210, 141/210, 128/210, and 155/210. With proposed adjudication: 111/210, 141/210, 125/210, and 155/210, respectively. These are heterogeneous inventory totals.\n\n<!-- src: docs/spec/v0.1-coverage.md, Per-dataset fit projection. -->')
    r=json.loads((ROOT.parent/'experiments/E0/closure_witnesses/report.json').read_text())
    write('closure-witness-table.md',table(['Closure development artifact','Count'],[['Cedar items',r['cedar_items']],['Alloy items',r['alloy_items']],['Paired true/false models',r['models']],['Python/Lean agreements',f"{r['python_lean_agree']}/{r['models']}"]])+'\n<!-- src: experiments/E0/closure_witnesses/report.json; README.md in that directory. -->')
    print('E0 tables: counts checked; Wilson intervals independently recomputed.')

if __name__ == '__main__':
    main()
