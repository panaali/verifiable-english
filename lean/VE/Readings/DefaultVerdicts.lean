import VE.Readings.SoftVerdicts
import VE.Defaults.Meaning

/-! Readings unless an exception applies (docs/spec/defeasible.md 3.9 and 7.4; plan 2.4, 3.5 and batch DF-3).

`dSem N` is RD-9's `xSem` with `Dflt_T` appended to each choice's `X`; a choice's conflict freedom is RD-9's strict one
together with the gate on the choice's soft document. RD-9's `foldG_*` theorems apply to it as stated: there is no
second fold. The replay (`replayVerdictsD`) is RD-9's `replayVerdictsSD` and, per chosen choice, the default evidence
decoded on the same `choiceLayeredG` source through `defaults-*`'s own view (`viewOn`), pair certificates
(`pairCertsOf`), collision (`collisionOf`) and certificate binding (`bindCertX`). The `default` member is present only
when the strict conflict fold is FREE (`DVerdicts.defaultMember`), so a default-fold CONFLICT comes from the gate
only (`readings_wire_default_conflict`). Enumerated route only (at most 64 choices). -/
namespace VE.Readings
open VE.Defaults
universe u

/-- A choice's soft document, as RD-9's `softXL` reads it. On the soft chain `choiceX N c` is its `softX` with
    `R = []`. -/
def choiceSoft (N : NDoc) (c : Choice) : VE.SoftNorms.SoftDoc := VE.Rights.correlate (choiceDoc N.D c).1

theorem choiceX_softX (N : NDoc) (c : Choice) :
    choiceX N c = VE.Defaults.softX (choiceU N c) (choiceSoft N c) [] := by
  simp [choiceX, softX, softXL, VE.Defaults.softX, choiceSoft, choiceU]

theorem choiceU_soften (N : NDoc) (c : Choice) : (choiceU N c).D = VE.SoftNorms.soften (choiceSoft N c) := rfl

/-- Per-choice results unless an exception applies: RD-9's `xSem` with `Dflt_T` appended; conflict freedom is the
    strict one together with the gate. -/
def dSem (N : NDoc) : ChoiceSem :=
  { xSem.{u} N (fun c => defaultX (choiceSoft N c) (choiceX N c)) with
    free := fun c => (VE.Readings.Wire.sdSem.{u} N).free c ∧ DefaultCoherent.{u} (choiceU N c) (choiceSoft N c) []
    notFree := fun c => (VE.Readings.Wire.sdSem.{0} N).notFree c ∨
      ¬ DefaultCoherent.{0} (choiceU N c) (choiceSoft N c) [] }

theorem dSem_entails (N : NDoc) (c : Choice) (Γ : List VE.Formula) (φ : VE.Formula) :
    (dSem.{u} N).entails c Γ φ ↔
      VE.NormDefaults.EntailsX.{u} (choiceU N c) (defaultX (choiceSoft N c) (choiceX N c))
        ((choiceDoc N.D c).2 ++ Γ) φ := Iff.rfl

/-- RD-9's fold theorems apply to `dSem` as stated (one instance shown). -/
example (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (cs rs : List (Choice × ChoiceResult))
    (hr : RowsHoldG (dSem.{u} N) A Γ φ cs rs) (h : foldEntailment cs rs = .all) :
    ∀ c, (dSem.{u} N).compat c → (∀ x ∈ A, x ∈ c) → (dSem.{u} N).free c ∧ (dSem.{u} N).entails c Γ φ :=
  foldG_all_sound _ _ _ _ _ _ hr h

/-- With the strict conflict fold FREE, a default-fold CONFLICT comes from the gate only (DE7, never RD-9's
    contradiction wording). -/
theorem default_conflict_is_gate (N : NDoc) (A : Choice) (cs ds : List (Choice × ChoiceResult))
    (hcs : CoversG (VE.Readings.Wire.sdSem.{0} N) A cs)
    (hrs : ∀ x ∈ cs, HoldsG (VE.Readings.Wire.sdSem.{0} N) [] .bottom x.1 x.2)
    (hfree : foldConflict cs = .free)
    (hds : CoversG (dSem.{0} N) A ds) (hrd : ∀ x ∈ ds, HoldsG (dSem.{0} N) [] .bottom x.1 x.2)
    (hconf : foldConflict ds = .conflict) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ¬ DefaultCoherent.{0} (choiceU N c) (choiceSoft N c) [] := by
  obtain ⟨c, hc, hA, hn⟩ := foldG_conflict_sound _ _ _ hds hrd hconf
  have hf := foldG_conflict_free_sound _ _ _ hcs hrs hfree c hc hA
  refine ⟨c, hc, hA, ?_⟩
  rcases hn with hn | hn
  · exact absurd hf hn
  · exact hn

/-! ### One choice's evidence unless an exception applies -/

open VE.Readings.Wire
open VE.Norms (envAt)
open Lean (Json)
open VE.NormDefaults (UDoc fill)

/-- One choice's default evidence on its source `U`, `D`, `X` (plan 2.4): the gate's pair certificates and a collision
    (`defaults-coherence`), and the query's certificate, the model where its premises hold with `Dflt_T` and a
    countermodel with `Dflt_T` (`defaults-certificate`, `defaults-model`). -/
structure DEvidence (U : UDoc) (D : VE.SoftNorms.SoftDoc) (X : List VE.Formula) where
  wfc : VE.NormDefaults.WellFormedU U = true
  hU : U.D = VE.SoftNorms.soften D
  hD : VE.SoftNorms.WellFormedSoft D = true
  hl : VE.Compose.Labelled.wellLabelled (dfltLabelled D) = true
  hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []
  pairCerts : List (Option VE.Tableau.Certificate)
  collision : Option (VE.Defaults.Wire.Collision U)
  cert : Option VE.Tableau.Certificate
  model : Option (FilledModel U)
  counter : Option (FilledModel U)

variable {U : UDoc} {D : VE.SoftNorms.SoftDoc} {X : List VE.Formula}

/-- The gate checks: a certificate for every colliding pair (`R = []` on the soft chain). -/
def DEvidence.coherent (d : DEvidence U D X) : Bool := defaultCoherenceCheck U D [] d.pairCerts

/-- The gate fails: a checked collision. -/
def DEvidence.collides (d : DEvidence U D X) : Bool :=
  match d.collision with
  | some w => collisionCheck U D [] w.S.M w.F w.m w.n
  | none => false

/-- The query's pieces as RD-9's `XEvidence` over `defaultX D X`, for `xCertOk_sound` and `xModelOk_sound`. -/
def DEvidence.asX (d : DEvidence U D X) : XEvidence U (defaultX D X) :=
  ⟨d.wfc, fun a ha => (List.mem_append.mp ha).elim (d.hX a) (dflt_wellFormed U d.wfc D d.hU d.hD a),
    [], none, d.cert, d.counter, none, d.model⟩

/-- The default conflict row: CONFLICT-FREE with the strict packages and the gate; CONFLICT with a strict witness or
    a checked collision. -/
def dConflictRow (e : XEvidence U X) (d : DEvidence U D X) : ChoiceResult :=
  if xFree e && d.coherent then .free else if e.witness.isSome || d.collides then .conflict else .unknown

/-- `defaults-certificate`'s FOLLOWS on the choice: the certificate with `Dflt_T`, the strict packages, the gate and
    a model where the premises hold with `Dflt_T`. -/
def dFollows (e : XEvidence U X) (d : DEvidence U D X) (A Γ : List VE.Formula) (φ : VE.Formula) : Bool :=
  (d.cert.map (xCertOk U (defaultX D X) A Γ φ)).getD false && xFree e && d.coherent &&
    (d.model.map (xModelOk U (defaultX D X) A Γ .bottom · false)).getD false

/-- The default query row: `proved` on FOLLOWS, `refuted` with a checked countermodel with `Dflt_T`. -/
def dQueryRow (e : XEvidence U X) (d : DEvidence U D X) (A Γ : List VE.Formula) (φ : VE.Formula) : ChoiceResult :=
  if dFollows e d A Γ φ then .proved
  else if (d.counter.map (xModelOk U (defaultX D X) A Γ φ · false)).getD false then .refuted
  else .unknown

/-- A FOLLOWS choice's basis and kept assumptions: `defaults-certificate`'s, the strict countermodel being the strict
    evidence's own. -/
def dBasis (e : XEvidence U X) (d : DEvidence U D X) (A Γ : List VE.Formula) (φ : VE.Formula) :
    Option (Basis × List String) :=
  if dFollows e d A Γ φ then
    match d.cert with
    | some k =>
      let as := assumptionsOf U D X (A ++ Γ) φ k
      some (basisOf as ((e.counter.map (xModelOk U X A Γ φ · false)).getD false), as)
    | none => none
  else none

abbrev DChoice (N : NDoc) (c : Choice) : Type :=
  XEvidence (choiceU N c) (choiceX N c) × DEvidence (choiceU N c) (choiceSoft N c) (choiceX N c)

/-- DF-3's replay: RD-9's (`replayVerdictsSD`) and, per chosen choice, its strict and default evidence on the same
    `choiceLayeredG` source; the default rows and bases are computed from them. -/
structure DVerdicts where
  y : VE.Readings.Wire.SDVerdicts
  ds : List ((c : Choice) × DChoice y.r.N c)
  hds : ds.map (·.1) = chosenOf y.r.N.D y.x.A

def DVerdicts.dConflictRows (z : DVerdicts) : List (Choice × ChoiceResult) :=
  z.ds.map (fun d => (d.1, dConflictRow d.2.1 d.2.2))
def DVerdicts.dQueryRows (z : DVerdicts) : List (Choice × ChoiceResult) :=
  z.ds.map (fun d => (d.1, dQueryRow d.2.1 d.2.2 (choiceDoc z.y.r.N.D d.1).2 z.y.x.Γ z.y.x.φ))
def DVerdicts.bases (z : DVerdicts) : List (Choice × Basis × List String) :=
  z.ds.filterMap (fun d => (dBasis d.2.1 d.2.2 (choiceDoc z.y.r.N.D d.1).2 z.y.x.Γ z.y.x.φ).map
    (fun p => (d.1, p.1, p.2)))

/-- The `default` member: present only when the strict conflict fold is FREE; it carries the default conflict fold
    and the default fold. -/
def DVerdicts.defaultMember (z : DVerdicts) : Option (ChoiceResult × ReadingVerdict) :=
  if foldConflict z.y.x.conflictRows = .free then
    some (foldConflict z.dConflictRows, foldEntailment z.dConflictRows z.dQueryRows)
  else none

/-! ### The rows hold at `dSem` -/

theorem dConflictRow_holds {N : NDoc} {c : Choice} (e : XEvidence (choiceU N c) (choiceX N c))
    (d : DEvidence (choiceU N c) (choiceSoft N c) (choiceX N c)) :
    HoldsG (dSem.{u} N) [] .bottom c (dConflictRow e d) := by
  unfold dConflictRow
  split
  · rename_i h
    simp only [Bool.and_eq_true] at h
    exact ⟨xFree_sound e h.1, defaultCoherenceCheck_sound _ _ _ _ h.2⟩
  · split
    · rename_i h
      simp only [Bool.or_eq_true] at h
      rcases h with hw | hc
      · obtain ⟨⟨p⟩, _⟩ := Option.isSome_iff_exists.mp hw
        exact .inl p
      · refine .inr ?_
        unfold DEvidence.collides at hc
        split at hc
        · rename_i w _
          exact collision_sound _ d.wfc _ _ w.S.M w.S.valid w.F w.m w.n hc
        · cases hc
    · trivial

theorem dFollows_sound {N : NDoc} {c : Choice} {e : XEvidence (choiceU N c) (choiceX N c)}
    {d : DEvidence (choiceU N c) (choiceSoft N c) (choiceX N c)} {Γ : List VE.Formula} {φ : VE.Formula}
    (h : dFollows e d (choiceDoc N.D c).2 Γ φ = true) :
    ∃ k, d.cert = some k ∧ xCertOk (choiceU N c) (defaultX (choiceSoft N c) (choiceX N c)) (choiceDoc N.D c).2 Γ φ k
      = true ∧ (dSem.{u} N).free c := by
  simp only [dFollows, Bool.and_eq_true] at h
  obtain ⟨⟨⟨hk, hf⟩, hc⟩, _⟩ := h
  cases hd : d.cert with
  | none => rw [hd] at hk; cases hk
  | some k =>
    rw [hd] at hk
    exact ⟨k, rfl, hk, xFree_sound e hf, defaultCoherenceCheck_sound _ _ _ _ hc⟩

theorem dQueryRow_holds {N : NDoc} {c : Choice} (e : XEvidence (choiceU N c) (choiceX N c))
    (d : DEvidence (choiceU N c) (choiceSoft N c) (choiceX N c)) (Γ : List VE.Formula) (φ : VE.Formula) :
    HoldsG (dSem.{u} N) Γ φ c (dQueryRow e d (choiceDoc N.D c).2 Γ φ) := by
  unfold dQueryRow
  split
  · rename_i h
    obtain ⟨k, _, hk, hfree⟩ := dFollows_sound.{u} h
    exact ⟨hfree, xCertOk_sound d.asX _ Γ φ k hk⟩
  · split
    · rename_i _ hr
      cases hc : d.counter with
      | none => rw [hc] at hr; cases hr
      | some m =>
        rw [hc] at hr
        obtain ⟨S, h1, h2, h3, h4⟩ := xModelOk_sound d.asX _ Γ φ m false hr
        exact ⟨S, h1, h2, h3, fun hd => by simpa using h4.mp hd⟩
    · trivial

theorem DVerdicts.covers (z : DVerdicts) {rs : List (Choice × ChoiceResult)} (h : rs.map (·.1) = z.ds.map (·.1)) :
    CoversG (dSem.{u} z.y.r.N) z.y.x.A rs := fun c => by
  show (Compatible z.y.r.N.D c ∧ _) ↔ _
  rw [h, z.hds, mem_chosenOf _ (z.y.hN ▸ z.y.x.ready) (z.y.hN ▸ z.y.x.hle)]

/-- The default rows hold at `dSem`, and both lists are exactly the compatible choices taking `A`. -/
theorem d_rowsHold (z : DVerdicts) :
    RowsHoldG (dSem.{u} z.y.r.N) z.y.x.A z.y.x.Γ z.y.x.φ z.dConflictRows z.dQueryRows := by
  refine ⟨z.covers (by simp only [DVerdicts.dConflictRows, List.map_map, Function.comp_def]),
    z.covers (by simp only [DVerdicts.dQueryRows, List.map_map, Function.comp_def]), ?_, ?_⟩
  · intro y hy
    obtain ⟨d, _, rfl⟩ := mem_rowsG (E := DChoice z.y.r.N) (f := fun _ d => dConflictRow d.1 d.2) hy
    exact dConflictRow_holds d.2.1 d.2.2
  · intro y hy
    obtain ⟨d, _, rfl⟩ := mem_rowsG (E := DChoice z.y.r.N) (f := fun c d => dQueryRow d.1 d.2 (choiceDoc z.y.r.N.D c).2 z.y.x.Γ z.y.x.φ) hy
    exact dQueryRow_holds d.2.1 d.2.2 z.y.x.Γ z.y.x.φ

/-- Each listed basis is its choice's `defaults_certificate_sound` basis. -/
theorem d_bases_sound (z : DVerdicts) :
    ∀ c b as, (c, b, as) ∈ z.bases →
      VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c)
        (choiceX z.y.r.N c ++ blank (dfltLabelled (choiceSoft z.y.r.N c)) as)
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ ∧
      (b = .strict → VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c) (choiceX z.y.r.N c)
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) ∧
      (b = .needs → CounterX (choiceU z.y.r.N c) (choiceX z.y.r.N c) ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) := by
  intro c b as hm
  obtain ⟨d, _, hd⟩ := List.mem_filterMap.mp hm
  obtain ⟨p, hp, he⟩ := Option.map_eq_some_iff.mp hd
  simp only [Prod.mk.injEq] at he
  obtain ⟨rfl, rfl, rfl⟩ := he
  obtain ⟨c, e, dv⟩ := d
  unfold dBasis at hp
  split at hp
  · rename_i hf
    obtain ⟨k, hk, hck, _⟩ := dFollows_sound.{u} hf
    rw [hk] at hp
    cases hp
    refine ⟨assumptions_sound _ dv.wfc _ dv.hU dv.hD dv.hl _ _ dv.hX _ k hck,
      fun hb => basis_strict_sound _ dv.wfc _ dv.hU dv.hD dv.hl _ _ dv.hX _ k hck _ hb, fun hb => ?_⟩
    have hs : ((e.counter.map (xModelOk (choiceU z.y.r.N c) (choiceX z.y.r.N c) (choiceDoc z.y.r.N.D c).2 z.y.x.Γ z.y.x.φ · false)).getD false) = true := by
      unfold basisOf at hb
      split at hb
      · cases hb
      · split at hb
        · assumption
        · cases hb
    cases hm' : e.counter with
    | none => rw [hm'] at hs; cases hs
    | some m =>
      rw [hm'] at hs
      exact (basis_needs_sound _ dv.wfc _ _ _ m hs).1
  · cases hp

/-! ### What the member shows agrees with its rows -/

theorem dBasis_proved {e : XEvidence U X} {d : DEvidence U D X} {A Γ : List VE.Formula} {φ : VE.Formula}
    {p : Basis × List String} (h : dBasis e d A Γ φ = some p) : dQueryRow e d A Γ φ = .proved := by
  unfold dBasis at h
  unfold dQueryRow
  split at h
  · rw [if_pos (by assumption)]
  · cases h

/-- A checked collision is never beside a checked gate (`collision_sound`, `defaultCoherenceCheck_sound`), so its row
    is CONFLICT. -/
theorem collides_conflict (e : XEvidence U X) (d : DEvidence U D X) (h : d.collides = true) :
    dConflictRow e d = .conflict := by
  have hn : d.coherent = false := by
    cases hc : d.coherent with
    | false => rfl
    | true =>
      exfalso
      have hd := defaultCoherenceCheck_sound.{0} U D [] d.pairCerts hc
      unfold DEvidence.collides at h
      split at h
      · rename_i w _
        exact collision_sound _ d.wfc _ _ w.S.M w.S.valid w.F w.m w.n h hd
      · cases h
  unfold dConflictRow
  rw [hn, Bool.and_false, if_neg (by decide), h, Bool.or_true, if_pos rfl]

/-! ### The replay -/

/-- Both branches of `choiceLayeredG` take the choice's soft document as the source's. -/
theorem choiceLayeredG_D (b : Admitted2) (N : NDoc) (c : Choice) (wfc : VE.NormDefaults.WellFormedU (choiceU N c) = true)
    (hN : N.D = b.D) (L : {L : VE.NormDefaults.Wire.LayeredU // L.U = choiceU N c ∧ L.X = choiceX N c ∧
      ∀ a ∈ L.X, a.WellFormed (envAt (VE.NormDefaults.fill L.U) 0) []})
    (h : choiceLayeredG b N c wfc hN = .ok L) : L.1.D = choiceSoft N c := by
  unfold choiceLayeredG at h
  dsimp only at h
  by_cases hn : normsShaped N.D = true
  · rw [dif_pos hn] at h
    repeat (obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h)
    cases h
    rfl
  · rw [dif_neg hn] at h
    split at h
    · split at h
      · split at h
        · repeat (obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h)
          cases h
          rfl
        · cases h
      · cases h
    · cases h

/-- A choice's default evidence (the request's `default` member of its evidence entry), decoded by `defaults-*`'s own
    view and pieces on the choice's `choiceLayeredG` source: the view's checks (`viewOn`), the pair certificates
    (`pairCertsOf`), the collision (`collisionOf`), the certificate bound to `premisesX U (defaultX D X) A` and the
    request's own premises (`bindCertX`, absent when it does not bind) and the two models (`filledOf`). -/
def dEvidenceOf (r : AdmittedSD) (j : Json) (c : Choice) (e : Json) :
    Except String (DEvidence (choiceU r.N c) (choiceSoft r.N c) (choiceX r.N c)) :=
  match ht : sdChoiceText r.b.a.re r.N c with
  | some err => .error err
  | none =>
    have hw : VE.NormDefaults.WellFormedU (choiceU r.N c) = true :=
      wellFormedU_of_ndDocTextG (Option.map_eq_none_iff.mp (option_or_none ht).2)
    match hL : choiceLayeredG r.b r.N c hw r.hN with
    | .error err => .error err
    | .ok L =>
      have hD := choiceLayeredG_D r.b r.N c hw r.hN L hL
      match hv : VE.Defaults.Wire.viewOn j L.1 (by rw [L.2.1, hD]; rfl) with
      | .error err => .error err
      | .ok v =>
        have hvL := VE.Defaults.Wire.viewOn_L hv
        have hU : v.L.U = choiceU r.N c := hvL ▸ L.2.1
        have hS : v.L.D = choiceSoft r.N c := hvL ▸ hD
        have hX : v.L.X = choiceX r.N c := hvL ▸ L.2.2.1
        let lower := r.b.a.re.lowerJson
        let d := e.getObjValD "default"
        let own := match j.getObjValD "premises" with | .arr xs => xs.toList | _ => []
        let A := (choiceDoc r.N.D c).2
        match VE.Defaults.Wire.pairCertsOf lower v d, VE.Defaults.Wire.pieceWith d "collision" (VE.Defaults.Wire.collisionOf v.L),
          VE.Defaults.Wire.pieceWith d "model" (VE.Defaults.Wire.filledOf v.L),
          VE.Defaults.Wire.pieceWith d "countermodel" (VE.Defaults.Wire.filledOf v.L) with
        | .ok pcs, .ok col, .ok m, .ok cm =>
          let cert := (pieceOf d "certificate").bind fun cj => (VE.NormDefaults.Wire.bindCertX lower v.L.U
            (defaultX v.L.D v.L.X) A own (j.getObjValD "conclusion") (cj.getObjValD "certificate")).toOption
          let ev : DEvidence v.L.U v.L.D v.L.X := ⟨v.L.wfU, v.hU, v.hD, v.hl, v.hXw, pcs, col, cert, m, cm⟩
          .ok (hU ▸ hS ▸ hX ▸ ev)
        | .error err, _, _, _ | _, .error err, _, _ | _, _, .error err, _ | _, _, _, .error err => .error err

/-- DF-3's replay on RD-9's: each chosen choice's strict evidence (`sdEvidenceOf`, as `replaySD` decodes it) and its
    default evidence (`dEvidenceOf`), in `chosenOf` order. -/
def replayD (y : VE.Readings.Wire.SDVerdicts) (j : Json) : Except String DVerdicts := do
  let evidence := VE.Readings.Run.evidenceList j
  let premisesJ := match j.getObjValD "premises" with | .null => Json.arr #[] | p => p
  let ps ← VE.Readings.Wire.mapSigma (β := DChoice y.r.N) (chosenOf y.r.N.D y.x.A) (fun c _ => do
    let e := VE.Readings.Run.entryFor evidence c
    let (strict, _) ← sdEvidenceOf y.r c e premisesJ (j.getObjValD "conclusion") y.x.Γ y.x.φ
    pure (strict, ← dEvidenceOf y.r j c e))
  pure ⟨y, ps.1, ps.2⟩

def replayVerdictsD (j : Lean.Json) : Except String DVerdicts := do
  replayD (← VE.Readings.Wire.replayVerdictsSD j) j

/-! ### The wire theorems (spec 7.4) -/

theorem readings_wire_default_present (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (m : ChoiceResult × ReadingVerdict) (hm : z.defaultMember = some m) :
    foldConflict z.y.x.conflictRows = .free := by
  have _ := h
  unfold DVerdicts.defaultMember at hm
  split at hm
  · assumption
  · cases hm

theorem readings_wire_default_verdicts_all (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldEntailment z.dConflictRows z.dQueryRows = .all) :
    ∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) →
      (dSem.{u} z.y.r.N).free c ∧
      VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ := by
  have _ := h
  exact foldG_all_sound _ _ _ _ _ _ (d_rowsHold z) hv

theorem readings_wire_default_verdicts_none (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldEntailment z.dConflictRows z.dQueryRows = .none) :
    ∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) →
      (dSem.{u} z.y.r.N).free c ∧
      CounterX (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ := by
  have _ := h
  exact foldG_none_sound _ _ _ _ _ _ (d_rowsHold.{u} z) hv

theorem readings_wire_default_verdicts_some (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldEntailment z.dConflictRows z.dQueryRows = .some) :
    (∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) → (dSem.{u} z.y.r.N).free c) ∧
    (∃ c, Compatible z.y.r.N.D c ∧ (∀ x ∈ z.y.x.A, x ∈ c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) ∧
    (∃ c, Compatible z.y.r.N.D c ∧ (∀ x ∈ z.y.x.A, x ∈ c) ∧
      CounterX (choiceU z.y.r.N c) (defaultX (choiceSoft z.y.r.N c) (choiceX z.y.r.N c))
        ((choiceDoc z.y.r.N.D c).2 ++ z.y.x.Γ) z.y.x.φ) := by
  have _ := h
  exact foldG_some_sound _ _ _ _ _ _ (d_rowsHold z) hv

theorem readings_wire_default_conflict_free (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (hv : foldConflict z.dConflictRows = .free) :
    ∀ c, Compatible z.y.r.N.D c → (∀ x ∈ z.y.x.A, x ∈ c) → (dSem.{u} z.y.r.N).free c := by
  have _ := h
  obtain ⟨hc, _, hr, _⟩ := d_rowsHold.{u} z
  exact foldG_conflict_free_sound _ _ _ hc hr hv

/-- A present member with a default-fold CONFLICT names a choice whose gate fails (DE7 for that choice). -/
theorem readings_wire_default_conflict (j : Lean.Json) (z : DVerdicts) (h : replayVerdictsD j = .ok z)
    (r : ReadingVerdict) (hm : z.defaultMember = some (.conflict, r)) :
    ∃ c, Compatible z.y.r.N.D c ∧ (∀ x ∈ z.y.x.A, x ∈ c) ∧
      ¬ DefaultCoherent.{0} (choiceU z.y.r.N c) (choiceSoft z.y.r.N c) [] := by
  have hfree := readings_wire_default_present j z h _ hm
  have hconf : foldConflict z.dConflictRows = .conflict := by
    unfold DVerdicts.defaultMember at hm
    rw [if_pos hfree] at hm
    simp only [Option.some.injEq, Prod.mk.injEq] at hm
    exact hm.1
  obtain ⟨hcs, _, hrs, _⟩ := VE.Readings.Wire.sd_rowsHold.{0} z.y
  obtain ⟨hds, _, hrd, _⟩ := d_rowsHold.{0} z
  exact default_conflict_is_gate _ _ _ _ hcs hrs hfree hds hrd hconf

end VE.Readings

/-! ### The `default` member of `readings-verdicts` (plan 2.4) -/

namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire

def verdictWord : ReadingVerdict → String
  | .all => "ALL" | .some => "SOME" | .none => "NONE" | .unknown => "UNKNOWN"

/-- One choice's default rows; with FOLLOWS its basis and kept assumptions, with a checked collision the pair, the
    tuple, DE7's deciders and the situation (`collisionFields`). -/
def dChoiceJson (z : DVerdicts) (d : (c : Choice) × DChoice z.y.r.N c) : Json :=
  let A := (choiceDoc z.y.r.N.D d.1).2
  Json.mkObj ([("choice", choiceJson d.1), ("conflict", .str (word (dConflictRow d.2.1 d.2.2))),
      ("query", .str (word (dQueryRow d.2.1 d.2.2 A z.y.x.Γ z.y.x.φ)))] ++
    (match dBasis d.2.1 d.2.2 A z.y.x.Γ z.y.x.φ with
     | some p => [("basis", .str (VE.Defaults.Wire.basisLabel p.1)), ("assumptions", toJson p.2)]
     | none => []) ++
    (match d.2.2.collision, d.2.2.collides with
     | some w, true => VE.Defaults.Wire.collisionFields (choiceU z.y.r.N d.1) (choiceSoft z.y.r.N d.1) w
     | _, _ => []))

/-- One English row of the member: DE8, or a row of one choice. -/
inductive DLine | de8 | de7 (c : Choice) | assumptions (c : Choice) | de12 (c : Choice)

def DLine.json : DLine → Json
  | .de8 => Json.mkObj [("row", .str "DE8")]
  | .de7 c => Json.mkObj [("row", .str "DE7"), ("choice", choiceJson c)]
  | .assumptions c => Json.mkObj [("row", .str "assumptions"), ("choice", choiceJson c)]
  | .de12 c => Json.mkObj [("row", .str "DE12"), ("choice", choiceJson c)]

/-- The member's English rows, Lean's selection (spec 7.4): with the default conflict fold CONFLICT, DE7 for each
    choice whose gate fails; with the default fold ALL and some reading not `strict`, DE8, then each such reading's
    assumption sentences and, for an `unsettled` one, DE12; otherwise none. -/
def dEnglish (z : DVerdicts) : List DLine :=
  if foldConflict z.dConflictRows == .conflict then
    z.ds.filterMap (fun d => if d.2.2.collides then some (.de7 d.1) else none)
  else if foldEntailment z.dConflictRows z.dQueryRows == .all && z.bases.any (·.2.1 != .strict) then
    .de8 :: z.bases.flatMap (fun p =>
      if p.2.1 == .strict then [] else .assumptions p.1 :: if p.2.1 == .unsettled then [.de12 p.1] else [])
  else []

/-- The member: the default conflict fold and the default fold (`DVerdicts.defaultMember`'s pair), each choice's rows
    and the English rows. -/
def defaultJson (z : DVerdicts) : Json :=
  Json.mkObj [("conflict", .str (word (foldConflict z.dConflictRows))),
    ("verdict", .str (verdictWord (foldEntailment z.dConflictRows z.dQueryRows))),
    ("per_choice", Json.arr (z.ds.map (dChoiceJson z)).toArray),
    ("english", Json.arr ((dEnglish z).map DLine.json).toArray)]

def askedText : String := "InvalidInput: assume_no_exception is true or false, and applies to the query question"

/-- RD-9's `readings-verdicts` under the soft completion (`runVerdictsSD`); when the request asks
    (`assume_no_exception: true`, the query question, at most 64 compatible choices), RD-9's answer on the same replay
    (`replaySD`, `ndVerdictsAnswer`) with the `default` member beside it, present only when the strict conflict fold is
    FREE (`DVerdicts.defaultMember`). -/
def runVerdictsD (id : String) (b : Admitted2) (j : Json) : Except String Json := do
  match j.getObjValD "assume_no_exception" with
  | .null | .bool false => runVerdictsSD id b j
  | .bool true =>
    let q ← verdictsRequest b j
    if q.question = "query" then
      let r ← admitSDOf b
      if (choices r.N.D).isEmpty then throw (unsatText r.N.D)
      if (choices r.N.D).length ≤ maxChoices then
        let y ← replaySD r "query" q.A j
        let z ← replayD y j
        let a := ndVerdictsAnswer id "query" (j.getObjValD "document") r.N.D q.A q.named (some (xInfos y.x)) []
          q.dead
        pure (match z.defaultMember with
          | some _ => a.setObjVal! "default" (defaultJson z)
          | none => a)
      else throw "UnsupportedProfile: answers that assume no exception take at most 64 compatible readings"
    else throw askedText
  | _ => throw askedText

end VE.Readings.Run
