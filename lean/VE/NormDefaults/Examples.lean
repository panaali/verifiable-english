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

/-! ## u16: limits -/

def longName (n : Nat) : String := "p" ++ String.mk (List.replicate (n - 1) 'q')

def u16 (n : Nat) : UDoc :=
  ⟨⟨envOf [(longName n, ["act"])] [], [], ⟨[⟨longName n, ["act"], false, .plain, none, none⟩], [], []⟩⟩,
    [longName n]⟩

#guard WellFormedU (u16 56)
#guard WellFormed (fill (u16 56))
#guard !WellFormedU (u16 57)

end VE.NormDefaults.Examples
