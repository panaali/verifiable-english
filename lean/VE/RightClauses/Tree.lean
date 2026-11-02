import VE.Compose.Slot
import VE.Compose.Content

/-! Structured right lines (docs/spec/right-clauses.md 1.1, 8.2): a rights line with its clauses, at most one
relation and its elided spans, and the document that carries them.

A clause is a base formula typed in the line's context with the source bytes it accounts for; a relation is a
declared binary base predicate between two slots of the line, optionally total on the holder slot; `elided` lists
the bytes of the unit nothing accounts for. Nothing here changes a rights line: `plain` (Plain.lean) is the whole
elaboration. No import of `VE.Readings` (spec 0). -/
namespace VE.RightClauses
open VE.Rights (RightsDoc SourceLine)

inductive Role | scope | trigger | object
  deriving DecidableEq, Repr
structure Clause where
  role : Role
  formula : VE.Formula
  span : Nat × Nat
  deriving DecidableEq, Repr
structure Relation where
  pred : String
  slots : Nat × Nat
  total : Option Nat
  cites : List String
  deriving DecidableEq, Repr
/-- A structured line. `unitSpan` is the span of the unit the line is written in (1.1: clause and elided spans
    lie inside it); the plan's sketch has no such field, and the span check needs it. -/
structure CLine where
  line : SourceLine
  clauses : List Clause
  relation : Option Relation
  elided : List (Nat × Nat)
  unitSpan : Nat × Nat
  deriving DecidableEq, Repr
/-- The rights document and its structured lines, each as (right, rule name, line). -/
structure ClauseDoc where
  doc : RightsDoc
  lines : List (String × String × CLine)
  /-- Reading candidates: (set, candidate index, content, its structured lines); `[]` when there is no reading set. -/
  cands : List (String × Nat × VE.Compose.Content × List (String × String × CLine))

/-- The rule name of a line; a power's is its liberty unit's name. -/
def lineName (S : SourceLine) : Option String := (S.norm <|> S.liberty).map (·.name)
/-- The argument sorts of a line's predicate (its context, slot order). -/
def lineSorts (E : VE.SoftNorms.SoftDoc) (S : SourceLine) : List String :=
  (S.norm.map (fun N => VE.SoftNorms.sortsOf E N.pred)).getD []
/-- The base vocabulary clauses and relations are typed in. -/
def baseEnv (D : ClauseDoc) : VE.Environment := VE.Norms.envAt D.doc.soft.base 0
end VE.RightClauses
