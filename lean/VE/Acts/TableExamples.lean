import VE.Acts.Table
import VE.Acts.Syntax

/-! Fixtures of the ops and the table (docs/spec/act-phrases.md 6.1 and 11.3: T1 to T10, on the act trees of 11.2).

The act trees are written by hand as 11.2 gives them: the grammar's rule table and meaning (ap-2b, ap-2c) are not
built yet, so no tree here comes from a parse. Atoms are `⟨toWord, beWord, head, args, mods⟩`.
-/

namespace VE.Acts.TableExamples
open VE.Acts

def w (s : String) : Part := .words (wordsOf s)

/-- G6 (u027, V6): "be subjected to torture or to [cruel, …]", a split marker's *or*. -/
def torture : Atom := ⟨false, true, ["subjected"], [("to", .one (w "torture"))], []⟩
def cruel : Atom := ⟨false, true, ["subjected"], [("to", .one (.fixed 0))], []⟩
def g6 : Act := .any false true [torture, cruel]

/-- G7 (u079b, V7): one atom, "by" a joined filler (not a split marker). -/
def held : Atom := ⟨false, true, ["held"], [("by", .joined .or [w "secret vote", .fixed 0])], []⟩
def g7 : Act := .one held

/-- G9 (u055, V9): *nor*; *arbitrarily* on `deprived` only, or on both. -/
def deprived : Atom := ⟨false, true, ["deprived"], [("of", .one (w "their nationality"))], [.adv "arbitrarily"]⟩
def denied (arb : Bool) : Atom :=
  ⟨false, true, ["denied"], [("", .one (.fixed 0))], if arb then [.adv "arbitrarily"] else []⟩
def g9 (arb : Bool) : Act := .any true false [deprived, denied arb]

/-- G10 (u092, V10): six causes under the split marker "in the event of"; the modifier on the last or on all. -/
def causes : List Part := [w "unemployment", w "sickness", w "disability", w "widowhood", w "old age", .fixed 0]
def beyond : Modifier := .prep "in circumstances" (w "beyond their control")
def g10 (all : Bool) : Act :=
  .any false true ((List.range 6).zip causes |>.map fun (i, c) =>
    ⟨true, false, ["security"], [("in the event of", .one c)], if all || i == 5 then [beyond] else []⟩)

/-- G11 (u076, V11): two ways, *or*, not a split marker's. -/
def directly : Atom := ⟨true, false, ["take", "part"], [("in", .one (.slot 1))], [.adv "directly"]⟩
def through : Atom := ⟨true, false, ["take", "part"], [("in", .one (.slot 1))], [.prep "through" (.fixed 0)]⟩
def g11 : Act := .any false false [directly, through]

/-- G12 (u087, V12): own *to*; *for the protection …* on `join` only, or on both. -/
def protection : Modifier := .prep "for" (w "the protection of their interests")
def form (pr : Bool) : Atom := ⟨true, false, ["form"], [("", .one (w "trade unions"))], if pr then [protection] else []⟩
def join : Atom := ⟨true, false, ["join"], [("", .one (w "trade unions"))], [protection]⟩
def g12 (pr : Bool) : Act := .all false false [form pr, join]

/-- G14v (u0123.s03, V14): five acts joined by *or*. -/
def g14v : Act := .any false false
  [⟨false, false, ["abandon"], [("", .one (.fixed 0))], []⟩, ⟨false, false, ["claim"], [("", .one (.fixed 1))], []⟩,
   ⟨false, false, ["use"], [("", .one (.fixed 2))], []⟩, ⟨false, false, ["endanger"], [("", .one (.fixed 3))], []⟩,
   ⟨false, false, ["act"], [("against", .one (.fixed 4))], []⟩]

/-- The number of readings and of simple acts in each. -/
def shape (Rs : List (List Simple)) : List Nat := Rs.map List.length

def reg (role : VE.Norms.Role) : VE.Norms.Regulated := ⟨"p", ["person"], false, role, none, none⟩

/-! ### Ops (6.1) -/

#guard opOf (reg .obligation) true == some .must
#guard opOf (reg .obligation) false == some .needNot
#guard opOf (reg .permission) true == some .may
#guard opOf (reg .permission) false == some .mustNot
#guard opOf (reg .plain) true == some .right
#guard opOf (reg .plain) false == none

/-! ### The table per cell (11.3) -/

-- T1: must not, G6: two prohibitions.
#guard table .mustNot g6 == [[.atom torture, .atom cruel]]
-- T2: must, G7: the atom, the act unchanged.
#guard table .must g7 == [[.atom held]]
#guard ([Op.must, .needNot, .may, .mustNot, .right].map (table · g7)).all (· == [[.atom held]])
-- T3: must not, G9's trees: two atoms each.
#guard [false, true].all fun b => table .mustNot (g9 b) == [[.atom deprived, .atom (denied b)]]
-- T4: may and has the right to, G9's trees: no reading (nor).
#guard [false, true].all fun b => table .may (g9 b) == [] && table .right (g9 b) == []
-- T5: has the right to and may, G11: each way, or one act.
#guard table .right g11 == [[.atom directly, .atom through], [.whole g11]]
#guard table .may g11 == [[.atom directly, .atom through], [.whole g11]]
-- T6: has the right to and may, G12's trees (own "to"): two atoms each.
#guard [false, true].all fun b => table .right (g12 b) == [[.atom (form b), .atom join]] && table .may (g12 b) == [[.atom (form b), .atom join]]
-- T7: has the right to, G10's trees (split marker): six atoms each.
#guard [false, true].all fun b => shape (table .right (g10 b)) == [6] && shape (table .may (g10 b)) == [6]
-- T8: must, G6 (a split marker's or): no reading.
#guard table .must g6 == []
-- must, an or that is not a split marker's: one act; nor: no reading.
#guard table .must g11 == [[.whole g11]]
#guard table .must (g9 false) == []
#guard table .must g14v == [[.whole g14v]]
-- must, and: split, whatever the flags.
#guard [false, true].all fun b => table .must (.all b true [torture, cruel]) == [[.atom torture, .atom cruel]] &&
  table .must (.all b false [torture, cruel]) == [[.atom torture, .atom cruel]]
-- T9: must not, G12's first tree (and, not split): each, or only doing both.
#guard table .mustNot (g12 false) == [[.atom (form false), .atom join], [.whole (g12 false)]]
#guard table .mustNot (.all true false [torture, cruel]) == [[.atom torture, .atom cruel], [.whole (.all true false [torture, cruel])]]
-- must not, a split marker's and: each only.
#guard [false, true].all fun b => table .mustNot (.all b true [torture, cruel]) == [[.atom torture, .atom cruel]]
-- must not, G14v: five prohibitions (E3's count).
#guard shape (table .mustNot g14v) == [5]
-- T10: need not, any join: no reading.
#guard [g6, g9 true, g11, g12 true, g14v, .all true true [torture, cruel]].all (table .needNot · == [])
-- may and has the right to, a shared "to" (and, not split): each, or both together; a split marker's and: each.
#guard [Op.may, .right].all fun op => table op (.all true false [form false, join]) ==
  [[.atom (form false), .atom join], [.whole (.all true false [form false, join])]] &&
  table op (.all true true [torture, cruel]) == [[.atom torture, .atom cruel]] &&
  table op (.all false true [torture, cruel]) == [[.atom torture, .atom cruel]]
-- a split marker's or under may and has the right to: each.
#guard table .may g6 == [[.atom torture, .atom cruel]] && table .right g6 == [[.atom torture, .atom cruel]]
-- nor under a split marker, under may: no reading.
#guard table .may (.any true true [torture, cruel]) == [] && table .right (.any true true [torture, cruel]) == []
#guard table .mustNot (.any true true [torture, cruel]) == [[.atom torture, .atom cruel]]
-- `freeTable` on its own: a simple act is its one reading.
#guard freeTable (.one torture) == [[.atom torture]]
#guard freeTable g11 == table .may g11 && freeTable (g9 true) == []

/-! ### The trees and the table's types (5.4; review F1)

Each type's constructors are matched once with no wildcard, so a constructor added or dropped fails here. Trees built
with named arguments pin each field's name to its place: the other fixtures build them by position only.
-/

def joinWord : Join → String | .and => "and" | .or => "or" | .nor => "nor"
def partIndex : Part → Option Nat | .slot i => some i | .fixed i => some i | .words _ => none
def fillerParts : Filler → List Part | .one p => [p] | .joined _ ps => ps
def modifierWord : Modifier → String | .adv w => w | .prep m _ => m
def actParts : Act → List Atom | .one a => [a] | .all _ _ ps => ps | .any _ _ ps => ps
def simpleParts : Simple → List Atom | .atom a => [a] | .whole A => actParts A
def opWords : Op → String
  | .must => "must" | .needNot => "need not" | .may => "may" | .mustNot => "must not" | .right => "has the right to"

-- A filler joined by and, or and nor stays one filler of one atom (1.5).
def heldBy (j : Join) : Atom := ⟨false, true, ["held"], [("by", .joined j [w "secret vote", .fixed 0])], []⟩
#guard [Join.and, .or, .nor].map joinWord == ["and", "or", "nor"]
#guard [Join.and, .or, .nor].all fun j => [Op.must, .needNot, .may, .mustNot, .right].all (table · (.one (heldBy j)) == [[.atom (heldBy j)]])
#guard [Join.and, .or, .nor].map (fun j => (heldBy j).args.map (fillerParts ·.2)) == [[[w "secret vote", .fixed 0]], [[w "secret vote", .fixed 0]], [[w "secret vote", .fixed 0]]]
#guard heldBy .or == held && heldBy .and != heldBy .nor
-- An index is a natural number: 0 - 1 is 0.
#guard [Part.slot (0 - 1), .fixed (0 - 1), w "torture"].map partIndex == [some 0, some 0, none]
#guard [beyond, protection, .adv "directly"].map modifierWord == ["in circumstances", "for", "directly"]
#guard [Op.must, .needNot, .may, .mustNot, .right].map opWords == ["must", "need not", "may", "must not", "has the right to"]
#guard simpleParts (.whole g11) == [directly, through] && simpleParts (.atom held) == [held] && actParts g7 == [held]
-- *to* and *be* as read: "be subjected", "be held", "be deprived"; "to take part", "to form", "to join".
#guard [torture, cruel, held, deprived, denied true].all fun a => a.beWord && !a.toWord
#guard [directly, through, form true, join].all fun a => a.toWord && !a.beWord
-- The same trees by name.
def joinByName : Atom :=
  { toWord := true, beWord := false, head := ["join"], args := [("", .one (w "trade unions"))], mods := [protection] }
#guard joinByName == join
#guard Act.all (shared := false) (split := false) (parts := [form true, joinByName]) == g12 true
#guard Act.any (nor := true) (split := false) (parts := [deprived, denied true]) == g9 true
#guard Act.any (nor := false) (split := true) (parts := [torture, cruel]) == g6
-- Their readings: a shared *to* reads each, or both together; *nor* under *may* has no reading.
#guard table .may (Act.all (shared := true) (split := false) (parts := [form false, joinByName])) ==
  [[.atom (form false), .atom join], [.whole (.all true false [form false, join])]]
#guard table .may (Act.any (nor := true) (split := false) (parts := [deprived, denied true])) == []
#guard table .must (Act.any (nor := false) (split := true) (parts := [torture, cruel])) == []

end VE.Acts.TableExamples
