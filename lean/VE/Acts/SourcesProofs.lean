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

end VE.Acts
