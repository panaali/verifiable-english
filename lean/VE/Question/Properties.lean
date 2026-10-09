import VE.Question.Read

namespace VE.Question
open VE.EnglishGrammar
open VE.Grammar (Derives)


/-- A candidate sentence lexes as one sentence and has no derivation. -/
def NoDerivation (E : Env) (L : Lexicon) (s : String) : Prop :=
  ∃ w, lex s = .ok #[w] ∧ ∀ t, ¬ Derives (grammar E L) (.n (grammar E L).start) w.toList t

/-- A candidate sentence lexes as one sentence and has at most one derivation. -/
def AtMostOneDerivation (E : Env) (L : Lexicon) (s : String) : Prop :=
  ∃ w, lex s = .ok #[w] ∧ ∀ t u, Derives (grammar E L) (.n (grammar E L).start) w.toList t →
    Derives (grammar E L) (.n (grammar E L).start) w.toList u → t = u

/-- An accepted one-sentence unmarked reading. -/
def HasReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) : Prop :=
  ∃ φ, EnglishOneReading E O L s [(φ, false)]

/-- R3: (a) every candidate lexes as one sentence with at most one derivation; (b) `c` is the first candidate that
    reads `[(φ, false)]`; (c) every other candidate reads `[(φ, false)]` or has no accepted one-sentence unmarked
    reading. -/
def QuestionOneReading (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (q : String) (c : Candidate)
    (φ : EFormula) : Prop :=
  c ∈ candidates auxs q ∧
  (∀ d ∈ candidates auxs q, AtMostOneDerivation E L d.sentence) ∧
  EnglishOneReading E O L c.sentence [(φ, false)] ∧
  (∀ d ∈ (candidates auxs q).takeWhile (fun d => d != c), ¬ HasReading E O L d.sentence) ∧
  (∀ d ∈ candidates auxs q, EnglishOneReading E O L d.sentence [(φ, false)] ∨ ¬ HasReading E O L d.sentence)

/-- `read_complete_english`'s hypotheses on the grammar. -/
def GrammarChecks (E : Env) (L : Lexicon) : Prop :=
  (grammar E L).wf = true ∧ terminatorFree (grammar E L) = true ∧
    (grammar E L).typed sig (ty E L) (acts E L) = true ∧ ty E L (grammar E L).start = .sentence


theorem got_none :
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (c : Candidate),
    got E O L b c = .none → NoDerivation E L c.sentence := by
  intro E O L b c h
  unfold got at h
  split at h
  · cases h
  · rename_i ws hlex
    split at h
    · cases h
    · rename_i hsize
      split at h <;> try cases h
      rename_i i hread
      obtain ⟨hv, hwf, _, _, _, sents, rs, st1, w, hl, hdoc, hw, ho, _⟩ :=
        read_stopped E O L b c.sentence i .noDerivation hread
      rw [hlex] at hl
      cases hl
      obtain ⟨w0, rfl⟩ := Array.size_eq_one_iff.mp (by simpa using hsize)
      cases i with
      | zero =>
        simp at hw
        subst w
        have hst : st1 = DState.init := by
          cases rs with
          | nil => simpa [VE.Grammar.DocOneReading] using hdoc
          | cons x xs => simp [VE.Grammar.DocOneReading] at hdoc
        subst st1
        cases hr : VE.Grammar.readSentence (grammar E L)
            (meaning (grammar E L) (acts E L)) DState.init b w0 with
        | mk out st2 =>
          simp only [hr] at ho
          subst out
          obtain ⟨_, hn⟩ := VE.Grammar.read_none hwf hr
          exact ⟨w0, hlex, hn⟩
      | succ i => simp at hw

theorem first_pred_unique {α : Type} [DecidableEq α] (xs : List α) (P : α → Prop)
    (c d : α) (hc : c ∈ xs) (hd : d ∈ xs) (hpc : P c) (hpd : P d)
    (hfirstc : ∀ x ∈ xs.takeWhile (fun x => x != c), ¬ P x)
    (hfirstd : ∀ x ∈ xs.takeWhile (fun x => x != d), ¬ P x) : c = d := by
  induction xs with
  | nil => cases hc
  | cons x xs ih =>
    by_cases hxc : x = c
    · by_cases hxd : x = d
      · exact hxc.symm.trans hxd
      · have hmem : x ∈ (x :: xs).takeWhile (fun y => y != d) := by simp [hxd]
        exact False.elim ((hfirstd x hmem) (hxc ▸ hpc))
    · by_cases hxd : x = d
      · have hmem : x ∈ (x :: xs).takeWhile (fun y => y != c) := by simp [hxc]
        exact False.elim ((hfirstc x hmem) (hxd ▸ hpd))
      · have hc' : c ∈ xs := by
          rcases List.mem_cons.mp hc with h | h
          · exact False.elim (hxc h.symm)
          · exact h
        have hd' : d ∈ xs := by
          rcases List.mem_cons.mp hd with h | h
          · exact False.elim (hxd h.symm)
          · exact h
        have hfc : ∀ y ∈ xs.takeWhile (fun y => y != c), ¬P y := by
          have htemp := hfirstc
          simp [hxc] at htemp
          exact htemp.2
        have hfd : ∀ y ∈ xs.takeWhile (fun y => y != d), ¬P y := by
          have htemp := hfirstd
          simp [hxd] at htemp
          exact htemp.2
        exact ih hc' hd' hfc hfd

theorem question_reading_unique :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (q : String) (c c' : Candidate) (φ φ' : EFormula),
    QuestionOneReading auxs E O L q c φ → QuestionOneReading auxs E O L q c' φ' → c = c' ∧ φ = φ' := by
  intro auxs E O L q c c' φ φ' h h'
  obtain ⟨hc, _, hr, hf, _⟩ := h
  obtain ⟨hc', _, hr', hf', _⟩ := h'
  have heq := first_pred_unique (candidates auxs q) (fun x => HasReading E O L x.sentence) c c' hc hc'
    ⟨φ, hr⟩ ⟨φ', hr'⟩ hf hf'
  subst c'
  have hs := english_reading_unique E O L c.sentence [(φ, false)] [(φ', false)] hr hr'
  cases hs
  exact ⟨rfl, rfl⟩

end VE.Question
