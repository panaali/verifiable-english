import VE.EnglishGrammar.Fixed.RelationalFol
import VE.EnglishGrammar.Fixed.Order
import VE.EnglishGrammar.Fixed.Alternatives
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

S3 (docs/spec/english-lean-s3.md 2.4 to 2.6, 5.2): the fixed table of a profile list is the base table, then
the `order@0` table when that profile is named, then the `alternatives@0` table (D1); the rank certificate is
S2's `ranks` unless a staged profile is named, and `ranksStaged` otherwise (D2, D3), followed by a 0 for each
value sort. Under `order@0` a hole whose argument sort is `$int` is `int_term`, the subject and object relatives
are cut only at an object slot, and an integer constant gets the `int_constant` rows instead of the spelling
rows. Under `data@0` an attribute (a binary predicate declared functional and total) gets
`the r of term is term` and, for its value sort, `the r of term is property_i` over one property nonterminal
per value sort (D6); a unary predicate on a value sort is a property. Under `alternatives@0` the action sort's
selected noun gives the five guard rows, the two head rows and the other reference (D7). A name, a noun or a
spelling is spelled from its tokens with `textSyms` (D20).
-/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The base profile. -/
def baseProfile : String := "relational-fol@0"

/-- Whether a profile list names a staged profile, one whose presence changes the fixed rules (S3 spec 2.1). -/
def staged (profiles : List String) : Bool :=
  profiles.contains "order@0" || profiles.contains "data@0" || profiles.contains "alternatives@0"

/-- The fixed rows of a profile list (S3 D1): the base table when the base profile is named, then the
`order@0` table, then the `alternatives@0` table, each when its profile is named. `closure@0`, `data@0`,
`risk@0` and `norms@0` have no table of their own (spec 2.5). -/
def fixedTable (profiles : List String) : Array FixedRow :=
  (if profiles.contains baseProfile then relationalFolRows else #[]) ++
  (if profiles.contains "order@0" then orderRows else #[]) ++
  (if profiles.contains "alternatives@0" then alternativesRows else #[])

/-- The action texts of the fixed rows of a profile list, in the order of `fixedTable`. -/
def fixedActTexts (profiles : List String) : Array String :=
  (if profiles.contains baseProfile then relationalFolActs else #[]) ++
  (if profiles.contains "order@0" then orderActs else #[]) ++
  (if profiles.contains "alternatives@0" then alternativesActs else #[])

/-- The rank certificate of a profile list (S3 spec 2.4): S2's unless a staged profile is named. -/
def ranksFor (profiles : List String) : Array Nat := if staged profiles then ranksStaged else ranks

/-- The nonterminal names of a profile list: S2's catalogue, and the staged nonterminals when a staged profile
is named. -/
def ntNamesFor (profiles : List String) : Array String :=
  if staged profiles then ntNames ++ stagedNames else ntNames

/-- The fixed rules: row `i` of the table, whose action is `fixedActs[i]`. -/
def fixedRules (profiles : List String) : Array (Rule Terminal) :=
  (fixedTable profiles).mapIdx fun i r => { lhs := r.lhs, rhs := r.rhs, act := i, tag := r.tag }

/-- The three guard phrases of `alternatives@0` (S3 spec 2.1). -/
inductive GuardMode where
  | every | other | another
  deriving DecidableEq, Repr

def GuardMode.name : GuardMode → String
  | .every => "every"
  | .other => "other"
  | .another => "another"

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
  -- S3 (spec 2.6, 2.7)
  | attribute (r : String)
  | attributeProperty (r s : String)
  | guard (mode : GuardMode) (excluding : Bool) (action noun available : String) (risk : Bool)
  | altHead (reference : String)
  | termOther (noun : String)
  deriving DecidableEq, Repr

/-- A lexical rule with its action. -/
structure LexRow where
  tag : String
  lhs : Nat
  rhs : List (Sym Terminal)
  act : LexAct
  deriving DecidableEq, Repr

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
The holes are lexed as words (`wordingTokens`, the substitution V3 reads), so the marks around them keep
the spacing a term gives them. -/
def wordingSyms (w : String) : Option (List Nat × List (Sym Terminal)) :=
  (wordingTokens w).map fun (order, toks) =>
    (order, toks.map fun t =>
      if isHoleWord order t then Sym.n ntTerm
      else match t with
        | .word x _ => .t (.content x)
        | t => .t (.exact t))

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

/-- A wording's hole order and symbols when each hole `k` is the nonterminal `slot k` (S3 spec 2.6): a word is
`content`, another token `exact`. -/
def wordingSymsBy (w : String) (slot : Nat → Nat) : Option (List Nat × List (Sym Terminal)) :=
  (wordingTokens w).map fun (order, toks) =>
    (order, toks.map fun t =>
      match t with
      | .word x _ =>
        match order.find? (fun k => x == holeMark k) with
        | some k => Sym.n (slot k)
        | none => .t (.content x)
      | t => .t (.exact t))

/-- The integer sort. -/
def intSort : String := "$int"

/-- The clause, subject relative and object relative of one wording of `p` with argument sorts `args`, in an
environment that names `order@0` (S3 spec 2.6): a hole is `int_term` when its argument sort is `$int`; the
subject relative exists when `{0}` is an object slot, the object relative when `{1}` is. -/
def clauseRowsOrder (p w : String) (negated : Bool) (suffix : String) (args : List String) : List LexRow :=
  let isInt := fun (k : Nat) => args.getD k "" == intSort
  let slot := fun (k : Nat) => if isInt k then ntIntTerm else ntTerm
  match wordingSymsBy w slot with
  | none => []
  | some (order, syms) =>
    let subject := if !isInt 0 && syms.head? == some (Sym.n ntTerm) then some syms.tail else none
    let object :=
      if order.length == 2 && occurs " {1}" w && !isInt 1 then
        (wordingSymsBy (replaceFirst w " {1}" "") slot).map (·.2)
      else none
    [{ tag := "clause." ++ p ++ suffix, lhs := ntAtom, rhs := syms, act := .pred p order negated }] ++
    (match subject with
     | some r => [{ tag := "relative." ++ p ++ suffix, lhs := ntRelative, rhs := r,
                    act := .relSubject p order negated }]
     | none => []) ++
    match object with
    | some o => [{ tag := "object-relative." ++ p ++ suffix, lhs := ntObjectRelative, rhs := o,
                   act := .relObject p negated }]
    | none => []

/-- The clause rows of a wording (spec 2.6): S2's when `order@0` is not named; otherwise by the argument
sorts of every declaration of `p` (S3). -/
def wordingRows (E : Env) (p w : String) (negated : Bool) (suffix : String) : List LexRow :=
  if E.profiles.contains "order@0" then
    (E.predicates.filter (·.name == p)).flatMap fun d => clauseRowsOrder p w negated suffix d.args
  else clauseRows p w negated suffix

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

/-- The integer-constant rows of constant `c` with spelling `sp` (S3 spec 2.6): `int_constant → sp`, and
`int_plain_constant → sp` when the spelling is one lower-case word. -/
def intConstantRows (c sp : String) : List LexRow :=
  match textSyms sp keywordTerminal with
  | none => []
  | some syms =>
    [{ tag := "int-constant." ++ c, lhs := ntIntConstant, rhs := syms, act := .const c intSort false }] ++
    (if lowerWord sp then
      [{ tag := "int-plain-constant." ++ c, lhs := ntIntPlainConstant, rhs := syms, act := .const c intSort false }]
     else [])

/-- The rows of a spelling of a constant declared with sort `s` (spec 2.6): under `order@0` an integer
constant gets the integer rows (S3), any other constant S2's spelling rows. -/
def constantRows (E : Env) (c s sp : String) : List LexRow :=
  if E.profiles.contains "order@0" && s == intSort then intConstantRows c sp else spellingRows c s sp

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

/-- The value sort of an attribute declaration (S3 spec 2.1): the second argument sort of a binary predicate
declared functional and total, when it is not `$string`. -/
def valueSortOf (d : PredDecl) : Option String :=
  match d.args with
  | [_, b] => if d.functional && d.total && b != "$string" then some b else none
  | _ => none

/-- The value sorts of an environment (S3 spec 2.4): none unless `data@0` is named; otherwise each value sort
once, in the order of the first attribute that has it (`dedup` keeps the last occurrence, so it reads the
reversed list). -/
def valueSorts (E : Env) : List String :=
  if E.profiles.contains "data@0" then (dedup (E.predicates.filterMap valueSortOf).reverse).reverse else []

/-- The position of the first occurrence of `a`. -/
def indexIn {α : Type} [DecidableEq α] (a : α) : List α → Nat
  | [] => 0
  | x :: xs => if x = a then 0 else indexIn a xs + 1

/-- The property nonterminal of a value sort (S3 spec 2.4): `51 + i` for the `i`-th value sort. -/
def propertyNt (E : Env) (s : String) : Nat := ntProperty + indexIn s (valueSorts E)

/-- The attribute rows of a declaration (S3 spec 2.6): `the r of term is term` for an attribute, and
`the r of term is property_i` when its second sort is the `i`-th value sort. -/
def attributeRows (E : Env) (d : PredDecl) : List LexRow :=
  match d.args, textSyms d.name keywordTerminal with
  | [_, b], some r =>
    if d.functional && d.total then
      let head : List (Sym Terminal) := Sym.t (.kw "the") :: r ++ [.t (.kw "of"), .n ntTerm, .t (.kw "is")]
      [{ tag := "attribute." ++ d.name, lhs := ntAtom, rhs := head ++ [.n ntTerm], act := .attribute d.name }] ++
      (if (valueSorts E).contains b then
        [{ tag := "attribute-property." ++ d.name, lhs := ntAtom, rhs := head ++ [.n (propertyNt E b)],
           act := .attributeProperty d.name b }]
       else [])
    else []
  | _, _ => []

/-- The property row of a unary declaration on a value sort (S3 spec 2.6). -/
def propertyRows (E : Env) (d : PredDecl) : List LexRow :=
  match d.args, textSyms d.name keywordTerminal with
  | [s], some p =>
    if (valueSorts E).contains s then
      [{ tag := "property." ++ d.name, lhs := propertyNt E s, rhs := p, act := .adjective d.name s }]
    else []
  | _, _ => []

/-- The guard family of the block `B` for the action sort's selected noun `n` (S3 spec 2.6): the five guard
rows, the two head rows and the other reference. The noun is spelled by `textSyms` (D20). -/
def guardRows (E : Env) (B : AltBlock) (n : String) : List LexRow :=
  match textSyms n keywordTerminal, textSyms n contentTerminal with
  | some N, some Nc =>
    let tail := fun (excluding : Bool) => [Sym.t (.kw "available"), .t (.kw "to"), .n ntTerm] ++
      (if excluding then [.t (.kw "excluding"), .n ntTerm] else []) ++ [.n ntAltVerbPhrase]
    let guard := fun (mode : GuardMode) (excluding : Bool) (head : List (Sym Terminal)) (tag : String) =>
      ({ tag := "guard." ++ tag ++ "." ++ B.action, lhs := ntAltGuard, rhs := head ++ N ++ tail excluding,
         act := .guard mode excluding B.action n B.available E.risk } : LexRow)
    [guard .every false [.t (.kw "every")] "every",
     guard .other false [.t (.kw "every"), .t (.kw "other")] "every-other",
     guard .another false [.t (.kw "another")] "another",
     guard .other true [.t (.kw "every"), .t (.kw "other")] "every-other-excluding",
     guard .another true [.t (.kw "another")] "another-excluding",
     { tag := "head.that." ++ B.action, lhs := ntAltHead, rhs := .t (.kw "that") :: N,
       act := .altHead ("that " ++ n) },
     { tag := "head.that-other." ++ B.action, lhs := ntAltHead, rhs := .t (.kw "that") :: .t (.kw "other") :: N,
       act := .altHead ("that other " ++ n) },
     { tag := "term.that-other." ++ B.action, lhs := ntTerm, rhs := .t (.content "that") :: .t (.content "other") :: Nc,
       act := .termOther n }]
  | _, _ => []

/-- Every lexical row, in the order of the lexicon's lists, before repeated rows are dropped. -/
def lexRowsAll (E : Env) (L : Lexicon) : List LexRow :=
  (L.wordings.flatMap fun (p, w) => wordingRows E p w false "") ++
  (L.negatives.flatMap fun (p, w) => wordingRows E p w true ".negative") ++
  (L.aliases.flatMap fun (p, w, neg) => wordingRows E p w neg ".alias") ++
  (L.nouns.flatMap fun (s, n) =>
    match textSyms n contentTerminal with
    | some ns => [{ tag := "noun." ++ s, lhs := ntNoun, rhs := ns, act := .noun s n }]
    | none => []) ++
  (L.letters.map fun (s, l) =>
    { tag := "label." ++ s, lhs := ntLabel, rhs := [.t (.cls (.label l))], act := .label s }) ++
  (L.spellings.flatMap fun (c, sp) =>
    (E.constants.filter (·.name == c)).flatMap fun d => constantRows E c d.sort sp) ++
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
    | _ => []) ++
  -- S3: attributes and properties under `data@0`, the guard family under `alternatives@0`
  (if E.profiles.contains "data@0" then E.predicates.flatMap (attributeRows E) else []) ++
  (if E.profiles.contains "data@0" then E.predicates.flatMap (propertyRows E) else []) ++
  (match E.alternatives with
   | some B => if E.profiles.contains "alternatives@0" then
       (L.nouns.filter (·.1 == B.action)).flatMap fun (_, n) => guardRows E B n
     else []
   | none => [])

/-- No terminal of the row accepts a terminator (W4). -/
def LexRow.terminatorFree (r : LexRow) : Bool :=
  r.rhs.all fun
    | .t a => terminators.all fun x => !a.accepts x
    | .n _ => true

/-- The lexical rows of spec 2.6: repeated rows dropped, rows with a terminator dropped. -/
def lexRows (E : Env) (L : Lexicon) : List LexRow :=
  (dedup (lexRowsAll E L)).filter LexRow.terminatorFree

/-- The lexical rules: row `i`, whose action is `acts E L` at `(fixedTable E.profiles).size + i`. -/
def lexRules (E : Env) (L : Lexicon) : Array (Rule Terminal) :=
  (lexRows E L).toArray.mapIdx fun i r =>
    { lhs := r.lhs, rhs := r.rhs, act := (fixedTable E.profiles).size + i, tag := r.tag }

/-- The English grammar (D1): the fixed rules of the profiles, then the lexical rules; the start
symbol is `sentence`; the ranks are the certificate of the profile list (S3 spec 2.4) and a 0 for each
property nonterminal. -/
def grammar (E : Env) (L : Lexicon) : Grammar Terminal :=
  { rules := fixedRules E.profiles ++ lexRules E L, start := 0,
    rank := ranksFor E.profiles ++ Array.replicate (valueSorts E).length 0 }

/-- The type table of S3 spec 2.4: the catalogue's types below 51, `adjective` for each property
nonterminal, `tok` beyond. It does not depend on the lexicon. -/
def ty (E : Env) (_L : Lexicon) (n : Nat) : Ty :=
  if n < ntProperty then ntTy n else if n < ntProperty + (valueSorts E).length then .adjective else .tok

-- The indices named in `Catalogue.lean` are those of the generated names and the staged names, and `ntTy`
-- types exactly the catalogue with the staged nonterminals (spec 2.4; S3 spec 2.4).
#guard [ntAtom, ntTerm, ntNoun, ntLabel, ntConstant, ntRelative, ntObjectRelative, ntAdjective,
    ntCopulaRelative, ntCopulaAdjective, ntNaturalSubject, ntOwnerClause, ntRelation].map (ntNames[·]?) ==
  ["atom", "term", "noun", "label", "constant", "relative", "object_relative", "adjective", "copula_relative",
    "copula_adjective", "natural_subject", "owner_clause", "relation"].map some
#guard ranks.size == ntNames.size
#guard [ntIntTerm, ntIntConstant, ntIntPlainConstant, ntAltGuard, ntAltVerbPhrase, ntAltHead].map
    ((ntNames ++ stagedNames)[·]?) ==
  ["int_term", "int_constant", "int_plain_constant", "alt_available_guard", "alt_verb_phrase", "alt_head"].map some
#guard ranksStaged.size == ntNames.size + stagedNames.size && ntProperty == ranksStaged.size
#guard (List.range (ntNames.size + stagedNames.size)).all (fun i => decide (ntTy i ≠ .tok)) &&
  decide (ntTy ntProperty = .tok)
#guard ranksStaged.toList.take ntNames.size != ranks.toList
-- `valueSorts` lists each value sort once, in the order of its first attribute
#guard valueSorts { sorts := [], constants := [], profiles := ["data@0"], predicates :=
    [{ name := "a", arity := 2, args := ["x", "s"], functional := true, total := true },
     { name := "b", arity := 2, args := ["x", "t"], functional := true, total := true },
     { name := "c", arity := 2, args := ["x", "s"], functional := true, total := true },
     { name := "d", arity := 2, args := ["x", "$string"], functional := true, total := true },
     { name := "e", arity := 2, args := ["x", "u"], functional := true }] } == ["s", "t"]

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

/-! ## The statements of S3 spec 5.5 on the catalogue, the ranks and subject first -/

theorem unstaged_fixed : ∀ (profiles : List String), staged profiles = false →
    profiles.contains baseProfile = true → fixedTable profiles = relationalFolRows ∧ ranksFor profiles = ranks := by
  intro profiles hs hb
  have hs' := hs
  unfold staged at hs'
  simp only [Bool.or_eq_false_iff] at hs'
  obtain ⟨⟨ho, _⟩, ha⟩ := hs'
  unfold fixedTable ranksFor
  simp only [hb, ho, ha, hs, if_true, Bool.false_eq_true, if_false, Array.append_empty]
  exact ⟨trivial, trivial⟩

theorem ty_catalogue : ∀ (E : Env) (L : Lexicon) (n : Nat), n < 37 → ty E L n = ntTy n := by
  intro E L n h
  unfold ty
  rw [if_pos (by unfold ntProperty; omega)]

theorem ty_property : ∀ (E : Env) (L : Lexicon) (i : Nat), i < (valueSorts E).length →
    ty E L (51 + i) = .adjective := by
  intro E L i h
  unfold ty
  rw [if_neg (by unfold ntProperty; omega), if_pos (by unfold ntProperty; omega)]

/-- An element of a list is an element of its `eraseDups`. -/
theorem mem_eraseDupsBy_loop {α : Type} [BEq α] [LawfulBEq α] : ∀ (as bs : List α) (x : α),
    x ∈ as ∨ x ∈ bs → x ∈ List.eraseDupsBy.loop (· == ·) as bs
  | [], bs, x, h => by
    unfold List.eraseDupsBy.loop
    rcases h with h | h
    · exact absurd h List.not_mem_nil
    · exact List.mem_reverse.mpr h
  | a :: as, bs, x, h => by
    unfold List.eraseDupsBy.loop
    split
    · rename_i hany
      apply mem_eraseDupsBy_loop
      rcases h with h | h
      · rcases List.mem_cons.mp h with rfl | h
        · obtain ⟨y, hy, hxy⟩ := List.any_eq_true.mp hany
          right; rw [eq_of_beq hxy]; exact hy
        · exact Or.inl h
      · exact Or.inr h
    · apply mem_eraseDupsBy_loop
      rcases h with h | h
      · rcases List.mem_cons.mp h with rfl | h
        · exact Or.inr List.mem_cons_self
        · exact Or.inl h
      · exact Or.inr (List.mem_cons_of_mem _ h)

theorem mem_eraseDups {α : Type} [BEq α] [LawfulBEq α] {x : α} {l : List α} (h : x ∈ l) : x ∈ l.eraseDups :=
  mem_eraseDupsBy_loop l [] x (Or.inl h)

theorem valid_subject_first : ∀ (E : Env) (O : Overlay) (L : Lexicon), L.valid E O = true →
    (∀ x ∈ L.wordings, subjectFirst x.2 = true) ∧ (∀ x ∈ L.negatives, subjectFirst x.2 = true) ∧
    (∀ x ∈ L.aliases, subjectFirst x.2.1 = true) := by
  intro E O L hv
  have hnil : L.failures E O = [] := (valid_iff_no_failure E O L).mp hv
  have no : ∀ f, f ∈ L.failures E O → False := fun f hf => by rw [hnil] at hf; exact List.not_mem_nil hf
  refine ⟨fun ⟨p, w⟩ hx => ?_, fun ⟨p, w⟩ hx => ?_, fun ⟨p, w, neg⟩ hx => ?_⟩
  · apply Classical.byContradiction
    intro hn
    simp only [Bool.not_eq_true] at hn
    by_cases hp : (E.predicates.map (·.name)).contains p = true
    · apply no ("V3", "predicate", p)
      unfold Lexicon.failures
      simp only [List.mem_append]
      left; left; left; left; left; right
      refine List.mem_flatMap.mpr ⟨(p, w), hx, ?_⟩
      have hp' : ∃ a ∈ E.predicates, a.name = p := by simpa using hp
      simp [hp', hn]
    · apply no ("V1", "predicate", p)
      unfold Lexicon.failures
      simp only [List.mem_append]
      left; left; left; left; left; left
      unfold coverage
      simp only [List.mem_append]
      left; left; left; right; right
      simp only [Bool.not_eq_true] at hp
      exact List.mem_map.mpr ⟨p, List.mem_filter.mpr ⟨List.mem_map.mpr ⟨(p, w), hx, rfl⟩, by simpa using hp⟩, rfl⟩
  · apply Classical.byContradiction
    intro hn
    simp only [Bool.not_eq_true] at hn
    by_cases hp : (E.predicates.map (·.name)).contains p = true
    · apply no ("V3", "negative", p)
      unfold Lexicon.failures
      simp only [List.mem_append]
      left; left; left; left; right
      refine List.mem_flatMap.mpr ⟨(p, w), hx, ?_⟩
      have hp' : ∃ a ∈ E.predicates, a.name = p := by simpa using hp
      simp [hp', hn]
    · apply no ("V1", "negative", p)
      unfold Lexicon.failures
      simp only [List.mem_append]
      left; left; left; left; left; left; left; right
      simp only [Bool.not_eq_true] at hp
      exact List.mem_map.mpr ⟨p, List.mem_filter.mpr ⟨List.mem_map.mpr ⟨(p, w), hx, rfl⟩, by rw [hp]; simp⟩, rfl⟩
  · apply Classical.byContradiction
    intro hn
    simp only [Bool.not_eq_true] at hn
    by_cases hp : (E.predicates.map (·.name)).contains p = true
    · apply no ("V3", "alias", p)
      unfold Lexicon.failures
      simp only [List.mem_append]
      left; left; left; right
      refine List.mem_flatMap.mpr ⟨p, mem_eraseDups (List.mem_append_left _
        (List.mem_map.mpr ⟨(p, w, neg), hx, rfl⟩)), ?_⟩
      have hsel : (w, neg) ∈ (L.aliases.filter (·.1 == p)).map (·.2) :=
        List.mem_map.mpr ⟨(p, w, neg), List.mem_filter.mpr ⟨hx, by simp⟩, rfl⟩
      simp only [List.mem_append]
      right
      have hall : (((L.aliases.filter (·.1 == p)).map (·.2)).all fun a =>
          shapeOk a.1 (E.arity p) && subjectFirst a.1) = false := by
        apply Bool.eq_false_iff.mpr
        intro h
        have := List.all_eq_true.mp h (w, neg) hsel
        simp [hn] at this
      simp [hall]
    · apply no ("V1", "alias", p)
      unfold Lexicon.failures
      simp only [List.mem_append]
      left; left; left; left; left; left; right
      simp only [Bool.not_eq_true] at hp
      exact List.mem_map.mpr ⟨p, List.mem_filter.mpr ⟨List.mem_map.mpr ⟨(p, w, neg), hx, rfl⟩, by simpa using hp⟩, rfl⟩

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
