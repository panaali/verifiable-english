import VE.NormDefaults.Replay

/-! Build-time regressions in the shapes of section 9's fixtures (docs/spec/norm-defaults.md):
u1 (an entity other than Claude: SETTLED no for `claude`, UNDECIDED for `sol`), u5 (pairs:
the pair rule settles a gap, and both-gap pairs allow only the fillings that respect "whatever
must be done may be done"), u6 (a latent conflict and its undecided cause), u12 (Kleene
incompleteness settled by enumeration, UNKNOWN with no budget) and u16 (the name-length limit).
Every value is computed by the definitions the theorems are about; `#guard` fails the build on
a regression. -/
namespace VE.NormDefaults.Examples
open VE.Norms

def act : String := "{0} be done"

def envOf (preds : List (String × List String)) (consts : List (String × String)) : VE.Environment :=
  ⟨["act", "entity"], fun p => VE.Bridge.lookup preds p, fun c => VE.Bridge.lookup consts c⟩

def modelOf (domain : String) (xs : List String) (rels : List (String × List (List String))) :
    VE.FiniteModel String :=
  { domains := fun s => if s = domain then xs else []
    constants := fun c => if c ∈ xs then some c else none
    relations := fun p => (VE.Bridge.lookup rels p).getD [] }

/-! ## u1: u0165.s07 -/

def csam : String := "csam_generation_permitted"

def u1 : UDoc :=
  ⟨⟨envOf [(csam, ["entity"])] [("claude", "entity"), ("sol", "entity")], [],
    ⟨[⟨csam, ["entity"], false, .permission, some "{0} generate child sexual abuse material", none⟩], [],
     [⟨"no-csam-generation", csam, false, .eq (.var 0) (.const "claude"), [], []⟩]⟩⟩, [csam]⟩

def m1 : VE.FiniteModel String := modelOf "entity" ["claude", "sol"] []

#guard WellFormedU u1
#guard WellFormed (fill u1)
#guard table3 u1 m1 csam ["claude"] == some false
#guard table3 u1 m1 csam ["sol"] == none
#guard enumerateSettled u1 m1 csam ["claude"] == some false
#guard enumerateSettled u1 m1 csam ["sol"] == none
-- the UNDECIDED witness: fillings {sol} and {}
def u1yes : FiniteFill u1 String := fun n => if n = unsaidName csam then [["sol"]] else []
def u1no : FiniteFill u1 String := fun _ => []
#guard fillValid u1 m1 u1yes && fillValid u1 m1 u1no
#guard (outcomeBase (fill u1) csam).eval (m1.withFill u1yes) (tupleVal ["sol"]) == true
#guard (outcomeBase (fill u1) csam).eval (m1.withFill u1no) (tupleVal ["sol"]) == false
-- the deny variant is the unchanged W1 document: `sol` SETTLED no
#guard table3 ⟨u1.D, []⟩ m1 csam ["sol"] == some false

/-! ## u5: pairs -/

def req : Regulated := ⟨"x_required", ["act"], false, .obligation, some act, some "x_permitted"⟩
def perm : Regulated := ⟨"x_permitted", ["act"], false, .permission, some act, none⟩

def pairDoc (nodes : List Node) (unspec : List String) : UDoc :=
  ⟨⟨envOf [("x_required", ["act"]), ("x_permitted", ["act"])] [("a", "act")], [], ⟨[req, perm], [], nodes⟩⟩,
    unspec⟩

def m5 : VE.FiniteModel String := modelOf "act" ["a"] []

-- (a) `x_required` unspecified, `x_permitted` deny, no rules: `x_required` SETTLED no (pair rule)
def u5a : UDoc := pairDoc [] ["x_required"]
#guard WellFormedU u5a
#guard table3 u5a m5 "x_required" ["a"] == some false
#guard enumerateSettled u5a m5 "x_required" ["a"] == some false
-- (b) `x_permitted` unspecified and "Every act must be done": `x_permitted` SETTLED yes (pair rule)
def u5b : UDoc := pairDoc [⟨"every-act", "x_required", true, .top, [], []⟩] ["x_permitted"]
#guard WellFormedU u5b
#guard table3 u5b m5 "x_permitted" ["a"] == some true
#guard enumerateSettled u5b m5 "x_permitted" ["a"] == some true
-- (c) both unspecified, no rules: both UNDECIDED; the filling (yes, no) fails `Fill_T`
def u5c : UDoc := pairDoc [] ["x_required", "x_permitted"]
#guard WellFormedU u5c
#guard table3 u5c m5 "x_permitted" ["a"] == none
#guard enumerateSettled u5c m5 "x_permitted" ["a"] == none
#guard enumerateSettled u5c m5 "x_required" ["a"] == none
def u5cBad : FiniteFill u5c String := fun n => if n = unsaidName "x_required" then [["a"]] else []
#guard fillValid u5c m5 u5cBad == false
def u5cBoth : FiniteFill u5c String := fun n =>
  if n = unsaidName "x_required" ∨ n = unsaidName "x_permitted" then [["a"]] else []
#guard fillValid u5c m5 u5cBoth

/-! ## u6: latent conflict -/

def yperm : Regulated := ⟨"y_permitted", ["act"], false, .permission, some "{0} be tried", none⟩

def u6 (unspec : List String) : UDoc :=
  ⟨⟨envOf [("x_required", ["act"]), ("x_permitted", ["act"]), ("y_permitted", ["act"])] [("a", "act")], [],
    ⟨[req, perm, yperm], [],
     [⟨"must-x-if-may-y", "x_required", true, .unary "y_permitted" (.var 0), [], []⟩,
      ⟨"must-not-x", "x_permitted", false, .top, [], []⟩]⟩⟩, unspec⟩

#guard WellFormedU (u6 ["y_permitted"])
-- the latent witness: `y_permitted(a)` filled yes makes the pair conflict true
def m6 : VE.FiniteModel String := modelOf "act" ["a"] [(unsaidName "y_permitted", [["a"]])]
#guard (fillPremises (u6 ["y_permitted"])).all (fun φ => φ.eval m6 [])
#guard (pairConflict (fill (u6 ["y_permitted"])) ⟨"x_required", "x_permitted", ["act"]⟩).eval m6 (tupleVal ["a"])
-- `y_permitted(a)` is UNDECIDED, not SETTLED no
#guard enumerateSettled (u6 ["y_permitted"]) m5 "y_permitted" ["a"] == none
-- with `y_permitted` deny the pair conflict is false: CONFLICT-FREE, as today
#guard !(pairConflict (fill (u6 [])) ⟨"x_required", "x_permitted", ["act"]⟩).eval m5 (tupleVal ["a"])

/-! ## u12: Kleene incompleteness -/

def u12 : UDoc :=
  ⟨⟨envOf [("x_required", ["act"]), ("x_permitted", ["act"]), ("y_permitted", ["act"])] [("a", "act")], [],
    ⟨[req, perm, yperm], [],
     [⟨"must-x", "x_required", true, .or (.unary "y_permitted" (.var 0)) (.not (.unary "y_permitted" (.var 0))),
       [], []⟩]⟩⟩, ["y_permitted"]⟩

#guard WellFormedU u12
#guard table3 u12 m5 "x_required" ["a"] == none
#guard enumerateSettled u12 m5 "x_required" ["a"] == some true
-- more than `MAX_UNSAID_ATOMS` unsaid atoms in the situation, one in the point's cone:
-- enumeration over the cone settles it, as Python's does (review B2)
def m13 : VE.FiniteModel String := modelOf "act" ((List.range 13).map (fun i => if i = 0 then "a" else s!"a{i}")) []
#guard (unsaidAtoms u12 m13).length == 13
#guard coneAtoms u12 m13 "x_required" ["a"] == [(unsaidName "y_permitted", ["a"])]
#guard enumerateSettled u12 m13 "x_required" ["a"] == some true

/-! ## A symbol placed between the members of a pair (review B1)

`x_permitted` unspecified with no rules; `a_permitted` deny, "may A if may X";
`x_required` deny, "must X if c". `table3` places `a_permitted` before the pair closes, so
`a_permitted(a)` stays unknown there; Python's `table3` does the same, and enumeration over
the cone settles it yes in both. -/

def aperm : Regulated := ⟨"a_permitted", ["act"], false, .permission, some "{0} be audited", none⟩

def uBetween : UDoc :=
  ⟨⟨envOf [("x_required", ["act"]), ("x_permitted", ["act"]), ("a_permitted", ["act"]), ("c", ["act"])]
      [("a", "act")], [],
    ⟨[req, perm, aperm], [],
     [⟨"may-a", "a_permitted", true, .unary "x_permitted" (.var 0), [], []⟩,
      ⟨"must-x", "x_required", true, .unary "c" (.var 0), [], []⟩]⟩⟩, ["x_permitted"]⟩

def mc : VE.FiniteModel String := modelOf "act" ["a"] [("c", [["a"]])]
#guard WellFormedU uBetween
#guard (syms (fill uBetween).T).map (·.name) == ["x_permitted", "a_permitted", "x_required"]
#guard table3 uBetween mc "x_permitted" ["a"] == some true
#guard table3 uBetween mc "a_permitted" ["a"] == none
#guard enumerateSettled uBetween mc "a_permitted" ["a"] == some true

-- Every row of a symbol reads the table before it (loop recheck): the close of
-- `x_permitted(a)` made at row `a` of `x_required` is not read by its row `b`, through an
-- existential or through a constant, whichever row `c` holds on.
def uRows (g : VE.Formula) : UDoc :=
  ⟨⟨envOf [("x_required", ["act"]), ("x_permitted", ["act"]), ("c", ["act"])] [("a", "act")], [],
    ⟨[req, perm], [],
     [⟨"must-x", "x_required", true, .unary "c" (.var 0), [], []⟩,
      ⟨"must-x-2", "x_required", true, g, [], []⟩]⟩⟩, ["x_permitted"]⟩

def someX : VE.Formula := .ex "act" (.unary "x_permitted" (.var 0))
def rowGuards : List VE.Formula := [someX, .unary "x_permitted" (.const "a")]
#guard rowGuards.all fun g => WellFormedU (uRows g)
#guard rowGuards.all fun g =>
  let m := modelOf "act" ["a", "b"] [("c", [["a"]])]
  table3 (uRows g) m "x_required" ["a"] == some true && table3 (uRows g) m "x_permitted" ["a"] == some true &&
  table3 (uRows g) m "x_required" ["b"] == none && table3 (uRows g) m "x_permitted" ["b"] == none &&
  enumerateSettled (uRows g) m "x_required" ["b"] == some true
#guard
  let m := modelOf "act" ["a", "b"] [("c", [["b"]])]
  table3 (uRows someX) m "x_required" ["b"] == some true &&
  table3 (uRows someX) m "x_required" ["a"] == none

/-! ## u16: limits -/

def longName (n : Nat) : String := "p" ++ String.mk (List.replicate (n - 1) 'q')

def u16 (n : Nat) : UDoc :=
  ⟨⟨envOf [(longName n, ["act"])] [], [], ⟨[⟨longName n, ["act"], false, .plain, none, none⟩], [], []⟩⟩,
    [longName n]⟩

#guard WellFormedU (u16 56)
#guard WellFormed (fill (u16 56))
#guard !WellFormedU (u16 57)

end VE.NormDefaults.Examples
