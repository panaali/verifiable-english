import VE.EnglishGrammar.Fixed.RelationalFol
import VE.EnglishGrammar.Lexicon
import VE.Grammar.TableProofs

/-! The English grammar of an environment and a lexicon (docs/spec/english-lean-s2.md 2.4 to 2.6 and
5.6): the fixed rules of the profiles followed by the lexical rules, over the catalogue of
`VE.EnglishGrammar.Catalogue`.

`lexRows E L` builds the lexical rules, each with the name of its action and the data the action
carries (`LexAct`), by one procedure per family of spec 2.6: a wording, a negative and an alias give
the clause, the subject relative (Lark's cut: one leading `term` stripped, whichever hole it is) and,
for a binary wording that contains ` {1}`, the object relative (` {1}` deleted from the text); a noun,
a letter and a spelling give their rules; a unary `{0} is a` wording gives the adjective, natural
subject and copula rules; `{0} owns {1}` gives the owner clause; a binary predicate over one sort gives
its relation. A text becomes symbols through the lexer (`lex`): a word is `content` (`kw` in a
spelling), any other token an `exact` terminal, a hole the nonterminal `term`. A text that does not lex
as one sentence gives no rule (V3 makes that visible for wordings). Each row is built from one lexicon
entry and, where a family needs a sort, from the signature of every declaration of that name, so an
extension that keeps the entry and the signature keeps the row (`grammar_extension`). Repeated rows
are dropped, and so is a row with a terminal that accepts a terminator, which the lexer never puts
inside a sentence: `lexRules_terminatorFree` holds by construction.
-/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The base profile. -/
def baseProfile : String := "relational-fol@0"

/-- The fixed rows of a profile list: the base table when the base profile is named. `closure@0` has no
table of its own; the typed check enforces it (spec 2.5). -/
def fixedTable (profiles : List String) : Array FixedRow :=
  if profiles.contains baseProfile then relationalFolRows else #[]

/-- The fixed rules: row `i` of the table, whose action is `fixedActs[i]`. -/
def fixedRules (profiles : List String) : Array (Rule Terminal) :=
  (fixedTable profiles).mapIdx fun i r => { lhs := r.lhs, rhs := r.rhs, act := i, tag := r.tag }

/-- The lexical actions of spec 2.7, each with the data spec 2.6 names. -/
inductive LexAct where
  | pred (p : String) (order : List Nat) (negated : Bool)
  | relSubject (p : String) (order : List Nat) (negated : Bool)
  | relObject (p : String) (negated : Bool)
  | noun (s n : String)
  | label (s : String)
  | const (c s : String) (nameForm : Bool)
  | adjective (p s : String)
  | natSubject (p s n : String)
  | copulaRel (p : String)
  | owner (s1 s2 : String)
  | relation (r : String)
  deriving DecidableEq, Repr

/-- A lexical rule with its action. -/
structure LexRow where
  tag : String
  lhs : Nat
  rhs : List (Sym Terminal)
  act : LexAct
  deriving DecidableEq, Repr

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

/-- A word of a wording, a noun or a relation name matches in any case; another token exactly. -/
def contentTerminal : Tok → Terminal
  | .word text _ => .content text
  | t => .exact t

/-- A word of a spelling matches as written (`kw`); another token exactly. -/
def keywordTerminal : Tok → Terminal
  | .word text _ => .kw text
  | t => .exact t

/-- A text without holes as terminals, or none. -/
def textSyms (text : String) (k : Tok → Terminal) : Option (List (Sym Terminal)) :=
  (sentenceTokens text).map fun toks => toks.map fun t => .t (k t)

/-- A wording's hole order and symbols: a hole is `term`, a word `content`, another token `exact`.
The holes are lexed as words, so the marks around them keep the spacing a term gives them. -/
def wordingSyms (w : String) : Option (List Nat × List (Sym Terminal)) :=
  if w.any (· == holeChar) then none
  else
    match fillHoles w holeMark with
    | (order, text) =>
      match sentenceTokens text with
      | none => none
      | some toks =>
        let syms := toks.map fun t =>
          match t with
          | .word x _ => if order.any (fun k => x == holeMark k) then Sym.n ntTerm else .t (.content x)
          | t => .t (.exact t)
        if (syms.filter (· == Sym.n ntTerm)).length == order.length then some (order, syms) else none

/-- Whether `pat` occurs in `s`. -/
def occurs (pat s : String) : Bool := (findSub pat.toList s.toList 0).isSome

/-- The clause, subject relative and object relative of one wording of `p` (spec 2.6). -/
def clauseRows (p w : String) (negated : Bool) (suffix : String) : List LexRow :=
  match wordingSyms w with
  | none => []
  | some (order, syms) =>
    let subject := if syms.head? == some (Sym.n ntTerm) then syms.tail else syms
    let object :=
      if order.length == 2 && occurs " {1}" w then (wordingSyms (replaceFirst w " {1}" "")).map (·.2)
      else none
    [{ tag := "clause." ++ p ++ suffix, lhs := ntAtom, rhs := syms, act := .pred p order negated },
     { tag := "relative." ++ p ++ suffix, lhs := ntRelative, rhs := subject,
       act := .relSubject p order negated }] ++
    match object with
    | some o => [{ tag := "object-relative." ++ p ++ suffix, lhs := ntObjectRelative, rhs := o,
                   act := .relObject p negated }]
    | none => []

/-- Python's name form (`english.py:1574`): letters and single spaces, optionally after `the `. -/
def nameForm (sp : String) : Bool :=
  let body := if sp.startsWith "the " then sp.drop 4 else sp
  let ws := body.splitOn " "
  !ws.isEmpty && ws.all fun w => !w.isEmpty && w.all fun c => ('a' ≤ c && c ≤ 'z') || ('A' ≤ c && c ≤ 'Z')

/-- One lower-case ASCII word. -/
def lowerWord (s : String) : Bool := !s.isEmpty && s.all fun c => 'a' ≤ c && c ≤ 'z'

/-- The spelling rules of constant `c` of sort `s` (spec 2.6): the spelling; `the` and the spelling
when it is one lower-case word; the capitalised form when it begins with `the `. -/
def spellingRows (c s sp : String) : List LexRow :=
  match sentenceTokens sp with
  | none => []
  | some toks =>
    let syms := toks.map fun t => Sym.t (keywordTerminal t)
    [{ tag := "constant." ++ c, lhs := ntConstant, rhs := syms, act := .const c s (nameForm sp) }] ++
    (if lowerWord sp then
      [{ tag := "constant." ++ c ++ ".the", lhs := ntConstant, rhs := .t (.kw "the") :: syms,
         act := .const c s false }]
     else []) ++
    (if sp.startsWith "the " then
      [{ tag := "constant." ++ c ++ ".capital", lhs := ntConstant, rhs := .t (.kwMid "The") :: syms.drop 1,
         act := .const c s (nameForm sp) }]
     else [])

/-- The adjective of a selected wording `{0} is a` with `a` one lower-case word. -/
def adjectiveOf (w : String) : Option String :=
  if w.startsWith "{0} is " && lowerWord (w.drop 7) then some (w.drop 7) else none

/-- The adjective, natural-subject and copula rules of a unary `p` on sort `s` (spec 2.6). -/
def adjectiveRows (L : Lexicon) (p s a : String) : List LexRow :=
  [{ tag := "adjective." ++ p, lhs := ntAdjective, rhs := [.t (.content a)], act := .adjective p s }] ++
  (L.nouns.filter (·.1 == s)).flatMap fun (_, n) =>
    match textSyms n contentTerminal with
    | none => []
    | some ns =>
      [{ tag := "natural-subject." ++ p, lhs := ntNaturalSubject, rhs := .t (.content a) :: ns,
         act := .natSubject p s n },
       { tag := "copula." ++ p, lhs := ntCopulaRelative, rhs := [.t (.content "is"), .t (.content a)],
         act := .copulaRel p },
       { tag := "copula-adjective." ++ p, lhs := ntCopulaAdjective, rhs := [.t (.content a)],
         act := .adjective p s }]

/-- The declarations of a predicate name. -/
def declsOf (E : Env) (p : String) : List PredDecl := E.predicates.filter (·.name == p)

/-- Every lexical row, in the order of the lexicon's lists, before repeated rows are dropped. -/
def lexRowsAll (E : Env) (L : Lexicon) : List LexRow :=
  (L.wordings.flatMap fun (p, w) => clauseRows p w false "") ++
  (L.negatives.flatMap fun (p, w) => clauseRows p w true ".negative") ++
  (L.aliases.flatMap fun (p, w, neg) => clauseRows p w neg ".alias") ++
  (L.nouns.flatMap fun (s, n) =>
    match textSyms n contentTerminal with
    | some ns => [{ tag := "noun." ++ s, lhs := ntNoun, rhs := ns, act := .noun s n }]
    | none => []) ++
  (L.letters.map fun (s, l) =>
    { tag := "label." ++ s, lhs := ntLabel, rhs := [.t (.cls (.label l))], act := .label s }) ++
  (L.spellings.flatMap fun (c, sp) =>
    (E.constants.filter (·.name == c)).flatMap fun d => spellingRows c d.sort sp) ++
  (L.wordings.flatMap fun (p, w) =>
    match adjectiveOf w with
    | some a => (declsOf E p).flatMap fun d =>
        match d.args with
        | [s] => adjectiveRows L p s a
        | _ => []
    | none => []) ++
  (L.wordings.flatMap fun (p, w) =>
    if p == "owns" && w == "{0} owns {1}" then
      (declsOf E p).flatMap fun d =>
        match d.args with
        | [s1, s2] => [{ tag := "owner", lhs := ntOwnerClause,
                         rhs := [.t (.kw "has"), .t (.kw "an"), .t (.kw "owner")], act := .owner s1 s2 }]
        | _ => []
    else []) ++
  (E.predicates.flatMap fun d =>
    match d.args with
    | [a, b] =>
      if a == b then
        match textSyms (jsonQuote d.name) contentTerminal with
        | some q => [{ tag := "relation." ++ d.name, lhs := ntRelation, rhs := q, act := .relation d.name }]
        | none => []
      else []
    | _ => [])

/-- No terminal of the row accepts a terminator (W4). -/
def LexRow.terminatorFree (r : LexRow) : Bool :=
  r.rhs.all fun
    | .t a => terminators.all fun x => !a.accepts x
    | .n _ => true

/-- The lexical rows of spec 2.6: repeated rows dropped, rows with a terminator dropped. -/
def lexRows (E : Env) (L : Lexicon) : List LexRow :=
  (dedup (lexRowsAll E L)).filter LexRow.terminatorFree

/-- The lexical rules: row `i`, whose action is `acts E L` at `relationalFolRows.size + i`. -/
def lexRules (E : Env) (L : Lexicon) : Array (Rule Terminal) :=
  (lexRows E L).toArray.mapIdx fun i r =>
    { lhs := r.lhs, rhs := r.rhs, act := relationalFolRows.size + i, tag := r.tag }

/-- The English grammar (D1): the fixed rules of the profiles, then the lexical rules; the start
symbol is `sentence`; the ranks are the certificate of spec 2.4. -/
def grammar (E : Env) (L : Lexicon) : Grammar Terminal :=
  { rules := fixedRules E.profiles ++ lexRules E L, start := 0, rank := ranks }

/-- The type table of spec 2.4, independent of the environment and the lexicon. -/
def ty (_E : Env) (_L : Lexicon) : Nat → Ty := ntTy

-- The indices named in `Catalogue.lean` are those of the generated names, and `ntTy` types exactly the
-- catalogue (spec 2.4).
#guard [ntAtom, ntTerm, ntNoun, ntLabel, ntConstant, ntRelative, ntObjectRelative, ntAdjective,
    ntCopulaRelative, ntCopulaAdjective, ntNaturalSubject, ntOwnerClause, ntRelation].map (ntNames[·]?) ==
  ["atom", "term", "noun", "label", "constant", "relative", "object_relative", "adjective", "copula_relative",
    "copula_adjective", "natural_subject", "owner_clause", "relation"].map some
#guard (List.range ntNames.size).all (fun i => decide (ntTy i ≠ .tok)) && decide (ntTy ntNames.size = .tok)
#guard ranks.size == ntNames.size

theorem grammar_rules : ∀ (E : Env) (L : Lexicon),
    (grammar E L).rules = fixedRules E.profiles ++ lexRules E L :=
  fun _ _ => rfl

theorem start_sentence : ∀ (E : Env) (L : Lexicon), ty E L (grammar E L).start = .sentence :=
  fun _ _ => rfl

theorem valid_iff_no_failure : ∀ (E : Env) (O : Overlay) (L : Lexicon),
    L.valid E O = true ↔ L.failures E O = [] := by
  intro E O L
  unfold Lexicon.valid
  exact List.isEmpty_iff

theorem lexRules_terminatorFree : ∀ (E : Env) (L : Lexicon),
    terminatorFree { rules := lexRules E L, start := 0, rank := #[] } = true := by
  intro E L
  unfold terminatorFree lexRules
  rw [Array.all_eq_true]
  intro i hi
  simp only [Array.size_mapIdx, List.size_toArray] at hi
  simp only [Array.getElem_mapIdx, List.getElem_toArray]
  have hmem : (lexRows E L)[i] ∈ lexRows E L := List.getElem_mem hi
  unfold lexRows at hmem
  exact (List.mem_filter.mp hmem).2

end VE.EnglishGrammar
