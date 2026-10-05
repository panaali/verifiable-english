import VE.Readings.Scan
import VE.Readings.Examples
import VE.Readings.Wire

/-! How much of the other reading's side the route's pair check evaluates, as build-time checks (`#guard`), with
no timing (batch 3d review B). `Run.lean`'s `pairFactsIn` runs `Scan.lean`'s `pairEval` in `Id`; here it runs in a state
monad that counts its two kinds of evaluation of the other side: a completion's admissibility (`sideValidOn`) and its
value (`sideValueOn`). Each count is pinned, far below the `2 ^ cells` completions that evaluating every completion
would cost, and each answer is `separates`'s. A `pairEval` that evaluates the completions up front, or reads them
other than through the scan, changes the counts. The fixtures are `Examples.lean`'s environment K with set `rs1` =
{0: strict `S`, 1: default `Df`}: the default reading owns one key, `excepted no-deception`, with one cell per user.
Last, which candidates' documents admission builds into the request's table (K15, a pending candidate; batch 3b). -/
namespace VE.Readings.RunExamples
open VE.Readings
open VE.Readings.Examples

/-- The state: admissibility evaluations, then value evaluations. -/
abbrev Counted := StateM (Nat × Nat)
def tickValid : Counted Unit := modify (fun c => (c.1 + 1, c.2))
def tickValue : Counted Unit := modify (fun c => (c.1, c.2 + 1))

/-- The pair (witness i, other j) as `pairFactsIn` evaluates it, each candidate's side its own: the facts
    (`separated`, `witness_admissible`, `witness_value`, `other_admissible`, `other_value`) and the two counts. -/
def counted (D : Doc) (s : String) (i j : Nat) (σ : Situation String) :
    (Bool × Bool × Option Bool × Bool × Option Bool) × (Nat × Nat) :=
  (pairEval tickValid tickValue D s i j (sideOf D s i) (sideOf D s j) σ).run (0, 0)

/-- The facts as specified, for comparison. -/
def specified (D : Doc) (s : String) (i j : Nat) (σ : Situation String) :
    Bool × Bool × Option Bool × Bool × Option Bool :=
  let Ti := tablesFor D s i (σ.fixed ++ σ.decisions)
  let Tj := tablesFor D s j σ.fixed
  (separates D s i j σ, sideValid D s i σ.base Ti, sideValue D s i σ.base Ti σ.probe,
    (assignments D s j σ.base).any (fun G => sideValid D s j σ.base (Tj ++ G)),
    if ownedKeys D s j = [] then sideValue D s j σ.base Tj σ.probe else none)

/-! ## The review's 12-cell query

Twelve users: the default reading owns 12 cells, so 4,096 completions, the most `maxCells` admits. The strict
witness answers `false` on `help_required`, which no rule decides, and so does the default reading's first
completion: that one completion decides both `separated` and `other_admissible`. One admissibility and one value are
evaluated, not 4,096. -/
def users12 : List String := ["u"] ++ (List.range 11).map (fun k => s!"u{k + 1}")
def m12 := modelK users12 []
#guard cells K1 "rs1" 1 m12 == 12 && cells K1 "rs1" 1 m12 ≤ maxCells && (assignments K1 "rs1" 1 m12).length == 4096
def σHelp12 : Situation String := sit m12 [] [] (.outcome "help_required" ["a", "u"]) false
#guard counted K1 "rs1" 0 1 σHelp12 == ((false, true, some false, true, none), (1, 1))
#guard (counted K1 "rs1" 0 1 σHelp12).1 == specified K1 "rs1" 0 1 σHelp12

/-! The witness does not show the value: no value of the other side is evaluated, and the scan stops at the first
admissible completion (`other_admissible`). -/
def σWrong12 : Situation String := sit m12 [] [] (.outcome "avoid_required" ["a", "u"]) false
#guard (counted K1 "rs1" 0 1 σWrong12).2 == (1, 0)
#guard (counted K1 "rs1" 0 1 σWrong12).1 == specified K1 "rs1" 0 1 σWrong12

/-! ## Four users: the scan stops at the first completion that shows the value

`avoid_required` at `(a, u1)` is `true` for the strict witness; the default reading shows it once its table excepts
no `(a, u1)`. -/
def users4 : List String := ["u1", "u2", "u3", "u4"]
def m4 := modelK users4 []
#guard cells K1 "rs1" 1 m4 == 4 && (assignments K1 "rs1" 1 m4).length == 16
def σAvoid : Situation String := sit m4 [] [] (.outcome "avoid_required" ["a", "u1"]) true
#guard (counted K1 "rs1" 0 1 σAvoid).2 == (9, 9)
#guard (counted K1 "rs1" 0 1 σAvoid).1 == specified K1 "rs1" 0 1 σAvoid

/-! The review's case on four users (batch 3b): one admissibility and one value are evaluated, not 16; and with the
witness not showing the value, one admissibility and no value. -/
def σHelp : Situation String := sit m4 [] [] (.outcome "help_required" ["a", "u1"]) false
#guard (counted K1 "rs1" 0 1 σHelp).2 == (1, 1)
#guard (counted K1 "rs1" 0 1 σHelp).1 == specified K1 "rs1" 0 1 σHelp && !separates K1 "rs1" 0 1 σHelp
def σWrong : Situation String := sit m4 [] [] (.outcome "avoid_required" ["a", "u1"]) false
#guard (counted K1 "rs1" 0 1 σWrong).2 == (1, 0)
#guard (counted K1 "rs1" 0 1 σWrong).1 == specified K1 "rs1" 0 1 σWrong && !separates K1 "rs1" 0 1 σWrong

/-! ## Every completion inadmissible: each is evaluated once, no value

K14: no completion of the default reading is admissible; the pair is separated. -/
#guard counted K14 "rs1" 0 1 (sit m1 [] [] q0 true) == ((true, true, some true, false, none), (2, 0))
#guard (counted K14 "rs1" 0 1 (sit m1 [] [] q0 true)).1 == specified K14 "rs1" 0 1 (sit m1 [] [] q0 true)

/-! ## The other reading owns no key: its one completion, evaluated once

K1 with the default reading as witness and the strict reading as the other side. -/
def σK1 : Situation String := sit m0 [] [(exc "no-deception", [["a", "u"]])] q0 false
#guard counted K1 "rs1" 1 0 σK1 == ((true, true, some false, true, some true), (1, 1))
#guard (counted K1 "rs1" 1 0 σK1).1 == specified K1 "rs1" 1 0 σK1

/-! K15: admission builds no pending candidate's document (batch 3b looprecheck B; `onesOf_active`). The request's
table holds the strict candidate alone, and the stage admits the document as 4.4 over every candidate does. -/
def K15 : Doc := docK [.set rs15]
#guard (Wire.onesOf K15).map (·.1) == [("rs1", 0)]
#guard (Wire.candidateStage K15).toOption.map (·.map (·.1)) == some [("rs1", 0)]
#guard (Wire.candidatesOf K15).length == 2 &&
  (Wire.firstSome (Wire.candidatesOf K15) (fun c => Wire.candidateText K15.chain c.1 c.2 (one K15 c.1.id c.2))).isNone

end VE.Readings.RunExamples
