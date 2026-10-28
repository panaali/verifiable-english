import VE.Calc.Run
import Std.Data.HashMap

/-! Spec 3.2's work addendum for `calc@0` (me-2n; me-2b review F1, under the DRI's rule of 2026-10-27 for `arith@0`:
each value evaluated once, and its size charged), type-checked as a scratch stub against `main`'s `lean/` tree:
`cd lean && lake env lean ../docs/spec/math-evidence/me-2n-calc-work-stub.lean`. Evidence only, not product code: its
names are in `VE.Calc.Work`, nothing imports it, and proofs are `sorry` where the build (me-2nb, me-2nc) proves them.
The units of the fixtures are computed below with `#guard`, by this file's evaluator, not by product code. -/

namespace VE.Calc.Work
open VE.Calc VE.Numbers

/-! ## The unit and the limit (3.2, limit 10) -/

/-- 12.2's size of an integer: the bit length of its magnitude, and 1 for 0. -/
def bits (x : Int) : Nat := x.natAbs.log2 + 1

/-- The size of an exact value: its numerator's and its denominator's. -/
def qbits (q : Rat) : Nat := bits q.num + bits q.den

/-- Limit 10: the units one case may spend, 12.2's unit (one per visit, plus the size of each value computed). -/
def maxWork : Nat := 2 ^ 33

/-! ## The digit limit, decided without a digit list -/

/-- `10 ^ maxDigits` lies between `2 ^ (smallBits - 1)` and `2 ^ smallBits`. -/
def smallBits : Nat := 13607
#guard 2 ^ (smallBits - 1) < 10 ^ maxDigits && 10 ^ maxDigits < 2 ^ smallBits

theorem digitCount_le_iff (n : Nat) : digitCount n ≤ maxDigits ↔ n < 10 ^ maxDigits := sorry
#guard [10 ^ maxDigits - 1, 10 ^ maxDigits].map digitCount = [maxDigits, maxDigits + 1]

/-- 2.4's guard by two comparisons: `Small`'s meaning, without building a list of digits. -/
def Val.check (q : Rat) : Val :=
  if q.num.natAbs < 10 ^ maxDigits ∧ q.den < 10 ^ maxDigits then .ok q else .tooLarge

theorem Val.check_eq (q : Rat) : Val.check q = Val.guard q := by
  unfold Val.check Val.guard Small
  simp only [digitCount_le_iff]

#guard ([10 ^ maxDigits - 1, 10 ^ maxDigits, 1 / (10 ^ maxDigits - 1), 1 / 10 ^ maxDigits] : List Rat).all fun q =>
  Val.check q == Val.guard q

/-- A power that is beyond the digit limit, known from its base's size before it is computed. -/
def powTooLarge (x : Rat) (k : Nat) : Bool :=
  smallBits ≤ (bits x.num - 1) * k || smallBits ≤ (bits x.den - 1) * k

theorem powTooLarge_sound (x : Rat) (k : Nat) (h : powTooLarge x k = true) : Val.guard (x ^ k) = .tooLarge := sorry

/-! ## (a) Each declaration evaluated once, in order, into a table that later values and every claim read -/

/-- The values so far, the latest declaration first. -/
abbrev Table := List (String × Val)

def Table.read (t : Table) (n : String) : Val := (t.lookup n).getD .undefined

/-- 2.4's values, each declaration's computed once from the entries before it. -/
def valueTable (ds : List Decl) : Table := ds.foldl (fun (t : Table) d => (d.name, d.valL t.read) :: t) []

/-- The meaning: the table reads what 2.4's `valuesL` gives, so every theorem of 2.4 and 3.4 is unchanged. -/
theorem valueTable_read (ds : List Decl) : (valueTable ds).read = valuesL ds := by
  suffices h : ∀ (t : Table) (τ : String → Val), t.read = τ →
      Table.read (ds.foldl (fun (t : Table) d => (d.name, d.valL t.read) :: t) t) =
        ds.foldl (fun τ d n => if n = d.name then d.valL τ else τ n) τ from
    h [] _ (funext fun _ => rfl)
  induction ds with
  | nil => intro t τ h; exact h
  | cons d rest ih =>
    intro t τ h
    apply ih
    funext n
    subst h
    by_cases hn : n = d.name
    · subst hn; simp [Table.read]
    · have : (n == d.name) = false := by simpa using hn
      simp only [Table.read, List.lookup, this, hn, if_false]

/-! ## (b) The charge: one visit per node, and each value computed its size, refused before the limit is passed -/

def charge {α : Type} (limit w : Nat) (k : Nat → Option (α × Nat)) : Option (α × Nat) :=
  if limit ≤ w then none else k (w + 1)

/-- A value computed is charged its size, then held to the digit limit. -/
def chargeQ (limit : Nat) (q : Rat) (w : Nat) : Option (Val × Nat) :=
  if limit < w + qbits q then none else some (Val.check q, w + qbits q)

/-- A value read from the table is charged its size; a fault costs nothing more. -/
def chargeV (limit : Nat) (v : Val) (w : Nat) : Option (Val × Nat) :=
  match v with
  | .ok q => if limit < w + qbits q then none else some (v, w + qbits q)
  | v => some (v, w)

/-- 2.4's `Val.bin`, charged: `f` computes a value only from two values, and the first fault decides. -/
def binC (limit : Nat) (f : Rat → Rat → Option Rat) (a b : Val) (w : Nat) : Option (Val × Nat) :=
  match a, b with
  | .ok x, .ok y => match f x y with
    | some q => chargeQ limit q w
    | none => some (.undefined, w)
  | .ok _, v => some (v, w)
  | v, _ => some (v, w)

/-- 2.4's `Expr.evalL` over the table, charged; `none` when the units would pass `limit`. -/
def Expr.evalC (limit : Nat) (t : Table) : Expr → Nat → Option (Val × Nat)
  | .lit q, w => charge limit w (chargeQ limit q)
  | .val n, w => charge limit w (chargeV limit (t.read n))
  | .add a b, w => charge limit w fun w => match Expr.evalC limit t a w with
    | none => none
    | some (x, w) => (Expr.evalC limit t b w).bind fun r => binC limit (fun x y => some (x + y)) x r.1 r.2
  | .sub a b, w => charge limit w fun w => match Expr.evalC limit t a w with
    | none => none
    | some (x, w) => (Expr.evalC limit t b w).bind fun r => binC limit (fun x y => some (x - y)) x r.1 r.2
  | .mul a b, w => charge limit w fun w => match Expr.evalC limit t a w with
    | none => none
    | some (x, w) => (Expr.evalC limit t b w).bind fun r => binC limit (fun x y => some (x * y)) x r.1 r.2
  | .div a b, w => charge limit w fun w => match Expr.evalC limit t a w with
    | none => none
    | some (x, w) => (Expr.evalC limit t b w).bind fun r =>
        binC limit (fun x y => if y = 0 then none else some (x / y)) x r.1 r.2
  | .pow a k, w => charge limit w fun w => match Expr.evalC limit t a w with
    | none => none
    | some (.ok x, w) => if powTooLarge x k then some (.tooLarge, w) else chargeQ limit (x ^ k) w
    | some (v, w) => some (v, w)

def Decl.valC (limit : Nat) (t : Table) (d : Decl) (w : Nat) : Option (Val × Nat) :=
  match d.source with
  | .stated q | .counted _ (.ok (some q)) => charge limit w (chargeQ limit q)
  | .defined e => Expr.evalC limit t e w
  | .free | .counted _ (.ok none) => some (.undefined, w)
  | .counted _ .exhausted => some (.exhausted, w)

/-- The table, charged: each declaration once, in order. -/
def valueTableC (limit : Nat) : List Decl → Table → Nat → Option (Table × Nat)
  | [], t, w => some (t, w)
  | d :: ds, t, w => match Decl.valC limit t d w with
    | none => none
    | some (v, w) => valueTableC limit ds ((d.name, v) :: t) w

def Expr.evalsC (limit : Nat) (t : Table) : List Expr → Nat → Option (List Val × Nat)
  | [], w => some ([], w)
  | e :: es, w => match Expr.evalC limit t e w with
    | none => none
    | some (v, w) => (Expr.evalsC limit t es w).map fun r => (v :: r.1, r.2)

/-- A claim's verdict from its sides' values, in `Claim.exprs`' order (2.2's `Claim.decide`, read from the sides). -/
def Claim.decideSides : Claim → List Rat → Verdict
  | .compare c _ _, [x, y] => if c.Holds x y then .holds else .fails
  | .within .., [x, l, h] => if l ≤ x ∧ x ≤ h then .holds else .fails
  | .rounds r _ p, [x] => if RoundsTo r p x then .holds else .fails
  | _, _ => .undefined

/-- 2.4's `Claim.run`, read from the sides evaluated once; the row's `sides`, `display` and `tie` read them too. -/
def Claim.ofSides (c : Claim) (vs : List Val) : Outcome :=
  match firstFault vs with
  | some .tooLarge => .unknown (.limit .digits)
  | some .exhausted => .unknown (.limit .evaluations)
  | some _ => .decided .undefined
  | none => .decided (Claim.decideSides c (vs.filterMap fun | .ok q => some q | _ => none))

/-- The case's claim rows within `limit` units, with each claim's sides: the table first, then each claim's
expressions once, in order. A derivation's row is 5's (its charge is (b)'s lowering and search, me-2nc). -/
def runC (limit : Nat) (c : Case) : Option (List (Outcome × List Val) × Nat) :=
  match valueTableC limit c.decls [] 0 with
  | none => none
  | some (t, w) => c.claims.foldl (fun acc (_, k) => acc.bind fun (rows, w) => match k with
      | .claim cl => (Expr.evalsC limit t cl.exprs w).map fun r => (rows ++ [(Claim.ofSides cl r.1, r.1)], r.2)
      | k => some (rows ++ [(k.run c.decls, [])], w)) (some ([], w))

/-! The statements the build proves (me-2nb): the charged run means what 2.4 and 3.4 say, its refusal depends only
on the case, it never passes its limit, and some limit covers every case. -/

theorem Expr.evalC_agrees (limit : Nat) (t : Table) (e : Expr) (w : Nat) (v : Val) (w' : Nat)
    (h : Expr.evalC limit t e w = some (v, w')) : v = e.evalL t.read := sorry
theorem valueTableC_eq (limit : Nat) (ds : List Decl) (t : Table) (w : Nat)
    (h : valueTableC limit ds [] 0 = some (t, w)) : t = valueTable ds := sorry
theorem Claim.ofSides_eq (ds : List Decl) (h : WellFormed ds) (c : Claim) :
    Claim.ofSides c (c.exprs.map (Expr.evalL (valuesL ds))) = c.run ds := sorry
theorem runC_sound (limit : Nat) (c : Case) (h : WellFormed c.decls) (rows : List (Outcome × List Val)) (w : Nat)
    (hr : runC limit c = some (rows, w)) : rows.map Prod.fst = c.claims.map fun k => k.2.run c.decls := sorry
theorem runC_mono (limit limit' : Nat) (c : Case) (r : List (Outcome × List Val) × Nat)
    (h : runC limit c = some r) (hl : limit ≤ limit') : runC limit' c = some r := sorry
theorem runC_work (limit : Nat) (c : Case) (r : List (Outcome × List Val) × Nat)
    (h : runC limit c = some r) : r.2 ≤ limit := sorry
theorem runC_complete (c : Case) : ∃ limit r, runC limit c = some r := sorry

/-! ## (b) for derivations: every step charged, each entry once; 5's lowering held to the digit limit -/

/-- The units of one entry visited (a coefficient of a form, a weight of a row): its small arithmetic and its lookups
among at most `FM.maxUnknowns` names, measured at 0.86 µs today against 0.58 ns per unit of size (3.2). -/
def entryUnits : Nat := 2 ^ 11

/-! One pass each. 5's `QLin.norm` (through `FM.firstAppearance` and `coeffOf`), `QLin.isConst`, `FM.pick` and
`Farkas.check` visit each entry once per other entry; these visit it once and are equal to them (me-2nc proves it). -/

/-- 5's `QLin.norm` in one pass: the names in order of first appearance, each with the sum of its coefficients. -/
def QLin.normOnce (L : QLin) : QLin :=
  let (order, sums) := L.coeffs.foldl (fun (acc : Array String × Std.HashMap String Rat) (n, c) =>
    match acc.2[n]? with
    | some s => (acc.1, acc.2.insert n (s + c))
    | none => (acc.1.push n, acc.2.insert n c)) (#[], {})
  ⟨L.const, (order.toList.map fun n => (n, sums.getD n 0)).filter (·.2 != 0)⟩
theorem QLin.normOnce_eq (L : QLin) : QLin.normOnce L = L.norm := sorry

/-- 5's `QLin.isConst`: every coefficient cancels. -/
def QLin.isConstOnce (L : QLin) : Bool := (QLin.normOnce L).coeffs.isEmpty
theorem QLin.isConstOnce_eq (L : QLin) : QLin.isConstOnce L = L.isConst := sorry

/-- 5's `Farkas.check` with its combination normalised once (`coeffOf` per name visits the whole combination). -/
def Farkas.checkOnce (fs : List QFact) (c : Farkas) : Bool :=
  let ls := List.zipWith (fun w f => f.form.scale w) c.weights fs
  let comb : QLin := QLin.normOnce ⟨(ls.map (·.const)).sum, ls.flatMap (·.coeffs)⟩
  c.weights.length == fs.length && c.weights.all (fun w => decide (0 ≤ w)) && comb.coeffs.isEmpty &&
  (decide (comb.const < 0) ||
    (comb.const == 0 && (List.zipWith (fun w f => decide (0 < w) && f.strict) c.weights fs).any id))
theorem Farkas.checkOnce_eq (fs : List QFact) (c : Farkas) : Farkas.checkOnce fs c = c.check fs := sorry

/-- The tightest of a list of bounds, strict when a bound equal to it is strict. -/
def tightest (better : Rat → Rat → Bool) (bs : List (Rat × Bool)) : Option (Rat × Bool) :=
  bs.foldl (fun acc (b, s) => match acc with
    | none => some (b, s)
    | some (a, t) => if better b a then some (b, s) else if b == a then some (a, t || s) else some (a, t)) none

/-- 5's `FM.pick` in two passes: a row holds at `x = v` exactly when `v` is within its bound, so a candidate fits
exactly when it is within the tightest bounds and every row without `x` holds; the candidates are 5's, in its order. -/
def pickOnce (x : String) (rows : List FM.Row) (κ : List (String × Rat)) : Rat :=
  let val := fun n => if n = x then (0 : Rat) else (κ.lookup n).getD 0
  let cs := rows.map fun r => (r.fact.form.coeffOf x, r.fact.form.eval val, r.fact.strict)
  let zeroOk := cs.all fun (c, r, s) => c != 0 || (if s then decide (0 < r) else decide (0 ≤ r))
  let lo := tightest (fun b a => decide (a < b)) <| cs.filterMap fun (c, r, s) =>
    if 0 < c then some (-r / c, s) else none
  let hi := tightest (fun b a => decide (b < a)) <| cs.filterMap fun (c, r, s) =>
    if c < 0 then some (-r / c, s) else none
  let fits := fun v => zeroOk &&
    (match lo with | none => true | some (l, s) => if s then decide (l < v) else decide (l ≤ v)) &&
    (match hi with | none => true | some (h, s) => if s then decide (v < h) else decide (v ≤ h))
  match (cs.filterMap fun (c, r, _) => if c == 0 then none else some (-r / c)).find? fits, lo, hi with
  | some v, _, _ => v
  | none, some (l, _), some (h, _) => (l + h) / 2
  | none, some (l, _), none => l + 1
  | none, none, some (h, _) => h - 1
  | none, none, none => 0
theorem pickOnce_eq (x : String) (rows : List FM.Row) (κ : List (String × Rat)) :
    pickOnce x rows κ = FM.pick x rows κ := sorry

/-- What a side beyond the digit limit is known to be, without its values: constant (known nonzero, known zero, or
neither), not constant, or unknown (two sides that are not constant were added, and their coefficients may cancel). -/
inductive Shape where
  | const (nonzero : Option Bool)
  | nonconst
  | unknown
  deriving BEq, Repr

/-- A lowered side: its form; not linear (the decoder's `NonlinearPremise`); or linear, with a value beyond the digit
limit met on the way (the derivation is `unknown derivationInconclusive`), and its shape. -/
inductive Lowered where
  | form (L : QLin)
  | nonlinear
  | tooLarge (s : Shape)

def shapeOf (L : QLin) : Shape := if QLin.isConstOnce L then .const (some (L.const != 0)) else .nonconst

def Lowered.shape : Lowered → Shape
  | .form L => shapeOf L
  | .tooLarge s => s
  | .nonlinear => .unknown

/-- A linear form's size: its constant's and its coefficients'. -/
def formSize (L : QLin) : Nat := qbits L.const + (L.coeffs.map fun p => qbits p.2).sum

def fits (q : Rat) : Bool := q.num.natAbs < 10 ^ maxDigits && q.den < 10 ^ maxDigits

/-- A form built is charged its entries and its size, then held to the digit limit, its constant and each
coefficient; one beyond keeps its exact shape. -/
def chargeL (limit : Nat) (L : QLin) (w : Nat) : Option (Lowered × Nat) :=
  let w := w + entryUnits * L.coeffs.length + formSize L
  if limit < w then none
  else some (if fits L.const && L.coeffs.all (fits ·.2) then .form L else .tooLarge (shapeOf L), w)

/-- Whether 5's operation is linear, decided from its operands' shapes, or unknown from them. -/
inductive Linearity where
  | linear (s : Shape)
  | nonlinear
  | unknown

/-- A constant factor's effect on a side's shape (zero makes it the constant zero; nonzero keeps it). -/
def Shape.scale : Option Bool → Shape → Shape
  | some false, _ => .const (some false)
  | some true, s => s
  | none, .const (some false) => .const (some false)
  | none, .const _ => .const none
  | none, _ => .unknown

def addS : Shape → Shape → Linearity
  | .const (some false), s | s, .const (some false) => .linear s
  | .const _, .const _ => .linear (.const none)
  | .const _, .nonconst | .nonconst, .const _ => .linear .nonconst
  | _, _ => .linear .unknown

/-- 5's product: linear exactly when one side is constant, the left one tried first. -/
def mulS : Shape → Shape → Linearity
  | .const k, s | s, .const k => .linear (Shape.scale k s)
  | .nonconst, .nonconst => .nonlinear
  | _, _ => .unknown

/-- 5's quotient: linear exactly when the divisor is a nonzero constant. -/
def divS (a : Shape) : Shape → Linearity
  | .const (some true) => .linear a
  | .const (some false) | .nonconst => .nonlinear
  | _ => .unknown

def powS : Shape → Nat → Linearity
  | _, 0 => .linear (.const (some true))
  | s, 1 => .linear s
  | .const nz, _ => .linear (.const nz)
  | .nonconst, _ => .nonlinear
  | .unknown, _ => .unknown

/-- 12.2's size bounds of every value in `e`'s form, numerator and denominator, from its shape alone. -/
def Expr.bitsBound : Expr → Nat × Nat
  | .lit q => (bits q.num, bits q.den)
  | .val _ => (1, 1)
  | .add a b | .sub a b =>
    let ((na, da), (nb, db)) := (Expr.bitsBound a, Expr.bitsBound b); (max (na + db) (nb + da) + 1, da + db)
  | .mul a b => let ((na, da), (nb, db)) := (Expr.bitsBound a, Expr.bitsBound b); (na + nb, da + db)
  | .div a b => let ((na, da), (nb, db)) := (Expr.bitsBound a, Expr.bitsBound b); (na + db, da + nb)
  | .pow a k => let (na, da) := Expr.bitsBound a; (max 1 (na * k), max 1 (da * k))

def Expr.leaves : Expr → Nat
  | .lit _ => 0
  | .val _ => 1
  | .add a b | .sub a b | .mul a b | .div a b => Expr.leaves a + Expr.leaves b
  | .pow a _ => Expr.leaves a

/-- The units of lowering `e` exactly, whatever its values' sizes, known before it is computed: per node a visit,
its form's entries, and each of its values at `b · (log₂ b + 1)` for `b` bits (the cost of arithmetic beyond twice the
digit limit grows faster than its size). -/
def Expr.exactBound (e : Expr) : Nat :=
  let (n, d) := Expr.bitsBound e
  let b := n + d
  let own := 1 + entryUnits * Expr.leaves e + (Expr.leaves e + 1) * b * (b.log2 + 1)
  own + match e with
    | .lit _ | .val _ => 0
    | .add a b | .sub a b | .mul a b | .div a b => Expr.exactBound a + Expr.exactBound b
    | .pow a _ => Expr.exactBound a

/-- The exact lowering, charged its bound first: only where the shapes leave 5's linearity unknown (a product,
quotient or power of a side whose coefficients beyond the digit limit may cancel). It stays `tooLarge`. -/
def exactC (limit : Nat) (e : Expr) (w : Nat) : Option (Lowered × Nat) :=
  if limit < w + Expr.exactBound e then none
  else some ((match e.linear with | none => .nonlinear | some L => .tooLarge (shapeOf L)), w + Expr.exactBound e)

def decided (limit : Nat) (e : Expr) (w : Nat) : Linearity → Option (Lowered × Nat)
  | .linear s => some (.tooLarge s, w)
  | .nonlinear => some (.nonlinear, w)
  | .unknown => exactC limit e w

/-- Two operands' lowerings: forms are combined and charged; a side not linear decides; otherwise the shapes do. -/
def binL (limit : Nat) (e : Expr) (f : QLin → QLin → Option QLin) (g : Shape → Shape → Linearity) :
    Lowered → Lowered → Nat → Option (Lowered × Nat)
  | .nonlinear, _, w | _, .nonlinear, w => some (.nonlinear, w)
  | .form L, .form M, w => match f L M with
    | some N => chargeL limit N w
    | none => some (.nonlinear, w)
  | a, b, w => decided limit e w (g a.shape b.shape)

/-- One node of 5's `Expr.linear` from its operands' lowerings (`e` is the inlined node, for the exact fallback). -/
def stepC (limit : Nat) (e : Expr) (parts : List Lowered) (w : Nat) : Option (Lowered × Nat) :=
  match e, parts with
  | .add .., [a, b] => binL limit e (fun L M => some (QLin.normOnce (L.add M))) addS a b w
  | .sub .., [a, b] => binL limit e (fun L M => some (QLin.normOnce (L.add (M.scale (-1))))) addS a b w
  | .mul .., [a, b] => binL limit e (fun L M =>
      if QLin.isConstOnce L then some (M.scale L.const)
      else if QLin.isConstOnce M then some (L.scale M.const) else none)
      mulS a b w
  | .div .., [a, b] => binL limit e (fun L M =>
      if QLin.isConstOnce M && M.const != 0 then some (L.scale (1 / M.const)) else none) divS a b w
  | .pow _ k, [.form L] =>
    if QLin.isConstOnce L then
      if powTooLarge L.const k then some (.tooLarge (.const (some true)), w) else chargeL limit ⟨L.const ^ k, []⟩ w
    else match k with
      | 0 => chargeL limit ⟨1, []⟩ w
      | 1 => some (.form L, w)
      | _ => some (.nonlinear, w)
  | .pow _ _, [.nonlinear] => some (.nonlinear, w)
  | .pow _ k, [.tooLarge s] => decided limit e w (powS s k)
  | _, _ => none

/-- 5's `Expr.linear` over an inlined expression, charged: one visit per node and each form built its entries and
size; a constant's power beyond the digit limit is known from its base (`powTooLarge`) and never computed. A left
operand that is not linear ends the node, as `do` does in 5. -/
def Expr.linearC (limit : Nat) : Expr → Nat → Option (Lowered × Nat)
  | .lit q, w => charge limit w (chargeL limit ⟨q, []⟩)
  | .val n, w => charge limit w (chargeL limit ⟨0, [(n, 1)]⟩)
  | e@(.add a b), w | e@(.sub a b), w | e@(.mul a b), w | e@(.div a b), w => charge limit w fun w =>
    match Expr.linearC limit a w with
    | none => none
    | some (.nonlinear, w) => some (.nonlinear, w)
    | some (la, w) => (Expr.linearC limit b w).bind fun (lb, w) => stepC limit e [la, lb] w
  | e@(.pow a _), w => charge limit w fun w => (Expr.linearC limit a w).bind fun (la, w) => stepC limit e [la] w

/-- The charged lowering decides 5's linearity exactly: a form is 5's form, `nonlinear` is 5's `none`, and a side
beyond the digit limit is linear in 5 with the shape it carries. So the decoder refuses exactly the cases it refuses
today (`NonlinearPremise`), and a value beyond the digit limit only ends a derivation. -/
def Shape.Sound (L : QLin) : Shape → Prop
  | .const nz => L.isConst = true ∧ ∀ b, nz = some b → (L.const != 0) = b
  | .nonconst => L.isConst = false
  | .unknown => True
theorem Expr.linearC_form (limit : Nat) (e : Expr) (w : Nat) (L : QLin) (w' : Nat)
    (h : Expr.linearC limit e w = some (.form L, w')) : e.linear = some L := sorry
theorem Expr.linearC_nonlinear (limit : Nat) (e : Expr) (w w' : Nat)
    (h : Expr.linearC limit e w = some (.nonlinear, w')) : e.linear = none := sorry
theorem Expr.linearC_tooLarge (limit : Nat) (e : Expr) (w : Nat) (s : Shape) (w' : Nat)
    (h : Expr.linearC limit e w = some (.tooLarge s, w')) : ∃ L, e.linear = some L ∧ Shape.Sound L s := sorry

/-- The decoder's linearity check (3.1's `NonlinearPremise`), charged: each side lowered once, bottom-up over the side
as written, each node's lowering built from its parts' (a name's from its inlined definition), so a side costs its
`linearC` and never more. It names 5's innermost part that is not linear (`Wire.nonlinearAt`'s path); a part whose
inlining has a fault or more than `maxPolyTerms` nodes is not judged, and neither is any node above it. -/
def nonlinearAtC (limit : Nat) (t : Inlined) (path : String) (e : Expr) (w : Nat) :
    Option ((Option String × Option Lowered) × Nat) :=
  let judged : Option Expr := match e.subst t with
    | .ok e' => if (e'.nodesWithin maxPolyTerms).isSome then some e' else none
    | .error _ => none
  let mark := fun (l : Lowered) w => some ((match l with | .nonlinear => some path | _ => none, some l), w)
  let node := fun (parts : List (Option Lowered)) (w : Nat) => match judged, parts.mapM id with
    | some e', some ls => (stepC limit e' ls w).bind fun (l, w) => mark l w
    | _, _ => some ((none, none), w)
  match e with
  | .lit _ | .val _ => match judged with
    | some e' => (Expr.linearC limit e' w).bind fun (l, w) => mark l w
    | none => some ((none, none), w)
  | .add a b | .sub a b | .mul a b | .div a b =>
    match nonlinearAtC limit t s!"{path}.1" a w with
    | none => none
    | some ((some p, _), w) => some ((some p, none), w)
    | some ((none, la), w) => match nonlinearAtC limit t s!"{path}.2" b w with
      | none => none
      | some ((some p, _), w) => some ((some p, none), w)
      | some ((none, lb), w) => charge limit w (node [la, lb])
  | .pow a _ => match nonlinearAtC limit t s!"{path}.1" a w with
    | none => none
    | some ((some p, _), w) => some ((some p, none), w)
    | some ((none, la), w) => charge limit w (node [la])
theorem nonlinearAtC_eq (limit : Nat) (t : Inlined) (path : String) (e : Expr) (w : Nat) (r : Option String)
    (l : Option Lowered) (w' : Nat) (h : nonlinearAtC limit t path e w = some ((r, l), w')) :
    r = Wire.nonlinearAt t path e := sorry

/-- A search row's size (5's elimination): its fact's form and its weights. Each row `FM.eliminate` builds is charged
one unit, `entryUnits` per entry (coefficients and weights) and its size to the case's units, and held to the digit
limit (me-2nc); so is each pass over a stage's rows (`eliminate`'s three filters, `pickOnce`'s two passes). -/
def rowSize (r : FM.Row) : Nat := formSize r.fact.form + (r.weights.map qbits).sum
def rowCost (r : FM.Row) : Nat := 1 + entryUnits * (r.fact.form.coeffs.length + r.weights.length) + rowSize r
/-- One pass over a stage's rows, as `pickOnce` and each of `eliminate`'s filters make: each row's coefficients. -/
def passCost (rows : List FM.Row) : Nat := (rows.map fun r => 1 + entryUnits * r.fact.form.coeffs.length).sum

end VE.Calc.Work

/-! ## The fixtures of 3.2 (units *by hand*: this file's evaluator, not product code) -/

namespace VE.Calc.Work.Fixtures
open VE.Calc VE.Numbers VE.Calc.Work

def eqc : Comparison := ⟨.eq, false⟩
def ltc : Comparison := ⟨.lt, false⟩
def stated (n : String) (q : Rat) : Decl := ⟨n, .stated q⟩
def defd (n : String) (e : Expr) : Decl := ⟨n, .defined e⟩
def mk (ds : List Decl) (cs : List Claim) : Case := ⟨ds, cs.zipIdx.map fun (c, i) => (s!"c{i}", .claim c), none⟩
def units (limit : Nat) (c : Case) : Option Nat := (runC limit c).map (·.2)
def outcomes (c : Case) : Option (List Outcome) := (runC maxWork c).map fun r => r.1.map (·.1)
/-- Product code's rows (2.4's `Claim.run`, re-reading every value), for agreement where it is fast enough. -/
def product (c : Case) : List Outcome := c.claims.map fun k => k.2.run c.decls
def nines : Rat := 10 ^ 40 - 1

/-! F1-24, F1-28, F1-511: me-2b review F1's chain, v0 = 1 and v(i+1) = v(i) + v(i). Units 9 + 9k + 3k(k + 1)/2 for
`v_k = 2^k` (3.2); product code agrees at k = 12; under, at and over F1-24's units. -/
def f1 (k : Nat) : List Decl :=
  stated "v0" 1 :: (List.range k).map fun i => defd s!"v{i + 1}" (.add (.val s!"v{i}") (.val s!"v{i}"))
def f1Case (k : Nat) : Case := mk (f1 k) [.compare eqc (.val s!"v{k}") (.lit (2 ^ k))]
#guard [24, 28].map (fun k => units maxWork (f1Case k)) = [some 1125, some 1479]
#guard [24, 28].all fun k => units maxWork (f1Case k) == some (9 + 9 * k + 3 * k * (k + 1) / 2)
#guard outcomes (f1Case 28) = some [.decided .holds]
#guard units maxWork (mk (f1 511) [.compare ltc (.lit 0) (.val "v511")]) = some 396545
#guard some (product (f1Case 12)) = outcomes (f1Case 12)
#guard [1124, 1125, 1126].map (units · (f1Case 24)) = [none, some 1125, some 1125]

/-! G-1: one power of a 2,560-digit value, 18.7 s today (the digit list of 2.4's guard); here the power is known to be
beyond the limit from its base and never computed. G-1x512: the same claim 512 times. -/
def g1 (n : Nat) : Case := mk [stated "v0" nines, defd "v1" (.pow (.val "v0") 64)]
  ((List.range n).map fun _ => .compare ltc (.pow (.val "v1") 64) (.lit 0))
#guard units maxWork (g1 1) = some 17288 && outcomes (g1 1) == some [.unknown (.limit .digits)]
#guard units maxWork (g1 512) = some 4366409

/-! V-11's shape: values at 40, 2,497 and 4,993 digits, and a zero divisor after a limit; product code agrees. -/
def v11 : Case := mk [stated "a" (10 ^ 39), defd "b" (.pow (.val "a") 64), defd "c" (.pow (.val "b") 2)]
  [.compare ltc (.val "a") (.lit 0), .compare ltc (.val "b") (.lit 0), .compare ltc (.val "c") (.lit 0),
   .compare ltc (.div (.val "c") (.lit 0)) (.lit 0)]
#guard some (product v11) = outcomes v11 && units maxWork v11 == some 25297

/-! H-1: near the most a claim case can spend. b has 4,080 digits over 4,080 (27,108 bits); 497 claims b·b = b·b
(20 JSON values each) fill 10,000 JSON values: 107,837,424 units, under 3.2's bound 163,290,000 and far under limit 10. -/
def heavy (n : Nat) : Case :=
  let m : Expr := .mul (.val "b") (.val "b")
  mk [stated "r" ((10 ^ 40 - 1) / (10 ^ 40 - 3)), defd "b" (.mul (.pow (.val "r") 64) (.pow (.val "r") 38))]
    ((List.range n).map fun _ => .compare eqc m m)
#guard units maxWork (heavy 497) = some 107837424 && 107837424 < 163290000 && 163290000 < maxWork

/-! L-1 to L-4: a premise over the constant c^(64^k), c = 10^40 − 1. L-1 lowers (2,560 digits); L-2 to L-4 are beyond
the digit limit, known from the base (L-2 holds today in 0.07 s; L-3 takes 12.7 s; L-4 passes the deadline). -/
def powChain : Nat → Expr
  | 0 => .lit nines
  | k + 1 => .pow (powChain k) 64
def lowered (e : Expr) : Option (Option QLin × Nat) := (Expr.linearC maxWork e 0).map fun
  | (.form L, w) => (some L, w)
  | (_, w) => (none, w)
#guard (lowered (powChain 1)).map (·.1) = some (powChain 1).linear
#guard [1, 2, 3, 4].map (fun k => (lowered (powChain k)).map (·.2)) = [some 8642, some 8643, some 8644, some 8645]
#guard [2, 3, 4].all fun k => match Expr.linearC maxWork (powChain k) 0 with
  | some (.tooLarge _, _) => true
  | _ => false
/-- L-5: a product of two constants of 4,080 digits is computed, charged, then beyond the limit. -/
def big : Expr := .mul (.pow (.lit nines) 64) (.pow (.lit nines) 38)
#guard match Expr.linearC maxWork (.mul big big) 0 with | some (.tooLarge _, w) => w == 81879 | _ => false

/-! P-1: me-2b's fan-out, a premise over a12 = a11 + a11 (8,191 nodes inlined), lowered once per case, not once per
mention (20 derivations naming it 450 times take 29 s today). P-2: the same doubling over 16 free values with
800-digit coefficients, 8 levels: 118,478,125 units a premise, most of them its forms' entries; a case of 72
such premises is under limit 10, of 73 over it (4.4 and 4.7 s today; me-2nc pins the case's exact units). -/
def keep : List String := (List.range 16).map (s!"u{·}")
def lowerName (ds : List Decl) (n : String) : Option (Option QLin × Nat) :=
  match Expr.inline ds keep (.val n) with
  | .ok e => lowered e
  | .error _ => none
def fan (k : Nat) : List Decl :=
  ⟨"u0", .free⟩ :: defd "a0" (.val "u0") ::
    (List.range k).map fun i => defd s!"a{i + 1}" (.add (.val s!"a{i}") (.val s!"a{i}"))
#guard (lowerName (fan 12) "a12").map (·.2) = some 16824301
#guard match Expr.inline (fan 12) keep (.val "a12") with
  | .ok e => (e.nodesWithin maxPolyTerms).isSome && (lowered e).map (·.1) == some e.linear
  | .error _ => false
def dense (k : Nat) : List Decl :=
  keep.map (fun n => (⟨n, .free⟩ : Decl)) ++
  [defd "big" (.pow (.lit nines) 20),
   defd "a0" (.mul (.val "big") ((List.range 15).foldl (fun e j => .add e (.val s!"u{j + 1}")) (.val "u0")))] ++
  (List.range k).map fun i => defd s!"a{i + 1}" (.add (.val s!"a{i}") (.val s!"a{i}"))
#guard (lowerName (dense 8) "a8").map (·.2) = some 118478125
#guard 72 * 118478125 < maxWork && maxWork < 73 * 118478125

/-! S-1 to S-10 (me-2n review F2): a side beyond the digit limit still has 5's linearity. C = c^4096 is beyond the limit
and never computed; `x + C` is linear and not constant, so its square and its product with `x` are not linear, and
the decoder refuses them (`NonlinearPremise`) as it does today. S-8 to S-10 add sides whose coefficients beyond the
limit may cancel; their linearity is decided exactly, charged before it is computed (`exactC`). -/
def C : Expr := powChain 2
def xC : Expr := .add (.val "x") C
def shapes : List Expr :=
  [.pow xC 2, .mul xC (.val "x"), .div (.val "x") xC,                                  -- S-1 to S-3: not linear
   .mul xC C, .div xC C, .pow xC 1, .pow xC 0,                                         -- S-4 to S-7: linear
   .mul (.sub (.mul C (.val "x")) (.mul C (.val "x"))) (.val "x"),                      -- S-8: cancels, linear
   .mul (.sub (.mul C (.val "x")) (.mul C (.val "y"))) (.val "x"),                      -- S-9: not linear
   .div (.val "x") (.sub C C)]                                                          -- S-10: a zero divisor
def linearity (e : Expr) : Option Bool := (Expr.linearC maxWork e 0).map fun
  | (.nonlinear, _) => false
  | _ => true
#guard shapes.map linearity = [false, false, false, true, true, true, true, true, false, false].map some
#guard shapes.all fun e => linearity e == some e.linear.isSome
-- S-1 costs its lowering; S-8 its exact lowering's bound, which charges big values more than their size.
#guard [0, 7].map (fun i => (Expr.linearC maxWork (shapes.getD i (.lit 0)) 0).map (·.2)) = [some 10698, some 144138778]
#guard match Expr.linearC maxWork (shapes.getD 7 (.lit 0)) 0 with
  | some (.tooLarge s, _) => s == .const (some false)
  | _ => false

/-! The one-pass steps equal 5's (me-2n review F1). N-1 is the review's `QLin.norm` case: a side of 8 mentions of
a sum of 400 free values. -/
def names (k : Nat) : List String := (List.range k).map (s!"v{·}")
def forms : List QLin :=
  [⟨1, [("a", 1), ("b", 2), ("a", -1), ("c", 0), ("b", 1/2)]⟩, ⟨0, [("a", 1), ("a", -1)]⟩, ⟨3, []⟩,
   ⟨0, (names 400).map (·, 1) ++ (names 400).reverse.map (·, 2)⟩]
#guard forms.all fun L => QLin.normOnce L == L.norm && QLin.isConstOnce L == L.isConst
def pairUp : List Expr → List Expr
  | a :: b :: r => .add a b :: pairUp r
  | r => r
/-- The review probe's balanced sum: neighbours paired, round by round. -/
def balanced (es : List Expr) : Expr := ((List.range 12).foldl (fun acc _ => pairUp acc) es).headD (.lit 0)
def n1Side : Expr := balanced ((List.range 8).map fun _ => balanced ((names 400).map .val))
#guard (lowered n1Side).map (·.2) = some 70576397

/-! The pick probe's stages (me-2n review F1): 0 < x − k_i and 0 < s + b_j − x over s = y + z1 + ... + z14, for the
conclusion y < 0; bounds on y increasing (`inc`) or decreasing in row order. -/
def zs : List String := (List.range 14).map (s!"z{· + 1}")
def probeFacts (sign : Int) (np nn : Nat) : List QFact :=
  (List.range np).map (fun i => ⟨⟨-(sign * 1000 * i), [("x", 1)]⟩, true⟩) ++
  (List.range nn).map (fun j => ⟨⟨-(sign * j), ("y", 1) :: zs.map (·, 1) ++ [("x", -1)]⟩, true⟩) ++
  [⟨⟨0, [("y", 1)]⟩, false⟩]
def stageY (fs : List QFact) : List FM.Row :=
  match (FM.run (FM.unknowns fs) (FM.inputRows fs) []).run' FM.maxSteps with
  | .ok (_, stages) => ((stages.find? (·.1 == "y")).map (·.2)).getD []
  | .error _ => []
def κz : List (String × Rat) := zs.map (·, 0)
def mixed : List FM.Row := [⟨1, [("x", 2)]⟩, ⟨-3, [("x", 1), ("y", 1)]⟩, ⟨-4, [("x", 2)]⟩, ⟨5, [("x", -1)]⟩,
  ⟨5, [("x", -1)]⟩, ⟨2, [("y", 1)]⟩].zipIdx.map fun ((c, l), i) => ⟨⟨⟨c, l⟩, i % 2 == 0⟩, [1]⟩
#guard [1, -1].all fun sign => let r := stageY (probeFacts sign 8 7); r.length == 57 &&
  pickOnce "y" r κz == FM.pick "y" r κz
#guard [mixed, mixed.reverse, mixed.take 3, mixed.drop 3, []].all fun r =>
  [[], [("y", 1)], [("y", -7)]].all fun κ => pickOnce "x" r κ == FM.pick "x" r κ
#guard let fs := probeFacts 1 3 2 ++ [⟨⟨-1, [("y", -1)]⟩, false⟩]
  match (FM.search fs).run' FM.maxSteps with
  | .ok (.refuted ws) => [ws, ws.map (· * 2), ws.map (· - 1), ws.drop 1].all fun ws =>
      Farkas.checkOnce fs ⟨ws⟩ == Farkas.check fs ⟨ws⟩
  | _ => false
def stage992 : List FM.Row := stageY (probeFacts 1 32 31)
#guard stage992.length == 993
#guard (stage992.map rowCost).sum + 2 * passCost stage992 = 221757785

/-! The decoder's check, once per side, names the part 5 names: a product inside a definition (`sq`), an unknown
name, P-1, a side beyond `maxPolyTerms` nodes, and S-1, S-2 and S-8 as premises over the declared value `C`. -/
def decoderDecls : List Decl :=
  [⟨"x", .free⟩, ⟨"y", .free⟩, defd "C" C, defd "sq" (.mul (.val "x") (.val "x"))] ++ fan 14
def decoderSides : List Expr :=
  [.add (.val "sq") (.lit 1), .add (.val "x") (.val "nope"), .val "a12", .val "a14", .mul (.val "a14") (.val "x"),
   .pow (.add (.val "x") (.val "C")) 2, .mul (.add (.val "x") (.val "C")) (.val "x"),
   .mul (.sub (.mul (.val "C") (.val "x")) (.mul (.val "C") (.val "x"))) (.val "x")]
#guard let t := inlineTable decoderDecls (freeNames decoderDecls)
  decoderSides.zipIdx.all fun (e, i) =>
    ((nonlinearAtC maxWork t s!"p{i}" e 0).map (·.1.1)) == some (Wire.nonlinearAt t s!"p{i}" e)
#guard let t := inlineTable decoderDecls (freeNames decoderDecls)
  decoderSides.zipIdx.map (fun (e, i) => Wire.nonlinearAt t s!"p{i}" e) =
    [some "p0.1", none, none, none, none, some "p5", some "p6", none]

end VE.Calc.Work.Fixtures
