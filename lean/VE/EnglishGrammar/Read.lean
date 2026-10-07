import VE.EnglishGrammar.Encode
import VE.EnglishGrammar.Policy
import VE.Grammar.Reading

/-! The English readers and their statements (docs/spec/english-lean-s2.md 5.3, 5.5 and 5.6).

`read` checks the lexicon, the grammar's well-formedness and terminator-freedom, its typing and its
start type, then lexes the source, reads its sentences in order with the generic reader, and checks
the document's formulas against the environment. `translate` reads one sentence from the initial state
and returns its set of results, complete exactly when the parser returned fewer trees than the cap.

S3 (docs/spec/english-lean-s3.md 2.10, 5.3): `admit` is `read` followed by the obligations of the marked
sentences, each a marked sentence with the unmarked sentences before it; a marked sentence with none is
`noPremise`. The proof of each obligation stays with the entailment operation (D10). `firstChecked` is the index
of the first rendered candidate that reads back as the given formulas and marks (D13).
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

/-! ## Admission and the check of candidates (S3 spec 5.3, 5.5) -/

def obligations (rs : List (EFormula × Bool)) : List (Nat × List Nat) :=
  (List.range rs.length).filterMap fun i =>
    match rs[i]? with
    | some (_, true) => some (i, (List.range i).filter fun j => (rs[j]?).map (·.2) == some false)
    | _ => none

inductive AdmitOutcome where
  | ok (rs : List (EFormula × Bool)) (obligations : List (Nat × List Nat))
  | noPremise (index : Nat)
  | refused (o : ReadOutcome)

def admit (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : AdmitOutcome :=
  match read E O L b s with
  | .ok rs =>
    match (obligations rs).find? (fun o => o.2.isEmpty) with
    | some (i, _) => .noPremise i
    | none => .ok rs (obligations rs)
  | o => .refused o

def firstChecked (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) : Option Nat :=
  candidates.findIdx? (checkRendering E O L b rs)

theorem obligations_exact : ∀ (rs : List (EFormula × Bool)) (i : Nat) (js : List Nat),
    (i, js) ∈ obligations rs ↔
      (∃ A, rs[i]? = some (A, true)) ∧ js = (List.range i).filter fun j => (rs[j]?).map (·.2) == some false := by
  intro rs i js
  unfold obligations
  rw [List.mem_filterMap]
  constructor
  · rintro ⟨a, _, hf⟩
    split at hf
    · rename_i A h
      cases hf
      exact ⟨⟨A, h⟩, rfl⟩
    · cases hf
  · rintro ⟨⟨A, h⟩, rfl⟩
    have hi : i < rs.length := (List.getElem?_eq_some_iff.mp h).1
    refine ⟨i, List.mem_range.mpr hi, ?_⟩
    simp only [h]

/-- The outcome of `admit` when `read` accepted the text. -/
theorem admit_of_read {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String} {rs : List (EFormula × Bool)}
    (h : read E O L b s = .ok rs) :
    admit E O L b s = match (obligations rs).find? (fun o => o.2.isEmpty) with
      | some (i, _) => .noPremise i
      | none => .ok rs (obligations rs) := by
  unfold admit
  rw [h]

/-- `admit` is `ok` only when `read` accepted the text and no obligation is without a premise. -/
theorem admit_ok_read {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String} {rs : List (EFormula × Bool)}
    {obs : List (Nat × List Nat)} (h : admit E O L b s = .ok rs obs) :
    read E O L b s = .ok rs ∧ obs = obligations rs ∧ ∀ o ∈ obs, o.2 ≠ [] := by
  unfold admit at h
  split at h
  · rename_i rs2 hr
    split at h
    · cases h
    · rename_i hn
      cases h
      refine ⟨hr, rfl, fun o ho he => ?_⟩
      exact List.find?_eq_none.mp hn o ho (List.isEmpty_iff.mpr he)
  · cases h

theorem admit_ok : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List (EFormula × Bool))
    (obs : List (Nat × List Nat)),
    admit E O L b s = .ok rs obs →
    EnglishOneReading E O L s rs ∧ obs = obligations rs ∧ ∀ o ∈ obs, o.2 ≠ [] := by
  intro E O L b s rs obs h
  obtain ⟨hr, ho, hp⟩ := admit_ok_read h
  exact ⟨read_ok E O L b s rs hr, ho, hp⟩

theorem admit_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List (EFormula × Bool)),
    (∃ obs, admit E O L b s = .ok rs obs) ↔ (read E O L b s = .ok rs ∧ ∀ o ∈ obligations rs, o.2 ≠ []) := by
  intro E O L b s rs
  constructor
  · rintro ⟨obs, h⟩
    obtain ⟨hr, rfl, hp⟩ := admit_ok_read h
    exact ⟨hr, hp⟩
  · rintro ⟨hr, hp⟩
    refine ⟨obligations rs, ?_⟩
    rw [admit_of_read hr]
    have hn : (obligations rs).find? (fun o => o.2.isEmpty) = none :=
      List.find?_eq_none.mpr fun o ho he => hp o ho (List.isEmpty_iff.mp he)
    rw [hn]

theorem admit_no_premise : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (i : Nat),
    admit E O L b s = .noPremise i →
    ∃ rs A, read E O L b s = .ok rs ∧ rs[i]? = some (A, true) ∧ ∀ j B, j < i → rs[j]? ≠ some (B, false) := by
  intro E O L b s i h
  unfold admit at h
  split at h
  · rename_i rs hr
    split at h
    · rename_i i2 js hf
      cases h
      have hm := List.mem_of_find?_eq_some hf
      have he : js = [] := List.isEmpty_iff.mp (by simpa using List.find?_some hf)
      obtain ⟨⟨A, hA⟩, hjs⟩ := (obligations_exact rs i js).mp hm
      refine ⟨rs, A, hr, hA, fun j B hj hb => ?_⟩
      have hmem : j ∈ (List.range i).filter fun j => (rs[j]?).map (·.2) == some false :=
        List.mem_filter.mpr ⟨List.mem_range.mpr hj, by simp [hb]⟩
      rw [← hjs, he] at hmem
      exact List.not_mem_nil hmem
    · cases h
  · cases h

theorem first_checked : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) (i : Nat),
    firstChecked E O L b rs candidates = some i →
    ∃ s, candidates[i]? = some s ∧ read E O L b s = .ok rs ∧
      ∀ j t, j < i → candidates[j]? = some t → read E O L b t ≠ .ok rs := by
  intro E O L b rs candidates i h
  unfold firstChecked at h
  obtain ⟨hi, hp, hbefore⟩ := List.findIdx?_eq_some_iff_getElem.mp h
  refine ⟨candidates[i], List.getElem?_eq_getElem hi, (checked_rendering_exact E O L b rs _).mp hp, ?_⟩
  intro j t hj ht hr
  obtain ⟨hjl, hjt⟩ := List.getElem?_eq_some_iff.mp ht
  apply hbefore j hj
  rw [hjt]
  exact (checked_rendering_exact E O L b rs t).mpr hr

/-! E2 request guards. The request's own lexicon is checked before the grammar reader. -/

def admitRequest (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : AdmitOutcome :=
  if L.policyOk E O then admit E O L b s else .refused (.invalidGrammar .lexicon)

def checkRequest (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) : Option Nat :=
  if L.policyOk E O then firstChecked E O L b rs candidates else none

def translateRequest (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String) : TranslateOutcome :=
  if L.policyOk E O then translate E O L cap b s else .invalidGrammar .lexicon

def grammarFault (E : Env) (O : Overlay) (L : Lexicon) : Option GrammarFault :=
  if !L.policyOk E O then some .lexicon
  else if !L.valid E O then some .lexicon
  else if !((grammar E L).wf && terminatorFree (grammar E L)) then some .notWellFormed
  else if !((grammar E L).typed sig (ty E L) (acts E L) && decide (ty E L (grammar E L).start = .sentence)) then
    some .notTyped
  else none

def lexiconFailure (E : Env) (O : Overlay) (L : Lexicon) : Option Failure :=
  (L.policyFailures E O ++ L.failures E O).head?

theorem policy_iff_no_failure : ∀ (E : Env) (O : Overlay) (L : Lexicon),
  L.policyOk E O = true ↔ L.policyFailures E O = [] := by
  intro E O L
  simp [Lexicon.policyOk, List.isEmpty_iff]

theorem policy_selection : ∀ (E : Env) (O : Overlay) (L : Lexicon), L.policyOk E O = true →
  (∀ p w, (p, w) ∈ L.wordings → (E.predicate? p).isSome →
    (policyPredicate E O p).map (·.1) = some w ∨ fallbackWording p (E.arity p) = some w) ∧
  (∀ p n, (p, n) ∈ L.negatives → (E.predicate? p).isSome →
    ∃ w, policyPredicate E O p = some (w, some n) ∧ L.wordings.lookup p = some w) ∧
  (∀ s n, (s, n) ∈ L.nouns → ∀ m, (policyNouns E O).lookup s = some m → n = m ∨ n = fallbackNoun s) ∧
  (∀ c sp, (c, sp) ∈ L.spellings → ∀ m, (policySpellings E O).lookup c = some m → sp = m ∨ sp = jsonQuote c) := by
  intro E O L hp
  simp only [Lexicon.policyOk, List.isEmpty_iff, Lexicon.policyFailures,
    List.append_eq_nil_iff, List.filterMap_eq_nil_iff, policyPredicate_tables] at hp
  rcases hp with ⟨⟨⟨hword, hneg⟩, hnoun⟩, hspell⟩
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro p w hmem hpred
    have hc : (E.predicates.map (·.name)).contains p = true := by
      rw [List.contains_iff_mem, List.mem_map]
      obtain ⟨d, hd, hname⟩ := List.find?_isSome.mp hpred
      exact ⟨d, hd, by simpa using hname⟩
    have hf := hword (p,w) hmem
    simp only [Prod.fst, Prod.snd, hc, Bool.not_true, Bool.false_eq_true, if_false] at hf
    cases hpol : policyPredicate E O p with
    | none =>
      have hs : (policyPredicate E O p).isSome = true := by
        unfold policyPredicate policyPredicateIn
        cases hp : E.predicate? p with
        | none => simp [hp] at hpred
        | some d => simp only [hp]; split <;> cases hform : List.lookup p E.forms.wordings <;> simp [hform]
      rw [hpol] at hs
      cases hs
    | some pair =>
      rcases pair with ⟨pw, pn⟩
      simp only [hpol, beq_iff_eq, Bool.or_eq_true, Option.some.injEq, Option.some.injEq, if_true, if_false] at hf
      have hsel : w = pw ∨ some w = fallbackWording p (E.arity p) := by
        by_cases hgood : w = pw ∨ some w = fallbackWording p (E.arity p)
        · exact hgood
        · simp [hgood] at hf
      rcases hsel with hleft | hright
      · left; simp [hpol, hleft]
      · right; exact hright.symm
  · intro p n hmem hpred
    have hc : (E.predicates.map (·.name)).contains p = true := by
      rw [List.contains_iff_mem, List.mem_map]
      obtain ⟨d, hd, hname⟩ := List.find?_isSome.mp hpred
      exact ⟨d, hd, by simpa using hname⟩
    have hf := hneg (p,n) hmem
    simp only [Prod.fst, Prod.snd, hc, Bool.not_true, Bool.false_eq_true, if_false] at hf
    cases hpol : policyPredicate E O p with
    | none =>
      have hs : (policyPredicate E O p).isSome = true := by
        unfold policyPredicate policyPredicateIn
        cases hp : E.predicate? p with
        | none => simp [hp] at hpred
        | some d => simp only [hp]; split <;> cases hform : List.lookup p E.forms.wordings <;> simp [hform]
      rw [hpol] at hs
      cases hs
    | some pair =>
      rcases pair with ⟨pw, pn⟩
      simp only [hpol] at hf
      have hsel : pn = some n ∧ L.wordings.lookup p = some pw := by
        by_cases hgood : pn = some n ∧ L.wordings.lookup p = some pw
        · exact hgood
        · simp [hgood] at hf
      exact ⟨pw, by simp [hpol, hsel.1, hsel.2]⟩
  · intro s n hmem m hm
    have hf := hnoun (s,n) hmem
    rw [hm] at hf
    simp at hf
    exact (Classical.em (n = m)).elim (fun h => Or.inl h) (fun h => Or.inr (hf h))
  · intro c sp hmem m hm
    have hf := hspell (c,sp) hmem
    rw [hm] at hf
    simp at hf
    exact (Classical.em (sp = m)).elim (fun h => Or.inl h) (fun h => Or.inr (hf h))

theorem admitRequest_ok : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List (EFormula × Bool)) (obs : List (Nat × List Nat)),
  admitRequest E O L b s = .ok rs obs →
  L.policyOk E O = true ∧ EnglishOneReading E O L s rs ∧ obs = obligations rs ∧ ∀ o ∈ obs, o.2 ≠ [] := by
  intro E O L b s rs obs h
  unfold admitRequest at h
  by_cases hp : L.policyOk E O = true
  · simp [hp] at h
    exact ⟨hp, admit_ok E O L b s rs obs h |>.1, (admit_ok E O L b s rs obs h).2.1,
      (admit_ok E O L b s rs obs h).2.2⟩
  · simp [hp] at h

theorem admitRequest_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List (EFormula × Bool)),
  (∃ obs, admitRequest E O L b s = .ok rs obs) ↔
    (L.policyOk E O = true ∧ read E O L b s = .ok rs ∧ ∀ o ∈ obligations rs, o.2 ≠ []) := by
  intro E O L b s rs
  unfold admitRequest
  by_cases hp : L.policyOk E O = true
  · simp [hp, admit_exact]
  · simp [hp]

theorem admitRequest_policy : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String),
  L.policyOk E O = false → admitRequest E O L b s = .refused (.invalidGrammar .lexicon) := by
  intro E O L b s h
  simp [admitRequest, h]

theorem translateRequest_policy : ∀ (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String),
  L.policyOk E O = false → translateRequest E O L cap b s = .invalidGrammar .lexicon := by
  intro E O L cap b s h
  simp [translateRequest, h]

theorem grammarFault_none : ∀ (E : Env) (O : Overlay) (L : Lexicon),
  grammarFault E O L = none → L.policyOk E O = true ∧ L.valid E O = true := by
  intro E O L h
  unfold grammarFault at h
  by_cases hp : L.policyOk E O = true
  · by_cases hv : L.valid E O = true
    · exact ⟨hp, hv⟩
    · simp [hp, hv] at h
  · simp [hp] at h

theorem overlayCheck_constants : ∀ (E : Env) (O : Overlay) (cs : List (String × String)),
  overlayCheck E { O with constants := cs } = overlayCheck E O := by
  intro E O cs
  rfl

theorem checkRequest_some : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) (i : Nat),
  checkRequest E O L b rs candidates = some i →
  L.policyOk E O = true ∧ ∃ s, candidates[i]? = some s ∧ read E O L b s = .ok rs ∧
    ∀ j t, j < i → candidates[j]? = some t → read E O L b t ≠ .ok rs := by
  intro E O L b rs candidates i h
  unfold checkRequest at h
  by_cases hp : L.policyOk E O = true
  · simp [hp] at h
    exact ⟨hp, first_checked E O L b rs candidates i h⟩
  · simp [hp] at h

end VE.EnglishGrammar
