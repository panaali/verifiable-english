import VE.Acts.Table

/-! Fixtures of the table, the renderings and the paraphrases (docs/spec/act-phrases.md 11.2, 11.3: T1 to T10,
the parts of G6 and G7, E9's paraphrases, P12n, D-32).

The act trees are written by hand as 11.2 gives them: the grammar's rule table and meaning (ap-2b, ap-2c) are not
built yet, so no tree here comes from a parse. Atoms are `⟨toWord, beWord, head, args, mods⟩`.
-/

namespace VE.Acts.TableExamples
open VE.Acts

def w (s : String) : Part := .words (wordsOf s)

/-- G6 (u027, V6): "be subjected to torture or to [cruel, …]", a split marker's *or*. -/
def fx6 : List String := ["cruel, inhuman or degrading treatment or punishment"]
def torture : Atom := ⟨false, true, ["subjected"], [("to", .one (w "torture"))], []⟩
def cruel : Atom := ⟨false, true, ["subjected"], [("to", .one (.fixed 0))], []⟩
def g6 : Act := .any false true [torture, cruel]

/-- G7 (u079b, V7): one atom, "by" a joined filler (not a split marker). -/
def fx7 : List String := ["equivalent free voting procedures"]
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
def fx11 : List String := ["freely chosen representatives"]
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

def errOf {α : Type} : Except String α → Option String
  | .error e => some e
  | .ok _ => none

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

/-! ### Renderings (5.5) -/

-- The parts of G6, as a permission's acts (no *to*), and part order kept.
#guard [torture, cruel].map (partAct fx6 .permission) ==
  ["{0} be subjected to torture", "{0} be subjected to cruel, inhuman or degrading treatment or punishment"]
-- G7's atom: the marker once before its joined filler.
#guard partAct fx7 .obligation held == "{0} be held by secret vote or equivalent free voting procedures"
-- *to* exactly when plain; adverbs before the head; the object, then marked arguments, then modifiers.
#guard partAct [] .plain (form true) == "{0} to form trade unions for the protection of their interests"
#guard partAct [] .permission (form true) == "{0} form trade unions for the protection of their interests"
#guard partAct fx11 .plain directly == "{0} to directly take part in {1}"
#guard Atom.text fx11 none through == "{0} to take part in {1} through freely chosen representatives"
#guard partAct ["the right to change their nationality"] .permission (denied true) ==
  "{0} be arbitrarily denied the right to change their nationality"
#guard partAct ["other lack of livelihood"] .plain
    ⟨true, false, ["security"], [("in the event of", .one (.fixed 0))], [beyond]⟩ ==
  "{0} to security in the event of other lack of livelihood in circumstances beyond their control"
-- A list of three and of two parts; the object before the other arguments, whatever their order in `args`.
#guard tokText [] (listToks .or [w "a", w "b", w "c"]) == "a, b or c"
#guard tokText [] (listToks .nor [w "a", w "b"]) == "a nor b"
#guard tokText [] (listToks .and [w "a b"]) == "a b"
#guard partAct [] .permission ⟨false, false, ["give"], [("to", .one (.slot 1)), ("", .one (w "notice"))], []⟩ ==
  "{0} give notice to {1}"
#guard tokText ["x"] [.slot 0, .fixed 0, .comma, .word "y"] == "{0} x, y"

/-! ### Paraphrases (2.2, 6.2) -/

-- E9: G11 under *may*, the D-23 list exactly.
#guard ((paraphrases fx11 .may none "rule r" (table .may g11)).map numbered).toOption ==
  some "1. {0} may directly take part in {1}, and {0} may take part in {1} through freely chosen representatives. 2. {0} may directly take part in {1} or take part in {1} through freely chosen representatives, as one act done in any one of these ways (not each way on its own)."
-- Under *has the right* and *is entitled*, with *to*.
#guard paraphrase fx11 .right none [.atom directly] == "{0} has the right to directly take part in {1}."
#guard paraphrase fx11 .right (some .entitled) [.whole g11] == "{0} is entitled to directly take part in {1} or to take part in {1} through freely chosen representatives, as one act done in any one of these ways (not each way on its own)."
-- A whole join by *and*; a split of more than two; *must*, *need not*, *must not* without *to*.
#guard paraphrase [] .mustNot none [.whole (g12 false)] == "{0} must not form trade unions and join trade unions for the protection of their interests, as one act done together (not each on its own)."
#guard paraphrase [] .must none [.atom (form false), .atom join, .atom (form true)] == "{0} must form trade unions; {0} must join trade unions for the protection of their interests; and {0} must form trade unions for the protection of their interests."
#guard paraphrase [] .needNot none [.atom (form false)] == "{0} need not form trade unions."
#guard paraphrase fx6 .mustNot none [.whole (.any true false [torture, cruel])] == "{0} must not be subjected to torture nor be subjected to cruel, inhuman or degrading treatment or punishment, as one act done in any one of these ways (not each way on its own)."
-- P12n: G12's four readings under *must not* read as four distinct sentences.
#guard (paraphrases [] .mustNot none "rule r" (table .mustNot (g12 false) ++ table .mustNot (g12 true))).toOption.map List.length == some 4
-- D-32: two readings that read the same are refused, naming the first equal pair.
#guard errOf (paraphrases [] .may none "rule r" [[.atom join], [.atom (form false)], [.atom join]]) ==
  some "InvalidInput: readings 1 and 3 of rule r read the same in English; rephrase the act"
#guard errOf (distinctTexts "x" ["a", "b", "c", "b"]) == some "InvalidInput: readings 2 and 4 of x read the same in English; rephrase the act"
#guard (distinctTexts "x" ["a", "b"]).toOption == some ["a", "b"]
#guard numbered ["a", "b", "c"] == "1. a 2. b 3. c"

end VE.Acts.TableExamples
