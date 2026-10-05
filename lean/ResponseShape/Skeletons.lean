import ResponseShape.Schemas
import ResponseShape.Skeleton
import Lean.Elab.Command

/-! # The skeleton of every mode's row shape

`ResponseShape.Skeletons.<mode>` is the skeleton (`ResponseShape.Skeleton`) of the row shape
`<mode>.json#/row`, extracted from `ResponseShape.Schemas` when this module is built, one
definition per constructor of `VE.Service.Mode`, and `row` maps each mode to its own. Nothing
here is written by hand: a shape that changes changes its skeleton, and the encoder theorems
(`ResponseShape.Encoders`) are checked against the new one. -/

namespace ResponseShape.Skeletons
open Lean Elab Command

/-- The constructor of a mode, from its `Repr` (`VE.Service.Mode.softNorms`). -/
def ctorName (m : VE.Service.Mode) : Name :=
  (toString (repr m)).splitOn "." |>.getLast! |>.toName

/-- Define `Skeletons.<ctor>` for every mode and `Skeletons.row`, failing on a mode without a row
shape, a shape whose skeleton cannot be extracted, or a constructor `VE.Service.modes` misses. -/
elab "define_row_skeletons" : command => do
  let ctors := (← getConstInfoInduct ``VE.Service.Mode).ctors.map (·.componentsRev.head!)
  let mut seen : List Name := []
  for m in VE.Service.modes do
    let ctor := ctorName m
    match skeleton Schemas.files s!"{m.name}.json#/row" with
    | .error e => throwError "mode {m.name}: {e}"
    | .ok (_, recursive@(_ :: _)) => throwError "mode {m.name}: recursive skeleton through {recursive}"
    | .ok (k, []) =>
      liftCoreM <| addAndCompile <| .defnDecl {
        name := `ResponseShape.Skeletons ++ ctor
        levelParams := []
        type := mkConst ``Skel
        value := toExpr k
        hints := .abbrev
        safety := .safe }
      seen := ctor :: seen
  for c in ctors do
    unless seen.contains c do throwError "VE.Service.modes misses the mode {c}"
  let arms := String.join (ctors.map fun c => s!"\n  | .{c} => ResponseShape.Skeletons.{c}")
  let text := s!"def row : VE.Service.Mode → ResponseShape.Skel{arms}"
  match Parser.runParserCategory (← getEnv) `command text with
  | .ok stx => elabCommand stx
  | .error e => throwError e

define_row_skeletons

/-- `skel% "file.json#/pointer"`: the skeleton of that shape, extracted when the term is
elaborated (for the lemmas about one encoder of a mode). -/
elab "skel% " target:str : term => do
  match skeleton Schemas.files target.getString with
  | .error e => throwError "{target.getString}: {e}"
  | .ok (_, recursive@(_ :: _)) => throwError "{target.getString}: recursive skeleton through {recursive}"
  | .ok (k, []) => pure (toExpr k)

/-- Recursive references: none, since every mode's skeleton is finite (`define_row_skeletons`
fails on a recursive one). -/
def Γ : String → Skel := fun _ => .nothing

end ResponseShape.Skeletons
