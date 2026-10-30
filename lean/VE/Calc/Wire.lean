import VE.Calc.Lower
import VE.Calc.Poly
import VE.Calc.Render
import VE.Time.Wire
import VE.Route.Wire

/-! The case `ve-calc@0` (math-evidence spec 3.1 to 3.3, ME-2): its limits in order, its decoder and its identity.
It decodes claims over stated, defined and free values, and derivations (`follows`) over the case's `premises`
(ME-5). The fields and checks of later batches (`counted` values, `unit`, `environment`, `source`, `data`, `budget`;
`consistent`, `identity` and `sqrt-rounds`) are refused, as unknown fields or as no claim, until their batch adds
them. -/

namespace VE.Calc
open Lean VE.Numbers

/-- Every question a `calc@0` case asks (spec 3.4): a claim or a derivation; ME-8 and ME-9 add their constructors.
The decoder resolves premise ids to their claims. -/
inductive Check where
  | claim (c : Claim)
  | follows (P : List Claim) (links : List (String × String)) (C : Claim)

def Check.exprs : Check → List Expr
  | .claim c => c.exprs
  | .follows P _ C => (C :: P).flatMap Claim.exprs

def Check.names (k : Check) : List String := k.exprs.flatMap Expr.names

structure Case where
  decls : List Decl
  claims : List (String × Check)
  software : Option String

/-- A check's sides under the values `τ`: a claim's expressions' values; a derivation has none here. -/
def Check.sides (τ : String → Val) : Check → List Val
  | .claim c => c.exprs.map (Expr.evalL τ)
  | .follows .. => []

/-- The checks' sides over the table, charged (3.2 (a), (b)): each claim's expressions once, in claim order. A
derivation is charged nothing here: its lowering and search are 5's (me-2nc charges them). -/
def Check.sidesC (limit : Nat) (t : Work.Table) : List Check → Nat → Option (List (List Val) × Nat)
  | [], w => some ([], w)
  | .claim c :: ks, w => (Work.Expr.evalsC limit t c.exprs w).bind fun (vs, w) =>
      (Check.sidesC limit t ks w).map fun r => (vs :: r.1, r.2)
  | .follows .. :: ks, w => (Check.sidesC limit t ks w).map fun r => ([] :: r.1, r.2)

/-- The case's work within `limit` units (limit 10): the value table, then each check's sides. -/
def Case.sidesC (limit : Nat) (c : Case) : Option (List (List Val) × Nat) :=
  (Work.valueTableC limit c.decls [] 0).bind fun (t, w) => Check.sidesC limit t (c.claims.map (·.2)) w

theorem Check.sidesC_some (limit : Nat) (t : Work.Table) (ks : List Check) (w : Nat) (vss : List (List Val)) (w' : Nat)
    (hw : w ≤ limit) (h : Check.sidesC limit t ks w = some (vss, w')) :
    vss = ks.map (Check.sides t.read) ∧ w ≤ w' ∧ w' ≤ limit := by
  induction ks generalizing w vss with
  | nil => cases h; exact ⟨rfl, by omega, hw⟩
  | cons k ks ih =>
    cases k with
    | claim c =>
      obtain ⟨⟨vs, w1⟩, hv, h⟩ := Option.bind_eq_some_iff.mp h
      obtain ⟨⟨vss', w2⟩, hr, h⟩ := Option.map_eq_some_iff.mp h
      cases h
      obtain ⟨rfl, h1, h2⟩ := Work.Expr.evalsC_some _ _ _ _ _ _ hw hv
      obtain ⟨rfl, h3, h4⟩ := ih _ _ h2 hr
      exact ⟨rfl, by omega, h4⟩
    | follows =>
      obtain ⟨⟨vss', w2⟩, hr, h⟩ := Option.map_eq_some_iff.mp h
      cases h
      obtain ⟨rfl, h3, h4⟩ := ih _ _ hw hr
      exact ⟨rfl, h3, h4⟩

theorem Check.sidesC_mono {limit limit' : Nat} (t : Work.Table) (ks : List Check) (w : Nat)
    (r : List (List Val) × Nat) (hl : limit ≤ limit') (h : Check.sidesC limit t ks w = some r) :
    Check.sidesC limit' t ks w = some r := by
  induction ks generalizing w r with
  | nil => exact h
  | cons k ks ih =>
    cases k with
    | claim c =>
      obtain ⟨⟨vs, w1⟩, hv, h⟩ := Option.bind_eq_some_iff.mp h
      obtain ⟨r', hr, rfl⟩ := Option.map_eq_some_iff.mp h
      simp only [Check.sidesC, Work.Expr.evalsC_mono _ _ _ _ hl hv, Option.bind_some, ih _ _ hr, Option.map_some]
    | follows =>
      obtain ⟨r', hr, rfl⟩ := Option.map_eq_some_iff.mp h
      simp only [Check.sidesC, ih _ _ hr, Option.map_some]

/-- Within its limit, the case's sides are 2.4's values, read from the table. -/
theorem Case.sidesC_some (limit : Nat) (c : Case) (vss : List (List Val)) (w : Nat)
    (h : c.sidesC limit = some (vss, w)) : vss = c.claims.map (·.2.sides (valuesL c.decls)) ∧ w ≤ limit := by
  obtain ⟨⟨t, w1⟩, ht, h⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨ht', _, h1⟩ := Work.valueTableC_some _ _ _ _ _ _ (Nat.zero_le _) ht
  obtain ⟨rfl, _, h2⟩ := Check.sidesC_some _ _ _ _ _ _ h1 h
  refine ⟨?_, h2⟩
  have : t = Work.valueTable c.decls := ht'
  rw [this, Work.valueTable_read, List.map_map]; rfl

theorem Case.sidesC_mono {limit limit' : Nat} (c : Case) (r : List (List Val) × Nat) (hl : limit ≤ limit')
    (h : c.sidesC limit = some r) : c.sidesC limit' = some r := by
  obtain ⟨⟨t, w1⟩, ht, h⟩ := Option.bind_eq_some_iff.mp h
  simp only [Case.sidesC, Work.valueTableC_mono _ _ _ _ hl ht, Option.bind_some]
  exact Check.sidesC_mono _ _ _ _ hl h

namespace Wire
open VE.Bridge (fields identifier)

def invalid (path what : String) : String := s!"InvalidInput: {path} {what}"

/-- Every field is one of `names` or `optional`, and every one of `names` is there. -/
def checkFields (path : String) (j : Json) (names : List String) (optional : List String := []) :
    Except String Unit := do
  let actual ← match fields j with
    | .ok fs => pure (fs.map Prod.fst)
    | .error _ => throw (invalid path "must be an object")
  if let some n := actual.find? (!(names ++ optional).contains ·) then throw (invalid s!"{path}.{n}" "is unknown")
  if let some n := names.find? (!actual.contains ·) then throw (invalid s!"{path}.{n}" "is missing")

/-! ## Limits (3.2), checked first and in this order -/

def limit (what : String) (n : Nat) : String := s!"ResourceLimit: {what} exceeds {n}"

def children (j : Json) : List Json := match j with
  | .arr xs => xs.toList
  | .obj _ => ((fields j).toOption.getD []).map (·.2)
  | _ => []

/-- The number of JSON values in `js` and below (objects, arrays and scalars alike), up to `fuel`: one at a time
from a worklist, so no nesting hides a value from limit 1 and none deepens the stack. -/
def count (fuel : Nat) (js : List Json) (n : Nat := 0) : Nat := match fuel, js with
  | 0, _ | _, [] => n
  | f + 1, j :: js => count f (children j ++ js) (n + 1)

/-- The nesting of arrays and objects in `j`, up to `fuel`. -/
def depth : Nat → Json → Nat
  | 0, _ => 0
  | n + 1, j => if j matches .arr _ | .obj _ then 1 + (children j).foldl (fun d c => max d (depth n c)) 0 else 0

/-- The first value of `j`, in document order, that `p` refuses. -/
def scan (p : Json → Option String) : Nat → Json → Option String
  | 0, _ => none
  | n + 1, j => (p j).orElse fun _ => (children j).findSome? (scan p n)

/-- Limit 5: a `pow` or `sci` exponent beyond 64 in absolute value. -/
def exponentFault (j : Json) : Option String :=
  match j with
  | .arr xs => match xs.toList with
    | [.str "pow", _, k] | [.str "sci", _, k] => match k.getInt? with
      | .ok k => if k.natAbs > 64 then some (limit "an exponent" 64) else none
      | .error _ => none
    | _ => none
  | _ => none

/-- Limit 6: a literal of more than 40 digits, as W6's `parseDecimal` counts and words it. -/
def literalFault (j : Json) : Option String :=
  let digits (s : String) : Option String := match VE.Time.parseDecimal s with
    | .error e => if e.startsWith "ResourceLimit" then some e else none
    | .ok _ => none
  match j with
  | .arr xs => match xs.toList with
    | [.str "lit", .str s] | .str "sci" :: .str s :: _ => digits s
    | .str r :: _ :: .str s :: _ => if r.startsWith "rounds" then digits s else none
    | _ => none
  | .obj _ => match j.getObjVal? "stated" with
    | .ok (.str s) => digits s
    | _ => none
  | _ => none

/-- Limit 7 (2.6): a string or object key of more than 64 bytes. Names, claim ids, `software` and every string a
later batch decodes are capped alike, as no field is listed. -/
def stringFault (j : Json) : Option String :=
  let long (s : String) : Bool := s.utf8ByteSize > VE.Limits.maxIdentifierBytes
  if (match j with
    | .str s => long s
    | .obj _ => ((fields j).toOption.getD []).any (long ·.1)
    | _ => false) then some (limit "a string" VE.Limits.maxIdentifierBytes) else none

/-- The case as limit 7 reads it: a value record's `words` string, the one string it does not cap, as `null`. -/
def unworded (j : Json) : Json := match j.getObjVal? "values" with
  | .ok (.arr vs) => j.setObjVal! "values" (.arr (vs.map fun v =>
    if v.getObjVal? "words" matches .ok (.str _) then v.setObjVal! "words" .null else v))
  | _ => j

def entries (j : Json) (key : String) : Nat := match j.getObjVal? key with
  | .ok (.arr xs) => xs.size
  | _ => 0

/-- Limit 10's refusal (3.2): the work of computing the case passes `maxWork` units. -/
def workLimit : String := limit "the work of the calculation" Work.maxWork

/-- The first limit of 3.2 the case exceeds: 10,000 JSON values, depth 64, 512 values, 512 claims, then
exponents, literals and strings, each anywhere in the case, then 512 premises. -/
def limitFault (j : Json) : Option String :=
  if count (VE.Limits.maxNodes + 1) [j] > VE.Limits.maxNodes then
    some (limit "the number of JSON values" VE.Limits.maxNodes)
  else if depth (VE.Limits.maxDepth + 1) j > VE.Limits.maxDepth then some (limit "the JSON depth" VE.Limits.maxDepth)
  else if entries j "values" > 512 then some (limit "the number of values" 512)
  else if entries j "claims" > 512 then some (limit "the number of claims" 512)
  else ([(exponentFault, j), (literalFault, j), (stringFault, unworded j)].findSome? fun (p, j) =>
    scan p (VE.Limits.maxDepth + 1) j).orElse fun _ =>
      if entries j "premises" > 512 then some (limit "the number of premises" 512) else none

/-! ## Literals, expressions and claims (3.1), each with its canonical form (3.3) -/

/-- The shortest plain decimal string of a printed number's value: "0.30" and "0.3" are "0.3", and
`["sci", "2", 7]` is "20000000". -/
def plain (p : Printed) : String :=
  if p.places ≤ 0 then toString (p.digits * 10 ^ (-p.places).toNat)
  else
    let d := VE.Time.render p.places.toNat p.digits
    VE.Time.Dec.toString { d with frac := (d.frac.reverse.dropWhile (· = 0)).reverse }

/-- A printed number with its written places, its digits and places as canonical decimal strings (J1). -/
def printedJson (p : Printed) : Json := Json.arr #[.str (toString p.digits), .str (toString p.places)]

/-- A literal: `"<decimal>"` (W6's `parseDecimal`) or `["sci", "<decimal>", e]`, read with its written places. -/
def literal (path : String) (j : Json) : Except String Printed := do
  let dec (s : String) : Except String VE.Time.Dec := match VE.Time.parseDecimal s with
    | .ok d => pure d
    | .error _ => throw (invalid path "must be a decimal")
  match j with
  | .str s => Printed.ofDec <$> dec s
  | .arr xs => match xs.toList with
    | .str "sci" :: .str s :: e :: [] => match e.getInt? with
      | .ok e => (Printed.sci · e) <$> dec s
      | .error _ => throw (invalid s!"{path}.2" "must be an integer")
    | _ => throw (invalid path "must be a literal")
  | _ => throw (invalid path "must be a literal")

def operations : List (String × (Expr → Expr → Expr)) :=
  [("add", .add), ("sub", .sub), ("mul", .mul), ("div", .div)]

def comparisons : List (String × Comparison) :=
  [("eq", ⟨.eq, false⟩), ("lt", ⟨.lt, false⟩), ("le", ⟨.le, false⟩), ("gt", ⟨.lt, true⟩), ("ge", ⟨.le, true⟩)]

def rules : List (String × Rounding) := [("ties-up", .tiesUp), ("half-even", .halfEven)]

/-- An expression and its canonical form; `fuel` bounds its nesting, which the depth limit keeps below it. -/
def expr (path : String) (fuel : Nat) (j : Json) : Except String (Expr × Json) := do
  let .succ n := fuel | throw (invalid path "is nested too deeply")
  let .ok xs := j.getArr? | throw (invalid path "must be an expression")
  match xs.toList with
  | .str "lit" :: l :: [] => do
    let p ← literal s!"{path}.1" l
    pure (.lit p.value, Json.arr #[.str "lit", .str (plain p)])
  | .str "val" :: .str v :: [] => pure (.val v, j)
  | .str "pow" :: a :: k :: [] => do
    let (a, ca) ← expr s!"{path}.1" n a
    let .ok k := k.getNat? | throw (invalid s!"{path}.2" "must be a natural number")
    pure (.pow a k, Json.arr #[.str "pow", ca, toJson k])
  | .str op :: a :: b :: [] => do
    let some f := operations.lookup op | throw (invalid path "must be an expression")
    let (a, ca) ← expr s!"{path}.1" n a
    let (b, cb) ← expr s!"{path}.2" n b
    pure (f a b, Json.arr #[.str op, ca, cb])
  | _ => throw (invalid path "must be an expression")

/-- A claim and its canonical form; a `rounds` claim carries its rule, the case's unless it names one. -/
def claim (rule : String × Rounding) (path : String) (j : Json) : Except String (Claim × Json) := do
  let e (i : Nat) (x : Json) := expr s!"{path}.{i}" VE.Limits.maxDepth x
  let rounds (name : String) (r : Rounding) (x p : Json) (tail : Array Json) := do
    let (x, cx) ← e 1 x
    let p ← literal s!"{path}.2" p
    pure (Claim.rounds r x p, Json.arr (#[.str name, cx, printedJson p].append tail))
  match (j.getArr?.toOption.map (·.toList) : Option (List Json)) with
  | some (.str "within" :: x :: lo :: hi :: []) => do
    let (x, cx) ← e 1 x
    let (lo, cl) ← e 2 lo
    let (hi, ch) ← e 3 hi
    pure (.within x lo hi, Json.arr #[.str "within", cx, cl, ch])
  | some (.str "rounds" :: x :: p :: []) => rounds "rounds" rule.2 x p #[.str rule.1]
  | some (.str "rounds" :: x :: p :: .str r :: []) => match rules.lookup r with
    | some rr => rounds "rounds" rr x p #[.str r]
    | none => throw (invalid s!"{path}.3" "must be \"ties-up\" or \"half-even\"")
  | some (.str "rounds-down" :: x :: p :: []) => rounds "rounds-down" .down x p #[]
  | some (.str "rounds-up" :: x :: p :: []) => rounds "rounds-up" .up x p #[]
  | some (.str op :: a :: b :: []) => do
    let some c := comparisons.lookup op | throw (invalid path "must be a claim")
    let (a, ca) ← e 1 a
    let (b, cb) ← e 2 b
    pure (.compare c a b, Json.arr #[.str op, ca, cb])
  | _ => throw (invalid path "must be a claim")

/-! ## Records (3.1) -/

def supports : List String := ["observation", "testimony", "assumption"]

/-- A record as hashed (3.3): `fields` with the record's optional `support` and `span` (a span is recorded, not
checked against a source, before ME-4). -/
def recordJson (path : String) (j : Json) (fields : List (String × Json)) : Except String Json := do
  let support ← match j.getObjVal? "support" with
    | .error _ => pure []
    | .ok (.str s) => do
      unless supports.contains s do throw (invalid s!"{path}.support" "must be observation, testimony or assumption")
      pure [("support", Json.str s)]
    | .ok _ => throw (invalid s!"{path}.support" "must be a string")
  let span ← match j.getObjVal? "span" with
    | .error _ => pure []
    | .ok s => match s.getArr?.toOption.map (·.toList.map Json.getNat?) with
      | some [Except.ok a, Except.ok b] => do
        unless a ≤ b do throw (invalid s!"{path}.span" "must not end before it starts")
        pure [("span", Json.arr #[toJson a, toJson b])]
      | _ => throw (invalid s!"{path}.span" "must be two natural numbers")
  pure (Json.mkObj (fields ++ support ++ span))

/-- 11.2's rules for a value's words, after W6's (`VE.Time.Wire.displayString`): they begin with "the" and not with
a phrase word (`ValueWordsForm`, naming the phrase word, else the first word), and contain no reserved word
(`ReservedWord`). -/
def checkWords (name w : String) : Except String Unit := do
  VE.Time.Wire.displayString w false "Verbalisation"
  let first := ((English.leadingPhrase w).getD ((w.splitOn " ").headD ""))
  unless w.startsWith "the " && (English.leadingPhrase w).isNone do
    throw s!"ValueWordsForm: the words of {name} must begin with \"the\" and not with \"{first}\""
  if let some r := English.reservedIn w then throw s!"ReservedWord: \"{r}\" in the words of {name}"

/-- W6a's check over the values' words (`VerbalisationCollision`), each value's words as a constant's
verbalisation. -/
def checkVerbalisations (vs : List Json) : Except String Unit :=
  VE.Time.Wire.checkVerbalisations <| vs.map fun v =>
    ((v.getObjValD "name").getStr?.toOption.getD "", Json.mkObj [("verbalisation", v.getObjValD "words")])

/-- A value record: its name and its source (stated, defined, or free as `none`), and the record as hashed, without
`words`. -/
def value (i : Nat) (j : Json) : Except String ((String × Option (Rat ⊕ Expr)) × Json) := do
  let path := s!"values.{i}"
  checkFields path j ["name", "words"] ["stated", "defined", "free", "support", "span"]
  let .ok (.str name) := j.getObjVal? "name" | throw (invalid s!"{path}.name" "must be a string")
  unless identifier name do throw (invalid s!"{path}.name" "must be a name")
  let .ok (.str words) := j.getObjVal? "words" | throw (invalid s!"{path}.words" "must be a string")
  checkWords name words
  let (src, cs) ← match j.getObjVal? "stated", j.getObjVal? "defined", j.getObjVal? "free" with
    | .ok l, .error _, .error _ => do
      let p ← literal s!"{path}.stated" l
      pure (some (Sum.inl p.value), ("stated", Json.str (plain p)))
    | .error _, .ok x, .error _ => do
      let (x, cx) ← expr s!"{path}.defined" VE.Limits.maxDepth x
      pure (some (Sum.inr x), ("defined", cx))
    | .error _, .error _, .ok f => do
      unless f == .bool true do throw (invalid s!"{path}.free" "must be true")
      pure (none, ("free", Json.bool true))
    | _, _, _ => throw (invalid path "must have one of stated, defined and free")
  pure ((name, src), ← recordJson path j [("name", .str name), cs])

def claimIdChar (c : Char) : Bool := VE.Surface.identChar c || c == '-'

def claimId (path : String) (j : Json) : Except String String := do
  let .ok (.str id) := j.getObjVal? "id" | throw (invalid s!"{path}.id" "must be a string")
  unless id != "" && id.all claimIdChar do throw (invalid s!"{path}.id" "must be a claim id")
  pure id

/-- A `premises` entry (ME-5): its id and claim, an `eq`, `lt`, `le`, `gt`, `ge` or `within` claim, and the entry as
hashed, with its support. -/
def premise (rule : String × Rounding) (i : Nat) (j : Json) : Except String ((String × Claim) × Json) := do
  let path := s!"premises.{i}"
  checkFields path j ["id", "claim", "support"] ["span"]
  let id ← claimId path j
  let (c, cc) ← claim rule s!"{path}.claim" (j.getObjValD "claim")
  if c matches .rounds .. then throw (invalid s!"{path}.claim" "must be a comparison or a range")
  pure ((id, c), ← recordJson path j [("id", .str id), ("claim", cc)])

/-- A check and its canonical form: a claim, or `["follows", conclusion, [premise ids], [[square, root], …]]` with
an `lt`, `le`, `gt` or `ge` conclusion and each id resolved to its premise's claim. -/
def check (rule : String × Rounding) (premises : List (String × Claim)) (path : String) (j : Json) :
    Except String (Check × Json) := do
  match (j.getArr?.toOption.map (·.toList) : Option (List Json)) with
  | some [.str "follows", c, .arr ids, .arr links] => do
    let (C, cc) ← claim rule s!"{path}.1" c
    unless C matches .compare ⟨.lt, _⟩ _ _ | .compare ⟨.le, _⟩ _ _ do
      throw (invalid s!"{path}.1" "must be an lt, le, gt or ge claim")
    let P ← ids.toList.zipIdx.mapM fun (id, i) => match id with
      | .str id => match premises.lookup id with
        | some p => pure p
        | none => throw s!"UnknownPremise: {id}"
      | _ => throw (invalid s!"{path}.2.{i}" "must be a premise id")
    let ls ← links.toList.zipIdx.mapM fun (l, i) => match (l.getArr?.toOption.map (·.toList) : Option (List Json)) with
      | some [.str s, .str r] => pure (s, r)
      | _ => throw (invalid s!"{path}.3.{i}" "must be two names")
    pure (.follows P ls C, Json.arr #[.str "follows", cc, .arr ids, .arr links])
  | _ => do
    let (c, cc) ← claim rule path j
    pure (.claim c, cc)

/-- A `claims` entry: its id and check, the claim as hashed and the entry as hashed. -/
def entry (rule : String × Rounding) (premises : List (String × Claim)) (i : Nat) (j : Json) :
    Except String ((String × Check) × Json × Json) := do
  let path := s!"claims.{i}"
  checkFields path j ["id", "claim"] ["span"]
  let id ← claimId path j
  let (k, cc) ← check rule premises s!"{path}.claim" (j.getObjValD "claim")
  pure ((id, k), cc, ← recordJson path j [("id", .str id), ("claim", cc)])

/-! ## Names and definition order -/

def decl (v : String × Option (Rat ⊕ Expr)) : Decl :=
  ⟨v.1, match v.2 with
    | some (.inl q) => .stated q
    | some (.inr e) => .defined e
    | none => .free⟩

/-- The first name that occurs again later in the list. -/
def firstDup : List String → Option String
  | [] => none
  | n :: ns => if ns.contains n then some n else firstDup ns

/-- The first name a definition reads that neither `known` nor a value before it declares. -/
def firstUnknown (known : List String) : List Decl → Option String
  | [] => none
  | d :: ds => (match d.source with
      | .defined e => e.names.find? (!known.contains ·)
      | _ => none).or (firstUnknown (known ++ [d.name]) ds)

/-- The path of the innermost part of `e` that, inlined by `t` within `maxPolyTerms` nodes, is not linear in the kept
names (`Expr.linear`). -/
def nonlinearAt (t : Inlined) (path : String) (e : Expr) : Option String :=
  let inner : Option String := match e with
    | .add a b | .sub a b | .mul a b | .div a b =>
      (nonlinearAt t s!"{path}.1" a).orElse fun _ => nonlinearAt t s!"{path}.2" b
    | .pow a _ => nonlinearAt t s!"{path}.1" a
    | .lit _ | .val _ => none
  inner.orElse fun _ =>
    if (e.subst t).toOption.any fun e => (e.nodesWithin maxPolyTerms).isSome && e.linear.isNone then some path
    else none

/-- Square links name free values (`UnknownLink`); then every premise and each derivation's conclusion is linear in
the free values once inlined (`NonlinearPremise`, naming the innermost part that is not). A part whose inlining meets
a fault, or whose inlined form is beyond `maxPolyTerms` nodes, is not judged here: its row says why. -/
def derivations (ds : List Decl) (premises : List (String × Claim)) (claims : List (String × Check)) :
    Except String Unit := do
  let free := freeNames ds
  let links := claims.flatMap fun (_, k) => match k with
    | .follows _ ls _ => ls.flatMap fun l => [l.1, l.2]
    | _ => []
  if let some n := links.find? (!free.contains ·) then throw s!"UnknownLink: {n}"
  let t := inlineTable ds free
  let lowered := premises.zipIdx.map (fun ((_, c), i) => (s!"premises.{i}.claim", c)) ++
    claims.zipIdx.filterMap fun ((_, k), i) => match k with
      | .follows _ _ C => some (s!"claims.{i}.claim.1", C)
      | _ => none
  if let some p := lowered.findSome? fun (path, c) =>
      c.exprs.zipIdx.findSome? fun (e, i) => nonlinearAt t s!"{path}.{i + 1}" e then
    throw s!"NonlinearPremise: {p} (declare a square link or name the product)"

/-- Names are unique, each name read is declared (before its use in a definition), claim and premise ids are unique,
and derivations are linear in the free values, in that order. -/
def admit (ds : List Decl) (premises : List (String × Claim)) (claims : List (String × Check)) : Except String Unit :=
  let names := ds.map Decl.name
  let read := premises.flatMap (·.2.exprs.flatMap Expr.names) ++ claims.flatMap (·.2.names)
  match firstDup names, (firstUnknown [] ds).or (read.find? (!names.contains ·)),
      firstDup (premises.map (·.1) ++ claims.map (·.1)) with
  | some n, _, _ => .error s!"DuplicateName: {n}"
  | none, some n, _ => .error s!"UnknownName: {n} (declare it before the value that uses it)"
  | none, none, some n => .error s!"DuplicateClaimId: {n}"
  | none, none, none => derivations ds premises claims

/-! ## The decoder and the identity (3.3) -/

/-- The case's limits, fields and format, before anything else is read. -/
def checkCase (j : Json) : Except String Unit := do
  if let some e := limitFault j then throw e
  checkFields "case" j ["format", "values", "claims"] ["premises", "rounding", "software"]
  unless j.getObjValD "format" == .str "ve-calc@0" do throw (invalid "case.format" "must be \"ve-calc@0\"")

/-- The case's `meaning_id` and each claim's id: the case as hashed, its environment `{}` until ME-6. -/
def identify (canonical : Json) (claims : List Json) : Except String (String × List String) := do
  let mid ← VE.Route.Wire.meaningId ["calc@0"] (← VE.Route.Wire.environmentId ["calc@0"] (Json.mkObj [])) canonical
  let ids ← claims.mapM fun c =>
    VE.CertificateWire.digest "ve-calc-claim-v0.2:calc@0\n" (Json.mkObj [("meaning_id", .str mid), ("claim", c)])
  pure (mid, ids)

/-- A decoded case with its `meaning_id` and each claim's id. -/
def decode (j : Json) : Except String (Case × String × List String) := do
  checkCase j
  let rule ← match j.getObjVal? "rounding" with
    | .error _ => pure ("ties-up", .tiesUp)
    | .ok (.str r) => match rules.lookup r with
      | some x => pure (r, x)
      | none => throw (invalid "case.rounding" "must be \"ties-up\" or \"half-even\"")
    | .ok _ => throw (invalid "case.rounding" "must be a string")
  let software ← match j.getObjVal? "software" with
    | .error _ => pure none
    | .ok (.str s) => if s == "" then throw (invalid "case.software" "must not be empty") else pure (some s)
    | .ok _ => throw (invalid "case.software" "must be a string")
  let .ok (.arr vs) := j.getObjVal? "values" | throw (invalid "case.values" "must be a list")
  let .ok (.arr cs) := j.getObjVal? "claims" | throw (invalid "case.claims" "must be a list")
  let ps ← match j.getObjVal? "premises" with
    | .error _ => pure #[]
    | .ok (.arr ps) => pure ps
    | .ok _ => throw (invalid "case.premises" "must be a list")
  if cs.size == 0 then throw "NoClaims: a calculation needs at least one claim"
  let (vals, cvals) := (← vs.toList.zipIdx.mapM fun (v, i) => value i v).unzip
  checkVerbalisations vs.toList
  let (premises, cprems) := (← ps.toList.zipIdx.mapM fun (p, i) => premise rule i p).unzip
  let (checks, hashed) := (← cs.toList.zipIdx.mapM fun (c, i) => entry rule premises i c).unzip
  let (claimJson, entryJson) := hashed.unzip
  let ds := vals.map decl
  admit ds premises checks
  let (mid, ids) ← identify (Json.mkObj ([("format", .str "ve-calc@0"), ("values", .arr cvals.toArray),
    ("claims", .arr entryJson.toArray)] ++ (if cprems.isEmpty then [] else [("premises", .arr cprems.toArray)]) ++
    (software.elim [] fun s => [("software", .str s)]))) claimJson
  pure (⟨ds, checks, software⟩, mid, ids)

/-- Decodes `ve-calc@0`: the limits of 3.2 first, then fields, words, names, definition order and literals, then
limit 10 (the case's work within `maxWork`). -/
def decodeCase (j : Json) : Except String Case := do
  let (c, _) ← decode j
  if (c.sidesC Work.maxWork).isNone then throw workLimit
  pure c

theorem decodeCase_decode (j : Json) (c : Case) (h : decodeCase j = .ok c) :
    (∃ m, decode j = .ok (c, m)) ∧ ∃ r, c.sidesC Work.maxWork = some r := by
  unfold decodeCase at h
  cases hd : decode j with
  | error e => rw [hd] at h; cases h
  | ok d =>
    rw [hd] at h
    simp only [bind, Except.bind] at h
    split at h
    · cases h
    · rename_i hs
      cases h
      exact ⟨⟨d.2, rfl⟩, Option.isSome_iff_exists.mp (Option.isSome_iff_ne_none.mpr (by simpa using hs))⟩

end Wire

/-! ## Well-formedness of a decoded case -/

theorem Wire.firstDup_nodup (l : List String) (h : Wire.firstDup l = none) : l.Nodup := by
  induction l with
  | nil => exact List.nodup_nil
  | cons n ns ih =>
    unfold Wire.firstDup at h
    split at h
    · cases h
    · rename_i hn
      exact List.nodup_cons.mpr ⟨fun hm => hn (List.contains_iff_mem.mpr hm), ih h⟩

theorem Wire.firstUnknown_order (known : List String) (ds : List Decl) (h : Wire.firstUnknown known ds = none) :
    ∀ (i : Nat) (hi : i < ds.length) (e : Expr), (ds[i]'hi).source = .defined e →
      ∀ n ∈ e.names, n ∈ known ++ (ds.take i).map Decl.name := by
  induction ds generalizing known with
  | nil => intro i hi; exact absurd hi (Nat.not_lt_zero _)
  | cons d ds ih =>
    unfold Wire.firstUnknown at h
    rw [Option.or_eq_none_iff] at h
    intro i hi e he n hn
    cases i with
    | zero =>
      simp only [List.getElem_cons_zero] at he
      rw [he] at h
      have := List.find?_eq_none.mp h.1 n hn
      simpa using this
    | succ i =>
      have := ih (known ++ [d.name]) h.2 i (by simpa using hi) e (by simpa using he) n hn
      simpa [List.take_succ_cons, List.append_assoc] using this

theorem Wire.decodeCase_wellFormed (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) :
    WellFormed c.decls := by
  obtain ⟨⟨m, hd⟩, _⟩ := Wire.decodeCase_decode j c h
  show WellFormed (c, m).1.decls
  generalize (c, m) = d at hd ⊢
  · obtain ⟨vals, ps, hds, hadm⟩ : ∃ (vals : List (String × Option (Rat ⊕ Expr))) (ps : List (String × Claim)),
        d.1.decls = vals.map Wire.decl ∧ Wire.admit d.1.decls ps d.1.claims = .ok () := by
      unfold Wire.decode at hd
      simp only [bind, Except.bind, pure, Except.pure] at hd
      repeat' split at hd
      all_goals (try cases hd)
      all_goals exact ⟨_, _, rfl, ‹Wire.admit _ _ _ = .ok _›⟩
    unfold Wire.admit at hadm
    dsimp only at hadm
    split at hadm
    · cases hadm
    · cases hadm
    · cases hadm
    · rename_i hn hu _
      rw [Option.or_eq_none_iff] at hu
      refine ⟨Wire.firstDup_nodup _ hn, fun i hi e he n hm => ?_, ?_⟩
      · simpa using Wire.firstUnknown_order [] _ hu.1 i hi e he n hm
      · intro x hx q v hs
        rw [hds] at hx
        obtain ⟨y, _, rfl⟩ := List.mem_map.mp hx
        unfold Wire.decl at hs
        split at hs <;> cases hs

end VE.Calc
