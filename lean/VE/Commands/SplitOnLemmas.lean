import VE.Acts.LexicalProofs

/-! `String.splitOn` with a separator of any length (docs/spec/commands-imperatives.md section 7; item ci-3b): the
lemmas `preposed_eq` and `readStep_conservative` need (ci-3a's REPORT found none in core Lean 4.24). `splitOnL` cuts a
character list at the leftmost non-overlapping occurrences of a separator, as `String.splitOnAux` does (after an
unfinished match it restarts one character on), and `splitOn_data` proves the two equal for every non-empty separator.
The lemmas are stated over `List Char`, then over `String`. `VE.Acts.Lexical.splitOn_space` is the one-space case,
proved there over `splitL`. -/

namespace VE.Commands.SplitOn

open String (utf8ByteSize)
open VE.Readings (utf8ByteSize_go_append)
open VE.Acts.Lexical (extract_mid get_mid)

set_option linter.unusedVariables false in
/-- The pieces of `l` between the leftmost non-overlapping occurrences of `sep`. -/
def splitOnL (sep : List Char) : List Char → List (List Char)
  | [] => [[]]
  | c :: cs =>
    if h : sep ≠ [] ∧ sep <+: c :: cs then [] :: splitOnL sep ((c :: cs).drop sep.length)
    else (splitOnL sep cs).modifyHead (c :: ·)
termination_by l => l.length
decreasing_by
  all_goals simp_wf
  all_goals have := List.length_pos_iff.2 h.1; omega

variable {sep : List Char}

/-! ### Over `List Char` -/

theorem splitOnL_ne_nil (l : List Char) : splitOnL sep l ≠ [] := by
  induction l using splitOnL.induct sep with
  | case1 => simp [splitOnL]
  | case2 c cs h _ => rw [splitOnL, dif_pos h]; simp
  | case3 c cs h ih => rw [splitOnL, dif_neg h]; cases hs : splitOnL sep cs <;> simp_all

theorem splitOnL_skip {c : Char} {cs : List Char} (h : ¬ sep <+: c :: cs) :
    splitOnL sep (c :: cs) = (splitOnL sep cs).modifyHead (c :: ·) := by
  rw [splitOnL, dif_neg (fun h' => h h'.2)]

theorem splitOnL_cut (hs : sep ≠ []) (l : List Char) : splitOnL sep (sep ++ l) = [] :: splitOnL sep l := by
  obtain ⟨d, ds, rfl⟩ := List.exists_cons_of_ne_nil hs
  rw [List.cons_append, splitOnL, dif_pos ⟨hs, by simp⟩]
  simp

theorem splitOnL_short : ∀ {l : List Char}, l.length < sep.length → splitOnL sep l = [l]
  | [], _ => by simp [splitOnL]
  | c :: cs, h => by
    rw [splitOnL_skip (fun hp => by have := hp.length_le; omega),
      splitOnL_short (by simp at h; omega)]
    rfl

/-- A separator that does not occur gives the whole list. -/
theorem splitOnL_none : ∀ {l : List Char}, ¬ sep <:+: l → splitOnL sep l = [l]
  | [], _ => by simp [splitOnL]
  | c :: cs, h => by
    rw [splitOnL_skip (fun hp => h hp.isInfix), splitOnL_none (fun hi => h (List.infix_cons_iff.2 (.inr hi)))]
    rfl

/-- A prefix without the separator's first character stays inside the first piece. -/
theorem prefix_first {d : Char} {ds : List Char} : ∀ {P l x : List Char} {xs : List (List Char)}, d ∉ P →
    P <+: l → splitOnL (d :: ds) l = x :: xs → P <+: x
  | [], _, _, _, _, _, _ => List.nil_prefix
  | c :: P, l, x, xs, hP, ⟨t, ht⟩, h => by
    subst ht
    simp only [List.mem_cons, not_or] at hP
    rw [List.cons_append, splitOnL_skip (fun hp => hP.1 (List.cons_prefix_cons.1 hp).1)] at h
    cases hs : splitOnL (d :: ds) (P ++ t) with
    | nil => exact absurd hs (splitOnL_ne_nil _)
    | cons y ys =>
      rw [hs, List.modifyHead_cons, List.cons.injEq] at h
      rw [← h.1]
      exact List.cons_prefix_cons.2 ⟨rfl, prefix_first hP.2 (List.prefix_append P t) hs⟩

/-- The first-occurrence decomposition: `l = a ++ sep ++ b` with `a` free of `sep`, and the pieces are `a`, then
the pieces of `b`. -/
theorem splitOnL_first (hs : sep ≠ []) : ∀ {l : List Char}, sep <:+: l →
    ∃ a b, l = a ++ sep ++ b ∧ ¬ sep <:+: a ∧ splitOnL sep l = a :: splitOnL sep b
  | [], h => absurd (List.eq_nil_of_infix_nil h) hs
  | c :: cs, h => by
    by_cases hp : sep <+: c :: cs
    · obtain ⟨b, hb⟩ := hp
      refine ⟨[], b, by simp [hb], fun hi => hs (List.eq_nil_of_infix_nil hi), ?_⟩
      rw [← hb, splitOnL_cut hs]
    · obtain ⟨a, b, rfl, ha, hsp⟩ := splitOnL_first hs ((List.infix_cons_iff.1 h).resolve_left hp)
      refine ⟨c :: a, b, by simp, fun hi => ?_, by rw [splitOnL_skip hp, hsp]; rfl⟩
      rcases List.infix_cons_iff.1 hi with hi | hi
      · exact hp (hi.trans (List.cons_prefix_cons.2 ⟨rfl, by simp [List.append_assoc]⟩))
      · exact ha hi

/-- A separator that occurs makes at least two pieces. -/
theorem splitOnL_two (hs : sep ≠ []) {l : List Char} : 2 ≤ (splitOnL sep l).length ↔ sep <:+: l := by
  refine ⟨fun h => Classical.byContradiction fun hi => by rw [splitOnL_none hi] at h; simp at h, fun h => ?_⟩
  obtain ⟨a, b, -, -, he⟩ := splitOnL_first hs h
  rw [he]
  cases hb : splitOnL sep b with
  | nil => exact absurd hb (splitOnL_ne_nil b)
  | cons _ _ => simp

/-- The pieces hold no occurrence of the separator. -/
theorem splitOnL_free (hs : sep ≠ []) : ∀ (l : List Char), ∀ p ∈ splitOnL sep l, ¬ sep <:+: p
  | l, p, hp => by
    by_cases hi : sep <:+: l
    · obtain ⟨a, b, rfl, ha, he⟩ := splitOnL_first hs hi
      rw [he, List.mem_cons] at hp
      have : b.length < (a ++ sep ++ b).length := by
        have := List.length_pos_iff.2 hs; simp; omega
      rcases hp with rfl | hp
      · exact ha
      · exact splitOnL_free hs b p hp
    · rw [splitOnL_none hi, List.mem_singleton] at hp
      exact hp ▸ hi
termination_by l => l.length

theorem intercalate_cons (x : List Char) (l : List (List Char)) :
    sep.intercalate (x :: l) = x ++ l.flatMap (sep ++ ·) := by
  induction l generalizing x with
  | nil => simp [List.intercalate]
  | cons y l ih =>
    have := ih y
    simp only [List.intercalate, List.intersperse_cons₂, List.flatten_cons] at this ⊢
    rw [this]; simp

/-- Joining the pieces with the separator gives the list back. -/
theorem intercalate_splitOnL (hs : sep ≠ []) : ∀ (l : List Char), sep.intercalate (splitOnL sep l) = l
  | l => by
    by_cases hi : sep <:+: l
    · obtain ⟨a, b, rfl, -, he⟩ := splitOnL_first hs hi
      have : b.length < (a ++ sep ++ b).length := by
        have := List.length_pos_iff.2 hs; simp; omega
      have ih := intercalate_splitOnL hs b
      rw [he]
      cases hb : splitOnL sep b with
      | nil => exact absurd hb (splitOnL_ne_nil b)
      | cons x xs =>
        rw [hb, intercalate_cons] at ih
        rw [intercalate_cons, List.flatMap_cons, ← ih]; simp
    · rw [splitOnL_none hi]; simp [List.intercalate]; rfl
termination_by l => l.length

/-! ### The bridge to `String.splitOnAux` -/

theorem modifyHead_comp (X : List (List Char)) (cur : List Char) (c : Char) :
    (X.modifyHead (c :: ·)).modifyHead (cur ++ ·) = X.modifyHead ((cur ++ [c]) ++ ·) := by
  cases X <;> simp

/-- `splitOnAux` at bytes `B`, `B ++ cur ++ m` and `m`: `cur` is the piece so far and `m` a proper prefix of the
separator matched since. By induction on the unread list with `m`, then on the unread list after it. -/
theorem splitOnAux_spec (s t : String) : ∀ (n k : Nat) (B cur m rest more : List Char) (r : List String),
    (m ++ rest).length < n → rest.length < k →
    s.data = B ++ cur ++ m ++ rest → t.data = m ++ more → more ≠ [] →
    s.splitOnAux t ⟨utf8ByteSize.go B⟩ ⟨utf8ByteSize.go (B ++ cur ++ m)⟩ ⟨utf8ByteSize.go m⟩ r =
      r.reverse ++ ((splitOnL t.data (m ++ rest)).modifyHead (cur ++ ·)).map String.mk := by
  intro n
  induction n with
  | zero => intros; omega
  | succ n ihn =>
  intro k
  induction k with
  | zero => intros; omega
  | succ k ihk =>
  intro B cur m rest more r hn hk hs ht hmore
  have ht0 : t.data ≠ [] := by rw [ht]; simp [hmore]
  have hlt : m.length < t.data.length := by
    rw [ht]; have := List.length_pos_iff.2 hmore; simp; omega
  cases rest with
  | nil =>
    rw [String.splitOnAux, if_pos (by simp [String.atEnd, String.utf8ByteSize, hs])]
    rw [List.append_assoc, extract_mid s B (cur ++ m) [] (by simp [hs]), List.append_nil,
      splitOnL_short hlt]
    simp
  | cons c rest =>
    have hc := Char.utf8Size_pos c
    rw [String.splitOnAux, if_neg (by
      simp [String.atEnd, String.utf8ByteSize, hs, utf8ByteSize_go_append, utf8ByteSize.go] <;> omega)]
    obtain ⟨d, more', rfl⟩ := List.exists_cons_of_ne_nil hmore
    have hg := get_mid s (B ++ cur ++ m) c rest (by simp [hs])
    have hgt := get_mid t m d more' ht
    rw [hg, hgt]
    by_cases hcd : c = d
    · subst hcd
      have hn1 : s.next ⟨utf8ByteSize.go (B ++ cur ++ m)⟩ = ⟨utf8ByteSize.go (B ++ cur ++ (m ++ [c]))⟩ := by
        rw [String.next, hg]; simp [String.Pos.ext_iff, utf8ByteSize_go_append, utf8ByteSize.go] <;> omega
      have hn2 : t.next ⟨utf8ByteSize.go m⟩ = ⟨utf8ByteSize.go (m ++ [c])⟩ := by
        rw [String.next, hgt]; simp [String.Pos.ext_iff, utf8ByteSize_go_append, utf8ByteSize.go] <;> omega
      simp only [beq_self_eq_true, if_true, hn1, hn2]
      cases more' with
      | nil =>
        rw [if_pos (by simp [String.atEnd, String.utf8ByteSize, ht, utf8ByteSize_go_append, utf8ByteSize.go])]
        have hsub : (⟨utf8ByteSize.go (B ++ cur ++ (m ++ [c]))⟩ : String.Pos) - ⟨utf8ByteSize.go (m ++ [c])⟩ =
            ⟨utf8ByteSize.go (B ++ cur)⟩ := by
          apply String.Pos.ext
          show utf8ByteSize.go _ - utf8ByteSize.go _ = utf8ByteSize.go _
          simp only [utf8ByteSize_go_append]; omega
        rw [hsub, extract_mid s B cur (m ++ c :: rest) (by simp [hs])]
        have := ihn (rest.length + 1) (B ++ cur ++ (m ++ [c])) [] [] rest t.data (⟨cur⟩ :: r)
          (by simp at hn ⊢; omega) (by omega) (by simp [hs]) rfl ht0
        simp only [List.append_nil, List.nil_append, utf8ByteSize.go] at this
        rw [show (0 : String.Pos) = ⟨0⟩ from rfl, this,
          show m ++ c :: rest = t.data ++ rest by rw [ht]; simp, splitOnL_cut ht0]
        cases splitOnL t.data rest <;> simp
      | cons e more'' =>
        rw [if_neg (by
          simp [String.atEnd, String.utf8ByteSize, ht, utf8ByteSize_go_append, utf8ByteSize.go]
          have := Char.utf8Size_pos e; omega)]
        have := ihk B cur (m ++ [c]) rest (e :: more'') r (by simp at hn ⊢; omega) (by simp at hk; omega)
          (by simp [hs])
          (by simp [ht]) (by simp)
        rw [this]; simp
    · rw [if_neg (by simpa using hcd)]
      have hsub : (⟨utf8ByteSize.go (B ++ cur ++ m)⟩ : String.Pos) - ⟨utf8ByteSize.go m⟩ =
          ⟨utf8ByteSize.go (B ++ cur)⟩ := by
        apply String.Pos.ext
        show utf8ByteSize.go _ - utf8ByteSize.go _ = utf8ByteSize.go _
        simp only [utf8ByteSize_go_append]; omega
      rw [hsub, show (0 : String.Pos) = ⟨utf8ByteSize.go []⟩ from rfl]
      cases m with
      | nil =>
        have hn1 : s.next ⟨utf8ByteSize.go (B ++ cur)⟩ = ⟨utf8ByteSize.go (B ++ (cur ++ [c]))⟩ := by
          rw [String.next, show B ++ cur = B ++ cur ++ [] by simp, hg]
          simp [String.Pos.ext_iff, utf8ByteSize_go_append, utf8ByteSize.go] <;> omega
        have := ihn (rest.length + 1) B (cur ++ [c]) [] rest (d :: more') r (by simp at hn ⊢; omega) (by omega)
          (by simp [hs]) ht hmore
        simp only [List.append_nil, List.nil_append] at this
        rw [hn1, this, List.nil_append, splitOnL_skip (by
          rw [ht]; intro hp; exact hcd (List.cons_prefix_cons.1 hp).1.symm), modifyHead_comp]
      | cons e m' =>
        have hge := get_mid s (B ++ cur) e (m' ++ c :: rest) (by simp [hs])
        have hn1 : s.next ⟨utf8ByteSize.go (B ++ cur)⟩ = ⟨utf8ByteSize.go (B ++ (cur ++ [e]))⟩ := by
          rw [String.next, hge]; simp [String.Pos.ext_iff, utf8ByteSize_go_append, utf8ByteSize.go] <;> omega
        have := ihn ((m' ++ c :: rest).length + 1) B (cur ++ [e]) [] (m' ++ c :: rest) t.data r
          (by simp at hn ⊢; omega) (by omega) (by simp [hs]) rfl ht0
        simp only [List.append_nil, List.nil_append] at this
        rw [hn1, this, List.cons_append, splitOnL_skip (by
          rw [ht]; intro hp
          have hp' : m' ++ d :: more' <+: m' ++ c :: rest := (List.cons_prefix_cons.1 hp).2
          rw [List.prefix_append_right_inj] at hp'
          exact hcd (List.cons_prefix_cons.1 hp').1.symm), modifyHead_comp]

/-- `String.splitOn` is `splitOnL` on the characters, for every non-empty separator. -/
theorem splitOn_data (s t : String) (ht : t ≠ "") : s.splitOn t = (splitOnL t.data s.data).map String.mk := by
  have ht0 : t.data ≠ [] := fun h => ht (String.ext h)
  have := splitOnAux_spec s t _ _ [] [] [] s.data t.data [] (Nat.lt_succ_self _) (Nat.lt_succ_self _) (by simp)
    (by simp) ht0
  simp only [List.append_nil, List.nil_append, utf8ByteSize.go] at this
  unfold String.splitOn
  rw [if_neg (by simpa using ht)]
  exact this.trans (by cases splitOnL t.data s.data <;> simp)

/-! ### Over `String` -/

theorem intercalate_data (t : String) : ∀ (l : List (List Char)),
    (t.intercalate (l.map String.mk)).data = t.data.intercalate l
  | [] => rfl
  | [x] => by simp [List.intercalate]; rfl
  | x :: y :: l => by
    have := intercalate_data t ((x ++ t.data ++ y) :: l)
    rw [List.map_cons, List.map_cons,
      show t.intercalate (String.mk x :: String.mk y :: l.map String.mk) =
        t.intercalate (String.mk (x ++ t.data ++ y) :: l.map String.mk) from rfl, ← List.map_cons, this,
      intercalate_cons, intercalate_cons, List.flatMap_cons]
    simp
termination_by l => l.length

/-- A separator that does not occur gives the whole string. -/
theorem splitOn_none (s t : String) (ht : t ≠ "") (h : ¬ t.data <:+: s.data) : s.splitOn t = [s] := by
  rw [splitOn_data s t ht, splitOnL_none h]; rfl

/-- Joining the pieces with the separator gives the string back. -/
theorem intercalate_splitOn (s t : String) (ht : t ≠ "") : t.intercalate (s.splitOn t) = s := by
  have ht0 : t.data ≠ [] := fun h => ht (String.ext h)
  exact String.ext (by rw [splitOn_data s t ht, intercalate_data, intercalate_splitOnL ht0])

/-- The pieces hold no occurrence of the separator. -/
theorem splitOn_free (s t : String) (ht : t ≠ "") : ∀ p ∈ s.splitOn t, ¬ t.data <:+: p.data := by
  intro p hp
  rw [splitOn_data s t ht, List.mem_map] at hp
  obtain ⟨q, hq, rfl⟩ := hp
  exact splitOnL_free (fun h => ht (String.ext h)) _ q hq

/-- The first occurrence: `s = a ++ t ++ b` with `a` free of `t`; the pieces are `a`, then those of `b`. -/
theorem splitOn_first (s t : String) (ht : t ≠ "") (h : t.data <:+: s.data) :
    ∃ a b : String, s = a ++ t ++ b ∧ ¬ t.data <:+: a.data ∧ s.splitOn t = a :: b.splitOn t := by
  obtain ⟨a, b, he, ha, hsp⟩ := splitOnL_first (fun h => ht (String.ext h)) h
  refine ⟨⟨a⟩, ⟨b⟩, String.ext (by simp [he, String.data_append]), ha, ?_⟩
  rw [splitOn_data s t ht, splitOn_data ⟨b⟩ t ht, hsp]; rfl

/-- At least two pieces exactly when the separator occurs. -/
theorem splitOn_two (s t : String) (ht : t ≠ "") : 2 ≤ (s.splitOn t).length ↔ t.data <:+: s.data := by
  rw [splitOn_data s t ht, List.length_map]; exact splitOnL_two fun h => ht (String.ext h)

/-! ### Fixtures: each lemma on a concrete string, the bridge on overlapping and unfinished matches -/

#guard "Click Ask".splitOn ", then " == ["Click Ask"]
#guard ", then ".intercalate ("Click a, then click b, then c".splitOn ", then ") == "Click a, then click b, then c"
#guard ("Click Check rule conflict, then click Ask".splitOn ", then ").all fun p => !(p.splitOn ", then ").length > 1
#guard "Click Check rule conflict, then click Ask".splitOn ", then " == ["Click Check rule conflict", "click Ask"]
#guard "x, then y, then z".splitOn ", then " == "x" :: "y, then z".splitOn ", then "
#guard 2 ≤ ("a, then b".splitOn ", then ").length && ("a then b".splitOn ", then ").length == 1
#guard ("Then x, if y, if z".splitOn ", if ").head!.startsWith "Then "
#guard "draft, is approved, click Ask".splitOn ", " == ["draft", "is approved", "click Ask"]
#guard (splitOnL ", then ".data "a, the, then b".data).map String.mk == "a, the, then b".splitOn ", then "
#guard (splitOnL "aab".data "aaab, aa".data).map String.mk == "aaab, aa".splitOn "aab"

end VE.Commands.SplitOn
