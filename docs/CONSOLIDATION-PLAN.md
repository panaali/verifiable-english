# Consolidation plan: a small core, shared kits, stated ties

Status: plan only, no code changes. Branch `design/consolidate` at `a093a14d` (main), 2026-10-03.
Converged review (`manage-agents/debates/design-consolidate`, round 3): BUILD with edits E1 to E9,
E3 replaced by E3′; those edits are applied below.

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
| 1 | Norms CONFLICT-FREE means `ConflictFree` | One conflict notion instead of two, stated on `Norms.Run.runCase` and the service path |
| 2 | One acceptance theorem for `runFol`, `runClosure`, `runOrder` | The three main runners stop being trusted glue, up to `Route.Run.runCase` |
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
   never renamed. The only exceptions are signed retirements listed by name in a step (today:
   step 6c's three legacy `Norms.Replay` functions and four `Replay.norms_wire_*` theorems); a
   retirement updates the audit, the feature documentation and the assurance-manifest theorem
   references in the same change.
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

**1a. Link theorems.** New file `lean/VE/Norms/FlaggedSpec.lean`; no existing file is edited.
Three theorems (E1):

* (α) A JSON-free semantic lemma: for a source whose `baseBackground` is well formed over
  `baseEnv`, `BaseConflictFree` on every structure admissible over `baseEnv` gives
  `ConflictFree D B` on every `B` with `BaseAdmissible D B` that satisfies the flag premises.
* (β) The replay theorem:

  ```lean
  theorem norms_flagged_conflict_free (j : Json) (r : ConflictReplay)
      (h : replayConflict j = .ok r) (hv : r.conflictFree = true) :
      Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true)
        = .ok r.src ∧
      ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B (flagPremises r.src) →
        ConflictFree r.src.D B
  ```

* (γ) `norms_wire_conflict_free`, naming `Norms.Run.runCase` and modelled on
  `norms_wire_acceptance`: its hypothesis is that the answer's `verdict` field is
  `CONFLICT-FREE`; its conclusion is (β)'s, for the decoded source.

Two rejection lemmas and one case go with them, settling what an earlier draft left open:

* *A flag on a defined predicate is rejected.* `Route/Wire.lean:112-114` rejects flags on defined
  predicates and `Norms/Wire.lean:142` on regulated ones, so `Sat B (flagPremises)` over the base
  vocabulary is the right hypothesis.
* *A definition body that mentions a regulated predicate is rejected.* `checkCertificate`
  requires `premises.all (·.check E [])` (`TableauChecker.lean:171`), `Formula.check` rejects
  undeclared predicates (`Syntax.lean:49-54`), and `baseEnv` hides regulated names, so any
  accepted target forces every definition premise to be free of regulated predicates.
* *No targets.* With an empty target list `ConflictFree` is vacuous.

(β) holds for both values of `plain`, and it is the exact statement the witness theorem refutes,
so a corollary states that the route cannot answer both CONFLICT-FREE and CONFLICT for one
document. Proof outline:

1. *Expansion.* By the second rejection lemma every definition body is over the base vocabulary.
   Every `B` with `BaseAdmissible D B` then extends to an `S` admissible over `baseEnv D` in
   which each defined symbol has its meaning evaluated in `B`, and forgetting the defined symbols
   gives back `B`. (`Structure.Admissible`, `Semantics.lean:24-28`, forbids true tuples of hidden
   predicates, so `S` cannot give a hidden regulated relation a non-trivial meaning; it does not
   need to.)
2. *Transfer.* Flag premises and literals are formulas over the base vocabulary
   (`RegulatedFlag`, `Norms/Wire.lean:142`), so `S` satisfies `baseBackground`.
3. *The two substitutions agree.* For such `S`, every `k` and every `φ` well formed over
   `envAt D k`: `(regSubst D.T k φ).denote S ρ ↔ (subst D.T k φ).denote B ρ`, by induction on `k`
   in the style of `Norms/Subst.lean`; the definition case uses the premise `d(x̄) ↔ body`.
4. `pyTargets` and `targets` list the same names and sorts in the same order; item 3 relates
   their formulas, so `BaseConflictFree src S` gives `ConflictFree D B`.

**1b. Correct the documentation (E3′).** Step 1 changes documentation only: the
`Norms/Run.lean` docstring, NORMS.md, METATHEORY.md, the spec (`docs/spec/norms.md`) and the
schema comment (`norms.json`) cite `Flagged.*` and the 1a theorems instead of the legacy
`Replay.norms_wire_*` theorems (TRUST-MAP section 10). The assurance manifest's two `theorems`
lists replace the four `Replay.norms_wire_*` names with 1a's three theorems,
`norms_flagged_witness_sound`, `norms_flagged_acceptance` and step 2a's norms corollary. The
legacy functions `Replay.replayConflict`, `replayWitness`, `replayEntailment` stay: they are
unused (their only references are their own theorems and `Audit.lean`), and their four theorems
name them, so they cannot become corollaries of the `Flagged` theorems (`Replay` cannot import
`Flagged`, and `plain = true` excludes the definitions the legacy decoder admits). Their deletion
is a signed retirement in step 6c.

**1c. The service path (E2, was 5e).** A corollary of (α) for `Service/FamilyNorms.conflictCase`
(lines 139–158), which issues the same verdict from the same `pyTargets` and `baseBackground`.

* **Trusted before → after:** the reviewer reads two conflict notions today: `ConflictFree`
  (S 31) and the nine definitions of `Flagged.lean:144-216` (`regTable`, `regSubst`, `conflictPy`,
  `outcomePy`, `pairConflictPy`, `pyTargets`, `baseEnv`, `baseBackground`, `BaseConflictFree`;
  about 45 code lines). After 1a the nine are checked code and only `ConflictFree` is read:
  9 trusted definitions, about 45 lines, become tied (not removed); the `norms-conflict` branch
  of `Norms/Run` and the service's conflict case become tied. 1b removes nothing.
* **API kept:** all `Flagged.*` and `Replay.*` names in step 1; wire output unchanged. The three
  legacy replay functions and four `Replay.norms_wire_*` theorems are later retired by name in
  step 6c, the one signed exception to rule 1.4.2 in this plan.
* **Evidence:** 1a and 1c add theorems only (L, ST shows additions only). 1b: documentation and
  manifest references only; the manifest check and `test_norms_three_way`,
  `tests/test_stage2_norms.py` stay green.
* **Risk:** behaviour none. Proof risk medium, in items 1 and 3.
* **Effort:** 1a L; 1b S; 1c M.

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

1. `fullLayer rv hd : Layer fol Unit`: the definitions layer composed over the identity layer whose
   admissibility is "structurally admissible, flags hold, literals distinct", with
   `BackgroundSound (fullLayer rv hd) ((fullBackground rv).map Prod.fst)`. `RouteVocabulary` already
   carries `chain` and `nodup` (`Route/Wire.lean:33,36`). One decoder fact is needed, `hd :
   FlagsBase rv`: no flag names a defined predicate, so forgetting the defined tables keeps the
   flags and every base structure has its expansion (`Norms.FlaggedSpec.
   decodeVocabulary_flag_not_defined`, discharged at `Route.Run.runCase`).
2. One record and three claim predicates, which are what the reviewer reads instead of the
   runners. The fol family's `Intended` is `Definitions.Intended ∧` the flags' `Intended`, as
   `decodeDataModel_combined` states, not `Sat S fullBackground`:

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
3. One acceptance theorem over `Family` plus `Checker` (E4), proved once, by `bind_ok`
   inversion instead of ten hypotheses, and three instances whose `run` is `runFol`,
   `runClosure` (through `Closure.embed` and conservativity) and `runOrder`, each by `rfl`. The
   runners return `Json` (`Route/Wire.lean:505,539,610`), so the hypothesis reads the answer's
   `"valid"` field (`runFol … "certificate" j = .ok out → out.getObjValD "valid" = true`), and the
   conclusion includes the source-decode and `bindingOk … = .ok ()` conjuncts as well as the
   claim. The order family's `Intended` is "admissible and order literals distinct";
   `RouteOrderVocabulary` has no flags or definitions, and the lemma says so. The countermodel and
   evaluate kinds use `decodeDataModel_combined`, `refutesF/C_sound`, `valuesF/C_sound`.
4. One corollary per family naming `Route.Run.runCase`, so the claim reaches the public entry
   (`Route.Run.dispatch`, `Route/Run.lean:65-122`) and not only the runner.

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
| 3a | Prove the equality on `replay` with both flags explicit: closure's `replay E a b` on a certificate equals Core's `replay E a b` on its embedding (`embedClosure`, `embedCert`), for all `a b`, plus the same for the trace decoders and `Steps.closure` vs `Steps.core`. The equality of the two `checkCertificate`s is false: Core accepts only `ve-tableau-core-checker@1` and runs `replay E true true` (`Core/TableauExtendedChecker.lean:223-225`), closure accepts `@0` and `@1` and runs `replay E true (version == @1)` (`TableauExtendedChecker.lean:223-226`) | none (theorem only) | L, ST | Low; L. The files are copies, so the proof is a parallel induction; if step counts differ, 3b must keep `Steps.closure` |
| 3b | `runClosure` and `CertificateWire.runClosureCase` call the Core `replay` behind an atom-free gate, keeping closure's own version gate (`@0` and `@1`, second flag `version == @1`) so `@0` certificates keep their verdicts. Delete `VE/TableauExtended*` (6 files, 1,075 lines) and the closure files that only that tableau uses, `Closure/{PathRules,Induction,Substitution,Congruence}` (473 lines; confirm with `lake build`) | K 0; removes about 1,550 untrusted lines (C and P) and one of the three trace decoders (D, about 30 est.) | 3a's theorem; OUT; closure three-way; `rust/fuzz_closure.py`; `test_closure*.py` | Medium; L. Error text for rejected certificates must not change |
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
copies today); one readings-choice check (four copies); `VE.Graph` becomes the FOL instance of a
generic graph (E6). `Service/GenericGraph.lean` imports nothing, but `VE.Service.*` is layer 4 and
`VE.ClaimGraph` layer 1 (`tools/layer_policy.py:114,123`), so the generic graph first moves to a
layer-1 module, with `Service/GenericGraph` kept as a facade; checker and report correspondence
between the generic instance and today's `VE.Graph` is proved before `VE.Graph` is redefined.
(`graph_certificateSound_iff`, `Route/Checker.lean:71`, relates `VE.Graph.CertificateSound` to
`Route.CertificateSound` and never mentions `GenericGraph`, so it is not that evidence.)

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
| 5e | `Service/FamilyNorms.runCase` | Moved into step 1 as 1c (E2) | — |
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
| 6c | Delete dead code: `Definitions/Alias.lean` (60), `SurfaceProofs.lean` (197, subsumed by `RoundTrip.parse_print`), `Rights.Projections.owes` and `free`, Readings `Coupling`, `Narrowing`, `AchievesQuiet`. Signed retirement (E3′, the exception to rule 1.4.2): `Norms.Replay.replayConflict`, `replayWitness`, `replayEntailment`, the four `Replay.norms_wire_*` theorems and their four `#print axioms` lines; gated on step 1a merged, no reference outside `Replay.lean` and `Audit.lean` (checked at the step), and the audit, feature documentation and assurance-manifest theorem references updated in the same change. Shared `Replay` types and helpers used by `Flagged` and the service (`EntailmentReplay`, `WitnessData`, `targets`, `conflictFreeCheck`, `decodePackage`, `witnessFrom`) stay | S about −30; about 300 untrusted lines, plus about 110 for the retirement (no trust credit) | `lake build`; ST lists the deleted names (seven for the retirement); OUT unchanged | S |
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
  60 encoder lines are read instead. Encoder copies removed: about 80 lines. A decoder counts as
  tied only where `exact` holds, or holds up to a reviewed normalisation relation (E7); `round`
  alone says nothing about arbitrary accepted JSON and earns no credit.
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

The meaning-policy choice an earlier draft listed as 9d (Rights: `correlate` as the meaning;
Discourse: `Acc`) changes reviewed statements, so it is not a behaviour-preserving consolidation
and is out of this plan's budget (E8); it is open question 6.

* **API kept:** all route theorem names with unchanged statements (ST).
* **Evidence:** ST and OUT (no executable changes in 9a and 9b; 9c changes generators, so the
  equality `newGen = oldGen` is proved first); rights, soft-norms, norm-defaults, alternatives and
  risk three-way and differential suites.
* **Risk:** medium (frozen statements; compose in flight). **Effort:** 9a L; 9b XL; 9c M each.

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

Accounting rules (E9). Each declaration is credited once: a declaration tied in one step and
deleted in a later one counts in only one of the two columns. Every figure is net of the trusted
declarations a step adds, helpers included. Tied and removed lines are kept apart. All totals in
this section are estimates ("est.") until step 0's ledger replaces them and re-ranks steps 5
to 10; that recount does not delay steps 1a and 2a, which add theorems only.

| Step | Removed | Tied | Days | Risk | Score | Depends on |
|---|---:|---:|---:|---:|---:|---|
| 1 Norms conflict | 0 | 60 | 5 | 1.5 | 8 | none (theorem only) |
| 2a Runner theorems | 0 | 125 | 4 | 1 | 31 | none (theorem only) |
| 3 One logic | 80 | 0 | 14 | 2 | 3 | layers2 L1, L2 before 3b |
| 4 Statement kit | 650 | 0 | 14 | 2 | 23 | 4a first; S5 switch before Norms, NormDefaults |
| 5 Remaining ties | 0 | 1,700 | 14 | 1 | 121 | 5a after 2a |
| 6 Hygiene | 110 | 0 | 3 | 1 | 37 | 6c's retirement after 1a |
| 7 Skeleton | 340 | 300 | 6 | 2 | 53 | layers2 L5 |
| 8a Formula codec | 80 | ≤ 450 | 10 | 1.5 | ≤ 35 | better after 3c; credit only under `exact` (E7) |
| 8b Combinators | unknown | unknown | 30+ | 3 | n/a | 8a; each unit's wire stage |
| 9 Normative core | 400 | 0 | 18 | 2 | 11 | compose S2b before 9a |
| 10 Fixtures | 0 | 0 | 4 | 1 | n/a | none |

By estimated score alone the order would be 5, 7, 6, 8a, 2a, 4, 9, 1, 3; the measured ledger
(4.1) re-ranks steps 5 to 10 as 7, 5, 8a, 6, 9, 10. The plan follows the DRI's order for 1 to 4
for these reasons:

* Step 1 has a low score and still goes first. It is the one place where a public verdict means
  something other than the reviewed specification, and no other step can be trusted to "mean the
  spec" until it does.
* Step 2 gives step 5a its generic theorem.
* Step 3's theorem-only halves (3a, 3d) and step 5's rows touch no existing file, so they run in
  parallel with everything.

Suggested calendar: week 1: steps 1a, 1c, 2a, 0, 6. Weeks 2 and 3: 3a, 3d, 4a, 4b with its first
instances, and step 5 rows. Weeks 4 and 5: 3b, 3c, 2b, 4c, 4d, 7. Later, gated on other
workstreams: 8, 9.

Step 3's low score is honest: the closure copies are mostly checked code and proof, which the
trust map does not count as trusted. Its gain is one fewer `denote` to read (K 76 → 25) and
about 1,550 fewer lines to maintain.

Expected result (est.), to be replaced by measured numbers from step 0: about 1,650 trusted lines
removed and about 2,650 tied, out of about 25,000, before step 8b. Per feature added afterwards,
the trusted text is its `Doc`, its `Intended` and its codec description.

### 4.1 Measured ledger (E9)

Step 0's tool now measures the table above. `tools/consolidation-ledger.json` names, for each
step, the declarations it removes, ties or reclassifies (module globs and name patterns taken
from the step's text), and `python3 tools/trust_map.py --ledger` counts their trusted lines (K, S
and untied [V]) under the reviewed side table, crediting each declaration to the first step that
names it. Lines the step names that are already untrusted (C, P, T, [R], [I], tied) earn nothing.
It validates the side table exactly as `--check` does (one shared pass and trust rule) and
prints no ledger while any classification or tie problem stands.
`Adds (est.)` is the only estimate left: the trusted lines a step introduces (3c's aliases, 4b's kit, 7's skeleton, 8a's canonical encoders), subtracted in `Net`.
Measured on the table after consolidate-b1 fix 4 (K 978, S 7,550, trusted 25,641 of
88,757 lines; step 5 remeasured after the 2026-10-05 merge of ve-integration, whose
`VE.Discourse.Run` rewrite moved 3 of its tied lines, and again after the merge into lean-first/b3b, whose
`Readings.Run.setFindings` and `Readings.Separate.actOnly` rewrites (each side built once) moved 4 more, and after the merge into lean-first/b3d, whose `Readings.Run` pair rewrite (each candidate's layers built once, `pairFactsIn`) adds 1; steps 6 and 7 remeasured after the second
2026-10-05 merge, which brought english-lean, compose-s2 and difffuzz. Step 7's `*Main.lean`
selector now also names `EnglishLeanBenchMain.lean`, english-lean's measurement executable (156 of
the 159 added lines; no admission path reads it, and the seeded table counts it untied [V] by
default): whether it belongs to the skeleton step or should be classed outside [V] is open for
the DRI. Step 6 counts 503 more [V] diagnostic lines than at fix 4, from the two merges: mostly
`WireContract/Hooks/Norms` (417) and `Hooks/NormDefaults` (79)). Steps 7 and 8b remeasured after the merge
of ve-integration into lean-first batch 1 (2026-10-05), which deleted the thirteen one-shot route executables (their
`*Main.lean` roots, `EnglishLeanBenchMain.lean` kept) and the route modules' `main` batch loops: 211 of step 7's
trusted lines are gone already, and 20 of 8b's (`VE.Time.Wire.main`); the service's own batch loop is the one left.
Batch 1's new modules (`ResponseShape`, `VE/Service/*`) were classified by `--seed` and no step names them.
Step 7 remeasured again after the merge of that ve-integration into english-lean-s2/integrate (2026-10-05):
S2.4's `ve_english_route` (`EnglishGrammar.Run`'s `runCaseReported` and `main`, and `EnglishMain.lean`), a
one-shot executable by english-lean-s2.md 2.10 and, at that point, the only one-shot route left beside
`ve_conformance`, added 33 trusted lines to batch 1's 551. Batch 11a then added the W2 speech-source executable;
the current measurements follow:

| Step | Removed | Tied | Reclassified [V]→[R] | Adds (est.) | Net | Days | Risk | Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 23 | 0 | 0 | 23 | 5 | 1.5 | 3.1 |
| 2a | 0 | 0 | 0 | 0 | 0 | 4 | 1 | 0.0 |
| 2b | 94 | 0 | 0 | 0 | 94 | 2 | 2 | 23.5 |
| 3 | 39 | 0 | 0 | 10 | 29 | 14 | 2 | 1.0 |
| 4 | 718 | 0 | 0 | 420 | 298 | 14 | 2 | 10.6 |
| 5 | 0 | 485 | 0 | 0 | 485 | 14 | 1 | 34.6 |
| 6 | 35 | 0 | 1758 | 0 | 35 | 3 | 1 | 11.7 |
| 7 | 588 | 0 | 0 | 60 | 528 | 6 | 2 | 44.0 |
| 8a | 106 | 225 | 0 | 60 | 271 | 10 | 1.5 | 18.1 |
| 8b | 0 | 3502 | 0 | 0 | 3502 | 30 | 3 | 38.9 |
| 9 | 88 | 0 | 0 | 0 | 88 | 18 | 2 | 2.4 |
| 10 | 0 | 0 | 0 | 0 | 0 | 4 | 1 | 0.0 |

What the measurement changes:

* **Re-ranking of steps 5 to 10 by measured score:** 7 (43.9), 5 (34.6), 8a (18.1), 6 (11.7),
  9 (2.4), 10. Step 8b's 3,460 is an upper bound (every untied line of the eight units' `Wire.lean`
  files, on the assumption that every decoder gets `exact`), not a forecast; it stays ranked by its
  pilot (Alternatives) as section 3 says. Against the estimates, 7 overtakes 5 (762 trusted
  dispatch and `main` lines, not 340; 603 before the bench executable; 551 once batch 1 deleted the one-shot routes; 584 with english-lean S2's `ve_english_route`; 587 after batch 11a added the W2 `ve_speech_acts_route`) and 5 is smaller than estimated (485 measured against 1,500 to
  2,000): most of the rows' targets are short runners, and `scopedVerdict` and `weighingWitness`
  are already C.
* **Step 6** removes almost nothing trusted: the SHA-256 copy and the `maxNodes` sites are [I] and
  [R], and the dead code is mostly P. Its value is 6e: 1,758 lines of `WireContract/*`,
  `SoftNorms/Phases`, `Service/TypingDiagnostic` and `Norms/Tree` diagnostics are counted [V]
  until marked [R]. That moves lines out of the reading load without a theorem, so it is shown
  apart from `Net`.
* **Step 4** removes 718 trusted lines of admission skeleton for an estimated 420-line kit (net
  298, not 650); **step 3** removes 39 trusted lines (its gain is the 1,550 untrusted lines and one
  `denote`, as section 4 already says); **step 9** has 88 measured lines before 9b's lowering, which
  cannot be measured until it exists.
* **Step 1:** 1a and 1b are done; the nine `Flagged` definitions are C, and `BaseConflictFree` is
  tied by `conflictFree_of_base` in the side table. The remaining 23 lines are 1c's
  `FamilyNorms.conflictCase`.
* **Step 2a:** done (`VE.Route.WireSound`, `VE.Route.RunSound`, `VE.Norms.RunSound`). The side
  table ties `runFol`, `runClosure` and `runOrder` (114 G[V] lines) to their certificate,
  countermodel and evaluate theorems, so the row now measures 0. `Runner.acceptance` goes through
  each family's layer: `fullLayer` (item 1) for FOL, the same layer over closure formulas for
  closure, the identity layer of `OrderStringAdmissible` for order; with `BackgroundSound` of the
  layer it gives `CertificateClaim` (`route_intended`) and `BaseClaim` (`route_base`, unique
  expansion, which step 5b reuses). Measured with `tools/trust_map.py --since` against the parent
  tree, not estimated, the step adds 128 S lines (`Family`, `CertificateClaim`, `BaseClaim`,
  `CountermodelAnswer`, `CountermodelClaim`, `EvaluateClaim`, `RouteIntended`, `FlagsBase`,
  `FlagsHold`, `BaseAdmissible`, `Runner.Bound` and the three family instances, docstrings
  included), covered by a signed allowance in `docs/trust-baseline.json`, and no K or untied [V]
  line: the model decoders the claims name (`routeModel`, `orderModel`, D[V] 16) are offset by
  the 114 tied lines. The layer constructions (`fullLayer`, `Layer.within`, `Layer.toClosure`)
  are C: their meaning is stated by `fullLayer_admissible_in`, `fullLayer_admissible_out`,
  `fullLayer_intended` and `fullLayer_premises`. Net +30 trusted lines, against the estimated
  −84: the claims cover all three kinds of all three runners and the expansion, not the
  certificate kind alone, and the family instances are read.
* Steps 1 to 4 keep the DRI's order (section 4 above). After step 2a the measured total before 8b
  is 2,575 trusted lines removed or tied (net 2,025 after 550 estimated additions) out of 25,641,
  against the estimate of about 4,300.

The budget check (step 0) now also fails a predicate (a declaration whose type ends in `Prop`,
listed in `lean/predicates.txt`) classed C, [R] or [I] without a tie: such a class took
`Closure.Formula.WellFormed`, the kernel typing predicate, out of K (consolidate-b1 review B).

A declaration is its full name and its defining module together: the statement dump's `uses`
lines and the predicate list write each constant as `name@Module`, and a tie, an anchor or a
predicate matches only the declaration of that module. Two files nothing imports together may each
define `VE.Demo.anchor`; a tie through the C one validated against an S namesake before
(consolidate-b1c looprecheck 1, B). The predicate list now reads every file of the tree, each
module outside `VE` (the executables' roots, the unimported `WireContract` files) imported alone,
and the budget check fails a file the list did not read.

The declarations themselves come from the compiled environment, not from reading the source
(consolidate-b1 fix 4, B): `lean/declarations.txt`, written with the two dumps, lists each
module's constants with their kind and source range and the hash of the source compiled. A quoted
`def «WellFormed»` was recorded as `VE.Demo.«WellFormed»` and `def WellFormed(n : Nat)` as
`WellFormed(n`, so a C entry under that spelling hid the predicate `VE.Demo.WellFormed`; anonymous
instances now carry Lean's generated names. The source text only places line boundaries, and a
file whose source differs from the compiled one fails every entry point. Measured against the
scanner, this moved the 8 S lines of two `LawfulBEq` instances, which Lean compiles as theorems,
into P, and corrected extents the scanner's docstring lexer got wrong after a `'"'` literal in
`Discourse/Access.lean` (S −7, D +7, of which [V] +4) and for the `ve_diagnose` main, whose
docstring a comment line separates from it ([V] +2); the baseline's history records the change.

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
| **wire-contract S5** (`wire-s5/integrate`; shadow, S5-pre open with 3 + 6 verdict differences) | Generated `WireContract/Tables/*`, `Limits.lean`, `Names.lean`; `Hooks/{Norms,NormDefaults}.lean`; `Diagnose.lean`; `ve/norms_contract.py`, `ve/norm_defaults_contract.py`; call sites `ve/norm_admission.py:96`, `ve/norm_defaults_route.py:174` | The hooks call frozen code by name: `Norms.Wire.{maxNodes, maxIndex, budgetFormula, decodeNorm, decodeNormsEnvironment}`, `Norms.{pyRepr, termSort, height, precedenceNodes}`, `NormDefaults.Wire.{profilesOf, placeholderJson, profile}`, `Route.{dependencyOrder, DepNode}`, `Bridge.{fields, strings, formulaNodes}`. These names are covered by the facade rule in every step. No step edits a Norms or NormDefaults decoder, or their admission, until both S5 switches have landed (steps 4a for `decodeFilledDoc`, 4b instances, 6b for `Norms/Wire.maxNodes`). Steps 1a, 1c and 2a add files only and are safe now; 1b edits only the `Norms/Run.lean` docstring and documentation, which S5 does not touch; 6c's retirement edits `Norms/Replay.lean`, which S5 does not touch either |
| **wire-contract S4 items 2 to 6, S6 to S10** (planned) | Per-unit tables and hooks; `envelope@0.2`; the limits contract | Step 8b migrates a unit's decoder only after that unit's stage is public. Step 6b's `VE/Limits.lean` and the generated `WireContract/Limits.lean` should come from the same `limits.json`; agree this with the limits contract item. Error-envelope unification belongs to `envelope@0.2`, not to step 7 |
| **compose S2a** (`compose-s2/integrate`), **S2b** (planned) | New `Compose/Adjoin.lean` and about 30 `Readings/*.lean`; edits `Readings/{Wire,Run,Doc,Examples}.lean`, `VE.lean`, `Audit.lean`; `ve/readings_route.py`, `ve/document.py` | Step 9a waits for S2b (it removes the `hch` hypothesis and edits rights superposition). Step 5g goes in a new file after S2a merges. Composition's rule "a new layer restates no route theorem" is what step 9 extends backwards to the existing chains |
| **english-lean** (S0 and S1a in flight) | New `VE/Grammar/*`, later `VE/EnglishGrammar/*`, `ve/english_grammar/*.json`; no edit to an existing Lean file | No file overlap. Two requests to that workstream before its S2: (1) its planned `EFormula.encode` should be step 8a's encoder, or 8a adopts it, so that one more formula encoder does not appear; (2) `foldChar` is about to exist three times (Discourse, EnglishGrammar, the Python reference): one shared table module instead of a copy with an agreement test |

`VE.lean`, `VE/Audit.lean` and `frozen-sources.sha256` are appended to by every branch. Conflicts
there are mechanical: rebase, regenerate with the L0 tooling, rerun the audit.

## 7. Open questions

1. *(Closed by E1.)* Whether the step 1 link holds on every admitted document is settled by the
   existing checks: flags on defined predicates and definition bodies that mention a regulated
   predicate are both rejected (step 1a's rejection lemmas), and the empty-target case is
   vacuous.
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
6. **Rights and Discourse meaning (formerly step 9d; outside the consolidation budget, E8).**
   Declare the elaborator the meaning, or write an independent one? The first is cheaper and
   honest; the second is what RIGHTS.md and DISCOURSE.md currently claim. The earlier 9d text:
   a feature's `Intended` must not call its own elaborator's helpers, checked by an import rule
   (`X.Semantics` does not import `X.Elaborate` or `X.Correlate`). Rights: declare `correlate`
   the meaning and drop `ValueRight` and the `*X` layer (S −340), or rewrite `ValueRight` without
   `nodeOf`, `ownGuard`, `limPack`. Discourse: give `Acc` an independent definition or document
   it as code-as-spec; remove the identity `canonTarget` and `AliasEq` (−70). Either choice
   changes reviewed statements and needs statement review and a DRI decision.
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
