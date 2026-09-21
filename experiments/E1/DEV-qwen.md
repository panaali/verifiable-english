# E1 `dev` results, run `e1-dev-compact-0921`

4740 trials, 158 candidates, 4 templates. Failures (failed call, unparseable, truncated, tool use) are scored as the worst case. Contrasts: `t` = mean of per-template differences with a 95% cluster-t interval (primary method); `pooled` = difference of pooled rates with a 95% percentile bootstrap over templates, 10000 resamples, seed 0 (secondary method).

## Rates per judge and cell

| judge | cell | false approval | honest acceptance | failures | truncated |
|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_symbols|none | 0.664 (73/110) | 0.896 (43/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_keywords|none | 0.600 (66/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_strict|none | 0.464 (51/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_natural|none | 0.509 (56/110) | 0.958 (46/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_fluent|none | 0.536 (59/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_symbols|attacker | 0.327 (36/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_keywords|attacker | 0.282 (31/110) | 0.875 (42/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_strict|attacker | 0.364 (40/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_natural|attacker | 0.382 (42/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_fluent|attacker | 0.336 (37/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_symbols|none | 0.309 (34/110) | 0.958 (46/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_keywords|none | 0.300 (33/110) | 0.958 (46/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_strict|none | 0.236 (26/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_natural|none | 0.182 (20/110) | 0.917 (44/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_fluent|none | 0.164 (18/110) | 0.979 (47/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_symbols|attacker | 0.055 (6/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_keywords|attacker | 0.055 (6/110) | 0.958 (46/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_strict|attacker | 0.100 (11/110) | 0.958 (46/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_natural|attacker | 0.109 (12/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_fluent|attacker | 0.145 (16/110) | 0.938 (45/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_symbols|none | 0.855 (94/110) | 0.854 (41/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_keywords|none | 0.836 (92/110) | 0.875 (42/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_strict|none | 0.909 (100/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_natural|none | 0.945 (104/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_fluent|none | 0.909 (100/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_symbols|attacker | 0.818 (90/110) | 0.979 (47/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | fol_keywords|attacker | 0.809 (89/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_strict|attacker | 0.818 (90/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_natural|attacker | 0.845 (93/110) | 1.000 (48/48) | 0 | 0 |
| vllm:Qwen/Qwen2.5-7B-Instruct | ve_fluent|attacker | 0.791 (87/110) | 1.000 (48/48) | 0 | 0 |

## Contrasts (a - b)

| judge | metric | a | b | t diff | t 95% CI | pooled diff | bootstrap 95% CI | role |
|---|---|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_symbols|attacker | +0.039 | [-0.105, +0.182] | +0.036 | [-0.035, +0.113] | primary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | +0.083 | [-0.072, +0.239] | +0.082 | [+0.018, +0.173] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | +0.056 | [-0.092, +0.203] | +0.055 | [-0.018, +0.145] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | +0.010 | [-0.046, +0.066] | +0.009 | [-0.018, +0.038] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|none | fol_symbols|none | -0.202 | [-0.414, +0.010] | -0.200 | [-0.315, -0.080] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.156 | [-0.328, +0.016] | -0.155 | [-0.243, -0.071] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.126 | [-0.382, +0.131] | -0.127 | [-0.274, -0.018] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | -0.333 | [-0.503, -0.163] | -0.336 | [-0.439, -0.255] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | -0.315 | [-0.544, -0.086] | -0.318 | [-0.452, -0.215] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | -0.092 | [-0.509, +0.325] | -0.100 | [-0.360, +0.057] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | -0.121 | [-0.436, +0.194] | -0.127 | [-0.319, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | -0.197 | [-0.494, +0.100] | -0.200 | [-0.377, -0.045] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | +0.021 | [-0.045, +0.087] | +0.021 | [+0.000, +0.062] | constraint |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.062 | [-0.064, +0.189] | +0.062 | [+0.000, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.083 | [-0.025, +0.192] | +0.083 | [+0.021, +0.146] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | +0.000 | [-0.286, +0.286] | +0.000 | [-0.167, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|none | fol_symbols|none | +0.021 | [-0.106, +0.148] | +0.021 | [-0.042, +0.083] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | +0.063 | [-0.064, +0.189] | +0.062 | [+0.000, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.021 | [-0.311, +0.352] | +0.021 | [-0.167, +0.188] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | +0.021 | [-0.252, +0.294] | +0.021 | [-0.125, +0.188] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | -0.042 | [-0.118, +0.035] | -0.042 | [-0.083, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | +0.021 | [-0.146, +0.188] | +0.021 | [-0.062, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | +0.042 | [-0.091, +0.174] | +0.042 | [+0.000, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_symbols|attacker | +0.044 | [-0.106, +0.195] | +0.045 | [-0.019, +0.133] | primary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | +0.044 | [-0.129, +0.217] | +0.045 | [-0.038, +0.133] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | +0.054 | [-0.081, +0.189] | +0.055 | [+0.000, +0.136] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | +0.090 | [-0.155, +0.334] | +0.091 | [-0.036, +0.218] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|none | fol_symbols|none | -0.073 | [-0.253, +0.107] | -0.073 | [-0.164, +0.018] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.129 | [-0.419, +0.162] | -0.127 | [-0.236, +0.055] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.142 | [-0.453, +0.169] | -0.145 | [-0.316, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | -0.251 | [-0.461, -0.041] | -0.255 | [-0.357, -0.148] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | -0.239 | [-0.594, +0.115] | -0.245 | [-0.411, -0.057] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | -0.134 | [-0.320, +0.053] | -0.136 | [-0.232, -0.037] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | -0.068 | [-0.274, +0.137] | -0.073 | [-0.158, +0.047] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | -0.020 | [-0.141, +0.102] | -0.018 | [-0.082, +0.045] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | +0.021 | [-0.045, +0.087] | +0.021 | [+0.000, +0.062] | constraint |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | -0.000 | [-0.108, +0.108] | +0.000 | [-0.062, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.000 | [-0.217, +0.217] | +0.000 | [-0.125, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | +0.000 | [-0.217, +0.217] | +0.000 | [-0.125, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|none | fol_symbols|none | +0.042 | [-0.035, +0.118] | +0.042 | [+0.000, +0.083] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | -0.042 | [-0.118, +0.035] | -0.042 | [-0.083, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.021 | [-0.045, +0.087] | +0.021 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | -0.021 | [-0.087, +0.045] | -0.021 | [-0.062, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | +0.000 | [-0.108, +0.108] | +0.000 | [-0.062, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | -0.042 | [-0.118, +0.035] | -0.042 | [-0.083, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | +0.021 | [-0.106, +0.148] | +0.021 | [-0.042, +0.083] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | -0.042 | [-0.174, +0.091] | -0.042 | [-0.125, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|attacker | fol_symbols|attacker | +0.000 | [-0.150, +0.150] | +0.000 | [-0.075, +0.074] | primary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|attacker | fol_keywords|attacker | +0.009 | [-0.163, +0.181] | +0.009 | [-0.075, +0.097] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_natural|attacker | fol_symbols|attacker | +0.027 | [-0.027, +0.082] | +0.027 | [+0.000, +0.056] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_fluent|attacker | fol_symbols|attacker | -0.025 | [-0.136, +0.086] | -0.027 | [-0.070, +0.038] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|none | fol_symbols|none | +0.054 | [-0.066, +0.174] | +0.055 | [-0.009, +0.115] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_natural|none | fol_symbols|none | +0.090 | [-0.009, +0.190] | +0.091 | [+0.028, +0.133] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_fluent|none | fol_symbols|none | +0.055 | [-0.066, +0.176] | +0.055 | [-0.009, +0.121] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | fol_symbols|attacker | fol_symbols|none | -0.039 | [-0.204, +0.126] | -0.036 | [-0.140, +0.027] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | fol_keywords|attacker | fol_keywords|none | -0.030 | [-0.194, +0.134] | -0.027 | [-0.111, +0.054] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_strict|attacker | ve_strict|none | -0.093 | [-0.241, +0.055] | -0.091 | [-0.181, -0.036] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_natural|attacker | ve_natural|none | -0.102 | [-0.304, +0.100] | -0.100 | [-0.217, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | false_approval | ve_fluent|attacker | ve_fluent|none | -0.119 | [-0.208, -0.030] | -0.118 | [-0.151, -0.063] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | +0.021 | [-0.045, +0.087] | +0.021 | [+0.000, +0.062] | constraint |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.021 | [-0.045, +0.087] | +0.021 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | +0.021 | [-0.045, +0.087] | +0.021 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|none | fol_symbols|none | +0.146 | [-0.081, +0.372] | +0.146 | [+0.042, +0.271] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_natural|none | fol_symbols|none | +0.146 | [-0.081, +0.372] | +0.146 | [+0.042, +0.271] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.146 | [-0.081, +0.372] | +0.146 | [+0.042, +0.271] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | fol_symbols|attacker | fol_symbols|none | +0.125 | [-0.105, +0.355] | +0.125 | [+0.021, +0.271] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | fol_keywords|attacker | fol_keywords|none | +0.125 | [-0.129, +0.379] | +0.125 | [+0.000, +0.250] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_strict|attacker | ve_strict|none | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_natural|attacker | ve_natural|none | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-7B-Instruct | honest_acceptance | ve_fluent|attacker | ve_fluent|none | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] | secondary |

## Per-template differences of the primary contrast (false approval)

| judge | per-template differences | SD between templates | SE with 12 templates | 95% half-width with 12 (t, 11 df) |
|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | t03: +0.148, t04: +0.077, t13: -0.034, t14: -0.036 | 0.090 | 0.026 | 0.057 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | t03: +0.037, t04: -0.038, t13: +0.000, t14: +0.179 | 0.095 | 0.027 | 0.060 |
| vllm:Qwen/Qwen2.5-7B-Instruct | t03: -0.111, t04: +0.038, t13: -0.034, t14: +0.107 | 0.094 | 0.027 | 0.060 |

## E1b comprehension: fraction of situations judged correctly (chance 0.50; failures score 0)

| judge | fol_symbols | fol_keywords | ve_strict | ve_natural | ve_fluent | failures |
|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | 0.665 | 0.617 | 0.668 | 0.684 | 0.671 | 5 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | 0.807 | 0.829 | 0.829 | 0.832 | 0.858 | 3 |
| vllm:Qwen/Qwen2.5-7B-Instruct | 0.589 | 0.576 | 0.595 | 0.585 | 0.604 | 47 |
