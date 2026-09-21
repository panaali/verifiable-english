# Verifiable English: Architecture and Design

**Status:** First draft. Implementation, proofs, and usability results are pending.

Verifiable English (VE) is an English-like language with precise, machine-checkable semantics for humans and AI agents. Its first workflow is **human–agent requirements exchange**: agree on typed constraints, submit a finite result, and check whether that result satisfies them.

This document explains the design choices and alternatives. The [language specification](spec/v0-language.md) defines syntax and semantics, the [verification contract](spec/verification-contract.md) defines guarantees, and the [roadmap](roadmap.md) defines experiments and acceptance criteria.

## First useful workflow

A human asks an agent to prepare a service inventory. The constraints require at least one deployed service and an owner and review for every deployed service.

1. The human and agent choose a local typed vocabulary and the finite-model profile.
2. Assisted authoring proposes VE constraints. The checker parses the exact text and displays canonical wording, quantifier scope, and vocabulary definitions.
3. The human confirms that interpretation against the document and environment identities.
4. The agent submits a complete finite inventory under that vocabulary.
5. The checker reports satisfied, violated, or an operational error, with an explanatory binding or trace where applicable.
6. The result identifies the exact constraints, vocabulary, inventory, and checker build. Changed inputs invalidate attached evidence.

The [worked example](spec/v0-language.md#worked-example) includes a passing inventory and meaningful failures. The checker establishes conformance of submitted records. Whether those records describe an actual deployment or completed review requires independent evidence.

Before freezing v0, representative tasks must fit this model. A required computation must not become an agent-supplied `compliant` flag. Counts, dates, time-dependent behavior, or external observations may require a richer profile or a specified input adapter.

## Language choices

| Choice | Rationale | Tradeoff or alternative |
|---|---|---|
| Many-sorted, function-free first-order formulas over a finite structure | Supports explicit quantifiers, relationships, equality, and a terminating evaluator | Arithmetic, functions and n-ary relations may be needed by real tasks; task fit must be tested |
| Local typed predicates, constants, and descriptions | Makes the vocabulary available without network resolution and exposes modeling assumptions | Dictionary senses and external identifiers can aid interoperability, but do not supply executable definitions or prove facts |
| Explicit variables and binder indices in the semantic AST | Makes scope and alpha-renaming precise | Pronouns and discourse reference require additional resolution rules; names are retained for diagnostics |
| Typed semantic objects, independent of runtime layout | States admissible meanings without dictating memory representation | Intrinsic dependent types and raw syntax with proved well-formedness are both viable; choose using a nested-binding proof |
| Fixed printing and binder renaming | Gives reproducible representations while preserving expression structure | Synonyms, paraphrases and logically equivalent formulas need separate equivalence rules or proofs |
| Complete finite snapshots | Makes absent tuples false within the supplied inventory, so evaluation is determinate | Partial knowledge needs a different profile; empty domains and material implication can produce vacuous satisfaction |
| Direct evaluation | The supplied finite model can be checked without a solver dependency | Model synthesis, general satisfiability or larger instances may justify a solver with its own correctness contract |
| Strict ASCII syntax with explicit parentheses | Keeps the first grammar and proof target small | Exact spacing, final newlines and restricted names may hinder authoring; these are usability hypotheses, not requirements of unambiguity |
| Fixed JSON and JCS artifact encodings | Defines portable source, environment, meaning and model identities | JSON-LD requires context semantics; Markdown is a presentation wrapper, not the semantic payload |
| One declared semantic profile | Keeps the meaning and proof obligations inspectable | Additional domains require explicit models and composition rules |

The AST, environment and denotation jointly define meaning. A well-formed tree alone does not establish that the tree matches the source. A deterministic parser may select a wrong interpretation, so the specification requires independent uniqueness and correspondence obligations.

## Implementation language and proof tools

**Use Lean for the reference semantics, proofs, parser, printer and evaluator, with a CLI first.** Executable definitions and their proofs can share one language, avoiding an initial hand-written port and its correspondence work. Lean distinguishes kernel checking from executable compilation, so compiler and runtime behavior remain part of the trust boundary. [Lean processing pipeline](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/).

This choice is based on reducing implementation and proof boundaries. VE has no measurements establishing the fastest runtime or lowest proof-maintenance cost. Meet the task's performance envelope before adding another core; optimize algorithms first, since a language change does not remove expensive quantifier enumeration.

| Option | Where it helps | Why it is not the default v0 path |
|---|---|---|
| Rust with Aeneas/Lean | A candidate for a measured native-runtime or deployment need; safe Rust provides static memory-safety restrictions | Requires extraction, library models and correspondence to VE semantics. Memory safety alone does not prove the checker correct; unsafe dependencies and foreign calls need a trust account. [Rust reference](https://doc.rust-lang.org/reference/unsafety.html), [Aeneas](https://github.com/AeneasVerif/aeneas) |
| C with VST/Rocq and CompCert | A serious option when compiler assurance or C integration matters; VST connects source reasoning to CompCert semantics | Requires memory and undefined-behavior reasoning plus VE correspondence. CompCert's main theorem is from its C AST to assembly AST; preprocessing, elaboration, assembling/linking and runtime boundaries still matter. [VST](https://vst.cs.princeton.edu/), [CompCert](https://compcert.org/man/manual001.html) |
| Rocq with extracted OCaml | An alternative for proved functional definitions and executable extraction | Changes the proof ecosystem; extraction, target compiler and adapters still need a trust account. Compare it if proof expertise or reusable work favors it. [Rocq extraction](https://docs.rocq-prover.org/master/refman/addendum/extraction.html) |
| HOL4/CakeML | Proof-producing translation and verified compilation to machine code, including checker applications | Introduces HOL4 and another integration path without a v0 requirement for compiler assurance. Worth comparing with C for a stronger deployment guarantee. [CakeML](https://cakeml.org/) |
| Dafny or F*/Low* | Proof-oriented programming with executable-generation paths | Requires a different proof, solver and extraction account. Specialized verified toolchains have restricted scopes, not guarantees for all programs. [F*/KaRaMeL](https://github.com/FStarLang/karamel), [Dafny subset research](https://arxiv.org/abs/2512.05262) |
| Other application languages | Python, TypeScript, Go, Java, OCaml, Haskell or C++ may suit authoring and integration | No VE-specific checker correspondence or performance advantage is established for a hand-written core in these languages; choose host tooling independently |

Lean is also a natural target for a future mathematical dialect, but v0's small logic does not require dependent type theory. Rocq, Isabelle/HOL and PVS can be considered when relevant expertise or reusable formalizations favor them. A future Lean export need not dictate the metatheory implementation.

If Rust is needed, evaluate Aeneas on actual binding, parsing, relation lookup and error handling. Its current README lists specific restrictions on control flow in nested loops and generic instantiation with mutable references; unsafe and concurrent verification remain ongoing work. Pin the complete toolchain and test the required constructs. [Aeneas supported subset](https://github.com/AeneasVerif/aeneas#targeted-subset-and-current-limitations).

hax's Lean backend orchestrates Charon/Aeneas, so it is an integration option rather than independent verification evidence. Verus and Kani can answer additional functional-correctness or harness questions under their own assumptions; adopt them for a named need rather than requiring every verifier in CI. Frama-C WP is another C verification option, but combining its output with a CompCert build does not itself prove agreement between their models. [hax architecture](https://hax.cryspen.com/dev/architecture/), [Verus assumptions](https://verus-lang.github.io/verus/guide/tcb.html), [Kani harnesses](https://model-checking.github.io/kani/reference/attributes.html), [Frama-C WP](https://www.frama-c.com/wp.html).

Verified compilation is outside v0. RustCompCert's restricted research pipeline includes an unverified Rust-to-Rustlight parser; its correspondence with an Aeneas model must be established separately. Do not impose a common Rust subset until the selected tools demonstrably support the required implementation. [RustCompCert v1](https://arxiv.org/html/2602.07455v1).

## Reuse and interoperability

| Resource | Useful contribution | Boundary for VE |
|---|---|---|
| [ACE/APE](https://github.com/Attempto/APE) | Concrete controlled-English parsing and DRS/FOL outputs | Reuse is attractive for an ACE import; a new finite-model profile needs its own semantics and cannot treat APE as its correctness oracle |
| [Canonical English](https://canonical-english.org/) | Agent-oriented communication and separation of proposals from deterministic checking | Its stated ideal is not constructively defined; adopting code requires obtainable source, license and demonstrated semantic fit |
| [FRET](https://github.com/NASA-SW-VnV/fret) | Restricted-English requirements with formal and visual representations | Compare it before developing a temporal requirements profile; template-like syntax is a usability question, not a reason to dismiss reuse |
| [Grammatical Framework](https://www.grammaticalframework.org/doc/gf-refman.html) | Abstract/concrete syntax separation and multiple language surfaces | Useful when another surface is needed; syntax-tree round trips alone do not establish VE semantic equivalence |
| [OWL](https://www.w3.org/TR/owl-primer/) and [JSON-LD](https://www.w3.org/TR/json-ld11/) | Ontology and linked-data interoperability | OWL's open-world assumptions differ from finite closed-world evaluation; JSON-LD contexts need pinned interpretation rules |

Each import or export must name its supported fragment and preserve its declared semantics. Unsupported translation fails explicitly. Stable external identifiers help provenance, but do not make two vocabularies equivalent. Project age, branding and implementation language alone do not decide reuse.

## Components and trust boundaries

```text
ordinary prose / author / agent
             |
      untrusted proposals
             v
exact VE bytes + explicit environment
             |
  reference parser and type checker
             v
closed typed AST + canonical rendering
             |
   human interpretation confirmation
             v
constraints + validated finite inventory
             |
       finite evaluator
             v
result + explanatory trace + artifact identities
```

An untrusted frontend may propose text, an AST or a proof. The checking path must establish correspondence to the exact submitted inputs. LLM agreement, successful type checking and proof of a producer-selected theorem cannot establish fidelity to an unstated human intention. Manual authoring remains available; candidate generation and clarification have bounded budgets.

The interface displays canonical text from the checker artifact. Display fidelity, JSON decoding, model validation, compiler behavior and IO remain explicit trust assumptions unless separately checked. A small semantic core does not automatically verify its surrounding application.

Language acceptance, canonical form, human confirmation, inventory evaluation and proof checking have separate [status fields](spec/verification-contract.md#status-and-evidence-contract). Per-result proof certificates are optional; a checked theorem about the evaluator does not mean every displayed result was independently kernel-checked. Authentication and authorization belong to the host application; satisfying constraints does not grant permission to execute an action.

## Extension boundary and broader goals

v0 admits `ve.core@0` with `finite-constraints@0`. Vocabulary entries add signatures and descriptions, not executable definitions or inference rules. Unknown profiles and unsupported constructs are errors.

A future profile must specify its AST, typing, model, interpretation, supported combinations, parser/printer rules, resource behavior and preservation of the existing fragment. For example, “Alice believes every request must eventually be answered” needs explicit interaction between belief, obligation and time. Installing three modules does not establish that interaction. Belief must not silently entail truth, and obligations must not silently become facts.

Longer-term applications include mathematical statements and proofs, scientific assumptions and derivations, temporal requirements, and legal or agent-policy reasoning. A mathematical dialect can target a bounded Lean fragment and later provide explicit escape hatches. Scientific work must distinguish assumptions, derivations and empirical evidence. Legal and policy models must expose interpretations, exceptions, priorities and their provenance. Vague or disputed standards require declared context rather than invented precision.

These applications need their own semantics and acceptance criteria. v0 does not accept embedded Lean programs, arbitrary imports or executable plugins. Signed transport, general evidence graphs and additional backends are introduced when a concrete workflow needs them.

## Evidence needed

The [roadmap](roadmap.md) tests four questions:

- Can representative requirements be expressed without hiding necessary checks in supplied facts?
- Can users correctly confirm the meaning, compared with prose plus clarification and typed forms?
- Can the parser, printer and evaluator meet the specified proof obligations?
- Does the reference runtime meet the workload's latency, memory and deployment needs?

Start usability work with an experimental reference slice while completing formal proofs. Measure AI assistance through checked artifacts, human review effort, repair work and compute cost. External model demonstrations do not establish VE's development cost.

Tool capabilities are supported by the linked primary sources, consulted September 20, 2026. VE-specific performance, usability and proof effort remain unmeasured. Exact dependency versions and applicable licenses must be established before adoption.
