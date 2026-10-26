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

/-- Each answer with one member added to one object, one leaf or array retyped, or one member dropped (but those in
    `optional`, and a filling's tables, whose keys are open), at any depth up to `n`. -/
def variants (optional : List String) : Nat → Json → List Json
  | 0, _ => []
  | n + 1, .obj kvs =>
    let kvs := kvs.toList
    Json.mkObj (kvs ++ [("extra", .null)]) ::
    ((kvs.filter fun (k, _) => !optional.contains k && !k.startsWith "unsaid__").map fun (k, _) => Json.mkObj (kvs.filter (·.1 != k))) ++
    kvs.flatMap fun (k, v) => (variants optional n v).map fun w => Json.mkObj (kvs.map fun (k', v') => (k', if k' == k then w else v'))
  | n + 1, .arr xs => .num 0 :: (List.range xs.size).flatMap fun i => (variants optional n xs[i]!).map (.arr <| xs.set! i ·)
  | _, .str _ => [.num 0]
  | _, .num _ => [.str "0"]
  | _, _ => []
def refusesAll (j : Json) (optional : List String := []) : Bool := (variants optional 6 (run j)).all (!accepts j ·)

def resolved : Json := req αEnv γbR "defaults-coherence" [("coherence", toJson [pairJ "r1" "r2" γbCert])]
def strictJ : Json := αCase excSelf cStrict.trace (αModels [exc1])
def unsettled : Json := αCase notExc cNeeds.trace (αModels [])
def long : Json := βFact [exAt "urgent"] [exAt "urgent"]

-- accepted: elaborate, COLLISION with its situation, COHERENT (no pair, a resolved pair), UNKNOWN pairs, FOLLOWS on
-- each basis and form, UNKNOWN with a reason, DOES-NOT-FOLLOW with a filled gap, an UNKNOWN model
#guard holds dγ fun L => [req αEnv γR "defaults-elaborate", coll L, req αEnv αR "defaults-coherence", resolved,
    req αEnv γR "defaults-coherence", cert, strictJ, unsettled, long, certNone].all fun j => accepts j (run j)
#guard holds dβ fun L => [βTwo L, modelCase βEnv βR L xAll [exc1]].all fun j => accepts j (run j)
-- refused: every variant of each answer (a COLLISION's `collision` and `situation` may be left out)
#guard holds dγ fun L => refusesAll (req αEnv γR "defaults-elaborate") && refusesAll (coll L) ["collision", "situation"] &&
  refusesAll resolved && refusesAll cert && refusesAll certNone
#guard holds dβ fun L => refusesAll (βTwo L) && refusesAll (modelCase βEnv βR L xAll [exc1])
-- refused: an elaborate row of one or three items, a pair of one or three rule names
#guard let a := run (req αEnv γR "defaults-elaborate"); let t := ((a.getObjValD "coherence_targets").getArrVal? 0).toOption.getD .null;
  [set a "default_premises" (toJson [toJson ["l"]]), set a "coherence_targets" (toJson [t.getArrVal? 0 |>.toOption.getD .null]),
    set a "coherence_targets" (toJson [toJson ["r1", "r2", "r3", "r4"]])].all (!accepts (req αEnv γR "defaults-elaborate") ·) &&
  [toJson ["r1"], toJson ["r1", "r2", "r3"]].all fun r =>
    !accepts resolved (set (run resolved) "pairs" (toJson [Json.mkObj [("rules", r), ("status", .str "resolved")]]))
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
