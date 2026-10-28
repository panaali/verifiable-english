import VE.Defaults.Meaning
import VE.Defaults.Examples

/-! DF-2's checks on decoded documents (docs/spec/defeasible.md 8.2): `softX` is the decoder's own `X` followed by
the other packs' premises; `SwitchesOff` and the least decisions `δ_B` read at one-element situations; and
`replacementSafe` exactly when the other packs name no decision and no unsaid table of a pair member (spec 8.2's row,
DF-π and DF-α). A situation's premises are read through RD-9's `eval` (`eval_withFill`), so each `Prop` here is
decided on a finite model.

DF-π's two `example`s (spec 8.5) are over the `SoftDoc` literal `Dπ`, which a `#guard` ties to the decoded `dπ`, so
that the kernel evaluates them by `decide`: `B_π` is a default base with draft 1's fixed filling, and is not a
`DefaultBase`. The kernel cannot reduce `String.map` or `String.startsWith`, so the names enter through three proved
facts: `soften_π` (the softened literal `Sπ`), `decisions_π` and `switch_π`. -/
namespace VE.Defaults.MeaningFixtures
open VE.Defaults VE.Defaults.Fixtures
open VE.NormDefaults (UDoc unsaidName withFill finFill FiniteFill)
open VE.NormDefaults.Wire (LayeredU)

instance denoteDec (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity) (φ : VE.Formula)
    (ρ : List Entity) : Decidable (φ.denote (withFill U M.asStructure (finFill M F)) ρ) :=
  decidable_of_iff _ (VE.NormDefaults.eval_withFill U M F φ ρ)

instance typedDec (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity) (ss : List String)
    (vs : List Entity) : Decidable (VE.TupleTyped (withFill U M.asStructure (finFill M F)) ss vs) :=
  decidable_of_iff _ ((VE.NormDefaults.mem_allTuples M ss vs).trans
    (VE.Norms.tupleTyped_relation M.asStructure _ ss vs).symm)

instance switchesDec (D : VE.SoftNorms.SoftDoc) (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity) :
    Decidable (SwitchesOff D (withFill U M.asStructure (finFill M F))) := by
  unfold SwitchesOff; (try unfold VE.Norms.Sat); infer_instance

instance leastDec (D : VE.SoftNorms.SoftDoc) (U : UDoc) (M : VE.FiniteModel Entity) (F : FiniteFill U Entity)
    (p : String) (vs : List Entity) : Decidable (leastDecisions D (withFill U M.asStructure (finFill M F)) p vs) := by
  unfold leastDecisions; infer_instance

/-- The one-element situation with the predicates `on` true and no gap filled. -/
abbrev sit (L : LayeredU) (on : List String) : VE.Structure.{0} :=
  withFill L.U (sitOf L on).asStructure (finFill (sitOf L on) (fillOf L []))

def a1 : List Entity := [elemOf "assistant"]

/-! ## `softX` -/

/-- One default rule with two stated sufficient conditions: two soft premises. -/
def dTwo : Except String LayeredU := layered (envJ [xReq, xPerm, baseJ "urgent", baseJ "calm"] strictSoft)
  [ruleJ "r1" "x_required" true (dfltJ [un "urgent", un "calm"])]
def rA : VE.Formula := .all "assistant" (.unary "urgent" (.var 0))
def rB : VE.Formula := .ex "assistant" (.unary "calm" (.var 0))

#guard holds dTwo fun L => L.X.length == 2 && softX L.U L.D [rA, rB] == L.X ++ [rA, rB]
#guard holds dα fun L => softX L.U L.D [] == L.X

/-! ## `SwitchesOff` -/

/-- A strict rule with two switches, so that `Dflt_T` is two switch premises. -/
def dSw : Except String LayeredU := layered (envJ [xReq, xPerm]
    r#"{"parties":["operator","user"],"outranking":{"mode":"strict"}}"#)
  [ruleJ "r0" "x_required" true ",\"alterable\":[\"operator\",\"user\"]"]
def offOf (L : LayeredU) (i : Nat) : String := ((VE.SoftNorms.offDecisions L.D).map (·.1)).getD i ""

#guard holds dSw fun L => (dfltLabelled L.D).length == 2 && decide (SwitchesOff L.D (sit L [])) &&
  !decide (SwitchesOff L.D (sit L [offOf L 0])) && !decide (SwitchesOff L.D (sit L [offOf L 1]))
#guard holds dε fun L => decide (SwitchesOff L.D (sit L [exc1])) && !decide (SwitchesOff L.D (sit L [offOf L 0]))

/-! ## The least decisions `δ_B` -/

#guard holds dTwo fun L => decide (leastDecisions L.D (sit L ["urgent"]) exc1 a1) &&
  decide (leastDecisions L.D (sit L ["calm"]) exc1 a1) && decide (leastDecisions L.D (sit L ["urgent", "calm"]) exc1 a1)
#guard holds dTwo fun L => !decide (leastDecisions L.D (sit L []) exc1 a1) &&
  !decide (leastDecisions L.D (sit L ["urgent"]) exc1 []) && !decide (leastDecisions L.D (sit L ["urgent"]) "a" a1) &&
  !decide (leastDecisions L.D (sit L ["urgent"]) "urgent" a1)
-- No switch is ever a least decision (DF-ε's switch, at a situation where it is on).
#guard holds dε fun L => !decide (leastDecisions L.D (sit L [offOf L 0]) (offOf L 0) a1)

/-! ## `replacementSafe` (spec 8.2: DF-π with `R = []` true, DF-α with `R = [∀a. excepted_r1(a)]` false) -/

/-- DF-π: DF-α with `x_permitted` also unspecified, so both members of the pair have unsaid tables. -/
def dπ : Except String LayeredU := layered (envJ [xReq,
    regJ "x_permitted" "[\"assistant\"]" "permission" "unspecified" ",\"act\":\"{0} do x\""] strictSoft)
  [ruleJ "r1" "x_required" true dfltJ]

#guard holds dπ fun L => replacementSafe L.U L.D [] && replacementSafe L.U L.D [rA] &&
  !replacementSafe L.U L.D [.all "assistant" (.unary (unsaidName "x_permitted") (.var 0))]
#guard holds dα fun L => replacementSafe L.U L.D [] && !replacementSafe L.U L.D [.all "assistant" (.unary exc1 (.var 0))]

/-! ## DF-π's two `example`s (spec 8.5) -/

def nπ : VE.SoftNorms.SoftNode :=
  ⟨⟨"r1", "x_required", true, .top, [], []⟩, .default, none, [], some ⟨some "assistant", [], [], []⟩, false⟩

/-- DF-π as a literal: the default obligation r1 on `x_required` and its paired permission, both unspecified. -/
def Dπ : VE.SoftNorms.SoftDoc where
  E.sorts := ["assistant"]
  E.constants _ := none
  E.predicates p := if p = "x_required" ∨ p = "x_permitted" then some ["assistant"] else none
  lits := []
  soft.parties := []
  soft.ranks := []
  soft.outranks := []
  soft.ties := []
  soft.outranking := .strict
  soft.outrankingDecider := none
  soft.exceptionDecider := none
  soft.instructionOf := []
  soft.below := []
  T.regulated := [
    ⟨"x_permitted", ["assistant"], false, .permission, some "{0} do x", none⟩,
    ⟨"x_required", ["assistant"], false, .obligation, some "{0} do x", some "x_permitted"⟩]
  T.definitions := []
  T.nodes := [nπ]

def Uπ : UDoc := ⟨VE.SoftNorms.soften Dπ, ["x_permitted", "x_required"]⟩
def excπ : String := "soft__excepted__r1"

-- The literal is the decoded document.
#guard holds dπ fun L => L.D.T == Dπ.T && L.D.soft == Dπ.soft && L.D.lits == Dπ.lits && L.D.E.sorts == Dπ.E.sorts &&
  L.U.unspec == Uπ.unspec && L.U.D.T == Uπ.D.T && VE.SoftNorms.decisionNames L.D == [excπ] &&
  ["x_required", "x_permitted", excπ, unsaidName "x_required", unsaidName "x_permitted", "assistant", "r1"].all
    fun p => L.D.E.predicates p == Dπ.E.predicates p && L.U.D.E.predicates p == Uπ.D.E.predicates p &&
      L.D.E.constants p == Dπ.E.constants p

/-- `soften Dπ` with r1's exception name written out. -/
def Sπ : VE.Norms.Doc where
  E := { Dπ.E with predicates := fun p => if p = excπ then some ["assistant"] else Dπ.E.predicates p }
  lits := []
  T.regulated := Dπ.T.regulated
  T.definitions := []
  T.nodes := [⟨"r1", "x_required", true, .top,
    [.or (.or (.or (.unary excπ (.var 0)) .bottom) (.or (.or (.or (.or .bottom .bottom) .bottom) .bottom) .bottom)) .bottom],
    []⟩]

theorem exceptedName_π : VE.SoftNorms.exceptedName nπ = excπ :=
  String.ext (by simp [VE.SoftNorms.exceptedName, VE.SoftNorms.ruleKey, VE.Readings.map_data, nπ, excπ])

theorem decisions_π : VE.SoftNorms.decisions Dπ = [(excπ, ["assistant"])] := by
  show [(VE.SoftNorms.exceptedName nπ, ["assistant"])] ++ [] ++ [] = _
  rw [exceptedName_π]; rfl

theorem decisionNames_π : VE.SoftNorms.decisionNames Dπ = [excπ] := by
  simp [VE.SoftNorms.decisionNames, decisions_π]

theorem soften_π : VE.SoftNorms.soften Dπ = Sπ := by
  have hE : VE.SoftNorms.envPrime Dπ = Sπ.E := by
    unfold VE.SoftNorms.envPrime
    rw [decisions_π]
    refine congrArg (fun f => ({ Dπ.E with predicates := f } : VE.Environment)) (funext fun p => ?_)
    by_cases h : p = excπ
    · subst h; rfl
    · have : (excπ == p) = false := beq_false_of_ne (Ne.symm h)
      simp [List.find?, this, h]
  have hN : Dπ.T.nodes.map (VE.SoftNorms.primeNode Dπ) = Sπ.T.nodes := by
    show [VE.SoftNorms.primeNode Dπ nπ] = _
    simp only [VE.SoftNorms.primeNode, VE.SoftNorms.derivedList, VE.SoftNorms.derived, VE.SoftNorms.exceptedF,
      exceptedName_π]
    rfl
  show (⟨VE.SoftNorms.envPrime Dπ, [], ⟨Dπ.T.regulated, [], Dπ.T.nodes.map (VE.SoftNorms.primeNode Dπ)⟩⟩ :
    VE.Norms.Doc) = Sπ
  rw [hE, hN]
  rfl

theorem Uπ_eq : Uπ = ⟨Sπ, ["x_permitted", "x_required"]⟩ := by
  show (⟨VE.SoftNorms.soften Dπ, _⟩ : UDoc) = _
  rw [soften_π]

/-- r1's exception label is not a switch label (`String.substrEq`'s loop unfolded through the first mismatch). -/
theorem switch_π : "default:exception:r1".startsWith "default:switch:" = false := by
  unfold String.startsWith
  show Substring.beq _ _ = false
  simp only [Substring.beq, Substring.bsize, Substring.take, String.toSubstring, String.substrEq]
  iterate 9 (unfold_substrEq_loop; try simp only [])
  decide

/-- DF-π has no switch, so every structure has its switches off. -/
theorem switchesOff_π (B : VE.Structure.{0}) : SwitchesOff Dπ B := by
  have h : (dfltLabelled Dπ).filter (fun a => a.1.startsWith "default:switch:") = [] := by
    show [("default:exception:r1", _)].filter _ = []
    simp [switch_π]
  unfold SwitchesOff
  rw [h]
  exact fun _ h => nomatch h

/-! ### DF-π's one-element situations -/

def Mπ (on : List String) : VE.FiniteModel Entity where
  domains s := if s = "assistant" then [elemOf "assistant"] else []
  constants _ := none
  relations p := if p ∈ on then [[elemOf "assistant"]] else []
def Fπ (fon : List String) : FiniteFill Uπ Entity := fun n => if n ∈ fon then [[elemOf "assistant"]] else []
/-- The base predicates `on` true at the one assistant, and the unsaid tables `fon` filled yes there. -/
abbrev sitπ (on fon : List String) : VE.Structure.{0} := withFill Uπ (Mπ on).asStructure (finFill (Mπ on) (Fπ fon))

theorem unsaid_π : VE.NormDefaults.unsaidNames Uπ = [unsaidName "x_permitted", unsaidName "x_required"] := rfl
theorem exc_unsaid : excπ ∉ VE.NormDefaults.unsaidNames Uπ := by rw [unsaid_π]; decide

theorem rel_unsaid {on fon : List String} {n : String} (hn : n ∈ VE.NormDefaults.unsaidNames Uπ) (vs : List Entity) :
    (sitπ on fon).relation n vs ↔ n ∈ fon ∧ vs = a1 := by
  rw [unsaid_π] at hn
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hn
  rcases hn with rfl | rfl <;>
  · show (vs ∈ Fπ fon _ ∧ VE.TupleTyped (Mπ on).asStructure ["assistant"] vs) ↔ _
    unfold Fπ
    split <;> simp_all [VE.TupleTyped, VE.FiniteModel.asStructure, Mπ, a1]

theorem rel_base {on fon : List String} {n : String} (hn : n ∉ VE.NormDefaults.unsaidNames Uπ) (vs : List Entity) :
    (sitπ on fon).relation n vs ↔ n ∈ on ∧ vs = a1 := by
  have hf : Uπ.unspec.find? (fun p => unsaidName p == n) = none :=
    List.find?_eq_none.mpr fun q hq h => hn (List.mem_map.mpr ⟨q, hq, beq_iff_eq.mp h⟩)
  show (match Uπ.unspec.find? (fun p => unsaidName p == n) with
    | some p => vs ∈ Fπ fon n ∧ VE.TupleTyped (Mπ on).asStructure (VE.NormDefaults.sortsOf Uπ.D p) vs
    | none => vs ∈ (Mπ on).relations n) ↔ _
  rw [hf]
  show vs ∈ (if n ∈ on then [[elemOf "assistant"]] else []) ↔ _
  split <;> simp_all [a1]

theorem rel_π {on fon : List String} (n : String) (vs : List Entity) : (sitπ on fon).relation n vs ↔
    (if n ∈ VE.NormDefaults.unsaidNames Uπ then n ∈ fon else n ∈ on) ∧ vs = a1 := by
  split
  · exact rel_unsaid ‹_› vs
  · exact rel_base ‹_› vs

theorem typed_π (on fon : List String) : VE.TupleTyped (sitπ on fon) ["assistant"] a1 :=
  ⟨show elemOf "assistant" ∈ (if "assistant" = "assistant" then [elemOf "assistant"] else []) by simp, trivial⟩

open VE.NormDefaults.Wire (BaseAdmissibleX) in
/-- A situation whose filling passes `Fill_T` (`fillValid`, read through `eval_withFill`) is admissible with
    `softX`. -/
theorem admissible_π {on fon : List String} (hon : ∀ p ∈ on, p = excπ)
    (hf : VE.NormDefaults.fillValid Uπ (Mπ on) (Fπ fon) = true) : BaseAdmissibleX Uπ (softX Uπ Dπ []) (sitπ on fon) := by
  have hX : softX Uπ Dπ [] = [] := by decide
  have hpred : ∀ q ∈ Uπ.unspec, (VE.Norms.envAt (VE.NormDefaults.fill Uπ) 0).predicates (unsaidName q) =
      some ["assistant"] := by
    rw [Uπ_eq]; decide
  have hexc : (VE.Norms.envAt (VE.NormDefaults.fill Uπ) 0).predicates excπ = some ["assistant"] := by
    rw [Uπ_eq]; decide
  refine ⟨⟨⟨⟨fun c s h => (nomatch h), fun n vs h => ?_⟩, ?_⟩, fun φ hφ => ?_⟩, hX ▸ fun _ h => nomatch h⟩
  · by_cases hn : n ∈ VE.NormDefaults.unsaidNames Uπ
    · obtain ⟨-, rfl⟩ := (rel_unsaid hn vs).mp h
      obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hn
      exact ⟨_, hpred q hq, typed_π on fon⟩
    · obtain ⟨hn', rfl⟩ := (rel_base hn vs).mp h
      rw [hon n hn']
      exact ⟨_, hexc, typed_π on fon⟩
  · show VE.Norms.Sat _ (VE.Route.Background.literals [])
    simp [VE.Route.Background.literals, VE.Route.sortStrings, VE.Route.Background.pairs, VE.Norms.Sat]
  · exact (VE.NormDefaults.eval_withFill Uπ (Mπ on) (Fπ fon) φ []).mp (List.all_eq_true.mp hf φ hφ)

/-- A competitor `withOpen` on a situation is again a situation, when its tables are that situation's. -/
theorem open_π {on fon on' fon' : List String} (δ F : String → List Entity → Prop)
    (hδ : ∀ vs, δ excπ vs ↔ (sitπ on' fon').relation excπ vs)
    (hF : ∀ n ∈ VE.NormDefaults.unsaidNames Uπ, ∀ vs, F n vs ↔ (sitπ on' fon').relation n vs)
    (hon : ∀ n, n ≠ excπ → n ∉ VE.NormDefaults.unsaidNames Uπ → (n ∈ on ↔ n ∈ on')) :
    withOpen Uπ Dπ (sitπ on fon) δ F = sitπ on' fon' := by
  have key : ∀ n vs, (withOpen Uπ Dπ (sitπ on fon) δ F).relation n vs ↔ (sitπ on' fon').relation n vs := by
    intro n vs
    show (if n ∈ VE.SoftNorms.decisionNames Dπ then δ n vs else if n ∈ VE.NormDefaults.unsaidNames Uπ then F n vs
      else (sitπ on fon).relation n vs) ↔ _
    rw [decisionNames_π]
    by_cases h1 : n = excπ
    · subst h1; simp [hδ]
    · by_cases h2 : n ∈ VE.NormDefaults.unsaidNames Uπ
      · simp [h1, h2, hF n h2 vs]
      · simp only [List.mem_singleton, h1, h2, if_false, rel_base h2, hon n h1 h2]
  show VE.Structure.mk Entity (sitπ on fon).domain (sitπ on fon).constant
      (withOpen Uπ Dπ (sitπ on fon) δ F).relation =
    VE.Structure.mk Entity (sitπ on' fon').domain (sitπ on' fon').constant (sitπ on' fon').relation
  congr 1
  funext n vs
  exact propext (key n vs)

/-! ### The two `example`s -/

/-- Draft 1's `DefaultBase`, kept here for DF-π only: the competitor keeps `B`'s unsaid tables. -/
def DefaultBaseFixed (U : UDoc) (D : VE.SoftNorms.SoftDoc) (X : List VE.Formula) (B : VE.Structure.{0}) : Prop :=
  VE.NormDefaults.Wire.BaseAdmissibleX U X B ∧ SwitchesOff D B ∧
  ∀ δ : String → List B.Carrier → Prop,
    (∀ p ∈ VE.SoftNorms.decisionNames D, ∀ vs, δ p vs → B.relation p vs) →
    VE.NormDefaults.Wire.BaseAdmissibleX U X (withOpen U D B δ B.relation) →
    SwitchesOff D (withOpen U D B δ B.relation) →
    ∀ p ∈ VE.SoftNorms.decisionNames D, ∀ vs, B.relation p vs → δ p vs

/-- `B_π`: r1's exception at the one assistant, both gaps filled no. -/
abbrev Bπ : VE.Structure.{0} := sitπ [excπ] []

/-- Spec 8.5: `B_π` is a default base with the filling fixed. Its only competitor below it is `{}` with the
    fillings no/no, and `Fill_T` refuses that one. -/
example : DefaultBaseFixed Uπ Dπ (softX Uπ Dπ []) Bπ := by
  refine ⟨admissible_π (by simp) (by rw [Uπ_eq]; decide), switchesOff_π _, fun δ hle hadm _ p hp vs hB => ?_⟩
  rw [decisionNames_π, List.mem_singleton] at hp
  subst hp
  obtain ⟨-, rfl⟩ := (rel_π excπ vs).mp hB
  refine Classical.byContradiction fun hδ => ?_
  have heq : withOpen Uπ Dπ Bπ δ Bπ.relation = sitπ [] [] :=
    open_π δ _ (fun vs => ⟨fun h => absurd (by
        obtain ⟨-, rfl⟩ := (rel_π excπ vs).mp (hle _ (by simp [decisionNames_π]) vs h); exact h) hδ,
        fun h => by simp [rel_π, exc_unsaid] at h⟩)
      (fun n hn vs => by simp [rel_π, hn])
      (fun n h1 _ => by simp [h1])
  rw [heq] at hadm
  have hno : VE.NormDefaults.fillValid Uπ (Mπ []) (Fπ []) = false := by rw [Uπ_eq]; decide
  have hyes : VE.NormDefaults.fillValid Uπ (Mπ []) (Fπ []) = true := List.all_eq_true.mpr fun φ hφ =>
    (VE.NormDefaults.eval_withFill Uπ (Mπ []) (Fπ []) φ []).mpr (hadm.1.2 φ hφ)
  rw [hno] at hyes
  cases hyes

/-- Spec 8.5: `B_π` is not a default base (D15). The competitor `{}` with the permission's gap filled yes is
    admissible and has fewer decisions. -/
example : ¬ DefaultBase Uπ Dπ (softX Uπ Dπ []) Bπ := by
  intro ⟨_, _, hmin⟩
  have heq : withOpen Uπ Dπ Bπ (sitπ [] [unsaidName "x_permitted"]).relation
      (sitπ [] [unsaidName "x_permitted"]).relation = sitπ [] [unsaidName "x_permitted"] :=
    open_π _ _ (fun _ => Iff.rfl) (fun _ _ _ => Iff.rfl) (fun n h1 _ => by simp [h1])
  have hadm := admissible_π (on := []) (fon := [unsaidName "x_permitted"]) (by simp) (by rw [Uπ_eq]; decide)
  have h := hmin (sitπ [] [unsaidName "x_permitted"]).relation (sitπ [] [unsaidName "x_permitted"]).relation
    (fun p hp vs h => by rw [decisionNames_π, List.mem_singleton] at hp; subst hp; simp [rel_π, exc_unsaid] at h)
    (by rw [heq]; exact hadm) (switchesOff_π _) excπ (by simp [decisionNames_π]) a1
    ((rel_π excπ a1).mpr (by simp [exc_unsaid]))
  simp [rel_π, exc_unsaid] at h

end VE.Defaults.MeaningFixtures
