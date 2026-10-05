import VE.Readings.Scan
import VE.Readings.Examples

/-! How much of the other reading's side the route's pair check evaluates, as build-time checks (`#guard`).
`Run.lean`'s `pairFacts` runs `otherScan` in `Id`; here it runs in a state monad that counts its two kinds of
evaluation: a completion's admissibility (`sideValidOf`) and its value (`sideValueOf`). Each count is pinned below the
`2 ^ cells` completions that evaluating every completion would cost, and each answer is `separates`'s. The
fixtures are `Examples.lean`'s environment K with set `rs1` = {0: strict `S`, 1: default `Df`}: the default
reading owns one key, `excepted no-deception`, with one cell per user. -/
namespace VE.Readings.RunExamples
open VE.Readings
open VE.Readings.Examples

/-- The state: admissibility evaluations, then value evaluations. -/
abbrev Counted := StateM (Nat × Nat)
def tickValid : Counted Unit := modify (fun c => (c.1 + 1, c.2))
def tickValue : Counted Unit := modify (fun c => (c.1, c.2 + 1))

/-- The other side of the pair (witness i, other j) as `pairFacts` scans it: the scan's answer (a completion of
    j shows the value while the witness does, some completion of j is admissible) and the two counts. -/
def scanned (D : Doc) (s : String) (i j : Nat) (σ : Situation String) : (Bool × Bool) × (Nat × Nat) :=
  let Ti := tablesFor D s i (σ.fixed ++ σ.decisions)
  let want := sideValid D s i σ.base Ti && sideValue D s i σ.base Ti σ.probe == some σ.value
  (otherScan tickValid tickValue (one D s j) σ.base (tablesFor D s j σ.fixed) σ.probe σ.value want
    (assignments D s j σ.base)).run (0, 0)

def users4 : List String := ["u1", "u2", "u3", "u4"]
def m4 := modelK users4 []
#guard cells K1 "rs1" 1 m4 == 4 && (assignments K1 "rs1" 1 m4).length == 16

/-! The review's case: the strict witness answers `false` on `help_required`, which no rule regulates, and so does
the default reading's first completion. One admissibility and one value are evaluated, not 16. -/
def σHelp : Situation String := sit m4 [] [] (.outcome "help_required" ["a", "u1"]) false
#guard scanned K1 "rs1" 0 1 σHelp == ((true, true), (1, 1))
#guard !separates K1 "rs1" 0 1 σHelp

/-! The first completion that shows the value is the ninth: the eight before it except `(a, u1)`. -/
def σAvoid : Situation String := sit m4 [] [] (.outcome "avoid_required" ["a", "u1"]) true
#guard scanned K1 "rs1" 0 1 σAvoid == ((true, true), (9, 9))
#guard !separates K1 "rs1" 0 1 σAvoid

/-! The witness does not show the value: no value of the other side is evaluated, and the scan stops at the first
admissible completion (`other_admissible`). -/
def σWrong : Situation String := sit m4 [] [] (.outcome "avoid_required" ["a", "u1"]) false
#guard scanned K1 "rs1" 0 1 σWrong == ((false, true), (1, 0))
#guard !separates K1 "rs1" 0 1 σWrong

/-! K14: no completion of the default reading is admissible. Each admissibility is evaluated once and no value
is; the pair is separated. -/
#guard scanned K14 "rs1" 0 1 (sit m1 [] [] q0 true) == ((false, false), (2, 0))
#guard separates K14 "rs1" 0 1 (sit m1 [] [] q0 true)

end VE.Readings.RunExamples
