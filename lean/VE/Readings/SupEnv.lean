import VE.Readings.Labels
import VE.Readings.Wire

/-! The vocabulary of a well-formed soft document and of `sup D` at level 0 (docs/spec/composition-s2.md 1.3, 1.6):
which names `envAt (soften X) 0` declares, and with which sorts.

A decision predicate's name begins `soft__`; a layer symbol is a regulated predicate, which the environment
declares and a decision predicate's name never is (`decFresh`), or a defined predicate, whose name never begins
`soft__` (the soft check refuses it). So the level-0 vocabulary declares every decision predicate with its sorts,
and every other name as the document's environment does. In `sup D` the environment is the frame's with the choice
vocabulary added: a bit predicate begins `ve__`, which no regulated or defined predicate of the frame does
(`reservedFree`), and `v`, which no decision predicate does. -/
namespace VE.Readings
open VE.Norms (envAt size Arity atom bindAll)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft decisions decisionNames envPrime checkSoft
  reservedPredicate)
open VE.Rights (RightsDoc correlate)
open VE.NormDefaults (ebind_ok forIn_each)

/-! ## Names -/

theorem soft_prefix_ascii : AsciiL "soft__".data := by decide

theorem exceptedName_soft (N : SoftNode) : (VE.SoftNorms.exceptedName N).startsWith "soft__" = true := by
  have : VE.SoftNorms.exceptedName N = "soft__" ++ ("excepted__" ++ VE.SoftNorms.ruleKey N.name) := by
    apply String.ext; simp [VE.SoftNorms.exceptedName, String.data_append]
  rw [this]; exact startsWith_append_ascii _ _ soft_prefix_ascii

theorem offName_soft (N : SoftNode) (π : String) : (VE.SoftNorms.offName N π).startsWith "soft__" = true := by
  have : VE.SoftNorms.offName N π = "soft__" ++ ("off__" ++ VE.SoftNorms.ruleKey N.name ++ "__" ++ π) := by
    apply String.ext; simp [VE.SoftNorms.offName, String.data_append]
  rw [this]; exact startsWith_append_ascii _ _ soft_prefix_ascii

theorem outweighsName_soft (a L H : String) : (VE.SoftNorms.outweighsName a L H).startsWith "soft__" = true := by
  have : VE.SoftNorms.outweighsName a L H = "soft__" ++ ("outweighs__" ++ L ++ "__" ++ H ++ "__" ++ a) := by
    apply String.ext; simp [VE.SoftNorms.outweighsName, String.data_append]
  rw [this]; exact startsWith_append_ascii _ _ soft_prefix_ascii

theorem mem_decisions {X : SoftDoc} {d : String × List String} :
    d ∈ decisions X ↔ (∃ N ∈ X.T.nodes, N.mode = .default ∧ d = (VE.SoftNorms.exceptedName N, VE.SoftNorms.sortsOf X N.pred)) ∨
      (∃ N ∈ X.T.nodes, ∃ π ∈ N.alterable, d = (VE.SoftNorms.offName N π, VE.SoftNorms.sortsOf X N.pred)) ∨
      (∃ a L H, (a, L, H) ∈ VE.SoftNorms.outweighsTriples X ∧
        d = (VE.SoftNorms.outweighsName a L H, VE.SoftNorms.actSortsOf X a)) := by
  simp only [decisions, VE.SoftNorms.exceptedDecisions, VE.SoftNorms.offDecisions, VE.SoftNorms.outweighsDecisions,
    List.mem_append, List.mem_map, List.mem_filter, List.mem_flatMap, beq_iff_eq]
  constructor
  · rintro ((⟨N, ⟨hN, hd⟩, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩) | ⟨⟨a, L, H⟩, ht, rfl⟩)
    · exact Or.inl ⟨N, hN, hd, rfl⟩
    · exact Or.inr (Or.inl ⟨N, hN, π, hπ, rfl⟩)
    · exact Or.inr (Or.inr ⟨a, L, H, ht, rfl⟩)
  · rintro (⟨N, hN, hd, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩)
    · exact Or.inl (Or.inl ⟨N, ⟨hN, hd⟩, rfl⟩)
    · exact Or.inl (Or.inr ⟨N, hN, π, hπ, rfl⟩)
    · exact Or.inr ⟨(a, L, H), ht, rfl⟩

theorem decision_soft {X : SoftDoc} {n : String} (h : n ∈ decisionNames X) : n.startsWith "soft__" = true := by
  obtain ⟨d, hd, rfl⟩ := List.mem_map.mp h
  rcases mem_decisions.mp hd with ⟨N, _, _, rfl⟩ | ⟨N, _, π, _, rfl⟩ | ⟨a, L, H, _, rfl⟩
  · exact exceptedName_soft N
  · exact offName_soft N π
  · exact outweighsName_soft a L H

/-! ## The soft check on definitions -/

theorem checkSoft_defs (X : SoftDoc) (h : checkSoft X = .ok ()) :
    ∀ d ∈ X.T.definitions, reservedPredicate d.name = false := by
  unfold checkSoft at h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, _, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, h3, _⟩ := (ebind_ok _ _ _).mp h
  intro d hd
  have := forIn_each _ (fun x t r hr => ?_) _ _ _ h3 d.name (List.mem_map.mpr ⟨d, hd, rfl⟩)
  · obtain ⟨_, _, hc⟩ := this
    split at hc
    · exact (throw_bind_ok hc).elim
    · rename_i hn; simpa using hn
  · split at hr
    · exact (throw_bind_ok hr).elim
    · obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr; cases hr; exact ⟨_, rfl⟩

/-! ## The level-0 vocabulary of a well-formed soft document -/

section SoftEnv
variable {X : SoftDoc} (hw : WellFormedSoft X = true)
include hw

omit hw in
theorem layer_mem (n : String) (hn : n ∈ VE.Norms.layerNames (soften X).T) :
    (∃ r ∈ X.T.regulated, r.name = n) ∨ (∃ d ∈ X.T.definitions, d.name = n) := by
  have := Wire.layerNames_sub hn
  rcases List.mem_append.mp this with h | h
  · obtain ⟨r, hr, rfl⟩ := List.mem_map.mp h; exact Or.inl ⟨r, hr, rfl⟩
  · obtain ⟨d, hd, rfl⟩ := List.mem_map.mp h; exact Or.inr ⟨d, hd, rfl⟩

theorem layer_not_decision {n : String} (hn : n ∈ VE.Norms.layerNames (soften X).T) : n ∉ decisionNames X := by
  have hv := VE.SoftNorms.softValid_of_wellFormed X hw
  intro hd
  rcases layer_mem n hn with ⟨r, hr, rfl⟩ | ⟨d, hdm, rfl⟩
  · have h1 := hv.regDecl r hr
    rw [hv.decFresh _ hd] at h1
    cases h1
  · have h1 := checkSoft_defs X (wellFormedSoft_check X hw) d hdm
    unfold reservedPredicate at h1
    rw [decision_soft hd] at h1
    cases h1

theorem envPrime_decision {d : String × List String} (hd : d ∈ decisions X) : (envPrime X).predicates d.1 = some d.2 := by
  have hv := VE.SoftNorms.softValid_of_wellFormed X hw
  unfold envPrime
  simp only
  rw [VE.SoftNorms.find_key (fun x : String × List String => x.1) _ hv.decNodup d hd]

theorem envAt_decision (k : Nat) {d : String × List String} (hd : d ∈ decisions X) :
    (envAt (soften X) k).predicates d.1 = some d.2 := by
  simp only [envAt, VE.Norms.hide]
  rw [if_neg (fun h => layer_not_decision hw (List.mem_of_mem_drop h) (List.mem_map.mpr ⟨d, hd, rfl⟩))]
  exact envPrime_decision hw hd

omit hw in
theorem envAt_other (k : Nat) {n : String} (hl : n ∉ VE.Norms.layerNames (soften X).T)
    (hd : n ∉ decisionNames X) : (envAt (soften X) k).predicates n = X.E.predicates n := by
  simp only [envAt, VE.Norms.hide]
  rw [if_neg (fun h => hl (List.mem_of_mem_drop h))]
  show (envPrime X).predicates n = _
  unfold envPrime
  simp only
  rw [List.find?_eq_none.mpr (fun x hx he => hd (List.mem_map.mpr ⟨x, hx, by simpa using he⟩))]

theorem sortsOf_sorts (p : String) : ∀ s ∈ VE.SoftNorms.sortsOf X p, s ∈ X.E.sorts := by
  have hv := VE.SoftNorms.softValid_of_wellFormed X hw
  have hvn := VE.Norms.valid_of_wellFormed _ hv.wf
  intro s hs
  unfold VE.SoftNorms.sortsOf VE.SoftNorms.sortsIn at hs
  cases hf : X.T.regulated.find? (·.name == p) with
  | none => rw [hf] at hs; cases hs
  | some r =>
    rw [hf] at hs
    have hr := List.mem_of_find?_eq_some hf
    exact (hvn.decl _ (hvn.regulated r hr)).2.2 s hs

theorem decision_sorts {d : String × List String} (hd : d ∈ decisions X) : ∀ s ∈ d.2, s ∈ X.E.sorts := by
  rcases mem_decisions.mp hd with ⟨N, _, _, rfl⟩ | ⟨N, _, π, _, rfl⟩ | ⟨a, L, H, _, rfl⟩
  · exact sortsOf_sorts hw _
  · exact sortsOf_sorts hw _
  · exact sortsOf_sorts hw _

end SoftEnv

theorem envAt_sorts0 (Y : VE.Norms.Doc) (k : Nat) : (envAt Y k).sorts = Y.E.sorts := rfl
theorem envAt_consts0 (Y : VE.Norms.Doc) (k : Nat) : (envAt Y k).constants = Y.E.constants := rfl
theorem soften_E (X : SoftDoc) : (soften X).E = envPrime X := rfl
theorem envPrime_sorts (X : SoftDoc) : (envPrime X).sorts = X.E.sorts := rfl
theorem envPrime_constants (X : SoftDoc) : (envPrime X).constants = X.E.constants := rfl

/-! ## The choice vocabulary in `sup D` -/

theorem bitName_reserved (n j : Nat) : reservedSym (bitName n j) = true := by
  unfold reservedSym bitName
  have : "ve__bit__" ++ toString n ++ "__" ++ toString j = "ve__" ++ ("bit__" ++ toString n ++ "__" ++ toString j) := by
    apply String.ext; simp [String.data_append]
  rw [this]
  exact startsWith_append_ascii _ _ (by decide)

theorem bitName_head (n j : Nat) : (bitName n j).data.head? = some 'v' := by
  simp [bitName, String.data_append]

theorem decision_head {X : SoftDoc} {n : String} (h : n ∈ decisionNames X) : n.data.head? = some 's' := by
  obtain ⟨t, rfl⟩ := eq_append_of_startsWith soft_prefix_ascii (decision_soft h)
  simp [String.data_append]

theorem bitName_not_decision {X : SoftDoc} (n j : Nat) : bitName n j ∉ decisionNames X := by
  intro h
  have := decision_head h
  rw [bitName_head] at this
  cases this

theorem sup_E {D : Doc} : (sup D).1.soft.E = choiceEnv D D.frame.soft.E := (sup_shape D).E

theorem sup_reg {D : Doc} : (sup D).1.soft.T.regulated = D.frame.soft.T.regulated := (sup_shape D).regulated

theorem sup_defs {D : Doc} : (sup D).1.soft.T.definitions = D.frame.soft.T.definitions := (sup_shape D).definitions

theorem sets_ne_nil {D : Doc} {m : Nat} (hm : m < D.sets.length) : D.sets.isEmpty = false := by
  cases h : D.sets with
  | nil => rw [h] at hm; simp at hm
  | cons _ _ => rfl

section Sup
variable {D : Doc} (hh : Hyps D)
include hh

theorem sup_wfSoft : WellFormedSoft (sup D).1.soft = true := by
  have := (sup_wellFormed D hh.sp).2
  rwa [sup_correlate hh] at this

theorem frame_names_free : ∀ n ∈ D.frame.soft.T.regulated.map (·.name) ++ D.frame.soft.T.definitions.map (·.name),
    reservedSym n = false := by
  have hr := (wellFormedDoc_parts hh.wf).1
  simp only [reservedFree, Bool.and_eq_true, Bool.not_eq_true', List.any_eq_false, List.mem_append] at hr
  intro n hn
  have := hr.1.1 n
  simp only [List.mem_append] at this hn
  cases hs : reservedSym n
  · rfl
  · exact absurd hs (by
      rcases hn with hn | hn
      · exact this (Or.inl (Or.inr hn))
      · exact this (Or.inr hn))

theorem bit_not_layer (n j : Nat) : bitName n j ∉ VE.Norms.layerNames (soften (sup D).1.soft).T := by
  intro h
  have := Wire.layerNames_sub h
  simp only [soften, sup_reg, sup_defs] at this
  have := frame_names_free hh _ this
  rw [bitName_reserved] at this
  cases this

omit hh in
theorem choiceEnv_bit {m j : Nat} (hm : m < D.sets.length) (hj : j < bitsOf (setSize D m)) :
    (choiceEnv D D.frame.soft.E).predicates (bitName (m + 1) j) = some ["ve__reading"] := by
  unfold choiceEnv
  rw [sets_ne_nil hm]
  simp only [Bool.false_eq_true, if_false]
  have hmem : (bitName (m + 1) j, ["ve__reading"]) ∈ bitDecls D := by
    simp only [bitDecls, List.mem_flatMap, List.mem_range, List.mem_map]
    exact ⟨m, hm, j, hj, rfl⟩
  cases hf : (bitDecls D).find? (·.1 == bitName (m + 1) j) with
  | none => exact absurd hmem (fun h => by simpa using List.find?_eq_none.mp hf _ h)
  | some d =>
    have hd := List.mem_of_find?_eq_some hf
    simp only [bitDecls, List.mem_flatMap, List.mem_range, List.mem_map] at hd
    obtain ⟨_, _, _, _, rfl⟩ := hd
    rfl

theorem sup_bit {m j : Nat} (hm : m < D.sets.length) (hj : j < bitsOf (setSize D m)) (k : Nat) :
    (envAt (soften (sup D).1.soft) k).predicates (bitName (m + 1) j) = some ["ve__reading"] := by
  rw [envAt_other k (bit_not_layer hh _ _) (bitName_not_decision _ _), sup_E]
  exact choiceEnv_bit hm hj

omit hh in
theorem sup_here {m : Nat} (hm : m < D.sets.length) (k : Nat) :
    (envAt (soften (sup D).1.soft) k).constants "ve__here" = some "ve__reading" := by
  rw [envAt_consts0, soften_E, envPrime_constants, sup_E]
  unfold choiceEnv
  rw [sets_ne_nil hm]
  simp

end Sup

/-! ## The slot is typed over the base vocabulary of `sup D` -/

theorem conj_wf {E : VE.Environment} {Γ : List String} : ∀ (l : List VE.Formula), (∀ a ∈ l, a.WellFormed E Γ) →
    (conj l).WellFormed E Γ
  | [], _ => trivial
  | [a], h => h a (by simp)
  | a :: b :: l, h => ⟨h a (by simp), conj_wf (b :: l) (fun x hx => h x (List.mem_cons_of_mem _ hx))⟩

theorem disj_wf {E : VE.Environment} {Γ : List String} : ∀ (l : List VE.Formula), (∀ a ∈ l, a.WellFormed E Γ) →
    (disj l).WellFormed E Γ
  | [], _ => trivial
  | [a], h => h a (by simp)
  | a :: b :: l, h => ⟨h a (by simp), disj_wf (b :: l) (fun x hx => h x (List.mem_cons_of_mem _ hx))⟩

section SupSlot
variable {D : Doc} (hh : Hyps D)
include hh

theorem pattern_wf {m : Nat} (hm : m < D.sets.length) (i : Nat) (Γ : List String) :
    (pattern (m + 1) (setSize D m) i).WellFormed (envAt (soften (sup D).1.soft) 0) Γ := by
  apply conj_wf
  intro a ha
  obtain ⟨j, hj, rfl⟩ := List.mem_map.mp ha
  rw [List.mem_range] at hj
  have hl : (VE.Formula.unary (bitName (m + 1) j) here).WellFormed (envAt (soften (sup D).1.soft) 0) Γ :=
    ⟨"ve__reading", sup_bit hh hm hj 0, by simp [here, VE.Term.sortOf, sup_here hm 0]⟩
  unfold lit
  split
  · exact hl
  · exact hl

theorem choiceAtom_wf (s : String) (i : Nat) (Γ : List String) :
    (choiceAtom D s i).WellFormed (envAt (soften (sup D).1.soft) 0) Γ := by
  unfold choiceAtom
  split
  · rename_i m hf
    split
    · exact pattern_wf hh (findIdx_set hf).1 i Γ
    · trivial
  · trivial

theorem atomAt_wf (o : Nat × Nat) (Γ : List String) :
    (atomAt D o).WellFormed (envAt (soften (sup D).1.soft) 0) Γ := choiceAtom_wf hh _ _ Γ

end SupSlot

end VE.Readings

namespace VE.Readings
open VE.Norms (envAt size Arity atom bindAll)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft decisions decisionNames envPrime)
open VE.Rights (RightsDoc correlate limPremises)
open VE.Compose (SlotWellFormed Labelled)

/-- On a document without rights material, every generated key is a decision predicate with its sorts. -/
theorem genKeys_decision {X : RightsDoc} (h : noRights X = true) {g : GenKey × String × List String}
    (hg : g ∈ genKeys X) : (g.2.1, g.2.2) ∈ decisions (correlate X) := by
  obtain ⟨_, hl, hb, hs⟩ := noRights_parts h
  have hlines : VE.Rights.linesOf X = [] := by simp [VE.Rights.linesOf, hs, VE.Rights.linesAux]
  have hk : keyedNodes X = X.soft.T.nodes.map (fun N => (N, N.name, none)) := by
    simp [keyedNodes, hlines, VE.Rights.barNodes_nil X hb]
  have hc : (correlate X).T.nodes = X.soft.T.nodes := by rw [(correlate_noRights X h).1]
  simp only [genKeys, hk, VE.Rights.limKeys_nil X hl, VE.Rights.condKeys_nil X hl, hb, List.mem_append,
    List.mem_map, List.mem_filter, List.mem_flatMap, List.map_nil, List.not_mem_nil, if_true, or_false] at hg
  apply mem_decisions.mpr
  rcases hg with ((⟨⟨N, n, b⟩, ⟨⟨M, hM, he⟩, hmode⟩, rfl⟩ | ⟨⟨N, n, b⟩, ⟨M, hM, he⟩, π, hπ, rfl⟩) |
    ⟨x, hx, rfl⟩)
  · simp only [Prod.mk.injEq] at he
    obtain ⟨rfl, rfl, rfl⟩ := he
    exact Or.inl ⟨M, hc ▸ hM, by simpa using hmode, rfl⟩
  · simp only [Prod.mk.injEq] at he
    obtain ⟨rfl, rfl, rfl⟩ := he
    exact Or.inr (Or.inl ⟨M, hc ▸ hM, π, hπ, rfl⟩)
  · exact Or.inr (Or.inr ⟨x.1, x.2.1, x.2.2, hx, rfl⟩)

theorem quietFormula_wf {D : Doc} (hh : Hyps D) {g : GenKey × String × List String}
    (hg : g ∈ genKeys (sup D).1) : (quietFormula D g).WellFormed (envAt (soften (sup D).1.soft) 0) [] := by
  have hd := genKeys_decision hh.noRights hg
  rw [sup_correlate hh] at hd
  have hw := sup_wfSoft hh
  unfold quietFormula
  refine VE.Norms.bindAll_wellFormed (E := envAt (soften (sup D).1.soft) 0)
    (fun s hs => decision_sorts hw hd s hs) [] _ ?_
  rw [List.append_nil]
  refine ⟨?_, disj_wf _ (fun a ha => ?_)⟩
  · have hp := envAt_decision hw 0 hd
    simp only at hp
    match hs : g.2.2, hp with
    | [s], hp => exact VE.Norms.atom_wellFormed (by simp [Arity]) hp
    | [s, t], hp => exact VE.Norms.atom_wellFormed (by simp [Arity]) hp
    | [], _ => trivial
    | _ :: _ :: _ :: _, _ => trivial
  · obtain ⟨o, _, rfl⟩ := List.mem_map.mp ha
    exact conj_wf _ (fun b hb => by
      obtain ⟨x, _, rfl⟩ := List.mem_map.mp hb
      exact atomAt_wf hh x _)

theorem slot_formula_wf {D : Doc} (hh : Hyps D) {a : VE.Formula} (ha : a ∈ choicePremises D) :
    a.WellFormed (envAt (soften (sup D).1.soft) 0) [] := by
  simp only [choicePremises, choiceLabelled, Labelled.formulas, List.map_append, List.mem_append, List.mem_map] at ha
  rcases ha with ((((⟨⟨l, f⟩, hl, rfl⟩ | ⟨⟨l, f⟩, hl, rfl⟩) | ⟨⟨l, f⟩, hl, rfl⟩) | ⟨⟨l, f⟩, hl, rfl⟩) |
    ⟨⟨l, f⟩, hl, rfl⟩)
  · simp only [onePremises, List.mem_filterMap, List.mem_range] at hl
    obtain ⟨m, hm, hb⟩ := hl
    rw [List.getElem?_eq_getElem hm] at hb
    simp only [Option.bind_some] at hb
    split at hb
    · cases hb
    · cases hb
      apply conj_wf
      intro b hb
      obtain ⟨i, _, rfl⟩ := List.mem_map.mp hb
      have := pattern_wf hh hm i []
      rw [setSize_eq hm] at this
      exact this
  · simp only [quietOwn, List.mem_flatMap, List.mem_filterMap, List.mem_range] at hl
    obtain ⟨m, _, R, _, i, _, hb⟩ := hl
    split at hb
    · cases hb
    · cases hb
      apply conj_wf
      intro b hb
      obtain ⟨g, hg, rfl⟩ := List.mem_map.mp hb
      exact quietFormula_wf hh (List.mem_filter.mp hg).1
  · simp only [quietShared, List.mem_map, List.mem_filter] at hl
    obtain ⟨g, ⟨hg, _⟩, he⟩ := hl
    simp only [Prod.mk.injEq] at he
    rw [← he.2]
    exact quietFormula_wf hh hg
  · simp only [couplingPremises, List.mem_filterMap] at hl
    obtain ⟨K, _, hb⟩ := hl
    split at hb
    · cases hb
    · cases hb
      apply conj_wf
      intro b hb
      simp only [List.mem_flatMap] at hb
      obtain ⟨⟨x, y⟩, _, hb⟩ := hb
      split at hb
      · simp only [List.mem_flatMap, List.mem_range, List.mem_filterMap] at hb
        obtain ⟨i, _, j, _, hb⟩ := hb
        split at hb
        · cases hb
          exact ⟨choiceAtom_wf hh _ _ [], choiceAtom_wf hh _ _ []⟩
        · cases hb
      · cases hb
  · simp only [narrowingPremises, List.mem_filterMap] at hl
    obtain ⟨N, _, hb⟩ := hl
    cases hf : inForce D N with
    | none => rw [hf] at hb; cases hb
    | some R =>
      rw [hf] at hb
      simp only [Option.bind_some] at hb
      split at hb
      · cases hb
      · cases hb
        apply conj_wf
        intro b hb
        obtain ⟨i, _, rfl⟩ := List.mem_map.mp hb
        exact choiceAtom_wf hh _ _ []

/-- 1.6: every premise of the slot, with any assumed atoms, is a closed formula over the base vocabulary of
    `sup D`'s soft route. -/
theorem slot_wellFormed (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome) :
    SlotWellFormed (correlate (sup D).1) (slotUnder D A) := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hlim : limPremises (sup D).1 = [] := (correlate_noRights _ hh.noRights).2
  rw [sup_correlate hh]
  intro a ha
  simp only [slotUnder, slotP, slotLabelled, Labelled.formulas, List.map_append, List.mem_append] at ha
  rcases ha with ((ha | ha) | ha) | ha
  · have : a ∈ limPremises (sup D).1 := ha
    rw [hlim] at this; cases this
  · exact slot_formula_wf hh ha
  · simp [gatedRel] at ha
  · obtain ⟨x, _, rfl⟩ := List.mem_map.mp ha
    exact choiceAtom_wf hh _ _ []

end VE.Readings
