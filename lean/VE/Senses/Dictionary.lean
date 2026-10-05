import VE.EnglishGrammar.Lexicon

/-! The dictionary of senses (docs/spec/senses.md 2.1 to 2.3, 4.2 and 5.2; batch B1).

A sense is one numbered meaning of a word: its gloss, its description, the kinds it applies to and its
wording. A pack declares senses and the sorts they apply to; a document may add its own senses. The
forms of a sense (2.3) are computed from its wording, part by part: the bare forms (the wording and the
bare negative) and the decorated forms (the glossed form `word (meaning gloss)` and the two comma forms
`word, in the sense of gloss` with and without the closing comma, of the wording and of the negative).

`Dictionary.failures D docSorts` lists every failed condition W1 to W7 of 2.2 as (condition, word or pack
or kind, detail), in the order of the table and, within a row, in the order written; the detail is the
English text of 4.2. `Dictionary.wf` holds exactly when that list is empty (`wf_iff_no_failure`).
`wordingKey`, `negativeTemplate`, `shapeOk`, `noHole` and `sentenceTokens` are S1's and S2's, called.
-/

namespace VE.Senses
open VE.EnglishGrammar

structure Sense where
  word : String
  /-- 1-based within the word; never displayed. -/
  index : Nat
  /-- One to three words. -/
  gloss : String
  /-- Displayed, never parsed. -/
  description : String
  /-- One or two argument sorts, in order. -/
  kinds : List String
  wording : String
  /-- Only where `negativeTemplate` gives none (W5). -/
  negative : Option String := none
  deriving DecidableEq, Repr

structure PackSort where
  name : String
  noun : String
  plural : String
  description : String
  /-- One capital ASCII letter (W4). -/
  letter : String
  deriving DecidableEq, Repr

structure Pack where
  name : String
  sorts : List PackSort
  senses : List Sense
  deriving Repr

structure Dictionary where
  packs : List Pack
  own : List Sense
  deriving Repr

/-- The words no sense may take (D13): Python's `_RESERVED` (`ve/english.py`, `_LOGICAL_WORDS` of
`ve/printer.py` with `_EXTRA_RESERVED` and the ordinals), then `means`, `meaning` and `document`.
`tests/test_senses_lean.py` checks it against Python's set. -/
def reservedWords : List String :=
  ("all any every some each no none not never neither nor and or both either if then unless except " ++
   "without only exists forall implies true false equal equals there such that case condition for at " ++
   "least most exactly does do must may can cannot should shall will would whenever when iff otherwise " ++
   "always sometimes one two three four five six seven eight nine ten a an the lacks nothing nobody " ++
   "everything everybody just solely many several another but plus few might " ++
   "this it holds impossible classified recorded relation entity sort named first second following hold " ++
   "who where step steps source destination from reachable using starting ending definition end " ++
   "therefore so hence third fourth fifth sixth seventh eighth " ++
   "means meaning document").splitOn " "

/-- Python's schema names `RESERVED` (`ve/environment.py`), which W4 refuses as sort names. -/
def schemaReserved : List String :=
  "true false is equals not and or if then for every there exists believes must eventually no".splitOn " "

/-- The longest form, noun or plural (W3, W4): Python's verbalisation limit. -/
def maxFormChars : Nat := 256

/-- The longest sort name (W4): Python's identifier limit. -/
def maxNameChars : Nat := 64

def Sense.symbol (s : Sense) : String := "sense__" ++ s.word ++ "_" ++ toString s.index
def Sense.arity (s : Sense) : Nat := s.kinds.length
def Sense.isSimpleAdjective (s : Sense) : Bool := s.wording == "{0} is " ++ s.word && s.kinds.length == 1

/-- The parts of a text: its pieces between single spaces (2.1). -/
def partsOf (t : String) : List String := t.splitOn " "

/-- `xs` with its first element equal to `a` replaced by `b`. -/
def replaceFirstIn : List String → String → String → List String
  | [], _, _ => []
  | x :: xs, a, b => if x == a then b :: xs else x :: replaceFirstIn xs a b

/-- `xs` with its last element equal to `a` replaced by `b`. -/
def replaceLast (xs : List String) (a b : String) : List String := (replaceFirstIn xs.reverse a b).reverse

/-- The head of `s` in the text `t` (2.3): the word when it is a part of `t`; otherwise the part of `t`
at the word's distance from the end of the wording's parts (`tell` in `{0} does not tell {1}`). -/
def Sense.headIn (s : Sense) (t : String) : Option String :=
  let ps := partsOf t
  if ps.contains s.word then some s.word
  else
    match ((partsOf s.wording).reverse.findIdx? (· == s.word)) with
    | some d => ps.reverse[d]?
    | none => none

/-- `t` with the last part equal to its head replaced by `deco head`; `t` when it has no head. -/
def Sense.decorate (s : Sense) (t : String) (deco : String → String) : String :=
  match s.headIn t with
  | some h => " ".intercalate (replaceLast (partsOf t) h (deco h))
  | none => t

def Sense.glossed (s : Sense) (t : String) : String :=
  s.decorate t fun h => h ++ " (meaning " ++ s.gloss ++ ")"

def Sense.commaForms (s : Sense) (t : String) : List String :=
  [s.decorate t fun h => h ++ ", in the sense of " ++ s.gloss ++ ",",
   s.decorate t fun h => h ++ ", in the sense of " ++ s.gloss]

def Sense.selectedWording (s : Sense) (isDefault : Bool) : String :=
  if isDefault then s.wording else s.glossed s.wording

def Sense.automaticNegative (s : Sense) (isDefault : Bool) : Option String :=
  negativeTemplate (s.selectedWording isDefault) s.arity

def Sense.fixedNegative (s : Sense) (isDefault : Bool) : Option String :=
  s.negative.map fun n => if isDefault then n else s.glossed n

/-- The fixed negative when one is declared, else the automatic one. -/
def Sense.selectedNegative (s : Sense) (isDefault : Bool) : Option String :=
  match s.fixedNegative isDefault with
  | some n => some n
  | none => s.automaticNegative isDefault

def Sense.bareNegative (s : Sense) : Option String := s.selectedNegative true

/-- The aliases with polarity (2.3): the comma forms of the wording and of the bare negative, and, for the
default, the glossed wording and the glossed bare negative. Repeats dropped. -/
def Sense.aliases (s : Sense) (isDefault : Bool) : List (String × Bool) :=
  ((s.commaForms s.wording).map (·, false) ++
   (match s.bareNegative with
    | some n => (s.commaForms n).map (·, true)
    | none => []) ++
   (if isDefault then
      [(s.glossed s.wording, false)] ++
      (match s.bareNegative with
       | some n => [(s.glossed n, true)]
       | none => [])
    else [])).eraseDups

/-- The wording and the bare negative. -/
def Sense.bareForms (s : Sense) : List String := [s.wording] ++ s.bareNegative.toList

/-- The glossed wording, its comma forms, the glossed bare negative, its comma forms, and the selected
negative of the sense when it is not the default. Repeats dropped. -/
def Sense.decoratedForms (s : Sense) : List String :=
  ([s.glossed s.wording] ++ s.commaForms s.wording ++
   (match s.bareNegative with
    | some n => [s.glossed n] ++ s.commaForms n
    | none => []) ++
   (s.selectedNegative false).toList).eraseDups

/-- The word and the head of the bare negative, folded, repeats dropped. -/
def Sense.headwordTokens (s : Sense) : List String :=
  (([some s.word, s.bareNegative.bind s.headIn].filterMap id).map fold).eraseDups

/-- A failed condition: the condition, the word, pack or kind, and the English detail of 4.2. -/
abbrev DictFailure := String × String × String

def Dictionary.senses (D : Dictionary) : List Sense := D.packs.flatMap (·.senses) ++ D.own
def Dictionary.sorts (D : Dictionary) : List PackSort := (D.packs.flatMap (·.sorts)).eraseDups
def Dictionary.sensesOf (D : Dictionary) (w : String) : List Sense := D.senses.filter (·.word == w)
def Dictionary.words (D : Dictionary) : List String := (D.senses.map (·.word)).eraseDups

/-- Only the letters `a` to `z`. -/
def lowerAscii (s : String) : Bool := s.all fun c => 'a' ≤ c && c ≤ 'z'

/-- The words of a text: its maximal runs of ASCII letters, folded (2.1). -/
def wordsOf (t : String) : List String :=
  splitWs (String.mk ((fold t).toList.map fun c => if 'a' ≤ c && c ≤ 'z' then c else ' '))

/-- Whether `phrase` occurs in `ws` as consecutive words. -/
def hasPhrase (ws phrase : List String) : Bool :=
  (List.range (ws.length + 1)).any fun i => phrase.isPrefixOf (ws.drop i)

/-- The first condition of W3's text conditions that the text `t` of `s` fails, as the end of 4.2's
sentence. -/
def wordingFault (s : Sense) (t : String) : Option String :=
  if !shapeOk t s.arity then some "does not have each of its places once, with a word"
  else if (partsOf t).head? != some "{0}" then some "does not begin with its first place"
  else if !((partsOf t).count s.word == 1 && (wordsOf t).count s.word == 1) then
    some ("does not contain " ++ s.word ++ " exactly once")
  else if t.any (fun c => c == '(' || c == ')' || c == '.') then some "contains a bracket or a full stop"
  else if (wordsOf t).any (fun w => w == "means" || w == "meaning") then some "contains means or meaning"
  else if hasPhrase (wordsOf t) ["in", "the", "sense", "of"] then some "contains in the sense of"
  else none

/-- W2's form of a gloss: one to three parts, each of 3 to 50 letters `a` to `z`, none reserved. -/
def glossOk (g : String) : Bool :=
  let ws := partsOf g
  1 ≤ ws.length && ws.length ≤ 3 && ws.all fun w =>
    3 ≤ w.length && w.length ≤ 50 && lowerAscii w && !reservedWords.contains w

/-- One character `A` to `Z`. -/
def letterOk (l : String) : Bool := l.length == 1 && l.all fun c => 'A' ≤ c && c ≤ 'Z'

/-- Python's identifier for a schema name: `[a-z][a-z0-9_]*`, at most 64 characters. -/
def identifierOk (n : String) : Bool :=
  match n.toList with
  | [] => false
  | c :: cs =>
    n.length ≤ maxNameChars && ('a' ≤ c && c ≤ 'z') &&
      cs.all fun d => ('a' ≤ d && d ≤ 'z') || ('0' ≤ d && d ≤ '9') || d == '_'

/-- A name no pack sort may take: a word of `schemaReserved`, `x` and one or more digits, or a name
beginning with `sense__`. -/
def nameReserved (n : String) : Bool :=
  schemaReserved.contains n || (n.startsWith "x" && n.length > 1 && (n.drop 1).all Char.isDigit) ||
    n.startsWith "sense__"

/-- Whether a text is longer than `maxFormChars`. -/
def tooLong (t : String) : Bool := t.length > maxFormChars

/-- W1: the words, their numbering, and one pack per word. -/
def w1Failures (D : Dictionary) : List DictFailure :=
  let groups : List (List Sense) := D.packs.map (·.senses) ++ [D.own]
  let form := D.senses.filterMap fun s =>
    if !(2 ≤ s.word.length && s.word.length ≤ 50 && lowerAscii s.word) then
      some ("W1", s.word, s.word ++ " is not a word of two to fifty lower-case letters")
    else none
  let reserved := D.senses.filterMap fun s =>
    if reservedWords.contains s.word then some ("W1", s.word, s.word ++ " is a reserved word") else none
  let numbering := groups.flatMap fun ss => ((ss.map (·.word)).eraseDups).filterMap fun w =>
    let idx := (ss.filter (·.word == w)).map (·.index)
    if idx.mergeSort (· ≤ ·) == (List.range idx.length).map (· + 1) then none
    else some ("W1", w, "the senses of " ++ w ++ " are not numbered from 1, each number once")
  let twoPacks := D.words.filterMap fun w =>
    match (D.packs.filter fun p => p.senses.any (·.word == w)).map (·.name) with
    | p1 :: p2 :: _ => some ("W1", w, "the word " ++ w ++ " is in two packs: " ++ p1 ++ " and " ++ p2)
    | _ => none
  let ownWord := (D.own.map (·.word)).eraseDups.filterMap fun w =>
    match (D.packs.filter fun p => p.senses.any (·.word == w)).map (·.name) with
    | p :: _ => some ("W1", w, "the document gives its own sense to " ++ w ++ ", a word of the pack " ++ p)
    | [] => none
  (form ++ reserved).eraseDups ++ numbering ++ twoPacks ++ ownWord

/-- W2: the glosses. -/
def w2Failures (D : Dictionary) : List DictFailure :=
  let shape := D.senses.filterMap fun s =>
    if !glossOk s.gloss then
      some ("W2", s.word, "the gloss " ++ s.gloss ++ " of " ++ s.word ++
        " is not one to three words of three to fifty lower-case letters, none reserved")
    else none
  let itself := D.senses.filterMap fun s =>
    if s.gloss == s.word then some ("W2", s.word, "the gloss of " ++ s.word ++ " is the word itself") else none
  let aWord := D.senses.filterMap fun s =>
    if s.gloss != s.word && D.words.contains s.gloss then
      some ("W2", s.word, "the gloss " ++ s.gloss ++ " of " ++ s.word ++ " is itself a word of the vocabulary")
    else none
  let twice := D.words.flatMap fun w =>
    let ss := D.sensesOf w
    (ss.filter fun s => (ss.filter fun t => wordingKey t.gloss == wordingKey s.gloss).length > 1).map
      (fun s => ("W2", w, "the word " ++ w ++ " has two senses with the gloss " ++ s.gloss))
  (shape ++ itself ++ aWord).eraseDups ++ twice.eraseDups

/-- W3: the wording's text conditions, then the length of every form. -/
def w3Failures (D : Dictionary) : List DictFailure :=
  D.senses.filterMap fun s =>
    let why := match wordingFault s s.wording with
      | some why => some why
      | none =>
        if (s.bareForms ++ s.decoratedForms).any tooLong then
          some "gives a form longer than two hundred and fifty-six characters"
        else none
    why.map fun why => ("W3", s.word, "the wording " ++ s.wording ++ " of " ++ s.word ++ " " ++ why)

/-- Whether a pack sort's noun is usable: not empty, no hole, at most 256 characters, one sentence. -/
def nounOk (n : String) : Bool := !n.isEmpty && noHole n && !tooLong n && (sentenceTokens n).isSome

/-- Whether a pack sort's plural is usable: not empty, no hole, at most 256 characters. -/
def pluralOk (n : String) : Bool := !n.isEmpty && noHole n && !tooLong n

/-- W4: kinds, sorts and descriptions. -/
def w4Failures (D : Dictionary) (docSorts : List String) : List DictFailure :=
  let packSortNames := D.packs.flatMap fun p => p.sorts.map (·.name)
  let arity := D.senses.filterMap fun s =>
    if s.kinds.length == 1 || s.kinds.length == 2 then none
    else some ("W4", s.word, s.word ++ " does not apply to one or two kinds")
  let described := D.senses.filterMap fun s =>
    if s.description.isEmpty then some ("W4", s.word, "a sense of " ++ s.word ++ " has no description") else none
  let packKinds := D.packs.flatMap fun p => p.senses.flatMap fun s =>
    (s.kinds.filter fun k => !(p.sorts.map (·.name)).contains k).map fun k =>
      ("W4", s.word, s.word ++ " applies to " ++ k ++ ", which is not a kind of the pack " ++ p.name)
  let ownKinds := D.own.flatMap fun s =>
    (s.kinds.filter fun k => !(docSorts.contains k || packSortNames.contains k)).map fun k =>
      ("W4", s.word, s.word ++ " applies to " ++ k ++ ", which is not a kind of the document or of its packs")
  let perSort (ok : PackSort → Bool) (text : PackSort → String) : List DictFailure :=
    D.packs.flatMap fun p => p.sorts.filterMap fun t => if ok t then none else some ("W4", p.name, text t)
  let names := perSort (identifierOk ·.name) fun t =>
    "the kind name " ++ t.name ++
      " is not lower-case letters, digits and underscores beginning with a letter, at most sixty-four in all"
  let reservedNames := perSort (!nameReserved ·.name) fun t => "the kind name " ++ t.name ++ " is reserved"
  let sortDescribed := perSort (!·.description.isEmpty) fun t => "the kind " ++ t.name ++ " has no description"
  let nouns := perSort (nounOk ·.noun) fun t => "the kind " ++ t.name ++ " has no usable noun"
  let plurals := perSort (pluralOk ·.plural) fun t => "the kind " ++ t.name ++ " has no usable plural"
  let letters := perSort (letterOk ·.letter) fun t =>
    "the label letter " ++ t.letter ++ " of the kind " ++ t.name ++ " is not one capital letter"
  let differently := (D.sorts.filter fun t => (D.sorts.filter (·.name == t.name)).length > 1).map fun t =>
    ("W4", t.name, "the kind " ++ t.name ++ " is declared differently in two packs")
  let sameLetter := D.sorts.flatMap fun t => (D.sorts.filter fun u => u.letter == t.letter && t.name < u.name).map
    fun u => ("W4", t.name, "the label letter " ++ t.letter ++ " is given to two kinds: " ++ t.name ++ " and " ++ u.name)
  let sameNoun := D.sorts.flatMap fun t =>
    (D.sorts.filter fun u => wordingKey u.noun == wordingKey t.noun && t.name < u.name).map fun u =>
      ("W4", t.name, "the noun " ++ t.noun ++ " is given to two kinds: " ++ t.name ++ " and " ++ u.name)
  (arity ++ described ++ packKinds ++ ownKinds ++ names ++ reservedNames ++ sortDescribed ++ nouns ++ plurals ++
    letters).eraseDups ++ differently.eraseDups ++ sameLetter.eraseDups ++ sameNoun.eraseDups

/-- W5: the negative. -/
def w5Failures (D : Dictionary) : List DictFailure :=
  D.senses.filterMap fun s =>
    match negativeTemplate s.wording s.arity, s.negative with
    | some _, some _ =>
      some ("W5", s.word, s.word ++ " declares a negative wording although its negative is automatic")
    | none, some n =>
      if n == s.wording then some ("W5", s.word, "the negative wording of " ++ s.word ++ " equals its wording")
      else (wordingFault s n).map fun why =>
        ("W5", s.word, "the negative wording " ++ n ++ " of " ++ s.word ++ " " ++ why)
    | _, none => none

/-- The first form of `s`, in the order `bareForms ++ decoratedForms`, whose key a compared form of `t`
has; two bare forms of one word are not compared (W6). -/
def clashingForm (s t : Sense) : Option String :=
  let keysOf (xs : List String) := xs.map wordingKey
  let all := keysOf (t.bareForms ++ t.decoratedForms)
  let againstBare := if s.word == t.word then keysOf t.decoratedForms else all
  (s.bareForms.find? fun f => againstBare.contains (wordingKey f)).orElse fun _ =>
    s.decoratedForms.find? fun f => all.contains (wordingKey f)

/-- W6: distinct forms; one failure per pair of senses, in the order of `D.senses`. -/
def w6Failures (D : Dictionary) : List DictFailure :=
  let indexed := D.senses.zipIdx
  let pairs := indexed.flatMap fun (s, i) => indexed.filterMap fun (t, j) =>
    if j ≤ i then none
    else (clashingForm s t).map fun f =>
      if s.word == t.word then ("W6", s.word, "the wording " ++ f ++ " belongs to two senses of " ++ s.word)
      else ("W6", s.word, "the wording " ++ f ++ " belongs to both " ++ s.word ++ " and " ++ t.word)
  let nouns := D.senses.flatMap fun s => D.sorts.filterMap fun t =>
    ((s.bareForms ++ s.decoratedForms).find? fun f => [wordingKey t.noun, wordingKey t.plural].contains (wordingKey f)).map
      fun f => ("W6", s.word, "the wording " ++ f ++ " of " ++ s.word ++ " is also the noun of the kind " ++ t.name)
  pairs ++ nouns.eraseDups

/-- Whether the words of a text contain `in this document` in a row. -/
def mentionsDocument (t : String) : Bool := hasPhrase (wordsOf t) ["in", "this", "document"]

/-- W7: the reserved phrase. -/
def w7Failures (D : Dictionary) : List DictFailure :=
  ((D.senses.flatMap fun s => (([s.wording] ++ s.negative.toList ++ [s.gloss]).filter mentionsDocument).map fun t =>
      ("W7", s.word, t ++ " contains in this document")) ++
    (D.sorts.flatMap fun t => ([t.noun, t.plural].filter mentionsDocument).map fun n =>
      ("W7", t.name, n ++ " contains in this document"))).eraseDups

/-- Every failed condition W1 to W7 of 2.2, in the order of the table. -/
def Dictionary.failures (D : Dictionary) (docSorts : List String) : List DictFailure :=
  w1Failures D ++ w2Failures D ++ w3Failures D ++ w4Failures D docSorts ++ w5Failures D ++ w6Failures D ++
    w7Failures D

def Dictionary.wf (D : Dictionary) (docSorts : List String) : Bool := (D.failures docSorts).isEmpty

theorem wf_iff_no_failure : ∀ (D : Dictionary) (ss : List String),
  D.wf ss = true ↔ D.failures ss = [] := by
  intro D ss
  unfold Dictionary.wf
  exact List.isEmpty_iff

/-- The statement of spec 5.3 for the automatic negative of a glossed simple adjective. It is checked on
the fixtures (`VE.Senses.Examples`, d25) and not proved: S2's `negativeTemplate` reads its prefix with
`String.startsWith`, for which the toolchain has no lemma (docs/spec/senses-lean-report.md). -/
def glossed_negative : Prop := ∀ (s : Sense), s.isSimpleAdjective = true →
  negativeTemplate (s.glossed s.wording) 1 = some (s.glossed ("{0} is not " ++ s.word))

end VE.Senses
