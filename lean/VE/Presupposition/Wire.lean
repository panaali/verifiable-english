import VE.Presupposition.Frame
import VE.Presupposition.Reading
import VE.Presupposition.Rows
import VE.Presupposition.Rules

/-! # The wire layer of presupposition admission (docs/spec/presupposition.md 4.7)

The obligation block's types (`Carrier`, `Candidate`, `Position`, `Args`, `Obligation`), the
candidate table and its shape check (`cellOk`, `tableOk`), PS-2a's view of the decoded W2
document (`PDoc`), the regenerated obligation (`Checked`), the `Report`, and the readings of an
open set (`claimReading`, `ruleReading`, `emitted`, `aliasesOf`, `expectedReadings`), with
`carrierAllowed` and the restriction paths. `admit` and its statements are `Admit.lean`'s.
Every body is the spec's or the PS-S stub's text. -/

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

/-- PS-E1's table (docs/research/presupposition-E1/candidate-table.json): `[assumed]` in every measured cell of the
    three rows, `[assumed, unconditional]` in generic's consequent cell; the disjunct cells and other rows are empty. -/
def candidateTable : CandidateTable := fun row pc => match row, pc with
  | _, .disjunct => []
  | "generic", .consequent => [.assumed, .unconditional]
  | "definite", _ | "plural", _ | "generic", _ => [.assumed]
  | _, _ => []

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

/-- A reading of an open set: the candidate it stands for, its content and what it takes for granted. -/
inductive RContent where
  | claim (a : VE.Formula)
  | rule (N : VE.Norms.Node)
  deriving DecidableEq, Repr

structure RReading where
  cand    : Candidate                         -- the canonical candidate; never `.inPlace`
  aliases : List Candidate                    -- R-1: other wordings of the same reading, ordered as in the cell
  content : RContent
  premise : Option VE.Formula
  deriving DecidableEq, Repr

inductive UContent where
  | claim (a : VE.Formula)
  | rule (name : String)
  | readings (rs : List RReading)
  | unformalised
  deriving DecidableEq, Repr

structure DocUnit where
  id       : String
  asserted : Bool
  content  : UContent
  deriving DecidableEq, Repr

/-- PS-2a's view of the decoded W2 document (`ve-document@2` units; the Lean document mode's after lf-16g). -/
structure PDoc where
  E          : VE.Environment
  lits       : List String
  norms      : VE.Norms.Tree                  -- the fixed W1 rules
  defaults   : Bool                           -- R-8, R-9: the document carries `norm-defaults@0`
  unspec     : List String                    -- norm-defaults' `unspecified` predicates ([] without its block)
  background : List VE.Formula                -- declared background, P0 generator order
  units      : List DocUnit                   -- document order
  proofs     : List (String × VE.Tableau.Certificate)   -- deduction nodes: id, certificate
  block      : Option (List Obligation)

def env (D : PDoc) : VE.Environment := D.E
def unitOf (D : PDoc) (u : String) : Option DocUnit := D.units.find? (fun x => x.id == u)

def unitContent (D : PDoc) (u : String) : Option VE.Formula :=
  match unitOf D u with
  | some ⟨_, _, .claim a⟩ => some a
  | _ => none

def unitAsserted (D : PDoc) (u : String) : Bool := ((unitOf D u).map (·.asserted)).getD false

def unitReadings (D : PDoc) (u : String) : Option (List RReading) :=
  match unitOf D u with
  | some ⟨_, _, .readings rs⟩ => some rs
  | _ => none

def nodeCertificate (D : PDoc) (n : String) : Option VE.Tableau.Certificate :=
  (D.proofs.find? (fun x => x.1 == n)).map (·.2)

/-- D2-3: the declared background, then the asserted claims of the units strictly before `u`, in order. -/
def premisesBefore (D : PDoc) (u : String) : List VE.Formula :=
  D.background ++ (D.units.takeWhile (fun x => x.id != u)).filterMap (fun x =>
    match x.content with
    | .claim a => if x.asserted then some a else none
    | _ => none)

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

/-- One candidate's reading of an unresolved claim obligation `c`, the unit's other obligations as recorded. -/
def claimReading (R : Report) (c : Checked) (B : VE.Formula) (k : Candidate) : RReading :=
  let ms := (R.checked.filter (fun d => d.ob.unit == c.ob.unit)).map (fun d =>
    (if d.ob.id == c.ob.id then k.root else d.ob.carrier.root, d.goal))
  { cand := k, aliases := [], content := .claim (carried ms B),
    premise := (match k with
      | .assumed => some c.goal
      | .unconditional => some (c.frame.close c.pre)
      | _ => none) }

/-- One candidate's reading of an unresolved rule-act obligation `c` on the base rule `N`. -/
def ruleReading (R : Report) (c : Checked) (N : VE.Norms.Node) (k : Candidate) : RReading :=
  let conds := (R.checked.filter (fun d => d.ob.position == .ruleAct N.name)).filterMap (fun d =>
    if d.ob.id == c.ob.id then (if k == .conditioned then some d.pre else none)
    else if d.ob.carrier == .conditioned then some d.pre else none)
  { cand := k, aliases := [], content := .rule (conds.foldl conditionNode N),
    premise := if k == .assumed then some c.goal else none }

/-- R-D1: the candidates that become readings: the cell without in place, in the cell's order. -/
def emitted (t : CandidateTable) (c : Checked) : List Candidate := (t c.ob.row c.pos).filter (· != .inPlace)

/-- R-1, R-D2: a reading's aliases, ordered as in the cell: in place, on the conditioned reading at a shallow frame. -/
def aliasesOf (t : CandidateTable) (c : Checked) (k : Candidate) : List Candidate :=
  (t c.ob.row c.pos).filter (fun a => a == .inPlace && k == .conditioned && decide c.frame.shallow)

/-- The readings an unresolved obligation's unit must carry: one per emitted candidate, in the cell's order. -/
def expectedReadings (t : CandidateTable) (R : Report) (c : Checked) : Option (List RReading) :=
  match c.ob.position with
  | .path _ => ((R.bases.find? (fun x => x.1 == c.ob.unit)).map (·.2)).map (fun B =>
      (emitted t c).map (fun k => { claimReading R c B k with aliases := aliasesOf t c k }))
  | .ruleAct n => (R.baseTree.nodes.find? (fun N => N.name == n)).map (fun N =>
      (emitted t c).map (ruleReading R c N))
  | .heading => none

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
