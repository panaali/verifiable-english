import VE.Question.Read

/-! The auxiliary of F2 is not moved out of a clause (DRI ruling of 2026-10-09 on the Q1 reviews, B: G11).

English fronts the main clause's auxiliary, never one inside a relative clause: `Is every member who is registered
eligible?` asks about `every member who is registered is eligible.`, but `Is every member who registered is
eligible?` (G11) puts the word back after `who`, and no English reader hears that question. `readQuestion` reads
both (spec 3.1, plan 4.9), and its fifteen statements are about that reading; `ask` is the outcome the mode shows.

A *clause* of a derivation is a constituent that a `who`, `that` or `which` of its parent's rule begins: the
constituent right after that word, or, when the word is followed by words of the rule itself, the rest of the
rule. An F2 candidate is *moved out* when its put-back word is inside a clause of its one derivation; one with no
single derivation, or whose put-back word is not one of its tokens, counts as moved out, so nothing unchecked is
shown. Such a question is refused, with the questions VE does read in its place (`movedRephrasings`). Every
rephrasing `ask` offers is itself shown as one reading (`askable_iff`, `ask_rephrasings`).
-/

namespace VE.Question
open Lean VE.EnglishGrammar VE.Grammar

/-- The words that begin a clause. -/
def clauseWords : List String := ["who", "that", "which"]

def isClauseWord : Tok → Bool
  | .word t _ => clauseWords.contains (fold t)
  | _ => false

mutual
/-- The number of tokens a tree reads. -/
def width : Tree Tok → Nat
  | .leaf _ => 1
  | .node _ kids => widths kids

def widths : List (Tree Tok) → Nat
  | [] => 0
  | t :: ts => width t + widths ts
end

mutual
/-- The token spans `[a, b)` of the clauses of a tree whose first token is token `start` of `w`. -/
def clauses (w : Array Tok) (start : Nat) : Tree Tok → List (Nat × Nat)
  | .leaf _ => []
  | .node _ kids => kidClauses w start (start + widths kids) start kids

/-- The clauses of the children of a node that reads tokens `[first, stop)`, from the child at token `pos`. A child
    right after a clause word of the node is a clause; a word there continues the clause to the node's end. -/
def kidClauses (w : Array Tok) (first stop pos : Nat) : List (Tree Tok) → List (Nat × Nat)
  | [] => []
  | t :: ts =>
    let next := pos + width t
    let opened := decide (first < pos) && ((w[pos - 1]?).map isClauseWord).getD false
    let here := if opened then [match t with | .leaf _ => (pos, stop) | .node .. => (pos, next)] else []
    here ++ clauses w pos t ++ kidClauses w first stop next ts
end

/-- The index of the token of a sentence that starts at byte `g`. -/
def tokenAt (toks : Array Spanned) (g : Nat) : Option Nat :=
  (List.range toks.size).find? fun i => (toks[i]?.map (·.2.1)) == some g

/-- Whether token `k` of `w` is inside a clause of `t`. -/
def inClause (w : Array Tok) (t : Tree Tok) (k : Nat) : Bool :=
  (clauses w 0 t).any fun (a, b) => decide (a ≤ k ∧ k < b)

/-- The one derivation of a one-sentence text with its tokens, or none. -/
def oneTree (E : Env) (L : Lexicon) (b : Nat) (s : String) : Option (Array Spanned × Tree Tok) :=
  match lexSpans s with
  | .ok ss => if ss.size != 1 then none else match ss[0]? with
    | some toks => match verdict (grammar E L) b (toks.map (·.1)) with
      | some (.one t) => some (toks, t)
      | _ => none
    | none => none
  | .error _ => none

/-- Whether a candidate's put-back auxiliary is inside a clause of its one derivation (or cannot be placed). -/
def movedOut (E : Env) (L : Lexicon) (b : Nat) (c : Candidate) : Bool :=
  match c.form with
  | .caseThat => false
  | .fronted _ g =>
    match oneTree E L b c.sentence with
    | some (toks, t) => match tokenAt toks g with
      | some k => inClause (toks.map (·.1)) t k
      | none => true
    | none => true

/-- Whether VE shows `q` as one reading: `readQuestion` reads it, and not with a moved-out word. -/
def askable (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) : Bool :=
  match readQuestion auxs E O L b q with
  | .one c _ => !movedOut E L b c
  | _ => false

/-- The question that fronts token `j` of a sentence (its auxiliary `a` and the space after it removed). -/
def frontedFrom (a s : String) (toks : Array Spanned) (j : Nat) : Option String := do
  let (_, x, y) ← toks[j]?
  pure (capitalise a ++ " " ++ s.extract ⟨0⟩ ⟨x⟩ ++ s.extract ⟨y + 1⟩ ⟨s.utf8ByteSize - 1⟩ ++ "?")

/-- In place of a moved-out candidate: its sentence with the same auxiliary fronted from each other place outside
    every clause, then F1's question of the sentence; those VE shows as one reading, each meaning once. -/
def movedRephrasings (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (c : Candidate) :
    List String :=
  let fronted := match c.form, oneTree E L b c.sentence with
    | .fronted a g, some (toks, t) =>
      let w := toks.map (·.1)
      (List.range toks.size).filterMap fun j =>
        if (toks[j]?.map (·.2.1)) != some g && w[j]? == some (.word a false) && !inClause w t j && j != 0
        then frontedFrom a c.sentence toks j else none
    | _, _ => []
  offered auxs E O L b ((fronted ++ [caseThatQuestion c]).filter (askable auxs E O L b))

/-- What the mode shows for a question: `readQuestion`'s outcome, or a refused moved-out reading. -/
inductive Asked
  | read (o : Outcome)
  | moved (c : Candidate) (rephrasings : List String)

/-- `readQuestion`, with a moved-out reading refused and every F2 rephrasing one VE shows. An indefinite question
    none of whose rephrasings VE shows is the `none` it was before the rephrasings were tried. -/
def ask (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) : Asked :=
  match readQuestion auxs E O L b q with
  | .one c φ => if movedOut E L b c then .moved c (movedRephrasings auxs E O L b c) else .read (.one c φ)
  | .indefinite art rs =>
    match rs.filter (askable auxs E O L b) with
    | [] => .read (classify auxs E O L b q)
    | rs' => .read (.indefinite art rs')
  | o => .read o

/-! ## Statements -/

theorem offeredFold_mem (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (qs : List String)
    (acc : List (String × EFormula)) (x : String × EFormula)
    (hx : x ∈ qs.foldl (fun (acc : List (String × EFormula)) r => match classify auxs E O L b r with
        | .one _ φ => if acc.any (·.2 == φ) then acc else acc ++ [(r, φ)]
        | _ => acc) acc) : x ∈ acc ∨ x.1 ∈ qs := by
  induction qs generalizing acc with
  | nil => exact .inl hx
  | cons q qs ih =>
    rcases ih _ hx with h | h
    · dsimp only at h
      split at h
      · split at h
        · exact .inl h
        · rcases List.mem_append.mp h with h | h
          · exact .inl h
          · simp at h; subst h; exact .inr (List.mem_cons_self ..)
      · exact .inl h
    · exact .inr (List.mem_cons_of_mem _ h)

theorem offered_mem (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (qs : List String)
    (r : String) (h : r ∈ offered auxs E O L b qs) : r ∈ qs := by
  unfold offered at h
  obtain ⟨⟨r', φ⟩, hm, rfl⟩ := List.mem_map.mp h
  rcases offeredFold_mem auxs E O L b qs [] _ hm with h | h
  · simp at h
  · exact h

theorem classify_not_indefinite (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q art : String)
    (rs : List String) : classify auxs E O L b q ≠ .indefinite art rs := by
  intro h
  unfold classify at h
  dsimp only at h
  repeat (split at h <;> try cases h)

theorem readQuestion_indefinite_classify (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (q : String) (art : String) (rs : List String) (h : readQuestion auxs E O L b q = .indefinite art rs) :
    ∃ cl, classify auxs E O L b q = .none cl := by
  unfold readQuestion at h
  generalize hc : classify auxs E O L b q = o at h
  cases o
  case none cl => exact ⟨cl, rfl⟩
  case indefinite a r => exact absurd hc (classify_not_indefinite auxs E O L b q a r)
  all_goals cases h

/-- A shown reading is `readQuestion`'s, so the fifteen statements of spec 5.1 hold of it, and its word is not
    moved out of a clause. -/
theorem ask_one (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate)
    (φ : EFormula) (h : ask auxs E O L b q = .read (.one c φ)) :
    readQuestion auxs E O L b q = .one c φ ∧ movedOut E L b c = false := by
  unfold ask at h
  generalize hr : readQuestion auxs E O L b q = r at h
  cases r <;> dsimp only at h
  case one c' φ' =>
    by_cases hm : movedOut E L b c' = true
    · rw [if_pos hm] at h; cases h
    · rw [if_neg hm] at h
      cases h
      exact ⟨by first | rfl | exact hr, by simpa using hm⟩
  case indefinite art rs =>
    obtain ⟨cl, hc⟩ := readQuestion_indefinite_classify auxs E O L b q art rs hr
    split at h
    · rw [hc] at h; cases h
    · cases h
  all_goals cases h

/-- Every question VE offers in place of a moved-out one is shown as one reading. -/
theorem ask_moved (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate)
    (rs : List String) (h : ask auxs E O L b q = .moved c rs) :
    (∃ φ, readQuestion auxs E O L b q = .one c φ) ∧ movedOut E L b c = true ∧
      ∀ r ∈ rs, askable auxs E O L b r = true := by
  unfold ask at h
  generalize hr : readQuestion auxs E O L b q = r at h
  cases r <;> dsimp only at h
  case one c' φ =>
    by_cases hm : movedOut E L b c' = true
    · rw [if_pos hm] at h
      cases h
      refine ⟨⟨φ, by first | rfl | exact hr⟩, hm, fun r hr' => ?_⟩
      unfold movedRephrasings at hr'
      exact (List.mem_filter.mp (offered_mem _ _ _ _ _ _ _ hr')).2
    · rw [if_neg hm] at h; cases h
  case indefinite art rs =>
    split at h <;> cases h
  all_goals cases h

/-- Every F2 rephrasing of an indefinite question VE shows is shown as one reading. -/
theorem ask_rephrasings (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q art : String)
    (rs : List String) (h : ask auxs E O L b q = .read (.indefinite art rs)) :
    ∀ r ∈ rs, askable auxs E O L b r = true := by
  unfold ask at h
  generalize hr : readQuestion auxs E O L b q = r at h
  cases r <;> dsimp only at h
  case one c' φ =>
    by_cases hm : movedOut E L b c' = true
    · rw [if_pos hm] at h; cases h
    · rw [if_neg hm] at h; cases h
  case indefinite art' rs' =>
    obtain ⟨cl, hc⟩ := readQuestion_indefinite_classify auxs E O L b q art' rs' hr
    generalize hf : rs'.filter (askable auxs E O L b) = f at h
    cases f with
    | nil => rw [hc] at h; cases h
    | cons x xs =>
      cases h
      intro r hr'
      have : r ∈ rs'.filter (askable auxs E O L b) := by rw [hf]; exact hr'
      exact (List.mem_filter.mp this).2
  all_goals cases h

/-- `askable` is exactly: the mode shows the question as one reading. -/
theorem askable_iff (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) :
    askable auxs E O L b q = true ↔ ∃ c φ, ask auxs E O L b q = .read (.one c φ) := by
  constructor
  · intro h
    unfold askable at h
    generalize hr : readQuestion auxs E O L b q = r at h
    cases r
    case one c φ =>
      refine ⟨c, φ, ?_⟩
      unfold ask
      rw [hr]
      simp only
      rw [if_neg (by simpa using h)]
    all_goals cases h
  · rintro ⟨c, φ, h⟩
    obtain ⟨hr, hm⟩ := ask_one auxs E O L b q c φ h
    unfold askable
    rw [hr]
    dsimp only
    rw [hm]
    rfl

end VE.Question
