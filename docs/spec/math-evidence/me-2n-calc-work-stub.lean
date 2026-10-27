import VE.Calc.Run

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

/-! ## (b) for derivations: 5's lowering held to the digit limit and charged; each premise lowered once per case -/

/-- A lowered side: its form, not linear (the decoder's `NonlinearPremise`), or a value beyond the digit limit (the
derivation is `unknown derivationInconclusive`, never `NonlinearPremise`). -/
inductive Lowered where
  | form (L : QLin)
  | nonlinear
  | tooLarge

/-- A linear form's size: its constant's and its coefficients'. -/
def formSize (L : QLin) : Nat := qbits L.const + (L.coeffs.map fun p => qbits p.2).sum

def fits (q : Rat) : Bool := q.num.natAbs < 10 ^ maxDigits && q.den < 10 ^ maxDigits

/-- A form built is charged its size, then held to the digit limit, its constant and each coefficient. -/
def chargeL (limit : Nat) (L : QLin) (w : Nat) : Option (Lowered × Nat) :=
  if limit < w + formSize L then none
  else some (if fits L.const && L.coeffs.all (fits ·.2) then .form L else .tooLarge, w + formSize L)

/-- Both operands' forms, then `f`'s form charged; the first side that is not a form decides, as `do` does in 5. -/
def both (limit : Nat) (a : Option (Lowered × Nat)) (b : Nat → Option (Lowered × Nat))
    (f : QLin → QLin → Option QLin) : Option (Lowered × Nat) :=
  match a with
  | some (.form L, w) => match b w with
    | some (.form M, w) => match f L M with
      | some N => chargeL limit N w
      | none => some (.nonlinear, w)
    | r => r
  | r => r

/-- 5's `Expr.linear` over an inlined expression, charged: one visit per node and each form built its size; a
constant's power beyond the digit limit is known from its base (`powTooLarge`) and never computed. -/
def Expr.linearC (limit : Nat) : Expr → Nat → Option (Lowered × Nat)
  | .lit q, w => charge limit w (chargeL limit ⟨q, []⟩)
  | .val n, w => charge limit w (chargeL limit ⟨0, [(n, 1)]⟩)
  | .add a b, w => charge limit w fun w =>
      both limit (Expr.linearC limit a w) (Expr.linearC limit b) fun L M => some (L.add M).norm
  | .sub a b, w => charge limit w fun w =>
      both limit (Expr.linearC limit a w) (Expr.linearC limit b) fun L M => some (L.add (M.scale (-1))).norm
  | .mul a b, w => charge limit w fun w => both limit (Expr.linearC limit a w) (Expr.linearC limit b) fun L M =>
      if L.isConst then some (M.scale L.const) else if M.isConst then some (L.scale M.const) else none
  | .div a b, w => charge limit w fun w => both limit (Expr.linearC limit a w) (Expr.linearC limit b) fun L M =>
      if M.isConst && M.const != 0 then some (L.scale (1 / M.const)) else none
  | .pow a k, w => charge limit w fun w => match Expr.linearC limit a w with
    | some (.form L, w) =>
      if L.isConst then (if powTooLarge L.const k then some (.tooLarge, w) else chargeL limit ⟨L.const ^ k, []⟩ w)
      else match k with
        | 0 => chargeL limit ⟨1, []⟩ w
        | 1 => some (.form L, w)
        | _ => some (.nonlinear, w)
    | r => r

/-- The charged lowering agrees with 5's wherever it gives a form or finds a side not linear. -/
theorem Expr.linearC_form (limit : Nat) (e : Expr) (w : Nat) (L : QLin) (w' : Nat)
    (h : Expr.linearC limit e w = some (.form L, w')) : e.linear = some L := sorry
theorem Expr.linearC_nonlinear (limit : Nat) (e : Expr) (w w' : Nat)
    (h : Expr.linearC limit e w = some (.nonlinear, w')) : e.linear = none := sorry

/-- A search row's size (5's elimination): its fact's form and its weights. Each row `FM.eliminate` builds is charged
one unit and its size to the case's units, and held to the digit limit (me-2nc). -/
def rowSize (r : FM.Row) : Nat := formSize r.fact.form + (r.weights.map qbits).sum

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
#guard [2, 3, 4].all fun k => match Expr.linearC maxWork (powChain k) 0 with | some (.tooLarge, _) => true | _ => false

/-! P-1: me-2b's fan-out, a premise over a12 = a11 + a11 (8,191 nodes inlined), lowered once per case, not once per
mention (20 derivations naming it 450 times take 29 s today). P-2: the same doubling over 16 free values with
4,080-digit coefficients, 8 levels: 117,946,925 units a premise; a case of 72 such premises is under limit 10, of
73 over it (4 to 5 s today; me-2nc pins the case's exact units). -/
def keep : List String := (List.range 16).map (s!"u{·}")
def lowerName (ds : List Decl) (n : String) : Option (Option QLin × Nat) :=
  match Expr.inline ds keep (.val n) with
  | .ok e => lowered e
  | .error _ => none
def fan (k : Nat) : List Decl :=
  ⟨"u0", .free⟩ :: defd "a0" (.val "u0") ::
    (List.range k).map fun i => defd s!"a{i + 1}" (.add (.val s!"a{i}") (.val s!"a{i}"))
#guard (lowerName (fan 12) "a12").map (·.2) = some 49133
#guard match Expr.inline (fan 12) keep (.val "a12") with
  | .ok e => (e.nodesWithin maxPolyTerms).isSome && (lowered e).map (·.1) == some e.linear
  | .error _ => false
def dense (k : Nat) : List Decl :=
  keep.map (fun n => (⟨n, .free⟩ : Decl)) ++
  [defd "big" (.mul (.pow (.lit nines) 64) (.pow (.lit nines) 38)),
   defd "a0" (.mul (.val "big") ((List.range 15).foldl (fun e j => .add e (.val s!"u{j + 1}")) (.val "u0")))] ++
  (List.range k).map fun i => defd s!"a{i + 1}" (.add (.val s!"a{i}") (.val s!"a{i}"))
#guard (lowerName (dense 8) "a8").map (·.2) = some 117946925
#guard 72 * 117946925 < maxWork && maxWork < 73 * 117946925

end VE.Calc.Work.Fixtures
