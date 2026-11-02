import VE.Acts.Faithful
import VE.Acts.ElaborateExamples

/-! Fixtures of `elaborate_faithful` (docs/spec/act-phrases.md 6.6, 11.3): both sides of the iff, computed on small
finite structures. `holdsB` and `intendedActsB` decide `holdsCatala` and `IntendedActs` there; `holdsB_iff` and
`intendedActsB_iff` tie them to the definitions, so each `#guard` is a fact about the theorem's two sides. -/

namespace VE.Acts.FaithfulExamples
open VE.Acts VE.Acts.ElaborateExamples VE.Acts.TableExamples VE.Norms VE.NormDefaults

abbrev Model := VE.FiniteModel Nat

/-- `forget ns` on a finite model. -/
def dropM (ns : List String) (M : Model) : Model :=
  { M with relations := fun r => if r ∈ ns then [] else M.relations r }
/-- `readAs p q` on a finite model. -/
def readM (p q : String) (M : Model) : Model :=
  { M with relations := fun r => if r = p then M.relations q else M.relations r }

theorem value_forget (T : Tree) (r : Regulated) (ns : List String) (M : Model) (vs : List Nat) :
    Value T r (forget ns M.asStructure) vs = Value T r (dropM ns M).asStructure vs := by
  have hR : (fun r vs => r ∉ ns ∧ vs ∈ M.relations r) = fun r vs => vs ∈ (dropM ns M).relations r := by
    funext r vs
    by_cases h : r ∈ ns <;> simp [dropM, h]
  exact congrArg (fun R => Value T r (⟨Nat, fun s v => v ∈ M.domains s, M.constants, R⟩ : VE.Structure) vs) hR

theorem readAs_asStructure (p q : String) (M : Model) : readAs p q M.asStructure = (readM p q M).asStructure := by
  simp only [readAs, VE.FiniteModel.asStructure, readM, VE.Structure.mk.injEq, heq_eq_eq, true_and]
  funext r vs
  by_cases h : r = p <;> simp [h]

section Eval
variable (T : Tree) (M : Model) (ρ : List Nat)

def appliesB (N : Node) : Bool := N.guard.eval M ρ && !N.carveOuts.any (·.eval M ρ)

def yieldsB : Nat → Node → Bool
  | 0, N => appliesB M ρ N
  | f + 1, N => appliesB M ρ N || (children T N).any (yieldsB f)

def selectsB (f : Nat) (N : Node) : Bool := appliesB M ρ N && !(children T N).any (yieldsB T M ρ f)

def decidesB (p : String) (sign : Bool) : Bool :=
  (rulesOn T p).any fun N => N.sign == sign && selectsB T M ρ (fuel T) N

theorem appliesB_iff (N : Node) : appliesB M ρ N = true ↔ AppliesD M.asStructure ρ N := by
  simp [appliesB, AppliesD, VE.eval_iff_denote]

theorem yieldsB_iff : ∀ (f : Nat) (N : Node), yieldsB T M ρ f N = true ↔ YieldsD T M.asStructure ρ f N
  | 0, N => by simp [yieldsB, YieldsD, appliesB_iff]
  | f + 1, N => by simp [yieldsB, YieldsD, appliesB_iff, yieldsB_iff f]

theorem selectsB_iff (f : Nat) (N : Node) : selectsB T M ρ f N = true ↔ SelectsD T M.asStructure ρ f N := by
  simp [selectsB, SelectsD, appliesB_iff, yieldsB_iff]

theorem decidesB_iff (p : String) (sign : Bool) :
    decidesB T M ρ p sign = true ↔ DecidesD T M.asStructure ρ p sign := by
  simp [decidesB, DecidesD, selectsB_iff]

end Eval

/-- `catalaValue` on two decided sides. -/
def valueB (P N d : Bool) : Option Bool := if P && N then none else if P then some true else if N then some false else some d

theorem value_eq (T : Tree) (r : Regulated) (M : Model) (vs : List Nat) :
    Value T r M.asStructure vs =
      valueB (decidesB T M (tupleVal vs) r.name true) (decidesB T M (tupleVal vs) r.name false) r.allowByDefault := by
  simp only [Value, catalaValue, valueB]
  have hp := decidesB_iff T M (tupleVal vs) r.name true
  have hn := decidesB_iff T M (tupleVal vs) r.name false
  cases hP : decidesB T M (tupleVal vs) r.name true <;> cases hN : decidesB T M (tupleVal vs) r.name false <;>
    simp_all

/-- The typed tuples of `ss`. -/
def tuples (M : Model) : List String → List (List Nat)
  | [] => [[]]
  | s :: ss => (M.domains s).flatMap fun v => (tuples M ss).map (v :: ·)

theorem mem_tuples (M : Model) : ∀ (ss : List String) (vs : List Nat),
    vs ∈ tuples M ss ↔ VE.TupleTyped M.asStructure ss vs
  | [], [] => by simp [tuples, VE.TupleTyped]
  | [], _ :: _ => by simp [tuples, VE.TupleTyped]
  | _ :: _, [] => by simp [tuples, VE.TupleTyped]
  | s :: ss, v :: vs => by
    simp only [tuples, List.mem_flatMap, List.mem_map, VE.TupleTyped, ← mem_tuples M ss vs]
    constructor
    · rintro ⟨w, hw, ws, hws, he⟩
      cases he
      exact ⟨hw, hws⟩
    · rintro ⟨hw, hws⟩
      exact ⟨v, hw, vs, hws, rfl⟩

/-- `IntendedAt`, read below `r.name` on every typed tuple. -/
def intendedB (T : Tree) (r : Regulated) (M : Model) : Bool :=
  (tuples M r.sorts).all fun vs =>
    let B := dropM [r.name] M
    match valueB (decidesB T B (tupleVal vs) r.name true) (decidesB T B (tupleVal vs) r.name false) r.allowByDefault with
    | some b => decide (vs ∈ M.relations r.name) == b
    | none => false

theorem intendedB_iff (T : Tree) (r : Regulated) (M : Model) : intendedB T r M = true ↔ IntendedAt T r M.asStructure := by
  simp only [intendedB, IntendedAt, List.all_eq_true, value_forget, value_eq, mem_tuples]
  apply forall_congr'
  intro vs
  apply imp_congr_right
  intro _
  cases valueB _ _ _ with
  | none => simp
  | some b => cases b <;> simp [VE.FiniteModel.asStructure]

def holdsB (T : Tree) (M : Model) : Bool := T.regulated.all (intendedB T · M)

theorem holdsB_iff (T : Tree) (M : Model) : holdsB T M = true ↔ holdsCatala T M.asStructure := by
  simp [holdsB, holdsCatala, intendedB_iff]

def intendedActsB (D : ActsDoc) (M : Model) : Bool :=
  D.U.D.T.regulated.all fun r => (partNames D r.name).all fun q => intendedB D.U.D.T r (readM r.name q M)

theorem intendedActsB_iff (D : ActsDoc) (M : Model) : intendedActsB D M = true ↔ IntendedActs D M.asStructure := by
  simp [intendedActsB, IntendedActs, intendedB_iff, readAs_asStructure]

/-- A model of one person with the relations `R` true of them. -/
def one (R : List String) : Model := ⟨fun _ => [0], fun _ => none, fun r => if r ∈ R then [[0]] else []⟩

/-- Both sides of the iff on `D`'s elaboration and `M`, or `none` when `D` is refused. -/
def sides (D : ActsDoc) (M : Model) : Option (Bool × Bool) :=
  (elaborate D).toOption.map fun U => (holdsB U.D.T M, intendedActsB D M)

/-! ### Rule on a part's name: the source is not well formed, the elaboration is accepted, and the sides differ -/

def ce : ActsDoc :=
  withActs (doc [rg "p027" .permission] [nd "r027" "p027" false, nd "r0" "p027__1" true]) fx6 [("p027", g6)]
#guard !VE.Norms.WellFormed ce.U.D
#guard (elaborate ce).toOption.map (fun U => WellFormedU U) == some true
#guard sides ce (one []) == some (false, true)

end VE.Acts.FaithfulExamples
