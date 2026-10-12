# Batch 14b relay mutation review

On task commit `366bd777101ed438774d21f3bde655dfd09f3bef`, the focused
`service:family-norms` relay mutation gate passed: 11 fixtures, 2,428
mutants, 2,350 refused, 78 allowed, zero failures. Its complete report is
`relay-mutation-family.json`.

The full relay mutation gate checked 39 routes and 109,195 mutants. It
returned 133 failures outside `service:family-norms`: 128 allow-list paths
that matched no mutant and five accepted mutations under
`service:readings-route`. Its complete report is
`relay-mutation-full.json`. No relay gate fixture or allow-list file changed
in batch 14b. This full-gate result is recorded as a review limitation, not
as a pass. The pre-review checker returned READY with a WARN because its
30-minute relay mutation subprocess did not finish.
