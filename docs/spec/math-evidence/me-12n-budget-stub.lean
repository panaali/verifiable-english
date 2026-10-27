import VE.Arith.Examples
import VE.Time.Budget

/-! Spec 12.2's budget addendum (me-12n; DRI decision 2026-10-27 on me-12aa's N1 and its review's F1), type-checked
as a scratch stub against `main`'s `lean/` tree: `cd lean && lake env lean ../docs/spec/math-evidence/me-12n-budget-stub.lean`.
Evidence only, not product code: it does not import `VE.Arith.Bounded` (whose names it restates) and nothing imports
it. Proofs are `sorry` where the build (me-12nb) proves them; the unit counts of spec 13.3 are computed below with
`#guard`, by this file's evaluator, not by product code. -/

namespace VE.Arith
open VE.Numbers

/-! ## The statements of the new 12.2 -/

/-- The size of a value: the bit length of its magnitude, and 1 for 0. -/
def bits (x : Int) : Nat := x.natAbs.log2 + 1

def charge {α : Type} (limit w : Nat) (k : Nat → Option (α × Nat)) : Option (α × Nat) :=
  if limit ≤ w then none else k (w + 1)

/-- A value is charged its size once it is computed: refused (none) when the units would pass the budget. -/
def chargeBits (limit : Nat) (x : Int) (w : Nat) : Option (Int × Nat) :=
  if limit < w + bits x then none else some (x, w + bits x)

/-- A range step charges the size of the value it binds, then visits the condition at that value. -/
def stepB (limit : Nat) (cond : Int → Nat → Option (Bool × Nat)) (i : Int) (w : Nat) : Option (Bool × Nat) :=
  (chargeBits limit i w).bind fun r => cond i r.2

def quantLoop (universal : Bool) (step : Int → Nat → Option (Bool × Nat)) :
    Nat → Int → Nat → Option (Bool × Nat)
  | 0, _, w => some (universal, w)
  | n + 1, i, w => match step i w with
    | none => none
    | some (b, w') => if b = universal then quantLoop universal step n (i + 1) w' else some (!universal, w')

def countLoop (step : Int → Nat → Option (Bool × Nat)) : Nat → Int → Nat → Nat → Option (Int × Nat)
  | 0, _, acc, w => some ((acc : Int), w)
  | n + 1, i, acc, w => match step i w with
    | none => none
    | some (b, w') => countLoop step n (i + 1) (if b then acc + 1 else acc) w'

structure OpEnv where
  funs : String → Option (Nat × (List Int → Nat → Option (Int × Nat)))
  preds : String → Option (Nat × (List Int → Nat → Option (Bool × Nat)))

mutual
def Term.evalB (E : OpEnv) (limit : Nat) (ρ : List Int) : Term → Nat → Option (Int × Nat)
  | .var i, w => charge limit w fun w => (ρ[i]?).bind fun x => chargeBits limit x w
  | .num n, w => charge limit w fun w => chargeBits limit n w
  | .add a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).bind fun r => chargeBits limit (x + r.1) r.2
  | .sub a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).bind fun r => chargeBits limit (x - r.1) r.2
  | .mul a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).bind fun r => chargeBits limit (x * r.1) r.2
  | .call f args, w => charge limit w fun w => match E.funs f with
    | none => none
    | some (n, g) => match Term.evalBs E limit ρ args w with
      | none => none
      | some (xs, w) => if xs.length = n then (g xs w).bind fun r => chargeBits limit r.1 r.2 else none
  | .countFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => (countLoop (stepB limit fun i w => Formula.evalB E limit (i :: ρ) φ w)
          (h - l + 1).toNat l 0 w).bind fun r => chargeBits limit r.1 r.2
def Term.evalBs (E : OpEnv) (limit : Nat) (ρ : List Int) : List Term → Nat → Option (List Int × Nat)
  | [], w => some ([], w)
  | t :: ts, w => match Term.evalB E limit ρ t w with
    | none => none
    | some (x, w) => (Term.evalBs E limit ρ ts w).map fun r => (x :: r.1, r.2)
def Formula.evalB (E : OpEnv) (limit : Nat) (ρ : List Int) : Formula → Nat → Option (Bool × Nat)
  | .eq a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x = r.1), r.2)
  | .lt a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x < r.1), r.2)
  | .le a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x ≤ r.1), r.2)
  | .dvd a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x ∣ r.1), r.2)
  | .call p args, w => charge limit w fun w => match E.preds p with
    | none => none
    | some (n, P) => match Term.evalBs E limit ρ args w with
      | none => none
      | some (xs, w) => if xs.length = n then P xs w else none
  | .not φ, w => charge limit w fun w => (Formula.evalB E limit ρ φ w).map fun r => (!r.1, r.2)
  | .and φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => Formula.evalB E limit ρ ψ w
    | some (false, w) => some (false, w)
  | .or φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => some (true, w)
    | some (false, w) => Formula.evalB E limit ρ ψ w
  | .imp φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => Formula.evalB E limit ρ ψ w
    | some (false, w) => some (true, w)
  | .allNat _, _ => none
  | .exNat _, _ => none
  | .allInt _, _ => none
  | .exInt _, _ => none
  | .allFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => quantLoop true (stepB limit fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
  | .exFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => quantLoop false (stepB limit fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
end

def Defs.opEnv (limit : Nat) (D : Defs) : OpEnv :=
  D.foldl (fun E d => match d with
    | .fn f n body => { E with funs := fun g => if g = f then some (n, fun xs w => Term.evalB E limit xs body w) else E.funs g }
    | .pred p n body => { E with preds := fun q => if q = p then some (n, fun xs w => Formula.evalB E limit xs body w) else E.preds q })
    ⟨fun _ => none, fun _ => none⟩

def maxSteps : Nat := VE.Time.maxEvaluations

/-- The value and the units spent, or none (UNKNOWN). -/
def decideBounded (D : Defs) (limit : Nat) (φ : Formula) : Option (Bool × Nat) :=
  Formula.evalB (D.opEnv limit) limit [] φ 0

/-! Unchanged statements, restated over the new `charge`: their text is draft 4's. -/

theorem decideBounded_sound (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : D.Means φ ↔ b = true := sorry
theorem decideBounded_mono (D : Defs) (φ : Formula) (limit limit' : Nat) (r : Bool × Nat)
    (h : decideBounded D limit φ = some r) (hl : limit ≤ limit') : decideBounded D limit' φ = some r := sorry
theorem decideBounded_work (D : Defs) (φ : Formula) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : w ≤ limit := sorry
theorem decideBounded_complete (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (hb : φ.Bounded D = true) : ∃ limit r, decideBounded D limit φ = some r := sorry
/-- me-12ab's work bound (in `Bounded.lean`, not in draft 4's text): unchanged. -/
theorem decideBounded_covered (D : Defs) (hD : D.WellFormed = true) (φ : Formula) (hφ : φ.Scoped D 0 = true)
    (hb : φ.Bounded D = true) : ∃ b W, ∀ limit, W ≤ limit → decideBounded D limit φ = some (b, W) := sorry

/-! New statements: the size bound, proved here (it needs no induction: every term clause ends in `chargeBits`), and
the bounds on the one value computed before its refusal. -/

theorem chargeBits_some {limit w : Nat} {x y : Int} {w' : Nat} (h : chargeBits limit x w = some (y, w')) :
    y = x ∧ w' = w + bits x ∧ w + bits x ≤ limit := by
  unfold chargeBits at h; split at h
  · simp at h
  · simp only [Option.some.injEq, Prod.mk.injEq] at h; omega

theorem chargeBits_bits {limit w : Nat} {x y : Int} {w' : Nat} (h : chargeBits limit x w = some (y, w')) :
    bits y ≤ limit ∧ w' ≤ limit := by
  obtain ⟨rfl, rfl, h⟩ := chargeBits_some h; omega

/-- Every value a term yields within budget `limit` has size at most `limit`, in any environment, and the units after
it are within the budget. -/
theorem Term.evalB_bits (E : OpEnv) (limit : Nat) (ρ : List Int) (t : Term) (w : Nat) (x : Int) (w' : Nat)
    (h : Term.evalB E limit ρ t w = some (x, w')) : bits x ≤ limit ∧ w' ≤ limit := by
  cases t <;> simp only [Term.evalB, charge] at h <;>
    repeat' (first | (split at h) | (rw [Option.bind_eq_some_iff] at h; obtain ⟨_, _, h⟩ := h))
  all_goals first | (simp at h; done) | exact chargeBits_bits h

theorem log2_le_of_lt {n k : Nat} (h : n < 2 ^ (k + 1)) : n.log2 ≤ k := by
  by_cases hn : n = 0
  · subst hn; simp [Nat.log2_zero]
  · exact Nat.lt_succ_iff.1 ((Nat.log2_lt hn).2 h)

theorem bits_natAbs_le {x : Int} {n k : Nat} (hx : x.natAbs ≤ n) (h : n < 2 ^ (k + 1)) : bits x ≤ k + 1 := by
  have := log2_le_of_lt (n := x.natAbs) (k := k) (by omega)
  unfold bits; omega

theorem bits_add_le (x y : Int) : bits (x + y) ≤ max (bits x) (bits y) + 1 := by
  have hx := Nat.lt_log2_self (n := x.natAbs)
  have hy := Nat.lt_log2_self (n := y.natAbs)
  have hm1 : 2 ^ (x.natAbs.log2 + 1) ≤ 2 ^ (max (bits x) (bits y)) :=
    Nat.pow_le_pow_right (by omega) (by simp only [bits]; omega)
  have hm2 : 2 ^ (y.natAbs.log2 + 1) ≤ 2 ^ (max (bits x) (bits y)) :=
    Nat.pow_le_pow_right (by omega) (by simp only [bits]; omega)
  exact bits_natAbs_le (Int.natAbs_add_le x y) (by rw [Nat.pow_succ]; omega)

theorem bits_sub_le (x y : Int) : bits (x - y) ≤ max (bits x) (bits y) + 1 := by
  have := bits_add_le x (-y)
  simpa [Int.sub_eq_add_neg, bits, Int.natAbs_neg] using this

theorem bits_mul_le (x y : Int) : bits (x * y) ≤ bits x + bits y := by
  have hx := Nat.lt_log2_self (n := x.natAbs)
  have hy := Nat.lt_log2_self (n := y.natAbs)
  have := bits_natAbs_le (k := x.natAbs.log2 + y.natAbs.log2 + 1) (Nat.le_of_eq (Int.natAbs_mul x y))
    (calc x.natAbs * y.natAbs < 2 ^ (x.natAbs.log2 + 1) * 2 ^ (y.natAbs.log2 + 1) := Nat.mul_lt_mul'' hx hy
      _ = 2 ^ (x.natAbs.log2 + y.natAbs.log2 + 1 + 1) := by rw [← Nat.pow_add]; congr 1; omega)
  unfold bits at this ⊢; omega

def arithOutcome (D : Defs) (limit : Nat) (φ : Formula) : Outcome :=
  if φ.Bounded D then
    match decideBounded D limit φ with
    | some (true, _) => .decided .holds
    | some (false, _) => .decided .fails
    | none => .unknown (.limit .evaluations)
  else .unknown .unboundedStatement

end VE.Arith

/-! ## Spec 13.3's units under the new charge (*by hand*: this file's evaluator, not product code) -/

namespace VE.Arith.Examples
open VE.Arith

/-! Hand checks, each derived clause by clause in 13.3: M-5, a predicate call, an empty count, `pos 3`. -/
#guard decideBounded primeDefs maxSteps (.call "prime" [lit 7]) = some (true, 85)
#guard decideBounded [] maxSteps (.eq (.countFromTo (lit 1) (lit 0) (.eq (lit 0) (lit 0))) (lit 0)) = some (true, 9)
#guard decideBounded chain maxSteps (.call "pos" [lit 3]) = some (true, 10)

/-! M-1, M-1b (13.2's 17,010 and 17,011 are both unknown now), M-4x, M-2, M-5: under, at and over each boundary. -/
#guard [337734, 337735, 337736].map (decideBounded primeDefs · (m1 161)) = [none, some (true, 337735), some (true, 337735)]
#guard [1000, 17010, 17011].map (decideBounded primeDefs · (m1 161)) = [none, none, none]
#guard [7419, 7420, 7421].map (decideBounded primeDefs · m2) = [none, some (true, 7420), some (true, 7420)]
#guard [32, 33, 34].map (decideBounded primeDefs · m5) = [none, some (false, 33), some (false, 33)]

/-! M-4 and M-4b: the instances, and each pair's completing bound N at `maxSteps` with the units N + 1 needs. -/
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 10)) = some (false, 890)
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 11)) = some (true, 1072)
#guard ([(1, 2), (3, 17), (4, 29), (5, 41)] : List (Int × Int)).map (fun (k, T) =>
    [T - 1, T, T + 1].map fun x => (decideBounded countDefs maxSteps (atLeast k (.num x))).map (·.1)) =
  List.replicate 4 [some false, some true, some true]
#guard ([(2, 11, 87, 973791, 1004183), (1, 2, 87, 977913, 1008304), (3, 17, 88, 995531, 1027872),
    (4, 29, 89, 989822, 1022334), (5, 41, 91, 981126, 1013976)] : List (Int × Int × Int × Nat × Nat)).all
  fun (k, T, N, u, u') => decideBounded countDefs maxSteps (m4 k T N) == some (true, u) &&
    decideBounded countDefs maxSteps (m4 k T (N + 1)) == none && decideBounded countDefs u' (m4 k T (N + 1)) == some (true, u')
#guard [200, 248, 249, 1000].all fun N => decideBounded countDefs maxSteps (m4 2 11 N) == none
#guard decideBounded countDefs 10000000 (m4 2 11 200) = some (true, 9694873)

/-! B-1 to B-4 (13.3): N1's pin and doubling chain, F1's squaring chain, and a reused large value. -/
def dbl (k : Nat) : Defs :=
  .fn "f0" 0 (lit 1) :: (List.range k).map fun i => .fn s!"f{i + 1}" 0 (.add (.call s!"f{i}" []) (.call s!"f{i}" []))
def dblx (k : Nat) : Defs :=
  .fn "f0" 1 (.var 0) :: (List.range k).map fun i =>
    .fn s!"f{i + 1}" 1 (.add (.call s!"f{i}" [.var 0]) (.call s!"f{i}" [.var 0]))
def sqChain (k : Nat) : Defs :=
  .fn "sq" 1 (.mul (.var 0) (.var 0)) :: .fn "g0" 0 (lit 2) ::
    (List.range k).map fun i => .fn s!"g{i + 1}" 0 (.call "sq" [.call s!"g{i}" []])
def reuse : Defs := sqChain 16 ++ [.fn "r" 2 (.countFromTo (lit 1) (lit 999000) (.dvd (.var 1) (.var 2)))]
def reuseStmt : Formula := .le (lit 0) (.call "r" [.add (.call "g15" []) (lit 1), .call "g16" []])
#guard (dbl 24).WellFormed && (sqChain 31).WellFormed && reuse.WellFormed &&
  (Formula.lt (lit 0) (.call "f24" [])).Bounded (dbl 24) && (Formula.lt (lit 0) (.call "g31" [])).Bounded (sqChain 31) &&
  reuseStmt.Bounded reuse && reuseStmt.Scoped reuse 0
#guard decideBounded (dbl 2) maxSteps (.eq (lit 4) (.call "f2" [])) = some (true, 41)
#guard [1, 1000, 12272, 12273, 12274].map (decideBounded (dbl 10) · (.eq (lit 1024) (.call "f10" []))) =
  [none, none, none, some (true, 12273), some (true, 12273)]
#guard decideBounded (dbl 24) maxSteps (.lt (lit 0) (.call "f24" [])) = none
#guard (dblx 24).WellFormed && decideBounded (dblx 2) maxSteps (.eq (lit 4) (.call "f2" [lit 1])) = some (true, 55) &&
  decideBounded (dblx 24) maxSteps (.lt (lit 0) (.call "f24" [lit 1])) == none
#guard decideBounded (sqChain 3) maxSteps (.lt (lit 0) (.call "g3" [])) = some (true, 95)
#guard decideBounded (sqChain 16) maxSteps (.lt (lit 0) (.call "g16" [])) = some (true, 524449)
#guard [maxSteps, 1048746, 1048747].map (decideBounded (sqChain 17) · (.lt (lit 0) (.call "g17" []))) =
  [none, none, some (true, 1048747)]
#guard decideBounded (sqChain 31) maxSteps (.lt (lit 0) (.call "g31" [])) = none
#guard decideBounded reuse maxSteps reuseStmt = none

end VE.Arith.Examples
