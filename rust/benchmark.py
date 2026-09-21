"""Reproducible checked-API benchmark; no process startup or input decoding timed.

Python's API revalidates models, recomputes hashes, and builds explanations.
Rust's immutable checked types avoid revalidation and its evaluator has no trace.
Also time Python's internal evaluator (still builds explanations), and report
search with matched enumeration separately from unused-predicate pruning.
"""
from __future__ import annotations
import argparse
import gc
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
from ve.ast import (Binary, Document, Forall, Not, Or, Unary, Var, document_from_data, document_to_data)
from ve.evaluate import _Evaluator


def inputs(repeats):
    data = {'language':'ve.core@0','profile':'relational-fol@0','spec_revision':'ve-v0-draft-2026-09-20',
            'vocabulary':{'sorts':{'item':{'description':'Item.'}},
                          'predicates':{'edge':{'arguments':['item','item'],'description':'Edge.'}},'constants':{}}}
    env = Environment.from_dict(data)
    f = Forall('item', Forall('item', Forall('item', Binary('edge',Var(2),Var(0)))))
    cases = []
    for n in [2,4,8,16,24,32]:
        domain = [f'e{i}' for i in range(n)]
        model = FiniteModel.from_dict(env,{'complete':True,'domains':{'item':domain},'constants':{},
                                          'relations':{'edge':[[a,b] for a in domain for b in domain]}})
        work = 1+n+n*n+n**3
        cases.append({'id':f'eval_n{n}','kind':'evaluation','size':n,'environment':env.to_dict(),
                      'model':model.to_dict(),'ast':document_to_data(env,Document((f,))),
                      'iterations':max(3,min(500,100000//work)),'repeats':repeats})
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


def main(repeats, output):
    env = {**os.environ,'CARGO_HOME':str(ROOT/'.cargo-home'),'CARGO_TARGET_DIR':str(ROOT/'rust/target')}
    subprocess.run(['cargo','build','--locked','--release','--manifest-path',str(ROOT/'rust/Cargo.toml'),
                    '--example','bench'],cwd=ROOT,env=env,check=True)
    cases=inputs(repeats)
    path=ROOT/'rust/target/benchmark-input.json';path.write_text(json.dumps(cases))
    # Alternate language order across repetitions by collecting one sample at a time.
    # Python and Rust run sequentially, not concurrently competing for CPU.
    rust_samples={c['id']:[] for c in cases}; python_samples={c['id']:[] for c in cases}
    kernel_samples={c['id']:[] for c in cases if c['kind']=='evaluation'}
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
        def python():
            for c in cases:
                e,d,m=prepared[c['id']];f=d.formulas[-1]
                if c['kind']=='evaluation':
                    samples,last=timed(lambda:evaluate(e,f,m,max_trace_nodes=1_000_000),c['iterations'],1)
                    observations[c['id']]={'value':last.value,'evaluations':last.evaluations}
                    ks,_=timed(lambda:_Evaluator(e,m,1_000_000).formula(f),c['iterations'],1)
                    kernel_samples[c['id']].extend(ks)
                else:
                    samples,last=timed(lambda:find_countermodel(e,d.formulas[:-1],f,max_domain_size=c['max_domain_size']),c['iterations'],1)
                    observations[c['id']]={'status':last.status,'models_checked':last.models_checked,'evaluations':last.evaluations}
                python_samples[c['id']].extend(samples)
        if repeat%2: python();rust()
        else: rust();python()
        print(f'Completed benchmark repetition {repeat+1}/{repeats}',file=sys.stderr,flush=True)
    results=[]
    for c in cases:
        key=c['id'];py=python_samples[key];rs=rust_samples[key]
        if c['kind']!='pruned_search': assert observations[key]==rust_observations[key],(key,observations[key],rust_observations[key])
        row={'id':key,'kind':c['kind'],'size':c['size'],'iterations_per_sample':c['iterations'],
             'python_seconds_per_call':py,'rust_seconds_per_call':rs,
             'python_median_ms':statistics.median(py)*1000,'rust_median_ms':statistics.median(rs)*1000,
             'api_speedup':statistics.median(py)/statistics.median(rs),
             'python_observations':observations[key],'rust_observations':rust_observations[key]}
        if key in kernel_samples:
            row['python_evaluator_seconds_per_call']=kernel_samples[key]
            row['python_evaluator_median_ms']=statistics.median(kernel_samples[key])*1000
            row['evaluator_speedup']=statistics.median(kernel_samples[key])/statistics.median(rs)
        results.append(row)
    def command(*args):
        run = subprocess.run(args, text=True, capture_output=True, env=env)
        return run.stdout.strip() if run.returncode == 0 else f'Unavailable: {run.stderr.strip()}'
    metadata={'platform':platform.platform(),'machine':platform.machine(),'python':sys.version,
              'rustc':command('rustc','--version'),'cargo':command('cargo','--version'),
              'processor':command('sysctl','-n','machdep.cpu.brand_string'),
              'memory_bytes':command('sysctl','-n','hw.memsize'),
              'repeats':repeats,'gc_enabled':gc.isenabled(),
              'command':f'python rust/benchmark.py --repeats {repeats} --output {output}',
              'method':__doc__,'results':results}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(metadata,indent=2)+'\n')
    for r in results: print(f"{r['id']}: Python {r['python_median_ms']:.4f} ms, Rust {r['rust_median_ms']:.4f} ms, API ratio {r['api_speedup']:.2f}x")


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repeats',type=int,default=5)
    p.add_argument('--output',type=Path,default=ROOT/'rust/benchmark-results.json')
    a=p.parse_args();main(a.repeats,a.output)
