import VE.Calc.Decls
import VE.Route.Wire

/-! The case `ve-calc@0` (math-evidence spec 3.1 to 3.3, ME-2): its limits in order, its decoder and its identity.
This batch decodes claims over stated and defined values. The fields and checks of later batches (`premises`,
`free` and `counted` values, `unit`, `environment`, `source`, `data`, `budget`; `follows`, `consistent`,
`identity` and `sqrt-rounds`) are refused, as unknown fields or as no claim, until their batch adds them. -/

namespace VE.Calc
open Lean VE.Numbers

/-- Every question a `calc@0` case asks (spec 3.4): ME-5, ME-8 and ME-9 add their constructors. -/
inductive Check where
  | claim (c : Claim)

def Check.names : Check → List String
  | .claim c => c.exprs.flatMap Expr.names

structure Case where
  decls : List Decl
  claims : List (String × Check)
  software : Option String

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

/-- The number of JSON values in `j` (objects, arrays and scalars alike) and its nesting of arrays and
objects. -/
def size : Nat → Json → Nat × Nat
  | 0, _ => (0, 0)
  | n + 1, j =>
    let ms := (children j).map (size n)
    (1 + (ms.map (·.1)).sum, if j matches .arr _ | .obj _ then 1 + (ms.map (·.2)).foldl max 0 else 0)

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

/-- Limit 7: a name or claim id of more than 64 bytes. -/
def nameFault (j : Json) : Option String :=
  let long (s : String) : Option String :=
    if s.utf8ByteSize > VE.Limits.maxIdentifierBytes then some (limit "a name" VE.Limits.maxIdentifierBytes) else none
  match j with
  | .arr xs => match xs.toList with
    | [.str "val", .str n] => long n
    | _ => none
  | .obj _ => ["name", "id"].findSome? fun k => match j.getObjVal? k with
    | .ok (.str n) => long n
    | _ => none
  | _ => none

def entries (j : Json) (key : String) : Nat := match j.getObjVal? key with
  | .ok (.arr xs) => xs.size
  | _ => 0

/-- The first limit of 3.2 the case exceeds: 10,000 JSON values, depth 64, 512 values, 512 claims, then
exponents, literals and names, each anywhere in the case. -/
def limitFault (j : Json) : Option String :=
  let (values, depth) := size (VE.Limits.maxJsonDepth + 1) j
  if values > VE.Limits.maxNodes then some (limit "the number of JSON values" VE.Limits.maxNodes)
  else if depth > VE.Limits.maxDepth then some (limit "the JSON depth" VE.Limits.maxDepth)
  else if entries j "values" > 512 then some (limit "the number of values" 512)
  else if entries j "claims" > 512 then some (limit "the number of claims" 512)
  else [exponentFault, literalFault, nameFault].findSome? (scan · 65 j)

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

/-- A value record: its name and its source (stated or defined), and the record as hashed, without `words`. -/
def value (i : Nat) (j : Json) : Except String ((String × (Rat ⊕ Expr)) × Json) := do
  let path := s!"values.{i}"
  checkFields path j ["name", "words"] ["stated", "defined", "support", "span"]
  let .ok (.str name) := j.getObjVal? "name" | throw (invalid s!"{path}.name" "must be a string")
  unless identifier name do throw (invalid s!"{path}.name" "must be a name")
  let .ok (.str _) := j.getObjVal? "words" | throw (invalid s!"{path}.words" "must be a string")
  let (src, cs) ← match j.getObjVal? "stated", j.getObjVal? "defined" with
    | .ok l, .error _ => do
      let p ← literal s!"{path}.stated" l
      pure (Sum.inl p.value, ("stated", Json.str (plain p)))
    | .error _, .ok x => do
      let (x, cx) ← expr s!"{path}.defined" VE.Limits.maxDepth x
      pure (Sum.inr x, ("defined", cx))
    | _, _ => throw (invalid path "must have one of stated and defined")
  pure ((name, src), ← recordJson path j [("name", .str name), cs])

def claimIdChar (c : Char) : Bool := VE.Surface.identChar c || c == '-'

/-- A `claims` entry: its id and check, the claim as hashed and the entry as hashed. -/
def entry (rule : String × Rounding) (i : Nat) (j : Json) : Except String ((String × Check) × Json × Json) := do
  let path := s!"claims.{i}"
  checkFields path j ["id", "claim"] ["span"]
  let .ok (.str id) := j.getObjVal? "id" | throw (invalid s!"{path}.id" "must be a string")
  unless id != "" && id.all claimIdChar do throw (invalid s!"{path}.id" "must be a claim id")
  let (c, cc) ← claim rule s!"{path}.claim" (j.getObjValD "claim")
  pure ((id, .claim c), cc, ← recordJson path j [("id", .str id), ("claim", cc)])

/-! ## Names and definition order -/

def decl (v : String × (Rat ⊕ Expr)) : Decl :=
  ⟨v.1, match v.2 with
    | .inl q => .stated q
    | .inr e => .defined e⟩

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

/-- Names are unique, each name read is declared (before its use in a definition), and claim ids are unique, in
that order. -/
def admit (ds : List Decl) (claims : List (String × Check)) : Except String Unit :=
  let names := ds.map Decl.name
  match firstDup names, (firstUnknown [] ds).or ((claims.flatMap (·.2.names)).find? (!names.contains ·)),
      firstDup (claims.map (·.1)) with
  | some n, _, _ => .error s!"DuplicateName: {n}"
  | none, some n, _ => .error s!"UnknownName: {n} (declare it before the value that uses it)"
  | none, none, some n => .error s!"DuplicateClaimId: {n}"
  | none, none, none => .ok ()

/-! ## The decoder and the identity (3.3) -/

/-- The case's limits, fields and format, before anything else is read. -/
def checkCase (j : Json) : Except String Unit := do
  if let some e := limitFault j then throw e
  checkFields "case" j ["format", "values", "claims"] ["rounding", "software"]
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
  if cs.size == 0 then throw "NoClaims: a calculation needs at least one claim"
  let (vals, cvals) := (← vs.toList.zipIdx.mapM fun (v, i) => value i v).unzip
  let (checks, hashed) := (← cs.toList.zipIdx.mapM fun (c, i) => entry rule i c).unzip
  let (claimJson, entryJson) := hashed.unzip
  let ds := vals.map decl
  admit ds checks
  let (mid, ids) ← identify (Json.mkObj ([("format", .str "ve-calc@0"), ("values", .arr cvals.toArray),
    ("claims", .arr entryJson.toArray)] ++ (software.elim [] fun s => [("software", .str s)]))) claimJson
  pure (⟨ds, checks, software⟩, mid, ids)

/-- Decodes `ve-calc@0`: the limits of 3.2 first, then fields, names, definition order and literals. -/
def decodeCase (j : Json) : Except String Case := (decode j).map (·.1)

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
  unfold Wire.decodeCase at h
  cases hd : Wire.decode j with
  | error e => rw [hd] at h; cases h
  | ok d =>
    rw [hd] at h
    cases h
    obtain ⟨vals, hds, hadm⟩ : ∃ vals : List (String × (Rat ⊕ Expr)),
        d.1.decls = vals.map Wire.decl ∧ Wire.admit d.1.decls d.1.claims = .ok () := by
      unfold Wire.decode at hd
      simp only [bind, Except.bind, pure, Except.pure] at hd
      repeat' split at hd
      all_goals (try cases hd)
      all_goals exact ⟨_, rfl, ‹Wire.admit _ _ = .ok _›⟩
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
