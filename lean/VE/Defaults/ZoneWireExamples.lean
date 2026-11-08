import VE.Defaults.ZoneExamples
import VE.Defaults.RouteExamples

/-! The `defaults-zone` kind through the service mode `norm-defaults` (`NormDefaults.Run.runCaseReported`), on spec
8.6's fixtures: the zone, DE10's form, `forced_all` and the rows after DE10 (DE11, DE10f, DE13), the zones with no
rows, the bounds, and the refusals. Each check has an accepting and a refusing side. -/
namespace VE.Defaults.ZoneWireFixtures
open Lean VE.Defaults.Fixtures VE.Defaults.WireFixtures VE.Defaults.ZoneFixtures

def run (j : Json) : Json := VE.NormDefaults.Run.runCaseReported j
/-- A complete situation over one sort: the decision tables `decs` empty, the base rows `on`. -/
def sitJ (sort : String) (ids : List String) (decs : List String) (on : List (String × List (List String)) := []) :
    Json :=
  Json.mkObj [("complete", true), ("domains", Json.mkObj [(sort, toJson ids)]), ("constants", Json.mkObj []),
    ("relations", Json.mkObj (decs.map (·, toJson ([] : List (List String))) ++ on.map fun (p, rows) => (p, toJson rows)))]
def zreq (env : Json) (rules : List String) (m : Json) (q : Json) (obs record : List Json := []) : Json :=
  req env rules "defaults-zone"
    [("model", m), ("record", Json.arr record.toArray), ("observations", Json.arr obs.toArray), ("query", q)]
/-- An outcome at a tuple, with a value for an observation. -/
def at_ (p : String) (t : List String) (v : Option Bool := none) : Json :=
  Json.mkObj ([("outcome", .str p), ("tuple", toJson t)] ++ (v.map (fun b => [("value", .bool b)])).getD [])
def dec (key : List (String × String)) (t : List String) (v : Bool) : Json :=
  Json.mkObj [("decision", Json.mkObj (key.map fun (k, x) => (k, .str x))), ("tuple", toJson t), ("value", .bool v)]
def shownZ (fields : List (String × Json)) : Json := VE.Route.Wire.ok "c" fields
def rowJ (row : String) (fields : List (String × Json)) : Json := Json.mkObj (("row", .str row) :: fields)
def de13x (r : String) (t : List String) : Json :=
  rowJ "DE13" [("decision", Json.mkObj [("excepted", .str r)]), ("tuple", toJson t)]
def byDefault (b : Bool) (form : String) (forced : List (String × List String)) (rows : List Json) : Json :=
  shownZ [("zone", .str "byDefault"), ("value", .bool b), ("form", .str form), ("forced_all", Json.arr (forced.map
    fun (r, t) => Json.mkObj [("rule", .str r), ("tuple", toJson t)]).toArray), ("completions", toJson [rows])]
def zoneOf (j : Json) : Json := (run j).getObjValD "zone"

def exR (r : String) : String := "soft__excepted__" ++ r
def lamEnv : Json := envS "operator" [regJ "instructs" "[\"operator\"]" "plain" "unspecified"]
  r#"{"parties":["operator"],"outranking":{"mode":"strict"}}"#
def lamR : List String := [ruleJ "g1" "instructs" true (dfltJ (dec := "operator"))]
def μ'Env : Json := envS "assistant" [regJ "p" "[\"assistant\"]" "plain" "unspecified", baseJ "cond_a", baseJ "cond_b"]
  r#"{"outranking":{"mode":"strict"}}"#
def μ'R : List String := [ruleG "r1" "p" true (un "cond_a") dfltJ, ruleG "r2" "p" false (un "cond_b") dfltJ]
def δSit : Json := sitJ "assistant" ["a"] [exR "r1", exR "r2", outw]
def πEnv : Json := envJ [xReq, regJ "x_permitted" "[\"assistant\"]" "permission" "unspecified" ",\"act\":\"{0} do x\""]
  strictSoft
def lam2 : Json := sitJ "operator" ["o1", "o2"] [exR "g1"]
def γSit : Json := sitJ "assistant" ["a"] [exR "r1", exR "r2"]
def lam13 : Json := sitJ "operator" ((List.range 13).map (s!"o{·}")) [exR "g1"]

/-! ## The zone and its rows (8.6) -/

-- DF-μ: by default yes at o2 and no at o1; the short form; g1's exception at o1 is forced (DE10f), as `forcedAll` says
#guard run (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) [at_ "instructs" ["o1"] (some false)]) ==
  byDefault true "short" [("g1", ["o1"])] [rowJ "DE10f" [("rule", .str "g1"), ("tuple", toJson ["o1"])]]
#guard run (zreq lamEnv lamR lam2 (at_ "instructs" ["o1"]) [at_ "instructs" ["o1"] (some false)]) ==
  byDefault false "short" [("g1", ["o1"])] [rowJ "DE10f" [("rule", .str "g1"), ("tuple", toJson ["o1"])]]
-- with nothing observed, nothing is forced and no decision is true: by default yes, no row
#guard run (zreq lamEnv lamR lam2 (at_ "instructs" ["o1"])) == byDefault true "short" [] []
-- DF-μ′ and DF-μ″: left to; two completions, each its alternative exception as DE13; nothing forced, so no DE10f
#guard run (zreq μ'Env μ'R (sitJ "assistant" ["a"] [exR "r1", exR "r2"] [("cond_a", [["a"]]), ("cond_b", [["a"]])])
    (at_ "p" ["a"])) == shownZ [("zone", .str "leftTo"), ("form", .str "short"), ("forced_all", toJson ([] : List Json)),
  ("completions", toJson [[de13x "r2" ["a"]], [de13x "r1" ["a"]]])]
#guard run (zreq αEnv γR γSit (at_ "x_permitted" ["a"])) == shownZ [("zone", .str "leftTo"), ("form", .str "short"),
  ("forced_all", toJson ([] : List Json)), ("completions", toJson [[de13x "r2" ["a"]], [de13x "r1" ["a"]]])]
-- DF-μ′b (neither guard): not said, with no row
#guard run (zreq μ'Env μ'R (sitJ "assistant" ["a"] [exR "r1", exR "r2"] [("cond_a", []), ("cond_b", [])])
    (at_ "p" ["a"])) == shownZ [("zone", .str "notSaid")]
-- DF-δz: by default yes in the long form, since the ranking atom is open (the regression for DE10's first form)
#guard run (zreq δEnv δR δSit (at_ "x_required" ["a"])) == byDefault true "long" [] []
-- DF-ξ (DF-α at {a}) and DF-π′: by default yes, short, no decision
#guard run (zreq αEnv αR (sitJ "assistant" ["a"] [exR "r1"]) (at_ "x_required" ["a"])) == byDefault true "short" [] []
#guard run (zreq πEnv αR (sitJ "assistant" ["a"] [exR "r1"]) (at_ "x_required" ["a"])) == byDefault true "short" [] []
-- DF-ξ′: the stated condition forces r1's exception, so DE11 (condition 0) and not DE10f; `x_required` is not said
def ξ'Sit : Json := sitJ "assistant" ["a"] [exR "r1"] [("urgent", [["a"]])]
#guard run (zreq βEnv βR ξ'Sit (at_ "x_permitted" ["a"])) == byDefault true "short" [("r1", ["a"])]
  [rowJ "DE11" [("rule", .str "r1"), ("condition", toJson 0), ("tuple", toJson ["a"])]]
#guard zoneOf (zreq βEnv βR ξ'Sit (at_ "x_required" ["a"])) == .str "notSaid"
-- the record's true decisions are listed too: a switch (DF-ε, r1 off for the user) and a ranking (DF-δ, the ranking
-- reversed, so r1 gives way with no exception), each as DE13 by its key; with them fixed, the short form
def recOff : List Json := [dec [("off", "r1"), ("party", "user")] ["a"] true]
#guard run (zreq (envJ [xReq, xPerm] userSoft) [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"alterable\":[\"user\"]"))]
    (sitJ "assistant" ["a"] [exR "r1", "soft__off__r1__user"]) (at_ "x_permitted" ["a"]) (record := recOff)) ==
  byDefault true "short" [] [rowJ "DE13" [("decision", Json.mkObj [("off", .str "r1"), ("party", .str "user")]),
    ("tuple", toJson ["a"])]]
def recOutw : List Json := [dec [("outweighs", "x_permitted"), ("lower", "helpfulness"), ("higher", "safety")] ["a"] true]
#guard run (zreq δEnv δR δSit (at_ "x_required" ["a"]) (record := recOutw)) == byDefault false "short" []
  [rowJ "DE13" [("decision", Json.mkObj [("outweighs", .str "x_permitted"), ("lower", .str "helpfulness"),
    ("higher", .str "safety")]), ("tuple", toJson ["a"])]]

-- the wire's one enumeration answers as `defaultZoneOf` and `forcedAllOf` each do (DRI 2026-11-04, df-5 item 2)
def oneCall (j : Json) : Bool :=
  match VE.Defaults.Wire.viewOf j >>= fun v => VE.Defaults.Wire.replayZoneOn v j with
  | .ok x => VE.Defaults.Wire.zoneFields x == VE.Defaults.Wire.zoneFieldsOf x
      (defaultZoneOf x.v.L x.X x.S.M x.record x.obs x.r x.vs []) (forcedAllOf x.v.L x.X x.S.M x.record x.obs [])
  | .error _ => false
#guard [zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) [at_ "instructs" ["o1"] (some false)],
  zreq μ'Env μ'R (sitJ "assistant" ["a"] [exR "r1", exR "r2"] [("cond_a", [["a"]]), ("cond_b", [["a"]])]) (at_ "p" ["a"]),
  zreq αEnv γR γSit (at_ "x_permitted" ["a"]), zreq δEnv δR δSit (at_ "x_required" ["a"]),
  zreq αEnv αR (sitJ "assistant" ["a"] [exR "r1"]) (at_ "x_required" ["a"]),
  zreq βEnv βR ξ'Sit (at_ "x_permitted" ["a"]), zreq πEnv αR (sitJ "assistant" ["a"] [exR "r1"]) (at_ "x_required" ["a"]),
  zreq lamEnv lamR lam13 (at_ "instructs" ["o0"])].all oneCall

-- two true decisions of one rule at two tuples (DF-α with `x_required` closed, both observed no): DE10f twice, in
-- tuple order; two rules' exceptions forced by their own stated conditions (β2 at {a}, urgent): DE11 twice
#guard run (zreq (envJ [xReq "deny", xPerm] strictSoft) αR (sitJ "assistant" ["a", "b"] [exR "r1"]) (at_ "x_required" ["b"])
    [at_ "x_required" ["a"] (some false), at_ "x_required" ["b"] (some false)]) ==
  byDefault false "short" [("r1", ["a"]), ("r1", ["b"])] (["a", "b"].map fun e =>
    rowJ "DE10f" [("rule", .str "r1"), ("tuple", toJson [e])])
#guard run (zreq β2Env β2R (sitJ "assistant" ["a"] [exR "r1", exR "r2"] [("calm", []), ("urgent", [["a"]])])
    (at_ "x_permitted" ["a"])) == byDefault true "short" [("r1", ["a"]), ("r2", ["a"])]
  [rowJ "DE11" [("rule", .str "r1"), ("condition", toJson 1), ("tuple", toJson ["a"])],
   rowJ "DE11" [("rule", .str "r2"), ("condition", toJson 0), ("tuple", toJson ["a"])]]
-- a record of two entries: the second, a true switch, is listed
#guard run (zreq (envJ [xReq, xPerm] userSoft) [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"alterable\":[\"user\"]"))]
    (sitJ "assistant" ["a"] [exR "r1", "soft__off__r1__user"]) (at_ "x_permitted" ["a"])
    (record := dec [("excepted", "r1")] ["a"] false :: recOff)) == byDefault true "short" []
  [rowJ "DE13" [("decision", Json.mkObj [("off", .str "r1"), ("party", .str "user")]), ("tuple", toJson ["a"])]]

/-! ## Zones with no rows, and the bounds -/

-- the record rules out the observation: no completion, with the refuting check's label; no form, no forcedAll
#guard run (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) [at_ "instructs" ["o1"] (some false)]
    [dec [("excepted", "g1")] ["o1"] false]) == shownZ [("zone", .str "noCompletion"), ("labels", toJson ["observed"])]
-- DF-λ at 13 operators: unknown (budget), and no forcedAll, form or row from it
#guard run (zreq lamEnv lamR lam13 (at_ "instructs" ["o0"])) ==
  shownZ [("zone", .str "unknown"), ("reason", .str "budget: 26 open atoms, over 12")]
-- observations past `maxZoneObservations` are not read: unknown at 1,025, answered at 1,024
def obsN (k : Nat) : List Json := List.replicate k (at_ "instructs" ["o1"] (some false))
#guard run (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) (obsN 1025)) ==
  shownZ [("zone", .str "unknown"), ("reason", .str "observations size")]
#guard zoneOf (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) (obsN 1024)) == .str "byDefault"
-- review F4: the sizes are counted before any entry is decoded (`zoneSizes`): past a bound, an entry no decoder
-- accepts (an observation with no outcome, a record entry `null`) is not read; within the bounds it is refused
def refusedZ (j : Json) : Json := (run j).getObjValD "error"
def noOutcome : Json := Json.mkObj [("tuple", toJson ["o1"]), ("value", .bool false)]
def recN (k : Nat) : List Json := List.replicate k (dec [("excepted", "g1")] ["o1"] false)
#guard run (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) (obsN 1024 ++ [noOutcome])) ==
  shownZ [("zone", .str "unknown"), ("reason", .str "observations size")]
#guard refusedZ (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) (obsN 1023 ++ [noOutcome])) ==
  .str "fields do not match: expected [outcome, tuple, value], got [tuple, value]"
#guard run (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) [] (recN 1024 ++ [.null])) ==
  shownZ [("zone", .str "unknown"), ("reason", .str "record size")]
#guard refusedZ (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) [] (recN 1023 ++ [.null])) == .str "object expected"
#guard zoneOf (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) [] (recN 1024)) == .str "byDefault"

/-! ## The words (review F3)

`ve/defaults_words.json` is `zoneWordsJson`: it reads back as Lean's rows, and the joins are REPORT's choices 2 and 3
(", " between a tuple's ids, " and " between a DE10″ completion's lines). -/

open VE.Defaults.Wire (zoneWordsJson zoneHeads zoneLineWords)

def wordsOf (key : String) (fields : List String) : Option (List (List String)) :=
  ((zoneWordsJson.getObjValD key).getArr?.toOption).map fun a => a.toList.map fun h =>
    fields.map fun f => ((h.getObjValD f).getStr?.toOption).getD "?"
#guard wordsOf "heads" ["zone", "form", "row", "words"] == some (zoneHeads.map fun (z, f, r, w) => [z, f, r, w])
#guard wordsOf "lines" ["row", "kind", "sentence", "inline"] ==
  some (zoneLineWords.map fun (r, k, s, i) => [r, k, s, i])
#guard zoneWordsJson.getObjValD "joins" == Json.mkObj [("tuple", .str ", "), ("and", .str " and ")]

/-! ## Refusals -/

#guard refusedZ (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) (record := [dec [("excepted", "g2")] ["o1"] true])) ==
  .str "InvalidInput: the record names a decision the document does not have"
#guard refusedZ (zreq lamEnv lamR lam2 (at_ "instructs" ["o2"]) (record := [dec [("excepted", "g1"), ("x", "y")] ["o1"] true])) ==
  .str "InvalidInput: a decision is named by excepted, by off and party, or by outweighs, lower and higher"
#guard refusedZ (zreq lamEnv lamR lam2 (at_ "orders" ["o2"])) == .str "InvalidInput: orders is not a regulated outcome of the document"
#guard refusedZ (zreq lamEnv lamR lam2 (at_ "instructs" ["o3"])) == .str "InvalidInput: tuple has the wrong length or sort"
#guard refusedZ (zreq lamEnv lamR (sitJ "operator" ["o1", "o2"] [] [(exR "g1", [["o1"]])]) (at_ "instructs" ["o2"])) ==
  .str "InvalidInput: the situation's decision tables are empty; a fixed decision goes in the record"
-- DF-θ: `weighing@0` is refused, by the layered decoder on main and by diagnostic 1 on a decoded document (WireExamples)
#guard refusedZ (zreq envW αR (sitJ "assistant" ["a"] [exR "r1"]) (at_ "x_required" ["a"])) ==
  .str "UnsupportedProfile: Unsupported profile weighing@0"
#guard holds dα fun L => VE.Defaults.Wire.weighingText ==
    "UnsupportedProfile: answers that assume no exception are not available with weighing@0 yet" &&
  match VE.Defaults.Wire.viewRest (zreq envW αR (sitJ "assistant" ["a"] [exR "r1"]) (at_ "x_required" ["a"])) L with
  | .error e => e == VE.Defaults.Wire.weighingText | .ok _ => false

end VE.Defaults.ZoneWireFixtures
