import VE.Norms.Subst

/-! Prefix satisfaction (docs/spec/norms.md 6.1): the admissibility of the
prefix `E_i` of the route, independent of any `Layer` value and of any
conflict-freedom hypothesis.

`PrefixAdmissible D (i+1) S` asks for structural admissibility over `E_(i+1)`,
the lower prefix after forgetting `q_(i+1)`, the meaning of `q_(i+1)` itself
(`IntendedAt` for a regulated predicate, the biconditional for a definition)
and every profile premise closed at `q_(i+1)`. `prefix_satisfaction` says this
is exactly admissibility, a base-admissible base restriction and the prefix's
premises. -/
namespace VE.Norms
universe u

/-- A structure satisfies every formula of a list. -/
def Sat (S : VE.Structure.{u}) (as : List VE.Formula) : Prop := ∀ a ∈ as, a.denote S []

/-- The profile premise `∀x̄. r(x̄) → m(x̄)` of a declared pair (Python `ve/background.py`). -/
def Pair.premise (pr : Pair) : VE.Formula :=
  bindAll pr.sorts (.implies (atom pr.req pr.sorts) (atom pr.perm pr.sorts))

def pairPremises (T : Tree) : List VE.Formula := (pairs T).map Pair.premise

/-- The position of a layer symbol in the DAG order. -/
def idx (T : Tree) (n : String) : Nat := (layerNames T).idxOf n

/-- The position at which a pair closes: that of its later member. -/
def Pair.closes (T : Tree) (pr : Pair) : Nat := max (idx T pr.req) (idx T pr.perm)

/-- The pairs whose later member is placed at `k`. -/
def pairsAt (T : Tree) (k : Nat) : List Pair := (pairs T).filter (fun pr => pr.closes T == k)

/-- `Background_base`: flags (none before W5) and literal distinctness. -/
def backgroundBase (D : Doc) : List VE.Formula := VE.Route.Background.literals D.lits

/-- The complete regenerated Background in the P0 generator order: flags,
definitions, literals, profile. -/
def background (D : Doc) : List VE.Formula :=
  definitionPremises D.T ++ backgroundBase D ++ pairPremises D.T

/-- Structural admissibility over `E_base` plus `Background_base`. -/
def BaseAdmissible (D : Doc) (B : VE.Structure.{u}) : Prop :=
  B.Admissible (envAt D 0) ∧ Sat B (backgroundBase D)

/-- The meaning of one layer symbol, as the spec states it. -/
def LayerMeaning (T : Tree) (S : VE.Structure.{u}) : Sym → Prop
  | .reg r => IntendedAt T r S
  | .defn d => ∀ vs, VE.TupleTyped S d.args vs →
      (S.relation d.name vs ↔ d.body.denote S (tupleVal vs))

def PrefixAdmissible (D : Doc) : Nat → VE.Structure.{u} → Prop
  | 0, S => BaseAdmissible D S
  | k + 1, S => match (syms D.T)[k]? with
    | none => False
    | some q => S.Admissible (envAt D (k + 1)) ∧ PrefixAdmissible D k (forget [q.name] S) ∧
        LayerMeaning D.T S q ∧ Sat S ((pairsAt D.T k).map Pair.premise)

/-- The first `i` layer premises and every pair premise closed in the prefix. -/
def PrefixPremises (D : Doc) (i : Nat) : List VE.Formula :=
  ((syms D.T).take i).map (Sym.premise D.T) ++
    ((pairs D.T).filter (fun pr => decide (pr.closes D.T < i))).map Pair.premise

/-! ## The uniform meaning -/

/-- No opposite selections, and the relation agrees with the meaning formula. -/
def Meaning (T : Tree) (q : Sym) (S : VE.Structure.{u}) : Prop :=
  ∀ vs, VE.TupleTyped S q.sorts vs →
    ¬ (q.clash T).denote S (tupleVal vs) ∧
      (S.relation q.name vs ↔ (q.meaning T).denote S (tupleVal vs))

def MeaningsBelow (D : Doc) (k : Nat) (S : VE.Structure.{u}) : Prop :=
  ∀ j q, j < k → (syms D.T)[j]? = some q → Meaning D.T q S

def PairsBelow (D : Doc) (k : Nat) (S : VE.Structure.{u}) : Prop :=
  ∀ pr ∈ pairs D.T, pr.closes D.T < k → pr.premise.denote S []

theorem body_iff_clash (P N R : Prop) (d : Bool) :
    ((P → R) ∧ (N → ¬ R) ∧ (¬ P ∧ ¬ N → (R ↔ d = true))) ↔
      (¬ (P ∧ N) ∧ (R ↔ if d then ¬ N else P)) := by
  classical
  by_cases hP : P <;> by_cases hN : N <;> cases d <;> simp_all

theorem elabPremise_iff_meaning (T : Tree) (r : Regulated) (ha : Arity r.sorts)
    (S : VE.Structure.{u}) : (elabPremise T r).denote S [] ↔ Meaning T (.reg r) S := by
  rw [elabPremise, bindAll_denote_nil]
  apply forall_congr'
  intro vs
  apply imp_congr_right
  intro hv
  rw [elabBody_denote T r ha S vs hv, body_iff_clash]
  simp only [Sym.clash, Sym.meaning, Sym.name, VE.Formula.denote, outcome_denote]

theorem definition_premise_iff (d : Definition) (ha : Arity d.args) (S : VE.Structure.{u}) :
    d.premise.denote S [] ↔
      ∀ vs, VE.TupleTyped S d.args vs → (S.relation d.name vs ↔ d.body.denote S (tupleVal vs)) := by
  rw [Definition.premise, bindAll_denote_nil]
  apply forall_congr'
  intro vs
  apply imp_congr_right
  intro hv
  rw [iffF_denote, atom_denote S d.name d.args ha vs hv]

theorem premise_iff_meaning {D : Doc} (hv : Valid D) {k : Nat} {q : Sym}
    (hk : (syms D.T)[k]? = some q) (S : VE.Structure.{u}) :
    (q.premise D.T).denote S [] ↔ Meaning D.T q S := by
  cases q with
  | reg r => exact elabPremise_iff_meaning D.T r (sym_arity hv hk) S
  | defn d =>
    rw [Sym.premise, definition_premise_iff d (sym_arity hv hk)]
    simp [Meaning, Sym.clash, Sym.meaning, Sym.name, Sym.sorts, VE.Formula.denote]

theorem layerMeaning_iff {D : Doc} (hv : Valid D) {k : Nat} {q : Sym}
    (hk : (syms D.T)[k]? = some q) (S : VE.Structure.{u}) :
    LayerMeaning D.T S q ↔ Meaning D.T q S := by
  cases q with
  | reg r =>
    rw [LayerMeaning, ← elab_iff_intended D.T r (sym_arity hv hk) S
      (decides_forget hv hk [r.name] (self_hidden hv hk) S)]
    exact elabPremise_iff_meaning D.T r (sym_arity hv hk) S
  | defn d =>
    simp [LayerMeaning, Meaning, Sym.clash, Sym.meaning, Sym.name, Sym.sorts, VE.Formula.denote]

theorem pair_premise_iff (pr : Pair) (ha : Arity pr.sorts) (S : VE.Structure.{u}) :
    pr.premise.denote S [] ↔
      ∀ vs, VE.TupleTyped S pr.sorts vs → S.relation pr.req vs → S.relation pr.perm vs := by
  rw [Pair.premise, bindAll_denote_nil]
  apply forall_congr'
  intro vs
  apply imp_congr_right
  intro hv
  simp only [VE.Formula.denote, atom_denote S _ _ ha vs hv]

/-! ## Positions -/

theorem idxOf_eq_of_getElem? {l : List String} (h : l.Nodup) :
    ∀ {j : Nat} {a : String}, l[j]? = some a → l.idxOf a = j := by
  induction l with
  | nil => intro j a h; simp at h
  | cons b l ih =>
    intro j a hj
    obtain ⟨hb, hl⟩ := List.nodup_cons.mp h
    cases j with
    | zero =>
      simp only [List.getElem?_cons_zero, Option.some.injEq] at hj
      subst hj
      exact List.idxOf_cons_self
    | succ j =>
      simp only [List.getElem?_cons_succ] at hj
      have hne : (b == a) = false := by
        simp only [beq_eq_false_iff_ne]
        exact fun e => hb (e ▸ List.mem_of_getElem? hj)
      rw [List.idxOf_cons, hne, ih hl hj]
      rfl

theorem idx_eq {D : Doc} (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q) :
    idx D.T q.name = k :=
  idxOf_eq_of_getElem? hv.nodup (getElem?_names hk)

theorem before_eq {D : Doc} (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q) :
    before D q.name = k :=
  idx_eq hv hk

/-- Both members of a declared pair are regulated layer symbols with the pair's sorts. -/
theorem pair_members {D : Doc} (hv : Valid D) {pr : Pair} (hpr : pr ∈ pairs D.T) :
    pr.req ≠ pr.perm ∧
    (∃ i r, (syms D.T)[i]? = some (.reg r) ∧ r.name = pr.req ∧ r.sorts = pr.sorts ∧
      idx D.T pr.req = i) ∧
    (∃ j m, (syms D.T)[j]? = some (.reg m) ∧ m.name = pr.perm ∧ m.sorts = pr.sorts ∧
      idx D.T pr.perm = j) := by
  obtain ⟨hne, ⟨r, hr, hrn, hrs⟩, ⟨m, hm, hmn, hms⟩⟩ := hv.pairs pr hpr
  obtain ⟨i, hi⟩ := mem_syms_getElem? hr
  obtain ⟨j, hj⟩ := mem_syms_getElem? hm
  exact ⟨hne, ⟨i, r, hi, hrn, hrs, hrn ▸ idx_eq hv hi⟩, ⟨j, m, hj, hmn, hms, hmn ▸ idx_eq hv hj⟩⟩

theorem pair_arity {D : Doc} (hv : Valid D) {pr : Pair} (hpr : pr ∈ pairs D.T) : Arity pr.sorts := by
  obtain ⟨_, ⟨i, r, hi, _, hrs, _⟩, _⟩ := pair_members hv hpr
  exact hrs ▸ sym_arity hv hi

theorem pair_premise_wellFormed {D : Doc} (hv : Valid D) {pr : Pair} (hpr : pr ∈ pairs D.T)
    {k : Nat} (hk : pr.closes D.T < k) : pr.premise.WellFormed (envAt D k) [] := by
  obtain ⟨_, ⟨i, r, hi, hrn, hrs, hri⟩, ⟨j, m, hj, hmn, hms, hmj⟩⟩ := pair_members hv hpr
  have hik : i < k := by simp only [Pair.closes] at hk; omega
  have hjk : j < k := by simp only [Pair.closes] at hk; omega
  have hsorts := (hv.decl _ (List.mem_of_getElem? hi)).2.2
  apply bindAll_wellFormed (E := envAt D k) (fun s hs => hsorts s (by simpa [Sym.sorts, hrs] using hs)) [] _
  simp only [List.append_nil]
  have ha := pair_arity hv hpr
  refine ⟨atom_wellFormed ha ?_, atom_wellFormed ha ?_⟩
  · have := envAt_earlier hv hi hik
    simpa [Sym.name, Sym.sorts, hrn, hrs] using this
  · have := envAt_earlier hv hj hjk
    simpa [Sym.name, Sym.sorts, hmn, hms] using this

theorem pair_closes_lt_size {D : Doc} (hv : Valid D) {pr : Pair} (hpr : pr ∈ pairs D.T) :
    pr.closes D.T < size D := by
  obtain ⟨_, ⟨i, _, hi, _, _, hri⟩, ⟨j, _, hj, _, _, hmj⟩⟩ := pair_members hv hpr
  have h₁ := (List.getElem?_eq_some_iff.mp hi).1
  have h₂ := (List.getElem?_eq_some_iff.mp hj).1
  simp only [Pair.closes, size]
  omega

/-! ## Environments and forgetting along the prefix -/

theorem envAt_succ {D : Doc} {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q) :
    envAt D k = hide (envAt D (k + 1)) [q.name] := by
  have hlt : k < (layerNames D.T).length := by
    simpa [layerNames] using (List.getElem?_eq_some_iff.mp hk).1
  have hd : (layerNames D.T).drop k = q.name :: (layerNames D.T).drop (k + 1) := by
    rw [List.drop_eq_getElem_cons hlt]
    congr 1
    have := getElem?_names hk
    rw [List.getElem?_eq_getElem hlt] at this
    exact Option.some.inj this
  simp only [envAt, hide, hd]
  congr 1
  funext r
  by_cases h₁ : r = q.name <;> simp [h₁]

theorem forget_admissible_succ {D : Doc} {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q)
    (S : VE.Structure.{u}) (h : S.Admissible (envAt D (k + 1))) :
    (forget [q.name] S).Admissible (envAt D k) := by
  rw [envAt_succ hk]
  exact forget_admissible _ _ S h

theorem restrictAll_forget {T : Tree} {n : String} (hn : n ∈ layerNames T) (S : VE.Structure.{u}) :
    restrictAll T (forget [n] S) = restrictAll T S := by
  unfold restrictAll
  rw [forget_forget]
  apply forget_congr
  intro r
  simp only [List.mem_append, List.mem_singleton]
  constructor
  · rintro (h | rfl)
    · exact h
    · exact hn
  · exact Or.inl

theorem name_mem_layerNames {T : Tree} {k : Nat} {q : Sym} (hk : (syms T)[k]? = some q) :
    q.name ∈ layerNames T :=
  List.mem_of_getElem? (getElem?_names hk)

/-- A base-admissible structure has no tuple of a layer symbol. -/
theorem restrictAll_self {D : Doc} (S : VE.Structure.{u}) (h : S.Admissible (envAt D 0)) :
    restrictAll D.T S = S := by
  apply forget_eq_self
  intro r vs hr hmem
  obtain ⟨ss, hss, _⟩ := h.2 r vs hr
  simp [envAt, hide, hmem] at hss

theorem restrictAll_admissible {D : Doc} (k : Nat) (S : VE.Structure.{u})
    (h : S.Admissible (envAt D k)) : (restrictAll D.T S).Admissible (envAt D 0) := by
  refine ⟨h.1, fun r vs hr => ?_⟩
  obtain ⟨hn, hr⟩ := hr
  obtain ⟨ss, hss, ht⟩ := h.2 r vs hr
  refine ⟨ss, ?_, (tupleTyped_forget _ S ss vs).mpr ht⟩
  rw [envAt_base hn]
  exact envAt_sub D k r ss hss

theorem sat_literals_forget (lits : List String) (ns : List String) (S : VE.Structure.{u}) :
    Sat (forget ns S) (VE.Route.Background.literals lits) ↔ Sat S (VE.Route.Background.literals lits) := by
  simp only [Sat, VE.Route.Background.literals, List.mem_map, forall_exists_index, and_imp,
    forall_apply_eq_imp_iff₂, VE.Route.Background.literalPremise_denote]
  rfl

/-- The meaning of an earlier symbol is unaffected by forgetting a later one. -/
theorem meaning_forget {D : Doc} (hv : Valid D) {j k : Nat} {q q' : Sym} (hj : (syms D.T)[j]? = some q)
    (hk : (syms D.T)[k]? = some q') (hjk : j < k) (S : VE.Structure.{u}) :
    Meaning D.T q (forget [q'.name] S) ↔ Meaning D.T q S := by
  have hne : q.name ≠ q'.name := fun e => by
    have := nodup_getElem?_inj hv.nodup (getElem?_names hj) (e ▸ getElem?_names hk); omega
  have hid : ∀ r ∈ [q'.name], (envAt D j).predicates r = none := by
    intro r hr; rw [List.mem_singleton.mp hr]; exact envAt_later hv hk (Nat.le_of_lt hjk)
  unfold Meaning
  apply forall_congr'
  intro vs
  rw [tupleTyped_forget]
  apply imp_congr_right
  intro _
  rw [denote_forget hid S _ _ _ (clash_wellFormed hv hj),
    denote_forget hid S _ _ _ (meaning_wellFormed hv hj),
    forget_relation S (by simpa using hne)]

theorem pairsBelow_forget {D : Doc} (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q)
    (S : VE.Structure.{u}) : PairsBelow D k (forget [q.name] S) ↔ PairsBelow D k S := by
  unfold PairsBelow
  apply forall_congr'; intro pr
  apply forall_congr'; intro hpr
  apply forall_congr'; intro hlt
  exact denote_forget (self_hidden hv hk) S _ [] [] (pair_premise_wellFormed hv hpr hlt)

theorem meaningsBelow_forget {D : Doc} (hv : Valid D) {k : Nat} {q : Sym}
    (hk : (syms D.T)[k]? = some q) (S : VE.Structure.{u}) :
    MeaningsBelow D k (forget [q.name] S) ↔ MeaningsBelow D k S := by
  unfold MeaningsBelow
  apply forall_congr'; intro j
  apply forall_congr'; intro q'
  apply forall_congr'; intro hj
  apply forall_congr'; intro hq'
  exact meaning_forget hv hq' hk hj S

/-! ## Prefix satisfaction -/

theorem prefix_char {D : Doc} (hv : Valid D) :
    ∀ k, k ≤ size D → ∀ S : VE.Structure.{u}, PrefixAdmissible D k S ↔
      S.Admissible (envAt D k) ∧ BaseAdmissible D (restrictAll D.T S) ∧
        MeaningsBelow D k S ∧ PairsBelow D k S
  | 0, _, S => by
    simp only [PrefixAdmissible]
    constructor
    · intro h
      refine ⟨h.1, by rw [restrictAll_self S h.1]; exact h, fun _ _ hj => absurd hj (Nat.not_lt_zero _),
        fun _ _ hlt => absurd hlt (Nat.not_lt_zero _)⟩
    · rintro ⟨hA, hB, _, _⟩
      rw [restrictAll_self S hA] at hB
      exact hB
  | k + 1, hk, S => by
    have hlt : k < (syms D.T).length := hk
    obtain ⟨q, hq⟩ : ∃ q, (syms D.T)[k]? = some q := ⟨_, List.getElem?_eq_getElem hlt⟩
    have ih := prefix_char hv k (Nat.le_of_succ_le hk) (forget [q.name] S)
    rw [restrictAll_forget (name_mem_layerNames hq), meaningsBelow_forget hv hq,
      pairsBelow_forget hv hq] at ih
    simp only [PrefixAdmissible, hq]
    rw [ih, layerMeaning_iff hv hq]
    constructor
    · rintro ⟨hA, ⟨_, hB, hM, hP⟩, hL, hpairs⟩
      refine ⟨hA, hB, fun j q' hj hq' => ?_, fun pr hpr hc => ?_⟩
      · rcases Nat.lt_succ_iff_lt_or_eq.mp hj with hj | rfl
        · exact hM j q' hj hq'
        · rw [hq] at hq'; cases hq'; exact hL
      · rcases Nat.lt_succ_iff_lt_or_eq.mp hc with hc | hc
        · exact hP pr hpr hc
        · exact hpairs _ (List.mem_map.mpr ⟨pr, List.mem_filter.mpr ⟨hpr, by simp [hc]⟩, rfl⟩)
    · rintro ⟨hA, hB, hM, hP⟩
      refine ⟨hA, ⟨forget_admissible_succ hq S hA, hB, fun j q' hj hq' => hM j q' (Nat.lt_succ_of_lt hj) hq',
        fun pr hpr hc => hP pr hpr (Nat.lt_succ_of_lt hc)⟩, hM k q (Nat.lt_succ_self k) hq, ?_⟩
      intro a ha
      obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
      obtain ⟨hpr, hc⟩ := List.mem_filter.mp hpr
      exact hP pr hpr (by simp at hc; omega)

theorem sat_prefixPremises {D : Doc} (hv : Valid D) (k : Nat) (S : VE.Structure.{u}) :
    Sat S (PrefixPremises D k) ↔ MeaningsBelow D k S ∧ PairsBelow D k S := by
  simp only [Sat, PrefixPremises, List.mem_append, List.mem_map, List.mem_filter, decide_eq_true_eq]
  constructor
  · intro h
    refine ⟨fun j q hj hq => ?_, fun pr hpr hc => h _ (Or.inr ⟨pr, ⟨hpr, hc⟩, rfl⟩)⟩
    apply (premise_iff_meaning hv hq S).mp
    apply h
    refine Or.inl ⟨q, ?_, rfl⟩
    rw [List.mem_iff_getElem?]
    exact ⟨j, by rw [List.getElem?_take]; simp [hj, hq]⟩
  · rintro ⟨hM, hP⟩ a (⟨q, hq, rfl⟩ | ⟨pr, ⟨hpr, hc⟩, rfl⟩)
    · obtain ⟨j, hj⟩ := List.mem_iff_getElem?.mp hq
      rw [List.getElem?_take] at hj
      split at hj
      · rename_i hjk
        exact (premise_iff_meaning hv hj S).mpr (hM j q hjk hj)
      · cases hj
    · exact hP pr hpr hc

/-- `prefix_satisfaction`: a prefix-admissible structure is exactly an admissible
one whose base restriction is base-admissible and which satisfies the prefix's
premises. -/
theorem prefix_satisfaction (D : Doc) (h : WellFormed D = true) (i : Nat) (hi : i ≤ size D)
    (S : VE.Structure.{u}) :
    PrefixAdmissible D i S ↔ S.Admissible (envAt D i) ∧ BaseAdmissible D (restrictAll D.T S) ∧
      Sat S (PrefixPremises D i) := by
  have hv := valid_of_wellFormed D h
  rw [prefix_char hv i hi S, sat_prefixPremises hv i S]

theorem prefixAdmissible_admissible {D : Doc} {k : Nat} {S : VE.Structure.{u}}
    (h : PrefixAdmissible D k S) : S.Admissible (envAt D k) := by
  cases k with
  | zero => exact h.1
  | succ k =>
    simp only [PrefixAdmissible] at h
    split at h
    · exact h.elim
    · exact h.1

theorem prefixAdmissible_le {D : Doc} {k : Nat} {S : VE.Structure.{u}}
    (h : PrefixAdmissible D k S) : k ≤ size D := by
  cases k with
  | zero => exact Nat.zero_le _
  | succ k =>
    simp only [PrefixAdmissible] at h
    split at h
    · exact h.elim
    · rename_i q hq
      exact (List.getElem?_eq_some_iff.mp hq).1

/-- Meanings below `k` give the agreement that substitution needs. -/
theorem agreesBelow_of_meanings {D : Doc} {k : Nat} {S : VE.Structure.{u}}
    (h : MeaningsBelow D k S) : AgreesBelow D k S :=
  fun j q hj hq vs hvs => (h j q hj hq vs hvs).2

theorem constantsTyped_of_admissible {D : Doc} {k : Nat} {S : VE.Structure.{u}}
    (h : S.Admissible (envAt D k)) : ConstantsTyped D S := h.1

/-- The whole background and the norm elaborations say exactly: literals,
every layer meaning and every pair premise. -/
theorem sat_document {D : Doc} (hv : Valid D) (S : VE.Structure.{u}) :
    Sat S (background D ++ elaborate D.T) ↔
      Sat S (backgroundBase D) ∧ MeaningsBelow D (size D) S ∧ PairsBelow D (size D) S := by
  have hall : ∀ q ∈ syms D.T, (q.premise D.T).denote S [] ↔ Meaning D.T q S := by
    intro q hq
    obtain ⟨k, hk⟩ := mem_syms_getElem? hq
    exact premise_iff_meaning hv hk S
  have hprem : Sat S (definitionPremises D.T ++ elaborate D.T) ↔ ∀ q ∈ syms D.T, Meaning D.T q S := by
    simp only [Sat, List.mem_append, definitionPremises, elaborate, List.mem_filterMap]
    constructor
    · intro h q hq
      apply (hall q hq).mp
      cases q with
      | reg r => exact h _ (Or.inr ⟨.reg r, hq, rfl⟩)
      | defn d => exact h _ (Or.inl ⟨.defn d, hq, rfl⟩)
    · rintro h a (⟨q, hq, hqa⟩ | ⟨q, hq, hqa⟩)
      · cases q with
        | defn d => cases hqa; exact (hall _ hq).mpr (h _ hq)
        | reg _ => cases hqa
      · cases q with
        | reg r => cases hqa; exact (hall _ hq).mpr (h _ hq)
        | defn _ => cases hqa
  have hmb : MeaningsBelow D (size D) S ↔ ∀ q ∈ syms D.T, Meaning D.T q S := by
    constructor
    · intro h q hq
      obtain ⟨k, hk⟩ := mem_syms_getElem? hq
      exact h k q (List.getElem?_eq_some_iff.mp hk).1 hk
    · intro h j q _ hq
      exact h q (List.mem_of_getElem? hq)
  have hpb : PairsBelow D (size D) S ↔ Sat S (pairPremises D.T) := by
    simp only [PairsBelow, Sat, pairPremises, List.mem_map, forall_exists_index, and_imp,
      forall_apply_eq_imp_iff₂]
    exact ⟨fun h pr hpr => h pr hpr (pair_closes_lt_size hv hpr),
      fun h pr hpr _ => h pr hpr⟩
  rw [hmb, hpb, ← hprem]
  simp only [Sat, background, List.mem_append]
  constructor
  · intro h
    exact ⟨fun a ha => h a (Or.inl (Or.inl (Or.inr ha))),
      fun a ha => by
        rcases ha with ha | ha
        · exact h a (Or.inl (Or.inl (Or.inl ha)))
        · exact h a (Or.inr ha),
      fun a ha => h a (Or.inl (Or.inr ha))⟩
  · rintro ⟨h₁, h₂, h₃⟩ a ((((ha | ha)) | ha) | ha)
    · exact h₂ a (Or.inl ha)
    · exact h₁ a ha
    · exact h₃ a ha
    · exact h₂ a (Or.inr ha)

end VE.Norms
