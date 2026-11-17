import VE
import VE.Service.Protocol
import VE.Route.MeteredProofs
import ResponseShape

/-! arch-decoder-measure: which project constants `VE.CertificateWire.decodeClosureTrace` reaches,
and which project constants outside that set use them. Measurement only; not part of the tree's
build. Run from `lean/`: `lake env lean ../docs/arch/arch-decoder-measure/deps.lean > <out>`.

A project constant is one whose module starts with `VE` or `ResponseShape`. A constant's
references are those of its type and its value (a theorem's proof included, so a theorem that
reads a decoder counts as its user). The output is one JSON object. -/

open Lean

def projectModule (env : Environment) (c : Name) : Option Name := do
  let idx ← env.getModuleIdxFor? c
  let m := env.header.moduleNames[idx.toNat]!
  if (`VE).isPrefixOf m || (`ResponseShape).isPrefixOf m then some m else none

def refs (ci : ConstantInfo) : NameSet :=
  let t := ci.type.getUsedConstants
  let v := match ci.value? (allowOpaque := true) with
    | some e => e.getUsedConstants
    | none => #[]
  (t ++ v).foldl (fun s n => s.insert n) {}

def reach (env : Environment) (roots : List Name) : NameSet := Id.run do
  let mut seen : NameSet := {}
  let mut todo := roots
  let mut fuel := 1000000
  while fuel > 0 do
    fuel := fuel - 1
    match todo with
    | [] => break
    | c :: rest =>
      todo := rest
      if seen.contains c then continue
      seen := seen.insert c
      if let some ci := env.find? c then
        for n in (refs ci).toList do
          if (projectModule env n).isSome && !seen.contains n then todo := n :: todo
  return seen

#eval show CoreM Unit from do
  let env ← getEnv
  let root := `VE.CertificateWire.decodeClosureTrace
  let r := reach env [root]
  -- the root and the constants Lean generated under its name (equations, matchers, `_unary`)
  let ofRoot := fun (n : Name) => n == root || root.isPrefixOf n
  -- project constants outside the reach that use a member of it: the root's users (its callers,
  -- rewritten by a switch) and the users of any other member (which keep that member alive)
  let mut rootUsers : NameSet := {}
  let mut kept : NameSet := {}
  for (c, ci) in env.constants.toList do
    if r.contains c then continue
    if (projectModule env c).isNone then continue
    for n in (refs ci).toList do
      if r.contains n then
        if ofRoot n then rootUsers := rootUsers.insert c else kept := kept.insert n
  -- everything a kept member reaches stays; the rest of the reach goes with the root
  let alive := reach env kept.toList
  let exclusive := r.toList.filter fun n => !alive.contains n
  let entry := fun (n : Name) => Json.mkObj [("name", toJson n.toString),
      ("module", toJson ((projectModule env n).getD .anonymous).toString)]
  IO.println (Json.mkObj [("root", toJson root.toString),
    ("reach", Json.arr ((r.toList.map entry).toArray.qsort (·.compress < ·.compress))),
    ("exclusive", Json.arr ((exclusive.map entry).toArray.qsort (·.compress < ·.compress))),
    ("root_users", Json.arr ((rootUsers.toList.map entry).toArray.qsort (·.compress < ·.compress))),
    ("kept_by_outside_users", Json.arr ((kept.toList.map entry).toArray.qsort (·.compress < ·.compress)))]).pretty
