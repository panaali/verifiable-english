import VE.Norms.Replay
import VE.Route.Flags

/-! `data@0` flags on the norms route outside document admission (the migration
plan's stage 2c), and conflict certificates over Python's base Background.

Python generates Background in the order flags, definitions, literals, profile
(`ve/background.py`). Flags name ordinary binary predicates: a regulated
predicate cannot carry one (`RegulatedFlag`), so every flag premise is a base
formula. Nothing here changes the norms theory: flag premises are regenerated
from the decoded declarations and enter each check as a prefix of its premise
list, and each theorem below takes them as a hypothesis.

* `norms-elaborate`: the regenerated output with the flag premises first in
  Background (generator `flags`). `fragment` is false when a `total` flag is
  declared: the small-model restriction (`conflict_smallModel`) keeps
  universal premises such as `functional` but not the `∀∃` premise of `total`,
  so the bound says nothing about witnesses that must satisfy it.
* `norms-certificate`: the unchanged checker over
  `flags ++ Background ++ layer premises ++ Γ` (`norms_flagged_acceptance`).
* `norms-conflict` with certificates: a document with neither flags nor
  definitions keeps the frozen check over `E_base` and `Background_base`
  (`Replay.norms_wire_conflict_sound`). Otherwise each target certificate is
  bound to and checked over Python's base environment (the complete
  environment with the regulated predicates hidden, `baseEnv`) and Python's
  Background there, `flags ++ definitions ++ literals` (`baseBackground`),
  against Python's conflict formulas, which expand earlier regulated atoms
  but keep defined ones (`pyTargets`) (`norms_flagged_conflict_sound`).
* `norms-conflict` with a witness: the base model must also satisfy every flag
  (`InvalidModel(flags)` otherwise, checked after the structural checks and
  before the literals, in Python's order); witnesses over documents with
  definitions are not implemented. -/
namespace VE.Norms.Flagged
open Lean
universe u

/-- Python `_flag_premises` over the decoded declarations. -/
def flagPremises (src : Wire.Source) : List VE.Formula :=
  VE.Data.Background.generate src.ne.rv.flags

/-- Whether some declaration carries a `total` flag. -/
def hasTotal (src : Wire.Source) : Bool := src.ne.rv.flags.any (·.total)

/-- `Wire.regenerated` with the flag premises first in Background, and the
fragment flag false under a `total` flag. -/
def regenerated (src : Wire.Source) : List (String × Json) :=
  (Wire.regenerated src.D).map fun (key, value) =>
    if key == "background" then
      (key, Json.arr (((flagPremises src).map (fun a =>
        Json.mkObj [("generator", .str "flags"), ("ast", Wire.enc a)])).toArray ++
        (value.getArr?.toOption.getD #[])))
    else if key == "fragment" then
      (key, .bool (InFragment src.D && !hasTotal src))
    else (key, value)

/-! ## Entailment certificates -/

/-- The unchanged checker on the regenerated `flags ++ Background ++ layer
premises ++ Γ`. -/
def valid (r : Replay.EntailmentReplay) : Bool :=
  VE.Tableau.checkCertificate (envAt r.src.D (size r.src.D))
    (flagPremises r.src ++ background r.src.D ++ elaborate r.src.D.T ++ r.premises) r.conclusion r.cert

/-- `Replay.replayEntailment` with flags admitted: the certificate must bind the
complete source environment, the regenerated flag premises, Background and
layer premises followed by the case's premises, and the conclusion. -/
def replayEntailment (j : Json) : Except String Replay.EntailmentReplay := do
  let environment ← j.getObjVal? "environment"
  let src ← Wire.decodeSource environment (j.getObjValD "norms") (flags := true)
  let E := envAt src.D (size src.D)
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk src.ne.profiles (← Wire.canonicalEnvironmentJson environment)
    ((flagPremises src ++ background src.D ++ elaborate src.D.T).map VE.Route.Wire.encodeFormula ++
      (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure ⟨src, ps, c, cert⟩

theorem replayEntailment_source (j : Json) (r : Replay.EntailmentReplay)
    (h : replayEntailment j = .ok r) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok r.src := by
  unfold replayEntailment at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  rw [he]; exact hd

/-- `norms_flagged_acceptance`: from a successful raw replay with an accepted
certificate, for the document decoded from that very input, (1) the conclusion
holds in every admissible structure satisfying the flag premises, the direct
semantics, the definitions, the profile, `Background_base` and the premises; and
(2) with no flag declared, the second half of `Replay.norms_wire_acceptance`
(base consequence for a conflict-free document). -/
theorem norms_flagged_acceptance (j : Json) (r : Replay.EntailmentReplay)
    (h : replayEntailment j = .ok r) (hv : valid r = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok r.src ∧
    (∀ S : VE.Structure.{u}, S.Admissible (envAt r.src.D (size r.src.D)) →
      Sat S (flagPremises r.src) → holdsCatala r.src.D.T S →
      definitionsHold r.src.D S → profileHold r.src.D S → Sat S (backgroundBase r.src.D) →
      Sat S r.premises → r.conclusion.denote S []) ∧
    (flagPremises r.src = [] →
      (∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → ConflictFree r.src.D B) →
      (∀ a ∈ r.premises, a.WellFormed (envAt r.src.D 0) []) → r.conclusion.WellFormed (envAt r.src.D 0) [] →
      ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B r.premises → r.conclusion.denote B []) := by
  refine ⟨replayEntailment_source j r h, fun S hS hF hcat hdef hprof hbase hΓ => ?_, fun hF hc hΓ hφ => ?_⟩
  · have hsat : Sat S (flagPremises r.src ++ background r.src.D ++ elaborate r.src.D.T ++ r.premises) := by
      intro a ha
      rcases List.mem_append.mp ha with ha | ha
      · rcases List.mem_append.mp ha with ha | ha
        · rcases List.mem_append.mp ha with ha | ha
          · exact hF a ha
          · simp only [background, List.mem_append] at ha
            rcases ha with (ha | ha) | ha
            · exact hdef a ha
            · exact hbase a ha
            · exact hprof a ha
        · exact (elaborate_iff r.src.D r.src.wf S).mpr hcat a ha
      · exact hΓ a ha
    exact VE.Tableau.checkCertificate_sound.{u} _ _ _ r.cert hv S hS hsat
  · have hv' : VE.Tableau.checkCertificate (envAt r.src.D (size r.src.D))
        (background r.src.D ++ elaborate r.src.D.T ++ r.premises) r.conclusion r.cert = true := by
      have := hv
      simp only [valid, hF, List.nil_append] at this
      exact this
    exact (norms_route_acceptance r.src.D r.src.wf hc r.premises r.conclusion r.cert hv').2 hΓ hφ

/-! ## Conflict certificates over Python's base Background -/

/-- Python `_expand`'s table: like `expTable`, the pushed-down outcome of every
earlier regulated predicate, but a defined predicate's atom is kept (its
meaning is a Background premise over the base environment, not a
substitution). -/
def regTable (T : Tree) : Nat → Table
  | 0 => fun _ => none
  | k + 1 => fun n => match (syms T)[k]? with
    | some (.reg r) => if n = r.name then some (substWith (regTable T k) (outcome T r)) else regTable T k n
    | _ => regTable T k n

def regSubst (T : Tree) (i : Nat) (φ : VE.Formula) : VE.Formula := substWith (regTable T i) φ

/-- Python's conflict formula of a regulated predicate: `P_p ∧ N_p` with the
earlier regulated atoms expanded. -/
def conflictPy (D : Doc) (r : Regulated) : VE.Formula :=
  .and (regSubst D.T (before D r.name) (pos D.T r.name)) (regSubst D.T (before D r.name) (neg D.T r.name))

def outcomePy (D : Doc) (n : String) : VE.Formula :=
  match D.T.regulated.find? (·.name == n) with
  | some r => regSubst D.T (before D n) (outcome D.T r)
  | none => .bottom

/-- Python's conflict formula of a declared pair. -/
def pairConflictPy (D : Doc) (pr : Pair) : VE.Formula :=
  .and (outcomePy D pr.req) (.not (outcomePy D pr.perm))

/-- Python `NormDocument.conflict_targets`, in its order: the formulas are over
the base environment with defined predicates, which `baseBackground` defines. -/
def pyTargets (D : Doc) : List (String × List String × VE.Formula) :=
  (syms D.T).filterMap (fun | .reg r => some (r.name, r.sorts, conflictPy D r) | .defn _ => none) ++
    (pairs D.T).map (fun pr => (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflictPy D pr))

/-- Python `NormDocument.base_environment`: the complete environment with the
regulated predicates hidden. Defined predicates stay. -/
def baseEnv (D : Doc) : VE.Environment := hide D.E (D.T.regulated.map (·.name))

/-- Python's Background over the base environment, in generator order: flags,
definitions, literals. The base environment declares no regulated predicate,
so it has no profile premise. -/
def baseBackground (src : Wire.Source) : List VE.Formula :=
  flagPremises src ++ definitionPremises src.D.T ++ backgroundBase src.D

/-- Every target has an accepted certificate for
`baseBackground ⊢ ∀x̄. ¬conflict` over `baseEnv`. -/
def conflictFreeCheck (src : Wire.Source) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (pyTargets src.D).length == certs.length &&
    ((pyTargets src.D).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (baseEnv src.D) (baseBackground src) (targetConclusion t) c
      | none => false)

theorem conflictFreeCheck_target {src : Wire.Source} {certs : List (Option VE.Tableau.Certificate)}
    (hc : conflictFreeCheck src certs = true) {t : String × List String × VE.Formula}
    (ht : t ∈ pyTargets src.D) :
    ∃ c, VE.Tableau.checkCertificate (baseEnv src.D) (baseBackground src) (targetConclusion t) c = true := by
  simp only [conflictFreeCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < (pyTargets src.D).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : (t, certs[i]) ∈ (pyTargets src.D).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  have := hall _ hmem
  cases hci : certs[i] with
  | none => rw [hci] at this; cases this
  | some c => rw [hci] at this; exact ⟨c, this⟩

/-- No Python conflict formula holds on a typed tuple of a structure
admissible over `baseEnv` that satisfies `baseBackground`. -/
def BaseConflictFree (src : Wire.Source) (S : VE.Structure.{u}) : Prop :=
  ∀ t ∈ pyTargets src.D, ∀ vs, VE.TupleTyped S t.2.1 vs → ¬ t.2.2.denote S (tupleVal vs)

theorem conflictFreeCheck_sound (src : Wire.Source) (certs : List (Option VE.Tableau.Certificate))
    (hc : conflictFreeCheck src certs = true) (S : VE.Structure.{u})
    (hS : S.Admissible (baseEnv src.D)) (hB : Sat S (baseBackground src)) : BaseConflictFree src S := by
  intro t ht vs hvs
  obtain ⟨c, hcc⟩ := conflictFreeCheck_target hc ht
  have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc S hS hB
  exact (bindAll_denote_nil S _ _).mp he vs hvs

/-- `Replay.decodePackage` over `baseEnv` and `baseBackground`. -/
def decodePackage (src : Wire.Source) (environment norms packages : Json)
    (t : String × List String × VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let profiles := src.ne.profiles
  let some baseEnvJson := (Replay.baseEnvironmentJson environment).toOption | none
  let some baseProfiles := (VE.Bridge.strings (baseEnvJson.getObjValD "profiles")).toOption | none
  let some canonical := (Wire.canonicalEnvironmentJson environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId profiles canonical).toOption | none
  let some docHash := (Replay.documentHash profiles environment norms).toOption | none
  let package := packages.getObjValD t.1
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str t.1 do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  let bound := VE.Route.Wire.bindingOk baseProfiles baseEnvJson
    ((baseBackground src).map VE.Route.Wire.encodeFormula) (VE.Route.Wire.encodeFormula (targetConclusion t))
    c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
  match bound with
  | .ok () => some c
  | .error _ => none

/-- A replayed conflict case. `plain` (no flag and no definition) selects the
frozen check. -/
structure ConflictReplay where
  src : Wire.Source
  plain : Bool
  certs : List (Option VE.Tableau.Certificate)
  outer : List Bool

/-- The targets the case checks: the frozen ones, or Python's. -/
def ConflictReplay.targets (r : ConflictReplay) : List (String × List String × VE.Formula) :=
  if r.plain then VE.Norms.targets r.src.D else pyTargets r.src.D

def ConflictReplay.conflictFree (r : ConflictReplay) : Bool :=
  if r.plain then VE.Norms.conflictFreeCheck r.src.D r.certs else conflictFreeCheck r.src r.certs

/-- The certificate check of one target, as the case's verdict uses it. -/
def ConflictReplay.accepts (r : ConflictReplay) (t : String × List String × VE.Formula)
    (c : VE.Tableau.Certificate) : Bool :=
  if r.plain then VE.Tableau.checkCertificate (envAt r.src.D 0) (backgroundBase r.src.D) (targetConclusion t) c
  else VE.Tableau.checkCertificate (baseEnv r.src.D) (baseBackground r.src) (targetConclusion t) c

def replayConflict (j : Json) : Except String ConflictReplay := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  let src ← Wire.decodeSource environment norms (flags := true)
  let plain := src.ne.rv.flags.isEmpty && src.D.T.definitions.isEmpty
  let packages := j.getObjValD "packages"
  let ts := if plain then targets src.D else pyTargets src.D
  pure ⟨src, plain, ts.map (fun t =>
      if plain then Replay.decodePackage src.D src.ne.profiles environment norms packages t
      else decodePackage src environment norms packages t),
    ts.map (fun t => Replay.outerBound src.ne.profiles environment norms packages t.1)⟩

/-- `norms_flagged_conflict_sound`: a successful raw replay whose every target
certificate is accepted gives, for the document decoded from that very input,
the frozen conclusion (every base-admissible structure is conflict-free) when
the document has neither flags nor definitions, and otherwise that no target
conflict holds in any structure admissible over Python's base environment that
satisfies Python's base Background (flags, definitions, literals). -/
theorem replayConflict_source (j : Json) (r : ConflictReplay) (h : replayConflict j = .ok r) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok r.src := by
  unfold replayConflict at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  rw [he]; exact hd

theorem conflictFree_plain (r : ConflictReplay) (hv : r.conflictFree = true) (hp : r.plain = true) :
    VE.Norms.conflictFreeCheck r.src.D r.certs = true := by
  simp only [ConflictReplay.conflictFree, hp, ↓reduceIte] at hv
  exact hv

theorem conflictFree_flagged (r : ConflictReplay) (hv : r.conflictFree = true) (hp : r.plain = false) :
    conflictFreeCheck r.src r.certs = true := by
  simp only [ConflictReplay.conflictFree, hp, Bool.false_eq_true, ↓reduceIte] at hv
  exact hv

theorem norms_flagged_conflict_sound (j : Json) (r : ConflictReplay) (h : replayConflict j = .ok r)
    (hv : r.conflictFree = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok r.src ∧
    (r.plain = true → ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → ConflictFree r.src.D B) ∧
    (r.plain = false → ∀ S : VE.Structure.{u}, S.Admissible (baseEnv r.src.D) →
      Sat S (baseBackground r.src) → BaseConflictFree r.src S) :=
  ⟨replayConflict_source j r h,
    fun hp B hB => VE.Norms.conflictFreeCheck_sound r.src.D r.src.wf _ (conflictFree_plain r hv hp) B hB,
    fun hp S hS hB => conflictFreeCheck_sound r.src _ (conflictFree_flagged r hv hp) S hS hB⟩

/-- The first target without an accepted certificate, as Python reports it. -/
def firstFailure (r : ConflictReplay) : Option String :=
  ((r.targets.zip (r.certs.zip r.outer)).find? (fun (t, c, _) => match c with
    | some c => !r.accepts t c
    | none => true)).map (fun (t, _, o) =>
      if o then s!"invalid certificate for {t.1}" else s!"missing certificate for {t.1}")

/-! ## Witness packages with flags -/

/-- A decoded witness whose base model also satisfies every flag. -/
structure Witness (src : Wire.Source) extends Replay.WitnessData src where
  flags : VE.Route.Flags.fastFlags M src.ne.rv.flags = true

/-- `Replay.witnessFrom` with the flag check between the structural checks and
the literals (Python `validate_background`: flags, definitions, literals). -/
def witnessFrom (src : Wire.Source) (w : Json) : Except String (Witness src) := do
  unless src.D.T.definitions.isEmpty do
    throw "UnsupportedProfile: norms conflict witnesses with definitions are not implemented"
  let v := Replay.baseModelVocabulary src.ne src.D
  let data ← VE.Bridge.decodeModelData v (← w.getObjVal? "model")
  let M := data.toModel
  let name ← VE.Bridge.stringField w "target"
  let ids ← VE.Bridge.strings (← w.getObjVal? "tuple")
  if hv : data.valid v = true then
    if hf : VE.Route.Flags.fastFlags M src.ne.rv.flags = true then
      if hb : backgroundValid src.D M = true then
        match hfind : (targets src.D).find? (·.1 == name) with
        | none => throw s!"InvalidInput: unknown conflict target {name}"
        | some t =>
          let tuple := t.2.1.zip ids
          if ht : ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple then
            pure ⟨⟨M, Replay.baseModel_valid src.ne src.D src.env M (VE.Bridge.modelData_valid data v hv),
              hb, t, List.mem_of_find?_eq_some hfind, tuple,
              (VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at ht; exact ht.2)⟩, hf⟩
          else throw "InvalidInput: witness tuple has the wrong length or sort"
      else throw (VE.Route.Wire.invalidModel "literals")
    else throw (VE.Route.Wire.invalidModel "flags")
  else throw "model is not semantically admissible"

def replayWitness (j : Json) : Except String ((src : Wire.Source) × Witness src) := do
  let environment ← j.getObjVal? "environment"
  let src ← Wire.decodeSource environment (j.getObjValD "norms") (flags := true)
  let wd ← witnessFrom src (← j.getObjVal? "witness")
  pure ⟨src, wd⟩

/-- `norms_flagged_witness_sound`: a successful raw witness replay whose
regenerated target formula is true at the typed tuple refutes, for the document
decoded from that very input, conflict-freedom over the base-admissible
structures that satisfy the flag premises (the witness model is one). -/
theorem norms_flagged_witness_sound (j : Json) (src : Wire.Source) (w : Witness src)
    (h : replayWitness j = .ok ⟨src, w⟩) (hw : w.conflict = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok src ∧
    BaseAdmissible src.D w.M.asStructure ∧ Sat w.M.asStructure (flagPremises src) ∧
    ¬ ConflictFree src.D w.M.asStructure ∧
      ¬ (∀ B : VE.Structure.{0}, BaseAdmissible src.D B → Sat B (flagPremises src) → ConflictFree src.D B) := by
  unfold replayWitness at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src', hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨wd, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  have hB : BaseAdmissible src.D w.M.asStructure :=
    ⟨w.valid, fun a ha => (VE.eval_iff_denote w.M [] a).mp (List.all_eq_true.mp w.background a ha)⟩
  have hF : Sat w.M.asStructure (flagPremises src) :=
    (VE.Data.Background.generate_sat_iff _ _).mpr ((VE.Route.Flags.fastFlags_iff _ _).mp w.flags)
  obtain ⟨hn, _, _⟩ := Replay.target_refutes src.D src.wf w.target w.mem w.M.asStructure hB
    w.tuple w.typed ((VE.eval_iff_denote w.M _ _).mp hw)
  exact ⟨by rw [he]; exact hd, hB, hF, hn, fun hall => hn (hall _ hB hF)⟩

end VE.Norms.Flagged
