import VE.Grammar.Expect
import VE.EnglishGrammar.Rules
import VE.EnglishGrammar.Lexer

/-! What a sentence without a reading needs, and where (docs/spec/english-lean-e2.md 4.5).

When `read` stops at sentence `i` with no derivation, `diagnose` finds the farthest token that some sentence of
the grammar reaches (`VE.Grammar.viable`) and says what may come there, as the hand parser said it: the words
that the grammar's rules read next (`Expected ', then ' here.`), or, where a declared wording may come, the
phrase written there with the three nearest declared wordings (`Unknown English phrase …`). The span runs from
the end of the last token read to the end of the token, or phrase, that cannot come there. The text is help: it
is computed after the verdict and changes nothing else in the response.
-/

namespace VE.EnglishGrammar
open VE.Grammar

/-- A terminal as written: its text, whether it is written against the token before it, and whether the next
token is written against it. A class terminal (a label or a number) has no fixed text. -/
def Terminal.piece? : Terminal → Option (String × Bool × Bool)
  | .kw s | .kwMid s | .content s => some (s, false, false)
  | .exact (.word t _) => some (t, false, false)
  | .exact (.punct p b a) => some (p, b, a)
  | .exact (.quoted n) => some ("\"" ++ n ++ "\"", false, false)
  | .exact (.label l k) => some (l ++ toString k, false, false)
  | .exact (.numeral v) => some (toString v, false, false)
  | .cls _ => none

def joinPieces : List (String × Bool × Bool) → String
  | [] => ""
  | (t, _, a) :: ps =>
    (ps.foldl (fun (acc, glue) (t2, b, a2) => (acc ++ (if b || glue then "" else " ") ++ t2, a2)) (t, a)).1

/-- The words an item reads next: its terminals up to its next nonterminal or class terminal, followed by a
space when the rule goes on (the hand parser's `', then '`). -/
def runOf (G : Grammar Terminal) (it : EarleyItem) : Option String :=
  let rest := (((G.rules[it.rule]?).map (·.rhs)).getD []).drop it.dot
  let fixed := rest.takeWhile fun
    | .t a => a.piece?.isSome
    | .n _ => false
  let pieces := fixed.filterMap fun
    | .t a => a.piece?
    | .n _ => none
  if pieces.isEmpty then none
  else some (joinPieces pieces ++ (if pieces.length < rest.length then " " else ""))

def quoteText (s : String) : String := "'" ++ s ++ "'"

/-- `'a'`, `'a' or 'b'`, `'a', 'b' or 'c'`. -/
def orList (xs : List String) : String :=
  match xs.reverse with
  | [] => ""
  | [x] => quoteText x
  | x :: rest => ", ".intercalate (rest.reverse.map quoteText) ++ " or " ++ quoteText x

/-! ## The nearest declared wordings (the hand parser's `nearest`, `ve/english_phrases.py`) -/

/-- The words of a text for comparison: maximal runs of ASCII letters and digits after folding, without `0`,
`1`, `is`, `not`, `a` and `an`, joined by spaces. -/
def lexicalText (s : String) : String :=
  let keep (c : Char) : Bool := ('a' ≤ c && c ≤ 'z') || ('0' ≤ c && c ≤ '9')
  let words := ((fold s).toList.splitBy (fun a b => keep a == keep b)).filterMap fun cs =>
    if cs.all keep then some (String.mk cs) else none
  " ".intercalate (words.filter fun x => !["0", "1", "is", "not", "a", "an"].contains x)

/-- The edit distance of two texts, by characters. -/
def editDistance (a b : String) : Nat :=
  let bs := b.toList.toArray
  let row0 : Array Nat := (List.range (bs.size + 1)).toArray
  let last := a.toList.zipIdx.foldl (fun (row : Array Nat) (x, i) =>
    (List.range bs.size).foldl (fun (nw : Array Nat) j =>
      let cost := if bs[j]! == x then 0 else 1
      nw.push (min (min (nw[j]! + 1) (row[j + 1]! + 1)) (row[j]! + cost))) #[i + 1]) row0
  last[bs.size]!

def lastWord (s : String) : Option String := (s.splitOn " ").filter (· ≠ "") |>.getLast?

/-- The three declared wordings nearest to `phrase`: the selected wordings without their `{0} `, the nouns
and the spellings, by edit distance to the wording or to the symbol's name, then a shared last word, then the
symbol's name. -/
def nearestWordings (L : Lexicon) (phrase : String) : List String :=
  let target := lexicalText phrase
  let symbols : List (String × String) :=
    L.wordings.map (fun (p, w) => (p, if w.startsWith "{0} " then w.drop 4 else w)) ++ L.nouns ++ L.spellings
  let rows := symbols.map fun (name, wording) =>
    let cands := [lexicalText wording, lexicalText name]
    let edit := (cands.map (editDistance target)).foldl min (editDistance target cands[0]!)
    let stem := cands.any fun c => lastWord c == lastWord target
    (edit, !stem, name, wording)
  let sorted := rows.mergeSort fun (e1, s1, n1, _) (e2, s2, n2, _) =>
    decide (e1 < e2) || (e1 == e2 && ((!s1 && s2) || (s1 == s2 && (decide (n1 < n2) || n1 == n2))))
  (sorted.take 3).map (·.2.2.2)

/-! ## The diagnosis -/

/-- The words that end a phrase of the hand parser (`BOUNDARIES`), and the `is not a` it skips. -/
def phraseBoundaries : List String :=
  ["is", "does", "not", "and", "or", "if", "then", "that", "who", "which", "both", "either", "every", "some", "for"]

def tokWord? : Tok → Option String
  | .word t _ => some (fold t)
  | _ => none

/-- The last token of the phrase at token `k`: `is`, `not` and an article first, then the words up to a
boundary word or a comma; at least token `k`. -/
def phraseEnd (toks : Array Tok) (k : Nat) : Nat := Id.run do
  let mut j := k
  if (toks[j]?.bind tokWord?) == some "is" then j := j + 1
  if (toks[j]?.bind tokWord?) == some "not" then j := j + 1
  if (toks[j]?.bind tokWord?) == some "a" || (toks[j]?.bind tokWord?) == some "an" then j := j + 1
  let mut e := j
  for _ in [j:toks.size] do
    match toks[e]? with
    | some (.word t _) => if phraseBoundaries.contains (fold t) then break else e := e + 1
    | some (.punct "," _ _) => break
    | some _ => e := e + 1
    | none => break
  return if e = 0 || e - 1 < k then k else e - 1

structure Diagnosis where
  text : String
  /-- Byte offsets in the source. -/
  span : Nat × Nat
  deriving Repr

/-- The predicate a lexical rule reads, if any. -/
def LexAct.predicate? : LexAct → Option String
  | .pred p _ _ | .relSubject p _ _ | .relObject p _ | .adjective p _ | .natSubject p _ _ | .copulaRel p => some p
  | _ => none

/-- How many terminals an item has read since its last nonterminal: the words of its wording so far. -/
def wordsRead (G : Grammar Terminal) (it : EarleyItem) : Nat :=
  ((((G.rules[it.rule]?).map (·.rhs)).getD []).take it.dot).reverse.takeWhile (fun
    | .t _ => true
    | .n _ => false) |>.length

/-- The second word of each selected wording, negative and alias: a word that may follow a subject (the hand
parser's clause heads). -/
def clauseHeads (L : Lexicon) : List String :=
  (L.wordings.map (·.2) ++ L.negatives.map (·.2) ++ L.aliases.map (·.2.1)).filterMap fun t =>
    ((splitWs t)[1]?).map fold

/-- What sentence `toks` needs where it stops, when the budget allows finding it. In order: a declared wording
followed by a word that cannot follow it (the hand parser's prefix collision); where a declared wording may
come, the phrase written there and the nearest declared wordings; otherwise the words the rules read next. -/
def diagnose (E : Env) (L : Lexicon) (source : String) (toks : Array Spanned) : Option Diagnosis := do
  let G := grammar E L
  let w := toks.map (·.1)
  let (far, items) ← viable G workBudget w
  let fixedCount := (fixedRules E.profiles).size
  let rows := (lexRows E L).toArray
  let lexical (it : EarleyItem) : Bool := fixedCount ≤ it.rule
  let ends := items.any fun it =>
    it.origin == 0 && it.next G == none && ((G.rules[it.rule]?).map (·.lhs)) == some G.start
  let ordered := items.toList.mergeSort fun a b => decide (a.rule < b.rule) || (a.rule == b.rule && decide (a.dot ≤ b.dot))
  let runs := ordered.filterMap fun it => match it.next G with
    | some (.t _) => (runOf G it).map fun r => (lexical it, r)
    | _ => none
  let structural := ((if ends then ["."] else []) ++ (runs.filter (!·.1)).map (·.2)).eraseDups
  let wordings := ((runs.filter (·.1)).map (·.2)).eraseDups
  let first ← toks[0]?
  let endOf (k : Nat) : Nat := if k == 0 then first.2.1 else ((toks[k - 1]?).map (·.2.2)).getD first.2.1
  let help := " Use the English paraphrase as a writing example."
  match toks[far]? with
  | some tok =>
    -- A declared wording that ends here, followed by a word that is no boundary and no clause head.
    let completed := ordered.filter fun it =>
      lexical it && it.next G == none && 0 < wordsRead G it && wordsRead G it ≤ far
    let names := (completed.filterMap fun it => (rows[it.rule - fixedCount]?).bind (·.act.predicate?)).eraseDups
    let tail := (tokWord? tok.1).filter fun x => !(phraseBoundaries ++ clauseHeads L).contains x
    match completed.head?, tail, names.isEmpty with
    | some it, some _, false =>
      let start := far - wordsRead G it
      let stop := (toks[phraseEnd w far]?).getD tok
      let begin := ((toks[start]?).map (·.2.1)).getD tok.2.1
      let existing := "; ".intercalate ((names.mergeSort (fun a b => decide (a < b) || a == b)).map fun p =>
        quoteText p ++ ": " ++ quoteText ((L.wordings.lookup p).getD p))
      pure ⟨s!"Phrase {quoteText (source.extract ⟨begin⟩ ⟨stop.2.2⟩)} extends existing wording {existing}; " ++
        "declare distinct wording by hand.", (endOf start, stop.2.2)⟩
    | _, _, _ =>
      if wordings.isEmpty then
        if structural.isEmpty then none
        else pure ⟨s!"Expected {orList structural} here." ++ help, (endOf far, tok.2.2)⟩
      else
        -- The phrase starts where the wording being read started: the hand parser's atom after its subject.
        let back := (ordered.filter fun it => lexical it && (it.next G).isSome).foldl
          (fun m it => max m (wordsRead G it)) 0
        let start := far - min back far
        let stop := (toks[phraseEnd w start]?).getD tok
        let stop := if stop.2.2 < tok.2.2 then tok else stop
        let begin := ((toks[start]?).map (·.2.1)).getD tok.2.1
        let phrase := source.extract ⟨begin⟩ ⟨stop.2.2⟩
        let nearest := "; ".intercalate ((nearestWordings L phrase).map quoteText)
        pure ⟨s!"Unknown English phrase {quoteText phrase}. Nearest declared wordings: {nearest}.",
          (endOf start, stop.2.2)⟩
  | none =>
    let all := (structural ++ wordings).eraseDups
    if all.isEmpty then none
    else pure ⟨s!"Expected {orList all} here." ++ help, (endOf far, endOf far + 1)⟩

end VE.EnglishGrammar
