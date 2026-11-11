import VE.Acts.Faithful

/-! The split map is exact and a part is its source's declaration with atom i's act (docs/spec/act-phrases.md 6.6:
`splitMap_exact`, `elaborate_parts`).

The proofs of `wip/ap-3cb` (ap-3c's definitions), ported to the splits read once (ap-3d): every step reads the split
`splitAtoms D` through `elaborateMap_ok`, so `partsOf`, `splitMap`, `splitReg` and `splitNode` take it as `sa`. Both
statements are 6.6's, unchanged; they need no hypothesis on the source: step 3 (`namesOk`) gives the fresh, distinct
generated names, and step 7's backstop gives that no split rule keeps its name. `inj_of_nodup_map`, `mem_splitReg`
and `mem_splitNode` are Faithful.lean's.
-/

namespace VE.Acts
open VE.Norms VE.NormDefaults

/-- Step 3 passed: every part name is fresh (no source regulated predicate, not unspecified) and the part names are
    distinct; every part rule name is fresh (no source rule) and the part rule names are distinct. -/
theorem namesOk_ok {D : ActsDoc} {M : SplitMap} (h : namesOk D M = .ok ()) :
    (∀ q ∈ M.preds.map (·.1), (∀ r ∈ D.U.D.T.regulated, r.name ≠ q) ∧ q ∉ D.U.unspec) ∧ (M.preds.map (·.1)).Nodup ∧
    (∀ n ∈ M.rules.map (·.1), ∀ N ∈ D.U.D.T.nodes, N.name ≠ n) ∧ (M.rules.map (·.1)).Nodup := by
  unfold namesOk at h
  dsimp only at h
  split at h
  · cases h
  · cases h
  next hq hn =>
    have hq := List.find?_eq_none.mp hq
    have hn := List.find?_eq_none.mp hn
    refine ⟨fun q m => ?_, List.nodup_iff_count.mpr fun q => ?_, fun n m N hN e => ?_,
      List.nodup_iff_count.mpr fun n => ?_⟩
    · have := hq q m
      simp only [Bool.or_eq_true, decide_eq_true_eq, List.any_eq_true, beq_iff_eq, List.contains_iff_mem,
        not_or] at this
      exact ⟨fun r hr e => this.1.1.1.2 ⟨r, hr, e⟩, this.1.1.2⟩
    · by_cases m : q ∈ M.preds.map (·.1)
      · have := hq q m
        simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at this
        exact Nat.le_of_not_gt this.1.2
      · rw [List.count_eq_zero_of_not_mem m]; exact Nat.zero_le _
    · have := hn n m
      simp only [Bool.or_eq_true, List.any_eq_true, beq_iff_eq, not_or] at this
      exact this.1.1 ⟨N, hN, e⟩
    · by_cases m : n ∈ M.rules.map (·.1)
      · have := hn n m
        simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at this
        exact Nat.le_of_not_gt this.1.2
      · rw [List.count_eq_zero_of_not_mem m]; exact Nat.zero_le _

/-- A part of `p` is atom i of `p`'s split, i from 1. -/
theorem mem_partsOf {sa : String → Option (List Atom)} {p : String} {x : Atom × Nat} (h : x ∈ partsOf sa p) :
    ∃ atoms, sa p = some atoms ∧ 1 ≤ x.2 ∧ atoms[x.2 - 1]? = some x.1 := by
  unfold partsOf at h
  cases hs : sa p with
  | none => simp [hs] at h
  | some atoms =>
    rw [hs, Option.getD_some, List.mem_zipIdx_iff_le_and_getElem?_sub] at h
    exact ⟨atoms, rfl, h⟩

theorem mem_preds {D : ActsDoc} {sa : String → Option (List Atom)} {x : String × String × Nat} :
    x ∈ (splitMap D sa).preds ↔
      ∃ r ∈ D.U.D.T.regulated, ∃ y ∈ partsOf sa r.name, x = (partPred r.name y.2, r.name, y.2) := by
  simp only [splitMap, List.mem_flatMap, List.mem_map]
  exact ⟨fun ⟨r, hr, y, hy, e⟩ => ⟨r, hr, y, hy, e.symm⟩, fun ⟨r, hr, y, hy, e⟩ => ⟨r, hr, y, hy, e.symm⟩⟩

theorem mem_rules {D : ActsDoc} {sa : String → Option (List Atom)} {x : String × String × Nat} :
    x ∈ (splitMap D sa).rules ↔
      ∃ N ∈ D.U.D.T.nodes, ∃ y ∈ partsOf sa N.pred, x = (partRule N.name y.2, N.name, y.2) := by
  simp only [splitMap, List.mem_flatMap, List.mem_map]
  exact ⟨fun ⟨N, hN, y, hy, e⟩ => ⟨N, hN, y, hy, e.symm⟩, fun ⟨N, hN, y, hy, e⟩ => ⟨N, hN, y, hy, e.symm⟩⟩

theorem splitMap_exact (D : ActsDoc) {U' : VE.NormDefaults.UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    (∀ q, (q ∈ U'.D.T.regulated.map (·.name) ∧ q ∉ D.U.D.T.regulated.map (·.name)) ↔ ∃ p i, (q, p, i) ∈ M.preds) ∧
    (∀ n, (n ∈ U'.D.T.nodes.map (·.name) ∧ n ∉ D.U.D.T.nodes.map (·.name)) ↔ ∃ m i, (n, m, i) ∈ M.rules) ∧
    (∀ q p i, (q, p, i) ∈ M.preds →
      q = partPred p i ∧ p ∈ D.U.D.T.regulated.map (·.name) ∧ p ∉ U'.D.T.regulated.map (·.name) ∧ 1 ≤ i) ∧
    (∀ n m i, (n, m, i) ∈ M.rules →
      n = partRule m i ∧ m ∈ D.U.D.T.nodes.map (·.name) ∧ m ∉ U'.D.T.nodes.map (·.name) ∧ 1 ≤ i) ∧
    (∀ q p i j, (q, p, i) ∈ M.preds → 1 ≤ j → j ≤ i → ∃ q', (q', p, j) ∈ M.preds) ∧
    (M.preds.map (·.1)).Nodup ∧ (M.rules.map (·.1)).Nodup := by
  obtain ⟨_, hn, rfl, rfl, _, hb⟩ := elaborateMap_ok h
  obtain ⟨hq, hqd, hr, hrd⟩ := namesOk_ok hn
  simp only [splitDoc, List.mem_map, List.mem_flatMap, not_exists, not_and]
  refine ⟨fun q => ⟨?_, ?_⟩, fun n => ⟨?_, ?_⟩, fun q p i hm => ?_, fun n m i hm => ?_, fun q p i j hm h1 hj => ?_,
    hqd, hrd⟩
  · rintro ⟨⟨s, ⟨r, hr, hs⟩, rfl⟩, hnot⟩
    rcases mem_splitReg.mp hs with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
    · exact absurd rfl (hnot s hr)
    · exact ⟨r.name, x.2, mem_preds.mpr ⟨r, hr, x, hx, rfl⟩⟩
  · rintro ⟨p, i, hm⟩
    obtain ⟨r, hr', y, hy, e⟩ := mem_preds.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    exact ⟨⟨_, ⟨r, hr', mem_splitReg.mpr (.inr ⟨y, hy, rfl⟩)⟩, rfl⟩,
      fun r' hr'' => (hq _ (List.mem_map_of_mem hm)).1 r' hr''⟩
  · rintro ⟨⟨K, ⟨N, hN, hK⟩, rfl⟩, hnot⟩
    rcases mem_splitNode.mp hK with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
    · exact absurd rfl (hnot K hN)
    · exact ⟨N.name, x.2, mem_rules.mpr ⟨N, hN, x, hx, rfl⟩⟩
  · rintro ⟨m, i, hm⟩
    obtain ⟨N, hN, y, hy, e⟩ := mem_rules.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    exact ⟨⟨_, ⟨N, hN, mem_splitNode.mpr (.inr ⟨y, hy, rfl⟩)⟩, rfl⟩,
      fun N' hN' => hr _ (List.mem_map_of_mem hm) N' hN'⟩
  · obtain ⟨r, hr', y, hy, e⟩ := mem_preds.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    obtain ⟨_, _, h1, _⟩ := mem_partsOf hy
    refine ⟨rfl, ⟨r, hr', rfl⟩, ?_, h1⟩
    rintro s ⟨r', hr'', hs⟩ e
    rcases mem_splitReg.mp hs with ⟨he, rfl⟩ | ⟨x, hx, rfl⟩
    · rw [e] at he; rw [he] at hy; cases hy
    · exact (hq _ (List.mem_map_of_mem (mem_preds.mpr ⟨r', hr'', x, hx, rfl⟩))).1 r hr' e.symm
  · obtain ⟨N, hN, y, hy, e⟩ := mem_rules.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    obtain ⟨_, _, h1, _⟩ := mem_partsOf hy
    refine ⟨rfl, ⟨N, hN, rfl⟩, ?_, h1⟩
    rintro K ⟨N', hN', hK⟩ e
    have := List.all_eq_true.mp hb _ hm
    simp only [Bool.not_eq_true', List.any_eq_false, beq_iff_eq] at this
    exact this K (List.mem_flatMap.mpr ⟨N', hN', hK⟩) e
  · obtain ⟨r, hr', y, hy, e⟩ := mem_preds.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    obtain ⟨atoms, hs, _, ha⟩ := mem_partsOf hy
    have hlt : j - 1 < atoms.length := by
      have := (List.getElem?_eq_some_iff.mp ha).1; omega
    refine ⟨partPred r.name j, mem_preds.mpr ⟨r, hr', (atoms[j - 1], j), ?_, rfl⟩⟩
    rw [partsOf, hs, Option.getD_some, List.mem_zipIdx_iff_le_and_getElem?_sub]
    exact ⟨h1, List.getElem?_eq_getElem hlt⟩

/-- What a part contains (SR9): part i of `p` is `p`'s declaration with atom i's act and the dual's part i, and keeps
    `p`'s sorts, role and completion; part rule i of `N` is `N` on part i with its `over` mapped, every other field
    copied. -/
theorem elaborate_parts (D : ActsDoc) {U' : VE.NormDefaults.UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    (∀ q p i, (q, p, i) ∈ M.preds → ∃ r ∈ D.U.D.T.regulated, r.name = p ∧ ∃ atoms a, splitAtoms D p = some atoms ∧
       atoms[i - 1]? = some a ∧
       U'.D.T.regulated.find? (·.name == q) =
         some { r with name := q, act := some (partAct D.fixed r.role a),
                       permission := r.permission.map (partPred · i) } ∧
       U'.D.E.predicates q = D.U.D.E.predicates p ∧ (q ∈ U'.unspec ↔ p ∈ D.U.unspec)) ∧
    (∀ n m i, (n, m, i) ∈ M.rules → ∃ N ∈ D.U.D.T.nodes, N.name = m ∧
       U'.D.T.nodes.find? (·.name == n) =
         some { N with name := n, pred := partPred N.pred i, over := N.over.map (partRule · i) }) := by
  obtain ⟨_, hn, rfl, rfl, _, _⟩ := elaborateMap_ok h
  obtain ⟨hq, hqd, hr, hrd⟩ := namesOk_ok hn
  refine ⟨fun q p i hm => ?_, fun n m i hm => ?_⟩
  · have hqm := List.mem_map_of_mem (f := (·.1)) hm
    -- the first regulated predicate of the result named `q` is a part, and its map entry is `(q, p, i)`
    obtain ⟨r0, hr0, y0, hy0, e0⟩ := mem_preds.mp hm
    cases hf : (splitDoc D (splitAtoms D) (splitMap D (splitAtoms D))).D.T.regulated.find? (·.name == q) with
    | none =>
      have := List.find?_eq_none.mp hf _ (List.mem_flatMap.mpr ⟨r0, hr0, mem_splitReg.mpr (.inr ⟨y0, hy0, rfl⟩)⟩)
      simp only [Prod.mk.injEq] at e0
      simp [e0.1] at this
    | some z =>
      have hz := List.mem_flatMap.mp (List.mem_of_find?_eq_some hf)
      have hzq : z.name = q := by simpa using List.find?_some hf
      obtain ⟨r, hr', hzr⟩ := hz
      rcases mem_splitReg.mp hzr with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
      · exact absurd hzq ((hq q hqm).1 z hr')
      · have hw := mem_preds.mpr ⟨r, hr', x, hx, rfl⟩
        have e := inj_of_nodup_map hqd hw hm hzq
        simp only [Prod.mk.injEq] at e
        obtain ⟨rfl, rfl, rfl⟩ := e
        obtain ⟨atoms, hs, _, ha⟩ := mem_partsOf hx
        refine ⟨r, hr', rfl, atoms, x.1, hs, ha, rfl, ?_, ?_⟩
        · simp only [splitDoc, splitEnv]
          cases hg : (splitMap D (splitAtoms D)).preds.find? (·.1 == partPred r.name x.2) with
          | none => have := List.find?_eq_none.mp hg _ hm; simp at this
          | some w =>
            have hw' : w.1 = partPred r.name x.2 := by simpa using List.find?_some hg
            rw [inj_of_nodup_map hqd (List.mem_of_find?_eq_some hg) hm hw']
        · simp only [splitDoc, List.mem_flatMap]
          constructor
          · rintro ⟨p', hp', hq'⟩
            unfold partNamesIn at hq'
            split at hq'
            · simp only [List.mem_singleton] at hq'
              exact absurd (hq' ▸ hp') (hq _ hqm).2
            · obtain ⟨w, hwf, hw1⟩ := List.mem_map.mp hq'
              obtain ⟨hwm, hwp⟩ := List.mem_filter.mp hwf
              rw [inj_of_nodup_map hqd hwm hm hw1] at hwp
              simp only [beq_iff_eq] at hwp
              exact hwp ▸ hp'
          · intro hp
            refine ⟨r.name, hp, ?_⟩
            unfold partNamesIn
            have hmf : (partPred r.name x.2, r.name, x.2) ∈ (splitMap D (splitAtoms D)).preds.filter
                (·.2.1 == r.name) := List.mem_filter.mpr ⟨hm, by simp⟩
            split
            next he => rw [he] at hmf; cases hmf
            · exact List.mem_map_of_mem (f := (·.1)) hmf
  · have hnm := List.mem_map_of_mem (f := (·.1)) hm
    obtain ⟨N0, hN0, y0, hy0, e0⟩ := mem_rules.mp hm
    cases hf : (splitDoc D (splitAtoms D) (splitMap D (splitAtoms D))).D.T.nodes.find? (·.name == n) with
    | none =>
      have := List.find?_eq_none.mp hf _ (List.mem_flatMap.mpr ⟨N0, hN0, mem_splitNode.mpr (.inr ⟨y0, hy0, rfl⟩)⟩)
      simp only [Prod.mk.injEq] at e0
      simp [e0.1] at this
    | some z =>
      have hzn : z.name = n := by simpa using List.find?_some hf
      obtain ⟨N, hN, hzN⟩ := List.mem_flatMap.mp (List.mem_of_find?_eq_some hf)
      rcases mem_splitNode.mp hzN with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
      · exact absurd hzn (hr n hnm z hN)
      · have e := inj_of_nodup_map hrd (mem_rules.mpr ⟨N, hN, x, hx, rfl⟩) hm hzn
        simp only [Prod.mk.injEq] at e
        obtain ⟨rfl, rfl, rfl⟩ := e
        exact ⟨N, hN, rfl, rfl⟩

end VE.Acts
