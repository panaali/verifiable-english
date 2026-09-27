import VE.Syntax

/-! # Abstract lexicon of the writable English surface (PLAN-EXPAND2 W7)

The English surface (`ve_english`, `docs/english-surface.md`) is modelled at the
token level. Whitespace, sentence-initial capitalisation and list indentation are
presentation and belong to the lexer (Lean coverage pending for that layer);
tokens are words, punctuation words such as `","` and `"(a)"`, and numbered
labels such as `S1`.

A lexicon gives each sort a singular noun and a label letter, each predicate a
template (a token list with numbered placeholder positions), and each constant
its displayed spelling. `Admitted` collects the lexical conditions under which
the core grammar is proved unambiguous; they are properties of the finite
vocabulary, independent of any sentence. -/
namespace VE.English

inductive Tok where
  | word (text : String)
  | label (letter : String) (index : Nat)
  deriving DecidableEq, Repr, Inhabited

def kw (s : String) : Tok := .word s

def kws (xs : List String) : List Tok := xs.map Tok.word

/-- A template slot: a literal word or the placeholder of argument `index`. -/
inductive Slot where
  | word (text : String)
  | hole (index : Nat)
  deriving DecidableEq, Repr

abbrev Template := List Slot

def Slot.isHole : Slot → Bool
  | .hole _ => true
  | .word _ => false

def Template.arity (T : Template) : Nat := (T.filter Slot.isHole).length

/-- Instantiate a template: literal words are copied, placeholder `i` becomes
the tokens of argument `i`. -/
def fill (T : Template) (args : List (List Tok)) : List Tok :=
  T.flatMap fun
    | .word w => [.word w]
    | .hole i => args.getD i []

structure Lexicon where
  sorts : List String
  noun : String → List String
  letter : String → String
  predicates : List String
  template : String → Option Template
  constants : List String
  spelling : String → List String

/-- The four naming forms of a bound entity (`EnglishTraversal.binding`):
`that person`; `the first person`/`the second person`; a numbered label. -/
inductive Ref where
  | plain (sort : String)
  | first (sort : String)
  | second (sort : String)
  | named (sort : String) (index : Nat)
  deriving DecidableEq, Repr, Inhabited

def Ref.sort : Ref → String
  | .plain s | .first s | .second s | .named s _ => s

/-- Declaration tokens: `person`, `first person`, `person named S1`. -/
def Ref.declYield (L : Lexicon) : Ref → List Tok
  | .plain s => kws (L.noun s)
  | .first s => kw "first" :: kws (L.noun s)
  | .second s => kw "second" :: kws (L.noun s)
  | .named s k => kws (L.noun s) ++ [kw "named", .label (L.letter s) k]

/-- Reference tokens: `that person`, `the first person`, `S1`. -/
def Ref.refYield (L : Lexicon) : Ref → List Tok
  | .plain s => kw "that" :: kws (L.noun s)
  | .first s => kw "the" :: kw "first" :: kws (L.noun s)
  | .second s => kw "the" :: kw "second" :: kws (L.noun s)
  | .named s k => [.label (L.letter s) k]

inductive TermTree where
  | const (name : String)
  | ref (r : Ref)
  deriving DecidableEq, Repr, Inhabited

def TermTree.yield (L : Lexicon) : TermTree → List Tok
  | .const c => kws (L.spelling c)
  | .ref r => r.refYield L

def TermTree.ok (L : Lexicon) : TermTree → Bool
  | .const c => L.constants.contains c
  | .ref r => L.sorts.contains r.sort

/-- Simple clauses: the operands of compact `both … and …`/`either … or …`. -/
inductive Lit where
  | truth
  | falsity
  | eq (a b : TermTree)
  | pred (predicate : String) (args : List TermTree)
  deriving DecidableEq, Repr, Inhabited

def Lit.yield (L : Lexicon) : Lit → List Tok
  | .truth => kws ["this", "holds", "in", "all", "cases"]
  | .falsity => kws ["this", "is", "impossible"]
  | .eq a b => a.yield L ++ kws ["is", "the", "same", "as"] ++ b.yield L
  | .pred p args => match L.template p with
    | some T => fill T (args.map (TermTree.yield L))
    | none => []

/-- A lexically valid simple clause: known symbols, and each argument's
placeholder occurs in the predicate's template. -/
def Lit.ok (L : Lexicon) : Lit → Bool
  | .truth | .falsity => true
  | .eq a b => a.ok L && b.ok L
  | .pred p args => L.predicates.contains p && args.all (TermTree.ok L) &&
      match L.template p with
      | some T => args.length == T.arity &&
          (List.range args.length).all fun i => T.contains (.hole i)
      | none => false

/-- Tokens that end a simple clause. -/
def atomStops : List Tok := kws [",", ";", ".", "and", "or"]

/-- Tokens that can follow a complete formula. -/
def formulaStops : List Tok := kws [",", ";", "."]

/-- Tokens that open a compound formula (or a list header after `both`). -/
def openers : List Tok := kws ["it", "both", "either", "if", "all", "at", "for", "there", "of"]

/-- Lexical conditions for the core theorems. The first three are properties
of the clause language of the vocabulary, the last two of its sort nouns. The
finite check `admissible` (`Check.lean`) implies all five (`admissible_sound`). -/
structure Admitted (L : Lexicon) : Prop where
  atom_unique : ∀ a b : Lit, a.ok L = true → b.ok L = true → a.yield L = b.yield L → a = b
  atom_delimited : ∀ a : Lit, a.ok L = true → ∀ x ∈ a.yield L, x ∉ atomStops
  atom_opens : ∀ a : Lit, a.ok L = true → ∃ x rest, a.yield L = x :: rest ∧ x ∉ openers
  noun_prefix_free : ∀ s ∈ L.sorts, ∀ s' ∈ L.sorts, kws (L.noun s) <+: kws (L.noun s') → s = s'
  noun_opens : ∀ s ∈ L.sorts, ∃ x rest, L.noun s = x :: rest ∧ x ≠ "first" ∧ x ≠ "second"

/-- The lexicon names every symbol of the environment, with templates of the
declared arity. -/
structure Covers (L : Lexicon) (E : Environment) : Prop where
  sorts : ∀ s ∈ E.sorts, s ∈ L.sorts
  predicates : ∀ p ss, E.predicates p = some ss → p ∈ L.predicates ∧
    ∃ T, L.template p = some T ∧ T.arity = ss.length ∧ ∀ i < ss.length, Slot.hole i ∈ T
  constants : ∀ c s, E.constants c = some s → c ∈ L.constants

end VE.English
