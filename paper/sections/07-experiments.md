# Experiments: frozen designs and development evidence

E1 v5 and E4 revision 2 were frozen on 2026-09-21 before scored judging.
At this manuscript cutoff, E1 scoring had started and E4 was queued behind it;
scored outcomes remain RESULT placeholders. E5 has materials and pilots only:
its scored run was not executed. E2 was not run. Development observations below
explain design choices and do not substitute for held-out effects.
<!-- src: paper/sources/e1-prereg-frozen.md; paper/sources/e4-prereg-frozen.md;
paper/sources/e5-materials-pilots.md; paper/sources/process-log-v1.md. -->

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
and 7B is not scored in E1. Hosted scoring is optional, not assumed completed.
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

### E1 scored table shells

**[RESULT-E1: fill from experiments/E1/RESULTS.md after complete scoring.]**
Every RESULT cell below is unobserved. Assigned denominators are fixed design
counts, not completed-call counts. FA includes failures as approvals; HA treats
failures as rejections. N/A would denote an unrun optional reference, never zero.
S, K, V, N, F abbreviate FOL symbols, FOL keywords, VE strict, VE natural, VE fluent;
A denotes asserted-faithful explanation, 0 denotes none.

Qwen2.5-32B AWQ (primary); each cell has 594 bad and 280 good assigned.

| Cell | Bad approved / 594; FA | Good approved / 280; HA | Failures / 874 | Truncated / 874 |
|---|---|---|---|---|
| S, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| K, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| V, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| N, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| F, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| S, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| K, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| V, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| N, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| F, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |

Qwen2.5-14B AWQ (secondary-permissive; exploratory); each cell has 594 bad and 280 good assigned.

| Cell | Bad approved / 594; FA | Good approved / 280; HA | Failures / 874 | Truncated / 874 |
|---|---|---|---|---|
| S, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| K, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| V, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| N, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| F, 0 | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| S, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| K, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| V, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| N, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |
| F, A | RESULT / 594; RESULT | RESULT / 280; RESULT | RESULT / 874 | RESULT / 874 |

Co-primary estimates and HA constraints (32B only; differences are V minus S).
The decision column applies the preregistered rules above, not significance alone.

| Contrast | Endpoint | Mean difference | 97.5% cluster-t interval | Preregistered decision |
|---|---|---|---|---|
| P1: A | FA | RESULT | [RESULT, RESULT] | RESULT |
| P1: A | HA | RESULT | [RESULT, RESULT] | RESULT constraint; VE HA in cell table |
| P2: 0 | FA | RESULT | [RESULT, RESULT] | RESULT |
| P2: 0 | HA | RESULT | [RESULT, RESULT] | RESULT constraint; VE HA in cell table |

**Per-judge combined decision: RESULT.** Any supported statement must identify
its explanation condition unless both co-primaries support benefit.

Bootstrap sensitivity analyses for 32B (pooled differences; 95% intervals).

| Contrast / endpoint | Pooled difference | Template bootstrap | Base-item bootstrap |
|---|---|---|---|
| P1 / FA | RESULT | [RESULT, RESULT] | [RESULT, RESULT] |
| P1 / HA | RESULT | [RESULT, RESULT] | [RESULT, RESULT] |
| P2 / FA | RESULT | [RESULT, RESULT] | [RESULT, RESULT] |
| P2 / HA | RESULT | [RESULT, RESULT] | [RESULT, RESULT] |

All secondary contrasts below are exploratory, with unadjusted 95% cluster-t
intervals, and cannot support or refute the main claim. Each endpoint cell will
hold the mean paired difference and its interval. The complete result record
also retains pooled-rate template-bootstrap sensitivities.

Qwen 14B: exploratory contrasts.

| Contrast (first minus second) | FA difference [95% CI] | HA difference [95% CI] |
|---|---|---|
| V - S, A (P1) | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| V - S, 0 (P2) | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| K - S, 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| K - S, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| N - S, 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| N - S, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| F - S, 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| F - S, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| V - K, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| S: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| K: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| V: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| N: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| F: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |

Qwen 32B: exploratory contrasts.

| Contrast (first minus second) | FA difference [95% CI] | HA difference [95% CI] |
|---|---|---|
| K - S, 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| K - S, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| N - S, 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| N - S, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| F - S, 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| F - S, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| V - K, A | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| S: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| K: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| V: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| N: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |
| F: A - 0 | RESULT [RESULT, RESULT] | RESULT [RESULT, RESULT] |

Descriptive reporting also includes attack family, oracle direction, and removal
of the 41 empty-sort-only attacks. Each breakdown retains judge and cell, bad
assigned/approved counts, FA and failures. Hosted references, if actually run,
receive separate cell tables and no primary decision. View length and fluent
contraction covariates are recorded below; they are not causal adjustments.

| View | Statement characters | Model tokens (14B / 32B) | Fluent relative-clause guard share |
|---|---|---|---|
| S | RESULT | RESULT / RESULT | N/A |
| K | RESULT | RESULT / RESULT | N/A |
| V | RESULT | RESULT / RESULT | N/A |
| N | RESULT | RESULT / RESULT | N/A |
| F | RESULT | RESULT / RESULT | RESULT |

<!-- src: paper/sources/e1-prereg-frozen.md; expected scored source: experiments/E1/RESULTS.md. -->

### E1b: comprehension control (exploratory)

Without a requirement, each judge predicts whether each candidate is true in
two finite models, labeled by the VE evaluator (balanced truth patterns; chance
.50). The same runner handles E1b; failures and tool use score zero of two.
Per judge and view, report the mean of the 12 template accuracies and a 95%
cluster-t interval, alongside raw correct counts and failures. The design assigns
874 calls and 1,748 truth judgments per row. Compact-prompt dev template means
for symbols/strict were .666/.669 for 14B and .808/.830 for 32B. These are dev
comprehension observations, not scored view effects.

**[RESULT-E1B: fill scored comprehension counts, template means and intervals.]**

| Judge | View | Correct / 1,748 | Template accuracy [95% CI] | Failed / truncated calls (each / 874) |
|---|---|---|---|---|
| 32B | S | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 32B | K | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 32B | V | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 32B | N | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 32B | F | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 14B | S | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 14B | K | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 14B | V | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 14B | N | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |
| 14B | F | RESULT / 1,748 | RESULT [RESULT, RESULT] | RESULT / RESULT |

Lower FA without better comprehension in the same view must be described as
"benefit not established as better understanding; compatible with a threshold
shift." Neither that pattern nor a failed HA constraint identifies a mechanism.
<!-- src: paper/sources/e1-prereg-frozen.md; paper/sources/e1-dev-qwen-e3.md. -->

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
for Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct-AWQ. They decode greedily with
seed 0 and no retries. Context is 8,192 tokens including an 800-token response
cap, increased equally from 400 before scoring because dev responses truncated.
The increased cap itself was not calibrated. Exact token preflight must pass;
inputs are never shortened to fit.

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

**[RESULT-E4: fill from the E4 scored score-summary.json and paired template
analysis; retain complete assignments and report actual runtime settings.]**

| Judge | Scored cell | Invalid approved / 60; FA | Valid approved / 60; HA | Failures / 120 | Truncated / 120 |
|---|---|---|---|---|---|
| 7B | Prose | RESULT / 60; RESULT | RESULT / 60; RESULT | RESULT / 120 | RESULT / 120 |
| 7B | Checked | RESULT / 60; RESULT | RESULT / 60; RESULT | RESULT / 120 | RESULT / 120 |
| 7B | Dishonest | RESULT / 60; RESULT | RESULT / 60; RESULT | RESULT / 120 | RESULT / 120 |
| 14B | Prose | RESULT / 60; RESULT | RESULT / 60; RESULT | RESULT / 120 | RESULT / 120 |
| 14B | Checked | RESULT / 60; RESULT | RESULT / 60; RESULT | RESULT / 120 | RESULT / 120 |
| 14B | Dishonest | RESULT / 60; RESULT | RESULT / 60; RESULT | RESULT / 120 | RESULT / 120 |

E4 paired contrasts and valid acceptance under dishonest objections; descriptive
95% template-t intervals. Each endpoint has 60 assigned items, 12 clusters.

| Judge | Endpoint | Estimate | 95% interval | Frozen interpretation / constraint |
|---|---|---|---|---|
| 7B | Checked - prose FA | RESULT | [RESULT, RESULT] | RESULT |
| 7B | Checked - prose HA | RESULT | [RESULT, RESULT] | RESULT noninferiority |
| 7B | Dishonest-critic HA | RESULT | [RESULT, RESULT] | RESULT versus .80 target |
| 14B | Checked - prose FA | RESULT | [RESULT, RESULT] | RESULT |
| 14B | Checked - prose HA | RESULT | [RESULT, RESULT] | RESULT noninferiority |
| 14B | Dishonest-critic HA | RESULT | [RESULT, RESULT] | RESULT versus .80 target |

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
