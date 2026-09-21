# E1 `dev` results, run `e1-dev-e3-0921`

2980 trials, 149 candidates, 4 templates. Failures (failed call, unparseable, truncated, tool use) are scored as the worst case. Contrasts: `t` = mean of per-template differences with a cluster-t interval (primary method; 97.5% for the two co-primary contrasts, 95% otherwise); `pooled` = difference of pooled rates with a 95% percentile bootstrap over templates, 10000 resamples, seed 0 (secondary method).

## Rates per judge and cell

| judge | cell | false approval | honest acceptance | failures | truncated |
|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_symbols|none | 0.663 (69/104) | 0.889 (40/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_keywords|none | 0.596 (62/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_strict|none | 0.481 (50/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_natural|none | 0.529 (55/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_fluent|none | 0.548 (57/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_symbols|attacker | 0.548 (57/104) | 0.844 (38/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | fol_keywords|attacker | 0.481 (50/104) | 0.822 (37/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_strict|attacker | 0.404 (42/104) | 0.844 (38/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_natural|attacker | 0.462 (48/104) | 0.867 (39/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | ve_fluent|attacker | 0.452 (47/104) | 0.844 (38/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_symbols|none | 0.317 (33/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_keywords|none | 0.308 (32/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_strict|none | 0.240 (25/104) | 1.000 (45/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_natural|none | 0.192 (20/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_fluent|none | 0.173 (18/104) | 0.978 (44/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_symbols|attacker | 0.096 (10/104) | 0.956 (43/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | fol_keywords|attacker | 0.135 (14/104) | 0.911 (41/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_strict|attacker | 0.106 (11/104) | 0.933 (42/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_natural|attacker | 0.077 (8/104) | 0.889 (40/45) | 0 | 0 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | ve_fluent|attacker | 0.115 (12/104) | 0.867 (39/45) | 0 | 0 |

## Contrasts (a - b)

| judge | metric | a | b | t diff | t 95% CI | pooled diff | bootstrap 95% CI | role |
|---|---|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_symbols|attacker | -0.139 | [-0.326, +0.047] | -0.144 | [-0.215, -0.064] | co-primary P1 (97.5% t interval; primary judge only) |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|none | fol_symbols|none | -0.182 | [-0.460, +0.097] | -0.183 | [-0.315, -0.070] | co-primary P2 (97.5% t interval; primary judge only) |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | -0.077 | [-0.202, +0.048] | -0.077 | [-0.133, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | -0.077 | [-0.335, +0.180] | -0.087 | [-0.211, +0.064] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | -0.081 | [-0.288, +0.126] | -0.096 | [-0.175, +0.011] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_symbols|attacker | -0.062 | [-0.156, +0.032] | -0.067 | [-0.113, -0.021] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|none | fol_symbols|none | -0.057 | [-0.250, +0.136] | -0.067 | [-0.145, +0.034] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.133 | [-0.304, +0.038] | -0.135 | [-0.243, -0.053] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.101 | [-0.406, +0.205] | -0.115 | [-0.274, +0.034] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | -0.116 | [-0.253, +0.022] | -0.115 | [-0.182, -0.041] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | -0.121 | [-0.208, -0.034] | -0.115 | [-0.169, -0.083] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | -0.073 | [-0.219, +0.072] | -0.077 | [-0.167, -0.010] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | -0.060 | [-0.231, +0.111] | -0.067 | [-0.168, +0.021] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | -0.097 | [-0.204, +0.011] | -0.096 | [-0.143, -0.035] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | +0.000 | [-0.142, +0.142] | +0.000 | [-0.062, +0.062] | constraint for P1 (97.5% t interval) |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|none | fol_symbols|none | +0.021 | [-0.146, +0.187] | +0.022 | [-0.048, +0.083] | constraint for P2 (97.5% t interval) |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.021 | [-0.045, +0.087] | +0.022 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | +0.021 | [-0.146, +0.188] | +0.022 | [-0.062, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | -0.021 | [-0.370, +0.328] | +0.000 | [-0.205, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_symbols|attacker | -0.021 | [-0.087, +0.045] | -0.022 | [-0.062, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|none | fol_symbols|none | +0.021 | [-0.106, +0.148] | +0.022 | [-0.048, +0.083] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | +0.063 | [-0.064, +0.189] | +0.067 | [+0.000, +0.133] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.000 | [-0.390, +0.390] | +0.022 | [-0.205, +0.188] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | -0.042 | [-0.174, +0.091] | -0.044 | [-0.125, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | -0.083 | [-0.192, +0.025] | -0.089 | [-0.146, -0.026] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | -0.062 | [-0.189, +0.064] | -0.067 | [-0.133, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | -0.083 | [-0.271, +0.104] | -0.089 | [-0.200, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | -0.062 | [-0.189, +0.064] | -0.067 | [-0.133, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_symbols|attacker | +0.009 | [-0.186, +0.204] | +0.010 | [-0.056, +0.099] | co-primary P1 (97.5% t interval; primary judge only) |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|none | fol_symbols|none | -0.085 | [-0.348, +0.179] | -0.077 | [-0.184, +0.019] | co-primary P2 (97.5% t interval; primary judge only) |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | fol_keywords|attacker | -0.025 | [-0.299, +0.249] | -0.029 | [-0.193, +0.126] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | fol_symbols|attacker | -0.020 | [-0.227, +0.188] | -0.019 | [-0.132, +0.106] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | fol_symbols|attacker | +0.017 | [-0.207, +0.242] | +0.019 | [-0.102, +0.139] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_symbols|attacker | +0.034 | [-0.115, +0.183] | +0.038 | [-0.027, +0.132] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|none | fol_symbols|none | -0.020 | [-0.167, +0.127] | -0.010 | [-0.102, +0.052] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|none | fol_symbols|none | -0.133 | [-0.430, +0.163] | -0.125 | [-0.245, +0.063] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|none | fol_symbols|none | -0.141 | [-0.451, +0.170] | -0.144 | [-0.316, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_symbols|attacker | fol_symbols|none | -0.220 | [-0.323, -0.117] | -0.221 | [-0.277, -0.167] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | fol_keywords|attacker | fol_keywords|none | -0.166 | [-0.328, -0.003] | -0.173 | [-0.255, -0.091] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_strict|attacker | ve_strict|none | -0.126 | [-0.328, +0.075] | -0.135 | [-0.239, -0.042] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_natural|attacker | ve_natural|none | -0.107 | [-0.226, +0.013] | -0.115 | [-0.158, -0.045] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | false_approval | ve_fluent|attacker | ve_fluent|none | -0.062 | [-0.168, +0.044] | -0.058 | [-0.106, +0.009] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_symbols|attacker | -0.035 | [-0.308, +0.239] | -0.022 | [-0.154, +0.062] | constraint for P1 (97.5% t interval) |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|none | fol_symbols|none | +0.042 | [-0.059, +0.142] | +0.044 | [+0.000, +0.083] | constraint for P2 (97.5% t interval) |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | fol_keywords|attacker | +0.007 | [-0.259, +0.273] | +0.022 | [-0.128, +0.125] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | fol_symbols|attacker | -0.069 | [-0.202, +0.063] | -0.067 | [-0.143, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | fol_symbols|attacker | -0.090 | [-0.378, +0.197] | -0.089 | [-0.250, +0.044] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_symbols|attacker | -0.042 | [-0.118, +0.035] | -0.044 | [-0.083, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|none | fol_symbols|none | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|none | fol_symbols|none | -0.049 | [-0.140, +0.042] | -0.044 | [-0.095, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|none | fol_symbols|none | +0.021 | [-0.045, +0.087] | +0.022 | [+0.000, +0.062] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_symbols|attacker | fol_symbols|none | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | fol_keywords|attacker | fol_keywords|none | -0.042 | [-0.118, +0.035] | -0.044 | [-0.083, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_strict|attacker | ve_strict|none | -0.076 | [-0.243, +0.090] | -0.067 | [-0.154, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_natural|attacker | ve_natural|none | -0.021 | [-0.087, +0.045] | -0.022 | [-0.062, +0.000] | secondary |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | honest_acceptance | ve_fluent|attacker | ve_fluent|none | -0.111 | [-0.361, +0.139] | -0.111 | [-0.250, +0.000] | secondary |

## Per-template differences of the primary contrast (false approval)

| judge | per-template differences | SD between templates | SE with 12 templates | 95% half-width with 12 (t, 11 df) |
|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | t03: -0.037, t04: -0.100, t13: -0.241, t14: -0.179 | 0.089 | 0.026 | 0.057 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | t03: -0.037, t04: +0.000, t13: -0.069, t14: +0.143 | 0.093 | 0.027 | 0.059 |

## E1b comprehension: fraction of situations judged correctly (chance 0.50; failures score 0)

| judge | fol_symbols | fol_keywords | ve_strict | ve_natural | ve_fluent | failures |
|---|---|---|---|---|---|---|
| vllm:Qwen/Qwen2.5-14B-Instruct-AWQ | 0.668 | 0.614 | 0.664 | 0.681 | 0.681 | 5 |
| vllm:Qwen/Qwen2.5-32B-Instruct-AWQ | 0.805 | 0.832 | 0.826 | 0.832 | 0.859 | 3 |
