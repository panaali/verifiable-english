import VE.Senses.Assignment
import VE.Grammar.Table

/-! The preamble: the lines that choose defaults (docs/spec/senses.md 2.4, 3.2 and 5.3; batch B4).

A sentence is preamble-shaped when its first four tokens are the words `in`, `this`, `document` (folded)
and a comma glued before; the test reads no dictionary. `preambleGrammar D` has one rule per sense of
`D.senses`, in order: `in this document,`, the word, `means` and the words of the gloss. A shaped line is
read by S1's engine (`verdict`); its one derivation names the sense. The faults of a line are those of
2.4's table. The leading shaped sentences are the preamble; a shaped sentence after the first body
sentence is `preambleLate`.
-/

namespace VE.Senses
open VE.Grammar VE.EnglishGrammar

/-- The rule of sense `s`, rule `i` of the preamble grammar. -/
def preambleRule (i : Nat) (s : Sense) : Rule Terminal :=
  { lhs := 0, act := i, tag := "preamble." ++ s.symbol,
    rhs := [.t (.kw "in"), .t (.kw "this"), .t (.kw "document"), .t (.exact (.punct "," true false)),
            .t (.content s.word), .t (.kw "means")] ++ (partsOf s.gloss).map fun g => .t (.content g) }

/-- One rule per sense of `D.senses`, in order; start symbol 0, one nonterminal of rank 0. -/
def preambleGrammar (D : Dictionary) : Grammar Terminal :=
  { rules := (D.senses.mapIdx preambleRule).toArray, start := 0, rank := #[0] }

/-- The first four tokens are `in`, `this`, `document` (folded) and a comma glued before. -/
def preambleShaped : List Tok → Bool
  | .word a _ :: .word b _ :: .word c _ :: .punct "," true _ :: _ =>
    fold a == "in" && fold b == "this" && fold c == "document"
  | _ => false

inductive Divergence where
  | referent (name : String)
  | binder
  deriving DecidableEq, Repr

inductive SenseFault where
  | invalidDictionary (f : DictFailure)
  | unknownWord (line : Nat) (word : String)
  | unknownGloss (line : Nat) (word gloss : String)
  | malformedPreamble (line : Nat)
  | preambleBudget (line : Nat)
  | repeatedDefault (line : Nat) (word : String)
  | preambleLate (sentence : Nat)
  /-- `kind`: sort, letter, name, a kind of a V4 pair, or an S2 condition (2.5). -/
  | collision (kind name : String) (sense : String)
  /-- `"sorts"` or `"predicates"`. -/
  | limit (what : String)
  | tooManyCandidates (sentence : Nat) (words : List String)
  | candidatesDiverge (sentence : Nat) (words : List String) (why : Divergence)
  | quotedSense (sentence : Nat) (word : String)
  deriving DecidableEq, Repr

/-- The fault of a shaped line with no derivation (2.4): an unknown word, an unknown gloss, or a
malformed line. -/
def zeroFault (D : Dictionary) (i : Nat) (w : List Tok) : SenseFault :=
  match w.drop 4 with
  | .word x _ :: rest =>
    if (D.sensesOf (fold x)).isEmpty then .unknownWord i (fold x)
    else
      match rest with
      | .word m _ :: g =>
        let gs := g.filterMap fun
          | .word y _ => some (fold y)
          | _ => none
        if fold m == "means" && !g.isEmpty && gs.length == g.length &&
            !((D.sensesOf (fold x)).any fun s => s.gloss == " ".intercalate gs) then
          .unknownGloss i (fold x) (" ".intercalate gs)
        else .malformedPreamble i
      | _ => .malformedPreamble i
  | _ => .malformedPreamble i

/-- The sense that the shaped sentence `w`, sentence `i` of the text, names; or its fault. -/
def readLine (D : Dictionary) (b : Nat) (i : Nat) (w : List Tok) : Except SenseFault Sense :=
  match verdict (preambleGrammar D) b w.toArray with
  | none => .error (.preambleBudget i)
  | some (.one (.node r _)) =>
    match D.senses[r]? with
    | some s => .ok s
    | none => .error (.malformedPreamble i)
  | some (.one (.leaf _)) => .error (.malformedPreamble i)
  | some (.many _ _) => .error (.malformedPreamble i)
  | some .zero => .error (zeroFault D i w)

/-- The index of the first shaped sentence. -/
def firstShaped : List (List Tok) → Option Nat
  | [] => none
  | w :: ws => if preambleShaped w then some 0 else (firstShaped ws).map (· + 1)

/-- Reads the leading shaped sentences from sentence `i`, with the defaults read so far (reversed). -/
def readPreambleGo (D : Dictionary) (b : Nat) : Nat → List (List Tok) → List (String × Nat) →
    Except SenseFault (Assignment × Nat)
  | i, [], acc => .ok (⟨acc.reverse⟩, i)
  | i, w :: ws, acc =>
    if preambleShaped w then
      match readLine D b i w with
      | .error f => .error f
      | .ok s =>
        if acc.any (·.1 == s.word) then .error (.repeatedDefault i s.word)
        else readPreambleGo D b (i + 1) ws ((s.word, s.index) :: acc)
    else
      match firstShaped ws with
      | some j => .error (.preambleLate (i + 1 + j))
      | none => .ok (⟨acc.reverse⟩, i)

/-- The assignment the preamble gives, in line order, and the number of its lines. -/
def readPreamble (D : Dictionary) (b : Nat) (sents : List (List Tok)) : Except SenseFault (Assignment × Nat) :=
  readPreambleGo D b 0 sents []

/-! ## The statements of spec 5.3 -/

theorem readLine_ok {D : Dictionary} {b i : Nat} {w : List Tok} {s : Sense} (h : readLine D b i w = .ok s) :
    ∃ t, verdict (preambleGrammar D) b w.toArray = some (.one t) := by
  unfold readLine at h
  split at h
  · cases h
  · exact ⟨_, by assumption⟩
  · exact ⟨_, by assumption⟩
  · cases h
  · cases h

theorem readPreambleGo_lines {D : Dictionary} {b : Nat} :
    ∀ (sents : List (List Tok)) (i : Nat) (acc : List (String × Nat)) (A : Assignment) (k : Nat),
    readPreambleGo D b i sents acc = .ok (A, k) →
    i ≤ k ∧ ∀ j, i ≤ j → j < k → ∀ w, sents[j - i]? = some w →
      ∃ t, verdict (preambleGrammar D) b w.toArray = some (.one t) := by
  intro sents
  induction sents with
  | nil =>
    intro i acc A k h
    simp only [readPreambleGo, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨_, rfl⟩ := h
    exact ⟨Nat.le_refl _, fun j h1 h2 => absurd h2 (Nat.not_lt.mpr h1)⟩
  | cons w ws ih =>
    intro i acc A k h
    unfold readPreambleGo at h
    split at h
    · split at h
      · cases h
      · rename_i s hl
        split at h
        · cases h
        · obtain ⟨hk, hall⟩ := ih (i + 1) _ A k h
          refine ⟨Nat.le_of_succ_le hk, ?_⟩
          intro j hj hjk w2 hw2
          by_cases e : j = i
          · subst e
            simp only [Nat.sub_self, List.getElem?_cons_zero, Option.some.injEq] at hw2
            subst hw2
            exact readLine_ok hl
          · have hj2 : i + 1 ≤ j := Nat.lt_of_le_of_ne hj (Ne.symm e)
            have : j - i = (j - (i + 1)) + 1 := by omega
            rw [this, List.getElem?_cons_succ] at hw2
            exact hall j hj2 hjk w2 hw2
    · split at h
      · cases h
      · simp only [Except.ok.injEq, Prod.mk.injEq] at h
        obtain ⟨_, rfl⟩ := h
        exact ⟨Nat.le_refl _, fun j h1 h2 => absurd h2 (Nat.not_lt.mpr h1)⟩

theorem preamble_unique : ∀ (D : Dictionary) (ss : List String) (b : Nat) (sents : List (List Tok))
    (A : Assignment) (k : Nat),
  D.wf ss = true → readPreamble D b sents = .ok (A, k) →
  ∀ i < k, ∀ w, sents[i]? = some w →
    ∃ t, verdict (preambleGrammar D) b w.toArray = some (.one t) := by
  intro D _ b sents A k _ h i hi w hw
  obtain ⟨_, hall⟩ := readPreambleGo_lines sents 0 [] A k h
  exact hall i (Nat.zero_le _) hi w (by simpa using hw)

/-- The statement of spec 5.3 that reading the rendered lines of an assignment gives it back. It is
checked on the fixtures (a10, a11) and not proved: its proof reads `lex` on the rendered text
(docs/spec/senses-lean-report.md). -/
def lines_read : Prop := ∀ (D : Dictionary) (ss : List String) (b : Nat) (A : Assignment)
    (sents : Array (Array Tok)),
  D.wf ss = true → A.wf D = true → lex (A.lines D) = .ok sents →
  (∀ w ∈ sents, verdict (preambleGrammar D) b w ≠ none) →
  readPreamble D b (sents.toList.map (·.toList)) = .ok (A, A.defaults.length)

end VE.Senses
