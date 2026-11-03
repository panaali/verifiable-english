import VE.Service.DocumentChainExamples

/-! PC-2a's fixtures of the branches around the chain: the soft source's every rule, the neighbouring chains' own
branches of `check` and `admitGraph`, and `requestOf` over several units and reading sets. Checks only, on the helpers
of `DocumentChainExamples`. -/

namespace VE.Service.DocumentChain.Examples
open Lean
open VE.Service.Document

/-! ## Every rule of the soft source is read, whichever one holds the fault (`softSource`) -/

#guard [(true, false), (false, true)].all fun (first, second) =>
  let rule (bad : Bool) (name : String) : Json :=
    Json.mkObj [("norm", ((complyRule.getObjValD "norm").setObjVal! "name" (.str name)).setObjVal! "predicate"
      (.str (if bad then "absent" else "comply_required")))]
  let unit (id : String) (start : Nat) (r : Json) : Json :=
    Json.mkObj [("id", .str id), ("span", toJson [start, start + 1]), ("kind", .str "norm"),
      ("meaning", .str "specified"), ("support", .str "assumption"), ("content", r)]
  let front := Json.mkObj [("format", .str "ve-document@1"), ("environment", environmentOver chain complyPredicates),
    ("units", Json.arr #[unit "u1" 0 (rule first "a"), unit "u2" 1 (rule second "b")])]
  match check ("---\n" ++ front.compress ++ "\n---\nxy") with
  | .error e => e == "CheckerUnavailable: a soft source the soft route rejects keeps its loader's diagnostic: " ++
      "UnknownSymbol: regulated predicate absent"
  | .ok _ => false

/-! ## Each chain's own branch: its `completions` and its claim graph -/

-- A list with `norm-defaults@0` first or last (the profile is set aside before the order is read), and with a later
-- profile beside the soft route: the same answers as `chain`.
#guard [["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"],
    ["documents@1", "norms@0", "relational-fol@0", "soft-norms@0", "norm-defaults@0"],
    ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0", "time@0"]].all fun ps =>
  let d (ms : List (String × Json)) := document (environmentOver ps complyPredicates) complyRule ms
  checkError (d []) == none &&
    checkError (d [("completions", completions "absent" "u1")]) == some "UnknownSymbol: regulated predicate absent"

-- The plain soft route never reads the layered decoder, whose reserved names are the profile's; the W1 route under the
-- profile answers with its own check.
#guard checkError (document (environmentOver ["documents@1", "norms@0", "relational-fol@0", "soft-norms@0"]
    (("unsaid__x", arg "x") :: complyPredicates.map fun (p, j) => (p, if p == "comply_required" then
      j.setObjVal! "regulated" ((j.getObjValD "regulated").setObjVal! "default" (.str "deny")) else j))) complyRule) == none
#guard [["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"], ["norm-defaults@0", "norms@0", "relational-fol@0"],
    ["documents@1", "norms@0", "relational-fol@0", "norm-defaults@0"]].all fun ps =>
  checkError (document (environmentOver ps denyPredicates) denyRule [("completions", completions "absent" "u1")]) ==
    some "UnknownSymbol: regulated predicate absent"

-- A claim graph on each route: the layered route's admission under the chain, each other route's beside it.
#guard [(chain, complyPredicates, complyRule),
    (["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"], complyPredicates, complyRule),
    (["documents@1", "norms@0", "relational-fol@0", "soft-norms@0", "norm-defaults@0"], complyPredicates, complyRule),
    (["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"], denyPredicates, denyRule),
    (["norm-defaults@0", "norms@0", "relational-fol@0"], denyPredicates, denyRule),
    (["documents@1", "norms@0", "relational-fol@0", "norm-defaults@0"], denyPredicates, denyRule),
    (["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0", "time@0"], complyPredicates,
      complyRule)].all fun (ps, predicates, rule) =>
  let claim := Json.mkObj [("id", .str "u2"), ("span", toJson [1, 2]), ("kind", .str "asserted"),
    ("meaning", .str "specified"), ("support", .str "assumption"), ("content", Json.mkObj [("ast", Json.arr #[.str "top"])])]
  let norm := (((document (environmentOver ps predicates) rule).getObjValD "units").getArr?.toOption.getD #[]).toList
  let front := (document (environmentOver ps predicates) rule).setObjVal! "units" (Json.arr (norm ++ [claim]).toArray)
  let graph := Json.mkObj [("root", .str "claim"), ("nodes", Json.arr #[Json.mkObj [("ast", Json.arr #[.str "top"]),
    ("name", .str "claim"), ("unit", .str "u2")]])]
  (check ("---\n" ++ (front.setObjVal! "graph" graph).compress ++ "\n---\nxy")) matches .ok _

/-! ## `requestOf` over several units and reading sets -/

-- Two free units are two norms; a set on either holds exactly that one, wherever it stands among the sets.
#guard holds (environmentOf (environmentOver chain complyPredicates)) fun E =>
  let unit (id : String) : SourceUnit :=
    { id, span := (0, 1), kind := .str "norm", decoded := RowKind.route VE.Route.Admission.Kind.norm,
      meaning := .str "specified", support := "assumption", status := "CHECKED", parent := none,
      content := some (UnitContent.soft complyRule) }
  let sets (us : List String) : Json := Json.mkObj
    [("reading_sets", Json.arr (us.map fun u => Json.mkObj [("unit", .str u)]).toArray)]
  let count (us : List String) : Nat :=
    (((requestOf E (sets us) [unit "u1", unit "u2"]).getObjValD "norms").getArr?.toOption.getD #[]).size
  count [] == 2 && count ["u1"] == 1 && count ["u2"] == 1 && count ["u1", "u3"] == 1 && count ["u3", "u1"] == 1 &&
    count ["u3", "u1", "u4"] == 1 && count ["u1", "u2"] == 0 && count ["u3"] == 2

/-! ## The refusal reads `readings@1` wherever it stands in a sorted list -/

#guard refusal ["documents@1", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"] ==
  some "CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route"
#guard refusal ["norms@0", "readings@1", "relational-fol@0", "soft-norms@0"] ==
  some "CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route"
-- Read before the order of the list is: the same refusal with `readings@1` first.
#guard refusal ["readings@1", "documents@1", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"] ==
  some "CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route"

end VE.Service.DocumentChain.Examples
