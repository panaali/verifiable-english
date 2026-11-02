import VE.Acts.Faithful
import VE.Acts.DecodeExamples

/-! Fixtures of `elaborate_faithful` (docs/spec/act-phrases.md 6.6, 11.3): both sides of the iff, computed on small
finite structures. `holdsB` and `intendedActsB` decide `holdsCatala` and `IntendedActs` there; `holdsB_iff` and
`intendedActsB_iff` tie them to the definitions, so each `#guard` is a fact about the theorem's two sides. -/

namespace VE.Acts.FaithfulExamples
open VE.Acts VE.Acts.ElaborateExamples VE.Acts.TableExamples VE.Norms VE.NormDefaults Lean

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

/-- `readAs` itself on a finite model, for the checks below (the sides read it through `readM`). -/
instance readAsDecidable (p q r : String) (M : Model) (vs : List Nat) :
    Decidable ((readAs p q M.asStructure).relation r vs) := by
  dsimp only [readAs, VE.FiniteModel.asStructure]
  exact inferInstance
-- The source reads as the part, and no longer as itself; every other name, before or after it, reads as itself.
#guard decide ((readAs "p" "q" (one ["q"]).asStructure).relation "p" [0])
#guard !decide ((readAs "p" "q" (one ["p"]).asStructure).relation "p" [0])
#guard decide ((readAs "p" "q" (one ["a"]).asStructure).relation "a" [0])
#guard !decide ((readAs "p" "q" (one ["q"]).asStructure).relation "a" [0])
#guard decide ((readAs "p" "q" (one ["s"]).asStructure).relation "s" [0])
#guard !decide ((readAs "p" "q" (one ["q"]).asStructure).relation "s" [0])

/-- Both sides of the iff on `D`'s elaboration and `M`, or `none` when `D` is refused. -/
def sides (D : ActsDoc) (M : Model) : Option (Bool × Bool) :=
  (elaborate D).toOption.map fun U => (holdsB U.D.T M, intendedActsB D M)

/-- A model of two people, `R` listing whom each relation is true of. -/
def people (R : List (String × List Nat)) : Model :=
  ⟨fun _ => [0, 1], fun _ => none, fun r => ((R.lookup r).getD []).map ([·])⟩

def parts027 : List String := ["p027__1", "p027__2"]
def bx : VE.Formula := .unary "b" (.var 0)

/-! ### E11's check: the two sides agree, each way, on every shape of rule -/

-- Spec 11.3: torture's prohibition holds and cruel treatment's fails: both false; both hold: both true.
#guard sides e1 (one ["p027__2"]) == some (false, false)
#guard sides e1 (one ["p027__1"]) == some (false, false)
#guard sides e1 (one []) == some (true, true)
-- One person of two breaks one part; a relation on no predicate of the rules, and the source's own name, are not read.
#guard sides e1 (people [("p027__2", [1])]) == some (false, false)
#guard sides e1 (people [("p027__1", [0])]) == some (false, false)
#guard sides e1 (people [("b", [0, 1]), ("p027", [0])]) == some (true, true)
-- The last of five parts counts as the first does.
#guard sides e3 (one ["p123__5"]) == some (false, false)
#guard sides e3 (one ["p123__1"]) == some (false, false)
#guard sides e3 (one []) == some (true, true)

-- Precedence on each part (E4): the exception decides; without `over` the two rules conflict, on every model.
#guard sides e4 (one parts027) == some (true, true)
#guard sides e4 (one ["p027__1"]) == some (false, false)
#guard sides e4 (one []) == some (false, false)
def conflict : ActsDoc :=
  withActs (doc [rg "p027" .permission] [nd "r027" "p027" false, nd "r027b" "p027" true]) fx6 [("p027", g6)]
#guard sides conflict (one parts027) == some (false, false)
#guard sides conflict (one []) == some (false, false)

/-- Three rules deep: the source's fuel is 3, the result's 6. -/
def chain : ActsDoc := withActs (doc [rg "p027" .permission]
  [nd "a" "p027" false, nd "c" "p027" true ["a"] bx, nd "d" "p027" false ["c"] (.unary "e" (.var 0))]
  (extra := ["b", "e"])) fx6 [("p027", g6)]
#guard sides chain (one ("b" :: parts027)) == some (true, true)
#guard sides chain (one ["b"]) == some (false, false)
#guard sides chain (one ["b", "e"]) == some (true, true)
#guard sides chain (one ("b" :: "e" :: parts027)) == some (false, false)
#guard sides chain (one []) == some (true, true)
#guard sides chain (one ["e", "p027__1"]) == some (false, false)

/-- Allowed by default; the rule prohibits when `b` holds, or unless `b` holds. -/
def allowed (N : Node) : ActsDoc :=
  withActs (doc [{ rg "p027" .permission with allowByDefault := true }] [N] (extra := ["b"])) fx6 [("p027", g6)]
def guarded : ActsDoc := allowed (nd "r027" "p027" false (guard := bx))
def carved : ActsDoc := allowed (nd "r027" "p027" false (carveOuts := [bx]))
#guard sides guarded (one parts027) == some (true, true)
#guard sides guarded (one ["b"]) == some (true, true)
#guard sides guarded (one ("b" :: parts027)) == some (false, false)
#guard sides guarded (one []) == some (false, false)
#guard sides carved (one ("b" :: parts027)) == some (true, true)
#guard sides carved (one []) == some (true, true)
#guard sides carved (one parts027) == some (false, false)

-- A predicate with no parts, beside one that splits, is read as itself.
def mix : ActsDoc := withActs (doc [rg "p027" .permission, rg "s" .obligation]
  [nd "r027" "p027" false, nd "rs" "s" true (guard := bx)] (extra := ["b"])) fx6 [("p027", g6)]
#guard sides mix (one ["s", "b"]) == some (true, true)
#guard sides mix (one []) == some (true, true)
#guard sides mix (one ["s"]) == some (false, false)
#guard sides mix (one ["b"]) == some (false, false)
#guard sides mix (one ["s", "b", "p027__1"]) == some (false, false)
-- One atom kept (E2); unspecified predicates, split and kept (E5).
#guard sides e2 (one ["p079"]) == some (true, true)
#guard sides e2 (one []) == some (false, false)
#guard sides e5 (one ["k"]) == some (true, true)
#guard sides e5 (one []) == some (false, false)
#guard sides e5 (one ["k", "p027__2"]) == some (false, false)
-- D3's revised cell: two readings, refused, so the theorem says nothing of it.
#guard sides e17 (one []) == none

/-! ### The twin: a decoded document (acts are lexical until the hook of ap-3db) -/

def decodedSides (j : Json) (ns : List Json) (M : Model) : Option (Bool × Bool) :=
  (Decode.decodeElaboratedU j (Json.arr ns.toArray)).toOption.map fun e => (holdsB e.U'.D.T M, intendedActsB e.D M)
def jdoc := VE.Acts.DecodeExamples.jenv ["acts@0", "norms@0", "relational-fol@0"] VE.Acts.DecodeExamples.lexical
#guard decodedSides jdoc [VE.Acts.DecodeExamples.jrule "p"] (one ["p", "q"]) == some (true, true)
#guard decodedSides jdoc [VE.Acts.DecodeExamples.jrule "p"] (one ["p"]) == some (false, false)

/-! ### The hypothesis `h0` is needed: a source that is not well formed, a rule on a part's name

`elaborate` accepts it and the result is well formed, but the two sides differ: `r0` conflicts with `r027-a1` on the
part, and `IntendedActs` never reads `r0`, which is on no source predicate (reviews/dri-decisions-20261102-ap-3dd.md).
Every other document in this file is well formed. -/

def ce : ActsDoc :=
  withActs (doc [rg "p027" .permission] [nd "r027" "p027" false, nd "r0" "p027__1" true]) fx6 [("p027", g6)]
#guard !VE.Norms.WellFormed ce.U.D
#guard (elaborate ce).toOption.map (fun U => WellFormedU U) == some true
#guard sides ce (one []) == some (false, true)
#guard [e1, e3, e4, conflict, chain, guarded, carved, mix, e2, e5].all (VE.Norms.WellFormed ·.U.D)

end VE.Acts.FaithfulExamples
