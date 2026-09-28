# Lean service parity (stage 1, gate 1)

Commit `6e8b62d`; full corpora. 16556/16556 cases byte-identical to the one-shot executables; service restarts 0.

| Mode | Corpus | Cases | Requests | Identical | One-shot exit codes (cases) |
|---|---|---:|---:|---:|---|
| evaluate | evaluation.json | 701 | 3 | 701 | 0: 701 |
| evaluate | countermodels.json | 708 | 3 | 708 | 0: 708 |
| evaluate | parser.json | 742 | 3 | 742 | 0: 512, 1: 230 |
| evaluate | identity.json | 706 | 3 | 706 | 0: 706 |
| evaluate | validation.json | 43 | 1 | 43 | 1: 43 |
| evaluate | closure.json + countermodel variants | 92 | 1 | 92 | 0: 92 |
| evaluate | P1 lean-replay countermodels | 136 | 1 | 136 | 0: 136 |
| evaluate | forged evaluation fields | 360 | 2 | 360 | 1: 360 |
| evaluate | adversarial (evaluate) | 6 | 1 | 6 | 1: 6 |
| evaluate | batch rejected: null (evaluate) | 2 | 1 | 2 | 2: 2 |
| evaluate | batch rejected: fraction (evaluate) | 1 | 1 | 1 | 2: 1 |
| check-certificate | v0-replay-baseline.json | 882 | 4 | 882 | 0: 512, 1: 370 |
| check-certificate | P1 lean-replay certificates | 364 | 2 | 364 | 0: 364 |
| check-certificate | closure-induction and iceberg queries | 5 | 1 | 5 | 0: 5 |
| check-certificate | certificates.py positive | 732 | 3 | 732 | 0: 732 |
| check-certificate | certificates.py forged | 150 | 1 | 150 | 1: 150 |
| check-certificate | closure_certificates.py positive | 63 | 1 | 63 | 0: 63 |
| check-certificate | closure_certificates.py forged | 442 | 2 | 442 | 1: 442 |
| check-certificate | induction.py positive | 36 | 1 | 36 | 0: 36 |
| check-certificate | induction.py forged | 17 | 1 | 17 | 1: 17 |
| check-certificate | adversarial (check-certificate) | 6 | 1 | 6 | 1: 6 |
| check-certificate | batch rejected: null (check-certificate) | 2 | 1 | 2 | 2: 2 |
| check-certificate | batch rejected: fraction (check-certificate) | 1 | 1 | 1 | 2: 1 |
| order | order.evaluation_cases(200) | 200 | 1 | 200 | 0: 200 |
| order | order surface variants | 200 | 1 | 200 | 0: 200 |
| order | order.py positive | 546 | 3 | 546 | 0: 546 |
| order | order.py forged | 4496 | 18 | 4496 | 0: 512, 1: 3984 |
| order | order.py refuted | 106 | 1 | 106 | 0: 106 |
| order | adversarial (order) | 6 | 1 | 6 | 1: 6 |
| order | batch rejected: null (order) | 2 | 1 | 2 | 2: 2 |
| order | batch rejected: fraction (order) | 1 | 1 | 1 | 2: 1 |
| route | route-cases.json | 356 | 2 | 356 | 1: 356 |
| route | definitions differential (1000 sets) | 2000 | 8 | 2000 | 0: 2000 |
| route | nary core replay of evaluation + closure | 747 | 3 | 747 | 0: 747 |
| route | dag_differential (200) | 200 | 1 | 200 | 1: 200 |
| route | math-mini-paper definitions bundle | 1 | 1 | 1 | 0: 1 |
| route | adversarial (route) | 6 | 1 | 6 | 1: 6 |
| route | batch rejected: null (route) | 2 | 1 | 2 | 2: 2 |
| route | batch rejected: fraction (route) | 1 | 1 | 1 | 2: 1 |
| norms | norms 1100 regenerated documents | 1100 | 5 | 1100 | 0: 1100 |
| norms | route-cases.json through ve_norms_route | 356 | 2 | 356 | 1: 356 |
| norms | adversarial (norms) | 6 | 1 | 6 | 1: 6 |
| norms | batch rejected: null (norms) | 2 | 1 | 2 | 2: 2 |
| norms | batch rejected: fraction (norms) | 1 | 1 | 1 | 2: 1 |
| english | english_lean differential payloads | 17 | 1 | 17 | 0: 17 |
| english | adversarial (english) | 3 | 1 | 3 | 0: 1, 2: 2 |
| english | one-shot JSON acceptance | 4 | 4 | 4 | 0: 4 |
