import VE.Alternatives.Replay
import VE.NormDefaults.Replay

/-! `alternatives@0` with the completion (docs/spec/events-time-causation.md 5 and 6.4, ET-7): the
alternatives route on `fill (inlineTree A)` under `norm-defaults@0`.

`decodeAltSourceU` has `decodeSourceU`'s two branches (SR-A2): without the profile an `unspecified` default
is refused and today's decoder runs unchanged (`decodeAltSourceU_conservative`); with it, today's gate on the
original profile list, the placeholders, today's decoder, then nd 8's reserved names and limits and
`WellFormedU`. CONFLICT-FREE is over `BaseAdmissibleAltU`, the slot premises included (SR-A3); FOLLOWABLE is a
certificate over `Background_baseAlt(E‴) ++ Fill_T ++ Γ` (`alternativesU_wire_followable_sound`); DILEMMA is a
validated witness, a filling validated by `fillValid` and a typed chooser
(`alternativesU_dilemma_witness_sound`, which assumes `WellFormedAlt`: SR-A1).

Packages are bound as on today's route (3.5), with the identity of the complete environment (profile and
`unspecified` values included) and the inner certificate bound to `E‴_base`: the block-free W1 view of the
environment with the placeholders, the regulated predicates and the profiles removed, and one `unsaid__p` per
unspecified `p`. `unsettledAt`, which names the alternatives two validated fillings answer both ways, is the
untrusted diagnosis's. -/
namespace VE.Alternatives
open Lean
open VE.Norms
open VE.NormDefaults (UDoc fill WellFormedU BaseAdmissibleU BaseAdmissibleAltU backgroundBaseAltU allFollowableU
  followableFU clearFU FiniteFill fillValid fillPremises finFill)
open VE.NormDefaults.Wire (hasProfile unspecifiedNames placeholderJson checkAuthor profilesOf)
universe u

structure AltSourceU where
  src : Wire.AltSource
  unspec : List String          -- the regulated predicates whose `default` is "unspecified", in regulated order

/-- The filled document's author side. -/
def AltSourceU.U (s : AltSourceU) : UDoc := ⟨inlineTree s.src.A, s.unspec⟩

/-- `decodeSourceU`'s two branches (SR-A2). -/
def decodeAltSourceU (environment norms premises : Json) (scope : Wire.Scope := .document) :
    Except String AltSourceU :=
  if hasProfile environment then do
    let _ ← Wire.profileGate environment
    let src ← Wire.decodeAltSource (← placeholderJson environment) norms premises scope
    let unspec := (src.A.T.regulated.map (·.name)).filter ((unspecifiedNames environment).contains ·)
    checkAuthor environment ⟨inlineTree src.A, unspec⟩
    unless WellFormedU ⟨inlineTree src.A, unspec⟩ do
      throw "InvalidInput: norm-defaults document is not well formed"
    pure ⟨src, unspec⟩
  else do
    unless (unspecifiedNames environment).isEmpty do
      throw "UnsupportedProfile: unspecified completion requires norm-defaults@0"
    let src ← Wire.decodeAltSource environment norms premises scope
    pure ⟨src, []⟩

def noUnspecified (environment : Json) : Bool :=
  !hasProfile environment && (unspecifiedNames environment).isEmpty

def notFollowableFU (A : AltDoc) (unspec : List String) : VE.Formula := .not (followableFU A unspec)

/-- No `unspecified` value and no `norm-defaults@0`: today's decoder, texts included. -/
theorem decodeAltSourceU_conservative (environment norms premises : Json)
    (h : noUnspecified environment = true) :
    decodeAltSourceU environment norms premises =
      (Wire.decodeAltSource environment norms premises).map (fun s => AltSourceU.mk s []) := by
  simp only [noUnspecified, Bool.and_eq_true, Bool.not_eq_true'] at h
  unfold decodeAltSourceU
  simp only [h.1, Bool.false_eq_true, if_false, h.2]
  cases Wire.decodeAltSource environment norms premises <;> rfl

/-- Conflict freedom over the route's own base, the slot premises included (SR-A3). -/
def AltConflictFreeU (A : AltDoc) (unspec : List String) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleAltU A unspec B → VE.Norms.ConflictFree (fill ⟨inlineTree A, unspec⟩) B

/-! ## CONFLICT-FREE -/

/-- One target's certificate over `Background_baseAlt(E‴) ++ Fill_T`, or over `Background_base(E‴) ++ Fill_T`
(fewer premises, as `targetAccepted`). -/
def targetAcceptedU (A : AltDoc) (unspec : List String) (t : String × List String × VE.Formula)
    (c : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill ⟨inlineTree A, unspec⟩) 0) (backgroundBaseAltU A unspec)
      (targetConclusion t) c ||
    VE.Tableau.checkCertificate (envAt (fill ⟨inlineTree A, unspec⟩) 0)
      (VE.NormDefaults.Wire.baseBackgroundU ⟨inlineTree A, unspec⟩) (targetConclusion t) c

/-- Every target of `fill (inlineTree A)` has an accepted certificate, in target order. -/
def altConflictFreeCheckU (A : AltDoc) (unspec : List String) (certs : List (Option VE.Tableau.Certificate)) :
    Bool :=
  (targets (fill ⟨inlineTree A, unspec⟩)).length == certs.length &&
    ((targets (fill ⟨inlineTree A, unspec⟩)).zip certs).all (fun (t, c) => match c with
      | some c => targetAcceptedU A unspec t c
      | none => false)

theorem zip_all_target {β : Type} {ts : List β} {cs : List (Option VE.Tableau.Certificate)}
    {f : β → VE.Tableau.Certificate → Bool}
    (hc : (ts.length == cs.length && (ts.zip cs).all (fun (t, c) => match c with
      | some c => f t c
      | none => false)) = true) {t : β} (ht : t ∈ ts) : ∃ c, f t c = true := by
  simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < ts.length := (List.getElem?_eq_some_iff.mp hi).1
  have hmem : (t, cs[i]'(hl ▸ hlt)) ∈ ts.zip cs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem _⟩
  have := hall _ hmem
  revert this
  cases cs[i]'(hl ▸ hlt) with
  | none => intro h; cases h
  | some c => intro h; exact ⟨c, h⟩

theorem alt_conflict_freeU (A : AltDoc) (unspec : List String) (h : WellFormedU ⟨inlineTree A, unspec⟩ = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : altConflictFreeCheckU A unspec certs = true) :
    AltConflictFreeU.{u} A unspec := by
  have hv := valid_of_wellFormed _ (VE.NormDefaults.fill_wellFormed _ h)
  intro B hB
  have cert : ∀ t ∈ targets (fill ⟨inlineTree A, unspec⟩), ∀ vs, VE.TupleTyped B t.2.1 vs →
      ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    obtain ⟨c, hcc⟩ := zip_all_target hc ht
    have he : (targetConclusion t).denote B [] := by
      rcases Bool.or_eq_true_iff.mp hcc with hcc | hcc
      · refine VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1.1 fun a ha => ?_
        simp only [backgroundBaseAltU, List.mem_append] at ha
        rcases ha with (ha | ha) | ha
        · exact hB.1.1.2 a ha
        · exact hB.2 a ha
        · exact hB.1.2 a ha
      · refine VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1.1 fun a ha => ?_
        rcases List.mem_append.mp ha with ha | ha
        · exact hB.1.1.2 a ha
        · exact hB.1.2 a ha
    exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact cert _ (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact cert _ (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-! ## Bindings and replays -/

/-- `E‴_base` of an alternatives source with the completion. -/
def baseEnvironmentJsonAltU (environment : Json) (s : AltSourceU) : Except String Json := do
  VE.NormDefaults.Wire.baseEnvironmentJsonU (← Wire.normsView environment (profilesOf environment)) s.U

/-- One package bound to the complete environment and to `E‴_base`. -/
def decodePackageU (s : AltSourceU) (environment norms units package : Json) (target : String)
    (premises : List VE.Formula) (conclusion : VE.Formula) : Option VE.Tableau.Certificate :=
  Replay.decodePackageAt (baseEnvironmentJsonAltU environment s) (profilesOf environment) environment norms units
    package target premises conclusion

def conflictCertsU (s : AltSourceU) (environment norms units packages : Json) :
    List (Option VE.Tableau.Certificate) :=
  (targets (fill s.U)).map fun t =>
    decodePackageU s environment norms units (packages.getObjValD t.1) t.1 (backgroundBaseAltU s.src.A s.unspec)
      (targetConclusion t) <|>
    decodePackageU s environment norms units (packages.getObjValD t.1) t.1
      (VE.NormDefaults.Wire.baseBackgroundU s.U) (targetConclusion t)

def sourceOfU (j : Json) : Except String AltSourceU := do
  let environment ← j.getObjVal? "environment"
  decodeAltSourceU environment (j.getObjValD "norms") (j.getObjValD "units")

theorem sourceOfU_ok {j : Json} {s : AltSourceU} (h : sourceOfU j = .ok s) :
    decodeAltSourceU (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok s := by
  unfold sourceOfU at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  rw [he]; exact h

structure AltConflictReplayU where
  src : AltSourceU
  certs : List (Option VE.Tableau.Certificate)

def AltConflictReplayU.conflictFree (r : AltConflictReplayU) : Bool :=
  WellFormedU r.src.U && altConflictFreeCheckU r.src.src.A r.src.unspec r.certs

def replayAltConflictU (j : Json) : Except String AltConflictReplayU := do
  let s ← sourceOfU j
  pure ⟨s, conflictCertsU s (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units")
    (j.getObjValD "packages")⟩

theorem alternativesU_wire_conflict_sound (j : Json) (res : AltConflictReplayU) (h : replayAltConflictU j = .ok res)
    (hv : res.conflictFree = true) :
    decodeAltSourceU (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok res.src ∧
      WellFormedU ⟨inlineTree res.src.src.A, res.src.unspec⟩ = true ∧ AltConflictFreeU.{u} res.src.src.A res.src.unspec := by
  unfold replayAltConflictU at h
  obtain ⟨s, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [AltConflictReplayU.conflictFree, Bool.and_eq_true] at hv
  exact ⟨sourceOfU_ok hs, hv.1, alt_conflict_freeU _ _ hv.1 _ hv.2⟩

/-- The first target without an accepted certificate. -/
def firstFailureU (r : AltConflictReplayU) : String :=
  match ((targets (fill r.src.U)).zip r.certs).find? (fun (t, c) => match c with
      | some c => !targetAcceptedU r.src.src.A r.src.unspec t c
      | none => true) with
  | some (t, some _) => s!"invalid certificate for {t.1}"
  | some (t, none) => s!"missing certificate for {t.1}"
  | none => "InvalidInput: norm-defaults document is not well formed"

/-! ## FOLLOWABLE -/

structure FollowableUReplay where
  src : AltSourceU
  certs : List (Option VE.Tableau.Certificate)
  cert : Option VE.Tableau.Certificate

def FollowableUReplay.conflictFree (r : FollowableUReplay) : Bool :=
  WellFormedU r.src.U && altConflictFreeCheckU r.src.src.A r.src.unspec r.certs

/-- CONFLICT-FREE first, then the certificate, as `FollowableReplay.followable`. -/
def FollowableUReplay.followable (r : FollowableUReplay) : Bool :=
  r.conflictFree && match r.cert with
    | some c => VE.Tableau.checkCertificate (envAt (fill r.src.U) 0)
        (backgroundBaseAltU r.src.src.A r.src.unspec ++ r.src.src.A.Γ) (allFollowableU r.src.src.A r.src.unspec) c
    | none => false

def replayFollowableU (j : Json) : Except String FollowableUReplay := do
  let s ← sourceOfU j
  let environment := j.getObjValD "environment"
  let norms := j.getObjValD "norms"
  let units := j.getObjValD "units"
  pure ⟨s, conflictCertsU s environment norms units (j.getObjValD "packages"),
    decodePackageU s environment norms units (j.getObjValD "package") "followable"
      (backgroundBaseAltU s.src.A s.unspec ++ s.src.A.Γ) (allFollowableU s.src.A s.unspec)⟩

/-- FOLLOWABLE on the wire, with the completion. -/
theorem alternativesU_wire_followable_sound (j : Json) (res : FollowableUReplay)
    (h : replayFollowableU j = .ok res) (hv : res.followable = true) :
    decodeAltSourceU (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok res.src ∧
    WellFormedU ⟨inlineTree res.src.src.A, res.src.unspec⟩ = true ∧
    AltConflictFreeU.{u} res.src.src.A res.src.unspec ∧
    ∀ B : VE.Structure.{u}, BaseAdmissibleAltU res.src.src.A res.src.unspec B → Sat B res.src.src.A.Γ →
      (allFollowableU res.src.src.A res.src.unspec).denote B [] := by
  unfold replayFollowableU at h
  obtain ⟨s, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [FollowableUReplay.followable, FollowableUReplay.conflictFree, Bool.and_eq_true] at hv
  obtain ⟨⟨hw, hc⟩, hf⟩ := hv
  refine ⟨sourceOfU_ok hs, hw, alt_conflict_freeU _ _ hw _ hc, ?_⟩
  revert hf
  split
  · intro hf B hB hΓ
    refine VE.Tableau.checkCertificate_sound.{u} _ _ _ _ hf B hB.1.1.1 fun a ha => ?_
    simp only [backgroundBaseAltU, List.mem_append] at ha
    rcases ha with ((ha | ha) | ha) | ha
    · exact hB.1.1.2 a ha
    · exact hB.2 a ha
    · exact hB.1.2 a ha
    · exact hΓ a ha
  · intro hf; cases hf

/-! ## DILEMMA -/

/-- A formula over the base vocabulary keeps its value when a filling is added. -/
theorem denote_withFill_base (A : AltDoc) (unspec : List String) (h : WellFormedU ⟨inlineTree A, unspec⟩ = true)
    (B : VE.Structure.{u}) (F : VE.NormDefaults.FillTables ⟨inlineTree A, unspec⟩ B) (φ : VE.Formula)
    (hφ : φ.WellFormed (envAt (inlineTree A) 0) []) :
    φ.denote (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ B F) [] ↔ φ.denote B [] :=
  VE.Norms.denote_relation_congr (VE.NormDefaults.unsaid_undeclared (VE.NormDefaults.uvalid h) 0) B _
    (fun _ vs hn => VE.NormDefaults.withFill_agrees B F _ hn vs) φ [] [] hφ

/-- A filling validated on a valid situation is admissible on the route's base, the slot premises included: no
statement over the admissible fillings of a validated scenario is vacuous (SR-A1, SR-A4). -/
theorem admissibleAltU_of_fillValid {α : Type u} [DecidableEq α] (A : AltDoc) (unspec : List String)
    (hA : WellFormedAlt A = true) (h : WellFormedU ⟨inlineTree A, unspec⟩ = true) (M : VE.FiniteModel α)
    (valid : M.Valid (VE.Norms.envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
    (F : FiniteFill ⟨inlineTree A, unspec⟩ α) (hfill : fillValid ⟨inlineTree A, unspec⟩ M F = true) :
    BaseAdmissibleAltU A unspec (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ M.asStructure (finFill M F)) := by
  have hv := altValid_of_wellFormed A hA
  have hbase := baseAdmissibleAlt_of_valid A M valid hb
  refine ⟨?_, fun a ha => (denote_withFill_base A unspec h _ _ a (altPremises_wellFormed hv a ha)).mpr (hbase.2 a ha)⟩
  simp only [backgroundValidAlt, Bool.and_eq_true] at hb
  exact VE.NormDefaults.admissible_of_fillValid _ h M valid hb.1 F hfill

/-- DILEMMA: a valid witness, a validated filling and a typed chooser at which ¬followable° holds refute the
document-wide claim. `hA` types Γ over the base vocabulary, which declares no unsaid predicate (SR-A1). -/
theorem alternativesU_dilemma_witness_sound {α : Type u} [DecidableEq α] (A : AltDoc) (unspec : List String)
    (hA : WellFormedAlt A = true) (h : WellFormedU ⟨inlineTree A, unspec⟩ = true) (M : VE.FiniteModel α)
    (F : FiniteFill ⟨inlineTree A, unspec⟩ α) (valid : M.Valid (VE.Norms.envAt (inlineTree A) 0))
    (hb : backgroundValidAlt A M = true) (hfill : fillValid ⟨inlineTree A, unspec⟩ M F = true)
    (hΓ : A.Γ.all (fun p => p.eval M []) = true) (r : α) (typed : r ∈ M.domains A.alt.chooser)
    (hd : (notFollowableFU A unspec).eval (M.withFill F) (VE.Norms.tupleVal [r]) = true) :
    ¬ (∀ B : VE.Structure.{u}, BaseAdmissibleAltU A unspec B → VE.Norms.Sat B A.Γ →
        (allFollowableU A unspec).denote B []) := by
  have hv := altValid_of_wellFormed A hA
  have hG : Sat (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ M.asStructure (finFill M F)) A.Γ := fun a ha =>
    (denote_withFill_base A unspec h _ _ a (hv.premises a ha)).mpr
      ((VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp hΓ a ha))
  intro hall
  have hF' := (bindAll_denote_nil _ _ _).mp
    (hall _ (admissibleAltU_of_fillValid A unspec hA h M valid hb F hfill) hG) [r] ⟨typed, trivial⟩
  exact ((VE.NormDefaults.eval_withFill _ M F _ _).mp hd) hF'

structure DilemmaDataU (s : AltSourceU) where
  certs : List (Option VE.Tableau.Certificate)
  sc : Replay.Scenario s.src
  F : FiniteFill s.U VE.Bridge.Entity
  r : VE.Bridge.Entity

def DilemmaDataU.dilemma {s : AltSourceU} (w : DilemmaDataU s) : Bool :=
  WellFormedU s.U && altConflictFreeCheckU s.src.A s.unspec w.certs && altModelChecks s.src.A w.sc.M w.sc.rows &&
    (w.sc.M.domains s.src.A.alt.chooser).contains w.r && fillValid s.U w.sc.M w.F &&
    (notFollowableFU s.src.A s.unspec).eval (w.sc.M.withFill w.F) (tupleVal [w.r])

def replayDilemmaU (j : Json) : Except String ((s : AltSourceU) × DilemmaDataU s) := do
  let s ← sourceOfU j
  let w ← j.getObjVal? "witness"
  let sc ← Replay.decodeScenario s.src w
  let r ← Replay.entity sc.M s.src.A.alt.chooser (← VE.Bridge.stringField w "chooser")
  let F ← VE.NormDefaults.Wire.decodeFilling s.U sc.M (← w.getObjVal? "filling")
  pure ⟨s, ⟨conflictCertsU s (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units")
    (j.getObjValD "packages"), sc, F, r⟩⟩

/-- DILEMMA from raw JSON: the source decodes, is well-formed and conflict-free, the witness passes today's
validation with its rows, the filling is validated, the chooser is typed, and the document-wide claim is
refuted. -/
theorem alternativesU_wire_dilemma_sound (j : Json) (s : AltSourceU) (w : DilemmaDataU s)
    (h : replayDilemmaU j = .ok ⟨s, w⟩) (hw : w.dilemma = true) :
    decodeAltSourceU (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok s ∧
      WellFormedAlt s.src.A = true ∧ WellFormedU s.U = true ∧ AltConflictFreeU.{0} s.src.A s.unspec ∧
      validateAlternatives s.src.A w.sc.M w.sc.rows = .ok () ∧ fillValid s.U w.sc.M w.F = true ∧
      ¬ (∀ B : VE.Structure.{0}, BaseAdmissibleAltU s.src.A s.unspec B → Sat B s.src.A.Γ →
        (allFollowableU s.src.A s.unspec).denote B []) := by
  have hdec : decodeAltSourceU (j.getObjValD "environment") (j.getObjValD "norms") (j.getObjValD "units") = .ok s := by
    unfold replayDilemmaU at h
    obtain ⟨s', hs, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    cases h
    exact sourceOfU_ok hs
  simp only [DilemmaDataU.dilemma, Bool.and_eq_true, List.contains_iff_mem] at hw
  obtain ⟨⟨⟨⟨⟨hU, hc⟩, hm⟩, hr⟩, hf⟩, hd⟩ := hw
  have hval : validateAlternatives s.src.A w.sc.M w.sc.rows = .ok () := validateAlternativesWith_ok.mpr hm
  obtain ⟨valid, hb, hΓ, _, _⟩ := Replay.validate_sound_decoded s.src w.sc hval
  exact ⟨hdec, s.src.wf, hU, alt_conflict_freeU _ _ hU _ hc, hval, hf,
    alternativesU_dilemma_witness_sound s.src.A s.unspec s.src.wf hU w.sc.M w.F valid hb hf hΓ w.r hr hd⟩

/-! ## The diagnosis (untrusted) -/

/-- `F` with the atoms `C` set exactly as `S` says. -/
def refill {α : Type u} [DecidableEq α] {U : UDoc} (F : FiniteFill U α) (C S : List (String × List α)) :
    FiniteFill U α :=
  fun n => (F n).filter (fun vs => !C.contains (n, vs)) ++ (S.filter (·.1 == n)).map (·.2)

/-- The alternatives available to `r` that some validated refilling of the cone of `clear°(r, a)` makes clear:
with the witness's filling, at which none is clear, two validated fillings that answer both ways. -/
def unsettledAt (A : AltDoc) (unspec : List String) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : FiniteFill ⟨inlineTree A, unspec⟩ VE.Bridge.Entity) (r : VE.Bridge.Entity) : List VE.Bridge.Entity :=
  (availOf M A.alt.available r).filter fun a =>
    let C := VE.NormDefaults.coneOf ⟨inlineTree A, unspec⟩ M (tupleVal [r, a]) (clearFU A unspec)
    decide (C.length ≤ VE.NormDefaults.MAX_UNSAID_ATOMS) && (VE.NormDefaults.subsets C).any fun S =>
      fillValid ⟨inlineTree A, unspec⟩ M (refill F C S) &&
        (clearFU A unspec).eval (M.withFill (refill F C S)) (tupleVal [r, a])

/-- The 4.6 classification with the completion: UNSETTLED before every other branch but "no alternatives",
then today's procedure on the filled outcomes. -/
def diagnoseU (A : AltDoc) (unspec : List String) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : FiniteFill ⟨inlineTree A, unspec⟩ VE.Bridge.Entity) (r : VE.Bridge.Entity) : Diagnosis VE.Bridge.Entity :=
  if (availOf M A.alt.available r).isEmpty then .noAlternatives
  else match unsettledAt A unspec M F r with
    | [] => diagnoseIn (fill ⟨inlineTree A, unspec⟩) A (M.withFill F) r
    | as => .unsettled as

/-! ## Scenario values (the evidence contract C, spec 5 and 6.4) -/

open VE.NormDefaults (FillTables coneOf coneValuesAt agreed subsets unsaidAtoms fillOfAtoms)

def SettledF (A : AltDoc) (unspec : List String) (B : VE.Structure.{u}) (φ : VE.Formula) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables ⟨inlineTree A, unspec⟩ B,
    BaseAdmissibleAltU A unspec (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ B F) →
    (φ.denote (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ B F) (tupleVal vs) ↔ b = true)

def UndecidedF (A : AltDoc) (unspec : List String) (B : VE.Structure.{u}) (φ : VE.Formula)
    (vs : List B.Carrier) : Prop :=
  ∃ F₁ F₂ : FillTables ⟨inlineTree A, unspec⟩ B,
    BaseAdmissibleAltU A unspec (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ B F₁) ∧
    BaseAdmissibleAltU A unspec (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ B F₂) ∧
    φ.denote (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ B F₁) (tupleVal vs) ∧
    ¬ φ.denote (VE.NormDefaults.withFill ⟨inlineTree A, unspec⟩ B F₂) (tupleVal vs)

inductive AltStatus
  | clear
  | notClear
  | undecided
  | unknown
  deriving DecidableEq

/-- The evidence a scenario status rests on (C): `budget` when the cone exceeds it, `search` when no two validated
refillings were found, `noFilling` when no filling of the scenario is validated. -/
inductive AltEvidence
  | kleene
  | enumeration
  | fillings
  | budget
  | search
  | noFilling
  deriving DecidableEq

/-- A scenario row: the scenario's validity, today's (its model, its background with the slot premises, its signed
rows, the existence checks and Γ), a typed chooser and action, and one filling validated by `fillValid`, so that
no status is vacuous (SR-A4); then the evidence its status needs (C). `unknown` needs no more. -/
structure ScenarioRowU (A : AltDoc) (unspec : List String) where
  M : VE.FiniteModel VE.Bridge.Entity
  rows : List Row
  chooser : VE.Bridge.Entity
  action : VE.Bridge.Entity
  status : AltStatus
  valid : M.Valid (VE.Norms.envAt (inlineTree A) 0)
  background : backgroundValidAlt A M = true
  checked : validateAlternatives A M rows = .ok ()
  chooser_typed : chooser ∈ M.domains A.alt.chooser
  action_typed : action ∈ M.domains A.alt.action
  F : FiniteFill ⟨inlineTree A, unspec⟩ VE.Bridge.Entity
  filled : fillValid ⟨inlineTree A, unspec⟩ M F = true
  clear_sound : status = .clear → SettledF.{0} A unspec M.asStructure (clearFU A unspec) [chooser, action] true
  notClear_sound : status = .notClear →
    SettledF.{0} A unspec M.asStructure (clearFU A unspec) [chooser, action] false
  undecided_sound : status = .undecided → UndecidedF.{0} A unspec M.asStructure (clearFU A unspec) [chooser, action]

/-- A value every assignment of `C` agrees on is settled (Kleene with `C = []`, enumeration of the cone). -/
theorem settledF_of_agreed (A : AltDoc) (unspec : List String) (M : VE.FiniteModel VE.Bridge.Entity)
    (C : List (String × List VE.Bridge.Entity)) (vs : List VE.Bridge.Entity) (b : Bool)
    (h : agreed (coneValuesAt ⟨inlineTree A, unspec⟩ M C (tupleVal vs) (clearFU A unspec)) = some b) :
    SettledF.{0} A unspec M.asStructure (clearFU A unspec) vs b :=
  fun F hF => VE.NormDefaults.denote_of_coneValuesAt _ M C _ _ b (VE.NormDefaults.agreed_all h) F hF.1.2

/-- Two validated fillings with opposite values of `clear°` are UNDECIDED (as `undecided_witness_sound`). -/
theorem undecidedF_of_fillings (A : AltDoc) (unspec : List String) (hA : WellFormedAlt A = true)
    (h : WellFormedU ⟨inlineTree A, unspec⟩ = true) (M : VE.FiniteModel VE.Bridge.Entity)
    (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
    (F₁ F₂ : FiniteFill ⟨inlineTree A, unspec⟩ VE.Bridge.Entity) (vs : List VE.Bridge.Entity)
    (hc : fillValid ⟨inlineTree A, unspec⟩ M F₁ = true ∧ fillValid ⟨inlineTree A, unspec⟩ M F₂ = true ∧
      (clearFU A unspec).eval (M.withFill F₁) (tupleVal vs) = true ∧
      (clearFU A unspec).eval (M.withFill F₂) (tupleVal vs) = false) :
    UndecidedF.{0} A unspec M.asStructure (clearFU A unspec) vs :=
  ⟨finFill M F₁, finFill M F₂, admissibleAltU_of_fillValid A unspec hA h M valid hb F₁ hc.1,
    admissibleAltU_of_fillValid A unspec hA h M valid hb F₂ hc.2.1,
    (VE.NormDefaults.eval_withFill _ M F₁ _ _).mp hc.2.2.1, fun hd => by
      have := (VE.NormDefaults.eval_withFill _ M F₂ _ _).mpr hd
      rw [hc.2.2.2] at this
      cases this⟩

/-- Two refillings of the cone `C` of `F`, at which `φ` holds and fails, each validated (untrusted: `settleU`
checks them). -/
def fillingsAt (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity) (F : FiniteFill U VE.Bridge.Entity)
    (C : List (String × List VE.Bridge.Entity)) (ρ : List VE.Bridge.Entity) (φ : VE.Formula) :
    Option (FiniteFill U VE.Bridge.Entity × FiniteFill U VE.Bridge.Entity) :=
  let at_ (b : Bool) := ((subsets C).find? fun S =>
    fillValid U M (refill F C S) && (φ.eval (M.withFill (refill F C S)) ρ == b)).map (refill F C)
  match at_ true, at_ false with
  | some F₁, some F₂ => some (F₁, F₂)
  | _, _ => none

/-- A filling for the scenario: the supplied one, else an assignment of the unsaid atoms when there are at most
`budget` of them, else nothing filled; the first that `fillValid` accepts. -/
def fillingFor (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity) (supplied : Option (FiniteFill U VE.Bridge.Entity))
    (budget : Nat) : Option (FiniteFill U VE.Bridge.Entity) :=
  let atoms := unsaidAtoms U M
  (supplied.toList ++ (if atoms.length ≤ budget then (subsets atoms).map fillOfAtoms else [fillOfAtoms []])).find?
    (fillValid U M)

section Scenario
variable (A : AltDoc) (unspec : List String) (hA : WellFormedAlt A = true)
  (h : WellFormedU ⟨inlineTree A, unspec⟩ = true) (M : VE.FiniteModel VE.Bridge.Entity) (rows : List Row)
  (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
  (checked : validateAlternatives A M rows = .ok ()) (F : FiniteFill ⟨inlineTree A, unspec⟩ VE.Bridge.Entity)
  (filled : fillValid ⟨inlineTree A, unspec⟩ M F = true)

/-- One alternative's row (C): a definite Kleene value, else enumeration of the cone of `clear°(r, a)` within
`budget`, else two validated refillings of the cone; UNKNOWN otherwise. The label names the evidence. -/
def settleU (budget : Nat) (r a : VE.Bridge.Entity) (hr : r ∈ M.domains A.alt.chooser)
    (ha : a ∈ M.domains A.alt.action) : ScenarioRowU A unspec × AltEvidence :=
  let U : UDoc := ⟨inlineTree A, unspec⟩
  let ρ := tupleVal [r, a]
  let unknown (label : AltEvidence) : ScenarioRowU A unspec × AltEvidence :=
    (⟨M, rows, r, a, .unknown, valid, hb, checked, hr, ha, F, filled, nofun, nofun, nofun⟩, label)
  let settled (b : Bool) (hs : SettledF.{0} A unspec M.asStructure (clearFU A unspec) [r, a] b) (label : AltEvidence) :
      ScenarioRowU A unspec × AltEvidence := match b, hs with
    | true, hs => (⟨M, rows, r, a, .clear, valid, hb, checked, hr, ha, F, filled, fun _ => hs, nofun, nofun⟩, label)
    | false, hs => (⟨M, rows, r, a, .notClear, valid, hb, checked, hr, ha, F, filled, nofun, fun _ => hs, nofun⟩,
        label)
  match hk : agreed (coneValuesAt U M [] ρ (clearFU A unspec)) with
  | some b => settled b (settledF_of_agreed A unspec M [] [r, a] b hk) .kleene
  | none =>
    let C := coneOf U M ρ (clearFU A unspec)
    if C.length > budget then unknown .budget else
    match he : agreed (coneValuesAt U M C ρ (clearFU A unspec)) with
    | some b => settled b (settledF_of_agreed A unspec M C [r, a] b he) .enumeration
    | none => match fillingsAt U M F C ρ (clearFU A unspec) with
      | some (F₁, F₂) =>
        if hc : fillValid U M F₁ = true ∧ fillValid U M F₂ = true ∧
            (clearFU A unspec).eval (M.withFill F₁) ρ = true ∧ (clearFU A unspec).eval (M.withFill F₂) ρ = false then
          (⟨M, rows, r, a, .undecided, valid, hb, checked, hr, ha, F, filled, nofun, nofun,
            fun _ => undecidedF_of_fillings A unspec hA h M valid hb F₁ F₂ [r, a] hc⟩, .fillings)
        else unknown .search
      | none => unknown .search

/-- The rows of chooser `r`: one per available alternative of the action sort, in `available` order. -/
def chooserRowsU (budget : Nat) (r : VE.Bridge.Entity) (hr : r ∈ M.domains A.alt.chooser) :
    List (ScenarioRowU A unspec × AltEvidence) :=
  (availOf M A.alt.available r).filterMap fun a =>
    if ha : a ∈ M.domains A.alt.action then some (settleU A unspec hA h M rows valid hb checked F filled budget r a hr ha)
    else none

end Scenario

theorem fillingFor_valid {U : UDoc} {M : VE.FiniteModel VE.Bridge.Entity} {supplied : Option (FiniteFill U _)}
    {budget : Nat} {F : FiniteFill U VE.Bridge.Entity} (h : fillingFor U M supplied budget = some F) :
    fillValid U M F = true :=
  List.find?_some h

/-- The scenario's rows, chooser by chooser (spec 6.4's `scenarioRowU`): today's validation (whose text the runner
answers on failure), then a validated filling, then each chooser's rows; `none` when no filling is validated, and
every alternative is UNKNOWN. -/
def scenarioRowsU (s : AltSourceU) (sc : Replay.Scenario s.src) (supplied : Option (FiniteFill s.U VE.Bridge.Entity))
    (budget : Nat) : Option (List (VE.Bridge.Entity × List (ScenarioRowU s.src.A s.unspec × AltEvidence))) :=
  if hm : altModelChecks s.src.A sc.M sc.rows = true then
    if hU : WellFormedU s.U = true then
      match hf : fillingFor s.U sc.M supplied budget with
      | some F =>
        have hval : validateAlternatives s.src.A sc.M sc.rows = .ok () := validateAlternativesWith_ok.mpr hm
        have hs := Replay.validate_sound_decoded s.src sc hval
        some ((sc.M.domains s.src.A.alt.chooser).attach.map fun ⟨r, hr⟩ => (r, chooserRowsU s.src.A s.unspec
          s.src.wf hU sc.M sc.rows hs.1 hs.2.1 hval F (fillingFor_valid hf) budget r hr))
      | none => none
    else none
  else none

end VE.Alternatives
