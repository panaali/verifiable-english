import VE.EnglishGrammar.Token
import VE.EnglishGrammar.Syntax

/-! The types of the nonterminal catalogue of the base profile and the names of the fixed actions
(docs/spec/english-lean-s2.md 2.4, 2.5 and 2.7).

One catalogue, numbered in the order of spec 2.4, serves every environment and lexicon: `ntTy` is the
type table. The names `ntNames` and the left-corner certificate `ranks` (W3) are generated with the fixed
table from `ve/english_grammar/relational-fol@0.json` (`Fixed/RelationalFol.lean`). A fixed rule is a
`FixedRow`: its tag, sides and the name of its action with the action's data, as the source writes them
(spec 2.9). The actions themselves are in `VE.EnglishGrammar.Actions`.
-/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The catalogue indices that the lexical rules name (spec 2.4); `Rules.lean` checks them against
`ntNames`. -/
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

/-- The connective of a listing or a coordination. -/
inductive Conn where
  | and | or | implies
  deriving DecidableEq, Repr

def Conn.name : Conn → String
  | .and => "and"
  | .or => "or"
  | .implies => "implies"

/-- The comparison of an integer comparison row (docs/spec/english-lean-s3.md 2.5). -/
inductive Cmp where
  | eq | lt | le
  deriving DecidableEq, Repr

/-- The fixed actions of spec 2.7, each with its data, and those of the `order@0` and `alternatives@0`
rows (docs/spec/english-lean-s3.md 2.5, 2.7). -/
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
  | intNegate | intConst | intTwice | numeral (negative : Bool) | intBracket | op
  | intCmp (k : Cmp) (swapped : Bool)
  | relOr | verbSubject | verbSame
  deriving DecidableEq, Repr

/-- A row of the fixed-rule source (spec 2.9). -/
structure FixedRow where
  tag : String
  lhs : Nat
  rhs : List (Sym Terminal)
  act : FixedAct
  deriving DecidableEq, Repr

end VE.EnglishGrammar
