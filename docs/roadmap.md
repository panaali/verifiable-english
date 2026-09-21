# VE v0: Experiments and Acceptance Criteria

**Status:** First draft. Implementation, proofs, and experiments are pending. Pilot sizes and resource limits below are provisional budgets, not measured results.

VE's first empirical hypothesis is: **at a fixed human review budget, its presentation helps reviewers detect incorrect specifications and mismatched evidence beyond a structured interface using the same checker.** Test the benefit of formal commitments against prose separately, and test whether multi-round debate adds value beyond one critique. None of these benefits is established yet.

The [architecture](architecture-and-design.md#research-target-and-evidence) connects this hypothesis to debate research. The [language](spec/v0-language.md), [argument protocol](spec/debate-protocol.md), and [verification contract](spec/verification-contract.md) define what is checked.

The [work plan](plan.md) breaks the remaining work into nested tasks and prerequisites.

The [critical review](research-review.md#recommended-first-study) proposes humans reviewing service-deployment requirements as the first application, with a small coverage screen and inspection study. This target is provisional. Human and model judges have separate hypotheses and results; model pilots cannot establish human readability.

## Research sequence

| Gate | Deliverable | Decision criterion |
|---|---|---|
| Pre-A — Coverage survey | Sample from a named application distribution independently of v0; record direct coverage, required adapters/extensions, and opaque judgments; survey a benchmark separately if making claims about it | If coverage is insufficient for that workflow, change the fragment or target before building the implementation |
| Pre-B — Baseline attack rate | Test prose with cross-examination and a shared glossary; calibrate attacker and critic on controls; keep model and human results separate | Rare baseline failures weaken this use case only if attack quality, task difficulty, and uncertainty have been assessed |
| Pre-C — Disposable inspection pilot | Matched structured, strict VE, and more natural read-only views of the same AST; include merged vocabulary, wrong-but-valid cases, and distinguishing inventories | Diagnose usability, review errors, and proof-label effects; a small null result alone is not evidence of equivalence |
| G0 — Task and protocol definition | Independently labeled cases, eligibility rules, comparison conditions, claim/graph/certificate wire formats, proof-worker isolation and replay design, and pinned dependencies | Tasks expose meaningful oversight failures; unsupported requirements remain visible; all methods receive equivalent information and clarification |
| G1 — Minimal checked argument | Reference parser/printer, finite evaluation, exact certificate binding, one valid deduction, one failed inference with a countermodel, and a valid explicit repair | The complete path from displayed claims to checked conclusion and assumptions works on independently specified cases |
| G2 — Human inspection pilot | Counterbalanced review of correct and wrong-but-valid specifications, with repair tasks and matched assistance | Identify whether VE helps people inspect meanings and where it causes errors; revise the interface before a scored comparison |
| G3 — Adversarial comparison | Held-out tasks, adaptive attacks, strong baselines, cost and uncertainty estimates | Test whether any reduction in false approval persists at comparable legitimate acceptance and total oversight cost |
| G4 — Assurance and runtime | P1–P7 and P9–P11, the conformance corpus, display/decoder checks, and runtime measurements; P8 for a differing production implementation | Advertised guarantees match completed proof scope and explicit remaining trust assumptions |
| G5 — Research and release decision | Reproducible results, dependency pins, proof replay, failure analysis, and supported task coverage | Report the demonstrated scope; broader alignment claims require additional evidence |

The preliminary steps need no Lean code and test major uncertainties; their duration depends on task access, independent labeling, and recruitment. The architecture's [known weaknesses](architecture-and-design.md#known-weaknesses-of-the-current-design) explain why they come first. Record decision rules before each step, including when the outcome will be inconclusive. Freeze quantitative efficacy thresholds after calibration and before held-out scoring; do not use an underpowered usability pilot to declare success or impossibility.

The gates guide decisions, not a requirement to finish all metatheory before studying users. G2 and runtime measurement may use an experimental G1 slice. No verified runtime port or general mathematical language is needed to test the initial hypothesis. Estimate engineering effort from that slice, including proof repair and authoring failures.

## Task families and ground truth

**Inconsistent meanings across branches.** Construct finite argument graphs with known interpretations and controlled attacks: reuse a label for different predicates, change the domain of a quantifier, import a certificate from another environment, or omit an assumption needed to connect two branches. Include valid alpha-renamings, equivalent formulas linked by checked deductions, valid repairs with added premises, and arguments whose premises remain disputed. The [worked example](spec/debate-protocol.md#worked-example) is a minimal instance.

Start with graph sizes such as 8, 32, and 128 claims, varying depth and the separation between conflicting uses. These are experimental settings to calibrate, not evidence that oversight scales. The checker may inspect the submitted graph, but must not receive hidden answers to empirical leaves or an exhaustive tree unavailable to baselines.

**Requirement reinterpretation.** Start from the selected application and independently authored mechanism cases. Include changing a conjunction to a disjunction, reversing an implication, weakening an exception, narrowing the checked inventory, and vacuous satisfaction. [ReaLMistake](https://github.com/psunlpgroup/ReaLMistake) is an optional external coverage check, not a mandatory first benchmark: its math word problems, fact verification, and answerability tasks require arithmetic, textual entailment, or world knowledge outside much of v0. If used, report a predefined expressible subset and exclusions. Its data is CC BY-SA 4.0 and its authors ask that examples not be published online in plain text, so do not commit examples to this repository.

Task eligibility must be determined by semantic coverage before measuring baseline failures. Report the fraction excluded and why. Arithmetic, numeric formatting, temporal behavior, and textual entailment may need a specified adapter or a new profile. An agent-supplied flag saying that a response meets such a requirement is not an implementation of the check. Benchmark handling must respect its license and data-use terms.

Independent reviewers establish the original intended requirements, expected formal interpretations, and relevant counterexamples or proof obligations. Genuinely ambiguous source tasks must be clarified equally for all conditions or excluded from binary scoring with the reason reported. Keep reference ASTs and scoring labels hidden from every evaluated method. Model agreement alone is not ground truth.

Ground truth needs two distinct checks: the formal target agrees with the intended requirement, and the supplied evidence supports the relevant premises. A generated formula and a paraphrase from the same generator are not independent validation. Use small scenarios that separate plausible interpretations, independently reviewed evidence mappings, and adjudication of reviewer disagreements. Identify every evidence snapshot and the deployment or inventory scope it covers.

Separate two tasks: detecting a wrong initial formalization, and preventing a change after confirmation. For initial formalization, count the human's inspection and correction work. For preservation, give every method the same clarified target; VE must not receive a better specification or more evidence than its comparators.

## Comparison conditions

| Condition | Role in the comparison |
|---|---|
| Natural-language debate with cross-examination and a shared glossary | Tests whether ordinary debate can expose the same meaning changes using cross-branch questions |
| Proposer plus one independent critique | Tests whether extra debate rounds improve on a cheaper review protocol |
| ColMAD | Tests against a recent collaborative error-detection protocol, not only a weak competitive baseline |
| Independent judgments with voting | Controls for the value of extra model calls in the ColMAD comparison |
| Structured formal claims with the same checker | Isolates the value of exact formal commitments, dependency checks, and certificates without the VE surface |
| VE with the same checker | Tests the additional benefit or cost of canonical English and assisted human inspection |

Keep the debate strategy identical between structured formal claims and VE; use cross-examination for the initial matched comparison. ColMAD is a separate protocol comparator. If results justify combining VE with ColMAD or prover-estimator debate, evaluate that combination separately rather than attributing a protocol change to the language.

All conditions receive equivalent task information, clarification, evidence access, and model assistance. Charge certificate generation, tools, and extra agent calls to the method using them. Also include a single-critique condition without multi-round debate, since prior debate experiments found small gains when the judge already has all the information. Include direct judging and a checker-only baseline wherever the available formal inputs already determine the answer; do not withhold a cheap deterministic solution just to make debate useful. FormalJudge is relevant related work for specification synthesis; include an applicable implementation if the chosen tasks support a fair comparison.

Use the same tasks and matched model configurations across conditions. Counterbalance order and use equivalent variants to limit memorization. Give natural-language baselines effective prompts and the opportunity to cross-examine. Preserve operational failures and unsupported cases in end-to-end results.

Run comparisons in stages. First hold candidate claims, evidence, and prepared critiques fixed to isolate presentation. Give structured and English conditions equivalent scope displays, predicate-use panels, and examples. Then test adaptive agents and the extra value of debate. These are different estimands: fixed-artifact inspection cannot measure authoring cost or attack adaptation, while an end-to-end result alone cannot isolate the English surface. Do not spread a small pilot across every protocol and interface combination.

## Human inspection pilot

Begin with an exploratory pilot of roughly 8–12 participants, sized for diagnosing problems rather than claiming population efficacy. Use counterbalanced task variants across prose plus clarification, a structured constraint editor, and VE. Hold the critic and checking capabilities constant.

Participants inspect the original task, candidate claims, definitions, and evidence; then approve, reject, or repair the candidate. Mix faithful specifications with wrong-but-valid ones, including candidates that pass their own checks. A passing evaluation or proof badge must not give away the experimental label.

Measure false confirmations, successful corrections, false rejections, review time, clarification count, and understanding of conditional proof versus factual truth. Include unaided inspection of the final artifact even when authoring is assisted. Test display of quantifier scope, distinct predicate senses, remaining assumptions, vacuity, and changed commitments.

Include satisfaction predictions on small inventories that distinguish competing readings, before revealing checker feedback. Test a separate intervention for proof-label presentation on valid deductions with both adequate and inadequate grounding. The interface must report the actual checking result in every condition. Record prior formal-methods experience, training time, and learning effects.

Use the pilot to set task difficulty, review budgets, and a power analysis for a larger comparison. Do not treat zero observed errors in a small pilot as a safety guarantee, or select only tasks where VE looked promising. If structured forms perform as well with less effort, retain the checker and reconsider the English surface.

## Testing the expected benefits

The [expected benefits](architecture-and-design.md#expected-benefits-for-debate-and-scalable-oversight) require evidence beyond successful proof checking. Use these measurements to explain any change in the primary approval and cost outcomes:

| Expected benefit | Measurement |
|---|---|
| Preserved meaning across branches | False approvals of changed claims as branch separation increases, with equally clarified targets and a cross-examination baseline |
| Human effort focused on interpretation and evidence | Review time spent on definitions, evidence, and deductions; vary formal argument size while controlling the number and difficulty of empirical premises |
| Precise challenges and reliable reuse | Accuracy and time to locate and repair flaws; errors, lost assumptions, and repeated review when a checked subargument is reused in another argument under the same environment |
| More useful training feedback | Initially compare rewards for honest and deceptive submissions; a subsequent training study must test whether this changes behavior on held-out tasks |

Collect review events with the same instrumentation in every condition and account for any measurement overhead. Reuse comparisons must give baselines access to the same prior work. Report results as argument complexity and the measured agent–judge capability gap increase, including formalization and certificate costs. An advantage at one small task size does not establish a scaling advantage. Training and PED-integration studies are conditional follow-ups, not requirements for the first language comparison.

## Adversarial evaluation

Use a proposer trying to obtain approval for a noncompliant result and a critic trying to expose the problem. Start with controlled attacks to check the mechanism, then allow adaptive attacks on development tasks. Keep held-out semantic patterns and vocabulary families unavailable during attack tuning.

Allow attacks against initial definitions, inference composition, premise selection, and presentation. Let the proposer author or amend the vocabulary in at least one condition, and include the [merged-vocabulary attack](spec/debate-protocol.md#the-same-attack-when-the-vocabulary-is-merged): one vaguely described predicate, fully certified deductions, and leaves grounded in different evidence. Compare its success under VE with its success in prose, since a checked proof may make the flaw harder to see. Include correct proofs of weakened claims, false but persuasive empirical leaves, contradictory assumptions, attempted reuse of stale certificates, and trivial arguments that assume their own conclusion. Include honest submissions, legitimate repairs, cases where both agents are wrong, and cases that should remain unresolved.

The supervisor can approve, reject, request repair, or abstain. A proof-search timeout is not a finding that the claim is false. Prompted adversaries and best-of-N search are limited approximations to adversarial optimization; they do not establish the equilibrium or training guarantees of a debate theory.

Record the following outcomes; choose one primary contrast and endpoint before held-out scoring:

- False approval rate on attacks, alongside acceptance of genuinely compliant submissions.
- Successful detection and repair of specification errors, separated from preservation after confirmation.
- Human review time and evidence queries; agent tokens, tool use, certificate production/replay, and total compute.
- Unresolved, unsupported, timeout, and invalid-certificate rates, without dropping these cases.
- Confidence on correct and incorrect approvals, to detect increased trust in wrong-but-valid claims.
- Reward earned by honest versus deceptive submissions, to distinguish useful supervision from simple deference to a usually-correct agent.

Report paired comparisons and confidence intervals, with uncertainty accounting for repeated tasks and judges. Fix the primary metric, meaningful effect size, legitimate-acceptance constraint, and budgets before held-out evaluation. Examine results as graph size, task difficulty, and the measured capability gap between proposer and judge increase. Fewer remaining premises is not itself a reduction in oversight difficulty.

Define false approval as approved noncompliant submissions divided by all assigned noncompliant submissions, and honest acceptance as approved compliant submissions divided by all assigned compliant submissions. Retain failures and unresolved cases in these denominators and report them separately. A reject-all system passes no usefulness gate. Show human time and compute as separate costs, with any conversion weights declared in advance. Calibrate verification ability on candidate answers as well as standalone task-solving ability. Vary semantic difficulty and evidence dependencies rather than only graph length.

An advantage over prose alone supports formalized oversight. An additional accuracy or effort advantage over the matched structured interface supports VE's language contribution. Failure to improve, reduced coverage, or displacement of errors into vocabulary and evidence limits the claim. A benchmark advantage is evidence on that distribution, not proof of general alignment.

## Frozen conformance corpus

Create 240 independently specified cases, with 160 for development and 80 held out by semantic pattern and vocabulary family:

| Group | Count | Required coverage |
|---|---:|---|
| Claims and finite models | 80 | True/false outcomes, binders, negation, implication, equality, empty domains, vacuity, and finite embedding |
| Commitment and evidence mismatches | 40 | Individually valid but mismatched source/AST, changed descriptions, substituted roots, stale model or proof evidence |
| Arguments and certificates | 40 | Valid composition, explicit repairs, countermodels, missing bridges, extra proof assumptions, negated conclusions, cycles, and conditional roots |
| Invalid syntax, types, or packages | 40 | Free variables, capture/shadowing, wrong arity, unknown IDs, duplicate aliases/keys, missing model tables, and dangling references |
| Unsupported inputs and resource behavior | 40 | Unsupported operators/imports, excessive aggregate size/depth/work, failed proof search, replay limits, and cancellation |

Include at least 20 minimal pairs differing in quantifier order, negation, argument order, domain assumptions, or premise scope. Validate expected outcomes independently of the implementation. Keep this engineering corpus distinct from the human and adversarial efficacy data.

The correctness gate requires zero disagreement with expected parsing, evaluation, binding, certificate, and error outcomes. Rejecting every input fails: supported claims and valid certificates inside the declared budget must succeed, including claims false in a particular model. Fuzzing supplements the corpus; tests do not replace formal proofs.

## Runtime and release scope

Measure the Lean reference before considering another implementation language. Pin hardware, OS, compiler, Lean and package versions, build settings, workloads, and process mode. Report cold start and warm execution separately. Measure source parsing, model validation, finite evaluation, graph checking, proof production and proof replay separately and end to end.

Use the language and argument protocol's provisional size limits. Set latency, memory and proof-search budgets using representative tasks before scored runs. Report resource exhaustion honestly; a slow proof or unsupported task must not disappear from the comparison.

Only a measured runtime or deployment need justifies a Rust/Aeneas slice. Compare it against the reference on scoped binding, parsing, relation lookup, graph validation and errors, including the required refinement obligations and proof-maintenance cost. Compiler assurance remains a separate question; see the [implementation alternatives](architecture-and-design.md#implementation-language-and-proof-tools).

A release claim must identify the supported judgments, task coverage, completed theorems and their dependencies, trusted decoding/display/replay components, reproducible experiment configuration, and known failures. General mathematics, uncertain evidence aggregation, temporal or normative reasoning, public proof-service deployment, and alignment-training guarantees require their own specifications and evidence.
