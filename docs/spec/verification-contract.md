# VE v0: Verification Contract

**Status:** Proposed obligations, September 20, 2026. Every theorem below is pending. This document specifies what evidence an implementation must produce; the prose and pseudocode are not that evidence.

The [language specification](v0-language.md) defines syntax, ASTs, environments, and finite models. The [roadmap](../roadmap.md) determines when a claim may be advertised.

## Objects and independent specification

Let `E` be a validated environment, `s` the exact source bytes, `A` a closed typed AST, and `M` a validated finite model. Let `ParseSpec(E,s,A)` be the grammar-and-binding relation defined independently of the production parser. Let `Denote(E,A,M)` be the mathematical interpretation from the language specification.

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
| P7 | `translate(E,A,M) ↔ Denote(E,A,M)` | A generated Lean proposition expresses the intended formal conclusion rather than an unrelated theorem |
| P8 | successful production parsing/evaluation refines the reference behavior on the same inputs | Any optimized or Rust implementation preserves the contracts and operational distinctions |

`normalize_E(s)` is defined as `print_E(A)` after successful reference parsing; it is an error on rejected text. P3 is for the total reference definition. Runtime completeness is required only within the declared size/work budget; outside it the result must be an explicit resource error. Each reference function needs a termination argument. Success must not depend on proof search terminating.

P4 alone does not establish P2 or P7. Parser and printer implementations could share a mistake. A unique AST also does not establish that its vocabulary matches a person's intention. These are different obligations.

## End-to-end acceptance contract

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

For a proof certificate, derive the expected proposition from the accepted `E`, `A`, and `M` in the trusted checker environment. Verify the proof against that proposition. Do not accept a theorem name, a successful build, or a producer-selected statement as equivalent evidence. A proof of `True` attached to a violated requirement is a rejection case.

v0 may evaluate a result without producing a fresh kernel-checked proof of that result. P1–P7 are development-time metatheory obligations; per-result certificates are a separate capability and cost. An optional future certificate-producing solver could leave its search procedure untrusted, but the certificate checker would still need soundness and input correspondence. No solver or certificate protocol is selected now.

## Status and evidence contract

These fields are independent, not a single progress ladder:

| Field and UI label | Evidence required | What it does not establish |
|---|---|---|
| `language: accepted` — “Accepted VE” | Successful specified parsing and type checking, environment identity, exact source and AST | Truth, agreement with ordinary-English intent, or a completed implementation proof |
| `canonical: true` — “Canonical text” | Exact source bytes equal `print_E(A)` | A logical equivalence class for all paraphrases |
| `intent: confirmed` — “Interpretation confirmed by …” | Identified reviewer confirms this canonical rendering, environment, definitions, and declared finite-model scope | Mathematical proof or independent accuracy of the model |
| `evaluation: satisfied/violated` — “Satisfied/violated in inventory …” | Successful evaluation on the identified valid model; checker build and assurance level recorded | Truth about a live system or universal validity across models |
| `proof: checked` — “Proof checked under listed assumptions” | Exact expected proposition, audited proof dependencies, successful permitted proof-checking path | Unstated assumptions, empirical correctness, or a verified executable binary |

Missing evidence yields `unconfirmed`, `not_evaluated`, or `not_checked`. Operational errors carry their own error codes. A violated formula may still have a checked proof of its negation; record the conclusion explicitly. A human-confirmed statement may still be false in a particular inventory.

Show implementation assurance separately: `experimental`, `reference-theorems-checked`, or `production-refinement-checked`, with links to the specific proof/build evidence. Before P1–P7 are proved, an implementation may report experimental results but cannot advertise the full formal contract. A completed source-level refinement proof does not upgrade compiler correctness.

Changing the source or environment invalidates all attached acceptance/confirmation evidence. A model change invalidates evaluations and model-specific proofs. Unchanged meaning under binder renaming may preserve a meaning-level confirmation only through an explicit, recorded correspondence check; never copy statuses merely because the screen text looks similar.

## Proof dependencies and trusted components

Lean distinguishes a well-formed proposition from a proof of it, and kernel checking concerns elaborated terms. That motivates the separate source correspondence and proposition-generation obligations above. [Lean propositions](https://lean-lang.org/doc/reference/latest/The-Type-System/Propositions/), [Lean processing pipeline](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/).

For the v0 release gate, permit only the declared standard logical dependencies `propext`, `Classical.choice`, and `Quot.sound` if used; prefer smaller dependencies where practical. Reject `sorryAx`, extra user axioms, and native-evaluation axioms in claims labeled kernel-checked. Record the transitive dependency list, exact proposition and definitions, Lean version, and package revisions. Domain assumptions belong in the displayed theorem premises rather than hidden global axioms. The allowlist is a project policy, not an assertion that Lean enforces it automatically. [Lean axiom documentation](https://lean-lang.org/doc/reference/latest/Axioms/).

v0 accepts data packages, not arbitrary submitted Lean programs, plugins, or imports. Project-generated proof artifacts must be checked in the pinned environment, with independent replay of stored declarations where supported. If a later service accepts unreviewed external proof-generating code, its design must additionally protect the environment and compare the resulting statement to a trusted challenge; a successful build alone is insufficient. [Lean proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

| Path | Trust remaining after its proposed checks |
|---|---|
| Semantic theorems | Correct formal definitions and theorem statements; Lean logic, audited dependencies, selected checker implementation |
| Lean reference executable | Above, plus environment/model JSON decoding and validation unless separately proved, runtime/IO boundary, and compiler behavior; kernel proofs do not verify the binary |
| Rust before P8 | Rust implementation, parser/model decoder, build chain, and runtime are additionally trusted; tests are empirical evidence |
| Rust after an Aeneas-based P8 | Extraction and its supported-semantics assumptions, bridge to VE reference types, ordinary Rust compiler/runtime, unmodeled interfaces |
| Future verified compilation | Separate source-parser and model-correspondence obligations, compiler theorem scope, linking/runtime assumptions, and machine environment |

The [architecture](../architecture-and-design.md#implementation-language-and-proof-tools) compares implementation paths and their evidence. A change of implementation language does not weaken VE's correspondence obligations. Evidence from another verifier or solver has its own assumptions; label it Lean-kernel-checked only when a translation or certificate has been checked by that path.

Canonical status rendering and identity display are interface responsibilities. Their fidelity must be checked or explicitly trusted; minimizing the semantic core does not remove a misleading display from the user-facing assurance argument.

## Extensions and preservation

A future profile `P` must declare which existing `E`, `A`, and `M` it embeds. Its compatibility contract must include a statement of the form:

```text
DenoteCore(E,A,M) ↔ DenoteP(embedEnv(E),embedAST(A),embedModel(M))
```

New syntax must also preserve the interpretation of previously accepted core documents under their original version. State how partial or absent embeddings fail. A vocabulary addition cannot change an old identifier's meaning. No implication from belief to truth, obligation to fact, or closed-world absence to open-world falsity may appear without an explicit rule and its premises.

Pairwise module tests are not a general composition proof. Freeze a concrete supported profile, its assumptions, and its operator interactions, and prove the fragment actually advertised. v0 avoids this unresolved obligation by admitting one profile only.
