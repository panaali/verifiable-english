import ResponseShape.Skeletons
import Lean.Elab.Command

/-! # Every enumeration of the response schemas, and the field skeleton that keeps it

A schema declares allowed values with `enum` or `const` (a one-value enum). `sites` lists every such
declaration of every file of `Schemas.files`, at the JSON pointer where the rendered schema
(`ve/backends/lean_service_schema/`) holds its keyword, with its role: the domain of a value
(`value`), a condition on another field or on the request (`condition`: under `if`, `not`,
`contains`, `x-case`, a selector's `when`, `x-count-where`), a value the runner copies from the
request (`copied`), or a slot of a tagged grammar (`grammar`). `tests/test_enum_domains.py` checks
this list against the rendered files, so a declaration this walk misses fails there.

`probes` lists every field (an object's property, an array's items, an object's other properties)
whose value resolves, through references and keyword groups, to a value-role declaration, and
`fieldSkel% i` is the skeleton extraction (`skeletonOf`) of probe `i`'s field, through the same
object, array and reference paths as a row's. The test proves that every declared value fits it,
and that `BOGUS` and every value another field of the same name allows do not (`Skel.admits`). -/

namespace ResponseShape.EnumSites
open Lean

/-- One `enum` or `const`: its file, the pointer of its keyword, its role where it is written, its
values, and its roles where the rows use it (`uses`: through every reference to its entry). -/
structure Site where
  file : String
  pointer : String
  role : String
  values : List Json
  uses : List String := []

instance : ToJson Site where
  toJson s := Json.mkObj [("file", .str s.file), ("pointer", .str s.pointer), ("role", .str s.role),
    ("values", .arr s.values.toArray), ("uses", toJson s.uses)]

def escape (t : String) : String := (t.replace "~" "~0").replace "/" "~1"

/-- The declarations under `s`, rendered at `p` in `file`, in the role `role` (a condition or copied
value keeps its role below it). -/
def sitesOf (file : String) : Nat → String → String → Shape → List Site
  | 0, _, _, _ => []
  | fuel + 1, p, role, s =>
    let go := sitesOf file fuel
    let cond := if role == "value" then "condition" else role
    let many (key : String) (ss : List Shape) : List Site :=
      (ss.zipIdx.map fun (x, i) => go s!"{p}/{key}/{i}" role x).flatten
    match s with
    | .const v => [⟨file, p ++ "/const", role, [v], []⟩]
    | .enum vs => [⟨file, p ++ "/enum", role, vs, []⟩]
    | .object ps extra =>
      (ps.map fun (k, v) => go s!"{p}/properties/{escape k}" role v).flatten ++
        (extra.map (go s!"{p}/additionalProperties" role)).getD []
    | .prefixItems ss => many "prefixItems" ss
    | .items x => go s!"{p}/items" role x
    | .contains x => go s!"{p}/contains" cond x
    | .anyOf ss => many "anyOf" ss
    | .allOf ss => many "allOf" ss
    | .not x => go s!"{p}/not" cond x
    | .ite c t e =>
      let branch (k : String) : Shape → List Site
        | .bool true => []
        | b => go s!"{p}/{k}" role b
      go s!"{p}/if" cond c ++ branch "then" t ++ branch "else" e
    | .tagged table =>
      (table.map fun (tag, slots) => (slots.zipIdx.map fun (x, i) =>
        go s!"{p}/x-tagged/{escape tag}/{i}" (if role == "value" then "grammar" else role) x).flatten).flatten
    | .zip _ x => go s!"{p}/x-zip/items" role x
    | .zipOrEmpty _ x => go s!"{p}/x-zip-or-empty/items" role x
    | .onCase x => go s!"{p}/x-case" cond x
    | .select cs =>
      (cs.zipIdx.map fun ((w, t), i) => go s!"{p}/x-select/{i}/when" cond w ++
        go s!"{p}/x-select/{i}/then" role t).flatten
    | .countWhere _ w _ => go s!"{p}/x-count-where/where" cond w
    | .rows x => go s!"{p}/x-rows" role x
    | .node _ keywords => (keywords.map (go p role)).flatten
    | .lean _ x _ => go p role x
    | .copied _ x => go p (if role == "value" then "copied" else role) x
    | .encodedEnvironment x => go p role x
    | _ => []

/-- Every top-level schema and `$defs` entry of a file, with its pointer. -/
def entries (f : File) : List (String × Shape) :=
  f.top.map (fun (k, s) => ("/" ++ escape k, s)) ++
    (f.defs.map fun (k, d) => match d with
      | .schema s => [(s!"/$defs/{escape k}", s)]
      | .group _ es => es.map fun (e, s) => (s!"/$defs/{escape k}/{escape e}", s)).flatten

/-- A role inside a part used in the role `outer`: a condition, copy or grammar slot keeps its own. -/
def compose (outer inner : String) : String := if inner == "value" then outer else if outer == "value" then inner else outer

/-- The references under `s`, used in the role `role`, each with the role of its use. -/
def refsOf : Nat → String → Shape → List (String × String)
  | 0, _, _ => []
  | fuel + 1, role, s =>
    let go := refsOf fuel
    let cond := compose role "condition"
    match s with
    | .ref target => [(target, role)]
    | .object ps extra => (ps.map fun (_, v) => go role v).flatten ++ (extra.map (go role)).getD []
    | .prefixItems ss | .anyOf ss | .allOf ss => (ss.map (go role)).flatten
    | .items x | .zip _ x | .zipOrEmpty _ x | .rows x | .lean _ x _ | .encodedEnvironment x => go role x
    | .contains x | .not x | .onCase x | .countWhere _ x _ => go cond x
    | .ite c t e => go cond c ++ go role t ++ go role e
    | .tagged table => (table.map fun (_, slots) => (slots.map (go (compose role "grammar"))).flatten).flatten
    | .select cs => (cs.map fun (w, t) => go cond w ++ go role t).flatten
    | .node _ keywords => (keywords.map (go role)).flatten
    | .copied _ x => go (compose role "copied") x
    | _ => []

/-- Every entry the rows reach (from each file's top-level schemas, as values), with each role in
which it is reached. -/
def reach (files : List File) : List (String × String) := Id.run do
  let mut seen : List (String × String) := []
  let mut todo : List (String × String) :=
    (files.map fun f => f.top.map fun (k, _) => (s!"{f.name}#/{escape k}", "value")).flatten
  for _ in [0:100000] do
    match todo with
    | [] => break
    | (t, r) :: rest =>
      todo := rest
      if seen.contains (t, r) then continue
      seen := seen ++ [(t, r)]
      if let some x := lookup files t then todo := todo ++ refsOf depth r x
  return seen

/-- Every `enum` and `const` of every file, with the roles in which the rows use it. -/
def sites (files : List File) : List Site :=
  let reached := reach files
  (files.map fun f => ((entries f).map fun (p, s) =>
    let uses := (reached.filter (·.1 == s!"{f.name}#{p}")).map (·.2)
    (sitesOf f.name depth p "value" s).map fun x =>
      { x with uses := (uses.map (compose · x.role)).eraseDups }).flatten).flatten

/-- Whether no value valid under `s` is a string (a type, a declared domain or a keyword excludes them). -/
def stringFree (files : List File) : Nat → Shape → Bool
  | 0, _ => false
  | fuel + 1, s =>
    let go := stringFree files fuel
    match s with
    | .bool false => true
    | .type ts => !ts.contains "string"
    | .const v | .enum [v] => match v with
      | .str _ => false
      | _ => true
    | .enum vs => vs.all fun | .str _ => false | _ => true
    | .node _ ks | .allOf ks => ks.any go
    | .anyOf ss => ss.all go
    | .ref target => (lookup files target).any go
    | .lean _ x _ | .copied _ x | .encodedEnvironment x => go x
    | _ => false

/-- The declared values of a field: the declarations they come from, the values, whether every
string the field may hold is among them (`strings`), and whether every value is (`exact`). -/
structure Domain where
  sites : List String
  values : List Json
  strings : Bool
  exact : Bool

/-- The domain a field's value resolves to, through references, keyword groups, Lean deciders and
alternatives (each of whose members declares values or holds no string). -/
def domainOf (files : List File) : Nat → String → String → Shape → Option Domain
  | 0, _, _, _ => none
  | fuel + 1, file, p, s =>
    match s with
    | .enum vs => some ⟨[s!"{file}#{p}/enum"], vs, true, true⟩
    | .const v => some ⟨[s!"{file}#{p}/const"], [v], true, true⟩
    | .ref target => do
      let x ← lookup files target
      let (f, ptr) := match target.splitOn "#" with
        | [f, ptr] => (f, ptr)
        | _ => (file, target)
      domainOf files fuel f ptr x
    | .lean _ x _ => domainOf files fuel file p x
    | .node _ keywords => keywords.findSome? (domainOf files fuel file p)
    | .allOf ss => ss.zipIdx.findSome? fun (x, i) => domainOf files fuel file s!"{p}/allOf/{i}" x
    | .anyOf ss =>
      let ds := ss.zipIdx.map fun (x, i) => (x, domainOf files fuel file s!"{p}/anyOf/{i}" x)
      if ds.all (·.2.isNone) then none else
      some ⟨(ds.filterMap (·.2)).flatMap (·.sites), (ds.filterMap (·.2)).flatMap (·.values),
        ds.all (fun (x, d) => match d with
          | some d => d.strings
          | none => stringFree files depth x),
        ds.all (fun (_, d) => d.any (·.exact))⟩
    | _ => none

/-- A field whose value resolves to declared values: where it is, its name (`[]` for an array's items,
`*` for an object's other properties), its domain, and the shape whose skeleton holds the field
(`wrapper`, an object of that one field or an array of those items). -/
structure Probe where
  file : String
  pointer : String
  name : String
  domain : Domain
  wrapper : Shape

instance : ToJson Probe where
  toJson q := Json.mkObj [("file", .str q.file), ("pointer", .str q.pointer), ("name", .str q.name),
    ("sites", toJson q.domain.sites), ("values", .arr q.domain.values.toArray),
    ("strings", .bool q.domain.strings), ("exact", .bool q.domain.exact)]

/-- The probes under `s`, in value positions only (not under a condition, a copy or a grammar). -/
def probesOf (files : List File) (file : String) : Nat → String → Shape → List Probe
  | 0, _, _ => []
  | fuel + 1, p, s =>
    let go := probesOf files file fuel
    let probe (ptr name : String) (v wrapper : Shape) : List Probe :=
      match domainOf files depth file ptr v with
      | some d => [⟨file, ptr, name, d, wrapper⟩]
      | none => []
    let many (key : String) (ss : List Shape) : List Probe :=
      (ss.zipIdx.map fun (x, i) => go s!"{p}/{key}/{i}" x).flatten
    match s with
    | .object ps extra =>
      (ps.map fun (k, v) =>
        let ptr := s!"{p}/properties/{escape k}"
        probe ptr k v (.object [(k, v)] none) ++ go ptr v).flatten ++
        (match extra with
         | some (.bool _) | none => []
         | some e => probe s!"{p}/additionalProperties" "*" e (.object [] (some e)) ++
             go s!"{p}/additionalProperties" e)
    | .items x => probe s!"{p}/items" "[]" x (.items x) ++ go s!"{p}/items" x
    | .prefixItems ss => many "prefixItems" ss
    | .anyOf ss => many "anyOf" ss
    | .allOf ss => many "allOf" ss
    | .ite _ t e =>
      let branch (k : String) : Shape → List Probe
        | .bool true => []
        | b => go s!"{p}/{k}" b
      branch "then" t ++ branch "else" e
    | .zip _ x => go s!"{p}/x-zip/items" x
    | .zipOrEmpty _ x => go s!"{p}/x-zip-or-empty/items" x
    | .select cs => (cs.zipIdx.map fun ((_, t), i) => go s!"{p}/x-select/{i}/then" t).flatten
    | .rows x => go s!"{p}/x-rows" x
    | .node _ keywords => (keywords.map (go p)).flatten
    | .lean _ x _ => go p x
    | .encodedEnvironment x => go p x
    | _ => []

def probes (files : List File) : List Probe :=
  (files.map fun f => ((entries f).map fun (p, s) => probesOf files f.name depth p s).flatten).flatten

/-- The skeleton of a probe's field: the extracted skeleton of its wrapper, then the field's. -/
def fieldSkeleton (files : List File) (q : Probe) : Except String Skel := do
  let (k, _) ← (skeletonOf files depth q.wrapper).run {}
  let k := Skel.simp depth k
  match q.name, k with
  | "[]", .arr _ it => pure it
  | "[]", .any => pure .any
  | _, .obj fs ex _ _ => pure (Skel.field fs ex (if q.name == "*" then "" else q.name))
  | _, .any => pure .any
  | _, k => throw s!"{q.file}{q.pointer}: the wrapper's skeleton is not an object or array: {repr k}"

/-- `fieldSkel% i`: the skeleton of the field of probe `i` (`probes Schemas.files`). -/
syntax (name := fieldSkelTerm) "fieldSkel% " num : term

open Elab in
elab_rules : term
  | `(fieldSkel% $i:num) => do
    let some q := (probes Schemas.files)[i.getNat]? | throwError "no probe {i.getNat}"
    match fieldSkeleton Schemas.files q with
    | .error e => throwError e
    | .ok k => pure (toExpr k)

end ResponseShape.EnumSites

namespace ResponseShape.Skel
open Lean

/-- Whether `k` may allow the scalar `v`: a decision the probes' negative cases evaluate. Every value
fitting `k` is allowed (`Fits.admits`); `fuel` bounds the nesting, past which everything is. -/
def admits (v : Json) : Nat → Skel → Bool
  | 0, _ => true
  | fuel + 1, k => match k with
    | .any => true
    | .nothing => false
    | .strIn vs => match v with
      | .str s => vs.contains s
      | _ => false
    | .lit l => Decidable.decide (Lit.of? v = some l)
    | .strNotIn vs => match v with
      | .str s => !vs.contains s
      | _ => true
    | .kindNot t => kind v != t
    | .obj .. => match v with
      | .obj _ => true
      | _ => false
    | .arr .. => match v with
      | .arr _ => true
      | _ => false
    | .all ss => ss.all (admits v fuel)
    | .alt ss => ss.any (admits v fuel)
    | .onCase _ t e => admits v fuel t || admits v fuel e
    | .encodedEnvironment _ => true

end ResponseShape.Skel

namespace ResponseShape
open Lean

theorem Lit.of_json (l : Lit) : Lit.of? l.json = some l := by
  cases l <;> rfl

theorem Fits.admits {c : Json} {k : Skel} {v : Json} (h : Fits c k v) : ∀ n, k.admits v n = true := by
  induction h with
  | any v => intro n; cases n <;> rfl
  | strIn hs => intro n; cases n <;> simp [Skel.admits, hs]
  | lit l => intro n; cases n <;> simp [Skel.admits, Lit.of_json]
  | strNotIn hs =>
    rename_i vs v
    intro n
    cases n with
    | zero => rfl
    | succ n =>
      cases v <;> simp [Skel.admits]
      exact hs _ rfl
  | kindNot hk => intro n; cases n <;> simp [Skel.admits, hk]
  | obj => intro n; cases n <;> rfl
  | arr => intro n; cases n <;> rfl
  | all _ ih =>
    intro n
    cases n with
    | zero => rfl
    | succ n =>
      simp only [Skel.admits, List.all_eq_true]
      exact fun s hs => ih s hs n
  | alt hm _ ih =>
    intro n
    cases n with
    | zero => rfl
    | succ n =>
      simp only [Skel.admits, List.any_eq_true]
      exact ⟨_, hm, ih n⟩
  | onCaseT _ _ ih => intro n; cases n <;> simp [Skel.admits, ih]
  | onCaseE _ _ ih => intro n; cases n <;> simp [Skel.admits, ih]
  | softEnvironment => intro n; cases n <;> rfl
  | rightsEnvironment => intro n; cases n <;> rfl

/-- A value the skeleton rules out does not fit it (the probes' negative cases, by `decide`). -/
theorem Fits.not_of_admits {c : Json} {k : Skel} {v : Json} {n : Nat} (h : k.admits v n = false) :
    ¬ Fits c k v := fun hf => by
  rw [hf.admits n] at h
  cases h

end ResponseShape
