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
        have := hr.1.1.1.1.2 R hR
        simp only [Bool.not_eq_true', List.isEmpty_eq_false_iff] at this
        exact List.length_pos_iff.mpr this.1
      have hcont : (R.candidates[0]?.bind (·.content)).isSome = true := by
        simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
        have := (hr.1.1.1.1.2 R hR)
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

end VE.Readings
