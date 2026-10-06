import VE.EnglishGrammar.Token
import VE.EnglishGrammar.Syntax

/-! The types of the nonterminal catalogue of the base profile and the names of the fixed actions
(docs/spec/english-lean-s2.md 2.4, 2.5 and 2.7).

One catalogue, numbered in the order of spec 2.4, serves every environment and lexicon: `ntTy` is the
type table. The names `ntNames` and the left-corner certificate `ranks` (W3) are generated with the fixed
table from `ve/english_grammar/relational-fol@0.json` (`Fixed/RelationalFol.lean`). A fixed rule is a
`FixedRow`: its tag, sides and the name of its action with the action's data, as the source writes them
(spec 2.9). The actions themselves are in `VE.EnglishGrammar.Actions`.

S3 (docs/spec/english-lean-s3.md 2.4) appends fourteen fixed nonterminals, 37 to 50: the integer terms of
`order@0` and the guard phrases of `alternatives@0`; per environment, one property nonterminal per value sort
follows from 51 (`ty` in `Rules.lean`). `stagedNames` names the fourteen and `ranksStaged` is the one rank
certificate of every profile list that names a staged profile (spec D3).
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
def ntIntTerm : Nat := 37
def ntIntConstant : Nat := 40
def ntIntPlainConstant : Nat := 41
def ntAltGuard : Nat := 47
def ntAltVerbPhrase : Nat := 48
def ntAltHead : Nat := 50
/-- The first property nonterminal (spec 2.4): the `i`-th value sort's is `ntProperty + i`. -/
def ntProperty : Nat := 51

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
  | 37 | 38 | 39 => .intTerm
  | 40 | 41 => .constant
  | 42 => .intTerm
  | 43 => .listMarker
  | 44 | 45 | 46 => .unit
  | 47 => .formula
  | 48 | 49 => .relative
  | 50 => .listMarker
  | _ => .tok

/-- The names of the staged nonterminals 37 to 50 (spec 2.4). -/
def stagedNames : Array String := #[
  "int_term", "int_atom", "int_neg", "int_constant", "int_plain_constant", "numeral", "int_op", "minus",
  "lbracket", "rbracket", "alt_available_guard", "alt_verb_phrase", "alt_verb_atom", "alt_head"]

/-- The rank certificate of a profile list that names a staged profile (spec 2.4, D3): S2's 37 entries
raised where an integer term can begin a clause, then the fourteen staged nonterminals. -/
def ranksStaged : Array Nat := #[6, 0, 5, 4, 0, 0, 0, 0, 0, 2, 6, 6, 5, 0, 0, 0, 1, 1, 0, 0, 0, 4, 4, 0, 1, 0, 5,
  0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 3, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 6, 5, 0]

/-- The connective of a listing or a coordination. -/
inductive Conn where
  | and | or | implies
  deriving DecidableEq, Repr

def Conn.name : Conn → String
  | .and => "and"
  | .or => "or"
  | .implies => "implies"

/-- The comparison of two integer terms (S3 spec 2.7). -/
inductive IntCmp where
  | eq | lt | le
  deriving DecidableEq, Repr

def IntCmp.name : IntCmp → String
  | .eq => "eq"
  | .lt => "lt"
  | .le => "le"

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
  -- `order@0` (S3 spec 2.5, 2.7)
  | intNegate | intConst | intTwice | intBracket | numeral (negative : Bool) | op
  | intCmp (kind : IntCmp) (swapped : Bool)
  -- `alternatives@0`
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
