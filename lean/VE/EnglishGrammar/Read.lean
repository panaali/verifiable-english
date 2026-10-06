import VE.EnglishGrammar.Encode
import VE.Grammar.Reading

/-! The English readers and their statements (docs/spec/english-lean-s2.md 5.3, 5.5 and 5.6).

`read` checks the lexicon, the grammar's well-formedness and terminator-freedom, its typing and its
start type, then lexes the source, reads its sentences in order with the generic reader, and checks
the document's formulas against the environment. `translate` reads one sentence from the initial state
and returns its set of results, complete exactly when the parser returned fewer trees than the cap.
-/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The meaning of a tree: its sentence value applied to the state. -/
def meaning (G : Grammar Terminal) (acts : Array (Action sig)) : Meaning Tok DState Reject EFormula :=
  fun st t => match t.sem G sig acts with
    | some ⟨.sentence, f⟩ => f st
    | _ => .error .internal

inductive GrammarFault where
  | lexicon | notWellFormed | notTyped
  deriving DecidableEq, Repr

inductive ReadOutcome where
  | ok (rs : List (EFormula × Bool))
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | stopped (index : Nat) (o : Outcome Tok Reject EFormula)
  | illTyped

def read (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : ReadOutcome :=
  if !L.valid E O then .invalidGrammar .lexicon
  else if !((grammar E L).wf && terminatorFree (grammar E L)) then .invalidGrammar .notWellFormed
  else if !((grammar E L).typed sig (ty E L) (acts E L) && decide (ty E L (grammar E L).start = .sentence)) then
    .invalidGrammar .notTyped
  else match lex s with
    | .error r => .lexical r
    | .ok sents =>
        match readDocument (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b sents.toList with
        | (.ok rs, _) => if typedDocument E (rs.map (·.1)) then .ok rs else .illTyped
        | (.stopped i o, _) => .stopped i o

def EnglishOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List (EFormula × Bool)) : Prop :=
  L.valid E O = true ∧
  ∃ sents st2, lex s = .ok sents ∧
    DocOneReading (grammar E L) (meaning (grammar E L) (acts E L)) DState.init
      (sents.toList.map (·.toList)) rs st2 ∧
    typedDocument E (rs.map (·.1)) = true

def checkRendering (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool)) (s : String) :
    Bool :=
  match read E O L b s with
  | .ok rs2 => decide (rs2 = rs)
  | _ => false

inductive TranslateOutcome where
  | readings (rs : List (EFormula × Bool × DState)) (complete : Bool)
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | notOneSentence
  | budget

def translate (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String) : TranslateOutcome :=
  if !L.valid E O then .invalidGrammar .lexicon
  else if !((grammar E L).wf && terminatorFree (grammar E L)) then .invalidGrammar .notWellFormed
  else if !((grammar E L).typed sig (ty E L) (acts E L) && decide (ty E L (grammar E L).start = .sentence)) then
    .invalidGrammar .notTyped
  else match lex s with
    | .error r => .lexical r
    | .ok sents =>
      match sents.toList with
      | [w] =>
        match parse (grammar E L) cap b w with
        | none => .budget
        | some ts => .readings (readingSet (meaning (grammar E L) (acts E L)) DState.init ts) (decide (ts.length < cap))
      | _ => .notOneSentence

/-! ## The statements of spec 5.6 -/

/-- The three checks of `read`, as one hypothesis. -/
theorem read_checks {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String} {o : ReadOutcome}
    (h : read E O L b s = o) (hv : ∀ g, o ≠ .invalidGrammar g) :
    L.valid E O = true ∧ (grammar E L).wf = true ∧ terminatorFree (grammar E L) = true ∧
      (grammar E L).typed sig (ty E L) (acts E L) = true ∧ ty E L (grammar E L).start = .sentence := by
  unfold read at h
  by_cases h1 : L.valid E O = true
  · by_cases h2 : ((grammar E L).wf && terminatorFree (grammar E L)) = true
    · by_cases h3 : ((grammar E L).typed sig (ty E L) (acts E L) &&
          decide (ty E L (grammar E L).start = .sentence)) = true
      · simp only [Bool.and_eq_true, decide_eq_true_eq] at h2 h3
        exact ⟨h1, h2.1, h2.2, h3.1, h3.2⟩
      · simp only [h1, h2, h3, Bool.not_true, Bool.not_false, if_true] at h
        exact absurd h.symm (hv _)
    · simp only [h1, h2, Bool.not_true, Bool.not_false, if_true] at h
      exact absurd h.symm (hv _)
  · simp only [h1, Bool.not_false, if_true] at h
    exact absurd h.symm (hv _)

/-- `read` after its three checks. -/
theorem read_eq {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String}
    (h1 : L.valid E O = true) (h2 : (grammar E L).wf = true) (h3 : terminatorFree (grammar E L) = true)
    (h4 : (grammar E L).typed sig (ty E L) (acts E L) = true) (h5 : ty E L (grammar E L).start = .sentence) :
    read E O L b s = match lex s with
      | .error r => .lexical r
      | .ok sents =>
          match readDocument (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b sents.toList with
          | (.ok rs, _) => if typedDocument E (rs.map (·.1)) then .ok rs else .illTyped
          | (.stopped i o, _) => .stopped i o := by
  unfold read
  simp [h1, h2, h3, h4, h5]

theorem read_ok : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List (EFormula × Bool)),
    read E O L b s = .ok rs → EnglishOneReading E O L s rs := by
  intro E O L b s rs h
  obtain ⟨h1, h2, h3, h4, h5⟩ := read_checks h (fun _ e => by cases e)
  rw [read_eq h1 h2 h3 h4 h5] at h
  split at h
  · cases h
  · rename_i sents hl
    split at h
    · rename_i rs2 st2 hd
      split at h
      · rename_i ht
        cases h
        exact ⟨h1, sents, st2, hl, doc_sound h2 hd, ht⟩
      · cases h
    · cases h

theorem read_complete_english : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List (EFormula × Bool)),
    EnglishOneReading E O L s rs →
    (grammar E L).wf = true → terminatorFree (grammar E L) = true →
    (grammar E L).typed sig (ty E L) (acts E L) = true → ty E L (grammar E L).start = .sentence →
    read E O L b s = .ok rs ∨ ∃ i, read E O L b s = .stopped i .budget := by
  intro E O L b s rs ⟨h1, sents, st2, hl, hd, ht⟩ h2 h3 h4 h5
  rw [read_eq h1 h2 h3 h4 h5, hl]
  rcases doc_complete (b := b) h2 hd with hr | ⟨i, st1, hr⟩
  · left
    simp only [hr, ht, if_true]
  · right
    exact ⟨i, by simp only [hr]⟩

theorem read_stopped : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (i : Nat)
    (o : Outcome Tok Reject EFormula),
    read E O L b s = .stopped i o →
    L.valid E O = true ∧ (grammar E L).wf = true ∧ terminatorFree (grammar E L) = true ∧
    (grammar E L).typed sig (ty E L) (acts E L) = true ∧ ty E L (grammar E L).start = .sentence ∧
    ∃ sents rs st1 w, lex s = .ok sents ∧
      DocOneReading (grammar E L) (meaning (grammar E L) (acts E L)) DState.init
        ((sents.toList.take i).map (·.toList)) rs st1 ∧
      sents.toList[i]? = some w ∧
      (readSentence (grammar E L) (meaning (grammar E L) (acts E L)) st1 b w).1 = o ∧ ∀ A c, o ≠ .ok A c := by
  intro E O L b s i o h
  obtain ⟨h1, h2, h3, h4, h5⟩ := read_checks h (fun _ e => by cases e)
  refine ⟨h1, h2, h3, h4, h5, ?_⟩
  rw [read_eq h1 h2 h3 h4 h5] at h
  split at h
  · cases h
  · rename_i sents hl
    split at h
    · split at h <;> cases h
    · rename_i i2 o2 st1 hd
      cases h
      obtain ⟨rs, w, hdoc, hw, ho, hne⟩ := doc_stopped h2 hd
      exact ⟨sents, rs, st1, w, hl, hdoc, hw, ho, hne⟩

theorem english_reading_unique : ∀ (E : Env) (O : Overlay) (L : Lexicon) (s : String)
    (rs rs2 : List (EFormula × Bool)),
    EnglishOneReading E O L s rs → EnglishOneReading E O L s rs2 → rs2 = rs := by
  intro E O L s rs rs2 ⟨_, sents, st2, hl, hd, _⟩ ⟨_, sents2, st3, hl2, hd2, _⟩
  rw [hl] at hl2
  cases hl2
  exact (doc_unique hd hd2).1

theorem meaning_total : ∀ (G : Grammar Terminal) (acts : Array (Action sig)) (ty : Nat → Ty)
    (st : DState) (w : List Tok) (t : Tree Tok),
    G.typed sig ty acts = true → ty G.start = .sentence → Derives G (.n G.start) w t →
    ∃ f, t.sem G sig acts = some ⟨.sentence, f⟩ ∧ meaning G acts st t = f st := by
  intro G acts ty st w t hT hs hd
  obtain ⟨v, hv⟩ := sem_total (S := sig) (ty := ty) hT hd.1
  simp only [symTy] at v hv
  revert v
  rw [hs]
  intro v hv
  exact ⟨v, hv, by simp [meaning, hv]⟩

theorem checked_rendering_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (rs : List (EFormula × Bool)) (s : String),
    checkRendering E O L b rs s = true ↔ read E O L b s = .ok rs := by
  intro E O L b rs s
  unfold checkRendering
  split
  · rename_i rs2 h
    rw [h]
    simp only [decide_eq_true_eq, ReadOutcome.ok.injEq]
  · rename_i h
    constructor
    · intro e; cases e
    · intro e; exact absurd e (h rs)

theorem checked_rendering : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (rs : List (EFormula × Bool)) (s : String),
    checkRendering E O L b rs s = true → EnglishOneReading E O L s rs :=
  fun E O L b rs s h => read_ok E O L b s rs ((checked_rendering_exact E O L b rs s).mp h)

/-- `translate` after its three checks. -/
theorem translate_eq {E : Env} {O : Overlay} {L : Lexicon} {cap b : Nat} {s : String}
    (h1 : L.valid E O = true) (h2 : (grammar E L).wf = true) (h3 : terminatorFree (grammar E L) = true)
    (h4 : (grammar E L).typed sig (ty E L) (acts E L) = true) (h5 : ty E L (grammar E L).start = .sentence) :
    translate E O L cap b s = match lex s with
      | .error r => .lexical r
      | .ok sents =>
        match sents.toList with
        | [w] =>
          match parse (grammar E L) cap b w with
          | none => .budget
          | some ts => .readings (readingSet (meaning (grammar E L) (acts E L)) DState.init ts)
              (decide (ts.length < cap))
        | _ => .notOneSentence := by
  unfold translate
  simp [h1, h2, h3, h4, h5]

/-- The three checks of `translate`, as one hypothesis. -/
theorem translate_checks {E : Env} {O : Overlay} {L : Lexicon} {cap b : Nat} {s : String} {o : TranslateOutcome}
    (h : translate E O L cap b s = o) (hv : ∀ g, o ≠ .invalidGrammar g) :
    L.valid E O = true ∧ (grammar E L).wf = true ∧ terminatorFree (grammar E L) = true ∧
      (grammar E L).typed sig (ty E L) (acts E L) = true ∧ ty E L (grammar E L).start = .sentence := by
  unfold translate at h
  by_cases h1 : L.valid E O = true
  · by_cases h2 : ((grammar E L).wf && terminatorFree (grammar E L)) = true
    · by_cases h3 : ((grammar E L).typed sig (ty E L) (acts E L) &&
          decide (ty E L (grammar E L).start = .sentence)) = true
      · simp only [Bool.and_eq_true, decide_eq_true_eq] at h2 h3
        exact ⟨h1, h2.1, h2.2, h3.1, h3.2⟩
      · simp only [h1, h2, h3, Bool.not_true, Bool.not_false, if_true] at h
        exact absurd h.symm (hv _)
    · simp only [h1, h2, Bool.not_true, Bool.not_false, if_true] at h
      exact absurd h.symm (hv _)
  · simp only [h1, Bool.not_false, if_true] at h
    exact absurd h.symm (hv _)

theorem translate_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String)
    (rs : List (EFormula × Bool × DState)) (x : EFormula × Bool × DState),
    translate E O L cap b s = .readings rs true →
    ∃ w, lex s = .ok #[w] ∧
      (x ∈ rs ↔ ∃ t, Derives (grammar E L) (.n (grammar E L).start) w.toList t ∧
        meaning (grammar E L) (acts E L) DState.init t = .ok x) := by
  intro E O L cap b s rs x h
  obtain ⟨h1, h2, h3, h4, h5⟩ := translate_checks h (fun _ e => by cases e)
  rw [translate_eq h1 h2 h3 h4 h5] at h
  split at h
  · cases h
  · rename_i sents hl
    split at h
    · rename_i w hw
      split at h
      · cases h
      · rename_i ts hp
        simp only [TranslateOutcome.readings.injEq, decide_eq_true_eq] at h
        obtain ⟨rfl, hlt⟩ := h
        refine ⟨w, ?_, readings_exact h2 hp hlt⟩
        have hs : sents = #[w] := Array.ext' hw
        rw [hl, hs]
    · cases h

theorem translate_one_sentence : ∀ (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String)
    (sents : Array (Array Tok)),
    lex s = .ok sents → sents.size ≠ 1 → L.valid E O = true →
    (grammar E L).wf = true → terminatorFree (grammar E L) = true →
    (grammar E L).typed sig (ty E L) (acts E L) = true → ty E L (grammar E L).start = .sentence →
    translate E O L cap b s = .notOneSentence := by
  intro E O L cap b s sents hl hn h1 h2 h3 h4 h5
  rw [translate_eq h1 h2 h3 h4 h5, hl]
  simp only
  split
  · rename_i w hw
    exact absurd (by rw [← Array.length_toList, hw]; rfl) hn
  · rfl

end VE.EnglishGrammar
