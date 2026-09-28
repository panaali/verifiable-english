import VE.Route.Wire
import VE.Time.Semantics
import VE.Time.Count
import VE.Time.Decimal
import VE.Time.Budget

/-! The `quantity` subcommand of `ve_conformance`: Lean admission of W6a
`ve-units@1` environments and `ve-quantity@1` statements (units-schema §3).

The generic `route` subcommand keeps rejecting extended environments, so raw
erased evidence never reaches a W6 claim. This route decodes the unit schema
and annotated vocabulary, regenerates the literal lowering (`Time.decimal_exact`,
`parseIso`) and the canonical annotated tree `Q`, requires any supplied `Q` to
equal it, admits the statement with the proved `QFormula.admits`, and erases it
(`QFormula.erase`). The frozen order decoder re-checks the regenerated core in
the regenerated target environment, whose identity is recomputed here.

Cases (`kind`): `admission` (default; with an optional `model` it also evaluates
under the Python/Rust budget over each domain in Python/Rust order,
`evalB_sorted_sound`), `countermodel` (the same budget and order,
`refutesB_sorted_sound`), `certificate` (a `ve-quantity-certificate@1` wrapping an order
certificate for the regenerated problem; see `checkW6Certificate_sound`),
`count` (the canonical counting expansion), and the conversions `day`,
`civil`, `lower`, `render` used by the differential tests. -/
namespace VE.Time.Wire
universe v
open Lean
open VE.Bridge (exactFields fields stringField strings identifier)
open VE.Order.ProfileGate (bind_ok)

def language : String := "ve.core@0.2"
def specRevision : String := "ve-v0.2-expand2-2026-09-25"
def schema : String := "ve-units@1"
def w6Profiles : List (List String) :=
  [["order@0", "relational-fol@0", "time@0"],
   ["documents@1", "order@0", "relational-fol@0", "time@0"]]
def numbers2 : String :=
  "UnsupportedProfile: $int quantification requires the missing numbers2 route"
def depthLimit : String := "ResourceLimit: Quantity AST exceeds node or depth limit"

inductive Display where
  | percent
  | money (currency : String) (symbol : Option String)
  | decimal (label : String) (isPrefix : Bool)
  | isoDate

structure UnitDecl where
  tag : String
  places : Nat
  display : Display

/-- A decoded W6 vocabulary with tagged signatures. -/
structure QVocab where
  sorts : List String
  units : List UnitDecl
  predicates : List (String × List QType)
  constants : List (String × QType)

def QVocab.env (v : QVocab) : QEnv :=
  ⟨v.sorts, v.units.map UnitDecl.tag, VE.Order.lookup v.predicates, VE.Order.lookup v.constants⟩

/-- The erased order vocabulary handed to the frozen checker. -/
def QVocab.core (v : QVocab) : VE.Order.Vocabulary :=
  ⟨v.sorts, v.predicates.map (fun p => (p.1, p.2.map QType.erase)),
    v.constants.map (fun c => (c.1, c.2.erase))⟩

theorem lookup_map {β γ : Type} (f : β → γ) (xs : List (String × β)) (k : String) :
    VE.Order.lookup (xs.map (fun p => (p.1, f p.2))) k = (VE.Order.lookup xs k).map f := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    by_cases h : x.1 = k
    · simp [VE.Order.lookup, h]
    · have hb : (x.1 == k) = false := beq_eq_false_iff_ne.mpr h
      simp only [VE.Order.lookup, List.map_cons, List.find?_cons, hb] at ih ⊢
      exact ih

/-- The checker's environment is exactly the erasure of the admitted one. -/
theorem QVocab.core_environment (v : QVocab) : v.core.environment = v.env.erase := by
  unfold QVocab.core QVocab.env QEnv.erase VE.Order.Vocabulary.environment
  congr 1
  · funext p; exact lookup_map (List.map QType.erase) v.predicates p
  · funext c; exact lookup_map QType.erase v.constants c

/-! ## Environment admission -/

/-- The characters for which Python's `str.isspace()` holds. -/
def isSpace (c : Char) : Bool :=
  let n := c.toNat
  (9 ≤ n && n ≤ 13) || (28 ≤ n && n ≤ 32) || n == 0x85 || n == 0xA0 || n == 0x1680 ||
    (0x2000 ≤ n && n ≤ 0x200A) || n == 0x2028 || n == 0x2029 || n == 0x202F || n == 0x205F ||
    n == 0x3000

/-- Nonempty words joined by single spaces; an input symbol may end in one space. -/
def displayString (s : String) (trailing : Bool) (what := "Display string") :
    Except String Unit := do
  if s.isEmpty then throw s!"{what} must be nonempty"
  if s.length > 256 then throw s!"ResourceLimit: {what} exceeds 256 characters"
  let words := s.splitOn " "
  let words := if trailing && words.length > 1 && words.getLast? == some "" then words.dropLast
    else words
  if words.any (fun w => w.isEmpty || w.any isSpace) then
    throw s!"{what} {s.quote} must be whitespace-normalized"

/-- The sentence-initial spelling of a name: its first letter ASCII-uppercased. -/
def sentenceInitial (s : String) : String :=
  match s.toList with
  | c :: cs => String.mk (c.toUpper :: cs)
  | [] => s

/-- Constant names survive sentence normalization, and no two share a spelling,
even when one starts a sentence, so a rendered name reads back as itself. -/
def checkVerbalisations (constants : List (String × Json)) : Except String Unit := do
  let mut seen : List (String × String) := []
  for (c, entry) in constants do
    if let .ok words := entry.getObjVal? "verbalisation" then
      let w ← words.getStr?
      displayString w false "Verbalisation"
      let key := sentenceInitial w
      if let some (_, other) := seen.find? (·.1 == key) then
        throw s!"VerbalisationCollision({other}, {c})"
      seen := (key, c) :: seen

def shape (j : Json) (required optional : List String) : Except String Unit := do
  let names := (← fields j).map Prod.fst
  unless required.all names.contains &&
      names.all (fun n => required.contains n || optional.contains n) do
    throw s!"fields do not match: required {required}, optional {optional}, got {names}"

def canonicalText (j : Json) : Except String String := VE.CertificateWire.canonical 257 j

def reservedDay : Json :=
  Json.mkObj [("scale", .str "1"), ("display", Json.mkObj [("kind", .str "iso_date")])]
def reservedElapsed : Json :=
  Json.mkObj [("scale", .str "1"),
    ("display", Json.mkObj [("kind", .str "decimal"), ("label", .str "days")])]

/-- A positive power of ten, spelled canonically; returns its exponent. -/
def decodeScale (tag : String) (j : Json) : Except String Nat := do
  let s ← j.getStr?
  let _ ← VE.Order.Wire.decodeInt s
  match s.toList with
  | '1' :: zeros =>
    if zeros.all (· == '0') then pure zeros.length
    else throw s!"UnitScale({tag}): expected a positive power of ten"
  | _ => throw s!"UnitScale({tag}): expected a positive power of ten"

def decodeUnit (tag : String) (record : Json) : Except String UnitDecl := do
  unless identifier tag && tag != dimensionless do throw s!"Invalid unit tag {tag.quote}"
  exactFields record ["scale", "display"]
  let places ← decodeScale tag (← record.getObjVal? "scale")
  let display ← record.getObjVal? "display"
  let kind ← match display.getObjVal? "kind" with
    | .ok k => k.getStr?
    | .error _ => throw s!"Invalid display for {tag}"
  let decoded ← match kind with
    | "percent" => do exactFields display ["kind"]; pure Display.percent
    | "money" => do
      shape display ["kind", "currency"] ["input_symbol"]
      let currency ← stringField display "currency"
      unless currency.length == 3 && currency.all (fun c => 'A' ≤ c && c ≤ 'Z') do
        throw s!"Invalid currency for {tag}"
      match display.getObjVal? "input_symbol" with
      | .ok symbol => do
        let s ← symbol.getStr?
        displayString s true
        pure (Display.money currency (some s))
      | .error _ => pure (Display.money currency none)
    | "decimal" => do
      shape display ["kind", "label"] ["placement"]
      let label ← stringField display "label"
      displayString label false
      let placement ← match display.getObjVal? "placement" with
        | .ok p => p.getStr?
        | .error _ => pure "suffix"
      unless placement == "prefix" || placement == "suffix" do throw s!"Invalid placement for {tag}"
      pure (Display.decimal label (placement == "prefix"))
    | "iso_date" => do
      exactFields display ["kind"]
      unless tag == dayTag && places == 0 do throw "iso_date requires day at scale 1"
      pure Display.isoDate
    | other => throw s!"Unknown display kind {other}"
  if tag == dayTag && (← canonicalText record) != (← canonicalText reservedDay) then
    throw "Reserved unit day has a fixed declaration"
  if tag == elapsedTag && (← canonicalText record) != (← canonicalText reservedElapsed) then
    throw "Reserved unit elapsed_day has a fixed declaration"
  pure ⟨tag, places, decoded⟩

def pointsSuffix : String := " percentage points"

/-- Every enabled literal affix, canonical or alias: (is prefix, text). -/
def affixes (units : List UnitDecl) : List (Bool × String) :=
  units.flatMap fun u => match u.display with
    | .percent => [(false, "%"), (false, pointsSuffix)]
    | .money c none => [(true, c ++ " ")]
    | .money c (some s) => [(true, c ++ " "), (true, s)]
    | .decimal l true => [(true, l ++ " ")]
    | .decimal l false => [(false, " " ++ l)]
    | .isoDate => []

def amountChar (c : Char) : Bool := c == '-' || c == '.' || c.isDigit

/-- No affix touches the amount, and none extends another on its side. -/
def displayInjective (units : List UnitDecl) : Except String Unit := do
  let forms := affixes units
  for (isPrefix, text) in forms do
    let edge := if isPrefix then text.toList.head? else text.toList.getLast?
    if edge.any amountChar then throw s!"DisplayCollision({text.quote} touches the amount)"
  let rec go : List (Bool × String) → Except String Unit
    | [] => pure ()
    | (p, a) :: rest => do
      for (q, b) in rest do
        if p == q && (if p then a.startsWith b || b.startsWith a else a.endsWith b || b.endsWith a) then
          throw s!"DisplayCollision({a.quote}, {b.quote})"
      go rest
  go forms

/-- A decoded, admitted W6 environment and its regenerated target. -/
structure W6Env where
  profiles : List String
  vocab : QVocab
  target : Json
  environmentId : String
  targetId : String

def dropFields (j : Json) (names : List String) : Except String Json := do
  pure (Json.mkObj ((← fields j).filter (fun p => !names.contains p.1)))

/-- The core target environment: W6 declaration fields removed, nothing else. -/
def eraseEnvironment (env : Json) : Except String Json := do
  let vocabulary ← env.getObjVal? "vocabulary"
  let predicates ← (← fields (← vocabulary.getObjVal? "predicates")).mapM fun (p, entry) => do
    pure (p, ← dropFields entry ["argument_units"])
  let constants ← (← fields (← vocabulary.getObjVal? "constants")).mapM fun (c, entry) => do
    pure (c, ← dropFields entry ["unit", "verbalisation"])
  let vocabulary := Json.mkObj [("sorts", vocabulary.getObjValD "sorts"),
    ("predicates", Json.mkObj predicates), ("constants", Json.mkObj constants)]
  let base ← dropFields env ["unit_schema", "units", "vocabulary"]
  pure (Json.mkObj (((← fields base)) ++ [("vocabulary", vocabulary)]))

def decodeSlot (args : List String) (validTag : String → Bool) (slot : String) (t : Json) :
    Except String (Nat × String) := do
  let some i := slot.toNat? | throw s!"Invalid argument unit slot {slot}"
  unless toString i == slot && i < args.length do throw s!"Invalid argument unit slot {slot}"
  unless args[i]? == some "$int" do throw s!"Unit on non-integer slot {slot}"
  let tag ← t.getStr?
  unless validTag tag do throw s!"UnknownUnit({tag})"
  pure (i, tag)

def decodeSlots (args : List String) (validTag : String → Bool) (entry : Json) :
    Except String (List (Nat × String)) :=
  match entry.getObjVal? "argument_units" with
  | .ok m => match fields m with
    | .ok ms => ms.mapM fun (slot, t) => decodeSlot args validTag slot t
    | .error _ => .error "argument_units must be an object"
  | .error _ => .ok []

def decodeEnvironment (env : Json) : Except String W6Env := do
  exactFields env ["language", "profiles", "spec_revision", "vocabulary", "unit_schema", "units"]
  unless (← stringField env "language") == language do
    throw "UnsupportedProfile: quantity route requires ve-units@1 on ve.core@0.2"
  let profiles ← strings (← env.getObjVal? "profiles")
  unless w6Profiles.contains profiles do
    throw "UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1"
  unless (← stringField env "spec_revision") == specRevision do
    throw "UnsupportedProfile: Unsupported specification revision"
  unless (← stringField env "unit_schema") == schema do
    throw "UnsupportedProfile: Unsupported unit schema"
  let unitFields ← match env.getObjVal? "units" >>= fields with
    | .ok fs => pure fs
    | .error _ => throw "units must be an object"
  if unitFields.length > 64 then throw "ResourceLimit: At most 64 unit tags"
  let units ← unitFields.mapM fun (tag, record) => decodeUnit tag record
  displayInjective units
  let tags := units.map UnitDecl.tag
  let validTag := fun (t : String) => t == dimensionless || tags.contains t
  let vocabulary ← env.getObjVal? "vocabulary"
  exactFields vocabulary ["sorts", "predicates", "constants"]
  let sortNames := (← fields (← vocabulary.getObjVal? "sorts")).map Prod.fst
  for tag in dimensionless :: tags do
    if sortNames.contains tag then throw s!"Unit tag {tag} collides with a declared sort"
  let constantFields ← fields (← vocabulary.getObjVal? "constants")
  for (_, entry) in constantFields do
    if entry.getObjValD "sort" == .str "$string" then
      throw "UnsupportedProfile: $string literals are not admitted with ve-units@1"
  let predicates ← (← fields (← vocabulary.getObjVal? "predicates")).mapM fun (p, entry) => do
    let args ← strings (← entry.getObjVal? "arguments")
    let slots ← decodeSlots args validTag entry
    let types := args.mapIdx fun i s =>
      if s == "$int" then QType.qty (((slots.find? (·.1 == i)).map Prod.snd).getD dimensionless)
      else QType.obj s
    pure (p, types)
  let constants ← constantFields.mapM fun (c, entry) => do
    let sort ← stringField entry "sort"
    let tag ← match entry.getObjVal? "unit" with
      | .ok u => do
        unless sort == "$int" do throw s!"Unit on non-integer constant {c}"
        let t ← u.getStr?
        unless validTag t do throw s!"UnknownUnit({t})"
        pure t
      | .error _ => pure dimensionless
    pure (c, if sort == "$int" then QType.qty tag else QType.obj sort)
  checkVerbalisations constantFields
  let target ← eraseEnvironment env
  -- Every legacy declaration rule is the frozen order decoder's, on the target.
  let _ ← VE.Route.Wire.decodeOrderVocabulary (← target.getObjVal? "vocabulary")
  pure ⟨profiles, ⟨sortNames, units, predicates, constants⟩, target,
    ← VE.Route.Wire.environmentId profiles env, ← VE.Route.Wire.environmentId profiles target⟩

/-! ## Statement elaboration: decode, lower literals, infer tags -/

def describeType : QType → String
  | .obj s => s!"sort {s}"
  | .qty g => s!"unit {g}"

def same (a b : QType) : Except String Unit :=
  if a == b then pure () else match a, b with
    | .qty x, .qty y => throw s!"TypeMismatch: UnitMismatch({x},{y})"
    | _, _ => throw s!"TypeMismatch: TypeMismatch({describeType a},{describeType b})"

def QVocab.tag (v : QVocab) (t : String) : Except String String :=
  if t == dimensionless || (v.units.map UnitDecl.tag).contains t then pure t
  else throw s!"UnknownUnit({t})"

def QVocab.places (v : QVocab) (t : String) : Nat :=
  ((v.units.find? (·.tag == t)).map UnitDecl.places).getD 0

def QVocab.constant (v : QVocab) (c : String) : Except String QType :=
  match VE.Order.lookup v.constants c with
  | some τ => pure τ
  | none => throw s!"Unknown constant {c.quote}"

def integer (s : String) : Except String Int := VE.Order.Wire.decodeInt s

/-- Terms: depth is counted from each atom, separately from formula depth. -/
def elabTerm (v : QVocab) (ctx : List String) : Nat → Json → Except String (QType × QTerm)
  | 0, _ => throw depthLimit
  | fuel + 1, j => do
    let items ← match j.getArr? with
      | .ok xs => pure xs.toList
      | .error _ => throw "Invalid quantity term"
    match items with
    | [.str "var", i] =>
      let n ← match i.getNat? with
        | .ok n => pure n
        | .error _ => throw "Unbound variable"
      match ctx[n]? with
      | some s => pure (.obj s, .var n)
      | none => throw s!"Unbound variable {n}"
    | [.str "var", _, _] => throw numbers2
    | [.str "const", .str name] => do
      match ← v.constant name with
      | .obj s => pure (.obj s, .obj name)
      | .qty g => do same (.qty dimensionless) (.qty g); pure (.qty dimensionless, .const dimensionless name)
    | [.str "const", .str tag, .str name] => do
      match ← v.constant name with
      | .obj _ => throw s!"TypeMismatch: Unit on object constant {name}"
      | .qty g => do
        let t ← v.tag tag
        same (.qty t) (.qty g)
        pure (.qty t, .const t name)
    | [.str "num", .str z] => pure (.qty dimensionless, .num dimensionless (← integer z))
    | [.str "num", .str tag, .str z] => do
      let t ← v.tag tag
      pure (.qty t, .num t (← integer z))
    | [.str "decimal", .str tag, .str text] => do
      let t ← v.tag tag
      let d ← parseDecimal text
      match lower d (v.places t) with
      | some q =>
        if (toString q).length > 40 then throw "ResourceLimit: Lowered integer exceeds 40 characters"
        pure (.qty t, .num t q)
      | none => throw s!"UnitPrecision({t}, scale={10 ^ v.places t})"
    | [.str "date", .str text] => do
      let t ← v.tag dayTag
      let D ← parseIso text
      pure (.qty t, .num t D.num)
    | [.str "add", l, r] => addTerm dimensionless l r fuel
    | [.str "add", .str tag, l, r] => do addTerm (← v.tag tag) l r fuel
    | [.str "scale", .str c, u] => scaleTerm dimensionless c u fuel
    | [.str "scale", .str tag, .str c, u] => do scaleTerm (← v.tag tag) c u fuel
    | _ => throw "Invalid quantity term"
where
  addTerm (tag : String) (l r : Json) (fuel : Nat) : Except String (QType × QTerm) := do
    let (lt, lq) ← elabTerm v ctx fuel l
    let (rt, rq) ← elabTerm v ctx fuel r
    same lt rt
    same (.qty tag) lt
    if tag == dayTag then throw "TypeMismatch: Calendar dates cannot be added"
    pure (.qty tag, .add tag lq rq)
  scaleTerm (tag c : String) (u : Json) (fuel : Nat) : Except String (QType × QTerm) := do
    let k ← integer c
    let (ut, uq) ← elabTerm v ctx fuel u
    same (.qty tag) ut
    if tag == dayTag then throw "TypeMismatch: Calendar dates cannot be scaled"
    pure (.qty tag, .scale tag k uq)

def w6b : List String :=
  ["sunday", "excluded_sundays", "forall_date", "exists_date", "trace_all", "trace_some"]

def elabFormula (v : QVocab) : Nat → List String → Json → Except String QFormula
  | 0, _, _ => throw depthLimit
  | fuel + 1, ctx, j => do
    let term := elabTerm v ctx 64
    let day := fun (τ : QType) => do same τ (.qty (← v.tag dayTag))
    let items ← match j.getArr? with
      | .ok xs => pure xs.toList
      | .error _ => throw "Invalid quantity formula"
    match items with
    | [.str "top"] => pure .top
    | [.str "bottom"] => pure .bottom
    | [.str "eq", t, u] => do
      let (a, tq) ← term t
      let (b, uq) ← term u
      same a b
      pure (.eq tq uq)
    | [.str "lt", t, u] => do
      let (a, tq) ← term t
      let (b, uq) ← term u
      same a b
      unless a matches .qty _ do throw "TypeMismatch: Order needs quantity terms"
      pure (.lt tq uq)
    | [.str "le", t, u] => do
      let (a, tq) ← term t
      let (b, uq) ← term u
      same a b
      unless a matches .qty _ do throw "TypeMismatch: Order needs quantity terms"
      pure (.le tq uq)
    | [.str "unary", .str p, t] => do
      let some [s] := VE.Order.lookup v.predicates p | throw s!"Unknown predicate or arity {p}"
      let (a, tq) ← term t
      same a s
      pure (.unary p tq)
    | [.str "binary", .str p, t, u] => do
      let some [s, r] := VE.Order.lookup v.predicates p | throw s!"Unknown predicate or arity {p}"
      let (a, tq) ← term t
      let (b, uq) ← term u
      same a s
      same b r
      pure (.binary p tq uq)
    | .str "atom" :: _ =>
      throw "UnsupportedProfile: n-ary atoms are not admitted on the order@0 quantity route"
    | [.str "not", a] => pure (.not (← elabFormula v fuel ctx a))
    | [.str "and", a, b] => pure (.and (← elabFormula v fuel ctx a) (← elabFormula v fuel ctx b))
    | [.str "or", a, b] => pure (.or (← elabFormula v fuel ctx a) (← elabFormula v fuel ctx b))
    | [.str "implies", a, b] =>
      pure (.implies (← elabFormula v fuel ctx a) (← elabFormula v fuel ctx b))
    | [.str "forall", .str "$int", _] | [.str "forall", .str "$int", _, _]
    | [.str "exists", .str "$int", _] | [.str "exists", .str "$int", _, _] => throw numbers2
    | [.str "forall", .str s, a] => do
      unless v.sorts.contains s do throw "Invalid quantity binder"
      pure (.all s (← elabFormula v fuel (s :: ctx) a))
    | [.str "exists", .str s, a] => do
      unless v.sorts.contains s do throw "Invalid quantity binder"
      pure (.ex s (← elabFormula v fuel (s :: ctx) a))
    | [.str "date_on", t, d] => do
      let (a, tq) ← term t; let (b, dq) ← term d; day a; day b; pure (.dateOn tq dq)
    | [.str "date_before", t, d] => do
      let (a, tq) ← term t; let (b, dq) ← term d; day a; day b; pure (.dateBefore tq dq)
    | [.str "date_after", t, d] => do
      let (a, tq) ← term t; let (b, dq) ← term d; day a; day b; pure (.dateAfter tq dq)
    | [.str "date_no_later", t, d] => do
      let (a, tq) ← term t; let (b, dq) ← term d; day a; day b; pure (.dateNoLater tq dq)
    | [.str "within_days", t, d, n] => do
      let (a, tq) ← term t; let (b, dq) ← term d; day a; day b
      pure (.within tq dq (← offset n))
    | [.str "shift_days", t, d, n] => do
      let (a, tq) ← term t; let (b, dq) ← term d; day a; day b
      pure (.shift tq dq (← offset n))
    | [.str "elapsed_days", d, t, w] => do
      let (a, dq) ← term d; let (b, tq) ← term t; day a; day b
      let (c, wq) ← term w
      same c (.qty (← v.tag elapsedTag))
      pure (.elapsed dq tq wq)
    | .str op :: _ =>
      if ["date_on", "date_before", "date_after", "date_no_later", "within_days", "shift_days",
          "elapsed_days"].contains op then throw s!"Invalid {op} node"
      else if w6b.contains op then throw numbers2
      else if ["forall", "exists"].contains op then throw "Invalid quantity binder"
      else throw s!"Unknown quantity formula {op}"
    | _ => throw "Invalid quantity formula"
where
  offset (n : Json) : Except String Nat := do
    let z ← integer (← n.getStr?)
    if z < 0 then throw "Day offset must be nonnegative"
    pure z.toNat

/-- Array nodes, as Python counts them (at most 10,000). -/
def jsonNodes : Nat → Json → Nat
  | 0, _ => 0
  | fuel + 1, .arr xs => 1 + (xs.toList.map (jsonNodes fuel)).foldl (· + ·) 0
  | _, _ => 0

/-! ## Encodings -/

def encTerm : QTerm → Json
  | .var i => Json.arr #[.str "var", toJson i]
  | .obj c => Json.arr #[.str "const", .str c]
  | .num g z => Json.arr #[.str "num", .str g, .str (toString z)]
  | .const g c => Json.arr #[.str "const", .str g, .str c]
  | .add g l r => Json.arr #[.str "add", .str g, encTerm l, encTerm r]
  | .scale g k t => Json.arr #[.str "scale", .str g, .str (toString k), encTerm t]

def encQ : QFormula → Json
  | .top => Json.arr #[.str "top"]
  | .bottom => Json.arr #[.str "bottom"]
  | .unary p t => Json.arr #[.str "unary", .str p, encTerm t]
  | .binary p t u => Json.arr #[.str "binary", .str p, encTerm t, encTerm u]
  | .eq t u => Json.arr #[.str "eq", encTerm t, encTerm u]
  | .lt t u => Json.arr #[.str "lt", encTerm t, encTerm u]
  | .le t u => Json.arr #[.str "le", encTerm t, encTerm u]
  | .not a => Json.arr #[.str "not", encQ a]
  | .and a b => Json.arr #[.str "and", encQ a, encQ b]
  | .or a b => Json.arr #[.str "or", encQ a, encQ b]
  | .implies a b => Json.arr #[.str "implies", encQ a, encQ b]
  | .all s a => Json.arr #[.str "forall", .str s, encQ a]
  | .ex s a => Json.arr #[.str "exists", .str s, encQ a]
  | .dateOn t d => Json.arr #[.str "date_on", encTerm t, encTerm d]
  | .dateBefore t d => Json.arr #[.str "date_before", encTerm t, encTerm d]
  | .dateAfter t d => Json.arr #[.str "date_after", encTerm t, encTerm d]
  | .dateNoLater t d => Json.arr #[.str "date_no_later", encTerm t, encTerm d]
  | .within t d n => Json.arr #[.str "within_days", encTerm t, encTerm d, .str (toString n)]
  | .shift t d n => Json.arr #[.str "shift_days", encTerm t, encTerm d, .str (toString n)]
  | .elapsed d t v => Json.arr #[.str "elapsed_days", encTerm d, encTerm t, encTerm v]

def encCoreTerm : VE.Order.Term → Json
  | .var i => Json.arr #[.str "var", toJson i]
  | .const c => Json.arr #[.str "const", .str c]
  | .num z => Json.arr #[.str "num", .str (toString z)]
  | .add t u => Json.arr #[.str "add", encCoreTerm t, encCoreTerm u]
  | .scale k t => Json.arr #[.str "scale", .str (toString k), encCoreTerm t]

def encCore : VE.Order.Formula → Json
  | .top => Json.arr #[.str "top"]
  | .bottom => Json.arr #[.str "bottom"]
  | .unary p t => Json.arr #[.str "unary", .str p, encCoreTerm t]
  | .binary p t u => Json.arr #[.str "binary", .str p, encCoreTerm t, encCoreTerm u]
  | .eq t u => Json.arr #[.str "eq", encCoreTerm t, encCoreTerm u]
  | .lt t u => Json.arr #[.str "lt", encCoreTerm t, encCoreTerm u]
  | .le t u => Json.arr #[.str "le", encCoreTerm t, encCoreTerm u]
  | .not a => Json.arr #[.str "not", encCore a]
  | .and a b => Json.arr #[.str "and", encCore a, encCore b]
  | .or a b => Json.arr #[.str "or", encCore a, encCore b]
  | .implies a b => Json.arr #[.str "implies", encCore a, encCore b]
  | .all s a => Json.arr #[.str "forall", .str s, encCore a]
  | .ex s a => Json.arr #[.str "exists", .str s, encCore a]

/-! ## Admission of one quantity object -/

/-- An admitted statement with its regenerated artifacts and identities. -/
structure Admission (w : W6Env) where
  formula : QFormula
  admitted : formula.admits w.vocab.env [] = true
  Q : Json
  core : Json
  meaningId : String
  coreId : String

def decodeQuantity (w : W6Env) (p : Json) : Except String (Admission w) := do
  shape p ["format", "formula"] ["traces", "Q"]
  unless p.getObjValD "format" == .str "ve-quantity@1" do throw "Unsupported quantity format"
  if let .ok traces := p.getObjVal? "traces" then
    let items ← match traces.getArr? with
      | .ok xs => pure xs
      | .error _ => throw "traces must be an array"
    unless items.isEmpty do
      throw "UnsupportedProfile: trace declarations require the missing numbers2 route"
  let source ← p.getObjVal? "formula"
  if jsonNodes 257 source > 10000 then throw depthLimit
  let formula ← elabFormula w.vocab 64 [] source
  let q := encQ formula
  if let .ok claimed := p.getObjVal? "Q" then
    let same ← match canonicalText claimed with
      | .ok text => pure (text == (← canonicalText q))
      | .error _ => pure false
    unless same do throw "Quantity Q differs from regenerated formula"
  if h : formula.admits w.vocab.env [] = true then
    let core := encCore formula.erase
    -- The frozen decoder re-checks the regenerated core in the target vocabulary.
    let _ ← VE.Order.Wire.decodeFormulas w.vocab.core.environment (Json.arr #[core])
    let canonical := Json.mkObj [("format", .str "ve-quantity@1"), ("formula", q),
      ("traces", Json.arr #[])]
    pure ⟨formula, h, q, core, ← VE.Route.Wire.meaningId w.profiles w.environmentId canonical,
      ← VE.Route.Wire.meaningId w.profiles w.targetId core⟩
  else throw "TypeMismatch: statement is not admitted"

/-- Every admitted statement satisfies the independent admission relation, and
its core is well typed in the erased environment. -/
theorem Admission.sound {w : W6Env} (a : Admission w) :
    Admitted w.vocab.env [] a.formula ∧
      a.formula.erase.WellFormed w.vocab.env.erase [] :=
  ⟨units_admit_sound _ _ _ a.admitted, erase_wellTyped (units_admit_sound _ _ _ a.admitted)⟩

/-! ## Static limits of a problem -/

def aggregateLimit : String :=
  "ResourceLimit: premises and conclusion exceed aggregate 10000-node limit"

/-- The static limits of a quantity problem, after each statement's own limits
(`decodeQuantity`: 10,000 source nodes, formula and term depth 64, the frozen
core decoder) and before any model is decoded, any certificate is read or
anything is evaluated: the regenerated cores of the premises and conclusion
together have at most 10,000 formula and term nodes (Python
`check_quantity_limits`, Rust `quantity_limits`, in this order). -/
def quantityLimits {w : W6Env} (ps : List (Admission w)) (c : Admission w) :
    Except String Unit :=
  if ((c :: ps).map (VE.Order.Wire.formulaNodes ·.formula.erase)).foldl (· + ·) 0 > 10000 then
    .error aggregateLimit
  else .ok ()

/-! ## Certificates -/

structure W6Certificate where
  environmentId : String
  premiseIds : List String
  conclusionId : String
  core : VE.Order.Tableau.Certificate

def decodeW6CertificateFields (j : Json) : Except String W6Certificate := do
  exactFields j ["format", "environment_id", "premise_meaning_ids", "conclusion_meaning_id", "core"]
  unless (← stringField j "format") == "ve-quantity-certificate@1" do
    throw "Unsupported quantity certificate format"
  pure ⟨← stringField j "environment_id", ← strings (← j.getObjVal? "premise_meaning_ids"),
    ← stringField j "conclusion_meaning_id",
    ← VE.Order.Wire.decodeCertificate (← j.getObjVal? "core")⟩

/-- A raw order certificate, or any other object, is not W6 evidence. -/
def decodeW6Certificate (j : Json) : Except String W6Certificate :=
  match decodeW6CertificateFields j with
  | .ok c => .ok c
  | .error e => .error s!"Invalid quantity certificate: {e}"

/-- The problem's static limits, the outer binding to the annotated statements,
the inner binding to their regenerated core problem, then the frozen order
replay. Documents check lemmas and graph edges here, so an oversized problem is
never established there either. -/
def checkW6Certificate {w : W6Env} (ps : List (Admission w)) (c : Admission w)
    (cert : W6Certificate) : Except String Bool :=
  if (quantityLimits ps c).isOk = false then .error aggregateLimit
  else if !(cert.environmentId == w.environmentId && cert.premiseIds == ps.map (·.meaningId) &&
      cert.conclusionId == c.meaningId) then
    .error "W6 certificate is stale or bound to different annotated statements"
  else if !(cert.core.environment_id == w.targetId &&
      cert.core.premise_meaning_ids == ps.map (·.coreId) &&
      cert.core.conclusion_meaning_id == c.coreId) then
    .error "core certificate is stale or bound to a different regenerated problem"
  else .ok (VE.Order.Tableau.checkCertificate w.vocab.core.environment (ps.map (·.formula.erase))
    c.formula.erase cert.core)

/-- **W6 composed certificate soundness.** An accepted certificate is bound to
exactly the submitted annotated statements (their quantity meaning ids and the
annotated environment), and they are entailed in the direct tagged semantics
over every admissible tagged structure. Raw erased evidence has no outer binding
and a retagged statement has a different meaning id, so neither is accepted. -/
theorem checkW6Certificate_sound {w : W6Env} (ps : List (Admission w)) (c : Admission w)
    (cert : W6Certificate) (h : checkW6Certificate ps c cert = .ok true) :
    cert.environmentId = w.environmentId ∧ cert.premiseIds = ps.map (·.meaningId) ∧
      cert.conclusionId = c.meaningId ∧
      TEntails.{v} w.vocab.env (ps.map (·.formula)) c.formula := by
  unfold checkW6Certificate at h
  split at h
  · cases h
  split at h
  · cases h
  · rename_i hb
    split at h
    · cases h
    · simp only [Bool.not_eq_true', Bool.not_eq_false, Bool.and_eq_true, beq_iff_eq] at hb
      have hv := Except.ok.inj h
      refine ⟨hb.1.1, hb.1.2, hb.2, ?_⟩
      have hent := VE.Order.Tableau.checkCertificate_sound.{v} _ _ _ _ hv
      rw [QVocab.core_environment] at hent
      apply tentails_of_entails
      · intro a ha
        obtain ⟨b, _, rfl⟩ := List.mem_map.mp ha
        exact units_admit_sound _ _ _ b.admitted
      · exact units_admit_sound _ _ _ c.admitted
      · simpa [List.map_map] using hent

/-! ## The runner -/

/-- UNKNOWN: evaluation stopped at the Python/Rust budget, never a truth value. -/
def budgetExhausted : String :=
  "ResourceLimit: formula-node evaluation budget MAX_EVALUATIONS=1000000 exhausted"

/-- Each submitted domain in Python `sorted` and Rust `sort` order (local
identifiers are ASCII, so code-point, byte and `String` order agree). `evalB`
stops at the first decisive entity, so its work, and whether the budget runs
out, depends on this order; values never do (`eval_domains_perm`). -/
def sortDomains (d : VE.Order.ModelData VE.Order.Wire.Entity) :
    VE.Order.ModelData VE.Order.Wire.Entity :=
  { d with domains := d.domains.map fun p => (p.1, p.2.mergeSort fun a b => decide (a.2 ≤ b.2)) }

theorem sortDomains_perm (d : VE.Order.ModelData VE.Order.Wire.Entity) (s : String) :
    ((sortDomains d).toModel.domains s).Perm (d.toModel.domains s) := by
  simp only [sortDomains, VE.Order.ModelData.toModel,
    lookup_map (fun xs : List VE.Order.Wire.Entity => xs.mergeSort fun a b => decide (a.2 ≤ b.2))]
  cases VE.Order.lookup d.domains s <;> simp [List.mergeSort_perm]

/-- A budgeted value on the sorted presentation is the reference value on the
submitted model. -/
theorem evalB_sorted_sound (d : VE.Order.ModelData VE.Order.Wire.Entity) (limit : Nat)
    (f : VE.Order.Formula) (w : Nat) (r : Bool × Nat)
    (h : evalB (sortDomains d).toModel limit [] f w = some r) : r.1 = f.eval d.toModel [] := by
  rw [evalB_sound (sortDomains d).toModel limit f [] w r h]
  exact eval_domains_perm (sortDomains d).toModel d.toModel rfl rfl (sortDomains_perm d) f []

/-- A budgeted countermodel verdict on the sorted presentation is the reference
verdict on the submitted model. -/
theorem refutesB_sorted_sound (d : VE.Order.ModelData VE.Order.Wire.Entity) (limit : Nat)
    (ps : List VE.Order.Formula) (c : VE.Order.Formula) (w : Nat) (b : Bool)
    (h : refutesB (sortDomains d).toModel limit ps c w = some b) :
    b = VE.Order.countermodelCheck d.toModel ps c := by
  rw [refutesB_sound (sortDomains d).toModel limit ps c w b h]
  exact countermodelCheck_domains_perm (sortDomains d).toModel d.toModel rfl rfl
    (sortDomains_perm d) ps c

def ok (id : String) (fs : List (String × Json)) : Json :=
  Json.mkObj ([("id", .str id), ("status", .str "ok")] ++ fs)

def admissions (w : W6Env) (j : Json) : Except String (List (Admission w)) := do
  (← j.getArr?).toList.mapM (decodeQuantity w)

def countBody (w : W6Env) (sort : String) (j : Json) : Except String VE.Order.Formula := do
  let body ← VE.Order.Wire.decodeFormula 64 j
  unless body.check w.vocab.core.environment [.user sort] do throw "ill-typed counting body"
  pure body

def runCount (w : W6Env) (id : String) (j : Json) : Except String Json := do
  let mode ← stringField j "mode"
  let sort ← stringField j "sort"
  if sort == "$int" then throw numbers2
  unless w.vocab.sorts.contains sort do throw s!"Unknown counting sort {sort}"
  let n ← (← j.getObjVal? "n").getNat?
  let expansion ← match mode with
    | "at_least" => do
      if n > 8 then throw "CountingBound(at least 8)"
      pure (atLeast sort n (← countBody w sort (← j.getObjVal? "body")))
    | "exactly" => do
      if n > 7 then throw "CountingBound(exactly 7)"
      pure (exactly sort n (← countBody w sort (← j.getObjVal? "body")))
    | "at_most" => do
      if n > 7 then throw "CountingBound(at most 7)"
      pure (atMost sort n (← countBody w sort (← j.getObjVal? "body")))
    | "n_of_m" => do
      let m ← (← j.getObjVal? "m").getNat?
      if n > 7 || m > 7 then throw "CountingBound(n of m: numerator and denominator at most 7)"
      pure (nOfM sort n m (← countBody w sort (← j.getObjVal? "selected"))
        (← countBody w sort (← j.getObjVal? "property")))
    | other => throw s!"Unknown counting mode {other}"
  pure (ok id [("expansion", encCore expansion)])

def runConversion (id kind : String) (j : Json) : Except String Json := do
  match kind with
  | "day" => do
    let D ← parseIso (← stringField j "date")
    pure (ok id [("day", toJson D.num)])
  | "civil" => do
    let n ← (← j.getObjVal? "day").getNat?
    if n > dateMax then throw s!"DateRange({n})"
    match civilOf n with
    | some D => pure (ok id [("date", .str D.iso)])
    | none => throw s!"DateRange({n})"
  | "lower" => do
    let places ← (← j.getObjVal? "places").getNat?
    let d ← parseDecimal (← stringField j "decimal")
    match lower d places with
    | some q =>
      if (toString q).length > 40 then throw "ResourceLimit: Lowered integer exceeds 40 characters"
      pure (ok id [("coordinate", .str (toString q))])
    | none => throw s!"UnitPrecision(scale={10 ^ places})"
  | "render" => do
    let places ← (← j.getObjVal? "places").getNat?
    let q ← integer (← stringField j "coordinate")
    pure (ok id [("amount", .str (renderAmount places q))])
  | other => throw s!"unknown case kind {other}"

/-- Case kinds beyond this module (the document route), by environment. -/
abbrev Extension := W6Env → String → String → Json → Except String Json

def noExtension : Extension := fun _ _ other _ => throw s!"unknown case kind {other}"

def runCase (j : Json) (more : Extension := noExtension) : Except String Json := do
  let id ← stringField j "id"
  let kind ← match j.getObjVal? "kind" with
    | .ok k => k.getStr?
    | .error _ => pure "admission"
  if ["day", "civil", "lower", "render"].contains kind then return ← runConversion id kind j
  let w ← decodeEnvironment (← j.getObjVal? "environment")
  let ids := [("environment_id", Json.str w.environmentId),
    ("target_environment_id", Json.str w.targetId)]
  match kind with
  | "admission" => do
    let a ← decodeQuantity w (← j.getObjVal? "quantity")
    let value ← match j.getObjVal? "model" with
      | .ok m => do
        let d ← VE.Order.Wire.decodeValidModel w.vocab.core m
        match evalB (sortDomains d).toModel maxEvaluations [] a.formula.erase 0 with
        | some (value, work) => pure [("value", Json.bool value), ("evaluations", toJson work)]
        | none => throw budgetExhausted
      | .error _ => pure []
    pure (ok id ([("assurance", .str "lean-admitted"), ("Q", a.Q), ("core", a.core),
      ("meaning_id", .str a.meaningId), ("core_meaning_id", .str a.coreId)] ++ ids ++ value))
  | "countermodel" => do
    let ps ← admissions w (← j.getObjVal? "premises")
    let c ← decodeQuantity w (← j.getObjVal? "conclusion")
    quantityLimits ps c
    let d ← VE.Order.Wire.decodeValidModel w.vocab.core (← j.getObjVal? "model")
    let some refutes := refutesB (sortDomains d).toModel maxEvaluations (ps.map (·.formula.erase))
      c.formula.erase 0 | throw budgetExhausted
    pure (ok id ([("refutes", .bool refutes),
      ("premise_meaning_ids", toJson (ps.map (·.meaningId))),
      ("conclusion_meaning_id", .str c.meaningId),
      ("core_premise_meaning_ids", toJson (ps.map (·.coreId))),
      ("core_conclusion_meaning_id", .str c.coreId)] ++ ids))
  | "certificate" => do
    let ps ← admissions w (← j.getObjVal? "premises")
    let c ← decodeQuantity w (← j.getObjVal? "conclusion")
    quantityLimits ps c
    let cert ← decodeW6Certificate (← j.getObjVal? "certificate")
    let valid ← checkW6Certificate ps c cert
    pure (ok id ([("valid", .bool valid), ("premise_meaning_ids", toJson (ps.map (·.meaningId))),
      ("conclusion_meaning_id", .str c.meaningId),
      ("core_premise_meaning_ids", toJson (ps.map (·.coreId))),
      ("core_conclusion_meaning_id", .str c.coreId)] ++ ids))
  | "count" => runCount w id j
  | other => more w id other j

def runCaseReported (j : Json) (more : Extension := noExtension) : Json :=
  match runCase j more with
  | .ok result => result
  | .error message => Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"),
      ("error", .str message)] ++
      (if j.getObjValD "kind" == .str "certificate" then [("valid", .bool false)] else []))

/-- The `quantity` subcommand: read a JSON case list, print the results. -/
def main (paths : List String) (more : Extension := noExtension) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_conformance quantity [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j more
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Time.Wire
