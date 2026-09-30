import VE.NormDefaults.Fill

/-! `fill_wellFormed` (docs/spec/norm-defaults.md 7 and 8): the author-side limits
of `WellFormedU` suffice, so `fill` never produces a tree that W1's `validate`
rejects.

The proof walks `CheckOK` (W1's `check`, read declaratively in `Check.lean`) and
`semanticCheck` on `T‴`. Each `F_p` adds one rule (`WellFormedU` (iii)), one rule
name (`(i)`, `(ii)` and the unused-name condition), one guard (`(v)`) and one
precedence level above the roots on `p` (`(iv)`); its guard is typed because
`E‴` declares `unsaid__p` with `p`'s sorts; the precedence DAG stays acyclic
because `F_p` has no parent; and the stratum order is unchanged because
`unsaid__p` is a base predicate, not a node of the stratum DAG
(`dependencyOrder_congr`). -/
namespace VE.NormDefaults
open VE.Norms VE.Route
universe u

/-! ## Typing over `E‴` -/

theorem termSort_congr {E E' : VE.Environment} (hc : E'.constants = E.constants) (Γ : List String)
    (t : VE.Term) : termSort E' Γ t = termSort E Γ t := by
  cases t <;> simp [termSort, hc]

theorem typeDiagnostic_congr {E E' : VE.Environment} (hs : E'.sorts = E.sorts)
    (hc : E'.constants = E.constants) :
    ∀ (φ : VE.Formula) (Γ : List String), (∀ p ∈ preds φ, E'.predicates p = E.predicates p) →
      typeDiagnostic E' Γ φ = typeDiagnostic E Γ φ := by
  intro φ
  induction φ with
  | top | bottom => intros; rfl
  | unary p t =>
    intro Γ hp
    simp only [typeDiagnostic, hp p (by simp [preds]), termSort_congr hc]
  | binary p t w =>
    intro Γ hp
    simp only [typeDiagnostic, hp p (by simp [preds]), termSort_congr hc]
  | eq t w =>
    intro Γ _
    simp only [typeDiagnostic, termSort_congr hc]
  | not a ih =>
    intro Γ hp
    simp only [typeDiagnostic]
    exact ih Γ (by simpa [preds] using hp)
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ hp
    simp only [typeDiagnostic]
    rw [ia Γ (fun p h => hp p (by simp [preds, h])), ib Γ (fun p h => hp p (by simp [preds, h]))]
  | all s a ih | ex s a ih =>
    intro Γ hp
    simp only [typeDiagnostic, hs]
    rw [ih (s :: Γ) (by simpa [preds] using hp)]

/-- A typed formula mentions only declared predicates. -/
theorem preds_declared {E : VE.Environment} :
    ∀ (φ : VE.Formula) (Γ : List String), φ.WellFormed E Γ → ∀ p ∈ preds φ, ∃ ss, E.predicates p = some ss := by
  intro φ
  induction φ with
  | top | bottom => intro _ _ p hp; cases hp
  | unary q t =>
    intro Γ ⟨s, hq, _⟩ p hp
    simp only [preds, List.mem_singleton] at hp; subst hp; exact ⟨_, hq⟩
  | binary q t w =>
    intro Γ ⟨s, s', hq, _⟩ p hp
    simp only [preds, List.mem_singleton] at hp; subst hp; exact ⟨_, hq⟩
  | eq t w => intro _ _ p hp; cases hp
  | not a ih => intro Γ h p hp; exact ih Γ h p hp
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ h p hp
    rcases List.mem_append.mp hp with hp | hp
    · exact ia Γ h.1 p hp
    · exact ib Γ h.2 p hp
  | all s a ih | ex s a ih => intro Γ h p hp; exact ih _ h.2 p hp

section Env
variable {U : UDoc} (hu : UValid U)
include hu

/-- `E‴` agrees with `E` on every declared predicate. -/
theorem fillEnv_declared {n : String} {ss : List String} (hn : U.D.E.predicates n = some ss) :
    (fillEnv U).predicates n = U.D.E.predicates n :=
  fillEnv_off U (hu.not_unsaid hn)

theorem fillEnv_mono (n : String) (ss : List String) (hn : U.D.E.predicates n = some ss) :
    (fillEnv U).predicates n = some ss := by
  rw [fillEnv_declared hu hn, hn]

theorem typeDiagnostic_fill {Γ : List String} {φ : VE.Formula} (hφ : φ.WellFormed U.D.E Γ) :
    typeDiagnostic (fillEnv U) Γ φ = typeDiagnostic U.D.E Γ φ :=
  typeDiagnostic_congr (fillEnv_sorts U) (fillEnv_constants U) φ Γ fun p hp => by
    obtain ⟨ss, hss⟩ := preds_declared φ Γ hφ p hp
    exact fillEnv_declared hu hss

theorem check_fill {Γ : List String} {φ : VE.Formula} (h : VE.Formula.check U.D.E Γ φ = true) :
    VE.Formula.check (fillEnv U) Γ φ = true := by
  rw [VE.check_iff_wellFormed] at h ⊢
  exact wf_mono (fillEnv_sorts U) (fillEnv_constants U) (fillEnv_mono hu) φ Γ h

end Env

/-! ## Heights -/

theorem foldl_max_le {l : List Nat} {B : Nat} (h : ∀ x ∈ l, x ≤ B) : ∀ acc, acc ≤ B → l.foldl max acc ≤ B := by
  induction l with
  | nil => intro acc hacc; exact hacc
  | cons x l ih =>
    intro acc hacc
    simp only [List.foldl_cons]
    exact ih (fun y hy => h y (List.mem_cons_of_mem _ hy)) _ (Nat.max_le.mpr ⟨hacc, h x List.mem_cons_self⟩)

theorem height_fillRoot (U : UDoc) (T : Tree) (f : Nat) (N : Node) :
    height T f (fillRoot U N) = height T f N := by
  cases f <;> simp only [height, children_fillRoot]

theorem height_stable {T : Tree} (hac : DagAcyclic (precedenceNodes T)) :
    ∀ (f g : Nat) (N : Node), N ∈ T.nodes → belowCount T N ≤ f → belowCount T N ≤ g →
      height T f N = height T g N
  | 0, 0, _, _, _, _ => rfl
  | 0, g + 1, N, hN, hf, _ => by
    have : children T N = [] := List.eq_nil_iff_forall_not_mem.mpr fun C hC => by
      have := belowCount_child hac hN hC; omega
    simp [height, this]
  | f + 1, 0, N, hN, _, hg => by
    have : children T N = [] := List.eq_nil_iff_forall_not_mem.mpr fun C hC => by
      have := belowCount_child hac hN hC; omega
    simp [height, this]
  | f + 1, g + 1, N, hN, hf, hg => by
    simp only [height]
    congr 2
    apply List.map_congr_left
    intro C hC
    have := belowCount_child hac hN hC
    exact height_stable hac f g C (mem_children_iff.mp hC).1 (by omega) (by omega)

section Heights
variable {U : UDoc} (hu : UValid U)
include hu

theorem height_fill_author : ∀ (f : Nat) (N : Node), N ∈ U.D.T.nodes →
    height (fill U).T f N = height U.D.T f N
  | 0, _, _ => rfl
  | f + 1, N, hN => by
    simp only [height]
    rw [children_fill_author hu hN]
    congr 2
    apply List.map_congr_left
    intro C hC
    exact height_fill_author f C (mem_children_iff.mp hC).1

/-- The precedence DAG of `T‴` is acyclic: `F_p` has no parent, and every other
edge is an edge of `T`. -/
theorem fill_acyclic : DagAcyclic (precedenceNodes (fill U).T) := by
  have hac := hu.acyclic
  have hnoout : ∀ a b, DepEdge (precedenceNodes (fill U).T) a b → a ∉ U.unspec.map fillName ∧
      (b ∈ U.unspec.map fillName ∨ DepEdge (precedenceNodes U.D.T) a b) := by
    rintro a b ⟨n, hn, rfl, hb⟩
    obtain ⟨N, hN, rfl⟩ := List.mem_map.mp hn
    rw [mem_deps] at hb
    obtain ⟨hbo, _⟩ := hb
    rcases mem_fill_nodes.mp hN with ⟨N₀, hN₀, rfl⟩ | hN
    · refine ⟨by simpa using hu.freshRule N₀ hN₀, ?_⟩
      rcases fillRoot_over U N₀ with ⟨hp, _, ho⟩ | ⟨_, he⟩
      · simp only [ho, List.mem_singleton] at hbo
        exact Or.inl (hbo ▸ List.mem_map_of_mem hp)
      · rw [he] at hbo ⊢
        obtain ⟨M, hM, rfl, _⟩ := hu.over_node hN₀ hbo
        exact Or.inr (over_edge hN₀ hM hbo)
    · obtain ⟨r, _, _, rfl⟩ := mem_fillNodes.mp hN
      simp [fillNode] at hbo
  have hpath : ∀ a c, DepPath (precedenceNodes (fill U).T) a c → a ∉ U.unspec.map fillName ∧
      (c ∈ U.unspec.map fillName ∨ DepPath (precedenceNodes U.D.T) a c) := by
    intro a c hp
    induction hp with
    | edge he =>
      obtain ⟨ha, hb⟩ := hnoout _ _ he
      exact ⟨ha, hb.imp id DepPath.edge⟩
    | trans _ _ ih₁ ih₂ =>
      obtain ⟨ha, hab⟩ := ih₁
      obtain ⟨hb, hbc⟩ := ih₂
      refine ⟨ha, ?_⟩
      rcases hab with hab | hab
      · exact absurd hab hb
      · exact hbc.imp id (DepPath.trans hab)
  intro a hp
  obtain ⟨ha, h⟩ := hpath a a hp
  rcases h with h | h
  · exact ha h
  · exact hac a h

end Heights

/-! ## List facts -/

theorem nodup_of_count : ∀ {l : List String}, (∀ x ∈ l, l.count x ≤ 1) → l.Nodup
  | [], _ => List.nodup_nil
  | a :: l, h => by
    refine List.nodup_cons.mpr ⟨fun ha => ?_, nodup_of_count fun x hx => ?_⟩
    · have := h a List.mem_cons_self
      rw [List.count_cons_self] at this
      have := List.count_pos_iff.mpr ha
      omega
    · have := h x (List.mem_cons_of_mem _ hx)
      rw [List.count_cons] at this
      omega

theorem nodup_of_dupNameOf {l : List String} (h : dupNameOf l = none) : l.Nodup := by
  apply nodup_of_count
  intro x hx
  have := List.find?_eq_none.mp h x hx
  simp only [decide_eq_true_eq] at this
  omega

theorem inj_of_nodup_map {α β : Type} {f : α → β} : ∀ {l : List α}, (l.map f).Nodup →
    ∀ x ∈ l, ∀ y ∈ l, f x = f y → x = y
  | [], _, _, hx, _, _, _ => absurd hx List.not_mem_nil
  | a :: l, h, x, hx, y, hy, e => by
    simp only [List.map_cons, List.nodup_cons, List.mem_map] at h
    rcases List.mem_cons.mp hx with hx' | hx' <;> rcases List.mem_cons.mp hy with hy' | hy'
    · rw [hx', hy']
    · subst hx'; exact absurd ⟨y, hy', e.symm⟩ h.1
    · subst hy'; exact absurd ⟨x, hx', e⟩ h.1
    · exact inj_of_nodup_map h.2 x hx' y hy' e

theorem nodup_map_of_inj {α β : Type} {f : α → β} : ∀ {l : List α}, l.Nodup →
    (∀ x ∈ l, ∀ y ∈ l, f x = f y → x = y) → (l.map f).Nodup
  | [], _, _ => List.nodup_nil
  | a :: l, h, hi => by
    obtain ⟨ha, hl⟩ := List.nodup_cons.mp h
    refine List.nodup_cons.mpr ⟨fun hm => ?_, nodup_map_of_inj hl fun x hx y hy => hi x
      (List.mem_cons_of_mem _ hx) y (List.mem_cons_of_mem _ hy)⟩
    obtain ⟨b, hb, e⟩ := List.mem_map.mp hm
    exact ha (hi b (List.mem_cons_of_mem _ hb) a List.mem_cons_self e ▸ hb)

theorem sum_map_erase {g : String → Nat} : ∀ {L : List String} {a : String}, a ∈ L →
    (L.map g).sum = g a + ((L.erase a).map g).sum
  | [], _, h => absurd h List.not_mem_nil
  | b :: L, a, h => by
    by_cases hab : b = a
    · subst hab; simp
    · rw [List.erase_cons_tail (by simpa using hab)]
      have ha : a ∈ L := by
        rcases List.mem_cons.mp h with h | h
        · exact absurd h.symm hab
        · exact h
      simp only [List.map_cons, List.sum_cons, sum_map_erase ha]
      omega

theorem sum_map_le {g : String → Nat} : ∀ {l L : List String}, l.Nodup → (∀ x ∈ l, x ∈ L) →
    (l.map g).sum ≤ (L.map g).sum
  | [], _, _, _ => by simp
  | a :: l, L, hn, hs => by
    obtain ⟨ha, hl⟩ := List.nodup_cons.mp hn
    have haL := hs a List.mem_cons_self
    have hsub : ∀ x ∈ l, x ∈ L.erase a := fun x hx =>
      (List.mem_erase_of_ne (fun (e : x = a) => ha (e ▸ hx))).mpr (hs x (List.mem_cons_of_mem _ hx))
    have := sum_map_le (g := g) hl hsub
    rw [sum_map_erase haL]
    simp only [List.map_cons, List.sum_cons]
    omega

theorem sum_append_nat : ∀ (l₁ l₂ : List Nat), (l₁ ++ l₂).sum = l₁.sum + l₂.sum
  | [], _ => by simp
  | a :: l, l₂ => by simp only [List.cons_append, List.sum_cons, sum_append_nat l l₂]; omega

theorem eq_of_name {l : List Node} (h : (l.map Node.name).Nodup) {a b : Node} (ha : a ∈ l) (hb : b ∈ l)
    (e : a.name = b.name) : a = b :=
  inj_of_nodup_map h a ha b hb e

theorem find_of_name {l : List Node} {m : String} {M : Node} (hM : M ∈ l) (hm : M.name = m) :
    ∃ M', l.find? (fun x => x.name == m) = some M' ∧ M' ∈ l ∧ M'.name = m := by
  cases hf : l.find? (fun x => x.name == m) with
  | none => exact absurd hf (by rw [List.find?_eq_none]; intro h; exact h M hM (by simp [hm]))
  | some M' => exact ⟨M', rfl, List.mem_of_find?_eq_some hf, by simpa using List.find?_some hf⟩

/-! ## `check` on `T‴` -/

section Check
variable {U : UDoc} (hu : UValid U)
include hu

theorem regulatedNames_nodup : (regulatedNames U.D.T).Nodup :=
  (List.nodup_append.mp (nodup_of_dupNameOf hu.ok.2.1)).1

/-- The regulated declarations of the unspecified predicates. -/
theorem fillRegs_names :
    ((U.D.T.regulated.filter (fun r => r.name ∈ U.unspec)).map Regulated.name).Nodup ∧
    ∀ p ∈ (U.D.T.regulated.filter (fun r => r.name ∈ U.unspec)).map Regulated.name, p ∈ U.unspec := by
  refine ⟨(regulatedNames_nodup hu).sublist (List.Sublist.map _ List.filter_sublist), fun p hp => ?_⟩
  obtain ⟨r, hr, rfl⟩ := List.mem_map.mp hp
  simpa using (List.mem_filter.mp hr).2

theorem fillNodes_length : (fillNodes U).length ≤ U.unspec.length := by
  have := nodup_length_le (fillRegs_names hu).1 (fillRegs_names hu).2
  simpa [fillNodes] using this

theorem fillName_inj {p q : String} (hp : p ∈ U.unspec) (hq : q ∈ U.unspec) (e : fillName p = fillName q) :
    p = q :=
  inj_of_nodup_map hu.fillNodup p hp q hq e

theorem fill_names_nodup : ((fill U).T.nodes.map Node.name).Nodup := by
  rw [fill_nodes, List.map_append, List.map_map]
  have h₁ : (U.D.T.nodes.map (Node.name ∘ fillRoot U)).Nodup := by
    have : Node.name ∘ fillRoot U = Node.name := funext fun N => fillRoot_name U N
    rw [this]; exact hu.names_nodup
  have h₂ : ((fillNodes U).map Node.name).Nodup := by
    simp only [fillNodes, List.map_map]
    have : Node.name ∘ fillNode = fillName ∘ Regulated.name := rfl
    rw [this, ← List.map_map]
    exact nodup_map_of_inj (fillRegs_names hu).1 fun x hx y hy e =>
      fillName_inj hu ((fillRegs_names hu).2 x hx) ((fillRegs_names hu).2 y hy) e
  refine List.nodup_append.mpr ⟨h₁, h₂, fun a ha b hb e => ?_⟩
  subst e
  obtain ⟨N, hN, rfl⟩ := List.mem_map.mp ha
  obtain ⟨F, hF, he⟩ := List.mem_map.mp hb
  obtain ⟨r, _, hp, rfl⟩ := mem_fillNodes.mp hF
  exact hu.freshRule N hN (List.mem_map.mpr ⟨r.name, hp, by simpa using he⟩)

theorem fill_regOK {r : Regulated} (hr : r ∈ U.D.T.regulated) : RegOK (fill U) r := by
  obtain ⟨h1, h2, h3, h4⟩ := hu.ok.2.2.1 r hr
  exact ⟨by simpa using fillEnv_mono hu _ _ h1, h2, by simpa [fillEnv_sorts] using h3, h4⟩

theorem fill_defOK {d : Definition} (hd : d ∈ U.D.T.definitions) : DefOK (fill U) d := by
  obtain ⟨h1, h2, h3, h4, h5⟩ := hu.ok.2.2.2.2.1 d hd
  have hw := (VE.check_iff_wellFormed _ _ _).mp h5
  exact ⟨by simpa using fillEnv_mono hu _ _ h1, h2, by simpa [fillEnv_sorts] using h3,
    by simpa [typeDiagnostic_fill hu hw] using h4, by simpa using check_fill hu h5⟩

omit hu in
theorem atom_typed {E : VE.Environment} {p : String} {ss : List String}
    (hp : E.predicates p = some ss) (ha : ss.length = 1 ∨ ss.length = 2) :
    typeDiagnostic E ss.reverse (atom p ss) = .ok () ∧ VE.Formula.check E ss.reverse (atom p ss) = true := by
  rcases ha with ha | ha
  · match ss, ha with
    | [s], _ => simp [atom, typeDiagnostic, termSort, VE.Formula.check, VE.Term.sortOf, hp, pure, Except.pure,
        bind, Except.bind]
  · match ss, ha with
    | [s, t], _ => simp [atom, typeDiagnostic, termSort, VE.Formula.check, VE.Term.sortOf, hp, pure,
        Except.pure, bind, Except.bind]

theorem fill_nodeOK {N : Node} (hN : N ∈ (fill U).T.nodes) : NodeOK (fill U) N := by
  rcases mem_fill_nodes.mp hN with ⟨N₀, hN₀, rfl⟩ | hN
  · obtain ⟨h1, h2, r, hr, hφ⟩ := hu.ok.2.2.2.2.2.2.1.1 N₀ hN₀
    refine ⟨by simpa using h1, by simpa using h2, r, by simpa using hr, fun φ hφm => ?_⟩
    simp only [fillRoot_guard, fillRoot_carveOuts] at hφm
    obtain ⟨h3, h4⟩ := hφ φ hφm
    have hw := (VE.check_iff_wellFormed _ _ _).mp h4
    exact ⟨by simpa [typeDiagnostic_fill hu hw] using h3, by simpa using check_fill hu h4⟩
  · obtain ⟨r, hr, hp, rfl⟩ := mem_fillNodes.mp hN
    obtain ⟨_, ha, _, _⟩ := hu.ok.2.2.1 r hr
    have hf : (fill U).T.regulated.find? (fun x => x.name == r.name) = some r := by
      cases hf : U.D.T.regulated.find? (fun x => x.name == r.name) with
      | none => exact absurd hf (by rw [List.find?_eq_none]; intro h; exact h r hr (by simp))
      | some r' =>
        have := hu.regulated_eq (List.mem_of_find?_eq_some hf) hr (by simpa using List.find?_some hf)
        subst this; simpa using hf
    refine ⟨hu.ruleNames _ hp, by simp [fillNode], r, hf, fun φ hφ => ?_⟩
    simp only [fillNode, List.mem_singleton] at hφ
    subst hφ
    have hpr : (fill U).E.predicates (unsaidName r.name) = some r.sorts := by
      simp only [fill_E]; rw [fillEnv_unsaid U hp, sortsOf_reg hu hr]
    exact atom_typed hpr ha

omit hu in
theorem ruleNodes_fillRoot (N : Node) : ruleNodes (fillRoot U N) = ruleNodes N := by
  simp [ruleNodes]

theorem fill_ast : ((fill U).T.nodes.map ruleNodes).sum ≤ 10000 := by
  rw [fill_nodes, List.map_append, sum_append_nat, List.map_map]
  have h₁ : (U.D.T.nodes.map (ruleNodes ∘ fillRoot U)).sum = (U.D.T.nodes.map ruleNodes).sum := by
    congr 1; apply List.map_congr_left; intro N _; exact ruleNodes_fillRoot N
  have h₂ : ((fillNodes U).map ruleNodes).sum ≤ fillGuardNodes U := by
    let g : String → Nat := fun p => VE.Bridge.formulaNodes (atom (unsaidName p) (sortsOf U.D p))
    have heq : (fillNodes U).map ruleNodes =
        ((U.D.T.regulated.filter (fun r => r.name ∈ U.unspec)).map Regulated.name).map g := by
      simp only [fillNodes, List.map_map]
      apply List.map_congr_left
      intro r hr
      simp [ruleNodes, fillNode, g, sortsOf_reg hu (List.mem_filter.mp hr).1]
    rw [heq]
    exact sum_map_le (fillRegs_names hu).1 (fillRegs_names hu).2
  have := hu.ast
  omega

theorem fill_overOK : OverOK (fill U) := by
  have hex : ∀ N ∈ (fill U).T.nodes, ∀ m ∈ N.over, ∃ M ∈ (fill U).T.nodes, M.name = m ∧ M.pred = N.pred := by
    intro N hN m hm
    rcases mem_fill_nodes.mp hN with ⟨N₀, hN₀, rfl⟩ | hN
    · rcases fillRoot_over U N₀ with ⟨hp, _, ho⟩ | ⟨_, he⟩
      · rw [ho, List.mem_singleton] at hm
        subst hm
        obtain ⟨r, hr, hrn, _⟩ := hu.declared _ hp
        refine ⟨fillNode r, mem_fill_nodes.mpr (Or.inr (mem_fillNodes.mpr ⟨r, hr, hrn ▸ hp, rfl⟩)), ?_, ?_⟩
        · simp [fillNode, hrn]
        · simp [fillNode, hrn]
      · rw [he] at hm ⊢
        obtain ⟨M, hM, hMn, hMp⟩ := hu.over_node hN₀ hm
        exact ⟨fillRoot U M, mem_fill_nodes.mpr (Or.inl ⟨M, hM, rfl⟩), by simpa using hMn, by simpa using hMp⟩
    · obtain ⟨r, _, _, rfl⟩ := mem_fillNodes.mp hN
      simp [fillNode] at hm
  intro N hN m hm
  obtain ⟨M, hM, hMn, hMp⟩ := hex N hN m hm
  obtain ⟨M', hf, hM', hM'n⟩ := find_of_name hM hMn
  have := eq_of_name (fill_names_nodup hu) hM hM' (hMn.trans hM'n.symm)
  subst this
  exact ⟨M, hf, hMp⟩

end Check

/-! ## Orders, heights and the two checks -/

section Orders
variable {U : UDoc} (hu : UValid U)
include hu

theorem fill_heights : ∀ N ∈ (fill U).T.nodes, height (fill U).T (fill U).T.nodes.length N ≤ 16 := by
  have hlen : (fill U).T.nodes.length = U.D.T.nodes.length + (fillNodes U).length := by simp [fill_nodes]
  intro N hN
  rcases mem_fill_nodes.mp hN with ⟨N₀, hN₀, rfl⟩ | hNf
  · rw [height_fillRoot, height_fill_author hu _ N₀ hN₀]
    have hb := belowCount_lt hu.acyclic hN₀
    rw [height_stable hu.acyclic _ U.D.T.nodes.length N₀ hN₀ (by omega) (by omega)]
    exact hu.ok.2.2.2.2.2.2.2.2.2.1 N₀ hN₀
  · obtain ⟨r, hr, hp, rfl⟩ := mem_fillNodes.mp hNf
    obtain ⟨k, hk⟩ : ∃ k, (fill U).T.nodes.length = k + 1 :=
      ⟨(fill U).T.nodes.length - 1, by have := List.length_pos_of_mem hN; omega⟩
    rw [hk]
    simp only [height]
    have : ((children (fill U).T (fillNode r)).map (height (fill U).T k)).foldl max 0 ≤ 15 := by
      apply foldl_max_le _ 0 (Nat.zero_le _)
      intro x hx
      obtain ⟨C, hC, rfl⟩ := List.mem_map.mp hx
      obtain ⟨C₀, hC₀, rfl, hpred, _⟩ := (mem_children_fillNode hu hp).mp hC
      rw [height_fillRoot, height_fill_author hu _ C₀ hC₀]
      have hb := belowCount_lt hu.acyclic hC₀
      rw [height_stable hu.acyclic _ (fuel U.D.T) C₀ hC₀ (by omega) (by unfold fuel; omega)]
      exact hu.heightU C₀ hC₀ (hpred ▸ hp)
    omega

omit hu in
theorem rulesOn_fill (p : String) :
    rulesOn (fill U).T p = (rulesOn U.D.T p).map (fillRoot U) ++ (fillNodes U).filter (·.pred == p) := by
  have : ((fun x : Node => x.pred == p) ∘ fillRoot U) = (fun x => x.pred == p) := funext fun N => by simp
  simp only [rulesOn, fill_nodes, List.filter_append, List.filter_map, this]

omit hu in
theorem formulas_fill (r : Regulated) :
    (Sym.reg r).formulas (fill U).T = (Sym.reg r).formulas U.D.T ++
      ((fillNodes U).filter (·.pred == r.name)).flatMap (fun N => N.guard :: N.carveOuts) := by
  simp only [Sym.formulas, rulesOn_fill, List.flatMap_append, List.flatMap_map, fillRoot_guard,
    fillRoot_carveOuts]

omit hu in
theorem stratum_names : nodeNames (stratumNodes (fill U).T) = nodeNames (stratumNodes U.D.T) := by
  simp [nodeNames, stratumNodes]

/-- The stratum DAG's node names are declared predicates of `E`. -/
theorem stratum_declared {x : String} (hx : x ∈ nodeNames (stratumNodes U.D.T)) :
    ∃ ss, U.D.E.predicates x = some ss := by
  simp only [nodeNames, stratumNodes, List.map_append, List.map_map, List.mem_append, List.mem_map,
    Function.comp] at hx
  rcases hx with ⟨r, hr, rfl⟩ | ⟨d, hd, rfl⟩
  · exact ⟨_, (hu.ok.2.2.1 r hr).1⟩
  · exact ⟨_, (hu.ok.2.2.2.2.1 d hd).1⟩

theorem fill_mentions_filtered (r : Regulated) :
    List.filter (nodeNames (stratumNodes U.D.T)).contains
      ((((fillNodes U).filter (·.pred == r.name)).flatMap (fun N => N.guard :: N.carveOuts)).flatMap preds) =
      [] := by
  rw [List.filter_eq_nil_iff]
  intro x hx hc
  simp only [List.mem_flatMap, List.mem_filter] at hx
  obtain ⟨φ, ⟨F, ⟨hF, _⟩, hφ⟩, hxφ⟩ := hx
  obtain ⟨r', _, hp, rfl⟩ := mem_fillNodes.mp hF
  simp only [fillNode, List.not_mem_nil, or_false, List.mem_cons] at hφ
  subst hφ
  have hxu : x = unsaidName r'.name := by
    unfold atom at hxφ
    split at hxφ <;> simp_all [preds]
  obtain ⟨ss, hss⟩ := stratum_declared hu (by simpa using hc)
  rw [hxu, hu.freshPred _ hp] at hss
  cases hss

theorem fill_stratum_key : keyOf (stratumNodes (fill U).T) = keyOf (stratumNodes U.D.T) := by
  unfold keyOf deps
  rw [stratum_names]
  have hfm := fill_mentions_filtered hu
  generalize nodeNames (stratumNodes U.D.T) = NN at hfm ⊢
  simp only [stratumNodes, List.map_append, List.map_map]
  congr 1
  apply List.map_congr_left
  intro r _
  simp only [Function.comp, formulas_fill, List.flatMap_append, List.filter_append, hfm, List.append_nil]

theorem order_fill : VE.Norms.order (fill U).T = VE.Norms.order U.D.T := by
  unfold VE.Norms.order
  rw [dependencyOrder_congr (fill_stratum_key hu)]

theorem syms_fill : syms (fill U).T = syms U.D.T := by
  unfold syms
  rw [order_fill hu]
  rfl

theorem layerNames_fill : layerNames (fill U).T = layerNames U.D.T := by
  unfold layerNames
  rw [syms_fill hu]

theorem fill_checkOK : CheckOK (fill U) := by
  have hlen : (fill U).T.nodes.length = U.D.T.nodes.length + (fillNodes U).length := by simp [fill_nodes]
  have hfl := fillNodes_length hu
  have hc := hu.count
  refine ⟨by simpa using hu.ok.1, by simpa [regulatedNames] using hu.ok.2.1, fun r hr => fill_regOK hu hr,
    by simpa using hu.ok.2.2.2.1, fun d hd => fill_defOK hu hd, by omega,
    ⟨fun N hN => fill_nodeOK hu hN, fill_names_nodup hu, fill_ast hu⟩, fill_overOK hu,
    dependencyOrder_ok _ (by rw [nodeNames_precedence]; exact fill_names_nodup hu) (fill_acyclic hu),
    fill_heights hu, ?_⟩
  rw [dependencyOrder_congr (fill_stratum_key hu)]
  exact hu.ok.2.2.2.2.2.2.2.2.2.2

theorem layer_declared {n : String} (hn : n ∈ layerNames U.D.T) : ∃ ss, U.D.E.predicates n = some ss := by
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hn
  exact ⟨_, (hu.valid.decl q hq).1⟩

theorem envAt_fill_mono (k : Nat) (n : String) (ss : List String) (h : (envAt U.D k).predicates n = some ss) :
    (envAt (fill U) k).predicates n = some ss := by
  simp only [envAt, hide, layerNames_fill hu] at h ⊢
  split at h
  · cases h
  · rename_i hn
    simp only [hn, if_false, fill_E]
    rw [fillEnv_declared hu h, h]

theorem envAt_fill_unsaid (k : Nat) {p : String} (hp : p ∈ U.unspec) :
    (envAt (fill U) k).predicates (unsaidName p) = some (sortsOf U.D p) := by
  have hn : unsaidName p ∉ (layerNames U.D.T).drop k := fun h => by
    obtain ⟨ss, hss⟩ := layer_declared hu (List.mem_of_mem_drop h)
    rw [hu.freshPred p hp] at hss
    cases hss
  simp only [envAt, hide, layerNames_fill hu, hn, if_false, fill_E]
  exact fillEnv_unsaid U hp

theorem check_envAt_fill {k : Nat} {Γ : List String} {φ : VE.Formula}
    (h : VE.Formula.check (envAt U.D k) Γ φ = true) : VE.Formula.check (envAt (fill U) k) Γ φ = true := by
  rw [VE.check_iff_wellFormed] at h ⊢
  exact wf_mono (E := envAt U.D k) (E' := envAt (fill U) k) rfl rfl (envAt_fill_mono hu k) φ Γ h

theorem fill_semanticCheck : semanticCheck (fill U) = true := by
  have hs := ((wellFormed_iff U.D).mp hu.wf).2
  have hck := fill_checkOK hu
  unfold semanticCheck at hs ⊢
  rw [syms_fill hu, layerNames_fill hu]
  simp only [Bool.and_eq_true] at hs ⊢
  obtain ⟨⟨⟨⟨⟨⟨_, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩ := hs
  refine ⟨⟨⟨⟨⟨⟨?_, ?_⟩, h3⟩, ?_⟩, ?_⟩, h6⟩, h7⟩
  · obtain ⟨o, ho⟩ := hck.2.2.2.2.2.2.2.2.1
    rw [ho]; rfl
  · rw [dependencyOrder_congr (fill_stratum_key hu)]; exact h2
  · rw [List.all_eq_true] at h4 ⊢
    intro q hq
    have := h4 q hq
    simp only [Bool.and_eq_true, beq_iff_eq] at this ⊢
    refine ⟨⟨?_, this.1.2⟩, this.2⟩
    simp only [fill_E]
    rw [fillEnv_declared hu this.1.1, this.1.1]
  · rw [List.all_eq_true] at h5 ⊢
    intro k hk
    have := h5 k hk
    split at this
    · rename_i q hq
      simp only [List.all_eq_true] at this ⊢
      intro φ hφ
      cases q with
      | defn d => exact check_envAt_fill hu (this φ hφ)
      | reg r =>
        rw [formulas_fill, List.mem_append] at hφ
        rcases hφ with hφ | hφ
        · exact check_envAt_fill hu (this φ hφ)
        · simp only [List.mem_flatMap, List.mem_filter, beq_iff_eq] at hφ
          obtain ⟨F, ⟨hF, hFp⟩, hφF⟩ := hφ
          obtain ⟨r', hr', hp, rfl⟩ := mem_fillNodes.mp hF
          simp only [fillNode] at hFp
          have hrr : r' = r := hu.regulated_eq hr' (mem_syms_reg (List.mem_of_getElem? hq)) hFp
          subst hrr
          simp only [fillNode, List.not_mem_nil, or_false, List.mem_cons] at hφF
          subst hφF
          have hpr := envAt_fill_unsaid hu k hp
          rw [sortsOf_reg hu hr'] at hpr
          exact (atom_typed hpr (hu.ok.2.2.1 r' hr').2.1).2
    · cases this

end Orders

/-- `fill_wellFormed`: the author-side limits of `WellFormedU` suffice: `fill`
never produces a tree that W1's `validate` rejects (8). -/
theorem fill_wellFormed (U : UDoc) (h : WellFormedU U = true) : WellFormed (fill U) = true :=
  (wellFormed_iff (fill U)).mpr ⟨fill_checkOK (uvalid h), fill_semanticCheck (uvalid h)⟩

end VE.NormDefaults
