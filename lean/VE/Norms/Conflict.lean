import VE.Norms.Prefix

/-! Conflict-freedom and unique expansion (docs/spec/norms.md 5 and 6.2).

* `ConflictFreeAtIdx D k S₀` is the local test on an interpreted prefix below
  the `k`-th layer symbol: no opposite selections, and every pair closing there
  is respected with the earlier member read from `S₀`'s actual relation.
* `local_expands` (and its spec form `conflictFree_expands`): an admissible
  prefix has exactly one admissible expansion by the next symbol iff it passes
  the local test. This is the `expands` field of each P0 `Layer`.
* `ConflictFree D B` is the base-level property over outcome-substituted
  formulas; `conflictFree_expands_document` is the pointwise iff over base
  structures and `conflictFree_expands_all` its universal form.
* `conflict_witness_sound` and `conflict_pair_witness_sound`: a checked finite
  base witness refutes the document property. -/
namespace VE.Norms
open VE.Route (Unique)
universe u

theorem unique_congr {α : Sort _} {P Q : α → Prop} (h : ∀ x, P x ↔ Q x) : Unique P ↔ Unique Q :=
  ⟨fun ⟨x, hx, hu⟩ => ⟨x, (h x).mp hx, fun y hy => hu y ((h y).mpr hy)⟩,
   fun ⟨x, hx, hu⟩ => ⟨x, (h x).mpr hx, fun y hy => hu y ((h y).mp hy)⟩⟩

/-- Truth ignores relations that agree off the symbols a formula cannot mention. -/
theorem denote_relation_congr {E : VE.Environment} {ns : List String}
    (hn : ∀ r ∈ ns, E.predicates r = none) (S : VE.Structure.{u})
    (R : String → List S.Carrier → Prop) (hR : ∀ r vs, r ∉ ns → (R r vs ↔ S.relation r vs))
    (a : VE.Formula) (Γ : List String) (ρ : VE.Valuation S) (hw : a.WellFormed E Γ) :
    a.denote { S with relation := R } ρ ↔ a.denote S ρ := by
  induction a generalizing Γ ρ with
  | unary r t =>
    obtain ⟨_, hr, _⟩ := hw
    have : r ∉ ns := fun h => by rw [hn r h] at hr; cases hr
    simp only [VE.Formula.denote, VE.Term.denote, hR r _ this]
  | binary r t w =>
    obtain ⟨_, _, hr, _⟩ := hw
    have : r ∉ ns := fun h => by rw [hn r h] at hr; cases hr
    simp only [VE.Formula.denote, VE.Term.denote, hR r _ this]
  | eq t w => exact Iff.rfl
  | top | bottom => exact Iff.rfl
  | not a ih => simp only [VE.Formula.denote]; rw [ih Γ ρ hw]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    simp only [VE.Formula.denote]; rw [ia Γ ρ hw.1, ib Γ ρ hw.2]
  | all t a ih | ex t a ih =>
    simp only [VE.Formula.denote]
    first
    | exact forall_congr' fun v => imp_congr_right fun _ => ih (t :: Γ) (v :: ρ) hw.2
    | exact exists_congr fun v => and_congr_right fun _ => ih (t :: Γ) (v :: ρ) hw.2

/-! ## Local expansion -/

/-- Interpret the next layer symbol by its meaning on typed tuples. -/
def interpret (T : Tree) (q : Sym) (S₀ : VE.Structure.{u}) : VE.Structure.{u} :=
  { S₀ with relation := fun r vs =>
      if r = q.name then VE.TupleTyped S₀ q.sorts vs ∧ (q.meaning T).denote S₀ (tupleVal vs)
      else S₀.relation r vs }

theorem tupleTyped_interpret (T : Tree) (q : Sym) (S₀ : VE.Structure.{u}) (ss : List String)
    (vs : List S₀.Carrier) : VE.TupleTyped (interpret T q S₀) ss vs ↔ VE.TupleTyped S₀ ss vs :=
  tupleTyped_relation S₀ _ ss vs

theorem tupleTyped_restrictAll (T : Tree) (S : VE.Structure.{u}) (ss : List String)
    (vs : List S.Carrier) : VE.TupleTyped (restrictAll T S) ss vs ↔ VE.TupleTyped S ss vs :=
  tupleTyped_forget _ S ss vs

/-- The local test at the `k`-th layer symbol, evaluated in the actual lower tables. -/
def ConflictFreeAtIdx (D : Doc) (k : Nat) (S₀ : VE.Structure.{u}) : Prop :=
  match (syms D.T)[k]? with
  | none => True
  | some q => ∀ vs, VE.TupleTyped S₀ q.sorts vs →
      ¬ (q.clash D.T).denote S₀ (tupleVal vs) ∧
      ∀ pr ∈ pairsAt D.T k,
        (pr.req = q.name → ¬ ((q.meaning D.T).denote S₀ (tupleVal vs) ∧ ¬ S₀.relation pr.perm vs)) ∧
        (pr.perm = q.name → ¬ (S₀.relation pr.req vs ∧ ¬ (q.meaning D.T).denote S₀ (tupleVal vs)))

/-- `ConflictFreeAt E T p S₀`: the local test at `p`, on a structure interpreting
the prefix below `p` (not a base structure). -/
def ConflictFreeAt (D : Doc) (p : String) (S₀ : VE.Structure.{u}) : Prop :=
  ConflictFreeAtIdx D (before D p) S₀

/-- The output admissibility of `p`'s layer: prefix admissibility including `p`. -/
def AdmissibleOut (D : Doc) (p : String) (S : VE.Structure.{u}) : Prop :=
  PrefixAdmissible D (before D p + 1) S

section Local
variable {D : Doc} (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q)
include hv hk

theorem forget_interpret (S₀ : VE.Structure.{u}) (h : S₀.Admissible (envAt D k)) :
    forget [q.name] (interpret D.T q S₀) = S₀ := by
  cases S₀ with
  | mk C d c rel =>
    simp only [forget, interpret, VE.Structure.mk.injEq, heq_eq_eq, true_and]
    funext r vs
    apply propext
    by_cases hr : r = q.name
    · subst hr
      simp only [List.mem_singleton, not_true_eq_false, false_and, false_iff]
      intro hrel
      obtain ⟨ss, hss, _⟩ := h.2 _ vs hrel
      rw [envAt_later hv hk (Nat.le_refl k)] at hss
      cases hss
    · simp [hr]

/-- Formulas below `q` have the same truth after interpreting `q`. -/
theorem interpret_denote (S₀ : VE.Structure.{u}) (a : VE.Formula) (Γ : List String)
    (ρ : VE.Valuation S₀) (hw : a.WellFormed (envAt D k) Γ) :
    a.denote (interpret D.T q S₀) ρ ↔ a.denote S₀ ρ :=
  denote_relation_congr (self_hidden hv hk) S₀ _ (fun r vs hr => by
    simp only [List.mem_singleton] at hr; simp [hr]) a Γ ρ hw

/-- The members of a pair closing at `k`: one is `q`, the other is placed earlier. -/
theorem pairsAt_members {pr : Pair} (hpr : pr ∈ pairsAt D.T k) :
    ∃ r, q = .reg r ∧ r.sorts = pr.sorts ∧
      ((pr.req = q.name ∧ ∃ j m, j < k ∧ (syms D.T)[j]? = some (.reg m) ∧ m.name = pr.perm) ∨
       (pr.perm = q.name ∧ ∃ j m, j < k ∧ (syms D.T)[j]? = some (.reg m) ∧ m.name = pr.req)) := by
  obtain ⟨hpr, hc⟩ := List.mem_filter.mp hpr
  have hc : pr.closes D.T = k := by simpa using hc
  obtain ⟨hne, ⟨i, r, hi, hrn, hrs, hri⟩, ⟨j, m, hj, hmn, hms, hmj⟩⟩ := pair_members hv hpr
  have hij : i ≠ j := fun e => by
    subst e; rw [hi] at hj; cases hj; exact hne (hrn.symm.trans hmn)
  simp only [Pair.closes, hri, hmj] at hc
  rcases Nat.lt_or_ge i j with h | h
  · have hjk : j = k := by omega
    subst hjk
    rw [hk] at hj; cases hj
    exact ⟨m, rfl, hms, Or.inr ⟨hmn.symm, i, r, h, hi, hrn⟩⟩
  · have hik : i = k := by omega
    subst hik
    rw [hk] at hi; cases hi
    exact ⟨r, rfl, hrs, Or.inl ⟨hrn.symm, j, m, by omega, hj, hmn⟩⟩

theorem name_ne_of_lt {j : Nat} {q' : Sym} (hj : (syms D.T)[j]? = some q') (hjk : j < k) :
    q'.name ≠ q.name := fun e => by
  have := nodup_getElem?_inj hv.nodup (getElem?_names hj) (e ▸ getElem?_names hk); omega

/-- Local unique expansion: an admissible prefix has exactly one admissible
expansion by the next layer symbol iff it passes the local test. -/
theorem local_expands (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissible D k S₀) :
    Unique (fun S => forget [q.name] S = S₀ ∧ PrefixAdmissible D (k + 1) S) ↔
      ConflictFreeAtIdx D k S₀ := by
  have hA₀ := prefixAdmissible_admissible h₀
  have hid := self_hidden hv hk
  simp only [ConflictFreeAtIdx, hk]
  constructor
  · rintro ⟨S, ⟨rfl, hS⟩, _⟩
    simp only [PrefixAdmissible, hk] at hS
    obtain ⟨_, _, hL, hpairs⟩ := hS
    have hM := (layerMeaning_iff hv hk S).mp hL
    intro vs hvs
    rw [tupleTyped_forget] at hvs
    have hmean : (q.meaning D.T).denote (forget [q.name] S) (tupleVal vs) ↔ S.relation q.name vs :=
      (denote_forget hid S _ _ _ (meaning_wellFormed hv hk)).trans (hM vs hvs).2.symm
    refine ⟨fun hc => (hM vs hvs).1 ((denote_forget hid S _ _ _ (clash_wellFormed hv hk)).mp hc),
      fun pr hpr => ?_⟩
    obtain ⟨r, rfl, hrs, hcase⟩ := pairsAt_members hv hk hpr
    have hprem := (pair_premise_iff pr (hrs ▸ sym_arity hv hk) S).mp
      (hpairs _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs (by simpa [Sym.sorts, hrs] using hvs)
    rcases hcase with ⟨hreq, j, m, hj, hjm, hmn⟩ | ⟨hperm, j, m, hj, hjm, hmn⟩
    · refine ⟨fun _ ⟨ho, hnp⟩ => hnp ?_, fun hperm => absurd (hperm.trans hreq.symm)
        (pair_members hv (List.mem_filter.mp hpr).1).1.symm⟩
      rw [forget_relation S (by simpa [← hmn] using name_ne_of_lt hv hk hjm hj)]
      exact hprem (hreq ▸ hmean.mp ho)
    · refine ⟨fun hreq => absurd (hreq.trans hperm.symm)
        (pair_members hv (List.mem_filter.mp hpr).1).1, fun _ ⟨hreq, hno⟩ => hno ?_⟩
      rw [forget_relation S (by simpa [← hmn] using name_ne_of_lt hv hk hjm hj)] at hreq
      exact hmean.mpr (hperm ▸ hprem hreq)
  · intro hcf
    have hfi := forget_interpret hv hk S₀ hA₀
    have hPA : PrefixAdmissible D (k + 1) (interpret D.T q S₀) := by
      simp only [PrefixAdmissible, hk]
      refine ⟨⟨hA₀.1, fun r vs hr => ?_⟩, by rw [hfi]; exact h₀, ?_, ?_⟩
      · simp only [interpret] at hr
        split at hr
        · rename_i hrq
          subst hrq
          exact ⟨q.sorts, envAt_earlier hv hk (Nat.lt_succ_self k),
            (tupleTyped_interpret D.T q S₀ _ vs).mpr hr.1⟩
        · rename_i hrq
          obtain ⟨ss, hss, ht⟩ := hA₀.2 r vs hr
          refine ⟨ss, ?_, (tupleTyped_interpret D.T q S₀ _ vs).mpr ht⟩
          rw [envAt_succ hk] at hss
          simpa [hide, hrq] using hss
      · apply (layerMeaning_iff hv hk _).mpr
        intro vs hvs
        rw [tupleTyped_interpret] at hvs
        refine ⟨fun hc => (hcf vs hvs).1 ((interpret_denote hv hk S₀ _ _ _ (clash_wellFormed hv hk)).mp hc), ?_⟩
        rw [interpret_denote hv hk S₀ _ _ _ (meaning_wellFormed hv hk)]
        simp [interpret, hvs]
      · intro a ha
        obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
        obtain ⟨r, rfl, hrs, hcase⟩ := pairsAt_members hv hk hpr
        apply (pair_premise_iff pr (hrs ▸ sym_arity hv hk) _).mpr
        intro vs hvs hreq
        rw [tupleTyped_interpret] at hvs
        have hvs' : VE.TupleTyped S₀ (Sym.reg r).sorts vs := by simpa [Sym.sorts, hrs] using hvs
        have hloc := (hcf vs hvs').2 pr hpr
        rcases hcase with ⟨hq, j, m, hj, hjm, hmn⟩ | ⟨hq, j, m, hj, hjm, hmn⟩
        · have hne : pr.perm ≠ (Sym.reg r).name := by
            simpa [← hmn] using name_ne_of_lt hv hk hjm hj
          simp only [interpret, hq, if_true] at hreq
          simp only [interpret, hne, if_false]
          exact Classical.byContradiction fun hn => hloc.1 hq ⟨hreq.2, hn⟩
        · have hne : pr.req ≠ (Sym.reg r).name := by
            simpa [← hmn] using name_ne_of_lt hv hk hjm hj
          simp only [interpret, hne, if_false] at hreq
          simp only [interpret, hq, if_true]
          exact ⟨hvs', Classical.byContradiction fun hn => hloc.2 hq ⟨hreq, hn⟩⟩
    refine ⟨interpret D.T q S₀, ⟨hfi, hPA⟩, ?_⟩
    rintro S ⟨rfl, hS⟩
    have hS' := hS
    simp only [PrefixAdmissible, hk] at hS'
    obtain ⟨hA, _, hL, _⟩ := hS'
    have hM := (layerMeaning_iff hv hk S).mp hL
    cases S with
    | mk C d c rel =>
      simp only [interpret, forget, VE.Structure.mk.injEq, heq_eq_eq, true_and]
      funext r vs
      apply propext
      by_cases hr : r = q.name
      · subst hr
        simp only [if_true]
        constructor
        · intro hrel
          obtain ⟨ss, hss, ht⟩ := hA.2 _ vs hrel
          rw [envAt_earlier hv hk (Nat.lt_succ_self k)] at hss
          cases hss
          refine ⟨(tupleTyped_forget [q.name] ⟨C, d, c, rel⟩ _ vs).mpr ht, ?_⟩
          have := (denote_forget hid ⟨C, d, c, rel⟩ _ _ (tupleVal vs) (meaning_wellFormed hv hk)).mpr
            (((hM vs ht).2).mp hrel)
          exact this
        · rintro ⟨ht, hm⟩
          exact ((hM vs ((tupleTyped_forget [q.name] ⟨C, d, c, rel⟩ _ vs).mp ht)).2).mpr
            ((denote_forget hid ⟨C, d, c, rel⟩ _ _ (tupleVal vs) (meaning_wellFormed hv hk)).mp hm)
      · simp [hr]

end Local

/-- `conflictFree_expands`: the local iff at a regulated predicate, with the
layer's output admissibility and its generated premise. -/
theorem conflictFree_expands (D : Doc) (h : WellFormed D = true) (r : Regulated)
    (hr : r ∈ D.T.regulated) (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissible D (before D r.name) S₀) :
    Unique (fun S => forget [r.name] S = S₀ ∧ AdmissibleOut D r.name S ∧
      (elabPremise D.T r).denote S []) ↔ ConflictFreeAt D r.name S₀ := by
  have hv := valid_of_wellFormed D h
  obtain ⟨k, hk⟩ := mem_syms_getElem? (hv.regulated r hr)
  have hb : before D r.name = k := before_eq hv hk
  unfold ConflictFreeAt AdmissibleOut
  rw [hb] at h₀ ⊢
  rw [← local_expands hv hk S₀ h₀]
  apply unique_congr
  intro S
  constructor
  · rintro ⟨h₁, h₂, _⟩; exact ⟨h₁, h₂⟩
  · rintro ⟨h₁, h₂⟩
    refine ⟨h₁, h₂, ?_⟩
    have h₂' := h₂
    simp only [PrefixAdmissible, hk] at h₂'
    exact (elabPremise_iff_meaning D.T r (sym_arity hv hk) S).mpr
      ((layerMeaning_iff hv hk S).mp h₂'.2.2.1)

/-! ## Base conflict formulas -/

/-- `conflict_p := P_p° ∧ N_p°`. -/
def conflict (D : Doc) (r : Regulated) : VE.Formula :=
  .and (subst D.T (before D r.name) (pos D.T r.name)) (subst D.T (before D r.name) (neg D.T r.name))

/-- `O_q°` for the regulated predicate named `n`. -/
def outcomeBase (D : Doc) (n : String) : VE.Formula :=
  match D.T.regulated.find? (·.name == n) with
  | some r => subst D.T (before D n) (outcome D.T r)
  | none => .bottom

/-- `conflict_(r,m) := O_r° ∧ ¬O_m°`. -/
def pairConflict (D : Doc) (pr : Pair) : VE.Formula :=
  .and (outcomeBase D pr.req) (.not (outcomeBase D pr.perm))

/-- `ConflictFree`: no typed base tuple satisfies any conflict formula. -/
def ConflictFree (D : Doc) (B : VE.Structure.{u}) : Prop :=
  (∀ r ∈ D.T.regulated, ∀ vs, VE.TupleTyped B r.sorts vs →
    ¬ (conflict D r).denote B (tupleVal vs)) ∧
  (∀ pr ∈ pairs D.T, ∀ vs, VE.TupleTyped B pr.sorts vs →
    ¬ (pairConflict D pr).denote B (tupleVal vs))

theorem find_regulated {D : Doc} (hv : Valid D) {k : Nat} {r : Regulated}
    (hk : (syms D.T)[k]? = some (.reg r)) : D.T.regulated.find? (·.name == r.name) = some r := by
  cases hf : D.T.regulated.find? (·.name == r.name) with
  | none =>
    have := List.find?_eq_none.mp hf r (mem_syms_reg (List.mem_of_getElem? hk))
    simp at this
  | some r' =>
    have hn : r'.name = r.name := by simpa using List.find?_some hf
    obtain ⟨k', hk'⟩ := mem_syms_getElem? (hv.regulated r' (List.mem_of_find?_eq_some hf))
    have := nodup_getElem?_inj hv.nodup (getElem?_names hk')
      (by show (layerNames D.T)[k]? = some r'.name; rw [hn]; exact getElem?_names hk)
    subst this
    rw [hk] at hk'
    cases hk'
    rfl

theorem conflict_wellFormed {D : Doc} (hv : Valid D) {k : Nat} {r : Regulated}
    (hk : (syms D.T)[k]? = some (.reg r)) : (conflict D r).WellFormed (envAt D 0) r.sorts.reverse := by
  have hb : before D r.name = k := before_eq hv hk
  simp only [conflict, hb]
  exact ⟨subst_wellFormed hv k _ _ (decides_wellFormed (rulesTyped_of_valid hv hk) true),
    subst_wellFormed hv k _ _ (decides_wellFormed (rulesTyped_of_valid hv hk) false)⟩

theorem outcomeBase_wellFormed {D : Doc} (hv : Valid D) {k : Nat} {r : Regulated}
    (hk : (syms D.T)[k]? = some (.reg r)) :
    (outcomeBase D r.name).WellFormed (envAt D 0) r.sorts.reverse := by
  have hb : before D r.name = k := before_eq hv hk
  simp only [outcomeBase, find_regulated hv hk, hb]
  exact subst_wellFormed hv k _ _ (outcome_wellFormed (rulesTyped_of_valid hv hk))

theorem pairConflict_wellFormed {D : Doc} (hv : Valid D) {pr : Pair} (hpr : pr ∈ pairs D.T) :
    (pairConflict D pr).WellFormed (envAt D 0) pr.sorts.reverse := by
  obtain ⟨_, ⟨i, r, hi, hrn, hrs, _⟩, ⟨j, m, hj, hmn, hms, _⟩⟩ := pair_members hv hpr
  refine ⟨?_, ?_⟩
  · have := outcomeBase_wellFormed hv hi; rwa [hrn, hrs] at this
  · have := outcomeBase_wellFormed hv hj; rwa [hmn, hms] at this

theorem conflict_denote {D : Doc} (hv : Valid D) {k : Nat} {r : Regulated}
    (hk : (syms D.T)[k]? = some (.reg r)) (S : VE.Structure.{u}) (hc : ConstantsTyped D S)
    (ha : AgreesBelow D k S) (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs) :
    (conflict D r).denote (restrictAll D.T S) (tupleVal vs) ↔
      ((Sym.reg r).clash D.T).denote S (tupleVal vs) := by
  have hb : before D r.name = k := before_eq hv hk
  have hρ := tupleVal_typed S _ vs hvs
  simp only [conflict, hb, VE.Formula.denote, Sym.clash]
  rw [subst_restrict_denote hv k S hc ha (pos D.T r.name) _
      (decides_wellFormed (rulesTyped_of_valid hv hk) true) _ hρ,
    subst_restrict_denote hv k S hc ha (neg D.T r.name) _
      (decides_wellFormed (rulesTyped_of_valid hv hk) false) _ hρ]

theorem outcomeBase_denote {D : Doc} (hv : Valid D) {k : Nat} {r : Regulated}
    (hk : (syms D.T)[k]? = some (.reg r)) (S : VE.Structure.{u}) (hc : ConstantsTyped D S)
    (ha : AgreesBelow D k S) (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs) :
    (outcomeBase D r.name).denote (restrictAll D.T S) (tupleVal vs) ↔
      ((Sym.reg r).meaning D.T).denote S (tupleVal vs) := by
  have hb : before D r.name = k := before_eq hv hk
  simp only [outcomeBase, find_regulated hv hk, hb]
  exact subst_restrict_denote hv k S hc ha _ _ (outcome_wellFormed (rulesTyped_of_valid hv hk)) _
    (tupleVal_typed S _ vs hvs)

/-- In a structure satisfying the prefix's meanings, the outcome of an earlier
regulated member agrees with its relation. -/
theorem outcomeBase_relation {D : Doc} (hv : Valid D) {k j : Nat} {m : Regulated}
    (hj : (syms D.T)[j]? = some (.reg m)) (hjk : j < k) (S : VE.Structure.{u})
    (hc : ConstantsTyped D S) (hM : MeaningsBelow D k S) (vs : List S.Carrier)
    (hvs : VE.TupleTyped S m.sorts vs) :
    (outcomeBase D m.name).denote (restrictAll D.T S) (tupleVal vs) ↔ S.relation m.name vs := by
  rw [outcomeBase_denote hv hj S hc (fun j' q' hj' => agreesBelow_of_meanings hM j' q'
    (Nat.lt_trans hj' hjk)) vs hvs]
  exact ((hM j _ hjk hj) vs hvs).2.symm

/-- The local test at an admissible prefix follows from base conflict-freedom of
its base restriction (transfer by substitution). -/
theorem conflictFreeAt_of_base {D : Doc} (hv : Valid D) {k : Nat} {q : Sym}
    (hk : (syms D.T)[k]? = some q) (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissible D k S₀)
    (hcf : ConflictFree D (restrictAll D.T S₀)) : ConflictFreeAtIdx D k S₀ := by
  have hle := prefixAdmissible_le h₀
  obtain ⟨hA, _, hM, _⟩ := (prefix_char hv k hle S₀).mp h₀
  have hc : ConstantsTyped D S₀ := hA.1
  have ha := agreesBelow_of_meanings hM
  simp only [ConflictFreeAtIdx, hk]
  intro vs hvs
  refine ⟨?_, fun pr hpr => ?_⟩
  · cases q with
    | defn _ => exact id
    | reg r =>
      intro hcl
      exact hcf.1 r (mem_syms_reg (List.mem_of_getElem? hk)) vs
        ((tupleTyped_forget _ S₀ _ vs).mpr hvs) ((conflict_denote hv hk S₀ hc ha vs hvs).mpr hcl)
  · obtain ⟨r, rfl, hrs, hcase⟩ := pairsAt_members hv hk hpr
    have hpr' := (List.mem_filter.mp hpr).1
    have hvs' : VE.TupleTyped (restrictAll D.T S₀) pr.sorts vs :=
      (tupleTyped_forget _ S₀ _ vs).mpr (by simpa [Sym.sorts, hrs] using hvs)
    have hno := hcf.2 pr hpr' vs hvs'
    have hr : outcomeBase D pr.req = outcomeBase D (Sym.reg r).name ∨
        outcomeBase D pr.perm = outcomeBase D (Sym.reg r).name := by
      rcases hcase with ⟨hq, _⟩ | ⟨hq, _⟩
      · exact Or.inl (by rw [hq])
      · exact Or.inr (by rw [hq])
    have hself := outcomeBase_denote hv hk S₀ hc ha vs hvs
    rcases hcase with ⟨hq, j, m, hjk, hj, hmn⟩ | ⟨hq, j, m, hjk, hj, hmn⟩
    · refine ⟨fun _ ⟨ho, hnp⟩ => hno ⟨?_, fun hp => hnp ?_⟩, fun hp => absurd (hp.trans hq.symm)
        (pair_members hv hpr').1.symm⟩
      · rw [hq]; exact hself.mpr ho
      · have hms : m.sorts = pr.sorts := by
          have := (pair_members hv hpr').2.2
          obtain ⟨j', m', hj', hm'n, hm's, _⟩ := this
          have := nodup_getElem?_inj hv.nodup (getElem?_names hj) (by simpa [Sym.name, hmn, ← hm'n] using getElem?_names hj')
          subst this; rw [hj] at hj'; cases hj'; exact hm's
        rw [← hmn] at hp ⊢
        exact (outcomeBase_relation hv hj hjk S₀ hc hM vs (by simpa [hms, ← hrs] using hvs)).mp hp
    · refine ⟨fun hp => absurd (hp.trans hq.symm) (pair_members hv hpr').1,
        fun _ ⟨hreq, hno'⟩ => hno ⟨?_, fun hp => hno' ?_⟩⟩
      · have hms : m.sorts = pr.sorts := by
          obtain ⟨_, ⟨j', m', hj', hm'n, hm's, _⟩, _⟩ := pair_members hv hpr'
          have := nodup_getElem?_inj hv.nodup (getElem?_names hj) (by simpa [Sym.name, hmn, ← hm'n] using getElem?_names hj')
          subst this; rw [hj] at hj'; cases hj'; exact hm's
        rw [← hmn] at hreq ⊢
        exact (outcomeBase_relation hv hj hjk S₀ hc hM vs (by simpa [hms, ← hrs] using hvs)).mpr hreq
      · rw [hq] at hp; exact hself.mp hp

/-! ## The document iff -/

/-- `DocumentExpansion`: an expansion of the base structure `B` to the complete
vocabulary satisfying Background and every layer premise. No conflict-freedom
is assumed and no `Layer` is constructed. -/
def DocumentExpansion (D : Doc) (B S : VE.Structure.{u}) : Prop :=
  restrictAll D.T S = B ∧ S.Admissible (envAt D (size D)) ∧ Sat S (background D ++ elaborate D.T)

theorem documentExpansion_iff {D : Doc} (hv : Valid D) (B S : VE.Structure.{u})
    (hB : BaseAdmissible D B) :
    DocumentExpansion D B S ↔ restrictAll D.T S = B ∧ PrefixAdmissible D (size D) S := by
  rw [DocumentExpansion, sat_document hv, prefix_char hv _ (Nat.le_refl _)]
  constructor
  · rintro ⟨rfl, hA, _, hM, hP⟩
    exact ⟨rfl, hA, hB, hM, hP⟩
  · rintro ⟨rfl, hA, hB', hM, hP⟩
    exact ⟨rfl, hA, (sat_literals_forget _ _ S).mp hB'.2, hM, hP⟩

theorem expansion_unique {D : Doc} (hv : Valid D) (B : VE.Structure.{u}) (hB : BaseAdmissible D B)
    (hcf : ConflictFree D B) :
    ∀ k, k ≤ size D → Unique (fun S => restrictAll D.T S = B ∧ PrefixAdmissible D k S)
  | 0, _ => ⟨B, ⟨restrictAll_self B hB.1, hB⟩, fun S ⟨h₁, h₂⟩ => by
      rw [restrictAll_self S h₂.1] at h₁; exact h₁⟩
  | k + 1, hk => by
    have hlt : k < (syms D.T).length := hk
    obtain ⟨q, hq⟩ : ∃ q, (syms D.T)[k]? = some q := ⟨_, List.getElem?_eq_getElem hlt⟩
    obtain ⟨Sk, ⟨hr, hpa⟩, hu⟩ := expansion_unique hv B hB hcf k (Nat.le_of_succ_le hk)
    have hloc := conflictFreeAt_of_base hv hq Sk hpa (hr ▸ hcf)
    obtain ⟨S', ⟨hf, hpa'⟩, hu'⟩ := (local_expands hv hq Sk hpa).mpr hloc
    refine ⟨S', ⟨?_, hpa'⟩, ?_⟩
    · rw [← restrictAll_forget (name_mem_layerNames hq), hf, hr]
    · rintro S'' ⟨hr'', hpa''⟩
      apply hu'
      have hpa2 := hpa''
      simp only [PrefixAdmissible, hq] at hpa2
      refine ⟨hu _ ⟨?_, hpa2.2.1⟩, hpa''⟩
      rw [restrictAll_forget (name_mem_layerNames hq), hr'']

/-- `conflictFree_expands_document`: over every base-admissible structure, the
document has exactly one full expansion iff the structure is conflict-free.
Existence alone already implies conflict-freedom. -/
theorem conflictFree_expands_document (D : Doc) (h : WellFormed D = true) (B : VE.Structure.{u})
    (hB : BaseAdmissible D B) :
    Unique (DocumentExpansion D B) ↔ ConflictFree D B := by
  have hv := valid_of_wellFormed D h
  constructor
  · rintro ⟨S, hS, _⟩
    obtain ⟨rfl, hpa⟩ := (documentExpansion_iff hv B S hB).mp hS
    obtain ⟨hA, _, hM, hP⟩ := (prefix_char hv _ (Nat.le_refl _) S).mp hpa
    have hc : ConstantsTyped D S := hA.1
    refine ⟨fun r hr vs hvs hcon => ?_, fun pr hpr vs hvs hcon => ?_⟩
    · obtain ⟨k, hk⟩ := mem_syms_getElem? (hv.regulated r hr)
      have hkl := (List.getElem?_eq_some_iff.mp hk).1
      rw [tupleTyped_restrictAll] at hvs
      exact (hM k _ hkl hk vs hvs).1 ((conflict_denote hv hk S hc
        (fun j q hj => agreesBelow_of_meanings hM j q (Nat.lt_trans hj hkl)) vs hvs).mp hcon)
    · obtain ⟨_, ⟨i, r, hi, hrn, hrs, _⟩, ⟨j, m, hj, hmn, hms, _⟩⟩ := pair_members hv hpr
      rw [tupleTyped_restrictAll] at hvs
      have hil := (List.getElem?_eq_some_iff.mp hi).1
      have hjl := (List.getElem?_eq_some_iff.mp hj).1
      obtain ⟨ho, hno⟩ := hcon
      rw [← hrn] at ho; rw [← hmn] at hno
      have h₁ := (outcomeBase_relation hv hi hil S hc hM vs (by rwa [hrs])).mp ho
      have h₂ := (pair_premise_iff pr (pair_arity hv hpr) S).mp
        (hP pr hpr (pair_closes_lt_size hv hpr)) vs hvs (hrn ▸ h₁)
      exact hno ((outcomeBase_relation hv hj hjl S hc hM vs (by rwa [hms])).mpr (hmn ▸ h₂))
  · intro hcf
    exact (unique_congr (fun S => documentExpansion_iff hv B S hB)).mpr
      (expansion_unique hv B hB hcf _ (Nat.le_refl _))

/-- `conflictFree_expands_all`: the document-wide iff. -/
theorem conflictFree_expands_all (D : Doc) (h : WellFormed D = true) :
    (∀ B : VE.Structure.{u}, BaseAdmissible D B → Unique (DocumentExpansion D B)) ↔
      (∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) :=
  ⟨fun hu B hB => (conflictFree_expands_document D h B hB).mp (hu B hB),
   fun hc B hB => (conflictFree_expands_document D h B hB).mpr (hc B hB)⟩

/-- `conflictFree_prefix`: base conflict-freedom gives each layer's local test on
every admissible prefix (the `hc` of the P0 `Layer`). -/
theorem conflictFree_prefix (D : Doc) (h : WellFormed D = true) (r : Regulated)
    (hr : r ∈ D.T.regulated) (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B)
    (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissible D (before D r.name) S₀) :
    ConflictFreeAt D r.name S₀ := by
  have hv := valid_of_wellFormed D h
  obtain ⟨k, hk⟩ := mem_syms_getElem? (hv.regulated r hr)
  have hb : before D r.name = k := before_eq hv hk
  unfold ConflictFreeAt
  rw [hb] at h₀ ⊢
  have hB := ((prefix_char hv k (prefixAdmissible_le h₀) S₀).mp h₀).2.1
  exact conflictFreeAt_of_base hv hk S₀ h₀ (hc _ hB)

/-- The same at every layer symbol, defined or regulated. -/
theorem conflictFree_prefix_idx {D : Doc} (hv : Valid D)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) (k : Nat)
    (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissible D k S₀) : ConflictFreeAtIdx D k S₀ := by
  cases hk : (syms D.T)[k]? with
  | none => simp [ConflictFreeAtIdx, hk]
  | some q =>
    have hB := ((prefix_char hv k (prefixAdmissible_le h₀) S₀).mp h₀).2.1
    exact conflictFreeAt_of_base hv hk S₀ h₀ (hc _ hB)

/-! ## Witnesses -/

/-- Finite validity of `Background_base` (literal distinctness), by evaluation. -/
def backgroundValid {α : Type u} [DecidableEq α] (D : Doc) (M : VE.FiniteModel α) : Bool :=
  (backgroundBase D).all (fun a => a.eval M [])

theorem baseAdmissible_of_valid {α : Type u} [DecidableEq α] (D : Doc) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt D 0)) (hb : backgroundValid D M = true) :
    BaseAdmissible D M.asStructure :=
  ⟨valid, fun a ha => (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp hb a ha)⟩

/-- `conflict_witness_sound`: a typed finite base witness of `conflict_p`
refutes base conflict-freedom there, unique expansion there, and the document
property. -/
theorem conflict_witness_sound {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormed D = true)
    (r : Regulated) (hr : r ∈ D.T.regulated) (M : VE.FiniteModel α) (valid : M.Valid (envAt D 0))
    (hb : backgroundValid D M = true) (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (hw : (conflict D r).eval M (tupleVal vs) = true) :
    ¬ ConflictFree D M.asStructure ∧ ¬ Unique (DocumentExpansion D M.asStructure) ∧
      ¬ (∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) := by
  have hB := baseAdmissible_of_valid D M valid hb
  have hn : ¬ ConflictFree D M.asStructure := fun hcf =>
    hcf.1 r hr vs typed ((VE.eval_iff_denote M _ _).mp hw)
  exact ⟨hn, fun hu => hn ((conflictFree_expands_document D h _ hB).mp hu),
    fun hall => hn (hall _ hB)⟩

/-- `conflict_pair_witness_sound`: the same for a declared pair's formula. -/
theorem conflict_pair_witness_sound {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormed D = true)
    (pr : Pair) (hpr : pr ∈ pairs D.T) (M : VE.FiniteModel α) (valid : M.Valid (envAt D 0))
    (hb : backgroundValid D M = true) (vs : List α) (typed : VE.TupleTyped M.asStructure pr.sorts vs)
    (hw : (pairConflict D pr).eval M (tupleVal vs) = true) :
    ¬ ConflictFree D M.asStructure ∧ ¬ Unique (DocumentExpansion D M.asStructure) ∧
      ¬ (∀ B : VE.Structure.{u}, BaseAdmissible D B → ConflictFree D B) := by
  have hB := baseAdmissible_of_valid D M valid hb
  have hn : ¬ ConflictFree D M.asStructure := fun hcf =>
    hcf.2 pr hpr vs typed ((VE.eval_iff_denote M _ _).mp hw)
  exact ⟨hn, fun hu => hn ((conflictFree_expands_document D h _ hB).mp hu),
    fun hall => hn (hall _ hB)⟩

end VE.Norms
