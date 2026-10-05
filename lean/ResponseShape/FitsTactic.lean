import ResponseShape.Skeletons
import Lean.Elab.Tactic

/-! # Tactics for the encoder theorems

* `okfits` goes through a runner's `do` block (binds, keeping each `x = .ok a`; conditions;
  matches; join points) down to each returned value, left as a `Fits` goal.
* `fits` proves `Fits Γ k v` for a value built from `Json.mkObj` with literal field names,
  arrays of mapped lists, and values `k` says nothing about. At an alternative it picks, by the
  object's field names, the first object skeleton whose fields they pass (`fits_pick`, decided
  here on the literals; the choice is then checked by the kernel). It leaves as goals what it
  cannot decide (a field value that depends on the encoder's data).
* `alt_mem` proves `s ∈ ss` for a member of a literal list, and `alt_sub` that every member of
  one alternative is a member of another (a runner that delegates to another mode's runner).
* `fits_as "file.json#/pointer"` narrows `Fits Γ (.alt ss) v` to the member that is the
  skeleton of that shape.

The tactics only build proofs: the kernel checks each, so a wrong choice fails the build. -/

namespace ResponseShape
open Lean

macro "keys_ok" : tactic =>
  `(tactic|(simp only [List.map_cons, List.map_nil, List.map_append, List.cons_append, List.nil_append, List.append_nil]; decide))

/-- The per-field goals of `Fits.mkObj`, one conjunct per field (each skeleton `Skel.field`,
left to unification). -/
macro "fields_split" : tactic =>
  `(tactic|(simp only [List.cons_append, List.nil_append, List.append_nil, List.forall_mem_cons, List.forall_mem_nil, List.not_mem_nil, false_imp_iff, implies_true, and_true]; (repeat' apply And.intro)))

/-- The per-element goals of `Fits.arrOf` over appended, mapped and filtered lists. -/
macro "elems_split" : tactic =>
  `(tactic|(simp only [List.mem_toArray, List.mem_append, List.mem_map, List.mem_filterMap, or_imp, forall_and, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂, Option.some.injEq, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp, forall_eq]; (repeat' apply And.intro)))

/-- Literal conditions of a field list (`"".isEmpty`). -/
macro "lits_simp" : tactic =>
  `(tactic|simp only [isEmpty_empty, ↓reduceIte, Bool.false_eq_true, eq_self_iff_true, if_true, if_false, List.cons_append, List.nil_append, List.append_nil])

/-- A hypothesis `(match x with ...) = some v` of a `filterMap` element: one case per branch. -/
macro "elem_cases" : tactic =>
  `(tactic|(try (rename_i h; split at h <;> (try simp only [Option.some.injEq, reduceCtorEq] at h) <;> (try subst_vars))))

/-- Through a runner's `do` block: binds (keeping `x = .ok a`), conditions, matches and join
points, down to each `pure` (left as a `Fits` goal) or `throw`. -/
macro "okfits" : tactic =>
  `(tactic|repeat' (first | (with_reducible apply OkP.pure) | (with_reducible apply OkP.ok) | (with_reducible show OkP _ (_ >>= _); simp only [bind_pure]) | (with_reducible apply OkP.bind; intro _ _) | (with_reducible apply OkP.ite <;> intro _) | exact OkP.throw | exact OkP.error | (show OkP _ _; split) | (show OkP _ _; simp only [])))

end ResponseShape

namespace ResponseShape.FitsTactic
open Lean Meta Elab Tactic

def strLit? (e : Expr) : Option String :=
  match e.consumeMData with
  | .lit (.strVal s) => some s
  | _ => none

/-- The elements of a list literal. -/
def listElems : Nat → Expr → Option (List Expr)
  | 0, _ => none
  | fuel + 1, e =>
    let e := e.consumeMData
    if e.isAppOfArity ``List.nil 1 then some []
    else if e.isAppOfArity ``List.cons 3 then do
      let rest ← listElems fuel e.appArg!
      pure (e.appFn!.appArg! :: rest)
    else if e.isAppOfArity ``HAppend.hAppend 6 || e.isAppOfArity ``List.append 3 then do
      pure ((← listElems fuel e.appFn!.appArg!) ++ (← listElems fuel e.appArg!))
    else none

def bound : Nat := 1000000

def strList? (e : Expr) : Option (List String) := (listElems bound e) >>= (·.mapM strLit?)

/-- The names of a list of pairs whose first components are literals. -/
def names? (e : Expr) : Option (List String) :=
  (listElems bound e) >>= (·.mapM fun p =>
    let p := p.consumeMData
    if p.isAppOfArity ``Prod.mk 4 then strLit? p.appFn!.appArg! else none)

/-- `Skel.keysOk`, on the literals of an object skeleton. -/
def objAccepts (k : Expr) (keys : List String) : Bool := Id.run do
  unless k.isAppOfArity ``Skel.obj 4 do return false
  let args := k.getAppArgs
  let some fs := names? args[0]! | return false
  let extra := args[1]!.isAppOfArity ``Option.some 1
  let some req := strList? args[2]! | return false
  let some ab := strList? args[3]! | return false
  keys.eraseDups.length == keys.length && keys.all (fun x => fs.contains x || extra) &&
    req.all keys.contains && ab.all (fun x => !keys.contains x)

/-- The skeleton and value of a goal `Fits Γ k v`, the skeleton in weak head normal form. -/
def fitsGoal : TacticM (Expr × Expr) := do
  let t ← instantiateMVars (← getMainTarget)
  unless t.isAppOfArity ``Fits 3 do throwError "not a Fits goal"
  let args := t.getAppArgs
  pure (← whnf args[1]!, (← instantiateMVars args[2]!).consumeMData)

/-- At `Fits Γ (.alt ss) (Json.mkObj l)` with literal field names: the first object member of
`ss` whose fields `l`'s names pass. -/
elab "fits_pick" : tactic => withMainContext do
  let (k, v) ← fitsGoal
  unless k.isAppOfArity ``Skel.alt 1 do throwError "fits_pick: not an alternative"
  unless v.isAppOfArity ``Lean.Json.mkObj 1 do throwError "fits_pick: not Json.mkObj"
  let some keys := names? v.appArg! | throwError "fits_pick: field names are not literals"
  let some members := listElems bound k.appArg! | throwError "fits_pick: members are not a literal list"
  let mut members' := #[]
  for m in members do members' := members'.push (← whnf m)
  match members'.toList.findIdx? (objAccepts · keys) with
  | none => throwError "fits_pick: no member of the alternative has the fields {keys}"
  | some i =>
    let n := Syntax.mkNumLit (toString i)
    evalTactic (← `(tactic| refine Fits.mkObjAlt $n rfl (by keys_ok) ?_))

/-- The position of `a` in the literal list `l` (structural equality). -/
def position (l a : Expr) : MetaM (Option Nat) := do
  let some xs := listElems bound (← whnf l) | return none
  let a ← instantiateMVars a
  for (x, i) in xs.zipIdx do
    if (← instantiateMVars x) == a then return some i
  for (x, i) in xs.zipIdx do
    if ← withReducible (isDefEq x a) then return some i
  return none

/-- `a ∈ l` for a member of a literal list. -/
elab "alt_mem" : tactic => withMainContext do
  let t ← instantiateMVars (← getMainTarget)
  unless t.isAppOfArity ``Membership.mem 5 do throwError "alt_mem: not a membership"
  let args := t.getAppArgs
  let (l, a) := (args[3]!, args[4]!)
  match ← position l a with
  | none => throwError "alt_mem: not a member"
  | some i =>
    let n := Syntax.mkNumLit (toString i)
    evalTactic (← `(tactic| exact List.mem_of_getElem? (i := $n) rfl))

/-- `Fits Γ (.alt ss) v` narrowed to the member that is the skeleton of the shape at `target`. -/
elab "fits_as " target:str : tactic => withMainContext do
  let (k, _) ← fitsGoal
  unless k.isAppOfArity ``Skel.alt 1 do throwError "fits_as: not an alternative"
  evalTactic (← `(tactic| refine Fits.ofAlt (s := skel% $target) (by alt_mem) ?_))

end ResponseShape.FitsTactic

namespace ResponseShape
open Lean

macro "alt_sub" : tactic =>
  `(tactic|(intro s hs; simp only [List.mem_cons, List.not_mem_nil, or_false] at hs; (repeat' (rcases hs with h | hs)); all_goals (subst_vars; alt_mem)))

syntax "fits" : tactic

macro_rules
  | `(tactic| fits) => `(tactic| first
      | exact Fits.any _
      | (apply Fits.mkObj (by keys_ok); fields_split <;> fits)
      | (fits_pick; fields_split <;> fits)
      | (apply Fits.arrOf; elems_split <;> (try intros) <;> elem_cases <;> fits)
      | (apply Fits.strIn_lit; decide)
      | (apply Fits.strNotIn_lit; decide)
      | (lits_simp; fits)
      | (split <;> fits)
      | skip)

end ResponseShape
