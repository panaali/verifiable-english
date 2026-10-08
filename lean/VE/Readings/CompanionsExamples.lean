import VE.Readings.Companions

/-! The fixtures of RD-4a's merge and split (docs/spec/readings-defaults.md 8.4, 5 rows 6 to 11), each a `#guard`
on `mergeCompanions`, `mergeOpenTerms` and `splitCase`; the service fixtures are in
`tests/test_readings_companions_lean.py`. Each claim of the merge has a fixture each way: identical declarations
unite (F-C5) and different ones are refused (F-C2); identical open terms unite and different ones are refused
(F-C10); a coupling is refused exactly when it names a companion set (F-C9). -/
namespace VE.Readings.CompanionsExamples
open Lean
open VE.Readings.Wire

def sortJ (d : String) : Json := Json.mkObj [("description", .str d)]
def predJ (args : List String) : Json := Json.mkObj [("arguments", toJson args), ("description", .str "d")]
def envJ (sorts preds : List (String × Json)) (profiles : List String := ["norms@0", "relational-fol@0"]) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("constants", Json.mkObj []), ("predicates", Json.mkObj preds),
      ("sorts", Json.mkObj sorts)])]

def errorOf {α : Type} : Except String α → String
  | .error e => e
  | .ok _ => ""

def namesIn (m : Json) (k : String) : List String := (entries ((m.getObjValD "vocabulary").getObjValD k)).map (·.1)

def people : List (String × Json) := [("bearer", sortJ "bearer"), ("person", sortJ "person"), ("state", sortJ "state")]
def avoid (first : String) : List (String × Json) := [("avoid_life_required", predJ [first, "person"])]

/-! F-C2: a predicate declared `(bearer, person)` and `(state, person)` -/
#guard errorOf (mergeCompanions [("rs_a@1:0", envJ people (avoid "bearer")), ("rs_a@1:1", envJ people (avoid "state"))]) ==
  "InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare avoid_life_required differently"

/-! F-C4 and 5 row 9: language, revision and profiles agree -/
#guard errorOf (mergeCompanions [("rs_a@1:0", envJ people []),
    ("rs_a@1:1", envJ people [] ["norm-defaults@0", "norms@0", "relational-fol@0"])]) ==
  "InvalidInput: the readings of rs_a declare different profiles"
#guard errorOf (mergeCompanions [("rs_a@1:0", envJ people []),
    ("rs_a@1:1", (envJ people []).setObjVal! "language" (.str "ve.core@0.1"))]) ==
  "InvalidInput: the readings of rs_a declare different language"
#guard errorOf (mergeCompanions [("rs_a@1:0", envJ people []), ("rs_a@1:1", (envJ people []).setObjVal! "extra" 1)]) ==
  "InvalidInput: the readings of rs_a declare different extra"

/-! F-C5: identical sorts are one sort; `readings@1` is added, the profiles sorted -/
def fc5 : Json := match mergeCompanions [("rs_a@1:0", envJ [("person", sortJ "a human person")] (avoid "person")),
    ("rs_a@1:1", envJ [("person", sortJ "a human person"), ("state", sortJ "state")] (avoid "person"))] with
  | .ok m => m
  | .error _ => .null
#guard namesIn fc5 "sorts" == ["person", "state"]
#guard namesIn fc5 "predicates" == ["avoid_life_required"]
#guard (fc5.getObjValD "profiles").compress == "[\"norms@0\",\"readings@1\",\"relational-fol@0\"]"

/-! One normal form: the same entries in another key order are another tree (`jeq` false), and the same after
`normJ`, so `componentOf` merges normalized companions (the request's key order decides nothing) -/
def personAB : Json := Json.mkObj [("description", .str "p"), ("verbalisation", .str "v")]
def personBA : Json := Json.mkObj [("verbalisation", .str "v"), ("description", .str "p")]
#guard !jeq personAB personBA
#guard jeq (normJ personAB) (normJ personBA)
#guard (mergeCompanions [("rs_a@1:0", envJ [("person", personAB)] []), ("rs_a@1:1", envJ [("person", personBA)] [])]) matches .error _
#guard (mergeCompanions [("rs_a@1:0", normJ (envJ [("person", personAB)] [])),
    ("rs_a@1:1", normJ (envJ [("person", personBA)] []))]) matches .ok _

/-! F-C10: open terms united by name; a repeated name only with the same entry; typed in the merged frame -/
def term (necessary : List Json) : Json := Json.mkObj [("name", .str "ill_treatment"), ("arguments", Json.arr #[]),
  ("decided_by", .str "court"), ("jurisdiction", .str "universal"), ("necessary", Json.arr necessary.toArray),
  ("sufficient", Json.arr #[]), ("factors", Json.arr #[]), ("precedents", Json.arr #[]), ("version", 1)]
def someone : Json := Json.arr #[.str "exists", .str "person", Json.arr #[.str "unary", .str "avoid_life_required",
  Json.arr #[.str "var", 0]]]
def companionJ (ts : List Json) : Json :=
  Json.mkObj [("environment", envJ [("person", sortJ "p")] [("avoid_life_required", predJ ["person"])]),
    ("open_terms", Json.arr ts.toArray)]
#guard (match mergeOpenTerms [("rs_a@1:0", companionJ [term [someone]]), ("rs_a@1:1", companionJ [term [someone]])] with
  | .ok ts => ts.length == 1
  | .error _ => false)
#guard errorOf (mergeOpenTerms [("rs_a@1:0", companionJ [term []]), ("rs_a@1:1", companionJ [term [someone]])]) ==
  "InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare open term ill_treatment differently"
-- a condition over a predicate the merged frame does not declare
def elsewhere : Json := Json.arr #[.str "exists", .str "person", Json.arr #[.str "unary", .str "greet_required",
  Json.arr #[.str "var", 0]]]
#guard (mergeOpenTerms [("rs_a@1:0", companionJ [term [elsewhere]])]) matches .error _

/-! The split (F-C9, F-C11, F-C12 and `split_keeps_links` on one document) -/
def companionReading (id : String) : Json := Json.mkObj [("id", .str id), ("kind", .str "norm"),
  ("companion", companionJ [term [someone]])]
def plainReading (id : String) : Json := Json.mkObj [("id", .str id), ("kind", .str "norm")]
def setJ (id unit : String) (readings : List Json) : Json := Json.mkObj [("id", .str id), ("unit", .str unit),
  ("version", 1), ("status", .str "open"), ("readings", Json.arr readings.toArray)]
def narrowingJ (id set : String) : Json := Json.mkObj [("id", .str id), ("set", .str set), ("version", 1),
  ("keeps", Json.arr #[.str "r0"]), ("by", .str "w"), ("reason_spans", Json.arr #[.str "u0"])]
def couplingJ (id : String) (sets : List String) : Json := Json.mkObj [("id", .str id), ("axis", .str "who"),
  ("by", .str "w"), ("reason_spans", Json.arr #[.str "u0"]),
  ("sets", Json.arr (sets.map (fun s => Json.mkObj [("set", .str s), ("version", 1)])).toArray)]
def docJ (couplings : List Json) : Json := Json.mkObj [
  ("units", Json.arr #[Json.mkObj [("id", .str "u0"), ("kind", .str "norm"), ("content", .str "main")],
    Json.mkObj [("id", .str "u_a"), ("content", .str "a")], Json.mkObj [("id", .str "u_m")]]),
  ("reading_sets", Json.arr #[setJ "rs_a" "u_a" [companionReading "r0", companionReading "r1"],
    setJ "rs_m" "u_m" [plainReading "m0", plainReading "m1"]]),
  ("narrowings", Json.arr #[narrowingJ "n_a" "rs_a", narrowingJ "n_m" "rs_m"]),
  ("couplings", Json.arr couplings.toArray),
  ("open_terms", Json.arr #[.str "main_term"])]
def parts : List (String × Json × Json) := match splitCase (envJ [] []) (docJ []) with
  | .ok ps => ps
  | .error _ => []
def partDoc (name : String) : Json := ((parts.find? (·.1 == name)).map (·.2.2)).getD .null
def idsAt (name k : String) : List String := (arr (partDoc name) k).map (fun x => strOf (x.getObjValD "id"))
#guard parts.map (·.1) == ["main", "rs_a"]
#guard idsAt "main" "reading_sets" == ["rs_m"] && idsAt "rs_a" "reading_sets" == ["rs_a"]
#guard idsAt "main" "narrowings" == ["n_m"] && idsAt "rs_a" "narrowings" == ["n_a"]
-- the companion set's unit stays in main without its content; the component has it as written and the cited unit
#guard idsAt "main" "units" == ["u0", "u_a", "u_m"]
#guard ((arr (partDoc "main") "units")[1]?.map (·.getObjValD "content")).isEqSome Json.null
#guard idsAt "rs_a" "units" == ["u0", "u_a"]
#guard ((arr (partDoc "rs_a") "units")[0]?.map (fun u => (entries u).map (·.1))).isEqSome ["id"]
-- main keeps only its own open terms; the component has its companions' merged ones
#guard (arr (partDoc "main") "open_terms").length == 1 && (arr (partDoc "rs_a") "open_terms").length == 1
#guard ((arr (partDoc "rs_a") "open_terms")[0]?.map nameText).isEqSome "ill_treatment"
-- the component's environment is the merged one, `readings@1` added
#guard ((parts.find? (·.1 == "rs_a")).map (fun p => ((p.2.1.getObjValD "profiles").compress))).isEqSome
  "[\"norms@0\",\"readings@1\",\"relational-fol@0\"]"
/-! F-C9 both ways: a coupling naming the companion set is refused; one over main sets stays in main -/
#guard errorOf (splitCase (envJ [] []) (docJ [couplingJ "c1" ["rs_m", "rs_a"]])) ==
  "InvalidInput: coupling c1 links rs_a and rs_m, which do not share one vocabulary"
#guard (match splitCase (envJ [] []) (docJ [couplingJ "c2" ["rs_m", "rs_x"]]) with
  | .ok ps => ps.map (fun p => (arr p.2.2 "couplings").length) == [1, 0]
  | .error _ => false)
/-! F-C3 (5 row 6) -/
#guard errorOf (companionSets (Json.mkObj [("reading_sets",
    Json.arr #[setJ "rs_a" "u_a" [companionReading "r0", plainReading "r1"]])])) ==
  "InvalidInput: reading set rs_a mixes readings with and without their own vocabulary"
/-! Without a companion the document is one case, unchanged (conservativity, 4.6) -/
def plainDoc : Json := Json.mkObj [("units", Json.arr #[Json.mkObj [("id", .str "u_m")]]),
  ("reading_sets", Json.arr #[setJ "rs_m" "u_m" [plainReading "m0", plainReading "m1"]])]
#guard (match splitCase (envJ [] []) plainDoc with
  | .ok [(n, e, d)] => n == "main" && jeq e (envJ [] []) && jeq d plainDoc
  | _ => false)

end VE.Readings.CompanionsExamples
