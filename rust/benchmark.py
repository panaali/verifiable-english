"""Sequential no-trace API-vs-API and kernel-vs-kernel benchmarks.

Setup, decoding, process startup and initial input validation are not timed.
Python API calls revalidate models and recompute hashes; Rust API calls check
immutable input compatibility. Both return results without explanatory traces.
Kernels evaluate already-checked formulas/models with the same work budget and
result wrapping: Python _evaluate_validated(trace=False) and Rust's feature-gated
EvaluationKernel. Search includes candidate construction and validation. Pruned
search reports raw times/counts only; both implementations now prune unused predicates.
"""
from __future__ import annotations
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ve import Environment, FiniteModel, evaluate, find_countermodel
from ve.ast import (Binary, Body, Document, Forall, Named, Not, Or, Reach, Unary, Var, document_from_data, document_to_data)
from ve.evaluate import _evaluate_validated


def inputs(repeats):
    data = {'language':'ve.core@0','profile':'relational-fol@0','spec_revision':'ve-v0-draft-2026-09-20',
            'vocabulary':{'sorts':{'item':{'description':'Item.'}},
                          'predicates':{'edge':{'arguments':['item','item'],'description':'Edge.'}},'constants':{}}}
    env = Environment.from_dict(data)
    f = Forall('item', Forall('item', Forall('item', Binary('edge',Var(2),Var(0)))))
    cases = []
    for n in [2,4,8,16,24,32,64]:
        domain = [f'e{i}' for i in range(n)]
        model = FiniteModel.from_dict(env,{'complete':True,'domains':{'item':domain},'constants':{},
                                          'relations':{'edge':[[a,b] for a in domain for b in domain]}})
        work = 1+n+n*n+n**3
        cases.append({'id':f'eval_n{n}','kind':'evaluation','size':n,'environment':env.to_dict(),
                      'model':model.to_dict(),'ast':document_to_data(env,Document((f,))),
                      'iterations':max(3,min(500,100000//work)),'repeats':repeats})
    closure_data = {**data, 'language':'ve.core@0.1', 'profiles':['closure@0','relational-fol@0'],
                    'spec_revision':'ve-v0.1-closure-2026-09-21'}
    closure_data.pop('profile')
    closure_env = Environment.from_dict(closure_data)
    # A fixed directed cycle, with and without a body edge. One quantifier
    # varies the endpoints/captured context; setup and parsing stay untimed.
    for body in (False, True):
        n = 12
        domain = [f'e{i:02}' for i in range(n)]
        model = FiniteModel.from_dict(closure_env, {'complete':True, 'domains':{'item':domain}, 'constants':{},
            'relations':{'edge':[[domain[i],domain[(i+1)%n]] for i in range(n)]}})
        edge = Body('item', Binary('edge',Var(1),Var(0))) if body else Named('edge')
        closure = Forall('item', Reach('plus',edge,Var(0),Var(0)))
        cases.append({'id':f'closure_{"body" if body else "named"}_n{n}', 'kind':'evaluation', 'size':n,
            'environment':closure_env.to_dict(), 'model':model.to_dict(),
            'ast':document_to_data(closure_env,Document((closure,))), 'iterations':5, 'repeats':repeats})
    atom = Binary('edge',Var(1),Var(0))
    conclusion = Forall('item',Forall('item',Or(atom,Not(atom))))
    for n in [1,2,3]:
        cases.append({'id':f'search_binary_n{n}','kind':'search','size':n,'environment':env.to_dict(),
                      'ast':document_to_data(env,Document((conclusion,))),'max_domain_size':n,
                      'iterations':max(1,12//(2**n)),'repeats':repeats})
    data['vocabulary']['predicates']['marked'] = {'arguments':['item'],'description':'Marked.'}
    env = Environment.from_dict(data)
    atom = Unary('marked',Var(0)); conclusion = Forall('item',Or(atom,Not(atom)))
    cases.append({'id':'search_unused_binary_n3','kind':'pruned_search','size':3,'environment':env.to_dict(),
                  'ast':document_to_data(env,Document((conclusion,))),'max_domain_size':3,'iterations':1,'repeats':repeats})
    return cases


def timed(fn, iterations, repeats):
    fn()  # warmup
    values=[]
    for _ in range(repeats):
        start=time.perf_counter()
        for _ in range(iterations): last=fn()
        values.append((time.perf_counter()-start)/iterations)
    return values,last


def main(repeats, output, closure_only=False):
    from tools import rust_build
    env = rust_build.cargo_env()
    subprocess.run(['cargo','build','-j','2','--locked','--release','--manifest-path',str(ROOT/'rust/Cargo.toml'),
                    '--features','bench-internals','--example','bench'],cwd=ROOT,env=env,check=True)
    cases=inputs(repeats)
    if closure_only:
        cases = [c for c in cases if c['id'].startswith('closure_')]
    path=ROOT/'rust/target/benchmark-input.json';path.write_text(json.dumps(cases))
    # Alternate language order across repetitions by collecting one sample at a time.
    # Python and Rust run sequentially, not concurrently competing for CPU.
    rust_samples={c['id']:[] for c in cases}; python_samples={c['id']:[] for c in cases}
    kernel_samples={c['id']:[] for c in cases if c['kind']=='evaluation'}
    rust_kernel_samples={key:[] for key in kernel_samples}
    load_start=os.getloadavg()
    prepared={}
    for c in cases:
        e=Environment.from_dict(c['environment']);d=document_from_data(e,c['ast'])
        m=FiniteModel.from_dict(e,c['model']) if c['kind']=='evaluation' else None
        prepared[c['id']]=(e,d,m)
    observations={};rust_observations={}
    for repeat in range(repeats):
        def rust():
            path.write_text(json.dumps([{**c,'repeats':1} for c in cases]))
            run=subprocess.run([str(ROOT/'rust/target/release/examples/bench'),str(path)],check=True,capture_output=True,text=True)
            for r in json.loads(run.stdout):
                rust_samples[r['id']].extend(r['seconds_per_call']);rust_observations[r['id']]=r['observations']
                if r['id'] in rust_kernel_samples:
                    rust_kernel_samples[r['id']].extend(r['kernel_seconds_per_call'])
                    assert r['kernel_observations'] == r['observations']
        def python():
            for c in cases:
                e,d,m=prepared[c['id']];f=d.formulas[-1]
                if c['kind']=='evaluation':
                    samples,last=timed(lambda:evaluate(e,f,m,trace=False),c['iterations'],1)
                    observations[c['id']]={'value':last.value,'evaluations':last.evaluations}
                    ks,klast=timed(lambda:_evaluate_validated(d.formulas,m,max_evaluations=1_000_000,trace=False),c['iterations'],1)
                    assert klast.value == last.value and klast.evaluations == last.evaluations
                    assert klast.explanation is None and last.explanation is None
                    kernel_samples[c['id']].extend(ks)
                else:
                    samples,last=timed(lambda:find_countermodel(e,d.formulas[:-1],f,max_domain_size=c['max_domain_size']),c['iterations'],1)
                    observations[c['id']]={'status':last.status,'models_checked':last.models_checked,'evaluations':last.evaluations}
                python_samples[c['id']].extend(samples)
        if repeat%2: python();rust()
        else: rust();python()
        for key in observations:
            assert observations[key] == rust_observations[key], (key, observations[key], rust_observations[key])
        print(f'Completed benchmark repetition {repeat+1}/{repeats}',file=sys.stderr,flush=True)
    results=[]
    for c in cases:
        key=c['id'];py=python_samples[key];rs=rust_samples[key]
        assert observations[key]==rust_observations[key],(key,observations[key],rust_observations[key])
        row={'id':key,'kind':c['kind'],'size':c['size'],'iterations_per_sample':c['iterations'],
             'python_seconds_per_call':py,'rust_seconds_per_call':rs,
             'python_median_ms':statistics.median(py)*1000,'rust_median_ms':statistics.median(rs)*1000,
             'python_observations':observations[key],'rust_observations':rust_observations[key]}
        if c['kind'] != 'pruned_search':
            row['api_ratio'] = statistics.median(py)/statistics.median(rs)
        else:
            row['comparison'] = 'Both prune unused predicates; raw times and counts only, no speedup ratio.'
        if key in kernel_samples:
            pk=kernel_samples[key];rk=rust_kernel_samples[key]
            row['python_kernel_seconds_per_call']=pk
            row['rust_kernel_seconds_per_call']=rk
            row['python_kernel_median_ms']=statistics.median(pk)*1000
            row['rust_kernel_median_ms']=statistics.median(rk)*1000
            row['kernel_ratio']=statistics.median(pk)/statistics.median(rk)
        results.append(row)
    def command(*args):
        run = subprocess.run(args, text=True, capture_output=True, env=env)
        return run.stdout.strip() if run.returncode == 0 else f'Unavailable: {run.stderr.strip()}'
    metadata={'platform':platform.platform(),'machine':platform.machine(),'python':sys.version,
              'rustc':command('rustc','--version'),'cargo':command('cargo','--version'),
              'git_revision':command('git','rev-parse','HEAD'),
              'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted([*ROOT.glob('ve/*.py'), *ROOT.glob('rust/ve-core/src/*.rs'),
                                                ROOT/'rust/ve-core/examples/bench.rs', ROOT/'rust/benchmark.py',
                                                ROOT/'rust/Cargo.lock', ROOT/'rust/ve-core/Cargo.toml'])},
              'load_average_start':load_start,'load_average_end':os.getloadavg(),
              'trace':False,
              'repeats':repeats,'gc_enabled':gc.isenabled(),
              'command':f'python rust/benchmark.py --repeats {repeats} --output {output}' + (' --closure-only' if closure_only else ''),
              'method':__doc__,'results':results}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(metadata,indent=2)+'\n')
    for r in results:
        detail = f", API ratio {r['api_ratio']:.2f}x" if 'api_ratio' in r else ', unused-predicate pruning (raw times/counts only)'
        if 'kernel_ratio' in r: detail += f", kernel ratio {r['kernel_ratio']:.2f}x"
        print(f"{r['id']}: Python {r['python_median_ms']:.4f} ms, Rust {r['rust_median_ms']:.4f} ms{detail}")


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repeats',type=int,default=5)
    p.add_argument('--output',type=Path,default=ROOT/'rust/benchmark-results.json')
    p.add_argument('--closure-only',action='store_true')
    a=p.parse_args();main(a.repeats,a.output,a.closure_only)
