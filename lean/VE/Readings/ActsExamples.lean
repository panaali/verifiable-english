import VE.Readings.Run

/-! act-phrases AP-1 (ap-1bd): the readings route's frame decoder reads `acts@0` single acts and refuses a joined act
with D-33 (spec 6.4, 10); a rule on a plain act passes the norms chain's `Soften.checkW1`. Fixtures A1-A3, A5 and A6
of 11.1, built as a service request carries them; `VE.Service.ActsExamples` has the other routes'. -/

namespace VE.Readings.ActsExamples
open Lean

def a1 := "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
def a2 := "{0} to equal pay for equal work without any discrimination"
def a5 := "{0} to seek and to enjoy in other countries asylum from persecution"
def a6 := "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment"
def fxs : List String := ["a fair and public hearing by an independent and impartial tribunal", "equal pay for equal work"]
def rdP : List String := ["acts@0", "norms@0", "readings@1", "relational-fol@0"]
def reg (role act : String) : Json := Json.mkObj ([("role", .str role), ("default", .str "deny"), ("act", .str act)] ++
  if role == "plain" then [("form", .str "has the right")] else [])
/-- An environment with `profiles`, the predicates `preds` (name, role, act; one argument, two from `{1}`) and the
fixed phrases `fxs`, and the constants `consts`. -/
def env (preds : List (String × String × String)) (profiles := rdP) (consts : List (String × Json) := []) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"), ("vocabulary", Json.mkObj [
      ("sorts", Json.mkObj [("person", Json.mkObj [("description", .str "p")]), ("case", Json.mkObj [("description", .str "c")])]),
      ("predicates", Json.mkObj (preds.map fun (p, role, act) => (p, Json.mkObj [("description", .str "d"),
        ("arguments", toJson (if (act.splitOn "{1}").length > 1 then ["person", "case"] else ["person"])),
        ("regulated", reg role act)]))),
      ("constants", Json.mkObj consts), ("acts", Json.mkObj [("fixed", toJson fxs)])])]
def envA (profiles := rdP) : Json := env [("heard", "plain", a1), ("paid", "plain", a2)] profiles
def err {α} (e : Except String α) : String := match e with | .error m => m | .ok _ => "ok"
def decode (j : Json) : String := err (VE.Readings.Wire.decodeEnvironment j)
def d33 (p : String) : String :=
  s!"UnsupportedProfile: acts@0 on the readings route admits single acts only; the act of {p} joins acts"

-- the route reads single acts (A1, A2), with and without `norm-defaults@0`
#guard (VE.Readings.Wire.decodeEnvironment envA).toOption.map (·.se.ne.regulated.map (·.act)) == some [some a1, some a2]
#guard decode (envA ["acts@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0"]) == "ok"
-- and admits a document with a rule on a plain act (the norms chain's `Soften.checkW1` admits the act)
def rule (sign : Bool) : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "m"), ("predicate", .str "paid"),
  ("sign", .bool sign), ("guard", Json.arr #[.str "top"]), ("unless", Json.arr #[]), ("over", Json.arr #[])])]
def ruleDoc : Json := Json.mkObj [("reading_sets", Json.arr #[]), ("units", Json.arr #[Json.mkObj [("id", .str "u1"),
  ("kind", .str "norm"), ("content", rule true)]])]
#guard err (VE.Readings.Run.validateOne "v" envA ruleDoc) == "ok"
-- a document with a reading set over `acts@0` keeps the base's refusal (ap-1bg); without `acts@0` the set is admitted
-- as before (here to its own refusal), and with no set the document is read (above)
def setDoc : Json := Json.mkObj [("units", Json.arr #[Json.mkObj [("id", .str "u1")]]), ("reading_sets", Json.arr #[
  Json.mkObj [("id", .str "rs1"), ("unit", .str "u1"), ("version", toJson 1), ("status", .str "open"), ("situations",
    Json.mkObj []), ("readings", Json.arr #[Json.mkObj [("id", .str "a"), ("kind", .str "norm"), ("content", rule true)],
      Json.mkObj [("id", .str "b"), ("kind", .str "norm"), ("content", rule false)]])]])]
def noActs : Json := (Json.parse ("{\"language\":\"ve.core@0.2\",\"profiles\":[\"norms@0\",\"readings@1\"," ++
  "\"relational-fol@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"person\":" ++
  "{\"description\":\"p\"}},\"constants\":{},\"predicates\":{\"paid\":{\"arguments\":[\"person\"],\"description\":" ++
  "\"d\",\"regulated\":{\"role\":\"plain\",\"default\":\"deny\"}}}}}")).toOption.getD .null
#guard [envA, noActs].map (fun e => err (VE.Readings.Run.validateOne "v" e setDoc)) ==
  ["UnsupportedProfile: Unsupported profile acts@0", "each other reading needs a distinguishing model id"]
-- D-33 for a joined act (A5's "and", A6's "or" outside the phrases; plain or a permission), the predicate named the
-- one whose act joins, first or last of several
#guard [env [("p", "plain", a5)], env [("p", "permission", a5)], env [("p", "plain", a6)]].map decode ==
  List.replicate 3 (d33 "p")
#guard [env [("a", "plain", a2), ("q", "plain", a5)], env [("a", "plain", a5), ("z", "plain", a2)]].map decode ==
  [d33 "q", d33 "a"]
-- every other act refusal (D-5's comma) is the decoder's own; without `acts@0` the block is refused as before
#guard decode (env [("p", "plain", "{0} seek, asylum")]) == "InvalidInput: act phrase for p has a comma outside a fixed phrase"
#guard decode (envA ["norms@0", "readings@1", "relational-fol@0"]) ==
  "fields do not match: expected [sorts, predicates, constants], got [acts, constants, predicates, sorts]"
-- the route's frame reads no constant's display (as before `acts@0`)
#guard decode (env [("paid", "plain", a2)] rdP [("ann", Json.mkObj [("sort", .str "person"), ("description", .str "d"),
  ("verbalisation", .str "Ann")])]) == "fields do not match: expected [sort, description], got [description, sort, verbalisation]"
-- the text map: the predicate D-4 names, never a prefix of it; another predicate's or another refusal is kept
def d4 (p : String) : String := s!"InvalidInput: act phrase for {p} joins acts with 'or' outside a fixed phrase"
#guard [d4 "pp", d4 "p"].map (VE.Readings.Wire.singleActsOnly ["p", "pp"]) == [d33 "pp", d33 "p"]
#guard [d4 "p", "InvalidInput: act phrase for q has a comma outside a fixed phrase"].map
  (VE.Readings.Wire.singleActsOnly ["q"]) == [d4 "p", "InvalidInput: act phrase for q has a comma outside a fixed phrase"]
-- the wordings of a `readings@1` environment's plain acts (review F1): the readings route runs an elaborate case on
-- the lower route without `readings@1`, so its row's `wordings` are that route's, with and without `norm-defaults@0`
def elabCase (kind : String) (e : Json) : Json :=
  Json.mkObj [("id", .str kind), ("kind", .str kind), ("environment", e), ("norms", Json.arr #[])]
def wordings (row : Json) : List String :=
  (((row.getObjValD "wordings").getObj?).toOption.map (·.toList.map (·.1))).getD []
#guard wordings (VE.Readings.Run.runLower (elabCase "norms-elaborate" envA)) == ["heard", "paid"]
#guard (VE.Readings.Run.runLower (elabCase "norms-elaborate" envA)).getObjValD "wordings" ==
  (VE.Norms.Run.runCaseReported (elabCase "norms-elaborate" (envA ["acts@0", "norms@0", "relational-fol@0"]))).getObjValD
    "wordings"
#guard (VE.Readings.Run.runLower (elabCase "norm-defaults-elaborate"
    (envA ["acts@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0"]))).getObjValD "wordings" ==
  (VE.NormDefaults.Run.runCaseReported (elabCase "norm-defaults-elaborate"
    (envA ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]))).getObjValD "wordings"
#guard wordings (VE.NormDefaults.Run.runCaseReported (elabCase "norm-defaults-elaborate"
    (envA ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]))) == ["heard", "paid"]

end VE.Readings.ActsExamples
