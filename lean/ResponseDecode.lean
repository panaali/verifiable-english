import VE.Norms.Run
import VE.Order.Wire
import VE.Service.EnglishRun
import VE.Service.Protocol
import ResponseShape.Schemas

/-! `ve_response_decode`: the Lean side of the tests of service responses. Test tooling
only: nothing imports it and no theorem depends on it.

* `decode` decides a response by the one description of the service's responses,
  `ResponseShape.Schemas` (from which the client's `ve/backends/lean_service_schema/` is
  generated): binding to the request (nonce, mode, each result's position and case
  digest, the identity fields the runners echo from the case) and well-formedness, with
  the Lean decoders the runners' outputs come from (`Bridge.decodeFormula`,
  `Order.Wire.decodeFormula`, `Route.Admission.decodeKind`, `parseLabel`, `EnglishRun`'s
  token form) and the runners' dispatch tests (`usesSoftPath`, `Norms.Run.usesNormsPath`,
  ...) deciding beside their schemas, which must agree (`ResponseShape`, `lean` nodes).
* `invariants` is `decode` and the content the runners guarantee, which the client does
  not check (docs/spec/lean-service.md, threat model): counts regenerated from the
  environment, graph unfoldings, dependency orders, distinct layers and conflict targets
  with their declared argument sorts, verdict details, English check consistency. The
  tests require every genuine service response to satisfy it.
* `schemas` renders the schema files (`tools/response_schemas.py` writes and checks them).

Each input line is `{"check"?: "decode" | "invariants", "mode", "request": {"id", "cases",
"digests", "bytes"}, "responses": [...]}`, where `digests` is `null` when the request's cases
text does not split into cases; the output line is an array with `"accept"`
or `"reject: <reason>"` per response. The line `{"check": "schemas"}` is answered with
`{file name: schema document}`. -/
namespace ResponseDecode
open Lean

abbrev Check := Except String Unit

def need (b : Bool) (message : String) : Check :=
  if b then pure () else throw message

def field (j : Json) (k : String) : Except String Json := j.getObjVal? k

def isField (j : Json) (k : String) (v : Json) : Bool :=
  match j.getObjVal? k with
  | .ok x => x == v
  | .error _ => false

def has (j : Json) (k : String) : Bool := (j.getObjVal? k).toBool

def array (j : Json) (f : Json → Check) : Check := do
  for x in ← j.getArr? do f x


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

/-! ## Graph reports -/

/-- A claim's identity: its name, AST and label (absent keys stay absent). -/
def project (x : Json) : List (Option Json) :=
  ["name", "ast", "label"].map (fun k => (x.getObjVal? k).toOption)

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

/-- The coding beside a rejection is its message's: `Service.Protocol.codeMembers`. -/
def coding (b r : Json) : Check := do
  if let .ok (.str m) := r.getObjVal? "error" then
    need (b.getObjValD "code" == .str (VE.Service.rejectionCode m)) "code is not the message's"
    need (b.getObjValD "generator" == match VE.Route.Run.generatorOf m with
      | some g => .str g
      | none => .null) "generator is not the message's"

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
  | "soft-norms" =>
    -- A soft rejection's contract code is the failed check's (`SoftNorms.Run.reportedCode`).
    if VE.SoftNorms.Run.usesSoftPath case && !ok then
      if let .ok (.str m) := r.getObjVal? "error" then
        need (r.getObjValD "code" == .str (VE.SoftNorms.Run.reportedCode case m)) "code is not the message's check"
  | _ => pure ()

end Invariants


/-- The response's verdict under `envelope.json#/response` with the mode's row, then the
content check of each bound result with its case and position (a request error has none). -/
def response (mode : String) (request r : Json) (content : Json → Json → Json → Nat → Check) : Check := do
  let some rowShape := ResponseShape.Schemas.row mode | throw s!"unknown mode {mode}"
  ResponseShape.decide ResponseShape.Schemas.files (.ref "envelope.json#/response")
    { value := request, row := rowShape } r
  if isField r "status" (.str "ok") then
    let cases ← (← field request "cases").getArr?
    let results ← (← field r "results").getArr?
    for i in [:results.size] do
      let b := results[i]!
      match content b (← field b "result") cases[i]! i with
      | .ok () => pure ()
      | .error m => throw s!"result {i}: {m}"

def verdict (check : Json → Json → Json → Nat → Check) (mode : String) (request r : Json) : Json :=
  match response mode request r check with
  | .ok () => .str "accept"
  | .error m => .str s!"reject: {m}"

def noContent (_ _ _ : Json) (_ : Nat) : Check := pure ()

/-- The invariants of one bound result: its coding, then its row's. -/
def invariants (mode : String) (b r case : Json) (index : Nat) : Check := do
  Invariants.coding b r
  Invariants.row mode r case index

def contentCheck (mode : String) : Json → Except String (Json → Json → Json → Nat → Check)
  | .null | .str "decode" => .ok noContent
  | .str "invariants" => .ok (invariants mode)
  | c => .error s!"unknown check {c.compress}"

def line (text : String) : Except String Json := do
  let j ← Json.parse text
  if j.getObjValD "check" == .str "schemas" then return ← ResponseShape.Schemas.rendered
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
