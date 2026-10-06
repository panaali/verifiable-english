import ResponseShape.Skeletons
import Lean.Elab.Tactic

/-! # Tactics for the encoder theorems

* `okfits` goes through a runner's `do` block (binds, keeping each `x = .ok a`; conditions;
  matches; join points) down to each returned value, left as a `Fits` goal.
* `fits` proves `Fits c k v` for a value built from `Json.mkObj` with literal field names,
  arrays of mapped lists, and values `k` says nothing about. At an alternative it picks, by the
  object's field names, the first object skeleton whose fields they pass (`fits_pick`, decided
  here on the literals; the choice is then checked by the kernel). It leaves as goals what it
  cannot decide (a field value that depends on the encoder's data).
* `alt_mem` proves `s ∈ ss` for a member of a literal list, and `alt_sub` that every member of
  one alternative is a member of another (a runner that delegates to another mode's runner).
* `fits_as "file.json#/pointer"` narrows `Fits c (.alt ss) v` to the member that is the
  skeleton of that shape.

The tactics only build proofs: the kernel checks each, so a wrong choice fails the build. -/

namespace ResponseShape
open Lean

macro "keys_ok" : tactic =>
  `(tactic|(simp only [List.map_cons, List.map_nil, List.map_append, List.cons_append, List.nil_append, List.append_nil, List.filter_cons, List.filter_nil, String.reduceBNe, ↓reduceIte, Bool.false_eq_true]; decide))

/-- The per-field goals of `Fits.mkObj`, one conjunct per field (each skeleton `Skel.field`,
left to unification). -/
macro "fields_split" : tactic =>
  `(tactic|(simp only [List.cons_append, List.nil_append, List.append_nil, List.forall_mem_cons, List.forall_mem_nil, List.not_mem_nil, false_imp_iff, implies_true, and_true]; (repeat' apply And.intro)))

/-- The per-element goals of `Fits.arrOf` over appended, mapped and filtered lists. -/
macro "elems_split" : tactic =>
  `(tactic|(simp only [List.mem_toArray, Array.mem_append, getArr_arr, toOption_ok, Option.getD_some, List.mem_append, List.mem_map, List.mem_filterMap, List.mem_flatMap, Option.map_eq_some_iff, or_imp, forall_and, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂, Option.some.injEq, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp, forall_eq]; (repeat' apply And.intro)))

/-- Literal conditions of a field list (`"".isEmpty`). -/
macro "lits_simp" : tactic =>
  `(tactic|simp only [isEmpty_empty, setObjVal_mkObj, ↓reduceIte, Bool.false_eq_true, eq_self_iff_true, if_true, if_false, List.cons_append, List.nil_append, List.append_nil])

/-- A hypothesis `(match x with ...) = some v` of a `filterMap` element: one case per branch. -/
macro "elem_cases" : tactic =>
  `(tactic|(first | (rename_i h; split at h <;> (try simp only [Option.some.injEq, reduceCtorEq, List.mem_map, List.not_mem_nil] at h) <;> (try obtain ⟨_, _, h⟩ := h) <;> (try subst_vars)) | (try subst_vars)))

/-- Through a runner's `do` block: binds (keeping `x = .ok a`), conditions, matches and join
points, down to each `pure` (left as a `Fits` goal) or `throw`. -/
macro "okfits" : tactic =>
  `(tactic|repeat' (first | (with_reducible apply OkP.pure) | (with_reducible apply OkP.ok) | (with_reducible show OkP _ (_ >>= _); simp only [bind_pure]) | with_reducible exact OkP.throw_bind | (with_reducible apply OkP.bind; intro _ h; try (rw [OkP.pure_ok] at h; subst h)) | (with_reducible apply OkP.ite <;> intro _) | with_reducible exact OkP.throw | with_reducible exact OkP.error | (show OkP _ _; split) | (show OkP _ _; simp only [])))

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

/-- The skeleton and value of a goal `Fits c k v`, the skeleton in weak head normal form. -/
def fitsGoal : TacticM (Expr × Expr) := do
  let t := (← instantiateMVars (← getMainTarget)).consumeMData.headBeta
  unless t.isAppOfArity ``Fits 3 do throwError "not a Fits goal"
  let args := t.getAppArgs
  pure (← whnf args[1]!, (← instantiateMVars args[2]!).consumeMData)

/-- The field names of an object value: `Json.mkObj l` with literal names, or
`(Json.mkObj l).setObjVal! key x` (with `key` in place of any field of that name); whether it is
the latter. -/
def valueKeys (v : Expr) : MetaM (Bool × List String) := do
  if v.isAppOfArity ``Lean.Json.setObjVal! 3 then
    let args := v.getAppArgs
    let inner := args[0]!.consumeMData
    unless inner.isAppOfArity ``Lean.Json.mkObj 1 do throwError "fits_pick: setObjVal! of another value"
    let some key := strLit? args[1]! | throwError "fits_pick: the set field's name is not a literal"
    let some ks := names? inner.appArg! | throwError "fits_pick: field names are not literals"
    pure (true, key :: ks.filter (· != key))
  else
    unless v.isAppOfArity ``Lean.Json.mkObj 1 do throwError "fits_pick: not Json.mkObj"
    let some ks := names? v.appArg! | throwError "fits_pick: field names are not literals"
    pure (false, ks)

/-- Which branch of `.onCase cond t e` has the fields `keys`: `t` (true), `e` (false) or neither. -/
def caseBranch (k : Expr) (keys : List String) : MetaM (Option Bool) := do
  unless k.isAppOfArity ``Skel.onCase 3 do return none
  let args := k.getAppArgs
  if objAccepts (← whnf args[1]!) keys then return some true
  if objAccepts (← whnf args[2]!) keys then return some false
  return none

/-- At `Fits c k v` for an object `v` with literal field names: when `k` is an alternative, the
first member whose fields `v`'s names pass (an object skeleton, or a branch of a condition on the
request case); when `k` is such a condition, the branch they pass, leaving the condition on the
case `c` as a goal. -/
elab "fits_pick" : tactic => withMainContext do
  let (k, v) ← fitsGoal
  let (set, keys) ← valueKeys v
  if k.isAppOfArity ``Skel.onCase 3 then
    match ← caseBranch k keys with
    | some true => evalTactic (← `(tactic| refine Fits.onCaseT ?_ ?_))
    | some false => evalTactic (← `(tactic| refine Fits.onCaseE ?_ ?_))
    | none => throwError "fits_pick: no branch of the condition has the fields {keys}"
    return
  unless k.isAppOfArity ``Skel.alt 1 do throwError "fits_pick: not an alternative"
  let some members := listElems bound k.appArg! | throwError "fits_pick: members are not a literal list"
  for (m, i) in members.zipIdx do
    let m ← whnf m
    let n := Syntax.mkNumLit (toString i)
    if objAccepts m keys then
      if set then evalTactic (← `(tactic| refine Fits.setObjAlt $n rfl (by keys_ok) ?_ ?_))
      else evalTactic (← `(tactic| refine Fits.mkObjAlt $n rfl (by keys_ok) ?_))
      return
    if (← caseBranch m keys).isSome then
      evalTactic (← `(tactic| refine Fits.ofAlt (List.mem_of_getElem? (i := $n) rfl) ?_))
      return
  throwError "fits_pick: no member of the alternative has the fields {keys}"

/-- `Fits c k v` with `k` replaced by its weak head normal form (a field's skeleton looked up,
an abbreviation unfolded), so that lemmas apply to it by reducible unification. -/
elab "skel_norm" : tactic => withMainContext do
  let t := (← instantiateMVars (← getMainTarget)).consumeMData.headBeta
  unless t.isAppOfArity ``Fits 3 do throwError "not a Fits goal"
  let args := t.getAppArgs
  let k ← whnf args[1]!
  if k == args[1]! then throwError "skel_norm: already normal"
  let g ← getMainGoal
  replaceMainGoal [← g.change (mkApp3 (mkConst ``Fits) args[0]! k args[2]!)]

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
  let t := (← instantiateMVars (← getMainTarget)).consumeMData
  unless t.isAppOfArity ``Membership.mem 5 do throwError "alt_mem: not a membership"
  let args := t.getAppArgs
  let (l, a) := (args[3]!, args[4]!)
  match ← position l a with
  | none => throwError "alt_mem: not a member"
  | some i =>
    let n := Syntax.mkNumLit (toString i)
    evalTactic (← `(tactic| exact List.mem_of_getElem? (i := $n) rfl))

/-- `Fits c (.alt ss) v` narrowed to the member that is the skeleton of the shape at `target`. -/
elab "fits_as " target:str : tactic => withMainContext do
  let (k, _) ← fitsGoal
  unless k.isAppOfArity ``Skel.alt 1 do throwError "fits_as: not an alternative"
  evalTactic (← `(tactic| refine Fits.ofAlt (s := skel% $target) (by alt_mem) ?_))

/-- `e = b` for a Boolean `e` the context decides: a hypothesis `e = true` (when `b` is true) or
`¬ e = true` (when `b` is false), found by structural equality. -/
elab "bool_hyp" : tactic => withMainContext do
  let t := (← instantiateMVars (← getMainTarget)).consumeMData
  let some (_, lhs, rhs) := t.eq? | throwError "bool_hyp: not an equation"
  let positive := rhs.isConstOf ``Bool.true
  for d in ← getLCtx do
    if d.isImplementationDetail then continue
    let ty := (← instantiateMVars d.type).consumeMData
    if positive then
      if let some (_, l, r) := ty.eq? then
        if r.isConstOf ``Bool.true && l == lhs then
          (← getMainGoal).assign d.toExpr
          replaceMainGoal []
          return
    else
      -- `¬ e = true`, or `e ≠ true`
      let negated := if ty.isAppOfArity ``Not 1 then some ty.appArg!.consumeMData
        else if ty.isAppOfArity ``Ne 3 then
          some (mkApp3 (mkConst ``Eq [levelOne]) ty.getAppArgs[0]! ty.getAppArgs[1]! ty.getAppArgs[2]!)
        else none
      if let some (_, l, r) := negated.bind (·.eq?) then
        if r.isConstOf ``Bool.true && l == lhs then
          (← getMainGoal).assign (← mkAppM ``Iff.mpr #[mkApp (mkConst ``Bool.eq_false_iff) lhs, d.toExpr])
          replaceMainGoal []
          return
  throwError "bool_hyp: no hypothesis decides it"

end ResponseShape.FitsTactic

namespace ResponseShape
open Lean


/-- A condition on the request case (`CaseCond.holds req = b`) that the encoder's own test of the
case decides, as a hypothesis. -/
macro "case_cond" : tactic => `(tactic|(simp only [CaseCond.holds]; bool_hyp))

macro "alt_sub" : tactic =>
  `(tactic|(intro s hs; simp only [List.mem_cons, List.not_mem_nil, or_false] at hs; (repeat' (rcases hs with h | hs)); all_goals (subst_vars; alt_mem)))

/-- `fits using l, ...`: as `fits`, trying at every node first each lemma `l` (a `Fits` fact about
an encoder, such as `claimJson_fits`), whose hypotheses are closed by assumption. -/
syntax "fits" (" using " term,+)? : tactic

macro_rules
  | `(tactic| fits) => `(tactic| fits using Fits.any)
  | `(tactic| fits using $ls,*) => do
    let mut known : Lean.TSyntax ``Lean.Parser.Tactic.tacticSeq ← `(tacticSeq| fail "no lemma applies")
    for l in ls.getElems.reverse do
      known ← `(tacticSeq| first | (with_reducible apply $l <;> assumption) | $known)
    `(tactic| first
      | (skel_norm; fits using $ls,*)
      | exact Fits.any _
      | (exfalso; assumption)
      | $known
      | (apply Fits.mkObj (by keys_ok); fields_split <;> fits using $ls,*)
      | (fits_pick <;> (try simp only [List.map_cons, List.map_nil, List.filter_cons, List.filter_nil, String.reduceBNe, ↓reduceIte, Bool.false_eq_true]) <;> (try fields_split) <;> fits using $ls,*)
      | (with_reducible apply Fits.setObj (by keys_ok) <;> (try simp only [List.map_cons, List.map_nil, List.filter_cons, List.filter_nil, String.reduceBNe, ↓reduceIte, Bool.false_eq_true]) <;> (try fields_split) <;> fits using $ls,*)
      | (apply Fits.arrOf; elems_split <;> (try intros) <;> elem_cases <;> fits using $ls,*)
      | (apply Fits.mkObjExtra; elems_split <;> (try intros) <;> elem_cases <;> fits using $ls,*)
      | (apply Fits.strIn_lit; decide)
      | (apply Fits.strNotIn_lit; decide)
      | (lits_simp; fits using $ls,*)
      | (split <;> fits using $ls,*)
      | skip)

end ResponseShape
