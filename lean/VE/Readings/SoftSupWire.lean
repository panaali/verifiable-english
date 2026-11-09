import VE.Readings.SoftSupLabels
import VE.Readings.SupVerdictsWire
import VE.Readings.SoftWire

/-! SC-11's route under the soft completion (docs/spec/rd-9-soft-chain.md 14.2, 14.8, 14.11).

`routeSD re N` is `routeOf true N.D` with its enumerated row superposed exactly when the superposed document is
superposable with `WellFormedU (supU N)` (`sdSuperposable`) and DRI ruling 5's per-choice check, extended by 3.3
step 5, passes within its limits (`sdChecked`): at most `maxChoiceChecks` compatible choices, `sdCheckWork N` within
`maxSdCheckWork` (read before the first `sdChoiceText`, since `&&` reads left to right), and `sdChoiceText` none for
each choice. Over a limit the row stays enumerated, as today; it is never an error. Nothing dispatches on `routeSD`
here (sc-11b switches the dispatch). 14.8's superposed case (`SupReplaySD`) and its wire theorems are sc-11c's
(docs/rd-9/sc-11/REPORT.md).

`maxSdCheckWork` is measured (14.11, DRI decision 2026-11-09 item 1, docs/rd-9/sc-11/w13-cpu.md): about 29 µs of
Lean CPU per unit of `sdCheckWork` on W-13's shape, so 32,768 units keep the route check under R4's 1 s. -/
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

end VE.Readings.Wire
