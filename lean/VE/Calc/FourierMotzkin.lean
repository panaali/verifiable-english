import VE.Calc.Linear

/-! Fourier-Motzkin elimination with multiplier tracking (plan ME-5). Nothing here is trusted: a refutation is
replayed by `Farkas.check`, and a point is checked by evaluation (`Derive.lean`). -/

namespace VE.Calc.FM

def maxFacts : Nat := 64
def maxUnknowns : Nat := 16
def maxSteps : Nat := 10000

/-- A derivation's input is within the limits of spec 5: at most `maxFacts` facts, and at most `maxUnknowns` unknowns
counting `names` (the square links') with the facts'. Checked once, on the derivation's input. -/
def admits (fs : List QFact) (names : List String) : Bool :=
  fs.length ≤ maxFacts && (firstAppearance (unknowns fs ++ names)).length ≤ maxUnknowns

/-- A search step within the combinations left for the whole derivation (the state). Running out throws, so it ends
the derivation as `limit .derivationSteps` and no search can turn it into "nothing found". -/
abbrev Search := StateT Nat (Except Unit)

/-- A derived fact with its weights on the input facts. -/
structure Row where
  fact : QFact
  weights : List Rat

def Row.trivial (r : Row) : Bool :=
  r.fact.form.coeffs.isEmpty && (decide (0 < r.fact.form.const) || (r.fact.form.const == 0 && !r.fact.strict))

def Row.contradiction (r : Row) : Bool :=
  r.fact.form.coeffs.isEmpty && (decide (r.fact.form.const < 0) || (r.fact.form.const == 0 && r.fact.strict))

/-- `p` has a positive and `n` a negative coefficient on `x`; the positive combination cancels `x`. -/
def Row.combine (x : String) (p n : Row) : Row :=
  let cp := p.fact.form.coeffOf x
  let cn := n.fact.form.coeffOf x
  ⟨⟨(QLin.add (p.fact.form.scale (-cn)) (n.fact.form.scale cp)).norm, p.fact.strict || n.fact.strict⟩,
    List.zipWith (fun a b => -cn * a + cp * b) p.weights n.weights⟩

/-- Eliminates `x`, charging its combinations to the budget before any is built; throws when they are more than
the budget left. -/
def eliminate (x : String) (rows : List Row) : Search (List Row) := do
  let pos := rows.filter fun r => decide (0 < r.fact.form.coeffOf x)
  let neg := rows.filter fun r => decide (r.fact.form.coeffOf x < 0)
  let zero := rows.filter fun r => r.fact.form.coeffOf x == 0
  let left ← get
  if pos.length * neg.length > left then throw ()
  set (left - pos.length * neg.length)
  pure ((zero ++ pos.flatMap fun p => neg.map (Row.combine x p)).filter (!·.trivial))

inductive Result where
  | refuted (weights : List Rat)
  | point (κ : List (String × Rat))
  deriving Repr

/-- The value of `x` meeting every row, given the later unknowns' values in `κ`: a bound itself when it meets them
all, else between the tightest bounds. -/
def pick (x : String) (rows : List Row) (κ : List (String × Rat)) : Rat :=
  let val := fun v n => if n = x then v else (κ.lookup n).getD 0
  let bounds := rows.filterMap fun r =>
    let c := r.fact.form.coeffOf x
    if c == 0 then none else some (c, -(r.fact.form.eval (val 0)) / c)
  let fits := fun v => rows.all fun r => decide (r.fact.Holds (val v))
  match (bounds.map (·.2)).find? fits, ((bounds.filter (0 < ·.1)).map (·.2)).max?,
      ((bounds.filter (·.1 < 0)).map (·.2)).min? with
  | some v, _, _ => v
  | none, some l, some h => (l + h) / 2
  | none, some l, none => l + 1
  | none, none, some h => h - 1
  | none, none, none => 0

/-- The tightest of a list of bounds, strict when a bound equal to it is strict. -/
def tightest (better : Rat → Rat → Bool) (bs : List (Rat × Bool)) : Option (Rat × Bool) :=
  bs.foldl (fun acc (b, s) => match acc with
    | none => some (b, s)
    | some (a, t) => if better b a then some (b, s) else if b == a then some (a, t || s) else some (a, t)) none

/-- A row at `x`: its coefficient on `x`, its value at `x = 0`, and whether it is strict. -/
abbrev Entry := Rat × Rat × Bool

def Entry.holds (v : Rat) (p : Entry) : Bool :=
  if p.2.2 then decide (0 < p.2.1 + p.1 * v) else decide (0 ≤ p.2.1 + p.1 * v)

def lowOk (v : Rat) : Option (Rat × Bool) → Bool
  | none => true
  | some (l, s) => if s then decide (l < v) else decide (l ≤ v)

def highOk (v : Rat) : Option (Rat × Bool) → Bool
  | none => true
  | some (h, s) => if s then decide (v < h) else decide (v ≤ h)

def zeroOk (cs : List Entry) : Bool := cs.all fun (c, r, s) => c != 0 || (if s then decide (0 < r) else decide (0 ≤ r))
def lows (cs : List Entry) : List (Rat × Bool) := cs.filterMap fun (c, r, s) => if 0 < c then some (-r / c, s) else none
def highs (cs : List Entry) : List (Rat × Bool) := cs.filterMap fun (c, r, s) => if c < 0 then some (-r / c, s) else none
def candidates (cs : List Entry) : List Rat := cs.filterMap fun (c, r, _) => if c == 0 then none else some (-r / c)

/-- 5's `FM.pick` in two passes: a row holds at `x = v` exactly when `v` is within its bound, so a candidate fits
exactly when it is within the tightest bounds and every row without `x` holds; the candidates are 5's, in its order. -/
def pickOnce (x : String) (rows : List Row) (κ : List (String × Rat)) : Rat :=
  let val := fun n => if n = x then (0 : Rat) else (κ.lookup n).getD 0
  let cs : List Entry := rows.map fun r => (r.fact.form.coeffOf x, r.fact.form.eval val, r.fact.strict)
  let zero := zeroOk cs
  let lo := tightest (fun b a => decide (a < b)) (lows cs)
  let hi := tightest (fun b a => decide (b < a)) (highs cs)
  match (candidates cs).find? (fun v => zero && lowOk v lo && highOk v hi), lo, hi with
  | some v, _, _ => v
  | none, some (l, _), some (h, _) => (l + h) / 2
  | none, some (l, _), none => l + 1
  | none, none, some (h, _) => h - 1
  | none, none, none => 0

theorem tightest_all (better : Rat → Rat → Bool) (ok : Rat × Bool → Bool) (bs : List (Rat × Bool))
    (acc : Option (Rat × Bool))
    (hs : ∀ a t b s, (if better b a then ok (b, s) else if b == a then ok (a, t || s) else ok (a, t)) =
      (ok (a, t) && ok (b, s))) :
    (acc.all ok && bs.all ok) = (bs.foldl (fun acc (b, s) => match acc with
      | none => some (b, s)
      | some (a, t) => if better b a then some (b, s) else if b == a then some (a, t || s) else some (a, t)) acc).all ok := by
  induction bs generalizing acc with
  | nil => simp
  | cons p bs ih =>
    obtain ⟨b, s⟩ := p
    simp only [List.foldl_cons, ← ih, List.all_cons]
    cases acc with
    | none => simp
    | some q =>
      obtain ⟨a, t⟩ := q
      have := hs a t b s
      simp only [Option.all_some, ← Bool.and_assoc, ← this]
      by_cases h1 : better b a = true <;> by_cases h2 : (b == a) = true <;> simp [h1, h2]

theorem tightest_first (better : Rat → Rat → Bool) (m : Rat → Rat → Rat) (bs : List (Rat × Bool)) (a : Rat)
    (t : Bool) (hm : ∀ a b, (if better b a then b else if b == a then a else a) = m a b) :
    (bs.foldl (fun acc (b, s) => match acc with
      | none => some (b, s)
      | some (a, t) => if better b a then some (b, s) else if b == a then some (a, t || s) else some (a, t)) (some (a, t))).map
      (·.1) = some ((bs.map (·.1)).foldl m a) := by
  induction bs generalizing a t with
  | nil => rfl
  | cons p bs ih =>
    obtain ⟨b, s⟩ := p
    simp only [List.foldl_cons, List.map_cons, ← hm a b]
    by_cases h1 : better b a = true
    · simp only [h1, if_true]; exact ih b s
    · by_cases h2 : (b == a) = true
      · simp only [h1, h2, if_true, Bool.false_eq_true, if_false]; exact ih a _
      · simp only [h1, h2, Bool.false_eq_true, if_false]; exact ih a t

theorem scaled (a b : Rat) (ha : 0 < a) : (0 < a * b ↔ 0 < b) ∧ (0 ≤ a * b ↔ 0 ≤ b) := by
  refine ⟨Rat.mul_pos_iff_of_pos_left ha, ?_⟩
  have := Rat.mul_neg_iff_of_pos_left (b := b) ha
  rw [← Rat.not_lt, ← Rat.not_lt, this]

theorem pos_bound (r c v : Rat) (hc : 0 < c) : (0 < r + c * v ↔ -r / c < v) ∧ (0 ≤ r + c * v ↔ -r / c ≤ v) := by
  have hb : -r / c * c = -r := Rat.div_mul_cancel (by grind)
  generalize -r / c = b at hb ⊢
  have he : r + c * v = c * (v - b) := by grind
  rw [he]
  obtain ⟨h1, h2⟩ := scaled c (v - b) hc
  rw [h1, h2]; constructor <;> constructor <;> grind

theorem neg_bound (r c v : Rat) (hc : c < 0) : (0 < r + c * v ↔ v < -r / c) ∧ (0 ≤ r + c * v ↔ v ≤ -r / c) := by
  have hb : -r / c * c = -r := Rat.div_mul_cancel (by grind)
  generalize -r / c = b at hb ⊢
  have he : r + c * v = (-c) * (b - v) := by grind
  rw [he]
  obtain ⟨h1, h2⟩ := scaled (-c) (b - v) (by grind)
  rw [h1, h2]; constructor <;> constructor <;> grind

def lowOk' (v : Rat) (q : Rat × Bool) : Bool := lowOk v (some q)
def highOk' (v : Rat) (q : Rat × Bool) : Bool := highOk v (some q)

/-- One pass over the entries decides every row at `v`: the rows without `x`, then the two tightest bounds. -/
theorem entries_all (cs : List Entry) (v : Rat) :
    cs.all (Entry.holds v) = (zeroOk cs && (lows cs).all (lowOk' v) && (highs cs).all (highOk' v)) := by
  induction cs with
  | nil => rfl
  | cons p cs ih =>
    obtain ⟨c, r, s⟩ := p
    have hl : lows ((c, r, s) :: cs) = (if 0 < c then [(-r / c, s)] else []) ++ lows cs := by
      by_cases h : 0 < c <;> simp [lows, List.filterMap_cons, h]
    have hh : highs ((c, r, s) :: cs) = (if c < 0 then [(-r / c, s)] else []) ++ highs cs := by
      by_cases h : c < 0 <;> simp [highs, List.filterMap_cons, h]
    have hz : zeroOk ((c, r, s) :: cs) = ((c != 0 || (if s then decide (0 < r) else decide (0 ≤ r))) && zeroOk cs) := rfl
    rw [hl, hh, hz, List.all_cons, ih]
    have hpart : Entry.holds v (c, r, s) = ((c != 0 || (if s then decide (0 < r) else decide (0 ≤ r))) &&
        ((if 0 < c then [(-r / c, s)] else []).all (lowOk' v)) &&
        ((if c < 0 then [(-r / c, s)] else []).all (highOk' v))) := by
      simp only [Entry.holds, lowOk', highOk', lowOk, highOk]
      rcases (by grind : c < 0 ∨ c = 0 ∨ 0 < c) with h | h | h
      · obtain ⟨h1, h2⟩ := neg_bound r c v h
        have h0 : c ≠ 0 := by grind
        have h3 : ¬ 0 < c := by grind
        cases s <;> simp [h, h0, h3, h1, h2, lowOk', highOk', lowOk, highOk]
      · subst h; cases s <;> simp [Rat.zero_mul, Rat.add_zero]
      · obtain ⟨h1, h2⟩ := pos_bound r c v h
        have h0 : c ≠ 0 := by grind
        have h3 : ¬ c < 0 := by grind
        cases s <;> simp [h, h0, h3, h1, h2, lowOk', highOk', lowOk, highOk]
    rw [hpart]
    simp only [List.all_append]
    cases (c != 0 || (if s then decide (0 < r) else decide (0 ≤ r))) <;>
      cases (if 0 < c then [(-r / c, s)] else []).all (lowOk' v) <;>
      cases (if c < 0 then [(-r / c, s)] else []).all (highOk' v) <;> simp

theorem low_step (v a : Rat) (t : Bool) (b : Rat) (s : Bool) :
    (if decide (a < b) then lowOk' v (b, s) else if b == a then lowOk' v (a, t || s) else lowOk' v (a, t)) =
      (lowOk' v (a, t) && lowOk' v (b, s)) := by
  simp only [lowOk', lowOk]
  by_cases h : a < b
  · cases s <;> cases t <;> simp only [h, decide_true, if_true, Bool.true_eq, Bool.false_eq_true, if_false,
      decide_eq_true_eq, Bool.and_eq_true, decide_eq_decide, Bool.true_and, Bool.and_true, Bool.decide_and,
      Bool.and_iff_right_iff_imp] <;> grind
  · by_cases hb : b = a
    · subst hb; cases s <;> cases t <;> simp <;> exact Rat.le_of_lt
    · have hb' : ¬ (b == a) = true := by simpa using hb
      simp only [h, decide_false, Bool.false_eq_true, if_false, hb']
      cases s <;> cases t <;> simp only [Bool.true_eq, Bool.false_eq_true, if_true, if_false,
        Bool.and_iff_left_iff_imp, decide_eq_true_eq] <;> grind

theorem high_step (v a : Rat) (t : Bool) (b : Rat) (s : Bool) :
    (if decide (b < a) then highOk' v (b, s) else if b == a then highOk' v (a, t || s) else highOk' v (a, t)) =
      (highOk' v (a, t) && highOk' v (b, s)) := by
  simp only [highOk', highOk]
  by_cases h : b < a
  · cases s <;> cases t <;> simp only [h, decide_true, if_true, Bool.true_eq, Bool.false_eq_true, if_false,
      decide_eq_true_eq, Bool.and_eq_true, decide_eq_decide, Bool.true_and, Bool.and_true, Bool.decide_and,
      Bool.and_iff_right_iff_imp] <;> grind
  · by_cases hb : b = a
    · subst hb; cases s <;> cases t <;> simp <;> exact Rat.le_of_lt
    · have hb' : ¬ (b == a) = true := by simpa using hb
      simp only [h, decide_false, Bool.false_eq_true, if_false, hb']
      cases s <;> cases t <;> simp only [Bool.true_eq, Bool.false_eq_true, if_true, if_false,
        Bool.and_iff_left_iff_imp, decide_eq_true_eq] <;> grind

theorem low_all (bs : List (Rat × Bool)) (v : Rat) :
    bs.all (lowOk' v) = lowOk v (tightest (fun b a => decide (a < b)) bs) := by
  have := tightest_all (fun b a => decide (a < b)) (lowOk' v) bs none (low_step v)
  simp only [Option.all_none, Bool.true_and] at this
  rw [this, tightest]
  generalize List.foldl _ _ bs = r
  cases r <;> rfl

theorem high_all (bs : List (Rat × Bool)) (v : Rat) :
    bs.all (highOk' v) = highOk v (tightest (fun b a => decide (b < a)) bs) := by
  have := tightest_all (fun b a => decide (b < a)) (highOk' v) bs none (high_step v)
  simp only [Option.all_none, Bool.true_and] at this
  rw [this, tightest]
  generalize List.foldl _ _ bs = r
  cases r <;> rfl

theorem low_max (bs : List (Rat × Bool)) :
    (tightest (fun b a => decide (a < b)) bs).map (·.1) = (bs.map (·.1)).max? := by
  cases bs with
  | nil => rfl
  | cons p bs =>
    obtain ⟨b, s⟩ := p
    simp only [List.map_cons, List.max?_cons']
    refine tightest_first (fun b a => decide (a < b)) max bs b s fun a b => ?_
    rw [show max a b = if a ≤ b then b else a from rfl]
    simp only [decide_eq_true_eq]
    by_cases h : a < b
    · simp [h, Rat.le_of_lt h]
    · by_cases hb : a ≤ b
      · have : a = b := by grind
        subst this; simp
      · simp [h, hb]

theorem high_min (bs : List (Rat × Bool)) :
    (tightest (fun b a => decide (b < a)) bs).map (·.1) = (bs.map (·.1)).min? := by
  cases bs with
  | nil => rfl
  | cons p bs =>
    obtain ⟨b, s⟩ := p
    simp only [List.map_cons, List.min?_cons']
    refine tightest_first (fun b a => decide (b < a)) min bs b s fun a b => ?_
    rw [show min a b = if a ≤ b then a else b from rfl]
    simp only [decide_eq_true_eq]
    by_cases h : b < a
    · have : ¬ a ≤ b := by grind
      simp [h, this]
    · by_cases hb : a ≤ b
      · simp [h, hb]
      · grind

def boundsOf (cs : List Entry) : List (Rat × Rat) :=
  cs.filterMap fun (c, r, _) => if c == 0 then none else some (c, -r / c)

theorem boundsOf_parts (cs : List Entry) :
    (boundsOf cs).map (·.2) = candidates cs ∧
      ((boundsOf cs).filter (0 < ·.1)).map (·.2) = (lows cs).map (·.1) ∧
      ((boundsOf cs).filter (·.1 < 0)).map (·.2) = (highs cs).map (·.1) := by
  induction cs with
  | nil => simp [boundsOf, candidates, lows, highs]
  | cons p cs ih =>
    obtain ⟨c, r, s⟩ := p
    obtain ⟨h1, h2, h3⟩ := ih
    simp only [boundsOf, candidates, lows, highs, List.filterMap_cons, beq_iff_eq] at h1 h2 h3 ⊢
    rcases (by grind : c < 0 ∨ c = 0 ∨ 0 < c) with h | h | h
    · have h0 : c ≠ 0 := by grind
      have h3' : ¬ 0 < c := by grind
      simp [h, h0, h3', h1, h2, h3]
    · subst h; simp [Rat.lt_irrefl, h1, h2, h3]
    · have h0 : c ≠ 0 := by grind
      have h3' : ¬ c < 0 := by grind
      simp [h, h0, h3', h1, h2, h3]

theorem eval_update (l : List (String × Rat)) (x : String) (f : String → Rat) (v : Rat) :
    (l.map fun p => p.2 * (if p.1 = x then v else f p.1)).sum =
      (l.map fun p => p.2 * (if p.1 = x then 0 else f p.1)).sum + ((l.filter (·.1 == x)).map (·.2)).sum * v := by
  induction l with
  | nil => simp [Rat.zero_mul, Rat.add_zero]
  | cons p l ih => by_cases h : p.1 = x <;> simp [h, ih] <;> grind

theorem row_holds (x : String) (f : String → Rat) (v : Rat) (r : Row) :
    decide (r.fact.Holds fun n => if n = x then v else f n) =
      Entry.holds v (r.fact.form.coeffOf x, r.fact.form.eval (fun n => if n = x then 0 else f n), r.fact.strict) := by
  have he : r.fact.form.eval (fun n => if n = x then v else f n) =
      r.fact.form.eval (fun n => if n = x then 0 else f n) + r.fact.form.coeffOf x * v := by
    simp only [QLin.eval, eval_update _ x f v, QLin.coeffOf]; grind
  simp only [QFact.Holds, Entry.holds, he]
  split <;> rfl

/-- `pickOnce` is 5's `FM.pick`: the same candidates, the same fit, the same tightest bounds. -/
theorem pickOnce_eq (x : String) (rows : List FM.Row) (κ : List (String × Rat)) :
    pickOnce x rows κ = FM.pick x rows κ := by
  have key : ∀ (A : Option Rat) (lo hi : Option (Rat × Bool)),
      (match A, lo, hi with
        | some v, _, _ => v
        | none, some (l, _), some (h, _) => (l + h) / 2
        | none, some (l, _), none => l + 1
        | none, none, some (h, _) => h - 1
        | none, none, none => 0) =
      (match A, lo.map (·.1), hi.map (·.1) with
        | some v, _, _ => v
        | none, some l, some h => (l + h) / 2
        | none, some l, none => l + 1
        | none, none, some h => h - 1
        | none, none, none => 0) := by
    intro A lo hi
    rcases A with _ | a <;> rcases lo with _ | ⟨l, _⟩ <;> rcases hi with _ | ⟨h, _⟩ <;> rfl
  obtain ⟨f, hf⟩ : ∃ f : String → Rat, f = fun n => (κ.lookup n).getD 0 := ⟨_, rfl⟩
  obtain ⟨cs, hcs⟩ : ∃ cs : List Entry, cs = rows.map fun r =>
      (r.fact.form.coeffOf x, r.fact.form.eval (fun n => if n = x then 0 else f n), r.fact.strict) := ⟨_, rfl⟩
  obtain ⟨h1, h2, h3⟩ := boundsOf_parts cs
  have hb : (rows.filterMap fun r =>
      let c := r.fact.form.coeffOf x
      if c == 0 then none else some (c, -(r.fact.form.eval (fun n => if n = x then 0 else f n)) / c)) = boundsOf cs := by
    simp only [boundsOf, hcs, List.filterMap_map]; rfl
  have hfit : (fun v => zeroOk cs && lowOk v (tightest (fun b a => decide (a < b)) (lows cs)) &&
        highOk v (tightest (fun b a => decide (b < a)) (highs cs))) =
      fun v => rows.all fun r => decide (r.fact.Holds fun n => if n = x then v else f n) := by
    funext v
    rw [← low_all, ← high_all, ← entries_all]
    simp only [hcs, List.all_map]
    exact congrArg (fun g => rows.all g) (funext fun r => (row_holds x f v r).symm)
  have hL := low_max (lows cs)
  have hH := high_min (highs cs)
  rw [← h2] at hL
  rw [← h3] at hH
  subst hf
  simp only [pickOnce, pick, ← hcs]
  refine (key _ _ _).trans ?_
  rw [hL, hH, ← h1, ← hb]
  simp only [hfit]

/-- Back-substitution through the stages, last eliminated unknown first. -/
def backSubstitute : List (String × List Row) → List (String × Rat) → List (String × Rat)
  | [], κ => κ
  | (x, rows) :: rest, κ => backSubstitute rest ((x, pick x rows κ) :: κ)

/-- Eliminates `xs` in order; the stages are recorded, latest first. -/
def run : List String → List Row → List (String × List Row) → Search (List Row × List (String × List Row))
  | [], rows, stages => pure (rows, stages)
  | x :: xs, rows, stages => do run xs (← eliminate x rows) ((x, rows) :: stages)

def inputRows (fs : List QFact) : List Row :=
  (List.range fs.length).zip fs |>.map fun (i, f) =>
    ⟨⟨f.form.norm, f.strict⟩, (List.range fs.length).map fun j => if i = j then 1 else 0⟩

/-- Searches a refutation of `fs`, or a point satisfying all of them. -/
def search (fs : List QFact) : Search Result := do
  let (rows, stages) ← run (unknowns fs) (inputRows fs) []
  match rows.find? Row.contradiction with
  | some r => pure (.refuted r.weights)
  | none => pure (.point (backSubstitute stages []))

/-- The least upper bound on `x` that the facts imply, with its strictness: every other unknown eliminated. -/
def upperBound (fs : List QFact) (x : String) : Search (Option (Rat × Bool)) := do
  let (rows, _) ← run ((unknowns fs).filter (· != x)) (inputRows fs) []
  let ups := rows.filterMap fun r =>
    let c := r.fact.form.coeffOf x
    if decide (c < 0) && r.fact.form.coeffs.all (·.1 == x) then some (r.fact.form.const / -c, r.fact.strict)
    else none
  pure <| ups.foldl (fun best u => match best with
    | none => some u
    | some b => if u.1 < b.1 || (u.1 == b.1 && u.2) then some u else some b) none

end VE.Calc.FM
