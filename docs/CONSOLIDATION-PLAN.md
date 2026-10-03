# Consolidation plan: a small core, shared kits, stated ties

Status: plan only, no code changes. Branch `design/consolidate` at `a093a14d` (main), 2026-10-03.

Inputs: `docs/TRUST-MAP.md` (branch `docs/trust-map`, `a18a86e6`) and its cross-family check
(`manage-agents/trustmap-check.final.md`); `docs/ARCHITECTURE-LAYERS.md` and
`ARCHITECTURE-LAYERS-PLAN2.md` (`design/layers2`); `docs/spec/wire-contract-PLAN.md`, `-S4-PLAN.md`,
`-S5-PLAN.md` (`design/wire-s5`); `docs/spec/composition-PLAN.md`, `-S2-PLAN.md`
(`compose-s2/integrate`); `docs/spec/english-lean-PLAN.md` (`design/english-lean`). The claims this
plan depends on most (section 3, steps 1 and 2) were re-read in the Lean sources.

Goal (lead): the trusted surface grows with every feature. Consolidate it into a small core with
shared abstractions, so VE is easier to review, trust, maintain and extend.

## 0. Summary

Order of work. Steps 1 to 4 are in the order the DRI fixed on 2026-10-03; the rest are ranked by
trusted lines removed or tied per day of effort, discounted by risk (section 4).

| # | Step | What it does to the trusted surface |
|---|---|---|
| 0 | Measurement tooling | Makes every later "before and after" a measured number |
| 1 | Norms CONFLICT-FREE means `ConflictFree` | One conflict notion instead of two |
| 2 | One acceptance theorem for `runFol`, `runClosure`, `runOrder` | The three main runners stop being trusted glue |
| 3 | One logic with profiles | One fewer definition of `denote` and `Entails`; closure checker copy deleted |
| 4 | Statement-layer kit | Seven copies of the admission statements become one |
| 5 | Remaining ties from TRUST-MAP 5.1 and 5.2 | About 20 verdict paths get a theorem; no code removed |
| 6 | Hygiene | One SHA-256, one limits module, dead code out |
| 7 | Route and service skeleton | One `runCase`/`main`; every public route named by a theorem |
| 8 | Formula codec, then decoder combinators | Decoders tied to short encoders by round trip |
| 9 | Normative core | Soft norms, rights, defaults, speech, alternatives instantiate one lowering |
| 10 | Shared fixtures and harness | No trusted lines; makes steps 4 to 9 cheap to verify |

Every numbered step is one or more independently mergeable changes. No step changes a wire byte,
an identity or a verdict unless it says so; section 1.3 lists how each step shows that.

## 1. Ground rules

### 1.1 What "trusted" means here

The trust map's classes are used unchanged. The trusted surface is **K + S + the D and G code that
no theorem ties to K or S**: about 690 + 6,300 + 10,300 + 7,700 ≈ 25,000 lines before ties are
subtracted. Checkers (C), proofs (P) and tests (T) are not trusted. Line figures in this plan are
the trust map's per-declaration counts (about ±10%) or sums of them; where a figure is this plan's
own estimate it says "est.".

Two limits on every number below:

* The trust map did not measure how much of D + G is verdict-bearing [V] as opposed to
  reject-only [R] or identity [I]. Step 0 adds that measurement.
* A step can shrink the surface in two ways: **remove** trusted lines, or **tie** them (a theorem
  now covers them, so only the theorem's statement is read). The tables keep the two apart.

Scope of the guarantee (cross-family check, correction 1): `VE_AUTHORITY` defaults to `python`,
and 24 of 26 manifest operations name Python as the authority. That includes `norms.elaborate`,
`norms.conflict` and `norms.certificate`: plain norm documents are decided in Python by default
(`ve/norms.py:340,367,506,606`, `ve/norm_admission.py:32`). Everything in this plan shrinks what
must be trusted **when Lean is the gate**. Making Lean the default authority (TRUST-MAP 7.1) is
decided in `docs/spec/SEMANTICS-MIGRATION-PLAN.md`, not here.

### 1.2 Corrections applied

| Check item | Effect on this plan |
|---|---|
| 1. Norms are not decided by Lean alone | Step 1 is stated as fixing the Lean-authority gate only (1.1 above) |
| 2. `runOrder` replays against `Background.orderLiterals` only (`Route/Wire.lean:636`) | Step 2 states the order theorem over literals only, and adds the fact that the order vocabulary has no flags or definitions |
| 3. `normDefaults_wire_status_sound` already states the decode (`NormDefaults/Replay.lean:270`) | Step 5j fixes only `_gaps_sound` and `_reached_sound` |
| 4. Only `CertificateWire.runCaseReported` and `Protocol.caseError` (check-certificate and order modes) add `valid:false` | Step 7 keeps each route's error envelope as it is; unifying them is a wire change (open question 7) |
| 5. `Readings/Lines.lean` is live: `lineOrderText` is on the admission gate | Not deleted (section 5, item 11) |
| 6. `encQ` is compared as text, not re-decoded; only `encCore` is re-decoded and discarded | Step 8a states the Time round trip for `encCore`; `encQ` gets a separate text-equality lemma |
| 7. `Attribution/Content` `elab` and `premises` are C, not S | Reports is treated as already in the target form; its S count is not used |
| 8. The Norms copy of the definition premises is split: `hide`, `forget` in `Norms/Basic.lean:169,173`; `iffF` at `:21`; `Definition.premise` in `Norms/Elaborate.lean:54` | Step 9c lists the four sites separately |
| 9. `Definitions/Alias` is imported only by `Audit`; `Route.Admission.decodeDoc` already takes `E` | Step 6 deletes `Alias`; step 4a deletes the two `decodeDoc` copies with no new parameter |

### 1.3 Invariants and evidence

The invariants are those of `ARCHITECTURE-LAYERS-PLAN2.md` section 0: identities (SHA-256 over a
domain string and canonical JSON), the assurance manifest (decoder files pinned by hash and line
range; pinned decoder total 16,985 lines, which may shrink but not grow),
`lean/VE/Route/frozen-sources.sha256`, `lean/checkers.lock`, and Python/Lean/Rust agreement. This
plan reuses that document's suite bundles **S**, **M**, **P**, **L**, **R** and adds three:

| Code | What | Shows |
|---|---|---|
| **ST** | Statement dump (step 0): name and pretty-printed type of every theorem in `VE/Audit.lean`, written to `lean/statements.txt` | A proof refactor left every kept statement identical; additions and deletions are listed in the step |
| **OUT** | Lean output differential (step 0): the previously pinned build and the new build of every `lean_exe`, run over all corpora, compared byte for byte on stdout and exit code | "No Lean output change" directly, the Lean twin of layers2's bundle D for Rust |
| **TB** | Trust budget (step 0): class counts regenerated per file and diffed against the committed baseline | The step's claimed reduction, measured |

Where a refactor replaces function `f` by `g`, the preferred evidence is a Lean theorem
`∀ x, g x = f x` proved **before** `f` is deleted. OUT is the fallback, and the step says which
one it uses.

### 1.4 Rules every step follows

1. **Tie, then delete.** A step that removes a definition first lands the theorem that makes it
   redundant, in its own commit. The deletion is a second commit that can be reverted alone.
2. **Facade rule.** Every public name stays: a moved definition leaves an `abbrev` or a one-line
   corollary under its old name. Theorem names in `VE/Audit.lean` and in the feature `.md` files
   do not change. The wire-contract hooks call frozen code by name (section 6); those names are
   never renamed.
3. **Reviewed statements keep their text.** A frozen statement (`ConflictFree`,
   `norms_route_acceptance`, the feature `Intended*` predicates) is restated only where the step
   says so and asks for statement review.
4. Each Lean edit rehashes its files, adds `#print axioms` lines for new theorems (no primed
   names), registers new modules in `tools/layer_policy.py` and the layer table, and repins
   `ve_service` (layers2 step L0 supplies the tooling).
5. A step does not edit a file that an in-flight branch is editing (section 6).

## 2. Target shape

```
kernel (read once)        VE.Syntax/Semantics/Finite/Consequence      v0 logic, 110 K lines
                          VE.Core.{Syntax,Paths,Consequence}          closure + n-ary atoms
                          VE.Order.*, VE.Time.*                       arithmetic, units
                          VE.Route.{Layer,Route,Checker}              Layer, Checker, route_acceptance
wire kit (proved once)    VE.Json, VE.Wire.Codec, VE.Limits, one SHA-256
statement kit             VE.Route.Kit.{Admission,Conflict,Package,Choice}
normative core            VE.Norms (W1) + VE.Norms.Lowering
service skeleton          VE.Service.Skeleton
per feature (read each)   Doc type, Intended (S), a Lowering or Layer instance,
                          a codec description, a list of route handlers
```

`VE.Route.Layer` (`Route/Layer.lean:61`) already is the abstraction the lead asks for: a layer
gives `premises` (executable), `Intended` (the reviewed meaning), `faithful` (premises hold iff
`Intended`) and `expands` (unique expansion); `route_acceptance` (`Route/Route.lean:213`) is
proved once over any `Layer` and any `Checker`. The elaborator is then untrusted and only
`Intended` is read. The consolidation is mostly making every feature and every runner go through
this one contract, instead of restating it.

What a new feature adds after the plan: its `Doc`, its `Intended`, one instance, one codec
description and its handlers. Step 0's budget check fails a change that adds K, S or untied [V]
lines without a note signed by the DRI.

## 3. Steps

Effort scale: **S** ≤ half a day, **M** 1 to 2 days, **L** 3 to 5 days, **XL** 6 to 10 days, each
including one full gate run.

### Step 0. Measurement tooling

* **Adds:** (a) `tools/trust_map.py`: reads a class tag per declaration (a `-- trust: K|S|D[V]|…`
  comment or a side table seeded from TRUST-MAP section 11) and writes per-file counts to
  `docs/trust-baseline.json`; fails when K + S + untied [V] grows without a signed entry.
  (b) `tools/lean_statements.py` (bundle ST). (c) `tools/lean_output_diff.py` (bundle OUT),
  taking inputs from `conformance/*.json`, the `lean/VE/*/examples` cases and the inputs recorded
  by `tests/contract_input_recorder.py`.
* **Trusted before → after:** unchanged. **API:** none. **Risk:** low. **Effort:** L.
* Steps 1 and 2 add only theorems and do not wait for this step.

### Step 1. The norms route's CONFLICT-FREE means the spec's `ConflictFree` (DRI item a)

Facts, re-read in the sources:

* `Norms/Run.lean:150-157` answers `CONFLICT-FREE` when `Flagged.replayConflict` succeeds and
  `res.conflictFree` holds. Nothing calls `Replay.replayConflict`, `replayWitness` or
  `replayEntailment`, yet the `Norms/Run.lean` docstring (lines 17, 21, 25) and NORMS.md cite the
  `Replay.norms_wire_*` theorems.
* For a document with a flag or a definition (`plain = false`),
  `norms_flagged_conflict_sound` (`Flagged.lean:307`) concludes `BaseConflictFree`
  (`Flagged.lean:215`): no formula of `pyTargets` holds in a structure admissible over `baseEnv`
  (regulated predicates hidden, defined ones kept) that satisfies `baseBackground` (flags ++
  definitions ++ literals). `pyTargets` expands earlier regulated atoms and keeps defined atoms
  (`regTable`, `Flagged.lean:148`).
* The spec's `ConflictFree D B` (`Norms/Conflict.lean:279`) ranges over `BaseAdmissible D B`
  (every layer symbol hidden; literals only) and uses `subst`, which expands every earlier
  symbol. `conflictFree_expands_document` (`Conflict.lean:447`) ties it to unique expansion.
* The witness side is already stated against the spec: `norms_flagged_witness_sound`
  (`Flagged.lean:366`) refutes `∀ B, BaseAdmissible D B → Sat B flags → ConflictFree D B`.

**1a. Link theorem (recommended).** New file `lean/VE/Norms/FlaggedSpec.lean`; no existing file
is edited.

```lean
theorem norms_flagged_conflict_free (j : Json) (r : ConflictReplay)
    (h : replayConflict j = .ok r) (hv : r.conflictFree = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true)
      = .ok r.src ∧
    ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B (flagPremises r.src) →
      ConflictFree r.src.D B
```

It holds for both values of `plain`, and it is the exact statement the witness theorem refutes,
so a corollary states that the route cannot answer both CONFLICT-FREE and CONFLICT for one
document. Proof outline:

1. *Expansion.* Every `B` with `BaseAdmissible D B` extends to an `S` admissible over
   `baseEnv D` in which each defined symbol has its meaning, and forgetting the defined symbols
   gives back `B`. Definitions and regulated predicates share one dependency DAG
   (`Norms/Tree.lean:149-152`), so a definition body may mention an earlier regulated predicate;
   `S` then interprets that hidden relation by its expanded outcome evaluated in `B`.
2. *Transfer.* Flag premises and literals are formulas over the base vocabulary
   (`RegulatedFlag`, `Norms/Wire.lean:142`), so `S` satisfies `baseBackground`.
3. *The two substitutions agree.* For such `S`, every `k` and every `φ` well formed over
   `envAt D k`: `(regSubst D.T k φ).denote S ρ ↔ (subst D.T k φ).denote B ρ`, by induction on `k`
   in the style of `Norms/Subst.lean`; the definition case uses the premise `d(x̄) ↔ body`.
4. `pyTargets` and `targets` list the same names and sorts in the same order; item 3 relates
   their formulas, so `BaseConflictFree src S` gives `ConflictFree D B`.

**1b. Remove the second path.** Delete `Replay.replayConflict`, `replayWitness`,
`replayEntailment`; keep the `Replay.norms_wire_*` names as corollaries of the `Flagged` theorems
at `plain = true`. Correct the `Norms/Run.lean` docstring and NORMS.md (TRUST-MAP section 10).

* **Trusted before → after:** the reviewer reads two conflict notions today: `ConflictFree`
  (S 31) and the nine definitions of `Flagged.lean:144-216` (`regTable`, `regSubst`, `conflictPy`,
  `outcomePy`, `pairConflictPy`, `pyTargets`, `baseEnv`, `baseBackground`, `BaseConflictFree`;
  about 45 code lines). After 1a the nine are checked code and only `ConflictFree` is read:
  −9 trusted definitions, −45 lines; the `norms-conflict` branch of `Norms/Run` becomes tied.
  1b deletes about 110 untrusted lines.
* **API kept:** all `Flagged.*` and `Replay.norms_wire_*` names; wire output unchanged.
* **Evidence:** 1a adds theorems only (L, ST shows additions only). 1b: OUT, `test_norms_three_way`,
  `tests/test_stage2_norms.py`.
* **Risk:** behaviour none (1a), low (1b). Proof risk medium: two cases must be settled before
  the proof starts, by reading `Tableau.checkCertificate` and Python's `_expand`.
  (i) A definition that depends on a regulated predicate puts a premise into `baseBackground`
  that is not well formed over `baseEnv`. Either the checker rejects such certificates (the link
  then holds vacuously, and a lemma must say so), or it accepts them and item 1's choice of `S`
  carries the proof. (ii) Whether a defined predicate may carry a flag; if so
  `Sat B (flagPremises)` must be stated on `S`. If either case makes the link false, the public
  check differs from the spec on real documents. That is a finding to report, and the fix is
  then **option R**: check the frozen `targets` over `envAt D 0`, as `Norms.Replay` does.
  Option R changes Python's conflict packages and their bindings, so it is a signed wire change
  and not a consolidation step.
* **Effort:** 1a L; 1b S. `Service/FamilyNorms.runCase` gets its family-level theorem in step 5e.

### Step 2. One acceptance theorem for `runFol`, `runClosure`, `runOrder` (DRI item b)

Facts: `fullBackground` (`Route/Wire.lean:249`) is flags ++ definitions ++ literals. `runFol`
(`:530-536`) and `runClosure` (`:572-579`) check the certificate against it; `runOrder` (`:636`)
uses `Background.orderLiterals` only. Existing theorems each cover part: `fol_route_acceptance`
(literals, `Route/Background.lean:144`), `fol_data_route_acceptance` (flags ++ literals,
`Data/Background.lean:104`), `Definitions.Route.acceptance` (definitions ++ literals,
`Definitions/Route.lean:66`), `order_string_route_acceptance` (`Route/Background.lean:284`). No
theorem covers all three parts, and none names a runner. `Core.Wire.run_certificate_acceptance`
(`Core/Wire.lean:112`) shows the shape for the fourth runner, with ten decode hypotheses.

**2a. Theorems on the runners as they are.** New file `lean/VE/Route/WireSound.lean`.

1. `fullLayer rv : Layer fol Unit`: the definitions layer composed over the identity layer whose
   admissibility is "structurally admissible, flags hold, literals distinct", with
   `BackgroundSound (fullLayer rv) ((fullBackground rv).map Prod.fst)`. Needs one decoder fact:
   `decodeVocabulary … = .ok rv → Definitions.Chain rv.environment rv.definitions`.
2. One record and three claim predicates, which are what the reviewer reads instead of the
   runners:

   ```lean
   structure Family where            -- fol, closure, order (and core)
     L : Semantics.{u}               -- Route/Layer.lean
     Vocab : Type
     env : Vocab → L.Env
     Intended : Vocab → L.Model → Prop   -- admissible, flags, definitions, literals
     decodePremises : Vocab → Json → Except String (List L.Formula)
     decodeConclusion : Vocab → Json → Except String L.Formula

   def CertificateClaim (F : Family) (rv : F.Vocab) (j : Json) : Prop :=
     ∃ ps c, F.decodePremises rv j = .ok ps ∧ F.decodeConclusion rv j = .ok c ∧
       ∀ S, F.Intended rv S → F.L.Sat S ps → F.L.Holds S c
   ```

   `CountermodelClaim` (a decoded model that is `Intended`, satisfies the premises and falsifies
   the conclusion) and `EvaluateClaim` (the values are `denote` in the decoded model) follow the
   same pattern.
3. Three short refinement lemmas, by `bind_ok` inversion instead of ten hypotheses:
   `runFol … "certificate" j = .ok res → res.valid = true → CertificateClaim folFamily rv j`, and
   the same for `runClosure` (through `Closure.embed` and conservativity) and `runOrder`. The
   order family's `Intended` is "admissible and order literals distinct";
   `RouteOrderVocabulary` has no flags or definitions, and the lemma says so. The countermodel and
   evaluate kinds use `decodeDataModel_combined`, `refutesF/C_sound`, `valuesF/C_sound`.
4. The binding conjunct (`bindingOk … = .ok ()`) is carried as in `run_certificate_acceptance`.

**2b. Merge the runners (after step 3b).** `runFamily (F : FamilyImpl)` replaces `runFol`,
`runClosure`, `runOrder` and `Core.Wire.run`; each old name becomes `runFamily <instance>` with a
theorem `∀ args, runX args = runFamily X args`.

* **Trusted before → after:** `Route/Wire` G 156 (the runners, [V]) becomes tied; about 30 new S
  lines (`Family`, three claims) are read instead: net about −125. 2b removes about 110 G lines
  (est.) and `Core/Wire` G 41.
* **API kept:** runner names and outputs. 2a edits no existing file.
* **Evidence:** 2a theorems only (L, ST). 2b: the equality theorems, then OUT, `test_p0_three_way`,
  `test_lean_conformance`, `test_data_three_way`, `test_definitions_differential`.
* **Risk:** 2a low; 2b medium (`Route/Wire.lean` is a pinned decoder file; manifest regen).
* **Effort:** 2a L; 2b M.

### Step 3. One logic with profiles

Today `Formula`, `denote` and `Entails` are defined in `VE`, `VE.Closure`, `VE.Core` and
`VE.Order`, with four separately proved tableau checkers. `Closure/{Paths,PathRules,Induction,
RoundTrip}` and `VE/TableauExtended*` are textual copies of the `Core/` files over a different
type (`Core/NARY.md` says so).

| Sub-step | Change | Trusted before → after | Evidence | Risk, effort |
|---|---|---|---|---|
| 3a | Prove `Closure.Tableau.checkCertificate E ps c cert = Core.Tableau.checkCertificate E (ps.map embedClosure) (embedClosure c) (embedCert cert)`, plus the same for the trace decoders and `Steps.closure` vs `Steps.core` | none (theorem only) | L, ST | Low; L. The files are copies, so the proof is a parallel induction; if step counts differ, 3b must keep `Steps.closure` |
| 3b | `runClosure` and `CertificateWire.runClosureCase` call the Core checker behind an atom-free gate. Delete `VE/TableauExtended*` (6 files, 1,075 lines) and the closure files that only that tableau uses, `Closure/{PathRules,Induction,Substitution,Congruence}` (473 lines; confirm with `lake build`) | K 0; removes about 1,550 untrusted lines (C and P) and one of the three trace decoders (D, about 30 est.) | 3a's theorem; OUT; closure three-way; `rust/fuzz_closure.py`; `test_closure*.py` | Medium; L. Error text for rejected certificates must not change |
| 3c | One semantics, two syntaxes: keep `Closure.Formula` as a syntax type, define `Closure.Formula.denote a := (embedClosure a).denote` and `Closure.Entails` through Core; `Closure/{Paths,Finite}` (315 lines) reduce to aliases of Core's | K 76 → about 25 (the inductive only); `embedClosure_denote` becomes `rfl` | L, ST (statements of `conservativity`, `closure_route_acceptance` unchanged); `Route/Budget.evalC` soundness restated through Core | Medium; L |
| 3d | Prove the converse of `Order.entails_v0`, giving `entails_v0_iff` | Order K 150 unchanged; "order agrees with v0 on v0 formulas" becomes a theorem instead of a one-way claim | L, ST | Low; M to L |

* **API kept:** `VE.Closure.Formula`, `Closure.Entails`, `Closure.Tableau.checkCertificate` (as a
  definition through Core), `Closure.embed`, every audited theorem name.
* **Not in this step:** merging Order into a core parameterised by a term theory (section 5), and
  making `Closure.Formula` a subtype of `Core.Formula`. The subtype would change pattern matching
  in `Route/Budget`, `Route/Closure` and `Closure/Surface` for the same trust result as 3c.
* By score alone step 3 ranks last of the proof steps (section 4). It is third because the DRI
  asked for it, because it removes a whole definition of the logic, and because steps 2b and 8a
  get smaller once closure is a view of Core. 3a and 3d are safe to start at once; 3b and 3c can
  interleave with step 4.

### Step 4. Statement-layer kit

The admission skeleton is restated in `Route/Admission`, `Norms`, `NormDefaults`, `SoftNorms`,
`Rights`, `Alternatives`, `Risk` (nearly a copy of Alternatives), `Time/Document` and
`Attribution/Admission`, with no theorem relating the copies (TRUST-MAP 6.2).
`Alternatives/Admission.lean` shows the pattern in 133 lines: feature leaves (`altLeaf`,
`layerLeaf`, `profileLeaf`), `nodeAdmitted`, `checkNodes`, `Admitted`, `admitDocument`,
`generated`, `otherAssumptions`, `report_consequence`.

**4a. Small shared pieces.**
* Move `bind_ok` (about 600 occurrences in 39 files) from `Order/ProfileGate.lean` to a kernel module
  `VE/Kit/Except.lean`; `VE.Order.ProfileGate.bind_ok` stays as an alias, so no call site changes.
* Delete `SoftNorms.Admission.decodeSoftDoc` (D 26) and `NormDefaults.Admission.decodeFilledDoc`
  (D 41), verbatim copies of `Route.Admission.decodeDoc`, which already takes `E`.

**4b. Admission kit.** New `lean/VE/Route/Kit/Admission.lean`:

```lean
structure Extension where
  Src : Type
  decode : (environment norms premises : Json) → Except String Src
  env : Src → VE.Environment                    -- typing environment of graph nodes
  leaves : Src → List (String × VE.Formula)     -- regenerated, labelled leaves
  generated : Src → List VE.Formula             -- premises regenerated from the source
  leaves_generated : ∀ s l, l ∈ leaves s → l.2 ∈ generated s

def admitWith (X : Extension) (environment document : Json) : Except String (Admitted X)
theorem admitWith_spec …        -- SourceDecoded ∧ CertificatesBound ∧ ReportAdmitted
theorem report_consequence …    -- generated ∧ other assumptions ⊢ root, proved once
def AdmissionAnswer (X : Extension) …
```

One instance per feature, each its own change, in this order: Alternatives and Risk (the closest
pair), Reports, Rights, SoftNorms, then Norms and NormDefaults after wire-contract S5 switches
(section 6). `Time/Document` is over `QFormula`, so it needs the kit generic in `Semantics`; it
goes last and may stay separate (open question 8).

**4c. Conflict check and package replay.** `Route/Kit/Conflict.lean`: one `certsCover targets
check certs` with one `certsCover_target` lemma, replacing the seven `conflictFreeCheck` and
`_target` pairs (`Norms/Replay`, `Norms/Flagged`, `NormDefaults/Wire`, `SoftNorms/Coherence`,
`Rights/Route`, `Alternatives/Background`, `Risk/Background`). `Route/Kit/Package.lean`: one
`decodePackage` over a binding description and one replay schema whose soundness theorem always
has the decode conjunct, `replay j = .ok r → decode j = .ok r.src ∧ …`. The unused-hypothesis
pattern of TRUST-MAP 5.2 then cannot recur.

**4d. Choices and graphs.** One `disjunction` over a `Semantics` with `or` and `bottom` (six
copies today); one readings-choice check (four copies); `VE.Graph` becomes the FOL instance of
`Service/GenericGraph` (`graph_certificateSound_iff` already relates the two contracts).

* **Trusted before → after (est. from section 11 of the trust map):** admission statements S about
  435 (seven copies plus five `AdmissionAnswer`s) → about 150; admission glue G about 570 → about
  270; D −67 (4a); claim graph S 67 + 28 → 67. Net about −650 trusted. Total lines removed 1,000
  to 1,500 (the trust map's estimate).
* **API kept:** every `X.Admission.admitDocument`, `Admitted`, `AdmissionAnswer`,
  `*_wire_acceptance` and `*_report_consequence` name, as abbreviations and corollaries with
  unchanged statements.
* **Evidence:** ST; OUT (admission answers and `report_id` are byte-identical); each feature's
  three-way or differential suite; M for the pinned decoder files.
* **Risk:** medium. The order of checks inside `admitDocument` fixes which error fires first;
  the kit takes the order as data and each instance reproduces today's order. **Effort:** 4a S;
  4b L for the kit plus M per instance; 4c L; 4d L.

### Step 5. Remaining ties (TRUST-MAP 5.1 and 5.2)

Each row adds theorems in a new file and edits nothing else, so rows are independent and can run
beside steps 3 and 4. They remove no code; they turn [V] glue into stated ties, about 1,500 to
2,000 G lines in total (est.).

| Row | Path | Theorem to add | Effort |
|---|---|---|---|
| 5a | `Order/Wire.runCase`, `Order/Surface.runCase`, `Time/Wire.runCase`, `Closure/Bridge.runCase`, `Core/Wire.run` (evaluate, countermodel), `Core/Layers.run` | Instances of step 2's three claims; for Time, `¬ TEntails` and `value = tdenote` | L |
| 5b | `Definitions/Bundle.runBundle` | `bundle_sound` over `fullLayer` (flags included) | M |
| 5c | `Norms/Plain.run` | Acceptance over the extended background and `softPremises` | M |
| 5d | `Risk/Run` `runConflict`, `runFollowable`, `runCertificate` | Risk twins of `alt_conflict_witness_sound`, `alternatives_wire_dilemma_sound`, `alternatives_wire_acceptance` | L |
| 5e | `Service/FamilyNorms.runCase` | Family-level CONFLICT-FREE, from step 1 | M |
| 5f | `SoftNorms/Run` `sufficientCoherence`, `classify`, `weighingWitness` | Dropping labels cumulatively preserves the claim; classification matches the spec | L |
| 5g | `Readings/Run` `setPairs`, `setFindings`; `Separate.actOnly` | "Every pair is separated" over the loop; `actOnly` proved, or marked not certified (a wire change) | M |
| 5h | `Rights/Run` `licence`, projections | `licence = Scope.licensed`; projections equal `rightsOf` and `dutiesOf` | M |
| 5i | `Attribution/Run.scopedVerdict`; `Discourse/Run` `runResolve`, `runJoint`; `Standalone.modelCase` | Name the branch in an existing soundness theorem | M each |
| 5j | Unused decode hypotheses: `readings_wire_separate_sound`; four `speech_wire_*`; `Service.Graph` `graph_sound`, `graph_entails`, `graph_unfolds`; `normDefaults_wire_gaps_sound`, `_reached_sound` | Add the `decode j = .ok r.src` conjunct. These restate audited theorems, so ST shows changed statements and the feature `.md` files are updated | M |

Left open: `Risk/Record.statuses` (it uses `permittedAt` and `requiredAt`, which ALTERNATIVES.md
labels untrusted diagnosis) and `Rights/Admission.validateCouplings` (couplings have no semantics
in Lean). Both need a specification before a theorem can be stated (open question 5).

### Step 6. Hygiene

| Item | Change | Trusted Δ | Evidence | Effort |
|---|---|---|---|---|
| 6a | One SHA-256: `Service/Protocol.Sha256.digest` becomes an alias of `CertificateWire.sha256` | [I] D about −60 | the 130 `#guard` vectors stay; OUT; identities unchanged in P | S |
| 6b | One limits module `VE/Limits.lean` (kernel). The six `maxNodes = 10000` sites (`Norms/Wire.lean:173`, `Route/AstLimit.lean:21`, `SoftNorms/Soften.lean:161`, `Alternatives/Decl.lean:219`, `Risk/Decl.lean:258`, `Service/TypingDiagnostic.lean:52`) become `abbrev`s of it, names kept. `WireContract/Limits.lean` stays generated; `Audit` checks the two agree by `rfl` | about −20, and one place to read | L, OUT | S |
| 6c | Delete dead code: `Definitions/Alias.lean` (60), `SurfaceProofs.lean` (197, subsumed by `RoundTrip.parse_print`), `Rights.Projections.owes` and `free`, Readings `Coupling`, `Narrowing`, `AchievesQuiet` | S about −30; about 300 untrusted lines | `lake build`; ST lists the deleted names | S |
| 6d | Doc fixes of TRUST-MAP section 10 not already made by a step | none | review | M |
| 6e | Mark reject-only modules (`Norms/Tree.check` diagnostics, SoftNorms `Phases` size tables and `checkW1`, `Service/TypingDiagnostic`, `WireContract/*`) with a header line that step 0's tool reads as [R] | none; the reading load drops | TB | S |

Not deleted here: `Core.Bridge.runCase` (layers2 L7 owns it), `Readings/Lines.lean`,
`Compose/Slot.lean` (section 5).

### Step 7. Route and service skeleton

Every `*/Run.lean` repeats the same shape, as `Norms/Run.lean:130-212` shows: `runCase` (read
`id` and `kind`, a chain of `if kind == …`, a fallback), `runCaseReported` (the error envelope)
and `main` (read a file or stdin, `parseCases`, map, print, exit code). There are eleven such
files, plus ten four-line `*Main` delegators.

New `lean/VE/Service/Skeleton.lean` (layer 4), built on layers2's `Route/Dispatch.lean`:

```lean
structure Handler where
  kind : String
  applies : Json → Bool
  run : (id : String) → Json → Except String Json

structure RouteSpec where
  usage : String
  handlers : List Handler
  fallback : Json → Except String Json
  envelope : Json → String → Json        -- today's error shape of this route, unchanged

def RouteSpec.runCase, RouteSpec.runCaseReported, RouteSpec.main

theorem RouteSpec.runCase_handler (R : RouteSpec) (j a : Json) (h : R.runCase j = .ok a) :
    (∃ hd ∈ R.handlers, hd.applies j = true ∧ ∃ id, hd.run id j = .ok a) ∨ R.fallback j = .ok a
```

`runCase_handler` lifts every per-handler theorem to the public entry point once. Today only the
admission branch of most routes has a wire theorem naming `runCase` (`norms_wire_acceptance`,
`discourse_wire_acceptance`). `Compose.dispatch` can then return a `RouteSpec`, which ties a
route value to its runner by construction (TRUST-MAP 5.3, Compose).

* **Trusted before → after:** G about −340 (est.: about 35 lines of dispatch and main in each of
  eleven files, replaced by one 60-line module and a handler list per route).
* **API kept:** each `X.Run.runCase`, `runCaseReported`, `main` as
  `abbrev … := X.spec.runCase`; executable names and `lakefile.toml` roots unchanged.
* **Evidence:** `∀ j, X.spec.runCase j = X.Run.runCase_old j` per route, then delete; OUT; the
  manifest `dispatch` file lists are regenerated (M), because kind literals move into handler
  lists.
* **Risk:** medium. Handler order decides which branch answers (for example
  `norms-conflict` with a witness before `norms-conflict`), and `Service/Protocol.lean` dispatch is
  pinned by `rfl` theorems, so the service keeps its own dispatch in this step.
* **Effort:** L for the skeleton and two routes; S per further route. After layers2 L5.

### Step 8. Formula codec, then decoder combinators

Today there are five formula decoders (`Bridge`, `Closure/Bridge`, `Core/Bridge`, `Order/Wire`,
`Norms/Wire.budgetFormula`), at least six encoders (`Route/Wire.encodeFormula`,
`Standalone.encodeClosure`, `encodeCore`, `EnglishRun.encodeFormula`, `Order/Surface.formulaJson`,
`Time/Wire.encCore`), three trace decoders, and no round-trip theorem for any of them.

**8a. One codec per logic, with a round trip.** New kernel module `lean/VE/Wire/Codec.lean`:

```lean
structure Codec (α : Type) where
  enc : α → Json
  dec : Json → Except String α
  ok : α → Prop                               -- depth and size bounds, valid identifiers
  round : ∀ a, ok a → dec (enc a) = .ok a
  exact : ∀ j a, dec j = .ok a → enc a = j    -- the decoder accepts only canonical input
```

Instances for v0, Core (closure is its atom-free view after step 3c) and Order formulas, for
traces, and for Time (`elabFormula` against `encCore`; a separate lemma that `encQ` prints the
text the runner compares). The existing decoders are not rewritten: the codec's `dec` **is** the
existing function and only the two theorems are new. With `exact`, a JSON input means the unique
value whose encoding it is, so the reviewer reads the encoder (structural, about 20 lines per
logic) instead of the decoder. Duplicate encoders become aliases of the codec's `enc` after a
proof that they are equal.

* **Trusted before → after:** formula and trace decoders, D about 450 (est.), become tied; about
  60 encoder lines are read instead. Encoder copies removed: about 80 lines.
* **Evidence:** theorems only for the round trips (L, ST); `enc₁ = enc₂` theorems before each
  alias; OUT. **Risk:** low to medium (`exact` fails if a decoder tolerates non-canonical input;
  then only `round` is stated and the step says so). **Effort:** L per logic.

**8b. Decoder combinators, one unit at a time.** Combinators `str`, `ident`, `nat`, `list`,
`obj` (exact fields, in order), `tagged`, `refine`, `fix` (fuelled), each with `round` and `exact`
proved once. A feature's decoder becomes a description built from them. The per-feature D is
large: SpeechActs 867, Discourse 1,389, Time 703, Risk 690, Attribution 628, Rights 589,
SoftNorms 481, Norms 464.

* A unit migrates only after its wire-contract stage is public (section 6). That stage's fault
  corpus (`conformance/wire_contract_faults_<name>.py`) is the oracle for error text, codes and
  fault order, which a decoder rewrite must reproduce exactly.
* **Evidence:** `∀ j, newDecode j = oldDecode j`, error strings included, proved before the old
  decoder is deleted. Where that proof is too costly: OUT plus the fault corpus, stated as the
  weaker evidence it is.
* **Trusted before → after:** unknown until one unit is done; the pilot (Alternatives, D 285)
  measures it. **Risk:** high: about thirty proofs unfold decoder bodies (wire-contract PLAN
  section 10), and manifest pins move. **Effort:** L to XL per unit.

### Step 9. Normative core

W1 norms are already the common target: soft norms lower by `soften`, rights by `soften ∘
correlate`, norm defaults by `fill`, speech acts by `policy`, alternatives by `inlineTree`, risk
through alternatives. Each feature still restates base admissibility (`BaseAdmissible'`,
`BaseAdmissibleR`, `BaseAdmissibleP`), conflict-freedom (`SoftConflictFree`, `RightsConflictFree`,
`ConflictFreeP`), background (`background'`, `backgroundR`, `backgroundP`, `backgroundAlt`), the
layer chain (`softSymLayer`, `rightsSymLayer`, `slotSymLayer`, `altSymLayer` and their chains) and
its route acceptance theorem. `Compose/Slot.lean` is the most general version: a `SoftDoc X` plus
a list `P` of closed base formulas. Today it is a parallel re-proof ("the slot theorems are the
rights route's proofs with `Lim_D` replaced by an arbitrary list `P`", COMPOSE.md), tied back only
by `rights_*_is_slot`.

| Sub-step | Change | Trusted Δ | Notes |
|---|---|---|---|
| 9a | Split `Compose/Slot.lean` into the generic slot (imports SoftNorms only) and `Compose/SlotRights.lean`. `Rights/Route.lean`'s route theorems become corollaries of the slot theorems at `P := Lim_D`, and the soft route's at `P := []` (`slot_empty*` exist). Delete the three parallel chains | S about −50; about 500 untrusted proof lines | Reverses today's direction of derivation. After compose S2b |
| 9b | `VE/Norms/Lowering.lean`: record with `Doc`, `wf`, `lower : Doc → Norms.Doc`, `extra : Doc → List Formula`, `Intended`, `faithful`; the slot stated over W1 (`BaseAdmissibleP (D : Norms.Doc) P`); soft = W1 slot at `soften X` with `softPremises X ++ P`. Instances: norms, norm defaults, soft, rights, speech, alternatives, risk | S about −150 (est.) | Needs the strict-norms embedding into `SoftDoc` that the composition plan (2.9) lists as missing; if it is costly, 9b covers the soft family only |
| 9c | Shared pieces: the profile-word inliner parameterised by a word table (`Alternatives/Decl` and `Risk/Decl`, line for line; S −120); `Norms.Definition` replaced by `Definitions.Def` at the four sites of correction 8; one followability formula (`Alternatives/Followable`, `NormDefaults/Routes`; S −38); one functional and pairwise-distinct premise generator (`Data/Background`, `Route/Background`, `Risk/Background`, `Alternatives.ownPremise`) | S about −200 | Each is its own change |
| 9d | Meaning policy. A feature's `Intended` must not call its own elaborator's helpers; an import rule checks that `X.Semantics` does not import `X.Elaborate` or `X.Correlate`. Rights: declare `correlate` the meaning and drop `ValueRight` and the `*X` layer (S −340), or rewrite `ValueRight` without `nodeOf`, `ownGuard`, `limPack`. Discourse: give `Acc` an independent definition or document it as code-as-spec; remove the identity `canonTarget` and `AliasEq` (−70) | S −410 | Changes reviewed statements: needs statement review and a DRI decision (open question 6) |

* **API kept:** all route theorem names with unchanged statements (ST), except in 9d.
* **Evidence:** ST and OUT (no executable changes in 9a and 9b; 9c changes generators, so the
  equality `newGen = oldGen` is proved first); rights, soft-norms, norm-defaults, alternatives and
  risk three-way and differential suites.
* **Risk:** medium (frozen statements; compose in flight). **Effort:** 9a L; 9b XL; 9c M each;
  9d L.

### Step 10. Shared fixtures and harness

* **Python:** nearly 70 files under `tests/` call `subprocess` directly and about 30 define their
  own `lean()` or `rust()` fixture; `tests/subprocesses.py` exists but is not the single entry. One
  `tests/harness.py`: `lean_route(exe, cases)`, `rust(cases)`, `three_way(case)` with the
  normalisation rules in one place. Tests migrate file by file; no test is deleted.
* **Corpora:** one layout `conformance/<unit>/` with recorded inputs and per-backend expected
  outputs, read by OUT, by the three-way tests and by the wire-contract gates.
* **Lean:** `VE/Examples/Kit.lean` with the small environments and models that the per-feature
  `Examples.lean` and `Checks.lean` files rebuild (T, about 2,800 lines outside `Audit`).
* **Trusted Δ:** none. **Risk:** low; the full suite must select the same test ids before and
  after. **Effort:** L, spread over other steps. Avoid the seven tests layers2 P10 rewrites while
  that step is open.

## 4. Order and scores

Score = trusted lines removed or tied ÷ (effort in days × risk), risk 1 low, 2 medium, 3 high.
The inputs are rough, so read the ranking and not the digits.

| Step | Removed | Tied | Days | Risk | Score | Depends on |
|---|---:|---:|---:|---:|---:|---|
| 1 Norms conflict | 45 | 15 | 4 | 1.5 | 10 | none (theorem only) |
| 2a Runner theorems | 0 | 125 | 4 | 1 | 31 | none (theorem only) |
| 3 One logic | 80 | 0 | 14 | 2 | 3 | layers2 L1, L2 before 3b |
| 4 Statement kit | 650 | 0 | 14 | 2 | 23 | 4a first; S5 switch before Norms, NormDefaults |
| 5 Remaining ties | 0 | 1,700 | 14 | 1 | 121 | 5a after 2a; 5e after 1 |
| 6 Hygiene | 110 | 0 | 3 | 1 | 37 | none |
| 7 Skeleton | 340 | 300 | 6 | 2 | 53 | layers2 L5 |
| 8a Formula codec | 80 | 450 | 10 | 1.5 | 35 | better after 3c |
| 8b Combinators | unknown | unknown | 30+ | 3 | n/a | 8a; each unit's wire stage |
| 9 Normative core | 810 | 0 | 20 | 2 | 20 | compose S2b before 9a; DRI decision for 9d |
| 10 Fixtures | 0 | 0 | 4 | 1 | n/a | none |

By score alone the order would be 5, 7, 6, 8a, 2a, 4, 9, 1, 3. The plan follows the DRI's order
for 1 to 4 for these reasons:

* Step 1 has a low score and still goes first. It is the one place where a public verdict means
  something other than the reviewed specification, and no other step can be trusted to "mean the
  spec" until it does.
* Step 2 gives step 5a its generic theorem.
* Step 3's theorem-only halves (3a, 3d) and step 5's rows touch no existing file, so they run in
  parallel with everything.

Suggested calendar: week 1: steps 1a, 2a, 0, 6. Weeks 2 and 3: 3a, 3d, 4a, 4b with its first
instances, and step 5 rows. Weeks 4 and 5: 3b, 3c, 2b, 4c, 4d, 7. Later, gated on other
workstreams: 8, 9.

Step 3's low score is honest: the closure copies are mostly checked code and proof, which the
trust map does not count as trusted. Its gain is one fewer `denote` to read (K 76 → 25) and
about 1,550 fewer lines to maintain.

Expected result, to be replaced by measured numbers from step 0: about 2,100 trusted lines
removed and about 2,600 tied, out of about 25,000, before step 8b. Per feature added afterwards,
the trusted text is its `Doc`, its `Intended` and its codec description.

## 5. What not to consolidate, and why

1. **The v0 logic** (`VE/Syntax`, `Semantics`, `Finite`, `Consequence`; 110 K lines). It stays a
   concrete inductive type with a concrete `denote`. It is where a reviewer starts and what every
   feature lowers into; making it an instance of a generic logic would make the anchor harder to
   read to save nothing.
2. **Order into Core.** Parameterising Core by a term theory would remove about 150 K lines and
   put a 985-line tableau and its soundness proof at risk. Step 3d states the exact relation
   instead. Revisit if a third arithmetic profile appears.
3. **Time and units.** `QFormula` is a tagged layer over Order with `units_faithful`; it is
   already in the target form.
4. **The v0 and order tableau checkers.** They are checked code with their own soundness
   theorems, so they add proof and not trust. Only the closure copy is merged (step 3).
5. **Python, Lean and Rust implementations of the same check.** Three independent
   implementations are the differential oracle that every "no behaviour change" claim in this
   plan relies on. Shared tables (wire-contract tables, limits) are fine; shared or generated
   decision code would remove the independence.
6. **The wire-contract engine and the decoders.** The contract decides the diagnostic and never
   the verdict (wire-contract PLAN 0.3), and that plan rejected generating decoders and relating
   a contract to its legacy decoder (3.2, 10). Step 8 consolidates the verdict-path decoders
   under proofs and leaves the diagnostic engine separate. Putting generated tables on the
   verdict path would move the trusted base to the generator.
7. **Diagnostic and reject-only code with verdict code.** Messages are per feature by nature and
   pinned by tests and signed wire changes. Step 6e separates them so a reviewer can skip them.
8. **Independent direct semantics.** Reports (`Sat`, `IntendedReports`), norm defaults
   (`Value3`), soft norms (`ValueSoft`), alternatives (`FollowableIn`) keep their own `Intended`.
   The features differ for real reasons (three-valued defaults, weighing, correlatives); one
   parametric deontic semantics would be larger and harder to review than their sum. What is
   shared is the lowering target and the scaffolding around it (step 9).
9. **`ConflictFree` and the other frozen W1 statements.** The kits instantiate them and never
   restate them.
10. **Identity material.** Domain strings, canonical JSON and digest inputs are not touched by
    any step; step 6a changes which function computes SHA-256, not what is hashed.
11. **`Readings/Lines.lean` and `Compose/Slot.lean`.** `lineOrderText` is on the admission gate
    (correction 5). On `compose-s2/integrate` `genKeys_nodup` is used by `Readings/Labels.lean`,
    and `ve_readings_route` calls slot functions at run time (`backgroundValidP`,
    `slotConflictFreeCheck`). The trust map's "dead" verdict on both holds on main only.
12. **The English grammars.** `English.Tree`, `Discourse.STree` and english-lean's generic engine
    are three grammars. english-lean keeps discourse separate (its plan 7.15) and adds new files
    only; unifying them belongs to that workstream after its S5, not here.
13. **`ResponseDecode.lean`.** It re-implements `Graph.check` over JSON on purpose, as an
    independent test oracle. It is T, not trusted.
14. **Pinned Python entries.** No `@semantic_entry` function and no Lean call site moves for the
    sake of sharing code (layers2 rule 4).

## 6. Coordination with work in flight

| Workstream (state) | Files it owns now | Consequence here |
|---|---|---|
| **layers2** (plan on `design/layers2`; batch 1 on `infra/layers2-b1`) | Policy files; L4 `VE/Tok.lean`, `English/Lexicon`, `Discourse/{Manifest,Access}`; L5 `Route/Run.lean`, new `Route/Dispatch.lean`, `Discourse/{Loader,Run}`; L6 `Order/WireGate`, `Route/Gate`; L7 `Core/Bridge.lean`; L8 `EnvironmentProofs`; L9 `Bridge.lean`, `Closure/Bridge.lean`, `Order/ProfileGate` | Step 7 lands after L5 and imports `Route/Dispatch`. Step 3b lands after L1 and L2, then removes the policy rows of the deleted modules. `Core.Bridge.runCase` is L7's to delete. Step 4a's `bind_ok` move edits `Order/ProfileGate.lean`: before or after L9, not during. Step 5a's corollaries for the `Bridge` runners wait for the L9 decision. Every new module here is registered with its layer: `VE.Kit.*`, `VE.Wire.Codec`, `VE.Limits` layer 1; `VE.Route.Kit.*`, `VE.Route.WireSound`, `VE.Norms.Lowering` layer 2; `VE.Service.Skeleton` layer 4 |
| **wire-contract S5** (`wire-s5/integrate`; shadow, S5-pre open with 3 + 6 verdict differences) | Generated `WireContract/Tables/*`, `Limits.lean`, `Names.lean`; `Hooks/{Norms,NormDefaults}.lean`; `Diagnose.lean`; `ve/norms_contract.py`, `ve/norm_defaults_contract.py`; call sites `ve/norm_admission.py:96`, `ve/norm_defaults_route.py:174` | The hooks call frozen code by name: `Norms.Wire.{maxNodes, maxIndex, budgetFormula, decodeNorm, decodeNormsEnvironment}`, `Norms.{pyRepr, termSort, height, precedenceNodes}`, `NormDefaults.Wire.{profilesOf, placeholderJson, profile}`, `Route.{dependencyOrder, DepNode}`, `Bridge.{fields, strings, formulaNodes}`. These names are covered by the facade rule in every step. No step edits a Norms or NormDefaults decoder, or their admission, until both S5 switches have landed (steps 4a for `decodeFilledDoc`, 4b instances, 6b for `Norms/Wire.maxNodes`). Steps 1a and 2a add files only and are safe now; 1b edits `Norms/Replay.lean` and `Norms/Run.lean`, which S5 does not touch |
| **wire-contract S4 items 2 to 6, S6 to S10** (planned) | Per-unit tables and hooks; `envelope@0.2`; the limits contract | Step 8b migrates a unit's decoder only after that unit's stage is public. Step 6b's `VE/Limits.lean` and the generated `WireContract/Limits.lean` should come from the same `limits.json`; agree this with the limits contract item. Error-envelope unification belongs to `envelope@0.2`, not to step 7 |
| **compose S2a** (`compose-s2/integrate`), **S2b** (planned) | New `Compose/Adjoin.lean` and about 30 `Readings/*.lean`; edits `Readings/{Wire,Run,Doc,Examples}.lean`, `VE.lean`, `Audit.lean`; `ve/readings_route.py`, `ve/document.py` | Step 9a waits for S2b (it removes the `hch` hypothesis and edits rights superposition). Step 5g goes in a new file after S2a merges. Composition's rule "a new layer restates no route theorem" is what step 9 extends backwards to the existing chains |
| **english-lean** (S0 and S1a in flight) | New `VE/Grammar/*`, later `VE/EnglishGrammar/*`, `ve/english_grammar/*.json`; no edit to an existing Lean file | No file overlap. Two requests to that workstream before its S2: (1) its planned `EFormula.encode` should be step 8a's encoder, or 8a adopts it, so that one more formula encoder does not appear; (2) `foldChar` is about to exist three times (Discourse, EnglishGrammar, the Python reference): one shared table module instead of a copy with an agreement test |

`VE.lean`, `VE/Audit.lean` and `frozen-sources.sha256` are appended to by every branch. Conflicts
there are mechanical: rebase, regenerate with the L0 tooling, rerun the audit.

## 7. Open questions

1. **Does the step 1 link hold on every admitted document?** It depends on whether a definition
   body may mention a regulated predicate and whether a defined predicate may carry a flag
   (step 1, risk). If the link is false somewhere, the Lean gate and the specification disagree
   today on those documents.
2. **Default authority.** Under `VE_AUTHORITY=python` the proofs here are cross-checks. How much
   of this plan should wait for, or be ordered by, migration stage 5?
3. **Equality or differential for step 3b.** If the closure and core checkers are not equal as
   functions (step counts, trace shapes), is OUT plus fuzzing enough evidence to delete the
   closure checker?
4. **`exact` for decoders.** Some decoders may accept non-canonical input (field order, optional
   fields). Each such tolerance is either a codec parameter or a wire tightening; the second is a
   signed change.
5. **Verdicts with no specification:** risk statuses built on `permittedAt` and `requiredAt`;
   rights couplings; `Readings.actOnly`. Prove against a new specification, or mark the output
   "not certified"?
6. **Rights and Discourse meaning (step 9d).** Declare the elaborator the meaning, or write an
   independent one? The first is cheaper and honest; the second is what RIGHTS.md and
   DISCOURSE.md currently claim.
7. **Error envelopes.** Routes differ in whether an error carries `valid:false` (correction 4).
   Step 7 preserves each shape. Should `envelope@0.2` make them one?
8. **Generic kits and readability.** A statement through `Extension` or `Lowering` is shorter
   but indirect. Proposal: each instance also states its unfolded theorem under the old name, so
   the reviewer reads the concrete statement and the kernel checks it against the generic one. Is
   that enough, and does `Time/Document` justify making the admission kit generic in `Semantics`?
9. **The strict-to-soft embedding (step 9b).** The composition plan lists it as unproved. Without
   it there are two chain families (W1 and soft). Is one family worth an XL proof?
10. **Python-side duplication.** The trust map did not audit Python internals. The five
    `ve/*_route.py` forwarders and `ve/alternatives.py` look like candidates for one adapter with
    one fail-closed rule, but that needs its own audit and must fit layers2 P22 and stage 5.
11. **Tagging for step 0.** Class tags as comments in Lean sources change every file hash once.
    A side table avoids that but can drift. Which one?
12. **Budget rule.** Should the trust budget block merges, or only report, until step 0's numbers
    have been checked against the trust map by a second reader?
