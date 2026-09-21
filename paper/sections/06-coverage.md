# Coverage: disputed translations and adapter assumptions

E0 sampled 30 items from each of seven heterogeneous datasets and obtained two
model-family ratings. This is an expressibility audit, not a measurement of
verified population coverage. DIRECT uses the base relational fragment;
REIFIED adds explicit tuple, request, event, or function-graph encodings with
adapter obligations; OPAQUE hides an essential interpreted operation; NO leaves
no useful supported substance. A parsed witness does not establish translation
correctness. Blinding was incomplete: the second-rater parent saw aggregate
first-rater commentary, though item labels were frozen before unblinding.

The more informative result is **which assumptions changed the ratings**.
The following POST HOC summary groups the disputes; the appendix prints every
one of the 77 disputed items, its two labels, and the proposed adapter
assumption or omitted meaning. Frozen percentages and proposed adjudications
remain separate in the appendices.

| Dataset | Disputed / 30 | Adapter assumption at issue (post hoc summary) |
|---|---|---|
| FOLIO | 6 | Preserve temporal, frequency, modal, and attitude qualifications in prose, rather than adopting a simplified supplied logical form |
| ProofWriter | 4 | Treat "usually", "often", and default-like language as meaning-bearing, rather than deleting it to recover Horn rules |
| Cedar | 26 | Interpret `in` as hierarchy ancestry; distinguish group entities from sets; specify fixed-action specialization versus uniform request reification |
| Gatekeeper | 12 | Include helpers, defaults, guards, and exemptions in the item; expose regex/string and numeric operations |
| Alloy | 10 | Expand referenced definitions; preserve closure, ordered structures, multiplicity, and arithmetic rather than naming their results |
| FRET | 8 | Preserve temporal/real-valued signal semantics; finite-state or integer encodings are additional assumptions |
| Clover | 11 | Preserve sequence, counting, arithmetic, and function semantics in contracts; function-graph reification alone is insufficient |

Cedar makes the instability concrete. Four-way agreement is only 4/30
(kappa -.11). An adapter-supplied ancestor relation can make a policy look
relational, while hiding the actual reachability computation. Worse, three
second-rater witnesses for GitHub policies #3, #4, and #5 interpreted group
entities as user sets. All parsed, but were semantically wrong. Proposed
corrections reduce the claimed-fit inventory from 114 to 111 of 210; that
heterogeneous total is not a coverage rate. Separately, specializing five
fixed-action policies changes DIRECT versus REIFIED without changing fit/no-fit.
Nominal binomial intervals cannot quantify this ambiguity about the item unit
and adapter semantics.

Closure witnesses for selected Cedar and Alloy examples provide development
checks against hand-specified finite interpretations, including Python/Lean
agreement. They do not execute the original Cedar evaluator or Alloy analyzer
and do not establish general source-to-VE equivalence. Executed differential
translation checks remain planned.

## Four qualitative use cases

All four committed use cases belong in the coverage account. They are authored
illustrations, not scored model comparisons or independently validated source
interpretations. Source pages were accessed through a summarizing fetch tool;
no fresh source verification was performed for this revision.

| Use case | DIRECT / rows | What the formalization leaves open |
|---|---|---|
| Birthright-citizenship debate | 4/9 claims | Competing jurisdiction bridges, empirical claims, authority weighting, and normative warrants |
| Fourteenth Amendment, Section 1 | 0/4 clauses | Deontic force and open-textured legal standards; one residence reification also needs a uniqueness assumption |
| Claude constitution excerpt | 0/23 rows | Values, obligations, preferences, and contextual interpretation are not supplied by relational predicate names |
| News article | 1/26 rows | Numeric and temporal claims, attribution content, causal or hedged framing; opaque quantity tags do not implement arithmetic |

In the debate reconstruction, both sides' deductions follow from their own
conflicting jurisdiction bridges. Finite countermodels expose missing bridges,
but do not decide which premise represents the source or should be accepted.
Bounded `NotFound` is not an entailment certificate. In the news example,
events and participants admit reification, but an opaque constant for what
someone said leaves its propositional content unchecked. The constitution
excerpt and amendment expose especially low direct coverage. These examples
show why expanding the logical fragment alone cannot settle grounding or
normative interpretation.
<!-- src: paper/sources/e0-second-rater.md; usecases/*/coverage.md;
paper/sources/debate-countermodel-RESULTS.md; docs/spec/v0.1-coverage.md. -->
