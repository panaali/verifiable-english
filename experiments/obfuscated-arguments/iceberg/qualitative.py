#!/usr/bin/env python3
"""Render and check ONLY the relational skeleton, with explicit Lean theorem imports.
Does not translate rational arithmetic or verify predicate-to-Lean correspondence.
Run after verify.py from the repository root.
"""
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from ve import (And, Const, Document, Environment, Forall, Implies, Unary, Var,
                parse, print_document, render, prove_entailment,
                check_entailment_certificate, formula_to_data)

meanings = {
    'admissible': 'Satisfies the Tub and Process premises in SPEC.md; arithmetic opaque to VE.',
    'water': 'Water material premise holds; arithmetic opaque to VE.',
    'air': 'Air endpoint premise holds; arithmetic opaque to VE.',
    'metal': 'Positive submerged metal volume and greater density premises hold; arithmetic opaque to VE.',
    'bounded': 'Nonnegative tolerance and air-mass bound hold; arithmetic opaque to VE.',
    'stable': 'Final height is Within the fixed nonnegative tolerance; arithmetic opaque to VE.',
    'lower': 'Final height is strictly below the rim; comparison opaque to relational VE.',
    'dry': 'Cumulative spill is zero (not that the tub contains no water).',
}
env = Environment.from_dict({
    'language': 've.core@0', 'profile': 'relational-fol@0',
    'spec_revision': 've-v0-draft-2026-09-20',
    'vocabulary': {
        'sorts': {'tub': {'description': 'A complete tub/process case with a fixed nonnegative tolerance.'}},
        'predicates': {p: {'arguments': ['tub'], 'description': d} for p,d in meanings.items()},
        'constants': {c: {'sort': 'tub', 'description': f'The {c.upper()} case.'} for c in ['w','a','m']},
    },
})
u = lambda p, t: Unary(p, t)
v = Var(0)
imports = [
    Forall('tub', Implies(And(u('admissible',v),u('water',v)), u('stable',v))),
    Forall('tub', Implies(And(u('admissible',v),And(u('air',v),u('bounded',v))),u('stable',v))),
    Forall('tub', Implies(And(u('admissible',v),u('metal',v)),u('lower',v))),
    Forall('tub', Implies(u('admissible',v),u('dry',v))),
]
facts = [u('admissible',Const(c)) for c in ['w','a','m']]
facts += [u('water',Const('w')),u('air',Const('a')),u('bounded',Const('a')),u('metal',Const('m'))]
outcomes = [u('stable',Const('w')),u('stable',Const('a')),u('lower',Const('m'))]
outcomes += [u('dry',Const(c)) for c in ['w','a','m']]
goal = outcomes[-1]
for f in reversed(outcomes[:-1]):
    goal = And(f,goal)

(HERE/'environment.json').write_text(json.dumps(env.to_dict(),indent=2)+'\n')
for name, fs in [('imports',imports),('facts',facts),('conclusion',[goal])]:
    document=Document(tuple(fs))
    text=print_document(env,document)
    assert parse(env,text)==document
    (HERE/(name+'.ve')).write_text(text)

start=time.perf_counter()
proof=prove_entailment(env,imports+facts,goal,max_steps=10000)
assert proof.certificate is not None, proof
replay=check_entailment_certificate(env,imports+facts,goal,proof.certificate,max_steps=10000)
assert replay.valid, replay
query={'id':'iceberg-qualitative-only','environment':env.to_dict(),
       'premises':[formula_to_data(env,f) for f in imports+facts],
       'conclusion':formula_to_data(env,goal),'certificate':proof.certificate}
(HERE/'qualitative-query.json').write_text(json.dumps(query,indent=2)+'\n')
result=subprocess.run([str(ROOT/'lean/.lake/build/bin/ve_conformance'),'check-certificate'],
                      input=json.dumps([query]),text=True,capture_output=True,check=True)
rows=json.loads(result.stdout)
assert len(rows)==1 and rows[0]['valid'],rows
(HERE/'qualitative-verification.json').write_text(json.dumps({
    'scope':'Relational implications only; Lean arithmetic theorem imports are trusted leaves here.',
    'canonical_roundtrip':True,'python_certificate_valid':replay.valid,
    'lean':rows,'seconds':round(time.perf_counter()-start,6)},indent=2)+'\n')
print('PASS: canonical VE roundtrip, Python certificate replay, Lean certificate replay')
