import VE.Attribution.Facts

/-! Spec 9.2, first half: vocabulary facts, faithfulness of the elaboration
with the typed model correspondence in both directions, and finite witness
decoding, at every universe. -/
namespace VE.Reports
open VE.Route (fol)
open VE.Definitions (forget hide)
universe u

/-! ## Vocabulary (1.5) -/

theorem env_ext {E F : VE.Environment} (hs : E.sorts = F.sorts)
    (hp : ∀ r, E.predicates r = F.predicates r) (hc : E.constants = F.constants) : E = F := by
  cases E; cases F
  simp only at hs hp hc
  subst hs hc
  simp only [VE.Environment.mk.injEq, true_and, and_true]
  funext r; exact hp r

/-- 1.5: E ⊆ E_reports. -/
theorem envReports_extends (D : ReportDoc) (h : WellFormedReports D = true) :
    ∀ a : VE.Formula, a.WellFormed D.E [] → a.WellFormed (envReports D) [] := fun a ha =>
  VE.Definitions.wf_mono (E := D.E) (E' := envReports D) rfl rfl (fun _ _ hr => envReports_pred_of_old (wf_of h) hr) a [] ha

theorem names_fresh (D : ReportDoc) (h : WellFormedReports D = true) :
    (∀ n ∈ names D, D.E.predicates n = none ∧ n.utf8ByteSize ≤ 64) ∧ (names D).Nodup :=
  ⟨fun n hn => ⟨fresh_pred (wf_of h) hn, ((wf_of h).fresh n hn).2⟩, (wf_of h).nodup⟩

theorem names_injective_on_keys (D : ReportDoc) (h : WellFormedReports D = true) :
    (∀ k ∈ keys D, ∀ k' ∈ keys D, reportName D k = reportName D k' → k = k') ∧
    (∀ k ∈ akeys D, ∀ k' ∈ akeys D, assessName D k = assessName D k' → k = k') :=
  ⟨fun _ hk _ hk' he => reportName_inj (wf_of h) hk hk' he,
   fun _ hk _ hk' he => assessName_inj (wf_of h) hk hk' he⟩

theorem hide_envReports (D : ReportDoc) (h : WellFormedReports D = true) :
    hide (envReports D) (names D) = D.E := by
  refine env_ext rfl (fun r => ?_) rfl
  show (if r ∈ names D then none else (envReports D).predicates r) = D.E.predicates r
  split
  · rename_i hr; rw [fresh_pred (wf_of h) hr]
  · rename_i hr; exact envReports_pred_old hr

/-- Every premise is a well-formed signed generated atom. -/
theorem premises_signed (D : ReportDoc) (h : WellFormedReports D = true) :
    ∀ a ∈ premises D, SignedAtom D a := by
  have hw := wf_of h
  intro a ha
  obtain ⟨u, hu, hp⟩ := mem_premises.mp ha
  have htop := mem_allNodes.mp (top_mem_allNodes hu)
  rcases unit_shape hw hu with
    ⟨hd, act, c, b, lit, s, hc, hs, hp'⟩ | ⟨j, x, b, r, hc, hr, hp'⟩ |
    ⟨hd, act, c, b, lit, s, hc, hs, hp'⟩ | ⟨j, x, b, r, hc, hr, hp'⟩
  · rw [hp'] at hp; cases hp
    have hk := report_key_mem (hc ▸ htop) hs
    exact ⟨_, reportName_mem hk, hd, ⟨s, envReports_pred_report hw hk, holderSort_const hs⟩, Or.inl rfl⟩
  · rw [hp'] at hp; cases hp
    have hk := assess_key_mem (hc ▸ htop)
    exact ⟨_, assessName_mem hk, r.context,
      ⟨D.evidence, envReports_pred_assess hw hk, recordOf_context hw hr⟩, Or.inl rfl⟩
  · rw [hp'] at hp; cases hp
    have hk := report_key_mem (occurs_sub (hc ▸ htop) operand_mem_negated) hs
    exact ⟨_, reportName_mem hk, hd, ⟨s, envReports_pred_report hw hk, holderSort_const hs⟩, Or.inr rfl⟩
  · rw [hp'] at hp; cases hp
    have hk := assess_key_mem (occurs_sub (hc ▸ htop) operand_mem_negated)
    exact ⟨_, assessName_mem hk, r.context,
      ⟨D.evidence, envReports_pred_assess hw hk, recordOf_context hw hr⟩, Or.inr rfl⟩

theorem signedAtom_wellFormed {D : ReportDoc} {a : VE.Formula} (ha : SignedAtom D a) :
    a.WellFormed (envReports D) [] := by
  obtain ⟨r, _, h, hwf, rfl | rfl⟩ := ha
  · exact hwf
  · exact hwf

theorem premises_wellFormed (D : ReportDoc) (h : WellFormedReports D = true) :
    ∀ a ∈ premises D, a.WellFormed (envReports D) [] := fun a ha =>
  signedAtom_wellFormed (premises_signed D h a ha)

theorem length_filterMap_of_isSome {α β : Type} (f : α → Option β) :
    ∀ l : List α, (∀ x ∈ l, (f x).isSome = true) → (l.filterMap f).length = l.length
  | [], _ => rfl
  | x :: xs, h => by
    obtain ⟨y, hy⟩ := Option.isSome_iff_exists.mp (h x (List.mem_cons_self))
    rw [List.filterMap_cons, hy]
    simp [length_filterMap_of_isSome f xs (fun z hz => h z (List.mem_cons_of_mem _ hz))]

/-- `elab` is total on statements. -/
theorem premises_all (D : ReportDoc) (h : WellFormedReports D = true) :
    (premises D).length = D.units.length := by
  apply length_filterMap_of_isSome
  intro u hu
  rcases unit_shape (wf_of h) hu with ⟨_, _, _, _, _, _, _, _, hp⟩ | ⟨_, _, _, _, _, _, hp⟩ |
    ⟨_, _, _, _, _, _, _, _, hp⟩ | ⟨_, _, _, _, _, _, hp⟩ <;> simp [hp]

theorem length_filterMap_two {α β γ : Type} (f : α → Option β) (g : α → Option γ)
    (hfg : ∀ x, f x = none ∨ g x = none) :
    ∀ l : List α, (l.filterMap f).length + (l.filterMap g).length ≤ l.length
  | [] => by simp
  | x :: xs => by
    have ih := length_filterMap_two f g hfg xs
    rw [List.filterMap_cons, List.filterMap_cons]
    have := hfg x
    cases hf : f x <;> cases hg : g x <;> simp only [hf, hg, reduceCtorEq, or_self] at this <;>
      simp <;> omega

theorem keys_finite (D : ReportDoc) (h : WellFormedReports D = true) :
    (keys D).length + (akeys D).length ≤ contentCount D := by
  have h1 : (keys D).length ≤ ((allNodes D).filterMap (reportKeyOf D)).length := by
    unfold keys; rw [List.length_mergeSort]; exact length_dedup _
  have h2 : (akeys D).length ≤ ((allNodes D).filterMap (assessKeyOf D)).length := by
    unfold akeys; rw [List.length_mergeSort]; exact length_dedup _
  have h3 := length_filterMap_two (reportKeyOf D) (assessKeyOf D)
    (fun x => by cases x <;> simp [reportKeyOf, assessKeyOf]) (allNodes D)
  unfold contentCount; omega

/-- 4.1 step 4 and 11.1 allow depth 16. -/
theorem content_depth_bounded (D : ReportDoc) (h : WellFormedReports D = true) :
    ∀ u ∈ D.units, u.content.depth ≤ 16 :=
  (wf_of h).depth

theorem mem_digestTable_content {D : ReportDoc} {x : Content} (hx : Occurs D x) :
    (contentId D x, canonicalObject D x) ∈ digestTable D :=
  List.mem_flatMap.mpr ⟨x, mem_allNodes.mpr hx, List.mem_cons_self⟩

theorem mem_digestTable_complement {D : ReportDoc} {b : Content} {l : Option String}
    (hb : OccursComplement D b l) : (complementId D b l, complementObject D b l) ∈ digestTable D := by
  obtain ⟨hd, act, c, ho⟩ := hb
  exact List.mem_flatMap.mpr ⟨_, mem_allNodes.mpr ho, by simp⟩

/-- 3.4: among the objects a well-formed document digests, a digest names one
canonical object. -/
theorem no_collision (D : ReportDoc) (h : WellFormedReports D = true) (x y : Content)
    (hx : Occurs D x) (hy : Occurs D y) :
    contentId D x = contentId D y → canonicalObject D x = canonicalObject D y :=
  (wf_of h).collision _ (mem_digestTable_content hx) _ (mem_digestTable_content hy)

theorem no_collision_complement (D : ReportDoc) (h : WellFormedReports D = true) (b b' : Content)
    (l l' : Option String) (hb : OccursComplement D b l) (hb' : OccursComplement D b' l') :
    complementId D b l = complementId D b' l' → complementObject D b l = complementObject D b' l' :=
  (wf_of h).collision _ (mem_digestTable_complement hb) _ (mem_digestTable_complement hb')

/-! ## Faithfulness and model correspondence (4.3) -/

section Faithful
variable {D : ReportDoc}

theorem interp_rel (M : Source.{u} D) (r : String) (vs : List M.S.Carrier) :
    (interp D M).relation r vs =
      match keyOf D r, vs with
      | some (.inl k), [v] => M.J k.act k.sort k.ctx k.content v
      | some (.inr k), [v] => M.A k.j k.a k.content v
      | some _, _ => False
      | none, _ => M.S.relation r vs := rfl

theorem interp_rel_report (hw : WF D) (M : Source.{u} D) {k : ReportKey} (hk : k ∈ keys D)
    (v : M.S.Carrier) : (interp D M).relation (reportName D k) [v] ↔ M.J k.act k.sort k.ctx k.content v := by
  rw [interp_rel, keyOf_reportName hw hk]

theorem interp_rel_assess (hw : WF D) (M : Source.{u} D) {k : AssessKey} (hk : k ∈ akeys D)
    (v : M.S.Carrier) : (interp D M).relation (assessName D k) [v] ↔ M.A k.j k.a k.content v := by
  rw [interp_rel, keyOf_assessName hw hk]

theorem interp_rel_old (M : Source.{u} D) {r : String} (hr : r ∉ names D) (vs : List M.S.Carrier) :
    (interp D M).relation r vs ↔ M.S.relation r vs := by
  rw [interp_rel, keyOf_eq_none.mpr hr]

theorem interp_admissible (hw : WF D) (M : Source.{u} D) (hM : M.S.Admissible D.E) :
    (interp D M).Admissible (envReports D) := by
  refine ⟨fun c s hc => hM.1 c s hc, fun p vs hp => ?_⟩
  rw [interp_rel] at hp
  cases hk : keyOf D p with
  | none =>
    rw [hk] at hp
    obtain ⟨ss, hss, ht⟩ := hM.2 p vs hp
    exact ⟨ss, envReports_pred_of_old hw hss,
      (VE.Route.Examples.tupleTyped_relation M.S _ ss vs).mpr ht⟩
  | some x =>
    rw [hk] at hp
    cases x with
    | inl k =>
      obtain ⟨hkm, rfl⟩ := keyOf_eq_inl hk
      match vs, hp with
      | [v], hp => exact ⟨[k.sort], envReports_pred_report hw hkm, M.J_typed _ _ _ _ _ hp, trivial⟩
    | inr k =>
      obtain ⟨hkm, rfl⟩ := keyOf_eq_inr hk
      match vs, hp with
      | [v], hp => exact ⟨[D.evidence], envReports_pred_assess hw hkm, M.A_typed _ _ _ _ hp, trivial⟩

theorem denote_atom (S : VE.Structure.{u}) (p h : String) :
    (VE.Formula.unary p (.const h)).denote S [] ↔ ∃ v, S.constant h = some v ∧ S.relation p [v] := by
  simp [VE.Formula.denote, VE.Term.denote]

theorem sat_report_iff (M : Source.{u} D) (hM : M.S.Admissible D.E) {h s c : String} {act : Act}
    {b : Content} {lit : Option String} (hs : holderSort D h = some s) :
    Sat D M (.report h act c b lit) ↔ ∃ v, M.S.constant h = some v ∧ M.J act s c (complementId D b lit) v := by
  obtain ⟨v₀, hv₀, _⟩ := const_exists hM (holderSort_const hs)
  constructor
  · intro hsat; exact ⟨v₀, hv₀, hsat s hs v₀ hv₀⟩
  · rintro ⟨v, hv, hj⟩ s' hs' v' hv'
    rw [hs] at hs'; cases hs'
    rw [hv] at hv'; cases hv'
    exact hj

theorem sat_assess_iff (hw : WF D) (M : Source.{u} D) (hM : M.S.Admissible D.E) {j : Judgment}
    {a : String} {b : Content} {r : Assessment} (hr : recordOf D a = some r) :
    Sat D M (.assessment j a b) ↔ ∃ v, M.S.constant r.context = some v ∧ M.A j a (contentId D b) v := by
  obtain ⟨v₀, hv₀, _⟩ := const_exists hM (recordOf_context hw hr)
  constructor
  · intro hsat; exact ⟨v₀, hv₀, hsat r hr v₀ hv₀⟩
  · rintro ⟨v, hv, hj⟩ r' hr' v' hv'
    rw [hr] at hr'; cases hr'
    rw [hv] at hv'; cases hv'
    exact hj

/-- One top-level unit: its premise holds in the interpretation exactly when
its statement holds of the source model. -/
theorem unit_denote_iff (hw : WF D) (M : Source.{u} D) (hM : M.S.Admissible D.E) {u : Unit}
    (hu : u ∈ D.units) {φ : VE.Formula} (hφ : unitPremise D u = some φ) :
    φ.denote (interp D M) [] ↔ Sat D M u.content := by
  have htop := mem_allNodes.mp (top_mem_allNodes hu)
  rcases unit_shape hw hu with
    ⟨hd, act, c, b, lit, s, hc, hs, hp⟩ | ⟨j, x, b, r, hc, hr, hp⟩ |
    ⟨hd, act, c, b, lit, s, hc, hs, hp⟩ | ⟨j, x, b, r, hc, hr, hp⟩ <;>
    rw [hp] at hφ <;> cases hφ <;> rw [hc]
  · have hk := report_key_mem (hc ▸ htop) hs
    rw [denote_atom, sat_report_iff M hM hs]
    exact exists_congr fun v => and_congr_right fun _ => interp_rel_report hw M hk v
  · have hk := assess_key_mem (hc ▸ htop)
    rw [denote_atom, sat_assess_iff hw M hM hr]
    exact exists_congr fun v => and_congr_right fun _ => interp_rel_assess hw M hk v
  · have hk := report_key_mem (occurs_sub (hc ▸ htop) operand_mem_negated) hs
    show ¬ _ ↔ ¬ _
    rw [denote_atom, sat_report_iff M hM hs]
    exact not_congr (exists_congr fun v => and_congr_right fun _ => interp_rel_report hw M hk v)
  · have hk := assess_key_mem (occurs_sub (hc ▸ htop) operand_mem_negated)
    show ¬ _ ↔ ¬ _
    rw [denote_atom, sat_assess_iff hw M hM hr]
    exact not_congr (exists_congr fun v => and_congr_right fun _ => interp_rel_assess hw M hk v)

theorem unit_premise_some (hw : WF D) {u : Unit} (hu : u ∈ D.units) : ∃ φ, unitPremise D u = some φ := by
  rcases unit_shape hw hu with ⟨_, _, _, _, _, _, _, _, hp⟩ | ⟨_, _, _, _, _, _, hp⟩ |
    ⟨_, _, _, _, _, _, _, _, hp⟩ | ⟨_, _, _, _, _, _, hp⟩ <;> exact ⟨_, hp⟩

/-- Premises hold in a structure exactly when each unit's premise does. -/
theorem sat_premises_iff (hw : WF D) (S : VE.Structure.{u}) :
    fol.Sat S (premises D) ↔ ∀ u ∈ D.units, ∀ φ, unitPremise D u = some φ → φ.denote S [] := by
  constructor
  · intro h u hu φ hφ; exact h φ (unitPremise_mem hu hφ)
  · intro h φ hφ
    obtain ⟨u, hu, hp⟩ := mem_premises.mp hφ
    exact h u hu φ hp

end Faithful

/-- reports_elaboration_faithful, the source-model direction: the elaborated
premises hold in the interpretation of a source model exactly when the
document's intended meaning holds of it. -/
theorem reports_elaboration_faithful (D : ReportDoc) (h : WellFormedReports D = true) (M : Source.{u} D)
    (hM : M.S.Admissible D.E) :
    (interp D M).Admissible (envReports D) ∧
    (fol.Sat (interp D M) (premises D) ↔ IntendedReports D M) := by
  have hw := wf_of h
  refine ⟨interp_admissible hw M hM, ?_⟩
  rw [sat_premises_iff hw]
  constructor
  · intro hs u hu
    obtain ⟨φ, hφ⟩ := unit_premise_some hw hu
    exact (unit_denote_iff hw M hM hu hφ).mp (hs u hu φ hφ)
  · intro hi u hu φ hφ
    exact (unit_denote_iff hw M hM hu hφ).mpr (hi u hu)

theorem restrictJ_admissible (D : ReportDoc) (h : WellFormedReports D = true) (S' : VE.Structure.{u})
    (hS : S'.Admissible (envReports D)) : (restrictJ D S').S.Admissible D.E := by
  refine ⟨fun c s hc => hS.1 c s hc, fun r vs hr => ?_⟩
  obtain ⟨hn, hr⟩ := hr
  obtain ⟨ss, hss, ht⟩ := hS.2 r vs hr
  exact ⟨ss, by rw [← envReports_pred_old hn]; exact hss,
    (VE.Route.Examples.tupleTyped_relation S' _ ss vs).mpr ht⟩

/-- In an admissible E_reports structure a generated atom holds only of an
element of its key's sort. -/
theorem gen_rel_domain {D : ReportDoc} (hw : WF D) {S' : VE.Structure.{u}} (hS : S'.Admissible (envReports D))
    {k : ReportKey} (hk : k ∈ keys D) {v : S'.Carrier} (hv : S'.relation (reportName D k) [v]) :
    S'.domain k.sort v := by
  obtain ⟨ss, hss, ht⟩ := hS.2 _ _ hv
  rw [envReports_pred_report hw hk] at hss; cases hss
  exact ht.1

theorem gen_rel_domain_assess {D : ReportDoc} (hw : WF D) {S' : VE.Structure.{u}}
    (hS : S'.Admissible (envReports D)) {k : AssessKey} (hk : k ∈ akeys D) {v : S'.Carrier}
    (hv : S'.relation (assessName D k) [v]) : S'.domain D.evidence v := by
  obtain ⟨ss, hss, ht⟩ := hS.2 _ _ hv
  rw [envReports_pred_assess hw hk] at hss; cases hss
  exact ht.1

/-- The structure direction: on every admissible E_reports structure. -/
theorem reports_elaboration_faithful_out (D : ReportDoc) (h : WellFormedReports D = true)
    (S' : VE.Structure.{u}) (hS : S'.Admissible (envReports D)) :
    fol.Sat S' (premises D) ↔ IntendedReports D (restrictJ D S') := by
  have hw := wf_of h
  have hM := restrictJ_admissible D h S' hS
  rw [sat_premises_iff hw]
  have key : ∀ u ∈ D.units, ∀ φ, unitPremise D u = some φ →
      (φ.denote S' [] ↔ Sat D (restrictJ D S') u.content) := by
    intro u hu φ hφ
    have htop := mem_allNodes.mp (top_mem_allNodes hu)
    rcases unit_shape hw hu with
      ⟨hd, act, c, b, lit, s, hc, hs, hp⟩ | ⟨j, x, b, r, hc, hr, hp⟩ |
      ⟨hd, act, c, b, lit, s, hc, hs, hp⟩ | ⟨j, x, b, r, hc, hr, hp⟩ <;>
      rw [hp] at hφ <;> cases hφ <;> rw [hc]
    · have hk := report_key_mem (hc ▸ htop) hs
      rw [denote_atom, sat_report_iff _ hM hs]
      exact exists_congr fun v => and_congr_right fun _ =>
        ⟨fun hr => ⟨hk, gen_rel_domain hw hS hk hr, hr⟩, fun hr => hr.2.2⟩
    · have hk := assess_key_mem (hc ▸ htop)
      rw [denote_atom, sat_assess_iff hw _ hM hr]
      exact exists_congr fun v => and_congr_right fun _ =>
        ⟨fun h' => ⟨hk, gen_rel_domain_assess hw hS hk h', h'⟩, fun h' => h'.2.2⟩
    · have hk := report_key_mem (occurs_sub (hc ▸ htop) operand_mem_negated) hs
      show ¬ _ ↔ ¬ _
      rw [denote_atom, sat_report_iff _ hM hs]
      exact not_congr (exists_congr fun v => and_congr_right fun _ =>
        ⟨fun hr => ⟨hk, gen_rel_domain hw hS hk hr, hr⟩, fun hr => hr.2.2⟩)
    · have hk := assess_key_mem (occurs_sub (hc ▸ htop) operand_mem_negated)
      show ¬ _ ↔ ¬ _
      rw [denote_atom, sat_assess_iff hw _ hM hr]
      exact not_congr (exists_congr fun v => and_congr_right fun _ =>
        ⟨fun h' => ⟨hk, gen_rel_domain_assess hw hS hk h', h'⟩, fun h' => h'.2.2⟩)
  constructor
  · intro hs u hu
    obtain ⟨φ, hφ⟩ := unit_premise_some hw hu
    exact (key u hu φ hφ).mp (hs u hu φ hφ)
  · intro hi u hu φ hφ
    exact (key u hu φ hφ).mpr (hi u hu)

theorem struct_eq_of_rel {S : VE.Structure.{u}} (R : String → List S.Carrier → Prop)
    (h : ∀ r vs, R r vs ↔ S.relation r vs) : { S with relation := R } = S := by
  cases S
  simp only [VE.Structure.mk.injEq, heq_eq_eq, true_and]
  funext r vs
  exact propext (h r vs)

theorem forget_interp (D : ReportDoc) (h : WellFormedReports D = true) (M : Source.{u} D)
    (hM : M.S.Admissible D.E) : forget (names D) (interp D M) = M.S := by
  have hw := wf_of h
  show { M.S with relation := fun r vs => r ∉ names D ∧ (interp D M).relation r vs } = M.S
  apply struct_eq_of_rel
  intro r vs
  by_cases hr : r ∈ names D
  · simp only [hr, not_true_eq_false, false_and, false_iff]
    intro hrel
    obtain ⟨ss, hss, _⟩ := hM.2 r vs hrel
    rw [fresh_pred hw hr] at hss; cases hss
  · simp only [hr, not_false_eq_true, true_and]
    exact interp_rel_old M hr vs

/-- Typed model correspondence in both directions. -/
theorem restrict_interp (D : ReportDoc) (h : WellFormedReports D = true) (M : Source.{u} D)
    (hM : M.S.Admissible D.E) : AgreeOn D (restrictJ D (interp D M)) M := by
  have hw := wf_of h
  refine ⟨forget_interp D h M hM, fun k hk v => ?_, fun k hk v => ?_⟩
  · show (_ ∧ _ ∧ _) ↔ M.J k.act k.sort k.ctx k.content v
    constructor
    · rintro ⟨_, _, hr⟩; exact (interp_rel_report hw M hk v).mp hr
    · intro hj; exact ⟨hk, M.J_typed _ _ _ _ _ hj, (interp_rel_report hw M hk v).mpr hj⟩
  · show (_ ∧ _ ∧ _) ↔ M.A k.j k.a k.content v
    constructor
    · rintro ⟨_, _, hr⟩; exact (interp_rel_assess hw M hk v).mp hr
    · intro hj; exact ⟨hk, M.A_typed _ _ _ _ hj, (interp_rel_assess hw M hk v).mpr hj⟩

theorem interp_restrict (D : ReportDoc) (h : WellFormedReports D = true) (S' : VE.Structure.{u})
    (hS : S'.Admissible (envReports D)) :
    ∀ r vs, (interp D (restrictJ D S')).relation r vs ↔ S'.relation r vs := by
  have hw := wf_of h
  intro r vs
  rw [interp_rel]
  cases hk : keyOf D r with
  | none =>
    show (r ∉ names D ∧ S'.relation r vs) ↔ _
    exact ⟨fun h' => h'.2, fun h' => ⟨keyOf_eq_none.mp hk, h'⟩⟩
  | some x =>
    cases x with
    | inl k =>
      obtain ⟨hkm, rfl⟩ := keyOf_eq_inl hk
      match vs with
      | [v] =>
        show (_ ∧ _ ∧ _) ↔ _
        exact ⟨fun h' => h'.2.2, fun h' => ⟨hkm, gen_rel_domain hw hS hkm h', h'⟩⟩
      | [] =>
        simp only [false_iff]
        intro hr; obtain ⟨ss, hss, ht⟩ := hS.2 _ _ hr
        rw [envReports_pred_report hw hkm] at hss; cases hss; exact ht
      | _ :: _ :: _ =>
        simp only [false_iff]
        intro hr; obtain ⟨ss, hss, ht⟩ := hS.2 _ _ hr
        rw [envReports_pred_report hw hkm] at hss; cases hss; exact ht.2
    | inr k =>
      obtain ⟨hkm, rfl⟩ := keyOf_eq_inr hk
      match vs with
      | [v] =>
        show (_ ∧ _ ∧ _) ↔ _
        exact ⟨fun h' => h'.2.2, fun h' => ⟨hkm, gen_rel_domain_assess hw hS hkm h', h'⟩⟩
      | [] =>
        simp only [false_iff]
        intro hr; obtain ⟨ss, hss, ht⟩ := hS.2 _ _ hr
        rw [envReports_pred_assess hw hkm] at hss; cases hss; exact ht
      | _ :: _ :: _ =>
        simp only [false_iff]
        intro hr; obtain ⟨ss, hss, ht⟩ := hS.2 _ _ hr
        rw [envReports_pred_assess hw hkm] at hss; cases hss; exact ht.2

/-- `interp ∘ restrictJ` is the identity on an admissible E_reports structure. -/
theorem interp_restrict_eq (D : ReportDoc) (h : WellFormedReports D = true) (S' : VE.Structure.{u})
    (hS : S'.Admissible (envReports D)) : interp D (restrictJ D S') = S' := by
  show { S' with relation := (interp D (restrictJ D S')).relation } = S'
  exact struct_eq_of_rel _ (interp_restrict D h S' hS)

theorem old_formula_invariant (D : ReportDoc) (h : WellFormedReports D = true) (M : Source.{u} D)
    (a : VE.Formula) (ha : a.WellFormed D.E []) : a.denote (interp D M) [] ↔ a.denote M.S [] :=
  VE.Definitions.denote_congr D.E M.S _
    (fun r _ vs hr => interp_rel_old M (not_mem_names_of_pred (wf_of h) hr) vs) a [] [] ha

/-- Finite witness decoding, at every universe: a valid finite model over
E_reports is the interpretation of a source model. The spec's relation-wise
conclusion compares relations over two carriers that are not definitionally
equal for an existential `M`; it is stated here as equality of the two
structures, which gives it by transport (lean/REPORTS.md, deviations). -/
theorem finite_witness_decodes {α : Type u} [DecidableEq α] (D : ReportDoc) (h : WellFormedReports D = true)
    (Mo : VE.FiniteModel α) (valid : Mo.Valid (envReports D)) :
    ∃ M : Source.{u} D, M.S.Admissible D.E ∧ interp D M = Mo.asStructure :=
  ⟨restrictJ D Mo.asStructure, restrictJ_admissible D h _ valid, interp_restrict_eq D h _ valid⟩

end VE.Reports
