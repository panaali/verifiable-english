import VE.Arith.Holds
import VE.Arith.Defs

/-! The example vocabulary (spec 12.3) with its unfolding lemma, one meaning example per clause of `Holds` and
`Term.value` in both directions, and the admission of plan 4.3's fixture statements; their evaluation within the
budget (M-1, M-2, M-4, M-4b, M-4x, M-5) is me-12aa's, with `Bounded.lean`. -/

namespace VE.Arith.Examples
open VE.Arith

/-- p is prime: p is at least 2 and no whole number from 2 through p − 1 divides p. -/
def primeBody : Formula :=
  .and (.le (.num 2) (.var 0)) (.not (.exFromTo (.num 2) (.sub (.var 0) (.num 1)) (.dvd (.var 0) (.var 1))))

def primeDefs : Defs := [.pred "prime" 1 primeBody]

def IsPrime (p : Nat) : Prop := 2 ≤ p ∧ ∀ d : Nat, 2 ≤ d → d < p → ¬ d ∣ p

/-- M-3, whole-number reading. -/
def bertrand : Formula :=
  .allNat (.imp (.le (.num 1) (.var 0))
    (.exNat (.and (.call "prime" [.var 0]) (.and (.lt (.var 1) (.var 0)) (.le (.var 0) (.mul (.num 2) (.var 1)))))))

/-- VE's `prime` body means `IsPrime` at every whole number, in any environment (it calls no name). -/
theorem primeBody_iff (E : Env) (p : Nat) : Holds E [(p : Int)] primeBody ↔ IsPrime p := by
  simp only [primeBody, IsPrime, Holds, Term.value, List.getElem?_cons_zero, List.getElem?_cons_succ, Option.some.injEq,
    exists_and_left, exists_eq_left', not_exists, not_and, Int.natCast_dvd_natCast.symm]
  refine and_congr (by omega) ⟨fun H d h1 h2 => H d (by omega) (by omega), fun H i h1 h2 => ?_⟩
  have := H i.toNat (by omega) (by omega)
  rwa [show ((i.toNat : Nat) : Int) = i by omega] at this

/-- The core-Lean unfolding lemma the import project rewrites with. -/
theorem bertrand_means_iff :
    primeDefs.Means bertrand ↔ ∀ n : Nat, 1 ≤ n → ∃ p : Nat, IsPrime p ∧ n < p ∧ p ≤ 2 * n := by
  simp only [Defs.Means, bertrand, primeDefs, Defs.env, List.foldl, Holds, Term.value, Term.values,
    List.getElem?_cons_zero, List.getElem?_cons_succ, Option.some.injEq, ite_true, Prod.mk.injEq,
    exists_and_left, exists_eq_left', List.length_singleton]
  refine ⟨fun H n hn => ?_, fun H n hn => ?_⟩
  · obtain ⟨p, ⟨_, _, ⟨rfl, rfl⟩, _, hp⟩, h1, h2⟩ := H n (by omega)
    exact ⟨p, (primeBody_iff _ p).mp hp, by omega, by omega⟩
  · obtain ⟨p, hp, h1, h2⟩ := H n (by omega)
    exact ⟨p, ⟨1, _, ⟨rfl, rfl⟩, rfl, (primeBody_iff _ p).mpr hp⟩, by omega, by omega⟩

def lit (k : Int) : Term := .num k
set_option hygiene false in
/-- The meaning of a closed statement over definitions `D`, unfolded. -/
macro "means" : tactic => `(tactic| (simp (config := { decide := true }) [Defs.Means, Defs.env, Holds,
  Term.value, Term.values, lit] <;> omega))

example : Defs.Means [] (.eq (.add (lit 2) (lit 3)) (.sub (.mul (lit 2) (lit 4)) (lit 3))) ∧ ¬ Defs.Means [] (.eq (lit 2) (lit 3)) := by means
example : Defs.Means [] (.lt (lit 2) (lit 3)) ∧ ¬ Defs.Means [] (.lt (lit 3) (lit 3)) := by means
example : Defs.Means [] (.le (lit 3) (lit 3)) ∧ ¬ Defs.Means [] (.le (lit 4) (lit 3)) := by means
example : Defs.Means [] (.dvd (lit 3) (lit 6)) ∧ ¬ Defs.Means [] (.dvd (lit 4) (lit 6)) := by means
example : Defs.Means [] (.or (.eq (lit 1) (lit 2)) (.eq (lit 2) (lit 2))) ∧ ¬ Defs.Means [] (.or (.eq (lit 1) (lit 2)) (.eq (lit 2) (lit 3))) := by means
example : Defs.Means [] (.imp (.eq (lit 1) (lit 2)) (.eq (lit 2) (lit 3))) ∧ ¬ Defs.Means [] (.imp (.eq (lit 1) (lit 1)) (.eq (lit 2) (lit 3))) := by means
example : Defs.Means [] (.allInt (.or (.lt (.var 0) (lit 1)) (.le (lit 1) (.var 0)))) ∧ ¬ Defs.Means [] (.allInt (.le (lit 0) (.var 0))) := by
  simp [Defs.Means, Holds, Term.value, lit]; exact ⟨fun n => by omega, -1, by omega⟩
example : Defs.Means [] (.exInt (.eq (.add (.var 0) (lit 3)) (lit 0))) := by
  simp [Defs.Means, Holds, Term.value, lit]; exact ⟨-3, by omega⟩
example : Defs.Means [] (.allFromTo (lit 1) (lit 3) (.lt (.var 0) (lit 4))) := by
  simp [Defs.Means, Holds, Term.value, lit]; exact fun i _ _ => by omega
example : Defs.Means [] (.allFromTo (lit 1) (lit 3) (.lt (lit 0) (.var 0))) ∧ ¬ Defs.Means [] (.allFromTo (lit 0) (lit 3) (.lt (lit 0) (.var 0))) ∧
    ¬ Defs.Means [] (.allFromTo (lit 1) (lit 3) (.lt (.var 0) (lit 3))) := by
  simp [Defs.Means, Holds, Term.value, lit]; exact ⟨fun i _ _ => by omega, ⟨0, by omega⟩, ⟨3, by omega⟩⟩
example : Defs.Means [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 3))) ∧ ¬ Defs.Means [] (.exFromTo (lit 1) (lit 3) (.eq (.var 0) (lit 0))) := by
  means
example : Defs.Means [] (.eq (.countFromTo (lit 2) (lit 5) (.dvd (lit 2) (.var 0))) (lit 2)) ∧
    Defs.Means [] (.eq (.countFromTo (lit 2) (lit 6) (.dvd (lit 2) (.var 0))) (lit 3)) := by
  simp (config := { decide := true }) [Defs.Means, Holds, Term.value, lit, List.range, List.range.loop]
example : Holds (Defs.env []) [5, 7] (.eq (.var 1) (lit 7)) := by means
def double : Defs := [.fn "double" 1 (.mul (lit 2) (.var 0)), .fn "quad" 1 (.call "double" [.call "double" [.var 0]]),
  .fn "seven" 1 (lit 7), .pred "below" 2 (.lt (.var 0) (.var 1))]
example : double.Means (.eq (.call "quad" [lit 3]) (lit 12)) ∧ double.Means (.eq (.call "double" [lit 4]) (lit 8)) ∧
    ¬ double.Means (.eq (.call "double" [lit 4, lit 1]) (lit 8)) ∧ ¬ double.Means (.eq (.call "seven" []) (lit 7)) ∧
    ¬ double.Means (.eq (.call "triple" [lit 1]) (lit 3)) ∧ double.Means (.call "below" [lit 1, lit 2]) ∧
    ¬ double.Means (.call "below" [lit 2, lit 1]) := by
  simp (config := { decide := true }) [double, Defs.Means, Defs.env, Holds, Term.value, Term.values, lit]
  exact ⟨2, _, ⟨rfl, rfl⟩, rfl, 1, rfl, 2, rfl, by omega⟩
example : Defs.Means [] (.eq (.countFromTo (lit 3) (lit 1) (.eq (lit 0) (lit 0))) (lit 0)) := by means

/-- M-1 through `hi`: for every n from 1 through hi there is a prime p from n + 1 through 2n. -/
def m1 (hi : Int) : Formula :=
  .allFromTo (.num 1) (.num hi) (.exFromTo (.add (.var 0) (.num 1)) (.mul (.num 2) (.var 0)) (.call "prime" [.var 0]))

/-- M-5: the strict n < p < 2n from 1 through 161. -/
def m5 : Formula :=
  .allFromTo (.num 1) (.num 161)
    (.exFromTo (.add (.var 0) (.num 1)) (.sub (.mul (.num 2) (.var 0)) (.num 1)) (.call "prime" [.var 0]))

/-- M-5 fails in the meaning, and n = 1 decides it: there the range n + 1 … 2n − 1 is 2 … 1, which is empty. -/
example : ¬ primeDefs.Means m5 := by
  simp [Defs.Means, m5, Holds, Term.value]
  exact ⟨1, by omega, by omega, fun p h1 h2 => by omega⟩

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

/-! Boundedness: M-3 is stated, not decided; the others are bounded, through the definitions they call. -/
#guard !bertrand.Bounded primeDefs && (m1 161).Bounded primeDefs && (m4 2 11 248).Bounded countDefs
#guard !(m4 2 11 248).Bounded
  (primeDefs ++ [.fn "prime_count" 1 (.countFromTo (.num 1) (.var 0) (.exNat (.eq (.var 0) (.var 1))))] ++ countDefs.drop 2)
#guard !(Formula.call "prime" [.num 7]).Bounded [.pred "prime" 1 (.allInt (.eq (.var 0) (.var 0)))]

/-! Admission: the fixtures are admitted; each refusal the core decides, and the decoder's order between them. -/
#guard caseRefusal countDefs [m1 161, m5, m2, bertrand, m4 2 11 248] = none
#guard countDefs.WellFormed && (m1 161).Scoped countDefs 0 && (Formula.lt (.var 1) (.var 0)).Scoped primeDefs 2
#guard !(Formula.lt (.var 2) (.var 0)).Scoped primeDefs 2 && !(Formula.call "nope" []).Scoped primeDefs 0 &&
  !(Formula.call "prime" []).Scoped primeDefs 0 && !Defs.WellFormed [.pred "loop" 1 (.call "loop" [.var 0])]
#guard caseRefusal [.pred "p" 1 (.lt (.var 0) (.var 1))] [] = some (.unscopedVariable 1)
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
