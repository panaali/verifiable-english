# Verifiable English: Research and Architecture Decision Memo

**Working names:** Verifiable English (VE), Canonical English Verified (CEV), “CE++” as an internal shorthand  
**Status:** Brainstorming synthesis / project direction  
**Date:** September 2026

**Source basis:** This memo consolidates [the brainstorming chat](<archive/sources/Chat-Formalize English In Lean.md>). External project, availability, licensing, and model-capability claims are discussion-time research notes and should be rechecked before implementation decisions. The memo was checked against the full chat on September 20, 2026.

---

## 1. Executive summary

The project idea is to build a **human-readable formal language that looks as much like ordinary English as possible, but has deterministic, machine-checkable semantics**.

The language should support:

- **human → agent communication**
- **agent → human communication**
- **agent → agent communication**
- **mathematical theorem statements and proofs**
- **scientific papers with explicit assumptions and derivations**
- **software and system requirements**
- **legal and constitutional texts**
- eventually, broader formalized everyday reasoning

The long-term ideal is:

> A sentence written in the language has one canonical machine-readable meaning; that meaning can be rendered back into readable English without semantic loss; and important transformations can be formally verified.

The strongest current direction is **not to start from scratch and not to simply extend the old ACE implementation**. The recommended path is:

1. Use **Canonical English (CE)** as the closest conceptual/front-end foundation.
2. Borrow mature semantics and examples from **Attempto Controlled English (ACE)**.
3. Borrow temporal semantics and verification methodology from **NASA FRET/FRETish**.
4. Borrow event/state modeling ideas from **PENG Light + Event Calculus**.
5. Define a **constructive typed semantic AST** as the real core of the language.
6. Define the semantics and metatheory in **Lean**.
7. Implement the production parser/checker in **Rust**.
8. Verify the critical Rust core against the Lean specification using tools such as **Aeneas**.
9. If end-to-end compiler correctness becomes important, investigate **RustCompCert** for the restricted verified core.
10. Treat LLMs as powerful but **untrusted generators**: they may propose parses, code, formalizations, and proofs, but deterministic checkers and proof kernels decide correctness.

The realistic “100% guarantee” is:

> **Every accepted Verifiable English document has the formal meaning defined by the language specification, and the verified transformations preserve that meaning.**

It is **not**:

> “The system always recovers exactly what a human intended from arbitrary unrestricted English.”

That second problem is fundamentally underdetermined whenever the speaker did not express enough information.

## Use-case catalog

| Use case | Design detail and demonstration |
|---|---|
| Human↔agent and agent↔agent communication | §§6–8; Appendix K.9; §22, Demo 1 |
| Software and system requirements | §§5.5, 13.4; §22, Demo 2 |
| Mathematical statements and proofs | §14; Appendix M; §22, Demo 3 |
| Scientific papers, authored directly or formalized retrospectively | §15; Appendix H; §22, Demo 4 |
| Constitutional text and versioned legal doctrine | §16; Appendix AD.19; §22, Demo 5 |
| AI constitutions and agent policy | §17; Appendices N and AD.20; §22, Demo 6 |

---

# 2. The problem we are trying to solve

Natural language is powerful because it is concise, flexible, contextual, and easy for humans. Those same properties make it unreliable as an interface to formal reasoning.

Ordinary English contains:

- grammatical ambiguity
- ambiguous word senses
- ambiguous references and pronouns
- unstated assumptions
- context-dependent meanings
- vague concepts
- temporal ambiguity
- modal language such as *must*, *may*, *should*, *could*
- belief and intention
- presupposition
- implicit causal structure
- pragmatic meaning
- domain-specific conventions

For example:

> Every doctor treats a patient.

A formal system must decide that this means something like:

```text
For every x:
    if x is a doctor,
    then there exists at least one y
    such that y is a patient
    and x treats y.
```

The hard part is not that logic cannot express this. The hard part is ensuring that the **surface sentence and formal representation are guaranteed to mean the same thing**.

A more difficult example is:

> Sarah had been avoiding John for three months before she finally stopped.

A rich formal language must account for:

- Sarah and John as entities
- an avoidance state/event
- past tense
- progressive aspect
- duration
- ordering of intervals/events
- termination of a state
- possibly the presuppositional or expectation-related meaning of *finally*

A general-purpose formal English therefore needs more than first-order logic alone.

---

# 3. Core design objective

The central architecture should separate **surface language** from **semantic meaning**.

```text
Human-readable Verifiable English
             │
             ▼
      deterministic parser
             │
             ▼
       typed semantic AST
             │
      ┌──────┼─────────┐
      ▼      ▼         ▼
     Lean   JSON-LD   other targets
 semantics
             │
             ▼
     machine-checked reasoning
```

The **semantic AST** is the real language.

English is one readable serialization of that AST.

This is a crucial design choice because it lets us prove properties about meaning without tying the project to one parser implementation or one programming language.

---

# 4. What “canonical” means

Here, **canonical** means that formulations identified by the language’s declared normalization rules map to a stable, standardized semantic representation. Logical equivalence or ordinary-English paraphrase alone does not require two texts to share an AST; see Appendix T.

For example:

> Every physician treats at least one patient.

and:

> Each doctor treats a patient.

may or may not be equivalent depending on the lexicon and exact senses. If they are declared equivalent, both should map to the same underlying semantic structure.

Canonicalization helps:

- agent-to-agent interoperability
- caching and hashing meanings
- semantic comparison
- deduplication
- deterministic serialization
- proof reuse
- long-term archival
- exact round trips

---

# 5. Why existing languages are not enough

## 5.1 Ordinary English

**Strengths**

- extremely expressive
- natural for humans
- supports almost every domain
- concise and pragmatic

**Weaknesses**

- ambiguous
- often underspecified
- semantic interpretation depends heavily on context
- no deterministic formal mapping

---

## 5.2 Lojban

Lojban is a constructed human language with logic-inspired grammar.

**Strengths**

- syntactically much less ambiguous
- designed to be spoken
- broad everyday expressiveness

**Weaknesses for this project**

- not English-like
- a unique grammatical parse does not automatically provide a fully specified theorem-prover semantics
- less attractive as a practical human↔agent interface for English speakers

Lojban is useful as evidence that **human-spoken language can be designed to reduce syntactic ambiguity**, but it is not the preferred foundation.

---

## 5.3 Attempto Controlled English (ACE)

ACE is one of the strongest historical precedents.

It uses restricted English while mapping accepted sentences into formal semantic representations such as Discourse Representation Structures and first-order logic.

The public APE implementation supports outputs including DRS, first-order logic, OWL/SWRL, TPTP, and RuleML.

Source: [Attempto/APE](https://github.com/Attempto/APE)

**Strengths**

- looks like English
- long research history
- deterministic interpretation rules
- established grammar
- thousands of regression examples
- good treatment of quantification, references, conditions, and logical structure
- open-source reference implementation

**Weaknesses**

- the reference ACE release is old
- the implementation is primarily Prolog
- the parser implementation itself is not end-to-end machine-verified
- language coverage is intentionally restricted
- many natural tense/aspect/pragmatic constructions are outside its scope

**Role in our project**

ACE should be a **semantic reference, compatibility target, and test source**, rather than the main implementation architecture.

---

## 5.4 PENG Light + Event Calculus

PENG Light explored controlled English as a high-level interface to Event Calculus.

The discussion also identified PENG's **bidirectional grammar**: controlled English can map through DRS into logic, and formal representations can be rendered back into English. This is a parser/printer precedent as well as an event-modeling precedent. The cited research lead is [Working for two: a bidirectional grammar for a controlled natural language](https://researchers.mq.edu.au/en/publications/working-for-two-a-bidirectional-grammar-for-a-controlled-natural-/).

Sources:

- [Working with events and states in PENG Light](https://researchers.mq.edu.au/en/publications/working-with-events-and-states-in-peng-light/)
- [Specifying events and their effects in controlled natural language](https://researchers.mq.edu.au/en/publications/specifying-events-and-their-effects-in-controlled-natural-languag)

**Strengths**

- directly relevant to events, states, timepoints, effects, and continuous change
- shows how an English-like language can express dynamic scenarios
- useful model for physics, processes, narratives, and causal systems

**Weaknesses**

- narrower and older project
- not the best modern codebase foundation
- does not by itself solve broad everyday English semantics

**Role in our project**

Borrow the **semantic ideas for events, states, and temporal change**.

---

## 5.5 NASA FRET / FRETish

FRET is a modern system for formal requirements.

A FRETish requirement has a restricted English structure with fields such as:

- scope
- condition
- component
- timing
- response
- probability

Example:

> In flight mode the battery shall always satisfy voltage > 9.

FRET maps such requirements into formal temporal semantics and supports several temporal-logic representations.

Sources:

- [NASA FRET repository](https://github.com/NASA-SW-VnV/fret)
- [Writing FRETish requirements](https://github.com/NASA-SW-VnV/fret/blob/master/fret-electron/docs/_media/user-interface/writingReqs.md)
- [FRET semantics overview](https://github.com/NASA-SW-VnV/fret/blob/master/fret-electron/docs/_media/semantics/semanticsOverview.md)

**Strengths**

- strong treatment of *always*, *eventually*, timing, conditions, and probabilistic requirements
- practical tooling
- active project
- formal semantics
- excellent precedent for formally translating English-like requirements to temporal logic

**Weaknesses**

- template-like
- aimed at system requirements, not general communication
- less natural than the broader language we want

**Role in our project**

Borrow:

- temporal operators
- timing semantics
- requirement-style deontic structure
- verification methodology

Do **not** make FRETish the whole language.

---

# 6. Canonical English: closest conceptual match

Canonical English currently describes itself as:

> a formal, computable, unambiguous subset of English intended for machine-to-human and machine-to-machine communication.

It also describes itself as:

> a domain-schema-independent API for agentic communication.

Source: [Canonical English](https://canonical-english.org/)

This is unusually close to our original motivation.

As of September 2026, the site reports version 1.0.0 with a small but concrete initial rule/lexicon/test base. Its methodology distinguishes an ideal form of Canonical English from the current computable approximation.

Sources:

- [Canonical English overview](https://canonical-english.org/)
- [Canonical English methodology](https://canonical-english.org/methodology.html)

Important ideas include:

- machine-to-machine communication
- machine-to-human communication
- humans writing with machine assistance
- explicit word senses
- stable entity identifiers
- semantic-web compatibility
- a deterministic acceptance layer
- an LLM-assisted semantic parser called `noah-parser`

## Why CE is attractive

It already targets the **exact communication setting** we care about:

```text
human ↔ agent
agent ↔ agent
```

It is much more forward-looking than ACE in this respect.

## Why CE should not simply be trusted as-is

Its current methodology is still early.

The ideal CE set is not yet constructively defined as a complete formal grammar plus semantics.

That is the part our project can strengthen.

---

# 7. NOAH architecture and what we should keep

The Canonical English design separates a best-effort parser from deterministic acceptance.

Conceptually:

```text
ordinary English
       │
       ▼
  noah-parser
   best effort
       │
       ▼
candidate Canonical English
       │
       ▼
deterministic checker/linter
       │
       ▼
accepted canonical representation
```

This is an excellent idea.

The LLM or semantic parser does **not need to be trusted**.

A model can generate twenty candidates. The deterministic language machinery determines which candidates are valid.

Our extension should make that structure even stronger:

```text
ordinary English
       │
       ▼
LLM / noah-like parser
       │
       ▼
candidate VE sentence / AST
       │
       ▼
verified deterministic checker
       │
       ▼
canonical semantic AST
       │
       ├────────► readable canonical English
       │
       ├────────► JSON-LD / APIs
       │
       └────────► Lean semantics / proofs
```

---

# 8. Recommended architecture

The recommended system has **three trust levels**.

## Level 1 — untrusted proposal layer

Components:

- LLMs
- heuristic parsers
- speech recognition
- ordinary-English converters
- autocomplete
- agent-generated messages

These components may be wrong.

Their job is only to propose candidate structures.

---

## Level 2 — deterministic language layer

Implemented in high-performance Rust.

Responsibilities:

- tokenize
- parse canonical syntax
- resolve explicitly allowed references
- type-check the semantic AST
- validate lexical senses
- canonicalize representations
- serialize/deserialize
- reject ambiguity
- enforce language invariants

This is the production runtime.

---

## Level 3 — formally verified semantic layer

Specified in Lean.

Responsibilities:

- define semantic AST
- define denotational/formal semantics
- prove uniqueness of meaning
- prove round-trip properties
- prove canonicalization correctness
- prove translations to supported target logics
- prove conservative compatibility with supported ACE constructs
- prove temporal/event/deontic transformations
- optionally prove the Rust checker implements the Lean specification

---

# 9. Why Lean belongs in the architecture

Lean is not required because users should write Lean.

Users should almost never see Lean.

Lean is useful because it gives us a **small trusted proof kernel** that can verify general theorems about the language.

Example properties:

```text
parse(print(ast)) = ast
```

Meaning:

> Printing a valid semantic AST and parsing it again recovers the same semantic object.

Another desired property:

```text
if checker accepts x,
then x has exactly one valid semantic interpretation
```

Another:

```text
translation_to_temporal_logic(x)
preserves the semantics of x
```

And for ACE compatibility:

```text
for every supported ACE sentence s:
    semantics_VE(embed(s)) = semantics_ACE(s)
```

The ACE compatibility theorem requires a **versioned formal model of the supported ACE semantics**, including its background assumptions. Agreement with APE regression examples provides empirical compatibility evidence; it does not establish the theorem for every sentence in that fragment.

The important difference from testing is that a proof applies to **all values covered by the theorem**, not only thousands of examples.

Regression tests are still useful; they are not the final correctness argument.

---

# 10. Production implementation: Rust

The production implementation should be Rust.

Reasons:

- high performance
- memory safety
- strong type system
- excellent systems ecosystem
- natural fit for parsers and language servers
- easier verification burden than C for memory-related properties
- compatible with emerging Rust→proof-assistant workflows

The performance-critical runtime can therefore remain:

```text
text
 ↓
native Rust parser/checker
 ↓
semantic AST
 ↓
result
```

Formal verification is primarily an **offline development activity**, so it need not impose significant runtime overhead.

---

# 11. Verifying the Rust implementation

A Lean specification alone does not prove that arbitrary Rust code implements it correctly.

We discussed three possibilities.

## Option A — independent Lean specification + normal Rust implementation

**Pros**

- easiest
- clear semantics
- strong theorem-level reasoning

**Cons**

- the Rust implementation could still contain a bug relative to the Lean specification

**Use**

Good initial stage.

---

## Option B — verify the actual Rust implementation against the Lean model

This is the recommended direction for the critical core.

**Aeneas** translates a supported subset of safe sequential Rust into functional models for theorem provers including Lean.

Sources:

- [Aeneas](https://aeneasverif.github.io/)
- [Aeneas user documentation](https://aeneasverif.github.io/aeneas/)
- [Aeneas project overview](https://aeneasverif.github.io/projects/)

Aeneas currently focuses on safe, sequential Rust and has limitations around some features such as concurrency and certain complex borrowing/control-flow patterns.

That is acceptable if the verified checker core is deliberately kept small and pure.

Architecture:

```text
actual Rust checker core
        │
        ▼
      Aeneas
        │
        ▼
 functional Lean model
        │
        ▼
 correctness theorems
```

**Pros**

- proofs apply to the logic of the code we actually execute
- native Rust performance remains
- strong fit for a pure deterministic semantic checker

**Cons**

- requires staying within the supported Rust subset
- verification engineering can be substantial
- some surrounding runtime components remain outside the proof

**Recommendation**

Use this for the **trusted semantic/checking core**, not the whole application.

---

## Option C — verified compilation to machine code

Even if source-level Rust is verified, ordinary `rustc`/LLVM compilation is part of the trusted computing base.

A stronger goal is proving that the compiled machine code preserves the verified source semantics.

### RustCompCert

RustCompCert is a 2026 research project developing an end-to-end verified compiler for a sequential Rust subset on top of CompCert.

Source:

- [RustCompCert: A Verified and Verifying Compiler for a Sequential Subset of Rust](https://arxiv.org/abs/2602.07455)

It aims to provide:

- source-to-assembly semantics preservation
- verified borrow checking / memory-safety guarantees
- a restricted Rust subset suitable for verification

**Pros**

- potentially much stronger end-to-end guarantee
- reduces compiler trust
- very attractive for the tiny critical checker

**Cons**

- restricted Rust subset
- research-stage tooling
- not yet a replacement for the full Rust ecosystem
- unsuitable as the compiler for the whole product today

**Recommended use**

Keep the verified core simple enough that we may later compile it through RustCompCert or a similar verified pipeline. The discussion reported an unverified Rust source parser before Rustlight; a source-to-assembly guarantee must account for that boundary explicitly (Appendix AD.15).

The UI, networking, indexing, LLM integration, parallel processing, and other noncritical services can continue using ordinary Rust.

---

# 12. What “100% accuracy” can mean

This distinction is central.

## Achievable guarantee

We can aim for:

> If a VE document is accepted, its formal interpretation is exactly the one defined by the VE specification.

We can also aim for:

> Every verified transformation preserves that formal meaning.

Potentially:

> The machine code implementing the core preserves the verified source semantics.

These are precise claims.

## Not generally achievable

We cannot guarantee:

> Given arbitrary ordinary English, the system always recovers exactly what the speaker intended.

Example:

> Nice job.

This could be sincere or sarcastic.

No parser can recover information that the utterance and context did not uniquely determine.

The safe workflow is therefore:

```text
ambiguous ordinary English
        │
        ▼
candidate interpretations
        │
        ▼
clarification / selection
        │
        ▼
canonical VE meaning
```

Once the ambiguity boundary has been crossed, the remainder can be lossless and verified.

A well-formed but unintended AST can still pass the checker. Acceptance establishes conformance to VE semantics; matching the author's intent still depends on context, back-translation, and clarification or selection.

---

# 13. Semantic layers the language will eventually need

Trying to put every kind of meaning directly into basic first-order logic will become awkward.

The language should probably have several formally defined semantic domains.

## 13.1 Core logic

For:

- entities
- predicates
- relations
- quantifiers
- equality
- negation
- implication
- conjunction/disjunction

ACE is a major reference here.

---

## 13.2 Types and mathematics

For:

- numbers
- functions
- sets
- algebraic structures
- dependent propositions
- mathematical definitions and proofs

Lean should be the primary target/foundation.

---

## 13.3 Events and time

For:

- events
- states
- start/end
- before/after
- duration
- continuous change
- temporal relationships

PENG/Event Calculus is an important precedent.

---

## 13.4 Temporal logic

For:

- always
- eventually
- until
- whenever
- deadlines
- bounded timing

FRETish is an important precedent.

---

## 13.5 Epistemic and intentional language

For:

- knows
- believes
- suspects
- intends
- expects
- observes

These cannot simply collapse into ordinary truth assertions.

Example:

> Alice believes that Bob is in Paris.

must not imply:

> Bob is in Paris.

---

## 13.6 Deontic and normative language

For:

- must
- shall
- may
- prohibited
- permitted
- obligation
- exception
- priority

This is essential for:

- constitutions
- regulations
- contracts
- AI constitutions
- organizational policy

---

## 13.7 Defeasible rules and exceptions

Law and real-world policy often work like:

> Normally X, unless Y.

rather than:

> X is universally true.

The language must distinguish hard logical implication from defeasible rules.

---

## 13.8 Probability and uncertainty

For:

- probability
- confidence
- statistical uncertainty
- measurement uncertainty
- uncertain hypotheses

Example:

> The model assigns a 0.7 probability to rain tomorrow.

This is much more precise than:

> It will probably rain.

---

## 13.9 Context-dependent predicates

Words such as:

- tall
- expensive
- safe
- reasonable
- significant

should not necessarily be banned.

They can instead be represented as explicitly context-dependent predicates whose interpretation depends on a declared context, comparison class, threshold rule, or external standard.

---

# 14. Mathematics as a flagship use case

The language should eventually support a mathematical dialect that compiles to Lean.

Instead of writing low-level Lean syntax, a mathematician should be able to write controlled mathematical prose.

Conceptually:

```text
mathematical Verifiable English
           │
           ▼
      semantic AST
           │
           ▼
          Lean
           │
           ▼
      Lean kernel
           │
           ▼
  machine-checked theorem
```

This does **not** mean replacing Lean.

Lean remains:

- proof kernel
- formal foundation
- target representation
- final correctness authority

VE becomes the human-facing language.

The ideal goal is:

> Every theorem and proof that a mathematician reasonably wants to communicate should be expressible in the natural mathematical dialect of VE.

For exotic theorem-prover implementation details, the language can provide a lower-level escape hatch rather than forcing every Lean metaprogramming construct to sound like ordinary English.

---

# 15. Scientific papers as a flagship use case

Physics and other sciences are especially interesting because they contain more than mathematical proof.

A formalized scientific paper should distinguish:

```text
definitions
    ↓
physical assumptions
    ↓
model
    ↓
approximations
    ↓
validity regime
    ↓
mathematical derivations
    ↓
observations/data
    ↓
statistical inference
    ↓
scientific conclusions
```

The system could identify problems such as:

- undefined terms
- ambiguous symbols
- a conclusion using an unstated assumption
- an approximation used outside its declared range
- a theorem invoked without satisfying its preconditions
- inconsistent units
- conflicting definitions
- empirical conclusions stronger than the statistical evidence supports

## Two workflows

### Workflow A — authors write papers directly in VE

Benefits:

- ambiguity detected while writing
- dependencies between claims explicit
- assumptions tracked automatically
- mathematical derivations checked
- reproducibility metadata attached to claims
- canonical semantic artifact published with the paper

The rendered paper could still look like a normal scientific PDF.

### Workflow B — formalize existing papers retrospectively

This is an excellent research benchmark.

A seminal paper is translated into VE.

Whenever the translation cannot proceed uniquely, the system records why.

Example:

> “We may therefore neglect the second-order term.”

The formalizer may need to ask:

- negligible relative to what?
- under what bound?
- for what parameter range?
- what error tolerance is assumed?

The output becomes an **assumption and ambiguity audit**.

A useful report could look like:

```text
✓ 214 claims formalized uniquely
✓ 73 derivations verified
? 12 unstated assumptions required
? 7 statements have multiple plausible interpretations
? 3 conclusions use stronger assumptions than stated
? 2 empirical claims lack sufficient reproduction information
```

This could be more scientifically valuable than a simple “verified/not verified” label.

---

# 16. Law and constitutions

The U.S. Constitution is a strong test because legal meaning is not simply the literal text.

A realistic representation needs layers:

```text
constitutional text
        │
        ▼
literal semantic representation
        │
        ▼
interpretive doctrine
        │
        ▼
cases / tests / exceptions
        │
        ▼
application to facts
```

A phrase such as “unreasonable searches and seizures” can remain an **open standard** in the text layer. A doctrinal interpretation adds rules and assumptions with their own provenance; it must not silently replace that standard with one invented precise definition.

## Versioning

The constitutional text may remain unchanged while controlling precedent changes.

Therefore:

```text
doctrine_1950
doctrine_1970
doctrine_2000
doctrine_2026
```

can all represent different states of the legal interpretation graph.

This lets the system answer questions such as:

> What was the controlling interpretation of this provision at a particular date?

It should also support a dependency query: **if a precedent is narrowed or overruled, which derived rules and applications lose that support or need reassessment?** Preserve the prior doctrine snapshot and identify any alternative support; a changed dependency should not automatically erase every derived conclusion.

The system should preserve provenance:

- constitutional clause
- case
- court
- date
- holding
- scope
- later modification
- overruling/narrowing/distinguishing relationships
- interpretive method and rationale, such as text, original meaning, precedent, historical practice, structure, or pragmatic reasoning

These method annotations make competing interpretations inspectable without treating one method as the constitutional text itself.

The goal is **not** to pretend legal interpretation is mechanically objective.

The goal is to make explicit:

- what follows from text
- what comes from precedent
- where interpretive choices enter
- where genuine disagreement remains

---

# 17. AI constitutions and agent policy

AI constitutions are another natural use case because agent rules often combine:

- hard prohibitions
- priorities
- defeasible rules
- values
- contextual judgments
- uncertainty

A VE representation could distinguish:

```text
HARD RULE
Never perform X.

PRIORITY
Safety outranks helpfulness in condition C.

DEFEASIBLE RULE
Normally perform Y unless exception Z applies.

VALUE
Preserve user autonomy.

CONTEXTUAL STANDARD
Action A undermines autonomy when conditions C1...Cn hold.
```

This is much more precise than encoding everything as flat Boolean rules. The normative layer uses the deontic and defeasible modules in §§13.6–13.7; mathematics and processes use their own semantic modules, with Lean formalizing the metatheory (Appendix S).

A formal agent constitution could support:

- static consistency checks
- conflict detection
- priority analysis
- provenance
- policy versioning
- explanation of why an action is permitted or forbidden
- agent-to-agent exchange of policy constraints

---

# 18. Why this is especially timely now

Historically, projects such as ACE faced two expensive problems:

1. implementing sophisticated natural-language/formal-language tooling
2. writing and maintaining large volumes of proof and verification code

Modern frontier coding/reasoning models substantially reduce both costs.

They can help:

- port grammars
- generate candidate semantics
- create Lean definitions
- write proof attempts
- repair failing proofs
- port test suites
- build parsers
- generate fuzz/property tests
- formalize papers
- compare candidate interpretations

But the model should remain **outside the trusted computing base**.

The trusted chain should end in deterministic checks such as:

- type checking
- parser validation
- Lean kernel verification
- verified Rust core
- optional verified compilation

The model can make mistakes without undermining the guarantee.

---

# 19. Candidate project paths

## Path 1 — extend APE directly

### Approach

Fork Attempto/APE and extend its Prolog grammar/DRS machinery.

### Pros

- mature baseline
- large test suite
- existing formal representations
- known ACE semantics
- less initial grammar work

### Cons

- old architecture
- difficult to obtain end-to-end formal verification
- Prolog implementation becomes a legacy constraint
- not designed for modern agent communication
- expanding to very broad semantics may become increasingly awkward

### Assessment

Useful as reference and compatibility suite, **not preferred as the main codebase**.

---

## Path 2 — build directly on PENG Light

### Pros

- strong event/state concepts
- useful temporal modeling

### Cons

- older and narrower
- not aimed at broad human↔agent communication
- weaker modern ecosystem

### Assessment

Borrow semantics, not codebase.

---

## Path 3 — build directly on FRET/FRETish

### Pros

- active
- strong temporal logic
- serious verification methodology
- production-minded formal tooling
- existing contribution process

### Cons

- heavily requirements-oriented
- sentence structure is template-like
- poor fit as a full general-purpose formal English

### Assessment

Excellent subsystem/reference, not the top-level language.

---

## Path 4 — build a completely new Lean-first language

### Pros

- formally clean from day one
- total control
- easiest place to prove metatheory
- no legacy constraints

### Cons

- rebuild grammar, lexicon, parsing, entity grounding, serialization, tooling, and community
- high risk of producing another isolated CNL
- wastes good ideas already present in CE/ACE

### Assessment

Good fallback if existing projects are incompatible with the vision.

---

## Path 5 — fork or collaborate with Canonical English

### Pros

- philosophically closest to our goal
- explicitly machine-to-machine and machine-to-human
- modern agent-oriented framing
- natural-looking English
- explicit lexical/entity grounding
- LLM-assisted workflow already part of its design

### Cons

- currently immature
- ideal language not yet fully constructive
- public implementation availability has been inconsistent
- no end-to-end formally verified semantic core yet

### Assessment

**Preferred starting point if collaboration/source access is practical.**

---

## Path 6 — hybrid successor

This is the recommended technical architecture.

Use:

- **Canonical English** for broad language/front-end philosophy
- **ACE** for mature logical semantics and regression corpus
- **PENG/Event Calculus** for events and states
- **FRETish** for temporal operators and temporal verification methodology
- **Lean** for formal semantics and metatheory
- **Rust** for the production checker
- **Aeneas** for proving the critical Rust core against Lean
- **RustCompCert** as a possible future route to verified machine code

### Assessment

**Recommended overall path.**

**Decision history:** The early technical proposal was to implement a useful ACE fragment in Lean, prove its English↔AST round trip and semantics, then add native temporal sentences. The later discussion explicitly revised the collaboration preference toward CE because its broad English surface, lexical/entity grounding, and agent-communication workflow better matched the long-term goal. The roadmap therefore checks CE source access and architectural fit first while retaining the ACE-informed core and compatibility milestone. If CE cannot be reused, a CE-compatible successor remains the fallback; this does not revive APE as the primary codebase.

---

# 20. Recommended roadmap

## Phase 0 — project charter

Write a short formal project charter defining the promises of the language.

The initial promise should be:

> Every accepted VE sentence has exactly the formal semantics assigned by the VE specification.

Avoid promising:

> VE fully captures all human meaning.

Define:

- trusted computing base
- semantic scope
- treatment of ambiguity
- treatment of unknown words
- compatibility policy
- versioning policy

---

## Phase 1 — obtain / evaluate Canonical English implementation

Actions:

1. Contact the Canonical English maintainer.
2. Obtain the current source or confirm the contribution model.
3. Inspect:
   - grammar representation
   - NOAH parser
   - linter/checker
   - semantic data model
   - JSON-LD representation
   - lexicon
   - test suite
4. Determine whether a verified semantic layer can be added cleanly.

Decision gate:

> If CE architecture is compatible, collaborate/fork.  
> If not, create a compatible successor.

---

## Phase 2 — define the semantic AST

Design a small, typed core.

Initial constructs should cover:

- entities
- predicates
- unary/binary relations
- quantifiers
- equality
- conjunction
- disjunction
- negation
- implication
- definitions
- simple reference
- explicit lexical senses

Keep this core small enough to understand completely.

---

## Phase 3 — formalize the semantic core in Lean

Implement:

- AST types
- well-formedness
- interpretation
- canonicalization
- parser/printer model

Prove initial invariants:

1. well-formed ASTs have defined semantics
2. canonical serialization is deterministic
3. `parse(print(ast)) = ast`
4. canonicalization is idempotent
5. equivalent supported ACE constructs preserve their semantics

---

## Phase 4 — ACE compatibility benchmark

Take the useful ACE subset and regression corpus.

Goal:

> A large set of ACE sentences should either map to equivalent VE semantics or fail for a clearly documented reason.

Deliverable:

```text
ACE sentence
    ↓
APE DRS/FOL
    │
compare
    │
VE AST → Lean semantics
```

This gives us a mature baseline without adopting APE as the core architecture.

---

## Phase 5 — build the production Rust checker

Implement:

- lexer
- canonical parser
- AST validator
- lexicon lookup
- canonical serializer
- deterministic ambiguity rejection

Design the verified core to stay:

- safe Rust
- deterministic
- mostly functional
- sequential
- simple ownership patterns

This makes Aeneas verification easier.

Before fixing the core's coding standard, build a representative parser/checker prototype against pinned Aeneas and RustCompCert versions. Record which AST representations, collections, ownership patterns, and control-flow constructs each accepts, and where source parsing lies outside either proof. The proposed common subset in Appendix E is a feasibility hypothesis until this experiment succeeds; do not assume generic `Vec`, `Option`, `Result`, or `Box` APIs work unchanged in both toolchains.

---

## Phase 6 — prove the Rust core

Use:

```text
Rust core
   ↓
Aeneas
   ↓
Lean functional model
   ↓
proofs against VE specification
```

Primary target theorem:

> Whenever the production checker accepts an input and returns AST `a`, `a` satisfies the formal VE language specification.

---

## Phase 7 — add native time and event semantics

Use PENG/Event Calculus and FRETish as references.

Add:

- event
- state
- interval
- timepoint
- before/after
- duration
- starts/ends
- always
- eventually
- until
- whenever
- bounded deadlines

Example target:

> Every request that is received is eventually answered.

This should become native language rather than an awkward encoding using manually introduced timestamps.

---

## Phase 8 — mathematical dialect

Build a controlled mathematical layer targeting Lean.

Initial benchmark set:

- undergraduate theorems
- textbook proofs
- existing Lean examples
- short research-level formalizations

Goals:

- natural theorem statements
- definitions
- assumptions
- structured proofs
- automatic Lean export
- proof certificate verification

---

## Phase 9 — scientific-paper benchmark

Choose one important but manageable physics paper.

Create:

1. original-text segmentation
2. VE formalization
3. assumptions graph
4. definitions graph
5. derivation graph
6. unresolved ambiguity report
7. formal proof coverage report

Do **not** silently fill missing assumptions.

Missing assumptions should be first-class outputs.

---

## Phase 10 — normative/legal dialect

Add:

- obligations
- permissions
- prohibitions
- defeasible rules
- exceptions
- priorities
- provenance
- versioned doctrine

Potential benchmark:

- a bounded portion of U.S. constitutional doctrine
- an AI constitution / policy document

---

## Phase 11 — verified compilation experiment

Once the trusted Rust core is stable:

1. identify the subset compatible with RustCompCert or a similar verified compiler
2. compile a minimal checker through the verified toolchain
3. establish the smallest practical end-to-end trusted computing base

This is **not necessary for the first useful version**.

---

# 21. First concrete prototype

The first prototype should deliberately be small.

## Language examples

```text
Every doctor treats a patient.
No doctor treats every patient.
Every patient who has a doctor trusts that doctor.
If a doctor treats a patient, then the patient knows the doctor.
```

## Deliverables

### A. semantic AST

Example:

```text
Forall(
  variable = x,
  restriction = Doctor(x),
  body =
    Exists(
      variable = y,
      restriction = Patient(y),
      body = Treats(x, y)
    )
)
```

### B. canonical printer

AST → canonical English

### C. parser

canonical English → AST

### D. Lean semantics

AST → proposition / denotation

### E. proofs

- round trip
- uniqueness
- deterministic canonicalization

### F. Rust implementation

High-performance implementation of the same checker.

### G. Rust verification

Aeneas-generated Lean model + equivalence proofs.

If this tiny prototype works cleanly, the overall architecture is validated.

---

# 22. Suggested flagship demonstrations

A mature project should eventually demonstrate several domains because each stresses a different semantic capability.

## Demo 1 — ordinary factual language

Tests:

- quantification
- references
- ambiguity
- entity identity

## Demo 2 — temporal requirements

Example:

> Whenever a request is received, it is eventually answered.

Tests:

- time
- event semantics
- temporal logic

## Demo 3 — mathematics

Formalize a theorem in natural mathematical VE and compile it to Lean.

Tests:

- proof expressiveness
- dependent/formal mathematics
- kernel verification

## Demo 4 — physics paper

Formalize an influential paper.

Tests:

- assumptions
- units
- approximations
- derivations
- empirical vs mathematical claims

## Demo 5 — legal doctrine

Formalize a bounded constitutional doctrine and associated precedents.

Tests:

- deontic rules
- defeasibility
- provenance
- versioning
- competing interpretations

## Demo 6 — agent constitution

Formalize a policy/constitution for an AI agent.

Tests:

- priorities
- exceptions
- policy conflicts
- human↔agent and agent↔agent communication

---

# 23. Open research questions

The main hard problems are no longer simply “can we build a parser?”

They are semantic.

## 23.1 How much ordinary English should be admitted?

Should VE:

- restrict the writer aggressively, like ACE?
- accept broad English but request clarification?
- support both a strict canonical form and a looser authoring layer?

Likely answer:

> broad assisted authoring → strict canonical representation.

---

## 23.2 How should vagueness be represented?

Should:

> John is tall.

be rejected unless a threshold is defined?

Or represented as:

```text
Tall(
    John,
    comparison_class = adult_men,
    context = C
)
```

with context deliberately explicit?

---

## 23.3 How should pragmatics be handled?

Example:

> It is cold in here.

Literal proposition:

> room temperature is low.

Possible communicative act:

> please close the window.

These should probably be separate layers:

```text
literal semantics
communicative intent
contextual inference
```

The verified core should not silently conflate them.

---

## 23.4 How should ambiguity be surfaced?

The system should favor:

```text
I found 3 valid interpretations.
Choose one.
```

over:

```text
I guessed interpretation 2.
```

Especially for scientific, legal, and agent-policy uses.

---

## 23.5 What is the relationship between VE and Lean?

VE should not be merely English syntax pasted over Lean tokens.

The semantic core should be rich enough for general communication.

Lean should serve as:

- metatheory
- proof target
- verification kernel
- mathematical backend

not necessarily the universal surface-level ontology for every domain.

---

# 24. Naming

“C++” should not be the public name because it is inseparable from the C++ programming language.

“CE++” is acceptable as an internal shorthand but likely poor branding.

Candidate names:

### Verifiable English

**Pros**

- communicates the central promise
- broad enough for science, math, agents, and law
- independent of Canonical English branding

**Cons**

- generic

### Canonical English Verified

**Pros**

- ideal if formally extending Canonical English
- communicates compatibility and verification

**Cons**

- depends on collaboration/branding relationship with CE

### Formal English

**Pros**

- immediately understandable

**Cons**

- extremely generic
- many prior uses

### Exact English

**Pros**

- memorable
- emphasizes precision

**Cons**

- “exact” may overpromise regarding human intent

### Semantic English

**Pros**

- emphasizes meaning

**Cons**

- does not immediately communicate verification

**Current preference**

- **Canonical English Verified (CEV)** if developed with/forked from CE
- **Verifiable English (VE)** if independent

---

# 25. Recommended decision today

If starting now:

## Primary path

**Attempt collaboration with Canonical English first.**

Propose adding:

1. a constructive typed semantic AST
2. formal semantics in Lean
3. a deterministic parser/printer contract
4. machine-proved round-trip properties
5. a verified Rust semantic checker
6. compatibility tests against ACE
7. temporal/event extensions informed by FRETish and PENG

## If collaboration is not practical

Build an independent **CE-compatible successor** with the same broad human↔agent / agent↔agent vision.

Do not base the architecture directly on APE.

Use APE as:

- a semantic reference
- a corpus
- a compatibility oracle
- a source of hard language examples

---

# 26. Minimal trusted-computing-base goal

Long-term, the critical path could look like:

```text
untrusted LLM / authoring tools
          │
          ▼
  verified canonical parser/checker
          │
          ▼
       semantic AST
          │
          ▼
    Lean-verified semantics
          │
          ▼
  verified transformations
```

Optional stronger endpoint:

```text
verified Rust checker
        │
        ▼
verified Rust compiler
        │
        ▼
machine code
```

The goal is not to formally verify every UI component.

The goal is to make it impossible for an untrusted front end to cause an **invalid semantic object to be accepted by the trusted core**.

---

# 27. Final project thesis

The project can be summarized in one statement:

> **Build a human-readable formal language in which accepted text has deterministic machine-checkable meaning, can be losslessly exchanged among humans and agents, and can compile into specialized formal systems such as Lean and temporal logic while retaining verified semantic guarantees.**

The key insight is that modern LLMs make authoring and implementation much easier, but they should not be the authority.

The architecture should combine:

> **LLMs for generation, deterministic parsers for acceptance, typed semantic structures for meaning, Rust for speed, and Lean for proof.**

That combination is what makes a modern successor to ACE materially more ambitious—and potentially much more useful—than earlier controlled natural languages.


---

# Appendix A — Related Languages, Formalisms, and Verification Systems

This appendix captures systems that are important to the project even when they are not the preferred implementation foundation.

## A.1 OWL — Web Ontology Language

OWL is a W3C language for formal knowledge representation: classes, individuals, properties, subtype relationships, disjointness, and other ontology constraints.

Example concept:

```text
Every professor is a person.
```

can correspond to an ontology inclusion such as:

```text
Professor ⊆ Person
```

### Why it matters

ACE has historically supported mappings into OWL. ACE/OWL work also demonstrated an important property for this project: within a supported fragment, a formal ontology can be verbalized into controlled English and converted back without loss of logical meaning.

### Limitation

OWL is primarily an ontology language. It is not intended to express arbitrary mathematical proofs, rich tense/aspect, event dynamics, general programs, or unrestricted discourse.

### Role for VE

- ontology interoperability
- entity/type constraints
- reversible formal-English precedent
- possible target representation for ontology-heavy domains

Reference: https://www.w3.org/OWL/

---

## A.2 Common Logic Controlled English (CLCE)

CLCE is an English-like notation associated with Common Logic.

It explored formal representations of things such as:

- situations
- times
- places
- causes
- contexts

### Why it matters

CLCE is evidence that controlled English can move beyond simple static first-order statements while staying formally interpretable.

It is particularly relevant to:

- scientific narratives
- temporal contexts
- event descriptions
- legal and causal statements

### Limitation

It still does not amount to unrestricted formalized English, and richer tense/aspect remains difficult.

### Role for VE

Historical and semantic reference.

Reference: https://www.jfsowa.com/clce/clce07.htm

---

## A.3 ForTheL / Naproche

ForTheL is a controlled language for mathematical writing. Naproche checks mathematical texts written in controlled natural language.

The intended style resembles normal mathematical prose:

```text
Let G be a group.
Assume that G is finite.
Then ...
```

rather than low-level theorem-prover syntax.

### Why it matters

This is one of the strongest precedents for the **mathematical dialect** of VE.

It demonstrates that natural-looking mathematical prose can serve as the user-facing layer of formal reasoning.

### Strengths

- familiar mathematical style
- explicit assumptions and definitions
- formal checking
- suitable for longer mathematical texts

### Limitation

It is mathematics-focused rather than a general-purpose human↔agent language.

### Role for VE

Major reference for:

- mathematical surface syntax
- proof-oriented prose
- paper formalization
- author experience

---

## A.4 Verbose Lean

Verbose Lean provides a controlled-natural-language style on top of Lean.

Conceptually:

```text
controlled mathematical prose
          ↓
        Lean
```

### Why it matters

It supports our conclusion that VE should **not replace Lean's kernel**.

Instead, VE can become a human-facing language that compiles to Lean while Lean remains the final proof checker.

### Limitation

Its scope is mathematical theorem proving rather than broad natural-language semantics.

### Role for VE

Reference for the mathematical frontend and proof-language design.

Reference: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2024.27

---

## A.5 Visored

Visored is a recent natural-language-oriented theorem-proving effort connected to Lean-style formal verification.

Its broader significance is that modern theorem proving is increasingly combining:

- controlled mathematical language
- automated proof generation
- LLM assistance
- formal kernel checking

### Why it matters

It is evidence that the gap between mathematical prose and formal proof-assistant input is shrinking.

### Role for VE

Reference for:

- LLM-assisted formalization
- proof generation
- natural mathematical authoring
- Lean export/checking

---

## A.6 TLA+

TLA+ is a formal specification language for systems that evolve over time, particularly concurrent and distributed systems.

It is strong at:

- state machines
- safety properties
- liveness properties
- concurrency
- temporal behavior

Example:

```text
Whenever a request is received,
it is eventually answered.
```

is naturally a temporal property.

### Why it matters

This kind of statement is awkward in basic ACE unless time is modeled manually.

TLA+ demonstrates why VE needs native temporal concepts such as:

- always
- eventually
- until
- next
- invariant
- liveness

### Difference from VE

TLA+ is not intended to look like ordinary English.

### Role for VE

Possible semantic target/reference for system behavior and temporal assertions. The discussion distinguished **TLC**, which explores reachable states of finite models for counterexamples, from **TLAPS**, which supports theorem proofs.

Reference: https://lamport.azurewebsites.net/tla/tla.html

---

## A.7 Coq

Coq is an interactive theorem prover based on dependent type theory.

It is widely used for:

- formal mathematics
- verified software
- certified compilers
- proof-carrying developments

### Why it matters

Coq is one of the systems that showed that large software artifacts can be proved correct, not merely tested.

Most importantly for this project, **CompCert** is implemented and proved in Coq.

### Role for VE

Not the preferred proof environment for VE, but an important precedent and source of verified-software technology.

Reference: https://coq.inria.fr/

---

## A.8 Isabelle

Isabelle is an interactive theorem prover with a different architecture from Lean/Coq.

It is widely used for large formal-verification efforts and supports multiple object logics.

### Why it matters

It is another mature example of machine-checked metatheory and software/system verification.

### Role for VE

Reference point for theorem-prover design and large formal developments.

Reference: https://isabelle.in.tum.de/

---

## A.9 PVS

PVS is a theorem-proving and specification system developed at SRI.

It combines a specification language with automated theorem-proving support.

### Why it matters

FRET/FRETish research used PVS to machine-prove important properties of its temporal semantics and translations.

That is directly relevant to our goal:

> prove that an English-like source language and its formal target have equivalent semantics.

### Role for VE

Methodological precedent. We would likely use Lean instead, but FRET's use of PVS is evidence that the verification strategy is practical.

Reference: https://pvs.csl.sri.com/

---

## A.10 Grammatical Framework (GF) / ACE-in-GF

Grammatical Framework is a language for building multilingual grammars with a separation between:

- abstract syntax
- concrete language realizations

ACE-in-GF explored representing ACE using this architecture.

Conceptually:

```text
            abstract semantic/syntactic tree
               /        |        \
          English     German     French ...
```

### Why it matters

GF supports an idea central to VE:

> the underlying structure should be separate from any particular surface language.

That also creates a possible future path to:

- multilingual Verifiable English-like surfaces
- lossless controlled translation
- different readable renderings of one semantic AST

### Limitation

GF by itself does not supply all the formal semantics and proof guarantees we want. In the discussion's assessment, ACE-in-GF tested tree round trips but did **not** implement the ACE→DRS semantic mapping. A syntax-tree round trip therefore cannot by itself establish preservation of ACE meaning.

### Role for VE

Strong architectural reference for bidirectional and multilingual surface syntax.

Reference: https://github.com/Attempto/ACE-in-GF

---

# Appendix B — Implementation and Verification Alternatives

## B.1 Rust + Aeneas + Lean

This remains the preferred implementation path for VE.

```text
production Rust core
        ↓
      Aeneas
        ↓
 functional Lean model
        ↓
 semantic correctness proofs
```

### Advantages

- native Rust speed
- memory safety from Rust's type system
- good engineering ecosystem
- proofs can target the logic of the actual implementation
- well suited to a small deterministic parser/checker core

### Limitation

Aeneas supports a restricted subset most comfortably, especially safe sequential Rust.

### Best use

Keep the trusted core deliberately simple and verification-friendly.

Reference: https://aeneasverif.github.io/

---

## B.2 hax

`hax` is another toolchain for extracting Rust into formal models and theorem-prover backends.

It can work with Lean-related verification flows and, in current versions, can use Aeneas for some Lean translation work.

### Why it matters

It may provide a more convenient frontend/workflow for turning Rust libraries into formal verification obligations.

### Role for VE

Evaluate alongside direct Aeneas use.

Reference: https://hax.cryspen.com/

---

## B.3 Kani

Kani is a Rust model checker.

It is particularly useful for:

- panics
- bounds violations
- assertions
- contracts
- edge cases
- finite-state correctness properties

### Why it matters

Kani is useful as an **additional verification layer**, even if Lean/Aeneas provides the semantic proof.

### Limitation

Model checking is not the same as proving the complete high-level semantics of the language, and some analyses may be bounded or resource-intensive.

### Role for VE

Use in CI alongside:

- tests
- property-based testing
- fuzzing
- Lean proofs

Reference: https://model-checking.github.io/kani/

---

## B.4 Verus

Verus is a verification system for Rust that supports proving functional correctness with specifications, preconditions, postconditions, and invariants.

### Why it matters

It offers another path to verified Rust and takes advantage of Rust's ownership discipline to reduce memory/aliasing proof burden.

### Role for VE

A serious alternative or supplementary verifier for parts of the Rust implementation.

Reference: https://verus-lang.github.io/verus/

---

# Appendix C — C, Frama-C, and CompCert

C remains the strongest alternative if the top priority becomes **end-to-end verified compilation to machine code** rather than Rust ergonomics and built-in memory safety.

## C.1 C

### Advantages

- extremely mature compiler ecosystem
- simple low-level execution model
- excellent runtime performance
- decades of formal-methods work
- direct compatibility with CompCert

### Disadvantages

- memory safety is not built into the language
- pointer validity, aliasing, bounds, lifetime, and undefined-behavior obligations must be controlled or proved
- larger proof burden for ordinary systems code

For VE, this matters because advanced coding agents may reduce the **human cost of writing proofs**, but they do not remove the need for those proofs to exist.

---

## C.2 Frama-C

Frama-C is a framework for analyzing and verifying C programs.

With ACSL specifications and its verification plugins, it can prove properties such as:

- function preconditions/postconditions
- memory safety
- loop invariants
- absence of some runtime errors
- functional properties

### Potential VE stack

```text
C semantic checker
       ↓
ACSL specifications
       ↓
Frama-C / proof obligations
       ↓
verified source-level properties
```

### Strength

Very mature C verification ecosystem.

### Weakness

Considerable annotation/proof burden compared with relying on Rust's type system for basic memory discipline.

Reference: https://www.frama-c.com/

---

## C.3 CompCert

CompCert is a formally verified optimizing C compiler.

Its central guarantee is roughly:

> the generated assembly preserves the observable behavior of the source C program, subject to CompCert's formal semantics and assumptions.

This is much stronger than simply testing a compiler.

### Why it matters

If we had:

1. a formally verified C checker, and
2. CompCert compilation,

we could get a strong end-to-end chain:

```text
formal VE specification
        ↑
proof of C checker correctness
        ↑
       C code
        ↓
     CompCert
        ↓
verified semantics-preserving machine code
```

### Major advantage over ordinary Rust today

CompCert is much more mature as a **verified source-to-machine-code compiler** than the standard Rust toolchain.

### Major disadvantage

Using C increases source-level memory-safety and verification obligations.

Reference: https://compcert.org/

---

## C.4 RustCompCert

RustCompCert is a 2026 research effort building a verified compiler for a sequential Rust subset, often described through a restricted language such as Rustlight, on top of CompCert-style infrastructure.

The project is important because it points toward combining:

- Rust's ownership/memory-safety model
- source-level verification
- verified compilation
- CompCert's machine-code guarantees

### Why it changes our decision

Before RustCompCert, the strongest argument for C was:

> C has CompCert; Rust does not have an equivalent mature verified compiler.

RustCompCert weakens that argument, although it is still a research-stage tool and supports only a subset of Rust.

### Potential long-term VE chain

```text
VE formal semantics
       ↑
verified Rust checker
       ↑
restricted safe Rust
       ↓
   RustCompCert
       ↓
verified machine code
```

### Current recommendation

Do **not** constrain the entire VE application to RustCompCert today.

Instead:

- write the entire product in Rust
- isolate a tiny trusted semantic/checking core
- keep that core intentionally simple
- verify it via Aeneas/Lean
- later attempt to compile that core through RustCompCert

Reference: https://arxiv.org/abs/2602.07455

---

## C.5 C + CompCert versus Rust + Aeneas/Lean

| Criterion | C + Frama-C + CompCert | Rust + Aeneas/Lean |
|---|---|---|
| Native speed | Excellent | Excellent |
| Memory safety by default | No | Yes |
| Source-level proof ecosystem | Very mature | Rapidly improving |
| Verified compilation to machine code | **Excellent / mature** | Emerging |
| Proof burden for memory safety | Higher | Lower |
| General development ergonomics | Lower | Higher |
| Fit for full VE product | Moderate | **High** |
| Fit for tiny maximum-assurance kernel | **High** | **High** |
| Current overall recommendation | Alternative | **Preferred** |

Because Astra/Fable-class coding agents can produce substantial proof and annotation code, the development-cost gap between C and Rust becomes less important.

However, **Rust's memory-safety model remains valuable even when AI writes the code**. It reduces the number and complexity of correctness obligations that must be proved.

Therefore the current recommendation remains:

> **Rust for VE, with a small verified core; Aeneas/Lean for functional correctness; RustCompCert as a future route to verified machine code.**

The main condition under which we would switch the critical core to C would be:

> a mature C + Frama-C + CompCert path provides significantly stronger end-to-end guarantees than the available Rust verified-compilation path, and those guarantees are important enough to justify the extra proof burden.

---

# Appendix D — How the Systems Fit Together

A useful summary is:

| System | Main contribution to VE |
|---|---|
| ACE / APE | Controlled English + mature logical semantics + test corpus |
| OWL | Ontology representation + reversible controlled-English precedent |
| CLCE | Richer controlled-English contexts/situations |
| Lojban | Evidence that spoken grammar can be deliberately unambiguous |
| PENG Light | Events, states, and Event Calculus |
| FRETish | Temporal requirements + proved semantic translations |
| TLA+ | Temporal/system behavior semantics |
| ForTheL / Naproche | Natural mathematical proof language |
| Verbose Lean | Controlled prose directly above Lean |
| Visored | Modern LLM-assisted natural-language theorem proving |
| Canonical English | Broad human↔agent and agent↔agent language vision |
| GF / ACE-in-GF | Abstract syntax + bidirectional/multilingual rendering |
| Lean | Formal semantic specification + proof kernel |
| Coq | Major precedent for verified software |
| Isabelle | Major theorem-proving precedent |
| PVS | FRET semantic-verification precedent |
| Rust | High-performance production implementation |
| Aeneas / hax | Rust → theorem-prover verification route |
| Kani / Verus | Additional Rust verification |
| C / Frama-C | Mature alternative source-verification stack |
| CompCert | Verified C → machine-code compiler |
| RustCompCert | Emerging verified Rust → machine-code path |

The project should **compose the strongest ideas rather than attempt to replace every one of these systems**.


---

# Appendix E — Common Verified Rust Subset for the Trusted Core

The project should deliberately define a **small common Rust subset** for the trusted semantic/checking core.

The goal is to write the critical core once and keep it compatible with both:

1. **Aeneas → Lean**, for proving functional/semantic correctness of the Rust implementation, and
2. **RustCompCert**, for eventually obtaining verified compilation from the restricted Rust source down to machine code.

Conceptually:

```text
                    Full Rust application
          UI / networking / LLMs / parallelism
                           │
                           ▼
                 trusted verified core
             written in common Rust subset
                    /               \
                   /                 \
          Aeneas → Lean          RustCompCert
        semantic correctness   verified compilation
```

## E.1 The two subsets

### Aeneas-friendly Rust

Aeneas is most comfortable with **safe, sequential Rust** and ordinary ownership/borrowing.

Its current limitations make it preferable to avoid complex features such as:

- concurrency
- complicated nested control flow in some cases
- interior mutability
- function pointers / closures in difficult forms
- highly dynamic abstractions
- intricate unsafe code

### RustCompCert / Rustlight-style Rust

RustCompCert targets a restricted sequential Rust language, often described through **Rustlight**.

Its supported subset focuses on a tractable, formally specified portion of Rust rather than the entire modern Rust language.

The September 2026 discussion described Rustlight as supporting structs/enums, `Box`/RAII, references and lifetimes, safe and unsafe modules, verified borrow checking, and compilation through CompCert to assembly. It listed concurrency, polymorphism, traits, and closures as excluded. This is a **reported tool snapshot**, not proof that any particular VE implementation is supported. Rustlight's reported unsafe support does not extend Aeneas's safe-Rust scope. Recheck both pinned tool versions before choosing core constructs.

The working hypothesis is that the intersection between these two subsets is large enough for a parser/checker kernel. Establish that with the representative prototype in Phase 5 before relying on a shared implementation.

---

## E.2 Common core we should target

The trusted VE core should prefer constructs such as:

```text
pure or mostly pure functions
if / else
match
simple loops
recursion where practical
structs
enums
integers
booleans
arrays / simple vectors
owned values
immutable references
mutable references with straightforward lifetimes
Box-like ownership
Option
Result
deterministic sequential execution
explicit error handling
```

These constructs appear sufficient at the algorithm-design level for the core jobs below; availability in both toolchains still needs validation:

```text
tokens
  ↓
canonical parsing
  ↓
semantic AST construction
  ↓
well-formedness checking
  ↓
type / semantic validation
  ↓
canonicalization
  ↓
serialization
```

These are primarily **tree-processing and validation algorithms**, not systems that inherently require advanced runtime features.

---

## E.3 Features to avoid in the trusted core

The trusted checker should deliberately avoid, unless future verification tooling supports them cleanly:

```text
threads
async/await
interior mutability
complex trait machinery
dynamic dispatch
closures with complicated capture behavior
FFI
unsafe pointer manipulation
custom allocators
self-referential structures
reflection-like behavior
heavy macro-generated semantics
runtime plugin systems
```

These features can still be used freely in the **untrusted outer application**.

For example:

```text
Full VE application
├── LLM APIs
├── network services
├── databases
├── editor integration
├── parallel indexing
├── UI
└── verified_core/
    ├── tokenizer
    ├── canonical parser
    ├── semantic AST
    ├── checker
    ├── canonicalizer
    └── serializer
```

Only `verified_core/` needs to obey the strict subset.

---

## E.4 Why this is valuable

If the same Rust core is accepted by both verification paths, we can establish two complementary guarantees.

### Functional / semantic correctness

Using:

```text
Rust core
   ↓
Aeneas
   ↓
Lean model
   ↓
proofs
```

we aim to prove:

> The Rust checker implements the formal VE semantics.

For example:

```text
If the checker accepts a sentence and produces AST A,
then A satisfies the VE formal specification.
```

### Compiler correctness

Using:

```text
restricted Rust core
       ↓
   RustCompCert
       ↓
verified machine code
```

we aim to prove:

> The compiled machine code preserves the verified behavior of the Rust core.

Combining both gives the long-term chain:

```text
VE language specification
          ↑
Lean semantic proof
          ↑
actual Rust checker
          ↓
verified compiler
          ↓
machine code
```

This is substantially stronger than either source-level verification or verified compilation alone.

---

## E.5 Architectural recommendation

Treat this common subset as a **project-level coding standard** from the beginning rather than trying to retrofit it later.

The rule should be:

> The trusted core must remain inside the intersection of the Rust subset supported by our source-verification path and the Rust subset supported by our verified-compilation path.

Everything outside that core may use ordinary modern Rust.

This lets the project combine:

- normal Rust performance
- normal Rust ergonomics for the broader product
- formal semantic verification
- a realistic future path to verified machine code
- a small trusted computing base


---

# Appendix F — Foundational Reasoning That Led to the Architecture

This section preserves several important conceptual insights from the original brainstorming that explain **why** the architecture looks the way it does.

## F.1 Why autoformalization is hard even when theorem proving is easy to verify

A theorem prover such as Lean can verify whether a proof proves a formal proposition.

That does **not** automatically verify that the formal proposition is the correct interpretation of the original English.

Example:

> Every positive real number has a positive square root.

Possible formalizations include:

```text
A.
For every real x:
    if x > 0,
    then there exists y > 0
    such that y² = x.

B.
For every real x:
    if x > 0,
    then there exists y
    such that y² = x.

C.
For every real x:
    if x ≥ 0,
    then there exists y ≥ 0
    such that y² = x.
```

All three may be mathematically true and provable.

Lean can verify each proof perfectly.

Lean cannot, by itself, determine which one best captures the original sentence.

This is the central distinction:

> **Proof verification is different from statement interpretation.**

A wrong formalization can still be perfectly well-typed, mathematically coherent, and provable.

A fully formal checker for `ordinary English ≡ Lean proposition` would itself need a precise formal interpretation of the English. Producing that interpretation is the autoformalization problem; proof checking alone cannot supply it. A controlled language with already specified semantics can support an equivalence theorem, but arbitrary English has no such given formal reference.

This is one of the strongest reasons VE needs a **canonical semantic layer**, rather than being merely an LLM that translates arbitrary English into Lean.

---

## F.2 The asymmetry between ordinary English and formal language

The two translation directions are fundamentally different.

### Formal meaning → readable English

If the semantic structure is already known, generation can be deterministic.

For example:

```text
Forall x:
    Doctor(x) →
    Exists y:
        Patient(y) ∧ Treats(x, y)
```

can have a canonical rendering such as:

> Every doctor treats at least one patient.

This direction can be designed to be lossless.

### Ordinary English → formal meaning

The reverse direction may be underdetermined.

Example:

> I saw the man with the telescope.

Possible meanings include:

1. I used the telescope to see the man.
2. The man had the telescope.

No parser can recover a uniquely intended interpretation if the speaker did not provide enough information.

Therefore VE should explicitly recognize an **ambiguity boundary**:

```text
ordinary English
      ↓
candidate interpretations
      ↓
clarification / context / user choice
      ↓
canonical semantic object
      ↓
lossless verified processing
```

Once a canonical meaning has been selected, the system can become deterministic and formally checked.

Before that point, uncertainty may be unavoidable.

---

## F.3 Generate-many + verify + clarify

A useful workflow emerged early in the discussion.

Instead of forcing one model-generated interpretation, the system can generate several candidates:

```text
ordinary English
      ↓
LLM / semantic parser
      ↓
candidate meaning A
candidate meaning B
candidate meaning C
      ↓
deterministic language checker
      ↓
remove invalid candidates
      ↓
semantic comparison / back-translation
      ↓
user or agent selects intended meaning
      ↓
canonical VE representation
```

The candidate space can be large: changing quantifier order, domains, assumptions, parentheses, or strict inequalities can yield different well-formed and even provable statements. Type checking rejects malformed candidates, and optional proof attempts can provide evidence about mathematical claims; neither ranks fidelity to the source. Failure to find a proof is not itself a disproof or evidence of mistranslation.

Compare candidates against surrounding definitions and examples, show their canonical back-translations, and ask for clarification where the source does not decide. An LLM's semantic ranking remains a proposal rather than a formal certificate of intended meaning.

This combines strengths of probabilistic and formal systems:

### LLMs are good at

- proposing interpretations
- resolving likely intended references
- rewriting natural English
- generating formal candidates
- explaining differences between interpretations

### Deterministic systems are good at

- rejecting malformed structures
- enforcing syntax
- checking types
- enforcing semantic invariants
- canonicalization
- proof checking

The key design principle is:

> **Generation can be probabilistic; acceptance should be deterministic.**

This is also why Canonical English's NOAH-style architecture is attractive.

---

## F.4 Back-translation as a semantic user interface

Back-translation can help humans inspect what the machine believes a sentence means.

Example:

Original:

> Every doctor treats a patient.

Machine interpretation:

```text
For every doctor D,
there exists at least one patient P
such that D treats P.
```

The system can display this canonical paraphrase before final acceptance.

For ambiguous input:

> I saw the man with the telescope.

it could display:

### Interpretation A

> I used a telescope to see the man.

### Interpretation B

> I saw a man who had a telescope.

This turns semantic verification into an interactive process rather than a hidden parser decision.

Back-translation does not prove that the selected meaning matches a person's private intention.

It does make the chosen formal meaning **visible and inspectable**.

---

# Appendix G — Why ACE Was Restricted

ACE's restrictions were not arbitrary.

They reflect its historical goals and the engineering context in which it was built.

## G.1 Original motivation

ACE originated primarily as a controlled language for things such as:

- software specifications
- knowledge representation
- rule systems
- formal requirements
- machine reasoning

Examples include statements like:

> Every customer has an account.

> If a payment fails, the system sends an error message.

The objective was not:

> formalize every aspect of human conversation.

It was closer to:

> define a practical English-like subset where accepted sentences have known formal interpretations.

---

## G.2 The core design trade-off

ACE aimed to combine:

```text
English-like syntax
+
automatic parsing
+
formal semantics
+
predictability
```

Rather than solving unrestricted English ambiguity, ACE deliberately restricted the grammar.

This made the language useful and implementable.

The strategy was:

> Do not solve all English.  
> Define a subset for which interpretation rules are reliable.

That was an extremely reasonable design choice for its era.

---

## G.3 APE architecture

The Attempto Parsing Engine roughly follows:

```text
ACE text
   ↓
tokenizer
   ↓
grammar parser
   ↓
unresolved DRS
   ↓
anaphora/reference resolution
   ↓
resolved DRS
   ↓
formal outputs
```

Possible outputs include:

- first-order logic
- OWL/SWRL
- TPTP
- RuleML
- regenerated ACE

The architecture is modular and remains a valuable reference.

---

## G.4 Why tests instead of a fully verified implementation?

ACE has formally described semantics, but the executable APE parser is not itself backed by a complete machine-checked proof of implementation correctness.

Instead, the project historically relied heavily on:

- specification
- implementation review
- regression tests
- thousands of ACE→DRS examples

This makes sense historically.

At the time ACE matured, formally verifying an entire NLP parser, reference resolver, semantic translator, and output stack would itself have been a major formal-methods research program.

Today, modern proof assistants and strong coding agents make that much more realistic.

VE can therefore preserve ACE's strengths while improving the verification story.

---

# Appendix H — Verification Taxonomy for Scientific Work

The phrase **"verify a scientific paper"** is ambiguous.

VE should distinguish at least three levels.

## H.1 Logical correctness

Question:

> Does the conclusion follow from the explicitly stated premises?

This includes:

- assumption dependency
- contradiction detection
- invalid implication
- missing preconditions
- inconsistent definitions
- circular reasoning

This is highly suitable for formal verification.

---

## H.2 Mathematical correctness

Question:

> Are the mathematical derivations themselves valid?

This includes:

- algebra
- calculus
- theorem applications
- inequalities
- symbolic manipulations
- formal proofs
- numerical bounds

This can often be checked at Lean-level rigor.

---

## H.3 Empirical correctness

Question:

> Does the model accurately describe the physical world?

This is different.

A formal system can verify that:

```text
given dataset D
given measurement model M
given uncertainty model U
given statistical procedure S
the reported inference follows
```

But it cannot prove from the paper text alone that:

- instruments had no unknown systematic error
- the sample is representative
- no hidden confounder exists
- nature actually obeys the proposed theory

Therefore VE should distinguish:

```text
formal logical validity
mathematical validity
empirical support
```

rather than collapsing them into one binary “verified” status.

---

# Appendix I — Human, LLM, and Proof-Kernel Division of Labor

Modern frontier models substantially change the economics of this project.

They reduce the cost of:

- writing parsers
- translating code
- writing Rust
- creating Lean definitions
- generating proof attempts
- repairing failing proofs
- porting test suites
- formalizing papers
- generating candidate semantic interpretations

But LLMs should remain outside the trusted core.

The preferred division of labor is:

## Humans

Humans decide:

- what language constructs mean
- which semantic distinctions matter
- whether a proposed interpretation matches intended usage
- what scope the language should have
- difficult linguistic and philosophical choices
- domain-specific modeling decisions

## LLM coding/reasoning agents

Models such as frontier OpenAI/Anthropic coding agents can perform much of the mechanical work:

- write Rust
- write Lean
- generate proof scripts
- refactor grammar
- create tests
- port ACE examples
- formalize existing papers
- search for counterexamples
- generate candidate interpretations

## Deterministic tools and proof kernels

These decide what is actually accepted:

- VE parser/checker
- Rust type checker
- Aeneas/verification pipeline
- Lean kernel
- verified compiler where applicable

The guiding principle is:

> **Humans decide semantics.  
> LLMs do much of the implementation work.  
> Formal systems decide correctness.**

---

# Appendix J — Additional Historical and Conceptual Notes

## J.1 Loglan and Lojban

Lojban grew out of Loglan, originally associated with experiments around linguistic relativity and the idea of a logically structured human language.

Its significance to VE is conceptual:

> humans can speak a deliberately engineered language whose grammar reduces ambiguity.

However, Lojban does not provide the same deterministic theorem-prover semantics that ACE attempts to provide.

This reinforces the distinction between:

```text
unambiguous syntax
```

and:

```text
fully specified formal semantics
```

VE needs both.

---

## J.2 ACE ↔ OWL round-trip precedent

ACE-related work on OWL verbalization demonstrated an important architectural precedent.

For a supported formal fragment:

```text
OWL
 ↓
ACE
 ↓
OWL
```

can preserve logical meaning.

This supports one of VE's main design goals:

> controlled natural language can be treated as a reversible surface syntax for a formal semantic structure.

VE generalizes that idea beyond OWL.

---

## J.3 Canonical English / NOAH maturity

Canonical English is especially aligned with VE's intended use because it explicitly targets:

- machine-to-human communication
- machine-to-machine communication
- agentic communication
- explicit word senses
- explicit entity grounding
- deterministic validation after best-effort parsing

However, as of the research performed during this brainstorming:

- the project was very new
- its published test base was still small
- the ideal language was not yet fully constructively defined
- the parser was described as best-effort
- the public repository linked from the site was not accessible at the time checked

Therefore CE should be treated as:

> the closest conceptual collaborator/foundation candidate,

not yet as a mature formally verified implementation to adopt unchanged.

---

# Appendix K — Project Principles Derived from the Discussion

The following principles summarize the reasoning accumulated throughout the brainstorming.

## K.1 Meaning is primary

The semantic AST is the language core.

English syntax is a human interface to that meaning.

---

## K.2 Ambiguity must be surfaced, not hidden

If multiple interpretations remain valid, the system should expose them.

It should not silently choose one merely because an LLM assigns it higher probability.

---

## K.3 Strict canonical language and flexible authoring should be separate

Users should be able to write naturally.

The authoring assistant can help transform loose input into strict VE.

Therefore:

```text
flexible natural authoring
        ↓
AI-assisted interpretation
        ↓
strict canonical VE
```

is preferable to requiring humans to memorize every grammatical restriction.

---

## K.4 The trusted core should be small

The trusted component should contain only what is necessary for:

- canonical parsing
- semantic validation
- AST construction
- canonicalization
- proof-relevant transformations

Everything else may remain ordinary software.

---

## K.5 Formal verification is layered

Possible levels include:

```text
tests
↓
property testing / fuzzing
↓
model checking
↓
source-level functional proof
↓
proof of semantic preservation
↓
verified compilation
↓
machine code
```

Not every component requires the strongest level.

The critical semantic kernel should receive the strongest treatment.

---

## K.6 Formalization should expose missing information

When formalizing an existing scientific/legal document, the system should not silently invent assumptions.

It should report:

- missing definitions
- hidden assumptions
- ambiguous referents
- missing bounds
- unresolved interpretations
- dependence on external doctrine or evidence

The inability to formalize uniquely is itself valuable information.

---

## K.7 Provenance is first-class

Every imported rule, interpretation, or formalized claim should be able to retain provenance such as:

- source document
- paragraph
- theorem
- case
- version
- date
- author
- external dataset
- interpretation method

This is essential for science, law, policy, and agent governance.

---

## K.8 Different domains may require different semantic modules

The project should not force all meaning into one logic.

Instead, VE can expose a common semantic framework with domain modules such as:

```text
core predicate logic
mathematics / dependent type theory
events / Event Calculus
temporal logic
epistemic logic
deontic logic
probability
defeasible reasoning
legal doctrine
scientific evidence
```

Lean can formalize the metatheory connecting these modules without requiring users to see the underlying formal machinery.

---

## K.9 VE should be a language for communication, not only proof

Mathematics is one important application, but the broader objective is:

```text
human ↔ human
human ↔ agent
agent ↔ human
agent ↔ agent
```

with explicit, inspectable, machine-checkable meaning.

This broader goal is what distinguishes VE from a natural-language syntax layer for Lean alone.


---

# Appendix L — Why This Project Is Newly Feasible

A major premise of the project is that the cost structure of formal-language engineering has changed.

Historically, the expensive parts included:

- implementing parsers and language tooling
- writing large regression suites
- porting semantics across formal systems
- writing proof-assistant code
- repairing formal proofs
- maintaining multiple backends
- formalizing existing scientific or legal texts by hand

Modern frontier coding and reasoning models can substantially reduce these costs.

They can assist with:

- Rust implementation
- Lean definitions and proof scripts
- grammar ports
- test generation
- fuzz/property-test generation
- formalization of existing documents
- candidate semantic interpretations
- proof repair
- comparison between formalizations
- documentation
- migration between language versions

This changes the principal bottleneck.

The hardest part increasingly becomes:

> **deciding what the language should mean**

rather than:

> **manually writing all of the code and proof scaffolding**

That is a profound shift.

## L.1 What AI changes

AI can make ambitious formalization projects economically realistic.

For example, an agent can:

```text
read an ACE grammar
        ↓
propose a typed VE AST
        ↓
generate Rust parser code
        ↓
generate Lean definitions
        ↓
attempt equivalence proofs
        ↓
repair failed proofs
        ↓
generate regression tests
```

## L.2 What AI does not change

AI does not eliminate the need to decide:

- whether `finally` carries a presupposition
- how vague predicates work
- how legal precedent interacts with text
- whether two formulations are semantically identical
- how belief differs from truth
- what counts as an exception
- whether a scientific approximation is valid in a declared regime

Those are language-design and modeling questions.

The project should therefore exploit AI heavily for implementation while keeping semantic decisions explicit and reviewable.

## L.3 Time-sensitive capability assumption

The project should maintain a short, dated capability note recording the frontier coding/formal-reasoning tools currently used.

That note should be treated as **replaceable project metadata**, not part of the stable language specification.

For example:

```text
Tooling profile — 2026-09

Primary coding agents:
- frontier OpenAI coding/reasoning model
- frontier Anthropic coding/reasoning model

Primary formal checker:
- Lean

Primary production language:
- Rust
```

Specific model benchmarks will age quickly and should not be embedded permanently into the core language standard.

---

# Appendix M — Strong Math Goal: VE as a Human Front End to Lean

For mathematics, the long-term goal should be stronger than merely supporting simple theorem statements.

The target should be:

> **Everything a mathematician reasonably needs to state or prove in Lean should be expressible through a natural mathematical dialect of VE.**

The user should write something like:

```text
Let G be a finite group.
Assume that the order of G is prime.
Then G is cyclic.
```

and the system should construct an exact formal theorem.

The architecture should be:

```text
mathematical VE
      ↓
typed semantic AST
      ↓
Lean declarations / theorem statements / proof terms
      ↓
Lean kernel
```

Lean remains the final mathematical authority.

VE becomes:

- authoring language
- explanation language
- proof-structure language
- semantic interchange language

## M.1 Escape hatch

VE should not force every low-level Lean mechanism into beautiful prose.

Some Lean features are primarily implementation mechanisms:

- metaprogramming
- tactic internals
- universe plumbing
- specialized dependent pattern matching
- low-level elaborator configuration

For these, VE should support a controlled escape hatch.

The key constraint should be:

> embedded low-level content must remain explicit and cannot silently alter surrounding semantics.

---

# Appendix N — Concrete AI-Constitution Case Study

An AI constitution is a useful example because it contains several different kinds of normative content.

A constitution may include:

- hard prohibitions
- goals
- priorities
- default behaviors
- exceptions
- values
- context-sensitive standards
- procedural requirements

A flat rule representation is inadequate.

Example:

```text
HARD RULE:
Do not intentionally disclose protected secrets.

PRIORITY:
Prevent catastrophic harm outranks ordinary helpfulness.

DEFAULT:
Assist the user unless a higher-priority rule applies.

VALUE:
Preserve user agency.

CONTEXTUAL STANDARD:
A response meaningfully undermines user agency when...
```

A real AI constitution may also emphasize the **spirit** of principles rather than rigid literal application.

VE should model this distinction explicitly.

Potential semantic categories:

```text
Obligation
Permission
Prohibition
Priority
DefaultRule
Exception
Value
Standard
InterpretivePrinciple
```

This is a strong benchmark for the normative layer because it tests whether the language can represent more than simple Boolean rules.

---

# Appendix O — Explicit Guarantees and Non-Goals

The language should publish a short, precise guarantee contract.

## O.1 Core guarantees

For a specific VE language version, the project should aim to guarantee:

### G1. Deterministic canonical parsing

A valid canonical VE document has exactly one accepted parse.

### G2. Defined semantic interpretation

Every accepted semantic AST has a formally defined meaning.

### G3. Canonical rendering

Every canonical AST has a deterministic canonical textual representation.

### G4. Round-trip correctness

For supported canonical objects:

```text
parse(print(ast)) = ast
```

### G5. Semantic preservation

Verified transformations preserve the semantics defined by the source language version.

### G6. Explicit ambiguity handling

Input with unresolved ambiguity is not silently promoted to canonical meaning.

For every accepted pronoun or anaphoric reference, the versioned discourse rules must select exactly one accessible antecedent. If they do not, request clarification or reject the input. This is an explicit reference-resolution proof obligation, beyond unique syntactic parsing; it does not establish that the selected antecedent matches an unexpressed human intention.

### G7. Version stability

The meaning of a valid document is determined by:

```text
(document, language-version, declared modules)
```

and does not silently change when a newer language version is released.

## O.2 Important non-goals

VE should **not** claim:

- perfect recovery of human intent from arbitrary ambiguous English
- universal empirical truth
- automatic resolution of normative disagreement
- elimination of all vagueness
- one universal logic for every domain
- a proof that every VE sentence sounds natural to English speakers
- a completeness theorem covering every meaning expressible in unrestricted English

The last two aspirations lack a complete formal reference specification in this proposal. A specified grammar can be checked; perceived naturalness should be evaluated with speakers, and expressiveness measured against declared domains and corpora. Those evaluations must not be presented as proofs about all English.

---

# Appendix P — Language-Version Governance

Language versioning is distinct from versioning legal doctrine or scientific datasets.

A VE document should declare the version of the language under which it is interpreted.

Example:

```text
ve-version: 1.2
modules:
  - core-logic@1
  - time@2
  - probability@1
```

The fundamental rule should be:

> **A document's meaning must never silently change because the implementation was upgraded.**

Therefore:

```text
VE document
+
VE language version
+
module versions
+
external referenced ontology versions
=
stable interpretation
```

## P.1 Semantic-version rule

Possible policy:

- **Patch:** implementation fixes, diagnostics, performance; no intended semantic change.
- **Minor:** new syntax/constructs/modules; old canonical meanings preserved.
- **Major:** semantic changes allowed, but migration must be explicit.

## P.2 Semantic hashes

Canonical documents could optionally carry a semantic hash computed over:

- canonical AST
- language version
- module versions
- referenced vocabulary identities

This would make semantic identity auditable across systems.

---

# Appendix Q — Conformance and Independent Implementations

VE should be a language standard, not merely one Rust codebase.

An independent implementation should be able to demonstrate conformance.

Publish test vectors such as:

```text
input canonical text
        ↓
expected AST
        ↓
expected canonical output
        ↓
expected semantic representation
```

## Q.1 Conformance levels

Possible levels:

- syntax conformance
- AST conformance
- semantic conformance
- round-trip conformance
- verified conformance

## Q.2 Reference implementation versus standard

Keep these separate:

```text
VE Specification
    ≠
VE Rust implementation
```

The Rust implementation may be the reference implementation, but it should not define the language merely by its accidental behavior.

---

# Appendix R — Evaluation and Benchmark Suite

The project should define measurable success criteria early.

## R.1 Canonical-language properties

Targets:

- 100% unique parse for valid canonical inputs
- 100% round-trip correctness for accepted canonical ASTs
- 100% defined semantics for accepted ASTs

These should ultimately be theorems, not merely empirical measurements.

## R.2 Ordinary-English formalization metrics

Measure:

- percentage of source sentences formalized without clarification
- percentage requiring one or more clarifications
- number of candidate interpretations
- semantic error rate under expert review
- disagreement between independent formalizers

Datasets should include:

- everyday statements
- software requirements
- mathematical prose
- physics papers
- legal texts
- policy documents
- agent instructions

## R.3 ACE compatibility benchmark

Track:

```text
ACE examples supported
ACE examples semantically equivalent
ACE examples intentionally rejected
ACE examples whose semantics differ
```

Every difference should have a documented reason.

## R.4 Mathematical benchmark

Measure:

- theorem-statement translation success
- proof translation success
- Lean compilation success
- clarification count
- human editing required
- proof length overhead
- semantic fidelity

## R.5 Scientific-paper benchmark

Measure:

- claims formalized
- assumptions identified
- undefined concepts detected
- ambiguous statements detected
- derivations formally verified
- unverified empirical steps
- hidden assumptions surfaced
- approximation-domain violations

## R.6 Performance benchmark

For the Rust runtime:

- parsing throughput
- latency
- memory use
- canonicalization throughput
- AST serialization speed
- large-document scaling
- agent-to-agent message throughput

---

# Appendix S — Extension Mechanism

A general-purpose formal language must be extensible.

Without a disciplined extension mechanism, the language will either become bloated or force every domain into awkward generic constructs.

## S.1 Core language versus modules

Keep the core small.

Potential modules:

```text
ve.core
ve.math
ve.time
ve.events
ve.probability
ve.epistemic
ve.deontic
ve.legal
ve.science
ve.software
```

A document explicitly declares which modules it uses.

## S.2 Domain vocabulary

Users should be able to define domain terms.

Definitions should produce typed semantic entries rather than merely textual aliases.

## S.3 External formal objects

VE should support references to externally verified objects such as:

- Lean theorem
- OWL ontology
- TLA+ module
- dataset
- Wikidata entity
- DOI
- legal case
- formal standard

The reference should include a stable identifier and version where possible.

## S.4 Escape hatches

Escape hatches are useful but must be explicit.

Examples:

```text
[Lean expression]
[TLA+ formula]
[SMT assertion]
[raw ontology axiom]
```

Unsupported semantics must never be approximated silently.

---

# Appendix T — Canonicalization, Equivalence, and Paraphrase

These concepts must not be conflated.

## T.1 Same canonical AST

Strongest identity.

Two texts map to exactly the same canonical semantic object.

## T.2 Semantic equivalence

Two different ASTs may denote the same meaning under VE semantics.

## T.3 Logical equivalence

Two propositions may be equivalent inside a particular logic.

## T.4 Paraphrase

Two natural-language statements may be reasonable paraphrases while differing in:

- emphasis
- presupposition
- discourse structure
- pragmatic effect
- lexical choice

Paraphrase should not automatically imply semantic identity.

## T.5 Why the distinction matters

For agent communication:

> same canonical AST

is ideal.

For theorem proving:

> logical equivalence

may be sufficient.

For human writing:

> paraphrase

may be acceptable.

The system should tell users which relationship holds.

---

# Appendix U — Security and Adversarial Robustness

If VE becomes an agent communication protocol, semantics become a security boundary.

Potential attacks include:

- ambiguous payloads
- intentionally misleading paraphrases
- parser differentials
- Unicode confusables
- malicious external references
- semantic-version downgrade attacks
- conflicting ontology versions
- resource-exhaustion inputs
- cyclic definitions
- hidden assumptions encoded in imported modules

## U.1 Canonical form as a security mechanism

Before signing, caching, or executing a message:

```text
source text
   ↓
canonical AST
   ↓
canonical serialization
   ↓
signature / authorization
```

Agents should authorize the **canonical meaning**, not merely the raw text.

## U.2 Parser differential attacks

Two implementations must not interpret the same canonical document differently.

The conformance suite and formal grammar should explicitly target this risk.

## U.3 Signed semantic messages

Possible future agent protocol:

```text
sender
timestamp
language-version
module versions
canonical semantic AST
semantic hash
signature
```

## U.4 Resource limits

Formal correctness does not imply denial-of-service resistance.

The production checker should define limits for:

- nesting depth
- recursive definitions
- imported modules
- external resolution
- proof search
- message size

---

# Appendix V — Error and Ambiguity Taxonomy

The system should produce structured diagnostics rather than generic parse failures.

Potential categories:

```text
SyntaxError
UnknownWordSense
AmbiguousWordSense
AmbiguousReference
QuantifierScopeAmbiguity
TemporalAmbiguity
UndefinedTerm
TypeMismatch
MissingAssumption
UnsupportedConstruct
ConflictingDefinition
UnresolvedExternalReference
SemanticVersionMismatch
PotentialPragmaticAmbiguity
```

This taxonomy is valuable for:

- authoring tools
- scientific audits
- training data
- benchmarking
- agent negotiation

---

# Appendix W — Provenance and Evidence Graph

Every important semantic object should be able to carry provenance.

Example:

```text
Claim C17
  source:
    paper DOI ...
    page 8
    equation 12

  depends_on:
    assumption A3
    theorem T4
    dataset D2

  formalized_by:
    agent X
    human reviewer Y

  verified_by:
    Lean theorem Z
```

For legal doctrine:

```text
Rule R
  source:
    Supreme Court case
    year
    holding
    opinion section

  modified_by:
    later case
```

For agent policy:

```text
Rule P
  source:
    constitution v3
    section 4.2
```

Provenance should be part of the data model, not merely comments.

---

# Appendix X — Interoperability Strategy

VE should avoid becoming a closed formal ecosystem.

Potential targets and bridges:

```text
Lean
Coq
Isabelle
PVS
OWL
TLA+
SMT-LIB
JSON-LD
RDF
TPTP
RuleML
OpenAPI / schema systems
```

The semantic AST should support multiple backends where appropriate.

Not every construct must map to every backend.

Backends should declare supported fragments, and unsupported translation must fail explicitly rather than silently approximate.

---

# Appendix Y — Authoring Experience

A formal language will fail if humans hate writing it.

The user experience should therefore be as important as the semantics.

## Y.1 Assisted authoring

The user writes:

> Sarah finally stopped avoiding John.

The editor may ask:

```text
I need clarification:

1. Does "finally" assert or merely suggest
   that the avoidance lasted longer than expected?

2. Whose expectation is relevant?
   - speaker
   - Sarah
   - unspecified context
```

Once answered, the sentence becomes canonical.

## Y.2 Two views

Users should be able to switch between:

### Natural view

Readable prose.

### Semantic view

Explicit canonical meaning.

## Y.3 Progressive strictness

The editor can allow loose prose during drafting.

Only canonicalized passages receive the **verified** status.

---

# Appendix Z — Language Governance and Standardization

If the language succeeds, governance becomes important.

Questions include:

- who can change semantics?
- how are new modules approved?
- who decides canonical wording?
- how are breaking changes handled?
- how are conflicting domain extensions resolved?
- how are security issues handled?

A possible structure:

```text
VE Core Specification
    stable governance

Official semantic modules
    versioned independently

Community/domain modules
    separately namespaced
```

Important principle:

> No implementation vendor or LLM provider should be able to silently redefine the language.

The formal specification is authoritative.

---

# Appendix AA — Open-Source and Reproducibility Strategy

The core language specification, reference checker, proof artifacts, and conformance suite should ideally be public.

This improves:

- trust
- academic reproducibility
- independent implementations
- security review
- long-term archival
- interoperability

A publication should ideally include:

```text
specification
Lean formalization
Rust reference implementation
proof artifacts
conformance tests
benchmark corpus
formalized demonstration documents
```

---

# Appendix AB — Recommended Project Artifacts

The project should maintain several distinct documents rather than one monolithic specification.

## AB.1 Vision document

Why the language should exist.

## AB.2 Language specification

Exact syntax and semantics.

## AB.3 Formal metatheory

Lean definitions and proofs.

## AB.4 Implementation specification

Rust architecture and verified-core constraints.

## AB.5 Conformance specification

Tests and independent-implementation rules.

## AB.6 Semantic-module specifications

Time, probability, epistemic logic, etc.

## AB.7 Benchmark corpus

ACE, math, physics, law, policy, agent communication.

## AB.8 Threat model

Security and adversarial communication.

## AB.9 Governance document

Versioning and language evolution.

Separating these artifacts will keep the formal language standard stable while tooling and implementations evolve.

---

# Appendix AC — Revised Project Thesis

A more complete project thesis is:

> **Build a versioned, extensible, human-readable formal communication language whose accepted canonical documents have deterministic machine-checkable semantics; whose meanings can be rendered back into readable language without semantic loss; whose critical implementation can be formally connected to its specification; and whose semantic modules can target systems such as Lean, temporal logic, ontologies, scientific reasoning, legal doctrine, and agent policy.**

The project deliberately separates:

```text
natural authoring
        ↓
probabilistic interpretation
        ↓
human/agent clarification
        ↓
canonical VE
        ↓
verified semantics
        ↓
formal reasoning / execution / communication
```

The central promise remains:

> **Probabilistic systems may propose meaning, but only deterministic and formally specified systems may certify it.**


---

# Appendix AD — Final Conversation Coverage Audit and Recovered Details

This appendix was added after a final audit of the original discussion to preserve concrete details that were either implicit, distributed across sections, or easy to lose in a higher-level architecture summary.

## AD.1 ACE's exact grammatical boundary matters

One reason ACE feels natural but still narrower than ordinary English is that its verb system is intentionally restricted.

The ACE 6.7 construction rules state that verbs in declarative and interrogative sentences are normally **third-person simple present**; imperatives use second person. That means ordinary constructions such as:

```text
Sarah was avoiding John.
Sarah has avoided John.
Sarah had been avoiding John.
Sarah will have been avoiding John.
```

are not simply ordinary native ACE tense/aspect constructions.

This is a concrete example of why VE needs a richer temporal/aspect layer rather than only a larger vocabulary.

Reference: https://attempto.ifi.uzh.ch/site/docs/ace_constructionrules.html

---

## AD.2 ACE can encode some temporal ideas indirectly

The absence of a native temporal operator does not mean ACE is incapable of describing time.

A statement such as:

> Whenever a request is received, it is eventually answered.

can be encoded indirectly by introducing explicit time objects:

```text
Every request R that is received at a time T1
is answered at a time T2
and T2 is later than T1.
```

Conceptually:

```text
Received(R,T1)
→
∃T2. LaterThan(T2,T1) ∧ Answered(R,T2)
```

This distinction is important:

- **expressible by explicit modeling** is not the same as
- **native and natural in the language**

VE should make common temporal concepts such as:

- eventually
- always
- before
- after
- until
- during
- within N seconds

first-class rather than forcing every writer to manually construct time variables.

---

## AD.3 ACE already shows pressure beyond plain first-order logic

APE's internal DRS machinery is richer than a simple FOL syntax layer.

Its source includes machinery for modal constructions and possible-world-style interpretation, while some richer modal/nonmonotonic DRS constructs are outside the supported FOL conversion in particular versions.

The architectural lesson is:

> As the natural-language layer becomes richer, the semantic target must also become richer.

VE should therefore not define itself as merely "English that maps to FOL."

FOL should be one important semantic fragment.

The discussion also noted that a unique ACE DRS can leave **background axioms** underspecified, especially for plurals and modality. A unique representation is not a complete axiomatization of every represented concept. VE must declare the semantic assumptions and modules required for such constructs.

---

## AD.4 APE implementation facts worth preserving

The APE reference implementation is:

- primarily SWI-Prolog
- modularized into tokenizer, grammar, lexicon, anaphora/reference resolution, and DRS translators
- capable of producing DRS, FOL, OWL/SWRL, TPTP, RuleML, and paraphrases
- distributed as free software under LGPL terms
- backed by a substantial regression suite

The ACE 6.6 release notes describe roughly **3,500 small ACE texts with expected DRSs** in the regression corpus.

This reinforces our decision to use APE as:

- a semantic reference
- a compatibility oracle
- a regression corpus

rather than as the mandatory production architecture.

References:

- https://github.com/Attempto/APE
- https://github.com/Attempto/APE/releases

---

## AD.5 Lojban's historical construction

Lojban is not "formal English."

It grew from Loglan, whose development began with James Cooke Brown in the 1950s and was associated with experiments around language, logic, and linguistic relativity.

Lojban later developed separately.

Its root vocabulary was algorithmically influenced by six source languages:

- Chinese
- English
- Hindi
- Spanish
- Russian
- Arabic

The significance for VE is not the vocabulary itself.

The lesson is:

> A language can be deliberately engineered for logical structure and human speech.

But Lojban also demonstrates that:

> uniquely parseable grammar does not automatically give complete machine-checkable semantics for every utterance.

References:

- https://www.lojban.org/static/publications/etymology.html
- https://lojban.org/publications/cll/cll_v1.1_book.pdf

---

## AD.6 The quantifier example that motivated the comparison

A useful comparison from the discussion was:

> Every doctor treats a patient.

ACE can use almost exactly that surface sentence.

Its intended logical structure is approximately:

```text
∀x.
    Doctor(x)
    →
    ∃y.
        Patient(y)
        ∧ Treats(x,y)
```

Lojban can make quantifier structure explicit with its predicate-logic-oriented variable and quantifier system.

The broader lesson was:

- English may leave structural interpretation implicit.
- Lojban makes much of the structure syntactically explicit.
- ACE goes further by defining a controlled mapping into a formal semantic representation.

This comparison concerns specified logical structure. “Good doctor” still needs a chosen predicate meaning in both Lojban and ACE; formal quantifiers alone do not settle lexical vagueness or context. This preserves the correction made in the discussion, rather than suggesting ACE automatically defines every content word.

That is why ACE became the more relevant ancestor for VE.

---

## AD.7 Canonical English: concrete state as researched

At the time of this research, the Canonical English website reported:

```text
Version:      1.0.0
Rules:        11
Word forms:   139
Word senses:  129
Parts of speech: 13
Test cases:   52
```

Those numbers matter because they show that CE is a **real but very early project**.

Its ambition is unusually aligned with VE:

> a formal, computable, unambiguous subset of English for machine-to-human and machine-to-machine communication.

It also describes itself as a:

> domain-schema-independent API for agentic communication.

Reference: https://canonical-english.org/

These figures are time-sensitive and should be updated rather than treated as permanent project facts.

---

## AD.8 NOAH is part of the Canonical English project

The discussion initially asked whether NOAH was an independent technology that Canonical English reused.

The important conclusion was:

> NOAH appears to be Canonical English's own parser/linter toolchain, not a separate mature external language project.

The current CE site distinguishes:

### `noah`

A fast, opinionated Rust linter for natural/Canonical English.

### `noah-parser`

A best-effort semantic parser that converts English into a DRS-style logical structure and records lexical senses/referents.

### `noah-linter`

The deterministic acceptance layer that checks that the CE document records one parse, one sense, one referent, and conforms to the required style/metadata.

That separation strongly influenced VE's architecture:

```text
probabilistic parser
        ↓
candidate canonical document
        ↓
deterministic checker
        ↓
accepted meaning
```

Reference: https://canonical-english.org/

---

## AD.9 Canonical English's useful implementation ideas

The CE design incorporates several ideas that VE should preserve or evaluate:

- Rust implementation for fast deterministic checking
- Markdown/GFM as a human-readable document surface
- JSON-LD metadata and tree representation
- explicit word-sense identifiers
- stable entity identifiers
- Open English WordNet for open-class word senses
- Wikidata/Wiktionary-style identifiers for other lexical/entity references
- canonical text plus a machine-walkable semantic structure
- tight generation loops in which an LLM keeps proposing until the deterministic checker accepts

The discussion also identified **CGEL/CGELBank** for grammatical structure, **Stanza** for best-effort part-of-speech analysis, and **Markdown/markdownlint** for document structure and checking. These are component leads that can be evaluated separately if NOAH source remains unavailable. Their actual integration, licensing, and suitability require source inspection; the unavailable repository was not audited.

The site describes two equivalent serialization ideas:

```text
ce-linear
ce-tree
```

with human-oriented and machine-oriented representations.

This is very close to our proposed:

```text
Natural view
Semantic view
```

and is one reason collaboration with CE remains attractive.

---

## AD.10 CE source-code availability is a project risk, not a conceptual rejection

During the discussion, the repository linked from the Canonical English site could not be accessed at the expected GitHub location. The reported locator was `MichaelCurrie/canonical-english`, including a link to `FORMAT.md`, and it returned 404 at that time. The site was described as claiming **MIT-0** licensing and a layout containing `canon/`, `src/`, and `docs/`.

These are historical investigation leads, not confirmed current availability, license terms, or inspected source layout. Verify them against the repository obtained before planning a fork.

That should be treated as a practical due-diligence item:

```text
Before committing to a fork:
1. contact the maintainer
2. obtain current source
3. confirm license
4. inspect parser/linter architecture
5. evaluate contribution model
```

It is not, by itself, a reason to reject CE's design.

The project roadmap already includes this as the first collaboration decision gate.

---

## AD.11 Why TLA+ is relevant but not a replacement for Lean

TLA+ was discussed because it handles system behavior over time naturally.

Its strengths include:

- state transitions
- temporal properties
- safety
- liveness
- distributed/concurrent-system specifications

A property such as:

> Every received request is eventually answered.

is native to temporal reasoning.

TLA+ is therefore useful as:

- a semantic inspiration
- a possible backend for a system-behavior fragment
- a model-checking target

But it does not replace Lean for proving VE's own parser/semantic metatheory.

The distinction is roughly:

```text
TLA+:
describe and analyze behaviors over time

Lean:
prove general mathematical properties about the language and transformations
```

---

## AD.12 The final Rust decision

Three implementation-verification options were considered:

### Option 1 — independent Lean specification

Write the semantics in Lean and separately write Rust.

Good, but does not prove that the Rust implementation matches the Lean specification.

### Option 2 — prove the actual Rust core against Lean

Use a tool such as Aeneas to translate a verification-friendly Rust subset into Lean and prove correspondence.

This became the preferred source-level verification route.

### Option 3 — generate the executable from verified code

Potentially powerful, but less attractive initially because it can constrain ordinary production engineering and integration.

The practical recommendation became:

> **Production Rust + a small verification-friendly trusted Rust core + Aeneas→Lean proofs.**

Then, if necessary:

> **compile that restricted core through a verified Rust compiler path such as RustCompCert.**

---

## AD.13 Full verified Rust versus a verified VE Rust subset

A major distinction from the discussion:

### Verifying all of modern Rust

This is an enormous formal-semantics/compiler project.

Difficult features include things such as:

- advanced traits/polymorphism
- closures
- concurrency
- unsafe Rust
- pointer/provenance semantics
- drop behavior
- layout
- advanced borrowing
- compiler optimizations

Even extremely capable coding agents do not make the semantic design and correctness obligations disappear.

### Verifying the subset VE needs

This is much more realistic.

The VE trusted core mainly needs:

```text
tree processing
parsing
validation
canonicalization
serialization
deterministic transformations
```

Therefore a deliberately restricted shared Rust subset can be sufficient.

That is why the common-subset strategy is important.

---

## AD.14 Aeneas's currently relevant limits

Aeneas targets safe sequential Rust and currently documents limitations including areas such as:

- nested loops
- function pointers/closures
- some forms of type parametricity
- nested borrows in signatures
- interior mutability
- concurrent execution

These limitations reinforce the architectural decision to keep the trusted core:

- small
- sequential
- deterministic
- structurally simple

while allowing the outer application to use unrestricted Rust.

Reference: https://aeneasverif.github.io/aeneas/

---

## AD.15 RustCompCert's precise role

RustCompCert is research work on an end-to-end verified compiler for a **sequential Rust subset**.

Its importance is that it aims to preserve source semantics down to assembly while also incorporating verified memory-safety/borrow-checking reasoning for its supported source language.

That makes the long-term chain plausible:

```text
VE specification
      ↑
Lean proof
      ↑
restricted Rust trusted core
      ↓
RustCompCert
      ↓
assembly
```

The key caution is that it is a research-stage restricted compiler, not a drop-in verified replacement for the entire Rust ecosystem.

The discussion reported a further trust boundary: the **Rust source parser was unverified**, with the verified compiler chain starting at the Rustlight representation. This is distinct from VE's own English parser. A complete argument from the checked Rust source to assembly must connect that source to the compiler's actual input. Candidate approaches were a small verified restricted parser, separate parser verification, or direct generation of a Rustlight AST. Direct AST generation still requires establishing its correspondence to the core whose behavior was proved; it does not automatically close the gap. Re-evaluate this boundary against the selected toolchain version.

Reference: https://arxiv.org/abs/2602.07455

---

## AD.16 Why C + CompCert remains a serious fallback

C was not rejected because it is slow; both C and Rust can be extremely fast.

C's strongest advantage is the maturity of the verified-compilation ecosystem:

```text
C
↓
CompCert
↓
verified semantics-preserving assembly
```

Frama-C and related systems also provide mature source-verification workflows.

The reason Rust remains preferred is that its ownership and type system eliminate or reduce many memory-safety proof obligations before theorem proving begins.

Thus:

```text
Best overall engineering + verification tradeoff:
Rust

Best mature verified-compiler story today:
C + CompCert

Long-term desired combination:
safe restricted Rust + Lean proof + verified Rust compilation
```

---

## AD.17 Recent formal-math results support the project's timing

**Discussion-time snapshot: September 2026.** The chat cited the following reports as evidence that frontier AI systems could generate or formalize large Lean developments. These examples are preserved as research leads from that discussion; this source-coverage audit did not independently re-verify the reports. Recheck them before using them to set delivery estimates, as required by Appendix L.3.

Two examples discussed were:

### Anthropic — Fermat's Last Theorem formalization

Anthropic reported a largely autonomous multi-agent effort that produced a complete Lean-checked formalization of Fermat's Last Theorem.

Reference:
https://www.anthropic.com/research/formalizing-fermats-last-theorem

### OpenAI — research mathematics with Lean certificates

OpenAI reported mathematical research results accompanied by Lean certificates, and separately released a Navier–Stokes result with a Lean formalization.

References:

- https://openai.com/index/ten-advances-in-mathematics/
- https://openai.com/index/navier-stokes-solution/

These examples do **not** eliminate the need for language semantics.

They strengthen the assumption that:

> generating large amounts of Lean and proof scaffolding is increasingly automatable.

Therefore VE can focus human effort on semantic design.

---

## AD.18 Formalizing existing work should never silently "repair" it

An important principle from the physics-paper discussion deserves explicit repetition:

> When a paper cannot be formalized without adding an assumption, VE should report the missing assumption rather than quietly inserting it.

For example:

```text
Original:
"We may neglect the second-order term."

Formalization status:
INCOMPLETE

Missing information:
- relative to what quantity?
- over what parameter range?
- under what error bound?
- under what approximation regime?
```

This same rule applies to:

- legal texts
- policies
- constitutions
- requirements
- mathematical arguments

Failure to obtain a unique formalization is itself a valuable result.

---

## AD.19 U.S. Constitution use case: text and doctrine must remain separate

The constitutional use case is not simply:

```text
Constitution → one final formula
```

It should instead preserve layers:

```text
constitutional text
       ↓
literal/formalized text layer
       ↓
interpretive doctrines
       ↓
precedents
       ↓
tests/exceptions
       ↓
application to facts
```

Supreme Court rulings should carry provenance and dates.

The formal system should be able to distinguish:

- text-derived claims
- precedent-derived rules
- interpretive choices
- unresolved disputes
- rules that were later narrowed or overruled

This is why doctrine needs its own versioned graph.

---

## AD.20 Claude/AI constitutions require "spirit" as well as explicit rules

The discussion of Anthropic's Claude Constitution highlighted a difficult class of formalization problem.

Some constitutions deliberately include:

- explicit rules
- priorities
- broad values
- contextual standards
- instructions to preserve the "spirit" rather than mechanically optimize literal rules

VE should not flatten all of these into:

```text
if X then Y
```

The semantic layer should be able to distinguish:

```text
hard constraint
default
priority
value
standard
exception
interpretive principle
```

This use case is one of the clearest reasons to include defeasible and deontic semantics.

---

## AD.21 Naming decision recovered from the discussion

`C++` should not be used as the public name because it conflicts overwhelmingly with the C++ programming language.

`CE++` can remain an internal shorthand.

Current naming preference:

```text
If collaborating directly with Canonical English:
Canonical English Verified (CEV)

If independent:
Verifiable English (VE)
```

Other names discussed:

- Formal English
- Exact English
- Semantic English
- Proof English

---

# Appendix AE — Conversation Topic Coverage Checklist

The following checklist maps the major questions from the brainstorming to where they are now represented in this memo.

| Discussion topic | Covered in |
|---|---|
| Can English statements be represented in Lean? | §§2–3, 9, 14, Appendix M |
| Why autoformalization is hard | Appendix F.1 |
| Generate candidates and verify them | Appendix F.3 |
| Need for a better human-spoken formal language | §§2–4 |
| Lojban vs ACE vs English | §5, Appendix J, Appendix AD |
| Lojban history and source languages | Appendix J.1, AD.5 |
| ACE example and formal quantification | §§5.3, 21, AD.6 |
| ACE's limited tense/aspect | §§13.3–13.4, AD.1 |
| Why ACE was historically narrow | Appendix G |
| Software-specification origin/use | Appendix G.1 |
| ACE open-source architecture | §5.3, Appendix G.3, AD.4 |
| Machine-verifying ACE semantics | §§9, 11, Appendix G.4 |
| Coq / Isabelle / Lean | Appendix A.7–A.9 |
| TLA+ | Appendix A.6, AD.11 |
| Indirect temporal encoding in ACE | AD.2 |
| Search for an existing "ACE++" | §5–7, Appendix A |
| PENG Light / Event Calculus | §5.4 |
| FRET / FRETish | §5.5 |
| CLCE | Appendix A.2 |
| ForTheL / Naproche | Appendix A.3 |
| Verbose Lean | Appendix A.4 |
| Visored | Appendix A.5 |
| GF / ACE-in-GF | Appendix A.10 |
| Canonical English | §§6–7, Appendix J.3, AD.7–AD.10 |
| NOAH parser/linter | §7, AD.8–AD.9 |
| Human↔agent and agent↔agent communication | §§1, 6, Appendix K.9 |
| Whether to fork CE or start fresh | §§19, 25 |
| Lean's role versus Rust's role | §§9–11 |
| "100% accuracy" definition | §12, Appendix O |
| Rust verification options | §11, AD.12 |
| Aeneas | Appendix B.1, AD.14 |
| hax | Appendix B.2 |
| Kani | Appendix B.3 |
| Verus | Appendix B.4 |
| Rust vs C | Appendix C |
| CompCert | Appendix C.3 |
| RustCompCert / Rustlight | Appendix C.4, E, AD.15 |
| Common Aeneas/RustCompCert subset | Appendix E |
| Full verified Rust compiler difficulty | AD.13 |
| Performance-critical execution | §§10–11, Appendix R.6 |
| Math papers / proof front end to Lean | §14, Appendix M |
| Recent AI-generated Lean formalization evidence | Appendix L, AD.17 |
| Physics/scientific papers | §15, Appendix H |
| Authors write directly vs retrospective formalization | §15 |
| Hidden assumptions and ambiguity audits | §15, Appendix K.6, AD.18 |
| Logical vs mathematical vs empirical verification | Appendix H |
| U.S. Constitution | §16, AD.19 |
| Supreme Court precedent/versioned doctrine | §16, AD.19 |
| Claude/AI constitutions | §17, Appendix N, AD.20 |
| Meaning of "versioned" | §16, Appendix P |
| Meaning of "canonical" | §4 |
| Naming VE / CEV / CE++ | §24, AD.21 |
| Security for agent communication | Appendix U |
| Language version governance | Appendix P |
| Conformance suite | Appendix Q |
| Benchmarks | Appendix R |
| Extension mechanism | Appendix S |
| Semantic equivalence vs canonical identity | Appendix T |
| Error/ambiguity taxonomy | Appendix V |
| Provenance/evidence graph | Appendix W |
| Interoperability | Appendix X |
| Authoring UX and clarification | Appendix Y |
| Governance/open-source strategy | Appendices Z–AA |
| Recommended concrete roadmap | §§20–21 |
| Recommended current architecture | §§8, 25–27 |

Additional details recovered during source review:

| Discussion detail | Covered in |
|---|---|
| Formal equivalence-oracle circularity and candidate-search limits | Appendix F.1, F.3 |
| ACE lexical/background-axiom caveats and formal compatibility prerequisite | §9; Appendix AD.3, AD.6 |
| Pronoun-resolution proof obligation; limits of naturalness/completeness claims | Appendix O |
| PENG bidirectional grammar; ACE-in-GF semantic boundary; TLC/TLAPS | §5.4; Appendix A.6, A.10 |
| ACE-first technical milestone and later CE collaboration preference | §19, Path 6 |
| CE component, repository, license, and source-layout leads | Appendix AD.9–AD.10 |
| Rustlight feature snapshot, common-subset validation, source-parser trust boundary | §11; §20, Phase 5; Appendix E.1–E.2, AD.15 |
| Open constitutional standards, interpretive methods, and precedent-change queries | §16 |

This checklist should be updated whenever major new design decisions are added.

---

# Appendix AF — Final Completeness Note

The September 20, 2026 review covered the full brainstorming chat and incorporated the supported additions and corrections into the relevant sections of this memo.

Repeated exchanges and redundant examples are consolidated. Coverage of a discussion claim does not establish that an external project claim is current or correct; the historical research notes remain subject to verification before implementation.

The source artifacts are:

- [Chat-Formalize English In Lean.md](<archive/sources/Chat-Formalize English In Lean.md>): full chronological conversation, including answers and research links.
- [Prompts-formal_language_user_prompts.md](archive/sources/Prompts-formal_language_user_prompts.md): separate chronological archive of the user's prompts.
- `architecture-and-design.md`: consolidated research and design record.

If a future decision materially changes the project, both the decision and its rationale should be added to this memo rather than relying on chat history alone.
