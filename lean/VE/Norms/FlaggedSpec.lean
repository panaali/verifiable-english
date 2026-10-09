import VE.Norms.Run

/-! The norms route's CONFLICT-FREE verdict for documents with flags or
definitions, stated against the spec's `ConflictFree` (docs/CONSOLIDATION-PLAN.md
step 1a).

`Flagged.norms_flagged_conflict_sound` concludes Python's `BaseConflictFree`
when a document has a flag or a definition: no conflict formula of `pyTargets`
(earlier regulated atoms expanded, defined atoms kept) holds in a structure
admissible over `baseEnv` (regulated predicates hidden) that satisfies
`baseBackground` (flags, definitions, literals). The spec's `ConflictFree D B`
ranges over `BaseAdmissible D B` (every layer symbol hidden) and expands every
earlier layer symbol (`subst`). This file links the two.

* `conflictFree_of_base` (JSON-free): for a source whose `baseBackground` is
  well formed over `baseEnv` and whose flags name no defined predicate,
  `BaseConflictFree` on every structure admissible over `baseEnv` gives
  `ConflictFree D B` on every base-admissible `B` satisfying the flag premises.
  The proof expands `B` freely (`freeExpansion`: every layer symbol takes its
  expanded meaning in `B`, clashes allowed), hides the regulated symbols again,
  and shows that the regulated-only substitution there agrees with `subst` in
  `B` (`regSubst_base_iff`).
* Two rejection facts make those hypotheses hold on every accepted case:
  a flag on a defined predicate is rejected by the vocabulary decoder
  (`decodeVocabulary_flag_not_defined`, `Route/Wire.lean`'s
  `UnsupportedProfile: Defined predicates cannot carry functional or total
  flags`), and a definition body mentioning a regulated predicate makes every
  conflict certificate fail its premise check over `baseEnv`
  (`conflictFreeCheck_definition_base`). With no targets, `ConflictFree` is
  vacuous (`pyTargets_nil_conflictFree`).
* `norms_flagged_conflict_free`: the replay theorem, for both values of
  `plain`; it is the statement `norms_flagged_witness_sound` refutes.
* `norms_wire_conflict_free` and `norms_wire_conflict_refuted`: the same at the
  public entry `Norms.Run.runCase`, read off the answer's `verdict` field; and
  `norms_wire_conflict_exclusive`: the route never answers CONFLICT-FREE and
  CONFLICT for the same environment and norms. -/
namespace VE.Norms.FlaggedSpec
open Lean
open VE.Norms.Flagged
open VE.Order.ProfileGate (bind_ok)
universe u

/-! ## Names and environments -/

/-- The names of the regulated predicates (hidden in `baseEnv`). -/
def regNames (D : Doc) : List String := D.T.regulated.map (·.name)

theorem baseEnv_predicates (D : Doc) (n : String) :
    (baseEnv D).predicates n = if n ∈ regNames D then none else D.E.predicates n := rfl

theorem regName_layer {D : Doc} (hv : Valid D) {n : String} (hn : n ∈ regNames D) : n ∈ layerNames D.T := by
  obtain ⟨r, hr, rfl⟩ := List.mem_map.mp hn
  obtain ⟨k, hk⟩ := mem_syms_index (hv.regulated r hr)
  exact name_mem_layerNames hk

theorem regName_hidden {D : Doc} (hv : Valid D) : ∀ n ∈ regNames D, (envAt D 0).predicates n = none :=
  fun _ hn => envAt_zero_later (regName_layer hv hn)

theorem baseEnv_hidden (D : Doc) : ∀ n ∈ regNames D, (baseEnv D).predicates n = none := by
  intro n hn
  simp [baseEnv_predicates, hn]

/-- A defined layer symbol is not also regulated: the layer names are distinct. -/
theorem defn_not_regName {D : Doc} (hv : Valid D) {k : Nat} {d : Definition}
    (hk : (syms D.T)[k]? = some (.defn d)) : d.name ∉ regNames D := by
  intro hn
  obtain ⟨r, hr, hrn⟩ := List.mem_map.mp hn
  obtain ⟨j, hj⟩ := mem_syms_index (hv.regulated r hr)
  have hjk := nodup_getElemOpt_inj hv.nodup (names_getElemOpt hj)
    (by show (layerNames D.T)[k]? = some r.name; rw [hrn]; exact names_getElemOpt hk)
  subst hjk
  rw [hj] at hk
  cases hk

/-- Every layer name is a regulated name or the name of a declared definition. -/
theorem layer_cases {D : Doc} {n : String} (hn : n ∈ layerNames D.T) :
    n ∈ regNames D ∨ ∃ d ∈ D.T.definitions, d.name = n := by
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hn
  cases q with
  | reg r => exact Or.inl (List.mem_map.mpr ⟨r, mem_syms_reg hq, rfl⟩)
  | defn d => exact Or.inr ⟨d, mem_syms_defn hq, rfl⟩

/-! ## Typing facts -/

/-- A well-formed formula's predicates are declared. -/
theorem preds_declared {E : VE.Environment} :
    ∀ (a : VE.Formula) (Γ : List String), a.WellFormed E Γ → ∀ p ∈ preds a, E.predicates p ≠ none := by
  intro a
  induction a with
  | top | bottom | eq _ _ => intro _ _ p hp; cases hp
  | unary q t =>
    intro Γ ⟨s, hq, _⟩ p hp
    rw [List.mem_singleton.mp hp, hq]; simp
  | binary q t w =>
    intro Γ ⟨s, s', hq, _⟩ p hp
    rw [List.mem_singleton.mp hp, hq]; simp
  | not a ih => intro Γ h p hp; exact ih Γ h p hp
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ h p hp
    rcases List.mem_append.mp hp with hp | hp
    · exact ia Γ h.1 p hp
    · exact ib Γ h.2 p hp
  | all s a ih | ex s a ih => intro Γ h p hp; exact ih _ h.2 p hp

/-- Typing depends only on the declarations of the predicates a formula mentions. -/
theorem wf_preds_congr {E E' : VE.Environment} (hs : E'.sorts = E.sorts) (hc : E'.constants = E.constants) :
    ∀ (a : VE.Formula), (∀ p ∈ preds a, E'.predicates p = E.predicates p) →
      ∀ Γ, a.WellFormed E Γ → a.WellFormed E' Γ := by
  intro a
  induction a with
  | top | bottom => intro _ _ h; exact h
  | unary q t =>
    intro hp Γ ⟨s, hq, ht⟩
    exact ⟨s, by rw [hp q (List.mem_singleton_self q)]; exact hq, by rw [sortOf_congr hc]; exact ht⟩
  | binary q t w =>
    intro hp Γ ⟨s, s', hq, ht, hw⟩
    exact ⟨s, s', by rw [hp q (List.mem_singleton_self q)]; exact hq,
      by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw⟩
  | eq t w =>
    intro _ Γ ⟨s, ht, hw⟩
    exact ⟨s, by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw⟩
  | not a ih => intro hp Γ h; exact ih hp Γ h
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro hp Γ h
    exact ⟨ia (fun p h' => hp p (List.mem_append_left _ h')) Γ h.1,
      ib (fun p h' => hp p (List.mem_append_right _ h')) Γ h.2⟩
  | all s a ih | ex s a ih => intro hp Γ h; exact ⟨hs ▸ h.1, ih hp _ h.2⟩

theorem bindAll_wellFormed_inv {E : VE.Environment} (body : VE.Formula) :
    ∀ (ss Γ : List String), (bindAll ss body).WellFormed E Γ → body.WellFormed E (ss.reverse ++ Γ)
  | [], Γ, h => h
  | s :: ss, Γ, h => by
    have := bindAll_wellFormed_inv body ss (s :: Γ) h.2
    simpa [List.reverse_cons, List.append_assoc] using this

/-- A definition premise typed over an environment types its body there. -/
theorem definition_body_wellFormed {E : VE.Environment} (d : Definition) (h : d.premise.WellFormed E []) :
    d.body.WellFormed E d.args.reverse := by
  have := bindAll_wellFormed_inv _ d.args [] h
  simpa [iffF] using this.1.2

/-! ## The free expansion of a base structure -/

/-- Every layer symbol interpreted by its expanded meaning evaluated in `B`, on
typed tuples; every other relation is `B`'s. No conflict-freedom is assumed. -/
def freeExpansion (D : Doc) (B : VE.Structure.{u}) : VE.Structure.{u} :=
  { B with relation := fun n vs => match (syms D.T)[idx D.T n]? with
      | some q => if q.name = n then
          VE.TupleTyped B q.sorts vs ∧ (subst D.T (idx D.T n) (q.meaning D.T)).denote B (tupleVal vs)
        else B.relation n vs
      | none => B.relation n vs }

section Expansion
variable {D : Doc} (B : VE.Structure.{u})

theorem freeExpansion_layer (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q) (vs : List B.Carrier) :
    (freeExpansion D B).relation q.name vs ↔
      VE.TupleTyped B q.sorts vs ∧ (subst D.T k (q.meaning D.T)).denote B (tupleVal vs) := by
  have hi : idx D.T q.name = k := idx_eq hv hk
  simp only [freeExpansion, hi, hk, if_true]

theorem freeExpansion_base {n : String} (hn : n ∉ layerNames D.T) (vs : List B.Carrier) :
    (freeExpansion D B).relation n vs ↔ B.relation n vs := by
  simp only [freeExpansion]
  split
  · rename_i q hq
    split
    · rename_i he
      exact absurd (he ▸ name_mem_layerNames hq) hn
    · exact Iff.rfl
  · exact Iff.rfl

theorem freeExpansion_tupleTyped (ss : List String) (vs : List B.Carrier) :
    VE.TupleTyped (freeExpansion D B) ss vs ↔ VE.TupleTyped B ss vs :=
  tupleTyped_relation B _ ss vs

variable {B}

/-- A base formula has the same truth in `B` and in its free expansion. -/
theorem freeExpansion_base_denote (a : VE.Formula) (Γ : List String) (hw : a.WellFormed (envAt D 0) Γ)
    (ρ : VE.Valuation B) : a.denote (freeExpansion D B) ρ ↔ a.denote B ρ :=
  denote_relation_congr (fun _ hr => envAt_zero_later hr) B _
    (fun _ vs hr => freeExpansion_base B hr vs) a Γ ρ hw

theorem freeExpansion_constants (hB : B.Admissible (envAt D 0)) : ConstantsTyped D (freeExpansion D B) :=
  fun c s hc => hB.1 c s hc

/-- Every layer symbol agrees with its meaning in the free expansion. -/
theorem freeExpansion_meaning (hv : Valid D) (hB : B.Admissible (envAt D 0)) :
    ∀ (k : Nat) (q : Sym), (syms D.T)[k]? = some q →
    ∀ vs, VE.TupleTyped (freeExpansion D B) q.sorts vs →
      ((freeExpansion D B).relation q.name vs ↔ (q.meaning D.T).denote (freeExpansion D B) (tupleVal vs)) := by
  intro k
  induction k using Nat.strongRecOn with
  | ind k ih =>
    intro q hk vs hvs
    have ha : AgreesBelow D k (freeExpansion D B) := fun j q' hj hq' => ih j hj q' hq'
    have hw := meaning_wellFormed hv hk
    have hρ := tupleVal_typed (freeExpansion D B) _ vs hvs
    rw [freeExpansion_layer B hv hk vs,
      ← subst_denote hv k _ (freeExpansion_constants hB) ha _ _ hw _ hρ,
      freeExpansion_base_denote _ _ (subst_wellFormed hv k _ _ hw)]
    exact ⟨fun h => h.2, fun h => ⟨(freeExpansion_tupleTyped B _ vs).mp hvs, h⟩⟩

theorem freeExpansion_agrees (hv : Valid D) (hB : B.Admissible (envAt D 0)) (k : Nat) :
    AgreesBelow D k (freeExpansion D B) :=
  fun j q _ hq => freeExpansion_meaning hv hB j q hq

theorem freeExpansion_admissible (hv : Valid D) (hB : B.Admissible (envAt D 0)) :
    (freeExpansion D B).Admissible D.E := by
  refine ⟨fun c s hc => hB.1 c s hc, fun p vs hp => ?_⟩
  by_cases hl : p ∈ layerNames D.T
  · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hl
    obtain ⟨k, hk⟩ := mem_syms_index hq
    obtain ⟨ht, _⟩ := (freeExpansion_layer B hv hk vs).mp hp
    exact ⟨q.sorts, (hv.decl q hq).1, (freeExpansion_tupleTyped B _ vs).mpr ht⟩
  · obtain ⟨ss, hss, ht⟩ := hB.2 p vs ((freeExpansion_base B hl vs).mp hp)
    exact ⟨ss, by rw [envAt_base hl] at hss; exact hss, (freeExpansion_tupleTyped B _ vs).mpr ht⟩

end Expansion

/-! ## The regulated-only substitution -/

theorem regTable_some (T : Tree) : ∀ (k : Nat) (n : String) (F : VE.Formula), regTable T k n = some F →
    ∃ j r, j < k ∧ (syms T)[j]? = some (.reg r) ∧ r.name = n ∧ F = substWith (regTable T j) (outcome T r)
  | 0, _, _, h => by cases h
  | k + 1, n, F, h => by
    cases hq : (syms T)[k]? with
    | none =>
      simp only [regTable, hq] at h
      obtain ⟨j, r, hj, h₁, h₂, h₃⟩ := regTable_some T k n F h
      exact ⟨j, r, Nat.lt_succ_of_lt hj, h₁, h₂, h₃⟩
    | some q =>
      cases q with
      | reg r =>
        simp only [regTable, hq] at h
        split at h
        · rename_i hn
          cases h
          exact ⟨k, r, Nat.lt_succ_self k, hq, hn.symm, rfl⟩
        · obtain ⟨j, r', hj, h₁, h₂, h₃⟩ := regTable_some T k n F h
          exact ⟨j, r', Nat.lt_succ_of_lt hj, h₁, h₂, h₃⟩
      | defn d =>
        simp only [regTable, hq] at h
        obtain ⟨j, r, hj, h₁, h₂, h₃⟩ := regTable_some T k n F h
        exact ⟨j, r, Nat.lt_succ_of_lt hj, h₁, h₂, h₃⟩

theorem regTable_at {D : Doc} (hv : Valid D) : ∀ (k j : Nat) (r : Regulated), j < k →
    (syms D.T)[j]? = some (.reg r) → regTable D.T k r.name = some (substWith (regTable D.T j) (outcome D.T r))
  | 0, _, _, h, _ => absurd h (Nat.not_lt_zero _)
  | k + 1, j, r, hj, hr => by
    rcases Nat.lt_succ_iff_lt_or_eq.mp hj with hj | rfl
    · have ih := regTable_at hv k j r hj hr
      cases hq : (syms D.T)[k]? with
      | none => simp only [regTable, hq]; exact ih
      | some q =>
        have hne : r.name ≠ q.name := by
          intro he
          have := nodup_getElemOpt_inj hv.nodup (names_getElemOpt hr)
            (by show (layerNames D.T)[k]? = some (Sym.reg r).name; rw [show (Sym.reg r).name = q.name from he]
                exact names_getElemOpt hq)
          omega
        cases q with
        | reg r' =>
          simp only [regTable, hq]
          rw [if_neg (by simpa [Sym.name] using hne)]
          exact ih
        | defn d => simp only [regTable, hq]; exact ih
    · simp only [regTable, hr, if_true]

/-- Where the table has no entry, a symbol declared at `E_k` is declared alike in `baseEnv`. -/
theorem regTable_none_base {D : Doc} (hv : Valid D) (k : Nat) :
    ∀ n ss, regTable D.T k n = none → (envAt D k).predicates n = some ss → (baseEnv D).predicates n = some ss := by
  intro n ss hn hp
  by_cases hl : n ∈ layerNames D.T
  · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hl
    obtain ⟨i, hi⟩ := mem_syms_index hq
    by_cases hik : i < k
    · cases q with
      | reg r =>
        rw [show (Sym.reg r).name = r.name from rfl, regTable_at hv k i r hik hi] at hn; cases hn
      | defn d =>
        rw [envAt_earlier hv hi hik] at hp
        rw [baseEnv_predicates, show (Sym.defn d).name = d.name from rfl, if_neg (defn_not_regName hv hi)]
        rw [← hp]; exact (hv.decl _ hq).1
    · rw [envAt_later hv hi (Nat.le_of_not_lt hik)] at hp; cases hp
  · rw [envAt_base hl] at hp
    rw [baseEnv_predicates, if_neg (fun h => hl (regName_layer hv h))]
    exact hp

theorem regTable_wellFormed {D : Doc} (hv : Valid D) (k : Nat) :
    ∀ n F, regTable D.T k n = some F →
      ∃ ss, (envAt D k).predicates n = some ss ∧ F.WellFormed (baseEnv D) ss.reverse := by
  induction k using Nat.strongRecOn with
  | ind k ih =>
    intro n F hF
    obtain ⟨j, r, hj, hr, rfl, rfl⟩ := regTable_some D.T k n F hF
    refine ⟨r.sorts, envAt_earlier hv hr hj, ?_⟩
    exact substWith_wellFormed _ (envAt D j) (baseEnv D) rfl rfl (ih j hj) (regTable_none_base hv j) _ _
      (outcome_wellFormed (rulesTyped_of_valid hv hr))

theorem regSubst_wellFormed {D : Doc} (hv : Valid D) (k : Nat) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt D k) Γ) : (regSubst D.T k φ).WellFormed (baseEnv D) Γ :=
  substWith_wellFormed _ (envAt D k) (baseEnv D) rfl rfl (regTable_wellFormed hv k) (regTable_none_base hv k) φ Γ hφ

theorem regTable_sound {D : Doc} (hv : Valid D) (S : VE.Structure.{u}) (hc : ConstantsTyped D S)
    (k : Nat) (ha : AgreesBelow D k S) :
    ∀ n F, regTable D.T k n = some F → ∃ ss, (envAt D k).predicates n = some ss ∧
      F.WellFormed (baseEnv D) ss.reverse ∧
      ∀ vs, VE.TupleTyped S ss vs → (F.denote S (tupleVal vs) ↔ S.relation n vs) := by
  induction k using Nat.strongRecOn with
  | ind k ih =>
    intro n F hF
    obtain ⟨ss, hss, hFw⟩ := regTable_wellFormed hv k n F hF
    refine ⟨ss, hss, hFw, ?_⟩
    obtain ⟨j, r, hj, hr, rfl, rfl⟩ := regTable_some D.T k n F hF
    rw [show r.name = (Sym.reg r).name from rfl, envAt_earlier hv hr hj] at hss
    cases hss
    intro vs hvs
    exact (substWith_denote _ (envAt D j) (baseEnv D) S hc
      (ih j hj (fun j' q' hj' => ha j' q' (Nat.lt_trans hj' hj))) _ _ _
      (outcome_wellFormed (rulesTyped_of_valid hv hr)) (tupleVal_typed S _ vs hvs)).trans
      (ha j (.reg r) hj hr vs hvs).symm

theorem regSubst_denote {D : Doc} (hv : Valid D) (k : Nat) (S : VE.Structure.{u})
    (hc : ConstantsTyped D S) (ha : AgreesBelow D k S) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt D k) Γ) (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
    (regSubst D.T k φ).denote S ρ ↔ φ.denote S ρ :=
  substWith_denote _ (envAt D k) (baseEnv D) S hc (regTable_sound hv S hc k ha) φ Γ ρ hφ hρ

/-- The structure the link evaluates Python's targets in: the free expansion
with the regulated symbols hidden again. -/
def pyStructure (D : Doc) (B : VE.Structure.{u}) : VE.Structure.{u} :=
  forget (regNames D) (freeExpansion D B)

/-- The two substitutions agree: Python's regulated-only expansion in
`pyStructure` and the spec's full expansion in `B`. -/
theorem regSubst_base_iff {D : Doc} (hv : Valid D) {B : VE.Structure.{u}} (hB : B.Admissible (envAt D 0))
    (k : Nat) (φ : VE.Formula) (Γ : List String) (hφ : φ.WellFormed (envAt D k) Γ)
    (ρ : VE.Valuation B) (hρ : VE.Valuation.Typed B Γ ρ) :
    (regSubst D.T k φ).denote (pyStructure D B) ρ ↔ (subst D.T k φ).denote B ρ := by
  have hc := freeExpansion_constants hB
  have ha := freeExpansion_agrees hv hB k
  unfold pyStructure
  rw [denote_forget (baseEnv_hidden D) (freeExpansion D B) _ Γ ρ (regSubst_wellFormed hv k φ Γ hφ),
    regSubst_denote hv k _ hc ha φ Γ hφ ρ hρ, ← subst_denote hv k _ hc ha φ Γ hφ ρ hρ,
    freeExpansion_base_denote _ Γ (subst_wellFormed hv k φ Γ hφ)]

/-! ## The JSON-free link -/

theorem conflictPy_iff {D : Doc} (hv : Valid D) {B : VE.Structure.{u}} (hB : B.Admissible (envAt D 0))
    {k : Nat} {r : Regulated} (hk : (syms D.T)[k]? = some (.reg r)) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (conflictPy D r).denote (pyStructure D B) (tupleVal vs) ↔ (conflict D r).denote B (tupleVal vs) := by
  have hb : before D r.name = k := before_eq hv hk
  have hρ := tupleVal_typed B _ vs hvs
  simp only [conflictPy, conflict, hb, VE.Formula.denote]
  rw [regSubst_base_iff hv hB k (pos D.T r.name) _ (decides_wellFormed (rulesTyped_of_valid hv hk) true) _ hρ,
    regSubst_base_iff hv hB k (neg D.T r.name) _ (decides_wellFormed (rulesTyped_of_valid hv hk) false) _ hρ]

theorem outcomePy_iff {D : Doc} (hv : Valid D) {B : VE.Structure.{u}} (hB : B.Admissible (envAt D 0))
    {k : Nat} {r : Regulated} (hk : (syms D.T)[k]? = some (.reg r)) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (outcomePy D r.name).denote (pyStructure D B) (tupleVal vs) ↔
      (outcomeBase D r.name).denote B (tupleVal vs) := by
  have hb : before D r.name = k := before_eq hv hk
  simp only [outcomePy, outcomeBase, find_regulated hv hk, hb]
  exact regSubst_base_iff hv hB k _ _ (outcome_wellFormed (rulesTyped_of_valid hv hk)) _
    (tupleVal_typed B _ vs hvs)

theorem pairConflictPy_iff {D : Doc} (hv : Valid D) {B : VE.Structure.{u}} (hB : B.Admissible (envAt D 0))
    {pr : Pair} (hpr : pr ∈ pairs D.T) (vs : List B.Carrier) (hvs : VE.TupleTyped B pr.sorts vs) :
    (pairConflictPy D pr).denote (pyStructure D B) (tupleVal vs) ↔
      (pairConflict D pr).denote B (tupleVal vs) := by
  obtain ⟨_, ⟨i, r, hi, hrn, hrs, _⟩, ⟨j, m, hj, hmn, hms, _⟩⟩ := pair_members hv hpr
  simp only [pairConflictPy, pairConflict, VE.Formula.denote]
  rw [← hrn, ← hmn, outcomePy_iff hv hB hi vs (hrs ▸ hvs), outcomePy_iff hv hB hj vs (hms ▸ hvs)]

theorem pyStructure_tupleTyped (D : Doc) (B : VE.Structure.{u}) (ss : List String) (vs : List B.Carrier) :
    VE.TupleTyped (pyStructure D B) ss vs ↔ VE.TupleTyped B ss vs :=
  tupleTyped_relation B _ ss vs

theorem pyStructure_admissible {D : Doc} (hv : Valid D) {B : VE.Structure.{u}} (hB : B.Admissible (envAt D 0)) :
    (pyStructure D B).Admissible (baseEnv D) :=
  forget_admissible D.E (regNames D) _ (freeExpansion_admissible hv hB)

/-- Flag premises typed over `baseEnv` are typed over the base vocabulary when no
flag names a defined predicate. -/
theorem flag_premise_base (src : Wire.Source)
    (hflag : ∀ f ∈ src.ne.rv.flags, ∀ d ∈ src.D.T.definitions, f.name ≠ d.name) :
    ∀ a ∈ flagPremises src, a.WellFormed (baseEnv src.D) [] → a.WellFormed (envAt src.D 0) [] := by
  intro a ha hw
  obtain ⟨f, hf, ha⟩ := List.mem_flatMap.mp ha
  have hpreds : ∀ p ∈ preds a, p = f.name := by
    intro p hp
    simp only [VE.Data.Background.premises, List.mem_append] at ha
    rcases ha with ha | ha
    · split at ha
      · rw [List.mem_singleton.mp ha] at hp
        simp [VE.Data.Background.functionalPremise, preds] at hp
        exact hp
      · cases ha
    · split at ha
      · rw [List.mem_singleton.mp ha] at hp
        simp [VE.Data.Background.totalPremise, preds] at hp
        exact hp
      · cases ha
  refine wf_preds_congr (E := baseEnv src.D) (E' := envAt src.D 0) rfl rfl a ?_ [] hw
  intro p hp
  have hpf := hpreds p hp
  have hdecl := preds_declared a [] hw p hp
  have hreg : p ∉ regNames src.D := fun h => hdecl (baseEnv_hidden src.D p h)
  have hl : p ∉ layerNames src.D.T := by
    intro hl
    rcases layer_cases hl with h | ⟨d, hd, hdn⟩
    · exact hreg h
    · exact hflag f hf d hd (hpf ▸ hdn.symm)
  rw [envAt_base hl, baseEnv_predicates, if_neg hreg]

theorem sat_literals_relation (lits : List String) (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop) :
    Sat { S with relation := R } (VE.Route.Background.literals lits) ↔ Sat S (VE.Route.Background.literals lits) := by
  simp only [Sat, VE.Route.Background.literals, List.mem_map, forall_exists_index, and_imp,
    forall_apply_eq_imp_iff₂, VE.Route.Background.literalPremise_denote]

/-- `pyStructure` satisfies Python's base Background whenever `B` satisfies the
literals and the flag premises. -/
theorem pyStructure_background (src : Wire.Source) {B : VE.Structure.{u}} (hB : BaseAdmissible src.D B)
    (hF : Sat B (flagPremises src))
    (hbg : ∀ a ∈ baseBackground src, a.WellFormed (baseEnv src.D) [])
    (hflag : ∀ f ∈ src.ne.rv.flags, ∀ d ∈ src.D.T.definitions, f.name ≠ d.name) :
    Sat (pyStructure src.D B) (baseBackground src) := by
  have hv := valid_of_wellFormed src.D src.wf
  intro a ha
  simp only [baseBackground, List.mem_append] at ha
  rcases ha with (ha | ha) | ha
  · have hw := flag_premise_base src hflag a ha (hbg a (by simp [baseBackground, ha]))
    unfold pyStructure
    rw [denote_forget (regName_hidden hv) (freeExpansion src.D B) a [] [] hw,
      freeExpansion_base_denote a [] hw]
    exact hF a ha
  · obtain ⟨q, hq, hqa⟩ := List.mem_filterMap.mp ha
    cases q with
    | reg _ => cases hqa
    | defn d =>
      cases hqa
      obtain ⟨k, hk⟩ := mem_syms_index hq
      have hbody := definition_body_wellFormed d (hbg d.premise (by simp [baseBackground, ha]))
      rw [definition_premise_iff d (sym_arity hv hk)]
      intro vs hvs
      have hvs' := (pyStructure_tupleTyped src.D B _ vs).mp hvs
      unfold pyStructure
      rw [forget_relation _ (defn_not_regName hv hk),
        denote_forget (baseEnv_hidden src.D) (freeExpansion src.D B) _ _ _ hbody]
      exact freeExpansion_meaning hv hB.1 k (.defn d) hk vs ((freeExpansion_tupleTyped B _ vs).mpr hvs')
  · unfold pyStructure
    exact ((sat_literals_forget src.D.lits (regNames src.D) (freeExpansion src.D B)).mpr
      ((sat_literals_relation src.D.lits B _).mpr hB.2)) a ha

/-- (α) The JSON-free link: for a source whose `baseBackground` is well formed
over `baseEnv` and whose flags name no defined predicate, Python's
`BaseConflictFree` on every structure admissible over `baseEnv` gives the
spec's `ConflictFree` on every base-admissible structure satisfying the flag
premises. -/
theorem conflictFree_of_base (src : Wire.Source)
    (hbg : ∀ a ∈ baseBackground src, a.WellFormed (baseEnv src.D) [])
    (hflag : ∀ f ∈ src.ne.rv.flags, ∀ d ∈ src.D.T.definitions, f.name ≠ d.name)
    (hbase : ∀ S : VE.Structure.{u}, S.Admissible (baseEnv src.D) → Sat S (baseBackground src) →
      BaseConflictFree src S) :
    ∀ B : VE.Structure.{u}, BaseAdmissible src.D B → Sat B (flagPremises src) → ConflictFree src.D B := by
  intro B hB hF
  have hv := valid_of_wellFormed src.D src.wf
  have hpy := hbase _ (pyStructure_admissible hv hB.1) (pyStructure_background src hB hF hbg hflag)
  refine ⟨fun r hr vs hvs hc => ?_, fun pr hpr vs hvs hc => ?_⟩
  · obtain ⟨k, hk⟩ := mem_syms_index (hv.regulated r hr)
    have ht : (r.name, r.sorts, conflictPy src.D r) ∈ pyTargets src.D :=
      List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, List.mem_of_getElem? hk, rfl⟩)
    exact hpy _ ht vs ((pyStructure_tupleTyped src.D B _ vs).mpr hvs)
      ((conflictPy_iff hv hB.1 hk vs hvs).mpr hc)
  · have ht : (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflictPy src.D pr) ∈ pyTargets src.D :=
      List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)
    exact hpy _ ht vs ((pyStructure_tupleTyped src.D B _ vs).mpr hvs)
      ((pairConflictPy_iff hv hB.1 hpr vs hvs).mpr hc)

/-! ## Rejection (a): flags never name a defined predicate -/

theorem mapM_ok_mem {α β ε : Type} {f : α → Except ε β} :
    ∀ {xs : List α} {ys : List β}, xs.mapM f = .ok ys → ∀ y ∈ ys, ∃ x ∈ xs, f x = .ok y
  | [], ys, h, y, hy => by
    simp only [List.mapM_nil] at h
    cases h
    cases hy
  | x :: xs, ys, h, y, hy => by
    rw [List.mapM_cons] at h
    obtain ⟨b, hb, h⟩ := bind_ok h
    obtain ⟨bs, hbs, h⟩ := bind_ok h
    cases h
    rcases List.mem_cons.mp hy with rfl | hy
    · exact ⟨x, List.mem_cons_self, hb⟩
    · obtain ⟨x', hx', hf⟩ := mapM_ok_mem hbs y hy
      exact ⟨x', List.mem_cons_of_mem _ hx', hf⟩

theorem filterMapM_ok_mem {α β ε : Type} {f : α → Except ε (Option β)} :
    ∀ {xs : List α} {ys : List β}, xs.filterMapM f = .ok ys → ∀ y ∈ ys, ∃ x ∈ xs, f x = .ok (some y)
  | [], ys, h, y, hy => by
    simp only [List.filterMapM_nil] at h
    cases h
    cases hy
  | x :: xs, ys, h, y, hy => by
    rw [List.filterMapM_cons] at h
    obtain ⟨b, hb, h⟩ := bind_ok h
    cases b with
    | none =>
      obtain ⟨x', hx', hf⟩ := filterMapM_ok_mem h y hy
      exact ⟨x', List.mem_cons_of_mem _ hx', hf⟩
    | some b =>
      obtain ⟨bs, hbs, h⟩ := bind_ok h
      cases h
      rcases List.mem_cons.mp hy with rfl | hy
      · exact ⟨x, List.mem_cons_self, hb⟩
      · obtain ⟨x', hx', hf⟩ := filterMapM_ok_mem hbs y hy
        exact ⟨x', List.mem_cons_of_mem _ hx', hf⟩

theorem eraseDups_length_le {α : Type} [BEq α] :
    ∀ (n : Nat) (l : List α), l.length ≤ n → l.eraseDups.length ≤ l.length
  | _, [], _ => by simp
  | 0, _ :: _, h => by simp at h
  | n + 1, a :: as, h => by
    rw [List.eraseDups_cons]
    have h2 := List.length_filter_le (fun b => !b == a) as
    have h1 := eraseDups_length_le n (as.filter fun b => !b == a) (by simp at h; omega)
    simp only [List.length_cons]
    omega

theorem nodup_of_eraseDups_length {α : Type} [BEq α] [LawfulBEq α] :
    ∀ (n : Nat) (l : List α), l.length ≤ n → l.eraseDups.length = l.length → l.Nodup
  | _, [], _, _ => List.nodup_nil
  | 0, _ :: _, h, _ => by simp at h
  | n + 1, a :: as, hl, h => by
    rw [List.eraseDups_cons, List.length_cons, List.length_cons] at h
    have hf := List.length_filter_le (fun b => !b == a) as
    have hle := eraseDups_length_le (as.filter fun b => !b == a).length (as.filter fun b => !b == a) (Nat.le_refl _)
    have hfe : (as.filter fun b => !b == a).length = as.length := by omega
    have hall := List.length_filter_eq_length_iff.mp hfe
    have heq : as.filter (fun b => !b == a) = as := List.filter_eq_self.mpr hall
    refine List.nodup_cons.mpr ⟨fun ha => by simpa using hall a ha, ?_⟩
    have := nodup_of_eraseDups_length n (as.filter fun b => !b == a) (by simp at hl; omega) (by omega)
    rwa [heq] at this

theorem nodup_fst_unique {α β : Type} : ∀ {l : List (α × β)} {a : α} {b c : β},
    (l.map Prod.fst).Nodup → (a, b) ∈ l → (a, c) ∈ l → b = c
  | [], _, _, _, _, hb, _ => by cases hb
  | x :: l, a, b, c, hn, hb, hc => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp hb with hb | hb <;> rcases List.mem_cons.mp hc with hc | hc
    · rw [← hb] at hc; cases hc; rfl
    · exact absurd (List.mem_map.mpr ⟨_, hc, by rw [← hb]⟩) hn.1
    · exact absurd (List.mem_map.mpr ⟨_, hb, by rw [← hc]⟩) hn.1
    · exact nodup_fst_unique hn.2 hb hc

theorem finish_eq {E : VE.Environment} {l ds : List VE.Definitions.Def}
    (h : VE.Definitions.finish E l = .ok ds) : ds = l := by
  unfold VE.Definitions.finish at h
  cases hb : VE.Definitions.firstBad E l with
  | none => rw [hb] at h; cases h; rfl
  | some x => rw [hb] at h; cases h

theorem elaborate_names (E : VE.Environment) (entries : List (String × List String × VE.Formula))
    (ds : List VE.Definitions.Def) (h : VE.Definitions.elaborate E entries = .ok ds) :
    ∀ d ∈ ds, ∃ e ∈ entries, d.name = e.1 := by
  unfold VE.Definitions.elaborate at h
  split at h
  · cases h
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨order, _, h⟩ := bind_ok h
    rw [finish_eq h]
    intro d hd
    obtain ⟨p, _, hp⟩ := List.mem_filterMap.mp hd
    obtain ⟨e, he, hed⟩ := Option.map_eq_some_iff.mp hp
    obtain ⟨n, ss, b⟩ := e
    cases hed
    exact ⟨_, List.mem_of_find?_eq_some he, rfl⟩

theorem decodeDefined_name {p : String} {ss : List String} {payload : Json}
    {e : String × List String × VE.Formula} (h : VE.Route.Wire.decodeDefined p ss payload = .ok e) : e.1 = p := by
  unfold VE.Route.Wire.decodeDefined at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    cases h
    rfl
  · cases h

/-- Rejection (a): the vocabulary decoder never yields a flag on a defined
predicate (`UnsupportedProfile: Defined predicates cannot carry functional or
total flags`, `Route/Wire.lean`). The flag's entry has no `defined` member, every
definition comes from an entry that has one, and predicate names are distinct
(the `duplicate declaration` check). -/
theorem decodeVocabulary_flag_not_defined (profiles : List String) (v : Json) (rv : VE.Route.Wire.RouteVocabulary)
    (h : VE.Route.Wire.decodeVocabulary profiles v = .ok rv) :
    ∀ f ∈ rv.flags, ∀ d ∈ rv.definitions, f.name ≠ d.name := by
  unfold VE.Route.Wire.decodeVocabulary at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨sorts, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨predicates, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨constants, _, h⟩ := bind_ok h
  split at h
  case isTrue => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  extract_lets names sortNames allowed flagged jpA jpB at h
  split at h
  case isFalse => cases h
  rename_i hnames
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpA] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨psAndFlags, hps, h⟩ := bind_ok h
  extract_lets ps flags at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨cs, _, h⟩ := bind_ok h
  extract_lets literals result jpC at h
  split at h
  case isTrue => cases h
  dsimp (config := { zeta := false }) only [jpC] at h
  split at h
  case isFalse => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨entries, hentries, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  split at h
  case h_2 => cases h
  rename_i ds hds
  cases h
  -- the predicate names are distinct
  have hnd : names.Nodup := nodup_of_eraseDups_length _ names (Nat.le_refl _) (by simpa using hnames)
  have hsub : (predicates.map Prod.fst).Sublist names := by
    simp only [names, List.map_append]
    exact (List.sublist_append_right _ _).trans (List.sublist_append_left _ _)
  have hkeys := hnd.sublist hsub
  intro f hf d hd hfd
  -- the flag's entry carries no `defined`
  obtain ⟨y, hy, hyf⟩ := List.mem_filterMap.mp (show f ∈ List.filterMap Prod.snd psAndFlags from hf)
  obtain ⟨⟨p, entry⟩, hx, hF⟩ := mapM_ok_mem hps y hy
  obtain ⟨⟨p0, ss0⟩, fl⟩ := y
  simp only at hyf
  subst hyf
  have hflag : (entry.getObjVal? "defined").isOk = false ∧ f.name = p := by
    dsimp (config := { zeta := false }) only at hF
    extract_lets defined jpE at hF
    split at hF
    case isTrue => cases hF
    rename_i hcond
    dsimp (config := { zeta := false }) only [jpE] at hF
    obtain ⟨_, _, hF⟩ := bind_ok hF
    obtain ⟨_, _, hF⟩ := bind_ok hF
    obtain ⟨_, _, hF⟩ := bind_ok hF
    obtain ⟨_, _, hF⟩ := bind_ok hF
    obtain ⟨_, _, hF⟩ := bind_ok hF
    obtain ⟨ss2, _, hF⟩ := bind_ok hF
    extract_lets jpS jpF at hF
    split at hF
    case isFalse => cases hF
    dsimp (config := { zeta := false }) only [jpF] at hF
    obtain ⟨_, _, hF⟩ := bind_ok hF
    have tail : ∀ fv, jpS fv = .ok ((p0, ss0), some f) →
        f.name = p ∧ (fv = true ∨ ∃ b, entry.getObjVal? "total" = .ok b) := by
      intro fv hS
      dsimp (config := { zeta := false }) only [jpS] at hS
      extract_lets jpT at hS
      have tail2 : ∀ tv, jpT tv = .ok ((p0, ss0), some f) → f.name = p ∧ (fv = true ∨ tv = true) := by
        intro tv hT
        dsimp (config := { zeta := false }) only [jpT] at hT
        extract_lets flag jpG at hT
        have fin : jpG () = .ok ((p0, ss0), some f) → f.name = p ∧ (fv = true ∨ tv = true) := by
          intro hG
          dsimp (config := { zeta := false }) only [jpG] at hG
          have hinj := Except.ok.inj hG
          simp only [Prod.mk.injEq] at hinj
          have hfl := hinj.2
          simp only [flag] at hfl
          split at hfl
          · rename_i hor
            cases hfl
            exact ⟨rfl, by simpa using hor⟩
          · cases hfl
        split at hT
        · split at hT
          · obtain ⟨_, _, hT⟩ := bind_ok hT; exact fin hT
          · cases hT
        · obtain ⟨_, _, hT⟩ := bind_ok hT; exact fin hT
      split at hS
      · rename_i b htk
        obtain ⟨tv, _, hS⟩ := bind_ok hS
        exact ⟨(tail2 tv hS).1, Or.inr ⟨b, htk⟩⟩
      · obtain ⟨tv, htv, hS⟩ := bind_ok hS
        cases htv
        obtain ⟨hn, hor⟩ := tail2 false hS
        exact ⟨hn, Or.inl (by simpa using hor)⟩
    split at hF
    · rename_i b hfk
      obtain ⟨fv, _, hF⟩ := bind_ok hF
      refine ⟨?_, (tail fv hF).1⟩
      cases hd : (entry.getObjVal? "defined").isOk
      · rfl
      · exact absurd (by rw [hd]; simp [hfk, Except.isOk, Except.toBool]) hcond
    · obtain ⟨fv, hfv, hF⟩ := bind_ok hF
      cases hfv
      obtain ⟨hn, hor⟩ := tail false hF
      refine ⟨?_, hn⟩
      rcases hor with hor | ⟨b, htk⟩
      · cases hor
      · cases hd : (entry.getObjVal? "defined").isOk
        · rfl
        · exact absurd (by rw [hd]; simp [htk, Except.isOk, Except.toBool]) hcond
  obtain ⟨hdefined, hname⟩ := hflag
  obtain ⟨e, he, hde⟩ := elaborate_names _ entries ds hds d hd
  obtain ⟨⟨p2, entry2⟩, hx2, hG⟩ := filterMapM_ok_mem hentries e he
  have hdef2 : (entry2.getObjVal? "defined").isOk = true ∧ e.1 = p2 := by
    dsimp (config := { zeta := false }) only at hG
    split at hG
    · rename_i payload hpay
      obtain ⟨_, _, hG⟩ := bind_ok hG
      obtain ⟨ss, _, hG⟩ := bind_ok hG
      cases hdd : VE.Route.Wire.decodeDefined p2 ss payload with
      | error err => rw [hdd] at hG; cases hG
      | ok e' =>
        rw [hdd] at hG
        cases hG
        exact ⟨by rw [hpay]; rfl, decodeDefined_name hdd⟩
    · cases hG
  have hp : p = p2 := by rw [← hname, hfd, hde, hdef2.2]
  subst hp
  have := nodup_fst_unique hkeys hx hx2
  subst this
  rw [hdefined] at hdef2
  cases hdef2.1


theorem normsEnvironment_flag_not_defined (environment : Json) (ne : VE.Norms.Wire.NormsEnvironment)
    (h : VE.Norms.Wire.decodeNormsEnvironment environment = .ok ne) :
    ∀ f ∈ ne.rv.flags, ∀ d ∈ ne.rv.definitions, f.name ≠ d.name := by
  unfold VE.Norms.Wire.decodeNormsEnvironment at h
  obtain ⟨e, _, h⟩ := bind_ok h
  extract_lets vocab jpX jpY at h
  split at h
  case isFalse => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpY] at h
  split at h
  case isFalse => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpX] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  extract_lets vocab2 at h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  extract_lets jpZ at h
  split at h
  case isTrue => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpZ] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  exact decodeVocabulary_flag_not_defined _ _ rv hrv

/-- Rejection (a) for a decoded norm source: no flag names one of its definitions. -/
theorem decodeSource_flag_not_defined (environment norms : Json) (flags : Bool) (src : VE.Norms.Wire.Source)
    (h : VE.Norms.Wire.decodeSource environment norms flags = .ok src) :
    ∀ f ∈ src.ne.rv.flags, ∀ d ∈ src.D.T.definitions, f.name ≠ d.name := by
  unfold VE.Norms.Wire.decodeSource at h
  obtain ⟨ne, hne, h⟩ := bind_ok h
  extract_lets defs jpU jpA jpB at h
  split at h
  case isFalse => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpB] at h
  split at h
  case isFalse => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpA] at h
  split at h
  case h_2 => cases h
  obtain ⟨units, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpU] at h
  extract_lets jpN at h
  split at h
  case isTrue => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpN] at h
  obtain ⟨nodes, _, h⟩ := bind_ok h
  extract_lets D at h
  split at h
  · cases h
  · cases h
    intro f hf d hd
    obtain ⟨d', hd', rfl⟩ := List.mem_map.mp hd
    exact normsEnvironment_flag_not_defined _ ne hne f hf d' hd'

/-! ## Rejection (b) and the empty-target case -/

/-- One accepted conflict certificate types the whole base Background over
`baseEnv`: the checker requires every premise to check (`TableauChecker.lean`). -/
theorem conflictFreeCheck_background {src : Wire.Source} {certs : List (Option VE.Tableau.Certificate)}
    (hc : Flagged.conflictFreeCheck src certs = true) {t : String × List String × VE.Formula}
    (ht : t ∈ pyTargets src.D) : ∀ a ∈ baseBackground src, a.WellFormed (baseEnv src.D) [] := by
  obtain ⟨c, hcc⟩ := Flagged.conflictFreeCheck_target hc ht
  intro a ha
  unfold VE.Tableau.checkCertificate at hcc
  simp only [Bool.and_eq_true, List.all_eq_true] at hcc
  exact (VE.check_iff_wellFormed _ _ _).mp (hcc.1.1.2 a ha)

/-- Rejection (b): when the case has a target, an accepted conflict check means
no definition body mentions a regulated predicate (such a body is not typed over
`baseEnv`, so every certificate fails its premise check). -/
theorem conflictFreeCheck_definition_base {src : Wire.Source} {certs : List (Option VE.Tableau.Certificate)}
    (hc : Flagged.conflictFreeCheck src certs = true) (hne : pyTargets src.D ≠ []) {d : Definition}
    (hd : Sym.defn d ∈ syms src.D.T) :
    d.body.WellFormed (baseEnv src.D) d.args.reverse ∧ ∀ p ∈ preds d.body, p ∉ regNames src.D := by
  obtain ⟨t, ht⟩ := List.exists_mem_of_ne_nil _ hne
  have hw := conflictFreeCheck_background hc ht d.premise
    (List.mem_append_left _ (List.mem_append_right _ (List.mem_filterMap.mpr ⟨.defn d, hd, rfl⟩)))
  have hb := definition_body_wellFormed d hw
  exact ⟨hb, fun p hp hreg => preds_declared _ _ hb p hp (baseEnv_hidden _ p hreg)⟩

/-- With no targets (no regulated predicate and no pair), `ConflictFree` is vacuous. -/
theorem pyTargets_nil_conflictFree (src : Wire.Source) (ht : pyTargets src.D = []) (B : VE.Structure.{u}) :
    ConflictFree src.D B := by
  have hv := valid_of_wellFormed src.D src.wf
  refine ⟨fun r hr => ?_, fun pr hpr => ?_⟩
  · have hm : (r.name, r.sorts, conflictPy src.D r) ∈ pyTargets src.D :=
      List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)
    rw [ht] at hm; cases hm
  · have hm : (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflictPy src.D pr) ∈ pyTargets src.D :=
      List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)
    rw [ht] at hm; cases hm

/-! ## The replay theorem -/

/-- (β) `norms_flagged_conflict_free`: a successful raw conflict replay whose
every target certificate is accepted gives, for the document decoded from that
very input, the spec's conflict-freedom over every base-admissible structure
satisfying the flag premises, whether or not the document has flags or
definitions. This is the statement `norms_flagged_witness_sound` refutes. -/
theorem norms_flagged_conflict_free (j : Json) (r : ConflictReplay)
    (h : replayConflict j = .ok r) (hv : r.conflictFree = true) :
    Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok r.src ∧
    ∀ B : VE.Structure.{u}, BaseAdmissible r.src.D B → Sat B (flagPremises r.src) → ConflictFree r.src.D B := by
  obtain ⟨hd, hplain, hflagged⟩ := norms_flagged_conflict_sound.{u} j r h hv
  refine ⟨hd, fun B hB hF => ?_⟩
  cases hp : r.plain
  · have hc := conflictFree_flagged r hv hp
    by_cases ht : pyTargets r.src.D = []
    · exact pyTargets_nil_conflictFree r.src ht B
    · obtain ⟨t, htm⟩ := List.exists_mem_of_ne_nil _ ht
      exact conflictFree_of_base r.src (conflictFreeCheck_background hc htm)
        (decodeSource_flag_not_defined _ _ _ r.src hd) (hflagged hp) B hB hF
  · exact hplain hp B hB

/-! ## The public entry -/

theorem verdict_witness (id v : String) (a b : Json) :
    (VE.Route.Wire.ok id [("verdict", .str v), ("target", a), ("targets", b)]).getObjValD "verdict" = .str v :=
  rfl

theorem verdict_conflict (id v : String) (t : Json) (rest : List (String × Json))
    (hrest : rest = [] ∨ ∃ d, rest = [("detail", .str d)]) :
    (VE.Route.Wire.ok id ([("verdict", .str v), ("targets", t)] ++ rest)).getObjValD "verdict" = .str v := by
  rcases hrest with rfl | ⟨d, rfl⟩ <;> rfl

/-- The two `norms-conflict` branches of `Norms.Run.runCase`: with a witness
the verdict is the witness replay's, otherwise the certificate replay's. -/
theorem runCase_conflict (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-conflict") :
    (∃ (src : Wire.Source) (w : Witness src), replayWitness j = .ok ⟨src, w⟩ ∧
      answer.getObjValD "verdict" = .str (if w.conflict then "CONFLICT" else "UNKNOWN")) ∨
    (∃ r, replayConflict j = .ok r ∧
      answer.getObjValD "verdict" = .str (if r.conflictFree then "CONFLICT-FREE" else "UNKNOWN")) := by
  unfold Run.runCase at h
  obtain ⟨id, _, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "norms-conflict" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [show ("norms-conflict" == "admission") = false from rfl,
    show ("norms-conflict" == "norms-elaborate") = false from rfl,
    show ("norms-conflict" == "norms-certificate") = false from rfl,
    beq_self_eq_true, Bool.false_and, Bool.true_and, Bool.false_eq_true, ↓reduceIte] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h
  · obtain ⟨⟨src, w⟩, hw, h⟩ := bind_ok h
    cases h
    exact Or.inl ⟨src, w, hw, verdict_witness _ _ _ _⟩
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨r, hr, h⟩ := bind_ok h
    cases h
    refine Or.inr ⟨r, hr, verdict_conflict _ _ _ _ ?_⟩
    split
    · split
      · exact Or.inl rfl
      · exact Or.inr ⟨_, rfl⟩
    · exact Or.inl rfl

/-- (γ) `norms_wire_conflict_free`: at the public entry, a `norms-conflict`
answer whose `verdict` is `CONFLICT-FREE` means, for the document decoded from
the case's own environment and norms, the spec's conflict-freedom over every
base-admissible structure satisfying the flag premises. -/
theorem norms_wire_conflict_free (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-conflict")
    (hverdict : answer.getObjValD "verdict" = .str "CONFLICT-FREE") :
    ∃ src : Wire.Source,
      Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok src ∧
      ∀ B : VE.Structure.{u}, BaseAdmissible src.D B → Sat B (flagPremises src) → ConflictFree src.D B := by
  rcases runCase_conflict j answer h hk with ⟨src, w, _, hv⟩ | ⟨r, hr, hv⟩
  · rw [hv] at hverdict
    split at hverdict <;> simp at hverdict
  · rw [hv] at hverdict
    split at hverdict
    · rename_i hcf
      exact ⟨r.src, norms_flagged_conflict_free j r hr hcf⟩
    · simp at hverdict

/-- The witness side at the public entry: a `norms-conflict` answer whose
`verdict` is `CONFLICT` refutes conflict-freedom over the base-admissible
structures satisfying the flag premises, for the decoded document. -/
theorem norms_wire_conflict_refuted (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "norms-conflict")
    (hverdict : answer.getObjValD "verdict" = .str "CONFLICT") :
    ∃ src : Wire.Source,
      Wire.decodeSource (j.getObjValD "environment") (j.getObjValD "norms") (flags := true) = .ok src ∧
      ¬ ∀ B : VE.Structure.{0}, BaseAdmissible src.D B → Sat B (flagPremises src) → ConflictFree src.D B := by
  rcases runCase_conflict j answer h hk with ⟨src, w, hw, hv⟩ | ⟨r, _, hv⟩
  · rw [hv] at hverdict
    split at hverdict
    · rename_i hc
      obtain ⟨hd, _, _, _, hn⟩ := norms_flagged_witness_sound j src w hw hc
      exact ⟨src, hd, hn⟩
    · simp at hverdict
  · rw [hv] at hverdict
    split at hverdict <;> simp at hverdict

/-- The route never answers CONFLICT-FREE and CONFLICT for one document: two
`norms-conflict` cases with the same environment and norms. -/
theorem norms_wire_conflict_exclusive (j₁ j₂ a₁ a₂ : Json)
    (h₁ : Run.runCase j₁ = .ok a₁) (hk₁ : VE.Route.Run.caseKind j₁ = .ok "norms-conflict")
    (h₂ : Run.runCase j₂ = .ok a₂) (hk₂ : VE.Route.Run.caseKind j₂ = .ok "norms-conflict")
    (he : j₁.getObjValD "environment" = j₂.getObjValD "environment")
    (hn : j₁.getObjValD "norms" = j₂.getObjValD "norms")
    (hv₁ : a₁.getObjValD "verdict" = .str "CONFLICT-FREE") :
    a₂.getObjValD "verdict" ≠ .str "CONFLICT" := by
  intro hv₂
  obtain ⟨s₁, hd₁, hc⟩ := norms_wire_conflict_free.{0} j₁ a₁ h₁ hk₁ hv₁
  obtain ⟨s₂, hd₂, hr⟩ := norms_wire_conflict_refuted j₂ a₂ h₂ hk₂ hv₂
  rw [he, hn, hd₂] at hd₁
  cases hd₁
  exact hr hc

end VE.Norms.FlaggedSpec
