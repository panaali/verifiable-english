import VE.Calc.Inline
import VE.Calc.Derive

/-! The lowering of a derivation's claims to facts over the free values (spec 5, J3), and the meaning of a derivation
with its bridge theorems: a certificate or a counterexample checked over the lowered facts is one of the derivation.
Inlining is `Claim.inline` (`Inline.lean`), keeping the free values. -/

namespace VE.Calc

/-- A form whose every coefficient cancels: its value is its constant (`QLin.eval_of_cancel`). -/
def QLin.isConst (L : QLin) : Bool := (L.coeffs.map (·.1)).all fun n => L.coeffOf n == 0

/-- The linear form of an expression over the free values, or none when it is not linear: a product of two forms
neither of them constant, a power of a form that is not constant other than its 0th and 1st, or a division by a
form that is not a nonzero constant. A sum is normalised (`QLin.norm`), one coefficient per unknown, so a chain of
definitions gives a form no longer than its unknowns. -/
def Expr.linear : Expr → Option QLin
  | .lit q => some ⟨q, []⟩
  | .val n => some ⟨0, [(n, 1)]⟩
  | .add a b => do return ((← a.linear).add (← b.linear)).norm
  | .sub a b => do return ((← a.linear).add ((← b.linear).scale (-1))).norm
  | .mul a b => do
      let (L, M) := (← a.linear, ← b.linear)
      if L.isConst then return M.scale L.const
      if M.isConst then return L.scale M.const
      none
  | .div a b => do
      let (L, M) := (← a.linear, ← b.linear)
      if M.isConst && M.const != 0 then return L.scale (1 / M.const)
      none
  | .pow a k => do
      let L ← a.linear
      if L.isConst then return ⟨L.const ^ k, []⟩
      match k with
      | 0 => return ⟨1, []⟩
      | 1 => return L
      | _ => none

/-- 5's `QLin.isConst` in one pass: every coefficient cancels. -/
def QLin.isConstOnce (L : QLin) : Bool := (QLin.normOnce L).coeffs.isEmpty

theorem QLin.isConstOnce_eq (L : QLin) : QLin.isConstOnce L = L.isConst := by
  simp only [QLin.isConstOnce, QLin.normOnce_eq, QLin.norm_coeffs_isEmpty, QLin.isConst]

namespace Work

/-! ## The charged lowering (3.2 (b), me-2nc): one visit per node, each form its entries and size, each value held to
the digit limit, 5's linearity kept exactly. -/

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

def shapeOf (L : QLin) : Shape := if L.isConstOnce then .const (some (L.const != 0)) else .nonconst

def Lowered.shape : Lowered → Shape
  | .form L => shapeOf L
  | .tooLarge s => s
  | .nonlinear => .unknown

/-- One node's lowering: its units, known before its result is computed, and that result. -/
structure Node where
  units : Nat
  result : Unit → Lowered

/-- A result that costs nothing more. -/
def Node.free (l : Lowered) : Node := ⟨0, fun _ => l⟩

/-- `limit`'s refusal comes before the result is computed. -/
def Node.run (limit : Nat) (n : Node) (w : Nat) : Option (Lowered × Nat) :=
  if limit < w + n.units then none else some (n.result (), w + n.units)

/-- A form built is charged its entries and its size, then held to the digit limit, its constant and each
coefficient; one beyond keeps its exact shape. -/
def chargeL (L : QLin) : Node :=
  ⟨entryUnits * L.coeffs.length + formSize L, fun _ =>
    if decide (Small L.const) && L.coeffs.all (fun p => decide (Small p.2)) then .form L else .tooLarge (shapeOf L)⟩

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
  | .lit q => (VE.Numbers.bits q.num, VE.Numbers.bits q.den)
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
def exactNode (e : Expr) : Node := ⟨Expr.exactBound e, fun _ => match e.linear with
  | none => .nonlinear
  | some L => .tooLarge (shapeOf L)⟩

def exactC (limit : Nat) (e : Expr) (w : Nat) : Option (Lowered × Nat) := (exactNode e).run limit w

def decided (e : Expr) : Linearity → Node
  | .linear s => .free (.tooLarge s)
  | .nonlinear => .free .nonlinear
  | .unknown => exactNode e

/-- Two operands' lowerings: forms are combined and charged; a side not linear decides; otherwise the shapes do. -/
def binL (e : Expr) (f : QLin → QLin → Option QLin) (g : Shape → Shape → Linearity) : Lowered → Lowered → Node
  | .nonlinear, _ | _, .nonlinear => .free .nonlinear
  | .form L, .form M => match f L M with
    | some N => chargeL N
    | none => .free .nonlinear
  | a, b => decided e (g a.shape b.shape)

/-- One node of 5's `Expr.linear` from its operands' lowerings (`e` is the inlined node, for the exact fallback); a
constant's power beyond the digit limit is known from its base (`powTooLarge`) and never computed. -/
def stepNode (e : Expr) (parts : List Lowered) : Node :=
  match e, parts with
  | .add .., [a, b] => binL e (fun L M => some (QLin.normOnce (L.add M))) addS a b
  | .sub .., [a, b] => binL e (fun L M => some (QLin.normOnce (L.add (M.scale (-1))))) addS a b
  | .mul .., [a, b] => binL e (fun L M =>
      if L.isConstOnce then some (M.scale L.const) else if M.isConstOnce then some (L.scale M.const) else none) mulS a b
  | .div .., [a, b] => binL e (fun L M =>
      if M.isConstOnce && M.const != 0 then some (L.scale (1 / M.const)) else none) divS a b
  | .pow _ k, [.form L] =>
    if L.isConstOnce then
      if powTooLarge L.const k then .free (.tooLarge (.const (some true))) else chargeL ⟨L.const ^ k, []⟩
    else match k with
      | 0 => chargeL ⟨1, []⟩
      | 1 => .free (.form L)
      | _ => .free .nonlinear
  | .pow _ _, [.nonlinear] => .free .nonlinear
  | .pow _ k, [.tooLarge s] => decided e (powS s k)
  | _, _ => .free .nonlinear

/-- 5's `Expr.linear` over an inlined expression, charged: one visit per node and each form built its entries and
size. A left operand that is not linear ends the node, as `do` does in 5. -/
def Expr.linearC (limit : Nat) : Expr → Nat → Option (Lowered × Nat)
  | .lit q, w => visitC limit w ((chargeL ⟨q, []⟩).run limit)
  | .val n, w => visitC limit w ((chargeL ⟨0, [(n, 1)]⟩).run limit)
  | e@(.add a b), w | e@(.sub a b), w | e@(.mul a b), w | e@(.div a b), w => visitC limit w fun w =>
    match Expr.linearC limit a w with
    | none => none
    | some (.nonlinear, w) => some (.nonlinear, w)
    | some (la, w) => (Expr.linearC limit b w).bind fun (lb, w) => (stepNode e [la, lb]).run limit w
  | e@(.pow a _), w => visitC limit w fun w =>
    (Expr.linearC limit a w).bind fun (la, w) => (stepNode e [la]).run limit w

/-- What a shape says of a form, in 5's terms. -/
def Shape.Sound (L : QLin) : Shape → Prop
  | .const nz => L.isConst = true ∧ ∀ b, nz = some b → (L.const != 0) = b
  | .nonconst => L.isConst = false
  | .unknown => True

/-- What a lowering says of 5's `Expr.linear`. -/
def Lowered.Sound (o : Option QLin) : Lowered → Prop
  | .form L => o = some L
  | .nonlinear => o = none
  | .tooLarge s => ∃ L, o = some L ∧ Shape.Sound L s

/-- What the operands' shapes say of 5's result. -/
def Linearity.Sound (o : Option QLin) : Linearity → Prop
  | .linear s => ∃ L, o = some L ∧ Shape.Sound L s
  | .nonlinear => o = none
  | .unknown => True

end Work

/-- `x − y ≥ 0`, or `> 0` when strict. -/
def QFact.sub (x y : QLin) (strict : Bool) : QFact := ⟨x.add (y.scale (-1)), strict⟩

/-- An inlined claim's facts: `eq` and `within` give two, `lt`, `le`, `gt` and `ge` one, a rounding claim none. -/
def Claim.lower : Claim → Option (List QFact)
  | .compare c a b => do
      let (A, B) := (← a.linear, ← b.linear)
      let (x, y) := if c.swap then (B, A) else (A, B)
      match c.rel with
      | .eq => return [QFact.sub x y false, QFact.sub y x false]
      | .lt => return [QFact.sub y x true]
      | .le => return [QFact.sub y x false]
  | .within e lo hi => do
      let (x, l, h) := (← e.linear, ← lo.linear, ← hi.linear)
      return [QFact.sub x l false, QFact.sub h x false]
  | .rounds .. => none

/-- The lowering of a premise or conclusion to facts over the free values (J3): inline (2.7), linearise; `eq` and
`within` give two facts, `lt`, `le`, `gt` and `ge` one; none when the claim is not linear in the free values or reads
a value that has none. -/
def Claim.facts (ds : List Decl) (c : Claim) : Option (List QFact) :=
  match c.inline ds (freeNames ds) with
  | .ok c' => c'.lower
  | .error _ => none

theorem QLin.eval_isConst (κ : String → Rat) (L : QLin) (h : L.isConst = true) : L.eval κ = L.const :=
  QLin.eval_of_cancel κ L (by simpa [QLin.isConst] using h)

theorem FM.firstAppearance_spec (ns acc : List String) (h : acc.Nodup) :
    (ns.foldl (fun acc n => if n ∈ acc then acc else acc ++ [n]) acc).Nodup ∧
      ∀ n, n ∈ ns.foldl (fun acc n => if n ∈ acc then acc else acc ++ [n]) acc ↔ n ∈ acc ∨ n ∈ ns := by
  induction ns generalizing acc with
  | nil => simpa using h
  | cons m ns ih =>
    by_cases hm : m ∈ acc
    · simp only [List.foldl_cons, hm, if_true]; refine ⟨(ih acc h).1, fun n => ?_⟩; rw [(ih acc h).2]; grind
    · simp only [List.foldl_cons, hm, if_false]
      have hn : (acc ++ [m]).Nodup := by
        rw [List.nodup_append]; refine ⟨h, by simp, ?_⟩; intro a ha b hb; simp at hb; subst hb; rintro rfl; exact hm ha
      exact ⟨(ih _ hn).1, fun n => by rw [(ih _ hn).2]; simp; grind⟩

/-- Over a list `U` of distinct names that holds every name of `l`, `l`'s value is one term per name of `U`. -/
theorem sum_by_names (κ : String → Rat) (U : List String) (hU : U.Nodup) (l : List (String × Rat))
    (hl : ∀ p ∈ l, p.1 ∈ U) :
    (l.map fun p => p.2 * κ p.1).sum = (U.map fun n => ((l.filter (·.1 == n)).map (·.2)).sum * κ n).sum := by
  induction U generalizing l with
  | nil => cases l with
    | nil => rfl
    | cons p _ => exact absurd (hl p (by simp)) (by simp)
  | cons n U ih =>
    obtain ⟨hn, hU⟩ := List.nodup_cons.mp hU
    rw [sum_split κ l n, ih hU _ (fun p hp => by
      have := List.mem_filter.mp hp; rcases List.mem_cons.mp (hl p this.1) with h | h
      · simp [h] at this
      · exact h)]
    simp only [List.map_cons, List.sum_cons]
    congr 1; congr 1; apply List.map_congr_left; intro m hm
    rw [List.filter_filter]; congr 3; apply List.filter_congr; intro q _
    by_cases hq : q.1 = m <;> simp [hq] <;> rintro rfl <;> exact hn hm

theorem sum_nonzero (κ c : String → Rat) (U : List String) :
    (((U.map fun n => (n, c n)).filter (·.2 != 0)).map fun p => p.2 * κ p.1).sum = (U.map fun n => c n * κ n).sum := by
  induction U with
  | nil => rfl
  | cons n U ih => by_cases h : c n = 0 <;> simp [h, ih, Rat.zero_add]

theorem QLin.eval_norm (κ : String → Rat) (L : QLin) : L.norm.eval κ = L.eval κ := by
  have hspec := FM.firstAppearance_spec (L.coeffs.map (·.1)) [] (by simp)
  unfold QLin.eval QLin.norm FM.unknowns FM.firstAppearance
  simp only [List.flatMap_cons, List.flatMap_nil, List.append_nil]
  rw [sum_nonzero κ L.coeffOf,
    sum_by_names κ _ hspec.1 L.coeffs (fun p hp => (hspec.2 p.1).mpr (.inr (List.mem_map_of_mem hp)))]
  rfl

/-! ### The charged lowering decides 5's linearity exactly -/

theorem QLin.eval_coeffOf (L : QLin) (n : String) :
    L.eval (fun m => if m = n then 1 else 0) = L.const + L.coeffOf n := by
  have h : ∀ l : List (String × Rat), (l.map fun p => p.2 * (if p.1 = n then (1 : Rat) else 0)).sum =
      ((l.filter (·.1 == n)).map (·.2)).sum := by
    intro l; induction l with
    | nil => rfl
    | cons p l ih => by_cases hp : p.1 = n <;> simp [hp, ih, Rat.zero_mul, Rat.mul_one, Rat.zero_add]
  simp [QLin.eval, QLin.coeffOf, h]

/-- 5's `isConst` by its meaning: the form's value is its constant at every point. -/
theorem QLin.isConst_iff (L : QLin) : L.isConst = true ↔ ∀ κ, L.eval κ = L.const := by
  refine ⟨fun h κ => QLin.eval_isConst κ L h, fun h => ?_⟩
  have hc : ∀ n, L.coeffOf n = 0 := fun n => by have := h (fun m => if m = n then 1 else 0); rw [QLin.eval_coeffOf] at this; grind
  simp [QLin.isConst, hc]

namespace Work

theorem bne_nonzero {x : Rat} (h : x ≠ 0) : (x != 0) = true := by simp [h]

theorem Shape.Sound.congr {L M : QLin} {s : Shape} (he : ∀ κ, M.eval κ = L.eval κ) (hc : M.const = L.const)
    (h : Shape.Sound L s) : Shape.Sound M s := by
  have hi : M.isConst = L.isConst := by
    rw [Bool.eq_iff_iff, QLin.isConst_iff, QLin.isConst_iff]; simp only [he, hc]
  cases s with
  | const nz => exact ⟨hi.trans h.1, fun b hb => hc ▸ h.2 b hb⟩
  | nonconst => exact hi.trans h
  | unknown => trivial

theorem shapeOf_sound (L : QLin) : Shape.Sound L (shapeOf L) := by
  simp only [shapeOf, QLin.isConstOnce_eq]
  cases h : L.isConst
  · simpa [Shape.Sound] using h
  · simp [Shape.Sound, h]

theorem Lowered.shape_sound {l : Lowered} {L : QLin} (h : Lowered.Sound (some L) l) : Shape.Sound L l.shape := by
  cases l with
  | form M => cases h; exact shapeOf_sound _
  | nonlinear => cases h
  | tooLarge s => obtain ⟨M, hM, hs⟩ := h; cases hM; exact hs

theorem chargeL_sound (L : QLin) : Lowered.Sound (some L) ((chargeL L).result ()) := by
  simp only [chargeL]
  split
  · rfl
  · exact ⟨L, rfl, shapeOf_sound L⟩

theorem decided_sound (e : Expr) (l : Linearity) (h : Linearity.Sound e.linear l) :
    Lowered.Sound e.linear ((decided e l).result ()) := by
  cases l with
  | linear s => exact h
  | nonlinear => exact h
  | unknown =>
    simp only [decided, exactNode]
    cases he : e.linear with
    | none => rfl
    | some L => exact ⟨L, rfl, shapeOf_sound L⟩

theorem const_norm_add (A B : QLin) : (A.add B).norm.const = A.const + B.const := rfl
theorem const_scale (w : Rat) (L : QLin) : (L.scale w).const = w * L.const := rfl

theorem isConst_add {A B : QLin} (ha : A.isConst = true) (hb : B.isConst = true) : (A.add B).norm.isConst = true := by
  rw [QLin.isConst_iff] at ha hb ⊢
  intro κ; rw [QLin.eval_norm, QLin.eval_add, ha, hb, const_norm_add]

theorem nonconst_add {A B : QLin} (ha : A.isConst = true) (hb : B.isConst = false) :
    (A.add B).norm.isConst = false := by
  apply Bool.eq_false_iff.mpr; intro h
  apply Bool.eq_false_iff.mp hb
  rw [QLin.isConst_iff] at ha h ⊢
  intro κ; have := h κ
  rw [QLin.eval_norm, QLin.eval_add, ha, const_norm_add] at this; grind

theorem add_comm_shape {A B : QLin} {s : Shape} (h : Shape.Sound (A.add B).norm s) : Shape.Sound (B.add A).norm s :=
  Shape.Sound.congr (fun κ => by simp only [QLin.eval_norm, QLin.eval_add]; grind)
    (by simp only [const_norm_add]; grind) h

theorem zero_add_shape {A B : QLin} {s : Shape} (ha : Shape.Sound A (.const (some false))) (hb : Shape.Sound B s) :
    Shape.Sound (A.add B).norm s := by
  have h0 : A.const = 0 := by simpa using ha.2 false rfl
  have hc := (QLin.isConst_iff A).mp ha.1
  exact Shape.Sound.congr (fun κ => by rw [QLin.eval_norm, QLin.eval_add, hc, h0, Rat.zero_add])
    (by rw [const_norm_add, h0, Rat.zero_add]) hb

theorem addS_sound {A B : QLin} {sa sb : Shape} (ha : Shape.Sound A sa) (hb : Shape.Sound B sb) :
    Linearity.Sound (some (A.add B).norm) (addS sa sb) := by
  have hz := fun (h : sa = .const (some false)) => zero_add_shape (h ▸ ha) hb
  have hz' := fun (h : sb = .const (some false)) => add_comm_shape (zero_add_shape (h ▸ hb) ha)
  rcases sa with (_ | (_ | _)) | _ | _ <;> rcases sb with (_ | (_ | _)) | _ | _ <;> simp only [addS] <;>
    first
    | exact ⟨_, rfl, hz rfl⟩
    | exact ⟨_, rfl, hz' rfl⟩
    | exact ⟨_, rfl, trivial⟩
    | exact ⟨_, rfl, isConst_add ha.1 hb.1, by simp⟩
    | exact ⟨_, rfl, nonconst_add ha.1 hb⟩
    | exact ⟨_, rfl, add_comm_shape (A := B) (B := A) (nonconst_add hb.1 ha)⟩

theorem scale_shape {w : Rat} {nz : Option Bool} {L : QLin} {s : Shape} (hw : ∀ b, nz = some b → (w != 0) = b)
    (h : Shape.Sound L s) : Shape.Sound (L.scale w) (Shape.scale nz s) := by
  have hzero (hL : L.isConst = true ∨ w = 0) (h0 : w * L.const = 0) : Shape.Sound (L.scale w) (.const (some false)) := by
    refine ⟨(QLin.isConst_iff _).mpr fun κ => ?_, fun b hb => ?_⟩
    · rw [QLin.eval_scale, const_scale]
      rcases hL with hL | rfl
      · rw [(QLin.isConst_iff L).mp hL]
      · simp [Rat.zero_mul]
    · cases hb; simp [const_scale, h0]
  have hconst (hc : L.isConst = true) : (L.scale w).isConst = true := by
    rw [QLin.isConst_iff] at hc ⊢; intro κ; rw [QLin.eval_scale, const_scale, hc]
  rcases nz with _ | _ | _
  · rcases s with (_ | (_ | _)) | _ | _
    · exact ⟨hconst h.1, fun b hb => by cases hb⟩
    · have h0 : L.const = 0 := by simpa using h.2 false rfl
      exact hzero (.inl h.1) (by rw [h0, Rat.mul_zero])
    · exact ⟨hconst h.1, fun b hb => by cases hb⟩
    · trivial
    · trivial
  · have hw0 : w = 0 := by simpa using hw false rfl
    exact hzero (.inr hw0) (by rw [hw0, Rat.zero_mul])
  · have hw0 : w ≠ 0 := by simpa using hw true rfl
    have hc : (L.scale w).const = w * L.const := rfl
    have hi : (L.scale w).isConst = L.isConst := by
      rw [Bool.eq_iff_iff, QLin.isConst_iff, QLin.isConst_iff]
      refine ⟨fun h κ => ?_, fun h κ => by rw [QLin.eval_scale, h, hc]⟩
      have h2 := congrArg (fun x => w⁻¹ * x) (h κ)
      simpa only [QLin.eval_scale, hc, ← Rat.mul_assoc, Rat.inv_mul_cancel _ hw0, Rat.one_mul] using h2
    cases s with
    | const nz' =>
      refine ⟨hi.trans h.1, fun b hb => ?_⟩
      have := h.2 b hb
      subst this
      by_cases h0 : L.const = 0
      · simp [hc, h0, Rat.mul_zero]
      · have h1 : w * L.const ≠ 0 := fun h => (Rat.mul_eq_zero.mp h).elim hw0 h0
        rw [hc, bne_nonzero h1, bne_nonzero h0]
    | nonconst => exact hi.trans h
    | unknown => trivial

theorem neg_shape {L : QLin} {s : Shape} (h : Shape.Sound L s) : Shape.Sound (L.scale (-1)) s := by
  simpa [Shape.scale] using scale_shape (w := -1) (nz := some true) (fun b hb => by cases hb; decide) h

/-- The rule 5 applies to a product and a quotient, as a function of the two forms. -/
def mulOp (A B : QLin) : Option QLin :=
  if A.isConst then some (B.scale A.const) else if B.isConst then some (A.scale B.const) else none

def divOp (A B : QLin) : Option QLin := if B.isConst && B.const != 0 then some (A.scale (1 / B.const)) else none

theorem mulS_sound {A B : QLin} {sa sb : Shape} (ha : Shape.Sound A sa) (hb : Shape.Sound B sb) :
    Linearity.Sound (mulOp A B) (mulS sa sb) := by
  rcases sa with nz | _ | _
  · simp only [mulS, mulOp, ha.1, if_true]
    exact ⟨_, rfl, scale_shape ha.2 hb⟩
  · have ha' : A.isConst = false := ha
    rcases sb with nz | _ | _
    · simp only [mulS, mulOp, ha', hb.1, if_true, Bool.false_eq_true, if_false]
      exact ⟨_, rfl, scale_shape hb.2 ha⟩
    · have hb' : B.isConst = false := hb
      simp only [mulS, mulOp, ha', hb', Bool.false_eq_true, if_false]; rfl
    · trivial
  · rcases sb with nz | _ | _
    · simp only [mulS, mulOp]
      cases hA : A.isConst
      · simp only [hb.1, if_true, Bool.false_eq_true, if_false]; exact ⟨_, rfl, scale_shape hb.2 ha⟩
      · refine ⟨_, by simp; rfl, ?_⟩
        rcases nz with _ | _ | _
        · trivial
        · have h0 : B.const = 0 := by simpa using hb.2 false rfl
          refine ⟨(QLin.isConst_iff _).mpr fun κ => ?_, fun b hb' => ?_⟩
          · rw [QLin.eval_scale, (QLin.isConst_iff B).mp hb.1, h0, Rat.mul_zero, const_scale, h0, Rat.mul_zero]
          · cases hb'; simp [const_scale, h0, Rat.mul_zero]
        · trivial
    · trivial
    · trivial

theorem divS_sound {A B : QLin} {sa sb : Shape} (ha : Shape.Sound A sa) (hb : Shape.Sound B sb) :
    Linearity.Sound (divOp A B) (divS sa sb) := by
  rcases sb with (_ | (_ | _)) | _ | _
  · trivial
  · have h0 : B.const = 0 := by simpa using hb.2 false rfl
    simp [divS, divOp, h0, Linearity.Sound]
  · have h0 : B.const ≠ 0 := by simpa using hb.2 true rfl
    simp only [divS, divOp, hb.1, h0, Bool.true_and, bne_iff_ne, ne_eq, not_false_eq_true, if_true]
    refine ⟨_, rfl, ?_⟩
    have := scale_shape (w := 1 / B.const) (nz := some true) (fun b hb' => by
      cases hb'
      have h1 : B.const⁻¹ ≠ 0 := fun h => by
        have := Rat.mul_inv_cancel _ h0
        rw [h, Rat.mul_zero] at this; exact absurd this (by decide)
      simp [Rat.div_def, h1]) ha
    simpa [Shape.scale] using this
  · have hb' : B.isConst = false := hb
    simp [divS, divOp, hb', Linearity.Sound]
  · trivial

/-- The operands' results combine by the rule `op`, `f` being its one-pass form and `g` its reading of shapes. -/
theorem binL_sound {e : Expr} {f : QLin → QLin → Option QLin} {g : Shape → Shape → Linearity}
    {op : QLin → QLin → Option QLin} {oa ob : Option QLin} {la lb : Lowered} (hf : ∀ L M, f L M = op L M)
    (hg : ∀ A B sa sb, Shape.Sound A sa → Shape.Sound B sb → Linearity.Sound (op A B) (g sa sb))
    (he : e.linear = oa.bind fun A => ob.bind (op A)) (ha : Lowered.Sound oa la) (hb : Lowered.Sound ob lb) :
    Lowered.Sound e.linear ((binL e f g la lb).result ()) := by
  have hl : ∀ A B, oa = some A → ob = some B → Lowered.Sound (op A B) ((decided e (g la.shape lb.shape)).result ()) := by
    intro A B h1 h2
    subst h1 h2
    have := decided_sound e (g la.shape lb.shape) (by
      simpa [he] using hg A B _ _ (Lowered.shape_sound ha) (Lowered.shape_sound hb))
    simpa [he] using this
  cases la with
  | nonlinear => cases ha; rw [he]; cases lb <;> rfl
  | form L =>
    cases ha
    cases lb with
    | nonlinear => cases hb; rw [he]; rfl
    | form M =>
      cases hb
      simp only [binL, he, Option.bind_some, ← hf]
      cases h : f L M with
      | some N => exact chargeL_sound N
      | none => rfl
    | tooLarge s =>
      obtain ⟨B, rfl, _⟩ := hb
      simpa [binL, he] using hl L B rfl rfl
  | tooLarge s =>
    obtain ⟨A, rfl, _⟩ := ha
    cases lb with
    | nonlinear => cases hb; rw [he]; rfl
    | form M => cases hb; simpa [binL, he] using hl A M rfl rfl
    | tooLarge t =>
      obtain ⟨B, rfl, _⟩ := hb
      simpa [binL, he] using hl A B rfl rfl

theorem pow_nonzero {x : Rat} {k : Nat} (h : powTooLarge x k = true) : x ^ k ≠ 0 := by
  intro h0
  have := powTooLarge_sound x k h
  rw [h0] at this
  have hs : Small 0 := ⟨by decide, by decide⟩
  simp [Val.guard, hs] at this

theorem pow_ne {x : Rat} (hx : x ≠ 0) (k : Nat) : x ^ k ≠ 0 := by
  induction k with
  | zero => simp
  | succ k ih => rw [Rat.pow_succ]; exact fun h => (Rat.mul_eq_zero.mp h).elim ih hx

theorem step_sound_bin {e a b : Expr} (he : e = .add a b ∨ e = .sub a b ∨ e = .mul a b ∨ e = .div a b) {la lb : Lowered}
    (ha : Lowered.Sound a.linear la) (hb : Lowered.Sound b.linear lb) :
    Lowered.Sound e.linear ((stepNode e [la, lb]).result ()) := by
  rcases he with rfl | rfl | rfl | rfl
  · exact binL_sound (op := fun A B => some (A.add B).norm) (fun L M => by rw [QLin.normOnce_eq])
      (fun _ _ _ _ h1 h2 => addS_sound h1 h2) (by simp [Expr.linear]) ha hb
  · exact binL_sound (op := fun A B => some (A.add (B.scale (-1))).norm) (fun L M => by rw [QLin.normOnce_eq])
      (fun _ _ _ _ h1 h2 => addS_sound h1 (neg_shape h2)) (by simp [Expr.linear]) ha hb
  · exact binL_sound (op := mulOp) (fun L M => by simp only [mulOp, QLin.isConstOnce_eq])
      (fun _ _ _ _ h1 h2 => mulS_sound h1 h2) (by
        simp only [Expr.linear, mulOp]; cases a.linear <;> cases b.linear <;> rfl) ha hb
  · exact binL_sound (op := divOp) (fun L M => by simp only [divOp, QLin.isConstOnce_eq])
      (fun _ _ _ _ h1 h2 => divS_sound h1 h2) (by
        simp only [Expr.linear, divOp]; cases a.linear <;> cases b.linear <;> rfl) ha hb

theorem step_sound_pow {a : Expr} {k : Nat} {la : Lowered} (ha : Lowered.Sound a.linear la) :
    Lowered.Sound (Expr.pow a k).linear ((stepNode (.pow a k) [la]).result ()) := by
  have hlin : ∀ A, a.linear = some A → (Expr.pow a k).linear =
      if A.isConst then some ⟨A.const ^ k, []⟩ else match k with
        | 0 => some ⟨1, []⟩
        | 1 => some A
        | _ => none := fun A h => by
    rcases k with _ | _ | k <;> simp [Expr.linear, h] <;> rfl
  cases la with
  | nonlinear => simp [stepNode, Node.free, Lowered.Sound, Expr.linear, show a.linear = none from ha]
  | form L =>
    have h : a.linear = some L := ha
    simp only [stepNode, hlin L h, QLin.isConstOnce_eq]
    cases hc : L.isConst
    · simp only [Bool.false_eq_true, if_false]
      rcases k with _ | _ | k
      · exact chargeL_sound _
      · rfl
      · rfl
    · simp only [if_true]
      cases hp : powTooLarge L.const k
      · exact chargeL_sound _
      · exact ⟨_, rfl, (QLin.isConst_iff _).mpr fun κ => by simp [QLin.eval, Rat.add_zero], fun b hb => by
          cases hb; simpa using pow_nonzero hp⟩
  | tooLarge s =>
    obtain ⟨L, h, hs⟩ := ha
    refine decided_sound _ _ ?_
    rw [hlin L h]
    have hp0 : powS s 0 = .linear (.const (some true)) := by cases s <;> rfl
    have hp1 : powS s 1 = .linear s := by cases s <;> rfl
    rcases k with _ | _ | k
    · rw [hp0]
      cases L.isConst <;> exact ⟨_, rfl, (QLin.isConst_iff _).mpr fun κ => by simp [QLin.eval, Rat.add_zero], by simp⟩
    · rw [show (0 + 1 : Nat) = 1 from rfl, hp1]
      cases hc : L.isConst
      · exact ⟨_, rfl, hs⟩
      · refine ⟨⟨L.const ^ 1, []⟩, by simp [hc], Shape.Sound.congr (L := L) (fun κ => ?_) (Rat.pow_one _) hs⟩
        rw [(QLin.isConst_iff L).mp hc]; simp [QLin.eval, Rat.add_zero]
    · rcases s with nz | _ | _
      · have hc : L.isConst = true := hs.1
        refine ⟨_, by simp [hc]; rfl, (QLin.isConst_iff _).mpr fun κ => by simp [QLin.eval, Rat.add_zero], fun b hb => ?_⟩
        have := hs.2 b hb
        subst this
        by_cases h0 : L.const = 0
        · simp [h0, Rat.pow_succ, Rat.mul_zero]
        · rw [bne_nonzero (pow_ne h0 (k + 1 + 1)), bne_nonzero h0]
      · have hc : L.isConst = false := hs
        simp [hc, Linearity.Sound, powS]
      · trivial

theorem Node.run_some {limit : Nat} {n : Node} {w : Nat} {r : Lowered × Nat} (h : n.run limit w = some r) :
    n.result () = r.1 := by
  unfold Node.run at h; split at h
  · cases h
  · cases h; rfl

theorem bin_sound {limit : Nat} {e a b : Expr} (he : e = .add a b ∨ e = .sub a b ∨ e = .mul a b ∨ e = .div a b)
    (iha : ∀ w l w', Expr.linearC limit a w = some (l, w') → Lowered.Sound a.linear l)
    (ihb : ∀ w l w', Expr.linearC limit b w = some (l, w') → Lowered.Sound b.linear l) {w w' : Nat} {l : Lowered}
    (h : (match Expr.linearC limit a w with
      | none => none
      | some (.nonlinear, w) => some (.nonlinear, w)
      | some (la, w) => (Expr.linearC limit b w).bind fun (lb, w) => (stepNode e [la, lb]).run limit w) = some (l, w')) :
    Lowered.Sound e.linear l := by
  split at h
  · cases h
  · cases h
    have ha : a.linear = none := iha _ .nonlinear _ ‹_›
    rcases he with rfl | rfl | rfl | rfl <;> simp [Expr.linear, ha, Lowered.Sound]
  · obtain ⟨⟨lb, w2⟩, h1, h2⟩ := Option.bind_eq_some_iff.mp h
    rw [show l = _ from (Node.run_some (r := (l, w')) h2).symm]
    exact step_sound_bin he (iha _ _ _ ‹_›) (ihb _ _ _ h1)

theorem linearC_sound (limit : Nat) (e : Expr) (w : Nat) (l : Lowered) (w' : Nat)
    (h : Expr.linearC limit e w = some (l, w')) : Lowered.Sound e.linear l := by
  induction e generalizing w l w' with
  | lit q =>
    rw [show l = _ from (Node.run_some (r := (l, w')) (visitC_some h).2).symm]
    exact chargeL_sound _
  | val n =>
    rw [show l = _ from (Node.run_some (r := (l, w')) (visitC_some h).2).symm]
    exact chargeL_sound _
  | add a b iha ihb => exact bin_sound (.inl rfl) iha ihb (visitC_some h).2
  | sub a b iha ihb => exact bin_sound (.inr (.inl rfl)) iha ihb (visitC_some h).2
  | mul a b iha ihb => exact bin_sound (.inr (.inr (.inl rfl))) iha ihb (visitC_some h).2
  | div a b iha ihb => exact bin_sound (.inr (.inr (.inr rfl))) iha ihb (visitC_some h).2
  | pow a k iha =>
    obtain ⟨_, h⟩ := visitC_some h
    obtain ⟨⟨la, w1⟩, h1, h2⟩ := Option.bind_eq_some_iff.mp h
    rw [show l = _ from (Node.run_some (r := (l, w')) h2).symm]
    exact step_sound_pow (iha _ _ _ h1)

theorem Expr.linearC_form (limit : Nat) (e : Expr) (w : Nat) (L : QLin) (w' : Nat)
    (h : Expr.linearC limit e w = some (.form L, w')) : e.linear = some L := linearC_sound limit e w _ w' h

theorem Expr.linearC_nonlinear (limit : Nat) (e : Expr) (w w' : Nat)
    (h : Expr.linearC limit e w = some (.nonlinear, w')) : e.linear = none := linearC_sound limit e w _ w' h

theorem Expr.linearC_tooLarge (limit : Nat) (e : Expr) (w : Nat) (s : Shape) (w' : Nat)
    (h : Expr.linearC limit e w = some (.tooLarge s, w')) : ∃ L, e.linear = some L ∧ Shape.Sound L s :=
  linearC_sound limit e w _ w' h

end Work

theorem Expr.linear_sound (κ : String → Rat) (e : Expr) (L : QLin) (h : e.linear = some L) :
    Denotes (fun n => some (κ n)) e (L.eval κ) := by
  induction e generalizing L with
  | lit q => cases h; rw [show QLin.eval κ ⟨q, []⟩ = q by simp [QLin.eval, Rat.add_zero]]; exact .lit
  | val n => cases h; rw [show QLin.eval κ ⟨0, [(n, 1)]⟩ = κ n by simp [QLin.eval, Rat.add_zero, Rat.zero_add]]; exact .val rfl
  | add a b iha ihb =>
      cases ha : a.linear <;> cases hb : b.linear <;> simp [Expr.linear, ha, hb] at h
      subst h; rw [QLin.eval_norm, QLin.eval_add]; exact .add (iha _ ha) (ihb _ hb)
  | sub a b iha ihb =>
      cases ha : a.linear <;> cases hb : b.linear <;> simp [Expr.linear, ha, hb] at h
      subst h; rw [QLin.eval_norm, QLin.eval_add, QLin.eval_scale]
      have := Denotes.sub (iha _ ha) (ihb _ hb); grind
  | mul a b iha ihb =>
      cases ha : a.linear <;> cases hb : b.linear <;> simp [Expr.linear, ha, hb] at h
      rename_i A B
      have hd := Denotes.mul (iha _ ha) (ihb _ hb)
      by_cases hA : A.isConst
      · simp [hA] at h; subst h
        rw [QLin.eval_isConst κ _ hA] at hd; rwa [QLin.eval_scale]
      · by_cases hB : B.isConst <;> simp [hA, hB] at h; subst h
        rw [QLin.eval_isConst κ _ hB] at hd; rw [QLin.eval_scale, Rat.mul_comm]; exact hd
  | div a b iha ihb =>
      cases ha : a.linear <;> cases hb : b.linear <;> simp [Expr.linear, ha, hb] at h
      rename_i A B
      obtain ⟨⟨hB, hB0⟩, rfl⟩ := h
      have hne : B.eval κ ≠ 0 := by rw [QLin.eval_isConst κ _ hB]; exact hB0
      have hd := Denotes.div (iha _ ha) (ihb _ hb) hne
      rw [QLin.eval_isConst κ _ hB] at hd; rw [QLin.eval_scale, Rat.mul_comm, Rat.div_def, Rat.one_mul, ← Rat.div_def]; exact hd
  | pow a k iha =>
      cases ha : a.linear <;> simp [Expr.linear, ha] at h
      rename_i A
      have hd := Denotes.pow (k := k) (iha _ ha)
      by_cases hA : A.isConst
      · simp [hA] at h; subst h
        rw [QLin.eval_isConst κ _ hA] at hd; rw [show QLin.eval κ ⟨A.const ^ k, []⟩ = A.const ^ k by simp [QLin.eval, Rat.add_zero]]
        exact hd
      · simp [hA] at h
        rcases k with _ | _ | k <;> simp at h <;> subst h
        · rw [show QLin.eval κ ⟨1, []⟩ = 1 by simp [QLin.eval, Rat.add_zero]]; simpa using hd
        · simpa using hd

/-- Over values every free name has, a claim holds exactly when its lowered facts do. -/
theorem Claim.lower_sound (κ : String → Rat) (c : Claim) (fs : List QFact) (h : c.lower = some fs) :
    (∀ f ∈ fs, f.Holds κ) ↔ c.Holds (fun n => some (κ n)) := by
  have hl := fun e L (he : Expr.linear e = some L) => Expr.linear_sound κ e L he
  have hu := fun e L x (he : Expr.linear e = some L) (hx : Denotes (fun n => some (κ n)) e x) =>
    Denotes.unique hx (hl e L he)
  cases c with
  | compare c a b =>
      obtain ⟨rel, swap⟩ := c
      cases ha : a.linear <;> cases hb : b.linear <;> cases swap <;> cases rel <;>
        simp [Claim.lower, ha, hb] at h <;> subst h <;>
        simp only [Claim.Holds, VE.Numbers.Comparison.Holds, VE.Numbers.Rel.Holds, QFact.sub, QFact.Holds, List.mem_cons,
          List.mem_nil_iff, forall_eq_or_imp, QLin.eval_add, QLin.eval_scale] <;>
        refine ⟨fun hf => ⟨_, _, hl a _ ha, hl b _ hb, by grind⟩, fun ⟨x, y, hx, hy, hxy⟩ => ?_⟩ <;>
        rw [hu a _ x ha hx, hu b _ y hb hy] at hxy <;> grind
  | within e lo hi =>
      cases he : e.linear <;> cases hlo : lo.linear <;> cases hhi : hi.linear <;>
        simp [Claim.lower, he, hlo, hhi] at h
      subst h
      simp only [Claim.Holds, QFact.sub, QFact.Holds, List.mem_cons, List.mem_nil_iff, forall_eq_or_imp,
        QLin.eval_add, QLin.eval_scale]
      refine ⟨fun hf => ⟨_, _, _, hl e _ he, hl lo _ hlo, hl hi _ hhi, by grind⟩, fun ⟨x, l, u, hx, hl', hu', hxl⟩ => ?_⟩
      rw [hu e _ x he hx, hu lo _ l hlo hl', hu hi _ u hhi hu'] at hxl; grind
  | rounds => simp [Claim.lower] at h

theorem Claim.facts_sound (ds : List Decl) (h : WellFormed ds) (c : Claim) (fs : List QFact)
    (hf : c.facts ds = some fs) (κ : String → Rat) :
    (∀ f ∈ fs, f.Holds κ) ↔ c.Holds (values (assign ds (freeNames ds) κ)) := by
  unfold Claim.facts at hf
  split at hf
  · rename_i c' hc
    rw [Claim.inline_sound ds h _ (freeNames_mem ds) c c' hc κ]; exact Claim.lower_sound κ c' fs hf
  · cases hf

/-- The meaning of a derivation: wherever the free values satisfy every square link and every premise, the conclusion
holds. Stated, defined and counted values keep their meaning; a defined value is evaluated from the free values. -/
def Follows (ds : List Decl) (P : List Claim) (links : List (String × String)) (C : Claim) : Prop :=
  ∀ κ : String → Rat, (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) →
    (∀ p ∈ P, p.Holds (values (assign ds (freeNames ds) κ))) → C.Holds (values (assign ds (freeNames ds) κ))

/-- What a "does not follow" row states: values of the free values meeting every link and premise, where the
conclusion does not hold. -/
def HasCounterexample (ds : List Decl) (P : List Claim) (links : List (String × String)) (C : Claim) : Prop :=
  ∃ κ : String → Rat, (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) ∧
    (∀ p ∈ P, p.Holds (values (assign ds (freeNames ds) κ))) ∧ ¬ C.Holds (values (assign ds (freeNames ds) κ))

theorem not_follows_of_counterexample (ds : List Decl) (P : List Claim) (links : List (String × String)) (C : Claim)
    (h : HasCounterexample ds P links C) : ¬ Follows ds P links C := by
  obtain ⟨κ, hl, hP, hC⟩ := h
  exact fun hf => hC (hf κ hl hP)

/-- Each premise's facts are in the flattened list, and each fact of the list is some premise's. -/
theorem mapM_facts {ds : List Decl} {P : List Claim} {fss : List (List QFact)}
    (hP : P.mapM (Claim.facts ds) = some fss) :
    (∀ p ∈ P, ∃ fs, p.facts ds = some fs ∧ ∀ f ∈ fs, f ∈ fss.flatten) ∧
      (∀ f ∈ fss.flatten, ∃ p ∈ P, ∃ fs, p.facts ds = some fs ∧ f ∈ fs) := by
  induction P generalizing fss with
  | nil => simp_all
  | cons p P ih =>
      simp only [List.mapM_cons, Option.bind_eq_bind, Option.bind_eq_some_iff, Option.pure_def,
        Option.some.injEq] at hP
      obtain ⟨fs, hp, fss', hfss', rfl⟩ := hP
      obtain ⟨ih1, ih2⟩ := ih hfss'
      refine ⟨fun q hq => ?_, fun f hf => ?_⟩
      · rcases List.mem_cons.mp hq with rfl | hq
        · exact ⟨fs, hp, fun f hf => by simp [hf]⟩
        · obtain ⟨gs, hg, hgs⟩ := ih1 q hq; exact ⟨gs, hg, fun f hf => by simp [hgs f hf]⟩
      · simp only [List.flatten_cons, List.mem_append] at hf
        rcases hf with hf | hf
        · exact ⟨p, by simp, fs, hp, hf⟩
        · obtain ⟨q, hq, gs, hg, hgs⟩ := ih2 f hf; exact ⟨q, by simp [hq], gs, hg, hgs⟩

/-- The premises hold exactly when their lowered facts do. -/
theorem premises_iff (ds : List Decl) (h : WellFormed ds) (P : List Claim) (fss : List (List QFact))
    (hP : P.mapM (Claim.facts ds) = some fss) (κ : String → Rat) :
    (∀ f ∈ fss.flatten, f.Holds κ) ↔ ∀ p ∈ P, p.Holds (values (assign ds (freeNames ds) κ)) := by
  obtain ⟨h1, h2⟩ := mapM_facts hP
  constructor
  · intro hf p hp
    obtain ⟨fs, hfs, hmem⟩ := h1 p hp
    exact (Claim.facts_sound ds h p fs hfs κ).mp fun f hf' => hf f (hmem f hf')
  · intro hp f hf
    obtain ⟨p, hpP, fs, hfs, hmem⟩ := h2 f hf
    exact (Claim.facts_sound ds h p fs hfs κ).mpr (hp p hpP) f hmem

/-- A replayed certificate over the lowered facts proves the derivation's meaning. -/
theorem follows_of_check (ds : List Decl) (h : WellFormed ds) (P : List Claim) (links : List (String × String))
    (C : Claim) (fss : List (List QFact)) (g : QFact) (d : Derivation) (hP : P.mapM (Claim.facts ds) = some fss)
    (hC : C.facts ds = some [g]) (hd : d.check fss.flatten links g = true) : Follows ds P links C := by
  intro κ hl hp
  have hg := Derivation.check_sound _ links g d hd κ ((premises_iff ds h P fss hP κ).mpr hp) hl
  exact (Claim.facts_sound ds h C [g] hC κ).mp (by simpa using hg)

/-- A counterexample checked over the lowered facts is a counterexample of the derivation. -/
theorem counterexample_of_check (ds : List Decl) (h : WellFormed ds) (P : List Claim)
    (links : List (String × String)) (C : Claim) (fss : List (List QFact)) (g : QFact) (κ : String → Rat)
    (hP : P.mapM (Claim.facts ds) = some fss) (hC : C.facts ds = some [g])
    (hκ : counterexampleCheck fss.flatten links g κ = true) : HasCounterexample ds P links C := by
  obtain ⟨hf, hl, hg⟩ := Counterexample.check_sound _ links g κ hκ
  refine ⟨κ, hl, (premises_iff ds h P fss hP κ).mp hf, fun hc => hg ?_⟩
  simpa using (Claim.facts_sound ds h C [g] hC κ).mpr hc

end VE.Calc
