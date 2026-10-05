import VE.Readings.SupConflict

/-! Bases correspond, downward (docs/spec/composition-s2.md 8.4 `base_down`).

A slot-admissible base `B` of `sup D` that encodes `c`, pulled through the name map, is an admissible base of `c`'s
document: it interprets only the choice's base vocabulary at its sorts (a pulled predicate is declared in `c`'s
complete vocabulary and its image is declared in `sup D`'s base vocabulary at the same sorts, `envPrime_nameMap`; a
layer symbol of the choice is one of `sup D`'s, which `B` leaves empty), it keeps the literals, and it satisfies `c`'s
exception and coherence premises. An exception premise of a rule is `sup D`'s premise of its image, whose sufficient
conditions a chosen candidate gates by `χ`, true where `c`'s atoms hold; its conditions are typed over the frame's
vocabulary (`checkSoftRule_exception`, read off the rule check of the document S1 checked the rule in), which the
name map fixes. A coherence premise reads two rules' selections on the expansion; `sup D`'s premise for their images
(in one order or the other, since qualified names need not keep the order) reads the same selections through the
simulation and Lemma K. -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped bindAll)
open VE.SoftNorms (SoftNode SoftDoc soften canon DecidesSoftD envPrime decisions decisionNames exceptedName offName
  outweighsName checkSoftRule SelectsSoftD)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP)
open VE.NormDefaults (ebind_ok ethrow_ok forIn_each epure_ok)
universe u

/-- The conditions of a rule's exception are typed over the rule's document's base vocabulary. -/
theorem checkSoftRule_exception (D : SoftDoc) (N : SoftNode) (h : checkSoftRule D N = .ok ())
    {e : VE.SoftNorms.Exception} (he : N.exception = some e) :
    ∀ C ∈ e.sufficient ++ e.necessary, C.check D.E (VE.SoftNorms.sortsOf D N.pred).reverse = true := by
  unfold checkSoftRule at h
  simp only [he, pure_bind] at h
  cases hr : N.rank with
  | none =>
    rw [hr] at h; dsimp only at h
    by_cases c2 : VE.SoftNorms.sortedDistinct N.alterable = true
    · rw [if_pos c2] at h
      obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
      try dsimp only at h
      by_cases c3 : (N.hard && (N.mode == VE.SoftNorms.Mode.default || !N.alterable.isEmpty)) = true
      · rw [if_pos c3] at h; cases h
      · rw [if_neg c3] at h
        cases hm : N.mode <;> rw [hm] at h <;> dsimp only at h
        · cases h
        · by_cases c4 : Option.all (fun d => !d.isEmpty && decide (d.utf8ByteSize ≤ 64)) e.decidedBy = true
          · rw [if_pos c4] at h
            by_cases c5 : (e.decidedBy.isNone && D.soft.exceptionDecider.isNone) = true
            · rw [if_pos c5] at h; cases h
            · rw [if_neg c5] at h
              obtain ⟨_, h1, _⟩ := (ebind_ok _ _ _).mp h
              intro C hC
              have := forIn_each _ (fun x t r hr => ?_) _ _ _ h1 C hC
              · obtain ⟨_, _, hc⟩ := this
                obtain ⟨_, _, hc⟩ := (ebind_ok _ _ _).mp hc
                try dsimp only at hc
                by_cases c6 : C.check D.E (VE.SoftNorms.sortsOf D N.pred).reverse = true
                · exact c6
                · rw [if_neg c6] at hc; cases hc
              · obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr
                try dsimp only at hr
                by_cases c6 : x.check D.E (VE.SoftNorms.sortsOf D N.pred).reverse = true
                · rw [if_pos c6] at hr
                  split at hr
                  · cases hr
                  · cases hr; exact ⟨_, rfl⟩
                · rw [if_neg c6] at hr; cases hr
          · rw [if_neg c4] at h; cases h
    · rw [if_neg c2] at h; cases h
  | some a =>
    rw [hr] at h; dsimp only at h
    by_cases c1 : D.soft.ranks.contains a = true
    · rw [if_pos c1] at h
      by_cases c2 : VE.SoftNorms.sortedDistinct N.alterable = true
      · rw [if_pos c2] at h
        obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
        try dsimp only at h
        by_cases c3 : (N.hard && (N.mode == VE.SoftNorms.Mode.default || !N.alterable.isEmpty)) = true
        · rw [if_pos c3] at h; cases h
        · rw [if_neg c3] at h
          cases hm : N.mode <;> rw [hm] at h <;> dsimp only at h
          · cases h
          · by_cases c4 : Option.all (fun d => !d.isEmpty && decide (d.utf8ByteSize ≤ 64)) e.decidedBy = true
            · rw [if_pos c4] at h
              by_cases c5 : (e.decidedBy.isNone && D.soft.exceptionDecider.isNone) = true
              · rw [if_pos c5] at h; cases h
              · rw [if_neg c5] at h
                obtain ⟨_, h1, _⟩ := (ebind_ok _ _ _).mp h
                intro C hC
                have := forIn_each _ (fun x t r hr => ?_) _ _ _ h1 C hC
                · obtain ⟨_, _, hc⟩ := this
                  obtain ⟨_, _, hc⟩ := (ebind_ok _ _ _).mp hc
                  try dsimp only at hc
                  by_cases c6 : C.check D.E (VE.SoftNorms.sortsOf D N.pred).reverse = true
                  · exact c6
                  · rw [if_neg c6] at hc; cases hc
                · obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr
                  try dsimp only at hr
                  by_cases c6 : x.check D.E (VE.SoftNorms.sortsOf D N.pred).reverse = true
                  · rw [if_pos c6] at hr
                    split at hr
                    · cases hr
                    · cases hr; exact ⟨_, rfl⟩
                  · rw [if_neg c6] at hr; cases hr
            · rw [if_neg c4] at h; cases h
      · rw [if_neg c2] at h; cases h
    · rw [if_neg c1] at h; cases h

section Down
variable {D : Doc} (hh : Hyps D)
include hh

omit hh in
theorem sortsOf_eq (c : Choice) (p : String) :
    VE.SoftNorms.sortsOf (sup D).1.soft p = VE.SoftNorms.sortsOf (choiceDoc D c).1.soft p := by
  simp only [VE.SoftNorms.sortsOf, regs_eq c]

theorem frame_not_bit {p : String} (hp : D.frame.soft.E.predicates p ≠ none) :
    (bitDecls D).find? (·.1 == p) = none := by
  have hf : choiceFresh D = true := by
    have hr := hh.ready
    simp only [supReady, Bool.and_eq_true] at hr; exact hr.1.2
  simp only [choiceFresh, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hf
  apply List.find?_eq_none.mpr
  intro d hd he
  have h1 := hf.2 d hd
  have h2 : d.1 = p := by simpa using he
  rw [h2] at h1
  exact hp (by simpa using h1)

theorem sup_E_frame {p : String} (hp : D.frame.soft.E.predicates p ≠ none) :
    (sup D).1.soft.E.predicates p = D.frame.soft.E.predicates p := by
  rw [sup_E]
  unfold choiceEnv
  split
  · rfl
  · show (match (bitDecls D).find? (·.1 == p) with
      | some d => some d.2
      | none => D.frame.soft.E.predicates p) = _
    rw [frame_not_bit hh hp]

theorem envPrime_sup_frame {p : String} (hp : D.frame.soft.E.predicates p ≠ none) :
    (envPrime (sup D).1.soft).predicates p = D.frame.soft.E.predicates p := by
  have hnd : p ∉ decisionNames (sup D).1.soft := fun hd => by
    have := (sup_softValid hh).decFresh p hd
    rw [sup_E_frame hh hp] at this; exact hp this
  rw [envPrime_not_decision hnd, sup_E_frame hh hp]

/-- A predicate of the choice's complete vocabulary is named, in `sup D`'s, at the same sorts. -/
theorem envPrime_nameMap (c : Choice) {p : String} {ss : List String}
    (hp : (envPrime (choiceDoc D c).1.soft).predicates p = some ss) :
    (envPrime (sup D).1.soft).predicates (nameMap D c p) = some ss := by
  by_cases hpd : p ∈ decisionNames (choiceDoc D c).1.soft
  · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hpd
    rw [choice_envPrime_decision hh c hx] at hp
    cases hp
    rcases mem_decisions.mp hx with ⟨N, hN, hd, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩
    · obtain ⟨hpred, _, hmode, _, _, _⟩ := fmap_fields hh c hN
      show (envPrime _).predicates (nameMap D c (exceptedName N)) = some (VE.SoftNorms.sortsOf _ N.pred)
      rw [nameMap_excepted hh c hN hd, ← sortsOf_eq c, ← hpred]
      exact envPrime_decision (sup_wfSoft hh)
        (mem_decisions.mpr (Or.inl ⟨_, fmap_mem hh c hN, by rw [hmode]; exact hd, rfl⟩))
    · obtain ⟨hpred, _, _, _, halt, _⟩ := fmap_fields hh c hN
      show (envPrime _).predicates (nameMap D c (offName N π)) = some (VE.SoftNorms.sortsOf _ N.pred)
      rw [nameMap_off hh c hN hπ, ← sortsOf_eq c, ← hpred]
      exact envPrime_decision (sup_wfSoft hh)
        (mem_decisions.mpr (Or.inr (Or.inl ⟨_, fmap_mem hh c hN, π, by rw [halt]; exact hπ, rfl⟩)))
    · show (envPrime _).predicates (nameMap D c (outweighsName a L H)) =
        some (VE.SoftNorms.actSortsOf _ a)
      rw [nameMap_outweighs hh c]
      have : VE.SoftNorms.actSortsOf (choiceDoc D c).1.soft a = VE.SoftNorms.actSortsOf (sup D).1.soft a :=
        (sortsOf_eq c a).symm
      rw [this]
      exact envPrime_decision (sup_wfSoft hh) (mem_decisions.mpr (Or.inr (Or.inr ⟨a, L, H, triple_sup hh c ht, rfl⟩)))
  · rw [envPrime_not_decision hpd, choice_E c] at hp
    rw [nameMap_frame hh c (by rw [hp]; simp), envPrime_sup_frame hh (by rw [hp]; simp)]
    exact hp

theorem pull_admissible {c : Choice} (hc : Compatible D c) (B : VE.Structure.{u})
    (hadm : B.Admissible (envAt (soften (sup D).1.soft) 0)) :
    (pull D c B).Admissible (envAt (soften (choiceDoc D c).1.soft) 0) := by
  refine ⟨fun x s hx => constantsTyped_pull hh (c := c) B hadm.1 x s hx, ?_⟩
  intro p vs hrel
  obtain ⟨hne, hrel⟩ := hrel
  obtain ⟨ss', hss', htyped⟩ := hadm.2 _ _ hrel
  by_cases hpl : p ∈ VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T
  · exfalso
    obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hpl
    rw [nameMap_frame hh c (by rw [choice_sym_frame hh c hq]; simp)] at hss'
    have hX := (layer_iff hh hc _).mp hpl
    have : (envAt (soften (sup D).1.soft) 0).predicates q.name = none := by
      simp [envAt, VE.Norms.hide, hX]
    rw [this] at hss'; cases hss'
  · rw [choiceEnvFull_eq hh c] at hne
    obtain ⟨ss, hss⟩ := Option.ne_none_iff_exists'.mp hne
    have h2 := envPrime_nameMap hh c hss
    have h3 : (envPrime (sup D).1.soft).predicates (nameMap D c p) = some ss' := envAt_sub hss'
    rw [h2] at h3
    cases h3
    exact ⟨ss', by rw [VE.Norms.envAt_base hpl]; exact hss,
      (VE.Route.Examples.tupleTyped_relation B _ _ vs).mpr htyped⟩

omit hh in
theorem pull_literals (c : Choice) (B : VE.Structure.{u})
    (hl : Sat B (VE.Norms.backgroundBase (soften (sup D).1.soft))) :
    Sat (pull D c B) (VE.Norms.backgroundBase (soften (choiceDoc D c).1.soft)) := by
  have e : (soften (choiceDoc D c).1.soft).lits = (soften (sup D).1.soft).lits := by
    show (build D (fun _ => true) (pickC c)).1.soft.lits = (sup D).1.soft.lits
    rw [(build_shape D (fun _ => true) (pickC c)).lits, (sup_shape D).lits]; rfl
  intro a ha
  unfold VE.Norms.backgroundBase at ha
  rw [e] at ha
  have := hl a ha
  obtain ⟨x, _, rfl⟩ := List.mem_map.mp ha
  exact this

/-- The home document of a rule of the choice's document is well formed. -/
theorem choice_exc_typed (c : Choice) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    {e : VE.SoftNorms.Exception} (hex : N.exception = some e) :
    ∀ C ∈ e.sufficient ++ e.necessary, ∃ Γ, C.WellFormed D.frame.soft.E Γ := by
  obtain ⟨keep, pick, _, hw, hm⟩ := choice_home hh c hN
  have hsh := build_shape D keep pick
  have hcw : chainWF D.chain (build D keep pick).1 = true := by
    simp only [sideWF, Bool.and_eq_true] at hw; exact hw.1
  have hsoft : VE.SoftNorms.WellFormedSoft (build D keep pick).1.soft = true := by
    cases hd : D.chain with
    | rights => exact absurd hd hh.chain
    | soft => rw [hd] at hcw; simp only [chainWF, Bool.and_eq_true] at hcw; exact hcw.2
    | norms => rw [hd] at hcw; simp only [chainWF, Bool.and_eq_true] at hcw; exact hcw.2
  have hrule := (checkSoft_parts _ (wellFormedSoft_check _ hsoft)).2 N hm
  intro C hC
  have := checkSoftRule_exception _ N hrule hex C hC
  rw [hsh.E] at this
  exact ⟨_, (VE.check_iff_wellFormed _ _ _).mp this⟩

/-- The exception of a rule's image: its own, with a chosen candidate's sufficient conditions gated by `χ`. -/
theorem fmap_exception (c : Choice) (B : VE.Structure.{u}) (he : Encodes D c B) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {e : VE.SoftNorms.Exception} (hex : N.exception = some e) :
    ∃ e', (fmap D c N).exception = some e' ∧ e'.necessary = e.necessary ∧
      ∀ (ρ : VE.Valuation B), ∀ C ∈ e.sufficient, ∃ C' ∈ e'.sufficient, (C'.denote B ρ ↔ C.denote B ρ) := by
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hcc⟩
  · rw [fmap_frame hh c hf]; exact ⟨e, hex, rfl, fun ρ C hC => ⟨C, hC, Iff.rfl⟩⟩
  · rw [fmap_fixed hh c hu]; exact ⟨e, hex, rfl, fun ρ C hC => ⟨C, hC, Iff.rfl⟩⟩
  · rw [fmap_chosen hh c hm hi ha hcc]
    refine ⟨{ e with sufficient := e.sufficient.map (fun C => .and C (pattern (m + 1) (setSize D m) i)) },
      by simp [gateNorm, hex], rfl, fun ρ C hC => ⟨_, List.mem_map_of_mem hC, ?_⟩⟩
    have hilt : i < setSize D m := by rw [setSize_eq hm]; exact (List.getElem?_eq_some_iff.mp ha).1
    have hχ : (pattern (m + 1) (setSize D m) i).denote B ρ := by
      rw [pattern_rho, ← choiceAtom_eq (findIdx_of_nodup hh.nodup hm) hilt]
      exact (he _ (List.getElem_mem hm) i (by rw [← setSize_eq hm]; exact hilt)).mpr (mem_of_index hi)
    simp only [VE.Formula.denote]
    exact ⟨fun h => h.1, fun h => ⟨h, hχ⟩⟩

theorem excepted_pull (c : Choice) (B : VE.Structure.{u}) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) (hd : N.mode = .default) (ρ : VE.Valuation B) :
    (VE.SoftNorms.exceptedF (sup D).1.soft (fmap D c N)).denote B ρ ↔
      (VE.SoftNorms.exceptedF (choiceDoc D c).1.soft N).denote (pull D c B) ρ := by
  obtain ⟨hpred, _, _, _, _, _⟩ := fmap_fields hh c hN
  simp only [VE.SoftNorms.exceptedF, hpred, sortsOf_eq c]
  exact atom_congr B _ _ _ _ (fun vs => (pull_excepted hh c B hN hd vs).symm) ρ

theorem exc_down (c : Choice) (B : VE.Structure.{u}) (he : Encodes D c B)
    (hX : Sat B (VE.SoftNorms.excPremises (sup D).1.soft)) :
    Sat (pull D c B) (VE.SoftNorms.excPremises (choiceDoc D c).1.soft) := by
  intro a ha
  obtain ⟨N, hN, ha⟩ := List.mem_flatMap.mp ha
  obtain ⟨hpred, _, hmode, _, _, _⟩ := fmap_fields hh c hN
  have hfX : fmap D c N ∈ (sup D).1.soft.T.nodes := fmap_mem hh c hN
  have hss : VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred =
      VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred := by rw [hpred, sortsOf_eq c]
  have tp : ∀ (vs : List B.Carrier), VE.TupleTyped (pull D c B) (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred) vs →
      VE.TupleTyped B (VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred) vs := fun vs h => by
    rw [hss]; exact (VE.Route.Examples.tupleTyped_relation B _ _ vs).mp h
  unfold VE.SoftNorms.excPremisesOf at ha
  cases hm : N.mode with
  | strict => rw [hm] at ha; cases ha
  | default =>
    cases hex : N.exception with
    | none => rw [hm, hex] at ha; cases ha
    | some e =>
      rw [hm, hex] at ha
      obtain ⟨e', hex', hnec, hsuf⟩ := fmap_exception hh c B he hN hex
      have hXp : ∀ a' ∈ VE.SoftNorms.excPremisesOf (sup D).1.soft (fmap D c N), a'.denote B [] :=
        fun a' h' => hX a' (List.mem_flatMap.mpr ⟨_, hfX, h'⟩)
      have hfm : (fmap D c N).mode = .default := by rw [hmode, hm]
      have htyped := choice_exc_typed hh c hN hex
      have hC : ∀ C ∈ e.sufficient ++ e.necessary, ∀ ρ, C.denote (pull D c B) ρ ↔ C.denote B ρ := fun C hC ρ => by
        obtain ⟨Γ, hw⟩ := htyped C hC; exact (pull_denote_frame hh c B C Γ hw ρ).symm
      rcases List.mem_append.mp ha with ha | ha
      · obtain ⟨C, hCm, rfl⟩ := List.mem_map.mp ha
        rw [VE.Norms.bindAll_denote_nil]
        intro vs hvs
        simp only [VE.Formula.denote]
        intro hCY
        obtain ⟨C', hC'm, hC'⟩ := hsuf (tupleVal vs) C hCm
        have hprem := hXp (bindAll (VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred)
          (.implies C' (VE.SoftNorms.exceptedF (sup D).1.soft (fmap D c N)))) (by
            unfold VE.SoftNorms.excPremisesOf; rw [hfm, hex']
            exact List.mem_append_left _ (List.mem_map_of_mem hC'm))
        rw [VE.Norms.bindAll_denote_nil] at hprem
        exact (excepted_pull hh c B hN hm _).mp
          (hprem vs (tp vs hvs) (hC'.mpr ((hC C (List.mem_append_left _ hCm) _).mp hCY)))
      · obtain ⟨C, hCm, rfl⟩ := List.mem_map.mp ha
        rw [VE.Norms.bindAll_denote_nil]
        intro vs hvs
        simp only [VE.Formula.denote]
        intro hEY
        have hprem := hXp (bindAll (VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred)
          (.implies (VE.SoftNorms.exceptedF (sup D).1.soft (fmap D c N)) C)) (by
            unfold VE.SoftNorms.excPremisesOf; rw [hfm, hex']
            exact List.mem_append_right _ (by rw [hnec]; exact List.mem_map_of_mem hCm))
        rw [VE.Norms.bindAll_denote_nil] at hprem
        exact (hC C (List.mem_append_right _ hCm) _).mpr
          (hprem vs (tp vs hvs) ((excepted_pull hh c B hN hm _).mpr hEY))

theorem choice_selTyped {c : Choice} (hc : Compatible D c) {M : SoftNode} (hM : M ∈ (choiceDoc D c).1.soft.T.nodes) :
    (VE.SoftNorms.selects' (choiceDoc D c).1.soft M).WellFormed
      (envAt (soften (choiceDoc D c).1.soft) (size (soften (choiceDoc D c).1.soft)))
      (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred).reverse := by
  have hvY := choice_valid hh hc
  obtain ⟨hpred, _⟩ := fmap_fields hh c hM
  have hreg := (sup_softValid hh).predReg _ (fmap_mem hh c hM)
  rw [hpred] at hreg
  obtain ⟨r, hr, hrn⟩ := List.mem_map.mp hreg
  have hrY : r ∈ (soften (choiceDoc D c).1.soft).T.regulated := by
    show r ∈ (choiceDoc D c).1.soft.T.regulated; rw [← regs_eq c]; exact hr
  have hk := VE.Norms.index_before hvY hrY
  have hT := VE.Norms.rulesTyped_of_valid hvY hk
  have hsel := VE.Norms.selects_wellFormed hT (VE.Norms.fuel (soften (choiceDoc D c).1.soft).T)
    (VE.SoftNorms.primeNode (choiceDoc D c).1.soft M) (List.mem_map_of_mem hM) (by show M.pred = r.name; rw [hrn])
  have hlt := (List.getElem?_eq_some_iff.mp hk).1
  have hsorts : VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred = r.sorts := by
    have hf := VE.Norms.find_regulated hvY hk
    unfold VE.SoftNorms.sortsOf VE.SoftNorms.sortsIn
    rw [← hrn]
    have e : (choiceDoc D c).1.soft.T.regulated = (soften (choiceDoc D c).1.soft).T.regulated := rfl
    rw [e, hf]; rfl
  rw [hsorts]
  exact VE.Norms.envAt_mono (Nat.le_of_lt hlt) _ _ hsel

/-- `coh_canon` for a choice's document, from `Valid` of its softened form. -/
theorem coh_canonY {c : Choice} (hc : Compatible D c) (S : VE.Structure.{u})
    (hcS : ConstantsTyped (soften (choiceDoc D c).1.soft) S) {M N : SoftNode}
    (hMN : (M, N) ∈ VE.SoftNorms.collidingPairs (choiceDoc D c).1.soft)
    (hsorts : VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred = VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred) :
    (VE.SoftNorms.cohPremise (choiceDoc D c).1.soft M N).denote S [] ↔
      ∀ vs, VE.TupleTyped S (VE.SoftNorms.actSorts (choiceDoc D c).1.soft M) vs →
        ¬ (SelectsSoftD (choiceDoc D c).1.soft (canon (soften (choiceDoc D c).1.soft) S) (tupleVal vs)
            (VE.SoftNorms.fuel (choiceDoc D c).1.soft) M ∧
           SelectsSoftD (choiceDoc D c).1.soft (canon (soften (choiceDoc D c).1.soft) S) (tupleVal vs)
            (VE.SoftNorms.fuel (choiceDoc D c).1.soft) N) := by
  obtain ⟨hM, hN, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hMN
  have hvY := choice_valid hh hc
  rw [VE.SoftNorms.cohPremise, VE.Norms.bindAll_denote_nil]
  apply forall_congr'; intro vs; apply imp_congr_right; intro hvs
  have hρ := VE.Norms.tupleVal_typed S _ vs hvs
  have hwN := choice_selTyped hh hc hN
  rw [← hsorts] at hwN
  simp only [VE.Formula.denote]
  rw [VE.SoftNorms.canon_subst hvY S hcS _ _ _ (choice_selTyped hh hc hM) _ hρ,
    VE.SoftNorms.canon_subst hvY S hcS _ _ _ hwN _ hρ,
    VE.SoftNorms.selectsPrime_denote, VE.SoftNorms.selectsPrime_denote]

theorem selects_iff {c : Choice} (hc : Compatible D c) (B : VE.Structure.{u})
    (hcB : ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, B.constant x = some v)
    (he : Encodes D c B) {M : SoftNode} (hM : M ∈ (choiceDoc D c).1.soft.T.nodes) (vs : List B.Carrier) :
    SelectsSoftD (sup D).1.soft (canon (soften (sup D).1.soft) B) (tupleVal vs) (VE.SoftNorms.fuel (sup D).1.soft)
        (fmap D c M) ↔
      SelectsSoftD (choiceDoc D c).1.soft (canon (soften (choiceDoc D c).1.soft) (pull D c B)) (tupleVal vs)
        (VE.SoftNorms.fuel (choiceDoc D c).1.soft) M := by
  have hs := faithful_sim hh hc (canon (soften (sup D).1.soft) B) (encodes_canon hh B he) (tupleVal vs)
  refine (sim_selects_fuel hs M hM).trans ?_
  rw [← VE.SoftNorms.selectsPrime_denote, ← VE.SoftNorms.selectsPrime_denote]
  exact denote_relation_congr _ (pull D c (canon (soften (sup D).1.soft) B))
    (canon (soften (choiceDoc D c).1.soft) (pull D c B)).relation
    (fun p ss hp vs' hvs' => pull_canon hh hc B hcB he (envAt_sub hp) vs' hvs') _ _ _
    ((VE.check_iff_wellFormed _ _ _).mpr (choice_selTyped hh hc hM))

theorem coh_down {c : Choice} (hc : Compatible D c) (B : VE.Structure.{u})
    (hBX : VE.Norms.BaseAdmissible (soften (sup D).1.soft) B) (he : Encodes D c B)
    (hX : Sat B (VE.SoftNorms.cohPremises (sup D).1.soft)) :
    Sat (pull D c B) (VE.SoftNorms.cohPremises (choiceDoc D c).1.soft) := by
  have hcB : ConstantsTyped (soften (sup D).1.soft) B := hBX.1.1
  have hcB' : ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, B.constant x = some v :=
    fun x s h => (hcB x s h).imp fun _ h => h.1
  have hvX := sup_softValid hh
  intro a ha
  obtain ⟨⟨M, N⟩, hMN, rfl⟩ := List.mem_map.mp ha
  obtain ⟨hM, hN, hMd, hNd, hlt, hinc⟩ := VE.SoftNorms.mem_collidingPairs.mp hMN
  obtain ⟨hpM, _, hmM, _, _, _⟩ := fmap_fields hh c hM
  obtain ⟨hpN, _, hmN, _, _, _⟩ := fmap_fields hh c hN
  have hs := faithful_sim hh hc (canon (soften (sup D).1.soft) B) (encodes_canon hh B he) []
  have hincX : VE.SoftNorms.Incompatible (sup D).1.soft (fmap D c M) (fmap D c N) = true := by
    rw [sim_incompatible hs M N hM hN]; exact hinc
  have hne : (fmap D c M).name ≠ (fmap D c N).name := fun h => by
    have h1 := fmap_inj hh c hM hN (sup_name_inj hh (fmap_mem hh c hM) (fmap_mem hh c hN) h)
    subst h1
    exact absurd hlt (String.lt_irrefl _)
  have key : (VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c M).pred =
      VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred) ∧
      ∀ vs, VE.TupleTyped B (VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c M).pred) vs →
        ¬ (SelectsSoftD (sup D).1.soft (canon (soften (sup D).1.soft) B) (tupleVal vs)
              (VE.SoftNorms.fuel (sup D).1.soft) (fmap D c M) ∧
           SelectsSoftD (sup D).1.soft (canon (soften (sup D).1.soft) B) (tupleVal vs)
              (VE.SoftNorms.fuel (sup D).1.soft) (fmap D c N)) := by
    rcases VE.SoftNorms.str_lt_or_gt _ _ hne with h1 | h1
    · have hp : (fmap D c M, fmap D c N) ∈ VE.SoftNorms.collidingPairs (sup D).1.soft :=
        VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM, fmap_mem hh c hN, by rw [hmM]; exact hMd,
          by rw [hmN]; exact hNd, h1, hincX⟩
      exact ⟨hvX.cpSorts _ hp, (VE.SoftNorms.coh_canon hvX B hBX hp).mp (hX _ (List.mem_map.mpr ⟨_, hp, rfl⟩))⟩
    · have hp : (fmap D c N, fmap D c M) ∈ VE.SoftNorms.collidingPairs (sup D).1.soft :=
        VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hN, fmap_mem hh c hM, by rw [hmN]; exact hNd,
          by rw [hmM]; exact hMd, h1, by rw [VE.SoftNorms.incompatible_symm]; exact hincX⟩
      have hsrt : VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred =
          VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c M).pred := hvX.cpSorts _ hp
      have := (VE.SoftNorms.coh_canon hvX B hBX hp).mp (hX _ (List.mem_map.mpr ⟨_, hp, rfl⟩))
      refine ⟨hsrt.symm, fun vs hvs h => this vs ?_ ⟨h.2, h.1⟩⟩
      show VE.TupleTyped B (VE.SoftNorms.sortsOf _ (fmap D c N).pred) vs
      rw [hsrt]; exact hvs
  have hsY : VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred =
      VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred := by
    rw [← sortsOf_eq c, ← sortsOf_eq c, ← hpM, ← hpN]; exact key.1
  rw [coh_canonY hh hc (pull D c B) (constantsTyped_pull hh B hcB) hMN hsY]
  intro vs hvs h
  apply key.2 vs
  · show VE.TupleTyped B (VE.SoftNorms.sortsOf _ (fmap D c M).pred) vs
    rw [hpM, sortsOf_eq c]; exact (VE.Route.Examples.tupleTyped_relation B _ _ vs).mp hvs
  · exact ⟨(selects_iff hh hc B hcB' he hM vs).mpr h.1, (selects_iff hh hc B hcB' he hN vs).mpr h.2⟩

end Down

/-- Bases correspond, downward. -/
theorem base_down (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights) (hs : superposable D = true)
    (c : Choice) (hc : Compatible D c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) (he : Encodes D c B) :
    VE.Rights.BaseAdmissibleR (choiceDoc D c).1 (pull D c B) := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hYn := choiceDoc_noRights D c hh.noRights
  unfold VE.Rights.BaseAdmissibleR
  rw [(correlate_noRights _ hYn).1, (correlate_noRights _ hYn).2]
  rw [sup_correlate hh] at hB
  refine ⟨⟨⟨pull_admissible hh hc B hB.1.1.1, pull_literals c B hB.1.1.2⟩, ?_⟩, fun _ h => nomatch h⟩
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact exc_down hh c B he (fun a' h' => hB.1.2 a' (List.mem_append_left _ h')) a ha
  · exact coh_down hh hc B hB.1.1 he (fun a' h' => hB.1.2 a' (List.mem_append_right _ h')) a ha

end VE.Readings
