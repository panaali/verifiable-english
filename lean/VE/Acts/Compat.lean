import VE.Norms.Wire
import VE.Readings.Strings
import VE.Acts.LexicalProofs

/-! Theorems of `VE.Acts.Lexical` stated above both `Norms.Wire` and `Acts.Lexical` (docs/spec/act-phrases.md 4.3),
where the string lemmas they use are available. -/

namespace VE.Acts.Lexical

/-- A plain predicate's wording begins with its subject slot. -/
theorem wording_subject_first (f : Form) (act : String) (_h : act.startsWith "{0} " = true) :
    (wording f act).startsWith "{0} " = true := by
  unfold wording
  rw [String.append_assoc, String.append_assoc]
  exact VE.Readings.startsWith_append_ascii _ _ (by decide)

open VE.Norms.Wire (words actWord actReserved scanSlots pyWhitespace asciiLetter) in
/-- Every act today's check accepts and that has no *nor* passes `check` with the same string (1.3). -/
theorem check_extends (fx : List String) (h : fixedOk fx = true) {name : String} {k : Nat}
    {raw : Lean.Json} {a : String} (hc : VE.Norms.Wire.canonicalAct name k raw = .ok a)
    (hn : ∀ w ∈ VE.Norms.Wire.words a, w.toLower ≠ "nor") : check fx name k raw = .ok a := by
  unfold VE.Norms.Wire.canonicalAct at hc
  simp only [bind, Except.bind, pure, Except.pure] at hc
  split at hc
  case isFalse => cases hc
  rename_i hcond
  generalize hs : (raw.getStr?).toOption.getD "" = s at hcond hc
  have ha : " ".intercalate (words s) = a := by simpa using hc
  rw [ha] at hcond
  generalize hW : words ⟨(scanSlots a.toList).2⟩ = W at hcond
  simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, List.all_eq_true, Bool.not_eq_true',
    List.any_eq_false] at hcond
  obtain ⟨⟨⟨⟨⟨hlen, hstart⟩, hslots⟩, hws2⟩, hact⟩, hres⟩ := hcond
  -- the act's characters, its words and its canonical form
  have hwa : words a = words s :=
    ha ▸ words_intercalate fun w hw => ⟨(mem_words hw).1, fun c hc => ((mem_words hw).2 c hc).2⟩
  have hgood : ∀ c ∈ a.data, pyWhitespace c = false → c ≠ '{' → c ≠ '}' → c.isDigit = false →
      asciiLetter c ∨ c = '\'' ∨ c = '-' := by
    intro c hc h0 h1 h2 h3
    obtain ⟨w, hw, hcw⟩ := out_cover hc h1 h2 h3 h0
    exact actWord_chars (hact w (hW ▸ hw)) c hcw
  have hq : ∀ c ∈ a.data, c.toNat ≠ 0x2019 := by
    intro c hc he
    have : c = '\u2019' := Char.ext (UInt32.toNat_inj.mp he)
    subst this
    have := hgood _ hc (by decide) (by decide) (by decide) (by decide)
    revert this; decide
  have hcomma : ',' ∉ a.data := fun hc => by
    have := hgood ',' hc (by decide) (by decide) (by decide) (by decide)
    revert this; decide
  have hsq : ∀ c ∈ s.data, c.toNat ≠ 0x2019 := by
    intro c hc he
    obtain ⟨w, hw, hcw⟩ := words_cover hc (by simp only [pyWhitespace, he]; decide)
    rw [← hwa] at hw
    exact hq c ((mem_words hw).2 c hcw).1 he
  have hnorm : normal s = a := by unfold normal; rw [fold_eq_self hsq, ha]
  have hnorm_a : normal a = a := by unfold normal; rw [fold_eq_self hq, hwa, ha]
  have hdrop : ∀ w ∈ W, dropComma w = w := by
    intro w hw
    unfold dropComma
    rw [if_neg]
    intro he
    have := actWord_chars (hact w hw) ',' (endsWith_comma he)
    revert this; decide
  -- the tokens of the act: one per word, never a comma, and no join word
  obtain ⟨ps, hps⟩ : ∃ ps, decodeFixed fx = .ok ps := by
    unfold fixedOk at h
    cases hd : decodeFixed fx with
    | error e => rw [hd] at h; cases h
    | ok ps => exact ⟨ps, rfl⟩
  have hpieces : (a.splitOn " ").filter (· ≠ "") = words a := by
    rw [splitOn_space, splitL_congr (q := pyWhitespace)]
    · simp only [words, split_data]
    · intro c hc
      rw [← ha] at hc
      rcases mem_intercalate hc with rfl | ⟨w, hw, hcw⟩
      · rfl
      · have h0 := ((mem_words hw).2 c hcw).2
        rw [h0]
        simp only [beq_eq_false_iff_ne]
        rintro rfl
        revert h0; decide
  have hpiece : ∀ w ∈ words a, pieceToks w = .ok [pieceTok w] := by
    intro w hw
    have hcw : ',' ∉ w.data := fun h => hcomma ((mem_words hw).2 ',' h).1
    have hend : w.endsWith "," = false := Bool.eq_false_iff.mpr fun he => hcw (endsWith_comma he)
    have hcon : w.contains ',' = false := Bool.eq_false_iff.mpr fun he => hcw (contains_mem (by decide) he)
    unfold pieceToks dropComma
    simp only [hend, Bool.false_eq_true, ↓reduceIte, isEmpty_false (mem_words hw).1, hcon, Bool.false_or]
    rfl
  have hraw : rawLex a = .ok ((words a).map pieceTok) := by
    unfold rawLex
    rw [hpieces, mapM_ok hpiece]
    have hflat : ∀ L : List String, (L.map (fun x => [pieceTok x])).flatten = L.map pieceTok := by
      intro L; induction L <;> simp_all
    simp only [bind, Except.bind, foldl_append_eq, List.nil_append, hflat]
    rw [if_neg]
    · rfl
    · intro hl
      simp only [List.getLast?_map, beq_iff_eq, Option.map_eq_some_iff] at hl
      obtain ⟨w, _, hw⟩ := hl
      unfold pieceTok at hw
      split at hw <;> cases hw
  have hlex : lex fx a = .ok (group ps ((words a).map pieceTok).length ((words a).map pieceTok)) := by
    unfold lex
    simp only [bind, Except.bind, hps, hnorm_a, hraw, pure, Except.pure]
  have hjoin : ∀ w ∈ words a, joinWords.contains w.toLower = false := by
    intro w hw
    by_cases hb : '{' ∈ w.data
    · exact (not_listed (toLower_mem hb (by decide)) (.inl rfl)).2
    · have hw' : w ∈ W := by
        have := word_out hw
        rw [out_eq_self _ hb] at this
        exact hW ▸ this
      by_cases hsl : w = "slot"
      · subst hsl
        rw [show "slot".toLower = "slot" from String.ext (by rw [String.toLower, VE.Readings.map_data]; decide)]
        decide
      have hr : actReserved.contains w.toLower = false := by simpa [hsl] using hres w hw'
      rw [Bool.eq_false_iff]
      intro hj
      have hm := List.contains_iff_mem.mp hj
      simp only [joinWords, List.mem_cons, List.mem_nil_iff, or_false] at hm
      rcases hm with hm | hm | hm | hm
      · rw [hm] at hr; cases hr
      · rw [hm] at hr; cases hr
      · exact hn w hw hm
      · rw [hm] at hr; cases hr
  -- `check`'s steps
  unfold check checkWith joinCheck
  simp only [bind, Except.bind, pure, Except.pure]
  rw [hs, hnorm, hW]
  rw [if_pos, if_pos]
  · rw [List.find?_eq_none.mpr]
    · simp only [hlex]
      rw [List.find?_eq_none.mpr]
      intro t ht
      rcases mem_group ht with ht | ⟨i, rfl⟩
      · obtain ⟨w, hw, rfl⟩ := List.mem_map.mp ht
        cases hsl : slotOf? w
        · have := hjoin w hw
          simp only [pieceTok, hsl, this]
          decide
        · simp [pieceTok, hsl]
      · simp
    · intro w hw hcl
      rw [hdrop w hw, Bool.and_eq_true] at hcl
      exact hres w hw ⟨hcl.1, clause_reserved hcl.2⟩
  · have := utf8ByteSize_le a
    simp only [maxActBytes]
    omega
  · simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, List.all_eq_true]
    exact ⟨⟨⟨hstart, hslots⟩, hws2⟩, fun w hw => by rw [hdrop w hw]; exact hact w hw⟩

end VE.Acts.Lexical
