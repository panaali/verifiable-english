# VE v0: Experiments and Acceptance Criteria

**Status:** First draft. All gates are **not started**. Numerical targets are provisional experiment budgets, not measured results.

The [architecture](architecture-and-design.md) explains the workflow, rationale and alternatives. The [language specification](spec/v0-language.md) and [verification contract](spec/verification-contract.md) define the rules being tested.

## Order and decision gates

| Gate | Deliverable and effort cap | Pass condition | Failure or fallback |
|---|---|---|---|
| G0 — Establish task fit and freeze the experiment | Task stories, corpus, exact schema/package format, machine profile, and dependency pins; initial allowance 2 focused engineering days | Representative author/submit/check/revise workflows have useful acceptance conditions expressible in the profile; every corpus item has an independently reviewed expected AST/error and model outcome where applicable | Revise the profile or explicitly narrow the intended workflow; do not conceal missing computations in agent-supplied predicates or proceed with undefined labels |
| G1 — Reference core and formal contracts | Small Lean definitions, parser/printer, model validator, evaluator, and P1–P7; 10 focused engineering days | All required proofs kernel-checked with audited dependencies; all frozen conformance cases correct; no placeholder axioms | Produce a concrete obstruction and revise grammar, semantics, or proof approach; do not add domains to conceal failure |
| G2 — Authoring and exchange prototype | CLI first, then only the interface needed for the pilot; 5 focused engineering days | Complete the worked workflow, reject mismatched artifacts, preserve provenance, and meet the pilot criteria below | Simplify the surface or retain typed forms as the interface; checker work remains reusable |
| G3 — Runtime measurement | Measure Lean reference first on fixed workloads; 2 focused engineering days | The selected runtime meets the latency/memory envelope | Profile failures, optimize the reference or investigate Rust, and rerun G3; identifying a bottleneck alone does not pass |
| G4 — Conditional runtime/proof comparison | Optimized reference versus a representative Rust/Aeneas slice, only after a measured runtime or concrete deployment need; 5 focused engineering days | Same required behavior and workload; demonstrated slice refinement including failure paths; enough measured deployment/performance benefit to justify recorded implementation and proof-maintenance cost | Retain Lean reference or narrow deployment scope; ordinary Rust may remain an untrusted proposer. Do not claim full refinement or require a compiler-compatible subset |
| G5 — Release decision | Reproducible evidence bundle and scope review; 1 focused engineering day | Mandatory G0–G3 passed; claims match delivered proof scope; any trusted implementation differing from the reference definitions also has full P8 | Release only an explicitly experimental prototype or pause the proposed product workflow |

Estimate delivery effort from the first representative implementation/proof slice. Track human effort, agent runs, compute cost and unresolved issues. A successful G4 slice supports deciding whether to fund full refinement; it does not satisfy P8 for the whole runtime.

The gates are release obligations, not a requirement to finish all formal proofs before learning from users. Start G2 when an experimental reference slice passes the independently reviewed workflow cases; label its results experimental while G1 is incomplete. G3 may also measure that slice. Do not fund a second runtime or complete an unwanted surface solely to preserve the order of the table.

G0 freezes the schema/model wire fields and semantic artifact encoding from the proposed specification into a machine-readable format contract. If this exposes omissions or inconsistencies, update that specification first. The implementation must not invent unrecorded defaults.

Task stories must identify the intended user, submitted artifact, facts supplied versus computations checked, a passing submission, a meaningful violation, and a revision that invalidates old evidence. Record required arithmetic, counts, n-ary relations, external observations or time-dependent behavior that the proposed fragment cannot express. Do not drop an essential task merely to make the current grammar pass. If temporal requirements are central, compare FRET before inventing a temporal extension.

During the first G1 slice, compare the proof burden of intrinsically typed ASTs with raw syntax plus well-formedness evidence for nested binding and printing. Keep the same wire AST. Choose one representation and record the reason; this is not a mandate to build two complete implementations. If a material Lean-specific obstacle remains, compare the same obligation in Rocq when available expertise or reusable work makes that comparison useful.

## Frozen correctness corpus

Create 240 authored cases, split into 160 development and 80 held-out cases by semantic pattern and vocabulary family, not random near-duplicates:

| Group | Count | Required coverage |
|---|---:|---|
| Well-typed documents with valid finite models | 120 | Both satisfied and violated outcomes; alternating quantifiers, negation, implication, equality, alpha-renaming, empty domains, and vacuous satisfaction |
| Mismatched artifact/evidence packages | 40 | Individually valid text/AST pairs that disagree; changed environment or model with stale evidence; wrong proof conclusion |
| Invalid syntax, types, or models | 40 | Free variables, capture/shadowing, wrong relation arity, unknown identifiers, omitted relation tables, duplicates, dangling entities, invalid bytes |
| Unsupported profiles and exceeded limits | 40 | Temporal/modal language, unknown imports, embedded code, excessive size/depth/work, and cancellation |

Every corpus group has explicit expected outputs, including distinctions between a false formula and an invalid input. Include at least 20 minimal pairs that change quantifier order, negation scope, argument order, or domain assumptions. Authors document why each changed meaning differs. Validate labels independently of the production parser/evaluator; using its output as the gold answer would make the test circular.

The correctness gate requires **zero incorrect acceptance, source/AST mismatch, evaluation disagreement, stale-evidence reuse, or unsupported-input fallback** across the frozen corpus. Rejecting every input fails: all supported well-typed cases inside the resource envelope must be accepted, including false formulas. Hold-out results are reported once before fixes; later fixes create a new version of the corpus and a fresh hold-out set.

Property-based generation and fuzzing extend this corpus but do not replace the proofs. Report seed, generated case count, limits, and failures. A passing finite test suite is never presented as proof of universal correctness.

## Usefulness and authoring pilot

Recruit eight pilot users and assign twelve service-inventory tasks per person, with counterbalanced equivalent variants across these three conditions:

1. ordinary prose plus clarification, followed by an explicitly inspected formal constraint;
2. a typed form/JSON constraint editor;
3. VE with assisted authoring and canonical back-translation.

All conditions use the same schema, finite evaluator, model cases, and result capabilities. Each receives the same assistance budget and any shared model/version is recorded. At least four tasks per person per condition, with changed entity names/data to reduce memorization. Use an expert-reviewed expected interpretation, blind to the assigned interface where practical. The pilot is exploratory, not a population-level efficacy claim.

Initial progression thresholds:

- At least 80% of VE tasks reach the correct confirmed interpretation and evaluation within ten minutes each.
- No silently wrong confirmed interpretation in the pilot; any such error triggers diagnosis and a revised interface before progression. This empirical result cannot establish perfect intent recovery.
- Median clarification count is at most two per completed VE task.
- VE's task accuracy is at least that of each baseline, and median completion time is no more than 1.25 times the faster baseline at comparable accuracy.
- At least six of eight users correctly distinguish “Accepted VE,” “Interpretation confirmed,” and “Satisfied in inventory” on the post-task check.

Report failures and individual distributions, not just successful examples or averages. If typed forms perform better without a compensating readability benefit, do not force an English surface into the first product. Retain the formal core and revise the interface hypothesis.

The participant count and numerical thresholds are initial exploratory budgets, not a power analysis or validated usability standard. Calibrate tasks and limits before scored runs, publish the rationale, then freeze them. Include manual authoring and track failures caused by punctuation, identifiers, canonical wording and misunderstood vacuity; model-assisted success alone does not establish that people can inspect the result.

## Runtime measurements

Before optimization, publish one pinned machine profile: hardware, OS, compiler, Lean version, dependency commits, build flags, and process mode. Use warm local execution, one request at a time, exclude network/LLM calls, and report cold-start separately.

The typical workload contains at most 20 statements, 2,000 AST nodes, 100 entities per sort, 1,000 relation tuples, and 100,000 evaluator node steps. Measure at least 1,000 repetitions across distinct published inputs. Initial targets are p95 at most 100 ms for parsing/type checking/canonical printing, p95 at most 250 ms for evaluation, and peak process RSS at most 256 MiB. Report proof-generation/checking time separately rather than hiding it inside or excluding it from an end-to-end claim.

The hard limits in the language specification define a larger rejection envelope, not a latency promise. Deep quantifier alternation can exhaust the evaluator budget even within size limits. It must yield `ResourceLimit`, never a false result. Test adversarial cases at and beyond the bounds, including cancellation and partial reads.

Keep the reference runtime if it meets the useful workload. Otherwise, profile the bottleneck and compare optimization against a small Rust experiment. Performance improvement must preserve P2/P6/P8 and the supported input scope.

The numerical targets are initial application budgets, not evidence that Rust, C or Lean will meet them. Reassess them against the selected task and machine before freezing the measurement plan. Quantifier enumeration can dominate the algorithm in any language; changing languages alone is not an answer to a combinatorial workload.

## Toolchain and automation experiments

For G4, record exact Rust, Charon/Aeneas, Lean, and library revisions; licenses; invoked commands; unsupported constructs; assumptions about external definitions; and generated artifacts. If using hax, pin it too and document that its current Lean backend invokes Charon/Aeneas rather than providing an independent proof path. The slice must include scoped binding, relation lookup, recursive traversal, error propagation, and the actual proposed data representation. Proving a trivial arithmetic function does not validate a parser/checker pipeline.

Check supported constructs and relevant regression cases at the pinned tool versions. Measure proof repair after a deliberate grammar change as well as initial success. Add Kani or Verus only for a specific property or proof-effort question with its own trust account.

Measure AI assistance on representative implementation, proof, and deliberate-change tasks. Record attempts, successful checked artifacts, human corrections, axiom audits, and proof maintenance after changing a grammar rule. Passing evidence is the artifact and its checks, not the model's explanation. No external model benchmark is a prerequisite or a substitute.

Canonical English collaboration is optional research, not a gate. Assess source availability, license, semantics, and integration cost if a concrete component would help. Do not wait for another project to define the v0 core.

If compiler verification becomes a requirement, first compare C/VST/CompCert and HOL4/CakeML, with RustCompCert as another candidate after a pinned compatibility demonstration. Check supported targets, source-proof/compiler semantics, input and IO boundaries, proof maintenance, and dependency licenses. A Frama-C proof plus a CompCert build does not by itself establish a checked bridge between the chosen models. No verified-compilation path is required for v0, and a syntactic subset accepted by two tools is not enough.

## Evidence required for a release claim

Publish the specification revision, frozen corpus and outcomes, exact toolchain pins, proof statements and dependency audits, replay logs, runtime results, pilot results, known limitations, and artifact-identification rules. Include failed cases and link each advertised guarantee to its evidence.

The v0 decision concerns bounded requirements exchange. Broader mathematics, temporal reasoning, science, and law each require a new profile specification and a new acceptance gate before being advertised as supported.
