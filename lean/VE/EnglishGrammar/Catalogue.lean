import VE.EnglishGrammar.Token
import VE.EnglishGrammar.Syntax

/-! The nonterminal catalogue of the base profile, its types and ranks, and the names of the fixed
actions (docs/spec/english-lean-s2.md 2.4, 2.5 and 2.7).

One catalogue, numbered in the order of spec 2.4, serves every environment and lexicon: `ntTy` is the
type table and `ranks` the left-corner certificate (W3). A fixed rule is a `FixedRow`: its tag, sides and
the name of its action with the action's data, as the source `ve/english_grammar/relational-fol@0.json`
writes them (spec 2.9). The actions themselves are in `VE.EnglishGrammar.Actions`.
-/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The nonterminal names of spec 2.4, in catalogue order. -/
def ntNames : Array String := #[
  "sentence", "marker", "formula", "atom", "negation", "compact", "listing", "universal",
  "existential", "coordination", "guard", "guard_relative", "guard_atom", "relative_pronoun",
  "list_marker", "article", "declaration", "term", "noun", "label", "constant", "relative",
  "object_relative", "adjective", "natural", "natural_some", "some_tail", "copula_relative",
  "copula_adjective", "natural_no", "natural_every", "natural_tail", "natural_subject",
  "owner_clause", "reach", "count", "relation"]

/-- The catalogue indices that the lexical rules name (spec 2.4). -/
def ntAtom : Nat := 3
def ntTerm : Nat := 17
def ntNoun : Nat := 18
def ntLabel : Nat := 19
def ntConstant : Nat := 20
def ntRelative : Nat := 21
def ntObjectRelative : Nat := 22
def ntAdjective : Nat := 23
def ntCopulaRelative : Nat := 27
def ntCopulaAdjective : Nat := 28
def ntNaturalSubject : Nat := 32
def ntOwnerClause : Nat := 33
def ntRelation : Nat := 36

/-- The type of each nonterminal (spec 2.4); `tok` past the catalogue. -/
def ntTy : Nat → Ty
  | 0 => .sentence
  | 1 => .marker
  | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 => .formula
  | 10 | 11 | 12 => .relative
  | 13 => .unit
  | 14 => .listMarker
  | 15 => .unit
  | 16 => .declaration
  | 17 => .term
  | 18 => .noun
  | 19 => .label
  | 20 => .constant
  | 21 | 22 => .relative
  | 23 => .adjective
  | 24 | 25 => .formula
  | 26 | 27 => .relative
  | 28 => .adjective
  | 29 | 30 => .formula
  | 31 => .relative
  | 32 => .natSubject
  | 33 => .relative
  | 34 => .formula
  | 35 => .count
  | 36 => .relation
  | _ => .tok

/-- The ranks of spec 2.4, one certificate for every lexicon: rank 0 for the nonterminals whose rules
begin with a terminal; `term`, `declaration`, `natural` at 1; `atom`, `object_relative`, `coordination`,
`relative` at 2; `some_tail`, `natural_tail`, `guard_atom`, `formula` at 3; `guard_relative`, `guard`,
`sentence` at 4. -/
def ranks : Array Nat := #[
  4, 0, 3, 2, 0, 0, 0, 0, 0, 2, 4, 4, 3, 0, 0, 0, 1, 1, 0, 0, 0, 2, 2, 0, 1, 0, 3, 0, 0, 0, 0, 3,
  0, 0, 0, 0, 0]

/-- The connective of a listing or a coordination. -/
inductive Conn where
  | and | or | implies
  deriving DecidableEq, Repr

def Conn.name : Conn → String
  | .and => "and"
  | .or => "or"
  | .implies => "implies"

/-- The fixed actions of spec 2.7, each with its data. -/
inductive FixedAct where
  | sentence (marked : Bool)
  | mark | unit | listMarker | through | nest | not | and2 | or2 | implies2
  | listWords (k : Conn) | listMarkers (k : Conn)
  | guardAnd | guardLeft | guardRight | relAnd
  | forallBody | forallGuardBody | forallRel | forallGuardRel | existsBody | existsRel
  | declThat | declOrdinal (ordinal : String) | declNamed
  | termConst | termIt | termRef (pre : String) | termLabel
  | top | bottom | eq
  | coordSubjects (k : Conn) | coordAdjectives (k : Conn)
  | naturalTop | someDecl | copulaAnd | noDecl | everySubject | everyOwner
  | reachNamed | reachBody (listed : Bool) | count (reflexive : Bool)
  deriving DecidableEq, Repr

/-- A row of the fixed-rule source (spec 2.9). -/
structure FixedRow where
  tag : String
  lhs : Nat
  rhs : List (Sym Terminal)
  act : FixedAct
  deriving DecidableEq, Repr

end VE.EnglishGrammar
