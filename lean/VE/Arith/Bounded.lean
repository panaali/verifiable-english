import VE.Arith.Holds
import VE.Arith.Defs
import VE.Time.Budget

/-! The budget (spec 12.2, debate F5): one unit per formula-node visit, as W6's `VE.Time.evalB`; term nodes are
free, a count is charged through its condition, a predicate call is one visit plus its body's. `decideBounded` is
this evaluator from no work spent; when it completes, its answer is the meaning's (`decideBounded_sound`), so the
budget only turns an answer into unknown. -/

namespace VE.Arith
open VE.Numbers

def charge {α : Type} (limit w : Nat) (k : Nat → Option (α × Nat)) : Option (α × Nat) :=
  if limit ≤ w then none else k (w + 1)

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
  | .var i, w => (ρ[i]?).map fun x => (x, w)
  | .num n, w => some (n, w)
  | .add a b, w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (x + r.1, r.2)
  | .sub a b, w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (x - r.1, r.2)
  | .mul a b, w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (x * r.1, r.2)
  | .call f args, w => match E.funs f with
    | none => none
    | some (n, g) => match Term.evalBs E limit ρ args w with
      | none => none
      | some (xs, w) => if xs.length = n then g xs w else none
  | .countFromTo lo hi φ, w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => countLoop (fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l 0 w
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
      | some (h, w) => quantLoop true (fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
  | .exFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => quantLoop false (fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
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

/-- A statement's row. An unbounded statement is classified before any evaluation. -/
def arithOutcome (D : Defs) (limit : Nat) (φ : Formula) : Outcome :=
  if φ.Bounded D then
    match decideBounded D limit φ with
    | some (true, _) => .decided .holds
    | some (false, _) => .decided .fails
    | none => .unknown (.limit .evaluations)
  else .unknown .unboundedStatement

/-! Proofs: the loops, then the evaluator against the meaning, through an agreement of environments. -/

open Classical in
theorem quantLoop_true (Q : Int → Prop) (step : Int → Nat → Option (Bool × Nat)) (limit : Nat)
    (hs : ∀ i w b w', step i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)) :
    ∀ n i w b w', quantLoop true step n i w = some (b, w') →
      (b = true ↔ ∀ k : Nat, k < n → Q (i + k)) ∧ (w ≤ limit → w' ≤ limit)
  | 0, i, w, b, w', h => by
    simp only [quantLoop, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    simp
  | n + 1, i, w, b, w', h => by
    simp only [quantLoop] at h
    cases hst : step i w with
    | none => simp [hst] at h
    | some r =>
      obtain ⟨b0, w0⟩ := r
      have ⟨hq, hw⟩ := hs i w b0 w0 hst
      cases b0 with
      | true =>
        simp only [hst, ite_true] at h
        have ⟨ih, ihw⟩ := quantLoop_true Q step limit hs n (i + 1) w0 b w' h
        refine ⟨ih.trans ⟨fun H k hk => ?_, fun H k hk => ?_⟩, fun h0 => ihw (hw h0)⟩
        · cases k with
          | zero => simpa using hq.mpr rfl
          | succ k => have := H k (by omega); rwa [show i + 1 + (k : Int) = i + ((k + 1 : Nat) : Int) by omega] at this
        · have := H (k + 1) (by omega); rwa [show i + ((k + 1 : Nat) : Int) = i + 1 + (k : Int) by omega] at this
      | false =>
        simp only [hst] at h
        simp at h hq
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp; exact ⟨0, by omega, by simpa using hq⟩, hw⟩

theorem quantLoop_false (Q : Int → Prop) (step : Int → Nat → Option (Bool × Nat)) (limit : Nat)
    (hs : ∀ i w b w', step i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)) :
    ∀ n i w b w', quantLoop false step n i w = some (b, w') →
      (b = true ↔ ∃ k : Nat, k < n ∧ Q (i + k)) ∧ (w ≤ limit → w' ≤ limit)
  | 0, i, w, b, w', h => by
    simp only [quantLoop, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    simp
  | n + 1, i, w, b, w', h => by
    simp only [quantLoop] at h
    cases hst : step i w with
    | none => simp [hst] at h
    | some r =>
      obtain ⟨b0, w0⟩ := r
      have ⟨hq, hw⟩ := hs i w b0 w0 hst
      cases b0 with
      | false =>
        simp only [hst, ite_true] at h
        have ⟨ih, ihw⟩ := quantLoop_false Q step limit hs n (i + 1) w0 b w' h
        refine ⟨ih.trans ⟨fun ⟨k, hk, H⟩ => ⟨k + 1, by omega, ?_⟩, fun ⟨k, hk, H⟩ => ?_⟩, fun h0 => ihw (hw h0)⟩
        · rwa [show i + ((k + 1 : Nat) : Int) = i + 1 + (k : Int) by omega]
        · cases k with
          | zero => simp at hq H; exact absurd H hq
          | succ k => exact ⟨k, by omega, by rwa [show i + 1 + (k : Int) = i + ((k + 1 : Nat) : Int) by omega]⟩
      | true =>
        simp only [hst] at h
        simp at h hq
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp; exact ⟨0, by omega, by simpa using hq⟩, hw⟩

open Classical in
theorem countLoop_sound (Q : Int → Prop) (step : Int → Nat → Option (Bool × Nat)) (limit : Nat)
    (hs : ∀ i w b w', step i w = some (b, w') → (Q i ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)) :
    ∀ n i acc w c w', countLoop step n i acc w = some (c, w') →
      c = ((acc + ((List.range n).filter fun k : Nat => decide (Q (i + k))).length : Nat) : Int) ∧
        (w ≤ limit → w' ≤ limit)
  | 0, i, acc, w, c, w', h => by
    simp only [countLoop, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    simp
  | n + 1, i, acc, w, c, w', h => by
    simp only [countLoop] at h
    cases hst : step i w with
    | none => simp [hst] at h
    | some r =>
      obtain ⟨b0, w0⟩ := r
      have ⟨hq, hw⟩ := hs i w b0 w0 hst
      simp only [hst] at h
      have ⟨ih, ihw⟩ := countLoop_sound Q step limit hs n (i + 1) _ w0 c w' h
      refine ⟨?_, fun h0 => ihw (hw h0)⟩
      rw [ih, List.range_succ_eq_map, List.filter_cons, List.filter_map]
      have hf : ((fun k : Nat => decide (Q (i + k))) ∘ Nat.succ) = fun k : Nat => decide (Q (i + 1 + k)) := by
        funext k; simp only [Function.comp]; congr 2; omega
      rw [hf]
      cases b0 <;> simp at hq <;> simp [hq] <;> omega

theorem range_all (l h : Int) (Q : Int → Prop) :
    (∀ k : Nat, k < (h - l + 1).toNat → Q (l + k)) ↔ ∀ i : Int, l ≤ i → i ≤ h → Q i :=
  ⟨fun H i h1 h2 => by have := H (i - l).toNat (by omega); rwa [show l + ((i - l).toNat : Int) = i by omega] at this,
   fun H k hk => H _ (by omega) (by omega)⟩

theorem range_ex (l h : Int) (Q : Int → Prop) :
    (∃ k : Nat, k < (h - l + 1).toNat ∧ Q (l + k)) ↔ ∃ i : Int, l ≤ i ∧ i ≤ h ∧ Q i :=
  ⟨fun ⟨k, hk, H⟩ => ⟨_, by omega, by omega, H⟩,
   fun ⟨i, h1, h2, H⟩ => ⟨(i - l).toNat, by omega, by rwa [show l + ((i - l).toNat : Int) = i by omega]⟩⟩

/-- An evaluator environment agrees with a meaning environment: each name has the same arity, a completed call gives
the meaning's value, and its work stays within the limit. -/
structure Agrees (E : Env) (O : OpEnv) (limit : Nat) : Prop where
  funs : ∀ f n g, O.funs f = some (n, g) → ∃ g', E.funs f = some (n, g') ∧
    ∀ xs w x w', g xs w = some (x, w') → g' xs = some x ∧ (w ≤ limit → w' ≤ limit)
  preds : ∀ p n P, O.preds p = some (n, P) → ∃ P', E.preds p = some (n, P') ∧
    ∀ xs w b w', P xs w = some (b, w') → (P' xs ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)

theorem charge_some {α : Type} {limit w : Nat} {k : Nat → Option (α × Nat)} {r : α × Nat}
    (h : charge limit w k = some r) : w < limit ∧ k (w + 1) = some r := by
  unfold charge at h; split at h <;> simp_all

mutual
theorem Term.evalB_sound {E : Env} {O : OpEnv} {limit : Nat} (hA : Agrees E O limit) :
    ∀ (t : Term) (ρ : List Int) (w : Nat) (x : Int) (w' : Nat), Term.evalB O limit ρ t w = some (x, w') →
      Term.value E ρ t = some x ∧ (w ≤ limit → w' ≤ limit)
  | .var i, ρ, w, x, w', h => by
    simp only [Term.evalB] at h
    cases hi : ρ[i]? <;> simp_all [Term.value]
  | .num n, ρ, w, x, w', h => by simp_all [Term.evalB, Term.value]
  | .add a b, ρ, w, x, w', h | .sub a b, ρ, w, x, w', h | .mul a b, ρ, w, x, w', h => by
    simp only [Term.evalB] at h
    cases ha : Term.evalB O limit ρ a w with
    | none => simp [ha] at h
    | some ra =>
      obtain ⟨xa, wa⟩ := ra
      cases hb : Term.evalB O limit ρ b wa with
      | none => simp [ha, hb] at h
      | some rb =>
        obtain ⟨xb, wb⟩ := rb
        have ⟨va, wka⟩ := Term.evalB_sound hA a ρ w xa wa ha
        have ⟨vb, wkb⟩ := Term.evalB_sound hA b ρ wa xb wb hb
        simp only [ha, hb, Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp [Term.value, va, vb], fun h0 => wkb (wka h0)⟩
  | .call f args, ρ, w, x, w', h => by
    simp only [Term.evalB] at h
    cases hf : O.funs f with
    | none => simp [hf] at h
    | some r =>
      obtain ⟨n, g⟩ := r
      cases hs : Term.evalBs O limit ρ args w with
      | none => simp [hf, hs] at h
      | some rs =>
        obtain ⟨xs, ws⟩ := rs
        simp only [hf, hs] at h
        split at h
        · obtain ⟨g', hg', hgg⟩ := hA.funs f n g hf
          have ⟨vs, wks⟩ := Term.evalBs_sound hA args ρ w xs ws hs
          have ⟨vx, wkx⟩ := hgg xs ws x w' h
          exact ⟨by simp [Term.value, *], fun h0 => wkx (wks h0)⟩
        · simp at h
  | .countFromTo lo hi φ, ρ, w, x, w', h => by
    simp only [Term.evalB] at h
    cases hl : Term.evalB O limit ρ lo w with
    | none => simp [hl] at h
    | some rl =>
      obtain ⟨l, wl⟩ := rl
      cases hh : Term.evalB O limit ρ hi wl with
      | none => simp [hl, hh] at h
      | some rh =>
        obtain ⟨u, wh⟩ := rh
        simp only [hl, hh] at h
        have ⟨vl, wkl⟩ := Term.evalB_sound hA lo ρ w l wl hl
        have ⟨vh, wkh⟩ := Term.evalB_sound hA hi ρ wl u wh hh
        have ⟨vc, wkc⟩ := countLoop_sound (fun i => Holds E (i :: ρ) φ) _ limit
          (fun i w b w' hs => Formula.evalB_sound hA φ (i :: ρ) w b w' hs) _ _ _ _ _ _ h
        exact ⟨by simp [Term.value, vl, vh, vc], fun h0 => wkc (wkh (wkl h0))⟩
theorem Term.evalBs_sound {E : Env} {O : OpEnv} {limit : Nat} (hA : Agrees E O limit) :
    ∀ (ts : List Term) (ρ : List Int) (w : Nat) (xs : List Int) (w' : Nat), Term.evalBs O limit ρ ts w = some (xs, w') →
      Term.values E ρ ts = some xs ∧ (w ≤ limit → w' ≤ limit)
  | [], ρ, w, xs, w', h => by simp_all [Term.evalBs, Term.values]
  | t :: ts, ρ, w, xs, w', h => by
    simp only [Term.evalBs] at h
    cases ht : Term.evalB O limit ρ t w with
    | none => simp [ht] at h
    | some r =>
      obtain ⟨x, w1⟩ := r
      cases hs : Term.evalBs O limit ρ ts w1 with
      | none => simp [ht, hs] at h
      | some rs =>
        obtain ⟨ys, w2⟩ := rs
        have ⟨vt, wkt⟩ := Term.evalB_sound hA t ρ w x w1 ht
        have ⟨vs, wks⟩ := Term.evalBs_sound hA ts ρ w1 ys w2 hs
        simp only [ht, hs, Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp [Term.values, vt, vs], fun h0 => wks (wkt h0)⟩
theorem Formula.evalB_sound {E : Env} {O : OpEnv} {limit : Nat} (hA : Agrees E O limit) :
    ∀ (φ : Formula) (ρ : List Int) (w : Nat) (b : Bool) (w' : Nat), Formula.evalB O limit ρ φ w = some (b, w') →
      (Holds E ρ φ ↔ b = true) ∧ (w ≤ limit → w' ≤ limit)
  | .eq a c, ρ, w, b, w', h | .lt a c, ρ, w, b, w', h | .le a c, ρ, w, b, w', h | .dvd a c, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases ha : Term.evalB O limit ρ a (w + 1) with
    | none => simp [ha] at h
    | some ra =>
      obtain ⟨xa, wa⟩ := ra
      cases hc : Term.evalB O limit ρ c wa with
      | none => simp [ha, hc] at h
      | some rc =>
        obtain ⟨xc, wc⟩ := rc
        have ⟨va, wka⟩ := Term.evalB_sound hA a ρ (w + 1) xa wa ha
        have ⟨vc, wkc⟩ := Term.evalB_sound hA c ρ wa xc wc hc
        simp only [ha, hc, Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨by simp [Holds, va, vc], fun _ => wkc (wka hw)⟩
  | .call p args, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hp : O.preds p with
    | none => simp [hp] at h
    | some r =>
      obtain ⟨n, P⟩ := r
      cases hs : Term.evalBs O limit ρ args (w + 1) with
      | none => simp [hp, hs] at h
      | some rs =>
        obtain ⟨xs, ws⟩ := rs
        simp only [hp, hs] at h
        split at h
        · obtain ⟨P', hP', hPP⟩ := hA.preds p n P hp
          have ⟨vs, wks⟩ := Term.evalBs_sound hA args ρ (w + 1) xs ws hs
          have ⟨vx, wkx⟩ := hPP xs ws b w' h
          refine ⟨?_, fun _ => wkx (wks hw)⟩
          simp only [Holds, hP', vs, Option.some.injEq, Prod.mk.injEq]
          constructor
          · rintro ⟨_, _, _, ⟨rfl, rfl⟩, rfl, _, hx⟩; exact vx.mp hx
          · intro hb; exact ⟨n, P', xs, ⟨rfl, rfl⟩, rfl, by assumption, vx.mpr hb⟩
        · simp at h
  | .not φ, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hφ : Formula.evalB O limit ρ φ (w + 1) with
    | none => simp [hφ] at h
    | some r =>
      obtain ⟨b1, w1⟩ := r
      have ⟨v, wk⟩ := Formula.evalB_sound hA φ ρ (w + 1) b1 w1 hφ
      simp only [hφ, Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl⟩ := h
      exact ⟨by simp [Holds, v], fun _ => wk hw⟩
  | .and φ ψ, ρ, w, b, w', h | .or φ ψ, ρ, w, b, w', h | .imp φ ψ, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hφ : Formula.evalB O limit ρ φ (w + 1) with
    | none => simp [hφ] at h
    | some r =>
      obtain ⟨b1, w1⟩ := r
      have ⟨v, wk⟩ := Formula.evalB_sound hA φ ρ (w + 1) b1 w1 hφ
      cases b1 <;> simp only [hφ, Option.some.injEq, Prod.mk.injEq] at h <;>
        first
        | (obtain ⟨rfl, rfl⟩ := h; exact ⟨by simp_all [Holds], fun _ => wk hw⟩)
        | (have ⟨v2, wk2⟩ := Formula.evalB_sound hA ψ ρ w1 b w' h
           exact ⟨by simp_all [Holds], fun _ => wk2 (wk hw)⟩)
  | .allNat _, _, _, _, _, h | .exNat _, _, _, _, _, h | .allInt _, _, _, _, _, h | .exInt _, _, _, _, _, h => by
    simp [Formula.evalB] at h
  | .allFromTo lo hi φ, ρ, w, b, w', h | .exFromTo lo hi φ, ρ, w, b, w', h => by
    simp only [Formula.evalB] at h
    have ⟨hw, h⟩ := charge_some h
    cases hl : Term.evalB O limit ρ lo (w + 1) with
    | none => simp [hl] at h
    | some rl =>
      obtain ⟨l, wl⟩ := rl
      cases hh : Term.evalB O limit ρ hi wl with
      | none => simp [hl, hh] at h
      | some rh =>
        obtain ⟨u, wh⟩ := rh
        simp only [hl, hh] at h
        have ⟨vl, wkl⟩ := Term.evalB_sound hA lo ρ (w + 1) l wl hl
        have ⟨vh, wkh⟩ := Term.evalB_sound hA hi ρ wl u wh hh
        have hs := fun i w b w' hs => Formula.evalB_sound hA φ (i :: ρ) w b w' hs
        first
        | (have ⟨v, wk⟩ := quantLoop_true (fun i => Holds E (i :: ρ) φ) _ limit hs _ _ _ _ _ h
           have H : Holds E ρ (.allFromTo lo hi φ) ↔ ∀ i, l ≤ i → i ≤ u → Holds E (i :: ρ) φ := by simp [Holds, vl, vh]
           exact ⟨(H.trans (range_all l u (fun i => Holds E (i :: ρ) φ)).symm).trans v.symm, fun _ => wk (wkh (wkl hw))⟩)
        | (have ⟨v, wk⟩ := quantLoop_false (fun i => Holds E (i :: ρ) φ) _ limit hs _ _ _ _ _ h
           have H : Holds E ρ (.exFromTo lo hi φ) ↔ ∃ i, l ≤ i ∧ i ≤ u ∧ Holds E (i :: ρ) φ := by simp [Holds, vl, vh]
           exact ⟨(H.trans (range_ex l u (fun i => Holds E (i :: ρ) φ)).symm).trans v.symm, fun _ => wk (wkh (wkl hw))⟩)
end

theorem agrees_env (D : Defs) (limit : Nat) : Agrees D.env (D.opEnv limit) limit := by
  unfold Defs.env Defs.opEnv
  generalize hE : (⟨fun _ => none, fun _ => none⟩ : Env) = E
  generalize hO : (⟨fun _ => none, fun _ => none⟩ : OpEnv) = O
  have hA : Agrees E O limit := by subst hE hO; exact ⟨by simp, by simp⟩
  clear hE hO
  induction D generalizing E O with
  | nil => exact hA
  | cons d D ih =>
    apply ih
    cases d with
    | fn f n body =>
      refine ⟨fun g m k hk => ?_, hA.preds⟩
      by_cases hg : g = f
      · subst hg
        simp only [ite_true, Option.some.injEq, Prod.mk.injEq] at hk ⊢
        obtain ⟨rfl, rfl⟩ := hk
        exact ⟨_, ⟨rfl, rfl⟩, fun xs w x w' h => Term.evalB_sound hA body xs w x w' h⟩
      · simp only [hg, ite_false] at hk ⊢; exact hA.funs g m k hk
    | pred p n body =>
      refine ⟨hA.funs, fun q m k hk => ?_⟩
      by_cases hq : q = p
      · subst hq
        simp only [ite_true, Option.some.injEq, Prod.mk.injEq] at hk ⊢
        obtain ⟨rfl, rfl⟩ := hk
        exact ⟨_, ⟨rfl, rfl⟩, fun xs w b w' h => Formula.evalB_sound hA body xs w b w' h⟩
      · simp only [hq, ite_false] at hk ⊢; exact hA.preds q m k hk


set_option linter.unusedVariables false in
theorem decideBounded_sound (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : D.Means φ ↔ b = true :=
  (Formula.evalB_sound (agrees_env D limit) φ [] 0 b w h).1

theorem decideBounded_work (D : Defs) (φ : Formula) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : w ≤ limit :=
  (Formula.evalB_sound (agrees_env D limit) φ [] 0 b w h).2 (Nat.zero_le _)

theorem arithOutcome_unbounded_iff (D : Defs) (limit : Nat) (φ : Formula) :
    arithOutcome D limit φ = .unknown .unboundedStatement ↔ φ.Bounded D = false := by
  unfold arithOutcome
  cases φ.Bounded D <;> simp
  split <;> simp

theorem arithOutcome_exhausted_iff (D : Defs) (limit : Nat) (φ : Formula) :
    arithOutcome D limit φ = .unknown (.limit .evaluations) ↔
      φ.Bounded D = true ∧ decideBounded D limit φ = none := by
  unfold arithOutcome
  cases φ.Bounded D <;> simp
  split <;> simp_all

theorem arithOutcome_decided (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (limit : Nat) (v : Verdict) (h : arithOutcome D limit φ = .decided v) :
    v ≠ .undefined ∧ (v = .holds ↔ D.Means φ) := by
  unfold arithOutcome at h
  split at h
  · split at h <;> simp at h <;> subst h
    · next w hb => simp [decideBounded_sound D hD φ hφ limit true w hb]
    · next w hb => simp [decideBounded_sound D hD φ hφ limit false w hb]
  · simp at h

end VE.Arith
