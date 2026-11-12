import VE
import VE.Service.Protocol

/-! The reading closure of a verdict path (docs/spec/kernel-boundary.md, section 2).

For a theorem `T : ∀ input answer, run input = .ok answer → Meaning input answer`, what a
reviewer must read to know what an accepted answer means is the *statement* of `T` and every
definition that statement mentions, transitively: the spec. The body of `run` is not read (the
theorem holds for whatever it computes) and no proof is read (Lean's kernel checked them).

This tool measures that closure from the compiled environment, so no hand-kept table decides
what is trusted:

* a root theorem contributes its type only;
* a definition reached contributes its type and its value; an inductive type its constructors;
* a theorem reached from inside a definition contributes nothing (a proof does not change what
  the definition computes);
* a constant named `opaque` for the path (the runner the theorem is about) is not followed.

With `"mode": "run"` the roots are definitions and the closure is the code that executes.

Input: the JSON file named by the environment variable `VE_KC_CFG`,
`{"out": <path>, "paths": [{"name", "roots": [..], "opaque": [..], "mode": "statement"|"run"}]}`.
Output (the file `out`): per path, the project constants reached with module and line range,
the line count per module (overlapping ranges counted once), the reached definitions the
compiler replaces (`implemented_by`, `extern`) or the kernel cannot unfold (`opaque`, `partial`),
the reached constants with no source range (`unranged`; the Python half reports them), and, in
statement mode, `stated`: for each opaque name (the path's subject), the roots whose statement
says something about its answer (`answersStated`). A subject no root states the answer of is
not what the theorems are about (the Python half reports it for a kernel path); and
`open_fields`: the roots and reached definitions that quantify existentially over a list of answer
fields (`hasOpenFields`), which the Python half reports for a kernel path. -/
open Lean Elab Command Meta

namespace VE.KernelClosure

/-- A module of this repository (not the Lean toolchain's). -/
def projectModule (m : Name) : Bool :=
  !([`Init, `Lean, `Std, `Lake].contains m.getRoot)

def moduleOf (env : Lean.Environment) (n : Name) : Option Name := do
  let idx ← env.getModuleIdxFor? n
  env.header.moduleNames[idx.toNat]?

/-- What reading a reached constant requires reading next. -/
def readDeps (info : ConstantInfo) : List Name :=
  let ty := info.type.getUsedConstants.toList
  match info with
  | .thmInfo _ => []
  | .defnInfo d => ty ++ d.value.getUsedConstants.toList
  | .opaqueInfo d => ty ++ d.value.getUsedConstants.toList
  | .inductInfo i => ty ++ i.ctors
  | .ctorInfo c => ty ++ [c.induct]
  | .recInfo r => ty ++ r.all
  | .axiomInfo _ => ty
  | .quotInfo _ => ty

structure Reached where
  consts : Array Name := #[]
  axioms : Array Name := #[]

/-- The closure of `roots`. `statement = true`: a root contributes its type only. -/
def closure (env : Lean.Environment) (roots opaqueNames : List Name) (statement : Bool) : Reached := Id.run do
  let mut pending : List Name := []
  let mut seen : Std.HashSet Name := {}
  for o in opaqueNames do seen := seen.insert o
  for r in roots do
    match env.find? r with
    | none => pure ()
    | some info =>
      if statement then
        pending := info.type.getUsedConstants.toList ++ pending
      else
        pending := r :: pending
  let mut out : Reached := {}
  while !pending.isEmpty do
    let n := pending.head!
    pending := pending.tail!
    if seen.contains n then continue
    seen := seen.insert n
    let some info := env.find? n | continue
    match info with
    | .thmInfo _ => continue
    | .axiomInfo _ => out := { out with axioms := out.axioms.push n }
    | _ => pure ()
    out := { out with consts := out.consts.push n }
    pending := readDeps info ++ pending
  return out

/-- Count the lines covered by a list of inclusive ranges, overlaps once. -/
def coveredLines (ranges : Array (Nat × Nat)) : Nat := Id.run do
  let sorted := ranges.qsort (fun a b => a.1 < b.1 || (a.1 == b.1 && a.2 < b.2))
  let mut total := 0
  let mut hi := 0
  for (a, b) in sorted do
    if b ≤ hi then continue
    let lo := if a > hi then a else hi + 1
    total := total + (b + 1 - lo)
    hi := b
  return total

/-- The source range that holds a constant: its own, or that of the nearest name prefix that
has one (`f.match_1`, `f._unary` and the like sit inside `f`). A private auxiliary
(`_private.M.0.f.match_1.splitter`, made by `unfold` in a proof) is looked up by its user name. -/
partial def rangeOf (n : Name) : CommandElabM (Option (Name × Nat × Nat)) := do
  match ← findDeclarationRanges? n with
  | some r => return some (n, r.range.pos.line, r.range.endPos.line)
  | none =>
    if let some user := privateToUserName? n then
      if user != n then
        if let some found ← rangeOf user then return some found
    match n with
    | .str p _ => if p.isAnonymous then return none else rangeOf p
    | .num p _ => if p.isAnonymous then return none else rangeOf p
    | .anonymous => return none

/-- The value of an accepted answer: `v` in `Except.ok v` or `some v`. -/
def acceptedValue? (e : Expr) : Option Expr :=
  let e := e.consumeMData
  if e.isAppOfArity ``Except.ok 3 || e.isAppOfArity ``Option.some 2 then some e.appArg! else none

/-- The subjects among `subjects` whose answer the statement of the theorem `thm` says something
about (kernel-boundary section 2): the statement has a hypothesis `s args = .ok answer` (or
`some answer`) whose `answer` is a variable that another hypothesis or the conclusion mentions,
or a hypothesis `s args = true` whose arguments the conclusion mentions. A theorem that only gates
the input (`s j = .ok r → P j`, with `r` unused) states nothing about the answer. -/
def answersStated (thm : Name) (subjects : List Name) : MetaM (List Name) := do
  let some info := (← getEnv).find? thm | return []
  forallTelescope info.type fun xs body => do
    let types ← xs.mapM inferType
    let mut out : List Name := []
    for i in [:types.size] do
      let some (_, lhs, rhs) := types[i]!.consumeMData.eq? | continue
      let some s := subjects.find? (lhs.consumeMData.getAppFn.isConstOf ·) | continue
      let others := ((List.range types.size).filterMap fun k => if k == i then none else types[k]?) ++ [body]
      let stated := match acceptedValue? rhs with
        | some a => a.isFVar && others.any (·.containsFVar a.fvarId!)
        | none => rhs.consumeMData.isConstOf ``Bool.true &&
            lhs.consumeMData.getAppArgs.any fun a => a.isFVar && body.containsFVar a.fvarId!
      if stated && !out.contains s then out := s :: out
    return out

/-- `List (String × Json)`: the fields of an answer object. -/
def fieldList (t : Expr) : Bool :=
  let t := t.consumeMData
  t.isAppOfArity ``List 1 &&
    (let p := t.appArg!.consumeMData
     p.isAppOfArity ``Prod 2 && p.appFn!.appArg!.consumeMData.isConstOf ``String &&
       p.appArg!.consumeMData.isConstOf ``Lean.Json)

/-- The term quantifies existentially over a list of answer fields. `Json.mkObj` keeps the last
value of a repeated key, so an answer stated as `mkObj (fields ++ rest)` with `rest` open can
override every stated field (KB-7 F1): a statement reads the fields it states by key instead. -/
def hasOpenFields (e : Expr) : Bool :=
  (e.find? fun x => x.isAppOfArity ``Exists 2 && fieldList x.appFn!.appArg!).isSome

/-- The roots whose statement, and the reached definitions whose body, leave answer fields open. -/
def openFields (env : Lean.Environment) (roots : List Name) (reached : Reached) : List Name :=
  (roots ++ reached.consts.toList).filter fun c => match env.find? c with
    | some (.defnInfo d) => hasOpenFields d.value
    | some info => roots.contains c && hasOpenFields info.type
    | none => false

/-- The detector's own fixtures: an answer stated with an open tail of fields, and the same answer
read by key. `run_cmd` below refuses to measure unless the first is found and the second is not. -/
def openTailFixture (answer : Json) : Prop :=
  ∃ rest : List (String × Json), answer = Json.mkObj ([("status", .str "ok")] ++ rest)

def keyedFixture (answer : Json) : Prop :=
  answer.getObjVal? "status" = .ok (.str "ok")

theorem openTailFixture_stated (answer : Json) (h : openTailFixture answer) : openTailFixture answer := h

theorem keyedFixture_stated (answer : Json) (h : keyedFixture answer) : keyedFixture answer := h

def strList (j : Json) (key : String) : List Name :=
  match j.getObjValD key with
  | .arr xs => xs.toList.filterMap fun x => x.getStr?.toOption.map String.toName
  | _ => []

def measure (path : Json) : CommandElabM Json := do
  let env ← getEnv
  let name := (path.getObjValAs? String "name").toOption.getD "?"
  let roots := strList path "roots"
  let opaqueNames := strList path "opaque"
  let statement := (path.getObjValAs? String "mode").toOption.getD "statement" != "run"
  let missing := (roots ++ opaqueNames).filter fun r => (env.find? r).isNone
  let reached := closure env roots opaqueNames statement
  let mut byModule : Std.HashMap Name (Array (Nat × Nat)) := {}
  let mut rows : Array Json := #[]
  let mut flagged : Array Json := #[]
  let mut unranged : Array Json := #[]
  let mut seenDecl : Std.HashSet (Name × Nat) := {}
  for c in reached.consts do
    let some m := moduleOf env c | continue
    unless projectModule m do continue
    if let some impl := Compiler.getImplementedBy? env c then
      flagged := flagged.push (Json.mkObj [("name", toString c), ("why", s!"implemented_by {impl}")])
    if isExtern env c then
      flagged := flagged.push (Json.mkObj [("name", toString c), ("why", "extern")])
    if let some (.opaqueInfo _) := env.find? c then
      flagged := flagged.push (Json.mkObj [("name", toString c), ("why", "opaque or partial")])
    match ← rangeOf c with
    | none => unranged := unranged.push (toString c)
    | some (decl, a, b) =>
      byModule := byModule.insert m ((byModule.getD m #[]).push (a, b))
      unless seenDecl.contains (m, a) do
        seenDecl := seenDecl.insert (m, a)
        rows := rows.push (Json.mkObj [("name", toString decl), ("module", toString m), ("from", a), ("to", b)])
  let mut modules : Array (String × Nat) := #[]
  let mut total := 0
  for (m, rs) in byModule.toList do
    let k := coveredLines rs
    total := total + k
    modules := modules.push (toString m, k)
  let sortedModules := modules.qsort (fun a b => a.2 > b.2 || (a.2 == b.2 && a.1 < b.1))
  -- statement mode: for each opaque name (the path's subject), the roots that state its answer
  let mut stated : Array (String × Json) := #[]
  if statement then
    let mut bySubject : Std.HashMap Name (Array String) := {}
    for r in roots do
      for s in ← liftTermElabM (answersStated r opaqueNames) do
        bySubject := bySubject.insert s ((bySubject.getD s #[]).push (toString r))
    for s in opaqueNames do
      stated := stated.push (toString s, toJson (bySubject.getD s #[]))
  let openTails := if statement then openFields env roots reached else []
  return Json.mkObj [
    ("name", name), ("mode", if statement then "statement" else "run"),
    ("open_fields", toJson (openTails.map toString)),
    ("roots", toJson (roots.map toString)), ("opaque", toJson (opaqueNames.map toString)),
    ("missing", toJson (missing.map toString)),
    ("lines", total), ("declarations", rows.size),
    ("modules", Json.mkObj (sortedModules.toList.map fun (m, k) => (m, toJson k))),
    ("axioms", toJson (reached.axioms.map toString)),
    ("flagged", Json.arr flagged), ("unranged", Json.arr unranged),
    ("stated", Json.mkObj stated.toList),
    ("decls", Json.arr rows)]

/-- The string literals of `tokens` that a term mentions. -/
def tokensIn (tokens : List String) (e : Expr) : List String :=
  tokens.filter fun t => (e.find? fun x => match x with
    | .lit (.strVal s) => s == t
    | _ => false).isSome

/-- Every definition of the repository whose body mentions one of the verdict tokens: the places
that can write a verdict into an answer (kernel-boundary section 3). Theorems and examples do not
compute answers and are not listed. -/
def census (tokens : List String) : CommandElabM Json := do
  let env ← getEnv
  let mut rows : Array Json := #[]
  for (n, info) in env.constants.toList do
    let some m := moduleOf env n | continue
    unless projectModule m do continue
    let value := match info with
      | .defnInfo d => some d.value
      | .opaqueInfo d => some d.value
      | _ => none
    let some v := value | continue
    let found := tokensIn tokens v
    if found.isEmpty then continue
    let (decl, a, b) := (← rangeOf n).getD (n, 0, 0)
    rows := rows.push (Json.mkObj [("name", toString decl), ("module", toString m), ("from", a), ("to", b),
      ("tokens", toJson found)])
  return Json.arr rows

end VE.KernelClosure

open VE.KernelClosure in
run_cmd do
  let some cfgPath ← IO.getEnv "VE_KC_CFG" | throwError "set VE_KC_CFG to the configuration file"
  let cfg ← match Json.parse (← IO.FS.readFile cfgPath) with
    | .ok j => pure j
    | .error e => throwError m!"{cfgPath}: {e}"
  let out ← match cfg.getObjValAs? String "out" with
    | .ok p => pure p
    | .error e => throwError m!"{cfgPath}: {e}"
  let paths := match cfg.getObjValD "paths" with
    | .arr xs => xs
    | _ => #[]
  let env ← getEnv
  let fixture := fun (n : Name) => openFields env [n] (closure env [n] [] true)
  unless fixture ``openTailFixture_stated == [``openTailFixture] && fixture ``keyedFixture_stated == [] do
    throwError "the open-fields detector misses its fixture: {fixture ``openTailFixture_stated}, {fixture ``keyedFixture_stated}"
  let mut results := #[]
  for p in paths do
    results := results.push (← measure p)
  let tokens := match cfg.getObjValD "census" with
    | .arr xs => xs.toList.filterMap fun x => x.getStr?.toOption
    | _ => []
  let censusRows ← if tokens.isEmpty then pure (Json.arr #[]) else census tokens
  IO.FS.writeFile out (Json.mkObj [("paths", Json.arr results), ("census", censusRows)]).pretty
