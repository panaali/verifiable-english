import VE.Readings.SoftSupLabels
import VE.Readings.SupVerdictsWire
import VE.Readings.SoftWire

/-! SC-11's route under the soft completion (docs/spec/rd-9-soft-chain.md 14.2, 14.8, 14.11).

`routeSD re N` is `routeOf true N.D` with its enumerated row superposed exactly when the superposed document is
superposable with `WellFormedU (supU N)` (`sdSuperposable`) and DRI ruling 5's per-choice check, extended by 3.3
step 5, passes within its limits (`sdChecked`): at most `maxChoiceChecks` compatible choices, `sdCheckWork N` within
`maxSdCheckWork` (read before the first `sdChoiceText`, since `&&` reads left to right), and `sdChoiceText` none for
each choice. Over a limit the row stays enumerated, as today; it is never an error. Nothing dispatches on `routeSD`
here (sc-11b switches the dispatch); the wire theorems read a superposed case's accepted evidence in each choice's
own terms through sc-10b's three superposition theorems, which they apply and do not restate.

`maxSdCheckWork` is measured (14.11, DRI decision 2026-11-09 item 1, docs/rd-9/sc-11/w13-cpu.md): about 29 µs of
Lean CPU per unit of `sdCheckWork` on W-13's shape, so 32,768 units keep the route check under R4's 1 s on that
shape; a wide guard costs more per unit, and row sc-11w makes the charge cost-proportional before sc-11b. -/
namespace VE.Readings.Wire
open VE.Readings
open VE.Bridge (Entity)
open VE.Norms (targets)
open VE.NormDefaults (fill)
universe u

def sdSuperposable (N : NDoc) : Bool := superposable N.D && VE.NormDefaults.WellFormedU (supU N)

/-- 14.11: the compatible choices times the superposed premises and rule nodes each check reads. -/
def maxSdCheckWork : Nat := 32768
def sdCheckWork (N : NDoc) : Nat :=
  (checkedChoices N.D).length * ((softXL N (sup N.D).1).length + ((sup N.D).1.soft.T.nodes.map
    (fun M => (M.guard :: M.carveOuts).map VE.Bridge.formulaNodes)).flatten.sum)

/-- DRI ruling 5 extended by 3.3 step 5, within its limits. -/
def sdChecked (re : ReadingsEnvironment) (N : NDoc) : Bool :=
  decide ((checkedChoices N.D).length ≤ maxChoiceChecks) && decide (sdCheckWork N ≤ maxSdCheckWork) &&
    (checkedChoices N.D).all (fun c => (sdChoiceText re N c).isNone)

def routeSD (re : ReadingsEnvironment) (N : NDoc) : Route :=
  match routeOf true N.D with
  | .enumerated => if sdSuperposable N && sdChecked re N then .superposed else .enumerated
  | r => r

/-- A superposed case on the soft chain: the case's one admission, its route, a compatible choice. -/
structure SupReplaySD where
  r : AdmittedSD
  route : routeSD r.b.a.re r.N = .superposed
  sat : (choices r.N.D).isEmpty = false

theorem routeSD_superposed_iff (re : ReadingsEnvironment) (N : NDoc) :
    routeSD re N = .superposed ↔
      routeOf true N.D = .enumerated ∧ sdSuperposable N = true ∧ sdChecked re N = true := by
  have hne : routeOf true N.D ≠ .superposed := by
    unfold routeOf
    repeat' split
    all_goals first | exact absurd rfl ‹¬true = true› | simp
  unfold routeSD
  cases h : routeOf true N.D
  case superposed => exact absurd h hne
  case enumerated => simp only [true_and, Bool.and_eq_true]; split <;> simp_all
  all_goals simp

theorem sdChecked_spec (re : ReadingsEnvironment) (N : NDoc) (hr : supReady N.D = true)
    (hw : sdChecked re N = true) (c : Choice) (hc : Compatible N.D c) :
    sdChoiceText re N c = none ∧ VE.NormDefaults.WellFormedU (choiceU N c) = true := by
  simp only [sdChecked, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Option.isNone_iff_eq_none] at hw
  obtain ⟨⟨hle, -⟩, hall⟩ := hw
  have hlt : (search N.D N.D.sets [] (maxChoiceChecks + 1)).length < maxChoiceChecks + 1 := by
    simp only [checkedChoices] at hle; omega
  have h1 := hall c ((search_spec N.D hr _ hlt c).mpr hc)
  refine ⟨h1, ?_⟩
  unfold sdChoiceText at h1
  exact wellFormedU_of_ndDocTextG (Option.map_eq_none_iff.mp (Option.or_eq_none_iff.mp h1).2)

/-- At most 64 compatible choices, the cut of 1024 is the cut of 64. -/
theorem checkedChoices_eq_choices (D : Doc) (hle : (checkedChoices D).length ≤ maxChoices) :
    checkedChoices D = choices D := by
  simp only [checkedChoices, choices, search_eq, List.length_take, maxChoices, maxChoiceChecks] at hle ⊢
  have : (allFrom D D.sets []).length ≤ 64 := by omega
  rw [List.take_of_length_le (by omega), List.take_of_length_le (by omega)]

theorem sdCheck_of_admitted (b : Admitted2) (r : AdmittedSD) (hadm : admitSDOf b = .ok r) (hr : supReady r.N.D = true)
    (hle : (checkedChoices r.N.D).length ≤ maxChoices) (hw : sdCheckWork r.N ≤ maxSdCheckWork) :
    sdChecked r.b.a.re r.N = true := by
  have _ := hr
  have heq := checkedChoices_eq_choices r.N.D hle
  have hnone : ∀ c ∈ choices r.N.D, sdChoiceText r.b.a.re r.N c = none := by
    unfold admitSDOf at hadm
    rw [Stage.stage_eq] at hadm
    simp only at hadm
    split at hadm
    · split at hadm
      · cases hadm
      · split at hadm
        · split at hadm
          · cases hadm
          · rename_i hc
            cases hadm
            rw [heq] at hle
            rw [if_pos hle] at hc
            exact List.findSome?_eq_none_iff.mp hc
        · cases hadm
    · cases hadm
  simp only [sdChecked, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Option.isNone_iff_eq_none, heq]
  exact ⟨⟨by rw [← heq]; simp only [maxChoices, maxChoiceChecks] at hle ⊢; omega, hw⟩, hnone⟩

/-- What a superposed case's route says of its document. -/
theorem SupReplaySD.parts (x : SupReplaySD) :
    superposable x.r.N.D = true ∧ VE.NormDefaults.WellFormedU (supU x.r.N) = true ∧
      sdChecked x.r.b.a.re x.r.N = true := by
  obtain ⟨-, hsp, hck⟩ := (routeSD_superposed_iff _ _).mp x.route
  simp only [sdSuperposable, Bool.and_eq_true] at hsp
  exact ⟨hsp.1, hsp.2, hck⟩

theorem readings_wire_sd_choices (x : SupReplaySD) :
    (∃ c, Compatible x.r.N.D c) ∧ ∀ c, Compatible x.r.N.D c →
      sdChoiceText x.r.b.a.re x.r.N c = none ∧ VE.NormDefaults.WellFormedU (choiceU x.r.N c) = true := by
  obtain ⟨hs, -, hck⟩ := x.parts
  exact ⟨exists_compatible_of_choices _ x.sat, fun c hc => sdChecked_spec _ _ (superposable_supReady hs) hck c hc⟩

theorem readings_wire_sd_conflict_sound (x : SupReplaySD) (A : Choice)
    (hA : ∀ z ∈ A, (candidate x.r.N.D z.1 z.2).isSome) (certs : List (Option VE.Tableau.Certificate))
    (hc : VE.NormDefaults.Wire.conflictFreeCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) certs = true) :
    ∀ c, Compatible x.r.N.D c → (∀ z ∈ A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N c) (choiceX x.r.N c) := by
  obtain ⟨hs, hsu, -⟩ := x.parts
  exact (sd_superpose_conflict_free x.r.N x.r.wf hs hsu A hA).mp
    (VE.NormDefaults.Wire.conflictFreeCheckX_sound _ (VE.NormDefaults.fill_wellFormed _ hsu) _ certs hc)

theorem readings_wire_sd_all_sound (x : SupReplaySD) (A : Choice)
    (hA : ∀ z ∈ A, (candidate x.r.N.D z.1 z.2).isSome) (certs : List (Option VE.Tableau.Certificate))
    (hc : VE.NormDefaults.Wire.conflictFreeCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) certs = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnvSD x.r.N) [])
    (hφ : φ.WellFormed (sharedEnvSD x.r.N) []) (cert : VE.Tableau.Certificate)
    (ha : supCertificateCheckSD x.r.N A Γ φ cert = true) :
    ∀ c, Compatible x.r.N.D c → (∀ z ∈ A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N c) (choiceX x.r.N c) ∧
        VE.NormDefaults.EntailsX.{u} (choiceU x.r.N c) (choiceX x.r.N c) ((choiceDoc x.r.N.D c).2 ++ Γ) φ := by
  obtain ⟨hs, hsu, -⟩ := x.parts
  have hcf := VE.NormDefaults.Wire.conflictFreeCheckX_sound.{u} _ (VE.NormDefaults.fill_wellFormed _ hsu) _ certs hc
  intro c hcc hAc
  exact ⟨(sd_superpose_conflict_free x.r.N x.r.wf hs hsu A hA).mp hcf c hcc hAc,
    sd_superpose_all x.r.N x.r.wf hs hsu A hA hcf Γ φ hΓ hφ cert ha c hcc hAc⟩

theorem readings_wire_sd_model_sound (x : SupReplaySD) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnvSD x.r.N) [])
    (hφ : φ.WellFormed (sharedEnvSD x.r.N) []) (M : VE.FiniteModel Entity)
    (valid : M.Valid (VE.Norms.envAt (supU x.r.N).D 0)) (F : VE.NormDefaults.FiniteFill (supU x.r.N) Entity)
    (hm : (VE.NormDefaults.modelCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F
      ((sup x.r.N.D).2 ++ Γ) φ).1 = true)
    (hn : (VE.NormDefaults.modelCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F
      ((sup x.r.N.D).2 ++ Γ) φ).2 = false)
    (hl : localFree (supU x.r.N) M F = true) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ z ∈ A, z ∈ c) ∧
      Encodes x.r.N.D c (VE.NormDefaults.withFill (supU x.r.N) M.asStructure (VE.NormDefaults.finFill M F)) ∧
      CounterX (choiceU x.r.N c) (choiceX x.r.N c) ((choiceDoc x.r.N.D c).2 ++ Γ) φ := by
  obtain ⟨hs, hsu, -⟩ := x.parts
  exact sd_superpose_countermodel x.r.N x.r.wf hs hsu A Γ φ hΓ hφ M valid F hm hn hl

theorem readings_wire_sd_consistent_sound (x : SupReplaySD) (A : Choice) (M : VE.FiniteModel Entity)
    (valid : M.Valid (VE.Norms.envAt (supU x.r.N).D 0)) (F : VE.NormDefaults.FiniteFill (supU x.r.N) Entity)
    (hm : (VE.NormDefaults.modelCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F
      (sup x.r.N.D).2 .bottom).1 = true)
    (hl : localFree (supU x.r.N) M F = true) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ z ∈ A, z ∈ c) ∧
      ConsistentX (choiceU x.r.N c) (choiceX x.r.N c) (choiceDoc x.r.N.D c).2 := by
  have hn : (VE.NormDefaults.modelCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F
      ((sup x.r.N.D).2 ++ []) .bottom).2 = false := by
    simp [VE.NormDefaults.modelCheckX, VE.NormDefaults.modelCheckU, VE.Norms.subst, VE.Norms.substWith]
    rfl
  obtain ⟨c, hc, hA, -, S, hB, hE, hS, -⟩ := readings_wire_sd_model_sound x A [] .bottom (fun _ h => by cases h)
    (by simp [VE.Formula.WellFormed]) M valid F (by rw [List.append_nil]; exact hm) hn hl
  exact ⟨c, hc, hA, S, hB, hE, by rw [List.append_nil] at hS; exact hS⟩

theorem readings_wire_sd_witness_sound (x : SupReplaySD) (A : Choice)
    (t : String × List String × VE.Formula) (ht : t ∈ targets (fill (supU x.r.N))) (M : VE.FiniteModel Entity)
    (valid : M.Valid (VE.Norms.envAt (supU x.r.N).D 0)) (hbg : VE.Norms.backgroundValid (supU x.r.N).D M = true)
    (F : VE.NormDefaults.FiniteFill (supU x.r.N) Entity)
    (hf : VE.NormDefaults.fillValid (supU x.r.N) M F = true)
    (hX : VE.NormDefaults.Wire.extraValid (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F = true)
    (vs : List Entity)
    (typed : VE.TupleTyped (VE.NormDefaults.withFill (supU x.r.N) M.asStructure (VE.NormDefaults.finFill M F)) t.2.1 vs)
    (hw : t.2.2.eval (M.withFill F) (VE.Norms.tupleVal vs) = true) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ z ∈ A, z ∈ c) ∧
      Encodes x.r.N.D c (VE.NormDefaults.withFill (supU x.r.N) M.asStructure (VE.NormDefaults.finFill M F)) ∧
      ¬ VE.NormDefaults.Wire.ConflictFreeX.{0} (choiceU x.r.N c) (choiceX x.r.N c) := by
  obtain ⟨hs, hsu, -⟩ := x.parts
  have hB := VE.NormDefaults.Wire.admissibleX_of_fill _ hsu _ M valid hbg F hf hX
  obtain ⟨c, hc, hAc, he, hsl, hY⟩ := pullF_baseX x.r.N x.r.wf hs hsu A _ hB
  refine ⟨c, hc, hAc, he, fun hcf => ?_⟩
  exact VE.NormDefaults.Wire.target_not_conflictFree _ (VE.NormDefaults.fill_wellFormed _ hsu) t ht _ vs typed
    ((VE.NormDefaults.eval_withFill _ M F _ _).mp hw)
    ((conflictFree_pullF x.r.N x.r.wf hs hsu c hc _ hB.1.1 hsl he).mpr (hcf _ hY))

end VE.Readings.Wire
