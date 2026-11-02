import VE.Service.Document
import VE.Cardinality.WireExamples

/-! The document mode's `cardinality@0` hook (quantities QT-A4): `cardinalityEnv`, the content branch of `contentOf`,
`cardinalityReport` and what `check` and `encode` do with them. `tests/test_cardinality_lean.py` checks the same answers
through the service and the relay. -/

namespace VE.Service.CardinalityExamples
open Lean VE.Service.Document
open VE.Cardinality.WireExamples (env)

def listed : List String := ["cardinality@0", "documents@1", "order@0", "relational-fol@0", "time@0"]
def environment (profiles : List String := listed) : Json := env.setObjVal! "profiles" (toJson profiles)

def statement (formula : Json) : Json := Json.mkObj [("format", .str "ve-cardinality@1"), ("formula", formula)]
def top : Json := statement (toJson [toJson "quantity", toJson ["top"]])
def low : Json := statement (toJson [toJson "quantity", toJson ["bottom"]])
def card (s : Json) : Json := Json.mkObj [("cardinality", s)]

def unit (id : String) (content : Json) (kind := "asserted") : Json := Json.mkObj [("id", .str id), ("span", toJson [0, 2]),
  ("kind", .str kind), ("meaning", .str "specified"), ("support", .str "testimony"), ("content", content)]

def text (e : Json) (units : List Json) (more : List (String × Json) := []) : String :=
  "---\n" ++ (Json.mkObj ([("format", .str "ve-document@1"), ("environment", e), ("units", toJson units)] ++ more)).compress ++
    "\n---\nA\n"

def run (t : String) (admit := true) : Except String Json :=
  checkCore (Json.mkObj [("id", .str "d"), ("document", .str t), ("admit", .bool admit)])

def said (t : String) : String := match run t with
  | .ok _ => "ok"
  | .error e => e

def graph (root : String) (nodes : List (String × Json)) : List (String × Json) :=
  [("graph", Json.mkObj [("root", .str root), ("nodes", toJson (nodes.map fun n =>
    Json.mkObj [("name", .str n.1), ("statement", n.2)]))])]

def decoded : Option VE.Cardinality.CardEnv := (VE.Cardinality.Wire.decodeEnvironment (environment)).toOption

/-! An admitted unit: its row holds the statement under the mode's meaning id, and CHECKED; no graph, no report. -/
def row : Json := (run (text environment [unit "u" (card top)])).toOption.getD .null
def rowUnit : Json := (((row.getObjValD "units").getArrVal? 0).toOption).getD .null
#guard row.getObjValD "status" == .str "ok"
#guard (row.getObjVal? "cardinality").toOption.isNone
#guard rowUnit.getObjValD "status" == .str "CHECKED"
#guard (rowUnit.getObjValD "content").getObjValD "formula" == top.getObjValD "formula"
#guard rowUnit.getObjValD "meaning_id" == (rowUnit.getObjValD "content").getObjValD "meaning_id"
#guard ((decoded.map fun w => (VE.Cardinality.Wire.decodeStatement w top).toOption.map (·.meaningId)).join.map Json.str) ==
  some (rowUnit.getObjValD "meaning_id")

/-! A graph: the report and its identities are the row's, when `check` asks for them. -/
def reported : Json := (run (text environment [unit "u" (card top)] (graph "u" [("u", top)]))).toOption.getD .null
def report : Json := reported.getObjValD "cardinality"
#guard ((report.getObjValD "report").getObjValD "root").getObjValD "name" == .str "u"
#guard (report.getObjValD "report").getObjValD "leaves" != toJson ([] : List Json)
#guard (decoded.map (Json.str ·.environmentId)) == some (report.getObjValD "environment_id")
#guard (decoded.map (Json.str ·.w6.environmentId)) == some (report.getObjValD "w6_environment_id")
#guard (decoded.map (Json.str ·.w6.targetId)) == some (report.getObjValD "w6_target_environment_id")
#guard (report.getObjValD "report_id") != .null
#guard ((run (text environment [unit "u" (card top)] (graph "u" [("u", top)])) (admit := false)).toOption.map
  fun j => (j.getObjVal? "cardinality").toOption.isNone) == some true

/-! Each node is a unit holding its statement, on both sides. -/
#guard said (text environment [unit "u" (card top)] (graph "u" [("u", top)])) == "ok"
#guard said (text environment [unit "u" (card top)] (graph "v" [("v", top)])) ==
  "claim graph node v is not a unit holding its statement"
#guard said (text environment [unit "u" (card low)] (graph "u" [("u", top)])) ==
  "claim graph node u is not a unit holding its statement"
#guard said (text environment [unit "u" .null "meta"] (graph "u" [("u", top)])) ==
  "claim graph node u is not a unit holding its statement"

/-! The gate over the list, then E2, on both sides; `documents@1` is optional without a graph. -/
#guard said (text (environment ["cardinality@0", "order@0", "relational-fol@0", "time@0"]) [unit "u" (card top)]) == "ok"
#guard said (text (environment ["cardinality@0", "norm-defaults@0", "norms@0", "readings@1"]) [unit "u" (card top)]) ==
  "UnsupportedProfile: Missing profile relational-fol@0"
#guard said (text (environment ["cardinality@0", "norms@0", "order@0", "relational-fol@0", "time@0"]) [unit "u" (card top)]) ==
  "UnsupportedProfile: cardinality@0 with norms@0"
#guard said (text (environment ["cardinality@0", "documents@1", "judgments@0", "order@0", "relational-fol@0", "time@0"])
  [unit "u" (card top)]) ==
  "UnsupportedProfile: cardinality@0 requires order@0, relational-fol@0 and time@0, optionally with documents@1"
#guard said (text ((environment).setObjVal! "cardinality_schema" (.str "x")) [unit "u" (card top)]) ==
  "UnsupportedProfile: Unsupported cardinality schema"

/-! Content: the profile's statements only, and those only under the profile. -/
#guard said (text environment [unit "u" (Json.mkObj [("ast", toJson ["top"])])]) ==
  "UnsupportedProfile: a cardinality@0 unit's content is a cardinality statement"
#guard said (text environment [unit "u" (card (Json.mkObj [("format", .str "x"), ("formula", toJson ["top"])]))]) ==
  "Unsupported cardinality format"
#guard said (text (Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson ["relational-fol@0"]),
  ("spec_revision", env.getObjValD "spec_revision"), ("vocabulary", Json.mkObj [("sorts", Json.mkObj []),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])])]) [unit "u" (card top)]) ==
  "UnsupportedProfile: cardinality content requires cardinality@0"

/-! What reads the first-order chain is refused by name; a null unit needs none of it. -/
#guard ["open_terms", "reading_sets", "narrowings"].all fun k =>
  said (text environment [unit "u" (card top)] [(k, toJson ([] : List Json))]) ==
    s!"UnsupportedProfile: {k} beside cardinality@0 is not composed"
#guard said (text environment [unit "u" (card top)] [("senses", Json.mkObj [])]) ==
  "UnsupportedProfile: senses beside cardinality@0 is not composed"

end VE.Service.CardinalityExamples
