"""Regenerate and independently replay the four closure-induction examples."""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from conformance.certificates import invoke, replay_python
from conformance.induction import math_cases, policy_cases
from ve import Environment, Document, formula_from_data, print_document
from ve.entailment import check_entailment_certificate
from ve.wire import canonical_json


def main():
    cases = math_cases() + policy_cases()
    rows = invoke(ROOT / 'lean/.lake/build/bin/ve_conformance', cases)
    report = []
    for case, row in zip(cases, rows, strict=True):
        assert replay_python(case) and row['valid'], (case['id'], row)
        env = Environment(case['environment'])
        ps = [formula_from_data(env, f) for f in case['premises']]
        goal = formula_from_data(env, case['conclusion'])
        checked = check_entailment_certificate(env, ps, goal, case['certificate'])
        out = HERE / case['id']
        out.mkdir(exist_ok=True)
        (out / 'query.json').write_bytes(canonical_json(case) + b'\n')
        (out / 'premises.ve').write_text(print_document(env, Document(tuple(ps))))
        (out / 'conclusion.ve').write_text(print_document(env, Document((goal,))))
        report.append({'id': case['id'], 'python_valid': checked.valid, 'lean_valid': row['valid'],
                       'replay_steps': checked.steps,
                       'certificate_bytes': len(canonical_json(case['certificate']))})
    (HERE / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
