# Coverage audit (E0)

## Sampling and rating

E0 is an exploratory expressibility audit, not a benchmark of automatic
formalization or a population estimate of oversight coverage. The first Claude
rater drew a fixed sample from id-sorted dataset populations. A GPT-family second
rater inherited those same items. The sample covers logic benchmarks, policy
examples, and boundary cases from relational modeling, requirements, and program
contracts.

| Audit property | Recorded value |
|---|---|
| Datasets | FOLIO, ProofWriter, Cedar, Gatekeeper, Alloy, FRET, Clover |
| Sample per dataset | 30 |
| Total sampled items | 210 |
| Sampling seed | 20260921 |
| Model-rater families | Claude and GPT |

<!-- src: paper/sources/e0-first-survey.md; paper/sources/e0-second-rater.md;
originals pinned in paper/sources/manifest.json. -->

The item unit matters. FOLIO includes the natural-language qualifications, even
when its supplied logical form omits them. ProofWriter includes a theory and
question, without treating a parsed question as an entailed conclusion. Cedar
covers an individual policy's matching condition and effect, not the complete
policy-set decision. Gatekeeper includes helpers, defaults, update guards, and
exemptions. Alloy expands necessary referenced definitions. FRET retains the
specified trace and signal interpretation. Clover covers contracts and
invariants, not the algorithm body.

`DIRECT` uses the base relational fragment. `REIFIED` supplies an explicit
mechanical encoding of records, tuples, events, positions, or function graphs,
with adapter assumptions. `OPAQUE` retains useful relational structure but hides
a required interpreted operation. `NO` leaves no useful supported substance.
Strict fit counts DIRECT. Lenient fit counts DIRECT plus REIFIED. Neither OPAQUE
nor NO counts as implemented coverage.

Blinding was incomplete. The second-rater parent saw aggregate first-survey
commentary before rating, though it did not display item-specific labels or
rationales before freezing. Dataset-specific agents reportedly began with fresh
contexts and raw samples. The parent reviewed their witnesses. These are
cross-family model judgments, not independent human annotations; shared training
and parent intervention limit independence.
<!-- src: paper/sources/e0-second-rater.md, Blinding and provenance. -->

## Per-dataset coverage and disagreement

The tables preserve the frozen labels. Each fit cell gives the count, percentage,
and nominal 95% Wilson interval. The first survey sometimes used a narrower item
unit, so differences reflect rubric application as well as rater disagreement.
In particular, its Gatekeeper core-rule counts do not all cover opaque exemptions.

<!-- INCLUDE generated/e0-first-table.md -->

<!-- INCLUDE generated/e0-coverage-table.md -->

Intervals describe item-sampling uncertainty under a binomial approximation.
They do not quantify rater correctness, source dependence, or translation
validity. Related templates and shared source files can reduce the effective
sample size. No pooled population coverage percentage is justified.

<!-- INCLUDE generated/e0-agreement-table.md -->

Cedar is the clearest disagreement. Its hierarchy-aware `in` operation includes
ancestry; the first survey allowed an adapter-supplied ancestor relation. The
second rater treated that as hiding the missing closure computation. A constant
or uninterpreted binary predicate cannot by itself implement arbitrary
reachability. Agreement also changes when uniform request reification is
required rather than specializing a fixed-action policy.

Unblinding exposed errors in the second rater too. Several purported set-valued
GitHub fields were actually group entities, so their witnesses also needed
hierarchy closure. Those witnesses parsed but did not faithfully translate the
source. Proposed corrections remain separate from the frozen comparison.

<!-- INCLUDE generated/e0-corrections-table.md -->

The corrected strict Cedar count also reflects a proposed convention change:
fixed-action specialization removes unnecessary request reification. It is not
solely a repaired semantic error. The audit thus supports a spread with explicit
assumptions, not the headline that real policy text fits the base language.
<!-- src: paper/sources/e0-second-rater.md, Findings during adjudication;
paper/sources/e0-first-survey.md, Cedar and Gatekeeper notes. -->

## Missing constructs and extension projections

The ranked missing-construct inventory is computed from frozen OPAQUE and NO
items. An item can require several constructs, so rows overlap. Lexical sense
disambiguation is an authoring problem rather than a missing logical operator.

<!-- INCLUDE generated/e0-constructs-table.md -->

The extension ledger projects which complete items would fit if closure and
linear integer arithmetic were available with the specified encodings. It does
not credit strings to either profile. Integer arithmetic does not discharge
real-valued FRET signals, nonlinear products, arbitrary counting, or string
exemptions. These are authored projections, not measurements of new translations
or solver success.

<!-- INCLUDE generated/coverage-projection-table.md -->

A subsequent closure artifact supplies actual encodings and finite examples for
a subset of projected movers:

<!-- INCLUDE generated/closure-witness-table.md -->

The bundles retain source hashes, adapter conditions, and true/false finite
models. Python and Lean agree with handwritten graph interpretations on these
examples. The Cedar encodings preserve group entities and policy contributions;
the Alloy encodings exercise filtered paths, connectivity, and positive cycles.
These checks do not prove general source-to-VE equivalence, execute the original
Cedar or Alloy engines, or revise E0's frozen coverage score.
<!-- src: experiments/E0/closure_witnesses/README.md;
experiments/E0/closure_witnesses/report.json; docs/spec/v0.1-coverage.md. -->

## Qualitative use case: a policy dispute and its legal text

One Sonnet agent analyzed a birthright-citizenship debate and Section 1 of the
Fourteenth Amendment. This exercise is not cross-reviewed or a scored
experiment. The source pages were read through a summarizing fetch tool;
quotations are best-effort and were not independently verified against raw
page text. We report the committed formalization's structure, not a legal
adjudication or a validation of its source interpretation.

The formalized deductive dispute reduces to the extension of one predicate,
`subject_to_jurisdiction`. Both sides' reconstructed arguments are deductively
valid from their own conflicting bridging premises. The recorded countermodel
runs make the distinction concrete:

| Run | Submitted inference | Recorded result and interpretation |
|---|---|---|
| 1 | Birth plus jurisdiction under the shared citizenship rule | NotFound; the displayed inference is modus ponens. |
| 2 | Birth without the jurisdiction premise | Found; a finite countermodel witnesses the missing premise. |
| 3 | A rule about domiciled parents applied to undocumented parents | Found; the extension needs an additional bridge. |
| 4 | Add the keep-it side's jurisdiction bridge | NotFound; the conclusion follows from that stated bridge. |
| 5 | Add the end-it side's contrary bridge | NotFound; the contrary conclusion follows from that stated bridge. |

The search used nonempty domains with maximum size 3. Bounded `NotFound`
alone is not an entailment certificate: validity for runs 1, 4, and 5 follows
from their displayed rules and premises by elementary deduction, not from
exhausting that finite search. The snapshot's stronger language about proving
entailment from `NotFound` is not adopted here. The two Found cases do provide
finite witnesses to non-entailment. None of these checks decides which bridging
premise faithfully represents the legal source or should be accepted.

The claim inventory marks 5 of 9 claims NO and 4 DIRECT as formal premises.
Empirical and predictive assertions, moral premises, authority weighting, and
the warrant for extending precedent remain outside the check. This count is a
qualitative judgment about this reconstruction, not a population estimate.
The predicate dispute summarizes its deductive core, not every substantive
issue in the debate.

The amendment's four clauses receive 0 DIRECT, 1 REIFIED, and 3 OPAQUE labels.
Deontic force and open-textured legal terms are the main gaps: an extensional
prohibition does not distinguish forbidden conduct from conduct that simply
never occurs, and naming a predicate does not define the applicable legal
standard. The reified residence relation also omits a uniqueness assumption
identified by the author. Thus even a parsable statement may lose source
meaning. Coverage of this real policy text is low without extensions, and
extensions alone cannot verify empirical evidence or settle normative and
interpretive judgments.
<!-- src: paper/sources/debate-claim-graph.md;
paper/sources/debate-countermodel-RESULTS.md (runs 1--5);
paper/sources/debate-coverage.md; paper/sources/debate-GAPS.md;
paper/sources/debate-source.md; paper/sources/amendment-coverage.md;
paper/sources/amendment-GAPS.md; paper/sources/amendment-source.md.
Snapshots from usecases/main; single Sonnet authorship and absence of
cross-review disclosed in the drafting handoff. No fresh countermodel runs. -->
