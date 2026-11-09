import VE.RightClauses.Relation
import VE.Rights.Wire
import VE.Compose.Dispatch

/-! The wire of `right-clauses@0` (docs/spec/right-clauses.md 3, 4.1, 7, 8.5) and its `clauses-elaborate` case.

A document under the profile is the rights route's: an array of rights units (rights 3.2). Each line object of a
`right` or `right_lines` unit carries three more keys: `elided` (mandatory), `clauses` and `relation`
(`headKeys`). Each unit may carry its source `span` (`[a, b)`, UTF-8 bytes), which the clause and elided spans of its
lines must lie in (1.1). This item reads the span from that key; a unit without it has the empty span `[0, 0)`, so a
non-empty clause or elided span on it is refused (`ClauseSpan`). `decodeClauseDoc` decodes the units in document order.
For each line object it runs the frozen rights decoder `decodeLine` on the object without the three keys (this gives
`<n>`), then reads `elided`, `clauses` and `relation` with the texts of section 7. Then it runs rights' own `addUnit`
on the unit without its span and its lines' three keys. `elaborateJson` writes the plained document: the keys and spans
dropped and each structured line's norm guard replaced by its plain guard (`plainGuard`). A line with no clause and no
relation keeps its norm as written. The case itself is `VE.RightClauses.Run`. No import of `VE.Readings` (spec 0). -/
namespace VE.RightClauses
open Lean
open VE.Rights.Wire (decodeRightsEnvironment decodeLine addUnit Units)
open VE.SoftNorms.Wire (SoftEnvironment enc)

/-- The three keys a line object gains under the profile (3). -/
def headKeys : List String := ["elided", "clauses", "relation"]

/-! ## The JSON the head reads and writes -/

/-- An object without its members `ks`, rebuilt; any other value unchanged. -/
def dropKeys (ks : List String) : Json → Json
  | .obj kvs => Json.mkObj (kvs.toList.filter (fun kv => !ks.contains kv.1))
  | j => j
/-- The members of an object, as written (none for any other value). -/
def members : Json → List (String × Json)
  | .obj kvs => kvs.toList
  | _ => []
/-- An object rebuilt from its members; any other value unchanged (a parsed object is its own rebuilding). -/
def rebuild : Json → Json
  | .obj kvs => Json.mkObj kvs.toList
  | j => j
/-- An object with member `k`'s value through `f`: its keys, their order and its other values unchanged (no member is
    added). Any other value unchanged. -/
def mapMember (k : String) (f : Json → Json) : Json → Json
  | .obj kvs => .obj (kvs.map fun k' v => if k' == k then f v else v)
  | j => j
/-- An array through `f` element by element; any other value unchanged. -/
def mapArr (f : Json → Json) : Json → Json
  | .arr xs => .arr (xs.map f)
  | j => j
/-- A line object without the members `ks`, its `norm` and `liberty` rebuilt (the soft decoder reads a norm through
    its member list). -/
def lineWith (ks : List String) (l : Json) : Json :=
  mapMember "liberty" rebuild (mapMember "norm" rebuild (dropKeys ks l))
/-- A unit's line-bearing body (`right` or `right_lines`) with its key. -/
def unitBody (u : Json) : Option (String × Json) :=
  match u.getObjVal? "right", u.getObjVal? "right_lines" with
  | .ok b, _ => some ("right", b)
  | _, .ok b => some ("right_lines", b)
  | _, _ => none
/-- The right a body's lines belong to: a `right`'s `name`, a `right_lines` unit's `right`. -/
def bodyRight (key : String) (body : Json) : String :=
  ((body.getObjValD (if key == "right" then "name" else "right")).getStr?).toOption.getD ""
def bodyLines (body : Json) : List Json :=
  match body.getObjVal? "lines" with
  | .ok (.arr ls) => ls.toList
  | _ => []
/-- A unit without its `span`, each line object of its body through `f` (given the line's right). -/
def mapUnit (f : String → Json → Json) (u : Json) : Json :=
  let u := dropKeys ["span"] u
  match unitBody u with
  | some (k, b) => mapMember k (mapMember "lines" (mapArr (f (bodyRight k b)))) u
  | none => u
def mapDoc (f : String → Json → Json) : Json → Json
  | .arr us => .arr (us.map (mapUnit f))
  | j => j
/-- The units of a document (none if it is not an array). -/
def unitsOf : Json → List Json
  | .arr us => us.toList
  | _ => []

/-- 8.5: removes the mandatory `elided` key from every line object (and each unit's `span`, this wire's reading of
    the unit span). -/
def stripElided : Json → Json := mapDoc (fun _ => lineWith ["elided"])
/-- 8.5: no line object has `clauses` or `relation`. -/
def NoClauseKeys (document : Json) : Prop :=
  ∀ u ∈ unitsOf document, ∀ b ∈ (unitBody (dropKeys ["span"] u)).toList, ∀ l ∈ bodyLines b.2,
    ∀ kv ∈ members l, kv.1 ≠ "clauses" ∧ kv.1 ≠ "relation"
/-- 8.5: the document has no reading set (the rights decoder reads an array of units, never `reading_sets`). -/
def NoReadingSets (document : Json) : Prop := (document.getObjVal? "reading_sets").toOption = none
/-- 8.5: the environment without `right-clauses@0` in its profile list (`VE.Compose.withoutClauses`, which the
    environment mode reads it by too). -/
def stripProfile (environment : Json) : Json := VE.Compose.withoutClauses environment

/-! ## Decoding (4.1 step 2, 7) -/

/-- Two naturals `[a, b]`. -/
def decodeSpan : Json → Option (Nat × Nat)
  | .arr #[a, b] => match a.getNat?, b.getNat? with
    | .ok a, .ok b => some (a, b)
    | _, _ => none
  | _ => none
def decodeRole : Json → Option Role
  | .str "scope" => some .scope
  | .str "trigger" => some .trigger
  | .str "object" => some .object
  | _ => none
/-- The member names of an object are the required `ks` and some of the optional `os`. -/
def hasKeys (j : Json) (ks : List String) (os : List String := []) : Bool :=
  let names := (members j).map (·.1)
  (match j with | .obj _ => true | _ => false) && ks.all names.contains &&
    names.all (fun k => ks.contains k || os.contains k) && names.length == (names.eraseDups).length

def decodeClause (n : String) (ci : Json × Nat) : Except String Clause := do
  let (c, i) := ci
  let bad := s!"InvalidInput: invalid clause {i} of rule {n}"
  unless hasKeys c ["role", "span", "formula"] do throw bad
  let some role := decodeRole (c.getObjValD "role") | throw bad
  let some span := decodeSpan (c.getObjValD "span") | throw bad
  -- W1's decoder and budget; any other failure is a formula that is no base formula of the line (7)
  let formula ← match VE.Norms.Wire.decodeBudgeted (c.getObjValD "formula") with
    | .ok φ => pure φ
    | .error e => throw (if e.startsWith "ResourceLimit" then e else s!"InvalidInput: ill-typed clause {i} of rule {n}")
  pure ⟨role, formula, span⟩
def decodeRelation (n : String) (v : Json) : Except String Relation := do
  let bad := s!"InvalidInput: invalid relation of rule {n}"
  -- `total: null` is written by omission: the service's restricted JSON has no null (rights' `_wire`)
  unless hasKeys v ["predicate", "slots", "cites"] ["total"] do throw bad
  let .str pred := v.getObjValD "predicate" | throw bad
  let some slots := decodeSpan (v.getObjValD "slots") | throw bad
  let total ← match v.getObjValD "total" with
    | .null => pure none
    | t => match t.getNat? with
      | .ok k => pure (some k)
      | .error _ => throw bad
  let .ok cites := VE.Bridge.strings (v.getObjValD "cites") | throw bad
  pure ⟨pred, slots, total, cites⟩
def decodeElided (n : String) (l : Json) : Except String (List (Nat × Nat)) :=
  match l.getObjVal? "elided" with
  | .error _ => throw s!"InvalidInput: elided missing on rule {n}"
  | .ok (.arr xs) => xs.toList.mapM fun x => match decodeSpan x with
    | some s => pure s
    | none => throw s!"InvalidInput: invalid elided of rule {n}"
  | .ok _ => throw s!"InvalidInput: invalid elided of rule {n}"
def decodeClauses (n : String) (l : Json) : Except String (List Clause) :=
  match l.getObjVal? "clauses" with
  | .error _ => pure []
  | .ok (.arr cs) => if cs.isEmpty then throw s!"InvalidInput: invalid clauses of rule {n}"
    else cs.toList.zipIdx.mapM (decodeClause n)
  | .ok _ => throw s!"InvalidInput: invalid clauses of rule {n}"
def decodeRelationOpt (n : String) (l : Json) : Except String (Option Relation) :=
  match l.getObjVal? "relation" with
  | .error _ => pure none
  | .ok v => some <$> decodeRelation n v

/-- One line object of right `R` in a unit of span `span` (7): `decodeLine` on it without the three keys, then
    `elided`, `clauses` and `relation`. A line with no rule name gets none of the head's checks (rights refuses it). -/
def headLine (se : SoftEnvironment) (R : String) (span : Nat × Nat) (l : Json) :
    Except String (Option (String × String × CLine)) := do
  let S ← decodeLine se (lineWith headKeys l)
  match lineName S with
  | none => pure none
  | some n => do
    let elided ← decodeElided n l
    let clauses ← decodeClauses n l
    let relation ← decodeRelationOpt n l
    pure (some (R, n, ⟨S, clauses, relation, elided, span⟩))
def unitSpanOf (u : Json) : Except String (Nat × Nat) :=
  match u.getObjVal? "span" with
  | .error _ => pure (0, 0)
  | .ok v => match decodeSpan v with
    | some s => pure s
    | none => throw "InvalidInput: invalid unit span"
/-- The head's entries of one unit, in line order. -/
def headUnit (se : SoftEnvironment) (u : Json) : Except String (List (String × String × CLine)) := do
  let span ← unitSpanOf u
  match unitBody (dropKeys ["span"] u) with
  | some (k, b) => (bodyLines b).filterMapM (headLine se (bodyRight k b) span)
  | none => pure []
/-- One unit: the head's entries, then rights' `addUnit` on the unit without the head's keys. -/
def headStep (se : SoftEnvironment) (acc : List (String × String × CLine) × Units) (u : Json) :
    Except String (List (String × String × CLine) × Units) := do
  let ls ← headUnit se u
  let us ← addUnit se acc.2 (mapUnit (fun _ => lineWith headKeys) u)
  pure (acc.1 ++ ls, us)

/-- 8.5: the rights document as `decodeRightsSource` builds it (without its `WellFormedRights` check, which runs on
    `plain D`, 4.1 step 6) and the entries of every named line, in document order. No reading sets: `cands = []`. -/
def decodeClauseDoc (environment document : Json) : Except String ClauseDoc := do
  let re ← decodeRightsEnvironment (stripProfile environment)
  unless re.se.ne.rv.definitions.isEmpty do
    throw "UnsupportedProfile: rights route with definitions is not implemented"
  unless re.se.ne.rv.flags.isEmpty do
    throw "UnsupportedProfile: rights route with data flags is not implemented"
  let units ← match document with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: document must be an array"
  if units.length > 1024 then throw "ResourceLimit: units"
  let (lines, us) ← units.foldlM (headStep re.se) ([], {})
  pure ⟨⟨⟨re.se.ne.rv.environment, re.se.ne.rv.literals, re.se.soft, ⟨re.se.ne.regulated, [], us.outside⟩⟩,
    re.block, us.rs, us.limits, us.bars, us.cites, some us.order, us.sourceUnits.getD []⟩, lines, []⟩

/-! ## The plained document (8.5) -/

/-- The rule name a line object is written with: its norm's, else its liberty's. -/
def jsonLineName (l : Json) : Option String :=
  ((l.getObjValD "norm").getObjValD "name").getStr?.toOption <|>
    ((l.getObjValD "liberty").getObjValD "name").getStr?.toOption
/-- A line object of right `R` without the three keys; a structured line's norm guard is its plain guard. -/
def plainLineJson (D : ClauseDoc) (R : String) (l : Json) : Json :=
  let l := lineWith headKeys l
  match (jsonLineName l).bind (fun n => D.lines.find? (fun x => x.1 == R && x.2.1 == n)) with
  | some (_, _, L) =>
    match L.line.norm with
    | some N =>
      if L.clauses.isEmpty && L.relation.isNone then l
      else mapMember "norm" (mapMember "guard" (fun _ => enc (plainGuard (lineSorts D.doc.soft L.line).length N.guard L))) l
    | none => l
  | none => l
/-- 8.5: the document under rights@0: every line through `plainLineJson`, the three keys and unit spans dropped. -/
def elaborateJson (D : ClauseDoc) (document : Json) : Json := mapDoc (plainLineJson D) document

/-- The DRI's added hypothesis of `elaborate_plain` (reviews/dri-decisions-20261104-cmp-s3.md Q1 A1): every structured
    line's plain guard is within `VE.Limits.maxDepth` and `maxNodes` as the wire counts them, that is, W1's budgeted
    decoder reads its encoding back. -/
def PlainOnWire (D : ClauseDoc) : Prop :=
  ∀ x ∈ D.lines, ∀ N ∈ x.2.2.line.norm.toList,
    let G := plainGuard (lineSorts D.doc.soft x.2.2.line).length N.guard x.2.2
    ∃ c, VE.Norms.Wire.budgetFormula VE.Limits.maxDepth 0 (enc G) = .ok (G, c)

end VE.RightClauses
