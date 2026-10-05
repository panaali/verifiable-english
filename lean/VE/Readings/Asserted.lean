import VE.Readings.SupEnv

/-! The assertions in force of a choice's document are typed over the shared vocabulary (docs/spec/composition-s2.md
1.7 and 8.4, `asserted_shared`).

A fixed assertion uses no name, so it is attached to no set and lies in `free D`, whose chain check types it over
`sharedEnv D`. An assertion candidate of a set declares nothing, so the set's interface is empty, no fixed unit uses
a name the set declares (`interfaceClosed`), and no fixed unit is attached to it; the candidate's own document is
then `free D` with the assertion added, and S1's check of that document types the assertion over `sharedEnv D`.
Both steps read units and sets by their ids, so they need the ids distinct, which `supReady` carries (set ids, and
`unitsDistinct`): with two open sets under one id, `one D s i` and `choiceDoc D c` pick index `i` in both, and an
assertion candidate is then checked beside the other set's rule; with two fixed units under one id, an assertion
unit is attached through the other unit's names and lies in no document `free D` checks (fixture M20). -/
namespace VE.Readings
open VE.Norms (envAt size)
open VE.SoftNorms (soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)

/-- The assertions one item contributes to `build`. -/
def buildAsserted (keep : String → Bool) (pick : ReadingSet → Option Candidate) : Item → List VE.Formula
  | .fixed u c _ => if keep u then asserted c else []
  | .bar _ _ => []
  | .set R => match (pick R).bind (fun a => a.content.map (fun c => (c, a.cites))) with
    | some (c, _) => asserted c
    | none => []

theorem build_snd_fold (keep : String → Bool) (pick : ReadingSet → Option Candidate) :
    ∀ (l : List Item) (acc : RightsDoc × List VE.Formula),
      (l.foldl (buildStep keep pick) acc).2 = acc.2 ++ l.flatMap (buildAsserted keep pick)
  | [], acc => by simp
  | it :: l, acc => by
    rw [List.foldl_cons, build_snd_fold keep pick l, List.flatMap_cons, ← List.append_assoc]
    congr 1
    cases it with
    | fixed u c cs => simp only [buildStep, buildAsserted]; split <;> simp
    | bar u b => simp only [buildStep, buildAsserted]; split <;> simp
    | set R =>
      simp only [buildStep, buildAsserted]
      split <;> rename_i heq <;> simp [heq]

theorem build_snd (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) :
    (build D keep pick).2 = D.items.flatMap (buildAsserted keep pick) := by
  rw [build_eq, build_snd_fold]; simp

theorem asserted_eq {c : Content} {a : VE.Formula} (h : a ∈ asserted c) : c = .assertion a := by
  cases c with
  | assertion φ => simp [asserted] at h; rw [h]
  | _ => simp [asserted] at h

/-- No fixed unit is attached to a set one of whose candidates is an assertion. -/
theorem not_attached_assertion {D : Doc} (hn : (D.sets.map (·.id)).Nodup) (hic : interfaceClosed D = true)
    {R : ReadingSet} (hR : R ∈ D.sets) {a : Candidate} (ha : a ∈ R.candidates) {φ : VE.Formula}
    (hc : a.content = some (.assertion φ)) (u : String) : ¬ Attached D u R.id := by
  intro hA
  generalize ht : R.id = t at hA
  induction hA with
  | direct hu n hn' R' hR' ht' hd =>
    have hRR : R' = R := inj_of_nodup_map hn hR' hR (ht'.trans ht.symm)
    subst hRR
    have hi := (interfaceClosed_spec D).mp hic _ _ _ hu n hn' R' hR' hd
    simp only [interfaceOf, List.mem_filter, List.all_eq_true] at hi
    have := hi.2 a ha
    rw [hc] at this
    simp [Content.declared] at this
  | step _ _ _ _ _ _ ih => exact ih ht

theorem one_assertion_eq {D : Doc} (hn : (D.sets.map (·.id)).Nodup) (hic : interfaceClosed D = true)
    {R : ReadingSet} (hR : R ∈ D.sets) {i : Nat} {a : Candidate} (ha : R.candidates[i]? = some a) {φ : VE.Formula}
    (hc : a.content = some (.assertion φ)) : (one D R.id i).1 = (free D).1 := by
  have hk : ∀ u, ((attached D u).all (· == R.id)) = (attached D u).isEmpty := by
    intro u
    have hno : R.id ∉ attached D u := fun h => not_attached_assertion hn hic hR (List.mem_of_getElem? ha) hc u
      ((attached_iff D u R.id).mp h)
    cases hl : attached D u with
    | nil => rfl
    | cons t l =>
      have : t ≠ R.id := fun e => hno (by rw [hl, e]; simp)
      simp [this]
  apply build_fst_assertions D _ _ _ _ (fun u _ _ _ _ => hk u) (fun u _ _ => hk u)
  · intro R' hR' a' ha' c' hc'
    split at ha'
    · rename_i he
      have hRR : R' = R := inj_of_nodup_map hn (mem_sets.mpr hR') hR (by simpa using he)
      subst hRR
      rw [ha] at ha'
      cases ha'
      rw [hc] at hc'
      cases hc'
      exact ⟨φ, rfl⟩
    · cases ha'
  · intro R' _ a' ha'; cases ha'

theorem fixed_attached_nil {D : Doc} (hr : supReady D = true) {u : String} {φ : VE.Formula}
    {cs : List (String × List String)} (hit : Item.fixed u (.assertion φ) cs ∈ D.items) : attached D u = [] := by
  cases hl : attached D u with
  | nil => rfl
  | cons t l =>
    have hA := (attached_iff D u t).mp (by rw [hl]; simp)
    have hud : (D.items.map itemUnit).Nodup := by
      simp only [supReady, unitsDistinct, Bool.and_eq_true, decide_eq_true_eq] at hr; exact hr.2
    exfalso
    cases hA with
    | direct hu n hn' =>
      have he := inj_of_nodup_map hud hu hit rfl
      simp only [Item.fixed.injEq] at he
      obtain ⟨_, rfl, _⟩ := he
      simp [uses] at hn'
    | step hu _ n hn' =>
      have he := inj_of_nodup_map hud hu hit rfl
      simp only [Item.fixed.injEq] at he
      obtain ⟨_, rfl, _⟩ := he
      simp [uses] at hn'

/-- A fixed assertion is typed over the shared vocabulary. -/
theorem fixed_assertion_shared {D : Doc} (h : WellFormedDoc D = true) (hr : supReady D = true) {u : String}
    {φ : VE.Formula} {cs : List (String × List String)} (hit : Item.fixed u (.assertion φ) cs ∈ D.items) :
    φ.WellFormed (sharedEnv D) [] := by
  obtain ⟨_, _, _, _, hfree, _⟩ := wellFormedDoc_parts h
  apply (VE.check_iff_wellFormed _ _ _).mp
  have hmem : φ ∈ (free D).2 := by
    rw [free, build_snd]
    refine List.mem_flatMap.mpr ⟨_, hit, ?_⟩
    simp [buildAsserted, fixed_attached_nil hr hit, asserted]
  simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hfree
  exact hfree.2 φ hmem

/-- An assertion candidate is typed over the shared vocabulary. -/
theorem cand_assertion_shared {D : Doc} (h : WellFormedDoc D = true) (hr : supReady D = true) {R : ReadingSet}
    (hR : R ∈ D.sets) {i : Nat} {a : Candidate} (ha : R.candidates[i]? = some a) {φ : VE.Formula}
    (hc : a.content = some (.assertion φ)) : φ.WellFormed (sharedEnv D) [] := by
  have hn := supReady_nodup hr
  obtain ⟨_, _, hic, _, _, hone⟩ := wellFormedDoc_parts h
  apply (VE.check_iff_wellFormed _ _ _).mp
  have hlt : i < R.candidates.length := (List.getElem?_eq_some_iff.mp ha).1
  rcases hone R hR i hlt with hnone | hw
  · rw [ha] at hnone; simp [hc] at hnone
  · have hmem : φ ∈ (one D R.id i).2 := by
      rw [one, build_snd]
      refine List.mem_flatMap.mpr ⟨_, mem_sets.mp hR, ?_⟩
      simp [buildAsserted, ha, hc, asserted]
    simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hw
    have := hw.2 φ hmem
    rw [one_assertion_eq hn hic hR ha hc] at this
    exact this

/-- 1.7 and 8.4: every assertion in force of a compatible choice's document is typed over the shared vocabulary.
    Stated with `supReady` (set and unit ids distinct): the statement of 8.4 without it is false of a document
    with two open sets under one id (fixture M20). -/
theorem asserted_shared (D : Doc) (h : WellFormedDoc D = true) (hr : supReady D = true) (c : Choice)
    (hc : Compatible D c) : ∀ a ∈ (choiceDoc D c).2, a.WellFormed (sharedEnv D) [] := by
  have hn := supReady_nodup hr
  obtain ⟨_, _, hic, _, hfree, hone⟩ := wellFormedDoc_parts h
  intro a ha
  rw [choiceDoc, build_snd] at ha
  obtain ⟨it, hit, ha⟩ := List.mem_flatMap.mp ha
  apply (VE.check_iff_wellFormed _ _ _).mp
  cases it with
  | fixed u c' cs =>
    simp only [buildAsserted, if_true] at ha
    have hc' := asserted_eq ha
    subst hc'
    -- the fixed assertion is in free D
    have hmem : a ∈ (free D).2 := by
      rw [free, build_snd]
      refine List.mem_flatMap.mpr ⟨_, hit, ?_⟩
      have : (attached D u).isEmpty = true := by
        cases hl : attached D u with
        | nil => rfl
        | cons t l =>
          have hA := (attached_iff D u t).mp (by rw [hl]; simp)
          have hud : (D.items.map itemUnit).Nodup := by
            simp only [supReady, unitsDistinct, Bool.and_eq_true, decide_eq_true_eq] at hr; exact hr.2
          exfalso
          cases hA with
          | direct hu n hn' =>
            have he := inj_of_nodup_map hud hu hit rfl
            simp only [Item.fixed.injEq] at he
            obtain ⟨_, rfl, _⟩ := he
            simp [uses] at hn'
          | step hu _ n hn' =>
            have he := inj_of_nodup_map hud hu hit rfl
            simp only [Item.fixed.injEq] at he
            obtain ⟨_, rfl, _⟩ := he
            simp [uses] at hn'
      simp [buildAsserted, this, asserted]
    simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hfree
    exact hfree.2 a hmem
  | bar u b => simp [buildAsserted] at ha
  | set R =>
    simp only [buildAsserted] at ha
    split at ha
    · rename_i c'' cs heq
      have hc' := asserted_eq ha
      subst hc'
      simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff, Prod.mk.injEq] at heq
      obtain ⟨cand, ⟨i, _, hpick⟩, _, hcc, rfl, _⟩ := heq
      have hR : R ∈ D.sets := mem_sets.mpr hit
      have hlt : i < R.candidates.length := (List.getElem?_eq_some_iff.mp hpick).1
      rcases hone R hR i hlt with hnone | hw
      · rw [hpick] at hnone; simp [hcc] at hnone
      · have hmem : a ∈ (one D R.id i).2 := by
          rw [one, build_snd]
          refine List.mem_flatMap.mpr ⟨_, hit, ?_⟩
          simp [buildAsserted, hpick, hcc, asserted]
        simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hw
        have := hw.2 a hmem
        rw [one_assertion_eq hn hic hR hpick hcc] at this
        exact this
    · cases ha

end VE.Readings
