import VE.Norms.Run
import VE.Order.Wire
import VE.Service.EnglishRun

/-! `ve_response_decode`: the Lean side of the differential test of the service
response schemas (`ve/backends/lean_service_schema/`). It decodes a response line
with the Lean decoders the runners' outputs come from (`Bridge.decodeFormula`,
`Order.Wire.decodeFormula`, `Route.Admission.decodeKind`, `parseLabel`,
`Route.Wire.decodeNodes` with `Route.verifyOrder`, `EnglishRun`'s token form) and
the dispatch functions of the runners (`Route.Run.caseKind`, `generatorOf`,
`Norms.Run.usesNormsPath`), and checks the links to the request that the runners
guarantee. Test tooling only: nothing imports it and no theorem depends on it.

Each input line is `{"mode", "request": {"id", "cases", "bytes"}, "responses": [...]}`;
the output line is an array with `"accept"` or `"reject: <reason>"` per response. -/
namespace ResponseDecode
open Lean

abbrev Check := Except String Unit

def need (b : Bool) (message : String) : Check :=
  if b then pure () else throw message

/-- The object has exactly the required fields, plus any of the optional ones. -/
def shape (j : Json) (required optional : List String) : Check := do
  let keys := (← VE.Bridge.fields j).map Prod.fst
  need (required.all keys.contains) s!"fields {keys}: missing one of {required}"
  need (keys.all (fun k => required.contains k || optional.contains k)) s!"unexpected field in {keys}"

def field (j : Json) (k : String) : Except String Json := j.getObjVal? k

def isField (j : Json) (k : String) (v : Json) : Bool :=
  match j.getObjVal? k with
  | .ok x => x == v
  | .error _ => false

def has (j : Json) (k : String) : Bool := (j.getObjVal? k).toBool

def bool (j : Json) : Check := do let _ ← j.getBool?

def nat (j : Json) : Check := do let _ ← j.getNat?

def string (j : Json) : Check := do let _ ← j.getStr?

def text (j : Json) : Check := do
  need (!(← j.getStr?).isEmpty) "empty message"

def array (j : Json) (f : Json → Check) : Check := do
  for x in ← j.getArr? do f x

def hex64 (j : Json) : Check := do
  let s ← j.getStr?
  need (s.length == 64 && s.all (fun c => c.isDigit || ('a' ≤ c && c ≤ 'f'))) "not a SHA-256 digest"

def folFormula (j : Json) : Check := do let _ ← VE.Bridge.decodeFormula 64 j

def orderFormula (j : Json) : Check := do let _ ← VE.Order.Wire.decodeFormula 64 j

def kind (j : Json) : Check := do let _ ← VE.Route.Admission.decodeKind 16 j

/-- The request's case at a path of object fields. -/
def path (j : Json) : List String → Except String Json
  | [] => pure j
  | k :: ks => do path (← j.getObjVal? k) ks

def length (j : Json) : Except String Nat := do pure (← j.getArr?).size

/-- The values of `values`: one per requested formula, and never an empty document. -/
def values (row case : Json) : Check := do
  let vs ← (← field row "values").getArr?
  for v in vs do bool v
  need (!vs.isEmpty) "empty values"
  need (vs.size == (← length (← field case "ast"))) "one value per formula"

/-- A successful result: the request's (string) id, status ok, then exactly `fields`. -/
def okRow (row case : Json) (required : List String) (optional : List String := []) : Check := do
  shape row (["id", "status"] ++ required) optional
  need (isField row "status" (.str "ok")) "status"
  let id ← (← field row "id").getStr?
  need (isField case "id" (.str id)) "id is not the request's"

def errorRow (row case : Json) (extra : List String) : Check := do
  shape row (["id", "status", "error"] ++ extra) []
  need (isField row "status" (.str "error")) "status"
  need ((← field row "id") == case.getObjValD "id") "id is not the request's"
  text (← field row "error")
  if extra.contains "valid" then need (isField row "valid" (.bool false)) "valid"

/-- `Service.Protocol.caseError`. -/
def caseErrorRow (row : Json) (index : Nat) (valid : Bool) : Check := do
  shape row (["status", "case_index", "error"] ++ if valid then ["valid"] else []) []
  need (isField row "status" (.str "error")) "status"
  need ((← (← field row "case_index").getNat?) == index) "case index"
  text (← field row "error")
  if valid then need (isField row "valid" (.bool false)) "valid"

def firstOk (checks : List (Unit → Check)) : Check :=
  match checks with
  | [] => throw "no alternative"
  | c :: cs => match c () with
    | .ok () => pure ()
    | .error m => match firstOk cs with
      | .ok () => pure ()
      | .error m' => throw s!"{m}; {m'}"

/-! ## Results by mode -/

/-- `Route.Run.claimJson` of a node the request declared (`admit_labels_decoded`);
an assumption is a leaf, a node without a deduction (`admit_report_sound`). -/
def claim (j case : Json) (leaf : Bool := false) : Check := do
  shape j ["name", "ast"] ["label"]
  string (← field j "name")
  folFormula (← field j "ast")
  if let .ok l := j.getObjVal? "label" then
    need ((← l.getStr?) != "asserted") "explicit default label"
  let nodes ← (← path case ["document", "graph", "nodes"]).getArr?
  let project := fun (x : Json) => ["name", "ast", "label"].map (fun k => (x.getObjVal? k).toOption)
  let isLeaf := fun (n : Json) => !has n "premises" && !has n "certificate"
  need (nodes.any (fun n => (n.getObj?).toBool && project n == project j && (!leaf || isLeaf n)))
    "not a node of the request"

def admission (row case : Json) : Check := do
  okRow row case ["admitted", "report", "report_id", "kinds"]
  need (isField row "admitted" (.bool true)) "admitted"
  let report ← field row "report"
  shape report ["root", "assumptions"] []
  let root ← field report "root"
  claim root case
  need ((← field root "name") == (← path case ["document", "graph", "root"])) "root"
  array (← field report "assumptions") (claim · case true)
  hex64 (← field row "report_id")
  let kinds ← field row "kinds"
  array kinds kind
  let units ← (← path case ["document", "units"]).getArr?
  let requested ← units.mapM (field · "kind")
  need (kinds == .arr requested) "kinds are not the request's unit kinds"

def dependencyOrder (row case : Json) : Check := do
  okRow row case ["order"]
  let order ← VE.Bridge.strings (← field row "order")
  let nodes ← VE.Route.Wire.decodeNodes (← field case "nodes")
  let names := VE.Route.nodeNames nodes
  need ((names.find? (fun n => names.count n > 1)).isNone) "duplicate node"
  need (VE.Route.verifyOrder nodes order) "not a dependency order of the request's nodes"

def bundle (row case : Json) : Check := do
  okRow row case ["checked", "lemmas"]
  let requested ← (← field case "lemmas").getArr?
  need ((← (← field row "checked").getNat?) == requested.size) "one check per requested lemma"
  let lemmas ← field row "lemmas"
  array lemmas hex64
  need (lemmas == .arr (← requested.mapM (field · "meaning_id"))) "lemmas are not the request's"

def background (row case : Json) : Check := do
  okRow row case ["background", "premises", "generators"]
  let bg ← field row "background"
  array bg folFormula
  array (← field row "premises") folFormula
  need (bg == (← field row "premises")) "premises differ from background"
  let gs ← field row "generators"
  array gs (fun g => do need (VE.Route.Background.generators.contains (← g.getStr?)) "generator")
  need ((← length bg) == (← length gs)) "one generator per premise"

def label (row case : Json) : Check := do
  okRow row case ["label"]
  let l ← (← field row "label").getStr?
  need (VE.Route.Admission.parseLabel l).isSome "not a canonical label"
  need (isField case "label" (.str l)) "not the request's label"

def routeError (row case : Json) : Check := do
  let message ← (← field row "error").getStr?
  let generator := VE.Route.Run.generatorOf message
  let valid := case.getObjValD "kind" == .str "certificate"
  errorRow row case ((if generator.isSome then ["generator"] else []) ++ if valid then ["valid"] else [])
  if let some g := generator then need (isField row "generator" (.str g)) "generator"

def routeOk (row case : Json) : Check := do
  need (case.getObj?).toBool "case is not an object"
  match ← VE.Route.Run.caseKind case with
  | "evaluate" => do okRow row case ["values"]; values row case
  | "countermodel" => do okRow row case ["refutes"]; bool (← field row "refutes")
  | "certificate" => do
    okRow row case ["valid", "background"]
    bool (← field row "valid"); nat (← field row "background")
  | "dependency-order" => dependencyOrder row case
  | "bundle" => bundle row case
  | "background" => background row case
  | "label" => label row case
  | "admission" => admission row case
  | k => throw s!"no result for kind {k}"

def route (row case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow row index false, fun _ => routeError row case, fun _ => routeOk row case]

def objects (j : Json) (required : List String) (f : Json → Check) : Check :=
  array j (fun x => do shape x required []; f x)

def normsElaborate (row case : Json) : Check := do
  okRow row case ["order", "background", "premises", "conflict_targets", "fragment"]
  let _ ← VE.Bridge.strings (← field row "order")
  objects (← field row "background") ["generator", "ast"] fun x => do
    need (["definitions", "literals", "profile"].contains (← (← field x "generator").getStr?)) "generator"
    folFormula (← field x "ast")
  objects (← field row "premises") ["label", "ast"] fun x => do
    need ((← (← field x "label").getStr?).startsWith "layer:norms:") "layer label"
    folFormula (← field x "ast")
  objects (← field row "conflict_targets") ["target", "sorts", "ast"] fun x => do
    string (← field x "target")
    let _ ← VE.Bridge.strings (← field x "sorts")
    folFormula (← field x "ast")
  bool (← field row "fragment")

def normsOk (row case : Json) : Check := do
  match ← VE.Route.Run.caseKind case with
  | "admission" => admission row case
  | "norms-elaborate" => normsElaborate row case
  | "norms-certificate" => do
    okRow row case ["valid", "background", "layers"]
    bool (← field row "valid"); nat (← field row "background"); nat (← field row "layers")
  | "norms-conflict" =>
    if has case "witness" then do
      okRow row case ["verdict", "target", "targets"]
      need (["CONFLICT", "UNKNOWN"].contains (← (← field row "verdict").getStr?)) "verdict"
      let target ← (← field row "target").getStr?
      let targets ← VE.Bridge.strings (← field row "targets")
      need (targets.contains target) "target is not a regenerated target"
      need ((← path case ["witness", "target"]) == .str target) "not the requested target"
    else do
      okRow row case ["verdict", "targets"] ["detail"]
      let verdict ← (← field row "verdict").getStr?
      need (["CONFLICT-FREE", "UNKNOWN"].contains verdict) "verdict"
      let _ ← VE.Bridge.strings (← field row "targets")
      if let .ok d := row.getObjVal? "detail" then
        string d
        need (verdict == "UNKNOWN") "detail without UNKNOWN"
  | k => throw s!"no norms result for kind {k}"

def norms (row case : Json) (index : Nat) : Check :=
  if VE.Norms.Run.usesNormsPath case then
    firstOk [fun _ => caseErrorRow row index false, fun _ => errorRow row case [],
      fun _ => normsOk row case]
  else route row case index

def evaluate (row case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow row index false, fun _ => errorRow row case [], fun _ => do
    need (case.getObj?).toBool "case is not an object"
    match case.getObjVal? "kind" with
    | .error _ => do
      okRow row case ["values", "value", "canonical"]
      values row case
      let vs ← (← field row "values").getArr?
      need (isField row "value" (.bool (vs.all (· == .bool true)))) "value is not the conjunction"
      string (← field row "canonical")
    | .ok k => do
      need (k == .str "countermodel") "unknown kind"
      okRow row case ["refutes"]
      bool (← field row "refutes")]

def checkCertificate (row case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow row index true, fun _ => errorRow row case ["valid"], fun _ => do
    okRow row case ["valid"]
    bool (← field row "valid")]

def order (row case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow row index true, fun _ => errorRow row case ["valid"], fun _ => do
    match ← (← field case "kind").getStr? with
    | "surface" => do
      okRow row case ["ast"]
      let fs ← (← field row "ast").getArr?
      need (!fs.isEmpty) "empty document"
      for f in fs do orderFormula f
    | "evaluate" => do okRow row case ["values"]; values row case
    | "countermodel" => do okRow row case ["refutes"]; bool (← field row "refutes")
    | "certificate" => do okRow row case ["valid"]; bool (← field row "valid")
    | k => throw s!"no order result for kind {k}"]

def token (j : Json) : Check := do
  let _ ← VE.English.ServiceRun.decodeTok j
  need (j == VE.English.ServiceRun.encodeTok (← VE.English.ServiceRun.decodeTok j)) "token"

def englishItem (j case : Json) : Check := do
  shape j ["parsed", "checked", "rendered", "roundtrip"] []
  let parsed ← field j "parsed"
  unless parsed.isNull do array parsed folFormula
  let checked ← (← field j "checked").getBool?
  let rendered ← field j "rendered"
  unless rendered.isNull do array rendered token
  let roundtrip ← (← field j "roundtrip").getBool?
  if checked then
    need (!rendered.isNull) "checked without rendering"
    let formulas := (case.getObjVal? "formulas" >>= Json.getArr?).toOption
    need (formulas.any (!·.isEmpty)) "checked without formulas"
  else need (rendered.isNull && !roundtrip) "rendering or roundtrip without a check"

def english (row case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow row index false,
    fun _ => do
      shape row ["status", "error"] []
      need (isField row "status" (.str "error")) "status"
      text (← field row "error"),
    fun _ => do
      shape row ["admissible", "covers", "results"] []
      bool (← field row "admissible"); bool (← field row "covers")
      let results ← (← field row "results").getArr?
      let cases ← (← field case "cases").getArr?
      need (results.size == cases.size) "one result per case"
      for (item, c) in results.zip cases do englishItem item c]

def standalone (mode : String) (r case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow r index false,
    fun _ => errorRow r case [],
    fun _ => do
      if mode == "environment" then
        okRow r case ["environment_id", "profiles", "family"]
        hex64 (← field r "environment_id")
        let _ ← VE.Bridge.strings (← field r "profiles")
        need ((← field r "profiles") == (← path case ["environment", "profiles"])) "profiles"
        let f ← (← field r "family").getStr?
        need (["fol", "closure", "closure+n-ary", "order"].contains f) "family"
      else if mode == "model" then
        okRow r case ["valid", "model_id"]
        need (isField r "valid" (.bool true)) "valid"
        hex64 (← field r "model_id")
      else
        okRow r case ["kind", "identity_id"]
        need ((← field r "kind") == (← field case "kind")) "kind"
        let k ← (← field r "kind").getStr?
        need (["source", "meaning", "model", "claim", "edge"].contains k) "kind"
        hex64 (← field r "identity_id")]

def row (mode : String) (r case : Json) (index : Nat) : Check :=
  match mode with
  | "evaluate" => evaluate r case index
  | "check-certificate" => checkCertificate r case index
  | "order" => order r case index
  | "route" => route r case index
  | "norms" => norms r case index
  | "english" => english r case index
  | "environment" | "model" | "identity" => standalone mode r case index
  | m => throw s!"unknown mode {m}"

/-- `Service.Protocol`: a line error, or one result per case with exact counts. -/
def response (mode : String) (request r : Json) : Check := do
  let nonce ← field request "id"
  if isField r "status" (.str "error") then
    shape r ["id", "status", "error"] []
    need ((← field r "id") == nonce && (← (field r "id")).getStr?.toBool) "id is not the nonce"
    text (← field r "error")
  else
    shape r ["id", "status", "mode", "results", "counts"] []
    need (isField r "status" (.str "ok")) "status"
    need ((← field r "id") == nonce && (← (field r "id")).getStr?.toBool) "id is not the nonce"
    need (isField r "mode" (.str mode)) "mode"
    let cases ← (← field request "cases").getArr?
    let results ← (← field r "results").getArr?
    need (results.size == cases.size) "one result per case"
    for i in [:results.size] do
      match row mode results[i]! cases[i]! i with
      | .ok () => pure ()
      | .error m => throw s!"result {i}: {m}"
    let counts ← field r "counts"
    shape counts ["cases", "bytes", "errors"] []
    need ((← (← field counts "cases").getNat?) == cases.size) "counts.cases"
    need ((← field counts "bytes") == (← field request "bytes")) "counts.bytes"
    let errors := (results.filter (fun x => isField x "status" (.str "error"))).size
    need ((← (← field counts "errors").getNat?) == errors) "counts.errors"

def verdict (mode : String) (request r : Json) : Json :=
  match response mode request r with
  | .ok () => .str "accept"
  | .error m => .str s!"reject: {m}"

def line (text : String) : Except String Json := do
  let j ← Json.parse text
  let mode ← (← field j "mode").getStr?
  let request ← field j "request"
  let responses ← (← field j "responses").getArr?
  pure (.arr (responses.map (verdict mode request)))

end ResponseDecode

def main : IO UInt32 := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  repeat
    let text ← stdin.getLine
    if text.isEmpty then break
    match ResponseDecode.line text with
    | .ok out => stdout.putStrLn out.compress
    | .error m => stdout.putStrLn (Lean.Json.str s!"invalid input: {m}").compress
    stdout.flush
  return 0
