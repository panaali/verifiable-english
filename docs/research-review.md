# Critical review and recommended first study

**Review date:** September 20, 2026. This is a document and source review, not an experiment or proof audit. All seven active project documents were reviewed; the archived brainstorm was not used. Recommendations below are design judgments unless attributed to a source. No VE implementation, participant study, or benchmark run exists in this repository.

## Assessment

VE is worth a bounded investigation as an interface for reviewing formal requirements and their supporting evidence. The case for building a new language, a fully verified implementation, or a debate-based alignment system is not yet established.

The strongest part of the design is its separation of model satisfaction, logical consequence, interpretation confirmation, and factual evidence. Preserve that separation. Exact claim references and assumption-preserving composition are useful even if the English surface fails. Their implementation would establish correspondence to an explicit formal model, not eliminate uncertainty about what the model represents.

The central risk is **a valid argument about the wrong concepts**. In the merged-vocabulary example, the formal deduction is correct. The evidence does not establish its premises under one common interpretation. Calling this a checker failure obscures the problem: the missing work is specification and evidence review. A proof badge could help by making that work visible, or hurt by making it seem already completed.

The research opportunity is to measure and improve that review step. Existing English-to-logic systems substantially limit the language-level novelty claim. A successful contribution could be a review method, attack corpus, or interface result even if the eventual syntax comes from another system.

## Separate the claims being tested

| Claim | Evidence needed | What would not establish it |
|---|---|---|
| Exact commitments prevent unnoticed changes to formal objects | Parser/display correspondence, reference binding, and assumption-preserving composition | A successful proof of a producer-selected statement |
| The English presentation improves human review | Same AST, evidence, checking, and assistance; vary the presentation | VE plus a checker beating prose without one |
| The evidence interface improves grounding | Same presentation and proofs; vary cross-claim evidence inspection | Fewer premises or more certified edges |
| Debate improves oversight beyond a critique | Same task and tools; compare one critique with further exchanges and charge their costs | Adding a stronger critic only to VE |
| Better judgments improve training or alignment | A subsequent training study and a stated deployment argument | Higher accuracy in a prompted evaluation |

The first formal claim is an engineering obligation. The next three are empirical hypotheses and may have different answers. The final claim is a separate research program.

## Priority findings

| Priority | Finding | Consequence for the project |
|---|---|---|
| First | Vocabulary identity does not establish consistent grounding | Review all evidence uses of a predicate together; include vague shared predicates in every attack set |
| First | The application distribution is unspecified | Choose a narrow user and task before measuring coverage or declaring that most realistic tasks do not fit |
| First | The original comparison bundles language, checking, and debate | Use staged matched comparisons; do not run every possible combination in a tiny pilot |
| First | There is no demonstrated reason for multiple debate rounds | Retain a single-critique baseline and measure critic verification ability |
| Next | Canonical serialization and readable presentation are unnecessarily coupled | Test a read-only AST-derived view before expanding the parser |
| Next | Some skeptical statements exceed the evidence | Remove assumptions about model readability, universal checker decidability, and the absence of related work |
| Next | Finding combinations and evidence freshness need stronger contracts | Distinguish inconsistent premises from a proof/countermodel conflict; bind review judgments to evidence snapshots |

### Grounding needs its own review action

For the service example, show the reviewer a predicate-use panel containing the predicate's description, every premise that uses it, and the cited evidence for each use. Ask whether operations records and the security policy support the same interpretation of `reviewed`. Allow a split into `ops_reviewed` and `security_reviewed`, with any bridge premise shown explicitly.

This is a proposed procedural defense, not a formal definition of review or a guarantee that the supervisor notices the problem. It should be available to matched non-English interfaces too. Record which uses and evidence were inspected. If the available budget does not cover a necessary premise, the review can remain unresolved; a checked derivation cannot fill that gap.

An evidence item should identify the inspected content, its relevant passage or record, the claim it is offered to support, and the scope in which that support is asserted. A URL alone does not identify a stable document. Version changes can invalidate an evidence judgment while leaving the mathematical implication intact. A fixed snapshot can also remain the same while becoming irrelevant to a later deployment; scope and freshness are separate review questions.

### Test understanding with distinguishing cases

A reviewer can agree with both a formula and its paraphrase while misunderstanding both. Include small inventories on which two plausible readings differ. For example, “every deployed service has an owner” permits different owners; “one person owns every deployed service” does not. An inventory with two services and different sole owners distinguishes the readings.

Use independently prepared examples and include cases the candidate formalization mishandles. Ask reviewers to predict satisfaction and explain or repair the mismatch before showing the checker outcome. Do not show only examples selected by the proposer. This adapts the interpretation-testing approach in [Kuhn's study](https://attempto.ifi.uzh.ch/site/pubs/papers/kuhn2013swj.pdf) and the formula/trace distinction in [Little Tricky Logic](https://arxiv.org/pdf/2211.01677); neither study establishes VE's effectiveness under adversarial pressure.

### A readable view does not require a richer input language

Keep the indexed AST and strict source grammar for the initial prototype. Separately test generated wording such as “Every deployed service is reviewed,” with explicit predicate descriptions and expandable scope. More complex forms can fall back to the strict rendering. Do not silently omit an existence condition, quantifier dependency, or premise.

For the disposable pilot, independently reviewed hand-renderings suffice. For a deployed view, specify the supported rendering templates and their semantic correspondence, identify the renderer version, and bind confirmation to the actual displayed artifact. No free-form LLM paraphrase should become authoritative merely because it accompanies a checked AST. FRET's [multiple representations and interactive simulation](https://software.nasa.gov/software/ARC-18066-1) are a relevant design precedent; a new display alone is not a novelty claim.

## Candidate applications beyond debate

These are design judgments about where the core of VE, human sign-off on precise claims plus checked composition, could matter most. None has been validated with users. They are ordered by the reviewer's confidence.

1. **Reading formal statements that AI systems produce.** As agents deliver machine-checked proofs and verified code, a person still has to confirm that the theorem or specification says what they intended. Rendering an existing formal statement as controlled English is deterministic printing. It avoids parsing ambiguity and needs a smaller proof burden than accepting English input. This limited search found no controlled study of whether people detect wrong formal specifications from English renderings. The [architecture](architecture-and-design.md#why-the-benefit-could-scale) explains why this step bears on scalable oversight.
2. **Policies and rules that non-experts approve.** Agent permissions, access control, compliance rules and deployment gates are largely relational and finite, so they are more likely to fit v0. The approver is a real human who does not read logic, and ground truth is formal, so experiments are clean. Countermodels become the main interaction: show a concrete scenario that the policy as written permits and ask whether it was meant to be allowed. The same machinery can show how an edit changes a policy's meaning. The provisional service-deployment application below belongs to this family.
3. **Disambiguation by example during authoring.** The weak link in every workflow is the first formalization, and controlled wording alone does not fix it. Given ambiguous prose, generate the candidate readings and show the author a small scenario on which two readings give different answers. The [distinguishing cases](#test-understanding-with-distinguishing-cases) above use this idea to test reviewers; here it becomes the way a specification is written. The assumption that people judge concrete cases more reliably than quantified statements needs its own check.

Debate remains a consumer of the same core. The [architecture](architecture-and-design.md#how-the-benefits-apply-to-debate) maps each mechanism to its role in a debate and states the limit: VE reduces how much must be debated and leaves the evidence and vocabulary disputes untouched. The first study below serves both uses, because both depend on whether people can reliably sign off on claims.

## Recommended first study

**Provisional audience and application:** humans reviewing bounded service-deployment requirements, inventories, and evidence packets, assisted by a proposer and critic. This extends the existing examples and uses predicates and relations v0 already supports. It is a candidate to validate with prospective users, not evidence of demand. Model judges can help calibrate attacks but cannot stand in for these participants.

1. **Define the task distribution.** Gather a small sampling frame of independently sourced requirements from the chosen workflow. Record provenance and inclusion rules before formalizing. A provisional coverage screen is 30 randomly selected requirements; report counts and uncertainty, not just a percentage. Separate directly expressible claims, claims needing independently specified input adapters, and claims whose difficult content remains an opaque judgment. Survey ReaLMistake separately only if making a claim about that benchmark.
2. **Prepare 24 mechanism cases.** As a planning budget, use six families with four cases each: faithful arguments, quantifier/implication changes, vacuity or omitted requirements, merged vocabulary, unsupported or stale evidence, and legitimate repairs. Include a small distinguishing inventory or a precise evidence-based scoring rationale for each. These authored cases diagnose mechanisms; they do not estimate prevalence in real deployments. Independent review of labels is still required.
3. **Calibrate the baseline.** Use prose with cross-examination, a shared glossary, and the same evidence access. Confirm that the attacker can exploit simpler controls and that honest cases remain answerable. Measure the critic's ability to identify flawed submissions independently of its ability to solve the underlying task. A weak attacker, an ineffective critic, or a saturated judge can make a null result uninformative.
4. **Run a small interface pilot.** Use roughly 8–12 participants to diagnose failures, distributing equivalent variants so each person sees a case only once. Hold the claim graph and checking results fixed across a structured interface, strict VE, and a more natural read-only view. Provide equivalent evidence and scope tools. Use the same prepared critique across matched cases for this diagnostic comparison. A later adaptive study must allow agents to respond to the interface.
5. **Inspect proof-label effects separately.** On matched arguments whose deductions really are valid, compare an inference-status label with a fuller display of outstanding evidence obligations. Include both faithful and wrong-but-valid submissions. Do not invent proof success for invalid deductions. This is a distinct intervention; do not attribute its effect to the English wording.
6. **Make a documented decision.** Keep the interface only if participants can use it and it has a credible path to improving accuracy or effort. Keep debate only if further rounds add value over a critique. Begin the verified implementation after identifying a useful workflow and a reviewable artifact contract.

The counts above are proposed scope limits, not powered efficacy-study sizes. Recruitment and independent labeling may take longer than the document preparation. No claim that these steps necessarily take only days is warranted.

### Decisions and metrics to freeze before scoring

The pilot diagnoses usability; it cannot establish equivalence from a nonsignificant result. Before a larger held-out study, record the minimum useful benefit, maximum acceptable loss in honest acceptance, coverage requirement, and separate human and compute budgets. Select these from the workflow's needs and pilot variance, not from which thresholds make the observed result look good.

Define the main rates over assigned cases, not just completed proofs:

```text
false approval = approved noncompliant submissions / assigned noncompliant submissions
honest acceptance = approved compliant submissions / assigned compliant submissions
unresolved rate = cases without a final substantive decision / all assigned cases
```

Also report malformed inputs, unsupported tasks, timeouts, repairs, review time, model calls, tokens, proof cost, and evidence queries. A method that rejects or times out on everything can achieve zero false approvals and still be useless. Review time, tokens, and money are different quantities: publish a cost breakdown and several budget points before choosing any scalar conversion.

Use two distinct evaluations. Fixed candidate arguments with matched critiques identify presentation effects. Adaptive proposers and critics estimate end-to-end performance, including formalization failures. Preserve the distinction between a wrong initial commitment and a later attempted change. Vary semantic depth, leaf difficulty, and evidence dependencies; padding a graph with trivial nodes does not establish scaling.

| Observation | Appropriate decision |
|---|---|
| The application mostly needs semantics outside v0 | Narrow the application or specify a justified extension before implementation |
| The baseline rarely fails and attacks are demonstrably effective on controls | Reconsider this attack family as the primary motivation; report uncertainty |
| English and structured views remain indistinguishable in a sufficiently powered study | Prefer the cheaper usable interface; retain useful checking machinery |
| The proof display increases false approval of grounding errors | Redesign the display and repeat that test before advancing |
| One critique matches multi-round debate at lower cost | Use one critique for this workflow |
| A small pilot is noisy or at ceiling | Improve measurement and task calibration; do not claim success or impossibility |

## Technical issues worth preserving in the specification

- **Inconsistent premises and conflicting checker evidence differ.** `follows` and `refuted` together imply unsatisfiable premises. `follows` and a valid `gap` for exactly the same edge cannot both be correct. The latter requires an integrity error and investigation of binding, semantics, or checking.
- **Finite countermodels are incomplete even without a size cap.** v0 permits claims whose only models are infinite. Absence of a finite witness cannot be treated as a nearly complete refutation procedure. The language specification now gives an explicit example.
- **General deductions and finite inventories answer different questions.** An example inventory does not implicitly restrict every structure quantified over by `Entails`. If a proof needs domain closure, declare it or choose a separately specified finite judgment.
- **Evidence judgments need independent invalidation.** A changed evidence snapshot or target deployment can invalidate approval without changing a formula. Mathematical proof validity must not be confused with current factual support.
- **Assurance should match operations.** Parser/evaluator results need the relevant correspondence obligations. P7 is additionally needed when advertising generated Lean propositions; it should not be required merely to run finite evaluation. Full verified-release claims still require the complete advertised contract.

These are specification observations, not newly proved Lean theorems. The current language remains a proposal and its resource limits are unmeasured.

## Source-review record

This was a targeted review of relevant sections, not an exhaustive literature search or independent reproduction of reported experiments. Links identify the material used; where possible, arXiv revisions are fixed.

| Source inspected | What the review changes or confirms |
|---|---|
| [Buhl et al., v3, §4.4.2](https://arxiv.org/html/2505.03989v3#S4.SS4.SSS2) | The branch-definition concern is real, but its discussion is not a prevalence study or evidence that VE solves it |
| [Prover-estimator debate, v2, introduction and §8](https://arxiv.org/html/2506.13609v2) | Distinguish the corrected stability-dependent completeness claim from soundness; the formal-proof integration remains a research suggestion |
| [Debate query complexity, v1, introduction and conclusion](https://arxiv.org/html/2602.08630v1) | Unbounded-debater results do not estimate VE's authoring, proof-generation, or human interpretation costs |
| [Chen et al., v2, Figure 4 and Tables 1, 9](https://arxiv.org/html/2510.20963v2) | Retain the attack illustration and acknowledge the behavioral analysis; compare strong single-agent and voting baselines, and distinguish heterogeneous from identical-model settings |
| [Elasky et al., v1, §§3–5](https://arxiv.org/html/2605.27483v1) | The relevant methods and results have now been read, beyond the abstract. Their comparison is with consultancy and their results do not establish a universal critic-advantage law |
| [FormalJudge, methods, limitations, and evaluation appendices](https://arxiv.org/html/2602.11136) | Formal checking still depends on intent decomposition and fact extraction. Model-oracle labels in parts of the evaluation support agreement claims, not independently established correctness |
| [Gordon and Matskevich, v1, §§3, 5–7](https://arxiv.org/html/2310.03885v1) | The predecessor addresses lexical manipulation as well as certified translation; VE should not claim either problem as newly identified |
| [Kuhn, §§5–6](https://attempto.ifi.uzh.ch/site/pubs/papers/kuhn2013swj.pdf), [Fuchs, §5](https://attempto.ifi.uzh.ch/site/pubs/papers/cnl2018main_fuchs.pdf), [Greenman et al., study design and task distinctions](https://arxiv.org/pdf/2211.01677) | Separate learning time from review speed; assess understanding with concrete cases; apparent familiarity with English does not establish the intended reading |
| [Kenton](https://arxiv.org/abs/2407.04622v2), [Khan](https://arxiv.org/abs/2402.06782v4), [Michael](https://arxiv.org/abs/2311.08702), [Parrish](https://arxiv.org/abs/2210.10860) — abstracts checked | Narrow the combined literature summary to the stated tasks and comparators; these papers were not reanalyzed in full in this review |
| [ReaLMistake README](https://github.com/psunlpgroup/ReaLMistake) | Confirm task families and the request not to publish examples in plain text; no benchmark examples were downloaded or scored |
| [Lean proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) | Confirms the separate trusted statement, sandboxed build, exported proof checking, and remaining presentation assumptions; no toolchain was installed or tested |
| [Logical English demonstration](https://www.doc.ic.ac.uk/~rak/papers/Logical_English_Demonstration_for_ICLP.pdf), [PENG publication abstract](https://researchers.mq.edu.au/en/publications/representing-knowledge-in-controlled-natural-language-a-case-stud/), [FRET README](https://github.com/NASA-SW-VnV/fret) | Replace missing references and identify reusable interface ideas; no implementation compatibility is claimed |
| [Canonical English site](https://canonical-english.org/), [TrojanSpec-Bench README](https://github.com/m-zest/TrojanSpec-Bench-v1.0) | Treat both as project descriptions requiring artifact review. Failure to fetch a repository does not prove that code does not exist; reported benchmark claims are not reproduced here |

The wider compiler/toolchain comparison was not independently audited in this pass. Its options are downstream of the research decision. Neither this review nor the existing specifications supplies evidence that VE improves oversight yet.
