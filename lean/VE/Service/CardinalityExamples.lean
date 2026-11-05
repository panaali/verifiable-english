import VE.Service.Document
import VE.Cardinality.WireExamples

/-! The document mode's `cardinality@0` hook (quantities QT-A4): `cardinalityEnv`, the content branch of `contentOf`,
`cardinalityReport` and what `environmentOf`, `check` and `encode` do with them, both sides of each.
`tests/test_cardinality_lean.py` checks the same answers through the service and the relay. Each guard through `check`
walks the whole mode for the trust mutants' probe, so those are folded into two; the rest read their definition alone. -/

namespace VE.Service.CardinalityExamples
open Lean VE.Service.Document
open VE.Cardinality.WireExamples (env)

def listed : List String := ["cardinality@0", "documents@1", "order@0", "relational-fol@0", "time@0"]
def environment (profiles : List String := listed) : Json := env.setObjVal! "profiles" (toJson profiles)
def statement (formula : List Json) : Json := Json.mkObj [("format", .str "ve-cardinality@1"), ("formula", toJson formula)]
def top : Json := statement [toJson "quantity", toJson ["top"]]
def low : Json := statement [toJson "quantity", toJson ["bottom"]]
def card (s : Json) : Json := Json.mkObj [("cardinality", s)]
def said {α : Type} : Except String α → String
  | .ok _ => "ok"
  | .error e => e

/-! `cardinalityEnv`: the gate over the list, then E2 and the rest of the decoder. -/
def decoded : Option Env := (cardinalityEnv environment).toOption
def w : Option VE.Cardinality.CardEnv := decoded.bind (·.cardinality)
#guard said (cardinalityEnv environment) == "ok" &&
  said (cardinalityEnv (environment ["cardinality@0", "order@0", "relational-fol@0", "time@0"])) == "ok"
#guard (decoded.map fun E => (E.profiles, E.block == .none, E.generated, E.legacy.isNone, E.rights, E.soft)) ==
  some (listed, true, false, true, false, false)
#guard (decoded.map (·.envId)) == (w.map (·.environmentId)) && (decoded.map (·.envId)) != none
#guard [(["cardinality@0", "norm-defaults@0", "norms@0", "readings@1"], "UnsupportedProfile: Missing profile relational-fol@0"),
  (["cardinality@0", "norms@0", "order@0", "relational-fol@0", "time@0"], s!"UnsupportedProfile: {VE.Cardinality.Wire.e2}"),
  (["cardinality@0", "data@0", "order@0", "relational-fol@0", "time@0"], "UnsupportedProfile: cardinality@0 with data@0"),
  (["cardinality@0", "documents@1", "judgments@0", "order@0", "relational-fol@0", "time@0"],
    s!"UnsupportedProfile: {VE.Cardinality.Wire.e2}")].all
  fun (ps, m) => said (cardinalityEnv (environment ps)) == m
#guard said (cardinalityEnv ((environment).setObjVal! "cardinality_schema" (.str "x"))) ==
  "UnsupportedProfile: Unsupported cardinality schema"

/-! `contentOf`: the profile's statements only, those only under the profile. -/
def plain : Json := Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson ["relational-fol@0"]),
  ("spec_revision", env.getObjValD "spec_revision"), ("vocabulary", Json.mkObj [("sorts", Json.mkObj []),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])])]
def content (E : Option Env) (c : Json) : Except String (UnitContent × String) := match E with
  | some E => contentOf E [] none .null "u" c
  | none => .error "no environment"
#guard (((content decoded (card top)).toOption).map fun (c, m) => (c.json.getObjValD "formula" == top.getObjValD "formula",
  c.json.getObjValD "meaning_id" == .str m, c.judged.isNone)) == some (true, true, true)
#guard ([(Json.mkObj [("ast", toJson ["top"])], "UnsupportedProfile: a cardinality@0 unit's content is a cardinality statement"),
  (card (Json.mkObj [("format", .str "x"), ("formula", toJson ["top"])]), "Unsupported cardinality format")].all
  fun (c, m) => said (content decoded c) == m) &&
  said (content ((environmentOf plain).toOption) (card top)) == "UnsupportedProfile: cardinality content requires cardinality@0"

/-! `environmentOf`: every position of the list routes to `cardinalityEnv`, and senses are refused by name. -/
#guard [["cardinality@0"], ["alternatives@0", "cardinality@0"], ["cardinality@0", "norms@0"]].all fun ps =>
  said (environmentOf (environment ps)) == said (cardinalityEnv (environment ps)) &&
    said (environmentOf (environment ps)) != "ok"
#guard said (environmentOf environment (senses := true)) == "UnsupportedProfile: senses beside cardinality@0 is not composed" &&
  said (environmentOf environment) == "ok"

/-! `cardinalityReport`: the report and its identities are the mode's; each node, wherever it stands, is a unit holding
its statement. -/
def graph (root : String) (nodes : List (String × Json)) : Json := Json.mkObj [("root", .str root),
  ("nodes", toJson (nodes.map fun n => Json.mkObj [("name", .str n.1), ("statement", n.2)]))]
def source (name : String) (mid : Option String) (kind : Json := .str "asserted") : SourceUnit :=
  { id := name, span := (0, 1), kind, decoded := .route .asserted, meaning := .null, support := "none",
    status := "CHECKED", parent := none, meaningId := mid }
def idOf (s : Json) : Option String := w.bind fun w => ((VE.Cardinality.Wire.decodeStatement w s).toOption).map (·.meaningId)
def reportOf (g : Json) (units : List SourceUnit) : Except String Json := match w with
  | some w => cardinalityReport w g units
  | none => .error "no environment"
def both : Json := graph "b" [("a", top), ("b", low)]
def asWritten : List SourceUnit := [source "a" (idOf top), source "b" (idOf low)]
def report : Json := (reportOf both asWritten).toOption.getD .null
#guard said (reportOf both asWritten) == "ok" && said (reportOf both asWritten.reverse) == "ok"
#guard ((report.getObjValD "report").getObjValD "root").getObjValD "name" == .str "b" && report.getObjValD "report_id" != .null
#guard (w.map (Json.str ·.environmentId)) == some (report.getObjValD "environment_id") &&
  (w.map (Json.str ·.w6.environmentId)) == some (report.getObjValD "w6_environment_id") &&
  (w.map (Json.str ·.w6.targetId)) == some (report.getObjValD "w6_target_environment_id")
def refused (name : String) : String := s!"claim graph node {name} is not an asserted unit holding its statement"
def quoted : Json := toJson [toJson "attributed", toJson "x", toJson "says", toJson "asserted"]
#guard [([source "b" (idOf low)], "a"), ([source "a" (idOf top)], "b"), ([source "a" (idOf low), source "b" (idOf low)], "a"),
  ([source "a" (idOf top), source "b" (idOf top)], "b"), ([source "a" none, source "b" (idOf low)], "a"),
  ([source "a" (idOf top), source "b" none], "b"), ([source "a" (idOf top) quoted, source "b" (idOf low)], "a"),
  ([source "a" (idOf top), source "b" (idOf low) (.str "meta")], "b")].all fun (us, n) => said (reportOf both us) == refused n

/-! `graphLabelled` and `bridgeAdmitted`: W6a's provenance rule's quoted half, both sides of each condition. -/
def labelled (label : Json) : Json :=
  (graph "a" [("a", top)]).setObjVal! "nodes" (toJson [Json.mkObj [("name", .str "a"), ("statement", top), ("label", label)]])
def bridge : Json := .str "bridge:accepts(x,q)"
def atQ (kind : Json) (m : Option String := idOf top) : List SourceUnit :=
  [{ source "q" m kind with decoded := (decodeRowKind false kind).toOption.getD (.route .asserted) }]
#guard said (reportOf (labelled bridge) (atQ quoted)) == "ok" &&
  ((reportOf (labelled bridge) (atQ quoted)).toOption.getD .null).getObjValD "leaf_labels" ==
    toJson [Json.mkObj [("name", .str "a"), ("label", bridge)]] &&
  (report.getObjValD "leaf_labels") == toJson ([] : List Json) &&
  said (reportOf (labelled (.str "asserted")) [source "a" (idOf top)]) == "ok"
def notAdmitted (l : String) : String := s!"AdmissionError: node a is not admitted under label {l}"
#guard [(atQ quoted (idOf low), "bridge:accepts(x,q)"), (atQ quoted none, "bridge:accepts(x,q)"), (atQ (.str "asserted"), "bridge:accepts(x,q)"),
  (atQ quoted, "bridge:accepts(y,q)"), (atQ quoted, "bridge:accepts(x,r)"), (atQ quoted, "bridge:accepts(x, q)"), (atQ quoted, "open:q")].all
    fun (us, l) => said (reportOf (labelled (.str l)) us) == notAdmitted l
#guard said (reportOf (labelled (.num 7)) (atQ quoted)) == "claim graph node label must be a string"
-- a deduction is never a bridge, and the same leaf is
def bridgedNode (deduction : Option (List String × Unit)) : Bool := match w with
  | some w => match (VE.Cardinality.Wire.decodeStatement w top).toOption with
    | some adm => bridgeAdmitted (Std.HashMap.ofList ((atQ quoted).map fun u => (u.id, u))) ⟨"a", adm, 1, deduction⟩ "bridge:accepts(x,q)"
    | none => false
  | none => false
#guard bridgedNode none && !bridgedNode (some ([], ()))
#guard (graphLabelled (Json.mkObj [("nodes", toJson (List.replicate 1001 (Json.mkObj [("label", .num 7)])))])).toOption.isNone &&
  said (graphLabelled (Json.mkObj [("nodes", toJson (List.replicate 1001 (Json.mkObj [("label", .num 7)])))])) ==
    VE.Cardinality.Document.nodeLimit

/-! `check` and `encode`: an admitted row, with the report only when it is asked for. -/
def unit (id : String) (c : Json) : Json := Json.mkObj [("id", .str id), ("span", toJson [0, 2]), ("kind", .str "asserted"),
  ("meaning", .str "specified"), ("support", .str "testimony"), ("content", c)]
def text (e : Json) (units : List Json) (more : List (String × Json) := []) : String :=
  "---\n" ++ (Json.mkObj ([("format", .str "ve-document@1"), ("environment", e), ("units", toJson units)] ++ more)).compress ++
    "\n---\nA\n"
def run (t : String) (claims := true) : Except String Json :=
  checkCore (Json.mkObj [("id", .str "d"), ("document", .str t), ("admit", .bool claims)])
def one : List Json := [unit "u" (card top)]
def withGraph : List (String × Json) := [("graph", graph "u" [("u", top)])]
def rowOf (t : String) (claims := true) : Json := (run t claims).toOption.getD .null
#guard let row := rowOf (text environment one)
  let u := ((row.getObjValD "units").getArrVal? 0).toOption.getD .null
  row.getObjValD "status" == .str "ok" && (row.getObjVal? "cardinality").toOption.isNone &&
    u.getObjValD "status" == .str "CHECKED" && (u.getObjValD "content").getObjValD "formula" == top.getObjValD "formula" &&
    u.getObjValD "meaning_id" == (u.getObjValD "content").getObjValD "meaning_id" &&
    (idOf top).map Json.str == some (u.getObjValD "meaning_id") &&
    (((rowOf (text environment one withGraph)).getObjValD "cardinality").getObjValD "report").getObjValD "root" != .null &&
    ((rowOf (text environment one withGraph) (claims := false)).getObjVal? "cardinality").toOption.isNone

/-! `check`: what reads the first-order chain is refused by name; the flag `decodedEnvironment` keeps is the retained
reader's; a graph's nodes are bound on this path too. -/
#guard (["open_terms", "reading_sets", "narrowings"].all fun k => said (run (text environment one [(k, toJson ([] : List Json))])) ==
    s!"UnsupportedProfile: {k} beside cardinality@0 is not composed") &&
  said (run (text environment one [("graph", graph "v" [("v", top)])])) == refused "v" &&
  said (run ("---\n" ++ (Json.mkObj [("format", .str "ve-document@1"), ("environment", plain), ("units", toJson [Json.mkObj
    [("id", .str "u"), ("span", toJson [0, 2]), ("kind", .str "asserted"), ("meaning", .str "specified"),
     ("support", .str "testimony"), ("surface", .str "strict"), ("content", Json.mkObj [("fence", .str "u")])]])]).compress ++
    "\n---\nA\n```ve u\nthere is\n```\n")) !=
    unavailable "a strict fence over a statement layer is read by its retained reader"

end VE.Service.CardinalityExamples
