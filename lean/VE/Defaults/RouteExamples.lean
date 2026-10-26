import VE.Defaults.WireExamples
import VE.NormDefaults.Run

/-! The `defaults-*` kinds through the service mode `norm-defaults` (`NormDefaults.Run.runCaseReported`): defeasible's
row of the layered kind table (`Defaults/Route.lean`), the pack it needs, the routing's boundaries, the answers of
every other kind unchanged, and a situation with a filled gap. -/
namespace VE.Defaults.RouteFixtures
open Lean VE.Defaults.WireFixtures VE.Defaults.Fixtures

def run (j : Json) : Json := VE.NormDefaults.Run.runCaseReported j
def refused (e : String) : Json := Json.mkObj [("id", .str "c"), ("status", .str "error"), ("error", .str e)]
def shown (e : Except String (Option Json)) : Json :=
  match e with | .ok (some a) => a | .ok none => .str "none" | .error e => .str ("error: " ++ e)

/-! ## The row: each kind through the mode is `defaultsCase`'s answer on `viewOf` -/

#guard holds dγ fun L => [req αEnv γR "defaults-elaborate",
    req αEnv γR "defaults-coherence" [("collision", collJ L "r1" "r2")]].all fun j =>
  run j == answer j && (run j).getObjValD "status" == .str "ok"
#guard run (αCase notExc cNeeds.trace (αModels [exc1])) == follows "needs" "short" [excN "r1"]
#guard holds dβ fun L => run (modelCase βEnv βR L xAll ["urgent", exc1]) == doesNotFollow [("r1", 0)]
-- the row's refusals are the mode's error rows (DF-η, diagnostic 3)
#guard run ((αCase notExc none []).setObjVal! "premises" (toJson [fJ (exAt exc1)])) == refused
  "InvalidInput: a question that assumes no exception may state facts only; it states whether rule r1's exception applies"

/-- DF-β at two assistants, both urgent and excepted, with r1's gap `unsaid__x_required` filled at e1 only. -/
def βTwo (L : VE.NormDefaults.Wire.LayeredU) : Json :=
  let two : Json := Json.mkObj [("complete", true),
    ("domains", Json.mkObj (L.sitVocab.sorts.map fun s => (s, toJson ["e1", "e2"]))), ("constants", Json.mkObj []),
    ("relations", Json.mkObj (L.sitVocab.predicates.map fun (x : String × List String) =>
      (x.1, toJson (if ["urgent", exc1].contains x.1 then [["e1"], ["e2"]] else ([] : List (List String))))))]
  (modelCase βEnv βR L xAll []).setObjVal! "model"
    (Json.mkObj [("model", two), ("filling", Json.mkObj [("unsaid__x_required", toJson [["e1"]])])])
-- the situation shows the filled gap (df-1ad review F3)
#guard holds dβ fun L => run (βTwo L) == VE.Route.Wire.ok "c" [("verdict", .str "DOES-NOT-FOLLOW"),
  ("situation", sitJ [["e1"]]), ("forced", toJson (["e1", "e2"].map fun e =>
    Json.mkObj [("rule", .str "r1"), ("condition", toJson 0), ("tuple", toJson [e])]))]

/-! ## The pack and the routing's boundaries -/

-- the row needs the soft pack: without it the kind is refused by the table; with it, answered
#guard holds dα fun L => ["defaults-elaborate", "defaults-model"].all fun k =>
  shown (VE.NormDefaults.Wire.layeredKindCase { L with packs := [] } "c" k (req αEnv αR k)) ==
    .str s!"error: UnsupportedProfile: case kind {k} needs the soft premise pack"
#guard holds dα fun L => shown (VE.NormDefaults.Wire.layeredKindCase L "c" "defaults-elaborate"
  (req αEnv αR "defaults-elaborate")) == answer (req αEnv αR "defaults-elaborate")
-- a `defaults-` kind outside the row, a plain norm-defaults source and a source without the profile keep the base's
-- refusals
def plainEnv : Json := αEnv.setObjVal! "profiles" (toJson ["norm-defaults@0", "norms@0", "relational-fol@0"])
#guard run (req αEnv αR "defaults-other") ==
  refused "UnsupportedProfile: case kind defaults-other is not available on the norm-defaults route"
#guard run (req plainEnv αR "defaults-model") ==
  refused "UnsupportedProfile: case kind defaults-model is not available on the norm-defaults route"
#guard run (req (αEnv.setObjVal! "profiles" (toJson ["norms@0", "relational-fol@0", "soft-norms@0"])) αR
  "defaults-elaborate") == refused "UnsupportedProfile: unspecified completion requires norm-defaults@0"

/-! ## Every other kind is answered as before (`layeredKindCase_other`) -/

#guard holds dγ fun L => ["norm-defaults-elaborate", "norm-defaults-conflict", "norm-defaults-status",
    "norm-defaults-report", "norm-defaults-gaps", "defaults-other", "admission"].all fun k =>
  shown (VE.NormDefaults.Wire.layeredKindCase L "c" k (req αEnv γR k)) ==
    shown (VE.NormDefaults.Wire.layeredCase L "c" k (req αEnv γR k))
#guard holds dγ fun L => run (req αEnv γR "norm-defaults-elaborate") ==
  shown (VE.NormDefaults.Wire.layeredCase L "c" "norm-defaults-elaborate" (req αEnv γR "norm-defaults-elaborate"))

end VE.Defaults.RouteFixtures
