import VE.Readings.SoftSup
import VE.NormDefaults.PacksLabels

/-! SC-11's label mapping (docs/spec/rd-9-soft-chain.md 14.1, 14.4, 14.8): a superposed answer shows each choice's
own labels.

`labelImage N c` pairs each soft label of `c`'s document with the label of the premise it is sent to in the superposed
document: an exception label keeps its role and index under the image name `fmap N.D c`, and a coherence label is
rebuilt with the two image names ascending. `sdShown` reads the used superposed labels back as choice labels of the
compatible choices taking `A`. The label theorems say the first components are the choice's labels
(`labelImage_fst`), the second components superposed labels (`labelImage_snd_mem`), and one superposed label has one
choice label in every choice that has it (`labelImage_functional`, through `fmap_name_cases`: a qualified name fixes
its candidate's author name), and at an encoded filled base a premise and its image hold together (`supLabel_pull`)
while every other superposed premise holds (`supLabel_other`). The last two are `exc_pullF`'s and `coh_pullF`'s
per-premise halves; `SoftSup.lean` keeps those pieces inside its proofs, so they are stated here per premise
(`sel_pullF`, `excPrem_pullF`, `excPrem_dead`), with a premise located by its label (`label_unique`). -/
namespace VE.Readings
open VE.Norms (Sat)
open VE.SoftNorms (SoftNode SoftDoc)
open VE.Rights (RightsDoc correlate)
universe u

/-- One rule's exception labels (the node form of `excLabels`). -/
def nodeExcLabels (M : VE.SoftNorms.SoftNode) : List String :=
  match M.mode, M.exception with
  | .default, some e =>
    (List.range e.sufficient.length).map (fun i => s!"soft:exception:{M.name}:sufficient:{i}") ++
      (List.range e.necessary.length).map (fun i => s!"soft:exception:{M.name}:necessary:{i}")
  | _, _ => []

/-- (choice label, superposed label) of each soft premise of `c`'s document. -/
def labelImage (N : NDoc) (c : Choice) : List (String × String) :=
  let Y := (choiceDoc N.D c).1.soft
  Y.T.nodes.flatMap (fun M => (nodeExcLabels M).zip (nodeExcLabels (fmap N.D c M))) ++
    (VE.SoftNorms.collidingPairs Y).map (fun x =>
      let a := fmap N.D c x.1
      let b := fmap N.D c x.2
      (VE.SoftNorms.Wire.cohLabel x.1 x.2,
        if a.name < b.name then VE.SoftNorms.Wire.cohLabel a b else VE.SoftNorms.Wire.cohLabel b a))

/-- What an answer shows for the superposed labels `used`: choice labels of the compatible choices taking `A`. -/
def sdShown (N : NDoc) (A : Choice) (used : List String) : List String :=
  VE.SoftNorms.dedup (((checkedChoices N.D).filter (fun c => A.all (c.contains ·))).flatMap (fun c =>
    (labelImage N c).filterMap (fun p => if used.contains p.2 then some p.1 else none)))

/-! ## The labels of a soft document, read from its nodes -/

/-- An exception label: `soft:exception:<name>:<kind>:<i>`, as `PacksLabels` reads it. -/
def excData (n : String) (k : List Char) (i : Nat) : List Char :=
  "soft:exception:".data ++ (n.data ++ ':' :: (k ++ ':' :: Nat.toDigits 10 i))

theorem nodeExcLabels_length (M M' : SoftNode) (hm : M'.mode = M.mode)
    (he : M'.exception.map (fun e => (e.sufficient.length, e.necessary.length)) =
      M.exception.map (fun e => (e.sufficient.length, e.necessary.length))) :
    (nodeExcLabels M').length = (nodeExcLabels M).length := by
  unfold nodeExcLabels
  rw [hm]
  cases M.mode <;> cases h1 : M.exception <;> cases h2 : M'.exception <;> simp_all

theorem zip_map_same {α β γ : Type} (f : α → β) (g : α → γ) :
    ∀ l : List α, (l.map f).zip (l.map g) = l.map (fun x => (f x, g x))
  | [] => rfl
  | x :: l => by simp [zip_map_same f g l]

/-- The pairs of two nodes' exception labels with one shape: one kind and one index, two names. -/
theorem mem_zip_nodeExcLabels {M M' : SoftNode} (hm : M'.mode = M.mode)
    (he : M'.exception.map (fun e => (e.sufficient.length, e.necessary.length)) =
      M.exception.map (fun e => (e.sufficient.length, e.necessary.length)))
    {p : String × String} (hp : p ∈ (nodeExcLabels M).zip (nodeExcLabels M')) :
    ∃ k i, (k = "sufficient".data ∨ k = "necessary".data) ∧ p.1.data = excData M.name k i ∧
      p.2.data = excData M'.name k i := by
  unfold nodeExcLabels at hp
  rw [hm] at hp
  cases hmd : M.mode <;> rw [hmd] at hp
  · simp at hp
  cases h1 : M.exception <;> cases h2 : M'.exception <;> rw [h1, h2] at he <;> simp only [h1, h2] at hp
  · simp at hp
  · simp at he
  · simp at he
  rename_i e e'
  simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at he
  rw [he.1, he.2, List.zip_append (by simp), zip_map_same, zip_map_same] at hp
  rcases List.mem_append.mp hp with hp | hp <;> obtain ⟨i, _, rfl⟩ := List.mem_map.mp hp
  · exact ⟨_, i, Or.inl rfl, VE.NormDefaults.Packs.pk_exc_suff _ i, VE.NormDefaults.Packs.pk_exc_suff _ i⟩
  · exact ⟨_, i, Or.inr rfl, VE.NormDefaults.Packs.pk_exc_nec _ i, VE.NormDefaults.Packs.pk_exc_nec _ i⟩

theorem excLabels_nodes (Y : SoftDoc) : VE.SoftNorms.Wire.excLabels Y = Y.T.nodes.flatMap nodeExcLabels := rfl

theorem softXL_labels (N : NDoc) (X : RightsDoc) :
    (softXL N X).map (·.1) = (correlate X).T.nodes.flatMap nodeExcLabels ++
      (VE.SoftNorms.collidingPairs (correlate X)).map (fun x => VE.SoftNorms.Wire.cohLabel x.1 x.2) := by
  simp only [softXL, VE.NormDefaults.Wire.softLabelledU, List.map_append]
  congr 1
  · exact List.map_fst_zip (Nat.le_of_eq (excLabels_length _))
  · rw [List.map_map]; rfl

/-- The colliding pairs of a document's own nodes are colliding pairs of its correlated document. -/
theorem collidingPairs_correlate {X : RightsDoc} {x : SoftNode × SoftNode}
    (hx : x ∈ VE.SoftNorms.collidingPairs X.soft) : x ∈ VE.SoftNorms.collidingPairs (correlate X) := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
  have hd : VE.SoftNorms.dualPerm (correlate X) = VE.SoftNorms.dualPerm X.soft := rfl
  refine VE.SoftNorms.mem_collidingPairs.mpr ⟨?_, ?_, h3, h4, h5, by simpa [VE.SoftNorms.Incompatible, hd] using h6⟩ <;>
    simp only [correlate, List.mem_append] <;> simp [h1, h2]

/-! ## The image of a choice's rule -/

section Image
variable {N : NDoc} (hh : Hyps N.D) (c : Choice)
include hh

theorem fmap_exception_shape {M : SoftNode} (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes) :
    (fmap N.D c M).exception.map (fun e => (e.sufficient.length, e.necessary.length)) =
      M.exception.map (fun e => (e.sufficient.length, e.necessary.length)) := by
  rcases (mem_choiceNodes N.D c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hcc⟩
  · rw [fmap_frame hh c hf]
  · rw [fmap_fixed hh c hu]; rfl
  · rw [fmap_chosen hh c hm hi ha hcc]; cases h : M.exception <;> simp [gateNorm, h]

theorem nodeExcLabels_fmap_length {M : SoftNode} (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes) :
    (nodeExcLabels (fmap N.D c M)).length = (nodeExcLabels M).length :=
  nodeExcLabels_length _ _ (fmap_fields hh c hM).2.2.1 (fmap_exception_shape hh c hM)

/-- The images of a colliding pair of `c`'s document, ascending, are a colliding pair of the superposed one. -/
theorem image_pair_mem {x : SoftNode × SoftNode} (hx : x ∈ VE.SoftNorms.collidingPairs (choiceDoc N.D c).1.soft) :
    (if (fmap N.D c x.1).name < (fmap N.D c x.2).name then (fmap N.D c x.1, fmap N.D c x.2)
      else (fmap N.D c x.2, fmap N.D c x.1)) ∈ VE.SoftNorms.collidingPairs (sup N.D).1.soft := by
  obtain ⟨hM, hM', hMd, hM'd, hlt, hi⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
  have hinc : ∀ P Q : SoftNode, VE.SoftNorms.Incompatible (sup N.D).1.soft P Q =
      VE.SoftNorms.Incompatible (choiceDoc N.D c).1.soft P Q := fun P Q => by
    simp only [VE.SoftNorms.Incompatible, dualPerm_eq c]
  have f1 := fmap_fields hh c hM
  have f2 := fmap_fields hh c hM'
  have hd1 : (fmap N.D c x.1).mode = .default := f1.2.2.1.trans hMd
  have hd2 : (fmap N.D c x.2).mode = .default := f2.2.2.1.trans hM'd
  have hI : VE.SoftNorms.Incompatible (sup N.D).1.soft (fmap N.D c x.1) (fmap N.D c x.2) = true := by
    rw [hinc]; simpa [VE.SoftNorms.Incompatible, f1.1, f1.2.1, f2.1, f2.2.1] using hi
  have hne : (fmap N.D c x.1).name ≠ (fmap N.D c x.2).name := fun h => by
    have := fmap_inj hh c hM hM' (sup_name_inj hh (fmap_mem hh c hM) (fmap_mem hh c hM') h)
    rw [this] at hlt; exact String.lt_irrefl _ hlt
  split
  · exact VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM, fmap_mem hh c hM', hd1, hd2, by assumption, hI⟩
  · rename_i hn
    rcases VE.SoftNorms.str_lt_or_gt _ _ hne with h | h
    · exact absurd h hn
    · exact VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM', fmap_mem hh c hM, hd2, hd1, h,
        by rw [VE.SoftNorms.incompatible_symm]; exact hI⟩

end Image

/-- Where a pair of `labelImage` comes from: an exception label of a rule of `c`'s document with its image's, or a
    colliding pair with its images ascending. -/
theorem mem_labelImage {N : NDoc} {c : Choice} {p : String × String} (hp : p ∈ labelImage N c) :
    (∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, p ∈ (nodeExcLabels M).zip (nodeExcLabels (fmap N.D c M))) ∨
      ∃ x ∈ VE.SoftNorms.collidingPairs (choiceDoc N.D c).1.soft, p.1 = VE.SoftNorms.Wire.cohLabel x.1 x.2 ∧
        p.2 = (let y := if (fmap N.D c x.1).name < (fmap N.D c x.2).name then (fmap N.D c x.1, fmap N.D c x.2)
          else (fmap N.D c x.2, fmap N.D c x.1); VE.SoftNorms.Wire.cohLabel y.1 y.2) := by
  rcases List.mem_append.mp hp with h | h
  · exact Or.inl (List.mem_flatMap.mp h)
  · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp h
    exact Or.inr ⟨x, hx, rfl, by simp only; split <;> rfl⟩

theorem labelImage_fst (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c) :
    (labelImage N c).map (·.1) = (softXL N (choiceDoc N.D c).1).map (·.1) := by
  have hh := hyps_sd hN hs
  rw [softXL_labels, choice_correlate hh]
  simp only [labelImage, List.map_append, List.map_flatMap, List.map_map]
  congr 1
  exact VE.NormDefaults.flatMap_congr_mem (fun M hM => List.map_fst_zip (Nat.le_of_eq (nodeExcLabels_fmap_length hh c hM).symm))

theorem labelImage_snd_mem (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (p : String × String) (hp : p ∈ labelImage N c) :
    p.2 ∈ (softXL N (sup N.D).1).map (·.1) := by
  have hh := hyps_sd hN hs
  rw [softXL_labels, sup_correlate hh]
  rcases mem_labelImage hp with ⟨M, hM, hz⟩ | ⟨x, hx, -, h2⟩
  · exact List.mem_append_left _ (List.mem_flatMap.mpr ⟨_, fmap_mem hh c hM, (List.of_mem_zip hz).2⟩)
  · exact List.mem_append_right _ (List.mem_map.mpr ⟨_, image_pair_mem hh c hx, h2.symm⟩)

/-- Two rules of compatible choices whose images have one name have one author name. -/
theorem fmap_name_det {N : NDoc} (hh : Hyps N.D) {c₁ c₂ : Choice} {M₁ M₂ : SoftNode}
    (h₁ : M₁ ∈ (choiceDoc N.D c₁).1.soft.T.nodes) (h₂ : M₂ ∈ (choiceDoc N.D c₂).1.soft.T.nodes)
    (he : (fmap N.D c₁ M₁).name = (fmap N.D c₂ M₂).name) : M₁.name = M₂.name := by
  rcases fmap_name_cases hh c₁ h₁ with ⟨r₁, e₁⟩ | ⟨k₁, e₁⟩ <;>
    rcases fmap_name_cases hh c₂ h₂ with ⟨r₂, e₂⟩ | ⟨k₂, e₂⟩ <;> rw [e₁, e₂] at he
  · exact he
  · exact absurd he.symm (qualify_ne r₁)
  · exact absurd he (qualify_ne r₂)
  · exact (qualify_inj he).2

/-- The names of the superposed document's rules have no `:` and no `,`. -/
theorem sup_name_sep {N : NDoc} (hh : Hyps N.D) {K : SoftNode} (hK : K ∈ (sup N.D).1.soft.T.nodes) :
    ':' ∉ K.name.data ∧ ',' ∉ K.name.data := by
  have h := (sup_wellFormed N.D hh.sp).2
  rw [sup_correlate hh] at h
  exact VE.NormDefaults.Packs.pk_ruleName_sep (VE.NormDefaults.Packs.pk_ruleName h hK)

theorem labelImage_functional (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c₁ c₂ : Choice) (h₁ : Compatible N.D c₁)
    (h₂ : Compatible N.D c₂) (l₁ l₂ s : String) (hp₁ : (l₁, s) ∈ labelImage N c₁) (hp₂ : (l₂, s) ∈ labelImage N c₂) :
    l₁ = l₂ := by
  have hh := hyps_sd hN hs
  rcases mem_labelImage hp₁ with ⟨M₁, hM₁, hz₁⟩ | ⟨x₁, hx₁, e₁, f₁⟩ <;>
    rcases mem_labelImage hp₂ with ⟨M₂, hM₂, hz₂⟩ | ⟨x₂, hx₂, e₂, f₂⟩
  · obtain ⟨k₁, i₁, hk₁, a₁, b₁⟩ := mem_zip_nodeExcLabels (fmap_fields hh c₁ hM₁).2.2.1
      (fmap_exception_shape hh c₁ hM₁) hz₁
    obtain ⟨k₂, i₂, hk₂, a₂, b₂⟩ := mem_zip_nodeExcLabels (fmap_fields hh c₂ hM₂).2.2.1
      (fmap_exception_shape hh c₂ hM₂) hz₂
    obtain ⟨hn, hk, hi⟩ := VE.NormDefaults.Packs.pk_exc_inj (sup_name_sep hh (fmap_mem hh c₁ hM₁)).1
      (sup_name_sep hh (fmap_mem hh c₂ hM₂)).1 (VE.NormDefaults.Packs.pk_kind_sep hk₁)
      (VE.NormDefaults.Packs.pk_kind_sep hk₂) (b₁.symm.trans b₂)
    apply String.ext
    simp only at a₁ a₂
    rw [a₁, a₂, fmap_name_det hh hM₁ hM₂ hn, hk, hi]
  · obtain ⟨k₁, i₁, -, -, b₁⟩ := mem_zip_nodeExcLabels (fmap_fields hh c₁ hM₁).2.2.1
      (fmap_exception_shape hh c₁ hM₁) hz₁
    simp only at f₂ b₁
    split at f₂ <;> exact absurd (b₁.symm.trans (by rw [f₂, VE.NormDefaults.Packs.pk_coh]))
      VE.NormDefaults.Packs.pk_exc_ne_coh
  · obtain ⟨k₂, i₂, -, -, b₂⟩ := mem_zip_nodeExcLabels (fmap_fields hh c₂ hM₂).2.2.1
      (fmap_exception_shape hh c₂ hM₂) hz₂
    simp only at f₁ b₂
    split at f₁ <;> exact absurd (b₂.symm.trans (by rw [f₁, VE.NormDefaults.Packs.pk_coh]))
      VE.NormDefaults.Packs.pk_exc_ne_coh
  · -- one coherence label: the ascending image names agree, so the author names agree as a pair
    have hm₁ := image_pair_mem hh c₁ hx₁
    have hm₂ := image_pair_mem hh c₂ hx₂
    obtain ⟨hA₁, hB₁, -, -, hlt₁, -⟩ := VE.SoftNorms.mem_collidingPairs.mp hx₁
    obtain ⟨hA₂, hB₂, -, -, hlt₂, -⟩ := VE.SoftNorms.mem_collidingPairs.mp hx₂
    have key : ∀ (y₁ y₂ : SoftNode × SoftNode), y₁ ∈ VE.SoftNorms.collidingPairs (sup N.D).1.soft →
        y₂ ∈ VE.SoftNorms.collidingPairs (sup N.D).1.soft →
        VE.SoftNorms.Wire.cohLabel y₁.1 y₁.2 = VE.SoftNorms.Wire.cohLabel y₂.1 y₂.2 →
        y₁.1.name = y₂.1.name ∧ y₁.2.name = y₂.2.name := by
      intro y₁ y₂ hy₁ hy₂ he
      obtain ⟨hP₁, hQ₁, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hy₁
      obtain ⟨hP₂, hQ₂, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hy₂
      have := congrArg String.data he
      rw [VE.NormDefaults.Packs.pk_coh, VE.NormDefaults.Packs.pk_coh] at this
      obtain ⟨h1, h2⟩ := VE.NormDefaults.Packs.pk_split _ _ _ _ (sup_name_sep hh hP₁).2 (sup_name_sep hh hP₂).2
        (List.append_cancel_left this)
      exact ⟨String.ext h1, String.ext h2⟩
    have hk := key _ _ hm₁ hm₂ (f₁.symm.trans f₂)
    simp only at e₁ e₂
    rw [e₁, e₂]
    unfold VE.SoftNorms.Wire.cohLabel
    have lt_asymm : ∀ a b : String, a < b → b < a → False := fun a b h h' =>
      String.lt_irrefl _ (String.lt_trans h h')
    split at hk <;> split at hk <;> simp only at hk <;> obtain ⟨n₁, n₂⟩ := hk
    · rw [fmap_name_det hh hA₁ hA₂ n₁, fmap_name_det hh hB₁ hB₂ n₂]
    · exact (lt_asymm _ _ hlt₂ (by rw [← fmap_name_det hh hA₁ hB₂ n₁, ← fmap_name_det hh hB₁ hA₂ n₂]; exact hlt₁)).elim
    · exact (lt_asymm _ _ hlt₂ (by rw [← fmap_name_det hh hB₁ hA₂ n₁, ← fmap_name_det hh hA₁ hB₂ n₂]; exact hlt₁)).elim
    · rw [fmap_name_det hh hB₁ hB₂ n₁, fmap_name_det hh hA₁ hA₂ n₂]

/-! ## A label names one premise

A soft label is read from the left: `soft:exception:<rule>:<kind>:<i>` or `soft:coherence:<rule>,<rule>`. In a
document whose rule names are distinct and have no `:` and no `,`, it names one premise (`label_unique`). A choice's
document need not pass the soft check here, so its names are read through their images (`choice_name_sep`). -/

theorem mem_zip_get {α β : Type} {L₁ : List α} {L₂ : List β} {x : α} {y : β} (h : (x, y) ∈ L₁.zip L₂) :
    ∃ j : Nat, L₁[j]? = some x ∧ L₂[j]? = some y := by
  obtain ⟨j, hj⟩ := List.mem_iff_getElem?.mp h
  exact ⟨j, (List.getElem?_zip_eq_some.mp hj)⟩

theorem zip_flatMap_of_length {α β γ : Type} (f : α → List β) (g : α → List γ) :
    ∀ l : List α, (∀ x ∈ l, (f x).length = (g x).length) →
      (l.flatMap f).zip (l.flatMap g) = l.flatMap (fun x => (f x).zip (g x))
  | [], _ => rfl
  | x :: l, h => by
    simp only [List.flatMap_cons]
    rw [List.zip_append (h x List.mem_cons_self),
      zip_flatMap_of_length f g l (fun y hy => h y (List.mem_cons_of_mem _ hy))]

theorem nodeExcLabels_length_prem (D : SoftDoc) (K : SoftNode) :
    (nodeExcLabels K).length = (VE.SoftNorms.excPremisesOf D K).length := by
  unfold nodeExcLabels VE.SoftNorms.excPremisesOf
  cases K.mode <;> cases K.exception <;> simp

/-- The label at position `j` of a rule's exception labels: its kind and index. -/
theorem nodeExcLabels_get {K : SoftNode} {j : Nat} {l : String} (h : (nodeExcLabels K)[j]? = some l) :
    ∃ e, K.mode = .default ∧ K.exception = some e ∧
      ((j < e.sufficient.length ∧ l.data = excData K.name "sufficient".data j) ∨
        (e.sufficient.length ≤ j ∧ l.data = excData K.name "necessary".data (j - e.sufficient.length))) := by
  unfold nodeExcLabels at h
  cases hm : K.mode <;> cases he : K.exception <;> simp only [hm, he, List.getElem?_nil, reduceCtorEq] at h
  rename_i e
  refine ⟨e, rfl, rfl, ?_⟩
  by_cases hj : j < e.sufficient.length
  · rw [List.getElem?_append_left (by simpa using hj)] at h
    simp only [List.getElem?_map, List.getElem?_range hj, Option.map_some, Option.some.injEq] at h
    exact Or.inl ⟨hj, by rw [← h]; exact VE.NormDefaults.Packs.pk_exc_suff _ _⟩
  · rw [List.getElem?_append_right (by simpa using hj)] at h
    simp only [List.length_map, List.length_range, List.getElem?_map, Option.map_eq_some_iff] at h
    obtain ⟨i, hi, rfl⟩ := h
    rw [(List.getElem?_eq_some_iff.mp hi).2.symm] at *
    simp only [List.getElem_range]
    exact Or.inr ⟨by omega, VE.NormDefaults.Packs.pk_exc_nec _ _⟩

/-- One rule, two positions, one label: one position. -/
theorem nodeExcLabels_pos {K : SoftNode} (hK : ':' ∉ K.name.data) {j j' : Nat} {l : String}
    (h : (nodeExcLabels K)[j]? = some l) (h' : (nodeExcLabels K)[j']? = some l) : j = j' := by
  obtain ⟨e, -, he, h1⟩ := nodeExcLabels_get h
  obtain ⟨e', -, he', h2⟩ := nodeExcLabels_get h'
  rw [he] at he'; cases he'
  have inj := fun {k k' : List Char} {i i' : Nat} (hk : k = "sufficient".data ∨ k = "necessary".data)
      (hk' : k' = "sufficient".data ∨ k' = "necessary".data) (hd : excData K.name k i = excData K.name k' i') =>
    VE.NormDefaults.Packs.pk_exc_inj hK hK (VE.NormDefaults.Packs.pk_kind_sep hk) (VE.NormDefaults.Packs.pk_kind_sep hk') hd
  rcases h1 with ⟨hj, d⟩ | ⟨hj, d⟩ <;> rcases h2 with ⟨hj', d'⟩ | ⟨hj', d'⟩
  · exact (inj (.inl rfl) (.inl rfl) (d.symm.trans d')).2.2
  · exact absurd (inj (.inl rfl) (.inr rfl) (d.symm.trans d')).2.1 (by decide)
  · exact absurd (inj (.inr rfl) (.inl rfl) (d.symm.trans d')).2.1 (by decide)
  · have := (inj (.inr rfl) (.inr rfl) (d.symm.trans d')).2.2; omega

/-- Where a labelled soft premise comes from: a rule's exception premise at a position, or a colliding pair. -/
theorem mem_softLabelledU {U : VE.NormDefaults.UDoc} {D : SoftDoc} {l : String} {a : VE.Formula}
    (h : (l, a) ∈ VE.NormDefaults.Wire.softLabelledU U D) :
    (∃ K ∈ D.T.nodes, ∃ j : Nat, (nodeExcLabels K)[j]? = some l ∧ (VE.SoftNorms.excPremisesOf D K)[j]? = some a) ∨
      ∃ x ∈ VE.SoftNorms.collidingPairs D, l = VE.SoftNorms.Wire.cohLabel x.1 x.2 ∧
        a = VE.NormDefaults.Wire.cohPremiseU U D x.1 x.2 := by
  rcases List.mem_append.mp h with h | h
  · rw [excLabels_nodes, VE.SoftNorms.excPremises, zip_flatMap_of_length _ _ _
      (fun K _ => nodeExcLabels_length_prem D K)] at h
    obtain ⟨K, hK, hz⟩ := List.mem_flatMap.mp h
    exact Or.inl ⟨K, hK, mem_zip_get hz⟩
  · obtain ⟨x, hx, he⟩ := List.mem_map.mp h
    exact Or.inr ⟨x, hx, (Prod.mk.inj he).1.symm, (Prod.mk.inj he).2.symm⟩

theorem exc_mem_softLabelledU (U : VE.NormDefaults.UDoc) {D : SoftDoc} {K : SoftNode} (hK : K ∈ D.T.nodes) {j : Nat}
    {l : String} {a : VE.Formula} (hl : (nodeExcLabels K)[j]? = some l)
    (ha : (VE.SoftNorms.excPremisesOf D K)[j]? = some a) : (l, a) ∈ VE.NormDefaults.Wire.softLabelledU U D := by
  refine List.mem_append_left _ ?_
  rw [excLabels_nodes, VE.SoftNorms.excPremises, zip_flatMap_of_length _ _ _
    (fun K _ => nodeExcLabels_length_prem D K)]
  exact List.mem_flatMap.mpr ⟨K, hK, List.mem_iff_getElem?.mpr ⟨j, List.getElem?_zip_eq_some.mpr ⟨hl, ha⟩⟩⟩

theorem label_unique {U : VE.NormDefaults.UDoc} {D : SoftDoc}
    (hsep : ∀ K ∈ D.T.nodes, ':' ∉ K.name.data ∧ ',' ∉ K.name.data)
    (hinj : ∀ K ∈ D.T.nodes, ∀ K' ∈ D.T.nodes, K.name = K'.name → K = K') {l : String} {a a' : VE.Formula}
    (h : (l, a) ∈ VE.NormDefaults.Wire.softLabelledU U D) (h' : (l, a') ∈ VE.NormDefaults.Wire.softLabelledU U D) :
    a = a' := by
  have get : ∀ {K : SoftNode} {j : Nat} {l : String}, (nodeExcLabels K)[j]? = some l →
      ∃ k i, (k = "sufficient".data ∨ k = "necessary".data) ∧ l.data = excData K.name k i := fun hl => by
    obtain ⟨_, -, -, ⟨-, d⟩ | ⟨-, d⟩⟩ := nodeExcLabels_get hl
    · exact ⟨_, _, .inl rfl, d⟩
    · exact ⟨_, _, .inr rfl, d⟩
  have exc_data : ∀ {K : SoftNode} {j : Nat} {l : String}, (nodeExcLabels K)[j]? = some l →
      ∃ X, l.data = "soft:exception:".data ++ X := fun hl => by
    obtain ⟨_, _, -, d⟩ := get hl; exact ⟨_, d⟩
  rcases mem_softLabelledU h with ⟨K, hK, j, hl, ha⟩ | ⟨x, hx, hl, rfl⟩ <;>
    rcases mem_softLabelledU h' with ⟨K', hK', j', hl', ha'⟩ | ⟨x', hx', hl', rfl⟩
  · obtain ⟨k, i, hk, d⟩ := get hl
    obtain ⟨k', i', hk', d'⟩ := get hl'
    have hn := (VE.NormDefaults.Packs.pk_exc_inj (hsep K hK).1 (hsep K' hK').1 (VE.NormDefaults.Packs.pk_kind_sep hk)
      (VE.NormDefaults.Packs.pk_kind_sep hk') (d.symm.trans d')).1
    obtain rfl := hinj K hK K' hK' hn
    obtain rfl := nodeExcLabels_pos (hsep K hK).1 hl hl'
    rw [ha] at ha'; exact Option.some.inj ha'
  · obtain ⟨X, hX⟩ := exc_data hl
    exact absurd (hX.symm.trans (by rw [hl', VE.NormDefaults.Packs.pk_coh])) VE.NormDefaults.Packs.pk_exc_ne_coh
  · obtain ⟨X, hX⟩ := exc_data hl'
    exact absurd (hX.symm.trans (by rw [hl, VE.NormDefaults.Packs.pk_coh])) VE.NormDefaults.Packs.pk_exc_ne_coh
  · have := congrArg String.data (hl.symm.trans hl')
    rw [VE.NormDefaults.Packs.pk_coh, VE.NormDefaults.Packs.pk_coh] at this
    obtain ⟨hx1, hx2⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
    obtain ⟨hx1', hx2', _⟩ := VE.SoftNorms.mem_collidingPairs.mp hx'
    obtain ⟨n1, n2⟩ := VE.NormDefaults.Packs.pk_split _ _ _ _ (hsep _ hx1).2 (hsep _ hx1').2
      (List.append_cancel_left this)
    rw [hinj _ hx1 _ hx1' (String.ext n1), hinj _ hx2.1 _ hx2' (String.ext n2)]

theorem qualify_data_mem {k : Nat} {n : String} {ch : Char} (h : ch ∈ n.data) : ch ∈ (qualify k n).data := by
  simp only [qualify, String.data_append]
  exact List.mem_append_right _ h

/-- A rule of a choice's document has a name with no `:` and no `,`: its image's, or a suffix of it. -/
theorem choice_name_sep {N : NDoc} (hh : Hyps N.D) (c : Choice) {M : SoftNode}
    (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes) : ':' ∉ M.name.data ∧ ',' ∉ M.name.data := by
  have h := sup_name_sep hh (fmap_mem hh c hM)
  rcases fmap_name_cases hh c hM with ⟨-, e⟩ | ⟨k, e⟩ <;> rw [e] at h
  · exact h
  · exact ⟨fun hc => h.1 (qualify_data_mem hc), fun hc => h.2 (qualify_data_mem hc)⟩

theorem softXL_choice_unique {N : NDoc} (hh : Hyps N.D) (c : Choice) {l : String} {a a' : VE.Formula}
    (h : (l, a) ∈ softXL N (choiceDoc N.D c).1) (h' : (l, a') ∈ softXL N (choiceDoc N.D c).1) : a = a' := by
  unfold softXL at h h'
  rw [choice_correlate hh] at h h'
  exact label_unique (fun _ hK => choice_name_sep hh c hK) (fun _ hK _ hK' hn => choice_name_inj hh c hK hK' hn) h h'

theorem softXL_sup_unique {N : NDoc} (hh : Hyps N.D) {l : String} {a a' : VE.Formula}
    (h : (l, a) ∈ softXL N (sup N.D).1) (h' : (l, a') ∈ softXL N (sup N.D).1) : a = a' := by
  unfold softXL at h h'
  rw [sup_correlate hh] at h h'
  exact label_unique (fun _ hK => sup_name_sep hh hK) (fun _ hK _ hK' hn => sup_name_inj hh hK hK' hn) h h'

/-! ## One premise at an encoded filled base (the per-premise halves of `exc_pullF` and `coh_pullF`) -/

section Pull
open VE.NormDefaults (fill)
variable {N : NDoc} (hh : Hyps N.D) {c : Choice} (hc : Compatible N.D c) (hN : WellFormedSD N = true)
  (hsu : VE.NormDefaults.WellFormedU (supU N) = true) {B : VE.Structure.{u}}
  (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (he : Encodes N.D c B)

include hh hc hN hsu hB he in
/-- A rule's selection on the superposed side and its preimage's on the choice's side agree (`coh_pullF`'s F1-F3);
    a rule that is no image selects nowhere (F4). -/
theorem sel_pullF :
    (∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, ∀ vs : List B.Carrier,
      VE.TupleTyped B (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred) vs →
      ((VE.Defaults.selU (supU N) (sup N.D).1.soft (fmap N.D c M)).denote B (VE.Norms.tupleVal vs) ↔
        (VE.Defaults.selU (choiceU N c) (choiceDoc N.D c).1.soft M).denote (pullF N c B) (VE.Norms.tupleVal vs))) ∧
    (∀ K ∈ (sup N.D).1.soft.T.nodes, (∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M ≠ K) →
      ∀ vs : List B.Carrier, VE.TupleTyped B (VE.SoftNorms.sortsOf (sup N.D).1.soft K.pred) vs →
      ¬ (VE.Defaults.selU (supU N) (sup N.D).1.soft K).denote B (VE.Norms.tupleVal vs)) := by
  have hX := fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)
  have hY := fillLite_choiceSD hh hc hN hsu
  have hvX := valid_fill_supU hsu
  have hvY := valid_fill_choiceSD hh hc hN hsu
  have hsv := sup_softValid hh
  have hcX : VE.Norms.ConstantsTyped (fill (supU N)) B := hB.1.1
  have hcB : ∀ x s, (fill (supU N)).E.constants x = some s → ∃ v, B.constant x = some v :=
    fun x s hx => (hcX x s hx).imp fun _ h => h.1
  have hcY : VE.Norms.ConstantsTyped (fill (choiceU N c)) (pullF N c B) := fun x s hx =>
    hcX x s (constants_choiceSD hh x s hx)
  have hS := encodes_canon_fill hh hsu B he
  have F1 : ∀ K ∈ (sup N.D).1.soft.T.nodes, ∀ vs, VE.TupleTyped B (VE.SoftNorms.sortsOf (sup N.D).1.soft K.pred) vs →
      ((VE.Defaults.selU (supU N) (sup N.D).1.soft K).denote B (VE.Norms.tupleVal vs) ↔
        VE.SoftNorms.SelectsSoftD (sup N.D).1.soft (VE.SoftNorms.canon (fill (supU N)) B) (VE.Norms.tupleVal vs)
          (VE.SoftNorms.fuel (sup N.D).1.soft) K) :=
    fun K hK vs hvs => selU_canon (supU_D hh) hX hvX hcX hK (hsv.predReg K hK) vs hvs
  refine ⟨fun M hM vs hvs => ?_, fun K hK hext vs hvs hsel => ?_⟩
  · have hss : VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c M).pred =
        VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred := by rw [(fmap_fields hh c hM).1, sortsOf_eq c]
    have hreg := hsv.predReg _ (fmap_mem hh c hM)
    rw [(fmap_fields hh c hM).1, sup_reg, ← choice_reg c] at hreg
    refine (F1 _ (fmap_mem hh c hM) vs (hss ▸ hvs)).trans (Iff.trans ?_ (selU_canon (choiceU_D hh c) hY hvY hcY hM hreg vs
      ((VE.Norms.tupleTyped_relation B _ _ vs).mpr hvs)).symm)
    refine (sim_selects_fuel (faithful_sim hh hc _ hS (VE.Norms.tupleVal vs)) M hM).trans ?_
    show _ ↔ VE.SoftNorms.SelectsSoftD (choiceDoc N.D c).1.soft (VE.SoftNorms.canon (fill (choiceU N c)) (pullF N c B))
      (VE.Norms.tupleVal vs) (VE.SoftNorms.fuel (choiceDoc N.D c).1.soft) M
    rw [← VE.SoftNorms.selectsPrime_denote, ← VE.SoftNorms.selectsPrime_denote]
    refine denote_relation_congr _ (pull N.D c (VE.SoftNorms.canon (fill (supU N)) B))
      (VE.SoftNorms.canon (fill (choiceU N c)) (pullF N c B)).relation
      (fun p ss hp ws hws => ?_) _ _ _ ((VE.check_iff_wellFormed _ _ _).mpr (choice_selTyped hh hc hM))
    have hp' := envAt_sub hp
    refine (pull_pullF hh (c := c) (VE.SoftNorms.canon (fill (supU N)) B) hp' ws).trans
      (pullF_canon hh hc hN hsu B hcB he ?_ ws hws)
    rw [← choiceU_D hh] at hp'
    rw [VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_off _ (not_unsaid_lite hY hp')]; exact hp'
  · have hdead := dead_extra hh hc _ hS (VE.Norms.tupleVal vs) hK hext
    have ha := ((F1 K hK vs hvs).mp hsel).1
    unfold VE.SoftNorms.AppliesSoftD at ha
    split at ha
    · exact hdead ha
    · exact hdead (effD_eligible ha).2.1

include hh hc hN hsu hB he in
/-- The coherence premise of a superposed colliding pair of images, at `B`, is the choice's at `pullF N c B`. -/
theorem cohPair_pullF {M M' : SoftNode} (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes)
    (hM' : M' ∈ (choiceDoc N.D c).1.soft.T.nodes)
    (hp : (fmap N.D c M, fmap N.D c M') ∈ VE.SoftNorms.collidingPairs (sup N.D).1.soft) :
    (VE.NormDefaults.Wire.cohPremiseU (supU N) (sup N.D).1.soft (fmap N.D c M) (fmap N.D c M')).denote B [] ↔
      (VE.NormDefaults.Wire.cohPremiseU (choiceU N c) (choiceDoc N.D c).1.soft M M').denote (pullF N c B) [] := by
  have hS := sel_pullF hh hc hN hsu hB he
  have hsrt := (sup_softValid hh).cpSorts _ hp
  have hss : ∀ K ∈ (choiceDoc N.D c).1.soft.T.nodes, VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c K).pred =
      VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft K.pred := fun K hK => by
    rw [(fmap_fields hh c hK).1, sortsOf_eq c]
  simp only [VE.Defaults.cohPremiseU_selU, VE.Norms.bindAll_denote_nil, VE.SoftNorms.actSorts]
  rw [hss M hM]
  refine forall_congr' fun vs => ?_
  rw [show VE.TupleTyped (pullF N c B) (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred) vs ↔
    VE.TupleTyped B (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred) vs from
      VE.Norms.tupleTyped_relation B _ _ vs]
  refine imp_congr_right fun hvs => not_congr (and_congr (hS.1 M hM vs hvs) (hS.1 M' hM' vs ?_))
  rw [← hss M' hM']; simp only at hsrt; rw [← hsrt, hss M hM]; exact hvs

include hh hc hN hsu hB he in
/-- The coherence premise of a superposed colliding pair with a member that is no image holds at `B`. -/
theorem cohPair_dead {P Q : SoftNode} (hp : (P, Q) ∈ VE.SoftNorms.collidingPairs (sup N.D).1.soft)
    (hd : (∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M ≠ P) ∨
      ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M ≠ Q) :
    (VE.NormDefaults.Wire.cohPremiseU (supU N) (sup N.D).1.soft P Q).denote B [] := by
  have hS := sel_pullF hh hc hN hsu hB he
  obtain ⟨hP, hQ, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hp
  have hsrt := (sup_softValid hh).cpSorts _ hp
  simp only at hsrt
  simp only [VE.Defaults.cohPremiseU_selU, VE.Norms.bindAll_denote_nil, VE.SoftNorms.actSorts]
  rintro vs hvs ⟨h1, h2⟩
  rcases hd with hd | hd
  · exact hS.2 P hP hd vs hvs h1
  · exact hS.2 Q hQ hd vs (hsrt ▸ hvs) h2

include hh hc hsu hB he in
/-- An exception premise of a rule's image, at `B`, is the rule's own at the same position, at `pullF N c B`
    (`exc_pullF`'s `img`, per premise). -/
theorem excPrem_pullF {M : SoftNode} (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes) {j : Nat} {a a' : VE.Formula}
    (ha : (VE.SoftNorms.excPremisesOf (choiceDoc N.D c).1.soft M)[j]? = some a)
    (ha' : (VE.SoftNorms.excPremisesOf (sup N.D).1.soft (fmap N.D c M))[j]? = some a') :
    a'.denote B [] ↔ a.denote (pullF N c B) [] := by
  obtain ⟨g, hg, hex⟩ := fmap_exception_eq hh he hM
  obtain ⟨hpred, _, hmode, _, _, _⟩ := fmap_fields hh c hM
  have hss : VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c M).pred =
      VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred := by rw [hpred, sortsOf_eq c]
  unfold VE.SoftNorms.excPremisesOf at ha ha'
  rw [hmode, hex] at ha'
  cases hm : M.mode <;> rw [hm] at ha ha'
  · simp at ha
  cases hE : M.exception <;> rw [hE] at ha ha'
  · simp at ha
  rename_i e
  have hC : ∀ C ∈ e.sufficient ++ e.necessary, ∀ ρ, C.denote B ρ ↔ C.denote (pullF N c B) ρ :=
    fun C hC ρ => by obtain ⟨Γ, hw⟩ := choice_exc_typed hh c hM hE C hC; exact pullF_denote_frame hh B C Γ hw ρ
  have hx := fun ρ => exceptedF_pullF hh B hM hm ρ
  simp only [Option.map_some] at ha'
  by_cases hj : j < e.sufficient.length
  · rw [List.getElem?_append_left (by simpa using hj)] at ha
    rw [List.getElem?_append_left (by simpa using hj)] at ha'
    simp only [List.getElem?_map, List.getElem?_eq_getElem hj, Option.map_some, Option.some.injEq] at ha ha'
    subst ha ha'
    simp only [VE.Norms.bindAll_denote_nil, hss]
    refine forall_congr' fun vs => ?_
    rw [← VE.Norms.tupleTyped_relation B (pullF N c B).relation]
    refine imp_congr_right fun _ => ?_
    simp only [VE.Formula.denote]
    rw [hx, hg, hC _ (List.mem_append_left _ (List.getElem_mem hj))]
  · rw [List.getElem?_append_right (by simpa using hj)] at ha
    rw [List.getElem?_append_right (by simpa using hj)] at ha'
    simp only [List.length_map, List.getElem?_map, Option.map_eq_some_iff] at ha ha'
    obtain ⟨C, hCm, rfl⟩ := ha
    obtain ⟨C', hCm', rfl⟩ := ha'
    rw [hCm] at hCm'; cases hCm'
    simp only [VE.Norms.bindAll_denote_nil, hss]
    refine forall_congr' fun vs => ?_
    rw [← VE.Norms.tupleTyped_relation B (pullF N c B).relation]
    refine imp_congr_right fun _ => ?_
    simp only [VE.Formula.denote]
    rw [hx, hC _ (List.mem_append_right _ (List.mem_of_getElem? hCm))]

include hh hc he in
/-- Every exception premise of a superposed rule that is no image holds where the bits encode `c` and the slot holds:
    a sufficient condition is gated by the unchosen candidate's bit, and the slot's quiet premise empties its
    `excepted` table (`exc_pullF`'s second half, per rule). -/
theorem excPrem_dead (hsl : Sat B (slotP N.D)) {K : SoftNode} (hK : K ∈ (sup N.D).1.soft.T.nodes)
    (hext : ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M ≠ K) :
    ∀ a ∈ VE.SoftNorms.excPremisesOf (sup N.D).1.soft K, a.denote B [] := by
  have hq : Sat B (choicePremises N.D) := fun a ha => hsl a (by
    simp only [slotP, slotLabelled, choicePremises, VE.Compose.Labelled.formulas, List.map_append,
      List.mem_append] at ha ⊢
    exact Or.inl (Or.inr ha))
  rcases (mem_supNodes N.D K).mp hK with hf | ⟨u, F, cs, hu, rfl⟩ | ⟨m, hm, i', a, K₀, ha, hac, rfl⟩
  · exact absurd (fmap_frame hh c hf) (hext K ((mem_choiceNodes N.D c K).mpr (Or.inl hf)))
  · exact absurd (fmap_fixed hh c hu) (hext F ((mem_choiceNodes N.D c F).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))))
  obtain ⟨i, hci, _⟩ := choice_index hh hc hm
  have hii : c.index N.D.sets[m].id ≠ some i' := fun h => by
    rw [hci] at h; cases h
    exact hext K₀ ((mem_choiceNodes N.D c K₀).mpr (Or.inr (Or.inr ⟨m, hm, i', a, hci, ha, hac⟩)))
      (fmap_chosen hh c hm hci ha hac)
  have hilt : i' < N.D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp ha).1
  have hoff := pattern_off hh hc he hm hilt hii
  unfold VE.SoftNorms.excPremisesOf
  cases hmK : (gateNorm N.D m i' K₀).mode with
  | strict => simp
  | default =>
    cases hE : K₀.exception with
    | none => simp [gateNorm, hE]
    | some e =>
      simp only [gateNorm, hE, Option.map_some, List.forall_mem_append, List.forall_mem_map,
        VE.Norms.bindAll_denote_nil]
      refine ⟨fun C _ vs _ h => absurd h.2 (hoff _), fun C _ vs hvs hx => absurd hx ?_⟩
      let M' := gateNorm N.D m i' K₀
      have hd : M'.mode = .default := hmK
      have hg : (GenKey.excepted M'.name none, VE.SoftNorms.exceptedName M',
          VE.SoftNorms.sortsOf (correlate (sup N.D).1) M'.pred) ∈ genKeys (sup N.D).1 := by
        obtain ⟨_, _, hb, hs⟩ := noRights_parts hh.noRights
        have hlines : VE.Rights.linesOf (sup N.D).1 = [] := by simp [VE.Rights.linesOf, hs, VE.Rights.linesAux]
        have hk : keyedNodes (sup N.D).1 = (sup N.D).1.soft.T.nodes.map (fun N => (N, N.name, none)) := by
          simp [keyedNodes, hlines, VE.Rights.barNodes_nil _ hb]
        simp only [genKeys, hk, List.mem_append]
        refine Or.inl (Or.inl (Or.inl (Or.inl (Or.inl ?_))))
        exact List.mem_map.mpr ⟨(M', M'.name, none), List.mem_filter.mpr ⟨List.mem_map.mpr ⟨M', hK, rfl⟩,
          by simp [hd]⟩, rfl⟩
      have ho : origin N.D M'.name = some (m, i') :=
        origin_qualify hm hilt ha hac (d := ("rule", K₀.name)) (by simp [VE.Compose.Content.declared])
      have hown : owners N.D (GenKey.excepted M'.name none) = [[(m, i')]] := by simp [owners, ho]
      have hQ := quiet_holds hq hg (by simp [fixedGenerated, hown]) (by
        simp only [hown, List.mem_singleton]; rintro o rfl x hx
        simp only [List.mem_singleton] at hx; subst hx; exact ⟨hm, by rw [setSize_eq hm]; exact hilt⟩)
      simp only [quietFormula, hown, VE.Norms.bindAll_denote_nil, sup_correlate hh] at hQ
      intro hx'
      have h1 := hQ vs hvs hx'
      simp only [List.map_cons, List.map_nil, disj_denote, conj_denote, List.mem_singleton, forall_eq,
        exists_eq_left] at h1
      unfold atomAt at h1
      rw [List.getElem?_eq_getElem hm, choiceAtom_rho] at h1
      simp only [Option.map_some, Option.getD_some] at h1
      rw [choiceAtom_eq (findIdx_of_nodup hh.nodup hm) (by rw [setSize_eq hm]; exact hilt)] at h1
      exact hoff _ h1

end Pull

theorem cohPremise_swap (U : VE.NormDefaults.UDoc) (D : SoftDoc) {P Q : SoftNode}
    (h : VE.SoftNorms.sortsOf D P.pred = VE.SoftNorms.sortsOf D Q.pred) (S : VE.Structure.{u}) :
    (VE.NormDefaults.Wire.cohPremiseU U D P Q).denote S [] ↔ (VE.NormDefaults.Wire.cohPremiseU U D Q P).denote S [] := by
  simp only [VE.Defaults.cohPremiseU_selU, VE.Norms.bindAll_denote_nil, VE.SoftNorms.actSorts, h]
  exact forall_congr' fun _ => imp_congr_right fun _ => not_congr and_comm

theorem supLabel_pull (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (VE.NormDefaults.fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (l s : String) (a a' : VE.Formula) (hp : (l, s) ∈ labelImage N c)
    (ha : (l, a) ∈ softXL N (choiceDoc N.D c).1) (ha' : (s, a') ∈ softXL N (sup N.D).1) :
    a'.denote B [] ↔ a.denote (pullF N c B) [] := by
  have _ := hsl
  have hh := hyps_sd hN hs
  have mc : ∀ {l a}, (l, a) ∈ VE.NormDefaults.Wire.softLabelledU (choiceU N c) (choiceDoc N.D c).1.soft →
      (l, a) ∈ softXL N (choiceDoc N.D c).1 := fun h => by unfold softXL; rw [choice_correlate hh]; exact h
  have ms : ∀ {l a}, (l, a) ∈ VE.NormDefaults.Wire.softLabelledU (supU N) (sup N.D).1.soft →
      (l, a) ∈ softXL N (sup N.D).1 := fun h => by unfold softXL; rw [sup_correlate hh]; exact h
  rcases mem_labelImage hp with ⟨M, hM, hz⟩ | ⟨x, hx, h1, h2⟩
  · obtain ⟨j, hl, hs'⟩ := mem_zip_get hz
    have hj : j < (VE.SoftNorms.excPremisesOf (choiceDoc N.D c).1.soft M).length := by
      rw [← nodeExcLabels_length_prem]; exact (List.getElem?_eq_some_iff.mp hl).1
    have hj' : j < (VE.SoftNorms.excPremisesOf (sup N.D).1.soft (fmap N.D c M)).length := by
      rw [← nodeExcLabels_length_prem]; exact (List.getElem?_eq_some_iff.mp hs').1
    rw [softXL_choice_unique hh c ha (mc (exc_mem_softLabelledU _ hM hl (List.getElem?_eq_getElem hj))),
      softXL_sup_unique hh ha' (ms (exc_mem_softLabelledU _ (fmap_mem hh c hM) hs' (List.getElem?_eq_getElem hj')))]
    exact excPrem_pullF hh hc hsu hB he hM (List.getElem?_eq_getElem hj) (List.getElem?_eq_getElem hj')
  · obtain ⟨hM, hM', -⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
    have hy := image_pair_mem hh c hx
    simp only at h1 h2
    rw [softXL_choice_unique hh c ha (mc (List.mem_append_right _ (List.mem_map.mpr ⟨x, hx, by rw [h1]⟩))),
      softXL_sup_unique hh ha' (ms (List.mem_append_right _ (List.mem_map.mpr ⟨_, hy, by rw [h2]⟩)))]
    have hss : ∀ K ∈ (choiceDoc N.D c).1.soft.T.nodes, VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c K).pred =
        VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft K.pred := fun K hK => by
      rw [(fmap_fields hh c hK).1, sortsOf_eq c]
    by_cases hlt : (fmap N.D c x.1).name < (fmap N.D c x.2).name
    · rw [if_pos hlt] at hy ⊢
      exact cohPair_pullF hh hc hN hsu hB he hM hM' hy
    · rw [if_neg hlt] at hy ⊢
      have hsrt := (sup_softValid hh).cpSorts _ hy
      simp only at hsrt
      refine (cohPair_pullF hh hc hN hsu hB he hM' hM hy).trans (cohPremise_swap _ _ ?_ _)
      rw [← hss _ hM', ← hss _ hM]; exact hsrt

theorem supLabel_other (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (VE.NormDefaults.fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (s : String) (a' : VE.Formula) (ha' : (s, a') ∈ softXL N (sup N.D).1)
    (hn : ∀ p ∈ labelImage N c, p.2 ≠ s) :
    a'.denote B [] := by
  have hh := hyps_sd hN hs
  unfold softXL at ha'
  rw [sup_correlate hh] at ha'
  rcases mem_softLabelledU ha' with ⟨K, hK, j, hl, hpa⟩ | ⟨x, hx, hl, rfl⟩
  · by_cases him : ∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M = K
    · obtain ⟨M, hM, rfl⟩ := him
      have hj : j < (nodeExcLabels M).length := by
        rw [← nodeExcLabels_fmap_length hh c hM]; exact (List.getElem?_eq_some_iff.mp hl).1
      exact absurd rfl (hn (_, s) (List.mem_append_left _ (List.mem_flatMap.mpr ⟨M, hM,
        List.mem_iff_getElem?.mpr ⟨j, List.getElem?_zip_eq_some.mpr ⟨List.getElem?_eq_getElem hj, hl⟩⟩⟩)))
    · exact excPrem_dead hh hc he hsl hK (fun M hM h => him ⟨M, hM, h⟩) a' (List.mem_of_getElem? hpa)
  · by_cases him : (∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M = x.1) ∧
        ∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M = x.2
    · obtain ⟨⟨M, hM, e1⟩, ⟨M', hM', e2⟩⟩ := him
      exfalso
      obtain ⟨-, -, hPd, hQd, hlt, hi⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
      have f1 := fmap_fields hh c hM
      have f2 := fmap_fields hh c hM'
      have hne : M.name ≠ M'.name := fun h => by
        rw [choice_name_inj hh c hM hM' h, e2] at e1; rw [e1] at hlt; exact String.lt_irrefl _ hlt
      have hI : ∀ P Q : SoftNode, VE.SoftNorms.Incompatible (sup N.D).1.soft P Q =
          VE.SoftNorms.Incompatible (choiceDoc N.D c).1.soft P Q := fun P Q => by
        simp only [VE.SoftNorms.Incompatible, dualPerm_eq c]
      have hi' : VE.SoftNorms.Incompatible (choiceDoc N.D c).1.soft M M' = true := by
        rw [← e1, ← e2, hI] at hi; simpa [VE.SoftNorms.Incompatible, f1.1, f1.2.1, f2.1, f2.2.1] using hi
      have hMd : M.mode = .default := by rw [← f1.2.2.1, e1]; exact hPd
      have hM'd : M'.mode = .default := by rw [← f2.2.2.1, e2]; exact hQd
      rw [← e1, ← e2] at hlt
      rcases VE.SoftNorms.str_lt_or_gt _ _ hne with h | h
      · refine hn _ (List.mem_append_right _ (List.mem_map.mpr ⟨(M, M'),
          VE.SoftNorms.mem_collidingPairs.mpr ⟨hM, hM', hMd, hM'd, h, hi'⟩, rfl⟩)) ?_
        simp only [hl, e1, e2]; rw [if_pos (by rw [← e1, ← e2]; exact hlt)]
      · refine hn _ (List.mem_append_right _ (List.mem_map.mpr ⟨(M', M),
          VE.SoftNorms.mem_collidingPairs.mpr ⟨hM', hM, hM'd, hMd, h,
            by rw [VE.SoftNorms.incompatible_symm]; exact hi'⟩, rfl⟩)) ?_
        have hng : ¬ (fmap N.D c M').name < (fmap N.D c M).name := fun h' =>
          String.lt_irrefl _ (String.lt_trans hlt h')
        simp only [hl, e1, e2]; rw [if_neg (by rw [← e1, ← e2]; exact hng)]
    · have hd : (∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M ≠ x.1) ∨
          ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M ≠ x.2 := by
        by_cases h1 : ∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M = x.1
        · exact Or.inr fun M hM h => him ⟨h1, M, hM, h⟩
        · exact Or.inl fun M hM h => h1 ⟨M, hM, h⟩
      exact cohPair_dead hh hc hN hsu hB he hx hd

/-! ## The shown labels -/

theorem sdShown_mem (N : NDoc) (hr : supReady N.D = true) (hle : (checkedChoices N.D).length ≤ maxChoiceChecks)
    (A : Choice) (used : List String) (l : String) (hl : l ∈ sdShown N A used) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ l ∈ (softXL N (choiceDoc N.D c).1).map (·.1) := by
  simp only [sdShown, VE.SoftNorms.mem_dedup, List.mem_flatMap, List.mem_filter, List.mem_filterMap,
    List.all_eq_true, List.contains_iff_mem] at hl
  obtain ⟨c, ⟨hc, hA⟩, p, hp, hpl⟩ := hl
  refine ⟨c, compatible_of_mem_search N.D _ c hc, hA, ?_⟩
  split at hpl
  · cases hpl
    rw [softXL_labels]
    rcases mem_labelImage hp with ⟨M, hM, hz⟩ | ⟨x, hx, h1, -⟩
    · refine List.mem_append_left _ (List.mem_flatMap.mpr ⟨M, ?_, (List.of_mem_zip hz).1⟩)
      simp only [correlate, List.mem_append]; exact Or.inl (Or.inr hM)
    · exact List.mem_append_right _ (List.mem_map.mpr ⟨x, collidingPairs_correlate hx, h1.symm⟩)
  · cases hpl

theorem sdShown_image (N : NDoc) (hr : supReady N.D = true) (hle : (checkedChoices N.D).length ≤ maxChoiceChecks)
    (A : Choice) (used : List String) (c : Choice) (hc : Compatible N.D c) (hA : ∀ x ∈ A, x ∈ c)
    (l s : String) (hp : (l, s) ∈ labelImage N c) (hu : s ∈ used) :
    l ∈ sdShown N A used := by
  have hlt : (search N.D N.D.sets [] (maxChoiceChecks + 1)).length < maxChoiceChecks + 1 := by
    have := hle; simp only [checkedChoices] at this; omega
  simp only [sdShown, VE.SoftNorms.mem_dedup, List.mem_flatMap, List.mem_filter, List.mem_filterMap,
    List.all_eq_true, List.contains_iff_mem]
  exact ⟨c, ⟨(search_spec N.D hr _ hlt c).mpr hc, hA⟩, (l, s), hp, by simp [hu]⟩

theorem fillLabels_choice (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c) :
    VE.NormDefaults.Admission.fillLabels (choiceU N c) = VE.NormDefaults.Admission.fillLabels (supU N) := by
  have hh := hyps_sd hN hs
  unfold VE.NormDefaults.Admission.fillLabels
  rw [choiceU_D hh, supU_D hh]
  simp only [VE.SoftNorms.soften, regs_eq c]
  rfl

end VE.Readings
