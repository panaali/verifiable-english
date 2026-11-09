import VE.Presupposition.Frame
import VE.Presupposition.Reading
import VE.Presupposition.Rows

/-! # The wire layer of presupposition admission (docs/spec/presupposition.md 4.7)

The obligation block's types (`Carrier`, `Candidate`, `Position`, `Args`, `Obligation`), the
candidate table and its shape check (`cellOk`, `tableOk`), the regenerated obligation (`Checked`),
the `Report`, `carrierAllowed` and the restriction paths. Every body is the spec's or the PS-S
stub's text. The readings of an open set and the decoded document (`RReading` to `PDoc`,
`claimReading`, `ruleReading`, `emitted`, `aliasesOf`, `expectedReadings`) are PS-2a's, cut there
by R16's 150-line limit (docs/presupposition/ps-2aa/REPORT.md); `admit` and its statements too. -/

namespace VE.Presupposition

inductive Carrier where
  | proved (node : String)
  | assumed (unit : String)
  | conditioned
  | asserted
  | inPlace
  | unconditional (unit : String)
  | unresolved
  deriving DecidableEq, Repr

inductive Candidate where
  | assumed | conditioned | asserted | inPlace | unconditional
  deriving DecidableEq, Repr

def Carrier.root : Carrier → Root
  | .asserted => .asserted
  | .conditioned => .conditioned
  | _ => .bare

def Carrier.cand : Carrier → Option Candidate
  | .assumed _ => some .assumed
  | .conditioned => some .conditioned
  | .asserted => some .asserted
  | .inPlace => some .inPlace
  | .unconditional _ => some .unconditional
  | .proved _ | .unresolved => none

def Candidate.root : Candidate → Root
  | .asserted => .asserted
  | .conditioned => .conditioned
  | _ => .bare

def Candidate.core : Candidate → Bool
  | .assumed | .conditioned | .asserted => true
  | _ => false

inductive Position where
  | path (p : List Nat)
  | ruleAct (rule : String)
  | heading                                   -- R-10: `{"heading": {}}`
  deriving DecidableEq, Repr

structure Args where
  sort        : Option String := none
  restriction : Option VE.Formula := none
  body        : Option VE.Formula := none
  pre         : Option VE.Formula := none
  deriving DecidableEq, Repr

def Args.tuple (a : Args) : Option String × Option VE.Formula × Option VE.Formula × Option VE.Formula :=
  (a.sort, a.restriction, a.body, a.pre)

structure Obligation where
  id       : String
  unit     : String
  span     : Nat × Nat
  row      : String
  position : Position
  args     : Args
  carrier  : Carrier
  deriving DecidableEq, Repr

/-- PS-E1's table: candidates per row and position class, in the row's order; an unmeasured cell is empty. -/
abbrev CandidateTable := String → PositionClass → List Candidate

/-- Filled from PS-E1's output; until then every cell is empty, so nothing is admitted as unresolved. -/
def candidateTable : CandidateTable := fun _ _ => []

/-- R-2: in place only in a negated or antecedent cell, and only beside conditioned. -/
def cellOk (pc : PositionClass) (cs : List Candidate) : Bool :=
  decide cs.Nodup && !(cs.contains .assumed && cs.contains .asserted) &&
    (!cs.contains .inPlace || cs.contains .conditioned) &&
    cs.all (fun c => match c with
      | .assumed | .conditioned => true
      | .asserted => pc != .ruleAct
      | .inPlace => pc == .negated || pc == .antecedent
      | .unconditional => pc == .consequent)

def tableOk (rows : List String) (t : CandidateTable) : Bool :=
  rows.all (fun row => [PositionClass.top, .negated, .antecedent, .consequent, .disjunct, .ruleAct,
    .ruleGuard].all (fun pc => cellOk pc (t row pc)))

def rowNames : List String := ["definite", "plural", "generic"]

/-- An obligation as Lean regenerates it from the base content: never read from the wire unchecked. -/
structure Checked where
  ob      : Obligation
  frame   : Frame                   -- in the base content; `.hole` at a rule act and at a heading
  pre     : VE.Formula
  reading : Option Reading          -- none at a rule act and at a heading
  goal    : VE.Formula
  pos     : PositionClass           -- `.top` at a heading, which has no cell (only proved and assumed)
  deriving DecidableEq, Repr

structure Report where
  checked  : List Checked                     -- one per obligation, block order
  bases    : List (String × VE.Formula)       -- each claim unit with obligations: its base content
  baseTree : VE.Norms.Tree                    -- every rule with the carriers' conditions removed (open rules included)

def unitModes (R : Report) (u : String) : List (Root × VE.Formula) :=
  (R.checked.filter (fun c => c.ob.unit == u)).map (fun c => (c.ob.carrier.root, c.goal))

/-- R-D1, check step 4: a recorded carrier's candidate is in the cell, and in place also needs a shallow frame. -/
def carrierAllowed (t : CandidateTable) (c : Checked) (k : Candidate) : Bool :=
  (t c.ob.row c.pos).contains k && (k != .inPlace || decide c.frame.shallow)

/-- R-D6: every path from a row's `strong` to a copy of its restriction `D` (4.4: `assertiveAt`, `plural`). -/
def restrictionPaths : String → List (List Nat)
  | "definite" => [[0, 0], [0, 1, 0, 0, 0]]
  | "plural" => [[0, 0], [1, 0, 0]]
  | _ => []

/-- R-D6: the path `q` enters the restriction of the obligation of row `row` at path `p`. -/
def entersRestriction (row : String) (p q : List Nat) : Bool :=
  (restrictionPaths row).any (fun o => (p ++ o).isPrefixOf q)

/-- The rule conditions recorded on the rule named `n`, in block order. -/
def ruleConditions (R : Report) (n : String) : List VE.Formula :=
  (R.checked.filter (fun d => d.ob.position == .ruleAct n && d.ob.carrier == .conditioned)).map (·.pre)

end VE.Presupposition
