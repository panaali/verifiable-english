import VE.Acts.Sources

/-! `sourceCheck` read from its parts, and why spec 7's `sourceCheck_complete` needs the choice bound
(docs/spec/act-phrases.md 7; DRI 2026-11-02 triage item 8c).

`sourceCheck_eq` unfolds `sourceCheck` once its lexing, op, readings and paraphrases are known: the choice limit, then
D-29's comparison on `choiceViews`. `sourceExact_of_compare` is `sourceCheck_exact`'s argument on those parts. With
them, `sourceCheck_complete_needs_bound` is the counterexample item 8c asks for: `SourceExact` reads `choiceViews`,
which projects `VE.Readings.choices`' cut list, so a document with more than `maxChoices` choices whose cut part is
exact satisfies `SourceExact` while `sourceCheck` refuses it with `ResourceLimit`. ReadingsExamples checks the
theorem's decidable premises on S4 beside six sets of two (128 choices, cut at 65).
-/

namespace VE.Acts

/-- `sourceCheck` once the phrase's lexing, op, readings and paraphrases are known. -/
theorem sourceCheck_eq {D unspec V fx N b s ts op Rs ps} (hl : Lexical.lex fx s.phrase = .ok ts)
    (ho : opOfSource s = some op) (hR : phraseReadings V op N b ts.toArray = .ok Rs)
    (hp : paraphrases fx op s.form "the source phrase" Rs = .ok ps) :
    sourceCheck D unspec V fx N b s =
      if VE.Readings.maxChoices < (VE.Readings.choices D).length then
        .error (s!"ResourceLimit: the document has more than {VE.Readings.maxChoices} choices, too many to " ++
          "compare with the source phrase's readings")
      else compareViews ps (choiceViews D unspec s) (readingViews fx s Rs) := by
  unfold sourceCheck
  rw [hl, ho]
  simp only [hR, hp]
  rfl

/-- `SourceExact` from its parts: D-29's comparison passing on `choiceViews`, whatever the number of choices. -/
theorem sourceExact_of_compare {D unspec V fx N b s ts op Rs ps} (h : framesOk V = true)
    (hl : Lexical.lex fx s.phrase = .ok ts) (ho : opOfSource s = some op) (hR : phraseReadings V op N b ts.toArray = .ok Rs)
    (hp : paraphrases fx op s.form "the source phrase" Rs = .ok ps)
    (hc : compareViews ps (choiceViews D unspec s) (readingViews fx s Rs) = .ok ()) :
    SourceExact D unspec V fx N b s := by
  obtain ⟨he, hn⟩ := paraphrases_nodup hp
  obtain ⟨hpw, σ, hσ, hf⟩ := compareViews_ok hc
  exact ⟨ts, op, Rs, hl, ho, hR, fun R => by simpa using phraseReadings_exact V h hR R, he ▸ hn, hpw, σ, hσ, hf⟩

/-- Item 8c's counterexample, mechanised: over `maxChoices` choices with an exact cut part, `SourceExact` holds and
    `sourceCheck` refuses with `ResourceLimit`. So `sourceCheck_complete` needs `(choices D).length ≤ maxChoices`. -/
theorem sourceCheck_complete_needs_bound {D unspec V fx N b s ts op Rs ps} (h : framesOk V = true)
    (hl : Lexical.lex fx s.phrase = .ok ts) (ho : opOfSource s = some op) (hR : phraseReadings V op N b ts.toArray = .ok Rs)
    (hp : paraphrases fx op s.form "the source phrase" Rs = .ok ps)
    (hc : compareViews ps (choiceViews D unspec s) (readingViews fx s Rs) = .ok ())
    (hm : VE.Readings.maxChoices < (VE.Readings.choices D).length) :
    SourceExact D unspec V fx N b s ∧
      sourceCheck D unspec V fx N b s = .error (s!"ResourceLimit: the document has more than " ++
        s!"{VE.Readings.maxChoices} choices, too many to compare with the source phrase's readings") := by
  refine ⟨sourceExact_of_compare h hl ho hR hp hc, ?_⟩
  rw [sourceCheck_eq hl ho hR hp, if_pos hm]
  rfl

/-! ### The converse (spec 7's `sourceCheck_complete`, with item 8c's bound)

When the choices are pairwise no permutation of each other, a reading is a permutation of at most one choice, so the
greedy `pick` (the first choice per reading) finds the matching `σ` itself, and D-29's checks all pass. -/

/-- Pairwise non-permutation makes a choice the only one in its permutation class. -/
theorem eq_of_perm_of_pairwise {cs : List (List (Option View))} (hpw : cs.Pairwise (fun v w => ¬ v.Perm w)) :
    ∀ {a c}, a ∈ cs → c ∈ cs → a.Perm c → a = c := by
  induction cs with
  | nil => intro a c ha; cases ha
  | cons x xs ih =>
    rw [List.pairwise_cons] at hpw
    intro a c ha hc hac
    rcases List.mem_cons.mp ha with rfl | ha' <;> rcases List.mem_cons.mp hc with rfl | hc'
    · rfl
    · exact absurd hac (hpw.1 c hc')
    · exact absurd hac.symm (hpw.1 a ha')
    · exact ih hpw.2 ha' hc' hac

theorem forall₂_mem_left {R : α → β → Prop} : ∀ {l₁ l₂}, List.Forall₂ R l₁ l₂ → ∀ {a}, a ∈ l₁ → ∃ b ∈ l₂, R a b
  | _, _, .nil, _, ha => by cases ha
  | _, _, .cons hab h, _, ha => by
    rcases List.mem_cons.mp ha with rfl | ha
    · exact ⟨_, List.mem_cons_self .., hab⟩
    · obtain ⟨b, hb, hr⟩ := forall₂_mem_left h ha
      exact ⟨b, List.mem_cons_of_mem _ hb, hr⟩

/-- On pairwise non-permutations, `pick` returns any matching drawn from the choices. -/
theorem pick_of_forall₂ {cs : List (List (Option View))} (hpw : cs.Pairwise (fun v w => ¬ v.Perm w)) :
    ∀ {σ rs}, (∀ c ∈ σ, c ∈ cs) → List.Forall₂ List.Perm σ rs → pick cs rs = some σ
  | _, _, _, .nil => rfl
  | c :: σ, r :: rs, hm, .cons hcr hf => by
    have hc : c ∈ cs := hm c (List.mem_cons_self ..)
    have hfind : cs.find? (fun c => decide (c.Perm r)) = some c := by
      cases hx : cs.find? (fun c => decide (c.Perm r)) with
      | none => exact absurd (decide_eq_true hcr) (by simpa using List.find?_eq_none.mp hx c hc)
      | some c' =>
        have hp : c'.Perm r := by simpa using List.find?_some hx
        rw [eq_of_perm_of_pairwise hpw (List.mem_of_find?_eq_some hx) hc (hp.trans hcr.symm)]
    simp only [pick, hfind, pick_of_forall₂ hpw (fun c h => hm c (List.mem_cons_of_mem _ h)) hf]

/-- D-29's comparison passes on a bijection: the converse of `compareViews_ok`. -/
theorem compareViews_complete {ps : List String} {cs rs : List (List (Option View))}
    (hpw : cs.Pairwise (fun v w => ¬ v.Perm w)) {σ} (hσ : σ.Perm cs) (hf : List.Forall₂ List.Perm σ rs) :
    compareViews ps cs rs = .ok () := by
  have hall : cs.all (fun c => rs.any (fun r => decide (c.Perm r))) = true := by
    simp only [List.all_eq_true, List.any_eq_true, decide_eq_true_eq]
    exact fun c hc => forall₂_mem_left hf (hσ.mem_iff.mpr hc)
  have hpick := pick_of_forall₂ hpw (fun c h => hσ.mem_iff.mp h) hf
  simp only [compareViews, hall, Bool.not_true, Bool.false_eq_true, ↓reduceIte, decide_eq_true hpw, hpick,
    decide_eq_true hσ, Bool.not_true]

/-- Spec 7's converse of `sourceCheck_exact`, with the bound item 8c signs (`sourceCheck_complete_needs_bound` shows it
    is needed): an exact reading set over at most `maxChoices` choices passes. -/
theorem sourceCheck_complete (D unspec V fx N b s) (h : framesOk V = true)
    (hn : (VE.Readings.choices D).length ≤ VE.Readings.maxChoices)
    (he : SourceExact D unspec V fx N b s) : sourceCheck D unspec V fx N b s = .ok () := by
  have _ := h
  obtain ⟨ts, op, Rs, hl, ho, hR, -, hnd, hpw, σ, hσ, hf⟩ := he
  have hp : paraphrases fx op s.form "the source phrase" Rs = .ok (Rs.map (paraphrase fx op s.form)) :=
    (distinctTexts_ok _ _ _).mpr ⟨rfl, hnd⟩
  rw [sourceCheck_eq hl ho hR hp, if_neg (Nat.not_lt.mpr hn)]
  exact compareViews_complete hpw hσ hf

end VE.Acts
