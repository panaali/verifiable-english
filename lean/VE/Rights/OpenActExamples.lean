import VE.Rights.Run
import VE.Rights.Examples

/-! rights-cfr-4: a rule is open when an open name is its act, as when it is in its guard or a carve-out
(docs/spec/rights.md 7.2), and a right's unit reads its own lines' acts (`nodeOpen`, `unitOpen`; build-time checks). -/
namespace VE.Rights.OpenActExamples
open Lean (Json)
open VE.Norms.Checks (perm)
open VE.Rights.Examples (mkRights strictNode defaultNode line diag)
open VE.Rights.Run (nodeOpen unitOpen)

def adult : VE.Formula := .unary "adult" (.var 0)

/-- Two strict rights of persons, each one liberty: `r1` on `speak_permitted`, `r2` on `marry_permitted`. -/
def twoRights : RightsDoc :=
  mkRights ["person"] [("adult", ["person"])]
    [perm "speak_permitted" ["person"] false "{0} speak", perm "marry_permitted" ["person"] true "{0} marry"] []
    ⟨["person"], ["person"], [], []⟩
    [⟨"r1", "person", .top, [line .liberty (strictNode "r1-line" "speak_permitted" true adult)]⟩,
     ⟨"r2", "person", .top, [line .liberty (strictNode "r2-line" "marry_permitted" true adult)]⟩] [] []

/-- The source unit of a right with the one line named `rule`. -/
def unitOf (rule : String) : Json :=
  Json.mkObj [("right", Json.mkObj [("lines", Json.arr #[Json.mkObj [("norm", Json.mkObj [("name", .str rule)])]])])]

/-- `unitOpen` of each right's unit, `r1` then `r2`. -/
def opens (openNames : List String) : List Bool := ["r1-line", "r2-line"].map (unitOpen twoRights openNames ∘ unitOf)

#guard diag twoRights == "ok"
-- the act alone opens a strict rule; another open name does not; the guard still does
#guard nodeOpen ["speak_permitted"] (strictNode "n" "speak_permitted" true adult)
#guard !nodeOpen ["marry_permitted"] (strictNode "n" "speak_permitted" true adult)
#guard !nodeOpen [] (strictNode "n" "speak_permitted" true adult)
#guard nodeOpen ["adult"] (strictNode "n" "speak_permitted" true adult)
-- the default mode alone, and one switch party alone, open a rule (as before rights-cfr-4)
#guard nodeOpen [] (defaultNode "n" "speak_permitted" true adult)
#guard nodeOpen [] { strictNode "n" "speak_permitted" true adult with alterable := ["p"] }
-- each right's unit reads its own line's act
#guard opens ["speak_permitted"] == [true, false]
#guard opens ["marry_permitted"] == [false, true]
#guard opens [] == [false, false]

end VE.Rights.OpenActExamples
