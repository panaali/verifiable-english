# Discussion, limitations, and threats to validity

The scored results narrow the claim. Strict English showed no benefit for the
capable primary judge: P1 is inconclusive and P2 rules out a useful 0.05
reduction. The combined E1 claim is not supported. Any benefit of fluent
rendering for the weaker 14B judge remains an exploratory hypothesis. The two hosted reference judges (one measured only under the earlier JSON
legend) were at ceiling on these development items, so these items do not
saturate capable readers. The checked components did help: the E4 14B FA contrast
passes its preregistered protection rule (-0.267 [-0.392, -0.142]); lenient
parsing gives a smaller reduction, -0.117 [-0.231, -0.002], in a post hoc
sensitivity analysis, not preregistered. The interval still excludes zero,
but differential parse failures inflate the frozen contrast. The 7B secondary HA contrast shows
recovery from near-universal prose-arm rejection. Replay also rejects dishonest
countermodel claims by construction. These are limited benefits of the
checking/display package, not evidence that English rendering improves oversight.
<!-- src: paper/sources/e1-results.md; paper/sources/e1-prereg-frozen.md;
paper/sources/e4-score-summary.json; paper/sources/e4-prereg-frozen.md. -->

The qualitative policy exercise exposes low coverage without extensions.
Five of nine debate claims are unformalized; the amendment has one REIFIED
and three OPAQUE clauses. Deontic force, open-textured terms, empirical
premises, and authority judgments do not become checked merely by being named.
One Sonnet agent produced this exercise, without cross-review, using
summarizing source retrieval; its quotations and interpretation need independent
review. The bounded search's NotFound outputs must not be mistaken for general
entailment proofs. These limitations constrain what the use case can demonstrate.
<!-- src: paper/sources/debate-coverage.md; paper/sources/debate-source.md;
paper/sources/debate-countermodel-RESULTS.md; paper/sources/amendment-coverage.md;
paper/sources/amendment-GAPS.md. -->

There are no human participants. Model supervisors may already understand
symbolic logic, respond to authority labels differently from people, or exploit
formatting cues unavailable to human readers. Neither a model-judge benefit nor
a model-judge null establishes human readability. The calibrated primary-band
open judges currently come from one model family. That is a limitation of the
observed ladder, not evidence for generalization across weak supervisors.
<!-- src: PLAN.md; paper/sources/colab-ladder.json. -->

The main experiments use synthetic semantic templates. Fresh vocabulary reduces
literal overlap but does not remove training-data familiarity with logical
patterns or generated prose. Public logic benchmarks are especially vulnerable
to contamination. The coverage audit samples several different task units and
is not representative of all policies, requirements, or AI work. Reified fits
can move difficulty into unverified adapters. Parsing a witness does not prove
its translation, as the second-rater Cedar corrections demonstrate.
<!-- src: design/critique-codex.md; paper/sources/e0-second-rater.md. -->

All project-specific implementation, proofs, annotation judgments, experiments,
reviews, and manuscript drafting were performed by AI agents. Humans supplied
direction and infrastructure; no human participant or annotation panel validated
the proposed interface. The model families may share training material,
conceptual errors, and incentives to finish. Reviewers can favor their own
family's outputs or accept plausible documentation without reproducing it.
Cross-family review changes the reviewer, but does not establish independent
error probabilities, unbiased model comparison, or faithful formal statements.
<!-- src: PROTOCOL.md; paper/sources/process-log-excerpts.md;
design/phase-t-literature.md, judge self-preference references. -->

The views change tokenization, length, variable names, and use of vocabulary
phrases. Identical ASTs and legends do not equalize every cognitive or computational
burden. Longer panels introduce information and organization together. Natural
view template restrictions cannot detect every misleading alias. The lexicon,
intent description, evidence selection, and display remain attack surfaces.
A proof badge may amplify trust in wrong grounding; that risk is an empirical
question, not a theorem about certificate replay.
<!-- src: docs/rendering-views.md; paper/sources/review-views.md;
paper/sources/e5-materials-pilots.md. -->

Development tuning creates selection effects. Pilot ladders contain correlated
variants, and their point estimates can change with quantization, prompts,
reasoning budgets, or batching. Small numbers of independent templates make
interval estimates fragile. E1 v5 and E4 revision 2 froze before scored judging; the reported dev
selection remains part of their evidential limits. E1 has only one primary judge,
one candidate inside its band, and its final explanation condition lowered both false approval and honest
acceptance on the scored split. The 12-template intervals are sensitive to the
structural sample; vocabulary renamings are not independent clusters. E4 retained two judges that failed its original gate.
E2 was not run, and E5 has no scored results. Leak audits
only cover the features and inventory actually tested; their success is not a
general absence-of-shortcuts guarantee. All 96 E1 scored base items have final explanations, but four oracle-UNKNOWN
model attacks were excluded before judging; conditional performance on the
retained inventory cannot establish performance on all generated submissions.
<!-- src: paper/sources/e1-prereg-frozen.md; paper/sources/local-ladder.md;
paper/sources/e5-materials-pilots.md. -->

The assurance boundary also remains substantial. Lean proves statements about
reference definitions; it does not verify production Python or Rust, all wire
correspondence, cryptographic implementations, compiler behavior, IO, or faithful
display. The default graph path uses Python replay. Closure now has proved certificate soundness, but extended graph and general
extended surface round-trip proofs remain open. Finite evaluation and certificate soundness do
not decide all consequences, authenticate facts, recover omitted requirements,
or ensure useful proof search. Canonical identities prevent accidental artifact
substitution only when the surrounding binding and display path is correct.
<!-- src: lean/METATHEORY.md; lean/CLOSURE.md; docs/implementation.md. -->

Humans, other model families in scored comparisons, external baselines,
long-context retention, compaction, and training remain untested. E4 has
failure-sensitive operational endpoints, a floor in 7B prose FA, and a
manifest default of 300 tokens overridden by the submitted 800-token caps
(no reply reached the effective cap). The source report omits E1b raw
correct counts and per-view failures and E1 model-token covariates. These gaps
are disclosed rather than filled from rounded estimates or assumed settings.
<!-- src: paper/sources/e1-results.md; paper/sources/e4-score-summary.json;
paper/sources/e4-prereg-frozen.md; paper/sources/planned-replication.md. -->
