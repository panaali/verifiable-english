# E4 revision 2: certified countermodels and matched critiques

Draft amendment; **no live model calls in this revision**. The previous single-
template pilot was at floor/ceiling. This revision needs a fresh dev-only pilot;
its prose false-approval rate is not yet known. E4 is a countermodel/display
mechanism experiment, not by itself evidence of an advantage specific to VE.

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

An interval above zero rules out a protective effect in the sampled setting.
An interval spanning benefit and harm is inconclusive. A result driven only by
unchecked dishonest assertions cannot establish a checked-countermodel effect.
Floor/ceiling rates cannot identify the primary mechanism. No useful-size
refutation claim is made until a feasible dev-based threshold is frozen.

## Honest-acceptance constraint

Checked-arm approval of valid inferences must have lower paired 95% bound ≥−.05
relative to prose for a protection claim. Also report valid acceptance under
unchecked dishonest objections (target ≥80%) and its uncertainty. A failure to
establish noninferiority is not evidence of an acceptance loss.

## Smallest useful effect

No confirmatory threshold is frozen without a dev variance/power estimate.
The former 10-point threshold over two clusters was unsupported. Freeze a
feasible effect and any larger inventory in an amendment before scored calls;
otherwise this remains a pilot-sized mechanism set, despite the larger inventory.

## Capability gate

On dev only, target prose-arm false approval **20–60%**, valid acceptance ≥70%,
and parseability ≥90%. The separate open-weight ladder may supply an informative
judge. Report all attempted judges and gate failures; do not claim the target is
met without running the pilot. Freeze judge IDs, context settings and repetitions
before scoring. No scored outcomes inform difficulty or template revision.

## Sample size

**136 inferences**: dev 8 invalid + 8 valid from four templates × two vocabulary
families; scored **60 invalid + 60 valid** from **12 templates × five fresh
vocabularies**. Templates and vocabularies are disjoint across splits. All three
arms cross all assigned items. Full scoring is 120 × 3 = 360 calls per judge per
sample. Repetitions do not create more independent structural templates.

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
templates. Report each judge, valid/invalid denominators, gate outcomes and dishonest-
critic outcomes separately. Do not pool judges with different contexts/backends.
No new model results are included in the material-validation report.
