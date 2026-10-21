import VE.Defaults.Premises
import VE.NormDefaults.LayeredAdmission

/-! The `defaults-*` kinds on a layered source (docs/spec/defeasible.md 7.2; plan DF-1a, 2.2 and 2.6).

Every case decodes its source with the layered route's own `decodeLayered` (`viewOf`), then checks that the document
is well formed (diagnostic 7) and that a default answer applies to it: no `weighing@0` (1), no decision in the other
packs' premises `R` (2), distinct generated labels (6), generated premises within soft's limits (4). Then:

* `defaults-elaborate`: `Dflt_T` and the colliding pairs with their coherence premises (`elaborateRows`).
* `defaults-coherence`: one optional certificate per colliding pair (diagnostic 5) and an optional collision; COHERENT,
  COLLISION or UNKNOWN, with each pair's status (`defaults_coherence_sound`), and with a collision the tuple and the
  deciders DE7 shows.
* The question kinds, `defaults-certificate` (FOLLOWS needs a certificate bound to `premisesX U (defaultX D X) Γ`, the
  gate's certificates and a checked model) and `defaults-model` (a countermodel of `defaultX` with the exceptions the
  text's own conditions force there), are df-1ad's.

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

/-- `decodeLayered` itself (no second decoder), then diagnostic 7 (`hD`, and `hXw` through `check_iff_wellFormed`),
    then `viewRest`. `hU` is `decodeLayered_soften`. -/
def viewOf (j : Json) : Except String DefaultsView :=
  match h : VE.NormDefaults.Wire.decodeLayered j with
  | .error e => .error e
  | .ok L =>
    if hD : WellFormedSoft L.D = true then
      if hXw : L.X.all (·.check (envAt (fill L.U) 0) []) = true then
        match viewRest j L with
        | .error e => .error e
        | .ok r => .ok ⟨L, r.R, r.hX, decodeLayered_soften j L h, hD,
            fun a ha => (VE.check_iff_wellFormed _ _ a).mp (List.all_eq_true.mp hXw a ha), r.hR, r.hl⟩
      else .error notWellFormedText
    else .error notWellFormedText

/-- The view's document is the layered route's own decoding. -/
theorem viewOf_layered (j : Json) (v : DefaultsView) (h : viewOf j = .ok v) :
    VE.NormDefaults.Wire.decodeLayered j = .ok v.L := by
  unfold viewOf at h
  split at h
  · cases h
  · rename_i L hL
    split at h
    · split at h
      · split at h
        · cases h
        · cases h
          exact hL
      · cases h
    · cases h

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

def collisionOf (L : LayeredU) (w : Json) : Except String (Collision L.U) := do
  let S ← VE.NormDefaults.Wire.situationX L (← w.getObjVal? "model")
  let F ← VE.NormDefaults.Wire.decodeFilling L.U S.M (w.getObjValD "filling")
  match ← VE.Bridge.strings (← w.getObjVal? "rules") with
  | [m, n] => pure ⟨S, F, m, n⟩
  | _ => throw "InvalidInput: a collision names two rules"

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
    optional certificate; a certificate that does not bind is absent. -/
def pairCertsOf (environment : Json) (v : DefaultsView) (j : Json) :
    Except String (List (Option VE.Tableau.Certificate)) := do
  let entries ← match j.getObjVal? "coherence" with
    | .error _ => pure []
    | .ok c => (·.toList) <$> c.getArr?
  let pairs := VE.SoftNorms.collidingPairs v.L.D
  unless entries.length == pairs.length do throw pairText
  (pairs.zip entries).mapM fun ((P, Q), e) => do
    unless (← VE.Bridge.strings (← e.getObjVal? "rules")) == [P.name, Q.name] do throw pairText
    pure ((VE.Readings.Wire.pieceOf e "certificate").bind fun c => (bindPair environment v P Q c).toOption)

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

/-! ## The answers -/

def entityIds (vs : List VE.Bridge.Entity) : Json := toJson (vs.map (·.2))

def elaborateFields (v : DefaultsView) : List (String × Json) :=
  [("default_premises", Json.arr ((elaborateRows v).1.map (fun (l, a) =>
      Json.arr #[.str l, VE.NormDefaults.Wire.enc a])).toArray),
   ("coherence_targets", Json.arr ((elaborateRows v).2.map (fun (P, Q) => Json.arr #[.str P.name, .str Q.name,
      VE.NormDefaults.Wire.enc (VE.NormDefaults.Wire.cohPremiseU v.L.U v.L.D P Q)])).toArray)]

def PairStatus.label : PairStatus → String
  | .resolved => "resolved" | .collision => "collision" | .unknown => "unknown"

/-- The verdict and the pairs' statuses; with COLLISION, the pair, the tuple Lean finds and DE7's deciders. -/
def coherenceFields (x : CoherenceReplay) : List (String × Json) :=
  [("verdict", .str x.verdict), ("pairs", Json.arr (x.pairs.map (fun (p, s) =>
      Json.mkObj [("rules", toJson [p.1.name, p.2.name]), ("status", .str s.label)])).toArray)] ++
  match x.verdict == "COLLISION", x.collision with
  | true, some w =>
    match (VE.SoftNorms.collidingPairs x.v.L.D).find? (fun p => p.1.name == w.m && p.2.name == w.n) with
    | some (P, Q) => [("collision", Json.mkObj [("rules", toJson [w.m, w.n]),
        ("tuple", entityIds ((collisionTuple x.v.L.U x.v.L.D w.S.M w.F P Q).getD [])),
        ("deciders", toJson (giveWayDeciders x.v.L.D P Q))])]
    | none => []
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
  · unfold coherenceFields at h
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
  · unfold coherenceFields at h
    rw [List.mem_append] at h
    rcases h with h | h
    · simp at h
    · split at h
      · rename_i w _ hw
        split at h
        · rename_i P Q hf
          simp only [List.mem_singleton, Prod.mk.injEq, true_and] at h
          have hpq := List.find?_some hf
          simp only [Bool.and_eq_true, beq_iff_eq] at hpq
          exact ⟨w, P, Q, hw, List.mem_of_find?_eq_some hf, hpq.1, hpq.2, h⟩
        · simp at h
      · simp at h

/-- The `defaults-*` kinds; `none` for any other kind (one row of PK-1's layered kind table). -/
def defaultsCase (v : DefaultsView) (id kind : String) (j : Json) : Except String (Option Json) :=
  if kind.startsWith "defaults-" then
    if kind == "defaults-elaborate" then pure (some (VE.Route.Wire.ok id (elaborateFields v)))
    else if kind == "defaults-coherence" then
      (fun x => some (VE.Route.Wire.ok id (coherenceFields x))) <$> replayCoherenceOn v j
    else pure none
  else pure none

theorem defaultsCase_other (v : DefaultsView) (id kind : String) (j : Json)
    (hk : kind.startsWith "defaults-" = false) : defaultsCase v id kind j = .ok none := by
  simp [defaultsCase, hk]; rfl

end VE.Defaults.Wire
