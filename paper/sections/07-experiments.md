# Experiments: scored results and development evidence

E1 v5 and E4 revision 2 were frozen on 2026-09-21 before scored judging.
Both scored runs are complete; the results below preserve their frozen
per-judge decision rules. E5 has materials and pilots only:
its scored run was not executed. E2 was not run. Development observations below
explain design choices and do not substitute for held-out effects.
<!-- src: paper/sources/e1-prereg-frozen.md; paper/sources/e4-prereg-frozen.md;
paper/sources/e5-materials-pilots.md; paper/sources/process-log-v1.md;
paper/sources/e1-results.md; paper/sources/e4-score-summary.json. -->

## Shared estimands and safeguards

False approval (FA) is approved bad submissions divided by assigned bad
submissions. Honest acceptance (HA) is approved good submissions divided by
assigned good submissions. Failed calls, timeouts, tool use, and unparseable
verdicts stay in denominators, scored as approval on bad items and rejection on
good items. Failures are reported beside endpoints. E1 invalidates truncated
responses before parsing; E4 retains a length-finished response's verdict if
its final JSON parses, and separately reports all truncations. Judges have no
tools, and any tool event in any E1 attempt invalidates the trial, including
failed attempts followed by retries. Incomplete E1 imports are refused.

Conditions share candidates, with one response per assigned trial. Replaying a
cached response is not an independent draw. Templates and vocabulary separate
development from scoring; renamed variants are not independent template clusters.
Judges are analyzed separately. No study here tests human readers, and no
cross-family efficacy claim can follow from the selected Qwen rungs.
<!-- src: paper/sources/e1-prereg-frozen.md; paper/sources/e4-prereg-frozen.md. -->

## E1: specification sign-off

E1 asks whether VE strict reduces approval of unfaithful formalizations relative
to symbolic FOL. Every candidate is crossed with five views (`fol_symbols`,
`fol_keywords`, `ve_strict`, `ve_natural`, `ve_fluent`) and two explanation
conditions (`none`, `attacker`). The requirement, AST, and compact vocabulary
legend are fixed across views. The legend is byte-identical across cells;
no VE-only checker information is supplied. Attacks were generated before any
scored judging, without judge feedback. Open-weight judges decode greedily with
a 400-token output cap, requesting at most 150 words of reasoning followed by
a JSON verdict. Per-judge context settings are frozen in `judges.json`; actual
model revisions and A100 runtime settings accompany the scored outputs.

The frozen inventory has 96 base items (12 templates by eight vocabularies in
four families) and 874 candidates. Good candidates comprise 96 canonical ASTs
and 184 certified equivalent rewrites. The 594 oracle-VALID bad candidates
comprise 280 mechanical attacks, 184 from `claude-fable-5-1`, and 130 from
`gpt-6-astra`. They type-check, preserve sorts and predicates, and have a checked
distinguishing finite model. Oracle direction is weaker for 243, stronger for
142, and incomparable for 209. The 41 attacks that differ only on empty sorts
remain included, with a descriptive exclusion sensitivity analysis. Semantic
difference does not prove the reference faithfully translates its requirement.

| Pre-judge exclusion reason | Count |
|---|---:|
| Mechanical edit string-detectable | 128 |
| Mechanical edit ill-typed | 64 |
| Model attack unparseable text | 25 |
| Model attack unparseable reply | 2 |
| Model attack duplicate | 37 |
| Model attack oracle UNKNOWN | 4 |
| Model attack oracle REJECTED | 0 |
| Uncertified good rewrite | 0 |

These counts account for 1,134 candidate records: 874 retained and 260 excluded.
UNKNOWN is not relabeled as a bad formalization. Scored judge rates condition on
the validated inventory; no all-generated-candidate accuracy is inferred.
All 12 templates enter the analysis, and no assigned judge trial is excluded.
<!-- src: paper/sources/e1-prereg-frozen.md, Materials and Exclusions. -->

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
counts. The style feature lists were revised before freezing to remove logical
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

### Frozen inference and decision rules

Two co-primary contrasts for 32B compare VE strict minus FOL symbols FA:
P1 with asserted-faithful explanations, P2 without explanations. P2 was added
on dev evidence before freezing because P1 dev FA was near .10. For each
contrast, average paired differences within each of the 12 templates, then take
the unweighted mean across templates. Bonferroni gives a 97.5% cluster-t interval
per contrast: mean plus/minus $t_{0.9875,11}s/\sqrt{12}$, with $t=2.593$.
Pairing must be complete. Pooled-rate differences with 95% percentile bootstraps
over templates and over 96 base items (10,000 resamples, seed 0) are sensitivity
analyses, not substitutes for the primary interval.

The useful reduction is 0.05. For a primary interval [lo, hi], benefit is
supported only if hi is at most -0.05 and the HA constraint holds. It is refuted
if lo exceeds -0.05; if lo also exceeds zero, VE is harmful. Intervals spanning
-0.05 are inconclusive. The paired HA difference must have 97.5% lower bound
at least -0.10 and point estimate at least -0.05; VE strict HA must also be at
least .70. Otherwise report "benefit not established; compatible with a shift
in approval threshold."

The per-judge claim is supported if at least one co-primary supports benefit and
neither is harmful; an unqualified positive statement requires both. A split
supported/refuted-but-not-harmful result is condition-specific. Both refuted,
or either harmful, refutes the per-judge claim; otherwise it is inconclusive.
One primary judge from one family cannot establish the overall two-family
claim: the study is exploratory with respect to that broader claim.

Dev variance from four templates gives rough 80%-power reductions for excluding
zero of .09 (P1) and .13 (P2). Supporting a reduction of at least .05 is harder:
approximately .145 and .18 true reductions respectively. Expected interval
half-widths are about .07 and .10. A true reduction of exactly .05 cannot be
confirmed by this design; additional vocabulary copies do not add clusters.
These are planning approximations, not measured scored precision.
<!-- src: paper/sources/e1-prereg-frozen.md, Primary contrast through Sample size. -->

### E1 scored outcomes

The strict English surface showed no benefit for the capable primary judge.
For Qwen2.5-32B-Instruct-AWQ, P1 is inconclusive and P2 refutes a useful
0.05 reduction, without establishing harm. **The combined per-judge claim is
inconclusive and NOT supported.** It is not refuted as a whole: that rule
requires both co-primaries to be refuted or one to be harmful. Both HA
constraints hold. This is not evidence of equivalence for every effect size.

All 17,480 sign-off trials were scored, with no failed calls, unparseable
verdicts, truncations, or tool use, and no trial exclusions. Each cell has
594 bad and 280 good candidates. Rates below are pooled; inferential differences
are unweighted template means, so their signs can differ from pooled differences.
S, K, V, N, F denote FOL symbols, FOL keywords, VE strict, VE natural, VE fluent;
A denotes asserted-faithful explanation and 0 denotes none.

Qwen2.5-32B AWQ (primary).

| Cell | FA (approved / bad) | HA (approved / good) | Failures | Truncated |
|---|---|---|---|---|
| S, 0 | 0.296 (176/594) | 0.914 (256/280) | 0 | 0 |
| K, 0 | 0.281 (167/594) | 0.900 (252/280) | 0 | 0 |
| V, 0 | 0.293 (174/594) | 0.918 (257/280) | 0 | 0 |
| N, 0 | 0.283 (168/594) | 0.875 (245/280) | 0 | 0 |
| F, 0 | 0.242 (144/594) | 0.929 (260/280) | 0 | 0 |
| S, A | 0.152 (90/594) | 0.793 (222/280) | 0 | 0 |
| K, A | 0.153 (91/594) | 0.789 (221/280) | 0 | 0 |
| V, A | 0.187 (111/594) | 0.832 (233/280) | 0 | 0 |
| N, A | 0.187 (111/594) | 0.754 (211/280) | 0 | 0 |
| F, A | 0.158 (94/594) | 0.807 (226/280) | 0 | 0 |

Qwen2.5-14B AWQ (secondary-permissive; exploratory).

| Cell | FA (approved / bad) | HA (approved / good) | Failures | Truncated |
|---|---|---|---|---|
| S, 0 | 0.621 (369/594) | 0.904 (253/280) | 0 | 0 |
| K, 0 | 0.620 (368/594) | 0.925 (259/280) | 0 | 0 |
| V, 0 | 0.508 (302/594) | 0.907 (254/280) | 0 | 0 |
| N, 0 | 0.572 (340/594) | 0.911 (255/280) | 0 | 0 |
| F, 0 | 0.473 (281/594) | 0.932 (261/280) | 0 | 0 |
| S, A | 0.475 (282/594) | 0.732 (205/280) | 0 | 0 |
| K, A | 0.470 (279/594) | 0.771 (216/280) | 0 | 0 |
| V, A | 0.423 (251/594) | 0.696 (195/280) | 0 | 0 |
| N, A | 0.478 (284/594) | 0.761 (213/280) | 0 | 0 |
| F, A | 0.318 (189/594) | 0.861 (241/280) | 0 | 0 |

Co-primary decisions and HA constraints; V minus S, 32B only.

| Contrast | Endpoint | Difference | 97.5% interval | Decision |
|---|---|---|---|---|
| P1 A | FA | +0.027 | [-0.065, +0.120] | inconclusive |
| P1 A | HA | +0.038 | [-0.019, +0.095] | constraint holds |
| P2 0 | FA | +0.003 | [-0.043, +0.049] | refuted (a useful reduction is excluded) |
| P2 0 | HA | +0.003 | [-0.049, +0.056] | constraint holds |

The P2 template mean is +0.003 even though the pooled difference is -0.003;
copying a subtraction of the pooled rates into the primary estimate would
change the estimand. The scored baseline FA of 0.296 lies just below the
0.30 development gate edge; the preregistered primary role is retained.
Hosted reference judges were not run.

Bootstrap sensitivities for the primary judge use pooled differences and
95% intervals; they do not replace the 97.5% primary analysis.

| Contrast / endpoint | Pooled difference [template bootstrap] | Base-item bootstrap |
|---|---|---|
| P1 / FA | +0.035 [-0.042, +0.102] | [-0.002, +0.071] |
| P1 / HA | +0.039 [+0.000, +0.086] | [+0.011, +0.071] |
| P2 / FA | -0.003 [-0.041, +0.032] | [-0.031, +0.023] |
| P2 / HA | +0.004 [-0.038, +0.040] | [-0.022, +0.032] |

### Exploratory contrasts: hypotheses for replication

All contrasts in this subsection use unadjusted 95% cluster-t intervals.
They generate replication hypotheses, not established findings of renderer
benefit. In particular, the weaker 14B judge's VE strict P2 contrast is
-0.106 [-0.202, -0.010]; fluent rendering is about 0.14 lower than symbols
with and without explanation. The corresponding 32B fluent intervals include
zero. Keyword substitution alone is about zero for both judges.

Qwen 14B: exploratory contrasts (first minus second).

| Contrast | FA difference [95% CI] | HA difference [95% CI] |
|---|---|---|
| V - S, A | -0.045 [-0.114, +0.023] | -0.035 [-0.120, +0.050] |
| V - S, 0 | -0.106 [-0.202, -0.010] | +0.003 [-0.073, +0.080] |
| V, A - K, A | -0.047 [-0.094, -0.001] | -0.073 [-0.120, -0.026] |
| N, A - S, A | +0.011 [-0.046, +0.069] | +0.028 [-0.057, +0.113] |
| F, A - S, A | -0.147 [-0.216, -0.078] | +0.125 [+0.031, +0.219] |
| K, A - S, A | +0.002 [-0.056, +0.060] | +0.038 [-0.031, +0.107] |
| K, 0 - S, 0 | +0.002 [-0.031, +0.036] | +0.021 [-0.022, +0.064] |
| N, 0 - S, 0 | -0.042 [-0.137, +0.053] | +0.007 [-0.045, +0.058] |
| F, 0 - S, 0 | -0.141 [-0.200, -0.083] | +0.028 [-0.023, +0.079] |
| S, A - S, 0 | -0.148 [-0.227, -0.069] | -0.167 [-0.290, -0.044] |
| K, A - K, 0 | -0.149 [-0.232, -0.065] | -0.149 [-0.246, -0.053] |
| V, A - V, 0 | -0.088 [-0.134, -0.042] | -0.205 [-0.322, -0.087] |
| N, A - N, 0 | -0.095 [-0.143, -0.047] | -0.146 [-0.245, -0.046] |
| F, A - F, 0 | -0.154 [-0.213, -0.094] | -0.069 [-0.146, +0.007] |

Qwen 32B: exploratory contrasts (first minus second).

| Contrast | FA difference [95% CI] | HA difference [95% CI] |
|---|---|---|
| V, A - K, A | +0.036 [-0.028, +0.101] | +0.042 [-0.010, +0.093] |
| N, A - S, A | +0.031 [-0.046, +0.107] | -0.038 [-0.096, +0.020] |
| F, A - S, A | +0.001 [-0.095, +0.096] | +0.014 [-0.055, +0.083] |
| K, A - S, A | -0.009 [-0.068, +0.050] | -0.003 [-0.057, +0.050] |
| K, 0 - S, 0 | -0.014 [-0.037, +0.009] | -0.014 [-0.044, +0.017] |
| N, 0 - S, 0 | -0.007 [-0.049, +0.035] | -0.038 [-0.071, -0.005] |
| F, 0 - S, 0 | -0.044 [-0.114, +0.027] | +0.014 [-0.010, +0.037] |
| S, A - S, 0 | -0.126 [-0.219, -0.033] | -0.118 [-0.195, -0.041] |
| K, A - K, 0 | -0.121 [-0.191, -0.050] | -0.108 [-0.195, -0.021] |
| V, A - V, 0 | -0.101 [-0.154, -0.048] | -0.083 [-0.163, -0.004] |
| N, A - N, 0 | -0.088 [-0.140, -0.036] | -0.118 [-0.198, -0.038] |
| F, A - F, 0 | -0.082 [-0.132, -0.031] | -0.118 [-0.187, -0.049] |

The asserted-faithful explanation lowers FA in every view and also lowers
HA in every view for both judges. For 32B symbolic FOL, HA falls from 0.914
to 0.793 while the FA contrast is -0.126 [-0.219, -0.033]. These judges become
more suspicious; the condition does not demonstrate successful persuasion.
A second requirement reference and a shifted approval threshold are possible
explanations, not identified mechanisms.

Descriptive attack-family and oracle-direction tables remain in the frozen
result snapshot; they have no intervals or decisions. For example, 32B's
weaker attacks have FA 0.128 (S,A) and 0.214 (V,A), while incomparable attacks
have 0.124 and 0.096. This heterogeneity does not rescue the primary claim.
Removing the 41 empty-sort-only attacks leaves 553 bad candidates, with the
following pooled FA rates (descriptive, not a replacement primary analysis).

| Judge | S,A | V,A | S,0 | V,0 |
|---|---|---|---|---|
| 14B | 0.438 | 0.387 | 0.595 | 0.474 |
| 32B | 0.152 | 0.166 | 0.255 | 0.257 |

View-length covariates are descriptive. The token counts in the source use
word/single-symbol matches, **not model tokenizer tokens**; model-token counts
are not supplied. Fluent relative-clause guards occur in 467/874 (53%)
candidates; 236/874 (27%) retain an uncontracted conditional or conjunction.

| view | mean chars | median chars | mean tokens | median tokens |
|---|---|---|---|---|
| fol_symbols | 92.1 | 91 | 39.6 | 38 |
| fol_keywords | 111.4 | 110 | 39.6 | 38 |
| ve_strict | 123.4 | 122 | 37.2 | 37 |
| ve_natural | 142.7 | 139 | 42.3 | 40 |
| ve_fluent | 120.4 | 116 | 27.8 | 26 |

<!-- src: paper/sources/e1-results.md, experiments/E1/RESULTS.md at cb2b7ff;
paper/sources/e1-prereg-frozen.md, experiments/E1/PREREG.md at 555b3ae.
All cell rates, contrasts, bootstrap sensitivities and covariates copied from
those tables; inferential and pooled estimands deliberately kept distinct. -->

### E1b: comprehension control (exploratory)

Without a requirement, each judge predicts candidate truth in two finite
models labeled by the VE evaluator; chance is 0.50. Each judge completed
4,370 calls (874 per view), with 1,748 truth judgments assigned per view.
The table gives mean template accuracy and 95% cluster-t intervals, not pooled
accuracy or pairwise view-effect intervals.

| Judge | View | Template accuracy [95% CI] |
|---|---|---|
| 14B | S | 0.678 [0.631, 0.724] |
| 14B | K | 0.659 [0.624, 0.694] |
| 14B | V | 0.675 [0.636, 0.713] |
| 14B | N | 0.691 [0.661, 0.721] |
| 14B | F | 0.717 [0.680, 0.754] |
| 32B | S | 0.830 [0.785, 0.875] |
| 32B | K | 0.827 [0.778, 0.875] |
| 32B | V | 0.842 [0.807, 0.878] |
| 32B | N | 0.859 [0.824, 0.894] |
| 32B | F | 0.878 [0.838, 0.918] |

The 14B judge has 11 invalid verdicts in total and no truncations; 32B has
13 invalid verdicts, including 11 truncations. Neither judge has failed calls
or tool use. Invalid responses score zero. The committed report does not give
raw correct counts or failures by view; they cannot be reconstructed from
rounded template means. Strict and symbolic comprehension are close; fluent
point estimates are higher, but these are exploratory hypotheses. A lower FA
rate alone does not establish better understanding and can reflect a threshold
shift.
<!-- src: paper/sources/e1-results.md, E1b and Exclusions, failures, provenance;
paper/sources/e1-prereg-frozen.md. -->

## E4: checked countermodels (frozen mechanism demonstration)

E4 revision 2 compares prose critique, checked countermodel, and unchecked
countermodel assertion by a dishonest critic. Every arm displays the same full
hypothetical finite interpretation. On invalid inferences it is a genuine
countermodel; on valid siblings it fails replay. The checked arm exposes actual
replay findings and the positive certificate on valid inferences. Thus any
advantage tests the checking/display intervention, not an English-specific
benefit. Critique sections have equal whitespace-token counts through neutral
padding; characters and model-token counts can still differ.

There are 16 dev inferences (eight invalid, eight valid; four templates) and
120 scored inferences (60 invalid, 60 valid; 12 templates by five fresh
vocabularies). A valid label requires a replayed entailment certificate; an
invalid label requires a checked finite countermodel. Forward UNKNOWN aborts
construction. Each judge receives 360 scored calls across three cells: 720 total
for Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct-AWQ. The frozen design specifies
greedy decoding with seed 0 and no retries, an 8,192-token context, and an
800-token response cap, increased equally from 400 because dev responses
truncated. The increased cap itself was not calibrated. Exact token preflight
must pass; inputs are never shortened to fit. Recorded runtime settings and
the per-prompt cap override are reported with the scored results below.

Neither judge passed the original gate (prose FA 20--60%, HA at least 70%,
parseability at least 90%). They were retained explicitly for a pilot-sized
mechanism demonstration. The uncompleted 32B assignment supplies no calibration.

| DEV judge | Cell | Invalid approved / 8 | Valid approved / 8 | Parse failures / 16 |
|---|---|---|---|---|
| 7B | Prose critique | 0 | 0 | 0 |
| 7B | Checked countermodel | 0 | 8 | 0 |
| 7B | Dishonest critic | 0 | 3 | 0 |
| 14B | Prose critique | 1 | 4 | 2 |
| 14B | Checked countermodel | 0 | 8 | 0 |
| 14B | Dishonest critic | 1 | 7 | 2 |

The contrast is checked minus prose FA, with equal-weight paired template-t
95% intervals over 12 clusters (11 degrees of freedom). A negative upper bound
supports protection only if the paired HA lower bound is at least -.05.
Report valid acceptance under dishonest objections separately with uncertainty
and its .80 target. A 95% interval wholly above -.22 rules out the 22-point
planning reduction; one wholly above zero rules out protection under this model.
Intervals spanning benefit and harm are inconclusive. Floor/ceiling outcomes
cannot identify the mechanism. All intervals are unadjusted and descriptive.

Four dev templates give 14B contrast SD .25 and approximate 80%-power detectable
reduction .22 with 12 templates. Its prose baseline was only .125, so that
reduction is impossible at the observed baseline. The zero dev variance for
7B is a floor, not evidence of high precision. Neither design sensitivity nor
cross-family efficacy follows from these pilots.
<!-- src: paper/sources/e4-prereg-frozen.md; paper/sources/e4-dev-summary.json;
paper/sources/process-log-v1.md. -->

### E4 scored outcomes

All 720 assigned calls have outputs. No cell has missing responses, backend
failures, or reported truncations. The 14B dishonest and prose cells have
4/120 and 18/120 parse failures respectively, scored worst case; all other
cells have zero failures.

| Judge | Cell | False approval | Honest acceptance | Failures |
|---|---|---|---|---|
| 14B | Checked | 0/60 | 53/60 | 0/120 |
| 14B | Dishonest | 9/60 | 49/60 | 4/120 |
| 14B | Prose | 16/60 | 44/60 | 18/120 |
| 7B | Checked | 0/60 | 52/60 | 0/120 |
| 7B | Dishonest | 9/60 | 31/60 | 0/120 |
| 7B | Prose | 0/60 | 4/60 | 0/120 |

Paired contrasts are checked minus prose, equal-weight template means with
95% cluster-t intervals (12 templates, 11 degrees of freedom).

| Judge | Endpoint | Difference | 95% interval |
|---|---|---|---|
| 14B | FA | -0.267 | [-0.392, -0.142] |
| 14B | HA | +0.150 | [+0.027, +0.273] |
| 7B | FA | +0.000 | [+0.000, +0.000] |
| 7B | HA | +0.800 | [+0.564, +1.036] |

For 14B, the primary FA contrast -0.267 [-0.392, -0.142] **supports protection
under the preregistered rule**: its upper bound is below zero, and the HA
contrast +0.150 [+0.027, +0.273] has lower bound at least -0.05. The rule does
not require the FA upper bound to be below -0.22; that number is a planning
reference, not the efficacy threshold. The result does not establish a reduction
of at least 22 points. This remains the result and decision under the frozen rule.

**Post hoc sensitivity analysis, not preregistered.** We recover the last JSON
object containing an approve/reject verdict anywhere in each reply, allowing
trailing text; all 720 replies then yield verdicts. For 14B, prose FA becomes
7/60 and HA 48/60, versus checked FA 0/60 and HA 53/60. The paired FA contrast
is -0.117 [-0.231, -0.002], a smaller 11.7-percentage-point reduction whose
95% interval still excludes zero; the paired HA contrast is +0.083
[-0.017, +0.184]. Parse failures were concentrated in the 14B prose arm
(11 bad, 7 good), versus dishonest critic (2 bad, 2 good) and checked
(0 bad, 0 good), with zero in every 7B arm and label, so worst-case scoring
inflates the preregistered contrast. Of the 11 failed bad prose verdicts,
lenient parsing recovers nine rejections and two approvals: nine of the
16 strict false approvals disappear. The 14B dishonest arm becomes FA 7/60
and HA 51/60. All 7B counts and intervals are unchanged. This sensitivity
analysis supports a smaller reduction, without replacing the frozen decision.

<!-- INCLUDE generated/e4-sensitivity-table.md -->

For 7B, the FA contrast is 0.00 [0.00, 0.00]. It excludes the 22-point
planning reduction but cannot identify protection at the prose-arm floor:
the judge rejects nearly everything, including 56/60 valid inferences. The
secondary HA contrast is +0.80 [0.56, 1.04], rescuing acceptance from 4/60
to 52/60. The unbounded cluster-t interval is reported as specified, including
its endpoint above one. This is an acceptance recovery, not a demonstrated
FA reduction.

Unchecked dishonest objections yield HA 49/60 for 14B and 31/60 for 7B.
The .80 target is met by the 14B point estimate and missed by 7B. For
uncertainty, their dishonest-minus-prose HA contrasts are +0.083
[-0.074, +0.241] and +0.450 [+0.178, +0.722]; the supplied summary does not
provide absolute-HA intervals, so the .80 target is not established with
an interval. In the checked arm, a fabricated countermodel to a valid inference
fails replay by construction and a positive certificate is displayed. That
mechanical rejection defeats the critic's unchecked claim as evidence; it
does not guarantee that a judge accepts every honest inference.

These are per-judge, unadjusted, descriptive results from a mechanism
demonstration whose judges failed the original gate. The intervention combines
checking, checker feedback, and positive certificates; it does not isolate
an English-surface effect or establish family-general efficacy.

The scored manifests identify an A100-SXM4-80GB, vLLM 0.29.0, seed 0,
temperature 0, and 8,192-token context. Model revisions are pinned in the
snapshot. Both manifests record a generic `max_new_tokens: 300` default,
but all 360 submitted prompts specify `max_new_tokens: 800`, and the runner
uses the per-prompt value in preference to that default. The effective cap
was therefore 800, as preregistered. No reply reached 800: the maximum was
658 tokens for 14B and 7 for 7B. For 14B, 257/360 replies reached or exceeded
the manifest default of 300 (one exactly, 256 above); these are not cap hits.
All 360 7B replies were seven tokens, containing only a verdict. No output
has a length finish reason.
<!-- src: paper/sources/e4-score-summary.json (metrics, contrasts, provenance);
paper/sources/e4-score-table.md; paper/sources/e4-prereg-frozen.md at cbc6a80;
paper/analysis/e4_sensitivity.py; paper/generated/e4-sensitivity-table.md.
Raw outputs and manifests: manage-agents/colab/results/e4-scored-a/out/;
submitted overrides: manage-agents/colab/jobs/e4-scored-a/prompts.jsonl;
runner: manage-agents/colab/repo/jobs_lib/vllm_judge.py, SamplingParams max_tokens.
Intervals rounded to three decimals. -->

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
