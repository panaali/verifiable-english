# E1: exact-translation discrimination

## Design and development observations

The scored inventory contains 96 base items from 12 authored templates with
fresh vocabulary bindings, yielding 874 candidates: 280 equivalent and 594
non-equivalent to their reference. Good candidates include canonical formulas
and verified equivalents. Bad candidates include mechanical and model-written
attacks, retained only when the oracle validates non-equivalence and decides
both implication directions; UNKNOWN candidates never reach a judge. The
requirements are short, near-formal descriptions authored with the reference
AST. No independent source-intent validation or specification-size manipulation
is performed. Symbolic statements average about 92 characters.

Each candidate is crossed with five views and explanation present/absent,
producing 8,740 sign-off trials per judge. Requirements and the compact vocabulary
legend are identical across views. Judges have no tools, see no reference AST,
and are asked to approve exact translations. Both scored judges are Qwen2.5
AWQ models, decode greedily, and receive the same 400-token response cap.
Failures remain in assigned denominators as false approvals for bad candidates
and rejections for good candidates; no E1 sign-off trial failed. E1b separately
asks for truth in two finite models without showing a requirement, adding
4,370 calls per judge.

Development drove prompt and role choices. The 32B symbolic/no-explanation
baseline was 34/110 false approvals, only one candidate inside the primary
30--60% gate; 14B was permissive at 73/110. Changing the legend alone had moved
32B false approval from about .15 to .31. Its scored baseline, 176/594 = .296,
is outside the gate band; we retain the frozen role rather than reselecting it.
Hosted development references (GPT-5.6 Luna and Claude Haiku 4.5) achieved about
.97 accuracy and .04--.05 false approval. They were near ceiling on these
items, and were not scored on the held-out inventory.

The largest development effect was not a rendering. Candidate-conditioned,
honest structured descriptions (recipe e2) reduced 32B symbolic false approval
from about .31 to .05. This exceeds any observed rendering effect and motivates
a trusted back-translation baseline. E2-style explanation here means recipe e2,
not the unrun scaling experiment E2. The final explanation recipe e3 instead
asserts the requirement's faithful reading, using exactly one text for every
candidate in a base item. On bad candidates the assertion is false. It is
not an adaptive attack written after seeing the candidate or judge objections.
It lowered both false approval and honest acceptance; "attacker" is the frozen
condition name, not evidence of successful persuasion.

## Frozen decisions, unchanged

E1's co-primaries compare strict VE minus symbols: P1 with e3, P2 without.
The estimand is the unweighted mean of paired template differences in false
approval. Each uses a 97.5% cluster-t interval over 12 templates (Bonferroni for
two contrasts). Support requires an upper bound at most -.05 and an honest-
acceptance constraint: paired HA lower bound at least -.10, point difference
at least -.05, and strict-VE HA at least .70. A lower FA bound above -.05
refutes the specified five-point benefit; otherwise the result is inconclusive.
Both HA constraints hold. The overall E1 decision remains **inconclusive**:
P1 is inconclusive and P2 refutes a five-point benefit. This is not evidence
that all rendering effects are exactly zero.

The compact table retains all frozen per-judge decisions, including E4's
strict-parser pilot rule discussed below. Only E1 32B has a primary role;
14B E1 contrasts cannot support or refute the preregistered claim.

<!-- INCLUDE generated/preregistered-decisions.md -->

E4's "supports protection" is the original rule's label, not a new mechanism
claim. Its gate failures and feedback content limit interpretation. The 7B frozen interval excludes the .22 planning reduction, but its prose
floor cannot identify protection. The preregistrations have repository freezes
but no external timestamps.

## Post hoc discrimination and paired sensitivity analyses

**Everything in this subsection is POST HOC.** All 20 judge-by-view-by-
explanation cells have reproducible FA, HA, balanced accuracy, signal-detection
$d'$ and criterion $c$ in the appendix. Balanced accuracy is
$(HA+1-FA)/2$. For $d'$ and $c$, the log-linear correction adds .5 to successes
and 1 to denominators in both signal (good) and noise (bad) rates, including
cells away from the boundaries. Positive $c$ denotes reluctant approval.

For 32B without explanation, balanced accuracy is .809 for symbols and .812
for strict VE; with explanation it is .821 and .823. The near-null strict
contrast therefore persists in a discrimination measure. For 14B, fluent
balanced accuracy is .730 versus symbolic .641 without explanation, and .771
versus .629 with explanation. In 32B symbols, e3 moves criterion from -.412
to +.107 while $d'$ changes from 1.892 to 1.840: the approval decline is
consistent with a threshold shift rather than improved discrimination.

We enumerate all $2^{12}$ sign flips of the paired template differences and
invert the same two-sided location tests for intervals. These are post hoc
sign-randomisation sensitivities, not design-based causal tests: templates are
fixed authored structures, and sign exchangeability/independence is an
assumption. Intervals further assume a common symmetric location shift; exact
enumeration does not remove those assumptions. The full output includes
leave-one-template-out ranges and the inversion grid specification.

| Post hoc contrast | Template FA difference | Raw two-sided p | Leave-one-template-out range |
|---|---|---|---|
| 32B strict - symbols, P1 | +.027 | .460938 | +.011 to +.052 |
| 32B strict - symbols, P2 | +.003 | .875488 | -.004 to +.014 |
| 14B fluent - symbols, no explanation | -.141 | .000977 | -.158 to -.123 |
| 14B fluent - symbols, e3 | -.147 | .001953 | -.160 to -.129 |
| 32B fluent - symbols, no explanation | -.044 | .218750 | -.053 to -.018 |
| 32B fluent - symbols, e3 | +.001 | .993164 | -.017 to +.037 |

The two co-primary p values above are unadjusted (Bonferroni doubles them,
capped at one); all fluent tests are exploratory. The 32B post hoc 97.5%
intervals are [-.068, +.115] for P1 and [-.047, +.048] for P2. Changing the
smallest-useful-effect threshold to .03 makes both inconclusive; at .05, P1
is inconclusive and P2 refuted; at .08, both are refuted. This holds with either
the frozen t intervals or the post hoc inverted intervals. The threshold is a
judgment, not a derived operational loss model, and no threshold supports a
benefit here.

![POST HOC template-level false-approval differences. V is strict VE; F is fluent; S is symbolic FOL. Each point is a within-template paired rate difference. Templates are authored structures, not population samples.](generated/posthoc-template-differences.pdf){width=85%}

A mixed-effects package (`statsmodels`) was unavailable in the offline cache.
We therefore fitted a post hoc binomial logistic model separately for good and
bad candidates, with fixed view, explanation, judge, and view-by-judge terms,
and a sandwich covariance clustered by template. Base items are nested within
those clusters; no random-intercept variances are estimated. This alternative
allows dependence within a template but relies on only 12 clusters and an
additive explanation effect. On bad candidates, the 32B interaction relative
to 14B is +.429 log odds for strict VE (95% interval [.089, .768]) and +.486
for fluent ([.089, .882]). These exploratory, unadjusted associations agree
with a weaker rendering benefit at 32B; they do not establish a general
capability law. Full coefficients and convergence checks are in the artifact.

## Post hoc weakening attacks only

A weakening is selected by the materials' oracle relation: faithful entails
attacked, but attacked does not entail faithful. This is not inferred from
attack-family names. There are 243 such candidates in nine templates; three
templates contain none. All view-by-judge rates and 95% inverted sign-flip
intervals are in the appendix, with pooled rates distinguished from equally
weighted template rates. The paired test uses all $2^9$ sign flips.

For **32B with explanation, strict VE is worse than symbols in this inventory**:
false approval is 52/243 (.214) versus 31/243 (.128), an 8.6-point pooled
increase. The equal-template difference is +.088, with post hoc 95% interval
[-.009, +.214] and two-sided p = .125. It is compatible with substantial harm,
but does not exclude zero. A possible safety cost is therefore visible even
though the all-attack primary result is inconclusive. Strengthening and
incomparable attacks should not be silently treated as the same safety outcome.
