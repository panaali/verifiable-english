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
