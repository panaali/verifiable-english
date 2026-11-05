import VE.Attitudes.Scale
import VE.Attribution.Content
import VE.Norms.Tree
import VE.EnglishGrammar.Lexicon

/-! The syntax of `attitudes@0` (docs/spec/attitudes.md sections 2.2 to 2.4): modes, attitude
conditions, guards, rules and documents; keys and their generated names `attitudes__<mode>__<i>`;
and the environments that declare those names. Content identity is syntax-tree equality, never a
hash (D-A3); keys are de-duplicated by `reports@0`'s `VE.Reports.dedup`. -/

namespace VE.Attitudes
open VE.Reports (Act)
universe u

/-! ## 2.2 Modes, conditions, guards, rules, documents -/

/-- `act a` is the act `a` of reports@0; `knows` and `thinks w` are new. -/
inductive Mode where
  | act (a : Act)
  | knows
  | thinks (w : Word)
  deriving DecidableEq, Repr

def Mode.slug : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks_" ++ w.map (fun c => if c == ' ' then '_' else c)

/-- The mode's English words, for diagnostics. -/
def Mode.words : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks it " ++ w

/-- One attitude condition. `holder` is a term of the guard. `slot = some (s, t)`: the content's variable 0 has sort
    `s` and stands for the guard's term `t`; `slot = none`: the content is closed. -/
structure Cond where
  holder : VE.Term
  mode : Mode
  slot : Option (String × VE.Term)
  content : VE.Formula
  deriving DecidableEq, Repr

/-- W1's guard formulas with attitude conditions as atoms. -/
inductive AFormula where
  | base (φ : VE.Formula)
  | att (c : Cond)
  | not (a : AFormula)
  | and (a b : AFormula)
  | or (a b : AFormula)
  | implies (a b : AFormula)
  | all (s : String) (a : AFormula)
  | ex (s : String) (a : AFormula)
  deriving DecidableEq, Repr

/-- A W1 rule whose guard and carve-outs may carry attitude conditions. -/
structure ARule where
  name : String
  pred : String
  sign : Bool
  guard : AFormula
  carveOuts : List AFormula
  over : List String
  deriving DecidableEq, Repr

/-- The English grammar's lexical data for one document (SR-3), from its owner `VE.EnglishGrammar`. -/
structure Lex where
  /-- the lexical view of the environment -/
  env : VE.EnglishGrammar.Env
  /-- the vocabulary overlay; `{}` when the case has none -/
  overlay : VE.EnglishGrammar.Overlay
  /-- the selected nouns, wordings, negatives, aliases and spellings -/
  lexicon : VE.EnglishGrammar.Lexicon

structure AttDoc where
  E : VE.Environment
  lits : List String
  /-- the author's declared predicate names, as decoded (the count `MAX_PREDICATES` bounds) -/
  authorPredicates : List String
  regulated : List VE.Norms.Regulated
  definitions : List VE.Norms.Definition
  rules : List ARule
  /-- the holder sorts -/
  holders : List String
  /-- the frozen table; the decoder always sets `table` -/
  T : Table
  /-- the document's own pairs between admitted words -/
  declared : List (Word × Word)
  /-- the decider of every generated open term; "unstated" (the one W2 token, C2) when the document names none;
      rendered legend lines take their wording from the token's owner -/
  decidedBy : String
  /-- the English lexical data; checked by `checkAtt` (D6a, D6b) -/
  lex : Lex
  /-- (at-rev, AT-R1) the closed attitude nodes of the document's reading-set parts (PC-11's `attitude` case), in
      document order; `[]` on a document without a reading set -/
  parts : List Cond := []

/-- The table's pairs and the document's own. -/
def AttDoc.scale (A : AttDoc) : Scale := ⟨A.T.words, A.T.scale.above ++ A.declared⟩

/-! ## 2.3 Keys and generated names -/

structure Key where
  mode : Mode
  holderSort : String
  slotSort : Option String
  content : VE.Formula
  deriving DecidableEq, Repr

def Key.sorts (k : Key) : List String := k.holderSort :: k.slotSort.toList

def Cond.key (A : AttDoc) (Γ : List String) (c : Cond) : Option Key :=
  match c.holder.sortOf A.E Γ with
  | some hs => if A.holders.contains hs then some ⟨c.mode, hs, c.slot.map (·.1), c.content⟩ else none
  | none => none

def AFormula.conds : List String → AFormula → List (List String × Cond)
  | _, .base _ => []
  | Γ, .att c => [(Γ, c)]
  | Γ, .not a => a.conds Γ
  | Γ, .and a b => a.conds Γ ++ b.conds Γ
  | Γ, .or a b => a.conds Γ ++ b.conds Γ
  | Γ, .implies a b => a.conds Γ ++ b.conds Γ
  | Γ, .all s a => a.conds (s :: Γ)
  | Γ, .ex s a => a.conds (s :: Γ)

/-- A rule's guard context: its predicate's sorts, the last argument as variable 0. -/
def ruleContext (A : AttDoc) (r : ARule) : List String :=
  match A.regulated.find? (·.name == r.pred) with
  | some d => d.sorts.reverse
  | none => []

def condsOf (A : AttDoc) : List (List String × Cond) :=
  A.rules.flatMap (fun r => (r.guard :: r.carveOuts).flatMap (·.conds (ruleContext A r)))

/-- (at-rev, AT-R1) The reading-set parts, each read in the empty context: a part is closed. -/
def partsOf (A : AttDoc) : List (List String × Cond) := A.parts.map (fun c => ([], c))

def keys (A : AttDoc) : List Key :=
  VE.Reports.dedup ((condsOf A ++ partsOf A).filterMap (fun p => p.2.key A p.1))

/-- `attitudes__<mode>__<i>`, `i` the 1-based position among the keys of that mode. -/
def name (A : AttDoc) (k : Key) : String :=
  "attitudes__" ++ k.mode.slug ++ "__" ++ toString (((keys A).filter (·.mode == k.mode)).idxOf k + 1)

def keyOf (A : AttDoc) (r : String) : Option Key := (keys A).find? (fun k => name A k == r)

/-! ## 2.4 Environments -/

def baseEnv (A : AttDoc) : VE.Environment :=
  VE.Norms.hide A.E (A.regulated.map (·.name) ++ A.definitions.map (·.name))

def envAtt (A : AttDoc) : VE.Environment :=
  { A.E with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => A.E.predicates r }

def baseEnvAtt (A : AttDoc) : VE.Environment :=
  let B := baseEnv A
  { B with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => B.predicates r }

end VE.Attitudes
