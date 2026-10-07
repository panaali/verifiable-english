import VE.Attribution.Wire

/-! The public fault order and texts of a reports document (LEAN-FIRST-PLAN DRI answer 3:
Lean's texts are canonical, and Python's better user-facing texts are ported into Lean).

Before this batch the public answer to a malformed reports document was the Python
`ReportsDocument`'s (`ve/reports.py` at `9aaf918d`): one walk over the raw JSON that names the
offending record, context, assessment, unit, bridge or scoped check. `check` is that walk, in
that order and with those texts, over the raw document; Python's view of each value
(`list(x)`, `x.get(k)`, `str(x)`, `null`) is reproduced here, so no Python code decides.

It never accepts anything the decoder rejects: it only rejects, and after an accepted walk
`Wire.decodeDocument` reads the document, whose `firstFailure` names the remaining faults (metadata,
generated predicate limits) in the same order. A formula's verdict is the decoder's
(`Route.Wire.decodeClosed`); only its text is Python's (`formulaFault`), named by the walk of
Python's AST decoder here and by the typing classifier the caller supplies
(`Service.TypingDiagnostic.diagnose`, a service module this layer cannot import).

JSON `null`: the service's restricted reader has none, so the relay removes each `null` and
lists its position (`nulls`); `restore` puts them back for this walk, which treats them as
Python treats `None`, and the decoder reads the document without them. -/
namespace VE.Reports.Preflight
open Lean
open VE.Route.Admission (token)

/-- The typing classifier: profiles, vocabulary and formulas to Python's first diagnostic. -/
abbrev Typing := List String → Json → List Json → Option String

/-! ## Python's view of a JSON value -/

def members (j : Json) : List (String × Json) :=
  match j.getObj? with
  | .ok o => o.toList
  | .error _ => []

def keys (j : Json) : List String := (members j).map Prod.fst

def isObj : Json → Bool
  | .obj _ => true
  | _ => false

/-- Python `set(row) == set(names)`. -/
def sameKeys (j : Json) (names : List String) : Bool :=
  isObj j && (keys j).length == names.length && names.all (keys j).contains

def hasKey (j : Json) (k : String) : Bool := (keys j).contains k

/-- Python `token(x)`. -/
def isToken : Json → Bool
  | .str s => token s
  | _ => false

def isNonEmptyStr : Json → Bool
  | .str s => !s.isEmpty
  | _ => false

def isStr : Json → Bool
  | .str _ => true
  | _ => false

def arr : Json → List Json
  | .arr a => a.toList
  | _ => []

def isArr : Json → Bool
  | .arr _ => true
  | _ => false

/-- A JSON integer (Python `type(x) is int`; the reader has no fractions). -/
def int? : Json → Option Int
  | .num n => if n.exponent == 0 then some n.mantissa else none
  | _ => none

/-- Python `repr` of a string: its quotes, and escapes for `\\`, the quote, controls and the
Latin-1 non-printables. -/
def quote (s : String) : String :=
  let q := if s.contains '\'' && !s.contains '"' then '"' else '\''
  let hex := fun (n : Nat) => "\\x" ++ (if n < 16 then "0" else "") ++ String.mk (Nat.toDigits 16 n)
  let esc := fun (c : Char) =>
    if c == '\\' then "\\\\" else if c == q then "\\" ++ c.toString
    else if c == '\t' then "\\t" else if c == '\n' then "\\n" else if c == '\r' then "\\r"
    else if c.toNat < 0x20 || (0x7f ≤ c.toNat && c.toNat ≤ 0xa0) || c.toNat == 0xad then hex c.toNat
    else c.toString
  q.toString ++ String.join (s.toList.map esc) ++ q.toString

/-- Python `repr` of a decoded JSON value. -/
def pyRepr : Nat → Json → String
  | 0, _ => "..."
  | _ + 1, .str s => quote s
  | _ + 1, .null => "None"
  | _ + 1, .bool b => if b then "True" else "False"
  | _ + 1, .num n => toString n
  | n + 1, .arr a => "[" ++ ", ".intercalate (a.toList.map (pyRepr n)) ++ "]"
  | n + 1, .obj o => "{" ++ ", ".intercalate (o.toList.map fun (k, v) => quote k ++ ": " ++ pyRepr n v) ++ "}"

/-- Python `str` of a decoded JSON value, as an f-string shows it. -/
def pyStr : Json → String
  | .str s => s
  | j => pyRepr 64 j

/-- Python `list(x)`: a list, a string's characters, an object's keys; any other value (a
`TypeError` before) is one malformed row. -/
def pyList : Json → List Json
  | .arr a => a.toList
  | .str s => s.toList.map fun c => .str (String.singleton c)
  | .obj o => o.toList.map fun (k, _) => .str k
  | j => [j]

/-- A document member as the Python constructor received it (absent: the empty list). -/
def field (doc : Json) (k : String) : Json :=
  match doc.getObjVal? k with
  | .ok v => v
  | .error _ => .arr #[]

/-! ## `null` positions -/

inductive Step where
  | key (k : String)
  | index (i : Nat)

def decodeStep : Json → Except String Step
  | .str k => pure (.key k)
  | j => do pure (.index (← j.getNat?))

/-- The case's `nulls` member: each removed `null`'s path in the document. -/
def nullPaths (j : Json) : Except String (List (List Step)) :=
  match j.getObjVal? "nulls" with
  | .ok v => do (← v.getArr?).toList.mapM fun p => do (← p.getArr?).toList.mapM decodeStep
  | .error _ => pure []

def setNull : List Step → Json → Json
  | [], _ => .null
  | .key k :: rest, j@(.obj _) => j.setObjVal! k (setNull rest (j.getObjValD k))
  | .index i :: rest, .arr a => if h : i < a.size then .arr (a.set i (setNull rest a[i])) else .arr a
  | _, j => j

def restore (doc : Json) (paths : List (List Step)) : Json := paths.foldl (fun d p => setNull p d) doc

/-! ## Formulas: Python's AST decoder, then its typing -/

abbrev Walk := StateT Nat (Except String)

def termArity : String → Option Nat
  | "var" | "const" | "num" => some 2
  | "add" | "scale" => some 3
  | _ => none

def formulaArity : String → Option Nat
  | "top" | "bottom" => some 1
  | "not" => some 2
  | "unary" | "eq" | "lt" | "le" | "and" | "or" | "implies" | "forall" | "exists" | "atom" => some 3
  | "binary" => some 4
  | "reach" => some 5
  | _ => none

/-- Python `decimal_from_wire`. -/
def decimal : Json → Walk _root_.Unit
  | .str s =>
    if s.length > 40 then throw "ResourceLimit: Integer literal exceeds 40 characters"
    else
      let ok := match s.toList with
        | '-' :: ds => VE.Route.AstLimit.digitsOk ds && ds != ['0']
        | ds => VE.Route.AstLimit.digitsOk ds
      if ok then pure () else throw s!"SyntaxError: Non-canonical integer literal {quote s}"
  | _ => throw "SyntaxError: Integer wire values must be canonical decimal strings"

def atomTerms : String := "SyntaxError: Atom terms must be an array of three to six terms"
def reachEdge : String := "SyntaxError: Reach edge must be a tagged array"

/-- Python `_Decoder.decode`: one node at `depth`, counted; terms when `term`. Fuel only
bounds recursion (the 64-level limit is reached first). -/
def decodeNode : Nat → Bool → Nat → Json → Walk _root_.Unit
  | 0, _, _, _ => pure ()
  | fuel + 1, term, depth, j => do
    let n := (← get) + 1
    set n
    if n > 10000 || depth > 64 then throw "ResourceLimit: AST exceeds depth or node budget"
    let (tag, args) ← match j with
      | .arr a => match a.toList with
        | .str t :: rest => pure (t, rest)
        | _ => throw "SyntaxError: AST nodes must be nonempty tagged JSON arrays"
      | _ => throw "SyntaxError: AST nodes must be nonempty tagged JSON arrays"
    let arity := if term then termArity tag else formulaArity tag
    unless arity == some (args.length + 1) do
      throw s!"SyntaxError: Unknown AST tag or incorrect arity: {quote tag}"
    let t := decodeNode fuel true
    let f := decodeNode fuel false
    match tag, args with
    | "var", [i] =>
      unless VE.Route.AstLimit.validIndex i do throw "UnboundVariable: Invalid variable index"
    | "num", [v] => decimal v
    | "add", [a, b] => do t (depth + 1) a; t (depth + 1) b
    | "scale", [k, x] => do decimal k; t (depth + 1) x
    | "lt", [a, b] | "le", [a, b] | "eq", [a, b] => do t 1 a; t 1 b
    | "unary", [_, a] => t 1 a
    | "binary", [_, a, b] => do t 1 a; t 1 b
    | "atom", [_, ts] =>
      match ts with
      | .arr xs =>
        unless 3 ≤ xs.size && xs.size ≤ 6 do throw atomTerms
        for x in xs.toList do t 1 x
      | _ => throw atomTerms
    | "reach", [_, edge, a, b] => do
      match edge with
      | .arr e => match e.toList with
        | [.str "named", _] => pure ()
        | [.str "body", _, body] => f (depth + 1) body
        | .str _ :: _ => throw "SyntaxError: Unknown Reach edge tag or incorrect arity"
        | _ => throw reachEdge
      | _ => throw reachEdge
      t 1 a
      t 1 b
    | "not", [a] => f (depth + 1) a
    | "and", [a, b] | "or", [a, b] | "implies", [a, b] => do f (depth + 1) a; f (depth + 1) b
    | "forall", [_, a] | "exists", [_, a] => f (depth + 1) a
    | _, _ => pure ()

def decoderFault (j : Json) : Option String :=
  match (decodeNode 300 false 1 j).run' 0 with
  | .error m => some m
  | .ok () => none

/-- A scope the walk types formulas in: its environment and Python's view of it. -/
structure Scope where
  E : VE.Environment
  profiles : List String
  vocabulary : Json

/-- Python `formula_from_data(scope, ast)`'s diagnostic: the decoder decides; a rejection
is named as Python's decoder, then its type checker, name it, else as the decoder does. -/
def formulaFault (typing : Typing) (s : Scope) (ast : Json) : Option String :=
  match VE.Route.Wire.decodeClosed s.E ast with
  | .ok _ => none
  | .error m => some ((decoderFault ast).getD ((typing s.profiles s.vocabulary [ast]).getD m))

def formulaOk (typing : Typing) (s : Scope) (ast : Json) : Except String _root_.Unit :=
  match formulaFault typing s ast with
  | some m => throw m
  | none => pure ()

/-- A quoted package's environment as Python's `Environment` reads it. -/
def localScope (env : Json) : Except String (VE.Route.Gate.Envelope × Scope) := do
  let e ← VE.Route.Gate.decodeEnvelope env
  let rv ← VE.Route.Wire.decodeVocabulary e.profiles e.vocabulary
  pure (e, ⟨rv.environment, e.profiles, e.vocabulary⟩)

/-! ## The walk -/

/-- What the walk knows of the document while it reads it. -/
structure Facts where
  typing : Typing
  root : Scope
  rootId : String
  holders : List String
  evidence : String
  contexts : List String
  assessments : List String
  units : List Json

def acts : List String := ["says", "believes", "wants", "intends"]

/-- Python `_records`: a list of at most 256 objects with distinct token ids. -/
def records (rows : Json) (label singular : String) : Except String (List (String × Json)) := do
  let .arr a := rows | throw s!"InvalidInput: {label} must be a list"
  if a.size > 256 then throw s!"ResourceLimit: {label}"
  a.toList.foldlM (init := []) fun acc row => do
    let some id := (match row.getObjValD "id" with
        | .str s => if isObj row && token s then some s else none
        | _ => none)
      | throw s!"InvalidInput: {label} record"
    if acc.any (·.1 == id) then throw s!"DuplicateDeclaration: {singular} {id}"
    pure (acc ++ [(id, row)])

/-- The first id (Python `row.get("id")`, `None` for a non-object) seen before. -/
def firstRepeat : List Json → List Json → Option Json
  | _, [] => none
  | seen, x :: xs => if seen.contains x then some x else firstRepeat (seen ++ [x]) xs

def context (cid : String) (row : Json) : Except String _root_.Unit := do
  let rt := row.getObjValD "reference_time"
  let d := row.getObjValD "description"
  unless (sameKeys row ["id", "tense", "description"] ||
      sameKeys row ["id", "tense", "reference_time", "description"]) &&
      (rt == .null || isToken rt) && isNonEmptyStr d do
    throw s!"InvalidInput: context {cid}"
  unless ["present", "past", "perfect"].any (fun t => row.getObjValD "tense" == .str t) do
    throw s!"ContextTense: {cid}"
  if (d.getStr?.toOption.getD "").utf8ByteSize > 200 then throw "ResourceLimit: context description"

def assessment (F : Facts) (aid : String) (row : Json) : Except String _root_.Unit := do
  unless sameKeys row ["id", "context", "decided_by", "necessary", "sufficient", "factors", "precedents",
      "jurisdiction", "version"] && isToken (row.getObjValD "decided_by") do
    throw s!"InvalidInput: assessment {aid} needs decided_by"
  let c := row.getObjValD "context"
  unless (match c with | .str s => F.root.E.constants s == some F.evidence | _ => false) do
    throw s!"UnknownSymbol: evidence context {pyStr c}"
  let lists := ["necessary", "sufficient", "factors", "precedents"]
  unless isToken (row.getObjValD "jurisdiction") && (int? (row.getObjValD "version")).any (· ≥ 1) &&
      lists.all (fun f => isArr (row.getObjValD f)) do
    throw s!"InvalidInput: assessment {aid}"
  for f in ["necessary", "sufficient"] do
    for formula in arr (row.getObjValD f) do formulaOk F.typing F.root formula
  unless ["factors", "precedents"].all (fun f => (arr (row.getObjValD f)).all isNonEmptyStr) do
    throw s!"InvalidInput: assessment {aid}"

/-- Python `ReportsDocument._meaning`. -/
def meaningOk (m : Json) : Bool :=
  m == .str "specified" ||
    match members m with
    | [("open", v)] => isArr v && (arr v).all isStr
    | [("contextual", v)] | [("unformalised", v)] => isStr v
    | _ => false

def reportKeys : List String := ["report", "assessment", "negated"]

def isReportContent (c : Json) : Bool := isObj c && (keys c).any reportKeys.contains

/-- Python `_node`: one content node of unit `uid` at `depth`. -/
def node (F : Facts) (uid : String) : Nat → Bool → Nat → Json → Except String _root_.Unit
  | 0, _, _, _ => pure ()
  | fuel + 1, top, depth, j => do
    if depth > 16 then throw "ResourceLimit: content depth"
    let [(tag, value)] := members j | throw s!"InvalidInput: invalid content for {uid}"
    if top && !reportKeys.contains tag then throw s!"InvalidInput: invalid content for {uid}"
    match tag with
    | "ast" => formulaOk F.typing F.root value
    | "norm" =>
      unless sameKeys value ["environment", "norms"] do throw s!"InvalidInput: quoted norm in {uid}"
      let (e, _) ← localScope (value.getObjValD "environment")
      unless e.profiles.contains "norms@0" do throw "UnsupportedProfile: quoted norm needs norms@0 locally"
      let _ ← Wire.decodeNormNode value
    | "definition" =>
      unless sameKeys value ["environment", "content"] do throw s!"InvalidInput: quoted definition in {uid}"
      let (e, s) ← localScope (value.getObjValD "environment")
      unless e.profiles.contains "definitions@0" do
        throw "UnsupportedProfile: quoted definition needs definitions@0 locally"
      let statement := value.getObjValD "content"
      if statement != .null then
        unless sameKeys statement ["ast"] do throw s!"InvalidInput: definition statement in {uid}"
        formulaOk F.typing s (statement.getObjValD "ast")
      let _ ← Wire.decodeDefinitionNode (match value, statement with
        | .obj kvs, .null => .obj (kvs.erase "content")
        | v, _ => v)
    | "report" =>
      unless sameKeys value ["holder", "act", "context", "content"] ||
          sameKeys value ["holder", "act", "context", "literal", "content"] do
        throw s!"InvalidInput: report in {uid}"
      let holder := value.getObjValD "holder"
      let sort := match holder with
        | .str h => F.root.E.constants h
        | _ => none
      let some sort := sort | throw s!"UnknownHolder: {pyStr holder}"
      unless F.holders.contains sort do throw s!"HolderSort: {pyStr holder} is not of a holder sort"
      let act := value.getObjValD "act"
      unless acts.any (fun a => act == .str a) do
        throw s!"UnsupportedAct: {pyStr act} (reports@0 admits says, believes, wants, intends)"
      let c := value.getObjValD "context"
      unless F.contexts.any (fun x => c == .str x) do throw s!"UnknownContext: {pyStr c}"
      let literal := value.getObjValD "literal"
      if literal != .null then
        unless isNonEmptyStr literal do throw "InvalidInput: literal"
        if (literal.getStr?.toOption.getD "").utf8ByteSize > 4096 then throw "ResourceLimit: literal bytes"
      node F uid fuel false (depth + 1) (value.getObjValD "content")
    | "assessment" =>
      unless sameKeys value ["judgment", "record", "content"] do throw s!"InvalidInput: assessment in {uid}"
      let record := value.getObjValD "record"
      unless (value.getObjValD "judgment" == .str "may" || value.getObjValD "judgment" == .str "probably") &&
          F.assessments.any (fun a => record == .str a) do
        throw s!"UnknownAssessment: {pyStr record}"
      node F uid fuel false (depth + 1) (value.getObjValD "content")
    | "negated" =>
      unless (match members value with
          | [(k, _)] => k == "report" || k == "assessment"
          | _ => false) do
        throw s!"InvalidInput: negated operand in {uid}"
      node F uid fuel false depth value
    | _ => throw s!"InvalidInput: invalid content for {uid}"

/-- Python `_kind_matches`. -/
def kindMatches : Nat → Json → Json → Bool
  | 0, _, _ => false
  | n + 1, kind, j =>
    match members j with
    | [("negated", v)] => kindMatches n kind v
    | [("ast", _)] => kind == .str "asserted"
    | [("norm", _)] => kind == .str "norm"
    | [("definition", _)] => kind == .str "definition"
    | [("report", v)] =>
      match arr kind, kind with
      | [.str "attributed", h, a, inner], .arr _ =>
        h == v.getObjValD "holder" && a == v.getObjValD "act" && kindMatches n inner (v.getObjValD "content")
      | _, _ => false
    | [("assessment", v)] =>
      let modal := if v.getObjValD "judgment" == .str "may" then "could" else "likely"
      match arr kind, kind with
      | [.str "hedged", m, inner], .arr _ => m == .str modal && kindMatches n inner (v.getObjValD "content")
      | _, _ => false
    | _ => false

/-- Python's unit loop: ids, spans, fields, meaning, then the unit's content. -/
def units (F : Facts) (rows : Json) : Except String _root_.Unit := do
  let .arr a := rows | throw "InvalidInput: units must be a list"
  let mut seen : List String := []
  let mut cursor : Int := 0
  for unit in a.toList do
    let some uid := (match unit.getObjValD "id" with
        | .str s => if isObj unit && token s && !seen.contains s then some s else none
        | _ => none)
      | throw "InvalidInput: report unit"
    seen := seen ++ [uid]
    let span := match arr (unit.getObjValD "span") with
      | [x, y] => match int? x, int? y with
        | some x, some y => if 0 ≤ x && x ≤ y && cursor ≤ x then some y else none
        | _, _ => none
      | _ => none
    let some stop := span | throw "unit spans must be sorted and non-overlapping"
    cursor := stop
    let content := unit.getObjValD "content"
    let report := isReportContent content
    let all := ["id", "span", "kind", "content", "meaning", "support"]
    unless (if report then sameKeys unit all
        else ["id", "span", "kind"].all (hasKey unit) && (keys unit).all all.contains) do
      throw s!"InvalidInput: unit {uid} fields"
    if hasKey unit "meaning" && !meaningOk (unit.getObjValD "meaning") then throw "invalid meaning status"
    if report then
      node F uid 40 true 1 content
      unless kindMatches 40 (unit.getObjValD "kind") content do throw s!"KindMismatch: {uid}"
    else if content != .null then
      let quoted := match arr (unit.getObjValD "kind") with
        | .str k :: _ => k == "attributed" || k == "hedged"
        | _ => false
      if quoted || !sameKeys content ["ast"] then throw s!"InvalidInput: invalid content for {uid}"
      formulaOk F.typing F.root (content.getObjValD "ast")

/-- Python `_path_object`: a unit (any value) and a depth. -/
def pathObject (p : Json) : Except String (Json × Nat) :=
  match p with
  | .str _ => pure (p, 0)
  | _ =>
    let parsed := if sameKeys p ["unit", "path"] then
        match p.getObjValD "path" with
        | .str s => parsePath s
        | _ => none
      else none
    match parsed with
    | some n => pure (p.getObjValD "unit", n)
    | none => throw "InvalidInput: bridge path"

/-- One step of Python `_resolve`: through a negation, then into a report's or assessment's
content or a definition package's statement (whose scope is the package's environment). -/
def descend : Option (Json × Option Json) → Option (Json × Option Json)
  | none => none
  | some (.null, _) => none
  | some (n, scope) =>
    let n := if hasKey n "negated" then n.getObjValD "negated" else n
    if hasKey n "report" then some ((n.getObjValD "report").getObjValD "content", scope)
    else if hasKey n "assessment" then some ((n.getObjValD "assessment").getObjValD "content", scope)
    else if hasKey n "definition" then
      let d := n.getObjValD "definition"
      some (d.getObjValD "content", some (d.getObjValD "environment"))
    else none

/-- Python `_resolve` (an absent node is no target). -/
def resolve (F : Facts) (unit : Json) (depth : Nat) : Option (Json × Option Json) :=
  match F.units.find? fun u => u.getObjValD "id" == unit && isReportContent (u.getObjValD "content") with
  | none => none
  | some u => match (List.range (depth + 1)).foldl (fun acc _ => descend acc) (some (u.getObjValD "content", none)) with
    | some (.null, _) => none
    | r => r

def scopeOf (F : Facts) : Option Json → Except String (String × Scope)
  | none => pure (F.rootId, F.root)
  | some env => do
    let (e, s) ← localScope env
    pure (← VE.Route.Wire.environmentId e.profiles env, s)

/-- Python `_scoped_object`. -/
def scopedRow (F : Facts) (row : Json) : Except String _root_.Unit := do
  let ks := keys row
  let all := ["id", "payloads", "conclusion", "certificate", "envelope"]
  let c := row.getObjValD "conclusion"
  unless isObj row && ["id", "payloads", "conclusion"].all ks.contains && ks.all all.contains &&
      isStr (row.getObjValD "id") && isArr (row.getObjValD "payloads") && sameKeys c ["ast"] do
    throw "InvalidInput: scoped"
  let sid := pyStr (row.getObjValD "id")
  if row.getObjValD "envelope" != .null && row.getObjValD "certificate" == .null then
    throw s!"InvalidInput: envelope without a certificate on scoped check {sid}"
  let payloads ← (arr (row.getObjValD "payloads")).mapM pathObject
  if payloads.length > 64 then throw "ResourceLimit: scoped payloads"
  let resolved := payloads.map fun (u, d) => resolve F u d
  unless resolved.all (fun r => match r with
      | some (n, _) => (keys n).head? == some "ast"
      | none => false) do
    throw s!"ScopedTarget: {sid}"
  let scopes ← resolved.filterMap id |>.mapM fun (_, s) => scopeOf F s
  let some (first, scope) := scopes.head? | throw s!"ScopedEnvironment: {sid}"
  unless scopes.all (·.1 == first) && (VE.Route.Wire.decodeClosed scope.E (c.getObjValD "ast")).toBool do
    throw s!"ScopedEnvironment: {sid}"

/-- Python `_bridge_object`. -/
def bridgeRow (F : Facts) (row : Json) : Except String _root_.Unit := do
  let ks := keys row
  unless isObj row && ["id", "unit", "accepted_by", "reason"].all ks.contains &&
      ks.all ["id", "unit", "accepted_by", "reason", "path"].contains &&
      ["id", "unit", "accepted_by"].all (fun f => isStr (row.getObjValD f)) &&
      isArr (row.getObjValD "reason") && (arr (row.getObjValD "reason")).all isStr do
    throw "InvalidInput: bridge"
  let (unit, depth) ← pathObject (if hasKey row "path" then
      Json.mkObj [("unit", row.getObjValD "unit"), ("path", row.getObjValD "path")]
    else row.getObjValD "unit")
  let some (n, scope) := resolve F unit depth | throw s!"BridgeTarget: {pyStr unit}"
  if ((keys n).head?.any fun k => k == "norm" || k == "definition") || scope.isSome then
    throw s!"BridgeKindMismatch: {pyStr unit}, {depth}"

/-- The pre-batch Python's walk over a reports document, in its order and with its texts. On
success the decoder reads the document as given (without its `null`s). -/
def check (typing : Typing) (environment document : Json) (nulls : List (List Step)) :
    Except String _root_.Unit := do
  let doc := restore document nulls
  -- The environment's own faults first (Python's `Environment` came first); a well-formed
  -- envelope without the profile has the reports document's text.
  let re ← match Wire.decodeEnvironment environment with
    | .ok re => pure re
    | .error e =>
      let profiles := (arr (environment.getObjValD "profiles")).filterMap (·.getStr?.toOption)
      if !profiles.contains "reports@0" && (VE.Route.Gate.decodeEnvelope environment).toBool then
        throw "UnsupportedProfile: reports@0 needs a reports block"
      else throw e
  let contexts ← records (field doc "contexts") "contexts" "context"
  let assessments ← records (field doc "assessments") "assessments" "assessment"
  let bridges := pyList (field doc "bridges")
  let checks := pyList (field doc "scoped")
  for (label, rows) in [("bridge", bridges), ("scoped", checks)] do
    let ids := rows.map fun r => if isObj r then r.getObjValD "id" else .null
    match firstRepeat [] ids with
    | some d => if d != .null then throw s!"DuplicateDeclaration: {label} {pyStr d}"
    | none => pure ()
  if bridges.length > 1000 || checks.length > 256 then throw "ResourceLimit: bridges or scoped"
  unless (pyList (field doc "choices")).isEmpty do
    throw "UnsupportedProfile: reports reading choices await the Lean route"
  let F : Facts := ⟨typing, ⟨re.rv.environment, re.profiles, environment.getObjValD "vocabulary"⟩,
    ← VE.Route.Wire.environmentId re.profiles environment, re.holders, re.evidence,
    contexts.map Prod.fst, assessments.map Prod.fst, arr (field doc "units")⟩
  for (cid, row) in contexts do context cid row
  for (aid, row) in assessments do assessment F aid row
  units F (field doc "units")
  for row in checks do scopedRow F row
  for row in bridges do bridgeRow F row

end VE.Reports.Preflight
