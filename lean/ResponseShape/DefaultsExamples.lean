import ResponseShape.Schemas
import VE.Defaults.RouteExamples

/-! The `defaults-*` rows of `norm-defaults.json` (`Schemas.NormDefaults`) on the mode's own answers to the route's
fixtures (`Defaults/RouteExamples.lean`): every answer is accepted, and an answer with a member added, dropped,
retyped or not bound to its request is refused. -/
namespace ResponseShape.DefaultsExamples
open Lean VE.Defaults.WireFixtures VE.Defaults.Fixtures VE.Defaults.RouteFixtures

def accepts (j a : Json) : Bool :=
  (ResponseShape.decide Schemas.files (.ref "norm-defaults.json#/row") { value := j } a).toOption.isSome
def set (j : Json) (k : String) (v : Json) : Json := j.setObjVal! k v
def drop (j : Json) (k : String) : Json := match j with
  | .obj kvs => .obj (kvs.erase k) | j => j

def coll (L : VE.NormDefaults.Wire.LayeredU) : Json := req αEnv γR "defaults-coherence" [("collision", collJ L "r1" "r2")]
def cert : Json := αCase notExc cNeeds.trace (αModels [exc1])
def certNone : Json := αCase notExc none (αModels [exc1])

-- accepted: elaborate, COLLISION with its situation, COHERENT, UNKNOWN pairs, FOLLOWS, UNKNOWN with a reason,
-- DOES-NOT-FOLLOW with a filled gap, an UNKNOWN model
#guard holds dγ fun L => [req αEnv γR "defaults-elaborate", coll L, req αEnv αR "defaults-coherence",
    req αEnv γR "defaults-coherence", cert, certNone].all fun j => accepts j (run j)
#guard holds dβ fun L => [βTwo L, modelCase βEnv βR L xAll [exc1]].all fun j => accepts j (run j)
-- refused: a member added, a verdict outside its enum, a collision or situation without COLLISION, the collision's
-- rules not the request's
#guard holds dγ fun L => let a := run (coll L);
  [set a "extra" .null, set a "verdict" (.str "FOLLOWS"), set a "verdict" (.str "UNKNOWN"),
    set a "collision" ((a.getObjValD "collision").setObjVal! "rules" (toJson ["r2", "r1"])),
    set (run (req αEnv γR "defaults-coherence")) "situation" (a.getObjValD "situation")].all (!accepts (coll L) ·)
-- refused: FOLLOWS without its basis or with a reason, UNKNOWN without its reason or with a form, a basis outside
-- its enum
#guard let a := run cert; let u := run certNone;
  [drop a "basis", set a "reason" (.str "x"), set a "basis" (.str "default"), drop u "reason",
    set u "form" (.str "short")].all fun b => !accepts cert b
-- refused: DOES-NOT-FOLLOW without its situation or its forced list, a forced entry's condition retyped, `forced`
-- with UNKNOWN
#guard holds dβ fun L => let a := run (βTwo L);
  [drop a "situation", drop a "forced", set a "forced" (toJson [Json.mkObj [("rule", .str "r1"),
    ("condition", .str "0"), ("tuple", toJson ["e1"])]]), set a "verdict" (.str "UNKNOWN")].all (!accepts (βTwo L) ·)

end ResponseShape.DefaultsExamples
