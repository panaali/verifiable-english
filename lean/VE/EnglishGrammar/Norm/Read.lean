import VE.EnglishGrammar.Norm.Rules

/-! The reader of authored W1 rule blocks (docs/spec/english-lean-s6.md 2.6): `read`'s checks on the norm grammar,
then `lex`, then `readDocument` from `NState.init`, then `assemble`. Each sentence has exactly one derivation and
its piece is computed from it once; the pieces are assembled into statements. -/

namespace VE.EnglishGrammar.Norm
open VE.Grammar VE.EnglishGrammar

inductive NormOutcome where
  | ok (rs : List NormStatement)
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | stopped (index : Nat) (o : VE.Grammar.Outcome Tok Reject Piece)
  | misplaced (f : BlockFault)

/-- `readNorm`'s steps on the grammar `G` it built and the text's sentences with their byte positions (`lexSpans`;
`lex` is them with the positions erased): `read`'s checks, then `readDocument` from `NState.init`, then `assemble`.
The statement mode builds `G` and lexes once and reads both again (the evaluator rule of 2026-10-27). -/
def readNormOn (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (G : VE.Grammar.Grammar Terminal)
    (lexed : Except Reject (Array (Array Spanned))) : NormOutcome :=
  let A := normActs E L
  if !L.valid E O then .invalidGrammar .lexicon
  else if !(G.wf && terminatorFree G) then .invalidGrammar .notWellFormed
  else if !(G.typed sig (normTy E L) A && decide (normTy E L G.start = .norm)) then .invalidGrammar .notTyped
  else match lexed with
    | .error r => .lexical r
    | .ok sents =>
      match readDocument G (normMeaning G A) NState.init b (sents.map fun sent => sent.map (·.1)).toList with
      | (.ok ps, _) =>
        match assemble (ps.map (·.1)) with
        | .ok rs => .ok rs
        | .error f => .misplaced f
      | (.stopped i o, _) => .stopped i o

/-- `read`'s checks, on the norm grammar, in `read`'s order. The start type is `.norm`. Then `lex`, then
`readDocument` from `NState.init`, then `assemble`. -/
def readNorm (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : NormOutcome :=
  readNormOn E O L b (normGrammar E L) (lexSpans s)

/-- `readNorm` is `readNormOn` on the grammar it builds and the sentences `lexSpans` gives. -/
theorem readNorm_on (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) :
    readNorm E O L b s = readNormOn E O L b (normGrammar E L) (lexSpans s) := rfl

def NormOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List NormStatement) : Prop :=
  L.valid E O = true ∧
  ∃ sents ps st2, lex s = .ok sents ∧
    VE.Grammar.DocOneReading (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init
      (sents.toList.map (·.toList)) (ps.map (·, false)) st2 ∧
    assemble ps = .ok rs

/-! ## The reading statements of spec section 4 -/

/-- The checks of `readNorm`, as one hypothesis. -/
theorem readNorm_checks {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String} {o : NormOutcome}
    (h : readNorm E O L b s = o) (hv : ∀ g, o ≠ .invalidGrammar g) :
    L.valid E O = true ∧ (normGrammar E L).wf = true ∧ terminatorFree (normGrammar E L) = true ∧
      (normGrammar E L).typed sig (normTy E L) (normActs E L) = true ∧
      normTy E L (normGrammar E L).start = .norm := by
  unfold readNorm readNormOn at h
  by_cases h1 : L.valid E O = true
  · by_cases h2 : ((normGrammar E L).wf && terminatorFree (normGrammar E L)) = true
    · by_cases h3 : ((normGrammar E L).typed sig (normTy E L) (normActs E L) &&
          decide (normTy E L (normGrammar E L).start = .norm)) = true
      · simp only [Bool.and_eq_true, decide_eq_true_eq] at h2 h3
        exact ⟨h1, h2.1, h2.2, h3.1, h3.2⟩
      · simp only [h1, h2, h3, Bool.not_true, Bool.not_false, if_true] at h
        exact absurd h.symm (hv _)
    · simp only [h1, h2, Bool.not_true, Bool.not_false, if_true] at h
      exact absurd h.symm (hv _)
  · simp only [h1, Bool.not_false, if_true] at h
    exact absurd h.symm (hv _)

/-- `readNorm` after its checks. -/
theorem readNorm_eq {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String} (h1 : L.valid E O = true)
    (h2 : (normGrammar E L).wf = true) (h3 : terminatorFree (normGrammar E L) = true)
    (h4 : (normGrammar E L).typed sig (normTy E L) (normActs E L) = true)
    (h5 : normTy E L (normGrammar E L).start = .norm) :
    readNorm E O L b s = match lex s with
      | .error r => .lexical r
      | .ok sents =>
        match readDocument (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init b
            sents.toList with
        | (.ok ps, _) =>
          match assemble (ps.map (·.1)) with
          | .ok rs => .ok rs
          | .error f => .misplaced f
        | (.stopped i o, _) => .stopped i o := by
  unfold readNorm readNormOn lex
  simp only [h1, h2, h3, h4, h5, Bool.not_true, Bool.and_self, decide_true, Bool.false_eq_true, if_false]
  cases lexSpans s <;> rfl

/-- A document of norm sentences carries no mark. -/
theorem doc_unmarked {E : Env} {L : Lexicon} : ∀ {st st2 : NState} {ws : List (List Tok)} {ps : List (Piece × Bool)},
    DocOneReading (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) st ws ps st2 →
    ps = (ps.map (·.1)).map (·, false)
  | _, _, [], [], _ => rfl
  | _, _, _ :: _, (p, c) :: ps, ⟨_, ⟨_, _, _, hm⟩, hd⟩ => by
    simp only [List.map_cons, normMeaning_unmarked E L _ _ _ _ _ hm, ← doc_unmarked hd]
  | _, _, [], _ :: _, h => h.elim
  | _, _, _ :: _, [], h => h.elim

theorem readNorm_sound : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List NormStatement),
  readNorm E O L b s = .ok rs → NormOneReading E O L s rs := by
  intro E O L b s rs h
  obtain ⟨h1, h2, h3, h4, h5⟩ := readNorm_checks h (fun _ e => by cases e)
  rw [readNorm_eq h1 h2 h3 h4 h5] at h
  split at h
  · cases h
  · rename_i sents hl
    split at h
    · rename_i ps st2 hd
      split at h
      · rename_i ha
        cases h
        have hdoc := doc_sound h2 hd
        exact ⟨h1, sents, ps.map (·.1), st2, hl, doc_unmarked hdoc ▸ hdoc, ha⟩
      · cases h
    · cases h

theorem readNorm_complete : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  NormOneReading E O L s rs →
  (normGrammar E L).wf = true → terminatorFree (normGrammar E L) = true →
  (normGrammar E L).typed sig (normTy E L) (normActs E L) = true → normTy E L (normGrammar E L).start = .norm →
  readNorm E O L b s = .ok rs ∨ ∃ i, readNorm E O L b s = .stopped i .budget := by
  intro E O L b s rs ⟨h1, sents, ps, st2, hl, hd, ha⟩ h2 h3 h4 h5
  rw [readNorm_eq h1 h2 h3 h4 h5, hl]
  rcases doc_complete (b := b) h2 hd with hr | ⟨i, st1, hr⟩
  · left
    simp only [hr, List.map_map, Function.comp_def, List.map_id', ha]
  · right
    exact ⟨i, by simp only [hr]⟩

theorem readNorm_unique : ∀ (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs rs2 : List NormStatement),
  NormOneReading E O L s rs → NormOneReading E O L s rs2 → rs2 = rs := by
  intro E O L s rs rs2 ⟨_, sents, ps, st2, hl, hd, ha⟩ ⟨_, sents2, ps2, st3, hl2, hd2, ha2⟩
  rw [hl] at hl2
  cases hl2
  have hp := congrArg (List.map (·.1)) (doc_unique hd hd2).1
  simp only [List.map_map, Function.comp_def, List.map_id'] at hp
  rw [hp, ha] at ha2
  exact (Except.ok.inj ha2).symm

theorem readNorm_numbered : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  rs.filterMap NormStatement.number? = List.range' 1 (ruleCount rs) ∧
  ∀ n ∈ rs.flatMap NormStatement.refs, 1 ≤ n ∧ n ≤ ruleCount rs := by
  intro E O L b s rs h
  obtain ⟨_, _, _, _, _, _, ha⟩ := readNorm_sound E O L b s rs h
  exact assemble_numbered _ rs ha

end VE.EnglishGrammar.Norm
