import VE.Arith.Bounded

/-! The example vocabulary (spec 12.3) and the fixtures of plan 4.3 that need no wire: M-1, M-1b, M-2, M-3, M-4 with
its measured bound, M-4b, M-4x and M-5, and the refusals the core decides. -/

namespace VE.Arith.Examples
open VE.Arith VE.Numbers

/-- p is prime: p is at least 2 and no whole number from 2 through p − 1 divides p. -/
def primeBody : Formula :=
  .and (.le (.num 2) (.var 0)) (.not (.exFromTo (.num 2) (.sub (.var 0) (.num 1)) (.dvd (.var 0) (.var 1))))

def primeDefs : Defs := [.pred "prime" 1 primeBody]

/-- M-3, whole-number reading. -/
def bertrand : Formula :=
  .allNat (.imp (.le (.num 1) (.var 0))
    (.exNat (.and (.call "prime" [.var 0]) (.and (.lt (.var 1) (.var 0)) (.le (.var 0) (.mul (.num 2) (.var 1)))))))

/-- M-1 through `hi`: for every n from 1 through hi there is a prime p from n + 1 through 2n. -/
def m1 (hi : Int) : Formula :=
  .allFromTo (.num 1) (.num hi) (.exFromTo (.add (.var 0) (.num 1)) (.mul (.num 2) (.var 0)) (.call "prime" [.var 0]))

/-- M-5: the strict n < p < 2n from 1 through 161. -/
def m5 : Formula :=
  .allFromTo (.num 1) (.num 161)
    (.exFromTo (.add (.var 0) (.num 1)) (.sub (.mul (.num 2) (.var 0)) (.num 1)) (.call "prime" [.var 0]))

/-- M-2: each number of the chain is prime and each is less than twice the one before, as a right fold of the 17
facts closed by the empty conjunction "0 equals 0" (the shape of spec 13.3's 395 units; without it, 393). -/
def m2 : Formula :=
  let c : List Int := [2, 3, 5, 7, 13, 23, 43, 83, 163]
  (c.map (fun n => Formula.call "prime" [.num n]) ++ (c.zip c.tail).map fun (a, b) => Formula.lt (.num b) (.mul (.num 2) (.num a))
    ).foldr .and (.eq (.num 0) (.num 0))

/-- M-4's vocabulary: π(x) and the number of primes p with 2p ≤ x, both from 1 through x. -/
def countDefs : Defs := primeDefs ++ [
  .fn "prime_count" 1 (.countFromTo (.num 1) (.var 0) (.call "prime" [.var 0])),
  .fn "half_prime_count" 1
    (.countFromTo (.num 1) (.var 0) (.and (.le (.mul (.num 2) (.var 0)) (.var 1)) (.call "prime" [.var 0])))]

/-- k ≤ π(x) − π(x/2) at the term x. -/
def atLeast (k : Int) (x : Term) : Formula :=
  .le (.num k) (.sub (.call "prime_count" [x]) (.call "half_prime_count" [x]))

/-- Formula (18)'s pair (k, T) from T through N. -/
def m4 (k T N : Int) : Formula := .allFromTo (.num T) (.num N) (atLeast k (.var 0))

/-! M-1, M-1b, M-4x: holds, and exactly its 17,011 units; one fewer, or 1,000, is unknown, never fails. -/
#guard decideBounded primeDefs maxSteps (m1 161) = some (true, 17011)
#guard decideBounded primeDefs 17011 (m1 161) = some (true, 17011)
#guard decideBounded primeDefs 17010 (m1 161) = none
#guard arithOutcome primeDefs maxSteps (m1 161) = .decided .holds
#guard arithOutcome primeDefs 1000 (m1 161) = .unknown (.limit .evaluations)
#guard maxSteps = 1000000
#guard decideBounded primeDefs 0 (m1 161) = none

/-! M-2 holds; one link broken (163 against 81) fails. -/
#guard decideBounded primeDefs maxSteps m2 = some (true, 395)
#guard (decideBounded primeDefs maxSteps (.and m2 (.lt (.num 163) (.mul (.num 2) (.num 81))))).map (·.1) = some false

/-! M-3: stated, not decided; M-1 is bounded. -/
#guard bertrand.Bounded primeDefs = false && (m1 161).Bounded primeDefs
#guard arithOutcome primeDefs maxSteps bertrand = .unknown .unboundedStatement
#guard UnknownReason.text maxSteps .unboundedStatement = "stated, not decided: a quantifier has no bound"

/-! M-5 fails in 2 units: the ∀ node and the ∃ at n = 1, whose range 2 … 1 is empty, so n = 1 decides it. -/
#guard decideBounded primeDefs maxSteps m5 = some (false, 2)
#guard arithOutcome primeDefs maxSteps m5 = .decided .fails
#guard decideBounded primeDefs maxSteps
  (.exFromTo (.add (.num 1) (.num 1)) (.sub (.mul (.num 2) (.num 1)) (.num 1)) (.call "prime" [.var 0])) = some (false, 1)

/-! M-4: π(10) − π(5) = 1 and π(11) − π(5) = 2 (spec 13.3's 111 and 127 units for the difference, plus the `le` node);
measured at the candidate bounds 200 and 1,000, the completing bound is 248 within 1,000,000 units. -/
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 10)) = some (false, 112)
#guard decideBounded countDefs maxSteps (atLeast 2 (.num 11)) = some (true, 128)
#guard decideBounded countDefs maxSteps (m4 2 11 200) = some (true, 576518)
#guard decideBounded countDefs maxSteps (m4 2 11 248) = some (true, 998395)
#guard decideBounded countDefs maxSteps (m4 2 11 249) = none
#guard decideBounded countDefs 2000000 (m4 2 11 249) = some (true, 1008568)
#guard decideBounded countDefs maxSteps (m4 2 11 1000) = none

/-! M-4b: each pair (k, T) fails at T − 1, holds at T, and holds through its measured bound N, unknown at N + 1. -/
#guard [(1, 2), (3, 17), (4, 29), (5, 41)].map (fun (k, T) =>
    ((decideBounded countDefs maxSteps (atLeast k (.num (T - 1)))).map (·.1),
     (decideBounded countDefs maxSteps (atLeast k (.num T))).map (·.1))) =
  [(some false, some true), (some false, some true), (some false, some true), (some false, some true)]
#guard decideBounded countDefs maxSteps (m4 1 2 248) = some (true, 998948)
#guard decideBounded countDefs maxSteps (m4 1 2 249) = none
#guard decideBounded countDefs maxSteps (m4 3 17 248) = some (true, 997399)
#guard decideBounded countDefs maxSteps (m4 3 17 249) = none
#guard decideBounded countDefs maxSteps (m4 4 29 248) = some (true, 993580)
#guard decideBounded countDefs maxSteps (m4 4 29 249) = none
#guard decideBounded countDefs maxSteps (m4 5 41 249) = some (true, 997116)
#guard decideBounded countDefs maxSteps (m4 5 41 250) = none

/-! Admission: the fixtures are admitted; each refusal the core decides, and the decoder's order between them. -/
#guard caseRefusal countDefs [m1 161, m5, m2, bertrand, m4 2 11 248] = none
#guard countDefs.WellFormed && (m1 161).Scoped countDefs 0 && (Formula.lt (.var 1) (.var 0)).Scoped primeDefs 2
#guard !(Formula.lt (.var 2) (.var 0)).Scoped primeDefs 2
#guard caseRefusal primeDefs [.allFromTo (.num 1) (.num 2) (.lt (.var 0) (.var 1))] = some (.unscopedVariable 0)
#guard caseRefusal primeDefs [.call "composite" [.num 4]] = some (.unknownDefinition "composite")
#guard caseRefusal primeDefs [.eq (.call "prime" [.num 4]) (.num 0)] = some (.unknownDefinition "prime")
#guard caseRefusal [.pred "loop" 1 (.call "loop" [.var 0])] [] = some (.recursiveDefinition "loop")
#guard caseRefusal [.pred "a" 1 (.call "b" [.var 0]), .pred "b" 1 (.le (.var 0) (.num 1))] [] = some (.recursiveDefinition "b")
#guard caseRefusal primeDefs [.call "prime" [.num 1, .num 2]] = some (.arityMismatch "prime" 1)
#guard caseRefusal primeDefs [.le (.num 0) (.countFromTo (.num 1) (.num 9) (.exNat (.eq (.var 0) (.var 1))))] =
  some .unboundedCount
#guard caseRefusal [.pred "p" 1 (.le (.num 0) (.countFromTo (.num 1) (.var 0) (.allInt (.eq (.var 0) (.var 0)))))] [] =
  some .unboundedCount
#guard caseRefusal (primeDefs ++ primeDefs) [] = some (.duplicateName "prime")
#guard caseRefusal primeDefs [.call "nope" [.var 0]] = some (.unscopedVariable 0)
#guard caseRefusal primeDefs [.call "prime" [.num 1, .num 2], .call "nope" []] = some (.unknownDefinition "nope")
#guard [Refusal.duplicateName "", .unscopedVariable 0, .unknownDefinition "", .recursiveDefinition "",
    .arityMismatch "" 0, .unboundedCount].map Refusal.code =
  ["DuplicateName", "UnscopedVariable", "UnknownDefinition", "RecursiveDefinition", "ArityMismatch", "UnboundedCount"]

end VE.Arith.Examples
