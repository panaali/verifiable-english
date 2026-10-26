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

/-! Each clause under an outer value (review F1): the values are `[5]` and every child of the clause reads them, so a
clause that loses them (a child read in `[]`, a binder's `[i]` for `i :: ρ` or `ρ ++ [i]`) leaves a variable without
a value. -/
example : let H := Holds (Defs.env []) [5]
    H (.eq (.add (.var 0) (.var 0)) (lit 10)) ∧ H (.eq (.sub (.var 0) (.var 0)) (lit 0)) ∧
    H (.eq (.mul (.var 0) (.var 0)) (lit 25)) ∧ H (.eq (.var 0) (.var 0)) ∧ H (.lt (.var 0) (.add (.var 0) (lit 1))) ∧
    H (.le (.var 0) (.var 0)) ∧ H (.dvd (.var 0) (.var 0)) ∧ ¬ H (.not (.eq (.var 0) (lit 5))) ∧
    H (.and (.eq (.var 0) (lit 5)) (.eq (.var 0) (lit 5))) ∧ H (.or (.eq (.var 0) (lit 5)) (.eq (lit 0) (lit 1))) ∧
    H (.or (.eq (lit 0) (lit 1)) (.eq (.var 0) (lit 5))) ∧ ¬ H (.imp (.eq (.var 0) (lit 5)) (.eq (lit 0) (lit 1))) ∧
    H (.imp (.eq (lit 0) (lit 0)) (.eq (.var 0) (lit 5))) := by
  simp [Holds, Term.value, lit]
example : let H := Holds (Defs.env []) [5]
    H (.allNat (.eq (.var 1) (lit 5))) ∧ H (.exNat (.and (.eq (.var 0) (lit 6)) (.eq (.var 1) (lit 5)))) ∧
    H (.allInt (.eq (.var 1) (lit 5))) ∧ H (.exInt (.and (.eq (.var 0) (lit 6)) (.eq (.var 1) (lit 5)))) ∧
    H (.allFromTo (.add (.var 0) (lit 1)) (.add (.var 0) (lit 1)) (.and (.eq (.var 0) (lit 6)) (.eq (.var 1) (lit 5)))) ∧
    H (.exFromTo (.add (.var 0) (lit 1)) (.add (.var 0) (lit 1)) (.and (.eq (.var 0) (lit 6)) (.eq (.var 1) (lit 5)))) ∧
    ¬ H (.allFromTo (.var 0) (.add (.var 0) (lit 1)) (.eq (.var 0) (.var 1))) ∧
    H (.allNat (.exInt (.eq (.var 0) (.add (.var 1) (.var 2))))) := by
  simp [Holds, Term.value, lit]; exact ⟨⟨6, rfl⟩, fun i _ _ => by omega, ⟨6, by omega⟩⟩
/-- The count from 5 through 9 of the values at most one more than the outer 5 is 2; with the outer value lost, 0. -/
example : Holds (Defs.env []) [5] (.eq (.countFromTo (.var 0) (.add (.var 0) (lit 4))
    (.and (.le (.var 0) (.add (.var 1) (lit 1))) (.eq (.var 1) (lit 5)))) (lit 2)) := by
  simp (config := { decide := true }) [Holds, Term.value, lit, List.range, List.range.loop]
example : Holds double.env [5] (.and (.eq (.call "double" [.var 0]) (lit 10)) (.call "below" [.var 0, .add (.var 0) (lit 1)])) := by
  simp (config := { decide := true }) [double, Defs.env, Holds, Term.value, Term.values, lit]
  exact ⟨2, _, ⟨rfl, rfl⟩, rfl, 5, rfl, 6, rfl, by omega⟩

/-- Each kind of definition read past a later definition of each kind (review F1): a definition that drops or clears
the names before it, or reads its body without them, leaves a call without a meaning; `minus` reads its arguments in
order. -/
def chain : Defs := [.fn "one" 0 (lit 1), .pred "pos" 1 (.lt (lit 0) (.var 0)),
  .fn "succ" 1 (.add (.var 0) (.call "one" [])), .pred "big" 1 (.and (.call "pos" [.var 0]) (.lt (.call "one" []) (.var 0))),
  .fn "minus" 2 (.sub (.var 0) (.var 1))]
example : chain.Means (.and (.eq (.call "one" []) (lit 1)) (.and (.call "pos" [lit 3])
      (.and (.eq (.call "succ" [lit 3]) (lit 4)) (.and (.call "big" [lit 3]) (.eq (.call "minus" [lit 5, lit 3]) (lit 2)))))) ∧
    ¬ chain.Means (.call "big" [lit 1]) ∧ ¬ chain.Means (.call "pos" [lit 0]) := by
  simp (config := { decide := true }) [chain, Defs.Means, Defs.env, Holds, Term.value, Term.values, lit,
    exists_and_left, exists_eq_left', and_assoc]

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

/-! Admission at every position (review F2): each planted term or formula, at each child position of each constructor
under up to two more constructors, in a statement, a predicate's body and a function's body, is refused as itself, and
a sound one is admitted. -/
namespace Positions

def ok : Formula := .eq (.num 0) (.num 0)
def z : Term := .num 0

/-- One constructor around a child: the binders it adds, whether the child is a count's condition, whether it is an
unbounded quantifier, and the constructor with the child filled. -/
structure Step (α β : Type) where
  binders : Nat := 0
  count : Bool := false
  quant : Bool := false
  fill : α → β

/-- A place in a statement: its binders, whether it lies in a count's condition or under an unbounded quantifier, and
whether such a quantifier lies in a count's condition around it (then the statement is `UnboundedCount` whatever
fills it). -/
structure Place (α : Type) where
  binders : Nat := 0
  count : Bool := false
  quant : Bool := false
  refused : Bool := false
  fill : α → Formula

def Place.down (p : Place β) (s : Step α β) : Place α :=
  ⟨p.binders + s.binders, p.count || s.count, p.quant || s.quant, p.refused || p.count && s.quant, p.fill ∘ s.fill⟩

/-- Every formula child of a formula. -/
def ff : List (Step Formula Formula) :=
  [{ fill := .not }, { fill := (.and · ok) }, { fill := .and ok }, { fill := (.or · ok) }, { fill := .or ok },
   { fill := (.imp · ok) }, { fill := .imp ok }, { binders := 1, quant := true, fill := .allNat },
   { binders := 1, quant := true, fill := .exNat }, { binders := 1, quant := true, fill := .allInt },
   { binders := 1, quant := true, fill := .exInt }, { binders := 1, fill := .allFromTo z z },
   { binders := 1, fill := .exFromTo z z }, { binders := 1, count := true, fill := fun φ => .le z (.countFromTo z z φ) }]

/-- Every term child of a formula. -/
def tf : List (Step Term Formula) :=
  [{ fill := (.eq · z) }, { fill := .eq z }, { fill := (.lt · z) }, { fill := .lt z }, { fill := (.le · z) },
   { fill := .le z }, { fill := (.dvd · z) }, { fill := .dvd z }, { fill := fun t => .call "p2" [t, z] },
   { fill := fun t => .call "p2" [z, t] }, { fill := (.allFromTo · z ok) }, { fill := (.allFromTo z · ok) },
   { fill := (.exFromTo · z ok) }, { fill := (.exFromTo z · ok) }]

/-- Every term child of a term, and a term in a count's condition. -/
def tt : List (Step Term Term) :=
  [{ fill := (.add · z) }, { fill := .add z }, { fill := (.sub · z) }, { fill := .sub z }, { fill := (.mul · z) },
   { fill := .mul z }, { fill := fun t => .call "f2" [t, z] }, { fill := fun t => .call "f2" [z, t] },
   { fill := (.countFromTo · z ok) }, { fill := (.countFromTo z · ok) },
   { binders := 1, count := true, fill := fun t => .countFromTo z z (.eq t z) }]

def formulaPlaces : List (Place Formula) :=
  let one := ff.map (Place.down { fill := id })
  { fill := id } :: one ++ one.flatMap fun p => ff.map p.down

def termPlaces : List (Place Term) :=
  formulaPlaces.flatMap (fun p => tf.map p.down) ++
    ((({ fill := id } : Place Formula) :: ff.map (Place.down { fill := id })).flatMap fun p =>
      tf.flatMap fun s => tt.map (p.down s).down)

/-- The definitions every case has: the names the planted calls read, and two definitions after the host. -/
def vocab : Defs := [.fn "f0" 0 z, .fn "f2" 2 (.add (.var 0) (.var 1)), .pred "p0" 0 ok,
  .pred "p2" 2 (.lt (.var 0) (.var 1)), .pred "unb" 0 (.allInt ok)]
def later : Defs := [.pred "later" 0 ok, .fn "laterf" 0 z]

/-- Where the statement goes: its parameters, the binders and count around it, and the case it makes. -/
structure Host where
  arity : Nat
  binders : Nat
  count : Bool
  pred : Option Bool
  case : Formula → Defs × List Formula

def hosts : List Host :=
  [⟨0, 0, false, none, fun φ => (vocab ++ later, [φ])⟩,
   ⟨1, 0, false, some true, fun φ => (vocab ++ .pred "host" 1 φ :: later, [])⟩,
   ⟨2, 1, true, some false, fun φ => (vocab ++ .fn "host" 2 (.countFromTo (.var 0) (.var 1) φ) :: later, [])⟩]

/-- A call of `later` or of the host itself: recursive in a body, and in a statement admitted or unknown. -/
def Host.calls (h : Host) (f : String) (pred : Bool) : Option Refusal :=
  if f = "host" then (if h.pred = some pred then some (.recursiveDefinition f) else some (.unknownDefinition f))
  else if h.pred.isSome then some (.recursiveDefinition f) else none

/-- The planted terms `d` values deep, each with its refusal (`none`: admitted). -/
def terms (h : Host) (d : Nat) : List (Term × Option Refusal) :=
  [(.var d, some (.unscopedVariable h.arity)), (.var (d + 2), some (.unscopedVariable (h.arity + 2))),
   (.call "nope" [], some (.unknownDefinition "nope")), (.call "p2" [z, z], some (.unknownDefinition "p2")),
   (.call "f2" [z], some (.arityMismatch "f2" 2)), (.call "f0" [z], some (.arityMismatch "f0" 0)),
   (.call "laterf" [], h.calls "laterf" false), (.call "host" [z, z], h.calls "host" false),
   (.countFromTo z z (.allInt ok), some .unboundedCount), (.countFromTo z z (.call "unb" []), some .unboundedCount),
   (.countFromTo (.var d) z ok, some (.unscopedVariable h.arity)), (.call "f2" [z, .call "f0" []], none)] ++
  if d = 0 then [] else [(.var 0, none), (.var (d - 1), none), (.countFromTo (.var (d - 1)) (.var 0) ok, none)]

/-- The planted formulas, each with its refusal; `count`: the place is in a count's condition. -/
def formulas (h : Host) (count : Bool) : List (Formula × Option Refusal) :=
  [(.call "nope" [z], some (.unknownDefinition "nope")), (.call "f2" [z, z], some (.unknownDefinition "f2")),
   (.call "p2" [z], some (.arityMismatch "p2" 2)), (.call "p0" [z], some (.arityMismatch "p0" 0)),
   (.call "later" [], h.calls "later" true), (.call "host" [z], h.calls "host" true),
   (.call "p2" [z, z], none), (.call "p0" [], none),
   (.call "unb" [], if count then some .unboundedCount else none),
   (.allInt ok, if count then some .unboundedCount else none)]

/-- Each planted case is refused as its table says, or `UnboundedCount` when only its place refuses it. -/
def refusedAs (h : Host) (p : Place α) (x : α) (r : Option Refusal) : Bool :=
  let (D, φs) := h.case (p.fill x)
  caseRefusal D φs = (r <|> if p.refused || h.count && p.quant then some .unboundedCount else none)

#guard hosts.all fun h => formulaPlaces.all fun p =>
  (formulas h (p.count || h.count)).all fun (φ, r) => refusedAs h p φ r
#guard hosts.all fun h => termPlaces.all fun p =>
  (terms h (p.binders + h.binders + h.arity)).all fun (t, r) => refusedAs h p t r

/-! Boundedness at every position: a statement is bounded exactly when no unbounded quantifier, and no call of a
definition that is unbounded itself or through an earlier one, lies anywhere in it. -/
def unbounded : Defs := vocab ++ [.fn "unbf" 0 (.countFromTo z z (.exNat ok)), .pred "unb2" 0 (.and ok (.call "unb" []))]
#guard formulaPlaces.all fun p => [(ok, true), (.call "p2" [z, z], true), (.allInt ok, false), (.exNat ok, false),
    (.call "unb" [], false), (.call "unb2" [], false)].all fun (φ, b) => (p.fill φ).Bounded unbounded == (b && !p.quant)
#guard termPlaces.all fun p => [(z, true), (.call "f2" [z, .call "f0" []], true), (.countFromTo z z (.allNat ok), false),
    (.countFromTo z z (.call "unb" []), false), (.call "unbf" [], false), (.call "f2" [z, .call "unbf" []], false)].all
  fun (t, b) => (p.fill t).Bounded unbounded == (b && !p.quant)

/-- One fault of each refusal, in the decoder's order: in statements where it can be, and in definitions' bodies. -/
def oneEach : List (List (Defs × List Formula × Refusal)) :=
  [[([.pred "d" 0 ok, .fn "d" 0 z], [], .duplicateName "d"), ([], [.lt (.var 0) z], .unscopedVariable 0),
    ([], [.call "nope" []], .unknownDefinition "nope"), ([.pred "r" 0 (.call "r" [])], [], .recursiveDefinition "r"),
    ([.pred "a" 1 ok], [.call "a" []], .arityMismatch "a" 1), ([], [.le z (.countFromTo z z (.allInt ok))], .unboundedCount)],
   [([.pred "d" 0 ok, .fn "d" 0 z], [], .duplicateName "d"), ([.pred "s" 1 (.lt (.var 1) z)], [], .unscopedVariable 1),
    ([.pred "u" 0 (.call "nope" [])], [], .unknownDefinition "nope"), ([.pred "r" 0 (.call "r" [])], [], .recursiveDefinition "r"),
    ([.pred "a" 1 ok, .pred "c" 0 (.call "a" [])], [], .arityMismatch "a" 1),
    ([.fn "n" 0 (.countFromTo z z (.allInt ok))], [], .unboundedCount)]]

/-! Each alone is refused as itself; any two, in either order, as the one earlier in the decoder's order; and
`firstRefusal` keeps the earlier in that order of any two, whichever comes first. -/
#guard oneEach.all fun fs => fs.zipIdx.all fun ((D, φs, r), i) => caseRefusal D φs = some r &&
  fs.zipIdx.all fun ((D', φs', r'), j) => i == j || caseRefusal (D' ++ D) (φs' ++ φs) = some (if i < j then r else r')
#guard (oneEach.head!.map (·.2.2)).zipIdx.all fun (r, i) => (oneEach.head!.map (·.2.2)).zipIdx.all fun (r', j) =>
  firstRefusal [r', r] = some (if i < j then r else r') && firstRefusal [r, r'] = some (if j < i then r' else r)
/-! `Formula.Scoped` reads the definition of the call's kind, whatever shares its name. -/
#guard (Formula.call "x" [z]).Scoped [.fn "x" 0 z, .pred "x" 1 ok] 0 && (Term.call "x" [] |> (Formula.eq · z)).Scoped
  [.pred "x" 1 ok, .fn "x" 0 z] 0 && !(Formula.call "x" []).Scoped [.fn "x" 0 z, .pred "x" 1 ok] 0
/-! Two of one kind: the first in order; a name used twice across kinds, and past another definition. -/
#guard caseRefusal [] [.call "x" [], .call "y" []] = some (.unknownDefinition "x") &&
  caseRefusal [.fn "x" 0 z, .pred "x" 0 ok] [] = some (.duplicateName "x") &&
  caseRefusal [.pred "x" 0 ok, .fn "y" 0 z, .pred "x" 0 ok] [] = some (.duplicateName "x") &&
  caseRefusal [.fn "x" 0 z, .fn "x" 0 z] [] = some (.duplicateName "x")

/-! Two of one kind in one statement or body: the one earlier in the request's order, at every place and host (a
call's name before its arguments, each child before the next, a binder's lo before its hi before its body), with the
two names either way round; and each definition before the next, the definitions before the statements. -/
def formulaPairs : List (String → String → Formula) :=
  let c (a : String) : Formula := .call a []
  let t (a : String) : Term := .call a []
  [fun a b => .and (c a) (c b), fun a b => .or (c a) (c b), fun a b => .imp (c a) (c b),
   fun a b => .eq (t a) (t b), fun a b => .lt (t a) (t b), fun a b => .le (t a) (t b), fun a b => .dvd (t a) (t b),
   fun a b => .call a [t b], fun a b => .call "p2" [t a, t b], fun a b => .allFromTo (t a) (t b) ok,
   fun a b => .exFromTo (t a) (t b) ok, fun a b => .allFromTo (t a) z (c b), fun a b => .exFromTo z (t a) (c b)]
def termPairs : List (String → String → Term) :=
  let c (a : String) : Formula := .call a []
  let t (a : String) : Term := .call a []
  [fun a b => .add (t a) (t b), fun a b => .sub (t a) (t b), fun a b => .mul (t a) (t b), fun a b => .call a [t b],
   fun a b => .call "f2" [t a, t b], fun a b => .countFromTo (t a) (t b) ok, fun a b => .countFromTo (t a) z (c b),
   fun a b => .countFromTo z (t a) (c b)]

#guard hosts.all fun h => formulaPlaces.all fun p => formulaPairs.all fun mk =>
  refusedAs h p (mk "x" "y") (some (.unknownDefinition "x")) && refusedAs h p (mk "y" "x") (some (.unknownDefinition "y"))
#guard hosts.all fun h => (({ fill := id } : Place Formula) :: ff.map (Place.down { fill := id })).all fun p =>
  tf.all fun s => termPairs.all fun mk => refusedAs h (p.down s) (mk "x" "y") (some (.unknownDefinition "x")) &&
    refusedAs h (p.down s) (mk "y" "x") (some (.unknownDefinition "y"))
#guard [("x", "y"), ("y", "x")].all fun (a, b) =>
  caseRefusal [.pred "d" 0 (.call a []), .fn "e" 0 (.call b [])] [] = some (.unknownDefinition a) &&
  caseRefusal [.pred "d" 0 (.call a [])] [.call b []] = some (.unknownDefinition a) &&
  caseRefusal [.pred "d" 0 (.lt (.var 1) z)] [.lt (.var 2) z] = some (.unscopedVariable 1) &&
  caseRefusal [] [.call a [], .call b []] = some (.unknownDefinition a)

end Positions

end VE.Arith.Examples
