import VE.Readings.Asserted

/-! Formula-only documents: superposition is W2's shortcut (docs/spec/composition-s2.md 4.7, 8.4
`superpose_assertions`).

When every candidate is an assertion and there is no coupling or narrowing, `sup D` holds the fixed assertions and
`χ_{s,i} → φ_{s,i}` for every candidate, and `Choice_D` is the `:one` premises alone. A structure satisfies the
fixed assertions and one candidate of every set exactly when the choice vocabulary can be set so that it satisfies
those: forward, the bits spell one admitted index per set, whose gated assertion then holds; backward, the bits are
set to spell a candidate that holds. Every formula involved is typed over the shared vocabulary, which declares no
symbol of the choice vocabulary, so setting it changes no formula's truth. -/
namespace VE.Readings
open VE.Norms (Sat envAt size)
open VE.SoftNorms (soften envPrime decisions decisionNames)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content Labelled)
universe u

/-! ## The shared vocabulary has no choice symbol -/

theorem genDecls_head (Z : RightsDoc) {d : String × List String} (hd : d ∈ VE.Rights.genDecls Z) :
    d.1.data.head? = some 'r' := by
  simp only [VE.Rights.genDecls, VE.Rights.limDecls, VE.Rights.condDecls, VE.Rights.aimedDecls, List.mem_append,
    List.mem_map] at hd
  rcases hd with (⟨k, _, rfl⟩ | ⟨k, _, rfl⟩) | hd
  · simp [VE.Rights.limName, String.data_append]; rfl
  · simp [VE.Rights.condName, String.data_append]; rfl
  · split at hd
    · cases hd
    · obtain ⟨m, _, rfl⟩ := List.mem_map.mp hd
      simp [VE.Rights.aimedName, String.data_append]; rfl

/-- A name the document's environment does not declare, beginning `v`, is declared at no level of its
    elaboration. -/
theorem envAt_correlate_none (Z : RightsDoc) (k : Nat) {p : String} (hp : Z.soft.E.predicates p = none)
    (hv : p.data.head? = some 'v') : (envAt (soften (correlate Z)) k).predicates p = none := by
  simp only [envAt, VE.Norms.hide]
  split
  · rfl
  · show (envPrime (correlate Z)).predicates p = none
    unfold envPrime
    simp only
    rw [List.find?_eq_none.mpr (fun x hx he => by
      have := decision_head (X := correlate Z) (List.mem_map.mpr ⟨x, hx, rfl⟩)
      rw [show x.1 = p by simpa using he, hv] at this
      cases this)]
    show (VE.Rights.envR Z).predicates p = none
    unfold VE.Rights.envR
    simp only
    rw [List.find?_eq_none.mpr (fun x hx he => by
      have := genDecls_head Z hx
      rw [show x.1 = p by simpa using he, hv] at this
      cases this)]
    exact hp

theorem free_E (D : Doc) : (free D).1.soft.E = D.frame.soft.E := (build_shape D _ _).E

theorem sharedEnv_sorts (D : Doc) : (sharedEnv D).sorts = D.frame.soft.E.sorts := by
  show (correlate (free D).1).E.sorts = _
  show (VE.Rights.envR (free D).1).sorts = _
  show (free D).1.soft.E.sorts = _
  rw [free_E]

theorem sharedEnv_constants (D : Doc) : (sharedEnv D).constants = D.frame.soft.E.constants := by
  show (VE.Rights.envR (free D).1).constants = _
  show (free D).1.soft.E.constants = _
  rw [free_E]

theorem reading_reserved : reservedSym "ve__reading" = true := by
  have : ("ve__reading" : String) = "ve__" ++ "reading" := by decide
  unfold reservedSym; rw [this]; exact startsWith_append_ascii _ _ (by decide)

theorem frame_sorts_free {D : Doc} (h : WellFormedDoc D = true) : "ve__reading" ∉ D.frame.soft.E.sorts := by
  intro hm
  have hr := (wellFormedDoc_parts h).1
  simp only [reservedFree, Bool.and_eq_true, Bool.not_eq_true', List.any_eq_false] at hr
  exact absurd reading_reserved (by
    have := hr.1.1 "ve__reading" (by simp [hm])
    simpa using this)

/-- A formula over a vocabulary without the choice symbols has one truth in a structure and in a choice
    extension of it. -/
theorem choiceExt_denote {D : Doc} {E : VE.Environment} (hs : "ve__reading" ∉ E.sorts)
    (hk : E.constants "ve__here" = none) (hp : ∀ p ∈ (bitDecls D).map (·.1), E.predicates p = none)
    {S : VE.Structure.{u}} (R : String → List S.Carrier → Prop) (dom : String → S.Carrier → Prop)
    (k : String → Option S.Carrier) (hR : ∀ p, p ∉ (bitDecls D).map (·.1) → ∀ vs, R p vs ↔ S.relation p vs)
    (hd : ∀ σ, σ ≠ "ve__reading" → dom σ = S.domain σ) (hc : ∀ x, x ≠ "ve__here" → k x = S.constant x) :
    ∀ (φ : VE.Formula) (Γ : List String) (ρ : VE.Valuation S), φ.WellFormed E Γ →
      (φ.denote { S with relation := R, domain := dom, constant := k } ρ ↔ φ.denote S ρ) := by
  have hterm : ∀ (t : VE.Term) (Γ : List String) (s : String) (ρ : VE.Valuation S), t.sortOf E Γ = some s →
      t.denote { S with relation := R, domain := dom, constant := k } ρ = t.denote S ρ := by
    intro t Γ s ρ ht
    cases t with
    | var i => rfl
    | const c =>
      show k c = S.constant c
      apply hc
      rintro rfl
      simp [VE.Term.sortOf, hk] at ht
  have hrel : ∀ p ss, E.predicates p = some ss → ∀ vs, R p vs ↔ S.relation p vs := by
    intro p ss hps vs
    apply hR p (fun hm => by rw [hp p hm] at hps; cases hps)
  intro φ
  induction φ with
  | top | bottom => intros; exact Iff.rfl
  | unary p t =>
    intro Γ ρ ⟨s, hps, ht⟩
    simp only [VE.Formula.denote, hterm t Γ s ρ ht]
    exact exists_congr fun v => and_congr_right fun _ => hrel p _ hps [v]
  | binary p t w =>
    intro Γ ρ ⟨s, r, hps, ht, hw⟩
    simp only [VE.Formula.denote, hterm t Γ s ρ ht, hterm w Γ r ρ hw]
    exact exists_congr fun v => exists_congr fun v' => and_congr_right fun _ => and_congr_right fun _ =>
      hrel p _ hps [v, v']
  | eq t w =>
    intro Γ ρ ⟨s, ht, hw⟩
    simp only [VE.Formula.denote, hterm t Γ s ρ ht, hterm w Γ s ρ hw]
  | not a ih => intro Γ ρ hw; exact not_congr (ih Γ ρ hw)
  | and a b ia ib => intro Γ ρ hw; exact and_congr (ia Γ ρ hw.1) (ib Γ ρ hw.2)
  | or a b ia ib => intro Γ ρ hw; exact or_congr (ia Γ ρ hw.1) (ib Γ ρ hw.2)
  | implies a b ia ib => intro Γ ρ hw; exact imp_congr (ia Γ ρ hw.1) (ib Γ ρ hw.2)
  | all s a ih =>
    intro Γ ρ ⟨hsE, hw⟩
    have hds : dom s = S.domain s := hd s (fun e => hs (e ▸ hsE))
    show (∀ v, dom s v → _) ↔ (∀ v, S.domain s v → _)
    rw [hds]
    exact forall_congr' fun v => imp_congr_right fun _ => ih (s :: Γ) (v :: ρ) hw
  | ex s a ih =>
    intro Γ ρ ⟨hsE, hw⟩
    have hds : dom s = S.domain s := hd s (fun e => hs (e ▸ hsE))
    show (∃ v, dom s v ∧ _) ↔ (∃ v, S.domain s v ∧ _)
    rw [hds]
    exact exists_congr fun v => and_congr_right fun _ => ih (s :: Γ) (v :: ρ) hw

theorem sharedEnv_noChoice {D : Doc} (h : WellFormedDoc D = true) (hr : supReady D = true) :
    "ve__reading" ∉ (sharedEnv D).sorts ∧ (sharedEnv D).constants "ve__here" = none ∧
      ∀ p ∈ (bitDecls D).map (·.1), (sharedEnv D).predicates p = none := by
  have hf : choiceFresh D = true := by
    simp only [supReady, Bool.and_eq_true] at hr; exact hr.1.2
  simp only [choiceFresh, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hf
  refine ⟨by rw [sharedEnv_sorts]; exact frame_sorts_free h, by rw [sharedEnv_constants]; exact hf.1, ?_⟩
  intro p hp
  obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hp
  have hdn : ∃ m j, d.1 = bitName m j := by
    simp only [bitDecls, List.mem_flatMap, List.mem_map] at hd
    obtain ⟨m, _, j, _, rfl⟩ := hd
    exact ⟨m + 1, j, rfl⟩
  obtain ⟨m, j, hmj⟩ := hdn
  apply envAt_correlate_none
  · rw [free_E]; exact hf.2 d hd
  · rw [hmj]; exact bitName_head m j

/-! ## The assertions of `sup D` -/

def supItemAsserted (D : Doc) (m : Nat) : Item → List VE.Formula
  | .fixed _ c _ => asserted c
  | .bar _ _ => []
  | .set R => (List.range R.candidates.length).flatMap (fun i =>
      match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
      | some (c, _) => asserted (gateContent D m i c)
      | none => [])

def supAssertedAux (D : Doc) : List Item → Nat → List VE.Formula
  | [], _ => []
  | it :: l, m => supItemAsserted D m it ++ supAssertedAux D l (if isSet it then m + 1 else m)

theorem sup_inner_snd (D : Doc) (m : Nat) (R : ReadingSet) :
    ∀ (is : List Nat) (acc : RightsDoc × List VE.Formula),
      (is.foldl (fun acc' i =>
        match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
        | some (c, cs) => let g := gateContent D m i c
                          (place acc'.1 g cs, acc'.2 ++ asserted g)
        | none => acc') acc).2 = acc.2 ++ is.flatMap (fun i =>
          match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
          | some (c, _) => asserted (gateContent D m i c)
          | none => [])
  | [], acc => by simp
  | i :: is, acc => by
    rw [List.foldl_cons, sup_inner_snd D m R is, List.flatMap_cons, ← List.append_assoc]
    congr 1
    split <;> rename_i heq <;> simp [heq]

theorem sup_snd_fold (D : Doc) : ∀ (l : List Item) (acc : (RightsDoc × List VE.Formula) × Nat),
    (l.foldl (supStep D) acc).1.2 = acc.1.2 ++ supAssertedAux D l acc.2
  | [], acc => by simp [supAssertedAux]
  | it :: l, acc => by
    rw [List.foldl_cons, sup_snd_fold D l, supAssertedAux, ← List.append_assoc]
    congr 1
    · cases it with
      | fixed u c cs => simp [supStep, supItemAsserted]
      | bar u b => simp [supStep, supItemAsserted]
      | set R => simp only [supStep, supItemAsserted]; exact sup_inner_snd D acc.2 R _ _
    · cases it <;> rfl

theorem mem_supAssertedAux (D : Doc) : ∀ (l : List Item) (m0 : Nat) (a : VE.Formula),
    a ∈ supAssertedAux D l m0 ↔ (∃ u c cs, Item.fixed u c cs ∈ l ∧ a ∈ asserted c) ∨
      (∃ t R i x c, (l.filterMap setOf)[t]? = some R ∧ R.candidates[i]? = some x ∧ x.content = some c ∧
        a ∈ asserted (gateContent D (m0 + t) i c))
  | [], _, _ => by simp [supAssertedAux]
  | it :: l, m0, a => by
    simp only [supAssertedAux, List.mem_append]
    rw [mem_supAssertedAux D l]
    cases it with
    | fixed u c cs =>
      simp only [supItemAsserted, isSet, Bool.false_eq_true, if_false, List.mem_cons, List.filterMap_cons, setOf]
      constructor
      · rintro (h | ⟨u', c', cs', hm, h⟩ | h)
        · exact Or.inl ⟨u, c, cs, Or.inl rfl, h⟩
        · exact Or.inl ⟨u', c', cs', Or.inr hm, h⟩
        · exact Or.inr h
      · rintro (⟨u', c', cs', (he | hm), h⟩ | h)
        · cases he; exact Or.inl h
        · exact Or.inr (Or.inl ⟨u', c', cs', hm, h⟩)
        · exact Or.inr (Or.inr h)
    | bar u b =>
      simp only [supItemAsserted, List.not_mem_nil, false_or, isSet, Bool.false_eq_true, if_false, List.mem_cons,
        List.filterMap_cons, setOf, reduceCtorEq]
    | set R =>
      simp only [supItemAsserted, List.mem_flatMap, List.mem_range, isSet, if_true, List.mem_cons, reduceCtorEq,
        false_or, List.filterMap_cons, setOf]
      constructor
      · rintro (⟨i, hi, hm⟩ | h | ⟨t, R', i, x, c, h1, h2, h3, h4⟩)
        · split at hm
          · rename_i c cs heq
            simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff, Prod.mk.injEq] at heq
            obtain ⟨x, hx, c', hc', rfl, _⟩ := heq
            exact Or.inr ⟨0, R, i, x, c', rfl, hx, hc', by simpa using hm⟩
          · cases hm
        · exact Or.inl h
        · exact Or.inr ⟨t + 1, R', i, x, c, by simpa using h1, h2, h3, by
            have e : m0 + 1 + t = m0 + (t + 1) := by omega
            rw [e] at h4; exact h4⟩
      · rintro (h | ⟨t, R', i, x, c, h1, h2, h3, h4⟩)
        · exact Or.inr (Or.inl h)
        · cases t with
          | zero =>
            simp at h1; subst h1
            refine Or.inl ⟨i, (List.getElem?_eq_some_iff.mp h2).1, ?_⟩
            simp only [h2, Option.bind_some, h3, Option.map_some]
            simpa using h4
          | succ t =>
            refine Or.inr (Or.inr ⟨t, R', i, x, c, by simpa using h1, h2, h3, ?_⟩)
            have e : m0 + (t + 1) = m0 + 1 + t := by omega
            rw [e] at h4; exact h4

theorem mem_sup_snd (D : Doc) (a : VE.Formula) :
    a ∈ (sup D).2 ↔ (∃ u c cs, Item.fixed u c cs ∈ D.items ∧ a ∈ asserted c) ∨
      (∃ m, ∃ hm : m < D.sets.length, ∃ i x c, D.sets[m].candidates[i]? = some x ∧ x.content = some c ∧
        a ∈ asserted (gateContent D m i c)) := by
  rw [sup_eq, sup_snd_fold D D.items ((supFrame D, []), 0)]
  simp only [List.nil_append, mem_supAssertedAux, Nat.zero_add]
  apply or_congr Iff.rfl
  rw [← sets_eq]
  constructor
  · rintro ⟨t, R, i, x, c, h1, h2, h3, h4⟩
    obtain ⟨ht, rfl⟩ := List.getElem?_eq_some_iff.mp h1
    exact ⟨t, ht, i, x, c, h2, h3, h4⟩
  · rintro ⟨m, hm, i, x, c, h2, h3, h4⟩
    exact ⟨m, D.sets[m], i, x, c, List.getElem?_eq_getElem hm, h2, h3, h4⟩

theorem asserted_gate {D : Doc} {m i : Nat} {c : Content} {a : VE.Formula} (h : a ∈ asserted (gateContent D m i c)) :
    ∃ φ, c = .assertion φ ∧ a = .implies (pattern (m + 1) (setSize D m) i) φ := by
  cases c with
  | assertion φ => simp [gateContent, asserted] at h; exact ⟨φ, rfl, h⟩
  | norm N => simp [gateContent, asserted] at h
  | _ => simp [gateContent, asserted] at h

/-! ## `Choice_D` of a formula-only document -/

theorem origin_assertions {D : Doc} (hk : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∃ φ, a.content = some (.assertion φ))
    (n : String) : origin D n = none := by
  unfold origin
  apply List.findSome?_eq_none_iff.mpr
  intro m hm
  rw [List.mem_range] at hm
  simp only [Option.map_eq_none_iff]
  apply List.find?_eq_none.mpr
  intro i hi
  rw [List.mem_range, setSize_eq hm] at hi
  rw [List.getElem?_eq_getElem hm]
  simp only [Option.bind_some, List.getElem?_eq_getElem hi]
  obtain ⟨φ, hφ⟩ := hk _ (List.getElem_mem hm) _ (List.getElem_mem hi)
  simp [hφ, Content.declared]

theorem fixedGenerated_of_origin {D : Doc} (ho : ∀ n, origin D n = none) {g : GenKey × String × List String}
    (hg : g ∈ genKeys (sup D).1) : fixedGenerated D g.1 = true := by
  unfold fixedGenerated
  cases hk : g.1 with
  | excepted r b => simp [owners, ho]
  | off r b π => simp [owners, ho]
  | outweighs a L H =>
    obtain ⟨_, M, N, hp, hcmp, ht⟩ := mem_outweighsTriples.mp (mem_genKeys_outweighs hg hk)
    simp only [owners, List.contains_iff_mem, VE.SoftNorms.mem_dedup, List.mem_filterMap]
    refine ⟨(M, N), hp, ?_⟩
    simp only [hcmp, ht, beq_self_eq_true, Bool.and_self, if_true, pairOwner, ho]
    rfl
  | lim L a => simp [owners]
  | cond L a c => simp [owners]
  | aimed m => simp [owners]

theorem choicePremises_assertions {D : Doc} (hk : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∃ φ, a.content = some (.assertion φ))
    (hn : D.couplings = [] ∧ D.narrowings = []) : choicePremises D = (onePremises D).formulas := by
  have ho := origin_assertions hk
  have h2 : quietOwn D = [] := by
    unfold quietOwn
    rw [List.flatMap_eq_nil_iff]
    intro m _
    rw [List.flatMap_eq_nil_iff]
    intro R _
    rw [List.filterMap_eq_nil_iff]
    intro i _
    rw [if_pos]
    rw [List.isEmpty_iff, List.filter_eq_nil_iff]
    intro g hg
    have := fixedGenerated_of_origin ho hg
    unfold fixedGenerated at this
    intro he
    rw [beq_iff_eq] at he
    rw [he] at this
    simp at this
  have h3 : quietShared D = [] := by
    unfold quietShared
    rw [List.map_eq_nil_iff, List.filter_eq_nil_iff]
    intro g hg
    simp [fixedGenerated_of_origin ho hg]
  simp [choicePremises, choiceLabelled, h2, h3, couplingPremises, narrowingPremises, hn.1, hn.2, Labelled.formulas]

/-! ## The theorem -/

/-- 4.7: for a document whose sets are all assertions, without couplings or narrowings, a structure extends to one
    satisfying `sup D`'s assertions and `Choice_D` exactly when it satisfies the fixed assertions and one candidate
    of every set (`readings_all_iff`). -/
theorem superpose_assertions (D : Doc) (h : WellFormedDoc D = true) (hr : supReady D = true)
    (hk : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∃ φ, a.content = some (.assertion φ))
    (hn : D.couplings = [] ∧ D.narrowings = []) (S : VE.Structure.{u}) (hne : Nonempty S.Carrier) :
    (∃ S', ChoiceExtension D S S' ∧ Sat S' ((sup D).2 ++ choicePremises D)) ↔
    (Sat S (free D).2 ∧ ∀ R ∈ D.sets, ∃ a ∈ R.candidates, ∃ φ, a.content = some (.assertion φ) ∧ φ.denote S []) := by
  classical
  have hnd := supReady_nodup hr
  obtain ⟨hsE, hkE, hpE⟩ := sharedEnv_noChoice h hr
  rw [choicePremises_assertions hk hn]
  -- the assertions of `free D` are the fixed assertions
  have hfree : ∀ a, a ∈ (free D).2 ↔ ∃ u cs, Item.fixed u (.assertion a) cs ∈ D.items := by
    intro a
    rw [free, build_snd]
    constructor
    · intro ha
      obtain ⟨it, hit, ha⟩ := List.mem_flatMap.mp ha
      cases it with
      | fixed u c cs =>
        simp only [buildAsserted] at ha
        split at ha
        · exact ⟨u, cs, (asserted_eq ha) ▸ hit⟩
        · cases ha
      | bar u b => cases ha
      | set R => simp [buildAsserted] at ha
    · rintro ⟨u, cs, hit⟩
      refine List.mem_flatMap.mpr ⟨_, hit, ?_⟩
      simp [buildAsserted, fixed_attached_nil hr hit, asserted]
  constructor
  · -- forward: the bits spell an admitted candidate of every set
    rintro ⟨S', ⟨R', dom, k, rfl, hR, hd, hc⟩, hsat⟩
    have tr : ∀ φ : VE.Formula, φ.WellFormed (sharedEnv D) [] →
        (φ.denote { S with relation := R', domain := dom, constant := k } [] ↔ φ.denote S []) :=
      fun φ hφ => choiceExt_denote hsE hkE hpE R' dom k hR hd hc φ [] [] hφ
    have hs1 := (VE.Compose.sat_append _ _ _).mp hsat
    refine ⟨fun a ha => ?_, fun R hR => ?_⟩
    · obtain ⟨u, cs, hit⟩ := (hfree a).mp ha
      exact (tr a (fixed_assertion_shared h hr hit)).mp
        (hs1.1 a ((mem_sup_snd D a).mpr (Or.inl ⟨u, _, cs, hit, by simp [asserted]⟩)))
    · obtain ⟨m, hm, rfl⟩ := mem_sets_getElem hR
      obtain ⟨v, hv, hpat⟩ := pattern_exists { S with relation := R', domain := dom, constant := k } (m + 1)
        (setSize D m)
      have hvk := one_sat hs1.2 hm hv hpat
      rw [setSize_eq hm] at hvk
      obtain ⟨φ, hφ⟩ := hk _ hR _ (List.getElem_mem hvk)
      refine ⟨_, List.getElem_mem hvk, φ, hφ, ?_⟩
      have hg : VE.Formula.implies (pattern (m + 1) (setSize D m) v) φ ∈ (sup D).2 :=
        (mem_sup_snd D _).mpr (Or.inr ⟨m, hm, v, _, _, List.getElem?_eq_getElem hvk, hφ, by
          simp [gateContent, asserted]⟩)
      exact (tr φ (cand_assertion_shared h hr hR (List.getElem?_eq_getElem hvk) hφ)).mp (hs1.1 _ hg hpat)
  · -- backward: set the bits to a candidate that holds
    rintro ⟨hfx, hsets⟩
    obtain ⟨e⟩ := hne
    have hch : ∀ m (hm : m < D.sets.length), ∃ i, ∃ _ : i < D.sets[m].candidates.length, ∃ φ,
        D.sets[m].candidates[i].content = some (.assertion φ) ∧ φ.denote S [] := by
      intro m hm
      obtain ⟨a, ha, φ, hφ, hs⟩ := hsets _ (List.getElem_mem hm)
      obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem ha
      exact ⟨i, hi, φ, hφ, hs⟩
    let chosen : Nat → Nat := fun m => if hm : m < D.sets.length then Classical.choose (hch m hm) else 0
    have hchosen : ∀ m (hm : m < D.sets.length), ∃ _ : chosen m < D.sets[m].candidates.length, ∃ φ,
        D.sets[m].candidates[chosen m].content = some (.assertion φ) ∧ φ.denote S [] := by
      intro m hm
      have := Classical.choose_spec (hch m hm)
      obtain ⟨h1, h2⟩ := this
      have hc : chosen m = Classical.choose (hch m hm) := by simp only [chosen, dif_pos hm]
      rw [hc]
      exact ⟨h1, h2⟩
    let on : String → Prop := fun p => ∃ m j, m < D.sets.length ∧ p = bitName (m + 1) j ∧ (chosen m).testBit j = true
    let R' : String → List S.Carrier → Prop := fun p vs =>
      if p ∈ (bitDecls D).map (·.1) then vs = [e] ∧ on p else S.relation p vs
    let dom : String → S.Carrier → Prop := fun σ x => if σ = "ve__reading" then True else S.domain σ x
    let k : String → Option S.Carrier := fun x => if x = "ve__here" then some e else S.constant x
    let S' : VE.Structure.{u} := { S with relation := R', domain := dom, constant := k }
    have hR : ∀ p, p ∉ (bitDecls D).map (·.1) → ∀ vs, R' p vs ↔ S.relation p vs := by
      intro p hp vs; simp only [R', if_neg hp]
    have hd : ∀ σ, σ ≠ "ve__reading" → dom σ = S.domain σ := by
      intro σ hσ; funext x; simp only [dom, if_neg hσ]
    have hc : ∀ x, x ≠ "ve__here" → k x = S.constant x := by
      intro x hx; simp only [k, if_neg hx]
    have tr : ∀ φ : VE.Formula, φ.WellFormed (sharedEnv D) [] → (φ.denote S' [] ↔ φ.denote S []) :=
      fun φ hφ => choiceExt_denote hsE hkE hpE R' dom k hR hd hc φ [] [] hφ
    have hbit : ∀ m (hm : m < D.sets.length) j, j < bitsOf (setSize D m) →
        (bitOn S' (m + 1) j ↔ (chosen m).testBit j = true) := by
      intro m hm j hj
      have hmem : bitName (m + 1) j ∈ (bitDecls D).map (·.1) := by
        simp only [bitDecls, List.map_flatMap, List.map_map, List.mem_flatMap, List.mem_range, List.mem_map,
          Function.comp]
        exact ⟨m, hm, j, hj, rfl⟩
      show (∃ v, k "ve__here" = some v ∧ R' (bitName (m + 1) j) [v]) ↔ _
      simp only [k, if_true, Option.some.injEq, R', if_pos hmem]
      constructor
      · rintro ⟨_, rfl, _, m', j', hm', he, hb⟩
        obtain ⟨h1, h2⟩ := bitName_inj he
        have : m = m' := by omega
        subst this; subst h2; exact hb
      · intro hb; exact ⟨e, rfl, rfl, m, j, hm, rfl, hb⟩
    have hpat : ∀ m (hm : m < D.sets.length) i, i < 2 ^ bitsOf (setSize D m) →
        ((pattern (m + 1) (setSize D m) i).denote S' [] ↔ i = chosen m) := by
      intro m hm i hi
      have hkb := le_two_pow_bitsOf (setSize D m)
      obtain ⟨hcl, _⟩ := hchosen m hm
      rw [← setSize_eq hm] at hcl
      rw [pattern_denote]
      constructor
      · intro hp
        apply eq_of_low_bits hi (by omega)
        intro j hj
        have := (hbit m hm j hj).symm.trans (hp j hj)
        cases h1 : i.testBit j <;> cases h2 : (chosen m).testBit j <;> simp_all
      · rintro rfl j hj
        exact hbit m hm j hj
    refine ⟨S', ⟨R', dom, k, rfl, hR, hd, hc⟩, (VE.Compose.sat_append _ _ _).mpr ⟨fun a ha => ?_, fun a ha => ?_⟩⟩
    · rcases (mem_sup_snd D a).mp ha with ⟨u, c, cs, hit, hac⟩ | ⟨m, hm, i, x, c, hx, hc', hac⟩
      · have := asserted_eq hac
        subst this
        exact (tr a (fixed_assertion_shared h hr hit)).mpr (hfx a ((hfree a).mpr ⟨u, cs, hit⟩))
      · obtain ⟨φ, rfl, rfl⟩ := asserted_gate hac
        intro hχ
        have hilt : i < D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp hx).1
        have hi2 : i < 2 ^ bitsOf (setSize D m) := by
          have := le_two_pow_bitsOf (setSize D m); rw [setSize_eq hm] at this ⊢; omega
        have hic := (hpat m hm i hi2).mp hχ
        subst hic
        obtain ⟨_, ψ, hψ, hs⟩ := hchosen m hm
        have hxe : x = D.sets[m].candidates[chosen m] := by
          rw [List.getElem?_eq_getElem hilt] at hx; cases hx; rfl
        rw [hxe, hψ] at hc'
        cases hc'
        exact (tr φ (cand_assertion_shared h hr (List.getElem_mem hm) (List.getElem?_eq_getElem hilt)
          (by rw [← hxe]; rw [hxe, hψ]))).mpr hs
    · simp only [onePremises, Labelled.formulas, List.mem_map, List.mem_filterMap, List.mem_range] at ha
      obtain ⟨⟨l, f⟩, ⟨m, hm, hb⟩, rfl⟩ := ha
      rw [List.getElem?_eq_getElem hm] at hb
      simp only [Option.bind_some] at hb
      split at hb
      · cases hb
      · cases hb
        apply (conj_denote S' [] _).mpr
        intro g hg
        obtain ⟨i', hi', rfl⟩ := List.mem_map.mp hg
        simp only [List.mem_filter, List.mem_range, decide_eq_true_eq] at hi'
        intro hp
        rw [← setSize_eq hm] at hi' hp
        have := (hpat m hm i' hi'.1).mp hp
        obtain ⟨hcl, _⟩ := hchosen m hm
        have := hcl
        rw [← setSize_eq hm] at this
        omega

end VE.Readings
