/-! Undeclared evaluative words (`judgments@0`, docs/spec/judgment-terms.md 7; plan D15, JT-3).

A catalogue row names an evaluative word and the phrases in which the word has another sense. The rows themselves
are english-lean's (`VE.EnglishGrammar.evaluativeRows`, its single catalogue); senses owns the numbered senses and
their `sense__<word>_<n>` projection (synthesis round 2, edit 3), so a row carries no sense of its own.
`undeclaredEvaluative` lists the base predicates whose words match a row and that are not bound. It says only "these
words match the catalogue; review them": it is never a refusal, and it never claims that a unit uses no other
judgment. -/

namespace VE.Judgments

/-- One catalogue row for an evaluative word, tied to its evaluative sense: the word, and the phrases in which it
    has another sense. JT-3 reads the rows from english-lean's single catalogue; there is no second list. -/
structure EvaluativeRow where
  word        : String
  otherSenses : List (List String)
  deriving DecidableEq, Repr

def hasPhrase (ph ws : List String) : Bool :=
  (List.range (ws.length + 1)).any fun i => (ws.drop i).take ph.length == ph

def EvaluativeRow.matches (row : EvaluativeRow) (ws : List String) : Bool :=
  ws.contains row.word && !row.otherSenses.any (hasPhrase · ws)

/-- The base predicates whose words match a row and that are not bound, in declaration order. `preds` is every
    predicate of the base environment `baseEnv E defs` (W3-defined names excluded, regulated predicates included),
    each with its words (its name split at `_`, then its template's words, lower case), read by Lean from the
    environment. -/
def undeclaredEvaluative (rows : List EvaluativeRow) (preds : List (String × List String)) (J : List String) :
    List String :=
  (preds.filter fun (p, ws) => !J.contains p && rows.any (·.matches ws)).map (·.1)

/-- A predicate's words: its name split at `_`, then its template's words (split at every character that is not a
    letter or a digit), lower case. -/
def predicateWords (name : String) (template : Option String) : List String :=
  name.toLower.splitOn "_" ++
    ((template.map fun t => (t.toLower.split fun c => !c.isAlphanum).filter (· ≠ "")).getD [])

theorem hasPhrase_iff (ph ws : List String) : hasPhrase ph ws = true ↔ ph <:+: ws := by
  simp only [hasPhrase, List.any_eq_true, List.mem_range, beq_iff_eq]
  constructor
  · rintro ⟨i, -, h⟩
    have hp : ph <+: ws.drop i := List.prefix_iff_eq_take.mpr h.symm
    exact hp.isInfix.trans (List.drop_suffix i ws).isInfix
  · rintro ⟨s, t, rfl⟩
    refine ⟨s.length, by simp; omega, ?_⟩
    simp [List.append_assoc]

theorem undeclaredEvaluative_iff (rows preds J p) :
    p ∈ undeclaredEvaluative rows preds J ↔
      ∃ ws, (p, ws) ∈ preds ∧ p ∉ J ∧ ∃ row ∈ rows, row.word ∈ ws ∧ ∀ ph ∈ row.otherSenses, ¬ ph <:+: ws := by
  simp only [undeclaredEvaluative, List.mem_map, List.mem_filter, Bool.and_eq_true, Bool.not_eq_true',
    List.any_eq_true, EvaluativeRow.matches, List.contains_iff_mem, List.any_eq_false, hasPhrase_iff]
  have hc : ∀ q, J.contains q = false ↔ q ∉ J := fun q => by simp
  constructor
  · rintro ⟨⟨q, ws⟩, ⟨hm, hJ, row, hr, hw, ho⟩, rfl⟩
    exact ⟨ws, hm, (hc q).mp hJ, row, hr, hw, fun ph h => by simpa using ho ph h⟩
  · rintro ⟨ws, hm, hJ, row, hr, hw, ho⟩
    exact ⟨(p, ws), ⟨hm, (hc p).mpr hJ, row, hr, hw, fun ph h => by simpa using ho ph h⟩, rfl⟩

end VE.Judgments
