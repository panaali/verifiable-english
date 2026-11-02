import VE.Senses.Read
import VE.Route.Budget

/-! Flip models (senses plan 2.6 step 7; spec 2.6, "Flip models"). For two candidates of one open unit: the
valuation that makes true exactly the senses the first chooses and the second does not, every other predicate
false for all arguments; if the two formulas differ in truth under it, it distinguishes the pair; else the same
with the two exchanged; else the pair is undistinguished. The model has one entity per sort and one per constant
the two formulas name, and is evaluated by the budgeted evaluator (`VE.Route.Budget.evalF`, sound for
`VE.Formula.eval` by `evalF_sound`) under one budget, `maxEvaluations`, charged across the whole answer. A formula
the evaluator has no case for, or an exhausted budget, gives `unknown`, never a distinction. -/

namespace VE.Senses
open VE.EnglishGrammar

/-- The core term the evaluator reads: a variable or a constant. -/
def termCore : ETerm → Option VE.Term
  | .var i => some (.var i)
  | .const c => some (.const c)
  | _ => none

/-- The core formula the evaluator reads, or none for a form it has no case for (numbers, comparisons, reach, an
atom of three or more arguments). -/
def formulaCore : EFormula → Option VE.Formula
  | .top => some .top
  | .bottom => some .bottom
  | .pred p [t] => return .unary p (← termCore t)
  | .pred p [t, u] => return .binary p (← termCore t) (← termCore u)
  | .eq t u => return .eq (← termCore t) (← termCore u)
  | .not a => return .not (← formulaCore a)
  | .and a b => return .and (← formulaCore a) (← formulaCore b)
  | .or a b => return .or (← formulaCore a) (← formulaCore b)
  | .implies a b => return .implies (← formulaCore a) (← formulaCore b)
  | .all s a => return .all s (← formulaCore a)
  | .ex s a => return .ex s (← formulaCore a)
  | _ => none

/-- The senses `c` chooses and `d` does not, as the projection's predicate ids, in the projection's order. -/
def flipOn (P : Projection) (c d : Candidate) : List String :=
  (P.map.filter fun (_, s, _) => c.choice.contains (s.word, s.index) && !d.choice.contains (s.word, s.index)).map (·.1)

/-- The model over the formulas `fs`: each sort has one entity of its own (`#` and the sort's name; no
identifier has a `#`) and the constants of that sort that `fs` name, each its own entity. -/
def flipModelOf (P : Projection) (fs : List EFormula) : VE.FiniteModel String :=
  let consts := (fs.flatMap EFormula.consts).eraseDups
  let sortOf (c : String) : String := ((P.env.constants.find? (·.name == c)).map (·.sort)).getD ""
  { domains := fun s => ("#" ++ s) :: consts.filter (sortOf · == s)
    constants := fun c => if consts.contains c then some c else none
    relations := fun _ => [] }

/-- The flip model of a pair: the senses made true and the two formulas' values, or no distinction, or unknown. -/
inductive Flip where
  | distinguished (on : List String) (first second : Bool)
  | undistinguished
  | unknown
  deriving DecidableEq, Repr

/-- The flip model of candidates `c` and `d` from work `w`, and the work after it; an exhausted budget leaves
none for the pairs after it. -/
def flipPair (P : Projection) (c d : Candidate) (w : Nat) : Flip × Nat :=
  match formulaCore c.formula, formulaCore d.formula with
  | some fc, some fd =>
    let M := flipModelOf P [c.formula, d.formula]
    let values (on : List String) (w : Nat) : Option ((Bool × Bool) × Nat) := do
      let (a, w) ← VE.Route.Budget.evalF (fun p _ => on.contains p) M VE.Limits.maxEvaluations [] fc w
      let (b, w) ← VE.Route.Budget.evalF (fun p _ => on.contains p) M VE.Limits.maxEvaluations [] fd w
      pure ((a, b), w)
    match values (flipOn P c d) w with
    | none => (.unknown, VE.Limits.maxEvaluations)
    | some ((a, b), w) =>
      if a != b then (.distinguished (flipOn P c d) a b, w) else
      match values (flipOn P d c) w with
      | none => (.unknown, VE.Limits.maxEvaluations)
      | some ((a, b), w) => if a != b then (.distinguished (flipOn P d c) a b, w) else (.undistinguished, w)
  | _, _ => (.unknown, w)

/-- The pairs `(i, j)`, `i < j < n`, in order. -/
def candidatePairs (n : Nat) : List (Nat × Nat) :=
  (List.range n).flatMap fun i => (List.range (n - i - 1)).map fun k => (i, i + k + 1)

/-- Every unit's flip models (`flipModel`, plan 4.2): for unit `k` and its candidates `i < j`, `(k, i, j)` and the
pair's flip model, in unit order, then pair order, under one budget. -/
def flipsOf (P : Projection) (units : List SenseUnit) : List ((Nat × Nat × Nat) × Flip) :=
  let pairs := (units.mapIdx fun k u => (candidatePairs u.candidates.length).filterMap fun (i, j) => do
    pure ((k, i, j), ← u.candidates[i]?, ← u.candidates[j]?)).flatten
  (pairs.foldl (fun (acc, w) (key, c, d) => let (f, w) := flipPair P c d w; (acc ++ [(key, f)], w)) ([], 0)).1

end VE.Senses
