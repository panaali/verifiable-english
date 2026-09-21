# VE v0: Work Plan

The repository currently contains the design and specifications. Implementation, proofs, and experiments remain to be done. This checklist tracks that work; the [roadmap](roadmap.md) defines the research questions and acceptance criteria.

Start with tasks 1 and 2. Develop proofs and conformance checks alongside the implementation. Run the human pilot once the experimental end-to-end path works; completing every theorem is not a prerequisite for learning whether people can use VE.

1. **Define the first experiment and freeze the prototype contracts — G0**
   - [ ] Establish a small, independently reviewed set of oversight tasks.
     - [ ] Cover both wrong initial formalizations and meaning changes after confirmation.
     - [ ] Include cross-branch predicate substitutions, changed requirements, honest submissions, and legitimate repairs.
     - [ ] Specify intended meanings, evidence available to the judge, expected outcomes, and counterexamples or proof obligations.
     - [ ] Set eligibility rules for the ReaLMistake subset and independently authored tasks; check data-use terms and report unsupported requirements.
   - [ ] Define the comparison protocol.
     - [ ] Specify proposer, critic, and supervisor actions, clarification rules, and stopping conditions.
     - [ ] Give comparison conditions equivalent information and assistance; keep reference answers hidden from all evaluated methods.
     - [ ] Define what counts toward human effort, model calls, proof production, and checking cost.
   - [ ] Complete the interchange and proof-checking contracts.
     - [ ] Specify claim, graph, certificate, and result schemas, canonical encodings, and artifact bindings.
     - [ ] Define allowed proof declarations, isolated proof production, replay, and dependency auditing before accepting agent certificates.
     - [ ] Pin the Lean toolchain and dependencies; check licenses and set initial resource budgets.
   - [ ] **Completion:** representative tasks fit the supported semantics, and their inputs, outputs, and checking boundaries are explicit. See [task criteria](roadmap.md#task-families-and-ground-truth) and the [debate protocol](spec/debate-protocol.md).

2. **Build the smallest usable reference implementation — G1**
   - [ ] Set up the Lean project, CLI, reproducible build, and CI checks.
   - [ ] Implement the [language core](spec/v0-language.md).
     - [ ] Formalize environments, typed claims, general relational structures, and denotation independently of the production parser.
     - [ ] Choose the AST representation using a nested-binding parser/printer proof.
     - [ ] Implement strict parsing, scope and type checking, canonical printing, and useful diagnostics.
     - [ ] Implement environment/model decoding, validation, canonical serialization, and source/meaning/model identities.
     - [ ] Implement finite evaluation and explanatory bindings, including empty domains, vacuity, and resource errors.
   - [ ] Implement argument checking.
     - [ ] Validate claim references and acyclic dependencies under one environment.
     - [ ] Construct the exact expected proposition for each deduction; replay certificates and audit their dependencies.
     - [ ] Validate finite countermodels and distinguish `follows`, `refuted`, `gap`, and unresolved findings from operational failures.
     - [ ] Compose positive certificates while retaining every undischarged assumption; display contradictory findings.
     - [ ] Bind results to the reviewed objects and invalidate evidence when relevant inputs change.
   - [ ] Turn the worked examples into executable fixtures.
     - [ ] Demonstrate satisfied and violated inventories, one valid deduction, a countermodel to an invalid inference, and an explicit repair.
     - [ ] Reject substituted claims, hidden proof assumptions, stale certificates, cycles, and malformed packages.
   - [ ] **Completion:** the CLI checks the [worked debate example](spec/debate-protocol.md#worked-example) from exact claim bytes through its result and remaining assumptions, with experimental assurance clearly labeled.

3. **Build the review interface and run a human pilot — G2**
   - [ ] Provide the minimum interface needed to inspect and repair claims.
     - [ ] Show the original task, canonical VE, vocabulary descriptions, quantifier scope, dependencies, and evidence.
     - [ ] Separate interpretation confirmation, finite evaluation, inference findings, proof checking, and final approval.
     - [ ] Support approve, reject, repair, and unresolved decisions; make changed commitments and remaining assumptions visible.
     - [ ] Add bounded assisted authoring and clarification, while keeping manual review of the final artifact possible.
   - [ ] Prepare matched prose, structured-form, and VE conditions with the same critic and checking capabilities.
   - [ ] Recruit roughly 8–12 pilot participants and counterbalance equivalent task variants.
   - [ ] Measure false confirmations, repairs, false rejections, review effort, and understanding of conditional proofs; include correct and wrong-but-valid claims.
   - [ ] Use the findings to improve the interface, calibrate task difficulty, and plan the larger study's sample size.
   - [ ] **Completion:** identify whether people can inspect VE reliably and what needs improvement before the scored comparison. Follow the [pilot criteria](roadmap.md#human-inspection-pilot).

4. **Run the adversarial comparison — G3**
   - [ ] Implement and calibrate the comparison conditions.
     - [ ] Natural-language debate with cross-examination and a shared glossary.
     - [ ] ColMAD as a separate protocol comparator.
     - [ ] Structured formal claims and VE using the same checker and debate strategy.
     - [ ] Direct judging and checker-only baselines where applicable; assess whether FormalJudge supports a fair additional comparison.
   - [ ] Build the evaluation harness.
     - [ ] Separate development and held-out tasks by semantic pattern and vocabulary family.
     - [ ] Include adaptive attacks, honest submissions, false empirical premises, misleading definitions, inconsistent assumptions, and cases that should remain unresolved.
     - [ ] Vary graph size, depth, branch separation, and the measured capability gap between proposer and judge.
     - [ ] Record all costs, unsupported cases, timeouts, failures, and supervisor decisions.
   - [ ] Fix the primary metric, meaningful effect size, legitimate-acceptance constraint, budgets, and analysis before held-out evaluation.
   - [ ] Run paired comparisons and report uncertainty accounting for repeated tasks and judges.
   - [ ] Distinguish gains from formal checking from gains attributable to the English surface; measure error repair separately from preservation after confirmation.
   - [ ] **Completion:** determine whether VE improves false-approval rates or review effort at comparable useful-answer rates and total cost. Report negative results and coverage limits under the [evaluation criteria](roadmap.md#adversarial-evaluation).

5. **Complete assurance and measure runtime — G4, alongside tasks 2–4**
   - [ ] Discharge the [formal obligations](spec/verification-contract.md#required-obligations).
     - [ ] P1–P3: grammar uniqueness and parser soundness/completeness.
     - [ ] P4–P5: canonical printing, round trips, and normalization.
     - [ ] P6–P7: finite evaluation and translation agree with denotation.
     - [ ] P9–P11: exact certificate propositions, assumption-preserving composition, and countermodel soundness.
     - [ ] P8 when a production implementation differs from the proved reference.
     - [ ] Review theorem statements, termination arguments, proof dependencies, and combined acceptance contracts.
   - [ ] Build the independently specified [conformance corpus](roadmap.md#frozen-conformance-corpus).
     - [ ] Prepare 240 cases with the specified 160/80 development/held-out split and at least 20 minimal pairs.
     - [ ] Cover claims/models, commitment mismatches, arguments/certificates, invalid inputs, and resource behavior; add targeted fuzzing.
     - [ ] Require supported valid inputs to succeed as well as invalid inputs to fail; keep these checks separate from efficacy experiments.
   - [ ] Validate decoding, display, certificate replay, and worker isolation; document any remaining trusted components.
   - [ ] Benchmark cold/warm execution, memory, and each checking stage, including proof production and replay.
   - [ ] Set deployment budgets from representative workloads and optimize measured bottlenecks in the Lean reference first.
   - [ ] **Completion:** all advertised guarantees have the required evidence, and runtime/authoring costs and failure rates are measured.

6. **Make the research and release decision — G5**
   - [ ] Compare results against the fixed acceptance criteria and decide whether the evidence supports further investment in VE's English surface.
   - [ ] Package reproducible builds, proof replay, experiment configurations, permitted data, and analysis scripts.
   - [ ] Document installation, the supported workflow, examples, task coverage, theorem evidence, trust assumptions, and known failures.
   - [ ] Choose the repository license and verify dependency/data redistribution terms.
   - [ ] State precisely what the results establish about oversight and what remains untested about alignment or debate incentives.
   - [ ] **Completion:** another researcher can reproduce the supported checks and evaluate the claimed benefit.

7. **Consider extensions only when evidence justifies them**
   - [ ] Evaluate Rust/Aeneas only for a measured runtime or deployment need, including P8 and proof-maintenance cost.
   - [ ] Add arithmetic, formatting adapters, or richer relations only when task coverage requires them, with explicit semantics and validation.
   - [ ] Study VE combined with ColMAD or prover-estimator debate if the matched language comparison warrants it.
   - [ ] Specify preservation contracts before adding mathematical, probabilistic, temporal, normative, or other semantic profiles.
   - [ ] Treat public proof-service deployment, stronger compiler assurance, and alignment-training/incentive guarantees as separate projects with their own requirements.
