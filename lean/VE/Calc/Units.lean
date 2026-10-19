import VE.Calc.Dimension
import VE.Calc.Render
import VE.Time.Wire

/-! `ve-units@2` (math-evidence spec 6.2, ME-6): its only decoder, its identity (3.3, J1) and the
dimension checks of a claim. A `ve-units@1` environment is decoded by W6a's frozen decoder,
unchanged; each of its tags is its own base dimension (`legacyDim`) and has no factor. -/

namespace VE.Calc.Units
open Lean VE.Calc VE.Numbers
open VE.Bridge (fields identifier)

def affineNames : List String := ["celsius", "degree_celsius", "fahrenheit", "degree_fahrenheit"]
def logarithmicNames : List String := ["decibel", "bel", "neper"]

/-- A declared unit: its physical dimension and its exact factor to the coherent unit of that
dimension; a `ve-units@1` tag has none and never converts. -/
structure UnitDef where
  name : String
  dim : PhysDim
  factor : Option Rat

structure UnitEnv where
  units : List UnitDef
  /-- The environment as hashed for identity (3.3). -/
  identity : Json

def invalid (path what : String) : String := s!"InvalidInput: {path} {what}"

def checkFields (path : String) (j : Json) (names : List String) : Except String Unit := do
  let actual ← match fields j with
    | .ok fs => pure (fs.map Prod.fst)
    | .error _ => throw (invalid path "must be an object")
  if let some n := actual.find? (!names.contains ·) then throw (invalid s!"{path}.{n}" "is unknown")
  if let some n := names.find? (!actual.contains ·) then throw (invalid s!"{path}.{n}" "is missing")

/-- `base_exponents`: each a declared base dimension with a nonzero integer exponent, in normal form. -/
def decodeExponents (bases : List String) (path : String) (j : Json) : Except String PhysDim := do
  let fs ← match fields j with
    | .ok fs => pure fs
    | .error _ => throw (invalid path "must be an object")
  fs.foldlM (init := PhysDim.one) fun d (b, k) => do
    unless bases.contains b do throw (invalid s!"{path}.{b}" "names no base dimension")
    let .ok k := k.getInt? | throw (invalid s!"{path}.{b}" "must be an integer")
    if k = 0 then throw (invalid s!"{path}.{b}" "must not be zero")
    pure ⟨insertExp (b, k) d.exps⟩

/-- An exact positive factor written as a decimal (W6's `parseDecimal`), and its shortest spelling. -/
def decodeFactor (path : String) (j : Json) : Except String (Rat × String) := do
  let .ok s := j.getStr? | throw (invalid path "must be a decimal string")
  let d ← match VE.Time.parseDecimal s with
    | .ok d => pure d
    | .error e => throw (if e.startsWith "ResourceLimit" then e else invalid path "must be a decimal")
  unless 0 < decValue d do throw (invalid path "must be more than zero")
  let frac := (d.frac.reverse.dropWhile (· = 0)).reverse
  pure (decValue d, VE.Time.Dec.toString { d with frac })

def decodeUnit (bases : List String) (name : String) (record : Json) :
    Except String (UnitDef × (String × Json)) := do
  let path := s!"units.{name}"
  unless identifier name do throw (invalid path "must be an identifier")
  if affineNames.contains name then throw s!"AffineUnit: {name}"
  if logarithmicNames.contains name then throw s!"LogarithmicUnit: {name}"
  if name = VE.Time.dayTag then throw "CalendarTagNotUnit: day (durations use elapsed_day)"
  checkFields path record ["base_exponents", "factor"]
  let dim ← decodeExponents bases s!"{path}.base_exponents" (record.getObjValD "base_exponents")
  let (factor, spelling) ← decodeFactor s!"{path}.factor" (record.getObjValD "factor")
  let exps := Json.mkObj (dim.exps.map fun (b, k) => (b, Json.str (toString k)))
  pure (⟨name, dim, some factor⟩, (name, Json.mkObj [("base_exponents", exps), ("factor", .str spelling)]))

def decodeV2 (env : Json) : Except String UnitEnv := do
  checkFields "environment" env ["unit_schema", "base_dimensions", "units"]
  let bases ← match (env.getObjValD "base_dimensions").getArr? with
    | .ok bs => bs.toList.mapM fun b => match b.getStr? with
      | .ok s => if identifier s then pure s else throw (invalid "base_dimensions" "must list identifiers")
      | .error _ => throw (invalid "base_dimensions" "must list identifiers")
    | .error _ => throw (invalid "base_dimensions" "must be a list")
  unless bases.Nodup do throw (invalid "base_dimensions" "must not repeat a name")
  let units ← match fields (env.getObjValD "units") with
    | .ok fs => fs.mapM fun (n, r) => decodeUnit bases n r
    | .error _ => throw (invalid "units" "must be an object")
  pure ⟨units.map Prod.fst, Json.mkObj [("unit_schema", .str "ve-units@2"),
    ("base_dimensions", .arr (bases.map Json.str).toArray), ("units", Json.mkObj (units.map Prod.snd))]⟩

/-- A `ve-units@1` environment: W6a's frozen decoder, hashed as written; nominal tags. -/
def decodeLegacy (env : Json) : Except String UnitEnv := do
  let w ← VE.Time.Wire.decodeEnvironment env
  pure ⟨w.vocab.units.map fun u => ⟨u.tag, legacyDim u.tag, none⟩, env⟩

def decode (env : Json) : Except String UnitEnv :=
  match env.getObjValD "unit_schema" with
  | .str "ve-units@2" => decodeV2 env
  | .str "ve-units@1" => decodeLegacy env
  | _ => throw (invalid "environment.unit_schema" "must be \"ve-units@2\" or \"ve-units@1\"")

/-- The environment's identity under the frozen encoder (3.3). -/
def UnitEnv.environmentId (u : UnitEnv) : Except String String :=
  VE.Route.Wire.environmentId ["calc@0"] u.identity

def UnitEnv.find? (u : UnitEnv) (n : String) : Option UnitDef := u.units.find? (·.name == n)

/-- Units are values: a unit's value is its factor (none for a `ve-units@1` tag). -/
def UnitEnv.values (u : UnitEnv) : Values := fun n => (u.find? n).bind (·.factor)

/-- Each name's physical dimension: a unit's own, else its declared unit's; a value without a unit
is dimensionless. `values` lists each value with its optional unit. -/
def UnitEnv.context (u : UnitEnv) (values : List (String × Option String)) :
    Except String (String → Option PhysDim) := do
  for (n, unit) in values do
    if (u.find? n).isSome then throw s!"DuplicateName: {n}"
    if let some t := unit then
      if (u.find? t).isNone then throw (invalid s!"values.{n}.unit" "names no declared unit")
  pure fun n => match u.find? n, values.find? (·.1 == n) with
    | some d, _ => some d.dim
    | none, some (_, some t) => (u.find? t).map (·.dim)
    | none, some (_, none) => some PhysDim.one
    | none, none => none

/-- A dimension in words: its base exponents ("length", "length per time"). -/
def dimWords (d : PhysDim) : String :=
  let part := fun (b : String) (k : Nat) =>
    if k = 1 then b else if k = 2 then b ++ " squared" else if k = 3 then b ++ " cubed"
    else b ++ " to the power " ++ toString k
  let up := (d.exps.filter (0 < ·.2)).map fun e => part e.1 e.2.toNat
  let down := (d.exps.filter (·.2 < 0)).map fun e => part e.1 (-e.2).toNat
  let top := if up.isEmpty then (if down.isEmpty then "dimensionless" else "one") else " times ".intercalate up
  if down.isEmpty then top else top ++ " per " ++ " times ".intercalate down

def mismatch (x y : PhysDim) : String := s!"DimensionMismatch: {dimWords x} and {dimWords y}"

/-- `Expr.dimOf` with its diagnostics: the first sum or difference of two dimensions names both. -/
def dimE (Γ : String → Option PhysDim) : Expr → Except String PhysDim
  | .lit _ => pure PhysDim.one
  | .val n => match Γ n with
    | some d => pure d
    | none => throw s!"UnknownName: {n} (declare it before the value that uses it)"
  | .add a b | .sub a b => do
      let x ← dimE Γ a
      let y ← dimE Γ b
      if x = y then pure x else throw (mismatch x y)
  | .mul a b => do pure ((← dimE Γ a).mul (← dimE Γ b))
  | .div a b => do pure ((← dimE Γ a).mul (← dimE Γ b).inv)
  | .pow a k => do pure ((← dimE Γ a).npow k)

theorem except_bind_ok {α β : Type} (m : Except String α) (f : α → Except String β) (b : β) :
    (m >>= f) = .ok b ↔ ∃ a, m = .ok a ∧ f a = .ok b := by
  cases m <;> simp [bind, Except.bind]

theorem dimE_ok (Γ : String → Option PhysDim) (e : Expr) (d : PhysDim) :
    dimE Γ e = .ok d ↔ e.dimOf Γ = some d := by
  induction e generalizing d with
  | lit q => simp [dimE, Expr.dimOf, pure, Except.pure, eq_comm]
  | val n => cases h : Γ n <;> simp [dimE, Expr.dimOf, h, pure, Except.pure, throw, throwThe,
      MonadExceptOf.throw]
  | add a b iha ihb | sub a b iha ihb =>
      simp only [dimE, Expr.dimOf, except_bind_ok, iha, ihb]
      simp only [bind, Option.bind_eq_some_iff]
      constructor <;> rintro ⟨x, hx, y, hy, h⟩ <;> refine ⟨x, hx, y, hy, ?_⟩ <;>
        by_cases hxy : x = y <;> simp_all [pure, Except.pure, throw, throwThe, MonadExceptOf.throw]
  | mul a b iha ihb | div a b iha ihb =>
      simp only [dimE, Expr.dimOf, except_bind_ok, iha, ihb]
      simp [Option.bind_eq_some_iff, pure, Except.pure]
  | pow a k iha =>
      simp only [dimE, Expr.dimOf, except_bind_ok, Option.map_eq_some_iff, iha]
      simp [pure, Except.pure]

def same (x y : PhysDim) : Except String Unit := if x = y then pure () else throw (mismatch x y)

/-- The dimension checks of a claim (6.2): the sides of a comparison and of a range share one
dimension, and a rounding claim is on a dimensionless expression. -/
def checkClaim (u : UnitEnv) (Γ : String → Option PhysDim) (words : String → Option String) :
    Claim → Except String Unit
  | .compare _ a b => do same (← dimE Γ a) (← dimE Γ b)
  | .within e lo hi => do
      let x ← dimE Γ e
      same x (← dimE Γ lo)
      same x (← dimE Γ hi)
  | .rounds _ e _ => do
      let x ← dimE Γ e
      unless x = PhysDim.one do
        let unit := match u.units.find? (fun d => d.dim = x ∧ d.factor = some 1) with
          | some d => d.name.replace "_" " "
          | none => "unit of " ++ dimWords x
        throw s!"RoundingNeedsNumber: divide by one {unit} to round \
          {(English.renderExpr words e).getD "the expression"}"

end VE.Calc.Units
