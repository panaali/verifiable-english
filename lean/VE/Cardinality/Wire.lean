import VE.Cardinality.Erase
import VE.Time.Wire

/-! The `ve-cardinality@1` wire (docs/spec/quantities.md 4.1–4.3): Lean decodes a cardinality environment and its
statements, with the diagnostics of spec 4.2 in their order.

The W6a part of an environment is decoded by `VE.Time.Wire.decodeEnvironment` on the projection `projectW6`; the
environment's own identity is over the original, and the projection's W6a identities stay W6a's (`CardEnv.w6`). The
decoder establishes `CEnv.WellFormed` (E5–E8), which `cardinality_elab_sound` needs. A statement is decoded in one
depth-first, left-to-right pass after its envelope (S1) and size (S2): at each node the checks S3–S10 that apply to
it run in table order, a ratio's operands are checked in full before their tags are compared (S9), and a W6a part
is elaborated by W6a (S4). The decoded formula is then admitted by the proved `CFormula.admits`, and its identity is
over its canonical encoding (`WireTheorems.lean` states what the decoders establish). Certificates (`CardCertificate`), the problem limits P1–P3 and the case runner are
QT-A3's next part (qt-a3b). -/
namespace VE.Cardinality
open Lean

/-- E4's projection: the W6a environment inside a cardinality environment. It removes `cardinality_schema` and
`cardinality`, and removes `cardinality@0` from `profiles`; nothing else changes. -/
def projectW6 (env : Lean.Json) : Except String Lean.Json := do
  let profiles ← VE.Bridge.strings (← env.getObjVal? "profiles")
  let base ← VE.Time.Wire.dropFields env ["cardinality_schema", "cardinality", "profiles"]
  pure (Lean.Json.mkObj ((← VE.Bridge.fields base) ++
    [("profiles", Lean.Json.arr ((profiles.filter (· != "cardinality@0")).map Lean.Json.str).toArray)]))

/-- A decoded cardinality environment; the decoder fills `wf` (E5–E8). `w6` is W6a's decoding of `projectW6` of the
request's environment (E4), with the projection's W6a identities; `environmentId` is the original environment's
identity (4.1). -/
structure CardEnv where
  w6 : VE.Time.Wire.W6Env
  env : CEnv
  wf : env.WellFormed
  environmentId : String

structure CAdmission (w : CardEnv) where
  formula : CFormula
  admitted : formula.admits w.env = true
  meaningId : String

/-- An admitted statement satisfies the independent admission relation. -/
theorem CAdmission.sound {w : CardEnv} (a : CAdmission w) : Admitted w.env a.formula := admits_sound _ _ a.admitted

/-- The original environment's profiles: `cardinality@0` and the projection's. -/
def CardEnv.profiles (w : CardEnv) : List String := "cardinality@0" :: w.w6.profiles

end VE.Cardinality

namespace VE.Cardinality.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings)
open VE.Time (QType)

def format : String := "ve-cardinality@1"

/-! ## The environment (E1–E8) -/

/-- E2: `cardinality@0` beside one of W6a's two profile lists (code point order). -/
def profileLists : List (List String) := VE.Time.Wire.w6Profiles.map ("cardinality@0" :: ·)

def maxFiniteSorts : Nat := 64

theorem wellFormed_of (v : VE.Time.Wire.QVocab) (finite : List String)
    (h : (finite.all v.sorts.contains && v.constants.all (fun c => !c.1.startsWith regionPrefix)) = true) :
    (CEnv.mk v.env finite).WellFormed := by
  simp only [Bool.and_eq_true, List.all_eq_true, List.contains_iff_mem, Bool.not_eq_true'] at h
  refine ⟨h.1, fun c τ hc => ?_⟩
  have := h.2 _ (VE.Order.lookup_mem _ _ _ hc)
  simpa only using this

/-- E5 and E6: the declared finite sorts, as written. -/
def finiteSorts (env : Json) : Except String (List String) := do
  let .ok finite := (do
      let c ← env.getObjVal? "cardinality"
      exactFields c ["finite_sorts"]
      strings (← c.getObjVal? "finite_sorts") : Except String (List String))
    | throw "InvalidInput: cardinality.finite_sorts must be an array of sort names"
  if finite.length > maxFiniteSorts then throw s!"ResourceLimit: At most {maxFiniteSorts} finite sorts"
  pure finite

/-- E7, name by name, then E8 over every declared sort, predicate and constant. -/
def checkDeclarations (v : VE.Time.Wire.QVocab) (finite : List String) : Except String Unit := do
  let mut seen : List String := []
  for s in finite do
    if seen.contains s then throw s!"DuplicateDeclaration: finite sort {s}"
    unless v.sorts.contains s do throw s!"UnknownSort({s})"
    seen := s :: seen
  for n in v.sorts ++ v.predicates.map (·.1) ++ v.constants.map (·.1) do
    if n.startsWith regionPrefix then
      throw s!"ReservedName: {regionPrefix} is reserved for region constants ({n})"

def decodeEnvironment (env : Json) : Except String CardEnv := do
  exactFields env ["language", "profiles", "spec_revision", "vocabulary", "unit_schema", "units",
    "cardinality_schema", "cardinality"]
  let profiles ← strings (← env.getObjVal? "profiles")
  unless profileLists.contains profiles do
    throw "UnsupportedProfile: cardinality@0 requires order@0, relational-fol@0 and time@0, optionally with documents@1"
  unless (← stringField env "cardinality_schema") == format do
    throw "UnsupportedProfile: Unsupported cardinality schema"
  let w6 ← VE.Time.Wire.decodeEnvironment (← projectW6 env)
  let finite ← finiteSorts env
  checkDeclarations w6.vocab finite
  let id ← VE.Route.Wire.environmentId profiles env
  if h : (finite.all w6.vocab.sorts.contains &&
      w6.vocab.constants.all (fun c => !c.1.startsWith regionPrefix)) = true then
    pure ⟨w6, ⟨w6.vocab.env, finite⟩, wellFormed_of w6.vocab finite h, id⟩
  else throw "InvalidInput: cardinality environment is not well formed"

/-! ## Statements (S1–S10) -/

def maxTerms : Nat := 64

def invalidNode : String := "Invalid cardinality formula"

/-- S3's texts for a node no case reads: an unknown operator, or a known one with the wrong shape. -/
def refuse {α : Type} (known : List String) : List Json → Except String α
  | .str op :: _ => if known.contains op then throw invalidNode else throw s!"Unknown cardinality operator {op}"
  | _ => throw invalidNode

def items (j : Json) : Except String (List Json) :=
  match j.getArr? with
  | .ok xs => pure xs.toList
  | .error _ => throw invalidNode

/-- A body's operators (S3); its atoms are typed at its node's S6. -/
def elabBody : Nat → Json → Except String Body
  | 0, _ => throw VE.Time.Wire.depthLimit
  | fuel + 1, j => do
    match ← items j with
    | [.str "is", .str p] => pure (.atom p)
    | [.str "any"] => pure .any
    | [.str "not", b] => pure (.not (← elabBody fuel b))
    | [.str "and", a, b] => pure (.and (← elabBody fuel a) (← elabBody fuel b))
    | [.str "or", a, b] => pure (.or (← elabBody fuel a) (← elabBody fuel b))
    | xs => refuse ["is", "any", "not", "and", "or"] xs

/-- S5, then S6: the counted sort is declared finite, then every atom of the node's bodies is a unary predicate of
it. -/
def countedSort (E : CEnv) (s : String) (bodies : List Body) : Except String Unit := do
  unless E.finite.contains s do throw s!"CardinalityNotFinite({s})"
  for p in bodies.flatMap Body.atoms do
    unless E.q.predicates p == some [.obj s] do throw s!"TypeMismatch: {p} is not a unary predicate of sort {s}"

/-- A ratio operand in full: a W6a term (S4) or a count over a finite sort (S3, S5, S6); with its type. -/
def elabOperand (w : CardEnv) (j : Json) : Except String (QType × CTerm) := do
  match ← items j with
  | [.str "quantity", t] =>
    let (τ, q) ← VE.Time.Wire.elabTerm w.w6.vocab [] VE.Limits.maxDepth t
    pure (τ, .quantity q)
  | [.str "count", .str s, b] =>
    let b ← elabBody VE.Limits.maxDepth b
    countedSort w.env s [b]
    pure (.qty VE.Time.dimensionless, .count s b)
  | xs => refuse ["quantity", "count"] xs

/-- A ratio node's operands, left to right, then their tags (S9). -/
def elabRatio (w : CardEnv) (x y : Json) : Except String (CTerm × CTerm) := do
  let (a, x) ← elabOperand w x
  let (b, y) ← elabOperand w y
  VE.Time.Wire.same a b
  match a with
  | .qty g =>
    if g == VE.Time.dayTag then
      throw "TypeMismatch: a ratio of calendar dates has no meaning; durations use elapsed_day"
  | .obj _ => throw "TypeMismatch: Ratio needs quantity terms"
  pure (x, y)

def ruleNames : List (String × VE.Numbers.Rounding) :=
  [("ties_up", .tiesUp), ("half_even", .halfEven), ("down", .down), ("up", .up)]

def elabRule (r : String) : Except String VE.Numbers.Rounding :=
  match VE.Order.lookup ruleNames r with
  | some x => pure x
  | none => throw s!"Unknown rounding rule {r}"

/-- S10, after the operands. -/
def admittedRule (name : String) (r : VE.Numbers.Rounding) : Except String Unit :=
  unless admittedRules.contains r do throw s!"UnsupportedRounding({name})"

/-- A printed number: its digits and its written places ("0.30" is (30, 2)). -/
def printed (s : String) : Except String (Int × Nat) := do
  let d ← VE.Time.parseDecimal s
  pure (d.significand, d.places)

def elabName {α : Type} (names : List (String × α)) (s : String) : Except String α :=
  match VE.Order.lookup names s with
  | some x => pure x
  | none => throw s!"Unknown cardinality operator {s}"

def relNames : List (String × Rel) := [("lt", .lt), ("le", .le), ("eq", .eq)]
def cmpNames : List (String × Cmp) := [("gt", .gt), ("ge", .ge), ("lt", .lt), ("le", .le), ("eq", .eq)]

def elabFormula (w : CardEnv) : Nat → Json → Except String CFormula
  | 0, _ => throw VE.Time.Wire.depthLimit
  | fuel + 1, j => do
    let body := elabBody VE.Limits.maxDepth
    match ← items j with
    | [.str "quantity", q] => pure (.quantity (← VE.Time.Wire.elabFormula w.w6.vocab VE.Limits.maxDepth [] q))
    | [.str "count", .str s, ts, .str rel, .str bound] =>
      let terms ← (← items ts).mapM fun t => do
        match ← items t with
        | [.str k, b] => pure (← VE.Time.Wire.integer k, ← body b)
        | _ => throw invalidNode
      let rel ← elabName relNames rel
      let bound ← VE.Time.Wire.integer bound
      countedSort w.env s (terms.map (·.2))
      if terms.length > maxTerms then throw s!"ResourceLimit: At most {maxTerms} terms in a count"
      pure (.count ⟨s, terms, rel, bound⟩)
    | [.str "proportion", .str s, whole, part, .str cmp, .str num, .str den] =>
      let whole ← body whole
      let part ← body part
      let cmp ← elabName cmpNames cmp
      let n ← VE.Time.Wire.integer num
      let d ← VE.Time.Wire.integer den
      countedSort w.env s [whole, part]
      unless 0 ≤ n && n ≤ d && 0 < d do throw s!"ProportionRange({num} in {den})"
      pure (.proportion ⟨s, whole, part, cmp, n.toNat, d.toNat⟩)
    | [.str "rounds_to", .str r, x, y, .str p] =>
      let rule ← elabRule r
      let (D, k) ← printed p
      let (x, y) ← elabRatio w x y
      admittedRule r rule
      pure (.roundsTo rule x y D k)
    | [.str "percent_of", x, y, .str p] =>
      let (D, k) ← printed p
      let (x, y) ← elabRatio w x y
      pure (.percentOf x y D k)
    | [.str "percent_rounds_to", .str r, x, y, .str p] =>
      let rule ← elabRule r
      let (D, k) ← printed p
      let (x, y) ← elabRatio w x y
      admittedRule r rule
      pure (.percentRoundsTo rule x y D k)
    | [.str "not", a] => pure (.not (← elabFormula w fuel a))
    | [.str "and", a, b] => pure (.and (← elabFormula w fuel a) (← elabFormula w fuel b))
    | [.str "or", a, b] => pure (.or (← elabFormula w fuel a) (← elabFormula w fuel b))
    | [.str "implies", a, b] => pure (.implies (← elabFormula w fuel a) (← elabFormula w fuel b))
    | xs => refuse ["quantity", "count", "proportion", "rounds_to", "percent_of", "percent_rounds_to", "not", "and",
        "or", "implies"] xs

/-! ## Canonical encoding (the identity's object, echoed in the answer) -/

def encBody : Body → Json
  | .atom p => toJson ["is", p]
  | .any => toJson ["any"]
  | .not b => Json.arr #[.str "not", encBody b]
  | .and a b => Json.arr #[.str "and", encBody a, encBody b]
  | .or a b => Json.arr #[.str "or", encBody a, encBody b]

def nameOf {α : Type} [BEq α] (names : List (String × α)) (x : α) : String :=
  ((names.find? (·.2 == x)).map (·.1)).getD ""

def encOperand : CTerm → Json
  | .quantity t => Json.arr #[.str "quantity", VE.Time.Wire.encTerm t]
  | .count s b => Json.arr #[.str "count", .str s, encBody b]

def encPrinted (D : Int) (k : Nat) : Json := .str (VE.Time.renderAmount k D)

def encode : CFormula → Json
  | .quantity a => Json.arr #[.str "quantity", VE.Time.Wire.encQ a]
  | .count c => Json.arr #[.str "count", .str c.sort,
      Json.arr (c.terms.map fun kb => Json.arr #[.str (toString kb.1), encBody kb.2]).toArray,
      .str (nameOf relNames c.rel), .str (toString c.bound)]
  | .proportion p => Json.arr #[.str "proportion", .str p.sort, encBody p.whole, encBody p.part,
      .str (nameOf cmpNames p.cmp), .str (toString p.num), .str (toString p.den)]
  | .roundsTo r x y D k => Json.arr #[.str "rounds_to", .str (nameOf ruleNames r), encOperand x, encOperand y,
      encPrinted D k]
  | .percentOf x y D k => Json.arr #[.str "percent_of", encOperand x, encOperand y, encPrinted D k]
  | .percentRoundsTo r x y D k => Json.arr #[.str "percent_rounds_to", .str (nameOf ruleNames r), encOperand x,
      encOperand y, encPrinted D k]
  | .not a => Json.arr #[.str "not", encode a]
  | .and a b => Json.arr #[.str "and", encode a, encode b]
  | .or a b => Json.arr #[.str "or", encode a, encode b]
  | .implies a b => Json.arr #[.str "implies", encode a, encode b]

def canonical (f : CFormula) : Json := Json.mkObj [("format", .str format), ("formula", encode f)]

/-- S1 (the envelope), S2 (10,000 source nodes), the pass, then admission; the meaning id is over the canonical
object in the cardinality environment's identity. -/
def decodeStatement (w : CardEnv) (j : Json) : Except String (CAdmission w) := do
  unless (exactFields j ["format", "formula"]).isOk && j.getObjValD "format" == .str format do
    throw "Unsupported cardinality format"
  let source ← j.getObjVal? "formula"
  if VE.Time.Wire.jsonNodes (VE.Limits.maxJsonDepth + 1) source > VE.Limits.maxNodes then
    throw VE.Time.Wire.depthLimit
  let f ← elabFormula w VE.Limits.maxDepth source
  if h : f.admits w.env = true then
    pure ⟨f, h, ← VE.Route.Wire.meaningId w.profiles w.environmentId (canonical f)⟩
  else throw "TypeMismatch: statement is not admitted"

end VE.Cardinality.Wire
