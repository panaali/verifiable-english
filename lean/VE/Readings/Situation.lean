import VE.Readings.ChoiceTyped
import VE.Readings.Assertions

/-! The situations of `sup D` and of a reading's document agree (docs/spec/composition-s2.md 4.3, 8.4
`superpose_situation`).

`canon D B` reads a layer symbol at any tuple as its expanded formula over `B`; at a tuple of the symbol's arity,
typed or not, that is the symbol's meaning over `canon D B` itself (`canon_meaning`, the substitution lemma for
defined valuations). On a base of `sup D` that encodes a choice, the expansion of `sup D` read through the name map
and the expansion of the choice's document over the pulled base then agree on every predicate of the choice's
complete vocabulary at every tuple of its arity (`pull_canon`): a base predicate by the name map, and a layer
symbol by induction over the stratum order, because the two meanings agree on the outcome (`superpose_faithful`'s
simulation) and the lower symbols. Every regulated value, every sentence over the shared vocabulary and every
assertion in force then agree. -/
namespace VE.Readings
open VE.Norms (envAt size preds anyF atom Arity Regulated tupleVal expTable substWith Sat)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft decisions decisionNames envPrime ValueSoft canon exceptedName
  offName)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP)
universe u

/-! ## The canonical interpretation at tuples of the symbol's arity -/

section Canon
variable {Dd : VE.Norms.Doc} (hv : VE.Norms.Valid Dd) (S : VE.Structure.{u})
  (hcd : ∀ c s, Dd.E.constants c = some s → ∃ v, S.constant c = some v)
include hv hcd

omit hcd in
omit hv in
theorem canon_term (ρ : VE.Valuation S) (t : VE.Term) : t.denote (canon Dd S) ρ = t.denote S ρ := by
  cases t <;> rfl

omit hv in
theorem term_defined {j : Nat} {Γ : List String} {ρ : VE.Valuation S} (hl : Γ.length ≤ ρ.length) {t : VE.Term}
    {s : String} (ht : t.sortOf (envAt Dd j) Γ = some s) : ∃ v, t.denote S ρ = some v := by
  cases t with
  | var i =>
    have hi : i < Γ.length := (List.getElem?_eq_some_iff.mp ht).1
    exact ⟨ρ[i]'(by omega), by simp [VE.Term.denote, List.getElem?_eq_getElem (show i < ρ.length by omega)]⟩
  | const c =>
    obtain ⟨v, hv⟩ := hcd c s ht
    exact ⟨v, hv⟩

/-- Substitution of the first `j` layer symbols, read on `S`, is the formula read on `canon Dd S`, under any
    valuation that defines the formula's variables. -/
theorem substWith_canon (j : Nat) : ∀ (φ : VE.Formula) (Γ : List String) (ρ : VE.Valuation S),
    φ.WellFormed (envAt Dd j) Γ → Γ.length ≤ ρ.length →
      ((substWith (expTable Dd.T j) φ).denote S ρ ↔ φ.denote (canon Dd S) ρ) := by
  have htable : ∀ p F, expTable Dd.T j p = some F → expTable Dd.T (size Dd) p = some F := by
    intro p F hF
    obtain ⟨j', q, hj', hq, rfl, rfl⟩ := VE.Norms.expTable_some Dd.T j p F hF
    exact VE.Norms.expTable_at hv _ j' q (List.getElem?_eq_some_iff.mp hq).1 hq
  have hnone : ∀ p ss, (envAt Dd j).predicates p = some ss → expTable Dd.T j p = none →
      expTable Dd.T (size Dd) p = none := by
    intro p ss hp hF
    apply VE.Norms.expTable_none
    rw [List.take_of_length_le (by simp [size, VE.Norms.layerNames])]
    intro hl
    obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hl
    obtain ⟨q', hq', rfl⟩ : ∃ q', (VE.Norms.syms Dd.T)[i]? = some q' ∧ q'.name = p := by
      simp only [VE.Norms.layerNames, List.getElem?_map, Option.map_eq_some_iff] at hi
      exact hi
    by_cases hij : i < j
    · rw [VE.Norms.expTable_at hv j i q' hij hq'] at hF; cases hF
    · rw [VE.Norms.envAt_later hv hq' (Nat.le_of_not_lt hij)] at hp; cases hp
  intro φ
  induction φ with
  | top | bottom => intros; exact Iff.rfl
  | unary p t =>
    intro Γ ρ ⟨s, hp, ht⟩ hl
    obtain ⟨v, hvt⟩ := term_defined S hcd hl ht
    simp only [substWith]
    split
    · rename_i F hF
      obtain ⟨ss, hss, hFw⟩ := VE.Norms.expTable_wellFormed hv j p F hF
      rw [hp] at hss; cases hss
      rw [VE.Norms.inst_denote S _ F [s] [t] ρ [v] hFw rfl ⟨rfl, fun i h₁ _ => by
        match i, h₁ with | 0, _ => exact hvt⟩]
      simp only [VE.Formula.denote, term_relation_congr]
      constructor
      · intro h; exact ⟨v, hvt, by simp only [canon, htable p F hF]; exact h⟩
      · rintro ⟨w, hw, h⟩
        rw [canon_term, hvt] at hw; cases hw
        simp only [canon, htable p F hF] at h
        exact h
    · rename_i hF
      simp only [VE.Formula.denote, term_relation_congr, canon, hnone p _ hp hF]
  | binary p t w =>
    intro Γ ρ ⟨s, s', hp, ht, hw⟩ hl
    obtain ⟨v, hvt⟩ := term_defined S hcd hl ht
    obtain ⟨v', hvw⟩ := term_defined S hcd hl hw
    simp only [substWith]
    split
    · rename_i F hF
      obtain ⟨ss, hss, hFw⟩ := VE.Norms.expTable_wellFormed hv j p F hF
      rw [hp] at hss; cases hss
      rw [VE.Norms.inst_denote S _ F [s', s] [w, t] ρ [v', v] hFw rfl ⟨rfl, fun i h₁ _ => by
        match i, h₁ with
        | 0, _ => exact hvw
        | 1, _ => exact hvt⟩]
      simp only [VE.Formula.denote, term_relation_congr]
      constructor
      · intro h
        refine ⟨v, v', hvt, hvw, ?_⟩
        simp only [canon, htable p F hF, tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append,
          List.cons_append]
        exact h
      · rintro ⟨a, b, ha, hb, h⟩
        rw [canon_term, hvt] at ha; rw [canon_term, hvw] at hb; cases ha; cases hb
        simp only [canon, htable p F hF, tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append,
          List.cons_append] at h
        exact h
    · rename_i hF
      simp only [VE.Formula.denote, term_relation_congr, canon, hnone p _ hp hF]
  | eq t w => intros; exact Iff.rfl
  | not a ih => intro Γ ρ hw hl; simp only [substWith, VE.Formula.denote]; rw [ih Γ ρ hw hl]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ ρ hw hl
    simp only [substWith, VE.Formula.denote]; rw [ia Γ ρ hw.1 hl, ib Γ ρ hw.2 hl]
  | all s a ih =>
    intro Γ ρ hw hl
    simp only [substWith, VE.Formula.denote]
    exact forall_congr' fun v => imp_congr_right fun _ => ih (s :: Γ) (v :: ρ) hw.2 (by simp; omega)
  | ex s a ih =>
    intro Γ ρ hw hl
    simp only [substWith, VE.Formula.denote]
    exact exists_congr fun v => and_congr_right fun _ => ih (s :: Γ) (v :: ρ) hw.2 (by simp; omega)

/-- At a tuple of its arity, a layer symbol of the canonical interpretation is its meaning there. -/
theorem canon_meaning {j : Nat} {q : VE.Norms.Sym} (hq : (VE.Norms.syms Dd.T)[j]? = some q) (ws : List S.Carrier)
    (hws : ws.length = q.sorts.length) :
    (canon Dd S).relation q.name ws ↔ (q.meaning Dd.T).denote (canon Dd S) (tupleVal ws) := by
  have hj : j < size Dd := (List.getElem?_eq_some_iff.mp hq).1
  simp only [canon, VE.Norms.expTable_at hv (size Dd) j q hj hq]
  exact substWith_canon hv S hcd j _ q.sorts.reverse _ (VE.Norms.meaning_wellFormed hv hq)
    (by simp [tupleVal, hws])

end Canon

/-! ## The layer symbols and the name map -/

theorem syms_transfer {T T' : VE.Norms.Tree} (hr : T.regulated = T'.regulated) (hd : T.definitions = T'.definitions)
    {o : List String} (ho : VE.Route.dependencyOrder (VE.Norms.stratumNodes T') = .ok o) {q : VE.Norms.Sym}
    (hq : q ∈ VE.Norms.syms T) : q ∈ VE.Norms.syms T' := by
  obtain ⟨x, _, hx⟩ := List.mem_filterMap.mp hq
  have hlook : VE.Norms.lookupSym T' x = VE.Norms.lookupSym T x := by
    simp only [VE.Norms.lookupSym, hr, hd]
  rw [← hlook] at hx
  exact syms_mem_of_node ho (node_of_lookupSym hx) hx

section Agree
variable {D : Doc} (hh : Hyps D)
include hh

theorem sup_valid : VE.Norms.Valid (soften (sup D).1.soft) :=
  VE.Norms.valid_of_wellFormed _ (sup_softValid hh).wf

theorem sup_choice_sym (c : Choice) {q : VE.Norms.Sym} (hq : q ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T) :
    q ∈ VE.Norms.syms (soften (sup D).1.soft).T := by
  obtain ⟨o, ho⟩ := (sup_valid hh).stratum
  exact syms_transfer (regs_eq c).symm (defs_eq c).symm ho hq

theorem choice_sup_sym {c : Choice} (hc : Compatible D c) {q : VE.Norms.Sym}
    (hq : q ∈ VE.Norms.syms (soften (sup D).1.soft).T) : q ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T := by
  obtain ⟨o, ho⟩ := (choice_valid hh hc).stratum
  exact syms_transfer (regs_eq c) (defs_eq c) ho hq

theorem layer_iff {c : Choice} (hc : Compatible D c) (p : String) :
    p ∈ VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T ↔ p ∈ VE.Norms.layerNames (soften (sup D).1.soft).T := by
  simp only [VE.Norms.layerNames, List.mem_map]
  constructor
  · rintro ⟨q, hq, rfl⟩; exact ⟨q, sup_choice_sym hh c hq, rfl⟩
  · rintro ⟨q, hq, rfl⟩; exact ⟨q, choice_sup_sym hh hc hq, rfl⟩

theorem nameMap_cases (c : Choice) (p : String) :
    nameMap D c p = p ∨ nameMap D c p ∈ decisionNames (sup D).1.soft := by
  unfold nameMap
  split
  · rename_i g _
    cases hx : (genKeys (sup D).1).find? (·.1 == qualifyKey D c g.1) with
    | none => left; simp
    | some g' =>
      right
      simp only [Option.map_some, Option.getD_some]
      have := genKeys_decision hh.noRights (List.mem_of_find?_eq_some hx)
      rw [sup_correlate hh] at this
      exact List.mem_map.mpr ⟨_, this, rfl⟩
  · left; rfl

theorem nameMap_nonlayer {c : Choice} (hc : Compatible D c) {p : String}
    (hp : p ∉ VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T) :
    nameMap D c p ∉ VE.Norms.layerNames (soften (sup D).1.soft).T := by
  rcases nameMap_cases hh c p with h | h
  · rw [h]; exact fun hx => hp ((layer_iff hh hc p).mpr hx)
  · exact fun hx => layer_not_decision (sup_wfSoft hh) hx h

theorem free_def_typed {d : VE.Norms.Definition} (hd : d ∈ (free D).1.soft.T.definitions) :
    d.body.check (envPrime (free D).1.soft) d.args.reverse = true := by
  have hv := free_soft_valid hh
  have hck := (VE.NormDefaults.wellFormed_iff _).mp hv.wf
  exact (hck.1.2.2.2.2.1 d hd).2.2.2.2

theorem free_envPrime_sub (c : Choice) {p : String} {ss : List String}
    (hp : (envPrime (free D).1.soft).predicates p = some ss) :
    (envPrime (choiceDoc D c).1.soft).predicates p = some ss := by
  by_cases hpd : p ∈ decisionNames (free D).1.soft
  · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hpd
    rw [choice_envPrime_decision hh c (free_decisions_in hx)]
    rw [envPrime_decision (free_wfSoft hh) hx] at hp; exact hp
  · have hF : (envPrime (free D).1.soft).predicates p = D.frame.soft.E.predicates p := by
      rw [envPrime_not_decision hpd, free_E]
    rw [hF] at hp
    rw [choice_envPrime_frame hh c (by rw [hp]; simp)]; exact hp

theorem fmap_free (c : Choice) {N : SoftNode} (hN : N ∈ (free D).1.soft.T.nodes) : (fmap D c N).name = N.name := by
  rcases mem_build_nodes hN with hf | ⟨u, cs, hu⟩ | ⟨R, a, _, hpa, _⟩
  · rw [fmap_frame hh c hf]
  · rw [fmap_fixed hh c hu]; rfl
  · cases hpa

/-- The name map is the identity on the shared vocabulary. -/
theorem nameMap_shared (c : Choice) {p : String} (hp : (envPrime (free D).1.soft).predicates p ≠ none) :
    nameMap D c p = p := by
  by_cases hpd : p ∈ decisionNames (free D).1.soft
  · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hpd
    rcases mem_decisions.mp hx with ⟨N, hN, hd, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, _, rfl⟩
    · show nameMap D c (exceptedName N) = exceptedName N
      rw [nameMap_excepted hh c (free_nodes_in hN) hd]
      simp only [exceptedName, fmap_free hh c hN]
    · show nameMap D c (offName N π) = offName N π
      rw [nameMap_off hh c (free_nodes_in hN) hπ]
      simp only [offName, fmap_free hh c hN]
    · exact nameMap_outweighs hh c a L H
  · rw [envPrime_not_decision hpd, free_E] at hp
    exact nameMap_frame hh c hp

theorem frame_const_sup {x s : String} (h : D.frame.soft.E.constants x = some s) :
    (soften (sup D).1.soft).E.constants x = some s := by
  rw [soften_E, envPrime_constants, sup_E]
  unfold choiceEnv
  split
  · exact h
  · show (if x == "ve__here" then some "ve__reading" else D.frame.soft.E.constants x) = some s
    have hhere := (sharedEnv_noChoice hh.wf hh.ready).2.1
    rw [sharedEnv_constants] at hhere
    have hx : (x == "ve__here") = false := by
      cases hx : x == "ve__here" with
      | false => rfl
      | true => rw [beq_iff_eq.mp hx, hhere] at h; cases h
    rw [hx]; exact h

theorem choiceEnvFull_eq (c : Choice) (p : String) :
    (choiceEnvFull D c).predicates p = (envPrime (choiceDoc D c).1.soft).predicates p := by
  unfold choiceEnvFull
  rw [choice_correlate hh c]
  have hd : (VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T).drop
      (VE.Norms.size (soften (choiceDoc D c).1.soft)) = [] := by
    simp [VE.Norms.layerNames, VE.Norms.size]
  simp only [VE.Norms.envAt, hd, VE.Norms.hide, List.not_mem_nil, if_false]
  rfl

/-- A layer symbol of a choice's document is declared by the frame. -/
theorem choice_sym_frame (c : Choice) {q : VE.Norms.Sym} (hq : q ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T) :
    D.frame.soft.E.predicates q.name = some q.sorts := by
  have hqF := choice_sym_free hh hq
  have hvF := VE.Norms.valid_of_wellFormed _ (free_soft_valid hh).wf
  obtain ⟨hd, _, _⟩ := hvF.decl q hqF
  have hnd := layer_not_decision (free_wfSoft hh) (List.mem_map.mpr ⟨q, hqF, rfl⟩)
  have : (envPrime (free D).1.soft).predicates q.name = some q.sorts := hd
  rwa [envPrime_not_decision hnd, free_E] at this

end Agree

theorem freeJunk_le (keep : String → Bool) :
    ∀ l : List Item, (l.map (buildJunk keep (fun _ => none))).sum ≤ (l.map supItemJunk).sum
  | [] => by simp
  | it :: l => by
    simp only [List.map_cons, List.sum_cons]
    have := freeJunk_le keep l
    suffices buildJunk keep (fun _ => none) it ≤ supItemJunk it by omega
    cases it with
    | fixed u c' cs => simp only [buildJunk, supItemJunk]; split <;> omega
    | bar u b => simp only [buildJunk, supItemJunk]; split <;> omega
    | set R => simp [buildJunk]

theorem free_noRights (D : Doc) (h : noRights (sup D).1 = true) : noRights (free D).1 = true := by
  rw [noRights_junk] at h ⊢
  have hx := (sup_shape D).junk
  have hy := (build_shape D (fun u => (attached D u).isEmpty) (fun _ => none)).junk
  have := freeJunk_le (fun u => (attached D u).isEmpty) D.items
  rw [supFrame_junk] at hx
  unfold free
  omega

theorem envAt_sub {Dd : VE.Norms.Doc} {k : Nat} {p : String} {ss : List String}
    (hp : (envAt Dd k).predicates p = some ss) : Dd.E.predicates p = some ss := by
  simp only [envAt, VE.Norms.hide] at hp
  split at hp
  · cases hp
  · exact hp

theorem sharedEnv_sub {D : Doc} (hh : Hyps D) {p : String} {ss : List String}
    (hp : (sharedEnv D).predicates p = some ss) : (envPrime (free D).1.soft).predicates p = some ss := by
  unfold sharedEnv at hp
  rw [(correlate_noRights _ (free_noRights D hh.noRights)).1] at hp
  exact envAt_sub hp

/-! ## Lemma K: the expansion of `sup D`, pulled, is the expansion of the choice's document over the pulled base -/

section K
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B : VE.Structure.{u})
  (hcB : ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, B.constant x = some v)
  (he : Encodes D c B)
include hh

include he in
theorem encodes_canon : Encodes D c (canon (soften (sup D).1.soft) B) := by
  intro R hR i hi
  rw [VE.SoftNorms.canon_base B _ [] (choiceAtom_wf hh R.id i []) []]
  exact he R hR i hi

include hc in
theorem pull_canon_off {p : String} (hp : p ∉ VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T)
    (ws : List B.Carrier) :
    (pull D c (canon (soften (sup D).1.soft) B)).relation p ws ↔
      (canon (soften (choiceDoc D c).1.soft) (pull D c B)).relation p ws := by
  rw [VE.SoftNorms.canon_off (pull D c B) hp]
  show ((choiceEnvFull D c).predicates p ≠ none ∧ (canon (soften (sup D).1.soft) B).relation (nameMap D c p) ws) ↔
    ((choiceEnvFull D c).predicates p ≠ none ∧ B.relation (nameMap D c p) ws)
  rw [VE.SoftNorms.canon_off B (nameMap_nonlayer hh hc hp)]

include hc hcB he in
theorem pull_canon_layer : ∀ (j : Nat) (q : VE.Norms.Sym), (VE.Norms.syms (soften (choiceDoc D c).1.soft).T)[j]? = some q →
    ∀ ws : List B.Carrier, ws.length = q.sorts.length →
      ((pull D c (canon (soften (sup D).1.soft) B)).relation q.name ws ↔
        (canon (soften (choiceDoc D c).1.soft) (pull D c B)).relation q.name ws) := by
  intro j
  induction j using Nat.strongRecOn with
  | ind j ih =>
  intro q hq ws hws
  have hvY := choice_valid hh hc
  have hvX := sup_valid hh
  have hqY : q ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T := List.mem_of_getElem? hq
  obtain ⟨j', hj'⟩ := VE.Norms.mem_syms_index (sup_choice_sym hh c hqY)
  have hfr := choice_sym_frame hh c hqY
  have hcdX : ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, B.constant x = some v := hcB
  have hcdY : ∀ x s, (soften (choiceDoc D c).1.soft).E.constants x = some s →
      ∃ v, (pull D c B).constant x = some v := by
    intro x s hx
    rw [soften_E, envPrime_constants, choice_E c] at hx
    exact hcB x s (frame_const_sup hh hx)
  have hfull : (choiceEnvFull D c).predicates q.name ≠ none := choiceEnvFull_frame hh c (by rw [hfr]; simp)
  have hL : (pull D c (canon (soften (sup D).1.soft) B)).relation q.name ws ↔
      (q.meaning (soften (sup D).1.soft).T).denote (canon (soften (sup D).1.soft) B) (tupleVal ws) := by
    show ((choiceEnvFull D c).predicates q.name ≠ none ∧
      (canon (soften (sup D).1.soft) B).relation (nameMap D c q.name) ws) ↔ _
    rw [nameMap_frame hh c (by rw [hfr]; simp), canon_meaning hvX B hcdX hj' ws hws]
    exact ⟨fun h => h.2, fun h => ⟨hfull, h⟩⟩
  rw [hL, canon_meaning hvY (pull D c B) hcdY hq ws hws]
  have hM : (q.meaning (soften (sup D).1.soft).T).denote (canon (soften (sup D).1.soft) B) (tupleVal ws) ↔
      (q.meaning (soften (choiceDoc D c).1.soft).T).denote (pull D c (canon (soften (sup D).1.soft) B))
        (tupleVal ws) := by
    cases q with
    | reg r =>
      have hs := faithful_sim hh hc (canon (soften (sup D).1.soft) B) (encodes_canon hh B he) (tupleVal ws)
      have h1 : ∀ sign, VE.SoftNorms.DecidesSoftD (sup D).1.soft (canon (soften (sup D).1.soft) B) (tupleVal ws)
          r.name sign ↔ VE.SoftNorms.DecidesSoftD (choiceDoc D c).1.soft
            (pull D c (canon (soften (sup D).1.soft) B)) (tupleVal ws) r.name sign :=
        fun sign => sim_decides hs r.name sign
      simp only [VE.Norms.Sym.meaning]
      rw [VE.Norms.outcome_denote, VE.Norms.outcome_denote]
      simp only [VE.Norms.pos, VE.Norms.neg, VE.Norms.decides_denote, VE.SoftNorms.decidesD_soften, h1]
    | defn d =>
      have hd : d ∈ (free D).1.soft.T.definitions := by
        rw [free_defs, ← choice_defs c]; exact VE.Norms.mem_syms_defn hqY
      simp only [VE.Norms.Sym.meaning]
      apply denote_relation_congr (envPrime (free D).1.soft) _ _ _ d.body d.args.reverse _ (free_def_typed hh hd)
      intro p ss hp vs _
      show _ ↔ ((choiceEnvFull D c).predicates p ≠ none ∧ _)
      rw [nameMap_shared hh c (by rw [hp]; simp), choiceEnvFull_eq hh c, free_envPrime_sub hh c hp]
      exact ⟨fun h => ⟨by simp, h⟩, fun h => h.2⟩
  rw [hM]
  apply denote_relation_congr (VE.Norms.envAt (soften (choiceDoc D c).1.soft) j) _ _ _ _ q.sorts.reverse _
    ((VE.check_iff_wellFormed _ _ _).mpr (VE.Norms.meaning_wellFormed hvY hq))
  intro p ss hp vs hvs
  by_cases hpl : p ∈ VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T
  · obtain ⟨q', hq', rfl⟩ := List.mem_map.mp hpl
    obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index hq'
    have hkj : k < j := by
      rcases Nat.lt_or_ge k j with h | h
      · exact h
      · rw [VE.Norms.envAt_later hvY hk h] at hp; cases hp
    rw [VE.Norms.envAt_earlier hvY hk hkj] at hp
    cases hp
    exact ih k hkj q' hk vs hvs
  · exact pull_canon_off hh hc B hpl vs

include hc hcB he in
/-- Lemma K over the complete vocabulary of the choice's document. -/
theorem pull_canon {p : String} {ss : List String} (hp : (envPrime (choiceDoc D c).1.soft).predicates p = some ss)
    (ws : List B.Carrier) (hws : ws.length = ss.length) :
    (pull D c (canon (soften (sup D).1.soft) B)).relation p ws ↔
      (canon (soften (choiceDoc D c).1.soft) (pull D c B)).relation p ws := by
  by_cases hpl : p ∈ VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T
  · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hpl
    obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index hq
    rw [(choice_decl hh hq).1] at hp
    cases hp
    exact pull_canon_layer hh hc B hcB he k q hk ws hws
  · exact pull_canon_off hh hc B hpl ws

include hc hcB he in
theorem decides_pull_canon {r : Regulated} (hr : r ∈ (choiceDoc D c).1.soft.T.regulated) (ρ : VE.Valuation B)
    (sign : Bool) :
    VE.SoftNorms.DecidesSoftD (choiceDoc D c).1.soft (pull D c (canon (soften (sup D).1.soft) B)) ρ r.name sign ↔
      VE.SoftNorms.DecidesSoftD (choiceDoc D c).1.soft (canon (soften (choiceDoc D c).1.soft) (pull D c B)) ρ
        r.name sign := by
  have hvY := choice_valid hh hc
  have hT := VE.Norms.rulesTyped_of_valid hvY (VE.Norms.index_before hvY hr)
  rw [← VE.SoftNorms.decidesD_soften, ← VE.SoftNorms.decidesD_soften, ← VE.Norms.decides_denote,
    ← VE.Norms.decides_denote]
  exact denote_relation_congr _ (pull D c (canon (soften (sup D).1.soft) B))
    (canon (soften (choiceDoc D c).1.soft) (pull D c B)).relation
    (fun p ss hp vs hvs => pull_canon hh hc B hcB he (envAt_sub hp) vs hvs) _ _ ρ
    ((VE.check_iff_wellFormed _ _ _).mpr (VE.Norms.decides_wellFormed hT sign))

include hc hcB he in
/-- A sentence over the shared vocabulary reads the two expansions alike. -/
theorem shared_canon (φ : VE.Formula) (hφ : φ.WellFormed (sharedEnv D) []) :
    φ.denote (canon (soften (sup D).1.soft) B) [] ↔
      φ.denote (canon (soften (choiceDoc D c).1.soft) (pull D c B)) [] := by
  have hck := (VE.check_iff_wellFormed _ _ _).mpr hφ
  have h1 : φ.denote (canon (soften (sup D).1.soft) B) [] ↔ φ.denote (pull D c (canon (soften (sup D).1.soft) B)) [] := by
    apply denote_relation_congr (sharedEnv D) _ _ _ φ [] [] hck
    intro p ss hp vs _
    have h := sharedEnv_sub hh hp
    show _ ↔ ((choiceEnvFull D c).predicates p ≠ none ∧ _)
    rw [nameMap_shared hh c (by rw [h]; simp), choiceEnvFull_eq hh c, free_envPrime_sub hh c h]
    exact ⟨fun h => ⟨by simp, h⟩, fun h => h.2⟩
  have h2 : φ.denote (pull D c (canon (soften (sup D).1.soft) B)) [] ↔
      φ.denote (canon (soften (choiceDoc D c).1.soft) (pull D c B)) [] :=
    denote_relation_congr (sharedEnv D) (pull D c (canon (soften (sup D).1.soft) B))
      (canon (soften (choiceDoc D c).1.soft) (pull D c B)).relation (fun p ss hp vs hvs =>
      pull_canon hh hc B hcB he (free_envPrime_sub hh c (sharedEnv_sub hh hp)) vs hvs) φ [] [] hck
  exact h1.trans h2

include hc hcB he in
theorem assertions_canon :
    Sat (canon (soften (sup D).1.soft) B) (sup D).2 ↔
      Sat (canon (soften (choiceDoc D c).1.soft) (pull D c B)) (choiceDoc D c).2 := by
  have hcomp : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hnd : (c.map (·.1)).Nodup := by rw [complete_map hcomp]; exact supReady_nodup hh.ready
  have hsh := asserted_shared D hh.wf hh.ready c hc
  have hgate : ∀ m (hm : m < D.sets.length) i, i < D.sets[m].candidates.length →
      ((pattern (m + 1) (setSize D m) i).denote (canon (soften (sup D).1.soft) B) [] ↔
        c.index D.sets[m].id = some i) := by
    intro m hm i hi
    rw [← choiceAtom_eq (findIdx_of_nodup (supReady_nodup hh.ready) hm) (by rw [setSize_eq hm]; exact hi),
      VE.SoftNorms.canon_base B _ [] (choiceAtom_wf hh _ i []) [], he _ (List.getElem_mem hm) i hi]
    exact ⟨fun hx => index_of_mem hnd hx, mem_of_index⟩
  constructor
  · intro hX a ha
    have ha' := ha
    rw [choiceDoc, build_snd] at ha'
    obtain ⟨it, hit, ha'⟩ := List.mem_flatMap.mp ha'
    apply (shared_canon hh hc B hcB he a (hsh a ha)).mp
    cases it with
    | fixed u c' cs =>
      simp only [buildAsserted, if_true] at ha'
      exact hX a ((mem_sup_snd D a).mpr (Or.inl ⟨u, c', cs, hit, ha'⟩))
    | bar u b => simp [buildAsserted] at ha'
    | set R =>
      simp only [buildAsserted] at ha'
      split at ha'
      · rename_i c'' cs heq
        have hc' := asserted_eq ha'
        subst hc'
        simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff, Prod.mk.injEq] at heq
        obtain ⟨cand, ⟨i, hidx, hpick⟩, _, hcc, rfl, _⟩ := heq
        obtain ⟨m, hm, rfl⟩ := mem_sets_getElem (mem_sets.mpr hit)
        have hi : i < D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp hpick).1
        have hmem : (VE.Formula.implies (pattern (m + 1) (setSize D m) i) a) ∈ (sup D).2 :=
          (mem_sup_snd D _).mpr (Or.inr ⟨m, hm, i, cand, _, hpick, hcc, by simp [gateContent, asserted]⟩)
        exact hX _ hmem ((hgate m hm i hi).mpr hidx)
      · cases ha'
  · intro hY a ha
    rcases (mem_sup_snd D a).mp ha with ⟨u, c', cs, hit, ha'⟩ | ⟨m, hm, i, x, c', hx, hxc, ha'⟩
    · have hmem : a ∈ (choiceDoc D c).2 := by
        rw [choiceDoc, build_snd]
        exact List.mem_flatMap.mpr ⟨_, hit, by simp only [buildAsserted, if_true]; exact ha'⟩
      exact (shared_canon hh hc B hcB he a (hsh a hmem)).mpr (hY a hmem)
    · obtain ⟨φ, rfl, rfl⟩ := asserted_gate ha'
      simp only [VE.Formula.denote]
      intro hp
      have hi : i < D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp hx).1
      have hidx := (hgate m hm i hi).mp hp
      have hmem : φ ∈ (choiceDoc D c).2 := by
        rw [choiceDoc, build_snd]
        refine List.mem_flatMap.mpr ⟨_, mem_sets.mp (List.getElem_mem hm), ?_⟩
        simp [buildAsserted, hidx, hx, hxc, asserted]
      exact (shared_canon hh hc B hcB he φ (hsh φ hmem)).mpr (hY φ hmem)

end K

/-! ## `superpose_situation` -/

theorem hyps_constants {D : Doc} (hh : Hyps D) {B : VE.Structure.{u}}
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) :
    ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, B.constant x = some v := by
  intro x s hx
  have h1 := hB.1.1.1.1 x s
  rw [sup_correlate hh] at h1
  obtain ⟨v, hv, _⟩ := h1 hx
  exact ⟨v, hv⟩

/-- The two situations agree: every regulated predicate's value, every sentence over the shared vocabulary, and
    the assertions in force. -/
theorem superpose_situation (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (c : Choice) (hc : Compatible D c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) (he : Encodes D c B) :
    (∀ r ∈ (correlate (choiceDoc D c).1).T.regulated, ∀ vs : List B.Carrier,
       ValueSoft (correlate (sup D).1) r (expand (sup D).1 B) vs =
         ValueSoft (correlate (choiceDoc D c).1) r (expand (choiceDoc D c).1 (pull D c B)) vs) ∧
    (∀ φ : VE.Formula, φ.WellFormed (sharedEnv D) [] →
       (φ.denote (expand (sup D).1 B) [] ↔ φ.denote (expand (choiceDoc D c).1 (pull D c B)) [])) ∧
    (Sat (expand (sup D).1 B) (sup D).2 ↔ Sat (expand (choiceDoc D c).1 (pull D c B)) (choiceDoc D c).2) := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hcB := hyps_constants hh hB
  unfold expand
  rw [sup_correlate hh, choice_correlate hh c]
  refine ⟨fun r hr vs => ?_, fun φ hφ => shared_canon hh hc B hcB he φ hφ, assertions_canon hh hc B hcB he⟩
  have h1 : ValueSoft (choiceDoc D c).1.soft r (pull D c (canon (soften (sup D).1.soft) B)) vs =
      ValueSoft (choiceDoc D c).1.soft r (canon (soften (choiceDoc D c).1.soft) (pull D c B)) vs := by
    unfold ValueSoft
    rw [propext (decides_pull_canon hh hc B hcB he hr _ true), propext (decides_pull_canon hh hc B hcB he hr _ false)]
  exact (value_sim (S := canon (soften (sup D).1.soft) B) r vs (faithful_sim hh hc _ (encodes_canon hh B he) (tupleVal vs))).trans h1

end VE.Readings
