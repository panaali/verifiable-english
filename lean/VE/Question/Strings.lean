import VE.Readings.Names

/-! Facts about `String` as a list of characters, for the question reader's statements (spec 5.1): `isPrefixOf`
is list prefix, `drop`, `dropRight 1` and `extract` are list operations, `endsWith "?"` reads the last character,
and byte sizes add. Core Lean has none of them; `String.substrEq`'s private loop is unfolded with
`VE.Readings`' `unfold_substrEq_loop`, whose unfolding equation the kernel checks. -/

namespace VE.Question.Str

/-- `utf8ByteSize.go` adds over appended lists. -/
theorem size_append (l l' : List Char) :
    String.utf8ByteSize.go (l ++ l') = String.utf8ByteSize.go l + String.utf8ByteSize.go l' := by
  induction l with
  | nil => simp [String.utf8ByteSize.go]
  | cons c l ih => simp [String.utf8ByteSize.go, ih]; omega

theorem size_cons (c : Char) (l : List Char) :
    String.utf8ByteSize.go (c :: l) = c.utf8Size + String.utf8ByteSize.go l := by
  simp [String.utf8ByteSize.go]; omega

theorem size_pos_of_cons (c : Char) (l : List Char) : 0 < String.utf8ByteSize.go (c :: l) := by
  rw [size_cons]; have := Char.utf8Size_pos c; omega

theorem size_data (s : String) : s.utf8ByteSize = String.utf8ByteSize.go s.data := rfl

theorem endPos_data (s : String) : s.endPos = ⟨String.utf8ByteSize.go s.data⟩ := rfl

theorem utf8ByteSize_append (a b : String) : (a ++ b).utf8ByteSize = a.utf8ByteSize + b.utf8ByteSize := by
  simp only [size_data, String.data_append, size_append]

/-- The character at the byte position of a list prefix. -/
theorem getAux_at (A : List Char) (c : Char) (R : List Char) (i : Nat) :
    String.utf8GetAux (A ++ c :: R) ⟨i⟩ ⟨i + String.utf8ByteSize.go A⟩ = c := by
  induction A generalizing i with
  | nil => simp [String.utf8GetAux, String.utf8ByteSize.go]
  | cons a A ih =>
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.utf8GetAux]
    rw [if_neg (by simp [String.Pos.ext_iff, size_cons]; omega)]
    have := ih (i + a.utf8Size)
    rw [show i + String.utf8ByteSize.go (a :: A) = i + a.utf8Size + String.utf8ByteSize.go A by
      rw [size_cons]; omega]
    exact this

theorem get_at (s : String) (A : List Char) (c : Char) (R : List Char) (h : s.data = A ++ c :: R) :
    s.get ⟨String.utf8ByteSize.go A⟩ = c := by
  obtain ⟨d⟩ := s
  simp only at h
  subst h
  have := getAux_at A c R 0
  simpa using this

/-- `substrEq` with nothing to compare. -/
theorem substrEq_zero (s1 s2 : String) (p1 p2 : Nat) (h1 : p1 ≤ s1.endPos.byteIdx) (h2 : p2 ≤ s2.endPos.byteIdx) :
    String.substrEq s1 ⟨p1⟩ s2 ⟨p2⟩ 0 = true := by
  unfold String.substrEq
  simp only [Nat.add_zero, h1, h2, decide_true, Bool.true_and]
  unfold_substrEq_loop
  simp

/-- One step of `substrEq`: the first characters, then the rest. -/
theorem substrEq_step (s1 s2 : String) (p1 p2 n : Nat) (hn : (s1.get ⟨p1⟩).utf8Size ≤ n) (hpos : 0 < n)
    (h1 : p1 + n ≤ s1.endPos.byteIdx) (h2 : p2 + n ≤ s2.endPos.byteIdx)
    (hsz : (s1.get ⟨p1⟩ = s2.get ⟨p2⟩)) :
    String.substrEq s1 ⟨p1⟩ s2 ⟨p2⟩ n =
      String.substrEq s1 ⟨p1 + (s1.get ⟨p1⟩).utf8Size⟩ s2 ⟨p2 + (s2.get ⟨p2⟩).utf8Size⟩
        (n - (s1.get ⟨p1⟩).utf8Size) := by
  unfold String.substrEq
  simp only [h1, h2, decide_true, Bool.true_and]
  have e1 : p1 + (s1.get ⟨p1⟩).utf8Size + (n - (s1.get ⟨p1⟩).utf8Size) = p1 + n := by omega
  have e2 : p2 + (s2.get ⟨p2⟩).utf8Size + (n - (s1.get ⟨p1⟩).utf8Size) = p2 + n := by rw [← hsz]; omega
  simp only [e1, e2, h1, h2, decide_true, Bool.true_and]
  unfold_substrEq_loop
  simp only [show p1 < p1 + n by omega, dite_true, hsz, beq_self_eq_true, Bool.true_and]
  rfl

theorem substrEq_ne (s1 s2 : String) (p1 p2 n : Nat) (hpos : 0 < n)
    (hne : s1.get ⟨p1⟩ ≠ s2.get ⟨p2⟩) : String.substrEq s1 ⟨p1⟩ s2 ⟨p2⟩ n = false := by
  unfold String.substrEq
  unfold_substrEq_loop
  simp [show p1 < p1 + n by omega, hne]

local notation "sz" => String.utf8ByteSize.go

theorem substrEq_prefix (s1 s2 : String) (X : List Char) :
    ∀ (A1 A2 R1 R2 : List Char), s1.data = A1 ++ X ++ R1 → s2.data = A2 ++ R2 → sz X ≤ sz R2 →
    (String.substrEq s1 ⟨sz A1⟩ s2 ⟨sz A2⟩ (sz X) = true ↔ X <+: R2) := by
  induction X with
  | nil =>
    intro A1 A2 R1 R2 h1 h2 _
    rw [show sz ([] : List Char) = 0 from rfl, substrEq_zero]
    · simp
    · rw [endPos_data, h1]; simp [size_append]
    · rw [endPos_data, h2]; simp [size_append]
  | cons x X ih =>
    intro A1 A2 R1 R2 h1 h2 hle
    cases R2 with
    | nil => have := size_pos_of_cons x X; have h0 : sz ([] : List Char) = 0 := rfl; omega
    | cons y R2 =>
      have gx : s1.get ⟨sz A1⟩ = x := get_at s1 A1 x (X ++ R1) (by rw [h1]; simp)
      have gy : s2.get ⟨sz A2⟩ = y := get_at s2 A2 y R2 (by rw [h2])
      rw [size_cons, size_cons] at hle
      by_cases hxy : x = y
      · subst hxy
        rw [size_cons, substrEq_step s1 s2 _ _ _ (by rw [gx]; omega) (by have := Char.utf8Size_pos x; omega)
          (by rw [endPos_data, h1]; simp [size_append, size_cons] <;> omega)
          (by rw [endPos_data, h2]; simp [size_append, size_cons] <;> omega) (by rw [gx, gy])]
        rw [gx, gy, show x.utf8Size + sz X - x.utf8Size = sz X by omega]
        have := ih (A1 ++ [x]) (A2 ++ [x]) R1 R2 (by rw [h1]; simp) (by rw [h2]; simp) (by omega)
        rw [size_append, size_append] at this
        simp only [String.utf8ByteSize.go, Nat.zero_add] at this
        rw [this]
        simp
      · rw [size_cons, substrEq_ne s1 s2 _ _ _ (by have := Char.utf8Size_pos x; omega) (by rw [gx, gy]; exact hxy)]
        simp only [Bool.false_eq_true, false_iff]
        intro hp
        exact hxy (List.cons_prefix_cons.mp hp).1

theorem isPrefixOf_iff (p s : String) : p.isPrefixOf s = true ↔ p.data <+: s.data := by
  unfold String.isPrefixOf
  by_cases hle : sz p.data ≤ sz s.data
  · have := substrEq_prefix p s p.data [] [] [] s.data (by simp) (by simp) hle
    simpa [endPos_data, String.utf8ByteSize.go] using this
  · constructor
    · intro h
      unfold String.substrEq at h
      simp [endPos_data] at h
      omega
    · intro ⟨t, ht⟩
      rw [← ht, size_append] at hle
      omega

/-! ## `extract`, `drop`, `dropRight`, `endsWith` as list operations -/

theorem size_eq_zero {l : List Char} (h : sz l = 0) : l = [] := by
  cases l with
  | nil => rfl
  | cons c l => have := size_pos_of_cons c l; omega

theorem go₂_all (l : List Char) (i e : Nat) (h : i + sz l ≤ e) : String.extract.go₂ l ⟨i⟩ ⟨e⟩ = l := by
  induction l generalizing i with
  | nil => rfl
  | cons c l ih =>
    rw [size_cons] at h
    have hc := Char.utf8Size_pos c
    simp only [String.extract.go₂]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    congr 1
    exact ih (i + c.utf8Size) (by omega)

theorem go₂_prefix (A R : List Char) (i : Nat) : String.extract.go₂ (A ++ R) ⟨i⟩ ⟨i + sz A⟩ = A := by
  induction A generalizing i with
  | nil =>
    cases R with
    | nil => rfl
    | cons c R => simp [String.extract.go₂, String.utf8ByteSize.go]
  | cons a A ih =>
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.extract.go₂]
    rw [if_neg (by simp [String.Pos.ext_iff, size_cons]; omega)]
    congr 1
    have := ih (i + a.utf8Size)
    rw [show i + sz (a :: A) = i + a.utf8Size + sz A by rw [size_cons]; omega]
    exact this

theorem go₁_at (l : List Char) (i : Nat) (e : String.Pos) :
    String.extract.go₁ l ⟨i⟩ ⟨i⟩ e = String.extract.go₂ l ⟨i⟩ e := by
  cases l with
  | nil => rfl
  | cons c l => simp [String.extract.go₁]

theorem go₁_suffix (A R : List Char) (i : Nat) (e : String.Pos) :
    String.extract.go₁ (A ++ R) ⟨i⟩ ⟨i + sz A⟩ e = String.extract.go₂ R ⟨i + sz A⟩ e := by
  induction A generalizing i with
  | nil => simpa [String.utf8ByteSize.go] using go₁_at R i e
  | cons a A ih =>
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.extract.go₁]
    rw [if_neg (by simp [String.Pos.ext_iff, size_cons]; omega)]
    have := ih (i + a.utf8Size)
    rw [show i + sz (a :: A) = i + a.utf8Size + sz A by rw [size_cons]; omega]
    exact this

theorem go_split (l : List Char) (i g : Nat) :
    String.extract.go₂ l ⟨i⟩ ⟨g⟩ ++ String.extract.go₁ l ⟨i⟩ ⟨g⟩ ⟨i + sz l⟩ = l := by
  induction l generalizing i with
  | nil => rfl
  | cons c l ih =>
    by_cases hig : i = g
    · subst hig
      simp only [String.extract.go₂, String.extract.go₁, if_true, List.nil_append]
      exact go₂_all (c :: l) i _ (by omega)
    · simp only [String.extract.go₂, String.extract.go₁]
      rw [if_neg (by simp [String.Pos.ext_iff]; exact hig), if_neg (by simp [String.Pos.ext_iff]; exact hig)]
      simp only [List.cons_append, List.cons.injEq, true_and]
      have := ih (i + c.utf8Size)
      rw [show i + sz (c :: l) = i + c.utf8Size + sz l by rw [size_cons]; omega]
      exact this

theorem pos_zero : (0 : String.Pos) = ⟨0⟩ := rfl
theorem zero_add_pos (p : String.Pos) : (0 : String.Pos) + p = p := by
  cases p; show (⟨0 + _⟩ : String.Pos) = _; rw [Nat.zero_add]
theorem mk_zero_add_pos (p : String.Pos) : (⟨0⟩ : String.Pos) + p = p := by
  cases p; show (⟨0 + _⟩ : String.Pos) = _; rw [Nat.zero_add]

/-- The two parts of a string at any byte offset are the whole string. -/
theorem extract_split (s : String) (g : Nat) :
    (s.extract 0 ⟨g⟩).data ++ (s.extract ⟨g⟩ s.endPos).data = s.data := by
  obtain ⟨d⟩ := s
  simp only [String.extract, endPos_data, pos_zero]
  rw [go₁_at d 0]
  by_cases hg : g = 0
  · subst hg
    by_cases hd : sz d = 0
    · have := size_eq_zero hd
      subst this
      rfl
    · rw [if_pos (Nat.le_refl 0), if_neg (by omega)]
      simp only [List.nil_append]
      rw [go₁_at d 0, go₂_all d 0 (sz d) (by omega)]
  · rw [if_neg (by omega)]
    by_cases hge : g ≥ sz d
    · rw [if_pos hge]
      simp only [List.append_nil]
      exact go₂_all d 0 g (by omega)
    · rw [if_neg hge]
      have := go_split d 0 g
      simp only [Nat.zero_add] at this
      exact this

theorem extract_size (s : String) (g : Nat) :
    (s.extract 0 ⟨g⟩).utf8ByteSize + (s.extract ⟨g⟩ s.endPos).utf8ByteSize = s.utf8ByteSize := by
  simp only [size_data, ← size_append, extract_split]

theorem extract_suffix (s : String) (A R : List Char) (h : s.data = A ++ R) :
    s.extract ⟨sz A⟩ s.endPos = ⟨R⟩ := by
  obtain ⟨d⟩ := s
  simp only at h
  subst h
  simp only [String.extract, endPos_data, size_append, pos_zero]
  by_cases hR : sz R = 0
  · have := size_eq_zero hR
    subst this
    rw [if_pos (by simp [String.utf8ByteSize.go])]
  · rw [if_neg (by omega)]
    have := go₁_suffix A R 0 ⟨sz A + sz R⟩
    simp only [Nat.zero_add] at this
    rw [this, go₂_all R (sz A) (sz A + sz R) (by omega)]

theorem extract_prefix (s : String) (A R : List Char) (h : s.data = A ++ R) :
    s.extract 0 ⟨sz A⟩ = ⟨A⟩ := by
  obtain ⟨d⟩ := s
  simp only at h
  subst h
  simp only [String.extract, pos_zero]
  by_cases hA : sz A = 0
  · have := size_eq_zero hA
    subst this
    rw [if_pos (by simp [String.utf8ByteSize.go])]
  · rw [if_neg (by omega), go₁_at]
    have h2 := go₂_prefix A R 0
    simp only [Nat.zero_add] at h2
    rw [h2]

theorem nextn_toSubstring (s : String) (n : Nat) :
    ∀ A R, s.data = A ++ R → s.toSubstring.nextn n ⟨sz A⟩ = ⟨sz A + sz (R.take n)⟩ := by
  induction n with
  | zero => intro A R _; simp [Substring.nextn, String.utf8ByteSize.go]
  | succ n ih =>
    intro A R h
    simp only [Substring.nextn]
    cases R with
    | nil =>
      have : s.toSubstring.next ⟨sz A⟩ = ⟨sz A⟩ := by
        show (if (⟨0⟩ : String.Pos) + ⟨sz A⟩ = s.endPos then _ else _) = _
        rw [mk_zero_add_pos, if_pos (by rw [endPos_data, h]; simp)]
      rw [this]
      have := ih A [] (by simp [h])
      simpa using this
    | cons c R =>
      have hc := Char.utf8Size_pos c
      have hn : s.toSubstring.next ⟨sz A⟩ = ⟨sz A + c.utf8Size⟩ := by
        show (if (⟨0⟩ : String.Pos) + ⟨sz A⟩ = s.endPos then (⟨sz A⟩ : String.Pos)
          else ⟨(s.next ((⟨0⟩ : String.Pos) + ⟨sz A⟩)).byteIdx - (⟨0⟩ : String.Pos).byteIdx⟩) = _
        rw [mk_zero_add_pos, if_neg (by rw [endPos_data, h]; simp [String.Pos.ext_iff, size_append, size_cons]; omega)]
        simp only [String.next, get_at s A c R h]
        rfl
      rw [hn]
      have := ih (A ++ [c]) R (by simp [h])
      rw [size_append, show sz [c] = c.utf8Size by simp [String.utf8ByteSize.go]] at this
      rw [this]
      simp [size_cons]
      omega

theorem drop_data (s : String) (n : Nat) : s.drop n = ⟨s.data.drop n⟩ := by
  have h := nextn_toSubstring s n [] s.data (by simp)
  simp only [String.utf8ByteSize.go, Nat.zero_add] at h
  show s.extract ((⟨0⟩ : String.Pos) + s.toSubstring.nextn n ⟨0⟩) s.endPos = _
  rw [h, mk_zero_add_pos]
  exact extract_suffix s (s.data.take n) (s.data.drop n) (List.take_append_drop n s.data).symm

theorem prevAux_last (A : List Char) (c : Char) (i : Nat) :
    String.utf8PrevAux (A ++ [c]) ⟨i⟩ ⟨i + sz A + c.utf8Size⟩ = ⟨i + sz A⟩ := by
  induction A generalizing i with
  | nil => simp [String.utf8PrevAux, String.utf8ByteSize.go, String.Pos.le_iff]
  | cons a A ih =>
    have hc := Char.utf8Size_pos c
    simp only [List.cons_append, String.utf8PrevAux]
    rw [if_neg (by simp [String.Pos.le_iff, size_cons]; omega)]
    have := ih (i + a.utf8Size)
    rw [show i + sz (a :: A) + c.utf8Size = i + a.utf8Size + sz A + c.utf8Size by rw [size_cons]; omega,
      show i + sz (a :: A) = i + a.utf8Size + sz A by rw [size_cons]; omega]
    exact this

theorem bsize_toSubstring (s : String) : s.toSubstring.bsize = sz s.data := by
  show s.endPos.byteIdx - (⟨0⟩ : String.Pos).byteIdx = _
  simp [endPos_data]

/-- The start of the last character, as `Substring.prevn 1` from the end finds it. -/
theorem prev_end (s : String) (A : List Char) (c : Char) (h : s.data = A ++ [c]) :
    s.toSubstring.prevn 1 ⟨s.toSubstring.bsize⟩ = ⟨sz A⟩ := by
  have hc := Char.utf8Size_pos c
  rw [bsize_toSubstring, h, size_append, show sz [c] = c.utf8Size by simp [String.utf8ByteSize.go]]
  show (if (⟨0⟩ : String.Pos) + ⟨sz A + c.utf8Size⟩ = ⟨0⟩ then (⟨sz A + c.utf8Size⟩ : String.Pos)
    else ⟨(s.prev ((⟨0⟩ : String.Pos) + ⟨sz A + c.utf8Size⟩)).byteIdx - (⟨0⟩ : String.Pos).byteIdx⟩) = _
  rw [mk_zero_add_pos, if_neg (by simp [String.Pos.ext_iff]; omega)]
  obtain ⟨d⟩ := s
  simp only at h
  subst h
  have := prevAux_last A c 0
  simp only [Nat.zero_add] at this
  show (⟨(String.utf8PrevAux (A ++ [c]) 0 ⟨sz A + c.utf8Size⟩).byteIdx - 0⟩ : String.Pos) = _
  rw [pos_zero, this]
  rfl

theorem dropRight_one (s : String) : s.dropRight 1 = ⟨s.data.dropLast⟩ := by
  rcases List.eq_nil_or_concat s.data with hd | ⟨A, c, hd⟩
  all_goals try rw [List.concat_eq_append] at hd
  · obtain ⟨d⟩ := s
    simp only at hd
    subst hd
    rfl
  · show s.extract ⟨0⟩ ((⟨0⟩ : String.Pos) + s.toSubstring.prevn 1 ⟨s.toSubstring.bsize⟩) = _
    rw [prev_end s A c hd, mk_zero_add_pos, ← pos_zero, extract_prefix s A [c] hd, hd]
    simp

theorem endsWith_q (s : String) : s.endsWith "?" = true ↔ s.data.getLast? = some '?' := by
  rcases List.eq_nil_or_concat s.data with hd | ⟨A, c, hd⟩
  · obtain ⟨d⟩ := s
    simp only at hd
    subst hd
    decide
  · rw [List.concat_eq_append] at hd
    rw [hd, List.getLast?_append, List.getLast?_singleton]
    simp only [Option.some_or, Option.some.injEq]
    show (Substring.beq ⟨s, (⟨0⟩ : String.Pos) + s.toSubstring.prevn 1 ⟨s.toSubstring.bsize⟩, s.endPos⟩
      "?".toSubstring) = true ↔ c = '?'
    rw [prev_end s A c hd, mk_zero_add_pos]
    have hc := Char.utf8Size_pos c
    have hb : (⟨s, ⟨sz A⟩, s.endPos⟩ : Substring).bsize = c.utf8Size := by
      show s.endPos.byteIdx - sz A = _
      rw [endPos_data, hd, size_append]; simp [String.utf8ByteSize.go]
    have hq : "?".toSubstring.bsize = 1 := rfl
    unfold Substring.beq
    rw [hb, hq]
    by_cases h1 : c.utf8Size = 1
    · rw [h1]
      simp only [beq_self_eq_true, Bool.true_and]
      have := substrEq_prefix s "?" [c] A [] [] ['?'] (by rw [hd]; simp) (by rfl)
        (by simp [String.utf8ByteSize.go, h1]; decide)
      simp only [String.utf8ByteSize.go, h1, Nat.zero_add] at this
      show String.substrEq s ⟨sz A⟩ "?" ⟨0⟩ 1 = true ↔ c = '?'
      rw [this]
      simp
    · constructor
      · intro h; simp [h1] at h
      · intro h; subst h; exact absurd rfl h1

end VE.Question.Str
