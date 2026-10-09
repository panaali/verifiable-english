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

namespace VE.Question
open VE.EnglishGrammar

theorem addMeaning_nodup (acc : List (Candidate × EFormula))
    (y : Candidate × Got) (h : (acc.map Prod.snd).Nodup) :
    ((addMeaning acc y).map Prod.snd).Nodup := by
  unfold addMeaning
  cases hm : y.2.meaning? with
  | none => simpa [hm] using h
  | some φ =>
    by_cases ha : acc.any (·.2 == φ) = true
    · simpa [hm, ha] using h
    · have hn : φ ∉ acc.map Prod.snd := by
        intro hmem
        obtain ⟨z, hz, hφ⟩ := List.mem_map.mp hmem
        have ht : acc.any (fun x => x.2 == φ) = true :=
          List.any_eq_true.mpr ⟨z, hz, by simp [hφ]⟩
        exact ha ht
      simp [ha, List.map_append, List.nodup_append, h]
      intro a x hx heq
      apply hn
      exact heq ▸ List.mem_map_of_mem hx

theorem fold_meanings_nodup (gs : List (Candidate × Got))
    (acc : List (Candidate × EFormula)) (h : (acc.map Prod.snd).Nodup) :
    ((gs.foldl addMeaning acc).map Prod.snd).Nodup := by
  induction gs generalizing acc with
  | nil => simpa using h
  | cons y ys ih =>
    exact ih (addMeaning acc y) (addMeaning_nodup acc y h)

theorem firstMeanings_nodup (gs : List (Candidate × Got)) :
    ((firstMeanings gs).map Prod.snd).Nodup := by
  change ((gs.foldl addMeaning []).map Prod.snd).Nodup
  exact fold_meanings_nodup gs [] (by simp)

theorem classify_meanings_sound (auxs : List String) (E : Env) (O : Overlay)
    (L : Lexicon) (b : Nat) (q : String)
    (fs : List (Candidate × EFormula)) (rs : List String)
    (h : classify auxs E O L b q = .meanings fs rs) :
    2 ≤ fs.length ∧ (fs.map (·.2)).Nodup ∧
    (∀ x ∈ fs, x.1 ∈ candidates auxs q ∧ read E O L b x.1.sentence = .ok [(x.2, false)]) ∧
    rs = fs.map (fun x => caseThatQuestion x.1) := by
  unfold classify at h
  dsimp only at h
  repeat (split at h <;> try cases h)
  all_goals
    refine ⟨?_, ?_, ?_, rfl⟩
    · cases hlist : firstMeanings
          (List.map (fun c => (c, got E O L b c)) (candidates auxs q)) with
      | nil => simp_all
      | cons x xs =>
        cases xs with
        | nil => cases x; simp_all
        | cons y ys => simp
    · exact firstMeanings_nodup _
    · intro x hx
      obtain ⟨y, hy, hcy, hgy⟩ := firstMeanings_sound _ x hx
      rcases List.mem_map.mp hy with ⟨d, hd, hdy⟩
      subst y
      simp at hcy
      subst d
      exact ⟨hd, got_one_read E O L b x.1 x.2 (by simpa using hgy)⟩

theorem readQuestion_meanings :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String)
    (fs : List (Candidate × EFormula)) (rs : List String),
    readQuestion auxs E O L b q = .meanings fs rs →
    2 ≤ fs.length ∧ (fs.map (·.2)).Nodup ∧
    (∀ x ∈ fs, x.1 ∈ candidates auxs q ∧ read E O L b x.1.sentence = .ok [(x.2, false)]) ∧
    rs = fs.map (fun x => caseThatQuestion x.1) := by
  intro auxs E O L b q fs rs h
  have hc : classify auxs E O L b q = .meanings fs rs := by
    unfold readQuestion at h
    dsimp only at h
    repeat (split at h <;> try cases h)
    all_goals assumption
  exact classify_meanings_sound auxs E O L b q fs rs hc

end VE.Question

namespace VE.Question
open VE.EnglishGrammar

theorem addMeaning_nonempty (acc : List (Candidate × EFormula))
    (y : Candidate × Got) (h : acc ≠ []) : addMeaning acc y ≠ [] := by
  unfold addMeaning
  cases hm : y.2.meaning? with
  | none => simpa [hm] using h
  | some φ =>
    by_cases ha : acc.any (·.2 == φ) = true
    · simpa [hm, ha] using h
    · simp [ha]

theorem foldMeaning_nonempty (gs : List (Candidate × Got))
    (acc : List (Candidate × EFormula)) (h : acc ≠ []) :
    gs.foldl addMeaning acc ≠ [] := by
  induction gs generalizing acc with
  | nil => simpa using h
  | cons y ys ih =>
    exact ih (addMeaning acc y) (addMeaning_nonempty acc y h)

theorem addMeaning_one_nonempty (acc : List (Candidate × EFormula))
    (y : Candidate × Got) (φ : EFormula) (hy : y.2 = .one φ) :
    addMeaning acc y ≠ [] := by
  unfold addMeaning
  simp only [hy, Got.meaning?]
  by_cases ha : acc.any (·.2 == φ) = true
  · have hn : acc ≠ [] := by
      intro he
      simp [he] at ha
    simpa [ha] using hn
  · simp [ha]

theorem foldMeaning_one_nonempty (gs : List (Candidate × Got))
    (acc : List (Candidate × EFormula)) (y : Candidate × Got)
    (φ : EFormula) (hy : y ∈ gs) (hone : y.2 = .one φ) :
    gs.foldl addMeaning acc ≠ [] := by
  induction gs generalizing acc with
  | nil => cases hy
  | cons z zs ih =>
    rcases List.mem_cons.mp hy with h | h
    · subst y
      exact foldMeaning_nonempty zs (addMeaning acc z)
        (addMeaning_one_nonempty acc z φ hone)
    · exact ih (addMeaning acc z) h

theorem firstMeanings_empty_no_one (gs : List (Candidate × Got))
    (h : firstMeanings gs = []) (y : Candidate × Got) (hy : y ∈ gs)
    (φ : EFormula) : y.2 ≠ .one φ := by
  intro hone
  have hh : gs.foldl addMeaning [] ≠ [] :=
    foldMeaning_one_nonempty gs [] y φ hy hone
  exact hh (by simpa [firstMeanings, addMeaning] using h)

theorem no_flags_only_none (gs : List (Candidate × Got))
    (hn : gs.any (·.2.isNotOne) = false)
    (hb : gs.find? (·.2.isBudget) = none)
    (hm : gs.find? (·.2.isMany) = none)
    (hf : firstMeanings gs = [])
    (hr : gs.find? (·.2.isRefused) = none)
    (y : Candidate × Got) (hy : y ∈ gs) : y.2 = .none := by
  have hn' := (List.any_eq_false.mp hn) y hy
  have hb' := (List.find?_eq_none.mp hb) y hy
  have hm' := (List.find?_eq_none.mp hm) y hy
  have hr' := (List.find?_eq_none.mp hr) y hy
  have hf' := firstMeanings_empty_no_one gs hf y hy
  cases hg : y.2 <;> simp_all [Got.isNotOne, Got.isBudget, Got.isMany, Got.isRefused]

theorem classify_none_got (auxs : List String) (E : Env) (O : Overlay)
    (L : Lexicon) (b : Nat) (q : String) (cl : Option Candidate)
    (h : classify auxs E O L b q = .none cl) :
    ∀ d ∈ candidates auxs q, got E O L b d = .none := by
  unfold classify at h
  dsimp only at h
  repeat (split at h <;> try cases h)
  all_goals
    let gs := List.map (fun c => (c, got E O L b c)) (candidates auxs q)
    have hn : gs.any (·.2.isNotOne) = false := by
      cases hv : gs.any (·.2.isNotOne) <;> simp_all [gs]
    have hb : gs.find? (·.2.isBudget) = none := by assumption
    have hm : gs.find? (·.2.isMany) = none := by assumption
    have hf : firstMeanings gs = [] := by assumption
    have hr : gs.find? (·.2.isRefused) = none := by
      cases hfind : gs.find? (·.2.isRefused) with
      | none => rfl
      | some y =>
        have hp := List.find?_some hfind
        cases y with
        | mk c g =>
          cases g <;> simp [Got.isRefused] at hp
          case refused o =>
            have hbad : ∀ c o, gs.find? (·.2.isRefused) = some (c, .refused o) → False := by
              assumption
            exact False.elim (hbad c o hfind)
    intro d hd
    have hmem : (d, got E O L b d) ∈ gs := List.mem_map_of_mem hd
    exact no_flags_only_none gs hn hb hm hf hr _ hmem

theorem readQuestion_indefinite :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q art : String) (rs : List String),
    readQuestion auxs E O L b q = .indefinite art rs → ∀ d ∈ candidates auxs q, NoDerivation E L d.sentence := by
  intro auxs E O L b q art rs h
  have hc : ∃ cl, classify auxs E O L b q = .none cl := by
    unfold readQuestion at h
    dsimp only at h
    repeat (split at h <;> try cases h)
    all_goals first
      | exact ⟨_, by assumption⟩
      | (exfalso; unfold classify at h; dsimp only at h;
         repeat (split at h <;> try cases h))
  obtain ⟨cl, hc⟩ := hc
  intro d hd
  exact got_none E O L b d (classify_none_got auxs E O L b q cl hc d hd)

end VE.Question

namespace VE.Question
open VE.EnglishGrammar

theorem closestStep_mem (E : Env) (L : Lexicon) (all : List Candidate)
    (best : Option (Candidate × Nat)) (x : Candidate)
    (hb : ∀ c k, best = some (c, k) → c ∈ all) (hx : x ∈ all) :
    ∀ c k, closestStep E L best x = some (c, k) → c ∈ all := by
  intro c k h
  unfold closestStep at h
  split at h <;> try cases h
  all_goals try exact hx
  all_goals try (apply hb; rfl)
  all_goals
    split at h <;> cases h
    all_goals first | exact hx | exact hb c k rfl

theorem closestFold_mem (E : Env) (L : Lexicon) (all cs : List Candidate)
    (best : Option (Candidate × Nat))
    (hb : ∀ c k, best = some (c, k) → c ∈ all)
    (hcs : ∀ c ∈ cs, c ∈ all) :
    ∀ c k, cs.foldl (closestStep E L) best = some (c, k) → c ∈ all := by
  induction cs generalizing best with
  | nil =>
    intro c k h
    exact hb c k (by simpa using h)
  | cons x xs ih =>
    have hx : x ∈ all := hcs x (by simp)
    have hxs : ∀ y ∈ xs, y ∈ all := by
      intro y hy
      exact hcs y (by simp [hy])
    exact ih (closestStep E L best x) (closestStep_mem E L all best x hb hx) hxs

theorem closest_mem (E : Env) (L : Lexicon) (cs : List Candidate)
    (c : Candidate) (h : closest E L cs = some c) : c ∈ cs := by
  change (cs.foldl (closestStep E L) none).map Prod.fst = some c at h
  have hf : ∃ k, cs.foldl (closestStep E L) none = some (c, k) := by
    cases hfold : cs.foldl (closestStep E L) none with
    | none => simp [hfold] at h
    | some p =>
      cases p with
      | mk d k =>
        simp only [hfold, Option.map_some] at h
        cases h
        exact ⟨k, rfl⟩
  obtain ⟨k, hk⟩ := hf
  exact closestFold_mem E L cs cs none (by simp) (by simp) c k hk

theorem readQuestion_none :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (cl : Option Candidate),
    readQuestion auxs E O L b q = .none cl →
    (∀ d ∈ candidates auxs q, NoDerivation E L d.sentence) ∧ ∀ d, cl = some d → d ∈ candidates auxs q := by
  intro auxs E O L b q cl h
  have hc : classify auxs E O L b q = .none cl := by
    unfold readQuestion at h
    dsimp only at h
    repeat (split at h <;> try cases h)
    all_goals first
      | assumption
      | (exfalso; unfold classify at h; dsimp only at h;
         repeat (split at h <;> try cases h))
  constructor
  · intro d hd
    exact got_none E O L b d (classify_none_got auxs E O L b q cl hc d hd)
  · intro d hd
    unfold classify at hc
    dsimp only at hc
    repeat (split at hc <;> try cases hc)
    all_goals exact closest_mem E L (candidates auxs q) d hd

end VE.Question

namespace VE.Question
open VE.EnglishGrammar
open VE.Grammar (Derives)

/-- The checks of `read`, as `grammarFault`'s `none` gives them. -/
theorem grammarFault_none_checks {E : Env} {O : Overlay} {L : Lexicon} (h : grammarFault E O L = none) :
    L.policyOk E O = true ∧ L.valid E O = true ∧ GrammarChecks E L := by
  unfold grammarFault at h
  by_cases hp : L.policyOk E O = true
  · by_cases hv : L.valid E O = true
    · by_cases h2 : ((grammar E L).wf && terminatorFree (grammar E L)) = true
      · by_cases h3 : ((grammar E L).typed sig (ty E L) (acts E L) &&
            decide (ty E L (grammar E L).start = .sentence)) = true
        · simp only [Bool.and_eq_true, decide_eq_true_eq] at h2 h3
          exact ⟨hp, hv, h2.1, h2.2, h3.1, h3.2⟩
        · simp [hp, hv, h2, h3] at h
      · simp [hp, hv, h2] at h
    · simp [hp, hv] at h
  · simp [hp] at h

theorem grammarFault_eq_none {E : Env} {O : Overlay} {L : Lexicon} (hp : L.policyOk E O = true)
    (hv : L.valid E O = true) (hg : GrammarChecks E L) : grammarFault E O L = none := by
  obtain ⟨h1, h2, h3, h4⟩ := hg
  unfold grammarFault
  simp [hp, hv, h1, h2, h3, h4]

/-- `read` of one lexed sentence, after its checks. -/
theorem read_single {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String} {w : Array Tok}
    (hv : L.valid E O = true) (hg : GrammarChecks E L) (hl : lex s = .ok #[w]) :
    read E O L b s = match VE.Grammar.readSentence (grammar E L) (meaning (grammar E L) (acts E L))
        DState.init b w with
      | (.ok A m, _) => if typedDocument E [A] then .ok [(A, m)] else .illTyped
      | (o, _) => .stopped 0 o := by
  obtain ⟨h2, h3, h4, h5⟩ := hg
  rw [read_eq hv h2 h3 h4 h5, hl]
  cases hr : VE.Grammar.readSentence (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b w with
  | mk o st1 =>
    cases o <;> simp [VE.Grammar.readDocument, hr]

theorem got_lex {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {c : Candidate}
    (h : (got E O L b c).isNotOne = false) : ∃ w, lex c.sentence = .ok #[w] := by
  unfold got at h
  split at h
  · simp [Got.isNotOne] at h
  · rename_i ws hl
    by_cases hs : ws.size = 1
    · obtain ⟨w, rfl⟩ := Array.size_eq_one_iff.mp hs
      exact ⟨w, hl⟩
    · simp [hs, Got.isNotOne] at h

/-- `got` of one lexed sentence, after `read`'s checks. -/
theorem got_single {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {c : Candidate} {w : Array Tok}
    (hv : L.valid E O = true) (hg : GrammarChecks E L) (hl : lex c.sentence = .ok #[w]) :
    got E O L b c = match VE.Grammar.readSentence (grammar E L) (meaning (grammar E L) (acts E L))
        DState.init b w with
      | (.ok A m, _) => if typedDocument E [A] then (if m then .refused (.ok [(A, true)]) else .one A)
          else .refused .illTyped
      | (.noDerivation, _) => .none
      | (.ambiguous _ _, _) => .many
      | (.budget, _) => .budget
      | (.rejected r, _) => .refused (.stopped 0 (.rejected r)) := by
  unfold got
  rw [hl]
  simp only [List.size_toArray, List.length_singleton, bne_self_eq_false, Bool.false_eq_true, if_false]
  rw [read_single hv hg hl]
  cases hr : VE.Grammar.readSentence (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b w with
  | mk o st1 =>
    cases o with
    | ok A m =>
      by_cases ht : typedDocument E [A] = true
      · cases m <;> simp [ht]
      · simp [ht]
    | _ => simp

theorem got_atMostOne {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {c : Candidate}
    (hv : L.valid E O = true) (hg : GrammarChecks E L) (hn : (got E O L b c).isNotOne = false)
    (hb : (got E O L b c).isBudget = false) (hm : (got E O L b c).isMany = false) :
    AtMostOneDerivation E L c.sentence := by
  obtain ⟨w, hl⟩ := got_lex hn
  refine ⟨w, hl, ?_⟩
  rw [got_single hv hg hl] at hb hm
  have hwf := hg.1
  cases hr : VE.Grammar.readSentence (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b w with
  | mk o st1 =>
    rw [hr] at hb hm
    cases o with
    | ok A m =>
      obtain ⟨t, _, hu, _⟩ := VE.Grammar.read_sound hwf hr
      intro t1 t2 h1 h2
      exact (hu t1 h1).trans (hu t2 h2).symm
    | noDerivation =>
      obtain ⟨_, hn⟩ := VE.Grammar.read_none hwf hr
      intro t1 _ h1
      exact absurd h1 (hn t1)
    | ambiguous t u => simp [Got.isMany] at hm
    | rejected r =>
      obtain ⟨_, t, _, hu, _⟩ := VE.Grammar.read_rejected hwf hr
      intro t1 t2 h1 h2
      exact (hu t1 h1).trans (hu t2 h2).symm
    | budget => simp [Got.isBudget] at hb

theorem got_of_reading {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {c : Candidate} {ψ : EFormula}
    (hv : L.valid E O = true) (hg : GrammarChecks E L) (hn : (got E O L b c).isNotOne = false)
    (hb : (got E O L b c).isBudget = false) (hr : EnglishOneReading E O L c.sentence [(ψ, false)]) :
    got E O L b c = .one ψ := by
  obtain ⟨w, hl⟩ := got_lex hn
  obtain ⟨_, sents, st2, hl2, hd, ht⟩ := hr
  rw [hl] at hl2
  cases hl2
  obtain ⟨st1, hone, _⟩ := hd
  rw [got_single hv hg hl] at hb ⊢
  rcases VE.Grammar.read_complete (b := b) hg.1 hone with hs | hs
  · rw [hs]
    simp only [List.map_cons, List.map_nil] at ht
    simp [ht]
  · rw [hs] at hb
    simp [Got.isBudget] at hb

theorem got_one_reading {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {c : Candidate} {ψ : EFormula}
    (h : got E O L b c = .one ψ) : EnglishOneReading E O L c.sentence [(ψ, false)] :=
  read_ok E O L b c.sentence _ (got_one_read E O L b c ψ h)


theorem fold_meanings_cons (gs : List (Candidate × Got)) (a : Candidate × EFormula)
    (as : List (Candidate × EFormula)) : ∃ rest, gs.foldl addMeaning (a :: as) = a :: rest := by
  induction gs generalizing as with
  | nil => exact ⟨as, rfl⟩
  | cons y ys ih =>
    simp only [List.foldl_cons]
    have : ∃ as', addMeaning (a :: as) y = a :: as' := by
      unfold addMeaning
      split
      · split
        · exact ⟨as, rfl⟩
        · exact ⟨as ++ _, rfl⟩
      · exact ⟨as, rfl⟩
    obtain ⟨as', h⟩ := this
    rw [h]
    exact ih as'

theorem firstMeanings_takeWhile (gs : List (Candidate × Got)) (c : Candidate) (φ : EFormula)
    (rest : List (Candidate × EFormula)) (h : firstMeanings gs = (c, φ) :: rest) :
    ∀ y ∈ gs.takeWhile (fun y => y.1 != c), y.2.meaning? = none := by
  induction gs with
  | nil => simp
  | cons y ys ih =>
    unfold firstMeanings at h
    simp only [List.foldl_cons] at h
    cases hm : y.2.meaning? with
    | none =>
      have h' : firstMeanings ys = (c, φ) :: rest := by
        unfold firstMeanings
        have : addMeaning [] y = [] := by simp [addMeaning, hm]
        rw [this] at h
        exact h
      intro z hz
      by_cases hy : (y.1 != c) = true
      · simp only [List.takeWhile_cons, hy, if_true] at hz
        rcases List.mem_cons.mp hz with rfl | hz
        · exact hm
        · exact ih h' z hz
      · simp only [List.takeWhile_cons, hy, Bool.false_eq_true, if_false] at hz
        cases hz
    | some ψ =>
      have : addMeaning [] y = [(y.1, ψ)] := by simp [addMeaning, hm]
      rw [this] at h
      obtain ⟨rest', h2⟩ := fold_meanings_cons ys (y.1, ψ) []
      rw [h2] at h
      simp only [List.cons.injEq, Prod.mk.injEq] at h
      intro z hz
      have hy : (y.1 != c) = false := by simp [h.1.1]
      rw [List.takeWhile_cons_of_neg (by simp [hy])] at hz
      cases hz

theorem fold_meanings_complete (gs : List (Candidate × Got)) (acc : List (Candidate × EFormula))
    (y : Candidate × Got) (ψ : EFormula) (hy : y ∈ gs) (hm : y.2.meaning? = some ψ) :
    ∃ x ∈ gs.foldl addMeaning acc, x.2 = ψ := by
  have keep : ∀ (zs : List (Candidate × Got)) (acc : List (Candidate × EFormula)) (x : Candidate × EFormula),
      x ∈ acc → x ∈ zs.foldl addMeaning acc := by
    intro zs
    induction zs with
    | nil => intro acc x hx; exact hx
    | cons z zs ih =>
      intro acc x hx
      apply ih
      unfold addMeaning
      split
      · split
        · exact hx
        · exact List.mem_append_left _ hx
      · exact hx
  induction gs generalizing acc with
  | nil => cases hy
  | cons z zs ih =>
    rcases List.mem_cons.mp hy with rfl | hy
    · simp only [List.foldl_cons]
      unfold addMeaning
      rw [hm]
      by_cases ha : acc.any (·.2 == ψ) = true
      · simp only [ha, if_true]
        obtain ⟨x, hx, hxe⟩ := List.any_eq_true.mp ha
        exact ⟨x, keep zs acc x hx, by simpa using hxe⟩
      · simp only [ha, Bool.false_eq_true, if_false]
        exact ⟨(y.1, ψ), keep zs _ _ (List.mem_append_right _ (by simp)), rfl⟩
    · exact ih (addMeaning acc z) hy

theorem fold_meanings_fixed (gs : List (Candidate × Got)) (c : Candidate) (φ : EFormula)
    (h : ∀ y ∈ gs, ∀ ψ, y.2.meaning? = some ψ → ψ = φ) :
    gs.foldl addMeaning [(c, φ)] = [(c, φ)] := by
  induction gs with
  | nil => rfl
  | cons y ys ih =>
    simp only [List.foldl_cons]
    have : addMeaning [(c, φ)] y = [(c, φ)] := by
      unfold addMeaning
      cases hm : y.2.meaning? with
      | none => rfl
      | some ψ =>
        have := h y (by simp) ψ hm
        subst this
        simp
    rw [this]
    exact ih (fun z hz => h z (by simp [hz]))

theorem firstMeanings_eq_single (gs : List (Candidate × Got)) (c : Candidate) (φ : EFormula)
    (hc : ∀ y ∈ gs, y.1 = c → y.2 = .one φ)
    (hall : ∀ y ∈ gs, ∀ ψ, y.2.meaning? = some ψ → ψ = φ)
    (hpre : ∀ y ∈ gs.takeWhile (fun y => y.1 != c), y.2.meaning? = none)
    (hmem : ∃ y ∈ gs, y.1 = c) :
    firstMeanings gs = [(c, φ)] := by
  unfold firstMeanings
  induction gs with
  | nil => obtain ⟨_, hy, _⟩ := hmem; cases hy
  | cons y ys ih =>
    simp only [List.foldl_cons]
    by_cases hy : y.1 = c
    · have hone := hc y (by simp) hy
      have : addMeaning [] y = [(c, φ)] := by simp [addMeaning, hone, Got.meaning?, hy]
      rw [this]
      exact fold_meanings_fixed ys c φ (fun z hz => hall z (by simp [hz]))
    · have hne : (y.1 != c) = true := by simpa using hy
      have hnone : y.2.meaning? = none := hpre y (by simp only [List.takeWhile_cons, hne, if_true]; simp)
      have : addMeaning [] y = [] := by simp [addMeaning, hnone]
      rw [this]
      apply ih
      · exact fun z hz => hc z (by simp [hz])
      · exact fun z hz => hall z (by simp [hz])
      · intro z hz
        apply hpre
        simp only [List.takeWhile_cons, hne, if_true]
        exact List.mem_cons_of_mem _ hz
      · obtain ⟨z, hz, hzc⟩ := hmem
        rcases List.mem_cons.mp hz with rfl | hz
        · exact absurd hzc hy
        · exact ⟨z, hz, hzc⟩

theorem mem_takeWhile_map (cs : List Candidate) (f : Candidate → Got) (c d : Candidate)
    (hd : d ∈ cs.takeWhile (fun d => d != c)) :
    (d, f d) ∈ (cs.map fun x => (x, f x)).takeWhile (fun y => y.1 != c) := by
  induction cs with
  | nil => cases hd
  | cons x xs ih =>
    simp only [List.map_cons, List.takeWhile_cons] at hd ⊢
    by_cases hx : (x != c) = true
    · simp only [hx, if_true] at hd ⊢
      rcases List.mem_cons.mp hd with rfl | hd
      · simp
      · exact List.mem_cons_of_mem _ (ih hd)
    · simp only [hx, Bool.false_eq_true, if_false] at hd
      cases hd

theorem mem_takeWhile_map_inv (cs : List Candidate) (f : Candidate → Got) (c : Candidate)
    (y : Candidate × Got) (hy : y ∈ (cs.map fun x => (x, f x)).takeWhile (fun y => y.1 != c)) :
    y.1 ∈ cs.takeWhile (fun d => d != c) ∧ y.2 = f y.1 := by
  induction cs with
  | nil => simp at hy
  | cons x xs ih =>
    simp only [List.map_cons, List.takeWhile_cons] at hy ⊢
    by_cases hx : (x != c) = true
    · simp only [hx, if_true] at hy ⊢
      rcases List.mem_cons.mp hy with rfl | hy
      · simp
      · obtain ⟨h1, h2⟩ := ih hy
        exact ⟨List.mem_cons_of_mem _ h1, h2⟩
    · simp only [hx, Bool.false_eq_true, if_false] at hy
      cases hy

theorem classify_one_spec (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String)
    (c : Candidate) (φ : EFormula) (h : classify auxs E O L b q = .one c φ) :
    grammarFault E O L = none ∧
    (∀ d ∈ candidates auxs q, (got E O L b d).isNotOne = false ∧ (got E O L b d).isBudget = false ∧
      (got E O L b d).isMany = false) ∧
    firstMeanings ((candidates auxs q).map fun d => (d, got E O L b d)) = [(c, φ)] := by
  unfold classify at h
  dsimp only at h
  split at h <;> try cases h
  rename_i hg
  repeat (split at h <;> try cases h)
  all_goals try (split at h <;> cases h)
  all_goals
    let gs := (candidates auxs q).map fun d => (d, got E O L b d)
    have hn : gs.any (fun x => x.snd.isNotOne) = false := by simp only [Bool.not_eq_true] at *; assumption
    have hb : ((candidates auxs q).map fun d => (d, got E O L b d)).find? (fun x => x.snd.isBudget) = none := by assumption
    have hm : ((candidates auxs q).map fun d => (d, got E O L b d)).find? (fun x => x.snd.isMany) = none := by assumption
    refine ⟨hg, ?_, by assumption⟩
    intro d hd
    have hmem : (d, got E O L b d) ∈ gs := List.mem_map_of_mem hd
    exact ⟨by simpa using (List.any_eq_false.mp hn) _ hmem, by simpa using (List.find?_eq_none.mp hb) _ hmem,
      by simpa using (List.find?_eq_none.mp hm) _ hmem⟩

theorem readQuestion_classify_one (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (q : String) (c : Candidate) (φ : EFormula) (h : readQuestion auxs E O L b q = .one c φ) :
    classify auxs E O L b q = .one c φ := by
  unfold readQuestion at h
  dsimp only at h
  split at h <;> try cases h
  split at h <;> try cases h
  split at h <;> try cases h
  all_goals assumption

theorem readQuestion_one :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate) (φ : EFormula),
    readQuestion auxs E O L b q = .one c φ → L.policyOk E O = true ∧ QuestionOneReading auxs E O L q c φ := by
  intro auxs E O L b q c φ h
  obtain ⟨hg, hflags, hf⟩ := classify_one_spec auxs E O L b q c φ (readQuestion_classify_one auxs E O L b q c φ h)
  obtain ⟨hp, hv, hchk⟩ := grammarFault_none_checks hg
  have hcmem : c ∈ candidates auxs q ∧ got E O L b c = .one φ := by
    obtain ⟨y, hy, hyc, hyg⟩ := firstMeanings_sound _ (c, φ) (by rw [hf]; simp)
    obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hy
    simp only at hyc hyg
    subst hyc
    exact ⟨hd, hyg⟩
  have hsame : ∀ d ∈ candidates auxs q, ∀ ψ, got E O L b d = .one ψ → ψ = φ := by
    intro d hd ψ hψ
    obtain ⟨x, hx, hxψ⟩ := fold_meanings_complete _ [] (d, got E O L b d) ψ
      (List.mem_map_of_mem (f := fun d => (d, got E O L b d)) hd)
      (by simp [hψ, Got.meaning?])
    change x ∈ firstMeanings _ at hx
    rw [hf] at hx
    simp at hx
    subst hx
    exact hxψ.symm
  have hread : ∀ d ∈ candidates auxs q, ∀ ψ, EnglishOneReading E O L d.sentence [(ψ, false)] →
      got E O L b d = .one ψ := fun d hd ψ hr =>
    got_of_reading hv hchk (hflags d hd).1 (hflags d hd).2.1 hr
  refine ⟨hp, hcmem.1, fun d hd => got_atMostOne hv hchk (hflags d hd).1 (hflags d hd).2.1 (hflags d hd).2.2,
    got_one_reading hcmem.2, ?_, ?_⟩
  · intro d hd ⟨ψ, hr⟩
    have hdm : d ∈ candidates auxs q := (List.takeWhile_sublist _).subset hd
    have hone := hread d hdm ψ hr
    have hnone := firstMeanings_takeWhile _ c φ [] hf (d, got E O L b d)
      (mem_takeWhile_map _ (got E O L b) c d hd)
    simp [hone, Got.meaning?] at hnone
  · intro d hd
    by_cases hr : HasReading E O L d.sentence
    · obtain ⟨ψ, hψ⟩ := hr
      have hone := hread d hd ψ hψ
      have := hsame d hd ψ hone
      subst this
      exact Or.inl hψ
    · exact Or.inr hr

theorem got_flags_of_lex {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {d : Candidate} {w : Array Tok}
    (hv : L.valid E O = true) (hg : GrammarChecks E L) (hl : lex d.sentence = .ok #[w])
    (hamo : AtMostOneDerivation E L d.sentence) (hb : ∀ i, read E O L b d.sentence ≠ .stopped i .budget) :
    (got E O L b d).isNotOne = false ∧ (got E O L b d).isBudget = false ∧ (got E O L b d).isMany = false := by
  have hs := got_single (b := b) hv hg hl
  have hr := read_single (b := b) hv hg hl
  obtain ⟨w', hl', huniq⟩ := hamo
  rw [hl] at hl'
  cases hl'
  cases hrs : VE.Grammar.readSentence (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b w with
  | mk o st1 =>
    rw [hrs] at hs hr
    cases o with
    | ok A m =>
      rw [hs]
      by_cases ht : typedDocument E [A] = true
      · cases m <;> simp [ht, Got.isNotOne, Got.isBudget, Got.isMany]
      · simp [ht, Got.isNotOne, Got.isBudget, Got.isMany]
    | noDerivation => rw [hs]; simp [Got.isNotOne, Got.isBudget, Got.isMany]
    | ambiguous t u =>
      obtain ⟨_, h1, h2, hne⟩ := VE.Grammar.read_ambiguous hrs
      exact absurd (huniq t u h1 h2) hne
    | rejected r => rw [hs]; simp [Got.isNotOne, Got.isBudget, Got.isMany]
    | budget => exact absurd hr (hb 0)

theorem candidates_body (auxs : List String) (q : String) (c : Candidate) (hc : c ∈ candidates auxs q) :
    ∃ t toks, (shape auxs q).body = some t ∧ bodySentence t = some toks := by
  unfold candidates at hc
  split at hc
  · rename_i t hsh
    split at hc
    · rename_i hb
      obtain ⟨toks, htoks⟩ := Option.isSome_iff_exists.mp hb
      exact ⟨t, toks, by simp [hsh, Shape.body], htoks⟩
    · cases hc
  · rename_i a r hsh
    cases hbs : bodySentence r with
    | none =>
      have : gaps r = [] := by simp [gaps, hbs]
      simp [this] at hc
    | some toks => exact ⟨r, toks, by simp [hsh, Shape.body], hbs⟩
  · cases hc

theorem readQuestion_complete :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate) (φ : EFormula),
    L.policyOk E O = true → GrammarChecks E L → withinLimits auxs q = true →
    (∀ d ∈ candidates auxs q, ∀ i, read E O L b d.sentence ≠ .stopped i .budget) →
    QuestionOneReading auxs E O L q c φ → readQuestion auxs E O L b q = .one c φ := by
  intro auxs E O L b q c φ hp hchk hlim hbud ⟨hc, hamo, hcr, hpre, hpost⟩
  have hv : L.valid E O = true := hcr.1
  have hflags : ∀ d ∈ candidates auxs q, (got E O L b d).isNotOne = false ∧ (got E O L b d).isBudget = false ∧
      (got E O L b d).isMany = false := by
    intro d hd
    obtain ⟨w, hl, _⟩ := hamo d hd
    exact got_flags_of_lex hv hchk hl (hamo d hd) (hbud d hd)
  have hgc : got E O L b c = .one φ := got_of_reading hv hchk (hflags c hc).1 (hflags c hc).2.1 hcr
  have hfm : firstMeanings ((candidates auxs q).map fun d => (d, got E O L b d)) = [(c, φ)] := by
    apply firstMeanings_eq_single
    · intro y hy hyc
      obtain ⟨d, _, rfl⟩ := List.mem_map.mp hy
      simp only at hyc ⊢
      subst hyc
      exact hgc
    · intro y hy ψ hψ
      obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hy
      have hone : got E O L b d = .one ψ := by
        cases hg : got E O L b d <;> simp [hg, Got.meaning?] at hψ
        subst hψ; rfl
      have hr := got_one_reading hone
      rcases hpost d hd with h | h
      · have := english_reading_unique E O L d.sentence _ _ h hr
        simp at this
        exact this
      · exact absurd ⟨ψ, hr⟩ h
    · intro y hy
      obtain ⟨hy1, hy2⟩ := mem_takeWhile_map_inv _ (got E O L b) c y hy
      cases hm : y.2.meaning? with
      | none => rfl
      | some ψ =>
        have hone : got E O L b y.1 = .one ψ := by
          rw [← hy2]
          cases hg : y.2 <;> simp [hg, Got.meaning?] at hm
          subst hm; rfl
        exact absurd ⟨ψ, got_one_reading hone⟩ (hpre y.1 hy1)
    · exact ⟨(c, got E O L b c), List.mem_map_of_mem (f := fun d => (d, got E O L b d)) hc, rfl⟩
  have hgf := grammarFault_eq_none hp hv hchk
  obtain ⟨t, toks, hbody, hbs⟩ := candidates_body auxs q c hc
  have hlex : lexSpans (t ++ ".") = .ok #[toks] := by
    unfold bodySentence at hbs
    split at hbs
    · rename_i ss hss
      by_cases h1 : ss.size = 1
      · simp only [h1, beq_self_eq_true, if_true] at hbs
        obtain ⟨x, rfl⟩ := Array.size_eq_one_iff.mp h1
        simp at hbs
        subst hbs
        exact hss
      · simp [h1] at hbs
    · cases hbs
  simp only [withinLimits, hbody, hbs, Bool.and_eq_true, decide_eq_true_eq] at hlim
  obtain ⟨⟨hqs, hts⟩, hcs⟩ := hlim
  have hn : ((candidates auxs q).map fun d => (d, got E O L b d)).any (fun x => x.snd.isNotOne) = false :=
    List.any_eq_false.mpr fun y hy => by
      obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hy
      simp [(hflags d hd).1]
  have hb : ((candidates auxs q).map fun d => (d, got E O L b d)).find? (fun x => x.snd.isBudget) = none :=
    List.find?_eq_none.mpr fun y hy => by
      obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hy
      simp [(hflags d hd).2.1]
  have hm : ((candidates auxs q).map fun d => (d, got E O L b d)).find? (fun x => x.snd.isMany) = none :=
    List.find?_eq_none.mpr fun y hy => by
      obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hy
      simp [(hflags d hd).2.2]
  have hcl : classify auxs E O L b q = .one c φ := by
    unfold classify
    rw [hgf]
    dsimp only
    cases hsh : shape auxs q with
    | notQuestion => simp [hsh, Shape.body] at hbody
    | other w => simp [hsh, Shape.body] at hbody
    | caseThat t' =>
      simp only [hsh, Shape.body, Option.some.injEq] at hbody
      subst hbody
      simp only [Shape.body, Option.getD_some, hlex]
      rw [if_neg (by omega), if_neg (by simp), if_neg (by simp; omega), if_neg (by omega), if_neg (by simp [hn]),
        hb]
      simp only [hm, hfm]
    | fronted a r =>
      simp only [hsh, Shape.body, Option.some.injEq] at hbody
      subst hbody
      simp only [Shape.body, Option.getD_some, hlex]
      rw [if_neg (by omega), if_neg (by simp), if_neg (by simp; omega), if_neg (by omega), if_neg (by simp [hn]),
        hb]
      simp only [hm, hfm]
  simp [readQuestion, hcl]

end VE.Question
