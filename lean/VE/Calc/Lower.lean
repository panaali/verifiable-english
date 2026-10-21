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
form that is not a nonzero constant. -/
def Expr.linear : Expr → Option QLin
  | .lit q => some ⟨q, []⟩
  | .val n => some ⟨0, [(n, 1)]⟩
  | .add a b => do return (← a.linear).add (← b.linear)
  | .sub a b => do return (← a.linear).add ((← b.linear).scale (-1))
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

theorem Expr.linear_sound (κ : String → Rat) (e : Expr) (L : QLin) (h : e.linear = some L) :
    Denotes (fun n => some (κ n)) e (L.eval κ) := by
  induction e generalizing L with
  | lit q => cases h; rw [show QLin.eval κ ⟨q, []⟩ = q by simp [QLin.eval, Rat.add_zero]]; exact .lit
  | val n => cases h; rw [show QLin.eval κ ⟨0, [(n, 1)]⟩ = κ n by simp [QLin.eval, Rat.add_zero, Rat.zero_add]]; exact .val rfl
  | add a b iha ihb =>
      cases ha : a.linear <;> cases hb : b.linear <;> simp [Expr.linear, ha, hb] at h
      subst h; rw [QLin.eval_add]; exact .add (iha _ ha) (ihb _ hb)
  | sub a b iha ihb =>
      cases ha : a.linear <;> cases hb : b.linear <;> simp [Expr.linear, ha, hb] at h
      subst h; rw [QLin.eval_add, QLin.eval_scale]
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
