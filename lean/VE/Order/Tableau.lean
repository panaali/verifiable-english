import VE.Order.Linear

/-! Signed tableaux for order@0 with a Farkas closing rule.

Branch rules are the ordinary propositional and user-sort quantifier rules,
plus two arithmetic splits (a cut on a linear comparison, and t != u into
t < u or u < t). A branch closes by complementary formulas, by congruence of
predicate arguments (identical resolved tokens, identical linear terms, or a
certified t <= u and u <= t already on the branch; never a trusted
normalisation of terms), or by a Farkas combination with nonnegative integer
multipliers and Chvatal-Gomory (gcd) cuts summing to 0 <= -k with k > 0. -/
namespace VE.Order.Tableau
open VE.Order
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

/-- A linear combination: branch formula indices and earlier cut indices, each
with an integer multiplier. Nonnegativity is checked except for equalities. -/
structure Combo where
  literals : List (Nat × Int)
  cuts : List (Nat × Int)
  deriving Repr

structure Cut where
  combo : Combo
  divisor : Int
  deriving Repr

inductive Trace where
  | close
  | expand (index : Nat) (parameter : Option String) (children : List Trace)
  | split (formula : Formula) (children : List Trace)
  | neq (index : Nat) (children : List Trace)
  | farkas (cuts : List Cut) (final : Combo)
  deriving Repr

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
  deriving DecidableEq, Repr

structure Branch where
  formulas : List Signed
  witnesses : List String := []
  expanded : List Nat := []
  instantiated : List (Nat × Token) := []
  deriving Repr

def Token.sortOf (E : Environment) (b : Branch) : Token → Option SortName
  | .constant c => E.constants c
  | .witness i => b.witnesses[i]?.map SortName.user

abbrev Assignment (S : Structure.{u}) := Nat → Option S.Carrier

def Token.denote (S : Structure.{u}) (ρ : Assignment S) : Token → Option (Value S.Carrier)
  | .constant c => S.constant c
  | .witness i => (ρ i).map Sum.inl

def bindingsValue (S : Structure.{u}) (ρ : Assignment S) (ts : List Token) : Valuation S :=
  ts.filterMap (Token.denote S ρ)

def Signed.Holds (S : Structure.{u}) (ρ : Assignment S) (a : Signed) : Prop :=
  if a.positive then a.formula.denote S (bindingsValue S ρ a.bindings)
  else ¬ a.formula.denote S (bindingsValue S ρ a.bindings)

def Branch.Holds (S : Structure.{u}) (ρ : Assignment S) (b : Branch) : Prop :=
  ∀ a ∈ b.formulas, a.Holds S ρ

def Assignment.Typed (S : Structure.{u}) (b : Branch) (ρ : Assignment S) : Prop :=
  ∀ i s, b.witnesses[i]? = some s → ∃ v, ρ i = some v ∧ S.objects s v

def Token.scoped (n : Nat) : Token → Bool
  | .constant _ => true
  | .witness i => i < n

def Branch.scoped (b : Branch) : Bool :=
  b.formulas.all fun a => a.bindings.all (Token.scoped b.witnesses.length)

def Branch.known (E : Environment) (b : Branch) : Bool :=
  b.formulas.all fun a => a.bindings.all fun t => (t.sortOf E b).isSome

def extend {S : Structure.{u}} (ρ : Assignment S) (n : Nat) (v : S.Carrier) : Assignment S :=
  fun i => if i = n then some v else ρ i

theorem token_defined {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    {b : Branch} {ρ : Assignment S} (hρ : Assignment.Typed S b ρ)
    {t : Token} {s : SortName} (ht : t.sortOf E b = some s) :
    ∃ v, t.denote S ρ = some v ∧ S.domain s v := by
  cases t with
  | constant c => exact hS.1 c s ht
  | witness i =>
    simp only [Token.sortOf, Option.map_eq_some_iff] at ht
    obtain ⟨w, hw, rfl⟩ := ht
    obtain ⟨v, hv, ho⟩ := hρ i w hw
    exact ⟨.inl v, by simp [Token.denote, hv], ho⟩

theorem bindings_extend (S : Structure.{u}) (ρ : Assignment S) (n : Nat) (v : S.Carrier)
    (ts : List Token) (h : ts.all (Token.scoped n) = true) :
    bindingsValue S (extend ρ n v) ts = bindingsValue S ρ ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih =>
    simp only [List.all_cons, Bool.and_eq_true] at h
    have he : t.denote S (extend ρ n v) = t.denote S ρ := by
      cases t with
      | constant c => rfl
      | witness i =>
        have hi : i < n := by simpa [Token.scoped] using h.1
        simp [Token.denote, extend, Nat.ne_of_lt hi]
    simp only [bindingsValue, List.filterMap_cons, he]
    rw [show ts.filterMap (Token.denote S (extend ρ n v)) = ts.filterMap (Token.denote S ρ)
      from ih h.2]

theorem holds_extend (S : Structure.{u}) (ρ : Assignment S) (b : Branch)
    (v : S.Carrier) (hb : b.scoped = true) (hh : b.Holds S ρ) :
    b.Holds S (extend ρ b.witnesses.length v) := by
  intro a ha
  have he := bindings_extend S ρ b.witnesses.length v a.bindings
    (List.all_eq_true.mp hb a ha)
  simpa only [Signed.Holds, he] using hh a ha

theorem typed_extend (S : Structure.{u}) (ρ : Assignment S) (b : Branch)
    (hρ : Assignment.Typed S b ρ) (s : String) (v : S.Carrier) (hv : S.objects s v) :
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
  | one (additions : List Signed)
  | two (left right : Signed)
  | gamma (sort : String) (body : Formula)
  | delta (sort : String) (body : Formula)

def Signed.rule (a : Signed) : Rule :=
  let mk := fun f p => Signed.mk f p a.bindings
  match a.formula, a.positive with
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

def Branch.add (b : Branch) (xs : List Signed) : Branch :=
  { b with formulas := b.formulas ++ xs }

theorem add_holds (S : Structure.{u}) (ρ : Assignment S) (b : Branch) (xs : List Signed)
    (hb : b.Holds S ρ) (hx : ∀ a ∈ xs, a.Holds S ρ) : (b.add xs).Holds S ρ := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hb a ha
  · exact hx a ha

theorem one_holds (S : Structure.{u}) (ρ : Assignment S) (a : Signed) (xs : List Signed)
    (hr : a.rule = .one xs) (ha : a.Holds S ρ) : ∀ x ∈ xs, x.Holds S ρ := by
  rcases a with ⟨f, p, bs⟩
  cases f <;> cases p <;>
    simp only [Signed.rule, Rule.one.injEq, reduceCtorEq] at hr <;>
    try contradiction
  all_goals subst xs; simp_all [Signed.Holds, Formula.denote]

theorem two_holds (S : Structure.{u}) (ρ : Assignment S) (a x y : Signed)
    (hr : a.rule = .two x y) (ha : a.Holds S ρ) : x.Holds S ρ ∨ y.Holds S ρ := by
  classical
  rcases a with ⟨f, p, bs⟩
  cases f <;> cases p <;>
    simp_all [Signed.rule, Signed.Holds, Formula.denote] <;> grind

theorem object_of_domain {S : Structure.{u}} {s : String} {v : Value S.Carrier}
    (h : S.domain (.user s) v) : ∃ w, v = .inl w ∧ S.objects s w := by
  cases v with
  | inl w => exact ⟨w, rfl, h⟩
  | inr z => exact False.elim h

theorem gamma_holds (S : Structure.{u}) (ρ : Assignment S) (a : Signed) (s : String)
    (f : Formula) (t : Token) (v : Value S.Carrier)
    (hr : a.rule = .gamma s f) (ha : a.Holds S ρ)
    (ht : t.denote S ρ = some v) (hv : S.domain (.user s) v) :
    (Signed.mk f a.positive (t :: a.bindings)).Holds S ρ := by
  obtain ⟨w, rfl, hw⟩ := object_of_domain hv
  rcases a with ⟨a, p, bs⟩
  cases a <;> cases p <;>
    simp_all [Signed.rule, Signed.Holds, Formula.denote, bindingsValue] <;> grind

theorem delta_witness (S : Structure.{u}) (ρ : Assignment S) (a : Signed) (s : String)
    (f : Formula) (hr : a.rule = .delta s f) (ha : a.Holds S ρ) :
    ∃ v, S.objects s v ∧
      (if a.positive then f.denote S (.inl v :: bindingsValue S ρ a.bindings)
       else ¬ f.denote S (.inl v :: bindingsValue S ρ a.bindings)) := by
  classical
  rcases a with ⟨a, p, bs⟩
  cases a <;> cases p <;>
    simp_all [Signed.rule, Signed.Holds, Formula.denote] <;> grind

def next (E : Environment) (b : Branch) (index : Nat) (parameter : Option String) :
    Option (List Branch) := do
  let a ← b.formulas[index]?
  match a.rule with
  | .literal => none
  | .gamma s f => do
    let text ← parameter
    let t ← Token.parse text
    if t.sortOf E b ≠ some (.user s) || (index, t) ∈ b.instantiated then none else
      some [({ b with instantiated := (index, t) :: b.instantiated }).add
        [⟨f, a.positive, t :: a.bindings⟩]]
  | rule =>
    if parameter.isSome || index ∈ b.expanded then none else
      let b' := { b with expanded := index :: b.expanded }
      match rule with
      | .one xs => some [b'.add xs]
      | .two x y => some [b'.add [x], b'.add [y]]
      | .delta s f => some [({ b' with witnesses := b.witnesses ++ [s] }).add
          [⟨f, a.positive, .witness b.witnesses.length :: a.bindings⟩]]
      | _ => none

theorem next_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hs : b.scoped = true) (hh : b.Holds S ρ)
    (index : Nat) (parameter : Option String) (bs : List Branch)
    (hn : next E b index parameter = some bs) :
    ∃ child ∈ bs, ∃ σ, Assignment.Typed S child σ ∧ child.Holds S σ := by
  cases ha : b.formulas[index]? with
  | none => simp [next, ha] at hn
  | some a =>
    have ham : a ∈ b.formulas := List.mem_of_getElem? ha
    have hah := hh a ham
    cases hr : a.rule with
    | literal => simp [next, ha, hr] at hn
    | gamma s f =>
      cases hp : parameter with
      | none => simp [next, ha, hr, hp] at hn
      | some text =>
        cases ht : Token.parse text with
        | none => simp [next, ha, hr, hp, ht] at hn
        | some t =>
          simp only [next, ha, hr, hp, ht, bind, Option.bind] at hn
          split at hn
          next => contradiction
          next hg =>
            have hsort : t.sortOf E b = some (.user s) := by
              have hg' : t.sortOf E b = some (.user s) ∧ (index, t) ∉ b.instantiated := by
                simpa using hg
              exact hg'.1
            obtain ⟨v, hv, hd⟩ := token_defined hS hρ hsort
            cases hn
            refine ⟨_, List.mem_cons_self, ρ, hρ, ?_⟩
            apply add_holds S ρ { b with instantiated := (index, t) :: b.instantiated } _ hh
            simpa using gamma_holds S ρ a s f t v hr hah hv hd
    | one xs =>
      simp only [next, ha, hr, bind, Option.bind] at hn
      split at hn
      next => contradiction
      next =>
        cases hn
        refine ⟨_, List.mem_cons_self, ρ, hρ, ?_⟩
        exact add_holds S ρ { b with expanded := index :: b.expanded } xs hh
          (one_holds S ρ a xs hr hah)
    | two x y =>
      simp only [next, ha, hr, bind, Option.bind] at hn
      split at hn
      next => contradiction
      next =>
        cases hn
        rcases two_holds S ρ a x y hr hah with hx | hy
        · refine ⟨_, List.mem_cons_self, ρ, hρ, ?_⟩
          exact add_holds S ρ { b with expanded := index :: b.expanded } [x] hh (by simpa)
        · refine ⟨_, List.mem_cons_of_mem _ (List.mem_cons_self), ρ, hρ, ?_⟩
          exact add_holds S ρ _ [y] hh (by simpa)
    | delta s f =>
      simp only [next, ha, hr, bind, Option.bind] at hn
      split at hn
      next => contradiction
      next =>
        cases hn
        obtain ⟨v, hv, hf⟩ := delta_witness S ρ a s f hr hah
        let σ := extend ρ b.witnesses.length v
        refine ⟨_, List.mem_cons_self, σ, ?_, ?_⟩
        · exact typed_extend S ρ b hρ s v hv
        apply add_holds S σ { b with witnesses := b.witnesses ++ [s], expanded := index :: b.expanded }
          _ (holds_extend S ρ b v hs hh)
        intro x hx
        have hx' : x = ⟨f, a.positive, .witness b.witnesses.length :: a.bindings⟩ := by simpa using hx
        subst x
        have hb := bindings_extend S ρ b.witnesses.length v a.bindings
          (List.all_eq_true.mp hs a ham)
        have hvalue : bindingsValue S σ (.witness b.witnesses.length :: a.bindings) =
            .inl v :: bindingsValue S ρ a.bindings := by
          have he : Token.denote S σ (.witness b.witnesses.length) = some (.inl v) := by
            simp [Token.denote, σ, extend]
          simp only [bindingsValue, List.filterMap_cons, he]
          exact congrArg (List.cons (.inl v)) hb
        simpa only [Signed.Holds, hvalue] using hf

/-! Arithmetic literals as linear constraints `0 ≤ p` (or `0 = p` for equalities). -/

def constraint (E : Environment) (a : Signed) : Option (Lin × Bool) :=
  match a.formula, a.positive with
  | .le t u, true => match linearize E t, linearize E u with
    | some x, some y => some (y.sub x, false)
    | _, _ => none
  | .lt t u, true => match linearize E t, linearize E u with
    | some x, some y => some ((y.sub x).shift (-1), false)
    | _, _ => none
  | .le t u, false => match linearize E t, linearize E u with
    | some x, some y => some ((x.sub y).shift (-1), false)
    | _, _ => none
  | .lt t u, false => match linearize E t, linearize E u with
    | some x, some y => some (x.sub y, false)
    | _, _ => none
  | .eq t u, true => match linearize E t, linearize E u with
    | some x, some y => some (y.sub x, true)
    | _, _ => none
  | _, _ => none

theorem compare_ints {α : Type u} (R : Int → Int → Prop) (x y : Int) :
    Compare (α := α) R (some (.inr x)) (some (.inr y)) ↔ R x y := by
  simp [Compare]

theorem constraint_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (ρ : Assignment S) (a : Signed) (p : Lin) (e : Bool) (h : a.Holds S ρ)
    (hc : constraint E a = some (p, e)) :
    0 ≤ p.eval (intValue S) ∧ (e = true → p.eval (intValue S) = 0) := by
  rcases a with ⟨f, pos, bs⟩
  simp only [Signed.Holds] at h
  cases f <;> cases pos <;> simp only [constraint, reduceCtorEq] at hc
  all_goals
    split at hc
    next x y hx hy =>
      simp only [Option.some.injEq, Prod.mk.injEq] at hc
      obtain ⟨rfl, rfl⟩ := hc
      simp only [if_true, if_false, Bool.false_eq_true] at h
      simp only [Formula.denote, linearize_denote hS _ _ x hx,
        linearize_denote hS _ _ y hy, compare_ints, Option.some.injEq,
        exists_eq_left', Sum.inr.injEq] at h
      simp only [Lin.eval_sub, Lin.eval_shift, Bool.false_eq_true, false_implies,
        and_true, forall_const]
      omega
    next => contradiction

def addLiterals (E : Environment) (b : Branch) : List (Nat × Int) → Option Lin
  | [] => some Lin.zero
  | (i, k) :: rest =>
    match b.formulas[i]? with
    | none => none
    | some a => match constraint E a with
      | none => none
      | some (p, e) =>
        if e || decide (0 ≤ k) then
          match addLiterals E b rest with
          | some r => some ((p.smul k).add r)
          | none => none
        else none

def addCuts (derived : List Lin) : List (Nat × Int) → Option Lin
  | [] => some Lin.zero
  | (j, k) :: rest =>
    match derived[j]? with
    | none => none
    | some q =>
      if decide (0 ≤ k) then
        match addCuts derived rest with
        | some r => some ((q.smul k).add r)
        | none => none
      else none

def comboLin (E : Environment) (b : Branch) (derived : List Lin) (c : Combo) : Option Lin :=
  match addLiterals E b c.literals, addCuts derived c.cuts with
  | some x, some y => some (x.add y)
  | _, _ => none

theorem addLiterals_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hh : b.Holds S ρ) (xs : List (Nat × Int)) (L : Lin)
    (h : addLiterals E b xs = some L) : 0 ≤ L.eval (intValue S) := by
  induction xs generalizing L with
  | nil =>
    simp only [addLiterals, Option.some.injEq] at h
    subst h
    simp [Lin.eval_zero]
  | cons item rest ih =>
    obtain ⟨i, k⟩ := item
    simp only [addLiterals] at h
    split at h
    next => contradiction
    next a ha =>
      split at h
      next => contradiction
      next p e hc =>
        split at h
        next hk =>
          split at h
          next r hr =>
            simp only [Option.some.injEq] at h
            subst h
            have hp := constraint_sound hS ρ a p e (hh a (List.mem_of_getElem? ha)) hc
            have hrest := ih r hr
            rw [Lin.eval_add, Lin.eval_smul]
            rcases Bool.or_eq_true_iff.mp hk with he | hk
            · rw [hp.2 he]
              simp only [Int.mul_zero, Int.zero_add]
              exact hrest
            · have hk' : 0 ≤ k := of_decide_eq_true hk
              have := Int.mul_nonneg hk' hp.1
              omega
          next => contradiction
        next => contradiction

theorem addCuts_sound (κ : String → Int) (derived : List Lin)
    (hd : ∀ q ∈ derived, 0 ≤ q.eval κ) (xs : List (Nat × Int)) (L : Lin)
    (h : addCuts derived xs = some L) : 0 ≤ L.eval κ := by
  induction xs generalizing L with
  | nil =>
    simp only [addCuts, Option.some.injEq] at h
    subst h
    simp [Lin.eval_zero]
  | cons item rest ih =>
    obtain ⟨j, k⟩ := item
    simp only [addCuts] at h
    split at h
    next => contradiction
    next q hq =>
      split at h
      next hk =>
        split at h
        next r hr =>
          simp only [Option.some.injEq] at h
          subst h
          have hq' := hd q (List.mem_of_getElem? hq)
          have hrest := ih r hr
          rw [Lin.eval_add, Lin.eval_smul]
          have := Int.mul_nonneg (of_decide_eq_true hk) hq'
          omega
        next => contradiction
      next => contradiction

theorem comboLin_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hh : b.Holds S ρ) (derived : List Lin)
    (hd : ∀ q ∈ derived, 0 ≤ q.eval (intValue S)) (c : Combo) (L : Lin)
    (h : comboLin E b derived c = some L) : 0 ≤ L.eval (intValue S) := by
  simp only [comboLin] at h
  split at h
  next x y hx hy =>
    simp only [Option.some.injEq] at h
    subst h
    rw [Lin.eval_add]
    have := addLiterals_sound hS b ρ hh c.literals x hx
    have := addCuts_sound (intValue S) derived hd c.cuts y hy
    omega
  next => contradiction

/-- Cuts are processed in order; each may use the literals and earlier cuts. -/
def runCuts (E : Environment) (b : Branch) : List Lin → List Cut → Option (List Lin)
  | derived, [] => some derived
  | derived, c :: cs =>
    match comboLin E b derived c.combo with
    | none => none
    | some L =>
      let N := L.normal
      if decide (0 < c.divisor) && N.coeffs.all (fun p => p.2 % c.divisor == 0) then
        runCuts E b (derived ++ [divideLin c.divisor N]) cs
      else none

theorem runCuts_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hh : b.Holds S ρ) (cs : List Cut) (derived result : List Lin)
    (hd : ∀ q ∈ derived, 0 ≤ q.eval (intValue S))
    (h : runCuts E b derived cs = some result) : ∀ q ∈ result, 0 ≤ q.eval (intValue S) := by
  induction cs generalizing derived with
  | nil =>
    simp only [runCuts, Option.some.injEq] at h
    subst h
    exact hd
  | cons c cs ih =>
    simp only [runCuts] at h
    split at h
    next => contradiction
    next L hL =>
      split at h
      next hg =>
        obtain ⟨hpos, hdiv⟩ := Bool.and_eq_true_iff.mp hg
        apply ih _ _ h
        intro q hq
        rcases List.mem_append.mp hq with hq | hq
        · exact hd q hq
        · have hq' : q = divideLin c.divisor L.normal := by simpa using hq
          subst hq'
          apply tighten_sound _ _ _ (of_decide_eq_true hpos) hdiv
          rw [Lin.eval_normal]
          exact comboLin_sound hS b ρ hh derived hd c.combo L hL
      next => contradiction

def farkasCloses (E : Environment) (b : Branch) (cuts : List Cut) (final : Combo) : Bool :=
  match runCuts E b [] cuts with
  | none => false
  | some derived =>
    match comboLin E b derived final with
    | none => false
    | some L => L.normal.coeffs.all (fun p => p.2 == 0) && decide (L.normal.const < 0)

theorem farkas_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hh : b.Holds S ρ) (cuts : List Cut) (final : Combo)
    (h : farkasCloses E b cuts final = true) : False := by
  simp only [farkasCloses] at h
  split at h
  next => contradiction
  next derived hd =>
    have hderived := runCuts_sound hS b ρ hh cuts [] derived (by simp) hd
    split at h
    next => contradiction
    next L hL =>
      obtain ⟨hz, hneg⟩ := Bool.and_eq_true_iff.mp h
      have hnonneg := comboLin_sound hS b ρ hh derived hderived final L hL
      rw [← Lin.eval_normal] at hnonneg
      simp only [Lin.eval, sumTerms_zero _ _ hz] at hnonneg
      have := of_decide_eq_true hneg
      omega

/-! Arithmetic branching rules. -/

def splitAtom (E : Environment) : Formula → Bool
  | .le t u | .lt t u => (linearize E t).isSome && (linearize E u).isSome
  | _ => false

def neqSplit (E : Environment) (b : Branch) (index : Nat) : Option (List Branch) :=
  match b.formulas[index]? with
  | some ⟨.eq t u, false, bs⟩ =>
    if (linearize E t).isSome && (linearize E u).isSome then
      some [b.add [⟨.lt t u, true, bs⟩], b.add [⟨.lt u t, true, bs⟩]]
    else none
  | _ => none

theorem neqSplit_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hh : b.Holds S ρ) (index : Nat) (bs : List Branch)
    (hn : neqSplit E b index = some bs) : ∃ child ∈ bs, child.Holds S ρ := by
  simp only [neqSplit] at hn
  split at hn
  next t u ts ha =>
    split at hn
    next hl =>
      obtain ⟨ht, hu⟩ := Bool.and_eq_true_iff.mp hl
      obtain ⟨x, hx⟩ := Option.isSome_iff_exists.mp ht
      obtain ⟨y, hy⟩ := Option.isSome_iff_exists.mp hu
      simp only [Option.some.injEq] at hn
      subst hn
      have hne := hh _ (List.mem_of_getElem? ha)
      simp only [Signed.Holds, Bool.false_eq_true, if_false, Formula.denote,
        linearize_denote hS _ _ x hx, linearize_denote hS _ _ y hy, Option.some.injEq,
        exists_eq_left', Sum.inr.injEq] at hne
      rcases Int.lt_or_gt_of_ne (Ne.symm hne) with hlt | hgt
      · refine ⟨_, List.mem_cons_self, add_holds S ρ b _ hh ?_⟩
        intro a ha
        simp only [List.mem_singleton] at ha
        subst ha
        simp [Signed.Holds, Formula.denote, linearize_denote hS _ _ x hx,
          linearize_denote hS _ _ y hy, compare_ints, hlt]
      · refine ⟨_, List.mem_cons_of_mem _ List.mem_cons_self, add_holds S ρ b _ hh ?_⟩
        intro a ha
        simp only [List.mem_singleton] at ha
        subst ha
        simp [Signed.Holds, Formula.denote, linearize_denote hS _ _ x hx,
          linearize_denote hS _ _ y hy, compare_ints, hgt]
    next => contradiction
  next => contradiction

/-! Closing by complementary literals, with explicit argument-equality evidence. -/

def termToken (bs : List Token) : Term → Option Token
  | .const c => some (.constant c)
  | .var i => bs[i]?
  | _ => none

def closedTerm : Term → Bool
  | .var _ => false
  | .const _ | .num _ => true
  | .add t u => closedTerm t && closedTerm u
  | .scale _ t => closedTerm t

theorem closed_denote (S : Structure.{u}) (ρ σ : Valuation S) (t : Term) (h : closedTerm t = true) :
    t.denote S ρ = t.denote S σ := by
  induction t with
  | var i => simp [closedTerm] at h
  | const c => rfl
  | num z => rfl
  | add t u it iu =>
    simp only [closedTerm, Bool.and_eq_true] at h
    simp [Term.denote, it h.1, iu h.2]
  | scale k t it =>
    simp only [closedTerm] at h
    simp [Term.denote, it h]

def hasLe (b : Branch) (t u : Term) : Bool :=
  b.formulas.any fun a => a.positive && decide (a.formula = .le t u)

/-- One positive object equality between the two resolved tokens (either order). -/
def objectEq (b : Branch) (x y : Token) : Bool :=
  b.formulas.any fun a => a.positive && match a.formula with
    | .eq t u => match termToken a.bindings t, termToken a.bindings u with
      | some x', some y' => (decide (x' = x) && decide (y' = y)) || (decide (x' = y) && decide (y' = x))
      | _, _ => false
    | _ => false

def sameValue (E : Environment) (b : Branch) (bs : List Token) (t : Term)
    (cs : List Token) (u : Term) : Bool :=
  (match termToken bs t, termToken cs u with
    | some x, some y => ((x.sortOf E b).isSome && decide (x = y)) || objectEq b x y
    | _, _ => false) ||
  (decide (t = u) && (linearize E t).isSome) ||
  (closedTerm t && closedTerm u && hasLe b t u && hasLe b u t)

theorem bindings_get (S : Structure.{u}) (ρ : Assignment S) (bs : List Token)
    (hb : ∀ t ∈ bs, ∃ v, t.denote S ρ = some v) (i : Nat) :
    (bindingsValue S ρ bs)[i]? = (bs[i]?).bind (Token.denote S ρ) := by
  induction bs generalizing i with
  | nil => simp [bindingsValue]
  | cons t ts ih =>
    obtain ⟨v, hv⟩ := hb t (by simp)
    have hh := ih (fun t ht => hb t (by simp [ht]))
    cases i with
    | zero => simp [bindingsValue, hv]
    | succ i => simpa [bindingsValue, hv] using hh i

theorem termToken_denote (S : Structure.{u}) (ρ : Assignment S) (bs : List Token)
    (hb : ∀ t ∈ bs, ∃ v, t.denote S ρ = some v) (t : Term) (x : Token)
    (ht : termToken bs t = some x) :
    t.denote S (bindingsValue S ρ bs) = x.denote S ρ := by
  cases t with
  | const c => cases ht; rfl
  | var i =>
    rw [Term.denote, bindings_get S ρ bs hb, show bs[i]? = some x from ht]
    rfl
  | num z => simp [termToken] at ht
  | add t u => simp [termToken] at ht
  | scale k t => simp [termToken] at ht

/-- On a known branch under a typed assignment, every binding token is defined. -/
def Defined (S : Structure.{u}) (ρ : Assignment S) (b : Branch) : Prop :=
  ∀ a ∈ b.formulas, ∀ t ∈ a.bindings, ∃ v, t.denote S ρ = some v

theorem known_defined {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ) (hk : b.known E = true) :
    Defined S ρ b := by
  intro a ha t ht
  have hi := List.all_eq_true.mp (List.all_eq_true.mp hk a ha) t ht
  cases hs : t.sortOf E b with
  | none => simp [hs] at hi
  | some s =>
    obtain ⟨v, hv, _⟩ := token_defined hS hρ hs
    exact ⟨v, hv⟩

theorem objectEq_sound (S : Structure.{u}) (ρ : Assignment S) (b : Branch)
    (hh : b.Holds S ρ) (hd : Defined S ρ b) (x y : Token) (h : objectEq b x y = true) :
    ∃ v, x.denote S ρ = some v ∧ y.denote S ρ = some v := by
  obtain ⟨a, ha, hx⟩ := List.any_eq_true.mp h
  obtain ⟨hp, hm⟩ := Bool.and_eq_true_iff.mp hx
  have hholds := hh a ha
  simp only [Signed.Holds, hp, if_true] at hholds
  split at hm
  next t u hf =>
    rw [hf] at hholds
    split at hm
    next x' y' htx hty =>
      obtain ⟨v, hv1, hv2⟩ := hholds
      rw [termToken_denote S ρ _ (hd a ha) t x' htx] at hv1
      rw [termToken_denote S ρ _ (hd a ha) u y' hty] at hv2
      rcases Bool.or_eq_true_iff.mp hm with hm | hm
      · obtain ⟨h1, h2⟩ := Bool.and_eq_true_iff.mp hm
        have h1 := of_decide_eq_true h1
        have h2 := of_decide_eq_true h2
        subst h1 h2
        exact ⟨v, hv1, hv2⟩
      · obtain ⟨h1, h2⟩ := Bool.and_eq_true_iff.mp hm
        have h1 := of_decide_eq_true h1
        have h2 := of_decide_eq_true h2
        subst h1 h2
        exact ⟨v, hv2, hv1⟩
    next => contradiction
  next => contradiction

theorem hasLe_sound (S : Structure.{u}) (ρ : Assignment S) (b : Branch)
    (hh : b.Holds S ρ) (t u : Term) (h : hasLe b t u = true) :
    ∃ σ : Valuation S, Compare (· ≤ ·) (t.denote S σ) (u.denote S σ) := by
  obtain ⟨a, ha, hx⟩ := List.any_eq_true.mp h
  obtain ⟨hp, hf⟩ := Bool.and_eq_true_iff.mp hx
  have hholds := hh a ha
  simp only [Signed.Holds, hp, if_true, of_decide_eq_true hf, Formula.denote] at hholds
  exact ⟨_, hholds⟩

theorem sameValue_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ) (hh : b.Holds S ρ)
    (hd : Defined S ρ b) (bs cs : List Token)
    (hbs : ∀ t ∈ bs, ∃ v, t.denote S ρ = some v) (hcs : ∀ t ∈ cs, ∃ v, t.denote S ρ = some v)
    (t u : Term) (h : sameValue E b bs t cs u = true) :
    ∃ v, t.denote S (bindingsValue S ρ bs) = some v ∧
      u.denote S (bindingsValue S ρ cs) = some v := by
  simp only [sameValue, Bool.or_eq_true] at h
  rcases h with (h | h) | h
  · split at h
    next x y hx hy =>
      rw [termToken_denote S ρ bs hbs t x hx, termToken_denote S ρ cs hcs u y hy]
      rcases Bool.or_eq_true_iff.mp h with h | h
      · obtain ⟨hk, he⟩ := Bool.and_eq_true_iff.mp h
        have he := of_decide_eq_true he
        subst he
        obtain ⟨s, hs⟩ := Option.isSome_iff_exists.mp hk
        obtain ⟨v, hv, _⟩ := token_defined hS hρ hs
        exact ⟨v, hv, hv⟩
      · exact objectEq_sound S ρ b hh hd x y h
    next => contradiction
  · obtain ⟨he, hl⟩ := Bool.and_eq_true_iff.mp h
    have he := of_decide_eq_true he
    subst he
    obtain ⟨L, hL⟩ := Option.isSome_iff_exists.mp hl
    exact ⟨_, linearize_denote hS _ t L hL, linearize_denote hS _ t L hL⟩
  · obtain ⟨⟨⟨htc, huc⟩, h1⟩, h2⟩ := And.intro (And.intro (Bool.and_eq_true_iff.mp
      (Bool.and_eq_true_iff.mp (Bool.and_eq_true_iff.mp h).1).1)
      (Bool.and_eq_true_iff.mp (Bool.and_eq_true_iff.mp h).1).2) (Bool.and_eq_true_iff.mp h).2
    obtain ⟨σ1, hc1⟩ := hasLe_sound S ρ b hh t u h1
    obtain ⟨σ2, hc2⟩ := hasLe_sound S ρ b hh u t h2
    rw [closed_denote S σ1 (bindingsValue S ρ bs) t htc,
      closed_denote S σ1 (bindingsValue S ρ cs) u huc] at hc1
    rw [closed_denote S σ2 (bindingsValue S ρ cs) u huc,
      closed_denote S σ2 (bindingsValue S ρ bs) t htc] at hc2
    obtain ⟨x, y, hx, hy, hxy⟩ := hc1
    obtain ⟨y', x', hy', hx', hyx⟩ := hc2
    rw [hx] at hx'
    rw [hy] at hy'
    cases hx'
    cases hy'
    have : x = y := by omega
    subst this
    exact ⟨_, hx, hy⟩

def complementary (E : Environment) (b : Branch) (p n : Signed) : Bool :=
  p.positive && !n.positive &&
    ((decide (p.formula = n.formula) && decide (p.bindings = n.bindings)) ||
    match p.formula, n.formula with
    | .unary q t, .unary r u => decide (q = r) && sameValue E b p.bindings t n.bindings u
    | .binary q t1 t2, .binary r u1 u2 => decide (q = r) &&
        sameValue E b p.bindings t1 n.bindings u1 && sameValue E b p.bindings t2 n.bindings u2
    | _, _ => false)

def selfClosed (E : Environment) (b : Branch) (a : Signed) : Bool :=
  match a.formula, a.positive with
  | .bottom, true => true
  | .top, false => true
  | .eq t u, false => sameValue E b a.bindings t a.bindings u
  | _, _ => false

def closed (E : Environment) (b : Branch) : Bool :=
  b.formulas.any (selfClosed E b) ||
    b.formulas.any (fun p => b.formulas.any (fun n => complementary E b p n))

theorem closed_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ) (hk : b.known E = true)
    (hh : b.Holds S ρ) (hc : closed E b = true) : False := by
  have hd := known_defined hS b ρ hρ hk
  rcases Bool.or_eq_true_iff.mp hc with hc | hc
  · obtain ⟨a, ha, hs⟩ := List.any_eq_true.mp hc
    have hholds := hh a ha
    rcases a with ⟨f, pos, bs⟩
    cases f <;> cases pos <;> simp only [selfClosed, reduceCtorEq] at hs <;>
      simp only [Signed.Holds, Formula.denote, Bool.false_eq_true, if_false, if_true] at hholds
    all_goals first
      | exact hholds trivial
      | exact hholds
      | exact hholds (sameValue_sound hS b ρ hρ hh hd bs bs (hd _ ha) (hd _ ha) _ _ hs)
  · obtain ⟨p, hp, hx⟩ := List.any_eq_true.mp hc
    obtain ⟨n, hn, hpn⟩ := List.any_eq_true.mp hx
    have hph := hh p hp
    have hnh := hh n hn
    obtain ⟨⟨hpos, hneg⟩, hm⟩ := And.intro (Bool.and_eq_true_iff.mp
      (Bool.and_eq_true_iff.mp hpn).1) (Bool.and_eq_true_iff.mp hpn).2
    have hneg : n.positive = false := by simpa using hneg
    simp only [Signed.Holds, hpos, hneg, if_true, Bool.false_eq_true, if_false] at hph hnh
    rcases Bool.or_eq_true_iff.mp hm with hm | hm
    · obtain ⟨hf, hb⟩ := Bool.and_eq_true_iff.mp hm
      rw [of_decide_eq_true hf, of_decide_eq_true hb] at hph
      exact hnh hph
    · split at hm
      next q t r u hpf hnf =>
        obtain ⟨hq, hs⟩ := Bool.and_eq_true_iff.mp hm
        have hq := of_decide_eq_true hq
        subst hq
        rw [hpf] at hph
        rw [hnf] at hnh
        obtain ⟨v, hv, hsame⟩ := sameValue_sound hS b ρ hρ hh hd p.bindings n.bindings
          (hd p hp) (hd n hn) t u hs
        obtain ⟨w, hw, hr⟩ := hph
        rw [hv] at hw
        cases hw
        exact hnh ⟨v, hsame, hr⟩
      next q t1 t2 r u1 u2 hpf hnf =>
        obtain ⟨⟨hq, hs1⟩, hs2⟩ := And.intro (Bool.and_eq_true_iff.mp
          (Bool.and_eq_true_iff.mp hm).1) (Bool.and_eq_true_iff.mp hm).2
        have hq := of_decide_eq_true hq
        subst hq
        rw [hpf] at hph
        rw [hnf] at hnh
        obtain ⟨v1, hv1, hsame1⟩ := sameValue_sound hS b ρ hρ hh hd p.bindings n.bindings
          (hd p hp) (hd n hn) t1 u1 hs1
        obtain ⟨v2, hv2, hsame2⟩ := sameValue_sound hS b ρ hρ hh hd p.bindings n.bindings
          (hd p hp) (hd n hn) t2 u2 hs2
        obtain ⟨w1, w2, hw1, hw2, hr⟩ := hph
        rw [hv1] at hw1
        rw [hv2] at hw2
        cases hw1
        cases hw2
        exact hnh ⟨v1, v2, hsame1, hsame2, hr⟩
      next => contradiction

def checkChildren (check : Branch → Trace → Bool) : List Branch → List Trace → Bool
  | [], [] => true
  | b :: bs, t :: ts => check b t && checkChildren check bs ts
  | _, _ => false

theorem checkChildren_member (check : Branch → Trace → Bool) (bs : List Branch)
    (ts : List Trace) (hc : checkChildren check bs ts = true) :
    ∀ b ∈ bs, ∃ t, check b t = true := by
  induction bs generalizing ts with
  | nil => simp
  | cons b bs ih =>
    cases ts with
    | nil => contradiction
    | cons t ts =>
      have hc' : check b t = true ∧ checkChildren check bs ts = true := by
        simpa [checkChildren] using hc
      intro x hx
      rcases List.mem_cons.mp hx with rfl | hx
      · exact ⟨t, hc'.1⟩
      · exact ih ts hc'.2 x hx

def splitBranches (b : Branch) (f : Formula) : List Branch :=
  [b.add [⟨f, true, []⟩], b.add [⟨f, false, []⟩]]

/-- Fuel bounds depth. Exhaustion rejects; it never accepts. -/
def replay (E : Environment) : Nat → Branch → Trace → Bool
  | 0, _, _ => false
  | fuel + 1, b, t =>
    b.scoped && b.known E && match t with
      | .close => closed E b
      | .farkas cuts final => farkasCloses E b cuts final
      | .expand index parameter children =>
        match next E b index parameter with
        | none => false
        | some bs => checkChildren (replay E fuel) bs children
      | .split f children =>
        splitAtom E f && checkChildren (replay E fuel) (splitBranches b f) children
      | .neq index children =>
        match neqSplit E b index with
        | none => false
        | some bs => checkChildren (replay E fuel) bs children

theorem replay_sound {E : Environment} {S : Structure.{u}} (hS : S.Admissible E)
    (fuel : Nat) (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hh : b.Holds S ρ) (t : Trace) (hc : replay E fuel b t = true) : False := by
  induction fuel generalizing b ρ t with
  | zero => contradiction
  | succ fuel ih =>
    have hc' := Bool.and_eq_true_iff.mp hc
    obtain ⟨hs, hk⟩ := Bool.and_eq_true_iff.mp hc'.1
    have hrest := hc'.2
    cases t with
    | close => exact closed_sound hS b ρ hρ hk hh hrest
    | farkas cuts final => exact farkas_sound hS b ρ hh cuts final hrest
    | expand index parameter children =>
      cases hn : next E b index parameter with
      | none => simp [hn] at hrest
      | some bs =>
        have hchildren : checkChildren (replay E fuel) bs children = true := by
          simpa [hn] using hrest
        obtain ⟨child, hm, σ, ht, hh⟩ := next_sound hS b ρ hρ hs hh index parameter bs hn
        obtain ⟨t, hc⟩ := checkChildren_member (replay E fuel) bs children hchildren child hm
        exact ih child σ ht hh t hc
    | split f children =>
      obtain ⟨_, hchildren⟩ := Bool.and_eq_true_iff.mp hrest
      have hpick : ∃ child ∈ splitBranches b f, child.Holds S ρ := by
        by_cases hf : f.denote S (bindingsValue S ρ [])
        · refine ⟨_, List.mem_cons_self, add_holds S ρ b _ hh ?_⟩
          intro a ha
          simp only [List.mem_singleton] at ha
          subst ha
          simpa [Signed.Holds] using hf
        · refine ⟨_, List.mem_cons_of_mem _ List.mem_cons_self, add_holds S ρ b _ hh ?_⟩
          intro a ha
          simp only [List.mem_singleton] at ha
          subst ha
          simpa [Signed.Holds] using hf
      obtain ⟨child, hm, hch⟩ := hpick
      obtain ⟨t, hc⟩ := checkChildren_member (replay E fuel) _ children hchildren child hm
      have hct : Assignment.Typed S child ρ := by
        simp only [splitBranches, List.mem_cons, List.not_mem_nil, or_false] at hm
        rcases hm with rfl | rfl <;> exact hρ
      exact ih child ρ hct hch t hc
    | neq index children =>
      cases hn : neqSplit E b index with
      | none => simp [hn] at hrest
      | some bs =>
        have hchildren : checkChildren (replay E fuel) bs children = true := by
          simpa [hn] using hrest
        obtain ⟨child, hm, hch⟩ := neqSplit_sound hS b ρ hh index bs hn
        obtain ⟨t, hc⟩ := checkChildren_member (replay E fuel) bs children hchildren child hm
        have hct : Assignment.Typed S child ρ := by
          simp only [neqSplit] at hn
          split at hn
          next =>
            split at hn
            next =>
              simp only [Option.some.injEq] at hn
              subst hn
              simp only [List.mem_cons, List.not_mem_nil, or_false] at hm
              rcases hm with rfl | rfl <;> exact hρ
            next => contradiction
          next => contradiction
        exact ih child ρ hct hch t hc

def initial (premises : List Formula) (conclusion : Formula) : Branch :=
  ⟨premises.map (fun f => ⟨f, true, []⟩) ++ [⟨conclusion, false, []⟩], [], [], []⟩

def checkerVersion : String := "ve-order-farkas-checker@1"

/-- The logical checker uses exact AST inputs; identity binding is a wire gate. -/
def checkCertificate (E : Environment) (premises : List Formula) (conclusion : Formula)
    (c : Certificate) : Bool :=
  c.checker_version == checkerVersion &&
    premises.all (fun f => f.check E []) && conclusion.check E [] &&
    replay E 125 (initial premises conclusion) c.trace

/-- Sound over every admissible order structure at every universe, with
standard unbounded integers. There is no certificate-soundness premise. -/
theorem checkCertificate_sound (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Certificate)
    (hc : checkCertificate E premises conclusion c = true) :
    Entails.{u} E premises conclusion := by
  classical
  intro S hS hp
  apply Classical.byContradiction
  intro hn
  have hr : replay E 125 (initial premises conclusion) c.trace = true :=
    (Bool.and_eq_true_iff.mp hc).2
  apply replay_sound hS 125 (initial premises conclusion) (fun _ => none) _ _ c.trace hr
  · intro i s hi
    simp [initial] at hi
  · intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · obtain ⟨f, hm, rfl⟩ := List.mem_map.mp ha
      exact hp f hm
    · have he : a = ⟨conclusion, false, []⟩ := by simpa using ha
      subst a
      exact hn

end VE.Order.Tableau
