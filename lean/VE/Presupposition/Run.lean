import VE.Presupposition.Admit
import VE.English.Render
import VE.English.Parse
import VE.Presupposition.Examples

/-! # The presupposition report (docs/spec/presupposition.md 4.7 "Where the report goes", 2.3, 5; plan PS-2a)

The value the Lean document mode's answer carries as its `presuppositions` field (plan PS-4; DRI PS-C9: no service
mode, no runner and no schema of its own). It is read off `admit`'s answer, never recomputed: one row per obligation
in the block's order with its id, unit and carrier; the regenerated goal with its English line, rendered here by the
core renderer and shown only when it parses back to exactly the goal; the outcome; and, for an admitted unresolved obligation, the readings its unit carries with their
aliases. Then the `PresuppositionRefuted` lines (2.3) the existing inconsistency report gives.

`admit` decides the block as a whole and answers its first failing step, so every row carries the block's outcome:
checked, the refusal's diagnostic, or `ResourceLimit: presuppositions`, which is UNKNOWN and never a refusal (spec 5).
A refused block has no regenerated goal, so its rows carry none. Each row's goal is charged in `admit` against W1's
node budget and the block against `maxObligations`; a rendered line over `maxLineTokens` tokens is not parsed and
not shown; the inconsistency certificate is checked once per report. -/

namespace VE.Presupposition

/-- A row's outcome: the block admitted, refused with `admit`'s diagnostic, or over a limit (UNKNOWN). -/
inductive Outcome where
  | checked
  | refused (diagnostic : String)
  | unknown (diagnostic : String)
  deriving DecidableEq, Repr

/-- A regenerated goal: the formula (PS-4 encodes it in P0's wire form) and its English line, none when the line
    does not parse back to exactly the formula or is over the limit. -/
structure Goal where
  formula : VE.Formula
  english : Option String
  deriving DecidableEq, Repr

/-- One obligation's row. `goal` is none on a refused block; `readings` is the unit's open set for an admitted
    unresolved obligation, in the unit's order, each with its aliases (R-1), and empty otherwise. -/
structure Row where
  id : String
  unit : String
  carrier : Carrier
  goal : Option Goal
  outcome : Outcome
  readings : List RReading
  deriving DecidableEq, Repr

/-- The `presuppositions` field: the rows in block order, then the `PresuppositionRefuted` lines. -/
structure Shown where
  rows : List Row
  refuted : List String
  deriving DecidableEq, Repr

/-- The existing inconsistency report (P0): the checked premise list and an inconsistency certificate on it. -/
structure Inconsistency where
  premises : List VE.Formula
  cert : VE.Tableau.Certificate

/-- A clause's tokens as one line: separated by spaces, punctuation attached to the word before it. -/
def lineOf (ts : List VE.English.Tok) : String :=
  ts.foldl (fun s t => match t with
    | .word w => if s.isEmpty then w else if [",", ";", ":", "."].contains w then s ++ w else s ++ " " ++ w
    | .label l i => (if s.isEmpty then "" else s ++ " ") ++ l ++ toString i) ""

/-- The limit on a rendered line: the core parser's work grows faster than the line, so a longer line is not parsed. -/
def maxLineTokens : Nat := 400

/-- The goal's English line: the core renderer's clause for it under the lexicon `L`, without the full stop, so
    that 2.3's lines can quote it ("Assumed (from ‘…’): <goal>."). It is shown only when the sentence parses back,
    in the document's environment `E`, to exactly the goal (one reading), and is within `maxLineTokens`. -/
def englishLine (E : VE.Environment) (L : VE.English.Lexicon) (A : VE.Formula) : Option String :=
  let ts := (VE.English.renderStatement L A).yield L 0
  if ts.length ≤ maxLineTokens && VE.English.parse E L (ts ++ [.word "."]) == some [A] then some (lineOf ts) else none

def outcomeOf (e : String) : Outcome := if e == budget then .unknown e else .refused e

def checkedRow (L : VE.English.Lexicon) (D : PDoc) (c : Checked) : Row :=
  { id := c.ob.id, unit := c.ob.unit, carrier := c.ob.carrier, goal := some ⟨c.goal, englishLine (env D) L c.goal⟩,
    outcome := .checked,
    readings := if c.ob.carrier == .unresolved then (unitReadings D c.ob.unit).getD [] else [] }

def refusedRow (e : String) (o : Obligation) : Row :=
  { id := o.id, unit := o.unit, carrier := o.carrier, goal := none, outcome := outcomeOf e, readings := [] }

/-- 2.3: `PresuppositionRefuted: <o>: <unit>` for each assumed obligation whose goal is one of the premises an
    accepted inconsistency certificate refutes (the other premises then refute the goal), in block order. -/
def refutedLines (D : PDoc) (R : Report) : Option Inconsistency → List String
  | none => []
  | some i =>
    if VE.Tableau.checkCertificate (env D) i.premises .bottom i.cert then
      R.checked.filterMap (fun c => match c.ob.carrier with
        | .assumed u => if i.premises.contains c.goal then some s!"PresuppositionRefuted: {c.ob.id}: {u}" else none
        | _ => none)
    else []

/-- The field from `admit`'s answer `a` on `D`: absent without the block (as `admitWrapped`). -/
def shownOf (L : VE.English.Lexicon) (inc : Option Inconsistency) (D : PDoc) (a : Except String Report) :
    Option Shown :=
  D.block.map (fun obs => match a with
    | .ok R => ⟨R.checked.map (checkedRow L D), refutedLines D R inc⟩
    | .error e => ⟨obs.map (refusedRow e), []⟩)

/-- The field PS-4 puts in the document mode's answer, on `admit`. -/
def shown (L : VE.English.Lexicon) (inc : Option Inconsistency) (D : PDoc) : Option Shown :=
  shownOf L inc D (admit D)

end VE.Presupposition

/-! ## Guards over spec 7.3's admission fixtures A1-A28 (`VE.Presupposition.Examples`) -/

namespace VE.Presupposition.RunExamples
open VE.Presupposition VE.Presupposition.Examples

/-- A fixture lexicon over `envA`'s words. -/
def lexA : VE.English.Lexicon :=
  { sorts := ["entity"], noun := fun _ => ["entity"], letter := fun _ => "E",
    predicates := ["owner", "ready", "manager", "trusts", "core_value_of"],
    template := fun p => match p with
      | "owner" => some [.hole 0, .word "is", .word "an", .word "owner"]
      | "ready" => some [.hole 0, .word "is", .word "ready"]
      | "manager" => some [.hole 0, .word "is", .word "a", .word "manager"]
      | "trusts" => some [.hole 0, .word "trusts", .hole 1]
      | "core_value_of" => some [.hole 0, .word "is", .word "a", .word "core", .word "value", .word "of", .hole 1]
      | _ => none,
    constants := ["claude"], spelling := fun c => if c == "claude" then ["Claude"] else [] }
def rowsOf (s : Option Shown) : List Row := (s.map (·.rows)).getD []

-- Rows in block order (A18b: two assumed obligations on one unit, admitted on `admit`); the reversed block gives the
-- reversed rows. Id, unit and carrier are the obligation's.
#guard (rowsOf (shown lexA none doc18b)).map (fun r => (r.id, r.unit, r.carrier)) ==
  [("p1", "u1", .assumed "u0"), ("p2", "u1", .assumed "u00")]
#guard (rowsOf (shown lexA none { doc18b with block := doc18b.block.map List.reverse })).map (·.id) == ["p2", "p1"]
-- outcome: checked on an admitted block; readings only for an unresolved obligation
#guard (rowsOf (shown lexA none doc18b)).map (fun r => (r.outcome, r.readings)) == [(.checked, []), (.checked, [])]
-- goal: `admit`'s regenerated goal and its English line (A24: a heading assumed on its own unit, goal `pre`)
#guard rowsOf (shown lexA none (docH coreU (.assumed "u0013.presupposition"))) ==
  [⟨"p2", "u0013.presupposition", .assumed "u0013.presupposition",
    some ⟨coreU, some "there is an entity such that that entity is a core value of Claude"⟩, .checked, []⟩]
#guard (rowsOf (shown lexA none doc18b)).map (·.goal.map (·.formula)) ==
  ((admit doc18b).toOption.map (·.checked.map (some ·.goal))).getD []
-- the English line: punctuation attached, list labels and numbered entity labels kept (A1's goal, the owner exists)
#guard englishLine envA lexA theOwnerU == some ("there is a first entity such that both of the following hold: (a) the first " ++
  "entity is an owner; (b) for every second entity, if the second entity is an owner, then the second entity is " ++
  "the same as the first entity")
-- a line that does not parse back to exactly the goal is not shown: a predicate without a wording (A18b's p2 under a
-- lexicon without "manager"), a wording that reads as another predicate's; and a line over `maxLineTokens`
def lexNoMgr : VE.English.Lexicon := { lexA with predicates := lexA.predicates.erase "manager" }
#guard (rowsOf (shown lexNoMgr none doc18b)).map (·.goal.map (·.english.isSome)) == [some true, some false]
#guard (rowsOf (shown lexA none doc18b)).map (·.goal.map (·.english.isSome)) == [some true, some true]
#guard englishLine envA { lexA with template := fun p => lexA.template (if p == "ready" then "owner" else p) } theOwner == none
#guard (englishLine envA lexA theOwner).isSome
def conj : Nat → VE.Formula
  | 0 => theOwnerU
  | n + 1 => .and theOwnerU (conj n)
#guard ((VE.English.renderStatement lexA (conj 6)).yield lexA 0).length ≤ maxLineTokens &&
  (englishLine envA lexA (conj 6)).isSome
#guard ((VE.English.renderStatement lexA (conj 7)).yield lexA 0).length > maxLineTokens && englishLine envA lexA (conj 7) == none
#guard lineOf [.word "if", .label "E" 1, .word "is", .word "an", .word "owner", .word ",", .word "then", .word "."] ==
  "if E1 is an owner, then."
-- a refused block: every row carries `admit`'s diagnostic and no goal (A20: assumed on its own unit; A18: p2 in p1's
-- restriction, both rows)
#guard rowsOf (shown lexA none (docA [cu "u1" theOwner] [pA (.assumed "u1")])) ==
  [⟨"p1", "u1", .assumed "u1", none, .refused "PresuppositionAssumedUnit: p1: u1", []⟩]
#guard (rowsOf (shown lexA none (doc18 [0, 0]))).map (fun r => (r.id, r.goal, r.outcome)) ==
  [("p1", none, .refused "PresuppositionPosition: p2"), ("p2", none, .refused "PresuppositionPosition: p2")]
-- A15: 257 obligations are UNKNOWN, never refused; 256 on one unit are checked, 256 rows with their lines
#guard (rowsOf (shown lexA none (docA [cu "u0" theOwnerU, cu "u1" theOwner] (many 257)))).all
  (·.outcome == .unknown "ResourceLimit: presuppositions")
#guard (rowsOf (shown lexA none (docA [cu "u0" theOwnerU, cu "u1" theOwner] (many 257)))).length == 257
#guard (rowsOf (shown lexA none (docA [cu "u0" theOwnerU, cu "u1" theOwner] (many 256)))).map
  (fun r => (r.outcome, r.goal.map (·.english))) == List.replicate 256 (.checked, some (englishLine envA lexA theOwnerU))
-- A17: without the block the field is absent
#guard (shown lexA none { docA1 with block := none }).isNone

-- Unresolved obligations: the unit's readings, each with its aliases. A1 (the fixture table): assumed, conditioned.
#guard (rowsOf (shownOf lexA none docA1 (admitWith fixtureTable fx1 docA1))).map (fun r => (r.carrier, r.readings)) ==
  [(.unresolved, [rdAs, rdCo])]
-- R-1: at a negated frame whose cell lists conditioned, asserted and in place, the conditioned reading carries in place
-- as its alias. (Assumed and conditioned are equivalent there, so step 5 never separates that pair.)
def tC : CandidateTable := fun _ pc => if pc == .negated then [.conditioned, .asserted, .inPlace] else [.assumed, .conditioned]
def rsC : List RReading :=
  ((admitWith tC fxN (docA [cu "u1" (negF.plug theOwner)] [pA .inPlace (.path [0])])).toOption.bind
    (fun R => R.checked.head?.bind (expectedReadings tC R))).getD []
def docC : PDoc := docA [⟨"u1", true, .readings rsC⟩] [pA .unresolved (.path [0])]
#guard tableOk rowNames tC && errOf (admitWith tC ⟨.norms, [("u1", 0, 1, sitNo)]⟩ docC) == "admitted"
#guard (rowsOf (shownOf lexA none docC (admitWith tC ⟨.norms, [("u1", 0, 1, sitNo)]⟩ docC))).map
  (·.readings.map (fun r => (r.cand, r.aliases))) == [[(.conditioned, [.inPlace]), (.asserted, [])]]

-- PresuppositionRefuted (2.3): an accepted inconsistency certificate over premises that contain assumed goals names
-- each such obligation and its assumed unit, in block order; a certificate that does not check, no report, a goal
-- not among the premises, a carrier other than assumed and a refused block give none.
def certI (k : Nat) : VE.Tableau.Certificate := { certC with trace := .expand k none [.close] }
def g1 : VE.Formula := rOut18b.pre
def g2 : VE.Formula := f18b.goal rIn18b.pre
def refutedOf (D : PDoc) (ps : List VE.Formula) (c : VE.Tableau.Certificate) : List String :=
  ((shown lexA (some ⟨ps, c⟩) D).map (·.refuted)).getD []
#guard refutedOf doc18b [g1, g2, .not g1] (certI 2) == ["PresuppositionRefuted: p1: u0", "PresuppositionRefuted: p2: u00"]
#guard refutedOf doc18b [g1, .not g1] (certI 1) == ["PresuppositionRefuted: p1: u0"]
#guard refutedOf doc18b [g1, .not g1] certC == [] && (shown lexA none doc18b).map (·.refuted) == some []
#guard refutedOf doc18b [isOpen, .not isOpen] (certI 1) == []
#guard refutedOf (docA [cu "u0" theMgrU, cu "u1" theMgr] [pP "u1"] (proofs := [("d1", certC)])) [theMgrU, .not theMgrU]
  (certI 1) == []
#guard refutedOf (doc18 [0, 0]) [g1, .not g1] (certI 1) == []

end VE.Presupposition.RunExamples
