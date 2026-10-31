import VE.Scope.ReadingsExamples

/-! sc-5rd: `governSets_every_choice`'s counterexample (every-choice-counterexample.md). Evidence, not product code: the
    unit `5` makes `setObjVal!` panic when evaluated (it answers `null`), so it is kept out of the build. Check it from
    `lean/` with `PATH=~/.elan/bin:$PATH lake env lean ../docs/scope/sc-5rd/EveryChoiceCounterexample.lean`. -/

namespace VE.Scope.Examples
open Lean VE.Scope

def ceDoc : Json := j "{\"units\": [{\"id\": \"a\"}, 5, {}], \"reading_sets\": [{\"id\": \"S\", \"version\": 1, \"readings\": [{\"id\": \"r\", \"content\": \"x\"}]}]}"
def ceG : Governor := ⟨"g", "a", .reguard (j "[\"top\"]"), .list "a", [""]⟩
def ceD (re : VE.Readings.Wire.ReadingsEnvironment) : SDoc :=
  ⟨Examples.layoutOf [("a", "Rules:\n"), ("", "- x\n")], ceDoc, .null, [ceG], [], [], re⟩

-- every hypothesis holds: the tree is well formed, a set is governed, `governSets` succeeds, the choice is checked
#guard jsonWF? ceDoc
#guard (do pure (governedSetUnits (ceD (← VE.Readings.Wire.decodeEnvironment envJ))) : Except String _).toOption == some [""]
#guard (do setChoices (ceD (← VE.Readings.Wire.decodeEnvironment envJ))).toOption == some [[("S", 1, 0)]]
#guard (do governSets (ceD (← VE.Readings.Wire.decodeEnvironment envJ))).isOk
-- and the conclusion fails: the choice read off the answer gives `{}` the content `null`, `govern` of it gives `"x"`
#guard (do
  let D := ceD (← VE.Readings.Wire.decodeEnvironment envJ)
  let out ← governSets D
  let o ← governChoice D [("S", 1, 0)]
  pure (VE.Readings.Wire.jeq (atChoiceOn (governedSetUnits D) out [("S", 1, 0)]) o, contentOf o "",
    (unitsOf o).map fun (x : Json) => x.getObjValD "content") : Except String (Bool × Json × List Json)).toOption ==
    some (false, Json.null, [Json.null, Json.null, Json.str "x"])

end VE.Scope.Examples
