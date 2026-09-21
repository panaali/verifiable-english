import VE.Closure.Substitution
import VE.Typing

/-! Data-only signed tableaux. Witness indices name fresh branch-local parameters;
no inhabitant of any sort is chosen by the executable. -/
namespace VE.Closure.Tableau
universe u

inductive Token where
  | constant (name : String)
  | witness (index : Nat)
  deriving DecidableEq, Repr

def Token.parse (text : String) : Option Token :=
  if text.startsWith "c:" then some (.constant (text.drop 2))
  else if text.startsWith "w:" then do
    let n ← (text.drop 2).toNat?
    if text = "w:" ++ toString n then some (.witness n) else none
  else none

inductive Trace where
  | close
  | expand (rule : String) (index : Nat) (parameter : Option String) (children : List Trace)
  deriving Repr

/-- The five fields shared by ve-tableau-checker@1 and @2. Hash bindings are checked by the
wire adapter; semantic replay always uses the actual supplied ASTs and E. -/
structure Certificate where
  checker_version : String
  environment_id : String
  premise_meaning_ids : List String
  conclusion_meaning_id : String
  trace : Trace
  deriving Repr

structure Signed where
  formula : Formula
  positive : Bool
  bindings : List Token := []
  deriving DecidableEq, BEq, Repr

structure Branch where
  formulas : List Signed
  witnesses : List String := []
  expanded : List Nat := []
  instantiated : List (Nat × Token) := []
  deriving Repr

def Token.sortOf (E : Environment) (b : Branch) : Token → Option String
  | .constant c => E.constants c
  | .witness i => b.witnesses[i]?

abbrev Assignment (S : Structure.{u}) := Nat → Option S.Carrier

def Token.denote (S : Structure) (ρ : Assignment S) : Token → Option S.Carrier
  | .constant c => S.constant c
  | .witness i => ρ i

def bindingsValue (S : Structure) (ρ : Assignment S) (ts : List Token) : Valuation S :=
  ts.filterMap (Token.denote S ρ)

def Signed.Holds (S : Structure) (ρ : Assignment S) (a : Signed) : Prop :=
  if a.positive then a.formula.denote S (bindingsValue S ρ a.bindings)
  else ¬ a.formula.denote S (bindingsValue S ρ a.bindings)

def Branch.Holds (S : Structure) (ρ : Assignment S) (b : Branch) : Prop :=
  ∀ a ∈ b.formulas, a.Holds S ρ

def Assignment.Typed (S : Structure) (b : Branch) (ρ : Assignment S) : Prop :=
  ∀ i s, b.witnesses[i]? = some s → ∃ v, ρ i = some v ∧ S.domain s v

def Token.scoped (n : Nat) : Token → Bool
  | .constant _ => true
  | .witness i => i < n

def Branch.scoped (b : Branch) : Bool :=
  b.formulas.all fun a => a.bindings.all (Token.scoped b.witnesses.length)

def extend (ρ : Assignment S) (n : Nat) (v : S.Carrier) : Assignment S :=
  fun i => if i = n then some v else ρ i

theorem token_defined {E : Environment} {S : Structure} (hS : S.Admissible E)
    {b : Branch} {ρ : Assignment S} (hρ : Assignment.Typed S b ρ)
    {t : Token} {s : String} (ht : t.sortOf E b = some s) :
    ∃ v, t.denote S ρ = some v ∧ S.domain s v := by
  cases t with
  | constant c => exact hS.1 c s ht
  | witness i => exact hρ i s ht

theorem bindings_extend (S : Structure) (ρ : Assignment S) (n : Nat) (v : S.Carrier)
    (ts : List Token) (h : ts.all (Token.scoped n) = true) :
    bindingsValue S (extend ρ n v) ts = bindingsValue S ρ ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih =>
    have hs := (List.all_eq_true.mp h t (by simp))
    have ht : ts.all (Token.scoped n) = true := by simpa only [List.all_cons, Bool.and_eq_true] using (show Token.scoped n t = true ∧ ts.all (Token.scoped n) = true from by simpa using h).2
    have he : t.denote S (extend ρ n v) = t.denote S ρ := by
      cases t with
      | constant c => rfl
      | witness i =>
        have hi : i < n := by simpa [Token.scoped] using hs
        simp [Token.denote, extend, Nat.ne_of_lt hi]
    simp only [bindingsValue, List.filterMap_cons, he]
    rw [show ts.filterMap (Token.denote S (extend ρ n v)) = ts.filterMap (Token.denote S ρ) from ih ht]

theorem holds_extend (S : Structure) (ρ : Assignment S) (b : Branch)
    (v : S.Carrier) (hb : b.scoped = true) (hh : b.Holds S ρ) :
    b.Holds S (extend ρ b.witnesses.length v) := by
  intro a ha
  have he := bindings_extend S ρ b.witnesses.length v a.bindings
    (List.all_eq_true.mp hb a ha)
  simpa only [Signed.Holds, he] using hh a ha

theorem typed_extend (S : Structure) (ρ : Assignment S) (b : Branch)
    (hρ : Assignment.Typed S b ρ) (s : String) (v : S.Carrier) (hv : S.domain s v) :
    Assignment.Typed S { b with witnesses := b.witnesses ++ [s] }
      (extend ρ b.witnesses.length v) := by
  intro i r hi
  by_cases h : i < b.witnesses.length
  · have hi' : b.witnesses[i]? = some r := by
      simpa [List.getElem?_append, h] using hi
    obtain ⟨w, hw, hr⟩ := hρ i r hi'
    exact ⟨w, by simp [extend, Nat.ne_of_lt h, hw], hr⟩
  · have hi' : i = b.witnesses.length ∧ s = r := by
      have hx : i - b.witnesses.length = 0 ∧ s = r := by
        simpa [List.getElem?_append, h, List.getElem?_singleton] using hi
      exact ⟨by omega, hx.2⟩
    rcases hi' with ⟨rfl, rfl⟩
    exact ⟨v, by simp [extend], hv⟩

inductive Rule where
  | literal
  | closure (kind : Kind) (edge : Edge) (left right : Term)
  | one (additions : List Signed)
  | two (left right : Signed)
  | gamma (sort : String) (body : Formula)
  | delta (sort : String) (body : Formula)

def Signed.rule (a : Signed) : Rule :=
  let mk := fun f p => Signed.mk f p a.bindings
  match a.formula, a.positive with
  | .reachNamed k r t u, _ => .closure k (.named r) t u
  | .reachBody k s f t u, _ => .closure k (.body s f) t u
  | .not f, p => .one [mk f (!p)]
  | .and f g, true => .one [mk f true, mk g true]
  | .and f g, false => .two (mk f false) (mk g false)
  | .or f g, false => .one [mk f false, mk g false]
  | .or f g, true => .two (mk f true) (mk g true)
  | .implies f g, false => .one [mk f true, mk g false]
  | .implies f g, true => .two (mk f false) (mk g true)
  | .all s f, true | .ex s f, false => .gamma s f
  | .all s f, false | .ex s f, true => .delta s f
  | _, _ => .literal

def Signed.tag (a : Signed) : String :=
  match a.formula with
  | .reachNamed .plus .. | .reachBody .plus .. => "closure-plus@0"
  | .reachNamed .star .. | .reachBody .star .. => "closure-star@0"
  | _ => "expand"

def Branch.add (b : Branch) (xs : List Signed) : Branch :=
  { b with formulas := b.formulas ++ xs }

theorem add_holds (S : Structure) (ρ : Assignment S) (b : Branch) (xs : List Signed)
    (hb : b.Holds S ρ) (hx : ∀ a ∈ xs, a.Holds S ρ) :
    (b.add xs).Holds S ρ := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hb a ha
  · exact hx a ha

theorem one_holds (S : Structure) (ρ : Assignment S) (a : Signed) (xs : List Signed)
    (hr : a.rule = .one xs) (ha : a.Holds S ρ) : ∀ x ∈ xs, x.Holds S ρ := by
  rcases a with ⟨f, p, bs⟩
  cases f <;> cases p <;>
    simp only [Signed.rule, Rule.one.injEq, reduceCtorEq] at hr <;>
    try contradiction
  all_goals subst xs; simp_all [Signed.Holds, Formula.denote]

theorem two_holds (S : Structure) (ρ : Assignment S) (a x y : Signed)
    (hr : a.rule = .two x y) (ha : a.Holds S ρ) : x.Holds S ρ ∨ y.Holds S ρ := by
  classical
  rcases a with ⟨f, p, bs⟩
  cases f <;> cases p <;>
    simp_all [Signed.rule, Signed.Holds, Formula.denote] <;> grind

theorem gamma_holds (S : Structure) (ρ : Assignment S) (a : Signed) (s : String)
    (f : Formula) (t : Token) (v : S.Carrier)
    (hr : a.rule = .gamma s f) (ha : a.Holds S ρ)
    (ht : t.denote S ρ = some v) (hv : S.domain s v) :
    (Signed.mk f a.positive (t :: a.bindings)).Holds S ρ := by
  rcases a with ⟨a, p, bs⟩
  cases a <;> cases p <;>
    simp_all [Signed.rule, Signed.Holds, Formula.denote,
      bindingsValue] <;> grind

theorem delta_witness (S : Structure) (ρ : Assignment S) (a : Signed) (s : String)
    (f : Formula) (hr : a.rule = .delta s f) (ha : a.Holds S ρ) :
    ∃ v, S.domain s v ∧
      (if a.positive then f.denote S (v :: bindingsValue S ρ a.bindings)
       else ¬ f.denote S (v :: bindingsValue S ρ a.bindings)) := by
  classical
  rcases a with ⟨a, p, bs⟩
  cases a <;> cases p <;>
    simp_all [Signed.rule, Signed.Holds, Formula.denote] <;> grind

end VE.Closure.Tableau
