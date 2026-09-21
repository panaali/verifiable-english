# E1 `dev` results, run `e1-dev-e3-0921`

2980 trials, 149 candidates, 4 templates. Failures (failed call, unparseable, truncated, tool use) are scored as the worst case. Contrasts are a - b. `t` = mean of the per-template differences with a cluster-t interval (the preregistered method): 97.5% for the two co-primary contrasts and their honest-acceptance constraints of a PRIMARY judge, 95% everywhere else. `pooled` = difference of pooled rates with a 95% percentile bootstrap over templates; `base items` = the same bootstrap over base items (10000 resamples, seed 0); both are sensitivity analyses.

## Rates per judge and cell

| judge | role | cell | false approval | honest acceptance | failures | truncated |
|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | fol_symbols|none | 0.663 (69/104) | 0.889 (40/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | fol_keywords|none | 0.596 (62/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | ve_strict|none | 0.481 (50/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | ve_natural|none | 0.529 (55/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | ve_fluent|none | 0.548 (57/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | fol_symbols|attacker | 0.548 (57/104) | 0.844 (38/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | fol_keywords|attacker | 0.481 (50/104) | 0.822 (37/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | ve_strict|attacker | 0.404 (42/104) | 0.844 (38/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | ve_natural|attacker | 0.462 (48/104) | 0.867 (39/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | ve_fluent|attacker | 0.452 (47/104) | 0.844 (38/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | fol_symbols|none | 0.317 (33/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | fol_keywords|none | 0.308 (32/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | ve_strict|none | 0.240 (25/104) | 1.000 (45/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | ve_natural|none | 0.192 (20/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | ve_fluent|none | 0.173 (18/104) | 0.978 (44/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | fol_symbols|attacker | 0.096 (10/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | fol_keywords|attacker | 0.135 (14/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | ve_strict|attacker | 0.106 (11/104) | 0.933 (42/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | ve_natural|attacker | 0.077 (8/104) | 0.889 (40/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | ve_fluent|attacker | 0.115 (12/104) | 0.867 (39/45) | 0 | 0 |

## Co-primary contrasts and their constraints

| judge | role | contrast | metric | t diff | level | t interval | pooled diff [95% template bootstrap] | [95% base-item bootstrap] | decision |
|---|---|---|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | P1 attacker | false_approval | -0.139 | 95.0% | [-0.281, +0.003] | -0.144 [-0.215, -0.064] | [-0.234, -0.049] | exploratory (secondary judge): no decision |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | P1 attacker | honest_acceptance | +0.000 | 95.0% | [-0.108, +0.108] | +0.000 [-0.062, +0.062] | [-0.089, +0.089] | exploratory |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | P2 none | false_approval | -0.182 | 95.0% | [-0.394, +0.031] | -0.183 [-0.315, -0.070] | [-0.262, -0.111] | exploratory (secondary judge): no decision |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | secondary_permissive | P2 none | honest_acceptance | +0.021 | 95.0% | [-0.106, +0.148] | +0.022 [-0.048, +0.083] | [-0.044, +0.089] | exploratory |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | P1 attacker | false_approval | +0.009 | 97.5% | [-0.186, +0.204] | +0.010 [-0.056, +0.099] | [-0.058, +0.077] | inconclusive |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | P1 attacker | honest_acceptance | -0.035 | 97.5% | [-0.308, +0.239] | -0.022 [-0.154, +0.062] | [-0.089, +0.044] | constraint fails |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | P2 none | false_approval | -0.085 | 97.5% | [-0.348, +0.179] | -0.077 [-0.184, +0.019] | [-0.176, +0.019] | inconclusive |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | primary | P2 none | honest_acceptance | +0.042 | 97.5% | [-0.059, +0.142] | +0.044 [+0.000, +0.083] | [+0.000, +0.111] | constraint holds |

## Secondary contrasts (exploratory; 95% intervals, no multiplicity adjustment)

| judge | metric | a | b | t diff | t 95% interval | pooled diff [95% template bootstrap] |
|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | -0.077 | [-0.202, +0.048] | -0.077 [-0.133, +0.000] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | -0.077 | [-0.335, +0.180] | -0.087 [-0.211, +0.064] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | -0.081 | [-0.288, +0.126] | -0.096 [-0.175, +0.011] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_symbols|attacker | -0.062 | [-0.156, +0.032] | -0.067 [-0.113, -0.021] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|none | fol_symbols|none | -0.057 | [-0.250, +0.136] | -0.067 [-0.145, +0.034] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.133 | [-0.304, +0.038] | -0.135 [-0.243, -0.053] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.101 | [-0.406, +0.205] | -0.115 [-0.274, +0.034] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | -0.116 | [-0.253, +0.022] | -0.115 [-0.182, -0.041] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | -0.121 | [-0.208, -0.034] | -0.115 [-0.169, -0.083] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | -0.073 | [-0.219, +0.072] | -0.077 [-0.167, -0.010] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | -0.060 | [-0.231, +0.111] | -0.067 [-0.168, +0.021] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | -0.097 | [-0.204, +0.011] | -0.096 [-0.143, -0.035] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.021 | [-0.045, +0.087] | +0.022 [+0.000, +0.062] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.021 | [-0.146, +0.188] | +0.022 [-0.062, +0.125] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | -0.021 | [-0.370, +0.328] | +0.000 [-0.205, +0.125] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_symbols|attacker | -0.021 | [-0.087, +0.045] | -0.022 [-0.062, +0.000] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|none | fol_symbols|none | +0.021 | [-0.106, +0.148] | +0.022 [-0.048, +0.083] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | +0.063 | [-0.064, +0.189] | +0.067 [+0.000, +0.133] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.000 | [-0.390, +0.390] | +0.022 [-0.205, +0.188] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | -0.042 | [-0.174, +0.091] | -0.044 [-0.125, +0.000] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | -0.083 | [-0.192, +0.025] | -0.089 [-0.146, -0.026] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | -0.062 | [-0.189, +0.064] | -0.067 [-0.133, +0.000] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | -0.083 | [-0.271, +0.104] | -0.089 [-0.200, +0.000] |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | -0.062 | [-0.189, +0.064] | -0.067 [-0.133, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | -0.025 | [-0.299, +0.249] | -0.029 [-0.193, +0.126] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | -0.020 | [-0.227, +0.188] | -0.019 [-0.132, +0.106] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | +0.017 | [-0.207, +0.242] | +0.019 [-0.102, +0.139] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_symbols|attacker | +0.034 | [-0.115, +0.183] | +0.038 [-0.027, +0.132] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|none | fol_symbols|none | -0.020 | [-0.167, +0.127] | -0.010 [-0.102, +0.052] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.133 | [-0.430, +0.163] | -0.125 [-0.245, +0.063] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.141 | [-0.451, +0.170] | -0.144 [-0.316, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | -0.220 | [-0.323, -0.117] | -0.221 [-0.277, -0.167] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | -0.166 | [-0.328, -0.003] | -0.173 [-0.255, -0.091] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | -0.126 | [-0.328, +0.075] | -0.135 [-0.239, -0.042] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | -0.107 | [-0.226, +0.013] | -0.115 [-0.158, -0.045] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | -0.062 | [-0.168, +0.044] | -0.058 [-0.106, +0.009] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.007 | [-0.259, +0.273] | +0.022 [-0.128, +0.125] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | -0.069 | [-0.202, +0.063] | -0.067 [-0.143, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | -0.090 | [-0.378, +0.197] | -0.089 [-0.250, +0.044] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_symbols|attacker | -0.042 | [-0.118, +0.035] | -0.044 [-0.083, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|none | fol_symbols|none | +0.000 | [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | -0.049 | [-0.140, +0.042] | -0.044 [-0.095, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.021 | [-0.045, +0.087] | +0.022 [+0.000, +0.062] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | +0.000 | [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | -0.042 | [-0.118, +0.035] | -0.044 [-0.083, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | -0.076 | [-0.243, +0.090] | -0.067 [-0.154, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | -0.021 | [-0.087, +0.045] | -0.022 [-0.062, +0.000] |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | -0.111 | [-0.361, +0.139] | -0.111 [-0.250, +0.000] |

## Per-template differences of the co-primary contrasts (false approval)

| judge | contrast | per-template differences | SD between templates | SE with 12 templates | 97.5% half-width with 12 (t = 2.593) |
|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | P1 attacker | t03: -0.037, t04: -0.100, t13: -0.241, t14: -0.179 | 0.089 | 0.026 | 0.067 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | P2 none | t03: -0.185, t04: -0.150, t13: -0.034, t14: -0.357 | 0.134 | 0.039 | 0.100 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | P1 attacker | t03: -0.037, t04: +0.000, t13: -0.069, t14: +0.143 | 0.093 | 0.027 | 0.070 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | P2 none | t03: -0.037, t04: -0.200, t13: -0.172, t14: +0.071 | 0.126 | 0.036 | 0.094 |

## E1b comprehension: mean over templates of the fraction of situations judged correctly, with a 95% cluster-t interval (chance 0.50; failures score 0)

| judge | fol_symbols | fol_keywords | ve_strict | ve_natural | ve_fluent | failures |
|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | 0.666 [0.555, 0.776] | 0.619 [0.501, 0.736] | 0.669 [0.516, 0.822] | 0.684 [0.517, 0.852] | 0.671 [0.567, 0.775] | 5 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | 0.808 [0.737, 0.879] | 0.830 [0.722, 0.938] | 0.830 [0.698, 0.962] | 0.833 [0.698, 0.969] | 0.858 [0.779, 0.937] | 3 |
| vllm:Qwen/Qwen2.5-7B-Instruct | 0.590 [0.461, 0.719] | 0.576 [0.506, 0.647] | 0.595 [0.515, 0.675] | 0.586 [0.524, 0.648] | 0.606 [0.465, 0.747] | 47 |
