import VE.Norms.Elaborate

/-! Outcome substitution (docs/spec/norms.md 4.5 and 6.1): push formulas over a
prefix `E_i` down to base symbols by replacing every atom of an earlier layer
symbol with that symbol's meaning (a regulated predicate's completed outcome,
a defined predicate's body), itself already pushed down. The table `expTable T i`
holds these base formulas for the first `i` layer symbols.

`subst_sound` is the typed statement: on any structure whose earlier layer
symbols agree with their meanings, a formula typed over `E_i` and its
substitution agree under every typed valuation, and the substitution is a base
formula (so it may be evaluated in the base restriction). -/
namespace VE.Norms
universe u

/-- The formula a layer symbol's relation must agree with: a regulated
predicate's completed outcome, a defined predicate's body. -/
def Sym.meaning (T : Tree) : Sym → VE.Formula
  | .reg r => outcome T r
  | .defn d => d.body

/-- Opposite selections: both `P_p` and `N_p` hold (never for a definition). -/
def Sym.clash (T : Tree) : Sym → VE.Formula
  | .reg r => .and (pos T r.name) (neg T r.name)
  | .defn _ => .bottom

abbrev Table := String → Option VE.Formula

/-- Replace every atom of a tabled symbol by its formula at the atom's arguments. -/
def substWith (tbl : Table) : VE.Formula → VE.Formula
  | .top => .top
  | .bottom => .bottom
  | .unary q t => match tbl q with
    | some F => inst [t] F
    | none => .unary q t
  | .binary q t w => match tbl q with
    | some F => inst [w, t] F
    | none => .binary q t w
  | .eq t w => .eq t w
  | .not a => .not (substWith tbl a)
  | .and a b => .and (substWith tbl a) (substWith tbl b)
  | .or a b => .or (substWith tbl a) (substWith tbl b)
  | .implies a b => .implies (substWith tbl a) (substWith tbl b)
  | .all s a => .all s (substWith tbl a)
  | .ex s a => .ex s (substWith tbl a)

/-- The base formulas of the first `i` layer symbols, in DAG order. -/
def expTable (T : Tree) : Nat → Table
  | 0 => fun _ => none
  | k + 1 => fun n => match (syms T)[k]? with
    | some q => if n = q.name then some (substWith (expTable T k) (q.meaning T)) else expTable T k n
    | none => expTable T k n

/-- `φ°` for a formula over the prefix `E_i`. -/
def subst (T : Tree) (i : Nat) (φ : VE.Formula) : VE.Formula := substWith (expTable T i) φ

/-- Forget every layer symbol: the base restriction. -/
def restrictAll (T : Tree) (S : VE.Structure.{u}) : VE.Structure.{u} := forget (layerNames T) S

/-! ## The table -/

theorem expTable_none (T : Tree) : ∀ (k : Nat) (n : String), n ∉ (layerNames T).take k →
    expTable T k n = none
  | 0, _, _ => rfl
  | k + 1, n, hn => by
    cases hq : (syms T)[k]? with
    | some q =>
      simp only [expTable, hq]
      have hk : (layerNames T).take (k + 1) = (layerNames T).take k ++ [q.name] := by
        rw [List.take_succ, names_getElemOpt hq]; rfl
      rw [hk] at hn
      simp only [List.mem_append, List.mem_singleton, not_or] at hn
      simp only [hn.2, if_false]
      exact expTable_none T k n hn.1
    | none =>
      simp only [expTable, hq]
      have hk : (layerNames T).take (k + 1) = (layerNames T).take k := by
        rw [List.take_succ]
        simp [layerNames, List.getElem?_map, hq]
      rw [hk] at hn
      exact expTable_none T k n hn

theorem expTable_some (T : Tree) : ∀ (k : Nat) (n : String) (F : VE.Formula), expTable T k n = some F →
    ∃ j q, j < k ∧ (syms T)[j]? = some q ∧ q.name = n ∧ F = substWith (expTable T j) (q.meaning T)
  | 0, _, _, h => by cases h
  | k + 1, n, F, h => by
    cases hq : (syms T)[k]? with
    | some q =>
      simp only [expTable, hq] at h
      split at h
      · rename_i hn
        cases h
        exact ⟨k, q, Nat.lt_succ_self k, hq, hn.symm, rfl⟩
      · obtain ⟨j, q', hj, h₁, h₂, h₃⟩ := expTable_some T k n F h
        exact ⟨j, q', Nat.lt_succ_of_lt hj, h₁, h₂, h₃⟩
    | none =>
      simp only [expTable, hq] at h
      obtain ⟨j, q', hj, h₁, h₂, h₃⟩ := expTable_some T k n F h
      exact ⟨j, q', Nat.lt_succ_of_lt hj, h₁, h₂, h₃⟩

theorem expTable_at {D : Doc} (hv : Valid D) : ∀ (k j : Nat) (q : Sym), j < k →
    (syms D.T)[j]? = some q → expTable D.T k q.name = some (substWith (expTable D.T j) (q.meaning D.T))
  | 0, _, _, h, _ => absurd h (Nat.not_lt_zero _)
  | k + 1, j, q, hj, hq => by
    cases hq' : (syms D.T)[k]? with
    | some q' =>
      simp only [expTable, hq']
      by_cases he : q.name = q'.name
      · have := nodup_getElemOpt_inj hv.nodup (names_getElemOpt hq) (he ▸ names_getElemOpt hq')
        subst this
        rw [hq] at hq'
        cases hq'
        simp
      · simp only [he, if_false]
        rcases Nat.lt_succ_iff_lt_or_eq.mp hj with hj | rfl
        · exact expTable_at hv k j q hj hq
        · rw [hq] at hq'; cases hq'; exact absurd rfl he
    | none =>
      simp only [expTable, hq']
      rcases Nat.lt_succ_iff_lt_or_eq.mp hj with hj | rfl
      · exact expTable_at hv k j q hj hq
      · rw [hq] at hq'; cases hq'

/-! ## Generic substitution lemmas -/

theorem term_defined_consts {E : VE.Environment} {S : VE.Structure.{u}}
    (hc : ∀ c s, E.constants c = some s → ∃ v, S.constant c = some v ∧ S.domain s v)
    {Γ : List String} {ρ : VE.Valuation S} (hρ : VE.Valuation.Typed S Γ ρ)
    {t : VE.Term} {s : String} (ht : t.sortOf E Γ = some s) :
    ∃ v, t.denote S ρ = some v ∧ S.domain s v := by
  cases t with
  | var i => exact hρ i s ht
  | const c => exact hc c s ht

/-- Typing: tabled symbols become base formulas; other atoms keep their typing. -/
theorem substWith_wellFormed (tbl : Table) (Ehi Elo : VE.Environment) (hs : Elo.sorts = Ehi.sorts)
    (hc : Elo.constants = Ehi.constants)
    (htbl : ∀ n F, tbl n = some F → ∃ ss, Ehi.predicates n = some ss ∧ F.WellFormed Elo ss.reverse)
    (hnone : ∀ n ss, tbl n = none → Ehi.predicates n = some ss → Elo.predicates n = some ss) :
    ∀ (φ : VE.Formula) (Γ : List String), φ.WellFormed Ehi Γ → (substWith tbl φ).WellFormed Elo Γ := by
  intro φ
  induction φ with
  | top | bottom => intro Γ h; exact h
  | unary q t =>
    intro Γ ⟨s, hq, ht⟩
    simp only [substWith]
    split
    · rename_i F hF
      obtain ⟨ss, hss, hFw⟩ := htbl q F hF
      rw [hq] at hss; cases hss
      apply inst_wellFormed Elo Elo rfl rfl (fun _ _ h => h) F Γ [s] [t] rfl _ hFw
      intro i h₁ _
      match i, h₁ with
      | 0, _ => simpa [sortOf_congr hc] using ht
    · rename_i hF
      exact ⟨s, hnone q _ hF hq, by rw [sortOf_congr hc]; exact ht⟩
  | binary q t w =>
    intro Γ ⟨s, s', hq, ht, hw⟩
    simp only [substWith]
    split
    · rename_i F hF
      obtain ⟨ss, hss, hFw⟩ := htbl q F hF
      rw [hq] at hss; cases hss
      apply inst_wellFormed Elo Elo rfl rfl (fun _ _ h => h) F Γ [s', s] [w, t] rfl _ hFw
      intro i h₁ _
      match i, h₁ with
      | 0, _ => simpa [sortOf_congr hc] using hw
      | 1, _ => simpa [sortOf_congr hc] using ht
    · rename_i hF
      exact ⟨s, s', hnone q _ hF hq, by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw⟩
  | eq t w =>
    intro Γ ⟨s, ht, hw⟩
    exact ⟨s, by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw⟩
  | not a ih => intro Γ h; exact ih Γ h
  | and a b ia ib | or a b ia ib | implies a b ia ib => intro Γ h; exact ⟨ia Γ h.1, ib Γ h.2⟩
  | all s a ih | ex s a ih => intro Γ h; exact ⟨hs ▸ h.1, ih _ h.2⟩

/-- Semantics: when every tabled formula agrees with its symbol's relation on
typed tuples, substitution preserves truth under typed valuations. -/
theorem substWith_denote (tbl : Table) (Ehi Elo : VE.Environment) (S : VE.Structure.{u})
    (hconst : ∀ c s, Ehi.constants c = some s → ∃ v, S.constant c = some v ∧ S.domain s v)
    (htbl : ∀ n F, tbl n = some F → ∃ ss, Ehi.predicates n = some ss ∧ F.WellFormed Elo ss.reverse ∧
      ∀ vs, VE.TupleTyped S ss vs → (F.denote S (tupleVal vs) ↔ S.relation n vs)) :
    ∀ (φ : VE.Formula) (Γ : List String) (ρ : VE.Valuation S), φ.WellFormed Ehi Γ →
      VE.Valuation.Typed S Γ ρ → ((substWith tbl φ).denote S ρ ↔ φ.denote S ρ) := by
  intro φ
  induction φ with
  | top | bottom => intros; exact Iff.rfl
  | unary q t =>
    intro Γ ρ ⟨s, hq, ht⟩ hρ
    simp only [substWith]
    split
    · rename_i F hF
      obtain ⟨ss, hss, hFw, hFa⟩ := htbl q F hF
      rw [hq] at hss; cases hss
      obtain ⟨v, hv, hd⟩ := term_defined_consts hconst hρ ht
      rw [inst_denote S Elo F [s] [t] ρ [v] hFw rfl ⟨rfl, fun i h₁ _ => by
        match i, h₁ with | 0, _ => exact hv⟩]
      have := hFa [v] ⟨hd, trivial⟩
      simp only [tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append] at this
      rw [this]
      simp only [VE.Formula.denote]
      exact ⟨fun h => ⟨v, hv, h⟩, fun ⟨w, hw, h⟩ => by rw [hv] at hw; cases hw; exact h⟩
    · exact Iff.rfl
  | binary q t w =>
    intro Γ ρ ⟨s, s', hq, ht, hw⟩ hρ
    simp only [substWith]
    split
    · rename_i F hF
      obtain ⟨ss, hss, hFw, hFa⟩ := htbl q F hF
      rw [hq] at hss; cases hss
      obtain ⟨v, hv, hd⟩ := term_defined_consts hconst hρ ht
      obtain ⟨v', hv', hd'⟩ := term_defined_consts hconst hρ hw
      rw [inst_denote S Elo F [s', s] [w, t] ρ [v', v] hFw rfl ⟨rfl, fun i h₁ _ => by
        match i, h₁ with
        | 0, _ => exact hv'
        | 1, _ => exact hv⟩]
      have := hFa [v, v'] ⟨hd, hd', trivial⟩
      simp only [tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append,
        List.cons_append] at this
      rw [this]
      simp only [VE.Formula.denote]
      exact ⟨fun h => ⟨v, v', hv, hv', h⟩, fun ⟨a, b, ha, hb, h⟩ => by
        rw [hv] at ha; rw [hv'] at hb; cases ha; cases hb; exact h⟩
    · exact Iff.rfl
  | eq t w => intros; exact Iff.rfl
  | not a ih =>
    intro Γ ρ hw hρ
    simp only [substWith, VE.Formula.denote]; rw [ih Γ ρ hw hρ]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ ρ hw hρ
    simp only [substWith, VE.Formula.denote]; rw [ia Γ ρ hw.1 hρ, ib Γ ρ hw.2 hρ]
  | all s a ih | ex s a ih =>
    intro Γ ρ hw hρ
    simp only [substWith, VE.Formula.denote]
    first
    | exact forall_congr' fun v => imp_congr_right fun hv => ih (s :: Γ) (v :: ρ) hw.2 (VE.typed_cons hρ hv)
    | exact exists_congr fun v => and_congr_right fun hv => ih (s :: Γ) (v :: ρ) hw.2 (VE.typed_cons hρ hv)

/-! ## The expansion table is typed and sound on agreeing structures -/

/-- The meaning formula of every layer symbol is typed below it. -/
theorem meaning_wellFormed {D : Doc} (hv : Valid D) {k : Nat} {q : Sym}
    (hk : (syms D.T)[k]? = some q) : (q.meaning D.T).WellFormed (envAt D k) q.sorts.reverse := by
  cases q with
  | reg r => exact outcome_wellFormed (rulesTyped_of_valid hv hk)
  | defn d => exact hv.typed k (.defn d) hk d.body (by simp [Sym.formulas])

theorem clash_wellFormed {D : Doc} (hv : Valid D) {k : Nat} {q : Sym}
    (hk : (syms D.T)[k]? = some q) : (q.clash D.T).WellFormed (envAt D k) q.sorts.reverse := by
  cases q with
  | reg r =>
    exact ⟨decides_wellFormed (rulesTyped_of_valid hv hk) true,
      decides_wellFormed (rulesTyped_of_valid hv hk) false⟩
  | defn d => trivial

theorem sym_arity {D : Doc} (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q) :
    Arity q.sorts := (hv.decl q (List.mem_of_getElem? hk)).2.1

theorem envAt_zero_later {D : Doc} {n : String} (hn : n ∈ layerNames D.T) :
    (envAt D 0).predicates n = none := by
  simp [envAt, hide, hn]

/-- Base formulas: every predicate declared at `envAt D 0` is outside the layer. -/
theorem expTable_wellFormed {D : Doc} (hv : Valid D) (k : Nat) :
    ∀ n F, expTable D.T k n = some F →
      ∃ ss, (envAt D k).predicates n = some ss ∧ F.WellFormed (envAt D 0) ss.reverse := by
  induction k using Nat.strongRecOn with
  | ind k ih =>
    intro n F hF
    obtain ⟨j, q, hj, hq, rfl, rfl⟩ := expTable_some D.T k n F hF
    refine ⟨q.sorts, envAt_earlier hv hq hj, ?_⟩
    apply substWith_wellFormed _ (envAt D j) (envAt D 0) rfl rfl (ih j hj) _ _ _
      (meaning_wellFormed hv hq)
    intro n ss hn hp
    by_cases hl : n ∈ layerNames D.T
    · obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hl
      obtain ⟨q', hq', rfl⟩ : ∃ q', (syms D.T)[i]? = some q' ∧ q'.name = n := by
        simp only [layerNames, List.getElem?_map, Option.map_eq_some_iff] at hi
        exact hi
      by_cases hij : i < j
      · rw [expTable_at hv j i q' hij hq'] at hn; cases hn
      · rw [envAt_later hv hq' (Nat.le_of_not_lt hij)] at hp; cases hp
    · rw [envAt_base hl] at hp ⊢; exact hp

/-- Base formulas are well-formed over `E_base` and see no layer symbol. -/
theorem subst_wellFormed {D : Doc} (hv : Valid D) (k : Nat) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt D k) Γ) : (subst D.T k φ).WellFormed (envAt D 0) Γ := by
  apply substWith_wellFormed _ (envAt D k) (envAt D 0) rfl rfl (expTable_wellFormed hv k) _ φ Γ hφ
  intro n ss hn hp
  by_cases hl : n ∈ layerNames D.T
  · obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hl
    obtain ⟨q', hq', rfl⟩ : ∃ q', (syms D.T)[i]? = some q' ∧ q'.name = n := by
      simp only [layerNames, List.getElem?_map, Option.map_eq_some_iff] at hi
      exact hi
    by_cases hik : i < k
    · rw [expTable_at hv k i q' hik hq'] at hn; cases hn
    · rw [envAt_later hv hq' (Nat.le_of_not_lt hik)] at hp; cases hp
  · rw [envAt_base hl] at hp ⊢; exact hp

/-- The layer symbols before `k` agree with their meanings in `S`. -/
def AgreesBelow (D : Doc) (k : Nat) (S : VE.Structure.{u}) : Prop :=
  ∀ j q, j < k → (syms D.T)[j]? = some q → ∀ vs, VE.TupleTyped S q.sorts vs →
    (S.relation q.name vs ↔ (q.meaning D.T).denote S (tupleVal vs))

def ConstantsTyped (D : Doc) (S : VE.Structure.{u}) : Prop :=
  ∀ c s, D.E.constants c = some s → ∃ v, S.constant c = some v ∧ S.domain s v

theorem expTable_sound {D : Doc} (hv : Valid D) (S : VE.Structure.{u}) (hc : ConstantsTyped D S)
    (k : Nat) (ha : AgreesBelow D k S) :
    ∀ n F, expTable D.T k n = some F → ∃ ss, (envAt D k).predicates n = some ss ∧
      F.WellFormed (envAt D 0) ss.reverse ∧
      ∀ vs, VE.TupleTyped S ss vs → (F.denote S (tupleVal vs) ↔ S.relation n vs) := by
  induction k using Nat.strongRecOn with
  | ind k ih =>
    intro n F hF
    obtain ⟨ss, hss, hFw⟩ := expTable_wellFormed hv k n F hF
    refine ⟨ss, hss, hFw, ?_⟩
    obtain ⟨j, q, hj, hq, rfl, rfl⟩ := expTable_some D.T k n F hF
    rw [envAt_earlier hv hq hj] at hss
    cases hss
    intro vs hvs
    rw [ha j q hj hq vs hvs]
    exact substWith_denote _ (envAt D j) (envAt D 0) S hc
      (ih j hj (fun j' q' hj' => ha j' q' (Nat.lt_trans hj' hj))) _ _ _
      (meaning_wellFormed hv hq) (tupleVal_typed S _ vs hvs)

/-- Substitution is sound on structures agreeing below `k` (internal form). -/
theorem subst_denote {D : Doc} (hv : Valid D) (k : Nat) (S : VE.Structure.{u})
    (hc : ConstantsTyped D S) (ha : AgreesBelow D k S) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt D k) Γ) (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
    (subst D.T k φ).denote S ρ ↔ φ.denote S ρ :=
  substWith_denote _ (envAt D k) (envAt D 0) S hc (expTable_sound hv S hc k ha) φ Γ ρ hφ hρ

/-- A base formula has the same truth in the base restriction. -/
theorem restrictAll_denote {D : Doc} (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt D 0) Γ) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    φ.denote (restrictAll D.T S) ρ ↔ φ.denote S ρ :=
  denote_forget (fun r hr => by simp [envAt, hide, hr]) S φ Γ ρ hφ

theorem subst_restrict_denote {D : Doc} (hv : Valid D) (k : Nat) (S : VE.Structure.{u})
    (hc : ConstantsTyped D S) (ha : AgreesBelow D k S) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt D k) Γ) (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
    (subst D.T k φ).denote (restrictAll D.T S) ρ ↔ φ.denote S ρ :=
  (restrictAll_denote _ Γ (subst_wellFormed hv k φ Γ hφ) S ρ).trans (subst_denote hv k S hc ha φ Γ hφ ρ hρ)

end VE.Norms
