import VE.Norms.Once

/-! The conditions of the metatheory (`Valid`), derived from the executable
`WellFormed`, and the prefix-environment facts they give: `envAt D k` declares
exactly the base vocabulary and the layer symbols placed before `k`. -/
namespace VE.Norms
open VE.Route

theorem nodup_getElem_inj {α : Type} {l : List α} (h : l.Nodup) {i j : Nat} (hi : i < l.length)
    (hj : j < l.length) (e : l[i] = l[j]) : i = j := by
  have hp := List.pairwise_iff_getElem.mp (List.nodup_iff_pairwise_ne.mp h)
  rcases Nat.lt_trichotomy i j with hlt | heq | hgt
  · exact absurd e (hp i j hi hj hlt)
  · exact heq
  · exact absurd e.symm (hp j i hj hi hgt)

theorem nodup_getElemOpt_inj {α : Type} {l : List α} (h : l.Nodup) {i j : Nat} {a : α}
    (hi : l[i]? = some a) (hj : l[j]? = some a) : i = j := by
  obtain ⟨hi', ei⟩ := List.getElem?_eq_some_iff.mp hi
  obtain ⟨hj', ej⟩ := List.getElem?_eq_some_iff.mp hj
  exact nodup_getElem_inj h hi' hj' (ei.trans ej.symm)

theorem isOk_ok {ε α : Type} {x : Except ε α} (h : x.isOk = true) : ∃ a, x = .ok a := by
  cases x with
  | error _ => cases h
  | ok a => exact ⟨a, rfl⟩

/-- The facts about a well-formed document that the proofs use. -/
structure Valid (D : Doc) : Prop where
  precedence : ∃ o, dependencyOrder (precedenceNodes D.T) = .ok o
  stratum : ∃ o, dependencyOrder (stratumNodes D.T) = .ok o
  nodup : (layerNames D.T).Nodup
  decl : ∀ q ∈ syms D.T, D.E.predicates q.name = some q.sorts ∧ Arity q.sorts ∧
    ∀ s ∈ q.sorts, s ∈ D.E.sorts
  typed : ∀ (k : Nat) (q : Sym), (syms D.T)[k]? = some q → ∀ φ ∈ q.formulas D.T,
    φ.WellFormed (envAt D k) q.sorts.reverse
  regulated : ∀ r ∈ D.T.regulated, Sym.reg r ∈ syms D.T
  pairs : ∀ pr ∈ pairs D.T, pr.req ≠ pr.perm ∧
    (∃ r, Sym.reg r ∈ syms D.T ∧ r.name = pr.req ∧ r.sorts = pr.sorts) ∧
    (∃ m, Sym.reg m ∈ syms D.T ∧ m.name = pr.perm ∧ m.sorts = pr.sorts)

theorem valid_of_semanticCheck (D : Doc) (h : semanticCheck D = true) : Valid D := by
  simp only [semanticCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    beq_iff_eq, Bool.or_eq_true, List.contains_iff_mem, List.mem_range, List.any_eq_true,
    bne_iff_ne, ne_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨hpo, hso⟩, hn⟩, hd⟩, ht⟩, hr⟩, hp⟩ := h
  refine ⟨isOk_ok hpo, isOk_ok hso, hn, fun q hq => ?_, fun k q hk φ hφ => ?_, hr, fun pr hpr => ?_⟩
  · obtain ⟨⟨h₁, h₂⟩, h₃⟩ := hd q hq
    exact ⟨h₁, h₂, h₃⟩
  · have hlt : k < (syms D.T).length := (List.getElem?_eq_some_iff.mp hk).1
    have := ht k hlt
    rw [hk] at this
    simp only [List.all_eq_true] at this
    exact (VE.check_iff_wellFormed _ _ _).mp (this φ hφ)
  · obtain ⟨⟨hne, ⟨r, hr, hrn⟩⟩, ⟨m, hm, hmn⟩⟩ := hp pr hpr
    refine ⟨hne, ?_, ?_⟩
    · cases r with
      | reg r =>
        simp only [Bool.and_eq_true, beq_iff_eq] at hrn
        exact ⟨r, hr, hrn.1, hrn.2⟩
      | defn _ => simp at hrn
    · cases m with
      | reg m =>
        simp only [Bool.and_eq_true, beq_iff_eq] at hmn
        exact ⟨m, hm, hmn.1, hmn.2⟩
      | defn _ => simp at hmn

theorem valid_of_wellFormed (D : Doc) (h : WellFormed D = true) : Valid D :=
  valid_of_semanticCheck D (semanticCheck_of_wellFormed D h)

/-- `precedence_acyclic`: both DAGs of a well-formed document are acyclic
(through the shared `VE.Route.dependencyOrder` and its `dag_acyclic`). -/
theorem precedence_acyclic (D : Doc) (h : WellFormed D = true) :
    DagAcyclic (precedenceNodes D.T) ∧ DagAcyclic (stratumNodes D.T) := by
  have hv := valid_of_wellFormed D h
  obtain ⟨o, ho⟩ := hv.precedence
  obtain ⟨o', ho'⟩ := hv.stratum
  exact ⟨(dag_acyclic _ _ ho).2.2.2, (dag_acyclic _ _ ho').2.2.2⟩

/-! ## Prefix environments -/

theorem names_getElemOpt {T : Tree} {k : Nat} {q : Sym} (hk : (syms T)[k]? = some q) :
    (layerNames T)[k]? = some q.name := by
  simp [layerNames, List.getElem?_map, hk]

/-- A layer symbol's name is among the names dropped at `k` exactly when it is
placed at or after `k`. -/
theorem mem_drop_names {D : Doc} (hv : Valid D) {j k : Nat} {q : Sym}
    (hj : (syms D.T)[j]? = some q) : q.name ∈ (layerNames D.T).drop k ↔ k ≤ j := by
  constructor
  · intro hm
    obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hm
    rw [List.getElem?_drop] at hi
    have := nodup_getElemOpt_inj hv.nodup hi (names_getElemOpt hj)
    omega
  · intro hkj
    apply List.mem_iff_getElem?.mpr
    refine ⟨j - k, ?_⟩
    rw [List.getElem?_drop, Nat.add_sub_cancel' hkj]
    exact names_getElemOpt hj

theorem envAt_sorts (D : Doc) (k : Nat) : (envAt D k).sorts = D.E.sorts := rfl
theorem envAt_constants (D : Doc) (k : Nat) : (envAt D k).constants = D.E.constants := rfl

theorem envAt_later {D : Doc} (hv : Valid D) {j k : Nat} {q : Sym} (hj : (syms D.T)[j]? = some q)
    (hkj : k ≤ j) : (envAt D k).predicates q.name = none := by
  simp [envAt, hide, (mem_drop_names hv hj).mpr hkj]

theorem envAt_earlier {D : Doc} (hv : Valid D) {j k : Nat} {q : Sym}
    (hj : (syms D.T)[j]? = some q) (hkj : j < k) :
    (envAt D k).predicates q.name = some q.sorts := by
  have : q.name ∉ (layerNames D.T).drop k := fun h => by
    have := (mem_drop_names hv hj).mp h; omega
  simp only [envAt, hide, this, if_false]
  exact (hv.decl q (List.mem_of_getElem? hj)).1

theorem mem_syms_index {D : Doc} {q : Sym} (hq : q ∈ syms D.T) :
    ∃ k : Nat, (syms D.T)[k]? = some q :=
  List.mem_iff_getElem?.mp hq

theorem envAt_base {D : Doc} {k : Nat} {r : String} (hr : r ∉ layerNames D.T) :
    (envAt D k).predicates r = D.E.predicates r := by
  have : r ∉ (layerNames D.T).drop k := fun h => hr (List.mem_of_mem_drop h)
  simp [envAt, hide, this]

theorem envAt_mono {D : Doc} {k k' : Nat} (hk : k ≤ k') (a : VE.Formula) (Γ : List String)
    (h : a.WellFormed (envAt D k) Γ) : a.WellFormed (envAt D k') Γ := by
  apply wf_hide_mono D.E _ a Γ h
  intro r hr
  have : (layerNames D.T).drop k' = ((layerNames D.T).drop k).drop (k' - k) := by
    rw [List.drop_drop, Nat.add_sub_cancel' hk]
  rw [this] at hr
  exact List.mem_of_mem_drop hr

/-- The predicates declared in `envAt D k` are declared in `E` with the same sorts. -/
theorem envAt_sub (D : Doc) (k : Nat) (r : String) (ss : List String)
    (h : (envAt D k).predicates r = some ss) : D.E.predicates r = some ss := by
  simp only [envAt, hide] at h
  split at h
  · cases h
  · exact h

/-- The whole layer order has been placed at `size D`. -/
theorem envAt_size_predicates (D : Doc) (r : String) :
    (envAt D (size D)).predicates r = D.E.predicates r := by
  have : (layerNames D.T).drop (size D) = [] := by
    simp [size, layerNames]
  simp [envAt, hide, this]

/-- Every symbol not yet placed at `k` is hidden in `envAt D k`. -/
theorem later_hidden (D : Doc) (k : Nat) : ∀ r ∈ (layerNames D.T).drop k,
    (envAt D k).predicates r = none := by
  intro r hr
  simp [envAt, hide, hr]

theorem self_hidden {D : Doc} (hv : Valid D) {k : Nat} {q : Sym} (hk : (syms D.T)[k]? = some q) :
    ∀ r ∈ [q.name], (envAt D k).predicates r = none := by
  intro r hr
  rw [List.mem_singleton.mp hr]
  exact envAt_later hv hk (Nat.le_refl k)

end VE.Norms
