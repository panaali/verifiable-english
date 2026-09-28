import VE.Alternatives.Wire

/-! Package replay on the alternatives route (docs/spec/alternatives.md 3.5, 7.2, 7.3):
conflict packages over `Background_baseAlt`, the followability package over
`Background_baseAlt ++ Γ_base`, dilemma witnesses with their signed rows, and
entailment certificates over `backgroundAlt ++ layer premises ++ premises`, each
bound to the raw source and regenerated here (norms.md 11.4 shape), with the wire
theorems.

Bindings (3.5). The outer binding of a package is `(environment_id, document_hash,
target)`: `environment_id` over the complete canonical environment (block
included), `document_hash` over the norm objects and the base units under it
(`ve-alternatives-…` domain). The inner certificate binds the regenerated base
environment (block, `alternatives@0`, `norms@0` and regulated predicates removed),
the regenerated premises and the conclusion by P0 meaning ids. A case carries
`norms` and `units` (the document's active base units). -/
namespace VE.Alternatives.Replay
open Lean
open VE.Norms
open VE.Bridge (fields stringField strings exactFields)
open Wire (AltSource decodeAltSource)
universe u

/-! ## Bindings -/

def baseEnvironmentJson (environment : Json) (ps : List String) : Except String Json := do
  VE.Norms.Replay.baseEnvironmentJson (← Wire.normsView environment ps)

def environmentId (ps : List String) (environment : Json) : Except String String := do
  VE.Route.Wire.environmentId ps (← VE.Norms.Wire.canonicalEnvironmentJson environment)

/-- The alternatives document hash (3.5): the norm objects and the base units under the
source environment id. -/
def documentHash (ps : List String) (environment norms units : Json) : Except String String := do
  let envId ← environmentId ps environment
  VE.CertificateWire.digest s!"ve-alternatives-{VE.Route.Wire.identityVersion ps}\n"
    (Json.mkObj [("environment_id", .str envId), ("norms", norms), ("units", units)])

/-- A package bound to the source, or `none`: the outer binding, the certificate, and its
inner binding to the regenerated base environment, premises and conclusion. -/
def decodePackage (ps : List String) (environment norms units package : Json) (target : String)
    (premises : List VE.Formula) (conclusion : VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let some baseEnv := (baseEnvironmentJson environment ps).toOption | none
  let some baseProfiles := (strings (baseEnv.getObjValD "profiles")).toOption | none
  let some envId := (environmentId ps environment).toOption | none
  let some docHash := (documentHash ps environment norms units).toOption | none
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str target do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv (premises.map VE.Route.Wire.encodeFormula)
      (VE.Route.Wire.encodeFormula conclusion) c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

/-- Every conflict target's package (target order). -/
def conflictCerts (src : AltSource) (environment norms units packages : Json) :
    List (Option VE.Tableau.Certificate) :=
  (targets (inlineTree src.A)).map fun t =>
    decodePackage src.profiles environment norms units (packages.getObjValD t.1) t.1
      (backgroundBaseAlt src.A) (targetConclusion t)

def sourceOf (j : Json) : Except String AltSource := do
  let environment ← j.getObjVal? "environment"
  decodeAltSource environment (j.getObjValD "norms") (j.getObjValD "units")

theorem sourceOf_ok {j : Json} {src : AltSource} (h : sourceOf j = .ok src) :
    decodeAltSource (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok src := by
  unfold sourceOf at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  rw [he]; exact h

/-! ## Conflict packages (4.5) -/

structure AltConflictReplay where
  src : AltSource
  certs : List (Option VE.Tableau.Certificate)

def AltConflictReplay.conflictFree (r : AltConflictReplay) : Bool := altConflictFreeCheck r.src.A r.certs

def replayAltConflict (j : Json) : Except String AltConflictReplay := do
  let src ← sourceOf j
  pure ⟨src, conflictCerts src (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units")
    (j.getObjValD "packages")⟩

/-- CONFLICT-FREE from raw JSON: the input decodes to exactly the replayed well-formed source,
and every `BaseAdmissibleAlt` structure is conflict-free. -/
theorem alternatives_wire_conflict_sound (j : Json) (res : AltConflictReplay) (h : replayAltConflict j = .ok res)
    (hv : res.conflictFree = true) :
    decodeAltSource (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok res.src ∧
      WellFormedAlt res.src.A = true ∧ AltConflictFree.{u} res.src.A := by
  unfold replayAltConflict at h
  obtain ⟨src, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  exact ⟨sourceOf_ok hs, src.wf, alt_conflict_free src.A src.wf _ hv⟩

/-- The first target without an accepted certificate. -/
def firstFailure (r : AltConflictReplay) : Option String :=
  (((targets (inlineTree r.src.A)).zip r.certs).find? (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt (inlineTree r.src.A) 0) (backgroundBaseAlt r.src.A)
        (targetConclusion t) c
    | none => true)).map (fun (t, c) => if c.isSome then s!"invalid certificate for {t.1}"
      else s!"missing certificate for {t.1}")

/-! ## The followability package (4.6) -/

structure FollowableReplay where
  src : AltSource
  certs : List (Option VE.Tableau.Certificate)
  cert : Option VE.Tableau.Certificate

def FollowableReplay.conflictFree (r : FollowableReplay) : Bool := altConflictFreeCheck r.src.A r.certs

def FollowableReplay.followable (r : FollowableReplay) : Bool :=
  r.conflictFree && match r.cert with
    | some c => VE.Tableau.checkCertificate (envAt (inlineTree r.src.A) 0) (backgroundBaseAlt r.src.A ++ r.src.A.Γ)
        (allFollowable r.src.A) c
    | none => false

def replayFollowable (j : Json) : Except String FollowableReplay := do
  let src ← sourceOf j
  let environment := j.getObjValD "environment"
  let norms := j.getObjValD "norms"
  let units := j.getObjValD "units"
  pure ⟨src, conflictCerts src environment norms units (j.getObjValD "packages"),
    decodePackage src.profiles environment norms units (j.getObjValD "package") "followable"
      (backgroundBaseAlt src.A ++ src.A.Γ) (allFollowable src.A)⟩

/-- FOLLOWABLE from raw JSON: the source decodes and is well-formed and conflict-free over the
extended bases, and every document expansion of a `BaseAdmissibleAlt` structure satisfying
`Γ_base` has a clear alternative at every chooser with one. -/
theorem alternatives_wire_followable_sound (j : Json) (res : FollowableReplay) (h : replayFollowable j = .ok res)
    (hv : res.followable = true) :
    decodeAltSource (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok res.src ∧
      WellFormedAlt res.src.A = true ∧ AltConflictFree.{u} res.src.A ∧
      ∀ B : VE.Structure.{u}, BaseAdmissibleAlt res.src.A B → Sat B res.src.A.Γ →
        ∀ S, DocumentExpansion (inlineTree res.src.A) B S → FollowableIn res.src.A S := by
  unfold replayFollowable at h
  obtain ⟨src, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [FollowableReplay.followable, FollowableReplay.conflictFree, Bool.and_eq_true] at hv
  obtain ⟨hc, hf⟩ := hv
  have hcf := alt_conflict_free.{u} src.A src.wf _ hc
  refine ⟨sourceOf_ok hs, src.wf, hcf, ?_⟩
  revert hf
  split
  · intro hf
    exact followable_sound src.A src.wf hcf _ hf
  · intro hf; cases hf

/-! ## Scenarios and dilemma witnesses (3.3, 4.6, 4.7) -/

def decodeRows (j : Json) : Except String (List Row) := do
  let xs ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: outcomes must be an array"
  xs.mapM fun x => do
    exactFields x ["action", "harm", "leads_to", "support"]
    let a ← stringField x "action"
    let h ← stringField x "harm"
    let b ← match x.getObjValD "leads_to" with
      | .bool b => pure b
      | _ => throw "InvalidInput: outcome row"
    let s ← stringField x "support"
    pure ⟨a, h, b, s⟩

/-- The `leads_to` table is the set of positive rows (3.3): filled in when the model omits it. -/
def withLeadsTo (leadsTo : String) (model : Json) (rows : List Row) : Json :=
  let rels := model.getObjValD "relations"
  match rels.getObjVal? leadsTo with
  | .ok _ => model
  | .error _ => model.setObjVal! "relations" (rels.setObjVal! leadsTo
      (Json.arr ((rows.filter (·.leadsTo)).map (fun r => toJson [r.action, r.harm])).toArray))

/-- A decoded scenario: the base model (validated structurally by the Bridge), its signed rows
and its raw form. Rows name entities of the action and harm domains, as constants of the model. -/
structure Scenario (src : AltSource) where
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt (inlineTree src.A) 0)
  rows : List Row
  json : Json

def decodeScenario (src : AltSource) (w : Json) : Except String (Scenario src) := do
  let rows ← decodeRows (← w.getObjVal? "outcomes")
  let v := VE.Norms.Replay.baseModelVocabulary src.ne (inlineTree src.A)
  let modelJ := withLeadsTo src.A.alt.leadsTo (← w.getObjVal? "model") rows
  let data ← VE.Bridge.decodeModelData v modelJ
  let ids (s : String) := (VE.Bridge.lookup data.domains s).getD []
  let extra := [src.A.alt.action, src.A.alt.harm].flatMap fun s => (ids s).map (fun x => (x, (s, x)))
  let data' : VE.Bridge.ModelData := { data with constants := data.constants ++ extra }
  if hv : data'.valid v = true then
    pure ⟨data'.toModel, VE.Norms.Replay.baseModel_valid src.ne (inlineTree src.A) src.env _
      (VE.Bridge.modelData_valid data' v hv), rows, modelJ⟩
  else throw "model is not semantically admissible"

def entity (M : VE.FiniteModel VE.Bridge.Entity) (s x : String) : Except String VE.Bridge.Entity :=
  if (M.domains s).contains (s, x) then pure (s, x) else throw s!"InvalidInput: {x} is not in the {s} domain"

/-- A decoded dilemma witness: the conflict packages of the same source, the scenario and the
chooser. -/
structure DilemmaData (src : AltSource) where
  certs : List (Option VE.Tableau.Certificate)
  sc : Scenario src
  r : VE.Bridge.Entity

def DilemmaData.M {src : AltSource} (w : DilemmaData src) : VE.FiniteModel VE.Bridge.Entity := w.sc.M
def DilemmaData.rows {src : AltSource} (w : DilemmaData src) : List Row := w.sc.rows

def DilemmaData.dilemma {src : AltSource} (w : DilemmaData src) : Bool :=
  altConflictFreeCheck src.A w.certs && altModelChecks src.A w.M w.rows &&
    (w.M.domains src.A.alt.chooser).contains w.r && (notFollowableF src.A).eval w.M (tupleVal [w.r])

def replayDilemma (j : Json) : Except String ((src : AltSource) × DilemmaData src) := do
  let src ← sourceOf j
  let w ← j.getObjVal? "witness"
  let sc ← decodeScenario src w
  let r ← entity sc.M src.A.alt.chooser (← stringField w "chooser")
  pure ⟨src, ⟨conflictCerts src (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units")
    (j.getObjValD "packages"), sc, r⟩⟩

/-- DILEMMA from raw JSON: the source decodes, is well-formed and conflict-free, the witness
passes validation with its rows, the chooser is typed, `¬followable°` evaluates true there, and
the document-wide claim is refuted. -/
theorem alternatives_wire_dilemma_sound (j : Json) (src : AltSource) (w : DilemmaData src)
    (h : replayDilemma j = .ok ⟨src, w⟩) (hw : w.dilemma = true) :
    decodeAltSource (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok src ∧
      WellFormedAlt src.A = true ∧ AltConflictFree.{0} src.A ∧
      validateAlternatives src.A w.M w.rows = .ok () ∧ w.M.inDomain src.A.alt.chooser w.r ∧
      (notFollowableF src.A).eval w.M (tupleVal [w.r]) = true ∧
      ¬ (∀ B : VE.Structure.{0}, BaseAdmissibleAlt src.A B → Sat B src.A.Γ → (allFollowable src.A).denote B []) := by
  have hdec : decodeAltSource (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok src := by
    unfold replayDilemma at h
    obtain ⟨src', hs, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    cases h
    exact sourceOf_ok hs
  simp only [DilemmaData.dilemma, Bool.and_eq_true, List.contains_iff_mem] at hw
  obtain ⟨⟨⟨hc, hm⟩, hr⟩, hd⟩ := hw
  have hval : validateAlternatives src.A w.M w.rows = .ok () := validateAlternativesWith_ok.mpr hm
  obtain ⟨valid, hb, hΓ, _, _⟩ := validate_sound src.A w.M w.rows w.sc.valid hval
  exact ⟨hdec, src.wf, alt_conflict_free src.A src.wf _ hc, hval, hr, hd,
    dilemma_witness_sound src.A src.wf w.M valid hb hΓ w.r hr hd⟩

/-! ## Entailment certificates -/

structure AltEntailmentReplay where
  src : AltSource
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate

/-- The unchanged checker on the regenerated `backgroundAlt ++ layer premises ++ premises`. -/
def AltEntailmentReplay.valid (r : AltEntailmentReplay) : Bool :=
  VE.Tableau.checkCertificate (envAt (inlineTree r.src.A) (size (inlineTree r.src.A)))
    (backgroundAlt r.src.A ++ elaborate (inlineTree r.src.A).T ++ r.premises) r.conclusion r.cert

/-- The certificate binds the complete source environment, every regenerated premise of
`backgroundAlt ++ layer premises` followed by the case's premises, and the conclusion. -/
def replayAltEntailment (j : Json) : Except String AltEntailmentReplay := do
  let src ← sourceOf j
  let environment ← j.getObjVal? "environment"
  let D := inlineTree src.A
  let E := envAt D (size D)
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk src.profiles (← VE.Norms.Wire.canonicalEnvironmentJson environment)
    ((backgroundAlt src.A ++ elaborate D.T).map VE.Route.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure ⟨src, ps, c, cert⟩

/-- Entailment certificates from raw JSON: the source decodes; the conclusion holds under the
direct semantics with the slot premises; and, given `AltConflictFree` and base formulas, in every
`BaseAdmissibleAlt` structure satisfying the premises. -/
theorem alternatives_wire_acceptance (j : Json) (r : AltEntailmentReplay) (h : replayAltEntailment j = .ok r)
    (hv : r.valid = true) :
    decodeAltSource (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok r.src ∧
    (∀ S : VE.Structure.{u}, S.Admissible (envAt (inlineTree r.src.A) (size (inlineTree r.src.A))) →
       VE.Norms.holdsCatala (inlineTree r.src.A).T S → VE.Norms.definitionsHold (inlineTree r.src.A) S →
       VE.Norms.profileHold (inlineTree r.src.A) S → Sat S (backgroundBase (inlineTree r.src.A)) →
       Sat S (altPremises r.src.A) → Sat S r.premises → r.conclusion.denote S []) ∧
    (AltConflictFree.{u} r.src.A →
       (∀ a ∈ r.premises, a.WellFormed (envAt (inlineTree r.src.A) 0) []) →
       r.conclusion.WellFormed (envAt (inlineTree r.src.A) 0) [] →
       ∀ B : VE.Structure.{u}, BaseAdmissibleAlt r.src.A B → Sat B r.premises → r.conclusion.denote B []) := by
  have hdec : decodeAltSource (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok r.src := by
    unfold replayAltEntailment at h
    obtain ⟨src, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
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
    exact sourceOf_ok hs
  refine ⟨hdec, fun S hS hcat hdef hprof hbase hslot hΓ => ?_, fun hc hΓ hφ => ?_⟩
  · exact alt_route_intended r.src.A r.src.wf r.premises r.conclusion r.cert hv S hS hcat hdef hprof hbase hslot hΓ
  · exact (alt_route_acceptance r.src.A r.src.wf hc r.premises r.conclusion r.cert hv).2 hΓ hφ

end VE.Alternatives.Replay
