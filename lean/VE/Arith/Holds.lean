import VE.Arith.Syntax

/-! The meaning of `arith@0` (spec 12.1, debate F4): `Term.value` and `Holds` are defined together and neither refers
to an evaluator; a count is the number of values for which `Holds` of its condition is decided true, by classical
decision. A definition is interpreted in the environment of the definitions before it (`Defs.env`). -/

namespace VE.Arith

/-- The meaning of each defined name. -/
structure Env where
  funs : String → Option (Nat × (List Int → Option Int))
  preds : String → Option (Nat × (List Int → Prop))

open Classical in
mutual
/-- Variables are de Bruijn indices into `ρ`; a count is the number of `i` from `lo` through `hi` for which `Holds`
of its condition is decided true, by classical decision. Neither function mentions an evaluator. -/
noncomputable def Term.value (E : Env) (ρ : List Int) : Term → Option Int
  | .var i => ρ[i]?
  | .num n => some n
  | .add a b => match Term.value E ρ a, Term.value E ρ b with
    | some x, some y => some (x + y)
    | _, _ => none
  | .sub a b => match Term.value E ρ a, Term.value E ρ b with
    | some x, some y => some (x - y)
    | _, _ => none
  | .mul a b => match Term.value E ρ a, Term.value E ρ b with
    | some x, some y => some (x * y)
    | _, _ => none
  | .call f args => match E.funs f, Term.values E ρ args with
    | some (n, g), some xs => if xs.length = n then g xs else none
    | _, _ => none
  | .countFromTo lo hi φ => match Term.value E ρ lo, Term.value E ρ hi with
    | some l, some h =>
      some ((((List.range (h - l + 1).toNat).filter fun (i : Nat) =>
        decide (Holds E ((l + (i : Int)) :: ρ) φ)).length : Nat) : Int)
    | _, _ => none
noncomputable def Term.values (E : Env) (ρ : List Int) : List Term → Option (List Int)
  | [] => some []
  | t :: ts => match Term.value E ρ t, Term.values E ρ ts with
    | some x, some xs => some (x :: xs)
    | _, _ => none
noncomputable def Holds (E : Env) (ρ : List Int) : Formula → Prop
  | .eq a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x = y
  | .lt a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x < y
  | .le a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x ≤ y
  | .dvd a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x ∣ y
  | .call p args => ∃ n P xs, E.preds p = some (n, P) ∧ Term.values E ρ args = some xs ∧
      xs.length = n ∧ P xs
  | .not φ => ¬ Holds E ρ φ
  | .and φ ψ => Holds E ρ φ ∧ Holds E ρ ψ
  | .or φ ψ => Holds E ρ φ ∨ Holds E ρ ψ
  | .imp φ ψ => Holds E ρ φ → Holds E ρ ψ
  | .allNat φ => ∀ n : Nat, Holds E ((n : Int) :: ρ) φ
  | .exNat φ => ∃ n : Nat, Holds E ((n : Int) :: ρ) φ
  | .allInt φ => ∀ n : Int, Holds E (n :: ρ) φ
  | .exInt φ => ∃ n : Int, Holds E (n :: ρ) φ
  | .allFromTo lo hi φ => ∃ l h, Term.value E ρ lo = some l ∧ Term.value E ρ hi = some h ∧
      ∀ i : Int, l ≤ i → i ≤ h → Holds E (i :: ρ) φ
  | .exFromTo lo hi φ => ∃ l h, Term.value E ρ lo = some l ∧ Term.value E ρ hi = some h ∧
      ∃ i : Int, l ≤ i ∧ i ≤ h ∧ Holds E (i :: ρ) φ
end

noncomputable def Defs.env (D : Defs) : Env :=
  D.foldl (fun E d => match d with
    | .fn f n body => { E with funs := fun g => if g = f then some (n, fun xs => Term.value E xs body) else E.funs g }
    | .pred p n body => { E with preds := fun q => if q = p then some (n, fun xs => Holds E xs body) else E.preds q })
    ⟨fun _ => none, fun _ => none⟩

def Defs.Means (D : Defs) (φ : Formula) : Prop := Holds D.env [] φ

end VE.Arith
