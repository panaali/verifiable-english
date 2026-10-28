import VE.Scope.Govern
import VE.Discourse.Joint
import VE.Readings.Companions

/-! Scope per choice over a reading set a governed unit owns (docs/spec/scope.md 11, addendum sc-5r; built by
    sc-5rb). The definitions are the statement stub's (`docs/spec/scope/SpecStubs_sc5r.lean`, 11.2), verbatim:
    `governSets` checks the governed list once per joint choice of lf-14d's reading sets (`VE.Discourse.allChoices`,
    called, never edited) and admits it only when every choice is admitted. -/

namespace VE.Scope
open Lean

/-- lf-14d's limit on joint choices (`compatibleChoices … 64`) and the readings route's (`VE.Readings.maxChoices`). -/
def choiceLimit : Nat := 64

def setsJson (doc : Json) : List Json := match doc.getObjValD "reading_sets" with
  | .arr xs => xs.toList
  | _ => []
def setUnit (s : Json) : String := (s.getObjValD "unit").getStr?.toOption.getD ""
def setVersion (s : Json) : Nat := (s.getObjValD "version").getNat?.toOption.getD 0
def readingsJson (s : Json) : List Json := match s.getObjValD "readings" with
  | .arr xs => xs.toList
  | _ => []

/-- Neither a frontier reach nor a frontier fixed by a pick (5.7). -/
def layoutReach : Reach → Bool
  | .frontier | .fixed _ => false
  | _ => true

/-- 11.1: the units whose reading set is governed per choice. A unit of the document, written without content, with
    exactly one reading set, which holds a reading; some governor covers it; it is no governor's own unit; and no
    frontier or fixed reach covers it. -/
def governedSetUnits (D : SDoc) : List String :=
  (setUnits D.doc).eraseDups.filter fun u =>
    (unitIds D.doc).contains u && (contentOf D.doc u).isNull && (setUnits D.doc).count u == 1 &&
    ((setsJson D.doc).find? (setUnit · == u)).any (fun s => !(readingsJson s).isEmpty) &&
    D.governors.any (fun g => coversU D g u) &&
    D.governors.all (fun g => g.unit != u && (layoutReach g.reach || !coversU D g u))

def governedSets (D : SDoc) : List Json := (setsJson D.doc).filter fun s => (governedSetUnits D).contains (setUnit s)

/-- A governed set as lf-14d's enumeration reads it: its id, its version and its number of readings
    (`VE.Discourse.mem_allChoices`: the enumeration reads nothing else). -/
def shapeOf (s : Json) : VE.Route.Admission.ReadingSet := ⟨idOf s, setVersion s, (readingsJson s).map fun _ => .top⟩

def setShapes (D : SDoc) : List VE.Route.Admission.ReadingSet := (governedSets D).map shapeOf

/-- Every joint choice of the governed sets, lf-14d's product in lf-14d's order, within the limit. -/
def setChoices (D : SDoc) : Except String (List VE.Discourse.Choice) :=
  if VE.Discourse.productSize (setShapes D) > choiceLimit then .error "ResourceLimit: scope choices"
  else .ok (VE.Discourse.allChoices (setShapes D))

def pickOf (ch : VE.Discourse.Choice) (s : Json) : Option Nat :=
  (ch.find? (fun x => x.1 == idOf s && x.2.1 == setVersion s)).map (·.2.2)
def readingAt (s : Json) (i : Nat) : Json := (((readingsJson s)[i]?).map (·.getObjValD "content")).getD .null

/-- The document under one choice: each unit of `su` carries the content of its set's chosen reading, and the sets on
    the units of `su` leave `reading_sets`. -/
def atChoiceOn (su : List String) (doc : Json) (ch : VE.Discourse.Choice) : Json :=
  let sets := setsJson doc
  let units := (unitsOf doc).map fun u =>
    match sets.find? (fun s => su.contains (setUnit s) && setUnit s == idOf u) with
    | some s => u.setObjVal! "content" (((pickOf ch s).map (readingAt s)).getD .null)
    | none => u
  (doc.setObjVal! "units" (.arr units.toArray)).setObjVal! "reading_sets"
    (.arr (sets.filter fun s => !su.contains (setUnit s)).toArray)

def atChoice (D : SDoc) (ch : VE.Discourse.Choice) : SDoc :=
  { D with doc := atChoiceOn (governedSetUnits D) D.doc ch }

/-- `govern` under one joint choice of the governed sets: the sibling of 5.7's `governAt`, whose `pick` fixes a
    governor's reach and cannot carry a unit's reading. -/
def governChoice (D : SDoc) (ch : VE.Discourse.Choice) : Except String Json := govern (atChoice D ch)

/-- 11.5: a choice, named by each governed set's unit, set, version and chosen reading. -/
def choiceText (D : SDoc) (ch : VE.Discourse.Choice) : String :=
  ", ".intercalate ((governedSets D).filterMap fun s => (pickOf ch s).map fun i =>
    s!"{setUnit s} {idOf s}@{setVersion s}:{(((readingsJson s)[i]?).map idOf).getD ""}")

/-- 11.5: a fault under a choice names the choice; a resource limit is passed on as it is (UNKNOWN). -/
def choiceFault (D : SDoc) (ch : VE.Discourse.Choice) (e : String) : String :=
  if e.startsWith "ResourceLimit" then e else s!"ScopeChoice: {choiceText D ch}: {e}"

/-- 11.5: the first fault in lf-14d's order of the choices, as the document's own text when every choice has that
    fault (it does not depend on the choice), else named with its choice by `choiceFault`. -/
def faultOf (D : SDoc) (rs : List (VE.Discourse.Choice × Except String Json)) : Option String :=
  match rs.findSome? (fun (ch, r) => match r with | .error e => some (ch, e) | .ok _ => none) with
  | none => none
  | some (ch, e) =>
    some (if rs.all (fun (_, r) => match r with | .error e' => e' == e | .ok _ => false) then e else choiceFault D ch e)

/-- The answer from the per-choice answers `outs` (in lf-14d's order, `(ch₀, o₀)` the first): every unit outside the
    governed set units as `o₀` writes it, refused when another choice writes it otherwise; each governed set unit as
    written; each governed set's reading `i` with the content its unit has under the choices that pick `i`, refused
    when two of them differ. Equality is `VE.Readings.Wire.jeq`, the tree equality proved sound (`jeq_iff`). -/
def assemble (D : SDoc) (ch₀ : VE.Discourse.Choice) (o₀ : Json) (outs : List (VE.Discourse.Choice × Json)) :
    Except String Json := do
  let su := governedSetUnits D
  for (ch, o) in outs do
    for (x, x₀) in (unitsOf o).zip (unitsOf o₀) do
      unless su.contains (idOf x) || VE.Readings.Wire.jeq x x₀ do
        throw s!"ScopeReadings: {idOf x}: differs between choices {choiceText D ch₀} and {choiceText D ch}"
  let readingIn (s : Json) (i : Nat) : Except String Json :=
    match outs.filter (fun (ch, _) => pickOf ch s == some i) with
    | [] => pure (readingAt s i)
    | (c₁, o₁) :: rest => do
      for (c, o) in rest do
        unless VE.Readings.Wire.jeq (contentOf o (setUnit s)) (contentOf o₁ (setUnit s)) do
          throw s!"ScopeReadings: {setUnit s}: differs between choices {choiceText D c₁} and {choiceText D c}"
      pure (contentOf o₁ (setUnit s))
  let sets ← (setsJson D.doc).mapM fun s => do
    if su.contains (setUnit s) then
      let rs ← (readingsJson s).zipIdx.mapM fun (r, i) => do pure (r.setObjVal! "content" (← readingIn s i))
      pure (s.setObjVal! "readings" (.arr rs.toArray))
    else pure s
  let units := ((unitsOf o₀).zip (unitsOf D.doc)).map fun (x, y) => if su.contains (idOf y) then y else x
  pure ((D.doc.setObjVal! "units" (.arr units.toArray)).setObjVal! "reading_sets" (.arr sets.toArray))

/-- 11.2: GOVERN over the governed sets, with `gv` for `govern` (the run path passes `governFast`, 1.5.8). -/
def governSetsWith (gv : SDoc → Except String Json) (D : SDoc) : Except String Json := do
  if (governedSetUnits D).isEmpty then gv D else
  let cs ← setChoices D
  let rs := cs.map fun ch => (ch, gv (atChoice D ch))
  if let some e := faultOf D rs then throw e
  match rs.filterMap (fun (ch, r) => r.toOption.map (ch, ·)) with
  | [] => throw "ResourceLimit: scope choices"   -- never: every governed set holds a reading
  | outs@((ch₀, o₀) :: _) => assemble D ch₀ o₀ outs

def governSets (D : SDoc) : Except String Json := governSetsWith govern D

end VE.Scope
