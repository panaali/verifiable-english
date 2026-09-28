import VE.Attribution.Semantics

/-! Supporting facts: the conjuncts of `WellFormedReports`, node membership,
keys and generated names, `keyOf`, the predicates of `E_reports` and the shape
of every top-level premise. -/
namespace VE.Reports
open VE.Route (fol)
open VE.Definitions (forget hide)
universe u

/-- The conjuncts of `WellFormedReports`, as propositions. -/
structure WF (D : ReportDoc) : Prop where
  gate : reportsGate D.profiles = .ok ()
  ids : (D.units.map (·.id)).Nodup
  stmt : ∀ u ∈ D.units, u.content.isStatement = true
  depth : ∀ u ∈ D.units, u.content.depth ≤ 16
  nodes : ∀ x ∈ allNodes D, nodeOk D x = true
  ctxIds : (D.contexts.map (·.id)).Nodup
  asIds : (D.assessments.map (·.id)).Nodup
  assess : ∀ a ∈ D.assessments, assessmentOk D a = true
  collision : ∀ a ∈ digestTable D, ∀ b ∈ digestTable D, a.1 = b.1 → a.2 = b.2
  fresh : ∀ n ∈ names D, (D.E.predicates n).isNone = true ∧ n.utf8ByteSize ≤ 64
  nodup : (names D).Nodup
  lits : ∀ l ∈ D.lits, (D.E.constants l == some VE.Route.Background.stringSort) = true
  «scoped» : ∀ s ∈ D.«scoped», scopedOk D s = true
  bridges : ∀ b ∈ D.bridges, bridgeOk D b = true
  w2quoted : ∀ x ∈ D.w2.units, (!x.kind.quoted || x.content.isNone) = true
  allIds : (D.units.map (·.id) ++ D.w2.units.map (·.id)).Nodup

theorem wf_of {D : ReportDoc} (h : WellFormedReports D = true) : WF D := by
  unfold WellFormedReports at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hg, hi⟩, hs⟩, hd⟩, hn⟩, hc⟩, ha⟩, has⟩, hcol⟩, hf⟩, hnd⟩, hl⟩, hsc⟩, hb⟩, hq⟩, hids⟩ := h
  refine ⟨?_, hi, hs, hd, hn, hc, ha, has, hcol, hf, hnd, hl, hsc, hb, hq, hids⟩
  cases hr : reportsGate D.profiles with
  | ok x => rfl
  | error e => rw [hr] at hg; simp [Except.toBool] at hg

/-! ## Nodes -/

theorem Content.nodes_trans {x y z : Content} (hy : y ∈ x.nodes) (hz : z ∈ y.nodes) : z ∈ x.nodes := by
  induction x with
  | formula _ | norm _ _ | definition _ _ _ =>
    simp only [Content.nodes, List.mem_singleton] at hy; subst hy; exact hz
  | report h act c b lit ih =>
    simp only [Content.nodes, List.mem_cons] at hy ⊢
    rcases hy with rfl | hy
    · simpa [Content.nodes] using hz
    · exact Or.inr (ih hy)
  | assessment j a b ih =>
    simp only [Content.nodes, List.mem_cons] at hy ⊢
    rcases hy with rfl | hy
    · simpa [Content.nodes] using hz
    · exact Or.inr (ih hy)
  | negated n ih =>
    simp only [Content.nodes, List.mem_cons] at hy ⊢
    rcases hy with rfl | hy
    · simpa [Content.nodes] using hz
    · exact Or.inr (ih hy)

theorem mem_allNodes {D : ReportDoc} {x : Content} : x ∈ allNodes D ↔ Occurs D x := by
  simp [allNodes, Occurs]

theorem top_mem_allNodes {D : ReportDoc} {u : Unit} (hu : u ∈ D.units) : u.content ∈ allNodes D :=
  mem_allNodes.mpr ⟨u, hu, Content.mem_nodes_self _⟩

theorem occurs_sub {D : ReportDoc} {x y : Content} (hx : Occurs D x) (hy : y ∈ x.nodes) : Occurs D y := by
  obtain ⟨u, hu, hxu⟩ := hx
  exact ⟨u, hu, Content.nodes_trans hxu hy⟩

theorem body_mem_report {h c : String} {act : Act} {b : Content} {lit : Option String} :
    b ∈ (Content.report h act c b lit).nodes := by
  simp [Content.nodes, Content.mem_nodes_self]

theorem body_mem_assessment {j : Judgment} {a : String} {b : Content} :
    b ∈ (Content.assessment j a b).nodes := by
  simp [Content.nodes, Content.mem_nodes_self]

theorem operand_mem_negated {n : Content} : n ∈ (Content.negated n).nodes := by
  simp [Content.nodes, Content.mem_nodes_self]

theorem nodeOk_of_occurs {D : ReportDoc} (hw : WF D) {x : Content} (hx : Occurs D x) : nodeOk D x = true :=
  hw.nodes x (mem_allNodes.mpr hx)

/-! ## Keys and names -/

theorem mem_keys {D : ReportDoc} {k : ReportKey} :
    k ∈ keys D ↔ ∃ x ∈ allNodes D, reportKeyOf D x = some k := by
  unfold keys
  rw [List.Perm.mem_iff (List.mergeSort_perm _ _), mem_dedup, List.mem_filterMap]

theorem mem_akeys {D : ReportDoc} {k : AssessKey} :
    k ∈ akeys D ↔ ∃ x ∈ allNodes D, assessKeyOf D x = some k := by
  unfold akeys
  rw [List.Perm.mem_iff (List.mergeSort_perm _ _), mem_dedup, List.mem_filterMap]

theorem report_key_mem {D : ReportDoc} {h act c b lit s} (ho : Occurs D (.report h act c b lit))
    (hs : holderSort D h = some s) : (⟨act, s, c, complementId D b lit⟩ : ReportKey) ∈ keys D :=
  mem_keys.mpr ⟨_, mem_allNodes.mpr ho, by simp [reportKeyOf, hs]⟩

theorem assess_key_mem {D : ReportDoc} {j a b} (ho : Occurs D (.assessment j a b)) :
    (⟨j, a, contentId D b⟩ : AssessKey) ∈ akeys D :=
  mem_akeys.mpr ⟨_, mem_allNodes.mpr ho, rfl⟩

theorem inj_of_nodup_map {α β : Type} (f : α → β) :
    ∀ l : List α, (l.map f).Nodup → ∀ a ∈ l, ∀ b ∈ l, f a = f b → a = b
  | [], _, a, ha, _, _, _ => nomatch ha
  | x :: xs, hn, a, ha, b, hb, he => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp ha with h1 | h1 <;> rcases List.mem_cons.mp hb with h2 | h2
    · rw [h1, h2]
    · subst h1; exact absurd (he ▸ List.mem_map_of_mem h2) hn.1
    · subst h2; exact absurd (he.symm ▸ List.mem_map_of_mem h1) hn.1
    · exact inj_of_nodup_map f xs hn.2 a h1 b h2 he

theorem reportName_mem {D : ReportDoc} {k : ReportKey} (hk : k ∈ keys D) : reportName D k ∈ names D :=
  List.mem_append_left _ (List.mem_map_of_mem hk)

theorem assessName_mem {D : ReportDoc} {k : AssessKey} (hk : k ∈ akeys D) : assessName D k ∈ names D :=
  List.mem_append_right _ (List.mem_map_of_mem hk)

theorem reportName_inj {D : ReportDoc} (hw : WF D) {k k' : ReportKey} (hk : k ∈ keys D) (hk' : k' ∈ keys D)
    (he : reportName D k = reportName D k') : k = k' :=
  inj_of_nodup_map _ _ (List.nodup_append.mp hw.nodup).1 k hk k' hk' he

theorem assessName_inj {D : ReportDoc} (hw : WF D) {k k' : AssessKey} (hk : k ∈ akeys D)
    (hk' : k' ∈ akeys D) (he : assessName D k = assessName D k') : k = k' :=
  inj_of_nodup_map _ _ (List.nodup_append.mp hw.nodup).2.1 k hk k' hk' he

theorem reportName_ne_assessName {D : ReportDoc} (hw : WF D) {k : ReportKey} {a : AssessKey}
    (hk : k ∈ keys D) (ha : a ∈ akeys D) : reportName D k ≠ assessName D a :=
  (List.nodup_append.mp hw.nodup).2.2 _ (List.mem_map_of_mem hk) _ (List.mem_map_of_mem ha)

theorem findEq {α β : Type} [DecidableEq β] {f : α → β} {b : β} {l : List α} {a : α}
    (h : l.find? (fun x => f x == b) = some a) : f a = b := by
  have := List.find?_some h
  simpa using this

theorem keyOf_eq_inl {D : ReportDoc} {r : String} {k : ReportKey} (h : keyOf D r = some (.inl k)) :
    k ∈ keys D ∧ reportName D k = r := by
  unfold keyOf at h
  split at h
  · rename_i k' hf
    cases h
    exact ⟨List.mem_of_find?_eq_some hf, findEq hf⟩
  · cases hf : (akeys D).find? (fun k => assessName D k == r) <;> simp [hf] at h

theorem keyOf_eq_inr {D : ReportDoc} {r : String} {k : AssessKey} (h : keyOf D r = some (.inr k)) :
    k ∈ akeys D ∧ assessName D k = r := by
  unfold keyOf at h
  split at h
  · cases h
  · cases hf : (akeys D).find? (fun k => assessName D k == r) with
    | none => simp [hf] at h
    | some k' =>
      simp only [hf, Option.map_some, Option.some.injEq, Sum.inr.injEq] at h
      subst h
      exact ⟨List.mem_of_find?_eq_some hf, findEq hf⟩

theorem keyOf_eq_none {D : ReportDoc} {r : String} : keyOf D r = none ↔ r ∉ names D := by
  unfold keyOf names
  constructor
  · intro h hr
    split at h
    · cases h
    · rename_i hf
      rcases List.mem_append.mp hr with hr | hr
      · obtain ⟨k, hk, rfl⟩ := List.mem_map.mp hr
        exact List.find?_eq_none.mp hf k hk (by simp)
      · obtain ⟨k, hk, rfl⟩ := List.mem_map.mp hr
        have := List.find?_eq_none.mp (Option.map_eq_none_iff.mp h) k hk
        simp at this
  · intro hr
    have h1 : (keys D).find? (fun k => reportName D k == r) = none :=
      List.find?_eq_none.mpr fun k hk he =>
        hr (List.mem_append_left _ (List.mem_map.mpr ⟨k, hk, beq_iff_eq.mp he⟩))
    have h2 : (akeys D).find? (fun k => assessName D k == r) = none :=
      List.find?_eq_none.mpr fun k hk he =>
        hr (List.mem_append_right _ (List.mem_map.mpr ⟨k, hk, beq_iff_eq.mp he⟩))
    simp [h1, h2]

theorem keyOf_reportName {D : ReportDoc} (hw : WF D) {k : ReportKey} (hk : k ∈ keys D) :
    keyOf D (reportName D k) = some (.inl k) := by
  unfold keyOf
  split
  · rename_i k' hf
    have hk' := List.mem_of_find?_eq_some hf
    have he := findEq hf
    rw [reportName_inj hw hk' hk he]
  · rename_i hf
    exact absurd (by simp) (List.find?_eq_none.mp hf k hk)

theorem keyOf_assessName {D : ReportDoc} (hw : WF D) {k : AssessKey} (hk : k ∈ akeys D) :
    keyOf D (assessName D k) = some (.inr k) := by
  unfold keyOf
  split
  · rename_i k' hf
    have hk' := List.mem_of_find?_eq_some hf
    have he := findEq hf
    exact absurd he (reportName_ne_assessName hw hk' hk)
  · cases hf : (akeys D).find? (fun k' => assessName D k' == assessName D k) with
    | none => exact absurd (by simp) (List.find?_eq_none.mp hf k hk)
    | some k' =>
      have hk' := List.mem_of_find?_eq_some hf
      have he := findEq hf
      simp [assessName_inj hw hk' hk he]

theorem fresh_pred {D : ReportDoc} (hw : WF D) {r : String} (hr : r ∈ names D) : D.E.predicates r = none := by
  simpa using (hw.fresh r hr).1

theorem not_mem_names_of_pred {D : ReportDoc} (hw : WF D) {r : String} {ss : List String}
    (h : D.E.predicates r = some ss) : r ∉ names D := fun hr => by
  rw [fresh_pred hw hr] at h; cases h

theorem envReports_pred_old {D : ReportDoc} {r : String} (hr : r ∉ names D) :
    (envReports D).predicates r = D.E.predicates r := by
  show (match keyOf D r with
    | some (.inl k) => some [k.sort] | some (.inr _) => some [D.evidence] | none => D.E.predicates r) = _
  rw [keyOf_eq_none.mpr hr]

theorem envReports_pred_report {D : ReportDoc} (hw : WF D) {k : ReportKey} (hk : k ∈ keys D) :
    (envReports D).predicates (reportName D k) = some [k.sort] := by
  show (match keyOf D (reportName D k) with
    | some (.inl k) => some [k.sort] | some (.inr _) => some [D.evidence] | none => _) = _
  rw [keyOf_reportName hw hk]

theorem envReports_pred_assess {D : ReportDoc} (hw : WF D) {k : AssessKey} (hk : k ∈ akeys D) :
    (envReports D).predicates (assessName D k) = some [D.evidence] := by
  show (match keyOf D (assessName D k) with
    | some (.inl k) => some [k.sort] | some (.inr _) => some [D.evidence] | none => _) = _
  rw [keyOf_assessName hw hk]

/-- Every relation symbol of E keeps its signature in E_reports. -/
theorem envReports_pred_of_old {D : ReportDoc} (hw : WF D) {r : String} {ss : List String}
    (h : D.E.predicates r = some ss) : (envReports D).predicates r = some ss := by
  rw [envReports_pred_old (not_mem_names_of_pred hw h), h]

/-- A generated predicate of E_reports is unary, on its key's sort. -/
theorem envReports_pred_names {D : ReportDoc} {r : String} {ss : List String}
    (h : (envReports D).predicates r = some ss) (hr : r ∈ names D) :
    ∃ s, ss = [s] := by
  have : (match keyOf D r with
    | some (.inl k) => some [k.sort] | some (.inr _) => some [D.evidence] | none => D.E.predicates r) =
      some ss := h
  cases hk : keyOf D r with
  | none => exact absurd hr (keyOf_eq_none.mp hk)
  | some x =>
    rw [hk] at this
    cases x <;> simp at this <;> exact ⟨_, this.symm⟩

/-! ## Holders, records, contexts -/

theorem holderSort_const {D : ReportDoc} {h s : String} (hs : holderSort D h = some s) :
    D.E.constants h = some s := by
  unfold holderSort at hs
  split at hs
  · rename_i s' he
    split at hs
    · cases hs; exact he
    · cases hs
  · cases hs

theorem recordOf_mem {D : ReportDoc} {a : String} {r : Assessment} (h : recordOf D a = some r) :
    r ∈ D.assessments ∧ r.id = a :=
  ⟨List.mem_of_find?_eq_some h, findEq h⟩

theorem recordOf_context {D : ReportDoc} (hw : WF D) {a : String} {r : Assessment}
    (h : recordOf D a = some r) : D.E.constants r.context = some D.evidence := by
  have := hw.assess r (recordOf_mem h).1
  simp only [assessmentOk, Bool.and_eq_true, beq_iff_eq] at this
  exact this.1.1

theorem contextOf_mem {D : ReportDoc} {c : String} {x : Context} (h : contextOf D c = some x) :
    x ∈ D.contexts ∧ x.id = c :=
  ⟨List.mem_of_find?_eq_some h, findEq h⟩

/-- Every constant of E denotes in an admissible structure. -/
theorem const_exists {D : ReportDoc} {S : VE.Structure.{u}} (hS : S.Admissible D.E) {h s : String}
    (hc : D.E.constants h = some s) : ∃ v, S.constant h = some v ∧ S.domain s v :=
  hS.1 h s hc

/-! ## Top-level statements and their premises -/

/-- The four shapes of a well-formed top-level unit, with its premise. -/
theorem unit_shape {D : ReportDoc} (hw : WF D) {u : Unit} (hu : u ∈ D.units) :
    (∃ h act c b lit s, u.content = .report h act c b lit ∧ holderSort D h = some s ∧
      unitPremise D u = some (.unary (reportName D ⟨act, s, c, complementId D b lit⟩) (.const h))) ∨
    (∃ j a b r, u.content = .assessment j a b ∧ recordOf D a = some r ∧
      unitPremise D u = some (.unary (assessName D ⟨j, a, contentId D b⟩) (.const r.context))) ∨
    (∃ h act c b lit s, u.content = .negated (.report h act c b lit) ∧ holderSort D h = some s ∧
      unitPremise D u = some (.not (.unary (reportName D ⟨act, s, c, complementId D b lit⟩) (.const h)))) ∨
    (∃ j a b r, u.content = .negated (.assessment j a b) ∧ recordOf D a = some r ∧
      unitPremise D u = some (.not (.unary (assessName D ⟨j, a, contentId D b⟩) (.const r.context)))) := by
  have hst := hw.stmt u hu
  have hok := hw.nodes _ (top_mem_allNodes hu)
  cases hc : u.content with
  | report h act c b lit =>
    rw [hc] at hok
    simp only [nodeOk, Bool.and_eq_true, Option.isSome_iff_exists] at hok
    obtain ⟨⟨s, hs⟩, _⟩ := hok
    exact Or.inl ⟨h, act, c, b, lit, s, rfl, hs, by simp [unitPremise, hc, «elab», hs]⟩
  | assessment j a b =>
    rw [hc] at hok
    simp only [nodeOk, Option.isSome_iff_exists] at hok
    obtain ⟨r, hr⟩ := hok
    exact Or.inr (Or.inl ⟨j, a, b, r, rfl, hr, by simp [unitPremise, hc, «elab», hr]⟩)
  | negated n =>
    have hn : nodeOk D n = true := hw.nodes n (mem_allNodes.mpr (occurs_sub
      (mem_allNodes.mp (top_mem_allNodes hu)) (by rw [hc]; exact operand_mem_negated)))
    rw [hc] at hst
    cases n with
    | report h act c b lit =>
      simp only [nodeOk, Bool.and_eq_true, Option.isSome_iff_exists] at hn
      obtain ⟨⟨s, hs⟩, _⟩ := hn
      exact Or.inr (Or.inr (Or.inl ⟨h, act, c, b, lit, s, rfl, hs, by simp [unitPremise, hc, «elab», hs]⟩))
    | assessment j a b =>
      simp only [nodeOk, Option.isSome_iff_exists] at hn
      obtain ⟨r, hr⟩ := hn
      exact Or.inr (Or.inr (Or.inr ⟨j, a, b, r, rfl, hr, by simp [unitPremise, hc, «elab», hr]⟩))
    | _ => simp [Content.isStatement, Content.isReport, Content.isAssessment] at hst
  | _ => rw [hc] at hst; simp [Content.isStatement] at hst

theorem mem_premises {D : ReportDoc} {φ : VE.Formula} :
    φ ∈ premises D ↔ ∃ u ∈ D.units, unitPremise D u = some φ := by
  simp [premises, List.mem_filterMap]

theorem unitPremise_mem {D : ReportDoc} {u : Unit} (hu : u ∈ D.units) {φ : VE.Formula}
    (h : unitPremise D u = some φ) : φ ∈ premises D :=
  mem_premises.mpr ⟨u, hu, h⟩

end VE.Reports
