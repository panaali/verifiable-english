import VE.Acts.Lexical
import VE.Readings.Strings

/-! The string lemmas behind the theorems of `VE.Acts.Lexical` (docs/spec/act-phrases.md 4.3).

`String.split` and `String.splitOn " "` are read as `splitL` on the character list; `words` is its non-empty
pieces. `scanSlots` commutes with that split, since a slot `{i}` never holds a space. -/

namespace VE.Acts.Lexical
open VE.Norms.Wire (actReserved words actWord scanSlots scanSlotsAux pyWhitespace asciiLetter)
open VE.Readings (utf8GetAux_append utf8ByteSize_go_append map_data)
open String (utf8ByteSize)

/-- The pieces of a character list between the characters `p` holds for. -/
def splitL (p : Char → Bool) : List Char → List (List Char)
  | [] => [[]]
  | c :: cs => if p c then [] :: splitL p cs else (splitL p cs).modifyHead (c :: ·)

/-! ### `String.split` and `String.splitOn " "` on the characters -/

theorem extract_go₁_general (B rest : List Char) (e : String.Pos) : ∀ i,
    String.extract.go₁ (B ++ rest) ⟨i⟩ ⟨i + utf8ByteSize.go B⟩ e =
      String.extract.go₂ rest ⟨i + utf8ByteSize.go B⟩ e := by
  induction B with
  | nil => intro i; cases rest <;> simp [String.extract.go₁, String.extract.go₂, utf8ByteSize.go]
  | cons c B ih =>
    intro i
    have hc := Char.utf8Size_pos c
    simp only [List.cons_append, String.extract.go₁, utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := ih (i + c.utf8Size)
    rw [show i + (utf8ByteSize.go B + c.utf8Size) = i + c.utf8Size + utf8ByteSize.go B by omega]
    exact this

theorem extract_go₂_prefix (more : List Char) :
    ∀ (cur : List Char) (j : Nat), String.extract.go₂ (cur ++ more) ⟨j⟩ ⟨j + utf8ByteSize.go cur⟩ = cur
  | [], j => by cases more <;> simp [String.extract.go₂, utf8ByteSize.go]
  | c :: cur, j => by
    have hc := Char.utf8Size_pos c
    simp only [List.cons_append, String.extract.go₂, utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := extract_go₂_prefix more cur (j + c.utf8Size)
    have e : (⟨j⟩ : String.Pos) + c = ⟨j + c.utf8Size⟩ := rfl
    rw [e, show j + (utf8ByteSize.go cur + c.utf8Size) = j + c.utf8Size + utf8ByteSize.go cur by omega, this]

theorem extract_mid (s : String) (B cur rest : List Char) (hs : s.data = B ++ cur ++ rest) :
    s.extract ⟨utf8ByteSize.go B⟩ ⟨utf8ByteSize.go (B ++ cur)⟩ = ⟨cur⟩ := by
  obtain ⟨l⟩ := s
  simp only at hs
  subst hs
  rw [utf8ByteSize_go_append]
  simp only [String.extract]
  cases cur with
  | nil => simp [utf8ByteSize.go]
  | cons c cur =>
    have hc := Char.utf8Size_pos c
    rw [if_neg (by simp [utf8ByteSize.go]; omega)]
    congr 1
    have := extract_go₁_general B (c :: cur ++ rest) ⟨utf8ByteSize.go B + utf8ByteSize.go (c :: cur)⟩ 0
    simp only [Nat.zero_add, List.append_assoc] at this ⊢
    exact this.trans (extract_go₂_prefix rest (c :: cur) (utf8ByteSize.go B))

theorem get_mid (s : String) (A : List Char) (c : Char) (rest : List Char) (hs : s.data = A ++ c :: rest) :
    s.get ⟨utf8ByteSize.go A⟩ = c := by
  obtain ⟨l⟩ := s
  simp only at hs
  subst hs
  simpa [String.get] using utf8GetAux_append A c rest 0

theorem splitAux_data (s : String) (p : Char → Bool) : ∀ (rest cur B : List Char) (r : List String),
    s.data = B ++ cur ++ rest → (∀ c ∈ cur, p c = false) →
    s.splitAux p ⟨utf8ByteSize.go B⟩ ⟨utf8ByteSize.go (B ++ cur)⟩ r =
      r.reverse ++ ((splitL p rest).modifyHead (cur ++ ·)).map String.mk
  | [], cur, B, r, hs, _ => by
    rw [String.splitAux, dif_pos (by simp [String.atEnd, String.utf8ByteSize, hs])]
    simp [splitL, extract_mid s B cur [] hs]
  | c :: rest, cur, B, r, hs, hcur => by
    have hc := Char.utf8Size_pos c
    have hs' : s.data = (B ++ cur) ++ c :: rest := by simp [hs]
    rw [String.splitAux, dif_neg (by
      simp [String.atEnd, String.utf8ByteSize, hs, utf8ByteSize_go_append, utf8ByteSize.go]; omega)]
    have hg := get_mid s _ c rest hs'
    have hn : s.next ⟨utf8ByteSize.go (B ++ cur)⟩ = ⟨utf8ByteSize.go (B ++ cur ++ [c])⟩ := by
      rw [String.next, hg]
      simp [String.Pos.ext_iff, utf8ByteSize_go_append, utf8ByteSize.go]; omega
    simp only [hg, hn]
    by_cases hp : p c
    · rw [if_pos hp, extract_mid s B cur (c :: rest) hs]
      have := splitAux_data s p rest [] (B ++ cur ++ [c]) (⟨cur⟩ :: r) (by simp [hs]) (by simp)
      simp only [List.append_nil] at this
      rw [this]
      cases h : splitL p rest <;> simp [splitL, hp, h]
    · rw [if_neg hp]
      have := splitAux_data s p rest (cur ++ [c]) B r (by simp [hs])
        (by intro d hd; simp at hd; rcases hd with hd | hd
            · exact hcur d hd
            · subst hd; simpa using hp)
      rw [← List.append_assoc] at this
      rw [this]
      simp only [splitL, hp]
      cases splitL p rest <;> simp

/-- `String.split` is `splitL` on the characters. -/
theorem split_data (s : String) (p : Char → Bool) : s.split p = (splitL p s.data).map String.mk := by
  have := splitAux_data s p s.data [] [] [] (by simp) (by simp)
  simp only [List.append_nil, utf8ByteSize.go] at this
  unfold String.split
  rw [show (0 : String.Pos) = ⟨0⟩ from rfl, this]
  cases splitL p s.data <;> simp

theorem splitOnAux_data (s : String) : ∀ (rest cur B : List Char) (r : List String),
    s.data = B ++ cur ++ rest → (∀ c ∈ cur, c ≠ ' ') →
    s.splitOnAux " " ⟨utf8ByteSize.go B⟩ ⟨utf8ByteSize.go (B ++ cur)⟩ 0 r =
      r.reverse ++ ((splitL (· == ' ') rest).modifyHead (cur ++ ·)).map String.mk
  | [], cur, B, r, hs, _ => by
    rw [String.splitOnAux, if_pos (by simp [String.atEnd, String.utf8ByteSize, hs])]
    simp [splitL, extract_mid s B cur [] hs]
  | c :: rest, cur, B, r, hs, hcur => by
    have hc := Char.utf8Size_pos c
    have hs' : s.data = (B ++ cur) ++ c :: rest := by simp [hs]
    rw [String.splitOnAux, if_neg (by
      simp [String.atEnd, String.utf8ByteSize, hs, utf8ByteSize_go_append, utf8ByteSize.go]; omega)]
    have hg := get_mid s _ c rest hs'
    have hn : s.next ⟨utf8ByteSize.go (B ++ cur)⟩ = ⟨utf8ByteSize.go (B ++ cur ++ [c])⟩ := by
      rw [String.next, hg]
      simp [String.Pos.ext_iff, utf8ByteSize_go_append, utf8ByteSize.go]; omega
    have h0 : " ".get 0 = ' ' := rfl
    rw [hg, h0]
    by_cases hp : c = ' '
    · subst hp
      have h1 : " ".next 0 = ⟨1⟩ := rfl
      have h2 : " ".atEnd ⟨1⟩ = true := rfl
      have h3 : (⟨utf8ByteSize.go (B ++ cur ++ [' '])⟩ : String.Pos) - ⟨1⟩ = ⟨utf8ByteSize.go (B ++ cur)⟩ := by
        simp [String.Pos.ext_iff, utf8ByteSize_go_append, utf8ByteSize.go]; rfl
      simp only [beq_self_eq_true, if_true, hn, h1, h2, h3]
      rw [extract_mid s B cur (' ' :: rest) hs]
      have := splitOnAux_data s rest [] (B ++ cur ++ [' ']) (⟨cur⟩ :: r) (by simp [hs]) (by simp)
      simp only [List.append_nil] at this
      rw [this]
      cases h : splitL (· == ' ') rest <;> simp [splitL, h]
    · rw [if_neg (by simpa using hp)]
      have h3 : (⟨utf8ByteSize.go (B ++ cur)⟩ : String.Pos) - 0 = ⟨utf8ByteSize.go (B ++ cur)⟩ := by
        simp [String.Pos.ext_iff]
      rw [h3, hn]
      have := splitOnAux_data s rest (cur ++ [c]) B r (by simp [hs])
        (by intro d hd; simp at hd; rcases hd with hd | hd
            · exact hcur d hd
            · subst hd; exact hp)
      rw [← List.append_assoc] at this
      rw [this]
      simp only [splitL, beq_iff_eq, hp, if_false]
      cases splitL (· == ' ') rest <;> simp

/-- `String.splitOn " "` is `splitL` at the spaces. -/
theorem splitOn_space (s : String) : s.splitOn " " = (splitL (· == ' ') s.data).map String.mk := by
  have := splitOnAux_data s s.data [] [] [] (by simp) (by simp)
  simp only [List.append_nil, utf8ByteSize.go] at this
  unfold String.splitOn
  rw [if_neg (by decide)]
  exact this.trans (by cases splitL (· == ' ') s.data <;> simp)

/-! ### `scanSlots`: its text, `out`, read one character at a time -/

theorem scanSlotsAux_fuel : ∀ (n m : Nat) (l : List Char), l.length < n → l.length < m →
    scanSlotsAux n l = scanSlotsAux m l
  | 0, _, _, h, _ => by omega
  | _, 0, _, _, h => by omega
  | n + 1, m + 1, [], _, _ => by simp [scanSlotsAux]
  | n + 1, m + 1, c :: rest, hn, hm => by
    simp only [List.length_cons] at hn hm
    have ih := fun l (h : l.length ≤ rest.length) => scanSlotsAux_fuel n m l (by omega) (by omega)
    by_cases hc : c = '{'
    · subst hc
      rw [VE.Norms.Wire.scanSlotsAux.eq_3, VE.Norms.Wire.scanSlotsAux.eq_3, ih rest (Nat.le_refl _)]
      split
      · next after h =>
        have := congrArg List.length h
        simp at this
        rw [ih after (by omega)]
      · rfl
    · rw [VE.Norms.Wire.scanSlotsAux.eq_4 _ _ _ hc, VE.Norms.Wire.scanSlotsAux.eq_4 _ _ _ hc,
        ih rest (Nat.le_refl _)]

/-- The text of `scanSlots`: every slot replaced by `slot`. -/
abbrev out (l : List Char) : List Char := (scanSlots l).2

theorem out_nil : out [] = [] := rfl

theorem out_fuel (n : Nat) (l : List Char) (h : l.length < n) : (scanSlotsAux n l).2 = out l :=
  congrArg Prod.snd (scanSlotsAux_fuel n _ l h (by omega))

theorem out_cons {c : Char} (hc : c ≠ '{') (rest : List Char) : out (c :: rest) = c :: out rest := by
  show (scanSlotsAux (rest.length + 1 + 1) (c :: rest)).2 = _
  rw [VE.Norms.Wire.scanSlotsAux.eq_4 _ _ _ hc]
  exact congrArg (c :: ·) (out_fuel _ rest (by omega))

/-- A slot `{d}` is read as `slot`. -/
theorem out_slot {d : List Char} (hd : d ≠ []) (hdig : ∀ c ∈ d, c.isDigit = true) (after : List Char) :
    out ('{' :: (d ++ '}' :: after)) = "slot".toList ++ out after := by
  have ht : (d ++ '}' :: after).takeWhile Char.isDigit = d := by
    rw [List.takeWhile_append_of_pos hdig]; simp [List.takeWhile]
  show (scanSlotsAux ((d ++ '}' :: after).length + 1 + 1) ('{' :: (d ++ '}' :: after))).2 = _
  rw [VE.Norms.Wire.scanSlotsAux.eq_3, ht]
  simp only [List.drop_left]
  cases d with
  | nil => exact absurd rfl hd
  | cons c d => exact congrArg ("slot".toList ++ ·) (out_fuel _ after (by simp; omega))

/-- A `{` that does not open a slot is kept. -/
theorem out_brace {rest : List Char}
    (h : ∀ d after, rest = d ++ '}' :: after → d ≠ [] → (∀ c ∈ d, c.isDigit = true) → False) :
    out ('{' :: rest) = '{' :: out rest := by
  show (scanSlotsAux (rest.length + 1 + 1) ('{' :: rest)).2 = _
  rw [VE.Norms.Wire.scanSlotsAux.eq_3]
  have hsplit : rest = rest.takeWhile Char.isDigit ++ rest.drop (rest.takeWhile Char.isDigit).length := by
    conv => lhs; rw [← List.take_append_drop (rest.takeWhile Char.isDigit).length rest]
    rw [← List.prefix_iff_eq_take.mp (List.takeWhile_prefix _)]
  have hdig : ∀ c ∈ rest.takeWhile Char.isDigit, c.isDigit = true :=
    fun c hc => List.all_eq_true.mp List.all_takeWhile c hc
  split
  · next after hdrop =>
    rw [hdrop] at hsplit
    split
    · exact congrArg ('{' :: ·) (out_fuel _ rest (by omega))
    · next hne => exact (h _ after hsplit (by simpa using hne) hdig).elim
  · exact congrArg ('{' :: ·) (out_fuel _ rest (by omega))

/-- Induction along `out`'s cases. -/
theorem out_induct (P : List Char → Prop) (nil : P [])
    (cons : ∀ c rest, c ≠ '{' → P rest → P (c :: rest))
    (slot : ∀ d after, d ≠ [] → (∀ c ∈ d, c.isDigit = true) → P after → P ('{' :: (d ++ '}' :: after)))
    (brace : ∀ rest, (∀ d after, rest = d ++ '}' :: after → d ≠ [] → (∀ c ∈ d, c.isDigit = true) → False) →
      P rest → P ('{' :: rest)) : ∀ l, P l := by
  intro l
  induction h : l.length using Nat.strongRecOn generalizing l with
  | ind n ih =>
    match l with
    | [] => exact nil
    | c :: rest =>
      have hr := ih rest.length (by simp at h; omega) rest rfl
      by_cases hc : c = '{'
      · subst hc
        by_cases hs : ∃ d after, rest = d ++ '}' :: after ∧ d ≠ [] ∧ ∀ c ∈ d, c.isDigit = true
        · obtain ⟨d, after, rfl, hd, hdig⟩ := hs
          exact slot d after hd hdig (ih after.length (by simp at h; omega) after rfl)
        · exact brace rest (fun d after h1 h2 h3 => hs ⟨d, after, h1, h2, h3⟩) hr
      · exact cons c rest hc hr

theorem mem_of_mem_out {c : Char} : ∀ l, c ∈ out l → c ∈ l ∨ c ∈ "slot".toList := by
  refine out_induct _ (by simp [out_nil]) ?_ ?_ ?_
  · intro x rest hx ih h
    rw [out_cons hx] at h
    rcases List.mem_cons.mp h with h | h
    · simp [h]
    · rcases ih h with h | h
      · exact .inl (List.mem_cons_of_mem _ h)
      · exact .inr h
  · intro d after _ _ ih h
    rw [out_slot ‹_› ‹_›] at h
    rcases List.mem_append.mp h with h | h
    · exact .inr h
    · rcases ih h with h | h
      · exact .inl (by simp [h])
      · exact .inr h
  · intro rest _ ih h
    rw [out_brace ‹_›] at h
    rcases List.mem_cons.mp h with h | h
    · simp [h]
    · rcases ih h with h | h
      · exact .inl (List.mem_cons_of_mem _ h)
      · exact .inr h

theorem mem_out_of_mem {c : Char} (h1 : c ≠ '{') (h2 : c ≠ '}') (h3 : c.isDigit = false) :
    ∀ l, c ∈ l → c ∈ out l := by
  refine out_induct _ (by simp) ?_ ?_ ?_
  · intro x rest hx ih h
    rw [out_cons hx]
    simp at h ⊢; rcases h with h | h
    · exact .inl h
    · exact .inr (ih h)
  · intro d after _ hdig ih h
    rw [out_slot ‹_› hdig]
    simp at h; rcases h with h | h | h | h
    · exact (h1 h).elim
    · rw [hdig c h] at h3; cases h3
    · exact (h2 h).elim
    · exact List.mem_append_right _ (ih h)
  · intro rest _ ih h
    rw [out_brace ‹_›]
    simp at h ⊢; rcases h with h | h
    · exact (h1 h).elim
    · exact .inr (ih h)

theorem out_ne_nil : ∀ l, l ≠ [] → out l ≠ [] := by
  refine out_induct _ (by simp) ?_ ?_ ?_
  · intro x rest hx _ _; rw [out_cons hx]; simp
  · intro d after _ hdig _ _; rw [out_slot ‹_› hdig]; simp
  · intro rest h _ _; rw [out_brace h]; simp

theorem out_eq_self : ∀ l, '{' ∉ l → out l = l := by
  refine out_induct _ (by simp [out_nil]) ?_ ?_ ?_
  · intro x rest hx ih h; rw [out_cons hx]; simp at h; rw [ih (by simp [h])]
  · intro _ _ _ _ _ h; simp at h
  · intro _ _ _ h; simp at h

/-- A separator that is no part of a slot splits `out`. -/
theorem out_append {c : Char} (h1 : c ≠ '{') (h2 : c ≠ '}') (h3 : c.isDigit = false) (v : List Char) :
    ∀ u, out (u ++ c :: v) = out u ++ c :: out v := by
  refine out_induct _ (by rw [List.nil_append, out_cons h1]; rfl) ?_ ?_ ?_
  · intro x rest hx ih; simp only [List.cons_append, out_cons hx, ih]
  · intro d after hd hdig ih
    have := out_slot hd hdig (after ++ c :: v)
    simp only [List.cons_append, List.append_assoc] at this ⊢
    rw [this, out_slot hd hdig, ih, List.append_assoc]
  · intro rest h ih
    simp only [List.cons_append]
    rw [out_brace, out_brace h, ih, List.cons_append]
    intro d after he hd hdig
    rcases List.append_eq_append_iff.mp he with ⟨a', rfl, ha⟩ | ⟨c', rfl, hc⟩
    · cases a' with
      | nil => simp at ha; exact h2 ha.1
      | cons y a' =>
        simp at ha
        rw [hdig c (by simp [← ha.1])] at h3; cases h3
    · cases c' with
      | nil => simp at hc; exact h2 hc.1.symm
      | cons y c' => simp at hc; exact h d c' (by rw [hc.1]) hd hdig

/-! ### `splitL` -/

theorem splitL_ne_nil {p : Char → Bool} (l : List Char) : splitL p l ≠ [] := by
  cases l with
  | nil => simp [splitL]
  | cons c l =>
    simp only [splitL]
    split
    · simp
    · cases h : splitL p l
      · exact absurd h (splitL_ne_nil l)
      · simp

theorem mem_splitL {p : Char → Bool} : ∀ {l w : List Char}, w ∈ splitL p l → ∀ c ∈ w, c ∈ l ∧ p c = false
  | [], w, hw, c, hc => by simp [splitL] at hw; subst hw; simp at hc
  | d :: l, w, hw, c, hc => by
    simp only [splitL] at hw
    split at hw
    · simp at hw; rcases hw with rfl | hw
      · simp at hc
      · have := mem_splitL hw c hc; exact ⟨List.mem_cons_of_mem _ this.1, this.2⟩
    · next hd =>
      cases h : splitL p l with
      | nil => rw [h] at hw; simp at hw
      | cons v vs =>
        rw [h] at hw; simp at hw; rcases hw with rfl | hw
        · simp at hc; rcases hc with rfl | hc
          · simpa using hd
          · have := mem_splitL (by rw [h]; simp) c hc; exact ⟨List.mem_cons_of_mem _ this.1, this.2⟩
        · have := mem_splitL (by rw [h]; simp [hw]) c hc; exact ⟨List.mem_cons_of_mem _ this.1, this.2⟩

theorem splitL_cover {p : Char → Bool} {c : Char} (hp : p c = false) :
    ∀ {l : List Char}, c ∈ l → ∃ w ∈ splitL p l, c ∈ w
  | d :: l, hc => by
    simp only [splitL]
    by_cases hd : p d
    · rw [if_pos hd]
      have : c ≠ d := by rintro rfl; rw [hp] at hd; cases hd
      obtain ⟨w, hw, hcw⟩ := splitL_cover hp (List.mem_of_ne_of_mem this hc)
      exact ⟨w, by simp [hw], hcw⟩
    · rw [if_neg hd]
      cases h : splitL p l with
      | nil => exact absurd h (splitL_ne_nil l)
      | cons v vs =>
        simp at hc
        rcases hc with rfl | hc
        · exact ⟨c :: v, by simp, by simp⟩
        · obtain ⟨w, hw, hcw⟩ := splitL_cover hp hc
          rw [h] at hw; simp at hw; rcases hw with rfl | hw
          · exact ⟨d :: w, by simp, by simp [hcw]⟩
          · exact ⟨w, by simp [hw], hcw⟩

theorem splitL_congr {p q : Char → Bool} : ∀ {l : List Char}, (∀ c ∈ l, p c = q c) → splitL p l = splitL q l
  | [], _ => rfl
  | c :: l, h => by
    simp only [splitL, h c (by simp), splitL_congr (fun d hd => h d (List.mem_cons_of_mem _ hd))]

theorem splitL_word {p : Char → Bool} : ∀ {w : List Char}, (∀ c ∈ w, p c = false) → splitL p w = [w]
  | [], _ => rfl
  | c :: w, h => by
    simp only [splitL, h c (by simp), splitL_word (fun d hd => h d (List.mem_cons_of_mem _ hd))]; rfl

theorem splitL_append {p : Char → Bool} {c : Char} (hc : p c = true) (rest : List Char) :
    ∀ {w : List Char}, (∀ d ∈ w, p d = false) → splitL p (w ++ c :: rest) = w :: splitL p rest
  | [], _ => by simp [splitL, hc]
  | d :: w, h => by
    simp only [List.cons_append, splitL, h d (by simp),
      splitL_append hc rest (fun e he => h e (List.mem_cons_of_mem _ he))]; rfl

/-- A list is one piece, or a piece, a separator and the rest. -/
theorem splitL_cases (p : Char → Bool) : ∀ l : List Char, (∀ c ∈ l, p c = false) ∨
    ∃ w c rest, l = w ++ c :: rest ∧ (∀ d ∈ w, p d = false) ∧ p c = true
  | [] => .inl (by simp)
  | c :: l => by
    by_cases hc : p c
    · exact .inr ⟨[], c, l, rfl, by simp, hc⟩
    · rcases splitL_cases p l with h | ⟨w, d, rest, rfl, hw, hd⟩
      · exact .inl (by simp_all)
      · exact .inr ⟨c :: w, d, rest, rfl, by simp_all, hd⟩

theorem pyWhitespace_sep {c : Char} (h : pyWhitespace c = true) : c ≠ '{' ∧ c ≠ '}' ∧ c.isDigit = false := by
  refine ⟨?_, ?_, ?_⟩
  · rintro rfl; revert h; decide
  · rintro rfl; revert h; decide
  · simp only [pyWhitespace] at h
    simp only [Char.isDigit, Bool.and_eq_false_iff, decide_eq_false_iff_not]
    have : c.toNat = c.val.toNat := rfl
    simp [UInt32.lt_iff_toNat_lt] at *
    omega

/-- `scanSlots` commutes with the split at Python's whitespace: a slot never holds a space. -/
theorem splitL_out (l : List Char) : splitL pyWhitespace (out l) = (splitL pyWhitespace l).map out := by
  induction h : l.length using Nat.strongRecOn generalizing l with
  | ind n ih =>
    rcases splitL_cases pyWhitespace l with hl | ⟨w, c, rest, rfl, hw, hc⟩
    · rw [splitL_word hl, splitL_word]
      · rfl
      · intro c hc
        rcases mem_of_mem_out l hc with hc | hc
        · exact hl c hc
        · simp at hc; rcases hc with rfl | rfl | rfl | rfl <;> rfl
    · obtain ⟨h1, h2, h3⟩ := pyWhitespace_sep hc
      rw [out_append h1 h2 h3, splitL_append hc _ hw, splitL_append hc,
        ih rest.length (by simp at h; omega) rest rfl]
      · rfl
      · intro d hd
        rcases mem_of_mem_out w hd with hd | hd
        · exact hw d hd
        · simp at hd; rcases hd with rfl | rfl | rfl | rfl <;> rfl

/-! ### `words` -/

/-- `words` on the characters: the non-empty pieces. -/
def wordsL (l : List Char) : List (List Char) := (splitL pyWhitespace l).filter (· ≠ [])

theorem words_data (s : String) : words s = (wordsL s.data).map String.mk := by
  simp only [words, wordsL, split_data, List.filter_map]
  congr 2
  funext w
  cases w <;> simp [String.ext_iff]

theorem wordsL_out (l : List Char) : wordsL (out l) = (wordsL l).map out := by
  simp only [wordsL, splitL_out, List.filter_map]
  congr 2
  funext w
  cases w with
  | nil => rfl
  | cons c w => simp [out_ne_nil (c :: w) (by simp)]

theorem mem_words {s w : String} (h : w ∈ words s) :
    w ≠ "" ∧ ∀ c ∈ w.data, c ∈ s.data ∧ pyWhitespace c = false := by
  rw [words_data] at h
  obtain ⟨v, hv, rfl⟩ := List.mem_map.mp h
  obtain ⟨hv, hne⟩ := List.mem_filter.mp hv
  exact ⟨by simpa [String.ext_iff] using hne, mem_splitL hv⟩

theorem words_cover {s : String} {c : Char} (h : c ∈ s.data) (hc : pyWhitespace c = false) :
    ∃ w ∈ words s, c ∈ w.data := by
  obtain ⟨v, hv, hcv⟩ := splitL_cover hc h
  refine ⟨⟨v⟩, ?_, hcv⟩
  rw [words_data]
  exact List.mem_map.mpr ⟨v, List.mem_filter.mpr ⟨hv, by simpa using List.ne_nil_of_mem hcv⟩, rfl⟩

/-- A word of `a` is read by `scanSlots` as a word of `a`'s text. -/
theorem word_out {a w : String} (h : w ∈ words a) : (⟨out w.data⟩ : String) ∈ words ⟨out a.data⟩ := by
  rw [words_data] at h ⊢
  obtain ⟨v, hv, rfl⟩ := List.mem_map.mp h
  exact List.mem_map.mpr ⟨out v, by rw [wordsL_out]; exact List.mem_map_of_mem hv, rfl⟩

/-- A character of `a` that is no part of a slot and no space is in a word of `a`'s text. -/
theorem out_cover {a : String} {c : Char} (h : c ∈ a.data) (h1 : c ≠ '{') (h2 : c ≠ '}') (h3 : c.isDigit = false)
    (hc : pyWhitespace c = false) : ∃ w ∈ words ⟨out a.data⟩, c ∈ w.data :=
  words_cover (mem_out_of_mem h1 h2 h3 _ h) hc

theorem intercalate_data (ws : List String) :
    ∀ w : String, (" ".intercalate (w :: ws)).data = w.data ++ ws.flatMap (' ' :: ·.data) := by
  induction ws with
  | nil => intro w; simp; rfl
  | cons v ws ih =>
    intro w
    rw [show " ".intercalate (w :: v :: ws) = " ".intercalate ((w ++ " " ++ v) :: ws) from rfl, ih]
    simp [String.data_append]

theorem mem_intercalate {ws : List String} {c : Char} (h : c ∈ (" ".intercalate ws).data) :
    c = ' ' ∨ ∃ w ∈ ws, c ∈ w.data := by
  cases ws with
  | nil => simp [String.intercalate] at h
  | cons w ws =>
    rw [intercalate_data] at h
    simp at h
    rcases h with h | ⟨v, hv, h | h⟩
    · exact .inr ⟨w, by simp, h⟩
    · exact .inl h
    · exact .inr ⟨v, by simp [hv], h⟩

/-- `words` of a normal string: its words. -/
theorem words_intercalate {ws : List String}
    (h : ∀ w ∈ ws, w ≠ "" ∧ ∀ c ∈ w.data, pyWhitespace c = false) : words (" ".intercalate ws) = ws := by
  cases ws with
  | nil => rw [words_data]; rfl
  | cons w ws =>
    have key : ∀ (L : List String) (v : List Char), (∀ c ∈ v, pyWhitespace c = false) →
        (∀ u ∈ L, ∀ c ∈ u.data, pyWhitespace c = false) →
        splitL pyWhitespace (v ++ L.flatMap (' ' :: ·.data)) = v :: L.map String.data := by
      intro L
      induction L with
      | nil => intro v hv _; simpa using splitL_word hv
      | cons u L ih =>
        intro v hv hL
        simp only [List.flatMap_cons, List.map_cons, List.cons_append]
        rw [splitL_append (by decide) _ hv,
          ih u.data (hL u (by simp)) (fun x hx => hL x (by simp [hx]))]
    rw [words_data, intercalate_data, wordsL,
      key ws w.data (h w (by simp)).2 (fun u hu => (h u (by simp [hu])).2)]
    rw [List.filter_eq_self.mpr]
    · simp only [List.map_cons, List.map_map]
      exact congrArg _ (List.map_id' _ ▸ List.map_congr_left (fun _ _ => rfl))
    · intro v hv
      simp at hv
      rcases hv with rfl | ⟨u, hu, rfl⟩
      · simpa [String.ext_iff] using (h w (by simp)).1
      · simpa [String.ext_iff] using (h u (by simp [hu])).1

/-! ### Characters of strings -/

theorem fold_eq_self {s : String} (h : ∀ c ∈ s.data, c.toNat ≠ 0x2019) : fold s = s := by
  unfold fold
  rw [List.map_congr_left (g := id) (fun c hc => by simp [h c hc]), List.map_id]
  rfl

theorem get_mem (s : String) (i : String.Pos) (h : s.get i ≠ default) : s.get i ∈ s.data := by
  obtain ⟨l⟩ := s
  simp only [String.get] at h ⊢
  generalize (0 : String.Pos) = j at h ⊢
  induction l generalizing j with
  | nil => exact (h rfl).elim
  | cons c l ih =>
    simp only [String.utf8GetAux] at h ⊢
    split
    · simp
    · next hi => rw [if_neg hi] at h; exact List.mem_cons_of_mem _ (ih _ h)

theorem endsWith_comma {s : String} (h : s.endsWith "," = true) : ',' ∈ s.data := by
  unfold String.endsWith at h
  simp only [String.toSubstring, Substring.takeRight] at h
  generalize ((0 : String.Pos) + _) = b at h
  change Substring.beq ⟨s, b, s.endPos⟩ ⟨",", 0, ⟨1⟩⟩ = true at h
  simp only [Substring.beq, Substring.bsize, String.substrEq, Bool.and_eq_true, beq_iff_eq,
    decide_eq_true_eq] at h
  have hsz : s.endPos.byteIdx - b.byteIdx = 1 := h.1
  have hl := h.2.2
  revert hl
  unfold_substrEq_loop
  rw [dif_pos (by simp; omega)]
  simp only [Bool.and_eq_true, beq_iff_eq]
  intro ⟨hg, _⟩
  have hc : ",".get 0 = ',' := rfl
  rw [hc] at hg
  exact hg ▸ get_mem s b (by rw [hg]; decide)

theorem contains_mem {s : String} {c : Char} (hc : c ≠ default) (h : s.contains c = true) : c ∈ s.data := by
  suffices ∀ i, s.anyAux s.endPos (· == c) i = true → ∃ j, s.get j = c by
    obtain ⟨j, hj⟩ := this 0 h
    exact hj ▸ get_mem s j (by rw [hj]; exact hc)
  intro i
  induction i using String.anyAux.induct s s.endPos (· == c) with
  | case1 x _ hp => intro; exact ⟨x, by simpa using hp⟩
  | case2 x hx hp _ ih => intro h; rw [String.anyAux, dif_pos hx, if_neg hp] at h; exact ih h
  | case3 x hx => intro h; rw [String.anyAux, dif_neg hx] at h; cases h

theorem actWord_chars {w : String} (h : actWord w = true) :
    ∀ c ∈ w.data, asciiLetter c ∨ c = '\'' ∨ c = '-' := by
  unfold actWord at h
  intro c hc
  cases hw : w.data with
  | nil => rw [hw] at hc; simp at hc
  | cons d ds =>
    have hw' : w.toList = d :: ds := hw
    rw [hw'] at h
    simp only [Bool.and_eq_true, List.all_eq_true, Bool.or_eq_true, beq_iff_eq] at h
    rw [hw] at hc
    rcases List.mem_cons.mp hc with rfl | hc
    · exact .inl h.1
    · rcases h.2 c hc with (h | h) | h <;> simp [h]

theorem utf8ByteSize_le (s : String) : s.utf8ByteSize ≤ 4 * s.length := by
  obtain ⟨l⟩ := s
  show utf8ByteSize.go l ≤ 4 * l.length
  induction l with
  | nil => simp [utf8ByteSize.go]
  | cons c l ih => simp only [utf8ByteSize.go, List.length_cons]; have := Char.utf8Size_le_four c; omega

theorem isEmpty_false {w : String} (h : w ≠ "") : w.isEmpty = false := by
  obtain ⟨l⟩ := w
  cases l with
  | nil => exact absurd rfl h
  | cons c l =>
    have := Char.utf8Size_pos c
    simp [String.isEmpty, String.endPos, String.utf8ByteSize, utf8ByteSize.go, String.Pos.ext_iff]; omega

theorem toLower_mem {x : String} {c : Char} (hx : c ∈ x.data) (hc : c.toLower = c) : c ∈ x.toLower.data := by
  rw [String.toLower, map_data]
  exact hc ▸ List.mem_map_of_mem hx

/-- A string with a brace or a comma is no clause word and no join word. -/
theorem not_listed {x : String} {c : Char} (hx : c ∈ x.data) (hc : c = '{' ∨ c = ',') :
    clauseWords.contains x = false ∧ joinWords.contains x = false := by
  have hl : ∀ y ∈ clauseWords ++ joinWords, '{' ∉ y.data ∧ ',' ∉ y.data := by decide
  have key : ∀ L : List String, (∀ y ∈ L, '{' ∉ y.data ∧ ',' ∉ y.data) → L.contains x = false := by
    intro L hL
    rw [Bool.eq_false_iff]
    intro hy
    have := hL x (List.contains_iff_mem.mp hy)
    rcases hc with rfl | rfl
    · exact this.1 hx
    · exact this.2 hx
  exact ⟨key _ (fun y hy => hl y (List.mem_append_left _ hy)), key _ (fun y hy => hl y (List.mem_append_right _ hy))⟩

theorem clause_reserved {y : String} (h : clauseWords.contains y = true) : actReserved.contains y = true :=
  List.contains_iff_mem.mpr (List.mem_filter.mp (List.contains_iff_mem.mp h)).1

/-! ### Tokens -/

theorem mapM_ok {α β ε : Type} {f : α → Except ε β} {g : α → β} :
    ∀ {l : List α}, (∀ x ∈ l, f x = .ok (g x)) → l.mapM f = .ok (l.map g)
  | [], _ => rfl
  | x :: l, h => by
    rw [List.mapM_cons, h x (by simp), mapM_ok (fun y hy => h y (by simp [hy]))]; rfl

theorem foldl_append_eq {α : Type} (tss : List (List α)) :
    ∀ acc, tss.foldl (· ++ ·) acc = acc ++ tss.flatten := by
  induction tss with
  | nil => simp
  | cons l tss ih => intro acc; simp [ih]

theorem mem_group {ps : List (List Tok)} : ∀ {n : Nat} {ts : List Tok} {t : Tok},
    t ∈ group ps n ts → t ∈ ts ∨ ∃ i, t = .fixed i
  | 0, _, _, h => .inl h
  | _ + 1, [], _, h => by simp [group] at h
  | n + 1, u :: rest, t, h => by
    simp only [group] at h
    split at h
    · rcases List.mem_cons.mp h with rfl | h
      · exact .inr ⟨_, rfl⟩
      · rcases mem_group h with h | h
        · exact .inl (List.mem_of_mem_drop h)
        · exact .inr h
    · rcases List.mem_cons.mp h with rfl | h
      · exact .inl (by simp)
      · rcases mem_group h with h | h
        · exact .inl (by simp [h])
        · exact .inr h

/-- A piece's single token. -/
def pieceTok (w : String) : Tok := match slotOf? w with
  | some i => .slot i
  | none => .word w

end VE.Acts.Lexical
