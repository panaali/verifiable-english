import Lean.Data.Json
import VE.CertificateWire

/-! # Response shapes: the one source of the client's response schemas

The service's responses are described once, here and in `ResponseShape.Schemas`, as `Shape`
values: a subset of the client's schema dialect
(`ve/backends/lean_service_schema/README.md`) as Lean data. From that one description

* `render` writes every file of `ve/backends/lean_service_schema/` (`ve_response_decode`,
  check `schemas`; `tools/response_schemas.py` writes and checks them), so no schema file is
  written by hand, and
* `check` decides a value with the dialect's meaning, which is how `ve_response_decode`
  decides responses (the Lean side of the client's validation).

At a `lean` node a Lean function (a runner's decoder or dispatch test) decides the same
value beside the shape; the two must agree, or the check fails as `broken`, which no
alternative, negation or condition hides. No runner imports this module: it is the schema
generator, test tooling, and the source of the skeletons (`ResponseShape.Skeleton`) against which
`ResponseShape.Encoders` proves every runner's rows. -/

namespace ResponseShape
open Lean

/-! ## Regular expressions (`pattern`)

Python's `re` syntax, matched against the whole string with `.` matching every character
(the client's `re.fullmatch` with `DOTALL`). `matches` uses Brzozowski derivatives. -/

inductive Re where
  | empty
  | eps
  | lit (s : String)
  | cls (ranges : List (Char × Char))
  | any
  | seq (a b : Re)
  | alt (a b : Re)
  | star (r : Re)
  | rep (r : Re) (lo hi : Nat)
  deriving BEq, Inhabited

namespace Re

def mkSeq : Re → Re → Re
  | .empty, _ => .empty
  | _, .empty => .empty
  | .eps, b => b
  | a, .eps => a
  | a, b => .seq a b

def mkAlt : Re → Re → Re
  | .empty, b => b
  | a, .empty => a
  | a, b => if a == b then a else .alt a b

def nullable : Re → Bool
  | .empty => false
  | .eps => true
  | .lit s => s.isEmpty
  | .cls _ => false
  | .any => false
  | .seq a b => a.nullable && b.nullable
  | .alt a b => a.nullable || b.nullable
  | .star _ => true
  | .rep r lo _ => lo == 0 || r.nullable

def deriv (c : Char) : Re → Re
  | .empty => .empty
  | .eps => .empty
  | .lit s => match s.toList with
    | d :: rest => if c == d then (if rest.isEmpty then .eps else .lit (String.mk rest)) else .empty
    | [] => .empty
  | .cls rs => if rs.any (fun (lo, hi) => lo ≤ c && c ≤ hi) then .eps else .empty
  | .any => .eps
  | .seq a b => mkAlt (mkSeq (deriv c a) b) (if a.nullable then deriv c b else .empty)
  | .alt a b => mkAlt (deriv c a) (deriv c b)
  | .star r => mkSeq (deriv c r) (.star r)
  | .rep r lo hi => match hi with
    | 0 => .empty
    | hi + 1 => mkSeq (deriv c r) (.rep r (lo - 1) hi)

def «matches» (r : Re) (s : String) : Bool := (s.toList.foldl (fun r c => deriv c r) r).nullable

/-- One of the strings, then anything. -/
def prefixes : List String → Re
  | [] => .empty
  | p :: ps => .seq (ps.foldl (fun r q => .alt r (.lit q)) (.lit p)) (.star .any)

/-- One of the strings exactly. -/
def oneOf : List String → Re
  | [] => .empty
  | p :: ps => ps.foldl (fun r q => .alt r (.lit q)) (.lit p)

def optional (r : Re) : Re := .rep r 0 1

def special : List Char := ['\\', '.', '^', '$', '*', '+', '?', '{', '}', '[', ']', '|', '(', ')']

def escape (s : String) : String :=
  s.foldl (fun out c => out ++ (if special.contains c then "\\" else "") ++ c.toString) ""

def classChar (c : Char) : String := (if ['\\', ']', '[', '^', '-'].contains c then "\\" else "") ++ c.toString

/-- Python `re` syntax; `prec` is the context: 0 alternation, 1 sequence, 2 an operand of a
repetition. -/
def render : Re → Nat → String
  | .empty, _ => "(?!)"
  | .eps, _ => ""
  | .lit s, prec => if prec ≥ 2 && s.length != 1 then "(" ++ escape s ++ ")" else escape s
  | .cls rs, _ => "[" ++ String.join (rs.map fun (lo, hi) =>
      if lo == hi then classChar lo else classChar lo ++ "-" ++ classChar hi) ++ "]"
  | .any, _ => "."
  | .seq a b, prec => let s := render a 1 ++ render b 1; if prec ≥ 2 then "(" ++ s ++ ")" else s
  | .alt a b, prec => let s := render a 0 ++ "|" ++ render b 0; if prec ≥ 1 then "(" ++ s ++ ")" else s
  | .star r, _ => render r 2 ++ "*"
  | .rep r lo hi, _ => render r 2 ++
      (if lo == 0 && hi == 1 then "?" else if lo == hi then s!"\{{lo}}" else s!"\{{lo},{hi}}")

end Re

/-! ## Shapes -/

/-- A schema of the dialect. A keyword constructor is a schema object with that keyword
alone; `node` is one schema object holding several keywords (their conjunction, as in JSON
Schema, with `x-fuel` applying to the whole object). -/
inductive Shape where
  | bool (b : Bool)
  | type (types : List String)
  | const (v : Json)
  | enum (vs : List Json)
  | pattern (r : Re)
  | minLength (n : Nat)
  | maxLength (n : Nat)
  | uniqueStrings
  | minimum (n : Int)
  | required (keys : List String)
  /-- `properties`, and `additionalProperties` when `extra` is given. -/
  | object (props : List (String × Shape)) (extra : Option Shape)
  | prefixItems (items : List Shape)
  | items (s : Shape)
  | minItems (n : Nat)
  | maxItems (n : Nat)
  | contains (s : Shape)
  | anyOf (ss : List Shape)
  | allOf (ss : List Shape)
  | not (s : Shape)
  /-- `if`/`then`/`else`; a `bool true` branch is left out. -/
  | ite (c t e : Shape)
  /-- `$ref`: `file.json#/pointer`, or `#/pointer` in its own file. -/
  | ref (target : String)
  | tagged (table : List (String × List Shape))
  | fuel (counter : String) (limit : Nat)
  | echo (pointer : String)
  | equals (pointer : String)
  | length (pointer : String)
  | count (pointer : String)
  /-- Every object's `field` in the response array is a request ID selected by `target`. -/
  | references (array field target : String)
  /-- Every selected claim has the name, AST and optional label of a request graph node. -/
  | claimNodes (sources : List String)
  /-- The replay count respects CertificateWire.limit, including its default and cap. -/
  | maxSteps
  /-- A certificate's Background count is at most what the request could generate (`backgroundBound`). -/
  | backgroundBound
  /-- A readings plan's indices, names and budget are bounded by its request. -/
  | readingPlan
  | index
  | digest
  | zip (pointer : String) (s : Shape)
  | zipOrEmpty (pointer : String) (s : Shape)
  | onCase (s : Shape)
  | select (choices : List (Shape × Shape))
  | countWhere (array : String) (where_ : Shape) (equals : String)
  | presenceCount (value equals : String)
  | rows (s : Shape)
  | row
  | node (comment : Option String) (keywords : List Shape)
  /-- Rendered as `s`; the Lean function `decide` must agree with `s` on every value. -/
  | lean (name : String) (s : Shape) (decide : Json → Bool)
  /-- Rendered and checked as `s`: a value the runner copies from the request (`why` says which),
  so its fields are the request's, not an encoder's; the encoder theorems
  (`ResponseShape.Encoders`) leave it to the client's validation (`ResponseShape.Skeleton`). -/
  | copied (why : String) (s : Shape)
  /-- The environment is assembled from a decoded source and generated predicate entries.
  The response checker uses `s`; the producer skeleton extracts the predicate-entry shape
  and ties the field to the corresponding prime-environment encoder. -/
  | encodedEnvironment (s : Shape)
  deriving Inhabited

/-- An entry of a file's `$defs`: a schema, or a group of named schemas (`kind/admission`). -/
inductive Def where
  | schema (s : Shape)
  | group (comment : Option String) (entries : List (String × Shape))
  deriving Inhabited

/-- A schema file: its top-level schemas (`row`, `response`, `handshake`) and `$defs`. -/
structure File where
  name : String
  comment : Option String
  top : List (String × Shape)
  defs : List (String × Def)
  deriving Inhabited

/-! ### Short forms used by the schema modules -/

def str : Shape := .type ["string"]
def obj : Shape := .type ["object"]
def arr : Shape := .type ["array"]
def n (keywords : List Shape) : Shape := .node none keywords
def c (comment : String) (keywords : List Shape) : Shape := .node (some comment) keywords
def ref (target : String) : Shape := .ref target
def props (ps : List (String × Shape)) : Shape := .object ps none
def closed (ps : List (String × Shape)) : Shape := .object ps (some (.bool false))
def strs (vs : List String) : List Json := vs.map Json.str
def enumS (vs : List String) : Shape := .enum (strs vs)
def constS (v : String) : Shape := .const (.str v)
/-- `s`, decided beside it by the Lean function `f` (a runner's decoder or dispatch test). -/
def decidedBy (name : String) (f : Json → Bool) (s : Shape) : Shape := .lean name s f
/-- `s`, a value copied from the request (`Shape.copied`). -/
def copied (why : String) (s : Shape) : Shape := .copied why s
def encodedEnvironment (s : Shape) : Shape := .encodedEnvironment s

/-- A request case whose `kind` is `k`. -/
def kindIs (k : String) : Shape := n [obj, .required ["kind"], props [("kind", constS k)]]

/-! ## Rendering -/

/-- The members of an object, in key order (none for another value). -/
def members (j : Json) : Array (String × Json) :=
  match j with
  | .obj kvs => kvs.foldl (fun acc k v => acc.push (k, v)) #[]
  | _ => #[]

def pointerString (p : List String) : String :=
  String.join (p.map fun t => "/" ++ (t.replace "~" "~0").replace "/" "~1")

/-- The JSON of a shape in `file`; `fuel` bounds the nesting (an error past it). -/
def render (file : String) : Nat → Shape → Except String Json
  | 0, _ => throw "shape nesting exceeds the renderer's bound"
  | fuel + 1, s => do
    let go := render file fuel
    let goList (ss : List Shape) : Except String Json := do pure (.arr (← ss.mapM go).toArray)
    match s with
    | .bool b => pure (.bool b)
    | .type [t] => pure (Json.mkObj [("type", .str t)])
    | .type ts => pure (Json.mkObj [("type", .arr (ts.map Json.str).toArray)])
    | .const v => pure (Json.mkObj [("const", v)])
    | .enum vs => pure (Json.mkObj [("enum", .arr vs.toArray)])
    | .pattern r => pure (Json.mkObj [("pattern", .str (r.render 0))])
    | .minLength k => pure (Json.mkObj [("minLength", toJson k)])
    | .maxLength k => pure (Json.mkObj [("maxLength", toJson k)])
    | .uniqueStrings => pure (Json.mkObj [("x-unique-strings", .bool true)])
    | .minimum k => pure (Json.mkObj [("minimum", toJson k)])
    | .required ks => pure (Json.mkObj [("required", toJson ks)])
    | .object ps extra => do
      let members ← ps.mapM fun (k, v) => do pure (k, ← go v)
      let out := if ps.isEmpty then [] else [("properties", Json.mkObj members)]
      match extra with
      | none => pure (Json.mkObj out)
      | some e => pure (Json.mkObj (out ++ [("additionalProperties", ← go e)]))
    | .prefixItems ss => pure (Json.mkObj [("prefixItems", ← goList ss)])
    | .items x => pure (Json.mkObj [("items", ← go x)])
    | .minItems k => pure (Json.mkObj [("minItems", toJson k)])
    | .maxItems k => pure (Json.mkObj [("maxItems", toJson k)])
    | .contains x => pure (Json.mkObj [("contains", ← go x)])
    | .anyOf ss => pure (Json.mkObj [("anyOf", ← goList ss)])
    | .allOf ss => pure (Json.mkObj [("allOf", ← goList ss)])
    | .not x => pure (Json.mkObj [("not", ← go x)])
    | .ite c t e => do
      let branch (k : String) : Shape → Except String (List (String × Json))
        | .bool true => pure []
        | b => do pure [(k, ← go b)]
      pure (Json.mkObj ([("if", ← go c)] ++ (← branch "then" t) ++ (← branch "else" e)))
    | .ref target =>
      let here := if target.startsWith (file ++ "#") then (target.drop file.length) else target
      pure (Json.mkObj [("$ref", .str here)])
    | .tagged table => do
      let rows ← table.mapM fun (tag, slots) => do pure (tag, ← goList slots)
      pure (Json.mkObj [("x-tagged", Json.mkObj rows)])
    | .fuel counter limit =>
      pure (Json.mkObj [("x-fuel", Json.mkObj [("counter", .str counter), ("limit", toJson limit)])])
    | .echo p => pure (Json.mkObj [("x-echo", .str p)])
    | .equals p => pure (Json.mkObj [("x-equals", .str p)])
    | .length p => pure (Json.mkObj [("x-length", .str p)])
    | .count p => pure (Json.mkObj [("x-count", .str p)])
    | .references a f p => pure (Json.mkObj [("x-references", Json.mkObj [
        ("array", .str a), ("field", .str f), ("in", .str p)])])
    | .claimNodes ps => pure (Json.mkObj [("x-claim-nodes", toJson ps)])
    | .maxSteps => pure (Json.mkObj [("x-max-steps", Json.mkObj [
        ("default", toJson VE.CertificateWire.maxSteps), ("cap", toJson VE.CertificateWire.caseCap)])])
    | .backgroundBound => pure (Json.mkObj [("x-background-bound", .bool true)])
    | .readingPlan => pure (Json.mkObj [("x-reading-plan", .bool true)])
    | .index => pure (Json.mkObj [("x-index", .bool true)])
    | .digest => pure (Json.mkObj [("x-digest", .bool true)])
    | .zip p x => pure (Json.mkObj [("x-zip", Json.mkObj [("of", .str p), ("items", ← go x)])])
    | .zipOrEmpty p x => pure (Json.mkObj [("x-zip-or-empty", Json.mkObj [("of", .str p), ("items", ← go x)])])
    | .onCase x => pure (Json.mkObj [("x-case", ← go x)])
    | .select cs => do
      let entries ← cs.mapM fun (w, t) => do pure (Json.mkObj [("when", ← go w), ("then", ← go t)])
      pure (Json.mkObj [("x-select", .arr entries.toArray)])
    | .countWhere a w e =>
      pure (Json.mkObj [("x-count-where", Json.mkObj [("array", .str a), ("where", ← go w), ("equals", .str e)])])
    | .presenceCount v e =>
      pure (Json.mkObj [("x-count-presence", Json.mkObj [("value", .str v), ("equals", .str e)])])
    | .rows x => pure (Json.mkObj [("x-rows", ← go x)])
    | .row => pure (Json.mkObj [("x-row", .bool true)])
    | .lean _ x _ => go x
    | .copied _ x => go x
    | .encodedEnvironment x => go x
    | .node comment keywords => do
      let mut out : List (String × Json) := comment.toList.map fun c => ("$comment", Json.str c)
      for k in keywords do
        match ← go k with
        | j@(.obj _) =>
          for (key, value) in members j do
            if out.any (·.1 == key) then throw s!"keyword {key} twice in one schema object"
            out := out ++ [(key, value)]
        | _ => throw "a boolean schema inside a schema object"
      if keywords.any (fun k => match k with | .items _ => true | _ => false) &&
          keywords.any (fun k => match k with | .prefixItems _ => true | _ => false) then
        throw "items beside prefixItems"
      pure (Json.mkObj out)

/-- The bound of the renderer's and the checker's nesting: far beyond any shape or value. -/
def depth : Nat := 1000000

def File.render (f : File) : Except String Json := do
  let top ← f.top.mapM fun (k, s) => do pure (k, ← ResponseShape.render f.name depth s)
  let defs ← f.defs.mapM fun (k, d) => do
    match d with
    | .schema s => pure (k, ← ResponseShape.render f.name depth s)
    | .group comment entries => do
      let rows ← entries.mapM fun (e, s) => do pure (e, ← ResponseShape.render f.name depth s)
      pure (k, Json.mkObj (comment.toList.map (fun c => ("$comment", Json.str c)) ++ rows))
  pure (Json.mkObj ([("$id", .str f.name)] ++ f.comment.toList.map (fun c => ("$comment", Json.str c)) ++ top ++
    (if defs.isEmpty then [] else [("$defs", Json.mkObj defs)])))

/-! ## Checking -/

/-- `invalid`: the value is not valid. `broken`: the shape and a Lean function at a `lean`
node disagree, or the shape cannot be checked; no alternative, negation or condition hides it. -/
inductive Fault where
  | invalid (message : String)
  | broken (message : String)

abbrev Result := Except Fault Unit

def fail (message : String) : Result := throw (.invalid message)

/-- The request data a value is checked against (the client's `Context`). -/
structure Ctx where
  value : Json
  index : Option Nat := none
  digest : Option Json := none
  row : Option Shape := none
  /-- The `lean` nodes being checked: a grammar's recursion into its own node is the shape alone,
  since the function already decided the whole value. -/
  inside : List String := []

/-- The JSON type of a value as the client names it: an integer has no fraction digits. -/
def kind : Json → String
  | .null => "null"
  | .bool _ => "boolean"
  | .num x => if x.exponent == 0 then "integer" else "number"
  | .str _ => "string"
  | .arr _ => "array"
  | .obj _ => "object"

/-- `a / 10^e` as a pair compared by cross-multiplication. -/
def numLe (a : JsonNumber) (b : JsonNumber) : Bool :=
  a.mantissa * (10 : Int) ^ b.exponent ≤ b.mantissa * (10 : Int) ^ a.exponent

def numEq (a b : JsonNumber) : Bool := numLe a b && numLe b a

/-- JSON equality without bool/number coercion (the client's `same_json`). -/
def same : Nat → Json → Json → Bool
  | 0, _, _ => false
  | fuel + 1, a, b => match a, b with
    | .null, .null => true
    | .bool x, .bool y => x == y
    | .num x, .num y => kind a == kind b && numEq x y
    | .str x, .str y => x == y
    | .arr xs, .arr ys => xs.size == ys.size && (xs.toList.zip ys.toList).all fun (x, y) => same fuel x y
    | .obj _, .obj _ =>
      let xs := members a
      let ys := members b
      xs.size == ys.size && (xs.toList.zip ys.toList).all fun ((k, x), (l, y)) => k == l && same fuel x y
    | _, _ => false

def sameJson (a b : Json) : Bool := same depth a b

def claimFields (j : Json) : List (Option Json) :=
  ["name", "ast", "label"].map fun k => (j.getObjVal? k).toOption

/-- The most Background premises a certificate case could generate, a relation to the request
only (arch decision D1: the count itself is Lean's, never predicted): per predicate declaration
at most two flags, one definition and one norm pair; one premise per pair of constants; one
per supplied soft premise. -/
def backgroundBound (case : Json) : Option Nat := do
  let vocab ← ((case.getObjValD "environment").getObjVal? "vocabulary").toOption
  let predicates ← (vocab.getObjVal? "predicates").toOption
  let constants ← (vocab.getObjVal? "constants").toOption
  if kind predicates != "object" || kind constants != "object" then none else pure ()
  let c := (members constants).size
  let soft := match case.getObjValD "soft_premises" with
    | .arr ps => ps.size
    | _ => 0
  pure (4 * (members predicates).size + c * (c - 1) / 2 + soft)

/-- Binding only: Lean's readings planner decides which indices are compatible;
this relation ensures that every reported choice, count, coupling and unit
refers to the submitted sets. -/
def readingPlanBound (request answer : Json) : Bool := Id.run do
  let some sets := (request.getObjValD "set_meta").getArr?.toOption | return false
  let some couplings := (request.getObjValD "couplings").getArr?.toOption | return false
  let some limit := (request.getObjValD "limit").getNat?.toOption | return false
  let mut sizes : List Nat := []
  let mut units : List Json := []
  for s in sets do
    let some rs := (s.getObjValD "readings").getArr?.toOption | return false
    let some sid := (s.getObjValD "id").getStr?.toOption | return false
    let unit := (s.getObjValD "unit").getStr?.toOption.getD sid
    sizes := sizes ++ [rs.size]
    units := units ++ [.str unit]
  let mut labels : List Json := []
  for c in couplings do
    let some cid := (c.getObjValD "id").getStr?.toOption | return false
    labels := labels ++ [.str ("coupling:" ++ cid)]
  if answer.getObjValD "route" == .str "enumerate" then
    let some choices := (answer.getObjValD "choices").getArr?.toOption | return false
    if choices.isEmpty || choices.size > limit then return false
    let mut seen : List (List Nat) := []
    for choice in choices do
      let some items := choice.getArr?.toOption | return false
      if items.size != sizes.length then return false
      let some is := items.toList.mapM (·.getNat?.toOption) | return false
      if seen.contains is || !(is.zip sizes).all (fun (i, n) => i < n) then return false
      seen := is :: seen
    return answer.getObjValD "conditional_on" == toJson labels
  else if answer.getObjValD "route" == .str "UNKNOWN" then
    let some budget := ((answer.getObjValD "budget").getObjValD "max_choices").getNat?.toOption |
      return false
    let some count := (answer.getObjValD "choice_count").getNat?.toOption | return false
    let some named := (answer.getObjValD "units").getArr?.toOption | return false
    return budget == limit && limit < count && count ≤ sizes.foldl (· * ·) 1 &&
      named.toList.all units.contains
  else return false

def tokens (pointer : String) : List String :=
  if pointer.isEmpty then [] else
    (pointer.splitOn "/").drop 1 |>.map fun t => (t.replace "~1" "/").replace "~0" "~"

/-- The value at a pointer; `*` maps the rest over an array (every element must resolve). -/
def resolveAt : Nat → Json → List String → Option Json
  | 0, _, _ => none
  | _, j, [] => some j
  | fuel + 1, j, "*" :: rest => match j with
    | .arr xs => (xs.toList.mapM fun x => resolveAt fuel x rest).map fun ys => .arr ys.toArray
    | _ => none
  | fuel + 1, j, t :: rest => match j with
    | .obj _ => (j.getObjVal? t).toOption.bind fun v => resolveAt fuel v rest
    | _ => none

def resolve (j : Json) (pointer : String) : Option Json := resolveAt depth j (tokens pointer)

def short (j : Json) : String :=
  let s := j.compress
  if s.length ≤ 60 then s else (s.take 57) ++ "..."

/-- The schema a `$ref` names, among `files`. -/
def lookup (files : List File) (target : String) : Option Shape := do
  let (file, pointer) := match target.splitOn "#" with
    | [f, p] => (f, p)
    | _ => ("", target)
  let f ← files.find? (·.name == file)
  match tokens pointer with
  | [k] => (f.top.find? (·.1 == k)).map (·.2)
  | ["$defs", k] => match (f.defs.find? (·.1 == k)).map (·.2) with
    | some (Def.schema s) => some s
    | _ => none
  | ["$defs", k, e] => match (f.defs.find? (·.1 == k)).map (·.2) with
    | some (Def.group _ entries) => (entries.find? (·.1 == e)).map (·.2)
    | _ => none
  | _ => none

/-- Qualify every local `$ref` with its file's name. -/
def qualify (file : String) : Nat → Shape → Shape
  | 0, s => s
  | fuel + 1, s =>
    let q := qualify file fuel
    match s with
    | .ref t => .ref (if t.startsWith "#" then file ++ t else t)
    | .object ps extra => .object (ps.map fun (k, v) => (k, q v)) (extra.map q)
    | .prefixItems ss => .prefixItems (ss.map q)
    | .items x => .items (q x)
    | .contains x => .contains (q x)
    | .anyOf ss => .anyOf (ss.map q)
    | .allOf ss => .allOf (ss.map q)
    | .not x => .not (q x)
    | .ite a b e => .ite (q a) (q b) (q e)
    | .tagged table => .tagged (table.map fun (t, slots) => (t, slots.map q))
    | .zip p x => .zip p (q x)
    | .zipOrEmpty p x => .zipOrEmpty p (q x)
    | .onCase x => .onCase (q x)
    | .select cs => .select (cs.map fun (w, t) => (q w, q t))
    | .countWhere a w e => .countWhere a (q w) e
    | .rows x => .rows (q x)
    | .node comment keywords => .node comment (keywords.map q)
    | .lean name x f => .lean name (q x) f
    | .copied why x => .copied why (q x)
    | .encodedEnvironment x => .encodedEnvironment (q x)
    | other => other

def File.qualified (f : File) : File :=
  { f with
    top := f.top.map fun (k, s) => (k, qualify f.name depth s)
    defs := f.defs.map fun (k, d) => (k, match d with
      | .schema s => .schema (qualify f.name depth s)
      | .group comment entries => .group comment (entries.map fun (e, s) => (e, qualify f.name depth s))) }

abbrev Counters := List (String × Nat)

def bump (counters : Counters) (counter : String) : Nat × Counters :=
  let used := ((counters.find? (·.1 == counter)).map (·.2)).getD 0 + 1
  (used, (counter, used) :: counters.filter (·.1 != counter))

/-- Whether `r` passed; a `broken` fault propagates. -/
def passed (r : Result) : Except Fault Bool :=
  match r with
  | .ok () => pure true
  | .error (.invalid _) => pure false
  | .error (.broken m) => throw (.broken m)

def within (k : String) (r : Result) : Result := match r with
  | .error (.invalid m) => throw (.invalid s!"{k}: {m}")
  | other => other

def isItems : Shape → Bool
  | .items _ => true
  | _ => false

/-- Check `value` against shape `s` with `files` for references. -/
def check (files : List File) : Nat → Shape → Ctx → Counters → Json → Result
  | 0, _, _, _, _ => throw (.broken "shape nesting exceeds the checker's bound")
  | fuel + 1, s, ctx, counters, value =>
    let go := check files fuel
    let ok? (x : Shape) (ctx : Ctx) (counters : Counters) (v : Json) : Except Fault Bool :=
      passed (go x ctx counters v)
    match s with
    | .bool true => pure ()
    | .bool false => fail "no value is valid here"
    | .type ts => if ts.contains (kind value) then pure () else fail s!"expected {"/".intercalate ts}"
    | .const v => if sameJson value v then pure () else fail s!"{short value} is not {short v}"
    | .enum vs => if vs.any (sameJson value) then pure () else fail s!"{short value} is not one of the values"
    | .pattern r => match value with
      | .str x => if r.matches x then pure () else fail s!"{short value} does not match {r.render 0}"
      | _ => pure ()
    | .minLength k => match value with | .str x => if x.length < k then fail s!"string shorter than {k}" else pure () | _ => pure ()
    | .maxLength k => match value with
      | .str x => if x.length > k then fail s!"string longer than {k}" else pure ()
      | _ => pure ()
    | .uniqueStrings => match value with | .arr xs => do let names ← xs.toList.mapM (fun x => match x with | .str s => pure s | _ => throw (.invalid "expected an array of strings")); if names.Nodup then pure () else fail "strings are not distinct" | _ => fail "expected an array of strings"
    | .minimum k => match value with
      | .num x => if numLe ⟨k, 0⟩ x then pure () else fail s!"{short value} is below {k}"
      | _ => pure ()
    | .required ks => match value with
      | .obj _ => match ks.find? (fun k => !(value.getObjVal? k).toBool) with
        | some k => fail s!"missing field {k}"
        | none => pure ()
      | _ => pure ()
    | .object ps extra => match value with
      | .obj _ => do
        for (k, v) in members value do
          match ps.find? (·.1 == k) with
          | some (_, x) => within k (go x ctx counters v)
          | none => match extra with
            | none => pure ()
            | some (.bool false) => fail s!"unexpected field {k}"
            | some x => within k (go x ctx counters v)
      | _ => pure ()
    | .prefixItems ss => match value with
      | .arr xs => do
        for (x, i) in (xs.toList.zip ss).zipIdx do within s!"[{i}]" (go x.2 ctx counters x.1)
      | _ => pure ()
    | .items x => match value with
      | .arr xs => do for (v, i) in xs.toList.zipIdx do within s!"[{i}]" (go x ctx counters v)
      | _ => pure ()
    | .minItems k => match value with
      | .arr xs => if xs.size < k then fail s!"fewer than {k} elements" else pure ()
      | _ => pure ()
    | .maxItems k => match value with
      | .arr xs => if xs.size > k then fail s!"more than {k} elements" else pure ()
      | _ => pure ()
    | .contains x => match value with
      | .arr xs => do
        for v in xs do
          if ← ok? x ctx counters v then return ()
        fail "no element is valid"
      | _ => pure ()
    | .anyOf ss => do
      let mut reasons := #[]
      for x in ss do
        match go x ctx counters value with
        | .ok () => return ()
        | .error (.invalid m) => reasons := reasons.push m
        | .error (.broken m) => throw (.broken m)
      fail s!"no alternative is valid ({"; ".intercalate reasons.toList})"
    | .allOf ss => do for x in ss do go x ctx counters value
    | .not x => do if ← ok? x ctx counters value then fail "a forbidden form is present"
    | .ite c t e => do go (if ← ok? c ctx counters value then t else e) ctx counters value
    | .ref target => match lookup files target with
      | some x => go x ctx counters value
      | none => throw (.broken s!"unresolved $ref {target}")
    | .tagged table => match value with
      | .arr xs => match xs.toList with
        | .str tag :: args => match table.find? (·.1 == tag) with
          | some (_, slots) =>
            if args.length != slots.length then fail s!"{tag} takes {slots.length} arguments" else do
              for (v, x) in args.zip slots do go x ctx counters v
          | none => fail s!"unknown tag {tag}"
        | _ => fail s!"expected a tagged array, got {short value}"
      | _ => fail s!"expected a tagged array, got {short value}"
    | .fuel counter limit =>
      if (bump counters counter).1 > limit then fail s!"nesting exceeds the Lean decoder fuel {limit}" else pure ()
    | .echo p => if sameJson value ((resolve ctx.value p).getD .null) then pure ()
        else fail s!"does not echo the request's {p}"
    | .equals p => match resolve ctx.value p with
      | some v => if sameJson value v then pure () else fail s!"does not equal the request's {p}"
      | none => fail s!"does not equal the request's {p}"
    | .length p => match resolve ctx.value p, value with
      | some (.arr ys), .arr xs => if xs.size == ys.size then pure () else fail s!"length differs from the request's {p}"
      | _, _ => fail s!"length differs from the request's {p}"
    | .count p => match resolve ctx.value p, value with
      | some (.arr ys), .num x => if kind value == "integer" && numEq x ⟨(ys.size : Int), 0⟩ then pure ()
          else fail s!"is not the number of the request's {p}"
      | _, _ => fail s!"is not the number of the request's {p}"
    | .references a f p => match resolve value a, resolve ctx.value p with
      | some (.arr xs), some (.arr ys) =>
        if xs.all (fun x => match x.getObjVal? f with
          | .ok v => kind v == "string" && ys.any (sameJson v)
          | .error _ => false) then pure ()
        else fail s!"{a} contains an unbound {f} outside the request's {p}"
      | _, _ => fail s!"{a} contains an unbound {f} outside the request's {p}"
    | .claimNodes sources =>
      for source in sources do
        match resolve value source, resolve ctx.value "/document/graph/nodes" with
        | some claims, some (.arr nodes) =>
          let claims := match claims with
            | .arr xs => xs.toList
            | .obj _ => [claims]
            | _ => []
          if (kind (resolve value source |>.getD .null) == "array" || !claims.isEmpty) && claims.all (fun c =>
              kind c == "object" && nodes.any (fun n => kind n == "object" &&
                claimFields c == claimFields n)) then pure ()
          else fail s!"{source} contains a claim outside the request graph"
        | _, _ => fail s!"{source} contains a claim outside the request graph"
    | .maxSteps => match value, VE.CertificateWire.limit ctx.value with
      | .num n, .ok limit =>
        if kind value == "integer" && numLe n ⟨(limit : Int), 0⟩ then pure ()
        else fail "steps exceed the request's max_steps"
      | _, _ => fail "steps exceed the request's max_steps"
    | .backgroundBound => match value, backgroundBound ctx.value with
      | .num n, some limit =>
        if kind value == "integer" && numLe n ⟨(limit : Int), 0⟩ then pure ()
        else fail "background exceeds what the request vocabulary generates"
      | _, _ => fail "background exceeds what the request vocabulary generates"
    | .readingPlan =>
      if readingPlanBound ctx.value value then pure ()
      else fail "readings plan names choices outside the request"
    | .index => match value, ctx.index with
      | .num x, some i => if kind value == "integer" && numEq x ⟨(i : Int), 0⟩ then pure () else fail "is not the result's position"
      | _, _ => fail "is not the result's position"
    | .digest => match value, ctx.digest with
      | .str x, some (.str d) => if x == d then pure () else fail "is not the digest of the result's case"
      | _, _ => fail "is not the digest of the result's case"
    | .zip p x => match resolve ctx.value p, value with
      | some (.arr contexts), .arr xs =>
        if xs.size != contexts.size then fail s!"not one element per element of the request's {p}" else do
          for ((v, cx), i) in (xs.toList.zip contexts.toList).zipIdx do
            within s!"[{i}]" (go x { value := cx, index := some i } counters v)
      | _, _ => fail s!"not one element per element of the request's {p}"
    | .zipOrEmpty p x => match resolve ctx.value p, value with
      | none, .arr xs => if xs.isEmpty then pure () else fail s!"not one element per element of the request's {p}"
      | some (.arr contexts), .arr xs =>
        if xs.size != contexts.size then fail s!"not one element per element of the request's {p}" else do
          for ((v, cx), i) in (xs.toList.zip contexts.toList).zipIdx do
            within s!"[{i}]" (go x { value := cx, index := some i } counters v)
      | _, _ => fail s!"not one element per element of the request's {p}"
    | .onCase x => go x ctx [] ctx.value
    | .select cs => do
      for (w, t) in cs do
        if ← ok? w ctx [] ctx.value then return ← go t ctx counters value
      fail "no result is possible for this request"
    | .countWhere a w e => match resolve value a, resolve value e with
      | some (.arr xs), some (.num x) => do
        let mut k := 0
        for v in xs do
          if ← ok? w ctx counters v then k := k + 1
        if kind (.num x) == "integer" && numEq x ⟨(k : Int), 0⟩ then pure () else fail s!"{e} does not count {a}"
      | _, _ => fail s!"{e} does not count {a}"
    | .presenceCount v e => match resolve value v, resolve value e with
      | some item, some (.num n) =>
        let expected : Int := if item == .null then 0 else 1
        if kind (.num n) == "integer" && numEq n ⟨expected, 0⟩ then pure ()
        else fail s!"{e} does not count the presence of {v}"
      | _, _ => fail s!"{e} does not count the presence of {v}"
    | .rows x => match resolve ctx.value "/cases", resolve ctx.value "/digests", value with
      | some (.arr cases), some (.arr digests), .arr results =>
        if results.size != cases.size || digests.size != cases.size then fail "one result per case" else do
          for (((r, case), d), i) in ((results.toList.zip cases.toList).zip digests.toList).zipIdx do
            match go x { value := case, index := some i, digest := some d, row := ctx.row } [] r with
            | .error (.invalid m) => throw (.invalid s!"result {i}: {m}")
            | other => other
      | _, _, _ => fail "one result per case"
    | .row => match ctx.row with
      | some x => go x { value := ctx.value, index := ctx.index } [] value
      | none => throw (.broken "x-row outside x-rows")
    | .copied _ x => go x ctx counters value
    | .encodedEnvironment x => go x ctx counters value
    | .lean name x decide => do
      if ctx.inside.contains name then return ← go x ctx counters value
      let ctx := { ctx with inside := name :: ctx.inside }
      let schema ← ok? x ctx counters value
      if schema != decide value then
        throw (.broken s!"the schema and {name} disagree on {short value}")
      unless schema do go x ctx counters value
    | .node _ keywords => do
      let fuelled := keywords.findSome? fun k => match k with
        | .fuel counter limit => some (counter, limit)
        | _ => none
      let counters ← match fuelled with
        | some (counter, limit) =>
          let (used, next) := bump counters counter
          if used > limit then throw (Fault.invalid s!"nesting exceeds the Lean decoder fuel {limit}")
          else pure next
        | none => pure counters
      let skip := (keywords.findSome? fun k => match k with
        | .prefixItems ss => some ss.length
        | _ => none).getD 0
      for k in keywords do
        match k, value with
        | .fuel _ _, _ => pure ()
        | .items x, .arr xs => do
          for (v, i) in (xs.toList.drop skip).zipIdx do within s!"[{i + skip}]" (go x ctx counters v)
        | _, _ => go k ctx counters value

/-- `Check` of a value in `files`, with the faults as messages (`broken:` marks a disagreement). -/
def decide (files : List File) (s : Shape) (ctx : Ctx) (value : Json) : Except String Unit :=
  match check files depth s ctx [] value with
  | .ok () => pure ()
  | .error (.invalid m) => throw m
  | .error (.broken m) => throw s!"broken: {m}"

/-! ## Pins -/

private def tok : Re := .rep (.cls [('A', 'Z'), ('a', 'z'), ('0', '9'), ('_', '_'), ('.', '.'), ('-', '-')]) 1 64
#guard tok.matches "a.b-c_d" && !tok.matches "" && !tok.matches "a b" && tok.matches ("".pushn 'x' 64)
#guard !tok.matches ("".pushn 'x' 65)
#guard (Re.prefixes ["soft:", "rights:"]).matches "rights:x\ny" && !(Re.prefixes ["soft:"]).matches "sof"
#guard (Re.optional (.seq (.lit "/") (.star .any))).matches "" && !(Re.optional (.lit "/")).matches "x"
#guard tok.render 0 == "[A-Za-z0-9_.\\-]{1,64}" && (Re.prefixes ["a(", "b"]).render 0 == "(a\\(|b).*"

private def disagreeing : Shape := .lean "never" (.type ["string"]) (fun _ => false)
private def brokenOn (s : Shape) (v : Json) (case : Json := .null) : Bool :=
  match check [] depth s {value := case} [] v with
  | .error (.broken _) => true
  | _ => false
-- A disagreement is reported, and no alternative, negation or condition hides it.
#guard brokenOn disagreeing (.str "x") && !brokenOn disagreeing (.num 1)
#guard brokenOn (.anyOf [disagreeing, .bool true]) (.str "x")
#guard brokenOn (.not disagreeing) (.str "x")
#guard brokenOn (.ite disagreeing (.bool true) (.bool true)) (.str "x")
#guard brokenOn (.select [(disagreeing, .bool true), (.bool true, .bool true)]) .null (.str "case")
#guard brokenOn (.onCase disagreeing) .null (.str "case")

end ResponseShape
