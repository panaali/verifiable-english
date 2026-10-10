import VE.EnglishGrammar.Lexicon
import VE.Finite
import VE.Bridge

/-! Situations and point clauses in English, filled from the request's validated lexicon (docs/spec/question-answering.md
3.3; plan 4.5, D10, Q2.3).

The templates are the lexicon's selected wordings (V1 to V6 validated them), each `{i}` hole filled with an element's
name: the spelling of a constant that denotes the element (constants in name order), else the element's id
(`elementName`, as Python's `element_name`). A situation lists the elements by sort, then the true facts of the
author's base predicates (not the regulated ones, not a filling, not a generated name), each list sorted, joined by
`; `, or `nothing exists` (`situation`). A point clause is a regulated predicate's modal wording at a tuple
(`pointClause`); a generic clause fills each hole with an indefinite noun phrase (`genericClause`); the pair sentence
is norm-defaults 4.1's (`pairSentence`).

No correctness theorem beyond its `#guard`s (plan 4.7): every line these functions make is shown only after W7's
all-derivations gate (`VE.Ask.Render`). Q2.4 moves Python's producers of the same lines onto this module. -/

namespace VE.Words
open VE.EnglishGrammar

/-- `{d}` holes (one decimal digit) filled with `args[d]`, in one pass; a hole with no argument is kept. -/
def fillChars (args : List String) : List Char → List Char
  | '{' :: d :: '}' :: rest =>
    if d.isDigit then
      match args[d.toNat - '0'.toNat]? with
      | some a => a.toList ++ fillChars args rest
      | none => '{' :: d :: '}' :: fillChars args rest
    else '{' :: fillChars args (d :: '}' :: rest)
  | c :: rest => c :: fillChars args rest
  | [] => []

def fill (template : String) (args : List String) : String := String.mk (fillChars args template.toList)

/-- `a` or `an` by the noun's first letter. -/
def article (noun : String) : String :=
  match noun.toList.head? with
  | some c => if "aeiouAEIOU".toList.contains c then "an" else "a"
  | none => "a"

/-- An element's name: the spelling of the first constant, in name order, that denotes it; else its id. -/
def elementName (L : Lexicon) (M : VE.FiniteModel VE.Bridge.Entity) (v : VE.Bridge.Entity) : String :=
  let byName := L.spellings.mergeSort (fun a b => decide (a.1 ≤ b.1))
  match byName.find? (fun (c, _) => M.constants c == some v) with
  | some (_, spelling) => spelling
  | none => v.2

def sortedStrings (l : List String) : List String := l.mergeSort (fun a b => decide (a ≤ b))

/-- `<name> is a/an <noun>`. -/
def elementLine (noun name : String) : String := name ++ " is " ++ article noun ++ " " ++ noun

/-- A true base atom by its wording, the element names in its holes. -/
def factLine (L : Lexicon) (M : VE.FiniteModel VE.Bridge.Entity) (p : String) (row : List VE.Bridge.Entity) :
    Option String :=
  (L.wordings.lookup p).map fun w => fill w (row.map (elementName L M))

/-- Lexicographic order on rows of names. -/
def rowLe (a b : List String) : Bool := decide (a ≤ b)

/-- The author's base predicates: declared and not regulated (no modal reading). -/
def authorPredicates (E : Env) : List String :=
  sortedStrings ((E.predicates.filter fun p => !p.modal).map (·.name))

/-- The elements by sort (sorted sorts, each sort's names sorted), then the true author facts (sorted predicates,
    rows sorted), joined by `; `; `nothing exists` when empty. -/
def situation (E : Env) (L : Lexicon) (M : VE.FiniteModel VE.Bridge.Entity) : String :=
  let elements := (sortedStrings (E.sorts.map (·.name))).flatMap fun s =>
    match L.nouns.lookup s with
    | some noun => (sortedStrings ((M.domains s).map (elementName L M))).map (elementLine noun)
    | none => []
  let facts := (authorPredicates E).flatMap fun p =>
    ((M.relations p).map (fun row => row.map (elementName L M))).mergeSort rowLe |>.filterMap fun names =>
      (L.wordings.lookup p).map (fill · names)
  let all := elements ++ facts
  if all.isEmpty then "nothing exists" else "; ".intercalate all

/-- A regulated predicate's modal wording at a tuple (`<subject> may/must <act>`), or a plain predicate's wording. -/
def pointClause (L : Lexicon) (M : VE.FiniteModel VE.Bridge.Entity) (p : String) (vs : List VE.Bridge.Entity) :
    Option String :=
  (L.wordings.lookup p).map fun w => fill w (vs.map (elementName L M))

/-- A point clause with the tuple's ids (`gapsOf` names tuples by id). -/
def pointClauseIds (L : Lexicon) (M : VE.FiniteModel VE.Bridge.Entity) (p : String) (sorts ids : List String) :
    Option String :=
  pointClause L M p (sorts.zip ids)

/-- `Here the text does not say whether <clause>; this situation answers 'no'.` (S3). -/
def fillingSentence (clause : String) : String :=
  "Here the text does not say whether " ++ clause ++ "; this situation answers 'no'."

/-- A predicate's wording with each hole an indefinite noun phrase of its argument's sort (C2). -/
def genericClause (E : Env) (L : Lexicon) (p : String) : Option String := do
  let decl ← E.predicate? p
  let w ← L.wordings.lookup p
  let nouns ← decl.args.mapM fun s => L.nouns.lookup s
  pure (fill w (nouns.map fun n => article n ++ " " ++ n))

/-- The act of a modal wording: the text after `{0} must ` or `{0} may `. -/
def actOf (w : String) : Option String :=
  if w.startsWith "{0} must " then some (w.drop 9)
  else if w.startsWith "{0} may " then some (w.drop 8)
  else none

/-- `Whenever a <noun> must <act>, it may <act>.` (norm-defaults 4.1), for a pair of one-place predicates. -/
def pairSentence (E : Env) (L : Lexicon) (req perm : String) : Option String := do
  let decl ← E.predicate? req
  let s ← decl.args.head?
  let noun ← L.nouns.lookup s
  let r ← actOf (← L.wordings.lookup req)
  let m ← actOf (← L.wordings.lookup perm)
  pure ("Whenever " ++ article noun ++ " " ++ noun ++ " must " ++ r ++ ", it may " ++ m ++ ".")

#guard fill "{0} is registered" ["Ann"] = "Ann is registered"
#guard fill "{0} compel {1} to belong to an association" ["a", "b"] = "a compel b to belong to an association"
#guard fill "{2} stays" ["a"] = "{2} stays"
#guard article "action" = "an" ∧ article "member" = "a"
#guard elementLine "member" "e0" = "e0 is a member"
#guard fillingSentence "e0 must be spared exclusion from education" =
  "Here the text does not say whether e0 must be spared exclusion from education; this situation answers 'no'."
#guard actOf "{0} must be reported to the user" = some "be reported to the user"
#guard actOf "{0} may be performed" = some "be performed"

end VE.Words
