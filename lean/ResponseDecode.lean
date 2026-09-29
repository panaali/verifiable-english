import VE.Norms.Run
import VE.Order.Wire
import VE.Service.EnglishRun

/-! `ve_response_decode`: the Lean side of the tests of service responses. Test tooling
only: nothing imports it and no theorem depends on it.

* `decode` is the differential oracle of the client's response schemas
  (`ve/backends/lean_service_schema/`): binding to the request (nonce, mode, each
  result's position and case digest, the identity fields the runners echo from the
  case) and well-formedness, decoded with the Lean decoders the runners' outputs come
  from (`Bridge.decodeFormula`, `Order.Wire.decodeFormula`, `Route.Admission.decodeKind`,
  `parseLabel`, `EnglishRun`'s token form) and the runners' dispatch
  (`Route.Run.caseKind`, `Norms.Run.usesNormsPath`).
* `invariants` is `decode` and the content the runners guarantee, which the client does
  not check (docs/spec/lean-service.md, threat model): counts regenerated from the
  environment, graph unfoldings, dependency orders, distinct layers and conflict targets
  with their declared argument sorts, verdict details, English check consistency. The
  tests require every genuine service response to satisfy it.

Each input line is `{"check"?: "decode" | "invariants", "mode", "request": {"id", "cases",
"digests", "bytes"}, "responses": [...]}`, where `digests` is `null` when the request's cases
text does not split into cases; the output line is an array with `"accept"`
or `"reject: <reason>"` per response. -/
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

/-- A formula the runner generated: `Bridge.decodeFormula`'s grammar at any depth. Each
level of a formula adds at least two characters to its rendering, so that length is
enough fuel. -/
def generatedFormula (j : Json) : Check := do let _ ← VE.Bridge.decodeFormula j.compress.length j

def orderFormula (j : Json) : Check := do let _ ← VE.Order.Wire.decodeFormula 64 j

def kind (j : Json) : Check := do let _ ← VE.Route.Admission.decodeKind 16 j

/-- The request's case at a path of object fields. -/
def path (j : Json) : List String → Except String Json
  | [] => pure j
  | k :: ks => do path (← j.getObjVal? k) ks

def length (j : Json) : Except String Nat := do pure (← j.getArr?).size

/-! ## Counts of regenerated lists (schema README: Counts) -/

/-- The members of the request's array or object at `p`. -/
def members (case : Json) (p : List String) : Except String (List Json) := do
  match ← path case p with
  | .arr xs => pure xs.toList
  | .obj kvs => pure (kvs.foldl (fun acc _ v => v :: acc) [])
  | _ => throw "not an array or object"

def countWhere (case : Json) (p : List String) (f : Json → Bool) : Except String Nat := do
  pure ((← members case p).filter f).length

def isTrue (e : Json) (k : String) : Bool :=
  match e.getObjVal? k with
  | .ok (.bool true) => true
  | _ => false

def predicates : List String := ["environment", "vocabulary", "predicates"]

/-- `Data.Background.generate`: one premise per functional and one per total flag. -/
def flagsCount (case : Json) : Except String Nat := do
  pure ((← countWhere case predicates (isTrue · "functional")) + (← countWhere case predicates (isTrue · "total")))

/-- `Definitions.expand`: one biconditional per defined predicate. -/
def definitionsCount (case : Json) : Except String Nat := countWhere case predicates (has · "defined")

/-- `Background.literals`: one premise per pair of `$string` literals. -/
def literalsCount (case : Json) : Except String Nat := do
  let n ← countWhere case ["environment", "vocabulary", "constants"]
    (fun e => e.getObjValD "sort" == .str "$string")
  pure (n * (n - 1) / 2)

/-- `Norms.syms`: one layer per regulated predicate. -/
def regulatedCount (case : Json) : Except String Nat := countWhere case predicates (has · "regulated")

/-- `Norms.pairs`: one per obligation with a permission dual. -/
def pairsCount (case : Json) : Except String Nat := countWhere case predicates fun e =>
  match e.getObjVal? "regulated" with
  | .ok r => r.getObjValD "role" == .str "obligation" && (match r.getObjVal? "permission" with
      | .ok (.str _) => true
      | _ => false)
  | .error _ => false

/-- The request's runs of generators, in generator order. -/
def runs (case : Json) (counts : List (String × (Json → Except String Nat))) : Except String (List Json) := do
  let mut out := []
  for (g, count) in counts do
    out := out ++ List.replicate (← count case) (Json.str g)
  pure out

/-- The values of `values`: one per requested formula. -/
def values (row case : Json) : Check := do
  let vs ← (← field row "values").getArr?
  for v in vs do bool v
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

/-- A claim's identity: its name, AST and label (absent keys stay absent). -/
def project (x : Json) : List (Option Json) :=
  ["name", "ast", "label"].map (fun k => (x.getObjVal? k).toOption)

/-- `Route.Run.claimJson`: a claim's shape. -/
def claim (j : Json) : Check := do
  shape j ["name", "ast"] ["label"]
  string (← field j "name")
  folFormula (← field j "ast")
  if let .ok l := j.getObjVal? "label" then
    need ((← l.getStr?) != "asserted") "explicit default label"

/-- The claim is a node the request declared (`admit_labels_decoded`). -/
def requestNode (j case : Json) : Check := do
  let nodes ← (← path case ["document", "graph", "nodes"]).getArr?
  need (nodes.any (fun n => (n.getObj?).toBool && project n == project j)) "not a node of the request"

/-- `VE.Graph.check`'s conditions on the graph's shape: unique names, premises and
certificate together, and every premise an earlier node (`acyclicCheck`). -/
def graphShape (nodes : Array Json) : Check := do
  let mut names : Array String := #[]
  for n in nodes do
    let name ← (← field n "name").getStr?
    need (!names.contains name) "duplicate node name"
    need (has n "premises" == has n "certificate") "premises and certificate come together"
    if let .ok ps := n.getObjVal? "premises" then
      for p in ← ps.getArr? do
        need (names.contains (← p.getStr?)) "a premise is not an earlier node"
    names := names.push name

/-- The ordered leaf list of node `i` (`VE.Graph.Unfolds`); premises name earlier
nodes, so `i + 1` fuel suffices. -/
def unfold (nodes : Array Json) : Nat → Nat → Except String (List Json)
  | 0, _ => throw "unfolding exceeds the graph"
  | fuel + 1, i => do
    let node := nodes[i]!
    match node.getObjVal? "premises" with
    | .error _ => pure [node]
    | .ok ps => do
      let mut out := []
      for p in ← ps.getArr? do
        let k := nodes.findIdx? (fun n => n.getObjValD "name" == p)
        out := out ++ (← unfold nodes fuel (k.getD nodes.size))
      pure out

/-- The report's assumptions are exactly the root's unfolding (`check_unfolds`). -/
def unfolds (assumptions case : Json) : Check := do
  let graph ← path case ["document", "graph"]
  let nodes ← (← field graph "nodes").getArr?
  graphShape nodes
  let root ← (← field graph "root").getStr?
  let some i := nodes.findIdx? (fun n => n.getObjValD "name" == .str root) | throw "the root is not a node"
  let leaves ← unfold nodes (i + 1) i
  let xs ← assumptions.getArr?
  need (xs.size == leaves.length && (xs.toList.zip leaves).all (fun (x, l) => project x == project l))
    "assumptions are not the root's unfolding"

def admission (row case : Json) : Check := do
  okRow row case ["admitted", "report", "report_id", "kinds"]
  need (isField row "admitted" (.bool true)) "admitted"
  let report ← field row "report"
  shape report ["root", "assumptions"] []
  let root ← field report "root"
  claim root
  need ((← field root "name") == (← path case ["document", "graph", "root"])) "root"
  array (← field report "assumptions") claim
  hex64 (← field row "report_id")
  let kinds ← field row "kinds"
  array kinds kind
  let units ← (← path case ["document", "units"]).getArr?
  let requested ← units.mapM (field · "kind")
  need (kinds == .arr requested) "kinds are not the request's unit kinds"

def dependencyOrder (row case : Json) : Check := do
  okRow row case ["order"]
  let _ ← VE.Bridge.strings (← field row "order")

def bundle (row case : Json) : Check := do
  okRow row case ["checked", "lemmas"]
  let requested ← (← field case "lemmas").getArr?
  need ((← (← field row "checked").getNat?) == requested.size) "one check per requested lemma"
  let lemmas ← field row "lemmas"
  array lemmas hex64
  need (lemmas == .arr (← requested.mapM (field · "meaning_id"))) "lemmas are not the request's"

def background (row case : Json) : Check := do
  okRow row case ["background", "premises", "generators"]
  array (← field row "background") generatedFormula
  array (← field row "premises") generatedFormula
  array (← field row "generators")
    (fun g => do need (VE.Route.Background.generators.contains (← g.getStr?)) "generator")

def label (row case : Json) : Check := do
  okRow row case ["label"]
  let l ← (← field row "label").getStr?
  need (VE.Route.Admission.parseLabel l).isSome "not a canonical label"
  need (isField case "label" (.str l)) "not the request's label"

def routeError (row case : Json) : Check := do
  let valid := case.getObjValD "kind" == .str "certificate"
  shape row (["id", "status", "error"] ++ if valid then ["valid"] else []) ["generator"]
  need (isField row "status" (.str "error")) "status"
  need ((← field row "id") == case.getObjValD "id") "id is not the request's"
  text (← field row "error")
  if valid then need (isField row "valid" (.bool false)) "valid"
  if let .ok g := row.getObjVal? "generator" then string g

def routeOk (row case : Json) : Check := do
  need (case.getObj?).toBool "case is not an object"
  match ← VE.Route.Run.caseKind case with
  | "evaluate" => do okRow row case ["values"]; values row case
  | "countermodel" => do okRow row case ["refutes"]; bool (← field row "refutes")
  | "certificate" => do
    okRow row case ["valid", "background"]
    bool (← field row "valid")
    nat (← field row "background")
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
  let order ← VE.Bridge.strings (← field row "order")
  let background ← field row "background"
  objects background ["generator", "ast"] fun x => do
    need (["definitions", "literals", "profile"].contains (← (← field x "generator").getStr?)) "generator"
    generatedFormula (← field x "ast")
  let premises ← field row "premises"
  objects premises ["label", "ast"] fun x => do
    need ((← (← field x "label").getStr?).startsWith "layer:norms:") "layer label"
    generatedFormula (← field x "ast")
  let targets ← field row "conflict_targets"
  objects targets ["target", "sorts", "ast"] fun x => do
    string (← field x "target")
    let _ ← VE.Bridge.strings (← field x "sorts")
    generatedFormula (← field x "ast")
  bool (← field row "fragment")
  let _ := order

def normsOk (row case : Json) : Check := do
  match ← VE.Route.Run.caseKind case with
  | "admission" => admission row case
  | "norms-elaborate" => normsElaborate row case
  | "norms-certificate" => do
    okRow row case ["valid", "background", "layers"]
    bool (← field row "valid")
    nat (← field row "background")
    nat (← field row "layers")
  | "norms-conflict" =>
    if has case "witness" then do
      okRow row case ["verdict", "target", "targets"]
      need (["CONFLICT", "UNKNOWN"].contains (← (← field row "verdict").getStr?)) "verdict"
      let target ← (← field row "target").getStr?
      let _ ← VE.Bridge.strings (← field row "targets")
      need ((← path case ["witness", "target"]) == .str target) "not the requested target"
    else do
      okRow row case ["verdict", "targets"] ["detail"]
      need (["CONFLICT-FREE", "UNKNOWN"].contains (← (← field row "verdict").getStr?)) "verdict"
      let _ ← VE.Bridge.strings (← field row "targets")
      if let .ok d := row.getObjVal? "detail" then string d
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
      bool (← field row "value")
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
      for f in ← (← field row "ast").getArr? do orderFormula f
    | "evaluate" => do okRow row case ["values"]; values row case
    | "countermodel" => do okRow row case ["refutes"]; bool (← field row "refutes")
    | "certificate" => do okRow row case ["valid"]; bool (← field row "valid")
    | k => throw s!"no order result for kind {k}"]

def token (j : Json) : Check := do
  let _ ← VE.English.ServiceRun.decodeTok j
  need (j == VE.English.ServiceRun.encodeTok (← VE.English.ServiceRun.decodeTok j)) "token"

def englishItem (j : Json) : Check := do
  shape j ["parsed", "checked", "rendered", "roundtrip"] []
  let parsed ← field j "parsed"
  unless parsed.isNull do array parsed generatedFormula
  bool (← field j "checked")
  let rendered ← field j "rendered"
  unless rendered.isNull do array rendered token
  bool (← field j "roundtrip")

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
      for item in results do englishItem item]

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

/-! ## Invariants: content the runners guarantee

The client does not check these (docs/spec/lean-service.md, threat model); the tests
require every genuine service response to satisfy them, and show that each finding's
corruption violates one. Expected values come from the request where they can be read
off it, and from the Lean functions the runners use where they cannot (the layer order
is a dependency order computed by the runner). -/
namespace Invariants

def distinct (xs : List Json) (what : String) : Check :=
  need (xs.eraseDups.length == xs.length) s!"duplicate {what}"

/-- The request's predicate declarations, by name (`RBNode` order). -/
def declarations (case : Json) : Except String (List (String × Json)) := do
  match ← path case predicates with
  | .obj kvs => pure (kvs.foldl (fun acc k v => acc ++ [(k, v)]) [])
  | _ => throw "predicates are not an object"

/-- The regulated predicates the request declares. -/
def regulatedNames (case : Json) : Except String (List String) := do
  pure ((← declarations case).filterMap fun (k, v) => if has v "regulated" then some k else none)

/-- `Norms.pairs`: `(r->m, r)` for each obligation `r` with a permission dual `m`, by `r`. -/
def pairNames (case : Json) : Except String (List (String × String)) := do
  pure ((← declarations case).filterMap fun (k, v) => match v.getObjVal? "regulated" with
    | .ok r =>
      if r.getObjValD "role" == .str "obligation" then
        match r.getObjVal? "permission" with
        | .ok (.str m) => some (k ++ "->" ++ m, k)
        | _ => none
      else none
    | .error _ => none)

/-- `Norms.Replay.targets` of the request's source, by the runners' Lean functions. -/
def sourceTargets (case : Json) : Except String (List String) := do
  let src ← VE.Norms.Wire.decodeSource (← field case "environment") (case.getObjValD "norms")
  pure ((VE.Norms.targets src.D).map (·.1))

/-- Conflict target names: distinct, one per regulated predicate (in the layer order),
then one per declared profile pair, and exactly `Norms.Replay.targets`. -/
def targetNames (names : List String) (case : Json) : Check := do
  let regs ← regulatedNames case
  let pairs ← pairNames case
  distinct (names.map .str) "conflict target"
  need (names.length == regs.length + pairs.length) "not one target per layer and profile pair"
  let layers := names.take regs.length
  need (layers.all regs.contains && regs.all layers.contains) "layer targets are not the regulated predicates"
  need (names.drop regs.length == pairs.map (·.1)) "pair targets are not the declared pairs"
  need (names == (← sourceTargets case)) "targets are not Norms.Replay.targets"

/-- The declared argument sorts of the predicate that owns a target (`r` for `r->m`). -/
def targetSorts (case : Json) (name : String) : Except String Json := do
  let owner := ((← pairNames case).find? (·.1 == name)).map (·.2) |>.getD name
  path case (predicates ++ [owner, "arguments"])

def nonemptyValues (row : Json) : Check := do
  need (!(← (← field row "values").getArr?).isEmpty) "empty values"

def normsElaborate (row case : Json) : Check := do
  let order ← VE.Bridge.strings (← field row "order")
  let regs ← regulatedNames case
  distinct (order.map .str) "layer"
  need (order.length == regs.length && order.all regs.contains) "layers are not the regulated predicates"
  let premises ← (← field row "premises").getArr?
  need (premises.toList.map (·.getObjValD "label") == order.map (fun p => .str ("layer:norms:" ++ p)))
    "not one premise per layer, in order"
  let targets ← (← field row "conflict_targets").getArr?
  let names ← targets.toList.mapM fun t => do (← field t "target").getStr?
  targetNames names case
  need (names.take order.length == order) "layer targets do not follow the layer order"
  for t in targets do
    let name ← (← field t "target").getStr?
    need ((← field t "sorts") == (← targetSorts case name)) s!"sorts of {name} are not its declared arguments"
  let expected ← runs case [("definitions", definitionsCount), ("literals", literalsCount), ("profile", pairsCount)]
  need ((← (← field row "background").getArr?).toList.map (·.getObjValD "generator") == expected)
    "Background is not the regenerated generators'"

def normsOk (row case : Json) : Check := do
  match ← VE.Route.Run.caseKind case with
  | "admission" => admissionContent row case
  | "norms-elaborate" => normsElaborate row case
  | "norms-certificate" => do
    let n := (← definitionsCount case) + (← literalsCount case) + (← pairsCount case)
    need ((← (← field row "background").getNat?) == n) "background is not the regenerated count"
    need ((← (← field row "layers").getNat?) == (← regulatedCount case)) "not one layer per regulated predicate"
  | "norms-conflict" => do
    let targets ← VE.Bridge.strings (← field row "targets")
    targetNames targets case
    if has case "witness" then
      need (targets.contains (← (← field row "target").getStr?)) "target is not a regenerated target"
    else if has row "detail" then
      need (isField row "verdict" (.str "UNKNOWN")) "detail without UNKNOWN"
  | _ => pure ()
where
  admissionContent (row case : Json) : Check := do
    let report ← field row "report"
    requestNode (← field report "root") case
    array (← field report "assumptions") (requestNode · case)
    unfolds (← field report "assumptions") case

def admission (row case : Json) : Check := normsOk.admissionContent row case

def routeRow (row case : Json) : Check := do
  if isField row "status" (.str "error") then
    match VE.Route.Run.generatorOf (← (← field row "error").getStr?) with
    | some g => need (isField row "generator" (.str g)) "generator is not the message's"
    | none => need (!has row "generator") "generator without InvalidModel"
  else match ← VE.Route.Run.caseKind case with
    | "evaluate" => nonemptyValues row
    | "certificate" => do
      let n := (← flagsCount case) + (← definitionsCount case) + (← literalsCount case)
      need ((← (← field row "background").getNat?) == n) "background is not the regenerated count"
    | "dependency-order" => do
      let order ← VE.Bridge.strings (← field row "order")
      let nodes ← VE.Route.Wire.decodeNodes (← field case "nodes")
      let names := VE.Route.nodeNames nodes
      need ((names.find? (fun n => names.count n > 1)).isNone) "duplicate node"
      need (VE.Route.verifyOrder nodes order) "not a dependency order of the request's nodes"
    | "background" => do
      let bg ← field row "background"
      need (bg == (← field row "premises")) "premises differ from background"
      let gs ← field row "generators"
      need ((← length bg) == (← length gs)) "not one generator per premise"
      let expected ← runs case [("flags", flagsCount), ("definitions", definitionsCount),
        ("literals", literalsCount)]
      need ((← gs.getArr?).toList == expected) "generators are not the regenerated Background's"
    | "admission" => admission row case
    | _ => pure ()

def englishItem (j case : Json) : Check := do
  let checked ← (← field j "checked").getBool?
  let rendered ← field j "rendered"
  if checked then
    need (!rendered.isNull) "checked without rendering"
    let formulas := (case.getObjVal? "formulas" >>= Json.getArr?).toOption
    need (formulas.any (!·.isEmpty)) "checked without formulas"
  else need (rendered.isNull && !(← (← field j "roundtrip").getBool?)) "rendering or roundtrip without a check"

/-- The content invariants of one decoded result (case errors have none). -/
def row (mode : String) (r case : Json) (_index : Nat) : Check := do
  if has r "case_index" then return
  let ok := isField r "status" (.str "ok")
  match mode with
  | "evaluate" =>
    if ok && !has case "kind" then
      nonemptyValues r
      let vs ← (← field r "values").getArr?
      need (isField r "value" (.bool (vs.all (· == .bool true)))) "value is not the conjunction"
  | "order" =>
    if ok then match case.getObjValD "kind" with
      | .str "surface" => need (!(← (← field r "ast").getArr?).isEmpty) "empty document"
      | .str "evaluate" => nonemptyValues r
      | _ => pure ()
  | "route" => routeRow r case
  | "norms" =>
    if VE.Norms.Run.usesNormsPath case then
      if ok then normsOk r case
    else routeRow r case
  | "english" =>
    if let .ok results := r.getObjVal? "results" then
      let cases ← (← field case "cases").getArr?
      for (item, c) in (← results.getArr?).zip cases do englishItem item c
  | _ => pure ()

end Invariants

/-- `Service.Protocol.bound`: result `i` carries position `i` and the digest of case `i`. -/
def bound (b : Json) (index : Nat) (digest : Json) : Except String Json := do
  shape b ["index", "digest", "result"] []
  need ((← (← field b "index").getNat?) == index) "index is not the result's position"
  hex64 (← field b "digest")
  need ((← field b "digest") == digest) "digest is not the case's"
  field b "result"

/-- `Service.Protocol`: a request error bound to the request's mode and case digests
(`requestError`), or one bound result per case with exact counts; `content` is applied to
each result with its case and position. -/
def response (mode : String) (request r : Json) (content : Json → Json → Nat → Check) : Check := do
  let nonce ← field request "id"
  if isField r "status" (.str "error") then
    shape r ["id", "status", "mode", "digests", "error"] []
    need ((← field r "id") == nonce && (← (field r "id")).getStr?.toBool) "id is not the nonce"
    need (isField r "mode" (.str mode)) "mode"
    need ((← field r "digests") == (← field request "digests")) "digests are not the request's"
    text (← field r "error")
  else
    shape r ["id", "status", "mode", "results", "counts"] []
    need (isField r "status" (.str "ok")) "status"
    need ((← field r "id") == nonce && (← (field r "id")).getStr?.toBool) "id is not the nonce"
    need (isField r "mode" (.str mode)) "mode"
    let cases ← (← field request "cases").getArr?
    let digests ← (← field request "digests").getArr?
    let results ← (← field r "results").getArr?
    need (results.size == cases.size && digests.size == cases.size) "one result per case"
    let mut rows := #[]
    for i in [:results.size] do
      match bound results[i]! i digests[i]! >>= fun x => do
          row mode x cases[i]! i; content x cases[i]! i; pure x with
      | .ok x => rows := rows.push x
      | .error m => throw s!"result {i}: {m}"
    let counts ← field r "counts"
    shape counts ["cases", "bytes", "errors"] []
    need ((← (← field counts "cases").getNat?) == cases.size) "counts.cases"
    need ((← field counts "bytes") == (← field request "bytes")) "counts.bytes"
    let errors := (rows.filter (fun x => isField x "status" (.str "error"))).size
    need ((← (← field counts "errors").getNat?) == errors) "counts.errors"

def verdict (check : Json → Json → Nat → Check) (mode : String) (request r : Json) : Json :=
  match response mode request r check with
  | .ok () => .str "accept"
  | .error m => .str s!"reject: {m}"

def noContent (_ _ : Json) (_ : Nat) : Check := pure ()

def contentCheck (mode : String) : Json → Except String (Json → Json → Nat → Check)
  | .null | .str "decode" => .ok noContent
  | .str "invariants" => .ok (Invariants.row mode)
  | c => .error s!"unknown check {c.compress}"

def line (text : String) : Except String Json := do
  let j ← Json.parse text
  let mode ← (← field j "mode").getStr?
  let request ← field j "request"
  let responses ← (← field j "responses").getArr?
  let content ← contentCheck mode (j.getObjValD "check")
  pure (.arr (responses.map (verdict content mode request)))

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
