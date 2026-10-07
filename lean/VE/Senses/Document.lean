import VE.Senses.Read

/-! Senses in `ve document` (readings-defaults plan, section 6, batch RD-8).

A request reads one source, as `ve senses check` does, or the English fences of a document in unit order,
one sentence per fence (`SenseText`). The document's front matter may give defaults, `{word: index}`; they
are rendered with `Assignment.lines` and their lines are put before the text's sentences, so the preamble
stays the reader's one channel for defaults (senses D5): the reader is `readSents`, the same as for a
source. Defaults together with a written preamble line are refused, and so is a default that names no
sense of its word. With no defaults a source reads exactly as `readWithSenses` reads it
(`readDocument_source`).

`fenceUnits` says, for each fence, which unit of the answer is its sentence, or that the fence is a preamble
line. `unresolvedText` is the English of an open unit (senses plan 2.8; spec 3.2, R11).
-/

namespace VE.Senses
open VE.Grammar VE.EnglishGrammar

/-- The text of a request: one source, or a document's English fences in unit order. -/
inductive SenseText where
  | source (s : String)
  | fences (fs : List String)
  deriving DecidableEq, Repr

def bothText : String := "InvalidInput: defaults are given both in the front matter and as lines"

/-- Fence `j` (from 0) lexes to `n` sentences, not one. -/
def fenceText (j n : Nat) : String :=
  "InvalidInput: English fence " ++ toString (j + 1) ++ " holds " ++ toString n ++
    " sentences; each VE fence must contain exactly one sentence"

def defaultText (w : String) (i : Nat) : String :=
  "InvalidInput: the front matter gives " ++ w ++ " the default " ++ toString i ++
    ", which is not one of its senses"

/-- The sentence of each fence, from fence `j` on: a lexical rejection of the first fence that has one, or
the text of the first fence that is not one sentence. -/
def fenceSents : Nat → List String → Except String (Except Reject (List (Array Tok)))
  | _, [] => .ok (.ok [])
  | j, f :: fs =>
    match lex f with
    | .error r => .ok (.error r)
    | .ok ws =>
      match ws.toList with
      | [w] =>
        match fenceSents (j + 1) fs with
        | .error e => .error e
        | .ok (.error r) => .ok (.error r)
        | .ok (.ok rest) => .ok (.ok (w :: rest))
      | other => .error (fenceText j other.length)

def SenseText.sents : SenseText → Except String (Except Reject (List (Array Tok)))
  | .source s =>
    match lex s with
    | .error r => .ok (.error r)
    | .ok ss => .ok (.ok ss.toList)
  | .fences fs => fenceSents 0 fs

/-- The first default that names no sense of its word. -/
def badDefault (D : Dictionary) (A : Assignment) : Option (String × Nat) :=
  A.defaults.find? fun (w, i) => !(D.sensesOf w).any (·.index == i)

/-- The sentences of the rendered defaults: none when there are none. -/
def defaultSents (D : Dictionary) (A : Assignment) : Except Reject (List (Array Tok)) :=
  if A.defaults.isEmpty then .ok []
  else
    match lex (A.lines D) with
    | .error r => .error r
    | .ok ls => .ok ls.toList

/-- Whether the first sentence of a text is a preamble line. -/
def writtenLine (ts : List (Array Tok)) : Bool := (ts.head?.map fun w => preambleShaped w.toList) == some true

/-- The sentences the reader reads and how many of them are rendered defaults; or the outcome that stops
before the reader; or the text of an invalid request. -/
def documentInput (D : Dictionary) (A : Assignment) (t : SenseText) :
    Except String (Except SensesOutcome (Nat × List (Array Tok))) :=
  match t.sents with
  | .error e => .error e
  | .ok (.error r) => .ok (.error (.lexical r))
  | .ok (.ok ts) =>
    match badDefault D A with
    | some (w, i) => .error (defaultText w i)
    | none =>
      if !A.defaults.isEmpty && writtenLine ts then .error bothText
      else
        match defaultSents D A with
        | .error r => .ok (.error (.lexical r))
        | .ok ds => .ok (.ok (ds.length, ds ++ ts))

/-- The reading of a request: the dictionary first, as `readWithSenses` checks it, then the text and the
defaults, then the reader. -/
def readDocument (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment) (t : SenseText) :
    Except String SensesOutcome :=
  match D.failures (E.sorts.map (·.name)) with
  | f :: _ => .ok (.fault (.invalidDictionary f))
  | [] =>
    match documentInput D A t with
    | .error e => .error e
    | .ok (.error o) => .ok o
    | .ok (.ok (_, sents)) => .ok (readSents D E L b sents)

/-- For each of `n` fences after `d` rendered lines: the index of its unit, or none for a preamble line. -/
def fenceUnits (D : Dictionary) (b d : Nat) (sents : List (Array Tok)) (n : Nat) : List (Option Nat) :=
  match readPreamble D b (sents.map (·.toList)) with
  | .ok (_, k) => (List.range n).map fun j => if d + j < k then none else some (d + j - k)
  | .error _ => []

/-! ## The English of an open unit -/

/-- A count in words, as the English of the senses spec writes it. -/
def countWord (n : Nat) : String :=
  ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"][n]?.getD (toString n)

/-- `a`, `a and b`, `a, b and c`. -/
def andList : List String → String
  | [] => ""
  | [a] => a
  | [a, b] => a ++ " and " ++ b
  | a :: rest => a ++ ", " ++ andList rest

def senseOf (D : Dictionary) (w : String) (i : Nat) : Option Sense := (D.sensesOf w).find? (·.index == i)

/-- The preamble lines of a choice, each in quotation marks. -/
def choiceLines (D : Dictionary) (c : List (String × Nat)) : String :=
  andList (c.filterMap fun (w, i) => (senseOf D w i).map fun s => "\"" ++ lineOf w s ++ "\"")

def choiceGloss (D : Dictionary) (c : Candidate) (w : String) : String :=
  ((c.choice.lookup w).bind (senseOf D w)).map (·.gloss) |>.getD ""

/-- The text of an open unit at `sentence` (from 0, preamble included): one word with one candidate (R11),
one word with several (plan 2.8), several words with one candidate or several. -/
def unresolvedText (D : Dictionary) (sentence : Nat) (u : SenseUnit) : String :=
  let head := "Sentence " ++ toString (sentence + 1) ++ " uses "
  match u.unresolved, u.candidates with
  | _, [] => ""
  | [w], [c] =>
    head ++ w ++ ", which has " ++ countWord (D.sensesOf w).length ++ " senses here, and only " ++
      choiceGloss D c w ++ " gives a reading of this sentence. Add the line " ++ choiceLines D c.choice ++
      " to say so."
  | [w], c :: c2 :: _ =>
    head ++ w ++ ", which has " ++ countWord (D.sensesOf w).length ++ " senses here: " ++
      "; ".intercalate ((D.sensesOf w).map (·.gloss)) ++ ". Add the line " ++ choiceLines D c.choice ++
      " or write " ++ w ++ " (meaning " ++ choiceGloss D c2 w ++ ")."
  | ws, [c] =>
    head ++ andList ws ++ ", which have more than one sense here, and only one choice of their senses gives " ++
      "a reading of this sentence. Add the lines " ++ choiceLines D c.choice ++ " to say so."
  | ws, c :: cs =>
    head ++ andList ws ++ ", which have more than one sense here, and " ++ countWord (cs.length + 1) ++
      " choices of their senses give a reading of this sentence. Add lines such as " ++ choiceLines D c.choice ++
      " to choose their senses."

/-! ## Statements -/

/-- With no defaults, a source reads exactly as `readWithSenses` reads it: `ve senses check` is unchanged. -/
theorem readDocument_source : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String),
    readDocument D E L b ⟨[]⟩ (.source s) = .ok (readWithSenses D E L b s) := by
  intro D E L b s
  unfold readDocument readWithSenses
  cases D.failures (E.sorts.map (·.name)) with
  | cons f fs => rfl
  | nil =>
    simp only [documentInput, SenseText.sents]
    cases lex s <;> simp [badDefault, defaultSents]

/-- A default that names no sense of its word is refused with its text. -/
theorem readDocument_bad_default : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment)
    (t : SenseText) (ts : List (Array Tok)) (w : String) (i : Nat),
    D.failures (E.sorts.map (·.name)) = [] → t.sents = .ok (.ok ts) → badDefault D A = some (w, i) →
    readDocument D E L b A t = .error (defaultText w i) ∧ (D.sensesOf w).all (·.index != i) = true := by
  intro D E L b A t ts w i hf ht hb
  refine ⟨by simp [readDocument, documentInput, hf, ht, hb], ?_⟩
  have := List.find?_some hb
  simpa [List.all_eq_true, List.any_eq_false] using this

/-- `badDefault` finds nothing exactly when every default names a sense of its word. -/
theorem badDefault_none : ∀ (D : Dictionary) (A : Assignment),
    badDefault D A = none ↔ ∀ p ∈ A.defaults, (D.sensesOf p.1).any (·.index == p.2) = true := by
  intro D A
  unfold badDefault
  rw [List.find?_eq_none]
  simp

/-- Defaults together with a written preamble line are refused. -/
theorem readDocument_both : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment)
    (t : SenseText) (w : Array Tok) (ts : List (Array Tok)),
    D.failures (E.sorts.map (·.name)) = [] → t.sents = .ok (.ok (w :: ts)) → badDefault D A = none →
    A.defaults ≠ [] → preambleShaped w.toList = true →
    readDocument D E L b A t = .error bothText := by
  intro D E L b A t w ts hf ht hb hA hw
  have : A.defaults.isEmpty = false := by cases e : A.defaults <;> simp_all
  simp [readDocument, documentInput, hf, ht, hb, this, writtenLine, hw]

/-- Defaults are read as their rendered lines put before the text: when the lines lex to `ls`, the reader
reads `ls` and then the text's sentences, and nothing else carries the defaults. -/
theorem readDocument_defaults : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment)
    (t : SenseText) (ts : List (Array Tok)) (ls : Array (Array Tok)),
    D.failures (E.sorts.map (·.name)) = [] → t.sents = .ok (.ok ts) → badDefault D A = none →
    A.defaults ≠ [] → writtenLine ts = false → lex (A.lines D) = .ok ls →
    readDocument D E L b A t = .ok (readSents D E L b (ls.toList ++ ts)) := by
  intro D E L b A t ts ls hf ht hb hA hw hl
  have : A.defaults.isEmpty = false := by cases e : A.defaults <;> simp_all
  simp [readDocument, documentInput, hf, ht, hb, this, hw, defaultSents, hl]

/-- A document with defaults in its front matter reads as the same text with the lines written: when a
source `s` lexes to the rendered lines followed by the text's sentences, the request with the defaults
gets `readWithSenses`'s answer on `s`. -/
theorem defaults_read_as_lines : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment)
    (t : SenseText) (ts : List (Array Tok)) (ls sents : Array (Array Tok)) (s : String),
    D.failures (E.sorts.map (·.name)) = [] → t.sents = .ok (.ok ts) → badDefault D A = none →
    A.defaults ≠ [] → writtenLine ts = false → lex (A.lines D) = .ok ls →
    lex s = .ok sents → sents.toList = ls.toList ++ ts →
    readDocument D E L b A t = .ok (readWithSenses D E L b s) := by
  intro D E L b A t ts ls sents s hf ht hb hA hw hl hs he
  rw [readDocument_defaults D E L b A t ts ls hf ht hb hA hw hl]
  simp [readWithSenses, hf, hs, he]

/-- Every fence of an accepted list is one sentence, in order. -/
theorem fenceSents_ok : ∀ (fs : List String) (j : Nat) (ts : List (Array Tok)),
    fenceSents j fs = .ok (.ok ts) →
    ts.length = fs.length ∧ ∀ (i : Nat) (f : String), fs[i]? = some f → ∃ w, lex f = .ok #[w] ∧ ts[i]? = some w := by
  intro fs
  induction fs with
  | nil =>
    intro j ts h
    simp only [fenceSents, Except.ok.injEq] at h
    subst h
    exact ⟨rfl, fun i f h => by simp at h⟩
  | cons f fs ih =>
    intro j ts h
    unfold fenceSents at h
    split at h
    · cases h
    · rename_i ws hl
      split at h
      · rename_i w hw
        split at h
        · cases h
        · cases h
        · rename_i rest hr
          simp only [Except.ok.injEq] at h
          subst h
          obtain ⟨hlen, hall⟩ := ih (j + 1) rest hr
          have hws : ws = #[w] := by
            cases ws with
            | mk l => subst hw; rfl
          refine ⟨by simp [hlen], fun i g hg => ?_⟩
          cases i with
          | zero =>
            simp only [List.getElem?_cons_zero, Option.some.injEq] at hg
            subst hg
            exact ⟨w, by rw [hl, hws], rfl⟩
          | succ i =>
            simp only [List.getElem?_cons_succ] at hg
            obtain ⟨w2, h1, h2⟩ := hall i g hg
            exact ⟨w2, h1, by simpa using h2⟩
      · cases h

/-- The facts of an accepted request: its dictionary passed, the sentences read, and the reader's facts. -/
theorem readDocument_ok {D : Dictionary} {E : Env} {L : Lexicon} {b : Nat} {A : Assignment} {t : SenseText}
    {units : List SenseUnit} {sm : List SenseOccurrence} {mx : List (String × List String)} {un : List String}
    {P : Projection} (h : readDocument D E L b A t = .ok (.ok units sm mx un P)) :
    D.failures (E.sorts.map (·.name)) = [] ∧
    ∃ d sents, documentInput D A t = .ok (.ok (d, sents)) ∧ readSents D E L b sents = .ok units sm mx un P := by
  unfold readDocument at h
  split at h
  · cases h
  · rename_i hf
    refine ⟨hf, ?_⟩
    split at h
    · cases h
    · rename_i o hi
      simp only [Except.ok.injEq] at h
      subst h
      exact absurd hi (by
        unfold documentInput
        split
        · simp
        · simp
        · split
          · simp
          · split
            · simp
            · split <;> simp)
    · rename_i d sents hi
      simp only [Except.ok.injEq] at h
      exact ⟨d, sents, hi, h⟩

/-- The sentences of an accepted fence request: the rendered lines, then one sentence per fence. -/
theorem documentInput_fences {D : Dictionary} {A : Assignment} {fs : List String} {d : Nat}
    {sents : List (Array Tok)} (h : documentInput D A (.fences fs) = .ok (.ok (d, sents))) :
    ∃ ds ts, sents = ds ++ ts ∧ ds.length = d ∧ fenceSents 0 fs = .ok (.ok ts) := by
  unfold documentInput SenseText.sents at h
  split at h
  · cases h
  · cases h
  · rename_i ts hts
    split at h
    · cases h
    · split at h
      · cases h
      · split at h
        · cases h
        · rename_i ds _
          simp only [Except.ok.injEq, Prod.mk.injEq] at h
          obtain ⟨rfl, rfl⟩ := h
          exact ⟨ds, ts, rfl, rfl, hts⟩

/-- Each fence of an accepted document is its own sentence, and `fenceUnits` maps it to the unit read from
that sentence: a resolved unit's formula is the one reading of the fence's sentence under the projection,
from the state the earlier units leave. -/
theorem document_unit_sound : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment)
    (fs : List String) (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String))
    (un : List String) (P : Projection) (j i : Nat),
    readDocument D E L b A (.fences fs) = .ok (.ok units sm mx un P) →
    (∃ d sents, documentInput D A (.fences fs) = .ok (.ok (d, sents)) ∧
      (fenceUnits D b d sents fs.length)[j]? = some (some i)) →
    ∃ f w u, fs[j]? = some f ∧ lex f = .ok #[w] ∧ units[i]? = some u ∧
      (u.formula.isSome = true ∨ u.candidates ≠ []) ∧
      ∀ (F : EFormula) (m : Bool), u.formula = some (F, m) →
        u.candidates = [] ∧ (grammar P.env P.lexicon).wf = true ∧
        readSentence (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon))
          (stateBefore units i) b w = (.ok F m, u.after) := by
  intro D E L b A fs units sm mx un P j i h ⟨d, sents, hi, hj⟩
  obtain ⟨-, d2, sents2, hi2, hr⟩ := readDocument_ok h
  rw [hi] at hi2
  simp only [Except.ok.injEq, Prod.mk.injEq] at hi2
  obtain ⟨rfl, rfl⟩ := hi2
  obtain ⟨A2, k, hpre, -, -, hg, hb, -, -⟩ := readSents_ok hr
  obtain ⟨ds, ts, rfl, rfl, hts⟩ := documentInput_fences hi
  obtain ⟨hlen, hall⟩ := fenceSents_ok fs 0 ts hts
  unfold fenceUnits at hj
  rw [hpre] at hj
  by_cases hjn : j < fs.length
  · rw [List.getElem?_map, List.getElem?_range hjn] at hj
    simp only [Option.map_some, Option.some.injEq] at hj
    by_cases hk : ds.length + j < k
    · simp [hk] at hj
    · simp only [hk, if_false, Option.some.injEq] at hj
      obtain ⟨f, hf⟩ : ∃ f, fs[j]? = some f := ⟨fs[j], List.getElem?_eq_getElem hjn⟩
      obtain ⟨w, hw, htw⟩ := hall j f hf
      obtain ⟨hulen, hgood⟩ := readBody_good _ _ _ _ _ hb
      have hsw : ((ds ++ ts).drop k)[i]? = some w := by
        rw [List.getElem?_drop, ← hj, show k + (ds.length + j - k) = ds.length + j by omega,
          List.getElem?_append_right (by omega)]
        simpa using htw
      have hi3 : i < units.length := by
        rw [hulen]
        exact (List.getElem?_eq_some_iff.mp hsw).1
      obtain ⟨u, hu⟩ : ∃ u, units[i]? = some u := ⟨units[i], List.getElem?_eq_getElem hi3⟩
      obtain ⟨w2, hw2, hgu⟩ := hgood i u hu
      rw [hsw] at hw2
      cases hw2
      rw [stateFrom_init] at hgu
      obtain ⟨h1, h2, -, -⟩ := hgu
      refine ⟨f, w, u, hf, hw, hu, h1, fun F m e => ?_⟩
      obtain ⟨hc, hrd⟩ := h2 F m e
      exact ⟨hc, (grammarFault_none hg).2, hrd⟩
  · rw [List.getElem?_map, List.getElem?_eq_none (by simpa using hjn)] at hj
    simp at hj

/-- A fence that `fenceUnits` maps to no unit is a preamble line: its one sentence has one derivation under
the preamble grammar. -/
theorem document_line_sound : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (A : Assignment)
    (fs : List String) (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String))
    (un : List String) (P : Projection) (j : Nat),
    readDocument D E L b A (.fences fs) = .ok (.ok units sm mx un P) →
    (∃ d sents, documentInput D A (.fences fs) = .ok (.ok (d, sents)) ∧
      (fenceUnits D b d sents fs.length)[j]? = some none) →
    ∃ f w t, fs[j]? = some f ∧ lex f = .ok #[w] ∧ verdict (preambleGrammar D) b w = some (.one t) := by
  intro D E L b A fs units sm mx un P j h ⟨d, sents, hi, hj⟩
  obtain ⟨-, d2, sents2, hi2, hr⟩ := readDocument_ok h
  rw [hi] at hi2
  simp only [Except.ok.injEq, Prod.mk.injEq] at hi2
  obtain ⟨rfl, rfl⟩ := hi2
  obtain ⟨A2, k, hpre, -⟩ := readSents_ok hr
  obtain ⟨ds, ts, rfl, rfl, hts⟩ := documentInput_fences hi
  obtain ⟨-, hall⟩ := fenceSents_ok fs 0 ts hts
  unfold fenceUnits at hj
  rw [hpre] at hj
  by_cases hjn : j < fs.length
  · rw [List.getElem?_map, List.getElem?_range hjn] at hj
    simp only [Option.map_some, Option.some.injEq] at hj
    by_cases hk : ds.length + j < k
    · obtain ⟨f, hf⟩ : ∃ f, fs[j]? = some f := ⟨fs[j], List.getElem?_eq_getElem hjn⟩
      obtain ⟨w, hw, htw⟩ := hall j f hf
      obtain ⟨-, hlines⟩ := readPreambleGo_lines _ 0 [] A2 k hpre
      have hsw : ((ds ++ ts).map (·.toList))[ds.length + j - 0]? = some w.toList := by
        simp [List.getElem?_append_right, htw]
      obtain ⟨t, ht⟩ := hlines (ds.length + j) (Nat.zero_le _) hk w.toList hsw
      exact ⟨f, w, t, hf, hw, by simpa using ht⟩
    · simp [hk] at hj
  · rw [List.getElem?_map, List.getElem?_eq_none (by simpa using hjn)] at hj
    simp at hj

end VE.Senses
