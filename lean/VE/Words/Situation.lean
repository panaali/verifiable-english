import VE.EnglishGrammar.Lexicon
import VE.EnglishGrammar.Encode
import VE.EnglishGrammar.Policy
import VE.Norms.Wire
import VE.Finite
import VE.Bridge

/-! Situations and point clauses in English, filled from the request's validated lexicon (docs/spec/question-answering.md
3.3; plan 4.5, D10, Q2.3, Q2.4). This module is the one owner of these lines: `ve ask`'s answers (`VE.Ask.Render`)
and, through the `words` service mode (`VE.Words.Run`), the readings and norm-defaults English that Python used to
word itself (`readings_s2_wording.situation`'s base part, `readings_route.situation_text`'s base part,
`norm_defaults_english.point_clause`, `_negative_modal` and `filling_sentence`, `readings_s2_english.gap_sentences`
and `norm_english.pair_sentence`, all deleted in Q2.4).

The templates are the lexicon's selected wordings (V1 to V6 validated them), each `{i}` hole filled with an element's
name. A situation lists the elements by sort, then the true facts of the shown predicates, each list sorted, then the
caller's own trailing lines (the soft and rights suppositions, which stay Python's, plan 4.5), joined by `; `, or
`nothing exists` (`situationText`). A point clause is a regulated predicate's act with its modal, `may`/`must` or
`must not`/`need not`, at a tuple, or a plain predicate's wording (`clauseAt`); a filling sentence says what a
situation answers to a silence (`fillingSentence`); a generic clause fills each hole with an indefinite noun phrase
(`genericClause`); the pair sentence is norm-defaults 4.1's (`pairSentence`).

No correctness theorem beyond its `#guard`s (plan 4.7): every line `ve ask` shows passes W7's all-derivations gate
(`VE.Ask.Render`), and the lines the readings and norm-defaults English shows pass those routes' own gates. -/

namespace VE.Words
open VE.EnglishGrammar
open Lean

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

/-- `a` or `an` by the noun's first letter (the pair and generic clauses' indefinite noun phrases). -/
def article (noun : String) : String :=
  match noun.toList.head? with
  | some c => if "aeiouAEIOU".toList.contains c then "an" else "a"
  | none => "a"

/-- `a` or `an` by the sound of the noun's first letters (`a user`, `an agent`, `an hour`): an element line's
    article, as Python's readings renderer chose it. -/
def articleBySound (noun : String) : String :=
  let w := pyLower noun
  if ["uni", "use", "usu", "uti", "eu", "one", "once"].any w.startsWith then "a"
  else if ["hour", "honest", "honour", "heir"].any w.startsWith then "an"
  else match w.toList.head? with
    | some c => if "aeiou".toList.contains c then "an" else "a"
    | none => "an"

def sortedStrings (l : List String) : List String := l.mergeSort (fun a b => decide (a ≤ b))

/-- Lexicographic order on rows of names. -/
def rowLe (a b : List String) : Bool := decide (a ≤ b)

/-- A constant's name in English: its own verbalisation in the environment, else its lexicon spelling, else the
    constant itself. -/
def constantName (E : Env) (L : Lexicon) (c : String) : String :=
  let own := (((E.source.getObjValD "vocabulary").getObjValD "constants").getObjValD c).getObjValD "verbalisation"
  match own with
  | .str v => if v.isEmpty then (L.spellings.lookup c).getD c else v
  | _ => (L.spellings.lookup c).getD c

/-- An element's name: the name of the first constant, in name order, that denotes it; else its id. -/
def nameOf {α : Type} [BEq α] (E : Env) (L : Lexicon) (consts : List (String × α)) (id : α → String) (v : α) :
    String :=
  match (consts.mergeSort (fun a b => decide (a.1 ≤ b.1))).find? (·.2 == v) with
  | some (c, _) => constantName E L c
  | none => id v

/-- `<name> is a/an <noun>`. -/
def elementLine (noun name : String) : String := name ++ " is " ++ articleBySound noun ++ " " ++ noun

/-- A situation's text: for each `(sort, noun, names)` (sorts sorted) each name's element line (names sorted), then
    for each `(predicate, wording, rows)` (predicates sorted) each row's fact (rows sorted), then `extra`, joined by
    `; `; `nothing exists` when there is no line. -/
def situationText (elements : List (String × String × List String))
    (facts : List (String × String × List (List String))) (extra : List String) : String :=
  let es := (elements.mergeSort (fun a b => decide (a.1 ≤ b.1))).flatMap fun (_, noun, names) =>
    (sortedStrings names).map (elementLine noun)
  let fs := (facts.mergeSort (fun a b => decide (a.1 ≤ b.1))).flatMap fun (_, w, rows) =>
    (rows.mergeSort rowLe).map (fill w)
  let all := es ++ fs ++ extra
  if all.isEmpty then "nothing exists" else "; ".intercalate all

/-- The author's base predicates: declared and not regulated (no modal reading). -/
def authorPredicates (E : Env) : List String :=
  sortedStrings ((E.predicates.filter fun p => !p.modal).map (·.name))

/-- The situation of a checked model (`ve ask`): the elements of every declared sort with a noun, named by `nameOf`,
    then the true facts of the author's base predicates. -/
def situation (E : Env) (L : Lexicon) (M : VE.FiniteModel VE.Bridge.Entity) : String :=
  let consts := L.spellings.filterMap fun (c, _) => (M.constants c).map (c, ·)
  let name := nameOf E L consts Prod.snd
  situationText
    (E.sorts.filterMap fun s => (L.nouns.lookup s.name).map fun noun => (s.name, noun, (M.domains s.name).map name))
    ((authorPredicates E).filterMap fun p => (L.wordings.lookup p).map fun w => (p, w, (M.relations p).map (·.map name)))
    []

/-- A predicate's `regulated` declaration in the environment (an `unspecified` default read as its placeholder). -/
def regulatedOf (E : Env) (p : String) : Option VE.Norms.Regulated := do
  let d ← E.predicate? p
  let entry := placeholderEntry (((E.source.getObjValD "vocabulary").getObjValD "predicates").getObjValD p)
  let raw ← (entry.getObjVal? "regulated").toOption
  (VE.Norms.Wire.decodeRegulated p d.args raw).toOption

/-- A regulated predicate's clause at named arguments: a plain predicate's wording; else its act with `may` or `must`
    where `value` holds, `must not` (a permission) or `need not` (an obligation) where it does not. -/
def clauseAt (E : Env) (L : Lexicon) (p : String) (names : List String) (value : Bool) : Option String := do
  let r ← regulatedOf E p
  match r.role with
  | .plain => (L.wordings.lookup p).map (fill · names)
  | role =>
    let act ← r.act
    let modal := if value then (if role == .permission then "may" else "must")
      else (if role == .permission then "must not" else "need not")
    pure (fill (replaceFirst act "{0} " ("{0} " ++ modal ++ " ")) names)

/-- A regulated predicate's positive clause at a model's tuple. -/
def pointClause (E : Env) (L : Lexicon) (M : VE.FiniteModel VE.Bridge.Entity) (p : String)
    (vs : List VE.Bridge.Entity) : Option String :=
  let consts := L.spellings.filterMap fun (c, _) => (M.constants c).map (c, ·)
  clauseAt E L p (vs.map (nameOf E L consts Prod.snd)) true

/-- `Here the text does not say whether <clause>; this situation answers 'yes'` (or `'no'`). -/
def fillingSentence (clause : String) (answer : Bool) : String :=
  "Here the text does not say whether " ++ clause ++ "; this situation answers '" ++
    (if answer then "yes" else "no") ++ "'."

/-- A predicate's wording with each hole an indefinite noun phrase of its argument's sort (C2). -/
def genericClause (E : Env) (L : Lexicon) (p : String) : Option String := do
  let decl ← E.predicate? p
  let w ← L.wordings.lookup p
  let nouns ← decl.args.mapM fun s => L.nouns.lookup s
  pure (fill w (nouns.map fun n => article n ++ " " ++ n))

/-- Each argument's noun phrase and its later reference (norm-defaults 4.1): `noun` and `that noun` for a sort that
    occurs once; `first noun`/`second noun` and `the first noun`/`the second noun` for one that occurs twice; none
    for a sort that occurs more often. -/
def bindings (L : Lexicon) (args : List String) : Option (List (String × String)) :=
  (List.range args.length).zip args |>.mapM fun (i, s) => do
    let noun ← L.nouns.lookup s
    let count := args.count s
    if count == 1 then pure (noun, "that " ++ noun)
    else if count == 2 then
      let shown := (if (args.take i).count s == 0 then "first " else "second ") ++ noun
      pure (shown, "the " ++ shown)
    else none

/-- `Whenever a <noun> must <act>, it may <act>.` (norm-defaults 4.1): the pair premise of an obligation that declares
    its permission, worded by the obligation's act; the first argument is `it` after the comma and every other
    argument its reference. -/
def pairSentence (E : Env) (L : Lexicon) (req : String) : Option String := do
  let decl ← E.predicate? req
  let r ← regulatedOf E req
  let _ ← r.permission
  let act ← r.act
  let parts ← bindings L decl.args
  let must := fill (replaceFirst act "{0} " "{0} must ") (parts.map fun (n, _) => article n ++ " " ++ n)
  let may := fill (replaceFirst act "{0} " "{0} may ") ("it" :: (parts.map (·.2)).drop 1)
  pure ("Whenever " ++ must ++ ", " ++ may ++ ".")

#guard fill "{0} is registered" ["Ann"] = "Ann is registered"
#guard fill "{0} compel {1} to belong to an association" ["a", "b"] = "a compel b to belong to an association"
#guard fill "{2} stays" ["a"] = "{2} stays"
#guard article "action" = "an" ∧ article "member" = "a"
#guard articleBySound "user" = "a" ∧ articleBySound "hour" = "an" ∧ articleBySound "agent" = "an" ∧
  articleBySound "member" = "a" ∧ articleBySound "Agent" = "an" ∧ articleBySound "" = "an"
#guard elementLine "member" "e0" = "e0 is a member"
#guard elementLine "user" "u" = "u is a user"
#guard situationText [("person", "person", ["b", "a"])] [("p", "{0} is late", [["b"], ["a"]])] ["suppose x"] =
  "a is a person; b is a person; a is late; b is late; suppose x"
#guard situationText [] [] [] = "nothing exists"
#guard fillingSentence "e0 must be spared exclusion from education" false =
  "Here the text does not say whether e0 must be spared exclusion from education; this situation answers 'no'."
#guard fillingSentence "Sol may generate it" true =
  "Here the text does not say whether Sol may generate it; this situation answers 'yes'."
/-- A lexicon of nouns only, for the guards. -/
def nounsOnly (nouns : List (String × String)) : Lexicon :=
  { nouns, letters := [], wordings := [], negatives := [], aliases := [], spellings := [] }

#guard bindings (nounsOnly [("state", "state"), ("person", "person")]) ["state", "person"] =
  some [("state", "that state"), ("person", "that person")]
#guard bindings (nounsOnly [("person", "person")]) ["person", "person"] =
  some [("first person", "the first person"), ("second person", "the second person")]
#guard bindings (nounsOnly [("person", "person")]) ["person", "person", "person"] = none

end VE.Words
