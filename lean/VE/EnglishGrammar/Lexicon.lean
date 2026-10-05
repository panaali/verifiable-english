import Lean.Data.Json
import VE.EnglishGrammar.Lexer

/-! The selected lexicon and its validity (docs/spec/english-lean.md 2.9 and 5.8; tier B).

A producer (Python's `EnglishVocabulary`) proposes the lexicon; Lean validates it. `Lexicon.valid E O L`
holds when the five conditions of spec 2.9 hold:

- V1 coverage: exactly one entry for each sort, predicate and constant of `E`, the symbols a profile
  block generates included, and no other entry. No symbol is exempt (DRI ruling 2, 2026-10-04): a
  generated symbol without an English wording makes the lexicon invalid until it gets one.
- V2 honesty: every selection is an honest wording of its own symbol (declared, profile, mechanical,
  fallback); negatives and aliases are the declared or profile-fixed ones.
- V3 shape: a predicate wording has each hole `{0}` to `{k-1}` once, no other hole, and a word; and,
  with each hole lexed as a word of its own, it lexes as one sentence (S2 spec 2.6, Q6), so no wording
  puts a terminator inside a rule. The substitution is `wordingTokens`, the one the lexical rules read,
  so a wording that passes V3 gives its rules (`{0}s are {1}` fails both).
- V4 distinctness, by `wordingKey`, against what every other symbol declares or selects.
- V5 polarity: a selected negative is `negativeTemplate` of the selected wording, unless a profile block
  fixes it.

The lint codes that the DRI's ruling 4 (2026-10-04) moves into Lean validity are these conditions:
`DUPLICATE_TEMPLATE` and `SORT_COLLISION` (V4), `NEGATIVE_NOT_NEGATION` and `NEGATIVE_WITHOUT_POSITIVE`
(V5), and the hole part of `TEMPLATE_SHAPE` (V3). The order rule of `TEMPLATE_SHAPE` and the advisory
lints stay Python checks; the final list is fixed at the statement review.

`Env` and `Overlay` here are the lexical views that `valid` reads: the declared wordings, nouns and
display forms, the arities, and the forms the profile blocks fix (`ProfileForms`, spec 2.9 notes and
O7). The profile forms are computed from the profile blocks in S3; the base environments of S2 have
none. S2 adds the signatures that the lexical rules and the actions read (S2 spec 2.3): a predicate's
argument sorts `args` and a constant's `sort`, and the environment JSON `source`, which only the typed
check of `VE.EnglishGrammar.Encode` reads.
-/

namespace VE.EnglishGrammar

/-- `json.dumps(s, ensure_ascii=True)`, Python's `quote` (`ve/english.py`): the quoted fallback names. -/
def jsonQuote (s : String) : String :=
  let hex4 (n : Nat) : String :=
    let d := Nat.toDigits 16 n
    String.mk (List.replicate (4 - d.length) '0' ++ d)
  let esc (c : Char) : String :=
    if c == '"' then "\\\""
    else if c == '\\' then "\\\\"
    else if c == '\n' then "\\n"
    else if c == '\r' then "\\r"
    else if c == '\t' then "\\t"
    else if c.val == 8 then "\\b"
    else if c.val == 12 then "\\f"
    else if c.val < 0x20 then "\\u" ++ hex4 c.val.toNat
    else if c.val < 0x7F || c.val == 0x7F then String.singleton c
    else if c.val < 0x10000 then "\\u" ++ hex4 c.val.toNat
    else
      let v := c.val.toNat - 0x10000
      "\\u" ++ hex4 (0xD800 + v / 0x400) ++ "\\u" ++ hex4 (0xDC00 + v % 0x400)
  "\"" ++ String.join (s.toList.map esc) ++ "\""

/-- The words of a text: its maximal runs of characters that are not whitespace (Python's
`str.split()`). -/
def splitWs (s : String) : List String :=
  let rec go : List Char → List Char → List String
    | [], cur => if cur.isEmpty then [] else [String.mk cur.reverse]
    | c :: cs, cur =>
      if isSpace c then (if cur.isEmpty then go cs [] else String.mk cur.reverse :: go cs [])
      else go cs (c :: cur)
  go s.toList []

/-- Python's `s.strip()`. -/
def stripWs (s : String) : String :=
  String.mk ((s.toList.dropWhile isSpace).reverse.dropWhile isSpace).reverse

/-- The first position at which `pat` occurs in `s`. -/
def findSub (pat : List Char) : List Char → Nat → Option Nat
  | [], i => if pat.isEmpty then some i else none
  | c :: cs, i => if pat.isPrefixOf (c :: cs) then some i else findSub pat cs (i + 1)

/-- Python's `s.replace(pat, new, 1)`. -/
def replaceFirst (s pat new : String) : String :=
  match findSub pat.toList s.toList 0 with
  | some i => String.mk (s.toList.take i) ++ new ++ String.mk (s.toList.drop (i + pat.length))
  | none => s

/-- `wording_key` (`ve/english_phrases.py`): outside quoted parts, fold the case and turn every run of
whitespace and hyphens into one space; then trim. A quoted part runs from `"` to the next `"` not
escaped by `\`; a `"` with no closing quote is an ordinary character. -/
def wordingKey (text : String) : String :=
  -- the quoted part that starts at a `"`: its characters after the opening quote, or nothing
  let rec quoted : List Char → Bool → List Char → Option (List Char × List Char)
    | [], _, _ => none
    | c :: cs, esc, acc =>
      if esc then quoted cs false (c :: acc)
      else if c == '\\' then quoted cs true (c :: acc)
      else if c == '"' then some ((c :: acc).reverse, cs)
      else quoted cs false (c :: acc)
  -- `prevSep`: the output ends with the space of a separator run
  let rec go : Nat → List Char → Bool → List Char → List Char
    | 0, _, _, out => out
    | _ + 1, [], _, out => out
    | n + 1, c :: cs, prevSep, out =>
      if c == '"' then
        match quoted cs false [] with
        | some (q, rest) => go n rest false (q.reverse ++ '"' :: out)
        | none => go n cs false ('"' :: out)
      else if isSpace c || c == '-' then
        go n cs true (if prevSep then out else ' ' :: out)
      else go n cs false (foldChar c :: out)
  stripWs (String.mk (go (text.length + 1) text.toList false []).reverse)

/-- Unary idioms (`IDIOMS[1]`, `ve/english_vocabulary.py`). -/
def idioms1 : List String :=
  ["{0} has a noncitizen parent domiciled in the United States",
   "{0} has a noncitizen parent temporarily in the United States",
   "{0} has an undocumented noncitizen parent",
   "{0} involves a hard constraint violation",
   "{0} is a US citizen",
   "{0} is a current Claude model",
   "{0} is an appropriately sanctioned human check",
   "{0} is born in the United States",
   "{0} is expected to have the core values",
   "{0} is inappropriately dangerous or harmful",
   "{0} is inappropriately harmful",
   "{0} is subject to US jurisdiction",
   "{0} is unanimous"]

/-- Binary idioms (`IDIOMS[2]`, `ve/english_vocabulary.py`). -/
def idioms2 : List String :=
  ["{0} abridges the privileges or immunities of {1}",
   "{0} attributes elevated inflation to {1}",
   "{0} calls for generally prioritizing {1}",
   "{0} deprives {1} of life, liberty, or property",
   "{0} interacts with {1}",
   "{0} involves apparent conflict over {1}",
   "{0} is a citizen of {1}",
   "{0} is projected for the end of {1}",
   "{0} is projected to occur in {1}",
   "{0} is scheduled for {1}",
   "{0} is the first policy shift under {1}",
   "{0} is within the jurisdiction of {1}",
   "{0} issued {1}",
   "{0} may access {1}",
   "{0} owes unconditional obedience to {1}",
   "{0} pledged {1}",
   "{0} promised {1}",
   "{0} raised its policy rate on {1}",
   "{0} raised its policy rate to {1}",
   "{0} submitted a rate projection for {1}",
   "{0} took office in {1}",
   "{0} undermines the oversight role of {1}",
   "{0} undermines {1}",
   "{0} voted for {1}",
   "{0} was appointed by {1}"]

def idioms : Nat → List String
  | 1 => idioms1
  | 2 => idioms2
  | _ => []

/-- `_IRREGULAR_VERBS` (`ve/printer.py`). -/
def irregularVerbs : List (String × String) :=
  [("has", "have"), ("does", "do"), ("goes", "go"), ("says", "say"), ("dies", "die"), ("lies", "lie"),
   ("ties", "tie"), ("unties", "untie"), ("vies", "vie"), ("quizzes", "quiz"), ("gases", "gas"),
   ("biases", "bias"), ("buses", "bus"), ("focuses", "focus"), ("echoes", "echo"), ("vetoes", "veto"),
   ("aches", "ache"), ("caches", "cache"), ("niches", "niche"), ("axes", "axe"), ("shoes", "shoe"),
   ("toes", "toe"), ("tiptoes", "tiptoe")]

/-- The idiom verbs in the past tense and their base forms (`negative_template`). -/
def pastVerbs : List (String × String) :=
  [("raised", "raise"), ("voted", "vote"), ("promised", "promise"), ("submitted", "submit"),
   ("took", "take"), ("issued", "issue"), ("pledged", "pledge")]

/-- The base form of a verb in the third person singular (`_negative_template`, `ve/printer.py`). -/
def verbBase (verb : String) : Option String :=
  match irregularVerbs.lookup verb with
  | some base => some base
  | none =>
    let n := verb.length
    if n > 3 && verb.endsWith "ies" && !"aeiou".contains (verb.get ⟨(verb.toList.take (n - 4)).foldl
        (fun k c => k + c.utf8Size) 0⟩) then
      some (verb.dropRight 3 ++ "y")
    else if ["ches", "shes", "sses", "xes", "zzes"].any verb.endsWith then some (verb.dropRight 2)
    else if n > 2 && verb.endsWith "s" && !(["ss", "us", "is", "ous", "oes"].any verb.endsWith) then
      some (verb.dropRight 1)
    else none

/-- `_negative_template(positive, 2)` (`ve/printer.py`). A wording of fewer than two words, on which
Python fails, has none. -/
def negateVerb (positive : String) : Option String :=
  match splitWs positive with
  | _ :: verb :: rest => (verbBase verb).map fun base => "{0} does not " ++ base ++ " " ++ " ".intercalate rest
  | _ => none

/-- `negative_template` (`ve/english_vocabulary.py`): the negative of a positive wording, or none. -/
def negativeTemplate (wording : String) (arity : Nat) : Option String :=
  if wording.startsWith "{0} is " then some (replaceFirst wording "{0} is " "{0} is not ")
  else if wording.startsWith "{0} was " then some (replaceFirst wording "{0} was " "{0} was not ")
  else if wording.startsWith "{0} has " then some (replaceFirst wording "{0} has " "{0} does not have ")
  else
    let rest := if arity == 2 || idioms1.contains wording then negateVerb wording else none
    match (splitWs wording).drop 1 |>.head? with
    | some verb =>
      match pastVerbs.lookup verb with
      | some base =>
        if (idioms arity).contains wording then
          some (replaceFirst wording ("{0} " ++ verb ++ " ") ("{0} did not " ++ base ++ " "))
        else rest
      | none => rest
    | none => none

/-- The holes of a wording, in order, and its text with every hole `{k}` replaced by `fill k`. -/
def fillHoles (w : String) (fill : Nat → String) : List Nat × String :=
  let rec go : Nat → List Char → List Nat → List Char → List Nat × List Char
    | 0, _, hs, out => (hs.reverse, out.reverse)
    | _ + 1, [], hs, out => (hs.reverse, out.reverse)
    | n + 1, c :: cs, hs, out =>
      if c == '{' then
        let ds := cs.takeWhile Char.isDigit
        match cs.drop ds.length with
        | '}' :: rest =>
          if ds.isEmpty then go n cs hs (c :: out)
          else
            let k := ds.foldl (fun k d => 10 * k + (d.toNat - '0'.toNat)) 0
            go n rest (k :: hs) ((fill k).toList.reverse ++ out)
        | _ => go n cs hs (c :: out)
      else go n cs hs (c :: out)
  match go (w.length + 1) w.toList [] [] with
  | (hs, out) => (hs, String.mk out)

/-- The holes of a wording, in order, and its text with every hole replaced by a space. -/
def holes (w : String) : List Nat × String := fillHoles w fun _ => " "

/-- The tokens of a text written as one sentence, or none. -/
def sentenceTokens (text : String) : Option (List Tok) :=
  match lex (text ++ ".") with
  | .ok sents =>
    match sents.toList with
    | [s] => some s.toList
    | _ => none
  | .error _ => none

/-- The character that stands for a hole while a wording is lexed; a wording that contains it gives no
rule. -/
def holeChar : Char := Char.ofNat 0xE000

/-- The word that stands for hole `k` while a wording is lexed. -/
def holeMark (k : Nat) : String := String.singleton holeChar ++ toString k

/-- Whether a token is the word of one of the holes `order`. -/
def isHoleWord (order : List Nat) : Tok → Bool
  | .word x _ => order.any fun k => x == holeMark k
  | _ => false

/-- A wording's hole order and its tokens, each hole lexed as the word `holeMark k`; none when the
wording contains `holeChar`, does not lex as one sentence, or has a hole that is not a word of its own
(`{0}s`). V3 (`shapeOk`) and the lexical rules (`wordingSyms`) read a wording through this one
substitution. -/
def wordingTokens (w : String) : Option (List Nat × List Tok) :=
  if w.any (· == holeChar) then none
  else
    match fillHoles w holeMark with
    | (order, text) =>
      match sentenceTokens text with
      | none => none
      | some toks => if (toks.filter (isHoleWord order)).length == order.length then some (order, toks) else none

/-- V3 for a predicate wording of arity `k`: each hole `{0}` to `{k-1}` once, no other, a word, and the
wording lexes as one sentence with each hole a word of its own (`wordingTokens`; S2 spec 2.6). -/
def shapeOk (w : String) (k : Nat) : Bool :=
  match holes w with
  | (hs, rest) =>
    decide (hs.mergeSort (· ≤ ·) = List.range k) && !(splitWs rest).isEmpty && (wordingTokens w).isSome

/-- V3 for a noun or a spelling: no hole. -/
def noHole (w : String) : Bool := (holes w).1.isEmpty

structure SortDecl where
  name : String
  noun : Option String := none
  deriving Repr

structure PredDecl where
  name : String
  arity : Nat
  wording : Option String := none
  negative : Option String := none
  /-- The argument sorts in order; `arity = args.length` for a decoded environment (S2 spec 2.3). -/
  args : List String := []
  deriving Repr

structure ConstDecl where
  name : String
  display : Option String := none
  /-- The constant's sort (S2 spec 2.3). -/
  sort : String := ""
  deriving Repr

/-- The forms that profile blocks fix (spec 2.9 notes, O7): wordings, negatives, aliases, nouns. -/
structure ProfileForms where
  wordings : List (String × String) := []
  negatives : List (String × String) := []
  aliases : List (String × String × Bool) := []
  nouns : List (String × String) := []
  deriving Repr

/-- The environment JSON is shown compressed. -/
instance reprJson : Repr Lean.Json := ⟨fun j _ => .text j.compress⟩

/-- The lexical view of an environment that `Lexicon.valid` reads: every sort, predicate and constant,
the symbols that profile blocks generate included, with their declared wordings. -/
structure Env where
  sorts : List SortDecl
  predicates : List PredDecl
  constants : List ConstDecl
  profiles : List String := []
  forms : ProfileForms := {}
  /-- The validated environment JSON; read by `typedDocument` only (S2 spec 2.3). -/
  source : Lean.Json := .null
  deriving Repr

/-- The replaced wordings of an English vocabulary overlay. A predicate entry replaces both the
wording and the negative (an old negative never attaches to a changed positive). -/
structure Overlay where
  sorts : List (String × String) := []
  predicates : List (String × String × Option String) := []
  constants : List (String × String) := []
  deriving Repr

structure Lexicon where
  nouns : List (String × String)              -- sort, selected noun
  letters : List (String × String)            -- sort, label letter
  wordings : List (String × String)           -- predicate, selected wording
  negatives : List (String × String)          -- predicate, selected negative
  aliases : List (String × String × Bool)     -- predicate, input wording, negated
  spellings : List (String × String)          -- constant, selected spelling
  deriving Repr

namespace Env

def predicate? (E : Env) (p : String) : Option PredDecl := E.predicates.find? (·.name == p)

def declaredWording (E : Env) (O : Overlay) (p : String) : Option String :=
  match O.predicates.find? (·.1 == p) with
  | some (_, w, _) => some w
  | none => (E.predicate? p).bind (·.wording)

def declaredNegative (E : Env) (O : Overlay) (p : String) : Option String :=
  match O.predicates.find? (·.1 == p) with
  | some (_, _, n) => n
  | none => (E.predicate? p).bind (·.negative)

def declaredNoun (E : Env) (O : Overlay) (s : String) : Option String :=
  match O.sorts.lookup s with
  | some n => some n
  | none => (E.sorts.find? (·.name == s)).bind (·.noun)

def declaredSpelling (E : Env) (O : Overlay) (c : String) : Option String :=
  match O.constants.lookup c with
  | some d => some d
  | none => (E.constants.find? (·.name == c)).bind (·.display)

def arity (E : Env) (p : String) : Nat := ((E.predicate? p).map (·.arity)).getD 0

end Env

/-- The mechanical wording of a bare identifier (`printer.py`), for a lower-case name when unary or
binary. -/
def mechanicalWording (name : String) (k : Nat) : Option String :=
  let lower := !name.isEmpty && name.all fun c => 'a' ≤ c && c ≤ 'z'
  if k == 1 then (if lower then some ("{0} is " ++ name) else none)
  else if k == 2 then (if lower then some ("{0} " ++ name ++ " {1}") else none)
  else if k ≤ 6 then
    some ("{0} has recorded relation " ++ name ++ " with " ++ " and ".intercalate
      ((List.range (k - 1)).map fun i =>
        "argument " ++ (["two", "three", "four", "five", "six"].getD i "") ++ " {" ++ toString (i + 1) ++ "}"))
  else none

/-- The quoted fallback wording (`english.py`). -/
def fallbackWording (name : String) (k : Nat) : Option String :=
  if k == 1 then some ("{0} is classified as " ++ jsonQuote name)
  else if k == 2 then some ("{0} has the recorded relation " ++ jsonQuote name ++ " to {1}")
  else none

/-- A failed condition of `Lexicon.valid`: the condition, the kind of symbol and its name. -/
abbrev Failure := String × String × String

def keysOf {β : Type} (l : List (String × β)) : List String := l.map (·.1)

/-- The symbols of `need` without exactly one entry, and the entries of `got` that are not symbols or repeat
one: V1. -/
def coverage (kind : String) (got need : List String) : List Failure :=
  (need.filter (fun s => got.count s != 1)).map (fun s => ("V1", kind, s)) ++
  (got.filter (fun s => !need.contains s)).map (fun s => ("V1", kind, s))

/-- Every failed condition of V1 to V5, in condition order. Empty exactly when the lexicon is valid. -/
def Lexicon.failures (E : Env) (O : Overlay) (L : Lexicon) : List Failure :=
  let sorts := E.sorts.map (·.name)
  let preds := E.predicates.map (·.name)
  let consts := E.constants.map (·.name)
  let F := E.forms
  -- V1
  let v1 := coverage "sort" (keysOf L.nouns) sorts ++ coverage "letter" (keysOf L.letters) sorts ++
    coverage "predicate" (keysOf L.wordings) preds ++ coverage "constant" (keysOf L.spellings) consts ++
    ((keysOf L.negatives).filter (fun p => !preds.contains p || (keysOf L.negatives).count p != 1)).map
      (fun p => ("V1", "negative", p)) ++
    ((L.aliases.map (·.1)).filter (fun p => !preds.contains p)).map (fun p => ("V1", "alias", p))
  -- V2 and V3
  let v23w := L.wordings.flatMap fun (p, w) =>
    if !preds.contains p then [] else
    let k := E.arity p
    let honest := [E.declaredWording O p, F.wordings.lookup p, mechanicalWording p k, fallbackWording p k]
    (if honest.contains (some w) then [] else [("V2", "predicate", p)]) ++
    (if shapeOk w k then [] else [("V3", "predicate", p)])
  let v235n := L.negatives.flatMap fun (p, w) =>
    if !preds.contains p then [] else
    let k := E.arity p
    let fixed := F.negatives.lookup p
    (if [E.declaredNegative O p, fixed].contains (some w) then [] else [("V2", "negative", p)]) ++
    (if shapeOk w k then [] else [("V3", "negative", p)]) ++
    (if fixed == some w || negativeTemplate ((L.wordings.lookup p).getD "") k == some w then []
     else [("V5", "negative", p)])
  let aliasPreds := ((L.aliases.map (·.1)) ++ (F.aliases.map (·.1))).eraseDups
  let sortPairs (l : List (String × Bool)) := l.mergeSort fun x y => x.1 < y.1 || (x.1 == y.1 && x.2 ≤ y.2)
  let v23a := aliasPreds.flatMap fun p =>
    let sel := (L.aliases.filter (·.1 == p)).map (·.2)
    let fix := (F.aliases.filter (·.1 == p)).map (·.2)
    (if sortPairs sel == sortPairs fix then [] else [("V2", "alias", p)]) ++
    (if sel.all (fun a => shapeOk a.1 (E.arity p)) then [] else [("V3", "alias", p)])
  let v23s := L.nouns.flatMap fun (s, n) =>
    if !sorts.contains s then [] else
    let honest := [E.declaredNoun O s, F.nouns.lookup s, some s, some ("entity of sort " ++ jsonQuote s)]
    (if honest.contains (some n) then [] else [("V2", "sort", s)]) ++
    (if noHole n then [] else [("V3", "sort", s)])
  let v23c := L.spellings.flatMap fun (c, sp) =>
    if !consts.contains c then [] else
    let honest := [E.declaredSpelling O c, some c, some (jsonQuote c)]
    (if honest.contains (some sp) then [] else [("V2", "constant", c)]) ++
    (if noHole sp then [] else [("V3", "constant", c)])
  -- V4: each selection against what every other symbol declares or selects
  let own (text : Option String) (kind name : String) : List (String × String × String) :=
    match text with
    | some t => if t.isEmpty then [] else [(wordingKey t, kind, name)]
    | none => []
  let owners :=
    (preds.flatMap fun p => own (E.declaredWording O p) "predicate" p ++ own (E.declaredNegative O p) "predicate" p ++
      own (F.wordings.lookup p) "predicate" p ++
      ((F.aliases.filter (·.1 == p)).flatMap fun a => own (some a.2.1) "predicate" p)) ++
    (sorts.flatMap fun s => own (E.declaredNoun O s) "sort" s ++ own (L.nouns.lookup s) "sort" s) ++
    (consts.flatMap fun c => own (E.declaredSpelling O c) "constant" c ++ own (L.spellings.lookup c) "constant" c)
  let selections : List (String × String × String) :=
    L.wordings.map (fun (p, w) => (w, "predicate", p)) ++ L.negatives.map (fun (p, w) => (w, "predicate", p)) ++
    L.aliases.map (fun (p, w, _) => (w, "predicate", p)) ++ L.nouns.map (fun (s, n) => (n, "sort", s)) ++
    L.spellings.map (fun (c, sp) => (sp, "constant", c))
  let v4 := selections.filterMap fun (text, kind, name) =>
    let key := wordingKey text
    if owners.any (fun (k2, kind2, name2) => k2 == key && !(kind2 == kind && name2 == name)) then
      some ("V4", kind, name)
    else none
  v1 ++ v23w ++ v235n ++ v23a ++ v23s ++ v23c ++ v4

/-- `Lexicon.valid` of spec 2.9: V1 to V5. -/
def Lexicon.valid (E : Env) (O : Overlay) (L : Lexicon) : Bool := (L.failures E O).isEmpty

/-- The work budget of one sentence, in steps of spec 2.6 (DRI ruling 5, 2026-10-04): ten times the
largest reference parse measured on the corpus (about 210,000 steps), for the design point of 300
tokens. -/
def workBudget : Nat := 2100000

end VE.EnglishGrammar
