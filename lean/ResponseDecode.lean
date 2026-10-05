import VE.Norms.Run
import VE.Order.Wire
import VE.Service.EnglishRun
import VE.Service.Protocol

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

/-- `Norms.Run.runCaseReported`'s dispatch: the norms path or a statement-layer profile. -/
def normsPath (case : Json) : Bool :=
  VE.Norms.Run.usesNormsPath case || VE.Norms.Plain.layered (case.getObjValD "environment")

def norms (row case : Json) (index : Nat) : Check :=
  if normsPath case then
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

/-! ## Statement-layer route modes (lean-first batch 1, lf-1 review B)

Every answer is closed: exactly the fields its encoder writes, each typed to its leaves, as
`<mode>.json` describes it. A route answers a case on its own path (the route's own dispatch
test: `usesSoftPath`, `usesRightsPath`, ...) and delegates every other case unchanged, so the
delegate's checks apply there. -/
namespace Routes

abbrev Field := String × (Json → Check)

def within (k : String) (c : Check) : Check :=
  match c with
  | .ok () => pure ()
  | .error m => throw s!"{k}: {m}"

/-- Exactly the fields of `req`, and any of `opt`, each valid. -/
def obj (req opt : List Field) (j : Json) : Check := do
  shape j (req.map (·.1)) (opt.map (·.1))
  for (k, f) in req do within k (f (← field j k))
  for (k, f) in opt do
    if let .ok v := j.getObjVal? k then within k (f v)

/-- Exactly the fields of `req`, each valid. -/
def closed (req : List Field) : Json → Check := obj req []

def arr (f : Json → Check) (j : Json) : Check := array j f
def strs : Json → Check := arr string
def texts : Json → Check := arr text
def gen : Json → Check := generatedFormula
def gens : Json → Check := arr generatedFormula
def hexE (j : Json) : Check := if j == .str "" then pure () else hex64 j
def constJ (v : Json) (j : Json) : Check := need (j == v) s!"not {v.compress}"
def oneOf (vs : List String) (j : Json) : Check := do
  let s ← j.getStr?
  need (vs.contains s) s!"{s} is not one of {vs}"
def pfx (ps : List String) (j : Json) : Check := do
  let s ← j.getStr?
  need (ps.any s.startsWith) s!"{s} starts with none of {ps}"
def nullOr (f : Json → Check) (j : Json) : Check := if j.isNull then pure () else f j
def alt (cs : List (Json → Check)) (j : Json) : Check := firstOk (cs.map fun c _ => c j)
def mapOf (f : Json → Check) (j : Json) : Check := do
  for (k, v) in ← VE.Bridge.fields j do within k (f v)
def anyObj (j : Json) : Check := do let _ ← j.getObj?
def pair (j : Json) : Check := do
  let xs ← j.getArr?
  need (xs.size == 2) "not a pair"
  for x in xs do string x
def intAtLeast (n : Int) (j : Json) : Check := do need ((← j.getInt?) ≥ n) s!"below {n}"
def atMost (n : Nat) (f : Json → Check) (j : Json) : Check := do
  f j
  need ((← j.getArr?).size ≤ n) s!"more than {n} elements"
def nonempty (f : Json → Check) (j : Json) : Check := do
  f j
  need (!(← j.getArr?).isEmpty) "empty"
def emptyArr (j : Json) : Check := do need ((← j.getArr?).isEmpty) "not empty"
def both (f g : Json → Check) (j : Json) : Check := do f j; g j
/-- `Order.Wire.decodeInt`'s domain: a canonical decimal of at most 40 characters. -/
def integerText (j : Json) : Check := do let _ ← VE.Order.Wire.decodeInt (← j.getStr?)

/-- The field `k` is present exactly when `cond` holds. -/
def presentIff (j : Json) (k : String) (cond : Bool) : Check :=
  need (has j k == cond) s!"{k} is {if cond then "missing" else "unexpected"}"

def kindIs (case : Json) (k : String) : Bool := isField case "kind" (.str k)

/-- The request value at `p`, which must exist. -/
def equalsAt (case : Json) (p : List String) (j : Json) : Check := do
  need (j == (← path case p)) s!"not the request's {p}"

/-- An answer: the request's (string) id, status ok, then exactly the fields. -/
def ok (case : Json) (req opt : List Field) : Json → Check :=
  obj ([("id", fun j => do
      let s ← j.getStr?
      need (isField case "id" (.str s)) "id is not the request's"),
    ("status", constJ (.str "ok"))] ++ req) opt

def answerOf (case : Json) (req : List Field) : Json → Check := ok case req []

/-- The request's units' kinds, each of which must exist. -/
def kindsEcho (case : Json) (domain : Option (Json → Check)) (j : Json) : Check := do
  let xs ← j.getArr?
  if let some f := domain then for x in xs do f x
  let units ← (← path case ["document", "units"]).getArr?
  need (j == .arr (← units.mapM (field · "kind"))) "kinds are not the request's unit kinds"

def report (j : Json) : Check := do
  shape j ["root", "assumptions"] []
  within "root" (claim (← field j "root"))
  within "assumptions" (array (← field j "assumptions") claim)

def boundReport (case : Json) (j : Json) : Check := do
  report j
  need ((← field (← field j "root") "name") == (← path case ["document", "graph", "root"])) "root"

def labelled (label : Json → Check) : Json → Check := closed [("label", both text label), ("ast", gen)]
def anyLabel : Json → Check := labelled (fun _ => pure ())
def normsBackground : Json → Check :=
  arr (closed [("generator", oneOf ["definitions", "literals", "profile"]), ("ast", gen)])
def layerPremises : Json → Check := arr (closed [("label", pfx ["layer:norms:"]), ("ast", gen)])
def conflictTargets : Json → Check := arr (closed [("target", text), ("sorts", strs), ("ast", gen)])
def normNode : Json → Check := closed [("name", string), ("predicate", string), ("sign", bool), ("guard", gen),
  ("unless", gens), ("over", strs)]

def witnessConflict (case : Json) : Json → Check :=
  answerOf case [("verdict", oneOf ["CONFLICT", "UNKNOWN"]),
    ("target", both string (equalsAt case ["witness", "target"])), ("targets", strs)]

def packagesConflict (case : Json) (j : Json) : Check := do
  ok case [("verdict", oneOf ["CONFLICT-FREE", "UNKNOWN"]), ("targets", strs)] [("detail", text)] j
  presentIff j "detail" (isField j "verdict" (.str "UNKNOWN"))

/-- `common.json` environment: the envelope-checked request environment with generated predicates. -/
def environment (case : Json) (j : Json) : Check := do
  let env := case.getObjValD "environment"
  let vocab := env.getObjValD "vocabulary"
  closed [("language", both string (equalsAt case ["environment", "language"])), ("profiles", strs),
    ("spec_revision", both string (equalsAt case ["environment", "spec_revision"])),
    ("vocabulary", fun v => do
      obj [("sorts", both anyObj (equalsAt case ["environment", "vocabulary", "sorts"])),
        ("constants", both anyObj (equalsAt case ["environment", "vocabulary", "constants"])),
        ("predicates", mapOf fun e => do anyObj e; strs (← field e "arguments"))]
        [("soft", both anyObj (equalsAt case ["environment", "vocabulary", "soft"])),
         ("rights", both anyObj (equalsAt case ["environment", "vocabulary", "rights"]))] v
      if (env.getObj?).toBool && (vocab.getObj?).toBool then
        if (vocab.getObjVal? "soft").toBool then need (has v "soft") "soft is missing"
        if (vocab.getObjVal? "rights").toBool then need (has v "rights") "rights is missing")] j

/-- A route's own rejection row (`common.json` route_path_error). -/
def pathError (row case : Json) : Check := errorRow row case []

/-- The first `(when, then)` whose condition holds selects the answer's check. -/
def select (choices : List (Bool × (Unit → Check))) : Check :=
  match choices.find? (·.1) with
  | some (_, c) => c ()
  | none => throw "no result is possible for this request"

/-- A route on its own path: a batch-decoder case error, its own rejection row or an answer. -/
def ownPath (row case : Json) (index : Nat) (error : Json → Json → Check) (answer : Check) : Check :=
  firstOk [fun _ => caseErrorRow row index false, fun _ => error row case, fun _ => answer]

/-! ### soft-norms -/

def softCodes : List String := ["SOFT_DEPENDENCY_CYCLE", "SOFT_DUPLICATE_DECLARATION", "SOFT_EXCEPTION_ARRAY",
  "SOFT_HARD_CONSTRAINT", "SOFT_INVALID_ALTERABLE", "SOFT_INVALID_ARRAY", "SOFT_INVALID_BLOCK",
  "SOFT_INVALID_DECIDER", "SOFT_INVALID_EXCEPTION_CONDITION", "SOFT_INVALID_FACTORS", "SOFT_INVALID_INPUT",
  "SOFT_INVALID_NAME", "SOFT_INVALID_OUTRANKING", "SOFT_INVALID_OUTRANKS_PAIR", "SOFT_INVALID_RULE_FIELDS",
  "SOFT_INVALID_TIES_PAIR", "SOFT_MISSING_DECIDER", "SOFT_MISSING_EXCEPTION", "SOFT_OVER_HARD",
  "SOFT_RESOURCE_LIMIT", "SOFT_STRICT_EXCEPTION", "SOFT_STRICT_OUTRANKING_DECIDER", "SOFT_TIE_AGAINST_ORDER",
  "SOFT_UNKNOWN_PARTY", "SOFT_UNKNOWN_RANK", "SOFT_UNSUPPORTED_PROFILE"]

def softError (row case : Json) : Check := do
  shape row ["id", "status", "error", "code"] []
  need (isField row "status" (.str "error")) "status"
  need ((← field row "id") == case.getObjValD "id") "id is not the request's"
  text (← field row "error")
  oneOf softCodes (← field row "code")

def coherence : Json → Check := arr (pfx ["soft:coherence:"])
def softDecisions : Json → Check := arr (closed [("name", pfx ["soft__"]), ("arguments", strs)])
def softDerived : Json → Check := arr (closed [("rule", string), ("ast", nullOr gen)])
def softPairs : Json → Check := arr (closed [("pair", pair), ("act", string), ("comparable", bool),
  ("label", pfx ["soft:coherence:"]), ("ast", gen)])
def softBackground : Json → Check := arr fun x => do
  obj [("generator", oneOf ["definitions", "literals", "profile", "soft"]), ("ast", gen)]
    [("label", pfx ["soft:exception:", "soft:coherence:"])] x
  presentIff x "label" (isField x "generator" (.str "soft"))

def softWitness (case : Json) (j : Json) : Check := do
  ok case [("verdict", oneOf ["CONFLICT", "UNKNOWN"]),
    ("target", both string (equalsAt case ["witness", "target"])), ("targets", strs), ("status_text", text)]
    [("witness_kind", pfx ["pair conflict on ", "strict collision on "])] j
  presentIff j "witness_kind" (isField j "verdict" (.str "CONFLICT"))

def softOk (row case : Json) : Check := select [
  (kindIs case "admission", fun _ => answerOf case [("admitted", constJ (.bool true)), ("report", boundReport case),
    ("report_id", hex64), ("kinds", kindsEcho case (some kind)), ("conditional_on", coherence)] row),
  (kindIs case "soft-elaborate", fun _ => answerOf case [("environment_prime", environment case),
    ("decisions", softDecisions), ("derived", softDerived), ("order", strs), ("background", softBackground),
    ("premises", layerPremises), ("colliding_pairs", softPairs), ("conflict_targets", conflictTargets),
    ("conditional_on", coherence), ("fragment", bool), ("warnings", texts)] row),
  (kindIs case "soft-pairs", fun _ => answerOf case [
    ("pairs", arr fun x => do
      obj [("pair", pair), ("label", pfx ["soft:coherence:"]),
        ("status", oneOf ["RANK-RESOLVED", "DISJOINT", "WEIGHING POINT", "UNKNOWN"])] [("detail", text)] x
      presentIff x "detail" !(isField x "status" (.str "RANK-RESOLVED") || isField x "status" (.str "DISJOINT"))),
    ("discharged", coherence), ("weighing_points", coherence)] row),
  (kindIs case "soft-certificate", fun _ => answerOf case [("valid", bool), ("background", nat), ("layers", nat),
    ("conditional_on", coherence)] row),
  (kindIs case "soft-conflict" && has case "witness", fun _ => softWitness case row),
  (kindIs case "soft-conflict", fun _ => do
    ok case [("verdict", oneOf ["CONFLICT-FREE", "UNKNOWN"]), ("status_text", text), ("coherent_exhibit", bool),
      ("budget", nat), ("targets", strs), ("conditional_on", coherence)] [("detail", text)] row
    presentIff row "detail" (isField row "verdict" (.str "UNKNOWN")))]

def softNorms (row case : Json) (index : Nat) : Check :=
  if VE.SoftNorms.Run.usesSoftPath case then ownPath row case index softError (softOk row case)
  else norms row case index

/-! ### rights -/

def rightsLabels : Json → Check := arr (pfx ["soft:coherence:", "rights:limitation:"])
def instanceKind : Json → Check := oneOf ["claim", "liberty", "immunity", "powerLiberty", "powerRecognition"]
def rightsNode : Json → Check := closed [("name", string), ("predicate", string), ("sign", bool),
  ("mode", oneOf ["strict", "default"]), ("guard", gen), ("unless", gens), ("over", strs), ("hard", bool)]
def narrowings : Json → Check := arr (closed [("right", string), ("rule", string), ("in_scope", bool),
  ("mechanisms", arr (closed [("mechanism", text), ("target", text), ("conclusion", gen), ("licence", nullOr text)]))])
def entries : Json → Check := arr (closed [("right", string), ("rule", string), ("instance", instanceKind),
  ("tuple", strs)])
def rightsLine (j : Json) : Check := do
  obj [("right", string), ("kind", oneOf ["claim", "liberty", "immunity", "power"]), ("instance", instanceKind),
    ("rule", string), ("predicate", string), ("holder_slot", nat), ("node", rightsNode)]
    [("bearer", string), ("source_line", string)] j
  presentIff j "source_line" (has j "bearer")
def generatedKey : Json → Check := alt [
  closed [("name", pfx ["rights__lim__"]), ("kind", constJ (.str "lim")), ("limitation", string), ("act", string)],
  closed [("name", pfx ["rights__cond__"]), ("kind", constJ (.str "cond")), ("limitation", string), ("act", string),
    ("condition", string)],
  closed [("name", pfx ["rights__bar__"]), ("kind", constJ (.str "aimed")), ("predicate", string)]]
def barRow : Json → Check := alt [
  closed [("predicate", string), ("aimed", pfx ["rights__bar__"]), ("reading", constJ (.str "rule")),
    ("barred", strs), ("blocked_defaults", strs), ("composition_candidates", strs),
    ("composition_conflicts", emptyArr)],
  obj [("predicate", string), ("aimed", pfx ["rights__bar__"]), ("reading", constJ (.str "query")),
    ("target", gen)] [("entailed", bool)]]

def rightsOk (row case : Json) : Check := select [
  (kindIs case "admission", fun _ => answerOf case [("admitted", constJ (.bool true)), ("report", boundReport case),
    ("report_id", hex64), ("kinds", kindsEcho case none), ("conditional_on", rightsLabels)] row),
  (kindIs case "rights-elaborate", fun _ => answerOf case [("environment_prime", environment case),
    ("generated", arr generatedKey), ("lines", arr rightsLine),
    ("limitations", arr (labelled (pfx ["rights:limitation:"]))), ("bars", arr rightsNode),
    ("rights_background", arr (closed [("generator", constJ (.str "rights")), ("ast", gen),
      ("label", pfx ["rights:limitation:"])])),
    ("narrowings", narrowings),
    ("distinction", arr (closed [("predicate", string), ("independent", bool),
      ("hits", arr (closed [("rule", string), ("right", string), ("protected", string), ("cited", bool)]))])),
    ("findings", texts), ("decisions", softDecisions), ("derived", softDerived), ("order", strs),
    ("background", softBackground), ("premises", layerPremises), ("colliding_pairs", softPairs),
    ("conflict_targets", conflictTargets), ("conditional_on", coherence), ("fragment", bool),
    ("warnings", texts)] row),
  (kindIs case "rights-projections", fun _ => answerOf case [("rights_of", entries), ("duties_of", entries)] row),
  (kindIs case "rights-scope", fun _ => do
    answerOf case [("findings", texts), ("licensed", bool), ("narrowings", narrowings)] row
    need (isField row "licensed" (.bool (← (← field row "findings").getArr?).isEmpty)) "licensed"),
  (kindIs case "rights-certificate", fun _ => answerOf case [("valid", bool), ("background", nat), ("layers", nat),
    ("conditional_on", rightsLabels)] row),
  (kindIs case "rights-bar", fun _ => answerOf case [("bars", arr barRow)] row),
  (kindIs case "rights-conflict" && has case "witness", fun _ => softWitness case row),
  (kindIs case "rights-conflict", fun _ => do
    ok case [("verdict", oneOf ["CONFLICT-FREE", "UNKNOWN"]), ("status_text", text), ("targets", strs),
      ("conditional_on", rightsLabels)] [("detail", text)] row
    presentIff row "detail" (isField row "verdict" (.str "UNKNOWN")))]

def rights (row case : Json) (index : Nat) : Check :=
  if VE.Rights.Run.usesRightsPath case then ownPath row case index pathError (rightsOk row case)
  else softNorms row case index

/-! ### speech-acts -/

def question (j : Json) : Check :=
  let base : List Field := [("unit", string), ("presupposition", gen), ("meaning_id", hexE)]
  alt [
    closed (base ++ [("mode", constJ (.str "polar")), ("tokens", constJ (toJson ["yes", "no"])), ("body", gen)]),
    closed (base ++ [("mode", constJ (.str "which_one")), ("tokens", strs), ("body", gen)]),
    closed (base ++ [("mode", constJ (.str "which_all")), ("domain", strs), ("body", gen)]),
    closed (base ++ [("mode", constJ (.str "follows")), ("query", string)]),
    closed (base ++ [("mode", constJ (.str "reading")), ("set", string), ("version", nat)])] j

def speechOk (row case : Json) : Check := select [
  (kindIs case "speech-elaborate", fun _ => answerOf case [("environment_id", hexE),
    ("scope", obj [("task", string)] [("addressee", closed [("sort", string), ("constant", string)]),
      ("definites", mapOf string)]),
    ("legend", texts), ("premises", gens),
    ("policy", closed [("order", strs), ("background", normsBackground), ("premises", layerPremises),
      ("conflict_targets", conflictTargets), ("fragment", bool)]),
    ("commands", arr (closed [("unit", string), ("force", oneOf ["require", "forbid"]), ("demand", normNode),
      ("paraphrase", pfx ["In this task, you are required to ", "In this task, you are not permitted to "]),
      ("meaning_id", hexE)])),
    ("dormant", strs), ("questions", arr question),
    ("queries", arr (obj [("id", string), ("premises", gens), ("target", gen)]
      [("warning", pfx ["TrivialQuery: "])]))] row),
  (kindIs case "speech-answer", fun _ => answerOf case [("question", both string (equalsAt case ["question"])),
    ("answer", text)] row),
  (kindIs case "speech-consequence", fun _ => answerOf case [("query", both string (equalsAt case ["query"])),
    ("judgment", pfx ["follows (", "gap (", "unresolved ("])] row),
  (kindIs case "speech-conflict" && has case "witness", fun _ => witnessConflict case row),
  (kindIs case "speech-conflict", fun _ => packagesConflict case row)]

def speechActs (row case : Json) (index : Nat) : Check :=
  if VE.SpeechActs.Run.usesSpeechPath case then ownPath row case index pathError (speechOk row case)
  else norms row case index

/-! ### reports -/

/-- `renderKind` of `Attribution.Bridge.kindOf`, at most 32 levels deep. -/
def reportKind : Nat → Json → Check
  | 0, _ => throw "nesting exceeds the Lean decoder fuel 32"
  | fuel + 1, j => match j with
    | .str s => need (["asserted", "norm", "definition"].contains s) s!"kind {s}"
    | .arr xs => match xs.toList with
      | [.str "attributed", h, a, b] => do
        text h; oneOf ["says", "believes", "wants", "intends"] a; reportKind fuel b
      | [.str "hedged", m, b] => do oneOf ["could", "likely"] m; reportKind fuel b
      | _ => throw "not a report kind"
    | _ => throw "not a report kind"

def envelope : Json → Check := closed [("environment_id", hexE), ("document_id", hexE)]
def reportKey : Json → Check := alt [
  closed [("act", oneOf ["says", "believes", "wants", "intends"]), ("holder_sort", string), ("context", string),
    ("complement_id", hexE)],
  closed [("judgment", oneOf ["may", "probably"]), ("assessment", string), ("content_id", hexE)]]
def verdict : Json → Check := alt [
  closed [("id", string), ("status", constJ (.str "UNKNOWN")), ("detail", constJ (.str "payloads"))],
  closed [("id", string), ("environment_id", string), ("background", nat),
    ("status", oneOf ["FOLLOWS", "PAYLOADS INCONSISTENT", "DOES NOT FOLLOW"])],
  closed [("id", string), ("environment_id", string), ("background", nat), ("status", constJ (.str "UNKNOWN")),
    ("detail", oneOf ["witness does not refute", "witness replay over a quoted package's scope is not implemented",
      "envelope", "certificate does not replay", "no evidence"])]]
def statusWord : Json → Check := oneOf ["UNFORMALISED", "OPEN", "UNKNOWN", "LABELLED", "CHECKED"]
/-- A nested path: empty, or steps from `steps` joined by dots. -/
def stepPath (steps : List String) (j : Json) : Check := do
  let s ← j.getStr?
  need (s.isEmpty || (s.splitOn ".").all steps.contains) s!"path {s}"
def nested : Json → Check := alt [
  closed [("item", constJ (.str "assessment")), ("path", stepPath ["1"]), ("name", string),
    ("status", constJ (.str "OPEN"))],
  closed [("item", constJ (.str "act")), ("path", stepPath ["1", "2"]), ("act", string),
    ("status", constJ (.str "LABELLED"))],
  closed [("item", constJ (.str "unformalised")), ("path", stepPath ["1", "2"]), ("reason", string),
    ("status", constJ (.str "UNFORMALISED"))]]
def envelopeBinding : Json → Check := closed [("envelope", bool)]

def reportsOk (row case : Json) : Check := select [
  (kindIs case "admission", fun _ => answerOf case [("admitted", constJ (.bool true)), ("report", boundReport case),
    ("report_id", hex64), ("envelope", envelope), ("kinds", arr (reportKind 32))] row),
  (kindIs case "reports-elaborate", fun _ => answerOf case [("environment_reports_id", hexE),
    ("keys", arr (closed [("name", pfx ["reports__"]), ("arguments", strs), ("key", reportKey)])),
    ("premises", arr (labelled (pfx ["report:", "assessment:"]))),
    ("open_terms", arr (obj [("name", string), ("arguments", strs)]
      [("record", closed [("id", string), ("context", string), ("decided_by", string), ("necessary", gens),
        ("sufficient", gens), ("factors", strs), ("precedents", strs), ("jurisdiction", string),
        ("version", nat)])])),
    ("bridge_formulas", arr (obj [("id", string), ("unit", string), ("depth", nat)] [("ast", gen)])),
    ("content_ids", arr (closed [("unit", string), ("content_id", hexE)])),
    ("envelope", envelope), ("warnings", arr (pfx ["unreviewed act "]))] row),
  (kindIs case "reports-certificate", fun _ => answerOf case [("valid", bool), ("environment_reports_id", hexE),
    ("envelope", envelope), ("bindings", closed [("inner", bool), ("envelope", bool)])] row),
  (kindIs case "reports-countermodel", fun _ => answerOf case [("refutes", bool),
    ("source_model", arr (closed [("name", string), ("key", reportKey), ("holds_of", strs)]))] row),
  (kindIs case "reports-scoped", fun _ => answerOf case [("scoped", arr verdict), ("envelope", envelope),
    ("bindings", envelopeBinding)] row),
  (kindIs case "reports-status", fun _ => answerOf case [
    ("units", arr (closed [("id", string), ("status", statusWord), ("nested", arr nested)])),
    ("scoped", arr verdict), ("document_status", statusWord), ("envelope", envelope),
    ("bindings", envelopeBinding)] row)]

def reports (row case : Json) (index : Nat) : Check :=
  if VE.Reports.Run.usesReportsPath case then ownPath row case index pathError (reportsOk row case)
  else route row case index

/-! ### alternatives -/

def altLabels : List String :=
  ["alternatives:own", "alternatives:one_taken", "alternatives:one_inaction", "alternatives:proximate"]
def inlined : Json → Check := arr (closed [("norm", normNode)])
def altPremises : Json → Check := arr (labelled (oneOf altLabels))
def followableFormulas : Json → Check := closed [("ast", gen), ("followable", gen), ("clear", gen)]
def unmapped : Json → Check := arr (closed [("obligation", string), ("act", string)])
def admissionWith (case : Json) (row : Json) : Check :=
  answerOf case [("admitted", constJ (.bool true)), ("report", boundReport case), ("report_id", hex64),
    ("kinds", kindsEcho case (some kind)), ("conditional_on", strs)] row

/-- The request's alternatives block names a taken predicate. -/
def taken (case : Json) : Bool :=
  match case.getObjVal? "environment" with
  | .ok env => match env.getObjVal? "alternatives" with
    | .ok a => (a.getObjVal? "taken").toBool
    | .error _ => false
  | .error _ => false

def chooser (case : Json) (j : Json) : Check := do
  obj [("chooser", string), ("alternatives", strs), ("inaction", strs), ("permitted", strs), ("required", strs),
    ("avoidable", strs), ("unavoidable", strs), ("allows", arr pair), ("prevents", arr pair), ("clear", strs),
    ("text", text)]
    [("violations", arr (alt [string, closed [("obligation", string), ("arguments", strs)]])), ("breaches", strs)] j
  if taken case then need (has j "violations" && has j "breaches") "violations and breaches are missing"
  else need (!has j "violations" && !has j "breaches") "violations or breaches without a taken predicate"

def dilemma (case : Json) : Json → Check := alt [
  answerOf case [("verdict", oneOf ["not computed", "UNKNOWN"]), ("text", text)],
  answerOf case [("verdict", constJ (.str "DILEMMA")), ("chooser", both string (equalsAt case ["witness", "chooser"])),
    ("diagnosis", text), ("text", text)]]

def altOk (row case : Json) : Check := select [
  (kindIs case "admission", fun _ => admissionWith case row),
  (kindIs case "alt-elaborate", fun _ => answerOf case [("legend", texts), ("inlined", inlined),
    ("alternatives", altPremises), ("base_premises", arr anyLabel), ("followable", followableFormulas),
    ("profile_exists", closed [("avoidable", gen), ("unavoidable", gen), ("allows", gen), ("prevents", gen)]),
    ("unmapped_obligations", unmapped), ("order", strs), ("background", normsBackground),
    ("premises", layerPremises), ("conflict_targets", conflictTargets), ("fragment", bool)] row),
  (kindIs case "alt-validate", fun _ => alt [
    answerOf case [("verdict", constJ (.str "CONFLICT")), ("target", string), ("tuple", strs), ("model_id", hexE),
      ("environment_id", hex64), ("document_hash", hex64), ("text", text)],
    answerOf case [("model_id", hexE), ("environment_id", hex64), ("document_hash", hex64),
      ("choosers", arr (chooser case)), ("assumed_harm_free", strs), ("unmapped_obligations", text),
      ("conditional_on", atMost 1 (arr (constJ (.str "alternatives:table_complete")))), ("text", text)]] row),
  (kindIs case "alt-conflict" && has case "witness", fun _ => answerOf case [("verdict", oneOf ["CONFLICT", "UNKNOWN"]),
    ("target", both string (equalsAt case ["witness", "target"]))] row),
  (kindIs case "alt-conflict", fun _ => packagesConflict case row),
  (kindIs case "alt-followable" && has case "witness", fun _ => dilemma case row),
  (kindIs case "alt-followable", fun _ => alt [
    answerOf case [("verdict", oneOf ["not computed", "UNKNOWN"]), ("text", text)],
    answerOf case [("verdict", constJ (.str "FOLLOWABLE")), ("conditional_on", strs), ("text", pfx ["FOLLOWABLE: "])]] row),
  (kindIs case "alt-certificate", fun _ => answerOf case [("valid", bool), ("background", nat), ("layers", nat),
    ("conditional_on", arr (oneOf altLabels))] row)]

def alternatives (row case : Json) (index : Nat) : Check :=
  if VE.Alternatives.Run.usesAltPath case then ownPath row case index pathError (altOk row case)
  else norms row case index

/-! ### risk -/

def riskLabels : List String := ["risk:certain_possible", "risk:severity_closure", "risk:classes_distinct",
  "risk:order", "risk:class_functional", "risk:class"]
def side : Json → Check := oneOf ["lo", "hi"]
def direction : Json → Check := oneOf ["down", "up"]

def riskStatus (j : Json) : Check := do
  obj [("alternative", string), ("permitted", bool), ("required", bool), ("clear", bool),
    ("rules", arr (intAtLeast 1)), ("by_default", bool)] [] j
  need (isField j "by_default" (.bool (← (← field j "rules").getArr?).isEmpty)) "by_default"

def margin (j : Json) : Check := do
  obj [("estimate", string), ("side", side), ("alternative", string), ("direction", direction)]
    [("nearest", string), ("no_single_valid_change", constJ (.bool true))] j
  need (has j "nearest" != has j "no_single_valid_change") "not exactly one of nearest and no_single_valid_change"

def riskOk (row case : Json) : Check := select [
  (kindIs case "admission", fun _ => admissionWith case row),
  (kindIs case "risk-elaborate", fun _ => answerOf case [("environment_id", hex64), ("document_hash", hex64),
    ("e_risk", closed [("sort", string), ("classes", strs), ("predicates", mapOf strs),
      ("words", closed [("risk__or_worse", pair), ("risk__less_worst", pair)])]),
    ("legend", texts), ("risk_premises", arr (labelled (oneOf riskLabels))),
    ("unranked_severities", arr pair), ("inlined", inlined), ("alternatives", altPremises),
    ("base_premises", arr anyLabel), ("followable", followableFormulas), ("unmapped_obligations", unmapped),
    ("order", strs), ("background", normsBackground), ("premises", layerPremises),
    ("conflict_targets", conflictTargets), ("fragment", bool)] row),
  (kindIs case "risk-decision", fun _ => alt [
    answerOf case [("environment_id", hex64), ("document_hash", hex64), ("decision_record_id", hexE),
      ("verdict", constJ (.str "CONFLICT")), ("target", string), ("tuple", strs), ("text", text)],
    answerOf case [("environment_id", hex64), ("document_hash", hex64), ("decision_record_id", hexE),
      ("tables", closed [
        ("might", arr (obj [("alternative", string), ("harm", string)]
          [("witness", arr (closed [("quantity", string), ("value", string)]))])),
        ("leads", arr (closed [("alternative", string), ("harm", string)]))]),
      ("statuses", arr riskStatus),
      ("worst_cases", mapOf (arr (closed [("harm", string), ("class", string)]))),
      ("margins", arr margin),
      ("record_invalid", arr (closed [("estimate", string), ("side", side), ("direction", direction),
        ("value", string), ("diagnostic", text)])),
      ("record_conflict", arr (closed [("estimate", string), ("side", side), ("direction", direction),
        ("value", string)])),
      ("lines", closed [("unexamined_possible", strs),
        ("assumed_ruled_out", closed [("decider", string), ("cells", strs)]),
        ("point_estimates", strs), ("default_decided", strs), ("dilemmas", atMost 1 strs)]),
      ("legend", atMost 3 texts), ("clear", strs), ("conditional_on", strs), ("text", text)]] row),
  (kindIs case "risk-conflict" && has case "witness", fun _ => answerOf case [
    ("verdict", oneOf ["CONFLICT", "UNKNOWN"]), ("target", both string (equalsAt case ["witness", "target"]))] row),
  (kindIs case "risk-conflict", fun _ => answerOf case [("verdict", oneOf ["CONFLICT-FREE", "UNKNOWN"]),
    ("targets", strs)] row),
  (kindIs case "risk-followable" && has case "witness", fun _ => dilemma case row),
  (kindIs case "risk-followable", fun _ => alt [
    answerOf case [("verdict", oneOf ["not computed", "UNKNOWN"]), ("text", text)],
    answerOf case [("verdict", constJ (.str "FOLLOWABLE")), ("conditional_on", strs)]] row),
  (kindIs case "risk-audit", fun _ => answerOf case [("alternative", string), ("q1", text), ("q2", text),
    ("procedure", strs), ("q3", strs), ("not_concluded", atMost 1 strs)] row),
  (kindIs case "risk-certificate", fun _ => answerOf case [("valid", bool), ("conditional_on", strs)] row)]

def risk (row case : Json) (index : Nat) : Check :=
  if VE.Risk.Run.usesRiskPath case then ownPath row case index pathError (riskOk row case)
  else alternatives row case index

/-- Risk.Eval.runCaseReported: no id, one result per condition. -/
def riskEval (row case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow row index false,
    fun _ => closed [("status", constJ (.str "error")), ("error", text)] row,
    fun _ => do
      closed [("status", constJ (.str "ok")), ("results", arr (alt [
        closed [("error", text)],
        fun x => do
          obj [("possible", bool), ("certain", bool), ("witness", alt [constJ .null, mapOf (fun v => do
            let _ ← v.getInt?)])] [] x
          if isField x "possible" (.bool true) then anyObj (← field x "witness")
          else need ((← field x "witness").isNull) "witness without a possible condition"]))] row
      need ((← length (← field row "results")) == (← length (← field case "conditions"))) "one result per condition"]

/-! ### quantity -/

/-- `Time.Wire.encTerm`, at most `fuel` levels (the rendering's length bounds them). -/
def qTerm : Nat → Json → Check
  | 0, _ => throw "term deeper than its rendering"
  | fuel + 1, j => do
    match (← j.getArr?).toList with
    | [.str "var", n] => nat n
    | [.str "const", c] => string c
    | [.str "const", g, c] => do string g; string c
    | [.str "num", g, z] => do string g; integerText z
    | [.str "add", g, t, u] => do string g; qTerm fuel t; qTerm fuel u
    | [.str "scale", g, k, t] => do string g; integerText k; qTerm fuel t
    | _ => throw "not a quantity term"

/-- `Time.Wire.encQ`. -/
def qFormula : Nat → Json → Check
  | 0, _ => throw "formula deeper than its rendering"
  | fuel + 1, j => do
    let t := qTerm fuel
    match (← j.getArr?).toList with
    | [.str "top"] | [.str "bottom"] => pure ()
    | [.str "unary", p, a] => do string p; t a
    | [.str "binary", p, a, b] => do string p; t a; t b
    | [.str "eq", a, b] | [.str "lt", a, b] | [.str "le", a, b] | [.str "date_on", a, b]
    | [.str "date_before", a, b] | [.str "date_after", a, b] | [.str "date_no_later", a, b] => do t a; t b
    | [.str "within_days", a, b, n] | [.str "shift_days", a, b, n] => do t a; t b; integerText n
    | [.str "elapsed_days", a, b, c] => do t a; t b; t c
    | [.str "not", f] => qFormula fuel f
    | [.str "and", f, g] | [.str "or", f, g] | [.str "implies", f, g] => do qFormula fuel f; qFormula fuel g
    | [.str "forall", s, f] | [.str "exists", s, f] => do string s; qFormula fuel f
    | _ => throw "not a quantity formula"

/-- `Time.Wire.encCoreTerm`. -/
def coreTerm : Nat → Json → Check
  | 0, _ => throw "term deeper than its rendering"
  | fuel + 1, j => do
    match (← j.getArr?).toList with
    | [.str "var", n] => nat n
    | [.str "const", c] => string c
    | [.str "num", z] => integerText z
    | [.str "add", t, u] => do coreTerm fuel t; coreTerm fuel u
    | [.str "scale", k, t] => do integerText k; coreTerm fuel t
    | _ => throw "not an order term"

/-- `Time.Wire.encCore`. -/
def coreFormula : Nat → Json → Check
  | 0, _ => throw "formula deeper than its rendering"
  | fuel + 1, j => do
    let t := coreTerm fuel
    match (← j.getArr?).toList with
    | [.str "top"] | [.str "bottom"] => pure ()
    | [.str "unary", p, a] => do string p; t a
    | [.str "binary", p, a, b] => do string p; t a; t b
    | [.str "eq", a, b] | [.str "lt", a, b] | [.str "le", a, b] => do t a; t b
    | [.str "not", f] => coreFormula fuel f
    | [.str "and", f, g] | [.str "or", f, g] | [.str "implies", f, g] => do coreFormula fuel f; coreFormula fuel g
    | [.str "forall", s, f] | [.str "exists", s, f] => do string s; coreFormula fuel f
    | _ => throw "not an order formula"

def qF (j : Json) : Check := qFormula j.compress.length j
def coreF (j : Json) : Check := coreFormula j.compress.length j

def digits (s : String) : Bool := !s.isEmpty && s.all Char.isDigit
def dateText (j : Json) : Check := do
  let s ← j.getStr?
  need (match s.splitOn "-" with
    | [y, m, d] => digits y && y.length == 4 && digits m && m.length == 2 && digits d && d.length == 2
    | _ => false) s!"date {s}"
def decimalText (j : Json) : Check := do
  let s ← j.getStr?
  let body := if s.startsWith "-" then s.drop 1 else s
  need (match body.splitOn "." with
    | [i] => digits i
    | [i, f] => digits i && digits f
    | _ => false) s!"amount {s}"

def qClaim : Json → Check := obj [("name", string),
  ("quantity", closed [("format", constJ (.str "ve-quantity@1")), ("formula", qF), ("traces", emptyArr)]),
  ("meaning_id", hex64)] [("label", fun l => do need ((← l.getStr?) != "asserted") "explicit default label")]

def premiseIds (case : Json) (j : Json) : Check := do
  arr hex64 j
  need ((← length j) == (← length (← field case "premises"))) "one identity per premise"

def quantityOk (row case : Json) : Check :=
  let ids : List Field := [("environment_id", hex64), ("target_environment_id", hex64)]
  let judged (verdict : Field) : Json → Check := answerOf case ([verdict, ("premise_meaning_ids", premiseIds case),
    ("conclusion_meaning_id", hex64), ("core_premise_meaning_ids", premiseIds case),
    ("core_conclusion_meaning_id", hex64)] ++ ids)
  let answer : Unit → Check := fun _ => do
    ok case ([("assurance", constJ (.str "lean-admitted")), ("Q", qF), ("core", coreF), ("meaning_id", hex64),
      ("core_meaning_id", hex64)] ++ ids) [("value", bool), ("evaluations", nat)] row
    if has case "model" then need (has row "value" && has row "evaluations") "value and evaluations are missing"
    else need (!has row "value" && !has row "evaluations") "value or evaluations without a model"
  select [
    ((case.getObj?).toBool && !has case "kind", answer),
    (kindIs case "admission", answer),
    (kindIs case "countermodel", fun _ => judged ("refutes", bool) row),
    (kindIs case "certificate", fun _ => judged ("valid", bool) row),
    (kindIs case "count", fun _ => answerOf case [("expansion", coreF)] row),
    (kindIs case "day", fun _ => answerOf case [("day", nat)] row),
    (kindIs case "civil", fun _ => answerOf case [("date", dateText)] row),
    (kindIs case "lower", fun _ => answerOf case [("coordinate", integerText)] row),
    (kindIs case "render", fun _ => answerOf case [("amount", decimalText)] row),
    (kindIs case "document", fun _ => answerOf case [("admitted", constJ (.bool true)),
      ("assurance", constJ (.str "lean-admitted")),
      ("report", closed [("root", both qClaim fun r => do
          need ((← field r "name") == (← path case ["document", "graph", "root"])) "root"),
        ("assumptions", arr qClaim)]),
      ("report_id", hex64), ("environment_id", hex64), ("kinds", kindsEcho case (some kind))] row)]

def quantity (row case : Json) (index : Nat) : Check :=
  ownPath row case index (fun r c => errorRow r c (if kindIs c "certificate" then ["valid"] else []))
    (quantityOk row case)

/-! ### norm-defaults -/

def normDefaultsOk (row case : Json) : Check := select [
  (kindIs case "admission", fun _ => admission row case),
  (kindIs case "norm-defaults-elaborate", fun _ => answerOf case [("order", strs), ("background", normsBackground),
    ("premises", layerPremises), ("conflict_targets", conflictTargets), ("fragment", bool),
    ("fill", arr (closed [("generator", constJ (.str "fill")), ("ast", gen)])), ("unspecified", strs),
    ("unsaid", arr (closed [("name", pfx ["unsaid__"]), ("sorts", strs)])),
    ("reached", arr (closed [("predicate", string), ("sorts", strs), ("ast", gen)])), ("fragment_fill", bool)] row),
  (kindIs case "norm-defaults-conflict" && has case "witness", fun _ => witnessConflict case row),
  (kindIs case "norm-defaults-conflict", fun _ => packagesConflict case row),
  (kindIs case "norm-defaults-status", fun _ => answerOf case [
    ("point_status", oneOf ["SETTLED yes", "SETTLED no", "UNDECIDED", "UNKNOWN"]),
    ("predicate", both string (equalsAt case ["predicate"]))] row),
  (kindIs case "norm-defaults-gaps" && has case "model", fun _ => answerOf case [("gaps", oneOf ["reachable", "unknown"]),
    ("predicate", both string (equalsAt case ["predicate"]))] row),
  (kindIs case "norm-defaults-gaps", fun _ => answerOf case [("gaps", oneOf ["none", "unknown"]),
    ("predicate", both string (equalsAt case ["predicate"]))] row),
  (kindIs case "norm-defaults-certificate", fun _ => answerOf case [("valid", bool), ("premises", nat)] row)]

def normDefaults (row case : Json) (index : Nat) : Check :=
  if VE.NormDefaults.Run.usesNormDefaultsPath case then
    ownPath row case index pathError (normDefaultsOk row case)
  else norms row case index

/-! ### discourse -/

def targetKind : Json → Check := oneOf ["entity", "predicate", "unit", "anchor", "rule", "claim", "document"]
def validityMap : Json → Check := mapOf fun v => do
  let s ← v.getStr?
  need (["checked", "refuted", "none"].contains s || s.startsWith "unconfirmed (") s!"verdict {s}"
def jointCount : Json → Check := alt [intAtLeast 1, text]
def reference : Json → Check := closed [("mention", string), ("unit", string),
  ("form", oneOf ["pronoun", "demonstrative", "definite", "ordinal_pair", "such", "possessive", "plural",
    "section_ref", "definition_ref", "document_name", "citation", "navigation"]),
  ("target", obj [("kind", targetKind)] [("name", string), ("version", nat), ("members", strs), ("pair", pair),
    ("units", strs), ("content_name", string)]),
  ("status", oneOf ["pending", "navigation", "resolved"])]
def resolvedTarget : Json → Check := obj [("kind", targetKind)]
  [("name", string), ("members", nonempty strs), ("pair", pair), ("units", nonempty strs)]
def pendingItem (j : Json) : Check := do
  match (← j.getArr?).toList with
  | [u, m] => do string u; pfx ["PresuppositionUnresolved: "] m
  | _ => throw "not a pending pair"
def choice (j : Json) : Check := arr (fun x => do
  match (← x.getArr?).toList with
  | [s, v, i] => do string s; nat v; nat i
  | _ => throw "not a choice") j

def discourseOk (row case : Json) : Check := select [
  (kindIs case "admission", fun _ => answerOf case [("admitted", alt [constJ (.bool true), constJ (.str "UNKNOWN")]),
    ("reading_verdicts", mapOf (constJ (.str "UNKNOWN (joint choices)"))), ("report", report),
    ("report_id", hexE), ("inner_report_id", hexE), ("document_id", hexE), ("source_id", hexE),
    ("environment_id", hexE), ("definitions_version", hexE), ("kinds", arr kind),
    ("references", arr reference), ("bound", mapOf gen), ("meaning_ids", mapOf hex64),
    ("presuppositions", mapOf (pfx ["discourse:presupposition:"])), ("pending", arr pendingItem),
    ("validity", validityMap), ("self_truth", strs),
    ("statuses", mapOf (oneOf ["CHECKED", "OPEN", "LABELLED", "UNFORMALISED"])), ("joint", jointCount)] row),
  (kindIs case "discourse-validity", fun _ => answerOf case [("validity", validityMap)] row),
  (kindIs case "discourse-resolve", fun _ => answerOf case [
    ("units", mapOf (alt [closed [("status", constJ (.str "resolved")), ("formula", gen), ("meaning_id", hex64)],
      closed [("status", constJ (.str "error")), ("error", text)]])),
    ("mentions", mapOf (obj [("accessible", arr resolvedTarget), ("recorded", resolvedTarget),
      ("accessible_recorded", bool)] [("pin", nat)])),
    ("well_formed", text), ("environment_id", hex64), ("source_id", hex64), ("joint", jointCount)] row),
  (kindIs case "discourse-joint", fun _ => alt [
    answerOf case [("verdict", constJ (.str "COMPLETE")), ("choices", nonempty (arr choice)), ("joint", gen)],
    answerOf case [("verdict", oneOf ["UNKNOWN", "INVALID"]), ("diagnostic", text)]] row)]

def discourse (row case : Json) (index : Nat) : Check :=
  if VE.Discourse.Run.usesDiscoursePath case then ownPath row case index pathError (discourseOk row case)
  else route row case index

/-! ### readings-route -/

def pairFacts : Json → Check := obj [("situation", string), ("witness", string), ("separated", bool),
  ("witness_admissible", bool), ("witness_value", nullOr bool), ("other_admissible", bool)]
  [("other_value", nullOr bool)]
def readingKey : Json → Check := alt [
  obj [("excepted", string)] [("bearer", string)],
  obj [("off", string), ("party", string)] [("bearer", string)],
  closed [("outweighs", string), ("lower", string), ("higher", string)],
  closed [("lim", string), ("act", string)],
  closed [("cond", string), ("act", string), ("condition", string)],
  closed [("aimed", string)]]
def keys : Json → Check := arr (closed [("key", readingKey), ("name", string)])
def candidate : Json → Check := alt [
  closed [("id", string), ("index", nat), ("pending", constJ (.bool true))],
  closed [("id", string), ("index", nat), ("pending", constJ (.bool false)), ("document_hash", hex64),
    ("owned", keys), ("shared", keys), ("findings", texts)]]

/-- Readings.Run.runCaseReported: the readings kinds, else any of the four runners `runLower`
reaches (the client does not evaluate `Compose.dispatch`). -/
def readingsRoute (row case : Json) (index : Nat) : Check :=
  if kindIs case "readings-validate" then
    ownPath row case index pathError (alt [
      answerOf case [("content_bearing", constJ (.bool false))],
      answerOf case [("content_bearing", constJ (.bool true)), ("sets", arr (closed [("set", string), ("version", nat),
        ("candidates", arr candidate),
        ("pairs", arr (closed [("reading", string), ("other", string), ("pair", pairFacts)])),
        ("findings", arr (pfx ["SeparatedByDecisionOnly: ", "SeparatedByActOnly: "]))]))]] row)
  else if kindIs case "readings-separate" then
    ownPath row case index pathError (answerOf case [("set", both string (equalsAt case ["set"])),
      ("pair", both pairFacts fun p => do
        need ((← field p "situation") == (← path case ["situation"])) "not the request's situation")] row)
  else firstOk [fun _ => rights row case index, fun _ => softNorms row case index,
    fun _ => normDefaults row case index, fun _ => norms row case index]

/-! ### diagnose -/

def diagnose (row case : Json) (index : Nat) : Check :=
  firstOk [fun _ => caseErrorRow row index false, fun _ => errorRow row case [], fun _ => do
    obj [("id", fun j => need (j == case.getObjValD "id") "id is not the request's"),
      ("status", constJ (.str "ok")), ("outcome", oneOf ["clean", "fault"])]
      [("diagnostic", closed [("contract", both string (equalsAt case ["unit"])), ("revision", nat), ("check", text),
        ("phase", text), ("code", text), ("class", oneOf VE.Service.rejectionCodes),
        ("path", fun p => do
          let s ← p.getStr?
          need (s.isEmpty || s.startsWith "/") s!"pointer {s}"),
        ("text", string), ("args", mapOf string)])] row
    presentIff row "diagnostic" (isField row "outcome" (.str "fault"))]

end Routes

def row (mode : String) (r case : Json) (index : Nat) : Check :=
  match mode with
  | "evaluate" => evaluate r case index
  | "check-certificate" => checkCertificate r case index
  | "order" => order r case index
  | "route" => route r case index
  | "norms" => norms r case index
  | "english" => english r case index
  | "environment" | "model" | "identity" => standalone mode r case index
  | "soft-norms" => Routes.softNorms r case index
  | "rights" => Routes.rights r case index
  | "speech-acts" => Routes.speechActs r case index
  | "reports" => Routes.reports r case index
  | "alternatives" => Routes.alternatives r case index
  | "risk" => Routes.risk r case index
  | "risk-eval" => Routes.riskEval r case index
  | "quantity" => Routes.quantity r case index
  | "norm-defaults" => Routes.normDefaults r case index
  | "discourse" => Routes.discourse r case index
  | "readings-route" => Routes.readingsRoute r case index
  | "diagnose" => Routes.diagnose r case index
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

/-- `Service.Protocol.coding`: beside a rejection (an error row with a text `error`), a public
diagnostic code and possibly a generator name; beside any other result, neither. -/
def coding (b result : Json) : Check := do
  if isField result "status" (.str "error") && (result.getObjValD "error").getStr?.toBool then
    need (VE.Service.rejectionCodes.contains (← (← field b "code").getStr?)) "code is not a public code"
    if let .ok g := b.getObjVal? "generator" then string g
  else need (!has b "code" && !has b "generator") "code beside a result that is not a rejection"

/-- `Service.Protocol.bound`: result `i` carries position `i` and the digest of case `i`, and
the coding of a rejection. -/
def bound (b : Json) (index : Nat) (digest : Json) : Except String Json := do
  shape b ["index", "digest", "result"] ["code", "generator"]
  coding b (← field b "result")
  need ((← (← field b "index").getNat?) == index) "index is not the result's position"
  hex64 (← field b "digest")
  need ((← field b "digest") == digest) "digest is not the case's"
  field b "result"

/-- `Service.Protocol`: a request error bound to the request's mode and case digests
(`requestError`), or one bound result per case with exact counts; `content` is applied to
each bound entry and its result, with its case and position. -/
def response (mode : String) (request r : Json) (content : Json → Json → Json → Nat → Check) : Check := do
  let nonce ← field request "id"
  if isField r "status" (.str "error") then
    shape r ["id", "status", "mode", "digests", "error", "code"] []
    need ((← field r "id") == nonce && (← (field r "id")).getStr?.toBool) "id is not the nonce"
    need (isField r "mode" (.str mode)) "mode"
    need ((← field r "digests") == (← field request "digests")) "digests are not the request's"
    text (← field r "error")
    need (VE.Service.rejectionCodes.contains (← (← field r "code").getStr?)) "code is not a public code"
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
          row mode x cases[i]! i; content results[i]! x cases[i]! i; pure x with
      | .ok x => rows := rows.push x
      | .error m => throw s!"result {i}: {m}"
    let counts ← field r "counts"
    shape counts ["cases", "bytes", "errors"] []
    need ((← (← field counts "cases").getNat?) == cases.size) "counts.cases"
    need ((← field counts "bytes") == (← field request "bytes")) "counts.bytes"
    let errors := (rows.filter (fun x => isField x "status" (.str "error"))).size
    need ((← (← field counts "errors").getNat?) == errors) "counts.errors"

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
