# Trust map: what a reviewer must accept, and what is proved

Audit of `main` at `a093a14d` (2026-10-03). This file does not change code. It answers
four questions:

1. What must a reviewer read and agree with to accept VE's guarantees (the trusted
   base)?
2. Which code is proved against that base, and by which theorem?
3. Where is the trusted base larger than it needs to be: duplicated notions, code that
   carries meaning with no theorem, and dead code?
4. Which guarantees rest on Python (or Rust) and are not checked by Lean at all?

Scope: all 286 Lean files under `lean/` (87,722 lines), plus the Python and Rust code that
decides what reaches Lean. Section 9 lists the method and its limits. In brief: line counts
are per declaration span, accurate to about ±10%, and the theorem links that most affect
the conclusions were checked again by hand.

## 1. Summary

* **Lean is the authority on only part of today's acceptance path.** Lean decides alone on
  the statement-layer routes: norms, norm defaults, soft norms, rights, risk, alternatives,
  reports, readings, `@2` discourse and quantity. Python modules such as
  `ve/alternatives.py` only forward those cases to a Lean executable.
  * Everything else defaults to Python. `VE_AUTHORITY` defaults to `python`
    (`ve/backends/dispatch.py:61`), and 24 of the 26 operations in
    `ve/assurance-manifest.json` list Python as the authority. Those operations include
    parse, typing, evaluation, certificate replay, countermodel checking and admission.
    Under the default setting, the Lean proofs for them are cross-checks, not the gate.
  * Running with `VE_AUTHORITY=lean` is supported, and the full suite passes under it.
* **English meaning is Python in every mode.** Turning an English sentence into a formula,
  and the "exactly one reading" check, are done by Python and the Lark library
  (`ve/english.py`, `ve/surface/unambiguity.py`). Lean has a proved grammar, but only for
  the core English fragment, only over token lists, and nothing on the acceptance path
  calls it (section 8).
* **The core logic is small, but there are four copies of it.** The base first-order
  logic is defined in about 110 lines: `VE/Syntax`, `Semantics`, `Finite`, `Consequence`.
  It is then defined again three times, each with its own `Formula`, `denote` and
  `Entails`: in `VE.Closure`, `VE.Core` and `VE.Order`. There are also four separately
  proved tableau checkers.
  * The copies are related only by one-directional conservativity theorems.
  * The checkers do not add trust, because each has its own soundness proof.
  * The repeated definitions do add trust: a reviewer has to read each one.
* **Most proofs are where they should be.** Every executable checker on a verdict path has
  a soundness or iff theorem: evaluators, tableau replay, conflict checks and elaborators.
  About 48% of all lines are proof.
* **The weak points are where checked results are joined together and where wire inputs
  are decoded.** Section 5.1 lists verdicts that reach users with no theorem covering the
  path that produces them. Section 5.2 lists theorems whose names suggest "decoded JSON ⇒
  property" but whose decoding hypothesis is never used. The most important cases:
  * The three main route runners, `runFol`, `runClosure` and `runOrder`
    (`VE/Route/Wire.lean`). No theorem covers the full background that they replay against
    (flags, definitions and literals).
  * The public norms route runs `Norms.Flagged`, not the `Norms.Replay` functions that
    NORMS.md cites. For a document with flags or definitions, its CONFLICT-FREE verdict
    means `Flagged.BaseConflictFree`, a separate notion with no theorem linking it to
    `ConflictFree`.
* **Feature meanings (S) are about 6,300 lines.** Most features define their meaning
  twice, once directly and once by elaboration into core, and tie the two with a
  faithfulness theorem. In several cases the direct meaning reuses the elaboration's own
  helpers, or is defined as the checker's output. The faithfulness theorem then proves
  less than its name suggests (section 4).
* **The same notions are defined many times across features.** Examples: admission,
  conflict-check, layer-chain and package-binding scaffolds; `disjunction`; claim graphs;
  bundles; formula encoders; SHA-256. A shared statement-layer kit, one logic with
  profiles, and decoder round-trip theorems would shrink the base the most (section 7).

## 2. Classes

Each `def`, `abbrev`, `structure`, `inductive`, `class` and `instance` was assigned one
class:

| Class | Meaning | Trusted? |
|---|---|---|
| **K** | Core logic and semantics: syntax, typing predicate, structures, denotation, `Entails`. Includes logic-profile extensions (closure, order, time). | Yes, by definition |
| **S** | A feature's intended meaning (what a norm, right, risk status or discourse reference means). | Yes, by definition |
| **D** | Decoders, encoders, wire and text parsing, printing, hashing, canonical JSON. | Yes, unless a theorem ties it to K/S |
| **G** | Glue: routes, dispatch, services, executables, report builders, limits. | Yes, unless a theorem ties it to K/S |
| **C** | Checked executable: a checker, evaluator, elaborator or replay with a soundness or iff theorem against K/S. | No; only the theorem's statement is read |
| **P** | Proof-only helpers and the theorems themselves. | No (kernel-checked) |
| **T** | Tests, `#guard` and example checks, the `#print axioms` audit list. | No |

C is not one of the four classes in the brief. It was added because checkers are neither
decoders nor glue, and keeping them in their own class shows how much executable code is
already outside the trusted base.

Trusted D and G code falls into three groups, depending on how a bug in it shows up:

* **[V] verdict-bearing.** A bug can produce a wrong accepted result: a decoder that
  misreads a premise, or a runner whose output field has no theorem.
* **[R] reject-only or diagnostic.** A bug can only produce a wrong rejection or wrong
  error text. This affects completeness and usability, not soundness.
* **[I] identity and provenance.** Hashes, ids and binding checks. A bug weakens
  freshness and binding claims; the logical replay does not depend on them.

## 3. Line counts by class

Counts are per directory. Section 10 has per-module rows. "Base v0" is
`VE/{Syntax,Semantics,Typing,Finite,Consequence}`.

| Group | Lines | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Base v0 logic | 381 | 107 | 0 | 0 | 0 | 44 | 166 | 0 | 64 |
| `VE/ClaimGraph` | 339 | 0 | 67 | 0 | 0 | 49 | 179 | 0 | 44 |
| v0 tableau (`Tableau`, `TableauClosure`, `TableauChecker`) | 655 | 0 | 0 | 0 | 0 | 169 | 412 | 0 | 74 |
| Closure tableau (`VE/TableauExtended*`) | 1,075 | 0 | 0 | 0 | 0 | 276 | 680 | 0 | 119 |
| Kernel wire and surface (`Json`, `Bridge`, `CertificateWire`, `Surface`) | 842 | 2 | 0 | 614 | 67 | 20 | 15 | 5 | 119 |
| Kernel proof files (`RoundTrip`, `LexicalProofs`, `SurfaceProofs`, ...) | 1,063 | 0 | 0 | 0 | 0 | 0 | 1,007 | 0 | 56 |
| Kernel checks and `VE/Audit` | 3,320 | 0 | 0 | 0 | 0 | 0 | 5 | 3,161 | 154 |
| `Closure/` | 1,381 | 76 | 0 | 192 | 39 | 178 | 717 | 26 | 153 |
| `Core/` | 3,093 | 88 | 0 | 348 | 133 | 503 | 1,562 | 47 | 362 |
| `Order/` | 2,986 | 150 | 0 | 367 | 121 | 422 | 1,554 | 195 | 177 |
| `Time/` | 3,827 | 180 | 204 | 703 | 232 | 369 | 1,931 | 0 | 208 |
| `Definitions/` | 1,294 | 0 | 58 | 28 | 39 | 201 | 864 | 0 | 104 |
| `Data/` | 172 | 0 | 32 | 0 | 0 | 20 | 111 | 0 | 9 |
| `Route/` | 5,249 | 61 | 369 | 651 | 538 | 614 | 2,291 | 325 | 400 |
| `WireContract/` | 1,073 | 0 | 0 | 161 | 636 | 0 | 86 | 75 | 115 |
| `Service/` | 3,927 | 5 | 84 | 783 | 1,478 | 338 | 891 | 11 | 337 |
| `English/` | 2,254 | 0 | 90 | 434 | 45 | 66 | 1,409 | 0 | 210 |
| `Discourse/` | 8,004 | 0 | 1,161 | 1,389 | 616 | 348 | 4,070 | 74 | 346 |
| `Readings/` | 3,920 | 0 | 249 | 397 | 316 | 265 | 2,140 | 285 | 268 |
| `Compose/` | 1,863 | 0 | 42 | 4 | 108 | 12 | 1,048 | 542 | 107 |
| `Norms/` | 5,957 | 21 | 363 | 464 | 414 | 536 | 3,371 | 324 | 464 |
| `NormDefaults/` | 6,189 | 0 | 234 | 181 | 129 | 584 | 4,536 | 165 | 360 |
| `SoftNorms/` | 5,300 | 0 | 485 | 481 | 540 | 375 | 2,502 | 0 | 917 |
| `SpeechActs/` | 2,962 | 0 | 187 | 867 | 146 | 318 | 977 | 0 | 467 |
| `Rights/` | 4,439 | 0 | 736 | 589 | 429 | 270 | 1,693 | 384 | 338 |
| `Attribution/` (namespace `VE.Reports`) | 4,198 | 0 | 637 | 628 | 332 | 150 | 2,179 | 0 | 272 |
| `Risk/` | 7,354 | 0 | 963 | 690 | 675 | 404 | 4,148 | 0 | 474 |
| `Alternatives/` | 3,412 | 0 | 356 | 285 | 621 | 106 | 1,472 | 265 | 307 |
| Top-level `lean/*.lean` (executables, `ResponseDecode`, `RiskEvalMain`) | 895 | 0 | 0 | 0 | 76 | 0 | 0 | 673 | 146 |
| `Iceberg.lean` (a standalone physics example, not VE) | 301 | – | – | – | – | – | – | – | – |
| **Total** | **~87,700** | **~690** | **~6,300** | **~10,300** | **~7,700** | **~6,600** | **~42,000** | **~6,600** | **~7,200** |

How to read the table:

* **K is under 1% of the code, and 110 lines of it are the actual base logic.** The other
  K lines are the Closure, Core, Order and Time copies and profile logics (section 6.1),
  plus 61 lines of route-layer semantics (`Route/Layer`, `Route/Checker`).
* **The trusted surface is about K+S+D+G ≈ 25,000 lines**, minus the D/G items that a
  theorem covers.
  * Most D/G code is not covered by a theorem. But much of it is [R]
    (reject-only/diagnostic) or [I] (identity/provenance), so for soundness the reviewer's
    real load is K + S + the [V] items in section 5.
  * This audit did not measure the [V]/[R]/[I] split in lines. Rough reading suggests the
    [V] share of D+G is under half.
* **D+G is larger than S in most statement features.** In SpeechActs, D is 867 lines
  against 187 lines of S. In Discourse, D is 1,389 against 1,161. Each feature carries its
  own wire decoders, and only a few of them have round-trip theorems.

## 4. The meaning a reviewer must accept (K and S)

### 4.1 Core

| Notion | Definition | What ties executables to it |
|---|---|---|
| v0 syntax, typing | `VE/Syntax.lean`: `Environment`, `Term`, `Formula`, `Term.sortOf`, `Formula.WellFormed`, `Document` | `check_iff_wellFormed` |
| v0 semantics | `VE/Semantics.lean`: `Structure`, `TupleTyped`, `Admissible`, `Valuation`, `denote`, `Entails` | `eval_iff_denote`, `countermodelCheck_iff`, `countermodel_sound`, `Tableau.checkCertificate_sound` |
| finite models | `VE/Finite.lean`: `FiniteModel`, `asStructure`, `Valid` | `modelData_valid`, `decodeModel_valid` |
| JSON consequence | `Bridge.JsonEntails := Entails.{0}` | `CertificateWire.Query.accepts_sound` |
| claim graphs | `VE/ClaimGraph.lean`: `Claim`, `Node`, `Report`, `Acyclic`, `Unfolds`, `SoundReport` (S) | `Graph.check_sound`, `check_entails`, `check_unfolds` |
| closure profile | `Closure/{Paths,Syntax,Consequence}`: `Path`, `Reachable`, `Formula` with reach atoms, `denote`, `Entails` | `Closure.Tableau.checkCertificate_sound`; `conservativity` (v0 ⊂ closure) |
| core (closure + n-ary atoms) | `Core/{Paths,Syntax,Consequence,Route}` | `Core.Tableau.checkCertificate_sound`; `embedClosure_denote`, `entails_closure` |
| order profile | `Order/{Syntax,Semantics,Finite,Consequence}`: a full separate logic with integer terms | `Order.Tableau.checkCertificate_sound`; `Order.entails_v0` (one direction only) |
| time and units | `Time/{Syntax,Semantics}`: `QTerm`, `QFormula`, `TStructure`, `tdenote`, `TEntails` | `units_faithful`, `tentails_of_entails`, `lift_admissible` |
| route layers | `Route/Layer.lean`: `Semantics`, `Layer` (with `Intended`, `faithful`, `expands`), `compose` | used by every statement route's chain proof |

Two assumptions sit outside every theorem; `lean/README.md` already records both:

* the disjoint-carrier interpretation assumption;
* the trust in Lean's kernel, compiler and runtime, and in the standard library.

### 4.2 Feature meanings

There are three ways a feature can give its meaning:

* **S-direct:** a Prop-level semantics.
* **S-by-elaboration:** the feature means whatever its elaborator produces as core
  formulas, so the elaborator itself is trusted.
* **Both:** a direct semantics plus an elaboration, tied by a faithfulness theorem.

"Both" is only worth having if the direct side is independent of the elaborator. The table
says how independent it really is.

| Feature | Form | Faithfulness theorem | Independence of the direct side |
|---|---|---|---|
| Norms (W1) | Both: `AppliesD` … `Value`, `IntendedAt` vs `elaborate` | `elaborate_iff_at`, `elaborate_iff`, `prefix_satisfaction` | Shares `children`, `rulesOn` and the fuel `T.nodes.length` with the generator. `ConflictFree` is defined over substituted formulas and tied to `Unique DocumentExpansion`. |
| Norm defaults | Both: `Value3`, `IntendedAt3`, `Expansion3` vs `fill` | `fill_intended`, `fill_expansions`, `fill_conservative` | Good. `fill U` is an ordinary W1 `Doc`. |
| Soft norms | Both: `ValueSoft`, `IntendedSoftAt` vs `soften` | `soften_faithful`, `soft_intended_iff` | Good. Dominance is defined three times; the three are tied. |
| Rights | Effectively by elaboration: `correlate` | `correlate_faithful`, `correlate_value` | Weak. `ValueRight` is built from `nodeOf`, `ownGuard`, `limPack` and `correlate D`, so the theorem certifies only the bar encoding. |
| Reports and attribution | Both: `Sat`, `IntendedReports` vs `elab`, `premises` | `reports_elaboration_faithful`, `reports_old_language_conservative`, `reports_no_leak` | Good. This is the cleanest feature. |
| Speech acts | By elaboration into W1 (`demand`, `policy`); answers direct (`AnswersAt`) | `model_answers`, `premiseStatus_sound` | Commands are ordinary W1 rules, so there is no new deontic notion. |
| Alternatives | Direct (`FollowableIn`, `E1`–`E3`) plus inlining of profile words | `inline_faithful`, `validate_sound` | Good. |
| Risk | Mostly by elaboration (`validateDecision`, the `regenerate` tables) on top of the Alternatives meaning | `risk_inline_faithful`, `regenerate_sound`, `certainE_iff`, `scan_sound` | Statuses and Q1 use Alternatives' `permittedAt` and `requiredAt`, which ALTERNATIVES.md labels untrusted diagnosis. |
| Discourse | Both: `Intended` vs `elaborateD` | `elaborate_faithful`, `validate_accepted`, `validate_complete` | Partial. `Acc` (accessibility) is defined as `accB D m t = true` (`Discourse/Access.lean:355`). `PredTyped` uses `restrFormula`. `SlotMeaning` reuses `npConsts` and `modPred`. |
| Readings (S1) | Direct: `Achieves`, `Separated`, `WellFormedDoc` | `separates_sound` (soundness only; returns false above 12 cells) | Good, but see section 5.1 for the pair loop. |
| Definitions | Layer: `Def`, `Agrees` | `faithful`, `conservative` | Good. |
| Data flags | `Functional`, `Total`, `DataAdmissible` | `generate_sat_iff`, `fol_data_route_acceptance` | Good. |
| Time documents | `Time/Document.lean` re-defines the admission model of `Route.Admission` | `admit_quantity_report_sound` | A duplicate notion (section 6.2). |
| Core English | `English.Tree.denote` | `core_parse_sound`, `core_unique_derivation`, `core_parse_render` | Not on the acceptance path (section 8). |

Code-as-spec cases are definitions that the reviewer reads as the meaning but that are
literally the checker's output:

* Discourse: `Acc` and `wellFormed`.
* Definitions/Bundle: `ReadingCompatible := (leafChoices ls).isOk` and `LeafBound`.
* Discourse: `canonTarget` is the identity function and `AliasEq` is plain equality.

For these, "checker ⇒ spec" holds by `rfl`, so the reviewer has to read the checker as the
specification.

## 5. Decoders and glue: tied or trusted

### 5.1 Verdicts with no theorem covering their production path [V]

Each item below is a user-visible verdict or field. Its parts may be proved, but no
theorem states the end-to-end claim. "By inspection" means a reviewer can compose existing
theorems by reading the code, but Lean has not checked that composition.

| Path | Verdict | What exists | Gap |
|---|---|---|---|
| `Route/Wire.lean` `runFol`, `runClosure`, `runOrder` | `valid`, `refutes`, `values` | `*_checkCertificate_sound`, `refutesF/C_sound`, `valuesF/C_sound` | No wire theorem names these runners. They replay against `fullBackground` (flags ++ definitions ++ literals). `fol_route_acceptance` covers literals; `fol_data_route_acceptance` covers flags ++ literals; `Definitions.Route.acceptance` covers definitions ++ literals. No theorem covers all three together. `Core.Wire.run_certificate_acceptance` shows the pattern that is missing. |
| `Order/Wire.runCase`, `Order/Surface.runCase` | `valid`, `refutes` | `Query.accepts_sound` (over a Lean `Query`), `checkCountermodel_sound` | Only the profile gate is proved (`order_route_gate`). |
| `Time/Wire.runCase` | `refutes`, `value` | `refutesB_sorted_sound` (on erased formulas), `lift_admissible`, `units_faithful` | ¬`TEntails` and value = `tdenote` are not stated. |
| `Definitions/Bundle.runBundle` | bundle accepted | `bundle_sound` over `backgroundLeaves` (definitions ++ literals) | `runBundle` replays on `fullBackground`, which also includes flags. |
| `Norms/Run` → `Flagged.replayConflict` | CONFLICT-FREE | `norms_flagged_conflict_sound` | When flags or definitions are present, this concludes only `BaseConflictFree`. No theorem relates that to `ConflictFree` or to unique expansion. |
| `Norms/Plain.run` | certificate `valid` | the core checkers' soundness | No theorem covers the extended background or `softPremises` ("a trusted composition point"). |
| `Service/FamilyNorms.runCase` | CONFLICT-FREE (family) | per-certificate `*_norms_certificate_sound` | No family-level theorem over `pyTargets`. |
| `Risk/Run.runConflict` (witness) | CONFLICT | – | No risk counterpart of `alt_conflict_witness_sound`. |
| `Risk/Run.runFollowable` (witness) | DILEMMA | `risk_dilemma_witness_sound` | Not composed with `decodeWitnessModel`. Alternatives has `alternatives_wire_dilemma_sound`. |
| `Risk/Run.runCertificate` | `valid` | `checkCertificate_sound` holds by inspection | No wire theorem. Alternatives has `Replay.alternatives_wire_acceptance`. |
| `Risk/Record.statuses` | permitted / required statuses, Q1 | `eval_iff_denote` | Uses `Alternatives.permittedAt` and `requiredAt` from the "untrusted diagnosis" section. RISK.md says `risk_wire_scenario_sound` certifies the statuses; it proves `res.statuses = statuses …` by definition. |
| `SoftNorms/Run` `sufficientCoherence` and friends | `conditional_on` | `soft_wire_conflict_sound` under all of `Coh_T` | Nothing proves that dropping labels one at a time, cumulatively, preserves the claim. |
| `SoftNorms/Run.classify`, `weighingWitness` | `soft-pairs` classification | `weighing_point_sound`, `disjoint_sound` | Matches by inspection only. |
| `Readings/Run.setPairs`, `setFindings` | "every pair is separated" | `separates_sound` per pair | No theorem about the pair loop. |
| `Readings/Separate.actOnly` | `SeparatedByActOnly` | – | No theorem, and the output carries no "(not certified)" marker. `decisionOnly` has the marker. |
| `Rights/Run` `tuples`, `projections`, `licence`, `barResult` | projections, licence, bar | `licensed_cases`, `circ_canon` | `licence` re-derives `Scope.licensed` with no theorem relating the two. Projections are not tied to `rightsOf` or `dutiesOf`. |
| `Rights/Admission.validateCouplings` | coupling acceptance | `admitDocument_spec` restates the Boolean | Couplings have no semantics in Lean. |
| `Attribution/Run.scopedVerdict` | DOES NOT FOLLOW | `scoped_witness_sound` covers the idea | No theorem names the branch. |
| `Core/Wire.run` (evaluate and countermodel), `Core/Layers.run`, `Closure/Bridge.runCase` | values, refutes, valid | pieces such as `valuesN_sound` and `decodeModel_valid` | No composed theorem. The `Core/Layers.lean` docstring claims soundness via `checkCertificate_sound`, which covers only the decoded premises. |
| `Service/Standalone.modelCase` | model `valid:true` | the decoders have validity theorems | Their results are discarded. |
| `Discourse/Run` `runResolve`, `runJoint`, validity answer | resolution and validity text | `validate_accepted` | Only the admission branch has `discourse_wire_acceptance`. |
| Error responses (`runCaseReported`, `Protocol.caseError`) | `valid:false` on every error | – | A resource limit or stale binding reads as "invalid". |

### 5.2 Theorems that never use their decoding hypothesis

Each of these takes `h : replayX j = .ok r` (or the equivalent) and its proof never uses
it. The conclusion is therefore about *any* record of that type, not about the record
decoded from `j`. The sound part, the checker's soundness, still holds. What is missing is
the claim the name suggests, that the decoded input had the property.

* `Readings.Wire.readings_wire_separate_sound` (`Readings/Wire.lean:645`).
* `SpeechActs.Run` theorems: `speech_wire_conflict_free_sound`,
  `speech_wire_answer_sound`, `speech_wire_consequence_sound` and
  `speech_wire_conflict_witness_sound`.
* `Service.Graph` theorems: `graph_sound`, `graph_entails` and `graph_unfolds`. Their
  `compose` hypothesis is unused, so they do not tie `c.E` to the submitted environment.
* NormDefaults theorems: `normDefaults_wire_gaps_sound`, `_status_sound` and
  `_reached_sound` have no `decodeSourceU … = .ok s` clause at all. In `fill_expansions`,
  the hypothesis `hB` is unused.

The soft-norms, rights, alternatives and norms replay theorems do include the decode
equation (for example `norms_flagged_conflict_sound`'s first conjunct). They are the model
to follow.

### 5.3 Decoders and glue trusted as-is

Grouped by module. Tags: [V] verdict-bearing, [R] reject-only or diagnostic, [I]
identity/provenance, [X] display text. Items not listed here are tied by a theorem;
section 10 and the per-feature `.md` files name those theorems.

**Kernel** (`VE/`, `Closure/`, `Core/`, top level)

* [V] `Json.lean`: the whole restricted JSON parser.
* [V] `Bridge.lean`: `decodeEnvironment`, `Vocabulary`, field helpers, `identifier`,
  `decodeTerm`, `decodeFormula`, and the AST part of `decodeDocument` and
  `decodeCountermodel`. The typing proof is carried; decoding fidelity is not proved.
  `decodeModel` has an output-admissibility proof (`decodeModel_valid`) but no wire
  correspondence theorem.
* [V] `CertificateWire`: the premise and conclusion parts of `decodeQuery`, plus
  `runCase` and `runClosureCase`.
* [I] `CertificateWire`: `sha256`, `canonical`, `digest`, `meaningId` (`#guard` vectors
  only).
* [V] `Closure/Surface` and `Core/Surface` beyond singleton Named reach atoms: Body edges,
  n-ary atoms and mixed documents. Only a runtime self-check guards them.
  `VE/Surface.lean` is fully round-tripped (`parse_print`, `print_injective`).
* [V] `Closure/Bridge` and `Core/Bridge` decoders. `Core.Bridge.runCase` and
  `runCaseReported` have no callers in the Lean tree.
* [V] `Core/Wire` decoders, and `Core/Layers` (all of it).
* [V] `Main`, `Serve` and the `*Main` delegators (dispatch only).

**Order, Time, Definitions**

* [V] `Order/ModelCheck.Vocabulary`: the definitional meaning of the wire vocabulary.
* [V] `Order/Wire` decoders for environment, terms and formulas.
* [V] `Order/Surface`: the parser and `formulaJson`. ORDER.md claims no round trip.
* [V] `Time/Wire`: environment decoding, `elabTerm`, `elabFormula` and `decodeQuantity`.
  These carry meaning: they are the JSON-to-`QFormula` elaborator.
* [V] `Time/Wire`: `encCore` and `encQ`. Each is re-decoded, then the result is discarded.
* [V] `Time/Calendar`: `parseIso` and `iso`; `Time/Decimal`: `parseDecimal`,
  `Dec.toString` and `renderAmount`. None has a string-level round trip.
* [V] `Time/Document` decoders.
* [I] `Time/Document`: the report JSON and `report_id`.
* [V] `Definitions/Bundle`: `decodeLeaf`, `decodeLemma`, `runBundle`.
* [R] `Definitions/Elaborate`: `levels` and `premiseWithin` (limits).

**Route, Service, WireContract**

* [V] `Route/Wire`: `decodeVocabulary`, `decodeBody`, `decodeDefined`, the AST part of
  `runBackground`, and the runners from section 5.1.
* [I] `Route/Wire`: `encodeFormula`, `meaningId`, `environmentId`, `bindingOk`. There is no
  decode∘encode theorem.
* [V] `Route/Admission`: `decodeUnit`, `decodeLemma`, `decodeReadingSet`, `decodeNode`,
  `decodeDoc`, `checkBindings`.
* [X] `Route/Admission`: `nodeDiagnostic`.
* [V] `Route/Decode`: the contents of `decodeModelData` and `decodeOrderModel`. The
  validity gates are proved equal; which tuples were read is not.
* [R] `Route/Steps` and `Route/AstLimit`.
* [V] `Route/Gate.registry`. `AllowedFamily` reads it, so in effect it is part of the spec.
* [V] `Service/Protocol`: `decodeRequest`, `decodeBudget`.
* [I] `Service/Protocol`: `Sha256.digest` and `caseDigests`. This is a second SHA-256,
  pinned to the first only by `#guard`.
* [V] `Service/Standalone`: `validated`, `typingReduced`, `reportsReduced`,
  `alternativesReduced`. Typing drops five statement profiles, with no theorem that this
  preserves typing.
* [I] `Service/Standalone`: the identity and normalisation helpers.
* [V] `Service/Graph` decoders.
* [R] `Service/Graph`: `cone` and `topological` (the checker re-checks the graph).
* [V] `Service/FamilyBundle` decoders.
* [V] `Service/FamilyNorms`: `folView` and `viewModel`, which drop predicates of arity
  greater than 2.
* [X] `Service/TypingDiagnostic`.
* [R] `WireContract/*` (engine, tables, hooks, Diagnose). It is diagnostic-only and not on
  the verdict path. Its four structural theorems relate `run` to `eval` only.

**English and Discourse**

* [V] `Discourse/Access`: the lexer (`lex`, `segments`, `unitTokens`). It matches Python
  only by tests.
* [V] `Discourse/Grammar`: slot discovery (`textSurfaces`, `discovered`). This is
  soundness-relevant: if it misses a pronoun, that unit's formula is admitted without
  elaboration.
* [V] `Discourse/Wire` (`decodeManifest` and friends) and `Discourse/Loader` (all of it).
* [V] `Discourse/Admission`: `project` and `projectUnits`. No round trip exists for the
  formula encoder they use.
* [I] `Discourse/Admission`: `reportJson` and `sourceIdOf`.
* [X] `Discourse/Resolve` and `WellFormed` diagnostic text.
* Advisory, not on any acceptance path: `English/Run` decoders and `covers`.

**Statement features**

* Norms:
  * [V] `Norms/Wire`: the whole decoder. `budgetFormula` re-implements
    `Bridge.decodeFormula` with a budget.
  * [V] `Norms/Admission.splitDocument`: its faithfulness.
  * [V] `Norms/Plain`: `run`, `strip`, `reduced`, `softPremises`.
  * [I] `Norms/Replay` and `Flagged`: `decodePackage`, `regenerated`.
  * [R] `Norms/Tree.check` and its diagnostics.
  * The Cedar export is Python-only. Lean has only `CedarShape`, and nothing checks the
    adapter's output against it.
* NormDefaults:
  * [V] `NormDefaults/Wire.decodeSourceU`, profiled branch.
  * [V] `NormDefaults/Admission.decodeFilledDoc`.
  * [I] `NormDefaults/Wire`: `decodePackageU` and the environment JSON.
* SoftNorms:
  * [V] `SoftNorms/Phases`: all of it (JSON to `SoftDoc`).
  * [V] `SoftNorms/Wire.decodeSoftSource`; `Admission.decodeSoftDoc`, a verbatim copy of
    `Route.Admission.decodeDoc`.
  * [V] the section 5.1 items in `SoftNorms/Run`.
  * [R] `SoftNorms/Soften`: `checkSoft*`, `checkW1` and the size tables.
* SpeechActs:
  * [V] `SpeechActs/Wire.decodeDocument` and friends. Three of them change meaning:
    * `mergeBindings` sets the addressee.
    * An authored reading choice replaces a unit's kind and content.
    * `signed` checks only that the signature looks like a token.
  * [X] `SpeechActs/Run`: `paraphrase`, `legend`, `answerText`.
* Rights:
  * [V] `Rights/Wire` decoders; `Rights/Admission` decoders and couplings.
  * [V] the section 5.1 items in `Rights/Run`.
  * [V] `Rights/Distinction`: which lines are listed as hits (`distinctionHits`).
  * [I] `Rights/Wire`: canonical forms and hashes.
* Attribution:
  * [V] `Attribution/Wire`: all decoders, including the computed `Pinned.background`.
  * [V] `Attribution/Status`: `meaningStatus` and `verdictStatus` (policy, not proved).
  * [I] `Attribution/Content`: `CJson`, `digestOf`, `documentId`.
* Readings:
  * [V] `Readings/Wire` decoders. These carry real meaning: `active` (the latest version
    wins), `inForce`, and pending versus fixed.
  * [V] the section 5.1 items in `Readings/Run`.
  * [I] `Readings/Run`: `oneJson` and `documentHash`. They re-implement the keep logic of
    `one`.
* Risk:
  * [V] `Risk/Record`: `decodeRecord`, and `elabTerm`/`elabCond`, which are the
    condition elaborator.
  * [V] `Risk/Wire` decoders; `Risk/Run.decodeWitnessModel`.
  * [V] the section 5.1 items in `Risk/Run`.
  * [X] `Risk/Run` rendering.
* Alternatives:
  * [V] `Alternatives/Wire` decoders and `Replay.decodeRows`.
  * [X] `Alternatives/Validate`: `diagnose` and the failure texts (documented as
    untrusted).
* Compose:
  * [V] the binding from `Route` value to runner (`Readings/Run.runLower` and the mains).
    `dispatch` itself is proved equivalent to `TodayList`, to the frozen classifier and to
    Python (exhaustive `#guard`), but no theorem ties a route to a feature soundness
    theorem.

## 6. Statement-level duplication

### 6.1 The logic itself

| Notion | Copies | Relation |
|---|---|---|
| `Formula`, `WellFormed`, `check`, `denote`, `eval`, `Entails`, `countermodelCheck` | `VE`, `VE.Closure`, `VE.Core`, `VE.Order` (plus the tagged `Time` layer) | `Closure.conservativity` (v0 ⊂ closure); `Core.embedClosure_denote` and `entails_closure` (closure ⊂ core); `Order.entails_v0`, one direction only, with no converse; nothing relates Order and Core. `Time`: `units_faithful` (good). |
| `Path`, `Kind`, `Reachable`, `warshall` | `Closure/Paths`, `Core/Paths` (identical except for the namespace) | `path_iff`, `reachable_iff` |
| Tableau checker | v0 (`VE/Tableau*`); closure (`VE/TableauExtended*`); core (`Core/TableauExtended*`); order (`Order/Tableau`, 985 lines) | Each is proved sound separately; nothing relates them. `VE/TableauClosure` and `VE/TableauExtendedClosure` are textual copies over different `Formula` types. |
| Path rules, induction, round trip | `Closure/{PathRules,Induction,Consequence,RoundTrip}` = `Core/…`; `VE/TableauExtended{,Rules,Extra,Induction}` = `Core/TableauExtended…` | Identical text, re-proved over a different type. `Core/NARY.md` admits the copy. |
| Budgeted evaluators | `Route/Budget` `evalF`, `evalC`, `evalN`; `Time/Budget.evalB` | Each has its own `*_sound` theorem. |

The checker copies add proof, not trust. The definition copies add trust: a reviewer has
to accept three or four definitions of `denote` and `Entails`.

### 6.2 Statement and wire scaffolding

| Notion | Where it is defined | Theorem relating the copies |
|---|---|---|
| Admission skeleton (`LayerLeaf`, `ProfileLeaf`, `NodeAdmitted`, `admitNodes`, `SourceDecoded`, `CertificatesBound`, `otherAssumptions`, `AdmissionAnswer`) | `Route/Admission`, `Norms`, `NormDefaults`, `SoftNorms`, `Rights`, `Alternatives`, `Risk` (an almost verbatim copy of Alternatives), `Time/Document`, `Attribution/Admission` | none |
| `decodeDoc` | `Route/Admission`; copied verbatim as `SoftNorms.decodeSoftDoc` and `NormDefaults.decodeFilledDoc` | none |
| Conflict-target check plus its `_target` lemma | `Norms/Replay`, `Norms/Flagged`, `NormDefaults/Wire`, `SoftNorms/Coherence`, `Rights/Route`, `Alternatives/Background`, `Risk/Background` | each proved separately |
| Two notions of norm conflict | `Norms/Conflict.ConflictFree` vs `Norms/Flagged.BaseConflictFree` | **none** |
| Layer chain (`*SymLayer`, `*Chain`, `*RouteChain`) | `Norms/Layer`, `SoftNorms`, `Rights/Route`, `Alternatives/Route`, `Compose/Slot` | each re-proved |
| `decodePackage`, `replayEntailment`, witness decoding | `Norms/Replay`, `Norms/Flagged`, `NormDefaults`, `SoftNorms`, `SpeechActs`, `Alternatives`, `Risk` | none |
| Definition premises (`hide`, `forget`, `iff`, `premise`) | `Definitions/Layer` and `Norms/Basic` (verbatim) | none |
| Followability formulas | `Alternatives/Followable` and `NormDefaults/Routes` | none |
| Profile-word inliner | `Alternatives/Decl` and `Risk/Decl` (line for line) | none |
| Functional and pairwise-distinct premises | `Data/Background`, `Route/Background`, `Risk/Background` (`classFunctional`, `lowerPairs`), `Alternatives.ownPremise` | none |
| `disjunction` of readings | `Route/Admission`, `Service/Readings`, `GenericReadings`, `FamilyBundle`, `Time/Document.qdisjunction`, `Discourse/Joint.disj` | `independent_shortcut` (Joint vs Route only) |
| Claim graph | `VE/ClaimGraph` and `Service/GenericGraph` (a full copy); three `CertificateSound` definitions | `graph_certificateSound_iff` (Route only) |
| Readings choice checking | `Route.ReadingChoices`, `Service/Readings`, `GenericReadings`, `Family.fol_readings_*` | none |
| Lemma bundles | `Definitions/Bundle` and `Service/FamilyBundle`, with different background semantics | none |
| English grammar and meaning | `English.Tree`/`denote` and `Discourse.STree`/`coreFormula` | none; only `presentation_expands` bridges them |
| Rights slot route proofs | `Rights/Route` and `Compose/Slot` | `rights_*_is_slot` (by `rfl`); about 350 lines of re-proof |
| Formula decoders | `Bridge`, `Closure/Bridge`, `Core/Bridge`, `Order/Wire`, `Norms/Wire.budgetFormula` | none |
| Formula encoders | `Route/Wire.encodeFormula`, `Standalone.encodeClosure`/`encodeCore`, `EnglishRun.encodeFormula`, `Order/Surface.formulaJson`, `Time/Wire.encCore` | none; no round trip for any of them |
| Trace decoders | `CertificateWire.decodeTrace`, `decodeClosureTrace`, `Core/Wire.decodeTrace` | none |
| SHA-256 | `CertificateWire.sha256`, `Service/Protocol.Sha256.digest` | `#guard` on 130 strings |
| Certificate binding | `Route/Wire.bindingOk`, `Family.legacyIds`, `Graph.legacyCtx`, `Standalone.legacy*Id` | none |
| Limits | `maxNodes = 10000` is defined at least six times; `Route/AstLimit`, `Wire.nodeLimit`, `Steps`, `Decode`, `Budget` and `WireContract.Limits` each have their own | none |

## 7. Candidates to shrink the trusted base

Ordered by how much trusted text each would remove or turn into a stated tie. The line
figures come from the readers' estimates.

1. **Make Lean the default authority.** Everything in sections 4 and 5 only becomes the
   *gate* for the Python-authority operations when `VE_AUTHORITY=lean`. This is
   configuration and process work, not proof work, and Gate 2 is already met
   (`docs/spec/stage2-progress.md`). It is listed first because it changes what the rest
   of this map protects.
2. **One logic with profiles.**
   * Route closure certificates through the Core checker, using its compound and
     induction flags. Delete `VE/TableauExtended*` and `Closure/{Paths,PathRules,
     Induction,Substitution,Congruence,Finite}`, about 2,000 lines. Closure soundness then
     follows from `Core.Tableau.checkCertificate_sound` plus `entails_closure`.
   * Define `Closure.Formula` as atom-free `Core.Formula`.
   * For Order, either parameterise core over a term theory or at least prove the converse
     of `entails_v0`, so that v0 ⊂ order is an iff.
   * This removes two of the four `denote`/`Entails` definitions a reviewer must read.
3. **One wire-acceptance theorem per runner.**
   * Merge `runFol`, `runClosure` and `runOrder` over `Route.Checker`. Prove a single
     acceptance theorem as `Core.Wire.run_certificate_acceptance` does, and make
     `fullBackground` one `Layer` with `BackgroundSound`.
   * Then add short corollaries for the rest of section 5.1: Order and Time `runCase`,
     `runBundle`, the risk CONFLICT, DILEMMA and certificate paths, family-norms
     CONFLICT-FREE, and `Core/Layers`. These remove no code; they turn [V]-trusted glue
     into stated ties.
4. **Use the decoding hypotheses.** Add a `decode j = .ok r.src` conjunct to the theorems
   in section 5.2, following the norms and soft-norms pattern.
5. **Formula codec round trips.**
   * Keep one encoder per logic and prove `decodeFormula (encodeFormula a) = .ok a` up to
     the depth bound, for v0, closure, core and order. Do the same for traces and for
     `Time/Wire.elabFormula ∘ encQ`.
   * The regenerated, hashed text then becomes the artifact the reviewer reads, and the
     decoders drop out of the trusted base for well-formed input.
   * Add string round trips for `parseIso`/`iso` and `parseDecimal`/`Dec.toString`;
     W6A-STATUS.md already claims them.
6. **A statement-layer kit.**
   * Write one admission module parameterised by (`Doc`, extra leaf predicate, generated
     premises, environment JSON). Add one `conflictFreeCheckWith`, one layer-chain
     builder, one `decodePackage`/`replayEntailment`, and one generic `disjunction` and
     readings check.
   * Instantiate them for Norms, NormDefaults, SoftNorms, Rights, Alternatives, Risk,
     `Time/Document` and Reports.
   * This removes six or seven copies of the admission *statements* (`NodeAdmitted`,
     `SourceDecoded`, …) that a reviewer otherwise reads per feature. The readers estimate
     1,000 to 1,500 lines.
7. **Norms.**
   * Delete `Replay.replayConflict`, `replayWitness` and `replayEntailment`, which nothing
     calls, or define them as `Flagged` with `flags = false`.
   * Either prove `BaseConflictFree → ConflictFree` on structures that satisfy the flags,
     or define `pyTargets` by definition expansion with a faithfulness lemma.
   * Replace the `Norms.Definition` copy with `Definitions.Def`.
   * Parameterise the Alternatives inliner by a word table and use it for Risk (about 120
     lines).
8. **Be honest about the direct semantics.**
   * Rights: either declare `correlate` the meaning (S-by-elaboration) and drop
     `ValueRight` and the `*X` layer (about 340 lines), or make `ValueRight` independent of
     `nodeOf` and `limPack`.
   * Discourse: either give `Acc` an independent specification, or document that it is
     code-as-spec. Remove the identity `canonTarget`/`AliasEq` layer (about 70 lines).
   * Definitions/Bundle: replace the code-as-spec `ReadingCompatible`/`LeafBound` with
     propositions plus iff lemmas, as `Time/Document` already does.
9. **One English grammar.** Express the discourse `STree` as an extension of `English.Tree`
   (or prove they agree on shared productions), so there is one English meaning function
   to review.
10. **Remove dead and unreached code.**
    * `Core.Bridge.runCase` and `runCaseReported`: no Lean caller.
    * `Compose/Slot.lean`: no executable calls it, and it re-proves Rights.
    * `Readings/Lines.lean`: about 690 proof lines. No theorem or gate consumes
      `genKeys_nodup`, and `linesOnce` is not part of `WellFormedDoc`.
    * `Rights.Projections.owes` and `free`; `Readings` `Coupling` and `Narrowing`;
      `AchievesQuiet`.
    * `Definitions/Alias.lean`: no runtime use was found (?).
    * `SurfaceProofs.lean`, which `RoundTrip.parse_print` subsumes.
11. **One SHA-256, one limits module, one profile registry.** Generate them, as
    `WireContract/Names` and `Limits` already are.
12. **Separate reject-only code.** Move diagnostics into modules marked "not
    soundness-relevant", so a reviewer can skip them without reading them: SoftNorms
    `Phases`, `checkW1` and the size tables; `Norms/Tree.check`; SpeechActs `checkSpeech`;
    `WireContract`. The base does not shrink, but the reading load does.

## 8. What depends on Python and Rust

### 8.1 Authority

| Component | Default status | Under `VE_AUTHORITY=lean` |
|---|---|---|
| Strict surface parse, typing, evaluation, certificate replay, countermodel check, graph, readings, bundles, core admission (`ve/parser.py`, `ve/ast.py`, `ve/evaluate.py`, `ve/entailment.py`, `ve/admission.py`) | **Trusted Python** | Lean decides (`parse_print`, `check_iff_wellFormed`, `eval_iff_denote`, `checkCertificate_sound`, `admit_report_sound`, …) |
| Statement-layer routes (norms, norm defaults, soft norms, rights, risk, alternatives, reports, readings, discourse `@2`, quantity) | Lean only; Python forwards the case (`ve/alternatives.py:27` refuses rather than answer in Python) | same |
| Combination rules (`equivalence.compare`, `vacuity`, readings coupled sets, `argument.py` reachability) | Trusted Python | Trusted Python (manifest class C) |
| `_check_conclusions` (`ve/english.py:1699`), "Therefore" markers | Trusted Python prover and replay in every mode | same (`entailment.py:591,607,685`) |
| Proof and model search (`prove_entailment`, `search.find_countermodel`, `rust/ve-core`) | Untrusted; output replayed (in Python by default) | Untrusted; Lean re-checks each witness |
| `rust/ve-core` under `rust-experimental` | Trusted, unverified evaluate and countermodel verdicts (not a gate authority) | – |
| Backend adapters (`ve/backends/lean.py`, `validation.py`, `dispatch.py`) | Trusted adapter; fails closed (Lean accepts but Python rejects → `CheckerUnavailable`) | same |
| Assurance records (`ve/check.py`, `assurance.py`) | Bookkeeping: records say `proof: not_checked`, `intent: unconfirmed` | same |

### 8.2 The one-reading property

What gates acceptance today is `require_unique_derivation` (`ve/surface/unambiguity.py`).
For each input, it runs a Lark Earley parse with `ambiguity="explicit"` over a separate
"context-free syntax envelope" grammar (`english_lark_grammar`), and rejects the input if
any `_ambig` node appears. This guarantee rests on four things:

* **Lark itself.** The assumption is that explicit-ambiguity Earley reports every
  ambiguity. This is assumed, not proved.
* **A design argument.** The Lark grammar is claimed to over-approximate the hand-written
  `EnglishParser`. Nothing checks this mechanically for core constructs; only registry
  extensions are tied to the Earley tree, by `require_correspondence`.
* **The hand parser.** It produces the AST that is actually used, so its output, not the
  Earley tree, defines the meaning.
* **Tests.** `conformance/english_surface.py` has about 85,000 AST round trips with Earley
  audits, and there is `tests/test_english_unambiguity.py`.

On the Lean side:

* **What is proved.** `VE/English/Proofs.lean` proves `core_unique_derivation`,
  `core_parse_sound`, `core_parse_render` and `core_render_injective`, plus their
  `checked_*` corollaries.
* **Scope.** These cover the core productions (connectives, lists, `for every`,
  `there is`), predicates of arity at most 2, and *token lists*, not strings. They assume
  `Admitted L`; `admissible` decides it soundly. Three of the 17 benchmark vocabularies
  fail it, yet Python accepts their texts.
* **Not covered:** lexing, contractions, validated negatives, closure, order, n-ary
  templates, definitions sugar, norm and soft blocks.
* **How it relates to Python.** Agreement with Python on the core fragment is a
  differential test (`conformance/english_lean.py`, 85,000 pairs, 0 failures). No Lean
  admission path parses English with this grammar.
* **The discourse exception.** For `@2` discourse slots, Lean lexes unit bytes and
  enumerates all derivations of its small reference grammar (`mem_derivs`). Even there,
  the lexer and slot discovery are trusted (section 5.3), and
  `discourse_uniqueDerivation` ranges only over derivations that already passed
  validation. It restates `Accepted`'s uniqueness clause rather than proving the grammar
  unambiguous.

Ordinary units: Lean never checks that a unit's prose matches its formula. Lean's loader
accepts AST content only. The exception is bound discourse units, whose content must equal
the elaboration.

### 8.3 The meaning of an English sentence

The English → formula map is defined by Python's `EnglishParser` and the
`EnglishVocabulary` templates (user verbalisations and reviewed overlays). Lean checks the
AST it is given. METATHEORY.md lists "P7 source-to-proposition correspondence … human
interpretation" as outside every theorem. The English shown to users is checked only by
Python re-parsing it.

Steps that would move this trust into Lean, cheapest first:

1. Under Lean authority, call the existing `english` service mode from `parse_english` and
   fail closed unless the Lean parse equals Python's AST.
2. Move tokenisation into Lean, so the theorems apply to strings.
3. Run `admissible L` when a vocabulary is admitted.
4. Derive the Python AST from the Earley tree rather than the hand parser.
5. Extend the Lean grammar to the full surface, generating the Lark grammar and the Lean
   `Tree` from one specification.

## 9. Method and limits

* **How the classification was done.** Ten read-only passes, nine over Lean module groups
  and one over Python and Rust. Each read the files and assigned every declaration a
  class. Each D, G and C item was checked against the statement of the theorem claimed to
  tie it, to confirm the theorem mentions that function.
* **Line counts.** Per declaration span, from the docstring to the line before the next
  declaration. Theorems count as P; imports, namespaces and module comments as o. Expect
  about ±10% per class. The `Core/` row sums to about 50 lines under its file total. The
  WireContract tables understate their size: a single line in `Tables/SoftNorms.lean` is
  about 25 KB.
* **Checked again by hand.** These claims were re-checked directly:
  * `VE_AUTHORITY` defaults to `python`, and 2 of 26 manifest operations are Lean-only.
  * `readings_wire_separate_sound` and `speech_wire_conflict_free_sound` never use `h`.
  * `Acc := accB … = true`.
  * `Norms/Run` calls only `Flagged.*`, and `Replay.replay*` has no caller.
  * `norms_flagged_conflict_sound` concludes `BaseConflictFree` when `plain = false`.
  * No theorem names `runFol`, `runClosure` or `runOrder`.
  * `Core.Bridge.runCase` has no Lean caller.
  * `Risk/Run.runCertificate` returns `checkCertificate` directly.
  * `runBundle` uses `fullBackground`.
  * `Order.entails_v0` is one-directional.
  * There is a second SHA-256 implementation.

  Items marked "(?)" were not re-checked. The rest relies on the readers' reports.
* **"Unused hypothesis" means the proof term ignores it.** The theorem is still true. The
  finding is about what it states, not whether it is correct.
* **Not audited:** Python internals beyond the authority and English paths; the generated
  WireContract tables; the content of `Iceberg.lean`.

## 10. Doc-vs-code discrepancies

Each of these should be fixed in the docs or the code. None is a proof error.

* **lean/README.md**
  * Line 310 says certificate replay "explicitly rejects" closure. In the code,
    `ve.core@0.1` goes to `runClosureCase`; CLOSURE.md is correct.
  * Theorem counts are stale: "25 source files, 110 theorems" against about 2,960
    `#print axioms` lines.
  * It never mentions `VE.English`, rights, reports, soft norms or speech acts. Its "Grammar
    P1–P3 remain unproved" predates the core English theorems.
* **NORMS.md**
  * Lines 154–157 say the route "rejects … definitions or flags". It accepts both,
    through `Flagged`.
  * It cites the `Replay.norms_wire_*` theorems for the public kinds, but the public kinds
    run the `norms_flagged_*` path.
  * It omits the `BaseConflictFree` caveat, the `hflags` hypothesis, and the files
    `Admission`, `Flagged` and `Plain`.
* **RISK.md and `Risk/Run.lean`**
  * They describe DILEMMA, CONFLICT-by-witness, `risk-certificate` and the statuses as
    certified. See section 5.1.
  * The `Risk/Decl.lean` docstring places checks in the wire decoder that are actually in
    `checkRiskBlock`.
* **READINGS.md**
  * It describes `readings_wire_separate_sound` as being about a decoded replay; the decode
    hypothesis is unused.
  * It is silent on `actOnly`.
  * It lists fixtures K1–K22, but K22 is absent.
* **COMPOSE.md:11** says "no executable calls anything here". `ve_readings_route` calls
  `Compose.dispatch`.
* **SOFT-NORMS.md**
  * It omits `Phases.lean`.
  * Its description of `conditional_on` ("replaced by ⊤") differs from the cumulative
    algorithm, and it does not list `conditional_on` or `soft-pairs` as unproved.
* **SPEECH-ACTS.md** describes the `speech_wire_*` theorems as being about "a replay"
  (section 5.2).
* **DISCOURSE.md**
  * It calls `Acc` "an independent relation" and says `Intended` "never mentions the
    elaboration". Both are false (section 4.2).
  * The name `discourse_uniqueDerivation` suggests an unambiguous grammar (section 8.2).
* **RIGHTS.md**
  * It calls `ValueRight` "the direct semantics" (section 4.2).
  * It omits `Admission.lean`, and lists `owes` and `free`, which are unused.
* **REPORTS.md** says every theorem holds at every universe. Three Run theorems are at
  universe 0.
* **Definitions and Bundle docs:** METATHEORY.md:496 and `Definitions/STATEMENTS.md` say
  `bundle_sound` covers `runBundle`. It does not cover flags.
* **W6A-STATUS.md and units-schema.md** claim decimal and calendar string round trips.
  Only the `Dec`/`Civil`-level inverses are proved.
* **`Core/Layers.lean` and `Route/Background.lean` docstrings**
  * They claim end-to-end soundness, and "literals only".
  * `fullBackground` emits flags and definitions too.
* **`docs/spec/wire-contract.md`** names `lean/VE/Contract/…`; the code is in
  `lean/VE/WireContract/`.

## 11. Per-module line counts

Columns: total, K, S, D, G, C, P, T, o. A dash means 0.

**VE/ (kernel)**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Syntax | 68 | 39 | – | – | – | 15 | – | – | 14 |
| Semantics | 90 | 53 | – | – | – | – | 19 | – | 18 |
| Typing | 45 | – | – | – | – | – | 40 | – | 5 |
| Finite | 96 | 15 | – | – | – | 24 | 43 | – | 14 |
| Consequence | 82 | – | – | – | – | 5 | 64 | – | 13 |
| ClaimGraph | 339 | – | 67 | – | – | 49 | 179 | – | 44 |
| Tableau | 199 | – | – | – | – | 63 | 106 | – | 30 |
| TableauClosure | 260 | – | – | – | – | 63 | 168 | – | 29 |
| TableauChecker | 196 | – | – | – | – | 43 | 138 | – | 15 |
| TableauExtended | 209 | – | – | – | – | 72 | 106 | – | 31 |
| TableauExtendedClosure | 260 | – | – | – | – | 63 | 168 | – | 29 |
| TableauExtendedRules | 106 | – | – | – | – | 20 | 72 | – | 14 |
| TableauExtendedExtra | 183 | – | – | – | – | 50 | 114 | – | 19 |
| TableauExtendedInduction | 53 | – | – | – | – | 14 | 31 | – | 8 |
| TableauExtendedChecker | 264 | – | – | – | – | 57 | 189 | – | 18 |
| CertificateWire | 236 | – | – | 153 | 33 | 4 | 8 | 5 | 33 |
| Json | 136 | – | – | 119 | – | – | – | – | 17 |
| Bridge | 282 | 2 | – | 186 | 34 | 16 | – | – | 44 |
| Surface | 188 | – | – | 156 | – | – | 7 | – | 25 |
| SurfaceProofs | 197 | – | – | – | – | – | 190 | – | 7 |
| RoundTrip | 423 | – | – | – | – | – | 415 | – | 8 |
| LexicalProofs | 151 | – | – | – | – | – | 145 | – | 6 |
| ParserContracts | 60 | – | – | – | – | – | 55 | – | 5 |
| EnvironmentProofs | 33 | – | – | – | – | – | 28 | – | 5 |
| ModelProofs | 80 | – | – | – | – | – | 74 | – | 6 |
| EvaluationCounts | 119 | – | – | – | – | – | 100 | – | 19 |
| Checks | 94 | – | – | – | – | – | – | 88 | 6 |
| GraphChecks | 73 | – | – | – | – | – | 5 | 62 | 6 |
| TableauChecks | 26 | – | – | – | – | – | – | 21 | 5 |
| Audit | 3,127 | – | – | – | – | – | – | 2,990 | 137 |

**Closure/ and Core/** (where a module exists in both, the Closure row comes first)

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Paths (each) | 195 | 12 | – | – | – | 16 | 143 | – | 24 |
| Syntax | 197 / 209 | 59 / 63 | – | – | – | 47 / 51 | 73 / 77 | – | 18 / 18 |
| Finite | 120 / 126 | – | – | – | – | 34 / 37 | 73 / 76 | – | 13 / 13 |
| Consequence (each) | 28 | 5 | – | – | – | 3 | 13 | – | 7 |
| Substitution | 190 / 198 | – | – | – | – | 38 / 39 | 133 / 140 | – | 19 / 19 |
| Congruence | 105 / 131 | – | – | – | – | 24 / 29 | 71 / 90 | – | 10 / 12 |
| PathRules (each) | 103 | – | – | – | – | 8 | 86 | – | 9 |
| Induction (each) | 75 | – | – | – | – | 8 | 60 | – | 7 |
| Surface | 165 / 186 | – | – | 148 / 167 | – | – | – | – | 17 / 19 |
| RoundTrip (each) | 71 | – | – | – | – | – | 65 | – | 6 |
| Bridge | 99 / 159 | – | – | 44 / 101 | 39 / 40 | – | – | – | 16 / 18 |
| Checks | 33 / 54 | – | – | – | – | – | – | 26 / 47 | 7 / 7 |
| Core/Conservativity | 79 | – | – | – | – | 18 | 50 | – | 11 |
| Core/Route | 58 | 8 | – | – | – | 11 | 27 | – | 12 |
| Core/Wire | 166 | – | – | 46 | 41 | – | 60 | – | 19 |
| Core/Layers | 128 | – | – | 34 | 52 | – | – | – | 42 |
| Core/TableauExtended | 209 | – | – | – | – | 72 | 106 | – | 31 |
| Core/TableauExtendedClosure | 313 | – | – | – | – | 71 | 213 | – | 29 |
| Core/TableauExtendedRules | 106 | – | – | – | – | 20 | 72 | – | 14 |
| Core/TableauExtendedExtra | 183 | – | – | – | – | 50 | 114 | – | 19 |
| Core/TableauExtendedInduction | 53 | – | – | – | – | 14 | 31 | – | 8 |
| Core/TableauExtendedChecker | 263 | – | – | – | – | 56 | 189 | – | 18 |

**Order/, Time/, Definitions/, Data/**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Order/Syntax | 90 | 66 | – | – | – | 16 | – | – | 8 |
| Order/Typing | 46 | – | – | – | – | – | 41 | – | 5 |
| Order/Semantics | 110 | 62 | – | – | – | – | 41 | – | 7 |
| Order/Finite | 113 | 18 | – | – | – | 31 | 56 | – | 8 |
| Order/Consequence | 28 | 4 | – | – | – | 4 | 14 | – | 6 |
| Order/Conservativity | 122 | – | – | – | – | – | 114 | – | 8 |
| Order/ModelCheck | 170 | – | – | 9 | – | 45 | 100 | – | 16 |
| Order/Linear | 201 | – | – | – | – | 37 | 151 | – | 13 |
| Order/Tableau | 985 | – | – | – | – | 281 | 689 | – | 15 |
| Order/Gate | 33 | – | – | – | – | – | 12 | 15 | 6 |
| Order/ProfileGate | 291 | – | – | – | 13 | – | 257 | – | 21 |
| Order/Checks | 83 | – | – | – | – | – | – | 75 | 8 |
| Order/TableauChecks | 114 | – | – | – | – | – | – | 105 | 9 |
| Order/Surface | 220 | – | – | 156 | 53 | – | – | – | 11 |
| Order/Wire | 292 | – | – | 202 | 55 | 8 | 5 | – | 22 |
| Order/WireGate | 88 | – | – | – | – | – | 74 | – | 14 |
| Time/Calendar | 526 | – | 55 | 29 | – | 29 | 395 | – | 18 |
| Time/Syntax | 437 | 95 | – | – | – | 85 | 233 | – | 24 |
| Time/Semantics | 636 | 85 | 17 | – | – | – | 511 | – | 23 |
| Time/Count | 260 | – | – | – | – | 52 | 190 | – | 18 |
| Time/Decimal | 161 | – | 15 | 43 | 2 | 6 | 80 | – | 15 |
| Time/Budget | 329 | – | – | – | 3 | 67 | 241 | – | 18 |
| Time/Document | 615 | – | 117 | 117 | 41 | 81 | 212 | – | 47 |
| Time/Wire | 863 | – | – | 514 | 186 | 49 | 69 | – | 45 |
| Definitions/Alias | 60 | – | 3 | – | – | – | 47 | – | 10 |
| Definitions/Elaborate | 128 | – | – | – | 10 | 44 | 56 | – | 18 |
| Definitions/Layer | 475 | – | 36 | – | – | 24 | 383 | – | 32 |
| Definitions/Route | 160 | – | 5 | – | – | 3 | 139 | – | 13 |
| Definitions/Bundle | 471 | – | 14 | 28 | 29 | 130 | 239 | – | 31 |
| Data/Background | 172 | – | 32 | – | – | 20 | 111 | – | 9 |

**Route/, WireContract/, Service/**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Route/Wire | 666 | – | 6 | 296 | 156 | 39 | 130 | – | 39 |
| Route/Admission | 697 | – | 162 | 214 | 51 | 48 | 184 | – | 38 |
| Route/Budget | 1,052 | – | – | – | 8 | 284 | 723 | – | 37 |
| Route/Closure | 481 | – | – | – | – | 72 | 392 | – | 17 |
| Route/Flags | 192 | – | – | – | – | 27 | 154 | – | 11 |
| Route/Decode | 282 | – | – | 104 | 16 | 49 | 86 | – | 27 |
| Route/Route | 229 | – | 38 | – | 7 | 34 | 122 | – | 28 |
| Route/Layer | 227 | 19 | 90 | – | – | – | 81 | – | 37 |
| Route/Checker | 148 | 42 | – | – | – | 33 | 54 | – | 19 |
| Route/Background | 304 | – | 54 | – | 6 | 10 | 210 | – | 24 |
| Route/Gate | 213 | – | 9 | 25 | 46 | 18 | 96 | – | 19 |
| Route/Run | 188 | – | – | 12 | 113 | – | 30 | – | 33 |
| Route/Steps | 73 | – | – | – | 56 | – | – | – | 17 |
| Route/AstLimit | 124 | – | – | – | 79 | – | – | 24 | 21 |
| Route/Readings | 49 | – | 10 | – | – | – | 29 | – | 10 |
| Route/Examples | 202 | – | – | – | – | – | – | 188 | 14 |
| Route/Checks | 122 | – | – | – | – | – | – | 113 | 9 |
| WireContract/Engine | 536 | – | – | 161 | 264 | – | 86 | – | 25 |
| WireContract/Table | 116 | – | – | – | 103 | – | – | – | 13 |
| WireContract/Diagnose | 81 | – | – | – | 60 | – | – | – | 21 |
| WireContract/Names + Limits | 20 | – | – | – | 12 | – | – | – | 8 |
| WireContract/Tables/* | 36 | – | – | – | 4 | – | – | 24 | 8 |
| WireContract/Hooks/Corpus | 63 | – | – | – | – | – | – | 50 | 13 |
| WireContract/Hooks/SoftNorms | 221 | – | – | – | 193 | – | – | 1 | 27 |
| Service/Protocol | 535 | – | – | 234 | 171 | – | 69 | 11 | 50 |
| Service/Standalone | 600 | – | 9 | 258 | 314 | – | – | – | 19 |
| Service/Family | 817 | – | 5 | 74 | 421 | 65 | 204 | – | 48 |
| Service/FamilyBundle | 500 | – | 17 | 43 | 78 | 113 | 215 | – | 34 |
| Service/FamilyNorms | 244 | – | – | 15 | 112 | 38 | 43 | – | 36 |
| Service/Graph | 255 | – | – | 82 | 115 | – | 18 | – | 40 |
| Service/GenericGraph | 282 | 5 | 28 | – | – | 82 | 150 | – | 17 |
| Service/GenericReadings | 137 | – | 14 | – | – | 8 | 95 | – | 20 |
| Service/Readings | 215 | – | 11 | 10 | 52 | 18 | 97 | – | 27 |
| Service/EnglishRun | 134 | – | – | 67 | 24 | 14 | – | – | 29 |
| Service/TypingDiagnostic | 208 | – | – | – | 191 | – | – | – | 17 |

**English/, Discourse/**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| English/Check | 543 | – | – | – | – | 66 | 464 | – | 13 |
| English/ClauseProofs | 171 | – | – | – | – | – | 162 | – | 9 |
| English/Grammar | 118 | – | 30 | 54 | – | – | – | – | 34 |
| English/Lexicon | 150 | – | 17 | 114 | – | – | – | – | 19 |
| English/Parse | 152 | – | – | 137 | – | – | – | – | 15 |
| English/ParseProofs | 415 | – | – | – | – | – | 404 | – | 11 |
| English/Proofs | 187 | – | – | – | – | – | 162 | – | 25 |
| English/Render | 82 | – | – | 62 | – | – | – | – | 20 |
| English/RenderProofs | 216 | – | – | – | – | – | 204 | – | 12 |
| English/Run | 137 | – | – | 67 | 45 | – | – | – | 25 |
| English/Statements | 83 | – | 43 | – | – | – | 13 | – | 27 |
| Discourse/Access | 668 | – | 260 | 76 | – | 18 | 290 | – | 24 |
| Discourse/Admission | 746 | – | 73 | 146 | 494 | – | – | – | 33 |
| Discourse/Descriptions | 156 | – | 14 | 7 | – | – | 122 | – | 13 |
| Discourse/Documents | 220 | – | 21 | – | – | – | 186 | – | 13 |
| Discourse/Elaborate | 416 | – | 102 | – | – | 50 | 244 | – | 20 |
| Discourse/English | 150 | – | 44 | 6 | – | – | 78 | – | 22 |
| Discourse/Examples | 77 | – | – | – | – | – | – | 65 | 12 |
| Discourse/Fusion | 65 | – | 5 | – | – | 26 | 20 | – | 14 |
| Discourse/Grammar | 580 | – | – | 238 | – | 49 | 258 | – | 35 |
| Discourse/Joint | 437 | – | 44 | – | – | 22 | 352 | – | 19 |
| Discourse/Loader | 557 | – | – | 523 | – | – | – | 9 | 25 |
| Discourse/Manifest | 279 | – | 148 | – | – | – | 111 | – | 20 |
| Discourse/Resolve | 802 | – | 13 | 60 | 6 | 183 | 522 | – | 18 |
| Discourse/Run | 207 | – | – | 41 | 116 | – | 24 | – | 26 |
| Discourse/Theorems | 1,123 | – | 10 | – | – | – | 1,098 | – | 15 |
| Discourse/WellFormed | 1,224 | – | 427 | 22 | – | – | 765 | – | 10 |
| Discourse/Wire | 297 | – | – | 270 | – | – | – | – | 27 |

**Readings/, Compose/**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Readings/Doc | 650 | – | 134 | – | 2 | 49 | 432 | – | 33 |
| Readings/Separate | 1,329 | – | 107 | – | – | 193 | 979 | – | 50 |
| Readings/Lines | 746 | – | 8 | – | – | 9 | 694 | – | 35 |
| Readings/Wire | 651 | – | – | 369 | 178 | 14 | 35 | – | 55 |
| Readings/Run | 217 | – | – | 28 | 136 | – | – | – | 53 |
| Readings/Examples | 327 | – | – | – | – | – | – | 285 | 42 |
| Compose/Content | 46 | – | 17 | 4 | 3 | – | 4 | – | 18 |
| Compose/Slot | 522 | – | 12 | – | – | 12 | 457 | – | 41 |
| Compose/Dispatch | 721 | – | 13 | – | 105 | – | 587 | – | 16 |
| Compose/Examples | 574 | – | – | – | – | – | – | 542 | 32 |

**Norms/, NormDefaults/**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Norms/Basic | 455 | 7 | – | – | – | 39 | 387 | – | 22 |
| Norms/Tree | 385 | 6 | 116 | – | 147 | 33 | 47 | – | 36 |
| Norms/Valid | 163 | – | – | – | – | – | 155 | – | 8 |
| Norms/Elaborate | 441 | – | 37 | – | – | 50 | 330 | – | 24 |
| Norms/Subst | 347 | 2 | – | – | – | 40 | 288 | – | 17 |
| Norms/Prefix | 471 | 1 | 46 | – | – | – | 406 | – | 18 |
| Norms/Conflict | 546 | – | 31 | – | – | 15 | 480 | – | 20 |
| Norms/Layer | 321 | – | 2 | – | – | 4 | 293 | – | 22 |
| Norms/SmallModel | 280 | 5 | 10 | – | – | – | 243 | – | 22 |
| Norms/Cedar | 127 | – | 9 | – | – | – | 106 | – | 12 |
| Norms/Checks | 277 | – | – | – | – | – | – | 262 | 15 |
| Norms/Examples | 141 | – | – | – | – | 19 | 40 | 62 | 20 |
| Norms/Wire | 314 | – | – | 290 | – | – | – | – | 24 |
| Norms/Replay | 393 | – | – | 53 | 6 | 109 | 184 | – | 41 |
| Norms/Flagged | 389 | – | 4 | 31 | 6 | 149 | 146 | – | 53 |
| Norms/Admission | 465 | – | 79 | 33 | 17 | 78 | 232 | – | 26 |
| Norms/Plain | 228 | – | – | 57 | 138 | – | – | – | 33 |
| Norms/Run | 214 | – | 29 | – | 100 | – | 34 | – | 51 |
| NormDefaults/Tree | 129 | – | 43 | – | – | 61 | – | – | 25 |
| NormDefaults/Dag | 324 | – | – | – | – | – | 309 | – | 15 |
| NormDefaults/Check | 543 | – | – | – | – | – | 528 | – | 15 |
| NormDefaults/Fill | 598 | – | – | – | – | – | 583 | – | 15 |
| NormDefaults/FillCheck | 597 | – | – | – | – | – | 582 | – | 15 |
| NormDefaults/Semantics | 132 | – | 22 | – | – | – | 94 | – | 16 |
| NormDefaults/Premises | 324 | – | 32 | – | – | – | 268 | – | 24 |
| NormDefaults/Status | 763 | – | 10 | – | – | – | 735 | – | 18 |
| NormDefaults/Evidence | 1,122 | – | 2 | – | 1 | 235 | 869 | – | 15 |
| NormDefaults/Routes | 164 | – | 38 | – | – | – | 99 | – | 27 |
| NormDefaults/Wire | 377 | – | – | 111 | 13 | 49 | 162 | – | 42 |
| NormDefaults/Replay | 371 | – | – | 29 | – | 184 | 118 | – | 40 |
| NormDefaults/Admission | 350 | – | 61 | 41 | 9 | 55 | 151 | – | 33 |
| NormDefaults/Run | 217 | – | 26 | – | 106 | – | 38 | – | 47 |
| NormDefaults/Examples | 178 | – | – | – | – | – | – | 165 | 13 |

**SoftNorms/, SpeechActs/** (C includes diagnostic-only checks that can only reject. The
soundness-relevant C is about 30 lines in Soften and about 70 lines in SpeechActs/Tree.)

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SoftNorms/Tree | 665 | – | 175 | – | – | 20 | 335 | – | 135 |
| SoftNorms/Soften | 809 | – | 114 | – | 196 | 237 | 123 | – | 139 |
| SoftNorms/Semantics | 1,172 | – | 94 | – | – | – | 902 | – | 176 |
| SoftNorms/Coherence | 862 | – | 36 | – | – | 15 | 664 | – | 147 |
| SoftNorms/RankProof | 185 | – | – | – | – | – | 160 | – | 25 |
| SoftNorms/Status | 70 | – | 4 | 7 | – | – | 34 | – | 25 |
| SoftNorms/Phases | 362 | – | – | 291 | 11 | – | – | – | 60 |
| SoftNorms/Wire | 462 | – | – | 135 | 68 | 55 | 109 | – | 95 |
| SoftNorms/Admission | 332 | – | 35 | 26 | 79 | – | 141 | – | 51 |
| SoftNorms/Run | 381 | – | 27 | 22 | 186 | 48 | 34 | – | 64 |
| SpeechActs/Tree | 359 | – | 135 | – | – | 127 | 27 | – | 70 |
| SpeechActs/Demand | 418 | – | – | – | – | – | 365 | – | 53 |
| SpeechActs/Answer | 336 | – | 33 | – | – | 4 | 245 | – | 54 |
| SpeechActs/Consequence | 223 | – | – | – | – | – | 178 | – | 45 |
| SpeechActs/Wire | 993 | – | 19 | 759 | – | – | 84 | – | 131 |
| SpeechActs/Run | 633 | – | – | 108 | 146 | 187 | 78 | – | 114 |

**Rights/, Attribution/**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Rights/Tree | 317 | – | 259 | – | – | – | 33 | – | 25 |
| Rights/Correlate | 564 | – | 292 | – | – | 116 | 110 | – | 46 |
| Rights/Semantics | 476 | – | 93 | – | – | – | 353 | – | 30 |
| Rights/Projections | 123 | – | 27 | – | – | – | 75 | – | 21 |
| Rights/Bar | 60 | – | – | – | – | – | 41 | – | 19 |
| Rights/Scope | 476 | – | 65 | 9 | 7 | 23 | 342 | – | 30 |
| Rights/Distinction | 74 | – | – | – | – | 26 | 33 | – | 15 |
| Rights/Route | 388 | – | – | – | – | 9 | 359 | – | 20 |
| Rights/Wire | 698 | – | – | 407 | 7 | 82 | 154 | – | 48 |
| Rights/Admission | 471 | – | – | 96 | 220 | 6 | 133 | – | 16 |
| Rights/Run | 387 | – | – | 77 | 195 | 8 | 60 | – | 47 |
| Rights/Examples | 405 | – | – | – | – | – | – | 384 | 21 |
| Attribution/Content | 726 | – | 545 | 73 | 15 | – | 61 | – | 32 |
| Attribution/Semantics | 82 | – | 70 | – | – | – | – | – | 12 |
| Attribution/Facts | 336 | – | – | – | – | – | 320 | – | 16 |
| Attribution/Elaborate | 433 | – | – | – | – | – | 421 | – | 12 |
| Attribution/Conservative | 351 | – | – | – | – | – | 337 | – | 14 |
| Attribution/Structure | 210 | – | – | – | – | – | 198 | – | 12 |
| Attribution/Route | 120 | – | – | – | – | – | 110 | – | 10 |
| Attribution/Scoped | 114 | – | – | – | – | – | 102 | – | 12 |
| Attribution/Assess | 86 | – | – | – | – | – | 76 | – | 10 |
| Attribution/Bridge | 251 | – | 9 | 39 | 16 | – | 173 | – | 14 |
| Attribution/Status | 110 | – | – | – | 44 | – | 52 | – | 14 |
| Attribution/Admission | 327 | – | 13 | 36 | 39 | 46 | 171 | – | 22 |
| Attribution/Wire | 510 | – | – | 413 | 65 | – | – | – | 32 |
| Attribution/Run | 542 | – | – | 67 | 153 | 104 | 158 | – | 60 |

**Risk/, Alternatives/**

| Module | Tot | K | S | D | G | C | P | T | o |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Risk/Cond | 456 | – | 85 | – | – | 72 | 261 | – | 38 |
| Risk/Derive | 820 | – | – | – | – | 63 | 727 | – | 30 |
| Risk/Decl | 357 | – | 238 | – | 2 | 19 | 70 | – | 28 |
| Risk/Severity | 19 | – | – | – | – | – | 11 | – | 8 |
| Risk/Words | 304 | – | 3 | – | – | – | 271 | – | 30 |
| Risk/Background | 960 | – | 59 | – | 5 | 14 | 842 | – | 40 |
| Risk/Record | 1,266 | – | 426 | 284 | 21 | 136 | 322 | – | 77 |
| Risk/Report | 330 | – | 62 | – | 4 | 79 | 156 | – | 29 |
| Risk/Piecewise | 1,386 | – | – | – | – | – | 1,341 | – | 45 |
| Risk/Audit | 190 | – | 63 | – | 36 | 21 | 39 | – | 31 |
| Risk/Wire | 487 | – | 4 | 353 | 73 | – | – | – | 57 |
| Risk/Admission | 128 | – | 12 | – | 82 | – | 13 | – | 21 |
| Risk/Run | 651 | – | 11 | 53 | 452 | – | 95 | – | 40 |
| Alternatives/Decl | 280 | – | 209 | – | 3 | 23 | 15 | – | 30 |
| Alternatives/Inline | 319 | – | – | – | – | – | 297 | – | 22 |
| Alternatives/Background | 381 | – | 55 | – | 5 | 15 | 276 | – | 30 |
| Alternatives/Route | 283 | – | – | – | – | – | 268 | – | 15 |
| Alternatives/Followable | 388 | – | 42 | – | – | – | 321 | – | 25 |
| Alternatives/Validate | 402 | – | 25 | – | 131 | 68 | 148 | – | 30 |
| Alternatives/Examples | 285 | – | – | – | – | – | – | 265 | 20 |
| Alternatives/Wire | 296 | – | – | 195 | 71 | – | – | – | 30 |
| Alternatives/Replay | 328 | – | – | 90 | 82 | – | 105 | – | 51 |
| Alternatives/Admission | 133 | – | 14 | – | 86 | – | 14 | – | 19 |
| Alternatives/Run | 317 | – | 11 | – | 243 | – | 28 | – | 35 |

**Top-level `lean/*.lean`**

| Module | Tot | G | T | o | Note |
|---|---:|---:|---:|---:|---|
| Main | 36 | 27 | – | 9 | conformance executable |
| Serve | 21 | 15 | – | 6 | service entry point |
| ResponseDecode | 677 | 11 | 625 | 41 | test oracle; re-implements `Graph.check` and `Unfolds` over JSON, with no theorem |
| RiskEvalMain | 61 | – | 48 | 13 | differential harness; does not check `Box.WF` |
| QuantityMain, DiagnoseMain, ten 4-line `*Main` | 51 | 23 | – | 28 | delegators |
| VE | 49 | – | – | 49 | imports only |
| Iceberg | 301 | – | – | – | standalone physics model, not part of VE |
