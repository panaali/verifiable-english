\clearpage
\appendix

# Additional analyses and reproducibility

All reanalyses in this appendix are POST HOC. Frozen exploratory tables are identified separately. No new model calls were made.

## E1 discrimination, influence, and model fit (post hoc)

<!-- INCLUDE generated/posthoc-e1-metrics.md -->

<!-- INCLUDE generated/posthoc-e1-contrasts.md -->

<!-- INCLUDE generated/posthoc-thresholds.md -->

<!-- INCLUDE generated/posthoc-logistic.md -->

<!-- INCLUDE generated/posthoc-e1b.md -->

## Weakening-only inventory (post hoc)

Only nine templates contain weakening attacks. Absolute intervals refer to equal-weight template rates, not the pooled rates beside them. The paired contrasts also weight these nine templates equally.

<!-- INCLUDE generated/posthoc-weakening-rates.md -->

<!-- INCLUDE generated/posthoc-weakening-contrasts.md -->

## E4 replies (post hoc inspection)

<!-- INCLUDE generated/posthoc-e4-replies.md -->

# Disputed E0 translations

<!-- INCLUDE generated/posthoc-e0-disputes.md -->

# Frozen exploratory tables and development records

These are archival exploratory results, not new confirmatory findings. S/K/V/N/F have the main-text view meanings; A is e3 and 0 is no explanation. 14B and 32B denote the same Qwen2.5 AWQ judges throughout. The new POST HOC analyses above do not alter their decision rules.

## Secondary contrasts (exploratory; 95% intervals, no multiplicity adjustment)

| judge | metric | a | b | t diff | t 95% interval | pooled diff [95% template bootstrap] |
|---|---|---|---|---|---|---|
| 14B AWQ | false_approval | V, A | K, A | -0.047 | [-0.094, -0.001] | -0.047 [-0.082, -0.002] |
| 14B AWQ | false_approval | N, A | S, A | +0.011 | [-0.046, +0.069] | +0.003 [-0.052, +0.055] |
| 14B AWQ | false_approval | F, A | S, A | -0.147 | [-0.216, -0.078] | -0.157 [-0.219, -0.094] |
| 14B AWQ | false_approval | K, A | S, A | +0.002 | [-0.056, +0.060] | -0.005 [-0.055, +0.048] |
| 14B AWQ | false_approval | K, 0 | S, 0 | +0.002 | [-0.031, +0.036] | -0.002 [-0.028, +0.028] |
| 14B AWQ | false_approval | N, 0 | S, 0 | -0.042 | [-0.137, +0.053] | -0.049 [-0.130, +0.035] |
| 14B AWQ | false_approval | F, 0 | S, 0 | -0.141 | [-0.200, -0.083] | -0.148 [-0.198, -0.096] |
| 14B AWQ | false_approval | S, A | S, 0 | -0.148 | [-0.227, -0.069] | -0.146 [-0.226, -0.084] |
| 14B AWQ | false_approval | K, A | K, 0 | -0.149 | [-0.232, -0.065] | -0.150 [-0.223, -0.083] |
| 14B AWQ | false_approval | V, A | V, 0 | -0.088 | [-0.134, -0.042] | -0.086 [-0.128, -0.048] |
| 14B AWQ | false_approval | N, A | N, 0 | -0.095 | [-0.143, -0.047] | -0.094 [-0.139, -0.055] |
| 14B AWQ | false_approval | F, A | F, 0 | -0.154 | [-0.213, -0.094] | -0.155 [-0.210, -0.098] |
| 14B AWQ | honest_acceptance | V, A | K, A | -0.073 | [-0.120, -0.026] | -0.075 [-0.118, -0.039] |
| 14B AWQ | honest_acceptance | N, A | S, A | +0.028 | [-0.057, +0.113] | +0.029 [-0.048, +0.101] |
| 14B AWQ | honest_acceptance | F, A | S, A | +0.125 | [+0.031, +0.219] | +0.129 [+0.051, +0.212] |
| 14B AWQ | honest_acceptance | K, A | S, A | +0.038 | [-0.031, +0.107] | +0.039 [-0.021, +0.097] |
| 14B AWQ | honest_acceptance | K, 0 | S, 0 | +0.021 | [-0.022, +0.064] | +0.021 [-0.014, +0.061] |
| 14B AWQ | honest_acceptance | N, 0 | S, 0 | +0.007 | [-0.045, +0.058] | +0.007 [-0.038, +0.052] |
| 14B AWQ | honest_acceptance | F, 0 | S, 0 | +0.028 | [-0.023, +0.079] | +0.029 [-0.014, +0.076] |
| 14B AWQ | honest_acceptance | S, A | S, 0 | -0.167 | [-0.290, -0.044] | -0.171 [-0.281, -0.071] |
| 14B AWQ | honest_acceptance | K, A | K, 0 | -0.149 | [-0.246, -0.053] | -0.154 [-0.236, -0.072] |
| 14B AWQ | honest_acceptance | V, A | V, 0 | -0.205 | [-0.322, -0.087] | -0.211 [-0.316, -0.117] |
| 14B AWQ | honest_acceptance | N, A | N, 0 | -0.146 | [-0.245, -0.046] | -0.150 [-0.246, -0.079] |
| 14B AWQ | honest_acceptance | F, A | F, 0 | -0.069 | [-0.146, +0.007] | -0.071 [-0.143, -0.010] |
| 32B AWQ | false_approval | V, A | K, A | +0.036 | [-0.028, +0.101] | +0.034 [-0.018, +0.094] |
| 32B AWQ | false_approval | N, A | S, A | +0.031 | [-0.046, +0.107] | +0.035 [-0.036, +0.101] |
| 32B AWQ | false_approval | F, A | S, A | +0.001 | [-0.095, +0.096] | +0.007 [-0.094, +0.084] |
| 32B AWQ | false_approval | K, A | S, A | -0.009 | [-0.068, +0.050] | +0.002 [-0.056, +0.062] |
| 32B AWQ | false_approval | K, 0 | S, 0 | -0.014 | [-0.037, +0.009] | -0.015 [-0.031, +0.003] |
| 32B AWQ | false_approval | N, 0 | S, 0 | -0.007 | [-0.049, +0.035] | -0.013 [-0.050, +0.022] |
| 32B AWQ | false_approval | F, 0 | S, 0 | -0.044 | [-0.114, +0.027] | -0.054 [-0.118, +0.005] |
| 32B AWQ | false_approval | S, A | S, 0 | -0.126 | [-0.219, -0.033] | -0.145 [-0.236, -0.060] |
| 32B AWQ | false_approval | K, A | K, 0 | -0.121 | [-0.191, -0.050] | -0.128 [-0.189, -0.065] |
| 32B AWQ | false_approval | V, A | V, 0 | -0.101 | [-0.154, -0.048] | -0.106 [-0.156, -0.065] |
| 32B AWQ | false_approval | N, A | N, 0 | -0.088 | [-0.140, -0.036] | -0.096 [-0.146, -0.049] |
| 32B AWQ | false_approval | F, A | F, 0 | -0.082 | [-0.132, -0.031] | -0.084 [-0.128, -0.043] |
| 32B AWQ | honest_acceptance | V, A | K, A | +0.042 | [-0.010, +0.093] | +0.043 [+0.000, +0.089] |
| 32B AWQ | honest_acceptance | N, A | S, A | -0.038 | [-0.096, +0.020] | -0.039 [-0.096, +0.007] |
| 32B AWQ | honest_acceptance | F, A | S, A | +0.014 | [-0.055, +0.083] | +0.014 [-0.042, +0.080] |
| 32B AWQ | honest_acceptance | K, A | S, A | -0.003 | [-0.057, +0.050] | -0.004 [-0.048, +0.048] |
| 32B AWQ | honest_acceptance | K, 0 | S, 0 | -0.014 | [-0.044, +0.017] | -0.014 [-0.043, +0.011] |
| 32B AWQ | honest_acceptance | N, 0 | S, 0 | -0.038 | [-0.071, -0.005] | -0.039 [-0.068, -0.011] |
| 32B AWQ | honest_acceptance | F, 0 | S, 0 | +0.014 | [-0.010, +0.037] | +0.014 [-0.004, +0.035] |
| 32B AWQ | honest_acceptance | S, A | S, 0 | -0.118 | [-0.195, -0.041] | -0.121 [-0.189, -0.059] |
| 32B AWQ | honest_acceptance | K, A | K, 0 | -0.108 | [-0.195, -0.021] | -0.111 [-0.191, -0.040] |
| 32B AWQ | honest_acceptance | V, A | V, 0 | -0.083 | [-0.163, -0.004] | -0.086 [-0.163, -0.025] |
| 32B AWQ | honest_acceptance | N, A | N, 0 | -0.118 | [-0.198, -0.038] | -0.121 [-0.198, -0.059] |
| 32B AWQ | honest_acceptance | F, A | F, 0 | -0.118 | [-0.187, -0.049] | -0.121 [-0.182, -0.064] |

## Per-template differences of the co-primary contrasts (false approval)

| judge | contrast | per-template differences | SD between templates | SE with 12 templates | 97.5% half-width with 12 (t = 2.593) |
|---|---|---|---|---|---|
| 14B AWQ | P1 attacker | t01: -0.100, t02: -0.133, t05: +0.094, t06: -0.192, t07: +0.021, t08: +0.086, t09: -0.057, t10: +0.000, t11: +0.061, t12: -0.050, t15: -0.246, t16: -0.029 | 0.108 | 0.031 | 0.081 |
| 14B AWQ | P2 none | t01: -0.150, t02: -0.378, t05: -0.264, t06: -0.135, t07: +0.128, t08: +0.029, t09: -0.075, t10: +0.022, t11: +0.020, t12: -0.100, t15: -0.308, t16: -0.058 | 0.151 | 0.044 | 0.113 |
| 32B AWQ | P1 attacker | t01: +0.050, t02: +0.022, t05: +0.132, t06: -0.250, t07: +0.000, t08: -0.086, t09: +0.208, t10: +0.087, t11: +0.000, t12: -0.025, t15: +0.000, t16: +0.188 | 0.124 | 0.036 | 0.093 |
| 32B AWQ | P2 none | t01: +0.050, t02: -0.044, t05: -0.057, t06: -0.077, t07: +0.021, t08: +0.057, t09: +0.019, t10: +0.043, t11: +0.082, t12: +0.025, t15: +0.031, t16: -0.116 | 0.061 | 0.018 | 0.046 |

## E1b comprehension: mean over templates of the fraction of situations judged correctly, with a 95% cluster-t interval (chance 0.50; failures score 0)

| judge | fol_symbols | fol_keywords | ve_strict | ve_natural | ve_fluent | failures |
|---|---|---|---|---|---|---|
| 14B AWQ | 0.678 [0.631, 0.724] | 0.659 [0.624, 0.694] | 0.675 [0.636, 0.713] | 0.691 [0.661, 0.721] | 0.717 [0.680, 0.754] | 11 |
| 32B AWQ | 0.830 [0.785, 0.875] | 0.827 [0.778, 0.875] | 0.842 [0.807, 0.878] | 0.859 [0.824, 0.894] | 0.878 [0.838, 0.918] | 13 |

## Descriptive breakdowns of false approval in the co-primary cells (no intervals, no decisions)

### By attack family

| judge | group | n | S, A | V, A | S, 0 | V, 0 |
|---|---|---|---|---|---|---|
| 14B AWQ | and_or_swap | 64 | 0.234 | 0.297 | 0.359 | 0.344 |
| 14B AWQ | argument_reversal | 16 | 0.500 | 0.438 | 0.875 | 0.562 |
| 14B AWQ | dropped_conjunct | 16 | 0.625 | 0.625 | 1.000 | 0.812 |
| 14B AWQ | implication_reversal | 104 | 0.308 | 0.163 | 0.548 | 0.250 |
| 14B AWQ | model:claude-fable-5-1 | 184 | 0.505 | 0.457 | 0.625 | 0.538 |
| 14B AWQ | model:gpt-6-astra | 130 | 0.523 | 0.500 | 0.631 | 0.654 |
| 14B AWQ | quantifier_swap | 32 | 0.281 | 0.031 | 0.438 | 0.000 |
| 14B AWQ | vacuous_domain | 24 | 0.958 | 1.000 | 1.000 | 1.000 |
| 14B AWQ | weakened_exception | 24 | 1.000 | 1.000 | 1.000 | 1.000 |
| 32B AWQ | and_or_swap | 64 | 0.047 | 0.000 | 0.203 | 0.188 |
| 32B AWQ | argument_reversal | 16 | 0.312 | 0.250 | 0.625 | 0.375 |
| 32B AWQ | dropped_conjunct | 16 | 0.938 | 0.375 | 0.875 | 0.750 |
| 32B AWQ | implication_reversal | 104 | 0.019 | 0.010 | 0.019 | 0.019 |
| 32B AWQ | model:claude-fable-5-1 | 184 | 0.228 | 0.277 | 0.386 | 0.359 |
| 32B AWQ | model:gpt-6-astra | 130 | 0.131 | 0.231 | 0.369 | 0.369 |
| 32B AWQ | quantifier_swap | 32 | 0.000 | 0.000 | 0.031 | 0.031 |
| 32B AWQ | vacuous_domain | 24 | 0.000 | 0.125 | 0.000 | 0.458 |
| 32B AWQ | weakened_exception | 24 | 0.250 | 0.667 | 0.708 | 0.667 |

### By direction (oracle)

| judge | group | n | S, A | V, A | S, 0 | V, 0 |
|---|---|---|---|---|---|---|
| 14B AWQ | incomparable | 209 | 0.316 | 0.215 | 0.550 | 0.330 |
| 14B AWQ | stronger | 142 | 0.627 | 0.577 | 0.725 | 0.683 |
| 14B AWQ | weaker | 243 | 0.523 | 0.510 | 0.621 | 0.560 |
| 32B AWQ | incomparable | 209 | 0.124 | 0.096 | 0.191 | 0.139 |
| 32B AWQ | stronger | 142 | 0.232 | 0.275 | 0.521 | 0.521 |
| 32B AWQ | weaker | 243 | 0.128 | 0.214 | 0.255 | 0.292 |

### By empty-sort-only attack

| judge | group | n | S, A | V, A | S, 0 | V, 0 |
|---|---|---|---|---|---|---|
| 14B AWQ | also with inhabited sorts | 553 | 0.438 | 0.387 | 0.595 | 0.474 |
| 14B AWQ | only when a sort is empty | 41 | 0.976 | 0.902 | 0.976 | 0.976 |
| 32B AWQ | also with inhabited sorts | 553 | 0.152 | 0.166 | 0.255 | 0.257 |
| 32B AWQ | only when a sort is empty | 41 | 0.146 | 0.463 | 0.854 | 0.780 |

## Exclusions, failures, provenance

- Candidates judged: 874 of 874 built (280 good, 594 bad); candidates without an explanation: 0.
- Excluded before any judge call (kind, reason: count): mech string-detectable: 128; mech type error: 64; model does not parse: 25; model duplicate: 37; model oracle UNKNOWN: 4; model unparseable reply: 2.
- No trial was excluded.
- E1, 14B AWQ: 8740 trials; failed calls 0, truncated 0, tool use 0, no valid verdict in total 0 (all scored as the worst case).
- E1, 32B AWQ: 8740 trials; failed calls 0, truncated 0, tool use 0, no valid verdict in total 0 (all scored as the worst case).
- E1b, 14B AWQ: 4370 trials; failed calls 0, truncated 0, tool use 0, no valid verdict in total 11 (all scored as the worst case).
- E1b, 32B AWQ: 4370 trials; failed calls 0, truncated 11, tool use 0, no valid verdict in total 13 (all scored as the worst case).
- PREREG: commit 555b3ae030352c7ce2bad745bc8ed97988d471dd 2026-09-21T11:06:17-07:00, blob 744b997ca7911d0e6e4faf9aa9806ef0ae40ae57; run at git 56424dabbff9dbb66dc46b3f8390645ce388d9e8.
- Compute: scored job e1-scored-0921 on one A100-80GB: 3,411 s wall, about 7.1 Colab units (14B 1,173 s, 32B 2,193 s). Dev jobs on the L4 earlier the same day: about 6.1 units.

## Covariates


Tokens are `\w+|[^\w\s]` matches (words and single symbols), not model tokens.

| view | mean chars | median chars | mean tokens | median tokens |
|---|---|---|---|---|
| fol_symbols | 92.1 | 91 | 39.6 | 38 |
| fol_keywords | 111.4 | 110 | 39.6 | 38 |
| ve_strict | 123.4 | 122 | 37.2 | 37 |
| ve_natural | 142.7 | 139 | 42.3 | 40 |
| ve_fluent | 120.4 | 116 | 27.8 | 26 |

## ve_fluent contraction

- 467/874 (53%) use a relative-clause guard on a universal (`for every N V that ...` or `such that ...`).
- 236/874 (27%) contain an uncontracted `if (...)` or `such that (both ...)`.
- By label: good: guard 148/280; bad: guard 319/594


## Development prompts and calibration
### Explanation revisions before freezing

Free-form explanations written from each candidate failed the balance gate:
stratified length SMD was -0.22 and a leave-one-template-out style-only classifier
had AUC 0.78. Recipe e2 used fixed form and length matching and passed (AUC 0.525),
but lowered false approval: for 32B symbolic FOL, about 0.31 became 0.05. An
honest structured description of the candidate could expose its weakening.

Final recipe e3 writes one asserted-faithful explanation per base item from the
requirement and faithful AST only, then uses it verbatim for every candidate.
It is true for good candidates and the overseen author's lie for bad ones. All
explanations are by `gpt-6-astra` because of Claude quota. The requested form is
three sentences, 55--65 words; code permits 50--70, with fixed openings/closing
and no formal notation. All 96 scored base items have explanations (111 samples,
15 rejected as inaccurate; observed lengths 54--63 words). Length SMD +0.005,
hedging SMD 0, and style AUC 0.469 pass the frozen thresholds: absolute SMD below
0.20 and AUC in [0.40, 0.60]. Within a base item the text carries no candidate
label information; aggregate residual imbalance reflects different candidate
counts. The style feature lists were revised twice before freezing to remove logical
content words; thresholds were unchanged.

Final e3 dev also lowered false approval in every view for both judges. One of
16 dev base items lacked an accepted explanation, leaving 104 bad and 45 good
candidates across four templates. This population differs from the gate cell.

| View | 32B FA: none to e3 | 14B FA: none to e3 |
|---|---|---|
| FOL symbols | .317 to .096 | .663 to .548 |
| FOL keywords | .308 to .135 | .596 to .481 |
| VE strict | .240 to .106 | .481 to .404 |
| VE natural | .192 to .077 | .529 to .462 |
| VE fluent | .173 to .115 | .548 to .452 |

A restated requirement may give the judge a second reference, but this is an
interpretation of dev behavior, not an identified mechanism. E3 is an untrusted
assertion condition; it did not make these judges' task harder on dev. A more
persuasive adaptive adversary remains untested.
<!-- src: paper/sources/e1-dev-qwen.md; paper/sources/e1-dev-qwen-e3.md;
paper/sources/e1-prereg-frozen.md; paper/sources/process-log-v1.md. -->

### Judge ladders and prompt-sensitive calibration (DEV only)

Calibration uses `fol_symbols` with no explanation. The primary rule requires
FA in [0.30, 0.60], HA at least 0.70, and accuracy at least five points below
the two strong-model mean (1.00). FA in (0.60, 0.85] gives a permissive secondary;
[0.10, 0.30) gives a near-floor secondary if the other conditions hold. Hosted
judges at floor are optional descriptive references. They cannot support or
refute the E1 claim. One strong reference was measured with the older JSON
legend and not remeasured because of quota.

| Prompt / serving stage | Judge | FA | HA | Calibration interpretation |
|---|---|---|---|---|
| Old prompt, local MLX 4-bit | Tested 0.5B--3B rungs | 91--100% | 81--100% | Largely approve everything; forced rungs approve all |
| Old plain-vocabulary prompt, L4 | Qwen 7B | 62/109 (.569) | 40/48 (.833) | Earlier primary-band rung |
| Old plain-vocabulary prompt, L4 | Qwen 14B AWQ | 42/109 (.385) | 47/48 (.979) | Earlier primary-band rung |
| Old plain-vocabulary prompt, L4 | Qwen 32B AWQ | 15/109 (.138) | 44/48 (.917) | Earlier near-floor rung |
| JSON legend, dev revision | Qwen 7B / 14B / 32B | .96 / .77 / .15 | Not tabulated here | None in primary FA band |
| Final compact prompt, gate cell | Qwen 7B | 94/110 (.855) | 41/48 (.854) | Not scored; above .85 |
| Final compact prompt, gate cell | Qwen 14B AWQ | 73/110 (.664) | 43/48 (.896) | Secondary-permissive |
| Final compact prompt, gate cell | Qwen 32B AWQ | 34/110 (.309) | 46/48 (.958) | Primary; one candidate inside band |
| Final compact prompt, hosted | GPT-5.6-luna | 5/110 (.045) | 48/48 (1.00) | Floor reference |
| JSON legend, hosted; not remeasured | Claude Haiku 4.5 | 4/110 (.036) | 48/48 (1.00) | Floor reference |

The roughly 4,000-character JSON legend swamped the statement; compacting it
moved the 32B gate FA from .15 to .31. The ladder is prompt-sensitive calibration,
not a stable capability ranking or scaling law. Old and final inventories also
differ (109 versus 110 bad candidates), and local/Colab quantization and serving
settings differ. Other-family ladder rungs did not qualify: Llama 8B rejected
nearly everything, Gemma 9B approved nearly everything, and Phi had substantial
response failures. Full historical counts remain in the committed source records.
Only Qwen2.5-32B-Instruct-AWQ is primary; 14B-Instruct-AWQ is exploratory,
and 7B is not scored in E1. The optional hosted scored references were not run. On these development
sign-off items, hosted small models read FOL near-perfectly (0.97 accuracy for
both hosted references); model readability is not the bottleneck here. This
is a task-specific calibration observation, not a general claim about all FOL.
<!-- src: paper/sources/local-ladder.md; paper/sources/colab-ladder.json;
paper/sources/e1-judges.json; paper/sources/process-log-v1.md. -->



## E0 frozen counts and development projections

<!-- INCLUDE generated/e0-first-table.md -->

<!-- INCLUDE generated/e0-coverage-table.md -->

<!-- INCLUDE generated/e0-agreement-table.md -->

<!-- INCLUDE generated/e0-corrections-table.md -->

<!-- INCLUDE generated/e0-constructs-table.md -->

<!-- INCLUDE generated/coverage-projection-table.md -->

<!-- INCLUDE generated/closure-witness-table.md -->

# Unrun studies

## Training study (Phase T): planned work

Phase T asks whether replacing a policy-controlled explanation with a
deterministic rendering changes the incentive to produce approved but wrong
formalizations. It has not yet run in the evidence frozen for this paper. Its
current design is a plan, not a training result or frozen preregistration.
<!-- src: design/phase-t.md, Status and Estimand; PLAN.md, Phase T. -->

A policy receives a prose requirement and a visible finite state. Some states
satisfy a tempting weakening but violate the hidden reference. Every arm emits
strict VE plus an explanation. Rewards combine output validity, approval, and a
task term based on satisfaction in the visible state. The primary manipulation
changes what the same frozen judge reads.

| Arm | Approval information | Interpretation |
|---|---|---|
| A | Policy-written explanation | Policy controls the explanatory channel. |
| B' | Deterministic VE rendering | Presentation intervention without reference-linked checking in approval. |
| F' | Deterministic keyword FOL | Control for exposing the same formal content without VE wording. |
| R | Matched random approval | Optimization control. |
| B | B' plus scenario tests | Privileged reference-linked baseline. |
| C | Hidden scenarios and two-way reference check | Privileged baseline sharing oracle machinery with evaluation. |

<!-- src: design/phase-t.md, Estimand; supersedes the earlier ceiling terminology
in PLAN.md and design/phase-t-literature.md. -->

The primary comparison is the change from a shared supervised baseline in
approved-and-wrong probability for B' versus A. B' versus F' is needed for a
VE-specific claim. The design also reports wrong-output probability, approval
conditional on wrongness, and approved-and-equivalent probability. Conditional
false approval alone can mislead when training changes which outputs are wrong.
All arms are cross-scored under each presentation, with held-out templates,
renamed vocabulary, distinguishing models, and a separate judge panel.
Reference-linked baselines are not independent gold standards or guaranteed
ceilings.

| Planned training safeguard | Value or decision |
|---|---|
| Selection probe | Best-of-n, n from 1 through 32 |
| Primary replication | 5 paired seeds per arm |
| Paired development RL pilot | 2 seeds, 60 steps |
| Main run length in design | 200 optimizer steps |
| Rollout audit | 100 per arm by strong models; proposed human spot-check is not completed |
| Spend ceiling in plan | 150 Colab compute units |

<!-- src: design/phase-t.md, Gates, Optimization, Inference and Budget;
PLAN.md, Phase T. All figures are plans, not measured costs or completed runs. -->

Before training, the policy must demonstrate faithful-output competence and a
nondegenerate reward signal. A best-of-n probe demonstrates selection pressure,
not learnability. The paired pilot must show inducible false approval before a
main comparison is informative. The final design must freeze power assumptions,
KL budget, checkpoint selection, usefulness constraint, and equivalence margin.
UNKNOWN outcomes retain both extreme assignments.

The original small-judge choices cannot simply be carried forward: the later E1
ladder found largely indiscriminate approval on its tested small open rungs.
Those results do not test every proposed training judge, but they require renewed
calibration on the actual training task and stack. Grammar-constrained generation
can enforce form; it cannot ensure faithfulness. The implemented oracle also
certifies both directions for identical ASTs, superseding the early plan's hash
shortcut wording. No throughput, GPU choice, or training benefit is established
by the budget estimates.
<!-- src: design/phase-t.md; paper/sources/local-ladder.md; docs/oracle.md. -->

The competence and exploitation gate, paired pilot, and end-to-end training run have not been executed.

Main training, cross-scoring, transfer, rollout audits, and seed-level uncertainty have not been executed.


## E5: materials and pilots only; scored run not executed

E5 holds deduction validity fixed while varying grounding and its display.
Bad-grounding families cover merged vocabulary, unsupported leaves, scope
mismatch, and stale evidence; labels derive from explicit records and scopes.
Its draft primary contrast is false approval with a truthful conditional-proof
badge minus approval without the badge. Invalid-edge controls remain separate.

| Cell | Display intervention |
|---|---|
| a | Argument and records |
| b | a plus truthful conditional-proof badge |
| c | b plus remaining leaf obligations and raw scopes |
| d | c plus predicate-use references into the same records |
| e | d plus supplied and declared sense tags |

The generated inventory has 3,072 items (768 dev, 2,304 reserved for scoring),
eight dev and 24 scored structural templates, three construction difficulty
levels, and two instruction styles. These are material counts, not completed
judgments. Panels omit mechanical mismatch verdicts. Honest/forged tags and
stale evidence require separate reporting. A revised duplication-signature
audit addressed a structural shortcut; its chance bound covers only the audited
features, not all classifiers or semantic leakage.

On medium, neutral-instruction Colab dev, Qwen 7B approved all 64 bad and all
64 good items in each of the five cells. The 14B job was incomplete, with 98
of 128 outputs missing per cell; worst-case scores would mainly measure missing
execution. 32B was not run. An earlier hosted Haiku pilot on reviewed materials
had medium cell-a FA 8/20 (.40) and HA 19/20, inside the behavioral calibration
band; it preceded the final structural-shortcut revision. The study was deferred
because thousands of long hosted calls did not fit the remaining quota and no
affordable completed local pilot supplied an informative judge. E5 therefore
has no scored badge-harm or panel-protection estimate. This is a resource and
calibration limit, not evidence of no effect.
<!-- src: paper/sources/e5-materials-pilots.md; paper/sources/process-log-v1.md. -->

## E2: not run; context preflight observation

E2 would compare direct review against checked VE and checked structured-FOL
arms as derivations grow, retaining errors outside checker visibility. The dev
job was refused before inference: 72 of 432 prompts exceeded its 24k-token
preflight setting. At size 256, direct-review prompts were about 40k tokens,
above the selected judges' native 32k context; checker arms were about 25k.
These are descriptive prompt-size observations, not accuracy, scalability, or
oversight results. No E2 judged outcome is available. A future run needs smaller
sizes (for example 4/32/128) or a longer-context judge, plus renewed preflight.
<!-- src: paper/sources/process-log-v1.md, 08:44. -->


# Implementation benchmarks



The committed corpora provide the following development evidence. Overlapping
fixtures are not independent samples. Python generates the semantic golden
values; executable agreement is differential evidence, not a refinement proof.

<!-- INCLUDE generated/conformance-table.md -->

The certificate corpus includes schema-generated valid queries, unconditioned
queries, and regressions. All search attempts remain recorded, including failed
searches and resource outcomes. Many valid certificates share schemas, and many
forgeries mutate the same simple base. Acceptance and rejection counts cannot
be read as an error rate on independently sampled adversarial certificates.
<!-- src: conformance/certificates-report.json; conformance/certificates.py;
paper/sources/review-lean.md. -->

Rust is a separately implemented and differentially tested core for both the
base and closure profiles. Its closure stream records 3,000/3,000 formula/model
agreements with Python, also agreeing on identities. Safe Rust restrictions
do not prove logical correctness. Rust still supplies neither certificate replay
nor claim-graph composition.
<!-- src: rust/closure-fuzz-summary.json; docs/rust.md. -->
The honest performance summary is roughly 20-30x on the evaluation kernel,
about thirtyfold on the two largest measured workloads shown below.
<!-- src: docs/rust.md; rust/benchmark-results.json; docs/spec/closure-implementation.md. -->

<!-- INCLUDE generated/rust-table.md -->

The benchmark evaluates already-validated inputs, excludes startup and JSON
setup, and disables traces in both implementations. Its nested universal workload
forces relation visits. Public API ratios additionally reflect Python's repeated
validation and hashing, so they are not kernel speedups. The run was serial on a
shared, loaded machine; the recorded samples are workload-specific observations,
not isolated estimates of general throughput or programming-language advantage.
Separate closure workloads on a 12-vertex cycle record kernel ratios of 5.38
for Named edges and 15.01 for Body edges, with five samples per workload; these
do not inherit the base evaluator's approximately thirtyfold characterization.
<!-- src: rust/closure-benchmark-results.json; docs/rust.md. -->
<!-- src: rust/benchmark.py; rust/benchmark-results.json; docs/rust.md. -->


# Process disclosure

The project was organized around a Claude-side worker and a GPT-side worker,
with additional task-specific AI instances, under a Claude-side AI orchestrator.
The human user set the objective, changed scope, supplied compute access, and
requested review. The protocol required cross-family review before integration
merges. The log records review requests, rejected merges, revisions, and
integration failures. This is a production record, not a controlled comparison
of development methods. This drafting pass used GPT-6 Astra after the Claude
scaffold author exhausted quota; a Claude-side manuscript audit was performed and its findings are
recorded in `paper/AUDIT.md`.
<!-- src: PROTOCOL.md; paper/sources/process-log-excerpts.md;
paper/sources/manifest.json; user drafting handoff recorded in paper/README.md. -->

The following defects illustrate what review actually caught. Counts from the
external orchestrator log are preserved as reported observations, not independent
reruns by the paper author.

| Defect caught | Consequence and recorded response |
|---|---|
| Judges could read ground truth from disk | The initial CLI harness retained tools. Prompt separation therefore did not isolate labels. Review required disabling tools and invalidating tool-using trials. |
| Cache collapsed repeated samples | Repeated assignments could reuse a response instead of obtaining the intended new sample. Review required trial-specific cache identity and explicit repeat handling; a cache replay is not an independent draw. |
| Converse template in the natural view | A relation such as `owns(person, service)` accepted wording like `{0} is owned by {1}`. The apparent direction could change only in the natural display. Revised lexical checks and a common identity-bearing legend narrowed this attack surface. Arbitrary semantic lies remain possible. |
| Unfair universal-rule scheduling | Early gamma choices repeatedly used some instances and starved useful witnesses. Semantically equivalent formulas became UNKNOWN. Fair bounded rounds and connection priorities changed search, while replay rules remained fixed. |
| Certificate-version mismatch after merges | Python's oracle introduced compound-formula closure before the Lean adapter supported that certificate version. Separately reviewed branches failed integration. The fix proved the existing rule in Lean, aligned decoding depth, repaired fixture naming, and added regressions. |
| Structural shortcut in E5 | An uncited dossier unmatched by any cited dossier revealed the label despite lexical balancing. Revision changed copy construction and added a duplication-signature audit over the enumerated features; fresh model calibration remains necessary. |

<!-- src: paper/sources/process-log-excerpts.md, entries 01:03, 01:24, 02:11,
02:48, 03:10, 03:50; paper/sources/review-views.md; docs/rendering-views.md;
docs/prover-fair-report.md; docs/integration-fix-report.md;
paper/sources/e5-prereg-draft.md. -->

Further episodes affected both measurement and scheduling:

| Episode | Consequence and response |
|---|---|
| JSON legend swamped the statement | The roughly 4,000-character legend put all tested Qwen judges outside the primary FA gate. A compact, common legend replaced it, and calibration was rerun before freezing. |
| Explanation balance failed | A style-only classifier distinguished labels (AUC .78), and length SMD was -.22. Fixed-form e2 passed but helped judges detect bad statements. Final e3 asserts one faithful reading verbatim across each base item's candidates; it also lowered FA on dev. |
| Genuine instruction treated as possible injection | A worker ignored an actual orchestrator message because it arrived inside tool output. The orchestrator resent it as a task message and work resumed. The delivery channel made legitimate coordination resemble untrusted content. |
| Usage-limit outage | The 04:00--04:50 Claude session limit interrupted the paper, Colab, and implementation workers. The orchestrator reduced Claude concurrency and moved drafting/build work to the separately metered GPT worker. |
| Colab idle shutdown and restart | Runtime idling required restart and dependency restoration; missing `ninja` blocked dev jobs, and E5 prompts also exceeded the initial context setting. Jobs were resubmitted after installation and revised preflight. A later queue/watchdog stall cost roughly two hours before orchestration resumed. |

The E5 duplication shortcut and certificate-version mismatch in the earlier
table remain relevant: structural balance did not guarantee task validity, and
separately reviewed changes did not guarantee a compatible integrated checker.
E1's later cross-review also required isolated CLI settings, routing E1b through
the common runner, enforced oracle/balance gates, and invalidation of truncated
or tool-using trials before parsing. These changes preceded the scored freeze.
<!-- src: paper/sources/process-log-excerpts.md; paper/sources/process-log-v1.md;
paper/sources/process-operations.md; paper/sources/e1-prereg-frozen.md. -->

The quantitative context is deliberately separated by audit population:

| Process observation | Reported count or rate | Evidential status |
|---|---|---|
| Reviewer's oracle distribution, before scheduling fix | 10.9% UNKNOWN overall; 32% at depth at least 3 | External log report, not the public paired benchmark |
| Committed paired scheduling benchmark | 237/602 UNKNOWN before; 2/602 after | Synthetic development suite, including timeouts |
| E5 shortcut on reviewed spread items | 384/384 identified | External review observation on superseded material |
| Revised E5 duplication-signature feature bound | 0.50 best accuracy | Finite-inventory structural audit described in revision; not a semantic-classifier bound |

<!-- src: paper/sources/process-log-excerpts.md, 02:11 and 03:50;
docs/prover-fair/before.json; docs/prover-fair/after.json;
paper/sources/e5-prereg-draft.md, offline leak audit.
Do not compare the private 10.9% distribution to the 602-pair benchmark as one experiment. -->

These examples show that cross-family review detected concrete mistakes in
semantics, measurement, and integration. They do not measure how many defects
remained, prove that another family was necessary, or show that AI review can
replace expert human judgment. In particular, a theorem can be valid about an
unfaithful formal definition, and both reviewers can accept the same bad
translation. Tests and theorem checking reduce specific uncertainties; review
must still inspect the statements and measurement contracts.

## Compute and cost

Colab accounting is approximate. The table distinguishes orchestrator and runner
estimates from recorded runtime fields and from a metered bill, which is
unavailable.

| Work | Accelerator | Colab compute units | Provenance / scope |
|---|---|---|---|
| Development before scored runs | L4 | About 12 | Orchestrator estimate from runner uptime times the nominal L4 rate (1.7 units/hour); includes earlier development; neither a Colab bill nor a user report. |
| E1 scored, including E1b | A100-80GB | About 7.1 | Runner estimate at 7.5 units/hour; 3,411 s recorded wall time. |
| E4 scored | A100-80GB | Not reported in the cited log | The supplied under-2 estimate could not be traced; see below. |

The E1 result report separately lists about 6.1 units for that day's earlier
L4 development jobs; this narrower accounting is not substituted for the
about-12 pre-scoring orchestrator estimate. E1 completed 26,220 prompts across sign-off
and E1b; E4 completed 720. E4 manifests record load/generation times of
76.9/959.11 s for 14B and 103.9/32.31 s for 7B. Summing those recorded phases
and applying 7.5 units/hour gives about 2.44 units, a derived runtime proxy
that excludes other overhead and is not a bill. It does not substantiate the
supplied under-2 estimate, so no combined cost total is asserted.

E4 manifests report 101,823 input tokens per judge and output counts of
116,832 (14B) and 2,520 (7B); these are runner fields, not an independently
audited token ledger. E1's committed report supplies text-token proxies but
no actual tokenizer usage. Local MLX pilots, hosted generation, and review
used separate resources without a complete dollar ledger. Quota limits shaped
the single-family scored roster and the decision not to execute E5. Units are
not converted to dollars using an assumed purchase price.
<!-- src: paper/sources/v1-handoff.md (about 12 units; provenance corrected by the
user in the audit-resolution handoff: orchestrator estimate from runner uptime
times the nominal L4 rate of 1.7 units/hour, not a user report or Colab bill);
paper/sources/e1-results.md (3,411 s, about 7.1 units, narrower 6.1-unit dev
estimate, assigned/completed prompts); paper/sources/process-log-results.md
(runner estimate of 57 min and about 7.1 units);
paper/sources/e4-score-summary.json, provenance manifests (phase times and
tokens). Derived E4 proxy: (76.9+959.11+103.9+32.31)/3600*7.5 = 2.442125.
The under-2 figure in the drafting request is not present in the cited log. -->
