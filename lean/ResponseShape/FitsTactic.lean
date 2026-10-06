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

namespace ResponseShape
open Lean Meta Elab Tactic

/-- At `ErrP P (let k := v; e)`: for a join point `v` (a function of one to three arguments into
`Except`), `ErrP.jp1`/`jp2`/`jp3`, its body proved once for every argument; for any other value, `e`
with `v` in place of `k`. A join point is never copied into the branches that call it. -/
elab "errp_let" : tactic => withMainContext do
  let g ← getMainGoal
  let t ← instantiateMVars (← g.getType)
  unless t.isAppOfArity ``ErrP 4 do throwError "errp_let: not an ErrP goal"
  let r := t.appArg!.consumeMData.headBeta
  let .letE n ty v body _ := r | throwError "errp_let: not a let"
  let tys ← forallTelescopeReducing ty fun xs res => do
    let res ← whnfR res
    unless res.isAppOfArity ``Except 2 && xs.size ≥ 1 && xs.size ≤ 3 do return none
    let bs ← xs.mapM fun x => do return (← inferType x)
    -- A dependent join point (a later argument's type naming an earlier one) is unfolded instead.
    if bs.any (fun b => b.hasAnyFVar fun f => xs.any (·.fvarId! == f)) then return none
    return some (bs, res.appArg!)
  let args := t.getAppArgs
  if let some (bs, γ) := tys then
    let lemma := match bs.size with | 1 => ``ErrP.jp1 | 2 => ``ErrP.jp2 | _ => ``ErrP.jp3
    let pf ← mkAppOptM lemma ((#[args[0]!, args[1]!, args[2]!] ++ bs ++ #[γ, v, .lam n ty body .default]).map some)
    replaceMainGoal (← g.apply pf)
  else
    replaceMainGoal [← g.change (mkApp4 (mkConst ``ErrP) args[0]! args[1]! args[2]! (body.instantiate1 v))]

/-- `ErrP P t` with `t` in weak head normal form (a `match` on a known value reduced, `fail` run). -/
elab "errp_whnf" : tactic => withMainContext do
  let g ← getMainGoal
  let t ← instantiateMVars (← g.getType)
  unless t.isAppOfArity ``ErrP 4 do throwError "errp_whnf: not an ErrP goal"
  let args := t.getAppArgs
  replaceMainGoal [← g.change (mkApp4 (mkConst ``ErrP) args[0]! args[1]! args[2]! (← whnf args[3]!))]

/-- Names `disc` the local that the goal's first `match` inspects, to case on it (a pattern such as
`#[a, b]`, which `split` cannot take apart, reduces once the value is known). -/
elab "name_disc" : tactic => withMainContext do
  let t ← instantiateMVars (← getMainTarget)
  let env ← getEnv
  let some m := t.find? (fun e => isMatcherAppCore env e) | throwError "name_disc: no match"
  let some app ← matchMatcherApp? m | throwError "name_disc: no match"
  let some d := app.discrs.find? (·.isFVar) | throwError "name_disc: no local discriminant"
  replaceMainGoal [← (← getMainGoal).rename d.fvarId! `disc]

/-- Through a computation's `do` block (join points, binds, conditions, matches, loops, `mapM`, `<$>`)
down to each call that may throw, left as an `ErrP` goal for the caller's lemmas (`Phases.fail` with
its code). -/
macro "errfits" : tactic =>
  `(tactic|repeat' (first
    | (errp_let <;> intros)
    | (with_reducible apply ErrP.pure)
    | (with_reducible apply ErrP.ok)
    | (with_reducible apply ErrP.bind <;> try intro _)
    | (with_reducible apply ErrP.ite)
    | (with_reducible apply ErrP.map)
    | (with_reducible apply ErrP.mapM; intro _)
    | (with_reducible apply ErrP.forIn; intro _ _)
    | (with_reducible apply ‹∀ _, ErrP _ _›)
    | (with_reducible apply ‹∀ _ _, ErrP _ _›)
    | (with_reducible apply ‹∀ _ _ _, ErrP _ _›)
    | (show ErrP _ _; dsimp -zeta only)
    | (show ErrP _ _; split)))

theorem not_not_true {b : Bool} (h : ¬ (!b) = true) : b = true := by
  cases b <;> simp_all

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

/-- A list of pairs whose first components are literals: each name with its second component. -/
def pairs? (e : Expr) : Option (List (String × Expr)) :=
  (listElems bound e) >>= (·.mapM fun p =>
    let p := p.consumeMData
    if p.isAppOfArity ``Prod.mk 4 then (strLit? p.appFn!.appArg!).map (·, p.appArg!) else none)

/-- The names of a list of pairs whose first components are literals. -/
def names? (e : Expr) : Option (List String) := (pairs? e).map (·.map (·.1))

/-- A literal JSON scalar: a string, a Boolean (`some b`) or null (`none`). -/
def jsonLit? (v : Expr) : Option (String ⊕ Option Bool) :=
  let v := v.consumeMData
  let bool? (b : Expr) : Option Bool :=
    if b.isConstOf ``Bool.true then some true else if b.isConstOf ``Bool.false then some false else none
  if v.isAppOfArity ``Lean.Json.str 1 then (strLit? v.appArg!).map .inl
  else if v.isAppOfArity ``Lean.Json.bool 1 then (bool? v.appArg!.consumeMData).map (.inr ∘ some)
  else if v.isConstOf ``Lean.Json.null then some (.inr none)
  else none

/-- Whether the value `v` is a literal outside the literal domain of the skeleton `s` (`strIn`, or a
Boolean or null `lit`): an alternative whose field is `s` cannot take it. -/
def litClash (s v : Expr) : Bool := Id.run do
  let some lit := jsonLit? v | return false
  let s := s.consumeMData
  if s.isAppOfArity ``Skel.strIn 1 then
    let some vs := strList? s.appArg! | return false
    return match lit with
      | .inl x => !vs.contains x
      | .inr _ => true
  if s.isAppOfArity ``Skel.lit 1 then
    let l := s.appArg!.consumeMData
    let want : Option (Option Bool) :=
      if l.isConstOf ``Lit.null then some none
      else if l.isAppOfArity ``Lit.bool 1 then
        let b := l.appArg!.consumeMData
        if b.isConstOf ``Bool.true then some (some true) else if b.isConstOf ``Bool.false then some (some false)
        else none
      else none
    return match lit, want with
      | .inl _, _ => true
      | .inr x, some w => x != w
      | .inr _, none => l.isAppOfArity ``Lit.num 2
  return false

/-- `Skel.keysOk`, on the literals of an object skeleton, and no literal value of `vals` outside
its field's literal domain. -/
def objAccepts (k : Expr) (keys : List String) (vals : List (String × Expr) := []) : Bool := Id.run do
  unless k.isAppOfArity ``Skel.obj 4 do return false
  let args := k.getAppArgs
  let some fps := pairs? args[0]! | return false
  let fs := fps.map (·.1)
  let extra := args[1]!.isAppOfArity ``Option.some 1
  let some req := strList? args[2]! | return false
  let some ab := strList? args[3]! | return false
  keys.eraseDups.length == keys.length && keys.all (fun x => fs.contains x || extra) &&
    req.all keys.contains && ab.all (fun x => !keys.contains x) &&
    vals.all fun (key, v) => match fps.lookup key with
      | some s => !litClash s v
      | none => true

/-- The skeleton and value of a goal `Fits c k v`, the skeleton in weak head normal form. -/
def fitsGoal : TacticM (Expr × Expr) := do
  let t := (← instantiateMVars (← getMainTarget)).consumeMData.headBeta
  unless t.isAppOfArity ``Fits 3 do throwError "not a Fits goal"
  let args := t.getAppArgs
  pure (← whnf args[1]!, (← instantiateMVars args[2]!).consumeMData)

/-- The field names of an object value: `Json.mkObj l` with literal names, or
`(Json.mkObj l).setObjVal! key x` (with `key` in place of any field of that name); whether it is
the latter. -/
def valueKeys (v : Expr) : MetaM (Bool × List String × List (String × Expr)) := do
  if v.isAppOfArity ``Lean.Json.setObjVal! 3 then
    let args := v.getAppArgs
    let inner := args[0]!.consumeMData
    unless inner.isAppOfArity ``Lean.Json.mkObj 1 do throwError "fits_pick: setObjVal! of another value"
    let some key := strLit? args[1]! | throwError "fits_pick: the set field's name is not a literal"
    let some ps := pairs? inner.appArg! | throwError "fits_pick: field names are not literals"
    let ps := (key, args[2]!) :: ps.filter (·.1 != key)
    pure (true, ps.map (·.1), ps)
  else
    unless v.isAppOfArity ``Lean.Json.mkObj 1 do throwError "fits_pick: not Json.mkObj"
    let some ps := pairs? v.appArg! | throwError "fits_pick: field names are not literals"
    pure (false, ps.map (·.1), ps)

/-- Whether some object skeleton reachable from `k` through conditions on the case and
alternatives has the fields `keys` and takes the literal values `vals`. -/
def reaches (keys : List String) (vals : List (String × Expr)) : Nat → Expr → MetaM Bool
  | 0, _ => pure false
  | fuel + 1, k => do
    let k ← whnf k
    if objAccepts k keys vals then return true
    if k.isAppOfArity ``Skel.onCase 3 then
      let args := k.getAppArgs
      return (← reaches keys vals fuel args[1]!) || (← reaches keys vals fuel args[2]!)
    if k.isAppOfArity ``Skel.alt 1 then
      let some members := listElems bound k.appArg! | return false
      for m in members do
        if ← reaches keys vals fuel m then return true
    return false

/-- Which branch of `.onCase cond t e` has the fields `keys` (with the literal values `vals`): `t`
(true), `e` (false) or neither. -/
def caseBranch (k : Expr) (keys : List String) (vals : List (String × Expr)) : MetaM (Option Bool) := do
  unless k.isAppOfArity ``Skel.onCase 3 do return none
  let args := k.getAppArgs
  if ← reaches keys vals bound args[1]! then return some true
  if ← reaches keys vals bound args[2]! then return some false
  return none

/-- At `Fits c k v` for an object `v` with literal field names: when `k` is an alternative, the
first member whose fields `v`'s names and literal values pass (an object skeleton, or a branch of a condition on the
request case); when `k` is such a condition, the branch they pass, leaving the condition on the
case `c` as a goal. -/
elab "fits_pick" : tactic => withMainContext do
  let (k, v) ← fitsGoal
  let (set, keys, vals) ← valueKeys v
  if k.isAppOfArity ``Skel.onCase 3 then
    match ← caseBranch k keys vals with
    | some true => evalTactic (← `(tactic| refine Fits.onCaseT ?_ ?_))
    | some false => evalTactic (← `(tactic| refine Fits.onCaseE ?_ ?_))
    | none => throwError "fits_pick: no branch of the condition has the fields {keys}"
    return
  unless k.isAppOfArity ``Skel.alt 1 do throwError "fits_pick: not an alternative"
  let some members := listElems bound k.appArg! | throwError "fits_pick: members are not a literal list"
  for (m, i) in members.zipIdx do
    let m ← whnf m
    let n := Syntax.mkNumLit (toString i)
    if objAccepts m keys vals then
      if set then evalTactic (← `(tactic| refine Fits.setObjAlt $n rfl (by keys_ok) ?_ ?_))
      else evalTactic (← `(tactic| refine Fits.mkObjAlt $n rfl (by keys_ok) ?_))
      return
    if (← caseBranch m keys vals).isSome then
      evalTactic (← `(tactic| refine Fits.ofAlt (List.mem_of_getElem? (i := $n) rfl) ?_))
      return
  throwError "fits_pick: no member of the alternative has the fields {keys}"

/-- Whether `t` is an enumeration: an inductive type without parameters or indices, not recursive,
whose constructors' fields are enumerations (`Bool`, `Act`, `Status` with its `settled (b : Bool)`). -/
def enumLike : Nat → Expr → MetaM Bool
  | 0, _ => pure false
  | fuel + 1, t => do
    let .const n _ := (← whnf t).getAppFn | return false
    let some (.inductInfo info) := (← getEnv).find? n | return false
    unless info.numParams == 0 && info.numIndices == 0 && !info.isRec do return false
    for c in info.ctors do
      let ok ← forallTelescopeReducing (← getConstInfo c).type fun xs _ =>
        xs.allM fun x => do enumLike fuel (← inferType x)
      unless ok do return false
    return true

/-- Closes a goal whose hypotheses equate one term to two different constructors (`hgen : a = C`
from `str_cases`, and the runner's test `a = C'`). -/
def ctorClash (a : Expr) : TacticM Bool := withMainContext do
  let some hgen := (← getLCtx).findFromUserName? `hgen | return false
  for d in ← getLCtx do
    if d.isImplementationDetail || d.fvarId == hgen.fvarId then continue
    let some (_, l, _) := (← instantiateMVars d.type).consumeMData.eq? | continue
    unless ← withReducible (isDefEq l a) do continue
    let s ← saveState
    try
      let p ← mkEqTrans (← mkEqSymm hgen.toExpr) d.toExpr
      let (fv, g) ← (← getMainGoal).note `hclash p
      if (← g.cases fv).isEmpty then
        setGoals []
        return true
      s.restore
    catch _ => s.restore
  return false

/-- The string domain goal decided, or each constructor of the first enumeration-typed local of the
value taken in turn, a case the runner's tests exclude closed (`fuel` bounds the nesting: a constructor's fields are cased in their turn). -/
def strCasesCore (a : Expr) : Nat → TacticM Unit
  | 0 => throwError "str_cases: too deep"
  | fuel + 1 => withMainContext do
    let s ← saveState
    try
      evalTactic (← `(tactic| (apply Fits.strIn_lit; decide)))
      return
    catch _ => s.restore
    if ← ctorClash a then return
    let (_, v) ← fitsGoal
    let mut found : Option FVarId := none
    for x in (collectFVars {} v).fvarIds do
      if ← enumLike 3 (← x.getType) then
        found := some x
        break
    let some x := found | throwError "str_cases: no enumeration to case on"
    let subgoals ← (← getMainGoal).cases x
    for sg in subgoals do
      setGoals [sg.mvarId]
      strCasesCore a fuel
    setGoals []

/-- `Fits c (.strIn vs) (.str (f a))` or `Fits c (.strIn vs) (f a)` for `a` of an inductive type
without indices (a renderer of an enumeration, `Act.name`, `encodeForce`, `Status.label`): one goal
per constructor of `a` (and of its constructors' enumeration fields), each string decided. Fails
unless every constructor's string is among `vs`. -/
elab "str_cases" : tactic => withMainContext do
  let (k, v) ← fitsGoal
  unless k.isAppOfArity ``Skel.strIn 1 do throwError "str_cases: not a string domain"
  let e := if v.isAppOfArity ``Lean.Json.str 1 then v.appArg!.consumeMData else v
  unless e.isApp do throwError "str_cases: not an application"
  let a := e.appArg!
  unless ← enumLike 3 (← inferType a) do throwError "str_cases: not an enumeration"
  -- `hgen : a = x` keeps what the runner tested of `a` (`ctorClash`).
  let (_, g) ← (← getMainGoal).generalize #[{ expr := a, hName? := some `hgen }]
  setGoals [g]
  strCasesCore a 4

/-- At `Fits c (.alt ss) v` for an object `v` with a field `.bool e` (`e` not a literal), alternatives
that differ only by that field's literal (`true` beside an empty list, `false` beside a nonempty
one): the cases of `e`, each then picked by its value. -/
elab "bool_cases" : tactic => withMainContext do
  let (k, v) ← fitsGoal
  unless k.isAppOfArity ``Skel.alt 1 do throwError "bool_cases: not an alternative"
  let (_, _, vals) ← valueKeys v
  for (_, e) in vals do
    let e := e.consumeMData
    unless e.isAppOfArity ``Lean.Json.bool 1 do continue
    let b := e.appArg!.consumeMData
    if b.isConstOf ``Bool.true || b.isConstOf ``Bool.false then continue
    let (fvs, g) ← (← getMainGoal).generalize #[{ expr := b }]
    let gs ← g.cases fvs[0]!
    replaceMainGoal (gs.map (·.mvarId)).toList
    return
  throwError "bool_cases: no Boolean field"

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

/-- `rw [CaseCond.holds_kind_of h]` with `h : c.getObjValD "kind" = .str s` found by its form (an
`assumption` search would unify against every hypothesis, unfolding the runners). -/
elab "case_kind_rw" : tactic => withMainContext do
  for d in ← getLCtx do
    if d.isImplementationDetail then continue
    let ty := (← instantiateMVars d.type).consumeMData
    let some (_, l, r) := ty.eq? | continue
    let l := l.consumeMData
    unless l.isAppOfArity ``Lean.Json.getObjValD 2 && strLit? l.getAppArgs[1]! == some "kind" do continue
    unless r.consumeMData.isAppOfArity ``Lean.Json.str 1 do continue
    let h ← mkAppM ``CaseCond.holds_kind_of #[d.toExpr]
    try
      let r ← (← getMainGoal).rewrite (← getMainTarget) h
      let g' ← (← getMainGoal).replaceTargetEq r.eNew r.eqProof
      replaceMainGoal (g' :: r.mvarIds)
      return
    catch _ => continue
  throwError "case_kind_rw: no hypothesis gives the case's kind"

/-- `rw [CaseCond.path_toBool h]` with `h : c.getObjVal? k = .ok w` found by its form. -/
elab "case_path_rw" : tactic => withMainContext do
  for d in ← getLCtx do
    if d.isImplementationDetail then continue
    let ty := (← instantiateMVars d.type).consumeMData
    let some (_, l, r) := ty.eq? | continue
    unless l.consumeMData.isAppOfArity ``Lean.Json.getObjVal? 2 && r.consumeMData.isAppOfArity ``Except.ok 3 do continue
    try
      let h ← mkAppM ``CaseCond.path_toBool #[d.toExpr]
      let r ← (← getMainGoal).rewrite (← getMainTarget) h
      let g' ← (← getMainGoal).replaceTargetEq r.eNew r.eqProof
      replaceMainGoal (g' :: r.mvarIds)
      return
    catch _ => continue
  throwError "case_path_rw: no field of the case is known"

/-- Closes the goal from two hypotheses `P` and `¬ P` (or `b = true` and `b = false`) that are
syntactically the same proposition; `contradiction` would unify across hypotheses, unfolding the
runners. -/
elab "contra" : tactic => withMainContext do
  let hyps ← (← getLCtx).foldlM (init := #[]) fun acc d => do
    if d.isImplementationDetail then return acc
    return acc.push (d, (← instantiateMVars d.type).consumeMData)
  for (d, t) in hyps do
    if t.isAppOfArity ``Not 1 then
      let p := t.appArg!.consumeMData
      for (d', t') in hyps do
        if t' == p then
          let g ← getMainGoal
          g.assign (← mkAppOptM ``absurd #[none, some (← g.getType), some d'.toExpr, some d.toExpr])
          replaceMainGoal []
          return
    if let some (_, l, r) := t.eq? then
      if r.isConstOf ``Bool.true then
        for (d', t') in hyps do
          if let some (_, l', r') := t'.eq? then
            if r'.isConstOf ``Bool.false && l' == l then
              let g ← getMainGoal
              let ft ← mkEqTrans (← mkEqSymm d'.toExpr) d.toExpr
              g.assign (← mkAppOptM ``absurd #[none, some (← g.getType), some ft, some (mkConst ``Bool.false_ne_true)])
              replaceMainGoal []
              return
  throwError "contra: no hypothesis and its negation"

/-- Fails unless the goal is `Fits c k v` with `k` a condition on the case (`Skel.onCase`). -/
elab "on_case_goal" : tactic => withMainContext do
  let (k, _) ← fitsGoal
  unless k.isAppOfArity ``Skel.onCase 3 do throwError "not a condition on the case"

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

/-- Is `e` a string literal? -/
def isStrLit (e : Expr) : Bool := (strLit? e).isSome

/-- `(a == b) = true` with `a b : String`: the two sides. -/
def strBeqTrue? (t : Expr) : MetaM (Option (Expr × Expr)) := do
  let some (_, l, r) := t.consumeMData.eq? | return none
  unless r.isConstOf ``Bool.true do return none
  let l := l.consumeMData
  unless l.isAppOfArity ``BEq.beq 4 do return none
  unless (← whnfR l.getAppArgs[0]!).isConstOf ``String do return none
  return some (l.getAppArgs[2]!.consumeMData, l.getAppArgs[3]!.consumeMData)

/-- The runner's tests of the kind it read, as substitutions: every hypothesis
`(kind == "lit") = true` (or `"lit" == kind`) replaces the local `kind` by the literal, and a
goal with a hypothesis `("a" == "b") = true` of distinct literals is closed. -/
elab "kind_subst" : tactic => do
  let step : TacticM Bool := withMainContext do
    let g ← getMainGoal
    for d in ← getLCtx do
      if d.isImplementationDetail then continue
      let ty := (← instantiateMVars d.type).consumeMData
      -- A closed Boolean fact that is false (`["day", "civil"].contains "admission" = true`).
      if !ty.hasFVar && !ty.hasMVar && (← isProp ty) then
        let closed ← try
            let r ← withDefault <| whnf (← mkDecide (mkNot ty))
            if r.isConstOf ``Bool.true then
              let nh ← mkDecideProof (mkNot ty)
              g.assign (← mkAbsurd (← g.getType) d.toExpr nh)
              pure true
            else pure false
          catch _ => pure false
        if closed then
          replaceMainGoal []
          return false
      -- `¬ ("a" == "a") = true`
      if ty.isAppOfArity ``Not 1 then
        if let some (a, b) ← strBeqTrue? ty.appArg! then
          if isStrLit a && isStrLit b && strLit? a == strLit? b then
            let hp ← mkDecideProof ty.appArg!
            g.assign (← mkAbsurd (← g.getType) hp d.toExpr)
            replaceMainGoal []
            return false
      -- `¬ (!b) = true`: `b = true`.
      if ty.isAppOfArity ``Not 1 then
        if let some (_, l, r) := ty.appArg!.consumeMData.eq? then
          if r.isConstOf ``Bool.true && l.consumeMData.isAppOfArity ``not 1 then
            let h' ← mkAppM ``ResponseShape.not_not_true #[d.toExpr]
            let (_, g1) ← g.note `hn h'
            replaceMainGoal [← g1.clear d.fvarId]
            return true
      -- `(!b) = true`: `b = false`.
      if let some (_, l, r) := ty.eq? then
        if r.isConstOf ``Bool.true && l.consumeMData.isAppOfArity ``not 1 then
          let b := l.consumeMData.appArg!
          let h' ← mkEqMP (mkApp (mkConst ``Bool.not_eq_true') b) d.toExpr
          let (_, g1) ← g.note `hn h'
          replaceMainGoal [← g1.clear d.fvarId]
          return true
      -- `(a && b) = true`: both, as two facts.
      if let some (_, l, r) := ty.eq? then
        if r.isConstOf ``Bool.true && l.consumeMData.isAppOfArity ``and 2 then
          let ab := l.consumeMData.getAppArgs
          let both ← mkEqMP (mkApp2 (mkConst ``Bool.and_eq_true) ab[0]! ab[1]!) d.toExpr
          let (_, g1) ← g.note `hl (← mkAppM ``And.left #[both])
          let (_, g2) ← g1.note `hr (← mkAppM ``And.right #[both])
          replaceMainGoal [← g2.clear d.fvarId]
          return true
      let some (a, b) ← strBeqTrue? ty | continue
      if isStrLit a && isStrLit b then
        if strLit? a != strLit? b then
          let notH ← mkDecideProof (mkNot (← instantiateMVars d.type))
          g.assign (← mkAbsurd (← g.getType) d.toExpr notH)
          replaceMainGoal []
          return false
        continue
      unless (a.isFVar && isStrLit b) || (b.isFVar && isStrLit a) do continue
      let h ← mkAppM ``eq_of_beq #[d.toExpr]
      let (fv, g') ← g.note `hkind h
      replaceMainGoal [← Lean.Meta.subst g' fv]
      return true
    return false
  let mut fuel := 64
  while fuel > 0 do
    if (← getGoals).isEmpty then return
    unless ← step do return
    fuel := fuel - 1

end ResponseShape.FitsTactic

namespace ResponseShape
open Lean


open Lean Meta Elab Tactic ResponseShape.FitsTactic in
/-- Reverts the hypotheses that compare two string literals (`"a" == "b"`), so that a `simp` of
the goal evaluates them and leaves every other hypothesis as it is. -/
elab "revert_lit_tests" : tactic => withMainContext do
  let isLitTest (e : Expr) : Bool :=
    e.isAppOfArity ``BEq.beq 4 && isStrLit e.getAppArgs[2]! && isStrLit e.getAppArgs[3]!
  let mut fvars := #[]
  for d in ← getLCtx do
    if d.isImplementationDetail then continue
    if ((← instantiateMVars d.type).find? isLitTest).isSome then fvars := fvars.push d.fvarId
  if fvars.isEmpty then throwError "no test of literals"
  let (_, g) ← (← getMainGoal).revert fvars (preserveOrder := true)
  replaceMainGoal [g]

/-- `kind_subst`, then the runner's tests of literals evaluated in the hypotheses that hold them
(`"a" == "a" && x` is `x`); other hypotheses are left as they are. -/
macro "kind_norm" : tactic =>
  `(tactic|(kind_subst
            try (revert_lit_tests
                 simp only [String.reduceBEq, Bool.true_and, Bool.and_true, Bool.false_and, Bool.and_false,
                   Bool.not_true, Bool.not_false, Bool.true_or, Bool.or_true, Bool.false_or, Bool.or_false,
                   Bool.false_eq_true, not_false_eq_true, reduceCtorEq, forall_const,
                   true_implies, false_implies, imp_self]
                 intros)
            try kind_subst))

/-- A condition on the request case that is not a conjunction, from the context: the case's kind
string (`c.getObjValD "kind" = .str s`, then the runner's own test of `s`), the absence of a
kind, a runner's test of the case (`CaseCond.decided`), or the runner's test written as the
condition reads (`bool_hyp`). -/
macro "case_cond_atom" : tactic =>
  `(tactic| first
    | with_reducible assumption
    | (case_kind_rw; first | decide | bool_hyp | rfl | (kind_subst; decide))
    | with_reducible exact CaseCond.kind_of_lacks ‹_› _
    | with_reducible exact CaseCond.lacks_of_kind ‹_›
    | with_reducible exact CaseCond.lacks_of_val ‹_›
    | (case_path_rw; first | assumption | bool_hyp)
    | with_reducible exact CaseCond.path_ok ‹_›
    | with_reducible exact CaseCond.path_error ‹_› ‹_›
    | (simp only [CaseCond.holds_decided, CaseDecider.fn]; bool_hyp)
    | (simp only [CaseCond.holds]; bool_hyp))

theorem CaseCond.all_true {c : CaseCond} {cs : List CaseCond} {j : Json} (h : c.holds j = true)
    (hs : (CaseCond.all cs).holds j = true) : (CaseCond.all (c :: cs)).holds j = true := by
  simp [h, hs]

theorem CaseCond.all_false_head {c : CaseCond} {cs : List CaseCond} {j : Json} (h : c.holds j = false) :
    (CaseCond.all (c :: cs)).holds j = false := by
  simp [h]

theorem CaseCond.all_false_tail {c : CaseCond} {cs : List CaseCond} {j : Json}
    (hs : (CaseCond.all cs).holds j = false) : (CaseCond.all (c :: cs)).holds j = false := by
  simp [hs]

open Meta Elab Tactic ResponseShape.FitsTactic in
/-- Fails unless the goal is `(CaseCond.all cs).holds c = b` for a literal list `cs`. -/
elab "case_all_goal" : tactic => withMainContext do
  let t := (← instantiateMVars (← getMainTarget)).consumeMData
  let some (_, l, _) := t.eq? | throwError "not an equation"
  unless l.isAppOfArity ``CaseCond.holds 2 do throwError "not a condition"
  let c ← whnf l.getAppArgs[0]!
  unless c.isAppOfArity ``CaseCond.all 1 do throwError "not a conjunction"
  unless (listElems bound c.appArg!).isSome do throwError "not a literal conjunction"

/-- A condition on the request case (`CaseCond.holds req = b`) that the context decides: a
conjunction member by member, each member by `case_cond_atom`. -/
syntax "case_cond" : tactic

macro_rules
  | `(tactic| case_cond) => `(tactic| first
    | (case_all_goal; first
        | exact CaseCond.holds_all_nil _
        | (refine CaseCond.all_true ?_ ?_ <;> case_cond)
        | (refine CaseCond.all_false_head ?_; case_cond)
        | (refine CaseCond.all_false_tail ?_; case_cond))
    | case_cond_atom)

macro "alt_sub" : tactic =>
  `(tactic|(intro s hs; simp only [List.mem_cons, List.not_mem_nil, or_false] at hs; (repeat' (rcases hs with h | hs)); all_goals (subst_vars; alt_mem)))

/-- `Fits c (.alt ss) v` for a scalar `v` (an `enum` of strings and other scalars): the first
member that is `v` itself or a string list holding it. -/
syntax "scalar_alt" : tactic

macro_rules
  | `(tactic| scalar_alt) => `(tactic| first
    | (apply Fits.altHead; first | exact Fits.lit _ | (apply Fits.strIn_lit; decide))
    | (apply Fits.altTail; scalar_alt))

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
      | (on_case_goal; refine Fits.onCaseT (by case_cond) ?_; fits using $ls,*)
      | (on_case_goal; refine Fits.onCaseE (by case_cond) ?_; fits using $ls,*)
      | (exfalso; assumption)
      | $known
      | (apply Fits.mkObj (by keys_ok); fields_split <;> fits using $ls,*)
      | focus (bool_cases <;> fits using $ls,*; done)
      | (fits_pick <;> (try simp only [List.map_cons, List.map_nil, List.filter_cons, List.filter_nil, String.reduceBNe, ↓reduceIte, Bool.false_eq_true]) <;> (try fields_split) <;> fits using $ls,*)
      | (with_reducible apply Fits.setObj (by keys_ok) <;> (try simp only [List.map_cons, List.map_nil, List.filter_cons, List.filter_nil, String.reduceBNe, ↓reduceIte, Bool.false_eq_true]) <;> (try fields_split) <;> fits using $ls,*)
      | (apply Fits.arrOf; elems_split <;> (try intros) <;> elem_cases <;> fits using $ls,*)
      | (apply Fits.mkObjExtra; elems_split <;> (try intros) <;> elem_cases <;> fits using $ls,*)
      | exact Fits.lit _
      | (apply Fits.strIn_lit; decide)
      | str_cases
      | scalar_alt
      | (apply Fits.strNotIn_lit; decide)
      | (apply Fits.toJsonStrs; decide)
      | (lits_simp; fits using $ls,*)
      | (split <;> fits using $ls,*)
      | skip)

open Lean Meta Elab Tactic in
/-- `case_absurd hc`: closes the goal when `hc : cond.holds c = b` contradicts what `case_cond`
derives from the context. -/
elab "case_absurd " hc:ident : tactic => withoutRecover <| withMainContext do
  let h ← Lean.Elab.Term.elabTerm hc none
  let ty ← whnfR (← instantiateMVars (← Meta.inferType h))
  let some (_, lhs, b) := ty.eq? | throwError "case_absurd: not an equation"
  let positive := b.isConstOf ``Bool.true
  unless positive || b.isConstOf ``Bool.false do throwError "case_absurd: not a Boolean fact"
  let other := if positive then Lean.mkConst ``Bool.false else Lean.mkConst ``Bool.true
  let g2 ← Meta.mkFreshExprSyntheticOpaqueMVar (← Meta.mkEq lhs other)
  let saved ← Lean.Elab.Tactic.getGoals
  Lean.Elab.Tactic.setGoals [g2.mvarId!]
  Lean.Elab.Tactic.evalTactic (← `(tactic| case_cond))
  unless (← Lean.Elab.Tactic.getGoals).isEmpty do throwError "case_absurd: not decided"
  Lean.Elab.Tactic.setGoals saved
  -- `false = true` from the two facts
  let ft ← if positive then Meta.mkEqTrans (← Meta.mkEqSymm g2) h else Meta.mkEqTrans (← Meta.mkEqSymm h) g2
  let g ← Lean.Elab.Tactic.getMainGoal
  g.assign (← Meta.mkAppOptM ``absurd #[none, some (← g.getType), some ft, some (Lean.mkConst ``Bool.false_ne_true)])
  Lean.Elab.Tactic.replaceMainGoal []

/-- `fits_invert h` with `h : Fits c k v`: one goal per object skeleton of `k` that `v` may fit,
through its alternatives and its conditions on the case, each condition kept as a hypothesis and a
branch whose condition contradicts the context (`case_absurd`) dropped. -/
syntax "fits_invert " ident : tactic

macro_rules
  | `(tactic| fits_invert $h) => `(tactic| (repeat' (first
      | (obtain ⟨_, hs, $h:ident⟩ := Fits.alt_inv $h:ident
         simp only [List.mem_cons, List.not_mem_nil, or_false] at hs
         repeat' (rcases hs with hs | hs)
         all_goals (try subst hs))
      | (rcases Fits.onCase_inv $h:ident with ⟨hc, $h:ident⟩ | ⟨hc, $h:ident⟩ <;> (try case_absurd hc)))))

end ResponseShape

namespace ResponseShape.FitsTactic
open Lean Meta Elab Tactic

/-- `fits_from h` with `h : Fits c s v` (a term, elaborated once, its holes filled from the goal):
the goal `Fits c k v` for a skeleton `k` of which `s` is a member, reached through `k`'s
alternatives (each tried) and its conditions on the case (each decided by `case_cond`). -/
def fitsFrom (h : Expr) : Nat → TacticM Unit
  | 0 => throwError "fits_from: too deep"
  | fuel + 1 => withMainContext do
    let g ← getMainGoal
    let s ← saveState
    if ← isDefEq (← g.getType) (← inferType h) then
      g.assign h
      replaceMainGoal []
      return
    s.restore
    try evalTactic (← `(tactic| skel_norm)) catch _ => pure ()
    let (k, _) ← fitsGoal
    if k.isAppOfArity ``Skel.onCase 3 then
      -- The branch whose condition `case_cond` proves.
      let branch (thm : Name) : TacticM Unit := do
        let gs ← (← getMainGoal).apply (mkConst thm)
        let some gc ← gs.findM? (fun g => do return (← instantiateMVars (← g.getType)).isAppOf ``Eq)
          | throwError "fits_from: no condition"
        let rest := gs.filter (· != gc)
        setGoals [gc]
        evalTactic (← `(tactic| case_cond))
        unless (← getGoals).isEmpty do throwError "fits_from: condition not decided"
        setGoals rest
        fitsFrom h fuel
      let s ← saveState
      try branch ``Fits.onCaseT
      catch _ =>
        s.restore
        branch ``Fits.onCaseE
      return
    unless k.isAppOfArity ``Skel.alt 1 do throwError "fits_from: the term does not fit here"
    -- The term's skeleton an alternative whose members are all members of this one.
    let s ← saveState
    try
      let gs ← (← getMainGoal).apply (mkConst ``Fits.altSub)
      let some gh ← gs.findM? (fun g => do return (← instantiateMVars (← g.getType)).isAppOf ``Fits)
        | throwError "fits_from: no row goal"
      unless ← isDefEq (← gh.getType) (← inferType h) do throwError "fits_from: not a sub-alternative"
      gh.assign h
      let rest := gs.filter (· != gh)
      setGoals rest
      evalTactic (← `(tactic| alt_sub))
      unless (← getGoals).isEmpty do throwError "fits_from: not a sub-alternative"
      return
    catch _ => s.restore
    let some members := listElems bound k.appArg! | throwError "fits_from: members are not a literal list"
    for (_, i) in members.zipIdx do
      let s ← saveState
      try
        let n := Syntax.mkNumLit (toString i)
        evalTactic (← `(tactic| refine Fits.ofAlt (List.mem_of_getElem? (i := $n) rfl) ?_))
        fitsFrom h fuel
        return
      catch _ => s.restore
    throwError "fits_from: no member of the alternative takes the term"

elab "fits_from " h:term : tactic => withoutRecover <| withMainContext do
  let e ← Term.withoutErrToSorry <| elabTerm h none (mayPostpone := true)
  fitsFrom (← instantiateMVars e) 64

end ResponseShape.FitsTactic
