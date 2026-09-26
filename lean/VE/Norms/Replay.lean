import VE.Norms.Wire

/-! Conflict-package replay on the norms route (docs/spec/norms.md 5.2 and
11.4 steps 3-5, the CONFLICT-FREE half).

A package for one conflict target is Python `ve/norms.py`'s
`{"environment_id", "document_hash", "target", "certificate"}`: the outer
binding names the complete source environment, the norm document hash and the
target; the inner certificate is an ordinary P0 FOL certificate bound to the
regenerated base environment (regulated predicates and the `norms@0` profile
removed), `Background_base` and the closed negated conflict formula
`∀x̄. ¬conflict`. Both bindings are recomputed from the raw source here; the
formulas are regenerated, never read from the wire.

`conflictFreeCheck` runs the unchanged tableau checker on the regenerated
`E_base`, `Background_base` and conclusion; `norms_wire_conflict_sound` proves
from a successful raw replay that every base-admissible structure is
conflict-free, hence (by `conflictFree_expands_all`) has a unique full
expansion. Hash equality is identity binding, not a proof step. -/
namespace VE.Norms
open Lean
universe u

/-- The conflict targets in Python's order: each regulated predicate in DAG
order (`p`), then each declared pair (`r->m`), with argument sorts. -/
def targets (D : Doc) : List (String × List String × VE.Formula) :=
  (syms D.T).filterMap (fun | .reg r => some (r.name, r.sorts, conflict D r) | .defn _ => none) ++
    (pairs D.T).map (fun pr => (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflict D pr))

/-- `∀x̄. ¬conflict`, the certified conclusion of a target. -/
def targetConclusion (t : String × List String × VE.Formula) : VE.Formula :=
  bindAll t.2.1 (.not t.2.2)

/-- Every target has an accepted certificate for `Background_base ⊢ ∀x̄. ¬conflict`
over the regenerated `E_base`. -/
def conflictFreeCheck (D : Doc) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets D).length == certs.length &&
    ((targets D).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt D 0) (backgroundBase D) (targetConclusion t) c
      | none => false)

theorem conflictFreeCheck_target {D : Doc} {certs : List (Option VE.Tableau.Certificate)}
    (hc : conflictFreeCheck D certs = true) {t : String × List String × VE.Formula}
    (ht : t ∈ targets D) :
    ∃ c, VE.Tableau.checkCertificate (envAt D 0) (backgroundBase D) (targetConclusion t) c = true := by
  simp only [conflictFreeCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < (targets D).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : (t, certs[i]) ∈ (targets D).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  have := hall _ hmem
  cases hci : certs[i] with
  | none => rw [hci] at this; cases this
  | some c => rw [hci] at this; exact ⟨c, this⟩

/-- A certified target excludes its conflict formula on every typed tuple of
every base-admissible structure. -/
theorem certified_target {D : Doc} (t : String × List String × VE.Formula)
    (c : VE.Tableau.Certificate)
    (hc : VE.Tableau.checkCertificate (envAt D 0) (backgroundBase D) (targetConclusion t) c = true)
    (B : VE.Structure.{u}) (hB : BaseAdmissible D B) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B t.2.1 vs) : ¬ t.2.2.denote B (tupleVal vs) := by
  have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c hc B hB.1 hB.2
  exact (bindAll_denote_nil B _ _).mp he vs hvs

/-- Certificates for every target give base conflict-freedom. -/
theorem conflictFreeCheck_sound (D : Doc) (h : WellFormed D = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : conflictFreeCheck D certs = true)
    (B : VE.Structure.{u}) (hB : BaseAdmissible D B) : ConflictFree D B := by
  have hv := valid_of_wellFormed D h
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · have ht : (r.name, r.sorts, conflict D r) ∈ targets D :=
      List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)
    obtain ⟨c, hcc⟩ := conflictFreeCheck_target hc ht
    exact certified_target _ c hcc B hB vs hvs
  · have ht : (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflict D pr) ∈ targets D :=
      List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)
    obtain ⟨c, hcc⟩ := conflictFreeCheck_target hc ht
    exact certified_target _ c hcc B hB vs hvs

namespace Replay
open VE.Bridge (fields stringField strings)

/-- The regenerated base environment: regulated predicates and `norms@0` removed
(Python `NormDocument.base_environment`). -/
def baseEnvironmentJson (environment : Json) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  let kept := preds.filter (fun (_, e) => !(e.getObjVal? "regulated").toBool)
  let profiles ← strings (← environment.getObjVal? "profiles")
  pure ((environment.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" (Json.mkObj kept))).setObjVal!
    "profiles" (toJson (profiles.filter (· != "norms@0"))))

/-- The norm document hash (11.2): the canonical array of norm objects under the
source environment id. -/
def documentHash (profiles : List String) (environment norms : Json) : Except String String := do
  let envId ← VE.Route.Wire.environmentId profiles environment
  VE.CertificateWire.digest s!"ve-norms-{VE.Route.Wire.identityVersion profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", norms)])

/-- Whether a target's package carries the outer source binding. -/
def outerBound (profiles : List String) (environment norms packages : Json) (target : String) : Bool :=
  let package := packages.getObjValD target
  match VE.Route.Wire.environmentId profiles environment, documentHash profiles environment norms with
  | .ok envId, .ok docHash =>
    package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash && package.getObjValD "target" == .str target
  | _, _ => false

/-- One target's package: `none` unless the outer binding matches the source,
the certificate decodes and its inner binding matches the regenerated base
environment, `Background_base` and conclusion. -/
def decodePackage (D : Doc) (profiles : List String) (environment norms packages : Json)
    (t : String × List String × VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let some baseEnv := (baseEnvironmentJson environment).toOption | none
  let some baseProfiles := (strings (baseEnv.getObjValD "profiles")).toOption | none
  let some envId := (VE.Route.Wire.environmentId profiles environment).toOption | none
  let some docHash := (documentHash profiles environment norms).toOption | none
  let package := packages.getObjValD t.1
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str t.1 do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  let bound := VE.Route.Wire.bindingOk baseProfiles baseEnv
    ((backgroundBase D).map VE.Route.Wire.encodeFormula) (VE.Route.Wire.encodeFormula (targetConclusion t))
    c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
  match bound with
  | .ok () => some c
  | .error _ => none

/-- A replayed conflict case: the decoded well-formed source and each target's
bound certificate, in target order. -/
structure ConflictReplay where
  ne : Wire.NormsEnvironment
  D : {D : Doc // WellFormed D = true}
  certs : List (Option VE.Tableau.Certificate)
  outer : List Bool

def ConflictReplay.conflictFree (r : ConflictReplay) : Bool := conflictFreeCheck r.D.1 r.certs

/-- Raw replay: decode and validate the source, then decode and bind every
target's package. -/
def replayConflict (j : Json) : Except String ConflictReplay := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  let (ne, D) ← Wire.decodeSource environment norms
  let packages := j.getObjValD "packages"
  pure ⟨ne, D, (targets D.1).map (decodePackage D.1 ne.profiles environment norms packages),
    (targets D.1).map (fun t => outerBound ne.profiles environment norms packages t.1)⟩

/-- `norms_wire_conflict_sound` (CONFLICT-FREE half): a successful raw replay
whose every target certificate is accepted proves, for the document decoded
from that very input, that every base-admissible structure is conflict-free. -/
theorem norms_wire_conflict_sound (j : Json) (res : ConflictReplay) (h : replayConflict j = .ok res)
    (hv : res.conflictFree = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok (res.ne, res.D) ∧
      ∀ B : VE.Structure.{u}, BaseAdmissible res.D.1 B → ConflictFree res.D.1 B := by
  unfold replayConflict at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨⟨ne, D⟩, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  refine ⟨by rw [he]; exact hd, fun B hB => conflictFreeCheck_sound D.1 D.2 _ hv B hB⟩

/-- With the document-wide iff: every base-admissible structure then has
exactly one full expansion. -/
theorem norms_wire_conflict_free_expands (j : Json) (res : ConflictReplay)
    (h : replayConflict j = .ok res) (hv : res.conflictFree = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissible res.D.1 B → VE.Route.Unique (DocumentExpansion res.D.1 B) :=
  (conflictFree_expands_all res.D.1 res.D.2).mpr (norms_wire_conflict_sound j res h hv).2

/-- The first target without an accepted certificate, as Python reports it. -/
def firstFailure (r : ConflictReplay) : Option String :=
  (((targets r.D.1).zip (r.certs.zip r.outer)).find? (fun (t, c, _) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt r.D.1 0) (backgroundBase r.D.1) (targetConclusion t) c
    | none => true)).map (fun (t, _, o) =>
      if o then s!"invalid certificate for {t.1}" else s!"missing certificate for {t.1}")

end Replay
end VE.Norms
