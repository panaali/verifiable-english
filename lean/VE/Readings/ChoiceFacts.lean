import VE.Readings.Shape
import VE.Readings.Superpose
import VE.Readings.SoftFacts
import VE.Readings.Names

/-! The nodes of a choice's document and of the superposed document, and the map between them
(docs/spec/composition-s2.md 1.4, 1.7; the proof of `superpose_faithful`).

A rule of `choiceDoc D c` is a rule of the frame, a fixed rule, or the rule of the candidate `c` takes in some
set. `fmap` sends the chosen candidate's rule to its gated, qualified copy in `sup D`, a fixed rule to its copy
with `over` on interface names mapped to every copy, and a frame rule to itself; `chosenAt` finds the candidate
as `qName` does, so the name of `fmap D c N` is `qName D c N.name`. -/
namespace VE.Readings
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)

/-- The candidate a choice takes in the set that declares the rule name `n`, when that candidate declares it. -/
def chosenAt (D : Doc) (c : Choice) (n : String) : Option (Nat × Nat) :=
  match D.sets.findIdx? (fun R => (declaredBy R).contains ("rule", n)) with
  | some m => match c.index ((D.sets[m]?.map (·.id)).getD "") with
    | some i => if declaresRule D m i n then some (m, i) else none
    | none => none
  | none => none

theorem qName_chosenAt (D : Doc) (c : Choice) (n : String) :
    qName D c n = match chosenAt D c n with
      | some (m, i) => qualify (position D m i) n
      | none => n := by
  unfold qName chosenAt
  cases h1 : D.sets.findIdx? (fun R => (declaredBy R).contains ("rule", n)) with
  | none => rfl
  | some m =>
    simp only
    cases h2 : c.index ((D.sets[m]?.map (·.id)).getD "") with
    | none => rfl
    | some i =>
      simp only
      by_cases h3 : declaresRule D m i n = true
      · simp [h3]
      · simp [h3]

/-- A candidate's rule as `gateContent` writes it. -/
def gateNorm (D : Doc) (m i : Nat) (N : SoftNode) : SoftNode :=
  { N with name := qualify (position D m i) N.name, guard := .and N.guard (pattern (m + 1) (setSize D m) i),
           exception := N.exception.map (fun e =>
             { e with sufficient := e.sufficient.map (fun C => .and C (pattern (m + 1) (setSize D m) i)) }) }

theorem gateContent_norm (D : Doc) (m i : Nat) (N : SoftNode) :
    gateContent D m i (.norm N) = .norm (gateNorm D m i N) := rfl

/-- The node of `sup D` a node of `choiceDoc D c` is mapped to. -/
def fmap (D : Doc) (c : Choice) (N : SoftNode) : SoftNode :=
  match chosenAt D c N.name with
  | some (m, i) => gateNorm D m i N
  | none => if N ∈ D.frame.soft.T.nodes then N else copyOver D N

/-- How the rule of a set's candidate enters a choice's document. -/
def ChosenNorm (D : Doc) (c : Choice) (N : SoftNode) : Prop :=
  ∃ m, ∃ hm : m < D.sets.length, ∃ i a, c.index D.sets[m].id = some i ∧ D.sets[m].candidates[i]? = some a ∧
    a.content = some (.norm N)

def FixedNorm (D : Doc) (N : SoftNode) : Prop := ∃ u cs, Item.fixed u (.norm N) cs ∈ D.items

def pickC (c : Choice) (R : ReadingSet) : Option Candidate := (c.index R.id).bind (R.candidates[·]?)

theorem choiceDoc_eq (D : Doc) (c : Choice) : choiceDoc D c = build D (fun _ => true) (pickC c) := rfl

theorem mem_normsOf {c : Content} {N : SoftNode} : N ∈ normsOf c ↔ c = .norm N := by
  cases c <;> simp [normsOf, eq_comm]

theorem mem_choiceNodes (D : Doc) (c : Choice) (N : SoftNode) :
    N ∈ (choiceDoc D c).1.soft.T.nodes ↔ N ∈ D.frame.soft.T.nodes ∨ FixedNorm D N ∨ ChosenNorm D c N := by
  rw [choiceDoc_eq, (build_shape D _ _).nodes, List.mem_append, List.mem_flatMap]
  apply or_congr_right
  constructor
  · rintro ⟨it, hit, hN⟩
    cases it with
    | fixed u c' cs =>
      simp only [buildNodes, if_true, mem_normsOf] at hN
      subst hN; exact Or.inl ⟨u, cs, hit⟩
    | bar u b => simp [buildNodes] at hN
    | set R =>
      simp only [buildNodes] at hN
      split at hN
      · rename_i c' cs hp
        rw [mem_normsOf] at hN
        subst hN
        simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at hp
        obtain ⟨a, hpa, c'', hc'', he⟩ := hp
        cases he
        obtain ⟨m, hm, rfl⟩ := mem_sets_getElem (mem_sets.mpr hit)
        simp only [pickC, Option.bind_eq_some_iff] at hpa
        obtain ⟨i, hi, ha⟩ := hpa
        exact Or.inr ⟨m, hm, i, a, hi, ha, hc''⟩
      · simp at hN
  · rintro (⟨u, cs, hit⟩ | ⟨m, hm, i, a, hi, ha, hc⟩)
    · exact ⟨_, hit, by simp [buildNodes, normsOf]⟩
    · refine ⟨.set D.sets[m], mem_sets.mp (List.getElem_mem hm), ?_⟩
      simp only [buildNodes, pickC, hi, Option.bind_some, ha, hc, Option.map_some]
      simp [normsOf]

def setOf : Item → Option ReadingSet
  | .set R => some R
  | _ => none

theorem sets_eq (D : Doc) : D.sets = D.items.filterMap setOf := by
  unfold Doc.sets; congr

theorem mem_candNodes {D : Doc} {m : Nat} {R : ReadingSet} {i : Nat} {M : SoftNode} :
    M ∈ candNodes D m R i ↔ ∃ a N, R.candidates[i]? = some a ∧ a.content = some (.norm N) ∧ M = gateNorm D m i N := by
  unfold candNodes
  cases ha : R.candidates[i]? with
  | none => simp
  | some a =>
    cases hc : a.content with
    | none => simp [hc]
    | some c =>
      simp only [Option.bind_some, hc, Option.map_some, mem_normsOf]
      constructor
      · intro h
        cases c with
        | norm N => exact ⟨a, N, rfl, hc, by rw [gateContent_norm] at h; cases h; rfl⟩
        | assertion φ => cases h
        | right R => cases h
        | rightLines r ls => cases h
        | limitation L => cases h
      · rintro ⟨a', N, ha', hc', rfl⟩
        cases ha'
        rw [hc] at hc'; cases hc'
        rfl

theorem mem_supNodesAux (D : Doc) : ∀ (l : List Item) (m0 : Nat) (M : SoftNode),
    M ∈ supNodesAux D l m0 ↔ (∃ u N cs, Item.fixed u (.norm N) cs ∈ l ∧ M = copyOver D N) ∨
      (∃ t R i a N, (l.filterMap setOf)[t]? = some R ∧ R.candidates[i]? = some a ∧ a.content = some (.norm N) ∧
        M = gateNorm D (m0 + t) i N)
  | [], _, _ => by simp [supNodesAux]
  | it :: l, m0, M => by
    simp only [supNodesAux, List.mem_append]
    rw [mem_supNodesAux D l]
    cases it with
    | fixed u c cs =>
      simp only [supItemNodes, copyContent_norms, List.mem_map, mem_normsOf, isSet, Bool.false_eq_true, if_false,
        List.mem_cons, List.filterMap_cons, setOf]
      constructor
      · rintro ((⟨N, rfl, rfl⟩) | (⟨u', N, cs', hm, rfl⟩) | ⟨t, R, i, a, N, h1, h2, h3, rfl⟩)
        · exact Or.inl ⟨u, N, cs, Or.inl rfl, rfl⟩
        · exact Or.inl ⟨u', N, cs', Or.inr hm, rfl⟩
        · exact Or.inr ⟨t, R, i, a, N, h1, h2, h3, rfl⟩
      · rintro (⟨u', N, cs', (he | hm), rfl⟩ | ⟨t, R, i, a, N, h1, h2, h3, rfl⟩)
        · cases he; exact Or.inl ⟨N, rfl, rfl⟩
        · exact Or.inr (Or.inl ⟨u', N, cs', hm, rfl⟩)
        · exact Or.inr (Or.inr ⟨t, R, i, a, N, h1, h2, h3, rfl⟩)
    | bar u b =>
      simp only [supItemNodes, List.not_mem_nil, false_or, isSet, Bool.false_eq_true, if_false, List.mem_cons,
        List.filterMap_cons, setOf, reduceCtorEq]
    | set R =>
      simp only [supItemNodes, List.mem_flatMap, List.mem_range, isSet, if_true, List.mem_cons, reduceCtorEq,
        false_or, List.filterMap_cons, setOf]
      constructor
      · rintro (⟨i, _, hi⟩ | (⟨u', N, cs', hm, rfl⟩) | ⟨t, R', i, a, N, h1, h2, h3, rfl⟩)
        · obtain ⟨a, N, h1, h2, rfl⟩ := mem_candNodes.mp hi
          exact Or.inr ⟨0, R, i, a, N, rfl, h1, h2, by simp⟩
        · exact Or.inl ⟨u', N, cs', hm, rfl⟩
        · exact Or.inr ⟨t + 1, R', i, a, N, by simpa using h1, h2, h3, by rw [Nat.add_assoc, Nat.add_comm 1 t]⟩
      · rintro (⟨u', N, cs', hm, rfl⟩ | ⟨t, R', i, a, N, h1, h2, h3, rfl⟩)
        · exact Or.inr (Or.inl ⟨u', N, cs', hm, rfl⟩)
        · cases t with
          | zero =>
            simp at h1; subst h1
            exact Or.inl ⟨i, (List.getElem?_eq_some_iff.mp h2).1, mem_candNodes.mpr ⟨a, N, h2, h3, rfl⟩⟩
          | succ t =>
            refine Or.inr (Or.inr ⟨t, R', i, a, N, by simpa using h1, h2, h3, ?_⟩)
            rw [Nat.add_assoc, Nat.add_comm t 1]

theorem mem_supNodes (D : Doc) (M : SoftNode) :
    M ∈ (sup D).1.soft.T.nodes ↔ M ∈ D.frame.soft.T.nodes ∨
      (∃ u N cs, Item.fixed u (.norm N) cs ∈ D.items ∧ M = copyOver D N) ∨
      (∃ m, ∃ hm : m < D.sets.length, ∃ i a N, D.sets[m].candidates[i]? = some a ∧ a.content = some (.norm N) ∧
        M = gateNorm D m i N) := by
  rw [(sup_shape D).nodes, List.mem_append, mem_supNodesAux]
  apply or_congr Iff.rfl
  apply or_congr Iff.rfl
  rw [← sets_eq]
  constructor
  · rintro ⟨t, R, i, a, N, h1, h2, h3, rfl⟩
    obtain ⟨ht, rfl⟩ := List.getElem?_eq_some_iff.mp h1
    exact ⟨t, ht, i, a, N, h2, h3, by simp⟩
  · rintro ⟨m, hm, i, a, N, h2, h3, rfl⟩
    exact ⟨m, D.sets[m], i, a, N, List.getElem?_eq_getElem hm, h2, h3, by simp⟩

/-! ## Facts about a rule from a document S1 checked -/

/-- A soft document with the frame's soft block, regulated predicates and environment, valid for the chain. -/
theorem nodeFacts_of_home (D : Doc) (hch : D.chain ≠ .rights) (H : RightsDoc × List VE.Formula)
    (hw : sideWF D H = true)
    (hE : H.1.soft.E = D.frame.soft.E) (hR : H.1.soft.T.regulated = D.frame.soft.T.regulated) (N : SoftNode) (hN : N ∈ H.1.soft.T.nodes) :
    VE.Norms.ruleName N.name = true ∧
    (∀ φ ∈ N.guard :: N.carveOuts,
      φ.WellFormed D.frame.soft.E (VE.SoftNorms.sortsIn D.frame.soft.T.regulated N.pred).reverse) ∧
    (N.mode = .default → D.frame.soft.E.predicates (VE.SoftNorms.exceptedName N) = none) ∧
    (∀ π ∈ N.alterable, D.frame.soft.E.predicates (VE.SoftNorms.offName N π) = none) ∧
    (∀ π ∈ N.alterable, VE.SoftNorms.validSoftName π = true) ∧
    (∀ m ∈ N.over, ∃ M ∈ H.1.soft.T.nodes, M.name = m ∧ M.pred = N.pred) := by
  have hc : chainWF D.chain H.1 = true := by
    simp only [sideWF, Bool.and_eq_true] at hw; exact hw.1
  have hsoft : VE.SoftNorms.WellFormedSoft H.1.soft = true := by
    cases hd : D.chain with
    | rights => exact absurd hd hch
    | soft => rw [hd] at hc; simp only [chainWF, Bool.and_eq_true] at hc; exact hc.2
    | norms => rw [hd] at hc; simp only [chainWF, Bool.and_eq_true] at hc; exact hc.2
  have hv := VE.SoftNorms.softValid_of_wellFormed _ hsoft
  obtain ⟨hck, _⟩ := (VE.NormDefaults.wellFormed_iff _).mp hv.wf
  obtain ⟨_, _, _, _, _, _, ⟨hrules, _, _⟩, hover, _⟩ := hck
  have hpN : VE.SoftNorms.primeNode H.1.soft N ∈ (soften H.1.soft).T.nodes := List.mem_map.mpr ⟨N, hN, rfl⟩
  have hnode := hrules _ hpN
  have hcs := checkSoft_parts _ (wellFormedSoft_check _ hsoft)
  refine ⟨hnode.1, fun φ hφ => ?_, fun hd => ?_, fun π hπ => ?_, fun π hπ => ?_, fun m hm => ?_⟩
  · have := hv.typed N hN φ hφ
    rw [hE] at this
    simpa [VE.SoftNorms.sortsOf, hR] using this
  · have := hv.decFresh (VE.SoftNorms.exceptedName N) (by
      simp only [VE.SoftNorms.decisionNames, VE.SoftNorms.decisions, VE.SoftNorms.exceptedDecisions, List.map_append,
        List.mem_append, List.mem_map, List.mem_filter]
      exact Or.inl (Or.inl ⟨_, ⟨N, ⟨hN, by simp [hd]⟩, rfl⟩, rfl⟩))
    rwa [hE] at this
  · have := hv.decFresh (VE.SoftNorms.offName N π) (by
      simp only [VE.SoftNorms.decisionNames, VE.SoftNorms.decisions, VE.SoftNorms.offDecisions, List.map_append,
        List.mem_append, List.mem_map, List.mem_flatMap]
      exact Or.inl (Or.inr ⟨_, ⟨N, hN, ⟨π, hπ, rfl⟩⟩, rfl⟩))
    rwa [hE] at this
  · have hp := checkSoftRule_parties _ N (hcs.2 N hN) π hπ
    have := checkSoftEnv_names _ hcs.1 π (List.mem_append_right _ hp)
    exact this
  · obtain ⟨M, hf, hpred⟩ := hover _ hpN m hm
    obtain ⟨M', hM', rfl⟩ := List.mem_map.mp (List.mem_of_find?_eq_some hf)
    refine ⟨M', hM', by simpa using List.find?_some hf, hpred⟩

theorem attached_set {D : Doc} {u t : String} (h : Attached D u t) : ∃ R ∈ D.sets, R.id = t := by
  induction h with
  | direct _ _ _ R hR ht _ => exact ⟨R, hR, ht⟩
  | step _ _ _ _ _ _ ih => exact ih

theorem wellFormedDoc_parts {D : Doc} (h : WellFormedDoc D = true) :
    reservedFree D = true ∧ distinctAcrossSets D = true ∧ interfaceClosed D = true ∧ singlyAttached D = true ∧
    sideWF D (free D) = true ∧ ∀ R ∈ D.sets, ∀ i, i < R.candidates.length →
      (R.candidates[i]?.bind (·.content)).isNone = true ∨ sideWF D (one D R.id i) = true := by
  simp only [WellFormedDoc, Bool.and_eq_true, List.all_eq_true, List.mem_range, Bool.or_eq_true] at h
  exact ⟨h.1.1.1.1.1, h.1.1.1.1.2, h.1.1.1.2, h.1.1.2, h.1.2, h.2⟩

/-- Every rule of a choice's document lies in a document that S1's admission checked. -/
theorem home_exists (D : Doc) (h : WellFormedDoc D = true) (hr : supReady D = true) (c : Choice) (N : SoftNode)
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    ∃ H : RightsDoc × List VE.Formula, sideWF D H = true ∧ N ∈ H.1.soft.T.nodes ∧
      ∃ keep pick, H = build D keep pick := by
  obtain ⟨_, _, _, hsa, hfree, hone⟩ := wellFormedDoc_parts h
  have hfreeNodes := (build_shape D (fun u => (attached D u).isEmpty) (fun _ => none)).nodes
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · exact ⟨free D, hfree, by rw [free, hfreeNodes]; exact List.mem_append_left _ hf, _, _, rfl⟩
  · cases hat : attached D u with
    | nil =>
      refine ⟨free D, hfree, ?_, _, _, rfl⟩
      rw [free, hfreeNodes]
      apply List.mem_append_right
      exact List.mem_flatMap.mpr ⟨_, hu, by simp [buildNodes, hat, normsOf]⟩
    | cons t rest =>
      have hA : Attached D u t := (attached_iff D u t).mp (by rw [hat]; simp)
      obtain ⟨R, hR, rfl⟩ := attached_set hA
      have hne : 0 < R.candidates.length := by
        simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
        have := hr.1.1.1.1.1.1.2 R hR
        simp only [Bool.not_eq_true', List.isEmpty_eq_false_iff] at this
        exact List.length_pos_iff.mpr this.1
      have hcont : (R.candidates[0]?.bind (·.content)).isSome = true := by
        simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
        have := (hr.1.1.1.1.1.1.2 R hR)
        rw [List.getElem?_eq_getElem hne]
        exact this.2 _ (List.getElem_mem hne)
      have hw : sideWF D (one D R.id 0) = true := by
        rcases hone R hR 0 hne with h' | h'
        · rw [Option.isNone_iff_eq_none] at h'; rw [h'] at hcont; cases hcont
        · exact h'
      refine ⟨one D R.id 0, hw, ?_, _, _, rfl⟩
      rw [one, (build_shape D _ _).nodes]
      apply List.mem_append_right
      refine List.mem_flatMap.mpr ⟨_, hu, ?_⟩
      have hall : (attached D u).all (· == R.id) = true := by
        have := (singlyAttached_spec D).mp hsa
        rw [List.all_eq_true]
        intro t' ht'
        have := this u R.id t' hA ((attached_iff D u t').mp ht')
        simp [this]
      simp [buildNodes, hall, normsOf]
  · have hw : sideWF D (one D D.sets[m].id i) = true := by
      have hlt : i < D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp ha).1
      rcases hone D.sets[m] (List.getElem_mem hm) i hlt with h' | h'
      · simp [ha, hc] at h'
      · exact h'
    refine ⟨one D D.sets[m].id i, hw, ?_, _, _, rfl⟩
    rw [one, (build_shape D _ _).nodes]
    apply List.mem_append_right
    refine List.mem_flatMap.mpr ⟨.set D.sets[m], mem_sets.mp (List.getElem_mem hm), ?_⟩
    simp [buildNodes, ha, hc, normsOf]

/-! ## Contents on the soft chain -/

theorem sum_eq_zero_iff : ∀ {l : List Nat}, l.sum = 0 ↔ ∀ x ∈ l, x = 0
  | [] => by simp
  | x :: l => by simp only [List.sum_cons, List.mem_cons, forall_eq_or_imp, ← sum_eq_zero_iff (l := l)]; omega

/-- Every content of a document whose `sup D` holds no rights material adds none. -/
theorem contrib_zero (D : Doc) (h : noRights (sup D).1 = true) :
    (∀ u c cs, Item.fixed u c cs ∈ D.items → contrib c = 0) ∧
    (∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∀ c, a.content = some c → contrib c = 0) := by
  rw [noRights_junk] at h
  have hx := (sup_shape D).junk
  rw [h] at hx
  have hz : (D.items.map supItemJunk).sum = 0 := by omega
  rw [sum_eq_zero_iff] at hz
  refine ⟨fun u c cs hu => ?_, fun R hR a ha c hc => ?_⟩
  · exact hz _ (List.mem_map.mpr ⟨_, hu, rfl⟩)
  · have hs := hz _ (List.mem_map.mpr ⟨_, mem_sets.mp hR, rfl⟩)
    simp only [supItemJunk, sum_eq_zero_iff, List.mem_map, List.mem_range, forall_exists_index, and_imp,
      forall_apply_eq_imp_iff₂] at hs
    obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem ha
    have := hs i hi
    simp only [candJunk, List.getElem?_eq_getElem hi, Option.bind_some, hc, Option.map_some] at this
    exact this

/-- A content that adds no rights material and declares a rule name is a norm of that name. -/
theorem declared_rule_norm {c : Content} (h0 : contrib c = 0) {n : String} (hn : ("rule", n) ∈ c.declared) :
    ∃ N, c = .norm N ∧ N.name = n := by
  cases c with
  | assertion φ => simp [Content.declared] at hn
  | norm N => simp [Content.declared] at hn; exact ⟨N, rfl, hn.symm⟩
  | right R => simp [contrib] at h0
  | rightLines r ls =>
    simp [contrib] at h0; subst h0
    simp [Content.declared] at hn
  | limitation L => simp [contrib] at h0

/-! ## `chosenAt` and `fmap` on each kind of rule -/

theorem build_soft_wf (D : Doc) (hch : D.chain ≠ .rights) (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (hw : sideWF D (build D keep pick) = true) : VE.SoftNorms.WellFormedSoft (build D keep pick).1.soft = true := by
  have hc : chainWF D.chain (build D keep pick).1 = true := by
    simp only [sideWF, Bool.and_eq_true] at hw; exact hw.1
  cases hd : D.chain with
  | rights => exact absurd hd hch
  | soft => rw [hd] at hc; simp only [chainWF, Bool.and_eq_true] at hc; exact hc.2
  | norms => rw [hd] at hc; simp only [chainWF, Bool.and_eq_true] at hc; exact hc.2

/-- In a document S1 checked, a frame rule and a placed rule never share a name, and frame names are distinct. -/
theorem build_names (D : Doc) (hch : D.chain ≠ .rights) (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (hw : sideWF D (build D keep pick) = true) :
    (D.frame.soft.T.nodes.map (·.name)).Nodup ∧
    ∀ N ∈ D.frame.soft.T.nodes, ∀ N' ∈ D.items.flatMap (buildNodes keep pick), N.name ≠ N'.name := by
  have hv := VE.SoftNorms.softValid_of_wellFormed _ (build_soft_wf D hch keep pick hw)
  have hn := hv.names
  rw [(build_shape D keep pick).nodes, List.map_append, List.nodup_append] at hn
  refine ⟨hn.1, fun N hN N' hN' he => ?_⟩
  exact hn.2.2 N.name (List.mem_map.mpr ⟨N, hN, rfl⟩) N'.name (List.mem_map.mpr ⟨N', hN', rfl⟩) he

theorem sets_declare_disjoint {D : Doc} (hn : (D.sets.map (·.id)).Nodup) (hda : distinctAcrossSets D = true)
    {m m' : Nat} (hm : m < D.sets.length) (hm' : m' < D.sets.length) (hne : m ≠ m') {x y : String × String}
    (hx : x ∈ declaredBy D.sets[m]) (hy : y ∈ declaredBy D.sets[m']) : x.2 ≠ y.2 := by
  have h3 := ((distinctAcrossSets_spec D).mp hda).2.2.1
  have hid : D.sets[m].id ≠ D.sets[m'].id := fun e => hne (ids_inj hn hm hm' e)
  exact fun e => h3 D.sets[m'] (List.getElem_mem hm') D.sets[m] (List.getElem_mem hm) (Ne.symm hid) y hy x hx e

theorem candidate_declares {D : Doc} {m : Nat} (hm : m < D.sets.length) {i : Nat} {a : Candidate}
    (ha : D.sets[m].candidates[i]? = some a) {c : Content} (hc : a.content = some c) {x : String × String}
    (hx : x ∈ c.declared) : x ∈ declaredBy D.sets[m] := by
  simp only [declaredBy, List.mem_flatMap, List.mem_filterMap]
  exact ⟨c, ⟨a, List.mem_of_getElem? ha, hc⟩, hx⟩

theorem chosenAt_chosen (D : Doc) (hn : (D.sets.map (·.id)).Nodup) (hda : distinctAcrossSets D = true) (c : Choice)
    {m : Nat} (hm : m < D.sets.length) {i : Nat} {a : Candidate} {N : SoftNode}
    (hi : c.index D.sets[m].id = some i) (ha : D.sets[m].candidates[i]? = some a)
    (hc : a.content = some (.norm N)) : chosenAt D c N.name = some (m, i) := by
  have hdecl : ("rule", N.name) ∈ declaredBy D.sets[m] :=
    candidate_declares hm ha hc (by simp [Content.declared])
  have hf : D.sets.findIdx? (fun R => (declaredBy R).contains ("rule", N.name)) = some m := by
    apply List.findIdx?_eq_some_iff_getElem.mpr
    refine ⟨hm, by simpa using hdecl, fun j hj => ?_⟩
    simp only [List.contains_iff_mem]
    intro hj'
    exact sets_declare_disjoint hn hda (Nat.lt_trans hj hm) hm (by omega) hj' hdecl rfl
  unfold chosenAt
  rw [hf]
  simp only [List.getElem?_eq_getElem hm, Option.map_some, Option.getD_some, hi]
  rw [if_pos]
  simp [declaresRule, List.getElem?_eq_getElem hm, ha, hc, Content.declared]

theorem chosenAt_fixed (D : Doc) (hda : distinctAcrossSets D = true) (c : Choice) {u : String} {N : SoftNode}
    {cs : List (String × List String)} (hu : Item.fixed u (.norm N) cs ∈ D.items) : chosenAt D c N.name = none := by
  have h1 := ((distinctAcrossSets_spec D).mp hda).1
  have hf : D.sets.findIdx? (fun R => (declaredBy R).contains ("rule", N.name)) = none := by
    apply List.findIdx?_eq_none_iff.mpr
    intro R hR
    cases hd : (declaredBy R).contains ("rule", N.name) with
    | false => rfl
    | true =>
      exact absurd rfl (h1 R hR _ (List.contains_iff_mem.mp hd) u _ cs hu ("rule", N.name)
        (by simp [Content.declared]))
  unfold chosenAt
  rw [hf]

/-- The documents of the hypotheses of 8.4. -/
structure Hyps (D : Doc) : Prop where
  wf : WellFormedDoc D = true
  chain : D.chain ≠ .rights
  sp : superposable D = true

theorem Hyps.ready {D : Doc} (hh : Hyps D) : supReady D = true := superposable_supReady hh.sp
theorem Hyps.nodup {D : Doc} (hh : Hyps D) : (D.sets.map (·.id)).Nodup := supReady_nodup hh.ready
theorem Hyps.noRights {D : Doc} (hh : Hyps D) : noRights (sup D).1 = true := by
  have := (sup_wellFormed D hh.sp).1
  cases hd : D.chain with
  | rights => exact absurd hd hh.chain
  | soft => rw [hd] at this; simp only [chainWF, Bool.and_eq_true] at this; exact this.1.1
  | norms => rw [hd] at this; simp only [chainWF, Bool.and_eq_true] at this; exact this.1.1
theorem Hyps.da {D : Doc} (hh : Hyps D) : distinctAcrossSets D = true := (wellFormedDoc_parts hh.wf).2.1

/-- The document of a candidate with content is one S1 checked. -/
theorem one_wf {D : Doc} (hh : Hyps D) {m : Nat} (hm : m < D.sets.length) {i : Nat} {a : Candidate}
    (ha : D.sets[m].candidates[i]? = some a) {c : Content} (hc : a.content = some c) :
    sideWF D (one D D.sets[m].id i) = true := by
  have hlt : i < D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp ha).1
  rcases (wellFormedDoc_parts hh.wf).2.2.2.2.2 D.sets[m] (List.getElem_mem hm) i hlt with h' | h'
  · simp [ha, hc] at h'
  · exact h'

theorem one_has {D : Doc} {m : Nat} (hm : m < D.sets.length) {i : Nat} {a : Candidate}
    (ha : D.sets[m].candidates[i]? = some a) {N : SoftNode} (hc : a.content = some (.norm N)) :
    N ∈ D.items.flatMap (buildNodes (fun u => (attached D u).all (· == D.sets[m].id))
      (fun R => if R.id == D.sets[m].id then R.candidates[i]? else none)) := by
  refine List.mem_flatMap.mpr ⟨.set D.sets[m], mem_sets.mp (List.getElem_mem hm), ?_⟩
  simp [buildNodes, ha, hc, normsOf]

theorem chosenAt_frame {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ D.frame.soft.T.nodes) :
    chosenAt D c N.name = none := by
  have hf : D.sets.findIdx? (fun R => (declaredBy R).contains ("rule", N.name)) = none := by
    apply List.findIdx?_eq_none_iff.mpr
    intro R hR
    cases hd : (declaredBy R).contains ("rule", N.name) with
    | false => rfl
    | true =>
      exfalso
      have hd' := List.contains_iff_mem.mp hd
      simp only [declaredBy, List.mem_flatMap, List.mem_filterMap] at hd'
      obtain ⟨c', ⟨a, ha, hc⟩, hx⟩ := hd'
      obtain ⟨m, hm, rfl⟩ := mem_sets_getElem hR
      obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem ha
      have ha' : D.sets[m].candidates[i]? = some D.sets[m].candidates[i] := List.getElem?_eq_getElem hi
      obtain ⟨N', rfl, hn⟩ := declared_rule_norm
        ((contrib_zero D hh.noRights).2 _ (List.getElem_mem hm) _ (List.getElem_mem hi) _ hc) hx
      have hw := one_wf hh hm ha' hc
      exact (build_names D hh.chain _ _ hw).2 N hN N' (one_has hm ha' hc) hn.symm
  unfold chosenAt
  rw [hf]

theorem fmap_chosen {D : Doc} (hh : Hyps D) (c : Choice) {m : Nat} (hm : m < D.sets.length) {i : Nat}
    {a : Candidate} {N : SoftNode} (hi : c.index D.sets[m].id = some i) (ha : D.sets[m].candidates[i]? = some a)
    (hc : a.content = some (.norm N)) : fmap D c N = gateNorm D m i N := by
  unfold fmap
  rw [chosenAt_chosen D hh.nodup hh.da c hm hi ha hc]

theorem fmap_frame {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ D.frame.soft.T.nodes) :
    fmap D c N = N := by
  unfold fmap
  rw [chosenAt_frame hh c hN, if_pos hN]

/-- A fixed rule lies, as a placed rule, in a document S1 checked. -/
theorem fixed_home {D : Doc} (hh : Hyps D) {u : String} {N : SoftNode} {cs : List (String × List String)}
    (hu : Item.fixed u (.norm N) cs ∈ D.items) :
    ∃ keep pick, (∀ R a, pick R = some a → a ∈ R.candidates) ∧ sideWF D (build D keep pick) = true ∧
      N ∈ D.items.flatMap (buildNodes keep pick) := by
  obtain ⟨_, _, _, hsa, hfree, hone⟩ := wellFormedDoc_parts hh.wf
  have hr := hh.ready
  cases hat : attached D u with
  | nil => exact ⟨fun u => (attached D u).isEmpty, fun _ => none, (fun R a h => by cases h), hfree,
      List.mem_flatMap.mpr ⟨_, hu, by simp [buildNodes, hat, normsOf]⟩⟩
  | cons t rest =>
    have hA : Attached D u t := (attached_iff D u t).mp (by rw [hat]; simp)
    obtain ⟨R, hR, rfl⟩ := attached_set hA
    have hne : 0 < R.candidates.length := by
      simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
      have := hr.1.1.1.1.1.1.2 R hR
      simp only [Bool.not_eq_true', List.isEmpty_eq_false_iff] at this
      exact List.length_pos_iff.mpr this.1
    have hcont : (R.candidates[0]?.bind (·.content)).isSome = true := by
      simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
      have := (hr.1.1.1.1.1.1.2 R hR)
      rw [List.getElem?_eq_getElem hne]
      exact this.2 _ (List.getElem_mem hne)
    have hw : sideWF D (one D R.id 0) = true := by
      rcases hone R hR 0 hne with h' | h'
      · rw [Option.isNone_iff_eq_none] at h'; rw [h'] at hcont; cases hcont
      · exact h'
    refine ⟨_, _, fun R' a h => ?_, hw, List.mem_flatMap.mpr ⟨_, hu, ?_⟩⟩
    · simp only at h
      split at h
      · exact List.mem_of_getElem? h
      · cases h
    have hall : (attached D u).all (· == R.id) = true := by
      have := (singlyAttached_spec D).mp hsa
      rw [List.all_eq_true]
      intro t' ht'
      have := this u R.id t' hA ((attached_iff D u t').mp ht')
      simp [this]
    simp [buildNodes, hall, normsOf]

/-- A fixed rule is no frame rule. -/
theorem fixed_not_frame {D : Doc} (hh : Hyps D) {u : String} {N : SoftNode} {cs : List (String × List String)}
    (hu : Item.fixed u (.norm N) cs ∈ D.items) : N ∉ D.frame.soft.T.nodes := by
  intro hN
  obtain ⟨keep, pick, _, hw, hm⟩ := fixed_home hh hu
  exact (build_names D hh.chain keep pick hw).2 N hN N hm rfl

theorem fmap_fixed {D : Doc} (hh : Hyps D) (c : Choice) {u : String} {N : SoftNode} {cs : List (String × List String)}
    (hu : Item.fixed u (.norm N) cs ∈ D.items) : fmap D c N = copyOver D N := by
  unfold fmap
  rw [chosenAt_fixed D hh.da c hu, if_neg (fixed_not_frame hh hu)]

/-! ## The image, fields, names -/

theorem fmap_mem {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    fmap D c N ∈ (sup D).1.soft.T.nodes := by
  rw [mem_supNodes]
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · rw [fmap_frame hh c hf]; exact Or.inl hf
  · rw [fmap_fixed hh c hu]; exact Or.inr (Or.inl ⟨u, N, cs, hu, rfl⟩)
  · rw [fmap_chosen hh c hm hi ha hc]; exact Or.inr (Or.inr ⟨m, hm, i, a, N, ha, hc, rfl⟩)

/-- The fields the soft semantics reads, apart from the name, guard and `over`, are kept by `fmap`. -/
theorem fmap_fields {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (fmap D c N).pred = N.pred ∧ (fmap D c N).sign = N.sign ∧ (fmap D c N).mode = N.mode ∧
    (fmap D c N).rank = N.rank ∧ (fmap D c N).alterable = N.alterable ∧ (fmap D c N).carveOuts = N.carveOuts := by
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · rw [fmap_frame hh c hf]; exact ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩
  · rw [fmap_fixed hh c hu]; exact ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩
  · rw [fmap_chosen hh c hm hi ha hc]; exact ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem pairwise_ne {α : Type} {R : α → α → Prop} : ∀ {l : List α}, l.Pairwise R → ∀ {x y : α}, x ∈ l → y ∈ l →
    x ≠ y → R x y ∨ R y x
  | [], _, _, _, hx, _, _ => by cases hx
  | z :: l, h, x, y, hx, hy, hne => by
    rw [List.pairwise_cons] at h
    rcases List.mem_cons.mp hx with h1 | hx'
    · rcases List.mem_cons.mp hy with h2 | hy'
      · exact absurd (h1.trans h2.symm) hne
      · subst h1; exact Or.inl (h.1 y hy')
    · rcases List.mem_cons.mp hy with h2 | hy'
      · subst h2; exact Or.inr (h.1 x hx')
      · exact pairwise_ne h.2 hx' hy' hne

/-- Two rules of a choice's document with one name are one rule. -/
theorem choice_name_inj {D : Doc} (hh : Hyps D) (c : Choice) {N N' : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) (hN' : N' ∈ (choiceDoc D c).1.soft.T.nodes) (he : N.name = N'.name) :
    N = N' := by
  have hfree := (wellFormedDoc_parts hh.wf).2.2.2.2.1
  have hda := (distinctAcrossSets_spec D).mp hh.da
  have frame_rest : ∀ {F M : SoftNode}, F ∈ D.frame.soft.T.nodes → M ∈ (choiceDoc D c).1.soft.T.nodes →
      M ∉ D.frame.soft.T.nodes → F.name ≠ M.name := by
    intro F M hF hM hMf
    rcases (mem_choiceNodes D c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
    · exact absurd hf hMf
    · obtain ⟨keep, pick, _, hw, hmem⟩ := fixed_home hh hu
      exact (build_names D hh.chain keep pick hw).2 F hF M hmem
    · exact (build_names D hh.chain _ _ (one_wf hh hm ha hc)).2 F hF M (one_has hm ha hc)
  by_cases hf : N ∈ D.frame.soft.T.nodes <;> by_cases hf' : N' ∈ D.frame.soft.T.nodes
  · exact inj_of_nodup_map (build_names D hh.chain _ _ hfree).1 hf hf' he
  · exact absurd he (frame_rest hf hN' hf')
  · exact absurd he.symm (frame_rest hf' hN hf)
  rcases (mem_choiceNodes D c N).mp hN with h1 | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · exact absurd h1 hf
  · rcases (mem_choiceNodes D c N').mp hN' with h1' | ⟨u', cs', hu'⟩ | ⟨m', hm', i', a', hi', ha', hc'⟩
    · exact absurd h1' hf'
    · by_cases hx : Item.fixed u (.norm N) cs = Item.fixed u' (.norm N') cs'
      · cases hx; rfl
      · exfalso
        rcases pairwise_ne hda.2.2.2 hu hu' hx with h | h
        · exact h N.name (by simp [Item.names, Content.declared]) (by simp [Item.names, Content.declared]; exact he)
        · exact h N'.name (by simp [Item.names, Content.declared]) (by simp [Item.names, Content.declared]; exact he.symm)
    · exfalso
      exact hda.1 _ (List.getElem_mem hm') ("rule", N'.name)
        (candidate_declares hm' ha' hc' (by simp [Content.declared])) u _ cs hu
        ("rule", N.name) (by simp [Content.declared]) (by simp [he])
  · rcases (mem_choiceNodes D c N').mp hN' with h1' | ⟨u', cs', hu'⟩ | ⟨m', hm', i', a', hi', ha', hc'⟩
    · exact absurd h1' hf'
    · exfalso
      exact hda.1 _ (List.getElem_mem hm) ("rule", N.name)
        (candidate_declares hm ha hc (by simp [Content.declared])) u' _ cs' hu'
        ("rule", N'.name) (by simp [Content.declared]) (by simp [he])
    · by_cases hmm : m = m'
      · subst hmm
        rw [hi] at hi'; cases hi'
        rw [ha] at ha'; cases ha'
        rw [hc] at hc'; cases hc'
        rfl
      · exact absurd he (sets_declare_disjoint hh.nodup hh.da hm hm' hmm
          (candidate_declares hm ha hc (x := ("rule", N.name)) (by simp [Content.declared]))
          (candidate_declares hm' ha' hc' (x := ("rule", N'.name)) (by simp [Content.declared])))

theorem split_char (x : Char) : ∀ (a a' b b' : List Char), (∀ c ∈ a, c ≠ x) → (∀ c ∈ a', c ≠ x) →
    a ++ x :: b = a' ++ x :: b' → a = a' ∧ b = b'
  | [], [], b, b', _, _, h => by simpa using h
  | [], c :: a', b, b', _, h', h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h; exact absurd h.1.symm (h' c (by simp))
  | c :: a, [], b, b', ha, _, h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h; exact absurd h.1 (ha c (by simp))
  | c :: a, c' :: a', b, b', ha, ha', h => by
    simp only [List.cons_append, List.cons.injEq] at h
    obtain ⟨h1, h2⟩ := split_char x a a' b b' (fun y hy => ha y (by simp [hy])) (fun y hy => ha' y (by simp [hy])) h.2
    exact ⟨by rw [h.1, h1], h2⟩

theorem digits_ne_dash (n : Nat) : ∀ c ∈ Nat.toDigits 10 n, c ≠ '-' := by
  have hv := toDigitsCore_valid (n + 1) n [] (by rfl)
  intro c hc
  have := List.all_eq_true.mp hv c hc
  simp only [Bool.and_eq_true, decide_eq_true_eq] at this
  intro he; subst he
  exact absurd this.1 (by decide)

theorem qualify_inj {k k' : Nat} {n n' : String} (h : qualify k n = qualify k' n') : k = k' ∧ n = n' := by
  have := congrArg String.toList h
  simp only [qualify, String.toList, String.data_append, toString_data, List.append_assoc] at this
  have h2 := List.append_cancel_left this
  obtain ⟨h3, h4⟩ := split_char '-' _ _ _ _ (digits_ne_dash k) (digits_ne_dash k') h2
  exact ⟨toDigits_inj h3, String.ext h4⟩

theorem frame_not_reserved {D : Doc} (hh : Hyps D) {N : SoftNode} (hN : N ∈ D.frame.soft.T.nodes) :
    reservedName N.name = false := by
  have hrf := (wellFormedDoc_parts hh.wf).1
  simp only [reservedFree, Bool.and_eq_true, Bool.not_eq_true', List.any_eq_false, List.mem_append,
    List.mem_map] at hrf
  have := hrf.1.2 N.name (Or.inl (Or.inl ⟨N, hN, rfl⟩))
  simpa using this

theorem fixed_not_reserved {D : Doc} (hh : Hyps D) {u : String} {N : SoftNode} {cs : List (String × List String)}
    (hu : Item.fixed u (.norm N) cs ∈ D.items) : reservedName N.name = false := by
  have hrf := (wellFormedDoc_parts hh.wf).1
  simp only [reservedFree, Bool.and_eq_true, List.all_eq_true] at hrf
  have := hrf.2 _ hu
  simpa [contentReserved, Content.declared] using this

theorem fmap_name {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (fmap D c N).name = qName D c N.name := by
  rw [qName_chosenAt]
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · rw [fmap_frame hh c hf, chosenAt_frame hh c hf]
  · rw [fmap_fixed hh c hu, chosenAt_fixed D hh.da c hu]; rfl
  · rw [fmap_chosen hh c hm hi ha hc, chosenAt_chosen D hh.nodup hh.da c hm hi ha hc]; rfl

theorem fmap_inj {D : Doc} (hh : Hyps D) (c : Choice) {N N' : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    (hN' : N' ∈ (choiceDoc D c).1.soft.T.nodes) (he : fmap D c N = fmap D c N') : N = N' := by
  have hn := congrArg (fun M : SoftNode => M.name) he
  simp only at hn
  rw [fmap_name hh c hN, fmap_name hh c hN', qName_chosenAt, qName_chosenAt] at hn
  apply choice_name_inj hh c hN hN'
  have plain : ∀ {M : SoftNode}, M ∈ (choiceDoc D c).1.soft.T.nodes → chosenAt D c M.name = none →
      reservedName M.name = false := by
    intro M hM hnone
    rcases (mem_choiceNodes D c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
    · exact frame_not_reserved hh hf
    · exact fixed_not_reserved hh hu
    · rw [chosenAt_chosen D hh.nodup hh.da c hm hi ha hc] at hnone; cases hnone
  cases h1 : chosenAt D c N.name with
  | none =>
    cases h2 : chosenAt D c N'.name with
    | none => rw [h1, h2] at hn; exact hn
    | some p =>
      rw [h1, h2] at hn
      exact absurd hn.symm (qualify_ne (plain hN h1))
  | some p =>
    cases h2 : chosenAt D c N'.name with
    | none =>
      rw [h1, h2] at hn
      exact absurd hn (qualify_ne (plain hN' h2))
    | some p' =>
      rw [h1, h2] at hn
      exact (qualify_inj hn).2

/-! ## The rules of a choice's document are distinct -/

theorem mem_buildNodes_choice {c : Choice} {it : Item} {M : SoftNode}
    (h : M ∈ buildNodes (fun _ => true) (pickC c) it) :
    (∃ u cs, it = .fixed u (.norm M) cs) ∨
      (∃ R a, it = .set R ∧ pickC c R = some a ∧ a.content = some (.norm M)) := by
  cases it with
  | fixed u c' cs =>
    simp only [buildNodes, if_true, mem_normsOf] at h
    subst h; exact Or.inl ⟨u, cs, rfl⟩
  | bar u b => simp [buildNodes] at h
  | set R =>
    simp only [buildNodes] at h
    split at h
    · rename_i c' cs hp
      rw [mem_normsOf] at h; subst h
      simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at hp
      obtain ⟨a, hpa, c'', hc'', he⟩ := hp
      cases he
      exact Or.inr ⟨R, a, rfl, hpa, hc''⟩
    · simp at h

theorem choice_names_nodup {D : Doc} (hh : Hyps D) (c : Choice) :
    ((choiceDoc D c).1.soft.T.nodes.map (·.name)).Nodup := by
  have hfree := (wellFormedDoc_parts hh.wf).2.2.2.2.1
  have hda := (distinctAcrossSets_spec D).mp hh.da
  rw [choiceDoc_eq, (build_shape D _ _).nodes, List.map_append, List.nodup_append]
  refine ⟨(build_names D hh.chain _ _ hfree).1, ?_, ?_⟩
  · -- the placed rules
    rw [List.map_flatMap, List.nodup_iff_pairwise_ne, List.pairwise_flatMap]
    refine ⟨fun it _ => ?_, ?_⟩
    · cases it with
      | fixed u c' cs => cases c' <;> simp [buildNodes, normsOf]
      | bar u b => simp [buildNodes]
      | set R =>
        simp only [buildNodes]
        split <;> rename_i hp
        · rename_i c' cs; cases c' <;> simp [normsOf]
        · simp
    · have hP1 := hda.2.2.2
      have hP2 : D.items.Pairwise (fun x y => ∀ R R', setOf x = some R → setOf y = some R' → R.id ≠ R'.id) := by
        have := hh.nodup
        rw [sets_eq, List.nodup_iff_pairwise_ne, List.pairwise_map, List.pairwise_filterMap] at this
        exact this.imp (fun h R R' hR hR' => h R hR R' hR')
      refine (hP1.and hP2).imp_of_mem (fun {x y} hx hy hxy => ?_)
      intro n hn n' hn' he
      simp only [List.mem_map] at hn hn'
      obtain ⟨M, hM, rfl⟩ := hn
      obtain ⟨M', hM', rfl⟩ := hn'
      rcases mem_buildNodes_choice hM with ⟨u, cs, rfl⟩ | ⟨R, a, rfl, hpa, hc⟩ <;>
        rcases mem_buildNodes_choice hM' with ⟨u', cs', rfl⟩ | ⟨R', a', rfl, hpa', hc'⟩
      · exact hxy.1 M.name (by simp [Item.names, Content.declared]) (by simp [Item.names, Content.declared]; exact he)
      · simp only [pickC, Option.bind_eq_some_iff] at hpa'
        obtain ⟨i', _, ha'⟩ := hpa'
        exact hda.1 R' (mem_sets.mpr hy) ("rule", M'.name)
          (by simp only [declaredBy, List.mem_flatMap, List.mem_filterMap]
              exact ⟨_, ⟨a', List.mem_of_getElem? ha', hc'⟩, by simp [Content.declared]⟩)
          u _ cs hx ("rule", M.name) (by simp [Content.declared]) he
      · simp only [pickC, Option.bind_eq_some_iff] at hpa
        obtain ⟨i, _, ha⟩ := hpa
        exact hda.1 R (mem_sets.mpr hx) ("rule", M.name)
          (by simp only [declaredBy, List.mem_flatMap, List.mem_filterMap]
              exact ⟨_, ⟨a, List.mem_of_getElem? ha, hc⟩, by simp [Content.declared]⟩)
          u' _ cs' hy ("rule", M'.name) (by simp [Content.declared]) he.symm
      · simp only [pickC, Option.bind_eq_some_iff] at hpa hpa'
        obtain ⟨i, _, ha⟩ := hpa
        obtain ⟨i', _, ha'⟩ := hpa'
        exact hda.2.2.1 R (mem_sets.mpr hx) R' (mem_sets.mpr hy) (hxy.2 R R' rfl rfl) ("rule", M.name)
          (by simp only [declaredBy, List.mem_flatMap, List.mem_filterMap]
              exact ⟨_, ⟨a, List.mem_of_getElem? ha, hc⟩, by simp [Content.declared]⟩)
          ("rule", M'.name)
          (by simp only [declaredBy, List.mem_flatMap, List.mem_filterMap]
              exact ⟨_, ⟨a', List.mem_of_getElem? ha', hc'⟩, by simp [Content.declared]⟩) he.symm
  · intro n hn n' hn' he
    simp only [List.mem_map] at hn hn'
    obtain ⟨F, hF, rfl⟩ := hn
    obtain ⟨M, hM, rfl⟩ := hn'
    obtain ⟨it, hit, hM⟩ := List.mem_flatMap.mp hM
    rcases mem_buildNodes_choice hM with ⟨u, cs, rfl⟩ | ⟨R, a, rfl, hpa, hc⟩
    · obtain ⟨keep, pick, _, hw, hm⟩ := fixed_home hh hit
      exact (build_names D hh.chain keep pick hw).2 F hF M hm he
    · obtain ⟨m, hm, rfl⟩ := mem_sets_getElem (mem_sets.mpr hit)
      simp only [pickC, Option.bind_eq_some_iff] at hpa
      obtain ⟨i, _, ha⟩ := hpa
      exact (build_names D hh.chain _ _ (one_wf hh hm ha hc)).2 F hF M (one_has hm ha hc) he

end VE.Readings
