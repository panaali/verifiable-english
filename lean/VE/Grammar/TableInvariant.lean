import VE.Grammar.Table

/-! The cap invariant of the table (docs/spec/english-lean.md 2.6 and 5.4).

The proof of `parse_complete` in four layers.

1. Buckets: what `Bucket.addAll` does to the items of one end position (`get_addAll`).
2. One combination: the candidates that `combine` builds from a complete-or-full entry and
   complete-or-full suffix entries are derivations, have no duplicate, and are either at least `cap`
   at an end position or all the derivations there (`combine_ok`).
3. One row: the rules applied in increasing rank (`ntRowGo_ok`), then the suffix entries
   (`sufGroups_ok`).
4. The rows, from the last start position to the first (`fill_ok`).
-/

namespace VE.Grammar

section Buckets

variable {X : Type}

/-- The end positions of a bucket strictly increase. -/
def Bucket.Sorted (e : Bucket X) : Prop := e.Pairwise (fun a b => a.1 < b.1)

theorem Bucket.get_nil {j : Nat} : Bucket.get ([] : Bucket X) j = [] := by simp [Bucket.get]

theorem Bucket.get_cons {k j : Nat} {xs : List X} {e : Bucket X} :
    Bucket.get ((k, xs) :: e) j = if k = j then xs else e.get j := by simp [Bucket.get]

theorem Bucket.get_eq_nil : ∀ {e : Bucket X} {j : Nat}, (∀ p ∈ e, p.1 ≠ j) → e.get j = []
  | [], _, _ => Bucket.get_nil
  | (k, xs) :: e, j, h => by
    rw [Bucket.get_cons, if_neg (h (k, xs) (by simp)), Bucket.get_eq_nil (fun p hp => h p (by simp [hp]))]

theorem Bucket.get_of_mem : ∀ {e : Bucket X} {p : Nat × List X}, e.Sorted → p ∈ e → e.get p.1 = p.2
  | [], _, _, hp => by simp at hp
  | (k, xs) :: e, p, hs, hp => by
    rw [Bucket.get_cons]
    rcases List.mem_cons.mp hp with rfl | hp
    · simp
    · have hlt := (List.pairwise_cons.mp hs).1 p hp
      rw [if_neg (by simp at hlt; omega)]
      exact Bucket.get_of_mem (List.pairwise_cons.mp hs).2 hp

theorem Bucket.mem_of_get : ∀ {e : Bucket X} {j : Nat} {x : X}, x ∈ e.get j → (j, e.get j) ∈ e
  | [], _, _, h => by simp [Bucket.get_nil] at h
  | (k, xs) :: e, j, x, h => by
    rw [Bucket.get_cons] at h ⊢
    split
    · rename_i hk; subst hk; simp
    · rename_i hk
      rw [if_neg hk] at h
      exact List.mem_cons_of_mem _ (Bucket.mem_of_get h)

/-- Adds the items, each while the list is shorter than `cap`. -/
def addCapped (cap : Nat) (xs : List X) (ys : List X) : List X := ys.foldl (insertCapped cap) xs

theorem addCapped_eq : ∀ {cap : Nat} {xs : List X} (ys : List X), xs.length ≤ cap →
    addCapped cap xs ys = (xs ++ ys).take cap
  | _, xs, [], h => by simp [addCapped, List.take_of_length_le h]
  | cap, xs, y :: ys, h => by
    unfold addCapped
    rw [List.foldl_cons]
    by_cases hlt : xs.length < cap
    · rw [show insertCapped cap xs y = xs ++ [y] from if_pos hlt]
      have := addCapped_eq (cap := cap) (xs := xs ++ [y]) ys (by simp; omega)
      unfold addCapped at this
      rw [this]
      simp
    · have hc : xs.length = cap := by omega
      rw [show insertCapped cap xs y = xs from if_neg hlt]
      have : ys.foldl (insertCapped cap) xs = xs := by
        clear h
        induction ys with
        | nil => rfl
        | cons z zs ih =>
          rw [List.foldl_cons, show insertCapped cap xs z = xs from if_neg hlt]
          exact ih
      rw [this, ← hc]
      simp

/-- The keys of a list of candidates do not decrease. -/
def KeysUp (cs : List (Nat × X)) : Prop := cs.Pairwise (fun a b => a.1 ≤ b.1)

theorem Bucket.merge_spec (cap : Nat) : ∀ (e : Bucket X) (cs : List (Nat × X)), e.Sorted → KeysUp cs →
    (Bucket.merge cap e cs).Sorted ∧
    (∀ p ∈ Bucket.merge cap e cs, (∃ q ∈ e, q.1 = p.1) ∨ (∃ c ∈ cs, c.1 = p.1)) ∧
    ∀ j, (Bucket.merge cap e cs).get j =
      addCapped cap (e.get j) ((cs.filter fun c => c.1 = j).map (·.2)) := by
  intro e cs
  induction e, cs using Bucket.merge.induct cap with
  | case1 e =>
    intro hs _
    refine ⟨by simpa [Bucket.merge] using hs, ?_, ?_⟩
    · intro p hp; left; exact ⟨p, by simpa [Bucket.merge] using hp, rfl⟩
    · intro j; simp [Bucket.merge, addCapped]
  | case2 j x cs ih =>
    intro _ hk
    have hk' := (List.pairwise_cons.mp hk).2
    obtain ⟨h1, h2, h3⟩ := ih (by simp [Bucket.Sorted]) hk'
    rw [Bucket.merge]
    refine ⟨h1, ?_, ?_⟩
    · intro p hp
      rcases h2 p hp with ⟨q, hq, e⟩ | ⟨c, hc, e⟩
      · simp at hq; subst hq; right; exact ⟨(j, x), by simp, e⟩
      · right; exact ⟨c, by simp [hc], e⟩
    · intro i
      rw [h3 i, Bucket.get_cons, Bucket.get_nil]
      by_cases hji : j = i
      · subst hji; simp [addCapped]
      · simp [hji, addCapped]
  | case3 k xs e j x cs hlt ih =>
    intro hs hk
    have hs' := (List.pairwise_cons.mp hs).2
    obtain ⟨h1, h2, h3⟩ := ih hs' hk
    rw [Bucket.merge, if_pos hlt]
    refine ⟨?_, ?_, ?_⟩
    · refine List.pairwise_cons.mpr ⟨fun p hp => ?_, h1⟩
      rcases h2 p hp with ⟨q, hq, e⟩ | ⟨c, hc, e⟩
      · rw [← e]; exact (List.pairwise_cons.mp hs).1 q hq
      · rw [← e]
        rcases List.mem_cons.mp hc with rfl | hc
        · exact hlt
        · have := (List.pairwise_cons.mp hk).1 c hc; simp at this; omega
    · intro p hp
      rcases List.mem_cons.mp hp with rfl | hp
      · left; exact ⟨(k, xs), by simp, rfl⟩
      · rcases h2 p hp with ⟨q, hq, e⟩ | h
        · left; exact ⟨q, by simp [hq], e⟩
        · right; exact h
    · intro i
      rw [Bucket.get_cons, Bucket.get_cons]
      by_cases hki : k = i
      · subst hki
        rw [if_pos rfl, if_pos rfl]
        have : ((j, x) :: cs).filter (fun c => c.1 = k) = [] := by
          rw [List.filter_eq_nil_iff]
          intro c hc
          rcases List.mem_cons.mp hc with rfl | hc
          · simp; omega
          · have := (List.pairwise_cons.mp hk).1 c hc; simp at this ⊢; omega
        rw [this]; simp [addCapped]
      · rw [if_neg hki, if_neg hki]; exact h3 i
  | case4 xs e j x cs _ ih =>
    intro hs hk
    have hk' := (List.pairwise_cons.mp hk).2
    obtain ⟨h1, h2, h3⟩ := ih (by simpa [Bucket.Sorted] using hs) hk'
    rw [Bucket.merge, if_neg (Nat.lt_irrefl j), if_pos rfl]
    refine ⟨h1, ?_, ?_⟩
    · intro p hp
      rcases h2 p hp with ⟨q, hq, e⟩ | ⟨c, hc, e⟩
      · rcases List.mem_cons.mp hq with rfl | hq
        · left; exact ⟨(j, xs), by simp, by simpa using e⟩
        · left; exact ⟨q, by simp [hq], e⟩
      · right; exact ⟨c, by simp [hc], e⟩
    · intro i
      rw [h3 i, Bucket.get_cons, Bucket.get_cons]
      by_cases hji : j = i
      · subst hji; simp [addCapped]
      · simp [hji]
  | case5 k xs e j x cs hlt hne ih =>
    intro hs hk
    have hk' := (List.pairwise_cons.mp hk).2
    have hjk : j < k := by omega
    have hs2 : Bucket.Sorted ((j, insertCapped cap [] x) :: (k, xs) :: e) := by
      refine List.pairwise_cons.mpr ⟨fun p hp => ?_, hs⟩
      rcases List.mem_cons.mp hp with rfl | hp
      · exact hjk
      · have := (List.pairwise_cons.mp hs).1 p hp; simp at this; omega
    obtain ⟨h1, h2, h3⟩ := ih hs2 hk'
    rw [Bucket.merge, if_neg hlt, if_neg hne]
    refine ⟨h1, ?_, ?_⟩
    · intro p hp
      rcases h2 p hp with ⟨q, hq, e⟩ | ⟨c, hc, e⟩
      · rcases List.mem_cons.mp hq with rfl | hq
        · right; exact ⟨(j, x), by simp, e⟩
        · left; exact ⟨q, hq, e⟩
      · right; exact ⟨c, by simp [hc], e⟩
    · intro i
      rw [h3 i, Bucket.get_cons]
      by_cases hji : j = i
      · subst hji
        rw [if_pos rfl]
        have : Bucket.get ((k, xs) :: e) j = [] := by
          apply Bucket.get_eq_nil
          intro p hp
          rcases List.mem_cons.mp hp with rfl | hp
          · simp; omega
          · have := (List.pairwise_cons.mp hs).1 p hp; simp at this; omega
        rw [this]; simp [addCapped]
      · rw [if_neg hji]; simp [hji]

/-- What `addAll` does to the items of one end position: the candidates of that end position, in some
order, are added while the list is shorter than `cap`. -/
theorem Bucket.addAll_spec {cap : Nat} {e : Bucket X} {cands : List (Nat × X)} (hs : e.Sorted) :
    (e.addAll cap cands).Sorted ∧
    (∀ p ∈ e.addAll cap cands, (∃ q ∈ e, q.1 = p.1) ∨ (∃ c ∈ cands, c.1 = p.1)) ∧
    ∀ j, ∃ L, L.Perm ((cands.filter fun c => c.1 = j).map (·.2)) ∧
      (e.addAll cap cands).get j = addCapped cap (e.get j) L := by
  have hsorted : KeysUp (cands.mergeSort fun a b => decide (a.1 ≤ b.1)) := by
    have := List.sorted_mergeSort (le := fun (a b : Nat × X) => decide (a.1 ≤ b.1))
      (by intro a b c h1 h2; simp at *; omega) (by intro a b; simp; omega) cands
    unfold KeysUp
    exact this.imp (by simp)
  have hperm := List.mergeSort_perm cands (fun a b => decide (a.1 ≤ b.1))
  obtain ⟨h1, h2, h3⟩ := Bucket.merge_spec cap e _ hs hsorted
  refine ⟨h1, ?_, ?_⟩
  · intro p hp
    rcases h2 p hp with h | ⟨c, hc, e⟩
    · left; exact h
    · right; exact ⟨c, hperm.mem_iff.mp hc, e⟩
  · intro j
    exact ⟨_, (hperm.filter _).map _, h3 j⟩

/-- A list without duplicates whose members all occur in another list is not longer than it. -/
theorem length_le_of_nodup_subset [DecidableEq X] : ∀ {xs ys : List X}, xs.Nodup → (∀ x ∈ xs, x ∈ ys) →
    xs.length ≤ ys.length
  | [], _, _, _ => by simp
  | x :: xs, ys, hn, hs => by
    have ⟨hx, hxs⟩ := List.nodup_cons.mp hn
    have hmem : x ∈ ys := hs x (by simp)
    have := length_le_of_nodup_subset (ys := ys.erase x) hxs (fun y hy => by
      have hyx : y ≠ x := fun e => hx (e ▸ hy)
      exact (List.mem_erase_of_ne hyx).mpr (hs y (by simp [hy])))
    rw [List.length_erase_of_mem hmem] at this
    have : 0 < ys.length := List.length_pos_of_mem hmem
    simp; omega

theorem Bucket.Sorted.nodup {e : Bucket X} (h : e.Sorted) : e.Nodup :=
  h.imp fun hlt he => by subst he; exact Nat.lt_irrefl _ hlt

theorem Bucket.Sorted.key_ne {e : Bucket X} (h : e.Sorted) : ∀ {p q}, p ∈ e → q ∈ e → p ≠ q → p.1 ≠ q.1 := by
  intro p q hp hq hpq hk
  have h1 := Bucket.get_of_mem h hp
  have h2 := Bucket.get_of_mem h hq
  rw [hk] at h1
  exact hpq (Prod.ext hk (h1.symm.trans h2))

theorem nodup_map_of_inj {Y : Type} {f : X → Y} : ∀ {l : List X}, l.Nodup →
    (∀ a ∈ l, ∀ b ∈ l, f a = f b → a = b) → (l.map f).Nodup
  | [], _, _ => by simp
  | x :: xs, hn, hi => by
    have ⟨hx, hxs⟩ := List.nodup_cons.mp hn
    refine List.nodup_cons.mpr ⟨?_, nodup_map_of_inj hxs (fun a ha b hb => hi a (by simp [ha]) b (by simp [hb]))⟩
    intro hm
    obtain ⟨y, hy, he⟩ := List.mem_map.mp hm
    exact hx (hi y (by simp [hy]) x (by simp) he ▸ hy)

theorem nodup_flatMap_of {Y : Type} {f : X → List Y} : ∀ {l : List X}, l.Nodup → (∀ x ∈ l, (f x).Nodup) →
    (∀ x ∈ l, ∀ y ∈ l, x ≠ y → ∀ a ∈ f x, a ∉ f y) → (l.flatMap f).Nodup
  | [], _, _, _ => by simp
  | x :: xs, hn, hf, hd => by
    have ⟨hx, hxs⟩ := List.nodup_cons.mp hn
    rw [List.flatMap_cons]
    refine List.nodup_append.mpr ⟨hf x (by simp), nodup_flatMap_of hxs (fun y hy => hf y (by simp [hy]))
      (fun a ha b hb => hd a (by simp [ha]) b (by simp [hb])), ?_⟩
    intro a ha b hb hab
    subst hab
    obtain ⟨y, hy, hay⟩ := List.mem_flatMap.mp hb
    exact hd x (by simp) y (by simp [hy]) (fun e => hx (e ▸ hy)) a ha hay

end Buckets

section Spans

variable {T K : Type} [Accepts K T]

/-- The derivations of `X` over the tokens of `w` from `i` to `j` (spec 5.4). -/
def Span (G : Grammar K) (w : Array T) (X : Sym K) (i j : Nat) (t : Tree T) : Prop :=
  Derives G X ((w.toList.drop i).take (j - i)) t

/-- The lists of trees that derive the symbols `Xs` over the tokens from `i` to `j`. -/
def SpanAll (G : Grammar K) (w : Array T) (Xs : List (Sym K)) (i j : Nat) (us : List (Tree T)) : Prop :=
  derivesAll G Xs us = true ∧ yieldAll us = (w.toList.drop i).take (j - i)

/-- An entry that should hold the derivations of `X` over the tokens from `i` to `j` (spec 5.4). -/
def EntryOk (G : Grammar K) (cap : Nat) (w : Array T) (X : Sym K) (i j : Nat) (e : List (Tree T)) : Prop :=
  e.Nodup ∧ (∀ t ∈ e, Span G w X i j t) ∧ e.length ≤ cap ∧
  (e.length < cap → ∀ t, Span G w X i j t → t ∈ e)

/-- A bucket whose items at each end position `j ≤ n` are a duplicate-free list of what `P j` holds of,
at most `cap` of them, and either all of them or exactly `cap`. -/
structure BOk {X : Type} (cap n : Nat) (P : Nat → X → Prop) (e : Bucket X) : Prop where
  sorted : e.Sorted
  keys : ∀ p ∈ e, p.1 ≤ n
  nodup : ∀ j, (e.get j).Nodup
  sound : ∀ j x, x ∈ e.get j → P j x
  length : ∀ j, (e.get j).length ≤ cap
  complete : ∀ j, j ≤ n → (e.get j).length < cap → ∀ x, P j x → x ∈ e.get j

theorem BOk.nil {X : Type} {cap n : Nat} {P : Nat → X → Prop} (h : ∀ j x, j ≤ n → 0 < cap → ¬ P j x) :
    BOk cap n P ([] : Bucket X) where
  sorted := List.Pairwise.nil
  keys := by simp
  nodup := by simp [Bucket.get_nil]
  sound := by simp [Bucket.get_nil]
  length := by simp [Bucket.get_nil]
  complete := by
    intro j hj hl x hx
    simp [Bucket.get_nil] at hl
    exact absurd hx (h j x hj hl)

theorem BOk.congr {X : Type} {cap n : Nat} {P Q : Nat → X → Prop} {e : Bucket X} (h : BOk cap n P e)
    (hPQ : ∀ j x, j ≤ n → (P j x ↔ Q j x)) : BOk cap n Q e where
  sorted := h.sorted
  keys := h.keys
  nodup := h.nodup
  sound := by
    intro j x hx
    have hj : j ≤ n := h.keys _ (Bucket.mem_of_get hx)
    exact (hPQ j x hj).mp (h.sound j x hx)
  length := h.length
  complete := fun j hj hl x hx => h.complete j hj hl x ((hPQ j x hj).mpr hx)

/-- The tokens from `i` to `j`. -/
abbrev toks (w : Array T) (i j : Nat) : List T := (w.toList.drop i).take (j - i)

theorem toks_length {w : Array T} {i j : Nat} (hj : j ≤ w.size) : (toks w i j).length = j - i := by
  simp [toks, List.length_take]; omega

theorem toks_append {w : Array T} {i j1 j : Nat} (h1 : i ≤ j1) (h2 : j1 ≤ j) :
    toks w i j1 ++ toks w j1 j = toks w i j := by
  unfold toks
  have : j - i = (j1 - i) + (j - j1) := by omega
  rw [this, List.take_add, List.drop_drop]
  congr 3
  omega

theorem lt_of_toks_ne_nil {w : Array T} {i j : Nat} (h : toks w i j ≠ []) : i < j := by
  unfold toks at h
  rcases Nat.lt_or_ge i j with hc | hc
  · exact hc
  · exact absurd (by rw [show j - i = 0 by omega]; simp) h

/-- A split of the tokens from `i` to `j` at the length of its first part. -/
theorem toks_split {w : Array T} {i j : Nat} {a b : List T} (hij : i ≤ j) (hj : j ≤ w.size)
    (h : a ++ b = toks w i j) :
    i + a.length ≤ j ∧ a = toks w i (i + a.length) ∧ b = toks w (i + a.length) j := by
  have hl : (a ++ b).length = j - i := by rw [h]; exact toks_length hj
  simp only [List.length_append] at hl
  have hle : i + a.length ≤ j := by omega
  refine ⟨hle, ?_⟩
  rw [← toks_append (w := w) (Nat.le_add_right i a.length) hle] at h
  exact List.append_inj h (by rw [toks_length (by omega)]; omega)

theorem toks_one {w : Array T} {i : Nat} (hi : i < w.size) : toks w i (i + 1) = [w[i]] := by
  unfold toks
  rw [show i + 1 - i = 1 by omega]
  rw [List.drop_eq_getElem_cons (by simpa using hi)]
  simp

variable {G : Grammar K}

theorem yieldAll_ne_nil (hG : G.wf = true) {Xs : List (Sym K)} {us : List (Tree T)} (h : derivesAll G Xs us = true)
    (hX : Xs ≠ []) : yieldAll us ≠ [] := by
  match Xs, us, h with
  | [], _, _ => exact absurd rfl hX
  | _ :: _, [], h => simp [derivesAll] at h
  | X :: _, u :: _, h =>
    rw [derivesAll_cons, Bool.and_eq_true] at h
    rw [yieldAll_cons]
    intro he
    exact yield_ne_nil hG h.1 (List.append_eq_nil_iff.mp he).1

end Spans

section Combine

variable {T K : Type} [DecidableEq T] [Accepts K T]
variable {G : Grammar K}

/-- The part of `combine` that one item of the first symbol's entry contributes. -/
def combineOne (next : Nat → Bucket (List (Tree T))) (last : Bool) (j1 : Nat) (t : Tree T) :
    List (Nat × List (Tree T)) :=
  if last then [(j1, [t])] else (next j1).flatMap fun q => q.2.map fun us => (q.1, t :: us)

theorem combine_eq {first : Bucket (Tree T)} {next : Nat → Bucket (List (Tree T))} {last : Bool} :
    combine first next last = first.flatMap fun p => p.2.flatMap (combineOne next last p.1) := by
  unfold combine combineOne
  rfl

theorem mem_combineOne {next : Nat → Bucket (List (Tree T))} {last : Bool} {j1 : Nat} {t : Tree T}
    {c : Nat × List (Tree T)} : c ∈ combineOne next last j1 t ↔
      (last = true ∧ c = (j1, [t])) ∨ (last = false ∧ ∃ q ∈ next j1, ∃ us ∈ q.2, c = (q.1, t :: us)) := by
  unfold combineOne
  cases last
  · simp only [Bool.false_eq_true, if_false, List.mem_flatMap, List.mem_map, false_and, true_and, false_or]
    constructor
    · rintro ⟨q, hq, us, hus, rfl⟩; exact ⟨q, hq, us, hus, rfl⟩
    · rintro ⟨q, hq, us, hus, rfl⟩; exact ⟨q, hq, us, hus, rfl⟩
  · simp

theorem head_of_mem_combineOne {next : Nat → Bucket (List (Tree T))} {last : Bool} {j1 : Nat} {t : Tree T}
    {c : Nat × List (Tree T)} (h : c ∈ combineOne next last j1 t) : c.2.head? = some t := by
  rcases mem_combineOne.mp h with ⟨_, rfl⟩ | ⟨_, q, _, us, _, rfl⟩ <;> rfl

theorem combine_ok (hG : G.wf = true) {cap : Nat} {w : Array T} {i : Nat}
    {Y : Sym K} {rest : List (Sym K)} {first : Bucket (Tree T)} {next : Nat → Bucket (List (Tree T))}
    {last : Bool} (hlast : last = rest.isEmpty)
    (hF : BOk cap w.size (Span G w Y i) first)
    (hN : rest ≠ [] → ∀ j1, i < j1 → j1 ≤ w.size → BOk cap w.size (SpanAll G w rest j1) (next j1)) :
    (∀ c ∈ combine first next last, c.1 ≤ w.size ∧ SpanAll G w (Y :: rest) i c.1 c.2) ∧
    (combine first next last).Nodup ∧
    ∀ j, j ≤ w.size → cap ≤ ((combine first next last).filter fun c => c.1 = j).length ∨
      ∀ us, SpanAll G w (Y :: rest) i j us → (j, us) ∈ combine first next last := by
  -- An item of the first symbol's entry.
  have F1 : ∀ p ∈ first, ∀ t ∈ p.2, Span G w Y i p.1 t ∧ i < p.1 ∧ p.1 ≤ w.size := by
    intro p hp t ht
    have hs : Span G w Y i p.1 t := hF.sound p.1 t (by rw [Bucket.get_of_mem hF.sorted hp]; exact ht)
    refine ⟨hs, ?_, hF.keys p hp⟩
    have hy := yield_ne_nil hG hs.1
    rw [hs.2] at hy
    exact lt_of_toks_ne_nil hy
  -- An item of a suffix entry.
  have F2 : rest ≠ [] → ∀ j1, i < j1 → j1 ≤ w.size → ∀ q ∈ next j1, ∀ us ∈ q.2,
      SpanAll G w rest j1 q.1 us ∧ j1 < q.1 ∧ q.1 ≤ w.size := by
    intro hr j1 h1 h2 q hq us hus
    have hB := hN hr j1 h1 h2
    have hs : SpanAll G w rest j1 q.1 us := hB.sound q.1 us (by rw [Bucket.get_of_mem hB.sorted hq]; exact hus)
    refine ⟨hs, ?_, hB.keys q hq⟩
    have hy := yieldAll_ne_nil hG hs.1 hr
    rw [hs.2] at hy
    exact lt_of_toks_ne_nil hy
  have hlast1 : last = true → rest = [] := by
    intro h; rw [h] at hlast; exact List.isEmpty_iff.mp hlast.symm
  have hlast0 : last = false → rest ≠ [] := by
    intro h he; rw [h, he] at hlast; simp at hlast
  rw [combine_eq]
  refine ⟨?_, ?_, ?_⟩
  · -- soundness
    intro c hc
    obtain ⟨p, hp, hc⟩ := List.mem_flatMap.mp hc
    obtain ⟨t, ht, hc⟩ := List.mem_flatMap.mp hc
    obtain ⟨hs, hi, hn⟩ := F1 p hp t ht
    rcases mem_combineOne.mp hc with ⟨hl, rfl⟩ | ⟨hl, q, hq, us, hus, rfl⟩
    · rw [hlast1 hl]
      refine ⟨hn, ?_, ?_⟩
      · simp [derivesAll, hs.1]
      · simp [yieldAll, hs.2]
    · obtain ⟨hs2, hq1, hq2⟩ := F2 (hlast0 hl) p.1 hi hn q hq us hus
      refine ⟨hq2, ?_, ?_⟩
      · rw [derivesAll_cons, hs.1, hs2.1]; rfl
      · rw [yieldAll_cons, hs.2, hs2.2]
        exact toks_append (Nat.le_of_lt hi) (Nat.le_of_lt hq1)
  · -- no duplicate
    apply nodup_flatMap_of hF.sorted.nodup
    · intro p hp
      apply nodup_flatMap_of (by rw [← Bucket.get_of_mem hF.sorted hp]; exact hF.nodup p.1)
      · intro t ht
        unfold combineOne
        split
        · simp
        · rename_i hl
          obtain ⟨_, hi, hn⟩ := F1 p hp t ht
          have hB := hN (hlast0 (by simpa using hl)) p.1 hi hn
          apply nodup_flatMap_of hB.sorted.nodup
          · intro q hq
            apply nodup_map_of_inj (by rw [← Bucket.get_of_mem hB.sorted hq]; exact hB.nodup q.1)
            intro a _ b _ he
            simp at he; exact he
          · intro q hq q2 hq2 hne a ha hb
            obtain ⟨us, _, rfl⟩ := List.mem_map.mp ha
            obtain ⟨us2, _, he⟩ := List.mem_map.mp hb
            exact hB.sorted.key_ne hq hq2 hne (congrArg Prod.fst he).symm
      · intro t ht t2 ht2 hne a ha hb
        have h1 := head_of_mem_combineOne ha
        have h2 := head_of_mem_combineOne hb
        rw [h1] at h2
        exact hne (Option.some.inj h2)
    · intro p hp p2 hp2 hne a ha hb
      obtain ⟨t, ht, ha⟩ := List.mem_flatMap.mp ha
      obtain ⟨t2, ht2, hb⟩ := List.mem_flatMap.mp hb
      have h1 := head_of_mem_combineOne ha
      have h2 := head_of_mem_combineOne hb
      rw [h1] at h2
      have htt : t = t2 := Option.some.inj h2
      subst htt
      obtain ⟨hs, hi, hn⟩ := F1 p hp t ht
      obtain ⟨hs2, hi2, hn2⟩ := F1 p2 hp2 t ht2
      have hl1 : t.yield.length = p.1 - i := by rw [hs.2]; exact toks_length hn
      have hl2 : t.yield.length = p2.1 - i := by rw [hs2.2]; exact toks_length hn2
      exact hF.sorted.key_ne hp hp2 hne (by omega)
  · -- either full, or every derivation is a candidate
    intro j hj
    by_cases hc : cap ≤ ((first.flatMap fun p => p.2.flatMap (combineOne next last p.1)).filter
        fun c => c.1 = j).length
    · exact Or.inl hc
    · right
      have hmem : ∀ j1 t, t ∈ first.get j1 → ∀ c ∈ combineOne next last j1 t,
          c ∈ first.flatMap fun p => p.2.flatMap (combineOne next last p.1) := by
        intro j1 t ht c hc
        exact List.mem_flatMap.mpr ⟨(j1, first.get j1), Bucket.mem_of_get ht,
          List.mem_flatMap.mpr ⟨t, ht, hc⟩⟩
      -- `cap` different candidates at `j` contradict `hc`.
      have hfull : ∀ M : List (Nat × List (Tree T)), M.Nodup → M.length = cap →
          (∀ c ∈ M, c.1 = j ∧ c ∈ first.flatMap fun p => p.2.flatMap (combineOne next last p.1)) → False := by
        intro M hM hl hall
        apply hc
        rw [← hl]
        apply length_le_of_nodup_subset hM
        intro c hcM
        have := hall c hcM
        exact List.mem_filter.mpr ⟨this.2, by simp [this.1]⟩
      intro us hus
      match us, hus with
      | [], hus => simp [SpanAll, derivesAll] at hus
      | t :: us2, hus =>
        obtain ⟨hd, hy⟩ := hus
        rw [derivesAll_cons, Bool.and_eq_true] at hd
        rw [yieldAll_cons] at hy
        have hij : i < j := by
          have hne : t.yield ++ yieldAll us2 ≠ [] := by
            intro he
            exact yield_ne_nil hG hd.1 (List.append_eq_nil_iff.mp he).1
          rw [hy] at hne
          exact lt_of_toks_ne_nil hne
        obtain ⟨hle, ht1, hu1⟩ := toks_split (Nat.le_of_lt hij) hj hy
        have hst : Span G w Y i (i + t.yield.length) t := ⟨hd.1, ht1⟩
        have hj1 : i < i + t.yield.length := by
          have := yield_ne_nil hG hd.1
          have : 0 < t.yield.length := List.length_pos_iff.mpr this
          omega
        have hj1n : i + t.yield.length ≤ w.size := by omega
        -- The first symbol's entry at `j1` is complete.
        have hcapF := hF.length (i + t.yield.length)
        cases last
        · -- not the last symbol
          have hr := hlast0 rfl
          have hB := hN hr (i + t.yield.length) hj1 hj1n
          have hsu : SpanAll G w rest (i + t.yield.length) j us2 := ⟨hd.2, hu1⟩
          have hcapN := hB.length j
          have hpos : 0 < cap := by
            rcases Nat.eq_zero_or_pos cap with h0 | h0
            · exact absurd (by rw [h0]; exact Nat.zero_le _) hc
            · exact h0
          by_cases hFc : (first.get (i + t.yield.length)).length < cap
          · have htin := hF.complete _ hj1n hFc t hst
            by_cases hNc : ((next (i + t.yield.length)).get j).length < cap
            · have husin := hB.complete j hj hNc us2 hsu
              apply hmem _ t htin
              exact mem_combineOne.mpr (Or.inr ⟨rfl, (j, (next _).get j), Bucket.mem_of_get husin, us2, husin, rfl⟩)
            · exfalso
              apply hfull (((next (i + t.yield.length)).get j).map fun u => (j, t :: u))
              · apply nodup_map_of_inj (hB.nodup j)
                intro a _ b _ he; simp at he; exact he
              · simp; omega
              · intro c hcM
                obtain ⟨u, hu, rfl⟩ := List.mem_map.mp hcM
                refine ⟨rfl, hmem _ t htin _ ?_⟩
                exact mem_combineOne.mpr (Or.inr ⟨rfl, (j, (next _).get j), Bucket.mem_of_get hu, u, hu, rfl⟩)
          · exfalso
            -- some suffix list at `j` exists
            have hne : ∃ u, u ∈ (next (i + t.yield.length)).get j := by
              by_cases hNc : ((next (i + t.yield.length)).get j).length < cap
              · exact ⟨us2, hB.complete j hj hNc us2 hsu⟩
              · match hl : (next (i + t.yield.length)).get j with
                | [] => rw [hl] at hNc; simp at hNc; omega
                | u :: _ => exact ⟨u, by simp⟩
            obtain ⟨u, hu⟩ := hne
            apply hfull ((first.get (i + t.yield.length)).map fun t2 => (j, t2 :: u))
            · apply nodup_map_of_inj (hF.nodup _)
              intro a _ b _ he; simp at he; exact he
            · simp; omega
            · intro c hcM
              obtain ⟨t2, ht2, rfl⟩ := List.mem_map.mp hcM
              refine ⟨rfl, hmem _ t2 ht2 _ ?_⟩
              exact mem_combineOne.mpr (Or.inr ⟨rfl, (j, (next _).get j), Bucket.mem_of_get hu, u, hu, rfl⟩)
        · -- the last symbol
          have hr := hlast1 rfl
          subst hr
          have hu0 : us2 = [] := by
            match us2, hd.2 with
            | [], _ => rfl
            | _ :: _, h => simp [derivesAll] at h
          subst hu0
          have hjj : i + t.yield.length = j := by
            have h0 : (toks w (i + t.yield.length) j).length = 0 := by rw [← hu1]; rfl
            rw [toks_length hj] at h0
            omega
          rw [hjj] at hst hcapF hj1n
          by_cases hFc : (first.get j).length < cap
          · have htin := hF.complete _ hj hFc t hst
            exact hmem _ t htin _ (mem_combineOne.mpr (Or.inl ⟨rfl, rfl⟩))
          · exfalso
            apply hfull ((first.get j).map fun t2 => (j, [t2]))
            · apply nodup_map_of_inj (hF.nodup _)
              intro a _ b _ he; simp at he; exact he
            · simp; omega
            · intro c hcM
              obtain ⟨t2, ht2, rfl⟩ := List.mem_map.mp hcM
              exact ⟨rfl, hmem _ t2 ht2 _ (mem_combineOne.mpr (Or.inl ⟨rfl, rfl⟩))⟩

end Combine

section Step

variable {X : Type}

/-- Adding candidates to a complete-or-full bucket: if the candidates are what `Pnew` holds of, have no
duplicate, are disjoint from what `Pold` holds of, and are either at least `cap` or all of `Pnew` at each
end position, the result is complete-or-full for `Pold` or `Pnew`. -/
theorem BOk.addAll {cap n : Nat} {Pold Pnew : Nat → X → Prop} {e : Bucket X} {cands : List (Nat × X)}
    (he : BOk cap n Pold e) (ha : ∀ c ∈ cands, c.1 ≤ n ∧ Pnew c.1 c.2) (hn : cands.Nodup)
    (hc : ∀ j, j ≤ n → cap ≤ (cands.filter fun c => c.1 = j).length ∨ ∀ x, Pnew j x → (j, x) ∈ cands)
    (hd : ∀ j x, Pold j x → ¬ Pnew j x) :
    BOk cap n (fun j x => Pold j x ∨ Pnew j x) (e.addAll cap cands) := by
  obtain ⟨hs, hk, hg⟩ := Bucket.addAll_spec (cap := cap) (cands := cands) he.sorted
  -- the candidates of one end position
  have hL : ∀ j (L : List X), L.Perm ((cands.filter fun c => c.1 = j).map (·.2)) →
      L.Nodup ∧ (∀ x ∈ L, (j, x) ∈ cands ∧ Pnew j x) ∧
      L.length = (cands.filter fun c => c.1 = j).length := by
    intro j L hp
    refine ⟨hp.symm.nodup ?_, ?_, by rw [hp.length_eq]; simp⟩
    · apply nodup_map_of_inj ((List.filter_sublist).nodup hn)
      intro a ha b hb he
      have ha' := (List.mem_filter.mp ha).2
      have hb' := (List.mem_filter.mp hb).2
      simp at ha' hb'
      exact Prod.ext (ha'.trans hb'.symm) he
    · intro x hx
      obtain ⟨c, hcm, rfl⟩ := List.mem_map.mp (hp.mem_iff.mp hx)
      have ⟨hcm, hcj⟩ := List.mem_filter.mp hcm
      simp at hcj
      have : c = (j, c.2) := Prod.ext hcj rfl
      rw [this] at hcm
      exact ⟨hcm, hcj ▸ (ha c (by rw [← this] at hcm; exact hcm)).2⟩
  refine ⟨hs, ?_, ?_, ?_, ?_, ?_⟩
  · intro p hp
    rcases hk p hp with ⟨q, hq, e⟩ | ⟨c, hc, e⟩
    · rw [← e]; exact he.keys q hq
    · rw [← e]; exact (ha c hc).1
  · intro j
    obtain ⟨L, hp, hget⟩ := hg j
    obtain ⟨hLn, hLm, _⟩ := hL j L hp
    rw [hget, addCapped_eq _ (he.length j)]
    apply List.Nodup.sublist (List.take_sublist _ _)
    refine List.nodup_append.mpr ⟨he.nodup j, hLn, ?_⟩
    intro a ha b hb hab
    subst hab
    exact hd j a (he.sound j a ha) (hLm a hb).2
  · intro j x hx
    obtain ⟨L, hp, hget⟩ := hg j
    obtain ⟨_, hLm, _⟩ := hL j L hp
    rw [hget, addCapped_eq _ (he.length j)] at hx
    rcases List.mem_append.mp (List.mem_of_mem_take hx) with h | h
    · exact Or.inl (he.sound j x h)
    · exact Or.inr (hLm x h).2
  · intro j
    obtain ⟨L, hp, hget⟩ := hg j
    rw [hget, addCapped_eq _ (he.length j)]
    simp only [List.length_take]
    omega
  · intro j hj hlt x hx
    obtain ⟨L, hp, hget⟩ := hg j
    obtain ⟨_, _, hLl⟩ := hL j L hp
    rw [hget, addCapped_eq _ (he.length j)] at hlt ⊢
    simp only [List.length_take, List.length_append] at hlt
    have hall : (e.get j ++ L).length < cap := by simp; omega
    rw [List.take_of_length_le (by omega)]
    rcases hx with hx | hx
    · exact List.mem_append_left _ (he.complete j hj (by omega) x hx)
    · rcases hc j hj with hc | hc
      · omega
      · have := hc x hx
        apply List.mem_append_right
        apply hp.mem_iff.mpr
        exact List.mem_map.mpr ⟨(j, x), List.mem_filter.mpr ⟨this, by simp⟩, rfl⟩

end Step

section Prepared

variable {K : Type} [DecidableEq K]
variable {G : Grammar K}

theorem mem_addTerms_of_mem {a : K} : ∀ {acc : Array K} {l : List (Sym K)}, a ∈ acc → a ∈ addTerms acc l
  | _, [], h => h
  | acc, .t b :: rest, h => by
    unfold addTerms
    apply mem_addTerms_of_mem
    split
    · exact h
    · exact Array.mem_push.mpr (Or.inl h)
  | _, .n _ :: rest, h => by unfold addTerms; exact mem_addTerms_of_mem h

theorem mem_addTerms {a : K} : ∀ {acc : Array K} {l : List (Sym K)}, .t a ∈ l → a ∈ addTerms acc l
  | _, [], h => by simp at h
  | acc, .t b :: rest, h => by
    unfold addTerms
    rcases List.mem_cons.mp h with h | h
    · cases h
      apply mem_addTerms_of_mem
      split
      · rename_i hc; exact Array.contains_iff.mp hc
      · exact Array.mem_push.mpr (Or.inr rfl)
    · exact mem_addTerms h
  | _, .n _ :: rest, h => by
    unfold addTerms
    rcases List.mem_cons.mp h with h | h
    · cases h
    · exact mem_addTerms h

/-- Every terminal of every rule is among the distinct terminals. -/
theorem mem_termsOf {r : Nat} {R : Rule K} {a : K} (hr : G.rules[r]? = some R) (ha : .t a ∈ R.rhs) :
    a ∈ termsOf G := by
  unfold termsOf
  have := Array.foldl_induction (as := G.rules)
    (motive := fun k (acc : Array K) => ∀ r2 (h : r2 < k) (h2 : r2 < G.rules.size), ∀ b,
      .t b ∈ G.rules[r2].rhs → b ∈ acc) (init := #[]) (by intro r2 h; omega)
    (f := fun acc R => addTerms acc R.rhs) (by
      intro k acc ih r2 h h2 b hb
      rcases Nat.lt_or_ge r2 k with hlt | hge
      · exact mem_addTerms_of_mem (ih r2 hlt h2 b hb)
      · have : r2 = k := by omega
        subst this
        exact mem_addTerms hb)
  obtain ⟨hlt, hR⟩ := Array.getElem?_eq_some_iff.mp hr
  exact this r hlt hlt a (by rw [hR]; exact ha)

theorem getElem_idxOf {terms : Array K} {a : K} (h : a ∈ terms) :
    ∃ hlt : terms.idxOf a < terms.size, terms[terms.idxOf a] = a := by
  have hlt := Array.idxOf_lt_length_of_mem h
  refine ⟨hlt, ?_⟩
  have := Array.findIdx_getElem (p := fun x => x == a) (xs := terms) (w := hlt)
  simpa using this

/-- The rules in the order of `prepare`, before sorting. -/
def cruleList (G : Grammar K) : List (CRule K) :=
  G.rules.toList.zipIdx.map fun (R, r) =>
    ({ index := r, lhs := R.lhs, rhs := R.rhs, first := (R.rhs.head?.map (termIndex (termsOf G))).getD 0 } : CRule K)

theorem prepare_grammar : G.prepare.grammar = G := rfl
theorem prepare_terms : G.prepare.terms = termsOf G := rfl

theorem order_perm : G.prepare.order.Perm (cruleList G) := List.mergeSort_perm _ _

theorem order_sorted : G.prepare.order.Pairwise (fun a b => G.rank.getD a.lhs 0 ≤ G.rank.getD b.lhs 0) := by
  have := List.sorted_mergeSort (le := fun (a b : CRule K) => decide (G.rank.getD a.lhs 0 ≤ G.rank.getD b.lhs 0))
    (by intro a b c h1 h2; simp at *; omega) (by intro a b; simp; omega) (cruleList G)
  exact this.imp (by simp)

theorem mem_order {R : CRule K} (h : R ∈ G.prepare.order) : ∃ R0, G.rules[R.index]? = some R0 ∧
    R0.lhs = R.lhs ∧ R0.rhs = R.rhs ∧ R.first = (R.rhs.head?.map (termIndex (termsOf G))).getD 0 := by
  have h := order_perm.mem_iff.mp h
  unfold cruleList at h
  obtain ⟨⟨R0, r⟩, hm, rfl⟩ := List.mem_map.mp h
  have := List.mem_zipIdx_iff_getElem?.mp hm
  simp only [Array.getElem?_toList] at this
  exact ⟨R0, this, rfl, rfl, rfl⟩

theorem order_complete {r : Nat} {R0 : Rule K} (h : G.rules[r]? = some R0) :
    ∃ R ∈ G.prepare.order, R.index = r ∧ R.lhs = R0.lhs := by
  have hm : (R0, r) ∈ G.rules.toList.zipIdx := List.mem_zipIdx_iff_getElem?.mpr (by simpa using h)
  refine ⟨_, order_perm.mem_iff.mpr (List.mem_map.mpr ⟨(R0, r), hm, rfl⟩), rfl, rfl⟩

theorem order_nodup : (G.prepare.order.map (·.index)).Nodup := by
  apply (order_perm.map _).symm.nodup
  unfold cruleList
  rw [List.map_map]
  have : ((fun (R : CRule K) => R.index) ∘ fun (x : Rule K × Nat) =>
      ({ index := x.2, lhs := x.1.lhs, rhs := x.1.rhs,
         first := (x.1.rhs.head?.map (termIndex (termsOf G))).getD 0 } : CRule K)) = Prod.snd := by
    funext x; rfl
  rw [this, List.zipIdx_map_snd]
  exact List.nodup_range'

theorem rule_lhs_lt (hG : G.wf = true) {r : Nat} {R0 : Rule K} (hr : G.rules[r]? = some R0) :
    R0.lhs < G.rank.size := by
  have h := rule_wf_of_mem hG hr
  simp only [Rule.wf, Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1.1.1

theorem rule_head_rank (hG : G.wf = true) {r : Nat} {R0 : Rule K} (hr : G.rules[r]? = some R0) {B : Nat}
    {rest : List (Sym K)} (hrhs : R0.rhs = .n B :: rest) : G.rank.getD B 0 < G.rank.getD R0.lhs 0 := by
  have h := rule_wf_of_mem hG hr
  simp only [Rule.wf, Bool.and_eq_true, hrhs, decide_eq_true_eq] at h
  exact h.2

end Prepared

section Row

variable {T K : Type} [DecidableEq T] [DecidableEq K] [Accepts K T]
variable {G : Grammar K} {cap : Nat} {w : Array T}

/-- The root rule of a tree is in `D`. -/
def rootIn (D : Nat → Prop) : Tree T → Prop
  | .node r _ => D r
  | .leaf _ => False

/-- The suffix entries of the start position `p` are complete-or-full. -/
def SufRowOk (G : Grammar K) (cap : Nat) (w : Array T) (p : Nat) (row : SufRow T) : Prop :=
  ∀ r R0, G.rules[r]? = some R0 → ∀ d, 1 ≤ d → d < R0.rhs.length →
    BOk cap w.size (SpanAll G w (R0.rhs.drop d) p) ((row.getD r #[]).getD d [])

/-- The nonterminal entries of the start position `i` are complete-or-full for the derivations whose
root rule is in `D`. -/
def NtOk (G : Grammar K) (cap : Nat) (w : Array T) (i : Nat) (D : Nat → Prop) (row : NtRow T) : Prop :=
  row.size = G.rank.size ∧ ∀ A, BOk cap w.size (fun j t => Span G w (.n A) i j t ∧ rootIn D t) (row.getD A [])

omit [DecidableEq T] [DecidableEq K] in
theorem derives_root {A : Nat} {t : Tree T} (h : t.derives G (.n A) = true) :
    ∃ r ks R0, t = .node r ks ∧ G.rules[r]? = some R0 ∧ R0.lhs = A ∧ derivesAll G R0.rhs ks = true := by
  match t, h with
  | .leaf _, h => simp [Tree.derives] at h
  | .node r ks, h =>
    rw [derives_node] at h
    cases hr : G.rules[r]? with
    | none => simp [hr] at h
    | some R0 =>
      simp only [hr, Bool.and_eq_true, beq_iff_eq] at h
      exact ⟨r, ks, R0, rfl, hr, h.1, h.2⟩

omit [DecidableEq T] [DecidableEq K] in
theorem span_node {A r : Nat} {R0 : Rule K} {i j : Nat} {ks : List (Tree T)} (hr : G.rules[r]? = some R0)
    (hA : R0.lhs = A) : Span G w (.n A) i j (.node r ks) ↔ SpanAll G w R0.rhs i j ks := by
  unfold Span SpanAll Derives
  rw [derives_node, hr, yield_node]
  simp [hA]

omit [DecidableEq T] [DecidableEq K] in
theorem span_term {a : K} {i j : Nat} {t : Tree T} (hi : i < w.size) (hj : j ≤ w.size) :
    Span G w (.t a) i j t ↔ t = .leaf w[i] ∧ Accepts.accepts a w[i] = true ∧ j = i + 1 := by
  constructor
  · intro ⟨hd, hy⟩
    match t, hd with
    | .node _ _, hd => simp [Tree.derives] at hd
    | .leaf y, hd =>
      rw [derives_leaf] at hd
      rw [yield_leaf] at hy
      have hl : ([y] : List T).length = (toks w i j).length := congrArg List.length hy
      rw [toks_length hj] at hl
      simp at hl
      have hj1 : j = i + 1 := by omega
      subst hj1
      have : [y] = [w[i]] := hy.trans (toks_one hi)
      simp at this
      subst this
      exact ⟨rfl, hd, rfl⟩
  · rintro ⟨rfl, ha, rfl⟩
    exact ⟨by rw [derives_leaf]; exact ha, by rw [yield_leaf]; exact (toks_one hi).symm⟩

theorem firstAt_term_ok {a : K} {i : Nat} {row : NtRow T} (hi : i < w.size) (hcap : 0 < cap) :
    BOk cap w.size (Span G w (.t a) i) (firstAt w i row (.t a)) := by
  have hw : w[i]? = some w[i] := by simp [hi]
  unfold firstAt
  rw [hw]
  simp only
  split
  · rename_i hacc
    refine ⟨by simp [Bucket.Sorted], by simp; omega, ?_, ?_, ?_, ?_⟩
    · intro j; rw [Bucket.get_cons, Bucket.get_nil]; split <;> simp
    · intro j x hx
      rw [Bucket.get_cons, Bucket.get_nil] at hx
      split at hx
      · rename_i hj
        simp at hx
        subst hx hj
        exact (span_term hi (by omega)).mpr ⟨rfl, hacc, rfl⟩
      · simp at hx
    · intro j; rw [Bucket.get_cons, Bucket.get_nil]; split <;> simp <;> omega
    · intro j hj _ x hx
      obtain ⟨rfl, _, rfl⟩ := (span_term hi hj).mp hx
      simp [Bucket.get_cons]
  · rename_i hacc
    exact BOk.nil (fun j x hj _ hx => hacc ((span_term hi hj).mp hx).2.1)

omit [DecidableEq T] in
theorem getD_modify {X : Type} {row : Array X} {k A : Nat} {f : X → X} {d : X} (hk : k < row.size) :
    (row.modify k f).getD A d = if A = k then f (row.getD A d) else row.getD A d := by
  simp only [Array.getD_eq_getD_getElem?, Array.getElem?_modify]
  by_cases h : A = k
  · subst h; simp [hk]
  · simp [Ne.symm h, h]

omit [DecidableEq T] [DecidableEq K] [Accepts K T] in
theorem addAll_nil {X : Type} {e : Bucket X} : e.addAll cap [] = e := by
  simp [Bucket.addAll, Bucket.merge]

/-- One rule applied at the start position `i`: its candidates added to the entry of its left-hand side
keep the entries complete-or-full, with the rule added to the done set. -/
theorem ruleStep_ok (hG : G.wf = true) (hcap : 0 < cap) {i : Nat} (hi : i < w.size)
    {suf : Array (SufRow T)} (hsuf : ∀ p, i < p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[]))
    {D : Nat → Prop} {row : NtRow T} (hrow : NtOk G cap w i D row)
    {R : CRule K} {R0 : Rule K} (hR0 : G.rules[R.index]? = some R0) (hlhs : R0.lhs = R.lhs)
    {Y : Sym K} {rest : List (Sym K)} (hrhs : R0.rhs = Y :: rest) (hnot : ¬ D R.index)
    (hdone : ∀ B, Y = .n B → ∀ r R1, G.rules[r]? = some R1 → R1.lhs = B → D r)
    {row2 : NtRow T} (hsize : row2.size = row.size)
    (hget : ∀ A, row2.getD A [] = if A = R.lhs then (row.getD A []).addAll cap
      ((combine (firstAt w i row Y) (fun j1 => sufGet suf j1 R.index 1) rest.isEmpty).map
        fun c => (c.1, Tree.node R.index c.2)) else row.getD A []) :
    NtOk G cap w i (fun r => D r ∨ r = R.index) row2 := by
  refine ⟨hsize.trans hrow.1, fun A => ?_⟩
  rw [hget A]
  split
  · rename_i hA
    subst hA
    -- the first symbol's entry
    have hF : BOk cap w.size (Span G w Y i) (firstAt w i row Y) := by
      match Y, hdone with
      | .t a, _ => exact firstAt_term_ok hi hcap
      | .n B, hdone =>
        have := hrow.2 B
        refine BOk.congr this (fun j t _ => ⟨fun h => h.1, fun h => ⟨h, ?_⟩⟩)
        obtain ⟨r, ks, R1, rfl, hr1, hl1, _⟩ := derives_root h.1
        exact hdone B rfl r R1 hr1 hl1
    -- the suffix entries of the rest
    have hN : rest ≠ [] → ∀ j1, i < j1 → j1 ≤ w.size →
        BOk cap w.size (SpanAll G w rest j1) (sufGet suf j1 R.index 1) := by
      intro hr j1 h1 h2
      have := hsuf j1 h1 h2 R.index R0 hR0 1 (Nat.le_refl 1) (by
        rw [hrhs]; simp; exact List.length_pos_iff.mpr hr)
      rw [hrhs] at this
      exact this
    obtain ⟨hca, hcn, hcc⟩ := combine_ok hG rfl hF hN
    have hB := BOk.addAll (cands := (combine (firstAt w i row Y) (fun j1 => sufGet suf j1 R.index 1)
        rest.isEmpty).map fun c => (c.1, Tree.node R.index c.2))
      (Pold := fun j t => Span G w (.n R.lhs) i j t ∧ rootIn D t)
      (Pnew := fun j t => Span G w (.n R.lhs) i j t ∧ ∃ ks, t = .node R.index ks)
      (hrow.2 R.lhs) ?_ ?_ ?_ ?_
    · refine BOk.congr hB (fun j t _ => ?_)
      constructor
      · rintro (⟨hs, hr⟩ | ⟨hs, ks, rfl⟩)
        · refine ⟨hs, ?_⟩
          match t, hr with
          | .node r _, hr => exact Or.inl hr
        · exact ⟨hs, Or.inr rfl⟩
      · rintro ⟨hs, hr⟩
        match t, hr with
        | .node r ks, Or.inl hr => exact Or.inl ⟨hs, hr⟩
        | .node r ks, Or.inr hr => subst hr; exact Or.inr ⟨hs, ks, rfl⟩
    · intro c hc
      obtain ⟨c0, hc0, rfl⟩ := List.mem_map.mp hc
      obtain ⟨hle, hs⟩ := hca c0 hc0
      refine ⟨hle, (span_node hR0 hlhs).mpr (by rw [hrhs]; exact hs), c0.2, rfl⟩
    · apply nodup_map_of_inj hcn
      intro a _ b _ he
      simp only [Prod.mk.injEq, Tree.node.injEq, true_and] at he
      exact Prod.ext he.1 he.2
    · intro j hj
      rcases hcc j hj with h | h
      · left
        rw [List.filter_map, List.length_map]
        exact h
      · right
        rintro t ⟨hs, ks, rfl⟩
        have := h ks (by rw [← hrhs]; exact (span_node hR0 hlhs).mp hs)
        exact List.mem_map.mpr ⟨(j, ks), this, rfl⟩
    · rintro j t ⟨_, hr⟩ ⟨_, ks, rfl⟩
      exact hnot hr
  · rename_i hA
    refine BOk.congr (hrow.2 A) (fun j t _ => ⟨fun ⟨hs, hr⟩ => ⟨hs, ?_⟩, fun ⟨hs, hr⟩ => ⟨hs, ?_⟩⟩)
    · match t, hr with
      | .node r _, hr => exact Or.inl hr
    · match t, hr with
      | .node r ks, Or.inl hr => exact hr
      | .node r ks, Or.inr hr =>
        subst hr
        obtain ⟨r2, ks2, R1, he, hr1, hl1, _⟩ := derives_root hs.1
        simp only [Tree.node.injEq] at he
        obtain ⟨rfl, rfl⟩ := he
        rw [hR0] at hr1
        cases hr1
        exact absurd (hl1.symm.trans hlhs) hA

omit [DecidableEq T] [DecidableEq K] in
theorem NtOk.congr {i : Nat} {D D2 : Nat → Prop} {row : NtRow T} (h : NtOk G cap w i D row)
    (hD : ∀ r, D r ↔ D2 r) : NtOk G cap w i D2 row := by
  refine ⟨h.1, fun A => BOk.congr (h.2 A) (fun j t _ => ?_)⟩
  match t with
  | .leaf _ => simp [rootIn]
  | .node r _ => simp [rootIn, hD r]

omit [DecidableEq T] in
/-- A rule that indexing skips has nothing to start with at the row. -/
theorem firstAt_nil_of_avail {i : Nat} (hi : i < w.size) {row : NtRow T} {R : CRule K}
    (hR : R ∈ G.prepare.order) {Y : Sym K} {rest : List (Sym K)} (hrhs : R.rhs = Y :: rest)
    (h : avail (accepted (termsOf G) w i) row R Y = false) : firstAt w i row Y = [] := by
  match Y, h with
  | .n B, h =>
    unfold avail at h
    unfold firstAt
    simpa using h
  | .t a, h =>
    obtain ⟨R0, hR0, _, hrhs0, hfirst⟩ := mem_order hR
    have ha : a ∈ termsOf G := mem_termsOf hR0 (by rw [hrhs0, hrhs]; simp)
    obtain ⟨hlt, hidx⟩ := getElem_idxOf ha
    have hw : w[i]? = some w[i] := by simp [hi]
    unfold avail at h
    rw [hfirst, hrhs] at h
    simp only [List.head?_cons, Option.map_some, Option.getD_some, termIndex] at h
    unfold accepted at h
    rw [hw] at h
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_map, Array.getElem?_eq_getElem hlt, hidx,
      Option.map_some, Option.getD_some] at h
    unfold firstAt
    rw [hw]
    simp [h]

/-- The rules applied at the start position `i` in the order of `prepare`: every entry of the row is
complete-or-full for all the derivations. -/
theorem ntRowGo_ok (hG : G.wf = true) (hcap : 0 < cap) {i : Nat} (hi : i < w.size)
    {suf : Array (SufRow T)} (hsuf : ∀ p, i < p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[])) :
    ∀ (post pre : List (CRule K)) (row : NtRow T) (steps : Nat), pre ++ post = G.prepare.order →
    NtOk G cap w i (fun r => r ∈ pre.map (·.index)) row →
    NtOk G cap w i (fun r => r ∈ G.prepare.order.map (·.index))
      (ntRowGo (accepted (termsOf G) w i) cap w i suf post row steps).1
  | [], pre, row, steps, hpo, hrow => by
    simp only [List.append_nil] at hpo
    subst hpo
    simpa [ntRowGo] using hrow
  | R :: Rs, pre, row, steps, hpo, hrow => by
    have hRmem : R ∈ G.prepare.order := by rw [← hpo]; simp
    obtain ⟨R0, hR0, hlhs, hrhs0, hfirst⟩ := mem_order hRmem
    have hnot : ¬ R.index ∈ pre.map (·.index) := by
      have hn := order_nodup (G := G)
      rw [← hpo, List.map_append, List.map_cons] at hn
      exact fun hm => (List.nodup_append.mp hn).2.2 _ hm _ (by simp) rfl
    have hD : ∀ r, (r ∈ pre.map (·.index) ∨ r = R.index) ↔ r ∈ (pre ++ [R]).map (·.index) := by
      intro r; simp [eq_comm]
    have hpo2 : (pre ++ [R]) ++ Rs = G.prepare.order := by rw [← hpo]; simp
    have hdone : ∀ B, (∃ rest, R.rhs = .n B :: rest) → ∀ r R1, G.rules[r]? = some R1 → R1.lhs = B →
        r ∈ pre.map (·.index) := by
      rintro B ⟨rest, hrest⟩ r R1 hr1 hl1
      have hrank := rule_head_rank hG hR0 (hrhs0.trans hrest)
      obtain ⟨R', hR', hidx, hl'⟩ := order_complete hr1
      rw [← hpo] at hR'
      rcases List.mem_append.mp hR' with h | h
      · exact List.mem_map.mpr ⟨R', h, hidx⟩
      · exfalso
        have hs := order_sorted (G := G)
        rw [← hpo] at hs
        rcases List.mem_cons.mp h with h | h
        · subst h; rw [hl', hl1] at hlhs; rw [hlhs] at hrank; omega
        · have := (List.pairwise_cons.mp (List.pairwise_append.mp hs).2.1).1 R' h
          rw [hl', hl1, ← hlhs] at this
          omega
    unfold ntRowGo
    split
    · rename_i hr
      exact absurd (hrhs0.trans hr) (rhs_ne_nil_of_mem hG hR0)
    · rename_i Y rest hr
      have hrhs : R0.rhs = Y :: rest := hrhs0.trans hr
      have hstep := fun (row2 : NtRow T) => ruleStep_ok hG hcap hi hsuf hrow hR0 hlhs hrhs hnot
        (fun B hB r R1 hr1 hl1 => hdone B ⟨rest, hB ▸ hr⟩ r R1 hr1 hl1) (row2 := row2)
      have hsz : row.size = G.rank.size := hrow.1
      have hlt : R.lhs < row.size := by rw [hsz, ← hlhs]; exact rule_lhs_lt hG hR0
      split
      · split
        · rename_i hav hnil
          refine ntRowGo_ok hG hcap hi hsuf Rs (pre ++ [R]) _ _ hpo2 (NtOk.congr (hstep row rfl fun A => ?_) hD)
          rw [hnil]; split <;> simp [addAll_nil]
        · rename_i hav cands hcands
          refine ntRowGo_ok hG hcap hi hsuf Rs (pre ++ [R]) _ _ hpo2 (NtOk.congr (hstep _ Array.size_modify fun A => ?_) hD)
          rw [getD_modify hlt]
      · rename_i hav
        have hnil := firstAt_nil_of_avail hi hRmem hr (by simpa using hav)
        refine ntRowGo_ok hG hcap hi hsuf Rs (pre ++ [R]) _ _ hpo2 (NtOk.congr (hstep row rfl fun A => ?_) hD)
        rw [hnil]
        have : combine ([] : Bucket (Tree T)) (fun j1 => sufGet suf j1 R.index 1) rest.isEmpty = [] := by
          simp [combine]
        rw [this]; split <;> simp [addAll_nil]

end Row

section Positions

variable {K : Type} [DecidableEq K]
variable {G : Grammar K}

/-- A position `d ≥ 1` of a rule's right-hand side, with its symbol and whether it is the last. -/
def ValidPos (G : Grammar K) (p : SufPos K) : Prop :=
  ∃ R0, G.rules[p.rule]? = some R0 ∧ 1 ≤ p.pos ∧ ∃ h : p.pos < R0.rhs.length,
    p.sym = R0.rhs[p.pos] ∧ p.last = (R0.rhs.drop (p.pos + 1)).isEmpty

theorem mem_sufPositions_succ {r : Nat} {p : SufPos K} : ∀ {l : List (Sym K)} {d0 : Nat}, 1 ≤ d0 →
    (p ∈ sufPositions r l d0 ↔ ∃ k, ∃ h : k < l.length, p = ⟨r, d0 + k, l[k], (l.drop (k + 1)).isEmpty⟩)
  | [], _, _ => by simp [sufPositions]
  | Y :: rest, d0, h0 => by
    unfold sufPositions
    rw [if_neg (by omega), List.mem_cons, mem_sufPositions_succ (by omega)]
    constructor
    · rintro (rfl | ⟨k, hk, rfl⟩)
      · exact ⟨0, by simp, by simp⟩
      · refine ⟨k + 1, by simp; omega, ?_⟩
        simp only [List.getElem_cons_succ, List.drop_succ_cons, SufPos.mk.injEq, true_and, and_true]
        omega
    · rintro ⟨k, hk, rfl⟩
      cases k with
      | zero => left; simp
      | succ k =>
        right
        refine ⟨k, by simp at hk; omega, ?_⟩
        simp only [List.getElem_cons_succ, List.drop_succ_cons, SufPos.mk.injEq, true_and, and_true]
        omega

theorem mem_sufPositions {r : Nat} {p : SufPos K} {l : List (Sym K)} :
    p ∈ sufPositions r l 0 ↔ ∃ d, 1 ≤ d ∧ ∃ h : d < l.length, p = ⟨r, d, l[d], (l.drop (d + 1)).isEmpty⟩ := by
  match l with
  | [] => simp [sufPositions]
  | Y :: rest =>
    unfold sufPositions
    rw [if_pos rfl, mem_sufPositions_succ (Nat.le_refl 1)]
    constructor
    · rintro ⟨k, hk, rfl⟩
      refine ⟨k + 1, by omega, by simp; omega, ?_⟩
      simp only [SufPos.mk.injEq, List.getElem_cons_succ, List.drop_succ_cons, true_and, and_true]
      omega
    · rintro ⟨d, hd, hdl, rfl⟩
      obtain ⟨d2, rfl⟩ : ∃ d2, d = d2 + 1 := ⟨d - 1, by omega⟩
      refine ⟨d2, by simp at hdl; omega, ?_⟩
      simp only [SufPos.mk.injEq, List.getElem_cons_succ, List.drop_succ_cons, true_and, and_true]
      omega

/-- The positions that `prepare` lists. -/
def allPositions (G : Grammar K) : List (SufPos K) :=
  G.rules.toList.zipIdx.flatMap fun (R, r) => sufPositions r R.rhs 0

theorem mem_allPositions {p : SufPos K} : p ∈ allPositions G ↔ ValidPos G p := by
  unfold allPositions ValidPos
  rw [List.mem_flatMap]
  constructor
  · rintro ⟨⟨R0, r⟩, hm, hp⟩
    have hr := List.mem_zipIdx_iff_getElem?.mp hm
    simp only [Array.getElem?_toList] at hr
    obtain ⟨d, hd, hdl, rfl⟩ := mem_sufPositions.mp hp
    exact ⟨R0, hr, hd, hdl, rfl, rfl⟩
  · rintro ⟨R0, hr, hd, hdl, hsym, hlast⟩
    refine ⟨(R0, p.rule), List.mem_zipIdx_iff_getElem?.mpr (by simpa using hr), ?_⟩
    apply mem_sufPositions.mpr
    refine ⟨p.pos, hd, hdl, ?_⟩
    cases p
    simp only at hsym hlast ⊢
    rw [hsym, hlast]

theorem getD_modify_any {α : Type} {g : Array α} {k2 k : Nat} {f : α → α} {d : α} :
    (g.modify k2 f).getD k d = if k2 = k ∧ k2 < g.size then f (g.getD k d) else g.getD k d := by
  simp only [Array.getD_eq_getD_getElem?, Array.getElem?_modify]
  by_cases h : k2 = k
  · subst h
    by_cases hlt : k2 < g.size
    · simp [hlt]
    · simp [hlt, Array.getElem?_eq_none (Nat.le_of_not_lt hlt)]
  · simp [h]

/-- One step of `groupBy`. -/
def groupStep {α : Type} (key : α → Option Nat) (g : Array (List α)) (x : α) : Array (List α) :=
  match key x with
  | some k => g.modify k (x :: ·)
  | none => g

theorem groupStep_spec {α : Type} {n : Nat} {key : α → Option Nat} {g : Array (List α)} {y x : α} {k : Nat}
    (hg : g.size = n) : (groupStep key g y).size = n ∧
    (x ∈ (groupStep key g y).getD k [] ↔ x ∈ g.getD k [] ∨ (x = y ∧ key y = some k ∧ k < n)) := by
  unfold groupStep
  cases hk : key y with
  | none => simp [hg]
  | some k2 =>
    simp only [Array.size_modify, hg, true_and, getD_modify_any, Option.some.injEq]
    by_cases h : k2 = k ∧ k2 < n
    · rw [if_pos h]
      obtain ⟨rfl, hlt⟩ := h
      simp only [List.mem_cons]
      constructor
      · rintro (rfl | h)
        · right; exact ⟨rfl, by trivial, by omega⟩
        · left; exact h
      · rintro (h | ⟨rfl, _, _⟩)
        · right; exact h
        · left; rfl
    · rw [if_neg h]
      constructor
      · intro h2; left; exact h2
      · rintro (h2 | ⟨_, rfl, hn⟩)
        · exact h2
        · exact absurd ⟨rfl, by omega⟩ h

theorem groupBy_spec {α : Type} {n : Nat} {key : α → Option Nat} {x : α} {k : Nat} :
    ∀ (xs : List α) (g : Array (List α)), g.size = n →
      (xs.foldl (groupStep key) g).size = n ∧
      (x ∈ (xs.foldl (groupStep key) g).getD k [] ↔ x ∈ g.getD k [] ∨ (x ∈ xs ∧ key x = some k ∧ k < n))
  | [], g, hg => by simp [hg]
  | y :: ys, g, hg => by
    rw [List.foldl_cons]
    have ⟨hsz, hstep⟩ := groupStep_spec (key := key) (y := y) (x := x) (k := k) hg
    obtain ⟨h1, h2⟩ := groupBy_spec ys _ hsz
    refine ⟨h1, ?_⟩
    rw [h2, hstep]
    constructor
    · rintro ((h | ⟨rfl, hk, hn⟩) | ⟨h, hk, hn⟩)
      · left; exact h
      · right; exact ⟨by simp, hk, hn⟩
      · right; exact ⟨by simp [h], hk, hn⟩
    · rintro (h | ⟨h, hk, hn⟩)
      · left; left; exact h
      · rcases List.mem_cons.mp h with rfl | h
        · left; right; exact ⟨rfl, hk, hn⟩
        · right; exact ⟨h, hk, hn⟩

theorem groupBy_eq {α : Type} {n : Nat} {key : α → Option Nat} {xs : List α} :
    groupBy n key xs = xs.foldl (groupStep key) (Array.replicate n []) := by
  unfold groupBy groupStep
  rfl

theorem mem_groupBy {α : Type} {n : Nat} {key : α → Option Nat} {xs : List α} {x : α} {k : Nat} :
    x ∈ (groupBy n key xs).getD k [] ↔ x ∈ xs ∧ key x = some k ∧ k < n := by
  rw [groupBy_eq, (groupBy_spec (n := n) xs _ (by simp)).2]
  simp only [Array.getD_eq_getD_getElem?, Array.getElem?_replicate]
  constructor
  · rintro (h | h)
    · split at h <;> simp at h
    · exact h
  · intro h; exact Or.inr h

theorem mem_groupList {α : Type} {g : Array (List α)} {k : Nat} {xs : List α} :
    (k, xs) ∈ groupList g ↔ g[k]? = some xs ∧ xs ≠ [] := by
  unfold groupList
  rw [List.mem_filterMap]
  constructor
  · rintro ⟨⟨ys, k2⟩, hm, he⟩
    have := List.mem_zipIdx_iff_getElem?.mp hm
    simp only [Array.getElem?_toList] at this
    by_cases hne : ys.isEmpty
    · simp [hne] at he
    · simp only [hne, Bool.false_eq_true, if_false, Option.some.injEq, Prod.mk.injEq] at he
      obtain ⟨rfl, rfl⟩ := he
      exact ⟨this, by simpa using hne⟩
  · rintro ⟨hk, hne⟩
    refine ⟨(xs, k), List.mem_zipIdx_iff_getElem?.mpr (by simpa using hk), ?_⟩
    simp [List.isEmpty_iff, hne]

/-- The key of a position in `byTerm`: the index of its terminal. -/
def termKey (G : Grammar K) (p : SufPos K) : Option Nat :=
  match p.sym with
  | .t a => some ((termsOf G).idxOf a)
  | .n _ => none

/-- The key of a position in `byNt`: its nonterminal. -/
def ntKey (p : SufPos K) : Option Nat :=
  match p.sym with
  | .n B => some B
  | .t _ => none

theorem prepare_byTerm : G.prepare.byTerm = groupList (groupBy (termsOf G).size (termKey G) (allPositions G)) :=
  rfl

theorem prepare_byNt : G.prepare.byNt = groupList (groupBy G.rank.size ntKey (allPositions G)) := rfl

theorem groupBy_size {α : Type} {n : Nat} {key : α → Option Nat} {xs : List α} : (groupBy n key xs).size = n := by
  rw [groupBy_eq]
  cases xs with
  | nil => simp
  | cons x _ => exact (groupBy_spec (x := x) (k := 0) _ _ (by simp)).1

/-- A position is in a group of `byTerm` or of `byNt`, under the key of its symbol. -/
theorem mem_groups {p : SufPos K} (hG : G.wf = true) (hp : ValidPos G p) :
    (∃ a, p.sym = .t a ∧ ∃ g, ((termsOf G).idxOf a, g) ∈ G.prepare.byTerm ∧ p ∈ g) ∨
    (∃ B, p.sym = .n B ∧ ∃ g, (B, g) ∈ G.prepare.byNt ∧ p ∈ g) := by
  have hall : p ∈ allPositions G := mem_allPositions.mpr hp
  obtain ⟨R0, hr, _, hdl, hsym, _⟩ := hp
  match hs : p.sym with
  | .t a =>
    left
    have hlt : (termsOf G).idxOf a < (termsOf G).size :=
      Array.idxOf_lt_length_of_mem (mem_termsOf hr (by rw [← hs, hsym]; simp))
    have hmem : p ∈ (groupBy (termsOf G).size (termKey G) (allPositions G)).getD ((termsOf G).idxOf a) [] :=
      mem_groupBy.mpr ⟨hall, by simp [termKey, hs], hlt⟩
    refine ⟨a, rfl, _, ?_, hmem⟩
    rw [prepare_byTerm]
    apply mem_groupList.mpr
    refine ⟨?_, List.ne_nil_of_mem hmem⟩
    have hlt' : (termsOf G).idxOf a < (groupBy (termsOf G).size (termKey G) (allPositions G)).size := by
      rw [groupBy_size]; exact hlt
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_eq_getElem hlt', Option.getD_some]
  | .n B =>
    right
    have hB : B < G.rank.size := by
      have h := rule_wf_of_mem hG hr
      simp only [Rule.wf, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
      have := h.1.2 (.n B) (by rw [← hs, hsym]; simp)
      simpa using this
    have hmem : p ∈ (groupBy G.rank.size ntKey (allPositions G)).getD B [] :=
      mem_groupBy.mpr ⟨hall, by simp [ntKey, hs], hB⟩
    refine ⟨B, rfl, _, ?_, hmem⟩
    rw [prepare_byNt]
    apply mem_groupList.mpr
    refine ⟨?_, List.ne_nil_of_mem hmem⟩
    have hB' : B < (groupBy G.rank.size ntKey (allPositions G)).size := by
      rw [groupBy_size]; exact hB
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_eq_getElem hB', Option.getD_some]

theorem byTerm_sym {k : Nat} {g : List (SufPos K)} (h : (k, g) ∈ G.prepare.byTerm) {p : SufPos K} (hp : p ∈ g) :
    ValidPos G p ∧ ∃ a, p.sym = .t a ∧ (termsOf G).idxOf a = k := by
  rw [prepare_byTerm] at h
  have ⟨hk, _⟩ := mem_groupList.mp h
  have hp' : p ∈ (groupBy (termsOf G).size (termKey G) (allPositions G)).getD k [] := by
    rw [Array.getD_eq_getD_getElem?, hk]; exact hp
  have hmem := mem_groupBy.mp hp'
  refine ⟨mem_allPositions.mp hmem.1, ?_⟩
  have hkey := hmem.2.1
  unfold termKey at hkey
  match hs : p.sym, hkey with
  | .t a, hkey => simp at hkey; exact ⟨a, rfl, hkey⟩
  | .n _, hkey => simp at hkey

theorem byNt_sym {B : Nat} {g : List (SufPos K)} (h : (B, g) ∈ G.prepare.byNt) {p : SufPos K} (hp : p ∈ g) :
    ValidPos G p ∧ p.sym = .n B := by
  rw [prepare_byNt] at h
  have ⟨hk, _⟩ := mem_groupList.mp h
  have hp' : p ∈ (groupBy G.rank.size ntKey (allPositions G)).getD B [] := by
    rw [Array.getD_eq_getD_getElem?, hk]; exact hp
  have hmem := mem_groupBy.mp hp'
  refine ⟨mem_allPositions.mp hmem.1, ?_⟩
  have hkey := hmem.2.1
  unfold ntKey at hkey
  match hs : p.sym, hkey with
  | .n B2, hkey => simp at hkey; rw [hkey]
  | .t _, hkey => simp at hkey

theorem ValidPos.unique {p q : SufPos K} (hp : ValidPos G p) (hq : ValidPos G q) (hr : p.rule = q.rule)
    (hd : p.pos = q.pos) : p = q := by
  obtain ⟨R0, h0, _, hl0, hs0, hz0⟩ := hp
  obtain ⟨R1, h1, _, hl1, hs1, hz1⟩ := hq
  obtain ⟨r1, d1, s1, l1⟩ := p
  obtain ⟨r2, d2, s2, l2⟩ := q
  simp only at hr hd hs0 hs1 hz0 hz1 h0 h1 hl0 hl1
  subst hr hd
  rw [h0] at h1
  cases h1
  simp only [SufPos.mk.injEq, true_and]
  exact ⟨hs0.trans hs1.symm, hz0.trans hz1.symm⟩

end Positions

section Rows

variable {T K : Type} [DecidableEq T] [DecidableEq K] [Accepts K T]
variable {G : Grammar K} {cap : Nat} {w : Array T}

/-- The value of the suffix entry of a position at the start position `i`. -/
def sufVal (cap : Nat) (w : Array T) (i : Nat) (nt : NtRow T) (suf : Array (SufRow T)) (p : SufPos K) :
    Bucket (List (Tree T)) :=
  Bucket.addAll cap [] (combine (firstAt w i nt p.sym) (fun j1 => sufGet suf j1 p.rule (p.pos + 1)) p.last)

/-- The suffix entry of the rule `r` at position `d` in a suffix row. -/
def outAt (out : SufRow T) (r d : Nat) : Bucket (List (Tree T)) := (out.getD r #[]).getD d []

/-- A suffix row being filled: each entry is still empty or has its value, and has its value once its
position is done. -/
structure OutInv (G : Grammar K) (cap : Nat) (w : Array T) (i : Nat) (nt : NtRow T) (suf : Array (SufRow T))
    (Done : Nat → Nat → Prop) (out : SufRow T) : Prop where
  size : out.size = G.rules.size
  inner : ∀ r R0, G.rules[r]? = some R0 → (out.getD r #[]).size = R0.rhs.length
  val : ∀ p, ValidPos G p → outAt out p.rule p.pos = [] ∨ outAt out p.rule p.pos = sufVal cap w i nt suf p
  done : ∀ p, ValidPos G p → Done p.rule p.pos → outAt out p.rule p.pos = sufVal cap w i nt suf p

omit [DecidableEq T] in
theorem OutInv.mono {i : Nat} {nt : NtRow T} {suf : Array (SufRow T)} {D D2 : Nat → Nat → Prop}
    {out : SufRow T} (h : OutInv G cap w i nt suf D out) (hD : ∀ r d, D2 r d → D r d) :
    OutInv G cap w i nt suf D2 out :=
  ⟨h.size, h.inner, h.val, fun p hp hd => h.done p hp (hD _ _ hd)⟩

omit [DecidableEq T] [DecidableEq K] [Accepts K T] in
theorem outAt_write {out : SufRow T} {r0 d0 r d : Nat} {v : Bucket (List (Tree T))} (hr : r0 < out.size)
    (hd : d0 < (out.getD r0 #[]).size) :
    outAt (out.modify r0 fun e => e.setIfInBounds d0 v) r d = if r = r0 ∧ d = d0 then v else outAt out r d := by
  unfold outAt
  rw [getD_modify hr]
  by_cases h1 : r = r0
  · subst h1
    simp only [if_pos rfl, true_and]
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_setIfInBounds]
    by_cases h2 : d = d0
    · subst h2
      simp only [Array.getD_eq_getD_getElem?] at hd
      simp [hd]
    · simp [Ne.symm h2, h2]
  · simp [h1]

theorem sufPosGo_ok {i : Nat} {nt : NtRow T} {suf : Array (SufRow T)} :
    ∀ (ps : List (SufPos K)) (out : SufRow T) (c : Nat) (D : Nat → Nat → Prop),
    (∀ p ∈ ps, ValidPos G p) → OutInv G cap w i nt suf D out →
    OutInv G cap w i nt suf (fun r d => D r d ∨ ∃ p ∈ ps, p.rule = r ∧ p.pos = d)
      (sufPosGo cap w i nt suf ps out c).1
  | [], out, c, D, _, h => by
    simp only [sufPosGo]
    exact h.mono (fun r d hd => by simpa using hd)
  | p :: ps, out, c, D, hv, h => by
    have hp := hv p (by simp)
    have hvs : ∀ q ∈ ps, ValidPos G q := fun q hq => hv q (by simp [hq])
    have hD : ∀ r d, (D r d ∨ ∃ q ∈ p :: ps, q.rule = r ∧ q.pos = d) →
        ((D r d ∨ (r = p.rule ∧ d = p.pos)) ∨ ∃ q ∈ ps, q.rule = r ∧ q.pos = d) := by
      rintro r d (h | ⟨q, hq, hqr, hqd⟩)
      · exact Or.inl (Or.inl h)
      · rcases List.mem_cons.mp hq with rfl | hq
        · exact Or.inl (Or.inr ⟨hqr.symm, hqd.symm⟩)
        · exact Or.inr ⟨q, hq, hqr, hqd⟩
    unfold sufPosGo
    cases hc : combine (firstAt w i nt p.sym) (fun j1 => sufGet suf j1 p.rule (p.pos + 1)) p.last with
    | nil =>
      have h2 : OutInv G cap w i nt suf (fun r d => D r d ∨ (r = p.rule ∧ d = p.pos)) out := by
        refine ⟨h.size, h.inner, h.val, ?_⟩
        rintro q hq (hd | ⟨hr, hd⟩)
        · exact h.done q hq hd
        · have := ValidPos.unique hq hp hr hd
          subst this
          have hv0 : sufVal cap w i nt suf q = [] := by
            unfold sufVal; rw [hc]; simp [Bucket.addAll, Bucket.merge]
          rcases h.val q hq with e | e <;> simp [e, hv0]
      exact (sufPosGo_ok ps out c _ hvs h2).mono hD
    | cons c0 cs =>
      obtain ⟨R0, hR0, _, hdl, _, _⟩ := hp
      have hr : p.rule < out.size := by
        rw [h.size]; exact (Array.getElem?_eq_some_iff.mp hR0).1
      have hd : p.pos < (out.getD p.rule #[]).size := by rw [h.inner _ _ hR0]; exact hdl
      have hval : ∀ q, ValidPos G q → q.rule = p.rule → q.pos = p.pos →
          Bucket.addAll cap [] (c0 :: cs) = sufVal cap w i nt suf q := by
        intro q hq hr hd
        have := ValidPos.unique hq (hv p (by simp)) hr hd
        subst this
        unfold sufVal
        rw [hc]
      have h2 : OutInv G cap w i nt suf (fun r d => D r d ∨ (r = p.rule ∧ d = p.pos))
          (out.modify p.rule fun e => e.setIfInBounds p.pos (Bucket.addAll cap [] (c0 :: cs))) := by
        refine ⟨by simp [h.size], ?_, ?_, ?_⟩
        · intro r R1 hR1
          rw [getD_modify hr]
          split
          · rename_i he; subst he; rw [Array.size_setIfInBounds]; exact h.inner _ _ hR1
          · exact h.inner _ _ hR1
        · intro q hq
          rw [outAt_write hr hd]
          split
          · rename_i he; exact Or.inr (hval q hq he.1 he.2)
          · exact h.val q hq
        · rintro q hq hdn
          rw [outAt_write hr hd]
          split
          · rename_i he; exact hval q hq he.1 he.2
          · rename_i he
            rcases hdn with hdn | ⟨hr2, hd2⟩
            · exact h.done q hq hdn
            · exact absurd ⟨hr2, hd2⟩ he
      exact (sufPosGo_ok ps _ _ _ hvs h2).mono hD

theorem sufGroups_ok {i : Nat} {nt : NtRow T} {suf : Array (SufRow T)} {on : Nat → Bool} :
    ∀ (gs : List (Nat × List (SufPos K))) (out : SufRow T) (c : Nat) (D : Nat → Nat → Prop),
    (∀ kg ∈ gs, ∀ p ∈ kg.2, ValidPos G p) → OutInv G cap w i nt suf D out →
    OutInv G cap w i nt suf (fun r d => D r d ∨ ∃ kg ∈ gs, on kg.1 = true ∧ ∃ p ∈ kg.2, p.rule = r ∧ p.pos = d)
      (sufGroups cap w i nt suf on gs out c).1
  | [], out, c, D, _, h => by
    simp only [sufGroups]
    exact h.mono (fun r d hd => by simpa using hd)
  | (k, g) :: gs, out, c, D, hv, h => by
    have hvs : ∀ kg ∈ gs, ∀ p ∈ kg.2, ValidPos G p := fun kg hkg => hv kg (by simp [hkg])
    unfold sufGroups
    split
    · rename_i hon
      have h1 := sufPosGo_ok g out c D (hv (k, g) (by simp)) h
      refine (sufGroups_ok gs _ _ _ hvs h1).mono ?_
      rintro r d (hd | ⟨kg, hkg, hk, hp⟩)
      · exact Or.inl (Or.inl hd)
      · rcases List.mem_cons.mp hkg with rfl | hkg
        · exact Or.inl (Or.inr hp)
        · exact Or.inr ⟨kg, hkg, hk, hp⟩
    · rename_i hon
      refine (sufGroups_ok gs _ _ _ hvs h).mono ?_
      rintro r d (hd | ⟨kg, hkg, hk, hp⟩)
      · exact Or.inl hd
      · rcases List.mem_cons.mp hkg with rfl | hkg
        · exact absurd hk hon
        · exact Or.inr ⟨kg, hkg, hk, hp⟩

/-- Every entry of the nonterminal row is complete-or-full for all the derivations. -/
def NtFull (G : Grammar K) (cap : Nat) (w : Array T) (i : Nat) (row : NtRow T) : Prop :=
  ∀ A, BOk cap w.size (Span G w (.n A) i) (row.getD A [])

/-- One row: given complete-or-full suffix entries at every later start position, the row's nonterminal
entries and suffix entries are complete-or-full. -/
theorem rowAt_ok (hG : G.wf = true) (hcap : 0 < cap) {i : Nat} (hi : i < w.size)
    {suf : Array (SufRow T)} (hsuf : ∀ p, i < p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[])) :
    NtFull G cap w i (rowAt G.prepare cap w (G.prepare.shape.map fun n => Array.replicate n []) suf i).1 ∧
    SufRowOk G cap w i (rowAt G.prepare cap w (G.prepare.shape.map fun n => Array.replicate n []) suf i).2.1 := by
  -- the nonterminal row
  have hinit : NtOk G cap w i (fun r => r ∈ ([] : List (CRule K)).map (·.index))
      (Array.replicate G.rank.size []) := by
    refine ⟨by simp, fun A => ?_⟩
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_replicate]
    have : ∀ (j : Nat) (t : Tree T), j ≤ w.size → 0 < cap →
        ¬ (Span G w (.n A) i j t ∧ rootIn (fun r => r ∈ ([] : List (CRule K)).map (·.index)) t) := by
      intro j t _ _ h
      obtain ⟨_, h⟩ := h
      cases t <;> simp [rootIn] at h
    split <;> exact BOk.nil this
  have hnt := ntRowGo_ok (G := G) hG hcap hi hsuf G.prepare.order [] (Array.replicate G.rank.size []) 0
    (List.nil_append _) hinit
  have hw : w[i]? = some w[i] := by simp [hi]
  have hempty : ∀ nt : NtRow T, OutInv G cap w i nt suf (fun _ _ => False)
      (G.prepare.shape.map fun n => Array.replicate n []) := by
    intro nt
    have hshape : G.prepare.shape = G.rules.map (·.rhs.length) := rfl
    refine ⟨by simp [hshape], ?_, ?_, ?_⟩
    · intro r R1 hR1
      obtain ⟨hlt, hR⟩ := Array.getElem?_eq_some_iff.mp hR1
      simp [hshape, Array.getD_eq_getD_getElem?, hlt, hR]
    · intro p _; left
      unfold outAt
      simp only [hshape, Array.getD_eq_getD_getElem?, Array.getElem?_map]
      cases G.rules[p.rule]? <;> simp [Array.getElem?_replicate] <;> split <;> rfl
    · intro _ _ h; exact h.elim
  simp only [rowAt, prepare_terms, prepare_grammar]
  cases hq : ntRowGo (accepted (termsOf G) w i) cap w i suf G.prepare.order (Array.replicate G.rank.size []) 0 with
  | mk nt s1 =>
  rw [hq] at hnt
  simp only at hnt ⊢
  have hfull : NtFull G cap w i nt := by
    intro A
    refine BOk.congr (hnt.2 A) (fun j t _ => ⟨fun h => h.1, fun h => ⟨h, ?_⟩⟩)
    obtain ⟨r, ks, R1, rfl, hr1, _, _⟩ := derives_root h.1
    obtain ⟨R', hR', hidx, _⟩ := order_complete hr1
    exact List.mem_map.mpr ⟨R', hR', hidx⟩
  have h1 := sufGroups_ok (on := fun k => (accepted (termsOf G) w i).getD k false) G.prepare.byTerm _ 0 _
    (fun kg hkg p hp => (byTerm_sym hkg hp).1) (hempty nt)
  cases hq1 : sufGroups cap w i nt suf (fun k => (accepted (termsOf G) w i).getD k false) G.prepare.byTerm
      (G.prepare.shape.map fun n => Array.replicate n []) 0 with
  | mk o1 c1 =>
  rw [hq1] at h1
  simp only at h1 ⊢
  have h2 := sufGroups_ok (on := fun B => !(nt.getD B []).isEmpty) G.prepare.byNt o1 c1 _
    (fun kg hkg p hp => (byNt_sym hkg hp).1) h1
  cases hq2 : sufGroups cap w i nt suf (fun B => !(nt.getD B []).isEmpty) G.prepare.byNt o1 c1 with
  | mk o2 c2 =>
  rw [hq2] at h2
  simp only at h2 ⊢
  refine ⟨hfull, ?_⟩
  intro r R0 hR0 d hd hdl
  let p : SufPos K := ⟨r, d, R0.rhs[d], (R0.rhs.drop (d + 1)).isEmpty⟩
  have hp : ValidPos G p := ⟨R0, hR0, hd, hdl, rfl, rfl⟩
  -- the entry has its value
  have hval : outAt o2 r d = sufVal cap w i nt suf p := by
    rcases mem_groups hG hp with ⟨a, hs, g, hg, hpg⟩ | ⟨B, hs, g, hg, hpg⟩
    · by_cases hon : (accepted (termsOf G) w i).getD ((termsOf G).idxOf a) false = true
      · exact h2.done p hp (Or.inl (Or.inr ⟨_, hg, hon, p, hpg, rfl, rfl⟩))
      · have hnil : sufVal cap w i nt suf p = [] := by
          have ha : a ∈ termsOf G := by
            have he : R0.rhs[d] = .t a := hs
            exact mem_termsOf hR0 (he ▸ List.getElem_mem hdl)
          obtain ⟨hlt, hidx⟩ := getElem_idxOf ha
          unfold accepted at hon
          rw [hw] at hon
          simp only [Array.getD_eq_getD_getElem?, Array.getElem?_map, Array.getElem?_eq_getElem hlt, hidx,
            Option.map_some, Option.getD_some] at hon
          unfold sufVal firstAt
          rw [hs, hw]
          simp [hon, combine, Bucket.addAll, Bucket.merge]
        rw [hnil]
        rcases h2.val p hp with e | e
        · exact e
        · exact e.trans hnil
    · by_cases hon : (!(nt.getD B []).isEmpty) = true
      · exact h2.done p hp (Or.inr ⟨_, hg, hon, p, hpg, rfl, rfl⟩)
      · have hnil : sufVal cap w i nt suf p = [] := by
          unfold sufVal firstAt
          rw [hs]
          simp at hon
          simp [hon, combine, Bucket.addAll, Bucket.merge]
        rw [hnil]
        rcases h2.val p hp with e | e
        · exact e
        · exact e.trans hnil
  show BOk cap w.size (SpanAll G w (R0.rhs.drop d) i) (outAt o2 r d)
  rw [hval]
  -- the value is complete-or-full
  have hdrop : R0.rhs.drop d = R0.rhs[d] :: R0.rhs.drop (d + 1) := List.drop_eq_getElem_cons hdl
  have hF : BOk cap w.size (Span G w R0.rhs[d] i) (firstAt w i nt R0.rhs[d]) := by
    match R0.rhs[d] with
    | .t a => exact firstAt_term_ok hi hcap
    | .n B => exact hfull B
  have hN : R0.rhs.drop (d + 1) ≠ [] → ∀ j1, i < j1 → j1 ≤ w.size →
      BOk cap w.size (SpanAll G w (R0.rhs.drop (d + 1)) j1) (sufGet suf j1 r (d + 1)) := by
    intro hne j1 h1 h2
    have hlen : d + 1 < R0.rhs.length := by
      rcases Nat.lt_or_ge (d + 1) R0.rhs.length with h | h
      · exact h
      · exact absurd (List.drop_eq_nil_of_le h) hne
    exact hsuf j1 h1 h2 r R0 hR0 (d + 1) (by omega) hlen
  obtain ⟨hca, hcn, hcc⟩ := combine_ok hG rfl hF hN
  have hB := BOk.addAll (Pold := fun _ _ => False) (BOk.nil (fun _ _ _ _ h => h)) hca hcn hcc
    (fun _ _ h => h.elim)
  rw [hdrop]
  exact BOk.congr hB (fun j x _ => by simp)

end Rows

section Fill

variable {T K : Type} [DecidableEq T] [DecidableEq K] [Accepts K T]
variable {G : Grammar K} {cap : Nat} {w : Array T}

omit [DecidableEq T] [DecidableEq K] in
/-- Nothing starts at the end of the sentence. -/
theorem sufRowOk_end (hG : G.wf = true) : SufRowOk G cap w w.size (#[] : SufRow T) := by
  intro r R0 hR0 d _ hdl
  simp only [Array.getD_eq_getD_getElem?, List.getElem?_toArray, List.getElem?_nil, Option.getD_none]
  refine BOk.nil (fun j us hj _ h => ?_)
  have hne : R0.rhs.drop d ≠ [] := by simp; omega
  have hy := yieldAll_ne_nil hG h.1 hne
  rw [h.2] at hy
  exact hy (by simp)

/-- The rows from the start position `k - 1` down to `0`: the nonterminal row of position `0` is
complete-or-full. -/
theorem fill_ok (hG : G.wf = true) (hcap : 0 < cap) {b : Nat} :
    ∀ (k : Nat) (suf : Array (SufRow T)) (steps : Nat) (last : NtRow T) (res : NtRow T × Nat),
    k ≤ w.size → suf.size = w.size + 1 →
    (∀ p, k ≤ p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[])) →
    (k < w.size → NtFull G cap w k last) →
    fill G.prepare cap w (G.prepare.shape.map fun n => Array.replicate n []) b k suf steps last = some res →
    0 < w.size → NtFull G cap w 0 res.1
  | 0, _, steps, last, res, _, _, _, hlast, h, hn => by
    simp only [fill, Option.some.injEq] at h
    subst h
    exact hlast hn
  | k + 1, suf, steps, last, res, hk, hsz, hsuf, _, h, hn => by
    unfold fill at h
    simp only at h
    split at h
    · simp at h
    · have hrow := rowAt_ok (G := G) (w := w) hG hcap (i := k) (by omega) (suf := suf)
        (fun p h1 h2 => hsuf p (by omega) h2)
      refine fill_ok hG hcap k _ _ _ res (by omega) (by rw [Array.size_setIfInBounds]; exact hsz) ?_
        (fun _ => hrow.1) h hn
      intro p h1 h2
      simp only [Array.getD_eq_getD_getElem?, Array.getElem?_setIfInBounds]
      by_cases hp : k = p
      · subst hp
        simp only [if_pos rfl, if_pos (show k < suf.size by omega), Option.getD_some]
        exact hrow.2
      · rw [if_neg hp]
        have := hsuf p (by omega) h2
        simpa [Array.getD_eq_getD_getElem?] using this

end Fill

end VE.Grammar
