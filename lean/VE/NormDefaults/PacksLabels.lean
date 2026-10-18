import VE.Readings.Labels
import VE.Readings.Lines
import VE.NormDefaults.Layered

/-! The labels of soft's extra base premises are distinct (docs/spec/premise-packs.md 2.6).

An exception label is `soft:exception:<rule>:<sufficient|necessary>:<i>` and a coherence label
`soft:coherence:<rule>,<rule>`. Rule names are W1 rule names (`[a-z][a-z0-9-]*`), so they contain neither `:`
nor `,`, and the rule names of a well-formed soft document are distinct: a label is read from the left, run by
run. `zip` keeps a prefix of the exception labels.

`legacy_labels_nodup` (the soft and rights labels together) is not proved here: as stated it is false (fixture
F1′ in `PacksExamples.lean`), and its repair is a DRI decision (pk-1 REPORT). -/
namespace VE.NormDefaults.Packs
open VE.NormDefaults.Wire (softLabelledU)
open VE.SoftNorms (SoftNode SoftDoc soften)

/-! ## Runs -/

/-- Two lists that start with a run followed by the separator `s` agree on the run and the rest. -/
theorem pk_split {s : Char} : ∀ (a a' b b' : List Char), s ∉ a → s ∉ a' → a ++ s :: b = a' ++ s :: b' →
    a = a' ∧ b = b'
  | [], [], b, b', _, _, h => by simpa using h
  | [], c :: a', b, b', _, h', h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    exact absurd (by rw [h.1]; exact List.mem_cons_self) h'
  | c :: a, [], b, b', h, _, h' => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h'
    exact absurd (by rw [← h'.1]; exact List.mem_cons_self) h
  | c :: a, c' :: a', b, b', h, h', he => by
    simp only [List.cons_append, List.cons.injEq] at he
    obtain ⟨rfl, he⟩ := he
    obtain ⟨h1, h2⟩ := pk_split a a' b b' (fun hm => h (List.mem_cons_of_mem _ hm))
      (fun hm => h' (List.mem_cons_of_mem _ hm)) he
    exact ⟨by rw [h1], h2⟩

/-- A W1 rule name has neither `:` nor `,`. -/
theorem pk_ruleName_sep {n : String} (h : VE.Norms.ruleName n = true) : ':' ∉ n.data ∧ ',' ∉ n.data := by
  unfold VE.Norms.ruleName at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨_, h⟩ := h
  have hd : n.toList = n.data := rfl
  rw [hd] at h
  split at h
  · rename_i c0 cs he
    rw [he]
    simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Bool.or_eq_true, beq_iff_eq] at h
    have hc : ∀ c ∈ c0 :: cs, c ≠ ':' ∧ c ≠ ',' := by
      intro c hc
      rcases List.mem_cons.mp hc with rfl | hc
      · constructor <;> intro e <;> subst e <;> exact absurd h.1.1 (by decide)
      · rcases h.2 c hc with (⟨h1, _⟩ | h1) | h1
        · constructor <;> intro e <;> subst e <;> exact absurd h1 (by decide)
        · constructor <;> intro e <;> subst e <;> exact absurd h1 (by decide)
        · constructor <;> intro e <;> subst e <;> exact absurd h1 (by decide)
    exact ⟨fun hm => (hc _ hm).1 rfl, fun hm => (hc _ hm).2 rfl⟩
  · cases h

theorem pk_ruleName {D : SoftDoc} (hs : VE.SoftNorms.WellFormedSoft D = true) {N : SoftNode}
    (hN : N ∈ D.T.nodes) : VE.Norms.ruleName N.name = true := by
  have hv := VE.SoftNorms.softValid_of_wellFormed _ hs
  obtain ⟨hck, _⟩ := (VE.NormDefaults.wellFormed_iff _).mp hv.wf
  obtain ⟨_, _, _, _, _, _, ⟨hrules, _, _⟩, _, _⟩ := hck
  exact (hrules _ (List.mem_map.mpr ⟨N, hN, rfl⟩)).1

theorem pk_zip_fst {α β : Type} : ∀ (l : List α) (m : List β), ((l.zip m).map (·.1)).Sublist l
  | [], _ => by simp
  | _ :: _, [] => by simp
  | a :: l, _ :: m => by
    simp only [List.zip_cons_cons, List.map_cons]
    exact (pk_zip_fst l m).cons₂ a

/-! ## The labels as character lists -/

theorem pk_toString (s : String) : toString s = s := rfl

theorem pk_exc_suff (n : String) (i : Nat) : (s!"soft:exception:{n}:sufficient:{i}").data =
    "soft:exception:".data ++ (n.data ++ ':' :: ("sufficient".data ++ ':' :: Nat.toDigits 10 i)) := by
  simp [String.data_append, pk_toString, VE.Readings.toString_data]

theorem pk_exc_nec (n : String) (i : Nat) : (s!"soft:exception:{n}:necessary:{i}").data =
    "soft:exception:".data ++ (n.data ++ ':' :: ("necessary".data ++ ':' :: Nat.toDigits 10 i)) := by
  simp [String.data_append, pk_toString, VE.Readings.toString_data]

theorem pk_coh (M N : SoftNode) : (VE.SoftNorms.Wire.cohLabel M N).data =
    "soft:coherence:".data ++ (M.name.data ++ ',' :: N.name.data) := by
  simp [VE.SoftNorms.Wire.cohLabel, String.data_append, pk_toString]

/-- The exception labels of one rule. -/
theorem pk_exc_parts {n : String} {s m : Nat} {b : String}
    (h : b ∈ (List.range s).map (fun i => s!"soft:exception:{n}:sufficient:{i}") ++
      (List.range m).map (fun i => s!"soft:exception:{n}:necessary:{i}")) :
    ∃ k i, (k = "sufficient".data ∨ k = "necessary".data) ∧
      b.data = "soft:exception:".data ++ (n.data ++ ':' :: (k ++ ':' :: Nat.toDigits 10 i)) := by
  rcases List.mem_append.mp h with h | h
  · obtain ⟨i, _, rfl⟩ := List.mem_map.mp h
    exact ⟨_, i, Or.inl rfl, pk_exc_suff n i⟩
  · obtain ⟨i, _, rfl⟩ := List.mem_map.mp h
    exact ⟨_, i, Or.inr rfl, pk_exc_nec n i⟩

theorem pk_kind_sep {k : List Char} (hk : k = "sufficient".data ∨ k = "necessary".data) : ':' ∉ k := by
  rcases hk with rfl | rfl <;> decide

theorem pk_exc_inj {n n' : String} {k k' : List Char} {i i' : Nat} (hn : ':' ∉ n.data) (hn' : ':' ∉ n'.data)
    (hk : ':' ∉ k) (hk' : ':' ∉ k')
    (h : "soft:exception:".data ++ (n.data ++ ':' :: (k ++ ':' :: Nat.toDigits 10 i)) =
      "soft:exception:".data ++ (n'.data ++ ':' :: (k' ++ ':' :: Nat.toDigits 10 i'))) :
    n = n' ∧ k = k' ∧ i = i' := by
  obtain ⟨h1, h2⟩ := pk_split _ _ _ _ hn hn' (List.append_cancel_left h)
  obtain ⟨h3, h4⟩ := pk_split _ _ _ _ hk hk' h2
  exact ⟨String.ext h1, h3, VE.Readings.toDigits_inj h4⟩

theorem pk_mem_exc {D : SoftDoc} {x : String} (h : x ∈ VE.SoftNorms.Wire.excLabels D) :
    ∃ k i, ∃ n : String, (k = "sufficient".data ∨ k = "necessary".data) ∧
      x.data = "soft:exception:".data ++ (n.data ++ ':' :: (k ++ ':' :: Nat.toDigits 10 i)) := by
  unfold VE.SoftNorms.Wire.excLabels at h
  obtain ⟨N, _, h⟩ := List.mem_flatMap.mp h
  split at h
  · obtain ⟨k, i, hk, hx⟩ := pk_exc_parts h
    exact ⟨k, i, N.name, hk, hx⟩
  · cases h

theorem pk_exc_ne_coh {X Y : List Char} :
    "soft:exception:".data ++ X ≠ "soft:coherence:".data ++ Y := by
  intro h
  have h1 : "soft:exception:".data = ['s', 'o', 'f', 't', ':', 'e', 'x', 'c', 'e', 'p', 't', 'i', 'o', 'n', ':'] := rfl
  have h2 : "soft:coherence:".data = ['s', 'o', 'f', 't', ':', 'c', 'o', 'h', 'e', 'r', 'e', 'n', 'c', 'e', ':'] := rfl
  rw [h1, h2] at h
  simp at h

/-! ## The soft labels -/

theorem softLabelledU_labels_nodup (U : UDoc) (D : VE.SoftNorms.SoftDoc)
    (hs : VE.SoftNorms.WellFormedSoft D = true) (hw : WellFormedU U = true) :
    ((softLabelledU U D).map (·.1)).Nodup := by
  have hnames := (VE.SoftNorms.softValid_of_wellFormed _ hs).names
  have hnodes : D.T.nodes.Nodup := VE.Readings.nodup_of_map hnames
  have hsep : ∀ N ∈ D.T.nodes, ':' ∉ N.name.data ∧ ',' ∉ N.name.data :=
    fun N hN => pk_ruleName_sep (pk_ruleName hs hN)
  -- exception labels
  have hE : (VE.SoftNorms.Wire.excLabels D).Nodup := by
    unfold VE.SoftNorms.Wire.excLabels
    refine VE.Readings.nodup_flatMap hnodes (fun N hN => ?_) (fun N hN N' hN' b h1 h2 => ?_)
    · split
      · refine List.nodup_append.mpr ⟨?_, ?_, ?_⟩
        · refine VE.Readings.nodup_map_of_inj (fun i i' he => ?_) List.nodup_range
          have := congrArg String.data he
          rw [pk_exc_suff, pk_exc_suff] at this
          exact (pk_exc_inj (hsep N hN).1 (hsep N hN).1 (by decide) (by decide) this).2.2
        · refine VE.Readings.nodup_map_of_inj (fun i i' he => ?_) List.nodup_range
          have := congrArg String.data he
          rw [pk_exc_nec, pk_exc_nec] at this
          exact (pk_exc_inj (hsep N hN).1 (hsep N hN).1 (by decide) (by decide) this).2.2
        · intro x hx y hy he
          obtain ⟨i, _, rfl⟩ := List.mem_map.mp hx
          obtain ⟨i', _, rfl⟩ := List.mem_map.mp hy
          have := congrArg String.data he
          rw [pk_exc_suff, pk_exc_nec] at this
          have := (pk_exc_inj (hsep N hN).1 (hsep N hN).1 (by decide) (by decide) this).2.1
          exact absurd this (by decide)
      · exact List.nodup_nil
    · split at h1
      · split at h2
        · obtain ⟨k, i, hk, hb⟩ := pk_exc_parts h1
          obtain ⟨k', i', hk', hb'⟩ := pk_exc_parts h2
          have := (pk_exc_inj (hsep N hN).1 (hsep N' hN').1 (pk_kind_sep hk) (pk_kind_sep hk')
            (hb.symm.trans hb')).1
          exact VE.Readings.inj_of_nodup_map hnames hN hN' this
        · cases h2
      · cases h1
  -- coherence labels
  have hP : (VE.SoftNorms.collidingPairs D).Nodup := by
    unfold VE.SoftNorms.collidingPairs
    refine (VE.Readings.sortBy_perm _ _).nodup_iff.mpr (VE.Readings.nodup_flatMap hnodes (fun M _ => ?_)
      (fun M _ M' _ b h1 h2 => ?_))
    · refine VE.Readings.nodup_filterMap hnodes (fun N _ N' _ b h1 h2 => ?_)
      split at h1 <;> split at h2 <;> simp only [reduceCtorEq, Option.some.injEq] at h1 h2
      exact (Prod.mk.inj (h1.trans h2.symm)).2
    · obtain ⟨N, _, h1⟩ := List.mem_filterMap.mp h1
      obtain ⟨N', _, h2⟩ := List.mem_filterMap.mp h2
      split at h1 <;> split at h2 <;> simp only [reduceCtorEq, Option.some.injEq] at h1 h2
      exact (Prod.mk.inj (h1.trans h2.symm)).1
  have hcmap : ((VE.SoftNorms.collidingPairs D).map
      (fun (M, N) => (VE.SoftNorms.Wire.cohLabel M N, VE.NormDefaults.Wire.cohPremiseU U D M N))).map (·.1) =
      (VE.SoftNorms.collidingPairs D).map (fun p => VE.SoftNorms.Wire.cohLabel p.1 p.2) := by
    rw [List.map_map]
    exact List.map_congr_left (fun _ _ => rfl)
  have hC : ((VE.SoftNorms.collidingPairs D).map (fun p => VE.SoftNorms.Wire.cohLabel p.1 p.2)).Nodup := by
    refine VE.Readings.nodup_map_on (fun p hp q hq he => ?_) hP
    obtain ⟨hM, hN, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hp
    obtain ⟨hM', hN', _⟩ := VE.SoftNorms.mem_collidingPairs.mp hq
    have := congrArg String.data he
    rw [pk_coh, pk_coh] at this
    obtain ⟨h1, h2⟩ := pk_split _ _ _ _ (hsep _ hM).2 (hsep _ hM').2 (List.append_cancel_left this)
    exact Prod.ext (VE.Readings.inj_of_nodup_map hnames hM hM' (String.ext h1))
      (VE.Readings.inj_of_nodup_map hnames hN hN' (String.ext h2))
  simp only [softLabelledU, List.map_append]
  rw [hcmap]
  refine List.nodup_append.mpr ⟨hE.sublist (pk_zip_fst _ _), hC, ?_⟩
  intro x hx y hy he
  obtain ⟨_, _, _, _, hxd⟩ := pk_mem_exc ((pk_zip_fst _ _).subset hx)
  obtain ⟨p, _, rfl⟩ := List.mem_map.mp hy
  have := congrArg String.data he
  rw [hxd, pk_coh] at this
  exact pk_exc_ne_coh this

end VE.NormDefaults.Packs
