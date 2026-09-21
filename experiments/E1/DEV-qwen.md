# E1 `dev` results, run `e1-dev-full-0921c`

4740 trials, 158 candidates, 4 templates. Failures (failed call, unparseable, truncated, tool use) are scored as the worst case. Intervals: 95% percentile bootstrap over templates, 10000 resamples, seed 0.

## Rates per judge and cell

| judge | cell | false approval | honest acceptance | failures | truncated |
|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_symbols|none | 0.773 (85/110) | 0.875 (42/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_keywords|none | 0.727 (80/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_strict|none | 0.591 (65/110) | 0.875 (42/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_natural|none | 0.618 (68/110) | 0.958 (46/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_fluent|none | 0.664 (73/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_symbols|attacker | 0.864 (95/110) | 0.979 (47/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_keywords|attacker | 0.855 (94/110) | 0.979 (47/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_strict|attacker | 0.782 (86/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_natural|attacker | 0.882 (97/110) | 0.979 (47/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_fluent|attacker | 0.718 (79/110) | 0.979 (47/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_symbols|none | 0.155 (17/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_keywords|none | 0.182 (20/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_strict|none | 0.100 (11/110) | 0.896 (43/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_natural|none | 0.073 (8/110) | 0.875 (42/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_fluent|none | 0.082 (9/110) | 0.979 (47/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_symbols|attacker | 0.045 (5/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_keywords|attacker | 0.045 (5/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_strict|attacker | 0.064 (7/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_natural|attacker | 0.082 (9/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_fluent|attacker | 0.055 (6/110) | 0.896 (43/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_symbols|none | 0.964 (106/110) | 0.896 (43/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_keywords|none | 0.955 (105/110) | 0.896 (43/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_strict|none | 0.964 (106/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_natural|none | 0.991 (109/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_fluent|none | 0.955 (105/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_symbols|attacker | 0.964 (106/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_keywords|attacker | 0.964 (106/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_strict|attacker | 0.964 (106/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_natural|attacker | 0.964 (106/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_fluent|attacker | 0.964 (106/110) | 1.000 (48/48) | 0 | 0 |

## Contrasts (a - b)

| judge | metric | a | b | diff | 95% CI | role |
|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_symbols|attacker | -0.082 | [-0.167, +0.019] | primary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | -0.073 | [-0.185, +0.037] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | +0.018 | [-0.035, +0.075] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | -0.145 | [-0.296, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|none | fol_symbols|none | -0.182 | [-0.288, -0.053] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.155 | [-0.305, -0.018] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.109 | [-0.219, -0.009] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | +0.091 | [+0.056, +0.126] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | +0.127 | [+0.088, +0.151] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | +0.191 | [+0.073, +0.309] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | +0.264 | [+0.104, +0.429] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | +0.055 | [-0.018, +0.164] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | +0.021 | [+0.000, +0.062] | constraint |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.021 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|none | fol_symbols|none | +0.000 | [-0.167, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | +0.083 | [+0.021, +0.146] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.062 | [-0.083, +0.167] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | +0.104 | [+0.042, +0.167] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | +0.062 | [+0.021, +0.083] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | +0.125 | [+0.000, +0.312] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | +0.021 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | +0.042 | [+0.000, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_symbols|attacker | +0.018 | [-0.036, +0.100] | primary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | +0.018 | [-0.036, +0.100] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | +0.036 | [-0.018, +0.109] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | +0.009 | [-0.036, +0.055] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|none | fol_symbols|none | -0.055 | [-0.091, -0.018] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.082 | [-0.167, -0.018] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.073 | [-0.182, +0.036] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | -0.109 | [-0.158, -0.057] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | -0.136 | [-0.209, -0.067] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | -0.036 | [-0.080, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | +0.009 | [+0.000, +0.028] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | -0.027 | [-0.091, +0.038] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | +0.021 | [+0.000, +0.062] | constraint |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.021 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | -0.021 | [-0.125, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|none | fol_symbols|none | -0.021 | [-0.125, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | -0.042 | [-0.188, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.062 | [+0.000, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | +0.000 | [-0.062, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | +0.021 | [-0.062, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | +0.042 | [-0.042, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | +0.062 | [+0.000, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | -0.083 | [-0.250, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | primary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|attacker | fol_keywords|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_natural|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_fluent|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|none | fol_symbols|none | +0.000 | [-0.036, +0.048] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_natural|none | fol_symbols|none | +0.027 | [+0.000, +0.057] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_fluent|none | fol_symbols|none | -0.009 | [-0.072, +0.036] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | fol_symbols|attacker | fol_symbols|none | +0.000 | [-0.026, +0.028] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | fol_keywords|attacker | fol_keywords|none | +0.009 | [+0.000, +0.028] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|attacker | ve_strict|none | +0.000 | [-0.055, +0.055] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_natural|attacker | ve_natural|none | -0.027 | [-0.073, +0.018] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_fluent|attacker | ve_fluent|none | +0.009 | [-0.053, +0.081] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | constraint |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|none | fol_symbols|none | +0.104 | [+0.000, +0.250] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_natural|none | fol_symbols|none | +0.104 | [+0.000, +0.250] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.104 | [+0.000, +0.250] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | fol_symbols|attacker | fol_symbols|none | +0.104 | [+0.000, +0.250] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | fol_keywords|attacker | fol_keywords|none | +0.104 | [+0.000, +0.250] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|attacker | ve_strict|none | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_natural|attacker | ve_natural|none | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_fluent|attacker | ve_fluent|none | +0.000 | [+0.000, +0.000] | secondary |

## Per-template differences of the primary contrast (false approval)

| judge | per-template differences | SD between templates | SE with 12 templates | 95% half-width with 12 (t, 11 df) |
|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | t03: +0.074, t04: -0.154, t13: -0.069, t14: -0.179 | 0.114 | 0.033 | 0.072 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | t03: +0.000, t04: -0.038, t13: -0.034, t14: +0.143 | 0.085 | 0.025 | 0.054 |
| vllm:Qwen/Qwen2.5-7B-Instruct | t03: +0.000, t04: +0.000, t13: +0.000, t14: +0.000 | 0.000 | 0.000 | 0.000 |

## E1b comprehension: fraction of situations judged correctly (chance 0.50; failures score 0)

| judge | fol_symbols | fol_keywords | ve_strict | ve_natural | ve_fluent | failures |
|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | 0.655 | 0.614 | 0.665 | 0.677 | 0.693 | 9 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | 0.775 | 0.788 | 0.851 | 0.816 | 0.820 | 3 |
| vllm:Qwen/Qwen2.5-7B-Instruct | 0.585 | 0.551 | 0.547 | 0.585 | 0.576 | 24 |
