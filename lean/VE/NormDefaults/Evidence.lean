import VE.NormDefaults.Status

/-! Finite evidence for statuses and conflicts (docs/spec/norm-defaults.md 2.5, 3.1
and 7): finite fillings, the UNDECIDED and latent-CONFLICT witnesses, `table3`
(Kleene evaluation with the pair rule) and exhaustive enumeration.

A finite filling `F : FiniteFill U α` lists, per unsaid predicate, the tuples filled
"yes"; `M.withFill F` keeps only its typed tuples, so its structure is
`withFill U M.asStructure (finFill F)` (`withFill_finite`). Every certificate is
checked here: the search that proposes it is untrusted. -/
namespace VE.NormDefaults
open VE.Norms VE.Route
universe u

/-- Finite unsaid tables, indexed by the unsaid predicate names. -/
def FiniteFill (_U : UDoc) (α : Type u) : Type u := String → List (List α)

/-- `TupleTyped` over a finite model, by evaluation. -/
def tupleTypedB {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) : List String → List α → Bool
  | [], [] => true
  | s :: ss, v :: vs => decide (v ∈ M.domains s) && tupleTypedB M ss vs
  | _, _ => false

theorem tupleTypedB_iff {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) :
    ∀ (ss : List String) (vs : List α), tupleTypedB M ss vs = true ↔ VE.TupleTyped M.asStructure ss vs
  | [], [] => by simp [tupleTypedB, VE.TupleTyped]
  | s :: ss, v :: vs => by
    simp only [tupleTypedB, Bool.and_eq_true, decide_eq_true_eq, VE.TupleTyped, tupleTypedB_iff M ss vs]
    rfl
  | [], _ :: _ => by simp [tupleTypedB, VE.TupleTyped]
  | _ :: _, [] => by simp [tupleTypedB, VE.TupleTyped]

end VE.NormDefaults

namespace VE.FiniteModel
open VE.NormDefaults

/-- `M` extended by a finite filling, on typed tuples. -/
def withFill {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) {U : UDoc} (F : FiniteFill U α) :
    VE.FiniteModel α :=
  { M with relations := fun n => match U.unspec.find? (fun p => unsaidName p == n) with
      | some p => (F n).filter (tupleTypedB M (sortsOf U.D p))
      | none => M.relations n }

end VE.FiniteModel

namespace VE.NormDefaults
open VE.Norms VE.Route

/-- A finite filling read as tables. -/
def finFill {U : UDoc} {α : Type u} (M : VE.FiniteModel α) (F : FiniteFill U α) : FillTables U M.asStructure :=
  fun n vs => vs ∈ F n

/-- `fillValid U M F` evaluates `Fill_T` on `M.withFill F`. -/
def fillValid {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (F : FiniteFill U α) : Bool :=
  (fillPremises U).all (fun φ => φ.eval (M.withFill F) [])

theorem withFill_finite_rel {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (F : FiniteFill U α)
    (n : String) (vs : List α) :
    (M.withFill F).asStructure.relation n vs ↔ (withFill U M.asStructure (finFill M F)).relation n vs := by
  simp only [VE.FiniteModel.asStructure, VE.FiniteModel.withFill, withFill, finFill]
  cases U.unspec.find? (fun p => unsaidName p == n) with
  | none => exact Iff.rfl
  | some p =>
    simp only [List.mem_filter]
    exact and_congr_right fun _ => tupleTypedB_iff M _ vs

/-- A formula has the same truth in `M.withFill F` and in `withFill U M (finFill F)`. -/
theorem denote_withFill_finite {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α)
    (F : FiniteFill U α) (φ : VE.Formula) (ρ : List α) :
    φ.denote (M.withFill F).asStructure ρ ↔ φ.denote (withFill U M.asStructure (finFill M F)) ρ :=
  denote_rel_iff M.asStructure _ _ (withFill_finite_rel U M F) φ ρ

theorem eval_withFill {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α)
    (F : FiniteFill U α) (φ : VE.Formula) (ρ : List α) :
    φ.eval (M.withFill F) ρ = true ↔ φ.denote (withFill U M.asStructure (finFill M F)) ρ :=
  (VE.eval_iff_denote _ ρ φ).trans (denote_withFill_finite U M F φ ρ)

/-- A checked finite filling is admissible. -/
theorem admissible_of_fillValid {α : Type u} [DecidableEq α] (U : UDoc) (h : WellFormedU U = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true)
    (F : FiniteFill U α) (hF : fillValid U M F = true) :
    BaseAdmissibleU U (withFill U M.asStructure (finFill M F)) := by
  have hu := uvalid h
  refine ⟨withFill_baseAdmissible hu (baseAdmissible_of_valid U.D M valid hb) _, fun φ hφ => ?_⟩
  exact (eval_withFill U M F φ []).mp (List.all_eq_true.mp hF φ hφ)

/-- `undecided_witness_sound`: two checked finite fillings with opposite values
witness UNDECIDED. -/
theorem undecided_witness_sound {α : Type u} [DecidableEq α] (U : UDoc) (h : WellFormedU U = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true)
    (F₁ F₂ : FiniteFill U α) (h₁ : fillValid U M F₁ = true) (h₂ : fillValid U M F₂ = true)
    (r : Regulated) (hr : r ∈ U.D.T.regulated) (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (v₁ : (outcomeBase (fill U) r.name).eval (M.withFill F₁) (tupleVal vs) = true)
    (v₂ : (outcomeBase (fill U) r.name).eval (M.withFill F₂) (tupleVal vs) = false) :
    UndecidedAt U M.asStructure r vs := by
  have _ := hr
  have _ := typed
  refine ⟨finFill M F₁, finFill M F₂, admissible_of_fillValid U h M valid hb F₁ h₁,
    admissible_of_fillValid U h M valid hb F₂ h₂, (eval_withFill U M F₁ _ _).mp v₁, fun hd => ?_⟩
  have := (eval_withFill U M F₂ _ _).mpr hd
  rw [v₂] at this
  cases this

/-- `conflictU_witness_sound`: a filled finite witness (settled or latent) refutes
`ConflictFreeU`; the pair companion is `conflictU_pair_witness_sound`. -/
theorem conflictU_witness_sound {α : Type u} [DecidableEq α] (U : UDoc) (h : WellFormedU U = true) (r : Regulated)
    (hr : r ∈ U.D.T.regulated) (M : VE.FiniteModel α) (valid : M.Valid (envAt (fill U) 0))
    (hb : backgroundValid (fill U) M = true) (hF : (fillPremises U).all (fun φ => φ.eval M []) = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (hw : (conflict (fill U) r).eval M (tupleVal vs) = true) :
    ¬ ConflictFreeU.{u} U := by
  have _ := h
  intro hc
  have hB : BaseAdmissibleU U M.asStructure :=
    ⟨baseAdmissible_of_valid (fill U) M valid hb, fun φ hφ =>
      (VE.eval_iff_denote M [] φ).mp (List.all_eq_true.mp hF φ hφ)⟩
  exact (hc _ hB).1 r hr vs typed ((VE.eval_iff_denote M _ _).mp hw)

theorem conflictU_pair_witness_sound {α : Type u} [DecidableEq α] (U : UDoc) (pr : Pair) (hpr : pr ∈ pairs U.D.T)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (fill U) 0))
    (hb : backgroundValid (fill U) M = true) (hF : (fillPremises U).all (fun φ => φ.eval M []) = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure pr.sorts vs)
    (hw : (pairConflict (fill U) pr).eval M (tupleVal vs) = true) :
    ¬ ConflictFreeU.{u} U := by
  intro hc
  have hB : BaseAdmissibleU U M.asStructure :=
    ⟨baseAdmissible_of_valid (fill U) M valid hb, fun φ hφ =>
      (VE.eval_iff_denote M [] φ).mp (List.all_eq_true.mp hF φ hφ)⟩
  exact (hc _ hB).2 pr hpr vs typed ((VE.eval_iff_denote M _ _).mp hw)

/-! ## Kleene evaluation -/

def kneg : Option Bool → Option Bool
  | some b => some (!b)
  | none => none

def kand : Option Bool → Option Bool → Option Bool
  | some false, _ => some false
  | _, some false => some false
  | some true, some true => some true
  | _, _ => none

def kor : Option Bool → Option Bool → Option Bool
  | some true, _ => some true
  | _, some true => some true
  | some false, some false => some false
  | _, _ => none

def kall (l : List (Option Bool)) : Option Bool :=
  if l.any (· == some false) then some false else if l.all (· == some true) then some true else none

def kany (l : List (Option Bool)) : Option Bool :=
  if l.any (· == some true) then some true else if l.all (· == some false) then some false else none

/-- Kleene evaluation over a finite model; `atomV` gives each atom's value
(`none`: unknown). Terms and quantifier domains are `M`'s. -/
def kleene {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) (atomV : String → List α → Option Bool)
    (ρ : List α) : VE.Formula → Option Bool
  | .top => some true
  | .bottom => some false
  | .unary p t => match t.denote M.asStructure ρ with
      | some v => atomV p [v]
      | none => some false
  | .binary p t w => match t.denote M.asStructure ρ, w.denote M.asStructure ρ with
      | some v, some v' => atomV p [v, v']
      | _, _ => some false
  | .eq t w => match t.denote M.asStructure ρ, w.denote M.asStructure ρ with
      | some v, some v' => some (decide (v = v'))
      | _, _ => some false
  | .not a => kneg (kleene M atomV ρ a)
  | .and a b => kand (kleene M atomV ρ a) (kleene M atomV ρ b)
  | .or a b => kor (kleene M atomV ρ a) (kleene M atomV ρ b)
  | .implies a b => kor (kneg (kleene M atomV ρ a)) (kleene M atomV ρ b)
  | .all s a => kall ((M.domains s).map (fun v => kleene M atomV (v :: ρ) a))
  | .ex s a => kany ((M.domains s).map (fun v => kleene M atomV (v :: ρ) a))

theorem kneg_sound {A : Prop} {x : Option Bool} (hx : ∀ c, x = some c → (A ↔ c = true)) :
    ∀ b, kneg x = some b → (¬ A ↔ b = true) := by
  intro b hb
  cases x with
  | none => cases hb
  | some c =>
    simp only [kneg, Option.some.injEq] at hb
    subst hb
    rw [hx c rfl]
    cases c <;> simp

theorem kand_sound {A B : Prop} {x y : Option Bool} (hx : ∀ c, x = some c → (A ↔ c = true))
    (hy : ∀ c, y = some c → (B ↔ c = true)) : ∀ b, kand x y = some b → (A ∧ B ↔ b = true) := by
  intro b hb
  rcases x with _ | _ | _ <;> rcases y with _ | _ | _ <;> simp [kand] at hb <;> subst hb <;>
    simp_all

theorem kor_sound {A B : Prop} {x y : Option Bool} (hx : ∀ c, x = some c → (A ↔ c = true))
    (hy : ∀ c, y = some c → (B ↔ c = true)) : ∀ b, kor x y = some b → (A ∨ B ↔ b = true) := by
  intro b hb
  rcases x with _ | _ | _ <;> rcases y with _ | _ | _ <;> simp [kor] at hb <;> subst hb <;>
    simp_all

theorem kall_sound {β : Type u} {P : β → Prop} (f : β → Option Bool) (l : List β)
    (hf : ∀ v ∈ l, ∀ c, f v = some c → (P v ↔ c = true)) :
    ∀ b, kall (l.map f) = some b → ((∀ v ∈ l, P v) ↔ b = true) := by
  intro b hb
  unfold kall at hb
  split at hb
  · rename_i ha
    cases hb
    obtain ⟨x, hx, hxe⟩ := List.any_eq_true.mp ha
    obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hx
    have hfv : f v = some false := by simpa using hxe
    simp only [Bool.false_eq_true, iff_false]
    intro hall
    exact absurd ((hf v hv false hfv).mp (hall v hv)) (by simp)
  · split at hb
    · rename_i _ ha
      cases hb
      simp only [iff_true]
      intro v hv
      have := List.all_eq_true.mp ha (f v) (List.mem_map_of_mem hv)
      exact (hf v hv true (by simpa using this)).mpr rfl
    · cases hb

theorem kany_sound {β : Type u} {P : β → Prop} (f : β → Option Bool) (l : List β)
    (hf : ∀ v ∈ l, ∀ c, f v = some c → (P v ↔ c = true)) :
    ∀ b, kany (l.map f) = some b → ((∃ v ∈ l, P v) ↔ b = true) := by
  intro b hb
  unfold kany at hb
  split at hb
  · rename_i ha
    cases hb
    obtain ⟨x, hx, hxe⟩ := List.any_eq_true.mp ha
    obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hx
    simp only [iff_true]
    exact ⟨v, hv, (hf v hv true (by simpa using hxe)).mpr rfl⟩
  · split at hb
    · rename_i _ ha
      cases hb
      simp only [Bool.false_eq_true, iff_false, not_exists, not_and]
      intro v hv hp
      have := List.all_eq_true.mp ha (f v) (List.mem_map_of_mem hv)
      exact absurd ((hf v hv false (by simpa using this)).mp hp) (by simp)
    · cases hb

/-- Kleene soundness: a definite value is the truth value in every structure over
`M`'s carrier, domains and constants whose relations agree with the definite atoms. -/
theorem kleene_sound {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) (atomV : String → List α → Option Bool)
    (R : String → List α → Prop) (hA : ∀ p vs b, atomV p vs = some b → (R p vs ↔ b = true)) :
    ∀ (φ : VE.Formula) (ρ : List α) (b : Bool), kleene M atomV ρ φ = some b →
      (φ.denote { M.asStructure with relation := R } ρ ↔ b = true) := by
  intro φ
  induction φ with
  | top => intro ρ b hb; simp only [kleene, Option.some.injEq] at hb; subst hb; simp [VE.Formula.denote]
  | bottom => intro ρ b hb; simp only [kleene, Option.some.injEq] at hb; subst hb; simp [VE.Formula.denote]
  | unary p t =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    have ht : t.denote { M.asStructure with relation := R } ρ = t.denote M.asStructure ρ := by
      cases t <;> rfl
    rw [ht]
    cases hv : t.denote M.asStructure ρ with
    | none => rw [hv] at hb; simp only [Option.some.injEq] at hb; subst hb; simp
    | some v =>
      rw [hv] at hb
      simp only [Option.some.injEq, exists_eq_left']
      exact hA p [v] b hb
  | binary p t w =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    have ht : ∀ t : VE.Term, t.denote { M.asStructure with relation := R } ρ = t.denote M.asStructure ρ := by
      intro t; cases t <;> rfl
    rw [ht t, ht w]
    cases hv : t.denote M.asStructure ρ <;> cases hw : w.denote M.asStructure ρ <;> rw [hv, hw] at hb <;>
      simp only [Option.some.injEq] at hb
    all_goals first
      | (subst hb; simp)
      | (constructor
         · rintro ⟨_, _, h1, h2, h⟩
           simp only [Option.some.injEq] at h1 h2
           subst h1; subst h2
           exact (hA p _ b hb).mp h
         · intro h
           exact ⟨_, _, rfl, rfl, (hA p _ b hb).mpr h⟩)
  | eq t w =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    have ht : ∀ t : VE.Term, t.denote { M.asStructure with relation := R } ρ = t.denote M.asStructure ρ := by
      intro t; cases t <;> rfl
    rw [ht t, ht w]
    cases hv : t.denote M.asStructure ρ <;> cases hw : w.denote M.asStructure ρ <;> rw [hv, hw] at hb <;>
      simp only [Option.some.injEq] at hb <;> subst hb <;> simp [eq_comm]
  | not a ih =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    exact kneg_sound (fun c hc => ih ρ c hc) b hb
  | and a c ia ic =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    exact kand_sound (fun x hx => ia ρ x hx) (fun x hx => ic ρ x hx) b hb
  | or a c ia ic =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    exact kor_sound (fun x hx => ia ρ x hx) (fun x hx => ic ρ x hx) b hb
  | implies a c ia ic =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    have himp : ∀ A C : Prop, (A → C) ↔ ¬ A ∨ C := fun A C =>
      ⟨fun h => (Classical.em A).elim (fun ha => Or.inr (h ha)) Or.inl, fun h ha => h.elim (absurd ha) id⟩
    rw [himp]
    exact kor_sound (kneg_sound (fun x hx => ia ρ x hx)) (fun x hx => ic ρ x hx) b hb
  | all s a ih =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    exact kall_sound (P := fun v => a.denote { M.asStructure with relation := R } (v :: ρ)) _ _
      (fun v _ c hc => ih (v :: ρ) c hc) b hb
  | ex s a ih =>
    intro ρ b hb
    simp only [kleene] at hb
    simp only [VE.Formula.denote]
    exact kany_sound (P := fun v => a.denote { M.asStructure with relation := R } (v :: ρ)) _ _
      (fun v _ c hc => ih (v :: ρ) c hc) b hb

/-! ## `table3`: outcomes in DAG order, unsaid atoms unknown, with the pair rule -/

/-- The value of an atom: a layer symbol from the table, an unsaid atom unknown, a
base atom from `M`. -/
def atomV {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (tab : String → List α → Option Bool)
    (p : String) (vs : List α) : Option Bool :=
  if p ∈ layerNames (fill U).T then tab p vs
  else if p ∈ unsaidNames U then none
  else some (decide (vs ∈ M.relations p))

/-- "No author rule on `p` decides", over the prefix (`gapF` before substitution). -/
def gapBody (U : UDoc) (p : String) : VE.Formula := .and (.not (pos U.D.T p)) (.not (neg U.D.T p))

/-- The profile rule at a gap of an unspecified `q`: `q := yes` where `q` is the
permission of a pair whose obligation is yes; `q := no` where `q` is the obligation
of a pair whose permission is no (2.5). -/
def pairRule {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (tab : String → List α → Option Bool)
    (q : Regulated) (vs : List α) : Option Bool :=
  if decide (q.name ∈ U.unspec) && kleene M (atomV U M tab) (tupleVal vs) (gapBody U q.name) == some true then
    if (pairs U.D.T).any (fun pr => pr.perm == q.name && tab pr.req vs == some true) then some true
    else if (pairs U.D.T).any (fun pr => pr.req == q.name && tab pr.perm vs == some false) then some false
    else none
  else none

/-- The table after the first `k` layer symbols of `T‴`. -/
def tabK {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) : Nat → String → List α → Option Bool
  | 0 => fun _ _ => none
  | k + 1 => fun n vs => match (syms (fill U).T)[k]? with
    | some q =>
      if n = q.name then
        (if tupleTypedB M q.sorts vs then
          match kleene M (atomV U M (tabK U M k)) (tupleVal vs) (q.meaning (fill U).T) with
          | some b => some b
          | none => match q with
            | .reg r => pairRule U M (tabK U M k) r vs
            | .defn _ => none
        else none)
      else tabK U M k n vs
    | none => tabK U M k n vs

/-- `table3 U M n vs`: the three-valued outcome of `n` at `vs` (`none`: unknown). -/
def table3 {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (n : String) (vs : List α) : Option Bool :=
  tabK U M (size (fill U)) n vs

open VE.SoftNorms (canon canon_subst canon_off canon_agrees) in
/-- `canon`'s relation of a regulated predicate is its outcome at the base, on every tuple. -/
theorem canon_regulated {D : Doc} (hv : Valid D) (B : VE.Structure.{u}) {r : Regulated} (hr : r ∈ D.T.regulated)
    (vs : List B.Carrier) : (canon D B).relation r.name vs ↔ (outcomeBase D r.name).denote B (tupleVal vs) := by
  obtain ⟨k, hk⟩ := mem_syms_index (hv.regulated r hr)
  have hkl : k < size D := (List.getElem?_eq_some_iff.mp hk).1
  have hb : before D r.name = k := before_eq hv hk
  have he : expTable D.T (size D) r.name = some (substWith (expTable D.T k) (outcome D.T r)) :=
    expTable_at hv (size D) k (.reg r) hkl hk
  simp only [canon, he, outcomeBase, find_regulated hv hk, hb]
  rfl

section Table
open VE.SoftNorms (canon canon_subst canon_off canon_agrees)
variable {α : Type u} [DecidableEq α] {U : UDoc} (hu : UValid U) (h : WellFormedU U = true)
  (M : VE.FiniteModel α) (F : FillTables U M.asStructure) (hF : BaseAdmissibleU U (withFill U M.asStructure F))
include hu h hF

theorem tabK_sound : ∀ k n vs b, tabK U M k n vs = some b →
    ((canon (fill U) (withFill U M.asStructure F)).relation n vs ↔ b = true) := by
  have hw' := fill_wellFormed U h
  have hv' := valid_of_wellFormed _ hw'
  have hc : ConstantsTyped (fill U) (withFill U M.asStructure F) := hF.1.1.1
  intro k
  induction k with
  | zero => intro n vs b ht; cases ht
  | succ k ih =>
    -- the atoms are sound for the table below `k`
    have hA : ∀ p vs b, atomV U M (tabK U M k) p vs = some b →
        ((canon (fill U) (withFill U M.asStructure F)).relation p vs ↔ b = true) := by
      intro p vs b hb
      unfold atomV at hb
      split at hb
      · exact ih p vs b hb
      · rename_i hl
        split at hb
        · cases hb
        · rename_i hun
          simp only [Option.some.injEq] at hb
          subst hb
          rw [canon_off _ hl, withFill_off U _ F hun]
          simp [VE.FiniteModel.asStructure]
    have hK : ∀ φ ρ b, kleene M (atomV U M (tabK U M k)) ρ φ = some b →
        (φ.denote (canon (fill U) (withFill U M.asStructure F)) ρ ↔ b = true) :=
      kleene_sound M _ _ hA
    intro n vs b ht
    simp only [tabK] at ht
    split at ht
    · rename_i q hq
      split at ht
      · rename_i hn
        subst hn
        split at ht
        · rename_i hty
          have htyX : VE.TupleTyped (canon (fill U) (withFill U M.asStructure F)) q.sorts vs :=
            (tupleTyped_relation (withFill U M.asStructure F) _ _ vs).mpr
              ((tupleTyped_relation M.asStructure _ _ vs).mpr ((tupleTypedB_iff M _ vs).mp hty))
          have hag := canon_agrees hv' (withFill U M.asStructure F) hc (k + 1) k q (Nat.lt_succ_self k) hq vs htyX
          split at ht
          · rename_i b' hb'
            simp only [Option.some.injEq] at ht
            subst ht
            exact hag.trans (hK _ _ _ hb')
          · cases q with
            | defn _ => cases ht
            | reg r =>
              have hr' : r ∈ (fill U).T.regulated := mem_syms_reg (List.mem_of_getElem? hq)
              have hr : r ∈ U.D.T.regulated := hr'
              have htyped : VE.TupleTyped (withFill U M.asStructure F) r.sorts vs :=
                (tupleTyped_relation M.asStructure _ _ vs).mpr ((tupleTypedB_iff M _ vs).mp hty)
              change (canon (fill U) (withFill U M.asStructure F)).relation r.name vs ↔ b = true
              simp only at ht
              unfold pairRule at ht
              split at ht
              · rename_i hcond
                simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hcond
                obtain ⟨hp, hgap⟩ := hcond
                -- the gap, read at the base
                have hgapB : (gapF U r.name).denote (withFill U M.asStructure F) (tupleVal vs) := by
                  have hk := index_before hu.valid hr
                  have hT := rulesTyped_of_valid hu.valid hk
                  have hmono : (gapBody U r.name).WellFormed (envAt (fill U) (before U.D r.name)) r.sorts.reverse := by
                    rw [← VE.check_iff_wellFormed]
                    exact check_envAt_fill hu ((VE.check_iff_wellFormed _ _ _).mpr
                      ⟨decides_wellFormed hT true, decides_wellFormed hT false⟩)
                  have := canon_subst hv' (withFill U M.asStructure F) hc _ _ _ hmono _
                    (tupleVal_typed _ _ vs htyped)
                  simp only [gapF, hp, if_true, before_fill hu]
                  exact this.mpr ((hK _ _ true hgap).mpr rfl)
                have hO : (canon (fill U) (withFill U M.asStructure F)).relation r.name vs ↔
                    (outcomeBase (fill U) r.name).denote (withFill U M.asStructure F) (tupleVal vs) :=
                  canon_regulated hv' (withFill U M.asStructure F) hr' vs
                split at ht
                · rename_i hany
                  simp only [Option.some.injEq] at ht
                  subst ht
                  obtain ⟨pr, hpr, hpe⟩ := List.any_eq_true.mp hany
                  simp only [Bool.and_eq_true, beq_iff_eq] at hpe
                  obtain ⟨hperm, hreq⟩ := hpe
                  obtain ⟨m', hm', hm'n, _, hm's⟩ := pair_perm hu hpr
                  obtain ⟨r', hr'', hr'n, _, _, _⟩ := pair_req hpr
                  have hmr : m' = r := hu.regulated_eq hm' hr (hm'n.trans hperm)
                  subst hmr
                  have hreqO := (canon_regulated hv' (withFill U M.asStructure F) (show r' ∈ (fill U).T.regulated from hr'') vs).mp
                    (by rw [hr'n]; exact (ih _ vs true hreq).mpr rfl)
                  have hprem := hF.2 _ (List.mem_map.mpr ⟨pr, List.mem_filter.mpr ⟨hpr, by simp [hperm, hp]⟩, rfl⟩)
                  rw [bindAll_denote_nil] at hprem
                  have := hprem vs (by rw [← hm's]; exact htyped)
                  simp only [VE.Formula.denote, pairConflict, not_and] at this
                  rw [hO]
                  simp only [iff_true]
                  apply Classical.byContradiction
                  intro hno
                  exact this ⟨hr'n ▸ hreqO, hm'n ▸ hno⟩ (Or.inr (hm'n ▸ hgapB))
                · split at ht
                  · rename_i _ hany
                    simp only [Option.some.injEq] at ht
                    subst ht
                    obtain ⟨pr, hpr, hpe⟩ := List.any_eq_true.mp hany
                    simp only [Bool.and_eq_true, beq_iff_eq] at hpe
                    obtain ⟨hreq, hperm⟩ := hpe
                    obtain ⟨r', hr'', hr'n, _, _, hr's⟩ := pair_req hpr
                    obtain ⟨m', hm', hm'n, _, _⟩ := pair_perm hu hpr
                    have hrr : r' = r := hu.regulated_eq hr'' hr (hr'n.trans hreq)
                    subst hrr
                    have hpermO : ¬ (outcomeBase (fill U) m'.name).denote (withFill U M.asStructure F) (tupleVal vs) := by
                      intro hm
                      have hc' := (canon_regulated hv' (withFill U M.asStructure F)
                        (show m' ∈ (fill U).T.regulated from hm') vs).mpr hm
                      rw [hm'n] at hc'
                      have := (ih _ vs false hperm).mp hc'
                      cases this
                    have hprem := hF.2 _ (List.mem_map.mpr ⟨pr, List.mem_filter.mpr ⟨hpr, by simp [hreq, hp]⟩, rfl⟩)
                    rw [bindAll_denote_nil] at hprem
                    have := hprem vs (by rw [← hr's]; exact htyped)
                    simp only [VE.Formula.denote, pairConflict, not_and] at this
                    rw [hO]
                    simp only [Bool.false_eq_true, iff_false]
                    intro hro
                    exact this ⟨hr'n ▸ hro, hm'n ▸ hpermO⟩ (Or.inl (hr'n ▸ hgapB))
                  · cases ht
              · cases ht
        · cases ht
      · exact ih n vs b ht
    · exact ih n vs b ht

/-- The value `table3` gives is the outcome at the base in every admissible filling. -/
theorem table3_outcome {r : Regulated} (hr : r ∈ U.D.T.regulated) (vs : List α) (b : Bool)
    (ht : table3 U M r.name vs = some b) :
    (outcomeBase (fill U) r.name).denote (withFill U M.asStructure F) (tupleVal vs) ↔ b = true := by
  have hv' := valid_of_wellFormed _ (fill_wellFormed U h)
  exact (canon_regulated hv' (withFill U M.asStructure F) (show r ∈ (fill U).T.regulated from hr) vs).symm.trans
    (tabK_sound hu h M F hF _ _ vs b ht)

end Table

/-- `table3_sound`: a definite `table3` entry is the outcome under every checked filling. -/
theorem table3_sound {α : Type u} [DecidableEq α] (U : UDoc) (h : WellFormedU U = true) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true) (F : FiniteFill U α)
    (hF : fillValid U M F = true) (r : Regulated) (hr : r ∈ U.D.T.regulated) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (b : Bool) (ht : table3 U M r.name vs = some b) :
    (outcomeBase (fill U) r.name).eval (M.withFill F) (tupleVal vs) = b := by
  have _ := typed
  have hBU := admissible_of_fillValid U h M valid hb F hF
  have key := (eval_withFill U M F _ _).trans (table3_outcome (uvalid h) h M (finFill M F) hBU hr vs b ht)
  cases hev : (outcomeBase (fill U) r.name).eval (M.withFill F) (tupleVal vs)
  · cases b
    · rfl
    · exact absurd (key.mpr rfl) (by rw [hev]; simp)
  · exact (key.mp hev).symm

/-- `settled_of_table3`: a definite `table3` entry is SETTLED. -/
theorem settled_of_table3 {α : Type u} [DecidableEq α] (U : UDoc) (h : WellFormedU U = true) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt U.D 0)) (hb : backgroundValid U.D M = true) (r : Regulated) (hr : r ∈ U.D.T.regulated)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs) (b : Bool)
    (ht : table3 U M r.name vs = some b) : SettledAs U M.asStructure r vs b := by
  have _ := valid
  have _ := hb
  have _ := typed
  intro F hF
  exact table3_outcome (uvalid h) h M F hF hr vs b ht

end VE.NormDefaults
