# DISCOURSE and CROSS-REFERENCE: plan

**Proposed, 2026-09-28; baseline `df874bd954aa`. Revised 2026-09-28 with the converged Astra + Fable edits (`manage-agents/debates/design-discourse/`, round 2, edits J1 to J8); the item-1 statement spec is [discourse.md](discourse.md).** Four-page design body below; no implementation or coverage gain claimed. Follows [VISION](../../VISION.md), [North Star][north], [W1](norms.md), [W2](document.md), [W3][w3] and the [natural view](../natural-view.md).

**Summary (104 words).** Resolve references into explicit, typed targets before checking; preserve the existing logic and its identities. Named antecedents, qualified descriptions, definitions and document anchors receive versioned bindings with source provenance. Each accepted VE sentence has one closed reading; unresolved English produces an IDE question or retained translation readings. Existential witnesses never silently become global names, and links never confer truth or authority. Descriptions expose existence, uniqueness and contextual restrictions. Lean must verify resolution, elaboration, compatible choices and model correspondence. Start with names and navigation, then descriptions and correlated readings, followed by W1/W3 integration. Measure faithful source-byte gains separately from reference resolution, labels and unresolved judgments.

## Page 1 — Meaning and scope

**Contract.** Propose `ve.discourse@1`, a versioned presentation and binding manifest extending W2 through a **new document-format version, `ve-document@2`**, never extra silently accepted `ve-document@1` fields. It elaborates into existing closed formulas, W1 blocks and W3 declarations/citations. No new logical operator or checker rule. Freeze old routes, canonical bytes, meanings and certificates; retain `ve.prose@1` behavior. New semantics require the verified-profile process in VISION, including a committed failed elaboration case, conservativity, executable model validity, certificate/countermodel soundness and composition proofs.

**Explicit context.** A manifest records document/source identity; ordered section/clause anchors; mention IDs and UTF-8 spans; target type, scope and kind; environment/definition versions; reading choices; and resolution provenance. Entity targets are declared constants or local binders; other targets are predicates, source units, rule IDs or certified claims. These types cannot coerce into one another. Names and section numbers are display labels, not identities. The checker regenerates bindings from source plus manifest and rejects stale, missing, colliding, ill-typed or inaccessible targets. A reading may bind an ordered list of source spans; each span has exactly one status and is counted once. A fused reading contributes one assertion; its spans keep their historical boundaries and receive status through that group, and no fragment acquires an independent assertion. Reading sets may declare compatibility constraints; joint enumeration uses only these.

Let `Resolve(E,K,s,ρ,A)` independently specify the parses and reference assignments of sentence `s` under the declared environment `E` (vocabulary and definition versions), in the manifest's explicit context `K`, given the recorded reading choices `ρ`. Acceptance requires exactly one derivation and assignment, modulo declared aliases, yielding closed typed `A`; selecting one parser result is insufficient. The all-derivations gate includes antecedent and scope alternatives. Resource exhaustion is an error/UNKNOWN, never uniqueness. Logical judgment uses `A`, not mutable conversation history; standalone export repeats its targets.

**Accessibility.** Registered names are reusable throughout their declared document scope; there is no nearest-mention, gender, salience or paragraph-reset heuristic. A local binder stays inside its sentence/rule. Quantification, negation, disjunction, conditionals, quotation and attitudes cannot export witnesses. A quoted name can be identified without admitting quoted facts. Forward navigation is allowed after indexing; proof and definition dependencies must remain acyclic. Section scope must be explicit, not inferred from typography.

“A service is deployed. It is reviewed” does not license a fresh constant or two unrelated existentials. The same-witness reading rewrites to “Some service is deployed and reviewed,” meaning `∃x (deployed(x) ∧ reviewed(x))`, with both source spans retained. Other readings remain alternatives. A universal followed by “it” likewise needs an explicit scoped rewrite. Sentence fusion changes reviewed presentation, never historical source boundaries.

**Definites.** Separate declared names (“the API”) from descriptions. For an explicit restriction `D`, define `U(D) := ∃x (D(x) ∧ ∀y (D(y) → y=x))`. An assertive unique-description reading of “The owner is ready” is `∃x (D(x) ∧ ∀y (D(y) → y=x) ∧ ready(x))`. A presuppositional reading records `U(D)` separately and checks `∀x (D(x) → ready(x))` only under that displayed premise: prove it or retain an admitted assumption; otherwise resolution remains pending. Never infer existence from “the,” uniqueness from one known instance, or truth from a finite lookup. Contextual restrictions and competing presupposition/accommodation readings remain explicit. No choice functions or witness constants are introduced.

<div style="break-after: page;"></div>

## Page 2 — English and cross-reference

These are **proposed admission rules**, not claims that today's parser accepts all examples. Declared vocabulary still controls predicate meanings. All accepted renderings must be writable and round-trip with their bindings.

| Input or situation | One-reading wording / admission rule |
|---|---|
| “The API is reviewed. It is safe.” | The reviewed presentation of the second sentence is “The API is safe.”; the source `It` is retained as provenance. Bare `it` requires one accessible antecedent and no competing quantified mention. |
| Alice and Bob precede “She is ready.” | Ask “Does ‘she’ mean Alice or Bob?” Offer “Alice is ready” and “Bob is ready,” with a distinguishing situation. Never select by name or gender. |
| “This service is safe.” | Bind to a particular named service; display “The API is safe.” Bare `this` referring to a claim/action needs that target kind and its own supported semantics. |
| “Every such service is safe.” | With an explicitly bound property, write “Every reviewed service is safe.” `such` copies exactly that property, not a guessed similarity relation. |
| “The former is ready.” | Bind to the first member of one explicitly identified ordered pair, e.g. Alice in “Alice and Bob”; render “Alice is ready.” Competing pairs require a question. Pair order asserts no inequality. |
| “Her manager is ready.” | First resolve “her”; then expose the manager relation and uniqueness: “Alice has exactly one manager. Every manager of Alice is ready.” Preserve any presupposition reading separately. |
| “They are ready.” | For a selected finite list and distributive reading, write “Alice is ready and Bob is ready.” Collective, generic and unknown-group readings stay unresolved. |
| “Every eligible service is reviewed, where eligible has the meaning defined in section 2.” | Rewrite as “Eligible has the meaning defined in section 2. Every eligible service is reviewed.” The first sentence selects the exact W3 declaration exported by the pinned section and attaches it to `eligible`; the second is checked as ordinary English with the same universal assertion. |
| “Article 29”; “clause 2.1” | Bind a qualified document/edition and stable container/unit ID. A whole article is a location, not one inferred proposition. |

**Three distinct operations.** “See Article 29 of the Universal Declaration of Human Rights” is a navigation instruction/label. “Eligible has the meaning defined in section 2” selects a pinned W3 declaration, signature and body; it neither invents a definition nor changes its environment. “By clause 2.1, the API is safe” requests a W3 checked deduction, with matching environment, every cited non-background transitive leaf listed among the citing claim's own hypotheses, compatible reading choices and inherited transitive leaves; all retained assumptions, bridges and reading choices remain visible. A link alone performs neither of the latter operations. Missing imported content stays unresolved; no live URL lookup can change committed meaning.

Qualified references include subsection/item paths when needed. Renumbering preserves target identity but refreshes source/display approval; edited target content invalidates dependent bindings and certificates as appropriate. Duplicate numbers, ambiguous editions and dangling anchors fail. Navigation cycles are harmless; inference cycles fail.

W1 exception/precedence references resolve to stable rule IDs and retain W1's same-predicate and DAG restrictions. “Under Article 29” does not automatically import every clause as a premise, establish legal authority, or choose override semantics. Incorporation and authority require explicit admitted content and remain open otherwise.

<div style="break-after: page;"></div>

## Page 3 — Ambiguity, assurance and implementation gates

**Modes.** Authoring asks a short English question, shows expanded alternatives and concrete distinguishing situations, then records the author's signed choice. The expansion is the reviewed presentation in authoring, approval and export; the source pronoun is kept as provenance only. A hidden binding never rescues ambiguous displayed prose. Translation keeps every admitted reading considered so far; its inventory is extensible, never a claim of exhaustive interpretation. A translator's narrowing is attributed and labelled on every dependent result; it cannot replace the source set. Weights never select a referent. Missing semantics or distinguishing evidence leaves a candidate pending, not fictitiously checked.

**Correlated readings.** A choice assigning “this pattern” controls all later references to that same mention. Record dependencies and enumerate compatible *joint* assignments, rather than taking independent per-sentence products. For same-environment/background assertion readings, a joint assignment denotes the conjunction of its sentences; use a disjunction of these conjunctions only after proving correspondence to the compatibility relation. Reuse W2's per-unit shortcut only for independent choices. Otherwise elaborate each complete choice (maximum 64); unsupported kinds/backgrounds or budget overflow yield UNKNOWN. ALL needs proof for every compatible choice; NONE needs checked countermodels for every choice (one shared model may suffice); SOME needs a choice proof and another choice's countermodel. Retain vacuity and global choice/version labels through citations. ALL, NONE and SOME are defined only over a nonempty validated compatible-joint set. An empty set is a manifest validation error (an invalid-compatibility diagnostic), distinct from inconsistent premises inside an existing choice, which keep W2's inconsistency and vacuity report; validation that does not finish within budget is UNKNOWN.

| Boundary | What is established |
|---|---|
| CHECKED | Source partition, target identity/accessibility, one admitted elaboration, typing, and certificate/model results under listed premises. Assumption support does not prove truth. |
| LABELLED | Navigation, headings, kind/support/provenance and proposed reference inventories. A linked clause or matched pronoun alone gives no substantive coverage. |
| OPEN | Fully represented claims with named W2 open predicates and residual adjudication; unstated deciders stay unstated. |
| READINGS / UNFORMALISED | Complete admitted alternatives versus missing content/semantics. Unelaborated inventories remain UNFORMALISED; never rename ambiguity as an open predicate. |

**Lean obligations, all pending.** Independently review `Resolve`, accessibility and description semantics before implementation. Prove (1) executable resolution soundness, supported-fragment completeness/termination, unique accepted assignment, capture-avoiding substitution and closedness; (2) `Holds(S, elaborate(K,s,ρ)) ↔ Intended(K,s,ρ,S)` for every admissible structure, including description definedness and same-witness rewrites; (3) unchanged environments/models for substitution, preservation of old denotations/consequence, finite evaluation and countermodel correspondence; (4) joint-choice equivalence, version-compatible citation composition and retention of assumptions/kinds/bridges; (5) English parse/render correspondence, exact source/manifest/expected-statement binding and stale-dependency rejection. Bind any actual vocabulary extension through P0 `Layer` obligations; do not present existential witness naming as W3's unique conservative expansion.

Audit proofs under the existing axiom allowlist; no `sorryAx`, added domain axioms or assumed checker soundness. Decoding, hashing and display remain named trust boundaries until refined. An untrusted resolver may propose bindings; a small verified validator authorizes them. Python/Rust/Lean agreement is regression evidence, not these proofs.

**Existing limits matter.** [Integration gaps](../INTEGRATION-GAPS.md) still block Lean mixed W1/W3/data cases, defined-environment document graph admission and a full W2/norm natural-view round trip. Current [natural rules](../natural-view.md) admit only narrowly placed `it` with one previously mentioned constant and no earlier quantifier; plural/possessive forms require repair. This plan adds no assurance to those paths. Unsupported compositions remain explicitly unsupported.

<div style="break-after: page;"></div>

## Page 4 — Evidence, delivery and expected unlock

**Pinned evidence.** Constitution [metrics][metrics], [units][units], [audit][audit] and [trend][trend], run `20260927T1800Z`, use 184,893 bytes / 1,124 units: C/L/O/R/U = **22/349/0/0/184,522 bytes**, **1/39/0/0/1,084 units**. Source SHA-256: `fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd`. The 20/20 audit covered one assertion and nineteen metadata units. It does not validate discourse coverage. Run `20260928T0600Z` adds one OPEN norm unit (`u0165.s07`, 48 bytes) whose fidelity is unaudited; its discourse tally (78) and heading-presupposition count (29) are unchanged. `1800Z` remains the pinned audited baseline North Star uses.

`other:discourse` marks 78 primary-blocker units / 8,200 bytes, including lists, questions and expository text. All 29 heading presuppositions total 999 bytes, but only **14 / 437 bytes** overlap that tag. North Star's 0–7,201-byte estimate subtracts all 999; the ledger's actual non-heading tagged pool is **64 / 7,763 bytes**. Record this reconciliation before refreshing the portfolio. Neither pool predicts gains; additional co-blockers were not exhaustively tagged. Heading presuppositions are a separate overlapping opportunity, not an automatic existence-claim upgrade.

Prioritize `u0136.s01` (“Such potential harms”: scope plus soft weighing), `u0182.s03` (“it … these mechanisms”: reference inside a question), `u0214.s02` (“this broad pattern”: naming plus open safety), and `u0256.s03` (“it … these questions”: entity/content distinction). The rejected `u0214` audit forbids calling the entire passage OPEN when parts remain unrepresented. [UDHR Article 29][udhr] supplies article/subclause and “These rights and freedoms” fixtures; rights semantics remain a co-blocker.

| Sequence / owner interface | Reviewable deliverable and exit gate |
|---|---|
| 1. Spec + corpus | Pin source spans, scope/target alternatives and co-blockers; review independent semantics and negative fixtures, including: a manifest that binds a span to a same-witness reading and also admits it as an independent unit is rejected; two independently quantified replacements for one shared witness are rejected as that reading's elaboration. Inventory docs/tutorial and paper references with denominators. |
| 2. Document + English | Versioned anchor/mention manifest, deterministic name/navigation resolver and explicit English expansion in `ve/document.py`, `ve/english.py`, `ve/natural.py`; reject tampering and dangling targets. |
| 3. Lean + conformance | Implement `lean/VE/Discourse/*`; discharge page-3 obligations for each advertised slice before assurance claims. Description tests cover absent/multiple owners and scope escape; replay proofs and countermodels. |
| 4. Readings + IDE | Extend `ve/readings.py` and W8 actions for compatible choices, source-preserving fusion, English questions and signed authoring; translation never drops alternatives. Test choice correlation, exhaustion and stale versions. |
| 5. Integration + pilots | Close required W1/W3/W2 gates; test quotation bridges, exception targets, duplicate/renumbered sections and changed definitions. Rerun pinned pilots and independently review source-to-rendering fidelity. |

**Accounting and risks.** Keep exact UTF-8 partitions, including punctuation; shared references/fused sentences never count bytes twice. Report C/L/O/R/U bytes and units, residuals and reference-resolution counts separately; W2 internally calls open reading sets OPEN, so derive pilot READINGS from admitted content, not that enum alone. Separate new semantics from splitting/relabeling; retain old-boundary comparisons and certificate/audit provenance. No new measured gain until rerun.

Expected first unlock is readable named-reference and navigation coverage in docs/paper, unmeasured today. Constitution substantive opportunity is **0–7,763 tagged non-heading bytes**, conditional on other semantics and fidelity; zero remains possible. Benefits outside this tag are unmeasured. UDHR, legal descriptions, news, policies and textbooks remain unquantified. Principal risks are hidden witness scope, false uniqueness, correlated-choice explosion, stale targets and invented authority. Staged rejection/UNKNOWN and explicit residuals are acceptance requirements, not temporary silent fallbacks.

[north]: ../../../ve-northstar/NORTH-STAR.md
[w3]: ../../lean/VE/Definitions/STATEMENTS.md
[metrics]: ../../../manage-agents/pilots/claude-constitution/run-20260927T1800Z/metrics.json
[units]: ../../../manage-agents/pilots/claude-constitution/run-20260927T1800Z/units.json
[audit]: ../../../manage-agents/pilots/claude-constitution/run-20260927T1800Z/AUDIT.md
[trend]: ../../../manage-agents/pilots/claude-constitution/TREND.md
[udhr]: ../../../manage-agents/pilots/udhr/source/udhr.md
