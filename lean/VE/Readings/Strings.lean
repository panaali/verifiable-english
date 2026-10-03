import VE.Readings.Names

/-! Prefixes of strings of one-byte characters (docs/spec/composition-s2.md 8.3: `copyCites` and the reserved
names). Core Lean has no lemma relating `String.startsWith` and `String.drop` to `String.append`; these are proved
here for an ASCII prefix through `String.substrEq`, `Substring.nextn` and `String.extract`. -/
namespace VE.Readings

/-- Every character is one byte. -/
def AsciiL (l : List Char) : Prop := ∀ c ∈ l, c.utf8Size = 1

instance (l : List Char) : Decidable (AsciiL l) := by unfold AsciiL; infer_instance

theorem asciiL_append {l l' : List Char} (h : AsciiL l) (h' : AsciiL l') : AsciiL (l ++ l') := by
  intro c hc
  rcases List.mem_append.mp hc with hc | hc
  · exact h c hc
  · exact h' c hc

theorem asciiL_of_append_left {l l' : List Char} (h : AsciiL (l ++ l')) : AsciiL l :=
  fun c hc => h c (List.mem_append_left _ hc)

theorem asciiL_of_append_right {l l' : List Char} (h : AsciiL (l ++ l')) : AsciiL l' :=
  fun c hc => h c (List.mem_append_right _ hc)

theorem utf8GetAux_prefix (A : List Char) (hA : AsciiL A) (c : Char) (rest : List Char) (a : Nat) :
    String.utf8GetAux (A ++ c :: rest) ⟨a⟩ ⟨a + A.length⟩ = c := by
  have := utf8GetAux_append A c rest ⟨a⟩
  rwa [utf8ByteSize_go_ascii A hA] at this

theorem get_prefix (s : String) (A : List Char) (hA : AsciiL A) (c : Char) (rest : List Char)
    (hs : s.data = A ++ c :: rest) : s.get ⟨A.length⟩ = c := by
  obtain ⟨l⟩ := s
  simp only at hs
  subst hs
  have := utf8GetAux_prefix A hA c rest 0
  simpa [String.get] using this

theorem get_end (s : String) (A : List Char) (hs : s.data = A) : s.get ⟨String.utf8ByteSize.go A⟩ = default := by
  obtain ⟨l⟩ := s
  simp only at hs
  subst hs
  show String.utf8GetAux l 0 ⟨String.utf8ByteSize.go l⟩ = default
  suffices ∀ (l : List Char) (i : Nat), String.utf8GetAux l ⟨i⟩ ⟨i + String.utf8ByteSize.go l⟩ = default by
    simpa using this l 0
  intro l
  induction l with
  | nil => intro i; rfl
  | cons c l ih =>
    intro i
    have hc := Char.utf8Size_pos c
    simp only [String.utf8GetAux, String.utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := ih (i + c.utf8Size)
    rw [show i + (String.utf8ByteSize.go l + c.utf8Size) = i + c.utf8Size + String.utf8ByteSize.go l by omega]
    exact this

theorem endPos_data (s : String) : s.endPos.byteIdx = String.utf8ByteSize.go s.data := rfl

/-- `substrEq` over a common ASCII prefix: a match of `B`'s length at the end of the prefix makes `B` a prefix of the
    rest. -/
theorem prefix_of_substrEq (s p : String) (hp : AsciiL p.data) : ∀ (B A rest : List Char),
    s.data = A ++ rest → p.data = A ++ B →
    String.substrEq s ⟨A.length⟩ p ⟨A.length⟩ B.length = true → ∃ t, rest = B ++ t
  | [], _, rest, _, _, _ => ⟨rest, rfl⟩
  | b :: B, A, rest, hs, hpd, h => by
    have hA : AsciiL A := asciiL_of_append_left (hpd ▸ hp)
    have hb : b.utf8Size = 1 := hp b (by rw [hpd]; simp)
    have hB : AsciiL B := fun c hc => hp c (by rw [hpd]; simp [hc])
    cases rest with
    | nil =>
      exfalso
      revert h
      unfold String.substrEq
      rw [endPos_data s, hs, List.append_nil, utf8ByteSize_go_ascii A hA]
      simp only [Bool.and_eq_true, decide_eq_true_eq, List.length_cons]
      intro ⟨⟨g1, _⟩, _⟩
      omega
    | cons r rest =>
      have hgs : s.get ⟨A.length⟩ = r := get_prefix s A hA r rest hs
      have hgp : p.get ⟨A.length⟩ = b := get_prefix p A hA b B hpd
      have hlen : (b :: B).length = B.length + 1 := rfl
      have hguard : A.length + (B.length + 1) ≤ s.endPos.byteIdx ∧
          A.length + (B.length + 1) ≤ p.endPos.byteIdx ∧ r = b ∧
          String.substrEq s ⟨(A ++ [b]).length⟩ p ⟨(A ++ [b]).length⟩ B.length = true := by
        revert h
        rw [hlen]
        unfold String.substrEq
        simp only [Bool.and_eq_true, decide_eq_true_eq]
        intro ⟨⟨g1, g2⟩, hl⟩
        revert hl
        unfold_substrEq_loop
        rw [dif_pos (show A.length < A.length + (B.length + 1) by omega)]
        simp only [hgs, hgp, Bool.and_eq_true, beq_iff_eq]
        intro ⟨hrb, hl⟩
        subst hrb
        have hr : r.utf8Size = 1 := hb
        refine ⟨g1, g2, rfl, ?_⟩
        simp only [Bool.and_eq_true, decide_eq_true_eq, List.length_append, List.length_singleton]
        refine ⟨⟨by omega, by omega⟩, ?_⟩
        have e1 : (⟨A.length⟩ : String.Pos) + r = ⟨A.length + 1⟩ := by
          simp [String.Pos.ext_iff, hr]
        have e2 : (⟨A.length + (B.length + 1)⟩ : String.Pos) = ⟨A.length + 1 + B.length⟩ := by
          simp only [String.Pos.mk.injEq]; omega
        rw [e1, e2] at hl
        exact hl
      obtain ⟨_, _, hrb, h'⟩ := hguard
      subst hrb
      obtain ⟨t, ht⟩ := prefix_of_substrEq s p hp B (A ++ [r]) rest (by rw [hs]; simp) (by rw [hpd]; simp) h'
      exact ⟨t, by rw [ht]; rfl⟩

theorem toSubstring_bsize_ascii (p : String) (hp : AsciiL p.data) : p.toSubstring.bsize = p.data.length := by
  show p.endPos.byteIdx - 0 = _
  rw [endPos_data, utf8ByteSize_go_ascii _ hp]
  rfl

/-- A string that starts with an ASCII prefix is that prefix followed by a rest. -/
theorem eq_append_of_startsWith {s p : String} (hp : AsciiL p.data) (h : s.startsWith p = true) :
    ∃ t : String, s = p ++ t := by
  unfold String.startsWith at h
  change Substring.beq _ _ = true at h
  unfold Substring.beq at h
  simp only [Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨hb, he⟩ := h
  rw [toSubstring_bsize_ascii p hp] at hb
  have hs0 : (s.toSubstring.take p.length).str = s := rfl
  have hp0 : (s.toSubstring.take p.length).startPos = 0 := rfl
  rw [hs0, hp0, hb] at he
  have := prefix_of_substrEq s p hp p.data [] s.data rfl rfl (by simpa using he)
  obtain ⟨t, ht⟩ := this
  exact ⟨⟨t⟩, String.ext (by simp [String.data_append, ht])⟩

/-! ## `drop` -/

theorem nextn_ascii (s : String) (A : List Char) (hA : AsciiL A) (rest : List Char) (hs : s.data = A ++ rest) :
    ∀ (i k : Nat), k + i ≤ A.length → s.toSubstring.nextn i ⟨k⟩ = ⟨k + i⟩
  | 0, k, _ => by simp [Substring.nextn]
  | i + 1, k, hk => by
    simp only [Substring.nextn]
    have hlt : k < A.length := by omega
    have hnext : s.toSubstring.next ⟨k⟩ = ⟨k + 1⟩ := by
      simp only [String.toSubstring, Substring.next]
      have hz : ({ } : String.Pos) + ⟨k⟩ = ⟨k⟩ := by simp [String.Pos.ext_iff]
      have hE : s.endPos.byteIdx = A.length + String.utf8ByteSize.go rest := by
        rw [endPos_data, hs, utf8ByteSize_go_append, utf8ByteSize_go_ascii A hA]
      rw [hz, if_neg (by simp [String.Pos.ext_iff, hE]; omega)]
      have hsplit : s.data = A.take k ++ A[k] :: (A.drop (k + 1) ++ rest) := by
        have hA' : A = A.take k ++ A[k] :: A.drop (k + 1) := by
          rw [← List.drop_eq_getElem_cons hlt, List.take_append_drop]
        rw [hs]
        rw (occs := .pos [1]) [hA']
        rw [List.append_assoc, List.cons_append]
      have hAk : AsciiL (A.take k) := fun c hc => hA c (List.mem_of_mem_take hc)
      have hg : s.get ⟨k⟩ = A[k] := by
        have := get_prefix s (A.take k) hAk A[k] _ hsplit
        simpa [Nat.min_eq_left (Nat.le_of_lt hlt)] using this
      rw [String.Pos.ext_iff]
      show (s.next ⟨k⟩).byteIdx - 0 = k + 1
      rw [show (s.next ⟨k⟩).byteIdx = k + (s.get ⟨k⟩).utf8Size from rfl, hg, hA _ (List.getElem_mem hlt)]
      omega
    rw [hnext]
    have := nextn_ascii s A hA rest hs i (k + 1) (by omega)
    rw [this]
    simp [String.Pos.ext_iff]; omega

theorem extract_go₂_all : ∀ (l : List Char) (i : Nat), String.extract.go₂ l ⟨i⟩ ⟨i + String.utf8ByteSize.go l⟩ = l
  | [], _ => rfl
  | c :: l, i => by
    have hc := Char.utf8Size_pos c
    simp only [String.extract.go₂, String.utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := extract_go₂_all l (i + c.utf8Size)
    have e : (⟨i⟩ : String.Pos) + c = ⟨i + c.utf8Size⟩ := rfl
    rw [e, show i + (String.utf8ByteSize.go l + c.utf8Size) = i + c.utf8Size + String.utf8ByteSize.go l by omega,
      this]

theorem extract_go₁_skip (A : List Char) (hA : AsciiL A) (rest : List Char) (e : String.Pos) :
    ∀ (k : Nat), k ≤ A.length → String.extract.go₁ (A.drop k ++ rest) ⟨k⟩ ⟨A.length⟩ e =
      String.extract.go₁ rest ⟨A.length⟩ ⟨A.length⟩ e := by
  intro k hk
  induction h : A.length - k generalizing k with
  | zero =>
    have : k = A.length := by omega
    subst this
    simp
  | succ n ih =>
    have hlt : k < A.length := by omega
    rw [List.drop_eq_getElem_cons hlt]
    simp only [List.cons_append, String.extract.go₁]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have e1 : (⟨k⟩ : String.Pos) + A[k] = ⟨k + 1⟩ := by
      simp [String.Pos.ext_iff, pos_add_char, hA _ (List.getElem_mem hlt)]
    rw [e1]
    exact ih (k + 1) (by omega) (by omega)

/-- Dropping an ASCII prefix's length leaves the rest. -/
theorem drop_append_ascii (p t : String) (hp : AsciiL p.data) : (p ++ t).drop p.length = t := by
  have hd : (p ++ t).data = p.data ++ t.data := String.data_append p t
  have hlen : p.length = p.data.length := rfl
  unfold String.drop
  have hn := nextn_ascii (p ++ t) p.data hp t.data hd p.data.length 0 (by omega)
  simp only [Nat.zero_add] at hn
  rw [hlen]
  change (p ++ t).extract (0 + (p ++ t).toSubstring.nextn p.data.length 0) (p ++ t).endPos = t
  have hn2 : (p ++ t).toSubstring.nextn p.data.length 0 = ⟨p.data.length⟩ := hn
  rw [hn2]
  have hE : (p ++ t).endPos.byteIdx = p.data.length + String.utf8ByteSize.go t.data := by
    rw [endPos_data, hd, utf8ByteSize_go_append, utf8ByteSize_go_ascii _ hp]
  have hz : (0 : String.Pos) + ⟨p.data.length⟩ = ⟨p.data.length⟩ := by simp [String.Pos.ext_iff]
  rw [hz]
  obtain ⟨tl⟩ := t
  obtain ⟨pl⟩ := p
  simp only at hd hE hp ⊢
  show String.extract ⟨pl ++ tl⟩ ⟨pl.length⟩ ((⟨pl⟩ : String) ++ ⟨tl⟩).endPos = ⟨tl⟩
  cases tl with
  | nil =>
    simp only [String.extract]
    rw [if_pos (by simp at hE ⊢; rw [hE]; simp [String.utf8ByteSize.go])]
  | cons c tl =>
    have hc := Char.utf8Size_pos c
    simp only [String.extract]
    rw [if_neg (by rw [hE]; simp [String.utf8ByteSize.go]; omega)]
    congr 1
    have h1 := extract_go₁_skip pl hp (c :: tl) ((⟨pl⟩ : String) ++ ⟨c :: tl⟩).endPos 0 (Nat.zero_le _)
    simp only [List.drop_zero] at h1
    rw [show (0 : String.Pos) = ⟨0⟩ from rfl, h1]
    simp only [String.extract.go₁, if_true]
    have h2 := extract_go₂_all (c :: tl) pl.length
    have hE' : ((⟨pl⟩ : String) ++ ⟨c :: tl⟩).endPos = ⟨pl.length + String.utf8ByteSize.go (c :: tl)⟩ := by
      simp [String.Pos.ext_iff, hE]
    rw [hE', h2]

/-- `"over:" ++ n` for a key that starts with `over:`, with `n` the rest. -/
theorem over_drop {s : String} (h : s.startsWith "over:" = true) : "over:" ++ s.drop 5 = s := by
  have hp : AsciiL "over:".data := by decide
  obtain ⟨t, rfl⟩ := eq_append_of_startsWith hp h
  have := drop_append_ascii "over:" t hp
  rw [show "over:".length = 5 from rfl] at this
  rw [this]

end VE.Readings
