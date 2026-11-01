import VE.Weighing.Zone
import VE.Defaults.Examples

/-! Fixtures for weighing's zone interface (weighing-PLAN 3.4). `decisionAtoms` and `openNames` are read on
defeasible's decoded DF-α document (one default rule: one decision predicate, one unspecified regulated predicate).
`AdmissibleCompletion`, `OutcomeIn` and `SettledZ` are read on `U0`, a literal the kernel reduces: sorts `s`,
predicates `q` and `x`, `x` a permission allowed by default with no rule, nothing unspecified. -/
namespace VE.Weighing.ZoneFixtures
open VE.Weighing
open VE.Defaults.Fixtures (dα holds Entity)

/-! ## `decisionAtoms` and `openNames` -/

def a1 : Entity := ("assistant", "e_a1")
def a2 : Entity := ("assistant", "e_a2")
/-- A two-element situation. -/
def M2 : VE.FiniteModel Entity := ⟨fun s => if s == "assistant" then [a1, a2] else [], fun _ => none, fun _ => []⟩

-- One decision predicate at both tuples, in order.
#guard holds dα fun L => VE.SoftNorms.decisions L.D == [("soft__excepted__r1", ["assistant"])] &&
  decisionAtoms L.D M2 == [("soft__excepted__r1", [a1]), ("soft__excepted__r1", [a2])]
-- One decision name, then one unsaid name.
#guard holds dα fun L => VE.SoftNorms.decisionNames L.D == ["soft__excepted__r1"] &&
  VE.NormDefaults.unsaidNames L.U == ["unsaid__x_required"] &&
  openNames L == VE.SoftNorms.decisionNames L.D ++ VE.NormDefaults.unsaidNames L.U &&
  openNames L == ["soft__excepted__r1", "unsaid__x_required"]

/-- Two default rules, and both regulated predicates unspecified: two decision names and two unsaid names. -/
def dTwo : Except String VE.NormDefaults.Wire.LayeredU :=
  VE.Defaults.Fixtures.layered (VE.Defaults.Fixtures.envJ [VE.Defaults.Fixtures.xReq,
      VE.Defaults.Fixtures.regJ "x_permitted" "[\"assistant\"]" "permission" "unspecified" ",\"act\":\"{0} do x\""]
    VE.Defaults.Fixtures.strictSoft)
  [VE.Defaults.Fixtures.ruleJ "r1" "x_required" true VE.Defaults.Fixtures.dfltJ,
   VE.Defaults.Fixtures.ruleJ "r2" "x_permitted" true VE.Defaults.Fixtures.dfltJ]

-- Every decision predicate at every tuple, predicate by predicate; every decision name, then every unsaid name.
#guard holds dTwo fun L => decisionAtoms L.D M2 == [("soft__excepted__r1", [a1]), ("soft__excepted__r1", [a2]),
    ("soft__excepted__r2", [a1]), ("soft__excepted__r2", [a2])] &&
  openNames L == ["soft__excepted__r1", "soft__excepted__r2", "unsaid__x_permitted", "unsaid__x_required"]

/-! ## Completions, outcomes and settledness on `U0` -/

def rx : VE.Norms.Regulated := ⟨"x", ["s"], true, .permission, some "{0} do x", none⟩
def ry : VE.Norms.Regulated := ⟨"y", ["s"], true, .permission, some "{0} do y", none⟩

def U0 : VE.NormDefaults.UDoc where
  D := { E := { sorts := ["s"], predicates := fun p => if p = "q" ∨ p = "x" then some ["s"] else none,
                constants := fun _ => none },
         lits := [], T := { regulated := [rx], definitions := [], nodes := [] } }
  unspec := []

def M0 : VE.FiniteModel Nat := ⟨fun s => if s = "s" then [0, 1] else [], fun _ => none, fun _ => []⟩
/-- `q` holds of `0` only. -/
def R0 (n : String) (vs : List Nat) : Prop := n = "q" ∧ vs = [0]
def rec0 : List ((String × List Nat) × Bool) := [(("q", [0]), true)]

theorem admissible0 : AdmissibleCompletion U0 [] M0 ["q"] rec0 R0 := by
  refine ⟨fun n vs hn => ?_, fun a b h => ?_, ⟨⟨⟨⟨fun c s h => ?_, fun p vs h => ?_⟩, ?_⟩, ?_⟩, ?_⟩⟩
  · simp only [List.mem_singleton] at hn; simp [R0, M0, hn]
  · simp only [rec0, List.mem_singleton, Prod.mk.injEq] at h; obtain ⟨rfl, rfl⟩ := h; simp [R0]
  · exact absurd h (by rw [show (VE.Norms.envAt (VE.NormDefaults.fill U0) 0).constants c = none from rfl]; simp)
  · obtain ⟨rfl, rfl⟩ := h
    exact ⟨["s"], by decide, by simp [VE.TupleTyped, VE.FiniteModel.asStructure, M0]⟩
  · intro a ha
    simp [VE.Norms.backgroundBase, VE.Route.Background.literals, U0, VE.NormDefaults.fill, VE.Route.sortStrings,
      VE.Route.Background.pairs] at ha
  · intro a ha; simp [VE.NormDefaults.fillPremises, VE.Norms.pairs, U0] at ha
  · intro a ha; simp at ha

-- The record says `q(1)`, which `R0` denies.
theorem notAdmissible1 : ¬ AdmissibleCompletion U0 [] M0 ["q"] [(("q", [1]), true)] R0 :=
  fun ⟨_, h, _⟩ => by simpa [R0] using (h ("q", [1]) true (List.mem_singleton_self _)).mpr rfl

-- Each outcome is computed through `OutcomeIn` by `decide`: `x` is allowed by default, `y` is not regulated.
theorem outcome_x : OutcomeIn U0 M0 R0 rx [0] := by
  unfold OutcomeIn; generalize hφ : VE.Norms.outcomeBase _ _ = φ
  obtain rfl : φ = .not .bottom := by rw [← hφ]; decide
  simp [VE.Formula.denote]

theorem not_outcome_y : ¬ OutcomeIn U0 M0 R0 ry [0] := by
  unfold OutcomeIn; generalize hφ : VE.Norms.outcomeBase _ _ = φ
  obtain rfl : φ = .bottom := by rw [← hφ]; decide
  simp [VE.Formula.denote]

theorem settled_x : SettledZ U0 [] M0 ["q"] rec0 rx [0] true := by
  refine ⟨⟨R0, admissible0⟩, fun R _ => ?_⟩
  unfold OutcomeIn; generalize hφ : VE.Norms.outcomeBase _ _ = φ
  obtain rfl : φ = .not .bottom := by rw [← hφ]; decide
  simp [VE.Formula.denote]

theorem not_settled_x_false : ¬ SettledZ U0 [] M0 ["q"] rec0 rx [0] false :=
  fun ⟨_, h⟩ => by simpa using (h R0 admissible0).mp outcome_x

-- Not vacuously: a record that says `q(0)` both ways has no completion, so nothing is settled.
theorem not_settled_vacuous (b : Bool) :
    ¬ SettledZ U0 [] M0 ["q"] [(("q", [0]), true), (("q", [0]), false)] rx [0] b :=
  fun ⟨⟨R, _, h, _⟩, _⟩ => by
    have h₁ := h ("q", [0]) true (by simp); have h₂ := h ("q", [0]) false (by simp)
    simp at h₁ h₂; exact h₂ h₁

/-! ## `ZoneUnknown` -/

example : ZoneUnknown Nat := .budget 13 12
example : ZoneUnknown Nat := .branch [(("q", [0]), true)] "none checked"
example : ZoneUnknown.budget (α := Nat) 13 12 ≠ .branch [] "none checked" := ZoneUnknown.noConfusion

end VE.Weighing.ZoneFixtures
