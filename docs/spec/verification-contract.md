# VE v0: Verification Contract

**Status:** Proposed obligations, September 20, 2026. Every theorem below is pending. This document specifies what evidence an implementation must produce; the prose and pseudocode are not that evidence.

The [language specification](v0-language.md) defines syntax, ASTs, environments, and relational structures. The [debate protocol](debate-protocol.md) defines claims, dependencies, and certificates. The [roadmap](../roadmap.md) determines when a claim may be advertised.

## Objects and independent specification

Let `E` be a validated environment, `s` the exact source bytes, `A` a closed typed AST, `S` an admissible relational structure, and `M` a validated finite model embedded as `asStructure(M)`. Let `ParseSpec(E,s,A)` be the grammar-and-binding relation defined independently of the production parser. Let `Denote(E,A,S)` be the mathematical interpretation from the language specification; use `Denote(E,A,M)` for its finite specialization.

The production parser must implement that relation. Defining `ParseSpec` to mean “whatever the production parser returns” would make a correspondence theorem uninformative. The same separation applies to denotation versus the evaluator. Reference code can accompany the definitions, but reviews must inspect the specification itself.

Vocabulary descriptions and human confirmation establish an intended modeling convention. They do not become axioms asserting facts about the outside world.

Theorems over validated `E` and `M` do not by themselves prove that a JSON decoder or validator constructs those values correctly from submitted bytes. The environment/model decoding boundary remains an explicit trusted component unless separately refined against the wire specification. Conformance tests must exercise malformed packages, but passing those tests does not remove that trust assumption.

## Required obligations

These statements are schematic, with validity premises shown explicitly or supplied by the typed arguments. Their Lean encodings, statement identities, and proof dependencies must be reviewed before a gate passes.

| ID | Obligation | Meaning |
|---|---|---|
| P1 | `ParseSpec(E,s,A) ∧ ParseSpec(E,s,B) → A = B` | The specified grammar and binding rules have one AST, not just one selected parser result |
| P2 | `parseImpl(E,s) = Ok(A) → ParseSpec(E,s,A)` | Every accepted source is parsed correctly; required for `parseRef` and each shipped parser |
| P3 | `ParseSpec(E,s,A) → parseRef(E,s) = Ok(A)` | The unbudgeted reference parser accepts the supported grammar; a reject-everything checker does not qualify |
| P4 | `parseRef(E,print_E(A)) = Ok(A)` | Printing a valid closed AST and parsing it recovers that AST |
| P5 | `normalize_E(normalize_E(s)) = normalize_E(s)` for accepted `s` | Normalization is idempotent; it performs only the specified binder renaming and printing |
| P6 | `evalRef(E,A,M) = true ↔ Denote(E,A,M)` | The finite evaluator agrees with denotation, including false and vacuous cases |
| P7 | `translate(E,A,S) ↔ Denote(E,A,S)` | The generated Lean proposition preserves meaning in every admissible structure, including the finite specialization |
| P8 | successful production parsing/evaluation/graph validation refines the reference behavior on the same inputs | Any optimized or Rust implementation preserves the contracts and operational distinctions |
| P9 | `edgeType(E,Δ,C) ↔ Entails(E,Δ,C)` | The expected certificate proposition expresses the exact submitted premises and conclusion across all admissible structures |
| P10 | certified acyclic composition yields `Entails(E,L,root)` | Composition preserves claim identities and retains every undischarged leaf assumption |
| P11 | `countermodelCheck(E,Δ,C,M) = true → ¬Entails(E,Δ,C)` | A validated finite witness genuinely disproves the stated inference |

`normalize_E(s)` is defined as `print_E(A)` after successful reference parsing; it is an error on rejected text. P3 is for the total reference definition. Runtime completeness is required only within the declared size/work budget; outside it the result must be an explicit resource error. Each reference function needs a termination argument. Success must not depend on proof search terminating.

P4 alone does not establish P2 or P7. Parser and printer implementations could share a mistake. A unique AST also does not establish that its vocabulary matches a person's intention. These are different obligations.

P9–P11 concern the explicit argument semantics. They rely on Lean's permitted proof-checking path for supplied proof terms; they are not proofs of Lean's own kernel or of debate equilibria. A proof of P10 is not evidence that every graph presented by an agent has valid edge certificates.

## Finite-evaluation acceptance contract

For valid `E`, exact bytes `s`, validated `M`, and sufficient resources, the required combined property is:

```text
check(E, s, M) = Result(A, b, record)
  implies
    ParseSpec(E, s, A)
    and A is closed and well typed under E
    and print_E(A) is the recorded canonical text
    and (b = true iff Denote(E, A, M))
    and record identifies exactly E, s, A, and M.
```

Here `b = false` is a valid negative evaluation, not a parsing failure. `Result` is distinct from `InvalidInput`, `UnsupportedProfile`, `ResourceLimit`, and cancellation. A successful outcome cannot discard errors and evaluate a repaired input.

If an untrusted frontend provides `A_candidate`, require equality with the specified AST of `s`, established by the checked parsing path. AST well-formedness alone cannot authorize acceptance. Mutation tests must replace a valid source/AST pair with another individually valid but mismatched pair and observe rejection.

Identity checks bind records to exact inputs, using the encodings in the language specification. Mathematical claims concern the actual values. Cryptographic digests index those values under a collision-resistance assumption; they do not replace parsing, type checking, or meaning correspondence.

For a model-specific proof certificate, derive the expected proposition from the accepted `E`, `A`, and `M` in the trusted checker environment. Verify the proof against that proposition. Do not accept a theorem name, a successful build, or a producer-selected statement as equivalent evidence. A proof of `True` attached to a violated requirement is a rejection case.

Finite evaluation may run without a fresh kernel-checked proof of that result. Deduction certification requires a proof for the particular edge. Development-time theorems about the checker and per-argument certificates are distinct evidence and costs.

## Argument checking contract

For an argument under `E`, parse each claim's exact source and resolve every dependency to its committed AST. Construct `edgeType(E,Δ,C)` from those objects; accept a positive certificate only after checking its proof against that exact proposition in the pinned environment. A proof using an additional assumption cannot certify an edge that omits it. A proof in one environment cannot certify an edge in another by matching display names.

The graph validator rejects cycles, missing claims, conflicting aliases, and stale evidence. For a complete positive derivation, construct the root implication from its checked edges. P10 requires the resulting theorem to retain all undischarged leaves `L`. Display the exact root and `L`; do not present the conditional theorem as an unconditional approval. For an incomplete graph, preserve unresolved obligations rather than silently promoting them to approved assumptions.

A countermodel check validates `M`, evaluates each premise as true and the conclusion as false, and binds the result to `E`, `Δ`, `C`, and `M`. P11 connects these finite computations to failure of general entailment. A model satisfying `C`, or a failed search for countermodels, supplies no positive entailment evidence.

P9 and P11 imply that a sound positive certificate and a valid countermodel cannot coexist for one exact edge. Such a result is `CheckerConflict`, an operational integrity error requiring investigation, not an ordinary combination of inference findings. In contrast, proofs of both the conclusion and its negation imply unsatisfiable premises and may coexist. Conformance checks must exercise this distinction and reject a claimed finite model of those contradictory premises.

Changes to the root, environment, dependencies, leaf assumptions, or certificate invalidate the affected argument record. Human confirmation and evidence judgments apply only to the objects actually reviewed. Exact dependency checking establishes formal correspondence; it does not establish that an unchanged predicate description is an adequate model of reality.

The main research property is that accepted argument composition cannot silently change a committed formal meaning. This requires P1–P7 and P9–P11, correct artifact decoding, and faithful display, with P8 for any differing production implementation. Whether humans can recognize an initially wrong or misleading commitment is measured experimentally, not asserted by these theorems.

## Status and evidence contract

These fields are independent, not a single progress ladder:

| Field and UI label | Evidence required | What it does not establish |
|---|---|---|
| `language: accepted` — “Accepted VE” | Successful specified parsing and type checking, environment identity, exact source and AST | Truth, agreement with ordinary-English intent, or a completed implementation proof |
| `canonical: true` — “Canonical text” | Exact source bytes equal `print_E(A)` | A logical equivalence class for all paraphrases |
| `intent: confirmed` — “Interpretation confirmed by …” | Identified reviewer confirms the claim, environment, descriptions, target scope, and actual displayed rendering with its version | Proof of intent recovery, truth, or completeness of the requirements |
| `evaluation: satisfied/violated` — “Satisfied/violated in inventory …” | Successful evaluation on the identified valid model; checker build and assurance level recorded | Truth about a live system or universal validity across models |
| `inference: findings[]` — “Follows under premises …” / “Negation follows …” / “Counterexample to inference …”; empty means “Unresolved” | Every established `follows`, `refuted`, or `gap` finding, with the certificate or countermodel required by the debate protocol | A `gap` does not make the conclusion false; a conditional proof does not approve its premises; contradictory findings must remain visible |
| `proof: checked` — “Proof checked under listed assumptions” | Exact expected proposition, audited proof dependencies, successful permitted proof-checking path | Unstated assumptions, empirical correctness, or a verified executable binary |

Missing evidence yields `unconfirmed`, `not_evaluated`, `unresolved`, or `not_checked` as appropriate. Operational errors carry their own error codes. A violated formula may still have a checked proof of its negation; record the conclusion explicitly. A human-confirmed statement may still be false. Evidence assessment and the supervisor's final approval remain separate from every checker status.

Show implementation assurance separately: `experimental`, `reference-theorems-checked`, or `production-refinement-checked`, with links to the specific proof/build evidence and covered operations. The finite parsing/rendering/evaluation path requires P1–P6 and the combined acceptance contract. Generated Lean propositions additionally require P7; the full argument layer requires P9–P11 as well, and a differing production implementation requires P8. List the covered operations rather than granting a blanket assurance label. Before the applicable obligations are met, results are experimental. A completed source-level refinement proof does not upgrade compiler correctness.

Changing the source or environment invalidates all attached acceptance/confirmation evidence. A model change invalidates evaluations and model-specific proofs. Unchanged meaning under binder renaming may preserve a meaning-level confirmation only through an explicit, recorded correspondence check; never copy statuses merely because the screen text looks similar.

Evidence support and final approval have separate bindings. A changed evidence snapshot, review scope, or displayed interpretation requires reassessment of affected judgments; an unchanged conditional theorem may still be valid. Proof-checking status must never be copied into an evidence-accepted or result-approved field.

## Proof dependencies and trusted components

Lean distinguishes a well-formed proposition from a proof of it, and kernel checking concerns elaborated terms. That motivates the separate source correspondence and proposition-generation obligations above. [Lean propositions](https://lean-lang.org/doc/reference/latest/The-Type-System/Propositions/), [Lean processing pipeline](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/).

For the v0 release gate, permit only the declared standard logical dependencies `propext`, `Classical.choice`, and `Quot.sound` if used; prefer smaller dependencies where practical. Reject `sorryAx`, extra user axioms, and native-evaluation axioms in claims labeled kernel-checked. Record the transitive dependency list, exact proposition and definitions, Lean version, and package revisions. Domain assumptions belong in the displayed theorem premises rather than hidden global axioms. The allowlist is a project policy, not an assertion that Lean enforces it automatically. [Lean axiom documentation](https://lean-lang.org/doc/reference/latest/Axioms/).

The VE checking interface accepts claim data and proof artifacts, not executable plugins or arbitrary imports. The local prototype's proof worker must be isolated from that interface. Replay its produced declarations in a pinned environment, forbid redefinition of the semantic core, audit transitive dependencies, and compare the proof's type to the trusted expected proposition. Artifact decoding, replay, worker isolation, and display require an explicit implementation contract before agent-produced certificates are accepted. A successful build alone is insufficient. Lean's guidance classes unreviewed AI-generated proofs as potentially malicious input. For that class it recommends writing the theorem statement in a trusted environment and judging the submitted proof against it with `lake comparator`, with external checkers enabled; it treats `lean4checker` replay as a weaker middle tier. Comparator sandboxes the build, matches the proved statement to the trusted one, and permits the same three axioms this contract allows. Evaluate it before designing a custom replay path. The guidance also lists “misleading presentation of the theorem statement” as a remaining trust assumption, which is the step VE assigns to human inspection. [Lean proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

| Path | Trust remaining after its proposed checks |
|---|---|
| Semantic theorems | Correct formal definitions and theorem statements; Lean logic, audited dependencies, selected checker implementation |
| Lean reference executable | Above, plus environment/model JSON decoding and validation unless separately proved, runtime/IO boundary, and compiler behavior; kernel proofs do not verify the binary |
| Argument checking | Above, plus claim/graph/certificate decoding, expected-type binding, replay implementation, assumption display, and isolation from untrusted proof generation |
| Rust before P8 | Rust implementation, parser/model decoder, build chain, and runtime are additionally trusted; tests are empirical evidence |
| Rust after an Aeneas-based P8 | Extraction and its supported-semantics assumptions, bridge to VE reference types, ordinary Rust compiler/runtime, unmodeled interfaces |
| Future verified compilation | Separate source-parser and model-correspondence obligations, compiler theorem scope, linking/runtime assumptions, and machine environment |

The [architecture](../architecture-and-design.md#implementation-language-and-proof-tools) compares implementation paths and their evidence. A change of implementation language does not weaken VE's correspondence obligations. Evidence from another verifier or solver has its own assumptions; label it Lean-kernel-checked only when a translation or certificate has been checked by that path.

Canonical status rendering and identity display are interface responsibilities. Their fidelity must be checked or explicitly trusted; minimizing the semantic core does not remove a misleading display from the user-facing assurance argument.

## Extensions and preservation

A future profile `P` must declare which existing environments, claims, structures, and finite models it embeds. Its compatibility contract must include denotation preservation for general structures, with the finite embedding as a specialization:

```text
DenoteCore(E,A,S) ↔ DenoteP(embedEnv(E),embedAST(A),embedStructure(S))
```

Reusing deduction certificates additionally requires preservation of logical consequence over the target profile's admissible structures; agreement only on selected example models is insufficient. Any new restriction on structures or domain axiom must be explicit in the profile and its premises.

New syntax must also preserve the interpretation of previously accepted core documents under their original version. State how partial or absent embeddings fail. A vocabulary addition cannot change an old identifier's meaning. No implication from belief to truth, obligation to fact, or closed-world absence to open-world falsity may appear without an explicit rule and its premises.

Pairwise module tests are not a general composition proof. Specify a concrete supported profile, its assumptions, and its operator interactions, and prove the fragment actually advertised. v0 uses one relational profile for both judgments; its finite-model embedding must preserve denotation. Generalizing the argument language does not automatically extend the finite evaluator or preserve an oversight protocol's incentive guarantees.
