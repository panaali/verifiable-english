import VE.Question.Read

namespace VE.Question
open VE.EnglishGrammar
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

namespace VE.Question
open VE.EnglishGrammar

private def addMeaning (acc : List (Candidate × EFormula)) (x : Candidate × Got) :
    List (Candidate × EFormula) :=
  match x.2.meaning? with
  | some φ => if acc.any (·.2 == φ) then acc else acc ++ [(x.1, φ)]
  | none => acc

theorem fold_meanings_sound (gs : List (Candidate × Got))
    (acc : List (Candidate × EFormula)) (x : Candidate × EFormula)
    (h : x ∈ gs.foldl addMeaning acc) :
    x ∈ acc ∨ ∃ y ∈ gs, y.1 = x.1 ∧ y.2 = .one x.2 := by
  induction gs generalizing acc with
  | nil => exact Or.inl h
  | cons y ys ih =>
    have h' := ih (addMeaning acc y) (by simpa using h)
    rcases h' with hacc | ⟨z, hz, hp⟩
    · unfold addMeaning at hacc
      cases hg : y.2.meaning? with
      | none => exact Or.inl (by simpa [hg] using hacc)
      | some φ =>
        by_cases hex : acc.any (·.2 == φ) = true
        · exact Or.inl (by simpa [hg, hex] using hacc)
        · have ha : x ∈ acc ∨ x = (y.1, φ) := by
            simpa [hg, hex] using hacc
          rcases ha with ha | ha
          · exact Or.inl ha
          · right
            refine ⟨y, by simp, ?_⟩
            cases y with
            | mk c g =>
              cases g <;> simp [Got.meaning?] at hg
              rename_i ψ
              cases hg
              simp [ha]
    · exact Or.inr ⟨z, by simp [hz], hp⟩

theorem firstMeanings_sound (gs : List (Candidate × Got)) (x : Candidate × EFormula)
    (h : x ∈ firstMeanings gs) :
    ∃ y ∈ gs, y.1 = x.1 ∧ y.2 = .one x.2 := by
  unfold firstMeanings at h
  have hs := fold_meanings_sound gs [] x h
  simpa using hs

end VE.Question

namespace VE.Question
open VE.EnglishGrammar

theorem got_one_read (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (c : Candidate) (φ : EFormula) (h : got E O L b c = .one φ) :
    read E O L b c.sentence = .ok [(φ, false)] := by
  unfold got at h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  all_goals assumption

end VE.Question

namespace VE.Question
open VE.EnglishGrammar

theorem classify_one_read (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon)
    (b : Nat) (q : String) (c : Candidate) (φ : EFormula)
    (h : classify auxs E O L b q = .one c φ) :
    c ∈ candidates auxs q ∧ read E O L b c.sentence = .ok [(φ, false)] := by
  unfold classify at h
  dsimp only at h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  all_goals try (split at h <;> try cases h)
  all_goals
    have hm : (c, φ) ∈ firstMeanings
        (List.map (fun d => (d, got E O L b d)) (candidates auxs q)) := by
      have hf : firstMeanings
          (List.map (fun d => (d, got E O L b d)) (candidates auxs q)) = [(c, φ)] := by
        assumption
      simp [hf]
    obtain ⟨y, hy, hcy, hgy⟩ := firstMeanings_sound _ _ hm
    rcases List.mem_map.mp hy with ⟨d, hd, hdy⟩
    subst y
    simp at hcy
    subst d
    exact ⟨hd, got_one_read E O L b c φ (by simpa using hgy)⟩

end VE.Question

namespace VE.Question
open VE.EnglishGrammar

theorem readQuestion_one_read (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon)
    (b : Nat) (q : String) (c : Candidate) (φ : EFormula)
    (h : readQuestion auxs E O L b q = .one c φ) :
    c ∈ candidates auxs q ∧ read E O L b c.sentence = .ok [(φ, false)] := by
  unfold readQuestion at h
  dsimp only at h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  all_goals exact classify_one_read auxs E O L b q c φ (by assumption)

theorem asked_reads_back :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate) (φ : EFormula),
    readQuestion auxs E O L b q = .one c φ → checkRendering E O L b [(φ, false)] c.sentence = true := by
  intro auxs E O L b q c φ h
  exact (checked_rendering_exact E O L b [(φ, false)] c.sentence).mpr
    (readQuestion_one_read auxs E O L b q c φ h).2

end VE.Question

namespace VE.Question
open VE.EnglishGrammar
open VE.Grammar (Derives)

theorem got_many_derivations (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (c : Candidate) (h : got E O L b c = .many) :
    ∃ w t u, lex c.sentence = .ok #[w] ∧ t ≠ u ∧
      Derives (grammar E L) (.n (grammar E L).start) w.toList t ∧
      Derives (grammar E L) (.n (grammar E L).start) w.toList u := by
  unfold got at h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  all_goals rename_i ws hlex hsize i t u hread
  all_goals
    obtain ⟨w0, harr⟩ := Array.size_eq_one_iff.mp (by simpa using hlex)
    rw [harr] at ws
    obtain ⟨_, hwf, _, _, _, sents, rs, st1, w, hl, hdoc, hw, ho, _⟩ :=
      read_stopped E O L b c.sentence i (.ambiguous t u) hread
    rw [ws] at hl
    cases hl
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
        obtain ⟨_, ht, hu, hne⟩ := VE.Grammar.read_ambiguous hr
        exact ⟨w0, t, u, ws, hne, ht, hu⟩
    | succ i => simp at hw

end VE.Question

namespace VE.Question
open VE.EnglishGrammar

theorem classify_ambiguous_candidate (auxs : List String) (E : Env) (O : Overlay)
    (L : Lexicon) (b : Nat) (q : String) (c : Candidate)
    (h : classify auxs E O L b q = .ambiguous c) :
    c ∈ candidates auxs q ∧ got E O L b c = .many := by
  unfold classify at h
  dsimp only at h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  all_goals try (split at h <;> try cases h)
  all_goals try (split at h <;> try cases h)
  all_goals try (split at h <;> try cases h)
  all_goals
    have hf : ∃ g, (List.map (fun d => (d, got E O L b d))
        (candidates auxs q)).find? (fun x => x.2.isMany) = some (c, g) := by
      exact ⟨_, by assumption⟩
    obtain ⟨g, hfind⟩ := hf
    have hmany : g.isMany = true := by
      have hp := List.find?_some hfind
      simpa using hp
    have hmem := List.mem_of_find?_eq_some hfind
    rcases List.mem_map.mp hmem with ⟨d, hd, hdc⟩
    cases g <;> simp [Got.isMany] at hmany
    case many =>
      have hcd : d = c := congrArg Prod.fst hdc
      have hgot : got E O L b d = .many := congrArg Prod.snd hdc
      subst d
      exact ⟨hd, hgot⟩

end VE.Question

namespace VE.Question
open VE.EnglishGrammar
open VE.Grammar (Derives)

theorem readQuestion_ambiguous :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate),
    readQuestion auxs E O L b q = .ambiguous c → c ∈ candidates auxs q ∧
    ∃ w t u, lex c.sentence = .ok #[w] ∧ t ≠ u ∧ Derives (grammar E L) (.n (grammar E L).start) w.toList t ∧
      Derives (grammar E L) (.n (grammar E L).start) w.toList u := by
  intro auxs E O L b q c h
  have hc : classify auxs E O L b q = .ambiguous c := by
    unfold readQuestion at h
    dsimp only at h
    split at h <;> try cases h
    split at h <;> try cases h
    split at h <;> try cases h
    all_goals assumption
  obtain ⟨hm, hg⟩ := classify_ambiguous_candidate auxs E O L b q c hc
  exact ⟨hm, got_many_derivations E O L b c hg⟩

end VE.Question
