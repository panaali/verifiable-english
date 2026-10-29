import VE.Norms.Wire
import VE.Norms.Layer

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

theorem targetsIn_eq (D : Doc) : targetsIn D (layersOf D) = targets D := by
  simp only [targetsIn, targets, layersOf_syms, conflictIn_eq, pairConflictIn_eq]
  all_goals rfl

/-- `targets` with the layers computed once (`VE.Norms.LayersOnce`, lean-first batch 7 review B1). -/
def targetsOnce (D : Doc) : List (String × List String × VE.Formula) := targetsIn D (layersOf D)

/-- Compiled code after this point, here and in every importer, builds the targets with `targetsOnce`. -/
@[csimp] theorem targets_eq_once : @targets = @targetsOnce :=
  funext fun D => (targetsIn_eq D).symm

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
  let envId ← VE.Route.Wire.environmentId profiles (← Wire.canonicalEnvironmentJson environment)
  VE.CertificateWire.digest s!"ve-norms-{VE.Route.Wire.identityVersion profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", norms)])

/-- Whether a target's package carries the outer source binding. -/
def outerBound (profiles : List String) (environment norms packages : Json) (target : String) : Bool :=
  let package := packages.getObjValD target
  match Wire.canonicalEnvironmentJson environment, documentHash profiles environment norms with
  | .ok canonical, .ok docHash =>
    let envId := (VE.Route.Wire.environmentId profiles canonical).toOption.getD ""
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
  let some canonical := (Wire.canonicalEnvironmentJson environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId profiles canonical).toOption | none
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
  src : Wire.Source
  certs : List (Option VE.Tableau.Certificate)
  outer : List Bool

def ConflictReplay.conflictFree (r : ConflictReplay) : Bool := conflictFreeCheck r.src.D r.certs

/-- Raw replay: decode and validate the source, then decode and bind every
target's package. -/
def replayConflict (j : Json) : Except String ConflictReplay := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  let src ← Wire.decodeSource environment norms
  let packages := j.getObjValD "packages"
  pure ⟨src, (targets src.D).map (decodePackage src.D src.ne.profiles environment norms packages),
    (targets src.D).map (fun t => outerBound src.ne.profiles environment norms packages t.1)⟩

/-- `norms_wire_conflict_sound` (CONFLICT-FREE half): a successful raw replay
whose every target certificate is accepted proves, for the document decoded
from that very input, that every base-admissible structure is conflict-free. -/
theorem norms_wire_conflict_sound (j : Json) (res : ConflictReplay) (h : replayConflict j = .ok res)
    (hv : res.conflictFree = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok res.src ∧
      ∀ B : VE.Structure.{u}, BaseAdmissible res.src.D B → ConflictFree res.src.D B := by
  unfold replayConflict at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  refine ⟨by rw [he]; exact hd, fun B hB => conflictFreeCheck_sound src.D src.wf _ hv B hB⟩

/-- With the document-wide iff: every base-admissible structure then has
exactly one full expansion. -/
theorem norms_wire_conflict_free_expands (j : Json) (res : ConflictReplay)
    (h : replayConflict j = .ok res) (hv : res.conflictFree = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissible res.src.D B → VE.Route.Unique (DocumentExpansion res.src.D B) :=
  (conflictFree_expands_all res.src.D res.src.wf).mpr (norms_wire_conflict_sound j res h hv).2

/-- The first target without an accepted certificate, as Python reports it. -/
def firstFailure (r : ConflictReplay) : Option String :=
  (((targets r.src.D).zip (r.certs.zip r.outer)).find? (fun (t, c, _) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt r.src.D 0) (backgroundBase r.src.D) (targetConclusion t) c
    | none => true)).map (fun (t, _, o) =>
      if o then s!"invalid certificate for {t.1}" else s!"missing certificate for {t.1}")

/-! ## Witness packages (CONFLICT) -/

/-- A valid finite base witness of any target refutes base conflict-freedom
there, unique expansion there and the document property. -/
theorem target_refutes (D : Doc) (h : WellFormed D = true) (t : String × List String × VE.Formula)
    (ht : t ∈ targets D) (B : VE.Structure.{u}) (hB : BaseAdmissible D B) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B t.2.1 vs) (hw : t.2.2.denote B (tupleVal vs)) :
    ¬ ConflictFree D B ∧ ¬ VE.Route.Unique (DocumentExpansion D B) ∧
      ¬ (∀ B' : VE.Structure.{u}, BaseAdmissible D B' → ConflictFree D B') := by
  have hn : ¬ ConflictFree D B := by
    intro hcf
    rcases List.mem_append.mp ht with ht | ht
    · obtain ⟨q, _, hq⟩ := List.mem_filterMap.mp ht
      cases q with
      | reg r =>
        cases hq
        exact hcf.1 r (mem_syms_reg ‹_›) vs hvs hw
      | defn _ => cases hq
    · obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ht
      exact hcf.2 pr hpr vs hvs hw
  exact ⟨hn, fun hu => hn ((conflictFree_expands_document D h B hB).mp hu), fun hall => hn (hall B hB)⟩

theorem lookup_filter_not {α : Type} (ns : List String) (k : String) :
    ∀ l : List (String × α), VE.Bridge.lookup (l.filter (fun x => !ns.contains x.1)) k =
      if k ∈ ns then none else VE.Bridge.lookup l k
  | [] => by by_cases hk : k ∈ ns <;> simp [VE.Bridge.lookup, hk]
  | x :: l => by
    have ih := lookup_filter_not ns k l
    by_cases hx : x.1 ∈ ns
    · have : (!ns.contains x.1) = false := by simp [hx]
      rw [List.filter_cons, this, if_neg (by simp), ih]
      by_cases hk : k ∈ ns
      · simp [hk]
      · have hne : (x.1 == k) = false := by
          simp only [beq_eq_false_iff_ne]; exact fun e => hk (e ▸ hx)
        simp [hk, VE.Bridge.lookup, hne]
    · have : (!ns.contains x.1) = true := by simp [hx]
      rw [List.filter_cons, this, if_pos rfl]
      by_cases hk : k ∈ ns
      · have hne : (x.1 == k) = false := by
          simp only [beq_eq_false_iff_ne]; exact fun e => hx (e ▸ hk)
        simp only [VE.Bridge.lookup, List.find?_cons, hne] at ih ⊢
        simpa [hk] using ih
      · by_cases he : (x.1 == k) = true
        · simp [hk, VE.Bridge.lookup, he]
        · have he' : (x.1 == k) = false := by simpa using he
          simp only [VE.Bridge.lookup, List.find?_cons, he'] at ih ⊢
          simpa [hk] using ih

/-- The base model vocabulary: the source vocabulary without layer symbols,
with `$string` listed as a domain when literals are declared. -/
def baseModelVocabulary (ne : Wire.NormsEnvironment) (D : Doc) : VE.Bridge.Vocabulary :=
  { ne.rv.modelVocabulary with
    predicates := ne.rv.vocabulary.predicates.filter (fun p => !(layerNames D.T).contains p.1) }

theorem baseModel_valid (ne : Wire.NormsEnvironment) (D : Doc) (hE : D.E = ne.rv.environment)
    (M : VE.FiniteModel VE.Bridge.Entity) (h : M.Valid (baseModelVocabulary ne D).environment) :
    M.Valid (envAt D 0) := by
  refine ⟨fun c s hc => h.1 c s (by change D.E.constants c = some s at hc; rw [hE] at hc; exact hc),
    fun p vs hp => ?_⟩
  obtain ⟨ss, hss, ht⟩ := h.2 p vs hp
  refine ⟨ss, ?_, ht⟩
  change VE.Bridge.lookup (ne.rv.vocabulary.predicates.filter _) p = some ss at hss
  rw [lookup_filter_not] at hss
  simp only [envAt, hide, List.drop_zero, hE]
  exact hss

/-- A decoded witness over a decoded source: the base model, the target and
the entity tuple, with their validity facts. -/
structure WitnessData (src : Wire.Source) where
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt src.D 0)
  background : backgroundValid src.D M = true
  target : String × List String × VE.Formula
  mem : target ∈ targets src.D
  tuple : List VE.Bridge.Entity
  typed : VE.TupleTyped M.asStructure target.2.1 tuple

def WitnessData.conflict {src : Wire.Source} (w : WitnessData src) : Bool :=
  w.target.2.2.eval w.M (tupleVal w.tuple)

/-- Decode the base model (validated structurally and against `Background_base`:
a violation is `InvalidModel(literals)`, never a verdict), the target and the
typed tuple. -/
def witnessFrom (src : Wire.Source) (w : Json) : Except String (WitnessData src) := do
  let v := baseModelVocabulary src.ne src.D
  let data ← VE.Bridge.decodeModelData v (← w.getObjVal? "model")
  let M := data.toModel
  let name ← VE.Bridge.stringField w "target"
  let ids ← VE.Bridge.strings (← w.getObjVal? "tuple")
  if hv : data.valid v = true then
    if hb : backgroundValid src.D M = true then
      match hf : (targets src.D).find? (·.1 == name) with
      | none => throw s!"InvalidInput: unknown conflict target {name}"
      | some t =>
        let tuple := t.2.1.zip ids
        if ht : ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple then
          pure ⟨M, baseModel_valid src.ne src.D src.env M (VE.Bridge.modelData_valid data v hv), hb, t,
            List.mem_of_find?_eq_some hf, tuple,
            (VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at ht; exact ht.2)⟩
        else throw "InvalidInput: witness tuple has the wrong length or sort"
    else throw (VE.Route.Wire.invalidModel "literals")
  else throw "model is not semantically admissible"

def replayWitness (j : Json) : Except String ((src : Wire.Source) × WitnessData src) := do
  let environment ← j.getObjVal? "environment"
  let src ← Wire.decodeSource environment (j.getObjValD "norms")
  let wd ← witnessFrom src (← j.getObjVal? "witness")
  pure ⟨src, wd⟩

/-- `norms_wire_conflict_sound` (CONFLICT half): a successful raw witness replay
whose regenerated target formula evaluates to true at the typed tuple refutes,
for the document decoded from that very input, base conflict-freedom of the
model, its unique expansion and the document property. -/
theorem norms_wire_conflict_witness_sound (j : Json) (src : Wire.Source) (w : WitnessData src)
    (h : replayWitness j = .ok ⟨src, w⟩) (hw : w.conflict = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok src ∧
    ¬ ConflictFree src.D w.M.asStructure ∧ ¬ VE.Route.Unique (DocumentExpansion src.D w.M.asStructure) ∧
      ¬ (∀ B : VE.Structure.{0}, BaseAdmissible src.D B → ConflictFree src.D B) := by
  unfold replayWitness at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src', hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨wd, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, target_refutes src.D src.wf w.target w.mem w.M.asStructure
    ⟨w.valid, fun a ha => (VE.eval_iff_denote w.M [] a).mp (List.all_eq_true.mp w.background a ha)⟩
    w.tuple w.typed ((VE.eval_iff_denote w.M _ _).mp hw)⟩

/-! ## Entailment certificates on the norms route -/

/-- A replayed entailment case: the decoded source, the document's own premises
and conclusion (typed over the complete environment) and the bound certificate. -/
structure EntailmentReplay where
  src : Wire.Source
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate

/-- The unchanged checker on the regenerated `Background ++ layer premises ++ Γ`. -/
def EntailmentReplay.valid (r : EntailmentReplay) : Bool :=
  VE.Tableau.checkCertificate (envAt r.src.D (size r.src.D))
    (background r.src.D ++ elaborate r.src.D.T ++ r.premises) r.conclusion r.cert

/-- Decode the source, the case's premises and conclusion and the certificate;
the certificate must bind the complete source environment, every regenerated
Background and layer premise followed by the case's premises, and the
conclusion (P0 meaning ids). A supplied elaboration is never read. -/
def replayEntailment (j : Json) : Except String EntailmentReplay := do
  let environment ← j.getObjVal? "environment"
  let src ← Wire.decodeSource environment (j.getObjValD "norms")
  let E := envAt src.D (size src.D)
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk src.ne.profiles (← Wire.canonicalEnvironmentJson environment)
    ((background src.D ++ elaborate src.D.T).map VE.Route.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure ⟨src, ps, c, cert⟩

/-- `norms_wire_acceptance` for entailment certificates (the certificate half of
11.4): from a successful raw replay with an accepted certificate, for the
document decoded from that very input, (1) the conclusion holds in every
admissible structure satisfying the direct semantics, the definitions, the
profile, `Background_base` and the premises; and (2) if the document is
conflict-free (for instance by `norms_wire_conflict_sound`) and the premises
and conclusion are base formulas, the conclusion holds in every base-admissible
structure satisfying the premises. -/
theorem norms_wire_acceptance (j : Json) (r : EntailmentReplay) (h : replayEntailment j = .ok r)
    (hv : r.valid = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
    (∀ S : VE.Structure.{u}, S.Admissible (envAt r.src.D (size r.src.D)) → holdsCatala r.src.D.T S →
      definitionsHold r.src.D S → profileHold r.src.D S → Sat S (backgroundBase r.src.D) →
      Sat S r.premises → r.conclusion.denote S []) ∧
    ((∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → ConflictFree r.src.D B) →
      (∀ a ∈ r.premises, a.WellFormed (envAt r.src.D 0) []) → r.conclusion.WellFormed (envAt r.src.D 0) [] →
      ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B r.premises → r.conclusion.denote B []) := by
  have hdec : Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src := by
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
  refine ⟨hdec, fun S hS hcat hdef hprof hbase hΓ => ?_, fun hc hΓ hφ => ?_⟩
  · exact norms_route_intended r.src.D r.src.wf r.premises r.conclusion r.cert hv S hS hcat hdef hprof hbase hΓ
  · exact (norms_route_acceptance r.src.D r.src.wf hc r.premises r.conclusion r.cert hv).2 hΓ hφ

end Replay
end VE.Norms
