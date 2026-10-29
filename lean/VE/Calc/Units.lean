import VE.Calc.Dimension
import VE.Calc.Wire
import VE.Time.Wire

/-! `ve-units@2` (math-evidence spec 6.2, ME-6): its only decoder, its identity (3.3, J1) and the
dimension of an expression with its diagnostic. A `ve-units@1` environment is decoded by W6a's frozen decoder,
unchanged; each of its tags is its own base dimension (`legacyDim`) and has no factor. -/

namespace VE.Calc.Units
open Lean VE.Calc VE.Numbers
open VE.Bridge (fields identifier)
open VE.Calc.Wire (invalid checkFields plain literal exponentFault literalFault)

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

/-- An exact positive factor written as a literal of 3.1 (`"<decimal>"` or `["sci", "<decimal>", e]`) within
limits 5 and 6 of 3.2, and its shortest plain decimal (11: no `sci` exponent remains). -/
def decodeFactor (path : String) (j : Json) : Except String (Rat × String) := do
  if let some e := exponentFault j <|> literalFault (if j matches .str _ then .arr #[.str "lit", j] else j) then
    throw e
  let p ← literal path j
  unless 0 < p.value do throw (invalid path "must be more than zero")
  pure (p.value, plain p)

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
  let exps := Json.mkObj (dim.exps.map (fun ((b, k) : String × Int) => (b, Json.str (toString k))))
  pure (⟨name, dim, some factor⟩, (name, Json.mkObj [("base_exponents", exps), ("factor", .str spelling)]))

def decodeV2 (env : Json) : Except String UnitEnv := do
  checkFields "environment" env ["unit_schema", "base_dimensions", "units"]
  let bases ← match (env.getObjValD "base_dimensions").getArr? with
    | .ok bs => bs.toList.mapM fun (b : Json) => match b.getStr? with
      | .ok s => if identifier s then pure s else throw (invalid "base_dimensions" "must list identifiers")
      | .error _ => throw (invalid "base_dimensions" "must list identifiers")
    | .error _ => throw (invalid "base_dimensions" "must be a list")
  unless bases.Nodup do throw (invalid "base_dimensions" "must not repeat a name")
  let units ← match fields (env.getObjValD "units") with
    | .ok fs => fs.mapM fun (n, r) => decodeUnit bases n r
    | .error _ => throw (invalid "units" "must be an object")
  let (defs, entries) := units.unzip
  pure ⟨defs, Json.mkObj [("unit_schema", .str "ve-units@2"),
    ("base_dimensions", .arr (bases.map Json.str).toArray), ("units", Json.mkObj entries)]⟩

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

def UnitEnv.unit? (u : UnitEnv) (n : String) : Option UnitDef := u.units.find? (·.name == n)

/-- Units are values: a unit's value is its factor (none for a `ve-units@1` tag). -/
def UnitEnv.values (u : UnitEnv) : Values := fun n => (u.unit? n).bind (·.factor)

/-- Each name's physical dimension: a unit's own, else its declared unit's; a value without a unit
is dimensionless. `values` lists each value with its optional unit. -/
def UnitEnv.context (u : UnitEnv) (values : List (String × Option String)) :
    Except String (String → Option PhysDim) := do
  for (n, unit) in values do
    if (u.unit? n).isSome then throw s!"DuplicateName: {n}"
    if let some t := unit then
      if (u.unit? t).isNone then throw (invalid s!"values.{n}.unit" "names no declared unit")
  pure fun n => match u.unit? n, values.find? (·.1 == n) with
    | some d, _ => some d.dim
    | none, some (_, some t) => (u.unit? t).map (·.dim)
    | none, some (_, none) => some PhysDim.one
    | none, none => none

/-- A declared name in words: no diagnostic text contains a symbol (13.1), so `fringe_width` is
"fringe width". -/
def spoken (name : String) : String := name.map fun c => if c = '_' then ' ' else c

/-- A dimension in words: its base exponents ("length", "length per time"). -/
def dimWords (d : PhysDim) : String :=
  let part := fun (b : String) (k : Nat) =>
    let b := spoken b
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

/-- The unit a rounding refusal divides by: the dimension's coherent unit (factor 1), else its first
unit by name, else a unit of it in words. -/
def unitOf (u : UnitEnv) (d : PhysDim) : String :=
  let same := u.units.filter (·.dim == d)
  match same.find? (·.factor == some 1) <|> same.head? with
  | some x => spoken x.name
  | none => "unit of " ++ dimWords d

/-- The claim-level checks of 6.2: every side of a comparison or range has one dimension, and a
rounding claim rounds a dimensionless expression. `words` are the rounded expression's words. -/
def checkClaim (u : UnitEnv) (Γ : String → Option PhysDim) (words : String) : Claim → Except String Unit
  | .compare _ a b => do
      let x ← dimE Γ a
      let y ← dimE Γ b
      unless x = y do throw (mismatch x y)
  | .within e lo hi => do
      let x ← dimE Γ e
      let l ← dimE Γ lo
      let h ← dimE Γ hi
      unless x = l do throw (mismatch x l)
      unless x = h do throw (mismatch x h)
  | .rounds _ e _ => do
      let d ← dimE Γ e
      unless d = PhysDim.one do
        throw s!"RoundingNeedsNumber: divide by one {unitOf u d} to round {words}"

theorem unless_ok (p : Prop) [Decidable p] (m : String) (a : Unit) :
    (unless p do throw m : Except String Unit) = .ok a ↔ p := by
  by_cases hp : p <;> simp [hp, throw, throwThe, MonadExceptOf.throw, pure, Except.pure]

/-- A claim the checks admit has the same truth in every system of base units. -/
theorem checkClaim_invariant (u : UnitEnv) (Γ : String → Option PhysDim) (words : String) (ρ : Rescale)
    (σ : Values) (c : Claim) (hΓ : ∀ n d', Γ n = some d' → d'.Normal) (h : checkClaim u Γ words c = .ok ()) :
    c.Holds σ ↔ c.Holds (ρ.apply Γ σ) := by
  cases c with
  | compare cmp a b =>
      simp only [checkClaim, except_bind_ok, dimE_ok, unless_ok] at h
      obtain ⟨x, ha, y, hb, rfl⟩ := h
      exact compare_invariant Γ ρ σ cmp a b x hΓ ha hb
  | within e lo hi =>
      simp only [checkClaim, except_bind_ok, dimE_ok] at h
      obtain ⟨x, he, l, hl, k, hk, h⟩ := h
      by_cases hxl : x = l
      · subst hxl
        by_cases hxk : x = k
        · subst hxk
          have hle := fun p q => Comparison.holds_scale ⟨.le, false⟩ p q _ (ρ.of_pos x)
          simp only [Comparison.Holds, Rel.Holds, Bool.false_eq_true, if_false] at hle
          simp only [Claim.Holds, ← Expr.eval_iff, Expr.eval_rescale Γ ρ σ _ x he,
            Expr.eval_rescale Γ ρ σ _ x hl, Expr.eval_rescale Γ ρ σ _ x hk]
          cases e.eval σ <;> cases lo.eval σ <;> cases hi.eval σ <;> simp [hle]
        · simp [hxk, throw, throwThe, MonadExceptOf.throw, bind, Except.bind, pure, Except.pure] at h
      · simp [hxl, bind, Except.bind] at h
  | rounds r e p =>
      simp only [checkClaim, except_bind_ok, dimE_ok, unless_ok] at h
      obtain ⟨d, he, rfl⟩ := h
      exact rounds_invariant Γ ρ σ r e p hΓ he

end VE.Calc.Units
