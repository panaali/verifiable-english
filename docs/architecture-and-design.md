# Verifiable English: Architecture and Design

**Status:** First draft. Implementation, proofs, and usability results are pending.

Verifiable English (VE) is an English-like language with precise, machine-checkable semantics for humans and AI agents. Its goal is to support **AI alignment and scalable oversight**, especially debate between agents before a human or weaker model judge.

The research hypothesis is that VE helps a limited supervisor detect and correct changes to an agent's claims, requirements, or assumptions, while a checker verifies deductions against those exact meanings. A formal proof cannot establish that the selected specification captures human intent. The human inspection step is therefore part of the experiment.

The [language specification](spec/v0-language.md) defines claims, the [debate protocol](spec/debate-protocol.md) defines argument checking, the [verification contract](spec/verification-contract.md) defines guarantees, and the [roadmap](roadmap.md) defines experiments and acceptance criteria.

## Research target and evidence

The first target is **meaning changes during decomposition and rebuttal**: a debater weakens a requirement, drops a condition, changes a quantifier, or uses one label for different predicates in separate branches. We test both whether people approve a wrong initial formalization and whether the protocol preserves meanings after confirmation.

| Research | Finding and implication for VE |
|---|---|
| [Buhl, Pfau, Hilton and Irving: alignment safety case, §4.4.2](https://arxiv.org/html/2505.03989#S4.SS4.SSS2) | D5.5 identifies inconsistent definitions across branches as a possible failure of judging only leaves. This is a one-sentence remark in a 2025 paper, not an analysis. It says cross-examination avoids the failure and that prover-estimator debate does not. This motivates a controlled attack family and a cross-examination baseline; it is not an empirical result for VE. |
| [Brown-Cohen et al.: prover-estimator debate, §8 of v2](https://arxiv.org/html/2506.13609#S8) | First posted June 2025. The July 2026 revision (v2) adds, as “an optimistic hope” in its open-problems discussion, that debaters could produce Lean proofs for mathematical subclaims and use debate for fuzzier ones. v1 has no such passage and a different §8. This is a speculative aside, not a design or an endorsement. Its guarantees have stated efficiency, stability, and equilibrium conditions. Adding proofs to debate alone is not VE's distinctive contribution, and VE does not automatically inherit these guarantees. |
| [Brown-Cohen et al.: Debate is efficient with your time](https://arxiv.org/html/2602.08630) | The 2026 query-complexity results assume unbounded debaters. They motivate measuring judge effort, but do not establish affordable certificate generation or faithful human interpretation of formal statements. |
| [Chen et al.: When and Why Does Multi-Agent Debate Fail and Does It Really Underperform?, Figure 4 of v2](https://arxiv.org/pdf/2510.20963#page=6) | A preprint from October 2025, revised July 2026. A schematic, elided figure shows a judge accepting a reinterpretation of “include [integers, numbers with 2 decimal places]” as either category. It is an illustration, not a measured rate of judge behavior. Its ColMAD protocol improves error detection mainly relative to weak competitive-debate baselines; simple voting is close behind in the paper's own tables. The underlying [ReaLMistake benchmark](https://github.com/psunlpgroup/ReaLMistake) supplies expert error annotations, but its tasks are math word problems, fact verification against Wikipedia text, and answerability classification, which v0 mostly cannot express. Its data is CC BY-SA 4.0, and its authors ask that examples not be published online in plain text. |
| [FormalJudge](https://arxiv.org/html/2602.11136) | This 2026 preprint already combines LLM-generated specifications with Dafny/Z3 checking. Its reported residual errors include intent decomposition and fact extraction; parts of its evaluation use model-generated reference labels. VE must test these boundaries with independently established labels. |
| [Gordon and Matskevich: Trustworthy Formal Natural Language Specifications](https://arxiv.org/abs/2310.03885) | This 2023 paper implements an extensible formal subset of English inside Lean using categorial grammar, with certificates showing how each word was interpreted. It is the closest prior work on the language itself. VE must state what it adds, which would have to be the oversight protocol and its evaluation. The English-to-Lean idea is already theirs. |
| [Kuhn: The Understandability of OWL Statements in Controlled English](https://www.semantic-web-journal.net/content/understandability-owl-statements-controlled-english) | With 64 participants, ACE was understood better and faster than a simplified Manchester OWL syntax. This supports a natural controlled-English surface on small, non-adversarial unary and binary statements. It does not cover long arguments or adversarial wording, and ACE's surface is far more natural than v0's. |
| [Fuchs: Understanding Texts in Attempto Controlled English](https://attempto.ifi.uzh.ch/site/pubs/papers/cnl2018main_fuchs.pdf) | ACE's deterministic interpretation rules can differ from a reader's ordinary English reading. Text that looks like English invites English intuitions. This is a direct risk to VE's hypothesis, and it grows as the surface becomes more natural. |
| [Greenman et al.: Little Tricky Logic](https://arxiv.org/abs/2211.01677) | Even formal-methods researchers systematically misread LTL formulas and their English glosses. Human inspection of formal claims is error-prone for experts, not only for novices. |
| Debate experiments: [Khan et al.](https://arxiv.org/abs/2402.06782), [Kenton et al.](https://arxiv.org/abs/2407.04622), [Michael et al.](https://arxiv.org/abs/2311.08702), [Parrish et al.](https://arxiv.org/abs/2210.10860) | Debate helps weak judges mainly when debaters hold information the judge lacks; gains are small or absent otherwise, and short debates did not help humans. VE's tasks give the judge all the information, which is the regime where debate has helped least. |
| [Barnes and Christiano: obfuscated arguments](https://www.alignmentforum.org/posts/PJLABqQ962hZEqhdB/debate-update-obfuscated-arguments-problem) | A valid-looking decomposition can hide a flaw that neither debater can locate efficiently. Formal checking removes deduction flaws but leaves flaws hidden in the premises. |

A literature search also surfaced [Elasky et al. 2026](https://arxiv.org/abs/2605.27483), whose abstract reports that on programmatically verifiable tasks a single critique recovers most of debate's benefit. We have not read this paper. If the abstract's claim holds, a critique-only condition belongs among the comparisons. The search found no controlled study of whether people detect wrong formal specifications from natural-language renderings, and no work combining a controlled language with debate. Both may be real gaps, but the search was brief.

These sources support the choice of failure modes and baselines. They do not demonstrate that VE improves oversight. The contribution to establish is reliable human inspection plus mechanically preserved meaning, compared with an equally capable structured formal interface.

## Expected benefits for debate and scalable oversight

If VE succeeds, a limited supervisor should be able to evaluate more complex AI work accurately within the same review budget. The proposed language and checker would contribute in four ways:

1. **Keep local arguments connected to the original question.** People inspect and correct the initial specification; checked deductions then preserve the confirmed meanings and explicit assumptions across submitted branches. In the [operations/security review example](spec/debate-protocol.md#worked-example), the two meanings of “reviewed” cannot be silently substituted in a certified deduction once the vocabulary separates them. If the vocabulary merges them under one vaguely described predicate, the checker certifies the substitution; see [known weaknesses](#known-weaknesses-of-the-current-design). Cross-examination already addresses this failure mode; VE tests whether mechanical enforcement makes that defense more reliable and less dependent on successful questioning and the judge's memory.
2. **Concentrate human attention on interpretation and evidence.** A checker verifies the formal deductions while the supervisor assesses the requirement and remaining premises. This could reduce the additional review effort required by longer arguments. The benefit depends on the difficulty of those premises and the cost of formalization and proof production; fewer premises alone does not establish easier oversight.
3. **Make challenges precise and conclusions reusable.** A critic can identify an exact disputed premise, unsupported inference, or countermodel. Agents investigating separate subclaims can combine certified results under the same environment while retaining their assumptions. This could reduce repeated review and errors during handoffs. Reuse must preserve artifact bindings and must not transfer confirmation or factual evidence to changed claims.
4. **Improve the feedback used to train agents.** If semantic tricks earn approval less often, training could reward them less often and favor inspectable specifications and justifications. This is a downstream hypothesis requiring training experiments; better judgments in a prompted debate do not establish more honest trained agents. Rewards must still account for faithful intent and useful answers, rather than certificate counts.

A future prover-estimator debate integration could attach uncertainty estimates to precisely identified claims and use certificates for supported formal deductions. The [PED paper](https://arxiv.org/html/2506.13609#S8) already proposes combining formal proofs with uncertain debate; VE's potential contribution is making the shared claims human-inspectable and preserving their connections. Such an integration needs its own protocol and evaluation.

The scaling outcome to establish is sustained oversight accuracy as argument complexity and the agent–judge capability gap increase, at affordable total cost. The checker covers the submitted argument, and human judgment remains necessary for intent, factual evidence, omitted requirements, and value judgments. The [roadmap](roadmap.md#testing-the-expected-benefits) defines measurements for these possible benefits.

## Known weaknesses of the current design

These are the strongest objections to the v0 design found in review. Each one could defeat the research claim, and none is yet answered. They are ordered by how much they threaten the project.

1. **The ambiguity is relocated, not removed.** Predicate symbols are exact, but their meanings are fixed by free-English `description` strings and by the evidence attached to premise leaves. An equivocating debater does not need to swap predicates inside a deduction. They can declare one vague predicate and ground it differently in each branch, as the [merged-vocabulary example](spec/debate-protocol.md#the-same-attack-when-the-vocabulary-is-merged) shows. Preserving a committed formal meaning holds by construction in any typed formal language, so it is not the uncertain part. The uncertain part is whether people catch bad vocabularies and mismatched evidence, which is exactly where VE stops being formal.
2. **A checked proof may raise trust in a wrong claim.** A “proof checked” label on an argument whose flaw lives in a description or a leaf could make supervisors less likely to find it than they would be in prose. VE must be tested for this harm as well as for benefit. The roadmap's confidence measurements cover it, but it needs a dedicated attack family.
3. **The v0 surface is barely English.** `for every service x0, (if (x0 is deployed), then (x0 is reviewed)).` is first-order logic with keywords, parentheses and generated variable names. ACE renders the same claim as “Every deployed service is reviewed.” The planned comparison between VE and structured formal claims therefore differs by very little, so the expected effect of the English surface is small and a small pilot is unlikely to detect it. Replacing author-chosen binder names with `x0`, `x1` in the text shown to reviewers also removes a readability aid. Either the surface must become substantially more natural (which enlarges the parser and proof work the strict grammar was chosen to avoid), or the project should state that v0 tests formal commitments and defer the English claim.
4. **Few realistic tasks fit the fragment.** Function-free logic with unary and binary predicates and no arithmetic cannot express the numeric-format requirement in the motivating Chen et al. example, and probably excludes most of ReaLMistake. A coverage survey must come before any other investment. If coverage is near zero, the experiments would run only on tasks authored to fit VE, and that result would say little about oversight in general.
5. **Debate may have nothing to do on tasks that fit.** Where the inputs are fully formal, the checker alone decides the answer and debate is unnecessary. Where the difficulty is in empirical leaves, VE contributes nothing. VE plus debate helps only in between: long compositions whose leaves a limited judge can assess individually. The first task set has to show that this region exists and matters.
6. **The motivation is thin.** The evidence that meaning changes are an important debate failure is one theoretical note, which says cross-examination already addresses it, and one illustrative figure. How often meaning-change attacks succeed against a well-run natural-language debate with cross-examination has not been measured. That baseline needs no VE implementation and should be measured first. A low success rate would remove the reason for the project.
7. **The human judge may not be the relevant judge.** Scalable-oversight protocols increasingly use weaker models as judges. A model judge reads formal syntax as easily as English, so the English surface matters only where a human inspects the claims. The docs should state which judge VE is for. Experiments with model judges are much cheaper and can test the formal-commitment mechanism early, but they cannot test the English surface.
8. **Assurance work is scheduled ahead of the evidence that would justify it.** Parser uniqueness proofs, canonical hashing, resource envelopes and an implementation-language survey are specified in detail before there is any sign that the approach helps a judge. None of that work tells us whether people inspect VE claims more accurately. The [roadmap](roadmap.md#research-sequence) now puts cheap, disposable experiments first.

## First useful workflow

A supervisor evaluates whether an agent's submitted result meets an agreed requirement. A proposer defends the result and a critic challenges its specification, evidence, or deductions.

1. The supervisor inspects and confirms the target claim and local vocabulary, using canonical VE and explanatory examples. Initial ambiguity is resolved equally in every experimental condition.
2. Agents submit named claims and a finite dependency graph. Every claim is bound to its exact text, typed AST, and common environment.
3. Each claimed deduction must have a certificate for its stated premises and conclusion. A finite countermodel can demonstrate that a deduction does not follow.
4. The checker composes certified edges and displays the root claim with all remaining assumptions and unresolved obligations. A changed target or vocabulary requires a fresh confirmation; it cannot inherit acceptance.
5. The supervisor examines the remaining interpretation and evidence questions, then accepts, rejects, requests repair, or leaves the result unresolved. A checked conditional argument is not an automatic approval.

For example, an operations review and a security review must have distinct predicate identities. An argument connecting them needs an explicit bridge premise. The [worked debate example](spec/debate-protocol.md#worked-example) exhibits a countermodel to an attempted substitution. The [finite example](spec/v0-language.md#worked-example) shows how submitted records can satisfy or violate constraints.

The checker verifies the submitted graph, not every possible branch of a recursive debate. Its cost, certificate construction, and the supervisor's initial confirmation effort all count toward oversight cost. Finite records need independent evidence if they are used to describe an actual deployment. A required computation must not become an agent-supplied `compliant` flag.

## Language choices

| Choice | Rationale | Tradeoff or alternative |
|---|---|---|
| Many-sorted, function-free first-order formulas | Supports explicit quantifiers, relationships, equality, and shared claim meanings | Arithmetic, functions and n-ary relations may be needed by real tasks; measure coverage before choosing an extension |
| Local typed predicates, constants, and descriptions | Makes the vocabulary available without network resolution and exposes modeling assumptions | Dictionary senses and external identifiers can aid interoperability, but do not supply executable definitions or prove facts |
| Explicit variables and binder indices in the semantic AST | Makes scope and alpha-renaming precise | Pronouns and discourse reference require additional resolution rules; names are retained for diagnostics |
| Typed semantic objects, independent of runtime layout | States admissible meanings without dictating memory representation | Intrinsic dependent types and raw syntax with proved well-formedness are both viable; choose using a nested-binding proof |
| Fixed printing and binder renaming | Gives reproducible representations while preserving expression structure | Synonyms, paraphrases and logically equivalent formulas need separate equivalence rules or proofs |
| Separate model satisfaction and logical consequence | Finite evaluation checks one structure; deduction certificates establish a conclusion across all admissible structures satisfying the premises | A passing example is not an entailment proof; failing to find a countermodel does not establish validity |
| Complete finite witnesses | Makes evaluation and countermodel validation determinate | Closed-world absence applies only inside that witness. Missing empirical evidence stays unresolved; empty domains and false antecedents can cause vacuity |
| Lean certificates for deductions; direct finite evaluation for witnesses | Keeps proof search outside the trusted reasoning path and exposes the exact conclusion and assumptions | Certificate production may be expensive or fail; a solver is useful only with a checked certificate or an explicitly stated trust boundary |
| Strict ASCII syntax with explicit parentheses | Keeps the first grammar and proof target small | Exact spacing, final newlines and restricted names may hinder authoring; these are usability hypotheses, not requirements of unambiguity |
| Fixed JSON and JCS artifact encodings | Defines portable source, environment, meaning and model identities | JSON-LD requires context semantics; Markdown is a presentation wrapper, not the semantic payload |
| One relational semantic profile, two judgments | The same formula interpretation supports finite examples and conditional arguments | Temporal, probabilistic and normative operators require additional semantics; evidence metadata does not silently supply them |

The AST, environment and denotation jointly define meaning. A well-formed tree alone does not establish that the tree matches the source. A deterministic parser may select a wrong interpretation, so the specification requires independent uniqueness and correspondence obligations.

## Implementation language and proof tools

**Use Lean for reference semantics, parser/printer proofs, finite evaluation and argument certificates, with a CLI first.** Executable definitions and their proofs can share one language, avoiding an initial hand-written port and its correspondence work. Lean distinguishes kernel checking from executable compilation, so compiler and runtime behavior remain part of the trust boundary. [Lean processing pipeline](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/).

This choice is based on reducing implementation and proof boundaries. VE has no measurements establishing the fastest runtime or lowest proof-maintenance cost. Meet the task's performance envelope before adding another core; optimize algorithms first, since a language change does not remove expensive quantifier enumeration.

| Option | Where it helps | Why it is not the default v0 path |
|---|---|---|
| Rust with Aeneas/Lean | A candidate for a measured native-runtime or deployment need; safe Rust provides static memory-safety restrictions | Requires extraction, library models and correspondence to VE semantics. Memory safety alone does not prove the checker correct; unsafe dependencies and foreign calls need a trust account. [Rust reference](https://doc.rust-lang.org/reference/unsafety.html), [Aeneas](https://github.com/AeneasVerif/aeneas) |
| C with VST/Rocq and CompCert | A serious option when compiler assurance or C integration matters; VST connects source reasoning to CompCert semantics | Requires memory and undefined-behavior reasoning plus VE correspondence. CompCert's main theorem is from its C AST to assembly AST; preprocessing, elaboration, assembling/linking and runtime boundaries still matter. [VST](https://vst.cs.princeton.edu/), [CompCert](https://compcert.org/man/manual001.html) |
| Rocq with extracted OCaml | An alternative for proved functional definitions and executable extraction | Changes the proof ecosystem; extraction, target compiler and adapters still need a trust account. Compare it if proof expertise or reusable work favors it. [Rocq extraction](https://docs.rocq-prover.org/master/refman/addendum/extraction.html) |
| HOL4/CakeML | Proof-producing translation and verified compilation to machine code, including checker applications | Introduces HOL4 and another integration path without a v0 requirement for compiler assurance. Worth comparing with C for a stronger deployment guarantee. [CakeML](https://cakeml.org/) |
| Dafny or F*/Low* | Proof-oriented programming with executable-generation paths | Requires a different proof, solver and extraction account. Specialized verified toolchains have restricted scopes, not guarantees for all programs. [F*/KaRaMeL](https://github.com/FStarLang/karamel), [Dafny subset research](https://arxiv.org/abs/2512.05262) |
| Other application languages | Python, TypeScript, Go, Java, OCaml, Haskell or C++ may suit authoring and integration | No VE-specific checker correspondence or performance advantage is established for a hand-written core in these languages; choose host tooling independently |

Lean is also a natural target for a future mathematical dialect, but v0's small logic does not require dependent type theory. Rocq, Isabelle/HOL and PVS can be considered when relevant expertise or reusable formalizations favor them. The export target and metatheory implementation can be chosen independently, with a correspondence obligation between them.

If Rust is needed, evaluate Aeneas on actual binding, parsing, relation lookup and error handling. Its current README lists specific restrictions on control flow in nested loops and generic instantiation with mutable references; unsafe and concurrent verification remain ongoing work. Pin the complete toolchain and test the required constructs. [Aeneas supported subset](https://github.com/AeneasVerif/aeneas#targeted-subset-and-current-limitations).

hax's Lean backend orchestrates Charon/Aeneas, so it is an integration option rather than independent verification evidence. Verus and Kani can answer additional functional-correctness or harness questions under their own assumptions; adopt them for a named need rather than requiring every verifier in CI. Frama-C WP is another C verification option, but combining its output with a CompCert build does not itself prove agreement between their models. [hax architecture](https://hax.cryspen.com/dev/architecture/), [Verus assumptions](https://verus-lang.github.io/verus/guide/tcb.html), [Kani harnesses](https://model-checking.github.io/kani/reference/attributes.html), [Frama-C WP](https://www.frama-c.com/wp.html).

Verified compilation is outside v0. RustCompCert's restricted research pipeline includes an unverified Rust-to-Rustlight parser; its correspondence with an Aeneas model must be established separately. Do not impose a common Rust subset until the selected tools demonstrably support the required implementation. [RustCompCert v1](https://arxiv.org/html/2602.07455v1).

## Reuse and interoperability

| Resource | Useful contribution | Boundary for VE |
|---|---|---|
| [ACE/APE](https://github.com/Attempto/APE) | Concrete controlled-English parsing and DRS/FOL outputs | Reuse is attractive for an ACE import; correspondence to VE's specified semantics needs its own evidence, and APE cannot serve as its correctness oracle |
| [Canonical English](https://canonical-english.org/) | Agent-oriented communication and separation of proposals from deterministic checking | A single-author project begun in August 2026 with no paper. Its stated ideal is not constructively defined. The site states CC0 and MIT-0 terms, but the linked source repository returned 404 on September 20, 2026, so there is currently no code to adopt |
| Kowalski's Logical English and Schwitter's PENG (references to be located) | Controlled-English surfaces for logic programs and specifications | Compare their surfaces and comprehension evidence before designing a more natural VE grammar |
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
committed target + explicit claim dependencies
             |
deduction certificates / finite countermodels
             v
conditional result + remaining assumptions
             |
   supervisor's evidence and intent judgment
```

An untrusted frontend may propose text, an AST or a proof. The checking path must establish correspondence to the exact submitted inputs. LLM agreement, successful type checking and proof of a producer-selected theorem cannot establish fidelity to an unstated human intention. Manual authoring remains available; candidate generation and clarification have bounded budgets.

The interface displays canonical text from the checker artifact. Display fidelity, JSON decoding, model validation, compiler behavior and IO remain explicit trust assumptions unless separately checked. A small semantic core does not automatically verify its surrounding application.

Language acceptance, canonical form, human confirmation, finite evaluation, inference status and proof checking have separate [status fields](spec/verification-contract.md#status-and-evidence-contract). Deduction certification requires a checked proof of the expected implication; finite evaluation may run without a per-result proof. Authentication and action authorization belong to the host application.

Initial formalization errors, misleading vocabulary descriptions, false observations, and omitted requirements remain possible. A proof can also follow from inconsistent or overly strong assumptions. Expose those assumptions and test these attacks; do not score agents by theorem count. Canonical wording removes some surface variation but cannot eliminate covert communication through the choice or ordering of claims. VE does not establish truthful incentives, prevent collusion, or solve the general obfuscated-arguments problem.

## Extension boundary and broader goals

v0 admits `ve.core@0` with `relational-fol@0`. Vocabulary entries add signatures and descriptions, not executable definitions or inference rules. The argument layer uses this same semantics. Unknown profiles and unsupported constructs are errors.

A future profile must specify its AST, typing, model, interpretation, supported combinations, parser/printer rules, resource behavior and preservation of the existing fragment. For example, “Alice believes every request must eventually be answered” needs explicit interaction between belief, obligation and time. Installing three modules does not establish that interaction. Belief must not silently entail truth, and obligations must not silently become facts.

Longer-term applications include mathematical statements and proofs, scientific assumptions and derivations, temporal requirements, and legal or agent-policy reasoning. A mathematical dialect can target a bounded Lean fragment and later provide explicit escape hatches. Scientific work must distinguish assumptions, derivations and empirical evidence. Legal and policy models must expose interpretations, exceptions, priorities and their provenance. Vague or disputed standards require declared context rather than invented precision.

These applications need their own semantics and acceptance criteria. v0 VE text does not accept embedded Lean programs, arbitrary imports or executable plugins. The local prototype's isolated proof-production path is separate from its checking interface. Signed transport, probabilistic evidence aggregation and additional backends require concrete workflows and contracts.

## Evidence needed

The [roadmap](roadmap.md) tests five questions:

- Can representative oversight claims be expressed without hiding the difficult checks in supplied facts?
- Can people detect and repair wrong initial formalizations and meaning changes under adversarial pressure?
- Does VE improve on cross-examination, ColMAD, and structured formal claims at comparable effort and useful-answer rates?
- Can parsing, rendering, certificate binding and argument composition meet the formal contracts?
- Is the total cost of authoring, proof production, checking and supervision acceptable as arguments grow?

Start usability work with an experimental reference slice while completing formal proofs. Measure AI assistance through checked artifacts, human review effort, repair work and compute cost. External model demonstrations do not establish VE's development cost.

Tool capabilities are supported by the linked primary sources, consulted September 20, 2026. VE-specific performance, usability and proof effort remain unmeasured. Exact dependency versions and applicable licenses must be established before adoption.
