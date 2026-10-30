import VE.Defaults.Premises
import VE.Readings.SoftFacts
import VE.NormDefaults.LayeredAdmission

/-! The `defaults-*` kinds on a layered source (docs/spec/defeasible.md 7.2; plan DF-1a, 2.2 and 2.6).

Every case decodes its source with the layered route's own `decodeLayered` (`viewOf`), then checks that the document
is well formed (diagnostic 7) and that a default answer applies to it: no `weighing@0` (1), no decision in the other
packs' premises `R` (2), distinct generated labels (6), generated premises within soft's limits (4). Then:

* `defaults-elaborate`: `Dflt_T` and the colliding pairs with their coherence premises (`elaborateRows`).
* `defaults-coherence`: one optional certificate per colliding pair (diagnostic 5) and an optional collision; COHERENT,
  COLLISION or UNKNOWN, with each pair's status (`defaults_coherence_sound`), and with a collision the tuple and the
  deciders DE7 shows.
* `defaults-certificate`: the question's premises state facts only (diagnostic 3); FOLLOWS needs a certificate bound
  to `premisesX U (defaultX D X) Γ`, the gate's certificates and a checked model of `defaultX` and the premises
  (`defaults_certificate_sound`); otherwise UNKNOWN with its reason, a checked collision first.
* `defaults-model`: a countermodel of `defaultX` (`defaults_model_sound`) with the exceptions the text's own conditions
  force there (`forcedAt_sound`).

Searching for certificates, models and collisions is not done here; every piece the request carries is checked. -/
namespace VE.Defaults.Wire
open Lean
open VE.Defaults
open VE.Norms (envAt size)
open VE.SoftNorms (SoftDoc SoftNode soften WellFormedSoft)
open VE.NormDefaults (UDoc fill EntailsX)
open VE.NormDefaults.Wire (LayeredU softLabelledU premisesX)
open VE.Order.ProfileGate (bind_ok)
universe u

structure DefaultsView where
  L : LayeredU
  R : List VE.Formula
  hX : L.X = (softLabelledU L.U L.D).map (·.2) ++ R
  hU : L.U.D = soften L.D
  hD : WellFormedSoft L.D = true
  hXw : ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) []
  hR : R.all (decisionFree L.D) = true
  hl : VE.Compose.Labelled.wellLabelled (dfltLabelled L.D) = true

theorem decodeRightsU_soften (environment document : Json) (L : LayeredU)
    (h : VE.NormDefaults.Wire.decodeRightsU environment document = .ok L) : L.U.D = soften L.D := by
  unfold VE.NormDefaults.Wire.decodeRightsU at h
  repeat (obtain ⟨_, _, h⟩ := bind_ok h)
  split at h
  · split at h
    · repeat (obtain ⟨_, _, h⟩ := bind_ok h)
      cases h; rfl
    · cases h
  · cases h

/-- Both branches of `decodeLayered` build `U := ⟨soften D, …⟩` (`decodeSoftU`, `decodeRightsU`). -/
theorem decodeLayered_soften (j : Json) (L : LayeredU) (h : VE.NormDefaults.Wire.decodeLayered j = .ok L) :
    L.U.D = soften L.D := by
  unfold VE.NormDefaults.Wire.decodeLayered at h
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h
  · exact decodeRightsU_soften _ _ L h
  · obtain ⟨_, _, _, _, hD, hU, _⟩ := VE.NormDefaults.Wire.decodeSoftU_source _ _ L h
    rw [hU, hD]
  · cases h

/-- What diagnostics 1, 2, 6 and 4 give on a decoded document: `R` (X after the soft pack) with `hX`, `hR`, `hl`. -/
structure ViewRest (L : LayeredU) where
  R : List VE.Formula
  hX : L.X = (softLabelledU L.U L.D).map (·.2) ++ R
  hR : R.all (decisionFree L.D) = true
  hl : VE.Compose.Labelled.wellLabelled (dfltLabelled L.D) = true

def notWellFormedText : String := "InvalidInput: answers that assume no exception need a well-formed document"

def weighingText : String :=
  "UnsupportedProfile: answers that assume no exception are not available with weighing@0 yet"

/-- Diagnostics 1, 2, 6 and 4 of section 5, in that order. `R` is the packs' labelled premises after the soft pack's;
    a document whose `X` does not start with the soft pack's premises is not well formed (never on a decoded one). -/
def viewRest (j : Json) (L : LayeredU) : Except String (ViewRest L) :=
  if (VE.NormDefaults.Wire.profilesOf (j.getObjValD "environment")).contains "weighing@0" then .error weighingText
  else
    let rest := (VE.NormDefaults.Packs.labelledX L.packs).drop (softLabelledU L.U L.D).length
    if hX : L.X = (softLabelledU L.U L.D).map (·.2) ++ rest.map (·.2) then
      if hR : (rest.map (·.2)).all (decisionFree L.D) = true then
        if hl : VE.Compose.Labelled.wellLabelled (dfltLabelled L.D) = true then
          match limitDiag L.D with
          | some e => .error e
          | none => .ok ⟨rest.map (·.2), hX, hR, hl⟩
        else .error ("InvalidInput: two generated default premises share the label " ++
          ((dfltLabels L.D).find? (fun l => (dfltLabels L.D).count l > 1)).getD "")
      else .error ("InvalidInput: answers that assume no exception need premises that name no decision: " ++
        ((rest.find? (fun x => !decisionFree L.D x.2)).map (·.1)).getD "")
    else .error notWellFormedText

/-- Diagnostic 7 (`hD`, and `hXw` through `check_iff_wellFormed`), then `viewRest`, on a decoded source `L`
    (`viewOf`'s, or a readings choice's `choiceLayeredG` source in DF-3). -/
def viewOn (j : Json) (L : LayeredU) (hU : L.U.D = soften L.D) : Except String DefaultsView :=
  if hD : WellFormedSoft L.D = true then
    if hXw : L.X.all (·.check (envAt (fill L.U) 0) []) = true then
      match viewRest j L with
      | .error e => .error e
      | .ok r => .ok ⟨L, r.R, r.hX, hU, hD,
          fun a ha => (VE.check_iff_wellFormed _ _ a).mp (List.all_eq_true.mp hXw a ha), r.hR, r.hl⟩
    else .error notWellFormedText
  else .error notWellFormedText

/-- The view's document is the source it was checked on. -/
theorem viewOn_L {j : Json} {L : LayeredU} {hU : L.U.D = soften L.D} {v : DefaultsView}
    (h : viewOn j L hU = .ok v) : v.L = L := by
  unfold viewOn at h
  split at h
  · split at h
    · split at h
      · cases h
      · cases h
        rfl
    · cases h
  · cases h

/-- `decodeLayered` itself (no second decoder), then `viewOn`. `hU` is `decodeLayered_soften`. -/
def viewOf (j : Json) : Except String DefaultsView :=
  match h : VE.NormDefaults.Wire.decodeLayered j with
  | .error e => .error e
  | .ok L => viewOn j L (decodeLayered_soften j L h)

/-- The view's document is the layered route's own decoding. -/
theorem viewOf_layered (j : Json) (v : DefaultsView) (h : viewOf j = .ok v) :
    VE.NormDefaults.Wire.decodeLayered j = .ok v.L := by
  unfold viewOf at h
  split at h
  · cases h
  · rename_i L hL
    rw [viewOn_L h]
    exact hL

/-! ## The pieces a request carries -/

/-- A collision witness: a base situation, a filling and the pair's rule names. -/
structure Collision (U : UDoc) where
  S : VE.NormDefaults.Wire.SituationG U
  F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity
  m : String
  n : String

/-- A present, non-null member `k`, decoded by `f`. -/
def pieceWith {α : Type} (j : Json) (k : String) (f : Json → Except String α) : Except String (Option α) :=
  match VE.Readings.Wire.pieceOf j k with
  | none => pure none
  | some w => some <$> f w

/-- A base situation (`situationX`) and its `filling` (`decodeFilling`). -/
def filledOf (L : LayeredU) (w : Json) : Except String (VE.Readings.Wire.FilledModel L.U) := do
  let S ← VE.NormDefaults.Wire.situationX L (← w.getObjVal? "model")
  pure ⟨S.M, S.valid, ← VE.NormDefaults.Wire.decodeFilling L.U S.M (w.getObjValD "filling")⟩

/-- A model is the request's: its `model` member's situation (`situationX`) and its `filling`. -/
theorem filledOf_request {L : LayeredU} {w : Json} {m : VE.Readings.Wire.FilledModel L.U}
    (h : filledOf L w = .ok m) : ∃ mj S, w.getObjVal? "model" = .ok mj ∧ VE.NormDefaults.Wire.situationX L mj = .ok S ∧
      m.M = S.M ∧ VE.NormDefaults.Wire.decodeFilling L.U S.M (w.getObjValD "filling") = .ok m.F := by
  unfold filledOf at h
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨S, hS, h⟩ := bind_ok h
  obtain ⟨F, hF, h⟩ := bind_ok h
  cases h
  exact ⟨mj, S, hmj, hS, rfl, hF⟩

def collisionOf (L : LayeredU) (w : Json) : Except String (Collision L.U) := do
  let S ← VE.NormDefaults.Wire.situationX L (← w.getObjVal? "model")
  let F ← VE.NormDefaults.Wire.decodeFilling L.U S.M (w.getObjValD "filling")
  match ← VE.Bridge.strings (← w.getObjVal? "rules") with
  | [m, n] =>
    if let some r := [m, n].find? (fun r => !L.D.T.nodes.any (·.name == r)) then
      throw s!"InvalidInput: a collision names an undeclared rule {r}"
    pure ⟨S, F, m, n⟩
  | _ => throw "InvalidInput: a collision names two rules"

/-- A collision is the request's: `model` (`situationX`), `filling` and `rules`. -/
theorem collisionOf_request {L : LayeredU} {w : Json} {c : Collision L.U}
    (h : collisionOf L w = .ok c) : ∃ mj rs, w.getObjVal? "model" = .ok mj ∧ VE.NormDefaults.Wire.situationX L mj = .ok c.S ∧
      VE.NormDefaults.Wire.decodeFilling L.U c.S.M (w.getObjValD "filling") = .ok c.F ∧
      w.getObjVal? "rules" = .ok rs ∧ VE.Bridge.strings rs = .ok [c.m, c.n] := by
  unfold collisionOf at h
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨S, hS, h⟩ := bind_ok h
  obtain ⟨F, hF, h⟩ := bind_ok h
  obtain ⟨rs, hrs, h⟩ := bind_ok h
  obtain ⟨ns, hns, h⟩ := bind_ok h
  split at h
  · split at h
    · cases h
    · cases h
      exact ⟨mj, rs, hmj, hS, hF, hrs, hns⟩
  · cases h

def pairText : String := "InvalidInput: coherence certificates do not match the colliding pairs"

/-- A pair's certificate bound to the source, to `backgroundBase ++ (Exc_T ++ R ++ Dflt_T) ++ Fill_T` and to the pair's
    `cohPremiseU` (`bindingOk`, as `bindCertX`). -/
def bindPair (environment : Json) (v : DefaultsView) (P Q : SoftNode) (c : Json) :
    Except String VE.Tableau.Certificate := do
  let U := v.L.U
  let cert ← VE.CertificateWire.decodeCertificate c
  VE.Route.Wire.bindingOk (VE.NormDefaults.Wire.profilesOf environment)
    (← VE.NormDefaults.Wire.canonicalEnvironmentJsonU environment)
    ((VE.Norms.backgroundBase (fill U) ++ (VE.SoftNorms.excPremises v.L.D ++ v.R ++ dfltPremises v.L.D) ++
      VE.NormDefaults.fillPremises U).map VE.NormDefaults.Wire.enc)
    (VE.NormDefaults.Wire.enc (VE.NormDefaults.Wire.cohPremiseU U v.L.D P Q))
    cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure cert

/-- Diagnostic 5: `coherence` lists the colliding pairs in `coherence_targets` order, each with its rule names and an
    optional certificate; a certificate that does not bind is absent. An absent, `null` or empty list sends no
    certificate for any pair (DF-ω's `[]`). -/
def pairCertsOf (environment : Json) (v : DefaultsView) (j : Json) :
    Except String (List (Option VE.Tableau.Certificate)) := do
  let entries ← match VE.Readings.Wire.pieceOf j "coherence" with
    | none => pure []
    | some c => (·.toList) <$> c.getArr?
  let pairs := VE.SoftNorms.collidingPairs v.L.D
  if entries.isEmpty then return pairs.map fun _ => none
  unless entries.length == pairs.length do throw pairText
  (pairs.zip entries).mapM fun ((P, Q), e) => do
    unless (← VE.Bridge.strings (← e.getObjVal? "rules")) == [P.name, Q.name] do throw pairText
    pure ((VE.Readings.Wire.pieceOf e "certificate").bind fun c => (bindPair environment v P Q c).toOption)

/-! ## `defaults-certificate` -/

structure CertReplay where
  v : DefaultsView
  Γ : List VE.Formula
  φ : VE.Formula
  cert : Option VE.Tableau.Certificate
  pairCerts : List (Option VE.Tableau.Certificate)
  collision : Option (Collision v.L.U)
  model : Option (VE.Readings.Wire.FilledModel v.L.U)
  strictModel : Option (VE.Readings.Wire.FilledModel v.L.U)

def CertReplay.certOk (x : CertReplay) : Bool :=
  match x.cert with
  | some c => certChecks x.v.L.U (premisesX x.v.L.U (defaultX x.v.L.D x.v.L.X) x.Γ) x.φ c
  | none => false
def CertReplay.coherent (x : CertReplay) : Bool := defaultCoherenceCheck x.v.L.U x.v.L.D x.v.R x.pairCerts
def CertReplay.collides (x : CertReplay) : Bool :=
  match x.collision with
  | some w => collisionCheck x.v.L.U x.v.L.D x.v.R w.S.M w.F w.m w.n
  | none => false
def CertReplay.modelOk (x : CertReplay) : Bool :=
  match x.model with
  | some m => VE.Readings.Wire.xModelOk x.v.L.U (defaultX x.v.L.D x.v.L.X) [] x.Γ .bottom m false
  | none => false
def CertReplay.strictCounter (x : CertReplay) : Bool :=
  match x.strictModel with
  | some m => VE.Readings.Wire.xModelOk x.v.L.U x.v.L.X [] x.Γ x.φ m false
  | none => false
def CertReplay.assumptions (x : CertReplay) : List String :=
  match x.cert with
  | some c => assumptionsOf x.v.L.U x.v.L.D x.v.L.X x.Γ x.φ c
  | none => []
def CertReplay.basis (x : CertReplay) : Basis := basisOf x.assumptions x.strictCounter
def CertReplay.form (x : CertReplay) : Form := followsForm x.v.L.D x.assumptions

/-- FOLLOWS needs the certificate, the gate and the model. -/
def CertReplay.verdict (x : CertReplay) : String :=
  if x.certOk && x.coherent && x.modelOk then "FOLLOWS" else "UNKNOWN"

/-- Plan 2.6's order: a checked collision first, whether or not a certificate was sent (it implies
    `coherent = false`, so no verdict changes); then the gate, the model and the certificate. -/
def CertReplay.reason (x : CertReplay) : String :=
  match x.collision, x.collides with
  | some w, true => s!"with no exception, rules {w.m} and {w.n} conflict"
  | _, _ =>
    if !x.coherent then "no-exception coherence not checked"
    else if !x.modelOk then "no checked situation where the premises hold with no exception"
    else "no certificate"

/-- `replayCert` on a decoded view. -/
def replayCertOn (v : DefaultsView) (j : Json) : Except String CertReplay := do
  let environment ← j.getObjVal? "environment"
  let E := envAt (fill v.L.U) (size (fill v.L.U))
  let premisesJson ← j.getObjVal? "premises"
  let Γ ← VE.Route.Wire.decodeFormulas E premisesJson
  if let some e := questionDiag v.L.D Γ then throw e
  let conclusionJson ← j.getObjVal? "conclusion"
  let φ ← VE.Route.Wire.decodeClosed E conclusionJson
  let pairCerts ← pairCertsOf environment v j
  let own ← premisesJson.getArr?
  let cert := (VE.Readings.Wire.pieceOf j "certificate").bind fun c =>
    (VE.NormDefaults.Wire.bindCertX environment v.L.U (defaultX v.L.D v.L.X) [] own.toList conclusionJson c).toOption
  let collision ← pieceWith j "collision" (collisionOf v.L)
  let model ← pieceWith j "model" (filledOf v.L)
  let strictModel ← pieceWith j "strict_model" (filledOf v.L)
  pure ⟨v, Γ, φ, cert, pairCerts, collision, model, strictModel⟩

/-- The view, the premises (diagnostic 3), the conclusion, the certificate bound by `bindCertX` to
    `premisesX U (defaultX D X) Γ` (absent when it does not bind), the pair certificates (diagnostic 5), the
    collision witness, the model and the strict model. -/
def replayCert (j : Json) : Except String CertReplay := do replayCertOn (← viewOf j) j

/-- What `replayCertOn` reads is the request's: `Γ` and `φ` decode `premises` and `conclusion`, the certificate is
    bound to the request's own premises and conclusion, and the pair certificates, the collision and the two models
    are its members' (review F1's class: a member replaced by a constant does not prove this). -/
theorem replayCertOn_request {v : DefaultsView} {j : Json} {x : CertReplay} (h : replayCertOn v j = .ok x) :
    x.v = v ∧ ∃ e p c own, j.getObjVal? "environment" = .ok e ∧ j.getObjVal? "premises" = .ok p ∧
      j.getObjVal? "conclusion" = .ok c ∧ p.getArr? = .ok own ∧
      VE.Route.Wire.decodeFormulas (envAt (fill x.v.L.U) (size (fill x.v.L.U))) p = .ok x.Γ ∧
      VE.Route.Wire.decodeClosed (envAt (fill x.v.L.U) (size (fill x.v.L.U))) c = .ok x.φ ∧
      pairCertsOf e x.v j = .ok x.pairCerts ∧
      x.cert = (VE.Readings.Wire.pieceOf j "certificate").bind (fun cj => (VE.NormDefaults.Wire.bindCertX e x.v.L.U
        (defaultX x.v.L.D x.v.L.X) [] own.toList c cj).toOption) ∧
      pieceWith j "collision" (collisionOf x.v.L) = .ok x.collision ∧
      pieceWith j "model" (filledOf x.v.L) = .ok x.model ∧
      pieceWith j "strict_model" (filledOf x.v.L) = .ok x.strictModel := by
  unfold replayCertOn at h
  obtain ⟨e, he, h⟩ := bind_ok h
  obtain ⟨p, hp, h⟩ := bind_ok h
  obtain ⟨Γ, hΓ, h⟩ := bind_ok h
  split at h
  · cases h
  · obtain ⟨_, -, h⟩ := bind_ok h
    obtain ⟨c, hc, h⟩ := bind_ok h
    obtain ⟨φ, hφ, h⟩ := bind_ok h
    obtain ⟨pc, hpc, h⟩ := bind_ok h
    obtain ⟨own, hown, h⟩ := bind_ok h
    obtain ⟨col, hcol, h⟩ := bind_ok h
    obtain ⟨m, hm, h⟩ := bind_ok h
    obtain ⟨sm, hsm, h⟩ := bind_ok h
    cases h
    exact ⟨rfl, e, p, c, own, he, hp, hc, hown, hΓ, hφ, hpc, rfl, hcol, hm, hsm⟩

/-- FOLLOWS is given only with the certificate, the gate and the model. -/
theorem defaults_follows_gated (x : CertReplay) (hv : x.verdict = "FOLLOWS") :
    x.certOk = true ∧ x.coherent = true ∧ x.modelOk = true := by
  unfold CertReplay.verdict at hv
  split at hv
  · rename_i h
    simp only [Bool.and_eq_true] at h
    exact ⟨h.1.1, h.1.2, h.2⟩
  · exact absurd hv (by decide)

theorem defaults_certificate_sound (x : CertReplay) (hv : x.verdict = "FOLLOWS") :
    EntailsX.{u} x.v.L.U (x.v.L.X ++ VE.Readings.blank (dfltLabelled x.v.L.D) x.assumptions) x.Γ x.φ ∧
    DefaultCoherent.{u} x.v.L.U x.v.L.D x.v.R ∧
    VE.Readings.ConsistentX x.v.L.U (defaultX x.v.L.D x.v.L.X) x.Γ ∧
    (x.basis = .strict → EntailsX.{u} x.v.L.U x.v.L.X x.Γ x.φ) ∧
    (x.basis = .needs → VE.Readings.CounterX x.v.L.U x.v.L.X x.Γ x.φ) := by
  obtain ⟨hc, hcoh, hm⟩ := defaults_follows_gated x hv
  cases hcert : x.cert with
  | none => simp [CertReplay.certOk, hcert] at hc
  | some c =>
    have hc' : certChecks x.v.L.U (premisesX x.v.L.U (defaultX x.v.L.D x.v.L.X) x.Γ) x.φ c = true := by
      simpa [CertReplay.certOk, hcert] using hc
    have has : x.assumptions = assumptionsOf x.v.L.U x.v.L.D x.v.L.X x.Γ x.φ c := by
      simp [CertReplay.assumptions, hcert]
    refine ⟨?_, defaultCoherenceCheck_sound _ _ _ _ hcoh, ?_, ?_, ?_⟩
    · rw [has]
      exact assumptions_sound _ x.v.L.wfU _ x.v.hU x.v.hD x.v.hl _ _ x.v.hXw _ c hc'
    · cases hmod : x.model with
      | none => simp [CertReplay.modelOk, hmod] at hm
      | some m =>
        have hm' : VE.Readings.Wire.xModelOk x.v.L.U (defaultX x.v.L.D x.v.L.X) [] x.Γ .bottom m false = true := by
          simpa [CertReplay.modelOk, hmod] using hm
        obtain ⟨⟨S, h1, h2, h3, _⟩, _⟩ := basis_needs_sound _ x.v.L.wfU _ _ _ m hm'
        exact ⟨S, h1, h2, h3⟩
    · intro hb
      rw [CertReplay.basis, has] at hb
      exact basis_strict_sound _ x.v.L.wfU _ x.v.hU x.v.hD x.v.hl _ _ x.v.hXw _ c hc' _ hb
    · intro hb
      have hs : x.strictCounter = true := by
        unfold CertReplay.basis basisOf at hb
        split at hb
        · cases hb
        · split at hb
          · assumption
          · cases hb
      cases hsm : x.strictModel with
      | none => simp [CertReplay.strictCounter, hsm] at hs
      | some m =>
        have hs' : VE.Readings.Wire.xModelOk x.v.L.U x.v.L.X [] x.Γ x.φ m false = true := by
          simpa [CertReplay.strictCounter, hsm] using hs
        exact (basis_needs_sound _ x.v.L.wfU _ _ _ m hs').1

/-! ## `defaults-elaborate` and `defaults-coherence` -/

/-- `defaults-elaborate`: `default_premises` (label, AST) and `coherence_targets` (the two rule names and the pair's
    `cohPremiseU`), in these orders. -/
def elaborateRows (v : DefaultsView) : List (String × VE.Formula) × List (SoftNode × SoftNode) :=
  (dfltLabelled v.L.D, VE.SoftNorms.collidingPairs v.L.D)

theorem elaborateRows_eq (v : DefaultsView) :
    (elaborateRows v).1 = dfltLabelled v.L.D ∧ (elaborateRows v).2 = VE.SoftNorms.collidingPairs v.L.D := ⟨rfl, rfl⟩

structure CoherenceReplay where
  v : DefaultsView
  pairCerts : List (Option VE.Tableau.Certificate)
  collision : Option (Collision v.L.U)

def CoherenceReplay.coherent (x : CoherenceReplay) : Bool :=
  defaultCoherenceCheck x.v.L.U x.v.L.D x.v.R x.pairCerts
def CoherenceReplay.collides (x : CoherenceReplay) : Bool :=
  match x.collision with
  | some w => collisionCheck x.v.L.U x.v.L.D x.v.R w.S.M w.F w.m w.n
  | none => false

/-- COHERENT with every pair certificate checked, COLLISION with a checked collision, UNKNOWN otherwise. -/
def CoherenceReplay.verdict (x : CoherenceReplay) : String :=
  if x.coherent then "COHERENT" else if x.collides then "COLLISION" else "UNKNOWN"

inductive PairStatus | resolved | collision | unknown
  deriving DecidableEq, Repr

/-- Each colliding pair, in `collidingPairs` order, with its status. -/
def CoherenceReplay.pairs (x : CoherenceReplay) : List ((SoftNode × SoftNode) × PairStatus) :=
  (VE.SoftNorms.collidingPairs x.v.L.D).mapIdx (fun i p =>
    (p, if pairChecks x.v.L.U x.v.L.D x.v.R p.1 p.2 (x.pairCerts.getD i none) then .resolved
        else if x.collides && x.collision.any (fun w => w.m == p.1.name && w.n == p.2.name) then .collision
        else .unknown))

def replayCoherenceOn (v : DefaultsView) (j : Json) : Except String CoherenceReplay := do
  let pairCerts ← pairCertsOf (← j.getObjVal? "environment") v j
  pure ⟨v, pairCerts, ← pieceWith j "collision" (collisionOf v.L)⟩

/-- The view, the pair certificates (diagnostic 5) and the collision witness. -/
def replayCoherence (j : Json) : Except String CoherenceReplay := do replayCoherenceOn (← viewOf j) j

/-- What `replayCoherenceOn` reads is the request's: the pair certificates and the collision. -/
theorem replayCoherenceOn_request {v : DefaultsView} {j : Json} {x : CoherenceReplay}
    (h : replayCoherenceOn v j = .ok x) : x.v = v ∧ ∃ e, j.getObjVal? "environment" = .ok e ∧
      pairCertsOf e x.v j = .ok x.pairCerts ∧ pieceWith j "collision" (collisionOf x.v.L) = .ok x.collision := by
  unfold replayCoherenceOn at h
  obtain ⟨e, he, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  cases h
  exact ⟨rfl, e, he, hps, hc⟩

theorem defaults_coherence_sound (x : CoherenceReplay) :
    (x.verdict = "COHERENT" → DefaultCoherent.{u} x.v.L.U x.v.L.D x.v.R) ∧
    (x.verdict = "COLLISION" → ¬ DefaultCoherent.{0} x.v.L.U x.v.L.D x.v.R) ∧
    (∀ P Q, ((P, Q), PairStatus.resolved) ∈ x.pairs → ∀ B : VE.Structure.{u},
      VE.NormDefaults.Wire.BaseAdmissibleX x.v.L.U (VE.SoftNorms.excPremises x.v.L.D ++ x.v.R ++ dfltPremises x.v.L.D) B →
        (VE.NormDefaults.Wire.cohPremiseU x.v.L.U x.v.L.D P Q).denote B []) := by
  refine ⟨fun hv => ?_, fun hv => ?_, fun P Q hm B hB => ?_⟩
  · unfold CoherenceReplay.verdict at hv
    split at hv
    · exact defaultCoherenceCheck_sound _ _ _ _ ‹_›
    · split at hv <;> exact absurd hv (by decide)
  · unfold CoherenceReplay.verdict at hv
    split at hv
    · exact absurd hv (by decide)
    · split at hv
      · rename_i hc
        unfold CoherenceReplay.collides at hc
        split at hc
        · rename_i w _
          exact collision_sound _ x.v.L.wfU _ _ _ w.S.valid _ _ _ hc
        · cases hc
      · exact absurd hv (by decide)
  · unfold CoherenceReplay.pairs at hm
    obtain ⟨i, hi, he⟩ := List.mem_mapIdx.mp hm
    simp only [Prod.mk.injEq] at he
    obtain ⟨hp, hs⟩ := he
    split at hs
    · rename_i hc
      rw [hp] at hc
      exact pairChecks_sound _ _ _ _ _ _ hc B hB
    · split at hs <;> cases hs

/-! ## `defaults-model` -/

/-- The exceptions that hold on the finite base, each with the index of the first stated sufficient condition that
    holds at its tuple (the number of conditions when none does), in rule order, then tuple order. -/
def forcedAt (D : SoftDoc) (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) : List (String × Nat × List VE.Bridge.Entity) :=
  D.T.nodes.flatMap (fun N => match N.mode with
    | .default =>
      let conds := (N.exception.map (·.sufficient)).getD []
      (VE.NormDefaults.allTuples M (VE.SoftNorms.sortsOf D N.pred)).filterMap (fun vs =>
        if (VE.SoftNorms.exceptedF D N).eval (M.withFill F) (VE.Norms.tupleVal vs) then
          some (N.name, (conds.findIdx? (fun C => C.eval (M.withFill F) (VE.Norms.tupleVal vs))).getD conds.length, vs)
        else none)
    | .strict => [])

structure ModelReplay where
  v : DefaultsView
  Γ : List VE.Formula
  φ : VE.Formula
  m : VE.Readings.Wire.FilledModel v.L.U

def ModelReplay.ok (x : ModelReplay) : Bool :=
  VE.Readings.Wire.xModelOk x.v.L.U (defaultX x.v.L.D x.v.L.X) [] x.Γ x.φ x.m false
def ModelReplay.forced (x : ModelReplay) : List (String × Nat × List VE.Bridge.Entity) :=
  forcedAt x.v.L.D x.v.L.U x.m.M x.m.F
def ModelReplay.verdict (x : ModelReplay) : String := if x.ok then "DOES-NOT-FOLLOW" else "UNKNOWN"

def replayModelOn (v : DefaultsView) (j : Json) : Except String ModelReplay := do
  let E := envAt (fill v.L.U) (size (fill v.L.U))
  let Γ ← VE.Route.Wire.decodeFormulas E (← j.getObjVal? "premises")
  let φ ← VE.Route.Wire.decodeClosed E (← j.getObjVal? "conclusion")
  pure ⟨v, Γ, φ, ← filledOf v.L (← j.getObjVal? "model")⟩

def replayModel (j : Json) : Except String ModelReplay := do replayModelOn (← viewOf j) j

/-- What `replayModelOn` reads is the request's: `Γ`, `φ` and the model decode `premises`, `conclusion` and `model`,
    so `defaults_model_sound`'s `x.Γ` is the question's premises (review F1). -/
theorem replayModelOn_request {v : DefaultsView} {j : Json} {x : ModelReplay} (h : replayModelOn v j = .ok x) :
    x.v = v ∧ ∃ p c w, j.getObjVal? "premises" = .ok p ∧ j.getObjVal? "conclusion" = .ok c ∧
      j.getObjVal? "model" = .ok w ∧
      VE.Route.Wire.decodeFormulas (envAt (fill x.v.L.U) (size (fill x.v.L.U))) p = .ok x.Γ ∧
      VE.Route.Wire.decodeClosed (envAt (fill x.v.L.U) (size (fill x.v.L.U))) c = .ok x.φ ∧
      filledOf x.v.L w = .ok x.m := by
  unfold replayModelOn at h
  obtain ⟨p, hp, h⟩ := bind_ok h
  obtain ⟨Γ, hΓ, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  obtain ⟨φ, hφ, h⟩ := bind_ok h
  obtain ⟨w, hw, h⟩ := bind_ok h
  obtain ⟨m, hm, h⟩ := bind_ok h
  cases h
  exact ⟨rfl, p, c, w, hp, hc, hw, hΓ, hφ, hm⟩

/-- A well-formed soft document's default rules each have an exception (`checkSoftRule`). -/
theorem default_exception {D : SoftDoc} (hD : WellFormedSoft D = true) {N : SoftNode} (hN : N ∈ D.T.nodes)
    (hm : N.mode = .default) : ∃ ex, N.exception = some ex := by
  have hr := (VE.Readings.checkSoft_parts D (VE.Readings.wellFormedSoft_check D hD)).2 N hN
  cases hex : N.exception with
  | some ex => exact ⟨ex, rfl⟩
  | none =>
    exfalso
    unfold VE.SoftNorms.checkSoftRule at hr
    simp only [hm, hex, bind, Except.bind, pure, Except.pure] at hr
    repeat' split at hr
    all_goals simp_all

/-- Where the model check of `X` passes, a premise of `X` that is `∀x̄. ψ` holds at every typed tuple of the model. -/
theorem eval_of_xModelOk {x : ModelReplay} (hv : x.ok = true) {ss : List String} {ψ : VE.Formula}
    (hp : VE.Norms.bindAll ss ψ ∈ defaultX x.v.L.D x.v.L.X) {vs : List VE.Bridge.Entity}
    (hvs : vs ∈ VE.NormDefaults.allTuples x.m.M ss) :
    ψ.eval (x.m.M.withFill x.m.F) (VE.Norms.tupleVal vs) = true := by
  simp only [ModelReplay.ok, VE.Readings.Wire.xModelOk, VE.NormDefaults.modelCheckX, Bool.and_eq_true] at hv
  have he := (VE.NormDefaults.eval_withFill _ _ _ _ _).mp (List.all_eq_true.mp hv.1.1.2.2 _ hp)
  rw [VE.Norms.bindAll_denote_nil] at he
  exact (VE.NormDefaults.eval_withFill _ _ _ _ _).mpr (he vs ((VE.Norms.tupleTyped_relation x.m.M.asStructure
    _ _ vs).mpr ((VE.NormDefaults.mem_allTuples x.m.M _ vs).mp hvs)))

/-- DE6′'s and DE11's claim: each `forced` entry names a default rule, its index is below that rule's number of
    stated sufficient conditions, and that condition and the exception both hold at the entry's tuple. -/
theorem forcedAt_sound (x : ModelReplay) (hv : x.ok = true) :
    ∀ e ∈ x.forced, ∃ N ∈ x.v.L.D.T.nodes, ∃ ex : VE.SoftNorms.Exception,
      N.mode = .default ∧ N.exception = some ex ∧ e.1 = N.name ∧
      ∃ hi : e.2.1 < ex.sufficient.length,
        (ex.sufficient[e.2.1]'hi).eval (x.m.M.withFill x.m.F) (VE.Norms.tupleVal e.2.2) = true ∧
        (VE.SoftNorms.exceptedF x.v.L.D N).eval (x.m.M.withFill x.m.F) (VE.Norms.tupleVal e.2.2) = true := by
  intro e he
  simp only [ModelReplay.forced, forcedAt, List.mem_flatMap] at he
  obtain ⟨N, hN, he⟩ := he
  split at he
  · rename_i hm
    obtain ⟨ex, hex⟩ := default_exception x.v.hD hN hm
    simp only [hex, Option.map_some, Option.getD_some, List.mem_filterMap] at he
    obtain ⟨vs, hvs, he⟩ := he
    split at he
    · rename_i hexc
      cases he
      have hd : (VE.Norms.bindAll (VE.SoftNorms.sortsOf x.v.L.D N.pred)
          (.implies (VE.SoftNorms.exceptedF x.v.L.D N) (VE.Norms.anyF ex.sufficient))) ∈
          defaultX x.v.L.D x.v.L.X :=
        List.mem_append_right _ (List.mem_map.mpr ⟨_, List.mem_append_left _ (List.mem_flatMap.mpr ⟨N, hN, by
          simp only [dfltOf, hm, hex]; exact List.mem_append_left _ List.mem_cons_self⟩), rfl⟩)
      have hc := eval_of_xModelOk hv hd hvs
      simp only [VE.Formula.eval, hexc, Bool.not_true, Bool.false_or, VE.Readings.Wire.anyF_eval] at hc
      obtain ⟨i, hi⟩ : ∃ i, ex.sufficient.findIdx? (fun C => C.eval (x.m.M.withFill x.m.F)
          (VE.Norms.tupleVal vs)) = some i := Option.isSome_iff_exists.mp (by
        rw [List.findIdx?_isSome]; simpa using hc)
      obtain ⟨hlt, hci, -⟩ := List.findIdx?_eq_some_iff_getElem.mp hi
      exact ⟨N, hN, ex, hm, hex, rfl, by simp only [hi, Option.getD_some]; exact hlt,
        by simpa [hi] using hci, hexc⟩
    · cases he
  · cases he

/-- The situation shown; with `forced = []` no rule's exception holds there (DE6's short form). -/
theorem defaults_model_sound (x : ModelReplay) (hv : x.ok = true) :
    ∃ S : VE.Structure.{0},
      VE.NormDefaults.Wire.BaseAdmissibleX x.v.L.U (defaultX x.v.L.D x.v.L.X)
        (VE.Norms.restrictAll (fill x.v.L.U).T S) ∧
      VE.Norms.DocumentExpansion (fill x.v.L.U) (VE.Norms.restrictAll (fill x.v.L.U).T S) S ∧
      VE.Norms.Sat S x.Γ ∧ ¬ x.φ.denote S [] ∧
      (x.forced = [] → ∀ N ∈ x.v.L.D.T.nodes, N.mode = .default →
        (VE.Norms.bindAll (VE.SoftNorms.sortsOf x.v.L.D N.pred) (.not (VE.SoftNorms.exceptedF x.v.L.D N))).denote S []) := by
  let D := x.v.L.D
  let U := x.v.L.U
  -- "no exception holds", one premise per default rule
  let none_ : List VE.Formula := (D.T.nodes.filter (·.mode == .default)).map (fun N =>
    VE.Norms.bindAll (VE.SoftNorms.sortsOf D N.pred) (.not (VE.SoftNorms.exceptedF D N)))
  have hwf : ∀ N ∈ D.T.nodes, N.mode = .default →
      (VE.Norms.bindAll (VE.SoftNorms.sortsOf D N.pred) (.not (VE.SoftNorms.exceptedF D N))).WellFormed
        (envAt (fill U) 0) [] := by
    intro N hN hm
    have hd : (VE.SoftNorms.exceptedName N, VE.SoftNorms.sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
      VE.Readings.mem_decisions.mpr (Or.inl ⟨N, hN, hm, rfl⟩)
    have hb := VE.Norms.bindAll_wellFormed (E := envAt (soften D) 0)
      (fun s hs => VE.Readings.decision_sorts x.v.hD hd s hs) [] (.not (VE.SoftNorms.exceptedF D N))
      (by simpa [VE.SoftNorms.exceptedF] using atom_wf (VE.Readings.envAt_decision x.v.hD 0 hd))
    rw [← x.v.hU] at hb
    exact VE.Norms.wf_mono (E := envAt U.D 0) (E' := envAt (fill U) 0) rfl rfl
      (VE.NormDefaults.envAt_fill_mono (VE.NormDefaults.uvalid x.v.L.wfU) 0) _ [] hb
  have hok := hv
  simp only [ModelReplay.ok, VE.Readings.Wire.xModelOk, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hok
  obtain ⟨⟨⟨hw, hm⟩, hval⟩, hl⟩ := hok
  have hw' : ∀ a ∈ ([] ++ x.Γ) ++ [x.φ], a.WellFormed (envAt (fill U) (size (fill U))) [] :=
    fun a ha => (VE.check_iff_wellFormed _ _ a).mp (hw a ha)
  have hΓ := fun a ha => hw' a (List.mem_append_left _ ha)
  have hφ := hw' x.φ (List.mem_append_right _ List.mem_cons_self)
  by_cases hf : x.forced = []
  · -- with `forced = []` every "no exception" premise holds on the model, so the expansion satisfies them too
    have hnone : ∀ a ∈ none_, a.eval (x.m.M.withFill x.m.F) [] = true := by
      intro a ha
      obtain ⟨N, hN, rfl⟩ := List.mem_map.mp ha
      obtain ⟨hN, hm⟩ := List.mem_filter.mp hN
      simp only [beq_iff_eq] at hm
      apply (VE.NormDefaults.eval_withFill _ _ _ _ _).mpr
      rw [VE.Norms.bindAll_denote_nil]
      intro vs hvs
      apply (VE.NormDefaults.eval_withFill _ _ _ _ _).mp
      have hmem := (VE.NormDefaults.mem_allTuples x.m.M _ vs).mpr
        ((VE.Norms.tupleTyped_relation x.m.M.asStructure _ _ vs).mp hvs)
      simp only [ModelReplay.forced, forcedAt, List.flatMap_eq_nil_iff] at hf
      have := hf N hN
      simp only [hm, List.filterMap_eq_nil_iff] at this
      have h2 := this vs hmem
      cases he : (VE.SoftNorms.exceptedF x.v.L.D N).eval (x.m.M.withFill x.m.F) (VE.Norms.tupleVal vs)
      · simp [VE.Formula.eval, D, he]
      · simp [he] at h2
    have hm2 : (VE.NormDefaults.modelCheckX U (defaultX D x.v.L.X ++ none_) x.m.M x.m.F ([] ++ x.Γ) x.φ).1 = true := by
      simp only [VE.NormDefaults.modelCheckX, Bool.and_eq_true] at hm ⊢
      refine ⟨hm.1, ?_⟩
      simp only [VE.NormDefaults.Wire.extraValid, List.all_append, Bool.and_eq_true] at hm ⊢
      exact ⟨hm.2, List.all_eq_true.mpr hnone⟩
    obtain ⟨S, h1, h2, h3, h4⟩ := VE.Readings.Wire.expansionX_of_modelCheck U x.v.L.wfU _ x.m.M x.m.valid x.m.F
      _ _ hΓ hφ hm2 hl
    refine ⟨S, ⟨h1.1, fun a ha => h1.2 a (List.mem_append_left _ ha)⟩, h2, by simpa using h3, fun hd => ?_,
      fun _ N hN hm => ?_⟩
    · have := h4.mp hd
      simp only [VE.NormDefaults.modelCheckX] at this hval
      rw [hval] at this
      cases this
    · have ha := h1.2 _ (List.mem_append_right _ (List.mem_map.mpr ⟨N, List.mem_filter.mpr ⟨hN, by simpa using hm⟩, rfl⟩))
      exact (VE.Norms.restrictAll_denote _ [] (hwf N hN hm) S []).mp ha
  · obtain ⟨S, h1, h2, h3, h4⟩ := VE.Readings.Wire.expansionX_of_modelCheck U x.v.L.wfU _ x.m.M x.m.valid x.m.F
      _ _ hΓ hφ hm hl
    refine ⟨S, h1, h2, by simpa using h3, fun hd => ?_, fun h => absurd h hf⟩
    have := h4.mp hd
    rw [hval] at this
    cases this

/-! ## The answers -/

def entityIds (vs : List VE.Bridge.Entity) : Json := toJson (vs.map (·.2))

def elaborateFields (v : DefaultsView) : List (String × Json) :=
  [("deciders", toJson (decidersOf v.L.D)),
   ("default_premises", Json.arr ((elaborateRows v).1.map (fun (l, a) =>
      Json.arr #[.str l, VE.NormDefaults.Wire.enc a])).toArray),
   ("coherence_targets", Json.arr ((elaborateRows v).2.map (fun (P, Q) => Json.arr #[.str P.name, .str Q.name,
      VE.NormDefaults.Wire.enc (VE.NormDefaults.Wire.cohPremiseU v.L.U v.L.D P Q)])).toArray)]

def PairStatus.label : PairStatus → String
  | .resolved => "resolved" | .collision => "collision" | .unknown => "unknown"

/-- The situation shown (DE6, DE7): its gaps, every unsaid table of the checked filled situation, as a reachable
    report line shows its witness (`witnessRow`). -/
def situationJson (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity) (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) :
    Json :=
  Json.mkObj [("filling", Json.mkObj (VE.NormDefaults.Wire.witnessRow U (M.withFill F) []).filling)]

/-- A collision's pair, the tuple Lean finds and DE7's deciders, then the situation (`defaults-coherence` and DF-3's
    readings member). -/
def collisionFields (U : UDoc) (D : SoftDoc) (w : Collision U) : List (String × Json) :=
  match (VE.SoftNorms.collidingPairs D).find? (fun p => p.1.name == w.m && p.2.name == w.n) with
  | some (P, Q) => [("collision", Json.mkObj [("rules", toJson [w.m, w.n]),
      ("tuple", entityIds ((collisionTuple U D w.S.M w.F P Q).getD [])),
      ("deciders", toJson (giveWayDeciders D P Q))]),
      ("situation", situationJson U w.S.M w.F)]
  | none => []

/-- The verdict and the pairs' statuses; with COLLISION, `collisionFields`. -/
def coherenceFields (x : CoherenceReplay) : List (String × Json) :=
  [("verdict", .str x.verdict), ("pairs", Json.arr (x.pairs.map (fun (p, s) =>
      Json.mkObj [("rules", toJson [p.1.name, p.2.name]), ("status", .str s.label)])).toArray)] ++
  match x.verdict == "COLLISION", x.collision with
  | true, some w => collisionFields x.v.L.U x.v.L.D w
  | _, _ => []

/-- What the answer shows of a collision: a pair shown `collision`, or a `collision` member, only with a collision
    that checks, and a checked collision means the document is not coherent. -/
theorem coherence_collision_shown (x : CoherenceReplay) :
    (∀ P Q, ((P, Q), PairStatus.collision) ∈ x.pairs → x.collides = true) ∧
    ((coherenceFields x).any (·.1 == "collision") = true → x.verdict = "COLLISION") ∧
    (x.collides = true → ¬ DefaultCoherent.{0} x.v.L.U x.v.L.D x.v.R) := by
  refine ⟨fun P Q hm => ?_, fun h => ?_, fun hc => ?_⟩
  · unfold CoherenceReplay.pairs at hm
    obtain ⟨i, hi, he⟩ := List.mem_mapIdx.mp hm
    simp only [Prod.mk.injEq] at he
    obtain ⟨_, hs⟩ := he
    split at hs
    · cases hs
    · split at hs
      · rename_i hc
        simp only [Bool.and_eq_true] at hc
        exact hc.1
      · cases hs
  · unfold coherenceFields collisionFields at h
    split at h
    · rename_i hv _
      exact beq_iff_eq.mp hv
    · simp at h
  · unfold CoherenceReplay.collides at hc
    split at hc
    · rename_i w _
      exact collision_sound _ x.v.L.wfU _ _ _ w.S.valid _ _ _ hc
    · cases hc

/-- Which pair the answer shows for a collision: a pair shown `collision` is the pair the collision names, both rule
    names, and the `collision` member's tuple and deciders are those of a colliding pair named exactly as the collision
    names it, never a pair that shares one rule with it. -/
theorem coherence_collision_named (x : CoherenceReplay) :
    (∀ P Q, ((P, Q), PairStatus.collision) ∈ x.pairs → ∃ w, x.collision = some w ∧ w.m = P.name ∧ w.n = Q.name) ∧
    (∀ c, ("collision", c) ∈ coherenceFields x → ∃ w P Q, x.collision = some w ∧
      (P, Q) ∈ VE.SoftNorms.collidingPairs x.v.L.D ∧ P.name = w.m ∧ Q.name = w.n ∧
      c = Json.mkObj [("rules", toJson [w.m, w.n]),
        ("tuple", entityIds ((collisionTuple x.v.L.U x.v.L.D w.S.M w.F P Q).getD [])),
        ("deciders", toJson (giveWayDeciders x.v.L.D P Q))]) := by
  refine ⟨fun P Q hm => ?_, fun c h => ?_⟩
  · unfold CoherenceReplay.pairs at hm
    obtain ⟨i, hi, he⟩ := List.mem_mapIdx.mp hm
    simp only [Prod.mk.injEq] at he
    obtain ⟨hp, hs⟩ := he
    split at hs
    · cases hs
    · split at hs
      · rename_i hc
        simp only [Bool.and_eq_true] at hc
        obtain ⟨_, ha⟩ := hc
        cases hw : x.collision with
        | none => simp [hw] at ha
        | some w =>
          simp only [hw, Option.any_some, Bool.and_eq_true, beq_iff_eq] at ha
          rw [hp] at ha
          exact ⟨w, rfl, ha.1, ha.2⟩
      · cases hs
  · unfold coherenceFields collisionFields at h
    rw [List.mem_append] at h
    rcases h with h | h
    · simp at h
    · split at h
      · rename_i w _ hw
        split at h
        · rename_i P Q hf
          simp only [List.mem_cons, List.not_mem_nil, or_false, Prod.mk.injEq, true_and] at h
          rcases h with h | ⟨h, -⟩
          rotate_left
          · exact absurd h (by decide)
          have hpq := List.find?_some hf
          simp only [Bool.and_eq_true, beq_iff_eq] at hpq
          exact ⟨w, P, Q, hw, List.mem_of_find?_eq_some hf, hpq.1, hpq.2, h⟩
        · simp at h
      · simp at h

def basisLabel : Basis → String
  | .strict => "strict" | .needs => "needs" | .unsettled => "unsettled"
def formLabel : Form → String
  | .short => "short" | .long => "long"

def certFields (x : CertReplay) : List (String × Json) :=
  [("verdict", .str x.verdict)] ++
  if x.verdict == "FOLLOWS" then
    [("basis", .str (basisLabel x.basis)), ("form", .str (formLabel x.form)),
      ("assumptions", toJson x.assumptions), ("deciders", toJson (decidersOf x.v.L.D))]
  else [("reason", .str x.reason)]

def modelFields (x : ModelReplay) : List (String × Json) :=
  [("verdict", .str x.verdict)] ++
  if x.ok then [("situation", situationJson x.v.L.U x.m.M x.m.F), ("forced", Json.arr (x.forced.map (fun (r, i, vs) =>
    Json.mkObj [("rule", .str r), ("condition", toJson i), ("tuple", entityIds vs)])).toArray)] else []

/-- The `defaults-*` kinds; `none` for any other kind (one row of PK-1's layered kind table). -/
def defaultsCase (v : DefaultsView) (id kind : String) (j : Json) : Except String (Option Json) :=
  if kind.startsWith "defaults-" then
    if kind == "defaults-elaborate" then pure (some (VE.Route.Wire.ok id (elaborateFields v)))
    else if kind == "defaults-coherence" then
      (fun x => some (VE.Route.Wire.ok id (coherenceFields x))) <$> replayCoherenceOn v j
    else if kind == "defaults-certificate" then
      (fun x => some (VE.Route.Wire.ok id (certFields x))) <$> replayCertOn v j
    else if kind == "defaults-model" then
      (fun x => some (VE.Route.Wire.ok id (modelFields x))) <$> replayModelOn v j
    else pure none
  else pure none

theorem defaultsCase_other (v : DefaultsView) (id kind : String) (j : Json)
    (hk : kind.startsWith "defaults-" = false) : defaultsCase v id kind j = .ok none := by
  simp [defaultsCase, hk]; rfl

end VE.Defaults.Wire
