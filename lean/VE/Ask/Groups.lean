import VE.Ask.Sources

/-! Readings: relevant sets and groups (docs/spec/question-answering.md 5.2; plan 4.4, D9, R7, Q2.2).

A row's key is its lead, and for yes and no its cited sources. `relevantSets` drops, greedily in set order, every
open set whose readings never change the key, then checks the result over all the rows (else every set). A group is
a key with an assignment on the relevant sets; every row is in exactly one group (`groups_cover`), every row of a
group has the group's key and assignment (`group_rows`), and every row that reads the relevant sets as a group
names them has that group's key (`group_claim`), which is what an R1 block claims. -/

namespace VE.Ask
open VE.Readings

def assignment (sets : List String) (r : Row) : List (String × Option Nat) := sets.map fun s => (s, r.choice.index s)

def separates (rows : List Row) (key : Row → Lead × List Source) (sets : List String) : Bool :=
  rows.all fun r => rows.all fun r' => assignment sets r != assignment sets r' || key r == key r'

/-- Greedy, in set order: a set is dropped while the rest still separates; checked, else every set. -/
def relevantSets (ids : List String) (rows : List Row) (key : Row → Lead × List Source) : List String :=
  let greedy := ids.foldl (fun S s => if separates rows key (S.erase s) then S.erase s else S) ids
  if separates rows key greedy then greedy else ids

theorem separates_sound {rows : List Row} {key : Row → Lead × List Source} {sets : List String}
    (h : separates rows key sets = true) :
    ∀ r ∈ rows, ∀ r' ∈ rows, assignment sets r = assignment sets r' → key r = key r' := by
  intro r hr r' hr' ha
  simp only [separates, List.all_eq_true, Bool.or_eq_true, bne_iff_ne, ne_eq, beq_iff_eq] at h
  rcases h r hr r' hr' with h | h
  · exact absurd ha h
  · exact h

theorem assignment_eq {sets : List String} {r r' : Row} (h : ∀ s ∈ sets, r.choice.index s = r'.choice.index s) :
    assignment sets r = assignment sets r' := by
  simp only [assignment]
  exact List.map_congr_left (fun s hs => by rw [h s hs])

theorem lookup_assignment (c : Choice) (s : String) :
    ∀ sets : List String, s ∈ sets → (sets.map fun t => (t, c.index t)).lookup s = some (c.index s)
  | [], hs => by cases hs
  | t :: ts, hs => by
    simp only [List.map_cons, List.lookup_cons]
    by_cases hts : s = t
    · subst hts; simp
    · have he : (s == t) = false := by simpa using hts
      rw [he]
      exact lookup_assignment c s ts (by simpa [hts] using hs)

theorem index_of_assignment {sets : List String} {r r' : Row} (h : assignment sets r = assignment sets r') :
    ∀ s ∈ sets, r.choice.index s = r'.choice.index s := by
  intro s hs
  have hl := congrArg (fun l => l.lookup s) h
  simp only [assignment] at hl
  rw [lookup_assignment r.choice s sets hs, lookup_assignment r'.choice s sets hs] at hl
  exact Option.some.inj hl

/-- A choice whose keys are exactly the nodup `ids` is fixed by its indices on them. -/
theorem choice_eq_of_index : ∀ (ids : List String) (c c' : Choice), ids.Nodup → c.map (·.1) = ids →
    c'.map (·.1) = ids → (∀ s ∈ ids, c.index s = c'.index s) → c = c'
  | [], c, c', _, h, h', _ => by
    cases c with
    | nil => cases c' with
      | nil => rfl
      | cons _ _ => simp at h'
    | cons _ _ => simp at h
  | s :: ss, c, c', hn, h, h', hi => by
    cases c with
    | nil => simp at h
    | cons x xs =>
      cases c' with
      | nil => simp at h'
      | cons y ys =>
        simp only [List.map_cons, List.cons.injEq] at h h'
        obtain ⟨hx, hxs⟩ := h
        obtain ⟨hy, hys⟩ := h'
        have hs := hi s List.mem_cons_self
        simp only [Choice.index, List.find?_cons, hx, hy, beq_self_eq_true, Option.map_some,
          Option.some.injEq] at hs
        have hns : s ∉ ss := (List.nodup_cons.mp hn).1
        have hrest : xs = ys := choice_eq_of_index ss xs ys (List.nodup_cons.mp hn).2 hxs hys (fun t ht => by
          have := hi t (List.mem_cons_of_mem _ ht)
          have hts : t ≠ s := fun e => hns (e ▸ ht)
          have h1 : (x.1 == t) = false := by rw [hx]; simpa using Ne.symm hts
          have h2 : (y.1 == t) = false := by rw [hy]; simpa using Ne.symm hts
          simpa [Choice.index, List.find?_cons, h1, h2] using this)
        obtain ⟨x1, x2⟩ := x
        obtain ⟨y1, y2⟩ := y
        simp only at hx hy hs
        subst hx hy hs hrest
        rfl

theorem relevantSets_sound : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
    ids.Nodup → (∀ r ∈ rows, r.choice.map (·.1) = ids) →
    (∀ r ∈ rows, ∀ r' ∈ rows, r.choice = r'.choice → key r = key r') →
    ∀ r ∈ rows, ∀ r' ∈ rows, (∀ s ∈ relevantSets ids rows key, r.choice.index s = r'.choice.index s) →
      key r = key r' := by
  intro ids rows key hn hids hfun r hr r' hr' hagree
  unfold relevantSets at hagree
  dsimp only at hagree
  split at hagree
  · rename_i hs
    exact separates_sound hs r hr r' hr' (assignment_eq hagree)
  · exact hfun r hr r' hr' (choice_eq_of_index ids _ _ hn (hids r hr) (hids r' hr') hagree)

structure Group where
  lead : Lead
  cited : List Source
  on : List (String × Option Nat)
  rows : List Row

/-- One group per distinct key and assignment on the relevant sets, in order of first row. -/
def groups (ids : List String) (rows : List Row) (key : Row → Lead × List Source) : List Group :=
  let sets := relevantSets ids rows key
  rows.foldl (fun gs r =>
    let k := key r
    let a := assignment sets r
    if gs.any (fun g => (g.lead, g.cited) == k && g.on == a) then
      gs.map (fun g => if (g.lead, g.cited) == k && g.on == a then { g with rows := g.rows ++ [r] } else g)
    else gs ++ [⟨k.1, k.2, a, [r]⟩]) []

/-- The fold's step, named. -/
def addRow (sets : List String) (key : Row → Lead × List Source) (gs : List Group) (r : Row) : List Group :=
  let k := key r
  let a := assignment sets r
  if gs.any (fun g => (g.lead, g.cited) == k && g.on == a) then
    gs.map (fun g => if (g.lead, g.cited) == k && g.on == a then { g with rows := g.rows ++ [r] } else g)
  else gs ++ [⟨k.1, k.2, a, [r]⟩]

theorem groups_eq (ids : List String) (rows : List Row) (key : Row → Lead × List Source) :
    groups ids rows key = rows.foldl (addRow (relevantSets ids rows key) key) [] := rfl

/-- A group's identity: its key and assignment. -/
def Group.tag (g : Group) : (Lead × List Source) × List (String × Option Nat) := ((g.lead, g.cited), g.on)

/-- What the fold keeps true: every row of a group has its tag, the groups have distinct tags, every group has a
    row, and the rows of the groups are exactly the rows seen. -/
structure Inv (sets : List String) (key : Row → Lead × List Source) (seen : List Row) (gs : List Group) : Prop where
  tagged : ∀ g ∈ gs, ∀ r ∈ g.rows, (key r, assignment sets r) = g.tag
  distinct : gs.Pairwise (fun g h => g.tag ≠ h.tag)
  nonempty : ∀ g ∈ gs, g.rows ≠ []
  covered : ∀ r ∈ seen, ∃ g ∈ gs, r ∈ g.rows
  only : ∀ g ∈ gs, ∀ r ∈ g.rows, r ∈ seen

theorem match_iff (sets : List String) (key : Row → Lead × List Source) (r : Row) (g : Group) :
    ((g.lead, g.cited) == key r && g.on == assignment sets r) = true ↔ g.tag = (key r, assignment sets r) := by
  simp [Group.tag, Prod.ext_iff]

theorem inv_addRow {sets : List String} {key : Row → Lead × List Source} {seen : List Row} {gs : List Group}
    (h : Inv sets key seen gs) (r : Row) : Inv sets key (seen ++ [r]) (addRow sets key gs r) := by
  unfold addRow
  dsimp only
  split
  · rename_i hany
    obtain ⟨g₀, hg₀, hm₀⟩ := List.any_eq_true.mp hany
    have ht₀ := (match_iff sets key r g₀).mp hm₀
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro g hg x hx
      obtain ⟨g', hg', rfl⟩ := List.mem_map.mp hg
      by_cases hm : ((g'.lead, g'.cited) == key r && g'.on == assignment sets r) = true
      · rw [if_pos hm] at hx ⊢
        have ht := (match_iff sets key r g').mp hm
        simp only [List.mem_append, List.mem_singleton] at hx
        rcases hx with hx | rfl
        · exact h.tagged g' hg' x hx
        · exact ht.symm
      · rw [if_neg hm] at hx ⊢
        exact h.tagged g' hg' x hx
    · refine List.Pairwise.map _ ?_ h.distinct
      intro a b hab
      split <;> split <;> simpa [Group.tag] using hab
    · intro g hg
      obtain ⟨g', hg', rfl⟩ := List.mem_map.mp hg
      split
      · simp
      · exact h.nonempty g' hg'
    · intro x hx
      simp only [List.mem_append, List.mem_singleton] at hx
      rcases hx with hx | rfl
      · obtain ⟨g, hg, hxg⟩ := h.covered x hx
        refine ⟨_, List.mem_map_of_mem hg, ?_⟩
        split
        · exact List.mem_append_left _ hxg
        · exact hxg
      · refine ⟨_, List.mem_map_of_mem hg₀, ?_⟩
        rw [if_pos hm₀]
        exact List.mem_append_right _ List.mem_cons_self
    · intro g hg x hx
      obtain ⟨g', hg', rfl⟩ := List.mem_map.mp hg
      split at hx
      · simp only [List.mem_append, List.mem_singleton] at hx
        rcases hx with hx | rfl
        · exact List.mem_append_left _ (h.only g' hg' x hx)
        · exact List.mem_append_right _ List.mem_cons_self
      · exact List.mem_append_left _ (h.only g' hg' x hx)
  · rename_i hany
    have hno : ∀ g ∈ gs, g.tag ≠ (key r, assignment sets r) := by
      intro g hg ht
      apply hany
      exact List.any_eq_true.mpr ⟨g, hg, (match_iff sets key r g).mpr ht⟩
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro g hg x hx
      simp only [List.mem_append, List.mem_singleton] at hg
      rcases hg with hg | rfl
      · exact h.tagged g hg x hx
      · simp only [List.mem_singleton] at hx
        subst hx
        rfl
    · refine List.pairwise_append.mpr ⟨h.distinct, by simp, ?_⟩
      intro a ha b hb
      simp only [List.mem_singleton] at hb
      subst hb
      exact hno a ha
    · intro g hg
      simp only [List.mem_append, List.mem_singleton] at hg
      rcases hg with hg | rfl
      · exact h.nonempty g hg
      · simp
    · intro x hx
      simp only [List.mem_append, List.mem_singleton] at hx
      rcases hx with hx | rfl
      · obtain ⟨g, hg, hxg⟩ := h.covered x hx
        exact ⟨g, List.mem_append_left _ hg, hxg⟩
      · exact ⟨_, List.mem_append_right _ List.mem_cons_self, List.mem_cons_self⟩
    · intro g hg x hx
      simp only [List.mem_append, List.mem_singleton] at hg
      rcases hg with hg | rfl
      · exact List.mem_append_left _ (h.only g hg x hx)
      · simp only [List.mem_singleton] at hx
        subst hx
        exact List.mem_append_right _ List.mem_cons_self

theorem inv_foldl (sets : List String) (key : Row → Lead × List Source) :
    ∀ (rows seen : List Row) (gs : List Group), Inv sets key seen gs →
      Inv sets key (seen ++ rows) (rows.foldl (addRow sets key) gs)
  | [], seen, gs, h => by simpa using h
  | r :: rs, seen, gs, h => by
    have := inv_foldl sets key rs (seen ++ [r]) (addRow sets key gs r) (inv_addRow h r)
    simpa using this

theorem inv_groups (ids : List String) (rows : List Row) (key : Row → Lead × List Source) :
    Inv (relevantSets ids rows key) key rows (groups ids rows key) := by
  rw [groups_eq]
  have := inv_foldl (relevantSets ids rows key) key rows [] []
    ⟨by simp, by simp, by simp, by simp, by simp⟩
  simpa using this

theorem groups_cover : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
    ∀ r ∈ rows, ∃ g ∈ groups ids rows key, r ∈ g.rows ∧ ∀ g' ∈ groups ids rows key, r ∈ g'.rows → g' = g := by
  intro ids rows key r hr
  have h := inv_groups ids rows key
  obtain ⟨g, hg, hrg⟩ := h.covered r hr
  refine ⟨g, hg, hrg, fun g' hg' hrg' => ?_⟩
  have t1 := h.tagged g hg r hrg
  have t2 := h.tagged g' hg' r hrg'
  have hpw := h.distinct
  apply Classical.byContradiction
  intro hne
  obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem hg
  obtain ⟨j, hj, rfl⟩ := List.getElem_of_mem hg'
  rcases Nat.lt_trichotomy i j with hij | rfl | hij
  · exact (List.pairwise_iff_getElem.mp hpw i j hi hj hij) (t1.symm.trans t2)
  · exact hne rfl
  · exact (List.pairwise_iff_getElem.mp hpw j i hj hi hij) (t2.symm.trans t1)

theorem group_rows : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
    ∀ g ∈ groups ids rows key, ∀ r ∈ g.rows,
      r ∈ rows ∧ key r = (g.lead, g.cited) ∧ g.on = assignment (relevantSets ids rows key) r := by
  intro ids rows key g hg r hr
  have h := inv_groups ids rows key
  have t := h.tagged g hg r hr
  simp only [Group.tag, Prod.mk.injEq] at t
  exact ⟨h.only g hg r hr, t.1, t.2.symm⟩

/-- What an R1 block claims: every row that reads the named sets as the block names them has its lead and
    citations. -/
theorem group_claim : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
    ids.Nodup → (∀ r ∈ rows, r.choice.map (·.1) = ids) →
    (∀ r ∈ rows, ∀ r' ∈ rows, r.choice = r'.choice → key r = key r') →
    ∀ g ∈ groups ids rows key, ∀ r ∈ rows, assignment (relevantSets ids rows key) r = g.on →
      key r = (g.lead, g.cited) := by
  intro ids rows key hn hids hfun g hg r hr ha
  have h := inv_groups ids rows key
  obtain ⟨r₀, hr₀⟩ := List.exists_mem_of_ne_nil _ (h.nonempty g hg)
  obtain ⟨hm₀, hk₀, ho₀⟩ := group_rows ids rows key g hg r₀ hr₀
  rw [← hk₀]
  exact relevantSets_sound ids rows key hn hids hfun r hr r₀ hm₀ (index_of_assignment (ha.trans ho₀))

end VE.Ask
