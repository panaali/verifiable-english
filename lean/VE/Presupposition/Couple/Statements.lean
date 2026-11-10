import VE.Presupposition.Couple
import VE.Presupposition.Admit.Statements

/-! # PS-3's statements (docs/spec/presupposition.md 4.8)

`coupled_subset`, `coupled_uniform` and `coupling_complete` word for word; `couplings_spec`: lf-14d's `satisfiesAll`
with the generated `requires` constraints keeps exactly `coupledSet J (couplable groups)`; `sourceChoice_entails`:
the source-identity choice entails every rule goal on its `pre` (`source_identity_entails`).

`coupling_complete` is stated over `admit`, whose table is PS-E1's `candidateTable`: there every cell with two
emitted candidates lists `unconditional`, which is not a root carrier, so no group forms (`groups_admit_nil`) and the
statement holds for every admitted document. If the table gains a cell with two root carriers, that lemma stops
building and the semantic proof of the spec's "Why it holds" is owed then. -/
namespace VE.Presupposition
universe u

/-! ## Lists -/

theorem uniformB_iff (g : Group) (ch : Pick) : uniformB g ch = true ↔ Uniform g ch := by
  simp [uniformB, Uniform, List.all_eq_true]

theorem eq_of_nodup_map {α β : Type} {f : α → β} : ∀ {l : List α}, (l.map f).Nodup →
    ∀ {x y : α}, x ∈ l → y ∈ l → f x = f y → x = y
  | [], _, _, _, hx, _, _ => nomatch hx
  | a :: l, h, x, y, hx, hy, he => by
    rw [List.map_cons, List.nodup_cons] at h
    rcases List.mem_cons.mp hx with hx' | hx' <;> rcases List.mem_cons.mp hy with hy' | hy'
    · rw [hx', hy']
    · subst hx'; exact absurd (he ▸ List.mem_map_of_mem hy') h.1
    · subst hy'; exact absurd (he.symm ▸ List.mem_map_of_mem hx') h.1
    · exact eq_of_nodup_map h.2 hx' hy' he

theorem idxOf_inj {l : List Candidate} {a b : Candidate} (ha : a ∈ l) (hb : b ∈ l) (h : l.idxOf a = l.idxOf b) :
    a = b := by
  induction l with
  | nil => exact nomatch ha
  | cons x xs ih =>
    simp only [List.idxOf_cons, cond_eq_if, beq_iff_eq] at h
    by_cases hxa : x = a <;> by_cases hxb : x = b
    · exact hxa.symm.trans hxb
    · rw [if_pos hxa, if_neg hxb] at h; omega
    · rw [if_neg hxa, if_pos hxb] at h; omega
    · rw [if_neg hxa, if_neg hxb] at h
      exact ih ((List.mem_cons.mp ha).resolve_left (Ne.symm hxa)) ((List.mem_cons.mp hb).resolve_left (Ne.symm hxb)) (by omega)

/-! ## Groups -/

/-- Every member of a group computed by `groups` is an unresolved obligation of the report whose cell is the
    group's candidate list and whose goal is the group's goal. -/
theorem foldl_groups (t : CandidateTable) (P : Checked → Prop) : ∀ (l : List Checked) (acc : List Group),
    (∀ c ∈ l, P c) →
    (∀ g ∈ acc, ∀ o ∈ g.members, ∃ c, P c ∧ c.ob.id = o ∧ t c.ob.row c.pos = g.cands ∧ c.goal = g.goal) →
    ∀ g ∈ l.foldl (fun gs c =>
      if gs.any (fun g => g.goal == c.goal && g.cands == t c.ob.row c.pos) then
        gs.map (fun g => if g.goal == c.goal && g.cands == t c.ob.row c.pos then
          { g with members := g.members ++ [c.ob.id] } else g)
      else gs ++ [({ members := [c.ob.id], goal := c.goal, cands := t c.ob.row c.pos } : Group)]) acc,
    ∀ o ∈ g.members, ∃ c, P c ∧ c.ob.id = o ∧ t c.ob.row c.pos = g.cands ∧ c.goal = g.goal
  | [], acc, _, h => h
  | c :: l, acc, hl, h => by
    refine foldl_groups t P l _ (fun d hd => hl d (List.mem_cons_of_mem _ hd)) ?_
    have hc := hl c List.mem_cons_self
    simp only []
    split
    · intro g' hg' o ho
      obtain ⟨g, hg, rfl⟩ := List.mem_map.mp hg'
      by_cases hm : (g.goal == c.goal && g.cands == t c.ob.row c.pos) = true
      · rw [if_pos hm] at ho ⊢
        simp only [Bool.and_eq_true, beq_iff_eq] at hm
        rcases List.mem_append.mp ho with ho | ho
        · exact h g hg o ho
        · obtain rfl := List.mem_singleton.mp ho
          exact ⟨c, hc, rfl, hm.2.symm, hm.1.symm⟩
      · rw [if_neg hm] at ho ⊢
        exact h g hg o ho
    · intro g hg o ho
      rcases List.mem_append.mp hg with hg | hg
      · exact h g hg o ho
      · obtain rfl := List.mem_singleton.mp hg
        obtain rfl := List.mem_singleton.mp ho
        exact ⟨c, hc, rfl, rfl, rfl⟩

theorem mem_groups {t : CandidateTable} {R : Report} {g : Group} (hg : g ∈ groups t R) :
    2 ≤ g.members.length ∧ g.cands.all Candidate.core = true ∧ ∀ o ∈ g.members, ∃ c ∈ R.checked,
      c.ob.carrier = .unresolved ∧ c.ob.id = o ∧ t c.ob.row c.pos = g.cands ∧ c.goal = g.goal := by
  unfold groups at hg
  obtain ⟨hg, hk⟩ := List.mem_filter.mp hg
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hk
  refine ⟨hk.1, hk.2, fun o ho => ?_⟩
  obtain ⟨c, hc, h⟩ := foldl_groups t (fun c => c ∈ R.checked.filter (fun c => c.ob.carrier == .unresolved))
    _ [] (fun _ h => h) (fun _ h => nomatch h) g hg o ho
  obtain ⟨hc, hu⟩ := List.mem_filter.mp hc
  exact ⟨c, hc, by simpa using hu, h⟩

/-- In a group every member's emitted candidates are the group's (root carriers only, so no in place). -/
theorem emitted_group {t : CandidateTable} {c : Checked} {g : Group} (hcore : g.cands.all Candidate.core = true)
    (hcell : t c.ob.row c.pos = g.cands) : emitted t c = g.cands := by
  unfold emitted; rw [hcell, List.filter_eq_self]
  intro k hk
  have := List.all_eq_true.mp hcore k hk
  cases k <;> simp_all [Candidate.core]

/-! ## `coupled_subset`, `coupled_uniform` -/

theorem coupled_subset (J : List Pick) (gs : List Group) (ch : Pick) (hch : ch ∈ coupledSet J gs) : ch ∈ J :=
  (List.mem_filter.mp hch).1

theorem coupled_uniform (J : List Pick) (gs : List Group) (g : Group) (hg : g ∈ gs) (ch : Pick)
    (hch : ch ∈ coupledSet J gs) : Uniform g ch :=
  (uniformB_iff g ch).mp (List.all_eq_true.mp (List.mem_filter.mp hch).2 g hg)

/-! ## `coupling_complete` -/

/-- PS-E1's table: a cell of root carriers only has at most one candidate. -/
theorem candidateTable_core (row : String) (pc : PositionClass)
    (h : (candidateTable row pc).all Candidate.core = true) : (candidateTable row pc).length ≤ 1 := by
  unfold candidateTable at *
  split <;> simp_all [Candidate.core]

theorem expectedReadings_length {t : CandidateTable} {R : Report} {c : Checked} {rs : List RReading}
    (h : expectedReadings t R c = some rs) : rs.length = (emitted t c).length := by
  unfold expectedReadings at h
  split at h
  · obtain ⟨B, _, rfl⟩ := Option.map_eq_some_iff.mp h; simp
  · obtain ⟨N, _, rfl⟩ := Option.map_eq_some_iff.mp h; simp
  · exact nomatch h

/-- Under `admit` no group forms: every unresolved obligation has two emitted readings (R-6), and PS-E1's only
    such cell lists `unconditional`. -/
theorem groups_admit_nil (D : PDoc) (R : Report) (h : admit D = .ok R) : groups candidateTable R = [] := by
  apply List.eq_nil_iff_forall_not_mem.mpr
  intro g hg
  obtain ⟨hlen, hcore, hm⟩ := mem_groups hg
  obtain ⟨o, ho⟩ : ∃ o, o ∈ g.members := List.exists_mem_of_length_pos (by omega)
  obtain ⟨c, hc, hu, _, hcell, _⟩ := hm o ho
  obtain ⟨_, rs, hrs, h2⟩ := admit_unresolved_readings D R h c hc hu
  have h1 := candidateTable_core c.ob.row c.pos (hcell ▸ hcore)
  rw [expectedReadings_length hrs, emitted_group hcore hcell, ← hcell] at h2
  omega

set_option linter.unusedVariables false in
theorem coupling_complete (D : PDoc) (R : Report) (h : admit D = .ok R) (J : List Pick) (g : Group)
    (hg : g ∈ groups candidateTable R) (hc : couplable J g = true) (ch : Pick) (hch : ch ∈ J)
    (hfit : PickFits candidateTable R ch) :
    rep g ch ∈ J ∧ Uniform g (rep g ch) ∧ SameModels.{u} D R ch (rep g ch) ∧ SameDecides.{u} D R ch (rep g ch) ∧
      ∀ φ, φ ∈ assumptionsUnder D R ch ↔ φ ∈ assumptionsUnder D R (rep g ch) := by
  rw [groups_admit_nil D R h] at hg
  exact nomatch hg

/-! ## `couplings_spec` -/

theorem find_id {R : Report} (hid : (R.checked.map (·.ob.id)).Nodup) {c : Checked} (hc : c ∈ R.checked) :
    R.checked.find? (fun d => d.ob.id == c.ob.id) = some c := by
  cases hf : R.checked.find? (fun d => d.ob.id == c.ob.id) with
  | none =>
    have := List.find?_eq_none.mp hf c hc
    simp at this
  | some d =>
    have he : d.ob.id = c.ob.id := by simpa using List.find?_some hf
    rw [eq_of_nodup_map hid (List.mem_of_find?_eq_some hf) hc he]

theorem pickOf_iff {ch : Pick} (hn : (ch.map (·.1)).Nodup) (o : String) (k : Candidate) :
    pickOf ch o = some k ↔ (o, k) ∈ ch := by
  unfold pickOf
  constructor
  · intro h
    obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.mp h
    have := List.find?_some hx
    simp only [beq_iff_eq] at this
    rw [← this]; exact List.mem_of_find?_eq_some hx
  · intro h
    cases hf : ch.find? (fun x => x.1 == o) with
    | none => have := List.find?_eq_none.mp hf _ h; simp at this
    | some x =>
      have he : x.1 = o := by simpa using List.find?_some hf
      rw [eq_of_nodup_map hn (List.mem_of_find?_eq_some hf) h he]; rfl

/-- `(o, ver o, i)` is chosen exactly when the pick names, for `o`, the candidate at index `i` of `o`'s cell. -/
theorem mem_choiceOf {t : CandidateTable} {R : Report} (hid : (R.checked.map (·.ob.id)).Nodup) (ver : String → Nat)
    (ch : Pick) {c : Checked} (hc : c ∈ R.checked) (i : Nat) :
    (c.ob.id, ver c.ob.id, i) ∈ choiceOf t R ver ch ↔ ∃ k, (c.ob.id, k) ∈ ch ∧ (emitted t c).idxOf k = i := by
  unfold choiceOf
  simp only [List.mem_filterMap]
  constructor
  · rintro ⟨x, hx, he⟩
    obtain ⟨d, hd, he⟩ := Option.map_eq_some_iff.mp he
    simp only [Function.comp, Prod.mk.injEq] at he
    obtain ⟨h1, -, h3⟩ := he
    rw [h1, find_id hid hc] at hd
    obtain rfl := Option.some.inj hd
    refine ⟨x.2, ?_, h3⟩
    rw [← h1]; exact hx
  · rintro ⟨k, hk, rfl⟩
    exact ⟨_, hk, by rw [find_id hid hc]; rfl⟩

/-- A couplable group's constraints hold of a fitting pick exactly when the pick is uniform on the group. -/
theorem groupConstraints_iff {t : CandidateTable} {R : Report} (hid : (R.checked.map (·.ob.id)).Nodup)
    (ver : String → Nat) {g : Group} (hg : g ∈ groups t R) {ch : Pick} (hfit : PickFits t R ch) :
    (groupConstraints ver g).all (fun k => decide (VE.Discourse.Satisfies (choiceOf t R ver ch) k)) = true ↔
      Uniform g ch := by
  obtain ⟨-, hcore, hm⟩ := mem_groups hg
  obtain ⟨hn, hin, hall⟩ := hfit
  -- each member's pick and its index in the shared cell
  have pick : ∀ o ∈ g.members, ∃ c ∈ R.checked, c.ob.id = o ∧ emitted t c = g.cands ∧
      ∃ k, (o, k) ∈ ch ∧ k ∈ g.cands := by
    intro o ho
    obtain ⟨c, hc, hu, rfl, hcell, -⟩ := hm o ho
    obtain ⟨k, hk⟩ := Option.isSome_iff_exists.mp (hall c hc hu)
    have hkm := (pickOf_iff hn _ _).mp hk
    obtain ⟨c', hc', he, -, hke⟩ := hin _ hkm
    obtain rfl := eq_of_nodup_map hid hc' hc he
    exact ⟨c', hc', rfl, emitted_group hcore hcell, k, hkm, emitted_group hcore hcell ▸ hke⟩
  simp only [groupConstraints, List.all_flatMap, List.all_map, List.all_eq_true, List.mem_range,
    Function.comp, decide_eq_true_eq, VE.Discourse.Satisfies, VE.Discourse.chosen]
  constructor
  · intro h o ho o' ho'
    obtain ⟨c, hc, rfl, he, k, hk, hkc⟩ := pick o ho
    obtain ⟨c', hc', rfl, he', k', hk', hkc'⟩ := pick o' ho'
    have hi := h c.ob.id ho c'.ob.id ho' (g.cands.idxOf k) (List.idxOf_lt_length_of_mem hkc)
      ((mem_choiceOf hid ver ch hc _).mpr ⟨k, hk, by rw [he]⟩)
    obtain ⟨k'', hk'', hidx⟩ := (mem_choiceOf hid ver ch hc' _).mp hi
    obtain rfl : k'' = k' := by
      have := (pickOf_iff hn _ _).mpr hk''; rw [(pickOf_iff hn _ _).mpr hk'] at this; exact (Option.some.inj this).symm
    rw [he'] at hidx
    rw [(pickOf_iff hn _ _).mpr hk, (pickOf_iff hn _ _).mpr hk', idxOf_inj hkc hkc' hidx.symm]
  · intro hu o ho o' ho' i _ hi
    obtain ⟨c, hc, rfl, he, -⟩ := pick o ho
    obtain ⟨c', hc', rfl, he', -⟩ := pick o' ho'
    obtain ⟨k, hk, rfl⟩ := (mem_choiceOf hid ver ch hc _).mp hi
    have hk' := (pickOf_iff hn _ _).mp ((hu _ ho _ ho').symm.trans ((pickOf_iff hn _ _).mpr hk))
    exact (mem_choiceOf hid ver ch hc' _).mpr ⟨k, hk', by rw [he, he']⟩

/-- PS-3's constraints, added to lf-14d's manifest, keep exactly the picks of `J` uniform on every couplable
    group: `coupledSet J (couplable groups)`. -/
theorem couplings_spec (t : CandidateTable) (R : Report) (hid : (R.checked.map (·.ob.id)).Nodup)
    (K : VE.Discourse.Manifest) (ver : String → Nat) (J : List Pick) (hJ : ∀ ch ∈ J, PickFits t R ch) :
    J.filter (fun ch => VE.Discourse.satisfiesAll { K with constraints := couplingConstraints ver J (groups t R) }
      (choiceOf t R ver ch)) = coupledSet J ((groups t R).filter (couplable J)) := by
  unfold coupledSet
  apply List.filter_congr
  intro ch hch
  unfold VE.Discourse.satisfiesAll couplingConstraints
  rw [List.all_flatMap]
  apply Bool.eq_iff_iff.mpr
  rw [List.all_eq_true, List.all_eq_true]
  apply forall₂_congr
  intro g hg
  rw [groupConstraints_iff hid ver (List.mem_filter.mp hg).1 (hJ ch hch), uniformB_iff]

/-! ## The source-identity choice -/

theorem sourceChoice_closed {E : VE.Environment} {R : Report} {s : SourceChoice} (hs : s ∈ sourceChoices E R) :
    s.pre.WellFormed E [] ∧ s.label = sourceLabel ∧ 2 ≤ s.members.length := by
  unfold sourceChoices at hs
  obtain ⟨hs, hl⟩ := List.mem_filter.mp hs
  obtain ⟨p, -, rfl⟩ := List.mem_map.mp hs
  simp only [decide_eq_true_eq] at hl
  obtain ⟨c, hc⟩ : ∃ c, c ∈ (R.checked.filter (fun c => c.ob.carrier == .unresolved && c.pos == .ruleAct &&
      c.pre.check E [])).filter (·.pre == p) := by
    cases hf : (R.checked.filter (fun c => c.ob.carrier == .unresolved && c.pos == .ruleAct &&
      c.pre.check E [])).filter (·.pre == p) with
    | nil => simp [hf] at hl
    | cons c _ => exact ⟨c, List.mem_cons_self⟩
  obtain ⟨hc, hp⟩ := List.mem_filter.mp hc
  obtain ⟨-, hk⟩ := List.mem_filter.mp hc
  simp only [Bool.and_eq_true, beq_iff_eq] at hk hp
  exact ⟨hp ▸ (VE.check_iff_wellFormed E [] _).mp hk.2, rfl, hl⟩

/-- Assuming the source-identity choice's `pre` once entails the rule goal of every rule on it. -/
theorem sourceChoice_entails (E : VE.Environment) (R : Report) (s : SourceChoice) (hs : s ∈ sourceChoices E R)
    (S : VE.Structure.{u}) (h : s.pre.denote S []) (r : VE.Norms.Regulated) (N : VE.Norms.Node) :
    (ruleGoal r N s.pre).denote S [] :=
  source_identity_entails E s.pre (sourceChoice_closed hs).1 S h r N

end VE.Presupposition
