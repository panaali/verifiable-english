import VE.Calc.Decls

/-! Algebraic identities (spec 8.2, plan 3.8), over expressions whose names are all free: both sides are brought to
fractions of normal polynomials over ℚ and compared cross-multiplied. Equal normal forms mean equal values wherever both
sides denote; a point where both sides denote and differ refutes the identity. Inlining the named values (spec 2.7),
the meaning `IsIdentity` and the runner are me-9b's. -/

namespace VE.Calc
open VE.Numbers

/-- A monomial: a coefficient and variables with positive exponents, sorted by name. -/
structure Mono where
  coeff : Rat
  vars : List (String × Nat)
  deriving Repr, DecidableEq

/-- A normal polynomial: monomials sorted by their variable lists, no repeated list, no zero coefficient. -/
abbrev Poly := List Mono

def Poly.eval (κ : String → Rat) (p : Poly) : Rat :=
  (p.map fun m => m.coeff * (m.vars.map fun v => κ v.1 ^ v.2).foldl (· * ·) 1).sum

/-- The limits of a normal form: 10,000 terms (spec 3.2, `limit .polyTerms`), counted before like terms merge and over
the nodes of an inlined side; coefficients within the digit limit (2.4); exponents at most 4,096. -/
def maxPolyTerms : Nat := 10000
def maxPolyExponent : Nat := 4096

def mulVars : List (String × Nat) → List (String × Nat) → List (String × Nat)
  | [], v => v
  | u, [] => u
  | (x, i) :: u, (y, j) :: v =>
    if x = y then (x, i + j) :: mulVars u v
    else if x < y then (x, i) :: mulVars u ((y, j) :: v)
    else (y, j) :: mulVars ((x, i) :: u) v
termination_by u v => u.length + v.length

def Mono.mul (m n : Mono) : Mono := ⟨m.coeff * n.coeff, mulVars m.vars n.vars⟩

/-- The order of monomials: their variable lists, lexicographically. -/
def varsLe : List (String × Nat) → List (String × Nat) → Bool
  | [], _ => true
  | _ :: _, [] => false
  | (x, i) :: u, (y, j) :: v => x < y || (x == y && (i < j || (i == j && varsLe u v)))

def Poly.cons0 (m : Mono) (p : Poly) : Poly := if m.coeff = 0 then p else m :: p

/-- Merges each monomial into the last one kept when their variables agree, dropping zero coefficients; the kept
monomials are in reverse order. Tail-recursive: a sum may have 10,000 terms. -/
def Poly.combine : Poly → Poly → Poly
  | acc, [] => acc
  | n :: acc, m :: p =>
    if m.vars = n.vars then Poly.combine (Poly.cons0 ⟨n.coeff + m.coeff, m.vars⟩ acc) p
    else Poly.combine (Poly.cons0 m (n :: acc)) p
  | [], m :: p => Poly.combine (Poly.cons0 m []) p

def Poly.norm (p : Poly) : Poly := (Poly.combine [] (p.mergeSort fun m n => varsLe m.vars n.vars)).reverse
def Poly.one : Poly := [⟨1, []⟩]
def Poly.neg (p : Poly) : Poly := p.map fun m => ⟨-m.coeff, m.vars⟩

/-- Numerators and denominators below `10 ^ maxDigits` have at most `maxDigits` digits (2.4): one comparison with a
constant instead of `Small`'s digit list, since every intermediate coefficient is checked. The term count is checked
by `add?` and `mul?` before the work, and `norm` never adds a term. -/
def Poly.coeffBound : Nat := 10 ^ maxDigits
def Poly.fits (p : Poly) : Bool :=
  p.all fun m =>
    m.coeff.num.natAbs < Poly.coeffBound && m.coeff.den < Poly.coeffBound && m.vars.all (·.2 ≤ maxPolyExponent)
def Poly.guard (p : Poly) : Option Poly := if p.fits then some p else none
def Poly.add? (p q : Poly) : Option Poly :=
  if p.length + q.length ≤ maxPolyTerms then Poly.guard (Poly.norm (p ++ q)) else none
def Poly.mul? (p q : Poly) : Option Poly :=
  if p.length * q.length ≤ maxPolyTerms then Poly.guard (Poly.norm (p.flatMap fun m => q.map m.mul)) else none
def Poly.pow? (p : Poly) (k : Nat) : Option Poly :=
  if k ≤ maxPolyExponent then go k Poly.one else none
where go : Nat → Poly → Option Poly
  | 0, r => some r
  | k + 1, r => (Poly.mul? r p).bind (go k)

/-- A fraction: a numerator and a denominator. -/
abbrev Frac := Poly × Poly

def Frac.add? (f g : Frac) : Option Frac :=
  if f.2 = g.2 then (Poly.add? f.1 g.1).map (·, f.2) else
    (Poly.mul? f.1 g.2).bind fun l => (Poly.mul? g.1 f.2).bind fun r =>
      (Poly.add? l r).bind fun n => (Poly.mul? f.2 g.2).map (n, ·)
def Frac.mul? (f g : Frac) : Option Frac := (Poly.mul? f.1 g.1).bind fun n => (Poly.mul? f.2 g.2).map (n, ·)
def Frac.div? (f g : Frac) : Option Frac := (Poly.mul? f.1 g.2).bind fun n => (Poly.mul? f.2 g.1).map (n, ·)
def Frac.pow? (f : Frac) (k : Nat) : Option Frac := (Poly.pow? f.1 k).bind fun n => (Poly.pow? f.2 k).map (n, ·)

/-- Every polynomial built passes `Poly.guard`, a literal too (recheck F9); `1 · n¹` always fits. -/
def Frac.go : Expr → Option Frac
  | .lit q => (Poly.guard (Poly.cons0 ⟨q, []⟩ [])).map (·, Poly.one)
  | .val n => some ([⟨1, [(n, 1)]⟩], Poly.one)
  | .add a b => (Frac.go a).bind fun f => (Frac.go b).bind (Frac.add? f)
  | .sub a b => (Frac.go a).bind fun f => (Frac.go b).bind fun g => Frac.add? f (Poly.neg g.1, g.2)
  | .mul a b => (Frac.go a).bind fun f => (Frac.go b).bind (Frac.mul? f)
  | .div a b => (Frac.go a).bind fun f => (Frac.go b).bind (Frac.div? f)
  | .pow a k => (Frac.go a).bind (Frac.pow? · k)

/-- The fuel left after the first `n` nodes, or `none` past them: an inlined side shares its definitions, so its tree
may be far larger than its memory, and the walk stops at the limit. -/
def Expr.nodesWithin : Nat → Expr → Option Nat
  | 0, _ => none
  | n + 1, .lit _ | n + 1, .val _ => some n
  | n + 1, .add a b | n + 1, .sub a b | n + 1, .mul a b | n + 1, .div a b =>
      (a.nodesWithin n).bind (b.nodesWithin ·)
  | n + 1, .pow a _ => a.nodesWithin n

/-- Numerator and denominator of an expression with division; `none` beyond the limits. -/
def Frac.ofExpr? (e : Expr) : Option (Poly × Poly) :=
  if (e.nodesWithin maxPolyTerms).isSome then Frac.go e else none

def Expr.hasDiv : Expr → Bool
  | .lit _ | .val _ => false
  | .add a b | .sub a b | .mul a b => a.hasDiv || b.hasDiv
  | .div _ _ => true
  | .pow a _ => a.hasDiv

/-- The normal form of a division-free expression (its fraction form's denominator is then 1); `none` with division or
beyond the limits. Division is looked for only within the limits, so a side that shares itself costs no more than the
node limit (`hasDiv` walks the whole tree). -/
def Poly.ofExpr? (e : Expr) : Option Poly :=
  (Frac.ofExpr? e).bind fun f => if e.hasDiv then none else if f.2 = Poly.one then some f.1 else none

/-- Both sides cross-multiplied and compared; `none` beyond the limits. -/
def Identity.compare (a b : Expr) : Option Bool :=
  (Frac.ofExpr? a).bind fun fa => (Frac.ofExpr? b).bind fun fb =>
    (Poly.mul? fa.1 fb.2).bind fun l => (Poly.mul? fb.1 fa.2).map (l == ·)

def identityCheck (a b : Expr) : Bool := (Identity.compare a b).getD false

def differsAt (a b : Expr) (κ : List (String × Rat)) : Bool :=
  let σ : Values := fun n => κ.lookup n
  match a.eval σ, b.eval σ with
  | some x, some y => x != y
  | _, _ => false

/-! ### Soundness -/

theorem foldl_mul_one (l : List Rat) (a : Rat) : l.foldl (· * ·) a = a * l.foldl (· * ·) 1 := by
  induction l generalizing a with
  | nil => grind
  | cons x l ih => simp only [List.foldl_cons]; rw [ih (a * x), ih (1 * x)]; grind

def vprod (κ : String → Rat) (vs : List (String × Nat)) : Rat := (vs.map fun v => κ v.1 ^ v.2).foldl (· * ·) 1

theorem vprod_cons (κ : String → Rat) (x : String) (i : Nat) (u : List (String × Nat)) :
    vprod κ ((x, i) :: u) = κ x ^ i * vprod κ u := by
  simp only [vprod, List.map_cons, List.foldl_cons]; rw [foldl_mul_one]; grind

theorem vprod_mulVars (κ : String → Rat) (u v : List (String × Nat)) :
    vprod κ (mulVars u v) = vprod κ u * vprod κ v := by
  have h0 : vprod κ [] = 1 := rfl
  fun_induction mulVars u v <;> simp only [vprod_cons, h0] at * <;> grind

theorem Poly.eval_nil (κ : String → Rat) : Poly.eval κ [] = 0 := rfl
theorem Poly.eval_cons (κ : String → Rat) (m : Mono) (p : Poly) :
    Poly.eval κ (m :: p) = m.coeff * vprod κ m.vars + Poly.eval κ p := by simp [Poly.eval, vprod]
theorem Poly.eval_one (κ : String → Rat) : Poly.eval κ Poly.one = 1 := by
  simp only [Poly.one, Poly.eval_cons, Poly.eval_nil]; simp [vprod]; grind

theorem Poly.eval_append (κ : String → Rat) (p q : Poly) :
    Poly.eval κ (p ++ q) = Poly.eval κ p + Poly.eval κ q := by
  induction p with
  | nil => simp only [List.nil_append, Poly.eval_nil]; grind
  | cons m p ih => simp only [List.cons_append, Poly.eval_cons, ih]; grind

theorem Poly.eval_cons0 (κ : String → Rat) (m : Mono) (p : Poly) :
    Poly.eval κ (Poly.cons0 m p) = Poly.eval κ (m :: p) := by
  unfold Poly.cons0; split <;> simp_all [Poly.eval_cons] <;> grind

theorem Poly.eval_combine (κ : String → Rat) (acc p : Poly) :
    Poly.eval κ (Poly.combine acc p) = Poly.eval κ acc + Poly.eval κ p := by
  fun_induction Poly.combine acc p <;> simp_all [Poly.eval_cons0, Poly.eval_cons, Poly.eval_nil] <;> grind

theorem Poly.eval_perm (κ : String → Rat) {p q : Poly} (h : p.Perm q) : Poly.eval κ p = Poly.eval κ q := by
  induction h with
  | nil => rfl
  | cons _ _ ih => simp [Poly.eval_cons, ih]
  | swap => simp only [Poly.eval_cons]; grind
  | trans _ _ ih1 ih2 => rw [ih1, ih2]

theorem Poly.eval_norm (κ : String → Rat) (p : Poly) : Poly.eval κ (Poly.norm p) = Poly.eval κ p := by
  rw [Poly.norm, Poly.eval_perm κ (List.reverse_perm _), Poly.eval_combine, Poly.eval_perm κ (List.mergeSort_perm p _),
    Poly.eval_nil]; grind

theorem Poly.eval_neg (κ : String → Rat) (p : Poly) : Poly.eval κ (Poly.neg p) = - Poly.eval κ p := by
  induction p with
  | nil => simp only [Poly.neg, List.map_nil, Poly.eval_nil]; grind
  | cons m p ih => simp only [Poly.neg, List.map_cons, Poly.eval_cons] at *; rw [ih]; grind

theorem Poly.eval_mapMul (κ : String → Rat) (m : Mono) (q : Poly) :
    Poly.eval κ (q.map m.mul) = m.coeff * vprod κ m.vars * Poly.eval κ q := by
  induction q with
  | nil => simp only [List.map_nil, Poly.eval_nil]; grind
  | cons n q ih => simp only [List.map_cons, Poly.eval_cons, Mono.mul, vprod_mulVars, ih]; grind

theorem Poly.eval_mulRaw (κ : String → Rat) (p q : Poly) :
    Poly.eval κ (p.flatMap fun m => q.map m.mul) = Poly.eval κ p * Poly.eval κ q := by
  induction p with
  | nil => simp only [List.flatMap_nil, Poly.eval_nil]; grind
  | cons m p ih => simp only [List.flatMap_cons, Poly.eval_append, ih, Poly.eval_cons, Poly.eval_mapMul]; grind

theorem Poly.guard_some {p r : Poly} (h : Poly.guard p = some r) : r = p := by
  unfold Poly.guard at h; split at h <;> simp_all

theorem Poly.add?_sound (κ : String → Rat) {p q r : Poly} (h : Poly.add? p q = some r) :
    Poly.eval κ r = Poly.eval κ p + Poly.eval κ q := by
  unfold Poly.add? at h; split at h
  · rw [Poly.guard_some h, Poly.eval_norm, Poly.eval_append]
  · cases h

theorem Poly.mul?_sound (κ : String → Rat) {p q r : Poly} (h : Poly.mul? p q = some r) :
    Poly.eval κ r = Poly.eval κ p * Poly.eval κ q := by
  unfold Poly.mul? at h; split at h
  · rw [Poly.guard_some h, Poly.eval_norm, Poly.eval_mulRaw]
  · cases h

theorem Poly.pow?_sound (κ : String → Rat) {p r : Poly} {k : Nat} (h : Poly.pow? p k = some r) :
    Poly.eval κ r = Poly.eval κ p ^ k := by
  have hgo : ∀ k s r, Poly.pow?.go p k s = some r → Poly.eval κ r = Poly.eval κ s * Poly.eval κ p ^ k := by
    intro k
    induction k with
    | zero => intro s r h; simp only [Poly.pow?.go, Option.some.injEq] at h; subst h; grind
    | succ k ih =>
        intro s r h
        simp only [Poly.pow?.go, Option.bind_eq_some_iff] at h
        obtain ⟨s', hs, hr⟩ := h
        rw [ih s' r hr, Poly.mul?_sound κ hs]; grind
  unfold Poly.pow? at h; split at h
  · rw [hgo k _ r h, Poly.eval_one]; grind
  · cases h

theorem rpow_mul (a b : Rat) (k : Nat) : (a * b) ^ k = a ^ k * b ^ k := by
  induction k with
  | zero => grind
  | succ k ih => rw [Rat.pow_succ, Rat.pow_succ, Rat.pow_succ, ih]; grind

theorem rpow_ne (a : Rat) (k : Nat) (h : a ≠ 0) : a ^ k ≠ 0 := by
  induction k with
  | zero => grind
  | succ k ih => rw [Rat.pow_succ]; grind

theorem rone_pow (k : Nat) : (1 : Rat) ^ k = 1 := by
  induction k with
  | zero => grind
  | succ k ih => rw [Rat.pow_succ, ih]; grind

theorem rdiv_pow (n d : Rat) (k : Nat) (hd : d ≠ 0) : (n / d) ^ k = n ^ k / d ^ k := by
  have e : n ^ k = (n / d) ^ k * d ^ k := by
    conv => lhs; rw [show n = n / d * d by grind]
    rw [rpow_mul]
  have := rpow_ne d k hd
  rw [e]; grind

/-- `f` means `x` at `κ`: its denominator is not zero there and `x` is their quotient. -/
def Frac.Means (κ : String → Rat) (f : Frac) (x : Rat) : Prop :=
  Poly.eval κ f.2 ≠ 0 ∧ x = Poly.eval κ f.1 / Poly.eval κ f.2

theorem Frac.pair_some {o1 o2 : Option Poly} {h : Frac} (he : (o1.bind fun n => o2.map (n, ·)) = some h) :
    o1 = some h.1 ∧ o2 = some h.2 := by
  cases o1 <;> cases o2 <;> simp_all <;> subst he <;> simp

theorem Frac.add?_sound {κ f g h x y} (hf : Frac.Means κ f x) (hg : Frac.Means κ g y) (he : Frac.add? f g = some h) :
    Frac.Means κ h (x + y) := by
  unfold Frac.add? at he; unfold Frac.Means at *
  split at he
  · rename_i hd
    simp only [Option.map_eq_some_iff] at he; obtain ⟨s, hs, rfl⟩ := he
    simp only [Poly.add?_sound κ hs]; rw [hd] at hf; grind
  · simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at he
    obtain ⟨l, hl, r, hr, s, hs, d, hd, rfl⟩ := he
    simp only [Poly.add?_sound κ hs, Poly.mul?_sound κ hl, Poly.mul?_sound κ hr, Poly.mul?_sound κ hd]; grind

theorem Frac.mul?_sound {κ f g h x y} (hf : Frac.Means κ f x) (hg : Frac.Means κ g y) (he : Frac.mul? f g = some h) :
    Frac.Means κ h (x * y) := by
  obtain ⟨hn, hd⟩ := Frac.pair_some he
  unfold Frac.Means at *; simp only [Poly.mul?_sound κ hn, Poly.mul?_sound κ hd]; grind

theorem Frac.div?_sound {κ f g h x y} (hf : Frac.Means κ f x) (hg : Frac.Means κ g y) (hy : y ≠ 0)
    (he : Frac.div? f g = some h) : Frac.Means κ h (x / y) := by
  obtain ⟨hn, hd⟩ := Frac.pair_some he
  unfold Frac.Means at *; simp only [Poly.mul?_sound κ hn, Poly.mul?_sound κ hd]
  have : Poly.eval κ g.1 ≠ 0 := by intro h0; apply hy; rw [hg.2, h0]; grind
  grind

theorem Frac.pow?_sound {κ f h x} {k : Nat} (hf : Frac.Means κ f x) (he : Frac.pow? f k = some h) :
    Frac.Means κ h (x ^ k) := by
  obtain ⟨hn, hd⟩ := Frac.pair_some he
  unfold Frac.Means at *; simp only [Poly.pow?_sound κ hn, Poly.pow?_sound κ hd]
  obtain ⟨h0, rfl⟩ := hf
  exact ⟨rpow_ne _ k h0, rdiv_pow _ _ k h0⟩

theorem Frac.go_sound (κ : String → Rat) (e : Expr) (x : Rat) (hx : Denotes (fun v => some (κ v)) e x) :
    ∀ f, Frac.go e = some f → Frac.Means κ f x := by
  induction hx with
  | lit =>
      intro f h; simp only [Frac.go, Option.map_eq_some_iff] at h; obtain ⟨p, hp, rfl⟩ := h; rw [Poly.guard_some hp]
      simp only [Frac.Means, Poly.eval_one, Poly.eval_cons0, Poly.eval_cons, Poly.eval_nil]; simp [vprod]; grind
  | val hv =>
      intro f h; simp only [Frac.go, Option.some.injEq] at h; subst h; simp only [Option.some.injEq] at hv; subst hv
      simp only [Frac.Means, Poly.eval_one, Poly.eval_cons, Poly.eval_nil]; simp [vprod]; grind
  | add _ _ iha ihb | mul _ _ iha ihb =>
      intro f h; simp only [Frac.go, Option.bind_eq_some_iff] at h; obtain ⟨g, hg, g', hg', h⟩ := h
      first | exact Frac.add?_sound (iha g hg) (ihb g' hg') h | exact Frac.mul?_sound (iha g hg) (ihb g' hg') h
  | @sub _ _ x y _ _ iha ihb =>
      intro f h; simp only [Frac.go, Option.bind_eq_some_iff] at h; obtain ⟨g, hg, g', hg', h⟩ := h
      have hn : Frac.Means κ (Poly.neg g'.1, g'.2) (-y) := by
        have := ihb g' hg'; unfold Frac.Means at *; simp only [Poly.eval_neg]; grind
      have := Frac.add?_sound (iha g hg) hn h; rw [Rat.sub_eq_add_neg]; exact this
  | div _ _ hne iha ihb =>
      intro f h; simp only [Frac.go, Option.bind_eq_some_iff] at h; obtain ⟨g, hg, g', hg', h⟩ := h
      exact Frac.div?_sound (iha g hg) (ihb g' hg') hne h
  | pow _ ih =>
      intro f h; simp only [Frac.go, Option.bind_eq_some_iff] at h; obtain ⟨g, hg, h⟩ := h
      exact Frac.pow?_sound (ih g hg) h

theorem Frac.ofExpr_sound (κ : String → Rat) (e : Expr) (n d : Poly) (x : Rat)
    (h : Frac.ofExpr? e = some (n, d)) (hx : Denotes (fun v => some (κ v)) e x) :
    d.eval κ ≠ 0 ∧ x = n.eval κ / d.eval κ := by
  unfold Frac.ofExpr? at h; split at h
  · exact Frac.go_sound κ e x hx _ h
  · cases h

theorem Expr.eval_noDiv (κ : String → Rat) (e : Expr) (h : e.hasDiv = false) :
    (e.eval fun v => some (κ v)) ≠ none := by
  induction e <;> simp_all [Expr.hasDiv, Expr.eval, Option.ne_none_iff_exists']

theorem Poly.ofExpr_sound (κ : String → Rat) (e : Expr) (p : Poly) (h : Poly.ofExpr? e = some p) :
    Denotes (fun n => some (κ n)) e (p.eval κ) := by
  simp only [Poly.ofExpr?, Option.bind_eq_some_iff] at h; obtain ⟨f, hf, h⟩ := h
  split at h
  · cases h
  · rename_i hd
    split at h
    · rename_i h1; cases h
      obtain ⟨x, hx⟩ := Option.ne_none_iff_exists'.mp (Expr.eval_noDiv κ e (by simpa using hd))
      have hm := Frac.ofExpr_sound κ e f.1 f.2 x hf (Expr.eval_sound _ _ _ hx)
      rw [h1, Poly.eval_one] at hm
      have : x = Poly.eval κ f.1 := by rw [hm.2]; grind
      rw [← this]; exact Expr.eval_sound _ _ _ hx
    · cases h

/-- **Identity**: equal cross-multiplied normal forms mean equal values wherever both sides denote. -/
theorem identity_sound (a b : Expr) (h : identityCheck a b = true) (κ : String → Rat) (x y : Rat)
    (hx : Denotes (fun v => some (κ v)) a x) (hy : Denotes (fun v => some (κ v)) b y) : x = y := by
  simp only [identityCheck, Identity.compare] at h
  cases ha : Frac.ofExpr? a with
  | none => simp [ha] at h
  | some fa =>
    cases hb : Frac.ofExpr? b with
    | none => simp [ha, hb] at h
    | some fb =>
      cases hl : Poly.mul? fa.1 fb.2 with
      | none => simp [ha, hb, hl] at h
      | some l =>
        cases hr : Poly.mul? fb.1 fa.2 with
        | none => simp [ha, hb, hl, hr] at h
        | some r =>
          simp only [ha, hb, hl, hr, Option.bind_some, Option.map_some, Option.getD_some, beq_iff_eq] at h
          subst h
          have h1 := Frac.ofExpr_sound κ a fa.1 fa.2 x ha hx
          have h2 := Frac.ofExpr_sound κ b fb.1 fb.2 y hb hy
          have e1 := Poly.mul?_sound κ hl; have e2 := Poly.mul?_sound κ hr
          rw [h1.2, h2.2]; grind

theorem differsAt_sound (a b : Expr) (κ : List (String × Rat)) (h : differsAt a b κ = true) :
    ∃ x y, Denotes (fun n => κ.lookup n) a x ∧ Denotes (fun n => κ.lookup n) b y ∧ x ≠ y := by
  simp only [differsAt] at h; split at h
  · rename_i x y hx hy; exact ⟨x, y, Expr.eval_sound _ _ _ hx, Expr.eval_sound _ _ _ hy, by simpa using h⟩
  · cases h

/-! ### Limits

An answer other than `none` is given under one condition: every limit check passed. A side has at most
`maxPolyTerms` nodes, and every polynomial built on the way, from a literal to the cross-multiplied sides, is
`Within`. Every other case is `none`; the fixtures pin each check at its limit and one past it. -/

/-- The limits of a polynomial: `fits` (digits and exponents) and at most `maxPolyTerms` terms. -/
def Poly.Within (p : Poly) : Prop := p.fits = true ∧ p.length ≤ maxPolyTerms

theorem Poly.guard_fits {p r : Poly} (h : Poly.guard p = some r) : r.fits = true := by
  unfold Poly.guard at h; split at h <;> simp_all

theorem Poly.length_norm (p : Poly) : (Poly.norm p).length ≤ p.length := by
  have h0 : ∀ (m : Mono) (p : Poly), (Poly.cons0 m p).length ≤ p.length + 1 := by
    intro m p; unfold Poly.cons0; split <;> simp
  have hc : ∀ acc q : Poly, (Poly.combine acc q).length ≤ acc.length + q.length := by
    intro acc q
    fun_induction Poly.combine acc q with
    | case1 => simp
    | case2 n acc m p _ ih => have := h0 ⟨n.coeff + m.coeff, m.vars⟩ acc; simp only [List.length_cons]; omega
    | case3 n acc m p _ ih => have := h0 m (n :: acc); simp only [List.length_cons] at *; omega
    | case4 m p ih => have := h0 m []; simp only [List.length_cons, List.length_nil] at *; omega
  have := hc [] (p.mergeSort fun m n => varsLe m.vars n.vars)
  simp only [List.length_mergeSort, List.length_nil] at this; simpa [Poly.norm] using this

theorem Poly.length_mulRaw (p q : Poly) : (p.flatMap fun m => q.map m.mul).length = p.length * q.length := by
  induction p with
  | nil => simp
  | cons m p ih => simp only [List.flatMap_cons, List.length_append, List.length_map, ih, List.length_cons,
      Nat.succ_mul]; omega

theorem Poly.add?_within {p q r : Poly} (h : Poly.add? p q = some r) : r.Within := by
  unfold Poly.add? at h; split at h
  · refine ⟨Poly.guard_fits h, ?_⟩; rw [Poly.guard_some h]
    have := Poly.length_norm (p ++ q); simp only [List.length_append] at this; omega
  · cases h

theorem Poly.mul?_within {p q r : Poly} (h : Poly.mul? p q = some r) : r.Within := by
  unfold Poly.mul? at h; split at h
  · refine ⟨Poly.guard_fits h, ?_⟩; rw [Poly.guard_some h]
    have := Poly.length_norm (p.flatMap fun m => q.map m.mul); rw [Poly.length_mulRaw] at this; omega
  · cases h

theorem Poly.one_within : Poly.one.Within :=
  ⟨by simp [Poly.one, Poly.fits, Poly.coeffBound, maxPolyExponent]; exact Nat.one_lt_pow (by decide) (by decide),
   by simp [Poly.one, maxPolyTerms]⟩

theorem Poly.pow?_within {p r : Poly} {k : Nat} (h : Poly.pow? p k = some r) : r.Within := by
  have hgo : ∀ k s r, s.Within → Poly.pow?.go p k s = some r → r.Within := by
    intro k
    induction k with
    | zero => intro s r hs h; simp only [Poly.pow?.go, Option.some.injEq] at h; subst h; exact hs
    | succ k ih =>
        intro s r _ h; simp only [Poly.pow?.go, Option.bind_eq_some_iff] at h
        obtain ⟨s', hs, hr⟩ := h; exact ih s' r (Poly.mul?_within hs) hr
  unfold Poly.pow? at h; split at h
  · exact hgo k _ r Poly.one_within h
  · cases h

theorem Frac.go_within (e : Expr) : ∀ f, Frac.go e = some f → f.1.Within ∧ f.2.Within := by
  have pair : ∀ {o1 o2 : Option Poly} {h : Frac}, (o1.bind fun n => o2.map (n, ·)) = some h →
      (∀ r, o1 = some r → r.Within) → (∀ r, o2 = some r → r.Within) → h.1.Within ∧ h.2.Within :=
    fun he h1 h2 => ⟨h1 _ (Frac.pair_some he).1, h2 _ (Frac.pair_some he).2⟩
  have add : ∀ {f g h : Frac}, f.2.Within → Frac.add? f g = some h → h.1.Within ∧ h.2.Within := by
    intro f g h hf he; unfold Frac.add? at he; split at he
    · simp only [Option.map_eq_some_iff] at he; obtain ⟨s, hs, rfl⟩ := he; exact ⟨Poly.add?_within hs, hf⟩
    · simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at he
      obtain ⟨_, _, _, _, s, hs, d, hd, rfl⟩ := he; exact ⟨Poly.add?_within hs, Poly.mul?_within hd⟩
  induction e with
  | lit q =>
      intro f h; simp only [Frac.go, Option.map_eq_some_iff] at h; obtain ⟨p, hp, rfl⟩ := h
      refine ⟨⟨Poly.guard_fits hp, ?_⟩, Poly.one_within⟩; rw [Poly.guard_some hp]
      simp only [Poly.cons0]; split <;> simp [maxPolyTerms]
  | val n =>
      intro f h; simp only [Frac.go, Option.some.injEq] at h; subst h
      refine ⟨⟨?_, by simp [maxPolyTerms]⟩, Poly.one_within⟩
      simp [Poly.fits, Poly.coeffBound, maxPolyExponent]; exact Nat.one_lt_pow (by decide) (by decide)
  | add a b iha _ | sub a b iha _ =>
      intro f h; simp only [Frac.go, Option.bind_eq_some_iff] at h; obtain ⟨g, hg, _, _, h⟩ := h
      exact add (iha g hg).2 h
  | mul a b _ _ | div a b _ _ =>
      intro f h; simp only [Frac.go, Option.bind_eq_some_iff] at h; obtain ⟨_, _, _, _, h⟩ := h
      exact pair h (fun _ => Poly.mul?_within) (fun _ => Poly.mul?_within)
  | pow a k _ =>
      intro f h; simp only [Frac.go, Option.bind_eq_some_iff] at h; obtain ⟨_, _, h⟩ := h
      exact pair h (fun _ => Poly.pow?_within) (fun _ => Poly.pow?_within)

/-- **Limits**: a side's fraction form is given only within the node limit, with both polynomials `Within`. -/
theorem Frac.ofExpr_within {e : Expr} {f : Frac} (h : Frac.ofExpr? e = some f) :
    (e.nodesWithin maxPolyTerms).isSome ∧ f.1.Within ∧ f.2.Within := by
  unfold Frac.ofExpr? at h; split at h
  · exact ⟨by assumption, Frac.go_within e f h⟩
  · cases h

/-- **Limits**: a normal form is given only within the node limit, and it is `Within`. -/
theorem Poly.ofExpr_within {e : Expr} {p : Poly} (h : Poly.ofExpr? e = some p) :
    (e.nodesWithin maxPolyTerms).isSome ∧ p.Within := by
  simp only [Poly.ofExpr?, Option.bind_eq_some_iff] at h; obtain ⟨f, hf, h⟩ := h
  have hw := Frac.ofExpr_within hf
  split at h
  · cases h
  · split at h
    · cases h; exact ⟨hw.1, hw.2.1⟩
    · cases h

/-- **Limits**: a comparison is answered only when both sides' forms and both cross products are `Within`. -/
theorem Identity.compare_within {a b : Expr} {r : Bool} (h : Identity.compare a b = some r) :
    ∃ fa fb l s, Frac.ofExpr? a = some fa ∧ Frac.ofExpr? b = some fb ∧ Poly.mul? fa.1 fb.2 = some l ∧
      Poly.mul? fb.1 fa.2 = some s ∧ l.Within ∧ s.Within ∧ r = (l == s) := by
  simp only [Identity.compare, Option.bind_eq_some_iff, Option.map_eq_some_iff] at h
  obtain ⟨fa, ha, fb, hb, l, hl, s, hs, rfl⟩ := h
  exact ⟨fa, fb, l, s, ha, hb, hl, hs, Poly.mul?_within hl, Poly.mul?_within hs, rfl⟩

end VE.Calc
