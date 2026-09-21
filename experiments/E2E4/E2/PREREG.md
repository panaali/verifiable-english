# E2 preregistration: scaling mechanism demonstration

E2 is reported as a mechanism demonstration unless VE differs from the matched structured-FOL
arm, which receives the identical checker findings. The outcome is judge approval/rejection;
false approval and honest acceptance retain failures and unparseable verdicts in their
denominators, scored worst for the cell.

## Primary contrast

Change in false approval from size 4 to size 256 for VE versus direct review, estimated separately
for every judge. The matched VE versus structured-FOL contrast diagnoses any VE-specific effect.
The signed interaction is (FA_VE,256 − FA_VE,4) − (FA_direct,256 − FA_direct,4);
negative values favor VE. The smallest useful benefit is an interaction of −0.10.

## Refutation condition

The scaling claim is refuted if the confidence interval rules out a 10-point smaller increase in
false approval for VE than direct review, or if honest acceptance falls below the constraint. An
interval spanning the 10-point threshold is inconclusive. A VE versus direct difference with no VE
versus structured-FOL difference is evidence for the checker/display mechanism only.
Specifically, a 95% interval with lower endpoint above −0.10 rules out the useful benefit.

## Honest-acceptance constraint

At every size, VE honest acceptance must be no more than 5 percentage points below direct review.

## Smallest useful effect

The smallest useful interaction is a 10 percentage-point smaller increase in false approval from
4 to 256 steps. An interval spanning that effect is inconclusive.

## Capability gate

On dev items each judge must achieve at least 60% balanced accuracy in the direct arm at size 4
and must produce parseable verdicts on at least 90% of trials. Otherwise recalibrate before scoring.

## Sample size

The committed scored set is a construction check and pilot. A scored model run's repetitions are
chosen from dev variance before freezing the run manifest; report item and judge counts and do not
pool judges. Bootstrap vocabulary families, retaining all three paired sizes within each sampled
cluster. Codex-family judges receive about 13.6k CLI context tokens per call and Claude-family
judges about 500; report each judge separately and do not pool across these families.
There are 36 items, 18 per split: at each size the full inventory contains four honest
controls, four invalid-step items, and four checker-invisible errors. Across all sizes,
checker-invisible errors split six false leaves and six wrong specifications. Half of
all error-bearing items are checker-visible. Report those two strata separately as
well as the prespecified combined contrast. Only two scored families and a single
padding mechanism preclude broad population inference. Freeze repetitions and judge
IDs in a committed amendment before scored calls. Use 10,000 paired family-cluster
bootstrap resamples, seed 5204, to compute the interaction directly; resample families
jointly across sizes and conditions. Do not subtract endpoints from independent CIs.

## Interpretation limitation

The size manipulation is one connected dependency sequence with two fixed leaves and an explicit
intermediate claim at each step. At size 256 the core claim bound prevents one monolithic argument
package: local deductions and every adjacent boundary are checked, while the display states that
the aggregate sequence has no single core composition certificate. Any apparent scaling benefit
therefore applies to this local-check-plus-boundary interface, not to a 256-edge core graph.
The extra steps are synthetic logical padding that alternate equivalent forms; they do not add new
empirical leaves or new factual content as length grows. Results may measure tracing burden for a
long connected derivation, but do not establish scaling to work whose evidence burden also grows.
