import VE.Calc.Inline

/-! Algebraic identities (spec 8.2, plan 3.8): both sides are inlined with the free values kept (spec 2.7, J3), brought
to fractions of normal polynomials over ℚ, and compared cross-multiplied. Equal normal forms prove the identity; a
point where both sides denote and differ, found by trying small values, refutes it. -/

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

/-- Merges neighbours with the same variables and drops zero coefficients. -/
def Poly.combine : Poly → Poly
  | [] => []
  | m :: p => match Poly.combine p with
    | n :: q => if m.vars = n.vars then Poly.cons0 ⟨m.coeff + n.coeff, m.vars⟩ q else Poly.cons0 m (n :: q)
    | [] => Poly.cons0 m []

def Poly.norm (p : Poly) : Poly := Poly.combine (p.mergeSort fun m n => varsLe m.vars n.vars)
def Poly.one : Poly := [⟨1, []⟩]
def Poly.neg (p : Poly) : Poly := p.map fun m => ⟨-m.coeff, m.vars⟩

def Poly.fits (p : Poly) : Bool :=
  p.length ≤ maxPolyTerms && p.all fun m => decide (Small m.coeff) && m.vars.all (·.2 ≤ maxPolyExponent)
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

def Frac.go : Expr → Option Frac
  | .lit q => some (Poly.cons0 ⟨q, []⟩ [], Poly.one)
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

/-- The normal form of a division-free expression; `none` with division or beyond the limits. -/
def Poly.ofExpr? (e : Expr) : Option Poly := if e.hasDiv then none else (Frac.ofExpr? e).map Prod.fst

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

theorem Poly.eval_combine (κ : String → Rat) (p : Poly) : Poly.eval κ (Poly.combine p) = Poly.eval κ p := by
  induction p with
  | nil => rfl
  | cons m p ih =>
      simp only [Poly.combine]
      split <;> rename_i h <;> rw [h] at ih
      · split <;> simp_all [Poly.eval_cons0, Poly.eval_cons] <;> grind
      · simp_all [Poly.eval_cons0, Poly.eval_cons]

theorem Poly.eval_perm (κ : String → Rat) {p q : Poly} (h : p.Perm q) : Poly.eval κ p = Poly.eval κ q := by
  induction h with
  | nil => rfl
  | cons _ _ ih => simp [Poly.eval_cons, ih]
  | swap => simp only [Poly.eval_cons]; grind
  | trans _ _ ih1 ih2 => rw [ih1, ih2]

theorem Poly.eval_norm (κ : String → Rat) (p : Poly) : Poly.eval κ (Poly.norm p) = Poly.eval κ p := by
  rw [Poly.norm, Poly.eval_combine, Poly.eval_perm κ (List.mergeSort_perm p _)]

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
      intro f h; simp only [Frac.go, Option.some.injEq] at h; subst h
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

theorem Expr.denotes_of_noDiv (κ : String → Rat) (e : Expr) (h : e.hasDiv = false) :
    ∃ x, Denotes (fun v => some (κ v)) e x := by
  induction e with
  | lit q => exact ⟨q, .lit⟩
  | val n => exact ⟨κ n, .val rfl⟩
  | div => simp [Expr.hasDiv] at h
  | pow a k ih => obtain ⟨x, hx⟩ := ih (by simpa [Expr.hasDiv] using h); exact ⟨_, .pow hx⟩
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb =>
      simp only [Expr.hasDiv, Bool.or_eq_false_iff] at h
      obtain ⟨x, hx⟩ := iha h.1; obtain ⟨y, hy⟩ := ihb h.2
      first | exact ⟨_, .add hx hy⟩ | exact ⟨_, .sub hx hy⟩ | exact ⟨_, .mul hx hy⟩

theorem Frac.go_one (κ : String → Rat) (e : Expr) (h : e.hasDiv = false) (f : Frac) (hf : Frac.go e = some f) :
    Poly.eval κ f.2 = 1 := by
  induction e generalizing f with
  | lit q => simp only [Frac.go, Option.some.injEq] at hf; subst hf; exact Poly.eval_one κ
  | val n => simp only [Frac.go, Option.some.injEq] at hf; subst hf; exact Poly.eval_one κ
  | div => simp [Expr.hasDiv] at h
  | pow a k ih =>
      simp only [Frac.go, Option.bind_eq_some_iff] at hf; obtain ⟨g, hg, hf⟩ := hf
      rw [Poly.pow?_sound κ (Frac.pair_some hf).2, ih (by simpa [Expr.hasDiv] using h) g hg]
      exact rone_pow k
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb =>
      simp only [Expr.hasDiv, Bool.or_eq_false_iff] at h
      simp only [Frac.go, Option.bind_eq_some_iff] at hf; obtain ⟨g, hg, g', hg', hf⟩ := hf
      have h1 := iha h.1 g hg; have h2 := ihb h.2 g' hg'
      first
        | (rw [Poly.mul?_sound κ (Frac.pair_some hf).2, h1, h2]; grind)
        | (unfold Frac.add? at hf; split at hf
           · simp only [Option.map_eq_some_iff] at hf; obtain ⟨s, _, rfl⟩ := hf; exact h1
           · simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at hf
             obtain ⟨_, _, _, _, _, _, d, hd, rfl⟩ := hf; rw [Poly.mul?_sound κ hd, h1, h2]; grind)

theorem Poly.ofExpr_sound (κ : String → Rat) (e : Expr) (p : Poly) (h : Poly.ofExpr? e = some p) :
    Denotes (fun n => some (κ n)) e (p.eval κ) := by
  unfold Poly.ofExpr? at h; split at h
  · cases h
  · rename_i hd
    simp only [Option.map_eq_some_iff] at h; obtain ⟨f, hf, rfl⟩ := h
    obtain ⟨x, hx⟩ := Expr.denotes_of_noDiv κ e (by simpa using hd)
    have hm := Frac.ofExpr_sound κ e f.1 f.2 x hf hx
    unfold Frac.ofExpr? at hf; split at hf
    · rw [Frac.go_one κ e (by simpa using hd) f hf] at hm
      have : x = Poly.eval κ f.1 := by rw [hm.2]; grind
      rw [← this]; exact hx
    · cases hf

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

/-! ### Meaning, refutation and the runner -/

/-- The meaning of an identity: the two sides are equal wherever both denote, for every value of the free values. -/
def IsIdentity (ds : List Decl) (a b : Expr) : Prop :=
  ∀ κ x y, Denotes (values (assign ds (freeNames ds) κ)) a x → Denotes (values (assign ds (freeNames ds) κ)) b y →
    x = y

/-- What a "not an identity" row states. -/
def NotIdentity (ds : List Decl) (a b : Expr) : Prop :=
  ∃ κ x y, Denotes (values (assign ds (freeNames ds) κ)) a x ∧ Denotes (values (assign ds (freeNames ds) κ)) b y ∧
    x ≠ y

theorem not_isIdentity (ds : List Decl) (a b : Expr) (h : NotIdentity ds a b) : ¬ IsIdentity ds a b := by
  obtain ⟨κ, x, y, hx, hy, hne⟩ := h
  exact fun hi => hne (hi κ x y hx hy)

theorem differsAt_sound (a b : Expr) (κ : List (String × Rat)) (h : differsAt a b κ = true) :
    ∃ x y, Denotes (fun n => κ.lookup n) a x ∧ Denotes (fun n => κ.lookup n) b y ∧ x ≠ y := by
  simp only [differsAt] at h; split at h
  · rename_i x y hx hy; exact ⟨x, y, Expr.eval_sound _ _ _ hx, Expr.eval_sound _ _ _ hy, by simpa using h⟩
  · cases h

theorem Denotes.mono {σ τ : Values} {e : Expr} {x : Rat} (h : Denotes σ e x) (hστ : ∀ n q, σ n = some q → τ n = some q) :
    Denotes τ e x := by
  induction h with
  | lit => exact .lit
  | val hv => exact .val (hστ _ _ hv)
  | add _ _ iha ihb => exact .add iha ihb
  | sub _ _ iha ihb => exact .sub iha ihb
  | mul _ _ iha ihb => exact .mul iha ihb
  | div _ _ hne iha ihb => exact .div iha ihb hne
  | pow _ ih => exact .pow ih

theorem freeNames_mem (ds : List Decl) : ∀ n ∈ freeNames ds, n ∈ ds.map Decl.name := by
  intro n hn; simp only [freeNames, List.mem_map, List.mem_filter] at hn ⊢
  obtain ⟨d, ⟨hd, _⟩, rfl⟩ := hn; exact ⟨d, hd, rfl⟩

/-- Over the inlined sides, the normaliser proves the identity and a differing point refutes it (J3). -/
theorem isIdentity_of_check (ds : List Decl) (h : WellFormed ds) (a b a' b' : Expr)
    (ha : a.inline ds (freeNames ds) = .ok a') (hb : b.inline ds (freeNames ds) = .ok b')
    (hc : identityCheck a' b' = true) : IsIdentity ds a b := by
  intro κ x y hx hy
  exact identity_sound a' b' hc κ x y ((Expr.inline_sound ds h _ (freeNames_mem ds) a a' ha κ x).mp hx)
    ((Expr.inline_sound ds h _ (freeNames_mem ds) b b' hb κ y).mp hy)

theorem notIdentity_of_differsAt (ds : List Decl) (h : WellFormed ds) (a b a' b' : Expr)
    (ha : a.inline ds (freeNames ds) = .ok a') (hb : b.inline ds (freeNames ds) = .ok b')
    (κ : List (String × Rat)) (hd : differsAt a' b' κ = true) : NotIdentity ds a b := by
  obtain ⟨x, y, hx, hy, hne⟩ := differsAt_sound a' b' κ hd
  let κ' : String → Rat := fun n => (κ.lookup n).getD 0
  have hm : ∀ n q, κ.lookup n = some q → some (κ' n) = some q := by intro n q h; simp [κ', h]
  exact ⟨κ', x, y, (Expr.inline_sound ds h _ (freeNames_mem ds) a a' ha κ' x).mpr (hx.mono hm),
    (Expr.inline_sound ds h _ (freeNames_mem ds) b b' hb κ' y).mpr (hy.mono hm), hne⟩

/-- The values tried, in order: point `i` gives the `j`th name the value `identityValues[i * (j + 1) % 13]`, so
point 0 sets every name to 1. -/
def identityValues : List Rat := [1, 2, 3, -1, 1/2, 5, -2, 1/3, 7, -3, 3/2, 11, 0]

def identityPoint (names : List String) (i : Nat) : List (String × Rat) :=
  names.mapIdx fun j n => (n, identityValues.getD (i * (j + 1) % 13) 0)

/-- A row: its outcome, and for `fails` the point (one value per free value read, in declaration order) and the two
sides' values there. -/
structure IdentityRow where
  outcome : Outcome
  point : Option (List (String × Rat)) := none
  sides : Option (Rat × Rat) := none
  deriving Repr, DecidableEq

/-- Over inlined sides: compare the normal forms, else try the 13 points over the names of `keep` the sides read. The
names are listed only once the normaliser has accepted both sides, whose trees are then within the node limit. -/
def identityDecide (keep : List String) (a' b' : Expr) : IdentityRow :=
  match Identity.compare a' b' with
  | none => ⟨.unknown (.limit .polyTerms), none, none⟩
  | some true => ⟨.decided .holds, none, none⟩
  | some false =>
    let names := keep.filter (· ∈ a'.names ++ b'.names)
    match ((List.range 13).map (identityPoint names)).find? (differsAt a' b') with
    | some κ => ⟨.decided .fails, some κ, (a'.eval (κ.lookup ·)).bind fun x => (b'.eval (κ.lookup ·)).map (x, ·)⟩
    | none => ⟨.unknown .identityNotShown, none, none⟩

/-- The identity row (spec 8.2): inline both sides with the free values kept, the first faulty side naming the fault;
then decide over the free values the sides read, in declaration order. -/
def identityRun (ds : List Decl) (a b : Expr) : IdentityRow :=
  match a.inline ds (freeNames ds), b.inline ds (freeNames ds) with
  | .ok a', .ok b' => identityDecide (freeNames ds) a' b'
  | .error .exhausted, _ | .ok _, .error .exhausted => ⟨.unknown (.limit .evaluations), none, none⟩
  | _, _ => ⟨.decided .undefined, none, none⟩

theorem identityDecide_outcome (keep : List String) (a' b' : Expr) :
    ((identityDecide keep a' b').outcome = .decided .holds → identityCheck a' b' = true) ∧
    ((identityDecide keep a' b').outcome = .decided .fails → ∃ κ, differsAt a' b' κ = true) ∧
    (identityDecide keep a' b').outcome ≠ .decided .undefined ∧
    (∀ u, (identityDecide keep a' b').outcome = .unknown u → u = .limit .polyTerms ∨ u = .identityNotShown) := by
  unfold identityDecide
  split
  · simp
  · rename_i h; simp [identityCheck, h]
  · dsimp only; split
    · rename_i κ hκ; simpa using ⟨κ, List.find?_some hκ⟩
    · simp

theorem identityRun_holds (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .holds) : IsIdentity ds a b := by
  cases ha : a.inline ds (freeNames ds) with
  | error v => cases v <;> simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v => cases v <;> simp [identityRun, ha, hb] at hr
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        exact isIdentity_of_check ds h a b _ _ ha hb ((identityDecide_outcome _ _ _).1 hr)

theorem identityRun_fails (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .fails) : NotIdentity ds a b := by
  cases ha : a.inline ds (freeNames ds) with
  | error v => cases v <;> simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v => cases v <;> simp [identityRun, ha, hb] at hr
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        obtain ⟨κ, hκ⟩ := (identityDecide_outcome _ _ _).2.1 hr
        exact notIdentity_of_differsAt ds h a b _ _ ha hb κ hκ

theorem identityRun_undefined (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .undefined) :
    ∃ e ∈ [a, b], ∀ κ x, ¬ Denotes (values (assign ds (freeNames ds) κ)) e x := by
  have hu := fun e (he : e.inline ds (freeNames ds) = .error .undefined) => Expr.inline_undefined ds h _ e he
  cases ha : a.inline ds (freeNames ds) with
  | error v =>
      rcases Expr.inline_error ds _ a v ha with rfl | rfl
      · exact ⟨a, by simp, hu a ha⟩
      · simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v =>
        rcases Expr.inline_error ds _ b v hb with rfl | rfl
        · exact ⟨b, by simp, hu b hb⟩
        · simp [identityRun, ha, hb] at hr
    | ok b' => simp only [identityRun, ha, hb] at hr; exact absurd hr (identityDecide_outcome _ _ _).2.2.1

/-- An unknown row gives one of the identity's reasons, with the cause the evaluation budget names (spec 3.4). -/
theorem identityRun_unknown (ds : List Decl) (a b : Expr) (u : UnknownReason)
    (hr : (identityRun ds a b).outcome = .unknown u) :
    u ∈ [.limit .polyTerms, .identityNotShown, .limit .digits, .limit .evaluations] ∧
      (u = .limit .digits → ∃ e ∈ [a, b], e.Overflows ds) ∧
      (u = .limit .evaluations → ∃ e ∈ [a, b], e.ReadsExhausted ds) := by
  cases ha : a.inline ds (freeNames ds) with
  | error v =>
      rcases Expr.inline_error ds _ a v ha with rfl | rfl
      · simp [identityRun, ha] at hr
      · simp only [identityRun, ha, Outcome.unknown.injEq] at hr; subst hr
        simpa using Or.inl (Expr.inline_exhausted ds _ a ha)
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v =>
        rcases Expr.inline_error ds _ b v hb with rfl | rfl
        · simp [identityRun, ha, hb] at hr
        · simp only [identityRun, ha, hb, Outcome.unknown.injEq] at hr; subst hr
          simpa using Or.inr (Expr.inline_exhausted ds _ b hb)
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        rcases (identityDecide_outcome _ _ _).2.2.2 u hr with rfl | rfl <;> simp

end VE.Calc
