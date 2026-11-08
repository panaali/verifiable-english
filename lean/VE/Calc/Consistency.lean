import VE.Calc.Interval
import VE.Calc.Inline
import VE.Calc.Poly
import VE.Calc.Stats

/-! Consistency of printed numbers (math-evidence spec 8.1, ME-8): the one proposition `Consistent` (statement review
J4), a witness that establishes it and an enclosure or a granularity that refutes it, all over the outputs inlined
with the inputs kept (2.7); GRIM (`mean_grain_refutes`) and the sign-flip granularity (`signFlip_grain_refutes`). -/

namespace VE.Calc
open VE.Numbers Work

/-- The meaning of a consistency check (J4). -/
def Consistent (ds : List Decl) (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) : Prop :=
  ∃ κ : String → Rat, InBox r inputs κ ∧ ∀ c ∈ outs, c.Holds (values (assign ds (inputs.map Prod.fst) κ))

/-- A witness for inlined outputs: a value for every input, inside its interval, under which every output holds. -/
def witnessCheck (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim)
    (w : List (String × Rat)) : Bool :=
  inputs.all (fun i => match w.lookup i.1 with
    | some x => decide (RoundsTo r i.2 x)
    | none => false) &&
  outs.all fun c => c.decide (fun n => w.lookup n) == .holds

/-- No pair of points of the two intervals is in the relation. -/
def _root_.VE.Numbers.Rel.misses : Rel → Rat × Rat → Rat × Rat → Bool
  | .eq, x, y => Decidable.decide (x.2 < y.1 ∨ y.2 < x.1)
  | .lt, x, y => Decidable.decide (y.2 ≤ x.1)
  | .le, x, y => Decidable.decide (y.2 < x.1)

/-- An output whose sides' enclosures, in `Claim.exprs`' order, show it false at every point. -/
def Claim.misses : Claim → List (Option (Rat × Rat)) → Bool
  | .compare c _ _, [some x, some y] => if c.swap then c.rel.misses y x else c.rel.misses x y
  | .within .., [some x, some l, some h] => Decidable.decide (x.2 < l.1 ∨ h.2 < x.1 ∨ h.2 < l.1)
  | .rounds r _ p, [some x] => Decidable.decide (x.2 < (p.box r).1 ∨ (p.box r).2 < x.1)
  | _, _ => false

/-- *Opaque* in spec 8.1: an inlined output whose enclosures show it false at every point of the input intervals. -/
def refuteByEnclosure (r : Rounding) (inputs : List (String × Printed)) (c : Claim) : Bool :=
  c.misses (c.exprs.map (enclose r inputs))

set_option linter.unusedVariables false in
/-- *Opaque* in spec 8.1: an inlined output `rounds r' (.stat .signFlip xs) p` with `grainRefutes (2 ^ xs.length) r' p`.
`Expr` has no `.stat` yet (me-7b), so no claim carries a sign-flip p and none is refuted here; the arm comes with it. -/
def refuteByGrain (c : Claim) : Bool := false

theorem refuteByEnclosure_sound (r : Rounding) (inputs : List (String × Printed)) (c : Claim)
    (h : refuteByEnclosure r inputs c = true) (κ : String → Rat) (hκ : InBox r inputs κ) :
    ¬ c.Holds (fun n => some (κ n)) := by
  have hs := fun e lo hi he x hx => enclose_sound r inputs e lo hi he κ hκ x hx
  cases c with
  | compare k a b =>
    rintro ⟨x, y, hx, hy, hk⟩
    simp only [refuteByEnclosure, Claim.exprs, List.map] at h
    cases ha : enclose r inputs a with
    | none => simp [ha, Claim.misses] at h
    | some A =>
      cases hb : enclose r inputs b with
      | none => simp [ha, hb, Claim.misses] at h
      | some B =>
        have := hs a A.1 A.2 ha x hx; have := hs b B.1 B.2 hb y hy
        obtain ⟨rel, swap⟩ := k
        cases rel <;> cases swap <;>
          simp_all [Claim.misses, Rel.misses, Comparison.Holds, Rel.Holds] <;> grind
  | within e lo hi =>
    rintro ⟨x, l, u, hx, hl, hu, h1, h2⟩
    simp only [refuteByEnclosure, Claim.exprs, List.map] at h
    cases he : enclose r inputs e <;> cases hle : enclose r inputs lo <;> cases hhi : enclose r inputs hi <;>
      simp only [he, hle, hhi, Claim.misses, decide_eq_true_eq, Bool.false_eq_true] at h
    rename_i X L U
    have := hs e X.1 X.2 he x hx; have := hs lo L.1 L.2 hle l hl; have := hs hi U.1 U.2 hhi u hu; grind
  | rounds r' e p =>
    rintro ⟨x, hx, hr⟩
    simp only [refuteByEnclosure, Claim.exprs, List.map] at h
    cases he : enclose r inputs e <;> simp only [he, Claim.misses, decide_eq_true_eq, Bool.false_eq_true] at h
    rename_i X
    have := hs e X.1 X.2 he x hx; have := Printed.box_sound r' p x hr; grind

theorem refuteByGrain_sound (c : Claim) (h : refuteByGrain c = true) (σ : Values) : ¬ c.Holds σ := by
  simp [refuteByGrain] at h

theorem mapM_ok_mem {α β ε : Type} {f : α → Except ε β} {xs : List α} {ys : List β} (h : xs.mapM f = .ok ys) :
    (∀ x ∈ xs, ∃ y ∈ ys, f x = .ok y) ∧ (∀ y ∈ ys, ∃ x ∈ xs, f x = .ok y) := by
  induction xs generalizing ys with
  | nil => simp only [List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h; subst h; simp
  | cons x xs ih =>
    simp only [List.mapM_cons, bind, Except.bind, pure, Except.pure] at h
    cases hx : f x with
    | error e => simp [hx] at h
    | ok y =>
      cases hr : xs.mapM f with
      | error e => simp [hx, hr] at h
      | ok ys' =>
        simp only [hx, hr, Except.ok.injEq] at h; subst h
        obtain ⟨ih1, ih2⟩ := ih hr
        refine ⟨fun z hz => ?_, fun z hz => ?_⟩
        · rcases List.mem_cons.mp hz with rfl | hz
          · exact ⟨y, by simp, hx⟩
          · obtain ⟨u, hu, hfu⟩ := ih1 z hz; exact ⟨u, by simp [hu], hfu⟩
        · rcases List.mem_cons.mp hz with rfl | hz
          · exact ⟨x, by simp, hx⟩
          · obtain ⟨u, hu, hfu⟩ := ih2 z hz; exact ⟨u, by simp [hu], hfu⟩

/-- An inlined claim reads only kept names. -/
theorem Claim.inline_names (ds : List Decl) (keep : List String) (c c' : Claim) (hc : c.inline ds keep = .ok c') :
    ∀ e ∈ c'.exprs, ∀ n ∈ e.names, n ∈ keep := by
  have hn := fun e e' (he : e.inline ds keep = .ok e') => Expr.inline_names ds keep e e' he
  cases c <;> simp only [Claim.inline, Claim.subst, bind, Except.bind, pure, Except.pure] at hc <;>
    (repeat' split at hc) <;> simp only [reduceCtorEq, Except.ok.injEq] at hc <;> subst hc <;>
    simp only [Claim.exprs, List.mem_cons, List.not_mem_nil, or_false] <;> rintro e (rfl | rfl | rfl) <;>
    first | exact hn _ _ ‹_› | (rename_i h; exact hn _ _ h)

theorem Claim.decide_congr_on (c : Claim) (σ τ : Values) (h : ∀ e ∈ c.exprs, ∀ n ∈ e.names, σ n = τ n) :
    c.decide σ = c.decide τ := by
  have he := fun e (m : e ∈ c.exprs) => Expr.eval_congr_on e σ τ (h e m)
  cases c with
  | compare k a b => simp only [Claim.decide]; rw [he a (by simp [Claim.exprs]), he b (by simp [Claim.exprs])]
  | within e lo hi =>
    simp only [Claim.decide]
    rw [he e (by simp [Claim.exprs]), he lo (by simp [Claim.exprs]), he hi (by simp [Claim.exprs])]
  | rounds r e p => simp only [Claim.decide]; rw [he e (by simp [Claim.exprs])]

/-- The witness establishes the one proposition, over one lowering. -/
theorem consistent_of_witness (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (w : List (String × Rat))
    (hw : witnessCheck r inputs outs' w = true) : Consistent ds r inputs outs := by
  simp only [witnessCheck, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at hw
  obtain ⟨hin, hout⟩ := hw
  have hlk : ∀ i ∈ inputs, ∃ x, w.lookup i.1 = some x ∧ RoundsTo r i.2 x := fun i hi => by
    have := hin i hi; split at this <;> simp_all
  let κ : String → Rat := fun n => (w.lookup n).getD 0
  refine ⟨κ, fun i hi => ?_, fun c hc => ?_⟩
  · obtain ⟨x, hx, hr⟩ := hlk i hi; simpa [κ, hx] using hr
  · obtain ⟨c', hc', hi⟩ := (mapM_ok_mem hl).1 c hc
    have hk' : ∀ n ∈ inputs.map Prod.fst, n ∈ ds.map Decl.name := fun n hn => by
      obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hn; exact hk i hi
    rw [Claim.inline_sound ds h _ hk' c c' hi κ, ← Claim.decide_holds]
    rw [Claim.decide_congr_on c' _ (fun n => w.lookup n) fun e he n hn => ?_]
    · exact hout c' hc'
    · obtain ⟨i, hi, rfl⟩ := List.mem_map.mp (Claim.inline_names ds _ c c' hi e he n hn)
      obtain ⟨x, hx, _⟩ := hlk i hi; simp [κ, hx]

/-- An enclosure that misses an inlined output, or a sign-flip granularity refutation, refutes the same proposition. -/
theorem inconsistent_of_refutation (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (c : Claim) (hc : c ∈ outs')
    (hr : refuteByEnclosure r inputs c = true ∨ refuteByGrain c = true) : ¬ Consistent ds r inputs outs := by
  rintro ⟨κ, hbox, hall⟩
  obtain ⟨c0, hc0, hi⟩ := (mapM_ok_mem hl).2 c hc
  have hk' : ∀ n ∈ inputs.map Prod.fst, n ∈ ds.map Decl.name := fun n hn => by
    obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hn; exact hk i hi
  have hholds := (Claim.inline_sound ds h _ hk' c0 c hi κ).mp (hall c0 hc0)
  rcases hr with hr | hr
  · exact refuteByEnclosure_sound r inputs c hr κ hbox hholds
  · exact refuteByGrain_sound c hr _ hholds

/-- No multiple of `1/g` rounds to `p` under `r` (the candidates are the multiples near p's interval). -/
def grainRefutes (g : Nat) (r : Rounding) (p : Printed) : Bool :=
  let u := tenPow p.places
  let a := Rat.floor ((p.digits - 1 : Rat) / u * g) - 1
  let b := Rat.ceil ((p.digits + 1 : Rat) / u * g) + 1
  (List.range (b - a + 1).toNat).all fun i => !decide (RoundsTo r p (((a + i : Int) : Rat) / g))

/-- Every rule's interval lies within one unit of the last place. -/
theorem roundsTo_near (r : Rounding) (p : Printed) (x : Rat) (h : RoundsTo r p x) :
    (p.digits : Rat) - 1 ≤ x * tenPow p.places ∧ x * tenPow p.places ≤ p.digits + 1 := by
  cases r <;> simp only [RoundsTo] at h <;> grind

theorem grain_sound (g : Nat) (hg : 0 < g) (r : Rounding) (p : Printed) (h : grainRefutes g r p = true) :
    ∀ m : Int, ¬ RoundsTo r p ((m : Rat) / g) := by
  intro m hm
  have hu := tenPow_pos p.places
  have hg' : (0 : Rat) < g := by exact_mod_cast hg
  obtain ⟨h1, h2⟩ := roundsTo_near r p _ hm
  -- (D ∓ 1) / u * g brackets m: multiply the bounds on m / g * u by g / u.
  have hc : (0 : Rat) ≤ g * (tenPow p.places)⁻¹ := Rat.le_of_lt (by
    have := Rat.inv_pos.mpr hu; exact Rat.mul_pos hg' this)
  have e1 : (m : Rat) / g * tenPow p.places * (g * (tenPow p.places)⁻¹) = m := by
    rw [Rat.div_def]; have : (g : Rat) ≠ 0 := Rat.ne_of_gt hg'; have : tenPow p.places ≠ 0 := Rat.ne_of_gt hu
    grind
  have hlo := Rat.mul_le_mul_of_nonneg_right h1 hc
  have hhi := Rat.mul_le_mul_of_nonneg_right h2 hc
  rw [e1] at hlo hhi
  have ea : ((p.digits : Rat) - 1) * (g * (tenPow p.places)⁻¹) = (p.digits - 1 : Rat) / tenPow p.places * g := by
    rw [Rat.div_def]; grind
  have eb : ((p.digits : Rat) + 1) * (g * (tenPow p.places)⁻¹) = (p.digits + 1 : Rat) / tenPow p.places * g := by
    rw [Rat.div_def]; grind
  rw [ea] at hlo; rw [eb] at hhi
  have fa := Rat.floor_le ((p.digits - 1 : Rat) / tenPow p.places * g)
  have fb := Rat.floor_le (-((p.digits + 1 : Rat) / tenPow p.places * g))
  have ha : Rat.floor ((p.digits - 1 : Rat) / tenPow p.places * g) ≤ m :=
    Rat.intCast_le_intCast.mp (Rat.le_trans fa hlo)
  have hb : m ≤ Rat.ceil ((p.digits + 1 : Rat) / tenPow p.places * g) := by
    rw [Rat.ceil_eq_neg_floor_neg]
    have : ((-(Rat.floor (-((p.digits + 1 : Rat) / tenPow p.places * g))) : Int) : Rat) ≥ (m : Rat) := by
      push_cast; grind
    exact Rat.intCast_le_intCast.mp this
  simp only [grainRefutes, List.all_eq_true, List.mem_range, Bool.not_eq_true', decide_eq_false_iff_not] at h
  have := h (m - (Rat.floor ((p.digits - 1 : Rat) / tenPow p.places * g) - 1)).toNat (by omega)
  rw [Int.toNat_of_nonneg (by omega), Int.add_comm, Int.sub_add_cancel] at this
  exact this hm

/-- Granularity of sign-flip p values (uses ME-7's `signFlipP_grain`, hence ME-7 → ME-8). -/
theorem signFlip_grain_refutes (d : List Rat) (r : Rounding) (p : Printed)
    (h : grainRefutes (2 ^ d.length) r p = true) : ¬ RoundsTo r p (signFlipP d) := by
  obtain ⟨m, _, hm⟩ := signFlipP_grain d
  have := grain_sound _ (Nat.pow_pos (by decide)) r p h m
  rw [hm]; simpa using this

theorem sum_intCast (xs : List Int) : (xs.map fun (x : Int) => (x : Rat)).sum = ((xs.sum : Int) : Rat) := by
  induction xs with
  | nil => simp
  | cons x xs ih => simp [ih]

/-- GRIM: the mean of n integers is a multiple of 1/n. -/
theorem mean_grain_refutes (xs : List Int) (hx : xs ≠ []) (r : Rounding) (p : Printed)
    (h : grainRefutes xs.length r p = true) :
    ¬ RoundsTo r p ((xs.map fun (x : Int) => (x : Rat)).sum / xs.length) := by
  rw [sum_intCast]; exact grain_sound _ (List.length_pos_iff.mpr hx) r p h _

/-! ## The runner (spec 8.1, 3.1): the decoder's two refusals, one lowering, the enclosures, then at most 4,096 witness
points: the printed values, then the interval endpoints. Each declaration is inlined once; the outputs' trees are held
to `maxPolyTerms` nodes together before either phase walks them; and every enclosure and every point is charged in
3.2's unit against `limit` (the DRI's rule of 2026-10-27): none past it, which the wire refuses as limit 10
(`Wire.workLimit`), never a verdict. -/

/-- The decoder's refusals of a consistency check (3.1, 13.1). -/
inductive ConsistencyRefusal where
  | input (name : String)   -- `ConsistencyInput`: not a stated value, or named twice
  | name (name : String)    -- `ConsistencyName`: an output reads this free value, directly or through definitions
  deriving Repr, DecidableEq

/-- A consistency check's answer, with what it shows: the witness, or the refuted output's index and enclosures. -/
inductive ConsistencyAnswer where
  | refused (f : ConsistencyRefusal)
  | holds (witness : List (String × Rat))
  | fails (output : Nat) (enclosures : List (Rat × Rat))
  | undefined
  | unknown (u : UnknownReason)
  deriving Repr, DecidableEq

/-- The consistency search's limit (14). -/
def maxWitnessPoints : Nat := 4096

def Source.isStated : Source → Bool
  | .stated _ => true
  | _ => false

/-- The first input that is not a stated value or is named twice. -/
def consistencyInputFault (ds : List Decl) : List String → Option String
  | [] => none
  | n :: ns =>
    if n ∈ ns ∨ !(ds.any fun d => d.name == n && d.source.isStated) then some n else consistencyInputFault ds ns

/-- For each declaration, the first free value outside `keep` it reads, directly or through definitions; each
declaration once, in order. -/
def freeReadTable (ds : List Decl) (keep : List String) : List (String × Option String) :=
  ds.foldl (fun t d => (d.name, if d.name ∈ keep then none else match d.source with
    | .free => some d.name
    | .defined e => e.names.findSome? fun n => (t.lookup n).join
    | _ => none) :: t) []

def consistencyNameFault (ds : List Decl) (keep : List String) (outs : List Claim) : Option String :=
  let t := freeReadTable ds keep
  outs.findSome? fun c => (c.exprs.flatMap Expr.names).findSome? fun n => if n ∈ keep then none else (t.lookup n).join

/-- How many nodes the outputs' inlined trees have together; none past `maxPolyTerms` (inlining shares definitions, so
a tree may be far larger than its memory, and the walk stops at the limit). An enclosure and each point visit every
node once, so this bounds the visits of both phases, however many outputs there are. -/
def outputNodes (outs : List Claim) : Option Nat :=
  ((outs.flatMap Claim.exprs).foldlM (fun n (e : Expr) => e.nodesWithin n) maxPolyTerms).map (maxPolyTerms - ·)

/-- What one pass over the outputs costs beyond the sizes of its values (spec 3.2: every kind of work charged in
proportion to its time). A lookup walks the n inputs, about 10 ns a step: the input check makes n of them and each node
at most one. A node's visit, small values included, takes about 64 steps' time (0.64 µs). At 8 units a step, 2^33 units
is at most about 26 s of any shape measured, under the 60 s deadline (`docs/math-evidence/me-8/evidence/limit-times.txt`). -/
def passWork (inputs : List (String × Printed)) (nodes : Nat) : Nat :=
  8 * (inputs.length * inputs.length + nodes * (inputs.length + 64))

/-- Expressions enclosed in order, charged; the inner none when one has no enclosure. -/
def enclosesC (limit : Nat) (r : Rounding) (inputs : List (String × Printed)) :
    List Expr → Nat → Option (Option (List (Rat × Rat)) × Nat)
  | [], w => some (some [], w)
  | e :: es, w => (encloseC limit r inputs e w).bind fun
    | (some x, w) => (enclosesC limit r inputs es w).map fun
      | (some xs, w) => (some (x :: xs), w)
      | (none, w) => (none, w)
    | (none, w) => some (none, w)

/-- The first output, from index `j`, whose enclosures miss it, with them. -/
def refuteC (limit : Nat) (r : Rounding) (inputs : List (String × Printed)) :
    List Claim → Nat → Nat → Option (Option (Nat × List (Rat × Rat)) × Nat)
  | [], _, w => some (none, w)
  | c :: cs, j, w => (enclosesC limit r inputs c.exprs w).bind fun
    | (some es, w) => if c.misses (es.map some) then some (some (j, es), w) else refuteC limit r inputs cs (j + 1) w
    | (none, w) => refuteC limit r inputs cs (j + 1) w

/-- The endpoint point numbered `m`: bit k of `m` takes input k's upper endpoint. -/
def endpointPoint (r : Rounding) (m : Nat) : List (String × Printed) → List (String × Rat)
  | [] => []
  | i :: is => (i.1, if m % 2 = 1 then (i.2.box r).2 else (i.2.box r).1) :: endpointPoint r (m / 2) is

/-- Candidate point `m`, built when it is tried: the printed values, then the 2ⁿ endpoint choices. -/
def witnessPoint (r : Rounding) (inputs : List (String × Printed)) : Nat → List (String × Rat)
  | 0 => inputs.map fun i => (i.1, i.2.value)
  | m + 1 => endpointPoint r m inputs

/-- How many points are tried: at most `maxWitnessPoints`. -/
def witnessCount (inputs : List (String × Printed)) : Nat := 1 + min (2 ^ inputs.length) (maxWitnessPoints - 1)

/-- A point as stated declarations. -/
def pointDecls (w : List (String × Rat)) : List Decl := w.map fun (n, x) => ⟨n, .stated x⟩

/-- Every output holds over the table, each side evaluated once and charged (`Expr.evalsC`). -/
def allHoldC (limit : Nat) (t : Table) : List Claim → Nat → Option (Bool × Nat)
  | [], u => some (true, u)
  | c :: cs, u => (Expr.evalsC limit t c.exprs u).bind fun (vs, u) =>
      if Claim.ofSides c vs = .decided .holds then allHoldC limit t cs u else some (false, u)

/-- One point, charged first its pass (`passWork`), then its values into a table once: inside the inputs' intervals and
every output holding. -/
def pointHoldsC (limit : Nat) (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) (pass : Nat)
    (w : List (String × Rat)) (u : Nat) : Option (Bool × Nat) :=
  visitC limit (u + pass) fun u =>
    if inputs.all (fun i => match w.lookup i.1 with
      | some x => decide (RoundsTo r i.2 x)
      | none => false) then
      (valueTableC limit (pointDecls w) [] u).bind fun (t, u) => allHoldC limit t outs u
    else some (false, u)

/-- `n` points from point `m`, in order, each built when it is tried; the first witness. -/
def searchC (limit : Nat) (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) (pass : Nat) :
    Nat → Nat → Nat → Option (Option (List (String × Rat)) × Nat)
  | 0, _, u => some (none, u)
  | n + 1, m, u => (pointHoldsC limit r inputs outs pass (witnessPoint r inputs m) u).bind fun (b, u) =>
      if b then some (some (witnessPoint r inputs m), u) else searchC limit r inputs outs pass n (m + 1) u

/-- No point decided it: the points ran out at the limit, or all were tried. -/
def searchUnknown (inputs : List (String × Printed)) : UnknownReason :=
  if maxWitnessPoints < 2 ^ inputs.length + 1 then .limit .witnessPoints else .consistencyInconclusive

/-- The consistency check over the declarations, charged against `limit`; none past it. -/
def consistencyRun (limit : Nat) (ds : List Decl) (r : Rounding) (inputs : List (String × Printed))
    (outs : List Claim) : Option ConsistencyAnswer :=
  let keep := inputs.map Prod.fst
  match consistencyInputFault ds keep, consistencyNameFault ds keep outs with
  | some n, _ => some (.refused (.input n))
  | none, some n => some (.refused (.name n))
  | none, none =>
    let t := inlineTable ds keep
    match outs.mapM (Claim.subst t) with
    | .error .undefined => some .undefined
    | .error .exhausted => some (.unknown (.limit .evaluations))
    | .error _ => some (.unknown (.limit .digits))
    | .ok outs' => match outputNodes outs' with
      | none => some (.unknown .consistencyInconclusive)
      | some nodes =>
        let pass := passWork inputs nodes
        (refuteC limit r inputs outs' 0 pass).bind fun
        | (some (j, es), _) => some (.fails j es)
        | (none, w) => (searchC limit r inputs outs' pass (witnessCount inputs) 0 w).map fun
          | (some pt, _) => .holds pt
          | (none, _) => .unknown (searchUnknown inputs)

theorem enclosesC_some {limit : Nat} {r : Rounding} {inputs : List (String × Printed)} {es : List Expr} {w : Nat}
    {is : List (Rat × Rat)} {w' : Nat} (h : enclosesC limit r inputs es w = some (some is, w')) :
    es.map (enclose r inputs) = is.map some := by
  induction es generalizing w is w' with
  | nil => simp only [enclosesC, Option.some.injEq, Prod.mk.injEq] at h; obtain ⟨⟨⟩, _⟩ := h; rfl
  | cons e es ih =>
    obtain ⟨⟨x, w1⟩, he, h⟩ := Option.bind_eq_some_iff.mp h
    cases x with
    | none => cases h
    | some x =>
      obtain ⟨⟨xs, w2⟩, hes, h⟩ := Option.map_eq_some_iff.mp h
      cases xs with
      | none => cases h
      | some xs =>
        simp only [Prod.mk.injEq, Option.some.injEq] at h; obtain ⟨rfl, -⟩ := h
        simp [encloseC_some limit r inputs e w x w1 he, ih hes]

theorem refuteC_some {limit : Nat} {r : Rounding} {inputs : List (String × Printed)} {cs : List Claim} {j w : Nat}
    {k : Nat} {es : List (Rat × Rat)} {w' : Nat} (h : refuteC limit r inputs cs j w = some (some (k, es), w')) :
    ∃ c ∈ cs, refuteByEnclosure r inputs c = true := by
  induction cs generalizing j w with
  | nil => cases h
  | cons c cs ih =>
    obtain ⟨⟨x, w1⟩, hx, h⟩ := Option.bind_eq_some_iff.mp h
    cases x with
    | none => obtain ⟨d, hd, hc⟩ := ih h; exact ⟨d, by simp [hd], hc⟩
    | some xs =>
      simp only at h; split at h
      · rename_i hm; exact ⟨c, by simp, by rw [refuteByEnclosure, enclosesC_some hx]; exact hm⟩
      · obtain ⟨d, hd, hc⟩ := ih h; exact ⟨d, by simp [hd], hc⟩

theorem pointDecls_names (w : List (String × Rat)) : (pointDecls w).map Decl.name = w.map Prod.fst := by
  simp [pointDecls]

theorem pointDecls_wellFormed (w : List (String × Rat)) (hn : (w.map Prod.fst).Nodup) :
    WellFormed (pointDecls w) := by
  refine ⟨pointDecls_names w ▸ hn, fun i hi e he => ?_, fun d hd q v hq => ?_⟩
  · simp [pointDecls] at he
  · simp only [pointDecls, List.mem_map] at hd; obtain ⟨_, _, rfl⟩ := hd; cases hq

/-- A point's declarations give each name its value. -/
theorem values_pointDecls (w : List (String × Rat)) (hn : (w.map Prod.fst).Nodup) :
    values (pointDecls w) = fun n => w.lookup n := by
  suffices h : ∀ σ : Values, (pointDecls w).foldl (fun σ d n => if n = d.name then d.valueUnder σ else σ n) σ =
      fun n => match w.lookup n with | some x => some x | none => σ n by
    funext n; rw [values, h]; show (match w.lookup n with | some x => some x | none => none) = _
    cases w.lookup n <;> rfl
  induction w with
  | nil => intro σ; rfl
  | cons a w ih =>
    obtain ⟨m, x⟩ := a
    simp only [List.map_cons, List.nodup_cons] at hn
    intro σ; simp only [pointDecls, List.map_cons, List.foldl_cons] at ih ⊢; rw [ih hn.2]; funext n
    by_cases hm : n = m
    · subst hm
      have : w.lookup n = none := by
        cases hl : w.lookup n with
        | none => rfl
        | some p => exact absurd (List.mem_map_of_mem (f := Prod.fst) (lookup_mem hl)) hn.1
      simp [this, List.lookup, Decl.valueUnder]
    · have : (n == m) = false := by simpa using hm
      simp only [List.lookup, this, if_neg hm]

theorem allHoldC_sound {limit : Nat} {t : Table} {cs : List Claim} {u u' : Nat} (hu : u ≤ limit)
    (h : allHoldC limit t cs u = some (true, u')) :
    ∀ c ∈ cs, Claim.ofSides c (c.exprs.map (Expr.evalL t.read)) = .decided .holds := by
  induction cs generalizing u with
  | nil => simp
  | cons c cs ih =>
    obtain ⟨⟨vs, u1⟩, hv, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨rfl, -, hu1⟩ := Expr.evalsC_some limit t c.exprs u vs u1 hu hv
    simp only at h; split at h
    · rename_i hc; intro d hd; rcases List.mem_cons.mp hd with rfl | hd
      · exact hc
      · exact ih hu1 h d hd
    · cases h

theorem pointHoldsC_sound {limit : Nat} {r : Rounding} {inputs : List (String × Printed)} {outs : List Claim}
    {pass : Nat} {w : List (String × Rat)} {u u' : Nat} (hn : (w.map Prod.fst).Nodup)
    (h : pointHoldsC limit r inputs outs pass w u = some (true, u')) : witnessCheck r inputs outs w = true := by
  obtain ⟨hu, h⟩ := visitC_some h
  split at h
  · rename_i hin
    obtain ⟨⟨t, u1⟩, ht, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨rfl, -, hu1⟩ := valueTableC_some limit (pointDecls w) [] _ t u1 hu ht
    have hall := allHoldC_sound hu1 h
    rw [show Table.read (List.foldl _ [] (pointDecls w)) = valuesL (pointDecls w) from valueTable_read _] at hall
    simp only [witnessCheck, hin, Bool.true_and, List.all_eq_true, beq_iff_eq]
    intro c hc
    have hw := pointDecls_wellFormed w hn
    rw [← values_pointDecls w hn, ← Claim.run_decided _ hw c _ (by rw [← Claim.ofSides_eq _ hw c]; exact hall c hc)]
  · cases h

theorem searchC_some {limit : Nat} {r : Rounding} {inputs : List (String × Printed)} {outs : List Claim}
    {pass n m u : Nat} {w : List (String × Rat)} {u' : Nat}
    (h : searchC limit r inputs outs pass n m u = some (some w, u')) :
    (∃ k, w = witnessPoint r inputs k) ∧ ∃ u0 u1, pointHoldsC limit r inputs outs pass w u0 = some (true, u1) := by
  induction n generalizing m u with
  | zero => cases h
  | succ n ih =>
    obtain ⟨⟨b, u1⟩, hb, h⟩ := Option.bind_eq_some_iff.mp h
    simp only at h; split at h
    · simp only [Option.some.injEq, Prod.mk.injEq] at h; obtain ⟨rfl, -⟩ := h
      rename_i hb'; subst hb'; exact ⟨⟨m, rfl⟩, _, _, hb⟩
    · exact ih h

theorem witnessPoint_names (r : Rounding) (inputs : List (String × Printed)) (k : Nat) :
    (witnessPoint r inputs k).map Prod.fst = inputs.map Prod.fst := by
  have he : ∀ m (is : List (String × Printed)), (endpointPoint r m is).map Prod.fst = is.map Prod.fst := by
    intro m is; induction is generalizing m with
    | nil => rfl
    | cons i is ih => simp [endpointPoint, ih]
  cases k with
  | zero => simp [witnessPoint]
  | succ m => exact he m inputs

theorem consistencyInputFault_none {ds : List Decl} {ns : List String} (h : consistencyInputFault ds ns = none) :
    ns.Nodup ∧ ∀ n ∈ ns, n ∈ ds.map Decl.name := by
  induction ns with
  | nil => simp
  | cons n ns ih =>
    simp only [consistencyInputFault] at h; split at h
    · cases h
    · rename_i hn
      simp only [not_or, Bool.not_eq_true', Bool.not_eq_false, List.any_eq_true, Bool.and_eq_true,
        beq_iff_eq] at hn
      obtain ⟨hn1, d, hd, hdn, -⟩ := hn
      obtain ⟨ih1, ih2⟩ := ih h
      refine ⟨List.nodup_cons.mpr ⟨hn1, ih1⟩, fun m hm => ?_⟩
      rcases List.mem_cons.mp hm with rfl | hm
      · exact List.mem_map.mpr ⟨d, hd, hdn⟩
      · exact ih2 m hm

/-- A witness the runner returns proves `Consistent`. -/
theorem consistencyRun_holds (limit : Nat) (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (outs : List Claim) (w : List (String × Rat))
    (hr : consistencyRun limit ds r inputs outs = some (.holds w)) : Consistent ds r inputs outs := by
  cases hin : consistencyInputFault ds (inputs.map Prod.fst) with
  | some n => simp [consistencyRun, hin] at hr
  | none =>
  cases hnm : consistencyNameFault ds (inputs.map Prod.fst) outs with
  | some n => simp [consistencyRun, hin, hnm] at hr
  | none =>
  obtain ⟨hnd, hk⟩ := consistencyInputFault_none hin
  cases hl : outs.mapM (Claim.subst (inlineTable ds (inputs.map Prod.fst))) with
  | error v => cases v <;> simp [consistencyRun, hin, hnm, hl] at hr
  | ok outs' =>
    simp only [consistencyRun, hin, hnm, hl] at hr
    cases hc : outputNodes outs' with
    | none => simp [hc] at hr
    | some nodes =>
    simp only [hc] at hr
    obtain ⟨⟨found, w1⟩, -, hr⟩ := Option.bind_eq_some_iff.mp hr
    cases found with
    | some jes => cases hr
    | none =>
      obtain ⟨⟨pt, w2⟩, hs, hr⟩ := Option.map_eq_some_iff.mp hr
      cases pt with
      | none => simp at hr
      | some pt =>
        simp only [ConsistencyAnswer.holds.injEq] at hr; subst hr
        obtain ⟨⟨k, hk'⟩, _, _, hp⟩ := searchC_some hs
        have hw := pointHoldsC_sound (by rw [hk', witnessPoint_names r inputs k]; exact hnd) hp
        exact consistent_of_witness ds h r inputs (fun i hi => hk _ (List.mem_map_of_mem hi)) outs outs' hl pt hw

/-- A refutation the runner returns proves `¬ Consistent`. -/
theorem consistencyRun_fails (limit : Nat) (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (outs : List Claim) (j : Nat) (es : List (Rat × Rat))
    (hr : consistencyRun limit ds r inputs outs = some (.fails j es)) : ¬ Consistent ds r inputs outs := by
  cases hin : consistencyInputFault ds (inputs.map Prod.fst) with
  | some n => simp [consistencyRun, hin] at hr
  | none =>
  cases hnm : consistencyNameFault ds (inputs.map Prod.fst) outs with
  | some n => simp [consistencyRun, hin, hnm] at hr
  | none =>
  obtain ⟨-, hk⟩ := consistencyInputFault_none hin
  cases hl : outs.mapM (Claim.subst (inlineTable ds (inputs.map Prod.fst))) with
  | error v => cases v <;> simp [consistencyRun, hin, hnm, hl] at hr
  | ok outs' =>
    simp only [consistencyRun, hin, hnm, hl] at hr
    cases hc : outputNodes outs' with
    | none => simp [hc] at hr
    | some nodes =>
    simp only [hc] at hr
    obtain ⟨⟨found, w1⟩, hf, hr⟩ := Option.bind_eq_some_iff.mp hr
    cases found with
    | some jes =>
      obtain ⟨c, hc, hrc⟩ := refuteC_some hf
      exact inconsistent_of_refutation ds h r inputs (fun i hi => hk _ (List.mem_map_of_mem hi)) outs outs' hl c hc
        (.inl hrc)
    | none =>
      obtain ⟨⟨pt, w2⟩, -, hr⟩ := Option.map_eq_some_iff.mp hr
      cases pt <;> simp at hr

end VE.Calc
