# Verifiable English: the vision (2026-09-25)

Status: the goal of record for the language track. Restated from the orchestrator's draft after the two vision
reviews (GPT-6 Astra, Claude Fable 5.1), which converge on most points; their disagreements are in section 6.
[PLAN-EXPAND2.md](PLAN-EXPAND2.md) executes stages 1 and 2; ROADMAP.md holds status.

## 1. The goal

Any document that someone is held to (a company's process or policy, a law, a contract, a specification, a
scientific paper, a news report, a textbook) can be written in Verifiable English (VE): a subset of English with
one reading per sentence, checked mechanically by a small Lean-proved checker, with Python, Rust and Lean agreeing.
Anyone who reads English can read a VE document and approve a paraphrase of it. Authors write ordinary English, an
assistant proposes the VE, and the author approves.

The reviews qualify this in two ways, both adopted. First, "every sentence formal" is the wrong target. The target
is a **checked spine**: everything the document commits to (definitions, claims, norms, quantities, evidence) is in
VE and checked; exposition, examples, motivation and figurative prose are spanned and labelled, never checked and
never silently dropped. Second, "anyone who knows English" is two claims. Reading and approving must work for any
English speaker. Writing strict VE unassisted is not required, and the evidence (P5: 0/12 one-shot; P3: faithful
only after repair) says it is not achievable. Writing goes through the assistant.

## 2. What a VE document is

Every source span belongs to exactly one unit and the units partition the source: 100% span accounting (the earlier
90% target contradicted "nothing silently dropped"). A unit carries three independent descriptions in place of the
flat label "judgement call":

- **Content kind**: assertion, definition, norm (obligation, prohibition, permission, with exceptions), attributed
  statement, hedge, question, instruction, example, exposition, analogy, explanation, meta. Kinds nest: "Alice
  believes Bob probably caused X" is an attribution over a hedge over a causal claim.
- **Meaning status**: fully specified; parameterised by a declared context; constrained but open-textured; or not
  yet formalised, with a reason code.
- **Support**: assumption, proof (certificate), observation, reproducible calculation, statistical assessment,
  testimony, adapter output, or unsupported.

**Open-textured terms** ("reasonable precautions", "inappropriately harmful") are legitimate vocabulary, not
failures. Each is a named open predicate with a schema: who decides it (court, panel, named role), stated
necessary conditions, sufficient conditions where known, pinned examples and precedents (VE facts by meaning id),
jurisdiction and version. The logic around the term is exact; applying the term is a recorded decision. In the
pilots the number of such terms per document is small (under ten).

The **headline number** of a document is its residual: open terms, named assumptions, bridge leaves (accepting an
attributed statement as true) and unresolved readings (section 3). There is no universal percentage target;
coverage tables are per-document measurements.

The checker certifies structure (consistency, entailment, conflict-freeness of norms, vacuity, coherence of
probabilities); it never certifies the world. First-order entailment is undecidable, so every check has an honest
UNKNOWN. A small checker limits automatic answers, not expressiveness: untrusted provers supply certificates.

## 3. Two ways a VE document comes to exist: the lead's proposal and our verdict

The lead proposed two modes. **Authoring**: the author writes in VE with the assistant and is responsible for
choosing the reading that says what they meant. **Translation**: we render someone else's text; we may not pick
the reading we think the author intended; every sentence with more than one plausible reading keeps all admissible
readings, stated factually ("could mean A or B"); a translator may add probabilities over readings only as
separate, attributed, removable annotations that never collapse the set.

**Verdict: adopted, generalised in three ways.**

1. **One construct, two closure policies.** A *reading set* attaches to one source span a list of candidate VE
   readings, each with provenance (who admitted it, why, and a checked model that distinguishes it from the
   others). It is explicitly "readings considered so far": versioned and extensible by anyone, including a
   challenger, because "all readings" of an English sentence is not a well-defined total. In authoring the set
   collapses to one reading by the author's signature and the rejected readings stay recorded; that is where "one
   reading" becomes visible to the approver. In translation nobody present may collapse it. The assistant's
   candidate-plus-distinguishing-model machinery already produces reading sets.
2. **Mode is per unit, not per document.** A document can mix spans its author confirms and spans nobody can
   confirm. A *narrowing* ("we read clause 3 as A because clause 4 says ...") is a new, attributed, citable unit by
   whoever narrows (an adopter, a court, a translator). It never edits the source's set, and every result obtained
   under it says so. This is Astra's "check under all admitted interpretations or explicitly identify the chosen one".
3. **Checking is per reading, without enumeration where that is sound.** For a conclusion that depends on
   ambiguous units the report is one of: holds under **all** readings; under **some** (a certificate for a named
   choice plus a countermodel for another); under **none**; or **unknown**. When every reading is an assertion
   over the same background (no reading is a norm, a definition or anything that changes the background
   premises), "all" is one certificate from the conjunction of per-unit disjunctions, which is equivalent to
   holding under every combination, and "none" is one finite model satisfying every reading and refuting the
   conclusion; no combination is enumerated. For any other kind of reading the complete choices are enumerated
   (up to 64), each choice is elaborated separately, and beyond that the verdict is unknown (converged Astra +
   Fable change, 2026-09-25, `debates/expand2-v2/`, item 7). A choice is global per unit, so one sentence is never
   read two ways inside one argument, and a cited result carries its choices, so citing it under incompatible
   choices is rejected. Adding a reading can only weaken an "all" verdict, so the summary cannot be gamed by
   omission without a visible gap in the set.

Translator probabilities over readings are claims about an author's intent, not evidence about the world; they sit
outside the evidence layer and outside every check. VE sentences still have exactly one reading each. The ambiguity
lives in the source, and the VE document says so.

## 4. Stages (revised)

| Stage | Content | When |
|---|---|---|
| 0 Contract and baseline | Inventory of guarantees (parse, evaluate, prove, countermodel, UNKNOWN); complete re-audit of the pilot documents including omitted material | now |
| 1a Document foundation | `ve-document@1` with 100% span accounting, content kinds including non-assertive ones, open-term schema, reading sets, versioned definitions, citations that keep every dependency, coverage dashboard, three pilots re-measured after every merge | round 2 |
| 1b Cheap language | Definitions with citation and `iff`; n-ary atoms; integers finished; dates; scaled decimals with display units (percent, money); small counting sugar | round 2 |
| 1c Norms and data | Static exception trees with Catala applicability, stratified and conflict-checked, conflict witnesses shown as situations; one default per predicate pair; attributes and strings; Cedar adapter | round 2 |
| 2 Authoring | The assistant offers every construct with paraphrase, example situation, rejected readings and a residual panel; per-construct held-out fidelity gates; witnesses de-elaborated into document terms; approval bound to meaning identity | round 2 (W8), continuing |
| 3 Evidence | Source snapshots, attribution, reproducible calculations, corrections and retractions; probability bounds only where inputs and interpretation are defensible; argument-scheme units for analogy and precedent; workflows and state changes | after round 2 |
| 4 Proofs and hardening | Unified checker stage 2 (closure, order and n-ary together); English round-trip proof once the surface stops moving; book-scale pilots | after the surface freezes |
| Research track | Richer mathematics and real arithmetic; temporal and causal semantics; defeasible "normally"; heuristic arguments; debate; calibration against resolved outcomes; proof-carrying actions; usability with humans | measured research |

## 5. Achievable versus research

Achievable with current methods: the checked spine with 100% accounting; typed kinds; the open-term schema;
definitions and citation; n-ary atoms; narrow norms; integers, dates and scaled decimals; attribution; reading sets;
provenance and reproducible calculations; an assistant with measured fidelity. Research: general heuristic
verification and resistance to obfuscation (ARC's open problem); debate certifying the absence of considerations;
calibration without labels; defeasible and cross-attitude inference; causal semantics; real analysis; and the
empirical claim that any English speaker uses the tool well (human studies are deferred).

## 6. Where the reviewers disagree, and the decision

- **"Elaborate, do not extend the logic."** Fable: a standing rule; the checker grows only by proved conservative
  extensions; defeasible weighing, attitudes and reals stay outside or in sibling checkers. Astra: an excellent
  default, not permanent; mathematics may warrant bounded proof imports, and causal or modal inference needs real
  semantics. Decision: the rule binds this round and the next. An extension is allowed only as a proved
  conservative extension with model validity; sibling checkers (units) are allowed; revisit when a pilot needs an
  inference that elaboration cannot give.
- **Decimals and units.** Astra: bring them forward. Fable: reals stay outside. Decision: scaled decimals as
  integers with a display unit now; genuine reals stay research.
- **Coverage numbers.** Astra: no defensible universal percentage. Fable: rough per-document fractions with the
  spine as the goal. Decision: residual counts are the headline; percentages are per-document measurements.
- **Events and workflows.** Astra adds events, state changes, deadlines and fulfilment for company procedures.
  Decision: time-indexed relations, deadlines and violation predicates in round 2; workflows in stage 3.

## Converged rule: elaborate by default, extend only through verified profiles (Astra + Fable, 2026-09-25)

Adopted verbatim from the two-round convergence debate (`~/code/manage-agents/debates/elaborate-vs-extend/`); supersedes the earlier disagreement note on this point.

> **Elaborate by default; extend only through declared, verified profiles.**
> 1. Default: elaborate into an existing profile with a Lean faithfulness theorem against independently specified semantics, including the model correspondence behind proof and countermodel results.
> 2. Meaning freeze: existing routes, identities, canonical bytes, certificates and theorem statements never change. Every extension is a new versioned profile on a new route, or a sibling checker.
> 3. Trigger: a recorded instance from a committed document whose intended inference has no faithful elaboration into an existing profile, or one the prover cannot use within budget. The failed attempt is recorded with the profile.
> 4. Obligations, in Lean, audited under the existing axiom allowlist: explicit semantics; conservativity (old structures embed, denotations preserved, no new consequences among old claims); certificate soundness at every universe without a soundness premise; executable model validity and countermodel soundness, so NO and UNKNOWN survive; `CertificateSound`; gate theorems for old routes and combinations; verified elaboration and composition bridges; exact statement, profile and dependency binding; statement review of `Intended`; Python/Rust/Lean conformance, which never substitutes for proofs; a trust-cost line in ROADMAP.
> 5. Every judgment kind is context-free. Non-monotone systems enter only as sealed content whose conclusions are computed under a distinct kind and used as conditional premises.
> 6. Proof imports: cited Lean lemmas as labelled premises with statement review, pinned versions and axiom audit. Not a checker change.
> 7. Sibling results enter deductions only through a verified bridge keeping assumptions and kind; otherwise they are external support.
> 8. Outside certification: empirical truth, interpretation choices, open-term adjudication, unsupported causal assumptions, unconstrained weighing. Their formalized conditional consequences may be checked.
> 9. Admissibility is never decided by topic. A status table beside the rule lists what is not yet admitted and the criterion it fails. A profile no pilot uses at a stage boundary leaves `ve assist` and is kept for identity.

## Lead principle: zero-training English (2026-09-26)

The whole benefit of VE is that it is English. Any non-expert should be able to read **and write** it with zero tutorial or training. VE should be as close to regular English as possible while preserving its properties (one reading per sentence, mechanical checking, a small verified checker). Consequences:
- Readable text carries no notation: no `@`, brackets, operators or variable letters where avoidable.
- What you can read is what you can write: the writable language and the natural view converge.
- When a sentence is ambiguous, the IDE resolves it in English: it shows each competing reading as a plain-English paraphrase with a concrete example situation, and suggests unambiguous rewrites the author can pick. Nobody is asked to read logic.
- The one-reading guarantee stays mandatory and is checked automatically; readability never overrides it.
This refines the earlier "writing goes through the assistant" split: the assistant is how ambiguity gets resolved, not a separate language.

## Synonyms and varied wording (2026-09-26)

Writers vary words for readability ("staff", "employees", "personnel"); VE allows it. A document glossary declares synonyms once ("In this document, staff, employees and personnel mean the same thing"); each is an alias definition (W3, conservative, Lean-proved) so the checker treats them as one concept, while the display keeps the author's word choice (meaning identity is separate from wording). Authoring mode: the IDE asks in plain English when a new word appears ("Does 'personnel' mean the same as 'staff' here?") and adds the alias on confirmation. Translation mode: an explicit statement in the source (a definition, "employees (staff)") is recorded with its citation; synonymy that is only "clear from context" is an interpretation, kept as a reading set (same / different) with the translator's cited reason, and the checker reports whether any conclusion depends on it.


## Self-reference boundary (2026-09-28)

"This document" is allowed as a name (scope, version, supersedes). A document may state that OTHER documents, identified by fingerprint, were checked, and that claim can be confirmed by re-running the check. A document may never assert its own validity or truth: validity lives in the external report (Tarski-style layering), which also rules out liar-type paradoxes such as "This document is not valid".
