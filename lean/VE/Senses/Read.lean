import VE.Senses.Project

/-! Reading with senses (docs/spec/senses.md 2.6, 3.3 and 5.3; batch B5, on the merged S2 grammar).

`readWithSenses D E L b s` checks the dictionary, lexes the text, reads the preamble, projects the
dictionary onto the document's lexicon for the words the body uses, runs S2's checks on the projection,
and reads the body sentence by sentence with S2's `readSentence` under `grammar P.env P.lexicon`. A
sentence with no derivation whose words with no default occur unswitched becomes an open unit: every
choice of one sense per such word is projected and read from the same state, and the choices that read
and type are its candidates. Nothing is guessed: one candidate is still an open unit. The reader stops
on a budget, an ambiguity or a rejection, as S2's reader does.

The grammar is S2's as merged: request R3 of the specification (6.2) is not applied, so a gloss after a
word that ends its wording reads only before a mark (L12), and the comma forms stay (Q4's rule on the
*as merged* column).
-/

namespace VE.Senses
open Lean VE.Grammar VE.EnglishGrammar

structure Candidate where
  choice : List (String × Nat)
  /-- `Assignment.lines D (A.extend choice)`. -/
  lines : String
  formula : EFormula
  mark : Bool
  deriving DecidableEq, Repr

structure SenseUnit where
  /-- Some exactly when the unit is resolved. -/
  formula : Option (EFormula × Bool)
  /-- Not empty exactly when the unit is open. -/
  candidates : List Candidate
  unresolved : List String
  /-- The state after the unit. -/
  after : DState
  deriving DecidableEq, Repr

structure SenseOccurrence where
  /-- The index of the sentence in the whole text, preamble included. -/
  sentence : Nat
  /-- Token index, inclusive. -/
  start : Nat
  /-- Token index, exclusive. -/
  stop : Nat
  symbol : String
  isDefault : Bool
  /-- None for a resolved unit. -/
  candidate : Option Nat
  deriving DecidableEq, Repr

inductive SensesOutcome where
  | ok (units : List SenseUnit) (senses : List SenseOccurrence) (mixed : List (String × List String))
       (unused : List String) (P : Projection)
  | fault (f : SenseFault)
  | lexical (r : Reject)
  | invalidGrammar (why : GrammarFault)
  | stopped (index : Nat) (o : Outcome Tok Reject EFormula)
  | illTyped

/-- The most choices an open unit may have. -/
def candidateCap : Nat := 8

/-- Every choice of one sense for each of the words, in the order of the words and of their senses. -/
def choicesOf (D : Dictionary) : List String → List (List (String × Nat))
  | [] => [[]]
  | w :: ws => (D.sensesOf w).flatMap fun s => (choicesOf D ws).map fun c => (w, s.index) :: c

/-- Whether the tokens begin a gloss: `(` and `meaning`, or a comma and `in the sense of`. -/
def glossFollows : List Tok → Bool
  | .punct "(" _ _ :: .word m _ :: _ => fold m == "meaning"
  | .punct "," _ _ :: .word a _ :: .word b _ :: .word c _ :: .word d _ :: _ =>
    fold a == "in" && fold b == "the" && fold c == "sense" && fold d == "of"
  | _ => false

/-- Whether the token at `j` is followed by `(` and `meaning`, or by a comma and `in the sense of`. -/
def switchedAt (w : List Tok) (j : Nat) : Bool := glossFollows (w.drop (j + 1))

/-- Whether some token of `w` folds to a headword token of `x` and is not switched. -/
def unswitchedIn (D : Dictionary) (x : String) (w : List Tok) : Bool :=
  let heads := (D.sensesOf x).flatMap (·.headwordTokens)
  (List.range w.length).any fun j =>
    match w[j]? with
    | some (.word t _) => heads.contains (fold t) && !switchedAt w j
    | _ => false

/-- The used words of one sentence that have no default under `A` and an unswitched occurrence. -/
def unresolvedIn (D : Dictionary) (A : Assignment) (w : List Tok) : List String :=
  (usedWords D [w]).filter fun x => (defaultOf D A x).isNone && unswitchedIn D x w

def stateBefore (units : List SenseUnit) : Nat → DState
  | 0 => DState.init
  | i + 1 =>
    match units[i]? with
    | some u => u.after
    | none => DState.init

/-- The predicate names of a formula, with repetition, in order. -/
def EFormula.predNames : EFormula → List String
  | .pred p _ => [p]
  | .reachNamed _ r _ _ => [r]
  | .not a | .all _ a | .ex _ a | .reachBody _ _ a _ _ => EFormula.predNames a
  | .and a b | .or a b | .implies a b => EFormula.predNames a ++ EFormula.predNames b
  | _ => []

/-- The predicate names of a formula, with repetition, that the projection's map names. -/
def senseOccurrences (P : Projection) (A : EFormula) : List String :=
  (EFormula.predNames A).filter fun p => (P.wordOf p).isSome

/-- For each word of the map, the senses of its occurrences in the resolved formulas, in order of first
occurrence, when there are two or more. -/
def mixedOf (P : Projection) (units : List SenseUnit) : List (String × List String) :=
  ((P.map.map fun x => x.2.1.word).eraseDups).filterMap fun w =>
    let ids := ((units.filterMap (·.formula)).flatMap fun (A, _) =>
      (senseOccurrences P A).filter (P.wordOf · == some w)).eraseDups
    if 2 ≤ ids.length then some (w, ids) else none

/-- Why two successor states differ: the first constant one has and the other lacks, else the binder. -/
def divergence (a b : DState) : Divergence :=
  match (a.referents.filter fun x => !b.referents.contains x) ++ (b.referents.filter fun x => !a.referents.contains x) with
  | x :: _ => .referent x
  | [] => .binder

/-! ## S2's checks and one sentence under a projection -/

/-- S2's checks on a projection, called in `read`'s order. -/
def grammarFault (P : Projection) : Option GrammarFault :=
  if !P.lexicon.valid P.env {} then some .lexicon
  else if !((grammar P.env P.lexicon).wf && terminatorFree (grammar P.env P.lexicon)) then some .notWellFormed
  else if !((grammar P.env P.lexicon).typed sig (ty P.env P.lexicon) (acts P.env P.lexicon) &&
      decide (ty P.env P.lexicon (grammar P.env P.lexicon).start = .sentence)) then some .notTyped
  else none

/-- One sentence under a projection, as `readSentence` reads it, with the tree of a reading: its tree and
result, no derivation (`none`), or the outcome that stops. -/
def readOne (P : Projection) (st : DState) (b : Nat) (w : Array Tok) :
    Except (Outcome Tok Reject EFormula) (Option (Tree Tok × EFormula × Bool × DState)) :=
  match verdict (grammar P.env P.lexicon) b w with
  | none => .error .budget
  | some .zero => .ok none
  | some (.many t u) => .error (.ambiguous t u)
  | some (.one t) =>
    match meaning (grammar P.env P.lexicon) (acts P.env P.lexicon) st t with
    | .ok (F, m, st2) => .ok (some (t, F, m, st2))
    | .error r => .error (.rejected r)

/-! ## The trees: the sense map and quoted names -/

/-- The predicate a lexical action names, for the actions of the sense map. -/
def actPredicate : LexAct → Option String
  | .pred p _ _ | .relSubject p _ _ | .relObject p _ | .adjective p _ | .natSubject p _ _ | .copulaRel p => some p
  | _ => none

/-- The tokens of a head and its gloss among the children that follow the head: 1 for a bare head. -/
def glossLength (glossWords : Nat) : List (Tree Tok) → Nat
  | .leaf (.punct "(" _ _) :: _ => 4 + glossWords
  | .leaf (.punct "," _ _) :: .leaf (.word a _) :: .leaf (.word b _) :: .leaf (.word c _) :: .leaf (.word d _) :: rest =>
    if fold a == "in" && fold b == "the" && fold c == "sense" && fold d == "of" then
      match rest.drop glossWords with
      | .leaf (.punct "," _ _) :: _ => 7 + glossWords
      | _ => 6 + glossWords
    else 1
  | _ => 1

/-- The span of the first child that is a headword token of `s`, with its gloss, among the children of a
node that starts at `offset`. -/
def headSpan (s : Sense) : List (Tree Tok) → Nat → Option (Nat × Nat)
  | [], _ => none
  | .leaf (.word x _) :: rest, offset =>
    if s.headwordTokens.contains (fold x) then some (offset, offset + glossLength (partsOf s.gloss).length rest)
    else headSpan s rest (offset + 1)
  | t :: rest, offset => headSpan s rest (offset + t.yield.length)

/-- The sense occurrence of a node of rule `r` with children `kids` at `offset`, when its rule is a lexical
rule of a predicate that the map names. -/
def occurrenceAt (P : Projection) (rows : List LexRow) (fixedN sentence : Nat) (cand : Option Nat) (r : Nat)
    (kids : List (Tree Tok)) (offset : Nat) : List SenseOccurrence :=
  if r < fixedN then [] else
  match (rows[r - fixedN]?).bind (actPredicate ·.act) with
  | some p =>
    match P.map.find? (·.1 == p) with
    | some (_, s, isDefault) =>
      let span := (headSpan s kids offset).getD (offset, offset + (Tree.node r kids).yield.length)
      [⟨sentence, span.1, span.2, p, isDefault, cand⟩]
    | none => []
  | none => []

mutual
/-- The sense occurrences of a tree that starts at token `offset`, in preorder. -/
def occurrencesIn (P : Projection) (rows : List LexRow) (fixedN sentence : Nat) (cand : Option Nat) :
    Tree Tok → Nat → List SenseOccurrence
  | .leaf _, _ => []
  | .node r kids, offset =>
    occurrenceAt P rows fixedN sentence cand r kids offset ++ occurrencesKids P rows fixedN sentence cand kids offset
/-- The sense occurrences of a list of sibling trees. -/
def occurrencesKids (P : Projection) (rows : List LexRow) (fixedN sentence : Nat) (cand : Option Nat) :
    List (Tree Tok) → Nat → List SenseOccurrence
  | [], _ => []
  | t :: ts, offset =>
    occurrencesIn P rows fixedN sentence cand t offset ++
      occurrencesKids P rows fixedN sentence cand ts (offset + t.yield.length)
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace (see `Derives.lean`).
end VE.Senses

namespace VE.Senses
open Lean VE.Grammar VE.EnglishGrammar

/-- The word of the sense whose quoted name a node of rule `r` reads (S2's `relation.` row). -/
def quotedAt (P : Projection) (rows : List LexRow) (fixedN r : Nat) : Option String :=
  if r < fixedN then none else
  match rows[r - fixedN]? with
  | some ⟨_, _, _, .relation p⟩ => P.wordOf p
  | _ => none

mutual
/-- The word of the first sense, in preorder, whose quoted name the tree reads. -/
def quotedIn (P : Projection) (rows : List LexRow) (fixedN : Nat) : Tree Tok → Option String
  | .leaf _ => none
  | .node r kids =>
    match quotedAt P rows fixedN r with
    | some x => some x
    | none => quotedKids P rows fixedN kids
/-- `quotedIn` over a list of sibling trees. -/
def quotedKids (P : Projection) (rows : List LexRow) (fixedN : Nat) : List (Tree Tok) → Option String
  | [] => none
  | t :: ts =>
    match quotedIn P rows fixedN t with
    | some x => some x
    | none => quotedKids P rows fixedN ts
end
end VE.Senses

namespace VE.Senses
open Lean VE.Grammar VE.EnglishGrammar

/-- The sense occurrences of a sentence's tree under a projection. -/
def senseMapOf (P : Projection) (sentence : Nat) (cand : Option Nat) (t : Tree Tok) : List SenseOccurrence :=
  occurrencesIn P (lexRows P.env P.lexicon) (fixedRules P.env.profiles).size sentence cand t 0

/-- The word of a sense whose quoted name the sentence's tree reads. -/
def quotedSenseOf (P : Projection) (t : Tree Tok) : Option String :=
  quotedIn P (lexRows P.env P.lexicon) (fixedRules P.env.profiles).size t

/-! ## The units -/

/-- Why the reading of the body stops: a fault, a failed check of a candidate's projection, or S2's
outcome for a sentence. -/
inductive Stop where
  | fault (f : SenseFault)
  | invalidGrammar (why : GrammarFault)
  | stopped (index : Nat) (o : Outcome Tok Reject EFormula)

def Stop.outcome : Stop → SensesOutcome
  | .fault f => .fault f
  | .invalidGrammar g => .invalidGrammar g
  | .stopped i o => .stopped i o

/-- One choice for an unresolved sentence: its candidate, its successor state and its occurrences; none
when the choice is dropped (no derivation, or a formula that does not type); or the outcome that stops. -/
def tryChoice (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (b sentence : Nat)
    (st : DState) (w : Array Tok) (j : Nat) (c : List (String × Nat)) :
    Except Stop (Option (Candidate × DState × List SenseOccurrence)) :=
  match project D (A.extend c) E L used with
  | .error f => .error (.fault f)
  | .ok P2 =>
    match grammarFault P2 with
    | some g => .error (.invalidGrammar g)
    | none =>
      match readOne P2 st b w with
      | .error o => .error (.stopped sentence o)
      | .ok none => .ok none
      | .ok (some (t, F, m, st2)) =>
        if typedDocument P2.env [F] then
          match quotedSenseOf P2 t with
          | some word => .error (.fault (.quotedSense sentence word))
          | none => .ok (some (⟨c, Assignment.lines D (A.extend c), F, m⟩, st2, senseMapOf P2 sentence (some j) t))
        else .ok none

/-- The candidates of an unresolved sentence, the `j`-th candidate first. -/
def candidatesOf (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (b sentence : Nat)
    (st : DState) (w : Array Tok) : List (List (String × Nat)) → Nat →
    Except Stop (List (Candidate × DState × List SenseOccurrence))
  | [], _ => .ok []
  | c :: cs, j =>
    match tryChoice D A E L used b sentence st w j c with
    | .error o => .error o
    | .ok none => candidatesOf D A E L used b sentence st w cs j
    | .ok (some x) =>
      match candidatesOf D A E L used b sentence st w cs (j + 1) with
      | .error o => .error o
      | .ok rest => .ok (x :: rest)

/-- The open unit of a sentence with no derivation under the base projection, or the outcome that stops. -/
def openUnit (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (b sentence : Nat)
    (st : DState) (w : Array Tok) : Except Stop (SenseUnit × List SenseOccurrence) :=
  let words := unresolvedIn D A w.toList
  if words.isEmpty then .error (.stopped sentence .noDerivation)
  else if (choicesOf D words).length > candidateCap then .error (.fault (.tooManyCandidates sentence words))
  else
    match candidatesOf D A E L used b sentence st w (choicesOf D words) 0 with
    | .error o => .error o
    | .ok [] => .error (.stopped sentence .noDerivation)
    | .ok ((c, st2, occ) :: rest) =>
      match rest.find? (fun x => x.2.1 != st2) with
      | some (_, st3, _) => .error (.fault (.candidatesDiverge sentence words (divergence st2 st3)))
      | none => .ok (⟨none, c :: rest.map (·.1), words, st2⟩, occ ++ rest.flatMap (·.2.2))

/-- One body sentence from the state `st`: a resolved unit, an open unit, or the outcome that stops. -/
def readUnit (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (P : Projection)
    (b sentence : Nat) (st : DState) (w : Array Tok) : Except Stop (SenseUnit × List SenseOccurrence) :=
  match readOne P st b w with
  | .error o => .error (.stopped sentence o)
  | .ok (some (t, F, m, st2)) =>
    match quotedSenseOf P t with
    | some word => .error (.fault (.quotedSense sentence word))
    | none => .ok (⟨some (F, m), [], [], st2⟩, senseMapOf P sentence none t)
  | .ok none => openUnit D A E L used b sentence st w

/-- The body sentences in order, body sentence `i` being sentence `k + i` of the text. -/
def readBody (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (P : Projection)
    (b k : Nat) : Nat → DState → List (Array Tok) → Except Stop (List SenseUnit × List SenseOccurrence)
  | _, _, [] => .ok ([], [])
  | i, st, w :: ws =>
    match readUnit D A E L used P b (k + i) st w with
    | .error o => .error o
    | .ok (u, occ) =>
      match readBody D A E L used P b k (i + 1) u.after ws with
      | .error o => .error o
      | .ok (us, occs) => .ok (u :: us, occ ++ occs)

/-- Steps 7 to 10 of 2.6 on the projection `P`. -/
def readProjected (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (P : Projection)
    (b k : Nat) (body : List (Array Tok)) : SensesOutcome :=
  match grammarFault P with
  | some g => .invalidGrammar g
  | none =>
    match readBody D A E L used P b k 0 DState.init body with
    | .error o => o.outcome
    | .ok (units, occ) =>
      if (units.filterMap (·.formula)).isEmpty || typedDocument P.env ((units.filterMap (·.formula)).map (·.1)) then
        .ok units occ (mixedOf P units) ((A.defaults.map (·.1)).filter fun w => !used.contains w) P
      else .illTyped

def readWithSenses (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String) : SensesOutcome :=
  match D.failures (E.sorts.map (·.name)) with
  | f :: _ => .fault (.invalidDictionary f)
  | [] =>
    match lex s with
    | .error r => .lexical r
    | .ok sents =>
      match readPreamble D b (sents.toList.map (·.toList)) with
      | .error f => .fault f
      | .ok (A, k) =>
        if (sents.toList.drop k).isEmpty then .lexical .emptyDocument
        else if !L.valid E {} then .invalidGrammar .lexicon
        else
          match project D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) with
          | .error f => .fault f
          | .ok P => readProjected D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) P b k
              (sents.toList.drop k)

end VE.Senses

/-! ## The statements of spec 5.3 -/

namespace VE.Senses
open Lean VE.Grammar VE.EnglishGrammar

theorem mem_eraseDups_iff {α : Type} [BEq α] [LawfulBEq α] : ∀ {l : List α} {a : α}, a ∈ l.eraseDups ↔ a ∈ l
  | [], _ => by simp
  | x :: xs, a => by
    rw [List.eraseDups_cons]
    have : (xs.filter fun b => !b == x).length < xs.length + 1 := Nat.lt_succ_of_le (List.length_filter_le _ _)
    have ih := @mem_eraseDups_iff α _ _ (xs.filter fun b => !b == x) a
    simp only [List.mem_cons, ih, List.mem_filter, Bool.not_eq_eq_eq_not, Bool.not_true, beq_eq_false_iff_ne]
    constructor
    · rintro (h | ⟨h, _⟩)
      · exact Or.inl h
      · exact Or.inr h
    · intro h
      by_cases e : a = x
      · exact Or.inl e
      · rcases h with h | h
        · exact absurd h e
        · exact Or.inr ⟨h, e⟩
termination_by l => l.length

theorem readOne_some {P : Projection} {st : DState} {b : Nat} {w : Array Tok} {t : Tree Tok} {F : EFormula}
    {m : Bool} {st2 : DState} (h : readOne P st b w = .ok (some (t, F, m, st2))) :
    readSentence (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon)) st b w =
      (.ok F m, st2) := by
  unfold readOne at h
  unfold readSentence
  split at h
  · cases h
  · cases h
  · cases h
  · rename_i t2 hv
    rw [hv]
    split at h
    · rename_i F2 m2 s2 hm
      simp only [Except.ok.injEq, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl, rfl, rfl⟩ := h
      simp only [hm]
    · cases h

theorem readOne_ok_iff {P : Projection} {st : DState} {b : Nat} {w : Array Tok} {F : EFormula} {m : Bool} :
    (readSentence (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon)) st b w).1 =
      .ok F m ↔ ∃ t st2, readOne P st b w = .ok (some (t, F, m, st2)) := by
  constructor
  · intro h
    unfold readSentence at h
    unfold readOne
    split at h
    · cases h
    · cases h
    · cases h
    · rename_i t hv
      rw [hv]
      split at h
      · rename_i F2 m2 s2 hm
        simp only [Outcome.ok.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨t, s2, by simp only [hm]⟩
      · cases h
  · rintro ⟨t, st2, h⟩
    rw [readOne_some h]

theorem grammarFault_none {P : Projection} (h : grammarFault P = none) :
    P.lexicon.valid P.env {} = true ∧ (grammar P.env P.lexicon).wf = true := by
  unfold grammarFault at h
  by_cases h1 : P.lexicon.valid P.env {} = true
  · by_cases h2 : ((grammar P.env P.lexicon).wf && terminatorFree (grammar P.env P.lexicon)) = true
    · simp only [Bool.and_eq_true] at h2
      exact ⟨h1, h2.1⟩
    · simp [h1, h2] at h
  · simp [h1] at h

/-- What a candidate of choice `c` from the state `st` satisfies: its lines, its projection, its reading
under that projection, and its type. -/
def CandidateGood (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (b : Nat)
    (st : DState) (w : Array Tok) (x : Candidate × DState × List SenseOccurrence) : Prop :=
  x.1.lines = Assignment.lines D (A.extend x.1.choice) ∧
  ∃ P2, project D (A.extend x.1.choice) E L used = .ok P2 ∧ P2.lexicon.valid P2.env {} = true ∧
    (grammar P2.env P2.lexicon).wf = true ∧
    readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon)) st b w =
      (.ok x.1.formula x.1.mark, x.2.1) ∧ typedDocument P2.env [x.1.formula] = true

theorem tryChoice_some {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {b sentence : Nat} {st : DState} {w : Array Tok} {j : Nat} {c : List (String × Nat)}
    {x : Candidate × DState × List SenseOccurrence}
    (h : tryChoice D A E L used b sentence st w j c = .ok (some x)) :
    x.1.choice = c ∧ CandidateGood D A E L used b st w x := by
  unfold tryChoice at h
  split at h
  · cases h
  · rename_i P2 hp
    split at h
    · cases h
    · rename_i hg
      split at h
      · cases h
      · cases h
      · rename_i t F m st2 hr
        split at h
        · rename_i ht
          split at h
          · cases h
          · simp only [Except.ok.injEq, Option.some.injEq] at h
            subst h
            obtain ⟨hv, hw⟩ := grammarFault_none hg
            exact ⟨rfl, rfl, P2, hp, hv, hw, readOne_some hr, ht⟩
        · cases h

theorem tryChoice_none {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {b sentence : Nat} {st : DState} {w : Array Tok} {j : Nat} {c : List (String × Nat)}
    (h : tryChoice D A E L used b sentence st w j c = .ok none) :
    ∀ P2, project D (A.extend c) E L used = .ok P2 → ∀ F m,
      (readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
        st b w).1 = .ok F m → typedDocument P2.env [F] = false := by
  intro P2 hp F m hr
  obtain ⟨t, st2, hr⟩ := readOne_ok_iff.mp hr
  unfold tryChoice at h
  rw [hp] at h
  simp only at h
  split at h
  · cases h
  · rw [hr] at h
    simp only at h
    split at h
    · split at h
      · cases h
      · cases h
    · rename_i ht
      simpa using ht

theorem candidatesOf_sound {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {b sentence : Nat} {st : DState} {w : Array Tok} :
    ∀ (cs : List (List (String × Nat))) (j : Nat) (xs : List (Candidate × DState × List SenseOccurrence)),
    candidatesOf D A E L used b sentence st w cs j = .ok xs →
    ∀ x ∈ xs, x.1.choice ∈ cs ∧ CandidateGood D A E L used b st w x := by
  intro cs
  induction cs with
  | nil =>
    intro j xs h x hx
    simp only [candidatesOf, Except.ok.injEq] at h
    subst h
    cases hx
  | cons c cs ih =>
    intro j xs h x hx
    unfold candidatesOf at h
    split at h
    · cases h
    · rename_i hc
      obtain ⟨h1, h2⟩ := ih j xs h x hx
      exact ⟨List.mem_cons_of_mem _ h1, h2⟩
    · rename_i y hc
      split at h
      · cases h
      · rename_i rest hr
        simp only [Except.ok.injEq] at h
        subst h
        rcases List.mem_cons.mp hx with e | hx
        · subst e
          obtain ⟨e, hg⟩ := tryChoice_some hc
          exact ⟨e ▸ List.mem_cons_self, hg⟩
        · obtain ⟨h1, h2⟩ := ih (j + 1) rest hr x hx
          exact ⟨List.mem_cons_of_mem _ h1, h2⟩

theorem candidatesOf_complete {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {b sentence : Nat} {st : DState} {w : Array Tok} :
    ∀ (cs : List (List (String × Nat))) (j : Nat) (xs : List (Candidate × DState × List SenseOccurrence)),
    candidatesOf D A E L used b sentence st w cs j = .ok xs →
    ∀ c ∈ cs, ∀ P2, project D (A.extend c) E L used = .ok P2 → ∀ F m,
      (readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
        st b w).1 = .ok F m → typedDocument P2.env [F] = true →
      ∃ x ∈ xs, x.1.choice = c ∧ x.1.formula = F ∧ x.1.mark = m := by
  intro cs
  induction cs with
  | nil => intro j xs _ c hc; cases hc
  | cons c0 cs ih =>
    intro j xs h c hc P2 hp F m hr ht
    unfold candidatesOf at h
    split at h
    · cases h
    · rename_i hn
      rcases List.mem_cons.mp hc with e | hc
      · subst e
        have := tryChoice_none hn P2 hp F m hr
        rw [ht] at this
        cases this
      · exact ih j xs h c hc P2 hp F m hr ht
    · rename_i y hy
      split at h
      · cases h
      · rename_i rest hrest
        simp only [Except.ok.injEq] at h
        subst h
        rcases List.mem_cons.mp hc with e | hc
        · subst e
          obtain ⟨e, -, P3, hp3, -, -, hr3, -⟩ := tryChoice_some hy
          rw [e] at hp3
          rw [hp] at hp3
          cases hp3
          rw [hr3] at hr
          simp only [Outcome.ok.injEq] at hr
          exact ⟨y, List.mem_cons_self, e, hr.1, hr.2⟩
        · obtain ⟨x, hx, h1⟩ := ih (j + 1) rest hrest c hc P2 hp F m hr ht
          exact ⟨x, List.mem_cons_of_mem _ hx, h1⟩

/-- What a unit read from the state `st` satisfies (2.6): it has a formula or a candidate; a resolved
unit is the reader's outcome under the base projection; each candidate is its choice's reading under its
own projection, typed, leaving the unit's state; and the candidates are exactly the choices that read and
type. -/
def UnitGood (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) (P : Projection)
    (b : Nat) (st : DState) (w : Array Tok) (u : SenseUnit) : Prop :=
  (u.formula.isSome = true ∨ u.candidates ≠ []) ∧
  (∀ F m, u.formula = some (F, m) → u.candidates = [] ∧
    readSentence (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon)) st b w =
      (.ok F m, u.after)) ∧
  (∀ c ∈ u.candidates, u.formula = none ∧ c.choice ∈ choicesOf D u.unresolved ∧
    CandidateGood D A E L used b st w (c, u.after, [])) ∧
  (u.candidates ≠ [] → ∀ choice F m,
    ((choice ∈ choicesOf D u.unresolved ∧ ∃ P2, project D (A.extend choice) E L used = .ok P2 ∧
      (readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
        st b w).1 = .ok F m ∧ typedDocument P2.env [F] = true)
     ↔ ∃ c ∈ u.candidates, c.choice = choice ∧ c.formula = F ∧ c.mark = m))

theorem openUnit_good {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {P : Projection} {b sentence : Nat} {st : DState} {w : Array Tok} {u : SenseUnit} {occ : List SenseOccurrence}
    (h : openUnit D A E L used b sentence st w = .ok (u, occ)) : UnitGood D A E L used P b st w u := by
  unfold openUnit at h
  simp only at h
  split at h
  · cases h
  · split at h
    · cases h
    · split at h
      · cases h
      · cases h
      · rename_i c st2 occ0 rest hcs
        split at h
        · cases h
        · rename_i hf
          simp only [Except.ok.injEq, Prod.mk.injEq] at h
          obtain ⟨rfl, -⟩ := h
          have hsame : ∀ x ∈ rest, x.2.1 = st2 := by
            intro x hx
            have := List.find?_eq_none.mp hf x hx
            simpa using this
          have hsound := candidatesOf_sound _ _ _ hcs
          have hcomp := candidatesOf_complete _ _ _ hcs
          refine ⟨Or.inr (List.cons_ne_nil _ _), fun F m e => (by cases e), ?_, ?_⟩
          · intro c' hc'
            refine ⟨rfl, ?_⟩
            rcases List.mem_cons.mp hc' with e | hc'
            · subst e
              obtain ⟨h1, h2⟩ := hsound _ List.mem_cons_self
              exact ⟨h1, h2⟩
            · obtain ⟨x, hx, e⟩ := List.mem_map.mp hc'
              subst e
              obtain ⟨h1, h2⟩ := hsound x (List.mem_cons_of_mem _ hx)
              refine ⟨h1, ?_⟩
              have hx2 := hsame x hx
              obtain ⟨hl, P2, hp, hv, hw, hr, ht⟩ := h2
              exact ⟨hl, P2, hp, hv, hw, hx2 ▸ hr, ht⟩
          · intro _ choice F m
            constructor
            · rintro ⟨hc, P2, hp, hr, ht⟩
              obtain ⟨x, hx, e1, e2, e3⟩ := hcomp choice hc P2 hp F m hr ht
              rcases List.mem_cons.mp hx with e | hx
              · subst e
                exact ⟨_, List.mem_cons_self, e1, e2, e3⟩
              · exact ⟨x.1, List.mem_cons_of_mem _ (List.mem_map_of_mem hx), e1, e2, e3⟩
            · rintro ⟨c', hc', e1, e2, e3⟩
              have hx : ∃ x ∈ (c, st2, occ0) :: rest, x.1 = c' := by
                rcases List.mem_cons.mp hc' with e | hc'
                · exact ⟨_, List.mem_cons_self, e.symm⟩
                · obtain ⟨x, hx, e⟩ := List.mem_map.mp hc'
                  exact ⟨x, List.mem_cons_of_mem _ hx, e⟩
              obtain ⟨x, hx, ex⟩ := hx
              obtain ⟨h1, -, P2, hp, -, -, hr, ht⟩ := hsound x hx
              subst ex
              refine ⟨e1 ▸ h1, P2, e1 ▸ hp, ?_, e2 ▸ ht⟩
              rw [hr]
              simp only [e2, e3]

theorem readUnit_good {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {P : Projection} {b sentence : Nat} {st : DState} {w : Array Tok} {u : SenseUnit} {occ : List SenseOccurrence}
    (h : readUnit D A E L used P b sentence st w = .ok (u, occ)) : UnitGood D A E L used P b st w u := by
  unfold readUnit at h
  split at h
  · cases h
  · rename_i t F m st2 hr
    split at h
    · cases h
    · simp only [Except.ok.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, -⟩ := h
      refine ⟨Or.inl rfl, ?_, fun c hc => (by cases hc), fun e => absurd rfl e⟩
      intro F2 m2 e
      simp only [Option.some.injEq, Prod.mk.injEq] at e
      obtain ⟨rfl, rfl⟩ := e
      exact ⟨rfl, readOne_some hr⟩
  · exact openUnit_good h

/-- The state before unit `j` when the first unit is read from `st`. -/
def stateFrom (st : DState) (units : List SenseUnit) : Nat → DState
  | 0 => st
  | i + 1 =>
    match units[i]? with
    | some u => u.after
    | none => st

theorem stateFrom_init : ∀ (units : List SenseUnit) (j : Nat), stateFrom DState.init units j = stateBefore units j
  | _, 0 => rfl
  | _, _ + 1 => rfl

theorem stateFrom_cons {st : DState} {u : SenseUnit} {us : List SenseUnit} {j : Nat} {v : SenseUnit}
    (h : us[j]? = some v) : stateFrom st (u :: us) (j + 1) = stateFrom u.after us j := by
  cases j with
  | zero => rfl
  | succ j =>
    have : ∃ y, us[j]? = some y := by
      have hl : j + 1 < us.length := (List.getElem?_eq_some_iff.mp h).1
      exact ⟨us[j], List.getElem?_eq_getElem (by omega)⟩
    obtain ⟨y, hy⟩ := this
    simp only [stateFrom, List.getElem?_cons_succ, hy]

theorem readBody_good {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {P : Projection} {b k : Nat} :
    ∀ (ws : List (Array Tok)) (i : Nat) (st : DState) (us : List SenseUnit) (occ : List SenseOccurrence),
    readBody D A E L used P b k i st ws = .ok (us, occ) →
    us.length = ws.length ∧
    ∀ j u, us[j]? = some u → ∃ w, ws[j]? = some w ∧ UnitGood D A E L used P b (stateFrom st us j) w u := by
  intro ws
  induction ws with
  | nil =>
    intro i st us occ h
    simp only [readBody, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, -⟩ := h
    exact ⟨rfl, fun j u h => by simp at h⟩
  | cons w ws ih =>
    intro i st us occ h
    unfold readBody at h
    split at h
    · cases h
    · rename_i u0 occ0 hu
      split at h
      · cases h
      · rename_i us0 occs hb
        simp only [Except.ok.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, -⟩ := h
        obtain ⟨hlen, hall⟩ := ih (i + 1) u0.after us0 occs hb
        refine ⟨by simp [hlen], ?_⟩
        intro j u hj
        cases j with
        | zero =>
          simp only [List.getElem?_cons_zero, Option.some.injEq] at hj
          subst hj
          exact ⟨w, rfl, readUnit_good hu⟩
        | succ j =>
          simp only [List.getElem?_cons_succ] at hj
          obtain ⟨w2, hw2, hg⟩ := hall j u hj
          exact ⟨w2, by simpa using hw2, by rw [stateFrom_cons hj]; exact hg⟩

/-- The facts of an accepted text: its sentences, its preamble, the projection, S2's checks, the body. -/
theorem readWithSenses_ok {D : Dictionary} {E : Env} {L : Lexicon} {b : Nat} {s : String} {units : List SenseUnit}
    {sm : List SenseOccurrence} {mx : List (String × List String)} {un : List String} {P : Projection}
    (h : readWithSenses D E L b s = .ok units sm mx un P) :
    ∃ sents A k, lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
      sents.toList.drop k ≠ [] ∧
      project D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P ∧ grammarFault P = none ∧
      readBody D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) P b k 0 DState.init (sents.toList.drop k) =
        .ok (units, sm) ∧ mx = mixedOf P units ∧
      ((units.filterMap (·.formula)).isEmpty || typedDocument P.env ((units.filterMap (·.formula)).map (·.1))) = true := by
  unfold readWithSenses at h
  split at h
  · cases h
  · split at h
    · cases h
    · rename_i sents hl
      split at h
      · cases h
      · rename_i A k hpre
        split at h
        · cases h
        · rename_i hne
          split at h
          · cases h
          · split at h
            · cases h
            · rename_i P0 hp
              unfold readProjected at h
              split at h
              · cases h
              · rename_i hg
                split at h
                · rename_i o _
                  cases o <;> simp [Stop.outcome] at h
                · rename_i us0 occ0 hb
                  split at h
                  · rename_i ht
                    simp only [SensesOutcome.ok.injEq] at h
                    obtain ⟨rfl, rfl, rfl, -, rfl⟩ := h
                    exact ⟨sents, A, k, hl, hpre, by simpa using hne, hp, hg, hb, rfl, ht⟩
                  · cases h

theorem readBody_resolved {D : Dictionary} {A : Assignment} {E : Env} {L : Lexicon} {used : List String}
    {P : Projection} {b k : Nat} (hG : (grammar P.env P.lexicon).wf = true) :
    ∀ (ws : List (Array Tok)) (i : Nat) (st : DState) (us : List SenseUnit) (occ : List SenseOccurrence),
    readBody D A E L used P b k i st ws = .ok (us, occ) → (∀ u ∈ us, u.candidates = []) →
    ∃ rs st2, us.map (·.formula) = rs.map some ∧
      DocOneReading (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon))
        st (ws.map (·.toList)) rs st2 := by
  intro ws
  induction ws with
  | nil =>
    intro i st us occ h _
    simp only [readBody, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, -⟩ := h
    exact ⟨[], st, rfl, rfl⟩
  | cons w ws ih =>
    intro i st us occ h hres
    unfold readBody at h
    split at h
    · cases h
    · rename_i u0 occ0 hu
      split at h
      · cases h
      · rename_i us0 occs hb
        simp only [Except.ok.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, -⟩ := h
        obtain ⟨h1, h2, -, -⟩ := readUnit_good (P := P) hu
        have hc0 : u0.candidates = [] := hres u0 List.mem_cons_self
        have hf : ∃ F m, u0.formula = some (F, m) := by
          rcases h1 with h1 | h1
          · cases e : u0.formula with
            | none => rw [e] at h1; cases h1
            | some x => exact ⟨x.1, x.2, rfl⟩
          · exact absurd hc0 h1
        obtain ⟨F, m, hF⟩ := hf
        obtain ⟨-, hr⟩ := h2 F m hF
        obtain ⟨rs0, st2, hm, hd⟩ := ih (i + 1) u0.after us0 occs hb (fun u hu => hres u (List.mem_cons_of_mem _ hu))
        refine ⟨(F, m) :: rs0, st2, ?_, ?_⟩
        · simp only [List.map_cons, hF, hm]
        · exact ⟨u0.after, read_sound hG hr, hd⟩

theorem filterMap_of_map_some {α β : Type} {f : α → Option β} :
    ∀ {l : List α} {rs : List β}, l.map f = rs.map some → l.filterMap f = rs
  | [], [], _ => rfl
  | [], _ :: _, h => by cases h
  | _ :: _, [], h => by cases h
  | x :: xs, r :: rs, h => by
    simp only [List.map_cons, List.cons.injEq] at h
    simp only [List.filterMap_cons, h.1, filterMap_of_map_some h.2]

theorem senses_resolved_one_reading : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection),
  readWithSenses D E L b s = .ok units sm mx un P →
  (∀ u ∈ units, u.candidates = []) →
  ∃ sents A k rs st2, lex s = .ok sents ∧
    readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    project D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P ∧
    units.map (·.formula) = rs.map some ∧
    P.lexicon.valid P.env {} = true ∧
    DocOneReading (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon))
      DState.init ((sents.toList.drop k).map (·.toList)) rs st2 ∧
    typedDocument P.env (rs.map (·.1)) = true := by
  intro D E L b s units sm mx un P h hres
  obtain ⟨sents, A, k, hl, hpre, hne, hp, hg, hb, -, ht⟩ := readWithSenses_ok h
  obtain ⟨hv, hw⟩ := grammarFault_none hg
  obtain ⟨rs, st2, hm, hd⟩ := readBody_resolved hw _ _ _ _ _ hb hres
  refine ⟨sents, A, k, rs, st2, hl, hpre, hp, hm, hv, hd, ?_⟩
  have hfm := filterMap_of_map_some hm
  rw [hfm] at ht
  have hlen := (readBody_good _ _ _ _ _ hb).1
  have hrs : rs ≠ [] := by
    intro e
    subst e
    have : units = [] := by
      cases units with
      | nil => rfl
      | cons _ _ => cases hm
    subst this
    exact hne (List.eq_nil_of_length_eq_zero hlen.symm)
  cases rs with
  | nil => exact absurd rfl hrs
  | cons r rs => simpa using ht

theorem senses_unit_sound : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit),
  readWithSenses D E L b s = .ok units sm mx un P →
  units[i]? = some u →
  (u.formula.isSome = true ∨ u.candidates ≠ []) ∧
  ∀ (F : EFormula) (m : Bool), u.formula = some (F, m) →
    u.candidates = [] ∧
    ∃ sents A k w, lex s = .ok sents ∧
      readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
      project D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P ∧
      (sents.toList.drop k)[i]? = some w ∧
      (grammar P.env P.lexicon).wf = true ∧
      readSentence (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon))
        (stateBefore units i) b w = (.ok F m, u.after) := by
  intro D E L b s units sm mx un P i u h hu
  obtain ⟨sents, A, k, hl, hpre, -, hp, hg, hb, -, -⟩ := readWithSenses_ok h
  obtain ⟨-, hall⟩ := readBody_good _ _ _ _ _ hb
  obtain ⟨w, hw, hgood⟩ := hall i u hu
  rw [stateFrom_init] at hgood
  obtain ⟨h1, h2, -, -⟩ := hgood
  refine ⟨h1, fun F m e => ?_⟩
  obtain ⟨hc, hr⟩ := h2 F m e
  exact ⟨hc, sents, A, k, w, hl, hpre, hp, hw, (grammarFault_none hg).2, hr⟩

theorem senses_candidate_sound : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (c : Candidate),
  readWithSenses D E L b s = .ok units sm mx un P →
  units[i]? = some u → c ∈ u.candidates →
  u.formula = none ∧
  ∃ sents A k P2 w,
    lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    project D (A.extend c.choice) E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P2 ∧
    P2.lexicon.valid P2.env {} = true ∧ (grammar P2.env P2.lexicon).wf = true ∧
    c.lines = Assignment.lines D (A.extend c.choice) ∧
    (sents.toList.drop k)[i]? = some w ∧
    readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
      (stateBefore units i) b w = (.ok c.formula c.mark, u.after) ∧
    typedDocument P2.env [c.formula] = true := by
  intro D E L b s units sm mx un P i u c h hu hc
  obtain ⟨sents, A, k, hl, hpre, -, -, -, hb, -, -⟩ := readWithSenses_ok h
  obtain ⟨-, hall⟩ := readBody_good _ _ _ _ _ hb
  obtain ⟨w, hw, hgood⟩ := hall i u hu
  rw [stateFrom_init] at hgood
  obtain ⟨-, -, h3, -⟩ := hgood
  obtain ⟨hn, -, hlines, P2, hp2, hv, hwf, hr, ht⟩ := h3 c hc
  exact ⟨hn, sents, A, k, P2, w, hl, hpre, hp2, hv, hwf, hlines, hw, hr, ht⟩

theorem candidates_complete : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (choice : List (String × Nat)) (F : EFormula) (m : Bool),
  readWithSenses D E L b s = .ok units sm mx un P → units[i]? = some u → u.candidates ≠ [] →
  ((choice ∈ choicesOf D u.unresolved ∧
    ∃ sents A k P2 w,
      lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
      project D (A.extend choice) E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P2 ∧
      (sents.toList.drop k)[i]? = some w ∧
      (readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
        (stateBefore units i) b w).1 = .ok F m ∧
      typedDocument P2.env [F] = true)
   ↔ ∃ c ∈ u.candidates, c.choice = choice ∧ c.formula = F ∧ c.mark = m) := by
  intro D E L b s units sm mx un P i u choice F m h hu hne
  obtain ⟨sents, A, k, hl, hpre, -, -, -, hb, -, -⟩ := readWithSenses_ok h
  obtain ⟨-, hall⟩ := readBody_good _ _ _ _ _ hb
  obtain ⟨w, hw, hgood⟩ := hall i u hu
  rw [stateFrom_init] at hgood
  obtain ⟨-, -, -, h4⟩ := hgood
  rw [← h4 hne choice F m]
  constructor
  · rintro ⟨hc, sents2, A2, k2, P2, w2, hl2, hpre2, hp2, hw2, hr, ht⟩
    rw [hl] at hl2
    cases hl2
    rw [hpre] at hpre2
    cases hpre2
    rw [hw] at hw2
    cases hw2
    exact ⟨hc, P2, hp2, hr, ht⟩
  · rintro ⟨hc, P2, hp2, hr, ht⟩
    exact ⟨hc, sents, A, k, P2, w, hl, hpre, hp2, hw, hr, ht⟩

theorem mixed_exact : ∀ (P : Projection) (units : List SenseUnit) (w : String) (ids : List String),
  (w, ids) ∈ mixedOf P units ↔
    ids = ((units.filterMap (·.formula)).flatMap
             (fun (A, _) => (senseOccurrences P A).filter (P.wordOf · == some w))).eraseDups ∧
    2 ≤ ids.length := by
  intro P units w ids
  unfold mixedOf
  simp only [List.mem_filterMap]
  constructor
  · rintro ⟨w2, -, hw⟩
    split at hw
    · simp only [Option.some.injEq, Prod.mk.injEq] at hw
      obtain ⟨rfl, rfl⟩ := hw
      exact ⟨rfl, by assumption⟩
    · cases hw
  · rintro ⟨rfl, hlen⟩
    refine ⟨w, ?_, by simp only [hlen, if_true]⟩
    obtain ⟨id, hid⟩ : ∃ id, id ∈ ((units.filterMap (·.formula)).flatMap
        (fun (A, _) => (senseOccurrences P A).filter (P.wordOf · == some w))).eraseDups := by
      cases e : ((units.filterMap (·.formula)).flatMap
          (fun (A, _) => (senseOccurrences P A).filter (P.wordOf · == some w))).eraseDups with
      | nil => rw [e] at hlen; simp at hlen
      | cons x _ => exact ⟨x, List.mem_cons_self⟩
    rw [mem_eraseDups_iff] at hid
    simp only [List.mem_flatMap, List.mem_filter, beq_iff_eq] at hid
    obtain ⟨_, -, -, hword⟩ := hid
    unfold Projection.wordOf at hword
    obtain ⟨x, hx, e⟩ := Option.map_eq_some_iff.mp hword
    rw [mem_eraseDups_iff]
    exact List.mem_map.mpr ⟨x, List.mem_of_find?_eq_some hx, e⟩

/-- The statement of spec 5.3 that the sense map of a resolved sentence names exactly the senses its
formula uses. It is checked on the fixtures (s1, s9, s15, n4; s23 for the exclusion) and not proved
(spec 5.4: stated only). -/
def senseMap_ids : Prop := ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (F : EFormula) (m : Bool),
  readWithSenses D E L b s = .ok units sm mx un P → units[i]? = some u → u.formula = some (F, m) →
  ∃ sents A k, lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    ∀ id, id ∈ (sm.filter (fun o => o.sentence == k + i && o.candidate.isNone)).map (·.symbol)
          ↔ id ∈ senseOccurrences P F

end VE.Senses
