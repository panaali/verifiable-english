# verify.py output

| Theorem | Certified (Python) | Certified (Lean) | Hypotheses necessary | Prove time (s) | Certificate bytes |
|---|---|---|---|---|---|
| T1 | yes | yes | (none) | 0.003 | 678 |
| T2 | yes | yes | (none) | 0.004 | 1144 |
| T3 | yes | yes | 2/2 | 0.004 | 928 |
| T4 | yes | yes | 1/1 | 0.003 | 614 |
| T5 | yes | yes | 2/2 | 0.008 | 1586 |
| T6 | yes | yes | 3/3 | 0.126 | 10522 |
| T7mono | no | n/a | n/a | 17.585 | 0 |
| T7a | yes | yes | 2/2 | 0.056 | 4676 |
| T7b | yes | yes | 2/2 | 0.048 | 3474 |
| T7 | yes | yes | 2/2 | 0.013 | 1571 |
| T8 | yes | yes | 3/3 | 0.007 | 1392 |
| T9 | no | n/a | 2/2 | 3.872 | 0 |
| T9a | yes | yes | (none) | 0.001 | 435 |
| T9b | yes | yes | (none) | 0.001 | 519 |
| T9c | yes | yes | (none) | 0.001 | 397 |
| T9d | yes | yes | (none) | 0.002 | 530 |
| T9e | no | n/a | 1/1 | 8.37 | 0 |
| C1 | no | n/a | 2/2 | 0.001 | 0 |
| C2 | yes | yes | 3/3 | 0.008 | 1706 |

Certified by the Python replay checker: 15/19.
Certified by the Lean `check-certificate` executable: 15/19.

- **T7mono not certified**: ResourceLimit — tableau step or certificate nesting budget exhausted Refutation search: ResourceLimit.
- **T9 not certified**: ResourceLimit — tableau step or certificate nesting budget exhausted Refutation search: ResourceLimit.
- **T9e not certified**: ResourceLimit — tableau step or certificate nesting budget exhausted Refutation search: ResourceLimit.
- **C1 not certified**: NotFound — saturated open branch; no entailment certificate found Refutation search: Found.

