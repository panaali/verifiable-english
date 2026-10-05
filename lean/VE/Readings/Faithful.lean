import VE.Readings.Live
import VE.Readings.Simulate

/-! `superpose_faithful` (docs/spec/composition-s2.md 8.4): the superposed document decides every act as a
compatible choice's document does on the pulled structure, in any structure in which exactly that choice's atoms
hold. The proof is the simulation of `Simulate.lean` along `fmap`, whose conditions are the facts of
`ChoiceFacts`, `Children` and `Live`, together with the dead copies, the outweighs atoms, a rank and the fuel. -/
namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal)
open VE.SoftNorms (SoftNode SoftDoc soften ValueSoft outweighsName)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u

/-- An unchosen copy is never live: its guard carries an atom the structure denies. -/
theorem dead_extra {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (S : VE.Structure.{u})
    (he : Encodes D c S) (ρ : VE.Valuation S) {M : SoftNode} (hM : M ∈ (sup D).1.soft.T.nodes)
    (hext : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N ≠ M) : ¬ VE.SoftNorms.LiveD (sup D).1.soft S ρ M := by
  rcases (mem_supNodes D M).mp hM with hf | ⟨u, F, cs, hu, rfl⟩ | ⟨m', hm', i', a', N', ha', hc', rfl⟩
  · exact absurd (fmap_frame hh c hf) (hext M ((mem_choiceNodes D c M).mpr (Or.inl hf)))
  · exact absurd (fmap_fixed hh c hu) (hext F ((mem_choiceNodes D c F).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))))
  obtain ⟨i, hi, _⟩ := choice_index hh hc hm'
  rintro ⟨⟨_, hχ⟩, _⟩
  have hilt : i' < setSize D m' := by rw [setSize_eq hm']; exact (List.getElem?_eq_some_iff.mp ha').1
  rw [pattern_rho, ← choiceAtom_eq (findIdx_of_nodup hh.nodup hm') hilt] at hχ
  have hmem := (he _ (List.getElem_mem hm') i' (by rw [← setSize_eq hm']; exact hilt)).mp hχ
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hcn : (c.map (·.1)).Nodup := (complete_map hcm) ▸ hh.nodup
  have := index_of_mem hcn hmem
  simp only at this
  rw [hi] at this
  cases this
  exact hext N' ((mem_choiceNodes D c N').mpr (Or.inr (Or.inr ⟨m', hm', i', a', hi, ha', hc'⟩)))
    (fmap_chosen hh c hm' hi ha' hc')

theorem mem_outweighsTriples {X : SoftDoc} {x : String × String × String} :
    x ∈ VE.SoftNorms.outweighsTriples X ↔ X.soft.outranking = .holistic ∧
      ∃ M N, (M, N) ∈ VE.SoftNorms.collidingPairs X ∧ VE.SoftNorms.Comparable X M N = true ∧
        VE.SoftNorms.pairTriple X M N = x := by
  unfold VE.SoftNorms.outweighsTriples
  split
  · rename_i hh
    simp only [List.mem_reverse, VE.SoftNorms.mem_dedup, List.mem_filterMap]
    constructor
    · rintro ⟨⟨M, N⟩, hp, hx⟩
      split at hx
      · rename_i hcmp; cases hx; exact ⟨hh, M, N, hp, hcmp, rfl⟩
      · cases hx
    · rintro ⟨_, M, N, hp, hcmp, rfl⟩
      exact ⟨(M, N), hp, by simp [hcmp]⟩
  · rename_i hh; simp [hh]

/-! ## The outweighs atoms -/

theorem soft_eq {D : Doc} (c : Choice) : (sup D).1.soft.soft = (choiceDoc D c).1.soft.soft :=
  (sup_shape D).soft.trans (build_shape D (fun _ => true) (pickC c)).soft.symm

theorem regs_eq {D : Doc} (c : Choice) : (sup D).1.soft.T.regulated = (choiceDoc D c).1.soft.T.regulated :=
  (sup_shape D).regulated.trans (build_shape D (fun _ => true) (pickC c)).regulated.symm

theorem dualPerm_eq {D : Doc} (c : Choice) :
    VE.SoftNorms.dualPerm (sup D).1.soft = VE.SoftNorms.dualPerm (choiceDoc D c).1.soft := by
  funext r
  simp only [VE.SoftNorms.dualPerm, VE.SoftNorms.SoftDoc.base, VE.Norms.pairs, regs_eq c]

theorem incompatible_self (X : SoftDoc) (M : SoftNode) : VE.SoftNorms.Incompatible X M M = false := by
  unfold VE.SoftNorms.Incompatible
  cases M.sign <;> simp

theorem act_choice_eq {D : Doc} (hh : Hyps D) (c : Choice) {M N : SoftNode}
    (hM : M ∈ (choiceDoc D c).1.soft.T.nodes) (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    (hi : VE.SoftNorms.Incompatible (choiceDoc D c).1.soft M N = true) :
    VE.SoftNorms.act (choiceDoc D c).1.soft M = VE.SoftNorms.act (choiceDoc D c).1.soft N := by
  have hx : VE.SoftNorms.Incompatible (sup D).1.soft (fmap D c M) (fmap D c N) = true := by
    rw [← hi]
    simp only [VE.SoftNorms.Incompatible, (fmap_fields hh c hM).1, (fmap_fields hh c hN).1,
      (fmap_fields hh c hM).2.1, (fmap_fields hh c hN).2.1, dualPerm_eq c]
  have := VE.SoftNorms.act_eq (sup_softValid hh) hx
  simp only [VE.SoftNorms.act, VE.SoftNorms.actKey, (fmap_fields hh c hM).1, (fmap_fields hh c hN).1,
    dualPerm_eq c] at this
  simpa [VE.SoftNorms.act, VE.SoftNorms.actKey] using this

theorem outweighs_triple {D : Doc} (hh : Hyps D) (c : Choice) {M N : SoftNode}
    (hM : M ∈ (choiceDoc D c).1.soft.T.nodes) (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    (hi : VE.SoftNorms.Incompatible (choiceDoc D c).1.soft M N = true) (hMd : M.mode = .default)
    (hNd : N.mode = .default) (hol : (choiceDoc D c).1.soft.soft.outranking = .holistic) :
    (VE.SoftNorms.higher (choiceDoc D c).1.soft M N = true →
      (VE.SoftNorms.act (choiceDoc D c).1.soft N, VE.SoftNorms.rk N, VE.SoftNorms.rk M) ∈
        VE.SoftNorms.outweighsTriples (choiceDoc D c).1.soft) ∧
    (VE.SoftNorms.higher (choiceDoc D c).1.soft N M = true →
      (VE.SoftNorms.act (choiceDoc D c).1.soft N, VE.SoftNorms.rk M, VE.SoftNorms.rk N) ∈
        VE.SoftNorms.outweighsTriples (choiceDoc D c).1.soft) := by
  have hrv : VE.SoftNorms.RanksValid (choiceDoc D c).1.soft.soft := by rw [← soft_eq c]; exact (sup_softValid hh).ranks
  have hne : M.name ≠ N.name := by
    intro he
    have := choice_name_inj hh c hM hN he
    subst this
    rw [incompatible_self] at hi; cases hi
  have hact := act_choice_eq hh c hM hN hi
  rcases VE.SoftNorms.str_lt_or_gt M.name N.name hne with hlt | hlt
  · have hp : (M, N) ∈ VE.SoftNorms.collidingPairs (choiceDoc D c).1.soft :=
      VE.SoftNorms.mem_collidingPairs.mpr ⟨hM, hN, hMd, hNd, hlt, hi⟩
    refine ⟨fun hh1 => ?_, fun hh2 => ?_⟩
    · refine mem_outweighsTriples.mpr ⟨hol, M, N, hp, by simp [VE.SoftNorms.Comparable, hh1], ?_⟩
      simp [VE.SoftNorms.pairTriple, hh1]
    · refine mem_outweighsTriples.mpr ⟨hol, M, N, hp, by simp [VE.SoftNorms.Comparable, hh2], ?_⟩
      have : VE.SoftNorms.higher (choiceDoc D c).1.soft M N = false := VE.SoftNorms.higher_asymm hrv hh2
      simp [VE.SoftNorms.pairTriple, this, hact]
  · have hp : (N, M) ∈ VE.SoftNorms.collidingPairs (choiceDoc D c).1.soft :=
      VE.SoftNorms.mem_collidingPairs.mpr ⟨hN, hM, hNd, hMd, hlt, by rw [VE.SoftNorms.incompatible_symm]; exact hi⟩
    refine ⟨fun hh1 => ?_, fun hh2 => ?_⟩
    · refine mem_outweighsTriples.mpr ⟨hol, N, M, hp, by simp [VE.SoftNorms.Comparable, hh1], ?_⟩
      have : VE.SoftNorms.higher (choiceDoc D c).1.soft N M = false := VE.SoftNorms.higher_asymm hrv hh1
      simp [VE.SoftNorms.pairTriple, this]
    · refine mem_outweighsTriples.mpr ⟨hol, N, M, hp, by simp [VE.SoftNorms.Comparable, hh2], ?_⟩
      simp [VE.SoftNorms.pairTriple, hh2, hact]

theorem outweighs_corr {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    {a L H : String} (ht : (a, L, H) ∈ VE.SoftNorms.outweighsTriples (choiceDoc D c).1.soft) :
    VE.SoftNorms.OutweighsD (sup D).1.soft S ρ a L H ↔
      VE.SoftNorms.OutweighsD (choiceDoc D c).1.soft (pull D c S) ρ a L H := by
  unfold VE.SoftNorms.OutweighsD VE.SoftNorms.actSortsOf VE.SoftNorms.sortsOf
  rw [regs_eq c]
  exact atom_congr S _ _ _ _ (fun vs => (pull_outweighs hh c S ht vs).symm) ρ

/-! ## Rank and fuel -/

theorem filter_length_le_imp {α : Type} (p q : α → Bool) : ∀ (l : List α), (∀ x ∈ l, p x = true → q x = true) →
    (l.filter p).length ≤ (l.filter q).length
  | [], _ => by simp
  | y :: l, h => by
    have ih := filter_length_le_imp p q l (fun x hx => h x (List.mem_cons_of_mem _ hx))
    simp only [List.filter_cons]
    cases hp : p y <;> cases hq : q y
    · simpa using ih
    · simp; omega
    · exact absurd (h y List.mem_cons_self hp) (by simp [hq])
    · simpa using ih

theorem filter_length_lt {α : Type} (p q : α → Bool) : ∀ (l : List α), (∀ x ∈ l, p x = true → q x = true) →
    (∃ x ∈ l, q x = true ∧ p x = false) → (l.filter p).length < (l.filter q).length
  | [], _, ⟨_, hx, _⟩ => by cases hx
  | y :: l, h, ⟨x, hx, hq, hp⟩ => by
    have hle := filter_length_le_imp p q l (fun z hz => h z (List.mem_cons_of_mem _ hz))
    simp only [List.filter_cons]
    rcases List.mem_cons.mp hx with rfl | hx'
    · rw [hp, hq]; simp; omega
    · have ih := filter_length_lt p q l (fun z hz => h z (List.mem_cons_of_mem _ hz)) ⟨x, hx', hq, hp⟩
      cases hpy : p y <;> cases hqy : q y
      · simpa using ih
      · simp; omega
      · exact absurd (h y List.mem_cons_self hpy) (by simp [hqy])
      · simp; omega

theorem choice_ranked {D : Doc} (hh : Hyps D) (c : Choice) :
    ∃ r : SoftNode → Nat, (∀ N ∈ (choiceDoc D c).1.soft.T.nodes,
      ∀ C ∈ VE.SoftNorms.children (choiceDoc D c).1.soft N, r C < r N) ∧
      ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, r N ≤ VE.SoftNorms.fuel (choiceDoc D c).1.soft := by
  have hv := sup_softValid hh
  obtain ⟨o, ho⟩ := (VE.Norms.valid_of_wellFormed _ hv.wf).precedence
  have hdag := (VE.Route.dag_acyclic _ _ ho).2.2.1
  refine ⟨fun N => ((choiceDoc D c).1.soft.T.nodes.filter
    (fun M => decide (o.idxOf (fmap D c N).name ≤ o.idxOf (fmap D c M).name))).length, fun N hN C hC => ?_,
    fun N _ => List.length_filter_le _ _⟩
  have hfw := child_fwd hh c hN hC
  rw [VE.SoftNorms.mem_childrenIn_iff] at hfw
  obtain ⟨hCX, _, hover⟩ := hfw
  have hidx : o.idxOf (fmap D c N).name < o.idxOf (fmap D c C).name := by
    apply hdag ⟨(fmap D c C).name, (fmap D c C).over⟩
    · simp only [VE.Norms.precedenceNodes, VE.SoftNorms.soften, List.map_map, List.mem_map]
      exact ⟨fmap D c C, hCX, rfl⟩
    · simp only [VE.Route.deps, List.mem_filter, List.contains_iff_mem]
      refine ⟨hover, ?_⟩
      simp only [VE.Route.nodeNames, VE.Norms.precedenceNodes, VE.SoftNorms.soften, List.map_map, List.mem_map]
      exact ⟨fmap D c N, fmap_mem hh c hN, rfl⟩
  apply filter_length_lt
  · intro x _ hx
    simp only [decide_eq_true_eq] at hx ⊢
    omega
  · exact ⟨N, hN, by simp, by simp; omega⟩

theorem nodup_map_on {α β : Type} {f : α → β} : ∀ {l : List α}, (∀ x ∈ l, ∀ y ∈ l, f x = f y → x = y) →
    l.Nodup → (l.map f).Nodup
  | [], _, _ => List.nodup_nil
  | x :: l, hf, hn => by
    rw [List.nodup_cons] at hn
    rw [List.map_cons, List.nodup_cons]
    refine ⟨fun hx => ?_, nodup_map_on (fun a ha b hb => hf a (List.mem_cons_of_mem _ ha) b
      (List.mem_cons_of_mem _ hb)) hn.2⟩
    obtain ⟨y, hy, he⟩ := List.mem_map.mp hx
    exact hn.1 (hf y (List.mem_cons_of_mem _ hy) x List.mem_cons_self he ▸ hy)

theorem choice_fuel_le {D : Doc} (hh : Hyps D) (c : Choice) :
    VE.SoftNorms.fuel (choiceDoc D c).1.soft ≤ VE.SoftNorms.fuel (sup D).1.soft := by
  unfold VE.SoftNorms.fuel
  have hnd : (choiceDoc D c).1.soft.T.nodes.Nodup := nodup_of_map (choice_names_nodup hh c)
  have hmap : ((choiceDoc D c).1.soft.T.nodes.map (fmap D c)).Nodup :=
    nodup_map_on (fun x hx y hy he => fmap_inj hh c hx hy he) hnd
  have := VE.SoftNorms.length_le_of_nodup_subset hmap (fun x hx => by
    obtain ⟨N, hN, rfl⟩ := List.mem_map.mp hx
    exact fmap_mem hh c hN)
  simpa using this

/-! ## The simulation and `superpose_faithful` -/

theorem faithful_sim {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (S : VE.Structure.{u})
    (he : Encodes D c S) (ρ : VE.Valuation S) :
    Sim (sup D).1.soft (choiceDoc D c).1.soft (fmap D c) S (pull D c S).relation ρ where
  soft := soft_eq c
  regs := regs_eq c
  mem := fun _ hN => fmap_mem hh c hN
  inj := fun _ hN _ hN' he => fmap_inj hh c hN hN' he
  pred := fun _ hN => (fmap_fields hh c hN).1
  sign := fun _ hN => (fmap_fields hh c hN).2.1
  mode := fun _ hN => (fmap_fields hh c hN).2.2.1
  rank := fun _ hN => (fmap_fields hh c hN).2.2.2.1
  live := fun _ hN => live_corr hh c S he ρ hN
  dead := fun _ hM hext => dead_extra hh hc S he ρ hM hext
  childFwd := fun _ hN _ hC => child_fwd hh c hN hC
  childBack := fun _ hN _ hC h => child_back hh c hN hC h
  sibling := fun _ hN _ hC hext _ hG => sibling hh hc hN hC hext hG
  outweighs := fun _ hM _ hN hi hMd hNd hol =>
    ⟨fun h1 => outweighs_corr hh c S ρ ((outweighs_triple hh c hM hN hi hMd hNd hol).1 h1),
     fun h2 => outweighs_corr hh c S ρ ((outweighs_triple hh c hM hN hi hMd hNd hol).2 h2)⟩
  ranked := choice_ranked hh c
  fuelLe := choice_fuel_le hh c

/-- 2.3 of the plan: where exactly c's atoms hold, the superposed document decides every act as c's document does on
    the pulled structure. On these chains hq is not needed (an unchosen rule is not live); it is stated because S2b's
    bar case needs it (F21), so that S2b removes only hch. -/
theorem superpose_faithful (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (c : Choice) (hc : Compatible D c) (S : VE.Structure.{u})
    (he : Encodes D c S) (hq : Sat S (choicePremises D)) (r : Regulated)
    (hr : r ∈ (correlate (choiceDoc D c).1).T.regulated) (vs : List S.Carrier) :
  ValueSoft (correlate (sup D).1) r S vs = ValueSoft (correlate (choiceDoc D c).1) r (pull D c S) vs := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  rw [sup_correlate hh, choice_correlate hh c]
  exact value_sim r vs (faithful_sim hh hc S he (tupleVal vs))

end VE.Readings
