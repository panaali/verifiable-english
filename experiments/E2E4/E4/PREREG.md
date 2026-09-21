Status: FROZEN
# E4 revision 2: certified countermodels and matched critiques

Frozen 2026-09-21 after DEV calibration only; no scored outcomes consulted.
This is a pilot-sized countermodel/display **mechanism demonstration**, not a
confirmatory efficacy study or evidence of an advantage specific to VE.

## Frozen judges and execution

Exactly two judges: `Qwen/Qwen2.5-7B-Instruct` and
`Qwen/Qwen2.5-14B-Instruct-AWQ`. These are **one model family (Qwen2.5)**,
not independent replications across model families. Analyze each separately.
Temperature 0, seed 0, one response per assigned item/cell/judge; no retries
or replacement samples. Context is 8192 tokens including the response,
max_num_seqs is 12, and enforce_eager is omitted. Record actual model revisions,
backend and GPU settings with outputs. There are 360 calls per judge, 720 total.

max_new_tokens: 800

DEV used 400 tokens. The 14B prose cell had 2/16 truncations and 2/16 parse
failures (dishonest critic: 3/16 truncations, 2/16 parse failures), so the cap
is raised to 800 **equally for all three cells and both judges** before scoring.
This budget change is not itself calibrated; residual truncation is possible.
Never truncate input prompts or drop items to fit. Exact chat-template preflight
must pass prompt plus cap <=8192 for every assignment before inference; otherwise
stop the run. Whitespace counts do not establish token fit or GPU memory fit.
A length-finished response with parseable final JSON retains its verdict;
otherwise it is an unparseable failure scored worst case. Report all truncations
separately, including those with parseable verdicts. No cap changes after scoring
starts. Scored export requires this file to equal HEAD byte for byte.

## Primary contrast

Per judge, false approval of invalid inferences in checked-countermodel minus
prose-critique, negative favoring checked models. Both arms carry the same full
hypothetical finite interpretation. Only the checked arm adds actual replay
findings; it reports rejection of the critic's alleged countermodel and the
positive inference certificate on valid items. The third, dishonest-critic arm
asserts the same interpretation as an **unchecked** countermodel. On valid items
that assertion is necessarily false. On invalid items it is an honest control.
Report acceptance of valid inferences despite dishonest objections separately.

Assigned failures, timeouts and unparseable responses remain in denominators,
scored as approval on invalid items and rejection on valid items. Report failure
rates beside endpoint estimates; never replace unsuccessful samples.

## Refutation condition

Let delta be checked-countermodel minus prose-critique false approval. Freeze
22 percentage points as the planning reference for a useful reduction, not a
validated efficacy threshold. A paired template-t 95% interval wholly above
-0.22 rules out a reduction of at least 22 points in the sampled setting; an
interval wholly above zero rules out any protective effect under this interval
model. An upper bound below zero supports protection only if the honest-
acceptance constraint also passes. An interval spanning benefit and harm is
inconclusive. Floor/ceiling results cannot identify the primary mechanism even
if they exclude the planning reference. Effects from unchecked dishonest
assertions alone cannot establish a checked-countermodel effect. All intervals
are per-judge, unadjusted and descriptive; no family-general or confirmatory claim.

## Honest-acceptance constraint

Checked-arm approval of valid inferences must have lower paired 95% bound ≥−.05
relative to prose for a protection claim. Also report valid acceptance under
unchecked dishonest objections (target ≥80%) and its uncertainty. A failure to
establish noninferiority is not evidence of an acceptance loss.

## Dev variance and detectable effect

Calibration source: `e4-dev-c/out/score-summary.json` from the supplied Colab L4
run (16 items per cell, four dev templates). For 14B the paired invalid-template
means, checked minus prose, are [0, -0.5, 0, 0]: sample SD 0.25, mean -0.125.
With K=12 and df=11, SE=0.25/sqrt(12)=0.07217; t-based 95% half-width is
0.15884 and approximate 80%-power MDE is
(t_0.975,11 + z_0.80)*SE = 0.21958, about **22 percentage points**.
This is a rough dev-variance planning approximation, not simulated power or a
reliable sensitivity guarantee: only four dev clusters estimate variance,
endpoints are bounded, templates differ, and the output budget has changed.
At the observed prose false-approval baseline of 12.5%, a 22-point reduction is
impossible; the inventory cannot reliably resolve effects of that observed size.
For 7B all four paired dev template means are zero at floor: zero estimated
variance does NOT imply zero MDE or high precision; sensitivity is unidentified.
No claim of power for a 5- or 10-point reduction is justified.

## Capability gate and calibration outcomes

Original dev targets were prose false approval 20–60%, valid acceptance >=70%,
and parseability >=90%. **Neither selected judge passed this gate.** Retaining
them is an explicit mechanism-demonstration decision, not a claim of gate success.
7B prose: false approval 0/8, honest acceptance 0/8, parse failures 0/16.
14B prose: false approval 1/8, honest acceptance 4/8, parse failures 2/16.
Both checked cells: false approval 0/8, honest acceptance 8/8, no parse failures
or truncations. Dishonest critic: 7B false approval 0/8 and honest acceptance
3/8; 14B false approval 1/8 and honest acceptance 7/8. The 32B ladder assignment
has all 16 outputs missing in every cell in this supplied summary; it provides
no behavioral calibration and is excluded from the frozen scored judges.
No scored outcomes may inform judge choice, difficulty or template revision.

## Sample size

**136 inferences**: dev 8 invalid + 8 valid from four templates × two vocabulary
families; scored **60 invalid + 60 valid** from **12 templates × five fresh
vocabularies**. Templates and vocabularies are disjoint across splits. All three
arms cross all assigned items. Full scoring is 120 × 3 = 360 calls per judge per
sample. Repetitions do not create more independent structural templates.
The effective independent sample size is **about 12 templates, not 60 items**
per label: the five renamed versions of each template are near-replicates.
Additional item-level trials do not repair this structural sample-size limit.

Held-out templates cover quantifier order, shared versus separate existential
witnesses, relation subject/range, witness direction, transitive paths, negative
instantiation, guarded relational transport, relational inclusion, quantifier
negation, existential disjunction and universal disjunction. Every template has
quantifier structure; most also have binary relations. Alpha-renamed copies are
nested in their structural template, not counted as independent templates.

`ve.equivalence.compare` decides the actual premise-conjunction → conclusion
direction for every item. A valid label requires a replayed entailment certificate;
an invalid label requires an explicit finite countermodel checked against all
premises and the conclusion. Reverse-direction UNKNOWN does not determine an
inference label. A forward UNKNOWN aborts construction, never becomes invalid.
Each result also becomes an argument package replayed with `search=False`.

The invalid sibling's genuine countermodel is used as the critic's hypothetical
interpretation for both siblings. On the valid sibling it fails the countermodel
check, either because a premise fails or the conclusion holds. Prose and unchecked
formal critics make the same false assertion. All domains, constants, relations
and the closed extension convention are displayed. No hidden facts determine
validity; sorts may be empty unless inhabited by premises or named constants.

Critique sections are matched to **exactly equal whitespace-token counts** across
all three arms of an item. The full content is retained, then neutral, fixed
record-reading text is appended to shorter sections. This is an explicit length
control and a token-count proxy; character counts and model-token counts can
still differ. It does not isolate every presentational difference from prose.

## Analysis and reporting

Pair conditions within items, retain assigned failures, and average effects over
vocabulary instances within structural templates. Use equal-weight paired
`experiments.cluster_stats.cluster_t`, K=12 and df=11, rather than a percentile
bootstrap. Report dependence on approximately normal template means and the
limited structural population; do not treat 60 renamed examples as 60 independent
templates. `python -m experiments.E2E4.analyze_e4 TRIALS.jsonl --judge JUDGE
--split scored --samples N` implements these primary and honest-acceptance paired
contrasts, checks complete assignments, retains recorded failures, and reports
60 items but K=12 clusters and df=11 for each endpoint. It never clusters by the
template/vocabulary `group` field. Report each judge, valid/invalid denominators,
gate outcomes and dishonest-
critic outcomes separately. Do not pool judges with different contexts/backends.
Calibration outcomes above are DEV only; no scored results are included.
